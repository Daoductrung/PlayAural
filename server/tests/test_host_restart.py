from __future__ import annotations

import pytest

from ..core.server import HOST_RESTART_CONFIRM_MENU, Server
from ..games.crazyeights.game import CrazyEightsGame
from ..users.test_user import MockUser


def _message_types(user: MockUser) -> list[str]:
    return [message.type for message in user.messages]


def _menu_ids(user: MockUser, menu_id: str) -> list[str]:
    items = user.menus[menu_id]["items"]
    return [
        getattr(item, "id", item.get("id") if isinstance(item, dict) else None)
        for item in items
    ]


def _make_playing_table():
    server = Server(db_path=":memory:")
    alice = MockUser("Alice", uuid="alice")
    bob = MockUser("Bob", uuid="bob")
    server._users = {
        alice.username: alice,
        bob.username: bob,
    }

    table = server._tables.create_table("crazyeights", alice.username, alice)
    game = CrazyEightsGame()
    table.game = game
    game._table = table
    server._set_in_game_state(alice, table.table_id)
    game.initialize_lobby(alice.username, alice)

    table.add_member(bob.username, bob)
    game.add_player(bob.username, bob)
    server._set_in_game_state(bob, table.table_id)

    game.status = "playing"
    game.game_active = True
    game._sync_table_status()
    game.scheduled_sounds = [
        [game.sound_scheduler_tick, "old_delayed_sound.ogg", 100, 0, 100]
    ]
    game.play_ambience("old_ambience.ogg", outro="old_outro.ogg")
    alice.clear_messages()
    bob.clear_messages()
    return server, table, game, alice, bob


@pytest.mark.asyncio
async def test_host_restart_requires_confirmation_and_resets_to_clean_lobby() -> None:
    server, table, old_game, alice, bob = _make_playing_table()
    server._voice_presence_by_user[alice.username] = {
        "scope": "table",
        "context_id": table.table_id,
    }

    host_menu_items = server._get_host_management_menu_items(alice, table)
    host_menu_ids = [item.id for item in host_menu_items]
    assert host_menu_ids[-2:] == ["restart_game", "back"]

    await server._handle_host_management_selection(
        alice,
        "restart_game",
        {"table_id": table.table_id},
    )
    assert server._user_states[alice.username]["menu"] == HOST_RESTART_CONFIRM_MENU
    assert _menu_ids(alice, HOST_RESTART_CONFIRM_MENU)[-2:] == ["no", "yes"]

    await server._handle_host_restart_confirm_selection(
        alice,
        "yes",
        {"table_id": table.table_id},
    )

    new_game = table.game
    assert new_game is not old_game
    assert table.status == "waiting"
    assert new_game.status == "waiting"
    assert new_game.game_active is False
    assert [member.username for member in table.members] == ["Alice", "Bob"]
    assert [player.name for player in new_game.players] == ["Alice", "Bob"]
    assert new_game.scheduled_sounds == []
    assert new_game.sound_scheduler_tick == 0
    assert new_game.current_ambience == ""
    assert new_game.current_music == "findgamemus.ogg"
    assert old_game._destroyed is True
    assert old_game.scheduled_sounds == []
    assert old_game._users == {}
    assert (
        server._voice_presence_by_user[alice.username]["context_id"]
        == table.table_id
    )
    assert server._user_states[alice.username] == {
        "menu": "in_game",
        "table_id": table.table_id,
    }
    assert server._user_states[bob.username] == {
        "menu": "in_game",
        "table_id": table.table_id,
    }

    for user in (alice, bob):
        message_types = _message_types(user)
        assert "stop_ambience" in message_types
        assert any(
            message.type == "play_music"
            and message.data.get("name") == "findgamemus.ogg"
            for message in user.messages
        )
        assert any(
            message.type == "speak"
            and "restarted the game" in message.data.get("text", "")
            for message in user.messages
        )

    new_game.on_tick()
    assert "old_delayed_sound.ogg" not in alice.get_sounds_played()
    assert "old_delayed_sound.ogg" not in bob.get_sounds_played()


@pytest.mark.asyncio
async def test_host_restart_cancel_keeps_current_game() -> None:
    server, table, old_game, alice, _bob = _make_playing_table()

    await server._handle_host_management_selection(
        alice,
        "restart_game",
        {"table_id": table.table_id},
    )
    await server._handle_host_restart_confirm_selection(
        alice,
        "no",
        {"table_id": table.table_id},
    )

    assert table.game is old_game
    assert table.status == "playing"
    assert server._user_states[alice.username]["menu"] == "host_management_menu"


@pytest.mark.asyncio
async def test_stale_host_restart_selection_is_rejected_after_reset() -> None:
    server, table, _old_game, alice, _bob = _make_playing_table()

    table.reset_game(preserve_scheduled_sounds=False)
    alice.clear_messages()

    await server._handle_host_management_selection(
        alice,
        "restart_game",
        {"table_id": table.table_id},
    )

    assert server._user_states[alice.username]["menu"] == "host_management_menu"
    assert "There is no active game to restart." in alice.get_spoken_messages()
