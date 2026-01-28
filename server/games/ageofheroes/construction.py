"""Construction system for Age of Heroes."""

from __future__ import annotations
from typing import TYPE_CHECKING

from .cards import Card, CardType, ResourceType, get_card_name
from .state import (
    BuildingType,
    BUILDING_COSTS,
    PlaySubPhase,
    get_building_name,
)

if TYPE_CHECKING:
    from .game import AgeOfHeroesGame, AgeOfHeroesPlayer


def get_affordable_buildings(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer
) -> list[str]:
    """Get list of buildings the player can afford to build."""
    if not player.tribe_state:
        return []

    affordable = []

    for building_type in BuildingType:
        if can_build(game, player, building_type):
            affordable.append(building_type)

    return affordable


def can_build(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, building_type: str
) -> bool:
    """Check if a player can build a specific building."""
    if not player.tribe_state:
        return False

    # Check supply availability
    if not has_supply(game, player, building_type):
        return False

    # Check if player has required resources
    required = BUILDING_COSTS.get(building_type, [])
    if not has_resources(player, required):
        return False

    # Special checks for roads
    if building_type == BuildingType.ROAD:
        # Check if there's a valid neighbor to connect to
        if not has_road_target(game, player):
            return False

    return True


def has_supply(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, building_type: str
) -> bool:
    """Check if the building supply has available units."""
    if building_type == BuildingType.ARMY:
        return game.army_supply > 0
    elif building_type == BuildingType.CITY:
        return game.city_supply > 0
    elif building_type == BuildingType.FORTRESS:
        return game.fortress_supply > 0
    elif building_type == BuildingType.GENERAL:
        return game.general_supply > 0
    elif building_type == BuildingType.ROAD:
        return game.road_supply > 0
    return False


def has_resources(player: AgeOfHeroesPlayer, required: list[str]) -> bool:
    """Check if a player has the required resource cards.

    Gold acts as a wildcard and can substitute for any other resource.
    """
    # Count available resources in hand
    resource_counts: dict[str, int] = {}
    for card in player.hand:
        if card.card_type == CardType.RESOURCE:
            resource_counts[card.subtype] = resource_counts.get(card.subtype, 0) + 1

    # Check if we have enough of each required resource
    required_counts: dict[str, int] = {}
    for resource in required:
        required_counts[resource] = required_counts.get(resource, 0) + 1

    # Track how much gold we need to use as wildcard
    gold_needed = 0
    gold_available = resource_counts.get(ResourceType.GOLD, 0)

    for resource, count in required_counts.items():
        available = resource_counts.get(resource, 0)
        if available < count:
            # Need to use gold to make up the difference
            shortfall = count - available
            gold_needed += shortfall

    # Check if we have enough gold to cover shortfalls
    # (but don't double-count gold if gold itself is required)
    if gold_needed > gold_available:
        return False

    return True


