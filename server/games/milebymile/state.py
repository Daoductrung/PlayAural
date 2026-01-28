"""Race state management for Mile by Mile."""

from dataclasses import dataclass, field

from mashumaro.mixins.json import DataClassJSONMixin

from .cards import Card, HazardType, SafetyType


# Set of non-critical problems (hazards that don't prevent playing distance cards)
NON_CRITICAL_PROBLEMS: set[str] = {HazardType.SPEED_LIMIT}


def is_critical_problem(hazard: str) -> bool:
    """Check if a hazard is a critical problem.

    Critical problems prevent playing distance cards entirely.
    Non-critical problems (like speed limit) only restrict but don't block.

    Args:
        hazard: The hazard type to check.

    Returns:
        True if the hazard is critical, False otherwise.
    """
    return hazard not in NON_CRITICAL_PROBLEMS


@dataclass
class RaceState(DataClassJSONMixin):
    """Per-team race state for Mile by Mile (resets each race)."""

    miles: int = 0
    problems: list[str] = field(default_factory=list)  # Active hazard types
    safeties: list[str] = field(default_factory=list)  # Played safety types
    battle_pile: list[Card] = field(default_factory=list)  # Cards played on/by team
    used_200_mile: bool = False
    dirty_trick_count: int = 0
    has_karma: bool = True

    def has_problem(self, problem_type: str) -> bool:
        """Check if team has a specific problem."""
        return problem_type in self.problems

    def has_safety(self, safety_type: str) -> bool:
        """Check if team has a specific safety."""
        return safety_type in self.safeties

    def has_any_problem(self) -> bool:
        """Check if team has any critical problems.

        Non-critical problems like speed limit are excluded.
        """
        return any(is_critical_problem(p) for p in self.problems)

    def add_problem(self, problem_type: str) -> None:
        """Add a problem to the team."""
        if problem_type not in self.problems:
            self.problems.append(problem_type)

    def remove_problem(self, problem_type: str) -> None:
        """Remove a problem from the team."""
        if problem_type in self.problems:
            self.problems.remove(problem_type)

    def add_safety(self, safety_type: str) -> None:
        """Add a safety to the team."""
        if safety_type not in self.safeties:
            self.safeties.append(safety_type)

    def can_play_distance(self) -> bool:
        """Check if team can play distance cards."""
        # Right of Way only protects against STOP and SPEED_LIMIT
        if self.has_safety(SafetyType.RIGHT_OF_WAY):
            # Can still be blocked by other problems (accident, flat tire, out of gas)
            for problem in self.problems:
                if problem not in (HazardType.STOP, HazardType.SPEED_LIMIT):
                    return False
            return True
        # Otherwise, can't have any critical problems
        return not self.has_any_problem()

    def reset(self) -> None:
        """Reset state for a new race."""
        self.miles = 0
        self.problems = [HazardType.STOP]  # Everyone starts stopped
        self.safeties = []
        self.battle_pile = []
        self.used_200_mile = False
        self.dirty_trick_count = 0
        self.has_karma = True
