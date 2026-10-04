import datetime
import errno
import json
import os
import sqlite3
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest

from server.persistence.database import (
    Database,
    DatabaseCleanupCategoryCode,
)
from server.persistence.retention import (
    ABANDONED_DATABASE_FRAGMENT_MINIMUM_AGE_SECONDS,
)


def _mark_backup_fragment_abandoned(path: Path) -> None:
    old_timestamp = (
        datetime.datetime.now().timestamp()
        - ABANDONED_DATABASE_FRAGMENT_MINIMUM_AGE_SECONDS
        - 1
    )
    os.utime(path, (old_timestamp, old_timestamp))

@pytest.fixture
def db():
    """In-memory database for testing."""
    database = Database(":memory:")
    database.connect()
    yield database
    database.close()

def test_storage_cleanup_is_allowlisted_and_preserves_excluded_data(db, tmp_path):
    cursor = db._conn.cursor()
    reference = datetime.datetime(2026, 9, 26, 12, 0, 0)
    recent = reference - timedelta(days=10)
    stale = reference - timedelta(days=200)
    old_game = reference - timedelta(days=400)
    future = reference + timedelta(days=10)

    users = {
        name: db.create_user(name, "hash")
        for name in (
            "mute_active",
            "mute_expired",
            "social_a",
            "social_b",
            "social_c",
        )
    }

    # Historical game results and saved tables are user data, not garbage.
    cursor.execute(
        "INSERT INTO game_results "
        "(game_type, timestamp, duration_ticks, custom_data) VALUES (?, ?, ?, ?)",
        ("pig", old_game.isoformat(), 100, "{}"),
    )
    old_game_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO game_result_players "
        "(result_id, player_id, player_name, is_bot) VALUES (?, 'u1', 'p1', 0)",
        (old_game_id,),
    )
    cursor.execute(
        "INSERT INTO saved_tables "
        "(username, save_name, game_type, game_json, members_json, saved_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("social_a", "Very Old Save", "pig", "{}", "[]", old_game.isoformat()),
    )
    message = db.add_global_chat_message(
        users["social_a"].uuid,
        "social_a",
        "en",
        "retained evidence",
    )
    cursor.execute(
        """
        INSERT INTO moderation_reports (
            reporter_uuid, reporter_username, reported_uuid, reported_username,
            reported_at_utc, reason_code, details, channel_code,
            context_anchor_message_id, status, origin_code, context_code
        ) VALUES (?, ?, ?, ?, ?, 'spam', '', 'en', ?, 'open', 'manual', 'global')
        """,
        (
            users["social_b"].uuid,
            "social_b",
            users["social_a"].uuid,
            "social_a",
            old_game.isoformat(),
            message.id,
        ),
    )

    # Every allowlisted category gets one independent candidate.
    cursor.execute(
        """
        INSERT INTO tables (
            table_id, game_type, host, members_json, game_json,
            checkpoint_created_at, checkpoint_expires_at
        ) VALUES ('expired', 'pig', 'social_a', '[]', '{}', ?, ?)
        """,
        ((reference - timedelta(days=2)).isoformat(), recent.isoformat()),
    )
    cursor.execute(
        """
        INSERT INTO tables (
            table_id, game_type, host, members_json, game_json,
            checkpoint_created_at, checkpoint_expires_at
        ) VALUES ('active', 'pig', 'social_a', '[]', '{}', ?, ?)
        """,
        ((reference - timedelta(days=2)).isoformat(), future.isoformat()),
    )
    cursor.execute(
        "INSERT INTO password_reset_tokens "
        "(user_uuid, token_hash, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (users["social_a"].uuid, "expired", stale.isoformat(), recent.isoformat()),
    )
    cursor.execute(
        "INSERT INTO password_reset_tokens "
        "(user_uuid, token_hash, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (users["social_b"].uuid, "malformed", recent.isoformat(), "not-a-date"),
    )
    cursor.execute(
        "INSERT INTO bans "
        "(username, admin_username, reason_key, issued_at, expires_at) "
        "VALUES (?, 'admin', 'reason', ?, ?)",
        ("recent_ban", old_game.isoformat(), recent.isoformat()),
    )
    cursor.execute(
        "INSERT INTO bans "
        "(username, admin_username, reason_key, issued_at, expires_at) "
        "VALUES (?, 'admin', 'reason', ?, ?)",
        ("old_ban", old_game.isoformat(), (reference - timedelta(days=40)).isoformat()),
    )
    cursor.execute(
        "INSERT INTO friendships VALUES (?, ?, 'accepted', ?)",
        (users["social_a"].uuid, users["social_b"].uuid, recent.isoformat()),
    )
    cursor.execute(
        "INSERT INTO friendships VALUES (?, ?, 'pending', ?)",
        (users["social_b"].uuid, users["social_c"].uuid, stale.isoformat()),
    )
    cursor.execute(
        "INSERT INTO friendships VALUES (?, ?, 'accepted', ?)",
        ("missing-friend", users["social_c"].uuid, recent.isoformat()),
    )
    cursor.execute(
        "INSERT INTO user_blocks VALUES (?, ?, ?)",
        (users["social_a"].uuid, users["social_b"].uuid, recent.isoformat()),
    )
    cursor.execute(
        "INSERT INTO user_blocks (blocker_id, blocked_id, created_at) VALUES (?, ?, ?)",
        ("missing-blocker", users["social_c"].uuid, recent.isoformat()),
    )
    cursor.execute(
        "INSERT INTO user_notifications VALUES (NULL, ?, ?, 'friend_added', ?)",
        (users["social_a"].uuid, "social_b", recent.isoformat()),
    )
    cursor.execute(
        "INSERT INTO user_notifications VALUES (NULL, ?, ?, 'friend_added', ?)",
        (users["social_b"].uuid, "social_a", stale.isoformat()),
    )
    cursor.execute(
        "INSERT INTO user_notifications VALUES (NULL, ?, ?, 'friend_removed', ?)",
        (users["social_c"].uuid, "missing-source", recent.isoformat()),
    )
    cursor.execute(
        "INSERT INTO mutes "
        "(username, admin_username, reason, issued_at, expires_at) "
        "VALUES (?, 'admin', 'reason', ?, ?)",
        ("mute_active", recent.isoformat(), future.isoformat()),
    )
    cursor.execute(
        "INSERT INTO mutes "
        "(username, admin_username, reason, issued_at, expires_at) "
        "VALUES (?, 'admin', 'reason', ?, ?)",
        ("mute_expired", old_game.isoformat(), recent.isoformat()),
    )
    cursor.execute(
        "INSERT INTO mutes "
        "(username, admin_username, reason, issued_at, expires_at) "
        "VALUES ('missing-mute', 'admin', 'reason', ?, ?)",
        (recent.isoformat(), future.isoformat()),
    )

    preview = db.analyze_storage_cleanup(
        tmp_path / "backups",
        reference_time=reference,
    )
    preview_counts = {category.code: category.count for category in preview.categories}
    expected_codes = tuple(category.value for category in DatabaseCleanupCategoryCode)
    assert tuple(preview_counts) == expected_codes
    assert set(preview_counts.values()) == {1}
    assert preview.total_candidate_records == len(expected_codes)
    assert preview.invalid_timestamp_values == 1
    assert db.get_password_reset_token(users["social_b"].uuid) is None

    result = db.clean_storage(reference_time=reference)
    assert {category.code: category.count for category in result.categories} == preview_counts
    assert result.total_deleted_records == preview.total_candidate_records
    assert result.invalid_timestamp_values == 1

    assert cursor.execute("SELECT COUNT(*) FROM game_results").fetchone()[0] == 1
    assert cursor.execute("SELECT COUNT(*) FROM game_result_players").fetchone()[0] == 1
    assert cursor.execute("SELECT save_name FROM saved_tables").fetchone()[0] == "Very Old Save"
    assert cursor.execute("SELECT COUNT(*) FROM global_chat_messages").fetchone()[0] == 1
    assert cursor.execute("SELECT COUNT(*) FROM moderation_reports").fetchone()[0] == 1
    assert cursor.execute("SELECT table_id FROM tables").fetchone()[0] == "active"
    assert cursor.execute("SELECT token_hash FROM password_reset_tokens").fetchone()[0] == "malformed"
    assert [row[0] for row in cursor.execute("SELECT username FROM bans")] == ["recent_ban"]
    assert [row[0] for row in cursor.execute("SELECT username FROM mutes")] == ["mute_active"]
    assert cursor.execute("SELECT COUNT(*) FROM friendships").fetchone()[0] == 1
    assert cursor.execute("SELECT COUNT(*) FROM user_blocks").fetchone()[0] == 1
    assert cursor.execute("SELECT COUNT(*) FROM user_notifications").fetchone()[0] == 1

