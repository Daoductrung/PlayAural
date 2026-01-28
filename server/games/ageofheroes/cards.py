"""Card definitions and deck management for Age of Heroes."""

from dataclasses import dataclass, field
from enum import Enum
import random

from mashumaro.mixins.json import DataClassJSONMixin


class CardType(str, Enum):
    """Card type enumeration."""

    RESOURCE = "resource"  # Standard resources (Iron, Wood, Grain, Stone, Gold)
    SPECIAL = "special"  # Monument resources (Limestone, Concrete, etc.)
    EVENT = "event"  # Events (Population Growth, Earthquake, etc.)


class ResourceType(str, Enum):
    """Standard resource types."""

    IRON = "iron"
    WOOD = "wood"
    GRAIN = "grain"
    STONE = "stone"
    GOLD = "gold"


class SpecialResourceType(str, Enum):
    """Special resources for monument building (one per tribe)."""

    LIMESTONE = "limestone"  # Egyptians
    CONCRETE = "concrete"  # Romans
    MARBLE = "marble"  # Greeks
    BRICKS = "bricks"  # Babylonians
    SANDSTONE = "sandstone"  # Celts
    GRANITE = "granite"  # Chinese


class EventType(str, Enum):
    """Event card types."""

    POPULATION_GROWTH = "population_growth"  # Build a free city
    EARTHQUAKE = "earthquake"  # Disable armies for a turn
    ERUPTION = "eruption"  # Lose a city
    HUNGER = "hunger"  # Discard (disaster)
    BARBARIANS = "barbarians"  # Discard (disaster)
    OLYMPICS = "olympics"  # Cancel a war declaration
    HERO = "hero"  # Acts as army or general in combat
    FORTUNE = "fortune"  # Reroll dice in combat


# Mapping from card subtype to localization key
CARD_NAME_KEYS: dict[str, str] = {
    # Resources
    ResourceType.IRON: "ageofheroes-resource-iron",
    ResourceType.WOOD: "ageofheroes-resource-wood",
    ResourceType.GRAIN: "ageofheroes-resource-grain",
    ResourceType.STONE: "ageofheroes-resource-stone",
    ResourceType.GOLD: "ageofheroes-resource-gold",
    # Special resources
    SpecialResourceType.LIMESTONE: "ageofheroes-special-limestone",
    SpecialResourceType.CONCRETE: "ageofheroes-special-concrete",
    SpecialResourceType.MARBLE: "ageofheroes-special-marble",
    SpecialResourceType.BRICKS: "ageofheroes-special-bricks",
    SpecialResourceType.SANDSTONE: "ageofheroes-special-sandstone",
    SpecialResourceType.GRANITE: "ageofheroes-special-granite",
    # Events
    EventType.POPULATION_GROWTH: "ageofheroes-event-population-growth",
    EventType.EARTHQUAKE: "ageofheroes-event-earthquake",
    EventType.ERUPTION: "ageofheroes-event-eruption",
    EventType.HUNGER: "ageofheroes-event-hunger",
    EventType.BARBARIANS: "ageofheroes-event-barbarians",
    EventType.OLYMPICS: "ageofheroes-event-olympics",
    EventType.HERO: "ageofheroes-event-hero",
    EventType.FORTUNE: "ageofheroes-event-fortune",
}

# Events that must be played/discarded during preparation phase
MANDATORY_EVENTS = {
    EventType.POPULATION_GROWTH,
    EventType.EARTHQUAKE,
    EventType.ERUPTION,
    EventType.HUNGER,
    EventType.BARBARIANS,
}

# Disaster events (negative effects)
DISASTER_EVENTS = {
    EventType.EARTHQUAKE,
    EventType.ERUPTION,
    EventType.HUNGER,
    EventType.BARBARIANS,
}

# Beneficial events (can be kept and used strategically)
BENEFICIAL_EVENTS = {
    EventType.POPULATION_GROWTH,
    EventType.OLYMPICS,
    EventType.HERO,
    EventType.FORTUNE,
}


@dataclass
class Card(DataClassJSONMixin):
    """A single card in Age of Heroes."""

    id: int  # Unique ID for this card instance
    card_type: str  # CardType value
    subtype: str  # ResourceType, SpecialResourceType, or EventType value

    def get_name_key(self) -> str:
        """Get the localization key for this card's name."""
        return CARD_NAME_KEYS.get(self.subtype, self.subtype)

    def is_resource(self) -> bool:
        """Check if this is a standard resource card."""
        return self.card_type == CardType.RESOURCE

    def is_special_resource(self) -> bool:
        """Check if this is a special monument resource."""
        return self.card_type == CardType.SPECIAL

    def is_event(self) -> bool:
        """Check if this is an event card."""
        return self.card_type == CardType.EVENT

    def is_mandatory_event(self) -> bool:
        """Check if this event must be played/discarded in preparation phase."""
        return self.card_type == CardType.EVENT and self.subtype in MANDATORY_EVENTS

    def is_disaster(self) -> bool:
        """Check if this is a disaster event."""
        return self.card_type == CardType.EVENT and self.subtype in DISASTER_EVENTS

    def is_beneficial_event(self) -> bool:
        """Check if this is a beneficial event."""
        return self.card_type == CardType.EVENT and self.subtype in BENEFICIAL_EVENTS


