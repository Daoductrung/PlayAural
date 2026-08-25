from __future__ import annotations

import hashlib
import os
import stat
import zipfile
from pathlib import Path

import pytest


CLIENT_DIR = Path(__file__).resolve().parents[1]

import sys

if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

import update_engine
from update_bootstrap import (
    cleanup_stale_update_files,
    consume_update_helper_cleanup_path,
    delete_update_helper_with_retry,
    mark_update_ready,
    update_helper_cleanup_arguments,
    update_ready_marker_matches,
    update_ready_path,
    update_token_from_arguments,
)
from update_contract import TEMPORARY_UPDATER_PREFIX
from update_engine import (
    UpdateInstallationError,
    cleanup_stale_transaction_directories,
    stage_and_swap_update,
)


def _write_zip(path: Path, files: dict[str, bytes | str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def test_application_update_replaces_the_complete_tree_and_commits(tmp_path):
    target = tmp_path / "PlayAural"
    target.mkdir()
    (target / "PlayAural.exe").write_text("old executable", encoding="utf-8")
    (target / "stale.dll").write_text("stale", encoding="utf-8")
    archive = tmp_path / "release.zip"
    _write_zip(
        archive,
        {
            "PlayAural/PlayAural.exe": "new executable",
            "PlayAural/_internal/version.txt": "new",
        },
    )

    lifecycle = []
    transaction = stage_and_swap_update(
        archive,
        target_directory=target,
        apply_directory=target,
        required_files=(Path("PlayAural.exe"),),
        before_swap_callback=lambda: lifecycle.append(
            (target / "PlayAural.exe").read_text(encoding="utf-8")
        ),
    )

    assert (target / "PlayAural.exe").read_text(encoding="utf-8") == "new executable"
    assert not (target / "stale.dll").exists()
    assert lifecycle == ["old executable"]
    backup = transaction.backup_directory
    assert backup is not None and backup.is_dir()

    transaction.commit()

    assert not backup.exists()


def test_failed_startup_can_roll_back_the_complete_tree(tmp_path):
    target = tmp_path / "PlayAural"
    target.mkdir()
    (target / "PlayAural.exe").write_text("old executable", encoding="utf-8")
    (target / "old-only.dat").write_text("keep", encoding="utf-8")
    archive = tmp_path / "release.zip"
    _write_zip(archive, {"PlayAural/PlayAural.exe": "new executable"})

    transaction = stage_and_swap_update(
        archive,
        target_directory=target,
        apply_directory=target,
        required_files=(Path("PlayAural.exe"),),
    )
    transaction.rollback()

    assert (target / "PlayAural.exe").read_text(encoding="utf-8") == "old executable"
    assert (target / "old-only.dat").read_text(encoding="utf-8") == "keep"


def test_missing_rollback_backup_never_deletes_the_only_installed_tree(tmp_path):
    target = tmp_path / "PlayAural"
    target.mkdir()
    (target / "PlayAural.exe").write_text("old executable", encoding="utf-8")
    archive = tmp_path / "release.zip"
    _write_zip(archive, {"PlayAural/PlayAural.exe": "new executable"})
    transaction = stage_and_swap_update(
        archive,
        target_directory=target,
        apply_directory=target,
        required_files=(Path("PlayAural.exe"),),
    )
    backup = transaction.backup_directory
    assert backup is not None
    for child in backup.iterdir():
        child.unlink()
    backup.rmdir()

    with pytest.raises(UpdateInstallationError, match="backup-missing"):
        transaction.rollback()

    assert (target / "PlayAural.exe").read_text(encoding="utf-8") == (
        "new executable"
    )
    assert not tuple(tmp_path.glob(".PlayAural.failed-*"))


def test_failed_precommit_restore_retains_the_previous_installation_backup(
    monkeypatch,
    tmp_path,
):
    target = tmp_path / "PlayAural"
    target.mkdir()
    (target / "PlayAural.exe").write_text("old executable", encoding="utf-8")
    archive = tmp_path / "release.zip"
    _write_zip(archive, {"PlayAural/PlayAural.exe": "new executable"})

    def fail_after_backup(source, destination, *, policy):
        if source == target:
            os.replace(source, destination)
            return
        raise UpdateInstallationError("updater-error-files-in-use")

    monkeypatch.setattr(update_engine, "_replace_with_retry", fail_after_backup)

    with pytest.raises(UpdateInstallationError, match="precommit-restore-failed"):
        stage_and_swap_update(
            archive,
            target_directory=target,
            apply_directory=target,
        )

    backups = tuple(tmp_path.glob(".PlayAural.backup-*"))
    assert len(backups) == 1
    assert (backups[0] / "PlayAural.exe").read_text(encoding="utf-8") == (
        "old executable"
    )
    assert not target.exists()
    assert not tuple(tmp_path.glob(".PlayAural.stage-*"))


@pytest.mark.parametrize(
    ("winerror", "message_id"),
    [
        (32, "updater-error-files-in-use"),
        (5, "updater-error-permission-denied"),
    ],
)
def test_replace_retry_reports_the_actual_windows_failure(
    monkeypatch,
    tmp_path,
    winerror,
    message_id,
):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    attempts = 0

    class WindowsOperationError(OSError):
        pass

    operation_error = WindowsOperationError("Windows operation failed")
    operation_error.winerror = winerror

    def fail_replace(_source, _destination):
        nonlocal attempts
        attempts += 1
        raise operation_error

    monkeypatch.setattr(update_engine.os, "replace", fail_replace)
    policy = update_engine.InstallationPolicy(
        file_operation_timeout_seconds=0.001,
        file_operation_retry_seconds=0.001,
    )

    with pytest.raises(UpdateInstallationError) as captured:
        update_engine._replace_with_retry(source, destination, policy=policy)

    assert captured.value.message_id == message_id
    assert captured.value.params["source"] == str(source)
    assert captured.value.params["destination"] == str(destination)
    assert attempts >= 2


def test_replace_does_not_retry_a_deterministic_filesystem_error(
    monkeypatch,
    tmp_path,
):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    attempts = 0

    def fail_replace(_source, _destination):
        nonlocal attempts
        attempts += 1
        raise FileNotFoundError("source disappeared")

    monkeypatch.setattr(update_engine.os, "replace", fail_replace)

    with pytest.raises(UpdateInstallationError) as captured:
        update_engine._replace_with_retry(
            source,
            destination,
            policy=update_engine.InstallationPolicy(),
        )

    assert captured.value.message_id == "updater-error-file-operation-failed"
    assert captured.value.params["error"] == "source disappeared"
    assert attempts == 1


def test_sound_update_is_transactional_and_strips_its_package_root(tmp_path):
    target = tmp_path / "PlayAural"
    sounds = target / "_internal" / "sounds"
    sounds.mkdir(parents=True)
    (target / "PlayAural.exe").write_text("executable", encoding="utf-8")
    (sounds / "version.txt").write_text("old", encoding="utf-8")
    (sounds / "removed.ogg").write_bytes(b"old")
    archive = tmp_path / "sounds.zip"
    _write_zip(
        archive,
        {
            "sounds/version.txt": "new",
            "sounds/added.ogg": b"new",
        },
    )

    transaction = stage_and_swap_update(
        archive,
        target_directory=target,
        apply_directory=sounds,
        required_files=(Path("version.txt"),),
    )

    assert (sounds / "version.txt").read_text(encoding="utf-8") == "new"
    assert (sounds / "added.ogg").read_bytes() == b"new"
    assert not (sounds / "removed.ogg").exists()
    assert (target / "PlayAural.exe").is_file()
    transaction.commit()


@pytest.mark.parametrize(
    "member_name",
    [
        "../outside.txt",
        "/absolute.txt",
        "C:/windows/path.txt",
        "folder/CON.txt",
        "folder/trailing. ",
    ],
)
def test_unsafe_archive_paths_are_rejected_without_touching_install(
    tmp_path,
    member_name,
):
    target = tmp_path / "PlayAural"
    target.mkdir()
    executable = target / "PlayAural.exe"
    executable.write_text("old", encoding="utf-8")
    archive = tmp_path / "unsafe.zip"
    _write_zip(archive, {member_name: "bad"})

    with pytest.raises(UpdateInstallationError, match="unsafe-package-path"):
        stage_and_swap_update(
            archive,
            target_directory=target,
            apply_directory=target,
        )

    assert executable.read_text(encoding="utf-8") == "old"
    assert not (tmp_path / "outside.txt").exists()


def test_symbolic_links_and_case_collisions_are_rejected(tmp_path):
    target = tmp_path / "PlayAural"
    target.mkdir()
    (target / "PlayAural.exe").write_text("old", encoding="utf-8")

    link_archive = tmp_path / "link.zip"
    link_info = zipfile.ZipInfo("PlayAural/link")
    link_info.create_system = 3
    link_info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(link_archive, "w") as archive:
        archive.writestr(link_info, "target")
    with pytest.raises(UpdateInstallationError, match="package-link"):
        stage_and_swap_update(
            link_archive,
            target_directory=target,
            apply_directory=target,
        )

    collision_archive = tmp_path / "collision.zip"
    _write_zip(
        collision_archive,
        {
            "PlayAural/File.txt": "one",
            "PlayAural/file.TXT": "two",
        },
    )
    with pytest.raises(UpdateInstallationError, match="path-collision"):
        stage_and_swap_update(
            collision_archive,
            target_directory=target,
            apply_directory=target,
        )


def test_checksum_and_required_file_failures_preserve_the_install(tmp_path):
    target = tmp_path / "PlayAural"
    target.mkdir()
    executable = target / "PlayAural.exe"
    executable.write_text("old", encoding="utf-8")
    archive = tmp_path / "release.zip"
    _write_zip(archive, {"PlayAural/not-the-app.txt": "incomplete"})

    with pytest.raises(UpdateInstallationError, match="hash-mismatch"):
        stage_and_swap_update(
            archive,
            target_directory=target,
            apply_directory=target,
            expected_sha256="0" * 64,
        )

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    with pytest.raises(UpdateInstallationError, match="required-file-missing"):
        stage_and_swap_update(
            archive,
            target_directory=target,
            apply_directory=target,
            expected_sha256=digest,
            required_files=(Path("PlayAural.exe"),),
        )

    assert executable.read_text(encoding="utf-8") == "old"


def test_required_text_version_is_validated_before_swap(tmp_path):
    target = tmp_path / "PlayAural"
    sounds = target / "sounds"
    sounds.mkdir(parents=True)
    (sounds / "version.txt").write_text("old", encoding="utf-8")
    archive = tmp_path / "sounds.zip"
    _write_zip(archive, {"sounds/version.txt": "wrong"})

    with pytest.raises(UpdateInstallationError, match="required-file-version"):
        stage_and_swap_update(
            archive,
            target_directory=target,
            apply_directory=sounds,
            required_text_files={Path("version.txt"): "expected"},
        )

    assert (sounds / "version.txt").read_text(encoding="utf-8") == "old"


def test_application_artifact_does_not_require_a_redundant_manifest(tmp_path):
    target = tmp_path / "PlayAural"
    target.mkdir()
    executable = target / "PlayAural.exe"
    executable.write_text("old executable", encoding="utf-8")
    archive = tmp_path / "old-release.zip"
    _write_zip(
        archive,
        {
            "PlayAural/PlayAural.exe": "downloaded executable",
            "PlayAural/updater.exe": "old updater",
        },
    )

    transaction = stage_and_swap_update(
        archive,
        target_directory=target,
        apply_directory=target,
        required_files=(Path("PlayAural.exe"), Path("updater.exe")),
    )

    assert executable.read_text(encoding="utf-8") == "downloaded executable"
    assert (target / "updater.exe").read_text(encoding="utf-8") == "old updater"
    transaction.commit()
    assert not tuple(tmp_path.glob(".PlayAural.stage-*"))
    assert not tuple(tmp_path.glob(".PlayAural.backup-*"))


def test_update_health_tokens_are_bounded_to_the_temp_directory(tmp_path):
    token = "a" * 32

    assert update_token_from_arguments(["--update-token", token]) == token
    assert update_token_from_arguments(["--update-token", "../escape"]) == ""
    assert update_ready_path(token, tmp_path).parent == tmp_path.resolve()


def test_health_marker_identifies_process_version_and_consumes_token(
    tmp_path,
    monkeypatch,
):
    token = "b" * 32
    monkeypatch.setattr(
        sys,
        "argv",
        ["PlayAural.exe", "--update-token", token, "--keep"],
    )
    monkeypatch.setattr("update_bootstrap.tempfile.gettempdir", lambda: str(tmp_path))

    assert mark_update_ready(client_version="2.0")
    assert sys.argv == ["PlayAural.exe", "--keep"]
    marker_path = update_ready_path(token, tmp_path)
    assert update_ready_marker_matches(
        marker_path,
        token=token,
        process_id=os.getpid(),
        client_version="2.0",
    )
    assert not update_ready_marker_matches(
        marker_path,
        token=token,
        process_id=os.getpid(),
        client_version="1.0",
    )


def test_temporary_updater_cleanup_handoff_is_bounded_and_consumed(
    tmp_path,
    monkeypatch,
):
    helper = tmp_path / f"{TEMPORARY_UPDATER_PREFIX}{'e' * 32}.exe"
    helper.write_bytes(b"helper")
    unrelated = tmp_path / "unrelated.exe"
    unrelated.write_bytes(b"keep")

    assert update_helper_cleanup_arguments(
        helper,
        temp_directory=tmp_path,
    ) == ["--cleanup-update-helper", str(helper.resolve())]
    assert update_helper_cleanup_arguments(
        unrelated,
        temp_directory=tmp_path,
    ) == []

    monkeypatch.setattr(
        sys,
        "argv",
        ["PlayAural.exe", "--cleanup-update-helper", str(helper), "--keep"],
    )
    cleanup_path = consume_update_helper_cleanup_path(temp_directory=tmp_path)

    assert cleanup_path == helper.resolve()
    assert sys.argv == ["PlayAural.exe", "--keep"]
    assert delete_update_helper_with_retry(
        cleanup_path,
        temp_directory=tmp_path,
        timeout_seconds=0,
    )
    assert not helper.exists()
    assert unrelated.read_bytes() == b"keep"


def test_stale_update_cleanup_is_bounded_to_known_temp_files(tmp_path):
    stale_helper = tmp_path / f"{TEMPORARY_UPDATER_PREFIX}{'a' * 32}.exe"
    stale_download = tmp_path / "playaural-application-old.zip.part"
    legacy_helper = tmp_path / "playaural_updater_123.exe"
    legacy_download = tmp_path / "playaural_sounds_123.zip"
    unrelated = tmp_path / "unrelated.exe"
    stale_helper.write_bytes(b"helper")
    stale_download.write_bytes(b"partial")
    legacy_helper.write_bytes(b"legacy helper")
    legacy_download.write_bytes(b"legacy download")
    unrelated.write_bytes(b"keep")
    os.utime(stale_helper, (1, 1))
    os.utime(stale_download, (1, 1))
    os.utime(legacy_helper, (1, 1))
    os.utime(legacy_download, (1, 1))

    cleanup_stale_update_files(temp_directory=tmp_path, maximum_age_seconds=1)

    assert not stale_helper.exists()
    assert not stale_download.exists()
    assert not legacy_helper.exists()
    assert not legacy_download.exists()
    assert unrelated.read_bytes() == b"keep"


def test_stale_transaction_cleanup_preserves_recent_and_recoverable_backups(
    tmp_path,
):
    apply_directory = tmp_path / "PlayAural"
    apply_directory.mkdir()
    stale_stage = tmp_path / f".PlayAural.stage-{'a' * 32}"
    stale_backup = tmp_path / f".PlayAural.backup-{'b' * 32}"
    recent_failure = tmp_path / f".PlayAural.failed-{'c' * 32}"
    unrelated = tmp_path / ".PlayAural.backup-not-a-token"
    for directory in (stale_stage, stale_backup, recent_failure, unrelated):
        directory.mkdir()
    os.utime(stale_stage, (1, 1))
    os.utime(stale_backup, (1, 1))

    cleanup_stale_transaction_directories(
        apply_directory,
        maximum_age_seconds=1_000,
    )

    assert not stale_stage.exists()
    assert not stale_backup.exists()
    assert recent_failure.exists()
    assert unrelated.exists()

    recoverable_backup = tmp_path / f".Missing.backup-{'d' * 32}"
    recoverable_backup.mkdir()
    os.utime(recoverable_backup, (1, 1))
    cleanup_stale_transaction_directories(
        tmp_path / "Missing",
        maximum_age_seconds=1_000,
    )
    assert recoverable_backup.exists()
