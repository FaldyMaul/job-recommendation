# backend/agents/agent_gap_analyzer.py

import json
from backend.llm_api import call_apilogy_llm
import asyncio

async def analyze_gaps(job_json: dict, summary_result: str, competencies: list) -> dict:
    job_info = json.dumps(job_json, indent=2)
    competency_text = json.dumps(competencies, indent=2)

    prompt = f"""
You are a career coach AI.

Compare a job's requirements with a user's current competencies and summarized CV.
Return up to 10 relevant skills or experience gaps—even those with 0 gap if important.
For each gap include:
- type: 'skill' or 'experience'
- competency: name of the competency or experience
- current_level (only if skill)
- required_level (only if skill)
- explanation: short reasoning why this gap matters
- recommendation: how the user can improve or fill the gap
- suggested_learning_mode: "video", "project", "community", "internship", etc.

Respond in this JSON format:
{{
  "job_title": "<job title>",
  "gaps": [
    {{
      "type": "skill",
      "competency": "<name>",
      "current_level": <int>,
      "required_level": <int>,
      "explanation": "<why this matters>",
      "recommendation": "<actionable advice>",
      "suggested_learning_mode": "<mode>"
    }},
    {{
      "type": "experience",
      "competency": "<experience area>",
      "explanation": "<missing experience>",
      "recommendation": "<how to get experience>",
      "suggested_learning_mode": "<mode>"
    }}
  ]
}}

Job Info:
{job_info}

User Summary:
{summary_result}

User Competency Input:
{competency_text}

Only return valid JSON.
"""

    for attempt in range(3):
        try:
            response = await call_apilogy_llm(prompt)
            parsed = json.loads(response)
            if "gaps" in parsed:
                return parsed
        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1}: Invalid JSON from LLM")
        except Exception as e:
            print(f"Attempt {attempt + 1}: Gap analysis failed: {e}")

    return {"job_title": job_json.get("title", ""), "gaps": []}
