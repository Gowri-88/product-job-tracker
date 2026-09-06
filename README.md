# Product Role Fresher Job Tracker (India)

A free, self-hosted tool that searches for fresher / 0–1 yr Product Manager,
Product Analyst, APM, and related openings in India, with a time-window
filter (24h / 2d / 3d / 1 week) and a one-click refresh.

## How it actually gets data (read this first)

Full real-time scraping of LinkedIn, Naukri, Indeed, Wellfound, Google, etc.
**for free, with zero missed listings, isn't something any tool can
honestly promise** — those platforms either have no free API, block
scraping aggressively, or both. This tool takes the most reliable free
path instead:

| Source | How | Reliability |
|---|---|---|
| **Greenhouse / Lever / Ashby / Workable** | Official public JSON APIs used by the ATS platforms many startups/unicorns use for their careers page | ✅ High — stable, free, no scraping |
| **Naukri** | Their internal search JSON endpoint (same one their own frontend calls) | ⚠️ Medium — unofficial, can change |
| **Unstop** | Their internal search JSON endpoint | ⚠️ Medium — unofficial, can change |
| **LinkedIn** (off by default) | Public no-login job search page | ⚠️ Low — rate-limited, JS-heavy, ToS grey area |
| **Wellfound** (off by default) | Placeholder only — needs a headless browser (Playwright) to work reliably; not implemented by default | ❌ Not implemented |
| **Google Jobs / "everywhere"** | Not included — Google has no free API for this. The only programmatic access is paid (SerpApi, ~$25/mo+). Since you wanted free, this is skipped. In practice, Naukri + company sites + LinkedIn already cover the large majority of what Google Jobs would surface. | N/A |

**Bottom line:** this will reliably catch fresh openings at any startup
using Greenhouse/Lever/Ashby/Workable (very common for Series A–C and many
unicorns), plus a good chunk of Naukri and Unstop listings. It will **not**
catch everything, everywhere, within one minute — nothing free can. Treat
it as your best daily/weekly sweep, not your only source.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

This opens a local live webpage in your browser with the search button and filters.

## Deploy it as a real hosted webpage (free)

1. Push this folder to a GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click "New app", pick your repo and `app.py`.
4. Deploy. You get a free public URL you can open from your phone or laptop any time you want to check.

## Expanding company coverage (the most important step)

`config.py` ships with only a handful of starter company slugs, and **I
could not verify them live from this environment** — companies switch ATS
vendors, so treat them as a starting point, not a guarantee.

To add more companies:

1. Go to a company's website → "Careers" / "We're hiring" link.
2. Look at the URL it takes you to:
   - `boards.greenhouse.io/<slug>` → Greenhouse
   - `jobs.lever.co/<slug>` → Lever
   - `jobs.ashbyhq.com/<slug>` → Ashby
   - `apply.workable.com/<slug>` → Workable
   - Anything else (custom career site) → not covered by this method; would need a custom scraper per company.
3. Verify it works:
   ```bash
   python test_slug.py greenhouse <slug>
   ```
4. If it prints ✅, add the slug to the matching list in `config.py`.

Spend 20–30 minutes doing this for the 30–40 startups/unicorns you
actually want to track — that's what will make this tool "broad" for you,
more than any scraper trick will.

## Tuning what counts as a match

Edit `config.py`:
- `ROLE_KEYWORDS` — titles to match (add "product owner", "strategy
  analyst", etc. if relevant to you)
- `EXCLUDE_KEYWORDS` — seniority terms to filter out
- `LOCATION_KEYWORDS` — cities/keywords to keep
- `TIME_WINDOWS` — the dropdown options in the UI

## If Naukri or Unstop fetchers stop returning results

These use unofficial internal endpoints, discovered via browser DevTools.
If they break:

1. Open naukri.com (or unstop.com) in Chrome, search for your role.
2. Open DevTools → Network tab → filter by "Fetch/XHR".
3. Find the request that returns job results as JSON.
4. Compare its URL/params/headers to `scrapers/naukri.py` (or `unstop.py`)
   and update accordingly.

## Known limitations, honestly

- "Posted 1 minute ago" freshness isn't achievable — you're bound by how
  fast each source's own systems index a listing, typically anywhere from
  minutes to hours.
- Experience filtering is only as good as what each source exposes; many
  listings don't state years of experience explicitly, so those are kept
  (not dropped) for you to manually judge — check the "Experience" column.
- LinkedIn and Wellfound are off by default because they're the least
  reliable/most fragile free options. Turn them on in the sidebar if you
  want to experiment, but expect inconsistent results.
- This tool is for personal job-search use — please don't hammer any of
  these endpoints with high-frequency automated requests (the code
  deliberately doesn't add scheduling/looping for this reason).
