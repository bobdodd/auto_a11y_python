"""
Multi-state test runner for page setup scripts

Executes accessibility tests across multiple page states using Playwright.

This version uses Playwright's browser contexts for state isolation, which is
much faster than restarting the browser between states (the approach required
with Pyppeteer due to connection instability).
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from playwright.async_api import Page, BrowserContext

from auto_a11y.models import TestResult, PageSetupScript, PageTestState
from auto_a11y.testing.state_validator import StateValidator
from auto_a11y.testing.script_executor import ScriptExecutor


logger = logging.getLogger(__name__)


class MultiStateTestRunner:
    """Execute tests across multiple page states using browser context isolation"""

    def __init__(self, script_executor: ScriptExecutor):
        """
        Initialize multi-state test runner

        Args:
            script_executor: ScriptExecutor instance for running scripts
        """
        self.script_executor = script_executor
        self.state_validator = StateValidator()

    async def _create_fresh_context_and_page(
        self,
        browser_manager,
        authenticated_user,
        login_automation,
        page_url: str
    ) -> tuple:
        """
        Create a fresh browser context and page for testing a new state.

        Uses Playwright's browser contexts for isolation - much faster than
        restarting the entire browser (which was required with Pyppeteer).

        Args:
            browser_manager: BrowserManager instance
            authenticated_user: User to authenticate as (or None)
            login_automation: LoginAutomation instance (or None)
            page_url: URL of page under test

        Returns:
            Tuple of (context, page) ready for testing
        """
        logger.info("Creating fresh browser context for new state")

        # Create isolated context (clean cookies, localStorage, etc.)
        context = await browser_manager.create_context()
        page = await context.new_page()

        # Authenticate if needed
        if authenticated_user and login_automation:
            logger.info(f"Authenticating as {authenticated_user.username}")
            login_result = await login_automation.perform_login(page, authenticated_user, timeout=30000)
            if login_result['success']:
                logger.info("Authentication successful")
            else:
                logger.error(f"Authentication failed: {login_result.get('error')}")

        # Navigate to test page
        logger.info(f"Navigating to test page: {page_url}")
        response = await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
        if response:
            logger.debug(f"Navigation successful, status={response.status}")

        # Brief wait for page to stabilize
        await asyncio.sleep(0.3)

        return context, page

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
        Test page across multiple states using browser context isolation.

        Each state follows this procedure:
        1. Create fresh browser context (isolated cookies/storage)
        2. Authenticate if needed
        3. Navigate to test page
        4. Execute script (if any for this state)
        5. Run accessibility tests
        6. Close context

        Args:
            page: Playwright Page object (initial page)
            page_id: ID of page being tested
            scripts: List of scripts to execute
            test_function: Async function that runs accessibility tests
            session_id: Script execution session ID
            environment_vars: Environment variables for scripts
            browser_manager: BrowserManager instance for creating contexts
            page_url: URL of test page
            authenticated_user: User to authenticate as
            login_automation: LoginAutomation instance

        Returns:
            List of TestResult objects (one per state tested)
        """
        logger.debug(f"test_page_multi_state: {len(scripts)} scripts for page_id={page_id}")
        results = []
        state_sequence = 0
        scripts_executed_so_far = []

        current_page = page
        current_context = None
        actual_page_url = page_url or page.url

        # Check if we need to test initial state (before any scripts)
        test_initial_state = any(script.test_before_execution for script in scripts)

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
            logger.debug(f"Initial state tests complete, violations={len(test_result.violations)}")

            test_result.page_state = initial_state.to_dict()
            test_result.state_sequence = state_sequence
            test_result.session_id = session_id
            test_result.metadata['state_description'] = initial_state.description

            results.append(test_result)
            state_sequence += 1

        # SUBSEQUENT STATES: One per script
        for script_idx, script in enumerate(scripts):
            logger.info(f"Processing script '{script.name}' (ID: {script.id})")

            # Create fresh context for this state
            if browser_manager:
                # Close previous context if we created one
                if current_context:
                    try:
                        await browser_manager.close_context(current_context)
                    except Exception as e:
                        logger.debug(f"Error closing previous context: {e}")

                try:
                    current_context, current_page = await self._create_fresh_context_and_page(
                        browser_manager,
                        authenticated_user,
                        login_automation,
                        actual_page_url
                    )
                except Exception as e:
                    logger.error(f"Failed to create context for state: {e}")
                    break

            # Execute the script
            logger.info(f"Executing script '{script.name}'")
            script_result = await self.script_executor.execute_script(
                page=current_page,
                script=script,
                environment_vars=environment_vars
            )
            logger.debug(f"Script execution complete - success={script_result['success']}")

            if not script_result['success']:
                logger.warning(f"Script '{script.name}' failed, skipping tests for this state")
                continue

            scripts_executed_so_far.append(script.id)

            # Brief wait for page to stabilize after script
            await asyncio.sleep(0.5)

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
                    logger.debug(f"Post-script tests complete, violations={len(test_result.violations)}")
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

        # Clean up the last context we created
        if current_context and browser_manager:
            try:
                await browser_manager.close_context(current_context)
            except Exception as e:
                logger.debug(f"Error closing final context: {e}")

        # Link all results together
        result_ids = [result.id for result in results if result.id]
        for result in results:
            result.related_result_ids = [rid for rid in result_ids if rid != result.id]

        logger.debug(f"Multi-state testing complete: {len(results)} test results generated")

        return results

    async def test_with_button_iteration(
        self,
        page: Page,
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
            page: Playwright Page object
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
                await page.goto(page_url, wait_until='domcontentloaded')
                await page.wait_for_timeout(300)

            # Click button
            try:
                await page.click(selector, timeout=5000)
                logger.info(f"Clicked button: {selector}")

                # Wait for potential state changes
                await page.wait_for_timeout(500)

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

    async def _clear_browser_state(self, page: Page, script: PageSetupScript):
        """
        Clear cookies and/or localStorage before script execution

        Args:
            page: Playwright Page object
            script: PageSetupScript with clear_cookies_before and clear_local_storage_before flags
        """
        try:
            if script.clear_cookies_before:
                logger.info(f"Clearing cookies for script '{script.name}'")
                context = page.context
                await context.clear_cookies()
                logger.info("Cleared all cookies via context")

            if script.clear_local_storage_before:
                logger.info(f"Clearing localStorage and sessionStorage for script '{script.name}'")
                await page.evaluate('''() => {
                    localStorage.clear();
                    sessionStorage.clear();
                }''')
                logger.info("Cleared localStorage and sessionStorage")

        except Exception as e:
            logger.error(f"Error clearing browser state: {e}")

    async def test_page_with_matrix(
        self,
        page: Page,
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
            page: Playwright Page object
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
                await page.goto(initial_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(0.3)

            # Execute scripts to reach this state
            scripts_executed = []
            for script_def in sorted(test_state_matrix.scripts, key=lambda s: s.execution_order):
                script_id = script_def.script_id
                desired_state = combination.script_states.get(script_id)

                if desired_state == "after" and script_id in scripts_by_id:
                    script = scripts_by_id[script_id]
                    logger.info(f"Executing script '{script.name}' to reach desired state")

                    # Clear browser state if configured
                    if script.clear_cookies_before or script.clear_local_storage_before:
                        try:
                            current_url = page.url
                            await self._clear_browser_state(page, script)
                            await page.goto(current_url, wait_until='networkidle', timeout=30000)
                            await asyncio.sleep(0.5)
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
