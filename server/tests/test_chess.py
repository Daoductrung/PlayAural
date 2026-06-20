"""Tests for Chess."""

from pathlib import Path

from ..game_utils.actions import Visibility
from ..game_utils.grid_mixin import GridCursor
from ..games.chess.game import (
    ChessGame,
    ChessOptions,
    ChessPiece,
    COLOR_BLACK,
    COLOR_WHITE,
    MUSIC_PATH,
    SOUND_TURN,
    index_to_notation,
    notation_to_index,
)
from ..games.chess.bot import find_best_move
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(start: bool = False, *, bot_white: bool = False, bot_black: bool = False) -> ChessGame:
    game = ChessGame(options=ChessOptions())
    game.setup_keybinds()
    if bot_white:
        game.add_player("BotWhite", Bot("BotWhite", uuid="p1"))
    else:
        game.add_player("Alice", MockUser("Alice", uuid="p1"))
    if bot_black:
        game.add_player("BotBlack", Bot("BotBlack", uuid="p2"))
    else:
        game.add_player("Bob", MockUser("Bob", uuid="p2"))
    game.host = game.players[0].name
    if start:
        game.on_start()
        game.flush_menus()
    return game


def make_game_with_options(
    start: bool = False,
    *,
    bot_white: bool = False,
    bot_black: bool = False,
    **option_overrides,
) -> ChessGame:
    game = ChessGame(options=ChessOptions(**option_overrides))
    game.setup_keybinds()
    if bot_white:
        game.add_player("BotWhite", Bot("BotWhite", uuid="p1"))
    else:
        game.add_player("Alice", MockUser("Alice", uuid="p1"))
    if bot_black:
        game.add_player("BotBlack", Bot("BotBlack", uuid="p2"))
    else:
        game.add_player("Bob", MockUser("Bob", uuid="p2"))
    game.host = game.players[0].name
    if start:
        game.on_start()
        game.flush_menus()
    return game


def advance_until(game: ChessGame, condition, max_ticks: int = 500) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
        game.flush_menus()
    return condition()


def clear_board(game: ChessGame) -> None:
    game.board = [None] * 64


def place_piece(game: ChessGame, square: str, kind: str, color: str, has_moved: bool = False) -> None:
    index = notation_to_index(square)
    assert index is not None
    game.board[index] = ChessPiece(kind, color, has_moved=has_moved)


def select_square(game: ChessGame, player, square: str) -> None:
    index = notation_to_index(square)
    assert index is not None
    row, col = game.square_to_view(player, index)
    game.on_grid_select(player, row, col)


class TestRegistration:
    def test_game_registered(self) -> None:
        assert GameRegistry.get("chess") is ChessGame

    def test_class_methods(self) -> None:
        assert ChessGame.get_name() == "Chess"
        assert ChessGame.get_type() == "chess"
        assert ChessGame.get_category() == "board"
        assert ChessGame.get_min_players() == 2
        assert ChessGame.get_max_players() == 2
        assert ChessGame.get_supported_leaderboards() == ["wins", "rating", "games_played"]
        options = ChessOptions()
        assert options.time_control == "untimed"
        assert options.draw_handling == "automatic"
        assert options.allow_draw_offers is True
        assert options.allow_undo_requests is False
        assert ChessGame.relevant_preferences == ["brief_announcements"]

    def test_prestart_validation_rejects_invalid_option_values(self) -> None:
        game = ChessGame(options=ChessOptions(time_control="speedrun", draw_handling="maybe"))

        errors = game.prestart_validate()

        assert ("chess-error-invalid-time-control", {"control": "speedrun"}) in errors
        assert ("chess-error-invalid-draw-handling", {"mode": "maybe"}) in errors


def test_on_start_sets_colors_music_and_turn_sound() -> None:
    game = make_game(start=True)
    white = game.players[0]
    black = game.players[1]
    assert white.color == COLOR_WHITE
    assert black.color == COLOR_BLACK
    assert game.current_player == white
    assert game.current_color == COLOR_WHITE

    white_user = game.get_user(white)
    black_user = game.get_user(black)
    assert any(msg.type == "play_music" and msg.data["name"] == MUSIC_PATH for msg in white_user.messages)
    assert SOUND_TURN in white_user.get_sounds_played()
    assert SOUND_TURN not in black_user.get_sounds_played()
    assert white_user.menus["turn_menu"]["grid_enabled"] is True
    assert white_user.menus["turn_menu"]["grid_height"] == 8
    assert white_user.menus["turn_menu"]["grid_width"] == 8
    assert game.white_clock_ticks == 0
    assert game.black_clock_ticks == 0


