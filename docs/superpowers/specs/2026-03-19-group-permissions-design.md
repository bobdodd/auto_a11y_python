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

| Resource | Description |
|----------|-------------|
| `projects` | Project CRUD |
| `websites` | Website CRUD within projects |
| `pages` | Page CRUD within websites |
| `test_results` | Run tests / view results |
| `reports` | Generate / view / download reports |
| `users` | Platform user management |
| `groups` | Group definition management |
| `project_members` | Manage who's in a project and their groups |
| `project_users` | Test credential management |
| `share_tokens` | Public sharing tokens |
| `scheduled_tests` | Scheduled test management |
| `fixture_tests` | Fixture test running/viewing |
| `ai_analysis` | AI-powered analysis |

### Project Membership Changes

`Project.members` changes from:

```python
# Old
{"user_id": str, "role": "ADMIN"}

# New
{"user_id": str, "group_ids": [ObjectId, ...]}
```

### Superadmin Flag

A boolean `is_superadmin` field on `AppUser`. Bypasses all permission checks entirely. Not a group — just a flag, since it's not per-project and has no configurable permissions.

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

    LEVELS = {'none': 0, 'read': 1, 'update': 2, 'create': 3, 'delete': 4}
    max_level = max(
        LEVELS.get(g.permissions.get(resource, 'none'), 0)
        for g in groups
    )

    return max_level >= LEVELS[required_level]
```

For non-project-scoped resources (users, groups, fixture_tests): check if the user has the required permission in **any** of their projects.

## Default Groups

Seeded on first run with `is_system: true`:

| Group | Permissions |
|-------|-------------|
| **Admin** | All resources at `delete` level |
| **Auditor** | projects: `create`, websites/pages/test_results/reports: `delete`, project_users/scheduled_tests/ai_analysis: `delete`, users/groups/share_tokens: `read`, fixture_tests: `read` |
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

The decorator extracts `project_id` from the route (resolving page -> website -> project hierarchy as today) and calls `user_has_permission`.

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

5. **Drop website-level member overrides** — stop checking `Website.members`

Migration adds new fields/collections without destroying old data for rollback safety.
