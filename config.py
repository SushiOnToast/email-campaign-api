from dotenv import load_dotenv
import os

load_dotenv()

# Gmail Credentials
GMAIL_EMAIL=os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD=os.getenv("GMAIL_APP_PASSWORD")
MONITOR_CC_EMAIL = os.getenv("MONITOR_CC_EMAIL", "")
 
# Run Configuration
SEARCH_KEYWORD=os.getenv("SEARCH_KEYWORD", "Singing Bowls")
DAILY_SEND_LIMIT=os.getenv("DAILY_SEND_LIMIT", 100)
PRESENTATION_PATH = os.getenv("PRESENTATION_PATH", "assets/product_presentation.pdf")
SEND_DELAY_SECONDS = float(os.getenv("SEND_DELAY_SECONDS", "3"))

# Directories
DATA_DIR=os.getenv("DATA_DIR")
BUYERS_CSV=os.path.join(DATA_DIR, "buyers.csv")
SENT_LOG_CSV=os.path.join(DATA_DIR, "sent_log.csv")
BUSINESS_EMAILS_CSV = os.path.join(DATA_DIR, "business_emails.csv")
INDIVIDUAL_EMAILS_CSV = os.path.join(DATA_DIR, "individual_emails.csv")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Product details (used in email personalization)
PRODUCT_NAME = os.getenv("PRODUCT_NAME", "Singing Bowls")
PRODUCT_CATEGORY = os.getenv("PRODUCT_CATEGORY", "Handcrafted Metal Singing Bowls")
EXPORT_AVAILABILITY = os.getenv("EXPORT_AVAILABILITY", "Worldwide")
CUSTOMIZATION_OPTIONS = os.getenv("CUSTOMIZATION_OPTIONS", "Custom branding and packaging available")
MIN_ORDER_QUANTITY = os.getenv("MIN_ORDER_QUANTITY", "50 pieces")
SHIPPING_AVAILABILITY = os.getenv("SHIPPING_AVAILABILITY", "Air and Sea Freight")

# Sender details (used in email signature)
SENDER_NAME = os.getenv("SENDER_NAME", "")
SENDER_COMPANY_NAME = os.getenv("SENDER_COMPANY_NAME", "")
SENDER_PHONE = os.getenv("SENDER_PHONE", "")