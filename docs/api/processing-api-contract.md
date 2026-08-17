# Processing API Contract

Contract status: Proposed and subject to review.

## Confirmed requirement

- Asset processing status must be queryable and workflow-safe.

## Proposed decision

- `POST /api/v1/interviews/{interviewId}/assets` registers asset metadata only.
- `GET /api/v1/assets/{assetId}/processing-status` returns current processing state.
- `POST /api/v1/events/{eventId}/publish` is a publication placeholder endpoint.

DTO responsibilities:

- Registration DTOs carry metadata and ownership context, not binary payloads.
- Status DTOs carry state, processor type, simulation flag, and message.

## Temporary POC choice

- Processing state transitions may be simulated.

## Unresolved question

- Final asynchronous job identifiers and callback model.

## Future implementation

- Integrate worker execution and approved provider outputs without changing public DTO semantics.
