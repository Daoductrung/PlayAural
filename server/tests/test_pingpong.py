"""Tests for the real-time spatial-audio Ping Pong game."""

from pathlib import Path
import hashlib
from unittest.mock import patch

import pytest

from ..games.pingpong.game import (
    LANE_X,
    PHASE_AIM_RETURN,
    PHASE_FLIGHT,
    PHASE_POINT_PAUSE,
    PHASE_SERVE,
    SIDE_LIMIT,
    PingPongGame,
    PingPongOptions,
    PingPongPlayer,
)
from ..games.registry import GameRegistry
from ..game_utils.actions import Visibility
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser


ROOT = Path(__file__).parent.parent.parent
Localization.init(ROOT / "server" / "locales")


def make_game(
    *,
    start: bool = True,
    second_is_bot: bool = False,
    first_locale: str = "en",
    second_locale: str = "en",
    **option_overrides,
) -> PingPongGame:
    game = PingPongGame(options=PingPongOptions(**option_overrides))
    game.setup_keybinds()
    game.add_player(
        "Player1", MockUser("Player1", locale=first_locale, uuid="p1")
    )
    second_user = (
        Bot("Player2", uuid="p2")
        if second_is_bot
        else MockUser("Player2", locale=second_locale, uuid="p2")
    )
    game.add_player("Player2", second_user)
    game.host = "Player1"
    if start:
        with patch("server.games.pingpong.game.random.randrange", return_value=0):
            game.on_start()
    return game


def make_doubles_game(*, start: bool = True, **option_overrides) -> PingPongGame:
    game = PingPongGame(
        options=PingPongOptions(team_mode="2v2", **option_overrides)
    )
    game.setup_keybinds()
    for index in range(4):
        name = f"Player{index + 1}"
        game.add_player(name, MockUser(name, locale="en", uuid=f"p{index + 1}"))
    game.host = "Player1"
    if start:
        with patch("server.games.pingpong.game.random.randrange", return_value=0):
            game.on_start()
    return game


def spoken(user: MockUser) -> list[str]:
    return user.get_spoken_messages()


def test_metadata_registration_and_defaults() -> None:
    assert GameRegistry.get("pingpong") is PingPongGame
    game = PingPongGame()
    assert game.get_name() == "Table Tennis"
    assert game.get_type() == "pingpong"
    assert game.get_category() == "arcade"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 4
    assert game.get_score_unit_key() == "game-score-unit-games"
    assert game.options.best_of == "3"
    assert game.options.pace == "standard"
    assert game.options.bot_difficulty == "normal"
    assert game.options.table_language == "en"
    assert game.options.team_mode == "individual"
    assert game.get_name_key() == "game-name-pingpong"


def test_game_name_is_localized_in_supported_table_languages() -> None:
    assert Localization.get("pt", "game-name-pingpong") == "Ping Pong"
    assert Localization.get("en", "game-name-pingpong") == "Table Tennis"
    assert Localization.get("es", "game-name-pingpong") == "Tenis de mesa"
    assert Localization.get("vi", "game-name-pingpong") == "Bóng bàn"
    assert Localization.get("fa", "game-name-pingpong") == "تنیس روی میز"


@pytest.mark.parametrize(
    ("playaural_locale", "expected"),
    [
        ("pt", "pt"),
        ("pt-BR", "pt"),
        ("en", "en"),
        ("es_ES", "es"),
        ("vi", "vi"),
        ("fa", "fa"),
        ("de", "en"),
        ("", "en"),
    ],
)
def test_table_language_follows_creator_with_english_fallback(
    playaural_locale: str, expected: str
) -> None:
    assert PingPongGame._language_from_playaural(playaural_locale) == expected


def test_table_language_is_shared_by_players_with_different_locales() -> None:
    game = make_game(
        start=False,
        table_language="pt",
        first_locale="en",
        second_locale="es",
    )
    first_user = game.get_user(game.players[0])
    second_user = game.get_user(game.players[1])
    assert isinstance(first_user, MockUser)
    assert isinstance(second_user, MockUser)
    with patch("server.games.pingpong.game.random.randrange", return_value=0):
        game.on_start()
    assert any("Saque de Player1" in message for message in spoken(first_user))
    assert any("Saque de Player1" in message for message in spoken(second_user))


