# Role-Based Access Control (RBAC) Design Spec

## Overview

Implement fine-grained, per-resource role-based access control for Auto A11y Python. Users are assigned named roles on specific projects, websites, and pages. Admins retain full system-wide access. Permissions cascade down the resource hierarchy (project → website → page) with per-resource overrides.

## Goals

1. Per-project, per-website, and per-page access control with named roles
2. Admin role bypasses RBAC (full read/write to everything)
3. Hierarchical permission inheritance with override capability
4. Clean migration path preserving existing user access
5. Management UI for assigning permissions

## Non-Goals

- Multi-tenancy / workspace isolation
- API key authentication (existing share tokens remain separate)
- Custom permission strings beyond read/write/manage

---

## Data Model

### `roles` Collection

Defines available roles and their permission sets. Ships with system defaults; admins can create custom roles.

```json
{
  "_id": "ObjectId",
  "name": "editor",
  "display_name": "Editor",
  "permissions": ["read", "write"],
  "is_system": true,
  "description": "Can view and edit projects, run tests",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**System roles (seeded on first run):**

| Name | Permissions | Description |
|------|-------------|-------------|
| `viewer` | `read` | View projects, reports, test results |
| `editor` | `read`, `write` | + Run tests, edit settings, manage pages/websites |
| `manager` | `read`, `write`, `manage` | + Assign roles to other users on the resource |

**Constraints:**
- `name` is unique
- System roles (`is_system: true`) cannot be deleted
- Permission values come from the set: `read`, `write`, `manage`
- Permissions are hierarchical: `manage` implies `write` implies `read`

### `role_assignments` Collection

Assigns a user to a role on a specific resource.

```json
{
  "_id": "ObjectId",
  "user_id": "string (AppUser ID)",
  "role_id": "ObjectId (reference to roles)",
  "resource_type": "string (project | website | page)",
  "resource_id": "string (ObjectId of the resource)",
  "assigned_by": "string (AppUser ID)",
  "created_at": "datetime"
}
```

**Indexes:**
- `(user_id, resource_type, resource_id)` — unique compound index (one role per user per resource)
- `(resource_type, resource_id)` — list all users with access to a resource
- `(user_id)` — list all resources a user can access

### Changes to `app_users`

The existing `role` field (admin/auditor/client) becomes a **global system role** only:

- **admin** — bypasses all RBAC checks, full access to everything, can manage users and system config
- **auditor** — no longer gates project access; resource access determined by RBAC assignments only
- **client** — no longer gates project access; resource access determined by RBAC assignments only

Global role only governs:
- User management (admin only)
- System configuration (admin only)
- Project creation (any authenticated user — see below)

Methods like `can_create_projects()`, `can_run_tests()`, `can_view_reports()` will be updated to check RBAC context instead of global role (except `can_manage_users()` which stays admin-only).

---

## Authorization Logic

### Core Permission Check

New module: `auto_a11y/core/authorization.py`

```python
def check_permission(user, resource_type, resource_id, required_permission):
    """
    Returns True if user has the required permission on the resource.

    Algorithm:
    1. If user.is_admin() → True (bypass all checks)
    2. Look up role_assignment for (user_id, resource_type, resource_id)
    3. If found → resolve role → check if role's permissions include required_permission
    4. If not found → walk up hierarchy:
       - page → look up parent website assignment
       - website → look up parent project assignment
       - project → deny (no parent)
    5. Return True if permission found at any level, False otherwise
    """
```

**Hierarchy walk with override:**

Example: User has `editor` on Project A → inherited `write` on all websites/pages. If user also has `viewer` explicitly on Website B within Project A, the explicit website-level assignment takes precedence. Result: `read`-only on Website B, `write` on everything else in Project A.

Rule: the **most specific** assignment wins. If no assignment exists at the current level, inherit from parent.

### Route Decorator

```python
@require_permission(resource_type, permission)
```

Usage:

```python
@app.route('/projects/<project_id>/test')
@login_required
@require_permission('project', 'write')
def run_test(project_id):
    ...
