"""
Filters extracted email addresses before they enter the outreach queue.
"""
import re

EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp")
MAX_DOMAIN_LENGTH = 50


def is_valid_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip().lower()
    if not EMAIL_PATTERN.match(email):
        return False
    if email.endswith(IMAGE_EXTENSIONS):
        return False
    domain = email.split("@")[-1]
    if len(domain) > MAX_DOMAIN_LENGTH:
        return False
    return True


def extract_valid_emails(raw_text: str) -> list[str]:
    candidates = re.findall(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", raw_text
    )
    return [e for e in candidates if is_valid_email(e)]


def filter_records(records: list[dict]) -> tuple[list[dict], list[dict]]:
    valid, flagged = [], []
    for record in records:
        if is_valid_email(record.get("email", "")):
            valid.append(record)
        else:
            flagged.append(record)
    return valid, flagged