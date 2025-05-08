import json
import httpx
from backend.llm_api import call_apilogy_llm

async def enrich_and_score_jobs(jobs, user_summary):
    try:
        if not jobs:
            return []

        trimmed_jobs = jobs[:5]  # Limit to 5 jobs to reduce LLM load

        # Format prompt
        prompt = f"""
You are a job matching assistant.

Given a user's profile and a list of job posts, return for each job:
- role
- company
- company_type (e.g., Private, Government, Startup)
- location
- industry
- pay_usd (estimated salary range per month, if available in the job post calculate to usd per month. If not available, try to analyze the estimated range of the salary based on the requirements, description, company, and location and add "(est)")
- fit_reason (why this job matches the user’s profile)
- match_score (between 0 and 100)
- description (brief 1–2 sentence summary of the job)
- link (direct application or view link)

User Profile:
{user_summary}

Jobs (raw data):
{json.dumps(trimmed_jobs, indent=2)}

Respond in this JSON format:
[
  {{
    "role": "Job Title",
    "company": "Company Name",
    "company_type": "Private / Government / BUMN / etc.",
    "location": "City, Country",
    "industry": "Field",
    "pay_usd": "1000 to 1500 USD/month",
    "fit_reason": "Why this job fits the user",
    "match_score": 0-100,
    "description": "Brief 1–2 sentence job summary",
    "link": "Apply/View link"
  }}
]

ONLY return a valid JSON list. Do not include explanation or notes.
"""

        response = await call_apilogy_llm(prompt)
        parsed = json.loads(response)

        # Add fallback fields from original raw data if missing
        for enriched, raw in zip(parsed, trimmed_jobs):
            if not enriched.get("description"):
                enriched["description"] = raw.get("description", "")[:300]
            if not enriched.get("link"):
                enriched["link"] = raw.get("apply_link") or raw.get("sharing_link", "")

        return parsed

    except httpx.HTTPStatusError as e:
        print(f"LLM API error: {e}")
        return []
    except json.JSONDecodeError:
        print("LLM response was not valid JSON.")
        return []
    except Exception as e:
        print(f"Unexpected error in job enrichment: {e}")
        return []
