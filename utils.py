"""
Shared helpers: normalizing listings into one schema, filtering, dedupe.
Every scraper returns a list of dicts with this schema:

{
    "title": str,
    "company": str,
    "location": str,
    "experience": str,       # free text, e.g. "0-1 yrs" or "Not specified"
    "posted_at": datetime | None,   # timezone-aware UTC if known
    "apply_url": str,
    "source": str,           # e.g. "Greenhouse", "Naukri"
    "job_type": str,         # "Full-time" | "Internship" | "Unknown"
}
"""
from __future__ import annotations
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from config import ROLE_KEYWORDS, EXCLUDE_KEYWORDS, LOCATION_KEYWORDS


def title_matches_role(title: str) -> bool:
    t = title.lower()
    if any(bad in t for bad in EXCLUDE_KEYWORDS):
        return False
    return any(kw in t for kw in ROLE_KEYWORDS)


def location_matches_india(location: str) -> bool:
    if not location:
        return True  # unknown location -> keep, let user judge
    loc = location.lower()
    return any(kw in loc for kw in LOCATION_KEYWORDS)


def guess_job_type(title: str) -> str:
    t = title.lower()
    if "intern" in t:
        return "Internship"
    if "ppo" in t:
        return "PPO / Internship"
    return "Full-time"


def within_time_window(posted_at, hours: int) -> bool:
    """If posted_at is unknown (None), we KEEP it but flag it — better to
    over-include than silently drop a real opening because a site didn't
    expose a clean timestamp."""
    if posted_at is None:
        return True
    now = datetime.now(timezone.utc)
    return (now - posted_at) <= timedelta(hours=hours)


def dedupe(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for item in listings:
        key = (
            item.get("company", "").strip().lower(),
            re.sub(r"\s+", " ", item.get("title", "")).strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def sort_by_recency(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def sort_key(item):
        pa = item.get("posted_at")
        # unknowns sort last
        return pa if pa is not None else datetime(1970, 1, 1, tzinfo=timezone.utc)
    return sorted(listings, key=sort_key, reverse=True)
