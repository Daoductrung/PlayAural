"""Versioned server-driven copy directives shared by UI surfaces."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass


COPY_DIRECTIVE_VERSION = 1
MAX_COPY_TEXT_LENGTH = 131_072
MAX_COPY_FEEDBACK_LENGTH = 1_000
COPY_DIRECTIVE_FIELDS = frozenset(
    {"version", "text", "success_text", "failure_text"}
)
UNSAFE_BIDI_CONTROLS = frozenset(
    "\u061c\u200e\u200f\u202a\u202b\u202c\u202d\u202e"
    "\u2066\u2067\u2068\u2069\u206a\u206b\u206c\u206d\u206e\u206f"
)


def _validate_copy_text(text: object) -> str:
    if not isinstance(text, str):
        raise TypeError("Copy directive text must be a string")
    if not text:
        raise ValueError("Copy directive text must not be empty")
    if len(text) > MAX_COPY_TEXT_LENGTH:
        raise ValueError("Copy directive text exceeds the protocol limit")
    for character in text:
        codepoint = ord(character)
        category = unicodedata.category(character)
        if (
            (codepoint < 32 and character not in "\t\n\r")
            or 127 <= codepoint <= 159
            or category in {"Cs", "Zl", "Zp"}
            or character in UNSAFE_BIDI_CONTROLS
        ):
            raise ValueError("Copy directive text contains unsafe controls")
    return text


def _validate_feedback_text(text: object) -> str:
    if not isinstance(text, str):
        raise TypeError("Copy directive feedback must be a string")
    if not text.strip():
        raise ValueError("Copy directive feedback must not be empty")
    if len(text) > MAX_COPY_FEEDBACK_LENGTH:
        raise ValueError("Copy directive feedback exceeds the protocol limit")
    for character in text:
        category = unicodedata.category(character)
        if (
            category in {"Cc", "Cs", "Zl", "Zp"}
            or character in UNSAFE_BIDI_CONTROLS
        ):
            raise ValueError("Copy directive feedback contains unsafe controls")
    return text


@dataclass(frozen=True, slots=True)
class CopyDirective:
    """A bounded clipboard request that any server-driven UI may expose."""

    text: str
    success_text: str
    failure_text: str
    version: int = COPY_DIRECTIVE_VERSION

    def __post_init__(self) -> None:
        if type(self.version) is not int or self.version != COPY_DIRECTIVE_VERSION:
            raise ValueError("Unsupported copy directive version")
        _validate_copy_text(self.text)
        _validate_feedback_text(self.success_text)
        _validate_feedback_text(self.failure_text)

    def to_dict(self) -> dict[str, str | int]:
        return {
            "version": self.version,
            "text": self.text,
            "success_text": self.success_text,
            "failure_text": self.failure_text,
        }

    @classmethod
    def from_dict(cls, value: object) -> "CopyDirective":
        """Strictly decode untrusted protocol data for menu restoration."""
        if not isinstance(value, dict) or set(value) != COPY_DIRECTIVE_FIELDS:
            raise ValueError("Malformed copy directive")
        return cls(
            version=value.get("version"),
            text=value.get("text"),
            success_text=value.get("success_text"),
            failure_text=value.get("failure_text"),
        )


def parse_copy_directive(value: object) -> CopyDirective | None:
    """Return a validated directive or fail closed for malformed data."""
    try:
        return CopyDirective.from_dict(value)
    except Exception:  # Untrusted mapping implementations must stay inert.
        return None
