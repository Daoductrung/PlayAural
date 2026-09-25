"""Whole-server database maintenance barrier tests."""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path

import pytest

from ..core.maintenance import (
    DatabaseMaintenanceBusyError,
    DatabaseMaintenanceUnavailableError,
)
from ..core.server import Server
from ..persistence.database import DatabaseBackupResult
from ..users.network_user import NetworkUser


class CapturingClient:
    def __init__(self, *, username: str | None = None, authenticated: bool = False):
        self.sent_messages: list[dict] = []
        self.username = username
        self.authenticated = authenticated
        self.retired = False
        self.ip_address = "127.0.0.1"
        self.address = "127.0.0.1:12345"

    async def send(self, packet: dict) -> None:
        self.sent_messages.append(packet)


def _make_server(tmp_path) -> Server:
    server = Server(
        db_path=tmp_path / "maintenance.sqlite",
        database_backup_dir=tmp_path / "backups",
    )
    server.db.connect()
    return server


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
    finally:
        release.set()
        result = await operation_task
        assert result.path == backup_path
        assert server.maintenance_manager.is_active is False
        assert server.db.get_user("Online").uuid == record.uuid
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
    original_connect(prune=False, recover_corrupt=False)
    server.maintenance_manager._active_operation = None
    server.maintenance_manager._resume_event.set()
    server.db.close()