def test_wrong_player_inputs_do_not_say_waiting_messages() -> None:
    game = make_game()
    server, receiver = game.players
    receiver_user = game.get_user(receiver)
    server_user = game.get_user(server)
    assert isinstance(receiver_user, MockUser)
    assert isinstance(server_user, MockUser)
    receiver_user.clear_messages()
    game.execute_action(receiver, "serve_ball")
    assert spoken(receiver_user) == []
    game._serve(server)
    server_user.clear_messages()
    game.execute_action(server, "hit_ball")
    assert spoken(server_user) == []


def test_desktop_rally_inputs_do_not_rebuild_menus() -> None:
    game = make_game()
    server = game.players[0]
    with patch.object(game, "refresh_menus") as refresh_menus:
        game.execute_action(server, "aim_left")
        game._serve(server)
    refresh_menus.assert_not_called()


def test_start_creates_official_singles_match_and_announces_server() -> None:
    game = make_game()
    assert game.phase == PHASE_SERVE
    assert game.serving_player_id == "p1"
    assert game.current_player.id == "p1"
    assert len(game.team_manager.teams) == 2
    assert all(team.total_score == 0 for team in game.team_manager.teams)
    player_user = game.get_user(game.players[0])
    opponent_user = game.get_user(game.players[1])
    assert isinstance(player_user, MockUser)
    assert isinstance(opponent_user, MockUser)
    assert any("Player1 to serve" in message for message in spoken(player_user))
    assert any("Player1 to serve" in message for message in spoken(opponent_user))


def test_player_count_matches_selected_official_mode() -> None:
    singles = make_game(start=False)
    assert not singles.prestart_validate()
    singles.options.team_mode = "2v2"
    assert any(
        error[0] == "pingpong-error-doubles-players"
        for error in singles.prestart_validate()
        if isinstance(error, tuple)
    )
    doubles = make_doubles_game(start=False)
    assert not doubles.prestart_validate()


def test_touch_clients_receive_visible_direction_and_hit_actions() -> None:
    game = make_game(start=False)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.client_type = "mobile"
    game.player_action_sets.pop(player.id, None)
    game.setup_player_actions(player)
    turn_actions = game.get_action_set(player, "turn")
    assert turn_actions is not None
    assert {
        action_id
        for action_id in turn_actions._order
        if turn_actions.get_action(action_id).show_in_actions_menu
    } == {
        "aim_left",
        "aim_right",
        "aim_center",
        "serve_ball",
        "hit_ball",
    }


def test_desktop_does_not_show_direction_choices_as_menu_options() -> None:
    game = make_game()
    player = game.players[0]
    assert game._is_play_action_hidden(player) is Visibility.HIDDEN
    game.execute_action(player, "aim_left")
    assert player.response_lane == "left"


@pytest.mark.parametrize(
    ("first_points", "second_points", "expected_server"),
    [
        (0, 0, "p1"),
        (1, 0, "p1"),
        (2, 0, "p2"),
        (9, 9, "p2"),
        (10, 10, "p1"),
        (11, 10, "p2"),
        (11, 11, "p1"),
    ],
)
def test_official_service_rotation(
    first_points: int, second_points: int, expected_server: str
) -> None:
    game = make_game()
    game.players[0].points = first_points
    game.players[1].points = second_points
    assert game._active_pingpong_players()[game._server_index_for_score()].id == expected_server


def test_game_requires_eleven_and_a_two_point_lead() -> None:
    player1, player2 = make_game().players
    player1.points, player2.points = 10, 9
    assert not PingPongGame._game_is_won(player1, player2)
    player1.points, player2.points = 11, 9
    assert PingPongGame._game_is_won(player1, player2)
    player1.points, player2.points = 11, 10
    assert not PingPongGame._game_is_won(player1, player2)
    player1.points, player2.points = 12, 10
    assert PingPongGame._game_is_won(player1, player2)


