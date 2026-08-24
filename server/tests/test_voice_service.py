import asyncio
import base64
import hashlib
import hmac
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ..auth.voice_rate_limit import VoiceRateLimiter
# Import Server first: administration imports core.power through the core
# package, whose public initializer exposes Server.
from ..core.server import Server
from ..administration.manager import AdministrationManager
from ..messages.localization import Localization
from ..persistence.database import MuteRecord
from ..tables.manager import TableManager
from ..users.test_user import MockUser
from ..voice import VoiceContext, VoiceService


class RecordingConnection:
    def __init__(self):
        self.sent: list[dict] = []

    async def send(self, packet: dict) -> None:
        self.sent.append(packet)


class YieldingRecordingConnection(RecordingConnection):
    """Model a WebSocket whose write completes on a later loop turn."""

    async def send(self, packet: dict) -> None:
        await asyncio.sleep(0)
        self.sent.append(packet)


class DummyDb:
    def __init__(self):
        self.mutes: dict[str, MuteRecord] = {}
        self.users: dict[str, SimpleNamespace] = {}
        self.saved_tables: list[dict] = []

    def get_active_mute(self, username: str):
        return self.mutes.get(username)

    def unmute_user(self, username: str):
        return self.mutes.pop(username, None) is not None

    def mute_user(self, username: str, admin_username: str, reason: str, expires_at: str | None):
        record = MuteRecord(
            id=len(self.mutes) + 1,
            username=username,
            admin_username=admin_username,
            reason=reason,
            issued_at="now",
            expires_at=expires_at,
        )
        self.mutes[username] = record
        return record

    def get_user(self, username: str):
        return self.users.get(username)

    def save_user_table(
        self,
        *,
        username: str,
        save_name: str,
        game_type: str,
        game_json: str,
        members_json: str,
    ) -> None:
        self.saved_tables.append(
            {
                "username": username,
                "save_name": save_name,
                "game_type": game_type,
                "game_json": game_json,
                "members_json": members_json,
            }
        )


def _make_server() -> Server:
    # __file__-relative so the suite does not depend on the working directory
    # (every other test uses this form; a cwd-relative path here was the lone
    # reason the suite had to be run from the repo root).
    Localization.init(Path(__file__).resolve().parents[1] / "locales")
    Localization.preload_bundles()
    server = Server.__new__(Server)
    server._tables = TableManager()
    server._tables._server = server
    server._db = DummyDb()
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
    server._voice_join_authorizations_by_user = {}
    server._voice_rate_limiter = VoiceRateLimiter()
    server.admin_manager = AdministrationManager(server)
    return server


def _decode_jwt(token: str, secret: str) -> dict:
    header, payload, signature = token.split(".")
    expected = hmac.new(secret.encode("utf-8"), f"{header}.{payload}".encode("ascii"), hashlib.sha256).digest()
    actual = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
    assert hmac.compare_digest(expected, actual)
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))


def _authorize_voice_join(server: Server, username: str, context_id: str) -> None:
    server._record_voice_join_authorization(
        username,
        scope="table",
        context_id=context_id,
    )


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
async def test_server_rejects_muted_user_from_joining_voice() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users["Alice"] = alice
    server._db.users["Alice"] = SimpleNamespace(username="Alice", trust_level=1)
    server._db.mute_user("Alice", "Admin", "reason-spam", None)
    server._tables.create_table("testgame", "Alice", alice)
    client = RecordingConnection()
    client.username = "Alice"

    await server._handle_voice_join(client, {"type": "voice_join", "scope": "table"})

    assert alice.connection.sent[0]["type"] == "voice_join_error"
    assert alice.connection.sent[0]["key"] == "voice-muted-permanent"


@pytest.mark.asyncio
async def test_voice_presence_requires_recent_join_authorization() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    bob = MockUser("Bob", uuid="uuid-bob")
    alice.connection = RecordingConnection()
    bob.connection = YieldingRecordingConnection()
    server._users["Alice"] = alice
    server._users["Bob"] = bob
    table = server._tables.create_table("testgame", "Alice", alice)
    table.add_member("Bob", bob)
    alice_client = RecordingConnection()
    alice_client.username = "Alice"

    await server._handle_voice_presence(
        alice_client,
        {"type": "voice_presence", "state": "connected", "scope": "table", "context_id": table.table_id},
    )

    assert "Alice" not in server._voice_presence_by_user
    assert bob.get_spoken_messages() == []


