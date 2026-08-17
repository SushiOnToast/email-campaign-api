"""
Single point of truth for buyers.csv read/write and duplicate-checking
against sent_log.csv.
"""
import os
import pandas as pd
from datetime import datetime, timezone

import config

BUYER_COLUMNS = ["buyer_name", "company_name", "email", "website", "country", "source_platform", "discovered_date"]
SENT_LOG_COLUMNS = ["email_address", "status", "timestamp"]


def _ensure_csv(path: str, columns: list[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)


def append_buyer_records(records: list[dict]):
    _ensure_csv(config.BUYERS_CSV, BUYER_COLUMNS)
    existing = pd.read_csv(config.BUYERS_CSV)
    known_emails = set(existing["email"].str.lower()) if not existing.empty else set()

    new_rows = []
    now = datetime.now(timezone.utc).isoformat()
    for r in records:
        if r["email"].lower() in known_emails:
            continue
        row = {col: r.get(col, "") for col in BUYER_COLUMNS if col != "discovered_date"}
        row["discovered_date"] = now
        new_rows.append(row)
        known_emails.add(r["email"].lower())

    if new_rows:
        pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True).to_csv(
            config.BUYERS_CSV, index=False
        )
    return new_rows


def get_sent_emails() -> set[str]:
    _ensure_csv(config.SENT_LOG_CSV, SENT_LOG_COLUMNS)
    log = pd.read_csv(config.SENT_LOG_CSV)
    if log.empty:
        return set()
    return set(log["email_address"].str.lower())


def filter_new_buyers(records: list[dict]) -> list[dict]:
    sent = get_sent_emails()
    return [r for r in records if r["email"].lower() not in sent]