"""Tests for the desktop client's WebSocket SSL context factory."""

from pathlib import Path
import ssl
import sys
from unittest.mock import patch


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

import certifi
import ssl_utils
from ssl_utils import make_ssl_context


def test_plain_ws_returns_none():
    assert make_ssl_context("ws://playaural.ddt.one:8000") is None
    assert make_ssl_context("ws://localhost:8000") is None


def test_local_dev_hosts_disable_certificate_verification():
    for url in (
        "wss://localhost:8000",
        "wss://127.0.0.1:8000",
        "wss://[::1]:8000",
        "WSS://LOCALHOST:8000/ws",
    ):
        ctx = make_ssl_context(url)
        assert ctx is not None
        assert ctx.check_hostname is False
        assert ctx.verify_mode == ssl.CERT_NONE


def test_production_wss_enforces_strict_validation_and_loads_certifi():
    empty_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    empty_ctx.check_hostname = True
    empty_ctx.verify_mode = ssl.CERT_REQUIRED

    with patch.object(ssl_utils.ssl, "create_default_context", return_value=empty_ctx):
        ctx = make_ssl_context("wss://playaural.ddt.one")

    assert ctx is empty_ctx
    assert ctx.check_hostname is True
    assert ctx.verify_mode == ssl.CERT_REQUIRED
    assert ctx.cert_store_stats()["x509_ca"] > 0


def test_production_wss_falls_back_gracefully_when_certifi_missing():
    with patch.object(ssl_utils, "certifi", None):
        ctx = make_ssl_context("wss://playaural.ddt.one")

    assert ctx is not None
    assert ctx.check_hostname is True
    assert ctx.verify_mode == ssl.CERT_REQUIRED


def test_certifi_bundle_path_exists():
    assert Path(certifi.where()).is_file()
