# backend/llm_api.py

import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("APILOGY_API_URL", "https://telkom-ai-dag-api.apilogy.id/Telkom-LLM/0.0.4/llm/chat/completions")
API_KEY = os.getenv("APILOGY_API_KEY", "your_default_api_key_here")  # Replace or set in .env

async def call_apilogy_llm(prompt: str, chat_history: list = None) -> str:
    if chat_history is None:
        chat_history = []

    messages = chat_history + [{"role": "user", "content": prompt}]

    payload = {
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7,
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]

