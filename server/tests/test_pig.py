"""Tests for the Pig game."""

import json
from pathlib import Path
import random
import re
from unittest.mock import patch

from ..games.pig.game import (
    DEFAULT_TARGET_SCORE,
    RISK_CONFIRM_TICKS,
    ROLL_SEQUENCE_ID,
    PigGame,
    PigOptions,
    PigPlayer,
)
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from ..ui.keybinds import KeybindState
from ..users.bot import Bot
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(
    *,
    player_count: int = 2,
    start: bool = False,
    bot_all: bool = False,
    mobile_first: bool = False,
    **option_overrides,
) -> PigGame:
    game = PigGame(options=PigOptions(**option_overrides))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        if bot_all:
            user = Bot(name, uuid=f"p{index + 1}")
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
            if mobile_first and index == 0:
                user.client_type = "mobile"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
    return game


def advance_until(game: PigGame, condition, max_ticks: int = 500) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def resolve_roll(game: PigGame) -> None:
    assert advance_until(
        game,
        lambda: not game.has_active_sequence(sequence_id=ROLL_SEQUENCE_ID),
    )


def test_game_registered_defaults_and_metadata() -> None:
    assert GameRegistry.get("pig") is PigGame
    game = PigGame()
    assert game.get_name() == "Pig"
    assert game.get_type() == "pig"
    assert game.get_category() == "dice"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 6
    assert game.get_supported_leaderboards() == [
        "wins",
        "total_score",
        "high_score",
        "rating",
        "games_played",
    ]
    assert game.relevant_preferences == [
        "brief_announcements",
        "confirm_destructive_actions",
    ]
    assert game.options.target_score == DEFAULT_TARGET_SCORE == 100
    assert game.options.min_bank_points == 0
    assert game.options.dice_sides == 6
    assert game.options.team_mode == "individual"


def test_player_state_and_full_game_state_serialize() -> None:
    game = make_game(start=True, min_bank_points=5)
    player = game.players[0]
    assert isinstance(player, PigPlayer)
    player.round_score = 12
    player.pending_risky_action = "roll:3:40:12:6"
    player.risky_confirm_ticks = 9
    game.round = 3
    game.winner_team_index = 1
    game._team_manager.teams[0].total_score = 40

    data = json.loads(game.to_json())
    assert data["round"] == 3
    assert data["winner_team_index"] == 1
    assert data["players"][0]["round_score"] == 12
    assert data["players"][0]["pending_risky_action"] == "roll:3:40:12:6"

    loaded = PigGame.from_json(game.to_json())
    assert loaded.round == 3
    assert loaded.winner_team_index == 1
    assert loaded.options.min_bank_points == 5
    assert loaded.players[0].round_score == 12
    assert loaded.players[0].risky_confirm_ticks == 9
    assert loaded.get_player_score(loaded.players[0]) == 40


def test_prestart_validation_reports_every_invalid_setting_with_context() -> None:
    game = make_game(
        player_count=3,
        target_score=9,
        min_bank_points=1000,
        dice_sides=3,
        team_mode="2v2",
    )

    errors = game.prestart_validate()
    assert "game-error-invalid-team-mode" in errors
    assert (
        "pig-error-target-out-of-range",
        {"value": 9, "min": 10, "max": 1000},
    ) in errors
    assert (
        "pig-error-min-bank-out-of-range",
        {"value": 1000, "min": 0, "max": 999},
    ) in errors
    assert (
        "pig-error-dice-sides-out-of-range",
        {"value": 3, "min": 4, "max": 20},
    ) in errors
    assert (
        "pig-error-min-bank-too-high",
        {"minimum": 1000, "target": 9},
    ) in errors


def test_minimum_hold_must_be_lower_than_target() -> None:
    game = make_game(target_score=50, min_bank_points=50)
    assert (
        "pig-error-min-bank-too-high",
        {"minimum": 50, "target": 50},
    ) in game.prestart_validate()


def test_hold_stays_visible_as_a_disabled_focus_anchor() -> None:
    game = make_game(start=True)
    current = game.players[0]
    waiting = game.players[1]

    current_actions = {
        action.action.id: action for action in game.get_all_visible_actions(current)
    }
    waiting_actions = {
        action.action.id: action for action in game.get_all_visible_actions(waiting)
    }

    assert current_actions["bank"].enabled is False
    assert current_actions["bank"].disabled_reason == "pig-no-turn-points"
    assert waiting_actions["roll"].enabled is False
    assert waiting_actions["bank"].enabled is False
    assert waiting_actions["bank"].disabled_reason == "action-not-your-turn"


