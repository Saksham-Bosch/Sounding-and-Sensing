# Target PostgreSQL Model

Status: Proposed target model. No migrations are generated in Phase 0.

## Confirmed requirement

- PostgreSQL on GCP is the target system of record.

## Proposed decision

Planned entities:

- events
- standard_questions
- standard_answers
- questionnaire_generations
- questionnaires
- generated_questions
- interview_sessions
- interview_answers
- assets
- processing_jobs

Planned model properties:

- UUID primary keys
- Organization scoping fields
- Timestamps for create and update
- Status and lifecycle fields
- Referential integrity across event, questionnaire, interview, and asset flows

## Temporary POC choice

- Contracts are defined before physical PostgreSQL migrations.

## Unresolved question

- Partitioning and retention approach for long-running event histories.

## Future implementation

- Create migrations only after cloud and database environment approval.
