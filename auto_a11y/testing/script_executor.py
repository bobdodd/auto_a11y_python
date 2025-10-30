"""
Script executor for running page setup scripts before accessibility testing
"""

import asyncio
import logging
import os
import time
from typing import Optional, Dict, Any
from pathlib import Path

from auto_a11y.models import PageSetupScript, ActionType, ExecutionTrigger

logger = logging.getLogger(__name__)


class ScriptExecutionError(Exception):
    """Raised when script execution fails"""
    def __init__(self, message: str, step_number: Optional[int] = None):
        super().__init__(message)
        self.step_number = step_number


class ScriptExecutor:
    """Executes page setup scripts on browser pages"""

    def __init__(self, screenshot_dir: Optional[Path] = None):
        """
        Initialize script executor

        Args:
            screenshot_dir: Directory for saving debug screenshots
        """
        self.screenshot_dir = screenshot_dir or Path('screenshots/script_debug')
        self.screenshot_dir.mkdir(exist_ok=True, parents=True)

    async def execute_script(
        self,
        page,  # Pyppeteer page object
        script: PageSetupScript,
        environment_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a page setup script

        Args:
            page: Pyppeteer page object
            script: PageSetupScript to execute
            environment_vars: Environment variables for ${ENV:VAR_NAME} substitution

        Returns:
            Execution result dict with success status, duration, and error details

        Raises:
            ScriptExecutionError: If script execution fails
        """
        start_time = time.time()
        logger.info(f"Executing script '{script.name}' with {len(script.steps)} steps")

        env_vars = environment_vars or {}
        execution_log = []

        try:
            for step in script.steps:
                step_start = time.time()
                logger.info(f"  Step {step.step_number}: {step.action_type.value} - {step.description}")

                try:
                    await self._execute_step(page, step, env_vars)
                    step_duration = int((time.time() - step_start) * 1000)
                    execution_log.append({
                        'step_number': step.step_number,
                        'action': step.action_type.value,
                        'description': step.description,
                        'success': True,
                        'duration_ms': step_duration
                    })

                    # Wait after action if specified
                    if step.wait_after > 0:
                        await asyncio.sleep(step.wait_after / 1000)

                    # Take screenshot if requested
                    if step.screenshot_after:
                        await self._take_debug_screenshot(page, script, step)

                except Exception as e:
                    step_duration = int((time.time() - step_start) * 1000)
                    error_msg = f"Step {step.step_number} failed: {str(e)}"
                    logger.error(error_msg)

                    execution_log.append({
                        'step_number': step.step_number,
                        'action': step.action_type.value,
                        'description': step.description,
                        'success': False,
                        'duration_ms': step_duration,
                        'error': str(e)
                    })

                    # Take screenshot on error
                    try:
                        await self._take_debug_screenshot(page, script, step, error=True)
                    except:
                        pass

                    raise ScriptExecutionError(error_msg, step.step_number) from e

            # Validate script execution if validation rules are defined
            if script.validation:
                await self._validate_execution(page, script)

            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Script '{script.name}' completed successfully in {duration_ms}ms")

            return {
                'success': True,
                'duration_ms': duration_ms,
                'steps_executed': len(script.steps),
                'execution_log': execution_log
            }

        except ScriptExecutionError:
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'duration_ms': duration_ms,
                'steps_executed': len(execution_log),
                'execution_log': execution_log,
                'error': str(e) if 'e' in locals() else 'Unknown error'
            }

    async def _execute_step(
        self,
        page,
        step,
        env_vars: Dict[str, str]
    ):
        """
        Execute a single script step

        Args:
            page: Pyppeteer page object
            step: ScriptStep to execute
            env_vars: Environment variables for substitution
        """
        action = step.action_type

        # Substitute environment variables in value
        value = self._substitute_env_vars(step.value, env_vars) if step.value else None

        if action == ActionType.CLICK:
            # Click element
            element = await page.querySelector(step.selector)
            if not element:
                raise ScriptExecutionError(f"Element not found: {step.selector}")
            await element.click()

        elif action == ActionType.TYPE:
            # Type into element
            element = await page.querySelector(step.selector)
            if not element:
                raise ScriptExecutionError(f"Element not found: {step.selector}")
            await element.type(value)

        elif action == ActionType.WAIT:
            # Wait for duration
            duration = int(value) if value else step.timeout
            await asyncio.sleep(duration / 1000)

        elif action == ActionType.WAIT_FOR_SELECTOR:
            # Wait for element to appear
            try:
                await page.waitForSelector(
                    step.selector,
                    timeout=step.timeout
                )
            except Exception as e:
                raise ScriptExecutionError(
                    f"Timeout waiting for selector: {step.selector}"
                ) from e

        elif action == ActionType.WAIT_FOR_NAVIGATION:
            # Wait for page navigation
            try:
                await page.waitForNavigation(timeout=step.timeout)
            except Exception as e:
                raise ScriptExecutionError("Navigation timeout") from e

        elif action == ActionType.WAIT_FOR_NETWORK_IDLE:
            # Wait for network to be idle
            try:
                await page.waitForNetworkIdle(timeout=step.timeout)
            except Exception as e:
                raise ScriptExecutionError("Network idle timeout") from e

        elif action == ActionType.SCROLL:
            # Scroll to element
            element = await page.querySelector(step.selector)
            if not element:
                raise ScriptExecutionError(f"Element not found: {step.selector}")
            await page.evaluate('(element) => element.scrollIntoView()', element)

        elif action == ActionType.SELECT:
            # Select dropdown option
            await page.select(step.selector, value)

        elif action == ActionType.HOVER:
            # Hover over element
            element = await page.querySelector(step.selector)
            if not element:
                raise ScriptExecutionError(f"Element not found: {step.selector}")
            await element.hover()

        elif action == ActionType.SCREENSHOT:
            # Take screenshot
            await self._take_debug_screenshot(page, None, step)

        else:
            raise ScriptExecutionError(f"Unknown action type: {action}")

    def _substitute_env_vars(self, value: str, env_vars: Dict[str, str]) -> str:
        """
        Substitute ${ENV:VAR_NAME} patterns with environment variables

        Args:
            value: String value to substitute
            env_vars: Environment variables dict

        Returns:
            Substituted string
        """
        if not value or '${ENV:' not in value:
            return value

        import re
        pattern = r'\$\{ENV:([A-Z_][A-Z0-9_]*)\}'

        def replace_var(match):
            var_name = match.group(1)
            # Check provided env_vars first, then os.environ
            return env_vars.get(var_name, os.environ.get(var_name, ''))

        return re.sub(pattern, replace_var, value)

    async def _validate_execution(self, page, script: PageSetupScript):
        """
        Validate script execution using validation rules

        Args:
            page: Pyppeteer page object
            script: PageSetupScript with validation rules

        Raises:
            ScriptExecutionError: If validation fails
        """
        validation = script.validation
        if not validation:
            return

        # Check for failure selectors
        for failure_selector in validation.failure_selectors:
            element = await page.querySelector(failure_selector)
            if element:
                raise ScriptExecutionError(
                    f"Failure condition detected: found element {failure_selector}"
                )

        # Check for success selector
        if validation.success_selector:
            element = await page.querySelector(validation.success_selector)
            if not element:
                raise ScriptExecutionError(
                    f"Success condition not met: selector {validation.success_selector} not found"
                )

        # Check for success text
        if validation.success_text:
            content = await page.content()
            if validation.success_text not in content:
                raise ScriptExecutionError(
                    f"Success condition not met: text '{validation.success_text}' not found"
                )

        logger.info("Script validation passed")

    async def _take_debug_screenshot(
        self,
        page,
        script: Optional[PageSetupScript],
        step,
        error: bool = False
    ):
        """
        Take a debug screenshot

        Args:
            page: Pyppeteer page object
            script: PageSetupScript (optional)
            step: ScriptStep
            error: Whether this is an error screenshot
        """
        try:
            script_name = script.name.replace(' ', '_').lower() if script else 'manual'
            timestamp = int(time.time())
            status = 'error' if error else 'success'
            filename = f"{script_name}_step_{step.step_number}_{status}_{timestamp}.png"
            filepath = self.screenshot_dir / filename

            await page.screenshot({'path': str(filepath)})
            logger.info(f"Debug screenshot saved: {filepath}")
        except Exception as e:
            logger.warning(f"Failed to save debug screenshot: {e}")

    async def execute_with_session(
        self,
        page,
        script: PageSetupScript,
        page_id: str,
        session_manager: 'ScriptSessionManager',
        environment_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute script with session awareness

        Args:
            page: Pyppeteer page object
            script: PageSetupScript to execute
            page_id: Page ID being tested
            session_manager: ScriptSessionManager instance
            environment_vars: Environment variables for substitution

        Returns:
            Execution result dict with success, duration, and optional violation
        """
        # Check if should execute based on trigger and session state
        should_run, skip_reason = session_manager.should_execute_script(script, page_id)
        if not should_run:
            logger.info(f"Skipping script '{script.name}': {skip_reason}")
            return {
                'success': True,
                'skipped': True,
                'skip_reason': skip_reason,
                'duration_ms': 0
            }

        # For conditional trigger, check if element exists first
        if script.trigger == ExecutionTrigger.CONDITIONAL:
            condition_met = await self._check_condition(page, script.condition_selector)

            logger.debug(
                f"Condition check for script '{script.name}': "
                f"selector '{script.condition_selector}' "
                f"{'found' if condition_met else 'not found'}"
            )

            # Check for violation (condition reappeared after previous execution)
            violation = session_manager.check_condition_violation(
                script, page_id, condition_met
            )
            if violation:
                logger.warning(f"Condition violation detected: {violation.message}")
                return {
                    'success': True,
                    'skipped': True,
                    'skip_reason': 'Condition violation detected',
                    'violation': violation,
                    'duration_ms': 0
                }

            # If condition not met, skip execution (no violation)
            if not condition_met:
                logger.info(f"Skipping script '{script.name}': condition not met")
                return {
                    'success': True,
                    'skipped': True,
                    'skip_reason': 'Condition not met (selector not found)',
                    'duration_ms': 0
                }

        # Execute script
        start_time = time.time()
        result = await self.execute_script(page, script, environment_vars)
        duration_ms = int((time.time() - start_time) * 1000)

        # Mark as executed in session if successful
        if result['success']:
            session_manager.mark_executed(
                script.id,
                page_id,
                success=True,
                duration_ms=duration_ms
            )
            logger.info(
                f"Script '{script.name}' executed successfully and marked in session"
            )
        else:
            session_manager.mark_executed(
                script.id,
                page_id,
                success=False,
                duration_ms=duration_ms
            )
            logger.warning(f"Script '{script.name}' failed but marked in session")

        return result

    async def _check_condition(self, page, selector: str) -> bool:
        """
        Check if condition selector exists on page

        Args:
            page: Pyppeteer page object
            selector: CSS selector to check

        Returns:
            True if selector found, False otherwise
        """
        try:
            element = await page.querySelector(selector)
            return element is not None
        except Exception as e:
            logger.debug(f"Error checking condition selector '{selector}': {e}")
            return False
