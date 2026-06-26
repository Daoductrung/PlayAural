import os
import tempfile
from types import SimpleNamespace

import pytest

from server.auth.auth import AuthManager
from server.core.server import Server, TABLE_MEMBERS_MENU, TABLE_MEMBER_ACTIONS_MENU
from server.games.crazyeights.game import CrazyEightsGame
from server.games.pig.game import PigGame, PigOptions
from server.messages.localization import Localization
from server.persistence.database import Database
from server.users.bot import Bot
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
        for invitee_name in list(self.server._pending_invites):
            self.server._cancel_invite(invitee_name)
        self.db.close()
        os.unlink(self.temp_file.name)

    def _create_online_user(self, username: str) -> MockUser:
        self.db.create_user(
            username,
            "Password123",
            approved=True,
            email=f"{username.lower()}@example.com",
        )
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

    def _create_waiting_table(self, host: MockUser, guest: MockUser, game):
        table = self.server._tables.create_table(game.get_type(), host.username, host)
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        table.add_member(guest.username, guest, as_spectator=False)
        game.add_player(guest.username, guest)
        game.refresh_menus()
        game.flush_menus()
        return table, game

    def _get_menu_action_ids(self, user: MockUser, menu_id: str) -> list[str]:
        items = user.get_current_menu_items(menu_id) or []
        return [item.id for item in items if hasattr(item, "id")]

    def _sound_names(self, user: MockUser) -> list[str]:
        return [message.data["name"] for message in user.messages if message.type == "play_sound"]

    def _add_named_bot(self, game: PigGame, name: str):
        bot_user = Bot(name)
        bot_player = game.create_player(bot_user.uuid, name, is_bot=True)
        game.players.append(bot_player)
        game.attach_user(bot_player.id, bot_user)
        game.setup_player_actions(bot_player)
        return bot_player

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
    async def test_host_invite_success_refreshes_invite_menu(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        friend = self._create_online_user("Friend")
        self.db.send_friend_request(host.uuid, friend.uuid)
        self.db.accept_friend_request(host.uuid, friend.uuid)
        table, _ = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )

        self.server._show_host_invite_menu(host, table)
        await self.server._handle_host_invite_selection(
            host,
            f"invite_{friend.username}",
            {"table_id": table.table_id},
        )

        assert self.server._user_states[host.username]["menu"] == "host_invite_menu"
        assert friend.username in self.server._pending_invites
        item_ids = self._get_menu_action_ids(host, "host_invite_menu")
        assert f"invite_{friend.username}" not in item_ids
        assert "back" in item_ids

    @pytest.mark.asyncio
    async def test_table_invite_info_line_does_not_dismiss_prompt(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        seated = self._create_online_user("Seated")
        table, _ = self._create_started_table(host, seated)

        await self.server._send_table_invite(host, table, guest)
        state = dict(self.server._user_states[guest.username])

        host.clear_messages()
        guest.clear_messages()
        await self.server._handle_table_invite_selection(guest, "", state)

        assert self.server._pending_invites[guest.username]["table_id"] == table.table_id
        assert self.server._user_states[guest.username]["menu"] == "table_invite_prompt"
        assert "table_invite_prompt" in guest.menus
        assert "host-invite-declined" not in host.get_spoken_messages()

        self.server._cancel_invite(guest.username)

    @pytest.mark.asyncio
    async def test_second_table_invite_does_not_replace_pending_invite(self):
        first_host = self._create_online_user("FirstHost")
        second_host = self._create_online_user("SecondHost")
        guest = self._create_online_user("Guest")
        first_seated = self._create_online_user("FirstSeated")
        second_seated = self._create_online_user("SecondSeated")
        first_table, _ = self._create_started_table(first_host, first_seated)
        second_table, _ = self._create_started_table(second_host, second_seated)

        await self.server._send_table_invite(first_host, first_table, guest)
        pending_task = self.server._pending_invites[guest.username]["task"]
        second_host.clear_messages()

        sent = await self.server._send_table_invite(second_host, second_table, guest)

        assert sent is False
        assert self.server._pending_invites[guest.username]["table_id"] == first_table.table_id
        assert self.server._pending_invites[guest.username]["task"] is pending_task
        assert second_host.get_last_spoken() == Localization.get(
            second_host.locale,
            "host-invite-already-pending",
        )

        self.server._cancel_invite(guest.username)

    @pytest.mark.asyncio
    async def test_table_invite_waits_until_private_message_input_finishes(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        friend = self._create_online_user("Friend")
        table, _ = self._create_started_table(host, friend)

        self.db.send_friend_request(guest.uuid, friend.uuid)
        self.db.send_friend_request(friend.uuid, guest.uuid)

        self.server._user_states[guest.username] = {"menu": "friend_actions_menu", "target_username": friend.username}
        guest.show_editbox(
            "send_pm_input",
            Localization.get(guest.locale, "enter-pm-message", username=friend.username),
            multiline=True,
        )
        self.server._enter_input_state(guest, "send_pm_input", target_username=friend.username)

        await self.server._send_table_invite(host, table, guest)

        assert self.server._user_states[guest.username]["menu"] == "send_pm_input"
        assert self.server._pending_invites[guest.username]["deferred"] is True
        assert self.server._pending_invites[guest.username]["task"] is not None
        assert "table_invite_prompt" not in guest.menus
        assert guest.get_last_spoken() == Localization.get(
            guest.locale,
            "table-invite-queued",
            host=host.username,
            game=Localization.get(guest.locale, "game-name-pig"),
        )

        client = SimpleNamespace(username=guest.username, authenticated=True)
        await self.server._on_client_message(client, {"type": "editbox", "text": "hello"})

        state = self.server._user_states[guest.username]
        assert state["menu"] == "table_invite_prompt"
        assert state["prev_state"]["menu"] == "friend_actions_menu"
        assert state["prev_state"]["target_username"] == friend.username
        assert self.server._pending_invites[guest.username]["deferred"] is False
        assert self.server._pending_invites[guest.username]["task"] is not None
        assert "table_invite_prompt" in guest.menus

        self.server._cancel_invite(guest.username)

    @pytest.mark.asyncio
    async def test_transient_private_message_input_escape_restores_parent_and_deferred_invite(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        friend = self._create_online_user("Friend")
        table, _ = self._create_started_table(host, friend)

        self.server._user_states[guest.username] = {
            "menu": "friend_actions_menu",
            "target_username": friend.username,
        }
        guest.show_editbox(
            "send_pm_input",
            Localization.get(guest.locale, "enter-pm-message", username=friend.username),
            multiline=True,
        )
        self.server._enter_input_state(guest, "send_pm_input", target_username=friend.username)

        await self.server._send_table_invite(host, table, guest)
        client = SimpleNamespace(username=guest.username, authenticated=True)
        await self.server._on_client_message(
            client,
            {"type": "escape", "menu_id": "send_pm_input"},
        )

        state = self.server._user_states[guest.username]
        assert state["menu"] == "table_invite_prompt"
        assert state["prev_state"]["menu"] == "friend_actions_menu"
        assert state["prev_state"]["target_username"] == friend.username
        assert self.server._pending_invites[guest.username]["deferred"] is False
        assert "table_invite_prompt" in guest.menus

        self.server._cancel_invite(guest.username)

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
        bot_name = replaced.name
        assert replaced.replaced_human_name == guest.username
        assert bot_name != guest.username

        await self.server._send_table_invite(host, table, guest)
        state = self.server._user_states[guest.username]
        host.clear_messages()
        guest.clear_messages()
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
        expected = Localization.get(
            guest.locale,
            "player-reclaimed-from-bot",
            player=guest.username,
            bot=bot_name,
        )
        assert expected in host.get_spoken_messages()
        assert expected in guest.get_spoken_messages()
        assert "join.ogg" in self._sound_names(host)
        assert "join.ogg" in self._sound_names(guest)

    @pytest.mark.asyncio
    async def test_accepting_invite_reattaches_existing_table_member(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)

        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None

        game._replace_with_bot(guest_player)
        bot_name = guest_player.name
        table._users.pop(guest.username, None)
        self.server._tables._username_to_table.pop(guest.username, None)

        await self.server._send_table_invite(host, table, guest)
        state = self.server._user_states[guest.username]
        host.clear_messages()
        guest.clear_messages()
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
        expected = Localization.get(
            guest.locale,
            "player-reclaimed-from-bot",
            player=guest.username,
            bot=bot_name,
        )
        assert expected in host.get_spoken_messages()
        assert expected in guest.get_spoken_messages()
        assert "join.ogg" in self._sound_names(host)
        assert "join.ogg" in self._sound_names(guest)

    def test_login_restore_reclaims_bot_replaced_seat_and_announces(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)

        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None

        game._replace_with_bot(guest_player)
        bot_name = guest_player.name
        table._users.pop(guest.username, None)
        host.clear_messages()
        guest.clear_messages()

        self.server._restore_user_state(guest, guest.username)

        reclaimed = game.get_player_by_id(guest.uuid)
        assert reclaimed is not None
        assert reclaimed.is_bot is False
        assert reclaimed.replaced_human is False
        assert reclaimed.is_spectator is False
        assert game.get_user(reclaimed) is guest
        assert table.get_user(guest.username) is guest
        assert self.server._tables.find_user_table(guest.username) is table
        assert self.server._user_states[guest.username] == {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        expected = Localization.get(
            guest.locale,
            "player-reclaimed-from-bot",
            player=guest.username,
            bot=bot_name,
        )
        assert expected in host.get_spoken_messages()
        assert expected in guest.get_spoken_messages()
        assert "join.ogg" in self._sound_names(host)
        assert "join.ogg" in self._sound_names(guest)

    @pytest.mark.asyncio
    async def test_join_player_reclaims_bot_replaced_seat_before_menu_rebuild(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)

        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None

        game._perform_leave_game(guest_player)
        table.remove_member(guest.username)
        bot_name = game.get_player_by_id(guest.uuid).name
        host.clear_messages()
        guest.clear_messages()

        await self.server._handle_join_selection(
            guest,
            "join_player",
            {"table_id": table.table_id, "game_type": "pig"},
        )

        reclaimed = game.get_player_by_id(guest.uuid)
        assert reclaimed is not None
        assert reclaimed.is_bot is False
        assert reclaimed.replaced_human is False
        assert reclaimed.is_spectator is False
        assert game.get_user(reclaimed) is guest
        assert table.get_user(guest.username) is guest
        assert self.server._user_states[guest.username] == {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        expected = Localization.get(
            guest.locale,
            "player-took-over",
            player=guest.username,
            bot=bot_name,
        )
        assert expected in host.get_spoken_messages()
        assert expected in guest.get_spoken_messages()
        assert "join.ogg" in self._sound_names(host)
        assert "join.ogg" in self._sound_names(guest)

    @pytest.mark.asyncio
    async def test_join_player_rejects_name_matching_existing_bot(self):
        host = self._create_online_user("Host")
        entrant = self._create_online_user("Test")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        self._add_named_bot(game, "Test")

        await self.server._handle_join_selection(
            entrant,
            "join_player",
            {"table_id": table.table_id, "game_type": "pig"},
        )

        assert self.server._tables.find_user_table(entrant.username) is None
        assert game.get_player_by_id(entrant.uuid) is None
        assert entrant.get_last_spoken() == Localization.get(
            entrant.locale,
            "table-name-already-used",
        )

    @pytest.mark.asyncio
    async def test_join_spectator_rejects_name_matching_existing_bot(self):
        host = self._create_online_user("Host")
        entrant = self._create_online_user("Test")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        self._add_named_bot(game, "Test")

        await self.server._handle_join_selection(
            entrant,
            "join_spectator",
            {"table_id": table.table_id, "game_type": "pig"},
        )

        assert self.server._tables.find_user_table(entrant.username) is None
        assert game.get_player_by_id(entrant.uuid) is None
        assert entrant.get_last_spoken() == Localization.get(
            entrant.locale,
            "table-name-already-used",
        )

    def test_custom_bot_name_rejects_registered_account_name(self):
        host = self._create_online_user("Host")
        self._create_online_user("Test")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        host.preferences.allow_custom_bot_names = True
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None

        game.execute_action(host_player, "add_bot")
        game.handle_event(
            host_player,
            {
                "type": "editbox",
                "input_id": "action_input_editbox",
                "text": "Test",
            },
        )

        assert not any(player.name == "Test" and player.is_bot for player in game.players)
        assert host.get_last_spoken() == Localization.get(
            host.locale,
            "bot-name-registered-account",
        )

    def test_generated_bot_name_skips_registered_account_name(self, monkeypatch):
        host = self._create_online_user("Host")
        self._create_online_user("Pho Pixel")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None
        monkeypatch.setattr(
            "server.game_utils.bot_names.random.choice",
            lambda options: options[0],
        )

        game.execute_action(host_player, "add_bot")

        bot_names = [player.name for player in game.players if player.is_bot]
        assert bot_names
        assert "Pho Pixel" not in bot_names

    def test_replacement_bot_name_skips_registered_account_name(self, monkeypatch):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        self._create_online_user("Pho Pixel")
        table, game = self._create_started_table(host, guest)
        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None
        monkeypatch.setattr(
            "server.game_utils.bot_names.random.choice",
            lambda options: options[0],
        )

        game._replace_with_bot(guest_player)

        assert guest_player.is_bot is True
        assert guest_player.name != "Pho Pixel"

    def test_disconnect_replacement_bot_survives_stale_waiting_table_status(
        self, monkeypatch
    ):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        table.status = "waiting"
        table._member_offline_since[guest.username] = 0.0

        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None
        game.on_player_disconnect(guest.uuid)
        self.server._users.pop(guest.username, None)

        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None
        assert replacement.is_bot is True
        bot_name = replacement.name
        host.clear_messages()
        monkeypatch.setattr("server.tables.table.time.time", lambda: 20.0)

        table.on_tick()

        replacement = game.get_player_by_id(guest.uuid)
        assert table.status == "playing"
        assert replacement is not None
        assert replacement.is_bot is True
        assert replacement.name == bot_name
        assert replacement.replaced_human_name == guest.username
        assert any(member.username == guest.username for member in table.members)
        assert self.server._tables.get_table(table.table_id) is table
        assert Localization.get(
            host.locale,
            "player-kicked-offline",
            player=guest.username,
        ) not in host.get_spoken_messages()

    @pytest.mark.asyncio
    async def test_unexpected_disconnect_replacement_plays_table_leave_sound(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        guest.connection = object()
        client = SimpleNamespace(username=guest.username, address="guest-client")
        host.clear_messages()

        await self.server._on_client_disconnect(client)

        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None
        assert replacement.is_bot is True
        assert replacement.replaced_human_name == guest.username
        assert "leave.ogg" in self._sound_names(host)
        assert Localization.get(
            host.locale,
            "player-replaced-by-bot",
            player=guest.username,
            bot=replacement.name,
        ) in host.get_spoken_messages()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_ban", [False, True])
    async def test_host_kick_plays_default_table_leave_sound(self, is_ban):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _ = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        host.clear_messages()

        await self.server._handle_host_kick_selection(
            host,
            f"kick_{guest.username}",
            {"table_id": table.table_id, "ban": is_ban},
        )

        assert "leave.ogg" in self._sound_names(host)
        assert all(member.username != guest.username for member in table.members)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_ban", [False, True])
    async def test_host_kick_success_refreshes_menu_when_candidates_run_out(self, is_ban):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _ = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        self.server._show_host_kick_menu(host, table, ban=is_ban)

        await self.server._handle_host_kick_selection(
            host,
            f"kick_{guest.username}",
            {"table_id": table.table_id, "ban": is_ban},
        )

        expected_menu = "host_kick_ban_menu" if is_ban else "host_kick_menu"
        assert self.server._user_states[host.username]["menu"] == expected_menu
        item_ids = self._get_menu_action_ids(host, expected_menu)
        assert item_ids == ["", "back"]

    @pytest.mark.asyncio
    async def test_host_pass_success_refreshes_with_no_longer_host_state(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _ = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        self.server._show_host_pass_menu(host, table)

        await self.server._handle_host_pass_selection(
            host,
            f"pass_{guest.username}",
            {"table_id": table.table_id},
        )

        assert table.host == guest.username
        assert self.server._user_states[host.username]["menu"] == "host_pass_menu"
        items = host.get_current_menu_items("host_pass_menu") or []
        assert [item.id for item in items] == ["", "back"]
        assert any("You passed host to another player" in item.text for item in items)

    @pytest.mark.asyncio
    async def test_host_pass_menu_auto_refreshes_when_player_joins(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        newcomer = self._create_online_user("Newcomer")
        table, game = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )

        self.server._show_host_pass_menu(host, table)
        table.add_member(newcomer.username, newcomer, as_spectator=False)
        game.add_player(newcomer.username, newcomer)

        item_ids = self._get_menu_action_ids(host, "host_pass_menu")
        assert f"pass_{newcomer.username}" in item_ids

    @pytest.mark.asyncio
    async def test_online_friend_selection_opens_friend_actions_and_back_returns_online_list(self):
        viewer = self._create_online_user("Viewer")
        friend = self._create_online_user("Friend")
        self.db.send_friend_request(viewer.uuid, friend.uuid)
        self.db.accept_friend_request(viewer.uuid, friend.uuid)

        self.server._show_online_users_menu(viewer)
        await self.server._handle_online_users_selection(
            viewer,
            f"online_{friend.username}",
            self.server._user_states[viewer.username],
        )

        assert self.server._user_states[viewer.username]["menu"] == "friend_actions_menu"
        item_ids = self._get_menu_action_ids(viewer, "friend_actions_menu")
        assert "send_pm" in item_ids
        assert "remove_friend" in item_ids

        await self.server._handle_friend_actions_selection(
            viewer,
            "back",
            self.server._user_states[viewer.username],
        )

        assert self.server._user_states[viewer.username]["menu"] == "online_users"

    @pytest.mark.asyncio
    async def test_whos_at_table_opens_interactive_roster_with_host_and_social_actions(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        host_player = game.get_player_by_name(host.username)
        assert host_player is not None

        game._action_whos_at_table(host_player, "whos_at_table")

        assert self.server._user_states[host.username]["menu"] == TABLE_MEMBERS_MENU
        roster_items = host.get_current_menu_items(TABLE_MEMBERS_MENU) or []
        assert roster_items[0].id == ""
        assert "Table summary" in roster_items[0].text
        own_row = next(item for item in roster_items if item.text.startswith("Host:"))
        assert own_row.id == ""
        assert "Host" in own_row.text
        assert "Player" in own_row.text
        assert f"table_member_user_{guest.username}" in [
            item.id for item in roster_items if hasattr(item, "id")
        ]

        await self.server._handle_table_members_selection(
            host,
            f"table_member_user_{guest.username}",
            self.server._user_states[host.username],
        )

        assert self.server._user_states[host.username]["menu"] == TABLE_MEMBER_ACTIONS_MENU
        action_ids = self._get_menu_action_ids(host, TABLE_MEMBER_ACTIONS_MENU)
        assert "table_pass_host" in action_ids
        assert "table_kick" in action_ids
        assert "table_kick_ban" in action_ids
        assert "view_profile" in action_ids
        assert "send_friend_request" in action_ids

        await self.server._handle_table_member_actions_selection(
            host,
            "back",
            self.server._user_states[host.username],
        )
        assert self.server._user_states[host.username]["menu"] == TABLE_MEMBERS_MENU

    @pytest.mark.asyncio
    async def test_table_roster_shows_multiple_statuses_and_blocks_self_selection(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        host_player = game.get_player_by_name(host.username)
        assert host_player is not None
        host_player.is_spectator = True
        for member in table.members:
            if member.username == host.username:
                member.is_spectator = True

        self.server._show_table_members_menu(host, table)
        roster_items = host.get_current_menu_items(TABLE_MEMBERS_MENU) or []
        own_row = next(item for item in roster_items if item.text.startswith("Host:"))
        assert own_row.id == ""
        assert "Host" in own_row.text
        assert "Spectator" in own_row.text

        await self.server._handle_table_members_selection(
            host,
            f"table_member_user_{host.username}",
            self.server._user_states[host.username],
        )

        assert self.server._user_states[host.username]["menu"] == TABLE_MEMBERS_MENU

    def test_table_roster_sorts_players_before_spectators_and_shows_voice_status(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        spectator = self._create_online_user("AaronSpectator")
        table, game = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        table.add_member(spectator.username, spectator, as_spectator=True)
        game.add_spectator(spectator.username, spectator)
        self.server._voice_presence_by_user[guest.username] = {
            "scope": "table",
            "context_id": table.table_id,
        }

        self.server._show_table_members_menu(host, table)

        roster_items = host.get_current_menu_items(TABLE_MEMBERS_MENU) or []
        row_texts = [
            item.text
            for item in roster_items
            if item.text not in {"Back"} and not item.text.startswith("Table summary")
        ]
        positions = {
            text.split(":", 1)[0]: index
            for index, text in enumerate(row_texts)
        }
        assert positions[guest.username] < positions[spectator.username]
        assert positions[host.username] < positions[spectator.username]
        guest_row = next(text for text in row_texts if text.startswith(f"{guest.username}:"))
        spectator_row = next(
            text for text in row_texts if text.startswith(f"{spectator.username}:")
        )
        assert "Player" in guest_row
        assert "Online" in guest_row
        assert "in voice chat" in guest_row
        assert "Spectator" in spectator_row
        assert "Online" in spectator_row

    @pytest.mark.asyncio
    async def test_table_roster_shows_offline_replaced_player_and_takeover_bot(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None

        assert game._replace_with_bot(guest_player) is True
        replacement_bot_name = guest_player.name
        self.server._users.pop(guest.username, None)

        self.server._show_table_members_menu(host, table)
        roster_items = host.get_current_menu_items(TABLE_MEMBERS_MENU) or []
        row_texts = [item.text for item in roster_items]
        assert "1 bot" in roster_items[0].text
        guest_row = next(text for text in row_texts if text.startswith(f"{guest.username}:"))
        assert "Player" in guest_row
        assert "Offline" in guest_row
        assert f"bot playing on their behalf: {replacement_bot_name}" in guest_row
        assert not any(
            text.startswith(f"{replacement_bot_name}:")
            for text in row_texts
        )

        self.server._show_host_kick_menu(host, table, ban=False)
        host_kick_items = host.get_current_menu_items("host_kick_menu") or []
        kick_row = next(
            item.text for item in host_kick_items if item.id == f"kick_{guest.username}"
        )
        assert "Offline" in kick_row
        assert f"bot playing on their behalf: {replacement_bot_name}" in kick_row

        self.server._show_table_members_menu(host, table)

        await self.server._handle_table_members_selection(
            host,
            f"table_member_user_{guest.username}",
            self.server._user_states[host.username],
        )
        action_ids = self._get_menu_action_ids(host, TABLE_MEMBER_ACTIONS_MENU)
        assert "table_pass_host" not in action_ids
        assert "table_kick" in action_ids
        assert "table_kick_ban" in action_ids

        await self.server._handle_table_member_actions_selection(
            host,
            "table_kick",
            self.server._user_states[host.username],
        )

        assert not any(member.username == guest.username for member in table.members)
        refreshed_items = host.get_current_menu_items(TABLE_MEMBERS_MENU) or []
        refreshed_texts = [item.text for item in refreshed_items]
        assert not any(text.startswith(f"{guest.username}:") for text in refreshed_texts)
        assert any(
            text.startswith(f"{replacement_bot_name}:")
            for text in refreshed_texts
        )

    @pytest.mark.asyncio
    async def test_table_roster_bot_actions_remove_selected_bot(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        bot = self._add_named_bot(game, "Botty")

        self.server._show_table_members_menu(host, table)
        await self.server._handle_table_members_selection(
            host,
            f"table_member_bot_{bot.id}",
            self.server._user_states[host.username],
        )

        action_ids = self._get_menu_action_ids(host, TABLE_MEMBER_ACTIONS_MENU)
        assert "table_remove_bot" in action_ids

        await self.server._handle_table_member_actions_selection(
            host,
            "table_remove_bot",
            self.server._user_states[host.username],
        )

        assert not any(player.id == bot.id for player in game.players)
        assert self.server._user_states[host.username]["menu"] == TABLE_MEMBERS_MENU

    @pytest.mark.asyncio
    async def test_host_kick_uses_crazyeights_custom_table_leave_sound(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _ = self._create_waiting_table(host, guest, CrazyEightsGame())
        host.clear_messages()

        await self.server._handle_host_kick_selection(
            host,
            f"kick_{guest.username}",
            {"table_id": table.table_id, "ban": True},
        )

        sounds = self._sound_names(host)
        assert "game_crazyeights/personleave.ogg" in sounds
        assert "leave.ogg" not in sounds
        assert all(member.username != guest.username for member in table.members)

    def test_last_human_disconnect_survives_stale_waiting_table_status(
        self, monkeypatch
    ):
        host = self._create_online_user("Host")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        game.on_start()
        table.status = "waiting"
        table._member_offline_since[host.username] = 0.0

        game.on_player_disconnect(host.uuid)
        self.server._users.pop(host.username, None)
        host.clear_messages()
        monkeypatch.setattr("server.tables.table.time.time", lambda: 20.0)

        table.on_tick()

        host_player = game.get_player_by_id(host.uuid)
        assert table.status == "playing"
        assert host_player is not None
        assert host_player.is_bot is False
        assert any(member.username == host.username for member in table.members)
        assert self.server._tables.get_table(table.table_id) is table
        assert Localization.get(
            host.locale,
            "player-kicked-offline",
            player=host.username,
        ) not in host.get_spoken_messages()

    def test_lobby_disconnected_player_becomes_reclaimable_bot_on_start(
        self, monkeypatch
    ):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        table.add_member(guest.username, guest, as_spectator=False)
        game.add_player(guest.username, guest)
        table._member_offline_since[guest.username] = 0.0
        self.server._users.pop(guest.username, None)
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None

        game.execute_action(host_player, "start_game")

        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None
        assert game.status == "playing"
        assert table.status == "playing"
        assert replacement.is_bot is True
        assert replacement.replaced_human is True
        assert replacement.replaced_human_name == guest.username
        assert replacement.name != guest.username
        assert any(member.username == guest.username for member in table.members)
        assert Localization.get(
            host.locale,
            "player-replaced-by-bot",
            player=guest.username,
            bot=replacement.name,
        ) in host.get_spoken_messages()
        assert "leave.ogg" in self._sound_names(host)

        host.clear_messages()
        monkeypatch.setattr("server.tables.table.time.time", lambda: 20.0)
        table.on_tick()

        assert game.get_player_by_id(guest.uuid) is replacement
        assert any(member.username == guest.username for member in table.members)
        assert self.server._tables.get_table(table.table_id) is table
        assert Localization.get(
            host.locale,
            "player-kicked-offline",
            player=guest.username,
        ) not in host.get_spoken_messages()

    def test_lobby_replacement_bot_can_be_reclaimed_during_team_arrangement(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        third = self._create_online_user("Third")
        fourth = self._create_online_user("Fourth")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25, team_mode="2v2"))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        for user in (guest, third, fourth):
            table.add_member(user.username, user, as_spectator=False)
            game.add_player(user.username, user)

        table._member_offline_since[guest.username] = 0.0
        self.server._users.pop(guest.username, None)
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None

        game.execute_action(host_player, "start_game")

        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None
        bot_name = replacement.name
        assert game.status == "waiting"
        assert game.team_arrangement_active is True
        assert replacement.is_bot is True
        assert game.team_manager.get_team(bot_name) is not None

        self.server._users[guest.username] = guest
        host.clear_messages()
        guest.clear_messages()

        self.server._auto_join_table(guest, table, table.game_type)

        reclaimed = game.get_player_by_id(guest.uuid)
        assert reclaimed is not None
        assert reclaimed.is_bot is False
        assert reclaimed.name == guest.username
        assert game.team_arrangement_active is True
        assert game.team_manager.get_team(guest.username) is not None
        assert game.team_manager.get_team(bot_name) is None
        assert Localization.get(
            host.locale,
            "player-reclaimed-from-bot",
            player=guest.username,
            bot=bot_name,
        ) in host.get_spoken_messages()

    def test_lobby_disconnected_spectator_is_removed_before_start(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        spectator = self._create_online_user("Spectator")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        table.add_member(guest.username, guest, as_spectator=False)
        game.add_player(guest.username, guest)
        table.add_member(spectator.username, spectator, as_spectator=True)
        game.add_spectator(spectator.username, spectator)
        table._member_offline_since[spectator.username] = 0.0
        self.server._users.pop(spectator.username, None)
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None

        game.execute_action(host_player, "start_game")

        assert game.status == "playing"
        assert game.get_player_by_id(spectator.uuid) is None
        assert not any(
            member.username == spectator.username for member in table.members
        )
        assert spectator.username not in table._member_offline_since

    def test_table_reset_converts_replacement_bot_to_fresh_bot_identity(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)

        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None
        game._perform_leave_game(guest_player)
        table.remove_member(guest.username)

        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None
        assert replacement.is_bot is True
        assert replacement.replaced_human is True
        replacement_name = replacement.name

        assert table.reset_game()
        assert table.game is not None
        fresh_bot = next(
            player
            for player in table.game.players
            if player.is_bot and player.name == replacement_name
        )
        assert fresh_bot.id != guest.uuid
        assert fresh_bot.replaced_human is False

    @pytest.mark.asyncio
    async def test_friend_join_reclaims_bot_replaced_seat(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)

        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None

        game._perform_leave_game(guest_player)
        table.remove_member(guest.username)
        bot_name = game.get_player_by_id(guest.uuid).name
        host.clear_messages()
        guest.clear_messages()

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
        expected = Localization.get(
            guest.locale,
            "player-reclaimed-from-bot",
            player=guest.username,
            bot=bot_name,
        )
        assert expected in host.get_spoken_messages()
        assert expected in guest.get_spoken_messages()
        assert "join.ogg" in self._sound_names(host)
        assert "join.ogg" in self._sound_names(guest)

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
