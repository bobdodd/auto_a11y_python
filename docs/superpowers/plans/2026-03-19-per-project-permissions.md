# Per-Project/Website Permissions Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scope user permissions per-project/website so non-admin users only see and interact with resources they're assigned to.

**Architecture:** Embed a `members` array on Project and Website MongoDB documents. A new `ProjectMember` dataclass holds `user_id` + `role`. A `project_role_required` decorator resolves the user's effective role via inheritance (website override → project → no access). Global admins bypass all checks.

**Tech Stack:** Python/Flask, MongoDB, Flask-Login, existing UserRole enum (ADMIN, AUDITOR, CLIENT)

**Spec:** `docs/superpowers/specs/2026-03-19-per-project-permissions-design.md`

---

## File Structure

### New Files
- `auto_a11y/models/project_member.py` — ProjectMember dataclass (user_id + role)
- `auto_a11y/web/routes/members.py` — Members blueprint with CRUD routes for project/website membership
- `migrate_add_project_members.py` — One-time migration script
- `tests/test_permissions.py` — Unit tests for permission logic

### Modified Files
- `auto_a11y/models/__init__.py` — Export ProjectMember
- `auto_a11y/models/project.py` — Add `members` field to Project
- `auto_a11y/models/website.py` — Add `members` field to Website
- `auto_a11y/core/database.py` — Add membership DB methods + indexes
- `auto_a11y/web/routes/auth.py` — Add `project_role_required`, `project_admin_required`, `get_effective_role`
- `auto_a11y/web/routes/__init__.py` — Export new decorators and blueprint
- `auto_a11y/web/app.py` — Register members blueprint
- `auto_a11y/web/routes/projects.py` — Filter project list, add decorator to routes
- `auto_a11y/web/routes/api.py` — Add permission decorators to API routes
- `auto_a11y/web/routes/testing.py` — Add permission decorators, filter dashboard data
- `auto_a11y/web/routes/schedules.py` — Add permission decorators
- `auto_a11y/web/routes/share_tokens.py` — Replace `@auditor_required` with `@project_role_required`
- `auto_a11y/web/routes/public.py` — Filter client routes by membership
- `auto_a11y/web/templates/projects/view.html` — Add members management section

---

## Task 1: ProjectMember Model

**Files:**
- Create: `auto_a11y/models/project_member.py`
- Create: `tests/test_permissions.py`

- [ ] **Step 1: Write test for ProjectMember serialization**

Create `tests/test_permissions.py`:

```python
"""Tests for per-project/website permission system."""
import pytest
from auto_a11y.models.project_member import ProjectMember
from auto_a11y.models.app_user import UserRole


class TestProjectMember:
    def test_to_dict(self):
        member = ProjectMember(user_id="abc123", role=UserRole.AUDITOR)
        d = member.to_dict()
        assert d == {"user_id": "abc123", "role": "auditor"}

    def test_from_dict(self):
        member = ProjectMember.from_dict({"user_id": "abc123", "role": "auditor"})
        assert member.user_id == "abc123"
        assert member.role == UserRole.AUDITOR

    def test_from_dict_missing_role_defaults_client(self):
        member = ProjectMember.from_dict({"user_id": "abc123"})
        assert member.role == UserRole.CLIENT

    def test_from_dict_invalid_role_defaults_client(self):
        member = ProjectMember.from_dict({"user_id": "abc123", "role": "bogus"})
        assert member.role == UserRole.CLIENT
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_permissions.py::TestProjectMember -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement ProjectMember**

Create `auto_a11y/models/project_member.py`:

```python
"""Project/website membership for per-resource access control.

Note: This is distinct from ProjectUser/WebsiteUser which store test
credentials for sites under test. ProjectMember controls which platform
users can see/manage a project or website.
"""
from dataclasses import dataclass
from auto_a11y.models.app_user import UserRole


