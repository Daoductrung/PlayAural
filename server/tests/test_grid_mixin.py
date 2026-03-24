"""Tests for the GridGameMixin."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from ..games.base import Game, Player, GameOptions
from ..games.registry import register_game
from ..game_utils.actions import Action, ActionSet, Visibility
from ..game_utils.grid_mixin import (
    GridGameMixin,
    GridCursor,
    grid_cell_id,
    parse_grid_cell_id,
    GRID_CELL_PREFIX,
)
from ..messages.localization import Localization
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


# ------------------------------------------------------------------ #
# Minimal concrete game for testing                                   #
# ------------------------------------------------------------------ #

@dataclass
class GridTestOptions(GameOptions):
    pass


@dataclass
class GridTestPlayer(Player):
    pass


@dataclass
class GridTestGame(GridGameMixin, Game):
    """Minimal grid game used exclusively for unit tests."""

    players: list[GridTestPlayer] = field(default_factory=list)
    options: GridTestOptions = field(default_factory=GridTestOptions)

    # Grid state (serialisable fields)
    grid_rows: int = 5
    grid_cols: int = 5
    grid_cursors: dict[str, GridCursor] = field(default_factory=dict)
    grid_row_labels: list[str] = field(default_factory=list)
    grid_col_labels: list[str] = field(default_factory=list)

    # Track select calls for assertions
    select_log: list[tuple[str, int, int]] = field(default_factory=list)

    # Per-cell state for testing visibility / enabled
    blocked_cells: set[tuple[int, int]] = field(default_factory=set)
    hidden_cells: set[tuple[int, int]] = field(default_factory=set)

    @classmethod
    def get_name(cls) -> str:
        return "Grid Test"

    @classmethod
    def get_type(cls) -> str:
        return "gridtest"

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> GridTestPlayer:
        return GridTestPlayer(id=player_id, name=name, is_bot=is_bot)

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self._init_grid()
        self.set_turn_players(self.get_active_players())
        for player in self.get_active_players():
            self._sync_grid_turn_actions(player)
        self.rebuild_all_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()

    def bot_think(self, player: Player) -> str | None:
        return None

    def get_cell_label(self, row: int, col: int, player: Player, locale: str) -> str:
        coord = self._grid_cell_coordinate(row, col)
        if (row, col) in self.blocked_cells:
            return f"{coord} blocked"
        return f"{coord} empty"

    def on_grid_select(self, player: Player, row: int, col: int) -> None:
        self.select_log.append((player.id, row, col))

    def is_grid_cell_enabled(self, player: Player, row: int, col: int) -> str | None:
        if (row, col) in self.blocked_cells:
            return "action-not-available"
        return super().is_grid_cell_enabled(player, row, col)

    def is_grid_cell_hidden(self, player: Player, row: int, col: int) -> Visibility:
        if (row, col) in self.hidden_cells:
            return Visibility.HIDDEN
        return super().is_grid_cell_hidden(player, row, col)

    def create_turn_action_set(self, player: Player) -> ActionSet:
        action_set = ActionSet(name="turn")
        for action in self.build_grid_actions(player):
            action_set.add(action)
        for action in self.build_grid_nav_actions():
            action_set.add(action)
        return action_set

    def _sync_grid_turn_actions(self, player: Player) -> None:
        action_sets = self.player_action_sets.get(player.id, [])
        turn_set = next((s for s in action_sets if s.name == "turn"), None)
        if turn_set is None:
            return
        turn_set.remove_by_prefix(GRID_CELL_PREFIX)
        for action in self.build_grid_actions(player):
            turn_set.add(action)

    def rebuild_player_menu(self, player: Player) -> None:
        self._sync_grid_turn_actions(player)
        super().rebuild_player_menu(player)

    def update_player_menu(self, player: Player, selection_id: str | None = None) -> None:
        self._sync_grid_turn_actions(player)
        super().update_player_menu(player, selection_id=selection_id)

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.setup_grid_keybinds()

    def build_game_result(self):
        from ..game_utils.game_result import GameResult
        return GameResult(game_type="gridtest", timestamp="", duration_ticks=0, player_results=[])

    def format_end_screen(self, result, locale: str) -> list[str]:
        return ["Game over"]


# ------------------------------------------------------------------ #
# Test helpers                                                        #
# ------------------------------------------------------------------ #


def make_game(rows: int = 5, cols: int = 5, player_count: int = 2, start: bool = False) -> GridTestGame:
    game = GridTestGame(grid_rows=rows, grid_cols=cols)
    game.setup_keybinds()
    for i in range(player_count):
        name = f"Player{i + 1}"
        game.add_player(name, MockUser(name, uuid=f"p{i + 1}"))
    game.host = "Player1"
    if start:
        game.on_start()
    return game


# ------------------------------------------------------------------ #
# Unit tests: coordinate encoding                                     #
# ------------------------------------------------------------------ #


class TestCoordinateEncoding:
    def test_grid_cell_id_roundtrip(self) -> None:
        for row in range(10):
            for col in range(10):
                cell_id = grid_cell_id(row, col)
                assert cell_id.startswith(GRID_CELL_PREFIX)
                parsed = parse_grid_cell_id(cell_id)
                assert parsed == (row, col)

    def test_parse_invalid_id_returns_none(self) -> None:
        assert parse_grid_cell_id("not_a_cell") is None
        assert parse_grid_cell_id("grid_cell_") is None
        assert parse_grid_cell_id("grid_cell_abc") is None
        assert parse_grid_cell_id("grid_cell_1") is None
        assert parse_grid_cell_id("grid_cell_1_abc") is None
        assert parse_grid_cell_id("") is None


# ------------------------------------------------------------------ #
# Unit tests: grid initialisation                                     #
# ------------------------------------------------------------------ #


class TestGridInit:
    def test_init_creates_cursors_for_all_players(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        for player in game.get_active_players():
            assert player.id in game.grid_cursors
            cursor = game.grid_cursors[player.id]
            assert cursor.row == 0
            assert cursor.col == 0

    def test_init_generates_default_labels(self) -> None:
        game = make_game(rows=3, cols=4, start=True)
        assert game.grid_row_labels == ["1", "2", "3"]
        assert game.grid_col_labels == ["A", "B", "C", "D"]

    def test_init_preserves_custom_labels(self) -> None:
        game = GridTestGame(grid_rows=2, grid_cols=2)
        game.grid_row_labels = ["X", "Y"]
        game.grid_col_labels = ["M", "N"]
        game.setup_keybinds()
        game.add_player("P1", MockUser("P1", uuid="p1"))
        game.host = "P1"
        game.on_start()
        assert game.grid_row_labels == ["X", "Y"]
        assert game.grid_col_labels == ["M", "N"]

    def test_coordinate_label_format(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        assert game._grid_cell_coordinate(0, 0) == "A1"
        assert game._grid_cell_coordinate(2, 2) == "C3"
        assert game._grid_cell_coordinate(1, 0) == "A2"
        assert game._grid_cell_coordinate(0, 2) == "C1"


# ------------------------------------------------------------------ #
# Unit tests: cursor navigation                                      #
# ------------------------------------------------------------------ #


class TestCursorNavigation:
    def test_move_right_increments_col(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)
        assert cursor.col == 0

        game._action_grid_move(player, "grid_move_right")
        assert cursor.col == 1

    def test_move_left_decrements_col(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)
        cursor.col = 2

        game._action_grid_move(player, "grid_move_left")
        assert cursor.col == 1

    def test_move_down_increments_row(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)

        game._action_grid_move(player, "grid_move_down")
        assert cursor.row == 1

    def test_move_up_decrements_row(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)
        cursor.row = 2

        game._action_grid_move(player, "grid_move_up")
        assert cursor.row == 1

    def test_cannot_move_past_left_edge(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)
        assert cursor.col == 0

        game._action_grid_move(player, "grid_move_left")
        assert cursor.col == 0  # unchanged

    def test_cannot_move_past_right_edge(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)
        cursor.col = 2  # rightmost

        game._action_grid_move(player, "grid_move_right")
        assert cursor.col == 2

    def test_cannot_move_past_top_edge(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)
        assert cursor.row == 0

        game._action_grid_move(player, "grid_move_up")
        assert cursor.row == 0

    def test_cannot_move_past_bottom_edge(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)
        cursor.row = 2

        game._action_grid_move(player, "grid_move_down")
        assert cursor.row == 2

    def test_move_speaks_cell_label(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        user = game.get_user(player)
        assert user is not None
        user.clear_messages()

        game._action_grid_move(player, "grid_move_right")

        spoken = user.get_last_spoken()
        assert spoken is not None
        assert "B1" in spoken
        assert "empty" in spoken

    def test_move_at_edge_does_not_speak(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        user = game.get_user(player)
        assert user is not None
        user.clear_messages()

        game._action_grid_move(player, "grid_move_left")  # already at col 0

        spoken = user.get_last_spoken()
        assert spoken is None  # no TTS on no-op

    def test_cursors_are_independent_per_player(self) -> None:
        game = make_game(rows=5, cols=5, start=True)
        p1, p2 = game.get_active_players()

        game._action_grid_move(p1, "grid_move_right")
        game._action_grid_move(p1, "grid_move_right")
        game._action_grid_move(p1, "grid_move_down")

        c1 = game._get_cursor(p1)
        c2 = game._get_cursor(p2)
        assert c1.row == 1 and c1.col == 2
        assert c2.row == 0 and c2.col == 0

    def test_full_traversal(self) -> None:
        """Move cursor across every cell of a small grid via snake path."""
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)

        visited = {(cursor.row, cursor.col)}
        # Row 0: right, right
        for _ in range(2):
            game._action_grid_move(player, "grid_move_right")
            visited.add((cursor.row, cursor.col))
        # Row 1: down, left, left
        game._action_grid_move(player, "grid_move_down")
        visited.add((cursor.row, cursor.col))
        for _ in range(2):
            game._action_grid_move(player, "grid_move_left")
            visited.add((cursor.row, cursor.col))
        # Row 2: down, right, right
        game._action_grid_move(player, "grid_move_down")
        visited.add((cursor.row, cursor.col))
        for _ in range(2):
            game._action_grid_move(player, "grid_move_right")
            visited.add((cursor.row, cursor.col))

        assert len(visited) == 9  # all 3x3 cells visited


# ------------------------------------------------------------------ #
# Unit tests: cell selection                                          #
# ------------------------------------------------------------------ #


class TestCellSelection:
    def test_grid_select_calls_on_grid_select(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)
        cursor.row, cursor.col = 1, 2

        game._action_grid_select(player, "grid_select")

        assert len(game.select_log) == 1
        assert game.select_log[0] == (player.id, 1, 2)

    def test_cell_tap_calls_on_grid_select(self) -> None:
        """Simulate web client tapping a cell directly."""
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]

        game._action_grid_cell(player, grid_cell_id(2, 1))

        assert len(game.select_log) == 1
        assert game.select_log[0] == (player.id, 2, 1)

    def test_cell_tap_updates_cursor(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        cursor = game._get_cursor(player)
        assert cursor.row == 0 and cursor.col == 0

        game._action_grid_cell(player, grid_cell_id(2, 1))

        assert cursor.row == 2 and cursor.col == 1

    def test_cell_tap_out_of_bounds_ignored(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]

        game._action_grid_cell(player, grid_cell_id(10, 10))
        assert len(game.select_log) == 0

    def test_cell_tap_invalid_action_id_ignored(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]

        game._action_grid_cell(player, "not_a_grid_cell")
        assert len(game.select_log) == 0


# ------------------------------------------------------------------ #
# Unit tests: visibility and enabled                                  #
# ------------------------------------------------------------------ #


class TestCellVisibility:
    def test_blocked_cell_returns_disabled_reason(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        game.blocked_cells.add((1, 1))

        reason = game._is_grid_cell_enabled(player, action_id=grid_cell_id(1, 1))
        assert reason == "action-not-available"

        reason_ok = game._is_grid_cell_enabled(player, action_id=grid_cell_id(0, 0))
        assert reason_ok is None

    def test_hidden_cell_returns_hidden(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        game.hidden_cells.add((2, 0))

        vis = game._is_grid_cell_hidden(player, action_id=grid_cell_id(2, 0))
        assert vis == Visibility.HIDDEN

        vis_ok = game._is_grid_cell_hidden(player, action_id=grid_cell_id(0, 0))
        assert vis_ok == Visibility.VISIBLE

    def test_spectator_cannot_select(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        player.is_spectator = True

        reason = game.is_grid_cell_enabled(player, 0, 0)
        assert reason == "action-spectator"

    def test_not_playing_cells_hidden(self) -> None:
        game = make_game(rows=3, cols=3, start=False)
        player = game.get_active_players()[0]

        vis = game.is_grid_cell_hidden(player, 0, 0)
        assert vis == Visibility.HIDDEN


# ------------------------------------------------------------------ #
# Unit tests: action generation                                       #
# ------------------------------------------------------------------ #


class TestActionGeneration:
    def test_build_grid_actions_count(self) -> None:
        game = make_game(rows=4, cols=6, start=True)
        player = game.get_active_players()[0]
        actions = game.build_grid_actions(player)
        assert len(actions) == 4 * 6

    def test_build_grid_actions_row_major_order(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        actions = game.build_grid_actions(player)
        ids = [a.id for a in actions]
        expected = [grid_cell_id(r, c) for r in range(3) for c in range(3)]
        assert ids == expected

    def test_build_grid_nav_actions(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        nav_actions = game.build_grid_nav_actions()
        ids = {a.id for a in nav_actions}
        assert ids == {"grid_move_up", "grid_move_down", "grid_move_left", "grid_move_right", "grid_select"}

    def test_nav_actions_hidden_from_menu(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        nav_actions = game.build_grid_nav_actions()
        for action in nav_actions:
            assert action.show_in_actions_menu is False

    def test_cell_actions_hidden_from_actions_menu(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        actions = game.build_grid_actions(player)
        for action in actions:
            assert action.show_in_actions_menu is False


# ------------------------------------------------------------------ #
# Unit tests: dynamic cell labels                                     #
# ------------------------------------------------------------------ #


class TestCellLabels:
    def test_get_label_returns_game_specific_content(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]

        label = game._get_grid_cell_label(player, grid_cell_id(0, 0))
        assert "A1" in label
        assert "empty" in label

    def test_get_label_blocked_cell(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        game.blocked_cells.add((1, 2))

        label = game._get_grid_cell_label(player, grid_cell_id(1, 2))
        assert "C2" in label
        assert "blocked" in label

    def test_get_label_invalid_id_returns_raw(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        label = game._get_grid_cell_label(player, "not_a_cell")
        assert label == "not_a_cell"


# ------------------------------------------------------------------ #
# Unit tests: grid menu kwargs                                        #
# ------------------------------------------------------------------ #


class TestGridMenuKwargs:
    def test_playing_returns_grid_params(self) -> None:
        game = make_game(rows=5, cols=8, start=True)
        kwargs = game._build_grid_menu_kwargs()
        assert kwargs == {"grid_enabled": True, "grid_width": 8}

    def test_waiting_returns_empty(self) -> None:
        game = make_game(rows=5, cols=8, start=False)
        kwargs = game._build_grid_menu_kwargs()
        assert kwargs == {}

    def test_grid_params_reach_show_menu(self) -> None:
        """Verify that grid kwargs are passed through to user.show_menu."""
        game = make_game(rows=4, cols=6, start=True)
        player = game.get_active_players()[0]
        user = game.get_user(player)
        assert user is not None

        game.rebuild_player_menu(player)

        menu_data = user.menus.get("turn_menu")
        assert menu_data is not None
        assert menu_data.get("grid_enabled") is True
        assert menu_data.get("grid_width") == 6

    def test_grid_params_reach_update_menu_after_cursor_move(self) -> None:
        game = make_game(rows=4, cols=6, start=True)
        player = game.get_active_players()[0]
        user = game.get_user(player)
        assert user is not None

        user.messages.clear()
        game._action_grid_move(player, "grid_move_right")

        update_message = next(
            message for message in reversed(user.messages)
            if message.type == "update_menu"
        )
        assert update_message.data["grid_enabled"] is True
        assert update_message.data["grid_width"] == 6
        assert update_message.data["selection_id"] == grid_cell_id(0, 1)
        assert user.menus["turn_menu"]["grid_enabled"] is True
        assert user.menus["turn_menu"]["grid_width"] == 6

    def test_non_grid_game_no_grid_params(self) -> None:
        """A regular game (without GridGameMixin) should not have grid params."""
        # GridTestGame has the mixin, but when status != playing, no grid params
        game = make_game(rows=4, cols=6, start=False)
        # Manually add a player and rebuild
        player = game.get_active_players()[0]
        game.rebuild_player_menu(player)
        user = game.get_user(player)
        if user and "turn_menu" in user.menus:
            menu_data = user.menus["turn_menu"]
            # In waiting state, grid should not be enabled
            assert not menu_data.get("grid_enabled", False)

    def test_non_grid_menu_updates_keep_list_layout_defaults(self) -> None:
        user = MockUser("ListPlayer", uuid="list-player")

        user.show_menu("turn_menu", ["First item"])
        user.update_menu("turn_menu", ["Updated item"], selection_id="item_1")

        assert user.menus["turn_menu"]["grid_enabled"] is False
        assert user.menus["turn_menu"]["grid_width"] == 1
        update_message = user.messages[-1]
        assert update_message.type == "update_menu"
        assert update_message.data["grid_enabled"] is False
        assert update_message.data["grid_width"] == 1


# ------------------------------------------------------------------ #
# Unit tests: turn menu cell count                                    #
# ------------------------------------------------------------------ #


class TestTurnMenuIntegration:
    def test_turn_menu_has_all_grid_cells(self) -> None:
        game = make_game(rows=3, cols=4, start=True)
        player = game.get_active_players()[0]
        user = game.get_user(player)
        assert user is not None

        menu_data = user.menus.get("turn_menu")
        assert menu_data is not None
        items = menu_data["items"]

        cell_ids = [
            item.id for item in items
            if hasattr(item, "id") and item.id and item.id.startswith(GRID_CELL_PREFIX)
        ]
        assert len(cell_ids) == 3 * 4

    def test_hidden_cells_excluded_from_visible_menu(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        player = game.get_active_players()[0]
        game.hidden_cells.add((0, 0))
        game.hidden_cells.add((1, 1))
        game.rebuild_player_menu(player)

        user = game.get_user(player)
        visible = game.get_all_visible_actions(player)
        visible_ids = {r.action.id for r in visible}

        assert grid_cell_id(0, 0) not in visible_ids
        assert grid_cell_id(1, 1) not in visible_ids
        assert grid_cell_id(2, 2) in visible_ids


# ------------------------------------------------------------------ #
# Unit tests: keybinds                                                #
# ------------------------------------------------------------------ #


class TestKeybinds:
    def test_enter_keybind_registered(self) -> None:
        game = make_game(rows=3, cols=3)
        binds = game._keybinds.get("enter", [])
        select_binds = [b for b in binds if "grid_select" in b.actions]
        assert len(select_binds) == 1

    def test_no_reserved_key_conflicts(self) -> None:
        """Grid mixin keybinds must not collide with base reserved keys."""
        game = make_game(rows=3, cols=3)
        # enter is used by start_game (IDLE) and grid_select (ACTIVE)
        # these don't conflict because they have different states
        enter_binds = game._keybinds.get("enter", [])
        from ..ui.keybinds import KeybindState
        states = {b.state for b in enter_binds}
        # Must have both IDLE and ACTIVE, never two ACTIVE on same key
        active_count = sum(1 for b in enter_binds if b.state == KeybindState.ACTIVE)
        assert active_count == 1  # only grid_select


# ------------------------------------------------------------------ #
# Unit tests: position tracking                                      #
# ------------------------------------------------------------------ #


class TestPositionTracking:
    def test_grid_position_for_cursor_first_cell(self) -> None:
        game = make_game(rows=5, cols=10, start=True)
        cursor = GridCursor(row=0, col=0)
        assert game._grid_position_for_cursor(cursor) == 1

    def test_grid_position_for_cursor_second_row(self) -> None:
        game = make_game(rows=5, cols=10, start=True)
        cursor = GridCursor(row=1, col=3)
        # row=1, col=3 in 10-col grid => flat index 13 => 1-based = 14
        assert game._grid_position_for_cursor(cursor) == 14

    def test_grid_position_for_cursor_last_cell(self) -> None:
        game = make_game(rows=5, cols=10, start=True)
        cursor = GridCursor(row=4, col=9)
        assert game._grid_position_for_cursor(cursor) == 50

    def test_clamp_cursor_within_bounds(self) -> None:
        game = make_game(rows=3, cols=3, start=True)
        cursor = GridCursor(row=5, col=-1)
        game._clamp_cursor(cursor)
        assert cursor.row == 2
        assert cursor.col == 0
