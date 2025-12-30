"""
Database-backed testing job implementation
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from auto_a11y.core.job_manager import JobManager, JobType, JobStatus
from auto_a11y.core.database import Database
from auto_a11y.models import Page, PageStatus

logger = logging.getLogger(__name__)


class TestingJob:
    """
    Represents a testing job backed by database storage
    """
    
    def __init__(
        self,
        job_manager: JobManager,
        website_id: str,
        job_id: str,
        page_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        test_all: bool = False,
        website_user_id: Optional[str] = None
    ):
        """
        Initialize testing job

        Args:
            job_manager: JobManager instance
            website_id: Website ID
            job_id: Unique job ID
            page_ids: List of specific page IDs to test (if not test_all)
            user_id: User who initiated the job
            session_id: Session ID for tracking
            test_all: Whether to test all pages in the website
            website_user_id: Optional WebsiteUser ID for authenticated testing
        """
        self.job_manager = job_manager
        self.website_id = website_id
        self.job_id = job_id
        self.page_ids = page_ids or []
        self.user_id = user_id
        self.session_id = session_id
        self.test_all = test_all
        self.website_user_id = website_user_id
        
        # Create job in database
        logger.info(f"Creating testing job {job_id} in database...")
        try:
            self.job_doc = job_manager.create_job(
                job_id=job_id,
                job_type=JobType.TESTING,
                website_id=website_id,
                user_id=user_id,
                session_id=session_id,
                metadata={
                    'page_ids': page_ids,
                    'test_all': test_all,
                    'total_pages': len(page_ids) if page_ids else 0,
                    'website_user_id': website_user_id
                }
            )
            logger.info(f"Successfully created testing job {job_id} in database for website {website_id}")
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
        pages_tested: int,
        total_pages: int,
        current_page: Optional[str] = None,
        message: str = None,
        pages_passed: int = 0,
        pages_failed: int = 0,
        pages_skipped: int = 0
    ):
        """
        Update job progress in database
        
        Args:
            pages_tested: Number of pages tested
            total_pages: Total number of pages to test
            current_page: URL of current page being tested
            message: Optional status message
            pages_passed: Number of pages that passed
            pages_failed: Number of pages that failed
            pages_skipped: Number of pages skipped
        """
        if not message:
            message = f"Tested {pages_tested}/{total_pages} pages"
            if current_page:
                message += f" - Current: {current_page}"
        
        self.job_manager.update_job_progress(
            job_id=self.job_id,
            current=pages_tested,
            total=total_pages,
            message=message,
            details={
                'pages_tested': pages_tested,
                'pages_passed': pages_passed,
                'pages_failed': pages_failed,
                'pages_skipped': pages_skipped,
                'total_pages': total_pages,
                'current_page': current_page
            }
        )
    
    def set_running(self, total_pages: int):
        """
        Mark job as running
        
        Args:
            total_pages: Total number of pages to test
        """
        self.job_manager.update_job_status(
            job_id=self.job_id,
            status=JobStatus.RUNNING,
            progress={
                'current': 0,
                'total': total_pages,
                'message': 'Testing started',
                'details': {
                    'pages_tested': 0,
                    'pages_passed': 0,
                    'pages_failed': 0,
                    'pages_skipped': 0,
                    'total_pages': total_pages
                }
            }
        )
        logger.info(f"Testing job {self.job_id} marked as running with {total_pages} pages to test")
    
    def set_completed(
        self,
        pages_tested: int,
        pages_passed: int,
        pages_failed: int,
        pages_skipped: int
    ):
        """
        Mark job as completed
        
        Args:
            pages_tested: Total pages tested
            pages_passed: Number of pages that passed
            pages_failed: Number of pages that failed  
            pages_skipped: Number of pages skipped
        """
        total_pages = pages_tested + pages_skipped
        self.job_manager.update_job_status(
            job_id=self.job_id,
            status=JobStatus.COMPLETED,
            progress={
                'current': pages_tested,
                'total': total_pages,
                'message': f'Testing completed: {pages_tested} tested, {pages_passed} passed, {pages_failed} failed',
                'details': {
                    'pages_tested': pages_tested,
                    'pages_passed': pages_passed,
                    'pages_failed': pages_failed,
                    'pages_skipped': pages_skipped,
                    'total_pages': total_pages
                }
            },
            result={
                'pages_tested': pages_tested,
                'pages_passed': pages_passed,
                'pages_failed': pages_failed,
                'pages_skipped': pages_skipped,
                'completed_at': datetime.now().isoformat()
            }
        )
        logger.info(f"Testing job {self.job_id} completed: {pages_tested} pages tested")
    
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
        logger.error(f"Testing job {self.job_id} failed: {error}")
    
    def set_cancelled(self):
        """Mark job as cancelled"""
        job = self.job_manager.get_job(self.job_id)
        if job:
            details = job.get('progress', {}).get('details', {})
            pages_tested = details.get('pages_tested', 0)
            pages_passed = details.get('pages_passed', 0)
            pages_failed = details.get('pages_failed', 0)
            pages_skipped = details.get('pages_skipped', 0)
            
            self.job_manager.update_job_status(
                job_id=self.job_id,
                status=JobStatus.CANCELLED,
                progress={
                    'current': pages_tested,
                    'total': details.get('total_pages', 0),
                    'message': 'Testing cancelled by user',
                    'details': {
                        'pages_tested': pages_tested,
                        'pages_passed': pages_passed,
                        'pages_failed': pages_failed,
                        'pages_skipped': pages_skipped,
                        'total_pages': details.get('total_pages', 0)
                    }
                }
            )
            logger.info(f"Testing job {self.job_id} cancelled")
    
    async def run(
        self,
        database: Database,
        browser_config: Dict[str, Any],
        take_screenshot: bool = True,
        run_ai_analysis: Optional[bool] = None,
        ai_api_key: Optional[str] = None
    ):
        """
        Run the testing job
        
        Args:
            database: Database instance
            browser_config: Browser configuration
            take_screenshot: Whether to take screenshots
            run_ai_analysis: Whether to run AI analysis
            ai_api_key: API key for AI analysis
        """
        from auto_a11y.testing import TestRunner
        
        logger.info(f"TestingJob.run started for job {self.job_id}")
        
        try:
            # Get website
            website = database.get_website(self.website_id)
            if not website:
                raise ValueError(f"Website {self.website_id} not found")
            
            # Get pages to test
            if self.test_all:
                pages = database.get_pages(self.website_id)
                # Filter out pages that are currently being tested
                testable_pages = [p for p in pages if p.status != PageStatus.TESTING]
            elif self.page_ids:
                testable_pages = []
                for page_id in self.page_ids:
                    page = database.get_page(page_id)
                    if page and page.status != PageStatus.TESTING:
                        testable_pages.append(page)
            else:
                raise ValueError("No pages specified for testing")
            
            if not testable_pages:
                logger.warning(f"No testable pages found for job {self.job_id}")
                self.set_completed(0, 0, 0, 0)
                return
            
            # Mark as running
            self.set_running(len(testable_pages))
            logger.info(f"Job {self.job_id} marked as running with {len(testable_pages)} pages to test")
            
            # Create test runner
            test_runner = TestRunner(database, browser_config)
            
            # Test statistics
            pages_tested = 0
            pages_passed = 0
            pages_failed = 0
            pages_skipped = 0
            
            # Test each page
            for i, page in enumerate(testable_pages):
                # Check for cancellation
                if self.is_cancelled():
                    logger.info(f"Testing job {self.job_id} was cancelled")
                    self.set_cancelled()
                    return
                
                # Update progress BEFORE testing to show current page
                self.update_progress(
                    pages_tested=pages_tested,
                    total_pages=len(testable_pages),
                    current_page=page.url,
                    message=f"Testing page {i+1}/{len(testable_pages)}: {page.url}",
                    pages_passed=pages_passed,
                    pages_failed=pages_failed,
                    pages_skipped=pages_skipped
                )
                
                # Mark page as testing
                page.status = PageStatus.TESTING
                database.update_page(page)
                
                try:
                    # Test the page with multi-state support
                    logger.info(f"Testing page {i+1}/{len(testable_pages)}: {page.url}")
                    test_results_list = await test_runner.test_page_multi_state(
                        page=page,
                        enable_multi_state=True,
                        take_screenshot=take_screenshot,
                        run_ai_analysis=run_ai_analysis,
                        ai_api_key=ai_api_key,
                        website_user_id=self.website_user_id
                    )

                    # test_page_multi_state returns List[TestResult]
                    # Use the last result (final state) for page status
                    test_results = test_results_list[-1] if test_results_list else None

                    # Update page status based on results
                    if test_results:
                        page.status = PageStatus.TESTED
                        if page.violation_count > 0:
                            pages_failed += 1
                        else:
                            pages_passed += 1
                    else:
                        page.status = PageStatus.ERROR
                        pages_failed += 1
                    
                    pages_tested += 1
                    
                    # Update progress AFTER testing to show correct count
                    self.update_progress(
                        pages_tested=pages_tested,
                        total_pages=len(testable_pages),
                        current_page=page.url,
                        message=f"Completed {pages_tested}/{len(testable_pages)} pages",
                        pages_passed=pages_passed,
                        pages_failed=pages_failed,
                        pages_skipped=pages_skipped
                    )
                    
                except Exception as e:
                    logger.error(f"Error testing page {page.url}: {e}")
                    page.status = PageStatus.ERROR
                    page.error_reason = str(e)
                    database.update_page(page)
                    pages_failed += 1
                    pages_tested += 1
                    
                    # Update progress after error too
                    self.update_progress(
                        pages_tested=pages_tested,
                        total_pages=len(testable_pages),
                        current_page=page.url,
                        message=f"Completed {pages_tested}/{len(testable_pages)} pages (with errors)",
                        pages_passed=pages_passed,
                        pages_failed=pages_failed,
                        pages_skipped=pages_skipped
                    )

                # Small delay between pages to let browser stabilize after multi-state testing
                if i < len(testable_pages) - 1:  # Don't delay after last page
                    await asyncio.sleep(0.5)

            # Check final cancellation status
            if self.is_cancelled():
                logger.info(f"Testing job {self.job_id} was cancelled")
                self.set_cancelled()
            else:
                # Mark as completed
                self.set_completed(pages_tested, pages_passed, pages_failed, pages_skipped)

        except Exception as e:
            logger.error(f"Testing job {self.job_id} failed: {e}")
            self.set_failed(str(e))
            raise
        finally:
            # Clean up browser resources
            if test_runner:
                await test_runner.cleanup()
    
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