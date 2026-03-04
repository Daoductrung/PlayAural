"""
Card and state definitions for Coup.
"""

from dataclasses import dataclass, field
from enum import Enum


class Character(str, Enum):
    DUKE = "duke"
    ASSASSIN = "assassin"
    CAPTAIN = "captain"
    AMBASSADOR = "ambassador"
    CONTESSA = "contessa"


@dataclass
class Card:
    """A Coup character card."""

    character: Character
    is_revealed: bool = False


@dataclass
class Deck:
    """The Coup deck."""

    cards: list[Card] = field(default_factory=list)

    def build_standard_deck(self) -> None:
        """Build a standard deck with 3 of each character."""
        self.cards = []
        for char in Character:
            for _ in range(3):
                self.cards.append(Card(character=char))

    def shuffle(self) -> None:
        """Shuffle the deck."""
        import random

        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        """Draw a card from the deck."""
        if not self.cards:
            return None
        return self.cards.pop()

    def add(self, card: Card) -> None:
        """Return a card to the deck."""
        self.cards.append(card)

    def is_empty(self) -> bool:
        """Check if the deck is empty."""
        return len(self.cards) == 0
