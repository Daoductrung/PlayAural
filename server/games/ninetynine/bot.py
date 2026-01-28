"""
Bot AI for Ninety Nine game.

Handles bot decision making for card play and choices.
"""

from typing import TYPE_CHECKING

from ...game_utils.cards import (
    Card,
    SUIT_NONE,
    RS_RANK_PASS,
    RS_RANK_MINUS_10,
    RS_RANK_REVERSE,
    RS_RANK_SKIP,
    RS_RANK_NINETY_NINE,
)

if TYPE_CHECKING:
    from .game import NinetyNineGame, NinetyNinePlayer

# Bot scoring constants
BOT_SCORE_BUST = -99999
BOT_SCORE_MILESTONE_HIT = 10000
BOT_SCORE_PERFECT_TRAP = 7000
BOT_SCORE_WEAK_TRAP = 3000
BOT_SCORE_SETUP_ZONE = 5000
BOT_SCORE_SKIP_TRAP = -5000
BOT_SCORE_BAD_SETUP = -3000

# Bot hoarding penalties (when not in danger)
BOT_HOARD_ACE = 350
BOT_HOARD_NINE = 300
BOT_HOARD_TEN = 200
BOT_HOARD_TWO = 150
BOT_HOARD_RS_PASS = 400
BOT_HOARD_RS_SKIP = 400
BOT_HOARD_RS_MINUS_10 = 300
BOT_HOARD_RS_REVERSE = 200
BOT_HOARD_RS_99 = 250

# Game constants needed for bot logic
MAX_COUNT = 99
MILESTONE_33 = 33
MILESTONE_66 = 66
TEN_AUTO_THRESHOLD = 90
TWO_DIVIDE_THRESHOLD = 49


def bot_think(game: "NinetyNineGame", player: "NinetyNinePlayer") -> str | None:
    """
    Bot AI decision making.

    Args:
        game: The Ninety Nine game instance.
        player: The bot player making a decision.

    Returns:
        Action ID to execute, or None if no action available.
    """
    if game.current_player != player:
        return None

    if game.pending_choice is not None:
        return _make_choice(game, player)

    return _choose_card(game, player)


def _make_choice(game: "NinetyNineGame", player: "NinetyNinePlayer") -> str | None:
    """Bot makes a choice for Ace or Ten."""
    if game.pending_choice == "ace":
        score_11 = _evaluate_count(game, game.count + 11, 1)
        score_1 = _evaluate_count(game, game.count + 1, 1)
        return "choice_1" if score_11 > score_1 else "choice_2"

    elif game.pending_choice == "ten":
        score_plus = _evaluate_count(game, game.count + 10, 10)
        score_minus = _evaluate_count(game, game.count - 10, 10)
        return "choice_1" if score_plus > score_minus else "choice_2"

    return None


def _choose_card(game: "NinetyNineGame", player: "NinetyNinePlayer") -> str | None:
    """Bot chooses which card to play."""
    if not player.hand:
        return None

    best_slot = 0
    best_score = -10000

    for i, card in enumerate(player.hand):
        score = _score_card(game, player, card)
        if score > best_score:
            best_score = score
            best_slot = i

    return f"card_slot_{best_slot + 1}"


def _evaluate_count(game: "NinetyNineGame", new_count: int, card_rank: int) -> int:
    """Evaluate how good a resulting count is for the bot."""
    if new_count > MAX_COUNT:
        return BOT_SCORE_BUST

    alive_count = len([p for p in game.players if p.tokens > 0])
    is_two_player = alive_count == 2

    # Check if this is a Skip card
    is_skip = (card_rank == 11 and game.is_quentin_c) or (
        card_rank == RS_RANK_SKIP and not game.is_quentin_c
    )

    if game.is_quentin_c:
        return _evaluate_quentin_c(game, new_count, is_two_player, is_skip)
    else:
        return _evaluate_rs_games(new_count, is_two_player, is_skip)


