import streamlit as st
import json

st.set_page_config(page_title="📄 Enriched Jobs Viewer", page_icon="💼")
st.title("📄 View Enriched Job Results")

# Load JSON file
json_path = "enriched_jobs.json"

try:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        jobs = data.get("jobs", data)  # handle if JSON root is list or dict with 'jobs'
except Exception as e:
    st.error(f"Failed to load JSON: {e}")
    st.stop()

# Display jobs
st.subheader(f"Showing {len(jobs)} jobs")

for idx, job in enumerate(jobs, 1):
    with st.container():
        st.markdown(f"### {idx}. {job.get('role', 'Unknown Role')} at {job.get('company', 'Unknown Company')}")
        st.markdown(f"📍 Location: {job.get('location', 'N/A')}")
        st.markdown(f"🏢 Industry: {job.get('industry', 'Unknown')}")
        st.markdown(f"💰 Estimated Pay: {job.get('pay_usd', 'N/A')}")
        st.markdown(f"✅ Match Score: **{job.get('match_score', 0)}%**")
        st.markdown(f"💬 Reason: {job.get('fit_reason', 'No reason provided')}")
        st.markdown(f"📝 Description: {job.get('description', '')[:250]}...")
        if job.get("link"):
            st.markdown(f"[🔗 View Job Posting]({job['link']})")
        st.divider()
