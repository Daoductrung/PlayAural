"""Admin menu navigation and focus restoration tests."""

import os
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from ..core.server import Server
from ..administration.manager import (
    ADMIN_DATABASE_BACKUP_CONFIRM_MENU,
    ADMIN_DATABASE_COMPACT_CONFIRM_MENU,
    ADMIN_DATABASE_MENU,
    ADMIN_DATABASE_STORAGE_ANALYSIS_MENU,
    ADMIN_DATABASE_STORAGE_CLEANUP_CONFIRM_MENU,
    ADMIN_MODERATION_CLEAR_CONFIRM_MENU,
    ADMIN_MODERATION_CONTEXT_MENU,
    ADMIN_MODERATION_HISTORY_INPUT,
    ADMIN_MODERATION_HISTORY_MENU,
    ADMIN_MODERATION_MESSAGES_MENU,
    ADMIN_MODERATION_MESSAGE_LANGUAGE_MENU,
    ADMIN_MODERATION_MESSAGE_PERIOD_MENU,
    ADMIN_MODERATION_MENU,
    ADMIN_MODERATION_REPORT_DETAIL_MENU,
    ADMIN_MODERATION_REPORTS_MENU,
    ADMIN_MODERATION_SENDER_RESULTS_MENU,
    _localized_database_size,
)
from ..users.test_user import MockUser
from ..moderation.reports import AutomatedSpamEvidence
from ..persistence.retention import (
    ABANDONED_BACKUP_FRAGMENT_MINIMUM_AGE_SECONDS,
)


def _mark_backup_fragment_abandoned(path) -> None:
    old_timestamp = (
        datetime.now().timestamp()
        - ABANDONED_BACKUP_FRAGMENT_MINIMUM_AGE_SECONDS
        - 1
    )
    os.utime(path, (old_timestamp, old_timestamp))


def _current_menu(server: Server, username: str) -> str:
    return server._user_states.get(username, {}).get("menu", "")


def _make_admin_server(tmp_path):
    server = Server(
        db_path=tmp_path / "admin_nav.sqlite",
        database_backup_dir=tmp_path / "backups",
    )
    server._db.connect()
    record = server._db.create_user("Admin", "hash", trust_level=3)
    server._db.approve_user("Admin")
    admin = MockUser("Admin", uuid=record.uuid)
    admin.trust_level = 3
    server._users[admin.username] = admin
    server._show_main_menu(admin)
    return server, admin


def _create_approved_user(server: Server, username: str, trust_level: int = 1):
    record = server._db.create_user(username, "hash", trust_level=trust_level)
    server._db.approve_user(username)
    return record


def test_database_storage_sizes_are_compact_and_locale_aware(tmp_path) -> None:
    server, _developer = _make_admin_server(tmp_path)
    try:
        assert _localized_database_size("en", 1) == "1 byte"
        assert _localized_database_size("en", 1536) == "1.5 KiB"
        assert _localized_database_size("vi", 1536) == "1,5 KiB"
        assert _localized_database_size("en", 1024**2) == "1 MiB"
    finally:
        server._db.close()


async def _select(server: Server, user: MockUser, menu_id: str, selection_id: str) -> None:
    await server._handle_menu(
        SimpleNamespace(username=user.username),
        {
            "type": "menu",
            "menu_id": menu_id,
            "selection_id": selection_id,
        },
    )


def _menu_item_ids(user: MockUser, menu_id: str) -> list[str]:
    return [item.id for item in user.get_current_menu_items(menu_id) or []]


def _menu_item_text(user: MockUser, menu_id: str, item_id: str) -> str:
    for item in user.get_current_menu_items(menu_id) or []:
        if item.id == item_id:
            return item.text
    raise AssertionError(f"{item_id!r} not found in {menu_id!r}")


