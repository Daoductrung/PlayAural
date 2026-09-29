"""
Combat System for Pirates of the Lost Seas.

Handles cannonball attacks, defenses, and gem stealing.
This module consolidates the duplicate target-finding logic that was
scattered throughout the Lua code.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import TYPE_CHECKING

from ...messages.localization import Localization
from . import gems, skills

if TYPE_CHECKING:
    from .game import PiratesGame
    from .player import PiratesPlayer


@dataclass
class CombatResult:
    """Result of a combat action."""

    hit: bool
    attack_roll: int
    defense_roll: int
    attack_bonus: int
    defense_bonus: int
    xp_gained: int
    boarding_pending: bool = False


def get_targets_in_range(
    game: "PiratesGame",
    attacker: "PiratesPlayer",
    max_range: int | None = None,
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
    allow_boarding: bool = True,
    announce_fire: bool = True,
) -> CombatResult:
    """
    Execute an attack between two players.

    Args:
        game: The game instance
        attacker: The attacking player
        defender: The defending player
        golden_moon_active: Whether golden moon is active this turn
        global_xp_multiplier: Global XP multiplier from game options
    Returns:
        CombatResult with the outcome
    """
    # Play cannon sound
    sound_num = random.randint(1, 3)
    game.play_sound(f"game_pirates/cannon{sound_num}.ogg", volume=60)

    if announce_fire:
        _broadcast_combat_event(
            game,
            attacker,
            defender,
            attacker_key="pirates-attack-you-fire",
            defender_key="pirates-attack-incoming",
            observer_key="pirates-attack-fired",
            brief_attacker_key="pirates-attack-you-fire-brief",
            brief_defender_key="pirates-attack-incoming-brief",
            brief_observer_key="pirates-attack-fired-brief",
        )

    # Get bonuses from skills
    attack_bonus = skills.get_attack_bonus(attacker)
    defense_bonus = skills.get_defense_bonus(defender)

    # Roll attack
    attack_die = random.randint(1, 6)
    attack_roll = attack_die + attack_bonus

    # Roll defense
    defense_die = random.randint(1, 6)
    defense_roll = defense_die + defense_bonus
    _broadcast_combat_event(
        game,
        attacker,
        defender,
        attacker_key="pirates-combat-rolls-you",
        defender_key="pirates-combat-rolls-defender",
        observer_key="pirates-combat-rolls-observer",
        brief_attacker_key="pirates-combat-rolls-you-brief",
        brief_defender_key="pirates-combat-rolls-defender-brief",
        brief_observer_key="pirates-combat-rolls-observer-brief",
        attack_die=attack_die,
        attack_bonus=attack_bonus,
        attack_total=attack_roll,
        defense_die=defense_die,
        defense_bonus=defense_bonus,
        defense_total=defense_roll,
    )

    # Calculate XP multiplier
    moon_mult = 3.0 if golden_moon_active else 1.0
    total_mult = moon_mult * global_xp_multiplier

    hit = attack_roll > defense_roll

    if hit:
        # Hit!
        sound_num = random.randint(1, 3)
        game.play_sound(f"game_pirates/cannonhit{sound_num}.ogg", volume=70)

        if allow_boarding:
            hit_keys = {
                "attacker_key": "pirates-attack-hit-you",
                "defender_key": "pirates-attack-hit-them",
                "observer_key": "pirates-attack-hit",
                "brief_attacker_key": "pirates-attack-hit-you-brief",
                "brief_defender_key": "pirates-attack-hit-them-brief",
                "brief_observer_key": "pirates-attack-hit-brief",
            }
        else:
            hit_keys = {
                "attacker_key": "pirates-attack-hit-no-boarding-you",
                "defender_key": "pirates-attack-hit-no-boarding-them",
                "observer_key": "pirates-attack-hit-no-boarding",
                "brief_attacker_key": "pirates-attack-hit-no-boarding-you-brief",
                "brief_defender_key": "pirates-attack-hit-no-boarding-them-brief",
                "brief_observer_key": "pirates-attack-hit-no-boarding-brief",
            }
        _broadcast_combat_event(
            game,
            attacker,
            defender,
            **hit_keys,
            attack_total=attack_roll,
            defense_total=defense_roll,
        )

        # Give XP to attacker
        xp_gain = random.randint(50, 150)
        attacker.leveling.give_xp(
            game,
            attacker.name,
            xp_gain,
            moon_mult,
            global_xp_multiplier,
            reason="attack",
        )

        boarding_pending = False
        if allow_boarding:
            boarding_pending = game.begin_boarding(
                attacker, defender, attack_bonus, defense_bonus
            )

        return CombatResult(
            hit=True,
            attack_roll=attack_roll,
            defense_roll=defense_roll,
            attack_bonus=attack_bonus,
            defense_bonus=defense_bonus,
            xp_gained=int(xp_gain * total_mult),
            boarding_pending=boarding_pending,
        )
    _broadcast_combat_event(
        game,
        attacker,
        defender,
        attacker_key="pirates-attack-miss-you",
        defender_key="pirates-attack-miss-them",
        observer_key="pirates-attack-miss",
        brief_attacker_key="pirates-attack-miss-you-brief",
        brief_defender_key="pirates-attack-miss-them-brief",
        brief_observer_key="pirates-attack-miss-brief",
        attack_total=attack_roll,
        defense_total=defense_roll,
    )

    xp_gain = random.randint(30, 100)
    defender.leveling.give_xp(
        game,
        defender.name,
        xp_gain,
        moon_mult,
        global_xp_multiplier,
        reason="defense",
    )
    return CombatResult(
        hit=False,
        attack_roll=attack_roll,
        defense_roll=defense_roll,
        attack_bonus=attack_bonus,
        defense_bonus=defense_bonus,
        xp_gained=int(xp_gain * total_mult),
    )


def _broadcast_combat_event(
    game: "PiratesGame",
    attacker: "PiratesPlayer",
    defender: "PiratesPlayer",
    *,
    attacker_key: str,
    defender_key: str,
    observer_key: str,
    brief_attacker_key: str | None = None,
    brief_defender_key: str | None = None,
    brief_observer_key: str | None = None,
    **kwargs,
) -> None:
    """Render one combat event exactly once for each listener role."""
    for listener in game.players:
        user = game.get_user(listener)
        if not user:
            continue
        if listener.id == attacker.id:
            key = (
                brief_attacker_key
                if brief_attacker_key and game._wants_brief(user)
                else attacker_key
            )
        elif listener.id == defender.id:
            key = (
                brief_defender_key
                if brief_defender_key and game._wants_brief(user)
                else defender_key
            )
        else:
            key = (
                brief_observer_key
                if brief_observer_key and game._wants_brief(user)
                else observer_key
            )
        payload = game._resolve_broadcast_kwargs(
            user.locale,
            {
                "attacker": attacker,
                "defender": defender,
                "target": defender,
                **kwargs,
            },
        )
        user.speak_l(key, buffer="game", **payload)


def push_defender(
    game: "PiratesGame",
    attacker: "PiratesPlayer",
    defender: "PiratesPlayer",
    direction: str,
) -> None:
    """Push the defender in the specified direction."""
    if direction not in {"left", "right"}:
        raise ValueError(f"Unsupported boarding direction: {direction}")
    push_amount = random.randint(3, 8) + skills.get_push_bonus(attacker)
    if direction == "left":
        push_amount = -push_amount

    old_pos = defender.position
    defender.position = max(1, min(40, defender.position + push_amount))
    actual_distance = abs(defender.position - old_pos)
    game.charted_tiles[defender.position] = True

    direction_key = f"pirates-dir-{direction}"
    for listener in game.players:
        user = game.get_user(listener)
        if not user:
            continue
        if listener.id == attacker.id:
            key = (
                "pirates-push-you-brief"
                if game._wants_brief(user)
                else "pirates-push-you"
            )
        elif listener.id == defender.id:
            key = (
                "pirates-push-them-brief"
                if game._wants_brief(user)
                else "pirates-push-them"
            )
        else:
            key = (
                "pirates-push-brief"
                if game._wants_brief(user)
                else "pirates-push"
            )
        payload = game._resolve_broadcast_kwargs(
            user.locale,
            {
                "attacker": attacker,
                "defender": defender,
                "target": defender,
                "direction": Localization.get(user.locale, direction_key),
                "old_pos": old_pos,
                "new_pos": defender.position,
                "position": defender.position,
                "distance": actual_distance,
                "bonus": skills.get_push_bonus(attacker),
            },
        )
        user.speak_l(key, buffer="game", **payload)
    game._check_gem_collection(defender)


def attempt_gem_steal(
    game: "PiratesGame",
    attacker: "PiratesPlayer",
    defender: "PiratesPlayer",
    attack_bonus: int,
    defense_bonus: int,
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
    if not defender.gems:
        _broadcast_combat_event(
            game,
            attacker,
            defender,
            attacker_key="pirates-steal-no-gems-you",
            defender_key="pirates-steal-no-gems-defender",
            observer_key="pirates-steal-no-gems",
            brief_attacker_key="pirates-steal-no-gems-you-brief",
            brief_defender_key="pirates-steal-no-gems-defender-brief",
            brief_observer_key="pirates-steal-no-gems-brief",
        )
        return False

    steal_roll = random.randint(1, 6) + attack_bonus
    defend_roll = random.randint(1, 6) + defense_bonus

    _broadcast_combat_event(
        game,
        attacker,
        defender,
        attacker_key="pirates-steal-rolls-you",
        defender_key="pirates-steal-rolls-defender",
        observer_key="pirates-steal-rolls-observer",
        brief_attacker_key="pirates-steal-rolls-you-brief",
        brief_defender_key="pirates-steal-rolls-defender-brief",
        brief_observer_key="pirates-steal-rolls-observer-brief",
        steal=steal_roll,
        defend=defend_roll,
    )

    if steal_roll > defend_roll:
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
            for listener in game.players:
                user = game.get_user(listener)
                if not user:
                    continue
                if listener.id == attacker.id:
                    key = (
                        "pirates-steal-success-you-brief"
                        if game._wants_brief(user)
                        else "pirates-steal-success-you"
                    )
                elif listener.id == defender.id:
                    key = (
                        "pirates-steal-success-them-brief"
                        if game._wants_brief(user)
                        else "pirates-steal-success-them"
                    )
                else:
                    key = (
                        "pirates-steal-success-brief"
                        if game._wants_brief(user)
                        else "pirates-steal-success"
                    )
                payload = game._resolve_broadcast_kwargs(
                    user.locale,
                    {
                        "attacker": attacker,
                        "defender": defender,
                        "target": defender,
                        "gem": Localization.get(user.locale, gem_name_key),
                        "attacker_score": attacker.score,
                        "defender_score": defender.score,
                    },
                )
                user.speak_l(key, buffer="game", **payload)
            return True

    _broadcast_combat_event(
        game,
        attacker,
        defender,
        attacker_key="pirates-steal-failed-you",
        defender_key="pirates-steal-failed-defender",
        observer_key="pirates-steal-failed",
        brief_attacker_key="pirates-steal-failed-you-brief",
        brief_defender_key="pirates-steal-failed-defender-brief",
        brief_observer_key="pirates-steal-failed-brief",
        steal=steal_roll,
        defend=defend_roll,
    )
    return False
