"""Locale-aware bot naming and unambiguous display-label helpers."""

from __future__ import annotations

import random
import unicodedata
from collections import Counter
from collections.abc import Iterable, Sequence

from ..messages.localization import DEFAULT_LOCALE, Localization


MIN_BOT_NAME_LENGTH = 3
MAX_BOT_NAME_LENGTH = 30
BOT_NAME_POOL_MESSAGE_ID = "bot-name-pool"
BOT_NAME_POOL_SEPARATOR = "|"


def normalize_bot_name(name: object) -> str:
    """Normalize a user-visible bot base name without changing letter case."""
    return " ".join(
        unicodedata.normalize("NFC", str(name or "")).strip().split()
    )


def bot_name_key(name: object) -> str:
    """Return a compatibility- and case-insensitive comparison key."""
    normalized = unicodedata.normalize("NFKC", normalize_bot_name(name))
    return unicodedata.normalize("NFKC", normalized.casefold())


def validate_custom_bot_name(name: object) -> str | None:
    """Return a localization key when a custom bot base name is invalid.

    Bot base names are presentation data. They deliberately may match an
    account name or another bot base name; the rendered bot marker and ordinal
    keep every table label distinct while immutable player ids remain the
    authority for gameplay and protocol actions.
    """
    normalized = normalize_bot_name(name)
    if not MIN_BOT_NAME_LENGTH <= len(normalized) <= MAX_BOT_NAME_LENGTH:
        return "bot-name-invalid-length"
    if not all(char.isalpha() or char.isdigit() or char == " " for char in normalized):
        return "bot-name-invalid-characters"
    return None


def get_valid_bot_name_pool(name_pool: Sequence[str]) -> tuple[str, ...]:
    """Normalize, validate, and de-duplicate one configured bot-name pool."""
    valid_names: list[str] = []
    seen: set[str] = set()
    for name in name_pool:
        normalized = normalize_bot_name(name)
        if validate_custom_bot_name(normalized) is not None:
            continue
        key = bot_name_key(normalized)
        if key in seen:
            continue
        valid_names.append(normalized)
        seen.add(key)
    return tuple(valid_names)


def get_native_bot_name_pool(locale: str | None) -> tuple[str, ...]:
    """Return the validated names authored for one resolved locale.

    A locale may omit the pool entirely and inherit English. Once it defines
    the pool, however, reject invalid or canonically duplicated entries rather
    than silently hiding a translator or maintainer mistake.
    """
    resolved_locale = Localization.resolve_locale(locale or DEFAULT_LOCALE)
    encoded_values = Localization.get_message_attribute_values(
        resolved_locale,
        BOT_NAME_POOL_MESSAGE_ID,
        include_fallback=False,
    )
    if not encoded_values:
        return ()
    if len(encoded_values) != 1:
        raise RuntimeError(
            f"Locale {resolved_locale!r} must define exactly one "
            f"{BOT_NAME_POOL_MESSAGE_ID} attribute"
        )

    configured_names = tuple(
        encoded_values[0].split(BOT_NAME_POOL_SEPARATOR)
    )
    valid_names = get_valid_bot_name_pool(configured_names)
    if len(valid_names) != len(configured_names):
        raise RuntimeError(
            f"Locale {resolved_locale!r} contains an invalid or duplicate "
            f"{BOT_NAME_POOL_MESSAGE_ID} entry"
        )
    return valid_names


def get_localized_bot_name_pool(locale: str | None) -> tuple[str, ...]:
    """Return locale-native names followed by de-duplicated English fallback."""
    resolved_locale = Localization.resolve_locale(locale or DEFAULT_LOCALE)
    localized_pool = get_native_bot_name_pool(resolved_locale)
    english_pool = get_native_bot_name_pool(DEFAULT_LOCALE)
    pool = get_valid_bot_name_pool((*localized_pool, *english_pool))
    if not pool:
        raise RuntimeError(
            f"Locale {locale!r} has no valid {BOT_NAME_POOL_MESSAGE_ID} entries"
        )
    return pool


