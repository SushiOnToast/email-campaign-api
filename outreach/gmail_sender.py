import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
import pandas as pd
import config
from logger.activity_logger import get_sent_emails
from outreach.email_templates import personalize


def _load_audience_records(audience: str) -> list[dict]:
    emails = []

    if audience in ("business", "all"):
        if os.path.exists(config.BUSINESS_EMAILS_CSV):
            df = pd.read_csv(config.BUSINESS_EMAILS_CSV)
            emails.extend(df["email_address"].tolist())

    if audience in ("individual", "all"):
        if os.path.exists(config.INDIVIDUAL_EMAILS_CSV):
            df = pd.read_csv(config.INDIVIDUAL_EMAILS_CSV)
            emails.extend(df["email_address"].tolist())

    emails = list(dict.fromkeys(emails))

    already_sent = get_sent_emails()
    emails = [e for e in emails if e.lower() not in already_sent]

    if not emails:
        return []

    # Join back to buyers.csv to get full buyer details for personalization
    buyer_lookup = {}
    if os.path.exists(config.BUYERS_CSV):
        buyers_df = pd.read_csv(config.BUYERS_CSV)
        for _, row in buyers_df.iterrows():
            buyer_lookup[str(row["email"]).lower()] = row.to_dict()

    records = []
    for email in emails:
        record = buyer_lookup.get(email.lower(), {})
        record["email"] = email  # ensure email is always present even if not matched
        records.append(record)

    return records


def _log_send_event(email: str, status: str):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    row = pd.DataFrame([{
        "email_address": email,
        "status": status,
        "timestamp": datetime.now().isoformat(),
    }])

    if os.path.exists(config.SENT_LOG_CSV):
        existing = pd.read_csv(config.SENT_LOG_CSV)
        pd.concat([existing, row], ignore_index=True).to_csv(config.SENT_LOG_CSV, index=False)
    else:
        row.to_csv(config.SENT_LOG_CSV, index=False)


def _build_message(subject_template: str, body_template: str, buyer: dict) -> EmailMessage:
    to_email = buyer["email"]
    subject = personalize(subject_template, buyer)
    body = personalize(body_template, buyer)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_EMAIL
    msg["To"] = to_email
    if config.MONITOR_CC_EMAIL:
        msg["Cc"] = config.MONITOR_CC_EMAIL
    msg.set_content(body)

    if config.PRESENTATION_PATH and os.path.exists(config.PRESENTATION_PATH):
        with open(config.PRESENTATION_PATH, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="octet-stream",
                filename=os.path.basename(config.PRESENTATION_PATH),
            )
    else:
        print(f"[gmail_sender] Warning: presentation not found at '{config.PRESENTATION_PATH}', sending without attachment")

    return msg


def _connect():
    smtp = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
    smtp.starttls()
    smtp.login(config.GMAIL_EMAIL, config.GMAIL_APP_PASSWORD)
    return smtp


def send_campaign(subject_template: str, body_template: str, audience: str) -> dict:
    recipients = _load_audience_records(audience)

    if not recipients:
        return {"total": 0, "success_count": 0, "failed_count": 0, "recipients": []}

    smtp = _connect()
    success_count, failed_count = 0, 0
    successful, failed = [], []

    for buyer in recipients:
        email = buyer["email"]
        try:
            msg = _build_message(subject_template, body_template, buyer)
            try:
                smtp.send_message(msg)
            except smtplib.SMTPServerDisconnected:
                smtp = _connect()
                smtp.send_message(msg)

            _log_send_event(email, "sent")
            success_count += 1
            successful.append(email)

        except Exception as e:
            _log_send_event(email, "failed")
            failed_count += 1
            failed.append({"email": email, "error": str(e)})

    smtp.quit()

    return {
        "total": len(recipients),
        "success_count": success_count,
        "failed_count": failed_count,
        "recipients": successful,
        "failed": failed,
    }