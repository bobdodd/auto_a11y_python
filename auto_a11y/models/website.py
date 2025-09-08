"""
Website model for managing sites within projects
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId


@dataclass
class ScrapingConfig:
    """Configuration for website scraping"""
    max_pages: int = 500
    max_depth: int = 3
    follow_external: bool = False
    include_subdomains: bool = True
    respect_robots: bool = True
    request_delay: float = 1.0
    allowed_paths: List[str] = field(default_factory=list)
    excluded_paths: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'max_pages': self.max_pages,
            'max_depth': self.max_depth,
            'follow_external': self.follow_external,
            'include_subdomains': self.include_subdomains,
            'respect_robots': self.respect_robots,
            'request_delay': self.request_delay,
            'allowed_paths': self.allowed_paths,
            'excluded_paths': self.excluded_paths
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScrapingConfig':
        """Create from dictionary"""
        return cls(**data) if data else cls()


@dataclass
class Website:
    """Website model"""
    
    project_id: str
    url: str
    name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_scraped: Optional[datetime] = None
    last_tested: Optional[datetime] = None
    page_count: int = 0
    scraping_config: ScrapingConfig = field(default_factory=ScrapingConfig)
    discovery_history: List[Dict[str, Any]] = field(default_factory=list)  # Track all discovery attempts
    _id: Optional[ObjectId] = None
    
    @property
    def id(self) -> str:
        """Get website ID as string"""
        return str(self._id) if self._id else None
    
    @property
    def display_name(self) -> str:
        """Get display name (name or URL)"""
        return self.name or self.url
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'project_id': self.project_id,
            'url': self.url,
            'name': self.name,
            'created_at': self.created_at,
            'last_scraped': self.last_scraped,
            'last_tested': self.last_tested,
            'page_count': self.page_count,
            'scraping_config': self.scraping_config.to_dict()
        }
        if self._id:
            data['_id'] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Website':
        """Create from MongoDB document"""
        return cls(
            project_id=data['project_id'],
            url=data['url'],
            name=data.get('name'),
            created_at=data.get('created_at', datetime.now()),
            last_scraped=data.get('last_scraped'),
            last_tested=data.get('last_tested'),
            page_count=data.get('page_count', 0),
            scraping_config=ScrapingConfig.from_dict(data.get('scraping_config', {})),
            discovery_history=data.get('discovery_history', []),
            _id=data.get('_id')
        )