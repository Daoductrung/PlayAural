"""Tests for shared team arrangement before team-game starts."""

import pytest

from ..games.dominos.game import DominosGame, DominosOptions
from ..games.milebymile.game import MileByMileGame
from ..games.milebymile.options import MileByMileOptions
from ..games.pig.game import PigGame, PigOptions
from ..games.scopa.game import ScopaGame, ScopaOptions
from ..users.test_user import MockUser


def make_game(game_cls, options, player_count: int = 4):
    game = game_cls(options=options)
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        game.add_player(name, MockUser(name, uuid=f"p{index + 1}"))
    game.host = "Player1"
    game.refresh_menus()
    game.flush_menus()
    return game


def team_members(game) -> list[list[str]]:
    return [list(team.members) for team in game.team_manager.teams]


def turn_team_indexes(game) -> list[int]:
    indexes = []
    for player in game.turn_players:
        team = game.team_manager.get_team(player.name)
        indexes.append(team.index if team else -1)
    return indexes


def status_box_texts(user: MockUser) -> list[str]:
    items = user.get_current_menu_items("status_box") or []
    return [getattr(item, "text", str(item)) for item in items]


def test_team_game_start_enters_arrangement_before_playing() -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="2v2"))
    host = game.players[0]

    game.execute_action(host, "start_game")

    assert game.status == "waiting"
    assert game.team_arrangement_active is True
    assert game.team_arrangement_team_mode == "2v2"
    assert team_members(game) == [["Player1", "Player3"], ["Player2", "Player4"]]

    visible = {
        resolved.action.id: resolved
        for resolved in game.get_all_visible_actions(host)
    }
    assert visible["start_game"].label == "Confirm teams and start"
    assert "confirm_team_arrangement" not in visible
    assert "confirm_team_arrangement" not in {
        resolved.action.id
        for resolved in game.get_all_enabled_actions(host)
    }


def test_host_can_swap_and_confirm_arranged_teams() -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="2v2"))
    host = game.players[0]
    game.execute_action(host, "start_game")

    game.execute_action(host, "select_team_member", "p1")
    game.execute_action(host, "swap_team_member", "p2")

    assert team_members(game) == [["Player2", "Player3"], ["Player1", "Player4"]]

    game.execute_action(host, "confirm_team_arrangement")

    assert game.status == "playing"
    assert game.team_arrangement_active is False
    assert team_members(game) == [["Player2", "Player3"], ["Player1", "Player4"]]
    assert [player.name for player in game.turn_players] == [
        "Player1",
        "Player3",
        "Player4",
        "Player2",
    ]


def test_enter_confirms_active_team_arrangement() -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="2v2"))
    host = game.players[0]
    game.execute_action(host, "start_game")

    host_user = game.get_user(host)
    assert host_user is not None
    host_user.clear_messages()

    game.handle_event(host, {"type": "keybind", "key": "enter"})

    assert game.status == "playing"
    assert game.team_arrangement_active is False
    assert not any(
        "Team arrangement is not active" in message
        for message in host_user.get_spoken_messages()
    )


def test_individual_team_mode_starts_immediately() -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="individual"))

    game.execute_action(game.players[0], "start_game")

    assert game.status == "playing"
    assert game.team_arrangement_active is False


def test_team_arrangement_can_be_opted_out() -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="2v2"))
    game.allows_team_arrangement = lambda: False

    game.execute_action(game.players[0], "start_game")

    assert game.status == "playing"
    assert game.team_arrangement_active is False


def test_confirm_handles_team_mode_changed_outside_arrangement_ui() -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="2v2"))
    host = game.players[0]
    game.execute_action(host, "start_game")

    game.options.team_mode = "individual"
    game.execute_action(host, "confirm_team_arrangement")

    assert game.status == "playing"
    assert game.team_arrangement_active is False
    assert team_members(game) == [["Player1"], ["Player2"], ["Player3"], ["Player4"]]


