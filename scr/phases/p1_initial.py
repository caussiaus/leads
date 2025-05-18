import asyncio
from scr.utils.google_cse import google_cse
from scr.utils.fetcher import fetch_html
from scr.utils.html_parser import html_to_text
from scr.utils.ner import extract_names

async def run(prompt: str, limit: int):
    urls = google_cse(prompt, limit)
    people = {}
    async with aiohttp.ClientSession() as session:
        tasks = [process(u, session, people) for u in urls]
        await asyncio.gather(*tasks)
    return people

async def process(url, session, people):
    html = await fetch_html(session, url)
    if not html: return
    text = await html_to_text(html)
    for name in extract_names(text):
        people.setdefault(name, {"urls":set(), "snips":[], "emails":set()})
        rec = people[name]
        rec["urls"].add(url)
        rec["snips"].append(text[:100])
