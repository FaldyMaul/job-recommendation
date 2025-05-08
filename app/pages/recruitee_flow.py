# app/pages/recruitee_flow.py

import sys
from pathlib import Path
import streamlit as st
from PyPDF2 import PdfReader

# Path setup
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

# Page config
st.set_page_config(page_title="📤 Share Your Profile", page_icon="📤", layout="centered")
st.sidebar.title("📤 Share Your Profile")
st.title("📤 Share Your Profile")
st.write("This is the Recruitee profiling step.")
st.subheader("Step 1: Let's Understand You First")

# --- Input: Upload CV ---
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

# --- Input: LinkedIn ---
linkedin_url = st.text_input("🔗 Or enter your LinkedIn profile URL")

# --- Input: Manual Fields ---
with st.expander("✍️ Or fill in your information manually"):
    name = st.text_input("Full Name")
    education = st.text_area("🎓 Educational Background")
    experience = st.text_area("💼 Work Experience")
    skills = st.text_input("🛠️ List of Skills (comma-separated)")

# --- Button: Just Save & Redirect ---
if st.button("🚀 Analyze Your Profile"):
    input_text = ""

    if cv_text:
        input_text = cv_text
        st.session_state["cv_text"] = cv_text

    elif linkedin_url:
        input_text = f"LinkedIn URL: {linkedin_url}"
        st.session_state["linkedin_url"] = linkedin_url

    elif any([name, education, experience, skills]):
        input_text = f"{education}\n{experience}\nSkills: {skills}"
        st.session_state["manual_data"] = {
            "name": name,
            "education": education,
            "experience": experience,
            "skills": skills
        }

    else:
        st.error("⚠️ Please upload a CV or fill out at least one profile input.")
        st.stop()

    # Save text to be summarized later
    st.session_state["raw_input_text"] = input_text

    # Redirect to next page immediately
    st.switch_page("pages/competency_summary.py")
