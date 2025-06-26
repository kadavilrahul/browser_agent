


import asyncio
import json
from browser_core import BrowserCore
from element_analyzer import ElementAnalyzer

class InteractiveController:
    def __init__(self):
        self.browser_core = BrowserCore(headless=False)
        self.element_analyzer = None

    async def run(self):
        try:
            url = input("Enter URL (or 'exit'): ")
            if url.lower() == 'exit':
                return # Exit if user types 'exit' at the first prompt
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            await self.browser_core.start()
            self.element_analyzer = ElementAnalyzer(self.browser_core.page)
            await self.browser_core.navigate(url)
            
            while True:
                clickable_elements = await self.element_analyzer.find_clickable_elements()

                elements_to_save = []
                print("\nClickable elements found:")
                for i, element in enumerate(clickable_elements):
                    details = await self.element_analyzer.get_element_details(element)
                    element_info = {'index': i, 'tag': details['tag'], 'text': details['text']}
                    elements_to_save.append(element_info)
                    print(f"  {i}: <{details['tag']}> {details['text']}")
                
                with open('clickable_elements.json', 'w') as f:
                    json.dump(elements_to_save, f, indent=2)
                print("\nSaved clickable elements to clickable_elements.json")

                choice = input("\nEnter element number to click (or 's' to skip): ")
                if choice.isdigit() and 0 <= int(choice) < len(clickable_elements):
                    await clickable_elements[int(choice)].click()
                    print("Clicked element.")
                    await self.browser_core.page.wait_for_load_state('networkidle')

        finally:
            await self.browser_core.close()

if __name__ == "__main__":
    controller = InteractiveController()
    asyncio.run(controller.run())
