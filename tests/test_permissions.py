"""Tests for per-project/website permission system."""
import os
os.environ.setdefault('RUN_AI_ANALYSIS', 'false')

import pytest
from auto_a11y.models.project_member import ProjectMember
from auto_a11y.models.app_user import UserRole
from auto_a11y.models.project import Project
from auto_a11y.models.website import Website


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


from unittest.mock import MagicMock, patch


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
