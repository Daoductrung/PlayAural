"""
Bot AI for Ninety Nine game.

Handles bot decision making for card play and choices.
"""

from typing import TYPE_CHECKING

from ...game_utils.cards import (
    Card,
    N99_RANK_PLUS_10,
    N99_RANK_MINUS_10,
    N99_RANK_PASS,
    N99_RANK_REVERSE,
    N99_RANK_SKIP,
    N99_RANK_NINETY_NINE,
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
BOT_SCORE_OPPONENT_NO_SAFE = 9000
BOT_SCORE_OPPONENT_KILL = 12000

# Bot hoarding penalties (when not in danger)
BOT_HOARD_ACE = 350
BOT_HOARD_NINE = 300
BOT_HOARD_TEN = 200
BOT_HOARD_TWO = 150
BOT_HOARD_ACTION_PASS = 400
BOT_HOARD_ACTION_SKIP = 400
BOT_HOARD_ACTION_MINUS_10 = 300
BOT_HOARD_ACTION_REVERSE = 200
BOT_HOARD_ACTION_99 = 250

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
    """Route legacy saved pending choices through the shared resolve action."""
    slot = game.pending_card_index
    if slot < 0 or slot >= len(player.hand):
        return None
    return "resolve_choice"


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
    return _evaluate_count_from_current(game, game.count, new_count, card_rank)


def _evaluate_count_from_current(
    game: "NinetyNineGame", current_count: int, new_count: int, card_rank: int
) -> int:
    """Evaluate a resulting count from an arbitrary starting count."""
    if new_count > MAX_COUNT:
        return BOT_SCORE_BUST

    alive_count = len([p for p in game.players if p.tokens > 0 and not p.is_spectator])
    is_two_player = alive_count == 2

    # Check if this is a Skip card
    is_skip = (card_rank == 11 and game.is_standard_rules) or (
        card_rank == N99_RANK_SKIP and not game.is_standard_rules
    )

    if game.is_standard_rules:
        return _evaluate_standard(current_count, new_count, is_two_player, is_skip)
    else:
        return _evaluate_action_cards(new_count, is_two_player, is_skip)


def _evaluate_standard(
    current_count: int, new_count: int, is_two_player: bool, is_skip: bool
) -> int:
    """Evaluate count for standard variant."""
    score = 0

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


def _evaluate_action_cards(new_count: int, is_two_player: bool, is_skip: bool) -> int:
    """Evaluate count for action cards variant."""
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
    outcome_scores = [
        _score_outcome(game, player, rank, new_count)
        for new_count in _enumerate_card_outcomes(game, card, game.count)
    ]
    base_score = max(outcome_scores, default=BOT_SCORE_BUST)
    base_score += _hoarding_modifier(game, rank)
    base_score += _special_card_modifier(game, rank)
    return base_score


def _score_outcome(
    game: "NinetyNineGame",
    player: "NinetyNinePlayer",
    card_rank: int,
    new_count: int,
) -> int:
    """Score a fully specified play outcome."""
    score = _evaluate_count(game, new_count, card_rank)
    score += _pressure_modifier(game, player, card_rank, new_count)

    if player.tokens <= 1:
        if new_count >= 95:
            score -= 1200
        elif new_count >= 90:
            score -= 600

    return score


def _hoarding_modifier(game: "NinetyNineGame", rank: int) -> int:
    """Calculate hoarding modifier for a card."""
    count = game.count

    if game.is_standard_rules:
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
            if rank == N99_RANK_PASS:
                return -BOT_HOARD_ACTION_PASS
            elif rank == N99_RANK_SKIP:
                return -BOT_HOARD_ACTION_SKIP
            elif rank == N99_RANK_MINUS_10:
                return -BOT_HOARD_ACTION_MINUS_10
            elif rank == N99_RANK_REVERSE:
                return -BOT_HOARD_ACTION_REVERSE
            elif rank == N99_RANK_NINETY_NINE:
                return -BOT_HOARD_ACTION_99
        else:
            if rank in (N99_RANK_PASS, N99_RANK_SKIP):
                return 150
            elif rank == N99_RANK_MINUS_10:
                return 200

    return 0


def _special_card_modifier(game: "NinetyNineGame", rank: int) -> int:
    """Small situational bonus for control cards (skip/reverse/pass)."""
    next_player = _next_alive_player_after_play(game, game.current_player, rank)
    if not next_player:
        return 0

    alive_count = len([p for p in game.players if p.tokens > 0 and not p.is_spectator])
    low_tokens = next_player.tokens <= 1

    if game.is_standard_rules:
        if rank == 11:  # Jack skips
            return 300 if low_tokens else 150
        if rank == 4 and alive_count > 2:
            return 150 if low_tokens else 50
    else:
        if rank == N99_RANK_SKIP:
            return 300 if low_tokens else 150
        if rank == N99_RANK_REVERSE and alive_count > 2:
            return 150 if low_tokens else 50
        if rank == N99_RANK_PASS:
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


def _next_alive_player_after_play(
    game: "NinetyNineGame",
    player: "NinetyNinePlayer | None",
    rank: int,
) -> "NinetyNinePlayer | None":
    """Find who would act next after applying this card's control effect."""
    if not player or player.id not in game.turn_player_ids:
        return _next_alive_player(game)

    direction = game.turn_direction
    alive_count = len([p for p in game.players if p.tokens > 0 and not p.is_spectator])

    reverse_applies = (
        game.is_standard_rules and rank == 4 and alive_count > 2
    ) or (
        not game.is_standard_rules and rank == N99_RANK_REVERSE and alive_count > 2
    )
    if reverse_applies:
        direction *= -1

    skips_remaining = 1 if (
        (game.is_standard_rules and rank == 11)
        or (not game.is_standard_rules and rank == N99_RANK_SKIP)
    ) else 0

    idx = game.turn_player_ids.index(player.id)
    for _ in range(len(game.turn_player_ids) * 2):
        idx = (idx + direction) % len(game.turn_player_ids)
        candidate = game.get_player_by_id(game.turn_player_ids[idx])
        if not candidate or candidate.tokens <= 0 or candidate.is_spectator:
            continue
        if skips_remaining > 0:
            skips_remaining -= 1
            continue
        return candidate

    return None


def _pressure_modifier(
    game: "NinetyNineGame",
    player: "NinetyNinePlayer",
    card_rank: int,
    new_count: int,
) -> int:
    """Estimate how hard the move makes the next player's turn."""
    next_player = _next_alive_player_after_play(game, player, card_rank)
    if not next_player:
        return 0

    safe_responses = _enumerate_safe_responses(game, next_player, new_count)
    if not safe_responses:
        bonus = BOT_SCORE_OPPONENT_KILL if next_player.tokens <= 1 else BOT_SCORE_OPPONENT_NO_SAFE
        return bonus

    best_response = max(
        _evaluate_count_from_current(game, new_count, response_count, response_rank)
        for response_rank, response_count in safe_responses
    )
    min_response_count = min(response_count for _, response_count in safe_responses)

    modifier = -(best_response // 4)
    if min_response_count >= 90:
        modifier += 500
    if next_player.tokens <= 1:
        modifier += 350
    return modifier


def _enumerate_safe_responses(
    game: "NinetyNineGame",
    player: "NinetyNinePlayer",
    current_count: int,
) -> list[tuple[int, int]]:
    """Enumerate the next player's safe card outcomes."""
    safe: list[tuple[int, int]] = []
    for card in player.hand:
        for new_count in _enumerate_card_outcomes(game, card, current_count):
            if new_count <= MAX_COUNT:
                safe.append((card.rank, new_count))
    return safe


def _enumerate_card_outcomes(
    game: "NinetyNineGame", card: Card, current_count: int
) -> list[int]:
    """Enumerate all legal count outcomes for a single card."""
    rank = card.rank

    if game.is_standard_rules:
        if rank == 1:
            return [current_count + 1] if current_count > 88 else [current_count + 11, current_count + 1]
        if rank == 2:
            return [_calculate_two_effect(current_count)]
        if rank == 9:
            return [current_count]
        if rank == 10:
            return [current_count - 10] if current_count >= TEN_AUTO_THRESHOLD else [current_count + 10, current_count - 10]
        if rank in (11, 12, 13):
            return [current_count + 10]
        return [current_count + _get_card_value(rank)]

    if rank == N99_RANK_NINETY_NINE:
        return [MAX_COUNT]
    return [current_count + _get_action_card_value(rank)]


def _calculate_two_effect(current_count: int) -> int:
    """Calculate the new count after playing a 2 (standard rules)."""
    if current_count % 2 == 0 and current_count > TWO_DIVIDE_THRESHOLD:
        return current_count // 2
    else:
        return current_count * 2


def _get_card_value(rank: int) -> int:
    """Get simple card value for standard rules (used by bot scoring)."""
    if 3 <= rank <= 8:
        return rank
    elif rank == 9:
        return 0
    elif rank in (11, 12, 13):
        return 10
    return 0


def _get_action_card_value(rank: int) -> int:
    """Get simple card value for action cards (used by bot scoring)."""
    if 1 <= rank <= 9:
        return rank
    elif rank == N99_RANK_PLUS_10:
        return 10
    elif rank == N99_RANK_MINUS_10:
        return -10
    elif rank in (N99_RANK_PASS, N99_RANK_REVERSE, N99_RANK_SKIP):
        return 0
    return 0
