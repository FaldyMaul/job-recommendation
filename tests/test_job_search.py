# tests/test_job_search.py

import os
import json
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

# Set the Streamlit environment variable
os.environ["SEARCH_API_KEY"] = "fake-key"
os.environ["SEARCH_API_URL"] = "https://fake-search-api"

# Point to app entry file
APP_PATH = "app/pages/job_search.py"

@pytest.fixture
def load_enriched_jobs():
    with open("data/enriched_jobs.json", encoding="utf-8") as f:
        return json.load(f)

def test_render_jobs_with_enriched_data(load_enriched_jobs):
    # Set required session state variables
    st.session_state["selected_job"] = {"title": "data scientist"}
    st.session_state["summary_result"] = "Experienced in Python, AI, and statistics."

    # Patch the search_jobs and enrich_and_score_jobs functions to bypass real API
    from app.pages import job_search
    job_search.search_jobs = lambda query: []  # Skip API call
    job_search.enrich_and_score_jobs = lambda jobs, summary: load_enriched_jobs

    # Launch the app for testing
    at = AppTest.from_file(APP_PATH)
    at.run()

    # Check that job cards are rendered
    for job in load_enriched_jobs[:5]:  # Max 5 per page
        title = job.get("role") or job.get("title")
        company = job.get("company") or job.get("company_name")
        assert at.markdown.contains(f"### {title} at {company}")

    # Check progress bars appear (match score)
    assert any(widget.type == "progress" for widget in at._main._widgets)

    # Check navigation buttons
    assert at.button["➡️ Next"].exists()
    assert at.button["⬅️ Prev"].exists()

    # Check detail expander exists
    assert at.expander["📄 Show Details"].exists()