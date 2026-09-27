import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest

from server.cli import cmd_set_user_role
from server.persistence.database import Database
from server.users.roles import (
    ADMIN_TRUST_LEVEL,
    DEVELOPER_TRUST_LEVEL,
    USER_TRUST_LEVEL,
)

SERVER_DIR = Path(__file__).resolve().parents[1]
CLI_PATH = SERVER_DIR / "cli.py"


def _connected_database(path):
    database = Database(path)
    database.connect()
    return database


def test_user_role_change_is_validated_and_atomic(tmp_path):
    database = _connected_database(tmp_path / "roles.sqlite")
    try:
        database.create_user(
            "Owner",
            "hash",
            trust_level=DEVELOPER_TRUST_LEVEL,
            approved=True,
        )
        database.create_user(
            "Rory101",
            "hash",
            trust_level=USER_TRUST_LEVEL,
            approved=True,
        )

        preview = database.preview_user_trust_level_change(
            "rory101",
            DEVELOPER_TRUST_LEVEL,
        )
        assert preview is not None
        assert preview.username == "Rory101"
        assert preview.previous_trust_level == USER_TRUST_LEVEL
        assert preview.changed is True

        result = database.update_user_trust_level(
            preview.username,
            DEVELOPER_TRUST_LEVEL,
            expected_trust_level=preview.previous_trust_level,
        )
        assert result is not None
        assert result.previous_trust_level == USER_TRUST_LEVEL
        assert result.trust_level == DEVELOPER_TRUST_LEVEL
        assert database.get_user("Rory101").trust_level == DEVELOPER_TRUST_LEVEL
    finally:
        database.close()


def test_privileged_role_requires_an_approved_account(tmp_path):
    database = _connected_database(tmp_path / "roles.sqlite")
    try:
        database.create_user("Pending", "hash", approved=False)

        with pytest.raises(ValueError, match="must be approved"):
            database.preview_user_trust_level_change(
                "Pending",
                ADMIN_TRUST_LEVEL,
            )
        assert database.get_user("Pending").trust_level == USER_TRUST_LEVEL
    finally:
        database.close()


def test_last_approved_developer_cannot_be_demoted(tmp_path):
    database = _connected_database(tmp_path / "roles.sqlite")
    try:
        database.create_user(
            "OnlyDeveloper",
            "hash",
            trust_level=DEVELOPER_TRUST_LEVEL,
            approved=True,
        )

        with pytest.raises(ValueError, match="last approved developer"):
            database.preview_user_trust_level_change(
                "OnlyDeveloper",
                ADMIN_TRUST_LEVEL,
            )
        with pytest.raises(ValueError, match="last approved developer"):
            database.update_user_trust_level(
                "OnlyDeveloper",
                ADMIN_TRUST_LEVEL,
            )
        assert (
            database.get_user("OnlyDeveloper").trust_level
            == DEVELOPER_TRUST_LEVEL
        )
    finally:
        database.close()


def test_developer_can_be_demoted_when_another_approved_developer_remains(tmp_path):
    database = _connected_database(tmp_path / "roles.sqlite")
    try:
        database.create_user(
            "FirstDeveloper",
            "hash",
            trust_level=DEVELOPER_TRUST_LEVEL,
            approved=True,
        )
        database.create_user(
            "SecondDeveloper",
            "hash",
            trust_level=DEVELOPER_TRUST_LEVEL,
            approved=True,
        )

        result = database.update_user_trust_level(
            "FirstDeveloper",
            ADMIN_TRUST_LEVEL,
        )
        assert result is not None
        assert result.changed is True
        assert database.get_user("FirstDeveloper").trust_level == ADMIN_TRUST_LEVEL
        assert (
            database.get_user("SecondDeveloper").trust_level
            == DEVELOPER_TRUST_LEVEL
        )
    finally:
        database.close()


def test_role_change_rejects_stale_preview_and_invalid_level(tmp_path):
    database = _connected_database(tmp_path / "roles.sqlite")
    try:
        database.create_user(
            "Owner",
            "hash",
            trust_level=DEVELOPER_TRUST_LEVEL,
            approved=True,
        )
        database.create_user("Target", "hash", approved=True)
        preview = database.preview_user_trust_level_change(
            "Target",
            DEVELOPER_TRUST_LEVEL,
        )
        assert preview is not None

        database.update_user_trust_level("Target", ADMIN_TRUST_LEVEL)
        with pytest.raises(ValueError, match="changed from trust level"):
            database.update_user_trust_level(
                "Target",
                DEVELOPER_TRUST_LEVEL,
                expected_trust_level=preview.previous_trust_level,
            )
        with pytest.raises(ValueError, match="Unsupported user trust level"):
            database.update_user_trust_level("Target", 4)
        assert database.get_user("Target").trust_level == ADMIN_TRUST_LEVEL
    finally:
        database.close()


