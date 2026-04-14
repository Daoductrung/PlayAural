import os
import tempfile

import pytest

from server.auth.auth import AuthManager
from server.core.server import Server
from server.games.pig.game import PigGame, PigOptions
from server.messages.localization import Localization
from server.persistence.database import Database
from server.users.test_user import MockUser


class TestTableInviteReclaim:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_file.close()
        self.db = Database(self.temp_file.name)
        self.db.connect()
        self.server = Server(db_path=self.temp_file.name)
        self.server._db = self.db
        self.server._auth = AuthManager(self.db)

    def teardown_method(self):
        self.db.close()
        os.unlink(self.temp_file.name)

    def _create_online_user(self, username: str) -> MockUser:
        self.db.create_user(username, "Password123")
        record = self.db.get_user(username)
        assert record is not None
        user = MockUser(username, uuid=record.uuid)
        self.server._users[username] = user
        self.server._user_states[username] = {"menu": "main_menu"}
        return user

    def _create_started_table(
        self, host: MockUser, guest: MockUser
    ) -> tuple:
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        table.add_member(guest.username, guest, as_spectator=False)
        game.add_player(guest.username, guest)
        game.on_start()
        return table, game

    def _get_menu_action_ids(self, user: MockUser, menu_id: str) -> list[str]:
        items = user.get_current_menu_items(menu_id) or []
        return [item.id for item in items if hasattr(item, "id")]

    def _sound_names(self, user: MockUser) -> list[str]:
        return [message.data["name"] for message in user.messages if message.type == "play_sound"]

    @pytest.mark.asyncio
    async def test_new_table_created_sound_follows_new_table_notification_preference(self):
        host = self._create_online_user("Host")
        listener_on = self._create_online_user("ListenerOn")
        listener_off = self._create_online_user("ListenerOff")
        listener_off.preferences.notify_table_created = False

        await self.server._handle_tables_selection(
            host,
            "create_table",
            {"game_type": "pig", "game_name": "Pig"},
        )

        assert "table_created.ogg" in self._sound_names(listener_on)
        assert "table_created.ogg" not in self._sound_names(listener_off)
        assert listener_on.get_last_spoken() == Localization.get(
            listener_on.locale,
            "table-created-broadcast",
            host=host.username,
            game=Localization.get(listener_on.locale, "game-name-pig"),
        )
        assert listener_off.get_last_spoken() is None

    @pytest.mark.asyncio
    async def test_table_invite_always_plays_invite_notification_sound(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _ = self._create_started_table(host, guest)

        guest.preferences.notify_table_created = False

        await self.server._send_table_invite(host, table, guest)

        assert "table_invite.ogg" in self._sound_names(guest)
        assert guest.get_last_spoken() == Localization.get(
            guest.locale,
            "table-invite-received",
            host=host.username,
            game=Localization.get(guest.locale, "game-name-pig"),
        )

    @pytest.mark.asyncio
    async def test_accepting_invite_reclaims_bot_replaced_seat(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)

        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None

        game._perform_leave_game(guest_player)
        table.remove_member(guest.username)

        replaced = game.get_player_by_id(guest.uuid)
        assert replaced is not None
        assert replaced.is_bot is True

        await self.server._send_table_invite(host, table, guest)
        state = self.server._user_states[guest.username]
        await self.server._handle_table_invite_selection(guest, "accept", state)

        reclaimed = game.get_player_by_id(guest.uuid)
        assert reclaimed is not None
        assert reclaimed.is_bot is False
        assert reclaimed.replaced_human is False
        assert reclaimed.is_spectator is False
        assert game.get_user(reclaimed) is guest
        assert table.get_user(guest.username) is guest
        assert self.server._tables.find_user_table(guest.username) is table
        assert sum(1 for member in table.members if member.username == guest.username) == 1
        assert sum(1 for player in game.players if player.name == guest.username) == 1

    @pytest.mark.asyncio
    async def test_accepting_invite_reattaches_existing_table_member(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)

        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None

        game._replace_with_bot(guest_player)
        table._users.pop(guest.username, None)
        self.server._tables._username_to_table.pop(guest.username, None)

        await self.server._send_table_invite(host, table, guest)
        state = self.server._user_states[guest.username]
        await self.server._handle_table_invite_selection(guest, "accept", state)

        reclaimed = game.get_player_by_id(guest.uuid)
        assert reclaimed is not None
        assert reclaimed.is_bot is False
        assert reclaimed.replaced_human is False
        assert reclaimed.is_spectator is False
        assert game.get_user(reclaimed) is guest
        assert table.get_user(guest.username) is guest
        assert self.server._tables.find_user_table(guest.username) is table
        assert sum(1 for member in table.members if member.username == guest.username) == 1

    @pytest.mark.asyncio
    async def test_friend_join_reclaims_bot_replaced_seat(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)

        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None

        game._perform_leave_game(guest_player)
        table.remove_member(guest.username)

        await self.server._handle_friend_actions_selection(
            guest,
            "join_table",
            {"target_username": host.username},
        )

        reclaimed = game.get_player_by_id(guest.uuid)
        assert reclaimed is not None
        assert reclaimed.is_bot is False
        assert reclaimed.replaced_human is False
        assert reclaimed.is_spectator is False
        assert game.get_user(reclaimed) is guest
        assert table.get_user(guest.username) is guest
        assert self.server._tables.find_user_table(guest.username) is table
        assert sum(1 for member in table.members if member.username == guest.username) == 1

    @pytest.mark.asyncio
    async def test_friend_join_switches_active_tables_via_leave_logic(self):
        host_a = self._create_online_user("HostA")
        mover = self._create_online_user("Mover")
        host_b = self._create_online_user("HostB")
        guest_b = self._create_online_user("GuestB")

        table_a, game_a = self._create_started_table(host_a, mover)
        table_b, game_b = self._create_started_table(host_b, guest_b)

        await self.server._handle_friend_actions_selection(
            mover,
            "join_table",
            {"target_username": host_b.username},
        )

        moved_from = game_a.get_player_by_id(mover.uuid)
        assert moved_from is not None
        assert moved_from.is_bot is True
        assert moved_from.replaced_human is True
        assert sum(1 for member in table_a.members if member.username == mover.username) == 0
        assert self.server._tables.find_user_table(mover.username) is table_b

        moved_to = game_b.get_player_by_id(mover.uuid)
        assert moved_to is not None
        assert moved_to.is_spectator is True
        assert moved_to.is_bot is False
        assert game_b.get_user(moved_to) is mover
        assert table_b.get_user(mover.username) is mover
        assert sum(1 for member in table_b.members if member.username == mover.username) == 1

    def test_private_tables_are_hidden_from_public_lists_and_friend_join(self):
        host = self._create_online_user("Host")
        public_host = self._create_online_user("PublicHost")
        member = self._create_online_user("Member")
        outsider = self._create_online_user("Outsider")

        private_table = self.server._tables.create_table("pig", host.username, host)
        private_game = PigGame(options=PigOptions(target_score=25))
        private_table.game = private_game
        private_game._table = private_table
        private_game.initialize_lobby(host.username, host)
        private_table.is_private = True
        private_table.add_member(member.username, member, as_spectator=False)
        private_game.add_player(member.username, member)

        public_table = self.server._tables.create_table(
            "pig", public_host.username, public_host
        )
        public_game = PigGame(options=PigOptions(target_score=25))
        public_table.game = public_game
        public_game._table = public_table
        public_game.initialize_lobby(public_host.username, public_host)

        game_items = self.server._get_tables_menu_items(outsider, "pig")
        active_items = self.server._get_active_tables_menu_items(outsider)
        outsider_table_ids = {item.id for item in game_items + active_items if hasattr(item, "id")}

        assert f"table_{private_table.table_id}" not in outsider_table_ids
        assert f"table_{public_table.table_id}" in outsider_table_ids

        self.server._show_friend_actions_menu(outsider, host.username)
        assert "join_table" not in self._get_menu_action_ids(outsider, "friend_actions_menu")

        member_game_items = self.server._get_tables_menu_items(member, "pig")
        member_ids = {item.id for item in member_game_items if hasattr(item, "id")}
        assert f"table_{private_table.table_id}" in member_ids

    @pytest.mark.asyncio
    async def test_stale_game_tables_menu_cannot_join_after_table_becomes_private(self):
        host = self._create_online_user("Host")
        outsider = self._create_online_user("Outsider")

        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)

        self.server._show_tables_menu(outsider, "pig")
        menu_ids = self._get_menu_action_ids(outsider, "tables_menu")
        assert f"table_{table.table_id}" in menu_ids

        table.is_private = True

        await self.server._handle_tables_selection(
            outsider,
            f"table_{table.table_id}",
            self.server._user_states[outsider.username],
        )

        assert self.server._tables.find_user_table(outsider.username) is None
        assert outsider.get_last_spoken() == Localization.get(outsider.locale, "table-private-invite-only")
        refreshed_ids = self._get_menu_action_ids(outsider, "tables_menu")
        assert f"table_{table.table_id}" not in refreshed_ids

    @pytest.mark.asyncio
    async def test_stale_active_tables_menu_cannot_join_after_table_becomes_private(self):
        host = self._create_online_user("Host")
        outsider = self._create_online_user("Outsider")

        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)

        self.server._show_active_tables_menu(outsider)
        menu_ids = self._get_menu_action_ids(outsider, "active_tables_menu")
        assert f"table_{table.table_id}" in menu_ids

        table.is_private = True

        await self.server._handle_active_tables_selection(
            outsider,
            f"table_{table.table_id}",
        )

        assert self.server._tables.find_user_table(outsider.username) is None
        assert outsider.get_last_spoken() == Localization.get(outsider.locale, "table-private-invite-only")
        refreshed_ids = self._get_menu_action_ids(outsider, "active_tables_menu")
        assert f"table_{table.table_id}" not in refreshed_ids
