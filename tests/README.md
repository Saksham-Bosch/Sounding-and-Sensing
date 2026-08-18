# Tests Overview

This suite runs three real, opt-in live API checks against the sample assets in
`tests/assets/private/`. It does not prove production behavior; it is a Phase 0
smoke test against each external dependency.

## Structure

- `tests/live/test_ocr_live.py`: renders `sample_document.pdf` to an image and asks
  the Azure OpenAI chat/vision model (`AZURE_OPENAI_*`) to extract its text.
- `tests/live/test_stt_live.py`: transcribes `sample_audio.mp3` directly, and
  `sample_video.mp4` after extracting its audio track, via Azure OpenAI Whisper
  (`AZURE_OPENAI_WHISPER_*`).
- `tests/live/test_news_agent_live.py`: sends a random topic to the External News
  Agent (`EXTERNAL_NEWS_AGENT_*`) and asks it to prepare a questionnaire.
- `tests/helpers/`: shared utilities (env loading, redaction, HTTP requests, AAD
  token fetch, PDF-to-image rendering, video-to-audio extraction).
- `tests/assets/private/`: local-only sample inputs (ignored by git).

## Commands

Standard safe command (live tests skipped):

```powershell
c:/Users/CUH7KOR/Documents/Sounding-and-Sensing/.venv/Scripts/python.exe -m pytest tests -m "not live_api"
```

Opt-in live command (prints transcription/questionnaire previews):

```powershell
c:/Users/CUH7KOR/Documents/Sounding-and-Sensing/.venv/Scripts/python.exe -m pytest tests/live -m live_api -s
```

Live tests only run when `API_TEST_ALLOW_LIVE_CALLS=true` is set in `.env.local`
(or the shell environment). Otherwise they are skipped automatically.

## Configuration

Place local values only in root `.env.local` (never committed). Variable names:

- `API_TEST_ALLOW_LIVE_CALLS`, `API_TEST_TIMEOUT_SECONDS`, `API_TEST_MAX_RETRIES`

OCR (document text extraction):
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`,
  `AZURE_OPENAI_CHAT_MODEL`

STT (audio/video transcription):
- `AZURE_OPENAI_WHISPER_ENDPOINT` (must be a distinct key from
  `AZURE_OPENAI_ENDPOINT` above if it is a different Azure OpenAI resource)
- Preferred auth: `AZURE_OPENAI_WHISPER_CLIENT_ID`,
  `AZURE_OPENAI_WHISPER_TENANT_ID`, `AZURE_OPENAI_WHISPER_SECRET`
  (Azure AD client-credentials flow)
- Fallback auth: `AZURE_OPENAI_WHISPER_API` (used as an `api-key` header if AAD
  credentials are absent or the token request fails)
- Optional: `AZURE_OPENAI_WHISPER_DEPLOYMENT` (default: `whisper`),
  `AZURE_OPENAI_WHISPER_API_VERSION` (default: `2024-06-01`)

External News Agent (topic -> questionnaire):
- `EXTERNAL_NEWS_AGENT_ENDPOINT`, `EXTERNAL_NEWS_AGENT_API_KEY`
- Optional: `EXTERNAL_NEWS_AGENT_PATH` (default: `/ask`),
  `EXTERNAL_NEWS_AGENT_AUTH_HEADER` (default: `x-api-key`)

## Required local dependencies

Video-to-audio conversion and PDF rendering need two extra packages:

```powershell
c:/Users/CUH7KOR/Documents/Sounding-and-Sensing/.venv/Scripts/python.exe -m pip install pymupdf imageio-ffmpeg
```

If either package is missing, the relevant test skips with a clear message
instead of failing.

## Test Assets

- `tests/assets/private/sample_audio.mp3`
- `tests/assets/private/sample_video.mp4`
- `tests/assets/private/sample_document.pdf`

These files are ignored by git (matched by extension in `.gitignore`). Do not
use production, confidential, or personal content.

## Output Locations

Live tests write their results locally for inspection (all ignored by git):

- `.test-output/ocr_sample_document_transcription.txt`
- `.test-output/stt_sample_audio_transcription.txt`
- `.test-output/stt_sample_video_transcription.txt`
- `.test-output/sample_video_extracted_audio.wav`
- `.test-output/news_agent_questionnaire_<topic-slug>.txt`

## Security Restrictions

- Never print tokens, authorization headers, or full confidential responses.
- Never use production or confidential user data as test input.
- `.env.local` must never be committed.

## Output Locations

- Local run output: `.test-output/`
- Optional response traces: `live-api-responses/`
- Optional generated artifacts: `generated-presentations/`, `generated-transcripts/`

All output paths above remain ignored.

## Markers and Result Interpretation

- `live_api` tests are skipped unless live mode is explicitly enabled.
- `SKIPPED` means a required precondition was not met.
- `FAILED` means a contract or safety assertion did not hold.

## Security Restrictions

- Never print tokens, authorization headers, signed URLs, or full confidential responses.
- Never use production or confidential user data in tests.
- Never assume endpoint paths, header names, or payload shape without documented contracts.

## Cleanup

- Delete local generated files from `.test-output/` when no longer needed.
- Remove any temporary synthetic files created for one-off diagnostics.

## References

- [Repository Rules](../AGENTS.md)
- [ADR-003 API Contract Testing Strategy](../docs/architecture/decisions/ADR-003-approved-model-providers.md)
- [ADR-004 Test Asset Governance](../docs/architecture/decisions/ADR-004-questionnaire-generation.md)
