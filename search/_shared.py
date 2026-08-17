"""
Shared HTTP fetching logic used by all source adapters.
"""
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
REQUEST_TIMEOUT = 10
REQUEST_DELAY = 1.5


def fetch_page(url: str) -> str:
    """Fetch raw HTML text content for a single URL. Returns '' on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except requests.RequestException:
        return ""


def fetch_seed_urls(urls: list[str], source_platform: str) -> list[dict]:
    """Fetch a list of URLs and return them in the standard raw-result shape."""
    results = []
    for url in urls:
        content = fetch_page(url)
        if content:
            results.append({"url": url, "raw_content": content, "source_platform": source_platform})
        time.sleep(REQUEST_DELAY)
    return results