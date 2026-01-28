"""
Bot AI Logic for Pirates of the Lost Seas.

Bots follow the exact same rules as human players - they use the same action
system and skill mechanics. This module provides intelligent decision-making
to determine which actions to take.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .game import PiratesGame
    from .player import PiratesPlayer
    from .skills import Skill

from . import combat
from . import skills
from .skills import (
    SWORD_FIGHTER,
    PUSH,
    SKILLED_CAPTAIN,
    PORTAL,
    GEM_SEEKER,
    BATTLESHIP,
    DOUBLE_DEVASTATION,
    SKILLS_BY_ID,
)


@dataclass
class BotDecision:
    """Represents a bot's decision for this turn."""

    action_id: str
    target: "PiratesPlayer | None" = None
    skill_name: str | None = None
    direction: str | None = None


def bot_think(game: "PiratesGame", player: "PiratesPlayer") -> str | None:
    """
    Determine what action a bot should take.

    Bots follow the same rules as humans - they select from available actions
    based on game state analysis.

    Args:
        game: The game instance
        player: The bot player

    Returns:
        Action ID to execute, or None if no action
    """
    decision = _analyze_and_decide(game, player)
    if decision:
        # Store decision context for follow-up handlers
        game._bot_decision = decision
        return decision.action_id
    return None


def _analyze_and_decide(game: "PiratesGame", player: "PiratesPlayer") -> BotDecision | None:
    """
    Analyze game state and decide on the best action.

    Decision priority:
    1. If we have attack buff skills available and targets nearby, consider activating them
    2. If targets have lots of gems and we can attack, prioritize attacking
    3. If gems are nearby, move toward them
    4. If no gems nearby but player is near one, consider portal
    5. Default to moving toward nearest gem or random movement
    """
    # Gather intel
    targets = combat.get_targets_in_range(game, player)
    closest_gem = _find_closest_gem(game, player)
    gem_distance = abs(player.position - closest_gem) if closest_gem != -1 else 999

    # Check if any target has valuable gems worth attacking for
    valuable_target = _find_valuable_target(game, player, targets)

    # Check our buff status using skill singletons
    has_attack_buff = (
        SWORD_FIGHTER.is_active(player) or
        SKILLED_CAPTAIN.is_active(player)
    )

    # Decision logic
    decision = None

    # Priority 1: If we want to attack a valuable target
    if valuable_target and targets:
        # Check if target has strong defense buffs
        target_has_defense = (
            PUSH.is_active(valuable_target) or
            SKILLED_CAPTAIN.is_active(valuable_target)
        )

        # If target has defense and we don't have attack buff, consider buffing first
        if target_has_defense and not has_attack_buff:
            # Try to activate sword fighter or skilled captain first
            if SWORD_FIGHTER.is_unlocked(player):
                can_use, _ = SWORD_FIGHTER.can_perform(game, player)
                if can_use and random.random() < 0.8:  # 80% chance to buff first
                    return BotDecision(action_id="use_skill", skill_name="sword_fighter")

            if SKILLED_CAPTAIN.is_unlocked(player):
                can_use, _ = SKILLED_CAPTAIN.can_perform(game, player)
                if can_use and random.random() < 0.8:
                    return BotDecision(action_id="use_skill", skill_name="skilled_captain")

        # Decide whether to attack
        attack_chance = _calculate_attack_chance(
            game, player, valuable_target,
            has_attack_buff, target_has_defense, gem_distance
        )

        if random.random() < attack_chance:
            # Use battleship if available and multiple targets or valuable target
            if BATTLESHIP.is_unlocked(player):
                can_use, _ = BATTLESHIP.can_perform(game, player)
                if can_use and (len(targets) >= 2 or valuable_target.score >= 3):
                    return BotDecision(
                        action_id="use_skill",
                        skill_name="battleship",
                        target=valuable_target
                    )

            # Regular cannonball attack
            return BotDecision(action_id="cannonball", target=valuable_target)

    # Priority 2: Move toward nearby gem
    if closest_gem != -1 and gem_distance <= 5:
        return _decide_movement_toward(game, player, closest_gem)

    # Priority 3: Consider portal if gems are far but another player is near one
    if gem_distance > 10 and PORTAL.is_unlocked(player):
        can_use, _ = PORTAL.can_perform(game, player)
        if can_use:
            # Check if another player is closer to a gem
            other_near_gem = _is_other_player_near_gem(game, player)
            if other_near_gem and random.random() < 0.6:  # 60% chance to portal
                return BotDecision(action_id="use_skill", skill_name="portal")

    # Priority 4: Use gem seeker if we have uses and can't find gems
    if gem_distance > 15:
        if GEM_SEEKER.is_unlocked(player):
            can_use, _ = GEM_SEEKER.can_perform(game, player)
            if can_use and random.random() < 0.3:  # 30% chance
                return BotDecision(action_id="use_skill", skill_name="gem_seeker")

    # Priority 5: Activate double devastation if targets are just out of range
    if DOUBLE_DEVASTATION.is_unlocked(player):
        can_use, _ = DOUBLE_DEVASTATION.can_perform(game, player)
        if can_use:
            # Check if there are targets in extended range but not current range
            extended_targets = combat.get_targets_in_range(game, player, max_range=10)
            current_targets = combat.get_targets_in_range(game, player, max_range=5)
            if len(extended_targets) > len(current_targets) and random.random() < 0.5:
                return BotDecision(action_id="use_skill", skill_name="double_devastation")

    # Default: Move toward closest gem or random
    return _decide_movement(game, player)


