"""
Recording model for Dictaphone audio/video audit sessions
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from bson import ObjectId
from .page import DrupalSyncStatus


class RecordingType(Enum):
    """Type of recording"""
    AUDIT = "audit"
    LIVED_EXPERIENCE_WEBSITE = "lived_experience_website"
    LIVED_EXPERIENCE_APP = "lived_experience_app"
    LIVED_EXPERIENCE_TANGIBLE_DEVICE = "lived_experience_tangible_device"
    LIVED_EXPERIENCE_NAV_AND_WAYFINDING = "lived_experience_nav_and_wayfinding"


@dataclass
class Recording:
    """Audio/video recording session from Dictaphone or manual audits"""

    # Core identifiers
    recording_id: str  # e.g., "NED-A"
    title: str
    description: Optional[str] = None

    # Media information
    media_file_path: Optional[str] = None  # Path to MP4 file
    duration: Optional[str] = None  # Total recording duration (HH:MM:SS)
    recorded_date: Optional[datetime] = None

    # Audit context
    auditor_name: Optional[str] = None
    auditor_role: Optional[str] = None  # e.g., "Screen Reader User", "Expert Auditor"
    test_user_account: Optional[str] = None  # Test account used (e.g., "Premium User", "Admin")
    recording_type: RecordingType = RecordingType.AUDIT

    # Lived experience testing participants (IDs referencing project testers/supervisors)
    lived_experience_tester_id: Optional[str] = None  # ID of tester from project.lived_experience_testers
    test_supervisor_id: Optional[str] = None  # ID of supervisor from project.test_supervisors

    # Testing scope - what content/features were tested
    testing_scope: Dict[str, bool] = field(default_factory=dict)  # e.g., {"forms": True, "video": False, ...}

    # Relationships
    project_id: Optional[str] = None  # Link to AutoA11y project

    # Component/Section references (context-specific based on project type)
    website_ids: List[str] = field(default_factory=list)  # Specific websites (for WEBSITE projects)
    page_urls: List[str] = field(default_factory=list)  # Specific page URLs
    page_ids: List[str] = field(default_factory=list)  # Specific page IDs (from database)
    discovered_page_ids: List[str] = field(default_factory=list)  # Discovered page IDs (from database)
    component_names: List[str] = field(default_factory=list)  # Common components (header, nav, footer, etc.)
    app_screens: List[str] = field(default_factory=list)  # Specific screens/views (for APP projects)
    device_sections: List[str] = field(default_factory=list)  # Device sections (for TANGIBLE_DEVICE projects)

    # Task context
    task_description: Optional[str] = None  # Specific task performed (e.g., "Complete checkout process", "Navigate to settings")

    # Statistics (computed from issues)
    total_issues: int = 0
    high_impact_count: int = 0
    medium_impact_count: int = 0
    low_impact_count: int = 0

    # Recording Content (Structured data)
    key_takeaways: List[Dict[str, Any]] = field(default_factory=list)  # List of {number, topic, description}
    user_painpoints: List[Dict[str, Any]] = field(default_factory=list)  # List of {title, user_quote, timecodes: [{start, end, duration}]}
    user_assertions: List[Dict[str, Any]] = field(default_factory=list)  # List of {number, assertion, user_quote, timecodes, context}

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None

    # Drupal sync (audit_video export)
    drupal_video_uuid: Optional[str] = None  # UUID of audit_video node in Drupal
    drupal_video_nid: Optional[int] = None  # Drupal node ID
    drupal_sync_status: DrupalSyncStatus = DrupalSyncStatus.NOT_SYNCED
    drupal_last_synced: Optional[datetime] = None
    drupal_error_message: Optional[str] = None

    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get recording ID as string"""
        return str(self._id) if self._id else None

    @property
    def is_synced(self) -> bool:
        """Check if recording is synced with Drupal"""
        return self.drupal_sync_status == DrupalSyncStatus.SYNCED and self.drupal_video_uuid is not None

    @property
    def needs_sync(self) -> bool:
        """Check if recording needs to be synced to Drupal"""
        return self.drupal_sync_status in [DrupalSyncStatus.NOT_SYNCED, DrupalSyncStatus.SYNC_FAILED]

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'recording_id': self.recording_id,
            'title': self.title,
            'description': self.description,
            'media_file_path': self.media_file_path,
            'duration': self.duration,
            'recorded_date': self.recorded_date,
            'auditor_name': self.auditor_name,
            'auditor_role': self.auditor_role,
            'test_user_account': self.test_user_account,
            'recording_type': self.recording_type.value,
            'lived_experience_tester_id': self.lived_experience_tester_id,
            'test_supervisor_id': self.test_supervisor_id,
            'testing_scope': self.testing_scope,
            'project_id': self.project_id,
            'website_ids': self.website_ids,
            'page_urls': self.page_urls,
            'page_ids': self.page_ids,
            'discovered_page_ids': self.discovered_page_ids,
            'component_names': self.component_names,
            'app_screens': self.app_screens,
            'device_sections': self.device_sections,
            'task_description': self.task_description,
            'key_takeaways': self.key_takeaways,
            'user_painpoints': self.user_painpoints,
            'user_assertions': self.user_assertions,
            'total_issues': self.total_issues,
            'high_impact_count': self.high_impact_count,
            'medium_impact_count': self.medium_impact_count,
            'low_impact_count': self.low_impact_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags,
            'notes': self.notes,
            'drupal_video_uuid': self.drupal_video_uuid,
            'drupal_video_nid': self.drupal_video_nid,
            'drupal_sync_status': self.drupal_sync_status.value,
            'drupal_last_synced': self.drupal_last_synced,
            'drupal_error_message': self.drupal_error_message
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Recording':
        """Create from dictionary"""
        # Handle ObjectId
        obj_id = data.get('_id')

        # Parse recording_type enum (with backward compatibility for old audit_type field)
        recording_type_value = data.get('recording_type') or data.get('audit_type', 'audit')
        recording_type = RecordingType(recording_type_value) if recording_type_value else RecordingType.AUDIT

        return cls(
            recording_id=data['recording_id'],
            title=data['title'],
            description=data.get('description'),
            media_file_path=data.get('media_file_path'),
            duration=data.get('duration'),
            recorded_date=data.get('recorded_date'),
            auditor_name=data.get('auditor_name'),
            auditor_role=data.get('auditor_role'),
            test_user_account=data.get('test_user_account'),
            recording_type=recording_type,
            lived_experience_tester_id=data.get('lived_experience_tester_id'),
            test_supervisor_id=data.get('test_supervisor_id'),
            testing_scope=data.get('testing_scope', {}),
            project_id=data.get('project_id'),
            website_ids=data.get('website_ids', []),
            page_urls=data.get('page_urls', []),
            page_ids=data.get('page_ids', []),
            discovered_page_ids=data.get('discovered_page_ids', []),
            component_names=data.get('component_names', []),
            app_screens=data.get('app_screens', []),
            device_sections=data.get('device_sections', []),
            task_description=data.get('task_description'),
            key_takeaways=data.get('key_takeaways', []),
            user_painpoints=data.get('user_painpoints', []),
            user_assertions=data.get('user_assertions', []),
            total_issues=data.get('total_issues', 0),
            high_impact_count=data.get('high_impact_count', 0),
            medium_impact_count=data.get('medium_impact_count', 0),
            low_impact_count=data.get('low_impact_count', 0),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            tags=data.get('tags', []),
            notes=data.get('notes'),
            drupal_video_uuid=data.get('drupal_video_uuid'),
            drupal_video_nid=data.get('drupal_video_nid'),
            drupal_sync_status=DrupalSyncStatus(data.get('drupal_sync_status', 'not_synced')),
            drupal_last_synced=data.get('drupal_last_synced'),
            drupal_error_message=data.get('drupal_error_message'),
            _id=obj_id
        )


