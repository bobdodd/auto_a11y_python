# Group-Based Permissions Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hardcoded ADMIN/AUDITOR/CLIENT role system with a flexible group-based permission system where groups have hierarchical CRUD levels per resource noun, are assigned per-project, and use a union/additive model.

**Architecture:** New `PermissionGroup` model stored in a `groups` MongoDB collection. `ProjectMember.role` replaced with `group_ids` list. `AppUser` gains `is_superadmin` flag. A central `user_has_permission(user, project_id, resource, level)` function powers a new `@permission_required` decorator that replaces all existing role decorators. A Jinja2 `user_can()` context processor handles template-side checks.

**Tech Stack:** Python/Flask, MongoDB, Bootstrap 5, Jinja2

**Spec:** `docs/superpowers/specs/2026-03-19-group-permissions-design.md`

---

## File Structure

### New Files
- `auto_a11y/models/permission_group.py` — PermissionGroup dataclass, RESOURCE_NOUNS constant, PERMISSION_LEVELS constant, default group definitions
- `auto_a11y/core/permissions.py` — `user_has_permission()`, `user_has_global_permission()`, `get_user_effective_permissions()`, `permission_required` decorator, `user_can` context processor
- `auto_a11y/web/routes/groups.py` — Group management CRUD routes (Blueprint)
- `auto_a11y/web/templates/groups/list.html` — Group list page
- `auto_a11y/web/templates/groups/edit.html` — Group create/edit form
- `auto_a11y/core/migrate_groups.py` — One-time migration: seed groups, migrate roles to group_ids, set is_superadmin

### Modified Files
- `auto_a11y/models/app_user.py` — Add `is_superadmin` field, update `to_dict`/`from_dict`
- `auto_a11y/models/project_member.py` — Replace `role: UserRole` with `group_ids: list`
- `auto_a11y/core/database.py` — Add group CRUD methods, update member methods to use group_ids
- `auto_a11y/web/routes/auth.py` — Replace old decorators with `permission_required`, update user management routes
- `auto_a11y/web/routes/members.py` — Replace role-based logic with group-based logic, remove website member routes
- `auto_a11y/web/routes/projects.py` — Replace decorator imports, add auto-membership on create
- `auto_a11y/web/routes/testing.py` — Replace inline `is_admin()` checks
- `auto_a11y/web/routes/share_tokens.py` — Replace inline `is_admin()` check
- `auto_a11y/web/routes/api.py` — Replace inline `is_admin()` check
- `auto_a11y/web/routes/public.py` — Replace `is_admin()` checks with `is_superadmin`
- `auto_a11y/web/app.py` — Register groups blueprint, add `user_can` context processor, update `is_admin()` refs, register migration
- `auto_a11y/web/templates/base.html` — Replace `is_admin()` checks with `user_can()`
- `auto_a11y/web/templates/auth/user_edit.html` — Add superadmin toggle, project membership overview
- `auto_a11y/web/templates/auth/user_list.html` — Show superadmin badge instead of role
- `auto_a11y/web/templates/projects/view.html` — Update members section to use groups

---

## Task 1: PermissionGroup Model

**Files:**
- Create: `auto_a11y/models/permission_group.py`
- Modify: `auto_a11y/models/__init__.py`

- [ ] **Step 1: Create the PermissionGroup model**

```python
# auto_a11y/models/permission_group.py
"""Permission group model for group-based access control."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict
from bson import ObjectId


PERMISSION_LEVELS = {
    'none': 0,
    'read': 1,
    'update': 2,
    'create': 3,
    'delete': 4,
}

LEVEL_NAMES = {v: k for k, v in PERMISSION_LEVELS.items()}

RESOURCE_NOUNS = [
    'projects',
    'websites',
    'pages',
    'test_results',
    'reports',
    'project_members',
    'project_users',
    'share_tokens',
    'scheduled_tests',
    'recordings',
    'project_participants',
    'scripts',
    'ai_analysis',
    'users',
    'groups',
    'fixture_tests',
]

GLOBAL_RESOURCES = {'users', 'groups', 'fixture_tests'}

PROJECT_SCOPED_RESOURCES = set(RESOURCE_NOUNS) - GLOBAL_RESOURCES


def _all_delete():
    return {r: 'delete' for r in RESOURCE_NOUNS}


def _all_none():
    return {r: 'none' for r in RESOURCE_NOUNS}


DEFAULT_GROUPS = {
    'Admin': {
        'description': 'Full access to all resources',
        'permissions': _all_delete(),
    },
    'Auditor': {
        'description': 'Can create projects, run tests, manage test config',
        'permissions': {
            **_all_none(),
            'projects': 'create',
            'websites': 'delete',
            'pages': 'delete',
            'test_results': 'delete',
            'reports': 'delete',
            'project_members': 'read',
            'project_users': 'delete',
            'scheduled_tests': 'delete',
            'recordings': 'delete',
            'project_participants': 'delete',
            'scripts': 'delete',
            'ai_analysis': 'delete',
            'users': 'read',
            'groups': 'read',
            'share_tokens': 'read',
            'fixture_tests': 'read',
        },
    },
    'Client': {
        'description': 'Read-only access to projects and reports',
        'permissions': {
            **_all_none(),
            'projects': 'read',
            'websites': 'read',
            'pages': 'read',
            'test_results': 'read',
            'reports': 'read',
        },
    },
}


@dataclass
class PermissionGroup:
    """A named group with per-resource permission levels."""
    name: str
    description: str = ''
    permissions: Dict[str, str] = field(default_factory=_all_none)
    is_system: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    _id: Optional[ObjectId] = None

    @property
    def id(self) -> Optional[str]:
        return str(self._id) if self._id else None

    def get_level(self, resource: str) -> int:
        """Return numeric permission level for a resource."""
        return PERMISSION_LEVELS.get(self.permissions.get(resource, 'none'), 0)

    def has_permission(self, resource: str, required_level: str) -> bool:
        """Check if this group grants at least the required level on resource."""
        return self.get_level(resource) >= PERMISSION_LEVELS.get(required_level, 0)

    def to_dict(self) -> dict:
        data = {
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'is_system': self.is_system,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'PermissionGroup':
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            permissions=data.get('permissions', {}),
            is_system=data.get('is_system', False),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            _id=data.get('_id'),
        )
```