@pytest.mark.asyncio
async def test_voice_join_requests_are_rate_limited() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    client = RecordingConnection()
    client.username = "Alice"
    alice.connection = client
    server._users["Alice"] = alice
    server._db.users["Alice"] = SimpleNamespace(username="Alice", trust_level=1)
    server._tables.create_table("testgame", "Alice", alice)

    saw_rate_limit = False
    for _ in range(8):
        await server._handle_voice_join(client, {"type": "voice_join", "scope": "table"})
        if client.sent[-1]["type"] == "voice_join_error":
            saw_rate_limit = True
            break

    assert saw_rate_limit is True
    assert client.sent[-1]["key"] == "voice-rate-limited"


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
    _authorize_voice_join(server, "Alice", table.table_id)

    await server._handle_voice_presence(
        alice_client,
        {
            "type": "voice_presence",
            "state": "connected",
            "scope": "table",
            "context_id": table.table_id,
        },
    )
    await asyncio.sleep(0)

    assert "Alice connected" in bob.get_last_spoken()
    assert bob.get_sounds_played()[-1] == "voice_join.ogg"
    assert alice.get_sounds_played()[-1] == "voice_join.ogg"

    await server._handle_voice_leave(
        alice_client,
        {"type": "voice_leave", "scope": "table", "context_id": table.table_id},
    )
    await asyncio.sleep(0)

    assert alice_client.sent[-1]["type"] == "voice_leave_ack"
    assert "Alice disconnected" in bob.get_last_spoken()
    assert bob.get_sounds_played()[-1] == "voice_leave.ogg"
    assert alice.get_sounds_played()[-1] == "voice_leave.ogg"


@pytest.mark.asyncio
async def test_voice_cues_batch_same_turn_but_not_separate_turns() -> None:
    server = _make_server()
    users = [
        MockUser("Alice", uuid="uuid-alice"),
        MockUser("Bob", uuid="uuid-bob"),
        MockUser("Carol", uuid="uuid-carol"),
    ]
    for user in users:
        user.connection = RecordingConnection()
        server._users[user.username] = user
    table = server._tables.create_table("testgame", "Alice", users[0])
    table.add_member("Bob", users[1])
    table.add_member("Carol", users[2])

    clients: list[RecordingConnection] = []
    for user in users[:2]:
        client = RecordingConnection()
        client.username = user.username
        clients.append(client)
        _authorize_voice_join(server, user.username, table.table_id)
        await server._handle_voice_presence(
            client,
            {
                "type": "voice_presence",
                "state": "connected",
                "scope": "table",
                "context_id": table.table_id,
            },
        )

    await asyncio.sleep(0)
    for user in users:
        assert user.get_sounds_played().count("voice_join.ogg") == 1
        assert len(user.get_spoken_messages()) == 2
        user.clear_messages()

    await server._handle_voice_leave(
        clients[0],
        {
            "type": "voice_leave",
            "scope": "table",
            "context_id": table.table_id,
        },
    )
    await asyncio.sleep(0)
    await server._handle_voice_leave(
        clients[1],
        {
            "type": "voice_leave",
            "scope": "table",
            "context_id": table.table_id,
        },
    )
    await asyncio.sleep(0)

    for user in users:
        assert user.get_sounds_played().count("voice_leave.ogg") == 2


@pytest.mark.asyncio
async def test_server_can_request_listen_only_voice_join_and_cancel_it() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users[alice.username] = alice
    table = server._tables.create_table("testgame", alice.username, alice)

    assert await server.force_voice_context_join(
        alice.username,
        context_id=table.table_id,
    )
    join_packet = alice.connection.sent[-1]
    assert join_packet["type"] == "voice_join_info"
    assert join_packet["server_requested"] is True
    assert join_packet["context_id"] == table.table_id
    assert server._voice_join_authorizations_by_user[alice.username][
        "context_id"
    ] == table.table_id

    assert await server.force_voice_context_leave(
        alice.username,
        scope="table",
        context_id=table.table_id,
    )
    assert alice.username not in server._voice_join_authorizations_by_user
    assert alice.connection.sent[-1] == {
        "type": "voice_context_closed",
        "scope": "table",
        "context_id": table.table_id,
    }


