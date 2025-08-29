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
    MINOR = "minor"
    MODERATE = "moderate"
    SERIOUS = "serious"
    CRITICAL = "critical"


@dataclass
class Violation:
    """Accessibility violation"""
    
    id: str  # Error code
    impact: ImpactLevel
    category: str  # heading, image, form, etc.
    description: str
    help_url: Optional[str] = None
    xpath: Optional[str] = None
    element: Optional[str] = None
    html: Optional[str] = None
    failure_summary: Optional[str] = None
    wcag_criteria: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'impact': self.impact.value,
            'category': self.category,
            'description': self.description,
            'help_url': self.help_url,
            'xpath': self.xpath,
            'element': self.element,
            'html': self.html,
            'failure_summary': self.failure_summary,
            'wcag_criteria': self.wcag_criteria
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Violation':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            impact=ImpactLevel(data['impact']),
            category=data['category'],
            description=data['description'],
            help_url=data.get('help_url'),
            xpath=data.get('xpath'),
            element=data.get('element'),
            html=data.get('html'),
            failure_summary=data.get('failure_summary'),
            wcag_criteria=data.get('wcag_criteria', [])
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
        return cls(
            type=data['type'],
            severity=ImpactLevel(data['severity']),
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
            'critical': len([v for v in self.violations if v.impact == ImpactLevel.CRITICAL]),
            'serious': len([v for v in self.violations if v.impact == ImpactLevel.SERIOUS]),
            'moderate': len([v for v in self.violations if v.impact == ImpactLevel.MODERATE]),
            'minor': len([v for v in self.violations if v.impact == ImpactLevel.MINOR])
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
            'metadata': self.metadata
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
            _id=data.get('_id')
        )