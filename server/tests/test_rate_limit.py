import pytest
from unittest.mock import patch
from server.auth.rate_limit import RateLimiter

def test_login_rate_limiting():
    limiter = RateLimiter()
    ip = "192.168.1.1"

    for _ in range(5):
        assert limiter.is_login_allowed(ip) is True
        limiter.record_failed_login(ip)

    assert limiter.is_login_allowed(ip) is False
    assert limiter.is_login_allowed("10.0.0.1") is True

    limiter.clear_failed_logins(ip)
    assert limiter.is_login_allowed(ip) is True

def test_registration_rate_limiting():
    limiter = RateLimiter()
    ip = "192.168.1.1"

    for _ in range(3):
        assert limiter.is_registration_allowed(ip) is True
        limiter.record_registration(ip)

    assert limiter.is_registration_allowed(ip) is False

@patch('server.auth.rate_limit.time.time')
def test_cleanup_logic(mock_time):
    # Start at time 1000 BEFORE init so _last_full_cleanup gets 1000.0
    mock_time.return_value = 1000.0

    limiter = RateLimiter()
    ip = "192.168.1.1"

    limiter.record_failed_login(ip)
    limiter.record_failed_login(ip)

    # Move forward 5 minutes (still in window)
    mock_time.return_value = 1300.0
    assert len(limiter._failed_logins[ip]) == 2

    # Move forward 16 minutes (past the 15 min / 900s window)
    mock_time.return_value = 1950.0

    # The next check should clean up the old attempts
    assert limiter.is_login_allowed(ip) is True
    assert ip not in limiter._failed_logins
