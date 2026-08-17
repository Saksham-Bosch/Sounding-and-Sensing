# Event API Contract

Contract status: Proposed and subject to review.

## Confirmed requirement

- Event creation and lifecycle status must be represented by stable API DTOs.

## Proposed decision

- `POST /api/v1/events` creates an event shell.
- `GET /api/v1/events/{eventId}` returns event summary and state.
- `PATCH /api/v1/events/{eventId}` updates editable event metadata.

## Temporary POC choice

- Frontend may use mocked responses while contract fields remain stable.

## Unresolved question

- Which event fields become immutable after questionnaire generation.

## Future implementation

- Add authorization and tenant enforcement once identity contracts are finalized.
