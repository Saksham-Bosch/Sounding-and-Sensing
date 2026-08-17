# Interview API Contract

Contract status: Proposed and subject to review.

## Confirmed requirement

- Interview sessions must progress through ordered questionnaire questions.

## Proposed decision

- `POST /api/v1/events/{eventId}/interviews` starts an interview session.
- `GET /api/v1/interviews/{interviewId}/current-question` returns one current question.
- `POST /api/v1/interviews/{interviewId}/answers/text` records a text answer.
- `POST /api/v1/interviews/{interviewId}/complete` marks interview completion.

DTO responsibilities:

- Request DTOs capture answer content and question references.
- Response DTOs return session status and next question position.

## Temporary POC choice

- Current-question behavior may be mocked in the frontend POC.

## Unresolved question

- Retry and idempotency behavior for duplicate answer submissions.

## Future implementation

- Persist final answer ordering and completion state behind repository interfaces.
