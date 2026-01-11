"""
Browser management using Playwright

This module provides a Playwright-based browser manager that implements the same
interface as the Pyppeteer-based BrowserManager, but with improved stability
for multi-state testing and authenticated user scenarios.

Key improvements over Pyppeteer:
- Browser context isolation for clean test states
- Built-in auto-waiting reduces timing issues
- Storage state API for authentication persistence
- More stable connection handling
- Active maintenance by Microsoft
"""

import asyncio
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import logging
from contextlib import asynccontextmanager

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Response,
    Playwright,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError
)

logger = logging.getLogger(__name__)


class BrowserManager:
    """
    Manages Playwright browser instances with context isolation.

    This class provides the same interface as the Pyppeteer BrowserManager
    but uses Playwright for improved stability, especially for:
    - Multi-state testing
    - Authenticated user testing
    - Multiple viewport changes
    - Script injection scenarios
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize browser manager

        Args:
            config: Browser configuration dictionary with keys:
                - headless: Run in headless mode (default: True)
                - timeout: Default timeout in ms (default: 60000)
                - viewport_width: Viewport width (default: 1920)
                - viewport_height: Viewport height (default: 1080)
                - user_agent: User agent string
                - stealth_mode: Apply anti-detection measures (default: False)
                - max_concurrent_pages: Max concurrent pages (default: 5)
        """
        self.config = config
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._default_context: Optional[BrowserContext] = None
        self._contexts: List[BrowserContext] = []
        self._pages: List[Page] = []
        self._semaphore = asyncio.Semaphore(config.get('max_concurrent_pages', 5))

    @property
    def pages(self) -> List[Page]:
        """Get list of open pages (for compatibility)"""
        return self._pages

    @property
    def browser(self) -> Optional[Browser]:
        """Get browser instance (for compatibility)"""
        return self._browser

    async def start(self) -> None:
        """Start browser instance"""
        if self._browser and self._browser.is_connected():
            return  # Browser already running

        # Get headless setting (check both uppercase and lowercase keys)
        is_headless = self.config.get('headless', self.config.get('BROWSER_HEADLESS', True))

        # Build args list (similar to Pyppeteer for consistency)
        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--disable-gpu',
            f'--window-size={self.config.get("viewport_width", 1920)},{self.config.get("viewport_height", 1080)}',
            '--disable-extensions',
            '--disable-background-networking',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-component-update',
        ]

        launch_options = {
            'headless': is_headless,
            'args': browser_args,
            'timeout': self.config.get('timeout', 60000),
        }

        # Add executable path if specified
        if self.config.get('executable_path'):
            launch_options['executable_path'] = self.config['executable_path']

        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(**launch_options)
            logger.info("Playwright browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            await self._cleanup_playwright()
            raise

    async def _cleanup_playwright(self) -> None:
        """Clean up Playwright resources"""
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    async def stop(self) -> None:
        """Stop browser instance completely"""
        # Close all pages
        for page in self._pages[:]:  # Copy list to avoid modification during iteration
            try:
                if not page.is_closed():
                    await page.close()
            except Exception:
                pass
        self._pages.clear()

        # Close all contexts
        for context in self._contexts[:]:
            try:
                await context.close()
            except Exception:
                pass
        self._contexts.clear()

        # Close default context
        if self._default_context:
            try:
                await self._default_context.close()
            except Exception:
                pass
            self._default_context = None

        # Close browser
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None

        # Stop Playwright
        await self._cleanup_playwright()
        logger.info("Playwright browser stopped")

    async def create_context(
        self,
        storage_state: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None
    ) -> BrowserContext:
        """
        Create an isolated browser context.

        Browser contexts provide complete isolation:
        - Separate cookies, localStorage, sessionStorage
        - Separate cache
        - Can have different viewports and user agents

        This is the KEY FEATURE that makes Playwright more stable
        for multi-state and multi-user testing.

        Args:
            storage_state: Path to saved storage state (for auth persistence)
            viewport: Custom viewport {width, height}
            user_agent: Custom user agent string

        Returns:
            BrowserContext instance
        """
        if not self._browser:
            await self.start()

        context_options = {
            'viewport': viewport or {
                'width': self.config.get('viewport_width', self.config.get('BROWSER_VIEWPORT_WIDTH', 1920)),
                'height': self.config.get('viewport_height', self.config.get('BROWSER_VIEWPORT_HEIGHT', 1080))
            },
            'user_agent': user_agent or self.config.get('user_agent') or self.config.get('USER_AGENT') or
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        # Load saved authentication state if provided
        if storage_state and Path(storage_state).exists():
            context_options['storage_state'] = storage_state
            logger.debug(f"Loading storage state from: {storage_state}")

        context = await self._browser.new_context(**context_options)

        # Set default timeouts
        default_timeout = self.config.get('timeout', 60000)
        context.set_default_timeout(default_timeout)
        context.set_default_navigation_timeout(default_timeout)

        # Apply stealth if enabled
        if self.config.get('stealth_mode', False):
            await self._apply_stealth(context)

        self._contexts.append(context)
        logger.debug(f"Created browser context (total: {len(self._contexts)})")
        return context

    async def close_context(self, context: BrowserContext) -> None:
        """
        Close a browser context and all its pages.

        Args:
            context: BrowserContext to close
        """
        try:
            # Remove pages from tracking
            for page in context.pages:
                if page in self._pages:
                    self._pages.remove(page)

            await context.close()

            if context in self._contexts:
                self._contexts.remove(context)

            logger.debug(f"Closed browser context (remaining: {len(self._contexts)})")
        except Exception as e:
            logger.warning(f"Error closing context: {e}")

    async def save_storage_state(self, context: BrowserContext, path: str) -> None:
        """
        Save authentication/storage state to file for reuse.

        This allows you to:
        1. Login once
        2. Save the state
        3. Create new contexts with that state (instant auth)

        Args:
            context: BrowserContext with authenticated state
            path: File path to save state to
        """
        await context.storage_state(path=path)
        logger.info(f"Saved storage state to: {path}")

    async def _apply_stealth(self, context: BrowserContext) -> None:
        """
        Apply stealth techniques to make the browser harder to detect.

        Args:
            context: BrowserContext to apply stealth to
        """
        stealth_script = '''() => {
            // Overwrite the `navigator.webdriver` property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });

            // Overwrite the `plugins` property to add fake plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Overwrite the `languages` property
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            // Pass the Chrome Test
            window.chrome = {
                runtime: {},
            };

            // Pass the Permissions Test
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        }'''

        await context.add_init_script(stealth_script)

    @asynccontextmanager
    async def get_page(self, context: Optional[BrowserContext] = None):
        """
        Get a new page with resource management.

        Args:
            context: Optional BrowserContext to use (creates default if not provided)

        Yields:
            Page instance
        """
        async with self._semaphore:
            if not self._browser:
                await self.start()

            # Use provided context or create/use default
            if context is None:
                if self._default_context is None:
                    self._default_context = await self.create_context()
                context = self._default_context

            page = None
            try:
                page = await context.new_page()
                self._pages.append(page)
                yield page

            finally:
                if page and not page.is_closed():
                    try:
                        await page.close()
                        if page in self._pages:
                            self._pages.remove(page)
                    except Exception as e:
                        logger.warning(f"Error closing page: {e}")

    async def create_page(self, context: Optional[BrowserContext] = None) -> Page:
        """
        Create a new page without context manager (caller must close it).

        Args:
            context: Optional BrowserContext to use

        Returns:
            Page instance
        """
        if not self._browser:
            await self.start()

        # Use provided context or create/use default
        if context is None:
            if self._default_context is None:
                self._default_context = await self.create_context()
            context = self._default_context

        page = await context.new_page()
        self._pages.append(page)
        return page

    async def close_page(self, page: Page) -> None:
        """
        Close a page created with create_page().

        Args:
            page: Page instance to close
        """
        try:
            if not page.is_closed():
                await page.close()
            if page in self._pages:
                self._pages.remove(page)
        except Exception as e:
            logger.warning(f"Error closing page: {e}")

    async def goto(
        self,
        page: Page,
        url: str,
        wait_until: str = 'networkidle',
        timeout: Optional[int] = None,
        capture_css: bool = False
    ) -> Optional[Response]:
        """
        Navigate to URL with error handling.

        Args:
            page: Page instance
            url: URL to navigate to
            wait_until: Wait condition ('load', 'domcontentloaded', 'networkidle')
            timeout: Navigation timeout in ms
            capture_css: Whether to capture CSS focus rules during navigation

        Returns:
            Response object or None if failed
        """
        # Map Pyppeteer wait conditions to Playwright
        wait_map = {
            'networkidle0': 'networkidle',
            'networkidle2': 'networkidle',
            'load': 'load',
            'domcontentloaded': 'domcontentloaded',
        }
        wait_until = wait_map.get(wait_until, wait_until)

        css_capture = None
        if capture_css:
            try:
                from auto_a11y.testing.css_focus_capture import (
                    CSSFocusCapture, set_css_capture_for_page, clear_css_capture_for_page
                )
                clear_css_capture_for_page(page)
                css_capture = CSSFocusCapture()
                await css_capture.start_capture(page)
                set_css_capture_for_page(page, css_capture)
            except Exception as e:
                logger.debug(f"CSS capture setup failed: {e}")
                css_capture = None

        try:
            response = await page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout or self.config.get('timeout', 60000)
            )
            logger.debug(f"Navigated to: {url}")

            if css_capture:
                try:
                    await css_capture.stop_capture()
                    await css_capture.capture_inline_styles(page)
                    logger.debug(f"CSS capture complete: {len(css_capture.cache.focus_rules)} focus rules captured")
                except Exception as e:
                    logger.debug(f"CSS capture finalization failed: {e}")

            return response

        except PlaywrightTimeoutError:
            logger.warning(f"Navigation timeout for: {url}")
            if css_capture:
                try:
                    await css_capture.stop_capture()
                except Exception:
                    pass
            return None

        except PlaywrightError as e:
            logger.error(f"Navigation error for {url}: {e}")
            if css_capture:
                try:
                    await css_capture.stop_capture()
                except Exception:
                    pass
            return None

    async def take_screenshot(
        self,
        page: Page,
        path: Optional[Path] = None,
        full_page: bool = True
    ) -> bytes:
        """
        Take screenshot of page.

        Args:
            page: Page instance
            path: Optional path to save screenshot
            full_page: Capture full page

        Returns:
            Screenshot bytes
        """
        screenshot_options = {
            'full_page': full_page,
            'type': 'jpeg',
            'quality': 80
        }

        if path:
            screenshot_options['path'] = str(path)

        try:
            screenshot = await page.screenshot(**screenshot_options)
            logger.debug(f"Screenshot taken{f' and saved to {path}' if path else ''}")
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            raise

    async def inject_scripts(
        self,
        page: Page,
        script_paths: List[Path]
    ) -> None:
        """
        Inject JavaScript files into page.

        Args:
            page: Page instance
            script_paths: List of script file paths
        """
        for script_path in script_paths:
            if not script_path.exists():
                logger.warning(f"Script not found: {script_path}")
                continue

            try:
                await page.add_script_tag(path=str(script_path))
                logger.debug(f"Injected script: {script_path.name}")
            except Exception as e:
                logger.error(f"Failed to inject script {script_path.name}: {e}")
                raise

    async def execute_script(
        self,
        page: Page,
        script: str
    ) -> Any:
        """
        Execute JavaScript in page context.

        Args:
            page: Page instance
            script: JavaScript code to execute

        Returns:
            Script execution result
        """
        try:
            result = await page.evaluate(script)
            return result
        except Exception as e:
            logger.error(f"Script execution error: {e}")
            raise

    async def wait_for_selector(
        self,
        page: Page,
        selector: str,
        timeout: Optional[int] = None,
        state: str = 'visible'
    ) -> bool:
        """
        Wait for element to appear.

        Args:
            page: Page instance
            selector: CSS selector or XPath (auto-detected)
            timeout: Wait timeout in ms
            state: Element state to wait for ('visible', 'attached', 'hidden', 'detached')

        Returns:
            True if element found, False otherwise
        """
        try:
            await page.wait_for_selector(
                selector,
                timeout=timeout or self.config.get('timeout', 60000),
                state=state
            )
            return True
        except PlaywrightTimeoutError:
            logger.debug(f"Selector not found: {selector}")
            return False
        except Exception as e:
            logger.error(f"Wait for selector error: {e}")
            return False

    async def get_page_content(self, page: Page) -> str:
        """
        Get page HTML content.

        Args:
            page: Page instance

        Returns:
            HTML content
        """
        try:
            content = await page.content()
            return content
        except Exception as e:
            logger.error(f"Error getting page content: {e}")
            raise

    async def get_page_title(self, page: Page) -> str:
        """
        Get page title.

        Args:
            page: Page instance

        Returns:
            Page title
        """
        try:
            title = await page.title()
            return title
        except Exception as e:
            logger.error(f"Error getting page title: {e}")
            return ""

    async def extract_links(self, page: Page) -> List[str]:
        """
        Extract all links from page.

        Args:
            page: Page instance

        Returns:
            List of URLs
        """
        try:
            links = await page.evaluate('''
                () => {
                    const links = document.querySelectorAll('a[href]');
                    return Array.from(links).map(link => link.href);
                }
            ''')
            return links
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []

    async def is_running(self) -> bool:
        """Check if browser is running and connected."""
        try:
            if not self._browser:
                return False
            return self._browser.is_connected()
        except Exception as e:
            logger.error(f"Error checking browser status: {e}")
            return False

    async def ensure_running(self) -> None:
        """Ensure browser is running, restart if needed."""
        if not await self.is_running():
            logger.info("Browser not running, restarting...")
            await self.stop()  # Clean up any dead resources
            await self.start()

    # Compatibility properties for code that accesses browser directly
    @property
    def browser(self) -> Optional[Browser]:
        """Get the underlying browser instance (for compatibility)."""
        return self._browser

    @property
    def pages(self) -> List[Page]:
        """Get list of open pages (for compatibility)."""
        return self._pages


class BrowserPool:
    """Pool of browser instances for parallel processing."""

    def __init__(self, config: Dict[str, Any], pool_size: int = 3):
        """
        Initialize browser pool.

        Args:
            config: Browser configuration
            pool_size: Number of browser instances
        """
        self.config = config
        self.pool_size = pool_size
        self.browsers: List[BrowserManager] = []
        self._lock = asyncio.Lock()
        self._available: asyncio.Queue = asyncio.Queue()

    async def start(self) -> None:
        """Start browser pool."""
        for _ in range(self.pool_size):
            browser = BrowserManager(self.config)
            await browser.start()
            self.browsers.append(browser)
            await self._available.put(browser)

        logger.info(f"Started browser pool with {self.pool_size} instances")

    async def stop(self) -> None:
        """Stop browser pool."""
        for browser in self.browsers:
            await browser.stop()

        self.browsers.clear()
        logger.info("Stopped browser pool")

    @asynccontextmanager
    async def acquire(self):
        """
        Acquire browser from pool.

        Yields:
            BrowserManager instance
        """
        browser = await self._available.get()
        try:
            yield browser
        finally:
            await self._available.put(browser)
