#!/usr/bin/env python3
"""
Unified Web Browsing Agent

This script combines all web browsing functionalities:
1. Automated login to websites
2. Web scraping and element identification  
3. Interactive browser control
4. Real-time navigation and interaction

Usage:
    python unified_web_agent.py                    # Interactive mode menu
    python unified_web_agent.py --mode login       # Login mode
    python unified_web_agent.py --mode scraper     # Web scraper mode
    python unified_web_agent.py --mode interactive # Interactive browser mode
    python unified_web_agent.py --mode navigate --url <url>  # Quick navigation
"""

import asyncio
import argparse
import json
import logging
import os
import sys
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
    sys.exit(1)

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

# JavaScript for identifying clickable elements
JS_GET_CLICKABLE_ELEMENTS = """
() => {
    // Helper function to check if element is visible
    function isVisible(element) {
        if (!element.getBoundingClientRect) return false;
        const rect = element.getBoundingClientRect();
        return !!(rect.top || rect.bottom || rect.width || rect.height) && 
               window.getComputedStyle(element).visibility !== 'hidden' &&
               window.getComputedStyle(element).display !== 'none' &&
               window.getComputedStyle(element).opacity !== '0';
    }
    
    // Helper function to check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= -100 &&
            rect.left >= -100 &&
            rect.bottom <= (window.innerHeight + 100) &&
            rect.right <= (window.innerWidth + 100)
        );
    }
    
    // Helper function to check if element is interactive
    function isInteractive(element) {
        const tagName = element.tagName.toLowerCase();
        
        // Common interactive elements
        const interactiveTags = ['a', 'button', 'input', 'select', 'textarea', 'details', 'summary'];
        if (interactiveTags.includes(tagName)) return true;
        
        // Check for interactive roles
        const role = element.getAttribute('role');
        const interactiveRoles = ['button', 'link', 'checkbox', 'radio', 'tab', 'menuitem'];
        if (role && interactiveRoles.includes(role)) return true;
        
        // Check for event handlers
        if (element.onclick || 
            element.getAttribute('onclick') || 
            element.getAttribute('ng-click') ||
            element.getAttribute('@click')) return true;
        
        // Check for tabindex
        if (element.getAttribute('tabindex') && element.getAttribute('tabindex') !== '-1') return true;
        
        // Check for contenteditable
        if (element.getAttribute('contenteditable') === 'true') return true;
        
        return false;
    }
    
    // Helper function to get all text from an element
    function getElementText(element) {
        // For input elements, get value or placeholder
        if (element.tagName.toLowerCase() === 'input') {
            return element.value || element.placeholder || '';
        }
        
        // For other elements, get innerText or textContent
        return element.innerText || element.textContent || '';
    }
    
    // Helper function to get XPath
    function getXPath(element) {
        if (!element) return '';
        
        // Use id if available
        if (element.id) {
            return `//*[@id="${element.id}"]`;
        }
        
        // Otherwise build path
        const parts = [];
        while (element && element.nodeType === Node.ELEMENT_NODE) {
            let idx = 0;
            let sibling = element.previousSibling;
            while (sibling) {
                if (sibling.nodeType === Node.ELEMENT_NODE && 
                    sibling.tagName === element.tagName) {
                    idx++;
                }
                sibling = sibling.previousSibling;
            }
            
            const tagName = element.tagName.toLowerCase();
            const pathIndex = idx ? `[${idx + 1}]` : '';
            parts.unshift(`${tagName}${pathIndex}`);
            
            element = element.parentNode;
        }
        
        return '/' + parts.join('/');
    }
    
    // Find all clickable elements
    const clickableElements = [];
    let index = 0;
    
    // Function to process elements recursively
    function processElement(element) {
        if (!element || !isVisible(element)) return;
        
        // Check if element is interactive
        if (isInteractive(element)) {
            // Get element properties
            const tagName = element.tagName.toLowerCase();
            const text = getElementText(element).trim();
            const isInView = isInViewport(element);
            const rect = element.getBoundingClientRect();
            
            // Get attributes
            const attributes = {};
            for (const attr of element.attributes) {
                attributes[attr.name] = attr.value;
            }
            
            // Add to results
            clickableElements.push({
                index: index++,
                tagName,
                text: text.substring(0, 100), // Limit text length
                attributes,
                xpath: getXPath(element),
                isVisible: true,
                isInViewport: isInView,
                boundingBox: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    right: rect.right,
                    bottom: rect.bottom,
                    left: rect.left
                }
            });
        }
        
        // Process children
        for (const child of element.children) {
            processElement(child);
        }
    }
    
    // Start processing from body
    processElement(document.body);
    
    return clickableElements;
}
"""

