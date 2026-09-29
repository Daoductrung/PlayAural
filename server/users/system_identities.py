"""Reserved non-account identities emitted by trusted server subsystems."""

from __future__ import annotations

from dataclasses import dataclass

from .identity import username_key


@dataclass(frozen=True)
class SystemIdentity:
    """One server-owned identity that must never be claimable by an account."""

    account_id: str
    username: str


AUTOMATED_MODERATION_IDENTITY = SystemIdentity(
    account_id="system:anti-spam",
    username="System",
)

SYSTEM_IDENTITIES = (AUTOMATED_MODERATION_IDENTITY,)
_RESERVED_SYSTEM_USERNAME_KEYS = frozenset(
    username_key(identity.username) for identity in SYSTEM_IDENTITIES
)


def is_reserved_system_username(value: object) -> bool:
    """Return whether a username would impersonate a server-owned identity."""
    return username_key(value) in _RESERVED_SYSTEM_USERNAME_KEYS
