# backend/agents/agent_gap_analyzer.py

from backend.llm_api import call_apilogy_llm
import json

async def analyze_gaps(job_json: dict, summary_result: str, competencies: list) -> dict:
    job_info = json.dumps(job_json, indent=2)
    competency_text = json.dumps(competencies, indent=2)

    prompt = f"""
You are a career coach AI.
Your task is to compare a job's requirements against a user's current competencies and summarized CV.

Return up to 5 competency or experience gaps that may reduce the user's job fit.
For each, include:
- Type: 'skill' or 'experience'
- Name of competency or experience required
- Current level (if skill)
- Target level (if skill)
- Explanation for gap or mismatch
- Recommendation to close the gap

Respond in this JSON format:
{{
  "job_title": "<title>",
  "gaps": [
    {{
      "type": "skill",
      "competency": "<competency name>",
      "current_level": <user level>,
      "required_level": <expected level>,
      "recommendation": "<how to close the gap>"
    }},
    {{
      "type": "experience",
      "requirement": "<required experience>",
      "found_in_cv": <true/false>,
      "recommendation": "<how to gain or match it>"
    }}
  ]
}}

Job Description:
{job_info}

User Summary:
{summary_result}

User Competency Input:
{competency_text}

Only return valid JSON.
"""

    try:
        response = await call_apilogy_llm(prompt)
        return json.loads(response)
    except Exception as e:
        print("Gap analysis failed:", e)
        return {"job_title": job_json.get("title", ""), "gaps": []}
