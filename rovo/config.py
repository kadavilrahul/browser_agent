"""
Configuration management for ROVO Browser Agent
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
            'page_timeout': self._get_int('PAGE_TIMEOUT', 30000),
            
            # AI settings
            'google_api_key': os.getenv('GOOGLE_API_KEY', ''),
            'llm_model': os.getenv('LLM_MODEL', 'gemini-pro'),
            
            # AgentOps settings
            'agentops_api_key': os.getenv('AGENTOPS_API_KEY', ''),
            'enable_monitoring': self._get_bool('ENABLE_MONITORING', False),
            
            # Default settings
            'default_url': os.getenv('DEFAULT_URL', 'https://www.google.com'),
            'verbose': self._get_bool('VERBOSE', True),
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
    
    def get_browser_options(self) -> Dict[str, Any]:
        """Get browser launch options"""
        return {
            'headless': self.get('headless'),
            'args': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
            ]
        }
    
    def get_context_options(self) -> Dict[str, Any]:
        """Get browser context options"""
        return {
            'viewport': {
                'width': self.get('viewport_width'),
                'height': self.get('viewport_height')
            }
        }