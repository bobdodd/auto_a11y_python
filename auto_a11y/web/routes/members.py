"""Membership management routes for project access control."""
from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user

from auto_a11y.core.permissions import permission_required

members_bp = Blueprint('members', __name__)


@members_bp.route('/projects/<project_id>/members', methods=['GET'])
@permission_required('project_members', 'read')
def list_project_members(project_id):
    """List members of a project with their groups."""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    all_groups = current_app.db.get_all_groups()
    group_map = {g.id: g for g in all_groups}

    members = []
    for m in project.members:
        user = current_app.db.get_app_user(m.user_id)
        member_groups = [
            {'id': gid, 'name': group_map[gid].name}
            for gid in m.group_ids
            if gid in group_map
        ]
        members.append({
            'user_id': m.user_id,
            'email': user.email if user else '(deleted user)',
            'display_name': user.display_name if user else None,
            'groups': member_groups,
        })

    return jsonify({
        'members': members,
        'available_groups': [{'id': g.id, 'name': g.name} for g in all_groups],
    })


@members_bp.route('/projects/<project_id>/members', methods=['POST'])
@permission_required('project_members', 'create')
def add_project_member(project_id):
    """Add a member to a project with group assignments."""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json() or request.form
    user_id = data.get('user_id')
    group_ids = data.getlist('group_ids') if hasattr(data, 'getlist') else data.get('group_ids', [])

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    user = current_app.db.get_app_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not group_ids:
        return jsonify({'error': 'At least one group is required'}), 400

    current_app.db.add_project_member(project_id, user_id, group_ids)
    return jsonify({'success': True, 'message': f'Added {user.email}'})


@members_bp.route('/projects/<project_id>/members/<user_id>', methods=['PUT'])
@permission_required('project_members', 'update')
def update_project_member(project_id, user_id):
    """Update a member's group assignments."""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json() or request.form
    group_ids = data.getlist('group_ids') if hasattr(data, 'getlist') else data.get('group_ids', [])

    if not group_ids:
        return jsonify({'error': 'At least one group is required'}), 400

    current_app.db.update_project_member_groups(project_id, user_id, group_ids)
    return jsonify({'success': True})


@members_bp.route('/projects/<project_id>/members/<user_id>', methods=['DELETE'])
@permission_required('project_members', 'delete')
def remove_project_member(project_id, user_id):
    """Remove a member from a project."""
    if user_id == str(current_user.get_id()):
        return jsonify({'error': 'Cannot remove yourself'}), 400

    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    current_app.db.remove_project_member(project_id, user_id)
    return jsonify({'success': True})


@members_bp.route('/members/api/search-users', methods=['GET'])
def search_users():
    """Search app users by email or display name for member autocomplete."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'users': []})

    exclude_project = request.args.get('exclude_project', '').strip()
    try:
        limit = min(int(request.args.get('limit', 10)), 20)
    except (ValueError, TypeError):
        limit = 10

    exclude_ids = []
    if exclude_project:
        try:
            project = current_app.db.get_project(exclude_project)
            if project:
                exclude_ids = [m.user_id for m in project.members]
        except Exception:
            pass

    users = current_app.db.search_app_users(
        query=q,
        exclude_user_ids=exclude_ids if exclude_ids else None,
        limit=limit
    )

    return jsonify({
        'users': [
            {
                'user_id': str(u.get_id()),
                'email': u.email,
                'display_name': u.display_name,
            }
            for u in users
        ]
    })
