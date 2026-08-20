import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / ".env.local"
load_dotenv(ENV_PATH)

MRA_ENDPOINT = os.getenv("EXTERNAL_NEWS_AGENT_ENDPOINT")
MRA_API_KEY = os.getenv("EXTERNAL_NEWS_AGENT_API_KEY")
MRA_PATH = os.getenv("EXTERNAL_NEWS_AGENT_PATH") or "/query"
MRA_AUTH_HEADER = os.getenv("EXTERNAL_NEWS_AGENT_AUTH_HEADER") or "x-api-key"

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_CHAT_MODEL = os.getenv("AZURE_OPENAI_CHAT_MODEL")

ALLOWED_INPUT_TYPES = ["text", "audio", "image", "pdf", "docx", "pptx", "xlsx", "video", "url"]


def _clean_json_text(raw: str) -> str:
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1]
    elif "```" in text:
        text = text.split("```", 1)[1]
    if "```" in text:
        text = text.split("```", 1)[0].strip()
    return text.strip()


def _extract_questionnaire_from_text(raw: str) -> dict | None:
    cleaned = _clean_json_text(raw)
    if not cleaned:
        return None
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict) and isinstance(data.get("questions"), list):
        return data
    return None


def _extract_questionnaire(data: Any) -> dict | None:
    if isinstance(data, dict):
        if isinstance(data.get("questions"), list):
            return data
        for key in ("answer", "response", "output", "result", "questionnaire", "content", "text"):
            value = data.get(key)
            candidate = _extract_questionnaire(value)
            if isinstance(candidate, dict):
                return candidate
        for value in data.values():
            candidate = _extract_questionnaire(value)
            if isinstance(candidate, dict):
                return candidate
        return None
    if isinstance(data, list):
        for value in data:
            candidate = _extract_questionnaire(value)
            if isinstance(candidate, dict):
                return candidate
        return None
    if isinstance(data, str):
        return _extract_questionnaire_from_text(data)
    return None


def _event_fields(event_data: dict) -> tuple[str, str, str, str, str, str, str]:
    title = str(event_data.get("title") or "")
    description = str(event_data.get("description") or "")
    speakers = ", ".join(event_data.get("speakers", [])) if event_data.get("speakers") else ""
    start_date = str(event_data.get("start_date") or "")
    end_date = str(event_data.get("end_date") or "")
    dates = " - ".join(part for part in [start_date, end_date] if part).strip() or "Not specified"
    search_query = f"{title} {speakers} {start_date} {description}"[:200].strip()
    return title, description, speakers, start_date, end_date, dates, search_query


def _baseline_questions() -> list[dict[str, Any]]:
    base_texts = [
        "Could you please state your primary role, department, and your main reason for attending this event?",
        "What was the most valuable insight, concept, or connection you gained from this session?",
        "How well did the event content and speakers meet your initial expectations?",
    ]
    return [
        {
            "id": f"q-{index:03d}",
            "position": index,
            "text": text,
            "type": "OPEN_TEXT",
            "required": True,
            "allowed_input_types": ALLOWED_INPUT_TYPES,
            "guidance": None,
            "branch_rules": [],
        }
        for index, text in enumerate(base_texts, start=1)
    ]


def _context_only_questionnaire(event_data: dict) -> dict:
    title, description, speakers, start_date, _, dates, _ = _event_fields(event_data)
    topic = f"Event: {title}\nDates: {start_date}\nSpeakers: {speakers}\nDescription: {description}"
    dynamic = [
        f"Which strategic outcomes matter most for stakeholders attending {title or 'this event'}?",
        f"What major risks, blockers, or execution challenges should be prioritized after {title or 'this event'}?",
        f"Which decisions, partnerships, or follow-up actions should happen in the next 30 days based on {title or 'this event'}?",
    ]

    questions = _baseline_questions()
    for idx, text in enumerate(dynamic, start=4):
        questions.append(
            {
                "id": f"q-{idx:03d}",
                "position": idx,
                "text": text,
                "type": "OPEN_TEXT",
                "required": True,
                "allowed_input_types": ALLOWED_INPUT_TYPES,
                "guidance": "Use event-specific details where possible.",
                "branch_rules": [],
            }
        )

    return {
        "schema_version": "1.0",
        "questionnaire_id": "string",
        "title": "Customized Event Interview",
        "metadata": {
            "event_title": title or "Not specified",
            "event_description": description or "Not specified",
            "event_dates": dates,
            "event_speakers": [s.strip() for s in speakers.split(",") if s.strip()] or ["Not specified"],
        },
        "questions": questions,
        "research_context": f"Generated from event metadata fallback context because structured retrieval was unavailable: {topic}",
    }


