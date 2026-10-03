"""Serializable cards and deck helpers for Skip-Bo."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ...messages.localization import Localization

MIN_NUMBER = 1
MAX_NUMBER = 12
NUMBER_COPIES = 12
WILD_COUNT = 24
WILD_VALUE = 0
DECK_SIZE = (MAX_NUMBER * NUMBER_COPIES) + WILD_COUNT


@dataclass
class SkipBoCard:
    """One physical Skip-Bo card; zero represents a wild card."""

    id: int
    value: int

    @property
    def is_wild(self) -> bool:
        return self.value == WILD_VALUE


def build_deck() -> list[SkipBoCard]:
    """Return the current official 168-card deck in a deterministic order."""

    deck: list[SkipBoCard] = []
    card_id = 0
    for value in range(MIN_NUMBER, MAX_NUMBER + 1):
        for _ in range(NUMBER_COPIES):
            deck.append(SkipBoCard(id=card_id, value=value))
            card_id += 1
    for _ in range(WILD_COUNT):
        deck.append(SkipBoCard(id=card_id, value=WILD_VALUE))
        card_id += 1
    return deck


def shuffle(deck: list[SkipBoCard]) -> None:
    random.shuffle(deck)


def format_card(card: SkipBoCard, locale: str, *, wild_as: int | None = None) -> str:
    """Return a localized card label, including a wild's chosen value."""

    if card.is_wild:
        if wild_as is not None:
            return Localization.get(locale, "skipbo-card-wild-as", value=wild_as)
        return Localization.get(locale, "skipbo-card-wild")
    return Localization.get(locale, "skipbo-card-number", value=card.value)


def sort_key(card: SkipBoCard) -> tuple[int, int]:
    """Sort numbered cards first and wilds last, retaining stable card identity."""

    return (MAX_NUMBER + 1 if card.is_wild else card.value, card.id)