def test_offline_role_cli_creates_backup_and_verifies_commit(tmp_path, capsys):
    database_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "backups"
    database = _connected_database(database_path)
    try:
        database.create_user(
            "Owner",
            "hash",
            trust_level=DEVELOPER_TRUST_LEVEL,
            approved=True,
        )
        database.create_user("Rory101", "hash", approved=True)
    finally:
        database.close()

    cmd_set_user_role(
        Namespace(
            username="Rory101",
            role="developer",
            database=str(database_path),
            database_backup_dir=str(backup_dir),
            confirm_server_stopped=True,
        )
    )

    output = capsys.readouterr().out
    assert "Verified safety backup:" in output
    assert "Rory101" in output
    assert len(list(backup_dir.glob("PlayAural-pre-role-change-*.sqlite3"))) == 1
    database = _connected_database(database_path)
    try:
        assert database.get_user("Rory101").trust_level == DEVELOPER_TRUST_LEVEL
    finally:
        database.close()


def test_offline_role_cli_works_through_production_script_entrypoint(tmp_path):
    database_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "backups"
    database = _connected_database(database_path)
    try:
        database.create_user(
            "Owner",
            "hash",
            trust_level=DEVELOPER_TRUST_LEVEL,
            approved=True,
        )
        database.create_user("Target", "hash", approved=True)
    finally:
        database.close()

    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "set-user-role",
            "Target",
            "admin",
            "--database",
            str(database_path),
            "--database-backup-dir",
            str(backup_dir),
            "--confirm-server-stopped",
        ],
        cwd=SERVER_DIR,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    database = _connected_database(database_path)
    try:
        assert database.get_user("Target").trust_level == ADMIN_TRUST_LEVEL
    finally:
        database.close()


def test_offline_role_cli_requires_stop_confirmation_before_opening_database(
    tmp_path,
):
    database_path = tmp_path / "missing.db"
    with pytest.raises(SystemExit) as exc_info:
        cmd_set_user_role(
            Namespace(
                username="Rory101",
                role="developer",
                database=str(database_path),
                database_backup_dir=str(tmp_path / "backups"),
                confirm_server_stopped=False,
            )
        )
    assert exc_info.value.code == 2
    assert not database_path.exists()


def test_offline_role_cli_requires_exact_registered_spelling(tmp_path):
    database_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "backups"
    database = _connected_database(database_path)
    try:
        database.create_user(
            "Owner",
            "hash",
            trust_level=DEVELOPER_TRUST_LEVEL,
            approved=True,
        )
        database.create_user("Rory101", "hash", approved=True)
    finally:
        database.close()

    with pytest.raises(SystemExit) as exc_info:
        cmd_set_user_role(
            Namespace(
                username="rory101",
                role="developer",
                database=str(database_path),
                database_backup_dir=str(backup_dir),
                confirm_server_stopped=True,
            )
        )
    assert exc_info.value.code == 2
    assert not list(backup_dir.glob("PlayAural-pre-role-change-*.sqlite3"))


def test_offline_role_cli_noop_does_not_create_backup(tmp_path, capsys):
    database_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "backups"
    database = _connected_database(database_path)
    try:
        database.create_user(
            "ExistingAdmin",
            "hash",
            trust_level=ADMIN_TRUST_LEVEL,
            approved=True,
        )
    finally:
        database.close()

    cmd_set_user_role(
        Namespace(
            username="ExistingAdmin",
            role="admin",
            database=str(database_path),
            database_backup_dir=str(backup_dir),
            confirm_server_stopped=True,
        )
    )
    assert "No change needed" in capsys.readouterr().out
    assert not list(backup_dir.glob("PlayAural-pre-role-change-*.sqlite3"))


def test_offline_role_cli_does_not_create_a_missing_database(tmp_path):
    database_path = tmp_path / "missing.db"
    with pytest.raises(SystemExit) as exc_info:
        cmd_set_user_role(
            Namespace(
                username="Rory101",
                role="developer",
                database=str(database_path),
                database_backup_dir=str(tmp_path / "backups"),
                confirm_server_stopped=True,
            )
        )
    assert exc_info.value.code == 1
    assert not database_path.exists()


def test_offline_role_cli_rejects_last_developer_without_extra_backup(
    tmp_path,
):
    database_path = tmp_path / "PlayAural.db"
    backup_dir = tmp_path / "backups"
    database = _connected_database(database_path)
    try:
        database.create_user(
            "OnlyDeveloper",
            "hash",
            trust_level=DEVELOPER_TRUST_LEVEL,
            approved=True,
        )
    finally:
        database.close()

    with pytest.raises(SystemExit) as exc_info:
        cmd_set_user_role(
            Namespace(
                username="OnlyDeveloper",
                role="admin",
                database=str(database_path),
                database_backup_dir=str(backup_dir),
                confirm_server_stopped=True,
            )
        )
    assert exc_info.value.code == 2
    assert not list(backup_dir.glob("PlayAural-pre-role-change-*.sqlite3"))
