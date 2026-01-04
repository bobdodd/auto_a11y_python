"""
AppUser model for application authentication and authorization
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash


class UserRole(Enum):
    """Application user roles"""
    ADMIN = "admin"
    AUDITOR = "auditor"
    CLIENT = "client"


@dataclass
class AppUser:
    """Application user for authentication"""

    email: str
    password_hash: str
    role: UserRole = UserRole.CLIENT

    display_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False

    last_login: Optional[datetime] = None
    login_count: int = 0
    failed_login_count: int = 0
    locked_until: Optional[datetime] = None

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get user ID as string"""
        return str(self._id) if self._id else None

    @property
    def name_display(self) -> str:
        """Get display name or email"""
        return self.display_name or self.email.split('@')[0]

    def get_id(self) -> str:
        """Required by Flask-Login"""
        return str(self._id) if self._id else None

    @property
    def is_authenticated(self) -> bool:
        """Required by Flask-Login"""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Required by Flask-Login"""
        return False

    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN

    def is_auditor(self) -> bool:
        """Check if user has auditor role"""
        return self.role == UserRole.AUDITOR

    def is_client(self) -> bool:
        """Check if user has client role"""
        return self.role == UserRole.CLIENT

    def can_create_projects(self) -> bool:
        """Check if user can create projects"""
        return self.role in [UserRole.ADMIN, UserRole.AUDITOR]

    def can_run_tests(self) -> bool:
        """Check if user can run tests"""
        return self.role in [UserRole.ADMIN, UserRole.AUDITOR]

    def can_view_reports(self) -> bool:
        """Check if user can view reports"""
        return True

    def can_download_reports(self) -> bool:
        """Check if user can download reports"""
        return True

    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.role == UserRole.ADMIN

    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def record_login(self, success: bool):
        """Record a login attempt"""
        if success:
            self.last_login = datetime.now()
            self.login_count += 1
            self.failed_login_count = 0
            self.locked_until = None
        else:
            self.failed_login_count += 1
            if self.failed_login_count >= 5:
                from datetime import timedelta
                self.locked_until = datetime.now() + timedelta(minutes=15)
        self.updated_at = datetime.now()

    def is_locked(self) -> bool:
        """Check if account is locked"""
        if self.locked_until and self.locked_until > datetime.now():
            return True
        return False

    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role.value,
            'display_name': self.display_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login,
            'login_count': self.login_count,
            'failed_login_count': self.failed_login_count,
            'locked_until': self.locked_until,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'AppUser':
        """Create from MongoDB document"""
        role = data.get('role', 'client')
        if isinstance(role, str):
            role = UserRole(role)

        return cls(
            email=data['email'],
            password_hash=data['password_hash'],
            role=role,
            display_name=data.get('display_name'),
            is_active=data.get('is_active', True),
            is_verified=data.get('is_verified', False),
            last_login=data.get('last_login'),
            login_count=data.get('login_count', 0),
            failed_login_count=data.get('failed_login_count', 0),
            locked_until=data.get('locked_until'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            _id=data.get('_id')
        )

    @classmethod
    def create(cls, email: str, password: str, role: UserRole = UserRole.CLIENT, display_name: str = None) -> 'AppUser':
        """Create a new user with hashed password"""
        user = cls(
            email=email.lower(),
            password_hash='',
            role=role,
            display_name=display_name
        )
        user.set_password(password)
        return user
