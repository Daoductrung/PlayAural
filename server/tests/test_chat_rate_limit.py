"""Tests for scope-aware chat throttling and conservative escalation."""

from unittest.mock import patch

import pytest

from server.auth.chat_rate_limit import ChatRateLimiter, normalize_chat_content


def _consume_capacity(
    limiter: ChatRateLimiter,
    scope: str,
    account_id: str = "account-a",
) -> None:
    policy = limiter.POLICIES[scope]
    for index in range(policy.capacity):
        assert limiter.try_consume(
            account_id,
            f"message {index}",
            scope=scope,
        )[0]


class TestScopedPolicies:
    def test_global_burst_is_limited_without_account_mute(self) -> None:
        limiter = ChatRateLimiter()
        _consume_capacity(limiter, "global")

        allowed, rejection = limiter.try_consume(
            "account-a", "one too many", scope="global"
        )

        assert not allowed
        assert rejection is not None
        assert rejection.kind == "rate_limited"
        assert rejection.scope == "global"
        assert rejection.seconds == 2
        assert not hasattr(limiter, "is_muted")

    def test_table_chat_is_substantially_looser_than_global_chat(self) -> None:
        limiter = ChatRateLimiter()

        for index in range(limiter.GLOBAL_POLICY.capacity + 1):
            global_allowed, _ = limiter.try_consume(
                "account-a", f"global {index}", scope="global"
            )
        for index in range(limiter.GLOBAL_POLICY.capacity + 1):
            table_allowed, _ = limiter.try_consume(
                "account-a", f"table {index}", scope="table"
            )

        assert not global_allowed
        assert table_allowed
        assert limiter.TABLE_POLICY.capacity > limiter.GLOBAL_POLICY.capacity
        assert (
            limiter.TABLE_POLICY.sustained_limit
            > limiter.GLOBAL_POLICY.sustained_limit
        )

    def test_scopes_and_accounts_have_independent_capacity(self) -> None:
        limiter = ChatRateLimiter()
        _consume_capacity(limiter, "global")

        assert limiter.try_consume("account-a", "table", scope="table")[0]
        assert limiter.try_consume("account-a", "direct", scope="direct")[0]
        assert limiter.try_consume("account-b", "global", scope="global")[0]
        assert not limiter.try_consume(
            "account-a", "more global", scope="global"
        )[0]

    @pytest.mark.parametrize("account_id", ["", "   ", None])
    def test_account_identity_is_required(self, account_id) -> None:
        limiter = ChatRateLimiter()
        with pytest.raises(ValueError):
            limiter.try_consume(account_id, "message", scope="global")

    def test_unknown_scope_is_rejected(self) -> None:
        limiter = ChatRateLimiter()
        with pytest.raises(ValueError):
            limiter.try_consume("account-a", "message", scope="unknown")

    @pytest.mark.parametrize("message", ["", "   ", "\u200b", None])
    def test_message_text_is_required(self, message) -> None:
        limiter = ChatRateLimiter()
        with pytest.raises(ValueError):
            limiter.try_consume("account-a", message, scope="global")


