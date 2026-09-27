"""Canonical account authorization roles."""

USER_TRUST_LEVEL = 1
ADMIN_TRUST_LEVEL = 2
DEVELOPER_TRUST_LEVEL = 3

USER_ROLE_TRUST_LEVELS = {
    "user": USER_TRUST_LEVEL,
    "admin": ADMIN_TRUST_LEVEL,
    "developer": DEVELOPER_TRUST_LEVEL,
}
USER_ROLE_NAMES = {
    trust_level: role_name
    for role_name, trust_level in USER_ROLE_TRUST_LEVELS.items()
}
VALID_USER_TRUST_LEVELS = frozenset(USER_ROLE_NAMES)


def user_role_name(trust_level: int) -> str:
    """Return the canonical operator-facing name for one exact trust level."""
    try:
        return USER_ROLE_NAMES[trust_level]
    except KeyError as exc:
        raise ValueError(f"Unsupported user trust level: {trust_level!r}") from exc