def _fallback_questionnaire(event_data: dict) -> dict:
    title, description, speakers, start_date, _, dates, _ = _event_fields(event_data)
    topic = f"Event: {title}\nDates: {start_date}\nSpeakers: {speakers}\nDescription: {description}"
    return {
        "schema_version": "1.0",
        "questionnaire_id": "string",
        "title": "Standard Fallback Interview",
        "metadata": {
            "event_title": title or "Not specified",
            "event_description": description or "Not specified",
            "event_dates": dates,
            "event_speakers": [s.strip() for s in speakers.split(",") if s.strip()] or ["Not specified"],
        },
        "questions": [
            {
                "id": "q-fallback-1",
                "position": 1,
                "text": f"What are the main objectives for the topic: {topic}?",
                "type": "OPEN_TEXT",
                "required": True,
                "allowed_input_types": ["text", "audio"],
                "guidance": "Please provide a brief overview.",
                "branch_rules": [],
            }
        ],
    }


def _extract_news_results(data: Any) -> list[dict[str, str]]:
    if not isinstance(data, dict):
        return []
    news = data.get("news")
    if not isinstance(news, dict):
        return []
    top_results = news.get("top_results")
    if not isinstance(top_results, list):
        return []

    extracted: list[dict[str, str]] = []
    for item in top_results:
        if not isinstance(item, dict):
            continue
        extracted.append(
            {
                "url": str(item.get("url") or "").strip(),
                "description": str(item.get("description") or "").strip(),
                "title": str(item.get("title") or "").strip(),
            }
        )
    return extracted


def _build_azure_url() -> str:
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_VERSION or not AZURE_OPENAI_CHAT_MODEL:
        raise ValueError("Azure OpenAI configuration missing in .env.local")
    base = AZURE_OPENAI_ENDPOINT.rstrip("/")
    return f"{base}/openai/deployments/{AZURE_OPENAI_CHAT_MODEL}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"


async def _scrape_page_text(client: httpx.AsyncClient, url: str) -> str:
    try:
        response = await client.get(url, timeout=20.0, follow_redirects=True)
    except Exception as exc:  # pragma: no cover - network path
        print(f"Scrape network failure for {url}: {exc}")
        return ""

    if response.status_code != 200:
        print(f"Scrape HTTP {response.status_code} for {url}")
        return ""

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.stripped_strings)
    except Exception as exc:  # pragma: no cover - parser path
        print(f"Scrape parsing failure for {url}: {exc}")
        return ""

    text = re.sub(r"\s+", " ", text).strip()
    return text[:5000]


async def _collect_context(client: httpx.AsyncClient, topic: str, news_results: list[dict[str, str]]) -> str:
    context_chunks = [f"Topic: {topic}"]

    urls = []
    for item in news_results:
        url = item.get("url", "")
        if url and url not in urls:
            urls.append(url)
        if len(urls) >= 3:
            break

    scraped_chunks = []
    for url in urls:
        page_text = await _scrape_page_text(client, url)
        if page_text:
            scraped_chunks.append(f"Source URL: {url}\nContent: {page_text}")

    if scraped_chunks:
        context_chunks.extend(scraped_chunks)
    else:
        snippet_lines = []
        for item in news_results[:5]:
            title = item.get("title", "")
            description = item.get("description", "")
            if title or description:
                snippet_lines.append(f"Title: {title}\nSnippet: {description}".strip())
        if snippet_lines:
            context_chunks.append("Snippet fallback context:\n" + "\n\n".join(snippet_lines))

    return "\n\n".join(chunk for chunk in context_chunks if chunk.strip())[:12000]


