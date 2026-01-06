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

                # Perform authentication FIRST if user specified
                authenticated_user = None
                if website_user_id:
                    logger.warning(f"DEBUG: Testing page {page.url} with user_id: {website_user_id}")
                    # Try project user first, then website user
                    user = self.db.get_project_user(website_user_id)
                    if not user:
                        user = self.db.get_website_user(website_user_id)
                    if user:
                        logger.warning(f"DEBUG: Found user: {user.username} (id: {user.id})")
                        if not user.enabled:
                            logger.warning(f"User {user.username} is disabled, skipping authentication")
                        else:
                            # Check if already logged in as this user
                            if self._logged_in_user:
                                logger.warning(f"DEBUG: Already have logged_in_user: {self._logged_in_user.username} (id: {self._logged_in_user.id})")
                                if self._logged_in_user.id == user.id:
                                    logger.warning(f"DEBUG: IDs match, reusing session")
                                    authenticated_user = self._logged_in_user
                                else:
                                    logger.warning(f"DEBUG: IDs don't match ({self._logged_in_user.id} != {user.id}), will re-authenticate")
                            else:
                                logger.warning(f"DEBUG: No logged_in_user set, will authenticate")

                            if not authenticated_user:
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

                # Navigate to test page (after authentication if applicable)
                logger.info(f"Navigating to test page: {page.url}")
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
                            test_config = TestConfiguration(database=self.db, debug_mode=True)

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
                
                # Store original viewport before running tests
                # Some tests (like text_contrast and floating_dialogs) change viewport for breakpoint testing
                original_viewport = await browser_page.evaluate('() => ({ width: window.innerWidth, height: window.innerHeight })')
                logger.debug(f"Stored original viewport: {original_viewport}")

                # Run all tests
                # Running JavaScript tests
                raw_results = await self.script_injector.run_all_tests(browser_page)

                # Restore original viewport after tests complete
                # This is critical because some tests change viewport for responsive breakpoint testing
                if original_viewport:
                    try:
                        await browser_page.setViewport({
                            'width': original_viewport['width'],
                            'height': original_viewport['height']
                        })
                        logger.debug(f"Restored viewport to original size: {original_viewport}")
                        # Give page a moment to reflow after viewport change
                        import asyncio
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.warning(f"Could not restore viewport: {e}")

                # Take screenshot if requested
                screenshot_path = None
                screenshot_bytes = None
                if take_screenshot:
                    # Take screenshot once and reuse bytes for AI analysis
                    # Taking two separate screenshots can destabilize Pyppeteer connection
                    screenshot_path, screenshot_bytes = await self._take_screenshot_with_bytes(browser_page, page.id)
                
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
                logger.warning(f"AI analysis decision - run_ai: {run_ai}, has_api_key: {bool(ai_api_key)}, has_screenshot: {bool(screenshot_bytes)}, tests_to_run: {ai_tests_to_run}")
                
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
                        logger.warning(f"Running AI accessibility analysis with tests: {ai_tests_to_run}")
                        ai_results = await analyzer.analyze_page(
                            screenshot=screenshot_bytes,
                            html=page_html,
                            analyses=ai_tests_to_run,
                            test_config=test_config
                        )
                        
                        ai_findings = ai_results.get('findings', [])
                        ai_analysis_results = ai_results.get('raw_results', {})
                        
                        logger.warning(f"AI analysis found {len(ai_findings)} issues")
                        if ai_findings:
                            logger.warning(f"AI finding IDs: {[f.id if hasattr(f, 'id') else str(f) for f in ai_findings]}")
                        
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
                    user_info = {
                        'user_id': authenticated_user.id,
                        'username': authenticated_user.username,
                        'display_name': authenticated_user.display_name,
                        'roles': authenticated_user.roles
                    }

                    # Add to test result metadata
                    test_result.metadata['authenticated_user'] = user_info

                    # Add to each violation's metadata
                    for violation in test_result.violations:
                        violation.metadata['authenticated_user'] = user_info

                    # Add to each warning's metadata
                    for warning in test_result.warnings:
                        warning.metadata['authenticated_user'] = user_info

                    # Add to each info item's metadata
                    for info in test_result.info:
                        info.metadata['authenticated_user'] = user_info

                    # Add to each discovery item's metadata
                    for discovery in test_result.discovery:
                        discovery.metadata['authenticated_user'] = user_info

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

        # Update page status
        page.status = PageStatus.TESTING
        self.db.update_page(page)

        # Start browser if needed
        if not await self.browser_manager.is_running():
            await self.browser_manager.start()

        results = []
        browser_page = None

        try:
            # Don't use get_page() context manager for multi-state testing
            # because _prepare_browser_for_state restarts the browser and creates new pages
            # The context manager would try to close a stale page reference
            browser_page = await self.browser_manager.create_page()
            
            # Get wait strategy from project config
            wait_strategy = 'networkidle2'
            try:
                website = self.db.get_website(page.website_id)
                if website:
                    project = self.db.get_project(website.project_id)
                    if project and project.config:
                        wait_strategy = project.config.get('page_load_strategy', 'networkidle2')
            except Exception as e:
                logger.warning(f"Could not get project config: {e}")

            # STEP 1: Perform authentication FIRST if user specified
            authenticated_user = None
            logger.warning(f"DEBUG multi-state: website_user_id={website_user_id}")
            if website_user_id:
                # Try project user first, then website user
                user = self.db.get_project_user(website_user_id)
                logger.warning(f"DEBUG multi-state: get_project_user returned: {user}")
                if not user:
                    user = self.db.get_website_user(website_user_id)
                    logger.warning(f"DEBUG multi-state: get_website_user returned: {user}")
                logger.warning(f"DEBUG multi-state: user={user}, user.enabled={user.enabled if user else 'N/A'}")
                if user and user.enabled:
                    logger.warning(f"DEBUG multi-state: About to authenticate as user: {user.username}")
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

            # STEP 2: Navigate to test page (after authentication)
            logger.info(f"Navigating to test page: {page.url}")
            response = await self.browser_manager.goto(
                browser_page,
                page.url,
                wait_until=wait_strategy,
                timeout=30000
            )

            if not response:
                raise RuntimeError(f"Failed to load page: {page.url}")

            await browser_page.waitForSelector('body', {'timeout': 5000})

            # STEP 3: Now detect scripts (after we're on the test page, authenticated)
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

            logger.warning(f"DEBUG: Found {len(scripts_to_execute)} scripts, filtering for multi-state")
            for script in scripts_to_execute:
                logger.warning(f"DEBUG: Script ID={script.id} '{script.name}' - test_before={script.test_before_execution}, test_after={script.test_after_execution}, clear_cookies={script.clear_cookies_before}, clear_localStorage={script.clear_local_storage_before}")

            if not multi_state_scripts:
                logger.info(f"No multi-state scripts configured for page {page.url}, using single-state testing")
                # Fall back to single test but we're already authenticated and on the page
                result = await self.test_page(page, take_screenshot, run_ai_analysis, ai_api_key, website_user_id)
                return [result]

            logger.warning(f"DEBUG: Testing page {page.url} with {len(multi_state_scripts)} multi-state scripts")

            # Create a test function that can be called multiple times
            async def run_single_test(browser_page, page_id):
                """Run accessibility tests and return TestResult"""
                # Verify browser connection before starting tests
                try:
                    ready_state = await asyncio.wait_for(
                        browser_page.evaluate('() => document.readyState'),
                        timeout=5.0
                    )
                    logger.warning(f"DEBUG run_single_test: page readyState={ready_state}")
                except Exception as conn_err:
                    logger.error(f"Browser connection lost at start of run_single_test: {conn_err}")
                    raise

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
                            test_config = TestConfiguration(database=self.db, debug_mode=True)

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
                logger.warning(f"DEBUG run_single_test: about to inject scripts")
                await self.script_injector.inject_script_files(browser_page)
                logger.warning(f"DEBUG run_single_test: scripts injected")

                # Verify connection still alive after injection
                try:
                    await asyncio.wait_for(
                        browser_page.evaluate('() => true'),
                        timeout=2.0
                    )
                    logger.warning(f"DEBUG run_single_test: connection verified after injection")
                except Exception as conn_err:
                    logger.error(f"Connection lost after script injection: {conn_err}")
                    raise

                # Set WCAG level
                logger.warning(f"DEBUG run_single_test: setting WCAG level")
                await browser_page.evaluate(f'window.WCAG_LEVEL = "{wcag_level}";')
                logger.warning(f"DEBUG run_single_test: WCAG level set")

                # Store original viewport before running tests (some tests change it)
                logger.warning(f"DEBUG run_single_test: getting viewport")
                original_viewport = await browser_page.evaluate('() => ({ width: window.innerWidth, height: window.innerHeight })')
                logger.warning(f"DEBUG run_single_test: viewport stored, about to run tests")
                logger.debug(f"Stored original viewport: {original_viewport}")

                # Run tests
                raw_results = await self.script_injector.run_all_tests(browser_page)
                
                # Verify browser connection after all tests complete
                logger.warning("DEBUG run_single_test: all tests complete, verifying connection")
                try:
                    await asyncio.wait_for(
                        browser_page.evaluate('() => document.readyState'),
                        timeout=5.0
                    )
                    logger.warning("DEBUG run_single_test: connection verified after tests")
                except Exception as conn_err:
                    logger.error(f"Browser connection lost after tests: {conn_err}")
                    raise

                # Restore original viewport after tests complete
                if original_viewport:
                    try:
                        await browser_page.setViewport({
                            'width': original_viewport['width'],
                            'height': original_viewport['height']
                        })
                        logger.debug(f"Restored viewport to original size: {original_viewport}")
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.warning(f"Could not restore viewport: {e}")

                # Take screenshot if requested
                screenshot_path = None
                screenshot_bytes = None
                if take_screenshot:
                    # Verify browser is still connected before taking screenshot
                    try:
                        await asyncio.wait_for(
                            browser_page.evaluate('() => document.readyState'),
                            timeout=5.0
                        )
                        logger.warning("DEBUG run_single_test: browser connected, taking screenshot")
                    except Exception as conn_err:
                        logger.error(f"Browser connection lost before screenshot: {conn_err}")
                        raise
                    
                    # Take screenshot once and save to file - also capture bytes for AI analysis
                    # Taking two separate screenshots can destabilize Pyppeteer connection
                    screenshot_path, screenshot_bytes = await self._take_screenshot_with_bytes(browser_page, page_id)
                    logger.warning(f"DEBUG run_single_test: screenshot done, path={screenshot_path}, bytes={len(screenshot_bytes) if screenshot_bytes else 0}")

                # Check if project has AI testing enabled
                ai_findings = []
                ai_analysis_results = {}
                
                run_ai = False
                ai_tests_to_run = []
                
                if project_config:
                    if project_config.get('enable_ai_testing', False):
                        run_ai = True
                        ai_tests_to_run = project_config.get('ai_tests', [])
                        logger.info(f"AI testing enabled, will run tests: {ai_tests_to_run}")
                
                # Get API key from config
                ai_api_key = None
                try:
                    from config import config
                    ai_api_key = getattr(config, 'CLAUDE_API_KEY', None)
                except Exception as e:
                    logger.warning(f"Could not get CLAUDE_API_KEY: {e}")
                
                logger.warning(f"AI analysis decision - run_ai: {run_ai}, has_api_key: {bool(ai_api_key)}, has_screenshot: {bool(screenshot_bytes)}, tests_to_run: {ai_tests_to_run}")
                
                # Run AI analysis if enabled
                if run_ai and ai_api_key and screenshot_bytes and ai_tests_to_run:
                    analyzer = None
                    try:
                        from auto_a11y.ai import ClaudeAnalyzer
                        
                        page_html = await browser_page.content()
                        analyzer = ClaudeAnalyzer(ai_api_key)
                        
                        logger.warning(f"Running AI accessibility analysis with tests: {ai_tests_to_run}")
                        ai_results = await analyzer.analyze_page(
                            screenshot=screenshot_bytes,
                            html=page_html,
                            analyses=ai_tests_to_run,
                            test_config=test_config
                        )
                        
                        ai_findings = ai_results.get('findings', [])
                        ai_analysis_results = ai_results.get('raw_results', {})
                        
                        logger.warning(f"AI analysis found {len(ai_findings)} issues")
                        if ai_findings:
                            logger.warning(f"AI finding IDs: {[f.id if hasattr(f, 'id') else str(f) for f in ai_findings]}")
                        
                    except Exception as e:
                        logger.error(f"AI analysis failed: {e}")
                    finally:
                        if analyzer and hasattr(analyzer, 'client'):
                            try:
                                await analyzer.client.aclose()
                            except Exception:
                                pass

                # Process results
                duration_ms = 0  # Will be set by caller
                test_result = self.result_processor.process_test_results(
                    page_id=page_id,
                    raw_results=raw_results,
                    screenshot_path=screenshot_path,
                    duration_ms=duration_ms,
                    ai_findings=ai_findings,
                    ai_analysis_results=ai_analysis_results
                )

                return test_result

            # Run multi-state testing with fresh pages for stability
            results = await self.multi_state_runner.test_page_multi_state(
                page=browser_page,
                page_id=page.id,
                scripts=multi_state_scripts,
                test_function=run_single_test,
                session_id=session_id,
                browser_manager=self.browser_manager,
                page_url=page.url,
                authenticated_user=authenticated_user,
                login_automation=self.login_automation
            )

            # Add authenticated user information to all results
            if authenticated_user:
                user_info = {
                    'user_id': authenticated_user.id,
                    'username': authenticated_user.username,
                    'display_name': authenticated_user.display_name,
                    'roles': authenticated_user.roles
                }

                for result in results:
                    # Add to result metadata
                    result.metadata['authenticated_user'] = user_info

                    # Add to each violation's metadata
                    for violation in result.violations:
                        violation.metadata['authenticated_user'] = user_info

                    # Add to each warning's metadata
                    for warning in result.warnings:
                        warning.metadata['authenticated_user'] = user_info

                    # Add to each info item's metadata
                    for info in result.info:
                        info.metadata['authenticated_user'] = user_info

                    # Add to each discovery item's metadata
                    for discovery in result.discovery:
                        discovery.metadata['authenticated_user'] = user_info

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
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

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
        
        finally:
            # Clean up: the multi_state_runner manages its own browser lifecycle via
            # _prepare_browser_for_state, so we don't need to close browser_page here.
            # The browser is stopped/restarted between states and the final page is
            # managed by the multi_state_runner. Just ensure browser is stopped.
            pass

    async def test_pages(
        self,
        pages: List[Page],
        parallel: int = 1,
        take_screenshots: bool = True,
        progress_callback: Optional[callable] = None,
        website_user_id: Optional[str] = None
    ) -> List[TestResult]:
        """
        Test multiple pages with multi-state support

        Args:
            pages: Pages to test
            parallel: Number of parallel tests
            take_screenshots: Whether to capture screenshots
            progress_callback: Progress callback function
            website_user_id: Optional user ID for authenticated testing

        Returns:
            List of test results (flattened from all states)
        """
        results = []
        total = len(pages)
        completed = 0

        # Process pages in batches
        for i in range(0, total, parallel):
            batch = pages[i:i+parallel]

            # Test batch in parallel - use test_page_multi_state for each page
            tasks = [
                self.test_page_multi_state(
                    page=page,
                    enable_multi_state=True,
                    take_screenshot=take_screenshots,
                    website_user_id=website_user_id
                )
                for page in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results - test_page_multi_state returns List[TestResult]
            for result_list in batch_results:
                if isinstance(result_list, Exception):
                    logger.error(f"Test failed with exception: {result_list}")
                elif isinstance(result_list, list):
                    # Flatten the list of results from multi-state testing
                    results.extend(result_list)
                else:
                    # Single result (shouldn't happen with multi_state, but handle it)
                    results.append(result_list)
            
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
            Screenshot file path (relative to project root for Flask static serving)
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

            # Return relative path for Flask static serving
            # Convert absolute path to relative from project root
            import os
            try:
                # Get path relative to current working directory (project root)
                relative_path = os.path.relpath(filepath, os.getcwd())
                logger.debug(f"Screenshot saved: {filepath} (relative: {relative_path})")
                return relative_path
            except ValueError:
                # If relative path cannot be computed (different drives on Windows), return just filename
                logger.debug(f"Screenshot saved: {filepath} (returning: {self.screenshot_dir.name}/{filename})")
                return f"{self.screenshot_dir.name}/{filename}"

        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None

    async def _take_screenshot_with_bytes(self, browser_page, page_id: str) -> tuple:
        """
        Take screenshot of page and return both path and bytes.
        
        This method takes a single screenshot to avoid destabilizing the Pyppeteer
        connection that can occur when taking multiple screenshots in succession.

        Args:
            browser_page: Pyppeteer page object
            page_id: Page ID for filename

        Returns:
            Tuple of (screenshot file path, screenshot bytes)
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"page_{page_id}_{timestamp}.jpg"
            filepath = self.screenshot_dir / filename

            # Take screenshot once - Pyppeteer returns bytes and saves to file if path provided
            screenshot_bytes = await browser_page.screenshot({
                'path': str(filepath),
                'fullPage': True,
                'type': 'jpeg',
                'quality': 80
            })

            # Return relative path for Flask static serving
            import os
            try:
                relative_path = os.path.relpath(filepath, os.getcwd())
                logger.debug(f"Screenshot saved: {filepath} (relative: {relative_path})")
                return relative_path, screenshot_bytes
            except ValueError:
                logger.debug(f"Screenshot saved: {filepath} (returning: {self.screenshot_dir.name}/{filename})")
                return f"{self.screenshot_dir.name}/{filename}", screenshot_bytes

        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None, None
    
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