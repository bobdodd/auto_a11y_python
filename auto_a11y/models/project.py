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


class ProjectType(Enum):
    """Project type enum"""
    WEBSITE = "website"
    APP = "app"
    TANGIBLE_DEVICE = "tangible_device"
    NAV_AND_WAYFINDING = "nav_and_wayfinding"


@dataclass
class Project:
    """
    Project model - container for accessibility audits

    Projects can be of different types:
    - website: Contains multiple websites (backward compatible)
    - app: Mobile or desktop application
    - tangible_device: Physical devices (kiosks, ATMs, etc.)
    - nav_and_wayfinding: Signage, navigation systems, etc.

    All project types support:
    - Multiple recordings (manual audits, lived experience testing)
    - Touchpoints (common accessibility issues)
    """

    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    project_type: ProjectType = ProjectType.WEBSITE  # Default for backward compatibility

    # Type-specific identifiers
    website_ids: List[str] = field(default_factory=list)  # Only for WEBSITE type
    app_identifier: Optional[str] = None  # For APP type (e.g., bundle ID, package name)
    device_model: Optional[str] = None  # For TANGIBLE_DEVICE type
    location: Optional[str] = None  # For NAV_AND_WAYFINDING type

    # Common to all types
    recording_ids: List[str] = field(default_factory=list)  # Manual audit recordings

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    _id: Optional[ObjectId] = None
    
    @property
    def id(self) -> str:
        """Get project ID as string"""
        return str(self._id) if self._id else None

    @property
    def is_website_project(self) -> bool:
        """Check if this is a website project"""
        return self.project_type == ProjectType.WEBSITE

    @property
    def project_type_display(self) -> str:
        """Get human-readable project type"""
        type_map = {
            ProjectType.WEBSITE: "Website",
            ProjectType.APP: "App",
            ProjectType.TANGIBLE_DEVICE: "Tangible Device",
            ProjectType.NAV_AND_WAYFINDING: "Nav and Wayfinding"
        }
        return type_map.get(self.project_type, self.project_type.value.replace('_', ' ').title())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'project_type': self.project_type.value,
            'website_ids': self.website_ids,
            'app_identifier': self.app_identifier,
            'device_model': self.device_model,
            'location': self.location,
            'recording_ids': self.recording_ids,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'config': self.config,
            'tags': self.tags
        }
        if self._id:
            data['_id'] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """Create from MongoDB document with backward compatibility"""
        # Backward compatibility: if project_type not set, default to WEBSITE
        project_type_value = data.get('project_type', 'website')
        try:
            project_type = ProjectType(project_type_value)
        except ValueError:
            project_type = ProjectType.WEBSITE

        return cls(
            name=data['name'],
            description=data.get('description'),
            status=ProjectStatus(data.get('status', 'active')),
            project_type=project_type,
            website_ids=data.get('website_ids', []),
            app_identifier=data.get('app_identifier'),
            device_model=data.get('device_model'),
            location=data.get('location'),
            recording_ids=data.get('recording_ids', []),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            config=data.get('config', {}),
            tags=data.get('tags', []),
            _id=data.get('_id')
        )
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()