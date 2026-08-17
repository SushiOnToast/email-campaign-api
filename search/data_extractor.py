"""
Parses raw content returned by a source adapter into the normalized
buyer schema: buyer_name, company_name, email, website, country, source_platform.
"""
from urllib.parse import urlparse
from search.email_validator import extract_valid_emails

COUNTRY_KEYWORDS = [
    "USA", "United States", "UK", "United Kingdom", "Germany", "France",
    "Canada", "Australia", "India", "Nepal", "Netherlands", "Japan",
    "Singapore", "UAE", "Italy", "Spain", "Switzerland",
]


def guess_country(text: str) -> str:
    for country in COUNTRY_KEYWORDS:
        if country.lower() in text.lower():
            return country
    return ""


def guess_company_name(url: str) -> str:
    domain = urlparse(url).netloc.replace("www.", "")
    name = domain.split(".")[0]
    return name.replace("-", " ").title()


def extract_records(raw_results: list[dict]) -> list[dict]:
    records = []
    for item in raw_results:
        url = item.get("url", "")
        content = item.get("raw_content", "")
        source = item.get("source_platform", "Unknown")

        emails = extract_valid_emails(content)
        if not emails:
            continue

        company = guess_company_name(url)
        country = guess_country(content)

        for email in set(emails):
            records.append({
                "buyer_name": "",
                "company_name": company,
                "email": email,
                "website": url,
                "country": country,
                "source_platform": source,
            })
    return records