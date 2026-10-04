"""Runtime throttling for disruptive table interactions."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Iterable


class TableInteractionScope(StrEnum):
    """Independent interaction classes with distinct UX and abuse costs."""

    ROLE_CHANGE = "role_change"
    VOICE_MODERATION = "voice_moderation"
    INVITE_SENDER = "invite_sender"
    INVITE_PAIR = "invite_pair"


@dataclass(frozen=True)
class TableInteractionPolicy:
    """Token-bucket policy for one interaction class."""

    capacity: int
    refill_seconds: float


@dataclass(frozen=True)
class TableInteractionKey:
    """Immutable-account scope for one runtime bucket."""

    account_id: str
    scope: TableInteractionScope
    table_id: str = ""
    related_account_id: str = ""


@dataclass(frozen=True)
class TableInteractionRejection:
    """Structured rejection suitable for localized caller feedback."""

    scope: TableInteractionScope
    seconds: int


class TableInteractionRateLimiter:
    """Bound noisy table actions without making reconnect a bypass.

    State is deliberately runtime-only. Keys use immutable account IDs, and
    multi-bucket operations are atomic so a rejected pair cooldown does not
    consume a sender-wide invitation token.
    """

    ROLE_CHANGE_POLICY = TableInteractionPolicy(capacity=2, refill_seconds=15.0)
    VOICE_MODERATION_POLICY = TableInteractionPolicy(
        capacity=3,
        refill_seconds=10.0,
    )
    INVITE_SENDER_POLICY = TableInteractionPolicy(capacity=3, refill_seconds=20.0)
    INVITE_PAIR_POLICY = TableInteractionPolicy(capacity=1, refill_seconds=60.0)
    POLICIES: dict[TableInteractionScope, TableInteractionPolicy] = {
        TableInteractionScope.ROLE_CHANGE: ROLE_CHANGE_POLICY,
        TableInteractionScope.VOICE_MODERATION: VOICE_MODERATION_POLICY,
        TableInteractionScope.INVITE_SENDER: INVITE_SENDER_POLICY,
        TableInteractionScope.INVITE_PAIR: INVITE_PAIR_POLICY,
    }

    IDLE_RETENTION_SECONDS = 10 * 60.0
    PRUNE_INTERVAL_SECONDS = 60.0

    def __init__(self, *, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._buckets: dict[TableInteractionKey, _Bucket] = {}
        self._last_prune = clock()

    @classmethod
    def role_change_key(
        cls,
        account_id: str,
        table_id: str,
    ) -> TableInteractionKey:
        return TableInteractionKey(
            account_id=account_id,
            scope=TableInteractionScope.ROLE_CHANGE,
            table_id=table_id,
        )

    @classmethod
    def invite_keys(
        cls,
        sender_account_id: str,
        invitee_account_id: str,
    ) -> tuple[TableInteractionKey, TableInteractionKey]:
        return (
            TableInteractionKey(
                account_id=sender_account_id,
                scope=TableInteractionScope.INVITE_PAIR,
                related_account_id=invitee_account_id,
            ),
            TableInteractionKey(
                account_id=sender_account_id,
                scope=TableInteractionScope.INVITE_SENDER,
            ),
        )

    @classmethod
    def voice_moderation_key(
        cls,
        account_id: str,
        table_id: str,
    ) -> TableInteractionKey:
        return TableInteractionKey(
            account_id=account_id,
            scope=TableInteractionScope.VOICE_MODERATION,
            table_id=table_id,
        )

    @classmethod
    def _policy(cls, scope: TableInteractionScope) -> TableInteractionPolicy:
        try:
            return cls.POLICIES[scope]
        except KeyError as exc:
            raise ValueError("Unsupported table interaction scope") from exc

    @staticmethod
    def _normalize_key(key: TableInteractionKey) -> TableInteractionKey:
        account_id = str(key.account_id or "").strip()
        table_id = str(key.table_id or "").strip()
        related_account_id = str(key.related_account_id or "").strip()
        if not account_id:
            raise ValueError("Table interaction rate limiting requires an account ID")
        if key.scope in {
            TableInteractionScope.ROLE_CHANGE,
            TableInteractionScope.VOICE_MODERATION,
        } and not table_id:
            raise ValueError("Table-scoped rate limiting requires a table ID")
        if key.scope is TableInteractionScope.INVITE_PAIR and not related_account_id:
            raise ValueError("Pair invitation rate limiting requires an invitee account ID")
        return TableInteractionKey(
            account_id=account_id,
            scope=key.scope,
            table_id=table_id,
            related_account_id=related_account_id,
        )

    def _prune_inactive(self, now: float) -> None:
        if now - self._last_prune < self.PRUNE_INTERVAL_SECONDS:
            return
        self._last_prune = now
        for key, bucket in list(self._buckets.items()):
            if now - bucket.last_activity > self.IDLE_RETENTION_SECONDS:
                self._buckets.pop(key, None)

    def _get_bucket(
        self,
        key: TableInteractionKey,
        now: float,
    ) -> tuple[TableInteractionKey, "_Bucket", TableInteractionPolicy]:
        policy = self._policy(key.scope)
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(float(policy.capacity), now)
            self._buckets[key] = bucket
        else:
            elapsed = max(0.0, now - bucket.last_refill)
            bucket.tokens = min(
                float(policy.capacity),
                bucket.tokens + elapsed / policy.refill_seconds,
            )
            bucket.last_refill = now
        bucket.last_activity = now
        return key, bucket, policy

    @staticmethod
    def _retry_seconds(
        bucket: "_Bucket",
        policy: TableInteractionPolicy,
        tokens: int,
    ) -> int:
        return max(1, math.ceil((tokens - bucket.tokens) * policy.refill_seconds))

    def check(
        self,
        keys: Iterable[TableInteractionKey],
    ) -> TableInteractionRejection | None:
        """Return the first blocker without consuming any capacity."""
        return self._evaluate(keys, consume=False)

    def try_consume(
        self,
        keys: Iterable[TableInteractionKey],
    ) -> TableInteractionRejection | None:
        """Atomically consume all requested buckets or return one blocker."""
        return self._evaluate(keys, consume=True)

    def _evaluate(
        self,
        keys: Iterable[TableInteractionKey],
        *,
        consume: bool,
    ) -> TableInteractionRejection | None:
        requested: dict[TableInteractionKey, int] = {}
        for key in keys:
            normalized = self._normalize_key(key)
            requested[normalized] = requested.get(normalized, 0) + 1
        if not requested:
            raise ValueError("At least one table interaction bucket is required")
        if any(
            token_count > self._policy(key.scope).capacity
            for key, token_count in requested.items()
        ):
            raise ValueError("A request cannot exceed its bucket capacity")

        now = self._clock()
        self._prune_inactive(now)
        hydrated = [
            (*self._get_bucket(key, now), token_count)
            for key, token_count in requested.items()
        ]
        for _key, bucket, policy, token_count in hydrated:
            if bucket.tokens < token_count:
                return TableInteractionRejection(
                    scope=_key.scope,
                    seconds=self._retry_seconds(bucket, policy, token_count),
                )
        if consume:
            for _key, bucket, _policy, token_count in hydrated:
                bucket.tokens -= token_count
        return None

    def remove_account(self, account_id: str) -> None:
        """Discard all buckets owned by or referring to a deleted account."""
        normalized = str(account_id or "").strip()
        if not normalized:
            return
        for key in list(self._buckets):
            if normalized in {key.account_id, key.related_account_id}:
                self._buckets.pop(key, None)

    def remove_table(self, table_id: str) -> None:
        """Discard table-scoped state when its table is destroyed."""
        normalized = str(table_id or "").strip()
        if not normalized:
            return
        for key in list(self._buckets):
            if key.table_id == normalized:
                self._buckets.pop(key, None)


class _Bucket:
    __slots__ = ("tokens", "last_refill", "last_activity")

    def __init__(self, tokens: float, now: float) -> None:
        self.tokens = tokens
        self.last_refill = now
        self.last_activity = now
