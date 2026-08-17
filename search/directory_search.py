"""
Business directory source adapter.

Fetches supplier/buyer listing pages from B2B directories (IndiaMART,
TradeIndia, ExportersIndia, etc.) via seed URLs.
"""
from search._shared import fetch_seed_urls


def run_search(keyword: str, seed_urls: list[str] | None = None, **kwargs) -> list[dict]:
    if not seed_urls:
        return []
    return fetch_seed_urls(seed_urls, "Directory")