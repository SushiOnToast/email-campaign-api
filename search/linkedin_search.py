"""
LinkedIn source adapter.

LinkedIn actively blocks unauthenticated scraping and gates its official
API behind partnership approval. This adapter fetches whatever public
content is reachable from seed URLs (company page URLs) -- expect
low/zero email yield in practice, consistent with the doc's own
Known Limitations.
"""
from search._shared import fetch_seed_urls


def run_search(keyword: str, seed_urls: list[str] | None = None, **kwargs) -> list[dict]:
    if not seed_urls:
        return []
    return fetch_seed_urls(seed_urls, "LinkedIn")