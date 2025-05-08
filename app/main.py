# app/main.py
import sys
from pathlib import Path
import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"


# Add the project root to sys.path so 'backend' is importable
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))



import streamlit as st

# ✅ MUST be the first Streamlit command
st.set_page_config(page_title="🏠 Home", page_icon="🏠", layout="centered")

# Sidebar menu label (simulated, not real label override)
st.sidebar.title("🏠 Home")

st.title("🎯 Your Personal AI Job Assistant")
st.subheader("Welcome! Please choose your role to begin:")

# st.sidebar.title("🏠 Home")

# st.set_page_config(page_title="AI Job Recommender", layout="centered")

# st.title("🎯 RAG-Based Multi-Agent Job Recommender")
# st.subheader("Welcome! Please choose your role to begin:")

# NEW: Name Input
name = st.text_input("Your Name", placeholder="e.g. Draco Malfoy")
if name:
    st.session_state["user_name"] = name

# Role selection
role = st.radio("Select your role:", ("Recruitee", "Recruiter"))
st.session_state["user_role"] = role

if role == "Recruitee":
    # st.success("You are a Recruitee. Please continue to the profiling step.")
    if st.button("🚀 Start Your Profiling Journey"):
        st.switch_page("pages/recruitee_flow.py")

elif role == "Recruiter":
    st.info("Recruiter functionality is under construction.")
    st.button("🚧 Recruiter Flow (Coming Soon)", disabled=True)
