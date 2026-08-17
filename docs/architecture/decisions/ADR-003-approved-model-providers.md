# Title

ADR-003 API Contract Testing Strategy

# Status

Proposed

# Context

Phase 0 requires a safe and repeatable way to validate external API contracts while preventing unapproved live calls and preventing disclosure of sensitive response content.

# Decision

- Tests are divided into unit, mocked contract, opt-in live contract, and file-processing tests.
- Live calls are disabled by default.
- API behavior must be discovered without guessing endpoints or schemas.
- Questionnaire output must be validated against a local schema.
- Raw API responses are not committed.
- Sanitized response shapes may become fixtures only after review.

# Alternatives considered

- Treat all contract checks as live tests in default CI.
- Rely only on documentation review without executable contract checks.

# Consequences

- CI remains deterministic and safe by default.
- Live behavior can still be validated when explicitly authorized and configured.

# Security considerations

- Authorization and signed URL details are redacted in diagnostic output.
- Live tests must use synthetic, non-sensitive payloads.

# Validation requirements

- Live tests require explicit opt-in (`API_TEST_ALLOW_LIVE_CALLS=true`).
- Unit and mocked contract tests must run without live network dependencies.
- Contract validation must enforce questionnaire schema checks.

# Unresolved questions

- Exact endpoint contracts for external services pending authoritative API specifications.

# Evidence classification

- Confirmed from repository policy: no production-service calls by default and no secret leakage.
- Proposed: four-part test partition and opt-in live contract process.

# Date

2026-08-17

# Owner

UNRESOLVED
