"""
Login automation for authenticated testing
"""

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
            self.db.update_website_user(user)

            result['duration_ms'] = duration_ms
            return result

        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            error_msg = f"Login automation error: {str(e)}"
            logger.error(error_msg)

            # Update user's login status
            user.mark_login_attempt(False, error_msg)
            self.db.update_website_user(user)

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
            await browser_page.waitForSelector(
                config.username_field_selector,
                {'visible': True, 'timeout': timeout}
            )

            # Fill username
            logger.info(f"Entering username: {user.username}")
            await browser_page.type(config.username_field_selector, user.username, {'delay': 50})

            # Fill password
            logger.info("Entering password")
            await browser_page.type(config.password_field_selector, user.password, {'delay': 50})

            # Click submit button if specified
            if config.submit_button_selector:
                logger.info(f"Clicking submit button: {config.submit_button_selector}")
                await browser_page.click(config.submit_button_selector)
            else:
                # Try submitting the form by pressing Enter
                logger.info("Pressing Enter to submit")
                await browser_page.keyboard.press('Enter')

            # Wait for navigation after login
            try:
                await browser_page.waitForNavigation({'timeout': timeout, 'waitUntil': 'networkidle2'})
            except Exception as nav_error:
                logger.warning(f"Navigation wait timed out, checking success indicator: {nav_error}")

            # Check for success indicator
            if config.success_indicator_selector:
                logger.info(f"Checking for success indicator: {config.success_indicator_selector}")
                try:
                    await browser_page.waitForSelector(
                        config.success_indicator_selector,
                        {'visible': True, 'timeout': 5000}
                    )
                    logger.info("Login success indicator found")
                    return {'success': True, 'error': None}
                except Exception as e:
                    error_msg = f"Success indicator not found: {config.success_indicator_selector}"
                    logger.error(error_msg)
                    return {'success': False, 'error': error_msg}
            else:
                # No success indicator - assume success if we got here
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
