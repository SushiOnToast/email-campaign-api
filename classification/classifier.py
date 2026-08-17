import os
import json
import pandas as pd
from google import genai
import config

FREE_MAIL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
BATCH_SIZE = 20


def classify_email_stub(email: str) -> str:
    """
    Fallback heuristic classifier, used if the Gemini API is unavailable
    or GEMINI_API_KEY isn't set. Business if domain isn't a common
    free-mail provider, else individual.
    """
    domain = email.strip().lower().split("@")[-1]
    return "individual" if domain in FREE_MAIL_DOMAINS else "business"


def _build_prompt(emails: list[str]) -> str:
    email_list = "\n".join(emails)
    return f"""You are classifying email addresses as belonging to a "business" \
(company, organization, store, wholesaler) or an "individual" (personal use).

Classify each email below. Base your judgment on the domain and any naming \
patterns (e.g. company names, generic role addresses like sales@ or info@ \
suggest business; free providers like gmail.com often suggest individual, \
but a business can also use a free provider).

Respond with ONLY a JSON object mapping each email to either "business" or \
"individual". No explanation, no markdown formatting, just raw JSON.

Emails:
{email_list}
"""


def classify_batch_with_gemini(emails: list[str]) -> dict:
    """
    Classifies a batch of emails via the Gemini API.
    Returns {email: "business"|"individual"}.
    Falls back to the heuristic for the whole batch on any failure.
    """
    if not config.GEMINI_API_KEY:
        return {e: classify_email_stub(e) for e in emails}

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=_build_prompt(emails),
        )
        raw_text = response.text.strip()

        # Strip markdown code fences if Gemini wraps the JSON in ```json ... ```
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        parsed = json.loads(raw_text)

        result = {}
        for e in emails:
            label = parsed.get(e, "").lower()
            result[e] = label if label in ("business", "individual") else classify_email_stub(e)
        return result

    except Exception as err:
        print(f"[classifier] Gemini batch failed, falling back to heuristic: {err}")
        return {e: classify_email_stub(e) for e in emails}


def run_classification():
    if not os.path.exists(config.BUYERS_CSV):
        return {"total_unique": 0, "business_count": 0, "individual_count": 0}

    df = pd.read_csv(config.BUYERS_CSV)
    df = df.drop_duplicates(subset="email")
    emails = df["email"].dropna().tolist()

    all_labels = {}
    for i in range(0, len(emails), BATCH_SIZE):
        batch = emails[i:i + BATCH_SIZE]
        batch_result = classify_batch_with_gemini(batch)
        all_labels.update(batch_result)

    business_emails = [e for e, label in all_labels.items() if label == "business"]
    individual_emails = [e for e, label in all_labels.items() if label == "individual"]

    os.makedirs(config.DATA_DIR, exist_ok=True)
    pd.DataFrame({"email_address": business_emails}).to_csv(config.BUSINESS_EMAILS_CSV, index=False)
    pd.DataFrame({"email_address": individual_emails}).to_csv(config.INDIVIDUAL_EMAILS_CSV, index=False)

    return {
        "total_unique": len(all_labels),
        "business_count": len(business_emails),
        "individual_count": len(individual_emails),
    }