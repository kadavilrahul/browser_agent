"""
Element detection and interaction for Browser Agent v12_p
Handles finding, analyzing, and interacting with page elements
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
from playwright.async_api import Page, Locator
from config import Config

class ElementManager:
    """Manages element detection, analysis, and interaction"""
    
    def __init__(self, config: Config, page: Page):
        """Initialize element manager"""
        self.config = config
        self.page = page
        self.last_elements: List[Dict[str, Any]] = []
    
    async def find_clickable_elements(self) -> List[Dict[str, Any]]:
        """Find all clickable elements on the current page"""
        if not self.page:
            return []
        
        try:
            # JavaScript to find clickable elements
            script = """
            () => {
                const clickableSelectors = [
                    'a[href]', 'button', 'input[type="button"]', 'input[type="submit"]',
                    'input[type="reset"]', '[onclick]', '[role="button"]', 
                    'select', 'input[type="checkbox"]', 'input[type="radio"]',
                    '.btn', '.button', '[tabindex="0"]'
                ];
                
                const elements = [];
                const seen = new Set();
                
                clickableSelectors.forEach(selector => {
                    try {
                        document.querySelectorAll(selector).forEach((el, index) => {
                            if (seen.has(el)) return;
                            seen.add(el);
                            
                            const rect = el.getBoundingClientRect();
                            if (rect.width === 0 || rect.height === 0) return;
                            
                            const computedStyle = window.getComputedStyle(el);
                            if (computedStyle.visibility === 'hidden' || 
                                computedStyle.display === 'none') return;
                            
                            const text = (el.textContent || el.innerText || 
                                         el.getAttribute('aria-label') || 
                                         el.getAttribute('title') || 
                                         el.getAttribute('alt') || '').trim();
                            
                            elements.push({
                                tag: el.tagName.toLowerCase(),
                                text: text.substring(0, 100),
                                id: el.id || '',
                                class: el.className || '',
                                href: el.href || '',
                                type: el.type || '',
                                value: el.value || '',
                                x: Math.round(rect.left),
                                y: Math.round(rect.top),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                selector: selector,
                                index: elements.length
                            });
                        });
                    } catch (e) {
                        console.warn('Error with selector:', selector, e);
                    }
                });
                
                return elements.slice(0, 50); // Limit results
            }
            """
            
            elements = await self.page.evaluate(script)
            
            # Add enhanced metadata
            for i, element in enumerate(elements):
                element['element_id'] = i
                element['clickable'] = True
                element['description'] = self._generate_description(element)
            
            self.last_elements = elements
            
            if self.config.get('verbose'):
                print(f"Found {len(elements)} clickable elements")
            
            return elements
            
        except Exception as e:
            print(f"Error finding elements: {e}")
            return []
    
    def _generate_description(self, element: Dict[str, Any]) -> str:
        """Generate human-readable description of element"""
        tag = element.get('tag', '')
        text = element.get('text', '')
        element_type = element.get('type', '')
        href = element.get('href', '')
        
        if tag == 'a' and href:
            return f"Link: {text or href}"
        elif tag == 'button':
            return f"Button: {text or 'unnamed'}"
        elif tag == 'input':
            if element_type in ['submit', 'button']:
                return f"Button ({element_type}): {text or element.get('value', 'unnamed')}"
            elif element_type in ['checkbox', 'radio']:
                return f"{element_type.title()}: {text or 'unnamed'}"
            else:
                return f"Input ({element_type}): {text or 'unnamed'}"
        elif tag == 'select':
            return f"Dropdown: {text or 'unnamed'}"
        else:
            return f"{tag.title()}: {text or 'unnamed'}"
    
    async def click_element(self, element_id: int) -> bool:
        """Click element by ID with multiple fallback strategies"""
        if not self.last_elements or element_id >= len(self.last_elements):
            print(f"Invalid element ID: {element_id}")
            return False
        
        element = self.last_elements[element_id]
        
        try:
            # Strategy 1: Try clicking by coordinates
            success = await self._click_by_coordinates(element)
            if success:
                if self.config.get('verbose'):
                    print(f"Clicked element {element_id} by coordinates")
                return True
            
            # Strategy 2: Try clicking by selector
            success = await self._click_by_selector(element)
            if success:
                if self.config.get('verbose'):
                    print(f"Clicked element {element_id} by selector")
                return True
            
            # Strategy 3: Try clicking by text content
            success = await self._click_by_text(element)
            if success:
                if self.config.get('verbose'):
                    print(f"Clicked element {element_id} by text")
                return True
            
            print(f"Failed to click element {element_id}: {element.get('description', 'unknown')}")
            return False
            
        except Exception as e:
            print(f"Error clicking element {element_id}: {e}")
            return False
    
    async def _click_by_coordinates(self, element: Dict[str, Any]) -> bool:
        """Click element by coordinates"""
        try:
            x = element.get('x', 0) + element.get('width', 0) // 2
            y = element.get('y', 0) + element.get('height', 0) // 2
            
            await self.page.mouse.click(x, y, timeout=self.config.get('click_timeout'))
            return True
        except:
            return False
    
    async def _click_by_selector(self, element: Dict[str, Any]) -> bool:
        """Click element by CSS selector"""
        try:
            selector = element.get('selector', '')
            if not selector:
                return False
            
            # Try to build a more specific selector
            specific_selector = self._build_specific_selector(element)
            
            if specific_selector:
                locator = self.page.locator(specific_selector).first
            else:
                locator = self.page.locator(selector).first
            
            await locator.click(timeout=self.config.get('click_timeout'))
            return True
        except:
            return False
    
    async def _click_by_text(self, element: Dict[str, Any]) -> bool:
        """Click element by text content"""
        try:
            text = element.get('text', '').strip()
            if not text or len(text) < 2:
                return False
            
            # Try different text-based selectors
            selectors = [
                f"text='{text}'",
                f"text={text}",
                f"[aria-label='{text}']",
                f"[title='{text}']"
            ]
            
            for selector in selectors:
                try:
                    locator = self.page.locator(selector).first
                    await locator.click(timeout=self.config.get('click_timeout'))
                    return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def _build_specific_selector(self, element: Dict[str, Any]) -> Optional[str]:
        """Build a more specific CSS selector for element"""
        try:
            tag = element.get('tag', '')
            element_id = element.get('id', '')
            class_name = element.get('class', '')
            
            if element_id:
                return f"#{element_id}"
            
            if class_name and ' ' not in class_name:
                return f"{tag}.{class_name}"
            
            if element.get('type'):
                return f"{tag}[type='{element['type']}']"
            
            return None
        except:
            return None
    
    async def export_elements(self, filename: Optional[str] = None) -> str:
        """Export found elements to JSON file"""
        if not filename:
            filename = self.config.get('elements_file')
        
        filepath = os.path.join(self.config.get('output_dir'), filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.last_elements, f, indent=2, ensure_ascii=False)
            
            if self.config.get('verbose'):
                print(f"Elements exported to: {filepath}")
            
            return filepath
        except Exception as e:
            print(f"Error exporting elements: {e}")
            return ""
    
    def get_element_summary(self) -> List[str]:
        """Get human-readable summary of found elements"""
        summary = []
        for i, element in enumerate(self.last_elements):
            summary.append(f"{i}: {element.get('description', 'Unknown element')}")
        return summary
    
    def get_element_count(self) -> int:
        """Get count of found elements"""
        return len(self.last_elements)
    
    def get_element_by_id(self, element_id: int) -> Optional[Dict[str, Any]]:
        """Get element data by ID"""
        if 0 <= element_id < len(self.last_elements):
            return self.last_elements[element_id]
        return None