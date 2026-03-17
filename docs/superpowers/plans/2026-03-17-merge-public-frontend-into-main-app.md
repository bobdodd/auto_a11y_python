# Merge Public Frontend Into Main App - Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge all public frontend features (token-based sharing, SSO login, client read-only views) into the existing main Flask app so there is exactly one application, one login screen, and one server process.

**Architecture:** The public frontend's features become a new Blueprint (`public_bp`) registered in the existing `auto_a11y/web/app.py`. Token-based routes (`/t/<token>/...`), SSO routes, and client read-only views all live within the main app's URL space. The public frontend's templates go into a `public/` subdirectory of the main app's templates. The public frontend's static assets (CSS/JS) go into a `public/` subdirectory of the main app's static. The existing login page gets SSO buttons added to it. The separate `public_frontend/` directory is deleted at the end.

**Tech Stack:** Python/Flask, Flask-Login (already present), itsdangerous, msal, google-auth-oauthlib, Flask-Limiter

---

## File Structure

### New files to create:
- `auto_a11y/web/routes/public.py` — New blueprint with all public/token/client routes + SSO routes (merged from `public_frontend/routes.py` + `public_frontend/auth.py`)
- `auto_a11y/web/templates/public/` — Directory for public-facing templates (copied from `public_frontend/templates/`)
  - `public_base.html` — Public base template (adapted to reference main app static)
  - `project.html`, `website.html`, `page.html`, `project_list.html` — Read-only client views
  - `error/403.html` — Token-specific 403 page
- `auto_a11y/web/static/public/` — Directory for public-specific static assets
  - `css/tokens.css`, `css/main.css`, `css/print.css`, `css/reset.css`
  - `js/enhancements.js`

### Files to modify:
- `auto_a11y/web/app.py` — Register `public_bp`, add SSO config properties to context processor, update `require_login` to allow public routes, add 403 error handler
- `auto_a11y/web/routes/__init__.py` — Export `public_bp`
- `auto_a11y/web/templates/auth/login.html` — Add SSO buttons (Microsoft/Google)
- `auto_a11y/web/routes/auth.py` — Add SSO helper functions and SSO callback routes
- `config.py` — Add SSO config fields (Microsoft/Google client ID, secret, tenant, redirect paths), add TOKEN_SALT, remove PUBLIC_BASE_URL
- `auto_a11y/web/routes/share_tokens.py` — Change public URL generation from external URL to internal `url_for('public.token_landing', ...)`
- `.env.example` — Remove PUBLIC_BASE_URL, PUBLIC_HOST, PUBLIC_PORT; keep SSO vars

### Files to delete (last task):
- `public_frontend/` — Entire directory (app.py, auth.py, routes.py, config.py, run_public.py, templates/, static/, translations/, __init__.py)

---

## Task 1: Add SSO and Token Config Fields to Main Config

**Files:**
- Modify: `config.py`

- [ ] **Step 1: Read `config.py` current state**

Verify current content matches what we expect.

- [ ] **Step 2: Add SSO and token config fields to `Config` dataclass**

Add these fields after the existing `PUBLIC_BASE_URL` line (and remove `PUBLIC_BASE_URL`):

```python
    # Share token salt (must match between token creation and validation)
    TOKEN_SALT: str = 'public-share-token'

    # Rate limiting for public routes
    RATELIMIT_DEFAULT: str = os.getenv('RATELIMIT_DEFAULT', '60/minute')

    # Microsoft SSO (optional -- leave blank to disable)
    MICROSOFT_CLIENT_ID: str = os.getenv('MICROSOFT_CLIENT_ID', '')
    MICROSOFT_CLIENT_SECRET: str = os.getenv('MICROSOFT_CLIENT_SECRET', '')
    MICROSOFT_TENANT_ID: str = os.getenv('MICROSOFT_TENANT_ID', 'common')
    MICROSOFT_REDIRECT_PATH: str = '/auth/microsoft/callback'

    # Google SSO (optional -- leave blank to disable)
    GOOGLE_CLIENT_ID: str = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET: str = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_PATH: str = '/auth/google/callback'

    @property
    def MICROSOFT_AUTHORITY(self) -> str:
        return f'https://login.microsoftonline.com/{self.MICROSOFT_TENANT_ID}'

    @property
    def MICROSOFT_SCOPE(self) -> list:
        return ['User.Read']

    @property
    def MICROSOFT_SSO_ENABLED(self) -> bool:
        return bool(self.MICROSOFT_CLIENT_ID and self.MICROSOFT_CLIENT_SECRET)

    @property
    def GOOGLE_SSO_ENABLED(self) -> bool:
        return bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET)

    @property
    def SSO_ENABLED(self) -> bool:
        return self.MICROSOFT_SSO_ENABLED or self.GOOGLE_SSO_ENABLED
```

