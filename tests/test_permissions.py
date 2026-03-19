"""Tests for per-project/website permission system."""
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
