from server.auth.table_interaction_rate_limit import (
    TableInteractionRateLimiter,
    TableInteractionScope,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_role_change_allows_correction_then_throttles_until_refill() -> None:
    clock = FakeClock()
    limiter = TableInteractionRateLimiter(clock=clock)
    key = limiter.role_change_key("account-a", "table-a")

    assert limiter.try_consume((key,)) is None
    assert limiter.try_consume((key,)) is None

    rejection = limiter.try_consume((key,))
    assert rejection is not None
    assert rejection.scope is TableInteractionScope.ROLE_CHANGE
    assert rejection.seconds == 15

    clock.advance(14.1)
    rejection = limiter.check((key,))
    assert rejection is not None
    assert rejection.seconds == 1

    clock.advance(0.9)
    assert limiter.try_consume((key,)) is None


def test_rejected_pair_cooldown_does_not_consume_sender_capacity() -> None:
    limiter = TableInteractionRateLimiter(clock=FakeClock())

    assert limiter.try_consume(limiter.invite_keys("host", "friend-a")) is None
    rejection = limiter.try_consume(limiter.invite_keys("host", "friend-a"))
    assert rejection is not None
    assert rejection.scope is TableInteractionScope.INVITE_PAIR

    assert limiter.try_consume(limiter.invite_keys("host", "friend-b")) is None
    assert limiter.try_consume(limiter.invite_keys("host", "friend-c")) is None
    rejection = limiter.try_consume(limiter.invite_keys("host", "friend-d"))
    assert rejection is not None
    assert rejection.scope is TableInteractionScope.INVITE_SENDER


def test_voice_moderation_has_an_independent_bounded_budget() -> None:
    clock = FakeClock()
    limiter = TableInteractionRateLimiter(clock=clock)
    key = limiter.voice_moderation_key("account-a", "table-a")

    for _ in range(3):
        assert limiter.try_consume((key,)) is None
    rejection = limiter.try_consume((key,))
    assert rejection is not None
    assert rejection.scope is TableInteractionScope.VOICE_MODERATION
    assert rejection.seconds == 10

    # Other interaction classes do not inherit a voice moderation cooldown.
    assert limiter.try_consume(
        (limiter.role_change_key("account-a", "table-a"),)
    ) is None
    clock.advance(10)
    assert limiter.try_consume((key,)) is None


def test_cleanup_removes_related_account_and_table_state() -> None:
    limiter = TableInteractionRateLimiter(clock=FakeClock())
    role_key = limiter.role_change_key("account-c", "table-a")
    pair_keys = limiter.invite_keys("account-b", "account-a")

    assert limiter.try_consume((role_key,)) is None
    assert limiter.try_consume((role_key,)) is None
    assert limiter.try_consume(pair_keys) is None
    limiter.remove_account("account-a")

    assert limiter.try_consume(pair_keys) is None
    assert limiter.try_consume((role_key,)) is not None
    limiter.remove_table("table-a")
    assert limiter.try_consume((role_key,)) is None


def test_invalid_keys_fail_closed() -> None:
    limiter = TableInteractionRateLimiter(clock=FakeClock())

    try:
        limiter.try_consume(
            (limiter.role_change_key("account-a", ""),)
        )
    except ValueError as exc:
        assert "table ID" in str(exc)
    else:
        raise AssertionError("Missing table identity must be rejected")
