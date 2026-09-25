"""Tests for the bounded account chat limiter and auto-moderation."""

from unittest.mock import patch

import pytest

from server.auth.chat_rate_limit import ChatRateLimiter, normalize_chat_content


def _exhaust_burst(limiter: ChatRateLimiter, account_id: str = "account-a") -> None:
    for _ in range(limiter.BUCKET_CAPACITY):
        assert limiter.try_consume(account_id)[0]


class TestTokenBucket:
    def test_initial_burst_allowed_and_sixth_message_denied(self) -> None:
        limiter = ChatRateLimiter()
        _exhaust_burst(limiter)

        allowed, rejection = limiter.try_consume("account-a")

        assert not allowed
        assert rejection is not None
        assert rejection.kind == "rate_limited"
        assert rejection.seconds == 0

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_token_refill_is_capped_at_capacity(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        assert limiter.try_consume("account-a")[0]

        mock_time.return_value = 2_000.0
        assert limiter.try_consume("account-a")[0]

        assert limiter.get_bucket("account-a").tokens == (
            ChatRateLimiter.BUCKET_CAPACITY - 1
        )

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_clock_rollback_does_not_create_refill_capacity(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a")
        bucket.tokens = 0.0

        mock_time.return_value = 900.0
        assert not limiter.try_consume("account-a")[0]
        assert bucket.last_refill == 1_000.0

        mock_time.return_value = 901.0
        assert not limiter.try_consume("account-a")[0]
        assert bucket.tokens == 0.0

    def test_accounts_have_independent_capacity(self) -> None:
        limiter = ChatRateLimiter()
        _exhaust_burst(limiter, "account-a")

        assert limiter.try_consume("account-b")[0]
        assert not limiter.try_consume("account-a")[0]

    @pytest.mark.parametrize("account_id", ["", "   ", None])
    def test_account_identity_is_required(self, account_id) -> None:
        limiter = ChatRateLimiter()

        with pytest.raises(ValueError):
            limiter.try_consume(account_id)


class TestContentProtection:
    def test_duplicate_fingerprint_normalizes_case_spacing_and_format_controls(
        self,
    ) -> None:
        limiter = ChatRateLimiter()

        assert limiter.try_consume("account-a", "Hello\u200b world")[0]
        assert limiter.try_consume("account-a", "  HELLO   WORLD  ")[0]
        allowed, rejection = limiter.try_consume("account-a", "hello world")

        assert not allowed
        assert rejection is not None
        assert rejection.kind == "repeated_message"
        assert limiter.get_bucket("account-a").strikes == 1
        assert len(limiter.get_bucket("account-a").recent_messages) == 2

    def test_unicode_compatibility_forms_share_a_fingerprint(self) -> None:
        assert normalize_chat_content("ＴＥＳＴ") == normalize_chat_content("test")

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_duplicate_window_expires(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        assert limiter.try_consume("account-a", "same")[0]
        assert limiter.try_consume("account-a", "same")[0]

        mock_time.return_value = 1_031.0
        assert limiter.try_consume("account-a", "same")[0]

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_sustained_window_caps_alternating_messages(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()

        for index in range(ChatRateLimiter.SUSTAINED_MESSAGE_LIMIT):
            mock_time.return_value = 1_000.0 + index * 2.1
            assert limiter.try_consume("account-a", f"message {index}")[0]

        mock_time.return_value = 1_042.0
        allowed, rejection = limiter.try_consume("account-a", "one too many")

        assert not allowed
        assert rejection is not None
        assert rejection.kind == "rate_limited"
        assert len(limiter.get_bucket("account-a").recent_messages) == 20

        mock_time.return_value = 1_060.1
        assert limiter.try_consume("account-a", "oldest expired")[0]


class TestStrikeEscalation:
    def test_rejections_accumulate_strikes(self) -> None:
        limiter = ChatRateLimiter()
        _exhaust_burst(limiter)

        for expected_strikes in range(1, 4):
            allowed, rejection = limiter.try_consume("account-a")
            assert not allowed
            assert rejection is not None
            assert rejection.kind == "rate_limited"
            assert limiter.get_bucket("account-a").strikes == expected_strikes

    @pytest.mark.parametrize(
        ("initial_strikes", "expected_seconds"),
        [
            (3, 30),
            (4, 120),
            (5, 300),
            (12, 300),
        ],
    )
    def test_auto_mute_duration_escalates(
        self, initial_strikes: int, expected_seconds: int
    ) -> None:
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a")
        bucket.tokens = 0.0
        bucket.strikes = initial_strikes

        allowed, rejection = limiter.try_consume("account-a")

        assert not allowed
        assert rejection is not None
        assert rejection.kind == "auto_mute_applied"
        assert rejection.seconds == expected_seconds

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_active_auto_mute_reports_exact_rounded_remaining_time(
        self, mock_time
    ) -> None:
        mock_time.return_value = 1_000.25
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a")
        bucket.muted_until = 1_030.0

        allowed, rejection = limiter.try_consume("account-a")

        assert not allowed
        assert rejection is not None
        assert rejection.kind == "auto_muted"
        assert rejection.seconds == 30

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_strikes_do_not_decay_during_forced_silence(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a")
        bucket.strikes = 4
        bucket.muted_until = 1_030.0
        bucket.last_strike_time = bucket.muted_until

        mock_time.return_value = 1_030.0
        assert limiter.try_consume("account-a", "allowed again")[0]
        assert bucket.strikes == 4

        mock_time.return_value = 1_090.0
        assert limiter.try_consume("account-a", "later")[0]
        assert bucket.strikes == 3

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_strike_decay_preserves_partial_interval(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a")
        bucket.strikes = 3
        bucket.last_strike_time = 1_000.0

        mock_time.return_value = 1_119.0
        assert limiter.try_consume("account-a", "first")[0]
        assert bucket.strikes == 2
        assert bucket.last_strike_time == 1_060.0

        mock_time.return_value = 1_121.0
        assert limiter.try_consume("account-a", "second")[0]
        assert bucket.strikes == 1
        assert bucket.last_strike_time == 1_120.0

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_long_decay_clamps_at_zero(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a")
        bucket.strikes = 1
        bucket.last_strike_time = 1_000.0

        mock_time.return_value = 2_000.0
        assert limiter.try_consume("account-a", "message")[0]
        assert bucket.strikes == 0
        assert bucket.last_strike_time is None


class TestQueriesAndCleanup:
    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_is_muted_does_not_create_unknown_account_state(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()

        assert limiter.is_muted("unknown") == (False, 0)
        assert "unknown" not in limiter._buckets

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_expired_mute_is_cleared(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a")
        bucket.muted_until = 999.0

        assert limiter.is_muted("account-a") == (False, 0)
        assert bucket.muted_until is None

    def test_admin_notification_is_one_shot_until_decay(self) -> None:
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a")
        bucket.strikes = limiter.ADMIN_NOTIFY_STRIKE_THRESHOLD

        assert limiter.should_notify_admins("account-a")
        limiter.mark_admin_notified("account-a")
        assert not limiter.should_notify_admins("account-a")

    def test_remove_account_discards_all_runtime_state(self) -> None:
        limiter = ChatRateLimiter()
        limiter.try_consume("account-a", "message")

        limiter.remove_user("account-a")

        assert "account-a" not in limiter._buckets
        fresh = limiter.get_bucket("account-a")
        assert fresh.tokens == limiter.BUCKET_CAPACITY
        assert fresh.strikes == 0
        assert fresh.recent_messages == []
