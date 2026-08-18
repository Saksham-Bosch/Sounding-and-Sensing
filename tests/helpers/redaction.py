from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


_SENSITIVE_HEADER_KEYS = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "api-key",
}

_SENSITIVE_QUERY_KEYS = {
    "token",
    "access_token",
    "signature",
    "sig",
    "x-amz-signature",
    "api_key",
    "key",
}


def redact_headers(headers: dict[str, str] | None) -> dict[str, str]:
    if not headers:
        return {}

    redacted: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in _SENSITIVE_HEADER_KEYS:
            redacted[key] = "***REDACTED***"
        else:
            redacted[key] = value
    return redacted


def redact_url(url: str | None) -> str:
    if not url:
        return ""

    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    safe_query = []
    for key, value in query:
        if key.lower() in _SENSITIVE_QUERY_KEYS:
            safe_query.append((key, "***REDACTED***"))
        else:
            safe_query.append((key, value))

    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(safe_query), parts.fragment))


def redact_text(text: str, known_secret_values: list[str] | None = None) -> str:
    if not text:
        return ""

    redacted = text
    for secret in known_secret_values or []:
        if secret:
            redacted = redacted.replace(secret, "***REDACTED***")
    return redacted
