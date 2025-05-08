# app/pages/recruitee_flow.py

import sys
from pathlib import Path
import streamlit as st
from PyPDF2 import PdfReader
import asyncio
import base64

# Path setup
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from backend.agents.agent_profile_summarizer import summarize_user_profile
from backend.rag_engine import query_competency

# Page config
st.set_page_config(page_title="📤 Share Your Profile", page_icon="📤", layout="centered")
st.sidebar.title("📤 Share Your Profile")
st.title("📤 Share Your Profile")
st.write("This is the Recruitee profiling step.")
st.subheader("Step 1: Let's Understand You First")

# --- Input: Full Name
# full_name = st.text_input("🙋 Full Name")

# --- Input: Upload CV
st.markdown("Please upload your **CV**, share your **LinkedIn URL**, or manually **fill in your data** below.")
cv_file = st.file_uploader("📄 Upload your CV (PDF format)", type=["pdf"])

cv_text = ""
if cv_file:
    try:
        pdf = PdfReader(cv_file)
        cv_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        st.success("✅ CV successfully uploaded!")
    except Exception as e:
        st.error(f"❌ Failed to read PDF: {e}")

# --- Input: LinkedIn
linkedin_url = st.text_input("🔗 Or enter your LinkedIn profile URL")

# --- Input: Manual fields
with st.expander("✍️ Or fill in your information manually"):
    education = st.text_area("🎓 Educational Background")
    experience = st.text_area("💼 Work Experience")
    skills = st.text_input("🛠️ List of Skills (comma-separated)")

# --- Button: Analyze Profile
if st.button("🚀 Analyze Your Profile"):
    input_text = ""

    if cv_text:
        input_text = cv_text
        st.session_state["cv_text"] = cv_text
    elif linkedin_url:
        input_text = f"LinkedIn URL: {linkedin_url}"
        st.session_state["linkedin_url"] = linkedin_url
    elif any([education, experience, skills]):
        input_text = f"{education}\n{experience}\nSkills: {skills}"
        st.session_state["manual_data"] = {
            "name": full_name,
            "education": education,
            "experience": experience,
            "skills": skills
        }
    else:
        st.error("⚠️ Please upload a CV or fill out at least one profile input.")
        st.stop()

    # Summarize and save results
    with st.spinner("🧠 Summarizing your profile using LLM..."):
        summary = asyncio.run(summarize_user_profile(input_text))
        st.session_state["summary_result"] = summary
        st.success("✅ Profile analysis complete!")

    # Get competency matches (optional preloading to save time)
    with st.spinner("🔍 Preloading competency matches..."):
        matches = query_competency(summary, top_k=5)
        st.session_state["competency_matches"] = matches

    st.switch_page("pages/competency_summary.py")
