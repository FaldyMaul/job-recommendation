# app/pages/test_job_search_local.py

import os
import json
import math
import streamlit as st

st.set_page_config(page_title="🧪 Test Job Search (Local)", page_icon="🧪")
st.title("🧪 Test: View Enriched Jobs from Local JSON")

# --- Redirect Trigger ---
if st.session_state.get("redirect_gap"):
    st.session_state["redirect_gap"] = False
    st.switch_page("pages/gap_analyzer.py")

# --- Load Local JSON ---
JSON_PATH = "data/enriched_jobs.json"

try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        enriched_jobs = json.load(f).get("jobs", [])
except Exception as e:
    st.error(f"❌ Failed to load enriched jobs from JSON: {e}")
    st.stop()

# --- Simulated user summary for scoring (can be replaced with session state if needed) ---
user_summary = st.session_state.get("summary_result", "Skilled in AI, Python, and analytics.")

st.markdown(f"### Showing {len(enriched_jobs)} jobs")

# --- Render Enriched Job Results ---
for idx, job in enumerate(enriched_jobs, start=1):
    with st.container():
        title = job.get("role") or job.get("title", "Unknown Role")
        company = job.get("company") or job.get("company_name", "Unknown Company")
        location = job.get("location", "Unknown")
        industry = job.get("industry", "Unknown")
        pay = job.get("pay_usd", "N/A")
        score = int(job.get("match_score", 0))
        fit_reason = job.get("fit_reason", "No reason provided")
        description = job.get("description", "Overview")

        st.markdown(f"#### {idx}. {title} at {company}")
        st.markdown(f"📍 **Location:** {location}")
        st.markdown(f"🏢 **Industry:** {industry}")
        st.markdown(f"💰 **Estimated Pay:** {pay}")
        st.markdown(f"✅ **Match Score:** {score}%")
        st.markdown(f"💬 **Reason:** {fit_reason}")
        st.markdown(f"📰 **Description:** {description[:250]}...")

        # Button to select interest and redirect
        if st.button(f"⭐️ I'm interested", key=f"interest_{idx}"):
            st.session_state.setdefault("interested_jobs", []).append(job)
            st.session_state["selected_gap_job"] = job
            st.session_state.setdefault("summary_result", user_summary)
            st.session_state.setdefault("final_competency_input", [])
            st.session_state["redirect_gap"] = True
            st.rerun()


        st.divider()
