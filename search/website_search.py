"""
Company website source adapter.

Fetches individual company "contact us" / homepage content directly
via seed URLs.
"""
from search._shared import fetch_seed_urls


def run_search(keyword: str, seed_urls: list[str] | None = None, **kwargs) -> list[dict]:
    if not seed_urls:
        return []
    return fetch_seed_urls(seed_urls, "Website")