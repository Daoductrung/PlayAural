"""Canonical game category identifiers and helpers."""

from collections.abc import Iterable

CATEGORY_CARDS = "cards"
CATEGORY_DICE = "dice"
CATEGORY_BOARD = "board"
CATEGORY_POKER = "poker"
CATEGORY_ARCADE = "arcade"
CATEGORY_MISC = "misc"
CATEGORY_FILTER_ALL = "all"

GAME_CATEGORY_ORDER = (
    CATEGORY_CARDS,
    CATEGORY_POKER,
    CATEGORY_DICE,
    CATEGORY_BOARD,
    CATEGORY_ARCADE,
    CATEGORY_MISC,
)

GAME_CATEGORY_IDS = frozenset(
    {
        CATEGORY_CARDS,
        CATEGORY_DICE,
        CATEGORY_BOARD,
        CATEGORY_POKER,
        CATEGORY_ARCADE,
        CATEGORY_MISC,
    }
)


def normalize_category(category: str) -> str:
    """Return a known backend category id, falling back to miscellaneous."""
    return category if category in GAME_CATEGORY_IDS else CATEGORY_MISC


def normalize_categories(categories: Iterable[str] | str | None) -> tuple[str, ...]:
    """Return unique known category ids, preserving order.

    Games currently declare one category through get_category(), but the Play
    menu filter is built on tuples so future games can opt into multiple
    categories without changing filtering or count logic.
    """
    if categories is None:
        return (CATEGORY_MISC,)
    raw_categories = [categories] if isinstance(categories, str) else list(categories)
    normalized: list[str] = []
    for category in raw_categories:
        category_id = normalize_category(str(category))
        if category_id not in normalized:
            normalized.append(category_id)
    return tuple(normalized or (CATEGORY_MISC,))
