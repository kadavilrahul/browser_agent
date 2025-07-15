#!/usr/bin/env python3
"""
Element Analyzer Module
Handles finding, analyzing, and interacting with page elements
"""

import asyncio
import logging
from typing import List, Any
from datetime import datetime
from browser_core import BrowserCore, ElementInfo, PageAnalysis, logger

# JavaScript for identifying clickable elements
JS_GET_CLICKABLE_ELEMENTS = """
() => {
    // Helper function to check if element is visible
    function isVisible(element) {
        if (!element.getBoundingClientRect) return false;
        const rect = element.getBoundingClientRect();
        return !!(rect.top || rect.bottom || rect.width || rect.height) && 
               window.getComputedStyle(element).visibility !== 'hidden' &&
               window.getComputedStyle(element).display !== 'none' &&
               window.getComputedStyle(element).opacity !== '0';
    }
    
    // Helper function to check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= -100 &&
            rect.left >= -100 &&
            rect.bottom <= (window.innerHeight + 100) &&
            rect.right <= (window.innerWidth + 100)
        );
    }
    
    // Helper function to check if element is interactive
    function isInteractive(element) {
        const tagName = element.tagName.toLowerCase();
        
        // Common interactive elements
        const interactiveTags = ['a', 'button', 'input', 'select', 'textarea', 'details', 'summary'];
        if (interactiveTags.includes(tagName)) return true;
        
        // Check for interactive roles
        const role = element.getAttribute('role');
        const interactiveRoles = ['button', 'link', 'checkbox', 'radio', 'tab', 'menuitem'];
        if (role && interactiveRoles.includes(role)) return true;
        
        // Check for event handlers
        if (element.onclick || 
            element.getAttribute('onclick') || 
            element.getAttribute('ng-click') ||
            element.getAttribute('@click')) return true;
        
        // Check for tabindex
        if (element.getAttribute('tabindex') && element.getAttribute('tabindex') !== '-1') return true;
        
        // Check for contenteditable
        if (element.getAttribute('contenteditable') === 'true') return true;
        
        return false;
    }
    
    // Helper function to get all text from an element
    function getElementText(element) {
        // For input elements, get value or placeholder
        if (element.tagName.toLowerCase() === 'input') {
            return element.value || element.placeholder || '';
        }
        
        // For other elements, get innerText or textContent
        return element.innerText || element.textContent || '';
    }
    
    // Helper function to get XPath
    function getXPath(element) {
        if (!element) return '';
        
        // Use id if available
        if (element.id) {
            return `//*[@id="${element.id}"]`;
        }
        
        // Otherwise build path
        const parts = [];
        while (element && element.nodeType === Node.ELEMENT_NODE) {
            let idx = 0;
            let sibling = element.previousSibling;
            while (sibling) {
                if (sibling.nodeType === Node.ELEMENT_NODE && 
                    sibling.tagName === element.tagName) {
                    idx++;
                }
                sibling = sibling.previousSibling;
            }
            
            const tagName = element.tagName.toLowerCase();
            const pathIndex = idx ? `[${idx + 1}]` : '';
            parts.unshift(`${tagName}${pathIndex}`);
            
            element = element.parentNode;
        }
        
        return '/' + parts.join('/');
    }
    
    // Find all clickable elements
    const clickableElements = [];
    let index = 0;
    
    // Function to process elements recursively
    function processElement(element) {
        if (!element || !isVisible(element)) return;
        
        // Check if element is interactive
        if (isInteractive(element)) {
            // Get element properties
            const tagName = element.tagName.toLowerCase();
            const text = getElementText(element).trim();
            const isInView = isInViewport(element);
            const rect = element.getBoundingClientRect();
            
            // Get attributes
            const attributes = {};
            for (const attr of element.attributes) {
                attributes[attr.name] = attr.value;
            }
            
            // Add to results
            clickableElements.push({
                index: index++,
                tagName,
                text: text.substring(0, 100), // Limit text length
                attributes,
                xpath: getXPath(element),
                isVisible: true,
                isInViewport: isInView,
                boundingBox: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    right: rect.right,
                    bottom: rect.bottom,
                    left: rect.left
                }
            });
        }
        
        // Process children
        for (const child of element.children) {
            processElement(child);
        }
    }
    
    // Start processing from body
    processElement(document.body);
    
    return clickableElements;
}
"""

