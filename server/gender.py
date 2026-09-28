"""Canonical account gender values and localization selectors."""

from __future__ import annotations

import re
from enum import Enum
from typing import Any


class Gender(str, Enum):
    """Supported account gender values.

    Values intentionally retain the existing database representation so this
    runtime model does not require a persistence migration. ``selector`` is
    the stable, language-independent value exposed to Fluent and game logic.
    """

    MALE = "Male"
    FEMALE = "Female"
    NON_BINARY = "Non-binary"
    UNSPECIFIED = "Not set"

    @property
    def selector(self) -> str:
        """Return the stable selector used by localization and game systems."""
        return {
            Gender.MALE: "male",
            Gender.FEMALE: "female",
            Gender.NON_BINARY: "non-binary",
            Gender.UNSPECIFIED: "unspecified",
        }[self]

    @property
    def localization_key(self) -> str:
        """Return the shared profile-label localization key."""
        return {
            Gender.MALE: "gender-male",
            Gender.FEMALE: "gender-female",
            Gender.NON_BINARY: "gender-non-binary",
            Gender.UNSPECIFIED: "gender-not-set",
        }[self]

    @property
    def menu_item_id(self) -> str:
        """Return the established stable id used by the gender menu."""
        return f"gender_{self.value}"


GENDER_OPTIONS = (
    Gender.MALE,
    Gender.FEMALE,
    Gender.NON_BINARY,
    Gender.UNSPECIFIED,
)

_GENDER_ALIASES = {
    gender.value.casefold(): gender for gender in GENDER_OPTIONS
} | {gender.selector.casefold(): gender for gender in GENDER_OPTIONS}
_LOCALIZATION_VARIABLE_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")


def normalize_gender(value: Any) -> Gender:
    """Return a supported gender, falling back safely to neutral/unspecified."""
    if isinstance(value, Gender):
        return value
    if not isinstance(value, str):
        return Gender.UNSPECIFIED
    return _GENDER_ALIASES.get(value.strip().casefold(), Gender.UNSPECIFIED)


def require_gender(value: Any) -> Gender:
    """Return a supported gender or reject an invalid mutation value."""
    gender = normalize_gender(value)
    if isinstance(value, Gender):
        return gender
    if not isinstance(value, str) or value.strip().casefold() not in _GENDER_ALIASES:
        raise ValueError("Gender must be one of the supported canonical values")
    return gender


def gender_localization_kwargs(
    value: Any,
    variable: str = "player",
) -> dict[str, str]:
    """Build the canonical Fluent gender selector for an identity variable."""
    if not isinstance(variable, str) or not _LOCALIZATION_VARIABLE_PATTERN.fullmatch(
        variable
    ):
        raise ValueError(
            "Localization variable must start with an ASCII letter and contain "
            "only ASCII letters, digits, or underscores"
        )
    return {f"{variable}_gender": normalize_gender(value).selector}


__all__ = [
    "GENDER_OPTIONS",
    "Gender",
    "gender_localization_kwargs",
    "normalize_gender",
    "require_gender",
]
