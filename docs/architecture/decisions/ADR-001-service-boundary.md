# ADR-001 Service Boundary

Status: Proposed

## Confirmed requirement

- The platform must support API, worker, web, and integration concerns within one repository during early delivery.

## Proposed decision

- Start with a modular monorepo.
- Keep the Event domain isolated from integration adapters.
- Keep portal and MRA integrations behind adapters.

## Temporary POC choice

- Retain components in one repository while contracts and boundaries stabilize.

## Unresolved question

- Which boundaries should become independently deployed services first.

## Future implementation

- Reassess extraction into independent services after real integration behavior and scaling requirements are known.
