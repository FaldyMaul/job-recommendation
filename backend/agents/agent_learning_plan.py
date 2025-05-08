# backend/agents/agent_learning_plan.py

import json
from backend.llm_api import call_apilogy_llm
import asyncio

async def generate_learning_plan(job_json: dict, summary_result: str, gaps: list, requirements: list) -> dict:
    job_info = json.dumps(job_json, indent=2)
    gaps_text = json.dumps(gaps, indent=2)
    requirements_text = json.dumps(requirements, indent=2)

    prompt = f"""
You are a learning coach AI. Based on the following job, user's profile, identified competency gaps, and job requirements:

Generate a 4-week personalized learning plan to improve the user's readiness.
For each week include:
- Week Number (1 to 4)
- Focus area (based on gaps or job requirement category)
- Objectives
- Activities (e.g. YouTube videos, free courses, articles, coding challenges, events, internships, community involvement)
- Resource links (max 3 per week, must be clickable/valid)
- Rationale: why these activities help close the user's gap

Respond in this JSON format:
{{
  "plan": [
    {{
      "week": 1,
      "focus_area": "<e.g. Backend Development>",
      "objectives": "<learning goal>",
      "activities": ["<course/article/video/challenge>"],
      "resources": ["<url1>", "<url2>", "<url3>"],
      "rationale": "<why this week matters>"
    }}
  ]
}}

Job:
{job_info}

User Summary:
{summary_result}

Competency Gaps:
{gaps_text}

Job Requirements:
{requirements_text}

Only return valid JSON. Do not include explanations.
"""

    for attempt in range(3):
        try:
            response = await call_apilogy_llm(prompt)
            parsed = json.loads(response)

            if "plan" in parsed and isinstance(parsed["plan"], list):
                return parsed
        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1}: Invalid JSON from LLM")
        except Exception as e:
            print(f"Attempt {attempt + 1}: Learning plan generation error - {e}")

    return {"plan": []}
