"""
Main test runner for accessibility testing
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import time

from auto_a11y.models import Page, PageStatus, TestResult
from auto_a11y.core.database import Database
from auto_a11y.core.browser_manager import BrowserManager
from auto_a11y.testing.script_injector import ScriptInjector
from auto_a11y.testing.result_processor import ResultProcessor

logger = logging.getLogger(__name__)


class TestRunner:
    """Runs accessibility tests on web pages"""
    
    def __init__(self, database: Database, browser_config: Dict[str, Any]):
        """
        Initialize test runner
        
        Args:
            database: Database connection
            browser_config: Browser configuration
        """
        self.db = database
        self.browser_manager = BrowserManager(browser_config)
        self.script_injector = ScriptInjector()
        self.result_processor = ResultProcessor()
        self.screenshot_dir = Path(browser_config.get('SCREENSHOTS_DIR', 'screenshots'))
        self.screenshot_dir.mkdir(exist_ok=True, parents=True)
    
    async def test_page(
        self,
        page: Page,
        take_screenshot: bool = True,
        run_ai_analysis: bool = False,
        ai_api_key: Optional[str] = None
    ) -> TestResult:
        """
        Run accessibility tests on a single page
        
        Args:
            page: Page to test
            take_screenshot: Whether to capture screenshot
            run_ai_analysis: Whether to run AI analysis
            
        Returns:
            Test result
        """
        # Testing page
        start_time = time.time()
        
        # Update page status
        page.status = PageStatus.TESTING
        self.db.update_page(page)
        
        # Start browser if needed
        if not await self.browser_manager.is_running():
            await self.browser_manager.start()
        
        try:
            async with self.browser_manager.get_page() as browser_page:
                # Navigate to page
                response = await self.browser_manager.goto(
                    browser_page,
                    page.url,
                    wait_until='networkidle2',
                    timeout=30000
                )
                
                if not response:
                    raise RuntimeError(f"Failed to load page: {page.url}")
                
                # Wait for content to be ready
                await browser_page.waitForSelector('body', {'timeout': 5000})
                
                # Get WCAG compliance level from project
                wcag_level = 'AA'  # Default to AA
                try:
                    # Get website to find project
                    website = self.db.get_website(page.website_id)
                    if website:
                        project = self.db.get_project(website.project_id)
                        if project and project.config:
                            wcag_level = project.config.get('wcag_level', 'AA')
                            logger.info(f"Project config: {project.config}")
                            logger.info(f"Using WCAG {wcag_level} compliance level for testing")
                        else:
                            logger.info(f"No config found in project, using default AA")
                    else:
                        logger.warning(f"Could not find website for page {page.website_id}")
                except Exception as e:
                    logger.warning(f"Could not get WCAG level from project: {e}, defaulting to AA")
                
                # Inject test scripts
                await self.script_injector.inject_script_files(browser_page)
                
                # Set WCAG level in page context
                await browser_page.evaluate(f'''
                    window.WCAG_LEVEL = "{wcag_level}";
                    console.log("Testing with WCAG Level:", window.WCAG_LEVEL);
                ''')
                
                # Run all tests
                # Running JavaScript tests
                raw_results = await self.script_injector.run_all_tests(browser_page)
                
                # Take screenshot if requested
                screenshot_path = None
                screenshot_bytes = None
                if take_screenshot:
                    screenshot_path = await self._take_screenshot(browser_page, page.id)
                    # Also get screenshot bytes for AI analysis
                    screenshot_bytes = await browser_page.screenshot({
                        'fullPage': True,
                        'type': 'jpeg',
                        'quality': 85
                    })
                
                # Run AI analysis if requested
                ai_findings = []
                ai_analysis_results = {}
                if run_ai_analysis and ai_api_key and screenshot_bytes:
                    analyzer = None
                    try:
                        from auto_a11y.ai import ClaudeAnalyzer
                        
                        # Get page HTML
                        page_html = await browser_page.content()
                        
                        # Initialize analyzer
                        analyzer = ClaudeAnalyzer(ai_api_key)
                        
                        # Run analysis
                        logger.info("Running AI accessibility analysis")
                        ai_results = await analyzer.analyze_page(
                            screenshot=screenshot_bytes,
                            html=page_html,
                            analyses=['headings', 'reading_order', 'language', 'interactive']
                        )
                        
                        ai_findings = ai_results.get('findings', [])
                        ai_analysis_results = ai_results.get('raw_results', {})
                        
                        logger.info(f"AI analysis found {len(ai_findings)} issues")
                        
                    except Exception as e:
                        logger.error(f"AI analysis failed: {e}")
                    finally:
                        # Clean up Claude client to avoid event loop errors
                        if analyzer and hasattr(analyzer, 'client'):
                            try:
                                await analyzer.client.aclose()
                            except Exception as cleanup_error:
                                logger.debug(f"Error cleaning up AI analyzer: {cleanup_error}")
                
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Process results
                test_result = self.result_processor.process_test_results(
                    page_id=page.id,
                    raw_results=raw_results,
                    screenshot_path=screenshot_path,
                    duration_ms=duration_ms
                )
                
                # Add AI findings to test result
                if ai_findings:
                    test_result.ai_findings = ai_findings
                    test_result.ai_analysis_results = ai_analysis_results
                
                # Save test result to database
                result_id = self.db.create_test_result(test_result)
                test_result._id = result_id
                
                # Update page with test results
                page.status = PageStatus.TESTED
                page.last_tested = datetime.now()
                page.violation_count = test_result.violation_count
                page.warning_count = test_result.warning_count
                page.info_count = test_result.info_count
                page.discovery_count = test_result.discovery_count
                page.pass_count = test_result.pass_count
                page.test_duration_ms = duration_ms
                self.db.update_page(page)
                
                # Page test completed successfully
                
                return test_result
                
        except Exception as e:
            logger.error(f"Error testing page {page.url}: {e}")
            
            # Update page status
            page.status = PageStatus.ERROR
            self.db.update_page(page)
            
            # Create error result
            test_result = TestResult(
                page_id=page.id,
                test_date=datetime.now(),
                duration_ms=int((time.time() - start_time) * 1000),
                error=str(e),
                violations=[],
                warnings=[],
                passes=[]
            )
            
            # Save error result
            result_id = self.db.create_test_result(test_result)
            test_result._id = result_id
            
            return test_result
    
    async def test_pages(
        self,
        pages: List[Page],
        parallel: int = 1,
        take_screenshots: bool = True,
        progress_callback: Optional[callable] = None
    ) -> List[TestResult]:
        """
        Test multiple pages
        
        Args:
            pages: Pages to test
            parallel: Number of parallel tests
            take_screenshots: Whether to capture screenshots
            progress_callback: Progress callback function
            
        Returns:
            List of test results
        """
        results = []
        total = len(pages)
        completed = 0
        
        # Process pages in batches
        for i in range(0, total, parallel):
            batch = pages[i:i+parallel]
            
            # Test batch in parallel
            tasks = [
                self.test_page(page, take_screenshots)
                for page in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Test failed with exception: {result}")
                else:
                    results.append(result)
            
            completed += len(batch)
            
            # Update progress
            if progress_callback:
                await progress_callback({
                    'completed': completed,
                    'total': total,
                    'percentage': (completed / total) * 100
                })
        
        return results
    
    async def test_website(
        self,
        website_id: str,
        page_filter: Optional[Dict[str, Any]] = None,
        parallel: int = 1
    ) -> Dict[str, Any]:
        """
        Test all pages in a website
        
        Args:
            website_id: Website ID
            page_filter: Optional filter for pages
            parallel: Number of parallel tests
            
        Returns:
            Test summary
        """
        website = self.db.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")
        
        # Get pages to test
        pages = self.db.get_pages(website_id)
        
        # Apply filter if provided
        if page_filter:
            if page_filter.get('untested_only'):
                pages = [p for p in pages if p.needs_testing]
            if page_filter.get('priority'):
                pages = [p for p in pages if p.priority == page_filter['priority']]
        
        if not pages:
            return {
                'website_id': website_id,
                'pages_tested': 0,
                'message': 'No pages to test'
            }
        
        logger.info(f"Testing {len(pages)} pages for website {website_id}")
        
        # Test pages
        results = await self.test_pages(pages, parallel=parallel)
        
        # Update website last_tested
        website.last_tested = datetime.now()
        self.db.update_website(website)
        
        # Calculate summary
        total_violations = sum(r.violation_count for r in results)
        total_warnings = sum(r.warning_count for r in results)
        total_passes = sum(r.pass_count for r in results)
        
        return {
            'website_id': website_id,
            'pages_tested': len(results),
            'total_violations': total_violations,
            'total_warnings': total_warnings,
            'total_passes': total_passes,
            'average_duration_ms': sum(r.duration_ms for r in results) / len(results) if results else 0
        }
    
    async def _take_screenshot(self, browser_page, page_id: str) -> str:
        """
        Take screenshot of page
        
        Args:
            browser_page: Pyppeteer page object
            page_id: Page ID for filename
            
        Returns:
            Screenshot file path
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"page_{page_id}_{timestamp}.jpg"
            filepath = self.screenshot_dir / filename
            
            await self.browser_manager.take_screenshot(
                browser_page,
                path=filepath,
                full_page=True
            )
            
            logger.debug(f"Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    async def cleanup(self):
        """Clean up resources"""
        await self.browser_manager.stop()


class TestJob:
    """Represents a testing job"""
    
    def __init__(self, job_id: str, pages: List[Page]):
        """
        Initialize test job
        
        Args:
            job_id: Job ID
            pages: Pages to test
        """
        self.job_id = job_id
        self.pages = pages
        self.status = 'pending'
        self.progress = {
            'total': len(pages),
            'completed': 0,
            'failed': 0,
            'current_page': None,
            'started_at': None,
            'completed_at': None,
            'results': []
        }
    
    async def run(self, test_runner: TestRunner):
        """
        Run the test job
        
        Args:
            test_runner: Test runner instance
        """
        self.status = 'running'
        self.progress['started_at'] = datetime.now()
        
        try:
            for page in self.pages:
                self.progress['current_page'] = page.url
                
                try:
                    result = await test_runner.test_page(page)
                    self.progress['results'].append(result)
                    self.progress['completed'] += 1
                except Exception as e:
                    logger.error(f"Failed to test page {page.url}: {e}")
                    self.progress['failed'] += 1
            
            self.status = 'completed'
            
        except Exception as e:
            logger.error(f"Test job {self.job_id} failed: {e}")
            self.status = 'failed'
            
        finally:
            self.progress['completed_at'] = datetime.now()