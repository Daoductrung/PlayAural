"""Shared SSL context factory for the PlayAural client.

A single place that encodes the two-tier SSL policy used everywhere the
client opens a WebSocket connection:

* Production servers  → full CA certificate validation (strict).
* Local dev servers   → certificate verification disabled (self-signed OK).
"""

from __future__ import annotations

import os
import ssl
from urllib.parse import urlsplit

try:
    import certifi
except ImportError:  # pragma: no cover - fallback when certifi is unavailable
    certifi = None


_LOCAL_DEV_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


def _load_certifi_bundle(ctx: ssl.SSLContext) -> None:
    """Supplement the OS trust store with certifi's CA bundle when available."""
    if certifi is None:
        return
    cafile = certifi.where()
    if cafile and os.path.isfile(cafile):
        # Windows OpenSSL only reads certificates already cached in the local
        # certificate store without Schannel's on-demand root fetch, so missing
        # roots like self-signed ISRG Root X2 must come from certifi's bundle.
        ctx.load_verify_locations(cafile=cafile)


def make_ssl_context(server_url: str) -> ssl.SSLContext | None:
    """Return an SSL context appropriate for *server_url*, or ``None``.

    Args:
        server_url: WebSocket URL, e.g. ``"wss://playaural.ddt.one"`` or
                    ``"ws://localhost:8000"``.

    Returns:
        An :class:`ssl.SSLContext` for ``wss://`` URLs, or ``None`` for
        plain ``ws://`` URLs (no TLS needed).
    """
    parsed = urlsplit(server_url)
    if parsed.scheme != "wss":
        return None

    host = parsed.hostname or ""
    ctx = ssl.create_default_context()
    if host in _LOCAL_DEV_HOSTS:
        # Local dev: self-signed certificates are acceptable.
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        _load_certifi_bundle(ctx)
    return ctx
