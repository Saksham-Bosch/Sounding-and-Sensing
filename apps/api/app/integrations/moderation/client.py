import os
from urllib.parse import urlparse

import httpx

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_MODEL = os.getenv("AZURE_OPENAI_CHAT_MODEL")
AZURE_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


def is_safe_url(url: str) -> bool:
    """Basic SSRF protection."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        if hostname in ["localhost", "127.0.0.1", "0.0.0.0"] or hostname.startswith("192.168.") or hostname.startswith("10."):
            return False
        return True
    except Exception:
        return False


async def check_content_safety(text: str) -> bool:
    """Uses Azure OpenAI to moderate scraped content."""
    if not all([AZURE_ENDPOINT, AZURE_API_KEY, AZURE_MODEL]):
        return True  # Skip if no credentials

    system_prompt = (
        "You are a strict enterprise content moderator. Analyze the text scraped from a user-submitted URL. "
        "Determine if it contains NSFW content, hate speech, malicious payloads, or highly unprofessional material. "
        "Reply ONLY with the exact word 'SAFE' if it is clean, or 'UNSAFE' if it violates policies."
    )

    url = f"{AZURE_ENDPOINT}/openai/deployments/{AZURE_MODEL}/chat/completions?api-version={AZURE_VERSION}"
    headers = {"api-key": AZURE_API_KEY, "Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text[:3000]}
        ],
        "max_completion_tokens": 10
    }

    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            normalized = str(content).strip().upper()
            return normalized.startswith("SAFE")
        except Exception:
            return False
