# Title

ADR-005 GCP Dependency Boundary

# Status

Proposed

# Context

Phase 0 development occurs before GCP access and managed service provisioning are available. Local test foundations are needed without claiming cloud integration readiness.

# Decision

- Phase 0 test scripts can be developed locally.
- Native processors may be evaluated locally.
- Cloud SQL, Cloud Storage, Pub/Sub, Cloud Run, Speech-to-Text, and Document AI integration require later GCP access.
- Local tests must not pretend to prove GCP integration.
- GCP-specific functionality remains mocked or contract-only until access is available.

# Alternatives considered

- Block all test and contract work until cloud access is available.
- Implement provisional cloud integrations using guessed or placeholder service behavior.

# Consequences

- Phase 0 can progress on interfaces and test discipline without cloud coupling.
- Cloud-specific confidence remains deferred until authorized environments exist.

# Security considerations

- No unmanaged cloud credentials are introduced during local scaffolding.
- Live cloud service calls remain prohibited without explicit authorization.

# Validation requirements

- Confirm no cloud resources are provisioned during this phase.
- Confirm GCP-dependent behaviors are represented as mocks or contracts only.

# Unresolved questions

- Final cloud project layout, IAM boundaries, and deployment topology.

# Evidence classification

- Confirmed from repository policy: no cloud provisioning or production-service calls in Phase 0.
- Proposed: strict local-versus-cloud boundary for testing and contract validation.

# Date

2026-08-17

# Owner

UNRESOLVED
