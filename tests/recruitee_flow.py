# app/pages/recruitee_flow.py

import sys
from pathlib import Path

# Add the project root to sys.path so 'backend' is importable
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))


import streamlit as st
from PyPDF2 import PdfReader
import base64

st.set_page_config(page_title="📤 Share Your Profile", page_icon="📤", layout="centered")
st.sidebar.title("📤 Share Your Profile")

st.title("📤 Share Your Profile")


# st.set_page_config(page_title="Recruitee Profiling", layout="wide")
# st.title("👤 Recruitee Journey")
st.write("This is the Recruitee profiling step.")
st.subheader("Step 1: Let's Understand You First")

st.markdown("Please upload your **CV**, share your **LinkedIn URL**, or manually **fill in your data** below.")

# --- Method 1: Upload CV ---
cv_file = st.file_uploader("📄 Upload your CV (PDF format)", type=["pdf"])

cv_text = ""
if cv_file:
    try:
        pdf = PdfReader(cv_file)
        cv_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        st.success("CV successfully processed!")
        st.text_area("Extracted CV Text:", cv_text, height=300)
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")

# --- Method 2: LinkedIn URL ---
linkedin_url = st.text_input("🔗 Or enter your LinkedIn profile URL")

# --- Method 3: Manual Input ---
with st.expander("✍️ Or fill in your information manually"):
    name = st.text_input("Full Name")
    education = st.text_area("Educational Background")
    experience = st.text_area("Work Experience")
    skills = st.text_input("List of Skills (comma-separated)")

# ---- NEXT BUTTON ----
if st.button("➡️ Continue to Competency Summary"):
    st.session_state['cv_text'] = cv_text
    st.session_state['linkedin_url'] = linkedin_url
    st.session_state['manual_data'] = {
        "name": name,
        "education": education,
        "experience": experience,
        "skills": skills
    }
    st.success("Profile received! Now analyzing your competencies...")
    st.switch_page("pages/competency_summary.py")

    # st.switch_page("pages/competency_summary.py")
