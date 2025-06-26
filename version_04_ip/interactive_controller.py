#!/usr/bin/env python3
"""
Interactive Controller Module - Ultra Simplified
Just asks for URL and provides basic browsing functionality
"""

import asyncio
import argparse
import time
from datetime import datetime
from browser_core import BrowserCore, validate_environment, logger
from login_manager import LoginManager
from element_analyzer import ElementAnalyzer

class InteractiveBrowserController:
    """Ultra-simple browser controller"""
    
    def __init__(self, browser_core: BrowserCore):
        self.browser = browser_core
        self.element_analyzer = ElementAnalyzer(browser_core)
        self.running = True
        self.current_elements = []
        
    async def start_interactive_session(self):
        """Start the simple browser session"""
        print("BROWSER READY")
        await self.interactive_loop()
        
    async def interactive_loop(self):
        """Ultra-simple loop - just ask for URL"""
        while self.running:
            try:
                await self.simple_flow()
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                print("\nInput ended, exiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
        self.running = False

    async def simple_flow(self):
        """Ultra-simple flow: URL -> Navigate -> Screenshot -> Show elements -> Click option"""
        print("\n" + "="*40)
        print("WEB BROWSING AGENT")
        print("="*40)
        
        # Show current status
        if hasattr(self.browser, 'page') and self.browser.page:
            print(f"Current: {self.browser.state.current_url}")
        
        # Get URL
        url = input("Enter website URL (or 'exit' to quit): ").strip()
        
        if url.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            self.running = False
            return
        
        if not url:
            print("Please enter a URL")
            return
            
        # Auto-correct URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            # Navigate
            print(f"Going to {url}...")
            await self.browser.navigate(url)
            print("SUCCESS: Page loaded")
            
            # Auto-screenshot
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            await self.browser.take_screenshot(filename)
            print(f"SUCCESS: Screenshot saved: {filename}")
            
            # Auto-find elements
            print("Finding clickable elements...")
            self.current_elements = await self.element_analyzer.find_clickable_elements()
            
            # Save elements to file
            from browser_core import PageAnalysis
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analysis = PageAnalysis(
                url=url,
                title=await self.browser.page.title(),
                timestamp=timestamp,
                elements=self.current_elements
            )
            
            # Generate filename
            filename = self.browser.generate_filename_from_url(url, "elements")
            analysis.save_to_file(filename)
            
            print(f"SUCCESS: Found {len(self.current_elements)} clickable elements")
            print(f"SUCCESS: Elements saved to {filename}")
            
            if self.current_elements:
                # Show elements
                print("\nClickable elements:")
                for i, elem in enumerate(self.current_elements[:10]):
                    text_preview = elem.text[:50] + "..." if len(elem.text) > 50 else elem.text
                    print(f"  [{elem.index}] {text_preview}")
                
                if len(self.current_elements) > 10:
                    print(f"  ... and {len(self.current_elements) - 10} more")
                
                # Click option
                click_choice = input("\nEnter element number to click (or press Enter to continue): ").strip()
                if click_choice.isdigit():
                    element_index = int(click_choice)
                    if 0 <= element_index < len(self.current_elements):
                        element = self.current_elements[element_index]
                        print(f"Clicking: {element.text[:50]}")
                        success = await self.element_analyzer.click_element(element_index, self.current_elements)
                        if success:
                            print("SUCCESS: Clicked successfully!")
                            await asyncio.sleep(2)
                        else:
                            print("ERROR: Click failed")
                    else:
                        print("Invalid element number")
            
        except Exception as e:
            print(f"Error: {e}")

# Main functions
async def run_interactive_mode():
    """Run interactive browser mode"""
    async with BrowserCore() as browser:
        await browser.new_page()
        controller = InteractiveBrowserController(browser)
        await controller.start_interactive_session()

async def main():
    """Main function"""
    if not validate_environment():
        print("Warning: Environment validation failed.")
    
    parser = argparse.ArgumentParser(description="Web Browsing Agent")
    parser.add_argument("--mode", choices=["interactive", "login", "scraper", "navigate"], 
                       help="Operation mode")
    parser.add_argument("--url", help="URL for navigation or scraping")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        await run_interactive_mode()
    elif args.mode == "login":
        from login_manager import run_login_mode
        await run_login_mode()
    elif args.mode == "scraper":
        if not args.url:
            print("Error: --url required for scraper mode")
            return
        from element_analyzer import run_scraper_mode
        await run_scraper_mode(args.url)
    elif args.mode == "navigate":
        if not args.url:
            print("Error: --url required for navigate mode")
            return
        from element_analyzer import run_navigate_mode
        await run_navigate_mode(args.url)
    else:
        # Default to interactive mode
        await run_interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())