Remove the `PUBLIC_BASE_URL` field entirely.

- [ ] **Step 3: Verify `config.py` is syntactically valid**

Run: `cd /home/tait/Documents/cnib/code/auto_a11y_python && .venv/bin/python -c "import config; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Update `.env.example`**

Remove `PUBLIC_BASE_URL`, `PUBLIC_HOST`, `PUBLIC_PORT`. Keep SSO vars.

- [ ] **Step 5: Commit**

```bash
git add config.py .env.example
git commit -m "feat: add SSO and token config to main Config, remove PUBLIC_BASE_URL"
```

---

## Task 2: Add SSO Helpers and Routes to Main Auth Module

**Files:**
- Modify: `auto_a11y/web/routes/auth.py`

The SSO logic from `public_frontend/auth.py` needs to be merged into the main app's auth module. This includes: Microsoft SSO helpers, Google SSO helpers, `find_or_create_sso_user`, and the SSO login/callback routes.

- [ ] **Step 1: Read `auto_a11y/web/routes/auth.py` current state**

Verify existing content.

- [ ] **Step 2: Add SSO imports at top of file**

Add after existing imports:

```python
import hashlib
import logging
import secrets

from itsdangerous import URLSafeSerializer, BadSignature
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)
```

- [ ] **Step 3: Add SSO helper functions after the `auditor_required` function**

Add these functions (copied from `public_frontend/auth.py` lines 139-309, adapted to use `current_app.app_config` for config access):

```python
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
    from google_auth_oauthlib.flow import Flow
    config = current_app.app_config
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
    return auth_url


def complete_google_auth(auth_request, redirect_uri):
    """
    Exchange the Google authorization code for tokens.
    Returns a dict of user claims on success, or None on failure.
    """
    state = session.pop('google_oauth_state', None)
    if state is None:
        return None

    try:
        flow = _google_flow(redirect_uri)
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
```

- [ ] **Step 4: Add SSO login and callback routes to auth blueprint**

Add these routes at the end of `auth.py` (before the file ends):

```python
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
```

**IMPORTANT:** The `MICROSOFT_REDIRECT_PATH` in config is `/auth/microsoft/callback`. Since the auth blueprint is mounted at `/auth`, the route within the blueprint is `/microsoft/callback` — this produces the full path `/auth/microsoft/callback` which matches the config. Same for Google: blueprint route `/google/callback` → full path `/auth/google/callback`.

- [ ] **Step 5: Add missing imports to the top of auth.py**

Make sure these are imported (add what's missing):
- `from flask import ..., session, g, abort` (add `session`, `g`, `abort` to the existing import)
- `import hashlib`, `import logging`, `import secrets`
- `from itsdangerous import URLSafeSerializer, BadSignature`
- `from werkzeug.security import generate_password_hash`

- [ ] **Step 6: Verify syntax**

Run: `.venv/bin/python -c "from auto_a11y.web.routes.auth import auth_bp; print('OK')"`
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add auto_a11y/web/routes/auth.py
git commit -m "feat: add SSO helpers, token validation, and SSO routes to main auth module"
```

---

## Task 3: Create the Public Blueprint (Routes)

**Files:**
- Create: `auto_a11y/web/routes/public.py`

This is the core of the public frontend's route logic, adapted as a blueprint within the main app.

- [ ] **Step 1: Create `auto_a11y/web/routes/public.py`**

