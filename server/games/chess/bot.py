"""Server-safe Chess bot.

The bot searches on a cloned game object in a bounded worker pool.  This keeps
the gameplay event loop responsive even when several chess tables have bots
thinking at the same time.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
import os
import random
from threading import Event
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import ChessGame, ChessPiece, ChessPlayer


PIECE_VALUES = {
    "pawn": 100,
    "knight": 320,
    "bishop": 330,
    "rook": 500,
    "queen": 900,
    "king": 20000,
}

PAWN_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0,
]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

ROOK_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0,
]

QUEEN_TABLE = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20,
]

KING_MIDDLEGAME_TABLE = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20,
]

KING_ENDGAME_TABLE = [
    -50, -30, -30, -30, -30, -30, -30, -50,
    -30, -10, 0, 0, 0, 0, -10, -30,
    -30, 0, 20, 30, 30, 20, 0, -30,
    -30, 0, 30, 40, 40, 30, 0, -30,
    -30, 0, 30, 40, 40, 30, 0, -30,
    -30, 0, 20, 30, 30, 20, 0, -30,
    -30, -10, 0, 0, 0, 0, -10, -30,
    -50, -30, -30, -30, -30, -30, -30, -50,
]

PIECE_SQUARE_TABLES = {
    "pawn": PAWN_TABLE,
    "knight": KNIGHT_TABLE,
    "bishop": BISHOP_TABLE,
    "rook": ROOK_TABLE,
    "queen": QUEEN_TABLE,
    "king": KING_MIDDLEGAME_TABLE,
}

MATE_SCORE = 1_000_000
INF = 10_000_000


def _env_int(name: str, default: int, minimum: int = 1, maximum: int | None = None) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def _env_float(name: str, default: float, minimum: float = 0.05, maximum: float | None = None) -> float:
    try:
        value = float(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


MAX_WORKERS = _env_int("PLAYAURAL_CHESS_BOT_WORKERS", 1, minimum=1, maximum=4)
DEFAULT_TIME_LIMIT = _env_float("PLAYAURAL_CHESS_BOT_TIME_LIMIT", 2.5, minimum=0.05, maximum=30.0)
DEFAULT_NODE_LIMIT = _env_int("PLAYAURAL_CHESS_BOT_NODE_LIMIT", 250_000, minimum=1_000)
DEFAULT_DEPTH = _env_int("PLAYAURAL_CHESS_BOT_DEPTH", 4, minimum=1, maximum=6)

_EXECUTOR = ThreadPoolExecutor(
    max_workers=MAX_WORKERS,
    thread_name_prefix="playaural-chess-bot",
)


class SearchTimeout(Exception):
    """Raised internally when the bounded search exhausts its budget."""


class SearchCancelled(Exception):
    """Raised internally when the owning game retires a search."""


@dataclass
class SearchContext:
    root_color: str
    deadline: float
    node_limit: int
    cancel_event: Event | None = None
    nodes: int = 0
    transpositions: dict[tuple[str, str, int], int] = field(default_factory=dict)

    def check_budget(self) -> None:
        if self.cancel_event is not None and self.cancel_event.is_set():
            raise SearchCancelled
        self.nodes += 1
        if self.nodes > self.node_limit or time.perf_counter() >= self.deadline:
            raise SearchTimeout


@dataclass
class BotSearchJob:
    signature: str
    future: Future
    cancel_event: Event

    def cancel(self) -> None:
        """Request cooperative termination and cancel work not yet started."""
        self.cancel_event.set()
        self.future.cancel()


def _opponent(color: str) -> str:
    return "black" if color == "white" else "white"


def _pst_index(square: int, color: str) -> int:
    rank = square // 8
    file_index = square % 8
    if color == "white":
        return (7 - rank) * 8 + file_index
    return rank * 8 + file_index


def _piece_value(piece: "ChessPiece | None") -> int:
    if piece is None:
        return 0
    return PIECE_VALUES.get(piece.kind, 0)


def _clone_game_for_search(game: "ChessGame") -> "ChessGame":
    clone = type(game)(options=type(game.options)(**game.options.to_dict()))
    clone.board = [game._clone_piece(piece) for piece in game.board]
    clone.current_color = game.current_color
    clone.halfmove_clock = game.halfmove_clock
    clone.en_passant_target = game.en_passant_target
    clone.castle_white_kingside = game.castle_white_kingside
    clone.castle_white_queenside = game.castle_white_queenside
    clone.castle_black_kingside = game.castle_black_kingside
    clone.castle_black_queenside = game.castle_black_queenside
    clone.position_history = list(game.position_history)
    clone.move_history = []
    return clone


def _bot_jobs(game: "ChessGame") -> dict[str, BotSearchJob]:
    return game._chess_bot_jobs


def _search_signature(game: "ChessGame", player: "ChessPlayer") -> str:
    return f"{player.id}|{player.color}|{len(game.move_history)}|{game._get_position_hash()}"


def _material_phase(game: "ChessGame") -> int:
    total = 0
    for piece in game.board:
        if piece and piece.kind not in {"king", "pawn"}:
            total += PIECE_VALUES.get(piece.kind, 0)
    return total


def _evaluate(game: "ChessGame", root_color: str) -> int:
    score = 0
    phase = _material_phase(game)
    endgame = phase <= 2600
    bishops: dict[str, int] = {"white": 0, "black": 0}

    for square, piece in enumerate(game.board):
        if piece is None:
            continue
        sign = 1 if piece.color == root_color else -1
        value = PIECE_VALUES.get(piece.kind, 0)
        pst = KING_ENDGAME_TABLE if piece.kind == "king" and endgame else PIECE_SQUARE_TABLES.get(piece.kind)
        positional = pst[_pst_index(square, piece.color)] if pst is not None else 0
        score += sign * (value + positional)
        if piece.kind == "bishop":
            bishops[piece.color] += 1

    if bishops[root_color] >= 2:
        score += 35
    if bishops[_opponent(root_color)] >= 2:
        score -= 35

    root_moves = len(game.get_legal_moves(root_color))
    opponent_moves = len(game.get_legal_moves(_opponent(root_color)))
    score += (root_moves - opponent_moves) * 3

    if game.is_in_check(root_color):
        score -= 45
    if game.is_in_check(_opponent(root_color)):
        score += 45
    return score


def _is_capture(game: "ChessGame", move: tuple[int, int]) -> bool:
    from_sq, to_sq = move
    piece = game.board[from_sq]
    target = game.board[to_sq]
    if target is not None:
        return True
    return bool(
        piece
        and piece.kind == "pawn"
        and to_sq == game.en_passant_target
        and (from_sq % 8) != (to_sq % 8)
    )


def _move_order_score(game: "ChessGame", move: tuple[int, int], color: str) -> int:
    from_sq, to_sq = move
    piece = game.board[from_sq]
    target = game.board[to_sq]
    if piece is None:
        return -INF

    score = 0
    if target is not None:
        score += 10_000 + _piece_value(target) * 10 - _piece_value(piece)
    elif piece.kind == "pawn" and to_sq == game.en_passant_target and (from_sq % 8) != (to_sq % 8):
        score += 10_000 + PIECE_VALUES["pawn"] * 10

    if piece.kind == "pawn" and to_sq // 8 in {0, 7}:
        score += 8_000

    is_castle, _ = game._is_castling_move(from_sq, to_sq, piece)
    if is_castle:
        score += 600

    saved = game.save_position()
    try:
        game._apply_move_core(from_sq, to_sq, promotion="queen", auto_promote_to_queen=True)
        if game.is_in_check(_opponent(color)):
            score += 700
    finally:
        game.restore_position(saved)

    file_index = to_sq % 8
    rank_index = to_sq // 8
    score += 20 - (abs(file_index - 3.5) + abs(rank_index - 3.5)) * 4
    return int(score)


def _ordered_moves(game: "ChessGame", color: str, preferred: tuple[int, int] | None = None) -> list[tuple[int, int]]:
    moves = game.get_legal_moves(color)
    if preferred in moves:
        moves.remove(preferred)
        return [preferred] + sorted(
            moves,
            key=lambda move: _move_order_score(game, move, color),
            reverse=True,
        )
    return sorted(moves, key=lambda move: _move_order_score(game, move, color), reverse=True)


def _position_key(game: "ChessGame", color: str, depth: int) -> tuple[str, str, int]:
    return (game._get_position_hash(), color, depth)


def _quiescence(
    game: "ChessGame",
    color: str,
    alpha: int,
    beta: int,
    ctx: SearchContext,
    ply: int,
) -> int:
    ctx.check_budget()
    stand_pat = _evaluate(game, ctx.root_color)
    maximizing = color == ctx.root_color
    if maximizing:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    noisy_moves = [
        move
        for move in _ordered_moves(game, color)
        if _is_capture(game, move) or (game.board[move[0]] and game.board[move[0]].kind == "pawn" and move[1] // 8 in {0, 7})
    ][:12]
    for move in noisy_moves:
        saved = game.save_position()
        try:
            game._apply_move_core(move[0], move[1], promotion="queen", auto_promote_to_queen=True)
            game.current_color = _opponent(color)
            score = _quiescence(game, _opponent(color), alpha, beta, ctx, ply + 1)
        finally:
            game.restore_position(saved)

        if maximizing:
            if score > alpha:
                alpha = score
            if alpha >= beta:
                return beta
        else:
            if score < beta:
                beta = score
            if beta <= alpha:
                return alpha
    return alpha if maximizing else beta


def _search(
    game: "ChessGame",
    color: str,
    depth: int,
    alpha: int,
    beta: int,
    ctx: SearchContext,
    ply: int = 0,
) -> int:
    ctx.check_budget()
    key = _position_key(game, color, depth)
    cached = ctx.transpositions.get(key)
    if cached is not None:
        return cached

    legal_moves = _ordered_moves(game, color)
    if not legal_moves:
        if game.is_in_check(color):
            score = -MATE_SCORE + ply if color == ctx.root_color else MATE_SCORE - ply
        else:
            score = 0
        ctx.transpositions[key] = score
        return score

    if depth <= 0:
        return _quiescence(game, color, alpha, beta, ctx, ply)

    maximizing = color == ctx.root_color
    best_score = -INF if maximizing else INF
    next_color = _opponent(color)

    for move in legal_moves:
        saved = game.save_position()
        try:
            game._apply_move_core(move[0], move[1], promotion="queen", auto_promote_to_queen=True)
            game.current_color = next_color
            score = _search(game, next_color, depth - 1, alpha, beta, ctx, ply + 1)
        finally:
            game.restore_position(saved)

        if maximizing:
            if score > best_score:
                best_score = score
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        else:
            if score < best_score:
                best_score = score
            beta = min(beta, best_score)
            if beta <= alpha:
                break

    ctx.transpositions[key] = best_score
    return best_score


def _root_search(
    game: "ChessGame",
    color: str,
    *,
    max_depth: int,
    time_limit: float,
    node_limit: int,
    cancel_event: Event | None = None,
) -> tuple[int, int] | None:
    if cancel_event is not None and cancel_event.is_set():
        return None
    moves = _ordered_moves(game, color)
    if not moves:
        return None

    deadline = time.perf_counter() + time_limit
    ctx = SearchContext(
        root_color=color,
        deadline=deadline,
        node_limit=node_limit,
        cancel_event=cancel_event,
    )
    best_move = moves[0]
    best_score = -INF
    preferred: tuple[int, int] | None = None

    for depth in range(1, max_depth + 1):
        depth_best = best_move
        depth_score = -INF
        alpha = -INF
        beta = INF
        try:
            for move in _ordered_moves(game, color, preferred):
                saved = game.save_position()
                try:
                    game._apply_move_core(move[0], move[1], promotion="queen", auto_promote_to_queen=True)
                    game.current_color = _opponent(color)
                    score = _search(game, _opponent(color), depth - 1, alpha, beta, ctx, 1)
                finally:
                    game.restore_position(saved)
                if score > depth_score:
                    depth_score = score
                    depth_best = move
                alpha = max(alpha, depth_score)
        except SearchCancelled:
            return None
        except SearchTimeout:
            break
        best_move = depth_best
        best_score = depth_score
        preferred = best_move
        if best_score >= MATE_SCORE - 100:
            break

    # Keep a little variety only when moves are practically equivalent.
    if cancel_event is not None and cancel_event.is_set():
        return None
    if best_score < MATE_SCORE - 100:
        contenders: list[tuple[int, int]] = []
        for move in moves[:6]:
            if cancel_event is not None and cancel_event.is_set():
                return None
            saved = game.save_position()
            try:
                game._apply_move_core(move[0], move[1], promotion="queen", auto_promote_to_queen=True)
                score = _evaluate(game, color)
            finally:
                game.restore_position(saved)
            if move == best_move or score >= best_score - 20:
                contenders.append(move)
        if len(contenders) > 1 and random.random() < 0.15:  # nosec B311
            return random.choice(contenders)  # nosec B311
    return best_move


def find_best_move(
    game: "ChessGame",
    player: "ChessPlayer",
    *,
    time_limit: float | None = None,
    node_limit: int | None = None,
    max_depth: int | None = None,
) -> tuple[int, int] | None:
    """Find a strong move synchronously on the provided game object.

    Tests and emergency fallbacks call this directly.  Runtime bots normally use
    ``bot_think()``, which offloads this search to the bounded worker pool.
    """

    return _root_search(
        game,
        player.color,
        max_depth=max_depth or DEFAULT_DEPTH,
        time_limit=time_limit if time_limit is not None else DEFAULT_TIME_LIMIT,
        node_limit=node_limit or DEFAULT_NODE_LIMIT,
    )


def _submit_search(game: "ChessGame", player: "ChessPlayer", signature: str) -> None:
    search_game = _clone_game_for_search(game)
    cancel_event = Event()
    future = _EXECUTOR.submit(
        _root_search,
        search_game,
        player.color,
        max_depth=DEFAULT_DEPTH,
        time_limit=DEFAULT_TIME_LIMIT,
        node_limit=DEFAULT_NODE_LIMIT,
        cancel_event=cancel_event,
    )
    _bot_jobs(game)[player.id] = BotSearchJob(
        signature=signature,
        future=future,
        cancel_event=cancel_event,
    )


def cancel_bot_search(game: "ChessGame", player_id: str) -> None:
    """Cancel and forget one game-owned search, if present."""
    job = _bot_jobs(game).pop(player_id, None)
    if job is not None:
        job.cancel()


def cancel_all_bot_searches(game: "ChessGame") -> None:
    """Cancel and forget every search owned by one game instance."""
    jobs = list(_bot_jobs(game).values())
    _bot_jobs(game).clear()
    for job in jobs:
        job.cancel()


def _material_balance(game: "ChessGame", color: str) -> int:
    balance = 0
    for piece in game.board:
        if piece is None:
            continue
        value = _piece_value(piece)
        balance += value if piece.color == color else -value
    return balance


def bot_think(game: "ChessGame", player: "ChessPlayer") -> str | None:
    if game.promotion_pending and game.promotion_player_id == player.id:
        return "promote_queen"

    if game.draw_offer_from and game.draw_offer_from != player.id:
        if _material_balance(game, player.color) < -200:
            return "accept_draw"
        return "decline_draw"

    if game.undo_request_from and game.undo_request_from != player.id:
        return "decline_undo"

    if game.current_player != player:
        cancel_bot_search(game, player.id)
        return None

    if player.id in game.bot_move_targets and game.selected_square.get(player.id) is not None:
        to_sq = game.bot_move_targets.pop(player.id)
        row, col = game.square_to_view(player, to_sq)
        return game.grid_cell_action_id(row, col)

    signature = _search_signature(game, player)
    jobs = _bot_jobs(game)
    job = jobs.get(player.id)
    if job and job.signature != signature:
        cancel_bot_search(game, player.id)
        job = None

    if job is None:
        _submit_search(game, player, signature)
        return None

    if not job.future.done():
        return None

    jobs.pop(player.id, None)
    try:
        move = job.future.result()
    except Exception:
        move = find_best_move(game, player, time_limit=0.1, node_limit=20_000, max_depth=2)

    if move is None:
        return None

    legal, _ = game._is_legal_move(move[0], move[1], player.color)
    if not legal:
        move = find_best_move(game, player, time_limit=0.1, node_limit=20_000, max_depth=2)
        if move is None:
            return None

    from_sq, to_sq = move
    game.bot_move_targets[player.id] = to_sq
    row, col = game.square_to_view(player, from_sq)
    return game.grid_cell_action_id(row, col)
