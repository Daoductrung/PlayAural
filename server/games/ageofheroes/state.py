"""Game state definitions for Age of Heroes."""

from dataclasses import dataclass, field
from enum import Enum

from mashumaro.mixins.json import DataClassJSONMixin

from .cards import SpecialResourceType, ResourceType


class Tribe(str, Enum):
    """Available tribes in the game."""

    EGYPTIANS = "egyptians"
    ROMANS = "romans"
    GREEKS = "greeks"
    BABYLONIANS = "babylonians"
    CELTS = "celts"
    CHINESE = "chinese"


class GamePhase(str, Enum):
    """Game phases."""

    SETUP = "setup"  # Dice roll for turn order
    PREPARE = "prepare"  # Play events, discard disasters
    FAIR = "fair"  # Trading phase
    PLAY = "play"  # Main game (Tax/Construction/War/Nothing)
    GAME_OVER = "game_over"


class PlaySubPhase(str, Enum):
    """Sub-phases within the PLAY phase."""

    DRAW_CARD = "draw_card"  # Player draws a card
    SELECT_ACTION = "select_action"  # Player chooses action
    TAX_COLLECTION = "tax_collection"  # Performing tax collection
    CONSTRUCTION = "construction"  # Building things
    ROAD_TARGET = "road_target"  # Selecting which neighbor to build road to
    ROAD_PERMISSION = "road_permission"  # Neighbor approving/denying road request
    WAR_DECLARE = "war_declare"  # Selecting war target and goal
    WAR_PREPARE_ATTACKER = "war_prepare_attacker"  # Attacker selecting forces
    WAR_PREPARE_DEFENDER = "war_prepare_defender"  # Defender selecting forces
    WAR_PREPARE = "war_prepare"  # Both sides selecting armies (bot handling)
    WAR_BATTLE = "war_battle"  # Dice rolling combat
    DISCARD_EXCESS = "discard_excess"  # Discard to max hand size
    DISASTER_TARGET = "disaster_target"  # Selecting target for disaster card (Earthquake/Eruption)


class ActionType(str, Enum):
    """Main turn actions in the play phase."""

    TAX_COLLECTION = "tax_collection"
    CONSTRUCTION = "construction"
    WAR = "war"
    DO_NOTHING = "do_nothing"


class WarGoal(str, Enum):
    """War objectives."""

    CONQUEST = "conquest"  # Take a city from opponent
    PLUNDER = "plunder"  # Steal cards from opponent's hand
    DESTRUCTION = "destruction"  # Destroy opponent's monument progress


class BuildingType(str, Enum):
    """Types of buildings/units that can be constructed."""

    ARMY = "army"
    FORTRESS = "fortress"
    GENERAL = "general"
    ROAD = "road"
    CITY = "city"


# Building costs: building -> list of required resources
BUILDING_COSTS: dict[str, list[str]] = {
    BuildingType.ARMY: [ResourceType.IRON, ResourceType.GRAIN, ResourceType.GRAIN],
    BuildingType.FORTRESS: [
        ResourceType.IRON,
        ResourceType.WOOD,
        ResourceType.STONE,
    ],
    BuildingType.GENERAL: [ResourceType.IRON, ResourceType.GOLD],
    BuildingType.ROAD: [ResourceType.STONE, ResourceType.STONE],
    BuildingType.CITY: [ResourceType.WOOD, ResourceType.WOOD, ResourceType.STONE],
}

# Building name localization keys
BUILDING_NAME_KEYS: dict[str, str] = {
    BuildingType.ARMY: "ageofheroes-building-army",
    BuildingType.FORTRESS: "ageofheroes-building-fortress",
    BuildingType.GENERAL: "ageofheroes-building-general",
    BuildingType.ROAD: "ageofheroes-building-road",
    BuildingType.CITY: "ageofheroes-building-city",
}

# Tribe to special resource mapping
TRIBE_SPECIAL_RESOURCE: dict[str, str] = {
    Tribe.EGYPTIANS: SpecialResourceType.LIMESTONE,
    Tribe.ROMANS: SpecialResourceType.CONCRETE,
    Tribe.GREEKS: SpecialResourceType.MARBLE,
    Tribe.BABYLONIANS: SpecialResourceType.BRICKS,
    Tribe.CELTS: SpecialResourceType.SANDSTONE,
    Tribe.CHINESE: SpecialResourceType.GRANITE,
}

