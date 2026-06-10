"""Tests for Senet."""

from pathlib import Path

from ..games.senet.game import SenetGame, SenetOptions
from ..games.senet.moves import generate_legal_moves
from ..games.senet.state import (
    HOUSE_HAPPINESS,
    HOUSE_HORUS,
    HOUSE_REBIRTH,
    SenetGameState,
)
from ..messages.localization import Localization
from ..tables.table import Table
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(*, start: bool = False, player_count: int = 2) -> SenetGame:
    game = SenetGame(options=SenetOptions())
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        game.add_player(name, MockUser(name, uuid=f"p{index + 1}"))
    game.host = "Player1"
    if start:
        game.on_start()
    return game


def test_prestart_validate_requires_exactly_two_active_players() -> None:
    too_few = make_game(player_count=1)
    too_many = make_game(player_count=3)

    assert (
        "senet-error-exactly-two-players",
        {"count": 1},
    ) in too_few.prestart_validate()
    assert (
        "senet-error-exactly-two-players",
        {"count": 3},
    ) in too_many.prestart_validate()


def test_spectator_leave_during_play_does_not_create_replacement_bot() -> None:
    game = make_game(start=True)
    spectator_user = MockUser("Watcher", uuid="watcher")
    spectator = game.add_spectator("Watcher", spectator_user)
    table = Table(table_id="senet-test", game_type="senet", host="Player1")
    for player in game.players:
        user = game.get_user(player)
        assert user is not None
        table.add_member(player.name, user, as_spectator=player.is_spectator)
    table._game = game
    table.status = game.status
    game._table = table
    for player in game.players:
        user = game.get_user(player)
        if user:
            user.clear_messages()

    game._perform_leave_game(spectator)

    assert spectator.id not in {player.id for player in game.players}
    assert "Watcher" not in {member.username for member in table.members}
    assert all(not player.is_bot for player in game.get_active_players())
    assert all(not player.replaced_human for player in game.get_active_players())
    assert not any(
        "playing on behalf" in message.data.get("text", "")
        for player in game.players
        for user in [game.get_user(player)]
        if user
        for message in user.messages
    )


def test_spectator_disconnect_is_removed_without_replacement_bot() -> None:
    game = make_game(start=True)
    spectator = game.add_spectator("Watcher", MockUser("Watcher", uuid="watcher"))

    game.on_player_disconnect(spectator.id)

    assert spectator.id not in {player.id for player in game.players}
    assert all(not player.is_bot for player in game.get_active_players())
    assert all(not player.replaced_human for player in game.get_active_players())


def test_ctrl_navigation_before_throw_explains_throw_requirement() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert player is not None
    user = game.get_user(player)
    assert user is not None
    user.clear_messages()

    game.handle_event(player, {"type": "keybind", "key": "right", "control": True})

    assert Localization.get("en", "senet-need-throw-first") in user.get_spoken_messages()
    assert Localization.get("en", "action-not-your-turn") not in user.get_spoken_messages()


def test_score_shortcuts_use_standard_s_keys() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert player is not None
    user = game.get_user(player)
    assert user is not None
    p1 = game._get_player_by_num(1)
    p2 = game._get_player_by_num(2)
    expected = Localization.get(
        "en",
        "senet-score",
        p1=p1.name if p1 else "?",
        off1=game.game_state.off[1],
        p2=p2.name if p2 else "?",
        off2=game.game_state.off[2],
    )

    assert [keybind.actions for keybind in game._keybinds["s"]] == [["check_scores"]]
    assert [keybind.actions for keybind in game._keybinds["shift+s"]] == [
        ["check_scores_detailed"]
    ]
    assert "v" not in game._keybinds

    user.clear_messages()
    game.handle_event(player, {"type": "keybind", "key": "s"})
    assert expected in user.get_spoken_messages()

    user.clear_messages()
    game.handle_event(player, {"type": "keybind", "key": "s", "shift": True})
    status_items = user.get_current_menu_items("status_box") or []
    assert [item.text for item in status_items] == [expected]

    user.clear_messages()
    game.handle_event(player, {"type": "keybind", "key": "v"})
    assert expected not in user.get_spoken_messages()


def test_special_houses_before_horus_are_safe_from_capture() -> None:
    state = SenetGameState(board=[0] * 30)
    state.board[HOUSE_REBIRTH - 2] = 1
    state.board[HOUSE_REBIRTH] = 2

    moves = generate_legal_moves(state, 1, 2)

    assert not any(move.destination == HOUSE_REBIRTH and move.is_swap for move in moves)


def test_house_of_horus_can_be_captured() -> None:
    state = SenetGameState(board=[0] * 30)
    state.board[HOUSE_HAPPINESS] = 1
    state.board[HOUSE_HORUS] = 2

    moves = generate_legal_moves(state, 1, 4)

    assert any(move.destination == HOUSE_HORUS and move.is_swap for move in moves)


def test_house_of_horus_auto_scores_when_first_row_is_clear() -> None:
    game = make_game(start=True)
    player = game.current_player
    assert player is not None
    pnum = player.player_num
    user = game.get_user(player)
    assert user is not None
    game.game_state.board = [0] * 30
    game.game_state.board[HOUSE_HORUS] = pnum
    game.game_state.off[pnum] = 4
    user.clear_messages()

    assert game._score_horus_if_ready(player) is True

    assert game.status == "finished"
    assert game.winner_name == player.name
    assert game.game_state.board[HOUSE_HORUS] == 0
    assert game.game_state.off[pnum] == 5
    assert any("House of Horus" in message for message in user.get_spoken_messages())
