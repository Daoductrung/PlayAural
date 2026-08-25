from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

import client_info
from update_engine import UpdateInstallationError
from updater import (
    UpdaterArguments,
    parse_arguments,
    validate_windows_updater_contract,
)


@pytest.fixture(autouse=True)
def _windows_release_target(monkeypatch):
    monkeypatch.setattr(client_info.platform, "system", lambda: "Windows")


def _arguments(tmp_path: Path) -> UpdaterArguments:
    return UpdaterArguments(
        archive_path=tmp_path / "release.zip",
        target_directory=tmp_path / "PlayAural",
        executable_name="PlayAural.exe",
        wait_pid=123,
        wait_process_started_at=None,
        extract_directory=None,
        expected_sha256="",
        required_files=(),
        artifact_version="2",
        expected_client_version="2",
        version_file=None,
        locale="en",
    )


def test_argument_parser_defaults_to_no_sha256_validation(tmp_path):
    parsed = parse_arguments(
        [
            "--zip",
            str(tmp_path / "release.zip"),
            "--target",
            str(tmp_path / "PlayAural"),
            "--exe",
            "PlayAural.exe",
            "--artifact-version",
            "2",
            "--expected-client-version",
            "2",
        ]
    )

    assert parsed.expected_sha256 == ""
    assert parsed.locale == "en"


def test_valid_windows_contract_does_not_require_a_sha256(tmp_path):
    arguments = _arguments(tmp_path)

    validate_windows_updater_contract(arguments)

    assert arguments.expected_sha256 == ""


@pytest.mark.parametrize(
    ("changes", "error_id"),
    [
        ({"archive_path": Path("release.exe")}, "windows-zip-required"),
        ({"executable_name": "PlayAural"}, "invalid-executable"),
        ({"executable_name": "../PlayAural.exe"}, "invalid-executable"),
        ({"wait_pid": 0}, "invalid-process"),
        ({"locale": "../en"}, "invalid-locale"),
        ({"artifact_version": ""}, "invalid-artifact-version"),
        ({"expected_client_version": ""}, "invalid-artifact-version"),
    ],
)
def test_standalone_contract_rejects_malformed_windows_arguments(
    tmp_path,
    changes,
    error_id,
):
    arguments = replace(_arguments(tmp_path), **changes)

    with pytest.raises(UpdateInstallationError, match=error_id):
        validate_windows_updater_contract(arguments)


def test_standalone_contract_rejects_non_windows_execution(monkeypatch, tmp_path):
    monkeypatch.setattr(client_info.platform, "system", lambda: "Darwin")

    with pytest.raises(UpdateInstallationError, match="windows-only"):
        validate_windows_updater_contract(_arguments(tmp_path))
