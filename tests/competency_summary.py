# app/pages/competency_summary.py

import sys
from pathlib import Path
import asyncio
import streamlit as st
import nest_asyncio
nest_asyncio.apply()

# Fix import path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

# Import agents and backend
from backend.agents.agent_profile_summarizer import summarize_user_profile
from backend.agents.agent_level_estimator import estimate_user_level
from backend.agents.agent_job_title_extractor import extract_job_title
from backend.agents.agent_role_competency_mapper import map_competencies_for_role
from backend.agents.agent_extract_latest_job import extract_latest_job_role
from backend.agents.agent_cv_strengths import extract_top_strengths
from backend.agents.agent_job_recommender import recommend_jobs_from_competencies
from backend.rag_engine import get_all_competency_names, query_competency_by_name, query_competency

# Setup Streamlit page
st.set_page_config(page_title="📊 Competency Summary", page_icon="📊", layout="centered")
st.sidebar.title("📊 Competency Summary")
st.title("📊 Your Competency Summary")


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


# --- Input Source Detection ---
cv_text = st.session_state.get("cv_text", "")
linkedin_url = st.session_state.get("linkedin_url", "")
manual_data = st.session_state.get("manual_data", {})
input_text = ""

if cv_text:
    st.info("Using uploaded CV text for summarization.")
    input_text = cv_text
elif linkedin_url:
    st.warning("LinkedIn summarization not yet implemented.")
    input_text = ""
elif manual_data:
    st.info("Using manually filled data.")
    input_text = f"{manual_data.get('education')}\n{manual_data.get('experience')}\nSkills: {manual_data.get('skills')}"
else:
    st.error("No valid input data found. Please return to the previous step.")
    st.stop()

# --- LLM Summarization and Competency Match ---
if input_text and st.button("🔍 Summarize and Extract Competencies"):
    with st.spinner("Analyzing profile with LLM..."):
        summary_text = asyncio.run(summarize_user_profile(input_text))
        st.session_state["summary_result"] = summary_text
        st.success("Summary complete!")

    with st.spinner("Matching competencies via RAG..."):
        competency_matches = query_competency(summary_text, top_k=5)
        st.session_state["competency_matches"] = competency_matches
        st.success("Competency match completed!")

# --- Display Summary ---
summary_text = st.session_state.get("summary_result", "")
if summary_text:
    st.subheader("📋 Profile Summary")
    st.markdown(summary_text)

# --- Infer Job Role from Profile ---
job_role = asyncio.run(extract_latest_job_role(summary_text))
if not job_role:
    job_role = "Unknown Role"

st.info(f"🔍 Recommended competencies based on your current role: **{job_role}**")

# --- Section 1: Most Needed Competencies for Role ---
st.markdown("### 🔍 Most Needed Competencies for Your Role")
all_competencies = get_all_competency_names()
role_competencies = asyncio.run(map_competencies_for_role(job_role, all_competencies))
most_needed_matches = []

for comp in role_competencies[:5]:
    result = query_competency_by_name(comp)
    if result:
        meta = result["metadata"]
        doc = result["definition"]
        user_level = asyncio.run(estimate_user_level(comp, summary_text))
        most_needed_matches.append({
            "competency": comp,
            "definition": doc,
            "level": user_level,
            "meta": meta
        })

for item in most_needed_matches:
    render_compact_row(item)

# --- Section 2: Strongest Competencies from CV ---
st.markdown("### 🟢 Your Strongest Competencies")
strength_matches_raw = asyncio.run(extract_top_strengths(cv_text, all_competencies))
strongest_matches = []

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

# --- Combine for Job Recommendation ---
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

# --- Job Recommendations ---
if st.button("🚀 Get Job Recommendations Based on My Competencies"):
    st.session_state["final_competency_input"] = unique_competency_input
    st.switch_page("pages/job_recommendation.py")
