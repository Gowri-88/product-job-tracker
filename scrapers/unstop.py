"""
BEST-EFFORT Unstop fetcher.

Unstop (formerly Dare2Compete) lists jobs & internships and its site calls
a public search-results JSON endpoint under the hood. Like the Naukri
fetcher, this is unofficial and can change without notice. If it breaks:
open unstop.com/jobs in a browser, DevTools -> Network tab, find the
XHR request that returns job results, and update BASE_URL / params below
to match.
"""
from __future__ import annotations
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any

from utils import title_matches_role, guess_job_type

BASE_URL = "https://unstop.com/api/public/opportunity/search-result"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def fetch_unstop(opportunity_type: str = "jobs", pages: int = 2) -> List[Dict[str, Any]]:
    """opportunity_type: 'jobs' or 'internships'"""
    out: List[Dict[str, Any]] = []
    for page in range(1, pages + 1):
        params = {
            "opportunity": opportunity_type,
            "page": page,
            "per_page": 20,
            "oppstatus": "open",
        }
        try:
            r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
            if r.status_code != 200:
                break
            data = r.json()
        except (requests.RequestException, ValueError):
            break

        items = (data.get("data") or {}).get("data", [])
        if not items:
            break

        for job in items:
            title = job.get("title", "")
            if not title_matches_role(title):
                continue
            posted_at = None
            if job.get("start_date"):
                try:
                    posted_at = datetime.fromisoformat(job["start_date"].replace("Z", "+00:00"))
                except ValueError:
                    pass

            organisation = job.get("organisation", {})
            out.append({
                "title": title,
                "company": organisation.get("name", "Unknown") if isinstance(organisation, dict) else "Unknown",
                "location": job.get("region", "India") or "India",
                "experience": "Fresher / Entry-level",
                "posted_at": posted_at,
                "apply_url": f"https://unstop.com/{job.get('public_url', '')}",
                "source": "Unstop",
                "job_type": "Internship" if opportunity_type == "internships" else guess_job_type(title),
            })
    return out