@pytest.mark.asyncio
async def test_stale_forced_voice_close_does_not_clear_newer_presence() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users[alice.username] = alice
    server._voice_presence_by_user[alice.username] = {
        "scope": "table",
        "context_id": "new-table",
    }

    assert await server.force_voice_context_leave(
        alice.username,
        scope="table",
        context_id="old-table",
    )

    assert server._voice_presence_by_user[alice.username][
        "context_id"
    ] == "new-table"
    assert alice.connection.sent[-1]["context_id"] == "old-table"


@pytest.mark.asyncio
async def test_unscoped_forced_voice_close_revokes_pending_and_active_contexts() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users[alice.username] = alice
    server._voice_presence_by_user[alice.username] = {
        "scope": "table",
        "context_id": "active-table",
    }
    _authorize_voice_join(server, alice.username, "pending-table")

    assert await server.force_voice_context_leave(alice.username)

    assert alice.username not in server._voice_presence_by_user
    assert alice.username not in server._voice_join_authorizations_by_user
    assert alice.connection.sent[-1]["context_id"] == "active-table"


@pytest.mark.asyncio
async def test_contextless_client_voice_teardown_cannot_clear_current_room() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users[alice.username] = alice
    table = server._tables.create_table("testgame", alice.username, alice)
    server._voice_presence_by_user[alice.username] = {
        "scope": "table",
        "context_id": table.table_id,
    }
    _authorize_voice_join(server, alice.username, table.table_id)
    client = RecordingConnection()
    client.username = alice.username

    await server._handle_voice_leave(
        client,
        {"type": "voice_leave", "scope": "table"},
    )
    await server._handle_voice_presence(
        client,
        {
            "type": "voice_presence",
            "state": "connection_lost",
            "scope": "table",
        },
    )

    assert server._voice_presence_by_user[alice.username]["context_id"] == table.table_id
    assert server._voice_join_authorizations_by_user[alice.username][
        "context_id"
    ] == table.table_id
    assert client.sent == [{"type": "voice_leave_ack"}]


@pytest.mark.asyncio
async def test_same_context_reauthorization_cancels_scheduled_stale_close() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    bob = MockUser("Bob", uuid="uuid-bob")
    alice.connection = RecordingConnection()
    bob.connection = RecordingConnection()
    server._users[alice.username] = alice
    server._users[bob.username] = bob
    table = server._tables.create_table("testgame", alice.username, alice)
    table.add_member(bob.username, bob)
    server._voice_presence_by_user[alice.username] = {
        "scope": "table",
        "context_id": table.table_id,
    }

    table.remove_member(alice.username)
    assert table.add_member(alice.username, alice)
    assert await server.force_voice_context_join(
        alice.username,
        context_id=table.table_id,
    )
    await asyncio.sleep(0)

    assert server._voice_presence_by_user[alice.username][
        "context_id"
    ] == table.table_id
    assert not any(
        packet["type"] == "voice_context_closed"
        for packet in alice.connection.sent
    )
    assert server._pending_voice_context_closures == {}


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
    _authorize_voice_join(server, "Alice", table.table_id)

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
    alice.connection.sent.clear()

    table.remove_member("Alice")
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert "Alice left the table" in bob.get_last_spoken()
    assert bob.get_sounds_played()[-1] == "voice_leave.ogg"
    assert alice.connection.sent[-1]["type"] == "voice_context_closed"
    assert alice.connection.sent[-1]["scope"] == "table"
    assert alice.connection.sent[-1]["context_id"] == table.table_id


