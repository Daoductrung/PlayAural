"""Card definitions and deck management for Mile by Mile."""

from dataclasses import dataclass, field
from enum import Enum
import random

from mashumaro.mixins.json import DataClassJSONMixin


class CardType(str, Enum):
    """Card type enumeration."""

    DISTANCE = "distance"
    HAZARD = "hazard"
    REMEDY = "remedy"
    SAFETY = "safety"
    SPECIAL = "special"


class HazardType(str, Enum):
    """Hazard card types."""

    OUT_OF_GAS = "out_of_gas"
    FLAT_TIRE = "flat_tire"
    ACCIDENT = "accident"
    SPEED_LIMIT = "speed_limit"
    STOP = "stop"


class RemedyType(str, Enum):
    """Remedy card types."""

    GASOLINE = "gasoline"
    SPARE_TIRE = "spare_tire"
    REPAIRS = "repairs"
    END_OF_LIMIT = "end_of_limit"
    ROLL = "roll"  # Green Light


class SafetyType(str, Enum):
    """Safety card types."""

    EXTRA_TANK = "extra_tank"
    PUNCTURE_PROOF = "puncture_proof"
    DRIVING_ACE = "driving_ace"
    RIGHT_OF_WAY = "right_of_way"


# Mapping: hazard -> remedy that fixes it
HAZARD_TO_REMEDY: dict[str, str] = {
    HazardType.OUT_OF_GAS: RemedyType.GASOLINE,
    HazardType.FLAT_TIRE: RemedyType.SPARE_TIRE,
    HazardType.ACCIDENT: RemedyType.REPAIRS,
    HazardType.SPEED_LIMIT: RemedyType.END_OF_LIMIT,
    HazardType.STOP: RemedyType.ROLL,
}

# Mapping: hazard -> safety that blocks it
HAZARD_TO_SAFETY: dict[str, str] = {
    HazardType.OUT_OF_GAS: SafetyType.EXTRA_TANK,
    HazardType.FLAT_TIRE: SafetyType.PUNCTURE_PROOF,
    HazardType.ACCIDENT: SafetyType.DRIVING_ACE,
    HazardType.SPEED_LIMIT: SafetyType.RIGHT_OF_WAY,
    HazardType.STOP: SafetyType.RIGHT_OF_WAY,
}

# Mapping: safety -> hazard it protects against
SAFETY_TO_HAZARD: dict[str, str] = {
    SafetyType.EXTRA_TANK: HazardType.OUT_OF_GAS,
    SafetyType.PUNCTURE_PROOF: HazardType.FLAT_TIRE,
    SafetyType.DRIVING_ACE: HazardType.ACCIDENT,
    SafetyType.RIGHT_OF_WAY: HazardType.STOP,  # Also protects against speed_limit
}

# Card names for display
CARD_NAMES: dict[str, str] = {
    # Hazards
    HazardType.OUT_OF_GAS: "Out of Gas",
    HazardType.FLAT_TIRE: "Flat Tire",
    HazardType.ACCIDENT: "Accident",
    HazardType.SPEED_LIMIT: "Speed Limit",
    HazardType.STOP: "Stop",
    # Remedies
    RemedyType.GASOLINE: "Gasoline",
    RemedyType.SPARE_TIRE: "Spare Tire",
    RemedyType.REPAIRS: "Repairs",
    RemedyType.END_OF_LIMIT: "End of Limit",
    RemedyType.ROLL: "Green Light",
    # Safeties
    SafetyType.EXTRA_TANK: "Extra Tank",
    SafetyType.PUNCTURE_PROOF: "Puncture Proof",
    SafetyType.DRIVING_ACE: "Driving Ace",
    SafetyType.RIGHT_OF_WAY: "Right of Way",
    # Special
    "false_virtue": "False Virtue",
}


@dataclass
class Card(DataClassJSONMixin):
    """A single card in Mile by Mile."""

    id: int  # Unique ID for this card instance
    card_type: str  # CardType value
    value: str  # Distance value or hazard/remedy/safety type

    @property
    def name(self) -> str:
        """Get the display name for this card."""
        if self.card_type == CardType.DISTANCE:
            return f"{self.value} miles"
        return CARD_NAMES.get(self.value, self.value)

    @property
    def distance(self) -> int:
        """Get distance value (only valid for distance cards)."""
        if self.card_type == CardType.DISTANCE:
            return int(self.value)
        return 0


