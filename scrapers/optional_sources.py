"""
OPTIONAL, OFF-BY-DEFAULT sources: LinkedIn and Wellfound.

Why off by default:
- LinkedIn's public (no-login) job search page is rate-limited hard and
  scraping it sits in a ToS grey area. It also renders results via JS,
  so a plain `requests` call gets an incomplete page.
- Wellfound (AngelList Talent) is a heavy JS/React app behind bot
  protection; reliable access needs a headless browser (Playwright), which
  is more setup than most of this project.

Both are included here as a *starting point* only, using their public,
no-login search pages with plain requests + BeautifulSoup. Expect these to
break, return partial results, or get blocked more often than the other
sources. Use sparingly (low frequency) and treat results as a bonus, not
a primary source. Toggle them on in the Streamlit sidebar if you want to
try them.
"""
from __future__ import annotations
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from utils import title_matches_role, guess_job_type

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_linkedin_public(
    keyword: str = "product manager",
    hours: int = 24,
    pages: int = 3,
) -> List[Dict[str, Any]]:
    """Scrapes LinkedIn's public (no-login) guest job search results page.

    Two important filters this now applies that the first version didn't:
    - f_TPR: time posted range, in seconds, derived from your selected
      time window (was hardcoded to 24h before, ignoring your filter).
    - f_E: LinkedIn's own EXPERIENCE LEVEL tag, self-selected by whoever
      posted the job (1=Internship, 2=Entry level). This is the only
      reliable way to get "fresher" postings from LinkedIn — job titles
      alone don't reveal seniority, and a plain "Product Manager" title
      could be for a 5-year-experience hire just as easily as a fresher
      one. Using f_E filters at the source instead of guessing from text.

    Still best-effort: LinkedIn may detect automation and return partial
    or zero results regardless of these params.
    """
    out: List[Dict[str, Any]] = []
    seconds = hours * 3600

    for page in range(pages):
        start = page * 25
        url = (
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={quote(keyword)}"
            "&location=India"
            f"&f_TPR=r{seconds}"
            "&f_E=1,2"   # Internship + Entry level only
            f"&start={start}"
        )
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                break
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.find_all("div", class_="base-card")
            if not cards:
                break
            for card in cards:
                try:
                    title_el = card.find("h3", class_="base-search-card__title")
                    company_el = card.find("h4", class_="base-search-card__subtitle")
                    location_el = card.find("span", class_="job-search-card__location")
                    link_el = card.find("a", class_="base-card__full-link")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title or not title_matches_role(title):
                        continue

                    out.append({
                        "title": title,
                        "company": company_el.get_text(strip=True) if company_el else "Unknown",
                        "location": location_el.get_text(strip=True) if location_el else "India",
                        "experience": "Internship / Entry level (per LinkedIn tag)",
                        "posted_at": None,  # not reliably exposed on this page
                        "apply_url": link_el["href"].split("?")[0] if link_el and link_el.has_attr("href") else "",
                        "source": "LinkedIn",
                        "job_type": guess_job_type(title),
                    })
                except Exception:
                    # one malformed card shouldn't kill the whole fetch
                    continue
        except Exception:
            # network hiccup, HTML shape change, anything — never crash the app
            break
    return out


def fetch_wellfound_placeholder(keyword: str = "product") -> List[Dict[str, Any]]:
    """Placeholder: Wellfound requires a headless browser (Playwright) for
    reliable results because listings are loaded via client-side JS behind
    bot protection. A plain `requests` call will typically return an empty
    shell page. Left here as a documented extension point rather than a
    fake/non-functional scraper.

    To implement properly: use `playwright` (free), navigate to
    https://wellfound.com/role/product-manager , wait for the job list to
    render, then extract card data. See README for a starter snippet.
    """
    return []