def has_road_target(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> bool:
    """Check if there's a valid neighbor to build a road to."""
    if not player.tribe_state:
        return False

    active_players = game.get_active_players()
    player_index = active_players.index(player)

    # Check left neighbor
    if not player.tribe_state.road_left:
        left_index = (player_index - 1) % len(active_players)
        left_player = active_players[left_index]
        if left_player != player and hasattr(left_player, "tribe_state"):
            if left_player.tribe_state and not left_player.tribe_state.road_right:
                return True

    # Check right neighbor
    if not player.tribe_state.road_right:
        right_index = (player_index + 1) % len(active_players)
        right_player = active_players[right_index]
        if right_player != player and hasattr(right_player, "tribe_state"):
            if right_player.tribe_state and not right_player.tribe_state.road_left:
                return True

    return False


def get_road_targets(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer
) -> list[tuple[int, str]]:
    """Get list of valid road targets (player_index, direction).

    Excludes targets that have declined during this construction action.
    In 2-player games, left and right neighbors are the same, so only one is returned.
    """
    if not player.tribe_state:
        return []

    targets = []
    active_players = game.get_active_players()
    player_index = active_players.index(player)

    # Check left neighbor
    if not player.tribe_state.road_left:
        left_index = (player_index - 1) % len(active_players)
        left_player = active_players[left_index]
        if (
            left_player != player
            and hasattr(left_player, "tribe_state")
            and left_player.tribe_state
            and not left_player.tribe_state.road_right
            and left_index not in player.declined_road_targets
        ):
            targets.append((left_index, "left"))

    # Check right neighbor
    if not player.tribe_state.road_right:
        right_index = (player_index + 1) % len(active_players)
        right_player = active_players[right_index]
        # Skip if this is the same player as left neighbor (2-player game)
        # and we already added them
        if (
            right_player != player
            and hasattr(right_player, "tribe_state")
            and right_player.tribe_state
            and not right_player.tribe_state.road_left
            and right_index not in player.declined_road_targets
            and not any(target[0] == right_index for target in targets)
        ):
            targets.append((right_index, "right"))

    return targets


def spend_resources(
    player: AgeOfHeroesPlayer, required: list[str], discard_pile: list[Card]
) -> list[Card]:
    """Remove resource cards from player's hand. Returns the spent cards.

    Gold acts as a wildcard and can substitute for any other resource.
    """
    spent = []
    required_counts: dict[str, int] = {}
    for resource in required:
        required_counts[resource] = required_counts.get(resource, 0) + 1

    for resource, count in required_counts.items():
        for _ in range(count):
            # First, try to find the exact resource
            found = False
            for i, card in enumerate(player.hand):
                if card.card_type == CardType.RESOURCE and card.subtype == resource:
                    removed = player.hand.pop(i)
                    spent.append(removed)
                    discard_pile.append(removed)
                    found = True
                    break

            # If not found, use Gold as wildcard
            if not found:
                for i, card in enumerate(player.hand):
                    if card.card_type == CardType.RESOURCE and card.subtype == ResourceType.GOLD:
                        removed = player.hand.pop(i)
                        spent.append(removed)
                        discard_pile.append(removed)
                        break

    return spent


def build(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, building_type: str
) -> bool:
    """Build a building, spending resources and updating supply."""
    if not can_build(game, player, building_type):
        return False

    if not player.tribe_state:
        return False

    # Spend resources
    required = BUILDING_COSTS.get(building_type, [])
    spend_resources(player, required, game.discard_pile)

    # Update supply and player state
    if building_type == BuildingType.ARMY:
        game.army_supply -= 1
        player.tribe_state.armies += 1
    elif building_type == BuildingType.CITY:
        game.city_supply -= 1
        player.tribe_state.cities += 1
    elif building_type == BuildingType.FORTRESS:
        game.fortress_supply -= 1
        player.tribe_state.fortresses += 1
    elif building_type == BuildingType.GENERAL:
        game.general_supply -= 1
        player.tribe_state.generals += 1
    elif building_type == BuildingType.ROAD:
        # Road requires special handling - need permission from neighbor
        game.road_supply -= 1
        # The actual road connection is made when permission is granted
        return True

    # Play build sound
    game.play_sound("game_ageofheroes/build.ogg")

    # Announce
    user = game.get_user(player)
    if user:
        building_name = get_building_name(building_type, user.locale)
        article = "an" if building_type == BuildingType.ARMY else "a"
        user.speak_l("ageofheroes-construction-done-you", building=building_name, article=article)

    for p in game.players:
        if p != player:
            other_user = game.get_user(p)
            if other_user:
                building_name = get_building_name(building_type, other_user.locale)
                article = "an" if building_type == BuildingType.ARMY else "a"
                other_user.speak_l(
                    "ageofheroes-construction-done",
                    player=player.name,
                    building=building_name,
                    article=article,
                )

    return True


def build_road(
    game: AgeOfHeroesGame,
    builder: AgeOfHeroesPlayer,
    target_index: int,
    direction: str,
) -> bool:
    """Complete road building between two players."""
    if not builder.tribe_state:
        return False

    active_players = game.get_active_players()
    if target_index < 0 or target_index >= len(active_players):
        return False

    target = active_players[target_index]
    if not hasattr(target, "tribe_state") or not target.tribe_state:
        return False

    # Set road connections
    if direction == "left":
        builder.tribe_state.road_left = True
        target.tribe_state.road_right = True
    else:
        builder.tribe_state.road_right = True
        target.tribe_state.road_left = True

    # Announce
    game.play_sound("game_ageofheroes/build.ogg")

    builder_tribe = get_building_name(builder.tribe_state.tribe, "en")
    target_tribe = get_building_name(target.tribe_state.tribe, "en")

    game.broadcast_l(
        "ageofheroes-road-built", tribe1=builder.name, tribe2=target.name
    )

    return True


def get_construction_menu_items(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, locale: str
) -> list[tuple[str, str]]:
    """Get menu items for construction selection.

    Returns list of (building_type, label) tuples.
    """
    items = []

    for building_type in BuildingType:
        if can_build(game, player, building_type):
            building_name = get_building_name(building_type, locale)

            # Add cost info
            required = BUILDING_COSTS.get(building_type, [])
            cost_parts = []
            for resource in set(required):
                count = required.count(resource)
                from ...messages.localization import Localization

                resource_name = Localization.get(
                    locale, f"ageofheroes-resource-{resource}"
                )
                if count > 1:
                    cost_parts.append(f"{count}x {resource_name}")
                else:
                    cost_parts.append(resource_name)

            cost_str = " + ".join(cost_parts)
            label = f"{building_name} ({cost_str})"
            items.append((building_type, label))

    return items


def execute_single_build(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, building_type: str, auto_road: bool = False
) -> bool:
    """Execute building a single item. Returns True if successful, False otherwise.

    Args:
        game: The game instance
        player: The player building
        building_type: Type of building to construct
        auto_road: If True, automatically build road to first target (for bots)

    Returns:
        True if building was successful, False if it failed or victory occurred
    """
    # Import here to avoid circular import at module level
    from ...game_utils.bot_helper import BotHelper

    if not player.tribe_state:
        return False

    # Handle road building specially (needs neighbor selection/permission)
    if building_type == BuildingType.ROAD:
        targets = get_road_targets(game, player)
        if not targets:
            return False

        if auto_road:
            # Bot mode: Select first target and send permission request
            target_index, direction = targets[0]
            active_players = game.get_active_players()
            builder_index = active_players.index(player)

            # Store the road request
            player.pending_road_targets = targets
            game.road_request_from = builder_index
            game.road_request_to = target_index

            # Enter road permission subphase
            game.sub_phase = PlaySubPhase.ROAD_PERMISSION
            game.rebuild_all_menus()

            # Notify target player
            if target_index < len(active_players):
                target = active_players[target_index]
                target_user = game.get_user(target)
                if target_user:
                    target_user.speak_l("ageofheroes-road-request-received", requester=player.name)

                # If target is also a bot, have them auto-respond
                if target.is_bot:
                    BotHelper.jolt_bot(target, ticks=5)

            # Road request sent, waiting for response
            return True
        else:
            # Human mode: Return False to indicate road needs selection menu
            # (caller should handle this)
            return False

    # Build the selected building
    if not build(game, player, building_type):
        return False

    # Check for city victory
    if building_type == BuildingType.CITY:
        if player.tribe_state.cities >= game.options.victory_cities:
            game._declare_victory(player, "cities")
            return False  # Don't continue building after victory

    return True


def start_construction(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> None:
    """Start construction action.

    Args:
        game: The game instance
        player: The player starting construction
    """
    # Import here to avoid circular import at module level
    from . import bot as bot_ai

    if not player.tribe_state:
        game._end_action(player)
        return

    affordable = get_affordable_buildings(game, player)
    if not affordable:
        user = game.get_user(player)
        if user:
            user.speak_l("ageofheroes-no-resources")
        # Don't end action - return to action selection
        return

    # For bots, auto-select what to build
    if player.is_bot:
        bot_ai.bot_perform_construction(game, player)
    else:
        # Show construction menu for human players
        game.sub_phase = PlaySubPhase.CONSTRUCTION
        user = game.get_user(player)
        if user:
            user.speak_l("ageofheroes-construction-menu")
        game.rebuild_all_menus()
