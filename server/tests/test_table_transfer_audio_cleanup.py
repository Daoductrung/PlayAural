from types import SimpleNamespace

import pytest

from ..core.server import Server
from ..games.pirates.game import PiratesGame
from ..users.test_user import MockUser


@pytest.mark.asyncio
async def test_creating_table_relinquishes_main_menu_music() -> None:
    server = Server(db_path=":memory:")
    server._db.connect()
    try:
        alice = MockUser("Alice", uuid="alice")
        server._users = {alice.username: alice}
        server._show_main_menu(alice)
        alice.clear_messages()

        await server._handle_tables_selection(
            alice,
            "create_table",
            {
                "game_type": "pig",
                "game_name": "Pig",
            },
        )

        table = server._tables.find_user_table(alice.username)
        assert table is not None
        assert table.game is not None
        assert table.game.status == "waiting"
        assert table.game.current_music == ""
        assert any(
            message.type == "stop_music"
            and message.data.get("handle") == "music"
            and message.data.get("fade_out_ms", 0) == 0
            for message in alice.messages
        )
        assert not alice.has_managed_audio(
            "music",
            handle="music",
            asset="mainmus.ogg",
        )
        assert not any(
            message.type == "play_music"
            for message in alice.messages
        )
    finally:
        server._db.close()


class _CurrentTableGame:
    def __init__(self, user: MockUser):
        self.status = "playing"
        self.players = [
            SimpleNamespace(
                id=user.uuid,
                name=user.username,
                is_bot=False,
                is_spectator=False,
            )
        ]
        self.left_players: list[str] = []

    def to_json(self) -> str:
        return "{}"

    def get_player_by_id(self, player_id: str):
        return next((player for player in self.players if player.id == player_id), None)

    def _perform_leave_game(self, player) -> None:
        self.left_players.append(player.id)


class _TargetTableGame:
    def __init__(self, host: MockUser):
        self.status = "waiting"
        self.players = [
            SimpleNamespace(
                id=host.uuid,
                name=host.username,
                is_bot=False,
                is_spectator=False,
            )
        ]

    def to_json(self) -> str:
        return "{}"

    def get_max_players(self) -> int:
        return 4

    def add_player(self, username: str, user: MockUser):
        self.players.append(
            SimpleNamespace(
                id=user.uuid,
                name=username,
                is_bot=False,
                is_spectator=False,
            )
        )
        user.play_music("target/music.ogg")
        user.play_ambience("target/ambience.ogg")

    def broadcast_l(self, *args, **kwargs) -> None:
        return None

    def broadcast_sound(self, *args, **kwargs) -> None:
        return None

    def play_table_join_sound(self, *args, **kwargs) -> None:
        return None

    def refresh_menus(self) -> None:
        return None


def test_direct_table_transfer_clears_audio_before_new_table_audio_starts() -> None:
    server = Server(db_path=":memory:")
    server._db.connect()
    try:
        alice = MockUser("Alice", uuid="alice")
        bob = MockUser("Bob", uuid="bob")
        server._users = {
            alice.username: alice,
            bob.username: bob,
        }

        current_table = server._tables.create_table("battle", alice.username, alice)
        current_table.game = _CurrentTableGame(alice)

        target_table = server._tables.create_table("pig", bob.username, bob)
        target_table.game = _TargetTableGame(bob)

        server._user_states[alice.username] = {
            "menu": "in_game",
            "table_id": current_table.table_id,
        }

        alice.clear_messages()
        server._auto_join_table(alice, target_table, "pig")

        message_types = [message.type for message in alice.messages]
        assert any(
            message.type == "audio"
            and message.data.get("command") == "stop_all"
            for message in alice.messages
        )
        assert "clear_ui" in message_types

        empty_context_index = next(
            index
            for index, message in enumerate(alice.messages)
            if message.type == "table_context" and message.data.get("table_id") == ""
        )
        new_context_index = next(
            index
            for index, message in enumerate(alice.messages)
            if message.type == "table_context"
            and message.data.get("table_id") == target_table.table_id
        )
        stop_all_index = next(
            index
            for index, message in enumerate(alice.messages)
            if message.type == "audio"
            and message.data.get("command") == "stop_all"
        )
        clear_ui_index = message_types.index("clear_ui")
        play_music_index = next(
            index
            for index, message in enumerate(alice.messages)
            if message.type == "play_music" and message.data.get("name") == "target/music.ogg"
        )
        play_ambience_index = next(
            index
            for index, message in enumerate(alice.messages)
            if message.type == "play_ambience"
            and message.data.get("loop") == "target/ambience.ogg"
        )

        assert empty_context_index < new_context_index
        assert stop_all_index < new_context_index
        assert clear_ui_index < new_context_index
        assert stop_all_index < play_music_index
        assert stop_all_index < play_ambience_index
        assert server._user_states[alice.username]["table_id"] == target_table.table_id
    finally:
        server._db.close()


