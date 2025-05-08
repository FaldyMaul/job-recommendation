# backend/agents/agent_enrich_job.py

import json
import httpx
from backend.llm_api import call_apilogy_llm

async def enrich_and_score_jobs(jobs, user_summary):
    try:
        if not jobs:
            return []

        trimmed_jobs = jobs[:5]  # Limit to reduce load

        prompt = f"""
You are a job matching assistant.

Given a user's profile and a list of job posts, return for each job:
- role
- company
- company_type (e.g., Private, Government, Startup)
- location
- industry
- pay_usd (estimated salary range per month)
- fit_reason (why this job matches the user’s profile)
- match_score (0 to 100)
- description (brief 1–2 sentence summary)
- link (application or view link)

User Profile:
{user_summary}

Jobs (raw):
{json.dumps(trimmed_jobs, indent=2)}

Respond only in JSON format:
[
  {{
    "role": "Job Title",
    "company": "Company Name",
    "company_type": "Private / Government / etc.",
    "location": "City, Country",
    "industry": "Field",
    "pay_usd": "Approx USD/month",
    "fit_reason": "Why this fits the user",
    "match_score": 0-100,
    "description": "1–2 sentence job summary",
    "link": "Direct job link"
  }}
]
"""

        for attempt in range(3):
            try:
                response = await call_apilogy_llm(prompt)
                parsed = json.loads(response)

                enriched_results = []
                for enriched, raw in zip(parsed, trimmed_jobs):
                    # Ensure fallbacks for critical fields
                    enriched.setdefault("description", raw.get("description", "")[:300])
                    enriched.setdefault("link", raw.get("apply_link") or raw.get("sharing_link", ""))
                    enriched.setdefault("role", raw.get("title", "Unknown Role"))
                    enriched.setdefault("company", raw.get("company_name", "Unknown Company"))
                    enriched.setdefault("match_score", 0)
                    enriched.setdefault("fit_reason", "Not provided.")

                    # Fallback to raw job if enrichment is clearly missing
                    if not enriched.get("fit_reason") or enriched.get("match_score", 0) == 0:
                        enriched["fit_reason"] = f"Auto-filled from raw data. Role: {raw.get('title', '')}"
                        enriched["match_score"] = 20  # Default minimal match score to ensure ranking

                    enriched_results.append(enriched)

                return enriched_results

            except json.JSONDecodeError:
                print(f"Attempt {attempt + 1}: Invalid JSON from LLM")
            except httpx.HTTPStatusError as e:
                print(f"Attempt {attempt + 1}: HTTP error - {e}")
            except Exception as e:
                print(f"Attempt {attempt + 1}: Unexpected error - {e}")

        return []  # All attempts failed

    except Exception as e:
        print(f"Outer error in enrich_and_score_jobs: {e}")
        return []
