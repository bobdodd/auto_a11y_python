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

    async def test_page_multi_state(
        self,
        page,
        page_id: str,
        scripts: List[PageSetupScript],
        test_function,
        session_id: str,
        environment_vars: Optional[Dict[str, str]] = None,
        browser_manager=None,
        page_url: Optional[str] = None
    ) -> List[TestResult]:
        """
        Test page across multiple states

        Workflow:
        1. Test initial state (if any script has test_before_execution=True)
        2. For each script:
           - Execute script
           - Validate state
           - Test after execution (if test_after_execution=True)
        3. Create fresh page after each state to prevent browser stability issues
        4. Link all results together

        Args:
            page: Pyppeteer page object
            page_id: ID of page being tested
            scripts: List of scripts to execute
            test_function: Async function that runs accessibility tests
            session_id: Script execution session ID
            environment_vars: Environment variables for scripts
            browser_manager: BrowserManager instance for creating fresh pages
            page_url: URL to navigate to when creating fresh pages

        Returns:
            List of TestResult objects (one per state tested)
        """
        logger.warning(f"DEBUG: test_page_multi_state called with {len(scripts)} scripts for page_id={page_id}")
        results = []
        state_sequence = 0
        scripts_executed_so_far = []
        
        # Track the current page - we'll create fresh pages for stability
        # Keep reference to original page so we don't close it (it's managed by caller's context manager)
        original_page = page
        current_page = page
        actual_page_url = page_url or page.url

        # Check if we need to test initial state (before any scripts)
        test_initial_state = any(script.test_before_execution for script in scripts)
        logger.warning(f"DEBUG: test_initial_state={test_initial_state}")

        if test_initial_state:
            logger.warning(f"DEBUG: Testing initial state (before any scripts)")
            logger.info(f"Testing page {page_id} in initial state (sequence {state_sequence})")

            # Create initial state
            initial_state = PageTestState(
                state_id=f"{page_id}_state_{state_sequence}",
                description="Initial page state (before script execution)",
                scripts_executed=[],
                elements_clicked=[],
                elements_visible=[],
                elements_hidden=[]
            )

            # Run accessibility tests
            test_result = await test_function(current_page, page_id)
            logger.warning(f"DEBUG: Initial state tests complete, violations={len(test_result.violations)}")

            # Add state metadata
            test_result.page_state = initial_state.to_dict()
            test_result.state_sequence = state_sequence
            test_result.session_id = session_id
            test_result.metadata['state_description'] = initial_state.description

            results.append(test_result)
            state_sequence += 1
            
            # Restart browser for next state if browser_manager available
            if browser_manager:
                logger.warning(f"DEBUG: Restarting browser after initial state test")
                try:
                    await browser_manager.stop()
                    await asyncio.sleep(0.5)
                    await browser_manager.start()
                    await asyncio.sleep(0.5)
                    
                    new_page = await browser_manager.create_page()
                    response = await new_page.goto(actual_page_url, {
                        'waitUntil': 'networkidle2',
                        'timeout': 30000
                    })
                    if response:
                        logger.warning(f"DEBUG: Fresh browser navigation successful, status={response.status}")
                        await asyncio.sleep(1.0)
                        current_page = new_page
                        original_page = new_page
                        logger.warning(f"DEBUG: Switched to fresh browser")
                    else:
                        logger.warning(f"DEBUG: Fresh browser navigation returned None")
                except Exception as e:
                    logger.error(f"Failed to restart browser after initial state: {e}")

        # Execute scripts and test after each one
        for script_idx, script in enumerate(scripts):
            logger.info(f"Processing script '{script.name}' (ID: {script.id})")
            logger.warning(f"DEBUG: Script ID={script.id} '{script.name}' clear settings - cookies={script.clear_cookies_before}, localStorage={script.clear_local_storage_before}")

            try:
                await asyncio.wait_for(current_page.evaluate('() => document.readyState'), timeout=5.0)
                logger.warning(f"DEBUG: Page connection OK at start of script loop")
            except Exception as conn_error:
                logger.error(f"Browser connection lost before script '{script.name}': {conn_error}")
                break

            # Clear cookies and/or localStorage if configured
            # Restart browser to ensure clean state (no cookies/localStorage)
            if script.clear_cookies_before or script.clear_local_storage_before:
                logger.warning(f"DEBUG: Entering clearing block - restarting browser for clean state")
                if browser_manager:
                    try:
                        await browser_manager.stop()
                        await asyncio.sleep(0.5)
                        await browser_manager.start()
                        await asyncio.sleep(0.5)
                        
                        new_page = await browser_manager.create_page()
                        response = await new_page.goto(actual_page_url, {
                            'waitUntil': 'networkidle2',
                            'timeout': 30000
                        })
                        
                        if response:
                            logger.warning(f"DEBUG: Fresh browser navigation complete, status={response.status}")
                            await asyncio.sleep(1.0)
                            current_page = new_page
                            original_page = new_page
                            logger.warning(f"DEBUG: Switched to fresh browser after clearing")
                            
                            # Wait for script target selector if defined
                            if script.steps and script.steps[0].selector:
                                try:
                                    selector = script.steps[0].selector
                                    logger.warning(f"DEBUG: Waiting for script target selector: {selector}")
                                    if selector.startswith('/'):
                                        await current_page.waitForXPath(selector, {'timeout': 5000})
                                    else:
                                        await current_page.waitForSelector(selector, {'timeout': 5000})
                                    logger.warning(f"DEBUG: Script target selector found and ready")
                                except Exception as e:
                                    logger.warning(f"DEBUG: Could not find script target selector (will try anyway): {e}")
                        else:
                            logger.error(f"DEBUG: Fresh browser navigation failed")
                            continue
                    except Exception as e:
                        logger.error(f"Error restarting browser: {e}")
                        logger.warning(f"Skipping script '{script.name}' due to browser restart failure")
                        continue
                else:
                    logger.warning(f"DEBUG: No browser_manager, skipping clear cookies (cannot restart browser)")
                    continue

            # Final connection check before script execution
            try:
                await asyncio.wait_for(current_page.evaluate('() => true'), timeout=2.0)
            except Exception as conn_err:
                logger.error(f"Browser connection lost just before executing script '{script.name}': {conn_err}")
                break

            # Execute script
            logger.warning(f"DEBUG: About to execute script '{script.name}'")
            script_result = await self.script_executor.execute_script(
                page=current_page,
                script=script,
                environment_vars=environment_vars
            )
            logger.warning(f"DEBUG: Script execution complete - success={script_result['success']}")

            # Wait for page to stabilize after script execution
            # Script may have triggered animations, DOM changes, or async operations
            await asyncio.sleep(1.0)
            logger.warning(f"DEBUG: Post-script wait complete")

            # Verify page connection is still alive
            try:
                await asyncio.wait_for(current_page.evaluate('() => document.readyState'), timeout=5.0)
                logger.warning(f"DEBUG: Page connection verified")
            except Exception as conn_error:
                logger.error(f"Browser connection lost after script execution: {conn_error}")
                # Try to continue with remaining scripts rather than abort completely
                continue

            scripts_executed_so_far.append(script.id)

            # Check if script execution succeeded
            if not script_result['success']:
                logger.warning(f"Script '{script.name}' failed, skipping state validation and testing")
                continue

            # Create expected state after script execution
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
                logger.info(f"Validating page state after script '{script.name}'")
                state_violations = await self.state_validator.validate_state(
                    page=current_page,
                    expected_state=expected_state
                )

                if state_violations:
                    logger.warning(f"State validation found {len(state_violations)} violations")

            # Test after script execution if configured
            if script.test_after_execution:
                logger.warning(f"DEBUG: test_after_execution=True, running post-script tests")
                logger.info(f"Testing page {page_id} after script '{script.name}' (sequence {state_sequence})")

                # Verify page connection before running tests
                try:
                    current_url = current_page.url
                    logger.warning(f"DEBUG: Page URL before tests: {current_url}")
                except Exception as url_error:
                    logger.error(f"Cannot get page URL - connection lost: {url_error}")
                    break

                # Run accessibility tests
                try:
                    test_result = await test_function(current_page, page_id)
                    logger.warning(f"DEBUG: Post-script tests complete, violations={len(test_result.violations)}")
                except Exception as test_error:
                    logger.error(f"Post-script test execution failed: {test_error}")
                    # Create a minimal error result
                    from auto_a11y.models import TestResult
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

                # Add state validation violations to test result
                test_result.violations.extend(state_violations)

                # Add state metadata
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

        # No cleanup needed - browser will be stopped by caller or reused

        # Link all results together
        result_ids = [result.id for result in results if result.id]
        for result in results:
            result.related_result_ids = [rid for rid in result_ids if rid != result.id]

        logger.warning(f"DEBUG: Multi-state testing complete: {len(results)} test results generated")
        logger.warning(f"DEBUG: Returning results list with {len(results)} items")

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
