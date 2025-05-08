from backend.llm_api import call_apilogy_llm
import json

async def recommend_jobs_from_competencies(competencies: list) -> list:
    """
    competencies: list of { "competency": "Data Analytics", "level": 4 }
    """
    prompt = f"""
You are a career advisor AI.

Based on the following list of user competencies and levels, recommend 3 suitable job titles with level and short fit reasons.

Competencies:
{json.dumps(competencies, indent=2)}

Return in this JSON format:
[
{{
"title": "Data Analyst",
"level": "Senior",
"fit_reason": "Strong match on Data Analytics, SQL, and visualization skills."
}},
...
]
Respond with only JSON, no explanation.
"""
    response = await call_apilogy_llm(prompt)
    return json.loads(response)