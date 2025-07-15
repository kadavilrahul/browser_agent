#!/usr/bin/env python3
import asyncio
from typing import Optional
from utils.logger import setup_logger
from utils.config import Config
from utils.models import DataExtractionResult
from utils.js_helpers import JavaScriptHelpers

logger = setup_logger(__name__)
config = Config()
js = JavaScriptHelpers()

async def extract_page_data(page, include_html: bool = False, screenshot: bool = False) -> DataExtractionResult:
    """
    Extract structured data from current page
    Args:
        page: Pyppeteer page object
        include_html: Whether to include full HTML content
        screenshot: Whether to take screenshot
    Returns:
        DataExtractionResult with extracted data
    """
    try:
        logger.info("Extracting data from page: %s", page.url)
        
        # Extract basic page information
        title = await page.title()
        
        # Execute JavaScript helpers to extract data
        links = await page.evaluate(js.get_all_links())
        images = await page.evaluate(js.get_all_images())
        forms = await page.evaluate(js.get_all_forms())
        metadata = await page.evaluate(js.get_page_metadata())
        
        # Get text content
        text_content = await page.evaluate('document.body.textContent')
        
        # Take screenshot if requested
        screenshot_path = None
        if screenshot:
            screenshot_path = f"screenshots/{page.url.split('//')[-1].replace('/', '_')}.png"
            await page.screenshot({'path': screenshot_path, 'quality': config.screenshot_quality})
            logger.info("Screenshot saved to: %s", screenshot_path)

        # Get HTML if requested
        html_content = None
        if include_html:
            html_content = await page.content()

        return DataExtractionResult(
            url=page.url,
            title=title,
            text_content=text_content.strip(),
            links=links,
            images=images,
            forms=forms,
            metadata=metadata,
            screenshot_path=screenshot_path,
            html_content=html_content
        )

    except Exception as e:
        logger.error("Data extraction failed: %s", str(e))
        return DataExtractionResult(
            url=page.url,
            title="",
            text_content="",
            links=[],
            images=[],
            forms=[],
            metadata={},
            error=str(e)
        )

async def extract_element_data(page, selector: str) -> dict:
    """
    Extract data from specific element
    Args:
        page: Pyppeteer page object
        selector: CSS selector for target element
    Returns:
        Dictionary with element data
    """
    try:
        logger.info("Extracting data from element: %s", selector)
        return await page.evaluate(f'''
            (selector) => {{
                const el = document.querySelector(selector);
                if (!el) return {{ error: 'Element not found' }};
                
                return {{
                    tagName: el.tagName,
                    textContent: el.textContent.trim(),
                    attributes: Array.from(el.attributes).reduce((obj, attr) => {{
                        obj[attr.name] = attr.value;
                        return obj;
                    }}, {{}}),
                    boundingBox: el.getBoundingClientRect().toJSON()
                }}
            }}
        ''', selector)

    except Exception as e:
        logger.error("Element extraction failed: %s", str(e))
        return {'error': str(e)}