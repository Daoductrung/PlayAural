"""Server reboot and shutdown scheduling."""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from time import monotonic
from typing import TYPE_CHECKING

from ..messages.localization import Localization
from ..messages.localized_content import localized_text_for_locale

if TYPE_CHECKING:
    from ..users.network_user import NetworkUser
    from .server import Server


POWER_REBOOT_EXIT_CODE = 75
POWER_CHECKPOINT_TTL_DAYS = 1
POWER_RESTORE_GRACE_SECONDS = 180
POWER_MAX_CUSTOM_DELAY_MINUTES = 24 * 60

logger = logging.getLogger(__name__)


class PowerAction(str, Enum):
    """The server-level power action requested by an administrator."""

    REBOOT = "reboot"
    SHUTDOWN = "shutdown"


@dataclass(frozen=True)
class ScheduledPowerOperation:
    """Runtime-only server power operation state."""

    operation_id: str
    action: PowerAction
    delay_seconds: int
    requested_by: str
    reason_id: str
    custom_reasons: dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def preserves_tables(self) -> bool:
        return self.action == PowerAction.REBOOT


class ServerPowerManager:
    """Coordinates safe scheduled reboot and shutdown transitions."""

    def __init__(self, server: "Server") -> None:
        self.server = server
        self._task: asyncio.Task | None = None
        self._operation: ScheduledPowerOperation | None = None
        self._finalizing = False

    @property
    def active_operation(self) -> ScheduledPowerOperation | None:
        return self._operation

    @property
    def is_scheduled(self) -> bool:
        return self._task is not None and not self._task.done()

    @property
    def is_finalizing(self) -> bool:
        return self._finalizing

    def schedule(
        self,
        *,
        action: PowerAction,
        delay_seconds: int,
        requested_by: str,
        reason_id: str,
        custom_reasons: dict[str, str] | None = None,
    ) -> ScheduledPowerOperation:
        """Schedule a power transition and start its countdown task."""
        if self.is_scheduled:
            raise RuntimeError("A server power operation is already scheduled.")

        safe_delay = max(10, int(delay_seconds))
        operation = ScheduledPowerOperation(
            operation_id=uuid.uuid4().hex,
            action=action,
            delay_seconds=safe_delay,
            requested_by=requested_by,
            reason_id=reason_id,
            custom_reasons=dict(custom_reasons or {}),
        )
        self._operation = operation
        self._task = asyncio.create_task(self._run(operation))
        return operation

    def cancel(self) -> bool:
        """Cancel the active scheduled operation if it has not finalized."""
        if not self.is_scheduled or self._finalizing:
            return False
        assert self._task is not None
        self._task.cancel()
        self._task = None
        self._operation = None
        return True

    def cancel_for_stop(self) -> None:
        """Cancel a non-finalizing schedule because the server is stopping."""
        if self._finalizing:
            return
        self.cancel()

    async def _run(self, operation: ScheduledPowerOperation) -> None:
        try:
            await self._run_countdown(operation)
            self._finalizing = True
            await self.server._finalize_power_operation(operation)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Server power operation failed during finalization.")
            self._finalizing = False
            await self.broadcast_failed(operation)
        finally:
            if not self._finalizing:
                self._operation = None
                self._task = None

    async def _run_countdown(self, operation: ScheduledPowerOperation) -> None:
        end_at = monotonic() + operation.delay_seconds
        for point in self._announcement_points(operation.delay_seconds):
            sleep_for = end_at - point - monotonic()
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            await self.broadcast_countdown(operation, point)
        sleep_for = end_at - monotonic()
        if sleep_for > 0:
            await asyncio.sleep(sleep_for)

    @staticmethod
    def _announcement_points(total_seconds: int) -> list[int]:
        """Return descending remaining-second marks for player announcements."""
        total_seconds = max(1, int(total_seconds))
        points: set[int] = {total_seconds}

        if total_seconds > 600:
            highest_half_hour = (total_seconds - 1) // 1800 * 1800
            for point in range(highest_half_hour, 600, -1800):
                points.add(point)

        for point in (600, 300, 60, 30):
            if total_seconds >= point:
                points.add(point)
        for point in range(10, 0, -1):
            if total_seconds >= point:
                points.add(point)

        return sorted(points, reverse=True)

    async def broadcast_countdown(
        self, operation: ScheduledPowerOperation, seconds_remaining: int
    ) -> None:
        """Broadcast one scheduled countdown announcement to approved users."""
        if seconds_remaining <= 10:
            sound = "server_alert_tick.ogg"
        else:
            sound = "server_alert_warning.ogg"

        sends = []
        for user in list(self.server.users.values()):
            if not user.approved:
                continue
            if seconds_remaining <= 10:
                text = str(seconds_remaining)
                speak_text = text
            else:
                text = self.format_warning(user.locale, operation, seconds_remaining)
                speak_text = text
            sends.extend(self._announcement_packets(user, text, sound, speak_text))
        if sends:
            await asyncio.gather(*sends, return_exceptions=True)

    async def broadcast_cancelled(
        self, cancelled_by: "NetworkUser", operation: ScheduledPowerOperation
    ) -> None:
        """Tell players that a scheduled action was cancelled."""
        sends = []
        for user in list(self.server.users.values()):
            if not user.approved:
                continue
            text = Localization.get(
                user.locale,
                "server-power-cancelled-broadcast",
                action=self.format_action(user.locale, operation.action),
                admin=cancelled_by.username,
            )
            sends.extend(self._announcement_packets(user, text, "notify.ogg", text))
        if sends:
            await asyncio.gather(*sends, return_exceptions=True)

    async def broadcast_final(self, operation: ScheduledPowerOperation) -> None:
        """Send final power-transition messages and reconnect instructions."""
        key = (
            "server-power-reboot-now"
            if operation.action == PowerAction.REBOOT
            else "server-power-shutdown-now"
        )
        sends = []
        for user in list(self.server.users.values()):
            if not user.approved:
                continue
            text = Localization.get(
                user.locale,
                key,
                reason=self.format_reason(user.locale, operation),
            )
            sends.extend(
                self._announcement_packets(
                    user,
                    text,
                    "server_alert_shutdown.ogg",
                    text,
                    disconnect=True,
                    reconnect=operation.action == PowerAction.REBOOT,
                )
            )
        if sends:
            await asyncio.gather(*sends, return_exceptions=True)

    async def broadcast_failed(self, operation: ScheduledPowerOperation) -> None:
        """Tell players that a scheduled power action could not complete."""
        sends = []
        for user in list(self.server.users.values()):
            if not user.approved:
                continue
            text = Localization.get(
                user.locale,
                "server-power-finalize-failed",
                action=self.format_action(user.locale, operation.action),
            )
            sends.extend(
                self._announcement_packets(
                    user,
                    text,
                    "error.ogg",
                    text,
                )
            )
        if sends:
            await asyncio.gather(*sends, return_exceptions=True)

    def _announcement_packets(
        self,
        user: "NetworkUser",
        text: str,
        sound: str,
        speak_text: str,
        *,
        disconnect: bool = False,
        reconnect: bool = False,
    ) -> list[asyncio.Future]:
        sys_name = Localization.get(user.locale, "system-name")
        packets: list[dict] = [
            {
                "type": "chat",
                "convo": "announcement",
                "sender": sys_name,
                "message": text,
                "silent": True,
            },
            {"type": "speak", "text": speak_text, "buffer": "system"},
            {
                "type": "play_sound",
                "name": sound,
                "volume": 100,
                "pan": 0,
                "pitch": 100,
            },
        ]
        if disconnect:
            packets.append(
                {
                    "type": "disconnect",
                    "reason": text,
                    "reconnect": reconnect,
                    "reconnect_after_ms": 3000 if reconnect else 0,
                    "reconnect_window_ms": 30000 if reconnect else 0,
                }
            )
        return [asyncio.create_task(user.connection.send(packet)) for packet in packets]

    def format_warning(
        self,
        locale: str,
        operation: ScheduledPowerOperation,
        seconds_remaining: int,
    ) -> str:
        key = (
            "server-power-reboot-warning"
            if operation.action == PowerAction.REBOOT
            else "server-power-shutdown-warning"
        )
        return Localization.get(
            locale,
            key,
            duration=self.format_duration(locale, seconds_remaining),
            reason=self.format_reason(locale, operation),
        )

    def format_action(self, locale: str, action: PowerAction) -> str:
        return Localization.get(locale, f"server-power-action-{action.value}")

    def format_reason(
        self, locale: str, operation: ScheduledPowerOperation
    ) -> str:
        if operation.reason_id == "custom":
            return self._custom_reason_for_locale(locale, operation.custom_reasons)
        return Localization.get(
            locale,
            f"server-power-reason-{operation.reason_id}",
        )

    @staticmethod
    def _custom_reason_for_locale(locale: str, translations: dict[str, str]) -> str:
        return localized_text_for_locale(
            locale,
            translations,
            default=Localization.get(locale, "server-power-reason-unspecified"),
        )

    @staticmethod
    def format_duration(locale: str, seconds: int) -> str:
        seconds = max(1, int(seconds))
        if seconds < 60:
            return Localization.get(locale, "duration-seconds", count=seconds)

        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if minutes < 60:
            if remaining_seconds:
                return Localization.get(
                    locale,
                    "duration-minutes-seconds",
                    minutes=minutes,
                    seconds=remaining_seconds,
                )
            return Localization.get(locale, "duration-minutes", count=minutes)

        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes:
            return Localization.get(
                locale,
                "duration-hours-minutes",
                hours=hours,
                minutes=remaining_minutes,
            )
        return Localization.get(locale, "duration-hours", count=hours)

    @staticmethod
    def checkpoint_expires_at() -> str:
        return (datetime.now() + timedelta(days=POWER_CHECKPOINT_TTL_DAYS)).isoformat()

    @staticmethod
    def seconds_from_custom_minutes(value: str) -> int | None:
        try:
            minutes = int(str(value).strip())
        except (TypeError, ValueError):
            return None
        if not 1 <= minutes <= POWER_MAX_CUSTOM_DELAY_MINUTES:
            return None
        return minutes * 60
