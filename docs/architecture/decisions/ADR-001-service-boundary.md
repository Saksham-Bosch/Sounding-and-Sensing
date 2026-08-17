# Title

ADR-001 Phase 0 Service Boundary

# Status

Proposed

# Context

The repository is the permanent implementation repository for the Event Information Gathering and Dissemination platform. Phase 0 is intended to establish architecture decisions, contracts, diagnostics, and test foundations, while GCP access and production integrations are not yet available.

# Decision

- The permanent repository is the implementation repository.
- `architecture-analysis-workspace/` remains ignored and read-only reference material.
- Phase 0 covers contracts, diagnostics, test foundations, and architecture decisions.
- Production application implementation is out of scope for this branch.
- The Event domain is proposed as isolated from generic MRA workflows.
- Portal and MRA integration details remain adapter-boundary concerns.

# Alternatives considered

- Split into independent runtime services during Phase 0.
- Keep all event and integration concerns tightly coupled in one runtime module.

# Consequences

- Contract-first development can proceed without committing to premature runtime decomposition.
- Service extraction remains possible after integration and scale evidence are collected.

# Security considerations

- Reference workspace stays non-executable and non-authoritative for production logic.
- Boundary separation reduces risk of secret propagation across unrelated modules.

# Validation requirements

- Confirm Phase 0 changes are contract and test-foundation scoped.
- Confirm runtime production capabilities are not claimed as implemented.

# Unresolved questions

- The exact production service boundary remains subject to architecture review.
- Which components should be extracted first when operational data is available.

# Evidence classification

- Confirmed from repository policy: permanent repository boundary and read-only reference workspace policy.
- Proposed: Event-domain isolation and deferred extraction strategy.

# Date

2026-08-17

# Owner

UNRESOLVED