def test_initialize_lobby_does_not_crash_before_board_setup() -> None:
    game = ChessGame(options=ChessOptions())
    user = MockUser("Alice", uuid="p1")
    game.initialize_lobby("Alice", user)
    game.flush_menus()

    assert game.status == "waiting"
    assert len(game.board) == 64
    assert "turn_menu" in user.menus


def test_basic_pawn_move_updates_board() -> None:
    game = make_game(start=True)
    white = game.players[0]
    select_square(game, white, "e2")
    select_square(game, white, "e4")

    assert game.board[notation_to_index("e2")] is None
    moved = game.board[notation_to_index("e4")]
    assert moved is not None
    assert moved.kind == "pawn"
    assert moved.color == COLOR_WHITE
    assert game.current_color == COLOR_BLACK
    assert game.move_history[-1].from_square == notation_to_index("e2")
    assert game.move_history[-1].to_square == notation_to_index("e4")


def test_typed_move_accepts_coordinate_and_san_notation() -> None:
    game = make_game(start=True)
    white = game.players[0]
    black = game.players[1]

    game.execute_action(white, "type_move", "e2e4")
    game.flush_menus()
    game.execute_action(black, "type_move", "Nf6")
    game.flush_menus()

    assert game.board[notation_to_index("e4")] is not None
    knight = game.board[notation_to_index("f6")]
    assert knight is not None
    assert knight.kind == "knight"
    assert knight.color == COLOR_BLACK
    assert game._fullmove_count() == 1
    assert len(game.move_history) == 2


def test_move_count_uses_completed_full_moves_not_half_moves() -> None:
    game = make_game(start=True)
    white = game.players[0]
    black = game.players[1]

    game.execute_action(white, "type_move", "e4")
    game.flush_menus()
    assert game._fullmove_count() == 0

    game.execute_action(black, "type_move", "e5")
    game.flush_menus()
    assert game._fullmove_count() == 1

    status_lines = game._status_lines("en")
    assert "Completed full moves: 1. Half-moves played: 2." in status_lines


def test_typed_move_accepts_castling_and_promotion() -> None:
    game = make_game(start=True)
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "h1", "rook", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    game.current_player = white
    game.current_color = COLOR_WHITE
    game.castle_white_kingside = True
    game.castle_white_queenside = False
    game.castle_black_kingside = False
    game.castle_black_queenside = False

    game.execute_action(white, "type_move", "O-O")
    game.flush_menus()

    assert game.board[notation_to_index("g1")].kind == "king"
    assert game.board[notation_to_index("f1")].kind == "rook"

    game = make_game(start=True)
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "h8", "king", COLOR_BLACK)
    place_piece(game, "a7", "pawn", COLOR_WHITE, has_moved=True)
    game.current_player = white
    game.current_color = COLOR_WHITE

    game.execute_action(white, "type_move", "a8=q")
    game.flush_menus()

    promoted = game.board[notation_to_index("a8")]
    assert promoted is not None
    assert promoted.kind == "queen"
    assert game.promotion_pending is False


def test_typed_move_invalid_input_speaks_and_reopens_editbox() -> None:
    game = make_game(start=True)
    white = game.players[0]
    user = game.get_user(white)
    user.clear_messages()

    game.execute_action(white, "type_move", "not a move")
    game.flush_menus()

    assert "not a move" in user.get_last_spoken()
    assert "action_input_editbox" in user.editboxes


def test_brief_announcements_shortens_move_broadcast_per_listener() -> None:
    game = make_game(start=True)
    white = game.players[0]
    black = game.players[1]
    white_user = game.get_user(white)
    black_user = game.get_user(black)
    black_user.preferences.brief_announcements = True
    white_user.clear_messages()
    black_user.clear_messages()

    game.execute_action(white, "type_move", "e2e4")
    game.flush_menus()

    assert "You move your pawn from e2 to e4." in white_user.get_spoken_messages()
    assert "Alice e2 e4." in black_user.get_spoken_messages()


