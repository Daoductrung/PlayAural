"""Event processing system for Age of Heroes.

Handles mandatory events like Population Growth, Earthquake, Eruption,
Hunger, and Barbarians.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .cards import (
    Card,
    CardType,
    ResourceType,
    EventType,
    get_card_name,
)
from .state import GamePhase

if TYPE_CHECKING:
    from .game import AgeOfHeroesGame, AgeOfHeroesPlayer


def process_player_events(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> None:
    """Process mandatory events for a player.

    Pascal behavior:
    - Round 1: Only Population Growth has effect, other disasters just discard
    - Round 2+: Population Growth effect, Hunger/Barbarians effects apply,
      Earthquake/Eruption are targetable (just discard here, play later)
    """
    if not player.tribe_state:
        return

    # Check if disaster effects should apply (round 2+ or during play phase)
    effects_active = game.current_day > 1 or game.phase == GamePhase.PLAY

    # Collect events to process (with their effects) before removing cards
    events_to_process: list[tuple[int, Card, str]] = []  # (index, card, effect_type)

    for i, card in enumerate(player.hand):
        if not card.is_mandatory_event():
            continue

        if card.subtype == EventType.POPULATION_GROWTH:
            events_to_process.append((i, card, "population_growth"))

        elif card.subtype == EventType.EARTHQUAKE:
            # In round 1, auto-discard. In round 2+, keep in hand to be played manually
            if not effects_active:
                events_to_process.append((i, card, "earthquake"))

        elif card.subtype == EventType.ERUPTION:
            # In round 1, auto-discard. In round 2+, keep in hand to be played manually
            if not effects_active:
                events_to_process.append((i, card, "eruption"))

        elif card.subtype == EventType.HUNGER:
            if effects_active:
                events_to_process.append((i, card, "hunger_effect"))
            else:
                events_to_process.append((i, card, "hunger_discard"))

        elif card.subtype == EventType.BARBARIANS:
            if effects_active:
                events_to_process.append((i, card, "barbarians_effect"))
            else:
                events_to_process.append((i, card, "barbarians_discard"))

    # Remove all event cards in reverse order
    for i, card, _ in reversed(events_to_process):
        removed = player.hand.pop(i)
        game.discard_pile.append(removed)

    # Now apply effects (cards are already removed, so no index issues)
    for _, card, effect_type in events_to_process:
        if effect_type == "population_growth":
            # Build a free city (always applies)
            if game.city_supply > 0:
                player.tribe_state.cities += 1
                game.city_supply -= 1
                game.broadcast_personal_l(
                    player,
                    "ageofheroes-population-growth-you",
                    "ageofheroes-population-growth",
                )
                game.play_sound("game_ageofheroes/build.ogg")

        elif effect_type == "earthquake":
            # Earthquake is targetable at other players in round 2+
            # For now, just announce discard
            user = game.get_user(player)
            if user:
                card_name = get_card_name(card, user.locale)
                user.speak_l("ageofheroes-discard-card-you", card=card_name)
            _broadcast_discard(game, player, card)

        elif effect_type == "eruption":
            # Eruption is targetable at other players in round 2+
            # For now, just announce discard
            user = game.get_user(player)
            if user:
                card_name = get_card_name(card, user.locale)
                user.speak_l("ageofheroes-discard-card-you", card=card_name)
            _broadcast_discard(game, player, card)

        elif effect_type == "hunger_effect":
            # ALL players lose 1 Grain (unless blocked by Fortune)
            apply_hunger_effect(game, player)

        elif effect_type == "hunger_discard":
            # Round 1: just announce discard
            user = game.get_user(player)
            if user:
                card_name = get_card_name(card, user.locale)
                user.speak_l("ageofheroes-discard-card-you", card=card_name)
            _broadcast_discard(game, player, card)

        elif effect_type == "barbarians_effect":
            # Playing player loses 2 conventional resources (unless blocked)
            apply_barbarians_effect(game, player)

        elif effect_type == "barbarians_discard":
            # Round 1: just announce discard
            user = game.get_user(player)
            if user:
                card_name = get_card_name(card, user.locale)
                user.speak_l("ageofheroes-discard-card-you", card=card_name)
            _broadcast_discard(game, player, card)

    # Check for elimination
    game._check_elimination(player)


def player_has_card(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, event_type: str) -> bool:
    """Check if player has a specific event card."""
    for card in player.hand:
        if card.card_type == CardType.EVENT and card.subtype == event_type:
            return True
    return False


def discard_player_card(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, event_type: str) -> bool:
    """Discard a specific event card from player's hand. Returns True if found."""
    for i, card in enumerate(player.hand):
        if card.card_type == CardType.EVENT and card.subtype == event_type:
            removed = player.hand.pop(i)
            game.discard_pile.append(removed)

            # Announce the block
            user = game.get_user(player)
            if user:
                card_name = get_card_name(removed, user.locale)
                user.speak_l("ageofheroes-block-with-card-you", card=card_name)

            for p in game.players:
                if p != player:
                    other_user = game.get_user(p)
                    if other_user:
                        card_name = get_card_name(removed, other_user.locale)
                        other_user.speak_l(
                            "ageofheroes-block-with-card",
                            player=player.name,
                            card=card_name,
                        )
            return True
    return False