```python
"""
Public-facing routes for token-based and client-login-based access to test results.
Integrated into the main app as a blueprint.
"""

from collections import defaultdict

from flask import (
    Blueprint, render_template, current_app, request, redirect,
    url_for, abort, g,
)
from flask_babel import _
from flask_login import current_user

from auto_a11y.models import TokenScope, PageStatus
from auto_a11y.reporting.issue_descriptions_translated import get_detailed_issue_description
from auto_a11y.web.routes.auth import require_access, check_scope

public_bp = Blueprint(
    'public', __name__,
    static_folder='../static/public',
    static_url_path='/public/static',
)
# NOTE: No template_folder set. All render_template calls use 'public/...' paths
# which resolve via the app-level template loader (auto_a11y/web/templates/).


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def group_by_touchpoint(violations):
    """Group a list of Violation objects by their touchpoint field."""
    groups = defaultdict(list)
    for v in violations:
        groups[v.touchpoint or _('Other')].append(v)
    return dict(sorted(groups.items()))


def sort_pages(pages, sort_by='url', sort_dir='asc'):
    """Sort a list of Page objects by the given field."""
    key_map = {
        'url': lambda p: (p.url or '').lower(),
        'violations': lambda p: p.violation_count,
        'warnings': lambda p: p.warning_count,
        'last_tested': lambda p: p.last_tested or p.discovered_at,
    }
    key_fn = key_map.get(sort_by, key_map['url'])
    reverse = sort_dir == 'desc'
    return sorted(pages, key=key_fn, reverse=reverse)


def _get_project_for_token():
    """For token-based access, resolve the project from g.access_scope."""
    if g.access_scope == TokenScope.PROJECT:
        return current_app.db.get_project(g.access_scope_id)
    elif g.access_scope == TokenScope.WEBSITE:
        website = current_app.db.get_website(g.access_scope_id)
        if website:
            return current_app.db.get_project(website.project_id)
    return None


# ------------------------------------------------------------------
# Token-based routes
# ------------------------------------------------------------------

@public_bp.route('/t/<token>/')
@require_access
def token_landing(token):
    """Landing page for a share-link token."""
    if g.access_scope == TokenScope.WEBSITE:
        website = current_app.db.get_website(g.access_scope_id)
        if not website:
            abort(404)
        project = current_app.db.get_project(website.project_id)
        pages = current_app.db.get_pages(website.id)
        sort_by = request.args.get('sort', 'url')
        sort_dir = request.args.get('dir', 'asc')
        sorted_pages = sort_pages(pages, sort_by, sort_dir)
        return render_template(
            'public/website.html',
            project=project, website=website, pages=sorted_pages,
            sort_by=sort_by, sort_dir=sort_dir, token=token,
        )

    # Project-scoped token
    project = current_app.db.get_project(g.access_scope_id)
    if not project:
        abort(404)
    stats = current_app.db.get_project_stats(g.access_scope_id)
    websites = current_app.db.get_websites(g.access_scope_id)
    return render_template(
        'public/project.html',
        project=project, stats=stats, websites=websites, token=token,
    )


@public_bp.route('/t/<token>/w/<website_id>/')
@require_access
def token_website(token, website_id):
    """Website detail via token."""
    check_scope('website', website_id)
    website = current_app.db.get_website(website_id)
    if not website:
        abort(404)
    project = current_app.db.get_project(website.project_id)
    pages = current_app.db.get_pages(website_id)
    sort_by = request.args.get('sort', 'url')
    sort_dir = request.args.get('dir', 'asc')
    sorted_pages = sort_pages(pages, sort_by, sort_dir)
    return render_template(
        'public/website.html',
        project=project, website=website, pages=sorted_pages,
        sort_by=sort_by, sort_dir=sort_dir, token=token,
    )


@public_bp.route('/t/<token>/w/<website_id>/p/<page_id>/')
@require_access
def token_page(token, website_id, page_id):
    """Page detail (issues) via token."""
    check_scope('page', page_id)
    page = current_app.db.get_page(page_id)
    if not page:
        abort(404)
    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(website.project_id) if website else None
    test_result = current_app.db.get_latest_test_result(page_id)

    violation_groups = {}
    warning_groups = {}
    info_groups = {}
    if test_result:
        violation_groups = group_by_touchpoint(test_result.violations)
        warning_groups = group_by_touchpoint(test_result.warnings)
        info_groups = group_by_touchpoint(test_result.info)

    return render_template(
        'public/page.html',
        project=project, website=website, page=page,
        test_result=test_result,
        violation_groups=violation_groups,
        warning_groups=warning_groups,
        info_groups=info_groups,
        token=token,
        get_issue_description=get_detailed_issue_description,
    )


# ------------------------------------------------------------------
# Client (logged-in) read-only routes
# ------------------------------------------------------------------

@public_bp.route('/client/projects/')
@require_access
def client_projects():
    """List all projects (for logged-in clients)."""
    projects = current_app.db.get_all_projects()
    project_data = []
    for project in projects:
        stats = current_app.db.get_project_stats(project.id)
        project_data.append({'project': project, 'stats': stats})
    return render_template('public/project_list.html', project_data=project_data)


@public_bp.route('/client/project/<project_id>/')
@require_access
def client_project(project_id):
    """Project overview (logged-in client)."""
    check_scope('project', project_id)
    project = current_app.db.get_project(project_id)
    if not project:
        abort(404)
    stats = current_app.db.get_project_stats(project_id)
    websites = current_app.db.get_websites(project_id)
    return render_template(
        'public/project.html',
        project=project, stats=stats, websites=websites, token=None,
    )


@public_bp.route('/client/project/<project_id>/w/<website_id>/')
@require_access
def client_website(project_id, website_id):
    """Website detail (logged-in client)."""
    check_scope('website', website_id)
    website = current_app.db.get_website(website_id)
    if not website:
        abort(404)
    project = current_app.db.get_project(project_id)
    pages = current_app.db.get_pages(website_id)
    sort_by = request.args.get('sort', 'url')
    sort_dir = request.args.get('dir', 'asc')
    sorted_pages = sort_pages(pages, sort_by, sort_dir)
    return render_template(
        'public/website.html',
        project=project, website=website, pages=sorted_pages,
        sort_by=sort_by, sort_dir=sort_dir, token=None,
    )


@public_bp.route('/client/project/<project_id>/w/<website_id>/p/<page_id>/')
@require_access
def client_page(project_id, website_id, page_id):
    """Page detail (logged-in client)."""
    check_scope('page', page_id)
    page = current_app.db.get_page(page_id)
    if not page:
        abort(404)
    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(project_id)
    test_result = current_app.db.get_latest_test_result(page_id)

    violation_groups = {}
    warning_groups = {}
    info_groups = {}
    if test_result:
        violation_groups = group_by_touchpoint(test_result.violations)
        warning_groups = group_by_touchpoint(test_result.warnings)
        info_groups = group_by_touchpoint(test_result.info)

    return render_template(
        'public/page.html',
        project=project, website=website, page=page,
        test_result=test_result,
        violation_groups=violation_groups,
        warning_groups=warning_groups,
        info_groups=info_groups,
        token=None,
        get_issue_description=get_detailed_issue_description,
    )
```

