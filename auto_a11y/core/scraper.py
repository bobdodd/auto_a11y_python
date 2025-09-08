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

from pyppeteer import launch
from pyppeteer.errors import TimeoutError, PageError, NetworkError
from bs4 import BeautifulSoup

from auto_a11y.models.page import Page, PageStatus
from auto_a11y.models.website import Website
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
        
        # Record discovery attempt in history
        discovery_record = {
            'started_at': datetime.now(),
            'max_pages': website.scraping_config.max_pages,
            'max_depth': website.scraping_config.max_depth,
            'status': 'running'
        }
        
        # Reset discovery state
        self.discovered_urls.clear()
        self.queued_urls.clear()
        
        # Parse base URL
        base_url = self._normalize_url(website.url)
        base_domain = urlparse(base_url).netloc
        
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
            max_discovery_time = 1800  # 30 minutes max
            consecutive_failures = 0  # Track consecutive failures
            max_consecutive_failures = 3  # Restart browser after 3 consecutive failures
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
                # Get URLs at current depth
                current_batch = list(self.queued_urls)
                self.queued_urls.clear()
                
                logger.info(f"Processing depth {depth} with {len(current_batch)} URLs, discovered so far: {len(discovered_pages)}")
                
                for i, url in enumerate(current_batch):
                    # Add small delay every 5 URLs to allow cancellation to be processed
                    if i > 0 and i % 5 == 0:
                        await asyncio.sleep(0.1)
                    
                    # Check for cancellation
                    if job and job.is_cancelled():
                        logger.info(f"Discovery cancelled during URL processing for website {website.id}")
                        max_pages_reached = True  # Use this flag to exit both loops
                        break
                    
                    # Check if browser is still running before each page
                    if not await self.browser_manager.is_running():
                        logger.error("Browser stopped during discovery, aborting")
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
                    if '?share=' in url or '&share=' in url or '?nb=' in url or '&nb=' in url:
                        logger.info(f"Skipping URL with problematic parameters: {url}")
                        # Still record it as a failed page so user knows it was skipped
                        failed_page = Page(
                            website_id=website.id,
                            url=url,
                            title="Skipped: Share/social link",
                            discovered_from=website.url if depth == 0 else None,
                            depth=depth,
                            status=PageStatus.DISCOVERY_FAILED,
                            error_reason="Skipped: URL contains share/social parameters that typically redirect externally"
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
                    logger.info(f"Starting discovery of page {len(discovered_pages) + 1}: {url}")
                    page = await self._discover_page(
                        url=url,
                        website=website,
                        depth=depth,
                        base_domain=base_domain
                    )
                    logger.info(f"Completed discovery of {url}, status: {page.status if page else 'None'}")
                    
                    if page:
                        discovered_pages.append(page)
                        self.discovered_urls.add(url)
                        # Reset failure counter on success
                        if page.status != PageStatus.DISCOVERY_FAILED:
                            consecutive_failures = 0
                    # Note: Failed pages are already added to discovered_pages in _discover_page
                        
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
                                logger.info("Browser restarted successfully")
                                consecutive_failures = 0  # Reset counter
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
            
            # Save discovered pages to database
            saved_count = 0
            if discovered_pages:
                saved_count = self.db.bulk_create_pages(discovered_pages)
                logger.info(f"Saved {saved_count} new pages to database")
            
            # Update discovery record with results
            discovery_record['completed_at'] = datetime.now()
            discovery_record['status'] = 'completed'
            discovery_record['pages_discovered'] = len([p for p in discovered_pages if p.status != PageStatus.DISCOVERY_FAILED])
            discovery_record['pages_failed'] = len([p for p in discovered_pages if p.status == PageStatus.DISCOVERY_FAILED])
            discovery_record['total_pages'] = len(discovered_pages)
            
            # Update website with history
            website.last_scraped = datetime.now()
            if not hasattr(website, 'discovery_history'):
                website.discovery_history = []
            website.discovery_history.append(discovery_record)
            self.db.update_website(website)
            
        except Exception as e:
            logger.error(f"Error during discovery: {e}", exc_info=True)
            
            # Update discovery record with error
            discovery_record['completed_at'] = datetime.now()
            discovery_record['status'] = 'failed'
            discovery_record['error'] = str(e)[:500]
            discovery_record['pages_discovered'] = len([p for p in discovered_pages if p.status != PageStatus.DISCOVERY_FAILED])
            discovery_record['pages_failed'] = len([p for p in discovered_pages if p.status == PageStatus.DISCOVERY_FAILED])
            discovery_record['total_pages'] = len(discovered_pages)
            
            # Save what we got so far
            if discovered_pages:
                saved_count = self.db.bulk_create_pages(discovered_pages)
                logger.info(f"Saved {saved_count} pages before error")
            
            # Update website with history
            if not hasattr(website, 'discovery_history'):
                website.discovery_history = []
            website.discovery_history.append(discovery_record)
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
        # Check if browser is still running
        if not await self.browser_manager.is_running():
            logger.error("Browser is not running, cannot discover page")
            # Return a failed page record
            return Page(
                website_id=website.id,
                url=url,
                title="Failed: Browser crashed",
                discovered_from=website.url if depth == 0 else None,
                depth=depth,
                status=PageStatus.DISCOVERY_FAILED,
                error_reason="Browser not running"
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
                
            # Create a new page
            page = await self.browser_manager.browser.newPage()
            
            # Set viewport
            await page.setViewport({
                'width': self.browser_manager.config.get('viewport_width', 1920),
                'height': self.browser_manager.config.get('viewport_height', 1080)
            })
            
            # Set navigation timeout - shorter to avoid hanging on problematic pages
            page.setDefaultNavigationTimeout(20000)  # 20 seconds, same as goto timeout
            
            # Navigate to URL with shorter timeout and less strict wait condition
            try:
                response = await self.browser_manager.goto(
                    page=page,
                    url=url,
                    wait_until='domcontentloaded',  # Just wait for DOM, not all resources
                    timeout=15000  # 15 seconds timeout per page - shorter to fail faster
                )
                
                if not response:
                    logger.warning(f"Failed to load page: {url}")
                    return None
                
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
                            
            except Exception as e:
                logger.warning(f"Navigation failed for {url}: {e}")
                # IMPORTANT: Close the page to prevent browser hanging
                if page:
                    try:
                        await page.close()
                    except:
                        pass
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
                    links = await self._extract_links(page, url, website, base_domain)
                    self.queued_urls.update(links)
                except Exception as e:
                    logger.warning(f"Failed to extract links from {url}: {e}")
                    # Continue without links rather than failing the whole page
            
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
                status=PageStatus.DISCOVERED
            )
            
            logger.debug(f"Discovered page: {url} - {title}")
            return page_obj
                
        except TimeoutError:
            logger.warning(f"Timeout loading page: {url}")
            # Create a failed page record for timeout
            return Page(
                website_id=website.id,
                url=url,
                title="Failed: Timeout",
                discovered_from=website.url if depth == 0 else None,
                depth=depth,
                status=PageStatus.DISCOVERY_FAILED,
                error_reason="Page load timeout (20 seconds)"
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
        base_domain: str
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
            # Extract all links using JavaScript
            links = await page.evaluate('''
                () => {
                    const anchors = document.querySelectorAll('a[href]');
                    return Array.from(anchors).map(a => a.href);
                }
            ''')
            
            # Filter and normalize links
            valid_links = set()
            
            for link in links:
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
                
                # Apply path filters
                path = parsed.path
                
                # Skip common non-HTML resources
                if path.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', 
                                 '.zip', '.exe', '.dmg', '.mp4', '.mp3')):
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
            
            logger.debug(f"Extracted {len(valid_links)} valid links from {current_url}")
            return valid_links
            
        except Exception as e:
            logger.error(f"Error extracting links from {current_url}: {e}")
            return set()
    
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


# ScrapingJob class has been moved to scraping_job.py for database-backed implementation