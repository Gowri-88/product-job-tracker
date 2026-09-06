"""
Central configuration: keywords, company lists, experience filters.
EDIT THIS FILE FIRST — especially COMPANIES — to tune results for you.
"""

# ---------------------------------------------------------------------------
# ROLE KEYWORDS — titles that count as "product" roles for you.
# Matching is case-insensitive substring match against the job title.
# Add/remove freely.
# ---------------------------------------------------------------------------
ROLE_KEYWORDS = [
    "product manager",
    "associate product manager",
    "apm",
    "product analyst",
    "product management",
    "product operations",
    "product ops",
    "business analyst",  # many freshers get routed here into product orgs
    "product intern",
    "product management intern",
    "growth analyst",
    "product marketing",  # optional — remove if not relevant
]

# Titles that should be EXCLUDED even if they match a keyword above
# (e.g. senior/lead roles you don't want as a fresher)
EXCLUDE_KEYWORDS = [
    "senior", "sr.", "sr ", "lead ", "principal", "director", "head of",
    "vp ", "vice president", "staff product", "10+ years", "8+ years",
    "5+ years", "manager, product marketing",  # tweak as needed
]

# Experience patterns considered "fresher-friendly" (0-1 yrs) when experience
# text is available from a source. If NO experience info is available, the
# listing is still KEPT (better to over-include than silently drop it) —
# review manually.
FRESHER_EXPERIENCE_MAX_YEARS = 1

# Locations to keep (India-wide). Leave broad; refine later if too noisy.
LOCATION_KEYWORDS = [
    "india", "bengaluru", "bangalore", "mumbai", "delhi", "ncr", "gurugram",
    "gurgaon", "noida", "hyderabad", "pune", "chennai", "kolkata", "remote",
    "pan india", "kerala", "kochi",
]

# ---------------------------------------------------------------------------
# COMPANY LISTS FOR ATS APIS (Greenhouse / Lever / Ashby / Workable)
# These are FREE, STABLE, public JSON endpoints — no login, no scraping.
# IMPORTANT: I could not verify these slugs live against the real sites from
# here (network sandboxing). Treat this as a STARTER list. Before relying on
# it, run `python test_slug.py <platform> <slug>` (see README) to confirm
# each slug actually resolves — companies switch ATS vendors over time.
# Add more by checking how a company's "Careers" button redirects:
#   - boards.greenhouse.io/<slug>      -> Greenhouse
#   - jobs.lever.co/<slug>             -> Lever
#   - jobs.ashbyhq.com/<slug>          -> Ashby
#   - apply.workable.com/<slug>        -> Workable
# ---------------------------------------------------------------------------

GREENHOUSE_COMPANIES = [
    "razorpay",
    "postman",
    "freshworks",
    "chargebee",
    "browserstack",
    "unacademy",
    "cred",
    # add more slugs here after verifying with test_slug.py
]

LEVER_COMPANIES = [
    "meesho",
    "groww",
    "slice",
    # add more slugs here after verifying with test_slug.py
]

ASHBY_COMPANIES = [
    "turing",
    "hasura",
    # add more slugs here after verifying with test_slug.py
]

WORKABLE_COMPANIES = [
    # add slugs here after verifying with test_slug.py
]

# ---------------------------------------------------------------------------
# TIME WINDOWS available in the UI, mapped to hours
# ---------------------------------------------------------------------------
TIME_WINDOWS = {
    "Last 24 hours": 24,
    "Last 2 days": 48,
    "Last 3 days": 72,
    "Last 1 week": 168,
}

# Toggle noisy / fragile scrapers on or off from the UI defaults here
DEFAULT_SOURCES_ENABLED = {
    "Greenhouse": True,
    "Lever": True,
    "Ashby": True,
    "Workable": True,
    "Naukri": True,
    "Unstop": True,
    "LinkedIn (best-effort)": False,   # off by default: fragile + ToS grey area
    "Wellfound (best-effort)": False,  # off by default: heavy JS, fragile
}