def _find_closest_gem(game: "PiratesGame", player: "PiratesPlayer") -> int:
    """Find the position of the closest uncollected gem."""
    closest_pos = -1
    closest_distance = 999

    for pos, gem_type in game.gem_positions.items():
        if gem_type != -1:
            distance = abs(player.position - pos)
            if distance < closest_distance:
                closest_distance = distance
                closest_pos = pos

    return closest_pos


def _find_valuable_target(
    game: "PiratesGame",
    player: "PiratesPlayer",
    targets: list["PiratesPlayer"]
) -> "PiratesPlayer | None":
    """
    Find the most valuable target to attack.

    Considers:
    - Number of gems the target has
    - Target's score
    - Whether target is a threat (high level, high score)
    """
    if not targets:
        return None

    # Score each target
    scored_targets = []
    for target in targets:
        score = 0

        # More gems = more valuable
        score += len(target.gems) * 3

        # Higher score = more valuable
        score += target.score * 2

        # Higher level = slight threat bonus
        score += target.level // 10

        scored_targets.append((target, score))

    # Sort by score descending
    scored_targets.sort(key=lambda x: x[1], reverse=True)

    # Return the highest scored target if it has any value
    if scored_targets and scored_targets[0][1] > 0:
        return scored_targets[0][0]

    # If no target has gems, still return one for XP (50% chance)
    if targets and random.random() < 0.5:
        return random.choice(targets)

    return None


def _calculate_attack_chance(
    game: "PiratesGame",
    player: "PiratesPlayer",
    target: "PiratesPlayer",
    has_attack_buff: bool,
    target_has_defense: bool,
    gem_distance: int
) -> float:
    """
    Calculate the probability that the bot should attack.

    Factors:
    - Target has gems: higher chance
    - We have attack buff: higher chance
    - Target has defense buff: lower chance
    - Gems are far away: higher chance (nothing better to do)
    - We need gems: higher chance
    """
    base_chance = 0.3

    # Target has gems - big bonus
    if target.has_gems():
        base_chance += 0.3
        # Even more if target has multiple gems
        base_chance += min(0.2, len(target.gems) * 0.05)

    # We have attack buff - bonus
    if has_attack_buff:
        base_chance += 0.15

    # Target has defense buff - penalty
    if target_has_defense:
        base_chance -= 0.2

    # Gems are far - might as well attack
    if gem_distance > 10:
        base_chance += 0.15
    elif gem_distance > 5:
        base_chance += 0.05

    # We're behind on score - more aggressive
    if player.score < target.score:
        base_chance += 0.1

    # Clamp to valid probability
    return max(0.1, min(0.9, base_chance))


def _is_other_player_near_gem(game: "PiratesGame", player: "PiratesPlayer") -> bool:
    """Check if another player is within 5 tiles of an uncollected gem."""
    for other in game.get_active_players():
        if other.id == player.id:
            continue

        for pos, gem_type in game.gem_positions.items():
            if gem_type != -1:
                if abs(other.position - pos) <= 5:
                    return True

    return False


def _decide_movement(game: "PiratesGame", player: "PiratesPlayer") -> BotDecision:
    """Decide on a movement action."""
    closest_gem = _find_closest_gem(game, player)

    if closest_gem != -1:
        return _decide_movement_toward(game, player, closest_gem)

    # No gems left, random movement
    direction = random.choice(["left", "right"])
    return _get_best_move_action(game, player, direction)


def _decide_movement_toward(
    game: "PiratesGame",
    player: "PiratesPlayer",
    target_pos: int
) -> BotDecision:
    """Decide movement toward a target position."""
    if player.position < target_pos:
        direction = "right"
    elif player.position > target_pos:
        direction = "left"
    else:
        # Already at position, move randomly
        direction = random.choice(["left", "right"])
        return _get_best_move_action(game, player, direction)

    return _get_best_move_action(game, player, direction, target_pos)


