import pytest

from ..auth.chat_rate_limit import ChatRateLimiter
from ..core import server as server_module
from ..core.server import MAX_CHAT_MESSAGE_LENGTH, Server
from ..messages.localization import Localization
from ..persistence.database import GlobalChatMessageRecord
from ..moderation.reports import ModerationReportSubmission
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
    def __init__(self):
        self.global_messages: list[GlobalChatMessageRecord] = []
        self.automated_reports: list[dict] = []
        self.fail_global_message_write = False

    def get_active_mute(self, username: str):
        return None

    def get_socially_blocked_ids(self, user_id: str) -> set[str]:
        return set()

    def add_global_chat_message(
        self,
        sender_uuid: str,
        sender_username: str,
        channel_code: str,
        message: str,
    ) -> GlobalChatMessageRecord:
        if self.fail_global_message_write:
            raise RuntimeError("simulated database failure")
        record = GlobalChatMessageRecord(
            id=len(self.global_messages) + 1,
            sender_uuid=sender_uuid,
            sender_username=sender_username,
            channel_code=channel_code,
            sent_at_utc="2026-09-25T12:00:00.000000+00:00",
            message=message,
        )
        self.global_messages.append(record)
        return record

    def submit_automated_spam_report(self, **kwargs) -> ModerationReportSubmission:
        self.automated_reports.append(kwargs)
        return ModerationReportSubmission(
            outcome="created",
            report_id=len(self.automated_reports),
        )


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
        for user in (alice, bob, cara):
            user.preferences.global_chat_channel = "en"
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
    if convo == "global":
        alice.preferences.global_chat_channel = "en"
        server._global_chat_sending_enabled = False
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
@pytest.mark.parametrize(
    "convo",
    [
        "global",
        "local",
    ],
)
async def test_unavailable_chat_attempts_do_not_consume_send_capacity(
    convo: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    alice.preferences.global_chat_channel = "en"
    bob.preferences.global_chat_channel = "en"
    server._users = {"Alice": alice, "Bob": bob}
    if convo == "global":
        server._global_chat_sending_enabled = False
    else:
        monkeypatch.setattr(
            server_module,
            "MAIN_MENU_LOCAL_CHAT_SENDING_ENABLED",
            False,
        )

    for index in range(server._chat_rate_limiter.GLOBAL_POLICY.capacity + 3):
        await server._handle_chat(
            DummyClient("Alice"),
            {"convo": convo, "message": f"blocked {index}", "type": "chat"},
        )

    assert all(
        key[0] != alice.uuid for key in server._chat_rate_limiter._buckets
    )

    if convo == "global":
        server._global_chat_sending_enabled = True
    else:
        monkeypatch.setattr(
            server_module,
            "MAIN_MENU_LOCAL_CHAT_SENDING_ENABLED",
            True,
        )
    await server._handle_chat(
        DummyClient("Alice"),
        {"convo": convo, "message": "now available", "type": "chat"},
    )

    assert [packet["message"] for packet in alice_connection.sent] == [
        "now available"
    ]
    assert [packet["message"] for packet in bob_connection.sent] == [
        "now available"
    ]


@pytest.mark.asyncio
async def test_repeated_global_message_is_not_logged_or_delivered() -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    alice.preferences.global_chat_channel = "en"
    bob.preferences.global_chat_channel = "en"
    server._users = {"Alice": alice, "Bob": bob}

    for message in ("Hello\u200b world", "  HELLO   WORLD", "hello world"):
        await server._handle_chat(
            DummyClient("Alice"),
            {"convo": "global", "message": message, "type": "chat"},
        )

    assert [packet["message"] for packet in bob_connection.sent] == [
        "Hello\u200b world",
        "HELLO   WORLD",
    ]
    assert [record.message for record in server._db.global_messages] == [
        "Hello\u200b world",
        "HELLO   WORLD",
    ]
    assert alice.get_last_spoken() == Localization.get(
        alice.locale,
        "chat-repeated-message",
    )
    assert alice.messages[-1].data["buffer"] == "system"


@pytest.mark.asyncio
async def test_repeated_global_spam_creates_one_system_report_and_staff_alert(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = 1_000.0
    monkeypatch.setattr("server.auth.chat_rate_limit.time.monotonic", lambda: clock)
    server = _make_server()
    alice_connection = RecordingConnection()
    admin_connection = RecordingConnection()
    developer_connection = RecordingConnection()
    player_connection = RecordingConnection()
    pending_admin_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    admin = _make_user("Admin", admin_connection)
    developer = _make_user("Developer", developer_connection)
    player = _make_user("Player", player_connection)
    pending_admin = MockUser("Pending Admin", approved=False)
    pending_admin.connection = pending_admin_connection
    admin.trust_level = 2
    developer.trust_level = 3
    pending_admin.trust_level = 2
    alice.preferences.global_chat_channel = "en"
    server._users = {
        "Alice": alice,
        "Admin": admin,
        "Developer": developer,
        "Player": player,
        "Pending Admin": pending_admin,
    }
    bucket = server._chat_rate_limiter.get_bucket(alice.uuid, "global")
    bucket.recent_messages = [(999.0, "flood"), (999.0, "flood")]

    for incident in range(3):
        clock = 1_000.0 + incident * 10.0
        await server._handle_chat(
            DummyClient("Alice"),
            {
                "convo": "global",
                "message": "flood",
                "type": "chat",
            },
        )

    assert len(server._db.automated_reports) == 1
    report = server._db.automated_reports[0]
    assert report["reported_uuid"] == alice.uuid
    assert report["reported_username"] == "Alice"
    assert report["channel_code"] == "en"
    assert report["evidence"].scope == "global"
    assert report["evidence"].incident_count == 3
    assert admin.get_last_spoken() == Localization.get(
        admin.locale,
        "admin-new-automatic-report",
        id=1,
        target="Alice",
    )
    assert developer.get_last_spoken() == Localization.get(
        developer.locale,
        "admin-new-automatic-report",
        id=1,
        target="Alice",
    )
    assert player.get_spoken_messages() == []
    assert pending_admin.get_spoken_messages() == []
    assert admin.get_sounds_played() == ["moderation_report.ogg"]
    assert developer.get_sounds_played() == ["moderation_report.ogg"]
    assert all(
        message.data.get("buffer") == "system"
        for message in admin.messages
        if message.type == "play_sound"
    )

    clock = 1_030.0
    await server._handle_chat(
        DummyClient("Alice"),
        {"convo": "global", "message": "flood", "type": "chat"},
    )
    assert len(server._db.automated_reports) == 1
    assert admin.get_sounds_played() == ["moderation_report.ogg"]


@pytest.mark.asyncio
async def test_message_with_no_visible_content_is_rejected_before_rate_limit() -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    server._users = {"Alice": alice}

    await server._handle_chat(
        DummyClient("Alice"),
        {"convo": "local", "message": "\u200b\u2060", "type": "chat"},
    )

    assert alice_connection.sent == []
    assert all(
        key[0] != alice.uuid for key in server._chat_rate_limiter._buckets
    )
    assert alice.get_last_spoken() == Localization.get(
        alice.locale,
        "chat-invalid-message",
    )


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
    assert server._db.global_messages == []


@pytest.mark.asyncio
async def test_global_chat_mute_blocks_receiving_global_messages() -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    alice.preferences.global_chat_channel = "en"
    bob.preferences.global_chat_channel = "en"
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
@pytest.mark.parametrize("locale", ["en", "vi"])
@pytest.mark.parametrize("message", ["hello", "@Bob hello"])
async def test_global_chat_requires_an_explicit_language_channel(
    locale: str,
    message: str,
) -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection, locale=locale)
    bob = _make_user("Bob", bob_connection)
    bob.preferences.global_chat_channel = "en"
    server._users = {"Alice": alice, "Bob": bob}

    await server._handle_chat(
        DummyClient("Alice"),
        {"convo": "global", "message": message, "type": "chat"},
    )

    assert alice_connection.sent == []
    assert bob_connection.sent == []
    assert alice.get_last_spoken() == Localization.get(
        locale,
        "chat-global-channel-required-send",
    )
    assert alice.messages[-1].data["buffer"] == "system"


@pytest.mark.asyncio
async def test_missing_channel_precedes_temporary_global_disable() -> None:
    server = _make_server()
    server._global_chat_sending_enabled = False
    alice_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    server._users = {"Alice": alice}

    await server._handle_chat(
        DummyClient("Alice"),
        {"convo": "global", "message": "hello", "type": "chat"},
    )

    assert alice_connection.sent == []
    assert alice.get_last_spoken() == Localization.get(
        alice.locale,
        "chat-global-channel-required-send",
    )


@pytest.mark.asyncio
async def test_global_chat_is_delivered_only_within_the_selected_channel() -> None:
    server = _make_server()
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    cara_connection = RecordingConnection()
    dan_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    cara = _make_user("Cara", cara_connection)
    dan = _make_user("Dan", dan_connection)
    alice.preferences.global_chat_channel = "es"
    bob.preferences.global_chat_channel = "es"
    cara.preferences.global_chat_channel = "en"
    server._users = {
        "Alice": alice,
        "Bob": bob,
        "Cara": cara,
        "Dan": dan,
    }

    await server._handle_chat(
        DummyClient("Alice"),
        {"convo": "global", "message": "hola", "type": "chat"},
    )

    assert [packet["message"] for packet in alice_connection.sent] == ["hola"]
    assert [packet["message"] for packet in bob_connection.sent] == ["hola"]
    assert cara_connection.sent == []
    assert dan_connection.sent == []
    assert server._db.global_messages == [
        GlobalChatMessageRecord(
            id=1,
            sender_uuid=alice.uuid,
            sender_username="Alice",
            channel_code="es",
            sent_at_utc="2026-09-25T12:00:00.000000+00:00",
            message="hola",
        )
    ]
    assert alice_connection.sent[0]["message_id"] == 1
    assert alice_connection.sent[0]["channel"] == "es"
    assert alice_connection.sent[0]["sent_at"].endswith("+00:00")


@pytest.mark.asyncio
async def test_global_chat_fails_closed_when_message_cannot_be_persisted() -> None:
    server = _make_server()
    server._db.fail_global_message_write = True
    alice_connection = RecordingConnection()
    bob_connection = RecordingConnection()
    alice = _make_user("Alice", alice_connection)
    bob = _make_user("Bob", bob_connection)
    alice.preferences.global_chat_channel = "en"
    bob.preferences.global_chat_channel = "en"
    server._users = {"Alice": alice, "Bob": bob}

    await server._handle_chat(
        DummyClient("Alice"),
        {"convo": "global", "message": "hello", "type": "chat"},
    )

    assert alice_connection.sent == []
    assert bob_connection.sent == []
    assert alice.get_last_spoken() == Localization.get(
        alice.locale,
        "chat-global-log-unavailable",
    )


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
    server._global_chat_sending_enabled = False
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
