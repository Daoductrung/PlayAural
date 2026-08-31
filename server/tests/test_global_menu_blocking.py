from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from ..core.server import Server
from ..games.pig.game import PigGame
from ..messages.localization import Localization
from ..users.test_user import MockUser


def _make_playing_game_server() -> tuple[Server, MockUser, MockUser, object, object, object]:
    server = Server(db_path=":memory:")
    server._db.connect()

    server._db.create_user("Alice", "hash")
    server._db.create_user("Bob", "hash")
    host_record = server._db.get_user("Alice")
    guest_record = server._db.get_user("Bob")
    assert host_record is not None
    assert guest_record is not None

    host = MockUser(host_record.username, uuid=host_record.uuid)
    guest = MockUser(guest_record.username, uuid=guest_record.uuid)
    server._users = {host.username: host, guest.username: guest}

    table = server._tables.create_table("pig", host.username, host)
    game = PigGame()
    table.game = game
    game._table = table
    game.initialize_lobby(host.username, host)

    table.add_member(guest.username, guest, as_spectator=False)
    game.add_player(guest.username, guest)
    game.on_start()

    server._user_states[host.username] = {"menu": "in_game", "table_id": table.table_id}
    server._user_states[guest.username] = {"menu": "in_game", "table_id": table.table_id}

    host_player = game.get_player_by_id(host.uuid)
    guest_player = game.get_player_by_id(guest.uuid)
    assert host_player is not None
    assert guest_player is not None
    return server, host, guest, table, game, host_player


