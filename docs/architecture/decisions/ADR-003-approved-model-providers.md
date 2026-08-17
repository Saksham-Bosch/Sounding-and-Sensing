# ADR-003 Approved Model Providers

Status: Proposed

## Confirmed requirement

- Speech-to-Text and OCR integrations must use approved organizational services.

## Proposed decision

- Open-source STT and OCR models are not introduced.
- STT and OCR remain provider interfaces in Phase 0.
- Real implementation depends on approved organizational service details.

## Temporary POC choice

- Simulated providers may support frontend and workflow testing.

## Unresolved question

- Final approved authentication mechanism (API key, gateway token, or workload identity) per service.

## Future implementation

- Keep credentials outside frontend and Git.
- Approve deterministic parsing libraries through a separate dependency review.
