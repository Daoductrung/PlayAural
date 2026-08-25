"""Transactional installation engine for PlayAural desktop updates."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import time
import uuid
import zipfile
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MAXIMUM_REQUIRED_TEXT_FILE_BYTES = 4 * 1024
STALE_TRANSACTION_MAX_AGE_SECONDS = 24 * 60 * 60
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
WINDOWS_INVALID_COMPONENT_RE = re.compile(r"[<>:\"|?*\x00-\x1f]")
WINDOWS_RESERVED_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{index}" for index in range(1, 10)),
        *(f"LPT{index}" for index in range(1, 10)),
    }
)


class UpdateInstallationError(Exception):
    """A localized, user-actionable installation failure."""

    def __init__(self, message_id: str, **params: object) -> None:
        super().__init__(message_id)
        self.message_id = message_id
        self.params = params


@dataclass(frozen=True, slots=True)
class InstallationPolicy:
    """Resource and retry boundaries for unpacking a release."""

    maximum_members: int = 100_000
    maximum_member_bytes: int = 2 * 1024 * 1024 * 1024
    maximum_total_bytes: int = 4 * 1024 * 1024 * 1024
    maximum_compression_ratio: int = 1_000
    minimum_free_space_reserve_bytes: int = 64 * 1024 * 1024
    file_operation_timeout_seconds: float = 30.0
    file_operation_retry_seconds: float = 0.25

    def __post_init__(self) -> None:
        numeric_values = (
            self.maximum_members,
            self.maximum_member_bytes,
            self.maximum_total_bytes,
            self.maximum_compression_ratio,
        )
        if any(value <= 0 for value in numeric_values):
            raise ValueError("installation resource limits must be positive")
        if self.minimum_free_space_reserve_bytes < 0:
            raise ValueError("free space reserve cannot be negative")
        if self.file_operation_timeout_seconds <= 0:
            raise ValueError("file operation timeout must be positive")
        if self.file_operation_retry_seconds <= 0:
            raise ValueError("file operation retry interval must be positive")


@dataclass(frozen=True, slots=True)
class ExtractionProgress:
    """Progress for one safely extracted archive member."""

    completed_members: int
    total_members: int
    relative_path: Path

    @property
    def percent(self) -> int:
        if self.total_members <= 0:
            return 100
        return min(100, int(self.completed_members * 100 / self.total_members))


@dataclass(frozen=True, slots=True)
class _ArchiveMember:
    info: zipfile.ZipInfo
    relative_path: Path


def validate_sha256(value: object) -> str:
    """Normalize an optional SHA-256 digest or reject malformed metadata."""
    digest = str(value or "").strip().lower()
    if digest and not SHA256_RE.fullmatch(digest):
        raise UpdateInstallationError("updater-error-invalid-hash")
    return digest


def verify_sha256(path: Path, expected: object) -> None:
    """Verify an artifact immediately before installation."""
    digest = validate_sha256(expected)
    if not digest:
        return
    calculated = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                calculated.update(block)
    except OSError as error:
        raise UpdateInstallationError("updater-error-package-unreadable") from error
    if calculated.hexdigest() != digest:
        raise UpdateInstallationError("updater-error-hash-mismatch")


def _is_zip_symlink(info: zipfile.ZipInfo) -> bool:
    unix_mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(unix_mode)


def _validate_path_component(component: str) -> None:
    if not component or component in {".", ".."}:
        raise UpdateInstallationError("updater-error-unsafe-package-path")
    if component[-1] in {" ", "."}:
        raise UpdateInstallationError("updater-error-unsafe-package-path")
    if WINDOWS_INVALID_COMPONENT_RE.search(component):
        raise UpdateInstallationError("updater-error-unsafe-package-path")
    base_name = component.split(".", 1)[0].upper()
    if base_name in WINDOWS_RESERVED_NAMES:
        raise UpdateInstallationError("updater-error-unsafe-package-path")


def _normalized_member_parts(info: zipfile.ZipInfo) -> tuple[str, ...]:
    raw_name = info.filename.replace("\\", "/")
    if (
        not raw_name
        or raw_name.startswith("/")
        or raw_name.startswith("//")
        or WINDOWS_DRIVE_RE.match(raw_name)
    ):
        raise UpdateInstallationError("updater-error-unsafe-package-path")
    parts = tuple(part for part in PurePosixPath(raw_name).parts if part != "/")
    for part in parts:
        _validate_path_component(part)
    return parts


def _archive_members(
    archive: zipfile.ZipFile,
    policy: InstallationPolicy,
) -> list[_ArchiveMember]:
    infos = archive.infolist()
    if len(infos) > policy.maximum_members:
        raise UpdateInstallationError("updater-error-package-too-many-files")

    candidates: list[tuple[zipfile.ZipInfo, tuple[str, ...]]] = []
    total_bytes = 0
    for info in infos:
        parts = _normalized_member_parts(info)
        if info.is_dir():
            continue
        if not parts:
            raise UpdateInstallationError("updater-error-unsafe-package-path")
        if info.flag_bits & 0x1:
            raise UpdateInstallationError("updater-error-encrypted-package")
        if _is_zip_symlink(info):
            raise UpdateInstallationError("updater-error-package-link")
        if info.file_size > policy.maximum_member_bytes:
            raise UpdateInstallationError("updater-error-package-file-too-large")
        total_bytes += info.file_size
        if total_bytes > policy.maximum_total_bytes:
            raise UpdateInstallationError("updater-error-package-too-large")
        if info.file_size > 0:
            compressed_size = max(1, info.compress_size)
            if info.file_size / compressed_size > policy.maximum_compression_ratio:
                raise UpdateInstallationError("updater-error-package-ratio")
        candidates.append((info, parts))

    if not candidates:
        raise UpdateInstallationError("updater-error-empty-package")

    roots = {parts[0].casefold() for _, parts in candidates}
    strip_root = len(roots) == 1 and all(len(parts) > 1 for _, parts in candidates)

    members: list[_ArchiveMember] = []
    file_keys: set[str] = set()
    directory_keys: set[str] = set()
    for info, original_parts in candidates:
        parts = original_parts[1:] if strip_root else original_parts
        if not parts:
            raise UpdateInstallationError("updater-error-empty-package")
        relative_path = Path(*parts)
        key = "/".join(parts).casefold()
        if key in file_keys or key in directory_keys:
            raise UpdateInstallationError("updater-error-package-path-collision")
        ancestor_parts: list[str] = []
        for part in parts[:-1]:
            ancestor_parts.append(part)
            ancestor_key = "/".join(ancestor_parts).casefold()
            if ancestor_key in file_keys:
                raise UpdateInstallationError("updater-error-package-path-collision")
            directory_keys.add(ancestor_key)
        file_keys.add(key)
        members.append(_ArchiveMember(info, relative_path))
    return members


def validate_archive_package(
    archive_path: Path,
    *,
    policy: InstallationPolicy | None = None,
    verify_crc: bool = True,
) -> None:
    """Validate archive structure, resource bounds, and optionally every CRC."""
    active_policy = policy or InstallationPolicy()
    try:
        with zipfile.ZipFile(archive_path) as archive:
            _archive_members(archive, active_policy)
            if verify_crc:
                corrupt_member = archive.testzip()
                if corrupt_member is not None:
                    raise UpdateInstallationError(
                        "updater-error-corrupt-package",
                        member=corrupt_member,
                    )
    except UpdateInstallationError:
        raise
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as error:
        raise UpdateInstallationError("updater-error-package-unreadable") from error


def _remove_owned_tree(path: Path, expected_parent: Path) -> None:
    resolved_path = path.resolve()
    resolved_parent = expected_parent.resolve()
    if resolved_path.parent != resolved_parent:
        raise UpdateInstallationError("updater-error-unsafe-cleanup-path")
    if resolved_path.is_dir():
        shutil.rmtree(resolved_path)
    elif resolved_path.exists():
        resolved_path.unlink()


def cleanup_stale_transaction_directories(
    apply_directory: Path,
    *,
    maximum_age_seconds: float = STALE_TRANSACTION_MAX_AGE_SECONDS,
) -> None:
    """Prune only expired updater-owned stage, backup, and failure trees."""
    if maximum_age_seconds < 0:
        raise ValueError("maximum_age_seconds cannot be negative")
    apply_directory = apply_directory.resolve()
    parent = apply_directory.parent
    owned_name = re.compile(
        rf"^\.{re.escape(apply_directory.name)}\.(stage|backup|failed)-[0-9a-f]{{32}}$"
    )
    cutoff = time.time() - maximum_age_seconds
    try:
        candidates = tuple(parent.iterdir())
    except OSError:
        return
    for candidate in candidates:
        match = owned_name.fullmatch(candidate.name)
        if not match:
            continue
        try:
            resolved = candidate.resolve()
            if resolved.parent != parent or not resolved.is_dir():
                continue
            if match.group(1) == "backup" and not apply_directory.is_dir():
                continue
            if resolved.stat().st_mtime > cutoff:
                continue
            _remove_owned_tree(resolved, parent)
        except (OSError, UpdateInstallationError):
            continue


def extract_archive_safely(
    archive_path: Path,
    destination: Path,
    *,
    policy: InstallationPolicy,
    progress_callback: Callable[[ExtractionProgress], None] | None = None,
) -> None:
    """Extract a validated archive into a new, empty staging directory."""
    if destination.exists():
        raise UpdateInstallationError("updater-error-stage-exists")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = _archive_members(archive, policy)
            required_bytes = sum(member.info.file_size for member in members)
            available_bytes = shutil.disk_usage(destination.parent).free
            if (
                available_bytes
                < required_bytes + policy.minimum_free_space_reserve_bytes
            ):
                raise UpdateInstallationError(
                    "updater-error-insufficient-space",
                    required_mb=(
                        required_bytes + policy.minimum_free_space_reserve_bytes
                    )
                    // (1024 * 1024),
                    available_mb=available_bytes // (1024 * 1024),
                )
            destination.mkdir(parents=True)
            destination_root = destination.resolve()
            for index, member in enumerate(members, start=1):
                output_path = destination / member.relative_path
                resolved_output = output_path.resolve()
                if destination_root not in resolved_output.parents:
                    raise UpdateInstallationError(
                        "updater-error-unsafe-package-path"
                    )
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member.info) as source, output_path.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                unix_mode = (member.info.external_attr >> 16) & 0o777
                if os.name != "nt" and unix_mode:
                    output_path.chmod(unix_mode)
                if progress_callback:
                    progress_callback(
                        ExtractionProgress(index, len(members), member.relative_path)
                    )
    except UpdateInstallationError:
        raise
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as error:
        raise UpdateInstallationError("updater-error-extraction-failed") from error


def _replace_with_retry(
    source: Path,
    destination: Path,
    *,
    policy: InstallationPolicy,
) -> None:
    deadline = time.monotonic() + policy.file_operation_timeout_seconds
    while True:
        try:
            os.replace(source, destination)
            return
        except OSError as error:
            if time.monotonic() >= deadline:
                raise UpdateInstallationError("updater-error-files-in-use") from error
            time.sleep(policy.file_operation_retry_seconds)


def _safe_required_path(stage: Path, required_file: Path) -> tuple[Path, Path]:
    relative = Path(required_file)
    if relative.is_absolute() or ".." in relative.parts:
        raise UpdateInstallationError("updater-error-invalid-required-file")
    return relative, stage / relative


def _validate_required_files(
    stage: Path,
    required_files: Iterable[Path],
    required_text_files: Mapping[Path, str],
) -> None:
    for required_file in required_files:
        relative, candidate = _safe_required_path(stage, Path(required_file))
        if not candidate.is_file():
            raise UpdateInstallationError(
                "updater-error-required-file-missing",
                path=str(relative),
            )
    for required_file, expected_value in required_text_files.items():
        relative, candidate = _safe_required_path(stage, Path(required_file))
        try:
            if (
                not candidate.is_file()
                or candidate.stat().st_size > MAXIMUM_REQUIRED_TEXT_FILE_BYTES
            ):
                raise OSError
            actual_value = candidate.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            actual_value = ""
        if actual_value != expected_value:
            raise UpdateInstallationError(
                "updater-error-required-file-version",
                path=str(relative),
                expected=expected_value,
                actual=actual_value,
            )


@dataclass(slots=True)
class PendingInstallation:
    """A swapped installation that remains rollback-capable until committed."""

    apply_directory: Path
    backup_directory: Path | None
    policy: InstallationPolicy
    _settled: bool = field(default=False, init=False)

    def commit(self) -> None:
        if self._settled:
            return
        if self.backup_directory and self.backup_directory.exists():
            try:
                _remove_owned_tree(
                    self.backup_directory,
                    self.apply_directory.parent,
                )
            except OSError:
                # A retained backup is safe and can be removed by a later update.
                pass
        self._settled = True

    def rollback(self) -> None:
        if self._settled:
            return
        failed_directory: Path | None = None
        restored = False
        try:
            if self.apply_directory.exists():
                failed_directory = self.apply_directory.parent / (
                    f".{self.apply_directory.name}.failed-{uuid.uuid4().hex}"
                )
                _replace_with_retry(
                    self.apply_directory,
                    failed_directory,
                    policy=self.policy,
                )
            if self.backup_directory:
                if not self.backup_directory.exists():
                    raise UpdateInstallationError(
                        "updater-error-rollback-backup-missing"
                    )
                _replace_with_retry(
                    self.backup_directory,
                    self.apply_directory,
                    policy=self.policy,
                )
            restored = True
        finally:
            if failed_directory and failed_directory.exists():
                try:
                    _remove_owned_tree(failed_directory, self.apply_directory.parent)
                except OSError:
                    pass
            if restored:
                self._settled = True


def stage_and_swap_update(
    archive_path: Path,
    *,
    target_directory: Path,
    apply_directory: Path,
    expected_sha256: object = "",
    required_files: Iterable[Path] = (),
    required_text_files: Mapping[Path, str] | None = None,
    policy: InstallationPolicy | None = None,
    progress_callback: Callable[[ExtractionProgress], None] | None = None,
) -> PendingInstallation:
    """Validate, stage, and atomically swap one application or asset tree."""
    active_policy = policy or InstallationPolicy()
    archive_path = archive_path.resolve()
    target_directory = target_directory.resolve()
    apply_directory = apply_directory.resolve()
    if apply_directory != target_directory and target_directory not in apply_directory.parents:
        raise UpdateInstallationError("updater-error-unsafe-target")
    if not target_directory.is_dir():
        raise UpdateInstallationError("updater-error-target-missing")
    if not archive_path.is_file():
        raise UpdateInstallationError("updater-error-package-missing")

    verify_sha256(archive_path, expected_sha256)
    transaction_id = uuid.uuid4().hex
    stage_directory = apply_directory.parent / (
        f".{apply_directory.name}.stage-{transaction_id}"
    )
    backup_directory = apply_directory.parent / (
        f".{apply_directory.name}.backup-{transaction_id}"
    )
    original_moved = False
    try:
        extract_archive_safely(
            archive_path,
            stage_directory,
            policy=active_policy,
            progress_callback=progress_callback,
        )
        _validate_required_files(
            stage_directory,
            required_files,
            required_text_files or {},
        )

        if apply_directory.exists():
            _replace_with_retry(
                apply_directory,
                backup_directory,
                policy=active_policy,
            )
            try:
                os.utime(backup_directory, None)
            except OSError:
                pass
            original_moved = True
        try:
            _replace_with_retry(
                stage_directory,
                apply_directory,
                policy=active_policy,
            )
        except UpdateInstallationError:
            if original_moved and backup_directory.exists():
                _replace_with_retry(
                    backup_directory,
                    apply_directory,
                    policy=active_policy,
                )
            raise
        return PendingInstallation(
            apply_directory=apply_directory,
            backup_directory=backup_directory if original_moved else None,
            policy=active_policy,
        )
    finally:
        if stage_directory.exists():
            try:
                _remove_owned_tree(stage_directory, apply_directory.parent)
            except OSError:
                pass