- [ ] **Step 2: Export from models/__init__.py**

Add `PermissionGroup` to the imports in `auto_a11y/models/__init__.py`.

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/models/permission_group.py auto_a11y/models/__init__.py
git commit -m "feat: add PermissionGroup model with resource nouns and defaults"
```

---

## Task 2: Update AppUser Model

**Files:**
- Modify: `auto_a11y/models/app_user.py:20-43` (dataclass fields), `:133-153` (to_dict), `:155-178` (from_dict)

- [ ] **Step 1: Add `is_superadmin` field to AppUser dataclass**

After line 38 (`sso_id`), add:

```python
    is_superadmin: bool = False
```

- [ ] **Step 2: Update `to_dict` to include `is_superadmin`**

In the `to_dict` method, add `'is_superadmin': self.is_superadmin` to the dict.

- [ ] **Step 3: Update `from_dict` to read `is_superadmin`**

In the `from_dict` method, add `is_superadmin=data.get('is_superadmin', False)` to the constructor call.

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/models/app_user.py
git commit -m "feat: add is_superadmin field to AppUser"
```

---

## Task 3: Update ProjectMember Model

**Files:**
- Modify: `auto_a11y/models/project_member.py`

- [ ] **Step 1: Replace `role` with `group_ids`**

Replace the entire file content:

```python
"""Project membership for per-resource access control.

Note: This is distinct from ProjectUser/WebsiteUser which store test
credentials for sites under test. ProjectMember controls which platform
users can see/manage a project.
"""
from dataclasses import dataclass, field
from typing import List
from bson import ObjectId


@dataclass
class ProjectMember:
    """A user's group memberships on a specific project."""
    user_id: str          # AppUser._id as string
    group_ids: List[str] = field(default_factory=list)  # PermissionGroup._id as strings

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "group_ids": [str(gid) for gid in self.group_ids],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectMember":
        # Handle old format with 'role' field (pre-migration)
        if 'role' in data and 'group_ids' not in data:
            return cls(user_id=data["user_id"], group_ids=[])
        return cls(
            user_id=data["user_id"],
            group_ids=[str(gid) for gid in data.get("group_ids", [])],
        )
```

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/models/project_member.py
git commit -m "feat: replace ProjectMember.role with group_ids list"
```

---

## Task 4: Database Layer — Group CRUD

**Files:**
- Modify: `auto_a11y/core/database.py`

- [ ] **Step 1: Add `groups` collection initialization**

In the `__init__` method of the Database class (where other collections are initialized), add:

```python
self.groups = self.db['groups']
```

- [ ] **Step 2: Add group CRUD methods**

Add these methods to the Database class (near the app_user methods section):

```python
    # ---- Permission Group operations ----

    def create_group(self, group) -> str:
        """Create a permission group. Returns inserted ID as string."""
        result = self.groups.insert_one(group.to_dict())
        return str(result.inserted_id)

    def get_group(self, group_id: str):
        """Get a single group by ID."""
        from auto_a11y.models.permission_group import PermissionGroup
        doc = self.groups.find_one({"_id": ObjectId(group_id)})
        return PermissionGroup.from_dict(doc) if doc else None

    def get_group_by_name(self, name: str):
        """Get a group by its name."""
        from auto_a11y.models.permission_group import PermissionGroup
        doc = self.groups.find_one({"name": name})
        return PermissionGroup.from_dict(doc) if doc else None

    def get_all_groups(self):
        """Get all permission groups."""
        from auto_a11y.models.permission_group import PermissionGroup
        return [PermissionGroup.from_dict(doc) for doc in self.groups.find()]

    def get_groups_by_ids(self, group_ids):
        """Get multiple groups by their IDs. Silently skips missing IDs."""
        from auto_a11y.models.permission_group import PermissionGroup
        if not group_ids:
            return []
        oids = []
        for gid in group_ids:
            try:
                oids.append(ObjectId(gid))
            except Exception:
                continue
        docs = self.groups.find({"_id": {"$in": oids}})
        return [PermissionGroup.from_dict(doc) for doc in docs]

    def update_group(self, group) -> bool:
        """Update an existing group."""
        from datetime import datetime
        group.updated_at = datetime.now()
        result = self.groups.replace_one(
            {"_id": group._id},
            group.to_dict()
        )
        return result.modified_count > 0

    def delete_group(self, group_id: str) -> bool:
        """Delete a non-system group."""
        result = self.groups.delete_one({
            "_id": ObjectId(group_id),
            "is_system": {"$ne": True}
        })
        return result.deleted_count > 0

    def count_group_members(self, group_id: str) -> int:
        """Count how many project memberships reference this group."""
        return self.projects.count_documents({
            "members.group_ids": str(group_id)
        })
