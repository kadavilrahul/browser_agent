#!/usr/bin/env python3
"""
Advanced Web Browsing Agent

This script provides automated web browsing and login capabilities:
1. Navigate websites intelligently
2. Handle login flows
3. Extract and analyze content
4. Interact with web elements
5. Manage browser sessions
"""

import asyncio
import json
import logging
import os
import sys
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Initialize logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'web_agent.log')
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import required packages
from playwright.async_api import Page, Browser, async_playwright, ElementHandle

@dataclass
class BrowserState:
    """Maintains the current state of the browser session"""
    logged_in: bool = False
    current_url: str = ""
    cookies: Dict = field(default_factory=dict)
    local_storage: Dict = field(default_factory=dict)
    session_storage: Dict = field(default_factory=dict)

class WebBrowsingAgent:
    """Advanced web browsing agent"""
    
    def __init__(self, headless: Optional[bool] = None):
        """Initialize the agent
        
        Args:
            headless: Whether to run the browser in headless mode.
                      If None, it will be determined by the HEADLESS environment variable.
        """
        if headless is None:
            self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        else:
            self.headless = headless
        
        self.browser = None
        self.page = None
        self.state = BrowserState()
        
    async def __aenter__(self):
        """Context manager entry"""
        self.playwright = await async_playwright().start()
        
        launch_options = {
            'headless': self.headless,
            'args': ['--disable-blink-features=AutomationControlled']  # Avoid detection
        }

        if not self.headless:
            # If not headless, try to use xvfb-run
            try:
                # Check if xvfb-run is available
                subprocess.check_call(['which', 'xvfb-run'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.info("xvfb-run found. Launching browser with xvfb-run.")
                # Playwright handles xvfb-run internally if it's available and headless is false
                # No need to explicitly add it to args here, Playwright's launch method will manage it.
            except subprocess.CalledProcessError:
                logger.warning("xvfb-run not found. Running in non-headless mode without X server might fail.")
                logger.warning("Consider installing xvfb (e.g., sudo apt-get install xvfb) or setting HEADLESS=true.")
        
        self.browser = await self.playwright.chromium.launch(**launch_options)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def create_new_context(self):
        """Create a new browser context with custom settings"""
        context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation', 'notifications'],
            java_script_enabled=True
        )
        
        # Add custom scripts to avoid detection
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        return context

    async def new_page(self) -> Page:
        """Create a new page with stealth settings"""
        context = await self.create_new_context()
        self.page = await context.new_page()
        
        # Set up page event handlers
        self.page.on('dialog', lambda dialog: dialog.accept())
        self.page.on('pageerror', lambda error: logger.error(f"Page error: {error}"))
        
        return self.page

    async def navigate(self, url: str, wait_for_network: bool = True):
        """Navigate to a URL with smart waiting strategy"""
        if not self.page:
            await self.new_page()
        
        try:
            await self.page.goto(
                url,
                wait_until="networkidle" if wait_for_network else "domcontentloaded",
                timeout=30000
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
            
            # Fill username
            await self.page.fill('input[name="login"]', username)
            await asyncio.sleep(1)
            
            # Fill password
            await self.page.fill('input[name="password"]', password)
            await asyncio.sleep(1)
            
            # Click sign in
            await self.page.click('input[name="commit"]')
            await asyncio.sleep(3)
            
            # Check success
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
                    'input[type="email"]',
                    'input[type="text"]',
                    'input[name="username"]',
                    'input[name="email"]',
                    'input[id="email"]',
                    'input[id="username"]',
                    'input[name="login"]'
                ],
                'password': [
                    'input[type="password"]',
                    'input[name="password"]',
                    'input[id="password"]'
                ],
                'submit': [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Sign in")',
                    'button:has-text("Log in")',
                    'button:has-text("Login")',
                    'input[name="commit"]'
                ]
            }

            # Find username field
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

            # Fill username
            await username_field.fill(username)
            await asyncio.sleep(1)

            # Find password field
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

            # Fill password
            await password_field.fill(password)
            await asyncio.sleep(1)

            # Find submit button
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
                '.avatar',
                '.user-avatar',
                '.profile-pic',
                'a[href*="logout"]',
                'a[href*="signout"]',
                '.logout-button',
                '.user-menu',
                '.dashboard'
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

    async def take_screenshot(self, path: str):
        """Take a screenshot of the current page."""
        if self.page:
            try:
                await self.page.screenshot(path=path)
                logger.info(f"Screenshot saved to {path}")
            except Exception as e:
                logger.error(f"Failed to take screenshot: {e}")
        else:
            logger.warning("No page available to take a screenshot.")

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

async def test_navigation(url: str):
    """Tests basic navigation to a URL."""
    async with WebBrowsingAgent(headless=True) as agent: # Force headless for testing
        try:
            print(f"\nAttempting to navigate to {url} in headless mode...")
            await agent.new_page()
            await agent.navigate(url)
            print(f"✓ Successfully navigated to {agent.state.current_url}")
            return True
        except Exception as e:
            print(f"✗ Failed to navigate to {url}: {e}")
            return False

