import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import requests  # type: ignore
except Exception:  # requests may be absent; allow tests to monkeypatch
    requests = None  # type: ignore

__all__ = ["upload_to_cloudflare_stream"]


class CloudflareStreamError(RuntimeError):
    pass


def upload_to_cloudflare_stream(
    file_path: str,
    account_id: Optional[str] = None,
    api_token: Optional[str] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Uploads a file to Cloudflare Stream using the REST API.

    Environment variables used if parameters are omitted:
    - CLOUDFLARE_ACCOUNT_ID
    - CLOUDFLARE_STREAM_API_TOKEN (API token with Stream:Edit perms)

    Returns parsed JSON (dict). Raises CloudflareStreamError on failure.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(path)

    account_id = account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = api_token or os.getenv("CLOUDFLARE_STREAM_API_TOKEN")

    if not account_id or not api_token:
        raise CloudflareStreamError(
            "Missing Cloudflare credentials. Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_STREAM_API_TOKEN."
        )

    if requests is None:
        raise CloudflareStreamError(
            "The 'requests' package is required for uploading. Install with 'pip install requests' or enable the 'uploader' extra."
        )

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/stream"
    headers = {"Authorization": f"Bearer {api_token}"}

    data = {}
    if name:
        data["name"] = name

    with path.open("rb") as fh:
        files = {"file": (path.name, fh)}
        response = requests.post(
            url, headers=headers, data=data, files=files, timeout=120
        )

    try:
        payload = response.json()
    except Exception as exc:  # pragma: no cover - defensive
        raise CloudflareStreamError(f"Invalid response from Cloudflare: {exc}")

    if not response.ok or not payload.get("success"):
        errors = payload.get("errors") if isinstance(payload, dict) else None
        raise CloudflareStreamError(
            f"Upload failed: HTTP {response.status_code}; errors={errors}"
        )

    return payload
