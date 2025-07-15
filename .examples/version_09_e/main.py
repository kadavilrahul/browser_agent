#!/usr/bin/env python3
import asyncio
import argparse
from utils.logger import setup_logger
from utils.config import Config
from utils.models import DataExtractionResult
from start_browser import start_browser
from navigate import navigate_to_url
from extract_data import extract_page_data
from save_data import save_as_json, save_as_csv

logger = setup_logger(__name__)
config = Config()

async def main():
    """Main execution flow for the browser agent"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Web Browser Automation Agent')
        parser.add_argument('url', help='URL to process')
        parser.add_argument('--extract', action='store_true', help='Extract page data')
        parser.add_argument('--screenshot', action='store_true', help='Take screenshot')
        parser.add_argument('--output', choices=['json', 'csv'], default='json', help='Output format')
        args = parser.parse_args()

        # Start browser session
        browser, page, playwright = await start_browser()

        # Navigate to target URL
        # Add https:// if missing
        url = args.url if args.url.startswith(('http://', 'https://')) else f'https://{args.url}'
        nav_result = await navigate_to_url(page, url)
        if not nav_result.success:
            raise Exception(f"Navigation failed: {nav_result.error}")

        # Extract data if requested
        if args.extract:
            data = await extract_page_data(
                page, 
                include_html=True,
                screenshot=args.screenshot
            )
            
            # Save results
            if args.output == 'json':
                save_as_json(data)
            else:
                save_as_csv(data)

        logger.info("Operation completed successfully")

    except Exception as e:
        logger.error("Main execution failed: %s", str(e))
        raise

    finally:
        # Clean up browser instance
        if 'playwright' in locals():
            await playwright.stop()
        elif 'browser' in locals():
            await browser.close()

def run_main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

if __name__ == "__main__":
    run_main()