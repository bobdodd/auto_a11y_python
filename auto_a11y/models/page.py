"""
Page model for individual web pages
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
from bson import ObjectId


class PageStatus(Enum):
    """Page status enum"""
    DISCOVERED = "discovered"
    QUEUED = "queued"
    TESTING = "testing"
    TESTED = "tested"
    ERROR = "error"
    SKIPPED = "skipped"
    DISCOVERY_FAILED = "discovery_failed"  # Failed during discovery (timeout, redirect, etc)


class DrupalSyncStatus(Enum):
    """Drupal synchronization status"""
    NOT_SYNCED = "not_synced"
    SYNCED = "synced"
    SYNC_FAILED = "sync_failed"
    PENDING = "pending"


@dataclass
class Page:
    """Page model"""
    
    website_id: str
    url: str
    title: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)
    discovered_from: Optional[str] = None  # URL that linked to this page
    discovery_run_id: Optional[str] = None  # ID of the discovery run that found this page
    last_tested: Optional[datetime] = None
    status: PageStatus = PageStatus.DISCOVERED
    violation_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    discovery_count: int = 0
    pass_count: int = 0
    test_duration_ms: Optional[int] = None
    priority: str = "normal"  # high, normal, low
    depth: int = 0  # Crawl depth from start page
    error_reason: Optional[str] = None  # Reason for discovery/test failure
    is_in_latest_discovery: bool = True  # Is this page in the most recent discovery?
    screenshot_path: Optional[str] = None  # Path to page screenshot
    setup_script_id: Optional[str] = None  # Reference to page_setup_scripts._id
    visible_to_users: List[str] = field(default_factory=list)  # List of user IDs who can access this page (empty string for guest, user_id for authenticated)

    # Discovered Page (Drupal) Integration Fields
    is_flagged_for_discovery: bool = False  # Flag this page as "discovered page" for export to Drupal
    discovery_reasons: List[str] = field(default_factory=list)  # "Interested because" taxonomy term names
    discovery_areas: List[str] = field(default_factory=list)  # "Page elements" (area of display) taxonomy term names
    discovery_notes_private: Optional[str] = None  # Private notes for auditors (HTML)
    discovery_notes_public: Optional[str] = None  # Public notes for audit reports (HTML)
    drupal_discovered_page_uuid: Optional[str] = None  # UUID of corresponding discovered_page in Drupal
    drupal_sync_status: DrupalSyncStatus = DrupalSyncStatus.NOT_SYNCED  # Sync status with Drupal
    drupal_last_synced: Optional[datetime] = None  # Timestamp of last successful sync
    drupal_error_message: Optional[str] = None  # Error message if sync failed

    _id: Optional[ObjectId] = None
    
    @property
    def id(self) -> str:
        """Get page ID as string"""
        return str(self._id) if self._id else None
    
    @property
    def needs_testing(self) -> bool:
        """Check if page needs testing"""
        return self.status in [PageStatus.DISCOVERED, PageStatus.QUEUED, PageStatus.ERROR]
    
    @property
    def has_issues(self) -> bool:
        """Check if page has accessibility issues"""
        return self.violation_count > 0 or self.warning_count > 0 or self.info_count > 0 or self.discovery_count > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'website_id': self.website_id,
            'url': self.url,
            'title': self.title,
            'discovered_at': self.discovered_at,
            'discovered_from': self.discovered_from,
            'discovery_run_id': self.discovery_run_id,
            'last_tested': self.last_tested,
            'status': self.status.value,
            'violation_count': self.violation_count,
            'warning_count': self.warning_count,
            'info_count': self.info_count,
            'discovery_count': self.discovery_count,
            'pass_count': self.pass_count,
            'test_duration_ms': self.test_duration_ms,
            'priority': self.priority,
            'depth': self.depth,
            'error_reason': self.error_reason,
            'is_in_latest_discovery': self.is_in_latest_discovery,
            'screenshot_path': self.screenshot_path,
            'setup_script_id': self.setup_script_id,
            'visible_to_users': self.visible_to_users,
            'is_flagged_for_discovery': self.is_flagged_for_discovery,
            'discovery_reasons': self.discovery_reasons,
            'discovery_areas': self.discovery_areas,
            'discovery_notes_private': self.discovery_notes_private,
            'discovery_notes_public': self.discovery_notes_public,
            'drupal_discovered_page_uuid': self.drupal_discovered_page_uuid,
            'drupal_sync_status': self.drupal_sync_status.value,
            'drupal_last_synced': self.drupal_last_synced,
            'drupal_error_message': self.drupal_error_message
        }
        if self._id:
            data['_id'] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Page':
        """Create from MongoDB document"""
        return cls(
            website_id=data['website_id'],
            url=data['url'],
            title=data.get('title'),
            discovered_at=data.get('discovered_at', datetime.now()),
            discovered_from=data.get('discovered_from'),
            discovery_run_id=data.get('discovery_run_id'),
            last_tested=data.get('last_tested'),
            status=PageStatus(data.get('status', 'discovered')),
            violation_count=data.get('violation_count', 0),
            warning_count=data.get('warning_count', 0),
            info_count=data.get('info_count', 0),
            discovery_count=data.get('discovery_count', 0),
            pass_count=data.get('pass_count', 0),
            test_duration_ms=data.get('test_duration_ms'),
            priority=data.get('priority', 'normal'),
            depth=data.get('depth', 0),
            error_reason=data.get('error_reason'),
            is_in_latest_discovery=data.get('is_in_latest_discovery', True),
            screenshot_path=data.get('screenshot_path'),
            setup_script_id=data.get('setup_script_id'),
            visible_to_users=data.get('visible_to_users', []),
            is_flagged_for_discovery=data.get('is_flagged_for_discovery', False),
            discovery_reasons=data.get('discovery_reasons', []),
            discovery_areas=data.get('discovery_areas', []),
            discovery_notes_private=data.get('discovery_notes_private'),
            discovery_notes_public=data.get('discovery_notes_public'),
            drupal_discovered_page_uuid=data.get('drupal_discovered_page_uuid'),
            drupal_sync_status=DrupalSyncStatus(data.get('drupal_sync_status', 'not_synced')),
            drupal_last_synced=data.get('drupal_last_synced'),
            drupal_error_message=data.get('drupal_error_message'),
            _id=data.get('_id')
        )