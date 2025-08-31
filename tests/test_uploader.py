from pathlib import Path
import types

import importlib
import sys

import video_trimmer.uploader as up


class DummyResponse:
    def __init__(self, ok=True, status=200, payload=None):
        self.ok = ok
        self.status_code = status
        self._payload = payload or {"success": True, "result": {"uid": "abc123"}}

    def json(self):
        return self._payload


def test_upload_success(monkeypatch, tmp_path):
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"x")

    called = {}

    def fake_post(url, headers=None, data=None, files=None, timeout=None):
        called["url"] = url
        called["headers"] = headers
        called["data"] = data
        assert "file" in files
        return DummyResponse()

    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acc")
    monkeypatch.setenv("CLOUDFLARE_STREAM_API_TOKEN", "tok")

    # Ensure a dummy requests object exists even if not installed
    class DummyRequests:
        post = staticmethod(fake_post)

    monkeypatch.setattr(up, "requests", DummyRequests)

    payload = up.upload_to_cloudflare_stream(str(f), name=f.name)
    assert payload["success"] is True
    assert "acc" in called["url"]
    assert called["headers"]["Authorization"].startswith("Bearer ")


def test_upload_missing_creds(tmp_path):
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"x")
    try:
        up.upload_to_cloudflare_stream(str(f))
    except up.CloudflareStreamError as e:
        assert "Missing Cloudflare credentials" in str(e)
    else:  # pragma: no cover - ensure failure surfaces
        assert False
