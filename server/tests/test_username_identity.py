"""Regression tests for canonical, case-insensitive username identity."""

import logging
import sqlite3
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace

import pytest

from server.auth.auth import AuthManager
from server.persistence.database import Database
from server.tables.table import Table, TableMember
from server.users.identity import find_username_prefix, normalize_username, username_key


@pytest.fixture
def db():
    database = Database(":memory:")
    database.connect()
    yield database
    database.close()


def _insert_legacy_user(database: Database, username: str) -> None:
    database._conn.execute(
        """
        INSERT INTO users (
            username, username_key, password_hash, uuid, approved
        ) VALUES (?, ?, 'hash', ?, 1)
        """,
        (username, username_key(username), str(uuid.uuid4())),
    )
    database._conn.commit()


def test_resolve_user_returns_registered_spelling_for_case_variant(db):
    created = db.create_user("Trung", "hash")

    resolved = db.get_user("trung")

    assert created is not None
    assert resolved is not None
    assert resolved.uuid == created.uuid
    assert resolved.username == "Trung"


def test_resolution_is_unicode_normalized_and_case_insensitive(db):
    created = db.create_user("Đặng", "hash")

    resolved = db.get_user("đẶNG")

    assert created is not None
    assert resolved is not None
    assert resolved.uuid == created.uuid
    assert resolved.username == "Đặng"


def test_legacy_casefold_collision_requires_exact_registered_spelling(db):
    first = db.create_user("Straße", "hash")
    _insert_legacy_user(db, "STRASSE")

    assert first is not None
    assert db.get_user("Straße").username == "Straße"
    assert db.get_user("STRASSE").username == "STRASSE"
    assert db.get_user("strasse") is None
    assert db.resolve_user("strasse").ambiguous is True
    assert db.create_user("Strasse", "hash") is None


def test_exact_legacy_normalization_form_remains_resolvable(db):
    composed = db.create_user("Trúng", "hash")
    decomposed_name = "Tru\u0301ng"
    _insert_legacy_user(db, decomposed_name)
    decomposed = db.get_user(decomposed_name)

    assert composed is not None
    assert decomposed is not None
    assert decomposed.username == decomposed_name
    assert decomposed.uuid != composed.uuid
    assert db.resolve_user("TRÚNG").ambiguous is True


def test_case_variant_account_operations_use_canonical_identity(db):
    created = db.create_user("Trung", "hash")
    assert created is not None

    saved = db.save_user_table("trung", "Save", "bang", "{}", "[]")
    muted = db.mute_user("TRUNG", "Admin", "reason-spam", None)

    assert saved.username == "Trung"
    assert db.count_user_saved_tables("tRuNg") == 1
    assert muted.username == "Trung"
    assert db.get_active_mute("trung").username == "Trung"
    assert db.delete_user("trung") is True
    assert db.get_user("Trung") is None
    assert db.count_user_saved_tables("Trung") == 0


def test_auth_session_and_password_reset_use_resolved_canonical_account(db):
    auth = AuthManager(db)
    created = db.create_user("Trung", auth.hash_password("OldPassword1"))
    assert created is not None

    token = auth.create_session("trung")
    assert auth.validate_session(token) == "Trung"
    assert auth.reset_password("TRUNG", "NewPassword2") is True
    assert auth.authenticate("trung", "NewPassword2") is True


def test_deleting_exact_legacy_collision_does_not_delete_peer(db):
    first = db.create_user("Straße", "hash")
    _insert_legacy_user(db, "STRASSE")
    second = db.get_user("STRASSE")

    assert first is not None
    assert second is not None
    db.save_user_table("Straße", "First", "bang", "{}", "[]")
    db.save_user_table("STRASSE", "Second", "bang", "{}", "[]")
    db.mute_user("Straße", "Admin", "reason-spam", None)
    db.mute_user("STRASSE", "Admin", "reason-spam", None)
    db.add_notification(second.uuid, "Straße", "friend_removed")
    db.add_notification(second.uuid, "STRASSE", "friend_removed")

    assert db.delete_user("Straße") is True
    remaining = db.get_user("STRASSE")
    assert remaining is not None
    assert remaining.uuid == second.uuid
    assert db.count_user_saved_tables("STRASSE") == 1
    assert db.get_active_mute("STRASSE") is not None
    notifications = db.get_and_clear_notifications(second.uuid)
    assert [item["source_username"] for item in notifications] == ["STRASSE"]
    assert db._conn.execute(
        "SELECT 1 FROM users WHERE uuid = ?", (first.uuid,)
    ).fetchone() is None


def test_table_membership_never_merges_folded_legacy_accounts(db):
    first = db.create_user("Straße", "hash")
    _insert_legacy_user(db, "STRASSE")
    second = db.get_user("STRASSE")
    table = Table(
        table_id="identity-test",
        game_type="pig",
        host="Straße",
        members=[TableMember("Straße")],
    )
    table._db = db

    joined = table.add_member(
        "STRASSE",
        SimpleNamespace(uuid=second.uuid, username="STRASSE"),
    )

    assert first is not None
    assert second is not None
    assert joined is False
    assert [member.username for member in table.members] == ["Straße"]
    assert table._users == {}


