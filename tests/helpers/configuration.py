from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


def _to_int(value: str | None, default: int) -> int:
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _load_env_file(file_path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not file_path.exists():
        return env

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def _first_present(env: dict[str, str], *keys: str) -> str | None:
    for key in keys:
        value = env.get(key)
        if value is not None and value.strip() != "":
            return value
    return None


@dataclass(frozen=True)
class Phase0TestSettings:
    api_test_allow_live_calls: bool
    api_test_timeout_seconds: int
    api_test_max_retries: int

    # OCR (Azure OpenAI chat/vision model used to extract text from documents)
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_api_version: str | None = None
    azure_openai_chat_model: str | None = None

    # STT (Azure OpenAI Whisper transcription, authenticated via AAD or API key)
    whisper_endpoint: str | None = None
    whisper_client_id: str | None = None
    whisper_tenant_id: str | None = None
    whisper_secret: str | None = None
    whisper_api_key: str | None = None
    whisper_deployment: str = "whisper"
    whisper_api_version: str = "2024-06-01"

    # External News/Research Agent (topic -> questionnaire)
    news_agent_endpoint: str | None = None
    news_agent_api_key: str | None = None
    news_agent_path: str = "/ask"
    news_agent_auth_header: str = "x-api-key"

    def redacted_summary(self) -> dict[str, object]:
        return {
            "api_test_allow_live_calls": self.api_test_allow_live_calls,
            "api_test_timeout_seconds": self.api_test_timeout_seconds,
            "api_test_max_retries": self.api_test_max_retries,
            "azure_openai_endpoint_configured": bool(self.azure_openai_endpoint),
            "azure_openai_api_key_configured": bool(self.azure_openai_api_key),
            "azure_openai_api_version_configured": bool(self.azure_openai_api_version),
            "azure_openai_chat_model_configured": bool(self.azure_openai_chat_model),
            "whisper_endpoint_configured": bool(self.whisper_endpoint),
            "whisper_aad_configured": bool(self.whisper_client_id and self.whisper_tenant_id and self.whisper_secret),
            "whisper_api_key_configured": bool(self.whisper_api_key),
            "news_agent_endpoint_configured": bool(self.news_agent_endpoint),
            "news_agent_api_key_configured": bool(self.news_agent_api_key),
        }

    def missing_for_live(self, service: str) -> list[str]:
        if service == "ocr":
            mapping = {
                "AZURE_OPENAI_ENDPOINT": self.azure_openai_endpoint,
                "AZURE_OPENAI_API_KEY": self.azure_openai_api_key,
                "AZURE_OPENAI_API_VERSION": self.azure_openai_api_version,
                "AZURE_OPENAI_CHAT_MODEL": self.azure_openai_chat_model,
            }
            return [name for name, value in mapping.items() if not value]

        if service in ("stt_audio", "stt_video"):
            missing: list[str] = []
            if not self.whisper_endpoint:
                missing.append("AZURE_OPENAI_WHISPER_ENDPOINT")
            has_aad = bool(self.whisper_client_id and self.whisper_tenant_id and self.whisper_secret)
            has_key = bool(self.whisper_api_key)
            if not (has_aad or has_key):
                missing.append(
                    "AZURE_OPENAI_WHISPER_CLIENT_ID+AZURE_OPENAI_WHISPER_TENANT_ID+AZURE_OPENAI_WHISPER_SECRET"
                    " (or AZURE_OPENAI_WHISPER_API as an API key)"
                )
            return missing

        if service == "news_agent":
            mapping = {
                "EXTERNAL_NEWS_AGENT_ENDPOINT": self.news_agent_endpoint,
                "EXTERNAL_NEWS_AGENT_API_KEY": self.news_agent_api_key,
            }
            return [name for name, value in mapping.items() if not value]

        return [f"unknown service: {service}"]


def load_test_settings(repo_root: Path | None = None) -> Phase0TestSettings:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    env_file = repo_root / ".env.local"
    env = _load_env_file(env_file)

    # Environment variables from the shell override .env.local values.
    for key, value in os.environ.items():
        if value is not None:
            env[key] = value

    timeout = _to_int(_first_present(env, "API_TEST_TIMEOUT_SECONDS"), 20)
    retries = _to_int(_first_present(env, "API_TEST_MAX_RETRIES"), 2)

    return Phase0TestSettings(
        api_test_allow_live_calls=_to_bool(_first_present(env, "API_TEST_ALLOW_LIVE_CALLS"), default=False),
        api_test_timeout_seconds=max(timeout, 1),
        api_test_max_retries=max(retries, 0),
        azure_openai_endpoint=_first_present(env, "AZURE_OPENAI_ENDPOINT"),
        azure_openai_api_key=_first_present(env, "AZURE_OPENAI_API_KEY"),
        azure_openai_api_version=_first_present(env, "AZURE_OPENAI_API_VERSION"),
        azure_openai_chat_model=_first_present(env, "AZURE_OPENAI_CHAT_MODEL"),
        whisper_endpoint=_first_present(env, "AZURE_OPENAI_WHISPER_ENDPOINT"),
        whisper_client_id=_first_present(env, "AZURE_OPENAI_WHISPER_CLIENT_ID"),
        whisper_tenant_id=_first_present(env, "AZURE_OPENAI_WHISPER_TENANT_ID"),
        whisper_secret=_first_present(env, "AZURE_OPENAI_WHISPER_SECRET"),
        whisper_api_key=_first_present(env, "AZURE_OPENAI_WHISPER_API"),
        whisper_deployment=_first_present(env, "AZURE_OPENAI_WHISPER_DEPLOYMENT") or "whisper",
        whisper_api_version=_first_present(env, "AZURE_OPENAI_WHISPER_API_VERSION") or "2024-06-01",
        news_agent_endpoint=_first_present(env, "EXTERNAL_NEWS_AGENT_ENDPOINT"),
        news_agent_api_key=_first_present(env, "EXTERNAL_NEWS_AGENT_API_KEY"),
        news_agent_path=_first_present(env, "EXTERNAL_NEWS_AGENT_PATH") or "/ask",
        news_agent_auth_header=_first_present(env, "EXTERNAL_NEWS_AGENT_AUTH_HEADER") or "x-api-key",
    )


@lru_cache(maxsize=1)
def get_test_settings() -> Phase0TestSettings:
    return load_test_settings()

