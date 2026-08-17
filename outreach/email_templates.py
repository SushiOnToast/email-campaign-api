"""
Default email subject/body templates matching the required export
outreach format. Placeholders in {{double_braces}} get filled in per
recipient at send time using their buyer record + product/sender config.
"""
import config

DEFAULT_SUBJECT_TEMPLATE = "Export Partnership Opportunity – {{product_name}}"

DEFAULT_BODY_TEMPLATE = """Dear {{buyer_name}},

I hope this email finds you well.

We came across your company while researching businesses involved in the import, distribution, or sale of {{product_name}}.

We would like to introduce our company and explore a potential business partnership with your organization. We offer quality products suitable for international buyers, distributors, wholesalers, and retailers.

Buyer Details

- Contact Name: {{buyer_name}}
- Company Name: {{company_name}}
- Country: {{country}}
- Website: {{website}}
- Source Platform: {{source_platform}}

Product Details

- Product Name: {{product_name}}
- Product Category: {{product_category}}
- Export Availability: {{export_availability}}
- Customization Options: {{customization_options}}
- Minimum Order Quantity: {{moq}}
- Shipping Availability: {{shipping_availability}}

Please find our company presentation and product information attached for your review.

We would be pleased to discuss pricing, product specifications, samples, customization, and long-term supply opportunities.

Thank you for your time and consideration. We look forward to hearing from you.

Best Regards,

{{sender_name}}
{{sender_company}}
{{sender_email}}
{{sender_phone}}"""


def personalize(template: str, buyer: dict) -> str:
    """
    Replaces {{token}} placeholders in a subject or body template using
    the buyer's own record plus product/sender info from config.
    Missing buyer fields fall back to a safe default rather than
    leaving a raw placeholder in the sent email.
    """
    replacements = {
        "buyer_name": buyer.get("buyer_name") or "Sir/Madam",
        "company_name": buyer.get("company_name") or "your company",
        "country": buyer.get("country") or "N/A",
        "website": buyer.get("website") or "N/A",
        "source_platform": buyer.get("source_platform") or "N/A",
        "product_name": config.PRODUCT_NAME,
        "product_category": config.PRODUCT_CATEGORY,
        "export_availability": config.EXPORT_AVAILABILITY,
        "customization_options": config.CUSTOMIZATION_OPTIONS,
        "moq": config.MIN_ORDER_QUANTITY,
        "shipping_availability": config.SHIPPING_AVAILABILITY,
        "sender_name": config.SENDER_NAME or "Export Team",
        "sender_company": config.SENDER_COMPANY_NAME or "",
        "sender_email": config.GMAIL_EMAIL,
        "sender_phone": config.SENDER_PHONE or "",
    }

    result = template
    for key, value in replacements.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result