def test_castling_kingside_moves_king_and_rook() -> None:
    game = make_game(start=True)
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "h1", "rook", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    game.castle_white_kingside = True
    game.castle_white_queenside = False
    game.castle_black_kingside = False
    game.castle_black_queenside = False
    game.current_player = white
    game.current_color = COLOR_WHITE
    game.selected_square.clear()

    select_square(game, white, "e1")
    select_square(game, white, "g1")

    king = game.board[notation_to_index("g1")]
    rook = game.board[notation_to_index("f1")]
    assert king is not None and king.kind == "king"
    assert rook is not None and rook.kind == "rook"
    assert game.board[notation_to_index("e1")] is None
    assert game.board[notation_to_index("h1")] is None


def test_castling_queenside_moves_king_and_rook() -> None:
    game = make_game(start=True)
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "a1", "rook", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    game.castle_white_kingside = False
    game.castle_white_queenside = True
    game.castle_black_kingside = False
    game.castle_black_queenside = False
    game.current_player = white
    game.current_color = COLOR_WHITE
    game.selected_square.clear()

    select_square(game, white, "e1")
    select_square(game, white, "c1")

    king = game.board[notation_to_index("c1")]
    rook = game.board[notation_to_index("d1")]
    assert king is not None and king.kind == "king"
    assert rook is not None and rook.kind == "rook"
    assert game.board[notation_to_index("e1")] is None
    assert game.board[notation_to_index("a1")] is None


def test_en_passant_captures_pawn() -> None:
    game = make_game(start=True)
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "h8", "king", COLOR_BLACK)
    place_piece(game, "e5", "pawn", COLOR_WHITE, has_moved=True)
    place_piece(game, "d5", "pawn", COLOR_BLACK, has_moved=True)
    game.en_passant_target = notation_to_index("d6")
    game.current_player = white
    game.current_color = COLOR_WHITE

    select_square(game, white, "e5")
    select_square(game, white, "d6")

    assert game.board[notation_to_index("d5")] is None
    moved = game.board[notation_to_index("d6")]
    assert moved is not None and moved.kind == "pawn" and moved.color == COLOR_WHITE
    assert game.move_history[-1].special == "en_passant"


def test_en_passant_target_is_set_then_cleared() -> None:
    game = make_game(start=True)
    white = game.players[0]
    black = game.players[1]

    select_square(game, white, "e2")
    select_square(game, white, "e4")
    assert game.en_passant_target == notation_to_index("e3")

    select_square(game, black, "a7")
    select_square(game, black, "a6")
    assert game.en_passant_target == -1


def test_promotion_requires_choice_then_records_result() -> None:
    game = make_game(start=True)
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "h8", "king", COLOR_BLACK)
    place_piece(game, "a7", "pawn", COLOR_WHITE, has_moved=True)
    game.current_player = white
    game.current_color = COLOR_WHITE

    select_square(game, white, "a7")
    select_square(game, white, "a8")

    assert game.promotion_pending is True
    game._action_promote(white, "promote_queen")

    promoted = game.board[notation_to_index("a8")]
    assert promoted is not None
    assert promoted.kind == "queen"
    assert promoted.color == COLOR_WHITE
    assert game.promotion_pending is False
    assert game.move_history[-1].promotion == "queen"


def test_fools_mate_checkmates_white() -> None:
    game = make_game(start=True)
    white = game.players[0]
    black = game.players[1]
    white_user = game.get_user(white)
    black_user = game.get_user(black)

    select_square(game, white, "f2")
    select_square(game, white, "f3")
    select_square(game, black, "e7")
    select_square(game, black, "e5")
    select_square(game, white, "g2")
    select_square(game, white, "g4")
    select_square(game, black, "d8")
    select_square(game, black, "h4")

    assert game.status == "finished"
    assert game.winner_color == COLOR_BLACK
    assert "game_pig/wingame.ogg" not in white_user.get_sounds_played()
    assert "game_pig/wingame.ogg" not in black_user.get_sounds_played()
    assert "game_pig/lose.ogg" not in white_user.get_sounds_played()
    assert "game_pig/lose.ogg" not in black_user.get_sounds_played()


def test_stalemate_detection() -> None:
    game = make_game(start=True)
    clear_board(game)
    place_piece(game, "f7", "king", COLOR_WHITE)
    place_piece(game, "g6", "queen", COLOR_WHITE)
    place_piece(game, "h8", "king", COLOR_BLACK)
    game.current_color = COLOR_BLACK

    assert game.is_stalemate(COLOR_BLACK) is True
    assert game.is_in_check(COLOR_BLACK) is False


