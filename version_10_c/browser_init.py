#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def init_browser():
    """Initialize browser with Playwright and keep open if configured"""
    # Browser launch configuration
    DEFAULT_ARGS = {
        'headless': False,  # Run with visible browser window
        'args': [
            # Required for Linux environments:
            '--no-sandbox',
            '--disable-setuid-sandbox',  # Security setting for Linux
            
            # Prevent /dev/shm issues in Docker/CI environments:
            '--disable-dev-shm-usage'
        ]
    }

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(**DEFAULT_ARGS)
    page = await browser.new_page()
    await page.set_viewport_size({'width': 1280, 'height': 720})

    print("Browser successfully initialized")
    keep_open = os.getenv('KEEP_BROWSER_OPEN', 'false').lower() == 'true'
    
    try:
        if keep_open:
            print("Keeping browser open (KEEP_BROWSER_OPEN=true)")
            print("Press Ctrl+C to exit...")
            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                print("\nClosing browser...")
        else:
            await browser.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(init_browser())