@pytest.mark.asyncio
async def test_muting_connected_user_forces_voice_chat_exit() -> None:
    server = _make_server()
    admin = MockUser("Admin", uuid="uuid-admin")
    admin.connection = RecordingConnection()
    admin.trust_level = 2
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    bob = MockUser("Bob", uuid="uuid-bob")
    bob.connection = RecordingConnection()
    server._users["Admin"] = admin
    server._users["Alice"] = alice
    server._users["Bob"] = bob
    server._db.users["Admin"] = SimpleNamespace(username="Admin", trust_level=2)
    server._db.users["Alice"] = SimpleNamespace(username="Alice", trust_level=1)
    table = server._tables.create_table("testgame", "Alice", alice)
    table.add_member("Bob", bob)

    alice_client = RecordingConnection()
    alice_client.username = "Alice"
    await server._handle_voice_join(alice_client, {"type": "voice_join", "scope": "table"})
    await server._handle_voice_presence(
        alice_client,
        {"type": "voice_presence", "state": "connected", "scope": "table", "context_id": table.table_id},
    )
    bob.clear_messages()
    alice.connection.sent.clear()

    await server.admin_manager._perform_mute(admin, "Alice", "5m", "reason-spam")

    assert "Alice" not in server._voice_presence_by_user
    assert alice.connection.sent[-1]["type"] == "voice_context_closed"
    assert alice.connection.sent[-1]["context_id"] == table.table_id
    assert "Alice disconnected" in bob.get_last_spoken()


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
async def test_save_and_close_clears_voice_presence_and_notifies_client() -> None:
    class FakeGame:
        def __init__(self, table):
            self.table = table
            self.players = [
                SimpleNamespace(name="Alice", is_bot=False, is_spectator=False),
                SimpleNamespace(name="Bob", is_bot=False, is_spectator=False),
            ]

        def to_json(self) -> str:
            return "{}"

        def get_name(self) -> str:
            return "Test Game"

        def broadcast_l(self, *args, **kwargs) -> None:
            return None

        def destroy(self) -> None:
            self._destroyed = True
            self.table.destroy()

    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    bob = MockUser("Bob", uuid="uuid-bob")
    alice.connection = RecordingConnection()
    bob.connection = RecordingConnection()
    server._users["Alice"] = alice
    server._users["Bob"] = bob
    server._db.users["Alice"] = SimpleNamespace(
        username="Alice",
        trust_level=1,
        locale="en",
    )
    table = server._tables.create_table("testgame", "Alice", alice)
    table.add_member("Bob", bob)
    table.game = FakeGame(table)

    for voice_user in (alice, bob):
        voice_client = RecordingConnection()
        voice_client.username = voice_user.username
        _authorize_voice_join(server, voice_user.username, table.table_id)
        await server._handle_voice_presence(
            voice_client,
            {
                "type": "voice_presence",
                "state": "connected",
                "scope": "table",
                "context_id": table.table_id,
            },
        )
    await asyncio.sleep(0)
    for voice_user in (alice, bob):
        voice_user.clear_messages()
        voice_user.connection.sent.clear()

    table.save_and_close("Alice")
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert server._db.saved_tables[-1]["username"] == "Alice"
    assert "Alice" not in server._voice_presence_by_user
    assert "Bob" not in server._voice_presence_by_user
    for voice_user in (alice, bob):
        closed_packets = [
            packet
            for packet in voice_user.connection.sent
            if packet["type"] == "voice_context_closed"
        ]
        assert closed_packets == [
            {
                "type": "voice_context_closed",
                "scope": "table",
                "context_id": table.table_id,
            }
        ]
        assert voice_user.get_sounds_played().count("voice_leave.ogg") == 1
        assert any(
            "left the table" in message
            for message in voice_user.get_spoken_messages()
        )


@pytest.mark.asyncio
async def test_show_main_menu_forces_voice_cleanup_if_session_is_stale() -> None:
    server = _make_server()
    alice = MockUser("Alice", uuid="uuid-alice")
    alice.connection = RecordingConnection()
    server._users["Alice"] = alice
    server._voice_presence_by_user["Alice"] = {
        "scope": "table",
        "context_id": "stale-table",
    }

    server._show_main_menu(alice)
    await asyncio.sleep(0)

    assert "Alice" not in server._voice_presence_by_user
    assert alice.connection.sent[-1]["type"] == "voice_context_closed"
    assert alice.connection.sent[-1]["context_id"] == "stale-table"


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
    _authorize_voice_join(server, "Alice", table.table_id)

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
