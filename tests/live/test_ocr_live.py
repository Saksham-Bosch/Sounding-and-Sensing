from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from tests.helpers.api_client import join_base_and_path, safe_request
from tests.helpers.configuration import get_test_settings
from tests.helpers.pdf_to_image import PdfRenderError, get_pdf_page_count, render_pdf_page_png

SAMPLE_DOCUMENT = Path("tests/assets/private/sample_document.pdf")
OUTPUT_DIR = Path(".test-output")


@pytest.mark.live_api
def test_ocr_extracts_text_from_sample_document() -> None:
    settings = get_test_settings()
    missing = settings.missing_for_live("ocr")
    if missing:
        pytest.skip("Missing required live-test configuration names: " + ", ".join(missing))

    if not SAMPLE_DOCUMENT.exists():
        pytest.skip(f"Sample document not found: {SAMPLE_DOCUMENT}")

    try:
        page_count = get_pdf_page_count(SAMPLE_DOCUMENT)
    except PdfRenderError as exc:
        pytest.skip(str(exc))

    url = (
        join_base_and_path(
            settings.azure_openai_endpoint or "",
            f"openai/deployments/{settings.azure_openai_chat_model}/chat/completions",
        )
        + f"?api-version={settings.azure_openai_api_version}"
    )
    headers = {
        "api-key": settings.azure_openai_api_key or "",
        "Content-Type": "application/json",
    }

    page_texts: list[str] = []
    for page_index in range(page_count):
        try:
            image_bytes = render_pdf_page_png(SAMPLE_DOCUMENT, page_index=page_index)
        except PdfRenderError as exc:
            pytest.skip(str(exc))

        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a precise OCR engine. You MUST extract every single word and character from the provided image exactly as it appears, line-by-line, from top-to-bottom. Do not summarize. Do not skip any text.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract and transcribe absolutely all text from this document page."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                    ],
                },
            ],
            "max_completion_tokens": 2000,
        }
        body = json.dumps(payload).encode("utf-8")

        result = safe_request(
            method="POST",
            url=url,
            headers=headers,
            body=body,
            timeout_seconds=settings.api_test_timeout_seconds,
            max_retries=settings.api_test_max_retries,
        )

        assert result.status_code == 200, (
            f"Unexpected OCR status={result.status_code}, Content-Type={result.content_type}, "
            f"body_preview={result.preview()}"
        )

        data = result.json()
        extracted_text = data["choices"][0]["message"]["content"]
        assert extracted_text.strip() != "", f"OCR response for page {page_index + 1} did not contain any extracted text"
        page_texts.append(f"--- Page {page_index + 1} ---\n{extracted_text.strip()}")

    full_text = "\n\n".join(page_texts)
    assert full_text.strip() != "", "OCR did not extract any text across document pages"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "ocr_sample_document_transcription.txt"
    output_file.write_text(full_text, encoding="utf-8")

    print(f"OCR extracted {len(full_text)} characters across {page_count} page(s). Saved to {output_file}")
