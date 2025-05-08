# app/pages/job_search.py

import os
import math
import json
import asyncio
import requests
import streamlit as st
from backend.agents.agent_enrich_job import enrich_and_score_jobs
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from datetime import datetime

st.set_page_config(page_title="🔎 Job Search", page_icon="🔍")
st.title("🔎 Matching Job Opportunities")

# --- Redirect Trigger to Gap Analyzer ---
if st.session_state.get("redirect_gap"):
    st.session_state["redirect_gap"] = False
    st.switch_page("pages/gap_analyzer.py")

# --- Load API keys ---
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_API_URL = os.getenv("SEARCH_API_URL")

# --- Initialize ChromaDB ---
client = PersistentClient(path="chromadb_data")
collection = client.get_or_create_collection(
    name="enriched_jobs",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
)

# --- Get user data ---
selected_job = st.session_state.get("selected_job")
user_summary = st.session_state.get("summary_result", "")

if not selected_job:
    st.error("Missing job selection. Please go back and choose a recommendation first.")
    st.stop()

# --- Retry-capable Search Function ---
def search_jobs(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            with st.spinner(f"🔍 Searching jobs... (attempt {attempt + 1})"):
                params = {
                    "engine": "google_jobs",
                    "q": query,
                    "api_key": SEARCH_API_KEY
                }
                response = requests.get(SEARCH_API_URL, params=params)
                response.raise_for_status()
                result = response.json()
                jobs = result.get("jobs") or result.get("results") or []
                if jobs:
                    return jobs
        except Exception as e:
            st.warning(f"Attempt {attempt + 1} failed: {e}")
    return []

# --- Prepare search query and cache key ---
job_title = selected_job.get("title", "").strip().lower()
search_key = f"{job_title}_{user_summary[:50]}"

# --- Check cache first ---
existing = collection.get(where={"job_title": job_title})
enriched_jobs = []

if existing and existing.get("documents"):
    try:
        enriched_jobs = [json.loads(doc) for doc in existing["documents"]]
        st.info("✅ Loaded enriched results from local cache.")
    except Exception as e:
        st.warning(f"⚠️ Failed to parse cached enrichment: {e}")

# --- Run enrichment if cache not available ---
if not enriched_jobs:
    raw_jobs = search_jobs(job_title)
    if raw_jobs:
        for attempt in range(3):
            try:
                with st.spinner(f"⚙️ Enhancing jobs with AI... (Attempt {attempt + 1})"):
                    enriched_jobs = asyncio.new_event_loop().run_until_complete(
                        enrich_and_score_jobs(raw_jobs, user_summary)
                    )
                    if enriched_jobs:
                        # Check if enrichment is actually useful
                        if all(not j.get("fit_reason") and not j.get("match_score") for j in enriched_jobs):
                            raise ValueError("LLM enrichment returned unusable data.")

                        for i, job in enumerate(enriched_jobs):
                            collection.add(
                                documents=[json.dumps(job)],
                                ids=[f"{search_key}_{i}"],
                                metadatas=[{"job_title": job_title}]
                            )
                        break  # Success
            except Exception as e:
                log_path = os.path.join("logs", "enrichment_failures.log")
                os.makedirs("logs", exist_ok=True)
                with open(log_path, "a", encoding="utf-8") as log:
                    log.write(f"{datetime.now()} - Attempt {attempt+1} failed: {str(e)}\n")
                if attempt == 2:
                    st.warning("❌ Enrichment failed after 3 attempts. Showing raw jobs.")
                    enriched_jobs = raw_jobs
    else:
        st.warning("⚠️ No jobs found from Search API.")
        enriched_jobs = []

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

    for i, job in enumerate(jobs[start:end]):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                title = job.get("role") or job.get("title", "Unknown Role")
                company = job.get("company") or job.get("company_name", "Unknown Company")
                st.markdown(f"### {title} at {company}")
                st.markdown(f"📍 {job.get('location', 'N/A')}")
                st.markdown(f"🏢 Industry: {job.get('industry', 'Unknown')}, Type: {job.get('company_type', 'N/A')}")
                st.markdown(f"**Why it fits you:** {job.get('fit_reason', 'N/A')}")
                st.markdown(f"💰 **Pay (est.):** {job.get('pay_usd', 'N/A')}")
                st.markdown(f"📝 {job.get('description', '')[:200]}")

                with st.expander("📄 Show Details"):
                    st.markdown(job.get("description", "No additional details available."))

                if "link" in job:
                    st.markdown(f"[🔗 View Job Posting]({job['link']})")

                unique_key = f"{section_key}_{i}_{title[:10]}_{company[:10]}"
                if st.button(f"⭐️ I'm interested", key=unique_key):
                    st.session_state.setdefault("interested_jobs", []).append(job)
                    st.session_state["selected_gap_job"] = job
                    st.session_state["selected_job"] = selected_job
                    st.session_state.setdefault("summary_result", user_summary)
                    st.session_state.setdefault("final_competency_input", [])
                    st.session_state["redirect_gap"] = True
                    st.switch_page("pages/gap_analyzer.py")

            with col2:
                score = int(job.get("match_score", 0))
                st.progress(score / 100)
                st.markdown(f"**{score}% Match**")

        st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if page > 1 and st.button("⬅️ Prev", key=f"{section_key}_prev"):
            st.session_state[f"page_{section_key}"] = page - 1
            st.rerun()
    with col2:
        st.markdown(f"Page {page} of {total_pages}")
    with col3:
        if page < total_pages and st.button("➡️ Next", key=f"{section_key}_next"):
            st.session_state[f"page_{section_key}"] = page + 1
            st.rerun()

# --- Run UI ---
render_jobs(enriched_jobs)
