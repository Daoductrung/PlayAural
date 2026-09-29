"""Canonical username normalization and comparison helpers."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable


def normalize_username(value: object) -> str:
    """Return the storage/display form used at account boundaries."""
    return unicodedata.normalize("NFC", str(value or "").strip())


def username_key(value: object) -> str:
    """Return the compatibility- and case-insensitive account lookup key.

    The stored username remains NFC-normalized for display.  Identity lookup
    additionally folds Unicode compatibility variants so visually equivalent
    forms such as full-width Latin letters cannot create a second account.
    Applying NFKC again after full case folding keeps the result normalized
    when a fold expands into multiple code points.
    """
    compatibility_form = unicodedata.normalize("NFKC", normalize_username(value))
    return unicodedata.normalize("NFKC", compatibility_form.casefold())


def legacy_username_key_v2(value: object) -> str:
    """Return the lookup key used by schema versions one and two.

    SQLite expression indexes depend on function semantics during pre-migration
    integrity checks, so the old transform remains available under its original
    SQL function name until those schema versions are retired.
    """
    return normalize_username(value).casefold()


def username_validation_error(value: object) -> str | None:
    """Return the public registration error code for an invalid username."""
    username = normalize_username(value)
    if len(username) < 3 or len(username) > 30:
        return "username_length"
    if "  " in username or not all(
        character.isalpha() or character.isdigit() or character == " "
        for character in username
    ):
        return "username_invalid_chars"
    return None


def find_username_prefix(text: str, usernames: Iterable[str]) -> tuple[str, int] | None:
    """Resolve the longest username at the start of a private-message command.

    The returned integer is the number of original characters consumed. Exact
    registered spelling wins over case-insensitive matching. A folded match is
    accepted only when it identifies one candidate, which keeps legacy
    case-fold collisions from being routed to the wrong account.
    """
    source = str(text or "")
    candidates = list(dict.fromkeys(str(name or "").strip() for name in usernames))
    candidates = [name for name in candidates if name]
    if not source or not candidates:
        return None

    exact_names = set(candidates)
    names_by_key: dict[str, list[str]] = {}
    for name in candidates:
        names_by_key.setdefault(username_key(name), []).append(name)

    boundaries = [index for index, char in enumerate(source) if char == " "]
    boundaries.append(len(source))
    for end in sorted(set(boundaries), reverse=True):
        if end <= 0:
            continue
        entered = source[:end].strip()
        if not entered:
            continue

        if entered in exact_names:
            return entered, end

        folded_matches = names_by_key.get(username_key(entered), [])
        if len(folded_matches) == 1:
            return folded_matches[0], end

    return None
