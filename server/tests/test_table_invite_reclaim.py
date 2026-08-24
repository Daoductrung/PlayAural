import asyncio
import json
import os
import tempfile
from contextlib import suppress
from types import SimpleNamespace

import pytest

from server.auth.auth import AuthManager
from server.core.server import Server, TABLE_MEMBERS_MENU, TABLE_MEMBER_ACTIONS_MENU
from server.games.crazyeights.game import CrazyEightsGame
from server.games.pig.game import PigGame, PigOptions
from server.messages.localization import Localization
from server.persistence.database import Database
from server.tables.table import ABANDONED_ACTIVE_TABLE_TIMEOUT_SECONDS
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

    def _create_single_human_started_table(self):
        host = self._create_online_user("Host")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        bot = Bot("Botty")
        game.add_player(bot.username, bot)
        game.on_start()
        return host, table, game

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

    def _save_pig_game(
        self,
        owner: MockUser,
        *participants: MockUser,
        replace: MockUser | None = None,
    ):
        """Create one valid user save using the production member schema."""
        game = PigGame(options=PigOptions(target_score=25))
        game.initialize_lobby(owner.username, owner)
        for participant in participants:
            game.add_player(participant.username, participant)
        if replace:
            game.status = "playing"
            player = game.get_player_by_id(replace.uuid)
            assert player is not None
            assert game._replace_with_bot(player)
        members_data = [
            {
                "player_id": player.id,
                "username": player.name,
                "is_bot": player.is_bot,
                "replaced_human": player.replaced_human,
                "replaced_human_name": player.replaced_human_name,
            }
            for player in game.players
            if not player.is_spectator
        ]
        return self.db.save_user_table(
            owner.username,
            "Saved Pig game",
            game.get_type(),
            game.to_json(),
            json.dumps(members_data),
        )

    def test_live_mobile_to_desktop_handover_rebuilds_global_overlay(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        player = game.get_player_by_id(host.uuid)
        assert player is not None
        player.reconnect_grace_ticks = 6
        host.client_type = "mobile"
        self.server._user_states[host.username] = {
            "menu": "mobile_voice_selection_menu",
            "_stack": [
                {"menu": "in_game", "table_id": table.table_id},
                {"menu": "options_accessibility_submenu"},
            ],
        }

        replacement = MockUser(host.username, uuid=host.uuid)
        replacement.client_type = "python"
        guest.clear_messages()
        self.server._users[host.username] = replacement
        self.server._restore_user_state(
            replacement,
            host.username,
            session_handover=True,
        )

        assert table.get_user(host.username) is replacement
        assert game.get_user(player) is replacement
        assert player.reconnect_grace_ticks == 6
        assert (
            self.server._user_states[host.username]["menu"]
            == "options_accessibility_submenu"
        )
        item_ids = self._get_menu_action_ids(
            replacement,
            "options_accessibility_submenu",
        )
        assert item_ids == [
            "show_menu_hints",
            "invert_multiline_enter",
            "back",
        ]
        assert "reconnect.ogg" not in self._sound_names(guest)

    @pytest.mark.asyncio
    async def test_new_table_created_sound_follows_new_table_notification_preference(self):
        host = self._create_online_user("Host")
        listener_on = self._create_online_user("ListenerOn")
        listener_off = self._create_online_user("ListenerOff")
        listener_blocked = self._create_online_user("ListenerBlocked")
        listener_off.preferences.notify_table_created = False
        assert self.db.block_user(listener_blocked.uuid, host.uuid) == "blocked"

        await self.server._handle_tables_selection(
            host,
            "create_table",
            {"game_type": "pig", "game_name": "Pig"},
        )

        assert "table_created.ogg" in self._sound_names(listener_on)
        assert "table_created.ogg" not in self._sound_names(listener_off)
        assert "table_created.ogg" not in self._sound_names(listener_blocked)
        assert listener_on.get_last_spoken() == Localization.get(
            listener_on.locale,
            "table-created-broadcast",
            host=host.username,
            game=Localization.get(listener_on.locale, "game-name-pig"),
        )
        assert listener_off.get_last_spoken() is None
        assert listener_blocked.get_last_spoken() is None

    @pytest.mark.parametrize("host_blocks_entrant", [True, False])
    def test_host_block_hides_table_and_denies_new_entry_without_forcing_transfer(
        self,
        host_blocks_entrant: bool,
    ):
        host = self._create_online_user("Host")
        entrant = self._create_online_user("Entrant")
        current_host = self._create_online_user("CurrentHost")

        target_table = self.server._tables.create_table("pig", host.username, host)
        target_game = PigGame(options=PigOptions(target_score=25))
        target_table.game = target_game
        target_game._table = target_table
        target_game.initialize_lobby(host.username, host)

        current_game = PigGame(options=PigOptions(target_score=25))
        current_table, _ = self._create_waiting_table(
            current_host,
            entrant,
            current_game,
        )

        self.server._show_active_tables_menu(entrant)
        assert f"table_{target_table.table_id}" in self._get_menu_action_ids(
            entrant,
            "active_tables_menu",
        )

        blocker = host if host_blocks_entrant else entrant
        blocked = entrant if host_blocks_entrant else host
        assert self.server._perform_block_user(blocker, blocked.username)

        assert f"table_{target_table.table_id}" not in self._get_menu_action_ids(
            entrant,
            "active_tables_menu",
        )
        entrant.clear_messages()
        self.server._auto_join_table(entrant, target_table, target_table.game_type)

        assert self.server._tables.find_user_table(entrant.username) is current_table
        assert target_game.get_player_by_id(entrant.uuid) is None
        assert entrant.get_last_spoken() == Localization.get(
            entrant.locale,
            "table-join-social-blocked",
        )

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

        client = SimpleNamespace(
            username=guest.username,
            authenticated=True,
            retired=False,
        )
        guest.connection = client
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
        client = SimpleNamespace(
            username=guest.username,
            authenticated=True,
            retired=False,
        )
        guest.connection = client
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
        await asyncio.sleep(0)

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
        assert "table_invite_prompt" not in guest.menus
        assert "turn_menu" in guest.menus
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
        assert "reconnect.ogg" in self._sound_names(host)
        assert "reconnect.ogg" in self._sound_names(guest)

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
        await asyncio.sleep(0)

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
        assert "reconnect.ogg" in self._sound_names(host)
        assert "reconnect.ogg" in self._sound_names(guest)

    @pytest.mark.asyncio
    async def test_host_transfer_cancels_invite_blocked_by_new_host(self):
        original_host = self._create_online_user("OriginalHost")
        new_host = self._create_online_user("NewHost")
        invitee = self._create_online_user("Invitee")
        table = self.server._tables.create_table(
            "pig",
            original_host.username,
            original_host,
        )
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(original_host.username, original_host)
        table.add_member(new_host.username, new_host, as_spectator=False)
        game.add_player(new_host.username, new_host)

        assert await self.server._send_table_invite(original_host, table, invitee)
        invite_state = self.server._user_states[invitee.username]
        assert self.server._perform_block_user(new_host, invitee.username)
        assert invitee.username in self.server._pending_invites
        assert self.server._perform_host_pass(
            original_host,
            table,
            new_host.username,
        )

        assert invitee.username not in self.server._pending_invites
        assert self.server._tables.find_user_table(invitee.username) is None
        assert (
            self.server._user_states[invitee.username]["menu"]
            == invite_state["prev_state"]["menu"]
        )
        assert "table_invite_prompt" not in invitee.menus

    def test_host_transfer_and_block_preserve_member_reconnect(self):
        original_host = self._create_online_user("OriginalHost")
        new_host = self._create_online_user("NewHost")
        guest = self._create_online_user("Guest")
        table = self.server._tables.create_table(
            "pig",
            original_host.username,
            original_host,
        )
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(original_host.username, original_host)
        for member in (new_host, guest):
            table.add_member(member.username, member, as_spectator=False)
            game.add_player(member.username, member)

        assert self.server._perform_block_user(new_host, guest.username)
        assert self.server._perform_host_pass(
            original_host,
            table,
            new_host.username,
        )
        assert table.host == new_host.username
        assert table.get_user(guest.username) is guest

        game.on_start()
        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None
        assert game._replace_with_bot(guest_player)
        table._users.pop(guest.username, None)

        guest.clear_messages()
        self.server._restore_user_state(guest, guest.username)

        reclaimed = game.get_player_by_id(guest.uuid)
        assert reclaimed is not None
        assert reclaimed.is_bot is False
        assert table.get_user(guest.username) is guest
        assert self.server._tables.find_user_table(guest.username) is table

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("restorer_blocks_guest", "message_key"),
        [
            (True, "saved-table-blocked-by-you"),
            (False, "saved-table-social-blocked"),
        ],
    )
    async def test_saved_table_restore_reports_block_direction_actionably(
        self,
        restorer_blocks_guest: bool,
        message_key: str,
    ):
        restorer = self._create_online_user("Restorer")
        guest = self._create_online_user("Guest")
        record = self._save_pig_game(restorer, guest)
        blocker = restorer if restorer_blocks_guest else guest
        blocked = guest if restorer_blocks_guest else restorer
        assert self.server._perform_block_user(blocker, blocked.username)

        restorer.clear_messages()
        await self.server._restore_saved_table(restorer, record.id)

        assert self.server._tables.find_user_table(restorer.username) is None
        assert self.server._tables.find_user_table(guest.username) is None
        assert self.db.get_saved_table(record.id) is not None
        assert restorer.get_last_spoken() == Localization.get(
            restorer.locale,
            message_key,
            players=guest.username,
        )

    @pytest.mark.asyncio
    async def test_saved_table_restore_reports_mixed_block_directions_once(self):
        restorer = self._create_online_user("Restorer")
        blocked_by_restorer = self._create_online_user("BlockedByRestorer")
        blocks_restorer = self._create_online_user("BlocksRestorer")
        record = self._save_pig_game(
            restorer,
            blocked_by_restorer,
            blocks_restorer,
        )
        assert self.server._perform_block_user(
            restorer,
            blocked_by_restorer.username,
        )
        assert self.server._perform_block_user(
            blocks_restorer,
            restorer.username,
        )

        restorer.clear_messages()
        await self.server._restore_saved_table(restorer, record.id)

        assert self.server._tables.find_user_table(restorer.username) is None
        assert self.db.get_saved_table(record.id) is not None
        assert restorer.get_last_spoken() == Localization.get(
            restorer.locale,
            "saved-table-social-blocked-mixed",
            blocked=blocked_by_restorer.username,
            unavailable=blocks_restorer.username,
        )

    @pytest.mark.asyncio
    async def test_saved_table_reports_restorer_block_before_offline_status(self):
        restorer = self._create_online_user("Restorer")
        guest = self._create_online_user("Guest")
        record = self._save_pig_game(restorer, guest)
        assert self.server._perform_block_user(restorer, guest.username)
        self.server._users.pop(guest.username)

        restorer.clear_messages()
        await self.server._restore_saved_table(restorer, record.id)

        assert self.db.get_saved_table(record.id) is not None
        assert restorer.get_last_spoken() == Localization.get(
            restorer.locale,
            "saved-table-blocked-by-you",
            players=guest.username,
        )

    @pytest.mark.asyncio
    async def test_saved_table_restore_reclaims_replaced_human(self):
        restorer = self._create_online_user("Restorer")
        guest = self._create_online_user("Guest")
        record = self._save_pig_game(restorer, guest, replace=guest)

        await self.server._restore_saved_table(restorer, record.id)

        table = self.server._tables.find_user_table(restorer.username)
        assert table is not None
        assert self.server._tables.find_user_table(guest.username) is table
        restored = table.game.get_player_by_id(guest.uuid)
        assert restored is not None
        assert restored.is_bot is False
        assert restored.replaced_human is False
        assert restored.name == guest.username
        assert self.db.get_saved_table(record.id) is None

    @pytest.mark.asyncio
    async def test_invalid_saved_table_is_retained_without_partial_table(self):
        restorer = self._create_online_user("Restorer")
        record = self.db.save_user_table(
            restorer.username,
            "Invalid save",
            "pig",
            "{}",
            "[]",
        )

        await self.server._restore_saved_table(restorer, record.id)

        assert self.server._tables.find_user_table(restorer.username) is None
        assert self.db.get_saved_table(record.id) is not None
        assert restorer.get_last_spoken() == Localization.get(
            restorer.locale,
            "saved-table-invalid",
        )

    @pytest.mark.asyncio
    async def test_saved_table_restore_and_delete_are_owner_scoped(self):
        owner = self._create_online_user("Owner")
        other = self._create_online_user("Other")
        record = self._save_pig_game(owner)

        await self.server._restore_saved_table(other, record.id)
        assert self.server._tables.find_user_table(other.username) is None
        assert self.db.get_saved_table(record.id) is not None
        assert other.get_last_spoken() == Localization.get(
            other.locale,
            "table-not-exists",
        )

        other.clear_messages()
        await self.server._handle_saved_table_actions_selection(
            other,
            "delete",
            {"save_id": record.id},
        )
        assert self.db.get_saved_table(record.id) is not None
        assert other.get_last_spoken() == Localization.get(
            other.locale,
            "table-not-exists",
        )

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
        assert "reconnect.ogg" in self._sound_names(host)
        assert "reconnect.ogg" in self._sound_names(guest)

    def test_auto_join_reclaims_bot_replaced_seat_before_menu_rebuild(self):
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

        self.server._auto_join_table(guest, table, table.game_type)

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
            "player-reclaimed-from-bot",
            player=guest.username,
            bot=bot_name,
        )
        assert expected in host.get_spoken_messages()
        assert expected in guest.get_spoken_messages()
        assert "reconnect.ogg" in self._sound_names(host)
        assert "reconnect.ogg" in self._sound_names(guest)

    def test_auto_join_rejects_name_matching_existing_bot(self):
        host = self._create_online_user("Host")
        entrant = self._create_online_user("Test")
        current_host = self._create_online_user("CurrentHost")
        current_table, _ = self._create_waiting_table(
            current_host,
            entrant,
            PigGame(options=PigOptions(target_score=25)),
        )
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        self._add_named_bot(game, "Test")

        self.server._auto_join_table(entrant, table, table.game_type)

        assert self.server._tables.find_user_table(entrant.username) is current_table
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
    async def test_unexpected_disconnect_replacement_plays_disconnect_sound(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        client = SimpleNamespace(
            username=guest.username,
            address="guest-client",
            authenticated=True,
            retired=False,
        )
        guest.connection = client
        host.clear_messages()

        await self.server._on_client_disconnect(client)
        await asyncio.sleep(0)

        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None
        assert replacement.is_bot is True
        assert replacement.replaced_human_name == guest.username
        assert "disconnect.ogg" in self._sound_names(host)
        assert Localization.get(
            host.locale,
            "player-replaced-by-bot",
            player=guest.username,
            bot=replacement.name,
        ) in host.get_spoken_messages()

    @pytest.mark.asyncio
    async def test_waiting_member_disconnect_and_reconnect_use_connection_cues(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        client = SimpleNamespace(
            username=guest.username,
            address="guest-client",
            authenticated=True,
            retired=False,
        )
        guest.connection = client
        host.clear_messages()

        await self.server._on_client_disconnect(client)
        await asyncio.sleep(0)

        assert "disconnect.ogg" in self._sound_names(host)
        assert "table_leave.ogg" not in self._sound_names(host)
        assert any(member.username == guest.username for member in table.members)

        returning_guest = MockUser(guest.username, uuid=guest.uuid)
        self.server._users[guest.username] = returning_guest
        host.clear_messages()
        self.server._restore_user_state(returning_guest, guest.username)
        await asyncio.sleep(0)

        assert game.get_user(game.get_player_by_id(guest.uuid)) is returning_guest
        assert "reconnect.ogg" in self._sound_names(host)
        assert "table_join.ogg" not in self._sound_names(host)

    @pytest.mark.asyncio
    async def test_network_disconnected_replacement_stays_under_human_roster_row(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        client = SimpleNamespace(
            username=guest.username,
            address="guest-client",
            authenticated=True,
            retired=False,
        )
        guest.connection = client

        await self.server._on_client_disconnect(client)
        pending = self.server._pending_disconnects.pop(guest.username, None)
        if pending:
            pending.cancel()
            with suppress(asyncio.CancelledError):
                await pending

        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None
        assert replacement.is_bot is True
        assert replacement.replaced_human_name == guest.username
        assert any(member.username == guest.username for member in table.members)

        self.server._show_table_members_menu(host, table)
        roster_items = host.get_current_menu_items(TABLE_MEMBERS_MENU) or []
        row_texts = [item.text for item in roster_items]
        guest_row = next(
            text for text in row_texts if text.startswith(f"{guest.username}:")
        )
        assert "Offline" in guest_row
        assert f"bot playing on their behalf: {replacement.name}" in guest_row
        assert not any(text.startswith(f"{replacement.name}:") for text in row_texts)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_ban", [False, True])
    async def test_host_kick_plays_default_table_kick_sound(self, is_ban):
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
        await asyncio.sleep(0)

        assert "table_kick.ogg" in self._sound_names(host)
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
        roster_ids = [item.id for item in roster_items if hasattr(item, "id")]
        assert roster_items[0].id == "table_members_summary"
        assert roster_items[0].text == "Table summary: 2 human players."
        assert "0" not in roster_items[0].text
        assert roster_ids[-1] == "back"
        assert "" not in roster_ids
        assert len(roster_ids) == len(set(roster_ids))
        own_row = next(item for item in roster_items if item.text.startswith("Host:"))
        assert own_row.id == f"table_member_self_{host.username}"
        assert "Host" in own_row.text
        assert "Player" in own_row.text
        assert f"table_member_user_{guest.username}" in [
            item.id for item in roster_items if hasattr(item, "id")
        ]

        await self.server._handle_table_members_selection(
            host,
            roster_items[0].id,
            self.server._user_states[host.username],
        )
        assert self.server._user_states[host.username]["menu"] == TABLE_MEMBERS_MENU

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
        assert own_row.id == f"table_member_self_{host.username}"
        assert "Host" in own_row.text
        assert "Spectator" in own_row.text

        await self.server._handle_table_members_selection(
            host,
            own_row.id,
            self.server._user_states[host.username],
        )

        assert self.server._user_states[host.username]["menu"] == TABLE_MEMBERS_MENU

    def test_table_roster_empty_rows_still_has_back_and_stable_ids(self, monkeypatch):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _ = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        monkeypatch.setattr(self.server, "_table_member_rows", lambda _table: [])

        self.server._show_table_members_menu(host, table)

        roster_items = host.get_current_menu_items(TABLE_MEMBERS_MENU) or []
        roster_ids = [item.id for item in roster_items if hasattr(item, "id")]
        assert roster_ids == ["table_members_summary", "table_members_empty", "back"]
        assert "No table members" in roster_items[1].text

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
    async def test_table_roster_back_stack_after_offline_kick_and_blocked_bot_remove(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        host_player = game.get_player_by_id(host.uuid)
        guest_player = game.get_player_by_id(guest.uuid)
        assert host_player is not None
        assert guest_player is not None

        assert game._replace_with_bot(guest_player) is True
        replacement_bot_name = guest_player.name
        self.server._users.pop(guest.username, None)
        self.server._set_in_game_state(host, table.table_id)

        game._action_whos_at_table(host_player, "whos_at_table")
        assert self.server._user_states[host.username]["menu"] == TABLE_MEMBERS_MENU

        await self.server._handle_table_members_selection(
            host,
            f"table_member_user_{guest.username}",
            self.server._user_states[host.username],
        )
        assert (
            self.server._user_states[host.username]["menu"]
            == TABLE_MEMBER_ACTIONS_MENU
        )

        await self.server._handle_table_member_actions_selection(
            host,
            "table_kick",
            self.server._user_states[host.username],
        )
        state = self.server._user_states[host.username]
        assert state["menu"] == TABLE_MEMBERS_MENU
        assert [frame.get("menu") for frame in state["_stack"]] == ["in_game"]

        roster_items = host.get_current_menu_items(TABLE_MEMBERS_MENU) or []
        assert any(
            item.text.startswith(f"{replacement_bot_name}:")
            for item in roster_items
        )

        await self.server._handle_table_members_selection(
            host,
            f"table_member_bot_{guest.uuid}",
            self.server._user_states[host.username],
        )
        assert (
            self.server._user_states[host.username]["menu"]
            == TABLE_MEMBER_ACTIONS_MENU
        )

        await self.server._handle_table_member_actions_selection(
            host,
            "table_remove_bot",
            self.server._user_states[host.username],
        )
        state = self.server._user_states[host.username]
        assert state["menu"] == TABLE_MEMBER_ACTIONS_MENU
        assert [frame.get("menu") for frame in state["_stack"]] == [
            "in_game",
            TABLE_MEMBERS_MENU,
        ]

        await self.server._handle_table_member_actions_selection(
            host,
            "back",
            self.server._user_states[host.username],
        )
        state = self.server._user_states[host.username]
        assert state["menu"] == TABLE_MEMBERS_MENU
        assert [frame.get("menu") for frame in state["_stack"]] == ["in_game"]

        await self.server._handle_table_members_selection(
            host,
            "back",
            self.server._user_states[host.username],
        )
        assert self.server._user_states[host.username]["menu"] == "in_game"

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
        await asyncio.sleep(0)

        sounds = self._sound_names(host)
        assert "game_crazyeights/personleave.ogg" in sounds
        assert "disconnect.ogg" not in sounds
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

    def test_private_playing_table_preserves_reclaimable_seat_within_grace(
        self, monkeypatch
    ):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        table.is_private = True

        game.on_player_disconnect(host.uuid)
        self.server._users.pop(host.username, None)
        game.on_player_disconnect(guest.uuid)
        self.server._users.pop(guest.username, None)

        monkeypatch.setattr("server.tables.table.time.time", lambda: 100.0)
        table.on_tick()
        monkeypatch.setattr(
            "server.tables.table.time.time",
            lambda: 100.0 + ABANDONED_ACTIVE_TABLE_TIMEOUT_SECONDS - 0.1,
        )
        table.on_tick()

        assert self.server._tables.get_table(table.table_id) is table
        assert self.server._tables.find_user_table(host.username) is table
        assert any(
            member.username == host.username and not member.is_spectator
            for member in table.members
        )

        # The bounded UI snapshot has expired, just as it would after the
        # normal five-minute disconnected-session cleanup.
        self.server._user_states.pop(host.username, None)
        returning_host = MockUser(host.username, uuid=host.uuid)
        self.server._users[host.username] = returning_host
        self.server._restore_user_state(returning_host, host.username)

        restored_player = game.get_player_by_id(host.uuid)
        assert restored_player is not None
        assert restored_player.is_bot is False
        assert restored_player.name == host.username
        assert game.get_user(restored_player) is returning_host
        assert table.get_user(host.username) is returning_host
        assert self.server._user_states[host.username]["menu"] == "in_game"

    def test_single_human_disconnect_pauses_until_reconnect(self, monkeypatch):
        host, table, game = self._create_single_human_started_table()
        game.on_player_disconnect(host.uuid)
        self.server._users.pop(host.username, None)
        game_ticks: list[float] = []
        monkeypatch.setattr(game, "on_tick", lambda: game_ticks.append(1.0))

        started_at = 100.0
        monkeypatch.setattr(
            "server.tables.table.time.time",
            lambda: started_at,
        )
        table.on_tick()
        assert table._offline_since == started_at

        monkeypatch.setattr(
            "server.tables.table.time.time",
            lambda: started_at + ABANDONED_ACTIVE_TABLE_TIMEOUT_SECONDS - 0.1,
        )
        table.on_tick()

        assert self.server._tables.get_table(table.table_id) is table
        assert game_ticks == []

        returning_host = MockUser(host.username, uuid=host.uuid)
        self.server._users[host.username] = returning_host
        self.server._restore_user_state(returning_host, host.username)
        table.on_tick()

        assert table._offline_since is None
        assert game_ticks == [1.0]
        assert table.get_user(host.username) is returning_host

    def test_single_human_disconnect_destroys_at_timeout_with_spectator(
        self,
        monkeypatch,
    ):
        host, table, game = self._create_single_human_started_table()
        spectator = self._create_online_user("Spectator")
        table.add_member(spectator.username, spectator, as_spectator=True)
        game.add_spectator(spectator.username, spectator)
        game.on_player_disconnect(host.uuid)
        self.server._users.pop(host.username, None)

        started_at = 200.0
        monkeypatch.setattr(
            "server.tables.table.time.time",
            lambda: started_at,
        )
        table.on_tick()
        monkeypatch.setattr(
            "server.tables.table.time.time",
            lambda: started_at + ABANDONED_ACTIVE_TABLE_TIMEOUT_SECONDS,
        )
        table.on_tick()

        assert table._destroyed
        assert self.server._tables.get_table(table.table_id) is None
        assert Localization.get(
            spectator.locale,
            "table-closed-disconnect-timeout",
            minutes=ABANDONED_ACTIVE_TABLE_TIMEOUT_SECONDS // 60,
        ) in spectator.get_spoken_messages()

    def test_spectators_do_not_keep_bot_only_playing_table_alive(self, monkeypatch):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        spectator = self._create_online_user("Spectator")
        table, game = self._create_started_table(host, guest)
        table.add_member(spectator.username, spectator, as_spectator=True)
        spectator_player = game.add_spectator(spectator.username, spectator)

        table.members = [
            member
            for member in table.members
            if member.username == spectator.username
        ]
        game.players = [spectator_player]
        self.server._tables._username_to_table.pop(host.username, None)
        self.server._tables._username_to_table.pop(guest.username, None)
        monkeypatch.setattr(game, "on_tick", lambda: None)

        table.on_tick()

        assert self.server._tables.get_table(table.table_id) is None

    @pytest.mark.asyncio
    async def test_account_deletion_releases_indefinite_table_reservation(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)

        deleted = await self.server._delete_account_and_evict(
            guest.username,
            {
                "type": "disconnect",
                "reason": "Account deleted",
                "reconnect": False,
            },
        )

        assert deleted is True
        assert self.db.get_user(guest.username) is None
        assert self.server._tables.get_table(table.table_id) is table
        assert self.server._tables.find_user_table(guest.username) is None
        assert not any(
            member.username == guest.username for member in table.members
        )
        assert not any(
            player.id == guest.uuid
            or player.name == guest.username
            or player.replaced_human_name == guest.username
            for player in game.players
        )

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
        assert "disconnect.ogg" in self._sound_names(host)

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

    def test_playing_disconnected_spectator_is_removed_from_table_roster(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        spectator = self._create_online_user("Spectator")
        table, game = self._create_started_table(host, guest)
        table.add_member(
            spectator.username,
            spectator,
            as_spectator=True,
        )
        spectator_player = game.add_spectator(
            spectator.username,
            spectator,
        )
        self.server._users.pop(spectator.username, None)

        game.on_player_disconnect(spectator_player.id)

        assert game.get_player_by_id(spectator_player.id) is None
        assert not any(
            member.username == spectator.username
            for member in table.members
        )
        assert table.get_user(spectator.username) is None
        assert self.server._tables.find_user_table(spectator.username) is None
        assert not any(
            row["name"] == spectator.username
            for row in self.server._table_member_rows(table)
        )

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
        self.db.send_friend_request(host.uuid, guest.uuid)
        self.db.accept_friend_request(host.uuid, guest.uuid)

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
        await asyncio.sleep(0)

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
        assert "reconnect.ogg" in self._sound_names(host)
        assert "reconnect.ogg" in self._sound_names(guest)

    @pytest.mark.asyncio
    async def test_friend_join_switches_active_tables_via_leave_logic(self):
        host_a = self._create_online_user("HostA")
        mover = self._create_online_user("Mover")
        host_b = self._create_online_user("HostB")
        guest_b = self._create_online_user("GuestB")

        table_a, game_a = self._create_started_table(host_a, mover)
        table_b, game_b = self._create_started_table(host_b, guest_b)
        self.db.send_friend_request(host_b.uuid, mover.uuid)
        self.db.accept_friend_request(host_b.uuid, mover.uuid)

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

        game_items, _ = self.server._get_tables_menu_items(outsider, "pig")
        active_items, _ = self.server._get_active_tables_menu_items(outsider)
        outsider_table_ids = {item.id for item in game_items + active_items if hasattr(item, "id")}

        assert f"table_{private_table.table_id}" not in outsider_table_ids
        assert f"table_{public_table.table_id}" in outsider_table_ids

        self.server._show_friend_actions_menu(outsider, host.username)
        assert "join_table" not in self._get_menu_action_ids(outsider, "friend_actions_menu")

        member_game_items, _ = self.server._get_tables_menu_items(member, "pig")
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
