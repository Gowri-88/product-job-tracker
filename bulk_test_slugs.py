"""
Bulk-test many candidate slugs at once, across all four ATS platforms.
Much faster than running test_slug.py one at a time.

Usage:
    python bulk_test_slugs.py

Edit the CANDIDATES list below with slug guesses to try — e.g. the
company's brand name, its full legal name with no spaces, name with
hyphens, etc. It's normal for most guesses to be wrong; the point is to
quickly find the ONE that's right for each company by trying several
variants at once instead of one at a time.
"""
import sys
from scrapers.ats import fetch_greenhouse, fetch_lever, fetch_ashby, fetch_workable
import utils

# Bypass role-keyword filtering so we can see ANY jobs (confirms slug is
# valid even if there's currently no fresher-relevant role open).
utils.title_matches_role = lambda t: True

FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
    "workable": fetch_workable,
}

# EDIT THIS: platform -> list of slug guesses to try for each company.
# Add as many variants per company as you want tested.
CANDIDATES = {
    "greenhouse": [
        "freshworks", "freshworksinc",
        "chargebee", "chargebeeinc",
        "browserstack",
        "unacademy",
        "cred", "credclub", "dreamplug",  # CRED's legal entity is Dreamplug Technologies
        "meesho", "fashnear",  # Meesho's legal entity is Fashnear Technologies
        "groww", "nextbillionai",  # Groww's legal entity is Billionbrains/NextBillion
        "swiggy", "bundl",  # Swiggy's legal entity is Bundl Technologies
        "zomato", "eternal",
        "phonepe",
        "urbancompany", "uc",
    ],
    "lever": [
        "slice", "sliceit",
        "cure.fit", "curefit",
        "khatabook",
        "vedantu",
        "whatfix",
        "darwinbox",
    ],
    "ashby": [
        "turing",
        "hasura",
        "loco",
        "rebelfoods",
        "innovaccer",
    ],
    "workable": [
        # add guesses here if relevant to companies you're tracking
    ],
}


def main():
    found = {}
    for platform, slugs in CANDIDATES.items():
        fetcher = FETCHERS[platform]
        for slug in slugs:
            try:
                results = fetcher(slug)
            except Exception as e:
                print(f"[{platform}] {slug:30s} -> ERROR: {type(e).__name__}")
                continue
            if results:
                print(f"[{platform}] {slug:30s} -> ✅ {len(results)} jobs found")
                found.setdefault(platform, []).append(slug)
            else:
                print(f"[{platform}] {slug:30s} -> ❌ no jobs / wrong slug")

    print("\n" + "=" * 50)
    print("WORKING SLUGS TO ADD TO config.py:")
    for platform, slugs in found.items():
        print(f"\n{platform.upper()}_COMPANIES:")
        for s in slugs:
            print(f'    "{s}",')

    if not found:
        print("None of the candidate slugs resolved. Edit CANDIDATES in this "
              "file with more guesses, or find the exact slug manually via "
              "each company's careers page redirect (see README).")


if __name__ == "__main__":
    main()
