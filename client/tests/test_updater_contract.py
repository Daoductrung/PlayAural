from __future__ import annotations

import os
import sys
from dataclasses import replace
from pathlib import Path

import pytest


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

import client_info
from update_engine import UpdateInstallationError
from update_contract import packaged_sounds_directory
from updater import (
    UpdaterApp,
    UpdaterArguments,
    installation_process_ids,
    leave_installation_working_directory,
    parse_arguments,
    select_updater_working_directory,
    update_package_requirements,
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
        (
            {"extract_directory": Path("sounds")},
            "invalid-update-mode",
        ),
        (
            {"version_file": Path("version.txt")},
            "invalid-update-mode",
        ),
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


def test_standalone_sound_contract_rejects_an_external_destination(tmp_path):
    arguments = replace(
        _arguments(tmp_path),
        extract_directory=tmp_path / "external-sounds",
        version_file=Path("version.txt"),
    )

    with pytest.raises(UpdateInstallationError, match="unsafe-target"):
        validate_windows_updater_contract(arguments)


def test_standalone_sound_contract_accepts_a_nested_destination(tmp_path):
    target = tmp_path / "PlayAural"
    arguments = replace(
        _arguments(tmp_path),
        extract_directory=target / "_internal" / "sounds",
        version_file=Path("version.txt"),
    )

    validate_windows_updater_contract(arguments)


def test_installation_process_scan_is_bounded_to_the_target_tree(
    monkeypatch,
    tmp_path,
):
    target = tmp_path / "PlayAural"

    class Process:
        def __init__(self, pid, executable):
            self.info = {"pid": pid, "exe": str(executable) if executable else None}

    monkeypatch.setattr(
        "updater.psutil.process_iter",
        lambda _attrs: (
            Process(10, target / "PlayAural.exe"),
            Process(11, target / "_internal" / "helper.exe"),
            Process(12, tmp_path / "Other" / "PlayAural.exe"),
            Process(13, None),
            Process(14, "Registry"),
        ),
    )

    assert installation_process_ids(target, excluded_pids={10}) == (11,)


def test_updater_waits_for_other_installation_processes_to_exit(
    monkeypatch,
    tmp_path,
):
    app = object.__new__(UpdaterApp)
    app.arguments = _arguments(tmp_path)
    statuses = []
    results = iter(((42,), ()))
    monkeypatch.setattr(
        "updater.installation_process_ids",
        lambda *_args, **_kwargs: next(results),
    )
    monkeypatch.setattr("updater.time.sleep", lambda _seconds: None)
    app._publish_status = lambda message_id, **params: statuses.append(
        (message_id, params)
    )

    assert app._wait_for_installation_processes()
    assert statuses == [
        ("updater-status-waiting-other-processes", {"count": 1})
    ]


def test_updater_reports_other_installation_processes_after_timeout(
    monkeypatch,
    tmp_path,
):
    app = object.__new__(UpdaterApp)
    app.arguments = _arguments(tmp_path)
    events = []
    times = iter((0.0, 31.0))
    monkeypatch.setattr(
        "updater.installation_process_ids",
        lambda *_args, **_kwargs: (42, 84),
    )
    monkeypatch.setattr("updater.time.monotonic", lambda: next(times))
    monkeypatch.setattr(
        "updater.Localization.get",
        lambda message_id, **params: f"{message_id}:{params}",
    )
    app._publish_status = lambda *_args, **_kwargs: None
    app._publish = lambda event, payload: events.append((event, payload))

    assert not app._wait_for_installation_processes()
    assert events[0][0] == "error"
    assert "42, 84" in events[0][1]


def test_updater_leaves_an_installation_cwd_before_replacing_the_tree(
    monkeypatch,
    tmp_path,
):
    arguments = _arguments(tmp_path)
    arguments.target_directory.mkdir()
    executable_path = arguments.target_directory / "updater.exe"
    unsafe_temp = arguments.target_directory / "temp"
    unsafe_temp.mkdir()
    monkeypatch.chdir(arguments.target_directory)

    if os.name == "nt":
        with pytest.raises(PermissionError):
            os.replace(arguments.target_directory, tmp_path / "blocked-backup")

    selected = leave_installation_working_directory(
        arguments,
        executable_path=executable_path,
        temporary_directory=unsafe_temp,
    )

    assert selected == tmp_path.resolve()
    assert Path.cwd() == tmp_path.resolve()
    os.replace(arguments.target_directory, tmp_path / "released-backup")
    assert (tmp_path / "released-backup" / "temp").is_dir()


def test_updater_rejects_runtime_candidates_inside_the_installation(tmp_path):
    target = tmp_path / "PlayAural"
    target.mkdir()
    runtime = target / "runtime"
    runtime.mkdir()
    arguments = replace(
        _arguments(tmp_path),
        archive_path=runtime / "release.zip",
    )

    with pytest.raises(UpdateInstallationError, match="unsafe-runtime-directory"):
        select_updater_working_directory(
            arguments,
            executable_path=runtime / "updater.exe",
            temporary_directory=runtime,
        )


def test_application_package_requires_the_executable_and_updater(tmp_path):
    arguments = _arguments(tmp_path)

    apply_directory, required_files, required_text_files = (
        update_package_requirements(arguments)
    )

    assert apply_directory == arguments.target_directory.resolve()
    assert Path("PlayAural.exe") in required_files
    assert Path("updater.exe") in required_files
    assert required_text_files == {}


def test_sound_package_keeps_its_independent_version_requirement(tmp_path):
    target = tmp_path / "PlayAural"
    sounds = target / "_internal" / "sounds"
    arguments = replace(
        _arguments(tmp_path),
        extract_directory=sounds,
        version_file=Path("version.txt"),
    )

    apply_directory, required_files, required_text_files = (
        update_package_requirements(arguments)
    )

    assert apply_directory == sounds.resolve()
    assert required_files == ()
    assert required_text_files == {Path("version.txt"): "2"}


def test_packaged_sounds_directory_supports_both_bundle_layouts(tmp_path):
    installation = tmp_path / "PlayAural"
    installation.mkdir()

    assert packaged_sounds_directory(installation) == installation / "sounds"

    internal = installation / "_internal"
    internal.mkdir()
    assert packaged_sounds_directory(installation) == internal / "sounds"
