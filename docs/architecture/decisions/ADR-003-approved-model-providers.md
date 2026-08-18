# Title

ADR-003 API Contract Testing Strategy

# Status

Proposed

# Context

Phase 0 requires a safe and repeatable way to validate external API contracts while preventing unapproved live calls and preventing disclosure of sensitive response content.

# Decision

- Phase 0.5 tests are opt-in live checks against three real dependencies: OCR
	(Azure OpenAI chat/vision), STT (Azure OpenAI Whisper), and the External News
	Agent (topic-to-questionnaire).
- Live calls are disabled by default and require `API_TEST_ALLOW_LIVE_CALLS=true`.
- Each live test skips cleanly (not fails) when required configuration or sample
	assets are missing.
- Raw API responses are not committed; generated output is written only to
	ignored local paths (`.test-output/`).

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
- Each live test asserts a successful (200) response and non-empty extracted
	content (transcription or questionnaire answer).

# Unresolved questions

- Exact endpoint contracts for external services pending authoritative API specifications.

# Evidence classification

- Confirmed from repository policy: no production-service calls by default and no secret leakage.
- Proposed: three-flow opt-in live test structure (OCR, STT, News Agent).

# Date

2026-08-17

# Owner

UNRESOLVED