@dataclass
class Deck(DataClassJSONMixin):
    """A deck of cards with draw and shuffle functionality."""

    cards: list[Card] = field(default_factory=list)
    _next_id: int = 0

    def _create_card(self, card_type: str, value: str) -> Card:
        """Create a card with a unique ID."""
        card = Card(id=self._next_id, card_type=card_type, value=value)
        self._next_id += 1
        return card

    def build_standard_deck(
        self,
        attack_multiplier: int = 1,
        defense_multiplier: int = 1,
        include_karma_cards: bool = False,
    ) -> None:
        """Build a standard Mile by Mile deck."""
        self.cards = []

        # Distance cards (46 total)
        for _ in range(10):
            self.cards.append(self._create_card(CardType.DISTANCE, "25"))
        for _ in range(10):
            self.cards.append(self._create_card(CardType.DISTANCE, "50"))
        for _ in range(10):
            self.cards.append(self._create_card(CardType.DISTANCE, "75"))
        for _ in range(12):
            self.cards.append(self._create_card(CardType.DISTANCE, "100"))
        for _ in range(4):
            self.cards.append(self._create_card(CardType.DISTANCE, "200"))

        # Hazard cards (18 base, can be multiplied)
        for _ in range(3 * attack_multiplier):
            self.cards.append(self._create_card(CardType.HAZARD, HazardType.OUT_OF_GAS))
        for _ in range(3 * attack_multiplier):
            self.cards.append(self._create_card(CardType.HAZARD, HazardType.FLAT_TIRE))
        for _ in range(3 * attack_multiplier):
            self.cards.append(self._create_card(CardType.HAZARD, HazardType.ACCIDENT))
        for _ in range(4 * attack_multiplier):
            self.cards.append(
                self._create_card(CardType.HAZARD, HazardType.SPEED_LIMIT)
            )
        for _ in range(5 * attack_multiplier):
            self.cards.append(self._create_card(CardType.HAZARD, HazardType.STOP))

        # Remedy cards (38 base, can be multiplied)
        for _ in range(6 * defense_multiplier):
            self.cards.append(self._create_card(CardType.REMEDY, RemedyType.GASOLINE))
        for _ in range(6 * defense_multiplier):
            self.cards.append(self._create_card(CardType.REMEDY, RemedyType.SPARE_TIRE))
        for _ in range(6 * defense_multiplier):
            self.cards.append(self._create_card(CardType.REMEDY, RemedyType.REPAIRS))
        for _ in range(6 * defense_multiplier):
            self.cards.append(
                self._create_card(CardType.REMEDY, RemedyType.END_OF_LIMIT)
            )
        for _ in range(14 * defense_multiplier):
            self.cards.append(self._create_card(CardType.REMEDY, RemedyType.ROLL))

        # Safety cards (4 total, always 1 of each)
        self.cards.append(self._create_card(CardType.SAFETY, SafetyType.EXTRA_TANK))
        self.cards.append(self._create_card(CardType.SAFETY, SafetyType.PUNCTURE_PROOF))
        self.cards.append(self._create_card(CardType.SAFETY, SafetyType.DRIVING_ACE))
        self.cards.append(self._create_card(CardType.SAFETY, SafetyType.RIGHT_OF_WAY))

        # Karma rule cards
        if include_karma_cards:
            for _ in range(2):
                self.cards.append(self._create_card(CardType.SPECIAL, "false_virtue"))

    def shuffle(self) -> None:
        """Shuffle the deck using Fisher-Yates."""
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        """Draw a card from the top of the deck."""
        if self.cards:
            return self.cards.pop(0)
        return None

    def draw_non_duplicate(self, hand: list[Card]) -> Card | None:
        """Draw a card that isn't already in the hand (for disallow duplicates mode)."""
        # First try to find a non-duplicate
        for i, card in enumerate(self.cards):
            if not any(
                c.card_type == card.card_type and c.value == card.value for c in hand
            ):
                return self.cards.pop(i)
        # Fall back to normal draw if all are duplicates
        return self.draw()

    def add(self, card: Card) -> None:
        """Add a card to the bottom of the deck."""
        self.cards.append(card)

    def add_all(self, cards: list[Card]) -> None:
        """Add multiple cards to the deck."""
        self.cards.extend(cards)

    def is_empty(self) -> bool:
        """Check if the deck is empty."""
        return len(self.cards) == 0

    def size(self) -> int:
        """Get the number of cards in the deck."""
        return len(self.cards)
