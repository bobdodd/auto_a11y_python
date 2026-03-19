"""Membership management routes for project/website access control."""
from flask import Blueprint, request, jsonify, current_app, flash, redirect, url_for
from flask_login import current_user, login_required
from auto_a11y.models.app_user import UserRole
from auto_a11y.web.routes.auth import project_admin_required, project_role_required

members_bp = Blueprint('members', __name__)


@members_bp.route('/projects/<project_id>/members', methods=['GET'])
@project_role_required(UserRole.ADMIN)
def list_project_members(project_id):
    """List members of a project."""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # Enrich with user display info
    members = []
    for m in project.members:
        user = current_app.db.get_app_user(m.user_id)
        members.append({
            'user_id': m.user_id,
            'role': m.role.value,
            'email': user.email if user else '(deleted user)',
            'display_name': user.display_name if user else None,
        })

    # Get all users for the "add member" dropdown (exclude current members)
    member_ids = {m.user_id for m in project.members}
    all_users = current_app.db.get_app_users()
    available_users = [
        {'user_id': str(u.get_id()), 'email': u.email, 'display_name': u.display_name}
        for u in all_users
        if str(u.get_id()) not in member_ids
    ]

    return jsonify({
        'members': members,
        'available_users': available_users,
        'roles': [r.value for r in UserRole],
    })


@members_bp.route('/projects/<project_id>/members', methods=['POST'])
@project_admin_required
def add_project_member(project_id):
    """Add a member to a project."""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json() or request.form
    user_id = data.get('user_id')
    role_str = data.get('role', 'client')

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    user = current_app.db.get_app_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        role = UserRole(role_str)
    except ValueError:
        return jsonify({'error': f'Invalid role: {role_str}'}), 400

    current_app.db.add_project_member(project_id, user_id, role)
    return jsonify({'success': True, 'message': f'Added {user.email} as {role.value}'})


@members_bp.route('/projects/<project_id>/members/<user_id>', methods=['PUT'])
@project_admin_required
def update_project_member(project_id, user_id):
    """Change a member's role on a project."""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json() or request.form
    role_str = data.get('role')
    if not role_str:
        return jsonify({'error': 'role is required'}), 400

    try:
        role = UserRole(role_str)
    except ValueError:
        return jsonify({'error': f'Invalid role: {role_str}'}), 400

    # Prevent self-demotion from admin
    if user_id == str(current_user.get_id()) and role != UserRole.ADMIN:
        return jsonify({'error': 'Cannot demote yourself'}), 400

    current_app.db.update_project_member_role(project_id, user_id, role)
    return jsonify({'success': True})


@members_bp.route('/projects/<project_id>/members/<user_id>', methods=['DELETE'])
@project_admin_required
def remove_project_member(project_id, user_id):
    """Remove a member from a project."""
    # Prevent self-removal
    if user_id == str(current_user.get_id()):
        return jsonify({'error': 'Cannot remove yourself'}), 400

    # Ensure at least one admin remains
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    admin_count = sum(
        1 for m in project.members
        if m.role == UserRole.ADMIN and m.user_id != user_id
    )
    if admin_count == 0:
        return jsonify({'error': 'Cannot remove the last project admin'}), 400

    current_app.db.remove_project_member(project_id, user_id)
    return jsonify({'success': True})


# --- Website member overrides ---

@members_bp.route('/websites/<website_id>/members', methods=['GET'])
@project_admin_required
def list_website_members(website_id):
    """List website-level member overrides."""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404

    project = current_app.db.get_project(website.project_id)

    # Show overrides + inherited roles
    overrides = {}
    for m in website.members:
        overrides[m.user_id] = m.role.value

    members = []
    for m in (project.members if project else []):
        user = current_app.db.get_app_user(m.user_id)
        members.append({
            'user_id': m.user_id,
            'project_role': m.role.value,
            'website_role': overrides.get(m.user_id),  # None = inherited
            'email': user.email if user else '(deleted user)',
            'display_name': user.display_name if user else None,
        })

    return jsonify({'members': members, 'roles': [r.value for r in UserRole]})


@members_bp.route('/websites/<website_id>/members', methods=['POST'])
@project_admin_required
def add_website_member(website_id):
    """Add a website-level role override."""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404

    data = request.get_json() or request.form
    user_id = data.get('user_id')
    role_str = data.get('role', 'client')

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    try:
        role = UserRole(role_str)
    except ValueError:
        return jsonify({'error': f'Invalid role: {role_str}'}), 400

    current_app.db.add_website_member(website_id, user_id, role)
    return jsonify({'success': True})


@members_bp.route('/websites/<website_id>/members/<user_id>', methods=['PUT'])
@project_admin_required
def update_website_member(website_id, user_id):
    """Change a website-level role override."""
    data = request.get_json() or request.form
    role_str = data.get('role')
    if not role_str:
        return jsonify({'error': 'role is required'}), 400

    try:
        role = UserRole(role_str)
    except ValueError:
        return jsonify({'error': f'Invalid role: {role_str}'}), 400

    current_app.db.update_website_member_role(website_id, user_id, role)
    return jsonify({'success': True})


@members_bp.route('/websites/<website_id>/members/<user_id>', methods=['DELETE'])
@project_admin_required
def remove_website_member(website_id, user_id):
    """Remove a website-level role override (reverts to project role)."""
    current_app.db.remove_website_member(website_id, user_id)
    return jsonify({'success': True})
