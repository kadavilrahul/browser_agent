#!/usr/bin/env python3
"""
Browser Core Module
Contains core browser functionality, data classes, and basic operations
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import required packages
try:
    from playwright.async_api import async_playwright, Page, Browser, ElementHandle
except ImportError:
    print("ERROR: Playwright not found!")
    print("Please install the required dependencies:")
    print("1. Create a virtual environment: python3 -m venv venv")
    print("2. Activate it: source venv/bin/activate")
    print("3. Install requirements: pip install -r requirements.txt")
    print("4. Install browsers: playwright install")
    print("Or use the setup script: ./run.sh setup")
    exit(1)

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_file = os.getenv('LOG_FILE', 'web_agent.log')

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# Create file handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(log_level)

# Create console handler for errors and warnings
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Data classes for browser state and element information
@dataclass
class BrowserState:
    """Maintains the current state of the browser session"""
    logged_in: bool = False
    current_url: str = ""
    cookies: Dict = field(default_factory=dict)
    local_storage: Dict = field(default_factory=dict)
    session_storage: Dict = field(default_factory=dict)

@dataclass
class ElementInfo:
    """Information about a clickable element on the page"""
    index: int
    tag_name: str
    text: str
    attributes: Dict[str, str] = field(default_factory=dict)
    xpath: str = ""
    is_visible: bool = True
    is_in_viewport: bool = True
    bounding_box: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    def __str__(self):
        """String representation of the element"""
        attrs = " ".join([f'{k}="{v}"' for k, v in self.attributes.items() 
                         if k in ['id', 'class', 'name', 'role', 'type', 'href']])
        return f"[{self.index}] <{self.tag_name} {attrs}>{self.text}</{self.tag_name}>"

@dataclass
class PageAnalysis:
    """Analysis results for a webpage"""
    url: str
    title: str
    timestamp: str
    elements: List[ElementInfo] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "url": self.url,
            "title": self.title,
            "timestamp": self.timestamp,
            "elements": [elem.to_dict() for elem in self.elements]
        }
    
    def save_to_file(self, filename: str):
        """Save analysis results to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Analysis saved to {filename}")
    
    def print_elements(self):
        """Print all clickable elements to console"""
        print(f"\n=== Clickable Elements on {self.url} ===")
        print(f"Page Title: {self.title}")
        print(f"Analysis Time: {self.timestamp}")
        print(f"Total Elements: {len(self.elements)}\n")
        
        for elem in self.elements:
            print(elem)

