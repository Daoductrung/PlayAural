"""Scope-aware runtime chat throttling with conservative spam escalation."""

import math
import time
import unicodedata
from dataclasses import dataclass
from typing import Literal


ChatScope = Literal["global", "table", "direct"]
ChatRejectionKind = Literal["rate_limited", "repeated_message"]


@dataclass(frozen=True)
class ChatRateLimitPolicy:
    """One channel scope's burst, sustained, and escalation limits."""

    capacity: int
    refill_per_second: float
    sustained_limit: int
    duplicate_limit: int
    short_duplicate_limit: int
    report_incident_threshold: int | None


@dataclass(frozen=True)
class ChatRateLimitRejection:
    """Structured explanation and review evidence for one rejected attempt."""

    kind: ChatRejectionKind
    scope: ChatScope
    seconds: int
    incident_count: int
    rejected_attempt_count: int
    accepted_message_count: int
    report_recommended: bool


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
    """Reject spam-shaped sends without applying automated account penalties.

    Buckets are isolated by immutable account ID and chat scope, so activity at
    a table cannot consume global-chat capacity. Repeated rejected attempts are
    coalesced into incidents before a review-only report is recommended. State
    remains runtime-only, survives ordinary reconnects, and is removed when an
    account is deleted.
    """

    GLOBAL_POLICY = ChatRateLimitPolicy(
        capacity=5,
        refill_per_second=0.5,
        sustained_limit=15,
        duplicate_limit=2,
        short_duplicate_limit=5,
        report_incident_threshold=3,
    )
    TABLE_POLICY = ChatRateLimitPolicy(
        capacity=20,
        refill_per_second=5.0,
        sustained_limit=120,
        duplicate_limit=8,
        short_duplicate_limit=15,
        report_incident_threshold=6,
    )
    DIRECT_POLICY = ChatRateLimitPolicy(
        capacity=8,
        refill_per_second=1.0,
        sustained_limit=30,
        duplicate_limit=4,
        short_duplicate_limit=8,
        report_incident_threshold=None,
    )
    POLICIES: dict[ChatScope, ChatRateLimitPolicy] = {
        "global": GLOBAL_POLICY,
        "table": TABLE_POLICY,
        "direct": DIRECT_POLICY,
    }

    SUSTAINED_WINDOW_SECONDS = 60.0
    DUPLICATE_WINDOW_SECONDS = 30.0
    SHORT_MESSAGE_MAX_CHARACTERS = 4
    INCIDENT_WINDOW_SECONDS = 10 * 60.0
    INCIDENT_COALESCE_SECONDS = 10.0
    MAX_REJECTED_ATTEMPTS_TRACKED = 1_000
    REPORT_FAILURE_RETRY_SECONDS = 60.0
    IDLE_RETENTION_SECONDS = 10 * 60.0
    PRUNE_INTERVAL_SECONDS = 60.0

    def __init__(self) -> None:
        self._buckets: dict[tuple[str, ChatScope], _ScopeBucket] = {}
        self._last_prune = time.monotonic()

    @classmethod
    def _policy(cls, scope: ChatScope) -> ChatRateLimitPolicy:
        try:
            return cls.POLICIES[scope]
        except KeyError as exc:
            raise ValueError("Unsupported chat rate-limit scope") from exc

    @classmethod
    def _prune_bucket(cls, bucket: "_ScopeBucket", now: float) -> None:
        message_cutoff = now - cls.SUSTAINED_WINDOW_SECONDS
        bucket.recent_messages = [
            entry for entry in bucket.recent_messages if entry[0] > message_cutoff
        ]
        incident_cutoff = now - cls.INCIDENT_WINDOW_SECONDS
        bucket.incidents = [
            occurred_at
            for occurred_at in bucket.incidents
            if occurred_at > incident_cutoff
        ]
        bucket.recent_rejections = [
            occurred_at
            for occurred_at in bucket.recent_rejections
            if occurred_at > incident_cutoff
        ]

    def _prune_inactive(self, now: float) -> None:
        """Bound runtime state without making reconnect a limiter bypass."""
        if now - self._last_prune < self.PRUNE_INTERVAL_SECONDS:
            return
        self._last_prune = now
        for key, bucket in list(self._buckets.items()):
            self._prune_bucket(bucket, now)
            if (
                not bucket.recent_messages
                and not bucket.incidents
                and not bucket.recent_rejections
                and now >= bucket.report_suppressed_until
                and now - bucket.last_activity > self.IDLE_RETENTION_SECONDS
            ):
                self._buckets.pop(key, None)

    @staticmethod
    def _account_id(account_id: str) -> str:
        normalized_id = str(account_id or "").strip()
        if not normalized_id:
            raise ValueError("Chat rate limiting requires an account identity")
        return normalized_id

    def get_bucket(
        self,
        account_id: str,
        scope: ChatScope,
    ) -> "_ScopeBucket":
        """Get or create runtime state for one account and channel scope."""
        normalized_id = self._account_id(account_id)
        policy = self._policy(scope)
        now = time.monotonic()
        self._prune_inactive(now)
        key = (normalized_id, scope)
        if key not in self._buckets:
            self._buckets[key] = _ScopeBucket(policy.capacity)
        bucket = self._buckets[key]
        bucket.last_activity = max(bucket.last_activity, now)
        return bucket

    def _record_violation(
        self,
        bucket: "_ScopeBucket",
        policy: ChatRateLimitPolicy,
        scope: ChatScope,
        kind: ChatRejectionKind,
        now: float,
    ) -> ChatRateLimitRejection:
        bucket.recent_rejections.append(now)
        if len(bucket.recent_rejections) > self.MAX_REJECTED_ATTEMPTS_TRACKED:
            del bucket.recent_rejections[
                : -self.MAX_REJECTED_ATTEMPTS_TRACKED
            ]
        if (
            not bucket.incidents
            or now - bucket.incidents[-1] >= self.INCIDENT_COALESCE_SECONDS
        ):
            bucket.incidents.append(now)
        threshold = policy.report_incident_threshold
        report_recommended = bool(
            threshold is not None
            and len(bucket.incidents) >= threshold
            and now >= bucket.report_suppressed_until
        )
        retry_seconds = max(
            1,
            math.ceil((1.0 - bucket.tokens) / policy.refill_per_second),
        )
        return ChatRateLimitRejection(
            kind=kind,
            scope=scope,
            seconds=retry_seconds,
            incident_count=len(bucket.incidents),
            rejected_attempt_count=len(bucket.recent_rejections),
            accepted_message_count=len(bucket.recent_messages),
            report_recommended=report_recommended,
        )

    def try_consume(
        self,
        account_id: str,
        message: str,
        *,
        scope: ChatScope,
    ) -> tuple[bool, ChatRateLimitRejection | None]:
        """Consume capacity for one otherwise-sendable chat message."""
        if not isinstance(message, str):
            raise ValueError("Chat rate limiting requires message text")
        fingerprint = normalize_chat_content(message)
        if not fingerprint:
            raise ValueError("Chat rate limiting requires message text")
        policy = self._policy(scope)
        bucket = self.get_bucket(account_id, scope)
        now = time.monotonic()
        self._prune_bucket(bucket, now)

        if now >= bucket.last_refill:
            elapsed = now - bucket.last_refill
            bucket.tokens = min(
                policy.capacity,
                bucket.tokens + elapsed * policy.refill_per_second,
            )
            bucket.last_refill = now

        duplicate_cutoff = now - self.DUPLICATE_WINDOW_SECONDS
        duplicate_count = sum(
            1
            for sent_at, prior_fingerprint in bucket.recent_messages
            if sent_at > duplicate_cutoff and prior_fingerprint == fingerprint
        )
        duplicate_limit = (
            policy.short_duplicate_limit
            if len(fingerprint) <= self.SHORT_MESSAGE_MAX_CHARACTERS
            else policy.duplicate_limit
        )
        if duplicate_count >= duplicate_limit:
            return False, self._record_violation(
                bucket, policy, scope, "repeated_message", now
            )
        if len(bucket.recent_messages) >= policy.sustained_limit:
            return False, self._record_violation(
                bucket, policy, scope, "rate_limited", now
            )

        if bucket.tokens < 1.0:
            return False, self._record_violation(
                bucket, policy, scope, "rate_limited", now
            )

        bucket.tokens -= 1.0
        bucket.recent_messages.append((now, fingerprint))
        return True, None

    def suppress_report(
        self,
        account_id: str,
        scope: ChatScope,
        seconds: float,
    ) -> None:
        """Suppress duplicate escalation after persistence or a write failure."""
        bucket = self.get_bucket(account_id, scope)
        now = time.monotonic()
        bucket.report_suppressed_until = max(
            bucket.report_suppressed_until,
            now + max(0.0, float(seconds)),
        )

    def remove_user(self, account_id: str) -> None:
        """Remove every scope bucket when an account is permanently deleted."""
        normalized_id = str(account_id or "").strip()
        for key in tuple(self._buckets):
            if key[0] == normalized_id:
                self._buckets.pop(key, None)


class _ScopeBucket:
    """Bounded runtime state for one account and channel scope."""

    __slots__ = (
        "tokens",
        "last_refill",
        "last_activity",
        "recent_messages",
        "incidents",
        "recent_rejections",
        "report_suppressed_until",
    )

    def __init__(self, capacity: float):
        now = time.monotonic()
        self.tokens: float = capacity
        self.last_refill: float = now
        self.last_activity: float = now
        self.recent_messages: list[tuple[float, str]] = []
        self.incidents: list[float] = []
        self.recent_rejections: list[float] = []
        self.report_suppressed_until = 0.0
