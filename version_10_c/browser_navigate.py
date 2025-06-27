#!/usr/bin/env python3
import asyncio
import os
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

def normalize_url(url):
    """Ensure URL has http protocol prefix"""
    if not re.match(r'^https?://', url):
        return f'http://{url}'
    return url

async def navigate_to_website():
    """Navigate to user-provided website"""
    url = input("Enter website URL (without https://): ").strip()
    url = normalize_url(url)

    DEFAULT_ARGS = {
        'headless': False,
        'args': [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage'
        ]
    }

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(**DEFAULT_ARGS)
    page = await browser.new_page()
    
    try:
        print(f"Navigating to {url}...")
        await page.goto(url, timeout=15000)
        print(f"Successfully loaded: {await page.title()}")
        
        if os.getenv('KEEP_BROWSER_OPEN', 'false').lower() == 'true':
            print("Keeping browser open (KEEP_BROWSER_OPEN=true)")
            print("Press Ctrl+C to exit...")
            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                print("\nClosing browser...")
    finally:
        try:
            if not browser.is_closed():
                await browser.close()
        except Exception as e:
            print(f"Browser close warning: {e}")
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(navigate_to_website())