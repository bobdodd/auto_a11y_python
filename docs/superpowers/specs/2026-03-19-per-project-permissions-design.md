# Per-Project/Website Permissions Design

## Problem

All authenticated users currently see all projects and websites. The only granular access control is share tokens for unauthenticated public access. We need per-project and per-website permission scoping so users only see and interact with resources they're assigned to.

## Requirements

1. Users are assigned roles (ADMIN, AUDITOR, CLIENT) per-project
2. Website-level role overrides are optional — default inherits from project
3. Global admins retain unrestricted access to all resources
4. Non-admin users only see projects they're assigned to
5. Project membership is managed by global admins and project-level admins
6. Existing projects are migrated by adding all current users with their global role

## Data Model

### ProjectMember (new dataclass)

Location: `auto_a11y/models/project_member.py`

```python
@dataclass
class ProjectMember:
    user_id: str      # AppUser._id as string
    role: UserRole    # ADMIN, AUDITOR, or CLIENT
```

**Naming note:** The codebase has existing `ProjectUser` and `WebsiteUser` models — those store *test credentials* for sites under test (login details for Playwright to use). `ProjectMember` is for *platform access control* — which users can see/manage a project.

### Project (modified)

Add `members: List[ProjectMember]` field (default empty list).

### Website (modified)

Add `members: List[ProjectMember]` field (default empty list). When empty, access inherits from the parent project. When populated, entries override the project-level role for that specific user.

### Role Resolution

For a user accessing a website:

1. If user is global admin → full access
2. If `website.members` has an entry for the user → use that role
3. Else if `project.members` has an entry for the user → use that role
4. Else → no access (403)

For a user accessing a project:

1. If user is global admin → full access
2. If `project.members` has an entry for the user → use that role
3. Else → no access (403)

For a user accessing a page (page-only routes like `/api/pages/<page_id>`):

1. Resolve `page.website_id` → `website.project_id`
2. Apply website/project role resolution as above

**Website overrides can both upgrade and downgrade access.** A project AUDITOR with a website CLIENT override cannot run tests on that specific website. This is intentional — it allows restricting access to sensitive websites within a project.

### MongoDB Indexes

Add indexes on both collections for membership queries:

```
projects: {"members.user_id": 1}
websites: {"members.user_id": 1}
```

These are needed because `get_projects_for_user` will be called on every project list page load for non-admin users.

## Permission Enforcement

### New Decorator: `@project_role_required(*roles)`

Location: `auto_a11y/web/routes/auth.py`

Extracts `project_id`, `website_id`, or `page_id` from route kwargs, resolves the user's effective role, and checks against the allowed roles. Caches the resolved role on `g.effective_role` to avoid duplicate DB lookups within the same request.

```python
def project_role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))

            # Global admins bypass
            if current_user.is_admin():
                g.effective_role = UserRole.ADMIN
                return f(*args, **kwargs)

            # Determine resource context
            project_id = kwargs.get('project_id')
            website_id = kwargs.get('website_id')
            page_id = kwargs.get('page_id')

            effective_role = get_effective_role(
                current_user, project_id, website_id, page_id
            )

            if effective_role not in roles:
                abort(403)

            g.effective_role = effective_role
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### Helper: `get_effective_role(user, project_id, website_id, page_id)`

Returns the user's effective `UserRole` on the given resource, applying the inheritance chain (website override → project → no access). Handles page → website → project resolution.

```python
def get_effective_role(user, project_id=None, website_id=None, page_id=None):
    """Return the user's effective role for the given resource context."""
    if user.is_admin():
        return UserRole.ADMIN

    # Resolve page to website
    if page_id and not website_id:
        page = db.get_page(page_id)
        if not page:
            return None
        website_id = page.website_id

    # Resolve website to project, check website override
    if website_id:
        website = db.get_website(website_id)
        if not website:
            return None
        # Check website-level override
        for member in getattr(website, 'members', []):
            if member.user_id == str(user.get_id()):
                return member.role
        # Fall through to project
        project_id = website.project_id

    if project_id:
        project = db.get_project(project_id)
        if not project:
            return None
        for member in getattr(project, 'members', []):
            if member.user_id == str(user.get_id()):
                return member.role

    return None  # No access