```

- [ ] **Step 3: Update member methods to use group_ids**

Replace the existing project member methods at lines 268-295:

```python
    def add_project_member(self, project_id: str, user_id: str, group_ids: list) -> bool:
        """Add or update a member on a project with given group IDs."""
        self.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$pull": {"members": {"user_id": user_id}}}
        )
        result = self.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$push": {"members": {"user_id": user_id, "group_ids": [str(g) for g in group_ids]}}}
        )
        return result.modified_count > 0

    def remove_project_member(self, project_id: str, user_id: str) -> bool:
        """Remove a member from a project."""
        result = self.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$pull": {"members": {"user_id": user_id}}}
        )
        return result.modified_count > 0

    def update_project_member_groups(self, project_id: str, user_id: str, group_ids: list) -> bool:
        """Update a member's group assignments on a project."""
        result = self.projects.update_one(
            {"_id": ObjectId(project_id), "members.user_id": user_id},
            {"$set": {"members.$.group_ids": [str(g) for g in group_ids]}}
        )
        return result.modified_count > 0
```

- [ ] **Step 4: Remove website member methods**

Delete the website member methods at lines 299-325 (`add_website_member`, `remove_website_member`, `update_website_member_role`). They are no longer used.

- [ ] **Step 5: Delete `update_project_member_role` method**

This method is replaced by `update_project_member_groups`.

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/core/database.py
git commit -m "feat: add group CRUD and update member methods to use group_ids"
```

---

## Task 5: Permission Resolution Core

**Files:**
- Create: `auto_a11y/core/permissions.py`

- [ ] **Step 1: Create the permissions module**

```python
# auto_a11y/core/permissions.py
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
        (g.get_level(resource) for g in groups),
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
        level = max((g.get_level(resource) for g in groups), default=0)
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
        max_level = max((g.get_level(resource) for g in groups), default=0)
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
        return recording.get('project_id') if recording else None

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
```

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/core/permissions.py
git commit -m "feat: add permission resolution core with decorator and context processor"
```

---

## Task 6: Migration Script

**Files:**
- Create: `auto_a11y/core/migrate_groups.py`

- [ ] **Step 1: Create the migration script**

```python
# auto_a11y/core/migrate_groups.py
"""One-time idempotent migration: seed default groups, migrate roles to group_ids, set is_superadmin."""
import logging
from datetime import datetime
from bson import ObjectId

from auto_a11y.models.permission_group import PermissionGroup, DEFAULT_GROUPS

logger = logging.getLogger(__name__)


def run_migration(db):
    """Run the group permissions migration. Idempotent — safe to call multiple times."""
    _seed_default_groups(db)
    _migrate_superadmin(db)
    _migrate_project_members(db)


def _seed_default_groups(db):
    """Create default groups if they don't exist."""
    for name, config in DEFAULT_GROUPS.items():
        existing = db.get_group_by_name(name)
        if existing:
            logger.info(f"Default group '{name}' already exists, skipping")
            continue

        group = PermissionGroup(
            name=name,
            description=config['description'],
            permissions=config['permissions'],
            is_system=True,
        )
        group_id = db.create_group(group)
        logger.info(f"Created default group '{name}' with id {group_id}")


def _migrate_superadmin(db):
    """Set is_superadmin=True for users with role=admin, False for others."""
    # Only migrate users that don't already have is_superadmin set
    result = db.db['app_users'].update_many(
        {"role": "admin", "is_superadmin": {"$exists": False}},
        {"$set": {"is_superadmin": True}}
    )
    if result.modified_count:
        logger.info(f"Set is_superadmin=True on {result.modified_count} admin users")

    result = db.db['app_users'].update_many(
        {"role": {"$ne": "admin"}, "is_superadmin": {"$exists": False}},
        {"$set": {"is_superadmin": False}}
    )
    if result.modified_count:
        logger.info(f"Set is_superadmin=False on {result.modified_count} non-admin users")