class UnifiedWebAgent:
    """Unified web browsing agent with all functionalities"""
    
    def __init__(self, headless: Optional[bool] = None):
        """Initialize the agent"""
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

    async def find_clickable_elements(self) -> List[ElementInfo]:
        """Find all clickable elements on the current page"""
        if not self.page:
            raise ValueError("No page is open. Call navigate() first.")
        
        elements_data = await self.page.evaluate(JS_GET_CLICKABLE_ELEMENTS)
        
        elements = []
        for data in elements_data:
            element = ElementInfo(
                index=data['index'],
                tag_name=data['tagName'],
                text=data['text'],
                attributes=data['attributes'],
                xpath=data['xpath'],
                is_visible=data['isVisible'],
                is_in_viewport=data['isInViewport'],
                bounding_box=data['boundingBox']
            )
            elements.append(element)
        
        logger.info(f"Found {len(elements)} clickable elements")
        return elements

    async def analyze_page(self, url: str) -> PageAnalysis:
        """Analyze a webpage to find clickable elements"""
        await self.navigate(url)
        
        title = await self.page.title()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        elements = await self.find_clickable_elements()
        
        analysis = PageAnalysis(
            url=url,
            title=title,
            timestamp=timestamp,
            elements=elements
        )
        
        return analysis

    # Login functionality methods
    async def login_google(self, email: str, password: str) -> bool:
        """Login to Google account"""
        try:
            await self.navigate("https://accounts.google.com/signin/v2/identifier")
            await asyncio.sleep(2)
            
            # Enter email
            email_selector = 'input[type="email"]'
            await self.page.wait_for_selector(email_selector, state="visible", timeout=10000)
            await self.page.fill(email_selector, email)
            await asyncio.sleep(1)
            
            # Click Next
            next_button = await self.page.query_selector('button:has-text("Next")')
            if next_button:
                await next_button.click()
            else:
                await self.page.keyboard.press('Enter')
            
            # Enter password
            await asyncio.sleep(2)
            password_selector = 'input[type="password"]'
            await self.page.wait_for_selector(password_selector, state="visible", timeout=10000)
            await self.page.fill(password_selector, password)
            await asyncio.sleep(1)
            
            # Click Next
            next_button = await self.page.query_selector('button:has-text("Next")')
            if next_button:
                await next_button.click()
            else:
                await self.page.keyboard.press('Enter')
            
            await asyncio.sleep(5)
            
            # Check success
            success_indicators = [
                'a[aria-label="Google Account"]',
                'img[alt="Google Account"]',
                'a[href*="myaccount.google.com"]',
                'div[data-email]'
            ]
            
            for indicator in success_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=5000)
                    self.state.logged_in = True
                    return True
                except:
                    continue
            
            return False
                
        except Exception as e:
            logger.error(f"Google login error: {e}")
            return False

    async def login_github(self, username: str, password: str) -> bool:
        """Login to GitHub account"""
        try:
            await self.navigate("https://github.com/login")
            await asyncio.sleep(2)
            
            await self.page.fill('input[name="login"]', username)
            await asyncio.sleep(1)
            
            await self.page.fill('input[name="password"]', password)
            await asyncio.sleep(1)
            
            await self.page.click('input[name="commit"]')
            await asyncio.sleep(3)
            
            try:
                await self.page.wait_for_selector('.avatar', timeout=5000)
                self.state.logged_in = True
                return True
            except:
                return False
                
        except Exception as e:
            logger.error(f"GitHub login error: {e}")
            return False

    async def login_to_website(self, url: str, username: str, password: str) -> bool:
        """Universal login function for any website"""
        try:
            logger.info(f"Attempting to login to {url}")
            
            # Special handling for common sites
            if 'github.com' in url:
                return await self.login_github(username, password)
            elif 'google.com' in url or 'gmail.com' in url:
                return await self.login_google(username, password)
            
            await self.navigate(url)
            await asyncio.sleep(2)

            # Common selectors for login forms
            common_selectors = {
                'username': [
                    'input[type="email"]', 'input[type="text"]', 'input[name="username"]',
                    'input[name="email"]', 'input[id="email"]', 'input[id="username"]', 'input[name="login"]'
                ],
                'password': ['input[type="password"]', 'input[name="password"]', 'input[id="password"]'],
                'submit': [
                    'button[type="submit"]', 'input[type="submit"]', 'button:has-text("Sign in")',
                    'button:has-text("Log in")', 'button:has-text("Login")', 'input[name="commit"]'
                ]
            }

            # Find and fill username field
            username_field = None
            for selector in common_selectors['username']:
                try:
                    username_field = await self.page.wait_for_selector(selector, timeout=2000)
                    if username_field:
                        break
                except:
                    continue

            if not username_field:
                logger.error("Could not find username field")
                return False

            await username_field.fill(username)
            await asyncio.sleep(1)

            # Find and fill password field
            password_field = None
            for selector in common_selectors['password']:
                try:
                    password_field = await self.page.wait_for_selector(selector, timeout=2000)
                    if password_field:
                        break
                except:
                    continue

            if not password_field:
                logger.error("Could not find password field")
                return False

            await password_field.fill(password)
            await asyncio.sleep(1)

            # Find and click submit button
            submit_button = None
            for selector in common_selectors['submit']:
                try:
                    submit_button = await self.page.wait_for_selector(selector, timeout=2000)
                    if submit_button:
                        break
                except:
                    continue

            if submit_button:
                await submit_button.click()
            else:
                await password_field.press('Enter')

            await asyncio.sleep(3)

            # Check login success
            success_indicators = [
                '.avatar', '.user-avatar', '.profile-pic', 'a[href*="logout"]',
                'a[href*="signout"]', '.logout-button', '.user-menu', '.dashboard'
            ]

            # Check URL change
            current_url = self.page.url
            if current_url != url and 'login' not in current_url.lower():
                self.state.logged_in = True
                return True

            # Check for success indicators
            for selector in success_indicators:
                try:
                    await self.page.wait_for_selector(selector, timeout=2000)
                    self.state.logged_in = True
                    return True
                except:
                    continue

            return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    # Session management methods
    async def save_session(self, filename: str):
        """Save current session state to file"""
        session_data = {
            'cookies': self.state.cookies,
            'localStorage': self.state.local_storage,
            'sessionStorage': self.state.session_storage,
            'url': self.state.current_url,
            'logged_in': self.state.logged_in
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f)
        logger.info(f"Session saved to {filename}")

    async def load_session(self, filename: str):
        """Load session state from file"""
        with open(filename) as f:
            session_data = json.load(f)
        
        context = await self.create_new_context()
        await context.add_cookies(session_data['cookies'])
        
        self.page = await context.new_page()
        
        await self.page.evaluate("""
            storage => {
                for (let key in storage.localStorage) {
                    window.localStorage.setItem(key, storage.localStorage[key]);
                }
                for (let key in storage.sessionStorage) {
                    window.sessionStorage.setItem(key, storage.sessionStorage[key]);
                }
            }
        """, session_data)
        
        self.state.cookies = session_data['cookies']
        self.state.local_storage = session_data['localStorage']
        self.state.session_storage = session_data['sessionStorage']
        self.state.current_url = session_data['url']
        self.state.logged_in = session_data['logged_in']
        
        await self.navigate(self.state.current_url)
        logger.info(f"Session loaded from {filename}")

    # Interactive browser methods
    async def click_element(self, element_index: int, elements: List[ElementInfo]) -> bool:
        """Click on a specific element by index"""
        if not self.page:
            return False
        
        element = next((e for e in elements if e.index == element_index), None)
        if not element:
            logger.warning(f"Element with index {element_index} not found")
            return False
        
        try:
            if element.xpath:
                await self.page.click(f"xpath={element.xpath}")
                logger.info(f"Clicked element {element_index} using XPath")
                return True
            
            if 'id' in element.attributes:
                await self.page.click(f"#{element.attributes['id']}")
                logger.info(f"Clicked element {element_index} using ID selector")
                return True
            
            if element.bounding_box:
                x = element.bounding_box['x'] + element.bounding_box['width'] / 2
                y = element.bounding_box['y'] + element.bounding_box['height'] / 2
                await self.page.mouse.click(x, y)
                logger.info(f"Clicked element {element_index} using coordinates")
                return True
            
            logger.warning(f"Could not click element {element_index}")
            return False
        except Exception as e:
            logger.error(f"Error clicking element {element_index}: {e}")
            return False

    async def type_in_element(self, selector: str, text: str) -> bool:
        """Type text in an element specified by selector"""
        if not self.page:
            return False
        
        try:
            await self.page.fill(selector, text)
            logger.info(f"Typed '{text}' in element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Error typing in element {selector}: {e}")
            return False

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

