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
from auto_a11y.testing.script_executor import ScriptExecutor
from auto_a11y.testing.script_session_manager import ScriptSessionManager
from auto_a11y.testing.multi_state_test_runner import MultiStateTestRunner
from auto_a11y.testing.login_automation import LoginAutomation

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
        self.script_injector = ScriptInjector()  # Will use test_config from project
        self.result_processor = ResultProcessor()
        self.script_executor = ScriptExecutor()  # For executing page setup scripts
        self.session_manager = ScriptSessionManager(database)  # For tracking script execution
        self.multi_state_runner = MultiStateTestRunner(self.script_executor)  # For multi-state testing
        self.login_automation = LoginAutomation(database)  # For authenticated testing
        self.screenshot_dir = Path(browser_config.get('SCREENSHOTS_DIR', 'screenshots'))
        self.screenshot_dir.mkdir(exist_ok=True, parents=True)
        self._current_website_id = None  # Track current website for session management
        self._logged_in_user = None  # Track currently logged in user
    
    async def test_page(
        self,
        page: Page,
        take_screenshot: bool = True,
        run_ai_analysis: bool = False,
        ai_api_key: Optional[str] = None,
        website_user_id: Optional[str] = None
    ) -> TestResult:
        """
        Run accessibility tests on a single page

        Args:
            page: Page to test
            take_screenshot: Whether to capture screenshot
            run_ai_analysis: Whether to run AI analysis
            ai_api_key: API key for AI analysis
            website_user_id: Optional ID of user to authenticate as before testing

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
                # Get wait strategy from project config (defaults to networkidle2 for complete content)
                # Valid options:
                #   - 'networkidle2': Wait for network to be mostly idle (default, best for slow/dynamic sites)
                #   - 'networkidle0': Wait for network to be completely idle (very thorough but slowest)
                #   - 'domcontentloaded': Wait only for DOM to be ready (fast, for sites with heavy background activity)
                #   - 'load': Wait for load event (faster than networkidle, slower than domcontentloaded)
                wait_strategy = 'networkidle2'  # Default: wait for network to be mostly idle

                try:
                    website = self.db.get_website(page.website_id)
                    if website:
                        project = self.db.get_project(website.project_id)
                        if project and project.config:
                            # Allow project to override wait strategy for sites with heavy background activity
                            wait_strategy = project.config.get('page_load_strategy', 'networkidle2')
                            logger.info(f"Using page load strategy: {wait_strategy}")
                except Exception as e:
                    logger.warning(f"Could not get project config for wait strategy: {e}")

                # Navigate to page
                response = await self.browser_manager.goto(
                    browser_page,
                    page.url,
                    wait_until=wait_strategy,
                    timeout=30000
                )

                if not response:
                    raise RuntimeError(f"Failed to load page: {page.url}")

                # Wait for content to be ready
                await browser_page.waitForSelector('body', {'timeout': 5000})

                # If using domcontentloaded, give the page a moment to stabilize
                # This prevents the browser from closing the session too early
                if wait_strategy == 'domcontentloaded':
                    import asyncio
                    await asyncio.sleep(2)  # Wait 2 seconds for JS to initialize

                # Perform authentication if user specified
                authenticated_user = None
                if website_user_id:
                    user = self.db.get_website_user(website_user_id)
                    if user:
                        if not user.enabled:
                            logger.warning(f"User {user.username} is disabled, skipping authentication")
                        else:
                            logger.info(f"Authenticating as user: {user.username} (roles: {user.role_display})")
                            login_result = await self.login_automation.perform_login(
                                browser_page,
                                user,
                                timeout=30000
                            )

                            if login_result['success']:
                                logger.info(f"Successfully authenticated as {user.username} in {login_result['duration_ms']}ms")
                                authenticated_user = user
                                self._logged_in_user = user
                            else:
                                logger.error(f"Authentication failed: {login_result['error']}")
                                # Continue with testing even if login fails, but record the failure
                    else:
                        logger.warning(f"User ID {website_user_id} not found")

                # Start script session if not already started for this website
                if self._current_website_id != page.website_id:
                    # End previous session if exists
                    if self._current_website_id is not None:
                        self.session_manager.end_session()

                    # Start new session for this website
                    self.session_manager.start_session(page.website_id)
                    self._current_website_id = page.website_id
                    logger.info(f"Started script session for website {page.website_id}")

                # Get all applicable scripts for this page (website-level + page-level)
                scripts_to_execute = self.db.get_scripts_for_page_v2(
                    page_id=page.id,
                    website_id=page.website_id,
                    enabled_only=True
                )

                # Execute scripts with session awareness
                script_violations = []
                for script in scripts_to_execute:
                    logger.info(f"Processing script: {script.name} (scope={script.scope.value}, trigger={script.trigger.value})")
                    try:
                        result = await self.script_executor.execute_with_session(
                            browser_page,
                            script,
                            page.id,
                            self.session_manager
                        )

                        # Check for violations reported by scripts
                        if 'violation' in result:
                            script_violations.append(result['violation'])
                            logger.warning(f"Script reported violation: {result['violation'].message}")

                        # Log result
                        if result.get('skipped'):
                            logger.info(f"Script '{script.name}' skipped: {result.get('skip_reason')}")
                        elif result['success']:
                            logger.info(f"Script '{script.name}' completed successfully in {result['duration_ms']}ms")
                            # Update execution stats
                            self.db.update_script_execution_stats(
                                script.id,
                                success=True,
                                duration_ms=result['duration_ms']
                            )
                        else:
                            logger.warning(f"Script '{script.name}' failed: {result.get('error', 'Unknown error')}")
                            # Update execution stats
                            self.db.update_script_execution_stats(
                                script.id,
                                success=False,
                                duration_ms=result['duration_ms']
                            )

                    except Exception as e:
                        logger.error(f"Error executing script '{script.name}': {e}")
                        # Continue with testing even if script crashes
                
                # Get project configuration including WCAG level and touchpoint settings
                wcag_level = 'AA'  # Default to AA
                project_config = None
                test_config = None
                
                try:
                    # Get website to find project
                    website = self.db.get_website(page.website_id)
                    if website:
                        project = self.db.get_project(website.project_id)
                        if project and project.config:
                            project_config = project.config
                            wcag_level = project_config.get('wcag_level', 'AA')
                            logger.info(f"Using WCAG {wcag_level} compliance level for testing")
                            
                            # Create test configuration from project settings
                            from auto_a11y.config.test_config import TestConfiguration
                            test_config = TestConfiguration(database=self.db, debug_mode=False)

                            # Apply touchpoint settings from project
                            if 'touchpoints' in project_config:
                                test_config.config['touchpoints'] = project_config['touchpoints']
                            
                            # Apply AI settings from project
                            test_config.config['global']['run_ai_tests'] = project_config.get('enable_ai_testing', False)
                            if 'ai_tests' in project_config:
                                for test_name in ['headings', 'reading_order', 'modals', 'language', 'animations', 'interactive']:
                                    enabled = test_name in project_config['ai_tests']
                                    test_config.set_ai_test_enabled(test_name, enabled)
                        else:
                            logger.info(f"No config found in project, using defaults")
                    else:
                        logger.warning(f"Could not find website for page {page.website_id}")
                except Exception as e:
                    logger.warning(f"Could not get project config: {e}, using defaults")
                
                # Set test configuration for Python tests
                if test_config:
                    self.script_injector.test_config = test_config

                # Pass project config separately for JavaScript config injection
                self.script_injector.project_config = project_config

                # Inject test scripts
                await self.script_injector.inject_script_files(browser_page)
                
                # Set WCAG level in page context
                await browser_page.evaluate(f'''
                    window.WCAG_LEVEL = "{wcag_level}";
                    console.log("Testing with WCAG Level:", window.WCAG_LEVEL);
                ''')

                # Inject document metadata for document link language testing
                try:
                    # Get all document references for this website
                    document_refs = self.db.get_document_references(page.website_id)

                    # Build a map of document URL to language metadata
                    doc_metadata = {}
                    for doc_ref in document_refs:
                        if doc_ref.language:
                            # Store with both full URL and just the filename for flexible matching
                            doc_metadata[doc_ref.document_url] = {
                                'language': doc_ref.language,
                                'confidence': doc_ref.language_confidence
                            }

                    # Inject into page context as JSON
                    import json
                    metadata_json = json.dumps(doc_metadata)
                    await browser_page.evaluate(f'''
                        window.DOCUMENT_METADATA = {metadata_json};
                    ''')
                    logger.debug(f"Injected metadata for {len(doc_metadata)} documents")
                except Exception as e:
                    logger.warning(f"Could not inject document metadata: {e}")
                    await browser_page.evaluate('''
                        window.DOCUMENT_METADATA = {{}};
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
                        'quality': 80  # Reduced from 85 to help prevent MongoDB 16MB document limit issues
                    })
                
                # Check if project has AI testing enabled
                ai_findings = []
                ai_analysis_results = {}
                
                # Get AI testing configuration from project
                run_ai = False
                ai_tests_to_run = []
                
                try:
                    website = self.db.get_website(page.website_id)
                    if website:
                        project = self.db.get_project(website.project_id)
                        if project and project.config:
                            # Check if AI testing is enabled at project level
                            if project.config.get('enable_ai_testing', False):
                                run_ai = True
                                ai_tests_to_run = project.config.get('ai_tests', [])
                                logger.info(f"AI testing enabled for project '{project.name}', will run tests: {ai_tests_to_run}")
                            else:
                                logger.info(f"AI testing disabled for project '{project.name}'")
                        else:
                            logger.info(f"No config found for project, AI testing disabled")
                    else:
                        logger.warning(f"Could not find website with id {page.website_id}")
                except Exception as e:
                    logger.warning(f"Could not get AI config from project: {e}")
                
                # Override with explicit parameter if provided (for backward compatibility)
                if run_ai_analysis is not None:
                    logger.info(f"Overriding AI setting with explicit parameter: run_ai_analysis={run_ai_analysis}")
                    run_ai = run_ai_analysis
                    if run_ai and not ai_tests_to_run:
                        # Default tests if not specified
                        ai_tests_to_run = ['headings', 'reading_order', 'language', 'interactive']
                        logger.info(f"Using default AI tests: {ai_tests_to_run}")
                
                # Get API key from config if not provided
                if not ai_api_key:
                    try:
                        from config import config
                        ai_api_key = getattr(config, 'CLAUDE_API_KEY', None)
                        if ai_api_key:
                            logger.info("Using CLAUDE_API_KEY from config")
                    except Exception as e:
                        logger.warning(f"Could not get CLAUDE_API_KEY from config: {e}")
                
                # Log decision factors
                logger.info(f"AI analysis decision - run_ai: {run_ai}, has_api_key: {bool(ai_api_key)}, has_screenshot: {bool(screenshot_bytes)}, tests_to_run: {ai_tests_to_run}")
                
                # Run AI analysis if enabled
                if run_ai and ai_api_key and screenshot_bytes and ai_tests_to_run:
                    analyzer = None
                    try:
                        from auto_a11y.ai import ClaudeAnalyzer
                        
                        # Get page HTML
                        page_html = await browser_page.content()
                        
                        # Initialize analyzer
                        analyzer = ClaudeAnalyzer(ai_api_key)
                        
                        # Run only the selected AI tests
                        logger.info(f"Running AI accessibility analysis with tests: {ai_tests_to_run}")
                        ai_results = await analyzer.analyze_page(
                            screenshot=screenshot_bytes,
                            html=page_html,
                            analyses=ai_tests_to_run,
                            test_config=test_config
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
                
                # Process results (including AI findings)
                test_result = self.result_processor.process_test_results(
                    page_id=page.id,
                    raw_results=raw_results,
                    screenshot_path=screenshot_path,
                    duration_ms=duration_ms,
                    ai_findings=ai_findings,
                    ai_analysis_results=ai_analysis_results
                )

                # AI findings are now merged in result_processor.process_test_results()

                # Add script violations to test result
                if script_violations:
                    logger.info(f"Adding {len(script_violations)} script violations to test result")
                    test_result.violations.extend(script_violations)
                    test_result.violation_count += len(script_violations)

                # Add authenticated user information to metadata
                if authenticated_user:
                    test_result.metadata['authenticated_user'] = {
                        'user_id': authenticated_user.id,
                        'username': authenticated_user.username,
                        'display_name': authenticated_user.display_name,
                        'roles': authenticated_user.roles
                    }
                    logger.info(f"Test completed as authenticated user: {authenticated_user.username}")

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
                page.screenshot_path = screenshot_path  # Save screenshot path to page
                self.db.update_page(page)
                
                # Update website's last_tested timestamp
                website = self.db.get_website(page.website_id)
                if website:
                    website.last_tested = datetime.now()
                    self.db.update_website(website)
                
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

    async def test_page_multi_state(
        self,
        page: Page,
        enable_multi_state: bool = True,
        take_screenshot: bool = True,
        run_ai_analysis: bool = False,
        ai_api_key: Optional[str] = None,
        website_user_id: Optional[str] = None
    ) -> List[TestResult]:
        """
        Run accessibility tests on a single page across multiple states

        This method tests the page in multiple states by executing setup scripts
        and testing before/after each script execution as configured.

        Args:
            page: Page to test
            enable_multi_state: Whether to use multi-state testing
            take_screenshot: Whether to capture screenshots
            run_ai_analysis: Whether to run AI analysis
            ai_api_key: API key for AI analysis
            website_user_id: Optional ID of user to authenticate as

        Returns:
            List of test results (one per state)
        """
        if not enable_multi_state:
            # Fall back to single-state testing
            result = await self.test_page(page, take_screenshot, run_ai_analysis, ai_api_key, website_user_id)
            return [result]

        # Start script session if not already started for this website
        if self._current_website_id != page.website_id:
            # End previous session if exists
            if self._current_website_id is not None:
                self.session_manager.end_session()

            # Start new session for this website
            self.session_manager.start_session(page.website_id)
            self._current_website_id = page.website_id
            logger.info(f"Started script session for website {page.website_id}")

        # Get session ID
        session_id = self.session_manager.current_session.session_id if self.session_manager.current_session else None

        # Get all applicable scripts for this page
        scripts_to_execute = self.db.get_scripts_for_page_v2(
            page_id=page.id,
            website_id=page.website_id,
            enabled_only=True
        )

        # Filter scripts that have multi-state testing configured
        multi_state_scripts = [
            script for script in scripts_to_execute
            if script.test_before_execution or script.test_after_execution
        ]

        if not multi_state_scripts:
            logger.info(f"No multi-state scripts configured for page {page.url}, using single-state testing")
            result = await self.test_page(page, take_screenshot, run_ai_analysis, ai_api_key)
            return [result]

        logger.info(f"Testing page {page.url} with {len(multi_state_scripts)} multi-state scripts")

        # Update page status
        page.status = PageStatus.TESTING
        self.db.update_page(page)

        # Start browser if needed
        if not await self.browser_manager.is_running():
            await self.browser_manager.start()

        results = []

        try:
            async with self.browser_manager.get_page() as browser_page:
                # Navigate to page
                wait_strategy = 'networkidle2'
                try:
                    website = self.db.get_website(page.website_id)
                    if website:
                        project = self.db.get_project(website.project_id)
                        if project and project.config:
                            wait_strategy = project.config.get('page_load_strategy', 'networkidle2')
                except Exception as e:
                    logger.warning(f"Could not get project config: {e}")

                response = await self.browser_manager.goto(
                    browser_page,
                    page.url,
                    wait_until=wait_strategy,
                    timeout=30000
                )

                if not response:
                    raise RuntimeError(f"Failed to load page: {page.url}")

                await browser_page.waitForSelector('body', {'timeout': 5000})

                # Perform authentication if user specified
                authenticated_user = None
                if website_user_id:
                    user = self.db.get_website_user(website_user_id)
                    if user and user.enabled:
                        logger.info(f"Authenticating as user: {user.username} for multi-state testing")
                        login_result = await self.login_automation.perform_login(
                            browser_page,
                            user,
                            timeout=30000
                        )

                        if login_result['success']:
                            logger.info(f"Successfully authenticated as {user.username}")
                            authenticated_user = user
                            self._logged_in_user = user
                        else:
                            logger.error(f"Authentication failed: {login_result['error']}")

                # Create a test function that can be called multiple times
                async def run_single_test(browser_page, page_id):
                    """Run accessibility tests and return TestResult"""
                    # Get project config
                    test_config = None
                    project_config = None
                    wcag_level = 'AA'

                    try:
                        website = self.db.get_website(page.website_id)
                        if website:
                            project = self.db.get_project(website.project_id)
                            if project and project.config:
                                project_config = project.config
                                wcag_level = project_config.get('wcag_level', 'AA')

                                from auto_a11y.config.test_config import TestConfiguration
                                test_config = TestConfiguration(database=self.db, debug_mode=False)

                                if 'touchpoints' in project_config:
                                    test_config.config['touchpoints'] = project_config['touchpoints']

                                test_config.config['global']['run_ai_tests'] = project_config.get('enable_ai_testing', False)
                    except Exception as e:
                        logger.warning(f"Could not get project config: {e}")

                    # Set test configuration
                    if test_config:
                        self.script_injector.test_config = test_config
                    self.script_injector.project_config = project_config

                    # Inject test scripts
                    await self.script_injector.inject_script_files(browser_page)

                    # Set WCAG level
                    await browser_page.evaluate(f'window.WCAG_LEVEL = "{wcag_level}";')

                    # Run tests
                    raw_results = await self.script_injector.run_all_tests(browser_page)

                    # Take screenshot if requested
                    screenshot_path = None
                    if take_screenshot:
                        screenshot_path = await self._take_screenshot(browser_page, page_id)

                    # Process results
                    duration_ms = 0  # Will be set by caller
                    test_result = self.result_processor.process_test_results(
                        page_id=page_id,
                        raw_results=raw_results,
                        screenshot_path=screenshot_path,
                        duration_ms=duration_ms,
                        ai_findings=[],
                        ai_analysis_results={}
                    )

                    return test_result

                # Run multi-state testing
                results = await self.multi_state_runner.test_page_multi_state(
                    page=browser_page,
                    page_id=page.id,
                    scripts=multi_state_scripts,
                    test_function=run_single_test,
                    session_id=session_id
                )

                # Add authenticated user information to all results
                if authenticated_user:
                    for result in results:
                        result.metadata['authenticated_user'] = {
                            'user_id': authenticated_user.id,
                            'username': authenticated_user.username,
                            'display_name': authenticated_user.display_name,
                            'roles': authenticated_user.roles
                        }
                    logger.info(f"Multi-state tests completed as authenticated user: {authenticated_user.username}")

                # Save all results to database
                for result in results:
                    result_id = self.db.create_test_result(result)
                    result._id = result_id

                # Update page with results from final state
                if results:
                    final_result = results[-1]
                    page.status = PageStatus.TESTED
                    page.last_tested = datetime.now()
                    page.violation_count = final_result.violation_count
                    page.warning_count = final_result.warning_count
                    page.info_count = final_result.info_count
                    page.discovery_count = final_result.discovery_count
                    page.pass_count = final_result.pass_count
                    page.test_duration_ms = sum(r.duration_ms for r in results)
                    page.screenshot_path = final_result.screenshot_path
                    self.db.update_page(page)

                # Update website's last_tested timestamp
                website = self.db.get_website(page.website_id)
                if website:
                    website.last_tested = datetime.now()
                    self.db.update_website(website)

                logger.info(f"Multi-state testing complete: {len(results)} test results generated")

                return results

        except Exception as e:
            logger.error(f"Error in multi-state testing for page {page.url}: {e}")

            # Update page status
            page.status = PageStatus.ERROR
            self.db.update_page(page)

            # Create error result
            test_result = TestResult(
                page_id=page.id,
                test_date=datetime.now(),
                duration_ms=0,
                error=str(e),
                violations=[],
                warnings=[],
                passes=[]
            )

            # Save error result
            result_id = self.db.create_test_result(test_result)
            test_result._id = result_id

            return [test_result]

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