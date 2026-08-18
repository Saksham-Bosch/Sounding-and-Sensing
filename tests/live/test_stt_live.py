from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers.api_client import build_multipart_body, join_base_and_path, safe_request
from tests.helpers.azure_auth import AadTokenError, fetch_aad_token
from tests.helpers.configuration import Phase0TestSettings, get_test_settings
from tests.helpers.media import VideoConversionError, extract_audio_from_video

SAMPLE_AUDIO = Path("tests/assets/private/sample_audio.mp3")
SAMPLE_VIDEO = Path("tests/assets/private/sample_video.mp4")
OUTPUT_DIR = Path(".test-output")

_WHISPER_SCOPE = "https://cognitiveservices.azure.com/.default"


def _build_stt_auth_headers(settings: Phase0TestSettings) -> dict[str, str]:
    """Prefer Azure AD client-credentials auth; fall back to an API key."""
    if settings.whisper_client_id and settings.whisper_tenant_id and settings.whisper_secret:
        try:
            token = fetch_aad_token(
                tenant_id=settings.whisper_tenant_id,
                client_id=settings.whisper_client_id,
                client_secret=settings.whisper_secret,
                scope=_WHISPER_SCOPE,
                timeout_seconds=settings.api_test_timeout_seconds,
            )
            return {"Authorization": f"Bearer {token}"}
        except AadTokenError:
            pass  # fall through to API key auth below

    if settings.whisper_api_key:
        return {"api-key": settings.whisper_api_key}

    raise AadTokenError("No usable STT authentication method (AAD client-credentials or API key) succeeded")


def _transcribe(settings: Phase0TestSettings, audio_path: Path) -> str:
    headers = _build_stt_auth_headers(settings)

    url = (
        join_base_and_path(
            settings.whisper_endpoint or "",
            f"openai/deployments/{settings.whisper_deployment}/audio/transcriptions",
        )
        + f"?api-version={settings.whisper_api_version}"
    )
    body, content_type = build_multipart_body(file_path=audio_path, file_field="file")
    headers["Content-Type"] = content_type

    result = safe_request(
        method="POST",
        url=url,
        headers=headers,
        body=body,
        timeout_seconds=settings.api_test_timeout_seconds,
        max_retries=settings.api_test_max_retries,
    )

    assert result.status_code == 200, (
        f"Unexpected STT status={result.status_code}, Content-Type={result.content_type}, "
        f"body_preview={result.preview()}"
    )

    data = result.json()
    text = data.get("text", "")
    assert text.strip() != "", "STT response did not contain any transcribed text"
    return text


@pytest.mark.live_api
def test_stt_transcribes_sample_audio() -> None:
    settings = get_test_settings()
    missing = settings.missing_for_live("stt_audio")
    if missing:
        pytest.skip("Missing required live-test configuration names: " + ", ".join(missing))

    if not SAMPLE_AUDIO.exists():
        pytest.skip(f"Sample audio not found: {SAMPLE_AUDIO}")

    try:
        text = _transcribe(settings, SAMPLE_AUDIO)
    except AadTokenError as exc:
        pytest.skip(str(exc))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "stt_sample_audio_transcription.txt"
    output_file.write_text(text, encoding="utf-8")
    print(f"STT transcribed {len(text)} characters from sample audio. Saved to {output_file}")


@pytest.mark.live_api
def test_stt_transcribes_sample_video() -> None:
    settings = get_test_settings()
    missing = settings.missing_for_live("stt_video")
    if missing:
        pytest.skip("Missing required live-test configuration names: " + ", ".join(missing))

    if not SAMPLE_VIDEO.exists():
        pytest.skip(f"Sample video not found: {SAMPLE_VIDEO}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    extracted_audio_path = OUTPUT_DIR / "sample_video_extracted_audio.mp3"
    try:
        extract_audio_from_video(SAMPLE_VIDEO, extracted_audio_path)
    except VideoConversionError as exc:
        pytest.skip(str(exc))

    try:
        text = _transcribe(settings, extracted_audio_path)
    except AadTokenError as exc:
        pytest.skip(str(exc))

    output_file = OUTPUT_DIR / "stt_sample_video_transcription.txt"
    output_file.write_text(text, encoding="utf-8")
    print(f"STT transcribed {len(text)} characters from sample video audio. Saved to {output_file}")
