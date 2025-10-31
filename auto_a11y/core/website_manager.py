"""
Website management business logic
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

from auto_a11y.models import Website, ScrapingConfig, Page, PageStatus
from auto_a11y.core.database import Database
from auto_a11y.core.scraper import ScrapingEngine
from auto_a11y.core.scraping_job import ScrapingJob
from auto_a11y.core.testing_job import TestingJob
from auto_a11y.core.job_manager import JobManager, JobType

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
        # Initialize job manager for database-backed job tracking
        self.job_manager = JobManager(database)
    
    def cancel_testing(self, job_id: str, user_id: Optional[str] = None) -> bool:
        """
        Cancel a testing job
        
        Args:
            job_id: Job ID to cancel
            user_id: User requesting cancellation
            
        Returns:
            True if cancelled, False if not found
        """
        logger.info(f"WebsiteManager.cancel_testing called for job {job_id} by user {user_id}")
        
        # Check if job exists
        job = self.job_manager.get_job(job_id)
        if not job:
            logger.error(f"Testing job {job_id} not found in database")
            return False
        
        logger.info(f"Found testing job {job_id} with status: {job.get('status')}")
        
        # Request cancellation
        success = self.job_manager.request_cancellation(job_id, requested_by=user_id)
        if success:
            logger.info(f"Successfully requested cancellation for testing job {job_id}")
        else:
            logger.warning(f"Could not cancel testing job {job_id} - may already be completed or cancelled")
        return success
    
    def cancel_discovery(self, job_id: str, user_id: Optional[str] = None) -> bool:
        """
        Cancel a discovery job
        
        Args:
            job_id: Job ID to cancel
            user_id: User requesting cancellation
            
        Returns:
            True if cancelled, False if not found
        """
        logger.info(f"WebsiteManager.cancel_discovery called")
        logger.info(f"  Attempting to cancel job_id: '{job_id}'")
        logger.info(f"  Requested by user: {user_id}")
        
        # Log all discovery jobs in database for debugging
        all_discovery_jobs = self.job_manager.get_active_jobs(job_type=JobType.DISCOVERY)
        logger.info(f"  Active discovery jobs in database: {len(all_discovery_jobs)}")
        for job in all_discovery_jobs:
            logger.info(f"    - Job ID: '{job.get('job_id')}' Status: {job.get('status')}")
        
        # First check if job exists
        job = self.job_manager.get_job(job_id)
        if not job:
            logger.error(f"Job '{job_id}' not found in database")
            
            # Try to find similar job IDs
            all_jobs = self.job_manager.collection.find({'job_type': JobType.DISCOVERY.value}, {'job_id': 1}).limit(10)
            logger.error(f"  Recent discovery job IDs in DB:")
            for j in all_jobs:
                logger.error(f"    - '{j.get('job_id')}'")
            
            return False
        
        logger.info(f"Found job {job_id} with status: {job.get('status')}")
        
        # Request cancellation
        success = self.job_manager.request_cancellation(job_id, requested_by=user_id)
        if success:
            logger.info(f"Successfully requested cancellation for job {job_id}")
        else:
            logger.warning(f"Could not cancel job {job_id} - may already be completed or cancelled")
        return success
    
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
        max_pages: Optional[int] = None,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ScrapingJob:
        """
        Start page discovery for website
        
        Args:
            website_id: Website ID
            max_pages: Optional maximum number of pages to discover
            job_id: Optional job ID
            user_id: User initiating discovery
            session_id: Session ID for tracking
            
        Returns:
            Scraping job
        """
        website = self.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")
        
        # Log max_pages setting
        if max_pages is not None and max_pages > 0:
            logger.info(f"Discovery will be limited to {max_pages} pages")
        else:
            logger.info(f"Using default max_pages: {website.scraping_config.max_pages}")
        
        # Create job with database backing
        if not job_id:
            job_id = f"discovery_{website_id}_{datetime.now().timestamp()}"
        
        logger.info(f"Creating ScrapingJob with job_id: {job_id}")
        
        try:
            job = ScrapingJob(
                job_manager=self.job_manager,
                website_id=website_id,
                job_id=job_id,
                max_pages=max_pages,
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"ScrapingJob created successfully: {job_id}")
        except Exception as e:
            logger.error(f"Failed to create ScrapingJob: {e}")
            raise
        
        # Run discovery
        logger.info(f"Starting job.run for {job_id}")
        await job.run(self.db, self.browser_config)
        logger.info(f"job.run completed for {job_id}")
        
        logger.info(f"Completed discovery job {job_id} for website {website_id}")
        return job
    
    # _run_discovery method removed - now handled by ScrapingJob.run()
    
    async def test_website(
        self,
        website_id: str,
        page_ids: Optional[List[str]] = None,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        test_all: bool = False,
        take_screenshot: bool = True,
        run_ai_analysis: Optional[bool] = None,
        ai_api_key: Optional[str] = None,
        website_user_id: Optional[str] = None
    ) -> TestingJob:
        """
        Start testing for website pages

        Args:
            website_id: Website ID
            page_ids: Specific page IDs to test (if not test_all)
            job_id: Optional job ID
            user_id: User initiating testing
            session_id: Session ID for tracking
            test_all: Whether to test all pages
            take_screenshot: Whether to take screenshots
            run_ai_analysis: Whether to run AI analysis
            ai_api_key: API key for AI analysis
            website_user_id: Optional WebsiteUser ID for authenticated testing

        Returns:
            Testing job
        """
        website = self.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")
        
        # Create job with database backing
        if not job_id:
            import uuid
            job_id = f"testing_{website_id}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Creating TestingJob with job_id: {job_id}")
        
        try:
            job = TestingJob(
                job_manager=self.job_manager,
                website_id=website_id,
                job_id=job_id,
                page_ids=page_ids,
                user_id=user_id,
                session_id=session_id,
                test_all=test_all,
                website_user_id=website_user_id
            )
            logger.info(f"TestingJob created successfully: {job_id}")
        except Exception as e:
            logger.error(f"Failed to create TestingJob: {e}")
            raise
        
        # Run testing
        logger.info(f"Starting testing job.run for {job_id}")
        await job.run(
            self.db,
            self.browser_config,
            take_screenshot=take_screenshot,
            run_ai_analysis=run_ai_analysis,
            ai_api_key=ai_api_key
        )
        logger.info(f"Testing job.run completed for {job_id}")
        
        logger.info(f"Completed testing job {job_id} for website {website_id}")
        return job
    
    async def test_project(
        self,
        project_id: str,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        test_all: bool = True,
        take_screenshot: bool = True,
        run_ai_analysis: Optional[bool] = None,
        ai_api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Test all websites in a project
        
        Args:
            project_id: Project ID to test
            job_id: Optional job ID prefix
            user_id: User who initiated the test
            session_id: Session ID for tracking
            test_all: Test all pages or just untested ones
            take_screenshot: Whether to take screenshots
            run_ai_analysis: Whether to run AI analysis
            ai_api_key: OpenAI API key for AI analysis
            
        Returns:
            List of job results for each website
        """
        logger.info(f"Starting project-level testing for project {project_id}")
        
        # Get project and its websites
        project = self.db.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        websites = self.db.get_websites(project_id)
        if not websites:
            logger.warning(f"No websites found for project {project_id}")
            return []
        
        # Create jobs for each website
        jobs = []
        for i, website in enumerate(websites):
            website_job_id = f"{job_id or 'proj-test'}_{i}_{website.id}" if job_id else None
            
            try:
                logger.info(f"Starting test for website {website.name} ({website.url})")
                
                # Get pages to test
                if test_all:
                    pages = self.db.get_pages(website.id)
                else:
                    pages = self.db.get_untested_pages(website.id)
                
                if not pages:
                    logger.info(f"No pages to test for website {website.id}")
                    continue
                
                page_ids = [p.id for p in pages]
                
                # Start async test for this website
                job = await self.test_website(
                    website_id=website.id,
                    page_ids=page_ids,
                    job_id=website_job_id,
                    user_id=user_id,
                    session_id=session_id,
                    test_all=test_all,
                    take_screenshot=take_screenshot,
                    run_ai_analysis=run_ai_analysis,
                    ai_api_key=ai_api_key
                )
                
                jobs.append({
                    'website_id': website.id,
                    'website_name': website.name,
                    'website_url': website.url,
                    'job_id': job.job_id,
                    'pages_tested': len(page_ids)
                })
                
            except Exception as e:
                logger.error(f"Failed to test website {website.id}: {e}")
                jobs.append({
                    'website_id': website.id,
                    'website_name': website.name,
                    'website_url': website.url,
                    'error': str(e)
                })
        
        logger.info(f"Completed project testing for {project_id} with {len(jobs)} website jobs")
        return jobs
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status from database
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status or None
        """
        job = self.job_manager.get_job(job_id)
        if not job:
            return None
        
        return {
            'job_id': job['job_id'],
            'status': job['status'],
            'progress': job.get('progress', {}),
            'error': job.get('error'),
            'created_at': job.get('created_at'),
            'started_at': job.get('started_at'),
            'completed_at': job.get('completed_at')
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