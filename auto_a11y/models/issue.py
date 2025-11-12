"""
Issue model for Drupal-synced accessibility findings

This model represents issues that can be synced with Drupal,
supporting both automated test results and manual audit findings.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from bson import ObjectId

from auto_a11y.models.test_result import ImpactLevel
from auto_a11y.models.page import DrupalSyncStatus


@dataclass
class Issue:
    """
    Accessibility issue that can be synced with Drupal.

    Supports both automated test findings and manual audit findings,
    with bidirectional sync to Drupal issue nodes.
    """

    # Core identification
    title: str
    description: str  # Maps to body in Drupal

    # Classification
    impact: ImpactLevel = ImpactLevel.MEDIUM  # Maps to field_impact (high/med/low)
    issue_type: Optional[str] = None  # Maps to field_issue_type taxonomy
    location_on_page: Optional[str] = None  # Maps to field_location_on_page taxonomy

    # WCAG references
    wcag_criteria: List[str] = field(default_factory=list)  # Maps to field_wcag_chapter

    # Technical details
    xpath: Optional[str] = None  # Maps to field_xpath
    element: Optional[str] = None
    html: Optional[str] = None
    url: Optional[str] = None  # Maps to field_url

    # Recording context (for manual findings)
    recording_id: Optional[str] = None  # Link to Recording document
    video_timecode: Optional[str] = None  # Maps to field_video_timecode

    # Detailed issue information (Dictaphone-style)
    what: Optional[str] = None  # What the issue is
    why: Optional[str] = None  # Why it matters
    who: Optional[str] = None  # Who is affected
    remediation: Optional[str] = None  # How to fix it

    # Relationships
    project_id: Optional[str] = None
    page_urls: List[str] = field(default_factory=list)
    page_ids: List[str] = field(default_factory=list)
    discovered_page_ids: List[str] = field(default_factory=list)
    component_names: List[str] = field(default_factory=list)

    # Source tracking
    source_type: str = "manual"  # "automated", "manual", "hybrid"
    detection_method: Optional[str] = None  # "axe", "pa11y", "dictaphone", "expert"

    # Status
    status: str = "open"  # open, in_progress, resolved, verified

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    # Drupal sync
    drupal_issue_id: Optional[int] = None  # Maps to field_id
    drupal_uuid: Optional[str] = None  # Drupal node UUID
    drupal_nid: Optional[int] = None  # Drupal node ID
    drupal_sync_status: DrupalSyncStatus = DrupalSyncStatus.NOT_SYNCED
    drupal_last_synced: Optional[datetime] = None
    drupal_error_message: Optional[str] = None

    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get issue ID as string"""
        return str(self._id) if self._id else None

    @property
    def is_synced(self) -> bool:
        """Check if issue is synced with Drupal"""
        return self.drupal_sync_status == DrupalSyncStatus.SYNCED and self.drupal_uuid is not None

    @property
    def needs_sync(self) -> bool:
        """Check if issue needs to be synced to Drupal"""
        return self.drupal_sync_status in [DrupalSyncStatus.NOT_SYNCED, DrupalSyncStatus.SYNC_FAILED]

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'title': self.title,
            'description': self.description,
            'impact': self.impact.value,
            'issue_type': self.issue_type,
            'location_on_page': self.location_on_page,
            'wcag_criteria': self.wcag_criteria,
            'xpath': self.xpath,
            'element': self.element,
            'html': self.html,
            'url': self.url,
            'recording_id': self.recording_id,
            'video_timecode': self.video_timecode,
            'what': self.what,
            'why': self.why,
            'who': self.who,
            'remediation': self.remediation,
            'project_id': self.project_id,
            'page_urls': self.page_urls,
            'page_ids': self.page_ids,
            'discovered_page_ids': self.discovered_page_ids,
            'component_names': self.component_names,
            'source_type': self.source_type,
            'detection_method': self.detection_method,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags,
            'drupal_issue_id': self.drupal_issue_id,
            'drupal_uuid': self.drupal_uuid,
            'drupal_nid': self.drupal_nid,
            'drupal_sync_status': self.drupal_sync_status.value,
            'drupal_last_synced': self.drupal_last_synced,
            'drupal_error_message': self.drupal_error_message
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Issue':
        """Create from dictionary"""
        # Handle ObjectId
        obj_id = data.get('_id')

        # Parse impact enum
        impact_value = data.get('impact', 'medium')
        # Map old impact levels for compatibility
        impact_mapping = {
            'critical': 'high',
            'serious': 'high',
            'moderate': 'medium',
            'minor': 'low'
        }
        if impact_value in impact_mapping:
            impact_value = impact_mapping[impact_value]
        impact = ImpactLevel(impact_value)

        return cls(
            title=data['title'],
            description=data['description'],
            impact=impact,
            issue_type=data.get('issue_type'),
            location_on_page=data.get('location_on_page'),
            wcag_criteria=data.get('wcag_criteria', []),
            xpath=data.get('xpath'),
            element=data.get('element'),
            html=data.get('html'),
            url=data.get('url'),
            recording_id=data.get('recording_id'),
            video_timecode=data.get('video_timecode'),
            what=data.get('what'),
            why=data.get('why'),
            who=data.get('who'),
            remediation=data.get('remediation'),
            project_id=data.get('project_id'),
            page_urls=data.get('page_urls', []),
            page_ids=data.get('page_ids', []),
            discovered_page_ids=data.get('discovered_page_ids', []),
            component_names=data.get('component_names', []),
            source_type=data.get('source_type', 'manual'),
            detection_method=data.get('detection_method'),
            status=data.get('status', 'open'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            tags=data.get('tags', []),
            drupal_issue_id=data.get('drupal_issue_id'),
            drupal_uuid=data.get('drupal_uuid'),
            drupal_nid=data.get('drupal_nid'),
            drupal_sync_status=DrupalSyncStatus(data.get('drupal_sync_status', 'not_synced')),
            drupal_last_synced=data.get('drupal_last_synced'),
            drupal_error_message=data.get('drupal_error_message'),
            _id=obj_id
        )

    @classmethod
    def from_recording_issue(cls, recording_issue: 'RecordingIssue') -> 'Issue':
        """
        Convert a RecordingIssue to an Issue for Drupal sync.

        Args:
            recording_issue: RecordingIssue instance

        Returns:
            Issue instance
        """
        # Combine the detailed fields into description
        description_parts = []
        if recording_issue.what:
            description_parts.append(f"<h3>What</h3><p>{recording_issue.what}</p>")
        if recording_issue.why:
            description_parts.append(f"<h3>Why</h3><p>{recording_issue.why}</p>")
        if recording_issue.who:
            description_parts.append(f"<h3>Who</h3><p>{recording_issue.who}</p>")
        if recording_issue.remediation:
            description_parts.append(f"<h3>Remediation</h3><p>{recording_issue.remediation}</p>")

        description = "\n".join(description_parts) if description_parts else recording_issue.what or ""

        # Convert timecodes to video_timecode string
        video_timecode = None
        if recording_issue.timecodes:
            timecode_strs = [f"{tc.start} - {tc.end}" for tc in recording_issue.timecodes]
            video_timecode = "; ".join(timecode_strs)

        # Extract WCAG criteria strings
        wcag_criteria = [w.criteria for w in recording_issue.wcag]

        return cls(
            title=recording_issue.title,
            description=description,
            impact=recording_issue.impact,
            issue_type=recording_issue.touchpoint,
            wcag_criteria=wcag_criteria,
            xpath=recording_issue.xpath,
            element=recording_issue.element,
            html=recording_issue.html,
            recording_id=recording_issue.recording_id,
            video_timecode=video_timecode,
            what=recording_issue.what,
            why=recording_issue.why,
            who=recording_issue.who,
            remediation=recording_issue.remediation,
            project_id=recording_issue.project_id,
            page_urls=recording_issue.page_urls,
            page_ids=recording_issue.page_ids,
            component_names=recording_issue.component_names,
            source_type="manual",
            detection_method="dictaphone",
            status=recording_issue.status,
            created_at=recording_issue.created_at,
            updated_at=recording_issue.updated_at,
            tags=recording_issue.tags
        )