def test_connect_never_runs_retention_cleanup_implicitly(tmp_path):
    db_path = tmp_path / "PlayAural.db"
    database = Database(db_path)
    database.connect()

    old_game = datetime.datetime.now() - timedelta(days=400)
    cursor = database._conn.cursor()
    cursor.execute(
        "INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data) VALUES (?, ?, ?, ?)",
        ("pig", old_game.isoformat(), 100, "{}"),
    )
    database._conn.commit()
    database.close()

    database = Database(db_path)
    database.connect()
    cursor = database._conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM game_results")
    assert cursor.fetchone()[0] == 1
    database.close()

    database = Database(db_path)
    database.connect()
    cursor = database._conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM game_results")
    assert cursor.fetchone()[0] == 1

    database.clean_storage()
    cursor.execute("SELECT COUNT(*) FROM game_results")
    assert cursor.fetchone()[0] == 1
    database.close()


def test_active_moderation_lookups_do_not_bypass_explicit_cleanup(db, tmp_path):
    reference = datetime.datetime.now()
    old_ban_expiry = reference - timedelta(days=31)
    old_mute_expiry = reference - timedelta(hours=1)
    db.ban_user("expired-ban", "admin", "reason", old_ban_expiry.isoformat())
    db.mute_user("expired-mute", "admin", "reason", old_mute_expiry.isoformat())

    assert db.get_active_ban("expired-ban") is None
    assert db.get_active_mute("expired-mute") is None
    assert db._conn.execute("SELECT COUNT(*) FROM bans").fetchone()[0] == 1
    assert db._conn.execute("SELECT COUNT(*) FROM mutes").fetchone()[0] == 1

    preview = db.analyze_storage_cleanup(
        tmp_path / "backups",
        reference_time=reference,
    )
    counts = {category.code: category.count for category in preview.categories}
    assert counts[DatabaseCleanupCategoryCode.EXPIRED_BANS.value] == 1
    assert counts[DatabaseCleanupCategoryCode.EXPIRED_MUTES.value] == 1

    db.clean_storage(reference_time=reference)
    assert db._conn.execute("SELECT COUNT(*) FROM bans").fetchone()[0] == 0
    assert db._conn.execute("SELECT COUNT(*) FROM mutes").fetchone()[0] == 0


def test_database_compaction_reclaims_free_pages_and_preserves_live_data(tmp_path):
    database = Database(tmp_path / "compact.sqlite")
    database.connect()
    try:
        user = database.create_user("Retained", "hash")
        for index in range(750):
            database.add_global_chat_message(
                user.uuid,
                user.username,
                "en",
                f"{index}:" + ("x" * 450),
            )
        assert database.clear_global_chat_messages() == 750
        free_pages = database._conn.execute(
            "PRAGMA freelist_count"
        ).fetchone()[0]
        assert free_pages > 0

        result = database.compact_database()

        assert result.before_free_pages == free_pages
        assert result.after_free_pages == 0
        assert result.after_bytes < result.before_bytes
        assert result.reclaimed_bytes == result.before_bytes - result.after_bytes
        assert database.get_user("Retained").uuid == user.uuid
        assert database._conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert not list(tmp_path.glob(".*.compaction-*.partial*"))
    finally:
        database.close()


