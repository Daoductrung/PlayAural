"""Bot AI for Battleship."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ...game_utils.grid_mixin import grid_cell_id

if TYPE_CHECKING:
    from .game import BattleshipGame, BattleshipPlayer

# Cell state constants (mirrored from game.py)
CELL_EMPTY = 0
CELL_MISS = 2
CELL_HIT = 3


def bot_think(game: "BattleshipGame", player: "BattleshipPlayer") -> str | None:
    """Decide the bot's next action. Deploy is handled in on_tick."""
    if game.phase == "battling":
        return _bot_battle(game, player)
    return None


def _bot_battle(
    game: "BattleshipGame", player: "BattleshipPlayer",
) -> str | None:
    """Choose a target cell and fire."""
    if game.current_player != player:
        return None

    # Make sure bot is viewing shot board
    player.viewing_own = False

    target = _choose_target(game, player)
    if not target:
        return None

    row, col = target
    # Move cursor to target, then select
    cursor = game._get_cursor(player)
    cursor.row = row
    cursor.col = col
    return grid_cell_id(row, col)


def _choose_target(
    game: "BattleshipGame", player: "BattleshipPlayer",
) -> tuple[int, int] | None:
    """Smart target selection: hunt around hits, else pick random."""
    size = int(game.options.grid_size)

    # Phase 1: Look for unsunk hit cells and hunt around them
    hit_cells = []
    for r in range(size):
        for c in range(size):
            if player.shot_board[r][c] == CELL_HIT:
                hit_cells.append((r, c))

    # Filter to hits on ships not yet sunk
    from .game import _get_opponent
    opponent = _get_opponent(game, player)
    if not opponent:
        return None

    unsunk_hits = []
    for r, c in hit_cells:
        ship = game._find_ship_at(opponent, r, c)
        if ship and not ship.sunk:
            unsunk_hits.append((r, c))

    if unsunk_hits:
        # Hunt mode: try adjacent cells of unsunk hits
        candidates = _get_hunt_candidates(player.shot_board, unsunk_hits, size)
        if candidates:
            return random.choice(candidates)

    # Phase 2: Random targeting with checkerboard pattern (parity)
    parity_targets = []
    other_targets = []
    for r in range(size):
        for c in range(size):
            if player.shot_board[r][c] == CELL_EMPTY:
                if (r + c) % 2 == 0:
                    parity_targets.append((r, c))
                else:
                    other_targets.append((r, c))

    if parity_targets:
        return random.choice(parity_targets)
    if other_targets:
        return random.choice(other_targets)
    return None


def _get_hunt_candidates(
    shot_board: list[list[int]],
    unsunk_hits: list[tuple[int, int]],
    size: int,
) -> list[tuple[int, int]]:
    """Get valid adjacent cells around unsunk hit cells."""
    candidates = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # If we have 2+ collinear hits, prefer continuing that line
    if len(unsunk_hits) >= 2:
        line_candidates = _get_line_candidates(shot_board, unsunk_hits, size)
        if line_candidates:
            return line_candidates

    for r, c in unsunk_hits:
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                if shot_board[nr][nc] == CELL_EMPTY:
                    candidates.add((nr, nc))

    return list(candidates)


def _get_line_candidates(
    shot_board: list[list[int]],
    unsunk_hits: list[tuple[int, int]],
    size: int,
) -> list[tuple[int, int]]:
    """If hits are in a line, extend that line."""
    rows = {r for r, _ in unsunk_hits}
    cols = {c for _, c in unsunk_hits}
    candidates = []

    if len(rows) == 1:
        # Horizontal line
        row = next(iter(rows))
        min_c = min(c for _, c in unsunk_hits)
        max_c = max(c for _, c in unsunk_hits)
        if min_c - 1 >= 0 and shot_board[row][min_c - 1] == CELL_EMPTY:
            candidates.append((row, min_c - 1))
        if max_c + 1 < size and shot_board[row][max_c + 1] == CELL_EMPTY:
            candidates.append((row, max_c + 1))
    elif len(cols) == 1:
        # Vertical line
        col = next(iter(cols))
        min_r = min(r for r, _ in unsunk_hits)
        max_r = max(r for r, _ in unsunk_hits)
        if min_r - 1 >= 0 and shot_board[min_r - 1][col] == CELL_EMPTY:
            candidates.append((min_r - 1, col))
        if max_r + 1 < size and shot_board[max_r + 1][col] == CELL_EMPTY:
            candidates.append((max_r + 1, col))

    return candidates
