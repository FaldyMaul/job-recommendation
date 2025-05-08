# app/pages/job_search.py

import os
import math
import streamlit as st
import requests
import asyncio
from backend.agents.agent_enrich_job import enrich_and_score_jobs

st.set_page_config(page_title="🔎 Job Search", page_icon="🔍")
st.title("🔎 Matching Job Opportunities")

# Load API keys
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_API_URL = os.getenv("SEARCH_API_URL")

# Get user data
selected_job = st.session_state.get("selected_job")
user_summary = st.session_state.get("summary_result", "")

if not selected_job:
    st.error("Missing job selection. Please go back and choose a recommendation first.")
    st.stop()

# --- Retry-capable Search Function ---
def search_jobs(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            with st.spinner(f"Searching jobs... (attempt {attempt+1})"):
                params = {
                    "engine": "google_jobs",
                    "q": query,
                    "api_key": SEARCH_API_KEY
                }
                response = requests.get(SEARCH_API_URL, params=params)
                response.raise_for_status()
                jobs = response.json().get("jobs", [])
                if jobs:
                    return jobs
        except Exception as e:
            st.warning(f"Attempt {attempt + 1} failed: {e}")
    return []

# --- Job search ---
job_title = selected_job["title"].strip().lower()
search_query = job_title

raw_jobs = search_jobs(search_query)

# --- Job enrichment with fallback ---
if raw_jobs:
    with st.spinner("Enhancing jobs with AI..."):
        try:
            enriched_jobs = asyncio.run(enrich_and_score_jobs(raw_jobs, user_summary))
        except Exception as e:
            st.warning(f"AI enrichment failed, showing raw jobs instead: {e}")
            enriched_jobs = []
else:
    enriched_jobs = []

# --- Fallback: use raw jobs if enrichment fails ---
jobs_to_display = enriched_jobs if enriched_jobs else raw_jobs

# --- Display job cards ---
def render_jobs(jobs):
    if not jobs:
        st.warning("No matching jobs found.")
        return

    per_page = 5
    section_key = "job_results"
    page = st.session_state.get(f"page_{section_key}", 1)
    total_pages = math.ceil(len(jobs) / per_page)
    start, end = (page - 1) * per_page, page * per_page

    for job in jobs[start:end]:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                title = job.get("role") or job.get("title", "Unknown Role")
                company = job.get("company") or job.get("company_name", "Unknown Company")
                st.markdown(f"### {job['role']} at {job['company']}")
                st.markdown(f"📍 {job.get('location', 'N/A')}")
                st.markdown(f"🏢 Industry: {job.get('industry', 'Unknown')}, Type: {job.get('company_type', 'N/A')}")
                st.markdown(f"**Why it fits you:** {job.get('fit_reason', 'N/A')}")
                st.markdown(f"💰 **Pay (est.):** {job.get('pay_usd', 'N/A')}") #USD/month
                st.markdown(f"📝 {job.get('description', '')[:200]}")

                with st.expander("📄 Show Details"):
                    original = next((j.get("description", "") for j in raw_jobs if job['role'].lower() in j.get("title", "").lower()), "")
                    st.markdown(original or "No additional details available.")

                if "link" in job:
                    st.markdown(f"[🔗 View Job Posting]({job['link']})")
                

                # if st.button(f"⭐ I'm interested", key=f"{section_key}_{title}_{company}"):
                #     st.session_state.setdefault("interested_jobs", []).append(job)
                #     st.success("Added to your interested list ✅")
                if st.button(f"⭐️ I'm interested", key=f"{section_key}_{title}_{company}"):
                    # Initialize session states if missing
                    st.session_state.setdefault("interested_jobs", [])
                    st.session_state["interested_jobs"].append(job)
                    st.session_state["selected_gap_job"] = job  # Store for gap analyzer

                    # ✅ Redirect to Gap Analyzer
                    st.success("Redirecting to Gap Analyzer...")
                    st.experimental_set_query_params(page="gap_analyzer")
                    st.switch_page("app/pages/gap_analyzer.py")

            with col2:
                score = int(job.get("match_score", 0))
                st.progress(score / 100)
                st.markdown(f"**{score}% Match**")

        st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if page > 1 and st.button("⬅️ Prev", key=f"{section_key}_prev"):
            st.session_state[f"page_{section_key}"] = page - 1
            st.experimental_rerun()
    with col2:
        st.markdown(f"Page {page} of {total_pages}")
    with col3:
        if page < total_pages and st.button("➡️ Next", key=f"{section_key}_next"):
            st.session_state[f"page_{section_key}"] = page + 1
            st.experimental_rerun()

# --- Render everything ---
render_jobs(jobs_to_display)