def _migrate_project_members(db):
    """Convert members with 'role' field to 'group_ids' field."""
    role_to_group = {}
    for name in DEFAULT_GROUPS:
        group = db.get_group_by_name(name)
        if group:
            role_to_group[name.lower()] = str(group._id)

    if not role_to_group:
        logger.warning("No default groups found, skipping member migration")
        return

    # Find all projects with members that have 'role' but no 'group_ids'
    projects = db.db['projects'].find({"members.role": {"$exists": True}})

    migrated = 0
    for project_doc in projects:
        members = project_doc.get('members', [])
        updated = False
        for member in members:
            if 'role' in member and 'group_ids' not in member:
                role = member['role']
                group_id = role_to_group.get(role)
                if group_id:
                    member['group_ids'] = [group_id]
                else:
                    member['group_ids'] = []
                updated = True

        if updated:
            db.db['projects'].update_one(
                {"_id": project_doc["_id"]},
                {"$set": {"members": members}}
            )
            migrated += 1

    if migrated:
        logger.info(f"Migrated members in {migrated} projects from role to group_ids")
```

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/core/migrate_groups.py
git commit -m "feat: add group permissions migration script"
```

---

## Task 7: Wire Migration and Context Processor into App

**Files:**
- Modify: `auto_a11y/web/app.py`

- [ ] **Step 1: Import and call migration on startup**

Near the top of `create_app()`, after database initialization (after `app.db = Database(...)` around line 98), add:

```python
from auto_a11y.core.migrate_groups import run_migration
run_migration(app.db)
```

- [ ] **Step 2: Register permission context processor**

After the existing context processors (after `inject_user_has_projects`, around line 268), add:

```python
from auto_a11y.core.permissions import inject_permission_helpers
inject_permission_helpers(app)
```

- [ ] **Step 3: Register groups blueprint**

With the other blueprint registrations (around line 235), add:

```python
from auto_a11y.web.routes.groups import groups_bp
app.register_blueprint(groups_bp, url_prefix='/groups')
```

Also add `'groups.list_groups'` and `'groups.create_group'` and `'groups.edit_group'` to the `before_request` login exemption list if needed (they should NOT be exempt — they require login).

- [ ] **Step 4: Update `is_admin()` references in app.py**

Replace the `is_admin()` checks in `app.py` with `is_superadmin`:

- Line 265: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`
- Line 357: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`
- Line 363: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`
- Line 371: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/web/app.py
git commit -m "feat: wire migration, context processor, and groups blueprint into app"
```

---

## Task 8: Group Management Routes & Templates

**Files:**
- Create: `auto_a11y/web/routes/groups.py`
- Create: `auto_a11y/web/templates/groups/list.html`
- Create: `auto_a11y/web/templates/groups/edit.html`

- [ ] **Step 1: Create group routes**

```python
# auto_a11y/web/routes/groups.py
"""Group management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required

from auto_a11y.core.permissions import permission_required
from auto_a11y.models.permission_group import (
    PermissionGroup, RESOURCE_NOUNS, PERMISSION_LEVELS
)

groups_bp = Blueprint('groups', __name__)


@groups_bp.route('/')
@permission_required('groups', 'read')
def list_groups():
    """List all permission groups."""
    groups = current_app.db.get_all_groups()
    group_data = []
    for g in groups:
        group_data.append({
            'group': g,
            'member_count': current_app.db.count_group_members(g.id),
        })
    return render_template('groups/list.html', groups=group_data)


@groups_bp.route('/create', methods=['GET', 'POST'])
@permission_required('groups', 'create')
def create_group():
    """Create a new permission group."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Group name is required.', 'error')
            return redirect(url_for('groups.create_group'))

        if current_app.db.get_group_by_name(name):
            flash(f'Group "{name}" already exists.', 'error')
            return redirect(url_for('groups.create_group'))

        permissions = {}
        for resource in RESOURCE_NOUNS:
            level = request.form.get(f'perm_{resource}', 'none')
            if level in PERMISSION_LEVELS:
                permissions[resource] = level
            else:
                permissions[resource] = 'none'

        group = PermissionGroup(
            name=name,
            description=description,
            permissions=permissions,
        )
        current_app.db.create_group(group)
        flash(f'Group "{name}" created.', 'success')
        return redirect(url_for('groups.list_groups'))

    return render_template('groups/edit.html',
                           group=None,
                           resource_nouns=RESOURCE_NOUNS,
                           permission_levels=list(PERMISSION_LEVELS.keys()))


@groups_bp.route('/<group_id>/edit', methods=['GET', 'POST'])
@permission_required('groups', 'update')
def edit_group(group_id):
    """Edit an existing permission group."""
    group = current_app.db.get_group(group_id)
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups.list_groups'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Group name is required.', 'error')
            return redirect(url_for('groups.edit_group', group_id=group_id))

        existing = current_app.db.get_group_by_name(name)
        if existing and str(existing._id) != group_id:
            flash(f'Group "{name}" already exists.', 'error')
            return redirect(url_for('groups.edit_group', group_id=group_id))

        permissions = {}
        for resource in RESOURCE_NOUNS:
            level = request.form.get(f'perm_{resource}', 'none')
            if level in PERMISSION_LEVELS:
                permissions[resource] = level
            else:
                permissions[resource] = 'none'

        group.name = name
        group.description = description
        group.permissions = permissions
        current_app.db.update_group(group)
        flash(f'Group "{name}" updated.', 'success')
        return redirect(url_for('groups.list_groups'))

    return render_template('groups/edit.html',
                           group=group,
                           resource_nouns=RESOURCE_NOUNS,
                           permission_levels=list(PERMISSION_LEVELS.keys()))


@groups_bp.route('/<group_id>/delete', methods=['POST'])
@permission_required('groups', 'delete')
def delete_group(group_id):
    """Delete a non-system group."""
    group = current_app.db.get_group(group_id)
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups.list_groups'))

    if group.is_system:
        flash('System groups cannot be deleted.', 'error')
        return redirect(url_for('groups.list_groups'))

    current_app.db.delete_group(group_id)
    flash(f'Group "{group.name}" deleted.', 'success')
    return redirect(url_for('groups.list_groups'))
```

