"""Reusable validation and execution for server-driven copy directives."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

import wx


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
NO_COPY_DIRECTIVE = object()


@dataclass(frozen=True, slots=True)
class CopyExecutionResult:
    accepted: bool
    copied: bool
    feedback: str = ""


def _valid_copy_text(text: object) -> bool:
    if not isinstance(text, str) or not text or len(text) > MAX_COPY_TEXT_LENGTH:
        return False
    return not any(
        (ord(character) < 32 and character not in "\t\n\r")
        or 127 <= ord(character) <= 159
        or unicodedata.category(character) in {"Cs", "Zl", "Zp"}
        or character in UNSAFE_BIDI_CONTROLS
        for character in text
    )


def _valid_feedback_text(text: object) -> bool:
    if (
        not isinstance(text, str)
        or not text.strip()
        or len(text) > MAX_COPY_FEEDBACK_LENGTH
    ):
        return False
    return not any(
        unicodedata.category(character) in {"Cc", "Cs", "Zl", "Zp"}
        or character in UNSAFE_BIDI_CONTROLS
        for character in text
    )


def validate_copy_directive(value: object) -> dict[str, str | int] | None:
    """Return a strict normalized directive or reject it without side effects."""
    try:
        if not isinstance(value, dict) or set(value) != COPY_DIRECTIVE_FIELDS:
            return None
        if type(value.get("version")) is not int:
            return None
        if value.get("version") != COPY_DIRECTIVE_VERSION:
            return None
        if not _valid_copy_text(value.get("text")):
            return None
        if not _valid_feedback_text(value.get("success_text")):
            return None
        if not _valid_feedback_text(value.get("failure_text")):
            return None
        return {
            "version": value["version"],
            "text": value["text"],
            "success_text": value["success_text"],
            "failure_text": value["failure_text"],
        }
    except Exception:  # Untrusted mapping implementations must stay inert.
        return None


def copy_text_to_clipboard(text: str, clipboard=None) -> bool:
    """Copy validated text with wx while safely releasing clipboard ownership."""
    target = clipboard if clipboard is not None else wx.TheClipboard
    opened = False
    try:
        opened = bool(target.Open())
        if not opened or not target.SetData(wx.TextDataObject(text)):
            return False
        return bool(target.Flush())
    except Exception:
        return False
    finally:
        if opened:
            try:
                target.Close()
            except Exception:
                pass


def execute_copy_directive(
    value: object,
    copier=copy_text_to_clipboard,
) -> CopyExecutionResult:
    """Validate and execute one directive for any desktop UI surface."""
    directive = validate_copy_directive(value)
    if directive is None:
        return CopyExecutionResult(accepted=False, copied=False)
    try:
        copied = bool(copier(directive["text"]))
    except Exception:
        copied = False
    feedback_key = "success_text" if copied else "failure_text"
    return CopyExecutionResult(
        accepted=True,
        copied=copied,
        feedback=str(directive[feedback_key]),
    )
