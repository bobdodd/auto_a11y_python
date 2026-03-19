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