@pytest.mark.asyncio
async def test_options_submenu_selection_while_playing_routes_to_server() -> None:
    server, host, _guest, _table, _game, _host_player = _make_playing_game_server()
    server._sync_pref_to_client = lambda *args, **kwargs: None
    try:
        original_typing_sounds = host.preferences.play_typing_sounds

        await server._handle_open_options(SimpleNamespace(username=host.username))
        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "options_menu",
                "selection_id": "options_audio",
            },
        )
        assert server._user_states[host.username]["menu"] == "options_audio_submenu"

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "options_audio_submenu",
                "selection_id": "play_typing_sounds",
            },
        )

        assert host.preferences.play_typing_sounds is not original_typing_sounds
        assert server._user_states[host.username]["menu"] == "options_audio_submenu"
        assert "options_audio_submenu" in host.menus
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_options_submenu_blocks_game_menu_rebuild_while_playing() -> None:
    server, host, _guest, _table, game, host_player = _make_playing_game_server()
    try:
        await server._handle_open_options(SimpleNamespace(username=host.username))
        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "options_menu",
                "selection_id": "options_audio",
            },
        )
        assert server._user_states[host.username]["menu"] == "options_audio_submenu"

        host.clear_messages()
        game.refresh_menus(host_player)
        game.flush_menus()

        assert not any(
            message.type == "show_menu" and message.data.get("menu_id") == "turn_menu"
            for message in host.messages
        )
        assert server._user_states[host.username]["menu"] == "options_audio_submenu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_game_over_waits_behind_global_menu_until_return_to_table() -> None:
    server, host, _guest, table, game, _host_player = _make_playing_game_server()
    server._sync_pref_to_client = lambda *args, **kwargs: None
    try:
        await server._handle_open_options(SimpleNamespace(username=host.username))
        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "options_menu",
                "selection_id": "options_audio",
            },
        )
        assert server._user_states[host.username]["menu"] == "options_audio_submenu"

        host.clear_messages()
        game.finish_game()
        assert table.game is not game
        assert server._user_states[host.username]["menu"] == "options_audio_submenu"
        assert not any(
            message.type == "show_menu"
            and message.data.get("menu_id") == "game_over"
            for message in host.messages
        )

        original_typing_sounds = host.preferences.play_typing_sounds
        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "options_audio_submenu",
                "selection_id": "play_typing_sounds",
            },
        )
        assert host.preferences.play_typing_sounds is not original_typing_sounds
        assert server._user_states[host.username]["menu"] == "options_audio_submenu"

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "options_audio_submenu",
                "selection_id": "back",
            },
        )
        assert server._user_states[host.username]["menu"] == "options_menu"

        host.clear_messages()
        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "options_menu",
                "selection_id": "back",
            },
        )
        assert server._user_states[host.username] == {
            "menu": "game_over",
            "table_id": table.table_id,
        }
        assert any(
            message.type == "show_menu"
            and message.data.get("menu_id") == "game_over"
            for message in host.messages
        )

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "game_over",
                "selection_id": "return_to_table",
            },
        )
        assert server._user_states[host.username] == {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        assert "game_over" not in host.menus
        assert "turn_menu" in host.menus
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_deferred_game_over_leave_routes_to_table() -> None:
    server, host, _guest, table, game, _host_player = _make_playing_game_server()
    try:
        await server._handle_open_options(SimpleNamespace(username=host.username))
        assert server._user_states[host.username]["menu"] == "options_menu"

        game.finish_game()
        assert server._user_states[host.username]["menu"] == "options_menu"

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "options_menu",
                "selection_id": "back",
            },
        )
        assert server._user_states[host.username]["menu"] == "game_over"

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "game_over",
                "selection_id": "leave_game",
            },
        )
        assert server._user_states[host.username] == {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        assert "leave_game_confirm" in host.menus

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "leave_game_confirm",
                "selection_id": "yes",
            },
        )
        assert table.get_user(host.username) is None
        assert server._user_states[host.username]["menu"] == "main_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_private_message_input_survives_game_over_and_sends_before_result() -> None:
    server, host, guest, table, game, _host_player = _make_playing_game_server()
    try:
        assert server._db.send_friend_request(host.uuid, guest.uuid) == "sent"
        assert server._db.send_friend_request(guest.uuid, host.uuid) == "accepted"

        client = SimpleNamespace(username=host.username)
        await server._handle_open_friends_hub(client)
        await server._handle_menu(
            client,
            {
                "type": "menu",
                "menu_id": "friends_hub_menu",
                "selection_id": "my_friends",
            },
        )
        await server._handle_menu(
            client,
            {
                "type": "menu",
                "menu_id": "friends_list_menu",
                "selection_id": f"friend_{guest.username}",
            },
        )
        await server._handle_menu(
            client,
            {
                "type": "menu",
                "menu_id": "friend_actions_menu",
                "selection_id": "send_pm",
            },
        )

        input_state = server._user_states[host.username]
        assert input_state["menu"] == "send_pm_input"
        assert input_state["target_username"] == guest.username
        assert input_state["_transient"] is True
        assert "send_pm_input" in host.editboxes

        host.clear_messages()
        game.finish_game()

        assert table.game is not game
        assert server._user_states[host.username] == input_state
        assert not any(
            message.type in {"remove_editbox", "show_menu"}
            and (
                message.type == "remove_editbox"
                or message.data.get("menu_id") == "game_over"
            )
            for message in host.messages
        )

        server._deliver_private_message = AsyncMock()
        await server._handle_editbox(
            client,
            {
                "type": "editbox",
                "input_id": "send_pm_input",
                "text": "Still here",
            },
        )
        server._deliver_private_message.assert_awaited_once_with(
            host,
            guest.username,
            "Still here",
        )
        assert server._user_states[host.username]["menu"] == "friend_actions_menu"

        for menu_id in (
            "friend_actions_menu",
            "friends_list_menu",
            "friends_hub_menu",
        ):
            await server._handle_menu(
                client,
                {
                    "type": "menu",
                    "menu_id": menu_id,
                    "selection_id": "back",
                },
            )

        assert server._user_states[host.username] == {
            "menu": "game_over",
            "table_id": table.table_id,
        }
        assert "game_over" in host.menus
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_new_game_clears_deferred_result_without_interrupting_global_menu() -> None:
    server, host, _guest, table, game, _host_player = _make_playing_game_server()
    try:
        await server._handle_open_options(SimpleNamespace(username=host.username))
        assert server._user_states[host.username]["menu"] == "options_menu"

        game.finish_game()
        new_game = table.game
        assert new_game is not game
        assert new_game._last_game_result is not None
        assert new_game._end_screen_open_player_ids

        host.clear_messages()
        new_game._start_game_from_lobby()

        assert new_game.status == "playing"
        assert new_game._last_game_result is None
        assert not new_game._end_screen_open_player_ids
        assert server._user_states[host.username]["menu"] == "options_menu"
        assert not any(
            message.type == "remove_menu"
            or (
                message.type == "show_menu"
                and message.data.get("menu_id") in {"game_over", "turn_menu"}
            )
            for message in host.messages
        )
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_open_options_is_idempotent_inside_options_flow() -> None:
    server, host, _guest, _table, _game, _host_player = _make_playing_game_server()
    try:
        await server._handle_open_options(SimpleNamespace(username=host.username))
        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "options_menu",
                "selection_id": "options_audio",
            },
        )
        state_before = dict(server._user_states[host.username])

        await server._handle_open_options(SimpleNamespace(username=host.username))

        assert server._user_states[host.username] == state_before
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_open_options_defers_while_status_box_open() -> None:
    server, host, _guest, _table, game, host_player = _make_playing_game_server()
    try:
        host.clear_messages()
        game.status_box(host_player, ["Turn summary"])
        assert host_player.id in game._status_box_open

        await server._handle_open_options(SimpleNamespace(username=host.username))

        assert server._user_states[host.username]["menu"] == "in_game"
        assert "options_menu" not in host.menus
        assert "status_box" in host.menus

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "status_box",
                "selection_id": "status_box:line:0",
            },
        )

        assert host_player.id not in game._status_box_open
        assert "status_box" not in host.menus
        assert server._user_states[host.username]["menu"] == "options_menu"
        assert "options_menu" in host.menus
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_open_friends_defers_while_status_box_open() -> None:
    server, host, _guest, _table, game, host_player = _make_playing_game_server()
    try:
        host.clear_messages()
        game.status_box(host_player, ["Score summary"])
        assert host_player.id in game._status_box_open

        await server._handle_open_friends_hub(SimpleNamespace(username=host.username))

        assert server._user_states[host.username]["menu"] == "in_game"
        assert "friends_hub_menu" not in host.menus
        assert "status_box" in host.menus

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "status_box",
                "selection_id": "status_box:line:0",
            },
        )

        assert host_player.id not in game._status_box_open
        assert server._user_states[host.username]["menu"] == "friends_hub_menu"
        assert "friends_hub_menu" in host.menus
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_host_management_keybind_defers_while_status_box_open() -> None:
    server, host, _guest, _table, game, host_player = _make_playing_game_server()
    try:
        host.clear_messages()
        game.status_box(host_player, ["Table summary"])
        assert host_player.id in game._status_box_open

        await server._handle_keybind(
            SimpleNamespace(username=host.username),
            {
                "type": "keybind",
                "key": "ctrl+m",
                "menu_item_id": "roll",
            },
        )

        assert server._user_states[host.username]["menu"] == "in_game"
        assert "host_management_menu" not in host.menus
        assert "status_box" in host.menus

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "status_box",
                "selection_id": "status_box:line:0",
            },
        )

        assert host_player.id not in game._status_box_open
        assert "status_box" not in host.menus
        assert server._user_states[host.username]["menu"] == "host_management_menu"
        assert "host_management_menu" in host.menus

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "host_management_menu",
                "selection_id": "back",
            },
        )
        game.flush_menus()
        turn_updates = [
            message
            for message in host.messages
            if message.type == "show_menu"
            and message.data.get("menu_id") == "turn_menu"
        ]
        assert turn_updates[-1].data["selection_id"] == "roll"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_host_management_back_restores_touch_actions_anchor() -> None:
    server, host, _guest, _table, game, host_player = _make_playing_game_server()
    try:
        host.client_type = "web"
        game.refresh_menus(host_player)
        game.flush_menus()
        game.handle_event(
            host_player,
            {
                "type": "menu",
                "menu_id": "turn_menu",
                "selection_id": "web_actions_menu",
            },
        )

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "actions_menu",
                "selection_id": "host_management",
            },
        )
        assert server._user_states[host.username]["menu"] == "host_management_menu"

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "host_management_menu",
                "selection_id": "back",
            },
        )
        game.flush_menus()

        turn_updates = [
            message
            for message in host.messages
            if message.type == "show_menu"
            and message.data.get("menu_id") == "turn_menu"
        ]
        assert turn_updates[-1].data["selection_id"] == "web_actions_menu"
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_rules_keybind_from_actions_menu_restores_turn_menu_after_status_close() -> None:
    server, host, _guest, _table, game, host_player = _make_playing_game_server()
    try:
        game._action_show_actions_menu(host_player, "show_actions_menu")
        assert host_player.id in game._actions_menu_open
        assert "actions_menu" in host.menus

        await server._handle_keybind(
            SimpleNamespace(username=host.username),
            {"type": "keybind", "key": "ctrl+f1"},
        )

        assert host_player.id not in game._actions_menu_open
        assert host_player.id in game._status_box_open
        assert "status_box" in host.menus

        host.clear_messages()
        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "status_box",
                "selection_id": "status_box:line:0",
            },
        )

        assert host_player.id not in game._status_box_open
        assert "status_box" not in host.menus
        assert any(
            message.type == "show_menu" and message.data.get("menu_id") == "turn_menu"
            for message in host.messages
        )
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_stale_global_state_recovers_from_last_sent_actions_menu() -> None:
    server, host, _guest, table, game, host_player = _make_playing_game_server()
    try:
        game._action_show_actions_menu(host_player, "show_actions_menu")
        host._last_menu_packet_id = "actions_menu"
        server._user_states[host.username] = {"menu": "options_menu"}

        await server._handle_menu(
            SimpleNamespace(username=host.username),
            {
                "type": "menu",
                "menu_id": "actions_menu",
                "selection_id": "go_back",
            },
        )

        assert server._user_states[host.username] == {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        assert host_player.id not in game._actions_menu_open
        assert "turn_menu" in host.menus
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_stale_global_state_recovers_keybind_from_last_sent_game_menu() -> None:
    server, host, _guest, table, _game, _host_player = _make_playing_game_server()
    try:
        host._last_menu_packet_id = "turn_menu"
        server._user_states[host.username] = {"menu": "options_menu"}

        await server._handle_keybind(
            SimpleNamespace(username=host.username),
            {
                "type": "keybind",
                "key": "ctrl+q",
                "menu_id": "turn_menu",
            },
        )

        assert server._user_states[host.username] == {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        assert "leave_game_confirm" in host.menus
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_active_game_input_blocks_navigation_without_deferring() -> None:
    server, host, _guest, _table, game, host_player = _make_playing_game_server()
    try:
        game._pending_actions[host_player.id] = "roll"

        await server._handle_open_options(SimpleNamespace(username=host.username))

        assert server._user_states[host.username]["menu"] == "in_game"
        assert "options_menu" not in host.menus
        assert host.username not in server._deferred_navigation

        game._pending_actions.pop(host_player.id, None)
        game.refresh_menus(host_player)
        game.flush_menus()

        assert server._user_states[host.username]["menu"] == "in_game"
        assert "options_menu" not in host.menus
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_server_editbox_escape_cancels_without_validation_error() -> None:
    server = Server(db_path=":memory:")
    server._db.connect()
    try:
        user = MockUser("Alice", uuid="p1")
        server._users[user.username] = user
        server._user_states[user.username] = {"menu": "options_menu"}
        server._enter_input_state(user, "speech_rate_input")
        client = SimpleNamespace(
            username=user.username,
            authenticated=True,
            retired=False,
        )
        user.connection = client

        await server._on_client_message(
            client,
            {"type": "escape", "menu_id": "speech_rate_input"},
        )

        assert server._user_states[user.username]["menu"] == "options_menu"
        assert "options_menu" in user.menus
        assert user.get_last_spoken() != Localization.get(user.locale, "invalid-rate")
    finally:
        server._db.close()


@pytest.mark.asyncio
async def test_blank_option_editbox_submission_cancels_without_validation_error() -> None:
    server = Server(db_path=":memory:")
    server._db.connect()
    try:
        user = MockUser("Alice", uuid="p1")
        server._users[user.username] = user
        server._user_states[user.username] = {"menu": "options_menu"}
        server._enter_input_state(user, "speech_rate_input")
        client = SimpleNamespace(
            username=user.username,
            authenticated=True,
            retired=False,
        )
        user.connection = client

        await server._on_client_message(
            client,
            {
                "type": "editbox",
                "input_id": "speech_rate_input",
                "text": "",
            },
        )

        assert server._user_states[user.username]["menu"] == "options_menu"
        assert "options_menu" in user.menus
        assert user.get_last_spoken() != Localization.get(user.locale, "invalid-rate")
    finally:
        server._db.close()


def test_game_action_input_escape_cancels_pending_editbox() -> None:
    server, _host, _guest, _table, game, host_player = _make_playing_game_server()
    try:
        game._pending_actions[host_player.id] = "roll"

        game.handle_event(
            host_player,
            {"type": "escape", "menu_id": "action_input_editbox"},
        )

        assert host_player.id not in game._pending_actions
        assert "turn_menu" in game.get_user(host_player).menus
    finally:
        server._db.close()


def test_game_action_input_escape_cancels_pending_menu() -> None:
    server, _host, _guest, _table, game, host_player = _make_playing_game_server()
    try:
        game._pending_actions[host_player.id] = "roll"

        game.handle_event(
            host_player,
            {"type": "escape", "menu_id": "action_input_menu"},
        )

        assert host_player.id not in game._pending_actions
        assert "turn_menu" in game.get_user(host_player).menus
    finally:
        server._db.close()
