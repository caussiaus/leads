import asyncio
import aiohttp

from scr.utils.google_cse import google_cse
from scr.utils.fetcher import fetch_html, fetch_js
from scr.utils.html_parser import html_to_text
from scr.utils.email_extractor import extract_emails

async def run_phase2(people: dict):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for name, rec in people.items():
            if not rec["emails"]:
                tasks.append(drill(name, rec, session))
        await asyncio.gather(*tasks)
    return people

async def drill(name, rec, session):
    for q in [f'"{name}" email', f'"{name}" linkedin OR profile']:
        for url in google_cse(q, 3):
            html = await fetch_js(url) if "linkedin.com" in url else await fetch_html(session, url)
            if not html:
                continue
            text = html_to_text(html)
            rec["emails"].update(extract_emails(text))
            if rec["emails"]:
                return