"""Token bucket chat rate limiter with auto-moderation escalation."""

import time


class ChatRateLimiter:
    """
    Per-user token bucket rate limiter for chat messages.

    Each user has a bucket of tokens. Sending a message consumes 1 token.
    Tokens refill at a fixed rate. When the bucket is empty, the message
    is dropped and a strike is recorded.

    Strikes escalate: warnings → auto-mute (30s) → longer auto-mutes.
    Strikes decay over time so a single burst doesn't permanently escalate.
    """

    # Token bucket parameters
    BUCKET_CAPACITY = 5       # Max burst size
    REFILL_RATE = 0.5         # Tokens per second (1 token every 2 seconds)

    # Auto-moderation escalation
    STRIKE_WARN_THRESHOLD = 4     # Strikes 1-3 = warning, 4 = first mute
    STRIKE_DECAY_INTERVAL = 60.0  # Seconds of clean behavior to decay 1 strike

    # Auto-mute durations in seconds
    AUTO_MUTE_DURATIONS = {
        4: 30,    # First mute: 30 seconds
        5: 120,   # Second mute: 2 minutes
    }
    AUTO_MUTE_SEVERE = 300  # 6+ strikes: 5 minutes

    def __init__(self):
        self._buckets: dict[str, _UserBucket] = {}

    def get_bucket(self, username: str) -> "_UserBucket":
        """Get or create a bucket for a user."""
        if username not in self._buckets:
            self._buckets[username] = _UserBucket(self.BUCKET_CAPACITY)
        return self._buckets[username]

    def try_consume(self, username: str) -> tuple[bool, str | None]:
        """
        Try to consume a token for a chat message.

        Returns:
            (allowed, reason_key) — allowed=True if the message can be sent.
            If not allowed, reason_key is the locale key to speak to the user.
            Returns ("auto_muted", remaining_seconds) info via the bucket state.
        """
        bucket = self.get_bucket(username)
        now = time.monotonic()

        # Check if user is currently auto-muted
        if bucket.muted_until and now < bucket.muted_until:
            remaining = int(bucket.muted_until - now) + 1
            return False, f"__auto_muted:{remaining}"

        # Refill tokens
        elapsed = now - bucket.last_refill
        bucket.tokens = min(
            self.BUCKET_CAPACITY,
            bucket.tokens + elapsed * self.REFILL_RATE,
        )
        bucket.last_refill = now

        # Decay strikes over time
        if bucket.strikes > 0 and bucket.last_strike_time:
            decay_elapsed = now - bucket.last_strike_time
            decay_count = int(decay_elapsed / self.STRIKE_DECAY_INTERVAL)
            if decay_count > 0:
                bucket.strikes = max(0, bucket.strikes - decay_count)
                bucket.last_strike_time = now

        # Try to consume a token
        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            return True, None

        # No tokens — record a strike
        bucket.strikes += 1
        bucket.last_strike_time = now

        # Determine escalation
        if bucket.strikes >= self.STRIKE_WARN_THRESHOLD:
            duration = self.AUTO_MUTE_DURATIONS.get(
                bucket.strikes, self.AUTO_MUTE_SEVERE
            )
            bucket.muted_until = now + duration
            if duration < 60:
                return False, f"__auto_muted_seconds:{duration}"
            else:
                return False, f"__auto_muted_minutes:{duration // 60}"

        return False, "chat-rate-limited"

    def is_muted(self, username: str) -> tuple[bool, int]:
        """Check if a user is currently auto-muted. Returns (muted, remaining_seconds)."""
        if username not in self._buckets:
            return False, 0
        bucket = self._buckets[username]
        if not bucket.muted_until:
            return False, 0
        now = time.monotonic()
        if now >= bucket.muted_until:
            bucket.muted_until = None
            return False, 0
        return True, int(bucket.muted_until - now) + 1

    def should_notify_admins(self, username: str) -> bool:
        """Check if this user has hit the severe spam threshold (strike 6+)."""
        if username not in self._buckets:
            return False
        bucket = self._buckets[username]
        return bucket.strikes >= 6 and not bucket.admin_notified

    def mark_admin_notified(self, username: str) -> None:
        """Mark that admins have been notified about this user's spam."""
        if username in self._buckets:
            self._buckets[username].admin_notified = True

    def remove_user(self, username: str) -> None:
        """Remove a user's bucket (on disconnect)."""
        self._buckets.pop(username, None)


class _UserBucket:
    """Per-user token bucket state."""

    __slots__ = (
        "tokens",
        "last_refill",
        "strikes",
        "last_strike_time",
        "muted_until",
        "admin_notified",
    )

    def __init__(self, capacity: float):
        self.tokens: float = capacity
        self.last_refill: float = time.monotonic()
        self.strikes: int = 0
        self.last_strike_time: float | None = None
        self.muted_until: float | None = None
        self.admin_notified: bool = False