```

### `@project_admin_required` (for management routes)

For membership management routes on websites, authorization must check the *project-level* admin role, not the website-level override. A user who is project ADMIN but has a website AUDITOR override should still be able to manage website membership.

```python
def project_admin_required(f):
    """Requires project-level ADMIN (ignores website overrides)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        if current_user.is_admin():
            return f(*args, **kwargs)

        # For website routes, resolve to project
        project_id = kwargs.get('project_id')
        website_id = kwargs.get('website_id')
        if website_id and not project_id:
            website = db.get_website(website_id)
            if website:
                project_id = website.project_id

        if not project_id:
            abort(403)

        project = db.get_project(project_id)
        if not project:
            abort(404)

        user_id = str(current_user.get_id())
        for member in getattr(project, 'members', []):
            if member.user_id == user_id and member.role == UserRole.ADMIN:
                return f(*args, **kwargs)

        abort(403)
    return decorated_function
```

### Filtered Queries

**`db.get_projects_for_user(user_id)`**: Replaces `db.get_all_projects()` for non-admin users.

```python
def get_projects_for_user(self, user_id):
    """Return projects where user_id is a member."""
    return self.projects.find({"members.user_id": user_id})
```

Global admins continue to use `get_all_projects()`.

### New Database Methods (in `auto_a11y/core/database.py`)

- `get_projects_for_user(user_id)` — query projects by membership
- `add_project_member(project_id, user_id, role)` — add/upsert a member entry
- `remove_project_member(project_id, user_id)` — remove a member entry
- `update_project_member_role(project_id, user_id, role)` — change a member's role
- `add_website_member(website_id, user_id, role)` — add website override
- `remove_website_member(website_id, user_id)` — remove website override
- `update_website_member_role(website_id, user_id, role)` — change website override role

These use MongoDB `$push`, `$pull`, and positional `$set` on the embedded `members` array.

## Route Changes (Comprehensive)

### Project Routes (`projects_bp`)

| Route | Current | New |
|---|---|---|
| `GET /projects` (list) | `@login_required`, shows all | Filter by membership; admins see all |
| `GET /projects/create` | `@auditor_required` | `@auditor_required` (global) — stays the same |
| `POST /projects/create` | `@auditor_required` | `@auditor_required` (global); creator auto-added as project ADMIN |
| `GET /projects/<id>` (detail) | `@login_required` | `@project_role_required(ADMIN, AUDITOR, CLIENT)` |
| `GET /projects/<id>/report` | `@login_required` | `@project_role_required(ADMIN, AUDITOR, CLIENT)` |

### API Routes (`api_bp`)

| Route | Current | New |
|---|---|---|
| `GET /api/list` (projects) | `@login_required` | Filter by membership |
| `POST /api/projects` | `@login_required` | `@auditor_required` (global); creator auto-added as project ADMIN |
| `GET /api/projects/<id>` | `@login_required` | `@project_role_required(ADMIN, AUDITOR, CLIENT)` |
| `PUT /api/projects/<id>` | `@login_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `DELETE /api/projects/<id>` | `@login_required` | `@project_role_required(ADMIN)` |
| `POST /api/projects/<id>/websites` | `@login_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `GET /api/websites/<id>` | `@login_required` | Resolve to project, `@project_role_required(ADMIN, AUDITOR, CLIENT)` |
| `PUT /api/websites/<id>` | `@login_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `DELETE /api/websites/<id>` | `@login_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `GET /api/pages/<id>` | `@login_required` | Resolve page → website → project |
| `POST /api/pages/<id>/test` | `@login_required` | `@project_role_required(ADMIN, AUDITOR)` (via page resolution) |
| `GET /api/pages/<id>/test-results` | `@login_required` | `@project_role_required(ADMIN, AUDITOR, CLIENT)` (via page resolution) |
| `GET /api/projects/<id>/reports/*` | `@login_required` | `@project_role_required(ADMIN, AUDITOR, CLIENT)` — all roles can download |

### Testing Routes (`testing_bp`)

| Route | Current | New |
|---|---|---|
| `GET /testing/dashboard` | `@login_required` | `@login_required` — filters data to user's projects |
| `GET /testing/api/stats` | `@login_required` | Filter aggregate stats to user's projects |
| `GET /testing/api/trends` | `@login_required` | Filter trends to user's projects |
| `POST /testing/api/run-tests` | `@login_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `GET /testing/fixture-status` | `@login_required` | No change — system-level |

### Schedule Routes (`schedules_bp`)

| Route | Current | New |
|---|---|---|
| `POST /websites/<id>/schedules/create` | `@login_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `PUT /websites/<id>/schedules/<sid>/edit` | `@login_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `DELETE /websites/<id>/schedules/<sid>/delete` | `@login_required` | `@project_role_required(ADMIN, AUDITOR)` |

### Share Token Routes (`share_tokens_bp`)

| Route | Current | New |
|---|---|---|
| `POST /projects/<id>/share-tokens` | `@auditor_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `POST /websites/<id>/share-tokens` | `@auditor_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `GET /projects/<id>/share-tokens` | `@auditor_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `GET /websites/<id>/share-tokens` | `@auditor_required` | `@project_role_required(ADMIN, AUDITOR)` |
| `POST /share-tokens/<id>/revoke` | `@auditor_required` | Look up token → resolve scope_id to project_id (for both project and website tokens) → check project membership ADMIN or AUDITOR |

### Public/Client Routes (`public_bp`)

| Route | Current | New |
|---|---|---|
| `GET /client/projects/` | `@require_access`, shows all | Filter by membership for logged-in users |
| `GET /client/project/<id>/` | `@require_access` | Check membership for logged-in users (403 if no membership); token access unchanged |
| `GET /client/project/<id>/w/<wid>/` | `@require_access` | Check membership (403 if no membership); token access unchanged |
| `GET /public/t/<token>/` | `@require_access` | No change — token-based, no membership check |

### Membership Management Routes (new, `members_bp`)

| Route | Required Role |
|---|---|
| `GET /projects/<id>/members` | `@project_role_required(ADMIN)` |
| `POST /projects/<id>/members` | `@project_admin_required` |
| `PUT /projects/<id>/members/<uid>` | `@project_admin_required` |
| `DELETE /projects/<id>/members/<uid>` | `@project_admin_required` |
| `GET /websites/<id>/members` | `@project_admin_required` |
| `POST /websites/<id>/members` | `@project_admin_required` |
| `PUT /websites/<id>/members/<uid>` | `@project_admin_required` |
| `DELETE /websites/<id>/members/<uid>` | `@project_admin_required` |

### Unchanged Routes

| Route Area | Reason |
|---|---|
| User management (`@admin_required`) | Global admin only — not project-scoped |
| Fixture testing | System-level — not project-scoped |
| Auth routes (login/logout/SSO) | Authentication, not authorization |
| Drupal integration | Out of scope for this change — currently admin-only configuration |

## Membership Management

### Routes (new)

- `GET /projects/<project_id>/members` — List members (project admin or global admin)
- `POST /projects/<project_id>/members` — Add member (project admin or global admin)
- `PUT /projects/<project_id>/members/<user_id>` — Change role (project admin or global admin)
- `DELETE /projects/<project_id>/members/<user_id>` — Remove member (project admin or global admin)
- `GET /websites/<website_id>/members` — List website-level overrides
- `POST /websites/<website_id>/members` — Add website override
- `PUT /websites/<website_id>/members/<user_id>` — Change website override role
- `DELETE /websites/<website_id>/members/<user_id>` — Remove website override (reverts to project role)

### UI

Project settings page gets a "Members" tab/section:
- Table of current members with role dropdowns
- "Add member" form (select existing user + role)
- Remove button per member
- Project admins cannot remove themselves or demote themselves (prevents lockout)

Website detail page gets an optional "Access Overrides" section:
- Shows inherited project role by default
- Option to add a website-level override for specific users

## Migration

A standalone migration script (`migrate_add_project_members.py`) run once manually:

1. Checks if migration already ran (looks for a `_migrations` collection entry)
2. Fetches all AppUsers (including admins)
3. Fetches all existing projects
4. For each project, adds all users as members with their current global role
5. Creates indexes on `projects.members.user_id` and `websites.members.user_id`
6. Records migration as complete in `_migrations` collection
7. Logs what was done

All users including admins are added as members. This ensures that if a user is later demoted from global admin, they retain project access through their membership entries.

**Pre-migration projects** (empty `members` list) are treated as "no one has access except global admins." The migration must be run before deploying the permission-enforced code. The app startup should log a warning if any projects have empty members lists.

This preserves current access patterns. After migration, admins can prune membership as needed.

## Share Token Interaction

No changes needed. Share tokens provide unauthenticated public access scoped to project/website. Project membership controls authenticated user access. These are independent systems that coexist.

## Edge Cases

- **User creates a project**: Creator is auto-added as project ADMIN member
- **User's global role changes**: Does NOT affect project memberships (they're independent). However, demoting a global admin means they'll fall back to their project membership roles.
- **User is deleted**: Their membership entries should be cleaned up (or ignored — member entry with nonexistent user_id is harmless)
- **Project admin removes all admins**: Prevented — at least one project admin must remain (or global admins can fix it)
- **SSO new user**: Created with CLIENT global role, no project memberships until assigned
- **Page-only routes**: Resolved via `page.website_id` → `website.project_id` chain
- **Website override downgrades**: Intentional — project AUDITOR with website CLIENT override cannot run tests on that website
- **Global auditor creates project**: Becomes project ADMIN on that project; has no access to other projects unless explicitly added
- **Decorator on route with no resource context**: If `project_id`, `website_id`, and `page_id` are all absent, `get_effective_role` returns `None` → 403 for non-admins. This is intentional — the decorator should only be used on routes that have resource context.