def test_main_menu_teardown_requests_immediate_ambience_outros_before_music() -> None:
    server = Server(db_path=":memory:")
    alice = MockUser("Alice", uuid="alice")
    server._users = {alice.username: alice}

    alice.play_music("game_pirates/mus.ogg")
    alice.play_ambience(
        "game_pirates/amloop.ogg",
        intro="game_pirates/am_intro.ogg",
        outro="game_pirates/am_outro.ogg",
    )
    alice.clear_messages()

    server._show_main_menu(alice)

    stop_index = next(
        index
        for index, message in enumerate(alice.messages)
        if message.type == "audio"
        and message.data.get("command") == "stop_all"
    )
    stop_packet = alice.messages[stop_index].data
    menu_music_index = next(
        index
        for index, message in enumerate(alice.messages)
        if message.type == "play_music"
        and message.data.get("name") == "mainmus.ogg"
    )

    assert stop_packet["play_outros"] is True
    assert stop_packet.get("outro_mode", "immediate") == "immediate"
    assert stop_index < menu_music_index


@pytest.mark.asyncio
async def test_pirates_leave_table_splices_outro_before_main_menu_music() -> None:
    server = Server(db_path=":memory:")
    server._db.connect()
    try:
        alice = MockUser("Alice", uuid="alice")
        bob = MockUser("Bob", uuid="bob")
        server._users = {alice.username: alice, bob.username: bob}

        table = server._tables.create_table("pirates", alice.username, alice)
        game = PiratesGame()
        table.game = game
        game._table = table
        game.initialize_lobby(alice.username, alice)
        table.add_member(bob.username, bob, as_spectator=False)
        game.add_player(bob.username, bob)
        game.on_start()
        server._user_states[alice.username] = {
            "menu": "in_game",
            "table_id": table.table_id,
        }

        await server._handle_keybind(
            SimpleNamespace(username=alice.username),
            {"type": "keybind", "key": "ctrl+q"},
        )
        assert "leave_game_confirm" in alice.menus
        alice.clear_messages()

        await server._handle_menu(
            SimpleNamespace(username=alice.username),
            {
                "type": "menu",
                "menu_id": "leave_game_confirm",
                "selection_id": "yes",
            },
        )

        assert table.get_user(alice.username) is None
        assert server._user_states[alice.username]["menu"] == "main_menu"
        stop_index = next(
            index
            for index, message in enumerate(alice.messages)
            if message.type == "audio"
            and message.data.get("command") == "stop_all"
        )
        stop_packet = alice.messages[stop_index].data
        menu_music_index = next(
            index
            for index, message in enumerate(alice.messages)
            if message.type == "play_music"
            and message.data.get("name") == "mainmus.ogg"
        )
        assert stop_packet["play_outros"] is True
        assert stop_packet.get("outro_mode", "immediate") == "immediate"
        assert stop_index < menu_music_index
    finally:
        server._db.close()
