"""Shared SSL context factory for the PlayAural client.

A single place that encodes the two-tier SSL policy used everywhere the
client opens a WebSocket connection:

* Production servers  → full CA certificate validation (strict).
* Local dev servers   → certificate verification disabled (self-signed OK).
"""

import ssl


def make_ssl_context(server_url: str):
    """Return an SSL context appropriate for *server_url*, or ``None``.

    Args:
        server_url: WebSocket URL, e.g. ``"wss://playaural.ddt.one"`` or
                    ``"ws://localhost:8000"``.

    Returns:
        An :class:`ssl.SSLContext` for ``wss://`` URLs, or ``None`` for
        plain ``ws://`` URLs (no TLS needed).
    """
    if not server_url.startswith("wss://"):
        return None

    host = server_url.split("://", 1)[-1].split("/")[0].split(":")[0]
    ctx = ssl.create_default_context()
    if host in ("localhost", "127.0.0.1", "::1"):
        # Local dev: self-signed certificates are acceptable.
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx
