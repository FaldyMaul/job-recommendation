from backend.llm_api import call_apilogy_llm
import asyncio

async def estimate_user_level(competency_name: str, profile_summary: str) -> int:
    prompt = f"""
Given this summary of a user's professional experience:

{profile_summary}

Estimate the user's level (1 to 5) for the following competency:
**{competency_name}**

Reply with ONLY a single digit from 1 to 5. No explanation.
"""
    result = await call_apilogy_llm(prompt)
    try:
        return min(max(int(result.strip()), 1), 5)
    except:
        return 3
