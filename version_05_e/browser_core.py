from playwright.async_api import async_playwright
import time
from element_analyzer import ElementAnalyzer
from login_manager import get_credentials
from urllib.parse import urlparse

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

    async def login(self, login_url, username, password, username_field, password_field, submit_button):
        await self.page.goto(login_url)
        await self.page.fill(username_field, username)
        await self.page.fill(password_field, password)
        await self.page.click(submit_button)
        await self.page.wait_for_load_state('networkidle')
        parsed_url = urlparse(login_url)
        website = parsed_url.netloc
        print(f"-> Login to {website} successful.")

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url):
        await self.page.goto(url)

    async def click_element(self, selector):
        if not self.page:
            print("-> Browser not started. Please navigate to a URL first.")
            return
        await self.page.click(selector)

    async def type_into_element(self, selector, text):
        if not self.page:
            print("-> Browser not started. Please navigate to a URL first.")
            return
        await self.page.fill(selector, text)

    async def scroll(self, direction):
        if not self.page:
            print("-> Browser not started. Please navigate to a URL first.")
            return
        if direction == "down":
            await self.page.evaluate("window.scrollBy(0, window.innerHeight)")
        elif direction == "up":
            await self.page.evaluate("window.scrollBy(0, -window.innerHeight)")

    async def read_element_text(self, selector):
        if not self.page:
            print("-> Browser not started. Please navigate to a URL first.")
            return
        return await self.page.text_content(selector)

    async def get_page_content(self):
        if not self.page:
            print("-> Browser not started. Please navigate to a URL first.")
            return
        return await self.page.content()
