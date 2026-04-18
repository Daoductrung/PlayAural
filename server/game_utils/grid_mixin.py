"""Grid navigation mixin for 2D board games.

Provides a reusable foundation for games that use a 2D grid (Battleship,
Minesweeper, Chess, etc.).  The mixin manages per-player cursor state,
spatial keybind navigation, grid cell action generation, and the
``grid_enabled`` / ``grid_width`` protocol flags so that both the desktop
and web clients can render a proper 2D layout.

Cell content announcements are **not** handled here — subclasses must
override ``get_cell_label(row, col, player, locale)`` to describe what
is in each cell.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from mashumaro.mixins.json import DataClassJSONMixin

from .actions import Action, ActionSet, Visibility
from ..messages.localization import Localization

if TYPE_CHECKING:
    from ..games.base import Player
    from ..users.base import User


GRID_CELL_PREFIX = "grid_cell_"


@dataclass
class GridCursor(DataClassJSONMixin):
    """Per-player cursor position on the grid."""

    row: int = 0
    col: int = 0

    def __getitem__(self, index: int) -> int:
        if index == 0:
            return self.row
        if index == 1:
            return self.col
        raise IndexError(index)

    def __len__(self) -> int:
        return 2


class GridGameMixin:
    """Mixin adding 2D grid support to a Game subclass.

    Subclasses must set ``grid_rows`` and ``grid_cols`` before calling
    ``_init_grid()``.  Override ``get_cell_label`` to provide
    game-specific cell descriptions.

    Attributes consumed from the host Game class:
        - ``self.players``
        - ``self.status``
        - ``self.get_user(player) -> User | None``
        - ``self.get_active_players() -> list[Player]``
        - ``self.rebuild_all_menus()``
        - ``self.update_player_menu(player, selection_id=...)``

    Serialised fields (add to your Game dataclass):
        grid_rows: int
        grid_cols: int
        grid_cursors: dict[str, GridCursor]   # player_id -> cursor
        grid_row_labels: list[str]
        grid_col_labels: list[str]
    """

    # ------------------------------------------------------------------ #
    # Initialisation                                                      #
    # ------------------------------------------------------------------ #

    def _init_grid(self) -> None:
        """Initialise the grid state.  Call once from ``on_start``."""
        if not hasattr(self, "grid_cursors"):
            self.grid_cursors: dict[str, GridCursor] = {}
        else:
            self.grid_cursors = {
                player_id: self._coerce_grid_cursor(cursor)
                for player_id, cursor in self.grid_cursors.items()
            }
        for player in self.get_active_players():
            if player.id not in self.grid_cursors:
                self.grid_cursors[player.id] = GridCursor(row=0, col=0)
        if not hasattr(self, "grid_row_labels") or not self.grid_row_labels:
            self.grid_row_labels = [str(i + 1) for i in range(self.grid_rows)]
        if not hasattr(self, "grid_col_labels") or not self.grid_col_labels:
            self.grid_col_labels = [
                chr(ord("A") + i) for i in range(self.grid_cols)
            ]

    def _coerce_grid_cursor(self, value) -> GridCursor:
        if isinstance(value, GridCursor):
            return value
        if isinstance(value, (tuple, list)) and len(value) >= 2:
            return GridCursor(row=int(value[0]), col=int(value[1]))
        if isinstance(value, dict):
            return GridCursor(
                row=int(value.get("row", 0)),
                col=int(value.get("col", 0)),
            )
        return GridCursor(row=0, col=0)

    # ------------------------------------------------------------------ #
    # Abstract — subclasses MUST override                                 #
    # ------------------------------------------------------------------ #

    def get_cell_label(
        self, row: int, col: int, player: "Player", locale: str
    ) -> str:
        """Return the display label for one grid cell.

        This is what appears as the menu item text **and** what the
        screen reader speaks when the cursor lands on the cell.  Include
        the coordinate plus any game-specific content, e.g.
        ``"A1 — empty"`` or ``"B3 — hit"``.

        Must be overridden by every game that uses this mixin.
        """
        raise NotImplementedError(
            "Subclasses must implement get_cell_label(row, col, player, locale)"
        )

    # ------------------------------------------------------------------ #
    # Optional hooks — subclasses MAY override                            #
    # ------------------------------------------------------------------ #

    def on_grid_select(self, player: "Player", row: int, col: int) -> None:
        """Called when a player selects (Enter / tap) a grid cell.

        Override to implement game-specific selection logic (fire a shot,
        place a piece, reveal a cell, etc.).
        """
        pass

    def is_grid_cell_enabled(
        self, player: "Player", row: int, col: int
    ) -> str | None:
        """Return ``None`` if the cell is selectable, or a disabled-reason
        localization key if not.  Default: all cells enabled during play.
        """
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def is_grid_cell_hidden(
        self, player: "Player", row: int, col: int
    ) -> Visibility:
        """Return cell visibility.  Default: all cells visible during play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # ------------------------------------------------------------------ #
    # Cursor helpers                                                      #
    # ------------------------------------------------------------------ #

    def _get_cursor(self, player: "Player") -> GridCursor:
        cursor = self.grid_cursors.get(player.id)
        if cursor is None:
            cursor = GridCursor(row=0, col=0)
        else:
            cursor = self._coerce_grid_cursor(cursor)
        self.grid_cursors[player.id] = cursor
        return cursor

    def _clamp_cursor(self, cursor: GridCursor) -> None:
        cursor.row = max(0, min(cursor.row, self.grid_rows - 1))
        cursor.col = max(0, min(cursor.col, self.grid_cols - 1))

    def _cursor_cell_id(self, cursor: GridCursor) -> str:
        return grid_cell_id(cursor.row, cursor.col)

    # ------------------------------------------------------------------ #
    # Coordinate ↔ action-ID conversion                                   #
    # ------------------------------------------------------------------ #

    def _grid_position_for_cursor(self, cursor: GridCursor) -> int:
        """Return 1-based flat index for the cursor position."""
        return cursor.row * self.grid_cols + cursor.col + 1

    # ------------------------------------------------------------------ #
    # Navigation actions (server-side spatial keybinds)                   #
    # ------------------------------------------------------------------ #

    def _action_grid_move(
        self, player: "Player", action_id: str
    ) -> None:
        cursor = self._get_cursor(player)
        direction = action_id.removeprefix("grid_move_")

        old_row, old_col = cursor.row, cursor.col
        if direction == "up" and cursor.row > 0:
            cursor.row -= 1
        elif direction == "down" and cursor.row < self.grid_rows - 1:
            cursor.row += 1
        elif direction == "left" and cursor.col > 0:
            cursor.col -= 1
        elif direction == "right" and cursor.col < self.grid_cols - 1:
            cursor.col += 1

        if cursor.row == old_row and cursor.col == old_col:
            return  # at edge, do nothing

        user = self.get_user(player)
        if user:
            locale = user.locale
            label = self.get_cell_label(cursor.row, cursor.col, player, locale)
            user.speak(label, buffer="game")
        self.update_player_menu(
            player, selection_id=self._cursor_cell_id(cursor)
        )

    def _action_grid_select(
        self, player: "Player", action_id: str
    ) -> None:
        cursor = self._get_cursor(player)
        self.on_grid_select(player, cursor.row, cursor.col)

    # ------------------------------------------------------------------ #
    # Visibility / enabled callbacks for navigation actions               #
    # ------------------------------------------------------------------ #

    def _is_grid_nav_enabled(self, player: "Player") -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_grid_nav_hidden(self, player: "Player") -> Visibility:
        return Visibility.HIDDEN  # never shown in menu

    def _is_grid_select_enabled(self, player: "Player") -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        cursor = self._get_cursor(player)
        return self.is_grid_cell_enabled(player, cursor.row, cursor.col)

    def _is_grid_select_hidden(self, player: "Player") -> Visibility:
        return Visibility.HIDDEN  # triggered by keybind, not menu

    # ------------------------------------------------------------------ #
    # Cell action callbacks (per-cell, dispatched by action_id)           #
    # ------------------------------------------------------------------ #

    def _action_grid_cell(
        self, player: "Player", action_id: str
    ) -> None:
        """Handler for tapping / clicking a grid cell (web / touch)."""
        coords = parse_grid_cell_id(action_id)
        if coords is None:
            return
        row, col = coords
        if row < 0 or row >= self.grid_rows or col < 0 or col >= self.grid_cols:
            return
        cursor = self._get_cursor(player)
        cursor.row, cursor.col = row, col
        self.on_grid_select(player, row, col)

    def _is_grid_cell_enabled(
        self, player: "Player", *, action_id: str | None = None
    ) -> str | None:
        if not action_id:
            return "action-not-available"
        coords = parse_grid_cell_id(action_id)
        if coords is None:
            return "action-not-available"
        return self.is_grid_cell_enabled(player, coords[0], coords[1])

    def _is_grid_cell_hidden(
        self, player: "Player", *, action_id: str | None = None
    ) -> Visibility:
        if not action_id:
            return Visibility.HIDDEN
        coords = parse_grid_cell_id(action_id)
        if coords is None:
            return Visibility.HIDDEN
        return self.is_grid_cell_hidden(player, coords[0], coords[1])

    def _get_grid_cell_label(
        self, player: "Player", action_id: str
    ) -> str:
        coords = parse_grid_cell_id(action_id)
        if coords is None:
            return action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return self.get_cell_label(coords[0], coords[1], player, locale)

    # ------------------------------------------------------------------ #
    # Keybind setup helper                                                #
    # ------------------------------------------------------------------ #

    def setup_grid_keybinds(self) -> None:
        """Register spatial navigation keybinds.  Call from
        ``setup_keybinds`` **after** ``super().setup_keybinds()``.

        Arrow-key navigation is handled client-side when
        ``grid_enabled=True`` (desktop) or via the CSS grid (web).
        These server-side keybinds are a fallback for the select action
        and for any client that doesn't support native grid mode.
        """
        from ..ui.keybinds import KeybindState

        self.define_keybind(
            "enter", "Select cell", ["grid_select"],
            state=KeybindState.ACTIVE,
        )

    # ------------------------------------------------------------------ #
    # Turn action-set builder                                             #
    # ------------------------------------------------------------------ #

    def build_grid_actions(self, player: "Player") -> list[Action]:
        """Build Action objects for every grid cell.

        Returns a flat list in row-major order that the menu system can
        render either linearly or as a grid (via ``grid_enabled`` /
        ``grid_width``).
        """
        actions: list[Action] = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_id = grid_cell_id(row, col)
                actions.append(
                    Action(
                        id=cell_id,
                        label="",
                        handler="_action_grid_cell",
                        is_enabled="_is_grid_cell_enabled",
                        is_hidden="_is_grid_cell_hidden",
                        get_label="_get_grid_cell_label",
                        show_in_actions_menu=False,
                    )
                )
        return actions

    def build_grid_nav_actions(self) -> list[Action]:
        """Build hidden navigation + select actions (for keybind use)."""
        actions: list[Action] = []
        for direction in ("up", "down", "left", "right"):
            actions.append(
                Action(
                    id=f"grid_move_{direction}",
                    label=f"Move {direction}",
                    handler="_action_grid_move",
                    is_enabled="_is_grid_nav_enabled",
                    is_hidden="_is_grid_nav_hidden",
                    show_in_actions_menu=False,
                )
            )
        actions.append(
            Action(
                id="grid_select",
                label="Select",
                handler="_action_grid_select",
                is_enabled="_is_grid_select_enabled",
                is_hidden="_is_grid_select_hidden",
                show_in_actions_menu=False,
            )
        )
        return actions

    # ------------------------------------------------------------------ #
    # Grid-aware menu rebuild                                             #
    # ------------------------------------------------------------------ #

    def _build_grid_menu_kwargs(self) -> dict:
        """Return extra kwargs for ``show_menu`` to enable grid mode.

        Only returns grid params when the game is actively playing.
        Lobby and end screens use normal linear menus.
        """
        if self.status != "playing":
            return {}
        return {
            "grid_enabled": True,
            "grid_height": self.grid_rows,
            "grid_width": self.grid_cols,
        }

    def _grid_cell_coordinate(self, row: int, col: int) -> str:
        """Return the human-readable coordinate label, e.g. 'A1'."""
        col_label = (
            self.grid_col_labels[col]
            if col < len(self.grid_col_labels)
            else str(col)
        )
        row_label = (
            self.grid_row_labels[row]
            if row < len(self.grid_row_labels)
            else str(row)
        )
        return f"{col_label}{row_label}"


# ---------------------------------------------------------------------- #
# Module-level helpers                                                    #
# ---------------------------------------------------------------------- #


def grid_cell_id(row: int, col: int) -> str:
    """Encode a (row, col) pair into an action ID."""
    return f"{GRID_CELL_PREFIX}{row}_{col}"


def parse_grid_cell_id(action_id: str) -> tuple[int, int] | None:
    """Decode an action ID back to (row, col), or None if invalid."""
    if not action_id.startswith(GRID_CELL_PREFIX):
        return None
    rest = action_id.removeprefix(GRID_CELL_PREFIX)
    parts = rest.split("_", 1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None
