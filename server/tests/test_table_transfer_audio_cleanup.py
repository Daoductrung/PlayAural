from types import SimpleNamespace

from ..core.server import Server
from ..users.test_user import MockUser


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

    def rebuild_all_menus(self) -> None:
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
        assert "stop_music" in message_types
        assert "stop_ambience" in message_types
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
        stop_music_index = message_types.index("stop_music")
        stop_ambience_index = message_types.index("stop_ambience")
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
        assert stop_music_index < new_context_index
        assert stop_ambience_index < new_context_index
        assert clear_ui_index < new_context_index
        assert stop_music_index < play_music_index
        assert stop_ambience_index < play_ambience_index
        assert server._user_states[alice.username]["table_id"] == target_table.table_id
    finally:
        server._db.close()
