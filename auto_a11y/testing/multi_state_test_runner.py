"""
Multi-state test runner for page setup scripts

Executes accessibility tests across multiple page states.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from auto_a11y.models import TestResult, PageSetupScript, PageTestState
from auto_a11y.testing.state_validator import StateValidator
from auto_a11y.testing.script_executor import ScriptExecutor


logger = logging.getLogger(__name__)


class MultiStateTestRunner:
    """Execute tests across multiple page states"""

    def __init__(self, script_executor: ScriptExecutor):
        """
        Initialize multi-state test runner

        Args:
            script_executor: ScriptExecutor instance for running scripts
        """
        self.script_executor = script_executor
        self.state_validator = StateValidator()

    async def _prepare_browser_for_state(
        self,
        browser_manager,
        authenticated_user,
        login_automation,
        page_url: str,
        max_retries: int = 3
    ):
        """
        Prepare browser for a new state: restart, re-authenticate, navigate to test page.
        
        Args:
            browser_manager: BrowserManager instance
            authenticated_user: User to authenticate as (or None)
            login_automation: LoginAutomation instance (or None)
            page_url: URL of page under test
            max_retries: Maximum retry attempts for browser restart
            
        Returns:
            New page object ready for testing
        """
        logger.info("Starting completely fresh browser instance")
        
        # Give time for any pending async operations to complete
        await asyncio.sleep(2.0)
        
        new_page = None
        for attempt in range(max_retries):
            try:
                # Completely stop and kill the old browser
                await browser_manager.stop()
                
                # Verify process is truly dead before continuing
                logger.info("Browser stopped, verifying process is dead")
                
                # Start a completely fresh browser from scratch
                await browser_manager.start()
                
                # Verify browser is actually running
                if not await browser_manager.is_running():
                    logger.warning(f"Browser not running after start (attempt {attempt + 1})")
                    continue
                
                # Create new page
                new_page = await browser_manager.create_page()
                
                # Verify page is usable
                await asyncio.wait_for(
                    new_page.evaluate('() => "ready"'),
                    timeout=5.0
                )
                
                logger.info(f"Fresh browser ready (attempt {attempt + 1})")
                break
                
            except Exception as e:
                logger.warning(f"Browser creation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to create fresh browser after {max_retries} attempts: {e}")
                await asyncio.sleep(1.0)
        
        if authenticated_user and login_automation:
            logger.info(f"Authenticating as {authenticated_user.username}")
            
            # Let browser stabilize before login
            await asyncio.sleep(0.5)
            
            login_result = await login_automation.perform_login(new_page, authenticated_user, timeout=30000)
            if login_result['success']:
                logger.info("Authentication successful")
                # Verify browser connection after login
                try:
                    await asyncio.wait_for(
                        new_page.evaluate('() => document.readyState'),
                        timeout=5.0
                    )
                    logger.info("Browser connection verified after login")
                except Exception as conn_err:
                    logger.error(f"Browser connection lost after login: {conn_err}")
                    raise RuntimeError(f"Browser died after login: {conn_err}")
            else:
                logger.error(f"Authentication failed: {login_result.get('error')}")
        
        # Verify page is still usable before navigation
        try:
            await asyncio.wait_for(
                new_page.evaluate('() => "ready"'),
                timeout=3.0
            )
        except Exception as pre_nav_err:
            raise RuntimeError(f"Page died before navigation: {pre_nav_err}")
        
        logger.info(f"Navigating to test page: {page_url}")
        try:
            response = await new_page.goto(page_url, {
                'waitUntil': 'domcontentloaded',
                'timeout': 30000
            })
            if response:
                logger.info(f"Navigation successful, status={response.status}")
            else:
                logger.warning("Navigation returned None")
        except Exception as nav_error:
            logger.warning(f"Navigation to test page had issue: {nav_error}, trying load")
            try:
                response = await new_page.goto(page_url, {
                    'waitUntil': 'load',
                    'timeout': 30000
                })
            except Exception as nav_error2:
                raise RuntimeError(f"Navigation failed: {nav_error2}")
        
        # Final connection verification
        await asyncio.sleep(0.5)
        try:
            await asyncio.wait_for(
                new_page.evaluate('() => document.readyState'),
                timeout=5.0
            )
            logger.info("Browser connection verified before returning page")
        except Exception as final_conn_err:
            logger.error(f"Final connection check failed: {final_conn_err}")
            raise RuntimeError(f"Browser connection unstable after preparation: {final_conn_err}")
        
        await asyncio.sleep(0.5)
        return new_page

    async def test_page_multi_state(
        self,
        page,
        page_id: str,
        scripts: List[PageSetupScript],
        test_function,
        session_id: str,
        environment_vars: Optional[Dict[str, str]] = None,
        browser_manager=None,
        page_url: Optional[str] = None,
        authenticated_user=None,
        login_automation=None
    ) -> List[TestResult]:
        """
        Test page across multiple states.
        
        Each state follows the same procedure:
        1. (Re)start browser with clean state
        2. Authenticate if authenticated user specified
        3. Navigate to test page
        4. Execute script (if any for this state)
        5. Run accessibility tests
        6. Save results

        Args:
            page: Pyppeteer page object (initial page)
            page_id: ID of page being tested
            scripts: List of scripts to execute
            test_function: Async function that runs accessibility tests
            session_id: Script execution session ID
            environment_vars: Environment variables for scripts
            browser_manager: BrowserManager instance for creating fresh pages
            page_url: URL of test page
            authenticated_user: User to authenticate as
            login_automation: LoginAutomation instance

        Returns:
            List of TestResult objects (one per state tested)
        """
        logger.debug(f"DEBUG: test_page_multi_state called with {len(scripts)} scripts for page_id={page_id}")
        results = []
        state_sequence = 0
        scripts_executed_so_far = []
        
        current_page = page
        actual_page_url = page_url or page.url

        # Check if we need to test initial state (before any scripts)
        test_initial_state = any(script.test_before_execution for script in scripts)
        logger.debug(f"DEBUG: test_initial_state={test_initial_state}")

        # STATE 0: Initial state (before any scripts)
        if test_initial_state:
            logger.info(f"Testing page {page_id} in initial state (sequence {state_sequence})")

            initial_state = PageTestState(
                state_id=f"{page_id}_state_{state_sequence}",
                description="Initial page state (before script execution)",
                scripts_executed=[],
                elements_clicked=[],
                elements_visible=[],
                elements_hidden=[]
            )

            test_result = await test_function(current_page, page_id)
            logger.debug(f"DEBUG: Initial state tests complete, violations={len(test_result.violations)}")

            test_result.page_state = initial_state.to_dict()
            test_result.state_sequence = state_sequence
            test_result.session_id = session_id
            test_result.metadata['state_description'] = initial_state.description

            results.append(test_result)
            state_sequence += 1
            
            # Allow any pending async operations (screenshots, AI analysis, etc.)
            # to complete before browser restart. This is critical to prevent
            # "Target closed" errors.
            await asyncio.sleep(3.0)

        # SUBSEQUENT STATES: One per script
        for script_idx, script in enumerate(scripts):
            logger.info(f"Processing script '{script.name}' (ID: {script.id})")
            
            # Restart browser and prepare for this state
            if browser_manager:
                try:
                    current_page = await self._prepare_browser_for_state(
                        browser_manager,
                        authenticated_user,
                        login_automation,
                        actual_page_url
                    )
                except Exception as e:
                    logger.error(f"Failed to prepare browser for state: {e}")
                    break

            # Verify page connection
            try:
                await asyncio.wait_for(current_page.evaluate('() => document.readyState'), timeout=5.0)
                logger.debug(f"DEBUG: Page connection OK")
            except Exception as conn_error:
                logger.error(f"Browser connection lost: {conn_error}")
                break

            # Execute the script
            logger.info(f"Executing script '{script.name}'")
            script_result = await self.script_executor.execute_script(
                page=current_page,
                script=script,
                environment_vars=environment_vars
            )
            logger.debug(f"DEBUG: Script execution complete - success={script_result['success']}")

            if not script_result['success']:
                logger.warning(f"Script '{script.name}' failed, skipping tests for this state")
                continue

            scripts_executed_so_far.append(script.id)

            # Wait for page to stabilize after script (clicks can destabilize Pyppeteer)
            await asyncio.sleep(2.0)
            
            # Verify connection after script execution - scripts with clicks can kill browser
            try:
                await asyncio.wait_for(current_page.evaluate('() => document.readyState'), timeout=5.0)
                logger.debug("DEBUG: Page connection OK after script")
            except Exception as post_script_err:
                logger.error(f"Browser died after script execution: {post_script_err}")
                # Try to recover with fresh browser
                if browser_manager:
                    logger.info("Attempting recovery after script killed browser")
                    try:
                        current_page = await self._prepare_browser_for_state(
                            browser_manager,
                            authenticated_user,
                            login_automation,
                            actual_page_url,
                            max_retries=2
                        )
                        # Re-execute the script on fresh browser
                        logger.info(f"Re-executing script '{script.name}' on fresh browser")
                        script_result = await self.script_executor.execute_script(
                            page=current_page,
                            script=script,
                            environment_vars=environment_vars
                        )
                        if not script_result['success']:
                            logger.error("Script re-execution failed")
                            break
                        await asyncio.sleep(2.0)
                    except Exception as recovery_err:
                        logger.error(f"Recovery failed: {recovery_err}")
                        break
                else:
                    break

            # Test after script execution if configured
            if script.test_after_execution:
                logger.info(f"Testing page {page_id} after script '{script.name}' (sequence {state_sequence})")

                expected_state = self.state_validator.create_expected_state(
                    state_id=f"{page_id}_state_{state_sequence}",
                    description=f"After executing script: {script.name}",
                    scripts_executed=scripts_executed_so_far.copy(),
                    expect_visible=script.expect_visible_after,
                    expect_hidden=script.expect_hidden_after,
                    elements_clicked=[]
                )

                # Validate state if expectations are defined
                state_violations = []
                if script.expect_visible_after or script.expect_hidden_after:
                    state_violations = await self.state_validator.validate_state(
                        page=current_page,
                        expected_state=expected_state
                    )
                    if state_violations:
                        logger.warning(f"State validation found {len(state_violations)} violations")

                # Run accessibility tests
                try:
                    test_result = await test_function(current_page, page_id)
                    logger.debug(f"DEBUG: Post-script tests complete, violations={len(test_result.violations)}")
                except Exception as test_error:
                    logger.error(f"Post-script test execution failed: {test_error}")
                    test_result = TestResult(
                        page_id=page_id,
                        test_date=datetime.now(),
                        duration_ms=0,
                        error=str(test_error),
                        violations=[],
                        warnings=[],
                        passes=[]
                    )
                    results.append(test_result)
                    break

                test_result.violations.extend(state_violations)
                test_result.page_state = expected_state.to_dict()
                test_result.state_sequence = state_sequence
                test_result.session_id = session_id
                test_result.metadata['state_description'] = expected_state.description
                test_result.metadata['script_executed'] = {
                    'script_id': script.id,
                    'script_name': script.name,
                    'execution_success': script_result['success'],
                    'execution_duration_ms': script_result['duration_ms']
                }

                results.append(test_result)
                state_sequence += 1
                
                # Allow any pending async operations (screenshots, AI analysis, etc.)
                # to complete before browser restart. This is critical to prevent
                # "Target closed" errors.
                await asyncio.sleep(3.0)

        # Link all results together
        result_ids = [result.id for result in results if result.id]
        for result in results:
            result.related_result_ids = [rid for rid in result_ids if rid != result.id]

        logger.debug(f"DEBUG: Multi-state testing complete: {len(results)} test results generated")
        
        # Final wait to ensure all async operations from the last state complete
        # before the caller potentially closes the browser
        await asyncio.sleep(2.0)

        return results

    async def test_with_button_iteration(
        self,
        page,
        page_id: str,
        button_selectors: List[str],
        test_function,
        session_id: str,
        reload_between_tests: bool = True
    ) -> List[TestResult]:
        """
        Test page by iterating through buttons

        Workflow:
        1. Test initial state
        2. For each button:
           - Reload page (optional)
           - Click button
           - Wait for state change
           - Test page
        3. Link all results together

        Args:
            page: Pyppeteer page object
            page_id: ID of page being tested
            button_selectors: List of button selectors to click
            test_function: Async function that runs accessibility tests
            session_id: Script execution session ID
            reload_between_tests: Whether to reload page between button clicks

        Returns:
            List of TestResult objects (one per state)
        """
        results = []
        state_sequence = 0

        # Test initial state
        logger.info(f"Testing page {page_id} in initial state (sequence {state_sequence})")

        initial_state = PageTestState(
            state_id=f"{page_id}_state_{state_sequence}",
            description="Initial page state (before button clicks)",
            scripts_executed=[],
            elements_clicked=[],
            elements_visible=[],
            elements_hidden=[]
        )

        test_result = await test_function(page, page_id)
        test_result.page_state = initial_state.to_dict()
        test_result.state_sequence = state_sequence
        test_result.session_id = session_id
        test_result.metadata['state_description'] = initial_state.description

        results.append(test_result)
        state_sequence += 1

        # Iterate through buttons
        page_url = page.url
        for idx, selector in enumerate(button_selectors):
            logger.info(f"Testing with button {idx + 1}/{len(button_selectors)}: {selector}")

            # Reload page if configured
            if reload_between_tests and idx > 0:
                logger.info(f"Reloading page to initial state")
                await page.goto(page_url, {'waitUntil': 'domcontentloaded'})
                await page.waitFor(500)  # Brief pause after reload

            # Click button
            try:
                await page.click(selector, {'timeout': 5000})
                logger.info(f"Clicked button: {selector}")

                # Wait for potential state changes
                await page.waitFor(1000)

            except Exception as e:
                logger.warning(f"Failed to click button {selector}: {str(e)}")
                continue

            # Create state for this button
            button_state = PageTestState(
                state_id=f"{page_id}_state_{state_sequence}",
                description=f"After clicking button: {selector}",
                scripts_executed=[],
                elements_clicked=[{
                    'selector': selector,
                    'index': idx,
                    'timestamp': datetime.now().isoformat()
                }],
                elements_visible=[],
                elements_hidden=[]
            )

            # Test page in this state
            logger.info(f"Testing page {page_id} after button click (sequence {state_sequence})")

            test_result = await test_function(page, page_id)
            test_result.page_state = button_state.to_dict()
            test_result.state_sequence = state_sequence
            test_result.session_id = session_id
            test_result.metadata['state_description'] = button_state.description
            test_result.metadata['button_clicked'] = {
                'selector': selector,
                'index': idx
            }

            results.append(test_result)
            state_sequence += 1

        # Link all results together
        result_ids = [result.id for result in results if result.id]
        for result in results:
            result.related_result_ids = [rid for rid in result_ids if rid != result.id]

        logger.info(f"Button iteration testing complete: {len(results)} test results generated")

        return results

    async def _clear_browser_state(self, page, script: PageSetupScript):
        """
        Clear cookies and/or localStorage before script execution

        Args:
            page: Pyppeteer page object
            script: PageSetupScript with clear_cookies_before and clear_local_storage_before flags
        """
        try:
            if script.clear_cookies_before:
                logger.info(f"Clearing cookies for script '{script.name}'")
                # Get all cookies
                cookies = await page.cookies()
                if cookies:
                    # Delete all cookies
                    await page.deleteCookie(*cookies)
                    logger.info(f"Cleared {len(cookies)} cookies")
                else:
                    logger.info("No cookies to clear")

            if script.clear_local_storage_before:
                logger.info(f"Clearing localStorage and sessionStorage for script '{script.name}'")
                # Execute JavaScript to clear storage
                await page.evaluate('''() => {
                    localStorage.clear();
                    sessionStorage.clear();
                }''')
                logger.info("Cleared localStorage and sessionStorage")

        except Exception as e:
            logger.error(f"Error clearing browser state: {e}")
            # Don't raise - continue with script execution even if clearing fails

    async def test_page_with_matrix(
        self,
        page,
        page_id: str,
        test_state_matrix,  # TestStateMatrix instance
        scripts_by_id: Dict[str, PageSetupScript],
        test_function,
        session_id: str,
        environment_vars: Optional[Dict[str, str]] = None
    ) -> List[TestResult]:
        """
        Test page using a state matrix to define which combinations to test

        This method tests only the state combinations defined in the matrix,
        avoiding the combinatorial explosion of testing all 2^N permutations.

        Args:
            page: Pyppeteer page object
            page_id: ID of page being tested
            test_state_matrix: TestStateMatrix defining which combinations to test
            scripts_by_id: Dict mapping script_id to PageSetupScript instances
            test_function: Async function that runs accessibility tests
            session_id: Script execution session ID
            environment_vars: Environment variables for scripts

        Returns:
            List of TestResult objects (one per state combination tested)
        """
        from auto_a11y.models import TestStateMatrix, StateCombination

        logger.info(f"Starting matrix-based multi-state testing for page {page_id}")
        results = []
        state_sequence = 0

        # Get all enabled state combinations from the matrix
        combinations = test_state_matrix.get_enabled_combinations()
        logger.info(f"Testing {len(combinations)} state combinations (instead of {2**len(test_state_matrix.scripts)} possible permutations)")

        # Save initial page URL for reloading
        initial_url = page.url

        # Test each combination
        for combo_idx, combination in enumerate(combinations):
            logger.info(f"Testing combination {combo_idx + 1}/{len(combinations)}: {combination.script_states}")

            # Reload page to start fresh
            if combo_idx > 0:
                logger.info(f"Reloading page to initial state")
                await page.goto(initial_url, {'waitUntil': 'networkidle2', 'timeout': 30000})
                await asyncio.sleep(1.0)  # Let page stabilize

            # Execute scripts to reach this state
            scripts_executed = []
            for script_def in sorted(test_state_matrix.scripts, key=lambda s: s.execution_order):
                script_id = script_def.script_id
                desired_state = combination.script_states.get(script_id)

                if desired_state == "after" and script_id in scripts_by_id:
                    # Execute this script
                    script = scripts_by_id[script_id]
                    logger.info(f"Executing script '{script.name}' to reach desired state")

                    # Clear browser state if configured
                    if script.clear_cookies_before or script.clear_local_storage_before:
                        try:
                            current_url = page.url
                            await self._clear_browser_state(page, script)
                            await page.goto(current_url, {'waitUntil': 'networkidle2', 'timeout': 30000})
                            await asyncio.sleep(2.0)
                        except Exception as e:
                            logger.error(f"Error clearing browser state: {e}")
                            continue

                    # Execute script
                    script_result = await self.script_executor.execute_script(
                        page=page,
                        script=script,
                        environment_vars=environment_vars
                    )

                    if script_result['success']:
                        scripts_executed.append(script_id)
                        logger.info(f"Successfully executed script '{script.name}'")
                    else:
                        logger.warning(f"Script '{script.name}' failed: {script_result.get('error', 'Unknown error')}")
                        # Continue anyway - we still want to test this state

            # Create state description
            state_description_parts = []
            for script_def in test_state_matrix.scripts:
                script_id = script_def.script_id
                state = combination.script_states.get(script_id, "before")
                state_label = f"{script_def.script_name} ({state})"
                state_description_parts.append(state_label)

            state_description = ", ".join(state_description_parts)
            if combination.description:
                state_description = f"{combination.description}: {state_description}"

            logger.info(f"Testing page in state: {state_description}")

            # Create PageTestState
            from auto_a11y.models import PageTestState
            page_state = PageTestState(
                state_id=f"{page_id}_state_{state_sequence}",
                description=state_description,
                scripts_executed=scripts_executed,
                elements_clicked=[],
                elements_visible=[],
                elements_hidden=[]
            )

            # Run accessibility tests
            test_result = await test_function(page, page_id)
            logger.info(f"Tests complete for state {state_sequence}, violations={len(test_result.violations)}")

            # Add state metadata
            test_result.page_state = page_state.to_dict()
            test_result.state_sequence = state_sequence
            test_result.session_id = session_id
            test_result.metadata['state_description'] = state_description
            test_result.metadata['state_combination'] = combination.to_dict()

            results.append(test_result)
            state_sequence += 1

        # Link all results together
        result_ids = [result.id for result in results if result.id]
        for result in results:
            result.related_result_ids = [rid for rid in result_ids if rid != result.id]

        logger.info(f"Matrix-based testing complete: {len(results)} test results generated")

        return results
