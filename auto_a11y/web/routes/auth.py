"""
Authentication routes for user login, logout, and registration
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from functools import wraps

from auto_a11y.models import AppUser, UserRole

auth_bp = Blueprint('auth', __name__)


def role_required(*roles):
    """
    Decorator to require specific roles for a route.
    
    Usage:
        @role_required(UserRole.ADMIN)
        @role_required(UserRole.ADMIN, UserRole.AUDITOR)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(_('Please log in to access this page.'), 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if current_user.role not in roles:
                flash(_('You do not have permission to access this page.'), 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator requiring admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_('Please log in to access this page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_admin():
            flash(_('Administrator access required.'), 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


def auditor_required(f):
    """Decorator requiring auditor or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_('Please log in to access this page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not (current_user.is_admin() or current_user.is_auditor()):
            flash(_('Auditor access required.'), 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


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
@admin_required
def user_list():
    """List all users (admin only)"""
    users = current_app.db.get_app_users()
    return render_template('auth/user_list.html', users=users)


@auth_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def user_create():
    """Create a new user (admin only)"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        display_name = request.form.get('display_name', '').strip()
        role = request.form.get('role', 'client')
        
        errors = []
        
        if not email or '@' not in email:
            errors.append(_('Please enter a valid email address.'))
        
        if not password or len(password) < 8:
            errors.append(_('Password must be at least 8 characters.'))
        
        if current_app.db.app_user_exists(email):
            errors.append(_('An account with this email already exists.'))
        
        try:
            user_role = UserRole(role)
        except ValueError:
            errors.append(_('Invalid role selected.'))
            user_role = UserRole.CLIENT
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/user_create.html', roles=UserRole)
        
        user = AppUser.create(
            email=email,
            password=password,
            role=user_role,
            display_name=display_name or None
        )
        user.is_verified = True
        
        try:
            current_app.db.create_app_user(user)
            flash(_('User created successfully.'), 'success')
            return redirect(url_for('auth.user_list'))
        except ValueError as e:
            flash(str(e), 'danger')
        
    return render_template('auth/user_create.html', roles=UserRole)


@auth_bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):
    """Edit a user (admin only)"""
    user = current_app.db.get_app_user(user_id)
    if not user:
        flash(_('User not found.'), 'danger')
        return redirect(url_for('auth.user_list'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update':
            user.display_name = request.form.get('display_name', '').strip() or None
            
            new_role = request.form.get('role', 'client')
            try:
                user.role = UserRole(new_role)
            except ValueError:
                pass
            
            user.is_active = request.form.get('is_active') == 'on'
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
    
    return render_template('auth/user_edit.html', user=user, roles=UserRole)


@auth_bp.route('/users/<user_id>/delete', methods=['POST'])
@admin_required
def user_delete(user_id):
    """Delete a user (admin only)"""
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
