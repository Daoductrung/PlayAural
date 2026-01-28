"""Combat/War system for Age of Heroes."""

from __future__ import annotations
import random
from typing import TYPE_CHECKING

from .cards import Card, CardType, EventType, get_card_name
from .state import (
    WarState,
    WarGoal,
    get_war_goal_name,
    get_tribe_name,
)

if TYPE_CHECKING:
    from .game import AgeOfHeroesGame, AgeOfHeroesPlayer


def can_declare_war(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str | None:
    """Check if a player can declare war. Returns error message or None."""
    if not player.tribe_state:
        return "No tribe state"

    # Need at least one available army OR a hero card (heroes can substitute for armies)
    available_armies = player.tribe_state.get_available_armies()
    hero_count = sum(
        1 for card in player.hand
        if card.card_type == CardType.EVENT and card.subtype == EventType.HERO
    )

    if available_armies < 1 and hero_count < 1:
        return "ageofheroes-war-no-army"

    # Need at least one valid target
    if not get_valid_war_targets(game, player):
        return "No valid targets"

    return None


def get_valid_war_targets(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer
) -> list[tuple[int, AgeOfHeroesPlayer]]:
    """Get list of valid war targets (player_index, player)."""
    targets = []
    active_players = game.get_active_players()
    player_index = active_players.index(player)

    for i, p in enumerate(active_players):
        if i == player_index:
            continue
        if not hasattr(p, "tribe_state") or not p.tribe_state:
            continue
        if p.tribe_state.is_eliminated():
            continue

        # Can attack anyone (for simplicity)
        # In classic rules, might be limited to neighbors without roads
        targets.append((i, p))

    return targets


def get_valid_war_goals(
    game: AgeOfHeroesGame,
    attacker: AgeOfHeroesPlayer,
    defender: AgeOfHeroesPlayer,
) -> list[str]:
    """Get list of valid war goals against a specific defender."""
    goals = []

    if not defender.tribe_state:
        return goals

    # Conquest - only available from Day 3 onwards (prevents early game rush)
    if defender.tribe_state.cities > 0 and game.current_day >= 3:
        goals.append(WarGoal.CONQUEST)

    # Plunder - can always try to steal cards (if defender has any)
    if len(defender.hand) > 0:
        goals.append(WarGoal.PLUNDER)

    # Destruction - can destroy monument progress (if defender has any)
    if defender.tribe_state.monument_progress > 0:
        goals.append(WarGoal.DESTRUCTION)

    return goals


def declare_war(
    game: AgeOfHeroesGame,
    attacker: AgeOfHeroesPlayer,
    defender_index: int,
    goal: str,
) -> bool:
    """Declare war on another player."""
    active_players = game.get_active_players()

    if defender_index < 0 or defender_index >= len(active_players):
        return False

    attacker_index = active_players.index(attacker)
    defender = active_players[defender_index]

    if not hasattr(defender, "tribe_state") or not defender.tribe_state:
        return False

    # Initialize war state
    game.war_state = WarState(
        attacker_index=attacker_index,
        defender_index=defender_index,
        goal=goal,
    )

    # Announce war declaration
    game.play_sound("game_ageofheroes/war.ogg")

    for p in game.players:
        user = game.get_user(p)
        if user:
            locale = user.locale
            goal_name = get_war_goal_name(goal, locale)
            user.speak_l(
                "ageofheroes-war-declare",
                attacker=attacker.name,
                defender=defender.name,
                goal=goal_name,
            )

    return True


def check_olympics_defense(game: AgeOfHeroesGame) -> AgeOfHeroesPlayer | None:
    """Check if defender has Olympic Games card to cancel war."""
    active_players = game.get_active_players()
    war = game.war_state

    if war.defender_index < 0 or war.defender_index >= len(active_players):
        return None

    defender = active_players[war.defender_index]
    if not hasattr(defender, "hand"):
        return None

    # Check if defender has Olympic Games
    for card in defender.hand:
        if card.card_type == CardType.EVENT and card.subtype == EventType.OLYMPICS:
            return defender

    return None


def use_olympics(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> bool:
    """Use Olympic Games to cancel war."""
    # Find and remove Olympics card
    for i, card in enumerate(player.hand):
        if card.card_type == CardType.EVENT and card.subtype == EventType.OLYMPICS:
            removed = player.hand.pop(i)
            game.discard_pile.append(removed)

            # Cancel the war
            game.war_state.cancelled_by_olympics = True
            game.play_sound("game_ageofheroes/olympics.ogg")

            game.broadcast_l("ageofheroes-olympics-cancel", name=player.name)
            return True

    return False


def prepare_forces(
    game: AgeOfHeroesGame,
    player: AgeOfHeroesPlayer,
    armies: int,
    generals: int,
    heroes: int = 0,
    hero_generals: int = 0,
) -> bool:
    """Prepare forces for battle."""
    if not player.tribe_state:
        return False

    active_players = game.get_active_players()
    player_index = active_players.index(player)
    war = game.war_state

    # Validate army/general counts
    available_armies = player.tribe_state.get_available_armies()
    available_generals = player.tribe_state.get_available_generals()

    # Count hero cards available
    hero_cards = sum(
        1 for card in player.hand
        if card.card_type == CardType.EVENT and card.subtype == EventType.HERO
    )

    total_heroes_used = heroes + hero_generals
    if total_heroes_used > hero_cards:
        return False

    if armies > available_armies:
        return False
    if generals > available_generals:
        return False

    # Commit forces
    if player_index == war.attacker_index:
        war.attacker_armies = armies
        war.attacker_generals = generals
        war.attacker_heroes = heroes
        war.attacker_hero_generals = hero_generals
        war.attacker_prepared = True
    elif player_index == war.defender_index:
        war.defender_armies = armies
        war.defender_generals = generals
        war.defender_heroes = heroes
        war.defender_hero_generals = hero_generals
        war.defender_prepared = True
    else:
        return False

    # Remove hero cards from hand
    for _ in range(total_heroes_used):
        for i, card in enumerate(player.hand):
            if card.card_type == CardType.EVENT and card.subtype == EventType.HERO:
                removed = player.hand.pop(i)
                game.discard_pile.append(removed)
                break

    # Announce preparation
    user = game.get_user(player)
    if user:
        user.speak_l(
            "ageofheroes-war-prepared",
            armies=armies + heroes,
            generals=generals + hero_generals,
            heroes=0,  # Heroes already counted in armies/generals
        )

    return True


def player_roll_war_dice(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> int:
    """Player clicks to roll dice for war. Returns the roll value (1d6)."""
    war = game.war_state
    active_players = game.get_active_players()
    player_index = active_players.index(player)

    # Roll one die (war uses 1d6, not 2d6 like setup)
    die_roll = random.randint(1, 6)

    # Store roll for this player
    if player_index == war.attacker_index:
        war.attacker_roll = die_roll
        war.attacker_dice = [die_roll]
    elif player_index == war.defender_index:
        war.defender_roll = die_roll
        war.defender_dice = [die_roll]

    # Play dice sound
    game.play_sound("game_pig/dice.ogg")

    # Announce roll
    user = game.get_user(player)
    if user:
        user.speak_l("ageofheroes-war-roll-you", roll=die_roll)

    # Announce to others
    for p in game.players:
        if p != player:
            other_user = game.get_user(p)
            if other_user:
                other_user.speak_l(
                    "ageofheroes-war-roll-other",
                    player=player.name,
                    roll=die_roll,
                )

    return die_roll


def resolve_battle_round(game: AgeOfHeroesGame) -> tuple[str, int, int]:
    """Resolve one round of battle using already-rolled dice. Returns (winner, attacker_losses, defender_losses).

    Winner is 'attacker', 'defender', or 'draw'.
    NOTE: In Pascal, draws cause NO losses (unlike Risk-style games).
    """
    war = game.war_state
    active_players = game.get_active_players()

    # Use stored rolls from player clicks
    att_dice_total = war.attacker_roll
    def_dice_total = war.defender_roll

    # Calculate bonuses separately
    att_gen_bonus = 0
    att_fort_bonus = 0
    def_gen_bonus = 0
    def_fort_bonus = 0

    # Attacker bonus: +2 if has at least 1 general (Pascal: SetStore)
    if war.get_attacker_total_generals() > 0:
        att_gen_bonus = 2

    # Defender bonus: +2 if has general, +fortresses
    if war.get_defender_total_generals() > 0:
        def_gen_bonus = 2

    defender_index = war.defender_index
    if defender_index < len(active_players):
        defender_player = active_players[defender_index]
        if hasattr(defender_player, "tribe_state") and defender_player.tribe_state:
            def_fort_bonus = defender_player.tribe_state.fortresses

    att_total_bonus = att_gen_bonus + att_fort_bonus
    def_total_bonus = def_gen_bonus + def_fort_bonus

    attacker_total = att_dice_total + att_total_bonus
    defender_total = def_dice_total + def_total_bonus

    # Get player references
    attacker = active_players[war.attacker_index] if war.attacker_index < len(active_players) else None
    defender = active_players[war.defender_index] if war.defender_index < len(active_players) else None

    # Announce bonuses only if there are any
    if attacker and att_total_bonus > 0:
        for p in game.players:
            user = game.get_user(p)
            if user:
                if p == attacker:
                    # Attacker sees their own bonuses
                    user.speak_l(
                        "ageofheroes-war-bonuses-you",
                        general=att_gen_bonus,
                        fortress=att_fort_bonus,
                        total=attacker_total,
                    )
                else:
                    # Others see attacker's bonuses
                    user.speak_l(
                        "ageofheroes-war-bonuses-other",
                        player=attacker.name,
                        general=att_gen_bonus,
                        fortress=att_fort_bonus,
                        total=attacker_total,
                    )

    if defender and def_total_bonus > 0:
        for p in game.players:
            user = game.get_user(p)
            if user:
                if p == defender:
                    # Defender sees their own bonuses
                    user.speak_l(
                        "ageofheroes-war-bonuses-you",
                        general=def_gen_bonus,
                        fortress=def_fort_bonus,
                        total=defender_total,
                    )
                else:
                    # Others see defender's bonuses
                    user.speak_l(
                        "ageofheroes-war-bonuses-other",
                        player=defender.name,
                        general=def_gen_bonus,
                        fortress=def_fort_bonus,
                        total=defender_total,
                    )

    # Determine winner and announce outcome
    attacker_losses = 0
    defender_losses = 0

    if attacker_total > defender_total:
        # Attacker wins this round - defender loses an army
        defender_losses = 1
        winner = "attacker"
        game.play_sound("game_ageofheroes/attack_win.ogg")

        # Announce round outcome
        game.broadcast_l(
            "ageofheroes-round-attacker-wins",
            attacker=attacker.name if attacker else "Attacker",
            defender=defender.name if defender else "Defender",
            att_total=attacker_total,
            def_total=defender_total,
        )

    elif defender_total > attacker_total:
        # Defender wins this round - attacker loses an army
        attacker_losses = 1
        winner = "defender"
        game.play_sound("game_ageofheroes/defend_win.ogg")

        # Announce round outcome
        game.broadcast_l(
            "ageofheroes-round-defender-wins",
            attacker=attacker.name if attacker else "Attacker",
            defender=defender.name if defender else "Defender",
            att_total=attacker_total,
            def_total=defender_total,
        )

    else:
        # Draw - NO LOSSES in Pascal version (unlike Risk)
        winner = "draw"

        # Announce round outcome
        game.broadcast_l(
            "ageofheroes-round-draw",
            attacker=attacker.name if attacker else "Attacker",
            defender=defender.name if defender else "Defender",
            total=attacker_total,
        )

    # Apply losses (only if not a draw)
    apply_battle_losses(game, attacker_losses, defender_losses)

    return winner, attacker_losses, defender_losses


def apply_battle_losses(
    game: AgeOfHeroesGame, attacker_losses: int, defender_losses: int
) -> None:
    """Apply army losses from battle."""
    war = game.war_state
    active_players = game.get_active_players()

    # Apply attacker losses
    if attacker_losses > 0 and war.attacker_index < len(active_players):
        attacker = active_players[war.attacker_index]
        if hasattr(attacker, "tribe_state") and attacker.tribe_state:
            # First lose heroes being used as armies
            heroes_lost = min(attacker_losses, war.attacker_heroes)
            war.attacker_heroes -= heroes_lost
            attacker_losses -= heroes_lost

            # Then lose regular armies
            if attacker_losses > 0:
                armies_lost = min(attacker_losses, war.attacker_armies)
                war.attacker_armies -= armies_lost
                attacker.tribe_state.armies -= armies_lost
                game.army_supply += armies_lost

    # Apply defender losses
    if defender_losses > 0 and war.defender_index < len(active_players):
        defender = active_players[war.defender_index]
        if hasattr(defender, "tribe_state") and defender.tribe_state:
            # First lose heroes being used as armies
            heroes_lost = min(defender_losses, war.defender_heroes)
            war.defender_heroes -= heroes_lost
            defender_losses -= heroes_lost

            # Then lose regular armies
            if defender_losses > 0:
                armies_lost = min(defender_losses, war.defender_armies)
                war.defender_armies -= armies_lost
                defender.tribe_state.armies -= armies_lost
                game.army_supply += armies_lost


def is_battle_over(game: AgeOfHeroesGame) -> bool:
    """Check if the battle is over (one side has no armies left)."""
    war = game.war_state

    attacker_armies = war.get_attacker_total_armies()
    defender_armies = war.get_defender_total_armies()

    return attacker_armies <= 0 or defender_armies <= 0


def get_battle_winner(game: AgeOfHeroesGame) -> str | None:
    """Get the winner of the battle, or None if not over."""
    if not is_battle_over(game):
        return None

    war = game.war_state
    attacker_armies = war.get_attacker_total_armies()
    defender_armies = war.get_defender_total_armies()

    if attacker_armies > 0 and defender_armies <= 0:
        return "attacker"
    elif defender_armies > 0 and attacker_armies <= 0:
        return "defender"
    else:
        # Both wiped out - defender wins by default
        return "defender"


def apply_war_outcome(game: AgeOfHeroesGame) -> None:
    """Apply the outcome of the war based on the goal."""
    war = game.war_state
    winner = get_battle_winner(game)
    active_players = game.get_active_players()

    if winner != "attacker":
        # Attacker lost or draw - no spoils
        return_surviving_forces(game)
        return

    # Attacker won - apply goal
    if war.attacker_index >= len(active_players):
        return
    if war.defender_index >= len(active_players):
        return

    attacker = active_players[war.attacker_index]
    defender = active_players[war.defender_index]

    if not hasattr(attacker, "tribe_state") or not attacker.tribe_state:
        return
    if not hasattr(defender, "tribe_state") or not defender.tribe_state:
        return

    # Get attacker's remaining army strength for calculating spoils
    attacker_strength = war.attacker_armies + war.attacker_heroes

    if war.goal == WarGoal.CONQUEST:
        # Take cities based on army strength (Pascal: wgsConquest)
        # 3+ armies: 2 cities, 1+ armies: 1 city
        if attacker_strength >= 3:
            cities_to_take = 2
        elif attacker_strength >= 1:
            cities_to_take = 1
        else:
            cities_to_take = 0

        cities_to_take = min(cities_to_take, defender.tribe_state.cities)

        if cities_to_take > 0:
            defender.tribe_state.cities -= cities_to_take
            attacker.tribe_state.cities += cities_to_take
            game.broadcast_l(
                "ageofheroes-conquest-success",
                attacker=attacker.name,
                defender=defender.name,
                count=cities_to_take,
            )
            game.play_sound("game_ageofheroes/conquest.ogg")

    elif war.goal == WarGoal.PLUNDER:
        # Steal cards: 2 × army strength (Pascal: wgsPlunder)
        cards_to_steal = min(2 * attacker_strength, len(defender.hand))
        if cards_to_steal > 0:
            stolen = []
            for _ in range(cards_to_steal):
                if defender.hand:
                    # Steal random card
                    idx = random.randint(0, len(defender.hand) - 1)
                    card = defender.hand.pop(idx)
                    attacker.hand.append(card)
                    stolen.append(card)

            game.broadcast_l(
                "ageofheroes-plunder-success",
                attacker=attacker.name,
                count=len(stolen),
                defender=defender.name,
            )
            game.play_sound("game_ageofheroes/plunder.ogg")

    elif war.goal == WarGoal.DESTRUCTION:
        # Destroy monument progress based on army strength (Pascal: wgsDestruction)
        # 3+ armies: 2 resources, 1-2 armies: 1 resource, 0 armies: 0 resources
        if attacker_strength >= 3:
            resources_to_destroy = 2
        elif attacker_strength >= 1:
            resources_to_destroy = 1
        else:
            resources_to_destroy = 0

        resources_to_destroy = min(
            resources_to_destroy, defender.tribe_state.monument_progress
        )

        if resources_to_destroy > 0:
            defender.tribe_state.monument_progress -= resources_to_destroy
            game.broadcast_l(
                "ageofheroes-destruction-success",
                attacker=attacker.name,
                defender=defender.name,
                count=resources_to_destroy,
            )
            game.play_sound("game_ageofheroes/destruction.ogg")

    return_surviving_forces(game)


def has_road_connection(
    game: AgeOfHeroesGame, player1_index: int, player2_index: int
) -> bool:
    """Check if two players have a road connection between them."""
    active_players = game.get_active_players()

    if player1_index >= len(active_players) or player2_index >= len(active_players):
        return False

    player1 = active_players[player1_index]
    player2 = active_players[player2_index]

    if not hasattr(player1, "tribe_state") or not player1.tribe_state:
        return False
    if not hasattr(player2, "tribe_state") or not player2.tribe_state:
        return False

    # Check if they are neighbors and have connecting roads
    # Players are neighbors if their indices differ by 1 (mod num_players)
    num_players = len(active_players)

    # Check if player2 is to the right of player1
    if (player1_index + 1) % num_players == player2_index:
        return player1.tribe_state.road_right and player2.tribe_state.road_left

    # Check if player2 is to the left of player1
    if (player1_index - 1) % num_players == player2_index:
        return player1.tribe_state.road_left and player2.tribe_state.road_right

    return False


def return_surviving_forces(game: AgeOfHeroesGame) -> None:
    """Return surviving armies after battle."""
    war = game.war_state
    active_players = game.get_active_players()

    # Attacker's surviving armies return
    if war.attacker_index < len(active_players):
        attacker = active_players[war.attacker_index]
        if hasattr(attacker, "tribe_state") and attacker.tribe_state:
            surviving_armies = war.attacker_armies
            surviving_generals = war.attacker_generals

            if surviving_armies > 0 or surviving_generals > 0:
                # Check if attacker has road to defender for immediate return
                has_road = has_road_connection(game, war.attacker_index, war.defender_index)

                if has_road:
                    # Immediate return via road
                    attacker.tribe_state.armies += surviving_armies
                    attacker.tribe_state.generals += surviving_generals

                    user = game.get_user(attacker)
                    if user:
                        user.speak_l("ageofheroes-army-return-road")
                    game.play_sound("game_ageofheroes/backarmy.ogg")
                else:
                    # Delayed return - armies come back next turn
                    attacker.tribe_state.returning_armies = surviving_armies
                    attacker.tribe_state.returning_generals = surviving_generals

                    user = game.get_user(attacker)
                    if user:
                        user.speak_l(
                            "ageofheroes-army-return-delayed",
                            count=surviving_armies + surviving_generals,
                        )

    # Defender's armies always return immediately (defending at home)
    if war.defender_index < len(active_players):
        defender = active_players[war.defender_index]
        if hasattr(defender, "tribe_state") and defender.tribe_state:
            # Defender's armies return to their tribe
            defender.tribe_state.armies += war.defender_armies
            defender.tribe_state.generals += war.defender_generals

    # Reset war state
    war.reset()


def check_fortune_reroll(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer
) -> bool:
    """Check if player has Fortune card for reroll."""
    for card in player.hand:
        if card.card_type == CardType.EVENT and card.subtype == EventType.FORTUNE:
            return True
    return False


def use_fortune_reroll(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> bool:
    """Use Fortune card to reroll dice."""
    for i, card in enumerate(player.hand):
        if card.card_type == CardType.EVENT and card.subtype == EventType.FORTUNE:
            removed = player.hand.pop(i)
            game.discard_pile.append(removed)
            game.broadcast_l("ageofheroes-fortune-reroll", name=player.name)
            game.play_sound("game_ageofheroes/fortune.ogg")
            return True
    return False


def jolt_war_bots(game: AgeOfHeroesGame) -> None:
    """Jolt bot players to roll dice in war."""
    active_players = game.get_active_players()
    war = game.war_state

    if war.attacker_index < len(active_players):
        attacker = active_players[war.attacker_index]
        if attacker.is_bot and war.attacker_roll == 0:
            # Clear any pending action and set to roll immediately next tick
            attacker.bot_pending_action = None
            attacker.bot_think_ticks = 1  # Will call bot_think on next tick

    if war.defender_index < len(active_players):
        defender = active_players[war.defender_index]
        if defender.is_bot and war.defender_roll == 0:
            # Clear any pending action and set to roll immediately next tick
            defender.bot_pending_action = None
            defender.bot_think_ticks = 1  # Will call bot_think on next tick


def resolve_war_round(game: AgeOfHeroesGame) -> None:
    """Resolve one round of war battle after both players have rolled."""
    # Resolve the round
    resolve_battle_round(game)

    # Check if battle is over
    if is_battle_over(game):
        # Battle is finished
        finish_war_battle(game)
    else:
        # Continue to next round - reset rolls
        game.war_state.reset_round_rolls()
        game.rebuild_all_menus()

        # Jolt both bots to roll for next round
        active_players = game.get_active_players()
        war = game.war_state
        if war.attacker_index < len(active_players):
            attacker = active_players[war.attacker_index]
            if attacker.is_bot:
                attacker.bot_think_ticks = 0
                attacker.bot_pending_action = None
        if war.defender_index < len(active_players):
            defender = active_players[war.defender_index]
            if defender.is_bot:
                defender.bot_think_ticks = 0
                defender.bot_pending_action = None


def execute_war_battle(game: AgeOfHeroesGame) -> None:
    """Start the interactive war battle after both sides have prepared forces.

    Players will now click to roll dice each round instead of automatic resolution.
    """
    from .state import PlaySubPhase

    # Announce battle start with army counts
    active_players = game.get_active_players()
    war = game.war_state

    if war.attacker_index < len(active_players) and war.defender_index < len(active_players):
        attacker = active_players[war.attacker_index]
        defender = active_players[war.defender_index]

        att_armies = war.get_attacker_total_armies()
        def_armies = war.get_defender_total_armies()

        # Announce battle start
        game.broadcast_l(
            "ageofheroes-battle-start",
            attacker=attacker.name,
            defender=defender.name,
            att_armies=att_armies,
            def_armies=def_armies,
        )

    # Check if battle is already over (one side has 0 armies)
    if is_battle_over(game):
        # Battle is already over without needing to roll
        finish_war_battle(game)
        return

    # Enter interactive battle mode
    game.sub_phase = PlaySubPhase.WAR_BATTLE
    war.battle_in_progress = True
    war.reset_round_rolls()

    # Rebuild menus to show "Roll dice" button
    game.rebuild_all_menus()

    # Jolt both bots to act immediately (set think ticks to 0)
    active_players = game.get_active_players()
    if war.attacker_index < len(active_players):
        attacker = active_players[war.attacker_index]
        if attacker.is_bot:
            attacker.bot_think_ticks = 0
            attacker.bot_pending_action = None
    if war.defender_index < len(active_players):
        defender = active_players[war.defender_index]
        if defender.is_bot:
            defender.bot_think_ticks = 0
            defender.bot_pending_action = None


def finish_war_battle(game: AgeOfHeroesGame) -> None:
    """Finish the war battle and apply outcome."""
    active_players = game.get_active_players()
    war = game.war_state

    # Save attacker/defender info BEFORE applying outcome (which resets war state)
    winner = get_battle_winner(game)

    attacker_name = None
    defender_name = None
    if war.attacker_index < len(active_players) and war.defender_index < len(active_players):
        attacker = active_players[war.attacker_index]
        defender = active_players[war.defender_index]
        attacker_name = attacker.name
        defender_name = defender.name

    # Apply war outcome (this may reset war state)
    apply_war_outcome(game)

    # Announce battle end summary
    if attacker_name and defender_name:
        if winner == "attacker":
            game.broadcast_l(
                "ageofheroes-battle-victory-attacker",
                attacker=attacker_name,
                defender=defender_name,
            )
        elif winner == "defender":
            game.broadcast_l(
                "ageofheroes-battle-victory-defender",
                attacker=attacker_name,
                defender=defender_name,
            )
        else:
            game.broadcast_l(
                "ageofheroes-battle-mutual-defeat",
                attacker=attacker_name,
                defender=defender_name,
            )

    # Check for elimination of both players
    if war.attacker_index < len(active_players):
        attacker = active_players[war.attacker_index]
        game._check_elimination(attacker)

    if war.defender_index < len(active_players):
        defender = active_players[war.defender_index]
        game._check_elimination(defender)

    # Reset war state and end action
    attacker_idx = war.attacker_index
    war.reset()

    if attacker_idx < len(active_players):
        attacker = active_players[attacker_idx]
        game._end_action(attacker)
