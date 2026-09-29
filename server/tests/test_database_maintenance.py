"""Whole-server database maintenance barrier tests."""

from __future__ import annotations

import asyncio
import sqlite3
import threading
from pathlib import Path

import pytest

from ..core.maintenance import (
    DatabaseMaintenanceBusyError,
    DatabaseMaintenanceUnavailableError,
)
from ..core.power import PowerAction
from ..core.server import Server
from ..persistence.database import (
    Database,
    DatabaseBackupResult,
    DatabaseStorageAnalysis,
)
from ..users.identity import username_key
from ..users.network_user import NetworkUser


class CapturingClient:
    def __init__(self, *, username: str | None = None, authenticated: bool = False):
        self.sent_messages: list[dict] = []
        self.username = username
        self.authenticated = authenticated
        self.retired = False
        self.closed = False
        self.ip_address = "127.0.0.1"
        self.address = "127.0.0.1:12345"

    async def send(self, packet: dict) -> None:
        self.sent_messages.append(packet)

    async def close(self) -> None:
        self.closed = True


def _make_server(tmp_path) -> Server:
    server = Server(
        db_path=tmp_path / "maintenance.sqlite",
        database_backup_dir=tmp_path / "backups",
    )
    server.db.connect()
    return server


@pytest.mark.asyncio
async def test_storage_analysis_runs_without_freezing_and_serializes_maintenance(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    started = threading.Event()
    release = threading.Event()

    def controlled_analysis(_db_path: Path, _backup_dir: Path) -> DatabaseStorageAnalysis:
        started.set()
        assert release.wait(timeout=5)
        return DatabaseStorageAnalysis(
            analyzed_at_utc="2026-09-26T00:00:00+00:00",
            database_size_bytes=4096,
            page_size_bytes=4096,
            free_page_count=0,
            categories=(),
            incomplete_backup_file_count=0,
            incomplete_backup_file_bytes=0,
            invalid_timestamp_values=0,
        )

    monkeypatch.setattr(
        "server.core.maintenance._perform_storage_analysis_worker",
        controlled_analysis,
    )
    analysis_task = asyncio.create_task(
        server.maintenance_manager.analyze_storage()
    )
    try:
        for _ in range(100):
            if started.is_set():
                break
            await asyncio.sleep(0.01)
        assert started.is_set()
        assert server.maintenance_manager.is_active is False
        assert server.maintenance_manager.is_busy is True
        assert server.maintenance_manager._storage_idle_event.is_set() is False
        assert server.db._conn is not None

        with pytest.raises(DatabaseMaintenanceBusyError):
            await server.maintenance_manager.back_up_database(
                requested_by="Developer"
            )
        with pytest.raises(RuntimeError, match="database maintenance"):
            server.power_manager.schedule(
                action=PowerAction.REBOOT,
                delay_seconds=60,
                requested_by="Developer",
                reason_id="maintenance",
            )
    finally:
        release.set()
        result = await analysis_task
        assert result.database_size_bytes == 4096
        assert server.maintenance_manager.is_busy is False
        assert server.maintenance_manager._storage_idle_event.is_set() is True
        server.db.close()


@pytest.mark.asyncio
async def test_cancelled_storage_analysis_remains_busy_until_worker_exits(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    started = threading.Event()
    release = threading.Event()

    def controlled_analysis(_db_path: Path, _backup_dir: Path) -> DatabaseStorageAnalysis:
        started.set()
        assert release.wait(timeout=5)
        return DatabaseStorageAnalysis(
            analyzed_at_utc="2026-09-26T00:00:00+00:00",
            database_size_bytes=4096,
            page_size_bytes=4096,
            free_page_count=0,
            categories=(),
            incomplete_backup_file_count=0,
            incomplete_backup_file_bytes=0,
            invalid_timestamp_values=0,
        )

    monkeypatch.setattr(
        "server.core.maintenance._perform_storage_analysis_worker",
        controlled_analysis,
    )
    analysis_task = asyncio.create_task(
        server.maintenance_manager.analyze_storage()
    )
    try:
        for _ in range(100):
            if started.is_set():
                break
            await asyncio.sleep(0.01)
        assert started.is_set()

        analysis_task.cancel()
        await asyncio.sleep(0)
        analysis_task.cancel()
        await asyncio.sleep(0)
        storage_idle = asyncio.create_task(
            server.maintenance_manager.wait_until_storage_idle()
        )
        await asyncio.sleep(0)
        assert analysis_task.done() is False
        assert storage_idle.done() is False
        assert server.maintenance_manager.is_busy is True

        release.set()
        with pytest.raises(asyncio.CancelledError):
            await analysis_task
        await storage_idle
        assert server.maintenance_manager.is_busy is False
    finally:
        release.set()
        if not analysis_task.done():
            with pytest.raises(asyncio.CancelledError):
                await analysis_task
        server.db.close()


@pytest.mark.asyncio
async def test_maintenance_keeps_sockets_responsive_and_blocks_all_state_changes(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    started = threading.Event()
    release = threading.Event()
    backup_path = tmp_path / "backups" / "simulated.sqlite3"

    def controlled_backup(_db_path: Path, _backup_dir: Path) -> DatabaseBackupResult:
        started.set()
        assert release.wait(timeout=5)
        return DatabaseBackupResult(
            path=backup_path,
            size_bytes=123,
            page_count=1,
            created_at_utc="2026-09-26T00:00:00+00:00",
        )

    monkeypatch.setattr(
        "server.core.maintenance._perform_backup_worker",
        controlled_backup,
    )

    record = server.db.create_user("Online", "hash")
    online_client = CapturingClient(username="Online", authenticated=True)
    online_user = NetworkUser(
        "Online",
        "en",
        online_client,
        uuid=record.uuid,
        approved=True,
    )
    server.users[online_user.username] = online_user

    operation_task = asyncio.create_task(
        server.maintenance_manager.back_up_database(requested_by="Developer")
    )
    logout_task: asyncio.Task[None] | None = None
    try:
        for _ in range(100):
            if started.is_set():
                break
            await asyncio.sleep(0.01)
        assert started.is_set()
        assert server.maintenance_manager.is_active
        assert server.db._conn is None

        await server._on_client_message(
            online_client,
            {
                "type": "menu",
                "menu_id": "turn_menu",
                "selection_id": "play_card",
            },
        )
        assert online_client.sent_messages[-1]["type"] == "speak"
        assert "database backup is in progress" in online_client.sent_messages[-1][
            "text"
        ]

        unauthenticated = CapturingClient()
        await server._on_client_message(
            unauthenticated,
            {"type": "authorize", "locale": "en"},
        )
        assert unauthenticated.sent_messages == [
            {
                "type": "login_failed",
                "reason": "server_maintenance",
                "error": "server_maintenance",
                "status": "error",
                "text": (
                    "Server database maintenance is in progress. Login, "
                    "registration, and password changes are temporarily "
                    "unavailable. Please try again after maintenance finishes."
                ),
                "reconnect": False,
            }
        ]

        for request_type, response_type in (
            ("register", "register_response"),
            ("request_password_reset", "request_password_reset_response"),
            ("submit_reset_code", "submit_reset_code_response"),
        ):
            blocked_auth_client = CapturingClient()
            await server._on_client_message(
                blocked_auth_client,
                {"type": request_type, "locale": "en"},
            )
            assert blocked_auth_client.sent_messages == [
                {
                    "type": response_type,
                    "reason": "server_maintenance",
                    "error": "server_maintenance",
                    "status": "error",
                    "text": (
                        "Server database maintenance is in progress. Login, "
                        "registration, and password changes are temporarily "
                        "unavailable. Please try again after maintenance finishes."
                    ),
                    "reconnect": False,
                }
            ]

        before_ping = len(online_client.sent_messages)
        await server._on_client_message(online_client, {"type": "ping"})
        assert len(online_client.sent_messages) == before_ping + 1
        assert online_client.sent_messages[-1]["type"] == "pong"

        logout_task = asyncio.create_task(
            server._on_client_message(online_client, {"type": "logout"})
        )
        await asyncio.sleep(0)
        assert logout_task.done() is False
        assert online_user.username in server.users
    finally:
        release.set()
        result = await operation_task
        assert result.path == backup_path
        assert server.maintenance_manager.is_active is False
        assert server.db.get_user("Online").uuid == record.uuid
        if logout_task is not None:
            await logout_task
            assert online_client.sent_messages[-1] == {"type": "force_exit"}
            assert online_client.closed is True
            assert online_user.username not in server.users
        server.db.close()


@pytest.mark.asyncio
async def test_maintenance_drains_inflight_work_before_closing_database(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    holder_started = asyncio.Event()
    release_holder = asyncio.Event()
    worker_started = threading.Event()

    async def hold_server_work() -> None:
        assert server.maintenance_manager.begin_tracked_work()
        try:
            holder_started.set()
            await release_holder.wait()
            assert server.db._conn is not None
        finally:
            server.maintenance_manager.end_tracked_work()

    def backup_worker(_db_path: Path, _backup_dir: Path) -> DatabaseBackupResult:
        worker_started.set()
        return DatabaseBackupResult(
            path=tmp_path / "backups" / "simulated.sqlite3",
            size_bytes=1,
            page_count=1,
            created_at_utc="2026-09-26T00:00:00+00:00",
        )

    monkeypatch.setattr(
        "server.core.maintenance._perform_backup_worker",
        backup_worker,
    )

    holder_task = asyncio.create_task(hold_server_work())
    await holder_started.wait()
    maintenance_task = asyncio.create_task(
        server.maintenance_manager.back_up_database(requested_by="Developer")
    )
    try:
        await asyncio.sleep(0.05)
        assert server.maintenance_manager.is_active
        assert worker_started.is_set() is False
        assert server.db._conn is not None

        release_holder.set()
        await holder_task
        await maintenance_task
        assert worker_started.is_set()
        assert server.db._conn is not None
    finally:
        release_holder.set()
        if not holder_task.done():
            await holder_task
        if not maintenance_task.done():
            await maintenance_task
        server.db.close()


@pytest.mark.asyncio
async def test_cancelled_maintenance_reports_worker_success_truthfully(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    started = threading.Event()
    release = threading.Event()
    backup_path = tmp_path / "backups" / "completed.sqlite3"

    def controlled_backup(_db_path: Path, _backup_dir: Path) -> DatabaseBackupResult:
        started.set()
        assert release.wait(timeout=5)
        return DatabaseBackupResult(
            path=backup_path,
            size_bytes=1,
            page_count=1,
            created_at_utc="2026-09-27T00:00:00+00:00",
        )

    monkeypatch.setattr(
        "server.core.maintenance._perform_backup_worker",
        controlled_backup,
    )
    operation_task = asyncio.create_task(
        server.maintenance_manager.back_up_database(requested_by="Developer")
    )
    try:
        for _ in range(100):
            if started.is_set():
                break
            await asyncio.sleep(0.01)
        assert started.is_set()

        operation_task.cancel()
        await asyncio.sleep(0)
        operation_task.cancel()
        await asyncio.sleep(0)
        assert operation_task.done() is False
        release.set()

        result = await operation_task
        assert result.path == backup_path
        assert server.maintenance_manager.is_active is False
        assert server.db._conn is not None
    finally:
        release.set()
        if not operation_task.done():
            await operation_task
        server.db.close()


@pytest.mark.asyncio
async def test_cancelled_maintenance_preserves_post_publication_failure(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    started = threading.Event()
    release = threading.Event()

    def controlled_compaction(_db_path: Path, _backup_dir: Path):
        started.set()
        assert release.wait(timeout=5)
        error = OSError("simulated uncertain publication")
        Database._add_sqlite_failure_note(
            error,
            operation="compaction",
            stage="atomically publish compacted database",
            path=server.db.db_path,
            replacement_applied=True,
        )
        raise error

    monkeypatch.setattr(
        "server.core.maintenance._perform_compaction_worker",
        controlled_compaction,
    )
    operation_task = asyncio.create_task(
        server.maintenance_manager.compact_database(requested_by="Developer")
    )
    try:
        for _ in range(100):
            if started.is_set():
                break
            await asyncio.sleep(0.01)
        assert started.is_set()

        operation_task.cancel()
        await asyncio.sleep(0)
        release.set()
        with pytest.raises(DatabaseMaintenanceUnavailableError):
            await operation_task

        assert server.maintenance_manager.is_active is True
        assert server.db._conn is None
    finally:
        release.set()
        if server.db._conn is None:
            server.db.connect()
        server.maintenance_manager._active_operation = None
        server.maintenance_manager._resume_event.set()
        server.db.close()


@pytest.mark.asyncio
async def test_second_maintenance_request_fails_instead_of_queueing(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    started = threading.Event()
    release = threading.Event()
    worker_calls = 0

    def controlled_backup(_db_path: Path, _backup_dir: Path) -> DatabaseBackupResult:
        nonlocal worker_calls
        worker_calls += 1
        started.set()
        assert release.wait(timeout=5)
        return DatabaseBackupResult(
            path=tmp_path / "backups" / "simulated.sqlite3",
            size_bytes=1,
            page_count=1,
            created_at_utc="2026-09-26T00:00:00+00:00",
        )

    monkeypatch.setattr(
        "server.core.maintenance._perform_backup_worker",
        controlled_backup,
    )
    first = asyncio.create_task(
        server.maintenance_manager.back_up_database(requested_by="Developer")
    )
    try:
        for _ in range(100):
            if started.is_set():
                break
            await asyncio.sleep(0.01)
        assert started.is_set()

        with pytest.raises(DatabaseMaintenanceBusyError):
            await server.maintenance_manager.back_up_database(
                requested_by="Developer"
            )
        assert worker_calls == 1
    finally:
        release.set()
        await first
        server.db.close()


@pytest.mark.asyncio
async def test_failed_compaction_retains_backup_and_resumes_validated_database(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    retained = server.db.create_user("Retained", "hash")

    def fail_vacuum(_connection) -> None:
        raise sqlite3.OperationalError("simulated compaction disk I/O error")

    monkeypatch.setattr(
        "server.persistence.database.Database._vacuum_connection",
        staticmethod(fail_vacuum),
    )
    try:
        with pytest.raises(sqlite3.OperationalError, match="disk I/O error"):
            await server.maintenance_manager.compact_database(
                requested_by="Developer"
            )

        assert server.maintenance_manager.is_active is False
        assert server.db._conn is not None
        assert server.db.get_user("Retained").uuid == retained.uuid
        backups = list((tmp_path / "backups").glob("*.sqlite3"))
        assert len(backups) == 1
        assert "pre-compaction" in backups[0].name
    finally:
        server.db.close()


@pytest.mark.asyncio
async def test_post_publication_compaction_failure_remains_fail_closed(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    retained = server.db.create_user("Retained", "hash")
    original_flush = Database._flush_directory_to_disk
    flush_calls = 0

    def fail_compaction_publication_flush(path: Path) -> None:
        nonlocal flush_calls
        flush_calls += 1
        if flush_calls == 2:
            raise OSError("simulated post-replacement directory fsync failure")
        original_flush(path)

    monkeypatch.setattr(
        Database,
        "_flush_directory_to_disk",
        staticmethod(fail_compaction_publication_flush),
    )
    with pytest.raises(DatabaseMaintenanceUnavailableError):
        await server.maintenance_manager.compact_database(
            requested_by="Developer"
        )

    assert flush_calls == 2
    assert server.maintenance_manager.is_active is True
    assert server.db._conn is None
    backups = list((tmp_path / "backups").glob("*.sqlite3"))
    assert len(backups) == 1
    connection = sqlite3.connect(server.db.db_path)
    connection.create_function(
        "USERNAME_KEY_V3",
        1,
        username_key,
        deterministic=True,
    )
    try:
        assert connection.execute(
            "SELECT uuid FROM users WHERE username = 'Retained'"
        ).fetchone()[0] == retained.uuid
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        connection.close()

    # Restore the fixture while preserving the production fail-closed assertion.
    server.db.connect()
    server.maintenance_manager._active_operation = None
    server.maintenance_manager._resume_event.set()
    server.db.close()


@pytest.mark.asyncio
async def test_reopen_failure_keeps_server_frozen_and_database_disconnected(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _make_server(tmp_path)
    original_connect = server.db.connect

    def backup_worker(_db_path: Path, _backup_dir: Path) -> DatabaseBackupResult:
        return DatabaseBackupResult(
            path=tmp_path / "backups" / "simulated.sqlite3",
            size_bytes=1,
            page_count=1,
            created_at_utc="2026-09-26T00:00:00+00:00",
        )

    def fail_reconnect(**_kwargs) -> None:
        raise RuntimeError("simulated reopen failure")

    monkeypatch.setattr(
        "server.core.maintenance._perform_backup_worker",
        backup_worker,
    )
    monkeypatch.setattr(server.db, "connect", fail_reconnect)

    with pytest.raises(DatabaseMaintenanceUnavailableError):
        await server.maintenance_manager.back_up_database(requested_by="Developer")

    assert server.maintenance_manager.is_active
    assert server.db._conn is None
    blocked_client = CapturingClient()
    await server._on_client_message(
        blocked_client,
        {"type": "register", "locale": "en"},
    )
    assert blocked_client.sent_messages[-1]["error"] == "server_maintenance"

    waiter = asyncio.create_task(
        server.maintenance_manager.begin_tracked_work_when_available()
    )
    await asyncio.sleep(0)
    assert not waiter.done()
    server._stopping = True
    server.maintenance_manager.wake_blocked_work_for_shutdown()
    assert await waiter is False

    # Restore the test fixture without weakening the production fail-closed state.
    monkeypatch.setattr(server.db, "connect", original_connect)
    original_connect()
    server.maintenance_manager._active_operation = None
    server.maintenance_manager._resume_event.set()
    server.db.close()
