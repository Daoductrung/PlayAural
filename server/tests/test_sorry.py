"""Tests for Sorry."""

from pathlib import Path

from ..games.registry import GameRegistry
from ..games.sorry.game import SorryGame, SorryOptions
from ..games.sorry.moves import apply_move, generate_legal_moves, generate_split_options_for_pair
from ..games.sorry.rules import RULES_PROFILES
from ..games.sorry.state import build_default_draw_pile, build_initial_game_state
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(
    *,
    player_count: int = 2,
    start: bool = False,
    bot_second: bool = False,
    web_first: bool = False,
    names: list[str] | None = None,
    locales: list[str] | None = None,
    **option_overrides,
) -> SorryGame:
    game = SorryGame(options=SorryOptions(**option_overrides))
    game.setup_keybinds()
    for index in range(player_count):
        if bot_second and index == 1:
            user = Bot("Bot", uuid=f"p{index + 1}")
            game.add_player("Bot", user)
        else:
            name = names[index] if names and index < len(names) else f"Player{index + 1}"
            locale = locales[index] if locales and index < len(locales) else "en"
            user = MockUser(name, locale=locale, uuid=f"p{index + 1}")
            if web_first and index == 0:
                user.client_type = "web"
            game.add_player(name, user)
    game.host = names[0] if names else "Player1"
    if start:
        game.on_start()
    return game


def advance_until(game: SorryGame, condition, max_ticks: int = 600) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


class TestRegistration:
    def test_game_registered(self) -> None:
        assert GameRegistry.get("sorry") is SorryGame

    def test_class_methods_and_defaults(self) -> None:
        assert SorryGame.get_name() == "Sorry!"
        assert SorryGame.get_type() == "sorry"
        assert SorryGame.get_category() == "category-board-games"
        assert SorryGame.get_min_players() == 2
        assert SorryGame.get_max_players() == 4
        assert SorryGame.get_supported_leaderboards() == ["wins", "rating", "games_played"]

        options = SorryOptions()
        assert options.rules_profile == "classic_00390"
        assert options.auto_apply_single_move is True
        assert options.faster_setup_one_pawn_out is False


def test_on_start_initializes_state_and_music() -> None:
    game = make_game(start=True)

    assert [player.color for player in game.get_active_players()] == ["red", "blue"]
    assert game.current_player == game.players[0]
    assert game.game_state.turn_phase == "draw"

    user = game.get_user(game.players[0])
    assert user is not None
    assert any(
        message.type == "play_music" and message.data["name"] == "game_pig/mus.ogg"
        for message in user.messages
    )


def test_default_deck_matches_standard_45_card_composition() -> None:
    deck = build_default_draw_pile()

    assert len(deck) == 45
    assert deck.count("1") == 5
    for face in ("2", "3", "4", "5", "7", "8", "10", "11", "12", "sorry"):
        assert deck.count(face) == 4


def test_classic_start_move_requires_one_or_two() -> None:
    state = build_initial_game_state(["p1", "p2"])
    player_state = state.player_states["p1"]
    rules = RULES_PROFILES["classic_00390"]

    assert generate_legal_moves(state, player_state, "1", rules)
    assert generate_legal_moves(state, player_state, "2", rules)
    assert not generate_legal_moves(state, player_state, "3", rules)


def test_a5065_sorry_card_has_forward_fallback() -> None:
    state = build_initial_game_state(["p1", "p2"], pawns_per_player=3)
    player_state = state.player_states["p1"]
    rules = RULES_PROFILES["a5065_core"]
    player_state.pawns[0].zone = "track"
    player_state.pawns[0].track_position = player_state.start_track

    moves = generate_legal_moves(state, player_state, "sorry", rules)
    assert any(move.move_type == "sorry_fallback_forward" for move in moves)


def test_slide_captures_all_opponents_on_slide() -> None:
    state = build_initial_game_state(["p1", "p2", "p3"])
    red = state.player_states["p1"]
    blue = state.player_states["p2"]
    green = state.player_states["p3"]
    rules = RULES_PROFILES["classic_00390"]

    red.pawns[0].zone = "track"
    red.pawns[0].track_position = 15
    blue.pawns[0].zone = "track"
    blue.pawns[0].track_position = 17
    green.pawns[0].zone = "track"
    green.pawns[0].track_position = 19

    move = next(move for move in generate_legal_moves(state, red, "1", rules) if move.pawn_index == 1)
    captures = apply_move(state, red, move, rules)

    assert red.pawns[0].track_position == 19
    assert blue.pawns[0].zone == "start"
    assert green.pawns[0].zone == "start"
    assert len(captures) == 2