async def main():
    """Interactive web login agent or automated login/navigation via arguments"""
    # Check for command-line arguments for automated testing or navigation
    if len(sys.argv) >= 2:
        command = sys.argv[1]
        if command == "test_navigate" and len(sys.argv) == 3:
            url = sys.argv[2]
            async with WebBrowsingAgent() as agent: # Respect HEADLESS env var
                try:
                    print(f"\nAttempting to navigate to {url}...")
                    await agent.new_page()
                    await agent.navigate(url)
                    print(f"✓ Successfully navigated to {agent.state.current_url}")
                    await agent.take_screenshot("screenshot_navigate.png")
                    
                    # Keep browser open for a while to demonstrate success
                    if not agent.headless:
                        print("\nBrowser will stay open for 15 seconds to demonstrate successful navigation...")
                        await asyncio.sleep(15)
                    else:
                        print("\nNavigation successful in headless mode. Taking screenshot...")
                        await asyncio.sleep(3)
                    sys.exit(0)
                except Exception as e:
                    print(f"✗ Failed to navigate to {url}: {e}")
                    sys.exit(1)
        elif command == "login" and len(sys.argv) == 5:
            website_url = sys.argv[2]
            username = sys.argv[3]
            password = sys.argv[4]
            
            async with WebBrowsingAgent() as agent: # Respect HEADLESS env var for automated tests
                try:
                    print(f"\nAttempting automated login to {website_url}...")
                    success = await agent.login_to_website(website_url, username, password)
                    
                    if success:
                        print(f"\n✓ Successfully logged into {website_url}")
                        await agent.take_screenshot("screenshot_login.png")
                        
                        # Keep browser open for a while to demonstrate success
                        if not agent.headless:
                            print("\nBrowser will stay open for 30 seconds to demonstrate successful login...")
                            await asyncio.sleep(30)
                        else:
                            print("\nLogin successful in headless mode. Taking screenshot...")
                            await asyncio.sleep(5)
                        sys.exit(0)
                    else:
                        print(f"\n✗ Failed automated login to {website_url}")
                        await agent.take_screenshot("screenshot_login_failed.png")
                        sys.exit(1)
                        
                except Exception as e:
                    print(f"\n✗ Error during automated login: {str(e)}")
                    await agent.take_screenshot("screenshot_error.png")
                    sys.exit(1)
            return

    # Original interactive mode
    async with WebBrowsingAgent() as agent:
        try:
            while True:
                print("\n=== Web Login Agent ===")
                print("Enter website details (or press Enter to exit)")
                
                website_url = input("\nEnter website URL (e.g., https://github.com): ").strip()
                if not website_url:
                    print("\nExiting...")
                    break
                
                if not website_url.startswith(('http://', 'https://')):
                    website_url = 'https://' + website_url
                
                username = input("Enter username/email: ").strip()
                password = input("Enter password: ").strip()
                
                if not username or not password:
                    print("Error: Username and password are required")
                    continue
                
                try:
                    print(f"\nAttempting to login to {website_url}...")
                    
                    success = await agent.login_to_website(
                        website_url,
                        username,
                        password
                    )
                    
                    if success:
                        print(f"\n✓ Successfully logged into {website_url}")
                        
                        domain = website_url.split('//')[-1].split('/')[0].replace('.', '_')
                        session_file = f"{domain}_session.json"
                        await agent.save_session(session_file)
                        print(f"✓ Saved session to {session_file}")
                        
                        while True:
                            print("\nWhat would you like to do?")
                            print("1. Try another website")
                            print("2. Keep browser open and exit")
                            print("3. Close browser and exit")
                            
                            choice = input("\nEnter your choice (1-3): ").strip()
                            
                            if choice == '1':
                                break
                            elif choice == '2':
                                print("\nKeeping browser open. Press Ctrl+C to exit...")
                                while True:
                                    await asyncio.sleep(1)
                            elif choice == '3':
                                print("\nClosing browser...")
                                return
                            else:
                                print("Invalid choice. Please try again.")
                    
                    else:
                        print(f"\n✗ Failed to login to {website_url}")
                        retry = input("\nWould you like to retry? (y/n): ").strip().lower()
                        if retry != 'y':
                            print("\nMoving to next website...")
                
                except KeyboardInterrupt:
                    print("\nOperation cancelled by user")
                    break
                except Exception as e:
                    print(f"\n✗ Error: {str(e)}")
                    cont = input("\nWould you like to try another website? (y/n): ").strip().lower()
                    if cont != 'y':
                        break
            
            print("\nThank you for using Web Login Agent!")
        
        except KeyboardInterrupt:
            print("\nReceived exit signal. Closing browser...")
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    asyncio.run(main())