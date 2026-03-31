"""Bot heuristics for Backgammon."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import BackgammonGame, BackgammonMove, BackgammonPlayer


def bot_think(game: "BackgammonGame", player: "BackgammonPlayer") -> str | None:
    """Choose a legal action for the current bot."""
    if game.current_player != player:
        return None

    if game.turn_phase == "pre_roll":
        if should_offer_double(game, player):
            return "offer_double"
        return "roll_dice"

    if game.turn_phase != "moving":
        return None

    if game.options.bot_strategy == "smart":
        best_move = _best_move_smart(game, player)
        if best_move is not None:
            return game.action_id_for_move(best_move)

    best_move = _best_move(game, player)
    if best_move is None:
        return None
    return game.action_id_for_move(best_move)


def bot_respond_to_double(game: "BackgammonGame", player: "BackgammonPlayer") -> str | None:
    """Decide whether a bot should accept or drop a double."""
    return "accept_double" if should_take_double(game, player) else "drop_double"


def should_offer_double(game: "BackgammonGame", player: "BackgammonPlayer") -> bool:
    """Simple cube heuristic based on score and pip advantage."""
    if not game._can_offer_double(player):
        return False

    my_pip = game._pip_count(player.color)
    opp_pip = game._pip_count(game._opponent_color(player.color))
    score_gap = game._score_for_color(player.color) - game._score_for_color(
        game._opponent_color(player.color)
    )
    if game.options.bot_strategy == "smart":
        return (opp_pip - my_pip) >= 18 or ((opp_pip - my_pip) >= 12 and score_gap <= 0)
    return (opp_pip - my_pip) >= 12 or ((opp_pip - my_pip) >= 8 and score_gap < 0)


def should_take_double(game: "BackgammonGame", player: "BackgammonPlayer") -> bool:
    """Simple take/drop heuristic based on pip deficit and match score."""
    my_pip = game._pip_count(player.color)
    opp_pip = game._pip_count(game._opponent_color(player.color))
    deficit = my_pip - opp_pip
    score_deficit = game._score_for_color(player.color) - game._score_for_color(
        game._opponent_color(player.color)
    )
    if game.options.bot_strategy == "smart":
        if deficit <= 14:
            return True
        if deficit <= 22 and score_deficit < 0:
            return True
        return False
    if deficit <= 10:
        return True
    if deficit <= 18 and score_deficit < 0:
        return True
    return False


def _best_move(game: "BackgammonGame", player: "BackgammonPlayer") -> "BackgammonMove | None":
    moves = game._get_legal_submoves(player.color)
    if not moves:
        return None

    best_move = None
    best_score = -10_000
    for move in moves:
        score = _score_move(game, player, move)
        if score > best_score:
            best_score = score
            best_move = move
    return best_move


def _best_move_smart(game: "BackgammonGame", player: "BackgammonPlayer") -> "BackgammonMove | None":
    sequences = game._generate_legal_sequences(player.color, list(game.remaining_dice))
    if not sequences:
        return None

    best_sequence = None
    best_score = -100_000
    for sequence in sequences:
        if not sequence:
            continue
        score = _score_sequence(game, player, sequence)
        if score > best_score:
            best_score = score
            best_sequence = sequence

    if not best_sequence:
        return None
    return best_sequence[0]


def _score_move(game: "BackgammonGame", player: "BackgammonPlayer", move: "BackgammonMove") -> int:
    score = 0
    sign = game._color_sign(player.color)

    if move.is_bear_off:
        score += 120

    if move.is_hit:
        score += 55
        if game._is_home_board_point(player.color, move.destination):
            score += 15

    if not move.is_bear_off:
        current_dest = game.board.points[move.destination]
        if current_dest * sign == 1:
            score += 35
            if game._is_home_board_point(player.color, move.destination):
                score += 15
        elif current_dest == 0:
            score -= 8

    if move.source >= 0:
        source_count = abs(game.board.points[move.source])
        if source_count == 2:
            score -= 18
            if game._is_opponent_home_board_point(player.color, move.source):
                score -= 10

        if game._is_opponent_home_board_point(player.color, move.source):
            score += 10

    if move.source == -1:
        score += 20

    score += move.die_value
    return score


def _score_sequence(
    game: "BackgammonGame", player: "BackgammonPlayer", sequence: list["BackgammonMove"]
) -> int:
    color = player.color
    applied: list[BackgammonMove] = []

    try:
        score = 0
        for move in sequence:
            score += _score_move(game, player, move)
            game._apply_move(move, color)
            applied.append(move)

        score += _board_position_score(game, color)
        score += len(sequence) * 40
        return score
    finally:
        for move in reversed(applied):
            game._undo_move(move, color)


def _board_position_score(game: "BackgammonGame", color: str) -> int:
    sign = game._color_sign(color)
    opponent = game._opponent_color(color)
    score = 0

    score += game._off_count(color) * 60
    score -= game._bar_count(color) * 45
    score += game._bar_count(opponent) * 30
    score += max(0, game._pip_count(opponent) - game._pip_count(color))

    for point_index, value in enumerate(game.board.points):
        if value * sign <= 0:
            continue
        count = abs(value)
        if count >= 2:
            score += 16
            if game._is_home_board_point(color, point_index):
                score += 8
        else:
            score -= 10
            if game._is_opponent_home_board_point(color, point_index):
                score -= 10

    return score