@dataclass
class Timecode:
    """Timecode reference in a recording"""
    start: str  # HH:MM:SS.mmm format
    end: str  # HH:MM:SS.mmm format
    duration: str  # HH:MM:SS.mmm format

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'start': self.start,
            'end': self.end,
            'duration': self.duration
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Timecode':
        """Create from dictionary"""
        return cls(
            start=data['start'],
            end=data['end'],
            duration=data['duration']
        )

    def to_seconds(self, time_str: str) -> float:
        """Convert HH:MM:SS.mmm to total seconds"""
        try:
            # Split into time and milliseconds
            if '.' in time_str:
                time_part, ms_part = time_str.split('.')
            else:
                time_part = time_str
                ms_part = '0'

            # Parse time components
            parts = time_part.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
            elif len(parts) == 2:
                hours = 0
                minutes, seconds = map(int, parts)
            else:
                return 0.0

            # Calculate total seconds
            total = hours * 3600 + minutes * 60 + seconds + float(f"0.{ms_part}")
            return total
        except (ValueError, AttributeError):
            return 0.0

    @property
    def start_seconds(self) -> float:
        """Get start time in seconds"""
        return self.to_seconds(self.start)

    @property
    def end_seconds(self) -> float:
        """Get end time in seconds"""
        return self.to_seconds(self.end)


@dataclass
class WCAGReference:
    """WCAG criteria reference"""
    criteria: str  # e.g., "1.3.1"
    level: str  # "A", "AA", "AAA"
    versions: List[str] = field(default_factory=list)  # ["2.0", "2.1", "2.2"]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'criteria': self.criteria,
            'level': self.level,
            'versions': self.versions
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WCAGReference':
        """Create from dictionary"""
        return cls(
            criteria=data['criteria'],
            level=data['level'],
            versions=data.get('versions', [])
        )
