"""
Recording issue model for accessibility findings from manual audits
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from auto_a11y.models.test_result import ImpactLevel
from auto_a11y.models.recording import Timecode, WCAGReference


@dataclass
class RecordingIssue:
    """
    Accessibility issue identified in a recording (Dictaphone or manual audit).
    Represents a single accessibility finding from human testing/auditing.
    """

    # Core identification
    recording_id: str  # Link to Recording.recording_id
    title: str
    short_title: Optional[str] = None

    # Issue details (Dictaphone format)
    what: str = ""  # Description of the issue
    why: str = ""  # Why it matters / impact explanation
    who: str = ""  # Affected user groups
    remediation: str = ""  # How to fix

    # Classification
    impact: ImpactLevel = ImpactLevel.MEDIUM
    touchpoint: Optional[str] = None  # Accessibility category

    # Timecode references
    timecodes: List[Timecode] = field(default_factory=list)

    # WCAG references
    wcag: List[WCAGReference] = field(default_factory=list)

    # Optional technical details (if issue can be mapped to specific elements)
    xpath: Optional[str] = None
    element: Optional[str] = None
    html: Optional[str] = None

    # Relationships
    project_id: Optional[str] = None

    # Component/Section references (same as Recording model)
    website_ids: List[str] = field(default_factory=list)  # Specific websites
    page_urls: List[str] = field(default_factory=list)  # Specific page URLs where issue occurs
    page_ids: List[str] = field(default_factory=list)  # Specific page IDs
    component_names: List[str] = field(default_factory=list)  # Common components affected
    app_screens: List[str] = field(default_factory=list)  # App screens where issue occurs
    device_sections: List[str] = field(default_factory=list)  # Device sections affected

    # Task context
    task_description: Optional[str] = None  # Task being performed when issue encountered

    # Status tracking
    status: str = "open"  # open, in_progress, resolved, verified
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get issue ID as string"""
        return str(self._id) if self._id else None

    @property
    def wcag_criteria(self) -> List[str]:
        """Get list of WCAG criteria strings for compatibility"""
        return [w.criteria for w in self.wcag]

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'recording_id': self.recording_id,
            'title': self.title,
            'short_title': self.short_title,
            'what': self.what,
            'why': self.why,
            'who': self.who,
            'remediation': self.remediation,
            'impact': self.impact.value,
            'touchpoint': self.touchpoint,
            'timecodes': [tc.to_dict() for tc in self.timecodes],
            'wcag': [w.to_dict() for w in self.wcag],
            'xpath': self.xpath,
            'element': self.element,
            'html': self.html,
            'project_id': self.project_id,
            'website_ids': self.website_ids,
            'page_urls': self.page_urls,
            'page_ids': self.page_ids,
            'component_names': self.component_names,
            'app_screens': self.app_screens,
            'device_sections': self.device_sections,
            'task_description': self.task_description,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'resolution_notes': self.resolution_notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'RecordingIssue':
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

        # Parse timecodes
        timecodes = [
            Timecode.from_dict(tc) for tc in data.get('timecodes', [])
        ]

        # Parse WCAG references
        wcag = [
            WCAGReference.from_dict(w) for w in data.get('wcag', [])
        ]

        return cls(
            recording_id=data['recording_id'],
            title=data['title'],
            short_title=data.get('short_title'),
            what=data.get('what', ''),
            why=data.get('why', ''),
            who=data.get('who', ''),
            remediation=data.get('remediation', ''),
            impact=impact,
            touchpoint=data.get('touchpoint'),
            timecodes=timecodes,
            wcag=wcag,
            xpath=data.get('xpath'),
            element=data.get('element'),
            html=data.get('html'),
            project_id=data.get('project_id'),
            website_ids=data.get('website_ids', []),
            page_urls=data.get('page_urls', []),
            page_ids=data.get('page_ids', []),
            component_names=data.get('component_names', []),
            app_screens=data.get('app_screens', []),
            device_sections=data.get('device_sections', []),
            task_description=data.get('task_description'),
            status=data.get('status', 'open'),
            assigned_to=data.get('assigned_to'),
            resolution_notes=data.get('resolution_notes'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            tags=data.get('tags', []),
            _id=obj_id
        )

    @classmethod
    def from_dictaphone_issue(
        cls,
        issue_data: dict,
        recording_id: str,
        project_id: Optional[str] = None
    ) -> 'RecordingIssue':
        """
        Create RecordingIssue from Dictaphone JSON issue format

        Args:
            issue_data: Issue dict from Dictaphone JSON
            recording_id: ID of the recording this issue belongs to
            project_id: Optional project ID to link to

        Returns:
            RecordingIssue instance
        """
        # Parse timecodes
        timecodes = [
            Timecode(
                start=tc['start'],
                end=tc['end'],
                duration=tc['duration']
            )
            for tc in issue_data.get('timecodes', [])
        ]

        # Parse WCAG references
        wcag_refs = [
            WCAGReference(
                criteria=w['criteria'],
                level=w['level'],
                versions=w.get('versions', [])
            )
            for w in issue_data.get('wcag', [])
        ]

        # Map impact
        impact_str = issue_data.get('impact', 'medium').lower()
        impact_mapping = {
            'low': ImpactLevel.LOW,
            'medium': ImpactLevel.MEDIUM,
            'moderate': ImpactLevel.MEDIUM,
            'high': ImpactLevel.HIGH,
            'critical': ImpactLevel.HIGH
        }
        impact = impact_mapping.get(impact_str, ImpactLevel.MEDIUM)

        return cls(
            recording_id=recording_id,
            title=issue_data['title'],
            short_title=issue_data.get('short_title'),
            what=issue_data.get('what', ''),
            why=issue_data.get('why', ''),
            who=issue_data.get('who', ''),
            remediation=issue_data.get('remediation', ''),
            impact=impact,
            timecodes=timecodes,
            wcag=wcag_refs,
            project_id=project_id
        )