async def _generate_with_azure(client: httpx.AsyncClient, topic: str, scraped_text: str) -> dict | None:
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY missing in .env.local")

    url = _build_azure_url()
    system_instructions = """You are an expert event interviewer. 
Your task is to generate a strict JSON questionnaire for an event.

INSTRUCTIONS:
1. You MUST output ONLY valid JSON matching the exact schema provided.
2. Extract the event metadata from the [EVENT TOPIC] and place it in the `metadata` object. If a field is missing, use "Not specified".
3. The questionnaire MUST start with these exact 3 standard, domain-agnostic baseline questions to capture participant context:
   - Q1: "Could you please state your primary role, department, and your main reason for attending this event?"
   - Q2: "What was the most valuable insight, concept, or connection you gained from this session?"
   - Q3: "How well did the event content and speakers meet your initial expectations?"
4. After the 3 standard questions, generate 3 to 5 highly specific, dynamic questions tailored to the event.
5. Base the dynamic questions on the provided [NEWS CONTEXT]. 
6. IF the [NEWS CONTEXT] is empty, irrelevant, or yields no results, fall back to generating dynamic questions based purely on the [EVENT TOPIC].

REQUIRED JSON SCHEMA:
{
  "schema_version": "1.0",
  "questionnaire_id": "string",
  "title": "Customized Event Interview",
  "metadata": {
    "event_title": "string",
    "event_description": "string",
    "event_dates": "string",
    "event_speakers": ["string"]
  },
  "questions": [
    {
      "id": "q-001",
      "position": 1,
      "text": "The question text",
      "type": "OPEN_TEXT",
      "required": true,
      "allowed_input_types": ["text", "audio", "image", "pdf", "docx", "pptx", "xlsx", "video", "url"],
      "guidance": null,
      "branch_rules": []
    }
  ]
}"""

    user_content = f"[EVENT TOPIC]:\n{topic}\n\n[NEWS CONTEXT]:\n{scraped_text}"

    payload = {
        "messages": [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_content}
        ],
        "max_completion_tokens": 2000,
        "response_format": {"type": "json_object"}
    }
    headers = {"api-key": AZURE_OPENAI_API_KEY, "Content-Type": "application/json"}

    response = await client.post(url, json=payload, headers=headers, timeout=90.0)
    if response.status_code != 200:
        print(f"Azure OpenAI Error {response.status_code}: {response.text[:300]}")
        return None

    try:
        data = response.json()
    except ValueError:
        print("Azure OpenAI response was not JSON.")
        return None

    choices = data.get("choices", []) if isinstance(data, dict) else []
    if not choices or not isinstance(choices, list):
        return None

    message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
    content = message.get("content", "")
    questionnaire = _extract_questionnaire(content)
    if questionnaire is not None:
        return questionnaire

    if isinstance(content, list):
        joined = "\n".join(str(item.get("text", "")) for item in content if isinstance(item, dict))
        questionnaire = _extract_questionnaire(joined)
        if questionnaire is not None:
            return questionnaire

    return None


async def _retrieve_news_results(client: httpx.AsyncClient, search_query: str) -> tuple[list[dict[str, str]], bool]:
    if not MRA_ENDPOINT or not MRA_API_KEY:
        raise ValueError("MRA credentials not found in .env.local")

    headers = {MRA_AUTH_HEADER: MRA_API_KEY, "Content-Type": "application/json"}
    configured_path = MRA_PATH if MRA_PATH.startswith("/") else f"/{MRA_PATH}"
    candidate_paths: list[str] = []
    for candidate in [configured_path, "/query", "/ask"]:
        if candidate not in candidate_paths:
            candidate_paths.append(candidate)

    had_network_failure = False
    for path in candidate_paths:
        url = f"{MRA_ENDPOINT.rstrip('/')}{path}"
        try:
            response = await client.post(url, json={"query": search_query, "user_id": "phase1-local-backend"}, headers=headers)
        except Exception as exc:  # pragma: no cover - network path
            print(f"MRA network failure for {url}: {exc}")
            had_network_failure = True
            continue

        if response.status_code != 200:
            print(f"MRA API Error {response.status_code} for {url}: {response.text[:300]}")
            continue

        try:
            data = response.json()
        except ValueError:
            print(f"MRA response was not valid JSON for {url}: {response.text[:300]}")
            continue

        return _extract_news_results(data), had_network_failure

    return [], had_network_failure


async def generate_custom_questions(event_data: dict) -> dict:
    title, description, speakers, start_date, _end_date, _dates, search_query = _event_fields(event_data)
    topic = f"Event: {title}\nDates: {start_date}\nSpeakers: {speakers}\nDescription: {description}"

    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
        mra_network_failed = False
        azure_network_failed = False

        try:
            news_results, mra_network_failed = await _retrieve_news_results(client, search_query)
        except Exception as exc:
            print(f"MRA retrieval failed: {exc}")
            news_results = []
            mra_network_failed = True

        context_text = await _collect_context(client, topic, news_results)
        if not context_text.strip():
            context_text = f"Topic: {topic}"

        try:
            generated = await _generate_with_azure(client, topic, context_text)
            if generated is not None:
                return generated
        except Exception as exc:
            print(f"Azure OpenAI generation failed: {exc}")
            azure_network_failed = True

        if mra_network_failed and azure_network_failed:
            print("Both MRA retrieval and Azure generation failed due to network errors. Using hard fallback.")
            return _fallback_questionnaire(event_data)

        # Non-catastrophic fallback: keep questionnaire contextual even if one dependency fails.
        return _context_only_questionnaire(event_data)


async def generate_questionnaire_from_mra(topic: str) -> dict:
    # Compatibility wrapper retained for existing tests/callers.
    event_data = {
        "title": topic,
        "description": "",
        "speakers": [],
        "start_date": "",
        "end_date": "",
    }
    return await generate_custom_questions(event_data)

