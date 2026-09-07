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
    try:
        return _fetch_greenhouse_impl(slug)
    except Exception:
        # Any unexpected shape/None/missing-key from this API should never
        # crash the whole app -- just treat this company as "no results".
        return []


def fetch_lever(slug: str) -> List[Dict[str, Any]]:
    try:
        return _fetch_lever_impl(slug)
    except Exception:
        # Any unexpected shape/None/missing-key from this API should never
        # crash the whole app -- just treat this company as "no results".
        return []


def fetch_ashby(slug: str) -> List[Dict[str, Any]]:
    try:
        return _fetch_ashby_impl(slug)
    except Exception:
        # Any unexpected shape/None/missing-key from this API should never
        # crash the whole app -- just treat this company as "no results".
        return []


def fetch_workable(slug: str) -> List[Dict[str, Any]]:
    try:
        return _fetch_workable_impl(slug)
    except Exception:
        # Any unexpected shape/None/missing-key from this API should never
        # crash the whole app -- just treat this company as "no results".
        return []


def _fetch_greenhouse_impl(slug: str) -> List[Dict[str, Any]]:
    data = _safe_get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
    if not data or "jobs" not in data:
        return []
    out = []
    for job in data["jobs"]:
        try:
            if not isinstance(job, dict):
                continue
            title = job.get("title", "")
            if not title_matches_role(title):
                continue
            posted_at = None
            if job.get("updated_at"):
                try:
                    posted_at = datetime.fromisoformat(str(job["updated_at"]).replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            loc = job.get("location")
            location = loc.get("name", "") if isinstance(loc, dict) else (loc or "")
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
        except Exception:
            continue
    return out


def _fetch_lever_impl(slug: str) -> List[Dict[str, Any]]:
    data = _safe_get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    if not data:
        return []
    out = []
    for job in data:
        try:
            if not isinstance(job, dict):
                continue
            title = job.get("text", "")
            if not title_matches_role(title):
                continue
            posted_at = None
            if job.get("createdAt"):
                try:
                    posted_at = datetime.fromtimestamp(job["createdAt"] / 1000, tz=timezone.utc)
                except (ValueError, OSError, TypeError):
                    pass
            cats = job.get("categories")
            location = cats.get("location", "") if isinstance(cats, dict) else ""
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
        except Exception:
            continue
    return out


def _fetch_ashby_impl(slug: str) -> List[Dict[str, Any]]:
    data = _safe_get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    if not data or "jobs" not in data:
        return []
    out = []
    for job in data["jobs"]:
        try:
            if not isinstance(job, dict):
                continue
            title = job.get("title", "")
            if not title_matches_role(title):
                continue
            posted_at = None
            if job.get("publishedAt"):
                try:
                    posted_at = datetime.fromisoformat(str(job["publishedAt"]).replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            out.append({
                "title": title,
                "company": slug,
                "location": job.get("location", "") or "",
                "experience": "Not specified",
                "posted_at": posted_at,
                "apply_url": job.get("jobUrl", ""),
                "source": "Ashby",
                "job_type": guess_job_type(title),
            })
        except Exception:
            continue
    return out


def _fetch_workable_impl(slug: str) -> List[Dict[str, Any]]:
    data = _safe_get(f"https://apply.workable.com/api/v1/widget/accounts/{slug}")
    if not data or "jobs" not in data:
        return []
    out = []
    for job in data["jobs"]:
        try:
            if not isinstance(job, dict):
                continue
            title = job.get("title", "")
            if not title_matches_role(title):
                continue
            posted_at = None
            if job.get("published_on"):
                try:
                    posted_at = datetime.fromisoformat(str(job["published_on"])).replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    pass
            location = job.get("location") or {}
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
        except Exception:
            continue
    return out
