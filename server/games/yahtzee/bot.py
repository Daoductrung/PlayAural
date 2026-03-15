"""Bot strategy for Yahtzee."""

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import YahtzeeGame, YahtzeePlayer


def _count_dice(dice: list[int]) -> dict[int, int]:
    """Count occurrences of each die value (1-6)."""
    counts = {i: 0 for i in range(1, 7)}
    for die in dice:
        counts[die] += 1
    return counts


def bot_think(
    game: "YahtzeeGame",
    player: "YahtzeePlayer",
    *,
    calculate_score: Callable[[list[int], str], int],
    all_categories: list[str],
    upper_categories: list[str],
) -> str | None:
    """Return the bot's next action."""
    if game.current_player != player:
        return None

    if not player.dice.has_rolled:
        return "roll"

    open_categories = player.get_open_categories()
    if not open_categories:
        return None

    # Check if eligible for Yahtzee bonus (already scored 50 in Yahtzee)
    yahtzee_bonus_eligible = player.scores.get("yahtzee") == 50

    if player.rolls_left > 0:
        target = _pick_target_category(
            player.dice.values,
            open_categories,
            player.rolls_left,
            yahtzee_bonus_eligible=yahtzee_bonus_eligible,
        )

        # Yahtzee bonus override: if eligible and have 4+ of a kind,
        # keep those dice regardless of target category
        counts = _count_dice(player.dice.values)
        best_val, best_cnt = max(counts.items(), key=lambda item: (item[1], item[0]))
        if yahtzee_bonus_eligible and best_cnt >= 4:
            desired_keeps = {i for i, v in enumerate(player.dice.values) if v == best_val}
        else:
            desired_keeps = _desired_keep_indices(player.dice.values, target)

        current_keeps = {i for i in range(5) if player.dice.is_kept(i)}

        if desired_keeps != current_keeps:
            for i in range(5):
                if (i in desired_keeps) != (i in current_keeps):
                    return f"toggle_die_{i}"

        if player.rolls_left > 0 and len(desired_keeps) < 5:
            return "roll"

    return _pick_best_category_action(
        player,
        calculate_score=calculate_score,
        all_categories=all_categories,
        upper_categories=upper_categories,
    )


def _pick_target_category(
    values: list[int],
    open_categories: list[str],
    rolls_left: int,
    *,
    yahtzee_bonus_eligible: bool = False,
) -> str:
    """Choose category to pursue while rolling."""
    best_cat = open_categories[0]
    best_value = -1.0
    for cat in open_categories:
        value = _category_potential(
            values, cat, rolls_left, yahtzee_bonus_eligible=yahtzee_bonus_eligible
        )
        if value > best_value:
            best_value = value
            best_cat = cat
    return best_cat


def _category_potential(
    values: list[int],
    category: str,
    rolls_left: int,
    *,
    yahtzee_bonus_eligible: bool = False,
) -> float:
    """Heuristic value for pursuing a category with remaining rolls."""
    counts = _count_dice(values)
    best_value, best_count = max(counts.items(), key=lambda item: (item[1], item[0]))
    unique_values = sorted(set(values))
    run_len = _longest_consecutive_run(unique_values)
    dice_sum = sum(values)

    if category in ("ones", "twos", "threes", "fours", "fives", "sixes"):
        target = _upper_target_value(category)
        matched = counts[target]
        return matched * target + (5 - matched) * target * 0.35 * rolls_left

    if category == "three_kind":
        if best_count >= 3:
            reroll_count = 5 - best_count
            return float(dice_sum) + reroll_count * 1.0 * rolls_left
        need = max(0, 3 - best_count)
        return (best_count * best_value) + (need * best_value * 1.5 * rolls_left)

    if category == "four_kind":
        if best_count >= 4:
            reroll_count = 5 - best_count
            return float(dice_sum) + reroll_count * 1.0 * rolls_left
        need = max(0, 4 - best_count)
        return (best_count * best_value) + (need * best_value * 1.2 * rolls_left)

    if category == "yahtzee":
        bonus = 100.0 if yahtzee_bonus_eligible else 0.0
        if best_count == 5:
            return 50.0 + bonus
        if best_count >= 3:
            return best_count * 8.0 + (5 - best_count) * 3.0 * rolls_left + bonus * 0.1
        return best_count * 5.0 + rolls_left * 2.0

    if category == "full_house":
        shape = sorted((c for c in counts.values() if c > 0), reverse=True)
        if len(shape) >= 2 and shape[0] >= 3 and shape[1] >= 2:
            return 45.0
        if len(shape) >= 2 and shape[0] >= 3:
            return 20.0 + rolls_left * 3.0
        if len(shape) >= 2 and shape[0] >= 2 and shape[1] >= 2:
            return 24.0 + rolls_left * 3.0
        return 10.0 + rolls_left * 2.0

    if category == "small_straight":
        if run_len >= 4:
            return 35.0
        return run_len * 7.0 + rolls_left * 4.0

    if category == "large_straight":
        if run_len >= 5:
            return 48.0
        return run_len * 6.0 + rolls_left * 3.0

    if category == "chance":
        low_dice = sum(1 for v in values if v < 4)
        return float(dice_sum) + low_dice * 1.5 * rolls_left

    return 0.0