def test_roster_change_cancels_team_arrangement() -> None:
    game = make_game(MileByMileGame, MileByMileOptions(team_mode="2v2"))
    game.execute_action(game.players[0], "start_game")

    game.add_player("Late", MockUser("Late", uuid="late"))

    assert game.team_arrangement_active is False
    assert game.team_arrangement_selected_player_id == ""
    assert game.team_manager.teams == []


def test_select_team_member_menu_uses_localized_member_labels() -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="2v2"))
    host = game.players[0]
    game.execute_action(host, "start_game")

    game.execute_action(host, "select_team_member")

    host_user = game.get_user(host)
    assert host_user is not None
    items = host_user.get_current_menu_items("action_input_menu")
    assert items is not None
    labels = [item.text for item in items]
    assert "Player1, Team 1, not selected" in labels
    assert "Player2, Team 2, not selected" in labels


@pytest.mark.parametrize("roster_change", ["join", "leave"])
def test_open_team_member_selector_closes_after_active_roster_change(
    roster_change: str,
) -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="2v2"))
    host = game.players[0]
    host_user = game.get_user(host)
    assert host_user is not None
    game.execute_action(host, "start_game")
    game.execute_action(host, "select_team_member")
    assert game._pending_actions[host.id] == "select_team_member"

    if roster_change == "join":
        game.add_player("Late", MockUser("Late", uuid="late"))
    else:
        game.remove_player(game.players[-1].id)
    game.flush_menus()

    assert game.team_arrangement_active is False
    assert host.id not in game._pending_actions
    assert "action_input_menu" not in host_user.menus
    assert host_user.get_current_menu_items("turn_menu") is not None


def test_open_team_member_selector_survives_spectator_roster_churn() -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="2v2"))
    host = game.players[0]
    host_user = game.get_user(host)
    assert host_user is not None
    game.execute_action(host, "start_game")
    game.execute_action(host, "select_team_member")

    spectator = game.add_spectator(
        "Spectator",
        MockUser("Spectator", uuid="spectator"),
    )
    game.flush_menus()
    game.remove_spectator(spectator.id)
    game.flush_menus()

    assert game._pending_actions[host.id] == "select_team_member"
    item_ids = [
        item.id
        for item in (host_user.get_current_menu_items("action_input_menu") or [])
    ]
    assert item_ids == ["p1", "p2", "p3", "p4", "_cancel"]

    game.handle_event(
        host,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "p1",
        },
    )
    assert host.id not in game._pending_actions
    assert game.team_arrangement_selected_player_id == "p1"


def test_team_arrangement_read_includes_balanced_turn_order() -> None:
    game = make_game(DominosGame, DominosOptions(team_mode="2v2"))
    host = game.players[0]
    game.execute_action(host, "start_game")

    game.execute_action(host, "select_team_member", "p1")
    game.execute_action(host, "swap_team_member", "p2")
    game.execute_action(host, "read_team_arrangement")

    host_user = game.get_user(host)
    assert host_user is not None
    assert "Turn order: Player1, Player3, Player4, and Player2" in (
        host_user.get_spoken_messages()
    )


def test_replacement_bot_preserves_team_assignment_during_play() -> None:
    game = make_game(PigGame, PigOptions(team_mode="2v2"))
    host = game.players[0]
    game.execute_action(host, "start_game")
    game.execute_action(host, "confirm_team_arrangement")

    replaced = game.players[1]
    original_team = game.team_manager.get_team(replaced.name)
    assert original_team is not None

    assert game._replace_with_bot(replaced) is True

    assert game.team_manager.get_team("Player2") is None
    replacement_team = game.team_manager.get_team(replaced.name)
    assert replacement_team is not None
    assert replacement_team.index == original_team.index


