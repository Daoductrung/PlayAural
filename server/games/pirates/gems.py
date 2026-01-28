"""
Gem System for Pirates of the Lost Seas.

Defines gem types, values, and placement logic.
"""

import random

# Gem names indexed by type (0-17)
GEM_NAMES: dict[int, str] = {
    0: "pirates-gem-0",
    1: "pirates-gem-1",
    2: "pirates-gem-2",
    3: "pirates-gem-3",
    4: "pirates-gem-4",
    5: "pirates-gem-5",
    6: "pirates-gem-6",
    7: "pirates-gem-7",
    8: "pirates-gem-8",
    9: "pirates-gem-9",
    10: "pirates-gem-10",
    11: "pirates-gem-11",
    12: "pirates-gem-12",
    13: "pirates-gem-13",
    14: "pirates-gem-14",
    15: "pirates-gem-15",
    16: "pirates-gem-16",
    17: "pirates-gem-17",
}

# Gem types with special values (2 points)
RARE_GEMS = {6, 8, 11, 12}

# Legendary gem (3 points)
LEGENDARY_GEM = 17

# Total number of gem types
TOTAL_GEM_TYPES = 18


def get_gem_value(gem_type: int) -> int:
    """
    Get the point value of a gem by its type index.

    Args:
        gem_type: The gem type (0-17)

    Returns:
        The point value (1, 2, or 3)
    """
    if gem_type == LEGENDARY_GEM:
        return 3
    if gem_type in RARE_GEMS:
        return 2
    return 1


def get_gem_name(gem_type: int) -> str:
    """
    Get the name of a gem by its type index.

    Args:
        gem_type: The gem type (0-17)

    Returns:
        The gem name, or "unknown gem" if invalid
    """
    return GEM_NAMES.get(gem_type, "unknown gem")


def calculate_score_from_gems(gems: list[int]) -> int:
    """
    Calculate total score from a list of gem types.

    Args:
        gems: List of gem type indices

    Returns:
        Total score
    """
    if not gems:
        return 0
    return sum(get_gem_value(gem) for gem in gems)


def place_gems(map_size: int = 40) -> dict[int, int]:
    """
    Place all gems randomly across the map.

    Args:
        map_size: Total number of tiles (default 40)

    Returns:
        Dictionary mapping position -> gem_type (-1 if no gem)
    """
    gem_positions: dict[int, int] = {}

    # Initialize all positions with no gems
    for i in range(1, map_size + 1):
        gem_positions[i] = -1

    # Place all 18 gems randomly
    available_positions = list(range(1, map_size + 1))
    random.shuffle(available_positions)

    for gem_type in range(TOTAL_GEM_TYPES):
        pos = available_positions.pop()
        gem_positions[pos] = gem_type

    return gem_positions


from ...messages.localization import Localization

def format_gem_list(gems: list[int], locale: str = "en") -> str:
    """
    Format a list of gems as a comma-separated string.

    Args:
        gems: List of gem type indices
        locale: Locale to format in (default "en")

    Returns:
        Formatted string like "ruby, diamond, emerald"
    """
    if not gems:
        return Localization.get(locale, "pirates-gem-none")
    gem_names = [Localization.get(locale, get_gem_name(gem)) for gem in gems]
    return Localization.format_list(locale, gem_names)