- [ ] **Step 2: Create group list template**

Create `auto_a11y/web/templates/groups/list.html`:

```html
{% extends "base.html" %}
{% block title %}Permission Groups{% endblock %}
{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Permission Groups</h1>
        {% if user_can('groups', 'create') %}
        <a href="{{ url_for('groups.create_group') }}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Create Group
        </a>
        {% endif %}
    </div>

    <div class="table-responsive d-none d-md-block">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Members</th>
                    <th>Type</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for item in groups %}
                <tr>
                    <td>{{ item.group.name }}</td>
                    <td>{{ item.group.description }}</td>
                    <td>{{ item.member_count }}</td>
                    <td>
                        {% if item.group.is_system %}
                        <span class="badge bg-info">System</span>
                        {% else %}
                        <span class="badge bg-secondary">Custom</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if user_can('groups', 'update') %}
                        <a href="{{ url_for('groups.edit_group', group_id=item.group.id) }}" class="btn btn-sm btn-outline-primary">Edit</a>
                        {% endif %}
                        {% if user_can('groups', 'delete') and not item.group.is_system %}
                        <form method="POST" action="{{ url_for('groups.delete_group', group_id=item.group.id) }}" class="d-inline" onsubmit="return confirm('Delete group {{ item.group.name }}?')">
                            <button type="submit" class="btn btn-sm btn-outline-danger">Delete</button>
                        </form>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Mobile card view -->
    <div class="d-md-none">
        {% for item in groups %}
        <div class="card mb-3">
            <div class="card-body">
                <h2 class="h5 card-title">
                    {{ item.group.name }}
                    {% if item.group.is_system %}
                    <span class="badge bg-info">System</span>
                    {% endif %}
                </h2>
                <p class="card-text text-muted">{{ item.group.description }}</p>
                <p class="card-text"><small>{{ item.member_count }} member(s)</small></p>
                <div class="d-flex gap-2">
                    {% if user_can('groups', 'update') %}
                    <a href="{{ url_for('groups.edit_group', group_id=item.group.id) }}" class="btn btn-sm btn-outline-primary">Edit</a>
                    {% endif %}
                    {% if user_can('groups', 'delete') and not item.group.is_system %}
                    <form method="POST" action="{{ url_for('groups.delete_group', group_id=item.group.id) }}" onsubmit="return confirm('Delete group {{ item.group.name }}?')">
                        <button type="submit" class="btn btn-sm btn-outline-danger">Delete</button>
                    </form>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Create group edit template**

Create `auto_a11y/web/templates/groups/edit.html`:

```html
{% extends "base.html" %}
{% block title %}{{ 'Edit' if group else 'Create' }} Group{% endblock %}
{% block content %}
<div class="container mt-4">
    <h1>{{ 'Edit' if group else 'Create' }} Group</h1>

    <form method="POST" class="mt-3">
        <fieldset class="mb-4">
            <legend class="h5">Group Details</legend>
            <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="name" name="name"
                       value="{{ group.name if group else '' }}" required maxlength="100">
            </div>
            <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <input type="text" class="form-control" id="description" name="description"
                       value="{{ group.description if group else '' }}" maxlength="255">
            </div>
        </fieldset>

        <fieldset class="mb-4">
            <legend class="h5">Permissions</legend>
            <p class="text-muted">Each level includes all lower levels: Read &lt; Update &lt; Create &lt; Delete</p>

            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Resource</th>
                            <th>Level</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for resource in resource_nouns %}
                        <tr>
                            <td>
                                <label for="perm_{{ resource }}" class="form-label mb-0">
                                    {{ resource | replace('_', ' ') | title }}
                                </label>
                            </td>
                            <td>
                                <select class="form-select form-select-sm" id="perm_{{ resource }}" name="perm_{{ resource }}" style="max-width: 200px;">
                                    {% for level in permission_levels %}
                                    <option value="{{ level }}"
                                            {% if group and group.permissions.get(resource, 'none') == level %}selected{% endif %}
                                            {% if not group and level == 'none' %}selected{% endif %}>
                                        {{ level | title }}
                                    </option>
                                    {% endfor %}
                                </select>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </fieldset>

        <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary">
                {{ 'Update' if group else 'Create' }} Group
            </button>
            <a href="{{ url_for('groups.list_groups') }}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/routes/groups.py auto_a11y/web/templates/groups/
