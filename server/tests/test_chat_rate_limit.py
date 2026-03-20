"""Tests for the token bucket chat rate limiter with auto-moderation."""

import pytest
from unittest.mock import patch
from server.auth.chat_rate_limit import ChatRateLimiter, _UserBucket


class TestTokenBucket:
    """Test basic token bucket consumption and refill."""

    def test_initial_burst_allowed(self):
        limiter = ChatRateLimiter()
        for _ in range(5):
            allowed, reason = limiter.try_consume("alice")
            assert allowed is True
            assert reason is None

    def test_sixth_message_denied(self):
        limiter = ChatRateLimiter()
        for _ in range(5):
            limiter.try_consume("alice")
        allowed, reason = limiter.try_consume("alice")
        assert allowed is False
        assert reason == "chat-rate-limited"

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_token_refill(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()
        # Consume all 5 tokens
        for _ in range(5):
            limiter.try_consume("alice")

        # Advance 4 seconds → 2 tokens refilled (0.5/sec)
        mock_time.return_value = 1004.0
        allowed, reason = limiter.try_consume("alice")
        assert allowed is True

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_refill_capped_at_capacity(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()
        # Consume 1 token
        limiter.try_consume("alice")

        # Wait a very long time — tokens should cap at 5
        mock_time.return_value = 2000.0
        bucket = limiter.get_bucket("alice")
        # Trigger refill via try_consume
        limiter.try_consume("alice")
        # Bucket should have 5 - 1 = 4 tokens (capped at 5 then consumed 1)
        assert bucket.tokens <= ChatRateLimiter.BUCKET_CAPACITY

    def test_separate_users_independent(self):
        limiter = ChatRateLimiter()
        for _ in range(5):
            limiter.try_consume("alice")

        # Alice is exhausted, Bob should still be fine
        allowed, _ = limiter.try_consume("bob")
        assert allowed is True

        # Alice is denied
        allowed, _ = limiter.try_consume("alice")
        assert allowed is False


class TestStrikeEscalation:
    """Test auto-moderation strike counting and escalation."""

    def test_strikes_accumulate(self):
        limiter = ChatRateLimiter()
        # Exhaust tokens
        for _ in range(5):
            limiter.try_consume("alice")

        # Each denied message adds a strike
        limiter.try_consume("alice")
        assert limiter.get_bucket("alice").strikes == 1

        limiter.try_consume("alice")
        assert limiter.get_bucket("alice").strikes == 2

    def test_warning_before_mute(self):
        limiter = ChatRateLimiter()
        # Exhaust tokens
        for _ in range(5):
            limiter.try_consume("alice")

        # Strikes 1-3 should return warning
        for i in range(3):
            allowed, reason = limiter.try_consume("alice")
            assert allowed is False
            assert reason == "chat-rate-limited"

    def test_first_auto_mute_at_strike_4(self):
        limiter = ChatRateLimiter()
        # Exhaust tokens
        for _ in range(5):
            limiter.try_consume("alice")

        # Accumulate 3 strikes (warnings)
        for _ in range(3):
            limiter.try_consume("alice")

        # Strike 4 → auto-mute 30 seconds
        allowed, reason = limiter.try_consume("alice")
        assert allowed is False
        assert reason == "__auto_muted_seconds:30"

    def test_second_auto_mute_at_strike_5(self):
        limiter = ChatRateLimiter()
        for _ in range(5):
            limiter.try_consume("alice")

        # Accumulate 3 strikes
        for _ in range(3):
            limiter.try_consume("alice")

        # Strike 4 → mute 30s
        limiter.try_consume("alice")

        # Clear mute to allow next strike
        bucket = limiter.get_bucket("alice")
        bucket.muted_until = None

        # Strike 5 → mute 2 minutes
        allowed, reason = limiter.try_consume("alice")
        assert allowed is False
        assert reason == "__auto_muted_minutes:2"

    def test_severe_auto_mute_at_strike_6(self):
        limiter = ChatRateLimiter()
        for _ in range(5):
            limiter.try_consume("alice")

        for _ in range(3):
            limiter.try_consume("alice")

        # Strike 4
        limiter.try_consume("alice")
        bucket = limiter.get_bucket("alice")
        bucket.muted_until = None

        # Strike 5
        limiter.try_consume("alice")
        bucket.muted_until = None

        # Strike 6 → 5 minutes
        allowed, reason = limiter.try_consume("alice")
        assert allowed is False
        assert reason == "__auto_muted_minutes:5"


class TestAutoMuteBlocking:
    """Test that auto-muted users are blocked until mute expires."""

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_muted_user_blocked(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("alice")
        bucket.muted_until = 1030.0  # Muted for 30 seconds

        allowed, reason = limiter.try_consume("alice")
        assert allowed is False
        assert reason == "__auto_muted:31"

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_mute_expires(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("alice")
        bucket.muted_until = 1030.0
        bucket.tokens = 5.0  # Ensure tokens available

        # Still muted
        mock_time.return_value = 1029.0
        allowed, _ = limiter.try_consume("alice")
        assert allowed is False

        # Mute expired
        mock_time.return_value = 1031.0
        allowed, _ = limiter.try_consume("alice")
        assert allowed is True


class TestStrikeDecay:
    """Test that strikes decay over time."""

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_single_strike_decay(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()

        # Exhaust tokens and get 1 strike
        for _ in range(5):
            limiter.try_consume("alice")
        limiter.try_consume("alice")
        assert limiter.get_bucket("alice").strikes == 1

        # Wait 60 seconds → 1 strike decays
        mock_time.return_value = 1061.0
        # Refill tokens to allow the try_consume to reach decay logic
        limiter.get_bucket("alice").tokens = 5.0
        limiter.try_consume("alice")
        assert limiter.get_bucket("alice").strikes == 0

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_multiple_strikes_decay(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()

        # Set up 3 strikes directly
        bucket = limiter.get_bucket("alice")
        bucket.strikes = 3
        bucket.last_strike_time = 1000.0
        bucket.tokens = 5.0

        # Wait 120 seconds → 2 strikes decay
        mock_time.return_value = 1121.0
        limiter.try_consume("alice")
        assert bucket.strikes == 1

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_strikes_dont_go_negative(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()

        bucket = limiter.get_bucket("alice")
        bucket.strikes = 1
        bucket.last_strike_time = 1000.0
        bucket.tokens = 5.0

        # Wait way too long — should clamp at 0, not go negative
        mock_time.return_value = 2000.0
        limiter.try_consume("alice")
        assert bucket.strikes == 0


class TestIsMuted:
    """Test the is_muted query method."""

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_not_muted(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()
        muted, remaining = limiter.is_muted("alice")
        assert muted is False
        assert remaining == 0

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_is_muted(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("alice")
        bucket.muted_until = 1030.0

        muted, remaining = limiter.is_muted("alice")
        assert muted is True
        assert remaining == 31  # int(30) + 1

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_mute_expired_clears(self, mock_time):
        mock_time.return_value = 1000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("alice")
        bucket.muted_until = 999.0

        muted, remaining = limiter.is_muted("alice")
        assert muted is False
        assert remaining == 0
        assert bucket.muted_until is None


class TestAdminNotification:
    """Test admin notification flags."""

    def test_notify_at_6_strikes(self):
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("alice")
        bucket.strikes = 6
        assert limiter.should_notify_admins("alice") is True

    def test_no_notify_below_6(self):
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("alice")
        bucket.strikes = 5
        assert limiter.should_notify_admins("alice") is False

    def test_no_notify_after_marked(self):
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("alice")
        bucket.strikes = 6
        limiter.mark_admin_notified("alice")
        assert limiter.should_notify_admins("alice") is False

    def test_no_notify_unknown_user(self):
        limiter = ChatRateLimiter()
        assert limiter.should_notify_admins("unknown") is False


class TestCleanup:
    """Test user removal."""

    def test_remove_user(self):
        limiter = ChatRateLimiter()
        limiter.try_consume("alice")
        limiter.remove_user("alice")
        # After removal, user gets a fresh bucket
        bucket = limiter.get_bucket("alice")
        assert bucket.tokens == ChatRateLimiter.BUCKET_CAPACITY
        assert bucket.strikes == 0

    def test_remove_nonexistent_user(self):
        limiter = ChatRateLimiter()
        # Should not raise
        limiter.remove_user("nobody")
