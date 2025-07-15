"""
Agent tools for ROVO Browser Agent
"""
from typing import Any, Dict, List
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from browser_manager import BrowserManager

class NavigationTool(BaseTool):
    name: str = "navigate_to_url"
    description: str = "Navigate browser to a specified URL. Input should be a valid URL string."
    browser_manager: BrowserManager = Field(exclude=True)
    
    def __init__(self, browser_manager: BrowserManager):
        super().__init__()
        self.browser_manager = browser_manager
    
    def _run(self, url: str) -> str:
        """Navigate to URL"""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            success = loop.run_until_complete(self.browser_manager.navigate(url))
            
            if success:
                return f"Successfully navigated to {url}"
            else:
                return f"Failed to navigate to {url}"
                
        except Exception as e:
            return f"Navigation error: {str(e)}"

class ElementDetectionTool(BaseTool):
    name: str = "find_clickable_elements"
    description: str = "Find all clickable elements on the current page. Returns a list of elements with their properties."
    browser_manager: BrowserManager = Field(exclude=True)
    
    def __init__(self, browser_manager: BrowserManager):
        super().__init__()
        self.browser_manager = browser_manager
    
    def _run(self, input_str: str = "") -> str:
        """Find clickable elements"""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            elements = loop.run_until_complete(self.browser_manager.find_clickable_elements())
            
            if not elements:
                return "No clickable elements found on the page"
            
            result = f"Found {len(elements)} clickable elements:\n"
            for elem in elements[:10]:  # Limit output
                result += f"  {elem['index']}: {elem['tag']} - {elem['text'][:50]}\n"
            
            # Store elements for later use
            self.browser_manager._last_elements = elements
            
            return result
            
        except Exception as e:
            return f"Element detection error: {str(e)}"

class ClickTool(BaseTool):
    name: str = "click_element"
    description: str = "Click an element by its index number. Input should be the element index from find_clickable_elements."
    browser_manager: BrowserManager = Field(exclude=True)
    
    def __init__(self, browser_manager: BrowserManager):
        super().__init__()
        self.browser_manager = browser_manager
    
    def _run(self, element_index: str) -> str:
        """Click element by index"""
        try:
            import asyncio
            
            # Get stored elements
            elements = getattr(self.browser_manager, '_last_elements', [])
            if not elements:
                return "No elements found. Please run find_clickable_elements first."
            
            # Parse index
            try:
                index = int(element_index)
            except ValueError:
                return f"Invalid index: {element_index}. Please provide a number."
            
            # Check bounds
            if index < 0 or index >= len(elements):
                return f"Index {index} out of range. Available: 0-{len(elements)-1}"
            
            # Click element
            loop = asyncio.get_event_loop()
            success = loop.run_until_complete(self.browser_manager.click_element(elements[index]))
            
            if success:
                return f"Successfully clicked element {index}: {elements[index]['text'][:50]}"
            else:
                return f"Failed to click element {index}"
                
        except Exception as e:
            return f"Click error: {str(e)}"

class ScreenshotTool(BaseTool):
    name: str = "take_screenshot"
    description: str = "Take a screenshot of the current page. Input can be filename (optional)."
    browser_manager: BrowserManager = Field(exclude=True)
    
    def __init__(self, browser_manager: BrowserManager):
        super().__init__()
        self.browser_manager = browser_manager
    
    def _run(self, filename: str = "screenshot.png") -> str:
        """Take screenshot"""
        try:
            import asyncio
            import time
            
            # Generate unique filename if not provided
            if filename == "screenshot.png":
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            loop = asyncio.get_event_loop()
            success = loop.run_until_complete(self.browser_manager.take_screenshot(filename))
            
            if success:
                return f"Screenshot saved as {filename}"
            else:
                return "Failed to take screenshot"
                
        except Exception as e:
            return f"Screenshot error: {str(e)}"

class PageInfoTool(BaseTool):
    name: str = "get_page_info"
    description: str = "Get information about the current page (title, URL, status)."
    browser_manager: BrowserManager = Field(exclude=True)
    
    def __init__(self, browser_manager: BrowserManager):
        super().__init__()
        self.browser_manager = browser_manager
    
    def _run(self, input_str: str = "") -> str:
        """Get page information"""
        try:
            import asyncio
            
            loop = asyncio.get_event_loop()
            info = loop.run_until_complete(self.browser_manager.get_page_info())
            
            if "error" in info:
                return f"Error getting page info: {info['error']}"
            
            return f"Page Title: {info['title']}\nURL: {info['url']}\nStatus: {info['status']}"
            
        except Exception as e:
            return f"Page info error: {str(e)}"