@pytest.mark.asyncio
async def test_database_management_compacts_with_confirmation_and_restores_focus(
    tmp_path,
) -> None:
    server, developer = _make_admin_server(tmp_path)
    try:
        retained = _create_approved_user(server, "Retained")
        for index in range(350):
            server._db.add_global_chat_message(
                retained.uuid,
                retained.username,
                "en",
                f"{index}:" + ("x" * 450),
            )
        server._db.clear_global_chat_messages()

        await _select(server, developer, "main_menu", "administration")
        assert "database_management" in _menu_item_ids(developer, "admin_menu")
        await _select(
            server,
            developer,
            "admin_menu",
            "database_management",
        )
        assert _current_menu(server, developer.username) == ADMIN_DATABASE_MENU
        summary = next(
            item
            for item in developer.get_current_menu_items(ADMIN_DATABASE_MENU)
            if item.id == "database_management_summary"
        )
        assert summary.read_only is True

        await _select(
            server,
            developer,
            ADMIN_DATABASE_MENU,
            "compact_database",
        )
        assert (
            _current_menu(server, developer.username)
            == ADMIN_DATABASE_COMPACT_CONFIRM_MENU
        )
        await _select(
            server,
            developer,
            ADMIN_DATABASE_COMPACT_CONFIRM_MENU,
            "database_compact_summary",
        )
        assert (
            _current_menu(server, developer.username)
            == ADMIN_DATABASE_COMPACT_CONFIRM_MENU
        )

        await _select(
            server,
            developer,
            ADMIN_DATABASE_COMPACT_CONFIRM_MENU,
            "confirm",
        )

        assert _current_menu(server, developer.username) == ADMIN_DATABASE_MENU
        assert "Database compaction completed" in developer.get_last_spoken()
        assert server._db.get_user("Retained") is not None
        assert server._db._conn.execute(
            "PRAGMA freelist_count"
        ).fetchone()[0] == 0
        safety_backups = list((tmp_path / "backups").glob("*-pre-compaction-*.sqlite3"))
        assert len(safety_backups) == 1

        await _select(server, developer, ADMIN_DATABASE_MENU, "back")
        assert _current_menu(server, developer.username) == "admin_menu"
        assert (
            developer.menus["admin_menu"]["selection_id"]
            == "database_management"
        )
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_database_storage_analysis_is_read_only_and_refreshable(tmp_path) -> None:
    server, developer = _make_admin_server(tmp_path)
    try:
        retained = _create_approved_user(server, "Storage Retained")
        old = (datetime.now() - timedelta(days=1000)).isoformat()
        expired = (datetime.now() - timedelta(days=1)).isoformat()
        server._db._conn.execute(
            """
            INSERT INTO saved_tables (
                username, save_name, game_type, game_json, members_json, saved_at
            ) VALUES (?, 'Ancient Save', 'pig', '{}', '[]', ?)
            """,
            (retained.username, old),
        )
        server._db.save_password_reset_token(
            retained.uuid,
            "expired-token",
            expired,
        )
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        partial = backup_dir / ".PlayAural-interrupted.sqlite3.partial"
        partial.write_bytes(b"partial")
        _mark_backup_fragment_abandoned(partial)

        await _select(server, developer, "main_menu", "administration")
        await _select(server, developer, "admin_menu", "database_management")
        await _select(
            server,
            developer,
            ADMIN_DATABASE_MENU,
            "analyze_storage",
        )

        assert (
            _current_menu(server, developer.username)
            == ADMIN_DATABASE_STORAGE_ANALYSIS_MENU
        )
        assert "Eligible database records: 1" in _menu_item_text(
            developer,
            ADMIN_DATABASE_STORAGE_ANALYSIS_MENU,
            "storage_analysis_summary",
        )
        assert "Expired password-reset tokens: 1" == _menu_item_text(
            developer,
            ADMIN_DATABASE_STORAGE_ANALYSIS_MENU,
            "storage_category_expired_password_reset_tokens",
        )
        assert "1 (7 bytes)" in _menu_item_text(
            developer,
            ADMIN_DATABASE_STORAGE_ANALYSIS_MENU,
            "storage_temporary_files",
        )
        assert "saved tables" in _menu_item_text(
            developer,
            ADMIN_DATABASE_STORAGE_ANALYSIS_MENU,
            "storage_exclusions",
        )
        assert all(
            item.read_only
            for item in developer.get_current_menu_items(
                ADMIN_DATABASE_STORAGE_ANALYSIS_MENU
            )
            if item.id.startswith("storage_")
        )

        await _select(
            server,
            developer,
            ADMIN_DATABASE_STORAGE_ANALYSIS_MENU,
            "storage_analysis_summary",
        )
        assert (
            _current_menu(server, developer.username)
            == ADMIN_DATABASE_STORAGE_ANALYSIS_MENU
        )
        await _select(
            server,
            developer,
            ADMIN_DATABASE_STORAGE_ANALYSIS_MENU,
            "refresh",
        )
        assert server._db._conn.execute(
            "SELECT COUNT(*) FROM password_reset_tokens"
        ).fetchone()[0] == 1
        assert server._db._conn.execute(
            "SELECT COUNT(*) FROM saved_tables"
        ).fetchone()[0] == 1
        assert partial.exists()
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_database_storage_cleanup_is_backed_up_and_preserves_saved_tables(
    tmp_path,
) -> None:
    server, developer = _make_admin_server(tmp_path)
    try:
        retained = _create_approved_user(server, "Cleanup Retained")
        old = (datetime.now() - timedelta(days=1000)).isoformat()
        expired = (datetime.now() - timedelta(days=1)).isoformat()
        server._db._conn.execute(
            """
            INSERT INTO saved_tables (
                username, save_name, game_type, game_json, members_json, saved_at
            ) VALUES (?, 'Never Automatic', 'pig', '{}', '[]', ?)
            """,
            (retained.username, old),
        )
        server._db.save_password_reset_token(
            retained.uuid,
            "expired-token",
            expired,
        )
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        partial = backup_dir / ".PlayAural-interrupted.sqlite3.partial"
        partial.write_bytes(b"partial")
        _mark_backup_fragment_abandoned(partial)

        await _select(server, developer, "main_menu", "administration")
        await _select(server, developer, "admin_menu", "database_management")
        await _select(
            server,
            developer,
            ADMIN_DATABASE_MENU,
            "cleanup_storage",
        )
        assert (
            _current_menu(server, developer.username)
            == ADMIN_DATABASE_STORAGE_CLEANUP_CONFIRM_MENU
        )
        confirmation = next(
            item
            for item in developer.get_current_menu_items(
                ADMIN_DATABASE_STORAGE_CLEANUP_CONFIRM_MENU
            )
            if item.id == "storage_cleanup_confirm_summary"
        )
        assert confirmation.read_only is True

        await _select(
            server,
            developer,
            ADMIN_DATABASE_STORAGE_CLEANUP_CONFIRM_MENU,
            "confirm",
        )

        assert _current_menu(server, developer.username) == ADMIN_DATABASE_MENU
        assert developer.get_last_spoken().startswith("Storage cleanup completed")
        assert server._db._conn.execute(
            "SELECT COUNT(*) FROM password_reset_tokens"
        ).fetchone()[0] == 0
        assert server._db._conn.execute(
            "SELECT save_name FROM saved_tables"
        ).fetchone()[0] == "Never Automatic"
        assert not partial.exists()
        safety_backups = list(
            backup_dir.glob("*-pre-cleanup-*.sqlite3")
        )
        assert len(safety_backups) == 1
        spoken = developer.get_spoken_messages()
        assert any("performing server storage cleanup" in text for text in spoken)
        assert any("cleanup and database validation are complete" in text for text in spoken)
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_database_storage_cleanup_skips_maintenance_when_nothing_is_eligible(
    tmp_path,
) -> None:
    server, developer = _make_admin_server(tmp_path)
    try:
        await _select(server, developer, "main_menu", "administration")
        await _select(server, developer, "admin_menu", "database_management")
        await _select(
            server,
            developer,
            ADMIN_DATABASE_MENU,
            "cleanup_storage",
        )
        await _select(
            server,
            developer,
            ADMIN_DATABASE_STORAGE_CLEANUP_CONFIRM_MENU,
            "confirm",
        )

        assert _current_menu(server, developer.username) == ADMIN_DATABASE_MENU
        assert developer.get_last_spoken().startswith(
            "Storage cleanup is not needed"
        )
        assert not (tmp_path / "backups").exists()
        assert server.maintenance_manager.is_active is False
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_database_management_is_hidden_and_forged_access_is_rejected(
    tmp_path,
) -> None:
    server, developer = _make_admin_server(tmp_path)
    try:
        admin_record = _create_approved_user(server, "Moderator", 2)
        admin = MockUser("Moderator", uuid=admin_record.uuid)
        admin.trust_level = 2
        server._users[admin.username] = admin
        server.admin_manager._show_admin_menu(admin)

        assert "database_management" not in _menu_item_ids(admin, "admin_menu")
        await server.admin_manager._handle_admin_menu_selection(
            admin,
            "database_management",
        )
        assert _current_menu(server, admin.username) == "admin_menu"
        assert admin.get_last_spoken() == (
            "This action is restricted to Developers only."
        )
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_database_compaction_failure_returns_to_maintenance_menu(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server, developer = _make_admin_server(tmp_path)
    try:
        def fail_compaction(self):
            raise RuntimeError("simulated compaction failure")

        monkeypatch.setattr(
            "server.core.maintenance.Database.compact_database",
            fail_compaction,
        )
        await _select(server, developer, "main_menu", "administration")
        await _select(
            server,
            developer,
            "admin_menu",
            "database_management",
        )
        await _select(
            server,
            developer,
            ADMIN_DATABASE_MENU,
            "compact_database",
        )
        await _select(
            server,
            developer,
            ADMIN_DATABASE_COMPACT_CONFIRM_MENU,
            "confirm",
        )

        assert _current_menu(server, developer.username) == ADMIN_DATABASE_MENU
        assert developer.get_last_spoken().startswith(
            "Database compaction failed"
        )
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_database_backup_uses_confirmation_and_publishes_verified_snapshot(
    tmp_path,
) -> None:
    server, developer = _make_admin_server(tmp_path)
    try:
        retained = _create_approved_user(server, "Backup Retained")
        await _select(server, developer, "main_menu", "administration")
        await _select(
            server,
            developer,
            "admin_menu",
            "database_management",
        )
        assert "backup_database" in _menu_item_ids(developer, ADMIN_DATABASE_MENU)

        await _select(
            server,
            developer,
            ADMIN_DATABASE_MENU,
            "backup_database",
        )
        assert (
            _current_menu(server, developer.username)
            == ADMIN_DATABASE_BACKUP_CONFIRM_MENU
        )
        summary = next(
            item
            for item in developer.get_current_menu_items(
                ADMIN_DATABASE_BACKUP_CONFIRM_MENU
            )
            if item.id == "database_backup_summary"
        )
        assert summary.read_only is True

        await _select(
            server,
            developer,
            ADMIN_DATABASE_BACKUP_CONFIRM_MENU,
            "confirm",
        )

        assert _current_menu(server, developer.username) == ADMIN_DATABASE_MENU
        assert developer.get_last_spoken().startswith("Database backup completed")
        backups = list((tmp_path / "backups").glob("*-manual-*.sqlite3"))
        assert len(backups) == 1
        backup_db = server._db.__class__(backups[0])
        backup_db.connect()
        try:
            assert backup_db.get_user("Backup Retained").uuid == retained.uuid
        finally:
            backup_db.close()
        assert not list((tmp_path / "backups").glob("*.partial"))
        spoken = developer.get_spoken_messages()
        assert any("backing up the server database" in text for text in spoken)
        assert any("backup is complete" in text for text in spoken)
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_global_admin_shortcut_is_server_permission_checked(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        user_record = _create_approved_user(server, "Player")
        player = MockUser("Player", uuid=user_record.uuid)
        player.trust_level = 1
        server._users[player.username] = player
        server._show_main_menu(player)

        await server._handle_open_admin_menu(SimpleNamespace(username=player.username))
        assert _current_menu(server, player.username) == "main_menu"

        await server._handle_open_admin_menu(SimpleNamespace(username=admin.username))
        assert _current_menu(server, admin.username) == "admin_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_editbox_input_is_permission_checked(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        user_record = _create_approved_user(server, "Player")
        player = MockUser("Player", uuid=user_record.uuid)
        player.trust_level = 1
        server._users[player.username] = player
        server._user_states[player.username] = {
            "menu": "admin_target_search_input",
            "target_mode": "ban",
        }

        await server._handle_editbox(
            SimpleNamespace(username=player.username),
            {
                "type": "editbox",
                "input_id": "admin_target_search_input",
                "text": "Admin",
            },
        )

        assert _current_menu(server, player.username) == "main_menu"
        assert player.get_last_spoken() == (
            "You are no longer an admin and cannot perform this action."
        )
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_manual_moderation_review_exposes_identity_time_and_context(
    tmp_path,
) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        reporter = _create_approved_user(server, "Reporter")
        target = _create_approved_user(server, "Target")
        other = _create_approved_user(server, "Other")
        before = server._db.add_global_chat_message(
            other.uuid, other.username, "en", "before message"
        )
        target_message = server._db.add_global_chat_message(
            target.uuid, target.username, "en", "reported message"
        )
        submission = server._db.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=target.uuid,
            reported_username=target.username,
            reason_code="harassment",
            channel_code="en",
        )
        after = server._db.add_global_chat_message(
            other.uuid, other.username, "en", "after message"
        )

        await _select(server, admin, "main_menu", "administration")
        assert "moderation" in _menu_item_ids(admin, "admin_menu")
        await _select(server, admin, "admin_menu", "moderation")
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_MENU
        await _select(server, admin, ADMIN_MODERATION_MENU, "reports_open")
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_REPORTS_MENU

        report_item = f"moderation_report_{submission.report_id}"
        row = _menu_item_text(admin, ADMIN_MODERATION_REPORTS_MENU, report_item)
        assert target.uuid in row
        assert reporter.username in row
        assert "UTC" in row
        report = server._db.get_moderation_report(submission.report_id)
        assert report.reported_at_utc not in row

        await _select(
            server, admin, ADMIN_MODERATION_REPORTS_MENU, report_item
        )
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_REPORT_DETAIL_MENU
        detail_text = " ".join(
            item.text
            for item in admin.get_current_menu_items(
                ADMIN_MODERATION_REPORT_DETAIL_MENU
            )
        )
        assert target.uuid in detail_text
        assert reporter.uuid in detail_text
        assert "UTC" in detail_text

        await _select(
            server,
            admin,
            ADMIN_MODERATION_REPORT_DETAIL_MENU,
            "view_context",
        )
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_CONTEXT_MENU
        context_ids = [
            item_id
            for item_id in _menu_item_ids(admin, ADMIN_MODERATION_CONTEXT_MENU)
            if item_id.startswith("context_message_")
        ]
        assert context_ids == [
            f"context_message_{before.id}",
            f"context_message_{target_message.id}",
            f"context_message_{after.id}",
        ]
        target_context = _menu_item_text(
            admin,
            ADMIN_MODERATION_CONTEXT_MENU,
            f"context_message_{target_message.id}",
        )
        assert "Anchored reported user message" in target_context
        assert target.uuid in target_context

        await _select(server, admin, ADMIN_MODERATION_CONTEXT_MENU, "back")
        await _select(
            server,
            admin,
            ADMIN_MODERATION_REPORT_DETAIL_MENU,
            "set_status_dismissed",
        )
        report = server._db.get_moderation_report(submission.report_id)
        assert report.status == "dismissed"
        assert report.reviewed_by_uuid == admin.uuid
        assert report.reviewed_at_utc is not None
        assert "No automatic penalty was applied" in admin.get_last_spoken()
        assert server._db.get_active_mute(target.username) is None

        await _select(
            server,
            admin,
            ADMIN_MODERATION_REPORT_DETAIL_MENU,
            "back",
        )
        await _select(server, admin, ADMIN_MODERATION_REPORTS_MENU, "back")
        await _select(server, admin, ADMIN_MODERATION_MENU, "reports_closed")
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_REPORTS_MENU
        assert report_item in _menu_item_ids(admin, ADMIN_MODERATION_REPORTS_MENU)
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_automatic_table_report_is_clear_and_has_no_global_context_action(
    tmp_path,
) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        target = _create_approved_user(server, "Target")
        submission = server._db.submit_automated_spam_report(
            reported_uuid=target.uuid,
            reported_username=target.username,
            evidence=AutomatedSpamEvidence(
                scope="table",
                detection_kind="repeated_message",
                incident_count=6,
                rejected_attempt_count=18,
                accepted_message_count=8,
                observation_window_seconds=600,
                sample_message="repeated table sample",
            ),
        )

        server.admin_manager._show_moderation_reports_menu(admin, "open")
        row = _menu_item_text(
            admin,
            ADMIN_MODERATION_REPORTS_MENU,
            f"moderation_report_{submission.report_id}",
        )
        assert "System" in row

        server.admin_manager._show_moderation_report_detail_menu(
            admin, submission.report_id
        )
        ids = _menu_item_ids(admin, ADMIN_MODERATION_REPORT_DETAIL_MENU)
        detail_text = " ".join(
            item.text
            for item in admin.get_current_menu_items(
                ADMIN_MODERATION_REPORT_DETAIL_MENU
            )
        )
        assert "automatically generated by System" in detail_text
        assert "manual review only" in detail_text
        assert "repeated table sample" in detail_text
        assert "view_context" not in ids
        assert "report_anchor" not in ids
        assert "view_target_history" not in ids
        assert next(
            item
            for item in admin.get_current_menu_items(
                ADMIN_MODERATION_REPORT_DETAIL_MENU
            )
            if item.id == "automatic_evidence"
        ).read_only is True

        await _select(
            server,
            admin,
            ADMIN_MODERATION_REPORT_DETAIL_MENU,
            "view_target_history",
        )
        assert (
            _current_menu(server, admin.username)
            == ADMIN_MODERATION_REPORT_DETAIL_MENU
        )
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_developer_can_persistently_toggle_global_chat_from_moderation(
    tmp_path,
) -> None:
    server, admin = _make_admin_server(tmp_path)
    database_path = server._db.db_path
    try:
        observer_record = _create_approved_user(server, "Observer")
        observer = MockUser("Observer", locale="vi", uuid=observer_record.uuid)
        observer.trust_level = 2
        server._users[observer.username] = observer
        server.admin_manager._show_moderation_menu(observer)
        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "moderation")

        toggle = next(
            item
            for item in admin.get_current_menu_items(ADMIN_MODERATION_MENU)
            if item.id == "toggle_global_chat"
        )
        assert toggle.read_only is False
        assert "On" in toggle.text

        await _select(
            server,
            admin,
            ADMIN_MODERATION_MENU,
            "toggle_global_chat",
        )

        assert server.global_chat_sending_enabled is False
        assert server._db.get_boolean_server_setting(
            "global_chat_enabled",
            default=True,
        ) is False
        assert "Off" in _menu_item_text(
            admin,
            ADMIN_MODERATION_MENU,
            "toggle_global_chat",
        )
        assert admin.get_last_spoken() == (
            "Global chat has been temporarily disabled by the developer."
        )
        assert observer.get_last_spoken() == (
            "Nhà phát triển đã tạm thời tắt trò chuyện chung."
        )
        assert "Tắt" in _menu_item_text(
            observer,
            ADMIN_MODERATION_MENU,
            "toggle_global_chat",
        )
        for recipient in (admin, observer):
            notification = next(
                message
                for message in reversed(recipient.messages)
                if message.type == "play_sound"
            )
            assert notification.data["family"] == "notify"
            assert notification.data["buffer"] == "system"

        await _select(
            server,
            admin,
            ADMIN_MODERATION_MENU,
            "toggle_global_chat",
        )
        assert server.global_chat_sending_enabled is True
        assert admin.get_last_spoken().startswith("Global chat has been enabled")
        assert observer.get_last_spoken().startswith(
            "Nhà phát triển đã bật trò chuyện chung"
        )

        await _select(
            server,
            admin,
            ADMIN_MODERATION_MENU,
            "toggle_global_chat",
        )
        assert server.global_chat_sending_enabled is False
    finally:
        server._db.close()

    restarted = Server(db_path=database_path)
    try:
        restarted._db.connect()
        restarted._load_persistent_server_settings()
        assert restarted.global_chat_sending_enabled is False
    finally:
        restarted._db.close()


