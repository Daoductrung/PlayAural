import pytest

from ..auth.chat_rate_limit import ChatRateLimiter
from ..core import server as server_module
from ..core.server import MAX_CHAT_MESSAGE_LENGTH, Server
from ..messages.localization import Localization
from ..tables.manager import TableManager
from ..users.test_user import MockUser


class DummyClient:
    def __init__(self, username: str):
        self.username = username


class RecordingConnection:
    def __init__(self):
        self.sent: list[dict] = []

    async def send(self, packet: dict) -> None:
        self.sent.append(packet)


class MutatingConnection(RecordingConnection):
    def __init__(self, server: Server, username_to_remove: str):
        super().__init__()
        self.server = server
        self.username_to_remove = username_to_remove

    async def send(self, packet: dict) -> None:
        await super().send(packet)
        self.server._users.pop(self.username_to_remove, None)


class DummyDatabase:
    def get_active_mute(self, username: str):
        return None

    def get_socially_blocked_ids(self, user_id: str) -> set[str]:
        return set()


def _make_server() -> Server:
    server = Server.__new__(Server)
    server._db = DummyDatabase()
    server._chat_rate_limiter = ChatRateLimiter()
    server._tables = TableManager()
    server._user_states = {}
    server._users = {}
    return server


def _make_user(
    username: str,
    connection: RecordingConnection,
    *,
    locale: str = "en",
) -> MockUser:
    user = MockUser(username, locale=locale)
    user.connection = connection
    return user


@pytest.mark.asyncio
@pytest.mark.parametrize("convo", ["global", "local"])
async def test_chat_broadcast_snapshots_users_when_connection_changes_during_send(
    convo: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server()
    alice_connection = MutatingConnection(server, "Bob")
    bob_connection = RecordingConnection()
    cara_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    cara = _make_user("Cara", cara_connection)
    server._users = {
        "Alice": alice,
        "Bob": bob,
        "Cara": cara,
    }

    if convo == "global":
        monkeypatch.setattr(server_module, "GLOBAL_CHAT_SENDING_ENABLED", True)
    else:
        monkeypatch.setattr(
            server_module,
            "MAIN_MENU_LOCAL_CHAT_SENDING_ENABLED",
            True,
        )

    await server._handle_chat(
        DummyClient("Alice"),
        {
            "convo": convo,
            "message": "hello",
            "type": "chat",
        },
    )

    assert "Bob" not in server._users
    assert alice_connection.sent[0]["message"] == "hello"
    assert cara_connection.sent[0]["message"] == "hello"
    assert bob_connection.sent == []


@pytest.mark.asyncio
@pytest.mark.parametrize("locale", ["en", "vi"])
@pytest.mark.parametrize(
    ("convo", "message", "expected_key"),
    [
        ("local", "hello", "chat-main-menu-table-required-send"),
        ("global", "hello", "chat-global-temporarily-disabled-send"),
        ("global", "@Bob hello", "chat-global-temporarily-disabled-send"),
    ],
)
async def test_unavailable_chat_paths_return_localized_system_warning(
    locale: str,
    convo: str,
    message: str,
    expected_key: str,
) -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection, locale=locale)
    bob = _make_user("Bob", bob_connection)
    server._users = {"Alice": alice, "Bob": bob}

    await server._handle_chat(
        DummyClient("Alice"),
        {"convo": convo, "message": message, "type": "chat"},
    )

    assert alice_connection.sent == []
    assert bob_connection.sent == []
    assert alice.get_last_spoken() == Localization.get(
        alice.locale,
        expected_key,
    )
    assert alice.messages[-1].data["buffer"] == "system"


@pytest.mark.asyncio
async def test_table_local_chat_remains_available() -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    server._users = {"Alice": alice, "Bob": bob}
    table = server._tables.create_table("pig", "Alice", alice)
    assert table.add_member("Bob", bob)

    await server._handle_chat(
        DummyClient("Alice"),
        {"convo": "local", "message": "hello", "type": "chat"},
    )

    assert [packet["message"] for packet in alice_connection.sent] == ["hello"]
    assert [packet["message"] for packet in bob_connection.sent] == ["hello"]


