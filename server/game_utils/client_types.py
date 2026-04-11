"""Helpers for client capability checks."""

from typing import Any


TOUCH_CLIENT_TYPES = {"web", "mobile"}
SELF_VOICING_CLIENT_TYPES = {"web", "mobile"}


def normalize_client_type(client_type: str | None) -> str:
    """Normalize a client type string for comparisons."""
    return (client_type or "").strip().lower()


def get_client_type(user: Any) -> str:
    """Return a normalized client type from a user-like object."""
    return normalize_client_type(getattr(user, "client_type", ""))


def is_touch_client_type(client_type: str | None) -> bool:
    """Return True for clients that need touch-friendly game actions."""
    return normalize_client_type(client_type) in TOUCH_CLIENT_TYPES


def is_web_client_type(client_type: str | None) -> bool:
    """Return True for the browser client."""
    return normalize_client_type(client_type) == "web"


def is_mobile_client_type(client_type: str | None) -> bool:
    """Return True for the first-party mobile client."""
    return normalize_client_type(client_type) == "mobile"


def is_touch_client(user: Any) -> bool:
    """Return True if the user is connected from a touch client."""
    return is_touch_client_type(get_client_type(user))


def uses_self_voicing_settings_type(client_type: str | None) -> bool:
    """Return True for clients that manage their own speech settings."""
    return normalize_client_type(client_type) in SELF_VOICING_CLIENT_TYPES


def uses_self_voicing_settings(user: Any) -> bool:
    """Return True if the user should receive self-voicing settings."""
    return uses_self_voicing_settings_type(get_client_type(user))
