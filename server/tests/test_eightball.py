"""Tests for server-authoritative Eight-Ball Pool."""

import math
from pathlib import Path
from unittest.mock import patch

from ..games.eightball.bot import choose_shot
from ..games.eightball.game import (
    GROUP_SOLIDS, GROUP_STRIPES, MODE_CHOICES, MODE_CUTTHROAT, MODE_DOUBLES,
    MODE_SINGLES,
    PHYSICS_PLAYBACK_RATE, TABLE_LANGUAGES,
    EightBallGame, EightBallOptions, EightBallPlayer,
)
from ..games.eightball.physics import (
    BALL_RADIUS, CORNER_POCKET_CUT_ANGLE, CORNER_POCKET_MOUTH,
    CORNER_POCKET_SHELF, POCKETS, POCKET_BACK_DRAFT_ANGLE, POCKET_RADII,
    SIDE_POCKET_CUT_ANGLE, SIDE_POCKET_MOUTH, SIDE_POCKET_SHELF,
    TABLE_SIZES, Ball, PhysicsEvent, ShotResult, build_cutthroat_rack, build_rack,
    get_table_geometry, simulate_shot,
)
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser


Localization.init(Path(__file__).parent.parent / "locales")


def make_game(
    *, bot_second: bool = False, start: bool = False, resolve_lag: bool = True,
    player_count: int = 2, mode: str = MODE_SINGLES, language: str = "en",
    power_assistance: bool = True, table_size: str = "9ft",
) -> EightBallGame:
    game = EightBallGame(options=EightBallOptions(
        play_mode=mode, table_language=language, power_assistance=power_assistance,
        table_size=table_size,
    ))
    game.setup_keybinds()
    game.add_player("Player1", MockUser("Player1", uuid="p1"))
    second = Bot("Bot", uuid="p2") if bot_second else MockUser("Player2", uuid="p2")
    game.add_player("Bot" if bot_second else "Player2", second)
    for number in range(3, player_count + 1):
        game.add_player(
            f"Player{number}", MockUser(f"Player{number}", uuid=f"p{number}")
        )
    game.host = "Player1"
    if start:
        game.on_start()
        if resolve_lag:
            game.lag_active = False
            game.lag_break_choice_pending = False
            game.breaker_index = 0
            game._start_frame()
    return game


def finish_sequence(game: EightBallGame, sequence_id: str) -> None:
    """Advance a deterministic game sequence without running unrelated bot AI."""
    for _ in range(200):
        sequence = next(
            (item for item in game.active_sequences if item.sequence_id == sequence_id),
            None,
        )
        if sequence is None:
            return
        game.sound_scheduler_tick = max(game.sound_scheduler_tick, sequence.next_tick)
        game.process_sequences()
    raise AssertionError(f"Sequence {sequence_id} did not finish")


def test_registration_options_and_supported_player_range() -> None:
    assert GameRegistry.get("eightball") is EightBallGame
    assert EightBallGame.get_min_players() == 2
    assert EightBallGame.get_max_players() == 5
    options = EightBallOptions()
    assert options.play_mode == MODE_SINGLES
    assert options.table_language == "en"
    assert options.table_size == "9ft"
    assert options.power_assistance is True
    assert options.frames_to_win == 1
    assert options.bot_difficulty == "medium"
    assert list(options.get_option_metas())[:4] == [
        "play_mode", "table_size", "power_assistance", "table_language",
    ]
    assert EightBallGame.get_name() == "Pool"


def test_new_table_inherits_supported_creator_language_and_falls_back_to_english() -> None:
    portuguese = EightBallGame()
    portuguese.initialize_lobby(
        "Criador", MockUser("Criador", locale="pt-BR", uuid="creator-pt")
    )
    assert portuguese.options.table_language == "pt"
    options = portuguese.get_action_set(portuguese.players[0], "options")
    assert options is not None
    assert options._order[:4] == [
        "set_play_mode", "set_table_size",
        "toggle_power_assistance", "set_table_language",
    ]

    vietnamese = EightBallGame()
    vietnamese.initialize_lobby(
        "Creator", MockUser("Creator", locale="vi", uuid="creator-vi")
    )
    assert vietnamese.options.table_language == "en"
    vi_options = vietnamese.get_action_set(vietnamese.players[0], "options")
    assert vi_options is not None
    first = vi_options.get_visible_actions(vietnamese, vietnamese.players[0])[0]
    assert first.label.startswith("Mode:")
    mode_action = vi_options._actions["set_play_mode"]
    mode_items = vietnamese._build_action_menu_input_items(
        mode_action, vietnamese.players[0],
        vietnamese.get_user(vietnamese.players[0]), MODE_CHOICES,
    )
    assert mode_items[0].text == "Eight-Ball Singles, 2 players"


def test_each_published_mode_requires_its_exact_player_count() -> None:
    for mode, correct_count in (
        (MODE_SINGLES, 2), (MODE_DOUBLES, 4), (MODE_CUTTHROAT, 5),
    ):
        valid = make_game(player_count=correct_count, mode=mode)
        assert valid.prestart_validate() == []
        invalid = make_game(player_count=2, mode=mode)
        if correct_count == 2:
            invalid.add_player("Extra", MockUser("Extra", uuid="extra"))
        assert invalid.prestart_validate()


def test_cutthroat_rack_uses_published_one_six_and_eleven_positions() -> None:
    balls = build_cutthroat_rack()
    one = next(ball for ball in balls if ball.number == 1)
    six = next(ball for ball in balls if ball.number == 6)
    eleven = next(ball for ball in balls if ball.number == 11)
    assert one.x == -25.0 and one.y == 0.0
    assert six.x == eleven.x
    assert {six.y, eleven.y} == {-4 * BALL_RADIUS, 4 * BALL_RADIUS}


def test_table_uses_wpa_nine_foot_ball_and_pocket_dimensions() -> None:
    assert BALL_RADIUS * 2.0 == 2.25
    assert CORNER_POCKET_MOUTH == 4.5625
    assert SIDE_POCKET_MOUTH == 5.0625
    assert CORNER_POCKET_SHELF == 1.625
    assert SIDE_POCKET_SHELF == 0.1875
    assert CORNER_POCKET_CUT_ANGLE == 142.0
    assert SIDE_POCKET_CUT_ANGLE == 104.0
    assert POCKET_BACK_DRAFT_ANGLE == 13.5
    assert POCKET_RADII[1] > POCKET_RADII[0]


def test_table_size_choices_do_not_speak_feet_in_the_creation_menu() -> None:
    labels = [
        Localization.get("pt", f"eightball-table-size-{size}").lower()
        for size in TABLE_SIZES
    ]
    assert labels == ["compacta de bar", "mesa de competição", "mesa profissional"]
    assert all("pé" not in label and "ft" not in label for label in labels)


