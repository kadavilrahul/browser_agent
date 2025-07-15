#!/usr/bin/env python3
import asyncio
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Default configuration values
DEFAULT_VIEWPORT = {'width': 1280, 'height': 720}
DEFAULT_LAUNCH_ARGS = {
    'headless': False,
    'args': [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu'
    ]
}

async def start_browser(headless: Optional[bool] = None) -> tuple:
        """Initialize and return browser resources without keep_open logic"""
    """
    Initialize and return a browser and page instance
    Args:
        headless: Override config headless setting if specified
    Returns:
        Tuple of (browser, page) instances
    """
    try:
        """Initialize browser with Playwright"""
        from playwright.async_api import async_playwright
        
        launch_args = DEFAULT_LAUNCH_ARGS.copy()
        if headless is not None:
            launch_args['headless'] = headless

        print(f"Launching browser with args: {launch_args}")
        playwright = await async_playwright().start()
        
        try:
            browser = await playwright.chromium.launch(**launch_args)
            page = await browser.new_page()

            await page.set_viewport_size(DEFAULT_VIEWPORT)
            print("Browser successfully started")
            return browser, page, playwright

        except Exception as e:
            if 'playwright' in locals():
                await playwright.stop()
            print(f"Failed to start browser: {str(e)}")
            raise

    except Exception as e:
        print(f"Browser initialization failed: {str(e)}")
        raise

def main():
    """Command line entry point for standalone browser launch"""
    import argparse
    parser = argparse.ArgumentParser(description='Launch browser instance')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--keep-open', action='store_true',
        help='Keep browser open until Enter pressed (overrides .env KEEP_BROWSER_OPEN)')
    args = parser.parse_args()

    async def run():
        browser, page, playwright = await start_browser(
            headless=args.headless,
            keep_open=args.keep_open
        )
        # Get final keep_open state from environment if not set by args
        final_keep_open = args.keep_open or os.getenv('KEEP_BROWSER_OPEN', 'false').lower() == 'true'
        print(f"Final keep_open state: {final_keep_open}")
        
        print(f"DEBUG: Starting cleanup (final_keep_open={final_keep_open})")
        try:
            if not final_keep_open:
                print("DEBUG: Closing page and browser")
                await page.close()
                await browser.close()
            print("DEBUG: Stopping playwright")
            await playwright.stop()
        except Exception as e:
            print(f"Cleanup error: {e}")
        finally:
            # Ensure playwright is always stopped
            try:
                print("DEBUG: Final playwright stop attempt")
                await playwright.stop()
            except Exception as e:
                print(f"DEBUG: Final stop error: {e}")

    asyncio.run(run())

if __name__ == "__main__":
    main()