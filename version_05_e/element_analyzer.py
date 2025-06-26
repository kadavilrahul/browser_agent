import asyncio
from playwright.async_api import Page

class ElementAnalyzer:
    def __init__(self, page: Page):
        self.page = page

    async def find_clickable_elements(self):
        # This selector is an example, you might need to adjust it
        elements = await self.page.query_selector_all(
            'button, a, input[type="submit"], input[type="button"], [role="button"]'
        )
        return elements

    async def get_element_details(self, element):
        tag = await element.evaluate('element => element.tagName')
        text = await element.inner_text()
        role = await element.get_attribute('role')
        aria_label = await element.get_attribute('aria-label')
        return {'tag': tag.lower(), 'text': text.strip(), 'role': role, 'aria_label': aria_label}