def _get_bot_name_pool_tiers(
    locale: str | None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return locale-native and English fallback pools as separate tiers."""
    resolved_locale = Localization.resolve_locale(locale or DEFAULT_LOCALE)
    primary = get_native_bot_name_pool(resolved_locale)
    if resolved_locale == DEFAULT_LOCALE:
        return primary, ()

    fallback = get_native_bot_name_pool(DEFAULT_LOCALE)
    primary_keys = {bot_name_key(name) for name in primary}
    return primary, tuple(
        name for name in fallback if bot_name_key(name) not in primary_keys
    )


def generate_bot_base_name(
    existing_bot_base_names: Iterable[str],
    locale: str | None,
    *,
    name_pool: Sequence[str] | None = None,
) -> str:
    """Choose a diverse bot base name without reserving human account names.

    Unused locale-native names are preferred within a table, followed by
    unused English fallback names. Only after both finite tiers are exhausted
    may a base repeat; roster reconciliation then adds a stable ordinal.
    """
    if name_pool is None:
        primary_pool, fallback_pool = _get_bot_name_pool_tiers(locale)
        pool = (*primary_pool, *fallback_pool)
    else:
        primary_pool = get_valid_bot_name_pool(name_pool)
        fallback_pool = ()
        pool = primary_pool
    if not pool:
        raise ValueError("name_pool must contain at least one valid bot name")

    used = {
        bot_name_key(name)
        for name in existing_bot_base_names
        if normalize_bot_name(name)
    }
    available_primary = [
        name for name in primary_pool if bot_name_key(name) not in used
    ]
    if available_primary:
        return random.choice(available_primary)

    available_fallback = [
        name for name in fallback_pool if bot_name_key(name) not in used
    ]
    if available_fallback:
        return random.choice(available_fallback)

    return random.choice(list(pool))


def format_bot_display_name(
    base_name: object,
    locale: str | None,
    *,
    ordinal: int = 1,
) -> str:
    """Render one visibly bot-owned label from a validated base name."""
    normalized = normalize_bot_name(base_name)
    if validate_custom_bot_name(normalized) is not None:
        raise ValueError("base_name must be a valid bot name")
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 1:
        raise ValueError("ordinal must be a positive integer")

    message_id = (
        "bot-display-name"
        if ordinal == 1
        else "bot-display-name-numbered"
    )
    resolved_locale = Localization.resolve_locale(locale or DEFAULT_LOCALE)
    locales = [resolved_locale]
    if resolved_locale != DEFAULT_LOCALE:
        locales.append(DEFAULT_LOCALE)

    for candidate_locale in locales:
        rendered = Localization.get(
            candidate_locale,
            message_id,
            name=normalized,
            number=ordinal,
        )
        rendered = normalize_bot_name(rendered)
        has_non_username_marker = any(
            not char.isalpha() and not char.isdigit() and char != " "
            for char in rendered
        )
        marker_text = rendered.replace(normalized, "", 1)
        has_spoken_marker = any(char.isalpha() for char in marker_text)
        if (
            rendered != message_id
            and rendered
            and normalized in rendered
            and has_non_username_marker
            and has_spoken_marker
            and (ordinal == 1 or str(ordinal) in rendered)
        ):
            return rendered

    raise RuntimeError(
        f"Invalid or missing bot-label localization message: {message_id}"
    )


def plan_bot_display_names(
    bot_base_names: Sequence[object],
    participant_names: Iterable[object],
    locale: str | None,
) -> tuple[str, ...]:
    """Plan unique bot labels for one complete roster.

    A lone bot keeps its bare base. The localized marker appears only when a
    human identity or another bot uses the same canonical base; ordinals are
    assigned in stable roster order. Structural ids remain authoritative.
    """
    bases = tuple(normalize_bot_name(name) for name in bot_base_names)
    if any(validate_custom_bot_name(name) is not None for name in bases):
        raise ValueError("bot_base_names must contain only valid bot names")

    participant_keys = {
        bot_name_key(name)
        for name in participant_names
        if normalize_bot_name(name)
    }
    counts = Counter(bot_name_key(name) for name in bases)
    next_ordinals: dict[str, int] = {}
    used = set(participant_keys)
    planned: list[str] = []

    for base_name in bases:
        base_key = bot_name_key(base_name)
        needs_marker = counts[base_key] > 1 or base_key in participant_keys
        if not needs_marker and base_key not in used:
            candidate = base_name
        else:
            ordinal = next_ordinals.get(base_key, 1)
            while True:
                candidate = format_bot_display_name(
                    base_name,
                    locale,
                    ordinal=ordinal,
                )
                if bot_name_key(candidate) not in used:
                    break
                ordinal += 1
            next_ordinals[base_key] = ordinal + 1

        planned.append(candidate)
        used.add(bot_name_key(candidate))

    return tuple(planned)


def allocate_bot_display_name(
    base_name: object,
    existing_display_names: Iterable[str],
    locale: str | None,
) -> str:
    """Allocate a bare label unless the current roster requires a bot marker."""
    used = {
        bot_name_key(name)
        for name in existing_display_names
        if normalize_bot_name(name)
    }
    normalized = normalize_bot_name(base_name)
    if validate_custom_bot_name(normalized) is not None:
        raise ValueError("base_name must be a valid bot name")
    if bot_name_key(normalized) not in used:
        return normalized

    ordinal = 1
    while True:
        candidate = format_bot_display_name(
            base_name,
            locale,
            ordinal=ordinal,
        )
        if bot_name_key(candidate) not in used:
            return candidate
        ordinal += 1
