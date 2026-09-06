"""
Product Role Fresher Job Tracker — India
Run locally:      streamlit run app.py
Deploy free:      push to GitHub, connect repo at share.streamlit.io
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from config import (
    GREENHOUSE_COMPANIES, LEVER_COMPANIES, ASHBY_COMPANIES, WORKABLE_COMPANIES,
    TIME_WINDOWS, DEFAULT_SOURCES_ENABLED,
)
from utils import within_time_window, dedupe, sort_by_recency, location_matches_india
from scrapers.ats import fetch_greenhouse, fetch_lever, fetch_ashby, fetch_workable
from scrapers.naukri import fetch_naukri
from scrapers.unstop import fetch_unstop
from scrapers.optional_sources import fetch_linkedin_public, fetch_wellfound_placeholder

st.set_page_config(page_title="Product Fresher Job Tracker", layout="wide")

st.title("🎯 Product Role Fresher Job Tracker — India")
st.caption(
    "Fresher / 0–1 yr Product Manager, Product Analyst, APM, and related "
    "roles, aggregated from company career-page APIs + Naukri + Unstop."
)

# --- Sidebar controls ------------------------------------------------------
st.sidebar.header("Filters")
time_window_label = st.sidebar.selectbox("Posted within", list(TIME_WINDOWS.keys()), index=0)
time_window_hours = TIME_WINDOWS[time_window_label]

job_type_filter = st.sidebar.multiselect(
    "Job type",
    ["Full-time", "Internship", "PPO / Internship", "Unknown"],
    default=["Full-time", "Internship", "PPO / Internship", "Unknown"],
)

india_only = st.sidebar.checkbox("India locations only (best-effort filter)", value=True)

st.sidebar.header("Sources")
enabled_sources = {}
for name, default in DEFAULT_SOURCES_ENABLED.items():
    enabled_sources[name] = st.sidebar.checkbox(name, value=default)

st.sidebar.markdown("---")
st.sidebar.caption(
    "⚠️ Naukri, LinkedIn, Wellfound sources use unofficial endpoints. "
    "They can break or get rate-limited. Company-API sources "
    "(Greenhouse/Lever/Ashby/Workable) are the most reliable."
)


@st.cache_data(ttl=600, show_spinner=False)
def run_search(enabled: dict):
    all_listings = []

    if enabled.get("Greenhouse"):
        for slug in GREENHOUSE_COMPANIES:
            all_listings += fetch_greenhouse(slug)
    if enabled.get("Lever"):
        for slug in LEVER_COMPANIES:
            all_listings += fetch_lever(slug)
    if enabled.get("Ashby"):
        for slug in ASHBY_COMPANIES:
            all_listings += fetch_ashby(slug)
    if enabled.get("Workable"):
        for slug in WORKABLE_COMPANIES:
            all_listings += fetch_workable(slug)
    if enabled.get("Naukri"):
        all_listings += fetch_naukri("product manager", experience_years=0)
        all_listings += fetch_naukri("product analyst", experience_years=0)
        all_listings += fetch_naukri("associate product manager", experience_years=0)
    if enabled.get("Unstop"):
        all_listings += fetch_unstop("jobs")
        all_listings += fetch_unstop("internships")
    if enabled.get("LinkedIn (best-effort)"):
        all_listings += fetch_linkedin_public("product manager fresher")
        all_listings += fetch_linkedin_public("product analyst")
    if enabled.get("Wellfound (best-effort)"):
        all_listings += fetch_wellfound_placeholder("product")

    return all_listings


# --- Main button -------------------------------------------------------
col1, col2 = st.columns([1, 4])
with col1:
    search_clicked = st.button("🔍 Search Now", type="primary", use_container_width=True)
with col2:
    st.write("")  # spacing

if "results" not in st.session_state:
    st.session_state.results = None
    st.session_state.last_run = None

if search_clicked:
    with st.spinner("Fetching from all enabled sources..."):
        raw = run_search(enabled_sources)
        raw = dedupe(raw)
        raw = [r for r in raw if within_time_window(r["posted_at"], time_window_hours)]
        if india_only:
            raw = [r for r in raw if location_matches_india(r["location"])]
        raw = [r for r in raw if r["job_type"] in job_type_filter]
        raw = sort_by_recency(raw)
        st.session_state.results = raw
        st.session_state.last_run = datetime.now(timezone.utc)

# --- Results display -----------------------------------------------------
if st.session_state.results is not None:
    results = st.session_state.results
    st.success(
        f"Found {len(results)} matching openings · "
        f"last fetched {st.session_state.last_run.strftime('%Y-%m-%d %H:%M UTC')}"
    )

    if results:
        df = pd.DataFrame(results)
        df["posted_at"] = df["posted_at"].apply(
            lambda d: d.strftime("%Y-%m-%d %H:%M UTC") if d is not None else "Unknown"
        )
        df = df[["title", "company", "location", "experience", "job_type", "source", "posted_at", "apply_url"]]
        df.columns = ["Title", "Company", "Location", "Experience", "Type", "Source", "Posted", "Apply Link"]

        # category breakdown
        st.subheader("By source")
        st.bar_chart(pd.DataFrame(results)["source"].value_counts())

        st.subheader("Results")
        st.dataframe(
            df,
            column_config={
                "Apply Link": st.column_config.LinkColumn("Apply Link"),
            },
            use_container_width=True,
            hide_index=True,
        )

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv, "product_jobs.csv", "text/csv")
    else:
        st.warning(
            "No matches in this time window from the enabled sources. "
            "Try a wider time window, enable more sources, or check your "
            "company list in config.py."
        )
else:
    st.info("Set your filters on the left, then click **Search Now**.")
