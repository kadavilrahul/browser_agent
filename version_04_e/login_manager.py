#!/usr/bin/env python3
"""
Login Manager Module
Handles login functionality and session management for various websites
"""

import asyncio
import json
import logging
import os
from typing import Dict, Optional
from browser_core import BrowserCore, logger

class LoginManager:
    """Manages login functionality and session persistence"""
    
    def __init__(self, browser_core: BrowserCore):
        """Initialize login manager with browser core"""
        self.browser = browser_core
        
    async def login_google(self, email: str, password: str) -> bool:
        """Login to Google account"""
        try:
            await self.browser.navigate("https://accounts.google.com/signin/v2/identifier")
            await asyncio.sleep(2)
            
            # Enter email
            email_selector = 'input[type="email"]'
            await self.browser.page.wait_for_selector(email_selector, state="visible", timeout=10000)
            await self.browser.page.fill(email_selector, email)
            await asyncio.sleep(1)
            
            # Click Next
            next_button = await self.browser.page.query_selector('button:has-text("Next")')
            if next_button:
                await next_button.click()
            else:
                await self.browser.page.keyboard.press('Enter')
            
            # Enter password
            await asyncio.sleep(2)
            password_selector = 'input[type="password"]'
            await self.browser.page.wait_for_selector(password_selector, state="visible", timeout=10000)
            await self.browser.page.fill(password_selector, password)
            await asyncio.sleep(1)
            
            # Click Next
            next_button = await self.browser.page.query_selector('button:has-text("Next")')
            if next_button:
                await next_button.click()
            else:
                await self.browser.page.keyboard.press('Enter')
            
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
                    await self.browser.page.wait_for_selector(indicator, timeout=5000)
                    self.browser.state.logged_in = True
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
            await self.browser.navigate("https://github.com/login")
            await asyncio.sleep(2)
            
            await self.browser.page.fill('input[name="login"]', username)
            await asyncio.sleep(1)
            
            await self.browser.page.fill('input[name="password"]', password)
            await asyncio.sleep(1)
            
            await self.browser.page.click('input[name="commit"]')
            await asyncio.sleep(3)
            
            try:
                await self.browser.page.wait_for_selector('.avatar', timeout=5000)
                self.browser.state.logged_in = True
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
            
            await self.browser.navigate(url)
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
                    username_field = await self.browser.page.wait_for_selector(selector, timeout=2000)
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
                    password_field = await self.browser.page.wait_for_selector(selector, timeout=2000)
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
                    submit_button = await self.browser.page.wait_for_selector(selector, timeout=2000)
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
            current_url = self.browser.page.url
            if current_url != url and 'login' not in current_url.lower():
                self.browser.state.logged_in = True
                return True

            # Check for success indicators
            for selector in success_indicators:
                try:
                    await self.browser.page.wait_for_selector(selector, timeout=2000)
                    self.browser.state.logged_in = True
                    return True
                except:
                    continue

            return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def save_session(self, filename: str):
        """Save current session state to file"""
        session_data = {
            'cookies': self.browser.state.cookies,
            'localStorage': self.browser.state.local_storage,
            'sessionStorage': self.browser.state.session_storage,
            'url': self.browser.state.current_url,
            'logged_in': self.browser.state.logged_in
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f)
        logger.info(f"Session saved to {filename}")

    async def load_session(self, filename: str):
        """Load session state from file"""
        with open(filename) as f:
            session_data = json.load(f)
        
        context = await self.browser.create_new_context()
        await context.add_cookies(session_data['cookies'])
        
        self.browser.page = await context.new_page()
        
        await self.browser.page.evaluate("""
            storage => {
                for (let key in storage.localStorage) {
                    window.localStorage.setItem(key, storage.localStorage[key]);
                }
                for (let key in storage.sessionStorage) {
                    window.sessionStorage.setItem(key, storage.sessionStorage[key]);
                }
            }
        """, session_data)
        
        self.browser.state.cookies = session_data['cookies']
        self.browser.state.local_storage = session_data['localStorage']
        self.browser.state.session_storage = session_data['sessionStorage']
        self.browser.state.current_url = session_data['url']
        self.browser.state.logged_in = session_data['logged_in']
        
        await self.browser.navigate(self.browser.state.current_url)
        logger.info(f"Session loaded from {filename}")

async def run_login_mode():
    """Run login mode as standalone"""
    print("=== LOGIN MODE ===")
    url = input("Enter website URL: ").strip()
    username = input("Enter username/email: ").strip()
    password = input("Enter password: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    async with BrowserCore() as browser:
        login_manager = LoginManager(browser)
        success = await login_manager.login_to_website(url, username, password)
        if success:
            print("Login successful!")
            await browser.take_screenshot("login_success.png")
        else:
            print("Login failed!")

if __name__ == "__main__":
    # Test the login manager
    asyncio.run(run_login_mode())