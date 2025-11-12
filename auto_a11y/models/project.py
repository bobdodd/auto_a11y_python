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
class LivedExperienceTester:
    """Lived experience tester for accessibility testing"""
    name: str
    email: Optional[str] = None
    disability_type: Optional[str] = None  # e.g., "Blind", "Low Vision", "Deaf", "Motor Disability"
    assistive_tech: List[str] = field(default_factory=list)  # e.g., ["JAWS", "Screen Magnifier"]
    notes: Optional[str] = None
    _id: Optional[str] = None  # Use string ID for simplicity

    @property
    def id(self) -> str:
        """Get tester ID"""
        return self._id

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            '_id': self._id,
            'name': self.name,
            'email': self.email,
            'disability_type': self.disability_type,
            'assistive_tech': self.assistive_tech,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LivedExperienceTester':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            email=data.get('email'),
            disability_type=data.get('disability_type'),
            assistive_tech=data.get('assistive_tech', []),
            notes=data.get('notes'),
            _id=data.get('_id')
        )


@dataclass
class TestSupervisor:
    """Test supervisor who oversees lived experience testing"""
    name: str
    email: Optional[str] = None
    role: Optional[str] = None  # e.g., "Accessibility Specialist", "Research Lead"
    organization: Optional[str] = None
    notes: Optional[str] = None
    _id: Optional[str] = None  # Use string ID for simplicity

    @property
    def id(self) -> str:
        """Get supervisor ID"""
        return self._id

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            '_id': self._id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'organization': self.organization,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TestSupervisor':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            email=data.get('email'),
            role=data.get('role'),
            organization=data.get('organization'),
            notes=data.get('notes'),
            _id=data.get('_id')
        )


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

    # Lived experience testing participants
    lived_experience_testers: List[LivedExperienceTester] = field(default_factory=list)
    test_supervisors: List[TestSupervisor] = field(default_factory=list)

    # Drupal integration
    drupal_audit_name: Optional[str] = None  # Name of corresponding audit in Drupal (for sync)

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
            'lived_experience_testers': [t.to_dict() for t in self.lived_experience_testers],
            'test_supervisors': [s.to_dict() for s in self.test_supervisors],
            'drupal_audit_name': self.drupal_audit_name,
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

        # Parse nested objects
        testers_data = data.get('lived_experience_testers', [])
        testers = [LivedExperienceTester.from_dict(t) for t in testers_data]

        supervisors_data = data.get('test_supervisors', [])
        supervisors = [TestSupervisor.from_dict(s) for s in supervisors_data]

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
            lived_experience_testers=testers,
            test_supervisors=supervisors,
            drupal_audit_name=data.get('drupal_audit_name'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            config=data.get('config', {}),
            tags=data.get('tags', []),
            _id=data.get('_id')
        )
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()

    # Helper methods for managing testers and supervisors
    def add_tester(self, tester: LivedExperienceTester) -> None:
        """Add a lived experience tester to the project"""
        import uuid
        if not tester._id:
            tester._id = str(uuid.uuid4())
        self.lived_experience_testers.append(tester)
        self.update_timestamp()

    def remove_tester(self, tester_id: str) -> bool:
        """Remove a lived experience tester by ID"""
        original_count = len(self.lived_experience_testers)
        self.lived_experience_testers = [t for t in self.lived_experience_testers if t.id != tester_id]
        if len(self.lived_experience_testers) < original_count:
            self.update_timestamp()
            return True
        return False

    def get_tester(self, tester_id: str) -> Optional[LivedExperienceTester]:
        """Get a lived experience tester by ID"""
        for tester in self.lived_experience_testers:
            if tester.id == tester_id:
                return tester
        return None

    def update_tester(self, tester: LivedExperienceTester) -> bool:
        """Update a lived experience tester"""
        for i, t in enumerate(self.lived_experience_testers):
            if t.id == tester.id:
                self.lived_experience_testers[i] = tester
                self.update_timestamp()
                return True
        return False

    def add_supervisor(self, supervisor: TestSupervisor) -> None:
        """Add a test supervisor to the project"""
        import uuid
        if not supervisor._id:
            supervisor._id = str(uuid.uuid4())
        self.test_supervisors.append(supervisor)
        self.update_timestamp()

    def remove_supervisor(self, supervisor_id: str) -> bool:
        """Remove a test supervisor by ID"""
        original_count = len(self.test_supervisors)
        self.test_supervisors = [s for s in self.test_supervisors if s.id != supervisor_id]
        if len(self.test_supervisors) < original_count:
            self.update_timestamp()
            return True
        return False

    def get_supervisor(self, supervisor_id: str) -> Optional[TestSupervisor]:
        """Get a test supervisor by ID"""
        for supervisor in self.test_supervisors:
            if supervisor.id == supervisor_id:
                return supervisor
        return None

    def update_supervisor(self, supervisor: TestSupervisor) -> bool:
        """Update a test supervisor"""
        for i, s in enumerate(self.test_supervisors):
            if s.id == supervisor.id:
                self.test_supervisors[i] = supervisor
                self.update_timestamp()
                return True
        return False