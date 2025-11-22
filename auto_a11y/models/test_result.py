"""
Test result models for accessibility testing
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from bson import ObjectId


class ImpactLevel(Enum):
    """Impact level for violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Violation:
    """
    Unified accessibility violation model.
    Supports both automated test findings and manual audit findings.
    """

    # Core fields (required for all violations)
    id: str  # Error code (e.g., "color-contrast") - NOT unique per instance
    impact: ImpactLevel
    touchpoint: str  # Accessibility category (e.g., "Images", "Forms")
    description: str

    # Unique identifier for this specific violation instance
    unique_id: Optional[str] = None  # UUID for this specific instance (generated if not provided)

    # Source tracking (NEW)
    source_type: str = "automated"  # "automated", "manual", "hybrid"
    detection_method: Optional[str] = None  # "axe", "pa11y", "dictaphone", "expert"

    # Automated test fields (may be None for manual findings)
    help_url: Optional[str] = None
    xpath: Optional[str] = None
    element: Optional[str] = None
    html: Optional[str] = None
    failure_summary: Optional[str] = None
    wcag_criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional details

    # Manual audit fields (NEW - from Dictaphone/expert audits)
    short_title: Optional[str] = None
    what: Optional[str] = None  # Detailed issue description
    why: Optional[str] = None  # Why it matters / impact explanation
    who: Optional[str] = None  # Affected user groups
    remediation: Optional[str] = None  # How to fix

    # Recording context (NEW - for manual findings)
    recording_id: Optional[str] = None
    timecodes: List[Dict[str, str]] = field(default_factory=list)
    # timecode format: [{"start": "00:00:56.085", "end": "00:01:19.265", "duration": "00:00:23.180"}]

    # Discovered Page reference (for linking to Drupal discovered pages)
    discovered_page_id: Optional[str] = None  # Local MongoDB discovered_page ID

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        import uuid
        # Generate unique_id if not set
        if not self.unique_id:
            self.unique_id = str(uuid.uuid4())

        return {
            'id': self.id,
            'unique_id': self.unique_id,
            'impact': self.impact.value,
            'touchpoint': self.touchpoint,
            'description': self.description,
            'source_type': self.source_type,
            'detection_method': self.detection_method,
            'help_url': self.help_url,
            'xpath': self.xpath,
            'element': self.element,
            'html': self.html,
            'failure_summary': self.failure_summary,
            'wcag_criteria': self.wcag_criteria,
            'metadata': self.metadata,
            'short_title': self.short_title,
            'what': self.what,
            'why': self.why,
            'who': self.who,
            'remediation': self.remediation,
            'recording_id': self.recording_id,
            'timecodes': self.timecodes,
            'discovered_page_id': self.discovered_page_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Violation':
        """Create from dictionary"""
        # Map old impact levels to new ones for backward compatibility
        impact_mapping = {
            'critical': 'high',
            'serious': 'high',
            'moderate': 'medium',
            'minor': 'low'
        }

        impact_value = data['impact']
        # If it's an old value, map it to the new one
        if impact_value in impact_mapping:
            impact_value = impact_mapping[impact_value]

        # Handle both old 'category' and new 'touchpoint' field names
        touchpoint = data.get('touchpoint', data.get('category', ''))

        import uuid
        # Generate unique_id if not present (for backward compatibility with old data)
        unique_id = data.get('unique_id')
        if not unique_id:
            unique_id = str(uuid.uuid4())

        return cls(
            id=data['id'],
            unique_id=unique_id,
            impact=ImpactLevel(impact_value),
            touchpoint=touchpoint,
            description=data['description'],
            source_type=data.get('source_type', 'automated'),
            detection_method=data.get('detection_method'),
            help_url=data.get('help_url'),
            xpath=data.get('xpath'),
            element=data.get('element'),
            html=data.get('html'),
            failure_summary=data.get('failure_summary'),
            wcag_criteria=data.get('wcag_criteria', []),
            metadata=data.get('metadata', {}),
            short_title=data.get('short_title'),
            what=data.get('what'),
            why=data.get('why'),
            who=data.get('who'),
            remediation=data.get('remediation'),
            recording_id=data.get('recording_id'),
            timecodes=data.get('timecodes', []),
            discovered_page_id=data.get('discovered_page_id')
        )


@dataclass
class AIFinding:
    """AI-detected accessibility finding"""
    
    type: str  # heading_mismatch, reading_order, modal_issue, etc.
    severity: ImpactLevel
    description: str
    suggested_fix: Optional[str] = None
    confidence: float = 0.0
    visual_location: Optional[Dict[str, int]] = None  # x, y, width, height
    related_html: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'type': self.type,
            'severity': self.severity.value,
            'description': self.description,
            'suggested_fix': self.suggested_fix,
            'confidence': self.confidence,
            'visual_location': self.visual_location,
            'related_html': self.related_html
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AIFinding':
        """Create from dictionary"""
        # Map old impact levels to new ones for backward compatibility
        impact_mapping = {
            'critical': 'high',
            'serious': 'high',
            'moderate': 'medium',
            'minor': 'low'
        }
        
        severity_value = data['severity']
        # If it's an old value, map it to the new one
        if severity_value in impact_mapping:
            severity_value = impact_mapping[severity_value]
        
        return cls(
            type=data['type'],
            severity=ImpactLevel(severity_value),
            description=data['description'],
            suggested_fix=data.get('suggested_fix'),
            confidence=data.get('confidence', 0.0),
            visual_location=data.get('visual_location'),
            related_html=data.get('related_html')
        )


@dataclass
class TestResult:
    """Complete test result for a page"""

    page_id: str
    test_date: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0
    violations: List[Violation] = field(default_factory=list)  # Errors (_Err)
    warnings: List[Violation] = field(default_factory=list)   # Warnings (_Warn)
    info: List[Violation] = field(default_factory=list)       # Information notes (_Info)
    discovery: List[Violation] = field(default_factory=list)  # Discovery items (_Disco)
    passes: List[Dict[str, Any]] = field(default_factory=list)
    ai_findings: List[AIFinding] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    js_test_results: Dict[str, Any] = field(default_factory=dict)
    ai_analysis_results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # NEW: Multi-state testing fields
    page_state: Optional[Dict[str, Any]] = None  # PageTestState as dict
    state_sequence: int = 0  # 0=initial, 1=after first script, 2=after button A, etc.
    session_id: Optional[str] = None  # Reference to script_execution_sessions
    related_result_ids: List[str] = field(default_factory=list)  # Other results for same page/session

    _id: Optional[ObjectId] = None
    
    @property
    def id(self) -> str:
        """Get result ID as string"""
        return str(self._id) if self._id else None
    
    @property
    def violation_count(self) -> int:
        """Get total violation count"""
        return len(self.violations)
    
    @property
    def warning_count(self) -> int:
        """Get total warning count"""
        return len(self.warnings)
    
    @property
    def info_count(self) -> int:
        """Get total info count"""
        return len(self.info)
    
    @property
    def discovery_count(self) -> int:
        """Get total discovery count"""
        return len(self.discovery)
    
    @property
    def pass_count(self) -> int:
        """Get total pass count"""
        return len(self.passes)
    
    @property
    def score(self) -> Dict[str, int]:
        """Get accessibility score summary"""
        return {
            'violations': self.violation_count,
            'warnings': self.warning_count,
            'info': self.info_count,
            'discovery': self.discovery_count,
            'passes': self.pass_count,
            'ai_findings': len(self.ai_findings),
            'high': len([v for v in self.violations if v.impact == ImpactLevel.HIGH]),
            'medium': len([v for v in self.violations if v.impact == ImpactLevel.MEDIUM]),
            'low': len([v for v in self.violations if v.impact == ImpactLevel.LOW])
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'page_id': self.page_id,
            'test_date': self.test_date,
            'duration_ms': self.duration_ms,
            'violations': [v.to_dict() for v in self.violations],
            'warnings': [w.to_dict() for w in self.warnings],
            'info': [i.to_dict() for i in self.info],
            'discovery': [d.to_dict() for d in self.discovery],
            'passes': self.passes,
            'ai_findings': [f.to_dict() for f in self.ai_findings],
            'screenshot_path': self.screenshot_path,
            'js_test_results': self.js_test_results,
            'ai_analysis_results': self.ai_analysis_results,
            'error': self.error,
            'metadata': self.metadata,
            # Multi-state testing fields
            'page_state': self.page_state,
            'state_sequence': self.state_sequence,
            'session_id': self.session_id,
            'related_result_ids': self.related_result_ids
        }
        if self._id:
            data['_id'] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TestResult':
        """Create from MongoDB document"""
        return cls(
            page_id=data['page_id'],
            test_date=data.get('test_date', datetime.now()),
            duration_ms=data.get('duration_ms', 0),
            violations=[Violation.from_dict(v) for v in data.get('violations', [])],
            warnings=[Violation.from_dict(w) for w in data.get('warnings', [])],
            info=[Violation.from_dict(i) for i in data.get('info', [])],
            discovery=[Violation.from_dict(d) for d in data.get('discovery', [])],
            passes=data.get('passes', []),
            ai_findings=[AIFinding.from_dict(f) for f in data.get('ai_findings', [])],
            screenshot_path=data.get('screenshot_path'),
            js_test_results=data.get('js_test_results', {}),
            ai_analysis_results=data.get('ai_analysis_results', {}),
            error=data.get('error'),
            metadata=data.get('metadata', {}),
            # Multi-state testing fields (defaults for backward compatibility)
            page_state=data.get('page_state'),
            state_sequence=data.get('state_sequence', 0),
            session_id=data.get('session_id'),
            related_result_ids=data.get('related_result_ids', []),
            _id=data.get('_id')
        )