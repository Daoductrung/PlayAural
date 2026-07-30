"""Rate limiter for voice chat join attempts."""

import time


class VoiceRateLimiter:
    """
    Per-user token bucket limiter for voice join actions.

    Voice join requests are more expensive than ordinary navigation because they
    generate signed media tokens and can trigger repeated table-wide connect and
    disconnect announcements. The limiter keeps the action responsive for normal
    use while preventing rapid join/leave spam from hammering the server.
    """

    BUCKET_CAPACITY = 2
    REFILL_RATE = 0.25  # 1 token every 4 seconds
    IDLE_RETENTION_SECONDS = 300.0
    PRUNE_INTERVAL_SECONDS = 60.0

    def __init__(self) -> None:
        self._buckets: dict[str, _VoiceBucket] = {}
        self._last_prune = time.monotonic()

    def _prune_inactive(self, now: float) -> None:
        """Bound runtime state while retaining limits across reconnects."""
        if now - self._last_prune < self.PRUNE_INTERVAL_SECONDS:
            return
        self._last_prune = now
        for username, bucket in list(self._buckets.items()):
            if now - bucket.last_activity > self.IDLE_RETENTION_SECONDS:
                self._buckets.pop(username, None)

    def try_consume(self, username: str) -> bool:
        now = time.monotonic()
        self._prune_inactive(now)
        bucket = self._buckets.get(username)
        if bucket is None:
            bucket = _VoiceBucket(self.BUCKET_CAPACITY)
            self._buckets[username] = bucket

        bucket.last_activity = now
        elapsed = now - bucket.last_refill
        bucket.tokens = min(
            self.BUCKET_CAPACITY,
            bucket.tokens + elapsed * self.REFILL_RATE,
        )
        bucket.last_refill = now

        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            return True
        return False

    def remove_user(self, username: str) -> None:
        self._buckets.pop(username, None)


class _VoiceBucket:
    __slots__ = ("tokens", "last_refill", "last_activity")

    def __init__(self, capacity: float) -> None:
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self.last_activity = self.last_refill