def _evaluate_quentin_c(
    game: "NinetyNineGame", new_count: int, is_two_player: bool, is_skip: bool
) -> int:
    """Evaluate count for Quentin C variant."""
    score = 0
    current_count = game.count

    # Hit milestones (highest priority when adding to count)
    if new_count in (MILESTONE_33, MILESTONE_66, MAX_COUNT) and new_count > current_count:
        return BOT_SCORE_MILESTONE_HIT

    # Skip self-trap in 2-player
    if is_two_player and is_skip:
        is_danger = (
            (28 <= new_count <= 32)
            or (61 <= new_count <= 65)
            or (88 <= new_count <= 98)
            or new_count in (23, 56, 89)
        )
        if is_danger:
            return BOT_SCORE_SKIP_TRAP

    # Perfect traps in 2-player
    if is_two_player and new_count in (31, 97):
        return BOT_SCORE_PERFECT_TRAP

    # 64 is weaker (opponent can divide)
    if is_two_player and new_count == 64:
        return BOT_SCORE_WEAK_TRAP

    # Setup zones
    if (29 <= new_count <= 32) or (62 <= new_count <= 65) or (95 <= new_count <= 98):
        return BOT_SCORE_SETUP_ZONE

    # Avoid bad setups when holding +10 cards
    if new_count in (23, 56, 89):
        return BOT_SCORE_BAD_SETUP

    # Penalize high counts
    if 70 <= new_count <= 94:
        score -= (new_count - 70) * 5

    # Pressure zone: make it harder for the next player
    if 88 <= new_count <= 97:
        score += 400 if is_two_player else 250

    # Avoid giving the table a very low count
    if new_count <= 15:
        score -= 50

    # Bonus for safe middle range
    if 40 <= new_count <= 60:
        score += 100

    return score


def _evaluate_rs_games(new_count: int, is_two_player: bool, is_skip: bool) -> int:
    """Evaluate count for RS Games variant."""
    score = 0

    if is_two_player and is_skip:
        if 88 <= new_count <= 98:
            return BOT_SCORE_SKIP_TRAP

    if is_two_player and new_count == 97:
        return BOT_SCORE_PERFECT_TRAP

    if 70 <= new_count <= 96:
        score -= (new_count - 70) * 8

    # Pressure zone: make it harder for the next player
    if 88 <= new_count <= 97:
        score += 350 if is_two_player else 200

    # Avoid giving the table a very low count
    if new_count <= 15:
        score -= 50

    if 20 <= new_count <= 60:
        score += 150
    if 0 <= new_count <= 30:
        score += 50

    return score


def _score_card(
    game: "NinetyNineGame", player: "NinetyNinePlayer", card: Card
) -> int:
    """Score a card for bot decision making."""
    rank = card.rank
    count = game.count

    # Calculate base score from evaluating the resulting count
    if game.is_quentin_c:
        base_score = _score_quentin_c_card(game, rank, count)
    else:
        base_score = _score_rs_games_card(game, rank, count)

    # Apply hoarding logic
    base_score += _hoarding_modifier(game, rank)

    # Apply situational bonuses for skip/reverse/pass
    base_score += _special_card_modifier(game, rank)

    return base_score


def _score_quentin_c_card(game: "NinetyNineGame", rank: int, count: int) -> int:
    """Score a card for Quentin C variant."""
    if rank == 1:  # Ace
        score_11 = _evaluate_count(game, count + 11, rank)
        score_1 = _evaluate_count(game, count + 1, rank)
        return max(score_11, score_1)
    elif rank == 10 and count < TEN_AUTO_THRESHOLD:
        score_plus = _evaluate_count(game, count + 10, rank)
        score_minus = _evaluate_count(game, count - 10, rank)
        return max(score_plus, score_minus)
    elif rank == 2:
        new_count = _calculate_two_effect(count)
        score = _evaluate_count(game, new_count, rank)
        # Treat doubling (non-divide use of 2) as a last resort.
        if new_count > count:
            score -= 8000
        if new_count < count and count >= 80:
            score += 200
        return score
    elif rank == 9:
        return _evaluate_count(game, count, rank)
    else:
        value = _get_card_value(rank, count)
        return _evaluate_count(game, count + (value or 0), rank)


