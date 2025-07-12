"""
Core browser operations for Browser Agent v12_p
Handles browser lifecycle, navigation, and screenshot functionality
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from config import Config

class BrowserManager:
    """Manages browser lifecycle and core operations"""
    
    def __init__(self, config: Config):
        """Initialize browser manager with configuration"""
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.current_url: Optional[str] = None
        
        # Ensure output directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories"""
        screenshot_dir = self.config.get('screenshot_dir')
        output_dir = self.config.get('output_dir')
        
        for directory in [screenshot_dir, output_dir]:
            os.makedirs(directory, exist_ok=True)
    
    async def start(self) -> None:
        """Start browser and create context"""
        if self.browser:
            return
        
        self.playwright = await async_playwright().start()
        browser_type = getattr(self.playwright, self.config.get('browser_type'))
        
        self.browser = await browser_type.launch(**self.config.get_browser_options())
        self.context = await self.browser.new_context(**self.config.get_context_options())
        self.page = await self.context.new_page()
        
        # Set timeouts
        self.page.set_default_timeout(self.config.get('element_timeout'))
        self.page.set_default_navigation_timeout(self.config.get('navigation_timeout'))
        
        if self.config.get('verbose'):
            print(f"Browser started: {self.config.get('browser_type')}")
    
    async def stop(self) -> None:
        """Stop browser and cleanup resources"""
        if self.page:
            await self.page.close()
            self.page = None
        
        if self.context:
            await self.context.close()
            self.context = None
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        
        if self.config.get('verbose'):
            print("Browser stopped")
    
    async def navigate(self, url: str) -> bool:
        """Navigate to URL with smart handling"""
        if not self.page:
            await self.start()
        
        # URL validation and correction
        url = self._validate_url(url)
        
        try:
            response = await self.page.goto(url, **self.config.get_page_options())
            
            if response and response.status >= 400:
                print(f"Warning: HTTP {response.status} for {url}")
                return False
            
            # Wait for page to be ready
            await self.page.wait_for_load_state('domcontentloaded')
            
            self.current_url = self.page.url
            
            if self.config.get('verbose'):
                print(f"Navigated to: {self.current_url}")
            
            # Auto screenshot if enabled
            if self.config.get('auto_screenshot'):
                await self.screenshot()
            
            return True
            
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
    
    def _validate_url(self, url: str) -> str:
        """Validate and fix URL format"""
        if not url:
            return self.config.get('default_url')
        
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            if '.' in url:
                url = f'https://{url}'
            else:
                return self.config.get('default_url')
        
        return url
    
    async def screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """Take screenshot of current page"""
        if not self.page:
            print("No page available for screenshot")
            return None
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                domain = self._get_domain_from_url(self.current_url or "unknown")
                filename = f"screenshot_{domain}_{timestamp}.png"
            
            filepath = os.path.join(self.config.get('screenshot_dir'), filename)
            
            screenshot_options = {
                'path': filepath,
                'full_page': True
            }
            
            # Only add quality for JPEG/JPG files
            if filepath.lower().endswith(('.jpg', '.jpeg')):
                screenshot_options['quality'] = self.config.get('screenshot_quality')
            
            await self.page.screenshot(**screenshot_options)
            
            if self.config.get('verbose'):
                print(f"Screenshot saved: {filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return None
    
    def _get_domain_from_url(self, url: str) -> str:
        """Extract domain from URL for filename"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain.replace('.', '_') if domain else "unknown"
        except:
            return "unknown"
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page information"""
        if not self.page:
            return {}
        
        try:
            return {
                'url': self.page.url,
                'title': await self.page.title(),
                'viewport': self.page.viewport_size,
                'ready_state': await self.page.evaluate('document.readyState'),
            }
        except Exception as e:
            if self.config.get('verbose'):
                print(f"Failed to get page info: {e}")
            return {'url': self.current_url or 'unknown'}
    
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Wait for element selector to appear"""
        if not self.page:
            return False
        
        try:
            timeout = timeout or self.config.get('element_selector_timeout')
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False
    
    async def evaluate_script(self, script: str) -> Any:
        """Execute JavaScript in page context"""
        if not self.page:
            return None
        
        try:
            return await self.page.evaluate(script)
        except Exception as e:
            if self.config.get('verbose'):
                print(f"Script evaluation failed: {e}")
            return None
    
    def is_ready(self) -> bool:
        """Check if browser is ready for operations"""
        return self.page is not None
    
    def get_current_url(self) -> Optional[str]:
        """Get current page URL"""
        return self.current_url