@dataclass
class Deck(DataClassJSONMixin):
    """A deck of cards with draw and shuffle functionality."""

    cards: list[Card] = field(default_factory=list)
    _next_id: int = 0

    def _create_card(self, card_type: str, subtype: str) -> Card:
        """Create a card with a unique ID."""
        card = Card(id=self._next_id, card_type=card_type, subtype=subtype)
        self._next_id += 1
        return card

    def build_standard_deck(self, num_players: int = 6) -> None:
        """Build a standard Age of Heroes deck.

        The deck composition matches the original Pascal version (108 cards):
        - 12 of each standard resource (Iron, Wood, Grain, Stone) = 48 cards
        - 6 Gold cards
        - 6 of each special resource (all 6 types) = 36 cards
        - Event cards (18 total)
        """
        self.cards = []

        # Standard resources (Iron, Wood, Grain, Stone) - 12 of each = 48 cards
        standard_resources = [
            ResourceType.IRON,
            ResourceType.WOOD,
            ResourceType.GRAIN,
            ResourceType.STONE,
        ]
        for resource in standard_resources:
            for _ in range(12):
                self.cards.append(self._create_card(CardType.RESOURCE, resource))

        # Gold - 6 cards (separate from other standard resources)
        for _ in range(6):
            self.cards.append(self._create_card(CardType.RESOURCE, ResourceType.GOLD))

        # Special resources - only include those for tribes in the game
        # 6 copies each (for monument completion requiring 5)
        from .state import Tribe, TRIBE_SPECIAL_RESOURCE

        tribes = list(Tribe)[:num_players]
        for tribe in tribes:
            special = TRIBE_SPECIAL_RESOURCE[tribe]
            for _ in range(6):
                self.cards.append(self._create_card(CardType.SPECIAL, special))

        # Event cards (18 total)
        # Population Growth - 2 copies
        for _ in range(2):
            self.cards.append(
                self._create_card(CardType.EVENT, EventType.POPULATION_GROWTH)
            )

        # Earthquake - 2 copies
        for _ in range(2):
            self.cards.append(self._create_card(CardType.EVENT, EventType.EARTHQUAKE))

        # Eruption - 2 copies
        for _ in range(2):
            self.cards.append(self._create_card(CardType.EVENT, EventType.ERUPTION))

        # Hunger - 2 copies
        for _ in range(2):
            self.cards.append(self._create_card(CardType.EVENT, EventType.HUNGER))

        # Barbarians - 3 copies
        for _ in range(3):
            self.cards.append(self._create_card(CardType.EVENT, EventType.BARBARIANS))

        # Olympics - 2 copies
        for _ in range(2):
            self.cards.append(self._create_card(CardType.EVENT, EventType.OLYMPICS))

        # Hero - 3 copies
        for _ in range(3):
            self.cards.append(self._create_card(CardType.EVENT, EventType.HERO))

        # Fortune - 2 copies
        for _ in range(2):
            self.cards.append(self._create_card(CardType.EVENT, EventType.FORTUNE))

    def shuffle(self) -> None:
        """Shuffle the deck using Fisher-Yates."""
        random.shuffle(self.cards)

    def draw(self, count: int = 1) -> list[Card]:
        """Draw cards from the top of the deck."""
        drawn = []
        for _ in range(count):
            if self.cards:
                drawn.append(self.cards.pop(0))
        return drawn

    def draw_one(self) -> Card | None:
        """Draw a single card from the top of the deck."""
        if self.cards:
            return self.cards.pop(0)
        return None

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

    def count_by_type(self, card_type: str, subtype: str | None = None) -> int:
        """Count cards of a specific type in the deck."""
        count = 0
        for card in self.cards:
            if card.card_type == card_type:
                if subtype is None or card.subtype == subtype:
                    count += 1
        return count


def get_card_name(card: Card, locale: str) -> str:
    """Get the localized name for a card."""
    from ...messages.localization import Localization

    return Localization.get(locale, card.get_name_key())


def read_cards(cards: list[Card], locale: str) -> str:
    """Get a comma-separated list of localized card names."""
    if not cards:
        return ""
    names = [get_card_name(card, locale) for card in cards]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"