@pytest.mark.asyncio
async def test_global_chat_mute_blocks_receiving_global_messages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(server_module, "GLOBAL_CHAT_SENDING_ENABLED", True)
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    bob.preferences.mute_global_chat = True
    server._users = {
        "Alice": alice,
        "Bob": bob,
    }

    await server._handle_chat(
        DummyClient("Alice"),
        {
            "convo": "global",
            "message": "hello",
            "type": "chat",
        },
    )

    assert alice_connection.sent[0]["message"] == "hello"
    assert bob_connection.sent == []


@pytest.mark.asyncio
async def test_table_chat_mute_blocks_receiving_local_messages() -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    bob.preferences.mute_table_chat = True
    server._users = {
        "Alice": alice,
        "Bob": bob,
    }
    table = server._tables.create_table("pig", "Alice", alice)
    assert table.add_member("Bob", bob)

    await server._handle_chat(
        DummyClient("Alice"),
        {
            "convo": "local",
            "message": "hello",
            "type": "chat",
        },
    )

    assert alice_connection.sent[0]["message"] == "hello"
    assert bob_connection.sent == []


@pytest.mark.asyncio
@pytest.mark.parametrize("message", ["hello", "@Bob hello"])
async def test_global_chat_mute_precedes_temporary_disable(message: str) -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    alice.preferences.mute_global_chat = True
    server._users = {
        "Alice": alice,
        "Bob": bob,
    }

    await server._handle_chat(
        DummyClient("Alice"),
        {
            "convo": "global",
            "message": message,
            "type": "chat",
        },
    )

    assert alice_connection.sent == []
    assert bob_connection.sent == []
    assert alice.get_last_spoken() == Localization.get(alice.locale, "chat-global-disabled-send")


@pytest.mark.asyncio
async def test_table_chat_mute_precedes_main_menu_disable() -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    alice.preferences.mute_table_chat = True
    server._users = {
        "Alice": alice,
        "Bob": bob,
    }

    await server._handle_chat(
        DummyClient("Alice"),
        {
            "convo": "local",
            "message": "hello",
            "type": "chat",
        },
    )

    assert alice_connection.sent == []
    assert bob_connection.sent == []
    assert alice.get_last_spoken() == Localization.get(alice.locale, "chat-table-disabled-send")


@pytest.mark.asyncio
@pytest.mark.parametrize("message", ["/stop", "/reboot", "/kick Bob"])
async def test_non_admin_slash_commands_do_not_broadcast_as_chat(message: str) -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    server._users = {
        "Alice": alice,
        "Bob": bob,
    }

    await server._handle_chat(
        DummyClient("Alice"),
        {
            "convo": "global",
            "message": message,
            "type": "chat",
        },
    )

    assert alice_connection.sent == []
    assert bob_connection.sent == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("packet", "expected_key"),
    [
        (
            {"convo": "forged", "message": "hello", "type": "chat"},
            "chat-invalid-channel",
        ),
        (
            {"convo": "global", "message": {"text": "hello"}, "type": "chat"},
            "chat-invalid-message",
        ),
        (
            {
                "convo": "global",
                "message": "x" * (MAX_CHAT_MESSAGE_LENGTH + 1),
                "type": "chat",
            },
            "chat-message-too-long",
        ),
    ],
)
async def test_forged_or_oversized_chat_packets_are_rejected(
    packet: dict, expected_key: str
) -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    server._users = {"Alice": alice, "Bob": bob}

    await server._handle_chat(DummyClient("Alice"), packet)

    assert alice_connection.sent == []
    assert bob_connection.sent == []
    assert alice.get_last_spoken() == Localization.get(
        alice.locale,
        expected_key,
        limit=MAX_CHAT_MESSAGE_LENGTH,
    )
