import config
from search import google_search, facebook_search, linkedin_search, directory_search, website_search
from search.data_extractor import extract_records
from search.email_validator import filter_records
from logger.activity_logger import append_buyer_records, filter_new_buyers

GOOGLE_SEED_URLS: list[str] = []  # empty = live DuckDuckGo search

FACEBOOK_SEED_URLS = [
    "https://www.facebook.com/people/Singing-Bowl-Specialist-MFG-Co/61567106432572/",
]

LINKEDIN_SEED_URLS = [
    "https://www.linkedin.com/company/singing-bowl-specialist-mfg-co",
]

DIRECTORY_SEED_URLS = [
    "https://dir.indiamart.com/impcat/singing-bowls.html",
    "https://www.exportersindia.com/indian-suppliers/singing-bowls.htm",
    "https://www.indiamart.com/indian-exim-corporation/",
    "https://www.indiamart.com/singingbowlcentre/aboutus.html",
]

WEBSITE_SEED_URLS = [
    "https://www.singingbowlexporter.com/",
    "https://www.singingbowlexporter.com/contact.html",
    "https://www.singingbowlmanufacturer.com/",
    "https://www.handmadesingingbowl.com/",
    "https://www.phoeniximport.com/en/3/singing-bowls-and-more.aspx",
    "https://www.ancientwisdom.biz/wholesale_tibetian_bowls_artifacts",
    "https://www.nepalartshop.com/handmade-singing-bowls.php",
    "https://www.singingbowlsspecialist.com/",
    "https://www.nepalyp.com/company/66055/Handmade_Singing_Bowl_Export_Nepal",
]

def run_discovery():
    print(f"[1/5] Searching for '{config.SEARCH_KEYWORD}' buyer leads across 5 sources...")

    raw_results = []
    raw_results += google_search.run_search(config.SEARCH_KEYWORD, seed_urls=GOOGLE_SEED_URLS)
    raw_results += facebook_search.run_search(config.SEARCH_KEYWORD, seed_urls=FACEBOOK_SEED_URLS)
    raw_results += linkedin_search.run_search(config.SEARCH_KEYWORD, seed_urls=LINKEDIN_SEED_URLS)
    raw_results += directory_search.run_search(config.SEARCH_KEYWORD, seed_urls=DIRECTORY_SEED_URLS)
    raw_results += website_search.run_search(config.SEARCH_KEYWORD, seed_urls=WEBSITE_SEED_URLS)

    print(f"      -> {len(raw_results)} pages fetched across all sources")

    print("[2/5] Extracting structured buyer records...")
    records = extract_records(raw_results)
    print(f"      -> {len(records)} candidate records")

    print("[3/5] Validating emails...")
    valid, flagged = filter_records(records)
    print(f"      -> {len(valid)} valid, {len(flagged)} flagged for review")

    print("[4/5] Saving to buyers.csv and checking for duplicates...")
    append_buyer_records(valid)
    new_buyers = filter_new_buyers(valid)
    print(f"      -> {len(new_buyers)} new (non-duplicate) buyers to queue")

    print("\n=== DISCOVERY SUMMARY ===")
    print(f"Candidates found     : {len(records)}")
    print(f"Passed validation    : {len(valid)}")
    print(f"Flagged for review   : {len(flagged)}")
    print(f"New (non-duplicate)  : {len(new_buyers)}")
    print("==========================\n")

    return new_buyers


if __name__ == "__main__":
    run_discovery()