- [ ] **Step 2: Verify syntax**

Run: `.venv/bin/python -c "from auto_a11y.web.routes.public import public_bp; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/routes/public.py
git commit -m "feat: create public blueprint with token and client read-only routes"
```

---

## Task 4: Copy and Adapt Public Templates

**Files:**
- Create: `auto_a11y/web/templates/public/public_base.html`
- Create: `auto_a11y/web/templates/public/project.html`
- Create: `auto_a11y/web/templates/public/website.html`
- Create: `auto_a11y/web/templates/public/page.html`
- Create: `auto_a11y/web/templates/public/project_list.html`
- Create: `auto_a11y/web/templates/public/error/403.html`

The templates need to be adapted so that:
1. Static file references use the `public.static` endpoint: `url_for('public.static', filename='...')`
2. Route references use the `public.` prefix (they already do in the originals)
3. The logout link points to `auth.logout` instead of `public.logout`
4. The login link in the 403 page points to `auth.login`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p auto_a11y/web/templates/public/error
```

- [ ] **Step 2: Copy and adapt `public_base.html`**

Copy `public_frontend/templates/public_base.html` to `auto_a11y/web/templates/public/public_base.html`.

Changes needed:
- Change all `url_for('static', ...)` to `url_for('public.static', ...)`
- Change `url_for('set_language', ...)` stays the same (main app has this route)
- Change `url_for('public.logout')` to `url_for('auth.logout')`
- Keep `current_user.name_display` as-is (this is a property on `AppUser` at line 51 of `app_user.py` that falls back to the email prefix when `display_name` is None — do NOT change to `display_name`)

- [ ] **Step 3: Copy and adapt view templates**

Copy these files from `public_frontend/templates/` to `auto_a11y/web/templates/public/`:
- `project.html` — No changes needed (already uses `public.*` url_for)
- `website.html` — No changes needed
- `page.html` — No changes needed
- `project_list.html` — No changes needed

All these templates extend `public_base.html` which is now at `public/public_base.html`. Since the templates are rendered from within the `public/` directory, `{% extends "public_base.html" %}` should work. However, since the main app's template loader also searches the top-level templates dir, we need to be careful. Use `{% extends "public/public_base.html" %}` to be explicit.

**Update all four templates**: Change `{% extends "public_base.html" %}` to `{% extends "public/public_base.html" %}`.

- [ ] **Step 4: Copy and adapt error/403.html**

Copy `public_frontend/templates/error/403.html` to `auto_a11y/web/templates/public/error/403.html`.

Changes:
- `{% extends "public_base.html" %}` → `{% extends "public/public_base.html" %}`
- `url_for('public.login')` → `url_for('auth.login')`

- [ ] **Step 5: Verify templates can be found**

Run: `.venv/bin/python -c "
from auto_a11y.web.app import create_app
from config import Config
app = create_app(Config())
with app.app_context():
    from flask import render_template
    # This would fail if template not found
    print('Template dir check passed')
