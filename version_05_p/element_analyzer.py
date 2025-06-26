
from playwright.async_api import Page

class ElementAnalyzer:
    def __init__(self, page: Page):
        self.page = page

    async def find_clickable_elements(self):
        elements = await self.page.query_selector_all(
            'a, button, input[type="submit"], input[type="button"], [role="button"]'
        )
        return elements

    async def get_element_details(self, element):
        tag = await element.evaluate('el => el.tagName')
        text = await element.inner_text()
        return {'tag': tag.lower(), 'text': text.strip()}
