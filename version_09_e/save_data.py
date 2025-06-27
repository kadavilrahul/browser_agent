#!/usr/bin/env python3
import json
import csv
import os
from datetime import datetime
from typing import Union, Optional
from utils.logger import setup_logger
from utils.config import Config
from utils.models import DataExtractionResult, NavigationResult, AutomationResult

logger = setup_logger(__name__)
config = Config()

def ensure_data_directory() -> str:
    """Ensure data directory exists and return path"""
    os.makedirs('browser_agent/data', exist_ok=True)
    return 'browser_agent/data'

def save_as_json(data: Union[DataExtractionResult, NavigationResult, AutomationResult], filename: Optional[str] = None) -> str:
    """
    Save data as JSON file
    Args:
        data: Data object to save
        filename: Optional custom filename
    Returns:
        Path to saved file
    """
    try:
        data_dir = ensure_data_directory()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not filename:
            if isinstance(data, DataExtractionResult):
                filename = f"extraction_{timestamp}.json"
            elif isinstance(data, NavigationResult):
                filename = f"navigation_{timestamp}.json"
            else:
                filename = f"automation_{timestamp}.json"

        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data.__dict__, f, indent=2)

        logger.info("Data saved to JSON: %s", filepath)
        return filepath

    except Exception as e:
        logger.error("Failed to save JSON: %s", str(e))
        raise

def save_as_csv(data: Union[DataExtractionResult, NavigationResult], filename: Optional[str] = None) -> str:
    """
    Save data as CSV file
    Args:
        data: Data object to save
        filename: Optional custom filename
    Returns:
        Path to saved file
    """
    try:
        data_dir = ensure_data_directory()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not filename:
            if isinstance(data, DataExtractionResult):
                filename = f"extraction_{timestamp}.csv"
            else:
                filename = f"navigation_{timestamp}.csv"

        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            if isinstance(data, DataExtractionResult):
                # Write header
                writer.writerow(['URL', 'Title', 'Text Content', 'Links Count', 'Images Count', 'Forms Count'])
                # Write data
                writer.writerow([
                    data.url,
                    data.title,
                    data.text_content[:100] + '...' if len(data.text_content) > 100 else data.text_content,
                    len(data.links),
                    len(data.images),
                    len(data.forms)
                ])
            else:
                writer.writerow(['URL', 'Final URL', 'Status Code', 'Success'])
                writer.writerow([
                    data.url,
                    data.final_url,
                    data.status_code,
                    data.success
                ])

        logger.info("Data saved to CSV: %s", filepath)
        return filepath

    except Exception as e:
        logger.error("Failed to save CSV: %s", str(e))
        raise

async def save_screenshot(page, filename: Optional[str] = None) -> str:
    """
    Save page screenshot
    Args:
        page: Pyppeteer page object
        filename: Optional custom filename
    Returns:
        Path to saved screenshot
    """
    try:
        data_dir = ensure_data_directory()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not filename:
            filename = f"screenshot_{timestamp}.png"

        filepath = os.path.join(data_dir, filename)
        await page.screenshot({'path': filepath, 'quality': config.screenshot_quality})

        logger.info("Screenshot saved: %s", filepath)
        return filepath

    except Exception as e:
        logger.error("Failed to save screenshot: %s", str(e))
        raise