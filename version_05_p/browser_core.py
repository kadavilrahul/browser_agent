
import asyncio
from playwright.async_api import async_playwright, Page
import os

class BrowserCore:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url):
        await self.page.goto(url)

    async def get_page_content(self):
        return await self.page.content()