def test_minimum_hold_disabled_reason_is_contextual() -> None:
    game = make_game(start=True, min_bank_points=10)
    player = game.players[0]
    player.round_score = 6

    hold = {
        action.action.id: action for action in game.get_all_visible_actions(player)
    }["bank"]
    assert hold.enabled is False
    assert hold.disabled_reason == (
        "pig-need-more-points",
        {"current": 6, "required": 10},
    )


def test_roll_sequence_locks_actions_and_resolves_with_personal_perspective() -> None:
    game = make_game(start=True)
    actor = game.players[0]
    observer = game.players[1]
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_user.clear_messages()
    observer_user.clear_messages()

    with patch("server.games.pig.game.random.randint", return_value=4):
        game.execute_action(actor, "roll")

    assert game.has_active_sequence(sequence_id=ROLL_SEQUENCE_ID)
    assert actor.round_score == 0
    roll_action = {
        action.action.id: action for action in game.get_all_visible_actions(actor)
    }["roll"]
    assert roll_action.enabled is False
    assert roll_action.disabled_reason == "pig-action-resolving"

    resolve_roll(game)
    assert actor.round_score == 4
    assert actor_user.get_last_spoken() == Localization.get(
        "en", "pig-you-roll-result", roll=4, total=4
    )
    assert observer_user.get_last_spoken() == Localization.get(
        "en", "pig-player-roll-result", player=actor.name, roll=4, total=4
    )


def test_brief_announcements_are_per_listener() -> None:
    game = make_game(start=True)
    actor = game.players[0]
    observer = game.players[1]
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_user.preferences.brief_announcements = True
    actor_user.clear_messages()
    observer_user.clear_messages()

    with patch("server.games.pig.game.random.randint", return_value=5):
        game.execute_action(actor, "roll")
    resolve_roll(game)

    assert actor_user.get_last_spoken() == Localization.get(
        "en", "pig-you-roll-result-brief", roll=5, total=5
    )
    assert observer_user.get_last_spoken() == Localization.get(
        "en", "pig-player-roll-result", player=actor.name, roll=5, total=5
    )


def test_rolling_one_loses_turn_total_and_advances() -> None:
    game = make_game(start=True)
    actor = game.players[0]
    observer = game.players[1]
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor.round_score = 15
    actor_user.clear_messages()
    observer_user.clear_messages()

    with patch("server.games.pig.game.random.randint", return_value=1):
        game.execute_action(actor, "roll")
    resolve_roll(game)

    assert actor.round_score == 0
    assert game.current_player is observer
    assert Localization.get("en", "pig-you-bust", points=15) in (
        actor_user.get_spoken_messages()
    )
    assert Localization.get(
        "en", "pig-player-busts", player=actor.name, points=15
    ) in observer_user.get_spoken_messages()


def test_holding_scores_points_and_advances() -> None:
    game = make_game(start=True)
    actor = game.players[0]
    next_player = game.players[1]
    game._team_manager.add_to_team_score(actor.name, 10)
    actor.round_score = 20

    game.execute_action(actor, "bank")

    assert game.get_player_score(actor) == 30
    assert actor.round_score == 0
    assert game.current_player is next_player


def test_holding_target_score_wins_immediately() -> None:
    game = make_game(start=True, target_score=10)
    actor = game.players[0]
    game._team_manager.add_to_team_score(actor.name, 8)
    actor.round_score = 2

    game.execute_action(actor, "bank")

    assert game.status == "finished"
    assert not game.game_active
    assert game.winner_team_index == game._team_manager.get_team(actor.name).index
    assert game._last_game_result.custom_data["winner_ids"] == [actor.id]
    assert game._last_game_result.custom_data["winner_score"] == 10


def test_team_member_can_secure_immediate_team_victory() -> None:
    game = make_game(player_count=4, start=True, target_score=100, team_mode="2v2")
    actor = game.players[0]
    winning_team = game._team_manager.get_team(actor.name)
    assert winning_team is not None
    winning_team.total_score = 95
    actor.round_score = 5

    game.execute_action(actor, "bank")

    assert game.status == "finished"
    result = game._last_game_result
    expected_ids = {
        player.id for player in game.players if player.name in winning_team.members
    }
    assert set(result.custom_data["winner_ids"]) == expected_ids
    assert len(result.player_results) == 4


