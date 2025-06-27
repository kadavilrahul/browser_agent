#!/usr/bin/env python3
import asyncio
import argparse
from typing import Optional
from utils.logger import setup_logger
from utils.config import Config
from utils.models import NavigationResult
from start_browser import start_browser

logger = setup_logger(__name__)
config = Config()

async def navigate_to_url(page, url: str, wait_for_network: Optional[bool] = None) -> NavigationResult:
    """
    Navigate to a URL and wait for page to load
    Args:
        page: Pyppeteer page object
        url: URL to navigate to
        wait_for_network: Override config setting if specified
    Returns:
        NavigationResult with operation details
    """
    try:
        should_wait = wait_for_network if wait_for_network is not None else config.wait_for_network
        website_url = config.get_website_url(url)
        
        logger.info("Navigating to URL: %s", website_url)
        response = await page.goto(
            website_url,
            wait_until="networkidle" if should_wait else "domcontentloaded",
            timeout=config.browser_timeout
        )

        final_url = page.url
        status_code = response.status if response else 200
        
        logger.info("Navigation successful - Final URL: %s, Status: %d", final_url, status_code)
        return NavigationResult(
            url=website_url,
            success=True,
            final_url=final_url,
            status_code=status_code
        )

    except Exception as e:
        logger.error("Navigation failed for URL %s: %s", url, str(e))
        return NavigationResult(
            url=url,
            success=False,
            final_url=page.url if 'page' in locals() else '',
            status_code=0,
            error=str(e)
        )

async def standalone_navigate(url: str):
    """Standalone navigation function that handles browser lifecycle"""
    logger.debug(f"Starting navigation with keep_open={config.keep_browser_open}")
    browser, page, playwright = await start_browser(headless=False, keep_open=config.keep_browser_open)
    try:
        result = await navigate_to_url(page, url)
        print(f"Navigation result: {result.__dict__}")
        logger.debug(f"Navigation complete, keep_open={config.keep_browser_open}")
        return result
    except Exception as e:
        logger.error(f"Navigation failed: {str(e)}")
        raise
    finally:
        logger.debug(f"Finalizing - keep_open={config.keep_browser_open}")
        try:
            if not config.keep_browser_open:
                logger.debug("Closing page and browser")
                if 'page' in locals():
                    await page.close()
                if 'browser' in locals():
                    await browser.close()
                logger.debug("Stopping playwright")
                await playwright.stop()
            else:
                logger.debug("Keeping browser open per config")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

def main():
    """Command line entry point"""
    parser = argparse.ArgumentParser(description='Standalone URL navigation')
    parser.add_argument('url', help='URL to navigate to')
    args = parser.parse_args()

    # Create new event loop policy to prevent subprocess transport errors
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(standalone_navigate(args.url))
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
    finally:
        # Give async operations time to complete
        pending = asyncio.all_tasks(loop)
        if pending:
            loop.run_until_complete(asyncio.wait(pending, timeout=1.0))
        loop.close()

if __name__ == "__main__":
    main()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")

async def reload_page(page) -> NavigationResult:
    """
    Reload current page
    Args:
        page: Pyppeteer page object
    Returns:
        NavigationResult with operation details
    """
    try:
        current_url = page.url
        logger.info("Reloading page: %s", current_url)
        response = await page.reload(wait_until="networkidle", timeout=config.browser_timeout)
        
        logger.info("Page reload successful")
        return NavigationResult(
            url=current_url,
            success=True,
            final_url=page.url,
            status_code=response.status if response else 200
        )

    except Exception as e:
        logger.error("Page reload failed: %s", str(e))
        return NavigationResult(
            url=current_url,
            success=False,
            final_url=page.url,
            status_code=0,
            error=str(e)
        )