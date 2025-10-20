"""
Database-backed scraping job implementation
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from auto_a11y.core.job_manager import JobManager, JobType, JobStatus
from auto_a11y.core.database import Database

logger = logging.getLogger(__name__)


class ScrapingJob:
    """
    Represents a scraping job backed by database storage
    """
    
    def __init__(
        self,
        job_manager: JobManager,
        website_id: str,
        job_id: str,
        max_pages: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """
        Initialize scraping job
        
        Args:
            job_manager: JobManager instance
            website_id: Website ID
            job_id: Unique job ID
            max_pages: Optional override for max pages to discover
            user_id: User who initiated the job
            session_id: Session ID for tracking
        """
        self.job_manager = job_manager
        self.website_id = website_id
        self.job_id = job_id
        self.max_pages = max_pages
        self.user_id = user_id
        self.session_id = session_id
        
        # Create job in database
        logger.info(f"Creating job {job_id} in database...")
        try:
            self.job_doc = job_manager.create_job(
                job_id=job_id,
                job_type=JobType.DISCOVERY,
                website_id=website_id,
                user_id=user_id,
                session_id=session_id,
                metadata={
                    'max_pages': max_pages
                }
            )
            logger.info(f"Successfully created scraping job {job_id} in database for website {website_id}")
        except Exception as e:
            logger.error(f"Failed to create job {job_id} in database: {e}")
            raise
    
    def is_cancelled(self) -> bool:
        """
        Check if job is cancelled by querying database
        
        Returns:
            True if cancellation requested
        """
        return self.job_manager.is_cancellation_requested(self.job_id)
    
    def update_progress(
        self,
        pages_found: int,
        pages_processed: int,
        current_depth: int,
        message: str = None,
        queue_size: int = 0
    ):
        """
        Update job progress in database
        
        Args:
            pages_found: Number of pages found
            pages_processed: Number of pages processed
            current_depth: Current crawl depth
            message: Optional status message
            queue_size: Number of URLs in queue
        """
        if not message:
            message = f"Found {pages_found} pages, processed {pages_processed}"
        
        self.job_manager.update_job_progress(
            job_id=self.job_id,
            current=pages_processed,
            total=self.max_pages or pages_found,
            message=message,
            details={
                'pages_found': pages_found,
                'pages_processed': pages_processed,
                'current_depth': current_depth,
                'queue_size': queue_size
            }
        )
    
    def set_running(self):
        """Mark job as running"""
        self.job_manager.update_job_status(
            job_id=self.job_id,
            status=JobStatus.RUNNING,
            progress={
                'current': 0,
                'total': self.max_pages or 0,
                'message': 'Discovery started',
                'details': {}
            }
        )
        logger.info(f"Scraping job {self.job_id} marked as running")
    
    def set_completed(self, pages_found: int, pages_processed: int):
        """
        Mark job as completed
        
        Args:
            pages_found: Total pages found
            pages_processed: Total pages processed
        """
        self.job_manager.update_job_status(
            job_id=self.job_id,
            status=JobStatus.COMPLETED,
            progress={
                'current': pages_processed,
                'total': pages_found,
                'message': f'Discovery completed: {pages_found} pages found',
                'details': {
                    'pages_found': pages_found,
                    'pages_processed': pages_processed
                }
            },
            result={
                'pages_found': pages_found,
                'pages_processed': pages_processed,
                'completed_at': datetime.now().isoformat()
            }
        )
        logger.info(f"Scraping job {self.job_id} completed: {pages_found} pages found")
    
    def set_failed(self, error: str):
        """
        Mark job as failed
        
        Args:
            error: Error message
        """
        self.job_manager.update_job_status(
            job_id=self.job_id,
            status=JobStatus.FAILED,
            error=error
        )
        logger.error(f"Scraping job {self.job_id} failed: {error}")
    
    def set_cancelled(self):
        """Mark job as cancelled"""
        job = self.job_manager.get_job(self.job_id)
        if job:
            pages_found = job.get('progress', {}).get('details', {}).get('pages_found', 0)
            pages_processed = job.get('progress', {}).get('details', {}).get('pages_processed', 0)
            
            self.job_manager.update_job_status(
                job_id=self.job_id,
                status=JobStatus.CANCELLED,
                progress={
                    'current': pages_processed,
                    'total': pages_found,
                    'message': 'Discovery cancelled by user',
                    'details': {
                        'pages_found': pages_found,
                        'pages_processed': pages_processed
                    }
                }
            )
            logger.info(f"Scraping job {self.job_id} cancelled")
    
    async def run(self, database: Database, browser_config: Dict[str, Any]):
        """
        Run the scraping job
        
        Args:
            database: Database instance
            browser_config: Browser configuration
        """
        from auto_a11y.core.scraper import ScrapingEngine
        
        logger.info(f"ScrapingJob.run started for job {self.job_id}")
        
        try:
            # Mark as running
            self.set_running()
            logger.info(f"Job {self.job_id} marked as running")
            
            # Get website
            website = database.get_website(self.website_id)
            logger.info(f"Got website {self.website_id}: {website.url if website else 'None'}")
            if not website:
                raise ValueError(f"Website {self.website_id} not found")
            
            # Create scraper
            scraper = ScrapingEngine(database, browser_config)
            
            # Apply max_pages override if provided
            if self.max_pages is not None and self.max_pages > 0:
                logger.info(f"Applying max_pages override: {self.max_pages} (was {website.scraping_config.max_pages})")
                website.scraping_config.max_pages = self.max_pages
            
            # Run discovery with progress callback
            pages = await scraper.discover_website(
                website=website,
                progress_callback=self._update_progress,
                job=self  # Pass self so scraper can check cancellation
            )
            
            # Check final cancellation status
            if self.is_cancelled():
                logger.info(f"Discovery job {self.job_id} was cancelled")
                self.set_cancelled()
            else:
                # Mark as completed
                pages_found = len(pages) if pages else 0
                self.set_completed(pages_found, pages_found)

        except Exception as e:
            logger.error(f"Discovery job {self.job_id} failed: {e}")
            self.set_failed(str(e))
            raise
        finally:
            # Clean up browser resources
            if scraper:
                await scraper.cleanup()
    
    async def _update_progress(self, progress: dict):
        """Update job progress in database"""
        logger.debug(f"ScrapingJob._update_progress called with: {progress}")
        
        # Update database with progress
        pages_found = progress.get('pages_found', 0)
        current_url = progress.get('current_url', '')
        
        try:
            self.update_progress(
                pages_found=pages_found,
                pages_processed=pages_found,  # For discovery, processed = found
                current_depth=progress.get('current_depth', 0),
                message=current_url,
                queue_size=progress.get('queue_size', 0)
            )
            logger.debug(f"ScrapingJob progress updated successfully for {pages_found} pages")
        except Exception as e:
            logger.error(f"Failed to update progress: {e}", exc_info=True)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current job status from database
        
        Returns:
            Job status dictionary
        """
        job = self.job_manager.get_job(self.job_id)
        if not job:
            return {
                'status': 'unknown',
                'message': 'Job not found'
            }
        
        return {
            'job_id': job['job_id'],
            'status': job['status'],
            'progress': job.get('progress', {}),
            'error': job.get('error'),
            'created_at': job.get('created_at'),
            'started_at': job.get('started_at'),
            'completed_at': job.get('completed_at')
        }