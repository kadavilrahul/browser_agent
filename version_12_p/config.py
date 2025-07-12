"""
Configuration management for Browser Agent v12_p
Handles environment variables, defaults, and browser settings
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class Config:
    """Configuration manager for browser agent settings"""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration with optional custom env file"""
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables with defaults"""
        return {
            # Browser settings
            'headless': self._get_bool('HEADLESS', True),
            'browser_type': os.getenv('BROWSER_TYPE', 'chromium'),
            'viewport_width': self._get_int('VIEWPORT_WIDTH', 1280),
            'viewport_height': self._get_int('VIEWPORT_HEIGHT', 720),
            'user_agent': os.getenv('USER_AGENT', None),
            
            # Timeout settings
            'page_timeout': self._get_int('PAGE_TIMEOUT', 30000),
            'element_timeout': self._get_int('ELEMENT_TIMEOUT', 5000),
            'navigation_timeout': self._get_int('NAVIGATION_TIMEOUT', 30000),
            
            # Screenshot settings
            'screenshot_dir': os.getenv('SCREENSHOT_DIR', 'screenshots'),
            'screenshot_quality': self._get_int('SCREENSHOT_QUALITY', 90),
            'auto_screenshot': self._get_bool('AUTO_SCREENSHOT', True),
            
            # Element detection settings
            'element_selector_timeout': self._get_int('ELEMENT_SELECTOR_TIMEOUT', 2000),
            'click_timeout': self._get_int('CLICK_TIMEOUT', 3000),
            'max_elements': self._get_int('MAX_ELEMENTS', 50),
            
            # Output settings
            'output_dir': os.getenv('OUTPUT_DIR', 'output'),
            'elements_file': os.getenv('ELEMENTS_FILE', 'elements.json'),
            'verbose': self._get_bool('VERBOSE', False),
            
            # Default URL
            'default_url': os.getenv('DEFAULT_URL', 'https://www.google.com'),
            
            # Login settings
            'demo_mode': self._get_bool('DEMO_MODE', True),
            'allow_real_login': self._get_bool('ALLOW_REAL_LOGIN', False),
            'max_login_attempts': self._get_int('MAX_LOGIN_ATTEMPTS', 3),
            
            # Gmail credentials (for testing only)
            'gmail_email': os.getenv('GMAIL_EMAIL', ''),
            'gmail_password': os.getenv('GMAIL_PASSWORD', ''),
            'email_recipient': os.getenv('EMAIL_RECIPIENT', ''),
            'email_subject': os.getenv('EMAIL_SUBJECT', 'Test Email'),
            'email_body': os.getenv('EMAIL_BODY', 'Test message'),
        }
    
    def _get_bool(self, key: str, default: bool) -> bool:
        """Get boolean value from environment with default"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _get_int(self, key: str, default: int) -> int:
        """Get integer value from environment with default"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
    
    def get_browser_options(self) -> Dict[str, Any]:
        """Get browser launch options"""
        options = {
            'headless': self.get('headless'),
            'args': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
            ]
        }
        
        if self.get('user_agent'):
            options['args'].append(f'--user-agent={self.get("user_agent")}')
        
        return options
    
    def get_context_options(self) -> Dict[str, Any]:
        """Get browser context options"""
        return {
            'viewport': {
                'width': self.get('viewport_width'),
                'height': self.get('viewport_height')
            },
            'user_agent': self.get('user_agent'),
        }
    
    def get_page_options(self) -> Dict[str, Any]:
        """Get page-specific options"""
        return {
            'timeout': self.get('page_timeout'),
            'wait_until': 'domcontentloaded'
        }
    
    def __str__(self) -> str:
        """String representation of config"""
        return f"Config(headless={self.get('headless')}, browser={self.get('browser_type')})"