# Phase 0.5: Azure API Verification Spike Summary

## Objective
Verify connectivity, authentication, and payload contracts with the approved external Azure APIs and Market Research Agent (MRA) prior to building the local FastAPI application.

## 1. OCR (Azure OpenAI Chat Model)
*   **Status:** PASSED
*   **Findings:** The `gpt-5.1-chat-cia` model successfully authenticated. Initial tests resulted in truncated extraction (98 characters). The payload was updated with strict line-by-line extraction system prompts. 
*   **Future Recommendation:** For production, this should be migrated to Azure AI Document Intelligence for deterministic layout extraction rather than relying on LLM vision capabilities.

## 2. Market Research Agent (News Agent)
*   **Status:** PASSED
*   **Findings:** The deployed endpoint was confirmed to be `/query` (not `/ask`). Initial tests returned raw search fallback text. The query payload was successfully updated to enforce a strict JSON Schema requirement, ensuring the agent returns the exact `Customized Event Interview` structure required by the frontend POC.

## 3. Speech-to-Text (STT - Azure Whisper)
*   **Status:** BLOCKED (Network / Infrastructure)
*   **Findings:** The client-side logic successfully fetched the Entra ID (Service Principal) token and built the multipart HTTP request. However, the Azure OpenAI resource (`oai-sds-rag-dev.openai.azure.com`) rejected the request with a **403 "Public access is disabled"** error. 
*   **Resolution:** An IP whitelisting request has been raised. Additionally, the video-to-audio extraction utility was updated to output `.mp3` instead of `.wav` to ensure compliance with Whisper's 25MB file size limit once network access is granted.

## 4. Security & Authentication
*   **Status:** PASSED
*   **Findings:** Service Principal (AAD) authentication was verified. All secrets are strictly maintained in `.env.local` and no credentials, API keys, or raw tokens have been committed to the repository.
