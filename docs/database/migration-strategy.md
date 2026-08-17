# Migration Strategy

Status: Proposed migration path.

## Confirmed requirement

- Temporary Excel-backed development data must be moved into PostgreSQL with controlled validation.

## Proposed decision

Migration sequence:

1. Excel adapter
2. Export validation
3. PostgreSQL migrations
4. Controlled data import
5. PostgreSQL adapter
6. Excel adapter retirement

## Temporary POC choice

- Keep migration as documentation-only in Phase 0.

## Unresolved question

- Final acceptance criteria and rollback thresholds for cutover.

## Future implementation

- Add repeatable migration scripts and verifiable reconciliation reports.
