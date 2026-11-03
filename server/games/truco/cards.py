"""Serializable cards and deck helpers for Argentine Truco (Spanish 40-card deck)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ...messages.localization import Localization

SUIT_OROS = "oros"
SUIT_COPAS = "copas"
SUIT_ESPADAS = "espadas"
SUIT_BASTOS = "bastos"
SUITS = (SUIT_OROS, SUIT_COPAS, SUIT_ESPADAS, SUIT_BASTOS)

# The Spanish deck used for Truco has no 8s or 9s.
RANKS = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)
DECK_SIZE = len(SUITS) * len(RANKS)

# Specific cards that outrank their number, from strongest to weakest.
_SPECIAL_POWER = {
    (1, SUIT_ESPADAS): 14,
    (1, SUIT_BASTOS): 13,
    (7, SUIT_ESPADAS): 12,
    (7, SUIT_OROS): 11,
    (1, SUIT_COPAS): 8,
    (1, SUIT_OROS): 8,
    (7, SUIT_COPAS): 4,
    (7, SUIT_BASTOS): 4,
}
_RANK_POWER = {3: 10, 2: 9, 12: 7, 11: 6, 10: 5, 6: 3, 5: 2, 4: 1}


@dataclass
class TrucoCard:
    """One physical card of the Spanish deck."""

    id: int
    rank: int
    suit: str

    @property
    def power(self) -> int:
        """Trick-taking strength; a higher number beats a lower one."""

        special = _SPECIAL_POWER.get((self.rank, self.suit))
        if special is not None:
            return special
        return _RANK_POWER[self.rank]

    @property
    def envido_value(self) -> int:
        """Value of this card when counting envido and flor (figures count zero)."""

        return self.rank if self.rank <= 7 else 0


def build_deck() -> list[TrucoCard]:
    """Return the 40-card deck in a deterministic order."""

    deck: list[TrucoCard] = []
    card_id = 0
    for suit in SUITS:
        for rank in RANKS:
            deck.append(TrucoCard(id=card_id, rank=rank, suit=suit))
            card_id += 1
    return deck


def shuffle(deck: list[TrucoCard]) -> None:
    random.shuffle(deck)


def format_card(card: TrucoCard, locale: str) -> str:
    """Return a localized card name such as "1 of Swords"."""

    suit = Localization.get(locale, f"truco-suit-{card.suit}")
    return Localization.get(locale, "truco-card-name", rank=card.rank, suit=suit)


def sort_key(card: TrucoCard) -> tuple[int, int]:
    """Sort a hand from strongest to weakest, keeping card identity stable."""

    return (-card.power, card.id)
