# API README

This directory contains the FastAPI backend for the Sounding and Sensing platform.

## Phase 1 Complete

The API now supports the full local enterprise backend workflow:

### Core Capabilities

- Event creation with rich metadata, including speakers and start/end dates.
- Hybrid RAG questionnaire generation that combines event metadata, live news grounding, and strict JSON output.
- Multi-modal ingestion for documents, images, URLs, audio, and video.
- Azure OpenAI Vision-based OCR for image and scanned-PDF extraction.
- Azure OpenAI Whisper-based STT for audio and video transcription with OAuth authentication.
- SSRF protection and Azure content moderation for user-submitted URLs.
- Automatic cleanup of uploaded files after extraction/transcription.
- Executive summary generation with audience-specific AI reporting and DOCX export.

## Architecture Overview

- `app/main.py` wires the routers into the FastAPI application.
- `app/api/routers/events.py` manages event creation and listing.
- `app/api/routers/questionnaires.py` generates hybrid RAG questionnaires from event metadata.
- `app/api/routers/interviews.py` manages interview sessions, text answers, file uploads, moderation, and transcription.
- `app/api/routers/reports.py` generates audience-specific executive summaries and DOCX exports.
- `app/integrations/mra/client.py` handles news retrieval, scraping, strict questionnaire generation, and fallback logic.
- `app/integrations/ocr/client.py` performs Azure OCR for images.
- `app/integrations/stt/client.py` performs Azure Whisper transcription for media files.
- `app/integrations/moderation/client.py` applies SSRF checks and content moderation for URL answers.
- `app/integrations/parsers/document_parser.py` provides deterministic parsing for documents and URLs.
- `app/repositories/excel_adapter.py` reads and writes the mocked Excel database.

## Local Storage Model

The backend currently uses a mocked Excel repository named `mock_database.xlsx` for development and verification.

- Excel is a temporary adapter, not the production persistence layer.
- Generated questionnaire and interview data are stored through repository interfaces.
- Uploaded files are written to local disk only during processing and then deleted.

## Setup Requirements

### Prerequisites

- Python 3.12+.
- FFmpeg available on the system PATH for audio/video processing.
- Azure credentials and approved service access in `.env.local`.

### Python Dependencies

Install dependencies from `requirements.txt` in this directory.

## Required Environment Variables

### Azure OpenAI Chat / OCR

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_CHAT_MODEL`

### Azure OpenAI Whisper

- `AZURE_OPENAI_WHISPER_ENDPOINT`
- `AZURE_OPENAI_WHISPER_TENANT_ID`
- `AZURE_OPENAI_WHISPER_CLIENT_ID`
- `AZURE_OPENAI_WHISPER_SECRET`
- `AZURE_OPENAI_WHISPER_API`
- `AZURE_OPENAI_WHISPER_DEPLOYMENT`
- `AZURE_OPENAI_WHISPER_API_VERSION`

### External News / Research Agent

- `EXTERNAL_NEWS_AGENT_ENDPOINT`
- `EXTERNAL_NEWS_AGENT_API_KEY`
- `EXTERNAL_NEWS_AGENT_PATH`
- `EXTERNAL_NEWS_AGENT_AUTH_HEADER`

### Test Controls

- `API_TEST_ALLOW_LIVE_CALLS`
- `API_TEST_TIMEOUT_SECONDS`
- `API_TEST_MAX_RETRIES`

## Running the API

From `apps/api`:

```powershell
& "..\\..\\.venv\\Scripts\\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Notable Endpoints

- `GET /health`
- `POST /api/v1/events/`
- `POST /api/v1/questionnaires/generate`
- `POST /api/v1/interviews/start`
- `POST /api/v1/interviews/{session_id}/answer`
- `POST /api/v1/interviews/{session_id}/answer/file`
- `GET /api/v1/reports/events/{event_id}/summary`
- `GET /api/v1/reports/events/{event_id}/export`

## Notes

- The API is optimized for the Phase 1 local proof of concept.
- Live Azure integrations require approved credentials and network access.
- The reference workspace under `architecture-analysis-workspace/` is read-only.
