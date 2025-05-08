from backend.llm_api import call_apilogy_llm
import asyncio

async def extract_job_title(summary_text: str) -> str:
    prompt = f"""
From the following user profile summary, identify the user's current job title or role.

Summary:
{summary_text}

Respond ONLY with the job title (e.g., Data Scientist, Software Engineer, HR Manager).
Do NOT include explanations, location, company, or extra text.
"""
    result = await call_apilogy_llm(prompt)
    return result.strip().title()
