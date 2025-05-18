import requests
import logging
from .config import GOOGLE_API_KEY, GOOGLE_CX

log = logging.getLogger(__name__)

def google_cse(query: str, num: int=10):
    try:
        r = requests.get("https://www.googleapis.com/customsearch/v1", params={
            "q": query, "cx": GOOGLE_CX, "key": GOOGLE_API_KEY,
            "num": min(num,10)
        })
        r.raise_for_status()
        return [i["link"] for i in r.json().get("items",[])]
    except Exception as e:
        log.error(f"CSE failed: {e}")
        return []
