"""Standalone, transactional desktop updater for PlayAural."""

from __future__ import annotations

import argparse
import queue
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import psutil

from localization import Localization
from client_info import get_client_release_platform
from update_bootstrap import update_ready_marker_matches, update_ready_path
from update_contract import (
    DEFAULT_LOCALE_TAG,
    UPDATER_EXECUTABLE_NAME,
    WINDOWS_ARCHIVE_SUFFIX,
    WINDOWS_RELEASE_TARGET,
    is_valid_locale_tag,
    is_valid_windows_executable_name,
)
from update_engine import (
    ExtractionProgress,
    PendingInstallation,
    UpdateInstallationError,
    stage_and_swap_update,
)

try:
    import accessible_output2.outputs.auto as auto_output
except ImportError:  # pragma: no cover - the packaged updater includes it.
    auto_output = None

try:
    import winsound
except ImportError:  # pragma: no cover - retained for future desktop targets.
    winsound = None


WINDOW_WIDTH = 480
WINDOW_HEIGHT = 180
STATUS_WRAP_LENGTH = WINDOW_WIDTH - 40
UI_POLL_INTERVAL_MS = 50
COMPLETION_DISPLAY_MS = 1_000
PROCESS_WAIT_TIMEOUT_SECONDS = 30.0
HEALTH_READY_TIMEOUT_SECONDS = 30.0
HEALTH_STABILIZATION_SECONDS = 2.0
HEALTH_POLL_SECONDS = 0.1
PROCESS_TERMINATE_TIMEOUT_SECONDS = 5.0
PROGRESS_BEEP_STEP = 5
PROGRESS_ANNOUNCEMENT_STEP = 10
PROGRESS_MIN_FREQUENCY = 500
PROGRESS_MAX_FREQUENCY = 2_000
PROGRESS_BEEP_DURATION_MS = 50


@dataclass(frozen=True, slots=True)
class UpdaterArguments:
    archive_path: Path
    target_directory: Path
    executable_name: str
    wait_pid: int | None
    wait_process_started_at: float | None
    extract_directory: Path | None
    expected_sha256: str
    required_files: tuple[Path, ...]
    artifact_version: str
    expected_client_version: str
    version_file: Path | None
    locale: str


