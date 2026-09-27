import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SERVER_DIR / "sc.sh"
BASH = shutil.which("bash")


def _script_prefix() -> str:
    script = SCRIPT_PATH.read_text(encoding="utf-8")
    prefix, marker, _menu = script.partition("\ncheck_root\n")
    assert marker, "sc.sh must keep its interactive entry point after check_root"
    return prefix


def _run_script_functions(tmp_path: Path, commands: str) -> subprocess.CompletedProcess[str]:
    if BASH is None:
        pytest.skip("bash is required for server management script behavior tests")
    (tmp_path / "sc-functions.sh").write_text(
        _script_prefix(),
        encoding="utf-8",
        newline="\n",
    )
    return subprocess.run(
        [BASH, "-c", "source ./sc-functions.sh\n" + textwrap.dedent(commands)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )


def test_management_script_uses_linux_line_endings():
    assert b"\r\n" not in SCRIPT_PATH.read_bytes()


def test_generated_game_service_bounds_restarts_and_secures_storage(tmp_path):
    _run_script_functions(
        tmp_path,
        """
        set -euo pipefail
        SERVER_DIR=/srv/playaural
        VENV_DIR=$SERVER_DIR/.venv
        VENV_PYTHON=$VENV_DIR/bin/python
        DATABASE_BACKUP_DIR=$SERVER_DIR/backups
        SERVICE_FILE=$PWD/playaural.service
        setup_system_user() { :; }
        ensure_config_dir() { :; }
        systemctl() { :; }
        setup_service
        """,
    )

    service = (tmp_path / "playaural.service").read_text(encoding="utf-8")
    assert "StartLimitIntervalSec=300\n" in service
    assert "StartLimitBurst=3\n" in service
    assert "RestartSec=10\n" in service
    assert "UMask=0077\n" in service
    assert "LimitFSIZE=infinity\n" in service
    assert (
        "ExecStart=/srv/playaural/.venv/bin/python /srv/playaural/main.py "
        "--host 127.0.0.1 --port 8000 "
        "--database-backup-dir /srv/playaural/backups\n"
    ) in service


def test_storage_preparation_repairs_database_artifact_permissions(tmp_path):
    result = _run_script_functions(
        tmp_path,
        """
        set -euo pipefail
        SERVER_DIR=$PWD/server
        DATABASE_PATH=$SERVER_DIR/PlayAural.db
        DATABASE_BACKUP_DIR=$SERVER_DIR/backups
        mkdir -p "$DATABASE_BACKUP_DIR"
        touch \
            "$DATABASE_PATH" \
            "$DATABASE_PATH-wal" \
            "$DATABASE_PATH-shm" \
            "$DATABASE_PATH-journal" \
            "$SERVER_DIR/errors.log" \
            "$DATABASE_BACKUP_DIR/existing.sqlite3"
        EVENTS=()
        install() { EVENTS+=("install:$*"); }
        chown() { EVENTS+=("chown:$*"); }
        chmod() { EVENTS+=("chmod:$*"); }
        find() { EVENTS+=("find:$*"); }

        prepare_database_storage
        printf '%s\n' "${EVENTS[@]}"
        """,
    )

    events = result.stdout.splitlines()
    assert any(
        event.startswith("install:-d -o playaural -g playaural -m 0700 ")
        for event in events
    )
    for name in (
        "PlayAural.db",
        "PlayAural.db-wal",
        "PlayAural.db-shm",
        "PlayAural.db-journal",
        "errors.log",
    ):
        assert any(
            event.startswith("chown:playaural:playaural ")
            and event.endswith(name)
            for event in events
        )
        assert any(
            event.startswith("chmod:600 ") and event.endswith(name)
            for event in events
        )
    assert any(
        event.startswith("find:")
        and event.endswith("/backups -type f -exec chmod 600 {} +")
        for event in events
    )


def test_start_and_restart_stop_service_before_environment_changes(tmp_path):
    result = _run_script_functions(
        tmp_path,
        """
        set -euo pipefail
        SERVICE_FILE=$PWD/playaural.service
        touch "$SERVICE_FILE"
        EVENTS=()
        IS_ACTIVE=1
        systemctl() {
            case "$1" in
                is-active) return "$IS_ACTIVE" ;;
                *) EVENTS+=("systemctl:$1"); return 0 ;;
            esac
        }
        install_environment() { EVENTS+=(install); }
        setup_service() { EVENTS+=(setup); }
        verify_database_storage() { EVENTS+=(verify); }
        pause_screen() { :; }
        sleep() { :; }
        check_status() { :; }

        start_server
        printf 'start=%s\n' "${EVENTS[*]}"
        EVENTS=()
        restart_server
        printf 'restart=%s\n' "${EVENTS[*]}"
        """,
    )

    expected = (
        "systemctl:stop install setup verify "
        "systemctl:reset-failed systemctl:start"
    )
    assert f"start={expected}\n" in result.stdout
    assert f"restart={expected}\n" in result.stdout


def test_start_failure_leaves_service_stopped(tmp_path):
    result = _run_script_functions(
        tmp_path,
        """
        set -euo pipefail
        SERVICE_FILE=$PWD/playaural.service
        touch "$SERVICE_FILE"
        EVENTS=()
        systemctl() {
            case "$1" in
                is-active) return 1 ;;
                *) EVENTS+=("systemctl:$1"); return 0 ;;
            esac
        }
        install_environment() { EVENTS+=(install); }
        setup_service() { EVENTS+=(setup); }
        verify_database_storage() { EVENTS+=(verify); return 1; }
        pause_screen() { :; }

        if start_server; then
            exit 64
        fi
        printf '%s\n' "${EVENTS[*]}"
        """,
    )

    assert result.stdout.rstrip().endswith("systemctl:stop install setup verify")
    assert "systemctl:start" not in result.stdout


def test_management_script_loads_runtime_dependencies_from_pyproject(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            dependencies = [
                "example-one>=1",
                "example-two[fast]==2.0",
            ]
            """
        ),
        encoding="utf-8",
    )
    result = _run_script_functions(
        tmp_path,
        """
        set -euo pipefail
        SERVER_DIR=$PWD/project
        VENV_PYTHON=python
        load_server_dependencies
        """,
    )

    assert result.stdout.splitlines() == [
        "example-one>=1",
        "example-two[fast]==2.0",
    ]


def test_python_detection_rejects_unsupported_fallback(tmp_path):
    result = _run_script_functions(
        tmp_path,
        """
        set -euo pipefail
        command_exists() { return 0; }
        python3.12() { return 1; }
        python3.11() { return 0; }
        python3() { return 0; }
        detect_python_bin
        """,
    )

    assert result.stdout == "python3.11\n"


def test_role_change_stops_service_and_restores_previous_running_state(tmp_path):
    result = _run_script_functions(
        tmp_path,
        """
        set -euo pipefail
        SERVICE_FILE=$PWD/playaural.service
        touch "$SERVICE_FILE"
        EVENTS=()
        IS_ACTIVE=0
        systemctl() {
            case "$1" in
                is-active) [ "$IS_ACTIVE" -eq 1 ] ;;
                stop) EVENTS+=(systemctl:stop); IS_ACTIVE=0 ;;
                reset-failed) EVENTS+=(systemctl:reset-failed) ;;
                start) EVENTS+=(systemctl:start); IS_ACTIVE=1 ;;
                cat) return 0 ;;
                *) return 0 ;;
            esac
        }
        ensure_cli_environment() { EVENTS+=(environment); }
        verify_database_storage() { EVENTS+=(verify); }
        run_role_cli() { EVENTS+=("role:$1:$2"); }
        sleep() { :; }

        IS_ACTIVE=1
        apply_user_role_change Rory101 developer
        printf '%s\n' "${EVENTS[*]}"
        """,
    )

    assert result.stdout.rstrip().endswith(
        "systemctl:stop environment verify role:Rory101:developer verify "
        "systemctl:reset-failed systemctl:start"
    )


def test_role_validation_rejection_restarts_service_but_storage_failure_does_not(
    tmp_path,
):
    result = _run_script_functions(
        tmp_path,
        """
        set -euo pipefail
        SERVICE_FILE=$PWD/playaural.service
        touch "$SERVICE_FILE"
        EVENTS=()
        IS_ACTIVE=1
        ROLE_RESULT=2
        systemctl() {
            case "$1" in
                is-active) [ "$IS_ACTIVE" -eq 1 ] ;;
                stop) EVENTS+=(systemctl:stop); IS_ACTIVE=0 ;;
                reset-failed) EVENTS+=(systemctl:reset-failed) ;;
                start) EVENTS+=(systemctl:start); IS_ACTIVE=1 ;;
                cat) return 0 ;;
                *) return 0 ;;
            esac
        }
        ensure_cli_environment() { EVENTS+=(environment); }
        verify_database_storage() { EVENTS+=(verify); }
        run_role_cli() { EVENTS+=("role:$1:$2:$ROLE_RESULT"); return "$ROLE_RESULT"; }
        sleep() { :; }

        if apply_user_role_change Rory101 developer; then exit 64; fi
        printf 'validation=%s\n' "${EVENTS[*]}"

        EVENTS=()
        IS_ACTIVE=1
        ROLE_RESULT=1
        if apply_user_role_change Rory101 developer; then exit 65; fi
        printf 'storage=%s\n' "${EVENTS[*]}"
        """,
    )

    assert (
        "validation=systemctl:stop environment verify role:Rory101:developer:2 "
        "systemctl:reset-failed systemctl:start\n"
    ) in result.stdout
    assert (
        "storage=systemctl:stop environment verify role:Rory101:developer:1\n"
    ) in result.stdout


def test_role_change_leaves_an_initially_stopped_service_stopped(tmp_path):
    result = _run_script_functions(
        tmp_path,
        """
        set -euo pipefail
        SERVICE_FILE=$PWD/playaural.service
        touch "$SERVICE_FILE"
        EVENTS=()
        systemctl() {
            case "$1" in
                is-active) return 1 ;;
                stop) EVENTS+=(systemctl:stop) ;;
                cat) return 0 ;;
                *) EVENTS+=("systemctl:$1") ;;
            esac
        }
        ensure_cli_environment() { EVENTS+=(environment); }
        verify_database_storage() { EVENTS+=(verify); }
        run_role_cli() { EVENTS+=("role:$1:$2"); }

        apply_user_role_change Rory101 admin
        printf '%s\n' "${EVENTS[*]}"
        """,
    )

    assert result.stdout.rstrip().endswith(
        "systemctl:stop environment verify role:Rory101:admin verify"
    )