def test_database_compaction_vacuum_failure_preserves_authoritative_database(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    database = Database(tmp_path / "compact.sqlite")
    database.connect()
    try:
        user = database.create_user("Still Here", "hash")

        def fail_vacuum(_connection):
            raise sqlite3.OperationalError("disk I/O error")

        monkeypatch.setattr(database, "_vacuum_connection", fail_vacuum)
        with pytest.raises(sqlite3.OperationalError, match="disk I/O error") as exc_info:
            database.compact_database()

        notes = " ".join(getattr(exc_info.value, "__notes__", ()))
        assert "VACUUM staged candidate" in notes
        assert "replacement applied: False" in notes
        assert "SQLite runtime:" in notes
        assert database.get_user("Still Here").uuid == user.uuid
        assert database._conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert not list(tmp_path.glob(".*.compaction-*.partial*"))
    finally:
        database.close()


def test_database_compaction_publish_failure_reopens_original_database(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    database = Database(tmp_path / "compact.sqlite")
    database.connect()
    try:
        user = database.create_user("Original Retained", "hash")

        def fail_replace(_source, _destination):
            raise OSError("simulated atomic replacement failure")

        monkeypatch.setattr(database, "_atomic_replace", fail_replace)
        with pytest.raises(OSError, match="replacement failure") as exc_info:
            database.compact_database()

        notes = " ".join(getattr(exc_info.value, "__notes__", ()))
        assert "atomically publish compacted database" in notes
        assert "replacement applied: False" in notes
        assert database.get_user("Original Retained").uuid == user.uuid
        assert database._conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert not list(tmp_path.glob(".*.compaction-*.partial*"))
    finally:
        database.close()


def test_database_compaction_post_publication_validation_fails_closed(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    database_path = tmp_path / "compact.sqlite"
    database = Database(database_path)
    database.connect()
    retained = database.create_user("Published Retained", "hash")
    original_signature = database._snapshot_signature
    signature_calls = 0

    def fail_post_publication_signature(connection):
        nonlocal signature_calls
        signature_calls += 1
        signature = original_signature(connection)
        if signature_calls == 6:
            return replace(
                signature,
                application_id=signature.application_id + 1,
            )
        return signature

    monkeypatch.setattr(
        database,
        "_snapshot_signature",
        fail_post_publication_signature,
    )
    with pytest.raises(
        sqlite3.DatabaseError,
        match="published compacted database failed logical validation",
    ) as exc_info:
        database.compact_database()

    assert signature_calls == 6
    assert database._conn is None
    assert "replacement applied: True" in " ".join(
        getattr(exc_info.value, "__notes__", ())
    )

    reopened = Database(database_path)
    reopened.connect()
    try:
        assert reopened.get_user("Published Retained").uuid == retained.uuid
    finally:
        reopened.close()


def test_database_compaction_removes_only_abandoned_owned_candidates(tmp_path):
    database_path = tmp_path / "source.sqlite"
    stale = tmp_path / ".source.sqlite.compaction-old.sqlite3.partial"
    recent = tmp_path / ".source.sqlite.compaction-live.sqlite3.partial"
    unrelated = tmp_path / ".other.sqlite.compaction-old.sqlite3.partial"
    for path in (stale, recent, unrelated):
        path.write_bytes(b"fragment")
    _mark_backup_fragment_abandoned(stale)
    _mark_backup_fragment_abandoned(unrelated)

    database = Database(database_path)
    database.connect()
    try:
        database.compact_database()
        assert not stale.exists()
        assert recent.read_bytes() == b"fragment"
        assert unrelated.read_bytes() == b"fragment"
    finally:
        database.close()


def test_database_compaction_preflights_staging_and_vacuum_space(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    database = Database(tmp_path / "compact.sqlite")
    database.connect()
    required_sizes: list[int] = []
    monkeypatch.setattr(database, "MINIMUM_MAINTENANCE_FREE_BYTES", 0)
    monkeypatch.setattr(
        database,
        "_require_free_space",
        lambda _directory, required_bytes: required_sizes.append(required_bytes),
    )
    try:
        page_size = database._conn.execute("PRAGMA page_size").fetchone()[0]
        page_count = database._conn.execute("PRAGMA page_count").fetchone()[0]
        database.compact_database()
        assert required_sizes == [
            page_size * page_count * 3,
            page_size * page_count * 2,
        ]
    finally:
        database.close()


def test_free_space_preflight_reserves_blocks_with_service_credentials(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    required_bytes = 4096
    reservations: list[tuple[int, int]] = []

    class DiskUsage:
        free = required_bytes * 10

    monkeypatch.setattr(
        "server.persistence.database.shutil.disk_usage",
        lambda _directory: DiskUsage(),
    )
    monkeypatch.setattr(
        os,
        "posix_fallocate",
        lambda _descriptor, offset, length: reservations.append((offset, length)),
        raising=False,
    )

    Database._require_free_space(tmp_path, required_bytes)

    assert reservations == [(0, required_bytes)]
    assert list(tmp_path.iterdir()) == []


def test_free_space_preflight_reports_effective_account_quota(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    required_bytes = 4096

    class DiskUsage:
        free = required_bytes * 10

    def reject_reservation(_descriptor: int, _offset: int, _length: int) -> None:
        raise OSError(errno.EDQUOT, "Disk quota exceeded")

    monkeypatch.setattr(
        "server.persistence.database.shutil.disk_usage",
        lambda _directory: DiskUsage(),
    )
    monkeypatch.setattr(
        os,
        "posix_fallocate",
        reject_reservation,
        raising=False,
    )

    with pytest.raises(OSError, match="current account could not reserve") as exc_info:
        Database._require_free_space(tmp_path, required_bytes)

    assert exc_info.value.__cause__.errno == errno.EDQUOT
    assert "user, group, or project quotas" in str(exc_info.value)
    assert list(tmp_path.iterdir()) == []


def test_database_compaction_rejects_an_active_transaction(tmp_path):
    database = Database(tmp_path / "compact-transaction.sqlite")
    database.connect()
    try:
        database._conn.execute("BEGIN")
        with pytest.raises(RuntimeError, match="during a transaction"):
            database.compact_database()
        database._conn.rollback()
    finally:
        database.close()


def test_database_connection_uses_explicit_crash_durability_settings(tmp_path):
    database = Database(tmp_path / "durable.sqlite")
    database.connect()
    try:
        assert database._conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert database._conn.execute("PRAGMA synchronous").fetchone()[0] == 2
        assert database._conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        database.close()


def test_transaction_preserves_original_error_when_rollback_also_fails():
    class FailingCursor:
        def __init__(self, connection):
            self.connection = connection
            self.closed = False

        def execute(self, _sql):
            self.connection.in_transaction = True

        def close(self):
            self.closed = True

    class FailingConnection:
        def __init__(self):
            self.in_transaction = False
            self.created_cursor = FailingCursor(self)

        def cursor(self):
            return self.created_cursor

        def commit(self):
            raise sqlite3.OperationalError("simulated commit failure")

        def rollback(self):
            raise sqlite3.OperationalError("simulated rollback failure")

    database = Database(":memory:")
    connection = FailingConnection()
    database._conn = connection
    try:
        with pytest.raises(sqlite3.OperationalError, match="commit failure") as exc_info:
            with database._transaction():
                pass
        assert "rollback also failed" in " ".join(
            getattr(exc_info.value, "__notes__", ())
        )
        assert connection.created_cursor.closed is True
    finally:
        database._conn = None


def test_sqlite_write_failure_note_identifies_operator_storage_checks(tmp_path):
    error = sqlite3.OperationalError("disk I/O error")
    error.sqlite_errorname = "SQLITE_IOERR_WRITE"
    error.sqlite_errorcode = 778

    Database._add_sqlite_failure_note(
        error,
        operation="migration",
        stage="commit schema transaction",
        path=tmp_path / "PlayAural.db",
        replacement_applied=False,
    )

    notes = " ".join(error.__notes__)
    assert "SQLITE_IOERR_WRITE (778)" in notes
    assert "filesystem and mount health" in notes
    assert "quota" in notes
    assert "file-size limits" in notes
    assert "SELinux" in notes


def test_sqlite_runtime_baseline_includes_almalinux_8():
    Database._require_supported_sqlite_version((3, 26, 0))
    with pytest.raises(RuntimeError, match="3.25.0 or newer"):
        Database._require_supported_sqlite_version((3, 24, 9))


def test_database_backup_is_unique_valid_and_preserves_live_data(tmp_path):
    source_path = tmp_path / "source.sqlite"
    backup_dir = tmp_path / "backups"
    database = Database(source_path)
    database.connect()
    try:
        user = database.create_user("Retained Backup User", "hash")
        first = database.backup_database(backup_dir, purpose="manual")
        second = database.backup_database(backup_dir, purpose="manual")

        assert first.path != second.path
        assert first.path.parent == backup_dir.resolve()
        assert first.size_bytes == first.path.stat().st_size
        assert first.page_count > 0
        assert not list(backup_dir.glob("*.partial"))

        restored = Database(first.path)
        restored.connect()
        try:
            assert restored.get_user("Retained Backup User").uuid == user.uuid
            assert restored._conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        finally:
            restored.close()
    finally:
        database.close()


def test_database_backup_rejects_snapshot_metadata_mismatch(tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    database = Database(tmp_path / "source.sqlite")
    database.connect()
    original_signature = database._snapshot_signature
    signature_calls = 0

    def mismatched_destination(connection):
        nonlocal signature_calls
        signature_calls += 1
        signature = original_signature(connection)
        if signature_calls == 2:
            return replace(signature, page_count=signature.page_count + 1)
        return signature

    monkeypatch.setattr(database, "_snapshot_signature", mismatched_destination)
    try:
        with pytest.raises(sqlite3.DatabaseError, match="does not match") as exc_info:
            database.backup_database(backup_dir)
        assert "database backup stage" in " ".join(
            getattr(exc_info.value, "__notes__", ())
        )
        assert not list(backup_dir.iterdir())
    finally:
        database.close()


def test_database_backup_publication_failure_removes_final_file(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    backup_dir = tmp_path / "backups"
    database = Database(tmp_path / "source.sqlite")
    database.connect()

    def fail_directory_flush(_directory):
        raise OSError("simulated directory fsync failure")

    monkeypatch.setattr(database, "_flush_directory_to_disk", fail_directory_flush)
    try:
        with pytest.raises(OSError, match="directory fsync failure") as exc_info:
            database.backup_database(backup_dir)
        assert not list(backup_dir.iterdir())
        assert "publication durability failed" in " ".join(
            getattr(exc_info.value, "__notes__", ())
        )
    finally:
        database.close()


def test_database_backup_rejects_active_transaction_without_partial_file(tmp_path):
    backup_dir = tmp_path / "backups"
    database = Database(tmp_path / "source.sqlite")
    database.connect()
    try:
        database._conn.execute("BEGIN")
        with pytest.raises(RuntimeError, match="during a transaction"):
            database.backup_database(backup_dir)
        database._conn.rollback()
        assert not backup_dir.exists()
    finally:
        database.close()


def test_database_backup_rejects_foreign_key_corruption(tmp_path):
    backup_dir = tmp_path / "backups"
    database = Database(tmp_path / "source.sqlite")
    database.connect()
    try:
        database._conn.execute("PRAGMA foreign_keys = OFF")
        database._conn.execute(
            "CREATE TABLE integrity_parent (id INTEGER PRIMARY KEY)"
        )
        database._conn.execute(
            """
            CREATE TABLE integrity_child (
                parent_id INTEGER REFERENCES integrity_parent(id)
            )
            """
        )
        database._conn.execute(
            "INSERT INTO integrity_child (parent_id) VALUES (1)"
        )
        database._conn.execute("PRAGMA foreign_keys = ON")

        with pytest.raises(sqlite3.DatabaseError, match="foreign key check"):
            database.backup_database(backup_dir)
        assert not list(backup_dir.glob("*.sqlite3"))
        assert not list(backup_dir.glob("*.partial"))
    finally:
        database.close()


def test_database_backup_removes_only_unpublished_backup_fragments(tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    stale_main = backup_dir / ".PlayAural-manual-old.sqlite3.partial"
    stale_wal = backup_dir / ".PlayAural-manual-old.sqlite3.partial-wal"
    retained_backup = backup_dir / "PlayAural-manual-old.sqlite3"
    unrelated_partial = backup_dir / ".unrelated.sqlite3.partial"
    for path in (stale_main, stale_wal, retained_backup, unrelated_partial):
        path.write_bytes(b"test")
    _mark_backup_fragment_abandoned(stale_main)
    _mark_backup_fragment_abandoned(stale_wal)

    database = Database(tmp_path / "source.sqlite")
    database.connect()
    try:
        result = database.backup_database(backup_dir)

        assert result.path.exists()
        assert result.incomplete_files_removed == 2
        assert result.incomplete_file_bytes_removed == 8
        assert not stale_main.exists()
        assert not stale_wal.exists()
        assert retained_backup.read_bytes() == b"test"
        assert unrelated_partial.read_bytes() == b"test"
    finally:
        database.close()


def test_database_backup_preserves_recent_matching_fragments(tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    recent_fragment = backup_dir / ".PlayAural-manual-live.sqlite3.partial"
    recent_fragment.write_bytes(b"possibly active")

    database = Database(tmp_path / "source.sqlite")
    database.connect()
    try:
        result = database.backup_database(backup_dir)

        assert result.incomplete_files_removed == 0
        assert result.incomplete_file_bytes_removed == 0
        assert recent_fragment.read_bytes() == b"possibly active"
    finally:
        database.close()


def test_storage_cleanup_rolls_back_every_category_if_one_delete_fails(
    tmp_path,
) -> None:
    database = Database(tmp_path / "cleanup-rollback.sqlite")
    database.connect()
    try:
        expired = (datetime.datetime.now() - timedelta(days=2)).isoformat()
        user = database.create_user("Rollback Retained", "hash")
        database._conn.execute(
            """
            INSERT INTO tables (
                table_id, game_type, host, members_json, game_json,
                checkpoint_created_at, checkpoint_expires_at
            ) VALUES ('expired', 'pig', ?, '[]', '{}', ?, ?)
            """,
            (user.username, expired, expired),
        )
        database.save_password_reset_token(
            user.uuid,
            "expired-token",
            expired,
        )
        database._conn.execute(
            """
            CREATE TRIGGER reject_token_cleanup
            BEFORE DELETE ON password_reset_tokens
            BEGIN
                SELECT RAISE(ABORT, 'simulated cleanup failure');
            END
            """
        )

        with pytest.raises(sqlite3.IntegrityError, match="simulated cleanup failure"):
            database.clean_storage()

        assert database._conn.execute(
            "SELECT COUNT(*) FROM tables WHERE table_id = 'expired'"
        ).fetchone()[0] == 1
        assert database._conn.execute(
            "SELECT COUNT(*) FROM password_reset_tokens"
        ).fetchone()[0] == 1
        assert database._conn.in_transaction is False
    finally:
        database.close()


def test_storage_cleanup_rolls_back_if_precommit_validation_fails(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = Database(tmp_path / "cleanup-validation.sqlite")
    database.connect()
    try:
        expired = (datetime.datetime.now() - timedelta(days=2)).isoformat()
        user = database.create_user("Validation Retained", "hash")
        database.save_password_reset_token(
            user.uuid,
            "expired-token",
            expired,
        )
        original_verify = database._verify_connection_integrity
        validation_count = 0

        def fail_precommit_validation(connection, *, full: bool) -> None:
            nonlocal validation_count
            validation_count += 1
            if validation_count == 2:
                raise sqlite3.DatabaseError("simulated precommit validation failure")
            original_verify(connection, full=full)

        monkeypatch.setattr(
            database,
            "_verify_connection_integrity",
            fail_precommit_validation,
        )

        with pytest.raises(
            sqlite3.DatabaseError,
            match="simulated precommit validation failure",
        ):
            database.clean_storage()

        assert validation_count == 2
        assert database._conn.execute(
            "SELECT COUNT(*) FROM password_reset_tokens"
        ).fetchone()[0] == 1
        assert database._conn.in_transaction is False
    finally:
        database.close()


def test_connect_leaves_corrupt_database_and_sidecars_untouched(tmp_path):
    db_path = tmp_path / "PlayAural.db"
    wal_path = tmp_path / "PlayAural.db-wal"
    shm_path = tmp_path / "PlayAural.db-shm"
    db_path.write_bytes(b"this is not a sqlite database")
    wal_path.write_bytes(b"stale wal")
    shm_path.write_bytes(b"stale shm")

    database = Database(db_path)
    with pytest.raises(sqlite3.DatabaseError):
        database.connect()

    assert db_path.read_bytes() == b"this is not a sqlite database"
    assert wal_path.read_bytes() == b"stale wal"
    assert shm_path.read_bytes() == b"stale shm"
    assert database._conn is None


def test_connect_rejects_orphan_sidecars_without_creating_main_database(tmp_path):
    db_path = tmp_path / "missing.db"
    wal_path = Path(f"{db_path}-wal")
    wal_path.write_bytes(b"orphaned wal")

    database = Database(db_path)
    with pytest.raises(sqlite3.DatabaseError, match="sidecar files exist"):
        database.connect()

    assert not db_path.exists()
    assert wal_path.read_bytes() == b"orphaned wal"
    assert database._conn is None


def _create_unversioned_database(db_path: Path) -> str:
    """Create the production v0 shape from the current schema for migration tests."""
    database = Database(db_path)
    database.connect()
    user = database.create_user("Legacy User", "hash")
    database._conn.execute(
        """
        INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data)
        VALUES (?, ?, ?, ?)
        """,
        ("pig", "2020-01-01T00:00:00", 100, "{}"),
    )
    database._conn.execute(
        """
        INSERT INTO password_reset_tokens
            (user_uuid, token_hash, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user.uuid,
            "expired-token",
            "2020-01-01T00:00:00",
            "2020-01-01T01:00:00",
        ),
    )
    database.close()

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("DROP TRIGGER protect_users_immutable_identity")
        connection.execute("DROP TABLE moderation_reports")
        connection.execute("DROP TABLE global_chat_messages")
        connection.execute("DROP TABLE server_settings")
        connection.execute("PRAGMA application_id = 0")
        connection.execute("PRAGMA user_version = 0")
        connection.commit()
    finally:
        connection.close()
    return user.uuid


def _replace_username_expression_index_with_v2_contract(
    connection: sqlite3.Connection,
) -> None:
    """Recreate the historical-chat index with schema-v2 function semantics."""
    connection.create_function(
        "USERNAME_KEY",
        1,
        lambda value: str(value or "").strip().casefold(),
        deterministic=True,
    )
    connection.execute("DROP INDEX idx_global_chat_messages_username_time")
    connection.execute(
        """
        CREATE INDEX idx_global_chat_messages_username_time
        ON global_chat_messages(
            USERNAME_KEY(sender_username), sent_at_utc DESC, id DESC
        )
        """
    )


def test_schema_discovery_uses_legacy_compatible_sqlite_catalog_name():
    """AlmaLinux 8 SQLite predates the sqlite_schema alias."""

    database = Database(":memory:")
    database.connect()
    connection = database._conn

    class LegacyCatalogConnection:
        def execute(self, sql, *args, **kwargs):
            if "sqlite_schema" in str(sql).lower():
                raise sqlite3.OperationalError("no such table: sqlite_schema")
            return connection.execute(sql, *args, **kwargs)

    database._conn = LegacyCatalogConnection()
    try:
        database._prepare_schema(migration_backup_dir=None)
    finally:
        database._conn = connection
        database.close()


def test_legacy_migration_creates_backup_and_preserves_all_rows(tmp_path):
    db_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "migration-backups"
    user_uuid = _create_unversioned_database(db_path)

    database = Database(db_path)
    database.connect(migration_backup_dir=backup_dir)
    try:
        assert database.get_user("Legacy User").uuid == user_uuid
        assert database._conn.execute(
            "SELECT COUNT(*) FROM game_results"
        ).fetchone()[0] == 1
        assert database._conn.execute(
            "SELECT COUNT(*) FROM password_reset_tokens"
        ).fetchone()[0] == 1
        assert database._conn.execute("PRAGMA application_id").fetchone()[0] == (
            Database.APPLICATION_ID
        )
        assert database._conn.execute("PRAGMA user_version").fetchone()[0] == (
            Database.CURRENT_SCHEMA_VERSION
        )
    finally:
        database.close()

    backups = list(backup_dir.glob("*.sqlite3"))
    assert len(backups) == 1
    backup = sqlite3.connect(backups[0])
    try:
        assert backup.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert backup.execute("PRAGMA application_id").fetchone()[0] == 0
        assert backup.execute("PRAGMA user_version").fetchone()[0] == 0
        assert backup.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert backup.execute("SELECT COUNT(*) FROM game_results").fetchone()[0] == 1
        assert backup.execute(
            "SELECT COUNT(*) FROM password_reset_tokens"
        ).fetchone()[0] == 1
        assert backup.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'moderation_reports'"
        ).fetchone()[0] == 0
    finally:
        backup.close()

    # A current database does not create repeated migration backups.
    database = Database(db_path)
    database.connect(migration_backup_dir=backup_dir)
    database.close()
    assert len(list(backup_dir.glob("*.sqlite3"))) == 1


def test_version_one_nullable_username_key_migrates_atomically(tmp_path):
    db_path = tmp_path / "version-one.db"
    backup_dir = tmp_path / "migration-backups"
    database = Database(db_path)
    database.connect()
    retained_user = database.create_user("Version One User", "hash")
    database.close()

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("ALTER TABLE users RENAME TO old_users")
        connection.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT COLLATE NOCASE UNIQUE NOT NULL,
                username_key TEXT,
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
        connection.execute("INSERT INTO users SELECT * FROM old_users")
        connection.execute("DROP TABLE old_users")
        connection.execute("CREATE INDEX idx_users_uuid ON users(uuid)")
        connection.execute(
            "CREATE INDEX idx_users_username_key ON users(username_key)"
        )
        _replace_username_expression_index_with_v2_contract(connection)
        connection.execute("PRAGMA user_version = 1")
        connection.commit()
    finally:
        connection.close()

    database = Database(db_path)
    database.connect(migration_backup_dir=backup_dir)
    try:
        assert database.get_user("Version One User").uuid == retained_user.uuid
        assert database._conn.execute("PRAGMA user_version").fetchone()[0] == (
            Database.CURRENT_SCHEMA_VERSION
        )
        username_key_column = next(
            row
            for row in database._conn.execute("PRAGMA table_info(users)")
            if row[1] == "username_key"
        )
        assert username_key_column[3] == 1
    finally:
        database.close()

    backups = list(backup_dir.glob("*.sqlite3"))
    assert len(backups) == 1
    backup = sqlite3.connect(backups[0])
    try:
        assert backup.execute("PRAGMA user_version").fetchone()[0] == 1
        assert backup.execute(
            "SELECT uuid FROM users WHERE username = 'Version One User'"
        ).fetchone()[0] == retained_user.uuid
        username_key_column = next(
            row
            for row in backup.execute("PRAGMA table_info(users)")
            if row[1] == "username_key"
        )
        assert username_key_column[3] == 0
    finally:
        backup.close()


def test_version_two_identity_contract_migrates_atomically(tmp_path):
    db_path = tmp_path / "version-two.db"
    backup_dir = tmp_path / "migration-backups"
    database = Database(db_path)
    database.connect()
    retained_user = database.create_user("Ｆｕｌｌ Width", "hash")
    retained_unicode_user = database.create_user("Đào Đức Trung", "hash")
    retained_message = database.add_global_chat_message(
        retained_user.uuid,
        retained_user.username,
        "en",
        "Retained identity evidence",
    )
    database.close()

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("DROP INDEX idx_users_uuid")
        connection.execute("CREATE INDEX idx_users_uuid ON users(uuid)")
        connection.execute("DROP TRIGGER protect_users_immutable_identity")
        _replace_username_expression_index_with_v2_contract(connection)
        connection.execute(
            "UPDATE users SET username_key = ? WHERE username = ?",
            ("ｆｕｌｌ width", "Ｆｕｌｌ Width"),
        )
        connection.execute("PRAGMA user_version = 2")
        connection.commit()
    finally:
        connection.close()

    database = Database(db_path)
    database.connect(migration_backup_dir=backup_dir)
    try:
        resolved = database.get_user("full width")
        assert resolved is not None
        assert resolved.uuid == retained_user.uuid
        assert resolved.username == retained_user.username
        resolved_unicode = database.get_user("đào đức trung")
        assert resolved_unicode is not None
        assert resolved_unicode.uuid == retained_unicode_user.uuid
        assert resolved_unicode.username == retained_unicode_user.username
        summaries = database.find_global_chat_sender_summaries("full width")
        assert [summary.sender_uuid for summary in summaries] == [
            retained_message.sender_uuid
        ]
        assert database._conn.execute(
            "SELECT username_key FROM users WHERE uuid = ?",
            (retained_user.uuid,),
        ).fetchone()[0] == "full width"
        uuid_index = next(
            row
            for row in database._conn.execute("PRAGMA index_list(users)")
            if row[1] == "idx_users_uuid"
        )
        assert uuid_index[2] == 1
        assert database._conn.execute("PRAGMA user_version").fetchone()[0] == (
            Database.CURRENT_SCHEMA_VERSION
        )
    finally:
        database.close()

    backups = list(backup_dir.glob("*.sqlite3"))
    assert len(backups) == 1
    backup = sqlite3.connect(backups[0])
    try:
        assert backup.execute("PRAGMA user_version").fetchone()[0] == 2
        backup_uuid_index = next(
            row
            for row in backup.execute("PRAGMA index_list(users)")
            if row[1] == "idx_users_uuid"
        )
        assert backup_uuid_index[2] == 0
    finally:
        backup.close()


@pytest.mark.parametrize("corruption", ["duplicate", "empty", "malformed"])
def test_version_two_migration_rejects_corrupt_account_ids_without_changes(
    tmp_path,
    corruption,
):
    db_path = tmp_path / f"version-two-{corruption}.db"
    backup_dir = tmp_path / "migration-backups"
    database = Database(db_path)
    database.connect()
    first = database.create_user("First Account", "hash")
    second = database.create_user("Second Account", "hash")
    database.close()

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("DROP INDEX idx_users_uuid")
        connection.execute("CREATE INDEX idx_users_uuid ON users(uuid)")
        connection.execute("DROP TRIGGER protect_users_immutable_identity")
        _replace_username_expression_index_with_v2_contract(connection)
        replacement = {
            "duplicate": first.uuid,
            "empty": "",
            "malformed": "not-an-account-uuid",
        }[corruption]
        connection.execute(
            "UPDATE users SET uuid = ? WHERE username = ?",
            (replacement, second.username),
        )
        connection.execute("PRAGMA user_version = 2")
        connection.commit()
    finally:
        connection.close()

    message = {
        "duplicate": "duplicate immutable account id",
        "empty": "empty immutable id",
        "malformed": "invalid immutable account id",
    }[corruption]
    with pytest.raises(sqlite3.DatabaseError, match=message):
        Database(db_path).connect(migration_backup_dir=backup_dir)

    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
        assert connection.execute(
            "SELECT uuid FROM users WHERE username = ?",
            (second.username,),
        ).fetchone()[0] == replacement
        uuid_index = next(
            row
            for row in connection.execute("PRAGMA index_list(users)")
            if row[1] == "idx_users_uuid"
        )
        assert uuid_index[2] == 0
    finally:
        connection.close()
    assert list(backup_dir.glob("*.sqlite3")) == []


def test_failed_migration_rolls_back_and_retains_recovery_backup(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "migration-backups"
    _create_unversioned_database(db_path)

    database = Database(db_path)
    original_create = database._create_tables_in_transaction

    def fail_after_schema_changes(cursor):
        original_create(cursor)
        raise RuntimeError("simulated migration failure")

    monkeypatch.setattr(
        database,
        "_create_tables_in_transaction",
        fail_after_schema_changes,
    )
    with pytest.raises(
        RuntimeError,
        match="simulated migration failure",
    ) as exc_info:
        database.connect(migration_backup_dir=backup_dir)

    assert database._conn is None
    notes = " ".join(exc_info.value.__notes__)
    assert "PlayAural database migration stage" in notes
    assert "replacement applied: False" in notes
    assert "verified migration backup" in notes
    assert "required live-filesystem workspace" in notes
    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute("PRAGMA application_id").fetchone()[0] == 0
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'moderation_reports'"
        ).fetchone()[0] == 0
    finally:
        connection.close()
    assert len(list(backup_dir.glob("*.sqlite3"))) == 1


def test_failed_migration_retry_reuses_exact_verified_backup(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "migration-backups"
    _create_unversioned_database(db_path)

    first_attempt = Database(db_path)
    original_create = first_attempt._create_tables_in_transaction

    def fail_after_schema_changes(cursor):
        original_create(cursor)
        raise RuntimeError("simulated first migration failure")

    monkeypatch.setattr(
        first_attempt,
        "_create_tables_in_transaction",
        fail_after_schema_changes,
    )
    with pytest.raises(RuntimeError, match="first migration failure"):
        first_attempt.connect(migration_backup_dir=backup_dir)

    backups = list(backup_dir.glob("*.sqlite3"))
    assert len(backups) == 1

    retry = Database(db_path)

    def reject_duplicate_backup(*_args, **_kwargs):
        raise AssertionError("an exact migration backup should be reused")

    monkeypatch.setattr(retry, "backup_database", reject_duplicate_backup)
    retry.connect(migration_backup_dir=backup_dir)
    try:
        assert retry.get_user("Legacy User") is not None
        assert retry._conn.execute("PRAGMA user_version").fetchone()[0] == (
            Database.CURRENT_SCHEMA_VERSION
        )
    finally:
        retry.close()
    assert list(backup_dir.glob("*.sqlite3")) == backups


def test_migration_retry_rejects_backup_with_same_counts_but_stale_values(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "migration-backups"
    _create_unversioned_database(db_path)

    first_attempt = Database(db_path)
    original_create = first_attempt._create_tables_in_transaction

    def fail_after_schema_changes(cursor):
        original_create(cursor)
        raise RuntimeError("simulated first migration failure")

    monkeypatch.setattr(
        first_attempt,
        "_create_tables_in_transaction",
        fail_after_schema_changes,
    )
    with pytest.raises(RuntimeError, match="first migration failure"):
        first_attempt.connect(migration_backup_dir=backup_dir)
    assert len(list(backup_dir.glob("*.sqlite3"))) == 1

    connection = sqlite3.connect(db_path)
    connection.execute(
        "UPDATE users SET bio = 'changed after first backup' "
        "WHERE username = 'Legacy User'"
    )
    connection.commit()
    connection.close()

    retry = Database(db_path)
    retry.connect(migration_backup_dir=backup_dir)
    try:
        assert retry.get_user("Legacy User").bio == "changed after first backup"
    finally:
        retry.close()
    assert len(list(backup_dir.glob("*.sqlite3"))) == 2


def test_migration_preflights_combined_backup_and_transaction_space(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "migration-backups"
    _create_unversioned_database(db_path)
    connection = sqlite3.connect(db_path)
    try:
        database_bytes = (
            connection.execute("PRAGMA page_size").fetchone()[0]
            * connection.execute("PRAGMA page_count").fetchone()[0]
        )
    finally:
        connection.close()

    database = Database(db_path)
    required_sizes: list[int] = []
    monkeypatch.setattr(database, "MINIMUM_MAINTENANCE_FREE_BYTES", 0)
    monkeypatch.setattr(
        database,
        "_require_free_space",
        lambda _directory, required_bytes: required_sizes.append(required_bytes),
    )
    database.connect(migration_backup_dir=backup_dir)
    database.close()

    assert required_sizes == [
        database_bytes * 3,
        database_bytes,
        database_bytes * 2,
    ]


def test_failed_migration_backup_prevents_any_schema_write(tmp_path, monkeypatch):
    db_path = tmp_path / "PlayAural.db"
    _create_unversioned_database(db_path)
    database = Database(db_path)

    def fail_backup(*_args, **_kwargs):
        raise OSError("simulated backup failure")

    monkeypatch.setattr(database, "backup_database", fail_backup)
    with pytest.raises(OSError, match="simulated backup failure"):
        database.connect(migration_backup_dir=tmp_path / "backups")

    assert database._conn is None
    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute("PRAGMA application_id").fetchone()[0] == 0
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'moderation_reports'"
        ).fetchone()[0] == 0
    finally:
        connection.close()


def test_post_migration_validation_failure_rolls_back_header_and_schema(tmp_path):
    db_path = tmp_path / "incomplete-legacy.db"
    backup_dir = tmp_path / "backups"
    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            uuid TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "INSERT INTO users VALUES (1, 'Retained', 'hash', 'retained-uuid')"
    )
    connection.commit()
    connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="invalid columns"):
        Database(db_path).connect(migration_backup_dir=backup_dir)

    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute("PRAGMA application_id").fetchone()[0] == 0
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
        assert connection.execute("SELECT username FROM users").fetchone()[0] == (
            "Retained"
        )
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(users)")
        }
        assert "username_key" not in columns
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'moderation_reports'"
        ).fetchone()[0] == 0
    finally:
        connection.close()
    assert len(list(backup_dir.glob("*.sqlite3"))) == 1


def test_connect_rejects_newer_or_foreign_database_without_mutation(tmp_path):
    newer_path = tmp_path / "newer.db"
    newer = Database(newer_path)
    newer.connect()
    newer.close()
    connection = sqlite3.connect(newer_path)
    connection.execute(
        f"PRAGMA user_version = {Database.CURRENT_SCHEMA_VERSION + 1}"
    )
    connection.close()
    newer_bytes = newer_path.read_bytes()

    with pytest.raises(sqlite3.DatabaseError, match="newer than supported"):
        Database(newer_path).connect()
    assert newer_path.read_bytes() == newer_bytes

    foreign_path = tmp_path / "foreign.db"
    connection = sqlite3.connect(foreign_path)
    connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
    connection.execute("PRAGMA application_id = 1234")
    connection.commit()
    connection.close()
    foreign_bytes = foreign_path.read_bytes()

    with pytest.raises(sqlite3.DatabaseError, match="another application"):
        Database(foreign_path).connect()
    assert foreign_path.read_bytes() == foreign_bytes


def test_current_schema_drift_fails_closed_without_recreating_data(tmp_path):
    db_path = tmp_path / "drift.db"
    database = Database(db_path)
    database.connect()
    database.create_user("Retained", "hash")
    database.close()
    connection = sqlite3.connect(db_path)
    connection.execute("DROP TABLE server_settings")
    connection.commit()
    connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="invalid application tables"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'server_settings'"
        ).fetchone()[0] == 0
    finally:
        connection.close()


def test_current_schema_rejects_unexpected_column_without_repair(tmp_path):
    db_path = tmp_path / "unexpected-column.db"
    database = Database(db_path)
    database.connect()
    database.create_user("Retained Column User", "hash")
    database.close()

    connection = sqlite3.connect(db_path)
    connection.execute("ALTER TABLE users ADD COLUMN obsolete_value TEXT")
    connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="unexpected: obsolete_value"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(users)")}
        assert "obsolete_value" in columns
        assert connection.execute(
            "SELECT COUNT(*) FROM users WHERE username = 'Retained Column User'"
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_current_schema_rejects_unexpected_trigger_without_repair(tmp_path):
    db_path = tmp_path / "unexpected-trigger.db"
    database = Database(db_path)
    database.connect()
    database.close()

    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TRIGGER unexpected_user_delete
        AFTER INSERT ON users
        BEGIN
            DELETE FROM users WHERE id = NEW.id;
        END
        """
    )
    connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="unexpected objects"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type = 'trigger' AND name = 'unexpected_user_delete'"
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_current_schema_rejects_missing_identity_trigger_without_repair(tmp_path):
    db_path = tmp_path / "missing-identity-trigger.db"
    database = Database(db_path)
    database.connect()
    database.close()

    connection = sqlite3.connect(db_path)
    connection.execute("DROP TRIGGER protect_users_immutable_identity")
    connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="missing required triggers"):
        Database(db_path).connect()


def test_current_schema_rejects_missing_required_index_without_repair(tmp_path):
    db_path = tmp_path / "missing-index.db"
    database = Database(db_path)
    database.connect()
    retained = database.create_user("Retained Index User", "hash")
    database.close()

    connection = sqlite3.connect(db_path)
    connection.execute("DROP INDEX idx_users_uuid")
    connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="missing required indexes"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute(
            "SELECT uuid FROM users WHERE username = 'Retained Index User'"
        ).fetchone()[0] == retained.uuid
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'idx_users_uuid'"
        ).fetchone()[0] == 0
    finally:
        connection.close()


def test_current_schema_rejects_malformed_required_index_without_repair(tmp_path):
    db_path = tmp_path / "malformed-index.db"
    database = Database(db_path)
    database.connect()
    database.close()

    connection = sqlite3.connect(db_path)
    connection.execute("DROP INDEX idx_users_uuid")
    connection.execute("CREATE INDEX idx_users_uuid ON users(locale)")
    connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="malformed definitions"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        columns = connection.execute("PRAGMA index_info(idx_users_uuid)").fetchall()
        assert [row[2] for row in columns] == ["locale"]
    finally:
        connection.close()


def test_current_schema_rejects_unexpected_unique_key_without_repair(tmp_path):
    db_path = tmp_path / "unexpected-unique-key.db"
    database = Database(db_path)
    database.connect()
    database.close()

    connection = sqlite3.connect(db_path)
    connection.execute("CREATE UNIQUE INDEX unexpected_unique_bio ON users(bio)")
    connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="required indexes"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE name = 'unexpected_unique_bio'"
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_current_schema_rejects_missing_primary_key_without_repair(tmp_path):
    db_path = tmp_path / "missing-primary-key.db"
    database = Database(db_path)
    database.connect()
    database.close()

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("ALTER TABLE server_settings RENAME TO old_server_settings")
        connection.execute(
            """
            CREATE TABLE server_settings (
                setting_key TEXT NOT NULL,
                value_json TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT INTO server_settings SELECT * FROM old_server_settings"
        )
        connection.execute("DROP TABLE old_server_settings")
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="malformed column definitions"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        columns = connection.execute("PRAGMA table_info(server_settings)").fetchall()
        assert all(row[5] == 0 for row in columns)
    finally:
        connection.close()


def test_current_schema_rejects_missing_check_constraint_without_repair(tmp_path):
    db_path = tmp_path / "missing-check.db"
    database = Database(db_path)
    database.connect()
    database.close()

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("ALTER TABLE server_settings RENAME TO old_server_settings")
        connection.execute(
            """
            CREATE TABLE server_settings (
                setting_key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT INTO server_settings SELECT * FROM old_server_settings"
        )
        connection.execute("DROP TABLE old_server_settings")
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="check constraints"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        table_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE name = 'server_settings'"
        ).fetchone()[0]
        assert "CHECK" not in table_sql.upper()
    finally:
        connection.close()


def test_current_schema_rejects_missing_required_foreign_key_without_repair(
    tmp_path,
):
    db_path = tmp_path / "missing-foreign-key.db"
    database = Database(db_path)
    database.connect()
    database.close()

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute(
            "ALTER TABLE game_result_players RENAME TO old_game_result_players"
        )
        connection.execute(
            """
            CREATE TABLE game_result_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                is_bot INTEGER NOT NULL
            )
            """
        )
        connection.execute("DROP TABLE old_game_result_players")
        connection.execute(
            "CREATE INDEX idx_result_players_player "
            "ON game_result_players(player_id)"
        )
        connection.execute(
            "CREATE INDEX idx_result_players_result "
            "ON game_result_players(result_id)"
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.DatabaseError, match="foreign keys"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute(
            "PRAGMA foreign_key_list(game_result_players)"
        ).fetchall() == []
    finally:
        connection.close()


def test_corruption_detection_is_narrow():
    assert Database._is_corruption_error(
        sqlite3.DatabaseError("database disk image is malformed")
    )
    assert Database._is_corruption_error(
        sqlite3.DatabaseError("database integrity check failed: freelist error")
    )
    assert not Database._is_corruption_error(
        sqlite3.OperationalError("database is locked")
    )


def test_cli_auth_database_refuses_corrupt_database(tmp_path, monkeypatch, capsys):
    from server import cli

    db_path = tmp_path / "PlayAural.db"
    db_path.write_bytes(b"this is not a sqlite database")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        with cli.open_auth_database():
            raise AssertionError("corrupt database should not open")

    assert exc_info.value.code == 1
    assert "database appears to be corrupt" in capsys.readouterr().out
    assert db_path.read_bytes() == b"this is not a sqlite database"
    assert not list(tmp_path.glob("PlayAural.db.corrupt-*"))


def test_prune_unregistered_game_data_removes_only_stale_game_types(db, capsys):
    cursor = db._conn.cursor()

    cursor.execute(
        """
        INSERT INTO tables (table_id, game_type, host, members_json, game_json, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("valid-table", "pig", "Alice", "[]", "{}", "waiting"),
    )
    cursor.execute(
        """
        INSERT INTO tables (table_id, game_type, host, members_json, game_json, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("stale-table", "lastcard", "Alice", "[]", "{}", "waiting"),
    )
    cursor.execute(
        """
        INSERT INTO saved_tables
            (username, save_name, game_type, game_json, members_json, saved_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("Alice", "Pig Save", "pig", "{}", "[]", "2026-01-01T00:00:00"),
    )
    cursor.execute(
        """
        INSERT INTO saved_tables
            (username, save_name, game_type, game_json, members_json, saved_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("Alice", "Last Card Save", "lastcard", "{}", "[]", "2026-01-01T00:00:00"),
    )
    cursor.execute(
        """
        INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data)
        VALUES (?, ?, ?, ?)
        """,
        ("pig", "2026-01-01T00:00:00", 100, "{}"),
    )
    valid_result_id = cursor.lastrowid
    cursor.execute(
        """
        INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data)
        VALUES (?, ?, ?, ?)
        """,
        ("lastcard", "2026-01-01T00:00:00", 100, "{}"),
    )
    stale_result_id = cursor.lastrowid
    cursor.execute(
        """
        INSERT INTO game_result_players (result_id, player_id, player_name, is_bot)
        VALUES (?, ?, ?, ?)
        """,
        (valid_result_id, "p1", "Alice", 0),
    )
    cursor.execute(
        """
        INSERT INTO game_result_players (result_id, player_id, player_name, is_bot)
        VALUES (?, ?, ?, ?)
        """,
        (stale_result_id, "p2", "Bob", 0),
    )
    cursor.execute(
        """
        INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
        VALUES (?, ?, ?, ?)
        """,
        ("p1", "pig", "wins", 2),
    )
    cursor.execute(
        """
        INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
        VALUES (?, ?, ?, ?)
        """,
        ("p2", "lastcard", "wins", 3),
    )
    cursor.execute(
        "INSERT INTO player_ratings (player_id, game_type, mu, sigma) VALUES (?, ?, ?, ?)",
        ("p1", "pig", 25.0, 8.0),
    )
    cursor.execute(
        "INSERT INTO player_ratings (player_id, game_type, mu, sigma) VALUES (?, ?, ?, ?)",
        ("p2", "lastcard", 28.0, 7.0),
    )
    cursor.execute(
        """
        CREATE TABLE future_game_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_type TEXT NOT NULL,
            note TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "INSERT INTO future_game_events (game_type, note) VALUES (?, ?)",
        ("pig", "keep"),
    )
    cursor.execute(
        "INSERT INTO future_game_events (game_type, note) VALUES (?, ?)",
        ("lastcard", "delete"),
    )
    cursor.execute(
        """
        CREATE TABLE future_result_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER REFERENCES game_results(id),
            note TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "INSERT INTO future_result_notes (result_id, note) VALUES (?, ?)",
        (valid_result_id, "keep"),
    )
    cursor.execute(
        "INSERT INTO future_result_notes (result_id, note) VALUES (?, ?)",
        (stale_result_id, "delete"),
    )
    db._conn.commit()

    counts = db.prune_unregistered_game_data({"pig", "uno"})
    printed = capsys.readouterr().out

    assert counts["tables"] == 1
    assert counts["saved_tables"] == 1
    assert counts["game_results"] == 1
    assert counts["game_result_players"] == 1
    assert counts["future_game_events"] == 1
    assert counts["future_result_notes"] == 1
    assert counts["player_game_stats"] == 1
    assert counts["player_ratings"] == 1
    assert "Database Pruning: Checking unregistered game data" in printed
    assert "Unregistered game types detected: lastcard" in printed
    assert "future_game_events=1" in printed
    assert "future_result_notes=1" in printed

    for table_name in (
        "tables",
        "saved_tables",
        "future_game_events",
        "game_results",
        "player_game_stats",
        "player_ratings",
    ):
        cursor.execute(f"SELECT DISTINCT game_type FROM {table_name}")
        assert [row[0] for row in cursor.fetchall()] == ["pig"]

    cursor.execute("SELECT result_id FROM game_result_players")
    assert [row[0] for row in cursor.fetchall()] == [valid_result_id]
    cursor.execute("SELECT result_id FROM future_result_notes")
    assert [row[0] for row in cursor.fetchall()] == [valid_result_id]


def test_prune_unregistered_game_data_empty_allowlist_is_noop(db):
    cursor = db._conn.cursor()
    cursor.execute(
        """
        INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
        VALUES (?, ?, ?, ?)
        """,
        ("p1", "lastcard", "wins", 1),
    )
    db._conn.commit()

    counts = db.prune_unregistered_game_data(set())

    assert not any(counts.values())
    cursor.execute("SELECT game_type FROM player_game_stats")
    assert [row[0] for row in cursor.fetchall()] == ["lastcard"]


def test_prune_unsupported_leaderboard_data_removes_only_invalid_stats(db, capsys):
    cursor = db._conn.cursor()
    stat_rows = [
        ("p1", "pig", "games_played", 5),
        ("p1", "pig", "wins", 2),
        ("p1", "pig", "losses", 3),
        ("p1", "pig", "total_score", 240),
        ("p1", "pig", "high_score", 120),
        ("p1", "pig", "junk_score", 999),
        ("p2", "twentyone", "games_played", 3),
        ("p2", "twentyone", "wins", 1),
        ("p2", "twentyone", "losses", 2),
        ("p2", "twentyone", "total_score", 50),
        ("p2", "twentyone", "high_score", 30),
        ("p3", "metalpipe", "games_played", 4),
        ("p3", "metalpipe", "losses", 4),
        ("p4", "battle", "games_played", 2),
        ("p4", "battle", "custom_most_enemies_defeated_high", 13),
        ("p4", "battle", "custom_deepest_wave_reached_high", 5),
        ("p4", "battle", "total_score", 500),
        ("p5", "lastcard", "wins", 8),
    ]
    cursor.executemany(
        """
        INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
        VALUES (?, ?, ?, ?)
        """,
        stat_rows,
    )
    rating_rows = [
        ("p1", "pig", 30.0, 6.0),
        ("p2", "twentyone", 28.0, 7.0),
        ("p3", "metalpipe", 31.0, 5.0),
        ("p6", "blackjack", 27.0, 8.0),
        ("p5", "lastcard", 35.0, 4.0),
        ("p7", "pig", 25.0, 0.0),
    ]
    cursor.executemany(
        "INSERT INTO player_ratings (player_id, game_type, mu, sigma) VALUES (?, ?, ?, ?)",
        rating_rows,
    )
    db._conn.commit()

    counts = db.prune_unsupported_leaderboard_data(
        {
            "pig": {"games_played", "wins", "losses", "total_score", "high_score"},
            "twentyone": {"games_played", "wins", "losses"},
            "metalpipe": set(),
            "battle": {
                "games_played",
                "custom_most_enemies_defeated_high",
                "custom_deepest_wave_reached_high",
            },
            "blackjack": {"games_played"},
        },
        {"pig", "twentyone"},
    )
    printed = capsys.readouterr().out

    assert counts == {"player_game_stats": 6, "player_ratings": 3}
    assert "Unsupported leaderboard stat keys detected" in printed
    assert "metalpipe:games_played" in printed
    assert "twentyone:total_score" in printed
    assert "Unsupported rating game types detected: blackjack, metalpipe" in printed
    assert "Invalid rating records detected: pig:p7" in printed

    cursor.execute(
        """
        SELECT player_id, game_type, stat_key, stat_value
        FROM player_game_stats
        ORDER BY player_id, game_type, stat_key
        """
    )
    remaining_stats = [tuple(row) for row in cursor.fetchall()]
    assert remaining_stats == [
        ("p1", "pig", "games_played", 5.0),
        ("p1", "pig", "high_score", 120.0),
        ("p1", "pig", "losses", 3.0),
        ("p1", "pig", "total_score", 240.0),
        ("p1", "pig", "wins", 2.0),
        ("p2", "twentyone", "games_played", 3.0),
        ("p2", "twentyone", "losses", 2.0),
        ("p2", "twentyone", "wins", 1.0),
        ("p4", "battle", "custom_deepest_wave_reached_high", 5.0),
        ("p4", "battle", "custom_most_enemies_defeated_high", 13.0),
        ("p4", "battle", "games_played", 2.0),
        ("p5", "lastcard", "wins", 8.0),
    ]

    cursor.execute(
        """
        SELECT player_id, game_type
        FROM player_ratings
        ORDER BY player_id, game_type
        """
    )
    assert [tuple(row) for row in cursor.fetchall()] == [
        ("p1", "pig"),
        ("p2", "twentyone"),
        ("p5", "lastcard"),
    ]


def test_prune_unsupported_leaderboard_data_empty_support_map_is_noop(db):
    cursor = db._conn.cursor()
    cursor.execute(
        """
        INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
        VALUES (?, ?, ?, ?)
        """,
        ("p1", "metalpipe", "games_played", 1),
    )
    cursor.execute(
        "INSERT INTO player_ratings (player_id, game_type, mu, sigma) VALUES (?, ?, ?, ?)",
        ("p1", "metalpipe", 30.0, 6.0),
    )
    db._conn.commit()

    counts = db.prune_unsupported_leaderboard_data({}, set())

    assert counts == {"player_game_stats": 0, "player_ratings": 0}
    cursor.execute("SELECT game_type, stat_key FROM player_game_stats")
    assert [tuple(row) for row in cursor.fetchall()] == [("metalpipe", "games_played")]
    cursor.execute("SELECT game_type FROM player_ratings")
    assert [row[0] for row in cursor.fetchall()] == ["metalpipe"]


def test_delete_user_cascades(db):
    db.create_user("Alice", "hash")
    alice = db.get_user("Alice")

    cursor = db._conn.cursor()

    # Insert fake data across all tables
    cursor.execute("INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value) VALUES (?, 'pig', 'wins', 1)", (alice.uuid,))
    cursor.execute("INSERT INTO player_ratings (player_id, game_type, mu, sigma) VALUES (?, 'pig', 25.0, 8.0)", (alice.uuid,))
    cursor.execute("INSERT INTO saved_tables (username, save_name, game_type, game_json, members_json, saved_at) VALUES (?, 'save', 'pig', '', '', '')", ("Alice",))
    cursor.execute("INSERT INTO bans (username, admin_username, reason_key, issued_at, expires_at) VALUES (?, 'admin', 'r', '', '')", ("Alice",))
    cursor.execute("INSERT INTO mutes (username, admin_username, reason, issued_at, expires_at) VALUES (?, 'admin', 'r', '', '')", ("Alice",))
    db._conn.commit()

    # Run delete
    assert db.delete_user("Alice") is True

    # Verify everything is gone
    cursor.execute("SELECT COUNT(*) FROM player_game_stats")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM player_ratings")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM saved_tables")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM bans")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM mutes")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM users")
    assert cursor.fetchone()[0] == 0


def test_delete_user_removes_checkpoint_with_only_a_reserved_seat(db):
    account = db.create_user("Reserved", "hash")
    cursor = db._conn.cursor()
    cursor.execute(
        """
        INSERT INTO tables (
            table_id, game_type, host, members_json, game_json, status
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "reserved-seat-table",
            "pig",
            "OtherHost",
            "[]",
            json.dumps(
                {
                    "players": [
                        {
                            "id": account.uuid,
                            "name": "Replacement Bot",
                            "is_bot": True,
                            "replaced_human": True,
                            "replaced_human_name": account.username,
                        }
                    ]
                }
            ),
            "playing",
        ),
    )

    assert db.delete_user(account.username) is True

    assert cursor.execute(
        "SELECT COUNT(*) FROM tables WHERE table_id = ?",
        ("reserved-seat-table",),
    ).fetchone()[0] == 0
