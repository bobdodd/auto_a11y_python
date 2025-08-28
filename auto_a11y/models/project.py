"""
Project model for organizing accessibility audits
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from bson import ObjectId


class ProjectStatus(Enum):
    """Project status enum"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Project:
    """Project model"""
    
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    config: Dict[str, Any] = field(default_factory=dict)
    website_ids: List[str] = field(default_factory=list)
    _id: Optional[ObjectId] = None
    
    @property
    def id(self) -> str:
        """Get project ID as string"""
        return str(self._id) if self._id else None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'config': self.config,
            'website_ids': self.website_ids
        }
        if self._id:
            data['_id'] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """Create from MongoDB document"""
        return cls(
            name=data['name'],
            description=data.get('description'),
            status=ProjectStatus(data.get('status', 'active')),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            config=data.get('config', {}),
            website_ids=data.get('website_ids', []),
            _id=data.get('_id')
        )
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()