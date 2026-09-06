"""
BEST-EFFORT Naukri fetcher.

Naukri's search page calls an internal JSON endpoint
(jobapi/v3/search) to render results. It requires no login for basic
search, but it is NOT an official public API — it can change or start
blocking without notice. This is for personal, low-volume, non-commercial
use only. If it stops working, open naukri.com in a browser, search for
"product manager fresher", open DevTools -> Network tab, find the
jobapi/v3/search request, and copy the new required headers/params here.
"""
from __future__ import annotations
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from utils import title_matches_role, guess_job_type

BASE_URL = "https://www.naukri.com/jobapi/v3/search"

# Headers Naukri's frontend sends with these requests. Required or you'll
# get blocked/empty results.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "appid": "109",
    "systemid": "Naukri",
    "Referer": "https://www.naukri.com/",
}


def fetch_naukri(keyword: str = "product manager", experience_years: int = 0, pages: int = 2) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for page in range(1, pages + 1):
        params = {
            "noOfResults": 40,
            "urlType": "search_by_keyword",
            "searchType": "adv",
            "keyword": keyword,
            "location": "india",
            "experience": experience_years,
            "pageNo": page,
            "sort": "f",  # sort by freshness
        }
        try:
            r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
            if r.status_code != 200:
                break
            data = r.json()
        except (requests.RequestException, ValueError):
            break

        job_details = data.get("jobDetails", [])
        if not job_details:
            break

        for job in job_details:
            title = job.get("title", "")
            if not title_matches_role(title):
                continue
            posted_at = None
            # Naukri gives relative freshness text like "1 day ago" or a
            # footerPlaceholderLabel / createdDate epoch (ms) in some payloads
            created_ms = job.get("createdDate")
            if created_ms:
                try:
                    posted_at = datetime.fromtimestamp(int(created_ms) / 1000, tz=timezone.utc)
                except (ValueError, OSError):
                    pass

            out.append({
                "title": title,
                "company": job.get("companyName", "Unknown"),
                "location": job.get("placeholders", {}).get("location", "") if isinstance(job.get("placeholders"), dict) else job.get("location", ""),
                "experience": job.get("experienceText", "Not specified"),
                "posted_at": posted_at,
                "apply_url": "https://www.naukri.com" + job.get("jdURL", "") if job.get("jdURL", "").startswith("/") else job.get("jdURL", ""),
                "source": "Naukri",
                "job_type": guess_job_type(title),
            })
    return out
