"""
Web scraping engine using Pyppeteer
"""

import asyncio
import logging
from typing import List, Set, Dict, Optional, Any
from urllib.parse import urlparse, urljoin, urlunparse
from urllib.robotparser import RobotFileParser
from pathlib import Path
from datetime import datetime
import re
from io import BytesIO

from pyppeteer import launch
from pyppeteer.errors import TimeoutError, PageError, NetworkError
from bs4 import BeautifulSoup

from auto_a11y.models.page import Page, PageStatus
from auto_a11y.models.website import Website
from auto_a11y.models.discovery_run import DiscoveryRun, DiscoveryStatus
from auto_a11y.core.database import Database
from auto_a11y.core.browser_manager import BrowserManager
# Note: ScrapingJob class has been moved to scraping_job.py for database-backed implementation

logger = logging.getLogger(__name__)


class ScrapingEngine:
    """Web scraping engine for page discovery"""
    
    def __init__(self, database: Database, browser_config: Dict[str, Any]):
        """
        Initialize scraping engine
        
        Args:
            database: Database connection
            browser_config: Browser configuration
        """
        self.db = database
        self.browser_manager = BrowserManager(browser_config)
        self.discovered_urls: Set[str] = set()
        self.queued_urls: Set[str] = set()
        self.robots_cache: Dict[str, RobotFileParser] = {}
        
    async def discover_website(
        self,
        website: Website,
        progress_callback: Optional[callable] = None,
        job: Optional['ScrapingJob'] = None
    ) -> List[Page]:
        """
        Discover all pages in a website
        
        Args:
            website: Website to discover
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of discovered pages
        """
        logger.info(f"Starting discovery for website: {website.url}")
        
        # Create a new discovery run
        discovery_run = DiscoveryRun(
            website_id=website.id,
            started_at=datetime.now(),
            status=DiscoveryStatus.RUNNING,
            max_pages=website.scraping_config.max_pages,
            max_depth=website.scraping_config.max_depth,
            follow_external=website.scraping_config.follow_external,
            respect_robots=website.scraping_config.respect_robots,
            triggered_by=job.user_id if job and hasattr(job, 'user_id') else 'manual',
            job_id=job.job_id if job and hasattr(job, 'job_id') else None
        )
        discovery_run_id = self.db.create_discovery_run(discovery_run)
        logger.info(f"Created discovery run {discovery_run_id} for website {website.id}")
        
        # Get the previous latest run for comparison
        previous_run = None
        previous_runs = self.db.get_discovery_runs(website.id)
        if len(previous_runs) > 1:  # More than just the current run
            previous_run = previous_runs[1]  # Second item is the previous latest
        
        # Reset discovery state
        self.discovered_urls.clear()
        self.queued_urls.clear()
        
        # Parse base URL
        base_url = self._normalize_url(website.url)
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        base_path = parsed_base.path.rstrip('/')  # Base path without trailing slash
        
        # Initialize queue with starting URL
        self.queued_urls.add(base_url)
        
        # Track discovered pages
        discovered_pages = []
        
        # Start browser once for entire discovery session
        try:
            await self.browser_manager.start()
            logger.info("Browser started for discovery session")
        except Exception as e:
            error_msg = f"Failed to start browser: {e}. Make sure Chromium is installed (run: python run.py --download-browser)"
            logger.error(error_msg)
            if progress_callback:
                await progress_callback({
                    'status': 'failed',
                    'error': error_msg
                })
            raise RuntimeError(error_msg)
        
        try:
            depth = 0
            max_pages_reached = False
            start_time = datetime.now()
            max_discovery_time = 7200  # 2 hours max (increased from 30 minutes)
            consecutive_failures = 0  # Track consecutive failures
            max_consecutive_failures = 10  # Restart browser after 10 consecutive failures
            total_failures = 0  # Track total failures
            max_total_failures = 50  # Stop if too many total failures
            pages_since_restart = 0  # Track pages processed since last browser restart
            max_pages_per_session = 500  # Restart browser periodically to prevent memory issues
            logger.info(f"Starting discovery with max_pages={website.scraping_config.max_pages}, max_depth={website.scraping_config.max_depth}")
            
            while self.queued_urls and depth <= website.scraping_config.max_depth and not max_pages_reached:
                # Check for cancellation
                if job and job.is_cancelled():
                    logger.info(f"Discovery cancelled by user for website {website.id}")
                    break
                    
                # Check if discovery has been running too long
                elapsed_time = (datetime.now() - start_time).total_seconds()
                if elapsed_time > max_discovery_time:
                    logger.warning(f"Discovery timeout reached after {elapsed_time:.0f} seconds")
                    break
                    
                # Memory management - clear discovered URLs set periodically to prevent excessive memory usage
                if len(self.discovered_urls) > 10000:
                    logger.info(f"Clearing discovered URLs cache (had {len(self.discovered_urls)} entries)")
                    # Keep only the last 5000 URLs to maintain some duplicate detection
                    recent_urls = list(self.discovered_urls)[-5000:]
                    self.discovered_urls = set(recent_urls)
                    
                # Get URLs at current depth
                current_batch = list(self.queued_urls)
                self.queued_urls.clear()
                
                logger.info(f"Processing depth {depth} with {len(current_batch)} URLs, discovered so far: {len(discovered_pages)}")
                logger.info(f"Elapsed time: {elapsed_time:.0f}s, Memory: {len(self.discovered_urls)} URLs cached")
                
                for i, url in enumerate(current_batch):
                    # Add small delay every 5 URLs to allow cancellation to be processed
                    if i > 0 and i % 5 == 0:
                        await asyncio.sleep(0.1)
                    
                    # Restart browser periodically to prevent memory issues
                    if pages_since_restart >= max_pages_per_session:
                        logger.info(f"Restarting browser after {pages_since_restart} pages to prevent memory issues")
                        try:
                            await self.browser_manager.stop()
                            await asyncio.sleep(2)
                            await self.browser_manager.start()
                            pages_since_restart = 0
                            logger.info("Browser restarted successfully (periodic restart)")
                        except Exception as e:
                            logger.error(f"Failed to restart browser (periodic): {e}")
                            max_pages_reached = True
                            break
                    
                    # Check for cancellation
                    if job and job.is_cancelled():
                        logger.info(f"Discovery cancelled during URL processing for website {website.id}")
                        max_pages_reached = True  # Use this flag to exit both loops
                        break
                    
                    # Check if browser is still running before each page
                    if not await self.browser_manager.is_running():
                        logger.warning("Browser stopped during discovery, attempting restart...")
                        try:
                            await self.browser_manager.ensure_running()
                            logger.info("Browser restarted successfully after connection loss")
                            pages_since_restart = 0
                        except Exception as e:
                            logger.error(f"Failed to restart browser after connection loss: {e}")
                            max_pages_reached = True  # Use this flag to exit both loops
                            break
                    
                    # Check if we've hit page limit
                    if len(discovered_pages) >= website.scraping_config.max_pages:
                        logger.warning(f"Reached max pages limit: {website.scraping_config.max_pages} (discovered: {len(discovered_pages)})")
                        max_pages_reached = True
                        break
                    
                    # Skip if already discovered
                    if url in self.discovered_urls:
                        continue
                    
                    # Pre-filter URLs that are known to cause problems
                    # These often redirect to external sites or cause timeouts
                    problematic_params = ['?share=', '&share=', '?nb=', '&nb=', 'utm_', 'fbclid=', 'gclid=', 
                                        '#disqus_thread', '#comments', '?print=', '&print=', 
                                        'javascript:', 'mailto:', 'tel:', '.pdf', '.doc', '.ppt', '.xls']
                    if any(param in url.lower() for param in problematic_params):
                        logger.info(f"Skipping URL with problematic parameters: {url}")
                        # Still record it as a failed page so user knows it was skipped
                        failed_page = Page(
                            website_id=website.id,
                            url=url,
                            title="Skipped: Problematic URL",
                            discovered_from=website.url if depth == 0 else None,
                            depth=depth,
                            status=PageStatus.DISCOVERY_FAILED,
                            error_reason="Skipped: URL contains parameters that typically cause problems"
                        )
                        discovered_pages.append(failed_page)
                        self.discovered_urls.add(url)
                        continue
                    
                    # Check robots.txt
                    if website.scraping_config.respect_robots:
                        if not await self._can_fetch(url):
                            logger.debug(f"Skipping {url} due to robots.txt")
                            continue
                    
                    # Discover page
                    logger.info(f"[Page {len(discovered_pages) + 1}/{website.scraping_config.max_pages}] Starting discovery: {url}")
                    page = await self._discover_page(
                        url=url,
                        website=website,
                        depth=depth,
                        base_domain=base_domain,
                        base_path=base_path
                    )
                    if page:
                        status_msg = "SUCCESS" if page.status != PageStatus.DISCOVERY_FAILED else f"FAILED: {page.error_reason[:50] if page.error_reason else 'Unknown'}"
                        logger.info(f"[Page {len(discovered_pages)}/{website.scraping_config.max_pages}] {status_msg} - {url}")
                    else:
                        logger.warning(f"[Page {len(discovered_pages)}/{website.scraping_config.max_pages}] NULL RESPONSE - {url}")
                    
                    if page:
                        discovered_pages.append(page)
                        self.discovered_urls.add(url)
                        pages_since_restart += 1
                        
                        # Track failures
                        if page.status == PageStatus.DISCOVERY_FAILED:
                            consecutive_failures += 1
                            total_failures += 1
                            logger.warning(f"Failed pages: {total_failures} total, {consecutive_failures} consecutive")
                            
                            # Stop if too many total failures
                            if total_failures >= max_total_failures:
                                logger.error(f"Too many total failures ({total_failures}), stopping discovery")
                                max_pages_reached = True
                                break
                        else:
                            # Reset consecutive counter on success
                            consecutive_failures = 0
                        
                        # Update progress
                        if progress_callback:
                            progress_data = {
                                'pages_found': len(discovered_pages),
                                'current_depth': depth,
                                'queue_size': len(self.queued_urls),
                                'current_url': url
                            }
                            logger.info(f"Starting progress update for page {len(discovered_pages)}")
                            try:
                                await progress_callback(progress_data)
                                logger.info(f"Progress update completed for page {len(discovered_pages)}")
                            except Exception as e:
                                logger.error(f"Progress callback failed: {e}")
                        else:
                            logger.warning("No progress_callback provided to ScrapingEngine")
                    else:
                        # Page discovery failed
                        consecutive_failures += 1
                        logger.warning(f"Page discovery failed, consecutive failures: {consecutive_failures}")
                        
                        # If too many consecutive failures, try restarting browser
                        if consecutive_failures >= max_consecutive_failures:
                            logger.warning(f"Too many consecutive failures ({consecutive_failures}), attempting browser restart")
                            try:
                                await self.browser_manager.stop()
                                await asyncio.sleep(2)  # Brief pause
                                await self.browser_manager.start()
                                logger.info("Browser restarted successfully after failures")
                                consecutive_failures = 0  # Reset counter
                                pages_since_restart = 0  # Reset page counter
                            except Exception as e:
                                logger.error(f"Failed to restart browser: {e}")
                                max_pages_reached = True
                                break
                        
                        # Check if browser is still running
                        if not await self.browser_manager.is_running():
                            logger.error("Browser failed during page discovery, stopping")
                            max_pages_reached = True
                            break
                    
                    # Respect rate limiting
                    await asyncio.sleep(website.scraping_config.request_delay)
                
                depth += 1
            
            # Check if discovery was cancelled
            was_cancelled = job and job.is_cancelled()
            
            # Log final statistics
            successful_pages = len([p for p in discovered_pages if p.status != PageStatus.DISCOVERY_FAILED])
            failed_pages = len([p for p in discovered_pages if p.status == PageStatus.DISCOVERY_FAILED])
            logger.info(f"Discovery finished: {successful_pages} successful, {failed_pages} failed, {len(discovered_pages)} total")
            
            # Save discovered pages to database with discovery run tracking
            saved_count = 0
            if discovered_pages:
                saved_count = self.db.bulk_create_pages_with_discovery(discovered_pages, discovery_run_id)
                logger.info(f"Saved/updated {saved_count} pages in database")
            
            # Compare with previous discovery if it exists
            if previous_run:
                comparison = self.db.compare_discoveries(
                    website.id,
                    previous_run.id,
                    discovery_run_id
                )
                discovery_run.pages_added = comparison['added_count']
                discovery_run.pages_removed = comparison['removed_count']
                discovery_run.pages_unchanged = comparison['unchanged_count']
                logger.info(f"Discovery comparison: +{discovery_run.pages_added} added, -{discovery_run.pages_removed} removed, {discovery_run.pages_unchanged} unchanged")
            
            # Update discovery run with final results
            discovery_run.completed_at = datetime.now()
            discovery_run.status = DiscoveryStatus.CANCELLED if was_cancelled else DiscoveryStatus.COMPLETED
            discovery_run.pages_discovered = len([p for p in discovered_pages if p.status != PageStatus.DISCOVERY_FAILED])
            discovery_run.pages_failed = len([p for p in discovered_pages if p.status == PageStatus.DISCOVERY_FAILED])
            discovery_run.documents_found = self.db.document_references.count_documents({'website_id': website.id})
            discovery_run.duration_seconds = int((discovery_run.completed_at - discovery_run.started_at).total_seconds())
            self.db.update_discovery_run(discovery_run)
            
            # Update website last scraped timestamp
            website.last_scraped = datetime.now()
            self.db.update_website(website)
            
        except Exception as e:
            logger.error(f"Error during discovery: {e}", exc_info=True)
            
            # Save what we got so far
            if discovered_pages:
                saved_count = self.db.bulk_create_pages_with_discovery(discovered_pages, discovery_run_id)
                logger.info(f"Saved {saved_count} pages before error")
            
            # Update discovery run with error
            discovery_run.completed_at = datetime.now()
            discovery_run.status = DiscoveryStatus.FAILED
            discovery_run.error_message = str(e)[:500]
            discovery_run.pages_discovered = len([p for p in discovered_pages if p.status != PageStatus.DISCOVERY_FAILED])
            discovery_run.pages_failed = len([p for p in discovered_pages if p.status == PageStatus.DISCOVERY_FAILED])
            discovery_run.duration_seconds = int((discovery_run.completed_at - discovery_run.started_at).total_seconds())
            self.db.update_discovery_run(discovery_run)
            
            # Update website last scraped timestamp
            website.last_scraped = datetime.now()
            self.db.update_website(website)
            
            if progress_callback:
                await progress_callback({
                    'status': 'failed',
                    'error': str(e)
                })
            raise
        finally:
            await self.browser_manager.stop()
            logger.info("Browser stopped after discovery session")
        
        logger.info(f"Discovery complete. Found {len(discovered_pages)} pages")
        return discovered_pages
    
    async def _discover_page(
        self,
        url: str,
        website: Website,
        depth: int,
        base_domain: str,
        base_path: str = "",
        browser_page=None
    ) -> Optional[Page]:
        """
        Discover a single page and extract links
        
        Args:
            url: URL to discover
            website: Website object
            depth: Current crawl depth
            base_domain: Base domain for filtering
            browser_page: Optional existing page to reuse
            
        Returns:
            Page object or None if failed
        """
        # Check if browser is still running, restart if needed
        if not await self.browser_manager.is_running():
            logger.warning(f"Browser not running before discovering {url}, attempting restart...")
            try:
                await self.browser_manager.ensure_running()
                logger.info("Browser restarted successfully")
            except Exception as e:
                logger.error(f"Failed to restart browser: {e}")
                # Return a failed page record
                return Page(
                    website_id=website.id,
                    url=url,
                    title="Failed: Browser crashed",
                    discovered_from=website.url if depth == 0 else None,
                    depth=depth,
                    status=PageStatus.DISCOVERY_FAILED,
                    error_reason="Browser not running and failed to restart"
                )
            
        page = None
        try:
            # Check browser connection before creating page
            if not self.browser_manager.browser:
                logger.error("Browser instance is None")
                return Page(
                    website_id=website.id,
                    url=url,
                    title="Failed: Browser error",
                    discovered_from=website.url if depth == 0 else None,
                    depth=depth,
                    status=PageStatus.DISCOVERY_FAILED,
                    error_reason="Browser instance unavailable"
                )
                
            # Create a new page with error handling
            try:
                page = await self.browser_manager.browser.newPage()
            except Exception as e:
                logger.error(f"Failed to create new page: {e}")
                # Browser might be in bad state, try to restart
                try:
                    await self.browser_manager.ensure_running()
                    page = await self.browser_manager.browser.newPage()
                except Exception as e2:
                    logger.error(f"Failed to create page even after restart: {e2}")
                    return Page(
                        website_id=website.id,
                        url=url,
                        title="Failed: Cannot create page",
                        discovered_from=website.url if depth == 0 else None,
                        depth=depth,
                        status=PageStatus.DISCOVERY_FAILED,
                        error_reason=f"Failed to create browser page: {str(e2)[:200]}"
                    )

            # Apply stealth techniques to avoid bot detection
            await self.browser_manager._apply_stealth(page)

            # Set viewport
            await page.setViewport({
                'width': self.browser_manager.config.get('viewport_width', 1920),
                'height': self.browser_manager.config.get('viewport_height', 1080)
            })

            # Set realistic user agent
            user_agent = self.browser_manager.config.get('user_agent',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            await page.setUserAgent(user_agent)

            # Configure timeouts and wait conditions based on stealth mode
            stealth_mode = self.browser_manager.config.get('stealth_mode', False)

            if stealth_mode:
                # Slower, more thorough for Cloudflare-protected sites
                page.setDefaultNavigationTimeout(45000)  # 45 seconds
                wait_until = 'networkidle0'  # Wait for all network activity to stop
                nav_timeout = 40000  # 40 seconds
                post_nav_wait = 3  # Wait 3 seconds after navigation
            else:
                # Faster for normal sites
                page.setDefaultNavigationTimeout(25000)  # 25 seconds
                wait_until = 'domcontentloaded'  # Just wait for DOM
                nav_timeout = 20000  # 20 seconds
                post_nav_wait = 0  # No extra wait

            # Navigate to URL with proper error handling
            response = None
            try:
                response = await self.browser_manager.goto(
                    page=page,
                    url=url,
                    wait_until=wait_until,
                    timeout=nav_timeout
                )

                # Wait additional time for JavaScript challenges if in stealth mode
                if post_nav_wait > 0:
                    await asyncio.sleep(post_nav_wait)

                # Check if we're stuck on a Cloudflare challenge page
                try:
                    page_title = await page.title()
                    page_content = await page.content()

                    # Detect Cloudflare challenge indicators
                    if 'cloudflare' in page_title.lower() or 'checking your browser' in page_content.lower():
                        logger.warning(f"Cloudflare challenge detected on: {url}")
                        logger.warning(f"Page title: {page_title}")
                        # Wait longer for challenge to complete
                        await asyncio.sleep(10)
                        page_title = await page.title()
                        page_content = await page.content()
                        if 'cloudflare' in page_title.lower() or 'checking your browser' in page_content.lower():
                            logger.error(f"Cloudflare challenge failed to complete for: {url}")
                            return Page(
                                website_id=website.id,
                                url=url,
                                title="Failed: Cloudflare challenge",
                                discovered_from=website.url if depth == 0 else None,
                                depth=depth,
                                status=PageStatus.DISCOVERY_FAILED,
                                error_reason="Stuck on Cloudflare challenge page"
                            )

                    logger.info(f"Successfully loaded page: {url} (title: {page_title[:50]})")
                except Exception as e:
                    logger.warning(f"Could not check page content for {url}: {e}")

                if not response:
                    logger.warning(f"Failed to load page: {url}")
                    # Return a failed page record instead of None
                    return Page(
                        website_id=website.id,
                        url=url,
                        title="Failed: No response",
                        discovered_from=website.url if depth == 0 else None,
                        depth=depth,
                        status=PageStatus.DISCOVERY_FAILED,
                        error_reason="No response from server"
                    )
                
                # Check if we were redirected to an external domain
                final_url = page.url
                if final_url and final_url != url:
                    final_parsed = urlparse(final_url)
                    final_domain = final_parsed.netloc
                    
                    # Log all redirects for debugging
                    logger.info(f"Page redirected: {url} -> {final_url}")
                    
                    if final_domain and final_domain != base_domain:
                        # Check if it's a subdomain of our base domain
                        if not final_domain.endswith(f'.{base_domain}'):
                            logger.warning(f"SKIPPING: Redirected to external domain {final_domain} from {url}")
                            # Create a failed page record
                            failed_page = Page(
                                website_id=website.id,
                                url=url,
                                title=f"Failed: External redirect",
                                discovered_from=website.url if depth == 0 else None,
                                depth=depth,
                                status=PageStatus.DISCOVERY_FAILED,
                                error_reason=f"Redirected to external domain: {final_domain}"
                            )
                            return failed_page
                        else:
                            logger.debug(f"Redirect to subdomain accepted: {final_domain}")
                    
                    # Also check if redirected outside base path
                    if base_path and final_domain == base_domain:
                        final_path = final_parsed.path
                        if not final_path.startswith(base_path + '/') and final_path != base_path:
                            logger.warning(f"SKIPPING: Redirected outside base path from {url} to {final_url}")
                            failed_page = Page(
                                website_id=website.id,
                                url=url,
                                title=f"Failed: Redirect outside scope",
                                discovered_from=website.url if depth == 0 else None,
                                depth=depth,
                                status=PageStatus.DISCOVERY_FAILED,
                                error_reason=f"Redirected outside base path: {final_path}"
                            )
                            return failed_page
                            
            except (TimeoutError, Exception) as e:
                logger.warning(f"Navigation failed for {url}: {e}")
                # IMPORTANT: Close the page to prevent browser hanging
                if page:
                    try:
                        await page.close()
                    except:
                        pass
                    page = None  # Clear reference
                
                # Check if browser is still alive after navigation failure
                if not await self.browser_manager.is_running():
                    logger.warning("Browser connection lost after navigation failure")
                    # Try to restart browser for next page
                    try:
                        await self.browser_manager.ensure_running()
                        logger.info("Browser restarted after navigation failure")
                    except:
                        pass  # Will be handled on next page attempt
                
                # Create a failed page record
                failed_page = Page(
                    website_id=website.id,
                    url=url,
                    title="Failed: Navigation error",
                    discovered_from=website.url if depth == 0 else None,
                    depth=depth,
                    status=PageStatus.DISCOVERY_FAILED,
                    error_reason=f"Navigation failed: {str(e)[:200]}"
                )
                return failed_page
            
            # Get page title
            title = await self.browser_manager.get_page_title(page)
            
            # Extract links if not at max depth
            if depth < website.scraping_config.max_depth:
                try:
                    links = await self._extract_links(page, url, website, base_domain, base_path)
                    self.queued_urls.update(links)
                except Exception as e:
                    logger.warning(f"Failed to extract links from {url}: {e}")
                    # Continue without links rather than failing the whole page

            # Take screenshot during discovery for page preview
            screenshot_path = None
            try:
                screenshot_path = await self._take_discovery_screenshot(page, website.id, url)
                if screenshot_path:
                    logger.debug(f"Discovery screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.warning(f"Failed to take discovery screenshot for {url}: {e}")
                # Continue without screenshot rather than failing the whole page

            # Close the page now that we're done with it
            try:
                await page.close()
                page = None  # Mark as closed
            except Exception as e:
                logger.warning(f"Error closing page after successful discovery: {e}")

            # Create page object
            page_obj = Page(
                website_id=website.id,
                url=url,
                title=title or "Untitled",
                discovered_from=website.url if depth == 0 else None,
                depth=depth,
                status=PageStatus.DISCOVERED,
                screenshot_path=screenshot_path  # Add screenshot from discovery
            )
            
            logger.debug(f"Discovered page: {url} - {title}")
            return page_obj
                
        except TimeoutError:
            logger.warning(f"Timeout loading page: {url}")
            # Check browser health after timeout
            if not await self.browser_manager.is_running():
                logger.warning("Browser died after timeout, will restart on next page")
            # Create a failed page record for timeout
            return Page(
                website_id=website.id,
                url=url,
                title="Failed: Timeout",
                discovered_from=website.url if depth == 0 else None,
                depth=depth,
                status=PageStatus.DISCOVERY_FAILED,
                error_reason="Page load timeout (25 seconds)"
            )
        except Exception as e:
            logger.error(f"Error discovering page {url}: {e}", exc_info=True)
            # Create a failed page record for other errors
            return Page(
                website_id=website.id,
                url=url,
                title="Failed: Error",
                discovered_from=website.url if depth == 0 else None,
                depth=depth,
                status=PageStatus.DISCOVERY_FAILED,
                error_reason=f"Discovery error: {str(e)[:200]}"
            )
        finally:
            # Close the page if it's still open (only happens on error paths)
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
    
    async def _extract_links(
        self,
        page,
        current_url: str,
        website: Website,
        base_domain: str,
        base_path: str = ""
    ) -> Set[str]:
        """
        Extract and filter links from a page
        
        Args:
            page: Pyppeteer page object
            current_url: Current page URL
            website: Website configuration
            base_domain: Base domain for filtering
            
        Returns:
            Set of valid URLs to crawl
        """
        try:
            # Extract all links with their text using JavaScript
            links_with_text = await page.evaluate('''
                () => {
                    const anchors = document.querySelectorAll('a[href]');
                    return Array.from(anchors).map(a => ({
                        href: a.href,
                        text: a.textContent.trim()
                    }));
                }
            ''')
            
            # Filter and normalize links
            valid_links = set()
            document_refs = []  # Collect document references
            
            for link_data in links_with_text:
                link = link_data['href']
                link_text = link_data.get('text', '')
                # Skip empty or invalid links
                if not link or link.startswith('#') or link.startswith('javascript:'):
                    continue
                
                # Skip mailto, tel, and other non-HTTP protocols
                if link.startswith(('mailto:', 'tel:', 'ftp:', 'file:')):
                    continue
                
                # Normalize URL
                normalized = self._normalize_url(link, current_url)
                if not normalized:
                    continue
                
                # Parse URL
                parsed = urlparse(normalized)
                
                # Check if we should follow this link
                if not website.scraping_config.follow_external:
                    # Only follow links on same domain
                    if parsed.netloc != base_domain:
                        # Check subdomains if configured
                        if not (website.scraping_config.include_subdomains and 
                               parsed.netloc.endswith(f'.{base_domain}')):
                            continue
                    
                    # If the base URL has a path component, ensure links stay within that path
                    if base_path:
                        # The link must start with the base path to be considered internal
                        if not parsed.path.startswith(base_path + '/') and parsed.path != base_path:
                            logger.debug(f"Skipping URL outside base path: {normalized} (base_path: {base_path})")
                            continue
                
                # Apply path filters
                path = parsed.path
                
                # Check for document files
                document_extensions = {
                    '.pdf': 'application/pdf',
                    '.doc': 'application/msword',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.xls': 'application/vnd.ms-excel',
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.document',
                    '.ppt': 'application/vnd.ms-powerpoint',
                    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.document',
                    '.rtf': 'application/rtf',
                    '.txt': 'text/plain',
                    '.csv': 'text/csv',
                    '.zip': 'application/zip',
                    '.rar': 'application/zip',
                    '.7z': 'application/zip'
                }
                
                # Check if this is a document
                file_ext = None
                for ext in document_extensions:
                    if path.lower().endswith(ext):
                        file_ext = ext
                        break
                
                if file_ext:
                    # This is a document, capture it
                    is_internal = parsed.netloc == base_domain or (
                        website.scraping_config.include_subdomains and 
                        parsed.netloc.endswith(f'.{base_domain}')
                    )
                    
                    document_refs.append({
                        'url': normalized,
                        'mime_type': document_extensions[file_ext],
                        'is_internal': is_internal,
                        'link_text': link_text,
                        'file_extension': file_ext
                    })
                    continue  # Don't add to crawl queue
                
                # Skip common non-HTML resources (images, videos, etc.)
                if path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.exe', '.dmg', '.mp4', '.mp3')):
                    continue
                
                # Check excluded paths
                if website.scraping_config.excluded_paths:
                    if any(path.startswith(exc) for exc in website.scraping_config.excluded_paths):
                        continue
                
                # Check allowed paths
                if website.scraping_config.allowed_paths:
                    if not any(path.startswith(allow) for allow in website.scraping_config.allowed_paths):
                        continue
                
                valid_links.add(normalized)
            
            logger.debug(f"Extracted {len(valid_links)} valid links and {len(document_refs)} documents from {current_url}")
            
            # Save document references to database
            if document_refs:
                await self._save_document_references(document_refs, website.id, current_url)
            
            return valid_links
            
        except Exception as e:
            logger.error(f"Error extracting links from {current_url}: {e}")
            return set()
    
    async def _save_document_references(self, document_refs: list, website_id: str, referring_page_url: str):
        """
        Save document references to database with language detection
        
        Args:
            document_refs: List of document reference data
            website_id: Website ID
            referring_page_url: URL of the page containing the links
        """
        from auto_a11y.models import DocumentReference
        
        for doc_data in document_refs:
            try:
                # Detect language from link text and URL
                language = await self._detect_document_language(
                    doc_data['url'],
                    doc_data.get('link_text'),
                    doc_data.get('file_extension')
                )
                
                doc_ref = DocumentReference(
                    website_id=website_id,
                    document_url=doc_data['url'],
                    referring_page_url=referring_page_url,
                    mime_type=doc_data['mime_type'],
                    is_internal=doc_data['is_internal'],
                    link_text=doc_data.get('link_text'),
                    file_extension=doc_data.get('file_extension'),
                    language=language.get('language') if language else None,
                    language_confidence=language.get('confidence') if language else None,
                    via_redirect=False  # Direct link, not via redirect
                )
                
                self.db.add_document_reference(doc_ref)
                lang_info = f" ({language['language']})" if language else ""
                logger.debug(f"Saved document reference: {doc_data['url']} ({'internal' if doc_data['is_internal'] else 'external'}){lang_info}")
            except Exception as e:
                logger.error(f"Error saving document reference {doc_data['url']}: {e}")
    
    async def _detect_document_language(self, doc_url: str, link_text: str = None, file_extension: str = None) -> Optional[Dict[str, Any]]:
        """
        Detect the language of a document using multiple methods
        
        Args:
            doc_url: URL of the document
            link_text: Text of the link to the document
            file_extension: File extension of the document
            
        Returns:
            Dictionary with 'language' code and 'confidence' score, or None
        """
        import aiohttp
        
        try:
            # Try to fetch document headers and content
            async with aiohttp.ClientSession() as session:
                async with session.head(doc_url, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True) as response:
                    # 1. Check Content-Language header
                    content_language = response.headers.get('Content-Language')
                    if content_language:
                        # Parse language code (e.g., "en-US" -> "en", "fr-CA" -> "fr")
                        lang_code = content_language.split('-')[0].lower()
                        logger.debug(f"Detected language from Content-Language header: {lang_code} for {doc_url}")
                        return {'language': lang_code, 'confidence': 0.95}
                    
                    # For small documents, download and analyze content
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) < 5 * 1024 * 1024:  # Less than 5MB
                        # Download the document
                        async with session.get(doc_url, timeout=aiohttp.ClientTimeout(total=15)) as content_response:
                            content = await content_response.read()
                            
                            # 2. Extract metadata based on file type
                            if file_extension in ['.pdf', 'pdf']:
                                lang = await self._detect_pdf_language(content)
                                if lang:
                                    return lang
                            elif file_extension in ['.docx', 'docx']:
                                lang = await self._detect_docx_language(content)
                                if lang:
                                    return lang
                            
                            # 3. Analyze text content for language patterns
                            lang = await self._detect_language_from_content(content, file_extension)
                            if lang:
                                return lang
        
        except Exception as e:
            logger.debug(f"Error fetching document for language detection: {e}")
        
        # 4. Fallback: Analyze URL and link text patterns
        return self._detect_language_from_patterns(doc_url, link_text)
    
    async def _detect_pdf_language(self, content: bytes) -> Optional[Dict[str, Any]]:
        """
        Detect language from PDF metadata and content
        
        Args:
            content: PDF file content as bytes
            
        Returns:
            Dictionary with language info or None
        """
        try:
            import PyPDF2
            
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check PDF metadata
            if pdf_reader.metadata:
                # Check for language in metadata
                if '/Lang' in pdf_reader.metadata:
                    lang_code = pdf_reader.metadata['/Lang']
                    if isinstance(lang_code, str):
                        # Parse language code (e.g., "en-US" -> "en")
                        lang_code = lang_code.split('-')[0].lower()
                        logger.debug(f"Detected language from PDF metadata: {lang_code}")
                        return {'language': lang_code, 'confidence': 0.9}
            
            # Extract text from first few pages for analysis
            text_sample = ""
            max_pages = min(3, len(pdf_reader.pages))
            for i in range(max_pages):
                try:
                    text_sample += pdf_reader.pages[i].extract_text()
                    if len(text_sample) > 1000:  # Enough text for analysis
                        break
                except:
                    continue
            
            if text_sample:
                return self._analyze_text_language(text_sample)
                
        except Exception as e:
            logger.debug(f"Error detecting PDF language: {e}")
        
        return None
    
    async def _detect_docx_language(self, content: bytes) -> Optional[Dict[str, Any]]:
        """
        Detect language from Word document metadata and content
        
        Args:
            content: DOCX file content as bytes
            
        Returns:
            Dictionary with language info or None
        """
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            
            # DOCX files are ZIP archives
            with zipfile.ZipFile(BytesIO(content)) as docx:
                # Check core properties for language
                if 'docProps/core.xml' in docx.namelist():
                    core_xml = docx.read('docProps/core.xml')
                    root = ET.fromstring(core_xml)
                    
                    # Look for dc:language element
                    for elem in root.iter():
                        if 'language' in elem.tag.lower():
                            lang_code = elem.text
                            if lang_code:
                                lang_code = lang_code.split('-')[0].lower()
                                logger.debug(f"Detected language from DOCX metadata: {lang_code}")
                                return {'language': lang_code, 'confidence': 0.9}
                
                # Extract text for analysis
                if 'word/document.xml' in docx.namelist():
                    doc_xml = docx.read('word/document.xml')
                    root = ET.fromstring(doc_xml)
                    
                    # Extract text from document
                    text_sample = ""
                    for elem in root.iter():
                        if elem.text:
                            text_sample += elem.text + " "
                            if len(text_sample) > 1000:
                                break
                    
                    if text_sample:
                        return self._analyze_text_language(text_sample)
                        
        except Exception as e:
            logger.debug(f"Error detecting DOCX language: {e}")
        
        return None
    
    async def _detect_language_from_content(self, content: bytes, file_extension: str = None) -> Optional[Dict[str, Any]]:
        """
        Detect language from document content
        
        Args:
            content: Document content as bytes
            file_extension: File extension for text extraction
            
        Returns:
            Dictionary with language info or None
        """
        try:
            # For text-based files, decode and analyze
            if file_extension in ['.txt', '.csv', '.rtf', 'txt', 'csv', 'rtf']:
                # Try different encodings
                text = None
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        text = content.decode(encoding)
                        break
                    except:
                        continue
                
                if text:
                    return self._analyze_text_language(text[:5000])  # Analyze first 5000 chars
                    
        except Exception as e:
            logger.debug(f"Error detecting language from content: {e}")
        
        return None
    
    def _analyze_text_language(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze text to detect language using pattern matching
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with language info or None
        """
        if not text or len(text) < 50:
            return None
        
        # Clean text
        text = text.lower().strip()
        
        # Language-specific patterns and common words
        language_patterns = {
            'en': {
                'words': ['the', 'and', 'of', 'to', 'in', 'is', 'for', 'with', 'that', 'this', 
                         'are', 'was', 'will', 'have', 'been', 'from', 'can', 'which', 'their', 'would'],
                'patterns': [r'\b(the|and|of|to|in)\b', r'\b(is|are|was|were)\b', r'\b(have|has|had)\b'],
                'weight': 1.0
            },
            'fr': {
                'words': ['le', 'la', 'les', 'de', 'et', 'est', 'pour', 'dans', 'avec', 'sur',
                         'une', 'des', 'que', 'qui', 'par', 'plus', 'sont', 'être', 'avoir', 'faire'],
                'patterns': [r'\b(le|la|les|un|une|des)\b', r'\b(de|du|des)\b', r'\b(est|sont|être)\b',
                           r'[àâäéèêëïîôùûü]'],  # French accented characters
                'weight': 1.2  # Slight boost for French since it's a priority
            },
            'es': {
                'words': ['el', 'la', 'de', 'y', 'en', 'que', 'es', 'por', 'con', 'para',
                         'los', 'las', 'una', 'se', 'del', 'al', 'más', 'pero', 'su', 'lo'],
                'patterns': [r'\b(el|la|los|las)\b', r'\b(de|del)\b', r'\b(es|son|está|están)\b',
                           r'[áéíóúñü]'],  # Spanish accented characters
                'weight': 1.0
            },
            'de': {
                'words': ['der', 'die', 'das', 'und', 'in', 'ist', 'mit', 'auf', 'für', 'von',
                         'den', 'des', 'ein', 'eine', 'sich', 'zu', 'werden', 'haben', 'sein', 'ihr'],
                'patterns': [r'\b(der|die|das|den|dem)\b', r'\b(ein|eine|einen)\b', r'\b(ist|sind|war|waren)\b',
                           r'[äöüß]'],  # German special characters
                'weight': 1.0
            }
        }
        
        scores = {}
        
        for lang, config in language_patterns.items():
            score = 0
            word_count = 0
            
            # Count occurrences of common words
            for word in config['words']:
                count = text.count(f' {word} ') + text.count(f' {word}.') + text.count(f' {word},')
                if count > 0:
                    word_count += count
                    score += count * config['weight']
            
            # Check patterns
            for pattern in config['patterns']:
                matches = len(re.findall(pattern, text))
                if matches > 0:
                    score += matches * 0.5 * config['weight']
            
            # Normalize score by text length
            scores[lang] = score / (len(text) / 100)
        
        # Get the language with highest score
        if scores:
            best_lang = max(scores, key=scores.get)
            best_score = scores[best_lang]
            
            # Calculate confidence based on score differential
            sorted_scores = sorted(scores.values(), reverse=True)
            if len(sorted_scores) > 1:
                confidence = min(0.85, 0.5 + (sorted_scores[0] - sorted_scores[1]) / 10)
            else:
                confidence = 0.7
            
            # Only return if score is significant
            if best_score > 0.5:
                logger.debug(f"Detected language from text analysis: {best_lang} (confidence: {confidence:.2f})")
                return {'language': best_lang, 'confidence': confidence}
        
        return None
    
    def _detect_language_from_patterns(self, url: str, link_text: str = None) -> Optional[Dict[str, Any]]:
        """
        Detect language from URL patterns and link text as fallback
        
        Args:
            url: Document URL
            link_text: Link text
            
        Returns:
            Dictionary with language info or None
        """
        # URL patterns that indicate language
        url_patterns = {
            'fr': ['/fr/', '_fr', '-fr', 'french', 'francais', 'français'],
            'en': ['/en/', '_en', '-en', 'english', 'anglais'],
            'es': ['/es/', '_es', '-es', 'spanish', 'espanol', 'español'],
            'de': ['/de/', '_de', '-de', 'german', 'deutsch', 'allemand']
        }
        
        url_lower = url.lower()
        
        for lang, patterns in url_patterns.items():
            for pattern in patterns:
                if pattern in url_lower:
                    logger.debug(f"Detected language from URL pattern: {lang}")
                    return {'language': lang, 'confidence': 0.6}
        
        # Check link text for language indicators
        if link_text:
            link_lower = link_text.lower()
            
            # French indicators
            if any(word in link_lower for word in ['français', 'francais', 'french', 'version française']):
                return {'language': 'fr', 'confidence': 0.7}
            
            # English indicators
            if any(word in link_lower for word in ['english', 'anglais', 'version anglaise']):
                return {'language': 'en', 'confidence': 0.7}
            
            # Analyze link text itself
            lang_result = self._analyze_text_language(link_text)
            if lang_result:
                lang_result['confidence'] *= 0.7  # Lower confidence for short text
                return lang_result
        
        return None
    
    def _normalize_url(self, url: str, base_url: Optional[str] = None) -> Optional[str]:
        """
        Normalize and validate URL
        
        Args:
            url: URL to normalize
            base_url: Base URL for relative links
            
        Returns:
            Normalized URL or None if invalid
        """
        try:
            # Handle relative URLs
            if base_url and not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)
            
            # Parse URL
            parsed = urlparse(url)
            
            # Ensure HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return None
            
            # Remove fragment
            parsed = parsed._replace(fragment='')
            
            # Normalize path - for root, remove the path entirely or use empty string
            # This makes both "example.com" and "example.com/" normalize to "example.com"
            path = parsed.path
            if path == '/':
                # Root path - remove it for consistent normalization
                parsed = parsed._replace(path='')
            elif path.endswith('/'):
                # Non-root path with trailing slash - remove the slash
                path = path[:-1]
                parsed = parsed._replace(path=path)
            
            # Reconstruct URL
            normalized = urlunparse(parsed)
            
            return normalized
            
        except Exception as e:
            logger.debug(f"Failed to normalize URL {url}: {e}")
            return None
    
    async def _can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt

        Args:
            url: URL to check

        Returns:
            True if URL can be fetched
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            # Check cache
            if robots_url not in self.robots_cache:
                # For now, skip robots.txt checking to avoid page conflicts
                # TODO: Implement proper robots.txt fetching with requests library
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.parse(['User-agent: *', 'Allow: /'])
                self.robots_cache[robots_url] = rp

            # Check if URL is fetchable
            return self.robots_cache[robots_url].can_fetch('*', url)

        except Exception as e:
            logger.debug(f"Error checking robots.txt for {url}: {e}")
            # Default to allow on error
            return True

    async def _take_discovery_screenshot(self, page, website_id: str, url: str) -> Optional[str]:
        """
        Take screenshot during page discovery for preview thumbnail

        Args:
            page: Pyppeteer page object
            website_id: Website ID
            url: Page URL being discovered

        Returns:
            Screenshot file path or None if failed
        """
        try:
            from pathlib import Path

            # Create screenshots directory if it doesn't exist
            screenshot_dir = Path('screenshots')
            screenshot_dir.mkdir(exist_ok=True, parents=True)

            # Generate filename using URL hash to keep it reasonable length
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"discovery_{website_id}_{url_hash}_{timestamp}.jpg"
            filepath = screenshot_dir / filename

            # Take screenshot with browser manager
            await self.browser_manager.take_screenshot(
                page,
                path=str(filepath),
                full_page=True
            )

            logger.debug(f"Discovery screenshot saved: {filepath}")
            # Return just the filename, not the full path with screenshots/
            return filename

        except Exception as e:
            logger.warning(f"Failed to take discovery screenshot for {url}: {e}")
            return None


# ScrapingJob class has been moved to scraping_job.py for database-backed implementation