git commit -m "feat: add group management UI (list, create, edit, delete)"
```

---

## Task 9: Update Members Routes

**Files:**
- Modify: `auto_a11y/web/routes/members.py`

- [ ] **Step 1: Rewrite members.py to use groups**

Replace the entire file:

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/routes/members.py
git commit -m "feat: rewrite members routes to use group assignments instead of roles"
```

---

## Task 10: Update Auth Routes — Replace Decorators

**Files:**
- Modify: `auto_a11y/web/routes/auth.py`

- [ ] **Step 1: Keep old decorators but rewire them**

The old decorators (`admin_required`, `auditor_required`, `role_required`, `project_role_required`, `project_admin_required`) are imported by many files. Instead of deleting them immediately, rewire them to use the new permission system:

Replace the decorator definitions (lines 23-217) with:

```python
def role_required(*roles):
    """Legacy decorator — now checks is_superadmin for admin, otherwise passes."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(_('Please log in to access this page.'), 'warning')
                return redirect(url_for('auth.login', next=request.url))
            if getattr(current_user, 'is_superadmin', False):
                return f(*args, **kwargs)
            flash(_('You do not have permission to access this page.'), 'danger')
            return redirect(url_for('index'))
        return decorated_function
    return decorator


def admin_required(f):
    """Legacy decorator — requires superadmin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_('Please log in to access this page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if not getattr(current_user, 'is_superadmin', False):
            flash(_('Administrator access required.'), 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def auditor_required(f):
    """Legacy decorator — requires superadmin (will be replaced with permission_required)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_('Please log in to access this page.'), 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if getattr(current_user, 'is_superadmin', False):
            return f(*args, **kwargs)
        # For non-superadmins, check if they have projects:create (auditor-level)
        from auto_a11y.core.permissions import user_has_global_permission
        if user_has_global_permission(current_user, 'projects', 'create'):
            return f(*args, **kwargs)
        flash(_('Auditor access required.'), 'danger')
        return redirect(url_for('index'))
    return decorated_function


def get_effective_role(user, request_obj=None, project_id=None, website_id=None, page_id=None):
    """Legacy function — returns UserRole for backward compat.
    Used by templates to determine is_project_admin etc.
    """
    if getattr(user, 'is_superadmin', False):
        return UserRole.ADMIN

    from auto_a11y.core.permissions import user_has_permission
    db = _get_db()

    # Resolve to project_id
    if page_id and not website_id:
        page = db.get_page(page_id)
        if not page:
            return None
        website_id = page.website_id

    if website_id and not project_id:
        website = db.get_website(website_id)
        if not website:
            return None
        project_id = website.project_id

    if not project_id:
        return None

    # Map permission levels to legacy roles
    if user_has_permission(user, project_id, 'project_members', 'delete'):
        return UserRole.ADMIN
    if user_has_permission(user, project_id, 'test_results', 'create'):
        return UserRole.AUDITOR
    if user_has_permission(user, project_id, 'projects', 'read'):
        return UserRole.CLIENT
    return None


def project_role_required(*roles):
    """Legacy decorator — checks group permissions instead of roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if getattr(current_user, 'is_superadmin', False):
                g.effective_role = UserRole.ADMIN
                return f(*args, **kwargs)

            project_id = kwargs.get('project_id')
            website_id = kwargs.get('website_id')
            page_id = kwargs.get('page_id')

            effective_role = get_effective_role(
                current_user, request, project_id, website_id, page_id
            )

            if effective_role not in roles:
                if request.is_json:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                flash('You do not have permission to access this resource.', 'danger')
                abort(403)

            g.effective_role = effective_role
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def project_admin_required(f):
    """Legacy decorator — checks project_members:delete permission."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        if getattr(current_user, 'is_superadmin', False):
            return f(*args, **kwargs)

        from auto_a11y.core.permissions import user_has_permission, _resolve_project_id
        project_id = _resolve_project_id(**kwargs)

        if project_id and user_has_permission(current_user, project_id, 'project_members', 'delete'):
            return f(*args, **kwargs)

        if request.is_json:
            return jsonify({'error': 'Project admin access required'}), 403
        flash('Project administrator access required.', 'danger')
        abort(403)
    return decorated_function
```

- [ ] **Step 2: Update user management routes to use permission_required**

Replace `@admin_required` on the user management routes with `@permission_required`:

```python
from auto_a11y.core.permissions import permission_required

# Line ~656
@auth_bp.route('/users')
@permission_required('users', 'read')
def user_list():
    ...

# Line ~664
@auth_bp.route('/users/create', methods=['GET', 'POST'])
@permission_required('users', 'create')
def user_create():
    ...

# Line ~714
@auth_bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@permission_required('users', 'update')
def user_edit(user_id):
    ...

# Line ~764
@auth_bp.route('/users/<user_id>/delete', methods=['POST'])
@permission_required('users', 'delete')
def user_delete(user_id):
    ...
```

