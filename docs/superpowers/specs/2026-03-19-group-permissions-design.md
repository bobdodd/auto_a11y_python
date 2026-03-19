# Group-Based Permissions System

## Overview

Replace the hardcoded role system (ADMIN/AUDITOR/CLIENT) with a flexible group-based permission system. Groups contain permissions defined as hierarchical CRUD levels per resource. Users are assigned groups per-project, and a union/additive model means if any group grants a permission, the user has it.

## Data Model

### Groups Collection (`groups`)

```
{
  _id: ObjectId,
  name: str,                    # e.g., "Auditor", "Client", "QA Lead"
  description: str,
  permissions: {
    "projects": "delete",       # Permission level per resource
    "websites": "create",
    "pages": "read",
    ...
  },
  is_system: bool,              # True for default groups — can't be deleted
  created_at: datetime,
  updated_at: datetime
}
```

### Permission Levels (Hierarchical)

```
none < read < update < create < delete
```

Each level includes all lower levels. A user with `create` on a resource can also `update` and `read` it.

### Resource Nouns

**Project-scoped** (permission checked against the relevant project):

| Resource | Description | Scope resolution |
|----------|-------------|------------------|
| `projects` | Project CRUD | Direct from route |
| `websites` | Website CRUD within projects | website -> project |
| `pages` | Page CRUD (includes discovered pages) | page -> website -> project |
| `test_results` | Run tests (`create`) / view results (`read`). `update` and `delete` are not meaningful. | page -> website -> project |
| `reports` | Generate (`create`) / view / download reports | project from route or page chain |
| `project_members` | Manage who's in a project and their groups | Direct from route |
| `project_users` | Test credential management (project-level and website-level) | Direct from route or website -> project |
| `share_tokens` | Public sharing tokens | Resolved from token's scope |
| `scheduled_tests` | Scheduled test management | project from route |
| `recordings` | Manual audit recordings | recording -> project |
| `project_participants` | Lived experience testers and supervisors | Direct from route |
| `scripts` | Page setup scripts for pre-test automation | page -> website -> project |
| `ai_analysis` | AI-powered analysis (costs money per request) | page -> website -> project |

**Global** (permission checked across **any** project the user belongs to):

| Resource | Description | Notes |
|----------|-------------|-------|
| `users` | Platform user management | Query all user's projects, take max |
| `groups` | Group definition management | Query all user's projects, take max |
| `fixture_tests` | Fixture test running/viewing (dev tool) | Query all user's projects, take max |

For global resources, the system queries all projects the user is a member of and takes the maximum permission level across all of them. To optimize this, a denormalized `max_global_permissions` dict can be cached on the user session and invalidated when group assignments change.

### Project Membership Changes

`Project.members` changes from:

```python
# Old
{"user_id": str, "role": "ADMIN"}

# New
{"user_id": str, "group_ids": [ObjectId, ...]}
```

### Superadmin Flag

A boolean `is_superadmin` field on `AppUser` (default: `False`). Bypasses all permission checks entirely. Not a group — just a flag, since it's not per-project and has no configurable permissions.

`AppUser.from_dict()` must handle documents that lack `is_superadmin` by defaulting to `False` for backward compatibility during rollout.

## Permission Resolution

```python
def user_has_permission(user, project_id, resource, required_level):
    if user.is_superadmin:
        return True

    project = db.get_project(project_id)
    member = find_member(project, user.id)
    if not member:
        return False

    groups = db.get_groups_by_ids(member.group_ids)
    if not groups:
        return False

    LEVELS = {'none': 0, 'read': 1, 'update': 2, 'create': 3, 'delete': 4}
    max_level = max(
        (LEVELS.get(g.permissions.get(resource, 'none'), 0) for g in groups),
        default=0
    )

    return max_level >= LEVELS[required_level]
```

**Global resources** (users, groups, fixture_tests) are not project-scoped. For these, the system queries all projects the user belongs to and takes the maximum permission level across all of them.

A missing key in a group's `permissions` dict is treated as `none`.

## Default Groups

Seeded on first run with `is_system: true`:

| Group | Permissions |
|-------|-------------|
| **Admin** | All resources at `delete` level |
| **Auditor** | projects: `create`, websites/pages/test_results/reports: `delete`, project_members: `read`, project_users/scheduled_tests/ai_analysis/recordings/project_participants/scripts: `delete`, users/groups/share_tokens: `read`, fixture_tests: `read` |
| **Client** | projects/websites/pages/test_results/reports: `read`, all others: `none` |