@dataclass
class ProjectMember:
    """A user's role on a specific project or website."""
    user_id: str      # AppUser._id as string
    role: UserRole    # ADMIN, AUDITOR, or CLIENT

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectMember":
        role_str = data.get("role", "client")
        try:
            role = UserRole(role_str)
        except ValueError:
            role = UserRole.CLIENT
        return cls(
            user_id=data["user_id"],
            role=role,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_permissions.py::TestProjectMember -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Export from models package**

In `auto_a11y/models/__init__.py`, add import and `__all__` entry for `ProjectMember`:

```python
from .project_member import ProjectMember
```

Add `'ProjectMember'` to the `__all__` list.

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/models/project_member.py auto_a11y/models/__init__.py tests/test_permissions.py
git commit -m "feat: add ProjectMember model for per-project permissions"
```

---

## Task 2: Add `members` Field to Project and Website Models

**Files:**
- Modify: `auto_a11y/models/project.py`
- Modify: `auto_a11y/models/website.py`
- Modify: `tests/test_permissions.py`

- [ ] **Step 1: Write tests for Project members serialization**

Append to `tests/test_permissions.py`:

```python
from auto_a11y.models.project import Project
from auto_a11y.models.website import Website


class TestProjectMembers:
    def test_project_to_dict_includes_members(self):
        from auto_a11y.models.project_member import ProjectMember
        p = Project(name="Test")
        p.members = [ProjectMember(user_id="u1", role=UserRole.AUDITOR)]
        d = p.to_dict()
        assert d["members"] == [{"user_id": "u1", "role": "auditor"}]

    def test_project_from_dict_parses_members(self):
        d = {"name": "Test", "members": [{"user_id": "u1", "role": "admin"}]}
        p = Project.from_dict(d)
        assert len(p.members) == 1
        assert p.members[0].user_id == "u1"
        assert p.members[0].role == UserRole.ADMIN

    def test_project_from_dict_missing_members_defaults_empty(self):
        d = {"name": "Test"}
        p = Project.from_dict(d)
        assert p.members == []


class TestWebsiteMembers:
    def test_website_to_dict_includes_members(self):
        from auto_a11y.models.project_member import ProjectMember
        w = Website(project_id="p1", url="https://example.com")
        w.members = [ProjectMember(user_id="u1", role=UserRole.CLIENT)]
        d = w.to_dict()
        assert d["members"] == [{"user_id": "u1", "role": "client"}]

    def test_website_from_dict_parses_members(self):
        d = {"project_id": "p1", "url": "https://example.com",
             "members": [{"user_id": "u1", "role": "auditor"}]}
        w = Website.from_dict(d)
        assert len(w.members) == 1
        assert w.members[0].role == UserRole.AUDITOR

    def test_website_from_dict_missing_members_defaults_empty(self):
        d = {"project_id": "p1", "url": "https://example.com"}
        w = Website.from_dict(d)
        assert w.members == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_permissions.py::TestProjectMembers tests/test_permissions.py::TestWebsiteMembers -v`
Expected: FAIL — `members` attribute not found or not serialized

- [ ] **Step 3: Add `members` field to Project model**

In `auto_a11y/models/project.py`:

Add import at top:
```python
from auto_a11y.models.project_member import ProjectMember
```

Add field to the Project dataclass (after existing fields, before methods):
```python
    members: list = field(default_factory=list)  # List[ProjectMember]
```

In `to_dict()`, add:
```python
        d['members'] = [m.to_dict() for m in self.members]
```

In `from_dict()`, add:
```python
        members_data = data.get('members', [])
        project.members = [ProjectMember.from_dict(m) for m in members_data]
```

- [ ] **Step 4: Add `members` field to Website model**

In `auto_a11y/models/website.py`:

Add import at top:
```python
from auto_a11y.models.project_member import ProjectMember
```

Add field to the Website dataclass (after existing fields, before methods):
```python
    members: list = field(default_factory=list)  # List[ProjectMember]
```

In `to_dict()`, add:
```python
        d['members'] = [m.to_dict() for m in self.members]
```

In `from_dict()`, add:
```python
        members_data = data.get('members', [])
        website.members = [ProjectMember.from_dict(m) for m in members_data]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_permissions.py -v`
Expected: PASS (all tests)

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/models/project.py auto_a11y/models/website.py tests/test_permissions.py
git commit -m "feat: add members field to Project and Website models"
```

---

## Task 3: Database Layer — Membership Methods and Indexes

**Files:**
- Modify: `auto_a11y/core/database.py`
- Modify: `tests/test_permissions.py`

- [ ] **Step 1: Add membership indexes**

In `auto_a11y/core/database.py`, inside the `_create_indexes()` method (after existing project/website indexes around line 78), add:

```python
        self.projects.create_index([("members.user_id", 1)])
        self.websites.create_index([("members.user_id", 1)])
```

- [ ] **Step 2: Add `get_projects_for_user` method**

Add after `get_all_projects()` (around line 258):

```python
    def get_projects_for_user(self, user_id: str) -> list:
        """Return projects where user_id is a member."""
        cursor = self.projects.find({"members.user_id": user_id})
        return [Project.from_dict(doc) for doc in cursor]
```

- [ ] **Step 3: Add member CRUD methods for projects**

Add after the new `get_projects_for_user` method:

```python
    def add_project_member(self, project_id: str, user_id: str, role) -> bool:
        """Add or update a member on a project."""
        from auto_a11y.models.app_user import UserRole
        # Remove existing entry if present, then add new one
        self.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$pull": {"members": {"user_id": user_id}}}
        )
        result = self.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$push": {"members": {"user_id": user_id, "role": role.value}}}
        )
        return result.modified_count > 0

    def remove_project_member(self, project_id: str, user_id: str) -> bool:
        """Remove a member from a project."""
        result = self.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$pull": {"members": {"user_id": user_id}}}
        )
        return result.modified_count > 0

    def update_project_member_role(self, project_id: str, user_id: str, role) -> bool:
        """Change a member's role on a project."""
        result = self.projects.update_one(
            {"_id": ObjectId(project_id), "members.user_id": user_id},
            {"$set": {"members.$.role": role.value}}
        )
        return result.modified_count > 0
```

- [ ] **Step 4: Add member CRUD methods for websites**

Add after the project member methods:

```python
    def add_website_member(self, website_id: str, user_id: str, role) -> bool:
        """Add or update a member override on a website."""
        self.websites.update_one(
            {"_id": ObjectId(website_id)},
            {"$pull": {"members": {"user_id": user_id}}}
        )
        result = self.websites.update_one(
            {"_id": ObjectId(website_id)},
            {"$push": {"members": {"user_id": user_id, "role": role.value}}}
        )
        return result.modified_count > 0

    def remove_website_member(self, website_id: str, user_id: str) -> bool:
        """Remove a member override from a website."""
        result = self.websites.update_one(
            {"_id": ObjectId(website_id)},
            {"$pull": {"members": {"user_id": user_id}}}
        )
        return result.modified_count > 0

    def update_website_member_role(self, website_id: str, user_id: str, role) -> bool:
        """Change a member's override role on a website."""
        result = self.websites.update_one(
            {"_id": ObjectId(website_id), "members.user_id": user_id},
            {"$set": {"members.$.role": role.value}}
        )
        return result.modified_count > 0
```

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/core/database.py
git commit -m "feat: add membership DB methods and indexes"
```

---

## Task 4: Permission Decorators and Role Resolution

**Files:**
- Modify: `auto_a11y/web/routes/auth.py`
- Modify: `auto_a11y/web/routes/__init__.py`
- Modify: `tests/test_permissions.py`

- [ ] **Step 1: Write tests for `get_effective_role`**

Append to `tests/test_permissions.py`:

```python
from unittest.mock import MagicMock, patch
from auto_a11y.models.project_member import ProjectMember


def _make_user(role=UserRole.AUDITOR, user_id="user1"):
    """Create a mock AppUser."""
    user = MagicMock()
    user.role = role
    user.get_id.return_value = user_id
    user.is_admin.return_value = (role == UserRole.ADMIN)
    user.is_authenticated = True
    return user


def _make_project(project_id="proj1", members=None):
    project = MagicMock()
    project._id = project_id
    project.members = members or []
    return project


def _make_website(website_id="web1", project_id="proj1", members=None):
    website = MagicMock()
    website._id = website_id
    website.project_id = project_id
    website.members = members or []
    return website


def _make_page(page_id="page1", website_id="web1"):
    page = MagicMock()
    page._id = page_id
    page.website_id = website_id
    return page


class TestGetEffectiveRole:
    def test_global_admin_always_returns_admin(self):
        from auto_a11y.web.routes.auth import get_effective_role
        user = _make_user(role=UserRole.ADMIN)
        result = get_effective_role(user, None, project_id="proj1")
        assert result == UserRole.ADMIN

    def test_project_member_returns_role(self):
        from auto_a11y.web.routes.auth import get_effective_role
        user = _make_user(user_id="u1")
        project = _make_project(members=[
            ProjectMember(user_id="u1", role=UserRole.AUDITOR)
        ])
        with patch("auto_a11y.web.routes.auth._get_db") as mock_db:
            mock_db.return_value.get_project.return_value = project
            result = get_effective_role(user, None, project_id="proj1")
        assert result == UserRole.AUDITOR

    def test_no_membership_returns_none(self):
        from auto_a11y.web.routes.auth import get_effective_role
        user = _make_user(user_id="u1")
        project = _make_project(members=[])
        with patch("auto_a11y.web.routes.auth._get_db") as mock_db:
            mock_db.return_value.get_project.return_value = project
            result = get_effective_role(user, None, project_id="proj1")
        assert result is None

    def test_website_override_takes_precedence(self):
        from auto_a11y.web.routes.auth import get_effective_role
        user = _make_user(user_id="u1")
        project = _make_project(members=[
            ProjectMember(user_id="u1", role=UserRole.AUDITOR)
        ])
        website = _make_website(members=[
            ProjectMember(user_id="u1", role=UserRole.CLIENT)
        ])
        with patch("auto_a11y.web.routes.auth._get_db") as mock_db:
            mock_db.return_value.get_website.return_value = website
            mock_db.return_value.get_project.return_value = project
            result = get_effective_role(user, None, website_id="web1")
        assert result == UserRole.CLIENT

    def test_website_no_override_inherits_project(self):
        from auto_a11y.web.routes.auth import get_effective_role
        user = _make_user(user_id="u1")
        project = _make_project(members=[
            ProjectMember(user_id="u1", role=UserRole.AUDITOR)
        ])
        website = _make_website(members=[])
        with patch("auto_a11y.web.routes.auth._get_db") as mock_db:
            mock_db.return_value.get_website.return_value = website
            mock_db.return_value.get_project.return_value = project
            result = get_effective_role(user, None, website_id="web1")
        assert result == UserRole.AUDITOR

    def test_page_resolves_through_website_to_project(self):
        from auto_a11y.web.routes.auth import get_effective_role
        user = _make_user(user_id="u1")
        page = _make_page()
        website = _make_website(members=[])
        project = _make_project(members=[
            ProjectMember(user_id="u1", role=UserRole.CLIENT)
        ])
        with patch("auto_a11y.web.routes.auth._get_db") as mock_db:
            mock_db.return_value.get_page.return_value = page
            mock_db.return_value.get_website.return_value = website
            mock_db.return_value.get_project.return_value = project
            result = get_effective_role(user, None, page_id="page1")
        assert result == UserRole.CLIENT
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_permissions.py::TestGetEffectiveRole -v`
Expected: FAIL — `get_effective_role` not found

- [ ] **Step 3: Implement `_get_db`, `get_effective_role`, and decorators in auth.py**

In `auto_a11y/web/routes/auth.py`, add imports at top:

```python
from auto_a11y.models.app_user import UserRole
```

Add the helper function and decorators (after the existing `auditor_required` decorator, before `validate_token`):

```python
def _get_db():
    """Get database instance from current app."""
    return current_app.db


def get_effective_role(user, request_obj=None, project_id=None, website_id=None, page_id=None):
    """Return the user's effective role for the given resource context.

    Resolution order:
    1. Global admin → UserRole.ADMIN
    2. page_id → resolve to website_id
    3. website_id → check website members, then fall to project
    4. project_id → check project members
    5. None → no access
    """
    if user.is_admin():
        return UserRole.ADMIN

    db = _get_db()

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
        user_id = str(user.get_id())
        for member in getattr(website, 'members', []):
            if member.user_id == user_id:
                return member.role
        # Fall through to project
        project_id = website.project_id

    if project_id:
        project = db.get_project(project_id)
        if not project:
            return None
        user_id = str(user.get_id())
        for member in getattr(project, 'members', []):
            if member.user_id == user_id:
                return member.role

    return None  # No access


def project_role_required(*roles):
    """Decorator: requires user to have one of the given roles on the project/website.

    Extracts project_id, website_id, or page_id from route kwargs.
    Caches resolved role on g.effective_role.
    Global admins bypass all checks.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            # Global admins bypass
            if current_user.is_admin():
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
    """Decorator: requires project-level ADMIN (ignores website overrides).

    Used for membership management routes where a project admin should
    retain management access even with a website-level override.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        if current_user.is_admin():
            return f(*args, **kwargs)

        db = _get_db()
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

        if request.is_json:
            return jsonify({'error': 'Project admin access required'}), 403
        flash('Project administrator access required.', 'danger')
        abort(403)
    return decorated_function
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_permissions.py::TestGetEffectiveRole -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Export new decorators from routes package**

In `auto_a11y/web/routes/__init__.py`, add to imports:

```python
from .auth import project_role_required, project_admin_required, get_effective_role
```

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/routes/auth.py auto_a11y/web/routes/__init__.py tests/test_permissions.py
git commit -m "feat: add project_role_required decorator and role resolution"
```

---

## Task 5: Members Blueprint — CRUD Routes

**Files:**
- Create: `auto_a11y/web/routes/members.py`
- Modify: `auto_a11y/web/app.py`
- Modify: `auto_a11y/web/routes/__init__.py`

- [ ] **Step 1: Create members blueprint**

Create `auto_a11y/web/routes/members.py`:

```python
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
```

- [ ] **Step 2: Export from routes package**

In `auto_a11y/web/routes/__init__.py`, add:

```python
from .members import members_bp
```

- [ ] **Step 3: Register blueprint in app.py**

In `auto_a11y/web/app.py`, after the other `register_blueprint` calls (around line 219), add:

```python
    app.register_blueprint(members_bp)
```

No URL prefix — routes already include `/projects/` and `/websites/` paths.

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/routes/members.py auto_a11y/web/routes/__init__.py auto_a11y/web/app.py
git commit -m "feat: add members blueprint for project/website membership management"
```

---

## Task 6: Apply Permission Decorators to Project Routes

**Files:**
- Modify: `auto_a11y/web/routes/projects.py`

- [ ] **Step 1: Add import for new decorators**

At the top of `auto_a11y/web/routes/projects.py`, add:

```python
from auto_a11y.web.routes.auth import project_role_required, get_effective_role
from auto_a11y.models.app_user import UserRole
from auto_a11y.models.project_member import ProjectMember
```

- [ ] **Step 2: Filter project list by membership**

In `list_projects()` (around line 205), replace the `get_all_projects()` call:

Change:
```python
    projects = current_app.db.get_all_projects()
```
To:
```python
    if current_user.is_admin():
        projects = current_app.db.get_all_projects()
    else:
        projects = current_app.db.get_projects_for_user(str(current_user.get_id()))
```

- [ ] **Step 3: Add decorator to project detail route**

On the `view_project(project_id)` function (around line 466), add the decorator:

```python
@projects_bp.route('/<project_id>')
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR, UserRole.CLIENT)
def view_project(project_id):
```

- [ ] **Step 4: Add decorator to project report route**

Find the project report route and add:

```python
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR, UserRole.CLIENT)
```

- [ ] **Step 5: Auto-add creator as project ADMIN on project creation**

In `create_project()` (around line 218), after `project_id = current_app.db.create_project(project)`, add:

```python
        # Auto-add creator as project admin
        current_app.db.add_project_member(
            project_id, str(current_user.get_id()), UserRole.ADMIN
        )
```

- [ ] **Step 6: Add decorator to add-website route**

On the `add_website(project_id)` handler (around line 688), add:

```python
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)
```

- [ ] **Step 7: Verify the app starts without errors**

Run: `.venv/bin/python run.py --test-db`
Expected: No import errors, DB connection OK

- [ ] **Step 8: Commit**

```bash
git add auto_a11y/web/routes/projects.py
git commit -m "feat: apply project permissions to project routes"
```

---

## Task 7: Apply Permission Decorators to API Routes

**Files:**
- Modify: `auto_a11y/web/routes/api.py`

- [ ] **Step 1: Add imports**

At the top of `auto_a11y/web/routes/api.py`, add:

```python
from auto_a11y.web.routes.auth import project_role_required
from auto_a11y.models.app_user import UserRole
from auto_a11y.models.project_member import ProjectMember
```

- [ ] **Step 2: Filter project list APIs**

There are two project list endpoints to update:

**`GET /api/v1/projects` (around line 99)** — replace the project query:

```python
    if current_user.is_admin():
        projects = current_app.db.get_all_projects()
    else:
        projects = current_app.db.get_projects_for_user(str(current_user.get_id()))
    # Apply status filter if provided
    if status:
        projects = [p for p in projects if p.status == status]
```

Also check for any other API list endpoint (e.g. a separate `GET /api/list` or `GET /api/v1/projects/list`) and apply the same filtering.

- [ ] **Step 3: Auto-add creator on API project creation**

In the `POST /projects` handler (around line 127), after project creation add:

```python
        current_app.db.add_project_member(
            project_id, str(current_user.get_id()), UserRole.ADMIN
        )
```

- [ ] **Step 4: Add decorators to project CRUD endpoints**

Apply these decorators:

```python
# GET /projects/<project_id> (line ~155)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR, UserRole.CLIENT)

# PUT /projects/<project_id> (line ~170)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)

# DELETE /projects/<project_id> (line ~197)
@project_role_required(UserRole.ADMIN)

# POST /projects/<project_id>/websites (line ~226)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)

# GET /projects/<project_id>/websites (line ~212)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR, UserRole.CLIENT)

# GET /projects/<project_id>/reports (line ~450)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR, UserRole.CLIENT)
```

- [ ] **Step 5: Add decorators to website endpoints**

For website endpoints that take `website_id` (not `project_id`), the decorator resolves website → project automatically:

```python
# GET /websites/<website_id> (line ~255)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR, UserRole.CLIENT)

# DELETE /websites/<website_id> (line ~265)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)

# POST /websites/<website_id>/discover (line ~396)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)

# POST /websites/<website_id>/test (line ~417)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)
```

- [ ] **Step 6: Add decorators to page endpoints**

For page endpoints, the decorator resolves page → website → project:

```python
# GET /pages/<page_id> (line ~334)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR, UserRole.CLIENT)

# POST /pages/<page_id>/test (line ~344)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)

# GET /pages/<page_id>/test-results (line ~380)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR, UserRole.CLIENT)
```

- [ ] **Step 7: Commit**

```bash
git add auto_a11y/web/routes/api.py
git commit -m "feat: apply project permissions to API routes"
```

---

## Task 8: Apply Permissions to Testing, Schedule, and Share Token Routes

**Files:**
- Modify: `auto_a11y/web/routes/testing.py`
- Modify: `auto_a11y/web/routes/schedules.py`
- Modify: `auto_a11y/web/routes/share_tokens.py`

- [ ] **Step 1: Add imports to testing.py**

```python
from auto_a11y.web.routes.auth import project_role_required, get_effective_role
from auto_a11y.models.app_user import UserRole
```

- [ ] **Step 2: Filter testing dashboard data by membership**

In the dashboard route handler (line ~1073), where project data is loaded, add membership filtering. The dashboard takes `project_id` and `website_id` as query params. Add filtering logic:

```python
    # Filter projects by membership
    if current_user.is_admin():
        projects = current_app.db.get_all_projects()
    else:
        projects = current_app.db.get_projects_for_user(str(current_user.get_id()))
```

If a `project_id` query param is provided, verify the user has access before showing data.

- [ ] **Step 3: Add permission check to run-tests endpoints**

On `POST /testing/run-test` (line ~1183) and `POST /testing/api/run-tests` (line ~1445), add a permission check. These take `page_ids` or `website_id` in the request body, not URL kwargs. Add manual permission checking inside the handler:

```python
    # Check permission on the website/project being tested
    if website_id:
        role = get_effective_role(current_user, request, website_id=website_id)
        if role not in (UserRole.ADMIN, UserRole.AUDITOR):
            return jsonify({'error': 'Insufficient permissions'}), 403
```

- [ ] **Step 4: Filter stats and trends API by membership**

In `/api/stats` (line ~1346), `/api/trends` (line ~1546), and related endpoints, add membership verification when `project_id` or `website_id` query params are provided:

```python
    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')
    if not current_user.is_admin():
        if project_id:
            role = get_effective_role(current_user, request, project_id=project_id)
            if role is None:
                return jsonify({'error': 'Insufficient permissions'}), 403
        elif website_id:
            role = get_effective_role(current_user, request, website_id=website_id)
            if role is None:
                return jsonify({'error': 'Insufficient permissions'}), 403
        else:
            # No filter specified — restrict to user's projects
            user_projects = current_app.db.get_projects_for_user(str(current_user.get_id()))
            project_ids = [str(p._id) for p in user_projects]
            # Pass project_ids to the stats/trends query to filter results
```

Apply this pattern to: `/api/stats`, `/api/trends`, `/api/trends/detailed`, `/api/trends/compare`, `/api/trends/progress`.

- [ ] **Step 5: Add imports and decorators to schedules.py**

```python
from auto_a11y.web.routes.auth import project_role_required
from auto_a11y.models.app_user import UserRole
```

Apply decorators to schedule routes. All take `website_id` as a URL kwarg:

```python
# All schedule CRUD routes:
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)
```

For the schedule list route that takes `project_id` as a query param (line ~21), filter by membership inside the handler.

- [ ] **Step 6: Update share_tokens.py decorators**

Replace `@auditor_required` with `@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)` on all share token routes.

In `auto_a11y/web/routes/share_tokens.py`, change imports:
```python
from auto_a11y.web.routes.auth import project_role_required
from auto_a11y.models.app_user import UserRole
```

Replace on each route:
```python
# POST /projects/<project_id>/share-tokens (line ~31)
# POST /websites/<website_id>/share-tokens (line ~42)
# GET /projects/<project_id>/share-tokens (line ~98)
# GET /websites/<website_id>/share-tokens (line ~108)
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)
```

For `POST /share-tokens/<token_id>/revoke` (line ~118), this route has `token_id` not `project_id`. Add these imports and a manual permission check inside the handler:

```python
from auto_a11y.models.share_token import TokenScope
from auto_a11y.web.routes.auth import get_effective_role
```

Then in the handler, before revoking:

```python
    # Look up token to find its scope, then check project membership
    token = current_app.db.get_share_token(token_id)
    if not token:
        return jsonify({'error': 'Token not found'}), 404
    # Resolve scope_id to project
    if token.scope == TokenScope.WEBSITE:
        website = current_app.db.get_website(token.scope_id)
        project_id = website.project_id if website else None
    else:
        project_id = token.scope_id
    role = get_effective_role(current_user, request, project_id=project_id)
    if role not in (UserRole.ADMIN, UserRole.AUDITOR):
        return jsonify({'error': 'Insufficient permissions'}), 403
```

- [ ] **Step 7: Commit**

```bash
git add auto_a11y/web/routes/testing.py auto_a11y/web/routes/schedules.py auto_a11y/web/routes/share_tokens.py
git commit -m "feat: apply project permissions to testing, schedule, and share token routes"
```

---

## Task 9: Apply Permissions to Public/Client Routes

**Files:**
- Modify: `auto_a11y/web/routes/public.py`

- [ ] **Step 1: Add imports**

```python
from auto_a11y.web.routes.auth import get_effective_role
from auto_a11y.models.app_user import UserRole
```

- [ ] **Step 2: Filter client project list**

In `GET /client/projects/` (line ~155), where it lists projects for logged-in users, add membership filtering:

```python
    # For logged-in users (no token), filter by membership
    if g.access_scope is None:  # No token — logged-in user
        if current_user.is_admin():
            projects = current_app.db.get_all_projects()
        else:
            projects = current_app.db.get_projects_for_user(str(current_user.get_id()))
```

- [ ] **Step 3: Add membership check to client project/website detail routes**

In `GET /client/project/<project_id>/` (line ~167) and `GET /client/project/<project_id>/w/<website_id>/` (line ~183), add a membership check for logged-in users (when `g.access_scope is None`):

```python
    if g.access_scope is None and not current_user.is_admin():
        role = get_effective_role(current_user, request, project_id=project_id)
        if role is None:
            abort(403)
```

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/routes/public.py
git commit -m "feat: apply project permissions to public/client routes"
```

---

## Task 10: Members Management UI

**Files:**
- Modify: `auto_a11y/web/templates/projects/view.html`

- [ ] **Step 1: Read the existing template to understand structure**

Read `auto_a11y/web/templates/projects/view.html` to understand the existing tab/card patterns, then add a "Members" tab/section.

- [ ] **Step 2: Add members management section to project view template**

In `auto_a11y/web/templates/projects/view.html`, add a "Members" tab/section. This should be visible only to project admins and global admins. The UI calls the members API endpoints via JavaScript:

Add a "Members" tab that contains:
- A table listing current members (email, role, remove button)
- An "Add Member" form with user dropdown and role selector
- Role change via dropdown that auto-saves
- JavaScript to call `GET/POST/PUT/DELETE /projects/<project_id>/members`

The exact template code depends on the existing template structure. Read the template first, then add the members section following the existing tab/card patterns.

Key JavaScript functions needed:

```javascript
async function loadMembers(projectId) {
    const resp = await fetch(`/projects/${projectId}/members`);
    const data = await resp.json();
    // Render members table and add-member form
}

async function addMember(projectId, userId, role) {
    await fetch(`/projects/${projectId}/members`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_id: userId, role: role})
    });
    loadMembers(projectId);
}