```

Behavior:
1. Extracts `resource_id` from URL kwargs based on `resource_type`
2. Calls `check_permission(current_user, resource_type, resource_id, permission)`
3. Returns 403 with error message if denied
4. For AJAX/API requests, returns JSON `{"error": "Access denied"}` with 403 status

### Caching Strategy

- **Per-request cache:** Store resolved permissions in Flask's `g` object to avoid duplicate DB queries within a single request
- **No long-lived cache initially** — avoid cache invalidation complexity; add later if performance requires it

### Decorator Migration

| Current Decorator | New Decorator | Notes |
|-------------------|---------------|-------|
| `@admin_required` | Keep as-is | System admin actions (user mgmt, system config) |
| `@auditor_required` | `@require_permission('project', 'write')` | Project-scoped write actions |
| `@login_required` (on project views) | `@login_required` + `@require_permission('project', 'read')` | Project-scoped read actions |
| `before_request` global login check | Keep as-is | Still requires authentication for all non-public routes |

---

## Admin UI

### Project Permissions Page

**Route:** `/projects/<project_id>/permissions`

**Access:** Admins + users with `manage` permission on the project

**Content:**
- Table of all users with access: user email/name, assigned role, assigned by, date
- "Add User" form: user selector + role dropdown
- "Remove" button per row to revoke access
- Section showing websites/pages with explicit overrides within this project

### Website Permissions Page

**Route:** `/projects/<project_id>/websites/<website_id>/permissions`

**Access:** Admins + users with `manage` on the website or parent project

**Content:**
- Same table pattern as project permissions
- Shows inherited role from project with label "(inherited from project)"
- "Override" action to set a different role at website level
- "Reset to inherited" action to remove website-level override

### Page Permissions Page

**Route:** `/projects/<project_id>/websites/<website_id>/pages/<page_id>/permissions`

Same pattern. Expected to be rarely used but available for restricting specific pages.

### User Profile — Resource Access Section

On `/auth/users/<user_id>/edit` (admin view), add a "Resource Access" section:
- List all projects/websites/pages the user has access to, with role and source (direct or inherited)
- Admins can add/remove assignments from this view

### Project Listing Changes

**`/projects` route:**
- Non-admin users: only see projects they have at least `read` permission on
- Admin users: see all projects
- Visual badge per project showing the user's role (Viewer / Editor / Manager)

**Project creation:**
- Any authenticated user can create a project
- Creator automatically receives `manager` role on the new project

---

## Migration Strategy

### One-Time Data Migration

Run automatically on application startup if `roles` collection is empty:

1. **Seed system roles:** Create `viewer`, `editor`, `manager` in `roles` collection with `is_system: true`
2. **Migrate existing users:**
   - `admin` users → no assignments needed (admin bypasses RBAC)
   - `auditor` users → `editor` role assignment on ALL existing projects
   - `client` users → `viewer` role assignment on ALL existing projects
3. **Log migration results** to application log

This preserves existing access: auditors keep write access to all projects, clients keep read access.

### New User Defaults

- Created via admin panel: admin selects projects and roles during creation
- Created via SSO first login: no project access (empty dashboard), admin assigns later
- Users who create a project: automatically get `manager` on that project

### Share Token Compatibility

Share tokens remain unchanged. They are a separate access mechanism for unauthenticated public access and are not affected by RBAC. The `require_access` decorator continues to handle dual auth (token OR authenticated user with RBAC check).

---

## Affected Files

### New Files
- `auto_a11y/core/authorization.py` — permission check logic, decorator
- `auto_a11y/models/role.py` — Role model
- `auto_a11y/models/role_assignment.py` — RoleAssignment model
- `auto_a11y/web/templates/permissions/` — permission management templates
- `auto_a11y/scripts/migrate_rbac.py` — migration script (or integrated into startup)

### Modified Files
- `auto_a11y/models/app_user.py` — update permission methods to be RBAC-aware
- `auto_a11y/core/database.py` — add CRUD for roles and role_assignments collections
- `auto_a11y/web/routes/auth.py` — update decorators, add permission management routes
- `auto_a11y/web/routes/projects.py` — filter project listing, add permission pages
- `auto_a11y/web/routes/websites.py` — add permission checks and pages
- `auto_a11y/web/routes/pages.py` — add permission checks
- `auto_a11y/web/routes/testing.py` — replace `@auditor_required` with RBAC checks
- `auto_a11y/web/app.py` — seed roles on startup, register new routes
- `auto_a11y/web/templates/` — various templates for permission badges, management UI
- `config.py` — (minimal, no new config needed)

---

## Error Handling

- **403 Forbidden:** Returned when a user lacks the required permission. HTML response for browser requests, JSON for API/AJAX.
- **Orphaned assignments:** If a project/website/page is deleted, its role_assignments should be cleaned up (cascade delete).
- **Missing role reference:** If a role is deleted but role_assignments reference it, treat as no-permission (deny access) and log a warning.

---

## Testing Strategy

- Unit tests for `check_permission()` covering: admin bypass, direct assignment, hierarchy inheritance, override, no-access denial
- Integration tests for the decorator on sample routes
- Migration tests: verify existing auditor/client users retain correct access after migration
- UI tests: verify permission management pages render and function correctly
