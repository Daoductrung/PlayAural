"""
Leveling System for Pirates of the Lost Seas.

Handles XP gain, level-ups, and skill unlock detection.
Skill unlock levels are defined on each skill class - this system reads from them.

This class inherits from DataClassJSONMixin to ensure serializability.
The game object is NEVER stored - it is only passed as a parameter to methods.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mashumaro.mixins.json import DataClassJSONMixin

from ...messages.localization import Localization
if TYPE_CHECKING:
    from .game import PiratesGame
    from .skills import Skill


def get_xp_for_level(level: int) -> int:
    """Get the XP required to reach a specific level."""
    return level * 20


@dataclass
class LevelingSystem(DataClassJSONMixin):
    """
    Manages a player's experience and level progression.

    Tied to a specific player via user_id.
    Skill unlock levels are read from the skill singletons in skills.py.

    The game object is NEVER stored - it is only passed as a parameter to methods.
    This ensures the leveling system remains serializable.
    """

    user_id: str
    level: int = 0
    xp: int = 0

    def get_xp_to_next_level(self) -> int:
        """Get XP needed to reach the next level."""
        return get_xp_for_level(self.level + 1) - self.xp

    def get_xp_progress(self) -> tuple[int, int]:
        """Get current XP and XP needed for next level."""
        current_level_xp = get_xp_for_level(self.level)
        next_level_xp = get_xp_for_level(self.level + 1)
        progress = self.xp - current_level_xp
        needed = next_level_xp - current_level_xp
        return progress, needed

    def can_level_up(self) -> bool:
        """Check if the player has enough XP to level up."""
        return self.xp >= get_xp_for_level(self.level + 1)

    def get_unlocked_skills(self) -> list["Skill"]:
        """Get list of skills unlocked at or below current level."""
        from .skills import ALL_SKILLS
        return [
            skill for skill in ALL_SKILLS
            if skill.required_level <= self.level
        ]

    def get_locked_skills(self) -> list["Skill"]:
        """Get list of skills not yet unlocked."""
        from .skills import ALL_SKILLS
        return [
            skill for skill in ALL_SKILLS
            if skill.required_level > self.level
        ]

    def get_next_skill_unlock(self) -> tuple[int, "Skill"] | None:
        """Get the next skill unlock (level, skill) or None if all unlocked."""
        locked = self.get_locked_skills()
        if not locked:
            return None

        # Find the skill with lowest required level above current
        next_skill = min(locked, key=lambda s: s.required_level)
        return next_skill.required_level, next_skill

    def get_skills_at_level(self, level: int) -> list["Skill"]:
        """Get skills that unlock exactly at the given level."""
        from .skills import ALL_SKILLS
        return [
            skill for skill in ALL_SKILLS
            if skill.required_level == level
        ]

    def give_xp(
        self,
        game: "PiratesGame",
        player_name: str,
        base_xp: int,
        golden_moon_multiplier: float = 1.0,
        global_multiplier: float = 1.0
    ) -> list["Skill"]:
        """
        Give XP to this leveling system and process level ups.

        Args:
            game: The game instance for announcements
            player_name: Name of the player for announcements
            base_xp: Base XP amount to give
            golden_moon_multiplier: Multiplier from golden moon (default 1.0)
            global_multiplier: Global XP multiplier from game options (default 1.0)

        Returns:
            List of newly unlocked skills
        """
        total_multiplier = golden_moon_multiplier * global_multiplier
        xp_gained = int(base_xp * total_multiplier)
        self.xp += xp_gained

        # Announce XP gain
        game.broadcast_l("pirates-xp-gained", xp=xp_gained)

        # Get skill manager for this player to check unlocks
        player = game.get_player_by_id(self.user_id)
        if not player:
            return []

        # Process level ups
        starting_level = self.level
        skills_unlocked: list["Skill"] = []

        while self.can_level_up():
            self.level += 1

            # Check for skill unlocks at this level
            newly_unlocked = self.get_skills_at_level(self.level)
            skills_unlocked.extend(newly_unlocked)

        # Announce level ups if any
        if self.level > starting_level:
            game.play_sound("game_pig/win.ogg", volume=80)
            levels_gained = self.level - starting_level
            user = game.get_user(player)

            if levels_gained == 1:
                if user:
                    user.speak_l("pirates-level-up-you", level=self.level)
                game.broadcast_l(
                    "pirates-level-up",
                    player=player_name,
                    level=self.level,
                    exclude=player
                )
            else:
                if user:
                    user.speak_l(
                        "pirates-level-up-multiple-you",
                        levels=levels_gained,
                        level=self.level
                    )
                game.broadcast_l(
                    "pirates-level-up-multiple",
                    player=player_name,
                    levels=levels_gained,
                    level=self.level,
                    exclude=player
                )

            # Announce unlocked skills in a single message
            # Announce unlocked skills
            if skills_unlocked:
                # For the player leveling up
                if user:
                    skill_names = ", ".join(Localization.get(user.locale, skill.name) for skill in skills_unlocked)
                    user.speak_l("pirates-skills-unlocked-you", skills=skill_names)
                
                # For other players (manual broadcast)
                for p in game.get_active_players():
                    if p.name == player_name:
                        continue
                    u = game.get_user(p)
                    if u:
                        skill_names = ", ".join(Localization.get(u.locale, skill.name) for skill in skills_unlocked)
                        u.speak_l(
                            "pirates-skills-unlocked",
                            player=player_name,
                            skills=skill_names
                        )

        return skills_unlocked

    def has_skill_unlocked(self, skill: "Skill") -> bool:
        """Check if a specific skill is unlocked based on current level."""
        return self.level >= skill.required_level
