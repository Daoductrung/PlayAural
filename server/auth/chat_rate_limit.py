"""Bounded account chat limiter with escalation and repetition detection."""

import math
import time
import unicodedata
from dataclasses import dataclass
from typing import Literal


ChatRejectionKind = Literal[
    "rate_limited",
    "repeated_message",
    "auto_muted",
    "auto_mute_applied",
]


@dataclass(frozen=True)
class ChatRateLimitRejection:
    """Structured explanation for one rejected chat attempt."""

    kind: ChatRejectionKind
    seconds: int = 0


def normalize_chat_content(message: str) -> str:
    """Normalize text for bounded duplicate detection, not for display."""
    normalized = unicodedata.normalize("NFKC", str(message)).casefold()
    safe_characters = "".join(
        " "
        if character.isspace()
        else character
        if not unicodedata.category(character).startswith("C")
        else ""
        for character in normalized
    )
    return " ".join(safe_characters.split())


class ChatRateLimiter:
    """Limit bursts, sustained floods, and repeated messages per account ID.

    State intentionally remains runtime-only, survives ordinary reconnects, and
    is explicitly removed only when the account is deleted. A token bucket
    protects short bursts, a bounded sliding window caps sustained throughput,
    and normalized duplicate detection rejects the third matching message in a
    short interval. Rejections share one strike escalation path.
    """

    BUCKET_CAPACITY = 5
    REFILL_RATE = 0.5

    SUSTAINED_WINDOW_SECONDS = 60.0
    SUSTAINED_MESSAGE_LIMIT = 20
    DUPLICATE_WINDOW_SECONDS = 30.0
    DUPLICATE_MESSAGE_LIMIT = 2

    STRIKE_WARN_THRESHOLD = 4
    ADMIN_NOTIFY_STRIKE_THRESHOLD = 6
    STRIKE_DECAY_INTERVAL = 60.0

    AUTO_MUTE_DURATIONS = {
        4: 30,
        5: 120,
    }
    AUTO_MUTE_SEVERE = 300
    IDLE_RETENTION_SECONDS = 600.0
    PRUNE_INTERVAL_SECONDS = 60.0

    def __init__(self) -> None:
        self._buckets: dict[str, _UserBucket] = {}
        self._last_prune = time.monotonic()

    @classmethod
    def _prune_recent_messages(cls, bucket: "_UserBucket", now: float) -> None:
        cutoff = now - cls.SUSTAINED_WINDOW_SECONDS
        bucket.recent_messages = [
            entry for entry in bucket.recent_messages if entry[0] > cutoff
        ]

    @classmethod
    def _decay_strikes(cls, bucket: "_UserBucket", now: float) -> None:
        if bucket.strikes <= 0 or bucket.last_strike_time is None:
            return
        decay_elapsed = max(0.0, now - bucket.last_strike_time)
        decay_count = int(decay_elapsed / cls.STRIKE_DECAY_INTERVAL)
        if decay_count <= 0:
            return
        bucket.strikes = max(0, bucket.strikes - decay_count)
        if bucket.strikes == 0:
            bucket.last_strike_time = None
        else:
            bucket.last_strike_time += decay_count * cls.STRIKE_DECAY_INTERVAL
        if bucket.strikes < cls.ADMIN_NOTIFY_STRIKE_THRESHOLD:
            bucket.admin_notified = False

    def _prune_inactive(self, now: float) -> None:
        """Bound runtime state without making reconnect a limiter bypass."""
        if now - self._last_prune < self.PRUNE_INTERVAL_SECONDS:
            return
        self._last_prune = now
        for account_id, bucket in list(self._buckets.items()):
            if bucket.muted_until is not None and now >= bucket.muted_until:
                bucket.muted_until = None
            self._decay_strikes(bucket, now)
            self._prune_recent_messages(bucket, now)
            if (
                bucket.muted_until is None
                and bucket.strikes == 0
                and not bucket.recent_messages
                and now - bucket.last_activity > self.IDLE_RETENTION_SECONDS
            ):
                self._buckets.pop(account_id, None)

    def get_bucket(self, account_id: str) -> "_UserBucket":
        """Get or create the runtime bucket for one immutable account ID."""
        normalized_id = str(account_id or "").strip()
        if not normalized_id:
            raise ValueError("Chat rate limiting requires an account identity")
        now = time.monotonic()
        self._prune_inactive(now)
        if normalized_id not in self._buckets:
            self._buckets[normalized_id] = _UserBucket(self.BUCKET_CAPACITY)
        bucket = self._buckets[normalized_id]
        bucket.last_activity = max(bucket.last_activity, now)
        return bucket

    def _record_violation(
        self,
        bucket: "_UserBucket",
        now: float,
        kind: Literal["rate_limited", "repeated_message"],
    ) -> ChatRateLimitRejection:
        bucket.strikes += 1
        bucket.last_strike_time = now
        if bucket.strikes < self.STRIKE_WARN_THRESHOLD:
            return ChatRateLimitRejection(kind)

        duration = self.AUTO_MUTE_DURATIONS.get(
            bucket.strikes, self.AUTO_MUTE_SEVERE
        )
        bucket.muted_until = now + duration
        # A forced-silence interval is not evidence of clean behavior. Strike
        # decay starts only after the user can chat again.
        bucket.last_strike_time = bucket.muted_until
        return ChatRateLimitRejection("auto_mute_applied", seconds=duration)

    def try_consume(
        self, account_id: str, message: str | None = None
    ) -> tuple[bool, ChatRateLimitRejection | None]:
        """Consume capacity for one otherwise-sendable chat message."""
        bucket = self.get_bucket(account_id)
        now = time.monotonic()

        if bucket.muted_until is not None:
            if now < bucket.muted_until:
                return False, ChatRateLimitRejection(
                    "auto_muted",
                    seconds=max(1, math.ceil(bucket.muted_until - now)),
                )
            bucket.muted_until = None

        if now >= bucket.last_refill:
            elapsed = now - bucket.last_refill
            bucket.tokens = min(
                self.BUCKET_CAPACITY,
                bucket.tokens + elapsed * self.REFILL_RATE,
            )
            bucket.last_refill = now
        self._decay_strikes(bucket, now)
        self._prune_recent_messages(bucket, now)

        fingerprint = None
        if message is not None:
            fingerprint = normalize_chat_content(message)
            duplicate_cutoff = now - self.DUPLICATE_WINDOW_SECONDS
            duplicate_count = sum(
                1
                for sent_at, prior_fingerprint in bucket.recent_messages
                if sent_at > duplicate_cutoff
                and prior_fingerprint == fingerprint
            )
            if fingerprint and duplicate_count >= self.DUPLICATE_MESSAGE_LIMIT:
                return False, self._record_violation(
                    bucket, now, "repeated_message"
                )
            if len(bucket.recent_messages) >= self.SUSTAINED_MESSAGE_LIMIT:
                return False, self._record_violation(
                    bucket, now, "rate_limited"
                )

        if bucket.tokens < 1.0:
            return False, self._record_violation(
                bucket, now, "rate_limited"
            )

        bucket.tokens -= 1.0
        if fingerprint:
            bucket.recent_messages.append((now, fingerprint))
        return True, None

    def is_muted(self, account_id: str) -> tuple[bool, int]:
        """Return the active auto-mute state without creating a new bucket."""
        now = time.monotonic()
        self._prune_inactive(now)
        bucket = self._buckets.get(str(account_id or "").strip())
        if bucket is None:
            return False, 0
        bucket.last_activity = max(bucket.last_activity, now)
        if bucket.muted_until is None:
            return False, 0
        if now >= bucket.muted_until:
            bucket.muted_until = None
            return False, 0
        return True, max(1, math.ceil(bucket.muted_until - now))

    def should_notify_admins(self, account_id: str) -> bool:
        """Return whether severe spam needs its one current admin alert."""
        bucket = self._buckets.get(str(account_id or "").strip())
        return bool(
            bucket
            and bucket.strikes >= self.ADMIN_NOTIFY_STRIKE_THRESHOLD
            and not bucket.admin_notified
        )

    def mark_admin_notified(self, account_id: str) -> None:
        """Mark the current severe-spam escalation as announced."""
        bucket = self._buckets.get(str(account_id or "").strip())
        if bucket:
            bucket.admin_notified = True

    def remove_user(self, account_id: str) -> None:
        """Remove limiter state when its account is permanently deleted."""
        self._buckets.pop(str(account_id or "").strip(), None)


class _UserBucket:
    """Bounded runtime state for one immutable account ID."""

    __slots__ = (
        "tokens",
        "last_refill",
        "strikes",
        "last_strike_time",
        "muted_until",
        "admin_notified",
        "last_activity",
        "recent_messages",
    )

    def __init__(self, capacity: float):
        now = time.monotonic()
        self.tokens: float = capacity
        self.last_refill: float = now
        self.strikes: int = 0
        self.last_strike_time: float | None = None
        self.muted_until: float | None = None
        self.admin_notified: bool = False
        self.last_activity: float = now
        self.recent_messages: list[tuple[float, str]] = []
