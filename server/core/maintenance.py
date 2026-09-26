"""Reversible, fail-closed server maintenance for SQLite operations."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from ..audio import AudioCommand
from ..messages.localization import Localization
from ..persistence.database import (
    Database,
    DatabaseBackupResult,
    DatabaseCompactionResult,
    DatabaseStorageAnalysis,
    DatabaseStorageCleanupResult,
)

if TYPE_CHECKING:
    from ..network.websocket_server import ClientConnection
    from ..users.network_user import NetworkUser
    from .server import Server


logger = logging.getLogger(__name__)

DATABASE_MAINTENANCE_DRAIN_TIMEOUT_SECONDS = 30.0
DEFAULT_DATABASE_BACKUP_DIR = Path(__file__).resolve().parents[1] / "backups"

_ResultT = TypeVar("_ResultT")


class DatabaseMaintenanceKind(str, Enum):
    """Supported whole-server database maintenance operations."""

    BACKUP = "backup"
    CLEANUP = "cleanup"
    COMPACTION = "compaction"


@dataclass(frozen=True)
class ActiveDatabaseMaintenance:
    """Runtime-only description of the current maintenance barrier."""

    kind: DatabaseMaintenanceKind
    requested_by: str
    started_at_utc: str


@dataclass(frozen=True)
class DatabaseCompactionOperationResult:
    """Compaction statistics plus its pre-operation recovery snapshot."""

    compaction: DatabaseCompactionResult
    safety_backup: DatabaseBackupResult


@dataclass(frozen=True)
class DatabaseStorageCleanupOperationResult:
    """Safe cleanup statistics plus its pre-operation recovery snapshot."""

    cleanup: DatabaseStorageCleanupResult
    safety_backup: DatabaseBackupResult


class DatabaseMaintenanceBusyError(RuntimeError):
    """Raised when another exclusive server operation prevents maintenance."""


class DatabaseMaintenanceUnavailableError(RuntimeError):
    """Raised when the live database cannot be reopened after maintenance."""


def _perform_backup_worker(
    db_path: Path,
    backup_dir: Path,
) -> DatabaseBackupResult:
    database = Database(db_path)
    database.connect()
    try:
        return database.backup_database(backup_dir, purpose="manual")
    finally:
        database.close()


def _perform_compaction_worker(
    db_path: Path,
    backup_dir: Path,
) -> DatabaseCompactionOperationResult:
    database = Database(db_path)
    database.connect()
    try:
        safety_backup = database.backup_database(
            backup_dir,
            purpose="pre-compaction",
        )
        logger.info(
            "Created pre-compaction database safety backup at %s",
            safety_backup.path,
        )
        compaction = database.compact_database()
        return DatabaseCompactionOperationResult(
            compaction=compaction,
            safety_backup=safety_backup,
        )
    finally:
        database.close()


def _perform_storage_cleanup_worker(
    db_path: Path,
    backup_dir: Path,
) -> DatabaseStorageCleanupOperationResult:
    database = Database(db_path)
    database.connect()
    try:
        safety_backup = database.backup_database(
            backup_dir,
            purpose="pre-cleanup",
        )
        logger.info(
            "Created pre-cleanup database safety backup at %s",
            safety_backup.path,
        )
        cleanup = database.clean_storage()
        return DatabaseStorageCleanupOperationResult(
            cleanup=cleanup,
            safety_backup=safety_backup,
        )
    finally:
        database.close()


def _perform_storage_analysis_worker(
    db_path: Path,
    backup_dir: Path,
) -> DatabaseStorageAnalysis:
    database = Database(db_path)
    database.connect()
    try:
        return database.analyze_storage_cleanup(backup_dir)
    finally:
        database.close()


class ServerMaintenanceManager:
    """Serialize database maintenance while keeping client sockets responsive.

    Maintenance is deliberately fail-closed. Game ticks stop first, new packet
    work is rejected, already-running handlers drain, and only then is the live
    SQLite connection closed. The blocking SQLite operation runs on a worker
    thread using its own connection. Gameplay resumes only after the main
    connection has reopened and passed its normal integrity validation.
    """

    def __init__(
        self,
        server: "Server",
        *,
        backup_dir: str | Path | None = None,
    ) -> None:
        self.server = server
        self.backup_dir = Path(
            backup_dir if backup_dir is not None else DEFAULT_DATABASE_BACKUP_DIR
        ).resolve()
        self._active_operation: ActiveDatabaseMaintenance | None = None
        self._operation_lock = asyncio.Lock()
        self._resume_event = asyncio.Event()
        self._resume_event.set()
        self._storage_idle_event = asyncio.Event()
        self._storage_idle_event.set()
        self._tracked_work: dict[asyncio.Task[Any], int] = {}
        self._work_changed = asyncio.Event()

    @property
    def active_operation(self) -> ActiveDatabaseMaintenance | None:
        return self._active_operation

    @property
    def is_active(self) -> bool:
        return self._active_operation is not None

    @property
    def is_busy(self) -> bool:
        """Return whether any database worker currently owns serialization."""
        return self.is_active or self._operation_lock.locked()

    def begin_tracked_work(self) -> bool:
        """Register event-loop work unless the maintenance barrier is active."""
        if self.is_active:
            return False
        task = asyncio.current_task()
        if task is None:
            raise RuntimeError("Tracked server work requires an asyncio task")
        self._tracked_work[task] = self._tracked_work.get(task, 0) + 1
        return True

    def end_tracked_work(self) -> None:
        task = asyncio.current_task()
        if task is None or task not in self._tracked_work:
            raise RuntimeError("Unbalanced tracked server work")
        depth = self._tracked_work[task] - 1
        if depth:
            self._tracked_work[task] = depth
        else:
            self._tracked_work.pop(task, None)
        self._work_changed.set()

    async def begin_tracked_work_when_available(self) -> bool:
        """Wait for the barrier, then register work without a resume race."""
        while True:
            if self.server._stopping and self.server.db._conn is None:
                return False
            if not await self.wait_until_resumed():
                return False
            if self.begin_tracked_work():
                return True

    def wake_blocked_work_for_shutdown(self) -> None:
        """Wake fail-closed waiters so transport shutdown cannot deadlock."""
        if self.server._stopping and self.server.db._conn is None:
            self._resume_event.set()

    async def wait_until_resumed(self) -> bool:
        """Wait for normal work, or return false for fail-closed shutdown."""
        while self.is_active:
            if self.server._stopping and self.server.db._conn is None:
                return False
            await self._resume_event.wait()
        return True

    async def wait_until_storage_idle(self) -> None:
        """Wait until no worker can still be reading or rewriting SQLite."""
        await self._storage_idle_event.wait()

    async def back_up_database(self, *, requested_by: str) -> DatabaseBackupResult:
        return await self._run_operation(
            DatabaseMaintenanceKind.BACKUP,
            requested_by=requested_by,
            worker=lambda: _perform_backup_worker(
                self.server.db.db_path,
                self.backup_dir,
            ),
        )

    async def compact_database(
        self,
        *,
        requested_by: str,
    ) -> DatabaseCompactionOperationResult:
        return await self._run_operation(
            DatabaseMaintenanceKind.COMPACTION,
            requested_by=requested_by,
            worker=lambda: _perform_compaction_worker(
                self.server.db.db_path,
                self.backup_dir,
            ),
        )

    async def analyze_storage(self) -> DatabaseStorageAnalysis:
        """Return a non-mutating cleanup preview without freezing gameplay."""
        if self.is_busy:
            raise DatabaseMaintenanceBusyError(
                "A database maintenance operation is already active"
            )
        async with self._operation_lock:
            if self.is_active:
                raise DatabaseMaintenanceBusyError(
                    "A database maintenance operation is already active"
                )
            if self.server.power_manager.is_scheduled:
                raise DatabaseMaintenanceBusyError(
                    "Storage analysis cannot start during a scheduled server power operation"
                )
            self._storage_idle_event.clear()
            analysis_task = asyncio.create_task(
                asyncio.to_thread(
                    _perform_storage_analysis_worker,
                    self.server.db.db_path,
                    self.backup_dir,
                )
            )
            try:
                return await asyncio.shield(analysis_task)
            except asyncio.CancelledError:
                # Cancelling the coroutine cannot stop SQLite work already
                # running in a thread. Keep shutdown blocked until it exits.
                try:
                    await analysis_task
                except BaseException as worker_exc:
                    logger.exception(
                        "Storage analysis worker failed after cancellation",
                        exc_info=worker_exc,
                    )
                raise
            finally:
                self._storage_idle_event.set()

    async def clean_storage(
        self,
        *,
        requested_by: str,
    ) -> DatabaseStorageCleanupOperationResult:
        return await self._run_operation(
            DatabaseMaintenanceKind.CLEANUP,
            requested_by=requested_by,
            worker=lambda: _perform_storage_cleanup_worker(
                self.server.db.db_path,
                self.backup_dir,
            ),
        )

    async def _run_operation(
        self,
        kind: DatabaseMaintenanceKind,
        *,
        requested_by: str,
        worker: Callable[[], _ResultT],
    ) -> _ResultT:
        # Do not silently queue a second destructive/expensive operation. An
        # accidental double activation must receive an immediate busy result.
        if self.is_busy:
            raise DatabaseMaintenanceBusyError(
                "A database maintenance operation is already active"
            )
        async with self._operation_lock:
            if self.is_active:
                raise DatabaseMaintenanceBusyError(
                    "A database maintenance operation is already active"
                )
            if self.server.power_manager.is_scheduled:
                raise DatabaseMaintenanceBusyError(
                    "Database maintenance cannot start during a scheduled server power operation"
                )

            operation = ActiveDatabaseMaintenance(
                kind=kind,
                requested_by=requested_by,
                started_at_utc=datetime.now(timezone.utc).isoformat(),
            )
            self._active_operation = operation
            self._resume_event.clear()
            self._storage_idle_event.clear()
            tick_scheduler_was_running = self.server._tick_scheduler is not None
            database_available = self.server.db._conn is not None
            result: _ResultT | None = None
            operation_error: BaseException | None = None
            reconnect_error: BaseException | None = None
            terminal_notice_sent = False

            logger.info(
                "Starting database %s requested by %s",
                kind.value,
                requested_by,
            )

            try:
                await self.server._pause_ticks_for_database_maintenance()
                await self._broadcast_notice(
                    f"database-maintenance-{kind.value}-started"
                )
                await self._wait_for_other_work_to_drain()

                connection = self.server.db._conn
                if connection is None:
                    raise RuntimeError("The live database is not connected")
                if connection.in_transaction:
                    raise RuntimeError(
                        "The live database still has an active transaction"
                    )

                self.server.db.close()
                database_available = False
                worker_task = asyncio.create_task(asyncio.to_thread(worker))
                try:
                    result = await asyncio.shield(worker_task)
                except asyncio.CancelledError as exc:
                    # A thread cannot be safely cancelled in the middle of a
                    # backup or VACUUM. Wait for it before reopening SQLite.
                    operation_error = exc
                    try:
                        await worker_task
                    except BaseException as worker_exc:
                        logger.exception(
                            "Database maintenance worker failed after cancellation",
                            exc_info=worker_exc,
                        )
                except BaseException as exc:
                    operation_error = exc

                try:
                    self.server.db.connect()
                    database_available = True
                except BaseException as exc:
                    reconnect_error = exc
                finally:
                    self._storage_idle_event.set()

                if reconnect_error is not None:
                    logger.critical(
                        "Database maintenance finished but the live database could not be reopened; "
                        "the server will remain frozen",
                        exc_info=(
                            type(reconnect_error),
                            reconnect_error,
                            reconnect_error.__traceback__,
                        ),
                    )
                    await self._broadcast_notice(
                        "database-maintenance-reopen-failed"
                    )
                    terminal_notice_sent = True
                    raise DatabaseMaintenanceUnavailableError(
                        "The live database could not be reopened after maintenance"
                    ) from reconnect_error

                if operation_error is not None:
                    await self._broadcast_notice(
                        f"database-maintenance-{kind.value}-failed"
                    )
                    terminal_notice_sent = True
                    raise operation_error

                await self._broadcast_notice(
                    f"database-maintenance-{kind.value}-completed"
                )
                terminal_notice_sent = True
                assert result is not None
                logger.info(
                    "Completed database %s requested by %s",
                    kind.value,
                    requested_by,
                )
                return result
            except BaseException as exc:
                if self.server.db._conn is not None:
                    database_available = True
                if not isinstance(exc, DatabaseMaintenanceUnavailableError):
                    if not self._storage_idle_event.is_set():
                        self._storage_idle_event.set()
                    if database_available and not terminal_notice_sent:
                        await self._broadcast_notice(
                            f"database-maintenance-{kind.value}-failed"
                        )
                        terminal_notice_sent = True
                    if not isinstance(exc, asyncio.CancelledError):
                        logger.error(
                            "Database maintenance operation could not complete",
                            exc_info=(type(exc), exc, exc.__traceback__),
                        )
                raise
            finally:
                if database_available:
                    self._active_operation = None
                    self._resume_event.set()
                    self._storage_idle_event.set()
                    if tick_scheduler_was_running and not self.server._stopping:
                        await self.server._resume_ticks_after_database_maintenance()

    async def _wait_for_other_work_to_drain(self) -> None:
        current = asyncio.current_task()
        loop = asyncio.get_running_loop()
        deadline = loop.time() + DATABASE_MAINTENANCE_DRAIN_TIMEOUT_SECONDS

        while any(task is not current for task in self._tracked_work):
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise TimeoutError(
                    "Timed out waiting for in-flight server work to finish"
                )
            self._work_changed.clear()
            if not any(task is not current for task in self._tracked_work):
                break
            await asyncio.wait_for(self._work_changed.wait(), timeout=remaining)

    def status_text(self, locale: str) -> str:
        operation = self._active_operation
        if operation is None:
            return Localization.get(locale, "database-maintenance-not-active")
        return Localization.get(
            locale,
            "database-maintenance-input-blocked",
            operation=Localization.get(
                locale,
                f"database-maintenance-operation-{operation.kind.value}",
            ),
        )

    async def reject_packet(
        self,
        client: "ClientConnection",
        packet: dict[str, Any],
    ) -> None:
        """Return protocol-appropriate maintenance feedback without using SQLite."""
        user = self.server._active_user_for_client(client)
        locale = (
            user.locale
            if user is not None
            else str(packet.get("locale") or "en")
        )
        text = (
            self.status_text(locale)
            if user is not None
            else Localization.get(locale, "database-maintenance-auth-blocked")
        )
        packet_type = str(packet.get("type") or "")

        if user is not None:
            await client.send({"type": "speak", "text": text, "buffer": "system"})
            return

        response_types = {
            "authorize": "login_failed",
            "register": "register_response",
            "request_password_reset": "request_password_reset_response",
            "submit_reset_code": "submit_reset_code_response",
        }
        response_type = response_types.get(packet_type)
        if response_type is None:
            return
        response: dict[str, Any] = {
            "type": response_type,
            "reason": "server_maintenance",
            "error": "server_maintenance",
            "status": "error",
            "text": text,
            "reconnect": False,
        }
        await client.send(response)

    async def _broadcast_notice(self, localization_key: str) -> None:
        async def send_to_user(user: "NetworkUser") -> None:
            text = Localization.get(user.locale, localization_key)
            system_name = Localization.get(user.locale, "system-name")
            packets = (
                {
                    "type": "chat",
                    "convo": "announcement",
                    "sender": system_name,
                    "message": text,
                    "silent": True,
                },
                {"type": "speak", "text": text, "buffer": "system"},
                AudioCommand(
                    command="play",
                    kind="sfx",
                    family="notify",
                    buffer="system",
                ).to_packet(),
            )
            connection = getattr(user, "connection", None)
            if connection is None:
                # Unit/play-test users intentionally have no transport.
                user.speak_l(localization_key, buffer="system")
                user.play_sound_family("notify", buffer="system")
                return
            for outgoing in packets:
                await connection.send(outgoing)

        sends = [send_to_user(user) for user in tuple(self.server.users.values())]
        if sends:
            results = await asyncio.gather(*sends, return_exceptions=True)
            for result in results:
                if isinstance(result, BaseException):
                    logger.warning(
                        "Failed to deliver a database maintenance notice",
                        exc_info=(type(result), result, result.__traceback__),
                    )