class TestContentProtection:
    def test_duplicate_fingerprint_normalizes_case_spacing_and_controls(self) -> None:
        limiter = ChatRateLimiter()

        assert limiter.try_consume(
            "account-a", "Hello\u200b world", scope="global"
        )[0]
        assert limiter.try_consume(
            "account-a", "  HELLO   WORLD  ", scope="global"
        )[0]
        allowed, rejection = limiter.try_consume(
            "account-a", "hello world", scope="global"
        )

        assert not allowed
        assert rejection is not None
        assert rejection.kind == "repeated_message"
        assert rejection.incident_count == 1
        assert rejection.rejected_attempt_count == 1

    def test_short_conversational_replies_receive_extra_tolerance(self) -> None:
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a", "global")
        bucket.tokens = 100

        for _ in range(limiter.GLOBAL_POLICY.short_duplicate_limit):
            assert limiter.try_consume("account-a", "gg", scope="global")[0]
        allowed, rejection = limiter.try_consume(
            "account-a", "GG", scope="global"
        )

        assert not allowed
        assert rejection is not None
        assert rejection.kind == "repeated_message"

    def test_table_duplicate_threshold_is_more_forgiving(self) -> None:
        limiter = ChatRateLimiter()

        for _ in range(limiter.TABLE_POLICY.duplicate_limit):
            assert limiter.try_consume(
                "account-a", "ready to begin", scope="table"
            )[0]
        allowed, rejection = limiter.try_consume(
            "account-a", "ready to begin", scope="table"
        )

        assert not allowed
        assert rejection is not None
        assert rejection.kind == "repeated_message"

    def test_unicode_compatibility_forms_share_a_fingerprint(self) -> None:
        assert normalize_chat_content("ＴＥＳＴ") == normalize_chat_content("test")

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_duplicate_window_expires(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        assert limiter.try_consume("account-a", "same", scope="global")[0]
        assert limiter.try_consume("account-a", "same", scope="global")[0]

        mock_time.return_value = 1_031.0
        assert limiter.try_consume("account-a", "same", scope="global")[0]

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_global_sustained_window_caps_alternating_messages(
        self, mock_time
    ) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()

        for index in range(limiter.GLOBAL_POLICY.sustained_limit):
            mock_time.return_value = 1_000.0 + index * 4.0
            assert limiter.try_consume(
                "account-a", f"message {index}", scope="global"
            )[0]

        mock_time.return_value = 1_058.0
        allowed, rejection = limiter.try_consume(
            "account-a", "one too many", scope="global"
        )
        assert not allowed
        assert rejection is not None
        assert rejection.kind == "rate_limited"

        mock_time.return_value = 1_060.1
        assert limiter.try_consume(
            "account-a", "oldest expired", scope="global"
        )[0]


class TestReportEscalation:
    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_rapid_retries_are_one_incident(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a", "global")
        bucket.recent_messages = [(999.0, "flood"), (999.0, "flood")]

        rejections = []
        for attempt in range(20):
            mock_time.return_value = 1_000.0 + attempt * 0.1
            allowed, rejection = limiter.try_consume(
                "account-a", "flood", scope="global"
            )
            assert not allowed
            rejections.append(rejection)

        assert rejections[-1] is not None
        assert rejections[-1].incident_count == 1
        assert rejections[-1].rejected_attempt_count == 20
        assert not rejections[-1].report_recommended

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_global_report_requires_time_separated_incidents(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a", "global")
        bucket.recent_messages = [(999.0, "flood"), (999.0, "flood")]

        for index, now in enumerate((1_000.0, 1_010.0, 1_020.0), start=1):
            mock_time.return_value = now
            allowed, rejection = limiter.try_consume(
                "account-a", "flood", scope="global"
            )
            assert not allowed
            assert rejection is not None
            assert rejection.incident_count == index

        assert rejection.report_recommended

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_table_report_requires_more_incidents_than_global(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a", "table")
        bucket.recent_messages = [(999.0, "flood")] * (
            limiter.TABLE_POLICY.duplicate_limit
        )

        for index in range(limiter.TABLE_POLICY.report_incident_threshold - 1):
            mock_time.return_value = 1_000.0 + index * 10.0
            bucket.recent_messages = [
                (mock_time.return_value - 1.0, "flood")
            ] * limiter.TABLE_POLICY.duplicate_limit
            _, rejection = limiter.try_consume(
                "account-a", "flood", scope="table"
            )
            assert rejection is not None

        assert not rejection.report_recommended

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_direct_messages_never_create_automatic_reports(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a", "direct")
        bucket.recent_messages = [(999.0, "direct flood")] * (
            limiter.DIRECT_POLICY.duplicate_limit
        )

        for index in range(20):
            mock_time.return_value = 1_000.0 + index * 10.0
            bucket.recent_messages = [
                (mock_time.return_value - 1.0, "direct flood")
            ] * limiter.DIRECT_POLICY.duplicate_limit
            _, rejection = limiter.try_consume(
                "account-a", "direct flood", scope="direct"
            )
            assert rejection is not None
            assert not rejection.report_recommended

    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_report_suppression_prevents_duplicate_escalation(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a", "global")
        bucket.recent_messages = [(999.0, "flood"), (999.0, "flood")]
        bucket.incidents = [980.0, 990.0]

        _, rejection = limiter.try_consume(
            "account-a", "flood", scope="global"
        )
        assert rejection is not None and rejection.report_recommended

        limiter.suppress_report("account-a", "global", 60)
        mock_time.return_value = 1_010.0
        _, rejection = limiter.try_consume(
            "account-a", "flood", scope="global"
        )
        assert rejection is not None
        assert not rejection.report_recommended


class TestCleanup:
    @patch("server.auth.chat_rate_limit.time.monotonic")
    def test_clock_rollback_does_not_create_refill_capacity(self, mock_time) -> None:
        mock_time.return_value = 1_000.0
        limiter = ChatRateLimiter()
        bucket = limiter.get_bucket("account-a", "global")
        bucket.tokens = 0.0

        mock_time.return_value = 900.0
        assert not limiter.try_consume(
            "account-a", "message", scope="global"
        )[0]
        assert bucket.last_refill == 1_000.0

    def test_remove_account_discards_every_scope(self) -> None:
        limiter = ChatRateLimiter()
        for scope in limiter.POLICIES:
            limiter.try_consume("account-a", "message", scope=scope)
        limiter.try_consume("account-b", "message", scope="global")

        limiter.remove_user("account-a")

        assert all(key[0] != "account-a" for key in limiter._buckets)
        assert ("account-b", "global") in limiter._buckets
