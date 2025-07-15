"""
Browser management for ROVO Browser Agent
"""
import asyncio
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from config import Config

class BrowserManager:
    """Manages browser lifecycle and operations"""
    
    def __init__(self, config: Config):
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def start(self) -> Page:
        """Start browser and return page instance"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser
            browser_type = getattr(self.playwright, self.config.get('browser_type'))
            self.browser = await browser_type.launch(**self.config.get_browser_options())
            
            # Create context
            self.context = await self.browser.new_context(**self.config.get_context_options())
            
            # Create page
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.config.get('page_timeout'))
            
            if self.config.get('verbose'):
                print(f"✅ Browser started: {self.config.get('browser_type')}")
            
            return self.page
            
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            await self.close()
            raise
    
    async def navigate(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            if not self.page:
                raise Exception("Browser not started")
            
            # Add https:// if missing
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            await self.page.goto(url, wait_until='domcontentloaded')
            
            if self.config.get('verbose'):
                print(f"🌐 Navigated to: {url}")
            
            return True
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    async def find_clickable_elements(self) -> List[Dict[str, Any]]:
        """Find all clickable elements on current page"""
        try:
            if not self.page:
                raise Exception("Browser not started")
            
            # Define selectors for clickable elements
            selectors = [
                'a[href]',
                'button',
                'input[type="submit"]',
                'input[type="button"]',
                '[onclick]',
                '[role="button"]'
            ]
            
            elements = []
            for i, selector in enumerate(selectors):
                page_elements = await self.page.query_selector_all(selector)
                
                for j, element in enumerate(page_elements[:10]):  # Limit to 10 per type
                    try:
                        # Get element info
                        tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                        text = await element.evaluate('el => el.textContent || el.value || el.alt || ""')
                        href = await element.evaluate('el => el.href || ""')
                        
                        # Clean text
                        text = text.strip()[:100] if text else "No text"
                        
                        elements.append({
                            'index': len(elements),
                            'tag': tag_name,
                            'text': text,
                            'href': href,
                            'selector': selector,
                            'element': element
                        })
                        
                    except Exception:
                        continue
            
            if self.config.get('verbose'):
                print(f"🔍 Found {len(elements)} clickable elements")
            
            return elements
            
        except Exception as e:
            print(f"❌ Element detection failed: {e}")
            return []
    
    async def click_element(self, element_data: Dict[str, Any]) -> bool:
        """Click an element"""
        try:
            if not self.page:
                raise Exception("Browser not started")
            
            element = element_data.get('element')
            if not element:
                raise Exception("Invalid element data")
            
            await element.click()
            
            if self.config.get('verbose'):
                print(f"👆 Clicked: {element_data.get('text', 'Unknown element')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Click failed: {e}")
            return False
    
    async def take_screenshot(self, filename: str = "screenshot.png") -> bool:
        """Take a screenshot"""
        try:
            if not self.page:
                raise Exception("Browser not started")
            
            await self.page.screenshot(path=filename)
            
            if self.config.get('verbose'):
                print(f"📸 Screenshot saved: {filename}")
            
            return True
            
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return False
    
    async def get_page_info(self) -> Dict[str, str]:
        """Get current page information"""
        try:
            if not self.page:
                return {"error": "Browser not started"}
            
            title = await self.page.title()
            url = self.page.url
            
            return {
                "title": title,
                "url": url,
                "status": "loaded"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            if self.config.get('verbose'):
                print("🔒 Browser closed")
                
        except Exception as e:
            print(f"❌ Cleanup error: {e}")