"""
ShareToken model for public share links
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
from bson import ObjectId


class TokenScope(Enum):
    """Scope of a share token"""
    PROJECT = "project"
    WEBSITE = "website"


@dataclass
class ShareToken:
    """Share token for public access to project/website results"""

    scope: TokenScope
    scope_id: str  # Project or website ObjectId as string
    created_by: str  # AppUser ID who created this token
    label: str  # Human-readable label for the token

    token_hash: str = ""  # SHA-256 hash of the signed token string
    expires_at: Optional[datetime] = None  # None = never expires
    revoked: bool = False
    revoked_at: Optional[datetime] = None

    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    use_count: int = 0

    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get token ID as string"""
        return str(self._id) if self._id else None

    @property
    def is_expired(self) -> bool:
        """Check if token has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if token is currently valid (not expired, not revoked)"""
        return not self.revoked and not self.is_expired

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'scope': self.scope.value,
            'scope_id': self.scope_id,
            'created_by': self.created_by,
            'label': self.label,
            'token_hash': self.token_hash,
            'expires_at': self.expires_at,
            'revoked': self.revoked,
            'revoked_at': self.revoked_at,
            'created_at': self.created_at,
            'last_used': self.last_used,
            'use_count': self.use_count,
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'ShareToken':
        """Create from MongoDB document"""
        scope = data.get('scope', 'project')
        if isinstance(scope, str):
            scope = TokenScope(scope)

        return cls(
            scope=scope,
            scope_id=data['scope_id'],
            created_by=data['created_by'],
            label=data.get('label', ''),
            token_hash=data.get('token_hash', ''),
            expires_at=data.get('expires_at'),
            revoked=data.get('revoked', False),
            revoked_at=data.get('revoked_at'),
            created_at=data.get('created_at', datetime.now()),
            last_used=data.get('last_used'),
            use_count=data.get('use_count', 0),
            _id=data.get('_id'),
        )
