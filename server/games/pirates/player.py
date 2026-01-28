"""
Player dataclass for Pirates of the Lost Seas.

Contains player state including position, score, gems, leveling system, and skill state.

Inherits from Player which has DataClassJSONMixin, so this class is serializable.
All fields are primitive types or simple serializable dataclasses.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..base import Player
from .leveling import LevelingSystem

if TYPE_CHECKING:
    pass


@dataclass
class PiratesPlayer(Player):
    """
    Player state for Pirates of the Lost Seas.

    Skill state is stored in simple dicts that serialize easily:
    - skill_cooldowns: remaining cooldown turns per skill
    - skill_active: remaining active turns for buffs
    - skill_uses: remaining uses for limited-use skills

    The game object is NEVER stored on this class - it is only passed as a
    parameter to methods. This ensures the player remains serializable.
    """

    position: int = 0
    score: int = 0
    gems: list[int] = field(default_factory=list)

    # Leveling system (serialized - has DataClassJSONMixin)
    _leveling: LevelingSystem = field(default=None)  # type: ignore

    # Skill state - simple dicts that serialize easily
    skill_cooldowns: dict[str, int] = field(default_factory=dict)
    skill_active: dict[str, int] = field(default_factory=dict)
    skill_uses: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize the leveling system if not set."""
        if self._leveling is None:
            self._leveling = LevelingSystem(user_id=self.id)

    @property
    def leveling(self) -> LevelingSystem:
        """Get the leveling system for this player."""
        return self._leveling

    @property
    def level(self) -> int:
        """Shortcut to get the player's level."""
        return self._leveling.level

    @property
    def xp(self) -> int:
        """Shortcut to get the player's XP."""
        return self._leveling.xp

    def add_gem(self, gem_type: int, gem_value: int) -> None:
        """Add a gem to the player's collection and update score."""
        self.gems.append(gem_type)
        self.score += gem_value

    def remove_gem(self, gem_index: int) -> int | None:
        """Remove and return a gem at the given index, or None if invalid."""
        if 0 <= gem_index < len(self.gems):
            return self.gems.pop(gem_index)
        return None

    def has_gems(self) -> bool:
        """Check if the player has any gems."""
        return len(self.gems) > 0

    def recalculate_score(self, get_gem_value: callable) -> None:
        """Recalculate score from current gems using the provided value function."""
        self.score = sum(get_gem_value(gem) for gem in self.gems)