# Tribe name localization keys
TRIBE_NAME_KEYS: dict[str, str] = {
    Tribe.EGYPTIANS: "ageofheroes-tribe-egyptians",
    Tribe.ROMANS: "ageofheroes-tribe-romans",
    Tribe.GREEKS: "ageofheroes-tribe-greeks",
    Tribe.BABYLONIANS: "ageofheroes-tribe-babylonians",
    Tribe.CELTS: "ageofheroes-tribe-celts",
    Tribe.CHINESE: "ageofheroes-tribe-chinese",
}

# Action name localization keys
ACTION_NAME_KEYS: dict[str, str] = {
    ActionType.TAX_COLLECTION: "ageofheroes-action-tax-collection",
    ActionType.CONSTRUCTION: "ageofheroes-action-construction",
    ActionType.WAR: "ageofheroes-action-war",
    ActionType.DO_NOTHING: "ageofheroes-action-do-nothing",
}

# War goal localization keys
WAR_GOAL_KEYS: dict[str, str] = {
    WarGoal.CONQUEST: "ageofheroes-war-conquest",
    WarGoal.PLUNDER: "ageofheroes-war-plunder",
    WarGoal.DESTRUCTION: "ageofheroes-war-destruction",
}

# Default supply limits
DEFAULT_ARMY_SUPPLY = 12
DEFAULT_CITY_SUPPLY = 12
DEFAULT_FORTRESS_SUPPLY = 9
DEFAULT_GENERAL_SUPPLY = 6
DEFAULT_ROAD_SUPPLY = 6


@dataclass
class TribeState(DataClassJSONMixin):
    """Per-player tribe state tracking.

    Similar to RaceState in Mile by Mile - tracks all state for a player's tribe.
    """

    tribe: str  # Tribe enum value

    # Buildings/Units
    cities: int = 1  # Start with 1 city
    armies: int = 1  # Start with 1 army
    generals: int = 0
    fortresses: int = 0

    # Monument progress (0-5 special resources collected)
    monument_progress: int = 0

    # Road connections (to adjacent players in circular seating)
    road_left: bool = False
    road_right: bool = False

    # Temporary states
    earthquaked_armies: int = 0  # Armies disabled by earthquake (recover next turn)
    returning_armies: int = 0  # Armies returning from war (arrive next turn)
    returning_generals: int = 0  # Generals returning from war

    def get_available_armies(self) -> int:
        """Get the number of armies available for combat."""
        return max(0, self.armies - self.earthquaked_armies - self.returning_armies)

    def get_available_generals(self) -> int:
        """Get the number of generals available for combat."""
        return max(0, self.generals - self.returning_generals)

    def has_road_to_neighbor(self, direction: str) -> bool:
        """Check if there's a road to a neighbor."""
        if direction == "left":
            return self.road_left
        elif direction == "right":
            return self.road_right
        return False

    def get_road_count(self) -> int:
        """Get total number of roads built."""
        count = 0
        if self.road_left:
            count += 1
        if self.road_right:
            count += 1
        return count

    def is_eliminated(self) -> bool:
        """Check if this tribe has been eliminated (no cities, no cards)."""
        return self.cities == 0

    def get_special_resource(self) -> str:
        """Get the special resource type for this tribe's monument."""
        return TRIBE_SPECIAL_RESOURCE.get(self.tribe, SpecialResourceType.LIMESTONE)

    def process_end_of_turn(self) -> tuple[int, int, int]:
        """Process end of turn effects. Returns (armies_returned, generals_returned, earthquaked_recovered)."""
        armies_back = self.returning_armies
        generals_back = self.returning_generals
        earthquaked_recovered = self.earthquaked_armies

        # Return armies and generals from war
        self.returning_armies = 0
        self.returning_generals = 0

        # Recover from earthquake
        self.earthquaked_armies = 0

        return armies_back, generals_back, earthquaked_recovered


