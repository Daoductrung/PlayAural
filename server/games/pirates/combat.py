"""
Combat System for Pirates of the Lost Seas.

Handles cannonball attacks, defenses, and gem stealing.
This module consolidates the duplicate target-finding logic that was
scattered throughout the Lua code.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .game import PiratesGame
    from .player import PiratesPlayer

from . import gems
from . import skills
from ...messages.localization import Localization


@dataclass
class CombatResult:
    """Result of a combat action."""

    hit: bool
    attack_roll: int
    defense_roll: int
    attack_bonus: int
    defense_bonus: int
    xp_gained: int


def get_targets_in_range(
    game: "PiratesGame",
    attacker: "PiratesPlayer",
    max_range: int | None = None
) -> list["PiratesPlayer"]:
    """
    Get all valid targets within attack range.

    This is the unified function that replaces the duplicate target-finding
    code that was in the Lua skills.lua and combat.lua files.

    Args:
        game: The game instance
        attacker: The attacking player
        max_range: Override range (None uses skill manager's calculated range)

    Returns:
        List of players within attack range
    """
    if max_range is None:
        max_range = skills.get_attack_range(attacker)

    targets = []
    for player in game.get_active_players():
        if player.id == attacker.id:
            continue
        distance = abs(attacker.position - player.position)
        if distance <= max_range:
            targets.append(player)

    return targets


def get_distance(player1: "PiratesPlayer", player2: "PiratesPlayer") -> int:
    """Get the distance between two players."""
    return abs(player1.position - player2.position)


def do_attack(
    game: "PiratesGame",
    attacker: "PiratesPlayer",
    defender: "PiratesPlayer",
    golden_moon_active: bool = False,
    global_xp_multiplier: float = 1.0,
    gem_stealing: str = "with_roll_bonus"
) -> CombatResult:
    """
    Execute an attack between two players.

    Args:
        game: The game instance
        attacker: The attacking player
        defender: The defending player
        golden_moon_active: Whether golden moon is active this turn
        global_xp_multiplier: Global XP multiplier from game options
        gem_stealing: Gem stealing mode ("with_roll_bonus", "no_roll_bonus", or "disabled")

    Returns:
        CombatResult with the outcome
    """
    # Play cannon sound
    sound_num = random.randint(1, 3)
    game.play_sound(f"game_pirates/cannon{sound_num}.ogg", volume=60)

    # Announce attack
    attacker_user = game.get_user(attacker)
    defender_user = game.get_user(defender)

    if attacker_user:
        attacker_user.speak_l("pirates-attack-you-fire", target=defender.name)
    if defender_user:
        defender_user.speak_l("pirates-attack-incoming", attacker=attacker.name)
    game.broadcast_l(
        "pirates-attack-fired",
        attacker=attacker.name,
        defender=defender.name,
        exclude=attacker
    )

    # Get bonuses from skills
    attack_bonus = skills.get_attack_bonus(attacker)
    defense_bonus = skills.get_defense_bonus(defender)

    # Roll attack
    attack_roll = random.randint(1, 6)
    game.broadcast_l("pirates-attack-roll", roll=attack_roll)

    if attack_bonus > 0:
        game.broadcast_l("pirates-attack-bonus", bonus=attack_bonus)
        attack_roll += attack_bonus

    # Roll defense
    defense_roll = random.randint(1, 6)
    if defender_user:
        defender_user.speak_l("pirates-defense-roll", roll=defense_roll)
    game.broadcast_l("pirates-defense-roll-others", player=defender.name, roll=defense_roll, exclude=defender)

    if defense_bonus > 0:
        game.broadcast_l("pirates-defense-bonus", bonus=defense_bonus)
        defense_roll += defense_bonus

    # Calculate XP multiplier
    moon_mult = 3.0 if golden_moon_active else 1.0
    total_mult = moon_mult * global_xp_multiplier

    hit = attack_roll > defense_roll

    if hit:
        # Hit!
        sound_num = random.randint(1, 3)
        game.play_sound(f"game_pirates/cannonhit{sound_num}.ogg", volume=70)

        if attacker_user:
            attacker_user.speak_l("pirates-attack-hit-you", target=defender.name)
        if defender_user:
            defender_user.speak_l("pirates-attack-hit-them", attacker=attacker.name)
        game.broadcast_l(
            "pirates-attack-hit",
            attacker=attacker.name,
            defender=defender.name,
            exclude=attacker
        )

        # Give XP to attacker
        xp_gain = random.randint(50, 150)
        attacker.leveling.give_xp(
            game, attacker.name, xp_gain, moon_mult, global_xp_multiplier
        )

        # Handle boarding action (push or steal)
        _handle_boarding(
            game, attacker, defender,
            attack_bonus, defense_bonus,
            gem_stealing
        )

        return CombatResult(
            hit=True,
            attack_roll=attack_roll,
            defense_roll=defense_roll,
            attack_bonus=attack_bonus,
            defense_bonus=defense_bonus,
            xp_gained=int(xp_gain * total_mult)
        )
    else:
        # Miss!
        if attacker_user:
            attacker_user.speak_l("pirates-attack-miss-you", target=defender.name)
        if defender_user:
            defender_user.speak_l("pirates-attack-miss-them")
        game.broadcast_l(
            "pirates-attack-miss",
            attacker=attacker.name,
            defender=defender.name,
            exclude=attacker
        )

        # Give XP to defender for successful defense
        xp_gain = random.randint(30, 100)
        defender.leveling.give_xp(
            game, defender.name, xp_gain, moon_mult, global_xp_multiplier
        )

        return CombatResult(
            hit=False,
            attack_roll=attack_roll,
            defense_roll=defense_roll,
            attack_bonus=attack_bonus,
            defense_bonus=defense_bonus,
            xp_gained=int(xp_gain * total_mult)
        )


def _handle_boarding(
    game: "PiratesGame",
    attacker: "PiratesPlayer",
    defender: "PiratesPlayer",
    attack_bonus: int,
    defense_bonus: int,
    gem_stealing: str
) -> None:
    """
    Handle the boarding action after a successful attack.

    The attacker can choose to push the defender or attempt to steal a gem.

    Args:
        game: The game instance
        attacker: The attacking player
        defender: The defending player
        attack_bonus: Attacker's bonus (for steal roll if applicable)
        defense_bonus: Defender's bonus (for steal roll if applicable)
        gem_stealing: Gem stealing mode
    """
    attacker_user = game.get_user(attacker)
    defender_user = game.get_user(defender)

    can_steal = gem_stealing != "disabled" and defender.has_gems()

    # If human and can steal, show choice menu
    if attacker_user and can_steal and not attacker.is_bot:
        # Request choice from player via game mechanism
        choice = game.request_boarding_choice(attacker, defender)

        if choice == "steal":
            _attempt_gem_steal(
                game, attacker, defender,
                attack_bonus if gem_stealing == "with_roll_bonus" else 0,
                defense_bonus if gem_stealing == "with_roll_bonus" else 0
            )
            return
        elif choice in ("left", "right"):
            _push_defender(game, attacker, defender, choice)
            return

    # Bot or timeout - random push
    direction = random.choice(["left", "right"])
    _push_defender(game, attacker, defender, direction)


def _push_defender(
    game: "PiratesGame",
    attacker: "PiratesPlayer",
    defender: "PiratesPlayer",
    direction: str
) -> None:
    """Push the defender in the specified direction."""
    push_amount = random.randint(3, 8)
    if direction == "left":
        push_amount = -push_amount

    old_pos = defender.position
    defender.position = max(1, min(40, defender.position + push_amount))

    attacker_user = game.get_user(attacker)
    defender_user = game.get_user(defender)

    direction_key = f"pirates-dir-{direction}"

    if attacker_user:
        direction_local = Localization.get(attacker_user.locale, direction_key)
        attacker_user.speak_l(
            "pirates-push-you",
            target=defender.name,
            direction=direction_local,
            position=defender.position
        )
    if defender_user:
        direction_local = Localization.get(defender_user.locale, direction_key)
        defender_user.speak_l(
            "pirates-push-them",
            attacker=attacker.name,
            direction=direction_local,
            position=defender.position
        )
    
    # Manual broadcast
    for p in game.get_active_players():
        if p.id == attacker.id or p.id == defender.id:
            continue
        u = game.get_user(p)
        if u:
            direction_local = Localization.get(u.locale, direction_key)
            u.speak_l(
                "pirates-push",
                attacker=attacker.name,
                defender=defender.name,
                direction=direction_local,
                old_pos=old_pos,
                new_pos=defender.position
            )


def _attempt_gem_steal(
    game: "PiratesGame",
    attacker: "PiratesPlayer",
    defender: "PiratesPlayer",
    attack_bonus: int,
    defense_bonus: int
) -> bool:
    """
    Attempt to steal a gem from the defender.

    Args:
        game: The game instance
        attacker: The attacking player
        defender: The defending player
        attack_bonus: Bonus to attacker's steal roll
        defense_bonus: Bonus to defender's steal roll

    Returns:
        True if steal was successful
    """
    game.broadcast_l("pirates-steal-attempt", attacker=attacker.name)

    steal_roll = random.randint(1, 6) + attack_bonus
    defend_roll = random.randint(1, 6) + defense_bonus

    game.broadcast_l(
        "pirates-steal-rolls",
        steal=steal_roll,
        defend=defend_roll
    )

    if steal_roll > defend_roll:
        # Successful steal
        stolen_index = random.randint(0, len(defender.gems) - 1)
        stolen_gem = defender.remove_gem(stolen_index)
        if stolen_gem is not None:
            gem_value = gems.get_gem_value(stolen_gem)
            attacker.add_gem(stolen_gem, gem_value)

            # Recalculate defender's score
            defender.recalculate_score(gems.get_gem_value)

            # Play steal sound
            sound_num = random.randint(1, 2)
            game.play_sound(f"game_pirates/stealgem{sound_num}.ogg", volume=70)

            gem_name_key = gems.get_gem_name(stolen_gem)
            attacker_user = game.get_user(attacker)
            defender_user = game.get_user(defender)

            if attacker_user:
                gem_local = Localization.get(attacker_user.locale, gem_name_key)
                attacker_user.speak_l(
                    "pirates-steal-success-you",
                    gem=gem_local,
                    target=defender.name
                )
            if defender_user:
                gem_local = Localization.get(defender_user.locale, gem_name_key)
                defender_user.speak_l(
                    "pirates-steal-success-them",
                    gem=gem_local,
                    attacker=attacker.name
                )
            
            # Manual broadcast
            for p in game.get_active_players():
                if p.id == attacker.id or p.id == defender.id:
                    continue
                u = game.get_user(p)
                if u:
                    gem_local = Localization.get(u.locale, gem_name_key)
                    u.speak_l(
                        "pirates-steal-success",
                        attacker=attacker.name,
                        gem=gem_local,
                        defender=defender.name,
                    )
            return True
    else:
        game.broadcast_l("pirates-steal-failed")
        return False

    return False