def apply_hunger_effect(game: AgeOfHeroesGame, source_player: AgeOfHeroesPlayer) -> None:
    """Apply Hunger effect: ALL players lose 1 Grain card.

    Can be blocked by Fortune card.
    """
    game.broadcast_l("ageofheroes-hunger-strikes")
    game.play_sound("game_ageofheroes/disaster.ogg")

    for player in game.get_active_players():
        from .game import AgeOfHeroesPlayer
        if not isinstance(player, AgeOfHeroesPlayer):
            continue
        if not player.tribe_state:
            continue

        # Check for Fortune block
        if player_has_card(game, player, EventType.FORTUNE):
            discard_player_card(game, player, EventType.FORTUNE)
            continue

        # Find and discard one Grain
        for i, card in enumerate(player.hand):
            if card.card_type == CardType.RESOURCE and card.subtype == ResourceType.GRAIN:
                removed = player.hand.pop(i)
                game.discard_pile.append(removed)

                user = game.get_user(player)
                if user:
                    card_name = get_card_name(removed, user.locale)
                    user.speak_l("ageofheroes-lose-card-hunger", card=card_name)
                break


def apply_barbarians_effect(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> None:
    """Apply Barbarians effect: player loses 2 conventional resource cards.

    Can be blocked by Fortune or Olympics card.
    """
    if not player.tribe_state:
        return

    game.broadcast_personal_l(
        player, "ageofheroes-barbarians-attack-you", "ageofheroes-barbarians-attack"
    )
    game.play_sound("game_ageofheroes/disaster.ogg")

    # Check for Fortune block
    if player_has_card(game, player, EventType.FORTUNE):
        discard_player_card(game, player, EventType.FORTUNE)
        return

    # Check for Olympics block
    if player_has_card(game, player, EventType.OLYMPICS):
        discard_player_card(game, player, EventType.OLYMPICS)
        return

    # Lose up to 2 conventional resources
    lost_count = 0
    while lost_count < 2:
        found = False
        for i, card in enumerate(player.hand):
            if card.card_type == CardType.RESOURCE and card.subtype != ResourceType.GOLD:
                removed = player.hand.pop(i)
                game.discard_pile.append(removed)
                lost_count += 1

                user = game.get_user(player)
                if user:
                    card_name = get_card_name(removed, user.locale)
                    user.speak_l("ageofheroes-lose-card-barbarians", card=card_name)
                found = True
                break
        if not found:
            break


def check_drawn_card_event(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, card: Card
) -> None:
    """Check if a drawn card triggers an immediate event.

    Pascal behavior: Hunger and Barbarians trigger immediately when drawn
    during Play phase or after round 1.
    """
    if card.card_type != CardType.EVENT:
        return

    # Only trigger during play phase or round 2+
    if game.phase != GamePhase.PLAY and game.current_day <= 1:
        return

    if card.subtype == EventType.HUNGER:
        apply_hunger_effect(game, player)
        # Remove the drawn card
        if card in player.hand:
            player.hand.remove(card)
            game.discard_pile.append(card)

    elif card.subtype == EventType.BARBARIANS:
        apply_barbarians_effect(game, player)
        # Remove the drawn card
        if card in player.hand:
            player.hand.remove(card)
            game.discard_pile.append(card)


def apply_earthquake_effect(game: AgeOfHeroesGame, source_player: AgeOfHeroesPlayer, target_player: AgeOfHeroesPlayer) -> None:
    """Apply Earthquake effect: Target player's armies are disabled for one turn.

    Armies become 'earthquaked' and cannot be used until next turn.
    Can be blocked by Fortune card.
    """
    if not target_player.tribe_state:
        return

    game.broadcast_personal_l(
        target_player,
        "ageofheroes-earthquake-strikes-you",
        "ageofheroes-earthquake-strikes",
        attacker=source_player.name,
    )
    game.play_sound("game_ageofheroes/disaster.ogg")

    # Check for Fortune block
    if player_has_card(game, target_player, EventType.FORTUNE):
        discard_player_card(game, target_player, EventType.FORTUNE)
        return

    # Disable all available armies (mark them as earthquaked)
    available_armies = target_player.tribe_state.get_available_armies()
    if available_armies > 0:
        target_player.tribe_state.earthquaked_armies = available_armies

        user = game.get_user(target_player)
        if user:
            user.speak_l("ageofheroes-armies-disabled", count=available_armies)


def apply_eruption_effect(game: AgeOfHeroesGame, source_player: AgeOfHeroesPlayer, target_player: AgeOfHeroesPlayer) -> None:
    """Apply Eruption effect: Target player loses one city.

    Can be blocked by Fortune or Olympics card.
    """
    if not target_player.tribe_state:
        return

    game.broadcast_personal_l(
        target_player,
        "ageofheroes-eruption-strikes-you",
        "ageofheroes-eruption-strikes",
        attacker=source_player.name,
    )
    game.play_sound("game_ageofheroes/disaster.ogg")

    # Check for Fortune block
    if player_has_card(game, target_player, EventType.FORTUNE):
        discard_player_card(game, target_player, EventType.FORTUNE)
        return

    # Check for Olympics block
    if player_has_card(game, target_player, EventType.OLYMPICS):
        discard_player_card(game, target_player, EventType.OLYMPICS)
        return

    # Destroy one city
    if target_player.tribe_state.cities > 0:
        target_player.tribe_state.cities -= 1
        game.city_supply += 1  # Return to supply

        user = game.get_user(target_player)
        if user:
            user.speak_l("ageofheroes-city-destroyed")


def _broadcast_discard(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, card: Card) -> None:
    """Broadcast card discard to other players."""
    for p in game.players:
        if p == player:
            continue
        user = game.get_user(p)
        if user:
            card_name = get_card_name(card, user.locale)
            user.speak_l("ageofheroes-discard-card", player=player.name, card=card_name)
