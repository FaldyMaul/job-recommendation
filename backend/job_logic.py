# backend/job_logic.py

import requests
import asyncio
from backend.agents.agent_enrich_job import enrich_and_score_jobs

def search_jobs(job_title, api_key, api_url, max_retries=3):
    for attempt in range(max_retries):
        try:
            params = {
                "engine": "google_jobs",
                "q": job_title,
                "api_key": api_key
            }
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            return response.json().get("jobs", [])
        except Exception as e:
            print(f"Search attempt {attempt + 1} failed: {e}")
    return []

def run_enrichment(jobs, user_summary):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(enrich_and_score_jobs(jobs, user_summary))
