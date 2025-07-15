#!/usr/bin/env python3

"""
Unified Web Browsing Agent with AI Integration
"""

import asyncio
import argparse
import json
import logging
import os
import sys
import subprocess
import time
import requests
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Import required packages
try:
    from playwright.async_api import async_playwright, Page, Browser, ElementHandle
except ImportError:
    print("ERROR: Playwright not found!")
    sys.exit(1)

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
except ImportError:
    Agent = None
    OpenAIChat = None

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_file = os.getenv('LOG_FILE', 'web_agent.log')

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(log_level)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Data classes
@dataclass
class BrowserState:
    logged_in: bool = False
    current_url: str = ""
    cookies: Dict = field(default_factory=dict)
    local_storage: Dict = field(default_factory=dict)
    session_storage: Dict = field(default_factory=dict)

@dataclass
class ElementInfo:
    index: int
    tag_name: str
    text: str
    attributes: Dict[str, str] = field(default_factory=dict)
    xpath: str = ""
    is_visible: bool = True
    is_in_viewport: bool = True
    bounding_box: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)
    
    def __str__(self):
        attrs = " ".join([f'{k}="{v}"' for k, v in self.attributes.items() 
                         if k in ['id', 'class', 'name', 'role', 'type', 'href']])
        return f"[{self.index}] <{self.tag_name} {attrs}>{self.text}</{self.tag_name}>"