class ElementAnalyzer:
    """Analyzes and interacts with page elements"""
    
    def __init__(self, browser_core: BrowserCore):
        """Initialize element analyzer with browser core"""
        self.browser = browser_core

    async def find_clickable_elements(self) -> List[ElementInfo]:
        """Find all clickable elements on the current page"""
        if not self.browser.page:
            raise ValueError("No page is open. Call navigate() first.")
        
        elements_data = await self.browser.page.evaluate(JS_GET_CLICKABLE_ELEMENTS)
        
        elements = []
        for data in elements_data:
            element = ElementInfo(
                index=data['index'],
                tag_name=data['tagName'],
                text=data['text'],
                attributes=data['attributes'],
                xpath=data['xpath'],
                is_visible=data['isVisible'],
                is_in_viewport=data['isInViewport'],
                bounding_box=data['boundingBox']
            )
            elements.append(element)
        
        logger.info(f"Found {len(elements)} clickable elements")
        return elements

    async def analyze_page(self, url: str) -> PageAnalysis:
        """Analyze a webpage to find clickable elements"""
        await self.browser.navigate(url)
        
        title = await self.browser.page.title()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        elements = await self.find_clickable_elements()
        
        analysis = PageAnalysis(
            url=url,
            title=title,
            timestamp=timestamp,
            elements=elements
        )
        
        return analysis

    async def click_element(self, element_index: int, elements: List[ElementInfo]) -> bool:
        """Click on a specific element by index"""
        if not self.browser.page:
            return False
        
        element = next((e for e in elements if e.index == element_index), None)
        if not element:
            logger.warning(f"Element with index {element_index} not found")
            return False
        
        try:
            if element.xpath:
                await self.browser.page.click(f"xpath={element.xpath}")
                logger.info(f"Clicked element {element_index} using XPath")
                return True
            
            if 'id' in element.attributes:
                await self.browser.page.click(f"#{element.attributes['id']}")
                logger.info(f"Clicked element {element_index} using ID selector")
                return True
            
            if element.bounding_box:
                x = element.bounding_box['x'] + element.bounding_box['width'] / 2
                y = element.bounding_box['y'] + element.bounding_box['height'] / 2
                await self.browser.page.mouse.click(x, y)
                logger.info(f"Clicked element {element_index} using coordinates")
                return True
            
            logger.warning(f"Could not click element {element_index}")
            return False
        except Exception as e:
            logger.error(f"Error clicking element {element_index}: {e}")
            return False

    async def type_in_element(self, selector: str, text: str) -> bool:
        """Type text in an element specified by selector"""
        if not self.browser.page:
            return False
        
        try:
            await self.browser.page.fill(selector, text)
            logger.info(f"Typed '{text}' in element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Error typing in element {selector}: {e}")
            return False

    async def get_element_text(self, selector: str) -> str:
        """Get text content from an element"""
        if not self.browser.page:
            return ""
        
        try:
            text = await self.browser.page.text_content(selector)
            return text or ""
        except Exception as e:
            logger.error(f"Error getting text from element {selector}: {e}")
            return ""

    async def get_element_attribute(self, selector: str, attribute: str) -> str:
        """Get attribute value from an element"""
        if not self.browser.page:
            return ""
        
        try:
            value = await self.browser.page.get_attribute(selector, attribute)
            return value or ""
        except Exception as e:
            logger.error(f"Error getting attribute {attribute} from element {selector}: {e}")
            return ""

    async def wait_for_element(self, selector: str, timeout: int = 5000) -> bool:
        """Wait for an element to appear"""
        if not self.browser.page:
            return False
        
        try:
            await self.browser.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Element {selector} not found within {timeout}ms: {e}")
            return False

    async def is_element_visible(self, selector: str) -> bool:
        """Check if an element is visible"""
        if not self.browser.page:
            return False
        
        try:
            element = await self.browser.page.query_selector(selector)
            if not element:
                return False
            
            is_visible = await element.is_visible()
            return is_visible
        except Exception as e:
            logger.error(f"Error checking visibility of element {selector}: {e}")
            return False

async def run_scraper_mode(url: str, output: str = None):
    """Run web scraper mode as standalone"""
    print(f"=== SCRAPER MODE ===")
    
    # Validate and fix URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"Auto-corrected URL to: {url}")
    
    print(f"Analyzing: {url}")
    
    try:
        async with BrowserCore() as browser:
            analyzer = ElementAnalyzer(browser)
            analysis = await analyzer.analyze_page(url)
            analysis.print_elements()
            
            # Auto-generate filename if not provided
            if not output:
                output = browser.generate_filename_from_url(url, "elements")
            
            analysis.save_to_file(output)
            print(f"Results saved to {output}")
    except Exception as e:
        print(f"ERROR: Scraper failed - {e}")
        if "Cannot navigate to invalid URL" in str(e):
            print("HINT: Check if the URL is correct and accessible")
        elif "net::ERR_NAME_NOT_RESOLVED" in str(e):
            print("HINT: Check your internet connection or the domain name")
        elif "timeout" in str(e).lower():
            print("HINT: The website is taking too long to load, try again later")
        return False

async def run_navigate_mode(url: str):
    """Run simple navigation mode as standalone"""
    print(f"=== NAVIGATION MODE ===")
    
    # Validate and fix URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"Auto-corrected URL to: {url}")
    
    print(f"Navigating to: {url}")
    
    try:
        async with BrowserCore() as browser:
            await browser.navigate(url)
            await browser.take_screenshot("navigation.png")
            print(f"Successfully navigated to {browser.page.url}")
            print("Screenshot saved as navigation.png")
    except Exception as e:
        print(f"ERROR: Navigation failed - {e}")
        if "Cannot navigate to invalid URL" in str(e):
            print("HINT: Check if the URL is correct and accessible")
        elif "net::ERR_NAME_NOT_RESOLVED" in str(e):
            print("HINT: Check your internet connection or the domain name")
        elif "timeout" in str(e).lower():
            print("HINT: The website is taking too long to load, try again later")
        return False

if __name__ == "__main__":
    # Test the element analyzer
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        asyncio.run(run_scraper_mode(url))
    else:
        print("Usage: python element_analyzer.py <url>")
        print("Example: python element_analyzer.py https://example.com")