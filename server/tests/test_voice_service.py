import asyncio
import base64
import hashlib
import hmac
import json
from pathlib import Path

import pytest

from ..core.server import Server
from ..messages.localization import Localization
from ..tables.manager import TableManager
from ..users.test_user import MockUser
from ..voice import VoiceContext, VoiceService


class RecordingConnection:
    def __init__(self):
        self.sent: list[dict] = []

    async def send(self, packet: dict) -> None:
        self.sent.append(packet)


def _make_server() -> Server:
    Localization.init(Path("server/locales"))
    Localization.preload_bundles()
    server = Server.__new__(Server)
    server._tables = TableManager()
    server._tables._server = server
    server._db = None
    server._users = {}
    server._user_states = {}
    server._voice = VoiceService(
        enabled=True,
        public_url="wss://voice.example.com",
        api_key="test-key",
        api_secret="test-secret",
        room_prefix="pa",
        token_ttl_seconds=300,
    )
    server._voice_context_resolvers = {"table": server._resolve_table_voice_context}
    server._voice_presence_by_user = {}
    return server


def _decode_jwt(token: str, secret: str) -> dict:
    header, payload, signature = token.split(".")
    expected = hmac.new(secret.encode("utf-8"), f"{header}.{payload}".encode("ascii"), hashlib.sha256).digest()
    actual = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
    assert hmac.compare_digest(expected, actual)
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))


def test_livekit_join_packet_contains_room_limited_grant() -> None:
    service = VoiceService(
        enabled=True,
        public_url="wss://voice.example.com",
        api_key="test-key",
        api_secret="test-secret",
        room_prefix="pa",
        token_ttl_seconds=300,
    )
    context = VoiceContext(scope="table", context_id="abc123", room_label="Test room")
    packet = service.create_join_packet(
        context=context,
        identity="uuid-alice",
        display_name="Alice",
    )

    claims = _decode_jwt(packet["token"], "test-secret")
    assert packet["type"] == "voice_join_info"
    assert packet["provider"] == "livekit"
    assert packet["scope"] == "table"
    assert packet["context_id"] == "abc123"
    assert packet["url"] == "wss://voice.example.com"
    assert packet["room"] == "pa:table:abc123"
    assert context.context_id == "abc123"
    assert claims["iss"] == "test-key"
    assert claims["sub"] == "uuid-alice"
    assert claims["name"] == "Alice"
    assert claims["video"]["roomJoin"] is True
    assert claims["video"]["room"] == "pa:table:abc123"
    assert claims["video"]["canPublish"] is True
    assert claims["video"]["canPublishSources"] == ["microphone"]
    assert claims["video"]["canSubscribe"] is True


@pytest.mark.asyncio
async def test_server_authorizes_voice_for_current_table_member() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users["Alice"] = alice
    table = server._tables.create_table("testgame", "Alice", alice)
    client = RecordingConnection()
    client.username = "Alice"

    await server._handle_voice_join(client, {"type": "voice_join", "scope": "table"})

    assert client.sent[0]["type"] == "voice_join_info"
    assert client.sent[0]["room"] == f"pa:table:{table.table_id}"
    assert client.sent[0]["context_id"] == table.table_id
    assert client.sent[0]["participant"]["identity"] == "uuid-alice"


@pytest.mark.asyncio
async def test_server_rejects_voice_for_non_member() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    bob = MockUser("Bob", uuid="uuid-bob")
    bob.connection = RecordingConnection()
    server._users["Bob"] = bob
    table = server._tables.create_table("testgame", "Alice", alice)
    client = RecordingConnection()
    client.username = "Bob"

    await server._handle_voice_join(
        client,
        {"type": "voice_join", "scope": "table", "context_id": table.table_id},
    )

    assert bob.connection.sent[0]["type"] == "voice_join_error"
    assert bob.connection.sent[0]["key"] == "voice-not-in-context"


@pytest.mark.asyncio
async def test_server_rejects_voice_when_user_has_no_table() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users["Alice"] = alice
    client = RecordingConnection()
    client.username = "Alice"

    await server._handle_voice_join(client, {"type": "voice_join", "scope": "table"})

    assert alice.connection.sent[0]["type"] == "voice_join_error"
    assert alice.connection.sent[0]["key"] == "voice-not-at-table"