def test_c_serves_and_x_is_reserved_for_returns() -> None:
    game = make_game()
    server = game.players[0]
    game.execute_action(server, "hit_ball")
    assert game.phase == PHASE_SERVE
    with patch("server.games.pingpong.game.random.uniform", return_value=0.0):
        game.execute_action(server, "serve_ball")
    assert game.phase == PHASE_FLIGHT
    assert game.receiving_player_id == "p2"
    assert game.ball_ticks_remaining == game.ball_total_ticks


def test_arrow_direction_choice_is_silent_and_up_means_center() -> None:
    game = make_game()
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game.execute_action(player, "aim_right")
    assert player.response_lane == "right"
    game.execute_action(player, "aim_center")
    assert player.response_lane == "center"
    assert player.court_x == 0
    assert not [
        message
        for message in user.messages
        if message.type in {"speak", "play_sound"}
    ]


def test_swing_before_bounce_loses_the_point() -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    game._attempt_return(receiver)
    assert game.players[0].points == 1
    assert receiver.points == 0
    assert game.phase == PHASE_POINT_PAUSE
    receiver_user = game.get_user(receiver)
    assert isinstance(receiver_user, MockUser)
    assert any("Score:" in message for message in spoken(receiver_user))


def test_well_positioned_and_timed_swing_returns_ball() -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    receiver.court_x = game.ball_target_x
    receiver.court_depth = game.ball_target_depth
    receiver.response_lane = game._lane_for_x(game.ball_target_x)
    game.ball_bounced = True
    game.return_window_ticks = 3
    game.ball_ticks_remaining = max(1, round(game.ball_total_ticks * 0.12))
    game._attempt_return(receiver)
    assert game.phase == PHASE_AIM_RETURN
    game.execute_action(receiver, "aim_center")
    assert game.phase == PHASE_FLIGHT
    assert game.receiving_player_id == "p1"
    assert game.rally_count == 1
    assert receiver.successful_returns == 1
    assert game.players[0].points == game.players[1].points == 0


def test_correct_timing_without_position_is_not_an_automatic_return() -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    receiver.court_x = -0.88 if game.ball_target_x > 0 else 0.88
    receiver.response_lane = (
        "left" if game._lane_for_x(game.ball_target_x) != "left" else "right"
    )
    receiver.court_depth = 1.0
    game.ball_bounced = True
    game.ball_ticks_remaining = max(1, round(game.ball_total_ticks * 0.12))
    game._attempt_return(receiver)
    assert game.players[0].points == 1
    assert receiver.missed_returns == 1


@pytest.mark.parametrize(("target_x", "expected_sign"), [(-0.7, -1), (0.0, 0), (0.7, 1)])
def test_table_bounce_uses_explicit_stereo_pan(target_x: float, expected_sign: int) -> None:
    game = make_game()
    receiver = game.players[1]
    game.receiving_player_id = receiver.id
    game.ball_target_x = target_x
    user = game.get_user(receiver)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game._play_table_bounce(receiver)
    sound = next(message for message in user.messages if message.type == "play_sound")
    pan = sound.data["pan"]
    assert pan == 0 if expected_sign == 0 else pan * expected_sign > 0


def test_swing_before_bounce_plays_real_net_contact_asset() -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    receiver.response_lane = game._lane_for_x(game.ball_target_x)
    receiver.court_x = game.ball_target_x
    game.ball_bounced = False
    game.ball_ticks_remaining = game.ball_total_ticks
    user = game.get_user(receiver)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game._attempt_return(receiver)
    assert any(
        message.type == "play_sound" and message.data["name"] == "game_pingpong/net.ogg"
        for message in user.messages
    )


@pytest.mark.parametrize(
    ("action", "expected_lane"),
    [("aim_left", "left"), ("aim_center", "center"), ("aim_right", "right")],
)
def test_server_chooses_serve_direction(action: str, expected_lane: str) -> None:
    game = make_game()
    server = game.players[0]
    game.execute_action(server, action)
    with patch("server.games.pingpong.game.random.uniform", return_value=0.0):
        game._serve(server)
    assert game._lane_for_x(game.ball_target_x) == expected_lane


def test_human_serve_has_no_hidden_random_direction_error() -> None:
    game = make_game()
    server = game.players[0]
    game.execute_action(server, "aim_right")
    with patch(
        "server.games.pingpong.game.random.uniform",
        side_effect=AssertionError("human serve must not use random error"),
    ):
        game._serve(server)
    assert game.ball_target_x == LANE_X


