from datetime import datetime, timedelta, timezone

import pytest

from ..chat_channels import MAX_CHAT_MESSAGE_LENGTH
from ..core.server import Server
from ..persistence.database import Database


def test_boolean_server_setting_defaults_and_persists_across_restart(tmp_path) -> None:
    path = tmp_path / "server_settings.sqlite"
    database = Database(path)
    database.connect()
    try:
        assert database.get_boolean_server_setting(
            "global_chat_enabled",
            default=True,
        ) is True
        database.set_boolean_server_setting("global_chat_enabled", False)
    finally:
        database.close()

    reopened = Database(path)
    reopened.connect()
    try:
        assert reopened.get_boolean_server_setting(
            "global_chat_enabled",
            default=True,
        ) is False
    finally:
        reopened.close()


def test_invalid_persisted_global_chat_setting_fails_closed(tmp_path) -> None:
    server = Server(db_path=tmp_path / "invalid_server_setting.sqlite")
    server._db.connect()
    try:
        server._db._conn.execute(
            """
            INSERT INTO server_settings (
                setting_key, value_json, updated_at_utc
            ) VALUES (?, ?, ?)
            """,
            ("global_chat_enabled", '"invalid"', "2026-09-25T00:00:00+00:00"),
        )

        server._load_persistent_server_settings()

        assert server.global_chat_sending_enabled is False
    finally:
        server._db.close()


def _connected_database(path) -> Database:
    database = Database(path)
    database.connect()
    return database


def test_global_chat_message_persists_across_restart_and_startup_pruning(
    tmp_path,
) -> None:
    path = tmp_path / "global_chat.sqlite"
    database = _connected_database(path)
    sender = database.create_user("Người Gửi", "hash")
    record = database.add_global_chat_message(
        sender.uuid,
        sender.username,
        "vi-VN",
        "Xin chào 👋",
    )
    old_timestamp = (datetime.now(timezone.utc) - timedelta(days=730)).isoformat()
    database._conn.execute(
        "UPDATE global_chat_messages SET sent_at_utc = ? WHERE id = ?",
        (old_timestamp, record.id),
    )
    database.close()

    reopened = _connected_database(path)
    try:
        retained = reopened.get_global_chat_message(record.id)
        assert retained is not None
        assert retained.sender_uuid == sender.uuid
        assert retained.sender_username == "Người Gửi"
        assert retained.channel_code == "vi"
        assert retained.sent_at_utc == old_timestamp
        assert retained.message == "Xin chào 👋"
        assert reopened.count_global_chat_messages() == 1
    finally:
        reopened.close()


def test_account_deletion_keeps_global_chat_identity_snapshot(tmp_path) -> None:
    database = _connected_database(tmp_path / "account_delete.sqlite")
    try:
        sender = database.create_user("Former User", "hash")
        record = database.add_global_chat_message(
            sender.uuid,
            sender.username,
            "en",
            "Retained evidence",
        )

        assert database.delete_user(sender.username)

        retained = database.get_global_chat_message(record.id)
        assert retained is not None
        assert retained.sender_uuid == sender.uuid
        assert retained.sender_username == sender.username
        assert retained.message == "Retained evidence"
    finally:
        database.close()


def test_global_chat_message_uses_utc_timestamp_and_indexed_filters(
    tmp_path,
) -> None:
    database = _connected_database(tmp_path / "filters.sqlite")
    try:
        alice = database.create_user("Alice", "hash")
        bob = database.create_user("Bob", "hash")
        first = database.add_global_chat_message(
            alice.uuid,
            alice.username,
            "es",
            "hola",
        )
        database.add_global_chat_message(
            bob.uuid,
            bob.username,
            "en",
            "hello",
        )

        parsed = datetime.fromisoformat(first.sent_at_utc)
        assert parsed.utcoffset() == timedelta(0)
        assert database.count_global_chat_messages(sender_uuid=alice.uuid) == 1
        assert database.count_global_chat_messages(channel_code="es-MX") == 1
        assert database.count_global_chat_messages(channel_code="en") == 1
    finally:
        database.close()


@pytest.mark.parametrize(
    ("sender_uuid", "username", "channel", "message"),
    [
        ("", "Alice", "en", "hello"),
        ("user-id", "", "en", "hello"),
        ("user-id", "Alice", "unknown", "hello"),
        ("user-id", "Alice", "en", ""),
        ("user-id", "Alice", "en", " hello"),
        ("user-id", "Alice", "en", "x" * (MAX_CHAT_MESSAGE_LENGTH + 1)),
    ],
)
def test_global_chat_persistence_rejects_noncanonical_records(
    tmp_path,
    sender_uuid: str,
    username: str,
    channel: str,
    message: str,
) -> None:
    database = _connected_database(tmp_path / "invalid.sqlite")
    try:
        with pytest.raises(ValueError):
            database.add_global_chat_message(
                sender_uuid,
                username,
                channel,
                message,
            )
        assert database.count_global_chat_messages() == 0
    finally:
        database.close()