async function updateMemberRole(projectId, userId, newRole) {
    await fetch(`/projects/${projectId}/members/${userId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({role: newRole})
    });
}

async function removeMember(projectId, userId) {
    if (!confirm('Remove this member?')) return;
    await fetch(`/projects/${projectId}/members/${userId}`, {
        method: 'DELETE'
    });
    loadMembers(projectId);
}
```

- [ ] **Step 3: Pass permission context to template**

In the `view_project()` route handler in `projects.py`, pass the user's effective role to the template so it can conditionally show the members section:

```python
    is_project_admin = current_user.is_admin() or (
        hasattr(g, 'effective_role') and g.effective_role == UserRole.ADMIN
    )
    return render_template('projects/view.html', ..., is_project_admin=is_project_admin)
```

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/templates/projects/view.html auto_a11y/web/routes/projects.py
git commit -m "feat: add members management UI to project view"
```

---

## Task 11: Migration Script

**Files:**
- Create: `migrate_add_project_members.py`

- [ ] **Step 1: Create migration script**

Create `migrate_add_project_members.py`:

```python
"""One-time migration: add all existing users as members to all existing projects.

Run once before deploying permission-enforced code.

Usage:
    python migrate_add_project_members.py [--dry-run]
"""
import sys
from datetime import datetime
from auto_a11y.core.database import Database
from auto_a11y.models.app_user import UserRole
from config import Config

MIGRATION_NAME = "add_project_members_v1"


def run_migration(dry_run=False):
    config = Config()
    db = Database(config.MONGODB_URI, config.DATABASE_NAME)

    # Check if already run
    if db.db['_migrations'].find_one({"name": MIGRATION_NAME}):
        print(f"Migration '{MIGRATION_NAME}' already applied. Skipping.")
        return

    users = db.get_app_users()
    projects = db.get_all_projects()

    print(f"Found {len(users)} users and {len(projects)} projects")

    for project in projects:
        project_id = str(project._id)
        existing_member_ids = {m.user_id for m in project.members}
        added = 0

        for user in users:
            user_id = str(user.get_id())
            if user_id in existing_member_ids:
                continue

            if dry_run:
                print(f"  [DRY RUN] Would add {user.email} ({user.role.value}) to '{project.name}'")
            else:
                db.add_project_member(project_id, user_id, user.role)
            added += 1

        print(f"Project '{project.name}': added {added} members")

    if not dry_run:
        db.db['_migrations'].insert_one({
            "name": MIGRATION_NAME,
            "applied_at": datetime.utcnow(),
            "users_count": len(users),
            "projects_count": len(projects),
        })
        print(f"\nMigration '{MIGRATION_NAME}' applied successfully.")
    else:
        print("\n[DRY RUN] No changes made.")


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    run_migration(dry_run=dry_run)
```

- [ ] **Step 2: Commit**

```bash
git add migrate_add_project_members.py
git commit -m "feat: add migration script to populate project membership"
```

---

## Task 12: Startup Warning and Final Verification

**Files:**
- Modify: `auto_a11y/web/app.py`

- [ ] **Step 1: Add startup warning for unmigrated projects**

In `auto_a11y/web/app.py`, after the app is created and DB is initialized, add a check:

```python
    # Warn about projects without members (pre-migration)
    try:
        empty_count = app.db.projects.count_documents({"$or": [
            {"members": {"$exists": False}},
            {"members": {"$size": 0}},
        ]})
        if empty_count > 0:
            app.logger.warning(
                f"{empty_count} project(s) have no members. "
                "Run 'python migrate_add_project_members.py' to populate membership."
            )
    except Exception:
        pass  # Don't block startup
```

- [ ] **Step 2: Run the full app and verify no errors**

Run: `.venv/bin/python run.py --test-db`
Expected: No import errors, app starts, DB connection OK

- [ ] **Step 3: Run all permission tests**

Run: `.venv/bin/python -m pytest tests/test_permissions.py -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/app.py
git commit -m "feat: add startup warning for unmigrated projects"
```

---

## Task Summary

| Task | Description | Depends On |
|------|-------------|------------|
| 1 | ProjectMember model | — |
| 2 | Add members field to Project/Website | Task 1 |
| 3 | Database membership methods + indexes | Task 2 |
| 4 | Permission decorators + role resolution | Task 1 |
| 5 | Members blueprint (CRUD routes) | Tasks 3, 4 |
| 6 | Apply permissions to project routes | Tasks 3, 4 |
| 7 | Apply permissions to API routes | Tasks 3, 4 |
| 8 | Apply permissions to testing/schedule/token routes | Tasks 3, 4 |
| 9 | Apply permissions to public/client routes | Tasks 3, 4 |
| 10 | Members management UI | Tasks 5, 6 |
| 11 | Migration script | Task 3 |
| 12 | Startup warning + final verification | All |