@pytest.mark.parametrize(
    ("action", "expected_lane"),
    [("aim_left", "left"), ("aim_center", "center"), ("aim_right", "right")],
)
def test_player_chooses_return_destination(action: str, expected_lane: str) -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    receiver.response_lane = game._lane_for_x(game.ball_target_x)
    game.ball_bounced = True
    game.return_window_ticks = 7
    game._attempt_return(receiver)
    assert game.phase == PHASE_AIM_RETURN
    game.execute_action(receiver, action)
    assert game.receiving_player_id == game.players[0].id
    assert game._lane_for_x(game.ball_target_x) == expected_lane


@pytest.mark.parametrize(
    ("target_x", "incoming_action"),
    [(-LANE_X, "aim_left"), (0.0, "aim_center"), (LANE_X, "aim_right")],
)
@pytest.mark.parametrize(
    ("outgoing_action", "outgoing_lane"),
    [("aim_left", "left"), ("aim_center", "center"), ("aim_right", "right")],
)
def test_direction_then_x_immediately_reaches_ball_and_chooses_destination(
    target_x: float,
    incoming_action: str,
    outgoing_action: str,
    outgoing_lane: str,
) -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    receiver.court_x = -SIDE_LIMIT if target_x >= 0 else SIDE_LIMIT
    game.ball_target_x = target_x
    game.ball_bounced = True
    game.return_window_ticks = 12

    game.execute_action(receiver, incoming_action)
    game.execute_action(receiver, "hit_ball")

    assert game.phase == PHASE_AIM_RETURN
    game.execute_action(receiver, outgoing_action)
    assert game.phase == PHASE_FLIGHT
    assert game._lane_for_x(game.ball_target_x) == outgoing_lane
    assert game.players[0].points == game.players[1].points == 0


def test_return_destination_defaults_to_center_after_short_window() -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    receiver.response_lane = game._lane_for_x(game.ball_target_x)
    game.ball_bounced = True
    game.return_window_ticks = 7
    game._attempt_return(receiver)
    assert game.phase == PHASE_AIM_RETURN
    for _ in range(12):
        game.on_tick()
    assert game.phase == PHASE_FLIGHT
    assert game._lane_for_x(game.ball_target_x) == "center"


def test_return_window_starts_at_bounce_and_expires_quickly() -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    while not game.ball_bounced:
        game.on_tick()
    assert 0 < game.return_window_ticks <= 22
    for _ in range(24):
        game.on_tick()
        if game.phase == PHASE_POINT_PAUSE:
            break
    assert game.phase == PHASE_POINT_PAUSE


def test_serve_paddle_and_first_table_bounce_are_not_simultaneous() -> None:
    game = make_game()
    server = game.players[0]
    user = game.get_user(server)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game._serve(server)
    names = [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound"
    ]
    assert names == ["game_pingpong/paddle.ogg"]
    game.on_tick()
    game.on_tick()
    assert "game_pingpong/table.ogg" not in user.get_sounds_played()
    game.on_tick()
    assert "game_pingpong/table.ogg" in user.get_sounds_played()


def test_keys_during_point_pause_do_not_announce_preparation_messages() -> None:
    game = make_game()
    winner, loser = game.players
    game._award_point(winner, "passed", loser)
    user = game.get_user(loser)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game.execute_action(loser, "hit_ball")
    game.execute_action(loser, "serve_ball")
    assert spoken(user) == []


def test_winning_game_updates_match_score_and_best_of_one_finishes() -> None:
    game = make_game(best_of="1")
    winner, loser = game.players
    winner.points = 10
    loser.points = 3
    game._award_point(winner, "passed", loser)
    assert winner.games_won == 1
    assert game.winner_id == winner.id
    assert game.game_active is False
    assert game.team_manager.get_team(winner.name).total_score == 1


def test_best_of_three_resets_points_and_switches_initial_server() -> None:
    game = make_game(best_of="3")
    winner, loser = game.players
    winner.points = 10
    loser.points = 4
    game._award_point(winner, "passed", loser)
    assert winner.games_won == 1
    assert game.game_active is True
    assert game.game_number == 2
    assert game.initial_server_index == 1
    assert winner.points == loser.points == 0
    assert game.phase == PHASE_POINT_PAUSE


