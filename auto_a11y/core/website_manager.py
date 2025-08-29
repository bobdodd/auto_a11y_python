"""
Website management business logic
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

from auto_a11y.models import Website, ScrapingConfig, Page, PageStatus
from auto_a11y.core.database import Database
from auto_a11y.core.scraper import ScrapingEngine, ScrapingJob

logger = logging.getLogger(__name__)


class WebsiteManager:
    """Manages website operations"""
    
    def __init__(self, database: Database, browser_config: Dict[str, Any]):
        """
        Initialize website manager
        
        Args:
            database: Database connection
            browser_config: Browser configuration
        """
        self.db = database
        self.browser_config = browser_config
        self.active_jobs: Dict[str, ScrapingJob] = {}
    
    def add_website(
        self,
        project_id: str,
        url: str,
        name: Optional[str] = None,
        scraping_config: Optional[ScrapingConfig] = None
    ) -> Website:
        """
        Add website to project
        
        Args:
            project_id: Project ID
            url: Website URL
            name: Optional display name
            scraping_config: Scraping configuration
            
        Returns:
            Created website
        """
        # Validate project exists
        project = self.db.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
        
        # Normalize URL - remove trailing slash for consistency
        if url.endswith('/') and len(parsed.path) <= 1:
            # Remove trailing slash from root URL
            url = url[:-1]
        
        # Check if website already exists in project
        existing = self.db.websites.find_one({
            'project_id': project_id,
            'url': url
        })
        if existing:
            raise ValueError(f"Website {url} already exists in project")
        
        # Create website
        website = Website(
            project_id=project_id,
            url=url,
            name=name or parsed.netloc,
            scraping_config=scraping_config or ScrapingConfig()
        )
        
        website_id = self.db.create_website(website)
        website._id = website_id
        
        logger.info(f"Added website: {url} to project {project_id}")
        return website
    
    def get_website(self, website_id: str) -> Optional[Website]:
        """
        Get website by ID
        
        Args:
            website_id: Website ID
            
        Returns:
            Website or None
        """
        return self.db.get_website(website_id)
    
    def list_websites(self, project_id: str) -> List[Website]:
        """
        List websites in project
        
        Args:
            project_id: Project ID
            
        Returns:
            List of websites
        """
        return self.db.get_websites(project_id)
    
    def update_website(
        self,
        website_id: str,
        url: Optional[str] = None,
        name: Optional[str] = None,
        scraping_config: Optional[ScrapingConfig] = None
    ) -> bool:
        """
        Update website details
        
        Args:
            website_id: Website ID
            url: New URL
            name: New name
            scraping_config: New scraping configuration
            
        Returns:
            True if updated successfully
        """
        website = self.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")
        
        # Update fields
        if url is not None:
            website.url = url
        if name is not None:
            website.name = name
        if scraping_config is not None:
            website.scraping_config = scraping_config
        
        return self.db.update_website(website)
    
    def delete_website(self, website_id: str) -> bool:
        """
        Delete website and all related data
        
        Args:
            website_id: Website ID
            
        Returns:
            True if deleted successfully
        """
        website = self.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")
        
        return self.db.delete_website(website_id)
    
    async def discover_pages(
        self,
        website_id: str,
        progress_callback: Optional[callable] = None
    ) -> ScrapingJob:
        """
        Start page discovery for website
        
        Args:
            website_id: Website ID
            progress_callback: Optional progress callback
            
        Returns:
            Scraping job
        """
        website = self.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")
        
        # Create job
        job_id = f"discovery_{website_id}_{datetime.now().timestamp()}"
        job = ScrapingJob(website_id, job_id)
        
        # Store job
        self.active_jobs[job_id] = job
        
        # Run discovery directly instead of creating a task
        # This ensures it completes within the event loop
        await self._run_discovery(job)
        
        logger.info(f"Completed discovery job {job_id} for website {website_id}")
        return job
    
    async def _run_discovery(self, job: ScrapingJob):
        """
        Run discovery job
        
        Args:
            job: Scraping job
        """
        try:
            await job.run(self.db, self.browser_config)
        finally:
            # Remove from active jobs when complete
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status or None
        """
        job = self.active_jobs.get(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'status': job.status,
            'progress': job.progress
        }
    
    def add_page_manually(
        self,
        website_id: str,
        url: str,
        priority: str = 'normal'
    ) -> Page:
        """
        Manually add a page to website
        
        Args:
            website_id: Website ID
            url: Page URL
            priority: Page priority
            
        Returns:
            Created page
        """
        website = self.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")
        
        # Check if page already exists
        existing = self.db.get_page_by_url(website_id, url)
        if existing:
            raise ValueError(f"Page {url} already exists")
        
        # Create page
        page = Page(
            website_id=website_id,
            url=url,
            discovered_from='manual',
            priority=priority,
            status=PageStatus.DISCOVERED
        )
        
        page_id = self.db.create_page(page)
        page._id = page_id
        
        logger.info(f"Manually added page: {url} to website {website_id}")
        return page
    
    def list_pages(
        self,
        website_id: str,
        status: Optional[PageStatus] = None,
        limit: int = 1000
    ) -> List[Page]:
        """
        List pages in website
        
        Args:
            website_id: Website ID
            status: Filter by status
            limit: Maximum number of pages
            
        Returns:
            List of pages
        """
        return self.db.get_pages(website_id, status=status, limit=limit)
    
    def get_website_statistics(self, website_id: str) -> Dict[str, Any]:
        """
        Get website statistics
        
        Args:
            website_id: Website ID
            
        Returns:
            Website statistics
        """
        website = self.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")
        
        pages = self.list_pages(website_id)
        
        tested_pages = [p for p in pages if p.status == PageStatus.TESTED]
        pages_with_issues = [p for p in pages if p.has_issues]
        
        return {
            'total_pages': len(pages),
            'tested_pages': len(tested_pages),
            'untested_pages': len(pages) - len(tested_pages),
            'pages_with_issues': len(pages_with_issues),
            'total_violations': sum(p.violation_count for p in pages),
            'total_warnings': sum(p.warning_count for p in pages),
            'test_coverage': (len(tested_pages) / len(pages) * 100) if pages else 0
        }


# Import asyncio here to avoid circular import
import asyncio