def test_connect_backfills_lookup_keys_from_legacy_schema(tmp_path):
    path = tmp_path / "legacy.db"
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            uuid TEXT NOT NULL,
            locale TEXT DEFAULT 'en',
            preferences_json TEXT DEFAULT '{}',
            trust_level INTEGER DEFAULT 1,
            approved INTEGER DEFAULT 0,
            email TEXT DEFAULT '',
            bio TEXT DEFAULT '',
            motd_version INTEGER DEFAULT 0,
            gender TEXT DEFAULT 'Not set',
            registration_date TEXT DEFAULT '',
            last_login_date TEXT DEFAULT ''
        )
        """
    )
    connection.execute(
        "INSERT INTO users (username, password_hash, uuid) VALUES (?, ?, ?)",
        ("Trung", "hash", str(uuid.uuid4())),
    )
    connection.commit()
    connection.close()

    database = Database(str(path))
    database.connect()
    try:
        resolved = database.get_user("trung")
        key = database._conn.execute(
            "SELECT username_key FROM users WHERE username = 'Trung'"
        ).fetchone()["username_key"]
    finally:
        database.close()

    assert resolved is not None
    assert resolved.username == "Trung"
    assert key == "trung"

    connection = sqlite3.connect(path)
    connection.execute(
        "UPDATE users SET username_key = 'stale' WHERE username = 'Trung'"
    )
    connection.commit()
    connection.close()

    reopened = Database(str(path))
    reopened.connect()
    try:
        repaired = reopened.get_user("TRUNG")
        repaired_key = reopened._conn.execute(
            "SELECT username_key FROM users WHERE username = 'Trung'"
        ).fetchone()["username_key"]
    finally:
        reopened.close()

    assert repaired is not None
    assert repaired.username == "Trung"
    assert repaired_key == "trung"


def test_concurrent_connections_cannot_create_folded_collision(tmp_path):
    path = tmp_path / "concurrent.db"
    initial = Database(str(path))
    initial.connect()
    initial.close()
    barrier = Barrier(2)

    def create(username: str) -> bool:
        database = Database(str(path))
        database.connect(prune=False)
        try:
            barrier.wait(timeout=10)
            return database.create_user(username, "hash") is not None
        finally:
            database.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(create, ("Straße", "STRASSE")))

    check = Database(str(path))
    check.connect(prune=False)
    try:
        count = check.get_user_count()
    finally:
        check.close()

    assert sorted(results) == [False, True]
    assert count == 1


def test_concurrent_first_account_creation_promotes_exactly_one_user(tmp_path):
    path = tmp_path / "first-account.db"
    initial = Database(str(path))
    initial.connect()
    initial.close()
    barrier = Barrier(2)

    def create(username: str) -> int:
        database = Database(str(path))
        database.connect(prune=False)
        try:
            barrier.wait(timeout=10)
            record = database.create_user(
                username,
                "hash",
                approved=True,
                promote_first_user=True,
            )
            assert record is not None
            return record.trust_level
        finally:
            database.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        trust_levels = list(executor.map(create, ("Alice", "Bob")))

    assert sorted(trust_levels) == [1, 3]


def test_registration_is_not_poisoned_by_prior_write_statement(db):
    first = db.create_user("Alice", "hash")
    assert first is not None

    db._conn.execute(
        "UPDATE users SET bio = ? WHERE id = ?",
        ("updated", first.id),
    )

    assert db._conn.in_transaction is False
    assert db.create_user("Bob", "hash") is not None


def test_failed_atomic_write_rolls_back_and_registration_recovers(db):
    existing = Table(
        table_id="existing",
        game_type="pig",
        host="Alice",
        members=[TableMember("Alice")],
    )
    db.save_table(existing)
    invalid = Table(
        table_id="invalid",
        game_type="pig",
        host="Alice",
        members=[TableMember(object())],
    )

    with pytest.raises(TypeError):
        db.save_all_tables([invalid])

    assert db._conn.in_transaction is False
    assert db.load_table("existing") is not None
    assert db.create_user("Alice", "hash") is not None


def test_registration_lock_failure_logs_sqlite_cause_at_error_level(
    tmp_path,
    caplog,
):
    path = tmp_path / "locked-registration.db"
    database = Database(path)
    database.connect(prune=False, timeout=0.01)
    blocker = sqlite3.connect(path, timeout=0.01, isolation_level=None)
    blocker.execute("BEGIN IMMEDIATE")
    caplog.set_level(logging.ERROR, logger="playaural.db")

    try:
        assert database.create_user("Alice", "hash") is None
    finally:
        blocker.rollback()
        blocker.close()
        database.close()

    matching = [
        record
        for record in caplog.records
        if record.name == "playaural.db"
        and record.levelno == logging.ERROR
    ]
    assert len(matching) == 1
    assert matching[0].exc_info is not None
    assert "Operational error creating user 'Alice'" in matching[0].message
    assert "database is locked" in str(matching[0].exc_info[1])


def test_username_prefix_prefers_longest_unique_case_insensitive_match():
    assert find_username_prefix(
        "đẶng văn hello there",
        ["Đặng", "Đặng Văn", "Other"],
    ) == ("Đặng Văn", len("đẶng văn"))


def test_username_prefix_rejects_ambiguous_folded_match_but_accepts_exact():
    candidates = ["Straße", "STRASSE"]

    assert find_username_prefix("strasse hello", candidates) is None
    assert find_username_prefix("STRASSE hello", candidates) == (
        "STRASSE",
        len("STRASSE"),
    )