## Decorator Replacement

Existing decorators (`@admin_required`, `@auditor_required`, `@project_role_required`) are replaced with:

```python
@permission_required('test_results', 'create')
def run_test(project_id):
    ...

@permission_required('users', 'update')
def edit_user(user_id):
    ...
```

The decorator extracts `project_id` from the route and calls `user_has_permission`. Resolution chain for finding the project:

1. Direct: `project_id` in route kwargs
2. Via website: `website_id` -> lookup website -> `project_id`
3. Via page: `page_id` -> lookup page -> `website_id` -> `project_id`
4. Via recording: `recording_id` -> lookup recording -> `project_id`
5. Via token: `token_id` -> lookup token -> scope -> `project_id`
6. Via form data: some POST routes pass project context in the request body

For global resources (users, groups, fixture_tests), the decorator does not need a project_id — it queries across all the user's projects.

**Auto-membership on project creation:** When a user creates a project, they are automatically added as a member with the Admin group. This ensures the creator can manage their own project.

## UI Interfaces

### 1. Group Management (`/groups`)

- Accessible to users with `groups: read`+ permission
- **List view**: Table of all groups with name, description, system badge, member count
- **Create/Edit**: Form with group name, description, and a table of resource nouns — each row has a dropdown (None/Read/Update/Create/Delete)
- System groups can be edited but not deleted

### 2. Project Members (modify existing `/projects/<id>/members`)

- Change from single role assignment to one or more groups via checkboxes
- Add member flow: search user, then select groups
- Edit member: modify group checkboxes
- Show effective permissions as a read-only summary (computed union)

### 3. User Edit (modify existing `/auth/users/<id>/edit`)

- Add section showing which projects the user belongs to and what groups they have in each
- Superadmin toggle (visible to other superadmins only)
- Read-only overview — actual group assignment happens on the project members page

## Migration Strategy

One-time idempotent migration on app startup:

1. **Seed default groups** — Create Admin, Auditor, Client groups in `groups` collection if they don't exist

2. **Migrate AppUser roles to superadmin flag**:
   - `role: ADMIN` -> `is_superadmin = True`
   - All others -> `is_superadmin = False`

3. **Migrate ProjectMember roles to group assignments**:
   - `role: ADMIN` -> Admin group
   - `role: AUDITOR` -> Auditor group
   - `role: CLIENT` -> Client group
   - Replace `role` field with `group_ids` list

4. **Keep `role` field on AppUser** — stop using it for authorization but don't delete it

5. **Drop website-level member overrides** — stop checking `Website.members`. Leave the field as dead data in existing documents; do not `$unset` it (safe for rollback). Remove the override logic from permission resolution code.

6. **Update registration and SSO flows** — new users get `is_superadmin = False`. SSO-created users (`find_or_create_sso_user`) get `is_superadmin = False`. New users have no project memberships by default (same as today — they must be added to projects).

Migration adds new fields/collections without destroying old data for rollback safety.

## Edge Cases

- **Empty `group_ids`**: If a project member has an empty `group_ids` list, they have no permissions (effectively no access). The `max()` call uses `default=0`.
- **Stale group references**: If a non-system group is deleted, its ObjectId may remain in members' `group_ids` lists. `get_groups_by_ids` returns only groups that still exist — stale IDs are silently ignored. A cleanup job or deletion hook can remove stale references.
- **System group editing**: System groups can be edited (permissions changed) but not deleted. No guardrail prevents neutering the Admin system group — this is intentional, as superadmin users bypass group checks entirely.
- **Missing permission keys**: A missing key in a group's `permissions` dict is treated as `none`. This means newly added resource nouns are automatically denied until explicitly granted, which is the safe default.

## Template Permission Checks

Templates currently use `current_user.is_admin()`, `current_user.can_create_projects()`, etc. to show/hide UI elements. These are replaced with a Jinja2 context processor that injects a `user_can(resource, level, project_id=None)` function:

```python
@app.context_processor
def inject_permissions():
    def user_can(resource, level, project_id=None):
        if not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, project_id, resource, level)
    return {'user_can': user_can}
```

This allows templates to write `{% if user_can('test_results', 'create', project.id) %}` to conditionally render elements.
