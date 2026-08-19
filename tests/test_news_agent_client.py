import asyncio

import httpx

import app.integrations.mra.client as client_mod


class FakeResponse:
    def __init__(self, status_code: int, data: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._data = data
        self.text = text

    def json(self):
        if self._data is None:
            raise ValueError("no json body")
        return self._data


def _patch_common_config(monkeypatch):
    monkeypatch.setattr(client_mod, "MRA_ENDPOINT", "https://mra.example.test")
    monkeypatch.setattr(client_mod, "MRA_API_KEY", "mra-key")
    monkeypatch.setattr(client_mod, "MRA_PATH", "/query")
    monkeypatch.setattr(client_mod, "MRA_AUTH_HEADER", "x-api-key")
    monkeypatch.setattr(client_mod, "AZURE_OPENAI_ENDPOINT", "https://azure.example.test")
    monkeypatch.setattr(client_mod, "AZURE_OPENAI_API_KEY", "azure-key")
    monkeypatch.setattr(client_mod, "AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    monkeypatch.setattr(client_mod, "AZURE_OPENAI_CHAT_MODEL", "gpt-test")


def test_rag_pipeline_clean_retrieval_and_azure_generation(monkeypatch):
    _patch_common_config(monkeypatch)

    class RagClient:
        def __init__(self, *args, **kwargs):
            self.scrape_seen = False

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json, headers, timeout=None):
            if url.endswith("/query"):
                assert json["query"] == "AI in healthcare"
                assert headers["x-api-key"] == "mra-key"
                return FakeResponse(
                    200,
                    {
                        "news": {
                            "top_results": [
                                {
                                    "title": "AI pilot",
                                    "url": "https://source.example/one",
                                    "description": "Hospitals are deploying AI triage tools.",
                                }
                            ]
                        }
                    },
                )

            assert "/openai/deployments/gpt-test/chat/completions" in url
            prompt = json["messages"][1]["content"]
            assert "Source URL: https://source.example/one" in prompt
            assert "triage" in prompt.lower()
            return FakeResponse(
                200,
                {
                    "choices": [
                        {
                            "message": {
                                "content": '{"schema_version":"1.0","title":"Customized Event Interview","questions":[{"id":"q-001","position":1,"text":"What outcomes are expected from AI triage adoption?","type":"OPEN_TEXT","required":true,"allowed_input_types":["text","audio","image","pdf","docx","pptx","xlsx","video","url"],"guidance":null,"branch_rules":[]}]}'
                            }
                        }
                    ]
                },
            )

        async def get(self, url, timeout=None, follow_redirects=None):
            assert url == "https://source.example/one"
            return FakeResponse(200, text="<html><body><p>AI triage reduced intake delays in two hospitals.</p></body></html>")

    monkeypatch.setattr(client_mod.httpx, "AsyncClient", RagClient)

    result = asyncio.run(client_mod.generate_questionnaire_from_mra("AI in healthcare"))

    assert result["title"] == "Customized Event Interview"
    assert result["questions"][0]["text"].startswith("What outcomes")


def test_rag_pipeline_uses_snippets_when_scraping_fails(monkeypatch):
    _patch_common_config(monkeypatch)

    class SnippetFallbackClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json, headers, timeout=None):
            if url.endswith("/query"):
                return FakeResponse(
                    200,
                    {
                        "news": {
                            "top_results": [
                                {
                                    "title": "Grid challenge",
                                    "url": "https://source.example/blocked",
                                    "description": "Grid capacity and depot charging remain major constraints.",
                                }
                            ]
                        }
                    },
                )

            prompt = json["messages"][1]["content"]
            assert "Snippet fallback context" in prompt
            assert "Grid capacity" in prompt
            return FakeResponse(
                200,
                {
                    "choices": [
                        {
                            "message": {
                                "content": '{"schema_version":"1.0","title":"Customized Event Interview","questions":[{"id":"q-001","position":1,"text":"How are grid constraints affecting electrification timelines?","type":"OPEN_TEXT","required":true,"allowed_input_types":["text","audio","image","pdf","docx","pptx","xlsx","video","url"],"guidance":null,"branch_rules":[]}]}'
                            }
                        }
                    ]
                },
            )

        async def get(self, url, timeout=None, follow_redirects=None):
            return FakeResponse(403, text="blocked")

    monkeypatch.setattr(client_mod.httpx, "AsyncClient", SnippetFallbackClient)

    result = asyncio.run(client_mod.generate_questionnaire_from_mra("public transportation electrification"))

    assert result["title"] == "Customized Event Interview"
    assert "grid" in result["questions"][0]["text"].lower()


def test_hard_fallback_only_when_both_networks_fail(monkeypatch):
    _patch_common_config(monkeypatch)

    class DownClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json, headers, timeout=None):
            raise httpx.ConnectError("network down")

        async def get(self, url, timeout=None, follow_redirects=None):
            raise httpx.ConnectError("network down")

    monkeypatch.setattr(client_mod.httpx, "AsyncClient", DownClient)

    result = asyncio.run(client_mod.generate_questionnaire_from_mra("AI in healthcare"))

    assert result["title"] == "Standard Fallback Interview"
    assert len(result["questions"]) == 1
