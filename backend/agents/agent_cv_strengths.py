from backend.llm_api import call_apilogy_llm
import asyncio
import json
import re

async def extract_top_strengths(cv_text: str, competency_list: list) -> list:
    list_str = "\n".join([f"- {c}" for c in competency_list])

    prompt = f"""
You are a professional HR analyst.

Analyze the user's CV and extract the top 5 strongest competencies from the list below, based on their skills, experiences, and years of practice.

Output ONLY a valid JSON array using this format:
[
  {{ "competency": "Competency Name", "level": 4 }},
  ...
]

Do not include explanations, markdown, or any text before/after the JSON.

CV Text:
{cv_text}

Available Competencies:
{list_str}
"""

    response = await call_apilogy_llm(prompt)

    try:
        # Extract only the JSON part if extra text is present
        match = re.search(r"\[\s*{.*?}\s*]", response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(response)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse LLM response:", response)
        return []
