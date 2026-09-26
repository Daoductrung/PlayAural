"""SQLite database for persistence."""

import logging
import math
import os
import shutil
import sqlite3
import time
import uuid as uuid_module
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

from ..messages.localization import DEFAULT_LOCALE, Localization
from ..chat_channels import MAX_CHAT_MESSAGE_LENGTH, normalize_global_chat_channel
from ..moderation.chat_history import GLOBAL_CHAT_HISTORY_SORT_ORDERS
from ..moderation.reports import (
    AUTOMATED_SPAM_REPORT_COOLDOWN_SECONDS,
    CLOSED_REPORT_STATUSES,
    MAX_MODERATION_QUERY_PAGE_SIZE,
    MAX_REPORT_DETAILS_LENGTH,
    MAX_REPORTS_PER_WINDOW,
    REPORT_CONTEXT_CODES,
    REPORT_CONTEXT_GLOBAL,
    REPORT_LIMIT_WINDOW_SECONDS,
    REPORT_ORIGIN_AUTOMATED_SPAM,
    REPORT_ORIGIN_MANUAL,
    REPORT_REASON_CODE_SET,
    REPORT_STATUS_SET,
    SAME_TARGET_REPORT_COOLDOWN_SECONDS,
    SYSTEM_REPORTER_USERNAME,
    SYSTEM_REPORTER_UUID,
    AutomatedSpamEvidence,
    ModerationReportSubmission,
)
from ..tables.table import Table
from ..users.identity import normalize_username, username_key
from .retention import (
    ABANDONED_BACKUP_FRAGMENT_MINIMUM_AGE_SECONDS,
    EXPIRED_BAN_RETENTION_DAYS,
    PENDING_FRIEND_REQUEST_RETENTION_DAYS,
    TRANSIENT_TABLE_CHECKPOINT_RETENTION_DAYS,
    USER_NOTIFICATION_RETENTION_DAYS,
)


_USER_RECORD_COLUMNS = (
    "id, username, password_hash, uuid, locale, preferences_json, "
    "trust_level, approved, email, bio, motd_version, gender, "
    "registration_date, last_login_date"
)


class DatabaseCleanupCategoryCode(str, Enum):
    """Stable codes for the complete safe-storage cleanup allowlist."""

    EXPIRED_TABLE_CHECKPOINTS = "expired_table_checkpoints"
    EXPIRED_PASSWORD_RESET_TOKENS = "expired_password_reset_tokens"
    EXPIRED_BANS = "expired_bans"
    STALE_PENDING_FRIEND_REQUESTS = "stale_pending_friend_requests"
    ORPHANED_FRIENDSHIPS = "orphaned_friendships"
    ORPHANED_USER_BLOCKS = "orphaned_user_blocks"
    STALE_USER_NOTIFICATIONS = "stale_user_notifications"
    ORPHANED_USER_NOTIFICATIONS = "orphaned_user_notifications"
    EXPIRED_MUTES = "expired_mutes"
    ORPHANED_MUTES = "orphaned_mutes"


@dataclass
class UserRecord:
    """A user record from the database."""

    id: int
    username: str
    password_hash: str
    uuid: str  # Persistent unique identifier for stats tracking
    locale: str = "en"
    preferences_json: str = "{}"
    trust_level: int = 1  # 1 = player, 2 = admin
    approved: bool = False  # Whether the account has been approved by an admin
    email: str = ""
    bio: str = ""
    motd_version: int = 0
    gender: str = "Not set"
    registration_date: str = ""
    last_login_date: str = ""


@dataclass(frozen=True)
class UsernameResolution:
    """Result of resolving one user-supplied username spelling."""

    user: UserRecord | None = None
    ambiguous: bool = False


@dataclass
class BanRecord:
    """A ban record from the database."""

    id: int
    username: str
    admin_username: str
    reason_key: str
    issued_at: str
    expires_at: str | None


@dataclass
class MuteRecord:
    """A mute record from the database."""

    id: int
    username: str
    admin_username: str
    reason: str
    issued_at: str
    expires_at: str | None


@dataclass(frozen=True)
class GlobalChatMessageRecord:
    """An accepted global-chat message retained for manual moderation."""

    id: int
    sender_uuid: str
    sender_username: str
    channel_code: str
    sent_at_utc: str
    message: str


@dataclass(frozen=True)
class GlobalChatSenderSummary:
    """One immutable sender identity represented in retained chat history."""

    sender_uuid: str
    sender_username: str
    message_count: int
    first_sent_at_utc: str
    last_sent_at_utc: str


@dataclass(frozen=True)
class ModerationReportRecord:
    """One persistent user report for later manual review."""

    id: int
    reporter_uuid: str
    reporter_username: str
    reported_uuid: str
    reported_username: str
    reported_at_utc: str
    reason_code: str
    details: str
    channel_code: str | None
    context_anchor_message_id: int | None
    status: str
    reviewed_by_uuid: str | None
    reviewed_by_username: str | None
    reviewed_at_utc: str | None
    origin_code: str
    context_code: str
    evidence_json: str | None


@dataclass(frozen=True)
class DatabaseCompactionResult:
    """Storage statistics from one completed SQLite VACUUM operation."""

    before_bytes: int
    after_bytes: int
    reclaimed_bytes: int
    before_free_pages: int
    after_free_pages: int


@dataclass(frozen=True)
class DatabaseBackupResult:
    """Metadata for one fully validated, durable SQLite backup snapshot."""

    path: Path
    size_bytes: int
    page_count: int
    created_at_utc: str
    incomplete_files_removed: int = 0
    incomplete_file_bytes_removed: int = 0


@dataclass(frozen=True)
class DatabaseCleanupCategoryResult:
    """One allowlisted storage-cleanup category and its row count."""

    code: str
    count: int
    retention_days: int | None = None


@dataclass(frozen=True)
class DatabaseStorageAnalysis:
    """Read-only snapshot of data eligible for safe storage cleanup."""

    analyzed_at_utc: str
    database_size_bytes: int
    page_size_bytes: int
    free_page_count: int
    categories: tuple[DatabaseCleanupCategoryResult, ...]
    incomplete_backup_file_count: int
    incomplete_backup_file_bytes: int
    invalid_timestamp_values: int

    @property
    def reusable_database_bytes(self) -> int:
        return self.page_size_bytes * self.free_page_count

    @property
    def total_candidate_records(self) -> int:
        return sum(category.count for category in self.categories)

    @property
    def has_candidates(self) -> bool:
        return bool(
            self.total_candidate_records or self.incomplete_backup_file_count
        )


@dataclass(frozen=True)
class DatabaseStorageCleanupResult:
    """Committed row deletions and resulting reusable SQLite space."""

    completed_at_utc: str
    database_size_bytes: int
    page_size_bytes: int
    free_pages_before: int
    free_pages_after: int
    categories: tuple[DatabaseCleanupCategoryResult, ...]
    invalid_timestamp_values: int

    @property
    def total_deleted_records(self) -> int:
        return sum(category.count for category in self.categories)

    @property
    def reusable_database_bytes(self) -> int:
        return self.page_size_bytes * self.free_pages_after


@dataclass(frozen=True)
class _DatabaseCleanupRule:
    """Internal allowlisted DELETE/COUNT rule shared by preview and cleanup."""

    code: DatabaseCleanupCategoryCode
    table: str
    predicate: str
    parameters: tuple[str, ...]
    retention_days: int | None = None


@dataclass
class SmtpConfig:
    """SMTP configuration from the database."""
    host: str
    port: int
    username: str
    password: str
    from_email: str
    from_name: str
    encryption_type: str  # 'none', 'ssl', 'tls'

@dataclass
class SavedTableRecord:
    """A saved table record from the database."""

    id: int
    username: str
    save_name: str
    game_type: str
    game_json: str
    members_json: str
    saved_at: str
    table_state_json: str = "{}"


