# Proposed Architecture Overview

This document describes the proposed architecture for the Event Information Gathering and Dissemination platform.

The planned request path is:

Lovable frontend
→ application API
→ repository interfaces
→ temporary Excel adapter initially
→ PostgreSQL adapter later
→ Market Research Agent integration
→ processing worker
→ approved Speech-to-Text providers
→ approved OCR and document-processing providers
→ portal integration later

This is a proposed architecture, not a statement of completed implementation.

Key design intent:

- The frontend begins as a frontend-only proof of concept using mock data.
- The API owns application behavior and enforces contracts.
- Repository interfaces hide whether temporary Excel storage or PostgreSQL backs the data layer.
- STT and OCR remain simulated or interface-backed until approved organizational services are available.
- The worker handles asynchronous processing and provider-specific tasks.
- Portal and chat integration is planned for a later phase.
