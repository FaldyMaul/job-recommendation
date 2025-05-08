from backend.llm_api import call_apilogy_llm
import asyncio

async def extract_latest_job_role(cv_text: str) -> str:
    prompt = f"""
You are an expert in resume analysis.

From the following CV text, extract the title of the latest job held. Only return the job title, nothing else.

CV:
{cv_text}
"""
    response = await call_apilogy_llm(prompt)
    return response.strip()