"`

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/templates/public/
git commit -m "feat: add public-facing templates to main app"
```

---

## Task 5: Copy Public Static Assets

**Files:**
- Create: `auto_a11y/web/static/public/css/tokens.css`
- Create: `auto_a11y/web/static/public/css/reset.css`
- Create: `auto_a11y/web/static/public/css/main.css`
- Create: `auto_a11y/web/static/public/css/print.css`
- Create: `auto_a11y/web/static/public/js/enhancements.js`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p auto_a11y/web/static/public/css
mkdir -p auto_a11y/web/static/public/js
```

- [ ] **Step 2: Copy static assets**

```bash
cp public_frontend/static/css/tokens.css auto_a11y/web/static/public/css/
cp public_frontend/static/css/reset.css auto_a11y/web/static/public/css/
cp public_frontend/static/css/main.css auto_a11y/web/static/public/css/
cp public_frontend/static/css/print.css auto_a11y/web/static/public/css/
cp public_frontend/static/js/enhancements.js auto_a11y/web/static/public/js/
```

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/static/public/
git commit -m "feat: add public-facing static assets to main app"
```

---

## Task 6: Merge French Translations

**Files:**
- Modify: `auto_a11y/web/translations/fr/LC_MESSAGES/messages.po`

The public frontend has 26 translation strings not present in the main app's catalog. These must be merged or the public templates will show untranslated English strings in French locale.

- [ ] **Step 1: Append missing msgid/msgstr pairs to the main .po file**

Add the following entries to the end of `auto_a11y/web/translations/fr/LC_MESSAGES/messages.po` (before the final blank line), under a `# Public frontend` section header comment:

