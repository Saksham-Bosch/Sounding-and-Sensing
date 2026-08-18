from __future__ import annotations

import json
import random
import re
from pathlib import Path

import pytest

from tests.helpers.api_client import join_base_and_path, safe_request
from tests.helpers.configuration import get_test_settings

OUTPUT_DIR = Path(".test-output")

_SAMPLE_TOPICS = [
    "renewable energy adoption in urban housing",
    "artificial intelligence in preventive healthcare",
    "public transportation electrification",
    "remote work productivity trends",
    "cybersecurity practices for small businesses",
]


@pytest.mark.live_api
def test_news_agent_generates_questionnaire_for_random_topic() -> None:
    settings = get_test_settings()
    missing = settings.missing_for_live("news_agent")
    if missing:
        pytest.skip("Missing required live-test configuration names: " + ", ".join(missing))

    topic = random.choice(_SAMPLE_TOPICS)

    url = join_base_and_path(settings.news_agent_endpoint or "", settings.news_agent_path)
    payload = {
        "query": (
            f"Research the topic '{topic}' and prepare a structured questionnaire. "
            "You MUST return ONLY valid JSON matching this exact schema: \n"
            "{\n"
            '  "schema_version": "1.0",\n'
            '  "questionnaire_id": "string",\n'
            '  "title": "Customized Event Interview",\n'
            '  "questions": [\n'
            "    {\n"
            '      "id": "q-001",\n'
            '      "position": 1,\n'
            '      "text": "Question text",\n'
            '      "type": "OPEN_TEXT",\n'
            '      "required": true,\n'
            '      "allowed_input_types": ["text", "audio", "image", "pdf", "docx", "pptx", "xlsx", "video", "url"],\n'
            '      "guidance": null,\n'
            '      "branch_rules": []\n'
            "    }\n"
            "  ]\n"
            "}"
        ),
        "user_id": "phase0-live-test",
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        settings.news_agent_auth_header: settings.news_agent_api_key or "",
        "Content-Type": "application/json",
    }

    result = safe_request(
        method="POST",
        url=url,
        headers=headers,
        body=body,
        timeout_seconds=settings.api_test_timeout_seconds,
        max_retries=settings.api_test_max_retries,
    )

    assert result.status_code == 200, (
        f"Unexpected News Agent status={result.status_code}, Content-Type={result.content_type}, "
        f"body_preview={result.preview()}"
    )

    data = result.json()
    answer: str
    if isinstance(data, dict) and isinstance(data.get("news"), dict):
        # Deployed /query pipeline shape: {"news": {"top_results": [{"title", "description", ...}, ...]}}
        top_results = data["news"].get("top_results") or []
        descriptions = [str(item.get("description", "")) for item in top_results if isinstance(item, dict)]
        answer = "\n\n".join(d for d in descriptions if d.strip())
    elif isinstance(data, dict):
        answer = str(
            data.get("answer")
            or data.get("response")
            or data.get("questionnaire")
            or data.get("result")
            or data.get("output")
            or ""
        )
    else:
        answer = str(data)

    assert answer.strip() != "", (
        f"News Agent response did not contain any usable research content: {result.preview()}"
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    topic_slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    output_file = OUTPUT_DIR / f"news_agent_questionnaire_{topic_slug}.txt"
    output_file.write_text(str(answer), encoding="utf-8")

    print(f"News Agent generated a questionnaire for topic '{topic}'. Saved to {output_file}")
