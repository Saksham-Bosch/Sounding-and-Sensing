# ADR-002 Temporary Excel Adapter

Status: Proposed

## Confirmed requirement

- Local development may require temporary non-database storage before GCP and PostgreSQL are available.

## Proposed decision

- Excel may temporarily support local development.
- Excel access must occur through repository interfaces.
- UI and business services must not directly access workbook sheets.
- Files are not stored inside the workbook.

## Temporary POC choice

- Use a replaceable Excel-backed adapter for local-only development behavior.

## Unresolved question

- Exact export and import control points for later migration verification.

## Future implementation

- Replace Excel with PostgreSQL.
- Keep workbooks free of production or sensitive data.
- Keep actual workbook files Git-ignored.
- Treat Excel as unsuitable for authorization, concurrency, and production use.
