"""
Discovery Run model for versioning website discoveries
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from bson import ObjectId


class DiscoveryStatus(Enum):
    """Discovery run status"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DiscoveryRun:
    """Model for a single discovery/scraping session"""
    
    website_id: str
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: DiscoveryStatus = DiscoveryStatus.RUNNING
    
    # Discovery parameters used
    max_pages: int = 999999  # Effectively unlimited (1 million pages)
    max_depth: int = 10  # How many clicks away from the starting page
    follow_external: bool = False
    respect_robots: bool = True
    
    # Results
    pages_discovered: int = 0
    pages_failed: int = 0
    documents_found: int = 0
    external_links_found: int = 0
    
    # Comparison with previous run
    pages_added: int = 0  # New pages not in previous discovery
    pages_removed: int = 0  # Pages in previous but not current
    pages_unchanged: int = 0  # Pages found in both
    
    # Metadata
    triggered_by: Optional[str] = None  # User ID or "scheduled"
    job_id: Optional[str] = None  # Associated job ID
    error_message: Optional[str] = None
    duration_seconds: Optional[int] = None
    
    # Is this the latest discovery for the website?
    is_latest: bool = True
    
    _id: Optional[ObjectId] = None
    
    @property
    def id(self) -> str:
        """Get discovery run ID as string"""
        return str(self._id) if self._id else None
    
    @property
    def duration_display(self) -> str:
        """Get human-readable duration"""
        if not self.duration_seconds:
            if self.completed_at and self.started_at:
                self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
            else:
                return "Unknown"
        
        if self.duration_seconds < 60:
            return f"{self.duration_seconds}s"
        elif self.duration_seconds < 3600:
            return f"{self.duration_seconds // 60}m {self.duration_seconds % 60}s"
        else:
            hours = self.duration_seconds // 3600
            minutes = (self.duration_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB"""
        data = {
            'website_id': self.website_id,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'status': self.status.value,
            'max_pages': self.max_pages,
            'max_depth': self.max_depth,
            'follow_external': self.follow_external,
            'respect_robots': self.respect_robots,
            'pages_discovered': self.pages_discovered,
            'pages_failed': self.pages_failed,
            'documents_found': self.documents_found,
            'external_links_found': self.external_links_found,
            'pages_added': self.pages_added,
            'pages_removed': self.pages_removed,
            'pages_unchanged': self.pages_unchanged,
            'triggered_by': self.triggered_by,
            'job_id': self.job_id,
            'error_message': self.error_message,
            'duration_seconds': self.duration_seconds,
            'is_latest': self.is_latest
        }
        if self._id:
            data['_id'] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiscoveryRun':
        """Create from MongoDB document"""
        return cls(
            website_id=data['website_id'],
            started_at=data.get('started_at', datetime.now()),
            completed_at=data.get('completed_at'),
            status=DiscoveryStatus(data.get('status', 'running')),
            max_pages=data.get('max_pages', 999999),
            max_depth=data.get('max_depth', 10),
            follow_external=data.get('follow_external', False),
            respect_robots=data.get('respect_robots', True),
            pages_discovered=data.get('pages_discovered', 0),
            pages_failed=data.get('pages_failed', 0),
            documents_found=data.get('documents_found', 0),
            external_links_found=data.get('external_links_found', 0),
            pages_added=data.get('pages_added', 0),
            pages_removed=data.get('pages_removed', 0),
            pages_unchanged=data.get('pages_unchanged', 0),
            triggered_by=data.get('triggered_by'),
            job_id=data.get('job_id'),
            error_message=data.get('error_message'),
            duration_seconds=data.get('duration_seconds'),
            is_latest=data.get('is_latest', False),
            _id=data.get('_id')
        )