@pytest.mark.asyncio
async def test_server_returns_clear_error_when_voice_service_unavailable() -> None:
    server = _make_server()
    server._voice = VoiceService(enabled=False)
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users["Alice"] = alice
    server._tables.create_table("testgame", "Alice", alice)
    client = RecordingConnection()
    client.username = "Alice"

    await server._handle_voice_join(client, {"type": "voice_join", "scope": "table"})

    assert alice.connection.sent[0]["type"] == "voice_join_error"
    assert alice.connection.sent[0]["key"] == "voice-unavailable"


@pytest.mark.asyncio
async def test_voice_presence_announces_connect_and_explicit_leave() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    bob = MockUser("Bob", uuid="uuid-bob")
    alice.connection = RecordingConnection()
    bob.connection = RecordingConnection()
    server._users["Alice"] = alice
    server._users["Bob"] = bob
    table = server._tables.create_table("testgame", "Alice", alice)
    table.add_member("Bob", bob)

    alice_client = RecordingConnection()
    alice_client.username = "Alice"

    await server._handle_voice_presence(
        alice_client,
        {"type": "voice_presence", "state": "connected", "scope": "table"},
    )

    assert "Alice connected" in bob.get_last_spoken()
    assert bob.get_sounds_played()[-1] == "voice_join.ogg"
    assert alice.get_sounds_played()[-1] == "voice_join.ogg"

    await server._handle_voice_leave(
        alice_client,
        {"type": "voice_leave", "scope": "table", "context_id": table.table_id},
    )

    assert alice_client.sent[-1]["type"] == "voice_leave_ack"
    assert "Alice disconnected" in bob.get_last_spoken()
    assert bob.get_sounds_played()[-1] == "voice_leave.ogg"
    assert alice.get_sounds_played()[-1] == "voice_leave.ogg"


@pytest.mark.asyncio
async def test_voice_presence_clears_when_member_leaves_table() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    bob = MockUser("Bob", uuid="uuid-bob")
    alice.connection = RecordingConnection()
    bob.connection = RecordingConnection()
    server._users["Alice"] = alice
    server._users["Bob"] = bob
    table = server._tables.create_table("testgame", "Alice", alice)
    table.add_member("Bob", bob)

    alice_client = RecordingConnection()
    alice_client.username = "Alice"

    await server._handle_voice_presence(
        alice_client,
        {"type": "voice_presence", "state": "connected", "scope": "table"},
    )
    bob.clear_messages()
    alice.connection.sent.clear()

    table.remove_member("Alice")
    await asyncio.sleep(0)

    assert "Alice left the table" in bob.get_last_spoken()
    assert bob.get_sounds_played()[-1] == "voice_leave.ogg"
    assert alice.connection.sent[-1]["type"] == "voice_context_closed"
    assert alice.connection.sent[-1]["scope"] == "table"
    assert alice.connection.sent[-1]["context_id"] == table.table_id


@pytest.mark.asyncio
async def test_table_removal_forces_voice_context_closed_even_without_presence() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users["Alice"] = alice
    table = server._tables.create_table("testgame", "Alice", alice)

    table.remove_member("Alice")
    await asyncio.sleep(0)

    assert alice.connection.sent[-1]["type"] == "voice_context_closed"
    assert alice.connection.sent[-1]["scope"] == "table"
    assert alice.connection.sent[-1]["context_id"] == table.table_id


@pytest.mark.asyncio
async def test_stale_voice_leave_does_not_clear_newer_presence() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    bob = MockUser("Bob", uuid="uuid-bob")
    alice.connection = RecordingConnection()
    bob.connection = RecordingConnection()
    server._users["Alice"] = alice
    server._users["Bob"] = bob
    table = server._tables.create_table("testgame", "Alice", alice)
    table.add_member("Bob", bob)
    alice_client = RecordingConnection()
    alice_client.username = "Alice"

    await server._handle_voice_presence(
        alice_client,
        {
            "type": "voice_presence",
            "state": "connected",
            "scope": "table",
            "context_id": table.table_id,
        },
    )
    bob.clear_messages()

    await server._handle_voice_leave(
        alice_client,
        {
            "type": "voice_leave",
            "scope": "table",
            "context_id": "stale-table-id",
        },
    )

    assert server._voice_presence_by_user["Alice"]["context_id"] == table.table_id
    assert bob.get_spoken_messages() == []
    assert alice_client.sent[-1]["type"] == "voice_leave_ack"
