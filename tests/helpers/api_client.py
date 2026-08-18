from __future__ import annotations

import json
import mimetypes
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urljoin

from tests.helpers.redaction import redact_headers, redact_url


@dataclass(frozen=True)
class ApiCallResult:
    status_code: int
    content_type: str
    body: bytes

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text())

    def preview(self, limit: int = 500) -> str:
        text = self.text()
        return text if len(text) <= limit else text[:limit] + "...(truncated)"


def join_base_and_path(base_url: str, endpoint_path: str) -> str:
    base = base_url.rstrip("/") + "/"
    suffix = endpoint_path.lstrip("/")
    return urljoin(base, suffix)


def build_multipart_body(
    *,
    file_path: Path,
    file_field: str,
    extra_fields: dict[str, str] | None = None,
) -> tuple[bytes, str]:
    boundary = f"phase0-{uuid.uuid4().hex}"
    safe_name = os.path.basename(file_path)
    content_type = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()

    chunks: list[bytes] = []
    for key, value in (extra_fields or {}).items():
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        chunks.append(value.encode("utf-8"))
        chunks.append(b"\r\n")

    chunks.append(f"--{boundary}\r\n".encode("utf-8"))
    chunks.append(
        (
            f'Content-Disposition: form-data; name="{file_field}"; filename="{safe_name}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
    )
    chunks.append(file_bytes)
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))

    body = b"".join(chunks)
    header_value = f"multipart/form-data; boundary={boundary}"
    return body, header_value


def safe_request(
    method: str,
    url: str,
    headers: dict[str, str] | None,
    body: bytes | None,
    timeout_seconds: int,
    max_retries: int,
) -> ApiCallResult:
    """Bounded-retry request helper for opt-in live tests.

    Returns the full response body so callers can parse JSON payloads.
    Error paths only ever surface redacted headers/URLs in diagnostics.
    """
    req = request.Request(url=url, method=method.upper(), headers=headers or {}, data=body)

    attempts = max_retries + 1
    last_exception: Exception | None = None
    for _ in range(attempts):
        try:
            with request.urlopen(req, timeout=timeout_seconds) as resp:
                raw = resp.read()
                return ApiCallResult(
                    status_code=int(resp.status),
                    content_type=str(resp.headers.get("Content-Type", "")),
                    body=raw,
                )
        except error.HTTPError as exc:
            raw = exc.read()
            return ApiCallResult(
                status_code=int(exc.code),
                content_type=str(exc.headers.get("Content-Type", "")),
                body=raw,
            )
        except Exception as exc:  # pragma: no cover - network path
            last_exception = exc

    redacted_headers = redact_headers(headers)
    redacted_url = redact_url(url)
    raise RuntimeError(
        f"API request failed after bounded retries. method={method.upper()} url={redacted_url} headers={redacted_headers} error={type(last_exception).__name__}"
    )
