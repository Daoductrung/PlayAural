"""Token generation for supported voice providers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any


def _base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def generate_livekit_token(
    *,
    api_key: str,
    api_secret: str,
    identity: str,
    name: str,
    room: str,
    ttl_seconds: int,
    metadata: dict[str, Any] | None = None,
) -> tuple[str, int]:
    issued_at = int(time.time())
    expires_at = issued_at + ttl_seconds
    header = {"alg": "HS256", "typ": "JWT"}
    claims: dict[str, Any] = {
        "exp": expires_at,
        "iss": api_key,
        "name": name,
        "nbf": issued_at - 5,
        "sub": identity,
        "video": {
            "canPublish": True,
            "canPublishData": False,
            "canPublishSources": ["microphone"],
            "canSubscribe": True,
            "room": room,
            "roomJoin": True,
        },
    }
    if metadata:
        claims["metadata"] = json.dumps(metadata, separators=(",", ":"), sort_keys=True)

    encoded_header = _base64url(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    encoded_claims = _base64url(json.dumps(claims, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_claims}".encode("ascii")
    signature = hmac.new(api_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_claims}.{_base64url(signature)}", expires_at
