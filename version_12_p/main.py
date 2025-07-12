#!/usr/bin/env python3

import asyncio
import argparse
import json
import logging
import os
import sys
import subprocess
import time
import socket
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
    analysis: str = ""   # Analysis result from Gemini
    
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
                text: text.substring(0, 100), # Limit text length
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

    @staticmethod
    def is_port_available(port: int) -> bool:
        """Check if a port is available for use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
            return True
        except OSError as e:
            logger.warning(f"Port {port} is unavailable: {e}")
            return False

    @staticmethod
    def is_port_available(port: int) -> bool:
        """Check if a port is available for use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
            return True
        except OSError as e:
            logger.warning(f"Port {port} is unavailable: {e}")
            return False

    @staticmethod
    def is_port_available(port: int) -> bool:
        """Check if a port is available for use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
            return True
        except OSError as e:
            logger.warning(f"Port {port} is unavailable: {e}")
            return False

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
"""Find all clickable elements on the current page and analyze with Gemini API"""
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
logger.info(f"Found {len(elements)} clickable elements. Analyzing with Gemini...")
# Analyze elements with Gemini API (Placeholder)
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
logger.warning("GEMINI_API_KEY not found. Skipping element analysis.")
else:
# Implement Gemini API call here to analyze elements
# This is a placeholder, replace with actual Gemini API call
logger.info("Gemini API analysis is not yet implemented. Add code here to call Gemini API")
return elements
# Login functionality methods
async def login_to_website(self, url: str, username: str, password: str) -> bool:
"""Universal login function for any website"""
logger.info(f"Attempting to login to {url}")
await self.navigate(url)
await asyncio.sleep(2)
# Step 1: Analyze elements on the login page
elements = await self.find_clickable_elements()
logger.info(f"Found {len(elements)} clickable elements on the login page")
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
# Step 2: Analyze elements after filling username
elements = await self.find_clickable_elements()
logger.info(f"Found {len(elements)} clickable elements after filling username")
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
# Step 3: Analyze elements after filling password
elements = await self.find_clickable_elements()
logger.info(f"Found {len(elements)} clickable elements after filling password")
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
# Step 4: Analyze elements after submitting form
elements = await self.find_clickable_elements()
logger.info(f"Found {len(elements)} clickable elements after submitting form")
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
"""Start the interactive browser session, find elements, and wait for user input."""
print("BROWSER READY")
# Automatically find elements on the current page
await self.handle_find_elements()
# Proceed to the interactive loop
await self.interactive_loop()
async def interactive_loop(self):
"""Main interactive command loop, streamlined for direct element interaction."""
while self.running:
try:
# Directly ask for the element to click
await self.handle_click_element()
# After a click, re-scan for elements on the new page
print("\nPage may have changed. Re-scanning for elements...")
await self.handle_find_elements()
except KeyboardInterrupt:
print("\nExiting...")
break
except EOFError:
print("\nInput ended, exiting...")
break
except Exception as e:
print(f"An error occurred: {e}")
logger.error(f"Interactive loop error: {e}")
# Offer a way to recover or exit
choice = input("Continue (c) or Exit (e)? ").strip().lower()
if choice == 'e':
break
self.running = False
async def auto_save_elements(self):
"""Automatically save elements with timestamp and short URL name"""
try:
# Generate filename using utility function
current_url = self.agent.state.current_url
filename = self.agent.generate_filename_from_url(current_url, "elements")
# Create analysis object and save
744