#!/usr/bin/env python3
import os
from typing import Dict

class Config:
    """Central configuration class for web agent settings"""
    
    def __init__(self):
        """Initialize with default values from environment variables"""
        from dotenv import load_dotenv
        load_dotenv()  # Load .env file
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.browser_timeout = int(os.getenv('BROWSER_TIMEOUT', '30000'))
        self.viewport_width = int(os.getenv('VIEWPORT_WIDTH', '1280'))
        self.viewport_height = int(os.getenv('VIEWPORT_HEIGHT', '800'))
        self.wait_for_network = os.getenv('WAIT_FOR_NETWORK', 'true').lower() == 'true'
        self.screenshot_quality = int(os.getenv('SCREENSHOT_QUALITY', '90'))
        self.disable_automation = os.getenv('DISABLE_AUTOMATION_DETECTION', 'true').lower() == 'true'
        self.keep_browser_open = os.getenv('KEEP_BROWSER_OPEN', 'false').lower() == 'true'
        
        # AI Configuration
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        self.gemini_endpoint = os.getenv('GEMINI_ENDPOINT', 'https://generativelanguage.googleapis.com/v1beta/models/')
        
        # Automation Configuration
        self.automation_mode = os.getenv('AUTOMATION_MODE', 'false').lower() == 'true'
        self.max_automation_steps = int(os.getenv('MAX_AUTOMATION_STEPS', '10'))
        self.automation_delay = int(os.getenv('AUTOMATION_DELAY', '2'))
        self.default_mode = os.getenv('DEFAULT_MODE', 'interactive')

        # Website URLs
        self.website_urls = self._load_website_urls()
        
        # Test configuration
        self.test_url = os.getenv('TEST_URL', 'https://httpbin.org/forms/post')
        self.test_username = os.getenv('TEST_USERNAME', 'test_user')
        self.test_password = os.getenv('TEST_PASSWORD', 'test_pass')

    def _load_website_urls(self) -> Dict[str, str]:
        """Load website URLs from environment variables"""
        return {
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

    def get_website_url(self, website_name: str) -> str:
        """Get URL for a website by name or return input if not found"""
        return self.website_urls.get(website_name.lower(), website_name)