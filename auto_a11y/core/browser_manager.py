"""
Browser management for Pyppeteer
"""

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
from contextlib import asynccontextmanager
from pyppeteer import launch, browser, page
from pyppeteer.errors import BrowserError, PageError, TimeoutError

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages Pyppeteer browser instances"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize browser manager
        
        Args:
            config: Browser configuration
        """
        self.config = config
        self.browser: Optional[browser.Browser] = None
        self.pages: List[page.Page] = []
        self._semaphore = asyncio.Semaphore(config.get('max_concurrent_pages', 5))
        
    async def start(self):
        """Start browser instance"""
        if self.browser and await self.is_running():
            pass  # Browser already running
            return
        
        # Check if headless mode is requested
        is_headless = self.config.get('headless', True)

        # Build args list
        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            # Removed --no-zygote and --single-process as they can cause connection issues
            '--disable-gpu',
            f'--window-size={self.config.get("viewport_width", 1920)},{self.config.get("viewport_height", 1080)}',
            # Suppress SPDY/HTTP2 warnings
            '--log-level=3',  # Only show fatal errors
            '--silent',
            '--disable-logging',
            '--disable-extensions',
            '--disable-background-networking',
            # Stealth mode arguments
            '--disable-blink-features=AutomationControlled',  # Hide automation
            '--exclude-switches=enable-automation',  # Hide automation flag
            '--disable-infobars',  # Hide "Chrome is being controlled" banner
        ]

        # Add headless=new mode if headless is requested (Chrome 109+)
        # This mode is much harder to detect than old headless
        # Only use new headless mode if stealth is enabled (it's slower)
        stealth_mode = self.config.get('stealth_mode', False)
        if is_headless and stealth_mode:
            browser_args.append('--headless=new')
        elif is_headless:
            # Use old headless for speed when stealth not needed
            browser_args.append('--headless')

        launch_options = {
            'headless': False,  # Don't use old headless, use --headless=new flag instead
            'handleSIGINT': False,
            'handleSIGTERM': False,
            'handleSIGHUP': False,
            'args': browser_args,
            'dumpio': self.config.get('dumpio', False),  # Disable to reduce console noise
            'timeout': self.config.get('timeout', 60000),  # Increased to 60 seconds
            'autoClose': False,  # Prevent automatic closing
            'ignoreDefaultArgs': ['--enable-automation']  # Don't use automation flag
        }
        
        # Add user data directory if specified
        if 'user_data_dir' in self.config:
            launch_options['userDataDir'] = self.config['user_data_dir']
        
        try:
            self.browser = await launch(**launch_options)
            pass  # Browser started
            # Keep a reference to prevent garbage collection
            self._browser_ref = self.browser
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            self.browser = None
            raise
    
    async def _apply_stealth(self, page):
        """
        Apply stealth techniques to make the browser harder to detect

        Args:
            page: Page instance to apply stealth to
        """
        # Only apply stealth if enabled in config
        if not self.config.get('stealth_mode', False):
            return

        # Override navigator properties to hide automation
        await page.evaluateOnNewDocument('''() => {
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
        }''')

    async def stop(self):
        """Stop browser instance"""
        if not self.browser:
            return
        
        # Close all pages
        for page in self.pages:
            try:
                await page.close()
            except:
                pass
        
        self.pages.clear()
        
        # Close browser
        try:
            await self.browser.close()
            pass  # Browser stopped
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
        finally:
            self.browser = None
    
    @asynccontextmanager
    async def get_page(self):
        """
        Get a new page with resource management
        
        Yields:
            Page instance
        """
        async with self._semaphore:
            if not self.browser:
                await self.start()
            
            page = None
            try:
                page = await self.browser.newPage()

                # Apply stealth techniques
                await self._apply_stealth(page)

                # Set viewport
                await page.setViewport({
                    'width': self.config.get('viewport_width', 1920),
                    'height': self.config.get('viewport_height', 1080)
                })

                # Set user agent if specified (check both uppercase and lowercase keys for compatibility)
                user_agent = (
                    self.config.get('user_agent') or
                    self.config.get('USER_AGENT') or
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                await page.setUserAgent(user_agent)

                # Set default timeout
                page.setDefaultNavigationTimeout(self.config.get('timeout', 60000))

                self.pages.append(page)
                yield page
                
            finally:
                if page:
                    try:
                        await page.close()
                        if page in self.pages:
                            self.pages.remove(page)
                    except Exception as e:
                        logger.warning(f"Error closing page: {e}")
    
    async def goto(
        self, 
        page: page.Page, 
        url: str,
        wait_until: str = 'networkidle2',
        timeout: Optional[int] = None
    ) -> Optional[page.Response]:
        """
        Navigate to URL with error handling
        
        Args:
            page: Page instance
            url: URL to navigate to
            wait_until: Wait condition
            timeout: Navigation timeout
            
        Returns:
            Response object or None if failed
        """
        options = {
            'waitUntil': wait_until,
            'timeout': timeout or self.config.get('timeout', 60000)
        }
        
        try:
            response = await page.goto(url, options)
            logger.debug(f"Navigated to: {url}")
            return response
        except TimeoutError:
            logger.warning(f"Navigation timeout for: {url}")
            return None
        except Exception as e:
            logger.error(f"Navigation error for {url}: {e}")
            return None
    
    async def take_screenshot(
        self,
        page: page.Page,
        path: Optional[Path] = None,
        full_page: bool = True
    ) -> bytes:
        """
        Take screenshot of page
        
        Args:
            page: Page instance
            path: Optional path to save screenshot
            full_page: Capture full page
            
        Returns:
            Screenshot bytes
        """
        options = {
            'fullPage': full_page,
            'type': 'jpeg',
            'quality': 80  # Reduced from 85 to help prevent MongoDB 16MB document limit issues
        }
        
        if path:
            options['path'] = str(path)
        
        try:
            screenshot = await page.screenshot(options)
            logger.debug(f"Screenshot taken{f' and saved to {path}' if path else ''}")
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            raise
    
    async def inject_scripts(
        self,
        page: page.Page,
        script_paths: List[Path]
    ):
        """
        Inject JavaScript files into page
        
        Args:
            page: Page instance
            script_paths: List of script file paths
        """
        for script_path in script_paths:
            if not script_path.exists():
                logger.warning(f"Script not found: {script_path}")
                continue
            
            try:
                await page.addScriptTag({'path': str(script_path)})
                logger.debug(f"Injected script: {script_path.name}")
            except Exception as e:
                logger.error(f"Failed to inject script {script_path.name}: {e}")
                raise
    
    async def execute_script(
        self,
        page: page.Page,
        script: str
    ) -> Any:
        """
        Execute JavaScript in page context
        
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
        page: page.Page,
        selector: str,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for element to appear
        
        Args:
            page: Page instance
            selector: CSS selector
            timeout: Wait timeout
            
        Returns:
            True if element found, False otherwise
        """
        try:
            await page.waitForSelector(
                selector,
                {'timeout': timeout or self.config.get('timeout', 60000)}
            )
            return True
        except TimeoutError:
            logger.debug(f"Selector not found: {selector}")
            return False
        except Exception as e:
            logger.error(f"Wait for selector error: {e}")
            return False
    
    async def get_page_content(self, page: page.Page) -> str:
        """
        Get page HTML content
        
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
    
    async def get_page_title(self, page: page.Page) -> str:
        """
        Get page title
        
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
    
    async def extract_links(self, page: page.Page) -> List[str]:
        """
        Extract all links from page
        
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
        """Check if browser is running"""
        try:
            if not self.browser:
                return False
            # Check if the browser process is still alive
            if hasattr(self.browser, 'process') and self.browser.process:
                if self.browser.process.returncode is not None:
                    logger.warning("Browser process has terminated")
                    self.browser = None  # Clear dead reference
                    return False
            # Try to verify connection is still alive
            try:
                # Get browser version to check connection with timeout
                version_task = self.browser.version()
                await asyncio.wait_for(version_task, timeout=2.0)
                return True
            except asyncio.TimeoutError:
                logger.warning("Browser connection check timed out")
                self.browser = None  # Clear dead reference
                return False
            except Exception as e:
                logger.warning(f"Browser connection lost: {e}")
                self.browser = None  # Clear dead reference
                return False
        except Exception as e:
            logger.error(f"Error checking browser status: {e}")
            self.browser = None  # Clear on any error
            return False
    
    async def ensure_running(self):
        """Ensure browser is running, restart if needed"""
        if not await self.is_running():
            logger.info("Browser not running, restarting...")
            await self.start()


class BrowserPool:
    """Pool of browser instances for parallel processing"""
    
    def __init__(self, config: Dict[str, Any], pool_size: int = 3):
        """
        Initialize browser pool
        
        Args:
            config: Browser configuration
            pool_size: Number of browser instances
        """
        self.config = config
        self.pool_size = pool_size
        self.browsers: List[BrowserManager] = []
        self._lock = asyncio.Lock()
        self._available = asyncio.Queue()
        
    async def start(self):
        """Start browser pool"""
        for _ in range(self.pool_size):
            browser = BrowserManager(self.config)
            await browser.start()
            self.browsers.append(browser)
            await self._available.put(browser)
        
        logger.info(f"Started browser pool with {self.pool_size} instances")
    
    async def stop(self):
        """Stop browser pool"""
        for browser in self.browsers:
            await browser.stop()
        
        self.browsers.clear()
        logger.info("Stopped browser pool")
    
    @asynccontextmanager
    async def acquire(self):
        """
        Acquire browser from pool
        
        Yields:
            BrowserManager instance
        """
        browser = await self._available.get()
        try:
            yield browser
        finally:
            await self._available.put(browser)