@dataclass
class WarState(DataClassJSONMixin):
    """State tracking for an ongoing war."""

    attacker_index: int = -1  # Player index of attacker
    defender_index: int = -1  # Player index of defender
    goal: str = ""  # WarGoal value

    # Committed forces
    attacker_armies: int = 0
    attacker_generals: int = 0
    attacker_heroes: int = 0  # Hero cards being used as armies
    attacker_hero_generals: int = 0  # Hero cards being used as generals

    defender_armies: int = 0
    defender_generals: int = 0
    defender_heroes: int = 0
    defender_hero_generals: int = 0

    # Battle progress
    attacker_prepared: bool = False
    defender_prepared: bool = False
    battle_in_progress: bool = False

    # Current round dice rolls (for interactive rolling)
    attacker_roll: int = 0  # Current round roll from attacker
    defender_roll: int = 0  # Current round roll from defender

    # Dice rolls (for display/replay)
    attacker_dice: list[int] = field(default_factory=list)
    defender_dice: list[int] = field(default_factory=list)

    # Olympics cancellation
    cancelled_by_olympics: bool = False

    def get_attacker_total_armies(self) -> int:
        """Get total army strength for attacker."""
        return self.attacker_armies + self.attacker_heroes

    def get_defender_total_armies(self) -> int:
        """Get total army strength for defender."""
        return self.defender_armies + self.defender_heroes

    def get_attacker_total_generals(self) -> int:
        """Get total general count for attacker."""
        return self.attacker_generals + self.attacker_hero_generals

    def get_defender_total_generals(self) -> int:
        """Get total general count for defender (including fortress bonus)."""
        return self.defender_generals + self.defender_hero_generals

    def is_both_prepared(self) -> bool:
        """Check if both sides have prepared their forces."""
        return self.attacker_prepared and self.defender_prepared

    def is_both_rolled(self) -> bool:
        """Check if both sides have rolled for the current round."""
        return self.attacker_roll > 0 and self.defender_roll > 0

    def reset_round_rolls(self) -> None:
        """Reset rolls for a new round."""
        self.attacker_roll = 0
        self.defender_roll = 0

    def reset(self) -> None:
        """Reset war state for a new war."""
        self.attacker_index = -1
        self.defender_index = -1
        self.goal = ""
        self.attacker_armies = 0
        self.attacker_generals = 0
        self.attacker_heroes = 0
        self.attacker_hero_generals = 0
        self.defender_armies = 0
        self.defender_generals = 0
        self.defender_heroes = 0
        self.defender_hero_generals = 0
        self.attacker_prepared = False
        self.defender_prepared = False
        self.battle_in_progress = False
        self.attacker_roll = 0
        self.defender_roll = 0
        self.attacker_dice = []
        self.defender_dice = []
        self.cancelled_by_olympics = False


@dataclass
class TradeOffer(DataClassJSONMixin):
    """A trade offer in the auction phase."""

    player_index: int  # Who is offering
    card_index: int  # Index of card in their hand being offered
    wanted_type: str | None = None  # CardType wanted (or None for "any")
    wanted_subtype: str | None = None  # Specific subtype wanted (or None for "any")


def get_tribe_name(tribe: str, locale: str) -> str:
    """Get the localized name for a tribe."""
    from ...messages.localization import Localization

    key = TRIBE_NAME_KEYS.get(tribe, "")
    return Localization.get(locale, key) if key else tribe


def get_building_name(building: str, locale: str) -> str:
    """Get the localized name for a building type."""
    from ...messages.localization import Localization

    key = BUILDING_NAME_KEYS.get(building, "")
    return Localization.get(locale, key) if key else building


def get_action_name(action: str, locale: str) -> str:
    """Get the localized name for an action type."""
    from ...messages.localization import Localization

    key = ACTION_NAME_KEYS.get(action, "")
    return Localization.get(locale, key) if key else action


def get_war_goal_name(goal: str, locale: str) -> str:
    """Get the localized name for a war goal."""
    from ...messages.localization import Localization

    key = WAR_GOAL_KEYS.get(goal, "")
    return Localization.get(locale, key) if key else goal
