import ssl, certifi, asyncio
import aiohttp
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str|None:
    headers = {"User-Agent": UA, "Referer": "https://www.google.com/"}
    for attempt in (1,2):
        try:
            async with session.get(url, headers=headers,
                                   timeout=15,
                                   ssl=ssl.create_default_context(cafile=certifi.where())
            ) as r:
                if r.status == 403 and url.startswith("http://"):
                    url = url.replace("http://","https://",1)
                    continue
                r.raise_for_status()
                return await r.text()
        except Exception:
            if attempt==1: await asyncio.sleep(2)
    return None

async def fetch_js(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page    = await browser.new_page()
        await page.goto(url, timeout=30000)
        html    = await page.content()
        await browser.close()
        return html
