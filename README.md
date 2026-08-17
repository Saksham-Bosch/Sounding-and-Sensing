# Sounding and Sensing

Sounding and Sensing is the permanent repository for the Event Information Gathering and Dissemination platform.

Current status: architecture and proof-of-concept planning stage. The repository currently contains scaffold, policy, and contract-oriented placeholders only. It does not claim to implement the full application.

Planned major components:

- Lovable-generated React frontend for an initial frontend-only proof of concept
- Python API for application orchestration and contract enforcement
- Market Research Agent backend integration
- Market Research Agent repository integration
- PostgreSQL database on GCP as the target system of record
- GCP-hosted asynchronous processing worker
- Approved organizational Speech-to-Text integrations
- Approved organizational OCR and document-processing integrations
- Existing organizational portal and multiparty chat integration

Temporary development constraints:

- GCP access is not yet available.
- PostgreSQL is introduced later.
- A local Excel workbook may temporarily act as development storage.
- Excel storage must stay behind repository interfaces.
- Actual Excel data files must never be committed.
- Speech-to-Text and OCR remain simulated or interface-backed until approved services are available.
- No third-party open-source Speech-to-Text or OCR models are added.
- Deterministic file parsers are deferred until organizational approval.
- Phase 0 is for architecture, contracts, configuration, and readiness only.

Excel is a temporary storage adapter, not the production persistence layer.
PostgreSQL on GCP is the target database.
Speech-to-Text and OCR integrations require approved organizational services.

Repository layout summary:

- `apps/api` - application API scaffold
- `apps/worker` - asynchronous processing worker scaffold
- `apps/web/lovable-exported-code` - Lovable export landing zone
- `packages/contracts` - shared contracts and schemas
- `database` - migration and seed planning
- `docs` - architecture, API, database, deployment, and testing documentation
- `infrastructure` - local and GCP infrastructure placeholders
- `tests` - contract, integration, and end-to-end test structure
- `data` - local-only storage guidance and templates

Branching strategy:

- `main` is the stable baseline branch.
- Work should proceed in short-lived task branches such as `docs/`, `feature/`, `fix/`, `test/`, `refactor/`, `chore/`, or `security/`.
- Phase tracking belongs in documentation, issues, labels, milestones, and release tags.

Architecture overview:

- [Proposed architecture overview](docs/architecture/overview.md)

Reference material under `architecture-analysis-workspace/` is read-only and must not be modified or copied wholesale into this repository.