def _get_best_move_action(
    game: "PiratesGame",
    player: "PiratesPlayer",
    direction: str,
    target_pos: int | None = None
) -> BotDecision:
    """Get the best available move action for the given direction."""
    # Determine how many tiles we can move based on level
    if player.level >= 150:
        max_tiles = 3
    elif player.level >= 15:
        max_tiles = 2
    else:
        max_tiles = 1

    # If we have a target, don't overshoot it
    if target_pos is not None:
        distance = abs(player.position - target_pos)
        max_tiles = min(max_tiles, distance)

    # Select appropriate move action
    if max_tiles >= 3:
        action = f"move_3_{direction}"
    elif max_tiles == 2:
        action = f"move_2_{direction}"
    else:
        action = f"move_{direction}"

    return BotDecision(action_id=action, direction=direction)


# =============================================================================
# Bot response handlers for multi-step actions
# =============================================================================


def bot_select_target(
    game: "PiratesGame",
    player: "PiratesPlayer",
    targets: list["PiratesPlayer"]
) -> "PiratesPlayer | None":
    """
    Select a target for the bot to attack.

    Uses the pre-computed decision if available, otherwise picks intelligently.
    """
    if not targets:
        return None

    # Check if we have a pre-computed decision
    decision = getattr(game, "_bot_decision", None)
    if decision and decision.target and decision.target in targets:
        return decision.target

    # Fall back to finding valuable target
    return _find_valuable_target(game, player, targets) or random.choice(targets)


def bot_select_boarding_action(
    game: "PiratesGame",
    player: "PiratesPlayer",
    defender: "PiratesPlayer",
    can_steal: bool
) -> str:
    """
    Select a boarding action for the bot.

    Considers:
    - Whether stealing is possible and beneficial
    - Our attack bonuses vs their defense bonuses
    """
    if not can_steal or not defender.has_gems():
        return random.choice(["left", "right"])

    # Calculate steal success probability
    attack_bonus = skills.get_attack_bonus(player)
    defense_bonus = skills.get_defense_bonus(defender)

    # If we have advantage, higher chance to steal
    advantage = attack_bonus - defense_bonus

    if advantage >= 2:
        steal_chance = 0.8
    elif advantage >= 0:
        steal_chance = 0.6
    elif advantage >= -2:
        steal_chance = 0.4
    else:
        steal_chance = 0.2

    # More gems = more tempting to steal
    steal_chance += min(0.2, len(defender.gems) * 0.05)

    if random.random() < steal_chance:
        return "steal"

    return random.choice(["left", "right"])


def bot_select_portal_ocean(
    game: "PiratesGame",
    player: "PiratesPlayer",
    ocean_options: list[tuple[int, str]]
) -> int | None:
    """
    Select an ocean for the bot to portal to.

    Prefers oceans where:
    - A gem is nearby
    - Players with gems are located
    """
    if not ocean_options:
        return None

    scored_oceans = []
    for ocean_num, ocean_name in ocean_options:
        score = 0
        ocean_start = ocean_num * 10 + 1
        ocean_end = (ocean_num + 1) * 10

        # Check for gems in this ocean
        for pos in range(ocean_start, ocean_end + 1):
            if game.gem_positions.get(pos, -1) != -1:
                score += 3

        # Check for players with gems in this ocean
        for other in game.get_active_players():
            if other.id == player.id:
                continue
            if ocean_start <= other.position <= ocean_end:
                if other.has_gems():
                    score += len(other.gems) * 2
                else:
                    score += 1  # Slight bonus for company

        scored_oceans.append((ocean_num, score))

    # Sort by score descending
    scored_oceans.sort(key=lambda x: x[1], reverse=True)

    # Pick the best ocean, with some randomness
    if scored_oceans:
        if random.random() < 0.8:  # 80% chance to pick best
            return scored_oceans[0][0]
        else:
            return random.choice([o[0] for o in scored_oceans])

    return ocean_options[0][0]


def bot_select_skill_choice(
    game: "PiratesGame",
    player: "PiratesPlayer",
    skill_options: list[str]
) -> str:
    """
    Select a skill from the skill menu.

    Uses the pre-computed decision if available.
    """
    decision = getattr(game, "_bot_decision", None)
    if decision and decision.skill_name:
        # Find the matching skill label in options
        skill = SKILLS_BY_ID.get(decision.skill_name)
        if skill:
            label = skill.get_menu_label(player)
            if label in skill_options:
                return label

    # Fall back to "Back" if no valid skill found
    return "Back"
