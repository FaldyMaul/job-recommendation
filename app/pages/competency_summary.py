# app/pages/competency_summary.py

import sys
from pathlib import Path
import asyncio
import streamlit as st
import nest_asyncio
nest_asyncio.apply()

# Fix path for backend imports
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

# Agents
from backend.agents.agent_profile_summarizer import summarize_user_profile
from backend.agents.agent_level_estimator import estimate_user_level
from backend.agents.agent_role_competency_mapper import map_competencies_for_role
from backend.agents.agent_extract_latest_job import extract_latest_job_role
from backend.agents.agent_cv_strengths import extract_top_strengths
from backend.rag_engine import get_all_competency_names, query_competency_by_name, query_competency

# UI Setup
st.set_page_config(page_title="📊 Competency Summary", page_icon="📊", layout="centered")
st.sidebar.title("📊 Competency Summary")
st.title("📊 Your Competency Summary")

# UI helper
def render_compact_row(item):
    percent = int((item["level"] / 5) * 100)
    with st.container():
        col1, col2 = st.columns([5, 2])
        with col1:
            st.markdown(f"**{item['competency']}** — Level: {item['level']} / 5 — Match: {percent}%")
        with col2:
            st.progress(percent / 100)
        with st.expander("ⓘ Show Detail"):
            st.markdown(f"**Definition:** {item['definition']}")
            for level in ['L1', 'L2', 'L3', 'L4', 'L5']:
                if level in item["meta"]:
                    st.markdown(f"- **{level}**: {item['meta'][level]}")

# Retrieve input
input_text = st.session_state.get("raw_input_text", "")
cv_text = st.session_state.get("cv_text", "")
manual_data = st.session_state.get("manual_data", {})
summary_text = st.session_state.get("summary_result", "")

# --- Run summarization if not yet processed
if input_text and not summary_text:
    with st.spinner("🧠 Summarizing your profile using AI..."):
        summary_text = asyncio.run(summarize_user_profile(input_text))
        st.session_state["summary_result"] = summary_text
        st.success("✅ Summary complete!")

# Stop if still no data
if not summary_text:
    st.error("⚠️ No input data or summary found. Please go back and start from profile page.")
    st.stop()

# Display profile summary
st.subheader("📋 Profile Summary")
st.markdown(summary_text)

# --- Identify role
with st.spinner("🔍 Identifying your latest job role..."):
    job_role = asyncio.run(extract_latest_job_role(summary_text)) or "Unknown Role"
    st.session_state["job_role"] = job_role

st.info(f"Recommended competencies based on your current role: **{job_role}**")

# --- Most Needed Competencies for Role
st.markdown("### 🔍 Most Needed Competencies for Your Role")
most_needed_matches = []
all_competencies = get_all_competency_names()
role_competencies = asyncio.run(map_competencies_for_role(job_role, all_competencies))

for comp in role_competencies[:5]:
    result = query_competency_by_name(comp)
    if result:
        user_level = asyncio.run(estimate_user_level(comp, summary_text))
        most_needed_matches.append({
            "competency": comp,
            "definition": result["definition"],
            "meta": result["metadata"],
            "level": user_level
        })

for item in most_needed_matches:
    render_compact_row(item)

# --- Strongest Competencies from CV
st.markdown("### 🟢 Your Strongest Competencies")
strongest_matches = []

if cv_text:
    with st.spinner("🔎 Extracting strongest competencies from CV..."):
        strength_matches_raw = asyncio.run(extract_top_strengths(cv_text, all_competencies))
        for match in strength_matches_raw:
            result = query_competency_by_name(match["competency"])
            if result:
                strongest_matches.append({
                    "competency": match["competency"],
                    "definition": result["definition"],
                    "meta": result["metadata"],
                    "level": match["level"]
                })

for item in strongest_matches:
    render_compact_row(item)

# --- Merge for Job Recommender ---
combined_competencies = most_needed_matches + strongest_matches
seen = set()
unique_competency_input = []

for comp in combined_competencies:
    if comp["competency"] not in seen:
        unique_competency_input.append({
            "competency": comp["competency"],
            "level": comp["level"]
        })
        seen.add(comp["competency"])

# Save for next step
st.session_state["final_competency_input"] = unique_competency_input

# --- CTA Button
if st.button("🚀 Get Job Recommendations Based on My Competencies"):
    st.switch_page("pages/job_recommendation.py")
