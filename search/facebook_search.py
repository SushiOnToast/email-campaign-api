"""
Facebook source adapter.

Facebook business pages require an authenticated session to view most
content, and the Graph API requires Meta app review for business use.
This adapter fetches whatever public content is reachable from seed URLs
(business page URLs) without authentication -- expect low/zero email yield
in practice, consistent with the doc's own Known Limitations.
"""
from search._shared import fetch_seed_urls


def run_search(keyword: str, seed_urls: list[str] | None = None, **kwargs) -> list[dict]:
    if not seed_urls:
        return []
    return fetch_seed_urls(seed_urls, "Facebook")