"""
Page model for individual web pages
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
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


@dataclass
class Page:
    """Page model"""
    
    website_id: str
    url: str
    title: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)
    discovered_from: Optional[str] = None  # URL that linked to this page
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
            'error_reason': self.error_reason
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
            _id=data.get('_id')
        )