# backend/agents/agent_extract_job_requirements.py

from backend.llm_api import call_apilogy_llm
import json
import asyncio

async def extract_job_requirements(job_description: str, cv_summary: str) -> dict:
    prompt = f"""
You are an AI job analyst.
Extract the key job requirements from the following job description.
For each requirement, identify:
- Requirement text
- Category: one of ['technical skill', 'soft skill', 'tool', 'experience', 'education', 'certification']
- Reason: a short justification why it's considered important
- Match score: score from 0 to 100 showing how well the requirement is fulfilled based on the CV summary
- Match explanation: a short reasoning based on user's CV summary

Return the result in the following JSON format:
{{
  "requirements": [
    {{
      "requirement": "<exact phrasing from job post>",
      "category": "<one of the categories>",
      "reason": "<why this requirement matters>",
      "match_score": <score from 0 to 100>,
      "match_explanation": "<brief justification from CV match>"
    }}
  ]
}}

Job Description:
{job_description}

User CV Summary:
{cv_summary}

Only return valid JSON. No explanation.
"""

    try:
        response = await call_apilogy_llm(prompt)
        return json.loads(response)
    except Exception as e:
        print("Requirement extraction failed:", e)
        return {"requirements": []}