```po
# Public frontend (merged from public_frontend/translations)
msgid "Skip to main content"
msgstr "Passer au contenu principal"

msgid "Breadcrumb"
msgstr "Fil d'Ariane"

msgid "Accessibility Report"
msgstr "Rapport d'accessibilité"

msgid "Last updated"
msgstr "Dernière mise à jour"

msgid "Project Overview"
msgstr "Aperçu du projet"

msgid "Pages Tested"
msgstr "Pages testées"

msgid "Test Coverage"
msgstr "Couverture des tests"

msgid "Test coverage"
msgstr "Couverture des tests"

msgid "Pages tested on %(url)s"
msgstr "Pages testées sur %(url)s"

msgid "Informational"
msgstr "Informations"

msgid "Violation"
msgstr "Violation"

msgid "Warning"
msgstr "Avertissement"

msgid "Info"
msgstr "Info"

msgid "Details"
msgstr "Détails"

msgid "How to fix"
msgstr "Comment corriger"

msgid "Affected HTML"
msgstr "HTML concerné"

msgid "No issues found on this page."
msgstr "Aucun problème trouvé sur cette page."

msgid "This page has not been tested yet."
msgstr "Cette page n'a pas encore été testée."

msgid "Other"
msgstr "Autre"

msgid "Sign in with Microsoft"
msgstr "Se connecter avec Microsoft"

msgid "or"
msgstr "ou"

msgid "Microsoft sign-in failed. Please try again."
msgstr "La connexion Microsoft a échoué. Veuillez réessayer."

msgid "%(tested)s of %(total)s pages tested"
msgstr "%(tested)s sur %(total)s pages testées"

msgid "%(count)s violations"
msgstr "%(count)s violations"

msgid "No projects available."
msgstr "Aucun projet disponible."

msgid "Access Denied"
msgstr "Accès refusé"

msgid "You do not have permission to view this page. The link may have expired or been revoked."
msgstr "Vous n'avez pas la permission de voir cette page. Le lien a peut-être expiré ou a été révoqué."

msgid "Your account has been deactivated."
msgstr "Votre compte a été désactivé."
```

- [ ] **Step 2: Recompile .mo file**

Run: `cd /home/tait/Documents/cnib/code/auto_a11y_python && .venv/bin/python -m babel compile -d auto_a11y/web/translations`

If `babel` CLI is not available via pip, use `msgfmt` directly:
```bash
msgfmt -o auto_a11y/web/translations/fr/LC_MESSAGES/messages.mo auto_a11y/web/translations/fr/LC_MESSAGES/messages.po
```

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/translations/fr/LC_MESSAGES/messages.po auto_a11y/web/translations/fr/LC_MESSAGES/messages.mo
git commit -m "feat: merge public frontend French translations into main app"
```

---

## Task 7: Register Public Blueprint and Wire Up Main App

**Files:**
- Modify: `auto_a11y/web/routes/__init__.py`
- Modify: `auto_a11y/web/app.py`

- [ ] **Step 1: Add public_bp export to routes/__init__.py**

Add import and export of `public_bp` from `auto_a11y.web.routes.public`.

- [ ] **Step 2: Register public_bp in app.py**

In `auto_a11y/web/app.py`, add `public_bp` to the imports from `auto_a11y.web.routes` and register it:

```python
app.register_blueprint(public_bp, url_prefix='')
```

The public blueprint has no prefix — its routes are at `/t/<token>/...` and `/client/...`.

- [ ] **Step 3: Update `require_login` in app.py to exempt public routes**

In the `require_login` before_request handler, add exemptions for the public blueprint's routes. Add these to the `allowed_endpoints` list or add endpoint prefix checks:

```python
# Allow public routes (token-based access + client read-only views)
if request.endpoint and request.endpoint.startswith('public.'):
    return None
```

Also add exemptions for the SSO callback routes:

```python
if request.endpoint and request.endpoint in [
    'auth.microsoft_login', 'auth.microsoft_callback',
    'auth.google_login', 'auth.google_callback',
]:
    return None
```

- [ ] **Step 4: Add SSO config to context processor**

In the `inject_globals` context processor in `app.py`, add:

```python
microsoft_sso_enabled=config.MICROSOFT_SSO_ENABLED,
google_sso_enabled=config.GOOGLE_SSO_ENABLED,
```

- [ ] **Step 5: Add 403 error handler**

The main app currently only has 404 and 500 handlers. Add a 403 handler:

```python
@app.errorhandler(403)
def forbidden(error):
    """403 error handler"""
    if '/api/' in request.path:
        return jsonify({'error': 'Forbidden'}), 403
    # For token-based routes, show the public 403 page
    if request.path.startswith('/t/'):
        return render_template('public/error/403.html'), 403
    return render_template('403.html'), 403
