"""
Scoring logic for Tradeoff game.

Handles set detection and optimal scoring combinations.
"""

from itertools import combinations


# Set definitions with point values
# (name_key, num_dice, points)
SET_DEFINITIONS = {
    "triple": ("tradeoff-set-triple", 3, 3),
    "mini_straight": ("tradeoff-set-mini-straight", 4, 7),
    "group": ("tradeoff-set-group", 5, 8),
    "double_triple": ("tradeoff-set-double-triple", 6, 10),
    "straight": ("tradeoff-set-straight", 5, 12),
    "double_group": ("tradeoff-set-double-group", 10, 30),
    "all_groups": ("tradeoff-set-all-groups", 15, 50),
    "all_triplets": ("tradeoff-set-all-triplets", 15, 50),
}


def is_triple(dice: list[int]) -> bool:
    """Check if dice form a triple (3 of the same value)."""
    return len(dice) == 3 and dice[0] == dice[1] == dice[2]


def is_mini_straight(dice: list[int]) -> bool:
    """Check if dice form a mini straight (4 consecutive values)."""
    if len(dice) != 4:
        return False
    sorted_dice = sorted(dice)
    # Check for any 4 consecutive: 1-2-3-4, 2-3-4-5, or 3-4-5-6
    return sorted_dice in [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]


def is_group(dice: list[int]) -> bool:
    """Check if dice form a group (5 of the same value)."""
    return len(dice) == 5 and len(set(dice)) == 1


def is_double_triple(dice: list[int]) -> bool:
    """Check if dice form a double triple (3 of 2 kinds, 6 dice total)."""
    if len(dice) != 6:
        return False
    counts = {}
    for d in dice:
        counts[d] = counts.get(d, 0) + 1
    # Need exactly two values, each appearing 3 times
    return sorted(counts.values()) == [3, 3]


def is_straight(dice: list[int]) -> bool:
    """Check if dice form a straight (5 consecutive values)."""
    if len(dice) != 5:
        return False
    sorted_dice = sorted(dice)
    # Check for any 5 consecutive: 1-2-3-4-5 or 2-3-4-5-6
    return sorted_dice in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]]


def is_double_group(dice: list[int]) -> bool:
    """Check if dice form a double group (5 of 2 kinds, 10 dice total)."""
    if len(dice) != 10:
        return False
    counts = {}
    for d in dice:
        counts[d] = counts.get(d, 0) + 1
    # Need exactly two values, each appearing 5 times
    return sorted(counts.values()) == [5, 5]


def is_all_groups(dice: list[int]) -> bool:
    """Check if dice form all groups (3 groups of 5, 15 dice total)."""
    if len(dice) != 15:
        return False
    counts = {}
    for d in dice:
        counts[d] = counts.get(d, 0) + 1
    # Need exactly three values, each appearing 5 times
    return sorted(counts.values()) == [5, 5, 5]


def is_all_triplets(dice: list[int]) -> bool:
    """Check if dice form all triplets (5 triples, 15 dice total)."""
    if len(dice) != 15:
        return False
    counts = {}
    for d in dice:
        counts[d] = counts.get(d, 0) + 1
    # Need exactly 5 values, each appearing 3 times
    return sorted(counts.values()) == [3, 3, 3, 3, 3]


def find_best_scoring(dice: list[int]) -> list[tuple[str, list[int], int]]:
    """
    Find the best combination of non-overlapping sets from dice.

    Returns list of (set_name, dice_used, points) tuples.
    Uses exhaustive search for optimal solution.
    """
    if not dice:
        return []

    # Check for the big 15-dice sets first (they're worth the same, 50 pts)
    if len(dice) == 15:
        if is_all_groups(dice):
            return [("all_groups", list(dice), 50)]
        if is_all_triplets(dice):
            return [("all_triplets", list(dice), 50)]

    # Try to find the best scoring combination
    best_score = 0
    best_sets: list[tuple[str, list[int], int]] = []

    def search(
        remaining: list[int],
        current_sets: list[tuple[str, list[int], int]],
        current_score: int
    ) -> None:
        nonlocal best_score, best_sets

        if current_score > best_score:
            best_score = current_score
            best_sets = list(current_sets)

        # If we don't have enough dice for the smallest set (3), we're done
        if len(remaining) < 3:
            return

        # Count dice values
        counts: dict[int, int] = {}
        for d in remaining:
            counts[d] = counts.get(d, 0) + 1

        # Try double group (5 of 2 kinds, 10 dice) - 30 points
        if len(remaining) >= 10:
            vals_with_5 = [v for v, c in counts.items() if c >= 5]
            if len(vals_with_5) >= 2:
                for combo in combinations(vals_with_5, 2):
                    new_remaining = list(remaining)
                    used = []
                    for v in combo:
                        for _ in range(5):
                            new_remaining.remove(v)
                            used.append(v)
                    new_sets = current_sets + [("double_group", used, 30)]
                    search(new_remaining, new_sets, current_score + 30)

        # Try straight (5 consecutive) - 12 points
        if len(remaining) >= 5:
            for start in [1, 2]:  # 1-2-3-4-5 or 2-3-4-5-6
                run = list(range(start, start + 5))
                if all(v in remaining for v in run):
                    new_remaining = list(remaining)
                    used = []
                    for v in run:
                        new_remaining.remove(v)
                        used.append(v)
                    new_sets = current_sets + [("straight", used, 12)]
                    search(new_remaining, new_sets, current_score + 12)

        # Try double triple (3 of 2 kinds, 6 dice) - 10 points
        if len(remaining) >= 6:
            vals_with_3 = [v for v, c in counts.items() if c >= 3]
            if len(vals_with_3) >= 2:
                for combo in combinations(vals_with_3, 2):
                    new_remaining = list(remaining)
                    used = []
                    for v in combo:
                        for _ in range(3):
                            new_remaining.remove(v)
                            used.append(v)
                    new_sets = current_sets + [("double_triple", used, 10)]
                    search(new_remaining, new_sets, current_score + 10)

        # Try group (5 of same) - 8 points
        if len(remaining) >= 5:
            for val, count in counts.items():
                if count >= 5:
                    new_remaining = list(remaining)
                    used = []
                    for _ in range(5):
                        new_remaining.remove(val)
                        used.append(val)
                    new_sets = current_sets + [("group", used, 8)]
                    search(new_remaining, new_sets, current_score + 8)

        # Try mini straight (4 consecutive) - 7 points
        if len(remaining) >= 4:
            for start in [1, 2, 3]:  # 1-2-3-4, 2-3-4-5, 3-4-5-6
                run = list(range(start, start + 4))
                if all(v in remaining for v in run):
                    new_remaining = list(remaining)
                    used = []
                    for v in run:
                        new_remaining.remove(v)
                        used.append(v)
                    new_sets = current_sets + [("mini_straight", used, 7)]
                    search(new_remaining, new_sets, current_score + 7)

        # Try triple (3 of same) - 3 points
        for val, count in counts.items():
            if count >= 3:
                new_remaining = list(remaining)
                used = []
                for _ in range(3):
                    new_remaining.remove(val)
                    used.append(val)
                new_sets = current_sets + [("triple", used, 3)]
                search(new_remaining, new_sets, current_score + 3)

    search(dice, [], 0)
    return best_sets
