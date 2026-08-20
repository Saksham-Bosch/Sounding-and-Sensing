# Sounding and Sensing

Sounding and Sensing is the permanent repository for the Event Information Gathering and Dissemination platform.

Phase 1 is complete. The backend now implements the enterprise event capture, hybrid RAG questionnaire generation, multi-modal ingestion, STT transcription, URL moderation, executive reporting, and DOCX export flows required for the local proof of concept.

## Phase 1 Complete

### Core Features

- Event creation captures rich metadata including speakers and event dates.
- Questionnaire generation uses centralized event metadata plus live news grounding, with strict JSON output and deterministic fallback behavior when news is unavailable.
- Multi-modal ingestion supports `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.csv`, images, URLs, audio, and video.
- Audio and video processing uses `pydub` and Azure OpenAI Whisper with OAuth, 24 MB-safe chunking, and rate-limited transcription.
- URL answers are protected with SSRF checks and Azure LLM content moderation before scraping and storage.
- Uploaded documents and media are cleaned up automatically after extraction/transcription.
- Executive reporting aggregates interview answers by event and generates audience-specific AI summaries with direct `.docx` export.

### Architecture Overview

- `apps/api` hosts the FastAPI backend and the Excel-backed repository adapters used by the local POC.
- `apps/api/app/api/routers` contains the domain routers for events, questionnaires, interviews, and reports.
- `apps/api/app/integrations` contains the hybrid RAG client, OCR client, STT client, moderation client, and parser utilities.
- `apps/api/app/repositories/excel_adapter.py` provides the current `mock_database.xlsx` storage adapter.
- `apps/api/app/main.py` wires the routers into the application and exposes the API under `/api/v1`.

### Repository Status

- Phase 0: Foundation and architecture baseline - completed as groundwork.
- Phase 1: Backend implementation and executive polish - completed.

### Current Storage Model

- The application currently uses a mocked Excel repository (`mock_database.xlsx`) for local development.
- Excel is an adapter for the POC only and must stay behind repository interfaces.
- Production persistence is still intended to move to PostgreSQL in the future.

### Setup Requirements

- Install Python dependencies from `apps/api/requirements.txt`.
- Install `FFmpeg` on the system PATH for audio/video processing.
- Use the local `.env.local` file for Azure and agent credentials.
- Do not commit secret-bearing `.env` files or generated Excel data.

### Required Environment Variables

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_CHAT_MODEL`
- `AZURE_OPENAI_WHISPER_ENDPOINT`
- `AZURE_OPENAI_WHISPER_TENANT_ID`
- `AZURE_OPENAI_WHISPER_CLIENT_ID`
- `AZURE_OPENAI_WHISPER_SECRET`
- `AZURE_OPENAI_WHISPER_API`
- `EXTERNAL_NEWS_AGENT_ENDPOINT`
- `EXTERNAL_NEWS_AGENT_API_KEY`
- `EXTERNAL_NEWS_AGENT_PATH`
- `EXTERNAL_NEWS_AGENT_AUTH_HEADER`

### Working Notes

- The API and live tests rely on approved Azure services and a network path that can reach them.
- OCR, STT, moderation, and summaries are all routed through Azure-backed integrations.
- The repository intentionally keeps reference material in `architecture-analysis-workspace/` read-only.

### Repository Layout

- `apps/api` - FastAPI backend, routers, schemas, integrations, and Excel repository adapter
- `apps/worker` - asynchronous processing worker scaffold
- `apps/web/lovable-exported-code` - Lovable export landing zone
- `packages/contracts` - shared contracts and schemas
- `database` - migration and seed planning
- `docs` - architecture, API, database, deployment, and testing documentation
- `infrastructure` - local and GCP infrastructure placeholders
- `tests` - contract, integration, and end-to-end test structure
- `data` - local-only storage guidance and templates

### Branching Strategy

- `main` is the stable baseline branch.
- Work should proceed in short-lived task branches such as `docs/`, `feature/`, `fix/`, `test/`, `refactor/`, `chore/`, or `security/`.

### Documentation

- [API README](apps/api/README.md)
- [Architecture overview](docs/architecture/overview.md)

Reference material under `architecture-analysis-workspace/` is read-only and must not be modified or copied wholesale into this repository.
