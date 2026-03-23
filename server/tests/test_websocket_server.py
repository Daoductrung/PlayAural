"""Regression tests for WebSocket handshake handling."""

from __future__ import annotations

import asyncio
import logging
import socket

import pytest
import websockets

from ..network.websocket_server import WebSocketServer


HOST = "127.0.0.1"


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return int(sock.getsockname()[1])


def _send_keepalive_probe(port: int) -> bytes:
    request = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {HOST}:{port}\r\n"
        f"User-Agent: keepalive-probe\r\n"
        f"Accept: */*\r\n"
        f"Connection: Keep-Alive\r\n"
        f"\r\n"
    ).encode("ascii")

    with socket.create_connection((HOST, port), timeout=5) as sock:
        sock.sendall(request)
        chunks: list[bytes] = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)


@pytest.mark.asyncio
async def test_keepalive_probe_returns_400_without_error_log(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.ERROR)
    port = _get_free_port()
    server = WebSocketServer(host=HOST, port=port)
    await server.start()

    try:
        response = await asyncio.to_thread(_send_keepalive_probe, port)
        await asyncio.sleep(0.1)
    finally:
        await server.stop()

    text = response.decode("utf-8", errors="replace")
    assert "400 Bad Request" in text
    assert "Invalid upgrade: invalid Connection header: Keep-Alive" in text
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


@pytest.mark.asyncio
async def test_valid_websocket_handshake_still_succeeds() -> None:
    port = _get_free_port()
    connected = asyncio.Event()
    disconnected = asyncio.Event()

    async def on_connect(_client) -> None:
        connected.set()

    async def on_disconnect(_client) -> None:
        disconnected.set()

    server = WebSocketServer(
        host=HOST,
        port=port,
        on_connect=on_connect,
        on_disconnect=on_disconnect,
    )
    await server.start()

    try:
        async with websockets.connect(f"ws://{HOST}:{port}", proxy=None):
            await asyncio.wait_for(connected.wait(), timeout=1)
        await asyncio.wait_for(disconnected.wait(), timeout=1)
    finally:
        await server.stop()
