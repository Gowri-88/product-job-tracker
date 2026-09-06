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
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from utils import title_matches_role, guess_job_type

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_linkedin_public(keyword: str = "product manager fresher") -> List[Dict[str, Any]]:
    """Scrapes LinkedIn's public (no-login) guest job search results page.
    Very likely to return few/no results if LinkedIn detects automation.
    """
    out: List[Dict[str, Any]] = []
    url = (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={requests.utils.quote(keyword)}&location=India&f_TPR=r86400"
    )
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return out
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")
        for card in cards:
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
                "experience": "Not specified",
                "posted_at": None,  # not reliably exposed on this page
                "apply_url": link_el["href"].split("?")[0] if link_el and link_el.has_attr("href") else "",
                "source": "LinkedIn",
                "job_type": guess_job_type(title),
            })
    except requests.RequestException:
        pass
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