def test_swap_can_trigger_slide() -> None:
    state = build_initial_game_state(["p1", "p2"])
    red = state.player_states["p1"]
    blue = state.player_states["p2"]
    rules = RULES_PROFILES["classic_00390"]

    red.pawns[0].zone = "track"
    red.pawns[0].track_position = 10
    blue.pawns[0].zone = "track"
    blue.pawns[0].track_position = 16

    move = next(move for move in generate_legal_moves(state, red, "11", rules) if move.move_type == "swap")
    apply_move(state, red, move, rules)

    assert red.pawns[0].track_position == 19
    assert blue.pawns[0].track_position == 10


def test_swap_only_checks_slide_for_active_pawn() -> None:
    state = build_initial_game_state(["p1", "p2"])
    red = state.player_states["p1"]
    blue = state.player_states["p2"]
    rules = RULES_PROFILES["classic_00390"]

    red.pawns[0].zone = "track"
    red.pawns[0].track_position = 1
    blue.pawns[0].zone = "track"
    blue.pawns[0].track_position = 10

    move = next(
        move
        for move in generate_legal_moves(state, red, "11", rules)
        if move.move_type == "swap" and move.target_player_id == "p2" and move.target_pawn_index == 1
    )
    apply_move(state, red, move, rules)

    assert red.pawns[0].track_position == 10
    assert blue.pawns[0].track_position == 1


def test_split_seven_moves_two_pawns() -> None:
    state = build_initial_game_state(["p1", "p2"])
    red = state.player_states["p1"]
    rules = RULES_PROFILES["classic_00390"]

    red.pawns[0].zone = "track"
    red.pawns[0].track_position = 5
    red.pawns[1].zone = "track"
    red.pawns[1].track_position = 8

    pick = next(move for move in generate_legal_moves(state, red, "7", rules) if move.move_type == "split7_pick")
    options = generate_split_options_for_pair(red, pick.pawn_index or 0, pick.secondary_pawn_index or 0)
    chosen = next(move for move in options if move.steps == 3 and move.secondary_steps == 4)
    apply_move(state, red, chosen, rules)

    assert red.pawns[0].track_position == 8
    assert red.pawns[1].track_position == 12


def test_exact_home_entry_required() -> None:
    state = build_initial_game_state(["p1", "p2"])
    red = state.player_states["p1"]
    rules = RULES_PROFILES["classic_00390"]

    red.pawns[0].zone = "track"
    red.pawns[0].track_position = 58

    moves = generate_legal_moves(state, red, "3", rules)
    assert any(move.pawn_index == 1 for move in moves)

    illegal = generate_legal_moves(state, red, "8", rules)
    assert not any(move.pawn_index == 1 for move in illegal)


def test_card_two_grants_extra_turn_in_classic() -> None:
    game = make_game(start=True)
    current = game.current_player
    assert current is not None
    state = game.game_state.player_states[current.id]
    for pawn in state.pawns[1:]:
        pawn.zone = "home"
    game._sync_player_counts()

    game.game_state.draw_pile = ["2"]
    game._action_draw_card(current, "draw_card")

    assert advance_until(
        game,
        lambda: game.current_player == current and game.game_state.turn_phase == "draw",
        max_ticks=80,
    )