@pytest.mark.asyncio
async def test_admin_global_chat_status_is_read_only(tmp_path) -> None:
    server, developer = _make_admin_server(tmp_path)
    try:
        admin_record = _create_approved_user(server, "Moderator", 2)
        admin = MockUser("Moderator", uuid=admin_record.uuid)
        admin.trust_level = 2
        server._users[admin.username] = admin
        server.admin_manager._show_moderation_menu(admin)
        status = next(
            item
            for item in admin.get_current_menu_items(ADMIN_MODERATION_MENU)
            if item.id == "toggle_global_chat"
        )
        assert status.read_only is True

        await _select(
            server,
            admin,
            ADMIN_MODERATION_MENU,
            "toggle_global_chat",
        )

        assert server.global_chat_sending_enabled is True
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_MENU
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_global_chat_toggle_keeps_live_state_when_persistence_fails(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "moderation")

        def fail_write(_setting_key: str, _value: bool) -> None:
            raise RuntimeError("simulated write failure")

        monkeypatch.setattr(
            server._db,
            "set_boolean_server_setting",
            fail_write,
        )
        await _select(
            server,
            admin,
            ADMIN_MODERATION_MENU,
            "toggle_global_chat",
        )

        assert server.global_chat_sending_enabled is True
        assert "no change was made" in admin.get_last_spoken()
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_MENU
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_history_lookup_separates_reused_username_account_ids(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        original = _create_approved_user(server, "Repeated Name")
        old_message = server._db.add_global_chat_message(
            original.uuid, original.username, "en", "old account message"
        )
        assert server._db.delete_user(original.username)
        replacement = _create_approved_user(server, "Repeated Name")
        server._db.add_global_chat_message(
            replacement.uuid,
            replacement.username,
            "en",
            "new account message",
        )

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "moderation")
        await _select(server, admin, ADMIN_MODERATION_MENU, "find_history")
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_HISTORY_INPUT

        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": ADMIN_MODERATION_HISTORY_INPUT,
                "text": "repeated name",
            },
        )
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_SENDER_RESULTS_MENU
        result_ids = _menu_item_ids(admin, ADMIN_MODERATION_SENDER_RESULTS_MENU)
        assert f"history_sender_{original.uuid}" in result_ids
        assert f"history_sender_{replacement.uuid}" in result_ids

        await _select(
            server,
            admin,
            ADMIN_MODERATION_SENDER_RESULTS_MENU,
            f"history_sender_{original.uuid}",
        )
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_HISTORY_MENU
        assert f"history_message_{old_message.id}" in _menu_item_ids(
            admin, ADMIN_MODERATION_HISTORY_MENU
        )
        heading = _menu_item_text(
            admin, ADMIN_MODERATION_HISTORY_MENU, "history_heading"
        )
        assert original.uuid in heading
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_global_message_browser_filters_pages_and_restores_parent(
    tmp_path,
) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        sender = _create_approved_user(server, "Sender")
        english_messages = [
            server._db.add_global_chat_message(
                sender.uuid,
                sender.username,
                "en",
                f"English message {index:02d}",
            )
            for index in range(51)
        ]
        vietnamese_message = server._db.add_global_chat_message(
            sender.uuid,
            sender.username,
            "vi",
            "Vietnamese archived message",
        )
        server._db._conn.execute(
            "UPDATE global_chat_messages SET sent_at_utc = ? WHERE id = ?",
            ("2020-01-01T00:00:00.000000+00:00", vietnamese_message.id),
        )

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "moderation")
        await _select(server, admin, ADMIN_MODERATION_MENU, "browse_messages")
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_MESSAGES_MENU
        message_ids = _menu_item_ids(admin, ADMIN_MODERATION_MESSAGES_MENU)
        assert "page_next" in message_ids
        assert f"moderation_message_{english_messages[-1].id}" in message_ids
        assert f"moderation_message_{vietnamese_message.id}" not in message_ids

        await _select(
            server,
            admin,
            ADMIN_MODERATION_MESSAGES_MENU,
            "message_filter_sort",
        )
        assert server._user_states[admin.username]["message_sort"] == "oldest"
        assert f"moderation_message_{vietnamese_message.id}" in _menu_item_ids(
            admin,
            ADMIN_MODERATION_MESSAGES_MENU,
        )
        old_row = _menu_item_text(
            admin,
            ADMIN_MODERATION_MESSAGES_MENU,
            f"moderation_message_{vietnamese_message.id}",
        )
        assert old_row.startswith("Sender: Vietnamese archived message")
        assert old_row.index("Vietnamese archived message") < old_row.index(
            f"Message #{vietnamese_message.id}"
        )

        await _select(
            server,
            admin,
            ADMIN_MODERATION_MESSAGES_MENU,
            "message_filter_language",
        )
        assert _current_menu(
            server, admin.username
        ) == ADMIN_MODERATION_MESSAGE_LANGUAGE_MENU
        await _select(
            server,
            admin,
            ADMIN_MODERATION_MESSAGE_LANGUAGE_MENU,
            "message_language_vi",
        )
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_MESSAGES_MENU
        assert server._user_states[admin.username]["message_channel"] == "vi"
        filtered_ids = _menu_item_ids(admin, ADMIN_MODERATION_MESSAGES_MENU)
        assert f"moderation_message_{vietnamese_message.id}" in filtered_ids
        assert not any(
            f"moderation_message_{message.id}" in filtered_ids
            for message in english_messages
        )

        await _select(
            server,
            admin,
            ADMIN_MODERATION_MESSAGES_MENU,
            "message_filter_period",
        )
        assert _current_menu(
            server, admin.username
        ) == ADMIN_MODERATION_MESSAGE_PERIOD_MENU
        await _select(
            server,
            admin,
            ADMIN_MODERATION_MESSAGE_PERIOD_MENU,
            "message_period_today",
        )
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_MESSAGES_MENU
        assert server._user_states[admin.username]["message_period"] == "today"
        assert "message_list_empty" in _menu_item_ids(
            admin,
            ADMIN_MODERATION_MESSAGES_MENU,
        )

        await _select(
            server,
            admin,
            ADMIN_MODERATION_MESSAGES_MENU,
            "message_filter_reset",
        )
        state = server._user_states[admin.username]
        assert state["message_channel"] is None
        assert state["message_period"] == "all"
        assert state["message_sort"] == "newest"
        assert state["moderation_page"] == 1
        await _select(server, admin, ADMIN_MODERATION_MESSAGES_MENU, "page_next")
        assert server._user_states[admin.username]["moderation_page"] == 2
        assert admin.menus[ADMIN_MODERATION_MESSAGES_MENU]["position"] == 6

        await _select(server, admin, ADMIN_MODERATION_MESSAGES_MENU, "back")
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_MENU
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_developer_cleanup_is_confirmed_and_preserves_open_reports(
    tmp_path,
) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        reporter = _create_approved_user(server, "Reporter")
        target = _create_approved_user(server, "Target")
        message = server._db.add_global_chat_message(
            target.uuid, target.username, "en", "evidence"
        )
        submission = server._db.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=target.uuid,
            reported_username=target.username,
            reason_code="spam",
            channel_code="en",
        )
        report = server._db.get_moderation_report(submission.report_id)
        assert report.context_anchor_message_id == message.id

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "moderation")
        await _select(server, admin, ADMIN_MODERATION_MENU, "clear_history")
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_CLEAR_CONFIRM_MENU
        summary = next(
            item
            for item in admin.get_current_menu_items(
                ADMIN_MODERATION_CLEAR_CONFIRM_MENU
            )
            if item.id == "clear_summary"
        )
        assert summary.read_only is True
        await _select(
            server,
            admin,
            ADMIN_MODERATION_CLEAR_CONFIRM_MENU,
            "clear_summary",
        )
        assert _current_menu(server, admin.username) == ADMIN_MODERATION_CLEAR_CONFIRM_MENU
        assert server._db.count_global_chat_messages() == 1
        await _select(
            server, admin, ADMIN_MODERATION_CLEAR_CONFIRM_MENU, "confirm"
        )

        assert server._db.count_global_chat_messages() == 0
        retained = server._db.get_moderation_report(submission.report_id)
        assert retained is not None
        assert retained.status == "open"
        assert retained.context_anchor_message_id is None

        ordinary_admin = _create_approved_user(server, "Ordinary Admin", 2)
        ordinary_user = MockUser("Ordinary Admin", uuid=ordinary_admin.uuid)
        ordinary_user.trust_level = 2
        server._users[ordinary_user.username] = ordinary_user
        server.admin_manager._show_moderation_menu(ordinary_user)
        ids = _menu_item_ids(ordinary_user, ADMIN_MODERATION_MENU)
        assert "clear_history" not in ids
        assert "clear_closed_reports" not in ids
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_account_approval_menu_pages_pending_accounts(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        for index in range(101):
            server._db.create_user(f"Pending{index:03d}", "hash")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "account_approval")

        ids = _menu_item_ids(admin, "account_approval_menu")
        assert len([item_id for item_id in ids if item_id.startswith("pending_")]) == 100
        assert "pending_Pending100" not in ids
        assert "refresh" in ids
        assert "page_next" in ids

        await _select(server, admin, "account_approval_menu", "page_next")
        assert server._user_states[admin.username]["account_approval_page"] == 2
        last_page_ids = _menu_item_ids(admin, "account_approval_menu")
        assert "pending_Pending100" in last_page_ids
        assert "page_previous" in last_page_ids
        assert "page_next" not in last_page_ids
        assert admin.menus["account_approval_menu"]["position"] == 1

        await _select(server, admin, "account_approval_menu", "pending_Pending100")
        assert _current_menu(server, admin.username) == "pending_user_actions_menu"

        await _select(server, admin, "pending_user_actions_menu", "back")
        assert _current_menu(server, admin.username) == "account_approval_menu"
        assert server._user_states[admin.username]["account_approval_page"] == 2
        assert admin.menus["account_approval_menu"]["selection_id"] == "pending_Pending100"
    finally:
        server._db.close()


