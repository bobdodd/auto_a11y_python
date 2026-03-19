"""
Authentication routes for user login, logout, and registration
"""

import hashlib
import logging
import secrets

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, g, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from functools import wraps
from itsdangerous import URLSafeSerializer, BadSignature
from werkzeug.security import generate_password_hash

from auto_a11y.models import AppUser, UserRole
from auto_a11y.core.permissions import permission_required

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


def role_required(*roles):
    """Legacy decorator -- now checks is_superadmin for admin, otherwise passes."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(_('Please log in to access this page.'), 'warning')
                return redirect(url_for('auth.login', next=request.url))
            if getattr(current_user, 'is_superadmin', False):
                return f(*args, **kwargs)
            flash(_('You do not have permission to access this page.'), 'danger')
            return redirect(url_for('index'))
        return decorated_function
    return decorator


def admin_required(f):
    """Legacy decorator -- requires superadmin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_('Please log in to access this page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if not getattr(current_user, 'is_superadmin', False):
            flash(_('Administrator access required.'), 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def auditor_required(f):
    """Legacy decorator -- requires superadmin or projects:create permission."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_('Please log in to access this page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if getattr(current_user, 'is_superadmin', False):
            return f(*args, **kwargs)
        # For non-superadmins, check if they have projects:create (auditor-level)
        from auto_a11y.core.permissions import user_has_global_permission
        if user_has_global_permission(current_user, 'projects', 'create'):
            return f(*args, **kwargs)
        flash(_('Auditor access required.'), 'danger')
        return redirect(url_for('index'))
    return decorated_function


# ------------------------------------------------------------------
# Per-project/website permission helpers
# ------------------------------------------------------------------

def _get_db():
    """Get database instance from current app."""
    return current_app.db


def get_effective_role(user, request_obj=None, project_id=None, website_id=None, page_id=None):
    """Legacy function -- returns UserRole for backward compat.
    Used by templates to determine is_project_admin etc.
    """
    if getattr(user, 'is_superadmin', False):
        return UserRole.ADMIN

    from auto_a11y.core.permissions import user_has_permission
    db = _get_db()

    # Resolve page to website
    if page_id and not website_id:
        page = db.get_page(page_id)
        if not page:
            return None
        website_id = page.website_id

    if website_id and not project_id:
        website = db.get_website(website_id)
        if not website:
            return None
        project_id = website.project_id

    if not project_id:
        return None

    # Map permission levels to legacy roles
    if user_has_permission(user, project_id, 'project_members', 'delete'):
        return UserRole.ADMIN
    if user_has_permission(user, project_id, 'test_results', 'create'):
        return UserRole.AUDITOR
    if user_has_permission(user, project_id, 'projects', 'read'):
        return UserRole.CLIENT
    return None


def project_role_required(*roles):
    """Legacy decorator -- checks group permissions instead of roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if getattr(current_user, 'is_superadmin', False):
                g.effective_role = UserRole.ADMIN
                return f(*args, **kwargs)

            project_id = kwargs.get('project_id')
            website_id = kwargs.get('website_id')
            page_id = kwargs.get('page_id')

            effective_role = get_effective_role(
                current_user, request, project_id, website_id, page_id
            )

            if effective_role not in roles:
                if request.is_json:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                flash('You do not have permission to access this resource.', 'danger')
                abort(403)

            g.effective_role = effective_role
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def project_admin_required(f):
    """Legacy decorator -- checks project_members:delete permission."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        if getattr(current_user, 'is_superadmin', False):
            return f(*args, **kwargs)

        from auto_a11y.core.permissions import user_has_permission, _resolve_project_id
        project_id = _resolve_project_id(**kwargs)

        if project_id and user_has_permission(current_user, project_id, 'project_members', 'delete'):
            return f(*args, **kwargs)

        if request.is_json:
            return jsonify({'error': 'Project admin access required'}), 403
        flash('Project administrator access required.', 'danger')
        abort(403)
    return decorated_function


# ------------------------------------------------------------------
# Token validation helpers
# ------------------------------------------------------------------

def validate_token(token_string):
    """
    Validate a share-link token.
    Uses URLSafeSerializer (not TimedSerializer -- expiry is checked via
    the DB ``expires_at`` field).
    Returns ``{scope, scope_id}`` on success or ``None``.
    """
    serializer = URLSafeSerializer(
        current_app.config['SECRET_KEY'],
        salt=current_app.app_config.TOKEN_SALT,
    )
    try:
        payload = serializer.loads(token_string)
    except BadSignature:
        return None

    token_hash = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
    token = current_app.db.get_share_token_by_hash(token_hash)
    if token is None or not token.is_valid:
        return None

    current_app.db.record_token_use(token_hash)
    return {'scope': token.scope, 'scope_id': token.scope_id}


def require_access(f):
    """
    Decorator that gates access to public routes.
    Checks for a ``token`` URL parameter first, then falls back to
    ``current_user.is_authenticated``.
    Sets ``g.access_scope`` and ``g.access_scope_id`` for downstream scope enforcement.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token_string = kwargs.get('token')

        if token_string:
            result = validate_token(token_string)
            if result is None:
                abort(403)
            g.access_scope = result['scope']
            g.access_scope_id = result['scope_id']
            return f(*args, **kwargs)

        if current_user.is_authenticated:
            g.access_scope = None
            g.access_scope_id = None
            return f(*args, **kwargs)

        return redirect(url_for('auth.login'))

    return decorated


def check_scope(scope_type, scope_id):
    """
    Verify the current token/login grants access to the requested resource.
    Aborts with 403 if access is denied.
    """
    from auto_a11y.models import TokenScope

    # Logged-in user (no token) -- allow all for MVP
    if g.access_scope is None:
        return

    if g.access_scope == TokenScope.PROJECT:
        if scope_type == 'project' and scope_id == g.access_scope_id:
            return
        if scope_type in ('website', 'page'):
            if scope_type == 'website':
                website = current_app.db.get_website(scope_id)
                if website and website.project_id == g.access_scope_id:
                    return
            elif scope_type == 'page':
                page = current_app.db.get_page(scope_id)
                if page:
                    website = current_app.db.get_website(page.website_id)
                    if website and website.project_id == g.access_scope_id:
                        return

    elif g.access_scope == TokenScope.WEBSITE:
        if scope_type == 'website' and scope_id == g.access_scope_id:
            return
        if scope_type == 'page':
            page = current_app.db.get_page(scope_id)
            if page and page.website_id == g.access_scope_id:
                return

    abort(403)


# ------------------------------------------------------------------
# Microsoft SSO helpers
# ------------------------------------------------------------------

def get_msal_app():
    """Create a ConfidentialClientApplication for Microsoft SSO."""
    import msal
    config = current_app.app_config
    return msal.ConfidentialClientApplication(
        config.MICROSOFT_CLIENT_ID,
        authority=config.MICROSOFT_AUTHORITY,
        client_credential=config.MICROSOFT_CLIENT_SECRET,
    )


def get_microsoft_auth_url(redirect_uri):
    """Build the Microsoft authorization URL and store state in session."""
    msal_app = get_msal_app()
    flow = msal_app.initiate_auth_code_flow(
        scopes=current_app.app_config.MICROSOFT_SCOPE,
        redirect_uri=redirect_uri,
    )
    session['msal_flow'] = flow
    return flow['auth_uri']


def complete_microsoft_auth(auth_request, redirect_uri):
    """
    Exchange the Microsoft authorization code for tokens.
    Returns a dict of user claims on success, or None on failure.
    """
    flow = session.pop('msal_flow', None)
    if flow is None:
        return None

    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_auth_code_flow(
        flow,
        auth_request.args,
    )

    if 'error' in result:
        logger.warning('Microsoft SSO token error: %s - %s',
                        result.get('error'), result.get('error_description'))
        return None

    claims = result.get('id_token_claims', {})
    email = claims.get('preferred_username') or claims.get('email')
    if not email:
        logger.warning('Microsoft SSO: no email in id_token_claims')
        return None

    return {
        'email': email.lower(),
        'name': claims.get('name', ''),
        'provider': 'microsoft',
        'provider_id': claims.get('oid', ''),
    }


# ------------------------------------------------------------------
# Google SSO helpers
# ------------------------------------------------------------------

def _google_flow(redirect_uri):
    """Create a Google OAuth2 flow."""
    import os
    from google_auth_oauthlib.flow import Flow
    config = current_app.app_config
    # Allow http:// redirect URIs in local development (debug mode only)
    if current_app.debug:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    # Google returns fully-qualified scope URLs that differ from the
    # shorthand names we request; accept the changed scopes.
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    return Flow.from_client_config(
        {
            'web': {
                'client_id': config.GOOGLE_CLIENT_ID,
                'client_secret': config.GOOGLE_CLIENT_SECRET,
                'auth_uri': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
            }
        },
        scopes=['openid', 'email', 'profile'],
        redirect_uri=redirect_uri,
    )


def get_google_auth_url(redirect_uri):
    """Build the Google authorization URL and store state in session."""
    flow = _google_flow(redirect_uri)
    auth_url, state = flow.authorization_url(prompt='select_account')
    session['google_oauth_state'] = state
    # PKCE: the library generates a code_verifier automatically;
    # persist it so the callback flow can send it with the token request.
    session['google_code_verifier'] = flow.code_verifier
    return auth_url


def complete_google_auth(auth_request, redirect_uri):
    """
    Exchange the Google authorization code for tokens.
    Returns a dict of user claims on success, or None on failure.
    """
    state = session.pop('google_oauth_state', None)
    if state is None:
        return None

    code_verifier = session.pop('google_code_verifier', None)

    try:
        flow = _google_flow(redirect_uri)
        flow.code_verifier = code_verifier
        flow.fetch_token(authorization_response=auth_request.url)
    except Exception:
        logger.warning('Google SSO token exchange failed', exc_info=True)
        return None

    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    try:
        claims = google_id_token.verify_oauth2_token(
            flow.credentials.id_token,
            google_requests.Request(),
            current_app.app_config.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        logger.warning('Google SSO: invalid id_token', exc_info=True)
        return None

    email = claims.get('email')
    if not email:
        logger.warning('Google SSO: no email in id_token')
        return None

    return {
        'email': email.lower(),
        'name': claims.get('name', ''),
        'provider': 'google',
        'provider_id': claims.get('sub', ''),
    }


# ------------------------------------------------------------------
# Shared SSO user management
# ------------------------------------------------------------------

def find_or_create_sso_user(claims):
    """
    Look up AppUser by email; create one if not found.
    For existing users that haven't used SSO before, link their
    sso_provider/sso_id fields.
    """
    db = current_app.db
    user = db.get_app_user_by_email(claims['email'])

    if user is None:
        user = AppUser(
            email=claims['email'],
            password_hash=generate_password_hash(secrets.token_hex(32)),
            role=UserRole.CLIENT,
            display_name=claims.get('name') or None,
            is_active=True,
            sso_provider=claims['provider'],
            sso_id=claims['provider_id'],
        )
        db.create_app_user(user)
        logger.info('Created SSO user (%s): %s', claims['provider'], user.email)
        return user

    # Link SSO if not already set
    if not user.sso_provider:
        user.sso_provider = claims['provider']
        user.sso_id = claims['provider_id']
        db.update_app_user(user)
        logger.info('Linked %s SSO to existing user: %s', claims['provider'], user.email)

    return user


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        if not email or not password:
            flash(_('Please enter both email and password.'), 'danger')
            return render_template('auth/login.html')
        
        user = current_app.db.get_app_user_by_email(email)
        
        if user is None:
            flash(_('Invalid email or password.'), 'danger')
            return render_template('auth/login.html')
        
        if user.is_locked():
            flash(_('Account is temporarily locked. Please try again later.'), 'danger')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash(_('Your account has been deactivated. Please contact an administrator.'), 'danger')
            return render_template('auth/login.html')
        
        if not user.check_password(password):
            user.record_login(success=False)
            current_app.db.update_app_user(user)
            flash(_('Invalid email or password.'), 'danger')
            return render_template('auth/login.html')
        
        user.record_login(success=True)
        current_app.db.update_app_user(user)
        
        login_user(user, remember=remember)
        
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        
        return redirect(url_for('dashboard'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash(_('You have been logged out.'), 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    admin_count = current_app.db.count_app_users(role=UserRole.ADMIN)
    is_first_user = admin_count == 0
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        display_name = request.form.get('display_name', '').strip()
        
        errors = []
        
        if not email:
            errors.append(_('Email is required.'))
        elif '@' not in email:
            errors.append(_('Please enter a valid email address.'))
        
        if not password:
            errors.append(_('Password is required.'))
        elif len(password) < 8:
            errors.append(_('Password must be at least 8 characters.'))
        
        if password != confirm_password:
            errors.append(_('Passwords do not match.'))
        
        if current_app.db.app_user_exists(email):
            errors.append(_('An account with this email already exists.'))
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', is_first_user=is_first_user)
        
        role = UserRole.ADMIN if is_first_user else UserRole.CLIENT

        user = AppUser.create(
            email=email,
            password=password,
            role=role,
            display_name=display_name or None
        )
        if is_first_user:
            user.is_superadmin = True

        try:
            current_app.db.create_app_user(user)
            
            if is_first_user:
                flash(_('Admin account created successfully. Please log in.'), 'success')
            else:
                flash(_('Account created successfully. Please log in.'), 'success')
            
            return redirect(url_for('auth.login'))
        
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('auth/register.html', is_first_user=is_first_user)
    
    return render_template('auth/register.html', is_first_user=is_first_user)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            display_name = request.form.get('display_name', '').strip()
            current_user.display_name = display_name or None
            current_user.update_timestamp()
            current_app.db.update_app_user(current_user)
            flash(_('Profile updated successfully.'), 'success')
        
        elif action == 'change_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not current_user.check_password(current_password):
                flash(_('Current password is incorrect.'), 'danger')
            elif len(new_password) < 8:
                flash(_('New password must be at least 8 characters.'), 'danger')
            elif new_password != confirm_password:
                flash(_('New passwords do not match.'), 'danger')
            else:
                current_user.set_password(new_password)
                current_user.update_timestamp()
                current_app.db.update_app_user(current_user)
                flash(_('Password changed successfully.'), 'success')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')


@auth_bp.route('/users')
@permission_required('users', 'read')
def user_list():
    """List all users"""
    users = current_app.db.get_app_users()
    return render_template('auth/user_list.html', users=users)


@auth_bp.route('/users/create', methods=['GET', 'POST'])
@permission_required('users', 'create')
def user_create():
    """Create a new user"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        display_name = request.form.get('display_name', '').strip()

        errors = []

        if not email or '@' not in email:
            errors.append(_('Please enter a valid email address.'))

        if not password or len(password) < 8:
            errors.append(_('Password must be at least 8 characters.'))

        if current_app.db.app_user_exists(email):
            errors.append(_('An account with this email already exists.'))

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/user_create.html')

        user = AppUser.create(
            email=email,
            password=password,
            role=UserRole.CLIENT,
            display_name=display_name or None
        )
        user.is_verified = True

        try:
            current_app.db.create_app_user(user)
            flash(_('User created successfully.'), 'success')
            return redirect(url_for('auth.user_list'))
        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('auth/user_create.html')


@auth_bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@permission_required('users', 'update')
def user_edit(user_id):
    """Edit a user"""
    user = current_app.db.get_app_user(user_id)
    if not user:
        flash(_('User not found.'), 'danger')
        return redirect(url_for('auth.user_list'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update':
            user.display_name = request.form.get('display_name', '').strip() or None
            user.is_active = request.form.get('is_active') == 'on'
            # Only superadmins can toggle superadmin
            if getattr(current_user, 'is_superadmin', False):
                user.is_superadmin = request.form.get('is_superadmin') == 'on'
            user.update_timestamp()
            current_app.db.update_app_user(user)
            flash(_('User updated successfully.'), 'success')

        elif action == 'reset_password':
            new_password = request.form.get('new_password', '')
            if len(new_password) < 8:
                flash(_('Password must be at least 8 characters.'), 'danger')
            else:
                user.set_password(new_password)
                user.failed_login_count = 0
                user.locked_until = None
                user.update_timestamp()
                current_app.db.update_app_user(user)
                flash(_('Password reset successfully.'), 'success')

        elif action == 'unlock':
            user.failed_login_count = 0
            user.locked_until = None
            user.update_timestamp()
            current_app.db.update_app_user(user)
            flash(_('Account unlocked.'), 'success')

        return redirect(url_for('auth.user_edit', user_id=user_id))

    # Build project membership data for display
    user_projects = []
    projects = current_app.db.get_projects_for_user(user_id)
    all_groups = current_app.db.get_all_groups()
    group_map = {g.id: g.name for g in all_groups}
    for p in projects:
        member = next((m for m in p.members if m.user_id == user_id), None)
        if member:
            group_names = [group_map.get(gid, '?') for gid in member.group_ids]
            user_projects.append({
                'id': p.id, 'name': p.name, 'group_names': group_names
            })

    return render_template('auth/user_edit.html', user=user, user_projects=user_projects)


@auth_bp.route('/users/<user_id>/delete', methods=['POST'])
@permission_required('users', 'delete')
def user_delete(user_id):
    """Delete a user"""
    if current_user.id == user_id:
        flash(_('You cannot delete your own account.'), 'danger')
        return redirect(url_for('auth.user_list'))
    
    user = current_app.db.get_app_user(user_id)
    if not user:
        flash(_('User not found.'), 'danger')
        return redirect(url_for('auth.user_list'))
    
    current_app.db.delete_app_user(user_id)
    flash(_('User deleted successfully.'), 'success')
    return redirect(url_for('auth.user_list'))


# ------------------------------------------------------------------
# Microsoft SSO routes
# ------------------------------------------------------------------

@auth_bp.route('/login/microsoft')
def microsoft_login():
    """Redirect user to Microsoft login page."""
    if not current_app.app_config.MICROSOFT_SSO_ENABLED:
        abort(404)
    redirect_uri = request.url_root.rstrip('/') + current_app.app_config.MICROSOFT_REDIRECT_PATH
    auth_url = get_microsoft_auth_url(redirect_uri)
    return redirect(auth_url)


@auth_bp.route('/microsoft/callback')
def microsoft_callback():
    """Handle the OAuth callback from Microsoft."""
    if not current_app.app_config.MICROSOFT_SSO_ENABLED:
        abort(404)

    redirect_uri = request.url_root.rstrip('/') + current_app.app_config.MICROSOFT_REDIRECT_PATH
    claims = complete_microsoft_auth(request, redirect_uri)

    if claims is None:
        flash(_('Microsoft sign-in failed. Please try again.'), 'danger')
        return redirect(url_for('auth.login'))

    user = find_or_create_sso_user(claims)

    if not user.is_active:
        flash(_('Your account has been deactivated.'), 'danger')
        return redirect(url_for('auth.login'))

    user.record_login(success=True)
    current_app.db.update_app_user(user)
    login_user(user)
    return redirect(url_for('dashboard'))


# ------------------------------------------------------------------
# Google SSO routes
# ------------------------------------------------------------------

@auth_bp.route('/login/google')
def google_login():
    """Redirect user to Google login page."""
    if not current_app.app_config.GOOGLE_SSO_ENABLED:
        abort(404)
    redirect_uri = request.url_root.rstrip('/') + current_app.app_config.GOOGLE_REDIRECT_PATH
    auth_url = get_google_auth_url(redirect_uri)
    return redirect(auth_url)


@auth_bp.route('/google/callback')
def google_callback():
    """Handle the OAuth callback from Google."""
    if not current_app.app_config.GOOGLE_SSO_ENABLED:
        abort(404)

    redirect_uri = request.url_root.rstrip('/') + current_app.app_config.GOOGLE_REDIRECT_PATH
    claims = complete_google_auth(request, redirect_uri)

    if claims is None:
        flash(_('Google sign-in failed. Please try again.'), 'danger')
        return redirect(url_for('auth.login'))

    user = find_or_create_sso_user(claims)

    if not user.is_active:
        flash(_('Your account has been deactivated.'), 'danger')
        return redirect(url_for('auth.login'))

    user.record_login(success=True)
    current_app.db.update_app_user(user)
    login_user(user)
    return redirect(url_for('dashboard'))
