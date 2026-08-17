# Temporary Excel Schema

Status: Proposed for local development only.

## Confirmed requirement

- Temporary storage must keep identifiers and relationships explicit while staying replaceable.

## Proposed decision

Workbook sheets:

- Events
- StandardQuestions
- StandardAnswers
- QuestionnaireGenerations
- Questionnaires
- GeneratedQuestions
- InterviewSessions
- InterviewAnswers
- Assets
- ProcessingJobs

Each sheet should include:

- UUID identifier columns
- Foreign-key-like ID columns
- Status columns where lifecycle applies
- ISO 8601 timestamp columns
- Organization ID placeholders

## Temporary POC choice

- Workbook-based storage is used only through repository interfaces.

## Unresolved question

- Final sheet-level validation policy for migration pre-checks.

## Future implementation

- No binary storage in workbook sheets.
- No secrets in workbook rows.
- No sensitive production data in workbook rows.
- Replace workbook adapter with PostgreSQL adapter.
