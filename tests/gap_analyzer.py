# app/pages/gap_analyzer.py

import streamlit as st
import asyncio
from backend.agents.agent_gap_analyzer import analyze_gaps
from backend.agents.agent_extract_job_requirements import extract_job_requirements

st.set_page_config(page_title="🧠 Gap Analyzer", page_icon="🧠")
st.title("🧠 Skill & Experience Gap Analyzer")

# --- Retrieve required session data ---
job = st.session_state.get("selected_gap_job")
cv_summary = st.session_state.get("summary_result", "")
competencies = st.session_state.get("final_competency_input", [])

if not job:
    st.error("❌ No job selected. Please go back and select a job from the search.")
    st.stop()
if not cv_summary:
    st.error("❌ CV summary missing. Please complete your profile first.")
    st.stop()
if not competencies:
    st.error("❌ No competencies provided. Please generate or input your competency list.")
    st.stop()

# --- Run agents asynchronously ---
async def run_all_agents():
    return await asyncio.gather(
        analyze_gaps(job, cv_summary, competencies),
        extract_job_requirements(job.get("description", ""), cv_summary)
    )

with st.spinner("🔍 Analyzing your profile against the job requirements..."):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        gaps, requirements = loop.run_until_complete(run_all_agents())
    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")
        gaps, requirements = {"gaps": []}, {"requirements": []}

# Ensure structure
if not isinstance(gaps, dict):
    gaps = {"gaps": []}
if not isinstance(requirements, dict):
    requirements = {"requirements": []}

# Save results to session (optional)
st.session_state["last_gap_analysis"] = gaps
st.session_state["last_requirements"] = requirements

# --- Display Job Info ---
st.header(f"Target Role: {job.get('title')} at {job.get('company_name', job.get('company', ''))}")
st.markdown(f"**Job Description Preview:** {job.get('description', '')[:300]}")

# --- Display Competency Gaps ---
st.subheader("📊 Competency Gap Analysis")
data_rows = []
for gap in gaps.get("gaps", []):
    if gap.get("type") == "skill":
        data_rows.append([
            gap.get("competency", "-"),
            f"Level {gap.get('current_level', 0)}",
            f"Level {gap.get('required_level', 0)}",
            f"-{abs(gap.get('required_level', 0) - gap.get('current_level', 0))}"
        ])

if data_rows:
    st.table({
        "Competency": [row[0] for row in data_rows],
        "My Level": [row[1] for row in data_rows],
        "Target Level": [row[2] for row in data_rows],
        "Gap": [row[3] for row in data_rows]
    })
else:
    st.info("✅ No major skill gaps found. Great work!")

# --- Display Requirement Matching ---
st.subheader("📋 Job Requirement Match")
for req in requirements.get("requirements", []):
    score = req.get("match_score", 0)
    st.markdown(f"**{req.get('requirement', 'Unknown Requirement')}**")
    st.markdown(f"- Category: `{req.get('category', '-')}`")
    st.markdown(f"- Match Score: **{score}%**")
    st.markdown(f"- Reason: {req.get('reason', '-')}")
    st.markdown(f"- Match Explanation: {req.get('match_explanation', '-')}")
    st.divider()

# --- Back navigation ---
if st.button("🔙 Back to Job Search"):
    st.switch_page("pages/job_search.py")
