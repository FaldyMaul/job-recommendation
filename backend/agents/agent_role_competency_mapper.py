# backend/agents/agent_role_competency_mapper.py

from backend.llm_api import call_apilogy_llm
import asyncio

async def map_competencies_for_role(role_name: str, competency_list: list) -> list:
    flat_list = "\n".join([f"- {comp}" for comp in competency_list])

    prompt = f"""
You are a career development expert.

From the list of competencies below, select the 5 to 10 most relevant competencies for the job role: **{role_name}**.

List only the competency names, comma-separated, with no explanation.

Available competencies:
{flat_list}
"""

    response = await call_apilogy_llm(prompt)
    return [c.strip() for c in response.split(",") if c.strip()]
