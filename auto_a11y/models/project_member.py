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
