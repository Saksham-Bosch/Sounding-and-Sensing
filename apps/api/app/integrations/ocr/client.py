import base64
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / ".env.local"
load_dotenv(ENV_PATH)

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_MODEL = os.getenv("AZURE_OPENAI_CHAT_MODEL")
AZURE_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


async def extract_text_with_ocr(image_path: Path) -> str:
    """Uses Azure OpenAI Vision to extract text from an image."""
    if not all([AZURE_ENDPOINT, AZURE_API_KEY, AZURE_MODEL]):
        return "[OCR Skipped: Azure OpenAI credentials missing]"

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    mime_type = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"

    url = f"{AZURE_ENDPOINT}/openai/deployments/{AZURE_MODEL}/chat/completions?api-version={AZURE_VERSION}"
    headers = {"api-key": AZURE_API_KEY, "Content-Type": "application/json"}

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all readable text from this image accurately. Return ONLY the extracted text. Do not add conversational filler.",
                    },
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                ],
            }
        ],
        "max_completion_tokens": 2000,
    }

    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[OCR Failed: {str(e)}]"