- [ ] **Step 3: Add superadmin toggle to user_edit route**

In the `user_edit` route's POST handler, add handling for the `is_superadmin` field:

```python
# In the 'update' action branch
if action == 'update':
    user.display_name = request.form.get('display_name', '').strip() or None
    user.is_active = request.form.get('is_active') == 'on'
    # Only superadmins can toggle superadmin
    if getattr(current_user, 'is_superadmin', False):
        user.is_superadmin = request.form.get('is_superadmin') == 'on'
    current_app.db.update_app_user(user)
    flash('User updated.', 'success')
```

- [ ] **Step 4: Update find_or_create_sso_user**

In `find_or_create_sso_user` (around line 464), ensure new SSO users get `is_superadmin=False` (which is the default, so no code change needed — just verify).

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/web/routes/auth.py
git commit -m "feat: rewire auth decorators to use group permissions, add permission_required to user routes"
```

---

## Task 11: Update Project Routes

**Files:**
- Modify: `auto_a11y/web/routes/projects.py`

- [ ] **Step 1: Add auto-membership on project creation**

In the `create_project` route (line 233), after the project is created and its ID is returned, add:

```python
# Auto-add creator as member with Admin group
admin_group = current_app.db.get_group_by_name('Admin')
if admin_group:
    current_app.db.add_project_member(project_id, str(current_user.get_id()), [admin_group.id])
```

- [ ] **Step 2: Replace is_admin() checks with is_superadmin**

- Line 24: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`
- Line 216: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`
- Line 516: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/routes/projects.py
git commit -m "feat: add auto-membership on project creation, replace is_admin with is_superadmin"
```

---

## Task 12: Update Testing Routes

**Files:**
- Modify: `auto_a11y/web/routes/testing.py`

- [ ] **Step 1: Replace all `is_admin()` checks**

Replace every `current_user.is_admin()` with `getattr(current_user, 'is_superadmin', False)` at these lines:
- Line 1081
- Line 1370
- Line 1487
- Line 1593
- Line 1621
- Line 1711
- Line 1808

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/routes/testing.py
git commit -m "feat: replace is_admin checks with is_superadmin in testing routes"
```

---

## Task 13: Update Remaining Route Files

**Files:**
- Modify: `auto_a11y/web/routes/public.py`
- Modify: `auto_a11y/web/routes/share_tokens.py`
- Modify: `auto_a11y/web/routes/api.py`

- [ ] **Step 1: Update public.py**

Replace `is_admin()` with `is_superadmin`:
- Line 162: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`
- Line 180: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`
- Line 200: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`

- [ ] **Step 2: Update share_tokens.py**

- Line 134: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`

- [ ] **Step 3: Update api.py**

- Line 111: `current_user.is_admin()` → `getattr(current_user, 'is_superadmin', False)`

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/routes/public.py auto_a11y/web/routes/share_tokens.py auto_a11y/web/routes/api.py
git commit -m "feat: replace is_admin checks with is_superadmin in public, share_tokens, api routes"
```

---

## Task 14: Update Templates

**Files:**
- Modify: `auto_a11y/web/templates/base.html`
- Modify: `auto_a11y/web/templates/auth/user_edit.html`
- Modify: `auto_a11y/web/templates/auth/user_list.html`

- [ ] **Step 1: Update base.html**

Replace `is_admin()` checks with `is_superadmin` (which is injected by the context processor):
- Line 47: `current_user.is_admin()` → `is_superadmin`
- Line 111: `current_user.is_admin()` → `is_superadmin`
- Line 135: `current_user.is_admin()` → `is_superadmin`

Add a "Groups" link in the settings/admin navigation, near the Users link:

```html
{% if user_can('groups', 'read') %}
<a class="dropdown-item" href="{{ url_for('groups.list_groups') }}">
    <i class="bi bi-shield-lock"></i> Groups
</a>
{% endif %}
```

- [ ] **Step 2: Update user_edit.html — add superadmin toggle**

Add a superadmin toggle in the update form (after the `is_active` checkbox, around line 40):

```html
{% if is_superadmin %}
<div class="mb-3 form-check">
    <input type="checkbox" class="form-check-input" id="is_superadmin" name="is_superadmin"
           {% if user.is_superadmin %}checked{% endif %}>
    <label class="form-check-label" for="is_superadmin">Superadmin</label>
    <div class="form-text">Superadmins bypass all permission checks and have full access to everything.</div>
</div>
{% endif %}
```

Add a section showing which projects the user belongs to:

