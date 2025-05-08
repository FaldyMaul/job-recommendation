# app/pages/gap_analyzer.py

import streamlit as st
import asyncio
from backend.agents.agent_gap_analyzer import analyze_gaps
from backend.agents.agent_extract_job_requirements import extract_job_requirements
from backend.agents.agent_learning_plan import generate_learning_plan

st.set_page_config(page_title="🧠 Gap Analyzer", page_icon="🧠")
st.title("🧠 Skill & Experience Gap Analyzer")

# --- Retrieve required session data ---
job = st.session_state.get("selected_gap_job")
cv_summary = st.session_state.get("summary_result", "")
competencies = st.session_state.get("final_competency_input", [])

if not job or not cv_summary or not competencies:
    st.error("Missing data: job selection, CV summary, or competencies not found.")
    st.stop()

# --- Run agents asynchronously ---
async def run_all_agents():
    gaps = await analyze_gaps(job, cv_summary, competencies)
    requirements = await extract_job_requirements(job.get("description", ""), cv_summary)
    plan = await generate_learning_plan(job, cv_summary, competencies, gaps, requirements)
    return gaps, requirements, plan

with st.spinner("🔍 Analyzing your profile against the job requirements..."):
    try:
        gaps, requirements, learning_plan = asyncio.run(run_all_agents())
    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")
        gaps, requirements, learning_plan = {"gaps": []}, {"requirements": []}, {"weeks": []}

# --- Display Job Info ---
st.header(f"Target Role: {job.get('title') or job.get('role', 'Unknown')} at {job.get('company_name', job.get('company', ''))}")
st.markdown(f"**Job Description Preview:** {job.get('description', '')[:300]}...")

# --- Display Match Score & Gaps Summary ---
match_score = job.get("match_score", 0)
st.progress(match_score / 100, text=f"Overall Match: {match_score}%")

# --- Display Competency Gaps ---
st.subheader("📊 Competency Gap Analysis")
data_rows = []
priority_gaps = set()
for gap in gaps.get("gaps", [])[:10]:
    if gap["type"] == "skill":
        gap_size = abs(gap['required_level'] - gap['current_level'])
        is_critical = gap_size > 1
        label = f"⭐ {gap['competency']}" if is_critical else gap['competency']
        if is_critical:
            priority_gaps.add(gap['competency'])
        data_rows.append([
            label,
            f"Level {gap['current_level']}",
            f"Level {gap['required_level']}",
            f"-{gap_size}"
        ])

if data_rows:
    st.table({
        "Competency": [row[0] for row in data_rows],
        "My Level": [row[1] for row in data_rows],
        "Target Level": [row[2] for row in data_rows],
        "Gap": [row[3] for row in data_rows]
    })
    st.markdown("These gaps highlight the areas that need development to strengthen your alignment with the job role. ⭐ indicates a key priority.")
else:
    st.info("✅ No major skill gaps found. Great work!")

# --- Display Requirement Matching ---
st.subheader("📋 Job Requirement Match")
for req in requirements.get("requirements", []):
    score = req.get("match_score", 0)
    st.markdown(f"**{req['requirement']}**")
    st.markdown(f"- Category: `{req['category']}`")
    st.markdown(f"- Match Score: **{score}%**")
    st.markdown(f"- Reason: {req['reason']}")
    st.markdown(f"- Match Explanation: {req['match_explanation']}")
    st.divider()

# --- Display Learning Plan ---
st.subheader("📚 Personalized 1-Month Learning Plan")
for week in learning_plan.get("weeks", []):
    st.markdown(f"### {week['week']}")
    st.markdown(f"**Focus:** {week['focus']}")
    st.markdown("**Activities:**")
    for activity in week.get("activities", []):
        words = activity.split()
        linked_activity = " ".join([
            f"[{word}]({word})" if word.startswith("http") else word
            for word in words
        ])
        for key in priority_gaps:
            if key.lower() in linked_activity.lower():
                linked_activity = f"⭐ {linked_activity}"
                break
        st.markdown(f"- {linked_activity}")
    st.divider()

# --- Back navigation ---
if st.button("🔙 Back to Job Search"):
    st.switch_page("pages/job_search.py")
