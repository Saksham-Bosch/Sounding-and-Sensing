# ADR-005 Tenant Identity

Status: Proposed

## Confirmed requirement

- Multi-organization isolation is required for future production architecture.

## Proposed decision

- Tenant-aware fields are preserved in contracts and storage designs from Phase 0 onward.

## Temporary POC choice

- Use placeholders for organization identifiers in contracts and schemas.

## Unresolved question

- User identity model.
- Organization identifier authority.
- JWT claims mapping.
- Event ownership model.
- Cross-organization isolation mechanics.
- Portal identity mapping approach.

## Future implementation

- Final tenant and identity model will be defined after organizational identity constraints are confirmed.
