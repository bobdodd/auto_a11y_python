"""
Discovered Page model for key pages/screens flagged for manual inspection
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from .page import DrupalSyncStatus


@dataclass
class DiscoveredPage:
    """
    Discovered Page - A key page/screen flagged for manual inspection or lived experience testing.

    Discovered pages represent the 20-25 most interesting pages in an audit that warrant
    manual inspection. Pages are "interesting" if they show accessibility concerns or contain
    complex UI elements (date pickers, carousels, forms, videos, etc.).

    Can be created manually or from scraped web pages.
    """

    # Core identifiers
    title: str  # User-friendly page name
    url: str  # Page URL (or screen identifier for apps/devices)
    project_id: str  # Link to parent project/audit

    # Source information
    source_type: str = "manual"  # "manual", "scraped_page", "app_screen", "device_display"
    source_page_id: Optional[str] = None  # If created from scraped Page, reference to Page._id
    source_website_id: Optional[str] = None  # If from scraped page, reference to Website._id

    # Taxonomy tags (from Drupal taxonomies)
    interested_because: List[str] = field(default_factory=list)  # Why is this page interesting? (taxonomy term names)
    page_elements: List[str] = field(default_factory=list)  # Areas of display: header, footer, main, etc. (taxonomy term names)

    # Notes
    private_notes: Optional[str] = None  # Private notes for auditors (HTML)
    public_notes: Optional[str] = None  # Public notes for audit reports (HTML)

    # Audit flags
    include_in_report: bool = True  # Include this page in the audit report
    audited: bool = False  # Has this page been audited?
    manual_audit: bool = False  # Has this page had manual inspection?

    # Media
    screenshot_paths: List[str] = field(default_factory=list)  # Paths to screenshots
    document_links: List[dict] = field(default_factory=list)  # PDFs/documents found on page: [{"uri": "...", "title": "..."}]

    # Drupal sync
    drupal_uuid: Optional[str] = None  # UUID of discovered_page in Drupal
    drupal_sync_status: DrupalSyncStatus = DrupalSyncStatus.NOT_SYNCED
    drupal_last_synced: Optional[datetime] = None
    drupal_error_message: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None  # User ID who created this

    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get discovered page ID as string"""
        return str(self._id) if self._id else None

    @property
    def is_synced(self) -> bool:
        """Check if page is synced with Drupal"""
        return self.drupal_sync_status == DrupalSyncStatus.SYNCED and self.drupal_uuid is not None

    @property
    def needs_sync(self) -> bool:
        """Check if page needs to be synced to Drupal"""
        return self.drupal_sync_status in [DrupalSyncStatus.NOT_SYNCED, DrupalSyncStatus.SYNC_FAILED]

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'title': self.title,
            'url': self.url,
            'project_id': self.project_id,
            'source_type': self.source_type,
            'source_page_id': self.source_page_id,
            'source_website_id': self.source_website_id,
            'interested_because': self.interested_because,
            'page_elements': self.page_elements,
            'private_notes': self.private_notes,
            'public_notes': self.public_notes,
            'include_in_report': self.include_in_report,
            'audited': self.audited,
            'manual_audit': self.manual_audit,
            'screenshot_paths': self.screenshot_paths,
            'document_links': self.document_links,
            'drupal_uuid': self.drupal_uuid,
            'drupal_sync_status': self.drupal_sync_status.value,
            'drupal_last_synced': self.drupal_last_synced,
            'drupal_error_message': self.drupal_error_message,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'DiscoveredPage':
        """Create from MongoDB document"""
        return cls(
            title=data['title'],
            url=data['url'],
            project_id=data['project_id'],
            source_type=data.get('source_type', 'manual'),
            source_page_id=data.get('source_page_id'),
            source_website_id=data.get('source_website_id'),
            interested_because=data.get('interested_because', []),
            page_elements=data.get('page_elements', []),
            private_notes=data.get('private_notes'),
            public_notes=data.get('public_notes'),
            include_in_report=data.get('include_in_report', True),
            audited=data.get('audited', False),
            manual_audit=data.get('manual_audit', False),
            screenshot_paths=data.get('screenshot_paths', []),
            document_links=data.get('document_links', []),
            drupal_uuid=data.get('drupal_uuid'),
            drupal_sync_status=DrupalSyncStatus(data.get('drupal_sync_status', 'not_synced')),
            drupal_last_synced=data.get('drupal_last_synced'),
            drupal_error_message=data.get('drupal_error_message'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            created_by=data.get('created_by'),
            _id=data.get('_id')
        )

    @classmethod
    def from_page(cls, page_model, project_id: str) -> 'DiscoveredPage':
        """
        Create a DiscoveredPage from a scraped Page model.

        Args:
            page_model: Page instance to convert
            project_id: Project ID to link to

        Returns:
            DiscoveredPage instance
        """
        return cls(
            title=page_model.title or page_model.url,
            url=page_model.url,
            project_id=project_id,
            source_type="scraped_page",
            source_page_id=page_model.id,
            source_website_id=page_model.website_id,
            interested_because=page_model.discovery_reasons,
            page_elements=page_model.discovery_areas,
            private_notes=page_model.discovery_notes_private,
            public_notes=page_model.discovery_notes_public,
            screenshot_paths=[page_model.screenshot_path] if page_model.screenshot_path else [],
            drupal_uuid=page_model.drupal_discovered_page_uuid,
            drupal_sync_status=page_model.drupal_sync_status,
            drupal_last_synced=page_model.drupal_last_synced,
            drupal_error_message=page_model.drupal_error_message
        )
