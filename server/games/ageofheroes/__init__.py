"""Age of Heroes game module.

A civilization-building card game for 2-6 players with resource management,
construction, trading, and dice-based combat.
"""

from .game import AgeOfHeroesGame, AgeOfHeroesPlayer, AgeOfHeroesOptions
from .cards import (
    Card,
    Deck,
    CardType,
    ResourceType,
    SpecialResourceType,
    EventType,
)
from .state import (
    Tribe,
    TribeState,
    WarState,
    TradeOffer,
    GamePhase,
    PlaySubPhase,
    ActionType,
    WarGoal,
    BuildingType,
    BUILDING_COSTS,
    TRIBE_SPECIAL_RESOURCE,
)

__all__ = [
    # Main game classes
    "AgeOfHeroesGame",
    "AgeOfHeroesPlayer",
    "AgeOfHeroesOptions",
    # Card system
    "Card",
    "Deck",
    "CardType",
    "ResourceType",
    "SpecialResourceType",
    "EventType",
    # State management
    "Tribe",
    "TribeState",
    "WarState",
    "TradeOffer",
    "GamePhase",
    "PlaySubPhase",
    "ActionType",
    "WarGoal",
    "BuildingType",
    # Constants
    "BUILDING_COSTS",
    "TRIBE_SPECIAL_RESOURCE",
]
