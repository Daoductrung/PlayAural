import pytest
import sqlite3
import json
import datetime
import os
from datetime import timedelta
from pathlib import Path
from server.persistence.database import (
    Database,
    DatabaseCleanupCategoryCode,
)
from server.persistence.retention import (
    ABANDONED_BACKUP_FRAGMENT_MINIMUM_AGE_SECONDS,
)


def _mark_backup_fragment_abandoned(path: Path) -> None:
    old_timestamp = (
        datetime.datetime.now().timestamp()
        - ABANDONED_BACKUP_FRAGMENT_MINIMUM_AGE_SECONDS
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
    finally:
        database.close()


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
        connection.execute("DROP TABLE moderation_reports")
        connection.execute("DROP TABLE global_chat_messages")
        connection.execute("DROP TABLE server_settings")
        connection.execute("PRAGMA application_id = 0")
        connection.execute("PRAGMA user_version = 0")
        connection.commit()
    finally:
        connection.close()
    return user.uuid


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
            "SELECT COUNT(*) FROM sqlite_schema WHERE name = 'moderation_reports'"
        ).fetchone()[0] == 0
    finally:
        backup.close()

    # A current database does not create repeated migration backups.
    database = Database(db_path)
    database.connect(migration_backup_dir=backup_dir)
    database.close()
    assert len(list(backup_dir.glob("*.sqlite3"))) == 1


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
    with pytest.raises(RuntimeError, match="simulated migration failure"):
        database.connect(migration_backup_dir=backup_dir)

    assert database._conn is None
    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute("PRAGMA application_id").fetchone()[0] == 0
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_schema WHERE name = 'moderation_reports'"
        ).fetchone()[0] == 0
    finally:
        connection.close()
    assert len(list(backup_dir.glob("*.sqlite3"))) == 1


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
            "SELECT COUNT(*) FROM sqlite_schema WHERE name = 'moderation_reports'"
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

    with pytest.raises(sqlite3.DatabaseError, match="missing required columns"):
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
            "SELECT COUNT(*) FROM sqlite_schema WHERE name = 'moderation_reports'"
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

    with pytest.raises(sqlite3.DatabaseError, match="missing required tables"):
        Database(db_path).connect()

    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_schema WHERE name = 'server_settings'"
        ).fetchone()[0] == 0
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

    assert counts == {"player_game_stats": 6, "player_ratings": 2}
    assert "Unsupported leaderboard stat keys detected" in printed
    assert "metalpipe:games_played" in printed
    assert "twentyone:total_score" in printed
    assert "Unsupported rating game types detected: blackjack, metalpipe" in printed

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
