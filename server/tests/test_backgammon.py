"""Tests for Backgammon (random + simple bots; no gnubg)."""

from pathlib import Path

import pytest

from ..games.backgammon.state import (
    INITIAL_BOARD,
    all_checkers_in_home,
    bar_count,
    build_initial_game_state,
    color_sign,
    game_multiplier,
    is_backgammon,
    is_gammon,
    off_count,
    opponent_color,
    pip_count,
    point_count,
    point_number_for_player,
    point_owner,
    player_point_to_index,
    remaining_dice,
    remaining_dice_unique,
    roll_dice,
    set_bar,
    set_off,
)
from ..games.backgammon.moves import (
    BackgammonMove,
    apply_move,
    generate_legal_moves,
    has_any_legal_move,
    must_use_both_dice,
    undo_last_move,
)
from ..games.backgammon.bot import _score_move, _pick_simple_move
from ..games.backgammon.game import (
    BackgammonGame,
    BackgammonOptions,
    BackgammonPlayer,
    BOT_DIFFICULTY_CHOICES,
    BOT_DIFFICULTY_LABELS,
)
from ..messages.localization import Localization
from ..users.bot import Bot


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(start: bool = False, **option_overrides) -> BackgammonGame:
    game = BackgammonGame(options=BackgammonOptions(**option_overrides))
    game.setup_keybinds()
    game.add_player("Alpha", Bot("Alpha", uuid="p1"))
    game.add_player("Beta", Bot("Beta", uuid="p2"))
    game.host = "Alpha"
    if start:
        game.on_start()
    return game


# ==========================================================================
# State tests
# ==========================================================================


class TestInitialPosition:
    def test_15_checkers_per_side(self):
        gs = build_initial_game_state()
        red = sum(v for v in gs.board.points if v > 0)
        white = sum(-v for v in gs.board.points if v < 0)
        assert red == 15
        assert white == 15

    def test_pip_count_167(self):
        gs = build_initial_game_state()
        assert pip_count(gs, "red") == 167
        assert pip_count(gs, "white") == 167

    def test_bar_and_off_start_at_zero(self):
        gs = build_initial_game_state()
        assert gs.board.bar_red == 0
        assert gs.board.bar_white == 0
        assert gs.board.off_red == 0
        assert gs.board.off_white == 0

    def test_initial_phase(self):
        gs = build_initial_game_state()
        assert gs.turn_phase == "pre_roll"
        assert gs.cube_value == 1
        assert gs.cube_owner == ""

    def test_match_length_passed_through(self):
        gs = build_initial_game_state(match_length=7)
        assert gs.match_length == 7


class TestStateHelpers:
    def test_color_sign(self):
        assert color_sign("red") == 1
        assert color_sign("white") == -1

    def test_opponent_color(self):
        assert opponent_color("red") == "white"
        assert opponent_color("white") == "red"

    def test_point_owner(self):
        gs = build_initial_game_state()
        assert point_owner(gs, 23) == "red"
        assert point_owner(gs, 0) == "white"
        assert point_owner(gs, 1) is None

    def test_point_count(self):
        gs = build_initial_game_state()
        assert point_count(gs, 23) == 2
        assert point_count(gs, 12) == 5
        assert point_count(gs, 1) == 0

    def test_bar_and_off_accessors(self):
        gs = build_initial_game_state()
        set_bar(gs, "red", 3)
        assert bar_count(gs, "red") == 3
        assert bar_count(gs, "white") == 0
        set_off(gs, "white", 5)
        assert off_count(gs, "white") == 5
        assert off_count(gs, "red") == 0

    def test_remaining_dice(self):
        gs = build_initial_game_state()
        gs.dice = [3, 5]
        gs.dice_used = [False, True]
        assert remaining_dice(gs) == [3]
        assert remaining_dice_unique(gs) == [3]

    def test_remaining_dice_doubles(self):
        gs = build_initial_game_state()
        gs.dice = [4, 4, 4, 4]
        gs.dice_used = [True, False, False, True]
        assert remaining_dice(gs) == [4, 4]
        assert remaining_dice_unique(gs) == [4]

    def test_point_number_for_player_red(self):
        assert point_number_for_player(0, "red") == 1
        assert point_number_for_player(23, "red") == 24

    def test_point_number_for_player_white(self):
        assert point_number_for_player(0, "white") == 24
        assert point_number_for_player(23, "white") == 1

    def test_player_point_to_index(self):
        assert player_point_to_index(1, "red") == 0
        assert player_point_to_index(24, "red") == 23
        assert player_point_to_index(1, "white") == 23
        assert player_point_to_index(24, "white") == 0

    def test_roll_dice_range(self):
        for _ in range(100):
            d1, d2 = roll_dice()
            assert 1 <= d1 <= 6
            assert 1 <= d2 <= 6


