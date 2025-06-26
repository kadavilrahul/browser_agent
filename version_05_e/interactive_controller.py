import sys
import asyncio
import json
from browser_core import BrowserCore
from element_analyzer import ElementAnalyzer
from login_manager import get_all_credentials
import login_manager
from reference import UnifiedWebAgent

class InteractiveController:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser_core = BrowserCore(headless=headless)
        self.element_analyzer = None
        self.web_agent = UnifiedWebAgent(headless=headless)

    async def run_agent(self):
        """Run the browser agent without showing the menu"""
        try:
            await self.browser_core.start()
            self.element_analyzer = self.browser_core.element_analyzer

            print("\nWhat would you like to do?")
            print("1. Login to a website")
            print("2. Navigate to a URL")
            initial_choice = input("Enter your choice [1-2]: ")
            if initial_choice == '1':
            if initial_choice == '1':
                credentials = get_all_credentials()
                if not credentials:
                    print("\n❌ No credentials found. Please add credentials first (use option 3 from main menu).")
                    return

                print("\nSelect a website to login to:")
                websites = list(credentials.keys())
                for i, website in enumerate(websites):
                    print(f"{i + 1}. {website}")

                choice_login = input("Enter your choice: ")
                if not choice_login.isdigit():
                    print("Invalid choice.")
                    return
                choice_login = int(choice_login) - 1
                if 0 <= choice_login < len(websites):
                    website = websites[choice_login]
                    info = credentials[website]
                    print(f"\n🔐 Logging into {website}...")
                    login_successful = await self.web_agent.login_to_website(
                        info['login_url'],
                        info['username'],
                        info['password']
                    )
                    if login_successful:
                        print("✓ Login successful!")
                        await self.browser_core.navigate(info['login_url'])
                        self.element_analyzer = ElementAnalyzer(self.browser_core.page)
                    else:
                        print("❌ Login failed.")
                        return
                else:
                    print("Invalid choice.")
                    return
            elif initial_choice == '2':
                url = input("Enter the URL you want to navigate to: ")
                if url:
                    if not url.startswith("http://") and not url.startswith("https://"):
                        url = "https://" + url
                    print(f"\n🌐 Navigating to {url}...")
                    await self.browser_core.navigate(url)
                    print("✓ Navigation successful!")
                    self.element_analyzer = ElementAnalyzer(self.browser_core.page)
            else:
                print("Invalid choice.")
                return

            # Interactive loop for actions
            while True:
                if self.element_analyzer is None:
                    print("Element analyzer not available. Please navigate to a page first.")
                    url = input("Enter URL to navigate to (or 'exit'): ")
                    if url.lower() == 'exit':
                        break
                    if url:
                        if not url.startswith("http://") and not url.startswith("https://"):
                            url = "https://" + url
                        await self.browser_core.navigate(url)
                        self.element_analyzer = ElementAnalyzer(self.browser_core.page)
                    else:
                        continue

                print("\n" + "="*50)
                print("Available actions:")
                print("  click  - Click on an element")
                print("  type   - Type text into a field")
                print("  scroll - Scroll the page")
                print("  read   - Read page content")
                print("  nav    - Navigate to a new URL")
                print("  exit   - Exit the browser")
                print("="*50)
                
                action = input("\nEnter action: ").strip().lower()

                if action == "exit":
                    print("👋 Exiting browser...")
                    break

                if action == "nav":
                    url = input("Enter new URL: ")
                    if url:
                        if not url.startswith("http://") and not url.startswith("https://"):
                            url = "https://" + url
                        await self.browser_core.navigate(url)
                        self.element_analyzer = ElementAnalyzer(self.browser_core.page)
                        print(f"✓ Navigated to {url}")
                    continue

                if action == "click":
                    clickable_elements = await self.element_analyzer.find_clickable_elements()
                    
                    if not clickable_elements:
                        print("No clickable elements found on this page.")
                        continue

                    elements_to_save = []
                    print("\n🔍 Interactive elements found:")
                    for i, element in enumerate(clickable_elements):
                        details = await self.element_analyzer.get_element_details(element)
                        element_info = {
                            'index': i, 
                            'tag': details['tag'], 
                            'text': details['text'], 
                            'role': details.get('role', ''), 
                            'aria_label': details.get('aria_label', '')
                        }
                        elements_to_save.append(element_info)
                        # Format the output better
                        text = details['text'][:50] + "..." if len(details['text']) > 50 else details['text']
                        print(f"  [{i}] {details['tag'].upper()} - {text}")

                    with open('clickable_elements.json', 'w') as f:
                        json.dump(elements_to_save, f, indent=2)
                    print("\n💾 Saved interactive elements to clickable_elements.json")

                    choice_click = input("\nEnter element number to click: ")
                    if choice_click.isdigit() and 0 <= int(choice_click) < len(clickable_elements):
                        await clickable_elements[int(choice_click)].click()
                        print("✓ Clicked element.")
                        await self.browser_core.page.wait_for_load_state('networkidle')
                        self.element_analyzer = ElementAnalyzer(self.browser_core.page)
                    else:
                        print("Invalid element number.")

                elif action == "type":
                    print("Type functionality not yet implemented.")
                    
                elif action == "scroll":
                    print("Scroll functionality not yet implemented.")
                    
                elif action == "read":
                    print("Read functionality not yet implemented.")
                    
                else:
                    print("Unknown action. Please try again.")

        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
        finally:
            if self.browser_core and self.browser_core.browser:
                await self.browser_core.close()

    async def run(self):
        """Run with menu - for backward compatibility"""
        while True:
            print("===========================")
            print("  Interactive Browser Agent")
            print("===========================")
            print("1. Setup (First time only)")
            print("2. Run Agent")
            print("3. Add/Update Credentials")
            print("4. Exit")
            print("---------------------------")
            choice = input("Enter your choice [1-4]: ").strip()
            
            if choice == '1':
                print("-> Setup should be done via the bash script.\n")
                continue
            elif choice == '2':
                await self.run_agent()
                continue
            elif choice == '3':
                login_manager.login()
                continue
            elif choice == '4':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
                continue

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Interactive Browser Agent')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--no-menu', action='store_true', help='Run without showing menu')
    args = parser.parse_args()

    controller = InteractiveController(headless=args.headless)

    if args.no_menu:
        # Run the agent directly without menu
        asyncio.run(controller.run_agent())
    else:
        # Run with the interactive menu
        asyncio.run(controller.run())