class Database:
    """
    SQLite database for PlayAural persistence.

    Stores users and tables as specified in persistence.md.
    """

    # SQLite exposes corruption through message text rather than a dedicated
    # exception type. These markers are used only to give operators a clearer
    # diagnostic; startup never moves or replaces a suspect database.
    CORRUPT_DATABASE_MARKERS = (
        "database disk image is malformed",
        "file is not a database",
        "file is not a sqlite database",
        "not a database",
        "malformed database schema",
        "database integrity check failed",
    )
    SQLITE_SIDECAR_SUFFIXES = ("-wal", "-shm", "-journal")
    APPLICATION_ID = 0x50415552  # "PAUR"
    CURRENT_SCHEMA_VERSION = 1
    SCHEMA_TABLE_COLUMNS = {
        "bans": frozenset(
            {"id", "username", "admin_username", "reason_key", "issued_at", "expires_at"}
        ),
        "friendships": frozenset(
            {"requester_id", "receiver_id", "status", "created_at"}
        ),
        "game_result_players": frozenset(
            {"id", "result_id", "player_id", "player_name", "is_bot"}
        ),
        "game_results": frozenset(
            {"id", "game_type", "timestamp", "duration_ticks", "custom_data"}
        ),
        "global_chat_messages": frozenset(
            {
                "id",
                "sender_uuid",
                "sender_username",
                "channel_code",
                "sent_at_utc",
                "message",
            }
        ),
        "moderation_reports": frozenset(
            {
                "id",
                "reporter_uuid",
                "reporter_username",
                "reported_uuid",
                "reported_username",
                "reported_at_utc",
                "reason_code",
                "details",
                "channel_code",
                "context_anchor_message_id",
                "status",
                "reviewed_by_uuid",
                "reviewed_by_username",
                "reviewed_at_utc",
                "origin_code",
                "context_code",
                "evidence_json",
            }
        ),
        "motd": frozenset({"id", "version", "language", "message"}),
        "mutes": frozenset(
            {"id", "username", "admin_username", "reason", "issued_at", "expires_at"}
        ),
        "password_reset_tokens": frozenset(
            {"id", "user_uuid", "token_hash", "created_at", "expires_at"}
        ),
        "player_game_stats": frozenset(
            {"player_id", "game_type", "stat_key", "stat_value"}
        ),
        "player_ratings": frozenset(
            {"player_id", "game_type", "mu", "sigma"}
        ),
        "saved_tables": frozenset(
            {
                "id",
                "username",
                "save_name",
                "game_type",
                "game_json",
                "members_json",
                "table_state_json",
                "saved_at",
            }
        ),
        "server_settings": frozenset(
            {"setting_key", "value_json", "updated_at_utc"}
        ),
        "smtp_config": frozenset(
            {
                "id",
                "host",
                "port",
                "username",
                "password",
                "from_email",
                "from_name",
                "encryption_type",
            }
        ),
        "tables": frozenset(
            {
                "table_id",
                "game_type",
                "host",
                "members_json",
                "game_json",
                "status",
                "is_private",
                "table_state_json",
                "active_human_offline_elapsed",
                "checkpoint_kind",
                "checkpoint_created_at",
                "checkpoint_expires_at",
                "checkpoint_operation_id",
            }
        ),
        "user_blocks": frozenset({"blocker_id", "blocked_id", "created_at"}),
        "user_notifications": frozenset(
            {"id", "user_id", "source_username", "event_type", "created_at"}
        ),
        "users": frozenset(
            {
                "id",
                "username",
                "username_key",
                "password_hash",
                "uuid",
                "locale",
                "preferences_json",
                "trust_level",
                "approved",
                "email",
                "bio",
                "motd_version",
                "gender",
                "registration_date",
                "last_login_date",
            }
        ),
    }
    BACKUP_FILE_PREFIX = "PlayAural"
    BACKUP_FILE_SUFFIX = ".sqlite3"
    BACKUP_PAGE_BATCH_SIZE = 256
    MINIMUM_MAINTENANCE_FREE_BYTES = 16 * 1024 * 1024
    VACUUM_WORKING_SPACE_MULTIPLIER = 2
    INCOMPLETE_BACKUP_SUFFIXES = (
        f"{BACKUP_FILE_SUFFIX}.partial",
        f"{BACKUP_FILE_SUFFIX}.partial-wal",
        f"{BACKUP_FILE_SUFFIX}.partial-shm",
        f"{BACKUP_FILE_SUFFIX}.partial-journal",
    )

    def __init__(self, db_path: str | Path = "PlayAural.db"):
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    def connect(
        self,
        *,
        timeout: float = 30.0,
        migration_backup_dir: str | Path | None = None,
    ) -> None:
        """Connect, validate, and migrate the database without deleting data.

        Existing databases are opened fail-closed. A corrupt, foreign, partial,
        or newer-schema database is never moved, replaced, or rebuilt, and the
        exception is returned to the caller. Before the first versioned schema
        migration, a validated online backup is durably published. Retention
        cleanup is explicit and is never coupled to opening the database.
        """
        if self._conn is not None:
            raise RuntimeError("Database is already connected")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._validate_database_file_layout()
        existed_with_content = (
            self._is_file_database()
            and self.db_path.exists()
            and self.db_path.stat().st_size > 0
        )
        try:
            self._connect_once(
                timeout=timeout,
                existed_with_content=existed_with_content,
                migration_backup_dir=migration_backup_dir,
            )
        except BaseException:
            self.close()
            raise

    def _connect_once(
        self,
        *,
        timeout: float,
        existed_with_content: bool,
        migration_backup_dir: str | Path | None,
    ) -> None:
        # Keep the connection in SQLite autocommit mode. Multi-statement writes
        # use _transaction() below, so a failed operation cannot leave an
        # implicit transaction open and poison a later explicit BEGIN.
        self._conn = sqlite3.connect(
            str(self.db_path),
            timeout=timeout,
            isolation_level=None,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.create_function(
            "USERNAME_KEY",
            1,
            username_key,
            deterministic=True,
        )
        self._conn.execute(f"PRAGMA busy_timeout = {int(timeout * 1000)};")
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._conn.execute("PRAGMA synchronous = FULL;")
        if existed_with_content:
            # Validate the original file before any schema or journal-mode write.
            self._verify_connection_integrity(self._conn, full=True)
        self._prepare_schema(migration_backup_dir=migration_backup_dir)
        # Make the durability policy explicit rather than relying on SQLite's
        # build-time defaults. WAL protects committed work from process crashes,
        # while FULL synchronization asks the OS to flush commit-critical data
        # before SQLite reports success.
        self._conn.execute("PRAGMA journal_mode = WAL;")
        self._conn.execute("PRAGMA synchronous = FULL;")
        self._verify_connection_integrity(self._conn, full=True)

    @contextmanager
    def _transaction(
        self, *, immediate: bool = False
    ) -> Iterator[sqlite3.Cursor]:
        """Run an explicit, atomic transaction on the shared connection."""
        if self._conn is None:
            raise RuntimeError("Database is not connected")
        if self._conn.in_transaction:
            raise RuntimeError("Nested database transactions are not supported")

        cursor = self._conn.cursor()
        cursor.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
        try:
            yield cursor
            self._conn.commit()
        except BaseException:
            if self._conn.in_transaction:
                self._conn.rollback()
            raise

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def compact_database(self) -> DatabaseCompactionResult:
        """Rebuild the main SQLite file and return exact page-level results.

        VACUUM cannot run inside a transaction. The server calls this from an
        exclusive worker-owned connection only after event-loop database work
        has drained and the live connection has closed.
        """
        if self._conn is None:
            raise RuntimeError("Database is not connected")
        if self._conn.in_transaction:
            raise RuntimeError("Cannot compact the database during a transaction")

        self._verify_connection_integrity(self._conn, full=True)

        page_size_row = self._conn.execute("PRAGMA page_size").fetchone()
        before_pages_row = self._conn.execute("PRAGMA page_count").fetchone()
        before_free_row = self._conn.execute("PRAGMA freelist_count").fetchone()
        page_size = int(page_size_row[0])
        before_pages = int(before_pages_row[0])
        before_free_pages = int(before_free_row[0])

        if self._is_file_database():
            required_bytes = max(
                before_pages * page_size * self.VACUUM_WORKING_SPACE_MULTIPLIER,
                self.MINIMUM_MAINTENANCE_FREE_BYTES,
            )
            self._require_free_space(self.db_path.parent, required_bytes)

        self._conn.execute("VACUUM")
        self._verify_connection_integrity(self._conn, full=True)

        after_pages_row = self._conn.execute("PRAGMA page_count").fetchone()
        after_free_row = self._conn.execute("PRAGMA freelist_count").fetchone()
        after_pages = int(after_pages_row[0])
        after_free_pages = int(after_free_row[0])
        before_bytes = before_pages * page_size
        after_bytes = after_pages * page_size
        return DatabaseCompactionResult(
            before_bytes=before_bytes,
            after_bytes=after_bytes,
            reclaimed_bytes=max(0, before_bytes - after_bytes),
            before_free_pages=before_free_pages,
            after_free_pages=after_free_pages,
        )

    def backup_database(
        self,
        backup_dir: str | Path,
        *,
        purpose: str = "manual",
    ) -> DatabaseBackupResult:
        """Create, validate, flush, and atomically publish a SQLite backup.

        The SQLite online-backup API copies the logical database rather than
        copying the main file and sidecars independently. The destination is
        written under a unique temporary name, checked with SQLite's full
        integrity checker, flushed to stable storage, and only then renamed to
        its final name. A failed operation never publishes a partial backup.
        """
        if self._conn is None:
            raise RuntimeError("Database is not connected")
        if self._conn.in_transaction:
            raise RuntimeError("Cannot back up the database during a transaction")
        if not self._is_file_database():
            raise RuntimeError("Database backups require a file-backed database")

        safe_purpose = "".join(
            character if character.isalnum() or character == "-" else "-"
            for character in str(purpose).strip().lower()
        ).strip("-")
        if not safe_purpose:
            raise ValueError("Backup purpose must contain at least one safe character")

        self._verify_connection_integrity(self._conn, full=True)
        page_size = int(self._conn.execute("PRAGMA page_size").fetchone()[0])
        page_count = int(self._conn.execute("PRAGMA page_count").fetchone()[0])
        required_bytes = max(
            page_size * page_count,
            self.MINIMUM_MAINTENANCE_FREE_BYTES,
        )

        directory = Path(backup_dir).resolve()
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        incomplete_files_removed, incomplete_file_bytes_removed = (
            self._remove_incomplete_backups(directory)
        )
        self._require_free_space(directory, required_bytes)

        created_at = datetime.now(timezone.utc)
        timestamp = created_at.strftime("%Y%m%dT%H%M%S.%fZ")
        unique_suffix = uuid_module.uuid4().hex[:12]
        filename = (
            f"{self.BACKUP_FILE_PREFIX}-{safe_purpose}-{timestamp}-"
            f"{unique_suffix}{self.BACKUP_FILE_SUFFIX}"
        )
        final_path = directory / filename
        temporary_path = directory / f".{filename}.partial"
        destination: sqlite3.Connection | None = None

        try:
            destination = sqlite3.connect(
                str(temporary_path),
                timeout=30.0,
                isolation_level=None,
            )
            destination.create_function(
                "USERNAME_KEY",
                1,
                username_key,
                deterministic=True,
            )
            destination.execute("PRAGMA synchronous = FULL;")
            self._conn.backup(
                destination,
                pages=self.BACKUP_PAGE_BATCH_SIZE,
                sleep=0.05,
            )
            # Publish one self-contained file. A backup must never depend on a
            # temporary WAL sidecar that is not part of the atomic rename.
            destination.execute("PRAGMA journal_mode = DELETE;")
            self._verify_connection_integrity(destination, full=True)
            destination.close()
            destination = None

            self._flush_file_to_disk(temporary_path)
            temporary_path.replace(final_path)
            try:
                final_path.chmod(0o600)
            except OSError:
                logging.getLogger("playaural.db").warning(
                    "Could not restrict backup file permissions for %s",
                    final_path,
                    exc_info=True,
                )
            self._flush_directory_to_disk(directory)
            return DatabaseBackupResult(
                path=final_path,
                size_bytes=final_path.stat().st_size,
                page_count=page_count,
                created_at_utc=created_at.isoformat(),
                incomplete_files_removed=incomplete_files_removed,
                incomplete_file_bytes_removed=incomplete_file_bytes_removed,
            )
        except BaseException:
            if destination is not None:
                destination.close()
            for suffix in ("", "-wal", "-shm", "-journal"):
                partial_path = Path(f"{temporary_path}{suffix}")
                try:
                    partial_path.unlink(missing_ok=True)
                except OSError:
                    logging.getLogger("playaural.db").warning(
                        "Could not remove incomplete database backup %s",
                        partial_path,
                        exc_info=True,
                    )
            raise

    @classmethod
    def _incomplete_backup_files(cls, directory: Path) -> tuple[Path, ...]:
        """Return old regular unpublished PlayAural backup fragments only."""
        if not directory.exists():
            return ()
        if not directory.is_dir():
            raise NotADirectoryError(directory)

        prefix = f".{cls.BACKUP_FILE_PREFIX}-"
        oldest_active_timestamp = (
            time.time() - ABANDONED_BACKUP_FRAGMENT_MINIMUM_AGE_SECONDS
        )
        candidates: list[Path] = []
        for candidate in directory.iterdir():
            if candidate.is_symlink() or not candidate.is_file():
                continue
            if not candidate.name.startswith(prefix):
                continue
            if not candidate.name.endswith(cls.INCOMPLETE_BACKUP_SUFFIXES):
                continue
            try:
                if candidate.stat().st_mtime > oldest_active_timestamp:
                    continue
            except FileNotFoundError:
                continue
            candidates.append(candidate)
        return tuple(sorted(candidates, key=lambda path: path.name))

    @classmethod
    def _remove_incomplete_backups(cls, directory: Path) -> tuple[int, int]:
        """Remove unpublished fragments left by an interrupted prior backup.

        The caller must own PlayAural's exclusive maintenance barrier. Final
        backups never use these suffixes, so a completed recovery snapshot is
        not eligible for cleanup.
        """
        file_count = 0
        bytes_removed = 0
        for candidate in cls._incomplete_backup_files(directory):
            try:
                size_bytes = candidate.stat().st_size
                candidate.unlink()
            except FileNotFoundError:
                continue
            file_count += 1
            bytes_removed += size_bytes
        return file_count, bytes_removed

    @classmethod
    def _verify_connection_integrity(
        cls,
        connection: sqlite3.Connection,
        *,
        full: bool,
    ) -> None:
        pragma = "integrity_check" if full else "quick_check(1)"
        rows = connection.execute(f"PRAGMA {pragma}").fetchall()
        results = [str(row[0]) for row in rows] if rows else ["no result"]
        if results != ["ok"]:
            raise sqlite3.DatabaseError(
                "database integrity check failed: " + "; ".join(results)
            )
        foreign_key_error = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchone()
        if foreign_key_error is not None:
            details = ", ".join(str(value) for value in foreign_key_error)
            raise sqlite3.DatabaseError(
                f"database foreign key check failed: {details}"
            )

    @classmethod
    def _require_free_space(cls, directory: Path, required_bytes: int) -> None:
        available_bytes = shutil.disk_usage(directory).free
        if available_bytes < required_bytes:
            raise OSError(
                "Insufficient free disk space for safe database maintenance: "
                f"requires at least {required_bytes} bytes, "
                f"but {available_bytes} bytes are available"
            )

    @staticmethod
    def _flush_file_to_disk(path: Path) -> None:
        # Windows requires a writable file descriptor for _commit()/fsync.
        descriptor = os.open(path, os.O_RDWR)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    @staticmethod
    def _flush_directory_to_disk(path: Path) -> None:
        """Persist an atomic rename where the platform supports directory fsync."""
        try:
            descriptor = os.open(path, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(descriptor)
        except OSError:
            # Windows does not expose directory fsync through os.open. The
            # backup file itself has already been flushed with FileFlushBuffers.
            pass
        finally:
            os.close(descriptor)

    def _is_file_database(self) -> bool:
        return str(self.db_path) not in {":memory:", ""}

    @classmethod
    def _is_corruption_error(cls, exc: sqlite3.DatabaseError) -> bool:
        message = str(exc).lower()
        return any(
            marker in message for marker in cls.CORRUPT_DATABASE_MARKERS
        )

    def _database_sidecar_paths(self) -> list[Path]:
        return [
            Path(f"{self.db_path}{suffix}")
            for suffix in self.SQLITE_SIDECAR_SUFFIXES
        ]

    def _validate_database_file_layout(self) -> None:
        """Reject orphan SQLite sidecars before SQLite can create a new main file."""
        if not self._is_file_database():
            return
        sidecars = [path for path in self._database_sidecar_paths() if path.exists()]
        main_missing_or_empty = (
            not self.db_path.exists() or self.db_path.stat().st_size == 0
        )
        if main_missing_or_empty and sidecars:
            names = ", ".join(path.name for path in sidecars)
            raise sqlite3.DatabaseError(
                "SQLite sidecar files exist without a non-empty main database: "
                f"{names}. Refusing to create or replace the database."
            )
        if self.db_path.exists() and self.db_path.stat().st_size > 0:
            with self.db_path.open("rb") as database_file:
                header = database_file.read(16)
            if header != b"SQLite format 3\x00":
                raise sqlite3.DatabaseError(
                    "file is not a SQLite database; refusing to open or replace it"
                )

    def _prepare_schema(
        self,
        *,
        migration_backup_dir: str | Path | None,
    ) -> None:
        """Validate schema ownership and run the one supported migration path."""
        application_id = int(
            self._conn.execute("PRAGMA application_id").fetchone()[0]
        )
        schema_version = int(
            self._conn.execute("PRAGMA user_version").fetchone()[0]
        )
        schema_rows = self._conn.execute(
            """
            SELECT type, name
            FROM sqlite_schema
            WHERE name NOT LIKE 'sqlite_%'
            """
        ).fetchall()
        table_names = {
            str(row["name"])
            for row in schema_rows
            if str(row["type"]) == "table"
        }
        has_application_schema = bool(schema_rows)

        if application_id not in {0, self.APPLICATION_ID}:
            raise sqlite3.DatabaseError(
                "database application_id belongs to another application; "
                "refusing to modify it"
            )
        if schema_version > self.CURRENT_SCHEMA_VERSION:
            raise sqlite3.DatabaseError(
                "database schema version "
                f"{schema_version} is newer than supported version "
                f"{self.CURRENT_SCHEMA_VERSION}"
            )
        if schema_version < 0:
            raise sqlite3.DatabaseError(
                f"database schema version {schema_version} is invalid"
            )

        if schema_version == self.CURRENT_SCHEMA_VERSION:
            if application_id != self.APPLICATION_ID:
                raise sqlite3.DatabaseError(
                    "current-version database is missing the PlayAural "
                    "application identifier"
                )
            self._validate_current_schema()
            return

        # Version zero is the only unversioned production layout. Historical
        # tests and deployment tools may contain one isolated PlayAural table,
        # so recognize any non-empty subset of the canonical table names while
        # rejecting an unrelated SQLite schema.
        if schema_version != 0:
            raise sqlite3.DatabaseError(
                f"no migration path exists from schema version {schema_version}"
            )
        unknown_tables = table_names - set(self.SCHEMA_TABLE_COLUMNS)
        if has_application_schema and (not table_names or unknown_tables):
            detail = (
                ": " + ", ".join(sorted(unknown_tables))
                if unknown_tables
                else ""
            )
            raise sqlite3.DatabaseError(
                "unversioned SQLite database is not a recognizable PlayAural "
                f"database; refusing to modify it{detail}"
            )

        if has_application_schema and self._is_file_database():
            backup_directory = (
                Path(migration_backup_dir)
                if migration_backup_dir is not None
                else self.db_path.resolve().parent / "backups"
            )
            result = self.backup_database(
                backup_directory,
                purpose=(
                    f"pre-migration-v{schema_version}-to-"
                    f"v{self.CURRENT_SCHEMA_VERSION}"
                ),
            )
            logging.getLogger("playaural.db").warning(
                "Created pre-migration database backup at %s",
                result.path,
            )
            print(f"Created pre-migration database backup: {result.path}")

        self._create_tables()

    def _validate_current_schema(
        self,
        cursor: sqlite3.Cursor | None = None,
    ) -> None:
        """Require every current table and column without repairing drift."""
        executor = cursor if cursor is not None else self._conn
        application_id = int(executor.execute("PRAGMA application_id").fetchone()[0])
        schema_version = int(executor.execute("PRAGMA user_version").fetchone()[0])
        if application_id != self.APPLICATION_ID:
            raise sqlite3.DatabaseError(
                "database is missing the PlayAural application identifier"
            )
        if schema_version != self.CURRENT_SCHEMA_VERSION:
            raise sqlite3.DatabaseError(
                "database schema version changed unexpectedly during validation"
            )

        actual_tables = {
            str(row[0])
            for row in executor.execute(
                """
                SELECT name
                FROM sqlite_schema
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                """
            ).fetchall()
        }
        missing_tables = sorted(set(self.SCHEMA_TABLE_COLUMNS) - actual_tables)
        if missing_tables:
            raise sqlite3.DatabaseError(
                "database schema is missing required tables: "
                + ", ".join(missing_tables)
            )

        for table_name, required_columns in self.SCHEMA_TABLE_COLUMNS.items():
            rows = executor.execute(
                f"PRAGMA table_info({self._quote_identifier(table_name)})"
            ).fetchall()
            actual_columns = {str(row[1]) for row in rows}
            missing_columns = sorted(required_columns - actual_columns)
            if missing_columns:
                raise sqlite3.DatabaseError(
                    f"database table {table_name!r} is missing required columns: "
                    + ", ".join(missing_columns)
                )

        stale_username_key = executor.execute(
            """
            SELECT username
            FROM users
            WHERE username_key IS NULL
               OR username_key != USERNAME_KEY(username)
            LIMIT 1
            """
        ).fetchone()
        if stale_username_key is not None:
            raise sqlite3.DatabaseError(
                "database contains an invalid canonical username key for "
                f"{stale_username_key[0]!r}"
            )

    def _create_tables(self) -> None:
        """Create or migrate the schema in one atomic transaction."""
        self._conn.execute("PRAGMA foreign_keys = ON;")
        with self._transaction(immediate=True) as cursor:
            self._create_tables_in_transaction(cursor)
            cursor.execute(f"PRAGMA application_id = {self.APPLICATION_ID}")
            cursor.execute(f"PRAGMA user_version = {self.CURRENT_SCHEMA_VERSION}")
            self._validate_current_schema(cursor)

    def _create_tables_in_transaction(self, cursor: sqlite3.Cursor) -> None:
        """Create and migrate the schema inside the caller's transaction."""

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT COLLATE NOCASE UNIQUE NOT NULL,
                username_key TEXT NOT NULL,
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
        """)
        self._migrate_username_lookup_keys(cursor)

        # Tables table (game tables)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tables (
                table_id TEXT PRIMARY KEY,
                game_type TEXT NOT NULL,
                host TEXT NOT NULL,
                members_json TEXT NOT NULL,
                game_json TEXT,
                status TEXT DEFAULT 'waiting',
                is_private INTEGER NOT NULL DEFAULT 0,
                table_state_json TEXT NOT NULL DEFAULT '{}',
                active_human_offline_elapsed REAL,
                checkpoint_kind TEXT NOT NULL DEFAULT 'legacy',
                checkpoint_created_at TEXT NOT NULL DEFAULT '',
                checkpoint_expires_at TEXT,
                checkpoint_operation_id TEXT NOT NULL DEFAULT ''
            )
        """)
        self._ensure_column(
            cursor, "tables", "is_private", "INTEGER NOT NULL DEFAULT 0"
        )
        self._ensure_column(
            cursor,
            "tables",
            "table_state_json",
            "TEXT NOT NULL DEFAULT '{}'",
        )
        self._ensure_column(
            cursor,
            "tables",
            "active_human_offline_elapsed",
            "REAL",
        )
        self._ensure_column(
            cursor, "tables", "checkpoint_kind", "TEXT NOT NULL DEFAULT 'legacy'"
        )
        self._ensure_column(
            cursor, "tables", "checkpoint_created_at", "TEXT NOT NULL DEFAULT ''"
        )
        self._ensure_column(cursor, "tables", "checkpoint_expires_at", "TEXT")
        self._ensure_column(
            cursor,
            "tables",
            "checkpoint_operation_id",
            "TEXT NOT NULL DEFAULT ''",
        )

        # Saved tables (user-saved game states)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                save_name TEXT NOT NULL,
                game_type TEXT NOT NULL,
                game_json TEXT NOT NULL,
                members_json TEXT NOT NULL,
                table_state_json TEXT NOT NULL DEFAULT '{}',
                saved_at TEXT NOT NULL
            )
        """)
        self._ensure_column(
            cursor,
            "saved_tables",
            "table_state_json",
            "TEXT NOT NULL DEFAULT '{}'",
        )

        # Game results (for statistics)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration_ticks INTEGER,
                custom_data TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_result_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER REFERENCES game_results(id) ON DELETE CASCADE,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                is_bot INTEGER NOT NULL
            )
        """)

        # Indexes for game results
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_results_type
            ON game_results(game_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_results_timestamp
            ON game_results(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_result_players_player
            ON game_result_players(player_id)
        """)

        # Player ratings (for skill-based matchmaking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_ratings (
                player_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                mu REAL NOT NULL,
                sigma REAL NOT NULL,
                PRIMARY KEY (player_id, game_type)
            )
        """)

        # Bans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                admin_username TEXT NOT NULL,
                reason_key TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                expires_at TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bans_username
            ON bans(username)
        """)

        # Mutes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                admin_username TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT '',
                issued_at TEXT NOT NULL,
                expires_at TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mutes_username
            ON mutes(username)
        """)

        # Player game stats (aggregated stats for leaderboards)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_game_stats (
                player_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                stat_key TEXT NOT NULL,
                stat_value REAL NOT NULL,
                PRIMARY KEY (player_id, game_type, stat_key)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_game_stats_leaderboard
            ON player_game_stats(game_type, stat_key, stat_value DESC)
        """)


        # MOTD table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS motd (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                language TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        # Friendships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friendships (
                requester_id TEXT NOT NULL,
                receiver_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (requester_id, receiver_id)
            )
        """)

        # Directional user blocks. UUIDs keep relationships stable even if
        # display-name handling evolves; account deletion and explicit cleanup
        # remove rows because the legacy users.uuid column is not a
        # foreign-key target.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_blocks (
                blocker_id TEXT NOT NULL,
                blocked_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (blocker_id, blocked_id),
                CHECK (blocker_id != blocked_id)
            )
        """)

        # User Notifications table (offline alerts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                source_username TEXT NOT NULL,
                event_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Accepted global-chat messages are retained as immutable moderation
        # evidence until a developer explicitly clears them. UUID and username
        # snapshots deliberately do not reference users: account deletion must
        # not turn historical evidence into a broken foreign-key relationship.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS global_chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_uuid TEXT NOT NULL,
                sender_username TEXT NOT NULL,
                channel_code TEXT NOT NULL,
                sent_at_utc TEXT NOT NULL,
                message TEXT NOT NULL,
                CHECK (sender_uuid != ''),
                CHECK (sender_username != ''),
                CHECK (channel_code != ''),
                CHECK (message != '')
            )
        """)

        # Reports are immutable identity/evidence snapshots with no user-table
        # foreign keys. Manual cleanup owns their retention, so deleting an
        # account cannot erase a pending review or orphan a constrained row.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moderation_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_uuid TEXT NOT NULL,
                reporter_username TEXT NOT NULL,
                reported_uuid TEXT NOT NULL,
                reported_username TEXT NOT NULL,
                reported_at_utc TEXT NOT NULL,
                reason_code TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                channel_code TEXT,
                context_anchor_message_id INTEGER
                    REFERENCES global_chat_messages(id) ON DELETE SET NULL,
                status TEXT NOT NULL DEFAULT 'open',
                reviewed_by_uuid TEXT,
                reviewed_by_username TEXT,
                reviewed_at_utc TEXT,
                origin_code TEXT NOT NULL,
                context_code TEXT NOT NULL,
                evidence_json TEXT,
                CHECK (reporter_uuid != ''),
                CHECK (reported_uuid != ''),
                CHECK (reporter_uuid != reported_uuid),
                CHECK (status IN ('open', 'reviewed', 'dismissed', 'actioned')),
                CHECK (origin_code IN ('manual', 'automated_spam')),
                CHECK (context_code IN ('global', 'table')),
                CHECK (
                    (origin_code = 'manual'
                        AND context_code = 'global'
                        AND evidence_json IS NULL)
                    OR
                    (origin_code = 'automated_spam'
                        AND evidence_json IS NOT NULL
                        AND evidence_json != '')
                ),
                CHECK (
                    context_code != 'table'
                    OR (channel_code IS NULL AND context_anchor_message_id IS NULL)
                ),
                CHECK (
                    origin_code != 'automated_spam'
                    OR context_code != 'global'
                    OR channel_code IS NOT NULL
                )
            )
        """)

        # Small server-wide feature settings persist independently of any
        # account. Rows live until explicitly changed or the database itself
        # is removed, so account deletion requires no cleanup and cannot leave
        # orphaned records.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_settings (
                setting_key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL,
                CHECK (setting_key != '')
            )
        """)

        # SMTP Configuration table (single row expected)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smtp_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                host TEXT NOT NULL DEFAULT '',
                port INTEGER NOT NULL DEFAULT 587,
                username TEXT NOT NULL DEFAULT '',
                password TEXT NOT NULL DEFAULT '',
                from_email TEXT NOT NULL DEFAULT '',
                from_name TEXT NOT NULL DEFAULT '',
                encryption_type TEXT NOT NULL DEFAULT 'tls'
            )
        """)

        # Password Reset Tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_uuid TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reset_tokens_user_uuid
            ON password_reset_tokens(user_uuid)
        """)

        # Additional indexes for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_uuid
            ON users(uuid)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username_key
            ON users(username_key)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_saved_tables_user_saved_at
            ON saved_tables(username, saved_at DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tables_checkpoint_expires
            ON tables(checkpoint_expires_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_friendships_receiver_status_created
            ON friendships(receiver_id, status, created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_global_chat_messages_sender_time
            ON global_chat_messages(sender_uuid, sent_at_utc DESC, id DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_global_chat_messages_sender_channel_time
            ON global_chat_messages(
                sender_uuid, channel_code, sent_at_utc DESC, id DESC
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_global_chat_messages_channel_time
            ON global_chat_messages(channel_code, sent_at_utc DESC, id DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_global_chat_messages_time
            ON global_chat_messages(sent_at_utc DESC, id DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_global_chat_messages_username_time
            ON global_chat_messages(
                USERNAME_KEY(sender_username), sent_at_utc DESC, id DESC
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_moderation_reports_status_time
            ON moderation_reports(status, reported_at_utc DESC, id DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_moderation_reports_reported_time
            ON moderation_reports(reported_uuid, reported_at_utc DESC, id DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_moderation_reports_reporter_time
            ON moderation_reports(reporter_uuid, reported_at_utc DESC, id DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_moderation_reports_reporter_target_time
            ON moderation_reports(
                reporter_uuid, reported_uuid, reported_at_utc DESC, id DESC
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_moderation_reports_origin_target_context_time
            ON moderation_reports(
                origin_code,
                reported_uuid,
                context_code,
                reported_at_utc DESC,
                id DESC
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_blocks_blocked
            ON user_blocks(blocked_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_result_players_result
            ON game_result_players(result_id)
        """)

    def _ensure_column(
        self,
        cursor: sqlite3.Cursor,
        table_name: str,
        column_name: str,
        definition: str,
    ) -> None:
        """Add a missing column to an existing SQLite table."""
        cursor.execute(f"PRAGMA table_info({self._quote_identifier(table_name)})")
        columns = {row["name"] for row in cursor.fetchall()}
        if column_name in columns:
            return
        cursor.execute(
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"ADD COLUMN {self._quote_identifier(column_name)} {definition}"
        )

    def _migrate_username_lookup_keys(self, cursor: sqlite3.Cursor) -> None:
        """Install and backfill the canonical lookup column for older databases.

        This method and its single call are the complete compatibility bridge.
        Normal runtime queries rely directly on the populated column. Once all
        supported installations are known to contain it, this method and call
        can be removed together; the column, index, and write path remain part
        of the permanent schema.

        The index is deliberately non-unique. Historical databases can contain
        Unicode names that SQLite's ASCII-only NOCASE collation considered
        distinct. Resolution handles those legacy collisions safely while new
        registrations reject creating more of them.
        """
        self._ensure_column(cursor, "users", "username_key", "TEXT")
        stale_predicate = (
            "WHERE username_key IS NULL "
            "OR username_key != USERNAME_KEY(username)"
        )
        cursor.execute(f"SELECT 1 FROM users {stale_predicate} LIMIT 1")
        if cursor.fetchone() is not None:
            cursor.execute(
                "UPDATE users SET username_key = USERNAME_KEY(username) "
                f"{stale_predicate}"
            )

    @staticmethod
    def _storage_cleanup_rules(
        reference_time: datetime,
    ) -> tuple[_DatabaseCleanupRule, ...]:
        """Build the single allowlist used by cleanup preview and execution.

        The predicates deliberately preserve malformed timestamps rather than
        guessing whether a record has expired. Historical game results, saved
        tables, chat history, moderation reports, and compatibility data do not
        appear here and therefore cannot be removed by storage cleanup.
        """
        now = reference_time.isoformat()
        checkpoint_cutoff = (
            reference_time
            - timedelta(days=TRANSIENT_TABLE_CHECKPOINT_RETENTION_DAYS)
        ).isoformat()
        ban_cutoff = (
            reference_time - timedelta(days=EXPIRED_BAN_RETENTION_DAYS)
        ).isoformat()
        pending_request_cutoff = (
            reference_time
            - timedelta(days=PENDING_FRIEND_REQUEST_RETENTION_DAYS)
        ).isoformat()
        notification_cutoff = (
            reference_time - timedelta(days=USER_NOTIFICATION_RETENTION_DAYS)
        ).isoformat()

        expired_checkpoint = """
            (
                checkpoint_expires_at IS NOT NULL
                AND julianday(checkpoint_expires_at) IS NOT NULL
                AND julianday(checkpoint_expires_at) <= julianday(?)
            )
            OR (
                checkpoint_expires_at IS NULL
                AND
                checkpoint_created_at != ''
                AND julianday(checkpoint_created_at) IS NOT NULL
                AND julianday(checkpoint_created_at) < julianday(?)
            )
        """
        stale_request = """
            status = 'pending'
            AND julianday(created_at) IS NOT NULL
            AND julianday(created_at) < julianday(?)
        """
        stale_notification = """
            julianday(created_at) IS NOT NULL
            AND julianday(created_at) < julianday(?)
        """
        expired_mute = """
            expires_at IS NOT NULL
            AND julianday(expires_at) IS NOT NULL
            AND julianday(expires_at) <= julianday(?)
        """

        return (
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.EXPIRED_TABLE_CHECKPOINTS,
                "tables",
                expired_checkpoint,
                (now, checkpoint_cutoff),
            ),
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.EXPIRED_PASSWORD_RESET_TOKENS,
                "password_reset_tokens",
                """
                    julianday(expires_at) IS NOT NULL
                    AND julianday(expires_at) <= julianday(?)
                """,
                (now,),
            ),
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.EXPIRED_BANS,
                "bans",
                """
                    expires_at IS NOT NULL
                    AND julianday(expires_at) IS NOT NULL
                    AND julianday(expires_at) < julianday(?)
                """,
                (ban_cutoff,),
                EXPIRED_BAN_RETENTION_DAYS,
            ),
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.STALE_PENDING_FRIEND_REQUESTS,
                "friendships",
                stale_request,
                (pending_request_cutoff,),
                PENDING_FRIEND_REQUEST_RETENTION_DAYS,
            ),
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.ORPHANED_FRIENDSHIPS,
                "friendships",
                f"""
                    NOT ({stale_request})
                    AND (
                        NOT EXISTS (
                            SELECT 1 FROM users
                            WHERE users.uuid = friendships.requester_id
                        )
                        OR NOT EXISTS (
                            SELECT 1 FROM users
                            WHERE users.uuid = friendships.receiver_id
                        )
                    )
                """,
                (pending_request_cutoff,),
            ),
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.ORPHANED_USER_BLOCKS,
                "user_blocks",
                """
                    NOT EXISTS (
                        SELECT 1 FROM users
                        WHERE users.uuid = user_blocks.blocker_id
                    )
                    OR NOT EXISTS (
                        SELECT 1 FROM users
                        WHERE users.uuid = user_blocks.blocked_id
                    )
                """,
                (),
            ),
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.STALE_USER_NOTIFICATIONS,
                "user_notifications",
                stale_notification,
                (notification_cutoff,),
                USER_NOTIFICATION_RETENTION_DAYS,
            ),
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.ORPHANED_USER_NOTIFICATIONS,
                "user_notifications",
                f"""
                    NOT ({stale_notification})
                    AND (
                        NOT EXISTS (
                            SELECT 1 FROM users
                            WHERE users.uuid = user_notifications.user_id
                        )
                        OR NOT EXISTS (
                            SELECT 1 FROM users
                            WHERE users.username =
                                user_notifications.source_username COLLATE BINARY
                        )
                    )
                """,
                (notification_cutoff,),
            ),
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.EXPIRED_MUTES,
                "mutes",
                expired_mute,
                (now,),
            ),
            _DatabaseCleanupRule(
                DatabaseCleanupCategoryCode.ORPHANED_MUTES,
                "mutes",
                f"""
                    NOT ({expired_mute})
                    AND NOT EXISTS (
                        SELECT 1 FROM users
                        WHERE users.username = mutes.username COLLATE BINARY
                    )
                """,
                (now,),
            ),
        )

    def _storage_cleanup_category_counts(
        self,
        rules: tuple[_DatabaseCleanupRule, ...],
    ) -> tuple[DatabaseCleanupCategoryResult, ...]:
        cursor = self._conn.cursor()
        results: list[DatabaseCleanupCategoryResult] = []
        for rule in rules:
            cursor.execute(
                f"SELECT COUNT(*) FROM {rule.table} WHERE {rule.predicate}",
                rule.parameters,
            )
            results.append(
                DatabaseCleanupCategoryResult(
                    rule.code.value,
                    int(cursor.fetchone()[0]),
                    rule.retention_days,
                )
            )
        return tuple(results)

    def _count_invalid_cleanup_timestamps(self) -> int:
        """Count malformed retention timestamps that cleanup will preserve."""
        timestamp_fields = (
            ("tables", "checkpoint_created_at", "checkpoint_created_at != ''"),
            ("tables", "checkpoint_expires_at", "checkpoint_expires_at IS NOT NULL"),
            ("password_reset_tokens", "expires_at", "expires_at IS NOT NULL"),
            ("bans", "expires_at", "expires_at IS NOT NULL"),
            (
                "friendships",
                "created_at",
                "status = 'pending' AND created_at != ''",
            ),
            ("user_notifications", "created_at", "created_at != ''"),
            ("mutes", "expires_at", "expires_at IS NOT NULL"),
        )
        cursor = self._conn.cursor()
        total = 0
        for table, column, present_predicate in timestamp_fields:
            cursor.execute(
                f"""
                SELECT COUNT(*) FROM {table}
                WHERE {present_predicate} AND julianday({column}) IS NULL
                """
            )
            total += int(cursor.fetchone()[0])
        return total

    def analyze_storage_cleanup(
        self,
        backup_dir: str | Path,
        *,
        reference_time: datetime | None = None,
    ) -> DatabaseStorageAnalysis:
        """Preview the exact allowlisted cleanup set without changing storage."""
        if self._conn is None:
            raise RuntimeError("Database is not connected")
        if self._conn.in_transaction:
            raise RuntimeError("Cannot analyze storage during a transaction")

        reference = reference_time or datetime.now()
        incomplete_files = self._incomplete_backup_files(Path(backup_dir).resolve())
        incomplete_file_bytes = 0
        retained_incomplete_files = 0
        for candidate in incomplete_files:
            try:
                incomplete_file_bytes += candidate.stat().st_size
            except FileNotFoundError:
                continue
            retained_incomplete_files += 1

        with self._transaction() as cursor:
            page_size = int(cursor.execute("PRAGMA page_size").fetchone()[0])
            page_count = int(cursor.execute("PRAGMA page_count").fetchone()[0])
            free_page_count = int(
                cursor.execute("PRAGMA freelist_count").fetchone()[0]
            )
            categories = self._storage_cleanup_category_counts(
                self._storage_cleanup_rules(reference)
            )
            invalid_timestamp_values = self._count_invalid_cleanup_timestamps()
        return DatabaseStorageAnalysis(
            analyzed_at_utc=datetime.now(timezone.utc).isoformat(),
            database_size_bytes=page_size * page_count,
            page_size_bytes=page_size,
            free_page_count=free_page_count,
            categories=categories,
            incomplete_backup_file_count=retained_incomplete_files,
            incomplete_backup_file_bytes=incomplete_file_bytes,
            invalid_timestamp_values=invalid_timestamp_values,
        )

    def clean_storage(
        self,
        *,
        reference_time: datetime | None = None,
    ) -> DatabaseStorageCleanupResult:
        """Atomically delete only records covered by the safe cleanup allowlist."""
        if self._conn is None:
            raise RuntimeError("Database is not connected")
        if self._conn.in_transaction:
            raise RuntimeError("Cannot clean storage during a transaction")

        self._verify_connection_integrity(self._conn, full=True)
        reference = reference_time or datetime.now()
        rules = self._storage_cleanup_rules(reference)
        page_size = int(self._conn.execute("PRAGMA page_size").fetchone()[0])
        page_count = int(self._conn.execute("PRAGMA page_count").fetchone()[0])
        database_size_bytes = page_size * page_count
        free_pages_before = int(
            self._conn.execute("PRAGMA freelist_count").fetchone()[0]
        )
        if self._is_file_database():
            self._require_free_space(
                self.db_path.parent,
                max(database_size_bytes, self.MINIMUM_MAINTENANCE_FREE_BYTES),
            )
        deleted: list[DatabaseCleanupCategoryResult] = []

        self._conn.execute("PRAGMA foreign_keys = ON")
        with self._transaction(immediate=True) as cursor:
            for rule in rules:
                cursor.execute(
                    f"DELETE FROM {rule.table} WHERE {rule.predicate}",
                    rule.parameters,
                )
                deleted.append(
                    DatabaseCleanupCategoryResult(
                        rule.code.value,
                        cursor.rowcount,
                        rule.retention_days,
                    )
                )

            # Validate the exact uncommitted result so any structural or
            # foreign-key failure rolls the complete allowlisted delete set
            # back instead of publishing a partially trusted state.
            self._verify_connection_integrity(self._conn, full=True)

        self._verify_connection_integrity(self._conn, full=True)
        free_pages_after = int(
            self._conn.execute("PRAGMA freelist_count").fetchone()[0]
        )
        result = DatabaseStorageCleanupResult(
            completed_at_utc=datetime.now(timezone.utc).isoformat(),
            database_size_bytes=database_size_bytes,
            page_size_bytes=page_size,
            free_pages_before=free_pages_before,
            free_pages_after=free_pages_after,
            categories=tuple(deleted),
            invalid_timestamp_values=self._count_invalid_cleanup_timestamps(),
        )
        logging.getLogger("playaural.db.cleanup").info(
            "Storage cleanup deleted %d records; categories: %s",
            result.total_deleted_records,
            self._format_cleanup_counts(
                {category.code: category.count for category in result.categories}
            ),
        )
        return result

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        """Quote a SQLite identifier discovered from the local schema."""
        return '"' + identifier.replace('"', '""') + '"'

    def _user_table_names(self, cursor: sqlite3.Cursor) -> list[str]:
        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        )
        return [row["name"] for row in cursor.fetchall()]

    def _table_columns(self, cursor: sqlite3.Cursor, table_name: str) -> set[str]:
        cursor.execute(f"PRAGMA table_info({self._quote_identifier(table_name)})")
        return {row["name"] for row in cursor.fetchall()}

    def _game_type_table_names(self, cursor: sqlite3.Cursor) -> list[str]:
        """Return tables that are directly scoped by a game_type column."""
        return [
            table_name
            for table_name in self._user_table_names(cursor)
            if "game_type" in self._table_columns(cursor, table_name)
        ]

    def _game_result_child_tables(self, cursor: sqlite3.Cursor) -> list[tuple[str, str]]:
        """Return (table, column) pairs that reference game_results.id."""
        result: list[tuple[str, str]] = []
        for table_name in self._user_table_names(cursor):
            cursor.execute(
                f"PRAGMA foreign_key_list({self._quote_identifier(table_name)})"
            )
            for row in cursor.fetchall():
                if row["table"] == "game_results" and row["to"] == "id":
                    result.append((table_name, row["from"]))
        return result

    @staticmethod
    def _format_cleanup_counts(counts: dict[str, int]) -> str:
        if not counts:
            return "none"
        return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))

    def prune_unregistered_game_data(
        self,
        valid_game_types: set[str] | list[str] | tuple[str, ...],
    ) -> dict[str, int]:
        """Delete persisted data for game types that are no longer registered.

        This is intentionally allow-list based: only rows whose game_type is
        outside the current registry are removed, and an empty registry is a
        no-op to avoid destructive cleanup during a startup/import failure.
        """
        valid = sorted({game_type for game_type in valid_game_types if game_type})
        logger = logging.getLogger("playaural.db.prune")
        cursor = self._conn.cursor()
        self._conn.execute("PRAGMA foreign_keys = ON;")

        game_type_tables = self._game_type_table_names(cursor)
        game_result_children = self._game_result_child_tables(cursor)
        checked_tables = sorted(
            set(game_type_tables) | {table for table, _ in game_result_children}
        )
        counts = {table: 0 for table in checked_tables}
        for table, _ in game_result_children:
            counts.setdefault(f"orphaned_{table}", 0)

        startup_scan_msg = (
            "Database Pruning: Checking unregistered game data "
            f"against {len(valid)} registered games. "
            f"Tables checked: {', '.join(checked_tables) if checked_tables else 'none'}."
        )
        logger.info(startup_scan_msg)
        print(startup_scan_msg)

        if not valid:
            skip_msg = (
                "Database Pruning: Skipped unregistered-game cleanup because "
                "the registered game list was empty."
            )
            logger.warning(skip_msg)
            print(skip_msg)
            return counts

        placeholders = ", ".join("?" for _ in valid)
        not_registered = f"game_type NOT IN ({placeholders})"
        params = tuple(valid)
        stale_game_types: set[str] = set()
        for table in game_type_tables:
            cursor.execute(
                f"""
                SELECT DISTINCT game_type
                FROM {self._quote_identifier(table)}
                WHERE {not_registered}
                """,
                params,
            )
            stale_game_types.update(
                row["game_type"] for row in cursor.fetchall() if row["game_type"]
            )

        stale_label = ", ".join(sorted(stale_game_types)) if stale_game_types else "none"
        logger.info(
            "Database Pruning: Unregistered game types detected: %s",
            stale_label,
        )
        print(f"Database Pruning: Unregistered game types detected: {stale_label}.")

        with self._transaction(immediate=True) as cursor:
            if "game_results" in game_type_tables:
                for child_table, child_column in game_result_children:
                    cursor.execute(
                        f"""
                        DELETE FROM {self._quote_identifier(child_table)}
                        WHERE {self._quote_identifier(child_column)} IN (
                            SELECT id
                            FROM game_results
                            WHERE {not_registered}
                        )
                        """,
                        params,
                    )
                    counts[child_table] += cursor.rowcount

            direct_tables = [table for table in game_type_tables if table != "game_results"]
            for table in direct_tables:
                cursor.execute(
                    f"""
                    DELETE FROM {self._quote_identifier(table)}
                    WHERE {not_registered}
                    """,
                    params,
                )
                counts[table] += cursor.rowcount

            if "game_results" in game_type_tables:
                cursor.execute(
                    f"DELETE FROM game_results WHERE {not_registered}",
                    params,
                )
                counts["game_results"] += cursor.rowcount

            for child_table, child_column in game_result_children:
                orphan_key = f"orphaned_{child_table}"
                cursor.execute(
                    f"""
                    DELETE FROM {self._quote_identifier(child_table)}
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM game_results
                        WHERE game_results.id =
                            {self._quote_identifier(child_table)}.{self._quote_identifier(child_column)}
                    )
                    """
                )
                counts[orphan_key] += cursor.rowcount

        total_deleted = sum(counts.values())
        detail = self._format_cleanup_counts(counts)
        logger.info(
            "Database Pruning: Unregistered-game cleanup removed %d rows. Details: %s",
            total_deleted,
            detail,
        )
        print(
            "Database Pruning: Unregistered-game cleanup removed "
            f"{total_deleted} rows. Details: {detail}."
        )

        return counts

    def prune_unsupported_leaderboard_data(
        self,
        supported_stat_keys_by_game: dict[str, set[str]],
        rating_game_types: set[str] | list[str] | tuple[str, ...],
    ) -> dict[str, int]:
        """Delete leaderboard aggregates no longer supported by registered games.

        This cleanup is intentionally scoped to derived leaderboard tables. It
        does not alter historical game results, saved tables, or any other game
        data. An empty support map is a no-op to avoid destructive cleanup during
        a startup/import failure.
        """
        supported = {
            game_type: set(stat_keys)
            for game_type, stat_keys in supported_stat_keys_by_game.items()
            if game_type
        }
        rating_supported = {game_type for game_type in rating_game_types if game_type}
        logger = logging.getLogger("playaural.db.prune")
        counts = {"player_game_stats": 0, "player_ratings": 0}

        startup_scan_msg = (
            "Database Pruning: Checking unsupported leaderboard data "
            f"for {len(supported)} registered games. "
            "Tables checked: player_game_stats, player_ratings."
        )
        logger.info(startup_scan_msg)
        print(startup_scan_msg)

        if not supported:
            skip_msg = (
                "Database Pruning: Skipped unsupported-leaderboard cleanup because "
                "the leaderboard support map was empty."
            )
            logger.warning(skip_msg)
            print(skip_msg)
            return counts

        cursor = self._conn.cursor()
        unsupported_stat_pairs: list[tuple[str, str]] = []
        cursor.execute(
            """
            SELECT DISTINCT game_type, stat_key
            FROM player_game_stats
            ORDER BY game_type, stat_key
            """
        )
        for row in cursor.fetchall():
            game_type = row["game_type"]
            stat_key = row["stat_key"]
            if game_type in supported and stat_key not in supported[game_type]:
                unsupported_stat_pairs.append((game_type, stat_key))

        cursor.execute(
            """
            SELECT DISTINCT game_type
            FROM player_ratings
            ORDER BY game_type
            """
        )
        unsupported_rating_types = [
            row["game_type"]
            for row in cursor.fetchall()
            if row["game_type"] in supported
            and row["game_type"] not in rating_supported
        ]

        if unsupported_stat_pairs:
            stat_label = ", ".join(
                f"{game_type}:{stat_key}"
                for game_type, stat_key in unsupported_stat_pairs
            )
        else:
            stat_label = "none"
        rating_label = (
            ", ".join(unsupported_rating_types)
            if unsupported_rating_types
            else "none"
        )
        logger.info(
            "Database Pruning: Unsupported leaderboard stat keys detected: %s",
            stat_label,
        )
        logger.info(
            "Database Pruning: Unsupported rating game types detected: %s",
            rating_label,
        )
        print(f"Database Pruning: Unsupported leaderboard stat keys detected: {stat_label}.")
        print(f"Database Pruning: Unsupported rating game types detected: {rating_label}.")

        with self._transaction(immediate=True) as cursor:
            for game_type, stat_key in unsupported_stat_pairs:
                cursor.execute(
                    """
                    DELETE FROM player_game_stats
                    WHERE game_type = ? AND stat_key = ?
                    """,
                    (game_type, stat_key),
                )
                counts["player_game_stats"] += cursor.rowcount

            for game_type in unsupported_rating_types:
                cursor.execute(
                    "DELETE FROM player_ratings WHERE game_type = ?",
                    (game_type,),
                )
                counts["player_ratings"] += cursor.rowcount

        total_deleted = sum(counts.values())
        detail = self._format_cleanup_counts(counts)
        logger.info(
            "Database Pruning: Unsupported-leaderboard cleanup removed %d rows. Details: %s",
            total_deleted,
            detail,
        )
        print(
            "Database Pruning: Unsupported-leaderboard cleanup removed "
            f"{total_deleted} rows. Details: {detail}."
        )

        return counts

    # Global-chat moderation records

    @staticmethod
    def _global_chat_message_from_row(
        row: sqlite3.Row,
    ) -> GlobalChatMessageRecord:
        return GlobalChatMessageRecord(
            id=int(row["id"]),
            sender_uuid=str(row["sender_uuid"]),
            sender_username=str(row["sender_username"]),
            channel_code=str(row["channel_code"]),
            sent_at_utc=str(row["sent_at_utc"]),
            message=str(row["message"]),
        )

    def add_global_chat_message(
        self,
        sender_uuid: str,
        sender_username: str,
        channel_code: str,
        message: str,
    ) -> GlobalChatMessageRecord:
        """Persist one accepted global message before it is broadcast."""
        normalized_uuid = str(sender_uuid or "").strip()
        normalized_username = str(sender_username or "").strip()
        normalized_channel = normalize_global_chat_channel(channel_code)
        if not normalized_uuid or not normalized_username:
            raise ValueError("Global chat messages require a sender identity")
        if normalized_channel is None:
            raise ValueError("Global chat messages require a supported channel")
        if not isinstance(message, str) or not message or message != message.strip():
            raise ValueError("Global chat messages must contain canonical text")
        if len(message) > MAX_CHAT_MESSAGE_LENGTH:
            raise ValueError("Global chat message exceeds the protocol limit")

        sent_at_utc = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO global_chat_messages (
                sender_uuid,
                sender_username,
                channel_code,
                sent_at_utc,
                message
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                normalized_uuid,
                normalized_username,
                normalized_channel,
                sent_at_utc,
                message,
            ),
        )
        return GlobalChatMessageRecord(
            id=int(cursor.lastrowid),
            sender_uuid=normalized_uuid,
            sender_username=normalized_username,
            channel_code=normalized_channel,
            sent_at_utc=sent_at_utc,
            message=message,
        )

    def get_global_chat_message(
        self, message_id: int
    ) -> GlobalChatMessageRecord | None:
        """Return one retained global-chat message by stable ID."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT id, sender_uuid, sender_username, channel_code,
                   sent_at_utc, message
            FROM global_chat_messages
            WHERE id = ?
            """,
            (int(message_id),),
        )
        row = cursor.fetchone()
        return self._global_chat_message_from_row(row) if row else None

    def count_global_chat_messages(
        self,
        *,
        sender_uuid: str | None = None,
        channel_code: str | None = None,
        started_at_utc: str | None = None,
        ended_before_utc: str | None = None,
    ) -> int:
        """Count retained global messages using indexed moderation filters."""
        where, params = self._global_chat_message_filter(
            sender_uuid=sender_uuid,
            channel_code=channel_code,
            started_at_utc=started_at_utc,
            ended_before_utc=ended_before_utc,
        )
        query = "SELECT COUNT(*) AS count FROM global_chat_messages"
        if where:
            query += " WHERE " + " AND ".join(where)
        row = self._conn.execute(query, params).fetchone()
        return int(row["count"] if row else 0)

    @staticmethod
    def _normalize_moderation_utc_boundary(value: str, field_name: str) -> str:
        """Validate one query boundary and return canonical UTC ISO text."""
        try:
            parsed = datetime.fromisoformat(str(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} must be an ISO timestamp") from exc
        if parsed.tzinfo is None:
            raise ValueError(f"{field_name} must include a timezone")
        return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds")

    @classmethod
    def _global_chat_message_filter(
        cls,
        *,
        sender_uuid: str | None,
        channel_code: str | None,
        started_at_utc: str | None,
        ended_before_utc: str | None,
    ) -> tuple[list[str], list[object]]:
        """Build the shared validated WHERE clause for message history queries."""
        where: list[str] = []
        params: list[object] = []
        if sender_uuid is not None:
            normalized_uuid = str(sender_uuid or "").strip()
            if not normalized_uuid:
                where.append("0 = 1")
            else:
                where.append("sender_uuid = ?")
                params.append(normalized_uuid)
        if channel_code is not None:
            normalized_channel = normalize_global_chat_channel(channel_code)
            if normalized_channel is None:
                raise ValueError("Unsupported global chat channel")
            where.append("channel_code = ?")
            params.append(normalized_channel)
        normalized_start = None
        if started_at_utc is not None:
            normalized_start = cls._normalize_moderation_utc_boundary(
                started_at_utc,
                "started_at_utc",
            )
            where.append("sent_at_utc >= ?")
            params.append(normalized_start)
        normalized_end = None
        if ended_before_utc is not None:
            normalized_end = cls._normalize_moderation_utc_boundary(
                ended_before_utc,
                "ended_before_utc",
            )
            where.append("sent_at_utc < ?")
            params.append(normalized_end)
        if (
            normalized_start is not None
            and normalized_end is not None
            and normalized_start >= normalized_end
        ):
            raise ValueError("Global chat message time range is empty or reversed")
        return where, params

    def find_global_chat_sender_summaries(
        self,
        username: str,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[GlobalChatSenderSummary]:
        """Find retained sender identities for one exact folded username."""
        lookup_key = username_key(normalize_username(username))
        if not lookup_key:
            return []
        safe_limit = max(1, min(int(limit), MAX_MODERATION_QUERY_PAGE_SIZE))
        safe_offset = max(0, int(offset))
        rows = self._conn.execute(
            """
            SELECT history.sender_uuid,
                   (
                       SELECT latest.sender_username
                       FROM global_chat_messages AS latest
                       WHERE latest.sender_uuid = history.sender_uuid
                       ORDER BY latest.sent_at_utc DESC, latest.id DESC
                       LIMIT 1
                   ) AS sender_username,
                   COUNT(*) AS message_count,
                   MIN(history.sent_at_utc) AS first_sent_at_utc,
                   MAX(history.sent_at_utc) AS last_sent_at_utc
            FROM global_chat_messages AS history
            WHERE history.sender_uuid IN (
                SELECT DISTINCT matching.sender_uuid
                FROM global_chat_messages AS matching
                WHERE USERNAME_KEY(matching.sender_username) = ?
            )
            GROUP BY history.sender_uuid
            ORDER BY last_sent_at_utc DESC, history.sender_uuid
            LIMIT ? OFFSET ?
            """,
            (lookup_key, safe_limit, safe_offset),
        ).fetchall()
        return [
            GlobalChatSenderSummary(
                sender_uuid=str(row["sender_uuid"]),
                sender_username=str(row["sender_username"]),
                message_count=int(row["message_count"]),
                first_sent_at_utc=str(row["first_sent_at_utc"]),
                last_sent_at_utc=str(row["last_sent_at_utc"]),
            )
            for row in rows
        ]

    def count_global_chat_sender_identities(self, username: str) -> int:
        """Count immutable sender IDs matching one exact folded username."""
        lookup_key = username_key(normalize_username(username))
        if not lookup_key:
            return 0
        row = self._conn.execute(
            """
            SELECT COUNT(DISTINCT sender_uuid) AS count
            FROM global_chat_messages
            WHERE USERNAME_KEY(sender_username) = ?
            """,
            (lookup_key,),
        ).fetchone()
        return int(row["count"] if row else 0)

    def list_global_chat_messages(
        self,
        *,
        sender_uuid: str | None = None,
        channel_code: str | None = None,
        started_at_utc: str | None = None,
        ended_before_utc: str | None = None,
        sort_order: str = "newest",
        limit: int = 50,
        offset: int = 0,
    ) -> list[GlobalChatMessageRecord]:
        """List retained messages with bounded, indexed moderation filters."""
        safe_limit = max(1, min(int(limit), MAX_MODERATION_QUERY_PAGE_SIZE))
        safe_offset = max(0, int(offset))
        normalized_sort = str(sort_order or "")
        if normalized_sort not in GLOBAL_CHAT_HISTORY_SORT_ORDERS:
            raise ValueError("Unsupported global chat history sort order")
        where, params = self._global_chat_message_filter(
            sender_uuid=sender_uuid,
            channel_code=channel_code,
            started_at_utc=started_at_utc,
            ended_before_utc=ended_before_utc,
        )
        query = "SELECT * FROM global_chat_messages"
        if where:
            query += " WHERE " + " AND ".join(where)
        direction = "DESC" if normalized_sort == "newest" else "ASC"
        query += (
            f" ORDER BY sent_at_utc {direction}, id {direction}"
            " LIMIT ? OFFSET ?"
        )
        params.extend((safe_limit, safe_offset))
        rows = self._conn.execute(query, params).fetchall()
        return [self._global_chat_message_from_row(row) for row in rows]

    def get_global_chat_context(
        self,
        reported_at_utc: str,
        *,
        channel_code: str | None = None,
        before_count: int = 20,
        after_count: int = 10,
    ) -> list[GlobalChatMessageRecord]:
        """Return chronological conversation context around one UTC instant."""
        try:
            report_time = datetime.fromisoformat(str(reported_at_utc))
        except (TypeError, ValueError) as exc:
            raise ValueError("Report context requires an ISO timestamp") from exc
        if report_time.tzinfo is None:
            raise ValueError("Report context timestamp must include a timezone")
        timestamp = report_time.astimezone(timezone.utc).isoformat(
            timespec="microseconds"
        )
        safe_before = max(
            0, min(int(before_count), MAX_MODERATION_QUERY_PAGE_SIZE)
        )
        safe_after = max(
            0, min(int(after_count), MAX_MODERATION_QUERY_PAGE_SIZE)
        )
        where = "sent_at_utc <= ?"
        params: list[object] = [timestamp]
        after_where = "sent_at_utc > ?"
        after_params: list[object] = [timestamp]
        if channel_code is not None:
            normalized_channel = normalize_global_chat_channel(channel_code)
            if normalized_channel is None:
                raise ValueError("Unsupported global chat channel")
            where += " AND channel_code = ?"
            after_where += " AND channel_code = ?"
            params.append(normalized_channel)
            after_params.append(normalized_channel)

        before: list[GlobalChatMessageRecord] = []
        if safe_before:
            before_rows = self._conn.execute(
                f"""
                SELECT * FROM global_chat_messages
                WHERE {where}
                ORDER BY sent_at_utc DESC, id DESC
                LIMIT ?
                """,
                (*params, safe_before),
            ).fetchall()
            before = [
                self._global_chat_message_from_row(row)
                for row in reversed(before_rows)
            ]

        after: list[GlobalChatMessageRecord] = []
        if safe_after:
            after_rows = self._conn.execute(
                f"""
                SELECT * FROM global_chat_messages
                WHERE {after_where}
                ORDER BY sent_at_utc ASC, id ASC
                LIMIT ?
                """,
                (*after_params, safe_after),
            ).fetchall()
            after = [self._global_chat_message_from_row(row) for row in after_rows]
        return [*before, *after]

    def clear_global_chat_messages(self) -> int:
        """Explicitly clear all retained global-chat evidence."""
        with self._transaction(immediate=True) as cursor:
            cursor.execute("DELETE FROM global_chat_messages")
            deleted = max(0, cursor.rowcount)
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name = ?",
                ("global_chat_messages",),
            )
            return deleted

    @staticmethod
    def _moderation_report_from_row(
        row: sqlite3.Row,
    ) -> ModerationReportRecord:
        return ModerationReportRecord(
            id=int(row["id"]),
            reporter_uuid=str(row["reporter_uuid"]),
            reporter_username=str(row["reporter_username"]),
            reported_uuid=str(row["reported_uuid"]),
            reported_username=str(row["reported_username"]),
            reported_at_utc=str(row["reported_at_utc"]),
            reason_code=str(row["reason_code"]),
            details=str(row["details"] or ""),
            channel_code=(
                str(row["channel_code"]) if row["channel_code"] else None
            ),
            context_anchor_message_id=(
                int(row["context_anchor_message_id"])
                if row["context_anchor_message_id"] is not None
                else None
            ),
            status=str(row["status"]),
            reviewed_by_uuid=(
                str(row["reviewed_by_uuid"])
                if row["reviewed_by_uuid"]
                else None
            ),
            reviewed_by_username=(
                str(row["reviewed_by_username"])
                if row["reviewed_by_username"]
                else None
            ),
            reviewed_at_utc=(
                str(row["reviewed_at_utc"]) if row["reviewed_at_utc"] else None
            ),
            origin_code=str(row["origin_code"]),
            context_code=str(row["context_code"]),
            evidence_json=(
                str(row["evidence_json"])
                if row["evidence_json"] is not None
                else None
            ),
        )

    def submit_moderation_report(
        self,
        *,
        reporter_uuid: str,
        reporter_username: str,
        reported_uuid: str,
        reported_username: str,
        reason_code: str,
        details: str = "",
        channel_code: str | None = None,
    ) -> ModerationReportSubmission:
        """Atomically enforce report limits and retain one manual-review case."""
        reporter_id = str(reporter_uuid or "").strip()
        reporter_name = str(reporter_username or "").strip()
        reported_id = str(reported_uuid or "").strip()
        reported_name = str(reported_username or "").strip()
        if not reporter_id or not reporter_name or not reported_id or not reported_name:
            raise ValueError("Moderation reports require both account identities")
        if reporter_id == reported_id:
            raise ValueError("An account cannot report itself")
        if reason_code not in REPORT_REASON_CODE_SET:
            raise ValueError("Unsupported moderation report reason")
        if not isinstance(details, str):
            raise ValueError("Moderation report details must be text")
        normalized_details = details.strip()
        if len(normalized_details) > MAX_REPORT_DETAILS_LENGTH:
            raise ValueError("Moderation report details exceed the limit")
        normalized_channel = None
        if channel_code is not None:
            normalized_channel = normalize_global_chat_channel(channel_code)
            if normalized_channel is None:
                raise ValueError("Unsupported moderation report channel")

        now = datetime.now(timezone.utc)
        reported_at_utc = now.isoformat(timespec="microseconds")
        limit_window_start = (
            now - timedelta(seconds=REPORT_LIMIT_WINDOW_SECONDS)
        ).isoformat(timespec="microseconds")
        target_cooldown_start = (
            now - timedelta(seconds=SAME_TARGET_REPORT_COOLDOWN_SECONDS)
        ).isoformat(timespec="microseconds")

        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                "SELECT uuid, username FROM users WHERE uuid IN (?, ?)",
                (reporter_id, reported_id),
            )
            current_accounts = {
                str(row["uuid"]): str(row["username"])
                for row in cursor.fetchall()
            }
            if (
                current_accounts.get(reporter_id) != reporter_name
                or current_accounts.get(reported_id) != reported_name
            ):
                raise ValueError(
                    "Moderation report identities must match current accounts"
                )

            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM moderation_reports
                WHERE reporter_uuid = ? AND reported_at_utc >= ?
                """,
                (reporter_id, limit_window_start),
            )
            recent_count_row = cursor.fetchone()
            recent_count = int(recent_count_row["count"] if recent_count_row else 0)
            if recent_count >= MAX_REPORTS_PER_WINDOW:
                cursor.execute(
                    """
                    SELECT reported_at_utc
                    FROM moderation_reports
                    WHERE reporter_uuid = ? AND reported_at_utc >= ?
                    ORDER BY reported_at_utc ASC, id ASC
                    LIMIT 1
                    """,
                    (reporter_id, limit_window_start),
                )
                oldest = cursor.fetchone()
                retry_after = REPORT_LIMIT_WINDOW_SECONDS
                if oldest:
                    oldest_at = datetime.fromisoformat(oldest["reported_at_utc"])
                    retry_after = max(
                        1,
                        math.ceil(
                            (
                                oldest_at
                                + timedelta(seconds=REPORT_LIMIT_WINDOW_SECONDS)
                                - now
                            ).total_seconds()
                        ),
                    )
                return ModerationReportSubmission(
                    outcome="reporter_limit",
                    retry_after_seconds=retry_after,
                )

            cursor.execute(
                """
                SELECT reported_at_utc
                FROM moderation_reports
                WHERE reporter_uuid = ?
                  AND reported_uuid = ?
                  AND reported_at_utc >= ?
                ORDER BY reported_at_utc DESC, id DESC
                LIMIT 1
                """,
                (reporter_id, reported_id, target_cooldown_start),
            )
            latest_same_target = cursor.fetchone()
            if latest_same_target:
                latest_at = datetime.fromisoformat(
                    latest_same_target["reported_at_utc"]
                )
                retry_after = max(
                    1,
                    math.ceil(
                        (
                            latest_at
                            + timedelta(seconds=SAME_TARGET_REPORT_COOLDOWN_SECONDS)
                            - now
                        ).total_seconds()
                    ),
                )
                return ModerationReportSubmission(
                    outcome="target_cooldown",
                    retry_after_seconds=retry_after,
                )

            anchor_query = (
                "SELECT id FROM global_chat_messages "
                "WHERE sender_uuid = ? AND sent_at_utc <= ?"
            )
            anchor_params: list[object] = [reported_id, reported_at_utc]
            if normalized_channel is not None:
                anchor_query += " AND channel_code = ?"
                anchor_params.append(normalized_channel)
            anchor_query += " ORDER BY sent_at_utc DESC, id DESC LIMIT 1"
            cursor.execute(anchor_query, anchor_params)
            anchor_row = cursor.fetchone()
            anchor_id = int(anchor_row["id"]) if anchor_row else None

            cursor.execute(
                """
                INSERT INTO moderation_reports (
                    reporter_uuid,
                    reporter_username,
                    reported_uuid,
                    reported_username,
                    reported_at_utc,
                    reason_code,
                    details,
                    channel_code,
                    context_anchor_message_id,
                    status,
                    origin_code,
                    context_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)
                """,
                (
                    reporter_id,
                    reporter_name,
                    reported_id,
                    reported_name,
                    reported_at_utc,
                    reason_code,
                    normalized_details,
                    normalized_channel,
                    anchor_id,
                    REPORT_ORIGIN_MANUAL,
                    REPORT_CONTEXT_GLOBAL,
                ),
            )
            return ModerationReportSubmission(
                outcome="created",
                report_id=int(cursor.lastrowid),
            )

    def submit_automated_spam_report(
        self,
        *,
        reported_uuid: str,
        reported_username: str,
        evidence: AutomatedSpamEvidence,
        channel_code: str | None = None,
    ) -> ModerationReportSubmission:
        """Persist one review-only System report with a durable flood guard."""
        reported_id = str(reported_uuid or "").strip()
        reported_name = str(reported_username or "").strip()
        if not reported_id or not reported_name:
            raise ValueError("Automated reports require a target identity")
        if evidence.scope not in REPORT_CONTEXT_CODES:
            raise ValueError("Unsupported automated-report context")
        normalized_channel = None
        if evidence.scope == REPORT_CONTEXT_GLOBAL:
            normalized_channel = normalize_global_chat_channel(channel_code)
            if normalized_channel is None:
                raise ValueError("Global automated reports require a channel")
        elif channel_code is not None:
            raise ValueError("Table automated reports cannot have a global channel")
        evidence_json = evidence.to_json()

        now = datetime.now(timezone.utc)
        reported_at_utc = now.isoformat(timespec="microseconds")
        cooldown_start = (
            now - timedelta(seconds=AUTOMATED_SPAM_REPORT_COOLDOWN_SECONDS)
        ).isoformat(timespec="microseconds")

        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                "SELECT username FROM users WHERE uuid = ?",
                (reported_id,),
            )
            target = cursor.fetchone()
            if not target or str(target["username"]) != reported_name:
                raise ValueError("Automated-report target must match a current account")

            cursor.execute(
                """
                SELECT reported_at_utc
                FROM moderation_reports
                WHERE origin_code = ?
                  AND reported_uuid = ?
                  AND context_code = ?
                  AND reported_at_utc >= ?
                ORDER BY reported_at_utc DESC, id DESC
                LIMIT 1
                """,
                (
                    REPORT_ORIGIN_AUTOMATED_SPAM,
                    reported_id,
                    evidence.scope,
                    cooldown_start,
                ),
            )
            latest = cursor.fetchone()
            if latest:
                latest_at = datetime.fromisoformat(latest["reported_at_utc"])
                retry_after = max(
                    1,
                    math.ceil(
                        (
                            latest_at
                            + timedelta(
                                seconds=AUTOMATED_SPAM_REPORT_COOLDOWN_SECONDS
                            )
                            - now
                        ).total_seconds()
                    ),
                )
                return ModerationReportSubmission(
                    outcome="automation_cooldown",
                    retry_after_seconds=retry_after,
                )

            anchor_id = None
            if evidence.scope == REPORT_CONTEXT_GLOBAL:
                cursor.execute(
                    """
                    SELECT id
                    FROM global_chat_messages
                    WHERE sender_uuid = ?
                      AND channel_code = ?
                      AND sent_at_utc <= ?
                    ORDER BY sent_at_utc DESC, id DESC
                    LIMIT 1
                    """,
                    (reported_id, normalized_channel, reported_at_utc),
                )
                anchor = cursor.fetchone()
                anchor_id = int(anchor["id"]) if anchor else None

            cursor.execute(
                """
                INSERT INTO moderation_reports (
                    reporter_uuid,
                    reporter_username,
                    reported_uuid,
                    reported_username,
                    reported_at_utc,
                    reason_code,
                    details,
                    channel_code,
                    context_anchor_message_id,
                    status,
                    origin_code,
                    context_code,
                    evidence_json
                ) VALUES (?, ?, ?, ?, ?, 'spam', '', ?, ?, 'open', ?, ?, ?)
                """,
                (
                    SYSTEM_REPORTER_UUID,
                    SYSTEM_REPORTER_USERNAME,
                    reported_id,
                    reported_name,
                    reported_at_utc,
                    normalized_channel,
                    anchor_id,
                    REPORT_ORIGIN_AUTOMATED_SPAM,
                    evidence.scope,
                    evidence_json,
                ),
            )
            return ModerationReportSubmission(
                outcome="created",
                report_id=int(cursor.lastrowid),
            )

    def get_moderation_report(
        self, report_id: int
    ) -> ModerationReportRecord | None:
        """Return one report by stable ID."""
        row = self._conn.execute(
            "SELECT * FROM moderation_reports WHERE id = ?",
            (int(report_id),),
        ).fetchone()
        return self._moderation_report_from_row(row) if row else None

    @staticmethod
    def _normalize_report_status_filter(
        *,
        status: str | None,
        statuses: tuple[str, ...] | None,
    ) -> tuple[str, ...] | None:
        """Return one validated status filter without ambiguous combinations."""
        if status is not None and statuses is not None:
            raise ValueError("Use status or statuses, not both")
        if status is not None:
            selected = (status,)
        elif statuses is not None:
            selected = tuple(dict.fromkeys(statuses))
        else:
            return None
        if not selected or any(item not in REPORT_STATUS_SET for item in selected):
            raise ValueError("Unsupported moderation report status")
        return selected

    def count_moderation_reports(
        self,
        *,
        status: str | None = None,
        statuses: tuple[str, ...] | None = None,
    ) -> int:
        """Count retained reports, optionally by review status."""
        selected = self._normalize_report_status_filter(
            status=status,
            statuses=statuses,
        )
        if selected is None:
            row = self._conn.execute(
                "SELECT COUNT(*) AS count FROM moderation_reports"
            ).fetchone()
        else:
            placeholders = ", ".join("?" for _ in selected)
            row = self._conn.execute(
                "SELECT COUNT(*) AS count FROM moderation_reports "
                f"WHERE status IN ({placeholders})",
                selected,
            ).fetchone()
        return int(row["count"] if row else 0)

    def list_moderation_reports(
        self,
        *,
        status: str | None = None,
        statuses: tuple[str, ...] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ModerationReportRecord]:
        """List reports newest-first, optionally filtered by review status."""
        selected = self._normalize_report_status_filter(
            status=status,
            statuses=statuses,
        )
        safe_limit = max(1, min(int(limit), MAX_MODERATION_QUERY_PAGE_SIZE))
        safe_offset = max(0, int(offset))
        if selected is None:
            rows = self._conn.execute(
                """
                SELECT * FROM moderation_reports
                ORDER BY reported_at_utc DESC, id DESC
                LIMIT ? OFFSET ?
                """,
                (safe_limit, safe_offset),
            ).fetchall()
        else:
            placeholders = ", ".join("?" for _ in selected)
            rows = self._conn.execute(
                f"""
                SELECT * FROM moderation_reports
                WHERE status IN ({placeholders})
                ORDER BY reported_at_utc DESC, id DESC
                LIMIT ? OFFSET ?
                """,
                (*selected, safe_limit, safe_offset),
            ).fetchall()
        return [self._moderation_report_from_row(row) for row in rows]

    def set_moderation_report_status(
        self,
        report_id: int,
        status: str,
        *,
        reviewer_uuid: str,
        reviewer_username: str,
    ) -> bool:
        """Record a manual review outcome with an immutable reviewer snapshot."""
        if status not in REPORT_STATUS_SET or status == "open":
            raise ValueError("Reports may only be closed with a review outcome")
        reviewer_id = str(reviewer_uuid or "").strip()
        reviewer_name = str(reviewer_username or "").strip()
        if not reviewer_id or not reviewer_name:
            raise ValueError("A moderation review requires a reviewer identity")
        reviewed_at_utc = datetime.now(timezone.utc).isoformat(
            timespec="microseconds"
        )
        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                "SELECT username FROM users WHERE uuid = ?",
                (reviewer_id,),
            )
            reviewer = cursor.fetchone()
            if not reviewer or str(reviewer["username"]) != reviewer_name:
                raise ValueError("Reviewer identity must match a current account")
            cursor.execute(
                """
                UPDATE moderation_reports
                SET status = ?, reviewed_by_uuid = ?,
                    reviewed_by_username = ?, reviewed_at_utc = ?
                WHERE id = ? AND status = 'open'
                """,
                (
                    status,
                    reviewer_id,
                    reviewer_name,
                    reviewed_at_utc,
                    int(report_id),
                ),
            )
            return cursor.rowcount > 0

    def clear_closed_moderation_reports(self) -> int:
        """Explicitly clear reviewed reports while preserving every open case."""
        placeholders = ", ".join("?" for _ in CLOSED_REPORT_STATUSES)
        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                f"DELETE FROM moderation_reports WHERE status IN ({placeholders})",
                CLOSED_REPORT_STATUSES,
            )
            deleted = max(0, cursor.rowcount)
            cursor.execute("SELECT 1 FROM moderation_reports LIMIT 1")
            if cursor.fetchone() is None:
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name = ?",
                    ("moderation_reports",),
                )
            return deleted

    # User operations

    @staticmethod
    def _user_record_from_row(row: sqlite3.Row) -> UserRecord:
        return UserRecord(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            uuid=row["uuid"],
            locale=row["locale"] or "en",
            preferences_json=row["preferences_json"] or "{}",
            trust_level=row["trust_level"] if row["trust_level"] is not None else 1,
            approved=bool(row["approved"]) if row["approved"] is not None else False,
            email=row["email"] or "",
            bio=row["bio"] or "",
            motd_version=row["motd_version"] if "motd_version" in row.keys() else 0,
            gender=row["gender"] if "gender" in row.keys() else "Not set",
            registration_date=(
                row["registration_date"] if "registration_date" in row.keys() else ""
            ),
            last_login_date=(
                row["last_login_date"] if "last_login_date" in row.keys() else ""
            ),
        )

    def get_user_by_email(self, email: str) -> UserRecord | None:
        """Get a user by email (case-insensitive)."""
        if not email:
            return None
        cursor = self._conn.cursor()
        cursor.execute(
            f"SELECT {_USER_RECORD_COLUMNS} FROM users "
            "WHERE LOWER(email) = LOWER(?)",
            (email,),
        )
        row = cursor.fetchone()
        return self._user_record_from_row(row) if row else None

    def resolve_user(self, username: str) -> UsernameResolution:
        """Resolve exact spelling first, then one unambiguous folded match."""
        entered = str(username or "").strip()
        normalized = normalize_username(entered)
        lookup_key = username_key(normalized)
        if not entered or not lookup_key:
            return UsernameResolution()

        cursor = self._conn.cursor()
        cursor.execute(
            f"SELECT {_USER_RECORD_COLUMNS} FROM users "
            "WHERE username = ? COLLATE BINARY LIMIT 1",
            (entered,),
        )
        exact_row = cursor.fetchone()
        if exact_row:
            return UsernameResolution(user=self._user_record_from_row(exact_row))

        if normalized != entered:
            cursor.execute(
                f"SELECT {_USER_RECORD_COLUMNS} FROM users "
                "WHERE username = ? COLLATE BINARY LIMIT 1",
                (normalized,),
            )
            normalized_row = cursor.fetchone()
            if normalized_row:
                return UsernameResolution(
                    user=self._user_record_from_row(normalized_row)
                )

        cursor.execute(
            f"SELECT {_USER_RECORD_COLUMNS} FROM users "
            "WHERE username_key = ? ORDER BY id LIMIT 2",
            (lookup_key,),
        )
        rows = cursor.fetchall()
        if len(rows) == 1:
            return UsernameResolution(user=self._user_record_from_row(rows[0]))
        return UsernameResolution(ambiguous=len(rows) > 1)

    def get_user(self, username: str) -> UserRecord | None:
        """Get a user by exact or unambiguous Unicode-insensitive username."""
        return self.resolve_user(username).user

    def create_user(
        self,
        username: str,
        password_hash: str,
        locale: str = "en",
        trust_level: int = 1,
        approved: bool = False,
        email: str = "",
        bio: str = "",
        promote_first_user: bool = False,
    ) -> UserRecord | None:
        """Atomically create a user unless its Unicode lookup key is taken.

        When ``promote_first_user`` is true, the empty-database check and
        developer promotion happen under the same cross-process write lock as
        the insert. This prevents simultaneous registrations from creating
        more than one first-account developer.
        """
        username = normalize_username(username)
        lookup_key = username_key(username)
        if not username or not lookup_key:
            return None
        user_uuid = str(uuid_module.uuid4())
        now_iso = datetime.now().isoformat()
        try:
            # Serialize the key check and insert across server/CLI processes.
            # The legacy username column's NOCASE constraint covers ASCII only.
            with self._transaction(immediate=True) as cursor:
                cursor.execute(
                    "SELECT 1 FROM users WHERE username_key = ? LIMIT 1",
                    (lookup_key,),
                )
                if cursor.fetchone() is not None:
                    return None
                effective_trust_level = trust_level
                effective_approved = approved
                if promote_first_user:
                    cursor.execute("SELECT 1 FROM users LIMIT 1")
                    if cursor.fetchone() is None:
                        effective_trust_level = 3
                        effective_approved = True
                cursor.execute(
                    "INSERT INTO users (username, username_key, password_hash, "
                    "uuid, locale, trust_level, approved, email, bio, "
                    "registration_date, last_login_date) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        username,
                        lookup_key,
                        password_hash,
                        user_uuid,
                        locale,
                        effective_trust_level,
                        1 if effective_approved else 0,
                        email,
                        bio,
                        now_iso,
                        "",
                    ),
                )
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # Another process may have won the same registration race.
            return None
        except sqlite3.OperationalError:
            # errors.log intentionally records ERROR and above, so retain the
            # actionable SQLite cause and traceback at that configured level.
            logging.getLogger("playaural.db").exception(
                "Operational error creating user '%s'", username
            )
            return None
        return UserRecord(
            id=user_id,
            username=username,
            password_hash=password_hash,
            uuid=user_uuid,
            locale=locale,
            trust_level=effective_trust_level,
            approved=effective_approved,
            email=email,
            bio=bio,
            registration_date=now_iso,
            last_login_date="",
        )

    def user_exists(self, username: str) -> bool:
        """Check for any exact or folded match, including legacy collisions."""
        lookup_key = username_key(username)
        if not lookup_key:
            return False
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE username_key = ? LIMIT 1",
            (lookup_key,),
        )
        return cursor.fetchone() is not None

    def email_exists(self, email: str, exclude_username: str | None = None) -> bool:
        """Check if an email is already in use by another account (case-insensitive)."""
        if not email:
            return False  # Empty emails shouldn't trigger "taken" errors
        cursor = self._conn.cursor()
        if exclude_username:
            excluded_user = self.get_user(exclude_username)
            excluded_id = excluded_user.id if excluded_user else -1
            cursor.execute(
                "SELECT 1 FROM users WHERE LOWER(email) = LOWER(?) AND id != ?",
                (email, excluded_id),
            )
        else:
            cursor.execute("SELECT 1 FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        return cursor.fetchone() is not None

    def _update_user_value(self, username: str, column: str, value: object) -> bool:
        """Update one allowlisted account field after safe identity resolution."""
        allowed_columns = {
            "locale",
            "preferences_json",
            "password_hash",
            "email",
            "bio",
            "gender",
            "last_login_date",
            "trust_level",
            "motd_version",
            "approved",
        }
        if column not in allowed_columns:
            raise ValueError(f"Unsupported user column: {column}")
        user = self.get_user(username)
        if not user:
            return False
        cursor = self._conn.cursor()
        cursor.execute(
            f"UPDATE users SET {column} = ? WHERE id = ?",
            (value, user.id),
        )
        return cursor.rowcount > 0

    def update_user_locale(self, username: str, locale: str) -> None:
        """Update a user's locale."""
        self._update_user_value(username, "locale", locale)

    def update_user_preferences(self, username: str, preferences_json: str) -> None:
        """Update a user's preferences."""
        self._update_user_value(username, "preferences_json", preferences_json)

    def update_user_password(self, username: str, password_hash: str) -> None:
        """Update a user's password hash."""
        self._update_user_value(username, "password_hash", password_hash)

    def update_user_email(self, username: str, email: str) -> None:
        """Update a user's email."""
        self._update_user_value(username, "email", email)

    def update_user_bio(self, username: str, bio: str) -> None:
        """Update a user's bio."""
        self._update_user_value(username, "bio", bio)

    def update_user_gender(self, username: str, gender: str) -> None:
        """Update a user's gender."""
        self._update_user_value(username, "gender", gender)

    def update_user_last_login(self, username: str) -> None:
        """Update a user's last login date."""
        now_iso = datetime.now().isoformat()
        self._update_user_value(username, "last_login_date", now_iso)

    def get_user_count(self) -> int:
        """Get the total number of users in the database."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

    def initialize_trust_levels(self) -> str | None:
        """
        Initialize trust levels for users who don't have one set.

        Sets all users without a trust level to 1 (player).
        If there's exactly one user and they have no trust level, sets them to 2 (admin).

        Returns:
            The username of the user promoted to admin, or None if no promotion occurred.
        """
        with self._transaction(immediate=True) as cursor:
            # Check if there's exactly one user with no trust level set.
            cursor.execute(
                "SELECT id, username FROM users WHERE trust_level IS NULL"
            )
            users_without_trust = cursor.fetchall()

            promoted_user = None
            if len(users_without_trust) == 1:
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                if total_users == 1:
                    username = users_without_trust[0]["username"]
                    cursor.execute(
                        "UPDATE users SET trust_level = 3 WHERE id = ?",
                        (users_without_trust[0]["id"],),
                    )
                    promoted_user = username

            cursor.execute(
                "UPDATE users SET trust_level = 1 WHERE trust_level IS NULL"
            )

        return promoted_user

    def update_user_trust_level(self, username: str, trust_level: int) -> None:
        """Update a user's trust level."""
        self._update_user_value(username, "trust_level", trust_level)

    def update_user_motd_version(self, username: str, motd_version: int) -> None:
        """Update a user's motd version."""
        self._update_user_value(username, "motd_version", motd_version)

    def count_pending_users(self) -> int:
        """Count users who are not yet approved."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM users WHERE approved = 0")
        row = cursor.fetchone()
        return int(row["count"] if row else 0)

    def get_pending_users(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[UserRecord]:
        """Get users who are not yet approved, optionally as a bounded page."""
        cursor = self._conn.cursor()
        query = (
            f"SELECT {_USER_RECORD_COLUMNS} FROM users WHERE approved = 0 "
            "ORDER BY username_key, "
            "username COLLATE BINARY"
        )
        params: tuple[object, ...] = ()
        if limit is not None:
            safe_limit = max(1, min(int(limit), 100))
            safe_offset = max(0, int(offset))
            query += " LIMIT ? OFFSET ?"
            params = (safe_limit, safe_offset)
        cursor.execute(query, params)
        return [self._user_record_from_row(row) for row in cursor.fetchall()]

    def approve_user(self, username: str) -> bool:
        """Approve a user account. Returns True if user was found and approved."""
        return self._update_user_value(username, "approved", 1)

    def delete_user(self, username: str) -> bool:
        """Delete a user account and safely clean up orphaned metadata. Returns True if user was found and deleted."""
        user = self.get_user(username)
        if not user:
            return False
        canonical_username = user.username

        with self._transaction(immediate=True) as cursor:
            # Delete dependent data using explicit soft keys (username/uuid).
            cursor.execute(
                "DELETE FROM player_game_stats WHERE player_id = ?",
                (user.uuid,),
            )
            cursor.execute(
                "DELETE FROM player_ratings WHERE player_id = ?",
                (user.uuid,),
            )
            cursor.execute(
                "DELETE FROM saved_tables WHERE username = ? COLLATE BINARY",
                (canonical_username,),
            )
            self._delete_table_checkpoints_for_user(cursor, user)
            cursor.execute(
                "DELETE FROM bans WHERE username = ? COLLATE BINARY",
                (canonical_username,),
            )
            cursor.execute(
                "DELETE FROM mutes WHERE username = ? COLLATE BINARY",
                (canonical_username,),
            )
            cursor.execute(
                "DELETE FROM friendships "
                "WHERE requester_id = ? OR receiver_id = ?",
                (user.uuid, user.uuid),
            )
            cursor.execute(
                "DELETE FROM user_blocks "
                "WHERE blocker_id = ? OR blocked_id = ?",
                (user.uuid, user.uuid),
            )
            cursor.execute(
                "DELETE FROM user_notifications "
                "WHERE user_id = ? OR source_username = ? COLLATE BINARY",
                (user.uuid, canonical_username),
            )
            cursor.execute(
                "DELETE FROM password_reset_tokens WHERE user_uuid = ?",
                (user.uuid,),
            )

            # Global-chat messages and reports deliberately retain immutable
            # UUID and username snapshots until a developer explicitly clears
            # them.

            # Preserve other players' historical results through anonymization.
            cursor.execute(
                "UPDATE game_result_players "
                "SET player_id = 'deleted', player_name = 'Deleted User' "
                "WHERE player_id = ?",
                (user.uuid,),
            )
            cursor.execute("DELETE FROM users WHERE id = ?", (user.id,))
            deleted = cursor.rowcount > 0

        return deleted

    def _delete_table_checkpoints_for_user(
        self, cursor: sqlite3.Cursor, user: UserRecord
    ) -> int:
        """Delete transient table checkpoints that reference an account."""
        cursor.execute("SELECT table_id, host, members_json FROM tables")
        table_ids: list[str] = []
        for row in cursor.fetchall():
            host = self.get_user(str(row["host"]))
            if host and host.uuid == user.uuid:
                table_ids.append(row["table_id"])
                continue
            try:
                members = json.loads(row["members_json"])
            except (TypeError, json.JSONDecodeError):
                continue
            member_records = (
                self.get_user(str(member.get("username", "")))
                for member in members
            )
            if any(record and record.uuid == user.uuid for record in member_records):
                table_ids.append(row["table_id"])

        for table_id in table_ids:
            cursor.execute("DELETE FROM tables WHERE table_id = ?", (table_id,))
        return len(table_ids)

    def get_non_admin_users(self) -> list[UserRecord]:
        """Get all approved users who are not admins (trust_level < 2)."""
        cursor = self._conn.cursor()
        cursor.execute(
            f"SELECT {_USER_RECORD_COLUMNS} FROM users "
            "WHERE approved = 1 AND trust_level < 2 "
            "ORDER BY username_key, username COLLATE BINARY"
        )
        return [self._user_record_from_row(row) for row in cursor.fetchall()]

    def get_admin_users(self) -> list[UserRecord]:
        """Get all users who are admins (trust_level >= 2)."""
        cursor = self._conn.cursor()
        cursor.execute(
            f"SELECT {_USER_RECORD_COLUMNS} FROM users "
            "WHERE trust_level >= 2 "
            "ORDER BY username_key, username COLLATE BINARY"
        )
        return [self._user_record_from_row(row) for row in cursor.fetchall()]

    def _build_user_search_filters(
        self,
        query: str = "",
        *,
        approved: bool | None = None,
        min_trust_level: int | None = None,
        max_trust_level: int | None = None,
        exclude_username: str | None = None,
        exclude_active_bans: bool = False,
        exclude_active_mutes: bool = False,
    ) -> tuple[list[str], list[object], str]:
        """Build shared SQL filters for paginated user search/count queries."""
        now = datetime.now().isoformat()
        term = normalize_username(query)
        term_key = username_key(term)

        where = ["INSTR(username_key, ?) > 0"]
        params: list[object] = [term_key]
        if approved is not None:
            where.append("approved = ?")
            params.append(1 if approved else 0)
        if min_trust_level is not None:
            where.append("COALESCE(trust_level, 1) >= ?")
            params.append(min_trust_level)
        if max_trust_level is not None:
            where.append("COALESCE(trust_level, 1) <= ?")
            params.append(max_trust_level)
        if exclude_username:
            excluded_user = self.get_user(exclude_username)
            if excluded_user:
                where.append("id != ?")
                params.append(excluded_user.id)
        if exclude_active_bans:
            where.append(
                """
                NOT EXISTS (
                    SELECT 1 FROM bans
                    WHERE bans.username = users.username COLLATE BINARY
                    AND (bans.expires_at IS NULL OR bans.expires_at > ?)
                )
                """
            )
            params.append(now)
        if exclude_active_mutes:
            where.append(
                """
                NOT EXISTS (
                    SELECT 1 FROM mutes
                    WHERE mutes.username = users.username COLLATE BINARY
                    AND (mutes.expires_at IS NULL OR mutes.expires_at > ?)
                )
                """
            )
            params.append(now)
        return where, params, term_key

    def count_users(
        self,
        query: str = "",
        *,
        approved: bool | None = None,
        min_trust_level: int | None = None,
        max_trust_level: int | None = None,
        exclude_username: str | None = None,
        exclude_active_bans: bool = False,
        exclude_active_mutes: bool = False,
    ) -> int:
        """Count users matching the same filters used by paginated search."""
        where, params, _ = self._build_user_search_filters(
            query,
            approved=approved,
            min_trust_level=min_trust_level,
            max_trust_level=max_trust_level,
            exclude_username=exclude_username,
            exclude_active_bans=exclude_active_bans,
            exclude_active_mutes=exclude_active_mutes,
        )
        cursor = self._conn.cursor()
        cursor.execute(
            f"SELECT COUNT(*) AS count FROM users WHERE {' AND '.join(where)}",
            params,
        )
        row = cursor.fetchone()
        return int(row["count"] if row else 0)

    def search_users(
        self,
        query: str = "",
        *,
        approved: bool | None = None,
        min_trust_level: int | None = None,
        max_trust_level: int | None = None,
        exclude_username: str | None = None,
        exclude_active_bans: bool = False,
        exclude_active_mutes: bool = False,
        limit: int = 25,
        offset: int = 0,
    ) -> list[UserRecord]:
        """Search users with bounded, SQL-level filtering for large admin menus."""
        limit = max(1, min(int(limit), 100))
        offset = max(0, int(offset))
        where, params, term_key = self._build_user_search_filters(
            query,
            approved=approved,
            min_trust_level=min_trust_level,
            max_trust_level=max_trust_level,
            exclude_username=exclude_username,
            exclude_active_bans=exclude_active_bans,
            exclude_active_mutes=exclude_active_mutes,
        )
        cursor = self._conn.cursor()
        cursor.execute(
            f"""
            SELECT {_USER_RECORD_COLUMNS}
            FROM users
            WHERE {' AND '.join(where)}
            ORDER BY
                CASE
                    WHEN username_key = ? THEN 0
                    WHEN INSTR(username_key, ?) = 1 THEN 1
                    ELSE 2
                END,
                username_key,
                username COLLATE BINARY
            LIMIT ?
            OFFSET ?
            """,
            (*params, term_key, term_key, limit, offset),
        )
        return [self._user_record_from_row(row) for row in cursor.fetchall()]


    # MOTD operations

    def get_highest_motd_version(self) -> int:
        """Get the highest motd version currently active."""
        cursor = self._conn.cursor()
        try:
            cursor.execute("SELECT MAX(version) FROM motd")
            row = cursor.fetchone()
            return row[0] if row[0] is not None else 0
        except sqlite3.OperationalError:
            return 0

    def get_motd(self, version: int, language: str) -> str | None:
        """Get a motd message for a specific version and language."""
        cursor = self._conn.cursor()
        try:
            requested = (
                Localization.normalize_locale_code(language) or DEFAULT_LOCALE
            )
            candidates = dict.fromkeys(
                (requested, requested.split("-", 1)[0], DEFAULT_LOCALE)
            )
            for candidate in candidates:
                cursor.execute(
                    "SELECT message FROM motd WHERE version = ? AND language = ?",
                    (version, candidate),
                )
                row = cursor.fetchone()
                if row:
                    return row["message"]

            # Fallback to any language
            cursor.execute(
                "SELECT message FROM motd WHERE version = ? "
                "ORDER BY language LIMIT 1",
                (version,)
            )
            row = cursor.fetchone()
            if row:
                return row["message"]
            return None
        except sqlite3.OperationalError:
            return None

    def get_active_motd(self, language: str) -> tuple[int, str] | None:
        """Get the active (highest version) motd and message for a language."""
        version = self.get_highest_motd_version()
        if version == 0:
            return None

        message = self.get_motd(version, language)
        if message:
            return (version, message)
        return None

    def create_motd(self, version: int, translations: dict[str, str]) -> None:
        """Create a new motd version with translations and delete old versions."""
        clean_translations: dict[str, str] = {}
        for language, message in translations.items():
            locale = Localization.normalize_locale_code(language)
            if locale and isinstance(message, str) and message.strip():
                clean_translations[locale] = message
        if version <= 0 or not clean_translations:
            raise ValueError("MOTD requires a positive version and translations")
        with self._transaction(immediate=True) as cursor:
            cursor.execute("DELETE FROM motd")
            cursor.executemany(
                "INSERT INTO motd (version, language, message) VALUES (?, ?, ?)",
                [
                    (version, language, message)
                    for language, message in clean_translations.items()
                ],
            )

    def delete_motd(self) -> None:
        """Delete all motd records."""
        cursor = self._conn.cursor()
        try:
            cursor.execute("DELETE FROM motd")
        except sqlite3.OperationalError:
            pass

    # Ban operations

    def _canonical_username_or_input(self, username: str) -> str:
        """Return a registered display name when *username* resolves uniquely."""
        resolution = self.resolve_user(username)
        if resolution.ambiguous:
            raise ValueError("Ambiguous username spelling")
        if resolution.user is not None:
            return resolution.user.username
        return normalize_username(username)

    def ban_user(self, username: str, admin_username: str, reason_key: str, expires_at: str | None) -> BanRecord:
        """Ban a user."""
        username = self._canonical_username_or_input(username)
        admin_username = self._canonical_username_or_input(admin_username)
        issued_at = datetime.now().isoformat()
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO bans (username, admin_username, reason_key, issued_at, expires_at) VALUES (?, ?, ?, ?, ?)",
            (username, admin_username, reason_key, issued_at, expires_at),
        )
        return BanRecord(
            id=cursor.lastrowid,
            username=username,
            admin_username=admin_username,
            reason_key=reason_key,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def unban_user(self, username: str) -> bool:
        """Unban a user by removing their active bans. Returns True if unbanned."""
        username = self._canonical_username_or_input(username)
        cursor = self._conn.cursor()
        cursor.execute(
            "DELETE FROM bans WHERE username = ? COLLATE BINARY", (username,)
        )
        return cursor.rowcount > 0

    def get_active_ban(self, username: str) -> BanRecord | None:
        """Get the active ban for a user, if any. Clears expired bans in one SQL call."""
        username = self._canonical_username_or_input(username)
        now = datetime.now().isoformat()
        cursor = self._conn.cursor()

        # Purge expired bans for this user in a single DELETE
        cursor.execute(
            "DELETE FROM bans WHERE username = ? COLLATE BINARY AND expires_at IS NOT NULL AND expires_at <= ?",
            (username, now),
        )

        # Fetch the most-recent active ban (permanent or future expiry)
        cursor.execute(
            """
            SELECT id, username, admin_username, reason_key, issued_at, expires_at
            FROM bans
            WHERE username = ? COLLATE BINARY AND (expires_at IS NULL OR expires_at > ?)
            ORDER BY issued_at DESC, id DESC
            LIMIT 1
            """,
            (username, now),
        )
        row = cursor.fetchone()
        if row:
            return BanRecord(
                id=row["id"],
                username=row["username"],
                admin_username=row["admin_username"],
                reason_key=row["reason_key"],
                issued_at=row["issued_at"],
                expires_at=row["expires_at"],
            )
        return None

    def get_all_banned_users(self) -> list[str]:
        """Get a list of all currently banned usernames."""
        now = datetime.now().isoformat()
        cursor = self._conn.cursor()
        # Find usernames where they have at least one active ban
        cursor.execute(
            "SELECT DISTINCT username FROM bans WHERE expires_at IS NULL OR expires_at > ?",
            (now,)
        )
        return [row["username"] for row in cursor.fetchall()]

    def search_active_ban_records(
        self,
        query: str = "",
        *,
        limit: int = 25,
        offset: int = 0,
    ) -> list[BanRecord]:
        """Search latest active ban records without loading the full ban table."""
        now = datetime.now().isoformat()
        term = username_key(query)
        limit = max(1, min(int(limit), 100))
        offset = max(0, int(offset))
        cursor = self._conn.cursor()
        cursor.execute(
            """
            WITH ranked_active_bans AS (
                SELECT
                    id,
                    username,
                    admin_username,
                    reason_key,
                    issued_at,
                    expires_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY username COLLATE BINARY
                        ORDER BY issued_at DESC, id DESC
                    ) AS row_number
                FROM bans
                WHERE (expires_at IS NULL OR expires_at > ?)
                  AND INSTR(USERNAME_KEY(username), ?) > 0
            )
            SELECT id, username, admin_username, reason_key, issued_at, expires_at
            FROM ranked_active_bans
            WHERE row_number = 1
            ORDER BY
                CASE
                    WHEN USERNAME_KEY(username) = ? THEN 0
                    WHEN INSTR(USERNAME_KEY(username), ?) = 1 THEN 1
                    ELSE 2
                END,
                USERNAME_KEY(username),
                username COLLATE BINARY
            LIMIT ?
            OFFSET ?
            """,
            (now, term, term, term, limit, offset),
        )
        return [
            BanRecord(
                id=row["id"],
                username=row["username"],
                admin_username=row["admin_username"],
                reason_key=row["reason_key"],
                issued_at=row["issued_at"],
                expires_at=row["expires_at"],
            )
            for row in cursor.fetchall()
        ]

    def count_active_banned_users(self, query: str = "") -> int:
        """Count currently banned usernames matching an optional search term."""
        now = datetime.now().isoformat()
        term = username_key(query)
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM (
                SELECT username
                FROM bans
                WHERE (expires_at IS NULL OR expires_at > ?)
                  AND INSTR(USERNAME_KEY(username), ?) > 0
                GROUP BY username COLLATE BINARY
            )
            """,
            (now, term),
        )
        row = cursor.fetchone()
        return int(row["count"] if row else 0)

    def search_active_banned_users(
        self,
        query: str = "",
        *,
        limit: int = 25,
        offset: int = 0,
    ) -> list[str]:
        """Search currently banned usernames without loading the full ban list."""
        return [
            record.username
            for record in self.search_active_ban_records(
                query,
                limit=limit,
                offset=offset,
            )
        ]

    # ==================== Mute operations ====================

    def mute_user(self, username: str, admin_username: str, reason: str, expires_at: str | None) -> MuteRecord:
        """Mute a user."""
        username = self._canonical_username_or_input(username)
        admin_username = self._canonical_username_or_input(admin_username)
        issued_at = datetime.now().isoformat()
        # Replace any existing mute atomically so a re-mute always supersedes
        # the previous one, even when timestamps tie.
        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                "DELETE FROM mutes WHERE username = ? COLLATE BINARY",
                (username,),
            )
            cursor.execute(
                "INSERT INTO mutes (username, admin_username, reason, "
                "issued_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                (username, admin_username, reason, issued_at, expires_at),
            )
            mute_id = cursor.lastrowid
        return MuteRecord(
            id=mute_id,
            username=username,
            admin_username=admin_username,
            reason=reason,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def unmute_user(self, username: str) -> bool:
        """Unmute a user by removing their active mutes. Returns True if unmuted."""
        username = self._canonical_username_or_input(username)
        cursor = self._conn.cursor()
        cursor.execute(
            "DELETE FROM mutes WHERE username = ? COLLATE BINARY", (username,)
        )
        return cursor.rowcount > 0

    def get_active_mute(self, username: str) -> MuteRecord | None:
        """Get the active mute for a user, if any. Clears expired mutes."""
        username = self._canonical_username_or_input(username)
        now = datetime.now().isoformat()
        cursor = self._conn.cursor()

        # Purge expired mutes
        cursor.execute(
            "DELETE FROM mutes WHERE username = ? COLLATE BINARY AND expires_at IS NOT NULL AND expires_at <= ?",
            (username, now),
        )

        # Fetch the most-recent active mute
        cursor.execute(
            """
            SELECT id, username, admin_username, reason, issued_at, expires_at
            FROM mutes
            WHERE username = ? COLLATE BINARY AND (expires_at IS NULL OR expires_at > ?)
            ORDER BY issued_at DESC, id DESC
            LIMIT 1
            """,
            (username, now),
        )
        row = cursor.fetchone()
        if row:
            return MuteRecord(
                id=row["id"],
                username=row["username"],
                admin_username=row["admin_username"],
                reason=row["reason"],
                issued_at=row["issued_at"],
                expires_at=row["expires_at"],
            )
        return None

    def get_all_muted_users(self) -> list[str]:
        """Get a list of all currently muted usernames."""
        now = datetime.now().isoformat()
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT DISTINCT username FROM mutes WHERE expires_at IS NULL OR expires_at > ?",
            (now,)
        )
        return [row["username"] for row in cursor.fetchall()]

    def search_active_mute_records(
        self,
        query: str = "",
        *,
        limit: int = 25,
        offset: int = 0,
    ) -> list[MuteRecord]:
        """Search latest active mute records without loading the full mute table."""
        now = datetime.now().isoformat()
        term = username_key(query)
        limit = max(1, min(int(limit), 100))
        offset = max(0, int(offset))
        cursor = self._conn.cursor()
        cursor.execute(
            """
            WITH ranked_active_mutes AS (
                SELECT
                    id,
                    username,
                    admin_username,
                    reason,
                    issued_at,
                    expires_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY username COLLATE BINARY
                        ORDER BY issued_at DESC, id DESC
                    ) AS row_number
                FROM mutes
                WHERE (expires_at IS NULL OR expires_at > ?)
                  AND INSTR(USERNAME_KEY(username), ?) > 0
            )
            SELECT id, username, admin_username, reason, issued_at, expires_at
            FROM ranked_active_mutes
            WHERE row_number = 1
            ORDER BY
                CASE
                    WHEN USERNAME_KEY(username) = ? THEN 0
                    WHEN INSTR(USERNAME_KEY(username), ?) = 1 THEN 1
                    ELSE 2
                END,
                USERNAME_KEY(username),
                username COLLATE BINARY
            LIMIT ?
            OFFSET ?
            """,
            (now, term, term, term, limit, offset),
        )
        return [
            MuteRecord(
                id=row["id"],
                username=row["username"],
                admin_username=row["admin_username"],
                reason=row["reason"],
                issued_at=row["issued_at"],
                expires_at=row["expires_at"],
            )
            for row in cursor.fetchall()
        ]

    def count_active_muted_users(self, query: str = "") -> int:
        """Count currently muted usernames matching an optional search term."""
        now = datetime.now().isoformat()
        term = username_key(query)
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM (
                SELECT username
                FROM mutes
                WHERE (expires_at IS NULL OR expires_at > ?)
                  AND INSTR(USERNAME_KEY(username), ?) > 0
                GROUP BY username COLLATE BINARY
            )
            """,
            (now, term),
        )
        row = cursor.fetchone()
        return int(row["count"] if row else 0)

    def search_active_muted_users(
        self,
        query: str = "",
        *,
        limit: int = 25,
        offset: int = 0,
    ) -> list[str]:
        """Search currently muted usernames without loading the full mute list."""
        return [
            record.username
            for record in self.search_active_mute_records(
                query,
                limit=limit,
                offset=offset,
            )
        ]

    def get_approved_users(self) -> list[tuple[str, int]]:
        """Return (username, trust_level) for every approved user account."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT username, trust_level FROM users WHERE approved = 1"
        )
        return [(row["username"], row["trust_level"]) for row in cursor.fetchall()]

    # Table operations

    @staticmethod
    def _serialize_active_human_offline_elapsed(
        table: Table,
        now: float,
    ) -> float | None:
        """Serialize elapsed online-server time for the abandonment timer."""
        if table._offline_since is None:
            return None
        return max(0.0, now - table._offline_since)

    @staticmethod
    def _restore_active_human_offline_since(
        elapsed: float | None,
        now: float,
    ) -> float | None:
        """Rebuild a runtime timestamp without counting server downtime."""
        if elapsed is None:
            return None
        return now - max(0.0, float(elapsed))

    def save_table(self, table: Table) -> None:
        """Save a table to the database."""
        cursor = self._conn.cursor()
        saved_at = time.time()

        # Serialize members
        members_json = json.dumps(
            [
                {"username": m.username, "is_spectator": m.is_spectator}
                for m in table.members
            ]
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO tables (
                table_id,
                game_type,
                host,
                members_json,
                game_json,
                status,
                is_private,
                table_state_json,
                active_human_offline_elapsed,
                checkpoint_kind,
                checkpoint_created_at,
                checkpoint_expires_at,
                checkpoint_operation_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                table.table_id,
                table.game_type,
                table.host,
                members_json,
                table.game_json,
                table.status,
                # Keep the legacy scalar populated during the compatibility
                # window; table_state_json is the canonical extensible state.
                int(table.is_private),
                table.serialize_saved_state(),
                self._serialize_active_human_offline_elapsed(table, saved_at),
                "manual",
                datetime.fromtimestamp(saved_at).isoformat(),
                None,
                "",
            ),
        )

    def load_table(self, table_id: str) -> Table | None:
        """Load a table from the database."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM tables WHERE table_id = ?", (table_id,))
        row = cursor.fetchone()
        if not row:
            return None

        # Deserialize members
        members_data = json.loads(row["members_json"])
        from ..tables.table import TableMember

        members = [
            TableMember(username=m["username"], is_spectator=m["is_spectator"])
            for m in members_data
        ]

        table = Table(
            table_id=row["table_id"],
            game_type=row["game_type"],
            host=row["host"],
            members=members,
            game_json=row["game_json"],
            status=row["status"],
            is_private=bool(row["is_private"]),
        )
        table.restore_saved_state(
            Table.deserialize_saved_state(row["table_state_json"])
        )
        table._checkpoint_kind = (
            row["checkpoint_kind"]
            if "checkpoint_kind" in row.keys()
            else "legacy"
        )
        table._checkpoint_created_at = (
            row["checkpoint_created_at"]
            if "checkpoint_created_at" in row.keys()
            else ""
        )
        table._offline_since = self._restore_active_human_offline_since(
            row["active_human_offline_elapsed"],
            time.time(),
        )
        return table

    def load_all_tables(self) -> list[Table]:
        """Load all tables from the database in a single query."""
        from ..tables.table import TableMember
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT
                table_id,
                game_type,
                host,
                members_json,
                game_json,
                status,
                is_private,
                table_state_json,
                active_human_offline_elapsed,
                checkpoint_kind,
                checkpoint_created_at,
                checkpoint_expires_at
            FROM tables
            ORDER BY checkpoint_created_at DESC, table_id
            """
        )
        tables = []
        restored_at = time.time()
        for row in cursor.fetchall():
            try:
                if self._table_checkpoint_is_expired(
                    row["checkpoint_created_at"],
                    row["checkpoint_expires_at"],
                ):
                    continue
                members_data = json.loads(row["members_json"])
                if not isinstance(members_data, list):
                    raise TypeError("members_json must contain a list")
                members = [
                    TableMember(username=m["username"], is_spectator=m["is_spectator"])
                    for m in members_data
                ]
                table = Table(
                    table_id=row["table_id"],
                    game_type=row["game_type"],
                    host=row["host"],
                    members=members,
                    game_json=row["game_json"],
                    status=row["status"],
                    is_private=bool(row["is_private"]),
                )
                table.restore_saved_state(
                    Table.deserialize_saved_state(row["table_state_json"])
                )
                table._checkpoint_kind = row["checkpoint_kind"] or "legacy"
                table._checkpoint_created_at = row["checkpoint_created_at"] or ""
                table._offline_since = self._restore_active_human_offline_since(
                    row["active_human_offline_elapsed"],
                    restored_at,
                )
                tables.append(table)
            except Exception as exc:
                raise sqlite3.DatabaseError(
                    "could not restore durable table checkpoint "
                    f"{row['table_id']!r}: {exc}"
                ) from exc
        return tables

    @staticmethod
    def _table_checkpoint_is_expired(
        created_at: str | None,
        expires_at: str | None,
    ) -> bool:
        """Return whether a transient table checkpoint is outside its TTL."""
        now_timestamp = time.time()

        def now_for(value: datetime) -> datetime:
            return datetime.fromtimestamp(now_timestamp, tz=value.tzinfo)

        if expires_at:
            expiration = datetime.fromisoformat(expires_at)
            if expiration <= now_for(expiration):
                return True
        if created_at:
            creation = datetime.fromisoformat(created_at)
            if creation < now_for(creation) - timedelta(
                days=TRANSIENT_TABLE_CHECKPOINT_RETENTION_DAYS
            ):
                return True
        return False

    def delete_table(self, table_id: str) -> None:
        """Delete a table from the database."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM tables WHERE table_id = ?", (table_id,))

    def delete_all_tables(self) -> None:
        """Delete all tables from the database."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM tables")

    def save_all_tables(
        self,
        tables: list[Table],
        *,
        checkpoint_kind: str = "shutdown",
        checkpoint_expires_at: str | None = None,
        checkpoint_operation_id: str = "",
    ) -> None:
        """Save multiple tables in a single transaction."""
        checkpoint_saved_at = time.time()
        checkpoint_created_at = datetime.fromtimestamp(
            checkpoint_saved_at
        ).isoformat()
        with self._transaction(immediate=True) as cursor:
            cursor.execute("DELETE FROM tables")
            for table in tables:
                members_json = json.dumps(
                    [
                        {"username": m.username, "is_spectator": m.is_spectator}
                        for m in table.members
                    ]
                )
                cursor.execute(
                    """
                    INSERT INTO tables (
                        table_id,
                        game_type,
                        host,
                        members_json,
                        game_json,
                        status,
                        is_private,
                        table_state_json,
                        active_human_offline_elapsed,
                        checkpoint_kind,
                        checkpoint_created_at,
                        checkpoint_expires_at,
                        checkpoint_operation_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        table.table_id,
                        table.game_type,
                        table.host,
                        members_json,
                        table.game_json,
                        table.status,
                        int(table.is_private),
                        table.serialize_saved_state(),
                        self._serialize_active_human_offline_elapsed(
                            table,
                            checkpoint_saved_at,
                        ),
                        checkpoint_kind,
                        checkpoint_created_at,
                        checkpoint_expires_at,
                        checkpoint_operation_id,
                    ),
                )

    # Saved table operations (user-saved game states)

    def save_user_table(
        self,
        username: str,
        save_name: str,
        game_type: str,
        game_json: str,
        members_json: str,
        table_state_json: str = "{}",
    ) -> SavedTableRecord:
        """Save a table state to a user's saved tables."""
        username = self._canonical_username_or_input(username)
        saved_at = datetime.now().isoformat()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO saved_tables (
                username,
                save_name,
                game_type,
                game_json,
                members_json,
                table_state_json,
                saved_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                username,
                save_name,
                game_type,
                game_json,
                members_json,
                table_state_json,
                saved_at,
            ),
        )

        return SavedTableRecord(
            id=cursor.lastrowid,
            username=username,
            save_name=save_name,
            game_type=game_type,
            game_json=game_json,
            members_json=members_json,
            saved_at=saved_at,
            table_state_json=table_state_json,
        )

    @staticmethod
    def _saved_table_record_from_row(row: sqlite3.Row) -> SavedTableRecord:
        """Build one saved-table record through the shared schema boundary."""
        return SavedTableRecord(
            id=row["id"],
            username=row["username"],
            save_name=row["save_name"],
            game_type=row["game_type"],
            game_json=row["game_json"],
            members_json=row["members_json"],
            saved_at=row["saved_at"],
            table_state_json=row["table_state_json"],
        )

    def count_user_saved_tables(self, username: str) -> int:
        """Count saved tables for a user without loading every row."""
        username = self._canonical_username_or_input(username)
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS count FROM saved_tables WHERE username = ? COLLATE BINARY",
            (username,),
        )
        row = cursor.fetchone()
        return int(row["count"] if row else 0)

    def get_user_saved_tables(
        self,
        username: str,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[SavedTableRecord]:
        """Get saved tables for a user, optionally limited for paginated menus."""
        username = self._canonical_username_or_input(username)
        cursor = self._conn.cursor()
        query = "SELECT * FROM saved_tables WHERE username = ? COLLATE BINARY ORDER BY saved_at DESC"
        params: list[object] = [username]
        if limit is not None:
            safe_limit = max(1, int(limit))
            safe_offset = max(0, int(offset))
            query += " LIMIT ? OFFSET ?"
            params.extend([safe_limit, safe_offset])
        cursor.execute(query, tuple(params))
        return [
            self._saved_table_record_from_row(row)
            for row in cursor.fetchall()
        ]

    def get_saved_table(
        self,
        save_id: int,
        *,
        username: str | None = None,
    ) -> SavedTableRecord | None:
        """Get a saved table by ID, optionally restricted to its owner."""
        cursor = self._conn.cursor()
        if username is None:
            cursor.execute("SELECT * FROM saved_tables WHERE id = ?", (save_id,))
        else:
            canonical_username = self._canonical_username_or_input(username)
            cursor.execute(
                "SELECT * FROM saved_tables "
                "WHERE id = ? AND username = ? COLLATE BINARY",
                (save_id, canonical_username),
            )
        row = cursor.fetchone()
        if not row:
            return None

        return self._saved_table_record_from_row(row)

    def delete_saved_table(
        self,
        save_id: int,
        *,
        username: str | None = None,
    ) -> bool:
        """Delete a saved table, optionally restricted to its owner."""
        cursor = self._conn.cursor()
        if username is None:
            cursor.execute("DELETE FROM saved_tables WHERE id = ?", (save_id,))
        else:
            canonical_username = self._canonical_username_or_input(username)
            cursor.execute(
                "DELETE FROM saved_tables "
                "WHERE id = ? AND username = ? COLLATE BINARY",
                (save_id, canonical_username),
            )
        return cursor.rowcount > 0

    # Game result operations (statistics)

    def save_game_result(
        self,
        game_type: str,
        timestamp: str,
        duration_ticks: int,
        players: list[tuple[str, str, bool]],  # (player_id, player_name, is_bot)
        custom_data: dict | None = None,
    ) -> int:
        """
        Save a game result to the database.

        Args:
            game_type: The game type identifier
            timestamp: ISO format timestamp
            duration_ticks: Game duration in ticks
            players: List of (player_id, player_name, is_bot) tuples
            custom_data: Game-specific result data

        Returns:
            The result ID
        """
        with self._transaction(immediate=True) as cursor:
            return self._save_game_result_in_transaction(
                cursor,
                game_type,
                timestamp,
                duration_ticks,
                players,
                custom_data,
            )

    def _save_game_result_in_transaction(
        self,
        cursor: sqlite3.Cursor,
        game_type: str,
        timestamp: str,
        duration_ticks: int,
        players: list[tuple[str, str, bool]],
        custom_data: dict | None,
    ) -> int:
        """Persist one result and its derived records atomically."""

        # Insert the main result record
        cursor.execute(
            """
            INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data)
            VALUES (?, ?, ?, ?)
            """,
            (
                game_type,
                timestamp,
                duration_ticks,
                json.dumps(custom_data) if custom_data else None,
            ),
        )
        result_id = cursor.lastrowid

        # Insert player records
        for player_id, player_name, is_bot in players:
            cursor.execute(
                """
                INSERT INTO game_result_players (result_id, player_id, player_name, is_bot)
                VALUES (?, ?, ?, ?)
                """,
                (result_id, player_id, player_name, 1 if is_bot else 0),
            )

        # Update player_game_stats
        from ..game_utils.game_result import GameResult, PlayerResult
        from ..game_utils.stats_extractor import StatsExtractor

        # We temporarily build a GameResult just for the extractor
        gr = GameResult(
            game_type=game_type,
            timestamp=datetime.now().isoformat(),
            duration_ticks=duration_ticks,
            player_results=[PlayerResult(player_id=pid, player_name=name, is_bot=is_bot) for pid, name, is_bot in players],
            custom_data=custom_data or {}
        )

        if gr.has_human_players():
            updates = StatsExtractor.extract_incremental_stats(gr)
            for p_id, stats in updates.items():
                for stat_key, stat_value in stats.items():
                    if stat_key.endswith("_high"):
                        # Built-in high_score is stored without the helper suffix.
                        # Custom max leaderboards keep their full stat key so the
                        # leaderboard and personal-stats queries can read them back.
                        base_key = "high_score" if stat_key == "high_score_high" else stat_key
                        cursor.execute("""
                            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(player_id, game_type, stat_key)
                            DO UPDATE SET stat_value = MAX(stat_value, excluded.stat_value)
                        """, (p_id, game_type, base_key, float(stat_value)))
                    else:
                        # For others (wins, total_score, games_played), use SUM
                        cursor.execute("""
                            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(player_id, game_type, stat_key)
                            DO UPDATE SET stat_value = stat_value + excluded.stat_value
                        """, (p_id, game_type, stat_key, float(stat_value)))

        return result_id

    def get_player_game_history(
        self,
        player_id: str,
        game_type: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        Get a player's game history.

        Args:
            player_id: The player ID to look up
            game_type: Optional filter by game type
            limit: Maximum number of results

        Returns:
            List of game result dictionaries
        """
        cursor = self._conn.cursor()

        if game_type:
            cursor.execute(
                """
                SELECT gr.id, gr.game_type, gr.timestamp, gr.duration_ticks, gr.custom_data
                FROM game_results gr
                INNER JOIN game_result_players grp ON gr.id = grp.result_id
                WHERE grp.player_id = ? AND gr.game_type = ?
                ORDER BY gr.timestamp DESC
                LIMIT ?
                """,
                (player_id, game_type, limit),
            )
        else:
            cursor.execute(
                """
                SELECT gr.id, gr.game_type, gr.timestamp, gr.duration_ticks, gr.custom_data
                FROM game_results gr
                INNER JOIN game_result_players grp ON gr.id = grp.result_id
                WHERE grp.player_id = ?
                ORDER BY gr.timestamp DESC
                LIMIT ?
                """,
                (player_id, limit),
            )

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "game_type": row["game_type"],
                "timestamp": row["timestamp"],
                "duration_ticks": row["duration_ticks"],
                "custom_data": json.loads(row["custom_data"]) if row["custom_data"] else {},
            })
        return results

    def get_game_result_players(self, result_id: int) -> list[dict]:
        """Get all players for a specific game result."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT player_id, player_name, is_bot
            FROM game_result_players
            WHERE result_id = ?
            """,
            (result_id,),
        )
        return [
            {
                "player_id": row["player_id"],
                "player_name": row["player_name"],
                "is_bot": bool(row["is_bot"]),
            }
            for row in cursor.fetchall()
        ]

    def get_game_stats(self, game_type: str, limit: int | None = None) -> list[tuple]:
        """
        Get game results for a game type.

        Args:
            game_type: The game type to query
            limit: Optional maximum number of results

        Returns:
            List of tuples: (id, game_type, timestamp, duration_ticks, custom_data)
        """
        cursor = self._conn.cursor()

        if limit:
            cursor.execute(
                """
                SELECT id, game_type, timestamp, duration_ticks, custom_data
                FROM game_results
                WHERE game_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (game_type, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, game_type, timestamp, duration_ticks, custom_data
                FROM game_results
                WHERE game_type = ?
                ORDER BY timestamp DESC
                """,
                (game_type,),
            )

        return [
            (row["id"], row["game_type"], row["timestamp"], row["duration_ticks"], row["custom_data"])
            for row in cursor.fetchall()
        ]

    def get_game_stats_aggregate(self, game_type: str) -> dict:
        """
        Get aggregate statistics for a game type.

        Returns:
            Dictionary with total_games, total_duration_ticks, etc.
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_games,
                SUM(duration_ticks) as total_duration,
                AVG(duration_ticks) as avg_duration
            FROM game_results
            WHERE game_type = ?
            """,
            (game_type,),
        )
        row = cursor.fetchone()
        return {
            "total_games": row["total_games"] or 0,
            "total_duration_ticks": row["total_duration"] or 0,
            "avg_duration_ticks": row["avg_duration"] or 0,
        }

    def get_player_stats(self, player_id: str, game_type: str | None = None) -> dict:
        """
        Get statistics for a player.

        Args:
            player_id: The player ID
            game_type: Optional filter by game type

        Returns:
            Dictionary with games_played, etc.
        """
        cursor = self._conn.cursor()

        if game_type:
            cursor.execute(
                """
                SELECT COUNT(*) as games_played
                FROM game_result_players grp
                INNER JOIN game_results gr ON grp.result_id = gr.id
                WHERE grp.player_id = ? AND gr.game_type = ?
                """,
                (player_id, game_type),
            )
        else:
            cursor.execute(
                """
                SELECT COUNT(*) as games_played
                FROM game_result_players
                WHERE player_id = ?
                """,
                (player_id,),
            )

        row = cursor.fetchone()
        return {
            "games_played": row["games_played"] or 0,
        }

    def get_top_player_game_stats(self, game_type: str, stat_key: str, limit: int = 10) -> list[tuple[str, str, float]]:
        """
        Get the top players for a specific stat in a specific game.
        Returns list of (player_id, player_name, stat_value).
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT pgs.player_id, u.username as player_name, pgs.stat_value
            FROM player_game_stats pgs
            LEFT JOIN users u ON pgs.player_id = u.uuid
            WHERE pgs.game_type = ? AND pgs.stat_key = ?
            ORDER BY
                CAST(pgs.stat_value AS REAL) DESC,
                USERNAME_KEY(COALESCE(u.username, pgs.player_id)) ASC,
                COALESCE(u.username, pgs.player_id) COLLATE BINARY ASC,
                pgs.player_id ASC
            LIMIT ?
            """,
            (game_type, stat_key, limit),
        )
        return [(row["player_id"], row["player_name"] or row["player_id"], row["stat_value"]) for row in cursor.fetchall()]

    def get_top_wins_with_losses(self, game_type: str, limit: int = 10) -> list[tuple[str, str, float, float]]:
        """
        Get the top players by wins along with their losses to avoid N+1 queries.
        Returns list of (player_id, player_name, wins, losses).
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT
                pgs_w.player_id,
                u.username as player_name,
                pgs_w.stat_value as wins,
                COALESCE(pgs_l.stat_value, 0) as losses
            FROM player_game_stats pgs_w
            LEFT JOIN player_game_stats pgs_l
                ON pgs_w.player_id = pgs_l.player_id AND pgs_w.game_type = pgs_l.game_type AND pgs_l.stat_key = 'losses'
            LEFT JOIN users u ON pgs_w.player_id = u.uuid
            WHERE pgs_w.game_type = ? AND pgs_w.stat_key = 'wins'
            ORDER BY
                CAST(pgs_w.stat_value AS REAL) DESC,
                CAST(COALESCE(pgs_l.stat_value, 0) AS REAL) ASC,
                USERNAME_KEY(COALESCE(u.username, pgs_w.player_id)) ASC,
                COALESCE(u.username, pgs_w.player_id) COLLATE BINARY ASC,
                pgs_w.player_id ASC
            LIMIT ?
            """,
            (game_type, limit),
        )
        return [(row["player_id"], row["player_name"] or row["player_id"], row["wins"], row["losses"]) for row in cursor.fetchall()]

    def get_top_ratio_stats(self, game_type: str, num_key: str, denom_key: str) -> list[tuple[str, str, float, float]]:
        """
        Get numerator and denominator stats for all players for a game type, returning them so they can be sorted.
        Returns list of (player_id, player_name, total_num, total_denom).
        """
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT p_num.player_id, u.username AS player_name,
                   CAST(p_num.stat_value AS REAL) AS num_value, CAST(p_denom.stat_value AS REAL) AS denom_value
            FROM player_game_stats p_num
            JOIN player_game_stats p_denom
                ON p_num.player_id = p_denom.player_id
               AND p_num.game_type = p_denom.game_type
               AND p_denom.stat_key = ?
            LEFT JOIN users u ON p_num.player_id = u.uuid
            WHERE p_num.game_type = ? AND p_num.stat_key = ?
        """, (denom_key, game_type, num_key))
        return [
            (row["player_id"], row["player_name"] or row["player_id"], row["num_value"], row["denom_value"])
            for row in cursor.fetchall()
        ]

    def get_user_name_by_uuid(self, uuid: str) -> str | None:
        """Look up a username by UUID efficiently."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT username FROM users WHERE uuid = ?", (uuid,))
        row = cursor.fetchone()
        return row["username"] if row else None

    def get_all_player_game_stats(self, player_id: str, game_type: str) -> dict[str, float]:
        """Get all pre-calculated stats for a specific player and game."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT stat_key, stat_value
            FROM player_game_stats
            WHERE player_id = ? AND game_type = ?
            """,
            (player_id, game_type)
        )
        return {row["stat_key"]: row["stat_value"] for row in cursor.fetchall()}

    # Server Setting Operations

    @staticmethod
    def _validate_server_setting_key(setting_key: str) -> str:
        """Return a canonical internal setting key or reject programmer error."""
        if not isinstance(setting_key, str) or not setting_key:
            raise ValueError("Server setting keys must be non-empty strings")
        return setting_key

    def get_boolean_server_setting(
        self,
        setting_key: str,
        *,
        default: bool,
    ) -> bool:
        """Read one persistent Boolean setting with a schema-safe default."""
        key = self._validate_server_setting_key(setting_key)
        row = self._conn.execute(
            "SELECT value_json FROM server_settings WHERE setting_key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return bool(default)
        try:
            value = json.loads(str(row["value_json"]))
        except (TypeError, ValueError, json.JSONDecodeError):
            value = None
        if type(value) is bool:
            return value
        raise ValueError(
            f"Server setting {key!r} does not contain a Boolean value"
        )

    def set_boolean_server_setting(
        self,
        setting_key: str,
        value: bool,
    ) -> None:
        """Atomically insert or replace one persistent Boolean setting."""
        key = self._validate_server_setting_key(setting_key)
        if type(value) is not bool:
            raise TypeError("Boolean server settings require a bool value")
        updated_at_utc = datetime.now(timezone.utc).isoformat(
            timespec="microseconds"
        )
        self._conn.execute(
            """
            INSERT INTO server_settings (
                setting_key, value_json, updated_at_utc
            ) VALUES (?, ?, ?)
            ON CONFLICT(setting_key) DO UPDATE SET
                value_json = excluded.value_json,
                updated_at_utc = excluded.updated_at_utc
            """,
            (key, json.dumps(value), updated_at_utc),
        )

    # SMTP Config Operations

    def get_smtp_config(self) -> SmtpConfig | None:
        """Get the current SMTP configuration."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT host, port, username, password, from_email, from_name, encryption_type FROM smtp_config WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return SmtpConfig(
                host=row["host"],
                port=row["port"],
                username=row["username"],
                password=row["password"],
                from_email=row["from_email"],
                from_name=row["from_name"],
                encryption_type=row["encryption_type"]
            )
        return None

    def update_smtp_config(self, host: str, port: int, username: str, password: str, from_email: str, from_name: str, encryption_type: str) -> None:
        """Update the SMTP configuration."""
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO smtp_config (id, host, port, username, password, from_email, from_name, encryption_type)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        """, (host, port, username, password, from_email, from_name, encryption_type))

    # Password Reset Token Operations

    def save_password_reset_token(self, user_uuid: str, token_hash: str, expires_at: str) -> None:
        """Save a new password reset token and delete any existing ones for this user."""
        now = datetime.now().isoformat()
        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                "DELETE FROM password_reset_tokens WHERE user_uuid = ?",
                (user_uuid,),
            )
            cursor.execute(
                """
                INSERT INTO password_reset_tokens (
                    user_uuid, token_hash, created_at, expires_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (user_uuid, token_hash, now, expires_at),
            )

    def get_password_reset_token(self, user_uuid: str) -> dict | None:
        """Get the active password reset token for a user."""
        now = datetime.now().isoformat()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT token_hash, expires_at
            FROM password_reset_tokens
            WHERE user_uuid = ?
              AND julianday(expires_at) IS NOT NULL
              AND julianday(expires_at) > julianday(?)
        """, (user_uuid, now))
        row = cursor.fetchone()
        if row:
            return {"token_hash": row["token_hash"], "expires_at": row["expires_at"]}
        return None

    def delete_password_reset_token(self, user_uuid: str) -> None:
        """Delete all password reset tokens for a user."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM password_reset_tokens WHERE user_uuid = ?", (user_uuid,))

    # Social / Friend Operations

    def send_friend_request(self, requester_id: str, receiver_id: str) -> str:
        """
        Send a friend request. Returns the status:
        'sent': Request sent successfully.
        'accepted': They had already sent one to you, so it was mutually accepted.
        'duplicate': Already pending.
        'already_friends': Already accepted.
        'blocked_by_you': The requester has blocked the receiver.
        'blocked': The receiver has blocked the requester.
        'self': Both UUIDs identify the same account.
        'unknown': At least one UUID no longer identifies an account.
        """
        if requester_id == receiver_id:
            return "self"
        now = datetime.now().isoformat()
        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                "SELECT COUNT(DISTINCT uuid) AS count FROM users WHERE uuid IN (?, ?)",
                (requester_id, receiver_id),
            )
            if int(cursor.fetchone()["count"]) != 2:
                return "unknown"
            cursor.execute(
                """
                SELECT blocker_id FROM user_blocks
                WHERE (blocker_id = ? AND blocked_id = ?)
                   OR (blocker_id = ? AND blocked_id = ?)
                """,
                (requester_id, receiver_id, receiver_id, requester_id),
            )
            block_rows = cursor.fetchall()
            if any(row["blocker_id"] == requester_id for row in block_rows):
                return "blocked_by_you"
            if block_rows:
                return "blocked"

            cursor.execute(
                """
                SELECT status, requester_id FROM friendships
                WHERE (requester_id = ? AND receiver_id = ?)
                   OR (requester_id = ? AND receiver_id = ?)
                """,
                (requester_id, receiver_id, receiver_id, requester_id),
            )

            row = cursor.fetchone()
            if row:
                status = row["status"]
                existing_requester = row["requester_id"]
                if status == "accepted":
                    return "already_friends"
                if status == "pending":
                    if existing_requester == requester_id:
                        return "duplicate"
                    cursor.execute(
                        """
                        UPDATE friendships SET status = 'accepted'
                        WHERE requester_id = ? AND receiver_id = ?
                        """,
                        (existing_requester, requester_id),
                    )
                    return "accepted"

            cursor.execute(
                """
                INSERT INTO friendships (
                    requester_id, receiver_id, status, created_at
                )
                VALUES (?, ?, 'pending', ?)
                """,
                (requester_id, receiver_id, now),
            )
            return "sent"

    def accept_friend_request(self, requester_id: str, receiver_id: str) -> bool:
        """Atomically accept an unblocked pending friend request."""
        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                """
                SELECT 1 FROM user_blocks
                WHERE (blocker_id = ? AND blocked_id = ?)
                   OR (blocker_id = ? AND blocked_id = ?)
                LIMIT 1
                """,
                (requester_id, receiver_id, receiver_id, requester_id),
            )
            if cursor.fetchone() is not None:
                return False
            cursor.execute(
                """
                UPDATE friendships SET status = 'accepted'
                WHERE requester_id = ? AND receiver_id = ? AND status = 'pending'
                """,
                (requester_id, receiver_id),
            )
            return cursor.rowcount > 0

    def decline_friend_request(self, requester_id: str, receiver_id: str) -> bool:
        """Delete only the specified incoming request, never a newer relationship."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            DELETE FROM friendships
            WHERE requester_id = ? AND receiver_id = ? AND status = 'pending'
            """,
            (requester_id, receiver_id),
        )
        return cursor.rowcount > 0

    def remove_friendship(self, user1_id: str, user2_id: str) -> bool:
        """Remove a friendship or pending request."""
        cursor = self._conn.cursor()
        cursor.execute("""
            DELETE FROM friendships
            WHERE (requester_id = ? AND receiver_id = ?)
               OR (requester_id = ? AND receiver_id = ?)
        """, (user1_id, user2_id, user2_id, user1_id))
        return cursor.rowcount > 0

    def get_friends(self, user_id: str) -> list[str]:
        """Get a list of accepted friend UUIDs."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT requester_id, receiver_id FROM friendships
            WHERE status = 'accepted' AND (requester_id = ? OR receiver_id = ?)
        """, (user_id, user_id))

        friends = []
        for row in cursor.fetchall():
            if row["requester_id"] == user_id:
                friends.append(row["receiver_id"])
            else:
                friends.append(row["requester_id"])
        return friends

    def count_pending_incoming_requests(self, user_id: str) -> int:
        """Count pending incoming friend requests without loading every row."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) AS count FROM friendships
            WHERE receiver_id = ? AND status = 'pending'
        """, (user_id,))
        row = cursor.fetchone()
        return int(row["count"] if row else 0)

    def get_pending_incoming_requests(
        self,
        user_id: str,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[str]:
        """Get UUIDs who sent a pending friend request to this user."""
        cursor = self._conn.cursor()
        query = """
            SELECT requester_id FROM friendships
            WHERE receiver_id = ? AND status = 'pending'
            ORDER BY created_at ASC, requester_id ASC
        """
        params: list[object] = [user_id]
        if limit is not None:
            safe_limit = max(1, int(limit))
            safe_offset = max(0, int(offset))
            query += " LIMIT ? OFFSET ?"
            params.extend([safe_limit, safe_offset])
        cursor.execute(query, tuple(params))
        return [row["requester_id"] for row in cursor.fetchall()]

    def has_blocked(self, blocker_id: str, blocked_id: str) -> bool:
        """Return whether one account has directionally blocked another."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM user_blocks
            WHERE blocker_id = ? AND blocked_id = ?
            LIMIT 1
            """,
            (blocker_id, blocked_id),
        )
        return cursor.fetchone() is not None

    def has_block_between(self, user1_id: str, user2_id: str) -> bool:
        """Return whether either account has blocked the other."""
        if user1_id == user2_id:
            return False
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM user_blocks
            WHERE (blocker_id = ? AND blocked_id = ?)
               OR (blocker_id = ? AND blocked_id = ?)
            LIMIT 1
            """,
            (user1_id, user2_id, user2_id, user1_id),
        )
        return cursor.fetchone() is not None

    def get_socially_blocked_ids(self, user_id: str) -> set[str]:
        """Return all UUIDs separated from this account by either block direction."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT blocked_id AS other_id FROM user_blocks WHERE blocker_id = ?
            UNION
            SELECT blocker_id AS other_id FROM user_blocks WHERE blocked_id = ?
            """,
            (user_id, user_id),
        )
        return {str(row["other_id"]) for row in cursor.fetchall()}

    def get_social_peer_ids(self, user_id: str) -> set[str]:
        """Return every account connected by a request, friendship, or block."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT receiver_id AS other_id FROM friendships WHERE requester_id = ?
            UNION
            SELECT requester_id AS other_id FROM friendships WHERE receiver_id = ?
            UNION
            SELECT blocked_id AS other_id FROM user_blocks WHERE blocker_id = ?
            UNION
            SELECT blocker_id AS other_id FROM user_blocks WHERE blocked_id = ?
            """,
            (user_id, user_id, user_id, user_id),
        )
        return {str(row["other_id"]) for row in cursor.fetchall()}

    def count_blocked_users(self, blocker_id: str) -> int:
        """Count valid accounts directionally blocked by this account."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM user_blocks
            JOIN users ON users.uuid = user_blocks.blocked_id
            WHERE user_blocks.blocker_id = ?
            """,
            (blocker_id,),
        )
        row = cursor.fetchone()
        return int(row["count"] if row else 0)

    def has_pending_friend_request(
        self, requester_id: str, receiver_id: str
    ) -> bool:
        """Return whether one exact incoming request is still pending."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM friendships
            WHERE requester_id = ? AND receiver_id = ? AND status = 'pending'
            LIMIT 1
            """,
            (requester_id, receiver_id),
        )
        return cursor.fetchone() is not None

    def get_blocked_users(
        self,
        blocker_id: str,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[str]:
        """Return directionally blocked UUIDs in stable username order."""
        cursor = self._conn.cursor()
        query = """
            SELECT user_blocks.blocked_id
            FROM user_blocks
            JOIN users ON users.uuid = user_blocks.blocked_id
            WHERE user_blocks.blocker_id = ?
            ORDER BY users.username_key ASC, users.username ASC
        """
        params: list[object] = [blocker_id]
        if limit is not None:
            safe_limit = max(1, int(limit))
            safe_offset = max(0, int(offset))
            query += " LIMIT ? OFFSET ?"
            params.extend([safe_limit, safe_offset])
        cursor.execute(query, tuple(params))
        return [str(row["blocked_id"]) for row in cursor.fetchall()]

    def block_user(self, blocker_id: str, blocked_id: str) -> str:
        """Persist a block and atomically remove every direct social tie.

        Blocks live until explicit unblocking or either account is deleted.
        The write also removes accepted friendships, requests in either
        direction, and queued relationship notifications between the pair.
        """
        if blocker_id == blocked_id:
            return "self"
        now = datetime.now().isoformat()
        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                "SELECT uuid, username FROM users WHERE uuid IN (?, ?)",
                (blocker_id, blocked_id),
            )
            users = {
                str(row["uuid"]): str(row["username"])
                for row in cursor.fetchall()
            }
            if blocker_id not in users or blocked_id not in users:
                return "unknown"

            cursor.execute(
                """
                SELECT 1 FROM user_blocks
                WHERE blocker_id = ? AND blocked_id = ?
                LIMIT 1
                """,
                (blocker_id, blocked_id),
            )
            if cursor.fetchone() is not None:
                return "already_blocked"

            cursor.execute(
                """
                DELETE FROM friendships
                WHERE (requester_id = ? AND receiver_id = ?)
                   OR (requester_id = ? AND receiver_id = ?)
                """,
                (blocker_id, blocked_id, blocked_id, blocker_id),
            )
            cursor.execute(
                """
                DELETE FROM user_notifications
                WHERE (user_id = ? AND source_username = ? COLLATE BINARY)
                   OR (user_id = ? AND source_username = ? COLLATE BINARY)
                """,
                (
                    blocker_id,
                    users[blocked_id],
                    blocked_id,
                    users[blocker_id],
                ),
            )
            cursor.execute(
                """
                INSERT INTO user_blocks (blocker_id, blocked_id, created_at)
                VALUES (?, ?, ?)
                """,
                (blocker_id, blocked_id, now),
            )
        return "blocked"

    def unblock_user(self, blocker_id: str, blocked_id: str) -> bool:
        """Remove one directional block without recreating prior relationships."""
        cursor = self._conn.cursor()
        cursor.execute(
            "DELETE FROM user_blocks WHERE blocker_id = ? AND blocked_id = ?",
            (blocker_id, blocked_id),
        )
        return cursor.rowcount > 0

    def add_notification(self, user_id: str, source_username: str, event_type: str) -> bool:
        """Atomically add an offline social notification for two valid accounts."""
        now = datetime.now().isoformat()
        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                "SELECT 1 FROM users WHERE uuid = ? LIMIT 1",
                (user_id,),
            )
            if cursor.fetchone() is None:
                return False
            cursor.execute(
                """
                SELECT uuid, username FROM users
                WHERE username = ? COLLATE BINARY
                LIMIT 1
                """,
                (source_username,),
            )
            source = cursor.fetchone()
            if source is None:
                return False
            cursor.execute(
                """
                SELECT 1 FROM user_blocks
                WHERE (blocker_id = ? AND blocked_id = ?)
                   OR (blocker_id = ? AND blocked_id = ?)
                LIMIT 1
                """,
                (user_id, source["uuid"], source["uuid"], user_id),
            )
            if cursor.fetchone() is not None:
                return False
            cursor.execute(
                """
                INSERT INTO user_notifications (
                    user_id, source_username, event_type, created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (user_id, source["username"], event_type, now),
            )
            return cursor.rowcount > 0

    def get_and_clear_notifications(self, user_id: str) -> list[dict]:
        """Retrieve and immediately delete all notifications for a user."""
        with self._transaction(immediate=True) as cursor:
            cursor.execute(
                """
                SELECT notification.source_username, notification.event_type
                FROM user_notifications AS notification
                LEFT JOIN users AS source
                    ON source.username = notification.source_username COLLATE BINARY
                WHERE notification.user_id = ?
                  AND NOT EXISTS (
                    SELECT 1 FROM user_blocks
                    WHERE source.uuid IS NOT NULL
                      AND (
                        (blocker_id = notification.user_id AND blocked_id = source.uuid)
                        OR
                        (blocker_id = source.uuid AND blocked_id = notification.user_id)
                      )
                  )
                ORDER BY notification.created_at ASC
                """,
                (user_id,),
            )
            notifications = [
                {
                    "source_username": row["source_username"],
                    "event_type": row["event_type"],
                }
                for row in cursor.fetchall()
            ]
            cursor.execute(
                "DELETE FROM user_notifications WHERE user_id = ?",
                (user_id,),
            )

        return notifications

    # Player rating operations

    def get_player_rating(
        self, player_id: str, game_type: str
    ) -> tuple[float, float] | None:
        """
        Get a player's rating for a game type.

        Returns:
            (mu, sigma) tuple or None if no rating exists
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT mu, sigma FROM player_ratings
            WHERE player_id = ? AND game_type = ?
            """,
            (player_id, game_type),
        )
        row = cursor.fetchone()
        if row:
            return (row["mu"], row["sigma"])
        return None

    def set_player_rating(
        self, player_id: str, game_type: str, mu: float, sigma: float
    ) -> None:
        """Set or update a player's rating for a game type."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO player_ratings (player_id, game_type, mu, sigma)
            VALUES (?, ?, ?, ?)
            """,
            (player_id, game_type, mu, sigma),
        )

    def get_rating_leaderboard(
        self, game_type: str, limit: int = 10
    ) -> list[tuple[str, str, float, float]]:
        """
        Get the rating leaderboard for a game type.

        Returns:
            List of (player_id, player_name, mu, sigma) tuples sorted by ordinal descending
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT pr.player_id, u.username as player_name, pr.mu, pr.sigma,
                   (pr.mu - 3 * pr.sigma) as ordinal
            FROM player_ratings pr
            LEFT JOIN users u ON pr.player_id = u.uuid
            WHERE pr.game_type = ?
            ORDER BY ordinal DESC
            LIMIT ?
            """,
            (game_type, limit),
        )
        return [(row["player_id"], row["player_name"] or row["player_id"], row["mu"], row["sigma"]) for row in cursor.fetchall()]
