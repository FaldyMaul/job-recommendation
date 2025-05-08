import streamlit as st
import asyncio
from backend.agents.agent_job_recommender import recommend_jobs_from_competencies

st.set_page_config(page_title="💼 Job Recommendations", page_icon="💼")
st.title("💼 Job Recommendations")

competencies = st.session_state.get("final_competency_input", [])
if not competencies:
    st.warning("No competency profile found. Please complete the competency summary first.")
    st.stop()

# Only call LLM recommender once and cache it in session state
if "job_recommendations" not in st.session_state:
    with st.spinner("Generating job recommendations..."):
        results = asyncio.run(recommend_jobs_from_competencies(competencies))
        st.session_state["job_recommendations"] = results

recommendations = st.session_state["job_recommendations"]

# Display recommendations
st.subheader("🎯 Based on your competency profile, here are your matches:")
for idx, job in enumerate(recommendations):
    st.markdown(f"""
    🔹 **{job['title']}**  
    📁 {job['level']}  
    🧠 {job['fit_reason']}  
    """)
    if st.button("🚀 I want to pursue this", key=f"pursue_{idx}"):
        st.session_state["selected_job"] = job
        st.session_state["show_preferences"] = True

# Show follow-up form after job selection
if st.session_state.get("show_preferences"):
    job_title = st.session_state['selected_job']['title']
    st.success(f"You’ve selected **{job_title}**. Let’s refine your preferences.")

    with st.form("preferences_form"):
        industries = st.multiselect(
            "Which industries are you most interested in?",
            ["IT", "Finance", "Healthcare", "Education", "Oil & Gas", "Mining", "F&B", "Telecommunication", "Retail", "Manufacturing"],
            key="industry_input"
        )

        company_type = st.selectbox(
            "What type of company do you prefer?",
            ["Private Sector", "BUMN", "Government", "Startup", "NGO"],
            key="company_type_input"
        )

        location = st.text_input("Preferred job location (e.g., Jakarta, Indonesia)", key="location_input")

        submitted = st.form_submit_button("✅ Save Preferences")
        if submitted:
            st.session_state["user_preferences"] = {
                "industries": industries,
                "company_type": company_type,
                "location": location
            }
            st.success("Preferences saved!")


# Next step
if st.session_state.get("user_preferences"):
    st.markdown("---")
    if st.button("🔎 Search Matching Jobs"):
        st.switch_page("pages/job_search.py")
