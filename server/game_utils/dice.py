"""Dice utilities for dice-based games."""

from dataclasses import dataclass, field
import random

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class DiceSet(DataClassJSONMixin):
    """
    A set of dice with keep/lock mechanics.

    Supports:
    - Rolling any number of dice with any sides
    - Keeping dice (marking for preservation)
    - Locking dice (permanently kept until reset)
    - Toggling keep status on unlocked dice

    Typical flow:
    1. roll() - roll all dice
    2. keep(index) / unkeep(index) - mark dice to keep
    3. roll() again - kept dice become locked, unlocked dice are rerolled
    4. Repeat until all dice locked or turn ends
    5. reset() - clear all state for next turn
    """

    num_dice: int = 5
    sides: int = 6
    values: list[int] = field(default_factory=list)
    kept: list[int] = field(default_factory=list)  # Indices marked to keep
    locked: list[int] = field(
        default_factory=list
    )  # Indices that are locked (can't change)

    def __post_init__(self):
        """Initialize empty values if needed."""
        if not self.values:
            self.values = []

    @property
    def has_rolled(self) -> bool:
        """Check if dice have been rolled."""
        return len(self.values) == self.num_dice

    @property
    def unlocked_count(self) -> int:
        """Count of dice that are not locked."""
        if not self.has_rolled:
            return self.num_dice
        return sum(1 for i in range(self.num_dice) if i not in self.locked)

    @property
    def kept_unlocked_count(self) -> int:
        """Count of kept dice that are not locked (will be locked on next roll)."""
        return sum(1 for i in self.kept if i not in self.locked)

    @property
    def all_decided(self) -> bool:
        """Check if all dice are either kept or locked."""
        if not self.has_rolled:
            return False
        return all(i in self.kept or i in self.locked for i in range(self.num_dice))

    def reset(self) -> None:
        """Reset all dice state for a new turn."""
        self.values = []
        self.kept = []
        self.locked = []

    def roll(self, lock_kept: bool = True, clear_kept: bool = True) -> list[int]:
        """
        Roll the dice.

        If dice haven't been rolled yet, rolls all dice.
        Otherwise, respects kept/locked dice and rerolls the rest.

        Args:
            lock_kept: If True, kept dice become locked before rolling.
                      Set False for games where you can unkeep after rolling.
            clear_kept: If True, clears kept list after rolling.
                       Set False to preserve kept state.

        Returns:
            List of all dice values after rolling.
        """
        if not self.has_rolled:
            # First roll - roll all dice
            self.values = [random.randint(1, self.sides) for _ in range(self.num_dice)]
        else:
            if lock_kept:
                # Lock the kept dice
                for i in self.kept:
                    if i not in self.locked:
                        self.locked.append(i)

            # Roll only dice that are neither locked nor kept
            for i in range(self.num_dice):
                if i not in self.locked and i not in self.kept:
                    self.values[i] = random.randint(1, self.sides)

            if clear_kept:
                # Reset kept to just locked dice
                self.kept = list(self.locked)

        return self.values

    def is_locked(self, index: int) -> bool:
        """Check if a die at index is locked."""
        return index in self.locked

    def is_kept(self, index: int) -> bool:
        """Check if a die at index is kept."""
        return index in self.kept

    def keep(self, index: int) -> bool:
        """
        Mark a die to keep.

        Returns:
            True if successful, False if die is locked.
        """
        if index in self.locked:
            return False
        if index not in self.kept:
            self.kept.append(index)
        return True

    def unkeep(self, index: int) -> bool:
        """
        Unmark a die from being kept.

        Returns:
            True if successful, False if die is locked.
        """
        if index in self.locked:
            return False
        if index in self.kept:
            self.kept.remove(index)
        return True

    def toggle_keep(self, index: int) -> bool | None:
        """
        Toggle keep status of a die.

        Returns:
            True if now kept, False if now unkept, None if locked.
        """
        if index in self.locked:
            return None
        if index in self.kept:
            self.kept.remove(index)
            return False
        else:
            self.kept.append(index)
            return True

    def get_value(self, index: int) -> int | None:
        """Get the value of a specific die."""
        if not self.has_rolled or index >= len(self.values):
            return None
        return self.values[index]

    def get_status(self, index: int) -> str:
        """Get status string for a die: 'locked', 'kept', or ''."""
        if index in self.locked:
            return "locked"
        elif index in self.kept:
            return "kept"
        return ""

    def format_die(self, index: int, show_status: bool = True) -> str:
        """Format a single die for display."""
        if not self.has_rolled:
            return "-"

        value = str(self.values[index])
        if show_status:
            status = self.get_status(index)
            if status:
                return f"{value} ({status})"
        return value

    def format_all(self, show_status: bool = True, separator: str = ", ") -> str:
        """Format all dice for display."""
        if not self.has_rolled:
            return "-"
        parts = [self.format_die(i, show_status) for i in range(self.num_dice)]
        return separator.join(parts)

    def format_values_only(self, separator: str = ", ") -> str:
        """Format just the dice values without status."""
        if not self.has_rolled:
            return "-"
        return separator.join(str(v) for v in self.values)

    def count_value(self, value: int) -> int:
        """Count how many dice show a specific value."""
        if not self.has_rolled:
            return 0
        return sum(1 for v in self.values if v == value)

    def sum_values(self, exclude_value: int | None = None) -> int:
        """
        Sum all dice values.

        Args:
            exclude_value: If set, dice showing this value are counted as 0.
        """
        if not self.has_rolled:
            return 0
        total = 0
        for v in self.values:
            if exclude_value is not None and v == exclude_value:
                continue
            total += v
        return total

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "num_dice": self.num_dice,
            "sides": self.sides,
            "values": self.values,
            "kept": self.kept,
            "locked": self.locked,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DiceSet":
        """Deserialize from dictionary."""
        return cls(
            num_dice=data.get("num_dice", 5),
            sides=data.get("sides", 6),
            values=data.get("values", []),
            kept=data.get("kept", []),
            locked=data.get("locked", []),
        )


def roll_dice(num_dice: int = 1, sides: int = 6) -> list[int]:
    """Roll multiple dice and return their values."""
    return [random.randint(1, sides) for _ in range(num_dice)]


def roll_die(sides: int = 6) -> int:
    """Roll a single die and return its value."""
    return random.randint(1, sides)
