from __future__ import annotations

import json
from urllib import error, request
from urllib.parse import urlencode


class AadTokenError(RuntimeError):
    """Raised when an Azure AD client-credentials token request fails."""


def fetch_aad_token(
    *,
    tenant_id: str,
    client_id: str,
    client_secret: str,
    scope: str,
    timeout_seconds: int,
) -> str:
    """Fetch a bearer token using the OAuth2 client-credentials grant.

    Only the resulting token is returned to the caller. This function never
    logs the client secret or the issued token.
    """
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }
    ).encode("utf-8")

    req = request.Request(
        url=url,
        method="POST",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise AadTokenError(f"AAD token request failed with status={exc.code}") from exc
    except Exception as exc:  # pragma: no cover - network path
        raise AadTokenError(f"AAD token request failed: {type(exc).__name__}") from exc

    token = data.get("access_token")
    if not token:
        raise AadTokenError("AAD token response did not include an access_token")
    return token
