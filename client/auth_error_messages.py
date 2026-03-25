"""Shared login failure message helpers for the desktop client."""

from localization import Localization


_CREDENTIAL_ERRORS = frozenset({"wrong_password", "user_not_found"})


def get_login_failure_message(reason: str) -> str:
    """Translate a server login failure reason into a localized client message."""
    reason_map = {
        "wrong_password": Localization.get("auth-error-wrong-password"),
        "user_not_found": Localization.get("auth-error-user-not-found"),
        "rate_limit": Localization.get("auth-error-rate-limit"),
    }
    return reason_map.get(reason) or Localization.get("login-info-failed")


def is_credential_error(reason: str) -> bool:
    """Return True when the failure is tied to stored credentials."""
    return reason in _CREDENTIAL_ERRORS
