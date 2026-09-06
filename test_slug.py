"""
Helper to verify a company's ATS slug before adding it to config.py.

Usage:
    python test_slug.py greenhouse razorpay
    python test_slug.py lever meesho
    python test_slug.py ashby turing
    python test_slug.py workable somecompany

How to find a slug in the first place:
    1. Go to the company's website, click "Careers"/"We're hiring".
    2. Look at the URL you land on:
       boards.greenhouse.io/<SLUG>   -> platform=greenhouse, slug=<SLUG>
       jobs.lever.co/<SLUG>          -> platform=lever, slug=<SLUG>
       jobs.ashbyhq.com/<SLUG>       -> platform=ashby, slug=<SLUG>
       apply.workable.com/<SLUG>     -> platform=workable, slug=<SLUG>
    3. Run this script with that platform + slug to confirm the API works
       before adding it to config.py.
"""
import sys
from scrapers.ats import fetch_greenhouse, fetch_lever, fetch_ashby, fetch_workable

FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
    "workable": fetch_workable,
}


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in FETCHERS:
        print(__doc__)
        sys.exit(1)

    platform, slug = sys.argv[1], sys.argv[2]
    print(f"Testing {platform} slug '{slug}'...")

    # Temporarily bypass the role-keyword filter to see ALL jobs, so you can
    # confirm the slug resolves even if there are no product roles open now.
    import utils
    original = utils.title_matches_role
    utils.title_matches_role = lambda t: True
    try:
        results = FETCHERS[platform](slug)
    finally:
        utils.title_matches_role = original

    if not results:
        print(f"❌ No jobs found. Either the slug is wrong, the company has "
              f"no open roles right now, or they don't use {platform}.")
    else:
        print(f"✅ Slug works! Found {len(results)} open roles (unfiltered). Examples:")
        for r in results[:5]:
            print(f"  - {r['title']} ({r['location']})")
        print(f"\nAdd '{slug}' to the {platform.upper()}_COMPANIES list in config.py")


if __name__ == "__main__":
    main()