def test_web_turn_menu_orders_utility_actions_at_bottom() -> None:
    game = make_game(start=True, web_first=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    game.game_state.current_card = "1"
    game.game_state.turn_phase = "choose_move"
    game.rebuild_player_menu(player)

    ids = [item.id for item in user.menus["turn_menu"]["items"]]
    assert ids.index("check_scores") < ids.index("whose_turn") < ids.index("whos_at_table")
    assert ids[-2:] == ["web_actions_menu", "web_leave_table"]


def test_turn_menu_contains_web_info_actions() -> None:
    game = make_game(start=True, web_first=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    game.rebuild_player_menu(player)
    labels = [item.text for item in user.menus["turn_menu"]["items"]]

    assert Localization.get("en", "sorry-check-board") in labels
    assert Localization.get("en", "sorry-check-card") in labels
    assert Localization.get("en", "sorry-check-status") in labels


def test_whos_at_table_is_visible_for_web_in_waiting_state() -> None:
    game = make_game(web_first=True)
    player = game.players[0]

    action = game.find_action(player, "whos_at_table")
    assert action is not None

    resolved = game.resolve_action(player, action)
    assert resolved.visible is True


def test_bot_can_finish_scripted_endgame() -> None:
    game = make_game(start=True, bot_second=True)
    bot_player = game.players[1]
    human = game.players[0]

    game.set_turn_players([bot_player, human])
    game.current_player = bot_player
    bot_state = game.game_state.player_states[bot_player.id]
    for pawn in bot_state.pawns[:-1]:
        pawn.zone = "home"
    bot_state.pawns[-1].zone = "home_path"
    bot_state.pawns[-1].home_steps = 5
    game._sync_player_counts()
    game.game_state.draw_pile = ["1"]

    bot_player.bot_think_ticks = 0
    assert advance_until(game, lambda: game.status == "finished", max_ticks=120)
    assert game.winner_name == bot_player.name


def test_game_start_uses_localized_player_list_joining() -> None:
    game = make_game(
        player_count=2,
        names=["Trung", "Ba"],
        locales=["vi", "vi"],
        start=True,
    )
    user = game.get_user(game.players[0])
    assert user is not None

    expected_message = Localization.get(
        "vi",
        "sorry-game-started",
        players=Localization.format_list_and("vi", ["Trung", "Ba"]),
    )
    started_message = next(text for text in user.get_spoken_messages() if text == expected_message)
    assert "và" in started_message
    assert " and " not in started_message


def test_draw_announcement_waits_for_audio_queue() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()

    game.game_state.draw_pile = ["1"]
    game._action_draw_card(player, "draw_card")

    assert game.game_state.turn_phase == "resolving"
    assert not any(message.type == "speak" for message in user.messages)

    assert advance_until(game, lambda: game.game_state.turn_phase == "choose_move", max_ticks=30)
    assert Localization.get("en", "sorry-you-draw-announcement", card="1") in user.get_spoken_messages()


def test_info_actions_remain_available_during_draw_sequence() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()

    game.game_state.draw_pile = ["1"]
    game._action_draw_card(player, "draw_card")

    assert game.is_sequence_gameplay_locked() is True
    game._action_check_card(player, "check_card")

    assert Localization.get("en", "sorry-current-card", card="1") in user.get_spoken_messages()


def test_draw_announcements_localize_card_text_per_listener(monkeypatch) -> None:
    game = make_game(start=True, locales=["en", "vi"])
    player = game.players[0]
    player_user = game.get_user(player)
    other_user = game.get_user(game.players[1])
    assert player_user is not None
    assert other_user is not None

    monkeypatch.setattr(
        game,
        "_card_display_text",
        lambda locale, card_face: f"{locale}:{card_face}",
    )

    game._handle_after_draw(player, "4")

    assert Localization.get("en", "sorry-you-draw-announcement", card="en:4") in player_user.get_spoken_messages()
    assert Localization.get("vi", "sorry-draw-announcement", player=player.name, card="vi:4") in other_user.get_spoken_messages()
    assert Localization.get("vi", "sorry-no-legal-moves", player=player.name, card="vi:4") in other_user.get_spoken_messages()


def test_self_bump_uses_dedicated_message() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()

    player_state = game.game_state.player_states[player.id]
    player_state.pawns[0].zone = "track"
    player_state.pawns[0].track_position = 15
    player_state.pawns[1].zone = "track"
    player_state.pawns[1].track_position = 17

    move = next(
        move
        for move in generate_legal_moves(game.game_state, player_state, "1", RULES_PROFILES["classic_00390"])
        if move.pawn_index == 1
    )
    game._apply_selected_move(player, move, "1")

    assert game.game_state.turn_phase == "resolving"
    assert advance_until(game, lambda: game.current_player != player and game.game_state.turn_phase == "draw", max_ticks=40)
    assert Localization.get("en", "sorry-you-bumped-own-pawn", pawn=2) in user.get_spoken_messages()
    assert Localization.get("en", "sorry-you-captured-pawn", target_player=player.name, pawn=2) not in user.get_spoken_messages()


def test_check_board_lists_every_square_status() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    player_state = game.game_state.player_states[player.id]
    player_state.pawns[0].zone = "track"
    player_state.pawns[0].track_position = 16

    game._action_check_board(player, "check_board")

    lines = [item.text for item in user.menus["status_box"]["items"]]
    assert lines[0] == "Your color: red."
    assert lines[1] == "Quick summary:"
    assert any("Player1 (red):" in line for line in lines)
    assert any("Square 1: empty" == line for line in lines)
    assert any("Square 17: blue slide, pawn 1 of Player1" == line for line in lines)
    assert any("red start area of Player1:" in line for line in lines)
    assert any("red safety space 1 of Player1:" in line for line in lines)
    assert any("red home of Player1:" in line for line in lines)


def test_safety_zone_pawns_cannot_be_targeted_by_swap_or_sorry() -> None:
    state = build_initial_game_state(["p1", "p2"])
    red = state.player_states["p1"]
    blue = state.player_states["p2"]
    rules = RULES_PROFILES["classic_00390"]

    red.pawns[0].zone = "track"
    red.pawns[0].track_position = 5
    red.pawns[1].zone = "start"
    blue.pawns[0].zone = "home_path"
    blue.pawns[0].home_steps = 2

    swap_moves = generate_legal_moves(state, red, "11", rules)
    sorry_moves = generate_legal_moves(state, red, "sorry", rules)

    assert not any(move.move_type == "swap" for move in swap_moves)
    assert not any(move.move_type == "sorry" for move in sorry_moves)


def test_spectator_board_view_skips_your_color_line() -> None:
    game = make_game(start=True)
    spectator_user = MockUser("Spectator", uuid="spec1")
    game.add_player("Spectator", spectator_user)
    spectator = game.players[-1]
    spectator.is_spectator = True

    game._action_check_board(spectator, "check_board")

    lines = [item.text for item in spectator_user.menus["status_box"]["items"]]
    assert lines[0] == "Quick summary:"
    assert not any(line.startswith("Your color:") for line in lines)


def test_check_status_uses_direct_tts_with_localized_phase() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()

    game.game_state.turn_phase = "choose_move"
    game._action_check_status(player, "check_status")

    assert "status_box" not in user.menus
    spoken = user.get_spoken_messages()
    assert any(text == "Phase: choose move" for text in spoken)
    assert not any("sorry-phase-" in text for text in spoken)


def test_move_announcement_includes_destination() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()

    player_state = game.game_state.player_states[player.id]
    player_state.pawns[0].zone = "track"
    player_state.pawns[0].track_position = 5

    move = next(
        move
        for move in generate_legal_moves(game.game_state, player_state, "3", RULES_PROFILES["classic_00390"])
        if move.pawn_index == 1
    )
    game._apply_selected_move(player, move, "3")

    expected_destination = Localization.get("en", "sorry-location-track", position=9)
    expected_message = Localization.get(
        "en",
        "sorry-you-play-forward",
        pawn=1,
        steps=3,
        destination=expected_destination,
    )
    assert advance_until(game, lambda: expected_message in user.get_spoken_messages(), max_ticks=40)


def test_result_contains_home_counts() -> None:
    game = make_game(start=True)
    player = game.players[0]
    state = game.game_state.player_states[player.id]
    for pawn in state.pawns:
        pawn.zone = "home"
    game._sync_player_counts()
    game.winner_name = player.name

    result = game.build_game_result()

    assert result.custom_data["winner_name"] == player.name
    assert result.custom_data["final_scores"][player.name] == 4


def test_empty_deck_ends_game_cleanly() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert player is not None
    user = game.get_user(player)
    assert user is not None

    game.game_state.draw_pile = []
    game.game_state.discard_pile = []
    game._action_draw_card(player, "draw_card")

    assert game.status == "finished"
    assert Localization.get("en", "sorry-deck-exhausted") in user.get_spoken_messages()

    result = game.build_game_result()
    assert result.custom_data["ended_due_to_empty_deck"] is True
    assert result.custom_data["winner_name"] is None


def test_draw_sequence_resumes_after_reload() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    game.game_state.draw_pile = ["1"]
    game._action_draw_card(player, "draw_card")
    payload = game.to_json()

    restored = SorryGame.from_json(payload)
    for restored_player in restored.players:
        original_player = game.get_player_by_id(restored_player.id)
        assert original_player is not None
        original_user = game.get_user(original_player)
        assert original_user is not None
        restored.attach_user(restored_player.id, original_user)

    assert restored.has_active_sequence(tag="turn_flow") is True
    assert advance_until(restored, lambda: restored.game_state.turn_phase == "choose_move", max_ticks=30)


def test_serialization_round_trips_game_state() -> None:
    game = make_game(start=True, faster_setup_one_pawn_out=True)
    player = game.players[0]
    game.game_state.current_card = "10"
    game.game_state.turn_phase = "choose_move"
    game.winner_name = "Nobody"

    restored = SorryGame.from_json(game.to_json())

    assert restored.options.faster_setup_one_pawn_out is True
    assert restored.game_state.current_card == "10"
    assert restored.game_state.turn_phase == "choose_move"
    assert restored.winner_name == "Nobody"
    assert restored.game_state.player_states[player.id].pawns[0].zone == "track"
