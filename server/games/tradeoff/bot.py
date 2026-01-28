"""
Bot AI logic for Tradeoff game.

Handles bot decision making for trading and taking phases.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import TradeoffGame, TradeoffPlayer


def bot_think_trading(game: "TradeoffGame", player: "TradeoffPlayer") -> str | None:
    """
    Bot AI for trading phase.

    Strategy: Keep dice that contribute to sets, trade the rest.
    Simple heuristic: keep duplicates, trade unique values.

    Note: All dice start marked for trading by default, so bot must
    toggle OFF the ones it wants to keep.
    """
    if player.trades_confirmed:
        return None

    counts: dict[int, int] = {}
    for d in player.rolled_dice:
        counts[d] = counts.get(d, 0) + 1

    # Also consider what's already in hand
    for d in player.hand:
        counts[d] = counts.get(d, 0) + 1

    # Decide which to KEEP (not trade)
    # Keep dice that appear more than once (useful for sets)
    desired_keeps: list[int] = []
    for i, d in enumerate(player.rolled_dice):
        total_count = counts.get(d, 0)
        if total_count > 1:
            desired_keeps.append(i)

    # Keep at least 2 dice (don't trade everything)
    if len(desired_keeps) < 2:
        # Keep the most common values
        sorted_dice = sorted(
            enumerate(player.rolled_dice),
            key=lambda x: counts.get(x[1], 0),
            reverse=True
        )
        for i, _ in sorted_dice:
            if i not in desired_keeps:
                desired_keeps.append(i)
                if len(desired_keeps) >= 2:
                    break

    # Toggle OFF any dice we want to keep (remove from trading)
    for i in desired_keeps:
        if i in player.trading_indices:
            return f"toggle_trade_{i}"

    # Confirm trades
    return "confirm_trades"


def bot_think_taking(game: "TradeoffGame", player: "TradeoffPlayer") -> str | None:
    """
    Bot AI for taking phase.

    Strategy: Take dice that match what we already have.
    """
    if game.taking_index >= len(game.taking_order):
        return None
    if game.taking_order[game.taking_index] != player.id:
        return None
    if player.dice_taken_count >= player.dice_traded_count:
        return None

    # Count what we already have in hand
    counts: dict[int, int] = {}
    for d in player.hand:
        counts[d] = counts.get(d, 0) + 1

    # Count what's in the pool
    pool_counts: dict[int, int] = {}
    for d in game.pool:
        pool_counts[d] = pool_counts.get(d, 0) + 1

    # Find best die to take from pool
    best_value = None
    best_score = -1

    for v, c in pool_counts.items():
        if c > 0:
            # Score based on how many we already have
            existing = counts.get(v, 0)
            score = existing  # Prefer values we already have
            if score > best_score:
                best_score = score
                best_value = v

    if best_value is not None:
        return f"take_{best_value}"

    return None
