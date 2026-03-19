"""Central permission resolution for the group-based access control system."""
import logging
from functools import wraps

from flask import current_app, request, g, abort, jsonify, flash, redirect, url_for
from flask_login import current_user

from auto_a11y.models.permission_group import (
    PERMISSION_LEVELS, GLOBAL_RESOURCES, RESOURCE_NOUNS
)

logger = logging.getLogger(__name__)


def _get_db():
    return current_app.db


def _find_member(project, user_id):
    """Find a user's membership entry in a project."""
    uid = str(user_id)
    for m in getattr(project, 'members', []):
        if m.user_id == uid:
            return m
    return None


def user_has_permission(user, project_id, resource, required_level):
    """Check if user has at least `required_level` on `resource` in `project_id`.

    For global resources (users, groups, fixture_tests), pass project_id=None
    and use user_has_global_permission instead.
    """
    if getattr(user, 'is_superadmin', False):
        return True

    if not project_id:
        return False

    db = _get_db()
    project = db.get_project(project_id)
    if not project:
        return False

    member = _find_member(project, user.get_id())
    if not member:
        return False

    groups = db.get_groups_by_ids(member.group_ids)
    if not groups:
        return False

    max_level = max(
        (grp.get_level(resource) for grp in groups),
        default=0
    )
    return max_level >= PERMISSION_LEVELS.get(required_level, 0)


def user_has_global_permission(user, resource, required_level):
    """Check permission across ALL projects the user belongs to.

    Used for global resources: users, groups, fixture_tests.
    """
    if getattr(user, 'is_superadmin', False):
        return True

    db = _get_db()
    user_id = str(user.get_id())
    projects = db.get_projects_for_user(user_id)

    required = PERMISSION_LEVELS.get(required_level, 0)

    for project in projects:
        member = _find_member(project, user_id)
        if not member:
            continue
        groups = db.get_groups_by_ids(member.group_ids)
        level = max((grp.get_level(resource) for grp in groups), default=0)
        if level >= required:
            return True

    return False


def get_effective_permissions(user, project_id):
    """Get the union of all permissions for a user in a project.

    Returns dict of {resource: level_name} representing the max level per resource.
    """
    from auto_a11y.models.permission_group import LEVEL_NAMES

    if getattr(user, 'is_superadmin', False):
        return {r: 'delete' for r in RESOURCE_NOUNS}

    db = _get_db()
    project = db.get_project(project_id)
    if not project:
        return {r: 'none' for r in RESOURCE_NOUNS}

    member = _find_member(project, user.get_id())
    if not member:
        return {r: 'none' for r in RESOURCE_NOUNS}

    groups = db.get_groups_by_ids(member.group_ids)
    result = {}
    for resource in RESOURCE_NOUNS:
        max_level = max((grp.get_level(resource) for grp in groups), default=0)
        result[resource] = LEVEL_NAMES.get(max_level, 'none')
    return result


def _resolve_project_id(**kwargs):
    """Resolve project_id from route kwargs by following resource chains."""
    db = _get_db()

    project_id = kwargs.get('project_id')
    if project_id:
        return project_id

    website_id = kwargs.get('website_id')
    if website_id:
        website = db.get_website(website_id)
        return website.project_id if website else None

    page_id = kwargs.get('page_id')
    if page_id:
        page = db.get_page(page_id)
        if page:
            website = db.get_website(page.website_id)
            return website.project_id if website else None
        return None

    recording_id = kwargs.get('recording_id')
    if recording_id:
        recording = db.get_recording(recording_id)
        return recording.project_id if recording else None

    return None


def permission_required(resource, level):
    """Decorator: require permission on a resource at a given level.

    For project-scoped resources, resolves project_id from route kwargs.
    For global resources, checks across all user projects.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if getattr(current_user, 'is_superadmin', False):
                return f(*args, **kwargs)

            if resource in GLOBAL_RESOURCES:
                if user_has_global_permission(current_user, resource, level):
                    return f(*args, **kwargs)
            else:
                project_id = _resolve_project_id(**kwargs)
                if project_id and user_has_permission(current_user, project_id, resource, level):
                    return f(*args, **kwargs)

            if request.is_json:
                return jsonify({'error': 'Insufficient permissions'}), 403
            flash('You do not have permission to access this resource.', 'danger')
            abort(403)
        return decorated_function
    return decorator


def superadmin_required(f):
    """Decorator: require superadmin status."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        if not getattr(current_user, 'is_superadmin', False):
            if request.is_json:
                return jsonify({'error': 'Superadmin access required'}), 403
            flash('Superadmin access required.', 'danger')
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def inject_permission_helpers(app):
    """Register the user_can context processor on the Flask app."""
    @app.context_processor
    def _inject():
        def user_can(resource, level, project_id=None):
            if not current_user.is_authenticated:
                return False
            if getattr(current_user, 'is_superadmin', False):
                return True
            if resource in GLOBAL_RESOURCES:
                return user_has_global_permission(current_user, resource, level)
            if project_id:
                return user_has_permission(current_user, project_id, resource, level)
            return False

        return {
            'user_can': user_can,
            'is_superadmin': getattr(current_user, 'is_superadmin', False) if current_user.is_authenticated else False,
        }
