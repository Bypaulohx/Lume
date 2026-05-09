"""
Browser Engine for Lume V2.0
Handles dynamic website crawling using Playwright
"""

import asyncio
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from lume.core import setup_logger
from lume.utils.url_utils import is_internal_link, extract_domain
from lume.utils.errors import PlaywrightError


@dataclass
class FormField:
    """Information about form field"""
    name: str
    field_type: str
    value: Optional[str] = None
    required: bool = False


@dataclass
class FormInfo:
    """Information about discovered form"""
    action: str
    method: str
    fields: List[FormField]
    enctype: str


@dataclass
class PageInfo:
    """Information about discovered page"""
    url: str
    title: str
    status_code: int
    content: str
    forms: List[FormInfo]
    links: Set[str]
    scripts: List[str]
    inputs: List[str]


class BrowserEngine:
    """
    Dynamic browser automation using Playwright for:
    - JavaScript rendering
    - Form discovery
    - Hidden endpoint detection
    - Dynamic content analysis
    """
    
    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        timeout: int = 30000,
    ):
        """
        Initialize Browser Engine.
        
        Args:
            browser_type: Browser to use (chromium, firefox, webkit)
            headless: Whether to run headless
            timeout: Page timeout in milliseconds
        """
        self.logger = setup_logger(__name__)
        self.browser_type = browser_type
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.context = None
    
    async def launch(self):
        """Launch browser"""
        try:
            from playwright.async_api import async_playwright
            
            self.logger.info(f"Launching {self.browser_type} browser (headless={self.headless})")
            
            self.playwright = await async_playwright().start()
            browser_obj = getattr(self.playwright, self.browser_type)
            self.browser = await browser_obj.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            
        except Exception as e:
            self.logger.error(f"Failed to launch browser: {e}")
            raise PlaywrightError(f"Browser launch failed: {e}")
    
    async def close(self):
        """Close browser"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
    
    async def fetch_page(self, url: str) -> PageInfo:
        """
        Fetch and analyze a page using dynamic browser.
        
        Args:
            url: URL to fetch
            
        Returns:
            PageInfo with page content and analysis
            
        Raises:
            PlaywrightError: If page fetch fails
        """
        try:
            if not self.browser:
                await self.launch()
            
            page = await self.context.new_page()
            self.logger.info(f"Fetching: {url}")
            
            try:
                response = await page.goto(url, timeout=self.timeout)
                status_code = response.status if response else 0
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout fetching {url}")
                status_code = 0
            
            # Wait for JavaScript to render
            await asyncio.sleep(1)  # Basic wait
            
            # Get content
            content = await page.content()
            title = await page.title()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")
            
            # Extract forms
            forms = await self._extract_forms(page, soup, url)
            
            # Extract links
            links = self._extract_links(soup, url)
            
            # Extract scripts
            scripts = [script.get("src", "") for script in soup.find_all("script") if script.get("src")]
            
            # Extract inputs
            inputs = [
                f"{inp.get('type', 'text')}: {inp.get('name', 'unnamed')}"
                for inp in soup.find_all("input")
            ]
            
            await page.close()
            
            return PageInfo(
                url=url,
                title=title,
                status_code=status_code,
                content=content,
                forms=forms,
                links=links,
                scripts=scripts,
                inputs=inputs,
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching page {url}: {e}")
            raise PlaywrightError(f"Failed to fetch page: {e}")
    
    async def _extract_forms(self, page, soup, url: str) -> List[FormInfo]:
        """Extract form information from page"""
        forms = []
        
        for form in soup.find_all("form"):
            action = form.get("action", "")
            action = urljoin(url, action) if action else url
            method = form.get("method", "GET").upper()
            enctype = form.get("enctype", "application/x-www-form-urlencoded")
            
            fields = []
            for field in form.find_all(["input", "textarea", "select"]):
                field_info = FormField(
                    name=field.get("name", "unnamed"),
                    field_type=field.get("type", field.name),
                    value=field.get("value"),
                    required="required" in field.attrs,
                )
                fields.append(field_info)
            
            forms.append(FormInfo(
                action=action,
                method=method,
                fields=fields,
                enctype=enctype,
            ))
        
        return forms
    
    def _extract_links(self, soup, base_url: str) -> Set[str]:
        """Extract internal links from page"""
        links = set()
        
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if not href or href.startswith(("#", "javascript:", "mailto:")):
                continue
            
            full_url = urljoin(base_url, href)
            
            # Only internal links
            if is_internal_link(base_url, full_url):
                links.add(full_url)
        
        return links
    
    async def crawl(
        self,
        start_url: str,
        max_pages: int = 50,
        max_depth: int = 3,
    ) -> Dict[str, PageInfo]:
        """
        Crawl website recursively.
        
        Args:
            start_url: Starting URL
            max_pages: Maximum pages to crawl
            max_depth: Maximum crawl depth
            
        Returns:
            Dictionary mapping URLs to PageInfo
        """
        try:
            if not self.browser:
                await self.launch()
            
            crawled = {}
            to_crawl = [(start_url, 0)]
            visited = set()
            
            while to_crawl and len(crawled) < max_pages:
                url, depth = to_crawl.pop(0)
                
                if url in visited or depth > max_depth:
                    continue
                
                visited.add(url)
                
                try:
                    page_info = await self.fetch_page(url)
                    crawled[url] = page_info
                    
                    # Add discovered links to queue
                    for link in page_info.links:
                        if link not in visited:
                            to_crawl.append((link, depth + 1))
                    
                except Exception as e:
                    self.logger.debug(f"Error crawling {url}: {e}")
            
            self.logger.info(f"Crawled {len(crawled)} pages")
            return crawled
            
        except Exception as e:
            self.logger.error(f"Crawl failed: {e}")
            raise PlaywrightError(f"Crawl operation failed: {e}")
