"""Data-driven global-chat language channel registry."""

from dataclasses import dataclass


MAX_CHAT_MESSAGE_LENGTH = 500


@dataclass(frozen=True, slots=True)
class GlobalChatChannel:
    """One selectable language partition for global chat."""

    code: str


# Stable BCP 47 base-language identifiers. Display names are resolved through
# the localization layer, so adding a channel does not require client changes
# or language-specific branches in chat delivery.
GLOBAL_CHAT_CHANNELS: tuple[GlobalChatChannel, ...] = tuple(
    GlobalChatChannel(code)
    for code in (
        "en",
        "es",
        "pt",
        "vi",
        "zh",
        "hi",
        "ar",
        "bn",
        "fr",
        "de",
        "id",
        "ja",
        "ko",
        "ru",
        "tr",
        "uk",
        "fa",
        "ur",
        "it",
        "th",
    )
)
GLOBAL_CHAT_CHANNEL_CODES = frozenset(
    channel.code for channel in GLOBAL_CHAT_CHANNELS
)


def normalize_global_chat_channel(value: object) -> str | None:
    """Return one supported base-language code, or no selection."""
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace("_", "-").split("-", 1)[0]
    return normalized if normalized in GLOBAL_CHAT_CHANNEL_CODES else None


def recommended_global_chat_channel(locale: object) -> str | None:
    """Return the channel matching an installed UI locale when available."""
    return normalize_global_chat_channel(locale)


def ordered_global_chat_channels(locale: object) -> tuple[GlobalChatChannel, ...]:
    """Place the current UI language first without changing registry order."""
    recommended = recommended_global_chat_channel(locale)
    if recommended is None:
        return GLOBAL_CHAT_CHANNELS
    return tuple(
        sorted(
            GLOBAL_CHAT_CHANNELS,
            key=lambda channel: channel.code != recommended,
        )
    )