@pytest.mark.parametrize("difficulty", ["easy", "normal", "hard"])
def test_bot_moves_and_eventually_resolves_a_rally(difficulty: str) -> None:
    game = make_game(second_is_bot=True, bot_difficulty=difficulty)
    game._serve(game.players[0])
    starting_generation = game.ball_generation
    for _ in range(80):
        game.on_tick()
        if game.phase != PHASE_FLIGHT or game.ball_generation > starting_generation:
            break
    assert game.ball_generation > starting_generation or game.phase == PHASE_POINT_PAUSE


def test_bot_waits_for_the_bounce_cue_before_moving() -> None:
    game = make_game(second_is_bot=True, bot_difficulty="hard")
    bot = game.players[1]
    game._serve(game.players[0])
    assert bot.court_x == bot.paddle_target_x == 0
    while not game.ball_bounced:
        game.on_tick()
    assert bot.paddle_target_x == 0
    for _ in range(3):
        game.on_tick()
    assert bot.paddle_target_x != 0 or game.bot_planned_lane == "center"


def test_serialization_preserves_live_ball_and_player_state() -> None:
    game = make_game()
    game._serve(game.players[0])
    game.players[1].court_x = 0.32
    loaded = PingPongGame.from_json(game.to_json())
    assert loaded.phase == PHASE_FLIGHT
    assert loaded.ball_target_x == game.ball_target_x
    assert loaded.ball_ticks_remaining == game.ball_ticks_remaining
    assert isinstance(loaded.players[1], PingPongPlayer)
    assert loaded.players[1].court_x == 0.32


def test_serialization_preserves_post_hit_choice_window() -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    receiver.court_x = game.ball_target_x
    game.ball_bounced = True
    game.return_window_ticks = 12
    game._attempt_return(receiver)
    loaded = PingPongGame.from_json(game.to_json())
    assert loaded.phase == PHASE_AIM_RETURN
    assert loaded.aim_return_ticks == 12
    assert loaded.pending_return_hitter_id == receiver.id
    assert loaded.service_rotation_ids == ["p1", "p2"]


def test_repeated_direction_input_does_not_duplicate_speech_or_break_rally() -> None:
    game = make_game()
    game._serve(game.players[0])
    receiver = game.players[1]
    user = game.get_user(receiver)
    assert isinstance(user, MockUser)
    user.clear_messages()
    for _ in range(100):
        game.execute_action(receiver, "aim_left")
        game.execute_action(receiver, "aim_right")
        game.execute_action(receiver, "aim_center")
    assert game.phase == PHASE_FLIGHT
    assert spoken(user) == []


def test_spectator_hears_spatial_match_audio() -> None:
    game = make_game(start=False)
    spectator_user = MockUser("Watcher", locale="en", uuid="watcher")
    spectator = game.add_player("Watcher", spectator_user)
    spectator.is_spectator = True
    with patch("server.games.pingpong.game.random.randrange", return_value=0):
        game.on_start()
    spectator_user.clear_messages()
    game._serve(game.players[0])
    assert "game_pingpong/paddle.ogg" in spectator_user.get_sounds_played()


def test_all_client_sound_trees_contain_the_same_assets() -> None:
    expected = {"paddle.ogg", "table.ogg", "net.ogg"}
    reference_hashes = None
    for client in ("client", "mobile_client", "web_client"):
        sound_dir = ROOT / client / "sounds" / "game_pingpong"
        assert {path.name for path in sound_dir.iterdir()} == expected
        assert all(path.stat().st_size > 0 for path in sound_dir.iterdir())
        hashes = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sound_dir.iterdir()
        }
        reference_hashes = reference_hashes or hashes
        assert hashes == reference_hashes


def test_audio_assets_have_public_provenance() -> None:
    provenance = (ROOT / "server" / "games" / "pingpong" / "AUDIO_PROVENANCE.md")
    text = provenance.read_text(encoding="utf-8")
    for sound_id in ("269718", "418555", "555202"):
        assert f"https://freesound.org/s/{sound_id}/" in text
    assert text.count("CC0 1.0") >= 3