def test_all_selectable_table_sizes_drive_real_geometry_and_rack_positions() -> None:
    expected = {
        "7ft": (39.0, 19.5),
        "8ft": (46.0, 23.0),
        "9ft": (50.0, 25.0),
    }
    assert set(TABLE_SIZES) == set(expected)
    for table_size, dimensions in expected.items():
        geometry = get_table_geometry(table_size)
        assert (geometry.half_width, geometry.half_height) == dimensions
        rack = build_rack(table_size=table_size)
        cue = next(ball for ball in rack if ball.number == 0)
        apex = next(ball for ball in rack if ball.number == 1)
        assert cue.x == geometry.half_width / 2.0
        assert apex.x == -geometry.half_width / 2.0
        assert all(
            abs(ball.x) <= geometry.half_width
            and abs(ball.y) <= geometry.half_height
            for ball in rack
        )
        target = Ball(1, 0.0, 0.0)
        cue = Ball(0, geometry.half_width * 0.4, 0.0)
        pocket_x, pocket_y = geometry.pocket_aim_points[0]
        path = math.hypot(pocket_x, pocket_y)
        ghost_x = -(pocket_x / path) * BALL_RADIUS * 2.0
        ghost_y = -(pocket_y / path) * BALL_RADIUS * 2.0
        angle = math.degrees(
            math.atan2(ghost_y - cue.y, ghost_x - cue.x)
        ) % 360.0
        result = simulate_shot(
            [cue, target], angle, 75, table_size=table_size,
        )
        potted = next(ball for ball in result.balls if ball.number == 1)
        assert potted.potted and potted.pocket_potted == 0


def test_selected_table_size_controls_game_cursor_and_pockets() -> None:
    game = make_game(start=True, table_size="7ft")
    player = game.current_player
    assert isinstance(player, EightBallPlayer)
    geometry = get_table_geometry("7ft")
    assert game._pockets == geometry.pockets
    assert player.cursor_x == geometry.half_width / 2.0
    assert all(
        abs(ball.x) <= geometry.half_width
        and abs(ball.y) <= geometry.half_height
        for ball in game.balls
    )


def test_ghost_ball_aim_enters_corner_pocket_at_all_sufficient_powers() -> None:
    cue = Ball(0, 20.0, 0.0)
    target = Ball(1, 0.0, 0.0)
    pocket_x, pocket_y = get_table_geometry().pocket_aim_points[0]
    length = math.hypot(pocket_x - target.x, pocket_y - target.y)
    ghost_x = target.x - (pocket_x - target.x) / length * BALL_RADIUS * 2.0
    ghost_y = target.y - (pocket_y - target.y) / length * BALL_RADIUS * 2.0
    angle = math.degrees(math.atan2(ghost_y - cue.y, ghost_x - cue.x)) % 360.0
    for power in (40, 55, 70, 85, 100):
        result = simulate_shot([cue, target], angle, power)
        potted = next(ball for ball in result.balls if ball.number == 1)
        assert potted.potted and potted.pocket_potted == 0


def test_regulation_pocket_jaws_reject_a_side_pocket_shot_outside_the_mouth() -> None:
    result = simulate_shot([Ball(0, 2.2, 0.0)], 90.0, 55)
    assert not result.cue_scratch
    assert any(event.kind == "rail" for event in result.events)


def test_side_pocket_requires_crossing_the_real_shelf_before_capture() -> None:
    geometry = get_table_geometry()
    before_shelf = Ball(1, 0.0, geometry.half_height + SIDE_POCKET_SHELF - 0.01)
    after_shelf = Ball(1, 0.0, geometry.half_height + SIDE_POCKET_SHELF + 0.01)
    assert not before_shelf.potted
    # A slow cue ball starting on the drop line is captured immediately.
    result = simulate_shot([Ball(0, after_shelf.x, after_shelf.y)], 90.0, 10)
    assert result.cue_scratch


def test_cushions_still_rebound_away_from_pocket_openings() -> None:
    result = simulate_shot([Ball(0, 10.0, 0.0)], 90.0, 40)
    assert not result.cue_scratch
    assert any(event.kind == "rail" for event in result.events)


def test_rack_is_complete_and_non_overlapping() -> None:
    balls = build_rack()
    assert sorted(ball.number for ball in balls) == list(range(16))
    for index, first in enumerate(balls):
        for second in balls[index + 1 :]:
            assert math.hypot(first.x - second.x, first.y - second.y) >= BALL_RADIUS * 2.0


def test_physics_is_deterministic_and_pockets_a_straight_ball() -> None:
    balls = [Ball(0, 0.0, 10.0), Ball(1, 0.0, 20.0)]
    first = simulate_shot(balls, 90.0, 45)
    second = simulate_shot(balls, 90.0, 45)
    assert first.to_dict() == second.to_dict()
    assert first.first_contact == 1
    assert first.potted == [1]
    assert next(ball for ball in first.balls if ball.number == 1).z < 0.0
    assert not first.cue_scratch
    assert {event.kind for event in first.events} >= {"cue", "collision", "pocket"}


def test_low_power_stops_short_while_playable_power_pockets_the_ball() -> None:
    balls = [Ball(0, 0.0, -10.0), Ball(1, 0.0, 5.0)]
    assert 1 not in simulate_shot(balls, 90.0, 10).potted
    assert 1 in simulate_shot(balls, 90.0, 20).potted


def test_break_uses_physics_instead_of_random_ball_placement() -> None:
    result = simulate_shot(build_rack(), 180.0, 100)
    assert result.first_contact == 1
    assert any(event.kind == "collision" for event in result.events)
    assert len({(round(ball.x, 4), round(ball.y, 4)) for ball in result.balls}) == 16


def test_keybinds_keep_standard_playaural_actions() -> None:
    game = make_game()
    assert any(bind.actions == ["whose_turn"] for bind in game._keybinds["t"])
    assert any(bind.actions == ["shoot"] for bind in game._keybinds["space"])
    assert any(bind.actions == ["turn_left"] for bind in game._keybinds["left"])
    assert any(bind.actions == ["move_forward"] for bind in game._keybinds["up"])
    assert any(bind.actions == ["spin_up"] for bind in game._keybinds["pageup"])


def test_desktop_play_surface_is_empty_so_plain_arrows_reach_the_game() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert isinstance(player, EightBallPlayer)
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    assert game.build_menu_items(player, user).items == []
    user.client_type = "mobile"
    assert game.build_menu_items(player, user).items


def test_start_builds_real_table_and_keeps_table_open_after_break() -> None:
    game = make_game(start=True)
    assert len(game.balls) == 16
    assert game.table_open
    assert game.break_shot
    assert isinstance(game.current_player, EightBallPlayer)


def test_start_keeps_full_mode_rules_in_help_instead_of_speaking_them() -> None:
    game = make_game(start=True, resolve_lag=False)
    player = game.current_player
    assert isinstance(player, EightBallPlayer)
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    spoken = [message.lower() for message in user.get_spoken_messages()]
    assert any("pool started" in message for message in spoken)
    assert any("lag for the first break" in message for message in spoken)
    assert not any("under wpa" in message for message in spoken)


