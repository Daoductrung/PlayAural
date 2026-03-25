from pathlib import Path
import sys


CLIENT_DIR = Path(__file__).resolve().parents[1]
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

from auth_error_messages import get_login_failure_message, is_credential_error
from localization import Localization


def setup_module():
    Localization.init(locales_dir=CLIENT_DIR / "locales", locale="en")


def test_get_login_failure_message_maps_known_reasons():
    assert get_login_failure_message("wrong_password") == "Incorrect password."
    assert get_login_failure_message("user_not_found") == "User does not exist."
    assert (
        get_login_failure_message("rate_limit")
        == "Too many failed login attempts. Please try again in 15 minutes."
    )


def test_get_login_failure_message_falls_back_for_unknown_reason():
    assert get_login_failure_message("captcha_missing") == "Verification failed!"


def test_is_credential_error_only_matches_stored_credential_failures():
    assert is_credential_error("wrong_password") is True
    assert is_credential_error("user_not_found") is True
    assert is_credential_error("rate_limit") is False
