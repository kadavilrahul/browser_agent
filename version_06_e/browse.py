import sys
import asyncio
import json
from playwright.async_api import async_playwright, Page
import time
from urllib.parse import urlparse
import argparse

class BrowserCore:
    def __init__(self, **kwargs):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.element_analyzer = None
        self.headless = kwargs.get('headless', True)

    async def start(self):
        if self.browser:
            return
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.element_analyzer = ElementAnalyzer(self.page)

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url):
        await self.page.goto(url)

    async def click_element(self, selector):
        if not self.page:
            print("No page loaded")
            return
        await self.page.click(selector)

    async def type_into_element(self, selector, text):
        if not self.page:
            print("No page loaded")
            return
        await self.page.fill(selector, text)

    async def scroll(self, direction):
        if not self.page:
            print("No page loaded")
            return
        if direction == "down":
            await self.page.evaluate("window.scrollBy(0, window.innerHeight)")
        elif direction == "up":
            await self.page.evaluate("window.scrollBy(0, -window.innerHeight)")
        else:
            # For mouse wheel scrolling
            await self.page.mouse.wheel(0, 300 if direction == "down" else -300)

    async def go_back(self):
        if self.page:
            await self.page.go_back()
            await self.page.wait_for_load_state('networkidle')

    async def read_element_text(self, selector):
        if not self.page:
            print("No page loaded")
            return
        return await self.page.text_content(selector)

    async def get_page_content(self):
        if not self.page:
            print("No page loaded")
            return
        return await self.page.content()

class ElementAnalyzer:
    def __init__(self, page: Page):
        self.page = page

    async def find_clickable_elements(self):
        # Expanded selector to catch more clickable elements
        elements = await self.page.query_selector_all(
            'button, a, input[type="submit"], input[type="button"], input[type="checkbox"], '
            'input[type="radio"], select, [role="button"], [role="link"], '
            '[onclick], [ng-click], [data-click], [tabindex]:not([tabindex="-1"])'
        )

        # Filter out hidden elements
        visible_elements = []
        for element in elements:
            try:
                is_visible = await element.is_visible()
                if is_visible:
                    visible_elements.append(element)
            except:
                # If we can't check visibility, include it anyway
                visible_elements.append(element)

        return visible_elements

    async def get_element_details(self, element):
        tag = await element.evaluate('element => element.tagName')

        # Try different methods to get text content
        text = ""
        try:
            text = await element.inner_text()
        except:
            try:
                text = await element.text_content()
            except:
                try:
                    # For input elements, get the value attribute
                    text = await element.get_attribute('value') or ""
                except:
                    text = ""

        # If still no text, try aria-label or title
        if not text:
            text = await element.get_attribute('aria-label') or await element.get_attribute('title') or ""

        role = await element.get_attribute('role')
        aria_label = await element.get_attribute('aria-label')
        href = await element.get_attribute('href') if tag.lower() == 'a' else None

        return {
            'tag': tag.lower(),
            'text': text.strip() if text else "",
            'role': role,
            'aria_label': aria_label,
            'href': href
        }

class InteractiveController:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser_core = BrowserCore(headless=headless)
        self.element_analyzer = None

    async def run_agent(self):
        """Main agent functionality"""
        try:
            url = input("URL: ").strip()
            if not url:
                url = "https://www.google.com"  # Default URL
            elif not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            print("Starting browser...")
            await self.browser_core.start()
            await self.browser_core.navigate(url)
            self.element_analyzer = ElementAnalyzer(self.browser_core.page)
            await self.browser_core.page.wait_for_load_state('networkidle')

            while True:
                print("\n1. Click")
                print("2. Back")
                print("3. Exit")
                choice = input("> ").strip()

                if choice == "3":
                    break

                elif choice == "1":
                    if not self.element_analyzer:
                        print("No page loaded")
                        continue

                    clickable_elements = await self.element_analyzer.find_clickable_elements()

                    if not clickable_elements:
                        print("No clickable elements")
                        continue

                    elements_to_save = []
                    print("\nClickable elements:")
                    for i, element in enumerate(clickable_elements):
                        try:
                            details = await self.element_analyzer.get_element_details(element)
                            element_info = {
                                'index': i,
                                'tag': details['tag'],
                                'text': details['text'],
                                'role': details.get('role', ''),
                                'aria_label': details.get('aria_label', ''),
                                'href': details.get('href', '')
                            }
                            elements_to_save.append(element_info)

                            # Format the display text
                            display_text = details['text'][:40] + "..." if len(details['text']) > 40 else details['text']

                            # Show href for links if no text
                            if details['tag'] == 'a' and not display_text and details.get('href'):
                                display_text = f"[Link: {details['href'][:30]}...]"

                            print(f"[{i}] {details['tag'].upper()} - {display_text}")
                        except Exception as e:
                            # Skip elements that cause errors
                            continue

                    with open('clickable_elements.json', 'w') as f:
                        json.dump(elements_to_save, f, indent=2)

                    choice_click = input("Element #: ")
                    if choice_click.isdigit() and 0 <= int(choice_click) < len(clickable_elements):
                        await clickable_elements[int(choice_click)].click()
                        await self.browser_core.page.wait_for_load_state('networkidle')
                        self.element_analyzer = ElementAnalyzer(self.browser_core.page)
                        print("OK")
                    else:
                        print("Invalid")

                elif choice == "2":
                    await self.browser_core.go_back()
                    self.element_analyzer = ElementAnalyzer(self.browser_core.page)
                    print("OK")

                else:
                    print("Invalid choice")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.browser_core and self.browser_core.browser:
                await self.browser_core.close()

    async def run(self):
        """Run with menu"""
        while True:
            print("\n1. Run")
            print("2. Exit")
            choice = input("> ").strip()

            if choice == '1':
                await self.run_agent()
                continue
            elif choice == '2':
                break
            else:
                print("Invalid")
                continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Interactive Browser Agent')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--no-menu', action='store_true', help='Run without showing menu')
    args = parser.parse_args()

    controller = InteractiveController(headless=args.headless)

    if args.no_menu:
        asyncio.run(controller.run_agent())
    else:
        asyncio.run(controller.run())