def test_admin_empty_paginated_menus_do_not_show_manual_refresh(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        server.admin_manager._show_account_approval_menu(admin)
        approval_ids = _menu_item_ids(admin, "account_approval_menu")
        assert "refresh" not in approval_ids

        server.admin_manager._show_ban_menu(admin)
        ban_ids = _menu_item_ids(admin, "ban_menu")
        assert "refresh" not in ban_ids
    finally:
        server._db.close()


def test_account_approval_list_auto_refreshes_when_pending_queue_changes(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        server.admin_manager._show_account_approval_menu(admin)
        assert "pending_NewPlayer" not in _menu_item_ids(admin, "account_approval_menu")

        server._db.create_user("NewPlayer", "hash")
        server.admin_manager.refresh_account_approval_menus()

        ids = _menu_item_ids(admin, "account_approval_menu")
        assert "pending_NewPlayer" in ids
        assert "refresh" in ids
        assert admin.menus["account_approval_menu"]["position"] is None
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_searchable_ban_menu_limits_and_filters_results(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        for index in range(100):
            _create_approved_user(server, f"User{index:03d}")
        _create_approved_user(server, "ZzzNeedleTarget")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "ban_user")
        assert _current_menu(server, admin.username) == "ban_menu"

        ids = _menu_item_ids(admin, "ban_menu")
        assert ids[0] == "search"
        assert len([item_id for item_id in ids if item_id.startswith("ban_")]) == 100
        assert "ban_ZzzNeedleTarget" not in ids
        assert "refresh" in ids
        assert "page_next" in ids
        assert "page_last" in ids

        await _select(server, admin, "ban_menu", "page_next")
        assert server._user_states[admin.username]["target_page"] == 2
        last_page_ids = _menu_item_ids(admin, "ban_menu")
        assert "ban_ZzzNeedleTarget" in last_page_ids
        assert "page_previous" in last_page_ids
        assert "page_next" not in last_page_ids
        assert admin.menus["ban_menu"]["position"] == 3

        await _select(server, admin, "ban_menu", "ban_ZzzNeedleTarget")
        assert _current_menu(server, admin.username) == "ban_duration_menu"

        await _select(server, admin, "ban_duration_menu", "back")
        assert _current_menu(server, admin.username) == "ban_menu"
        assert admin.menus["ban_menu"]["selection_id"] == "ban_ZzzNeedleTarget"
        assert server._user_states[admin.username]["target_page"] == 2

        await _select(server, admin, "ban_menu", "search")
        assert _current_menu(server, admin.username) == "admin_target_search_input"

        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "admin_target_search_input",
                "text": "Needle",
            },
        )

        assert _current_menu(server, admin.username) == "ban_menu"
        filtered_ids = _menu_item_ids(admin, "ban_menu")
        assert "ban_ZzzNeedleTarget" in filtered_ids
        assert server._user_states[admin.username]["search_query"] == "Needle"
        assert server._user_states[admin.username]["target_page"] == 1

        await _select(server, admin, "ban_menu", "ban_ZzzNeedleTarget")
        assert _current_menu(server, admin.username) == "ban_duration_menu"

        await _select(server, admin, "ban_duration_menu", "back")
        assert _current_menu(server, admin.username) == "ban_menu"
        assert admin.menus["ban_menu"]["selection_id"] == "ban_ZzzNeedleTarget"
        assert server._user_states[admin.username]["search_query"] == "Needle"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_searchable_unban_menu_uses_active_ban_search(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        for index in range(100):
            username = f"Banned{index:03d}"
            _create_approved_user(server, username)
            server._db.ban_user(username, admin.username, "reason-spam", None)
        _create_approved_user(server, "SpecialBan")
        server._db.ban_user("SpecialBan", admin.username, "reason-spam", None)

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "unban_user")
        ids = _menu_item_ids(admin, "unban_menu")
        assert ids[0] == "search"
        assert len([item_id for item_id in ids if item_id.startswith("unban_")]) == 100
        assert "unban_SpecialBan" not in ids
        assert "refresh" in ids
        assert "page_next" in ids

        await _select(server, admin, "unban_menu", "page_next")
        assert server._user_states[admin.username]["target_page"] == 2
        assert "unban_SpecialBan" in _menu_item_ids(admin, "unban_menu")

        await _select(server, admin, "unban_menu", "search")
        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "admin_target_search_input",
                "text": "Special",
            },
        )

        filtered_ids = _menu_item_ids(admin, "unban_menu")
        assert "unban_SpecialBan" in filtered_ids
        assert not any(item_id == "unban_Banned00" for item_id in filtered_ids)
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_unban_menu_shows_penalty_details(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        _create_approved_user(server, "TimedBan")
        expires = (datetime.now() + timedelta(hours=2, minutes=5)).isoformat()
        server._db.ban_user("TimedBan", admin.username, "reason-spam", expires)

        _create_approved_user(server, "LegacyBan")
        server._db.ban_user("LegacyBan", "", "", None)

        _create_approved_user(server, "DuplicateBan")
        server._db.ban_user("DuplicateBan", "OldAdmin", "reason-spam", expires)
        server._db.ban_user("DuplicateBan", admin.username, "reason-cheating", None)

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "unban_user")

        timed_text = _menu_item_text(admin, "unban_menu", "unban_TimedBan")
        assert "TimedBan" in timed_text
        assert "Ban expiration:" in timed_text
        assert "remaining" in timed_text
        assert "Spam" in timed_text
        assert "Admin" in timed_text

        legacy_text = _menu_item_text(admin, "unban_menu", "unban_LegacyBan")
        assert "LegacyBan" in legacy_text
        assert "permanent" in legacy_text
        assert "unspecified reason" in legacy_text
        assert "unknown administrator" in legacy_text

        duplicate_ids = [
            item_id
            for item_id in _menu_item_ids(admin, "unban_menu")
            if item_id == "unban_DuplicateBan"
        ]
        assert duplicate_ids == ["unban_DuplicateBan"]
        duplicate_text = _menu_item_text(admin, "unban_menu", "unban_DuplicateBan")
        assert "Cheating" in duplicate_text
        assert "Spam" not in duplicate_text
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_unmute_menu_shows_penalty_details(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        _create_approved_user(server, "MutedTarget")
        server._db.mute_user(
            "MutedTarget",
            admin.username,
            "CUSTOM_repeated table chat spam",
            None,
        )

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "unmute_user")

        text = _menu_item_text(admin, "unmute_menu", "unmute_MutedTarget")
        assert "MutedTarget" in text
        assert "Mute expiration:" in text
        assert "permanent" in text
        assert "repeated table chat spam" in text
        assert "Admin" in text
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_submenu_back_restores_admin_focus_and_outer_stack(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        await _select(server, admin, "main_menu", "administration")
        assert _current_menu(server, admin.username) == "admin_menu"

        await _select(server, admin, "admin_menu", "kick_user")
        assert _current_menu(server, admin.username) == "kick_menu"

        await _select(server, admin, "kick_menu", "back")
        assert _current_menu(server, admin.username) == "admin_menu"
        assert admin.menus["admin_menu"]["selection_id"] == "kick_user"

        await _select(server, admin, "admin_menu", "back")
        assert _current_menu(server, admin.username) == "main_menu"
        assert admin.menus["main_menu"]["selection_id"] == "administration"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_nested_dynamic_back_restores_target_and_root_focus(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        _create_approved_user(server, "Target")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "ban_user")
        assert _current_menu(server, admin.username) == "ban_menu"

        await _select(server, admin, "ban_menu", "ban_Target")
        assert _current_menu(server, admin.username) == "ban_duration_menu"

        await _select(server, admin, "ban_duration_menu", "back")
        assert _current_menu(server, admin.username) == "ban_menu"
        assert admin.menus["ban_menu"]["selection_id"] == "ban_Target"

        await _select(server, admin, "ban_menu", "back")
        assert _current_menu(server, admin.username) == "admin_menu"
        assert admin.menus["admin_menu"]["selection_id"] == "ban_user"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_confirmation_cancel_restores_list_target_focus(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        _create_approved_user(server, "Target")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "promote_admin")
        await _select(server, admin, "promote_admin_menu", "promote_Target")
        assert _current_menu(server, admin.username) == "promote_confirm_menu"

        await _select(server, admin, "promote_confirm_menu", "no")
        assert _current_menu(server, admin.username) == "promote_admin_menu"
        assert admin.menus["promote_admin_menu"]["selection_id"] == "promote_Target"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_broadcast_scope_back_restores_confirmation_focus(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        _create_approved_user(server, "Target")

        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "promote_admin")
        await _select(server, admin, "promote_admin_menu", "promote_Target")
        await _select(server, admin, "promote_confirm_menu", "yes")
        assert _current_menu(server, admin.username) == "broadcast_choice_menu"

        await _select(server, admin, "broadcast_choice_menu", "back")
        assert _current_menu(server, admin.username) == "promote_confirm_menu"
        assert admin.menus["promote_confirm_menu"]["selection_id"] == "yes"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_editbox_cancel_restores_admin_focus_and_back_path(tmp_path) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "broadcast_announcement")
        assert _current_menu(server, admin.username) == "admin_broadcast_input"

        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "broadcast_message",
                "text": "",
            },
        )

        assert _current_menu(server, admin.username) == "admin_menu"
        assert admin.menus["admin_menu"]["selection_id"] == "broadcast_announcement"

        await _select(server, admin, "admin_menu", "back")
        assert _current_menu(server, admin.username) == "main_menu"
        assert admin.menus["main_menu"]["selection_id"] == "administration"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_admin_translation_editbox_cancel_restores_editor_and_back_path(
    tmp_path,
) -> None:
    server, admin = _make_admin_server(tmp_path)
    try:
        await _select(server, admin, "main_menu", "administration")
        await _select(server, admin, "admin_menu", "manage_motd")
        await _select(server, admin, "manage_motd_menu", "create_update")
        assert _current_menu(server, admin.username) == "admin_localized_text_menu"

        await _select(
            server,
            admin,
            "admin_localized_text_menu",
            "localized_text_locale_en",
        )
        assert _current_menu(server, admin.username) == "admin_localized_text_input"

        await server._handle_editbox(
            SimpleNamespace(username=admin.username),
            {
                "type": "editbox",
                "input_id": "admin_localized_text_input",
                "cancelled": True,
            },
        )

        assert _current_menu(server, admin.username) == "admin_localized_text_menu"
        assert (
            admin.menus["admin_localized_text_menu"]["selection_id"]
            == "localized_text_locale_en"
        )

        await _select(server, admin, "admin_localized_text_menu", "back")
        assert _current_menu(server, admin.username) == "manage_motd_menu"
        assert admin.menus["manage_motd_menu"]["selection_id"] == "create_update"
    finally:
        server._db.close()
