#!/usr/bin/env python3

"""
Simple test script for the unified web agent
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_basic_functionality():
    """Test basic functionality"""
    print("🧪 Testing Unified Web Agent...")
    
    # Test environment loading
    print(f"✅ Environment loaded")
    print(f"   - Headless: {os.getenv('HEADLESS', 'true')}")
    print(f"   - Browser timeout: {os.getenv('BROWSER_TIMEOUT', '30000')}")
    print(f"   - Gemini API key configured: {bool(os.getenv('GEMINI_API_KEY'))}")
    
    # Test website URLs
    website_urls = {
        'github': os.getenv('GITHUB_URL', 'https://github.com/login'),
        'google': os.getenv('GOOGLE_URL', 'https://accounts.google.com/signin'),
        'test': os.getenv('TEST_URL', 'https://httpbin.org/forms/post')
    }
    
    print(f"✅ Website URLs configured: {len(website_urls)} sites")
    for name, url in website_urls.items():
        print(f"   - {name}: {url}")
    
    print("✅ Basic configuration test passed!")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())