def test_traditional_lag_decides_the_first_breaker() -> None:
    game = make_game(start=True, resolve_lag=False)
    first = game.current_player
    assert isinstance(first, EightBallPlayer)
    second = game._opponent(first)
    assert isinstance(second, EightBallPlayer)
    assert game.lag_active
    assert game.balls == []
    first.power = 50
    game._action_shoot(first)
    assert game.has_active_sequence(sequence_id="eightball-lag-shot")
    assert game.current_player is first
    finish_sequence(game, "eightball-lag-shot")
    assert game.current_player is second
    second.power = 40
    game._action_shoot(second)
    finish_sequence(game, "eightball-lag-shot")
    assert not game.lag_active
    assert game.lag_break_choice_pending
    assert game.current_player is first
    first_user = game.get_user(first)
    second_user = game.get_user(second)
    assert isinstance(first_user, MockUser)
    assert isinstance(second_user, MockUser)
    first_user.clear_messages()
    second_user.clear_messages()
    game._action_lag_break_self(first)
    assert not game.lag_break_choice_pending
    assert game.current_player is first
    assert game.breaker_index == game.turn_players.index(first)
    assert len(game.balls) == 16
    assert any(
        "you will take the first break" in message.lower()
        for message in first_user.get_spoken_messages()
    )
    assert any(
        "player1 will take the first break" in message.lower()
        for message in second_user.get_spoken_messages()
    )


def test_equal_selected_lag_power_does_not_force_a_permanent_tie() -> None:
    game = make_game(start=True, resolve_lag=False)
    first = game.current_player
    assert isinstance(first, EightBallPlayer)
    second = game._opponent(first)
    assert isinstance(second, EightBallPlayer)
    first.power = second.power = 55
    with patch(
        "server.games.eightball.game.random.uniform", side_effect=(-0.4, 0.4)
    ):
        game._action_shoot(first)
        finish_sequence(game, "eightball-lag-shot")
        game._action_shoot(second)
        finish_sequence(game, "eightball-lag-shot")
    assert not game.lag_active
    assert game.lag_break_choice_pending
    assert game.lag_winner_id in {first.id, second.id}


def test_lag_explains_an_invalid_short_attempt() -> None:
    game = make_game(start=True, resolve_lag=False)
    player = game.current_player
    assert isinstance(player, EightBallPlayer)
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()
    player.power = 10
    game._action_shoot(player)
    finish_sequence(game, "eightball-lag-shot")
    assert player.id in game.lag_bad_players
    assert any(
        "did not reach the foot cushion" in message.lower()
        for message in user.get_spoken_messages()
    )


def test_ball_in_hand_uses_arrow_placement_before_shooting() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert isinstance(player, EightBallPlayer)
    game.ball_in_hand = True
    cue = game._ball(0)
    assert cue is not None
    old_x = cue.x
    game._action_turn_right(player)
    assert cue.x == old_x + 1.0
    game._action_shoot(player)
    assert not game.ball_in_hand
    assert game.pending_shot is None


def test_arrows_use_first_person_3d_movement_and_direct_aiming() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert isinstance(player, EightBallPlayer)
    start_x, start_y = player.cursor_x, player.cursor_y
    assert player.aim_angle == 180.0
    game._action_turn_right(player)
    assert player.aim_angle == 180.0
    assert player.cursor_x == start_x
    assert player.cursor_y == start_y + 1.0
    game._action_turn_right_fine(player)
    assert player.aim_angle == 179.0
    game._action_move_forward(player)
    radians = math.radians(179.0)
    assert player.cursor_x == round(start_x + math.cos(radians), 1)
    assert player.cursor_y == round(start_y + 1.0 + math.sin(radians), 1)
    for _ in range(30):
        game._action_move_forward_fast(player)
    assert -50.0 <= player.cursor_x <= 50.0
    assert -25.0 <= player.cursor_y <= 25.0


def test_first_person_movement_never_speaks_menu_options() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert isinstance(player, EightBallPlayer)
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game._action_turn_left(player)
    game._action_move_forward(player)
    game._action_move_backward(player)
    assert not any("choose" in message.lower() for message in user.get_spoken_messages())


def test_first_person_heading_rotates_the_spatial_sound_field() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert isinstance(player, EightBallPlayer)
    player.cursor_x, player.cursor_y = 25.0, 0.0
    player.aim_angle = 180.0
    # A sound five world units toward the rack is directly in front.
    assert game._relative_audio_position(player, 20.0, 0.0) == (0.0, 1.0, 0.0)
    player.aim_angle = 90.0
    # After turning north, the same world point is now heard to the left.
    assert game._relative_audio_position(player, 20.0, 0.0) == (-1.0, 0.0, 0.0)