def test_replacement_bot_score_checks_use_current_bot_name() -> None:
    game = make_game(
        PigGame,
        PigOptions(target_score=25, team_mode="individual"),
        player_count=2,
    )
    host = game.players[0]
    game.execute_action(host, "start_game")
    replaced = game.players[1]
    game.team_manager.add_to_team_score(replaced.name, 7)

    assert game._replace_with_bot(replaced) is True
    bot_name = replaced.name

    # Simulate a stale saved table or missed older path where scores still held
    # the human name after the seat was converted to a bot.
    assert game.team_manager.rename_member(bot_name, "Player2") is True
    assert game.team_manager.get_team(bot_name) is None

    host_user = game.get_user(host)
    assert host_user is not None

    host_user.clear_messages()
    game.execute_action(host, "check_scores")
    spoken_scores = host_user.get_spoken_messages()

    assert any(line.startswith(f"{bot_name}: 7/25") for line in spoken_scores)
    assert not any(line.startswith("Player2:") for line in spoken_scores)
    assert game.team_manager.get_team(bot_name) is not None
    assert game.team_manager.get_team("Player2") is None

    host_user.clear_messages()
    game.execute_action(host, "check_scores_detailed")
    detailed_scores = status_box_texts(host_user)

    assert any(line.startswith(f"{bot_name}: 7/25") for line in detailed_scores)
    assert not any(line.startswith("Player2:") for line in detailed_scores)


def test_reclaimed_replacement_seat_score_checks_use_human_name() -> None:
    game = make_game(
        PigGame,
        PigOptions(target_score=25, team_mode="individual"),
        player_count=2,
    )
    host = game.players[0]
    game.execute_action(host, "start_game")
    replaced = game.players[1]
    game.team_manager.add_to_team_score(replaced.name, 7)

    assert game._replace_with_bot(replaced) is True
    bot_name = replaced.name

    replaced.is_bot = False
    replaced.replaced_human = False
    replaced.name = "Player2"
    replaced.replaced_human_name = ""
    replaced.replacement_bot_name = ""
    game._on_replacement_slot_reclaimed(bot_name, "Player2")

    host_user = game.get_user(host)
    assert host_user is not None

    host_user.clear_messages()
    game.execute_action(host, "check_scores")
    spoken_scores = host_user.get_spoken_messages()

    assert any(line.startswith("Player2: 7/25") for line in spoken_scores)
    assert not any(line.startswith(f"{bot_name}:") for line in spoken_scores)
    assert game.team_manager.get_team("Player2") is not None
    assert game.team_manager.get_team(bot_name) is None


@pytest.mark.parametrize(
    ("game_cls", "options"),
    [
        (DominosGame, DominosOptions(team_mode="2v2")),
        (MileByMileGame, MileByMileOptions(team_mode="2v2")),
        (PigGame, PigOptions(team_mode="2v2")),
        (ScopaGame, ScopaOptions(team_mode="2v2")),
    ],
)
def test_current_team_games_enter_arrangement_phase(game_cls, options) -> None:
    game = make_game(game_cls, options)

    game.execute_action(game.players[0], "start_game")

    assert game.status == "waiting"
    assert game.team_arrangement_active is True
    assert team_members(game) == [["Player1", "Player3"], ["Player2", "Player4"]]


@pytest.mark.parametrize(
    ("game_cls", "options"),
    [
        (DominosGame, DominosOptions(team_mode="2v2")),
        (MileByMileGame, MileByMileOptions(team_mode="2v2")),
        (PigGame, PigOptions(team_mode="2v2")),
        (ScopaGame, ScopaOptions(team_mode="2v2")),
    ],
)
def test_current_team_games_keep_balanced_turn_order_after_swap(
    game_cls, options
) -> None:
    game = make_game(game_cls, options)
    host = game.players[0]
    game.execute_action(host, "start_game")
    game.execute_action(host, "select_team_member", "p1")
    game.execute_action(host, "swap_team_member", "p2")

    game.execute_action(host, "confirm_team_arrangement")

    indexes = turn_team_indexes(game)
    assert len(indexes) == 4
    assert all(indexes[i] != indexes[(i + 1) % len(indexes)] for i in range(4))