def test_pingpong_locales_and_documentation_exist() -> None:
    for locale in ("en", "es", "fa", "pt", "vi"):
        assert (ROOT / "server" / "locales" / locale / "pingpong.ftl").is_file()
        document_path = (
            ROOT
            / "server"
            / "documentation"
            / "content"
            / locale
            / "games"
            / "pingpong.md"
        )
        assert document_path.is_file()
        document = document_path.read_text(encoding="utf-8")
        assert document.startswith(
            f"**{Localization.get(locale, 'game-name-pingpong')}**"
        )
        assert not any(line.startswith("#") for line in document.splitlines())
        assert "PlayAural" not in document
        for shortcut in ("C", "X", "P", "M"):
            assert f"**{shortcut}:**" in document


def test_doubles_uses_shared_balanced_team_arrangement() -> None:
    game = make_doubles_game()
    assert [player.id for player in game.turn_players] == ["p1", "p2", "p3", "p4"]
    assert [team.members for team in game.team_manager.teams] == [
        ["Player1", "Player3"],
        ["Player2", "Player4"],
    ]
    assert game.service_rotation_ids == ["p1", "p2", "p3", "p4"]


def test_doubles_service_and_return_order_follow_official_rotation() -> None:
    game = make_doubles_game()
    assert (game.serving_player_id, game.receiving_player_id) == ("p1", "p2")
    game._serve(game.players[0])
    receiver = game.players[1]
    receiver.court_x = game.ball_target_x
    receiver.paddle_target_x = game.ball_target_x
    game.ball_bounced = True
    game.return_window_ticks = 12
    game._attempt_return(receiver)
    game._finalize_aimed_return(receiver, "center")
    assert game.receiving_player_id == "p3"


@pytest.mark.parametrize(
    ("first_points", "second_points", "server_id", "receiver_id"),
    [
        (0, 0, "p1", "p2"),
        (1, 0, "p1", "p2"),
        (2, 0, "p2", "p3"),
        (4, 0, "p3", "p4"),
        (6, 0, "p4", "p1"),
        (10, 10, "p3", "p4"),
        (11, 10, "p4", "p1"),
    ],
)
def test_doubles_official_service_blocks(
    first_points: int,
    second_points: int,
    server_id: str,
    receiver_id: str,
) -> None:
    game = make_doubles_game()
    game._set_team_points(0, first_points)
    game._set_team_points(1, second_points)
    game._prepare_serve(announce=False)
    assert (game.serving_player_id, game.receiving_player_id) == (
        server_id,
        receiver_id,
    )


def test_doubles_serve_stays_inside_diagonal_half() -> None:
    game = make_doubles_game()
    server = game.players[0]
    for lane in ("left", "center", "right"):
        game._prepare_serve(announce=False)
        server.shot_lane = lane
        game._serve(server)
        assert 0 < game.ball_target_x <= 0.76


def test_doubles_points_and_games_are_shared_by_teammates() -> None:
    game = make_doubles_game(best_of="1")
    winner, loser = game.players[0], game.players[1]
    game._set_team_points(0, 10)
    game._set_team_points(1, 3)
    game._award_point(winner, "passed", loser)
    assert [player.points for player in (game.players[0], game.players[2])] == [11, 11]
    assert [player.games_won for player in (game.players[0], game.players[2])] == [1, 1]
    assert game.winner_team_index == 0


def test_arrow_sets_destination_and_paddle_moves_continuously() -> None:
    game = make_game()
    player = game.players[0]
    game.execute_action(player, "aim_right")
    assert player.paddle_target_x > 0
    assert player.court_x == 0
    game.on_tick()
    assert 0 < player.court_x < player.paddle_target_x


def test_post_hit_direction_window_is_slightly_longer() -> None:
    game = make_game(pace="standard")
    game._serve(game.players[0])
    receiver = game.players[1]
    receiver.court_x = game.ball_target_x
    receiver.paddle_target_x = game.ball_target_x
    game.ball_bounced = True
    game.return_window_ticks = 12
    game._attempt_return(receiver)
    assert game.aim_return_ticks == 12
