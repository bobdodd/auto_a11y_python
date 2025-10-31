"""
Routes for managing website users (test users for authenticated testing)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from auto_a11y.models import WebsiteUser, LoginConfig, AuthenticationMethod
import logging

logger = logging.getLogger(__name__)

website_users_bp = Blueprint('website_users', __name__)


@website_users_bp.route('/website/<website_id>/users')
def list_users(website_id):
    """List all test users for a website"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('index'))

    # Get project for context
    project = current_app.db.get_project(website.project_id) if website else None

    # Get all users
    users = current_app.db.get_website_users(website_id)

    # Get unique roles
    all_roles = current_app.db.get_user_roles_for_website(website_id)

    return render_template('website_users/list.html',
                         website=website,
                         project=project,
                         users=users,
                         all_roles=all_roles)


@website_users_bp.route('/website/<website_id>/users/create', methods=['GET', 'POST'])
def create_user(website_id):
    """Create a new test user"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('index'))

    project = current_app.db.get_project(website.project_id) if website else None

    if request.method == 'POST':
        try:
            data = request.form

            # Parse roles from comma-separated string
            roles_str = data.get('roles', '').strip()
            roles = [r.strip() for r in roles_str.split(',') if r.strip()] if roles_str else []

            # Create login config
            auth_method_str = data.get('authentication_method', 'form_login')
            login_config = LoginConfig(
                authentication_method=AuthenticationMethod(auth_method_str),
                login_url=data.get('login_url', '').strip() or None,
                username_field_selector=data.get('username_field_selector', '').strip() or None,
                password_field_selector=data.get('password_field_selector', '').strip() or None,
                submit_button_selector=data.get('submit_button_selector', '').strip() or None,
                success_indicator_selector=data.get('success_indicator_selector', '').strip() or None,
                session_timeout_minutes=int(data.get('session_timeout_minutes', 30))
            )

            # Create user
            user = WebsiteUser(
                website_id=website_id,
                username=data.get('username', '').strip(),
                password=data.get('password', '').strip(),
                display_name=data.get('display_name', '').strip() or None,
                roles=roles,
                description=data.get('description', '').strip() or None,
                login_config=login_config,
                enabled=data.get('enabled') == 'on'
            )

            user_id = current_app.db.create_website_user(user)
            flash(f'Test user "{user.name_display}" created successfully', 'success')
            return redirect(url_for('website_users.list_users', website_id=website_id))

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            flash(f'Error creating user: {str(e)}', 'error')

    # Get existing roles for autocomplete
    existing_roles = current_app.db.get_user_roles_for_website(website_id)

    return render_template('website_users/create.html',
                         website=website,
                         project=project,
                         existing_roles=existing_roles,
                         auth_methods=[m for m in AuthenticationMethod])


@website_users_bp.route('/user/<user_id>')
def view_user(user_id):
    """View user details"""
    user = current_app.db.get_website_user(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('index'))

    website = current_app.db.get_website(user.website_id)
    project = current_app.db.get_project(website.project_id) if website else None

    return render_template('website_users/view.html',
                         user=user,
                         website=website,
                         project=project)


@website_users_bp.route('/user/<user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit a test user"""
    user = current_app.db.get_website_user(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('index'))

    website = current_app.db.get_website(user.website_id)
    project = current_app.db.get_project(website.project_id) if website else None

    if request.method == 'POST':
        try:
            data = request.form

            # Parse roles
            roles_str = data.get('roles', '').strip()
            roles = [r.strip() for r in roles_str.split(',') if r.strip()] if roles_str else []

            # Update login config
            user.login_config.authentication_method = AuthenticationMethod(
                data.get('authentication_method', 'form_login')
            )
            user.login_config.login_url = data.get('login_url', '').strip() or None
            user.login_config.username_field_selector = data.get('username_field_selector', '').strip() or None
            user.login_config.password_field_selector = data.get('password_field_selector', '').strip() or None
            user.login_config.submit_button_selector = data.get('submit_button_selector', '').strip() or None
            user.login_config.success_indicator_selector = data.get('success_indicator_selector', '').strip() or None
            user.login_config.session_timeout_minutes = int(data.get('session_timeout_minutes', 30))

            # Update user fields
            user.username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            if password:  # Only update password if provided
                user.password = password
            user.display_name = data.get('display_name', '').strip() or None
            user.roles = roles
            user.description = data.get('description', '').strip() or None
            user.enabled = data.get('enabled') == 'on'

            current_app.db.update_website_user(user)
            flash(f'Test user "{user.name_display}" updated successfully', 'success')
            return redirect(url_for('website_users.list_users', website_id=user.website_id))

        except Exception as e:
            logger.error(f"Error updating user: {e}")
            flash(f'Error updating user: {str(e)}', 'error')

    # Get existing roles for autocomplete
    existing_roles = current_app.db.get_user_roles_for_website(user.website_id)

    return render_template('website_users/edit.html',
                         user=user,
                         website=website,
                         project=project,
                         existing_roles=existing_roles,
                         auth_methods=[m for m in AuthenticationMethod])


@website_users_bp.route('/user/<user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a test user"""
    user = current_app.db.get_website_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        website_id = user.website_id
        current_app.db.delete_website_user(user_id)
        return jsonify({
            'success': True,
            'message': 'User deleted successfully',
            'redirect': url_for('website_users.list_users', website_id=website_id)
        })
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({'error': str(e)}), 500


@website_users_bp.route('/user/<user_id>/toggle', methods=['POST'])
def toggle_user(user_id):
    """Enable/disable a test user"""
    user = current_app.db.get_website_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        user.enabled = not user.enabled
        success = current_app.db.update_website_user(user)

        return jsonify({
            'success': success,
            'enabled': user.enabled,
            'message': f'User {"enabled" if user.enabled else "disabled"}'
        })
    except Exception as e:
        logger.error(f"Error toggling user: {e}")
        return jsonify({'error': str(e)}), 500