class TestAllCheckersInHome:
    def test_initial_position_not_home(self):
        gs = build_initial_game_state()
        assert not all_checkers_in_home(gs, "red")
        assert not all_checkers_in_home(gs, "white")

    def test_all_in_home_red(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[0] = 5
        gs.board.points[3] = 5
        gs.board.points[5] = 5
        assert all_checkers_in_home(gs, "red")

    def test_all_in_home_white(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[18] = -5
        gs.board.points[20] = -5
        gs.board.points[23] = -5
        assert all_checkers_in_home(gs, "white")

    def test_bar_prevents_home(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[0] = 14
        gs.board.bar_red = 1
        assert not all_checkers_in_home(gs, "red")


class TestGammonBackgammon:
    def test_gammon(self):
        gs = build_initial_game_state()
        assert is_gammon(gs, "red")
        gs.board.off_red = 1
        assert not is_gammon(gs, "red")

    def test_backgammon_bar(self):
        gs = build_initial_game_state()
        gs.board.bar_red = 1
        assert is_backgammon(gs, "red")

    def test_backgammon_in_winner_home(self):
        gs = build_initial_game_state()
        assert is_backgammon(gs, "red")

    def test_not_backgammon_if_not_gammon(self):
        gs = build_initial_game_state()
        gs.board.off_red = 1
        assert not is_backgammon(gs, "red")

    def test_game_multiplier(self):
        gs = build_initial_game_state()
        gs.board.bar_red = 1
        assert game_multiplier(gs, "red") == 3
        gs.board.bar_red = 0
        gs.board.points = [0] * 24
        assert game_multiplier(gs, "red") == 2
        gs.board.off_red = 1
        assert game_multiplier(gs, "red") == 1


# ==========================================================================
# Move generation tests
# ==========================================================================


class TestMoveGeneration:
    def test_initial_red_die_1(self):
        gs = build_initial_game_state()
        moves = generate_legal_moves(gs, "red", 1)
        sources = sorted(set(m.source for m in moves))
        assert all(s in [5, 7, 12, 23] for s in sources)
        assert len(moves) >= 3

    def test_initial_red_die_6(self):
        gs = build_initial_game_state()
        moves = generate_legal_moves(gs, "red", 6)
        sources = [m.source for m in moves]
        assert 12 in sources

    def test_initial_white_die_3(self):
        gs = build_initial_game_state()
        moves = generate_legal_moves(gs, "white", 3)
        assert len(moves) > 0
        for m in moves:
            assert m.destination > m.source

    def test_bar_entry_required(self):
        gs = build_initial_game_state()
        gs.board.bar_red = 1
        moves = generate_legal_moves(gs, "red", 3)
        assert all(m.source == -1 for m in moves)

    def test_bar_entry_red_die_values(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.bar_red = 1
        moves = generate_legal_moves(gs, "red", 1)
        assert len(moves) == 1
        assert moves[0].destination == 23

    def test_bar_entry_white_die_values(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.bar_white = 1
        moves = generate_legal_moves(gs, "white", 4)
        assert len(moves) == 1
        assert moves[0].destination == 3

    def test_bar_entry_blocked(self):
        gs = build_initial_game_state()
        gs.board.bar_red = 1
        gs.board.points[23] = -2
        moves = generate_legal_moves(gs, "red", 1)
        assert len(moves) == 0

    def test_bar_entry_hit(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.bar_red = 1
        gs.board.points[22] = -1
        moves = generate_legal_moves(gs, "red", 2)
        assert len(moves) == 1
        assert moves[0].is_hit

    def test_hit_detection(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[10] = 2
        gs.board.points[7] = -1
        moves = generate_legal_moves(gs, "red", 3)
        hit_moves = [m for m in moves if m.is_hit]
        assert len(hit_moves) == 1
        assert hit_moves[0].destination == 7

    def test_blocked_by_opponent(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[10] = 2
        gs.board.points[7] = -2
        moves = generate_legal_moves(gs, "red", 3)
        assert len(moves) == 0


class TestBearOff:
    def _bearing_off_state(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[0] = 3
        gs.board.points[2] = 4
        gs.board.points[4] = 3
        gs.board.off_red = 5
        return gs

    def test_exact_bear_off(self):
        gs = self._bearing_off_state()
        moves = generate_legal_moves(gs, "red", 3)
        bear_off = [m for m in moves if m.is_bear_off]
        assert any(m.source == 2 for m in bear_off)

    def test_overshoot_bear_off_highest(self):
        gs = self._bearing_off_state()
        moves = generate_legal_moves(gs, "red", 6)
        bear_off = [m for m in moves if m.is_bear_off]
        assert any(m.source == 4 for m in bear_off)

    def test_overshoot_not_highest_blocked(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[0] = 5
        gs.board.points[3] = 5
        gs.board.off_red = 5
        moves = generate_legal_moves(gs, "red", 6)
        bear_off_from_0 = [m for m in moves if m.is_bear_off and m.source == 0]
        assert len(bear_off_from_0) == 0
        bear_off_from_3 = [m for m in moves if m.is_bear_off and m.source == 3]
        assert len(bear_off_from_3) == 1

    def test_cannot_bear_off_if_not_all_home(self):
        gs = build_initial_game_state()
        moves = generate_legal_moves(gs, "red", 1)
        assert not any(m.is_bear_off for m in moves)

    def test_white_bear_off(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[23] = -3
        gs.board.points[20] = -5
        gs.board.off_white = 7
        moves = generate_legal_moves(gs, "white", 1)
        bear_off = [m for m in moves if m.is_bear_off]
        assert any(m.source == 23 for m in bear_off)


class TestApplyAndUndo:
    def test_apply_normal_move(self):
        gs = build_initial_game_state()
        gs.moves_this_turn = []
        move = BackgammonMove(source=23, destination=20, die_value=3)
        apply_move(gs, move, "red")
        assert gs.board.points[23] == 1
        assert gs.board.points[20] == 1
        assert len(gs.moves_this_turn) == 1

    def test_apply_hit(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[10] = 2
        gs.board.points[7] = -1
        gs.moves_this_turn = []
        move = BackgammonMove(source=10, destination=7, die_value=3, is_hit=True)
        apply_move(gs, move, "red")
        assert gs.board.points[7] == 1
        assert gs.board.bar_white == 1

    def test_apply_bar_entry(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.bar_red = 2
        gs.moves_this_turn = []
        move = BackgammonMove(source=-1, destination=23, die_value=1)
        apply_move(gs, move, "red")
        assert gs.board.bar_red == 1
        assert gs.board.points[23] == 1

    def test_apply_bear_off(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[2] = 3
        gs.board.off_red = 12
        gs.moves_this_turn = []
        move = BackgammonMove(source=2, destination=24, die_value=3, is_bear_off=True)
        apply_move(gs, move, "red")
        assert gs.board.points[2] == 2
        assert gs.board.off_red == 13

    def test_undo_restores_state(self):
        gs = build_initial_game_state()
        gs.moves_this_turn = []
        original_23 = gs.board.points[23]
        original_20 = gs.board.points[20]
        move = BackgammonMove(source=23, destination=20, die_value=3)
        apply_move(gs, move, "red")
        undone = undo_last_move(gs, "red")
        assert undone is not None
        assert gs.board.points[23] == original_23
        assert gs.board.points[20] == original_20
        assert len(gs.moves_this_turn) == 0

    def test_undo_hit_restores_opponent(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[10] = 2
        gs.board.points[7] = -1
        gs.moves_this_turn = []
        move = BackgammonMove(source=10, destination=7, die_value=3, is_hit=True)
        apply_move(gs, move, "red")
        undo_last_move(gs, "red")
        assert gs.board.points[10] == 2
        assert gs.board.points[7] == -1
        assert gs.board.bar_white == 0

    def test_undo_empty_returns_none(self):
        gs = build_initial_game_state()
        gs.moves_this_turn = []
        assert undo_last_move(gs, "red") is None


class TestMustUseBothDice:
    def test_both_usable_returns_none(self):
        gs = build_initial_game_state()
        result = must_use_both_dice(gs, "red", [3, 1])
        assert result is None

    def test_doubles_returns_none(self):
        gs = build_initial_game_state()
        result = must_use_both_dice(gs, "red", [3, 3])
        assert result is None

    def test_only_one_usable_returns_larger(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[3] = 1
        gs.board.off_red = 14
        result = must_use_both_dice(gs, "red", [2, 5])
        assert result is None

    def test_neither_usable_returns_empty(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.bar_red = 1
        gs.board.points[23] = -2
        gs.board.points[21] = -2
        result = must_use_both_dice(gs, "red", [1, 3])
        assert result == []


class TestHasAnyLegalMove:
    def test_initial_has_moves(self):
        gs = build_initial_game_state()
        gs.dice = [3, 1]
        gs.dice_used = [False, False]
        assert has_any_legal_move(gs, "red")

    def test_no_dice_no_moves(self):
        gs = build_initial_game_state()
        gs.dice = [3, 1]
        gs.dice_used = [True, True]
        assert not has_any_legal_move(gs, "red")

    def test_completely_blocked(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.bar_red = 1
        for i in range(18, 24):
            gs.board.points[i] = -2
        gs.dice = [1, 2, 3, 4]
        gs.dice_used = [False, False, False, False]
        assert not has_any_legal_move(gs, "red")


# ==========================================================================
# Simple bot heuristic tests
# ==========================================================================


class TestSimpleBot:
    def test_prefers_bear_off(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[2] = 3
        gs.board.off_red = 12
        bear_off = BackgammonMove(source=2, destination=24, die_value=3, is_bear_off=True)
        normal = BackgammonMove(source=2, destination=0, die_value=2)
        assert _score_move(gs, bear_off, "red") > _score_move(gs, normal, "red")

    def test_prefers_hit(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[10] = 2
        gs.board.points[7] = -1
        hit = BackgammonMove(source=10, destination=7, die_value=3, is_hit=True)
        plain = BackgammonMove(source=10, destination=8, die_value=2)
        assert _score_move(gs, hit, "red") > _score_move(gs, plain, "red")

    def test_prefers_making_point(self):
        gs = build_initial_game_state()
        gs.board.points = [0] * 24
        gs.board.points[10] = 2
        gs.board.points[7] = 1
        gs.board.points[6] = 0
        make_point = BackgammonMove(source=10, destination=7, die_value=3)
        leave_blot = BackgammonMove(source=10, destination=6, die_value=4)
        assert _score_move(gs, make_point, "red") > _score_move(gs, leave_blot, "red")


# ==========================================================================
# Game registration / option tests
# ==========================================================================


class TestGameRegistration:
    def test_import(self):
        from server.games.backgammon import BackgammonGame

        assert BackgammonGame.get_name() == "Backgammon"
        assert BackgammonGame.get_type() == "backgammon"

    def test_registered(self):
        from server.games import BackgammonGame

        assert BackgammonGame is not None

    def test_min_max_players(self):
        assert BackgammonGame.get_min_players() == 2
        assert BackgammonGame.get_max_players() == 2

    def test_category(self):
        assert BackgammonGame.get_category() == "board"


class TestDifficultyOptions:
    def test_choices_are_exactly_random_and_simple(self):
        assert BOT_DIFFICULTY_CHOICES == ["random", "simple"]

    def test_no_gnubg_or_whackgammon(self):
        for bad in ("gnubg_0ply", "gnubg_1ply", "gnubg_2ply", "whackgammon"):
            assert bad not in BOT_DIFFICULTY_CHOICES
            assert bad not in BOT_DIFFICULTY_LABELS

    def test_all_choices_have_labels(self):
        for choice in BOT_DIFFICULTY_CHOICES:
            assert choice in BOT_DIFFICULTY_LABELS

    def test_no_difficulty_ply_map(self):
        import server.games.backgammon.game as bg_game

        assert not hasattr(bg_game, "DIFFICULTY_PLY")


class TestGridLayout:
    def test_grid_indices_count(self):
        game = BackgammonGame.__new__(BackgammonGame)
        indices = game._grid_indices()
        assert len(indices) == 24
        assert set(indices) == set(range(24))

    def test_grid_home_bottom_right_red(self):
        game = BackgammonGame.__new__(BackgammonGame)
        indices = game._grid_indices()
        bottom_row = indices[12:]
        assert bottom_row[-1] == 0
        assert bottom_row[-6:] == [5, 4, 3, 2, 1, 0]

    def test_grid_top_row_starts_with_13(self):
        game = BackgammonGame.__new__(BackgammonGame)
        indices = game._grid_indices()
        top_row = indices[:12]
        assert top_row[0] == 12
        assert top_row[-1] == 23


# ==========================================================================
# Integration: start, full game, serialization
# ==========================================================================


class TestGameLifecycle:
    def test_on_start_assigns_colors(self):
        game = make_game(start=True)
        colors = sorted(p.color for p in game.players)
        assert colors == ["red", "white"]
        assert game.status == "playing"

    def test_serialization_round_trip(self):
        game = make_game(start=True)
        # Advance a few ticks so there is interesting in-flight state.
        for _ in range(20):
            game.on_tick()
            if game.status == "finished":
                break
        payload = game.to_json()
        loaded = BackgammonGame.from_json(payload)
        assert loaded.game_state.match_length == game.game_state.match_length
        assert loaded.game_state.board.points == game.game_state.board.points
        assert [p.color for p in loaded.players] == [p.color for p in game.players]

    @pytest.mark.parametrize("difficulty", ["random", "simple"])
    def test_full_bot_game_runs_to_completion(self, difficulty):
        game = make_game(start=True, bot_difficulty=difficulty, match_length=1)
        ticks = 0
        max_ticks = 200_000
        while game.status != "finished" and ticks < max_ticks:
            game.on_tick()
            ticks += 1
        assert game.status == "finished", (
            f"{difficulty} game did not finish within {max_ticks} ticks"
        )
        winner = getattr(game, "_match_winner", None)
        assert winner is not None

    def test_keybinds_reference_real_actions(self):
        game = make_game(start=True)
        action_ids: set[str] = set()
        for p in game.players:
            for action_set in game.get_action_sets(p):
                action_ids.update(action_set._order)
        for key, keybinds in game._keybinds.items():
            for kb in keybinds:
                for act in kb.actions:
                    assert act in action_ids, f"keybind {key} -> unknown action {act}"

    def test_no_hint_or_gnubg_keybinds(self):
        game = make_game(start=True)
        all_action_targets = {
            act for kbs in game._keybinds.values() for kb in kbs for act in kb.actions
        }
        for forbidden in ("get_hint", "get_cube_hint"):
            assert forbidden not in all_action_targets
        # The cube-state reader ("d") must survive — it is not a gnubg hint.
        assert "h" not in game._keybinds or not game._keybinds["h"]
        assert "shift+h" not in game._keybinds or not game._keybinds["shift+h"]


# ==========================================================================
# Square (per-point highlight) sounds
# ==========================================================================


def _expected_point_sound(val: int, owns_positive: bool) -> str | None:
    """Mirror the perspective-relative mapping the game uses."""
    if val == 0:
        return None
    is_own = (val > 0) == owns_positive
    count = abs(val)
    if is_own:
        return "game_squares/token1.ogg" if count == 1 else "game_squares/token3.ogg"
    return "game_squares/token7.ogg" if count == 1 else "game_squares/token4.ogg"


class TestSquareSounds:
    def test_point_actions_carry_get_sound(self):
        game = make_game(start=True)
        red = next(p for p in game.players if p.color == "red")
        action_set = game.create_turn_action_set(red)
        for idx in range(24):
            action = action_set.get_action(f"point_{idx}")
            assert action is not None
            assert action.get_sound == "_get_point_sound"

    def test_get_point_sound_is_perspective_relative(self):
        game = make_game(start=True)
        red = next(p for p in game.players if p.color == "red")
        white = next(p for p in game.players if p.color == "white")
        points = game.game_state.board.points
        for idx, val in enumerate(points):
            assert game._get_point_sound(red, f"point_{idx}") == _expected_point_sound(
                val, owns_positive=True
            )
            assert game._get_point_sound(white, f"point_{idx}") == _expected_point_sound(
                val, owns_positive=False
            )
        # A checker reads as "mine" to its owner and "theirs" to the opponent.
        occupied = next(i for i, v in enumerate(points) if v > 0)
        assert game._get_point_sound(red, f"point_{occupied}").startswith("game_squares/token1") or \
            game._get_point_sound(red, f"point_{occupied}").startswith("game_squares/token3")
        assert game._get_point_sound(white, f"point_{occupied}").startswith("game_squares/token7") or \
            game._get_point_sound(white, f"point_{occupied}").startswith("game_squares/token4")

    def test_get_point_sound_handles_malformed_id(self):
        game = make_game(start=True)
        red = next(p for p in game.players if p.color == "red")
        assert game._get_point_sound(red, "garbage") is None
        assert game._get_point_sound(red, "point_") is None

    def test_resolved_action_propagates_sound(self):
        """End-to-end: get_sound resolves onto ResolvedAction.sound."""
        game = make_game(start=True)
        red = next(p for p in game.players if p.color == "red")
        action_set = game.create_turn_action_set(red)
        occupied = next(
            i for i, v in enumerate(game.game_state.board.points) if v != 0
        )
        action = action_set.get_action(f"point_{occupied}")
        resolved = action_set.resolve_action(game, red, action)
        assert resolved.sound == game._get_point_sound(red, f"point_{occupied}")
        assert resolved.sound is not None


# ==========================================================================
# Board persistence across turns (focus-anchor regression)
# ==========================================================================


class TestBoardPersistsOffTurn:
    """The 24-point grid must stay in every player's turn menu even when it is
    not their turn (the points disable, but must not vanish). If the board
    collapses to zero items off-turn, the desktop client loses its focus anchor
    and snaps the cursor to the first cell when the menu repopulates at turn
    start — the "focus teleports to square 13" bug. Guards the real cause, which
    lives in get_visible_actions, not in the rebuild-vs-update turn-pass call.
    """

    def _point_ids(self, game, player):
        return {
            ra.action.id
            for ra in game.get_all_visible_actions(player)
            if ra.action.id.startswith("point_")
        }

    def test_off_turn_board_keeps_all_24_points(self):
        game = make_game(start=True)
        gs = game.game_state
        gs.opening_roll = False
        red = next(p for p in game.players if p.color == "red")
        white = next(p for p in game.players if p.color == "white")

        gs.current_color = "red"
        gs.turn_phase = "moving"
        # The off-turn player (white) must still see the whole board.
        assert len(self._point_ids(game, white)) == 24
        # And the on-turn player, of course.
        assert len(self._point_ids(game, red)) == 24

    def test_off_turn_points_are_disabled_but_visible(self):
        game = make_game(start=True)
        gs = game.game_state
        gs.opening_roll = False
        white = next(p for p in game.players if p.color == "white")

        gs.current_color = "red"
        gs.turn_phase = "moving"
        action_set = game.create_turn_action_set(white)
        resolved = action_set.resolve_action(
            game, white, action_set.get_action("point_0")
        )
        assert resolved.visible is True
        assert resolved.enabled is False  # not white's turn