def test_team_hold_name_is_localized_per_listener() -> None:
    game = PigGame(options=PigOptions(team_mode="2v2"))
    game.setup_keybinds()
    users = [
        MockUser("Player1", locale="en", uuid="p1"),
        MockUser("Player2", locale="vi", uuid="p2"),
        MockUser("Player3", locale="en", uuid="p3"),
        MockUser("Player4", locale="en", uuid="p4"),
    ]
    for user in users:
        game.add_player(user.username, user)
    game.host = "Player1"
    game.on_start()
    actor = game.players[0]
    actor.round_score = 10
    users[1].clear_messages()

    game.execute_action(actor, "bank")

    team = game._team_manager.get_team(actor.name)
    assert team is not None
    assert Localization.get(
        "vi",
        "pig-player-holds",
        player=actor.name,
        points=10,
        total=10,
        team="yes",
        team_name=game._team_manager.get_team_name(team, "vi"),
    ) in users[1].get_spoken_messages()


def test_legacy_tiebreaker_save_finishes_and_restores_original_players() -> None:
    game = make_game(start=True, target_score=20)
    game._team_manager.teams[0].total_score = 20
    game.players[1].is_spectator = True

    game.on_tick()

    assert game.status == "finished"
    assert game.players[1].is_spectator is False
    assert len(game._last_game_result.player_results) == 2


def test_risky_roll_requires_second_press_when_enabled() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.preferences.confirm_destructive_actions = True
    player.round_score = game._expected_hold_threshold()
    user.clear_messages()

    game.execute_action(player, "roll")

    assert not game.has_active_sequence(sequence_id=ROLL_SEQUENCE_ID)
    assert player.pending_risky_action
    assert player.risky_confirm_ticks == RISK_CONFIRM_TICKS
    assert "Press Roll again" in user.get_last_spoken()

    with patch("server.games.pig.game.random.randint", return_value=4):
        game.execute_action(player, "roll")

    assert game.has_active_sequence(sequence_id=ROLL_SEQUENCE_ID)
    assert player.pending_risky_action == ""


def test_winning_hold_is_confirmed_even_below_normal_risk_threshold() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.preferences.confirm_destructive_actions = True
    game._team_manager.get_team(player.name).total_score = 95
    player.round_score = 5

    game.execute_action(player, "roll")

    assert not game.has_active_sequence(sequence_id=ROLL_SEQUENCE_ID)
    assert "win the game" in user.get_last_spoken()


def test_risky_confirmation_can_be_disabled_and_expires() -> None:
    disabled_game = make_game(start=True)
    disabled_player = disabled_game.players[0]
    disabled_user = disabled_game.get_user(disabled_player)
    assert isinstance(disabled_user, MockUser)
    disabled_user.preferences.confirm_destructive_actions = False
    disabled_player.round_score = disabled_game._expected_hold_threshold()

    with patch("server.games.pig.game.random.randint", return_value=3):
        disabled_game.execute_action(disabled_player, "roll")
    assert disabled_game.has_active_sequence(sequence_id=ROLL_SEQUENCE_ID)

    expiring_game = make_game(start=True)
    expiring_player = expiring_game.players[0]
    expiring_player.round_score = expiring_game._expected_hold_threshold()
    expiring_game.execute_action(expiring_player, "roll")
    assert expiring_player.risky_confirm_ticks == RISK_CONFIRM_TICKS

    for _ in range(RISK_CONFIRM_TICKS):
        expiring_game.on_tick()

    assert expiring_player.pending_risky_action == ""
    assert expiring_player.risky_confirm_ticks == 0


def test_low_stakes_roll_does_not_prompt() -> None:
    game = make_game(start=True)
    player = game.players[0]
    player.round_score = game._expected_hold_threshold() - 1

    with patch("server.games.pig.game.random.randint", return_value=2):
        game.execute_action(player, "roll")

    assert game.has_active_sequence(sequence_id=ROLL_SEQUENCE_ID)
    assert player.pending_risky_action == ""


def test_bot_strategy_adapts_to_goal_leader_and_die_risk() -> None:
    game = make_game(start=True)
    bot = game.players[0]
    bot.is_bot = True
    opponent_team = game._team_manager.get_team(game.players[1].name)
    bot_team = game._team_manager.get_team(bot.name)
    assert bot_team is not None
    assert opponent_team is not None

    bot.round_score = 19
    assert game.bot_think(bot) == "roll"
    bot.round_score = 20
    assert game.bot_think(bot) == "bank"

    bot_team.total_score = 95
    bot.round_score = 5
    assert game.bot_think(bot) == "bank"

    bot_team.total_score = 0
    opponent_team.total_score = 90
    bot.round_score = 25
    assert game.bot_think(bot) == "roll"

    bot_team.total_score = 60
    opponent_team.total_score = 0
    bot.round_score = 15
    assert game.bot_think(bot) == "bank"

    four_sided = make_game(start=True, dice_sides=4)
    four_sided_bot = four_sided.players[0]
    four_sided_bot.is_bot = True
    four_sided_bot.round_score = 9
    assert four_sided.bot_think(four_sided_bot) == "bank"