def test_insufficient_material_detection() -> None:
    game = make_game(start=True)
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    assert game._is_insufficient_material() is True


def test_same_colored_bishops_same_side_are_insufficient() -> None:
    game = make_game(start=True)
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    place_piece(game, "c1", "bishop", COLOR_WHITE)
    place_piece(game, "e3", "bishop", COLOR_WHITE)

    assert game._is_insufficient_material() is True


def test_opposite_colored_bishop_pair_is_not_insufficient() -> None:
    game = make_game(start=True)
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    place_piece(game, "c1", "bishop", COLOR_WHITE)
    place_piece(game, "f1", "bishop", COLOR_WHITE)

    assert game._is_insufficient_material() is False


def test_position_hash_ignores_non_castling_piece_move_history() -> None:
    game = make_game(start=True)
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    place_piece(game, "g1", "knight", COLOR_WHITE, has_moved=False)

    original_hash = game._get_position_hash()
    place_piece(game, "g1", "knight", COLOR_WHITE, has_moved=True)

    assert game._get_position_hash() == original_hash


def test_web_standard_actions_are_ordered_and_visible_once() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    user.client_type = "web"

    action_set = game.create_standard_action_set(player)
    order = action_set._order
    assert order.index("read_board") < order.index("check_status")
    assert order.index("check_status") < order.index("flip_board")
    assert order.index("flip_board") < order.index("check_clock")
    assert order.index("check_clock") < order.index("whose_turn")
    assert order.index("whose_turn") < order.index("whos_at_table")
    assert order[-2:] == ["whose_turn", "whos_at_table"]

    game.refresh_menus(player)
    game.flush_menus()
    visible_ids = [item.id for item in user.menus["turn_menu"]["items"] if getattr(item, "id", None)]
    for action_id in ("read_board", "check_status", "flip_board", "check_clock"):
        assert action_id in visible_ids
        assert visible_ids.count(action_id) == 1


def test_type_move_is_standard_action_not_desktop_turn_button() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)

    visible_ids = [item.id for item in user.menus["turn_menu"]["items"] if getattr(item, "id", None)]
    assert "type_move" not in visible_ids

    game._action_show_actions_menu(player, "show_actions")

    action_ids = [item.id for item in user.menus["actions_menu"]["items"] if getattr(item, "id", None)]
    assert "type_move" in action_ids


def test_type_move_is_touch_visible_in_standard_utility_order() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    user.client_type = "web"

    game.refresh_menus(player)
    game.flush_menus()

    visible_ids = [item.id for item in user.menus["turn_menu"]["items"] if getattr(item, "id", None)]
    assert "type_move" in visible_ids
    assert visible_ids.index("type_move") < visible_ids.index("read_board")


