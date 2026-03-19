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
