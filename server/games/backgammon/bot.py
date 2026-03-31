"""Bot heuristics for Backgammon."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import (
        BackgammonBoard,
        BackgammonGame,
        BackgammonMove,
        BackgammonPlayer,
        BackgammonSmartSearchNode,
        BackgammonSmartSearchState,
    )


SMART_BOT_SEQUENCE_BUDGET = 6
SMART_BOT_NODE_BUDGET = 18


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
        return _continue_smart_search(game, player)

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


def _continue_smart_search(game: "BackgammonGame", player: "BackgammonPlayer") -> str | None:
    if not game._is_smart_bot_search_valid(player):
        game.smart_bot_search = game._new_smart_bot_search_state(player)

    search = game.smart_bot_search
    if search is None:
        return None

    nodes_processed = 0
    sequences_scored = 0

    while (
        search.stack
        and nodes_processed < SMART_BOT_NODE_BUDGET
        and sequences_scored < SMART_BOT_SEQUENCE_BUDGET
    ):
        node = search.stack.pop()
        board = _board_after_prefix(game, search.root_board, player.color, node.prefix)

        if not node.remaining_dice:
            if _consider_sequence(game, player, search, node.prefix):
                sequences_scored += 1
            nodes_processed += 1
            continue

        tried_values: set[int] = set()
        found_move = False
        child_nodes: list[BackgammonSmartSearchNode] = []

        for die_value in list(node.remaining_dice):
            if die_value in tried_values:
                continue
            tried_values.add(die_value)
            legal_moves = game._generate_moves_for_die(player.color, die_value, board)
            if not legal_moves:
                continue
            found_move = True
            remaining = list(node.remaining_dice)
            remaining.remove(die_value)
            for move in legal_moves:
                child_nodes.append(
                    type(node)(
                        prefix=[*node.prefix, move],
                        remaining_dice=list(remaining),
                    )
                )

        if found_move:
            for child in reversed(child_nodes):
                search.stack.append(child)
        else:
            if _consider_sequence(game, player, search, node.prefix):
                sequences_scored += 1

        nodes_processed += 1

    if search.stack:
        return None

    search.completed = True
    if not search.best_sequence:
        return None
    return game.action_id_for_move(search.best_sequence[0])


def _board_after_prefix(
    game: "BackgammonGame",
    root_board: "BackgammonBoard",
    color: str,
    prefix: list["BackgammonMove"],
) -> "BackgammonBoard":
    board = game._clone_board(root_board)
    for move in prefix:
        game._apply_move(move, color, board)
    return board


def _consider_sequence(
    game: "BackgammonGame",
    player: "BackgammonPlayer",
    search: "BackgammonSmartSearchState",
    sequence: list["BackgammonMove"],
) -> bool:
    if not sequence:
        return False

    if len(sequence) < search.best_length:
        return False

    if (
        len(search.root_dice) == 2
        and search.root_dice[0] != search.root_dice[1]
        and len(sequence) == 1
        and sequence[0].die_value != max(search.root_dice)
    ):
        return False

    score = _score_sequence(game, player, sequence, board=search.root_board)
    search.evaluated_sequences += 1
    if len(sequence) > search.best_length or score > search.best_score:
        search.best_length = len(sequence)
        search.best_score = score
        search.best_sequence = list(sequence)
    return True


def _score_move(
    game: "BackgammonGame",
    player: "BackgammonPlayer",
    move: "BackgammonMove",
    board: "BackgammonBoard | None" = None,
) -> int:
    score = 0
    sign = game._color_sign(player.color)
    active_board = board or game.board

    if move.is_bear_off:
        score += 120

    if move.is_hit:
        score += 55
        if game._is_home_board_point(player.color, move.destination):
            score += 15

    if not move.is_bear_off:
        current_dest = active_board.points[move.destination]
        if current_dest * sign == 1:
            score += 35
            if game._is_home_board_point(player.color, move.destination):
                score += 15
        elif current_dest == 0:
            score -= 8

    if move.source >= 0:
        source_count = abs(active_board.points[move.source])
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
    game: "BackgammonGame",
    player: "BackgammonPlayer",
    sequence: list["BackgammonMove"],
    board: "BackgammonBoard | None" = None,
) -> int:
    color = player.color
    working_board = game._clone_board(board)
    score = 0

    for move in sequence:
        score += _score_move(game, player, move, working_board)
        game._apply_move(move, color, working_board)

    score += _board_position_score(game, color, working_board)
    score += len(sequence) * 40
    return score


def _board_position_score(
    game: "BackgammonGame",
    color: str,
    board: "BackgammonBoard | None" = None,
) -> int:
    sign = game._color_sign(color)
    opponent = game._opponent_color(color)
    active_board = board or game.board
    score = 0

    score += game._off_count(color, active_board) * 60
    score -= game._bar_count(color, active_board) * 45
    score += game._bar_count(opponent, active_board) * 30
    score += max(0, game._pip_count(opponent, active_board) - game._pip_count(color, active_board))

    for point_index, value in enumerate(active_board.points):
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
