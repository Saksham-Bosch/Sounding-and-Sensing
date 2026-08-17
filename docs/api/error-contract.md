# Error Contract

Contract status: Proposed and subject to review.

## Confirmed requirement

- API failures require a stable machine-readable error envelope.

## Proposed decision

- Standard error object fields: `code`, `message`, `correlationId`, `fieldErrors`.
- `fieldErrors` contains per-field validation failures when applicable.

## Temporary POC choice

- Correlation IDs may be deterministic placeholders in local-only workflows.

## Unresolved question

- Final internal-to-external error code mapping taxonomy.

## Future implementation

- Add consistent mapping across API, worker, integrations, and portal handoff paths.
