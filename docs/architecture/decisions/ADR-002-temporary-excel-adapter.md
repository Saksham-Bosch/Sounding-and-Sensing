# Title

ADR-002 Local Secret Management

# Status

Proposed

# Context

Phase 0 introduces test and contract scaffolding that depends on local configuration for URLs, IDs, keys, and tokens. Confidential values must remain outside version control while still supporting local diagnostics.

# Decision

- `.env.local` is the approved local-development filename for this repository.
- `.env.example` contains only empty placeholders and safe descriptions.
- Deployed secrets will later use the approved secret-management mechanism.
- Frontend variables must never contain MRA keys.
- Real confidential API URLs must not enter Git history.
- Ignored files are not considered a secure secret store by themselves, so values must not be copied into agent prompts, logs, or screenshots.

# Alternatives considered

- Store local secrets in committed development config files.
- Use ad hoc per-script environment-variable conventions without a documented file contract.

# Consequences

- Local configuration is standardized for test and tooling behavior.
- Secret leakage risk is reduced through explicit storage and logging boundaries.

# Security considerations

- Secrets remain excluded from repository history and review surfaces.
- Configuration errors must report missing-variable names only, never values.

# Validation requirements

- Confirm `.env.local` is ignored.
- Confirm `.env.example` contains no real secret values.
- Confirm tests and helpers do not log key, token, or URL values.

# Unresolved questions

- Final approved runtime secret-store mechanism and operational access workflow.

# Evidence classification

- Confirmed from repository policy: `.env.example` placeholder-only rule and secret non-commit requirement.
- Proposed: `.env.local` as the local-development contract file.

# Date

2026-08-17

# Owner

UNRESOLVED
