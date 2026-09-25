"""Validated filters for persistent global-chat moderation history."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone

from ..chat_channels import normalize_global_chat_channel


GLOBAL_CHAT_HISTORY_SORT_ORDERS = ("newest", "oldest")
GLOBAL_CHAT_HISTORY_PERIODS = (
    "all",
    "today",
    "yesterday",
    "last_7_days",
    "last_30_days",
    "current_month",
    "previous_month",
)


@dataclass(frozen=True, slots=True)
class GlobalChatHistoryFilter:
    """One normalized, non-persistent moderation message query."""

    channel_code: str | None = None
    period: str = "all"
    sort_order: str = "newest"

    @classmethod
    def from_values(
        cls,
        *,
        channel_code: object = None,
        period: object = "all",
        sort_order: object = "newest",
    ) -> "GlobalChatHistoryFilter":
        """Normalize restored or client-derived filter values without failing."""
        normalized_channel = normalize_global_chat_channel(channel_code)
        normalized_period = str(period or "all")
        if normalized_period not in GLOBAL_CHAT_HISTORY_PERIODS:
            normalized_period = "all"
        normalized_sort = str(sort_order or "newest")
        if normalized_sort not in GLOBAL_CHAT_HISTORY_SORT_ORDERS:
            normalized_sort = "newest"
        return cls(
            channel_code=normalized_channel,
            period=normalized_period,
            sort_order=normalized_sort,
        )

    @property
    def is_default(self) -> bool:
        return (
            self.channel_code is None
            and self.period == "all"
            and self.sort_order == "newest"
        )

    def utc_bounds(
        self,
        *,
        now: datetime | None = None,
    ) -> tuple[datetime | None, datetime | None]:
        """Return an inclusive start and exclusive end for the selected period."""
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("Global-chat history time requires a timezone")
        current = current.astimezone(timezone.utc)
        today = datetime.combine(current.date(), time.min, tzinfo=timezone.utc)

        if self.period == "all":
            return None, None
        if self.period == "today":
            return today, today + timedelta(days=1)
        if self.period == "yesterday":
            return today - timedelta(days=1), today
        if self.period == "last_7_days":
            return current - timedelta(days=7), current
        if self.period == "last_30_days":
            return current - timedelta(days=30), current

        current_month = today.replace(day=1)
        if current_month.month == 12:
            next_month = current_month.replace(
                year=current_month.year + 1,
                month=1,
            )
        else:
            next_month = current_month.replace(month=current_month.month + 1)
        if self.period == "current_month":
            return current_month, next_month

        previous_month_end = current_month
        previous_month_start = (current_month - timedelta(days=1)).replace(day=1)
        return previous_month_start, previous_month_end
