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

    async def _check_page_connection(self, page) -> bool:
        """
        Check if the browser page connection is still alive

        Args:
            page: Pyppeteer page object

        Returns:
            True if connection is alive, False otherwise
        """
        try:
            await asyncio.wait_for(page.evaluate('() => true'), timeout=2.0)
            return True
        except Exception as e:
            logger.warning(f"Page connection check failed: {e}")
            return False

    async def _safe_page_operation(self, page, operation_name: str, operation_coro):
        """
        Execute a page operation with connection check and error handling

        Args:
            page: Pyppeteer page object
            operation_name: Name of the operation for logging
            operation_coro: Coroutine to execute

        Returns:
            Result of the operation or None if failed

        Raises:
            Exception if page connection is lost
        """
        if not await self._check_page_connection(page):
            raise ConnectionError(f"Browser connection lost before {operation_name}")

        try:
            return await operation_coro
        except Exception as e:
            if 'Target closed' in str(e) or 'Session closed' in str(e) or 'Connection' in str(e):
                raise ConnectionError(f"Browser connection lost during {operation_name}: {e}")
            raise

    async def test_page_multi_state(
        self,
        page,
        page_id: str,
        scripts: List[PageSetupScript],
        test_function,
        session_id: str,
        environment_vars: Optional[Dict[str, str]] = None,
        original_url: Optional[str] = None
    ) -> List[TestResult]:
        """
        Test page across multiple states

        Workflow:
        1. Test initial state (if any script has test_before_execution=True)
        2. For each script:
           - Execute script
           - Validate state
           - Test after execution (if test_after_execution=True)
        3. Link all results together

        Args:
            page: Pyppeteer page object
            page_id: ID of page being tested
            scripts: List of scripts to execute
            test_function: Async function that runs accessibility tests
            session_id: Script execution session ID
            environment_vars: Environment variables for scripts
            original_url: Original URL to navigate back to (uses page.url if not provided)

        Returns:
            List of TestResult objects (one per state tested)
        """
        results = []
        state_sequence = 0
        
        # Store original URL for navigation
        target_url = original_url or page.url
        scripts_executed_so_far = []
        scripts_executed_names = []  # Track names for descriptions

        # Check if we need to test initial state (before any scripts)
        test_initial_state = any(script.test_before_execution for script in scripts)

        if test_initial_state:
            logger.info(f"Testing page {page_id} in initial state (sequence {state_sequence})")

            # Check page connection before running initial state tests
            if not await self._check_page_connection(page):
                logger.error(f"Browser connection lost before initial state tests")
                return results

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
            try:
                test_result = await test_function(page, page_id)
            except Exception as e:
                if 'Target closed' in str(e) or 'Session closed' in str(e):
                    logger.error(f"Browser connection lost during initial state tests: {e}")
                    return results
                raise

            # Add state metadata
            test_result.page_state = initial_state.to_dict()
            test_result.state_sequence = state_sequence
            test_result.session_id = session_id
            test_result.metadata['state_description'] = initial_state.description

            results.append(test_result)
            state_sequence += 1

        # Execute scripts and test after each one
        for script in scripts:
            logger.info(f"Processing script '{script.name}' (ID: {script.id})")

            # Clear cookies and/or localStorage if configured
            if script.clear_cookies_before or script.clear_local_storage_before:
                try:
                    await self._clear_browser_state(page, script)

                    # Navigate to original URL to apply the cleared state
                    logger.info(f"Navigating to {target_url} after clearing browser state")
                    await page.goto(target_url, {'waitUntil': 'networkidle2', 'timeout': 30000})
                    logger.info(f"Page navigation completed successfully")

                    # Brief wait for page to stabilize
                    await asyncio.sleep(0.5)

                    # Ensure body is present and interactive
                    await page.waitForSelector('body', {'timeout': 5000})

                    # If script has a selector (likely the cookie banner button), wait for it
                    if script.steps and script.steps[0].selector:
                        try:
                            selector = script.steps[0].selector

                            # Check if XPath selector (starts with / or //)
                            if selector.startswith('/'):
                                await page.waitForXPath(selector, {'timeout': 5000})
                            else:
                                await page.waitForSelector(selector, {'timeout': 5000})
                        except Exception:
                            pass  # Continue anyway
                except Exception as e:
                    logger.error(f"Error during browser state clearing/navigation: {e}")
                    # Skip this script and continue with next one
                    logger.warning(f"Skipping script '{script.name}' due to clearing/navigation failure")
                    continue

            # Check page connection before executing script
            if not await self._check_page_connection(page):
                logger.error(f"Browser connection lost before executing script '{script.name}'")
                break

            # Execute script
            try:
                script_result = await self.script_executor.execute_script(
                    page=page,
                    script=script,
                    environment_vars=environment_vars
                )
            except Exception as e:
                if 'Target closed' in str(e) or 'Session closed' in str(e):
                    logger.error(f"Browser connection lost during script execution: {e}")
                    break
                raise

            scripts_executed_so_far.append(script.id)
            scripts_executed_names.append(script.name)

            # Check if script execution succeeded
            if not script_result['success']:
                logger.warning(f"Script '{script.name}' failed, skipping state validation and testing")
                continue

            # Build cumulative state description
            if len(scripts_executed_names) == 1:
                state_description = f"After: {scripts_executed_names[0]}"
            else:
                state_description = "After: " + " + ".join(scripts_executed_names)

            # Create expected state after script execution
            expected_state = self.state_validator.create_expected_state(
                state_id=f"{page_id}_state_{state_sequence}",
                description=state_description,
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
                    page=page,
                    expected_state=expected_state
                )

                if state_violations:
                    logger.warning(f"State validation found {len(state_violations)} violations")

            # Test after script execution if configured
            if script.test_after_execution:
                logger.info(f"Testing page {page_id} after script '{script.name}' (sequence {state_sequence})")

                # Check page connection before running tests
                if not await self._check_page_connection(page):
                    logger.error(f"Browser connection lost before post-script tests")
                    break

                # Run accessibility tests
                try:
                    test_result = await test_function(page, page_id)
                except Exception as e:
                    if 'Target closed' in str(e) or 'Session closed' in str(e):
                        logger.error(f"Browser connection lost during post-script tests: {e}")
                        break
                    raise

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

        # Link all results together
        result_ids = [result.id for result in results if result.id]
        for result in results:
            result.related_result_ids = [rid for rid in result_ids if rid != result.id]


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
        environment_vars: Optional[Dict[str, str]] = None,
        original_url: Optional[str] = None
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
            original_url: Original URL to navigate back to (uses page.url if not provided)

        Returns:
            List of TestResult objects (one per state combination tested)
        """
        logger.info(f"Starting matrix-based multi-state testing for page {page_id}")
        results = []
        state_sequence = 0

        # Get all enabled state combinations from the matrix
        combinations = test_state_matrix.get_enabled_combinations()
        logger.info(f"Testing {len(combinations)} state combinations (instead of {2**len(test_state_matrix.scripts)} possible permutations)")

        # Use original URL for navigation
        initial_url = original_url or page.url

        # Test each combination
        for combo_idx, combination in enumerate(combinations):
            logger.info(f"Testing combination {combo_idx + 1}/{len(combinations)}: {combination.script_states}")

            # Reload page to start fresh
            if combo_idx > 0:
                logger.info(f"Reloading page to initial state")
                await page.goto(initial_url, {'waitUntil': 'networkidle2', 'timeout': 30000})
                await asyncio.sleep(0.3)  # Let page stabilize

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
                            await self._clear_browser_state(page, script)
                            await page.goto(initial_url, {'waitUntil': 'networkidle2', 'timeout': 30000})
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

            logger.info(f"Matrix test result: state_sequence={state_sequence}, session_id={session_id}, description={state_description}")

            results.append(test_result)
            state_sequence += 1

        # Link all results together
        result_ids = [result.id for result in results if result.id]
        for result in results:
            result.related_result_ids = [rid for rid in result_ids if rid != result.id]

        logger.info(f"Matrix-based testing complete: {len(results)} test results generated")

        return results
