"""
Login automation for authenticated testing
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LoginAutomation:
    """Handles automated login for authenticated testing"""

    def __init__(self, database):
        """
        Initialize login automation

        Args:
            database: Database connection
        """
        self.db = database

    async def _find_element(self, page, selector: str):
        """
        Find element by CSS selector or XPath

        Args:
            page: Pyppeteer page object
            selector: CSS selector or XPath (XPath must start with / or //)

        Returns:
            Element handle or None
        """
        if selector.startswith('/'):
            elements = await page.xpath(selector)
            return elements[0] if elements else None
        else:
            return await page.querySelector(selector)

    async def _wait_for_selector(self, page, selector: str, options: dict = None):
        """
        Wait for element by CSS selector or XPath

        Args:
            page: Pyppeteer page object
            selector: CSS selector or XPath (XPath must start with / or //)
            options: Options dict with timeout, visible, etc.
        """
        opts = options or {}
        if selector.startswith('/'):
            await page.waitForXPath(selector, opts)
        else:
            await page.waitForSelector(selector, opts)

    async def _type_into_element(self, page, selector: str, text: str, options: dict = None):
        """
        Type text into element by CSS selector or XPath

        Args:
            page: Pyppeteer page object
            selector: CSS selector or XPath
            text: Text to type
            options: Options dict with delay, etc.
        """
        opts = options or {}
        if selector.startswith('/'):
            elements = await page.xpath(selector)
            if elements:
                await elements[0].type(text, opts)
            else:
                raise Exception(f"Element not found: {selector}")
        else:
            await page.type(selector, text, opts)

    async def _click_element(self, page, selector: str):
        """
        Click element by CSS selector or XPath

        Args:
            page: Pyppeteer page object
            selector: CSS selector or XPath
        """
        if selector.startswith('/'):
            elements = await page.xpath(selector)
            if elements:
                await elements[0].click()
            else:
                raise Exception(f"Element not found: {selector}")
        else:
            await page.click(selector)

    async def perform_login(
        self,
        browser_page,
        user: 'WebsiteUser',
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """
        Perform automated login for a user

        Args:
            browser_page: Pyppeteer page object
            user: WebsiteUser object with credentials and login config
            timeout: Maximum time to wait for login (milliseconds)

        Returns:
            Dictionary with success status, error message, and timing
        """
        start_time = datetime.now()

        try:
            login_config = user.login_config

            if login_config.authentication_method.value == 'form_login':
                result = await self._perform_form_login(browser_page, user, timeout)
            elif login_config.authentication_method.value == 'basic_auth':
                result = await self._perform_basic_auth(browser_page, user)
            else:
                return {
                    'success': False,
                    'error': f'Authentication method {login_config.authentication_method.value} not yet implemented',
                    'duration_ms': 0
                }

            # Update user's login status in database
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            user.mark_login_attempt(result['success'], result.get('error'))
            self.db.update_project_user(user)

            result['duration_ms'] = duration_ms
            return result

        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            error_msg = f"Login automation error: {str(e)}"
            logger.error(error_msg)

            # Update user's login status
            user.mark_login_attempt(False, error_msg)
            self.db.update_project_user(user)

            return {
                'success': False,
                'error': error_msg,
                'duration_ms': duration_ms
            }

    async def _perform_form_login(
        self,
        browser_page,
        user: 'WebsiteUser',
        timeout: int
    ) -> Dict[str, Any]:
        """
        Perform form-based login

        Args:
            browser_page: Pyppeteer page object
            user: WebsiteUser with login configuration
            timeout: Timeout in milliseconds

        Returns:
            Result dictionary
        """
        config = user.login_config

        # Validate configuration
        if not config.login_url:
            return {'success': False, 'error': 'Login URL not configured'}
        if not config.username_field_selector:
            return {'success': False, 'error': 'Username field selector not configured'}
        if not config.password_field_selector:
            return {'success': False, 'error': 'Password field selector not configured'}

        try:
            logger.info(f"Navigating to login page: {config.login_url}")

            # Navigate to login page
            await browser_page.goto(config.login_url, {
                'waitUntil': 'networkidle2',
                'timeout': timeout
            })

            # Wait for login form to be visible
            logger.info(f"Waiting for username field: {config.username_field_selector}")
            await self._wait_for_selector(
                browser_page,
                config.username_field_selector,
                {'visible': True, 'timeout': timeout}
            )

            # Fill username
            logger.info(f"Entering username: {user.username}")
            await self._type_into_element(browser_page, config.username_field_selector, user.username, {'delay': 50})

            # Fill password
            logger.info("Entering password")
            await self._type_into_element(browser_page, config.password_field_selector, user.password, {'delay': 50})

            # Click submit button if specified
            if config.submit_button_selector:
                logger.info(f"Clicking submit button: {config.submit_button_selector}")
                await self._click_element(browser_page, config.submit_button_selector)
            else:
                # Try submitting the form by pressing Enter
                logger.info("Pressing Enter to submit")
                await browser_page.keyboard.press('Enter')

            # Wait briefly for any immediate response
            await asyncio.sleep(0.5)

            # Check for success indicator if configured (primary check for AJAX logins)
            if config.success_indicator_selector:
                logger.info(f"Checking for success indicator: {config.success_indicator_selector}")
                try:
                    await self._wait_for_selector(
                        browser_page,
                        config.success_indicator_selector,
                        {'visible': True, 'timeout': 10000}
                    )
                    logger.info("Login success indicator found")
                    return {'success': True, 'error': None}
                except Exception as e:
                    error_msg = f"Success indicator not found: {config.success_indicator_selector}"
                    logger.error(error_msg)
                    return {'success': False, 'error': error_msg}
            else:
                # No success indicator - wait for navigation with shorter timeout
                try:
                    await browser_page.waitForNavigation({'timeout': 10000, 'waitUntil': 'networkidle2'})
                    logger.info("Navigation completed, assuming login successful")
                    return {'success': True, 'error': None}
                except Exception as nav_error:
                    logger.warning(f"Navigation wait timed out: {nav_error}")
                    # Assume success since no success indicator was configured
                    logger.info("No success indicator configured, assuming login successful")
                    return {'success': True, 'error': None}

        except Exception as e:
            error_msg = f"Form login failed: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

    async def _perform_basic_auth(
        self,
        browser_page,
        user: 'WebsiteUser'
    ) -> Dict[str, Any]:
        """
        Perform HTTP Basic Authentication

        Args:
            browser_page: Pyppeteer page object
            user: WebsiteUser with credentials

        Returns:
            Result dictionary
        """
        try:
            # Set authentication credentials
            await browser_page.authenticate({
                'username': user.username,
                'password': user.password
            })

            logger.info(f"Basic auth credentials set for user: {user.username}")
            return {'success': True, 'error': None}

        except Exception as e:
            error_msg = f"Basic auth failed: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

    async def perform_logout(
        self,
        browser_page,
        user: 'WebsiteUser',
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """
        Perform automated logout for a user

        Args:
            browser_page: Pyppeteer page object
            user: WebsiteUser object with logout configuration
            timeout: Maximum time to wait for logout (milliseconds)

        Returns:
            Dictionary with success status, error message, and timing
        """
        start_time = datetime.now()

        try:
            login_config = user.login_config

            # Check if logout is configured
            if not login_config.logout_url and not login_config.logout_button_selector:
                logger.info(f"No logout configuration for user {user.username}, clearing cookies instead")
                # Clear all cookies to ensure clean logout
                await browser_page._client.send('Network.clearBrowserCookies')
                return {
                    'success': True,
                    'error': None,
                    'duration_ms': int((datetime.now() - start_time).total_seconds() * 1000),
                    'method': 'cookie_clear'
                }

            # Perform configured logout
            if login_config.logout_url:
                # Navigate to logout URL
                logger.info(f"Navigating to logout URL: {login_config.logout_url}")
                await browser_page.goto(login_config.logout_url, {
                    'waitUntil': 'networkidle2',
                    'timeout': timeout
                })

            # Click logout button if specified
            if login_config.logout_button_selector:
                logger.info(f"Clicking logout button: {login_config.logout_button_selector}")
                try:
                    await self._wait_for_selector(
                        browser_page,
                        login_config.logout_button_selector,
                        {'visible': True, 'timeout': 5000}
                    )
                    await self._click_element(browser_page, login_config.logout_button_selector)

                    # Wait for navigation if logout triggers redirect
                    try:
                        await browser_page.waitForNavigation({
                            'timeout': 5000,
                            'waitUntil': 'networkidle2'
                        })
                    except:
                        pass  # Navigation may not happen for AJAX logouts

                except Exception as e:
                    logger.warning(f"Could not click logout button: {e}")

            # Check for logout success indicator
            if login_config.logout_success_indicator_selector:
                logger.info(f"Checking for logout success indicator: {login_config.logout_success_indicator_selector}")
                try:
                    await self._wait_for_selector(
                        browser_page,
                        login_config.logout_success_indicator_selector,
                        {'visible': True, 'timeout': 5000}
                    )
                    logger.info("Logout success indicator found")
                except Exception as e:
                    logger.warning(f"Logout success indicator not found: {e}")
                    # Still return success - we tried our best

            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.info(f"Logout completed for user {user.username} in {duration_ms}ms")

            return {
                'success': True,
                'error': None,
                'duration_ms': duration_ms,
                'method': 'configured_logout'
            }

        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            error_msg = f"Logout error: {str(e)}"
            logger.error(error_msg)

            # Try to clear cookies as fallback
            try:
                await browser_page._client.send('Network.clearBrowserCookies')
                logger.info("Cleared cookies as logout fallback")
            except:
                pass

            return {
                'success': False,
                'error': error_msg,
                'duration_ms': duration_ms
            }

    def is_session_valid(self, user: 'WebsiteUser') -> bool:
        """
        Check if a user's session is still valid based on timeout

        Args:
            user: WebsiteUser to check

        Returns:
            True if session is still valid
        """
        if not user.last_used:
            return False

        # Check if session has timed out
        elapsed_minutes = (datetime.now() - user.last_used).total_seconds() / 60
        return elapsed_minutes < user.login_config.session_timeout_minutes