class InteractiveBrowserController:
    """Interactive browser controller for real-time commands"""
    
    def __init__(self, agent: UnifiedWebAgent):
        self.agent = agent
        self.running = True
        self.current_elements = []
        
    async def start_interactive_session(self):
        """Start the interactive browser session"""
        print("BROWSER READY")
        await self.interactive_loop()
        
    async def interactive_loop(self):
        """Main interactive command loop with simplified menu"""
        while self.running:
            try:
                await self.show_main_menu()
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                print("\nInput ended, exiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                logger.error(f"Interactive loop error: {e}")
        self.running = False

    async def show_main_menu(self):
        """Show simplified main menu with max 3 options"""
        print("\n" + "="*40)
        print("WEB BROWSING AGENT")
        print("="*40)
        print("1. Browse & Screenshot")
        print("2. Find & Click Elements") 
        print("3. Exit")
        print("="*40)
        
        # Show status
        if hasattr(self.agent, 'page') and self.agent.page:
            print(f"Current: {self.agent.state.current_url}")
        if self.current_elements:
            print(f"Elements: {len(self.current_elements)} loaded")
        print()
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            await self.browse_menu()
        elif choice == "2":
            await self.element_menu()
        elif choice == "3":
            print("Goodbye!")
            self.running = False
        else:
            print("Invalid choice. Please try again.")

    async def browse_menu(self):
        """Website browsing and screenshot submenu"""
        print("\n" + "="*40)
        print("BROWSE & SCREENSHOT")
        print("="*40)
        print("1. Go to website")
        print("2. Take screenshot")
        print("3. Back to main menu")
        print("="*40)
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            await self.handle_navigation()
        elif choice == "2":
            await self.handle_screenshot()
        elif choice == "3":
            return
        else:
            print("Invalid choice.")

    async def element_menu(self):
        """Find and click elements submenu"""
        if not self.agent.page:
            print("ERROR: No website loaded. Go to a website first.")
            return
            
        print("\n" + "="*40)
        print("FIND & CLICK ELEMENTS")
        print("="*40)
        print("1. Find clickable elements")
        print("2. Click element by number")
        print("3. View element details")
        print("="*40)
        
        if self.current_elements:
            print(f"Elements loaded: {len(self.current_elements)}")
        print()
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            await self.handle_find_elements()
        elif choice == "2":
            await self.handle_click_element()
        elif choice == "3":
            await self.handle_view_elements()
        else:
            print("Invalid choice.")


    async def handle_navigation(self):
        """Handle website navigation"""
        url = input("Enter URL: ").strip()
        if not url:
            print("ERROR: URL cannot be empty")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            print(f"Navigating to {url}...")
            await self.agent.navigate(url)
            print(f"SUCCESS: Navigated to {url}")
            # Clear previous elements since we're on a new page
            self.current_elements = []
        except Exception as e:
            print(f"ERROR: Navigation failed: {e}")

    async def handle_find_elements(self):
        """Handle finding clickable elements"""
        if not self.agent.page:
            print("ERROR: No page loaded. Please navigate to a website first.")
            return
        
        try:
            print("Searching for clickable elements...")
            self.current_elements = await self.agent.find_clickable_elements()
            print(f"SUCCESS: Found {len(self.current_elements)} clickable elements")
            
            # Auto-save elements to file with timestamp and short URL
            if self.current_elements:
                await self.auto_save_elements()
                
                print("\nFirst 10 elements (use option 3 to see all details):")
                for i, elem in enumerate(self.current_elements[:10]):
                    text_preview = elem.text[:60] + "..." if len(elem.text) > 60 else elem.text
                    tag_info = f"<{elem.tag_name}>"
                    if 'id' in elem.attributes:
                        tag_info += f" id='{elem.attributes['id']}'"
                    if 'class' in elem.attributes:
                        class_preview = elem.attributes['class'][:30] + "..." if len(elem.attributes['class']) > 30 else elem.attributes['class']
                        tag_info += f" class='{class_preview}'"
                    print(f"  [{elem.index}] {tag_info} - {text_preview}")
                
                if len(self.current_elements) > 10:
                    print(f"  ... and {len(self.current_elements) - 10} more elements")
                print("\nTIP: Use option 4 to click an element by its index number")
            else:
                print("INFO: No clickable elements found on this page")
                
        except Exception as e:
            print(f"ERROR: Failed to find elements: {e}")

    async def auto_save_elements(self):
        """Automatically save elements with timestamp and short URL name"""
        try:
            # Generate filename using utility function
            current_url = self.agent.state.current_url
            filename = self.agent.generate_filename_from_url(current_url, "elements")
            
            # Create analysis object and save
            analysis = PageAnalysis(
                url=current_url,
                title=await self.agent.page.title() if self.agent.page else "Unknown",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                elements=self.current_elements
            )
            
            analysis.save_to_file(filename)
            print(f"AUTO-SAVED: Elements saved to {filename}")
            
        except Exception as e:
            print(f"WARNING: Auto-save failed: {e}")

    async def handle_view_elements(self):
        """Handle viewing detailed element information"""
        if not self.current_elements:
            print("ERROR: No elements loaded. Use option 2 to find elements first.")
            return
        
        print(f"\nDetailed view of all {len(self.current_elements)} elements:")
        print("="*80)
        
        for elem in self.current_elements:
            print(f"\n[{elem.index}] Element Details:")
            print(f"  Tag: <{elem.tag_name}>")
            print(f"  Text: {elem.text}")
            print(f"  Visible: {elem.is_visible}")
            print(f"  In Viewport: {elem.is_in_viewport}")
            
            if elem.attributes:
                print("  Attributes:")
                for key, value in elem.attributes.items():
                    if key in ['id', 'class', 'name', 'href', 'type', 'role', 'aria-label']:
                        value_preview = value[:50] + "..." if len(value) > 50 else value
                        print(f"    {key}: {value_preview}")
            
            if elem.xpath:
                xpath_preview = elem.xpath[:70] + "..." if len(elem.xpath) > 70 else elem.xpath
                print(f"  XPath: {xpath_preview}")
            
            if elem.bounding_box:
                bb = elem.bounding_box
                print(f"  Position: ({bb['x']:.0f}, {bb['y']:.0f}) Size: {bb['width']:.0f}x{bb['height']:.0f}")
            
            print("-" * 80)

    async def handle_click_element(self):
        """Handle clicking an element"""
        if not self.current_elements:
            print("ERROR: No elements loaded. Use option 2 to find elements first.")
            return
        
        print(f"Available elements (0-{len(self.current_elements)-1}):")
        for i, elem in enumerate(self.current_elements[:20]):  # Show first 20
            text_preview = elem.text[:50] + "..." if len(elem.text) > 50 else elem.text
            print(f"  [{elem.index}] <{elem.tag_name}> - {text_preview}")
        
        if len(self.current_elements) > 20:
            print(f"  ... and {len(self.current_elements) - 20} more (use option 3 to see all)")
        
        try:
            index_input = input("\nEnter element index to click (or 'cancel'): ").strip()
            if index_input.lower() == 'cancel':
                return
            
            element_index = int(index_input)
            
            if element_index < 0 or element_index >= len(self.current_elements):
                print(f"ERROR: Invalid index. Please enter a number between 0 and {len(self.current_elements)-1}")
                return
            
            element = self.current_elements[element_index]
            print(f"Clicking element [{element_index}]: <{element.tag_name}> - {element.text[:50]}")
            
            success = await self.agent.click_element(element_index, self.current_elements)
            if success:
                print("SUCCESS: Element clicked successfully!")
                # Wait a moment for page changes
                await asyncio.sleep(2)
                print("INFO: Page may have changed. You might want to find elements again.")
            else:
                print("ERROR: Failed to click element")
                
        except ValueError:
            print("ERROR: Invalid input. Please enter a valid number.")
        except Exception as e:
            print(f"ERROR: Error clicking element: {e}")

    async def handle_type_text(self):
        """Handle typing text in an element"""
        if not self.agent.page:
            print("ERROR: No page loaded. Please navigate to a website first.")
            return
        
        print("Type text in element")
        selector = input("Enter CSS selector (e.g., '#username', '.search-box'): ").strip()
        if not selector:
            print("ERROR: Selector cannot be empty")
            return
        
        text = input("Enter text to type: ").strip()
        if not text:
            print("ERROR: Text cannot be empty")
            return
        
        try:
            success = await self.agent.type_in_element(selector, text)
            if success:
                print("SUCCESS: Text typed successfully!")
            else:
                print("ERROR: Failed to type text")
        except Exception as e:
            print(f"ERROR: Error typing text: {e}")

    async def handle_screenshot(self):
        """Handle taking screenshot"""
        if not self.agent.page:
            print("ERROR: No page loaded. Please navigate to a website first.")
            return
        
        try:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            await self.agent.take_screenshot(filename)
            print(f"SUCCESS: Screenshot saved as {filename}")
        except Exception as e:
            print(f"ERROR: Failed to take screenshot: {e}")


# Utility functions
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

# Main functions and modes
async def run_interactive_mode():
    """Run interactive browser mode"""
    async with UnifiedWebAgent() as agent:
        await agent.new_page()
        controller = InteractiveBrowserController(agent)
        await controller.start_interactive_session()

async def run_login_mode():
    """Run login mode"""
    print("=== LOGIN MODE ===")
    url = input("Enter website URL: ").strip()
    username = input("Enter username/email: ").strip()
    password = input("Enter password: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    async with UnifiedWebAgent() as agent:
        success = await agent.login_to_website(url, username, password)
        if success:
            print("Login successful!")
            await agent.take_screenshot("login_success.png")
        else:
            print("Login failed!")

async def run_scraper_mode(url: str, output: str = None):
    """Run web scraper mode"""
    print(f"=== SCRAPER MODE ===")
    
    # Validate and fix URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"Auto-corrected URL to: {url}")
    
    print(f"Analyzing: {url}")
    
    try:
        async with UnifiedWebAgent() as agent:
            analysis = await agent.analyze_page(url)
            analysis.print_elements()
            
            # Auto-generate filename if not provided
            if not output:
                output = agent.generate_filename_from_url(url, "elements")
            
            analysis.save_to_file(output)
            print(f"Results saved to {output}")
    except Exception as e:
        print(f"ERROR: Scraper failed - {e}")
        if "Cannot navigate to invalid URL" in str(e):
            print("HINT: Check if the URL is correct and accessible")
        elif "net::ERR_NAME_NOT_RESOLVED" in str(e):
            print("HINT: Check your internet connection or the domain name")
        elif "timeout" in str(e).lower():
            print("HINT: The website is taking too long to load, try again later")
        return False

async def run_navigate_mode(url: str):
    """Run simple navigation mode"""
    print(f"=== NAVIGATION MODE ===")
    
    # Validate and fix URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"Auto-corrected URL to: {url}")
    
    print(f"Navigating to: {url}")
    
    try:
        async with UnifiedWebAgent() as agent:
            await agent.navigate(url)
            await agent.take_screenshot("navigation.png")
            print(f"Successfully navigated to {agent.page.url}")
            print("Screenshot saved as navigation.png")
    except Exception as e:
        print(f"ERROR: Navigation failed - {e}")
        if "Cannot navigate to invalid URL" in str(e):
            print("HINT: Check if the URL is correct and accessible")
        elif "net::ERR_NAME_NOT_RESOLVED" in str(e):
            print("HINT: Check your internet connection or the domain name")
        elif "timeout" in str(e).lower():
            print("HINT: The website is taking too long to load, try again later")
        return False

def show_main_menu():
    """Show main menu for interactive selection"""
    print("=" * 60)
    print("UNIFIED WEB BROWSING AGENT")
    print("=" * 60)
    print("Select a mode:")
    print("1. Interactive Browser Mode - Real-time browser control")
    print("2. Login Mode - Automated website login")
    print("3. Web Scraper Mode - Analyze page elements")
    print("4. Navigation Mode - Simple page navigation")
    print("5. Exit")
    print("=" * 60)

async def main():
    """Main function"""
    # Validate environment first
    if not validate_environment():
        print("Warning: Environment validation failed. Check the log file for details.")
        print("The application will continue but may not work as expected.")
    
    parser = argparse.ArgumentParser(description="Unified Web Browsing Agent")
    parser.add_argument("--mode", choices=["interactive", "login", "scraper", "navigate"], 
                       help="Operation mode")
    parser.add_argument("--url", help="URL for navigation or scraping")
    parser.add_argument("--output", help="Output file for scraper results")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        await run_interactive_mode()
    elif args.mode == "login":
        await run_login_mode()
    elif args.mode == "scraper":
        if not args.url:
            print("Error: --url required for scraper mode")
            return
        await run_scraper_mode(args.url, args.output)
    elif args.mode == "navigate":
        if not args.url:
            print("Error: --url required for navigate mode")
            return
        await run_navigate_mode(args.url)
    else:
        # Interactive menu mode
        while True:
            show_main_menu()
            try:
                choice = input("Enter your choice (1-5): ").strip()
                
                if choice == "1":
                    await run_interactive_mode()
                elif choice == "2":
                    await run_login_mode()
                elif choice == "3":
                    url = input("Enter URL to analyze: ").strip()
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    output = input("Enter output file (optional): ").strip() or None
                    await run_scraper_mode(url, output)
                elif choice == "4":
                    url = input("Enter URL to navigate: ").strip()
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    await run_navigate_mode(url)
                elif choice == "5":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    asyncio.run(main())