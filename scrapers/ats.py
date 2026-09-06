"""
Fetchers for company career-page platforms that expose PUBLIC, FREE, JSON
job-board APIs. No login, no API key, no scraping fragility — these are the
most reliable part of this whole tool. This is how you cover Series A-C
startups / unicorns without ever touching their raw HTML.
"""
from __future__ import annotations
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any

from utils import title_matches_role, guess_job_type

HEADERS = {"User-Agent": "job-search-tool/1.0 (personal use)"}
TIMEOUT = 10


def _safe_get(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


def fetch_greenhouse(slug: str) -> List[Dict[str, Any]]:
    data = _safe_get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
    if not data or "jobs" not in data:
        return []
    out = []
    for job in data["jobs"]:
        title = job.get("title", "")
        if not title_matches_role(title):
            continue
        posted_at = None
        if job.get("updated_at"):
            try:
                posted_at = datetime.fromisoformat(job["updated_at"].replace("Z", "+00:00"))
            except ValueError:
                pass
        location = (job.get("location") or {}).get("name", "")
        out.append({
            "title": title,
            "company": slug,
            "location": location,
            "experience": "Not specified",
            "posted_at": posted_at,
            "apply_url": job.get("absolute_url", ""),
            "source": "Greenhouse",
            "job_type": guess_job_type(title),
        })
    return out


def fetch_lever(slug: str) -> List[Dict[str, Any]]:
    data = _safe_get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    if not data:
        return []
    out = []
    for job in data:
        title = job.get("text", "")
        if not title_matches_role(title):
            continue
        posted_at = None
        if job.get("createdAt"):
            try:
                posted_at = datetime.fromtimestamp(job["createdAt"] / 1000, tz=timezone.utc)
            except (ValueError, OSError):
                pass
        location = (job.get("categories") or {}).get("location", "")
        out.append({
            "title": title,
            "company": slug,
            "location": location,
            "experience": "Not specified",
            "posted_at": posted_at,
            "apply_url": job.get("hostedUrl", ""),
            "source": "Lever",
            "job_type": guess_job_type(title),
        })
    return out


def fetch_ashby(slug: str) -> List[Dict[str, Any]]:
    data = _safe_get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    if not data or "jobs" not in data:
        return []
    out = []
    for job in data["jobs"]:
        title = job.get("title", "")
        if not title_matches_role(title):
            continue
        posted_at = None
        if job.get("publishedAt"):
            try:
                posted_at = datetime.fromisoformat(job["publishedAt"].replace("Z", "+00:00"))
            except ValueError:
                pass
        out.append({
            "title": title,
            "company": slug,
            "location": job.get("location", ""),
            "experience": "Not specified",
            "posted_at": posted_at,
            "apply_url": job.get("jobUrl", ""),
            "source": "Ashby",
            "job_type": guess_job_type(title),
        })
    return out


def fetch_workable(slug: str) -> List[Dict[str, Any]]:
    data = _safe_get(f"https://apply.workable.com/api/v1/widget/accounts/{slug}")
    if not data or "jobs" not in data:
        return []
    out = []
    for job in data["jobs"]:
        title = job.get("title", "")
        if not title_matches_role(title):
            continue
        posted_at = None
        if job.get("published_on"):
            try:
                posted_at = datetime.fromisoformat(job["published_on"]).replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        location = job.get("location", {})
        loc_str = ", ".join(filter(None, [location.get("city"), location.get("country")])) if isinstance(location, dict) else ""
        out.append({
            "title": title,
            "company": slug,
            "location": loc_str,
            "experience": "Not specified",
            "posted_at": posted_at,
            "apply_url": job.get("url", ""),
            "source": "Workable",
            "job_type": guess_job_type(title),
        })
    return out