```

- [ ] **Step 5b: Create admin 403 template**

Create `auto_a11y/web/templates/403.html`:

```html
{% extends "base.html" %}

{% block title %}{{ _('Access Denied') }} - {{ _('Auto A11y') }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6 text-center">
        <h1>403</h1>
        <p>{{ _('You do not have permission to access this page.') }}</p>
        <a href="{{ url_for('dashboard') }}" class="btn btn-primary">{{ _('Go Home') }}</a>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 6: Verify the app starts**

Run: `.venv/bin/python -c "
from auto_a11y.web.app import create_app
from config import Config
app = create_app(Config())
print('App created successfully with', len(app.url_map._rules), 'routes')
"`

- [ ] **Step 7: Commit**

```bash
git add auto_a11y/web/routes/__init__.py auto_a11y/web/app.py
git commit -m "feat: register public blueprint in main app, exempt public routes from login"
```

---

## Task 8: Add SSO Buttons to Existing Login Page

**Files:**
- Modify: `auto_a11y/web/templates/auth/login.html`

- [ ] **Step 1: Read current login template**

Already read above. It's a Bootstrap-based login form.

- [ ] **Step 2: Add SSO buttons above the email/password form**

After the `<h4>` card header and before the `<form>`, add SSO buttons:

```html
{% if microsoft_sso_enabled or google_sso_enabled %}
<div class="mb-3">
    {% if microsoft_sso_enabled %}
    <a href="{{ url_for('auth.microsoft_login') }}" class="btn btn-dark w-100 mb-2">
        <i class="bi bi-microsoft"></i> {{ _('Sign in with Microsoft') }}
    </a>
    {% endif %}
    {% if google_sso_enabled %}
    <a href="{{ url_for('auth.google_login') }}" class="btn btn-light w-100 mb-2 border">
        <i class="bi bi-google"></i> {{ _('Sign in with Google') }}
    </a>
    {% endif %}

    <div class="text-center text-muted my-2">
        <span>{{ _('or') }}</span>
    </div>
</div>
{% endif %}
```

This goes inside the `card-body` div, before the `<form>`.

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/templates/auth/login.html
git commit -m "feat: add SSO buttons to main login page"
```

---

## Task 9: Update Share Token URL Generation

**Files:**
- Modify: `auto_a11y/web/routes/share_tokens.py`

Currently, `share_tokens.py` generates the public URL using `PUBLIC_BASE_URL` pointing to port 5002. Since there's now only one app, the URL should use `url_for`.

- [ ] **Step 1: Read the file (already read above)**

- [ ] **Step 2: Change `_create_token` to use `url_for`**

Replace the public URL generation logic:

```python
# Old:
public_base_url = current_app.app_config.PUBLIC_BASE_URL.rstrip('/')
public_url = f"{public_base_url}/t/{token_string}/"

# New:
public_url = url_for('public.token_landing', token=token_string, _external=True)
```

Add `url_for` to the imports from flask.

- [ ] **Step 3: Verify syntax**

Run: `.venv/bin/python -c "from auto_a11y.web.routes.share_tokens import share_tokens_bp; print('OK')"`

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/routes/share_tokens.py
git commit -m "fix: generate share token URLs using url_for instead of external base URL"
```

---

## Task 10: Smoke Test the Integrated App

**Files:** None (testing only)

- [ ] **Step 1: Start the app and check it runs**

Run: `.venv/bin/python run.py &`
Wait a few seconds, then:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/
# Expected: 302 (redirect to login)

curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/auth/login
# Expected: 200

curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/t/fake-token/
# Expected: 403

curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/client/projects/
# Expected: 302 (redirect to login because not authenticated)

curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/health
# Expected: 200
```

- [ ] **Step 2: Check that the login page contains SSO buttons**

Only if SSO is configured in `.env`. If not configured, verify the page loads without errors:

```bash
curl -s http://127.0.0.1:5001/auth/login | grep -c "Login"
# Expected: at least 1 (the login page renders)
```

- [ ] **Step 3: Check public static assets serve correctly**

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/public/static/css/main.css
# Expected: 200
```

- [ ] **Step 4: Stop the test server**

```bash
kill %1
```

---

## Task 11: Delete the Public Frontend Directory

**Files:**
- Delete: `public_frontend/` (entire directory)

- [ ] **Step 1: Verify nothing in the main app imports from `public_frontend`**

```bash
grep -r "public_frontend" auto_a11y/ config.py run.py
# Expected: no matches
```

Also check:
```bash
grep -r "from public_frontend" .
# Expected: only matches in public_frontend/ itself (which we're deleting)
```

- [ ] **Step 2: Delete the directory**

```bash
rm -rf public_frontend/
```

- [ ] **Step 3: Remove `public_frontend` from any imports or references**

Check `requirements.txt` — no changes needed (dependencies are already listed for the main app).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove public_frontend directory (merged into main app)"
```

---

## Task 12: Update README and .env.example

**Files:**
- Modify: `README.md`
- Modify: `.env.example`

- [ ] **Step 1: Update README**

Remove any references to running a separate public frontend on port 5002. The SSO setup documentation should remain (it's still relevant). Update any references from `PUBLIC_BASE_URL` to explain that token URLs are now served by the main app.

- [ ] **Step 2: Final check of .env.example**

Ensure `PUBLIC_BASE_URL`, `PUBLIC_HOST`, `PUBLIC_PORT` are removed (should have been done in Task 1). Verify SSO vars are present.

- [ ] **Step 3: Commit**

```bash
git add README.md .env.example
git commit -m "docs: update README and .env.example for single-app architecture"
```

---

## Summary of URL Changes

| Old URL (public_frontend, port 5002) | New URL (main app, port 5001) |
|---|---|
| `http://localhost:5002/t/<token>/` | `http://localhost:5001/t/<token>/` |
| `http://localhost:5002/t/<token>/w/<id>/` | `http://localhost:5001/t/<token>/w/<id>/` |
| `http://localhost:5002/t/<token>/w/<id>/p/<id>/` | `http://localhost:5001/t/<token>/w/<id>/p/<id>/` |
| `http://localhost:5002/login` | `http://localhost:5001/auth/login` (existing) |
| `http://localhost:5002/login/microsoft` | `http://localhost:5001/auth/login/microsoft` |
| `http://localhost:5002/auth/microsoft/callback` | `http://localhost:5001/auth/microsoft/callback` |
| `http://localhost:5002/login/google` | `http://localhost:5001/auth/login/google` |
| `http://localhost:5002/auth/google/callback` | `http://localhost:5001/auth/google/callback` |
| `http://localhost:5002/projects/` | `http://localhost:5001/client/projects/` |
| `http://localhost:5002/project/<id>/` | `http://localhost:5001/client/project/<id>/` |
| `http://localhost:5002/project/<id>/w/<id>/` | `http://localhost:5001/client/project/<id>/w/<id>/` |
| `http://localhost:5002/project/<id>/w/<id>/p/<id>/` | `http://localhost:5001/client/project/<id>/w/<id>/p/<id>/` |

## Key Design Decisions

1. **Client read-only routes are prefixed with `/client/`** to avoid collisions with admin routes like `/projects/`. Token routes stay at `/t/<token>/...` with no prefix.

2. **SSO goes into the auth blueprint** since it's authentication logic that belongs with login/logout/register. The redirect paths (`/auth/microsoft/callback`) naturally fall under the `/auth` prefix.

3. **Public templates live in `templates/public/`** to keep them clearly separated from admin templates. They use their own base template (`public_base.html`) with different CSS/JS.

4. **Public static assets live in `static/public/`** to keep them separate from admin static assets (Bootstrap-based).

5. **One Flask-Login instance** handles all users. The existing `before_request` login check is updated to exempt public routes (token access doesn't require login; `require_access` decorator handles auth).

6. **The `require_access` decorator** (moved to `auth.py`) handles dual auth: token validation OR Flask-Login session. This is the same logic as before, just in a different file.