def test_roll_sequence_survives_save_and_reload() -> None:
    game = make_game(start=True)
    users = [game.get_user(player) for player in game.players]
    actor = game.players[0]

    with patch("server.games.pig.game.random.randint", return_value=6):
        game.execute_action(actor, "roll")
    assert game.has_active_sequence(sequence_id=ROLL_SEQUENCE_ID)

    loaded = PigGame.from_json(game.to_json())
    loaded.rebuild_runtime_state()
    loaded.setup_keybinds()
    for player, user in zip(loaded.players, users, strict=True):
        assert user is not None
        loaded.attach_user(player.id, user)
        loaded.setup_player_actions(player)

    resolve_roll(loaded)
    assert loaded.players[0].round_score == 6
    assert loaded.current_player is loaded.players[0]


def test_live_turn_status_has_stable_rows_and_refreshes() -> None:
    game = make_game(start=True, mobile_first=True)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)

    game.execute_action(player, "check_turn_status")
    items = user.menus["status_box"]["items"]
    assert [item.id for item in items] == [
        "target",
        "round",
        f"current:{player.id}",
        "team:0",
        "team:1",
    ]
    assert "0 in this turn" in items[2].text

    player.round_score = 7
    game.refresh_menus(player)
    game.flush_menus()

    updated = user.menus["status_box"]["items"]
    assert [item.id for item in updated] == [item.id for item in items]
    assert "7 in this turn" in updated[2].text
    assert "7 if held now" in updated[2].text


def test_touch_actions_are_hidden_before_start_and_ordered_during_play() -> None:
    game = make_game(mobile_first=True)
    player = game.players[0]

    waiting_ids = {
        action.action.id for action in game.get_all_visible_actions(player)
    }
    assert "roll" not in waiting_ids
    assert "bank" not in waiting_ids
    assert "check_turn_status" not in waiting_ids

    game.on_start()
    standard = game.create_standard_action_set(player)
    ordered = [
        action_id
        for action_id in standard._order
        if action_id
        in {
            "check_turn_status",
            "check_scores",
            "whose_turn",
            "whos_at_table",
        }
    ]
    assert ordered == [
        "check_turn_status",
        "check_scores",
        "whose_turn",
        "whos_at_table",
    ]


def test_keyboard_shortcuts_use_hold_without_overriding_lobby_bot_key() -> None:
    game = PigGame()
    game.setup_keybinds()

    assert any(
        keybind.actions == ["bank"] and keybind.state == KeybindState.ACTIVE
        for keybind in game._keybinds["h"]
    )
    assert all(
        keybind.actions != ["bank"] for keybind in game._keybinds["b"]
    )


def test_two_and_six_player_bot_games_complete() -> None:
    for player_count in (2, 6):
        random.seed(1000 + player_count)
        game = make_game(
            player_count=player_count,
            start=True,
            bot_all=True,
            target_score=20,
        )
        assert advance_until(
            game,
            lambda: game.status == "finished",
            max_ticks=12000,
        )
        winner = next(
            team
            for team in game._team_manager.teams
            if team.index == game.winner_team_index
        )
        assert winner.total_score >= 20
        assert len(game.players) == player_count


def test_team_bot_game_completes_without_tiebreaker_state() -> None:
    random.seed(2026)
    game = make_game(
        player_count=4,
        start=True,
        bot_all=True,
        target_score=25,
        team_mode="2v2",
    )

    assert advance_until(game, lambda: game.status == "finished", max_ticks=12000)
    assert game.winner_team_index in {0, 1}
    assert all(not player.is_spectator for player in game.players)


def test_pig_locale_key_and_variable_parity() -> None:
    en_text = (_locales_dir / "en" / "pig.ftl").read_text(encoding="utf-8")
    vi_text = (_locales_dir / "vi" / "pig.ftl").read_text(encoding="utf-8")

    def messages(text: str) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        current = ""
        for line in text.splitlines():
            match = re.match(r"^([a-z0-9-]+)\s*=", line)
            if match:
                current = match.group(1)
                result[current] = set()
            if current:
                result[current].update(re.findall(r"\{\s*\$([a-z0-9_]+)", line))
        return result

    assert messages(en_text) == messages(vi_text)


def test_vietnamese_documentation_matches_game_terminology() -> None:
    doc_text = (
        Path(__file__).parent.parent
        / "documentation"
        / "content"
        / "vi"
        / "games"
        / "pig.md"
    ).read_text(encoding="utf-8")

    assert "điểm lượt" in doc_text
    assert "Giữ điểm" in doc_text
    assert "điểm đích" in doc_text
    assert "gieo trúng mặt 1" in doc_text
    assert "bị \"nổ\"" not in doc_text