@dataclass
class PageAnalysis:
    url: str
    title: str
    timestamp: str
    elements: List[ElementInfo] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "timestamp": self.timestamp,
            "elements": [elem.to_dict() for elem in self.elements]
        }
    
    def save_to_file(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Analysis saved to {filename}")

# Configuration class
class Config:
    def __init__(self):
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.browser_timeout = int(os.getenv('BROWSER_TIMEOUT', '30000'))
        self.viewport_width = int(os.getenv('VIEWPORT_WIDTH', '1280'))
        self.viewport_height = int(os.getenv('VIEWPORT_HEIGHT', '800'))
        self.wait_for_network = os.getenv('WAIT_FOR_NETWORK', 'true').lower() == 'true'
        self.screenshot_quality = int(os.getenv('SCREENSHOT_QUALITY', '90'))
        self.disable_automation = os.getenv('DISABLE_AUTOMATION_DETECTION', 'true').lower() == 'true'
        
        # AI Configuration
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        self.gemini_endpoint = os.getenv('GEMINI_ENDPOINT', 'https://generativelanguage.googleapis.com/v1beta/models/')
        
        # Popular website URLs
        self.website_urls = {
            'github': os.getenv('GITHUB_URL', 'https://github.com/login'),
            'google': os.getenv('GOOGLE_URL', 'https://accounts.google.com/signin'),
            'facebook': os.getenv('FACEBOOK_URL', 'https://www.facebook.com/login'),
            'twitter': os.getenv('TWITTER_URL', 'https://twitter.com/i/flow/login'),
            'linkedin': os.getenv('LINKEDIN_URL', 'https://www.linkedin.com/login'),
            'instagram': os.getenv('INSTAGRAM_URL', 'https://www.instagram.com/accounts/login/'),
            'reddit': os.getenv('REDDIT_URL', 'https://www.reddit.com/login'),
            'amazon': os.getenv('AMAZON_URL', 'https://www.amazon.com/ap/signin'),
            'netflix': os.getenv('NETFLIX_URL', 'https://www.netflix.com/login'),
            'youtube': os.getenv('YOUTUBE_URL', 'https://accounts.google.com/signin/v2/identifier?service=youtube')
        }
        
        # Test configuration
        self.test_url = os.getenv('TEST_URL', 'https://httpbin.org/forms/post')
        self.test_username = os.getenv('TEST_USERNAME', 'test_user')
        self.test_password = os.getenv('TEST_PASSWORD', 'test_pass')
    
    def get_website_url(self, website_name: str) -> str:
        return self.website_urls.get(website_name.lower(), website_name)

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

# AI Integration Classes
class GeminiAI:
    """Gemini AI integration for intelligent element selection and page analysis"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini AI client"""
        if not genai or not self.config.gemini_api_key or self.config.gemini_api_key == 'your_gemini_api_key_here':
            logger.warning("Gemini AI not available - missing API key or library")
            return
        
        try:
            genai.configure(api_key=self.config.gemini_api_key)
            self.client = genai.GenerativeModel(self.config.gemini_model)
            logger.info("Gemini AI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.client = None
    
    async def analyze_page_elements(self, elements: List[ElementInfo], user_intent: str) -> Dict[str, Any]:
        """Analyze page elements and suggest best actions based on user intent"""
        if not self.client:
            return {"error": "Gemini AI not available"}
        
        try:
            # Prepare elements data for AI analysis
            elements_data = []
            for elem in elements[:20]:  # Limit to first 20 elements to avoid token limits
                elements_data.append({
                    "index": elem.index,
                    "tag": elem.tag_name,
                    "text": elem.text[:100],  # Limit text length
                    "attributes": {k: v for k, v in elem.attributes.items() 
                                 if k in ['id', 'class', 'name', 'type', 'href', 'role']}
                })
            
            prompt = f"""
            Analyze the following webpage elements and suggest the best action for this user intent: "{user_intent}"
            
            Available elements:
            {json.dumps(elements_data, indent=2)}
            
            Please respond with a JSON object containing:
            1. "recommended_element": The index of the best element to interact with
            2. "confidence": A confidence score from 0-100
            3. "reasoning": Brief explanation of why this element was chosen
            4. "action_type": Suggested action ("click", "fill", "select", etc.)
            5. "additional_steps": Any additional steps needed
            
            If no suitable element is found, set recommended_element to -1.
            """
            
            response = self.client.generate_content(prompt)
            
            # Parse AI response
            try:
                ai_response = json.loads(response.text)
                logger.info(f"AI analysis completed with confidence: {ai_response.get('confidence', 0)}")
                return ai_response
            except json.JSONDecodeError:
                # Fallback: extract information from text response
                return {
                    "recommended_element": -1,
                    "confidence": 50,
                    "reasoning": response.text[:200],
                    "action_type": "manual_review",
                    "additional_steps": ["Review AI response manually"]
                }
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"error": f"AI analysis failed: {str(e)}"}
    
    async def suggest_element_for_task(self, elements: List[ElementInfo], task: str) -> Optional[int]:
        """Suggest the best element index for a specific task"""
        analysis = await self.analyze_page_elements(elements, task)
        
        if "error" in analysis:
            return None
        
        recommended = analysis.get("recommended_element", -1)
        confidence = analysis.get("confidence", 0)
        
        # Only return suggestion if confidence is reasonable
        if recommended >= 0 and confidence >= 60:
            logger.info(f"AI suggests element {recommended} with {confidence}% confidence")
            return recommended
        
        return None
    
    async def generate_page_summary(self, page_title: str, elements: List[ElementInfo]) -> str:
        """Generate a summary of the current page"""
        if not self.client:
            return "AI summary not available"
        
        try:
            # Prepare summary data
            element_types = {}
            for elem in elements:
                elem_type = elem.tag_name
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            prompt = f"""
            Summarize this webpage in 2-3 sentences:
            
            Page Title: {page_title}
            Available Elements: {element_types}
            
            Focus on what the user can do on this page.
            """
            
            response = self.client.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate page summary: {e}")
            return f"Page: {page_title} with {len(elements)} interactive elements"

class AgnoAgent:
    """Agno agent integration for validation and smooth execution"""
    
    def __init__(self, config: Config):
        self.config = config
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize Agno agent"""
        if not Agent or not OpenAIChat:
            logger.warning("Agno agent not available - missing library")
            return
        
        try:
            # Note: This would require OpenAI API key for full functionality
            # For now, we'll create a basic agent structure
            self.agent = Agent(
                model=None,  # Would need OpenAI model here
                description="Web browsing validation and execution agent",
                markdown=True,
                exponential_backoff=True,
                retries=2,
                retry_delay=1
            )
            logger.info("Agno agent structure initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Agno agent: {e}")
            self.agent = None
    
    async def validate_action(self, action: str, element: ElementInfo, context: str) -> Dict[str, Any]:
        """Validate if an action is safe and appropriate"""
        # Basic validation without full Agno functionality
        validation_result = {
            "is_safe": True,
            "confidence": 80,
            "warnings": [],
            "suggestions": []
        }
        
        # Basic safety checks
        if element.tag_name == "a" and "href" in element.attributes:
            href = element.attributes["href"]
            if href.startswith("javascript:") or "onclick" in element.attributes:
                validation_result["warnings"].append("Link contains JavaScript - proceed with caution")
                validation_result["confidence"] = 60
        
        if element.tag_name == "input" and element.attributes.get("type") == "file":
            validation_result["warnings"].append("File upload detected - ensure you trust this site")
            validation_result["confidence"] = 70
        
        if "delete" in element.text.lower() or "remove" in element.text.lower():
            validation_result["warnings"].append("Destructive action detected - double-check before proceeding")
            validation_result["confidence"] = 50
        
        if "submit" in element.text.lower() or element.attributes.get("type") == "submit":
            validation_result["warnings"].append("Form submission detected - review data before proceeding")
            validation_result["confidence"] = 65
        
        # Check for external links
        if element.tag_name == "a" and "href" in element.attributes:
            href = element.attributes["href"]
            if href.startswith("http") and not any(domain in href for domain in [context]):
                validation_result["warnings"].append("External link detected - will navigate away from current site")
                validation_result["confidence"] = 70
        
        logger.info(f"Action validation completed with {validation_result['confidence']}% confidence")
        return validation_result
    
    async def suggest_next_steps(self, current_page: str, user_goal: str) -> List[str]:
        """Suggest next steps based on current page and user goal"""
        # Basic suggestions without full Agno functionality
        suggestions = []
        
        if "login" in current_page.lower():
            suggestions.extend([
                "Fill in username/email field",
                "Fill in password field",
                "Click login/sign in button"
            ])
        elif "search" in current_page.lower():
            suggestions.extend([
                "Enter search terms",
                "Click search button or press Enter"
            ])
        elif "form" in current_page.lower():
            suggestions.extend([
                "Fill required fields",
                "Review form data",
                "Submit form"
            ])
        elif "checkout" in current_page.lower() or "cart" in current_page.lower():
            suggestions.extend([
                "Review items in cart",
                "Enter shipping information",
                "Select payment method",
                "Complete purchase"
            ])
        elif "profile" in current_page.lower() or "account" in current_page.lower():
            suggestions.extend([
                "Update profile information",
                "Change account settings",
                "View account history"
            ])
        else:
            suggestions.extend([
                "Analyze available elements",
                "Identify relevant navigation options",
                "Take screenshot for reference"
            ])
        
        return suggestions
    
    async def monitor_execution(self, action: str, success: bool, error_msg: str = "") -> Dict[str, Any]:
        """Monitor action execution and provide feedback"""
        monitoring_result = {
            "action": action,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "feedback": "",
            "next_recommendations": []
        }
        
        if success:
            monitoring_result["feedback"] = "Action completed successfully"
            monitoring_result["next_recommendations"] = [
                "Wait for page to load",
                "Scan for new elements",
                "Continue with next step"
            ]
        else:
            monitoring_result["feedback"] = f"Action failed: {error_msg}"
            monitoring_result["next_recommendations"] = [
                "Retry the action",
                "Try alternative element",
                "Check page state",
                "Take screenshot for debugging"
            ]
        
        logger.info(f"Execution monitoring: {action} - {'Success' if success else 'Failed'}")
        return monitoring_result
    
    async def analyze_page_context(self, url: str, title: str, elements: List[ElementInfo]) -> Dict[str, Any]:
        """Analyze page context to understand what type of page this is"""
        context_analysis = {
            "url": url,
            "title": title,
            "num_elements": len(elements),
            "is_login_page": False,
            "is_form_page": False,
            "is_search_page": False,
        }

        title_lower = title.lower()
        if "login" in title_lower or "sign in" in title_lower:
            context_analysis["is_login_page"] = True
        if any(tag in url for tag in ["form", "submit", "register"]):
            context_analysis["is_form_page"] = True
        if any(tag in url for tag in ["search", "query", "find"]):
            context_analysis["is_search_page"] = True

        return context_analysis

class UnifiedWebAgent:
    """Unified web browsing agent with AI integration and all functionalities"""
    
    def __init__(self, headless: Optional[bool] = None):
        """Initialize the agent"""
        self.config = Config()
        
        if headless is not None:
            self.config.headless = headless
        
        # Force headless mode if no display available
        if not os.getenv('DISPLAY'):
            self.config.headless = True
        
        self.browser = None
        self.page = None
        self.state = BrowserState()
        
        # Initialize AI components
        self.gemini_ai = GeminiAI(self.config)
        self.agno_agent = AgnoAgent(self.config)
        
    async def __aenter__(self):
        """Context manager entry"""
        try:
            self.playwright = await async_playwright().start()
            
            launch_options = {
                'headless': self.config.headless,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            }

            if not self.config.headless:
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
        context = await self.browser.new_context(
            viewport={'width': self.config.viewport_width, 'height': self.config.viewport_height},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation', 'notifications'],
            java_script_enabled=True
        )
        
        # Add stealth script if automation detection is disabled
        if self.config.disable_automation:
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
        
        # Check if URL is a website name and convert to full URL
        full_url = self.config.get_website_url(url)
        if not full_url.startswith(('http://', 'https://')):
            full_url = 'https://' + full_url
        
        if wait_for_network is None:
            wait_for_network = self.config.wait_for_network
        
        try:
            await self.page.goto(
                full_url,
                wait_until="networkidle" if wait_for_network else "domcontentloaded",
                timeout=self.config.browser_timeout
            )
            
            await self.page.wait_for_load_state("domcontentloaded")
            self.state.current_url = self.page.url
            
            # Store cookies and storage data
            self.state.cookies = await self.page.context.cookies()
            self.state.local_storage = await self.page.evaluate("() => Object.assign({}, window.localStorage)")
            self.state.session_storage = await self.page.evaluate("() => Object.assign({}, window.sessionStorage)")
            
            logger.info(f"Successfully navigated to: {self.state.current_url}")
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            raise

    async def take_screenshot(self, path: str):
        """Take a screenshot of the current page"""
        if self.page:
            try:
                screenshot_options = {'path': path, 'full_page': True}
                
                # Add quality setting for JPEG files
                if path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
                    screenshot_options['quality'] = self.config.screenshot_quality
                
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

    async def get_ai_element_suggestion(self, user_intent: str) -> Dict[str, Any]:
        """Get AI suggestion for element interaction based on user intent"""
        try:
            elements = await self.find_clickable_elements()
            if not elements:
                return {"error": "No clickable elements found on page"}
            
            analysis = await self.gemini_ai.analyze_page_elements(elements, user_intent)
            return analysis
            
        except Exception as e:
            logger.error(f"AI suggestion failed: {e}")
            return {"error": f"AI suggestion failed: {str(e)}"}

    async def get_page_summary(self) -> str:
        """Get AI-generated summary of the current page"""
        try:
            if not self.page:
                return "No page loaded"
            
            title = await self.page.title()
            elements = await self.find_clickable_elements()
            summary = await self.gemini_ai.generate_page_summary(title, elements)
            return summary
            
        except Exception as e:
            logger.error(f"Page summary failed: {e}")
            return f"Page summary unavailable: {str(e)}"

    # Login functionality methods
    async def login_to_website(self, url: str, username: str, password: str) -> bool:
        """Universal login function for any website"""
        try:
            logger.info(f"Attempting to login to {url}")
            
            # Convert website name to URL if needed
            full_url = self.config.get_website_url(url)
            await self.navigate(full_url)
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
            for selector in common_selectors["password"]:
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
            for selector in common_selectors["submit"]:
                try:
                    submit_button = await self.page.wait_for_selector(selector, timeout=2000)
                    if submit_button:
                        break
                except:
                    continue

            if submit_button:
                await submit_button.click()
            else:
                await password_field.press("Enter")

            await asyncio.sleep(3)

            # Check login success
            success_indicators = [
                ".avatar", ".user-avatar", ".profile-pic", "a[href*=\"logout\"]",
                "a[href*=\"signout\"]", ".logout-button", ".user-menu", ".dashboard"
            ]

            # Check URL change
            current_url = self.page.url
            if current_url != full_url and "login" not in current_url.lower():
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
                for warning in validation["warnings"]:
                    print(f"   - {warning}")
                
                if validation["confidence"] < 70:
                    confirm = input("Proceed anyway? (y/N): ").strip().lower()
                    if confirm != "y":
                        print("Action cancelled by user")
                        return False
            
            # Attempt to click using different strategies
            success = False
            
            # Strategy 1: XPath
            if element.xpath and not success:
                try:
                    await self.page.click(f"xpath={element.xpath}")
                    success = True
                    logger.info(f"Clicked element {element_index} using XPath")
                except:
                    pass
            
            # Strategy 2: ID selector
            if "id" in element.attributes and not success:
                try:
                    await self.page.click(f"#{element.attributes["id"]}")
                    success = True
                    logger.info(f"Clicked element {element_index} using ID selector")
                except:
                    pass
            
            # Strategy 3: Coordinates
            if element.bounding_box and not success:
                try:
                    x = element.bounding_box["x"] + element.bounding_box["width"] / 2
                    y = element.bounding_box["y"] + element.bounding_box["height"] / 2
                    await self.page.mouse.click(x, y)
                    success = True
                    logger.info(f"Clicked element {element_index} using coordinates")
                except:
                    pass
            
            # Monitor execution
            await self.agno_agent.monitor_execution("click", success, "" if success else "All click strategies failed")
            
            if success:
                await asyncio.sleep(2)  # Wait for potential page changes
            
            return success
            
        except Exception as e:
            logger.error(f"Error clicking element {element_index}: {e}")
            await self.agno_agent.monitor_execution("click", False, str(e))
            return False

    def generate_filename_from_url(self, url: str, prefix: str = "elements") -> str:
        """Generate a filename with timestamp and short URL name"""
        try:
            import re
            
            # Extract domain and path for short name
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace("www.", "")
            path = parsed_url.path.strip("/").replace("/", "_")
            
            # Create short URL name (max 30 chars)
            if path:
                short_url = f"{domain}_{path}"[:30]
            else:
                short_url = domain[:30]
            
            # Remove invalid filename characters
            short_url = re.sub(r"[<>:/\\|?*]", "_", short_url)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}_{short_url}.json"
            
            return filename
            
        except Exception as e:
            # Fallback to simple timestamp if URL parsing fails
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{prefix}_{timestamp}.json"

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False        
    async def interactive_loop(self):
        """Main interactive command loop"""
        while self.running:
            try:
                print("\n" + "="*50)
                print("🤖 AI Web Agent - Choose an action:")
                print("1. Click element by index")
                print("2. Get AI suggestion")
                print("3. Navigate to URL")
                print("4. Take screenshot")
                print("5. Get page summary")
                print("6. Refresh elements")
                print("7. Exit")
                print("="*50)
                
                choice = input("Enter choice (1-7): ").strip()
                
                if choice == "1":
                    await self.handle_click_element()
                elif choice == "2":
                    await self.handle_ai_suggestion()
                elif choice == "3":
                    await self.handle_navigate()
                elif choice == "4":
                    await self.handle_screenshot()
                elif choice == "5":
                    await self.handle_page_summary()
                elif choice == "6":
                    await self.handle_find_elements()
                elif choice == "7":
                    print("👋 Goodbye!")
                    self.running = False
                else:
                    print("❌ Invalid choice. Please try again.")

            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except EOFError:
                print("\n👋 Input ended, exiting...")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                logger.error(f"Interactive loop error: {e}")
                choice = input("Continue (c) or Exit (e)? ").strip().lower()
                if choice == "e":
                    break
        self.running = False

    async def handle_find_elements(self):
        """Handle finding clickable elements"""
        if not self.agent.page:
            print("❌ No page loaded. Please navigate to a website first.")
            return

        try:
            print("🔍 Searching for clickable elements...")
            self.current_elements = await self.agent.find_clickable_elements()
            print(f"✅ Found {len(self.current_elements)} clickable elements")

            # Auto-save elements to file with timestamp and short URL
            if self.current_elements:
                await self.auto_save_elements()

                print("\n📋 Available elements:")
                for elem in self.current_elements[:10]:  # Show first 10
                    text_preview = elem.text[:50] + "..." if len(elem.text) > 50 else elem.text
                    print(f"  [{elem.index}] <{elem.tag_name}> - {text_preview}")
                
                if len(self.current_elements) > 10:
                    print(f"  ... and {len(self.current_elements) - 10} more elements")
            else:
                print("ℹ️  No clickable elements found on this page")

        except Exception as e:
            print(f"❌ Failed to find elements: {e}")
            logger.error(f"Error finding elements: {e}")

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
            print(f"💾 AUTO-SAVED: Elements saved to {filename}")
            
        except Exception as e:
            print(f"⚠️  Auto-save failed: {e}")

    async def handle_click_element(self):
        """Handle clicking an element"""
        if not self.current_elements:
            print("❌ No clickable elements found. Please refresh elements first.")
            return

        print(f"\n📋 Available elements (0-{len(self.current_elements) - 1}):")
        for elem in self.current_elements[:15]:  # Show first 15
            text_preview = elem.text[:60] + "..." if len(elem.text) > 60 else elem.text
            print(f"  [{elem.index}] <{elem.tag_name}> - {text_preview}")

        try:
            index_input = input("\nEnter element index to click: ").strip()
            element_index = int(index_input)
            
            # Find the specific element from the list
            element_to_click = next((elem for elem in self.current_elements if elem.index == element_index), None)

            if element_to_click is None:
                print(f"❌ Invalid index. Please enter a number between 0 and {len(self.current_elements) - 1}.")
                return

            print(f"🖱️  Clicking element [{element_index}]: <{element_to_click.tag_name}> - {element_to_click.text[:50]}")
            
            success = await self.agent.click_element(element_index, self.current_elements)
            if success:
                print("✅ Element clicked successfully!")
                await asyncio.sleep(3)  # Wait for page to potentially load
                print("🔄 Re-scanning for elements...")
                await self.handle_find_elements()
            else:
                print("❌ Failed to click element.")
                
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")
        except Exception as e:
            print(f"❌ An error occurred while clicking the element: {e}")
            logger.error(f"Error clicking element: {e}")

    async def handle_ai_suggestion(self):
        """Handle AI suggestion for element interaction"""
        if not self.current_elements:
            print("❌ No elements available. Please refresh elements first.")
            return
        
        user_intent = input("🤖 What would you like to do? (e.g., login, search, click submit): ").strip()
        if not user_intent:
            print("❌ Please provide a valid intent.")
            return
        
        print("🧠 Getting AI suggestion...")
        try:
            suggestion = await self.agent.get_ai_element_suggestion(user_intent)
            
            if "error" in suggestion:
                print(f"❌ AI suggestion failed: {suggestion[error]}")
                return
            
            print(f"🎯 AI Recommendation:")
            print(f"   Element: {suggestion.get(recommended_element, None)}")
            print(f"   Confidence: {suggestion.get(confidence, 0)}%")
            print(f"   Action: {suggestion.get(action_type, Unknown)}")
            print(f"   Reasoning: {suggestion.get('reasoning', 'No reasoning provided')}")
            
            if suggestion.get(recommended_element, -1) >= 0:
                proceed = input("🤔 Would you like to execute this suggestion? (y/N): ").strip().lower()
                if proceed == y:
                    element_index = suggestion[recommended_element]
                    success = await self.agent.click_element(element_index, self.current_elements)
                    if success:
                        print("✅ AI suggestion executed successfully!")
                        await asyncio.sleep(3)
                        await self.handle_find_elements()
                    else:
                        print("❌ Failed to execute AI suggestion.")
            
        except Exception as e:
            print(f"❌ AI suggestion failed: {e}")
            logger.error(f"AI suggestion error: {e}")

    async def handle_navigate(self):
        """Handle navigation to a new URL"""
        url = input("🌐 Enter URL or website name (e.g., github, google.com): ").strip()
        if not url:
            print("❌ Please provide a valid URL.")
            return
        
        try:
            print(f"🚀 Navigating to {url}...")
            await self.agent.navigate(url)
            print(f"✅ Successfully navigated to: {self.agent.state.current_url}")
            
            # Automatically find elements on new page
            await self.handle_find_elements()
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            logger.error(f"Navigation error: {e}")

    async def handle_screenshot(self):
        """Handle taking a screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            print(f"📸 Taking screenshot...")
            await self.agent.take_screenshot(filename)
            print(f"✅ Screenshot saved as: {filename}")
            
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            logger.error(f"Screenshot error: {e}")

    async def handle_page_summary(self):
        """Handle getting AI page summary"""
        try:
            print("🧠 Generating AI page summary...")
            summary = await self.agent.get_page_summary()
            print(f"📄 Page Summary:")
            print(f"   {summary}")
            
        except Exception as e:
            print(f"❌ Page summary failed: {e}")
            logger.error(f"Page summary error: {e}")

# Main execution functions
async def run_interactive_mode():
    """Run the interactive web browsing mode"""
    print("=" * 60)
    print("🤖 UNIFIED WEB AGENT - INTERACTIVE MODE")
    print("=" * 60)
    
    # Get initial URL from user
    url = input("🌐 Enter starting URL or website name (or press Enter for test site): ").strip()
    if not url:
        url = os.getenv("TEST_URL", "https://httpbin.org/forms/post")
        print(f"Using test URL: {url}")
        
    async with UnifiedWebAgent() as agent:
        try:
            # Navigate to initial URL
            await agent.navigate(url)
            print(f"✅ Successfully loaded: {agent.state.current_url}")
            
            # Start interactive session
            controller = InteractiveBrowserController(agent)
            await controller.start_interactive_session()
            
        except Exception as e:
            print(f"❌ Failed to start interactive mode: {e}")
            logger.error(f"Interactive mode error: {e}")

async def run_login_mode():
    """Run the login mode"""
    print("=" * 60)
    print("🔐 UNIFIED WEB AGENT - LOGIN MODE")
    print("=" * 60)
    
    # Get login credentials from user
    url = input("🌐 Enter website URL or name (e.g., github, google): ").strip()
    username = input("👤 Enter username/email: ").strip()
    password = input("🔒 Enter password: ").strip()
    
    if not all([url, username, password]):
        print("❌ All fields are required for login.")
        return
        
    async with UnifiedWebAgent() as agent:
        try:
            # Attempt to log in
            print(f"🔐 Attempting login to {url}...")
            success = await agent.login_to_website(url, username, password)
            
            if success:
                print("✅ Login successful!")
                await agent.take_screenshot("login_success.png")
                
                # Start interactive session after successful login
                print("🚀 Starting interactive session...")
                controller = InteractiveBrowserController(agent)
                await controller.start_interactive_session()
            else:
                print("❌ Login failed. Please check your credentials and try again.")
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            logger.error(f"Login error: {e}")

def show_main_menu():
    """Show the main menu"""
    print("\n" + "=" * 60)
    print("🤖 UNIFIED WEB AGENT WITH AI INTEGRATION")
    print("=" * 60)
    print("1. 🌐 Interactive Browsing Mode")
    print("2. 🔐 Login Mode")
    print("3. 🧪 Test Mode (Demo)")
    print("4. ❌ Exit")
    print("=" * 60)

async def run_test_mode():
    """Run test mode with demo functionality"""
    print("=" * 60)
    print("🧪 UNIFIED WEB AGENT - TEST MODE")
    print("=" * 60)
    
    test_url = os.getenv("TEST_URL", "https://httpbin.org/forms/post")
    
    async with UnifiedWebAgent() as agent:
        try:
            print(f"🚀 Navigating to test site: {test_url}")
            await agent.navigate(test_url)
            
            print("🔍 Finding elements...")
            elements = await agent.find_clickable_elements()
            print(f"✅ Found {len(elements)} clickable elements")
            
            print("📸 Taking screenshot...")
            await agent.take_screenshot("test_screenshot.png")
            
            print("🧠 Getting AI page summary...")
            summary = await agent.get_page_summary()
            print(f"📄 Summary: {summary}")
            
            if elements:
                print("🤖 Getting AI suggestion for form interaction...")
                suggestion = await agent.get_ai_element_suggestion("fill out the form")
                print(f"🎯 AI Suggestion: {suggestion}")
            
            print("✅ Test mode completed successfully!")
            
        except Exception as e:
            print(f"❌ Test mode failed: {e}")
            logger.error(f"Test mode error: {e}")

async def main():
    """Main function"""
    print("🚀 Starting Unified Web Agent...")
    
    # Check if running in non-interactive mode
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "test":
            await run_test_mode()
            return
        elif mode == "interactive":
            await run_interactive_mode()
            return
        elif mode == "login":
            await run_login_mode()
            return
    
    # Interactive menu mode
    while True:
        try:
            show_main_menu()
            choice = input("Choose option (1-4): ").strip()
            
            if choice == "1":
                await run_interactive_mode()
            elif choice == "2":
                await run_login_mode()
            elif choice == "3":
                await run_test_mode()
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            logger.error(f"Main loop error: {e}")

if __name__ == "__main__":
    # Suppress playwright logs for cleaner output
    logging.getLogger("playwright").setLevel(logging.WARNING)
    asyncio.run(main())
