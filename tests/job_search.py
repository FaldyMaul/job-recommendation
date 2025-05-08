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

# --- Search Google Jobs ---
# def search_jobs(query):
#     try:
#         params = {
#             "engine": "google_jobs",
#             "q": query,
#             "api_key": SEARCH_API_KEY
#         }
#         response = requests.get(SEARCH_API_URL, params=params)
#         response.raise_for_status()
#         return response.json().get("jobs", [])
#     except Exception as e:
#         st.warning(f"No results for '{query}'. Reason: {e}")
#         return []
def search_jobs(query, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            params = {
                "engine": "google_jobs",
                "q": query,
                "api_key": SEARCH_API_KEY
            }
            response = requests.get(SEARCH_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            jobs = data.get("jobs", [])
            if jobs:
                return jobs
            else:
                attempt += 1
        except Exception as e:
            st.warning(f"Attempt {attempt + 1} failed for '{query}': {e}")
            attempt += 1
    return []


# --- Clean and normalize job title ---
job_title = selected_job["title"].strip().lower()
local_query = f"{job_title} in Indonesia"
global_query = job_title

local_raw = search_jobs(local_query)
global_raw = search_jobs(global_query)

local_jobs = asyncio.run(enrich_and_score_jobs(local_raw, user_summary)) if local_raw else []
global_jobs = asyncio.run(enrich_and_score_jobs(global_raw, user_summary)) if global_raw else []

# --- Render Results ---
def render_jobs(jobs, section_title, section_key):
    st.markdown(f"## {section_title}")
    if not jobs:
        st.warning("No jobs found in this section.")
        return

    per_page = 5
    page = st.session_state.get(f"page_{section_key}", 1)
    total_pages = math.ceil(len(jobs) / per_page)
    start, end = (page - 1) * per_page, (page) * per_page

    for job in jobs[start:end]:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {job['role']} at {job['company']}")
                st.markdown(f"📍 {job.get('location', 'N/A')}")
                st.markdown(f"🏢 Industry: {job.get('industry', 'Unknown')}, Type: {job.get('company_type', 'N/A')}")
                st.markdown(f"**Why it fits you:** {job.get('fit_reason', 'N/A')}")
                st.markdown(f"💰 **Pay (est.):** {job.get('pay_usd', 'N/A')} USD/month")
                st.markdown(f"📝 {job.get('description', '')[:800]}")
                # with st.expander("📄 Show Details"):
                    

                if "link" in job:
                    st.markdown(f"[🔗 View Job Posting]({job['link']})")

                if st.button(f"⭐ I'm interested", key=f"{section_key}_{job['role']}_{job['company']}"):
                    st.session_state.setdefault("interested_jobs", []).append(job)
                    st.success("Added to your interested list ✅")

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

# --- Render All Sections ---
render_jobs(local_jobs, "🇮🇩 Jobs in Indonesia", "local")
render_jobs(global_jobs, "🌍 Global Jobs (#KaburAjaDulu)", "global")
