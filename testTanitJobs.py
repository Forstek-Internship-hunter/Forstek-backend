import asyncio
from playwright.async_api import async_playwright
from undetected_playwright import stealth_async

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await stealth_async(page)
        await page.goto("https://www.tanitjobs.com")
        await asyncio.sleep(5)
        print(page.url)
        await browser.close()

asyncio.run(test())