class UpdaterApp:
    """Accessible UI shell around the pure transactional update engine."""

    def __init__(self, arguments: UpdaterArguments) -> None:
        self.arguments = arguments
        self.events: queue.SimpleQueue[tuple[str, object]] = queue.SimpleQueue()
        self.last_beep_percent = -PROGRESS_BEEP_STEP
        self.last_announced_percent = -PROGRESS_ANNOUNCEMENT_STEP
        self.worker: threading.Thread | None = None
        try:
            self.speaker = auto_output.Auto() if auto_output else None
        except Exception:
            self.speaker = None

        self.root = tk.Tk()
        self.root.title(Localization.get("updater-window-title"))
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_requested)

        self.status_var = tk.StringVar(
            value=Localization.get("updater-status-initializing")
        )
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            wraplength=STATUS_WRAP_LENGTH,
        )
        self.status_label.pack(pady=12)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(
            self.root,
            variable=self.progress_var,
            maximum=100,
        )
        self.progress.pack(pady=10, fill=tk.X, padx=24)
        self._center_window()
        self.root.after(UI_POLL_INTERVAL_MS, self._drain_events)

    def _center_window(self) -> None:
        self.root.update_idletasks()
        x = max(0, (self.root.winfo_screenwidth() - WINDOW_WIDTH) // 2)
        y = max(0, (self.root.winfo_screenheight() - WINDOW_HEIGHT) // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _on_close_requested(self) -> None:
        messagebox.showinfo(
            Localization.get("updater-window-title"),
            Localization.get("updater-close-disabled"),
            parent=self.root,
        )

    def _publish(self, event: str, payload: object = None) -> None:
        self.events.put((event, payload))

    def _publish_status(
        self,
        message_id: str,
        *,
        announce: bool = True,
        **params: object,
    ) -> None:
        text = Localization.get(message_id, **params)
        self._publish("status", text)
        if announce:
            self._publish("announce", text)

    def _drain_events(self) -> None:
        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "status":
                self.status_var.set(str(payload))
            elif event == "progress":
                self.progress_var.set(float(payload))
            elif event == "announce" and self.speaker:
                try:
                    self.speaker.speak(str(payload), interrupt=True)
                except Exception:
                    pass
            elif event == "error":
                messagebox.showerror(
                    Localization.get("updater-error-title"),
                    str(payload),
                    parent=self.root,
                )
            elif event == "finish":
                self.root.after(COMPLETION_DISPLAY_MS, self.root.destroy)
        if self.root.winfo_exists():
            self.root.after(UI_POLL_INTERVAL_MS, self._drain_events)

    def _extraction_progress(self, progress: ExtractionProgress) -> None:
        percent = progress.percent
        self._publish("progress", percent)
        self._publish_status(
            "updater-status-extracting-progress",
            announce=False,
            percent=percent,
        )
        if percent >= self.last_beep_percent + PROGRESS_BEEP_STEP:
            self.last_beep_percent = percent
            if winsound:
                span = PROGRESS_MAX_FREQUENCY - PROGRESS_MIN_FREQUENCY
                frequency = PROGRESS_MIN_FREQUENCY + int(span * percent / 100)
                try:
                    winsound.Beep(frequency, PROGRESS_BEEP_DURATION_MS)
                except RuntimeError:
                    pass
        if percent >= self.last_announced_percent + PROGRESS_ANNOUNCEMENT_STEP:
            self.last_announced_percent = percent
            self._publish(
                "announce",
                Localization.get(
                    "updater-status-extracting-progress",
                    percent=percent,
                ),
            )

    def _wait_for_parent(self) -> bool:
        pid = self.arguments.wait_pid
        if not pid:
            return True
        self._publish_status("updater-status-waiting", pid=pid)
        try:
            process = psutil.Process(pid)
            expected_started_at = self.arguments.wait_process_started_at
            if expected_started_at is not None:
                actual_started_at = process.create_time()
                if abs(actual_started_at - expected_started_at) > 1.0:
                    return True
            process.wait(timeout=PROCESS_WAIT_TIMEOUT_SECONDS)
            return True
        except psutil.NoSuchProcess:
            return True
        except psutil.TimeoutExpired:
            self._publish(
                "error",
                Localization.get("updater-error-process-still-running"),
            )
            return False
        except (psutil.AccessDenied, OSError):
            # The directory swap remains the authoritative lock check.
            return True

    def _launch_path(self) -> Path:
        name = self.arguments.executable_name
        if not is_valid_windows_executable_name(name):
            raise UpdateInstallationError("updater-error-invalid-executable")
        return self.arguments.target_directory / name

    def _terminate_failed_process(self, process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=PROCESS_TERMINATE_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
                process.wait(timeout=PROCESS_TERMINATE_TIMEOUT_SECONDS)
            except (OSError, subprocess.TimeoutExpired):
                pass

    def _launch_and_confirm(self) -> None:
        executable = self._launch_path()
        if not executable.is_file():
            raise UpdateInstallationError(
                "updater-error-executable-missing",
                path=str(executable),
            )

        token = uuid.uuid4().hex
        ready_path = update_ready_path(token)
        ready_path.unlink(missing_ok=True)
        self._publish_status("updater-status-launching")
        process = subprocess.Popen(
            [str(executable), "--update-token", token],
            cwd=self.arguments.target_directory,
        )
        deadline = time.monotonic() + HEALTH_READY_TIMEOUT_SECONDS
        try:
            while time.monotonic() < deadline:
                if ready_path.is_file() and update_ready_marker_matches(
                    ready_path,
                    token=token,
                    process_id=process.pid,
                    client_version=self.arguments.expected_client_version,
                ):
                    stabilization_deadline = (
                        time.monotonic() + HEALTH_STABILIZATION_SECONDS
                    )
                    while time.monotonic() < stabilization_deadline:
                        if process.poll() is not None:
                            raise UpdateInstallationError(
                                "updater-error-new-version-exited"
                            )
                        time.sleep(HEALTH_POLL_SECONDS)
                    return
                if process.poll() is not None:
                    raise UpdateInstallationError("updater-error-new-version-exited")
                time.sleep(HEALTH_POLL_SECONDS)
            raise UpdateInstallationError("updater-error-health-timeout")
        except Exception:
            self._terminate_failed_process(process)
            raise
        finally:
            ready_path.unlink(missing_ok=True)

    def _relaunch_previous_version(self) -> None:
        executable = self._launch_path()
        if executable.is_file():
            subprocess.Popen([str(executable)], cwd=self.arguments.target_directory)

    def _error_text(self, error: BaseException) -> str:
        if isinstance(error, UpdateInstallationError):
            return Localization.get(error.message_id, **error.params)
        return Localization.get("updater-error-unexpected", error=str(error))

    def _run_update(self) -> None:
        transaction: PendingInstallation | None = None
        parent_exited = False
        previous_relaunched = False
        try:
            validate_windows_updater_contract(self.arguments)
            parent_exited = self._wait_for_parent()
            if not parent_exited:
                self.arguments.archive_path.unlink(missing_ok=True)
                return
            apply_directory = (
                self.arguments.extract_directory
                or self.arguments.target_directory
            )
            required_files = self.arguments.required_files
            required_text_files = {}
            if self.arguments.version_file is not None:
                required_text_files[self.arguments.version_file] = (
                    self.arguments.artifact_version
                )
            if apply_directory == self.arguments.target_directory:
                required_files = (
                    *required_files,
                    Path(self.arguments.executable_name),
                    Path(UPDATER_EXECUTABLE_NAME),
                )

            self._publish_status("updater-status-validating")
            transaction = stage_and_swap_update(
                self.arguments.archive_path,
                target_directory=self.arguments.target_directory,
                apply_directory=apply_directory,
                expected_sha256=self.arguments.expected_sha256,
                required_files=required_files,
                required_text_files=required_text_files,
                progress_callback=self._extraction_progress,
            )
            self._publish_status("updater-status-verifying-startup")
            try:
                self._launch_and_confirm()
            except Exception:
                transaction.rollback()
                transaction = None
                self._relaunch_previous_version()
                previous_relaunched = True
                raise

            transaction.commit()
            transaction = None
            self.arguments.archive_path.unlink(missing_ok=True)
            self._publish("progress", 100)
            self._publish_status("updater-status-complete")
        except Exception as error:
            if transaction is not None:
                try:
                    transaction.rollback()
                except Exception as rollback_error:
                    error = UpdateInstallationError(
                        "updater-error-rollback-failed",
                        error=self._error_text(rollback_error),
                    )
            self.arguments.archive_path.unlink(missing_ok=True)
            if parent_exited and not previous_relaunched:
                try:
                    self._relaunch_previous_version()
                except OSError:
                    pass
            self._publish("error", self._error_text(error))
        finally:
            self._publish("finish")

    def run(self) -> None:
        self.worker = threading.Thread(
            target=self._run_update,
            name="PlayAural updater",
            daemon=False,
        )
        self.worker.start()
        self.root.mainloop()
        self.worker.join()


def _locales_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "locales"
    return Path(__file__).resolve().parent / "locales"


def validate_windows_updater_contract(arguments: UpdaterArguments) -> None:
    """Reject a non-Windows or malformed ZIP/executable contract before mutation."""
    if get_client_release_platform() != WINDOWS_RELEASE_TARGET:
        raise UpdateInstallationError("updater-error-windows-only")
    if arguments.archive_path.suffix.lower() != WINDOWS_ARCHIVE_SUFFIX:
        raise UpdateInstallationError("update-release-windows-zip-required")
    if not is_valid_windows_executable_name(arguments.executable_name):
        raise UpdateInstallationError("updater-error-invalid-executable")
    if arguments.wait_pid is not None and arguments.wait_pid <= 0:
        raise UpdateInstallationError("updater-error-invalid-process")
    if not is_valid_locale_tag(arguments.locale):
        raise UpdateInstallationError("updater-error-invalid-locale")
    if not arguments.artifact_version or not arguments.expected_client_version:
        raise UpdateInstallationError("updater-error-invalid-artifact-version")


def parse_arguments(arguments: list[str] | None = None) -> UpdaterArguments:
    parser = argparse.ArgumentParser(description="PlayAural Auto-Updater")
    parser.add_argument("--zip", required=True, dest="archive_path")
    parser.add_argument("--target", required=True, dest="target_directory")
    parser.add_argument("--exe", required=True, dest="executable_name")
    parser.add_argument("--pid", type=int, dest="wait_pid")
    parser.add_argument("--process-started-at", type=float)
    parser.add_argument("--extract-dir", dest="extract_directory")
    parser.add_argument("--sha256", default="", dest="expected_sha256")
    parser.add_argument("--required-file", action="append", default=[])
    parser.add_argument("--artifact-version", required=True)
    parser.add_argument("--expected-client-version", required=True)
    parser.add_argument("--version-file")
    parser.add_argument("--locale", default=DEFAULT_LOCALE_TAG)
    parsed = parser.parse_args(arguments)
    return UpdaterArguments(
        archive_path=Path(parsed.archive_path).resolve(),
        target_directory=Path(parsed.target_directory).resolve(),
        executable_name=str(parsed.executable_name),
        wait_pid=parsed.wait_pid,
        wait_process_started_at=parsed.process_started_at,
        extract_directory=(
            Path(parsed.extract_directory).resolve()
            if parsed.extract_directory
            else None
        ),
        expected_sha256=str(parsed.expected_sha256 or ""),
        required_files=tuple(Path(value) for value in parsed.required_file),
        artifact_version=str(parsed.artifact_version or "").strip(),
        expected_client_version=str(parsed.expected_client_version or "").strip(),
        version_file=Path(parsed.version_file) if parsed.version_file else None,
        locale=str(parsed.locale or DEFAULT_LOCALE_TAG).strip(),
    )


def main(arguments: list[str] | None = None) -> None:
    parsed = parse_arguments(arguments)
    display_locale = (
        parsed.locale if is_valid_locale_tag(parsed.locale) else DEFAULT_LOCALE_TAG
    )
    Localization.init(locales_dir=_locales_directory(), locale=display_locale)
    UpdaterApp(parsed).run()


if __name__ == "__main__":
    main()
