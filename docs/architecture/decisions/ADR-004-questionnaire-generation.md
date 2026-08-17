# ADR-004 Questionnaire Generation

Status: Proposed

## Confirmed requirement

- Questionnaire generation is driven by event details and standardized question-answer context.

## Proposed decision

- Event details and standard answers are sent in one request.
- MRA integration returns the complete questionnaire.
- Questionnaire output is validated against a strict JSON schema.
- Generated questions are stored in deterministic order.

## Temporary POC choice

- Frontend displays one current question at a time while server-side ordering remains authoritative.

## Unresolved question

- Final policy for regenerating or partially updating questionnaires after an interview starts.

## Future implementation

- Agent must not be called separately for each displayed question.
