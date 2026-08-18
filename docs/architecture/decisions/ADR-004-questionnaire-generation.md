# Title

ADR-004 Test Asset Governance

# Status

Proposed

# Context

Phase 0 introduces local file-processing and contract-testing scaffolding. Test inputs and outputs must be governed so private or sensitive material is never committed or exposed.

# Decision

- User-provided audio, video, and documents are local test inputs.
- Uploaded test assets are ignored by default.
- Test inputs must not contain confidential, personal, or production data.
- Original files, extracted content, and generated output remain local.
- Small synthetic fixtures may be committed only after explicit review.
- File size, MIME type, and checksum may be recorded without committing content when sensitive naming context is not exposed.

# Alternatives considered

- Commit all diagnostic test assets for reproducibility.
- Disable file-based testing in Phase 0 entirely.

# Consequences

- Test reproducibility relies on controlled synthetic fixtures and local manifests.
- Sensitive-content leakage risk is significantly reduced.

# Security considerations

- Private assets must never be committed.
- Generated outputs from private inputs must remain ignored and local.

# Validation requirements

- Confirm private asset directories are ignored except required placeholders.
- Confirm generated outputs are ignored.
- Confirm no private assets are staged before commits.

# Unresolved questions

- Final fixture-approval process for synthetic assets shared across teams.

# Evidence classification

- Confirmed from repository policy: no sensitive or user content in Git.
- Proposed: explicit asset-governance controls for Phase 0 testing.

# Date

2026-08-17

# Owner

UNRESOLVED
