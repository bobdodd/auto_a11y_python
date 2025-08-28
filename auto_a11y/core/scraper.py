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

from auto_a11y.models import Page, PageStatus, Website
from auto_a11y.core.database import Database
from auto_a11y.core.browser_manager import BrowserManager

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
        progress_callback: Optional[callable] = None
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
        
        # Reset discovery state
        self.discovered_urls.clear()
        self.queued_urls.clear()
        
        # Check browser availability first
        try:
            if not await self.browser_manager.is_running():
                await self.browser_manager.start()
        except Exception as e:
            error_msg = f"Failed to start browser: {e}. Make sure Chromium is installed (run: python run.py --download-browser)"
            logger.error(error_msg)
            if progress_callback:
                await progress_callback({
                    'status': 'failed',
                    'error': error_msg
                })
            raise RuntimeError(error_msg)
        
        # Parse base URL
        base_url = self._normalize_url(website.url)
        base_domain = urlparse(base_url).netloc
        
        # Initialize queue with starting URL
        self.queued_urls.add(base_url)
        
        # Track discovered pages
        discovered_pages = []
        
        # Start browser
        await self.browser_manager.start()
        
        try:
            depth = 0
            while self.queued_urls and depth <= website.scraping_config.max_depth:
                # Get URLs at current depth
                current_batch = list(self.queued_urls)
                self.queued_urls.clear()
                
                logger.info(f"Processing depth {depth} with {len(current_batch)} URLs")
                
                for url in current_batch:
                    # Check if we've hit page limit
                    if len(discovered_pages) >= website.scraping_config.max_pages:
                        logger.info(f"Reached max pages limit: {website.scraping_config.max_pages}")
                        break
                    
                    # Skip if already discovered
                    if url in self.discovered_urls:
                        continue
                    
                    # Check robots.txt
                    if website.scraping_config.respect_robots:
                        if not await self._can_fetch(url):
                            logger.debug(f"Skipping {url} due to robots.txt")
                            continue
                    
                    # Discover page
                    page = await self._discover_page(
                        url=url,
                        website=website,
                        depth=depth,
                        base_domain=base_domain
                    )
                    
                    if page:
                        discovered_pages.append(page)
                        self.discovered_urls.add(url)
                        
                        # Update progress
                        if progress_callback:
                            await progress_callback({
                                'pages_found': len(discovered_pages),
                                'current_depth': depth,
                                'queue_size': len(self.queued_urls),
                                'current_url': url
                            })
                    
                    # Respect rate limiting
                    await asyncio.sleep(website.scraping_config.request_delay)
                
                depth += 1
            
            # Save discovered pages to database
            if discovered_pages:
                saved_count = self.db.bulk_create_pages(discovered_pages)
                logger.info(f"Saved {saved_count} new pages to database")
                
                # Update website last_scraped
                website.last_scraped = datetime.now()
                self.db.update_website(website)
            
        finally:
            await self.browser_manager.stop()
        
        logger.info(f"Discovery complete. Found {len(discovered_pages)} pages")
        return discovered_pages
    
    async def _discover_page(
        self,
        url: str,
        website: Website,
        depth: int,
        base_domain: str
    ) -> Optional[Page]:
        """
        Discover a single page and extract links
        
        Args:
            url: URL to discover
            website: Website object
            depth: Current crawl depth
            base_domain: Base domain for filtering
            
        Returns:
            Page object or None if failed
        """
        try:
            async with self.browser_manager.get_page() as page:
                # Navigate to URL
                response = await self.browser_manager.goto(
                    page=page,
                    url=url,
                    wait_until='networkidle2',
                    timeout=30000
                )
                
                if not response:
                    logger.warning(f"Failed to load page: {url}")
                    return None
                
                # Get page title
                title = await self.browser_manager.get_page_title(page)
                
                # Extract links if not at max depth
                if depth < website.scraping_config.max_depth:
                    links = await self._extract_links(page, url, website, base_domain)
                    self.queued_urls.update(links)
                
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
        except Exception as e:
            logger.error(f"Error discovering page {url}: {e}")
        
        return None
    
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
            
            # Remove trailing slash from path (except root)
            path = parsed.path
            if path != '/' and path.endswith('/'):
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
                # Fetch and parse robots.txt
                rp = RobotFileParser()
                rp.set_url(robots_url)
                
                # Use custom fetch to handle async
                async with self.browser_manager.get_page() as page:
                    try:
                        await page.goto(robots_url, {'waitUntil': 'domcontentloaded', 'timeout': 5000})
                        content = await page.content()
                        
                        # Parse robots.txt content
                        if 'text/plain' in content or 'User-agent' in content:
                            rp.parse(content.split('\n'))
                        else:
                            # No valid robots.txt, allow all
                            rp.parse(['User-agent: *', 'Allow: /'])
                    except:
                        # Error fetching robots.txt, assume allow all
                        rp.parse(['User-agent: *', 'Allow: /'])
                
                self.robots_cache[robots_url] = rp
            
            # Check if URL is fetchable
            return self.robots_cache[robots_url].can_fetch('*', url)
            
        except Exception as e:
            logger.debug(f"Error checking robots.txt for {url}: {e}")
            # Default to allow on error
            return True


class ScrapingJob:
    """Represents a scraping job"""
    
    def __init__(self, website_id: str, job_id: str):
        """
        Initialize scraping job
        
        Args:
            website_id: Website ID
            job_id: Unique job ID
        """
        self.website_id = website_id
        self.job_id = job_id
        self.status = 'pending'
        self.progress = {
            'pages_found': 0,
            'current_depth': 0,
            'queue_size': 0,
            'current_url': None,
            'started_at': None,
            'completed_at': None,
            'error': None
        }
    
    async def run(self, database: Database, browser_config: Dict[str, Any]):
        """
        Run the scraping job
        
        Args:
            database: Database connection
            browser_config: Browser configuration
        """
        self.status = 'running'
        self.progress['started_at'] = datetime.now()
        
        try:
            # Get website
            website = database.get_website(self.website_id)
            if not website:
                raise ValueError(f"Website {self.website_id} not found")
            
            # Create scraper
            scraper = ScrapingEngine(database, browser_config)
            
            # Run discovery with progress callback
            pages = await scraper.discover_website(
                website=website,
                progress_callback=self._update_progress
            )
            
            self.status = 'completed'
            self.progress['completed_at'] = datetime.now()
            self.progress['pages_found'] = len(pages)
            
        except Exception as e:
            logger.error(f"Scraping job {self.job_id} failed: {e}")
            self.status = 'failed'
            self.progress['error'] = str(e)
            self.progress['completed_at'] = datetime.now()
    
    async def _update_progress(self, progress: dict):
        """Update job progress"""
        self.progress.update(progress)