def test_type_move_stays_touch_visible_when_not_players_turn() -> None:
    game = make_game(start=True)
    white = game.players[0]
    black = game.players[1]
    white_user = game.get_user(white)
    black_user = game.get_user(black)
    white_user.client_type = "web"
    black_user.client_type = "web"

    game.refresh_menus(black)
    game.flush_menus()

    black_ids = [
        item.id
        for item in black_user.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert "type_move" in black_ids
    assert game._is_type_move_enabled(black) == "action-not-your-turn"

    game.execute_action(white, "type_move", "e2e4")
    game.flush_menus()

    white_ids = [
        item.id
        for item in white_user.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert "type_move" in white_ids
    assert game._is_type_move_enabled(white) == "action-not-your-turn"


def test_type_move_touch_input_returns_focus_to_type_move() -> None:
    game = make_game(start=True)
    white = game.players[0]
    user = game.get_user(white)
    user.client_type = "web"

    game.refresh_menus(white)
    game.flush_menus()
    game.handle_event(
        white,
        {"type": "menu", "menu_id": "turn_menu", "selection_id": "type_move"},
    )
    assert "action_input_editbox" in user.editboxes

    game.handle_event(
        white,
        {"type": "editbox", "input_id": "action_input_editbox", "text": "e2e4"},
    )
    game.flush_menus()

    assert game.board[notation_to_index("e4")] is not None
    assert user.menus["turn_menu"]["selection_id"] == "type_move"


def test_desktop_hides_web_only_utility_actions() -> None:
    game = make_game_with_options(
        start=True,
        time_control="blitz_3_0",
        draw_handling="claim_required",
        allow_draw_offers=True,
        allow_undo_requests=True,
    )
    white = game.players[0]

    game.halfmove_clock = 100

    assert game._is_check_clock_hidden(white) == Visibility.HIDDEN
    assert game._is_offer_draw_hidden(white) == Visibility.HIDDEN
    assert game._is_request_undo_hidden(white) == Visibility.HIDDEN
    assert game._is_claim_draw_hidden(white) == Visibility.HIDDEN


def test_flip_board_hidden_from_spectators_and_keybind_matches() -> None:
    game = make_game(start=True)
    player = game.players[0]
    player.is_spectator = True

    assert game._is_flip_board_hidden(player) == Visibility.HIDDEN
    assert all(binding.include_spectators is False for binding in game._keybinds["f"])


def test_master_bot_finishes_forced_mate_position() -> None:
    game = ChessGame(options=ChessOptions())
    game.setup_keybinds()
    game.add_player("BotWhite", Bot("BotWhite", uuid="p1"))
    game.add_player("Bob", MockUser("Bob", uuid="p2"))
    game.host = game.players[0].name
    game.on_start()
    game.flush_menus()
    clear_board(game)
    white = game.players[0]
    black = game.players[1]
    place_piece(game, "f6", "king", COLOR_WHITE)
    place_piece(game, "g6", "queen", COLOR_WHITE)
    place_piece(game, "h8", "king", COLOR_BLACK)
    white.color = COLOR_WHITE
    black.color = COLOR_BLACK
    game.set_turn_players([white, black])
    game.current_player = white
    game.current_color = COLOR_WHITE
    game.selected_square.clear()
    game.bot_move_targets.clear()
    game.board_flipped[white.id] = False
    game.board_flipped[black.id] = True
    game.position_history = [game._get_position_hash()]
    game.refresh_menus()
    game.flush_menus()

    move = find_best_move(game, white, time_limit=0.2, node_limit=20_000, max_depth=2)
    assert move is not None
    game._execute_move_full(white, move[0], move[1])

    assert game.status == "finished"
    assert game.winner_color == COLOR_WHITE


def test_bot_returns_action_in_simple_position() -> None:
    game = ChessGame(options=ChessOptions())
    game.setup_keybinds()
    game.add_player("BotWhite", Bot("BotWhite", uuid="p1"))
    game.add_player("Bob", MockUser("Bob", uuid="p2"))
    game.host = game.players[0].name
    game.on_start()
    game.flush_menus()
    clear_board(game)
    white = game.players[0]
    black = game.players[1]
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    place_piece(game, "d1", "queen", COLOR_WHITE)
    place_piece(game, "d8", "queen", COLOR_BLACK)
    game.current_player = white
    game.current_color = COLOR_WHITE
    game.position_history = [game._get_position_hash()]

    move = find_best_move(game, white, time_limit=0.1, node_limit=20_000, max_depth=2)
    assert move is not None
    assert game._is_legal_move(move[0], move[1], white.color)[0] is True


def test_time_control_initializes_and_increment_applies() -> None:
    game = make_game_with_options(start=True, time_control="blitz_3_2")
    white = game.players[0]

    assert game.white_clock_ticks == 180 * 20
    assert game.black_clock_ticks == 180 * 20

    for _ in range(10):
        game.on_tick()
        game.flush_menus()

    select_square(game, white, "e2")
    select_square(game, white, "e4")

    assert game.white_clock_ticks == (180 * 20) - 10 + (2 * 20)
    assert game.current_color == COLOR_BLACK


def test_check_clock_speaks_directly_without_opening_state_box() -> None:
    game = make_game_with_options(start=True, time_control="blitz_3_0")
    white = game.players[0]
    user = game.get_user(white)
    user.clear_messages()

    game._action_check_clock(white, "check_clock")

    assert user.get_last_spoken() is not None
    assert all(message.type != "show_menu" for message in user.messages)


def test_timeout_ends_game_with_opponent_win() -> None:
    game = make_game_with_options(start=True, time_control="bullet_1_0")
    game.white_clock_ticks = 1
    game.black_clock_ticks = 100

    game.on_tick()
    game.flush_menus()

    assert game.status == "finished"
    assert game.winner_color == COLOR_BLACK


def test_timeout_with_insufficient_material_is_draw() -> None:
    game = make_game_with_options(start=True, time_control="bullet_1_0")
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    game.current_player = game.players[0]
    game.current_color = COLOR_WHITE
    game.white_clock_ticks = 1
    game.black_clock_ticks = 100

    game.on_tick()
    game.flush_menus()

    assert game.status == "finished"
    assert game.winner_color == ""
    assert game.draw_reason == "timeout_insufficient_material"


def test_claim_required_draw_can_be_claimed() -> None:
    game = make_game_with_options(start=True, draw_handling="claim_required")
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    game.current_player = white
    game.current_color = COLOR_WHITE
    game.halfmove_clock = 100
    game.position_history = [game._get_position_hash()]

    assert game._is_claim_draw_enabled(white) is None

    game._action_claim_draw(white, "claim_draw")

    assert game.status == "finished"
    assert game.draw_reason == "fifty_move_rule"


def test_claim_required_threefold_can_be_claimed() -> None:
    game = make_game_with_options(start=True, draw_handling="claim_required")
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    current_hash = game._get_position_hash()
    game.position_history = [current_hash, current_hash, current_hash]
    game.current_player = white
    game.current_color = COLOR_WHITE

    assert game._is_claim_draw_enabled(white) is None

    game._action_claim_draw(white, "claim_draw")

    assert game.status == "finished"
    assert game.draw_reason == "threefold_repetition"


def test_automatic_draw_handling_hides_claim_action() -> None:
    game = make_game_with_options(start=True, draw_handling="automatic")
    white = game.players[0]
    game.halfmove_clock = 100

    assert game._is_claim_draw_enabled(white) == "action-not-available"


def test_automatic_fifty_move_draw_triggers_on_move() -> None:
    game = make_game_with_options(start=True, draw_handling="automatic")
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    game.current_player = white
    game.current_color = COLOR_WHITE
    game.halfmove_clock = 99
    game.position_history = [game._get_position_hash()]

    select_square(game, white, "e1")
    select_square(game, white, "e2")

    assert game.status == "finished"
    assert game.draw_reason == "fifty_move_rule"


def test_mandatory_seventy_five_move_draw_ignores_claim_required_option() -> None:
    game = make_game_with_options(start=True, draw_handling="claim_required")
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    game.current_player = white
    game.current_color = COLOR_WHITE
    game.halfmove_clock = 149
    game.position_history = [game._get_position_hash()]

    select_square(game, white, "e1")
    select_square(game, white, "e2")

    assert game.status == "finished"
    assert game.draw_reason == "seventy_five_move_rule"


def test_mandatory_fivefold_repetition_ignores_claim_required_option() -> None:
    game = make_game_with_options(start=True, draw_handling="claim_required")
    white = game.players[0]
    clear_board(game)
    place_piece(game, "e1", "king", COLOR_WHITE)
    place_piece(game, "e8", "king", COLOR_BLACK)
    game.current_player = white
    game.current_color = COLOR_WHITE

    from_sq = notation_to_index("e1")
    to_sq = notation_to_index("e2")
    saved = game.save_position()
    game._apply_move_core(from_sq, to_sq)
    game.current_color = COLOR_BLACK
    repeated_hash = game._get_position_hash()
    game.restore_position(saved)
    game.position_history = [repeated_hash] * 4

    select_square(game, white, "e1")
    select_square(game, white, "e2")

    assert game.status == "finished"
    assert game.draw_reason == "fivefold_repetition"


def test_draw_offer_can_be_accepted() -> None:
    game = make_game_with_options(start=True, allow_draw_offers=True)
    white = game.players[0]
    black = game.players[1]

    select_square(game, white, "g1")
    select_square(game, white, "f3")
    select_square(game, black, "g8")
    select_square(game, black, "f6")

    game._action_offer_draw(white, "offer_draw")
    assert game.draw_offer_from == white.id
    assert game._is_draw_response_enabled(black) is None

    game._action_accept_draw(black, "accept_draw")

    assert game.status == "finished"
    assert game.draw_reason == "agreement"


def test_draw_offer_can_be_declined() -> None:
    game = make_game_with_options(start=True, allow_draw_offers=True)
    white = game.players[0]
    black = game.players[1]

    select_square(game, white, "g1")
    select_square(game, white, "f3")
    select_square(game, black, "g8")
    select_square(game, black, "f6")

    game._action_offer_draw(white, "offer_draw")
    game._action_decline_draw(black, "decline_draw")

    assert game.status == "playing"
    assert game.draw_offer_from == ""


def test_draw_offer_requires_both_players_to_have_moved() -> None:
    game = make_game_with_options(start=True, allow_draw_offers=True)
    white = game.players[0]
    black = game.players[1]

    assert game._is_offer_draw_enabled(white) == "chess-draw-offer-too-early"

    select_square(game, white, "g1")
    select_square(game, white, "f3")
    assert game._is_offer_draw_enabled(black) == "chess-draw-offer-too-early"

    select_square(game, black, "g8")
    select_square(game, black, "f6")
    assert game._is_offer_draw_enabled(white) is None


def test_undo_request_restores_previous_position() -> None:
    game = make_game_with_options(start=True, allow_undo_requests=True)
    white = game.players[0]
    black = game.players[1]

    select_square(game, white, "e2")
    select_square(game, white, "e4")

    assert game.board[notation_to_index("e4")] is not None
    assert game.current_color == COLOR_BLACK

    assert game._is_request_undo_enabled(white) is None
    assert game._is_request_undo_enabled(black) == "action-not-available"

    game._action_request_undo(white, "request_undo")
    assert game.undo_request_from == white.id

    game._action_accept_undo(black, "accept_undo")

    assert game.board[notation_to_index("e2")] is not None
    assert game.board[notation_to_index("e4")] is None
    assert game.current_color == COLOR_WHITE
    assert not game.move_history


def test_undo_request_visible_to_last_mover_after_their_move() -> None:
    game = make_game_with_options(start=True, allow_undo_requests=True)
    white = game.players[0]
    black = game.players[1]
    white_user = game.get_user(white)
    black_user = game.get_user(black)
    white_user.client_type = "web"
    black_user.client_type = "web"

    select_square(game, white, "e2")
    select_square(game, white, "e4")
    game.flush_menus()

    white_ids = [
        item.id
        for item in white_user.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    black_ids = [
        item.id
        for item in black_user.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert "request_undo" in white_ids
    assert "request_undo" not in black_ids


def test_undo_history_keeps_only_latest_snapshot() -> None:
    game = make_game_with_options(start=True, allow_undo_requests=True)
    white = game.players[0]
    black = game.players[1]

    game.execute_action(white, "type_move", "e2e4")
    assert len(game.undo_history) == 1
    game.execute_action(black, "type_move", "e7e5")
    assert len(game.undo_history) == 1
    game.execute_action(white, "type_move", "g1f3")
    assert len(game.undo_history) == 1

    game._action_request_undo(white, "request_undo")
    game._action_accept_undo(black, "accept_undo")

    assert game.board[notation_to_index("g1")] is not None
    assert game.board[notation_to_index("f3")] is None
    assert game.board[notation_to_index("e4")] is not None
    assert game.board[notation_to_index("e5")] is not None
    assert len(game.move_history) == 2
    assert game.undo_history == []


def test_accept_undo_clears_legacy_extra_snapshots() -> None:
    game = make_game_with_options(start=True, allow_undo_requests=True)
    white = game.players[0]
    black = game.players[1]

    game.execute_action(white, "type_move", "e2e4")
    game.execute_action(black, "type_move", "e7e5")
    latest_snapshot = game.undo_history[-1]
    game.undo_history = [game._make_undo_snapshot(), latest_snapshot]

    game._action_request_undo(black, "request_undo")
    game._action_accept_undo(white, "accept_undo")

    assert game.undo_history == []
    assert game.board[notation_to_index("e7")] is not None
    assert game.board[notation_to_index("e5")] is None


def test_undo_and_pending_input_state_clear_when_game_finishes() -> None:
    game = make_game_with_options(start=True, allow_undo_requests=True)
    white = game.players[0]

    game.execute_action(white, "type_move", "e2e4")
    game.draw_offer_from = white.id
    game.undo_request_from = white.id
    game.pending_undo_snapshot = game._make_undo_snapshot()
    game._pending_actions[white.id] = "type_move"
    game._pending_action_return_focus[white.id] = "type_move"
    game._chess_bot_jobs[white.id] = object()

    game.finish_game(show_end_screen=False)

    assert game.status == "finished"
    assert game.draw_offer_from == ""
    assert game.undo_request_from == ""
    assert game.undo_history == []
    assert game.pending_undo_snapshot is None
    assert game._pending_actions == {}
    assert game._pending_action_return_focus == {}
    assert game._chess_bot_jobs == {}


def test_undo_accept_shortcut_does_not_accept_draw() -> None:
    game = make_game_with_options(
        start=True,
        allow_draw_offers=True,
        allow_undo_requests=True,
    )
    white = game.players[0]
    black = game.players[1]

    select_square(game, white, "e2")
    select_square(game, white, "e4")
    game._action_request_undo(white, "request_undo")

    assert game.undo_request_from == white.id
    assert game.draw_offer_from == ""
    assert game._is_draw_response_enabled(black) == "action-not-available"
    assert game._is_undo_response_enabled(black) is None

    game.handle_event(black, {"type": "keybind", "key": "y"})
    game.flush_menus()

    assert game.status == "playing"
    assert game.draw_reason == ""
    assert game.undo_request_from == ""
    assert game.board[notation_to_index("e2")] is not None
    assert game.board[notation_to_index("e4")] is None
    assert game.current_color == COLOR_WHITE
    assert not game.move_history


def test_undo_request_cannot_be_answered_by_draw_actions_directly() -> None:
    game = make_game_with_options(
        start=True,
        allow_draw_offers=True,
        allow_undo_requests=True,
    )
    white = game.players[0]
    black = game.players[1]

    select_square(game, white, "e2")
    select_square(game, white, "e4")
    game._action_request_undo(white, "request_undo")

    game.execute_action(black, "accept_draw")
    game.flush_menus()

    assert game.status == "playing"
    assert game.draw_reason == ""
    assert game.undo_request_from == white.id
    assert game.board[notation_to_index("e4")] is not None


def test_draw_offer_cannot_be_answered_by_undo_actions() -> None:
    game = make_game_with_options(
        start=True,
        allow_draw_offers=True,
        allow_undo_requests=True,
    )
    white = game.players[0]
    black = game.players[1]

    select_square(game, white, "g1")
    select_square(game, white, "f3")
    select_square(game, black, "g8")
    select_square(game, black, "f6")
    game._action_offer_draw(white, "offer_draw")

    assert game.draw_offer_from == white.id
    assert game._is_draw_response_enabled(black) is None
    assert game._is_undo_response_enabled(black) == "action-not-available"

    game.execute_action(black, "accept_undo")
    game.flush_menus()

    assert game.status == "playing"
    assert game.draw_offer_from == white.id
    assert game.draw_reason == ""


def test_undo_request_can_be_declined() -> None:
    game = make_game_with_options(start=True, allow_undo_requests=True)
    white = game.players[0]
    black = game.players[1]

    select_square(game, white, "e2")
    select_square(game, white, "e4")
    game._action_request_undo(white, "request_undo")
    game._action_decline_undo(black, "decline_undo")

    assert game.status == "playing"
    assert game.undo_request_from == ""
    assert game.board[notation_to_index("e4")] is not None


def test_chess_game_state_round_trips_with_grid_cursor() -> None:
    game = make_game_with_options(
        start=True,
        time_control="blitz_3_2",
        draw_handling="claim_required",
        allow_draw_offers=True,
        allow_undo_requests=True,
    )
    white = game.players[0]

    select_square(game, white, "e2")
    select_square(game, white, "e4")
    game.grid_cursors[white.id] = GridCursor(row=3, col=4)
    game.board_flipped[white.id] = True

    payload = game.to_json()
    restored = ChessGame.from_json(payload)

    assert restored.grid_cursors[white.id].row == 3
    assert restored.grid_cursors[white.id].col == 4
    assert restored.board[notation_to_index("e4")] is not None
    assert restored.board[notation_to_index("e2")] is None
    assert restored.move_history[-1].from_square == notation_to_index("e2")
    assert restored.move_history[-1].to_square == notation_to_index("e4")
    assert restored.board_flipped[white.id] is True


def test_custom_keybinds_do_not_use_reserved_keys() -> None:
    game = make_game()
    reserved = {
        "enter",
        "escape",
        "b",
        "shift+b",
        "f3",
        "t",
        "s",
        "shift+s",
        "ctrl+m",
        "ctrl+q",
        "ctrl+u",
        "ctrl+s",
        "ctrl+r",
        "ctrl+i",
        "ctrl+f1",
    }
    custom_keys = {"v", "c", "f", "shift+t", "shift+d", "shift+u", "shift+c", "y", "n", "m"}
    assert custom_keys.isdisjoint(reserved)
    assert all(key in game._keybinds for key in custom_keys)