```html
<div class="card mt-4">
    <div class="card-header">
        <h2 class="h5 mb-0">Project Memberships</h2>
    </div>
    <div class="card-body">
        {% if user_projects %}
        <div class="table-responsive">
            <table class="table table-sm">
                <thead>
                    <tr><th>Project</th><th>Groups</th></tr>
                </thead>
                <tbody>
                    {% for p in user_projects %}
                    <tr>
                        <td><a href="{{ url_for('projects.view_project', project_id=p.id) }}">{{ p.name }}</a></td>
                        <td>
                            {% for gname in p.group_names %}
                            <span class="badge bg-secondary">{{ gname }}</span>
                            {% endfor %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <p class="text-muted mb-0">This user is not a member of any projects.</p>
        {% endif %}
    </div>
</div>
```

The route must pass `user_projects` to the template. Update the `user_edit` route in `auth.py` to compute this:

```python
# In user_edit GET handler, before render_template:
user_projects = []
projects = current_app.db.get_projects_for_user(user_id)
all_groups = current_app.db.get_all_groups()
group_map = {g.id: g.name for g in all_groups}
for p in projects:
    member = next((m for m in p.members if m.user_id == user_id), None)
    if member:
        group_names = [group_map.get(gid, '?') for gid in member.group_ids]
        user_projects.append({
            'id': p.id, 'name': p.name, 'group_names': group_names
        })

return render_template('auth/user_edit.html', user=user, user_projects=user_projects)
```

- [ ] **Step 3: Update user_list.html — replace role display**

In the user list table, replace the "Role" column with "Superadmin" badge:

Where the role badge is displayed, change to:
```html
<td>
    {% if u.is_superadmin %}<span class="badge bg-danger">Superadmin</span>{% endif %}
</td>
```

Replace the column header from "Role" to "Status".

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/templates/base.html auto_a11y/web/templates/auth/user_edit.html auto_a11y/web/templates/auth/user_list.html auto_a11y/web/routes/auth.py
git commit -m "feat: update templates for group permissions (superadmin toggle, groups link, project memberships)"
```

---

## Task 15: Update Project View Members Section

**Files:**
- Modify: `auto_a11y/web/templates/projects/view.html`
- Modify: `auto_a11y/web/routes/projects.py` (pass groups to template)

- [ ] **Step 1: Update the project view route to pass group data**

In `view_project` (around line 484), add:

```python
all_groups = current_app.db.get_all_groups()
```

Pass `all_groups=all_groups` to `render_template`.

- [ ] **Step 2: Update the members section in the template**

In the members section of `projects/view.html` (around lines 389-462), update:
- Replace the role dropdown with group checkboxes
- In the add-member modal, replace the role selector with group checkboxes
- In the member list, show group badges instead of a role badge
- The JavaScript for adding/editing members needs to send `group_ids` instead of `role`

The member list display should show:
```html
{% for member in project.members %}
<tr>
    <td>{{ member.email }}</td>
    <td>
        {% for gid in member.group_ids %}
        {% set group = group_map.get(gid) %}
        {% if group %}<span class="badge bg-secondary">{{ group.name }}</span>{% endif %}
        {% endfor %}
    </td>
    <td><!-- edit/remove buttons --></td>
</tr>
{% endfor %}
```

The add-member form should include checkboxes:
```html
<div class="mb-3">
    <label class="form-label">Groups</label>
    {% for group in all_groups %}
    <div class="form-check">
        <input class="form-check-input" type="checkbox" name="group_ids"
               value="{{ group.id }}" id="group_{{ group.id }}">
        <label class="form-check-label" for="group_{{ group.id }}">
            {{ group.name }}
            <small class="text-muted">{{ group.description }}</small>
        </label>
    </div>
    {% endfor %}
</div>
```

- [ ] **Step 3: Update the JavaScript member management**

The existing JavaScript (around lines 635-932) that calls the members API needs to:
- Send `group_ids` array instead of `role` string in POST/PUT requests
- Display group badges instead of role text in the member list
- Show group checkboxes in the edit modal instead of a role dropdown

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/templates/projects/view.html auto_a11y/web/routes/projects.py
git commit -m "feat: update project view members section to use groups"
```

---

## Task 16: Smoke Test and Verify

- [ ] **Step 1: Start the app and verify migration runs**

```bash
python run.py --debug
```

Check console logs for migration messages. Verify:
- Default groups (Admin, Auditor, Client) created in `groups` collection
- Existing admin users have `is_superadmin: true`
- Project members have `group_ids` arrays

- [ ] **Step 2: Verify group management UI**

Navigate to `/groups`:
- All three default groups should appear with "System" badges
- Create a custom group, edit it, delete it
- System groups should not have a delete button

- [ ] **Step 3: Verify project member management**

Navigate to a project's view page:
- Members section should show group badges
- Adding a member should show group checkboxes
- Editing a member should allow changing groups

- [ ] **Step 4: Verify user management**

Navigate to `/auth/users/<id>/edit`:
- Superadmin toggle should appear (if you are superadmin)
- Project memberships section should list projects and groups

- [ ] **Step 5: Verify permission enforcement**

- Non-superadmin with Client group should not see admin nav items
- Non-superadmin with Client group should get 403 on `/auth/users`
- Superadmin should have full access everywhere

- [ ] **Step 6: Final commit if any fixes needed**

```bash
git add -A
git commit -m "fix: address issues found during smoke testing"
```
