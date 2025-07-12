"""
Login Manager for Browser Agent v12_p
Handles universal login functionality with enhanced safety controls
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from config import Config
from browser import BrowserManager

@dataclass
class LoginSession:
    """Maintains login session state"""
    logged_in: bool = False
    current_url: str = ""
    username: str = ""
    login_timestamp: Optional[str] = None
    cookies: Dict = field(default_factory=dict)
    local_storage: Dict = field(default_factory=dict)
    session_storage: Dict = field(default_factory=dict)

class LoginManager:
    """Manages login functionality with safety controls"""
    
    def __init__(self, config: Config, browser: BrowserManager):
        """Initialize login manager"""
        self.config = config
        self.browser = browser
        self.session = LoginSession()
        
        # Enhanced safety controls
        self.demo_mode = config.get('demo_mode', True)
        self.allow_real_login = config.get('allow_real_login', False)
        self.max_login_attempts = config.get('max_login_attempts', 3)
        self.login_attempts = 0
        
        # Common login selectors - enhanced from v07_c
        self.login_selectors = {
            'username': [
                'input[type="email"]',
                'input[type="text"][name*="email"]',
                'input[type="text"][name*="username"]',
                'input[type="text"][name*="login"]',
                'input[name="username"]',
                'input[name="email"]',
                'input[name="login"]',
                'input[id="email"]',
                'input[id="username"]',
                'input[id="login"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="username" i]'
            ],
            'password': [
                'input[type="password"]',
                'input[name="password"]',
                'input[id="password"]',
                'input[placeholder*="password" i]'
            ],
            'submit': [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'button:has-text("Continue")',
                'button:has-text("Next")',
                'input[name="commit"]',
                'button[data-testid*="login"]',
                'button[id*="submit"]'
            ]
        }
        
        # Success indicators for login verification
        self.success_indicators = [
            '.avatar', '.user-avatar', '.profile-pic',
            'a[href*="logout"]', 'a[href*="signout"]',
            '.logout-button', '.user-menu', '.dashboard',
            '[data-testid*="avatar"]', '[data-testid*="user"]',
            '.account-menu', '.user-profile'
        ]
    
    async def attempt_login(self, url: str, username: str, password: str) -> Dict[str, Any]:
        """Attempt login with safety controls"""
        result = {
            'success': False,
            'message': '',
            'demo_mode': self.demo_mode,
            'attempts': self.login_attempts + 1,
            'timestamp': datetime.now().isoformat()
        }
        
        # Safety check - prevent real login if demo mode enabled
        if self.demo_mode:
            return await self._demo_login(url, username, password, result)
        
        # Safety check - verify real login is allowed
        if not self.allow_real_login:
            result['message'] = 'Real login disabled for safety. Enable with allow_real_login=true'
            return result
        
        # Safety check - maximum attempts
        if self.login_attempts >= self.max_login_attempts:
            result['message'] = f'Maximum login attempts ({self.max_login_attempts}) exceeded'
            return result
        
        self.login_attempts += 1
        
        try:
            # Navigate to login page
            nav_success = await self.browser.navigate(url)
            if not nav_success:
                result['message'] = f'Failed to navigate to {url}'
                return result
            
            # Attempt login
            success = await self._perform_login(username, password)
            
            if success:
                self.session.logged_in = True
                self.session.current_url = self.browser.get_current_url()
                self.session.username = username
                self.session.login_timestamp = datetime.now().isoformat()
                
                result['success'] = True
                result['message'] = 'Login successful'
                
                # Save session state
                await self._capture_session_state()
                
                if self.config.get('verbose'):
                    print(f"✅ Login successful for {username}")
            else:
                result['message'] = 'Login failed - credentials or page structure'
                
        except Exception as e:
            result['message'] = f'Login error: {str(e)}'
            if self.config.get('verbose'):
                print(f"❌ Login error: {e}")
        
        return result
    
    async def _demo_login(self, url: str, username: str, password: str, result: Dict) -> Dict[str, Any]:
        """Demonstrate login process without actually logging in"""
        if self.config.get('verbose'):
            print("🎭 DEMO MODE: Simulating login process")
        
        try:
            # Navigate to demonstrate detection
            nav_success = await self.browser.navigate(url)
            if not nav_success:
                result['message'] = f'Failed to navigate to {url}'
                return result
            
            # Analyze login form without filling
            form_analysis = await self._analyze_login_form()
            
            result['success'] = True
            result['message'] = 'Demo login completed successfully'
            result['form_analysis'] = form_analysis
            result['demo_actions'] = [
                f'Would fill username field with: {username}',
                f'Would fill password field with: ***hidden***',
                'Would click submit button',
                'Would verify login success'
            ]
            
            if self.config.get('verbose'):
                print("✅ Demo login analysis completed")
                
        except Exception as e:
            result['message'] = f'Demo error: {str(e)}'
        
        return result
    
    async def _perform_login(self, username: str, password: str) -> bool:
        """Perform actual login (only when safety controls allow)"""
        if not self.browser.page:
            return False
        
        try:
            # Find username field
            username_field = await self._find_field('username')
            if not username_field:
                if self.config.get('verbose'):
                    print("❌ Could not find username field")
                return False
            
            await username_field.fill(username)
            await asyncio.sleep(1)
            
            # Find password field
            password_field = await self._find_field('password')
            if not password_field:
                if self.config.get('verbose'):
                    print("❌ Could not find password field")
                return False
            
            await password_field.fill(password)
            await asyncio.sleep(1)
            
            # Submit form
            submit_success = await self._submit_login_form(password_field)
            if not submit_success:
                if self.config.get('verbose'):
                    print("❌ Could not submit login form")
                return False
            
            # Wait for page response
            await asyncio.sleep(3)
            
            # Verify login success
            return await self._verify_login_success()
            
        except Exception as e:
            if self.config.get('verbose'):
                print(f"❌ Login performance error: {e}")
            return False
    
    async def _find_field(self, field_type: str) -> Optional[Any]:
        """Find form field by type using multiple selectors"""
        if field_type not in self.login_selectors:
            return None
        
        for selector in self.login_selectors[field_type]:
            try:
                field = await self.browser.page.wait_for_selector(
                    selector, 
                    timeout=self.config.get('element_timeout', 2000)
                )
                if field:
                    return field
            except:
                continue
        
        return None
    
    async def _submit_login_form(self, password_field) -> bool:
        """Submit login form using button or Enter key"""
        # Try to find and click submit button
        submit_button = await self._find_field('submit')
        if submit_button:
            try:
                await submit_button.click()
                return True
            except:
                pass
        
        # Fallback to Enter key press
        try:
            await password_field.press('Enter')
            return True
        except:
            return False
    
    async def _verify_login_success(self) -> bool:
        """Verify login success using multiple indicators"""
        current_url = self.browser.page.url
        
        # Check URL change (not on login page anymore)
        if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
            return True
        
        # Check for success indicator elements
        for selector in self.success_indicators:
            try:
                await self.browser.page.wait_for_selector(
                    selector, 
                    timeout=self.config.get('element_timeout', 2000)
                )
                return True
            except:
                continue
        
        return False
    
    async def _analyze_login_form(self) -> Dict[str, Any]:
        """Analyze login form structure for demo mode"""
        analysis = {
            'form_detected': False,
            'username_field': False,
            'password_field': False,
            'submit_button': False,
            'field_count': 0,
            'selectors_found': []
        }
        
        try:
            # Check for username field
            for selector in self.login_selectors['username']:
                try:
                    field = await self.browser.page.wait_for_selector(selector, timeout=500)
                    if field:
                        analysis['username_field'] = True
                        analysis['selectors_found'].append(f'username: {selector}')
                        break
                except:
                    continue
            
            # Check for password field
            for selector in self.login_selectors['password']:
                try:
                    field = await self.browser.page.wait_for_selector(selector, timeout=500)
                    if field:
                        analysis['password_field'] = True
                        analysis['selectors_found'].append(f'password: {selector}')
                        break
                except:
                    continue
            
            # Check for submit button
            for selector in self.login_selectors['submit']:
                try:
                    button = await self.browser.page.wait_for_selector(selector, timeout=500)
                    if button:
                        analysis['submit_button'] = True
                        analysis['selectors_found'].append(f'submit: {selector}')
                        break
                except:
                    continue
            
            # Overall form detection
            analysis['form_detected'] = (analysis['username_field'] and 
                                       analysis['password_field'] and 
                                       analysis['submit_button'])
            
            analysis['field_count'] = len(analysis['selectors_found'])
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _capture_session_state(self):
        """Capture current session state for persistence"""
        try:
            # Get cookies
            cookies = await self.browser.context.cookies()
            self.session.cookies = {cookie['name']: cookie['value'] for cookie in cookies}
            
            # Get local and session storage
            storage_data = await self.browser.page.evaluate("""
                () => {
                    const localStorage = {};
                    const sessionStorage = {};
                    
                    for (let i = 0; i < window.localStorage.length; i++) {
                        const key = window.localStorage.key(i);
                        localStorage[key] = window.localStorage.getItem(key);
                    }
                    
                    for (let i = 0; i < window.sessionStorage.length; i++) {
                        const key = window.sessionStorage.key(i);
                        sessionStorage[key] = window.sessionStorage.getItem(key);
                    }
                    
                    return { localStorage, sessionStorage };
                }
            """)
            
            self.session.local_storage = storage_data.get('localStorage', {})
            self.session.session_storage = storage_data.get('sessionStorage', {})
            
        except Exception as e:
            if self.config.get('verbose'):
                print(f"Warning: Could not capture session state: {e}")
    
    async def save_session(self, filename: str = None) -> str:
        """Save current session to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.json"
        
        filepath = os.path.join(self.config.get('output_dir'), filename)
        
        session_data = {
            'logged_in': self.session.logged_in,
            'current_url': self.session.current_url,
            'username': self.session.username,
            'login_timestamp': self.session.login_timestamp,
            'cookies': self.session.cookies,
            'local_storage': self.session.local_storage,
            'session_storage': self.session.session_storage,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            if self.config.get('verbose'):
                print(f"📄 Session saved to: {filepath}")
            
            return filepath
        except Exception as e:
            if self.config.get('verbose'):
                print(f"❌ Failed to save session: {e}")
            return ""
    
    def is_logged_in(self) -> bool:
        """Check if currently logged in"""
        return self.session.logged_in
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            'logged_in': self.session.logged_in,
            'username': self.session.username,
            'current_url': self.session.current_url,
            'login_timestamp': self.session.login_timestamp,
            'demo_mode': self.demo_mode,
            'attempts_made': self.login_attempts,
            'max_attempts': self.max_login_attempts
        }