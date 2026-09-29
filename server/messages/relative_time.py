"""Locale-neutral relative-time calculation with Fluent-owned wording."""

from __future__ import annotations

from datetime import datetime, timezone

from .localization import Localization


_MINUTE_SECONDS = 60
_HOUR_SECONDS = 60 * _MINUTE_SECONDS
_DAY_SECONDS = 24 * _HOUR_SECONDS
_WEEK_SECONDS = 7 * _DAY_SECONDS
_MONTH_SECONDS = 30 * _DAY_SECONDS
_YEAR_SECONDS = 365 * _DAY_SECONDS

_RELATIVE_TIME_UNITS = (
    (_YEAR_SECONDS, "relative-time-years-ago"),
    (_MONTH_SECONDS, "relative-time-months-ago"),
    (_WEEK_SECONDS, "relative-time-weeks-ago"),
    (_DAY_SECONDS, "relative-time-days-ago"),
    (_HOUR_SECONDS, "relative-time-hours-ago"),
    (_MINUTE_SECONDS, "relative-time-minutes-ago"),
)


def parse_persisted_datetime(value: object) -> datetime | None:
    """Parse a stored timestamp into UTC, including legacy local-naive values."""
    if isinstance(value, datetime):
        parsed = value
    else:
        raw = str(value or "").strip()
        if not raw:
            return None
        try:
            parsed = datetime.fromisoformat(raw)
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        # Historical account timestamps were written with datetime.now().
        # Interpret them in the server's local zone before normalizing to UTC.
        return parsed.astimezone(timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalized_past_datetime(
    value: object,
    *,
    now: datetime | None = None,
) -> datetime | None:
    """Return a valid UTC timestamp, clamped against future clock skew."""
    parsed = parse_persisted_datetime(value)
    if parsed is None:
        return None
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    else:
        reference = reference.astimezone(timezone.utc)
    return min(parsed, reference)


def format_relative_time(
    locale: str,
    value: object,
    *,
    now: datetime | None = None,
) -> str | None:
    """Format a persisted time as a localized, coarse elapsed duration."""
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    else:
        reference = reference.astimezone(timezone.utc)
    parsed = normalized_past_datetime(value, now=reference)
    if parsed is None:
        return None

    elapsed_seconds = max(0, int((reference - parsed).total_seconds()))
    for unit_seconds, localization_key in _RELATIVE_TIME_UNITS:
        if elapsed_seconds >= unit_seconds:
            return Localization.get(
                locale,
                localization_key,
                count=max(1, elapsed_seconds // unit_seconds),
            )
    return Localization.get(locale, "relative-time-just-now")


__all__ = [
    "format_relative_time",
    "normalized_past_datetime",
    "parse_persisted_datetime",
]