def _score_rs_games_card(game: "NinetyNineGame", rank: int, count: int) -> int:
    """Score a card for RS Games variant."""
    if rank == RS_RANK_NINETY_NINE:
        return _evaluate_count(game, MAX_COUNT, rank)
    else:
        value = _get_rs_card_value(rank)
        return _evaluate_count(game, count + (value or 0), rank)


def _hoarding_modifier(game: "NinetyNineGame", rank: int) -> int:
    """Calculate hoarding modifier for a card."""
    count = game.count

    if game.is_quentin_c:
        in_danger = (28 <= count <= 32) or (61 <= count <= 65) or count >= 88

        if not in_danger:
            if rank == 1:
                return -BOT_HOARD_ACE
            elif rank == 9:
                return -BOT_HOARD_NINE
            elif rank == 10:
                return -BOT_HOARD_TEN
            elif rank == 2:
                return -BOT_HOARD_TWO
        else:
            if rank == 1:
                return 100
            elif rank == 9:
                return 50
    else:
        in_danger = count >= 85

        if not in_danger:
            if rank == RS_RANK_PASS:
                return -BOT_HOARD_RS_PASS
            elif rank == RS_RANK_SKIP:
                return -BOT_HOARD_RS_SKIP
            elif rank == RS_RANK_MINUS_10:
                return -BOT_HOARD_RS_MINUS_10
            elif rank == RS_RANK_REVERSE:
                return -BOT_HOARD_RS_REVERSE
            elif rank == RS_RANK_NINETY_NINE:
                return -BOT_HOARD_RS_99
        else:
            if rank in (RS_RANK_PASS, RS_RANK_SKIP):
                return 150
            elif rank == RS_RANK_MINUS_10:
                return 200

    return 0


def _special_card_modifier(game: "NinetyNineGame", rank: int) -> int:
    """Small situational bonus for control cards (skip/reverse/pass)."""
    next_player = _next_alive_player(game)
    if not next_player:
        return 0

    alive_count = len([p for p in game.players if p.tokens > 0])
    low_tokens = next_player.tokens <= 1

    if game.is_quentin_c:
        if rank == 11:  # Jack skips
            return 300 if low_tokens else 150
        if rank == 4 and alive_count > 2:
            return 150 if low_tokens else 50
    else:
        if rank == RS_RANK_SKIP:
            return 300 if low_tokens else 150
        if rank == RS_RANK_REVERSE and alive_count > 2:
            return 150 if low_tokens else 50
        if rank == RS_RANK_PASS:
            return 200 if low_tokens else 75

    return 0


def _next_alive_player(game: "NinetyNineGame") -> "NinetyNinePlayer | None":
    """Find the next alive player in turn order."""
    if not game.turn_player_ids:
        return None

    step = game.turn_direction
    idx = game.turn_index
    for _ in range(len(game.turn_player_ids)):
        idx = (idx + step) % len(game.turn_player_ids)
        player = game.get_player_by_id(game.turn_player_ids[idx])
        if player and player.tokens > 0:
            return player

    return None


def _calculate_two_effect(current_count: int) -> int:
    """Calculate the new count after playing a 2 (Quentin C)."""
    if current_count % 2 == 0 and current_count > TWO_DIVIDE_THRESHOLD:
        return current_count // 2
    else:
        return current_count * 2


def _get_card_value(rank: int, current_count: int) -> int:
    """Get simple card value for Quentin C (used by bot scoring)."""
    if 3 <= rank <= 8:
        return rank
    elif rank == 9:
        return 0
    elif rank in (11, 12, 13):
        return 10
    return 0


def _get_rs_card_value(rank: int) -> int:
    """Get simple card value for RS Games (used by bot scoring)."""
    from ...game_utils.cards import RS_RANK_PLUS_10

    if 1 <= rank <= 9:
        return rank
    elif rank == RS_RANK_PLUS_10:
        return 10
    elif rank == RS_RANK_MINUS_10:
        return -10
    elif rank in (RS_RANK_PASS, RS_RANK_REVERSE, RS_RANK_SKIP):
        return 0
    return 0
