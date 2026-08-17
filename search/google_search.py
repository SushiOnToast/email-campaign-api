"""
Google-labeled adapter: live-queries DuckDuckGo's HTML search for the keyword,
or fetches seed_urls directly if provided.
"""
import requests
from bs4 import BeautifulSoup
from search._shared import fetch_page, fetch_seed_urls, HEADERS, REQUEST_TIMEOUT

DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"


def _search_duckduckgo(query: str, max_results: int = 10) -> list[str]:
    try:
        resp = requests.get(DUCKDUCKGO_HTML_URL, params={"q": query}, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as err:
        print(f"[google_search] DuckDuckGo search failed: {err}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    urls = [a.get("href") for a in soup.select("a.result__a") if a.get("href")]
    return urls[:max_results]


def run_search(keyword: str, seed_urls: list[str] | None = None, max_results: int = 10, **kwargs) -> list[dict]:
    if seed_urls:
        return fetch_seed_urls(seed_urls, "Google")

    query = f'"{keyword}" buyer OR importer OR wholesaler contact email'
    urls = _search_duckduckgo(query, max_results)
    return fetch_seed_urls(urls, "Google") if urls else []