def test_l_probe_uses_the_selected_first_person_shot_angle() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert isinstance(player, EightBallPlayer)
    hit = game._raycast(player.aim_angle)
    assert hit is not None and hit[1] == 50.0
    apex_number = hit[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game._action_probe_line(player)
    assert f"ball {apex_number}" in user.get_last_spoken().lower()
    player.aim_angle = 90.0
    user.clear_messages()
    game._action_probe_line(player)
    assert "no ball" in user.get_last_spoken().lower()


def test_bot_plans_a_physical_shot_at_each_difficulty() -> None:
    rack = build_rack()
    legal = set(range(1, 8))
    for difficulty in ("easy", "medium", "hard", "hardcore"):
        angle, power, spin = choose_shot(rack, legal, difficulty)
        assert 0.0 <= angle < 360.0
        assert 10 <= power <= 100
        assert -1 <= spin <= 1


def test_first_legal_post_break_pot_assigns_groups_and_keeps_turn() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    game.shot_player_id = shooter.id
    game.shot_group_before = ""
    game.shot_remaining_before = 7
    game.shot_was_break = False
    shooter.called_ball = 1
    shooter.called_pocket = 0
    balls = build_rack()
    one = next(ball for ball in balls if ball.number == 1)
    one.potted = True
    one.pocket_potted = 0
    game.pending_shot = ShotResult(
        balls=balls, first_contact=1, potted=[1], rail_after_contact=True
    )
    shooter_user = game.get_user(shooter)
    opponent = game._opponent(shooter)
    assert isinstance(opponent, EightBallPlayer)
    opponent_user = game.get_user(opponent)
    assert isinstance(shooter_user, MockUser)
    assert isinstance(opponent_user, MockUser)
    shooter_user.clear_messages()
    opponent_user.clear_messages()
    game._resolve_shot()
    assert shooter.group == "solids"
    assert opponent.group == "stripes"
    assert game.current_player is shooter
    shooter_spoken = [message.lower() for message in shooter_user.get_spoken_messages()]
    opponent_spoken = [message.lower() for message in opponent_user.get_spoken_messages()]
    assert any("you are assigned solids" in message for message in shooter_spoken)
    assert any("player1 is assigned solids" in message for message in opponent_spoken)
    assert any("you pocketed: 1" in message for message in shooter_spoken)
    assert any("you pocketed a legal ball and continue" in message for message in shooter_spoken)


def test_non_break_shot_requires_a_called_ball_and_pocket() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    game.get_user(shooter).clear_messages()
    game._action_shoot(shooter)
    assert game.pending_shot is None
    assert "call a ball" in game.get_user(shooter).get_last_spoken().lower()


def test_rejected_shot_stays_on_human_turn_and_never_starts_bot() -> None:
    game = make_game(bot_second=True, start=True)
    shooter = game.current_player
    bot = game._opponent(shooter)
    assert isinstance(shooter, EightBallPlayer)
    assert isinstance(bot, EightBallPlayer) and bot.is_bot
    game.break_shot = False
    bot.bot_pending_action = None
    bot.bot_think_ticks = 0
    game._action_shoot(shooter)
    assert game.current_player is shooter
    game.on_tick()
    assert bot.bot_pending_action is None
    spoken = game.get_user(shooter).get_spoken_messages()
    assert any("call a ball" in message.lower() for message in spoken)
    assert not any("calculat" in message.lower() for message in spoken)


def test_physical_foul_announces_invalid_before_bot_turn_without_calculation_message() -> None:
    game = make_game(bot_second=True, start=True)
    shooter = game.current_player
    bot = game._opponent(shooter)
    assert isinstance(shooter, EightBallPlayer)
    assert isinstance(bot, EightBallPlayer) and bot.is_bot
    user = game.get_user(shooter)
    user.clear_messages()
    game.break_shot = False
    game.shot_player_id = shooter.id
    game.shot_was_break = False
    game.shot_group_before = ""
    game.shot_remaining_before = 7
    game.pending_shot = ShotResult(balls=build_rack(), first_contact=-1)
    game._resolve_shot()
    assert game.current_player is bot
    spoken = user.get_spoken_messages()
    invalid_index = next(
        i for i, message in enumerate(spoken) if "did not contact" in message.lower()
    )
    turn_index = next(i for i, message in enumerate(spoken) if "bot" in message.lower() and "turn" in message.lower())
    assert invalid_index < turn_index
    assert not any("calculat" in message.lower() for message in spoken)


def test_foul_announces_only_the_group_balls_still_on_the_table() -> None:
    game = make_game(start=True, language="pt")
    shooter = game.current_player
    opponent = game._opponent(shooter)
    assert isinstance(shooter, EightBallPlayer)
    assert isinstance(opponent, EightBallPlayer)
    shooter.group = GROUP_SOLIDS
    opponent.group = GROUP_STRIPES
    game.table_open = False
    game.break_shot = False
    for number in (1, 2, 3):
        ball = game._ball(number)
        assert ball is not None
        ball.potted = True
    user = game.get_user(shooter)
    assert isinstance(user, MockUser)
    user.clear_messages()

    game._announce_foul_reasons(
        shooter,
        ShotResult(first_contact=9, rail_after_contact=True),
        {4, 5, 6, 7},
        [],
        was_break=False,
    )

    spoken = user.get_spoken_messages()
    remaining = next(message for message in spoken if "ainda restam" in message.lower())
    assert "4, 5, 6, 7" in remaining
    assert "1, 2, 3" not in remaining


def test_shot_snapshot_excludes_group_balls_potted_before_the_shot() -> None:
    game = make_game(start=True)
    game.shot_group_before = GROUP_SOLIDS
    game.shot_remaining_before = 4
    game.shot_legal_targets_before = [4, 5, 6, 7]
    assert game._legal_targets_from_snapshot() == {4, 5, 6, 7}


def test_b_calls_focused_ball_once_and_p_opens_six_pockets() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False

    focused_ball = shooter.focused_ball
    assert focused_ball in game._legal_targets(shooter)
    game.handle_event(shooter, {"type": "keybind", "key": "b"})
    assert shooter.called_ball == focused_ball
    assert shooter.id not in game._pending_actions

    game.handle_event(shooter, {"type": "keybind", "key": "p"})
    assert game._pending_actions[shooter.id] == "call_pocket"
    assert len(game._call_pocket_options(shooter)) == 6
    label = game._call_pocket_label(shooter, "0").lower()
    assert "pocket 1" in label
    assert "distance" in label
    assert f"ball {focused_ball}" in label
    game.handle_event(shooter, {
        "type": "menu", "menu_id": "action_input_menu", "selection_id": "0",
    })
    assert shooter.called_pocket == 0
    assert shooter.id not in game._pending_actions


def test_m_opens_ball_list_without_calling_and_shift_m_cycles_focus() -> None:
    game = make_game(start=True, language="pt")
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    shooter.called_ball = -1

    game.handle_event(shooter, {"type": "keybind", "key": "m"})
    assert game._pending_actions[shooter.id] == "locate_ball"
    options = game._locate_ball_options(shooter)
    assert len(options) == 15
    selected = options[5]
    game.handle_event(shooter, {
        "type": "menu", "menu_id": "action_input_menu", "selection_id": selected,
    })

    ball = game._ball(int(selected))
    assert ball is not None
    assert (shooter.cursor_x, shooter.cursor_y) == (ball.x, ball.y)
    assert shooter.focused_ball == int(selected)
    assert shooter.called_ball == -1
    assert "pressione b" in game.get_user(shooter).get_last_spoken().lower()

    game.handle_event(shooter, {"type": "keybind", "key": "shift+m"})
    assert shooter.focused_ball == int(options[(options.index(selected) + 1) % len(options)])


def test_same_ball_keeps_an_audio_landmark_when_focus_is_rechecked() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    user = game.get_user(shooter)
    assert isinstance(user, MockUser)
    game.balls = [Ball(0, 20.0, 0.0), Ball(1, 0.0, 0.0)]
    shooter.cursor_x = 0.0
    shooter.cursor_y = 0.0
    shooter.focused_ball = -1
    user.clear_messages()

    game._update_spatial_focus(shooter)
    game._update_spatial_focus(shooter)

    assert len([
        sound for sound in user.get_sounds_played()
        if sound.endswith("collision.ogg")
    ]) == 2
    assert sum(
        "ball 1" in message.lower() for message in user.get_spoken_messages()
    ) == 1


def test_pocket_information_is_one_relative_reading_at_a_time() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    user = game.get_user(shooter)
    user.clear_messages()
    game._action_pockets_info(shooter)
    spoken = user.get_spoken_messages()
    assert len(spoken) == 1
    assert "pocket" in spoken[0].lower()
    assert "distance" in spoken[0].lower()
    assert "degree" not in spoken[0].lower()
    assert ";" not in spoken[0]


def test_pocket_at_cursor_does_not_invent_direction_or_zero_distance() -> None:
    game = make_game(start=True, language="pt")
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    user = game.get_user(shooter)
    assert isinstance(user, MockUser)
    shooter.called_pocket = 4
    shooter.cursor_x, shooter.cursor_y = POCKETS[4]
    user.clear_messages()

    game._action_pockets_info(shooter)

    assert user.get_last_spoken() == "Caçapa 5 cantada: você está na caçapa."


def test_pocket_less_than_one_away_never_reports_zero() -> None:
    game = make_game(start=True, language="pt")
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    user = game.get_user(shooter)
    assert isinstance(user, MockUser)
    shooter.called_pocket = 4
    shooter.cursor_x = POCKETS[4][0] + 0.2
    shooter.cursor_y = POCKETS[4][1]
    user.clear_messages()

    game._action_pockets_info(shooter)

    spoken = user.get_last_spoken()
    assert "a menos de 1 de distância" in spoken
    assert "distância 0" not in spoken


def test_movement_snaps_to_called_pocket_instead_of_oscillating_around_it() -> None:
    game = make_game(start=True, language="pt", table_size="7ft")
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    target_x, target_y = game._pockets[0]
    shooter.called_pocket = 0
    shooter.cursor_x = target_x + 0.8
    shooter.cursor_y = target_y + 0.4
    shooter.aim_angle = 180.0
    user = game.get_user(shooter)
    user.clear_messages()

    game._walk(shooter, 1.0)

    assert (shooter.cursor_x, shooter.cursor_y) == (target_x, target_y)
    assert "você está na caçapa" in user.get_last_spoken().lower()


def test_calling_pocket_menu_uses_ball_distance_without_changing_heading() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    shooter.called_ball = 1
    ball = game._ball(1)
    assert ball is not None
    shooter.cursor_x, shooter.cursor_y = ball.x, ball.y
    shooter.aim_angle = math.degrees(math.atan2(25.0 - ball.y, -50.0 - ball.x)) % 360.0
    heading = shooter.aim_angle
    user = game.get_user(shooter)
    user.clear_messages()
    assert "distance" in game._call_pocket_label(shooter, "0").lower()
    game._action_call_pocket(shooter, "0", "call_pocket")
    assert shooter.called_pocket == 0
    assert shooter.aim_angle == heading
    spoken = [message.lower() for message in user.get_spoken_messages()]
    assert any("pocket 1 called" in message for message in spoken)
    assert any("degrees" in message or "ahead." in message for message in spoken)
    user.clear_messages()
    game._action_pockets_info(shooter)
    assert "pocket 1 called" in user.get_last_spoken().lower()


def test_elevated_cue_shot_has_real_vertical_motion() -> None:
    result = simulate_shot([Ball(0, 0.0, 0.0)], 0.0, 70, elevation_degrees=35)
    assert any(event.kind == "land" for event in result.events)
    assert all(ball.z == 0.0 for ball in result.balls)


def test_power_changes_speak_force_while_shooting_does_not() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    user = game.get_user(shooter)
    user.clear_messages()
    game._action_power_up(shooter)
    assert user.get_spoken_messages() == ["Power: 60 percent."]
    shooter.power = 100
    game._action_power_up(shooter)
    assert shooter.power == 100


def test_invalid_pocket_selection_explains_the_exact_problem() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    user = game.get_user(shooter)
    assert user is not None
    user.clear_messages()
    game._action_call_pocket(shooter, "not-a-pocket", "call_pocket")
    assert "does not exist" in user.get_last_spoken().lower()


def test_completed_shot_resets_advanced_cue_settings() -> None:
    player = EightBallPlayer(id="p1", name="Player1")
    player.called_ball = 3
    player.called_pocket = 2
    player.safety = True
    player.spin = 2
    player.side_spin = -2
    player.cue_elevation = 35
    EightBallGame._clear_call(player)
    assert player.called_ball == player.called_pocket == -1
    assert not player.safety
    assert player.spin == player.side_spin == player.cue_elevation == 0


def test_ctrl_aim_reports_exact_error_and_ahead_for_called_shot() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    game.balls = [Ball(0, 20.0, 0.0), Ball(1, 0.0, 0.0)]
    shooter.called_ball = 1
    shooter.called_pocket = 0
    pocket_x, pocket_y = game.balls[1].x, game.balls[1].y
    target_x, target_y = game._pocket_aim_points[0]
    length = math.hypot(target_x - pocket_x, target_y - pocket_y)
    ghost_x = pocket_x - (target_x - pocket_x) / length * BALL_RADIUS * 2.0
    ghost_y = pocket_y - (target_y - pocket_y) / length * BALL_RADIUS * 2.0
    required = math.degrees(math.atan2(ghost_y, ghost_x - 20.0)) % 360.0
    shooter.aim_angle = round((required - 3.0) % 360.0, 1)
    user = game.get_user(shooter)
    user.clear_messages()
    game._action_turn_left_fine(shooter)
    assert "2 degrees left" in user.get_last_spoken().lower()
    game._action_turn_left_fine(shooter)
    assert "1 degree left" in user.get_last_spoken().lower()
    game._action_turn_left_fine(shooter)
    assert user.get_last_spoken().lower().startswith("ball 1, ahead.")
    assert abs(shooter.aim_angle - required) < 0.001


def test_aligned_called_shot_reports_calculated_minimum_power() -> None:
    game = make_game(start=True, language="pt")
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    game.balls = [Ball(0, 20.0, 0.0), Ball(1, 0.0, 0.0)]
    shooter.called_ball = 1
    shooter.called_pocket = 0
    pocket_x, pocket_y = game._pocket_aim_points[0]
    length = math.hypot(pocket_x, pocket_y)
    ghost_x = -(pocket_x / length) * BALL_RADIUS * 2.0
    ghost_y = -(pocket_y / length) * BALL_RADIUS * 2.0
    shooter.aim_angle = math.degrees(
        math.atan2(ghost_y, ghost_x - 20.0)
    ) % 360.0
    user = game.get_user(shooter)
    assert isinstance(user, MockUser)
    user.clear_messages()

    game._announce_aim_feedback(shooter)

    assert "mínimo para alcançar a caçapa" in user.get_last_spoken().lower()
    minimum = game._minimum_direct_power(shooter, require_aligned=True)
    assert minimum is not None and minimum > 10
    below = simulate_shot(game.balls, shooter.aim_angle, minimum - 5)
    at_minimum = simulate_shot(game.balls, shooter.aim_angle, minimum)
    below_target = next(ball for ball in below.balls if ball.number == 1)
    minimum_target = next(ball for ball in at_minimum.balls if ball.number == 1)
    assert not below_target.potted
    assert minimum_target.potted and minimum_target.pocket_potted == 0
    shooter.power = minimum - 5
    game._power_feedback(shooter)
    assert "insuficiente" in user.get_last_spoken().lower()
    shooter.power = minimum
    game._power_feedback(shooter)
    assert "suficiente" in user.get_last_spoken().lower()
    preview = game._preview_shot(shooter, minimum)
    game._action_shoot(shooter)
    assert game.pending_shot is preview
    resolved_target = next(ball for ball in preview.balls if ball.number == 1)
    assert resolved_target.potted and resolved_target.pocket_potted == 0


def test_force_minimum_is_simulation_confirmed_for_corner_and_side_pockets_on_every_table() -> None:
    for table_size in TABLE_SIZES:
        for pocket, cue_position in ((0, (20.0, 0.0)), (1, (0.0, -20.0))):
            game = make_game(start=True, table_size=table_size)
            shooter = game.current_player
            assert isinstance(shooter, EightBallPlayer)
            cue_x, cue_y = cue_position
            game.break_shot = False
            game.balls = [Ball(0, cue_x, cue_y), Ball(1, 0.0, 0.0)]
            shooter.called_ball = 1
            shooter.called_pocket = pocket
            pocket_x, pocket_y = game._pocket_aim_points[pocket]
            length = math.hypot(pocket_x, pocket_y)
            ghost_x = -(pocket_x / length) * BALL_RADIUS * 2.0
            ghost_y = -(pocket_y / length) * BALL_RADIUS * 2.0
            shooter.aim_angle = math.degrees(
                math.atan2(ghost_y - cue_y, ghost_x - cue_x)
            ) % 360.0

            minimum = game._minimum_direct_power(shooter, require_aligned=True)

            assert minimum is not None
            confirmed = simulate_shot(
                game.balls, shooter.aim_angle, minimum, table_size=table_size,
            )
            confirmed_target = next(ball for ball in confirmed.balls if ball.number == 1)
            assert confirmed_target.potted and confirmed_target.pocket_potted == pocket
            if minimum > 10:
                below = simulate_shot(
                    game.balls, shooter.aim_angle, minimum - 5,
                    table_size=table_size,
                )
                below_target = next(ball for ball in below.balls if ball.number == 1)
                assert not below_target.potted


def test_disabled_power_assistance_only_reports_selected_percentage() -> None:
    game = make_game(start=True, language="pt", power_assistance=False)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    game.balls = [Ball(0, 20.0, 0.0), Ball(1, 0.0, 0.0)]
    shooter.called_ball = 1
    shooter.called_pocket = 0
    pocket_x, pocket_y = game._pocket_aim_points[0]
    length = math.hypot(pocket_x, pocket_y)
    ghost_x = -(pocket_x / length) * BALL_RADIUS * 2.0
    ghost_y = -(pocket_y / length) * BALL_RADIUS * 2.0
    shooter.aim_angle = math.degrees(math.atan2(ghost_y, ghost_x - 20.0)) % 360.0
    shooter.power = 35
    user = game.get_user(shooter)
    assert isinstance(user, MockUser)

    user.clear_messages()
    game._power_feedback(shooter)
    spoken = user.get_last_spoken().lower()
    assert "força: 35 por cento" in spoken
    assert "suficiente" not in spoken
    assert "mínimo" not in spoken

    user.clear_messages()
    game._announce_aim_feedback(shooter)
    assert user.get_last_spoken().lower() == "à frente."


def test_power_assistance_explains_when_side_spin_prevents_a_safe_prediction() -> None:
    game = make_game(start=True, language="pt", power_assistance=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    game.balls = [Ball(0, 20.0, 0.0), Ball(1, 0.0, 0.0)]
    shooter.called_ball = 1
    shooter.called_pocket = 0
    pocket_x, pocket_y = game._pocket_aim_points[0]
    length = math.hypot(pocket_x, pocket_y)
    ghost_x = -(pocket_x / length) * BALL_RADIUS * 2.0
    ghost_y = -(pocket_y / length) * BALL_RADIUS * 2.0
    shooter.aim_angle = math.degrees(
        math.atan2(ghost_y, ghost_x - 20.0)
    ) % 360.0
    shooter.side_spin = 1
    user = game.get_user(shooter)
    assert isinstance(user, MockUser)
    user.clear_messages()

    game._announce_aim_feedback(shooter)

    spoken = user.get_last_spoken().lower()
    assert "à frente" in spoken
    assert "efeito lateral" in spoken
    assert "indisponível" in spoken


def test_aligned_help_names_the_ball_and_reports_reach_power_when_pot_is_unconfirmed() -> None:
    game = make_game(start=True, language="pt", power_assistance=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    game.balls = [Ball(0, 20.0, 0.0), Ball(1, 0.0, 0.0)]
    shooter.called_ball = 1
    shooter.called_pocket = 0
    pocket_x, pocket_y = game._pocket_aim_points[0]
    length = math.hypot(pocket_x, pocket_y)
    ghost_x = -(pocket_x / length) * BALL_RADIUS * 2.0
    ghost_y = -(pocket_y / length) * BALL_RADIUS * 2.0
    shooter.aim_angle = math.degrees(
        math.atan2(ghost_y, ghost_x - 20.0)
    ) % 360.0
    user = game.get_user(shooter)
    assert isinstance(user, MockUser)
    user.clear_messages()

    with patch.object(
        game, "_called_ball_pots_in_direct_preview", return_value=False,
    ):
        game._announce_aim_feedback(shooter)

    spoken = user.get_last_spoken().lower()
    assert "bola 1" in spoken
    assert "mínimo para alcançar a caçapa" in spoken
    assert "não está confirmada" in spoken


def test_shift_arrows_turn_45_ctrl_shift_turns_ten_and_ctrl_turns_one() -> None:
    game = make_game(start=True, language="pt")
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    initial = shooter.aim_angle
    game._action_turn_left_fast(shooter)
    assert shooter.aim_angle == round((initial + 45.0) % 360.0, 1)
    game._action_turn_right_fast(shooter)
    assert shooter.aim_angle == initial
    game._action_turn_left_medium(shooter)
    assert shooter.aim_angle == round((initial + 10.0) % 360.0, 1)
    game._action_turn_right_medium(shooter)
    assert shooter.aim_angle == initial
    game._action_turn_left_fine(shooter)
    assert shooter.aim_angle == round((initial + 1.0) % 360.0, 1)
    assert game._keybinds["shift+left"][-1].name == "Girar 45 graus para a esquerda"
    assert game._keybinds["ctrl+shift+left"][-1].name == "Girar dez graus para a esquerda"


def test_arrow_aim_feedback_never_runs_a_full_physics_preview() -> None:
    game = make_game(start=True, language="pt", power_assistance=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    game.balls = [Ball(0, 20.0, 0.0), Ball(1, 0.0, 0.0)]
    shooter.called_ball = 1
    shooter.called_pocket = 0
    pocket_x, pocket_y = game._pocket_aim_points[0]
    length = math.hypot(pocket_x, pocket_y)
    ghost_x = -(pocket_x / length) * BALL_RADIUS * 2.0
    ghost_y = -(pocket_y / length) * BALL_RADIUS * 2.0
    shooter.aim_angle = math.degrees(
        math.atan2(ghost_y, ghost_x - 20.0)
    ) % 360.0

    with patch.object(
        game, "_called_ball_pots_in_direct_preview",
        side_effect=AssertionError("arrow aiming must not run a physics preview"),
    ):
        game._announce_aim_feedback(shooter)


def test_ctrl_aim_names_a_real_blocking_ball() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    target = Ball(1, 0.0, 0.0)
    pocket_x, pocket_y = -50.0, 25.0
    length = math.hypot(pocket_x - target.x, pocket_y - target.y)
    ghost_x = target.x - (pocket_x - target.x) / length * BALL_RADIUS * 2.0
    ghost_y = target.y - (pocket_y - target.y) / length * BALL_RADIUS * 2.0
    blocker = Ball(2, (20.0 + ghost_x) / 2.0, ghost_y / 2.0)
    game.balls = [Ball(0, 20.0, 0.0), target, blocker]
    shooter.called_ball = 1
    shooter.called_pocket = 0
    required = math.degrees(math.atan2(ghost_y, ghost_x - 20.0)) % 360.0
    shooter.aim_angle = round((required - 1.0) % 360.0, 1)
    user = game.get_user(shooter)
    user.clear_messages()
    game._action_turn_left_fine(shooter)
    assert "cue-ball path is blocked by ball 2" in user.get_last_spoken().lower()


def test_illegal_break_gives_the_incoming_player_all_three_official_choices() -> None:
    game = make_game(start=True)
    breaker = game.current_player
    incoming = game._opponent(breaker)
    assert isinstance(breaker, EightBallPlayer)
    assert isinstance(incoming, EightBallPlayer)
    game.shot_player_id = breaker.id
    game.shot_was_break = True
    game.pending_shot = ShotResult(
        balls=build_rack(), first_contact=1, rail_balls=[1, 2, 3]
    )
    game._resolve_shot()
    assert game.break_decision == "illegal"
    assert game.current_player is incoming
    assert game._break_decision_disabled(incoming, action_id="break_option_3") is None
    game._action_break_option_2(incoming)
    assert game.break_shot
    assert game.current_player is incoming


def test_eight_on_a_legal_break_can_be_spotted_and_play_continues() -> None:
    game = make_game(start=True)
    breaker = game.current_player
    assert isinstance(breaker, EightBallPlayer)
    balls = build_rack()
    eight = next(ball for ball in balls if ball.number == 8)
    eight.potted = True
    eight.pocket_potted = 0
    game.shot_player_id = breaker.id
    game.shot_was_break = True
    game.pending_shot = ShotResult(balls=balls, first_contact=1, potted=[8])
    game._resolve_shot()
    assert game.break_decision == "eight_legal"
    game._action_break_option_1(breaker)
    assert not game._ball(8).potted
    assert game.current_player is breaker


def test_break_foul_ball_in_hand_is_restricted_above_head_string() -> None:
    game = make_game(start=True)
    breaker = game.current_player
    incoming = game._opponent(breaker)
    assert isinstance(breaker, EightBallPlayer)
    assert isinstance(incoming, EightBallPlayer)
    balls = build_rack()
    next(ball for ball in balls if ball.number == 0).potted = True
    game.shot_player_id = breaker.id
    game.shot_was_break = True
    game.pending_shot = ShotResult(
        balls=balls, first_contact=1, potted=[0], cue_scratch=True, rail_balls=[1, 2, 3, 4]
    )
    game._resolve_shot()
    assert game.break_decision == "break_foul"
    game._action_break_option_2(incoming)
    assert game.ball_in_hand and game.ball_in_hand_head_string
    cue = game._ball(0)
    assert cue is not None and cue.x >= 25.0 + BALL_RADIUS


def test_scratch_passes_turn_and_grants_real_ball_in_hand() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    game.shot_player_id = shooter.id
    game.shot_group_before = ""
    game.shot_remaining_before = 7
    game.shot_was_break = False
    balls = build_rack()
    next(ball for ball in balls if ball.number == 0).potted = True
    game.pending_shot = ShotResult(
        balls=balls, first_contact=1, potted=[0], cue_scratch=True,
        rail_after_contact=True,
    )
    game._resolve_shot()
    assert game.current_player is not shooter
    assert game.ball_in_hand
    assert not game._ball(0).potted


def test_early_eight_ball_awards_frame_to_opponent() -> None:
    game = make_game(start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    opponent = game._opponent(shooter)
    assert opponent is not None
    shooter.group = "solids"
    opponent.group = "stripes"
    game.table_open = False
    game.break_shot = False
    game.shot_player_id = shooter.id
    game.shot_group_before = "solids"
    game.shot_remaining_before = 3
    game.shot_was_break = False
    balls = build_rack()
    next(ball for ball in balls if ball.number == 8).potted = True
    game.pending_shot = ShotResult(
        balls=balls, first_contact=8, potted=[8], rail_after_contact=True
    )
    game._resolve_shot()
    assert opponent.frames_won == 1


def test_pocketing_ball_nine_alone_never_ends_the_match() -> None:
    game = make_game(start=True, language="pt")
    shooter = game.current_player
    opponent = game._opponent(shooter)
    assert isinstance(shooter, EightBallPlayer)
    assert isinstance(opponent, EightBallPlayer)
    shooter.group = GROUP_STRIPES
    opponent.group = GROUP_SOLIDS
    game.table_open = False
    game.break_shot = False
    balls = build_rack()
    nine = next(ball for ball in balls if ball.number == 9)
    nine.potted = True
    nine.pocket_potted = 0
    shooter.called_ball = 9
    shooter.called_pocket = 0
    game.shot_player_id = shooter.id
    game.shot_group_before = GROUP_STRIPES
    game.shot_remaining_before = 7
    game.shot_was_break = False
    game.pending_shot = ShotResult(
        balls=balls, first_contact=9, potted=[9], rail_after_contact=False,
    )

    game._resolve_shot()

    assert game.status == "playing"
    assert game.winner_id == ""
    assert shooter.frames_won == opponent.frames_won == 0


def test_illegal_eight_with_another_ball_announces_both_before_the_winner() -> None:
    game = make_game(start=True, language="pt")
    shooter = game.current_player
    opponent = game._opponent(shooter)
    assert isinstance(shooter, EightBallPlayer)
    assert isinstance(opponent, EightBallPlayer)
    shooter.group = GROUP_STRIPES
    opponent.group = GROUP_SOLIDS
    game.table_open = False
    game.break_shot = False
    balls = build_rack()
    for number in (9, 8):
        ball = next(item for item in balls if item.number == number)
        ball.potted = True
        ball.pocket_potted = 0
    shooter.called_ball = 9
    shooter.called_pocket = 0
    game.shot_player_id = shooter.id
    game.shot_group_before = GROUP_STRIPES
    game.shot_remaining_before = 7
    game.shot_was_break = False
    game.pending_shot = ShotResult(
        balls=balls, first_contact=9, potted=[9, 8], rail_after_contact=False,
    )
    shooter_user = game.get_user(shooter)
    assert isinstance(shooter_user, MockUser)
    shooter_user.clear_messages()

    game._resolve_shot()

    spoken = [message.lower() for message in shooter_user.get_spoken_messages()]
    pots_index = next(
        index for index, message in enumerate(spoken)
        if "você encaçapou: 9, 8" in message
    )
    illegal_index = next(
        index for index, message in enumerate(spoken)
        if "bola 8 ilegalmente" in message
    )
    winner_index = next(
        index for index, message in enumerate(spoken)
        if opponent.name.lower() in message and "venceu" in message
    )
    assert pots_index < illegal_index < winner_index
    assert game.winner_id == opponent.id
    assert game.winner_id == opponent.id
    assert game.status == "finished"


def test_native_bot_helper_drives_bot_turn() -> None:
    game = make_game(bot_second=True, start=True)
    game.advance_turn(announce=False)
    bot = game.current_player
    assert isinstance(bot, EightBallPlayer) and bot.is_bot
    bot.bot_think_ticks = 0
    game.on_tick()
    assert bot.bot_pending_action == "shoot"
    game.on_tick()
    assert game.has_active_sequence(sequence_id="eightball-shot")


def test_state_round_trip_includes_physics_state() -> None:
    game = make_game(start=True)
    restored = EightBallGame.from_json(game.to_json())
    assert restored.balls == game.balls
    assert restored.options.frames_to_win == game.options.frames_to_win


def test_real_pool_sounds_match_every_client_pack() -> None:
    root = Path(__file__).parents[2]
    names = ("cue.ogg", "collision.ogg", "rail.ogg", "pocket.ogg")
    packs = ("client", "web_client", "mobile_client")
    for name in names:
        payloads = [
            (root / pack / "sounds" / "game_eightball" / name).read_bytes()
            for pack in packs
        ]
        assert payloads[0]
        assert payloads[0] == payloads[1] == payloads[2]


def test_table_language_controls_messages_for_every_player() -> None:
    game = make_game(language="es")
    player = game.get_active_players()[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game._speak_personal(player, "eightball-power-level", power=60)
    assert user.get_last_spoken() == "Fuerza: 60 por ciento."


def test_portuguese_is_available_as_a_table_language() -> None:
    assert "pt" in TABLE_LANGUAGES
    game = make_game(language="pt")
    player = game.get_active_players()[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.clear_messages()
    game._speak_personal(player, "eightball-power-level", power=60)
    assert user.get_last_spoken() == "Força: 60 por cento."


def test_changing_table_language_rebuilds_actions_and_keybind_names() -> None:
    game = make_game(language="en")
    player = game.get_active_players()[0]
    assert game.find_action(player, "shoot").label == "Shoot or confirm cue-ball placement"
    assert game._keybinds["x"][-1].name == "Increase shot power"

    game._handle_option_change("table_language", "pt")

    assert game.find_action(player, "shoot").label == "Dar tacada ou confirmar a posição da bola branca"
    assert game._keybinds["x"][-1].name == "Aumentar a força"
    assert game._keybinds["l"][-1].name == "Sondar a linha de mira"


def test_setting_up_keybinds_again_does_not_duplicate_help_entries() -> None:
    game = make_game(language="pt")
    game.setup_keybinds()
    assert len(game._keybinds["space"]) == 1
    assert len(game._keybinds["x"]) == 1
    assert len(game._keybinds["l"]) == 1


def test_physics_playback_is_compressed_without_changing_result() -> None:
    result = ShotResult(
        events=[
            PhysicsEvent(0, "cue", 0.0, 0.0),
            PhysicsEvent(10, "rail", 1.0, 0.0),
        ],
        duration_ticks=20,
    )
    beats = EightBallGame._physics_sequence_beats(result)
    assert PHYSICS_PLAYBACK_RATE == 3.0
    assert sum(beat.delay_after_ticks for beat in beats) == 7
    assert result.duration_ticks == 20


def test_doubles_preserves_host_arrangement_and_alternates_partners() -> None:
    game = make_game(player_count=4, mode=MODE_DOUBLES)
    game._begin_team_arrangement()
    assert game.team_manager.swap_members("Player3", "Player4")
    game.on_start()
    assert game.team_manager.get_team("Player1") is game.team_manager.get_team("Player4")
    assert game.team_manager.get_team("Player2") is game.team_manager.get_team("Player3")
    assert [player.name for player in game.turn_players] == [
        "Player1", "Player2", "Player4", "Player3",
    ]
    game.lag_active = False
    game.lag_break_choice_pending = False
    game.breaker_index = 0
    game._start_frame()
    shooter = game.current_player
    assert shooter is not None and shooter.name == "Player1"
    game._continue_or_pass(
        shooter, [1], False, was_break=True, called_made=False
    )
    assert game.current_player is not None and game.current_player.name == "Player4"


def test_cutthroat_assigns_three_published_groups_and_needs_no_call() -> None:
    game = make_game(player_count=5, mode=MODE_CUTTHROAT, start=True)
    assert [player.protected_balls for player in game.turn_players] == [
        [1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15],
    ]
    first_user = game.get_user(game.turn_players[0])
    second_user = game.get_user(game.turn_players[1])
    assert isinstance(first_user, MockUser)
    assert isinstance(second_user, MockUser)
    assert any(
        "you protect balls 1, 2, 3" in message.lower()
        for message in first_user.get_spoken_messages()
    )
    assert any(
        "player1 protects balls 1, 2, 3" in message.lower()
        for message in second_user.get_spoken_messages()
    )
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    assert game._call_disabled(shooter) == "eightball-cutthroat-no-call"
    game._action_shoot(shooter)
    assert game.pending_shot is not None


def test_cutthroat_foul_restores_illegal_ball_and_one_penalty_ball() -> None:
    game = make_game(player_count=5, mode=MODE_CUTTHROAT, start=True)
    shooter = game.current_player
    assert isinstance(shooter, EightBallPlayer)
    game.break_shot = False
    balls = build_cutthroat_rack()
    four = next(ball for ball in balls if ball.number == 4)
    five = next(ball for ball in balls if ball.number == 5)
    four.potted = True
    five.potted = True
    five.pocket_potted = 0
    game.shot_player_id = shooter.id
    game.shot_was_break = False
    game.pending_shot = ShotResult(
        balls=balls, first_contact=1, potted=[5], rail_after_contact=True
    )
    game._resolve_shot()
    assert not game._ball(4).potted
    assert not game._ball(5).potted
    assert game.current_player is not shooter


def test_cutthroat_eliminated_player_returns_after_ball_is_restored() -> None:
    game = make_game(player_count=5, mode=MODE_CUTTHROAT, start=True)
    player = game.turn_players[1]
    for number in player.protected_balls:
        game._ball(number).potted = True
    game._refresh_cutthroat_eliminations()
    assert player.id in game.cutthroat_eliminated_ids
    assert player.id in game.cutthroat_elimination_order
    game._spot_number(player.protected_balls[0])
    game._refresh_cutthroat_eliminations()
    assert player.id not in game.cutthroat_eliminated_ids
    assert player.id not in game.cutthroat_elimination_order
