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
from auto_a11y.models.app_user import UserRole
from auto_a11y.reporting.issue_descriptions_translated import get_detailed_issue_description
from auto_a11y.web.routes.auth import require_access, check_scope, get_effective_role

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
    # For logged-in users (no token), filter by membership
    if g.access_scope is None and current_user.is_authenticated:
        if getattr(current_user, 'is_superadmin', False):
            projects = current_app.db.get_all_projects()
        else:
            projects = current_app.db.get_projects_for_user(str(current_user.get_id()))
    else:
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
    if g.access_scope is None and current_user.is_authenticated and not getattr(current_user, 'is_superadmin', False):
        role = get_effective_role(current_user, request, project_id=project_id)
        if role is None:
            abort(403)
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
    if g.access_scope is None and current_user.is_authenticated and not getattr(current_user, 'is_superadmin', False):
        role = get_effective_role(current_user, request, project_id=project_id)
        if role is None:
            abort(403)
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
