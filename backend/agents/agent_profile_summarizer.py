from backend.llm_api import call_apilogy_llm
import asyncio

async def summarize_user_profile(input_text: str) -> str:
    prompt = f"""
You are a professional career analyst.

Given the following user profile, generate a detailed **competency-based summary only**.

🚫 Do NOT include: name, email, phone number, address, or any personal information.
✅ DO include: technical skills, soft skills, tools, leadership, certifications, achievements, and experience area.

User profile:
{input_text}
"""
    return await call_apilogy_llm(prompt)
