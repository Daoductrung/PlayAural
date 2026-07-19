"""Helpers for localized administrator-authored content."""

from __future__ import annotations

import json
from collections.abc import Mapping

from .localization import DEFAULT_LOCALE, Localization


LOCALIZED_CUSTOM_PREFIX = "CUSTOM_I18N:"
LEGACY_CUSTOM_PREFIX = "CUSTOM_"


def normalize_localized_value(value: object, *, multiline: bool = True) -> str:
    """Normalize one administrator-authored value without truncating it."""
    if not isinstance(value, str):
        return ""
    text = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    return text if multiline else " ".join(text.split())


def normalize_localized_text(
    translations: Mapping[str, object] | None,
    *,
    max_length: int | None = None,
    multiline: bool = True,
) -> dict[str, str]:
    """Return clean installed-locale translations suitable for storage."""
    available = set(Localization.available_locale_codes())
    normalized: dict[str, str] = {}
    for raw_locale, raw_text in (translations or {}).items():
        if not isinstance(raw_locale, str) or not isinstance(raw_text, str):
            continue
        locale = Localization.normalize_locale_code(raw_locale)
        if locale not in available:
            continue
        text = normalize_localized_value(raw_text, multiline=multiline)
        if not text:
            continue
        if max_length is not None:
            text = text[:max_length]
        normalized[locale] = text
    return normalized


def localized_text_for_locale(
    locale: str,
    translations: Mapping[str, str] | None,
    *,
    default: str = "",
) -> str:
    """Resolve translated content with the configured source-locale fallback."""
    values = translations or {}
    resolved = Localization.resolve_locale(locale)
    value = values.get(resolved) or values.get(DEFAULT_LOCALE)
    if isinstance(value, str) and value.strip():
        return value
    return default


def encode_localized_custom_text(translations: Mapping[str, str]) -> str:
    """Encode localized custom text in a backward-compatible text field."""
    payload = json.dumps(
        dict(translations),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return f"{LOCALIZED_CUSTOM_PREFIX}{payload}"


def decode_localized_custom_text(value: str | None) -> dict[str, str] | None:
    """Decode localized or legacy custom text; return None for locale keys."""
    raw = str(value or "")
    if raw.startswith(LOCALIZED_CUSTOM_PREFIX):
        try:
            decoded = json.loads(raw[len(LOCALIZED_CUSTOM_PREFIX) :])
        except (json.JSONDecodeError, TypeError):
            return {}
        if not isinstance(decoded, dict):
            return {}
        return {
            str(locale): text
            for locale, text in decoded.items()
            if isinstance(locale, str) and isinstance(text, str) and text.strip()
        }
    if raw.startswith(LEGACY_CUSTOM_PREFIX):
        legacy = raw[len(LEGACY_CUSTOM_PREFIX) :].strip()
        return {DEFAULT_LOCALE: legacy} if legacy else {}
    return None


def localized_custom_text_for_locale(
    locale: str,
    value: str | None,
    *,
    default: str = "",
) -> str | None:
    """Resolve custom text, preserving None for ordinary localization keys."""
    translations = decode_localized_custom_text(value)
    if translations is None:
        return None
    return localized_text_for_locale(locale, translations, default=default)


def localized_penalty_reason_for_locale(locale: str, value: str | None) -> str:
    """Resolve a stored moderation reason into concise, safe display text."""
    unknown = Localization.get(locale, "admin-penalty-reason-unknown")
    raw = str(value or "").strip()
    if not raw:
        return unknown

    custom = localized_custom_text_for_locale(locale, raw)
    if custom is not None:
        return normalize_localized_value(custom, multiline=False)[:200] or unknown

    localized = Localization.get(locale, raw)
    if not localized or localized == raw:
        return unknown
    return localized