class BrowserCore:
    """Core browser functionality and management"""
    
    def __init__(self, headless: Optional[bool] = None):
        """Initialize the browser core"""
        if headless is None:
            self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        else:
            self.headless = headless
        
        # Force headless mode if no display available
        if not os.getenv('DISPLAY'):
            self.headless = True
        
        self.browser = None
        self.page = None
        self.state = BrowserState()
        
    async def __aenter__(self):
        """Context manager entry"""
        try:
            self.playwright = await async_playwright().start()
            
            launch_options = {
                'headless': self.headless,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            }

            if not self.headless:
                try:
                    subprocess.check_call(['which', 'xvfb-run'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    logger.info("xvfb-run found. Launching browser with xvfb-run.")
                except subprocess.CalledProcessError:
                    logger.warning("xvfb-run not found. Running in non-headless mode without X server might fail.")
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            return self
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def create_new_context(self):
        """Create a new browser context with custom settings"""
        viewport_width = int(os.getenv('VIEWPORT_WIDTH', '1280'))
        viewport_height = int(os.getenv('VIEWPORT_HEIGHT', '800'))
        
        context = await self.browser.new_context(
            viewport={'width': viewport_width, 'height': viewport_height},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation', 'notifications'],
            java_script_enabled=True
        )
        
        # Add stealth script if automation detection is disabled
        if os.getenv('DISABLE_AUTOMATION_DETECTION', 'true').lower() == 'true':
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Remove automation indicators
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
        
        return context

    async def new_page(self) -> Page:
        """Create a new page with stealth settings"""
        context = await self.create_new_context()
        self.page = await context.new_page()
        
        self.page.on('dialog', lambda dialog: dialog.accept())
        self.page.on('pageerror', lambda error: logger.error(f"Page error: {error}"))
        
        return self.page

    async def navigate(self, url: str, wait_for_network: bool = None):
        """Navigate to a URL with smart waiting strategy"""
        if not self.page:
            await self.new_page()
        
        if wait_for_network is None:
            wait_for_network = os.getenv('WAIT_FOR_NETWORK', 'true').lower() == 'true'
        
        timeout = int(os.getenv('BROWSER_TIMEOUT', '30000'))
        
        try:
            await self.page.goto(
                url,
                wait_until="networkidle" if wait_for_network else "domcontentloaded",
                timeout=timeout
            )
            
            await self.page.wait_for_load_state("domcontentloaded")
            self.state.current_url = self.page.url
            
            # Store cookies and storage data
            self.state.cookies = await self.page.context.cookies()
            self.state.local_storage = await self.page.evaluate("() => Object.assign({}, window.localStorage)")
            self.state.session_storage = await self.page.evaluate("() => Object.assign({}, window.sessionStorage)")
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            raise

    async def take_screenshot(self, path: str):
        """Take a screenshot of the current page"""
        if self.page:
            try:
                quality = int(os.getenv('SCREENSHOT_QUALITY', '90'))
                screenshot_options = {'path': path, 'full_page': True}
                
                # Add quality setting for JPEG files
                if path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
                    screenshot_options['quality'] = quality
                
                await self.page.screenshot(**screenshot_options)
                logger.info(f"Screenshot saved to {path}")
                print(f"Screenshot saved: {path}")
            except Exception as e:
                logger.error(f"Failed to take screenshot: {e}")
        else:
            logger.warning("No page available to take a screenshot.")

    async def execute_javascript(self, js_code: str) -> Any:
        """Execute JavaScript code on the current page"""
        if not self.page:
            return None
        
        try:
            result = await self.page.evaluate(js_code)
            logger.info(f"Executed JavaScript: {js_code}")
            return result
        except Exception as e:
            logger.error(f"Error executing JavaScript: {e}")
            return None

    def generate_filename_from_url(self, url: str, prefix: str = "elements") -> str:
        """Generate a filename with timestamp and short URL name"""
        try:
            from urllib.parse import urlparse
            import re
            
            # Extract domain and path for short name
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '')
            path = parsed_url.path.strip('/').replace('/', '_')
            
            # Create short URL name (max 30 chars)
            if path:
                short_url = f"{domain}_{path}"[:30]
            else:
                short_url = domain[:30]
            
            # Remove invalid filename characters
            short_url = re.sub(r'[<>:"/\\|?*]', '_', short_url)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}_{short_url}.json"
            
            return filename
            
        except Exception as e:
            # Fallback to simple timestamp if URL parsing fails
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{prefix}_{timestamp}.json"

def validate_environment():
    """Validate environment configuration"""
    issues = []
    
    # Check required environment variables
    required_vars = ['HEADLESS', 'LOG_LEVEL', 'LOG_FILE']
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"Missing environment variable: {var}")
    
    # Check numeric values
    try:
        int(os.getenv('BROWSER_TIMEOUT', '30000'))
    except ValueError:
        issues.append("BROWSER_TIMEOUT must be a valid integer")
    
    try:
        int(os.getenv('VIEWPORT_WIDTH', '1280'))
    except ValueError:
        issues.append("VIEWPORT_WIDTH must be a valid integer")
    
    try:
        int(os.getenv('VIEWPORT_HEIGHT', '800'))
    except ValueError:
        issues.append("VIEWPORT_HEIGHT must be a valid integer")
    
    try:
        quality = int(os.getenv('SCREENSHOT_QUALITY', '90'))
        if not 1 <= quality <= 100:
            issues.append("SCREENSHOT_QUALITY must be between 1 and 100")
    except ValueError:
        issues.append("SCREENSHOT_QUALITY must be a valid integer")
    
    if issues:
        logger.warning("Environment validation issues found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
        return False
    
    logger.info("Environment validation passed")
    return True

if __name__ == "__main__":
    # Test the browser core functionality
    async def test_browser_core():
        async with BrowserCore() as browser:
            await browser.navigate("https://example.com")
            await browser.take_screenshot("test_core.png")
            print("Browser core test completed successfully!")
    
    asyncio.run(test_browser_core())