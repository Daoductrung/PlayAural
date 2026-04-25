"""Canonical backend game category identifiers.

Categories are metadata for server-side organization and future extension.
They are not currently exposed as user-facing menu sections.
"""

CATEGORY_CARDS = "cards"
CATEGORY_DICE = "dice"
CATEGORY_BOARD = "board"
CATEGORY_POKER = "poker"
CATEGORY_ARCADE = "arcade"
CATEGORY_MISC = "misc"

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