def _desired_keep_indices(values: list[int], category: str) -> set[int]:
    """Select which dice to keep while pursuing a category."""
    counts = _count_dice(values)

    if category in ("ones", "twos", "threes", "fours", "fives", "sixes"):
        target = _upper_target_value(category)
        keep = {i for i, value in enumerate(values) if value == target}
        return keep if keep else {max(range(5), key=lambda i: values[i])}

    if category in ("three_kind", "four_kind", "yahtzee"):
        best_value, _ = max(counts.items(), key=lambda item: (item[1], item[0]))
        keep = {i for i, value in enumerate(values) if value == best_value}
        return keep if keep else {max(range(5), key=lambda i: values[i])}

    if category == "full_house":
        top_values = sorted(
            (value for value, count in counts.items() if count > 0),
            key=lambda value: (counts[value], value),
            reverse=True,
        )[:2]
        keep = {i for i, value in enumerate(values) if value in top_values}
        return keep if keep else {max(range(5), key=lambda i: values[i])}

    if category in ("small_straight", "large_straight"):
        run = _best_straight_run(sorted(set(values)))
        keep: set[int] = set()
        used_values: set[int] = set()
        for i, value in enumerate(values):
            if value in run and value not in used_values:
                keep.add(i)
                used_values.add(value)
        return keep if keep else {max(range(5), key=lambda i: values[i])}

    if category == "chance":
        keep = {i for i, value in enumerate(values) if value >= 4}
        return keep if keep else {max(range(5), key=lambda i: values[i])}

    return {max(range(5), key=lambda i: values[i])}


def _pick_best_category_action(
    player: "YahtzeePlayer",
    *,
    calculate_score: Callable[[list[int], str], int],
    all_categories: list[str],
    upper_categories: list[str],
) -> str:
    """Choose the best category to score now."""
    open_categories = player.get_open_categories()
    scores = {cat: calculate_score(player.dice.values, cat) for cat in open_categories}

    # Yahtzee bonus: if dice are 5-of-a-kind and yahtzee already scored as 50,
    # we get +100 bonus no matter which category we pick.
    counts = _count_dice(player.dice.values)
    is_five_kind = any(c >= 5 for c in counts.values())
    yahtzee_bonus_active = is_five_kind and player.scores.get("yahtzee") == 50

    best_cat = None
    best_utility = -1.0
    upper_total_before = player.get_upper_total()

    for cat in open_categories:
        score = scores[cat]
        utility = float(score)

        if yahtzee_bonus_active:
            utility += 100.0

        if cat in upper_categories:
            before_gap = max(0, 63 - upper_total_before)
            after_gap = max(0, 63 - (upper_total_before + score))
            if before_gap > 0:
                utility += (before_gap - after_gap) * 0.2
            if before_gap > 0 and after_gap == 0:
                utility += 35.0

        if utility > best_utility:
            best_utility = utility
            best_cat = cat

    if best_cat is not None and scores[best_cat] > 0:
        return f"score_{best_cat}"

    # Forced to zero-out: waste the least valuable category.
    # Preserve upper categories if the 63-pt bonus is still reachable.
    upper_bonus_lost = not player.upper_bonus_awarded and upper_total_before < 63
    waste_order: list[str] = [
        "yahtzee",
        "large_straight",
        "small_straight",
        "full_house",
        "four_kind",
        "three_kind",
    ]
    if upper_bonus_lost:
        waste_order.extend(["ones", "twos", "threes", "chance", "fours", "fives", "sixes"])
    else:
        waste_order.extend(["chance", "ones", "twos", "threes", "fours", "fives", "sixes"])

    for cat in waste_order:
        if cat in open_categories:
            return f"score_{cat}"

    return f"score_{all_categories[0]}"


def _upper_target_value(category: str) -> int:
    return {
        "ones": 1,
        "twos": 2,
        "threes": 3,
        "fours": 4,
        "fives": 5,
        "sixes": 6,
    }[category]


def _longest_consecutive_run(values: list[int]) -> int:
    """Return longest consecutive run length in a sorted unique list."""
    if not values:
        return 0
    best = 1
    current = 1
    for i in range(1, len(values)):
        if values[i] == values[i - 1] + 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def _best_straight_run(unique_values: list[int]) -> set[int]:
    """Return the set of values forming the longest consecutive run."""
    if not unique_values:
        return set()
    best_start = unique_values[0]
    best_len = 1
    start = unique_values[0]
    length = 1
    for i in range(1, len(unique_values)):
        if unique_values[i] == unique_values[i - 1] + 1:
            length += 1
        else:
            if length > best_len:
                best_len = length
                best_start = start
            start = unique_values[i]
            length = 1
    if length > best_len:
        best_len = length
        best_start = start
    return set(range(best_start, best_start + best_len))
