# Questionnaire API Contract

Contract status: Proposed and subject to review.

## Confirmed requirement

- Standard questions and answers contribute to generated questionnaires.

## Proposed decision

- `POST /api/v1/events/{eventId}/standard-answers` upserts context answers.
- `POST /api/v1/events/{eventId}/questionnaire-generations` triggers questionnaire generation.
- `GET /api/v1/events/{eventId}/questionnaires/current` returns questionnaire metadata and current question pointer.

DTO responsibilities:

- Request DTOs carry event context and standardized answers.
- Response DTOs carry ordered questions and schema version.

## Temporary POC choice

- POC uses deterministic mock data for displayed question flow.

## Unresolved question

- Regeneration policy when an interview is already in progress.

## Future implementation

- Contract tests enforce strict schema validation for generated payloads.
