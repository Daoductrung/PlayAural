import asyncio
import json
import os
import tempfile
from contextlib import suppress
from types import SimpleNamespace

import pytest

from server.auth.auth import AuthManager
from server.auth.table_interaction_rate_limit import TableInteractionRateLimiter
from server.core import server as server_module
from server.core.server import (
    HOST_VOICE_MANAGEMENT_MENU,
    HOST_VOICE_TARGET_MENU,
    PERSONAL_VOICE_SETTINGS_MENU,
    PERSONAL_VOICE_VOLUME_MENU,
    Server,
    TABLE_MEMBERS_MENU,
    TABLE_MEMBER_ACTIONS_MENU,
    USER_REPORT_REASON_MENU,
)
from server.games.crazyeights.game import CrazyEightsGame
from server.games.pig.game import PigGame, PigOptions
from server.games.uno.game import UnoGame
from server.games.yahtzee.game import YahtzeeGame
from server.messages.localization import Localization
from server.persistence.database import Database
from server.tables.table import (
    ABANDONED_ACTIVE_TABLE_TIMEOUT_SECONDS,
    TABLE_STATE_SCHEMA_VERSION,
)
from server.users.bot import Bot
from server.users.test_user import MockUser
from server.voice import VoiceAuthorizationError


class RecordingConnection:
    def __init__(self):
        self.sent: list[dict] = []

    async def send(self, packet: dict) -> None:
        self.sent.append(packet)


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

    def _make_friends(self, first: MockUser, second: MockUser) -> None:
        assert self.db.send_friend_request(first.uuid, second.uuid) == "sent"
        assert self.db.accept_friend_request(first.uuid, second.uuid)

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

    def _install_table_interaction_clock(self):
        clock = SimpleNamespace(now=100.0)
        self.server._table_interaction_rate_limiter = TableInteractionRateLimiter(
            clock=lambda: clock.now,
        )
        return clock

    def _invite_decision_id(self, user: MockUser, decision: str) -> str:
        state = self.server._user_states[user.username]
        return self.server._table_invite_action_id(
            decision,
            state["invite_id"],
        )

    def _add_named_bot(self, game: PigGame, name: str):
        display_name = game._allocate_bot_display_name(name)
        bot_user = Bot(display_name)
        bot_player = game.create_player(bot_user.uuid, display_name, is_bot=True)
        bot_player.bot_name_base = name
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
        seated = self._create_online_user("Seated")
        table, _ = self._create_started_table(host, seated)
        self._make_friends(host, guest)

        guest.preferences.notify_table_created = False

        await self.server._send_table_invite(host, table, guest)

        assert "table_invite.ogg" in self._sound_names(guest)
        assert guest.get_last_spoken() == Localization.get(
            guest.locale,
            "table-invite-received",
            host=host.username,
            game=Localization.get(guest.locale, "game-name-pig"),
        )
        action_ids = self._get_menu_action_ids(guest, "table_invite_prompt")
        assert self._invite_decision_id(guest, "accept") in action_ids
        assert self._invite_decision_id(guest, "decline") in action_ids
        assert "accept" not in action_ids
        assert "decline" not in action_ids

    @pytest.mark.asyncio
    async def test_direct_invite_rejects_non_friend_without_notifying_target(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        seated = self._create_online_user("Seated")
        table, _ = self._create_started_table(host, seated)

        assert not await self.server._send_table_invite(host, table, guest)

        assert guest.username not in self.server._pending_invites
        assert guest.messages == []
        assert host.get_last_spoken() == Localization.get(
            host.locale,
            "host-invite-friend-unavailable",
        )

    @pytest.mark.asyncio
    async def test_direct_invite_allows_human_to_share_bot_base_name(
        self,
    ):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        seated = self._create_online_user("Seated")
        table, game = self._create_started_table(host, seated)
        self._make_friends(host, guest)
        self._add_named_bot(game, guest.username)

        assert await self.server._send_table_invite(host, table, guest)

        assert guest.username in self.server._pending_invites
        assert any(
            player.is_bot
            and player.bot_name_base == guest.username
            and player.name == guest.username
            for player in game.players
        )

    @pytest.mark.asyncio
    async def test_declined_invite_enforces_pair_cooldown_without_renotifying(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        seated = self._create_online_user("Seated")
        table, _ = self._create_started_table(host, seated)
        self._make_friends(host, guest)
        clock = self._install_table_interaction_clock()

        assert await self.server._send_table_invite(host, table, guest)
        state = dict(self.server._user_states[guest.username])
        await self.server._handle_table_invite_selection(
            guest,
            self._invite_decision_id(guest, "decline"),
            state,
        )
        guest.clear_messages()

        assert not await self.server._send_table_invite(host, table, guest)
        assert guest.messages == []
        assert host.get_last_spoken() == Localization.get(
            host.locale,
            "host-invite-pair-cooldown",
            seconds=60,
        )

        clock.now += 60.0
        assert await self.server._send_table_invite(host, table, guest)

    @pytest.mark.asyncio
    async def test_stale_expiry_generation_cannot_cancel_reissued_invite(
        self,
        monkeypatch,
    ):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        seated = self._create_online_user("Seated")
        table, _ = self._create_started_table(host, seated)
        self._make_friends(host, guest)
        clock = self._install_table_interaction_clock()

        assert await self.server._send_table_invite(host, table, guest)
        old_invite_id = self.server._pending_invites[guest.username]["invite_id"]
        self.server._cancel_invite(guest.username, invite_id=old_invite_id)
        clock.now += 60.0
        assert await self.server._send_table_invite(host, table, guest)
        current_invite = self.server._pending_invites[guest.username]
        current_invite_id = current_invite["invite_id"]
        current_invite["task"].cancel()
        current_invite["task"] = None
        monkeypatch.setattr(
            server_module,
            "INTERACTIVE_TABLE_REQUEST_TIMEOUT_SECONDS",
            0.0,
        )

        await self.server._expire_invite(guest.username, old_invite_id)

        assert self.server._pending_invites[guest.username]["invite_id"] == current_invite_id

    @pytest.mark.asyncio
    async def test_automatic_host_transfer_cancels_invite_without_social_block(self):
        original_host = self._create_online_user("OriginalHost")
        new_host = self._create_online_user("NewHost")
        invitee = self._create_online_user("Invitee")
        table, _ = self._create_waiting_table(
            original_host,
            new_host,
            PigGame(options=PigOptions(target_score=25)),
        )
        self._make_friends(original_host, invitee)

        assert await self.server._send_table_invite(
            original_host,
            table,
            invitee,
        )
        game = table.game
        original_player = game.get_player_by_id(original_host.uuid)
        assert original_player is not None
        game.remove_player(original_player.id)
        assert table.remove_member(original_host.username)

        assert table.host == new_host.username
        assert invitee.username not in self.server._pending_invites
        assert self.server._user_states[invitee.username]["menu"] == "main_menu"
        assert "table_invite_prompt" not in invitee.menus
        assert invitee.get_last_spoken() == Localization.get(
            invitee.locale,
            "table-invite-no-longer-available",
        )

    @pytest.mark.asyncio
    async def test_table_destruction_cancels_invite_and_restores_prompt(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        seated = self._create_online_user("Seated")
        table, _ = self._create_started_table(host, seated)
        self._make_friends(host, guest)

        assert await self.server._send_table_invite(host, table, guest)
        table.destroy()

        assert guest.username not in self.server._pending_invites
        assert self.server._user_states[guest.username]["menu"] == "main_menu"
        assert "table_invite_prompt" not in guest.menus
        assert guest.get_last_spoken() == Localization.get(
            guest.locale,
            "table-invite-no-longer-available",
        )

    @pytest.mark.asyncio
    async def test_host_disconnect_cancels_invite_and_restores_prompt(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        seated = self._create_online_user("Seated")
        table, _ = self._create_started_table(host, seated)
        self._make_friends(host, guest)

        assert await self.server._send_table_invite(host, table, guest)
        self.server._users.pop(host.username)
        self.server.on_user_presence_changed()

        assert guest.username not in self.server._pending_invites
        assert self.server._user_states[guest.username]["menu"] == "main_menu"
        assert "table_invite_prompt" not in guest.menus
        assert guest.get_last_spoken() == Localization.get(
            guest.locale,
            "table-invite-no-longer-available",
        )

    @pytest.mark.asyncio
    async def test_friendship_removal_cancels_invite_and_restores_prompt(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        seated = self._create_online_user("Seated")
        table, _ = self._create_started_table(host, seated)
        self._make_friends(host, guest)

        assert await self.server._send_table_invite(host, table, guest)
        assert self.server._perform_remove_friend(host, guest.username)

        assert guest.username not in self.server._pending_invites
        assert self.server._user_states[guest.username]["menu"] == "main_menu"
        assert "table_invite_prompt" not in guest.menus
        assert guest.get_last_spoken() == Localization.get(
            guest.locale,
            "table-invite-no-longer-available",
        )

    def test_role_change_throttle_blocks_broadcast_sound_and_state_spam(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_waiting_table(
            host,
            guest,
            PigGame(options=PigOptions(target_score=25)),
        )
        clock = self._install_table_interaction_clock()
        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None
        host.clear_messages()
        guest.clear_messages()

        game._action_toggle_spectator(guest_player, "toggle_spectator")
        game._action_toggle_spectator(guest_player, "toggle_spectator")
        host_spoken = list(host.get_spoken_messages())
        host_sounds = list(self._sound_names(host))

        game._action_toggle_spectator(guest_player, "toggle_spectator")

        guest_member = next(
            member for member in table.members if member.username == guest.username
        )
        assert guest_player.is_spectator is False
        assert guest_member.is_spectator is False
        assert host.get_spoken_messages() == host_spoken
        assert self._sound_names(host) == host_sounds
        assert guest.get_last_spoken() == Localization.get(
            guest.locale,
            "action-role-change-rate-limited",
            seconds=15,
        )

        clock.now += 15.0
        game._action_toggle_spectator(guest_player, "toggle_spectator")
        assert guest_player.is_spectator is True
        assert guest_member.is_spectator is True

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
        self._make_friends(host, guest)

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
    async def test_simultaneous_invites_use_one_slot_and_only_winner_can_be_accepted(self):
        first_host = self._create_online_user("FirstHost")
        second_host = self._create_online_user("SecondHost")
        guest = self._create_online_user("Guest")
        first_seated = self._create_online_user("FirstSeated")
        second_seated = self._create_online_user("SecondSeated")
        first_table, _ = self._create_started_table(first_host, first_seated)
        second_table, _ = self._create_started_table(second_host, second_seated)
        self._make_friends(first_host, guest)
        self._make_friends(second_host, guest)

        outcomes = await asyncio.gather(
            self.server._send_table_invite(first_host, first_table, guest),
            self.server._send_table_invite(second_host, second_table, guest),
        )

        assert outcomes.count(True) == 1
        assert outcomes.count(False) == 1
        candidates = [
            (first_host, first_table),
            (second_host, second_table),
        ]
        winner_host, winner_table = candidates[outcomes.index(True)]
        loser_host, _loser_table = candidates[outcomes.index(False)]
        pending = self.server._pending_invites[guest.username]
        assert pending["table_id"] == winner_table.table_id
        assert pending["host_username"] == winner_host.username
        assert loser_host.get_last_spoken() == Localization.get(
            loser_host.locale,
            "host-invite-already-pending",
        )

        state = dict(self.server._user_states[guest.username])
        await self.server._handle_table_invite_selection(
            guest,
            self._invite_decision_id(guest, "accept"),
            state,
        )

        assert guest.username not in self.server._pending_invites
        assert self.server._tables.find_user_table(guest.username) is winner_table
        assert self.server._user_states[guest.username]["table_id"] == winner_table.table_id

    @pytest.mark.asyncio
    async def test_joining_another_table_dismisses_pending_invite(self):
        inviting_host = self._create_online_user("InvitingHost")
        other_host = self._create_online_user("OtherHost")
        guest = self._create_online_user("Guest")
        inviting_seated = self._create_online_user("InvitingSeated")
        other_seated = self._create_online_user("OtherSeated")
        inviting_table, _ = self._create_started_table(
            inviting_host,
            inviting_seated,
        )
        other_table, _ = self._create_started_table(other_host, other_seated)
        self._make_friends(inviting_host, guest)

        assert await self.server._send_table_invite(
            inviting_host,
            inviting_table,
            guest,
        )
        self.server._auto_join_table(guest, other_table, other_table.game_type)

        assert guest.username not in self.server._pending_invites
        assert "table_invite_prompt" not in guest.menus
        assert self.server._tables.find_user_table(guest.username) is other_table
        assert self.server._user_states[guest.username] == {
            "menu": "in_game",
            "table_id": other_table.table_id,
        }

    @pytest.mark.asyncio
    async def test_stale_decision_cannot_accept_replacement_invite(self):
        first_host = self._create_online_user("FirstHost")
        second_host = self._create_online_user("SecondHost")
        guest = self._create_online_user("Guest")
        first_seated = self._create_online_user("FirstSeated")
        second_seated = self._create_online_user("SecondSeated")
        first_table, _ = self._create_started_table(first_host, first_seated)
        second_table, _ = self._create_started_table(second_host, second_seated)
        self._make_friends(first_host, guest)
        self._make_friends(second_host, guest)

        assert await self.server._send_table_invite(first_host, first_table, guest)
        stale_state = dict(self.server._user_states[guest.username])
        stale_accept_id = self._invite_decision_id(guest, "accept")
        self.server._users.pop(first_host.username)

        assert await self.server._send_table_invite(second_host, second_table, guest)
        current_accept_id = self._invite_decision_id(guest, "accept")
        assert current_accept_id != stale_accept_id
        pending = self.server._pending_invites[guest.username]
        assert pending["host_username"] == second_host.username

        await self.server._handle_table_invite_selection(
            guest,
            stale_accept_id,
            stale_state,
        )
        assert self.server._pending_invites[guest.username] is pending
        assert self.server._user_states[guest.username]["invite_id"] == pending["invite_id"]

        client = SimpleNamespace(username=guest.username)
        await self.server._handle_menu(
            client,
            {
                "type": "menu",
                "menu_id": "table_invite_prompt",
                "selection_id": stale_accept_id,
            },
        )

        assert self.server._pending_invites[guest.username] is pending
        assert self.server._tables.find_user_table(guest.username) is None
        assert self.server._user_states[guest.username]["menu"] == "table_invite_prompt"

        await self.server._handle_menu(
            client,
            {
                "type": "menu",
                "menu_id": "table_invite_prompt",
                "selection_id": current_accept_id,
            },
        )

        assert guest.username not in self.server._pending_invites
        assert self.server._tables.find_user_table(guest.username) is second_table

    @pytest.mark.asyncio
    async def test_table_invite_waits_until_private_message_input_finishes(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        friend = self._create_online_user("Friend")
        table, _ = self._create_started_table(host, friend)
        self._make_friends(host, guest)

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
        self._make_friends(host, guest)

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
        self._make_friends(host, guest)

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
        await self.server._handle_table_invite_selection(
            guest,
            self._invite_decision_id(guest, "accept"),
            state,
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
        assert "table_join.ogg" in self._sound_names(host)
        assert "table_join.ogg" in self._sound_names(guest)
        assert "reconnect.ogg" not in self._sound_names(host)

    @pytest.mark.asyncio
    async def test_accepting_invite_reattaches_existing_table_member(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        self._make_friends(host, guest)

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
        await self.server._handle_table_invite_selection(
            guest,
            self._invite_decision_id(guest, "accept"),
            state,
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
        assert "table_join.ogg" in self._sound_names(host)
        assert "table_join.ogg" in self._sound_names(guest)
        assert "reconnect.ogg" not in self._sound_names(host)

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
        self._make_friends(original_host, invitee)

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
        assert table.is_private is False
        assert self.db.get_saved_table(record.id) is None

    @pytest.mark.asyncio
    async def test_saved_table_restore_preserves_privacy_and_table_bans(self):
        host = self._create_online_user("Host")
        banned = self._create_online_user("Banned")
        outsider = self._create_online_user("Outsider")
        table, _ = self._create_waiting_table(
            host,
            banned,
            PigGame(options=PigOptions(target_score=25)),
        )
        table.is_private = True
        assert self.server._perform_host_kick(
            host,
            table,
            banned.username,
            is_ban=True,
        )

        self.server.on_table_save(table, host.username)

        records = self.db.get_user_saved_tables(host.username)
        assert len(records) == 1
        record = records[0]
        saved_state = json.loads(record.table_state_json)
        assert saved_state["properties"] == {
            "banned_uuids": [banned.uuid],
            "is_private": True,
        }

        await self.server._restore_saved_table(host, record.id)

        restored_table = self.server._tables.find_user_table(host.username)
        assert restored_table is not None
        assert restored_table.is_private is True
        assert restored_table.is_banned(banned.uuid)
        assert self.db.get_saved_table(record.id) is None

        self.server._auto_join_table(
            outsider,
            restored_table,
            restored_table.game_type,
        )
        assert self.server._tables.find_user_table(outsider.username) is None
        assert outsider.get_last_spoken() == Localization.get(
            outsider.locale,
            "table-private-invite-only",
        )

        self.server._auto_join_table(
            banned,
            restored_table,
            restored_table.game_type,
            allow_private_join=True,
        )
        assert self.server._tables.find_user_table(banned.username) is None
        assert banned.get_last_spoken() == Localization.get(
            banned.locale,
            "table-you-are-banned",
        )

    def test_invalid_runtime_table_property_aborts_save_before_destroy(self):
        host = self._create_online_user("Host")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        table.is_private = 1

        with pytest.raises(ValueError, match="is_private must be a boolean"):
            self.server.on_table_save(table, host.username)

        assert self.server._tables.get_table(table.table_id) is table
        assert self.db.count_user_saved_tables(host.username) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "table_state",
        [
            {
                "version": TABLE_STATE_SCHEMA_VERSION,
                "properties": {"is_private": "not-a-boolean"},
            },
            {
                "version": TABLE_STATE_SCHEMA_VERSION,
                "properties": {"future_admission_rule": True},
            },
            {
                "version": TABLE_STATE_SCHEMA_VERSION + 1,
                "properties": {},
            },
        ],
        ids=["invalid-type", "unknown-property", "unknown-version"],
    )
    async def test_invalid_saved_table_properties_fail_without_partial_restore(
        self,
        table_state,
    ):
        restorer = self._create_online_user("Restorer")
        record = self._save_pig_game(restorer)
        self.db._conn.execute(
            "UPDATE saved_tables SET table_state_json = ? WHERE id = ?",
            (json.dumps(table_state), record.id),
        )

        await self.server._restore_saved_table(restorer, record.id)

        assert self.server._tables.find_user_table(restorer.username) is None
        assert self.db.get_saved_table(record.id) is not None
        assert restorer.get_last_spoken() == Localization.get(
            restorer.locale,
            "saved-table-invalid",
        )

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
        assert "table_join.ogg" not in self._sound_names(host)

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
        assert "table_join.ogg" in self._sound_names(host)
        assert "table_join.ogg" in self._sound_names(guest)
        assert "reconnect.ogg" not in self._sound_names(host)

    def test_reclaim_is_unambiguous_when_dedicated_bot_shares_human_base(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        dedicated_bot = self._add_named_bot(game, guest.username)
        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None

        game._perform_leave_game(guest_player)
        table.remove_member(guest.username)

        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None
        assert replacement.is_bot is True
        assert replacement.name != dedicated_bot.name
        assert replacement.replaced_human_name == guest.username

        self.server._auto_join_table(guest, table, table.game_type)

        reclaimed = game.get_player_by_id(guest.uuid)
        assert reclaimed is not None
        assert reclaimed.name == guest.username
        assert reclaimed.is_bot is False
        assert reclaimed.bot_name_base == ""
        assert dedicated_bot.name == "Guest (Bot)"
        assert dedicated_bot.bot_name_base == "Guest"

    def test_auto_join_allows_human_to_share_a_bot_base_name(self):
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

        self.server._auto_join_table(entrant, table, table.game_type)

        assert self.server._tables.find_user_table(entrant.username) is table
        assert game.get_player_by_id(entrant.uuid).name == "Test"
        assert any(
            player.is_bot
            and player.bot_name_base == "Test"
            and player.name == "Test (Bot)"
            for player in game.players
        )
        assert all(
            member.username != entrant.username
            for member in current_table.members
        )

    def test_custom_bot_name_accepts_registered_account_base_name(self):
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

        assert any(
            player.name == "Test"
            and player.bot_name_base == "Test"
            and player.is_bot
            for player in game.players
        )

    def test_generated_bot_name_can_match_registered_account_base(self, monkeypatch):
        host = self._create_online_user("Host")
        self._create_online_user("Alice")
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
        assert bot_names == ["Alice"]

    def test_replacement_bot_name_can_match_registered_account_base(self, monkeypatch):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        self._create_online_user("Alice")
        table, game = self._create_started_table(host, guest)
        guest_player = game.get_player_by_id(guest.uuid)
        assert guest_player is not None
        monkeypatch.setattr(
            "server.game_utils.bot_names.random.choice",
            lambda options: options[0],
        )

        game._replace_with_bot(guest_player)

        assert guest_player.is_bot is True
        assert guest_player.bot_name_base == "Alice"
        assert guest_player.name == "Alice"

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
    async def test_table_voice_controls_apply_by_account_id_with_personal_feedback(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        host.connection = RecordingConnection()
        guest.connection = RecordingConnection()
        table, _game = self._create_started_table(host, guest)

        self.server._open_host_management_from_game(host, table)
        await self.server._handle_host_management_selection(
            host,
            "manage_voice",
            self.server._user_states[host.username],
        )
        assert self.server._user_states[host.username]["menu"] == HOST_VOICE_MANAGEMENT_MENU
        assert f"host_voice_member_{guest.uuid}" in self._get_menu_action_ids(
            host,
            HOST_VOICE_MANAGEMENT_MENU,
        )

        await self.server._handle_host_voice_management_selection(
            host,
            f"host_voice_member_{guest.uuid}",
            self.server._user_states[host.username],
        )
        assert self.server._user_states[host.username]["menu"] == HOST_VOICE_TARGET_MENU
        await self.server._handle_host_voice_target_selection(
            host,
            "toggle_host_voice_mute",
            self.server._user_states[host.username],
        )

        assert table.is_voice_host_muted(guest.uuid)
        assert guest.connection.sent[-1] == {
            "type": "voice_settings",
            "version": 1,
            "context_id": table.table_id,
            "host_muted": True,
            "participants": [],
        }
        assert any(
            "You disabled Guest's microphone" in text
            for text in host.get_spoken_messages()
        )
        assert any(
            "Host disabled your microphone" in text
            for text in guest.get_spoken_messages()
        )

        self.server._show_table_members_menu(host, table)
        await self.server._handle_table_members_selection(
            host,
            f"table_member_user_{guest.username}",
            self.server._user_states[host.username],
        )
        assert "personal_voice_settings" in self._get_menu_action_ids(
            host,
            TABLE_MEMBER_ACTIONS_MENU,
        )
        await self.server._handle_table_member_actions_selection(
            host,
            "personal_voice_settings",
            self.server._user_states[host.username],
        )
        assert self.server._user_states[host.username]["menu"] == PERSONAL_VOICE_SETTINGS_MENU
        await self.server._handle_personal_voice_settings_selection(
            host,
            "toggle_personal_voice_mute",
            self.server._user_states[host.username],
        )
        assert table.get_personal_voice_settings(host.uuid, guest.uuid) == (100, True)
        assert host.connection.sent[-1]["participants"] == [
            {"participant_id": guest.uuid, "volume": 100, "muted": True}
        ]

        await self.server._handle_personal_voice_settings_selection(
            host,
            "set_personal_voice_volume",
            self.server._user_states[host.username],
        )
        assert self.server._user_states[host.username]["menu"] == PERSONAL_VOICE_VOLUME_MENU
        await self.server._handle_personal_voice_volume_selection(
            host,
            "personal_voice_volume_30",
            self.server._user_states[host.username],
        )
        assert table.get_personal_voice_settings(host.uuid, guest.uuid) == (30, True)

    @pytest.mark.asyncio
    async def test_voice_presence_repaints_open_management_menu_in_place(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _game = self._create_started_table(host, guest)
        self.server._show_host_voice_management_menu(host, table)

        def guest_row_text() -> str:
            items = host.get_current_menu_items(HOST_VOICE_MANAGEMENT_MENU) or []
            return next(
                item.text
                for item in items
                if item.id == f"host_voice_member_{guest.uuid}"
            )

        assert "not connected" in guest_row_text()
        self.server._voice_presence_by_user[guest.username] = {
            "scope": "table",
            "context_id": table.table_id,
        }
        await self.server._broadcast_voice_presence_event(
            table,
            guest.username,
            "voice-status-connected",
            play_sound=False,
        )
        assert "connected to voice chat" in guest_row_text()

        await self.server._clear_voice_presence(
            guest.username,
            "",
            table=table,
            broadcast=False,
        )
        assert "not connected" in guest_row_text()

    @pytest.mark.asyncio
    async def test_voice_presence_refresh_preserves_open_volume_menu_focus(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _game = self._create_started_table(host, guest)
        self.server._show_personal_voice_volume_menu(
            host,
            table,
            guest.uuid,
            guest.username,
        )
        assert host.menus[PERSONAL_VOICE_VOLUME_MENU]["position"] is not None
        host.clear_messages()

        self.server._voice_presence_by_user[guest.username] = {
            "scope": "table",
            "context_id": table.table_id,
        }
        await self.server._broadcast_voice_presence_event(
            table,
            guest.username,
            "voice-status-connected",
            play_sound=False,
        )

        repaint = next(
            message
            for message in reversed(host.messages)
            if message.type == "show_menu"
            and message.data["menu_id"] == PERSONAL_VOICE_VOLUME_MENU
        )
        assert repaint.data["position"] is None
        assert repaint.data["selection_id"] is None

    def test_departing_voice_target_closes_personal_overlay_without_stale_stack(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _game = self._create_started_table(host, guest)
        self.server._show_personal_voice_volume_menu(
            host,
            table,
            guest.uuid,
            guest.username,
        )

        assert table.remove_member(guest.username)

        state = self.server._user_states[host.username]
        assert state["menu"] == "in_game"
        assert "_stack" not in state
        assert any(
            "no longer at this table" in text
            for text in host.get_spoken_messages()
        )

    @pytest.mark.asyncio
    async def test_stale_personal_voice_menu_cannot_mutate_after_target_leaves(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        host.connection = RecordingConnection()
        table, _game = self._create_started_table(host, guest)
        self.server._show_personal_voice_settings_menu(
            host,
            table,
            guest.uuid,
            guest.username,
        )
        stale_state = dict(self.server._user_states[host.username])

        assert table.remove_member(guest.username)
        await self.server._handle_personal_voice_settings_selection(
            host,
            "toggle_personal_voice_mute",
            stale_state,
        )

        assert table.get_personal_voice_settings(host.uuid, guest.uuid) == (100, False)
        assert any(
            "no longer at this table" in text
            for text in host.get_spoken_messages()
        )

    @pytest.mark.asyncio
    async def test_live_host_voice_mute_commits_only_after_provider_success(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        host.connection = RecordingConnection()
        guest.connection = RecordingConnection()
        table, _game = self._create_started_table(host, guest)
        self.server._voice_presence_by_user[guest.username] = {
            "scope": "table",
            "context_id": table.table_id,
        }
        calls = []

        async def fail_update(**kwargs):
            calls.append(kwargs)
            raise VoiceAuthorizationError("voice-moderation-provider-failed")

        self.server._voice = SimpleNamespace(
            set_participant_can_publish=fail_update,
        )
        self.server._show_host_voice_target_menu(
            host,
            table,
            guest.uuid,
            guest.username,
        )

        await self.server._handle_host_voice_target_selection(
            host,
            "toggle_host_voice_mute",
            self.server._user_states[host.username],
        )

        assert calls[0]["identity"] == guest.uuid
        assert calls[0]["can_publish"] is False
        assert not table.is_voice_host_muted(guest.uuid)
        assert guest.connection.sent == []
        assert any(
            "could not be applied" in text
            for text in host.get_spoken_messages()
        )

    @pytest.mark.asyncio
    async def test_live_host_voice_mute_updates_provider_before_client_snapshot(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        host.connection = RecordingConnection()
        guest.connection = RecordingConnection()
        table, _game = self._create_started_table(host, guest)
        self.server._voice_presence_by_user[guest.username] = {
            "scope": "table",
            "context_id": table.table_id,
        }
        events = []

        async def apply_provider_permission(**kwargs):
            events.append(("provider", kwargs["identity"], kwargs["can_publish"]))

        async def record_guest_packet(packet):
            events.append(("client", packet["host_muted"]))
            guest.connection.sent.append(packet)

        self.server._voice = SimpleNamespace(
            set_participant_can_publish=apply_provider_permission,
        )
        guest.connection.send = record_guest_packet
        self.server._show_host_voice_target_menu(
            host,
            table,
            guest.uuid,
            guest.username,
        )

        await self.server._handle_host_voice_target_selection(
            host,
            "toggle_host_voice_mute",
            self.server._user_states[host.username],
        )

        assert events == [
            ("provider", guest.uuid, False),
            ("client", True),
        ]
        assert table.is_voice_host_muted(guest.uuid)

    @pytest.mark.asyncio
    async def test_rapid_host_voice_toggles_serialize_against_provider_state(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        host.connection = RecordingConnection()
        guest.connection = RecordingConnection()
        table, _game = self._create_started_table(host, guest)
        self.server._voice_presence_by_user[guest.username] = {
            "scope": "table",
            "context_id": table.table_id,
        }
        first_started = asyncio.Event()
        release_first = asyncio.Event()
        provider_permissions = []

        async def apply_provider_permission(**kwargs):
            provider_permissions.append(kwargs["can_publish"])
            if len(provider_permissions) == 1:
                first_started.set()
                await release_first.wait()

        self.server._voice = SimpleNamespace(
            set_participant_can_publish=apply_provider_permission,
        )
        self.server._show_host_voice_target_menu(
            host,
            table,
            guest.uuid,
            guest.username,
        )
        state = dict(self.server._user_states[host.username])

        first = asyncio.create_task(
            self.server._handle_host_voice_target_selection(
                host,
                "toggle_host_voice_mute",
                state,
            )
        )
        await first_started.wait()
        second = asyncio.create_task(
            self.server._handle_host_voice_target_selection(
                host,
                "toggle_host_voice_mute",
                state,
            )
        )
        release_first.set()
        await asyncio.gather(first, second)

        assert provider_permissions == [False, True]
        assert not table.is_voice_host_muted(guest.uuid)

    @pytest.mark.asyncio
    async def test_host_voice_policy_survives_target_departure_during_provider_update(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        host.connection = RecordingConnection()
        guest.connection = RecordingConnection()
        table, _game = self._create_started_table(host, guest)
        self.server._voice_presence_by_user[guest.username] = {
            "scope": "table",
            "context_id": table.table_id,
        }
        provider_started = asyncio.Event()
        finish_provider = asyncio.Event()

        async def participant_disappears(**_kwargs):
            provider_started.set()
            await finish_provider.wait()
            raise VoiceAuthorizationError("voice-moderation-provider-failed")

        self.server._voice = SimpleNamespace(
            set_participant_can_publish=participant_disappears,
        )
        self.server._show_host_voice_target_menu(
            host,
            table,
            guest.uuid,
            guest.username,
        )
        state = dict(self.server._user_states[host.username])
        moderation = asyncio.create_task(
            self.server._handle_host_voice_target_selection(
                host,
                "toggle_host_voice_mute",
                state,
            )
        )
        await provider_started.wait()
        self.server._voice_presence_by_user.pop(guest.username, None)
        assert table.remove_member(guest.username)
        finish_provider.set()
        await moderation

        assert table.is_voice_host_muted(guest.uuid)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "member_state",
        ["active_player", "replaced_player", "spectator"],
    )
    async def test_table_member_report_opens_shared_flow_and_restores_focus(
        self,
        member_state: str,
    ):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, game = self._create_started_table(host, guest)
        target = guest
        if member_state == "replaced_player":
            guest_player = game.get_player_by_id(guest.uuid)
            assert guest_player is not None
            assert game._replace_with_bot(guest_player) is True
            self.server._users.pop(guest.username, None)
        elif member_state == "spectator":
            target = self._create_online_user("Spectator")
            table.add_member(target.username, target, as_spectator=True)
            game.add_spectator(target.username, target)

        self.server._show_table_members_menu(host, table)
        client = SimpleNamespace(username=host.username)
        await self.server._handle_menu(
            client,
            {
                "menu_id": TABLE_MEMBERS_MENU,
                "selection_id": f"table_member_user_{target.username}",
            },
        )

        action_ids = self._get_menu_action_ids(host, TABLE_MEMBER_ACTIONS_MENU)
        assert "report" in action_ids

        await self.server._handle_menu(
            client,
            {
                "menu_id": TABLE_MEMBER_ACTIONS_MENU,
                "selection_id": "report",
            },
        )

        state = self.server._user_states[host.username]
        assert state["menu"] == USER_REPORT_REASON_MENU
        assert state["target_uuid"] == target.uuid

        await self.server._handle_menu(
            client,
            {
                "menu_id": USER_REPORT_REASON_MENU,
                "selection_id": "back",
            },
        )

        state = self.server._user_states[host.username]
        assert state["menu"] == TABLE_MEMBER_ACTIONS_MENU
        assert host.menus[TABLE_MEMBER_ACTIONS_MENU]["selection_id"] == "report"

    @pytest.mark.asyncio
    async def test_table_member_account_actions_reject_username_reuse(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table, _ = self._create_started_table(host, guest)
        self.server._show_table_members_menu(host, table)
        client = SimpleNamespace(username=host.username)
        await self.server._handle_menu(
            client,
            {
                "menu_id": TABLE_MEMBERS_MENU,
                "selection_id": f"table_member_user_{guest.username}",
            },
        )
        action_ids = self._get_menu_action_ids(host, TABLE_MEMBER_ACTIONS_MENU)
        assert "report" in action_ids

        assert self.db.delete_user(guest.username)
        replacement = self.db.create_user(
            guest.username,
            "Password123",
            approved=True,
            email="replacement@example.com",
        )
        assert replacement.uuid != guest.uuid
        host.clear_messages()

        await self.server._handle_menu(
            client,
            {
                "menu_id": TABLE_MEMBER_ACTIONS_MENU,
                "selection_id": "report",
            },
        )

        state = self.server._user_states[host.username]
        assert state["menu"] == TABLE_MEMBER_ACTIONS_MENU
        assert self._get_menu_action_ids(host, TABLE_MEMBER_ACTIONS_MENU) == [
            "table_member_no_actions",
            "back",
        ]
        assert host.get_last_spoken() == Localization.get(
            host.locale,
            "user-account-unavailable",
        )
        assert self.db.count_moderation_reports() == 0

    @pytest.mark.asyncio
    async def test_fallback_table_member_actions_keep_original_account_identity(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        original = self._create_online_user("FallbackMember")
        table, _ = self._create_started_table(host, guest)
        assert table.add_member(original.username, original, as_spectator=True)

        self.server._show_table_members_menu(host, table)
        await self.server._handle_table_members_selection(
            host,
            f"table_member_user_{original.username}",
            self.server._user_states[host.username],
        )
        assert "report" in self._get_menu_action_ids(
            host,
            TABLE_MEMBER_ACTIONS_MENU,
        )

        assert self.db.delete_user(original.username)
        replacement = self.db.create_user(
            original.username,
            "Password123",
            approved=True,
            email="fallback-replacement@example.com",
        )
        assert replacement.uuid != original.uuid
        replacement_user = MockUser(original.username, uuid=replacement.uuid)
        table.attach_user(original.username, replacement_user)
        self.server._users[original.username] = replacement_user
        host.clear_messages()

        await self.server._handle_table_member_actions_selection(
            host,
            "report",
            self.server._user_states[host.username],
        )

        assert self._get_menu_action_ids(host, TABLE_MEMBER_ACTIONS_MENU) == [
            "table_member_no_actions",
            "back",
        ]
        assert host.get_last_spoken() == Localization.get(
            host.locale,
            "user-account-unavailable",
        )
        assert self.db.count_moderation_reports() == 0

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
        assert "report" not in action_ids

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

    @pytest.mark.parametrize(
        "game_class",
        [PigGame, CrazyEightsGame, UnoGame],
        ids=["pig", "crazy-eights", "uno"],
    )
    def test_spectator_host_keeps_kicked_disconnect_replacement_active(
        self,
        monkeypatch,
        game_class,
    ):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        game = game_class()
        table = self.server._tables.create_table(
            game.get_type(),
            host.username,
            host,
        )
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        table.add_member(guest.username, guest)
        game.add_player(guest.username, guest)
        self._add_named_bot(game, "Bot One")
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None

        game.execute_action(host_player, "toggle_spectator")
        game.flush_menus()
        game.execute_action(host_player, "start_game")
        game.flush_menus()
        assert game.status == "playing"
        assert table.has_online_spectator_host()

        game.on_player_disconnect(guest.uuid)
        self.server._users.pop(guest.username, None)
        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None and replacement.is_bot

        assert self.server._perform_host_kick(host, table, guest.username)
        assert all(member.username != guest.username for member in table.members)
        assert table.player_count == 0
        assert game.get_player_by_id(guest.uuid) is replacement

        game_ticks: list[bool] = []
        monkeypatch.setattr(game, "on_tick", lambda: game_ticks.append(True))
        table.on_tick()

        assert self.server._tables.get_table(table.table_id) is table
        assert not table._destroyed
        assert table.host == host.username
        assert game.host == host.username
        assert game_ticks == [True]

    def test_waiting_spectator_host_can_change_options_but_other_spectators_cannot(
        self,
    ):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        spectator = self._create_online_user("Spectator")
        game = PigGame(options=PigOptions(target_score=25))
        table, game = self._create_waiting_table(host, guest, game)
        table.add_member(spectator.username, spectator, as_spectator=True)
        spectator_player = game.add_spectator(spectator.username, spectator)
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None
        for user in (host, guest, spectator):
            self.server._set_in_game_state(user, table.table_id)

        game.execute_action(host_player, "toggle_spectator")
        game.flush_menus()

        host_actions = {
            resolved.action.id: resolved
            for resolved in game.get_all_visible_actions(host_player)
        }
        spectator_action_ids = {
            resolved.action.id
            for resolved in game.get_all_visible_actions(spectator_player)
        }
        assert host_actions["set_target_score"].enabled
        assert "set_target_score" not in spectator_action_ids
        assert "set_target_score" in self._get_menu_action_ids(host, "turn_menu")
        assert "set_target_score" not in self._get_menu_action_ids(
            spectator,
            "turn_menu",
        )

        game.execute_action(
            host_player,
            "set_target_score",
            input_value="50",
        )
        game.flush_menus()
        assert game.options.target_score == 50

        spectator.clear_messages()
        game.execute_action(
            spectator_player,
            "set_target_score",
            input_value="75",
        )
        assert game.options.target_score == 50
        assert spectator.get_last_spoken() == Localization.get(
            spectator.locale,
            "action-not-host",
        )

    def test_spectator_host_keeps_zero_seat_active_table_safely_frozen(
        self,
        monkeypatch,
    ):
        host = self._create_online_user("Host")
        replacement = self._create_online_user("Replacement")
        game = YahtzeeGame()
        table = self.server._tables.create_table(
            game.get_type(),
            host.username,
            host,
        )
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        table.add_member(
            replacement.username,
            replacement,
            as_spectator=True,
        )
        replacement_spectator = game.add_spectator(
            replacement.username,
            replacement,
        )
        host_seat = game.get_player_by_id(host.uuid)
        assert host_seat is not None

        game.execute_action(host_seat, "start_game")
        game.flush_menus()
        assert game.status == "playing"
        result = game.substitute_player_with_spectator(
            host_seat,
            replacement_spectator,
            replacement,
            outgoing_user=host,
        )
        assert result.outgoing_spectator is not None
        assert table.apply_player_substitution(
            replacement.username,
            outgoing_username=host.username,
            outgoing_becomes_spectator=True,
        )
        assert table.has_online_spectator_host()

        game._perform_leave_game(host_seat, allow_bot_takeover=False)
        table.remove_member(replacement.username)
        assert not any(not player.is_spectator for player in game.players)
        assert table.player_count == 0

        game_ticks: list[bool] = []
        monkeypatch.setattr(game, "on_tick", lambda: game_ticks.append(True))
        table.on_tick()

        assert self.server._tables.get_table(table.table_id) is table
        assert not table._destroyed
        assert game_ticks == []

    def test_spectating_host_cannot_start_bot_only_table(self):
        host = self._create_online_user("Host")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        self._add_named_bot(game, "Bot One")
        self._add_named_bot(game, "Bot Two")
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None

        game.execute_action(host_player, "toggle_spectator")
        host.clear_messages()
        game.execute_action(host_player, "start_game")
        table.on_tick()

        assert host_player.is_spectator is True
        assert game.status == "waiting"
        assert table.status == "waiting"
        assert game._destroyed is False
        assert table._destroyed is False
        assert self.server._tables.get_table(table.table_id) is table
        assert Localization.get(
            host.locale,
            "action-start-needs-human-player",
        ) in host.get_spoken_messages()
        assert Localization.get(
            host.locale,
            "game-starting",
        ) not in host.get_spoken_messages()

    def test_start_revalidates_after_disconnected_human_becomes_bot(self):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        table.add_member(guest.username, guest, as_spectator=False)
        game.add_player(guest.username, guest)
        self._add_named_bot(game, "Bot One")
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None
        game.execute_action(host_player, "toggle_spectator")
        self.server._users.pop(guest.username, None)
        assert game.validate_start() == []

        host.clear_messages()
        game.execute_action(host_player, "start_game")

        replacement = game.get_player_by_id(guest.uuid)
        assert replacement is not None
        assert replacement.is_bot is True
        assert replacement.replaced_human_name == guest.username
        assert game.status == "waiting"
        assert table.status == "waiting"
        assert self.server._tables.get_table(table.table_id) is table
        assert Localization.get(
            host.locale,
            "action-start-needs-human-player",
        ) in host.get_spoken_messages()
        assert Localization.get(
            host.locale,
            "game-starting",
        ) not in host.get_spoken_messages()

    def test_bot_only_team_confirmation_cancels_arrangement_and_can_recover(self):
        host = self._create_online_user("Host")
        guests = [
            self._create_online_user(f"Guest{index}")
            for index in range(1, 4)
        ]
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25, team_mode="2v2"))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        for guest in guests:
            table.add_member(guest.username, guest, as_spectator=False)
            game.add_player(guest.username, guest)
        self._add_named_bot(game, "Bot One")
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None
        game.execute_action(host_player, "toggle_spectator")

        game.execute_action(host_player, "start_game")
        assert game.team_arrangement_active is True
        for guest in guests:
            self.server._users.pop(guest.username, None)

        host.clear_messages()
        game.execute_action(host_player, "start_game")

        assert game.status == "waiting"
        assert game.team_arrangement_active is False
        assert game.team_manager.teams == []
        assert self.server._tables.get_table(table.table_id) is table
        assert Localization.get(
            host.locale,
            "action-start-needs-human-player",
        ) in host.get_spoken_messages()
        assert Localization.get(
            host.locale,
            "team-arrangement-cancelled-roster",
        ) in host.get_spoken_messages()

        game.handle_event(
            host_player,
            {"type": "keybind", "key": "shift+b"},
        )
        game.handle_event(host_player, {"type": "keybind", "key": "f3"})

        assert host_player.is_spectator is False
        assert game.get_active_human_players() == [host_player]
        assert game.validate_start() == []

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

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "game_class",
        [PigGame, CrazyEightsGame, UnoGame],
        ids=["pig", "crazy-eights", "uno"],
    )
    async def test_account_deletion_does_not_leave_bot_reservation_with_spectator_host(
        self,
        game_class,
    ):
        host = self._create_online_user("Host")
        guest = self._create_online_user("Guest")
        game = game_class()
        table = self.server._tables.create_table(
            game.get_type(),
            host.username,
            host,
        )
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        table.add_member(guest.username, guest)
        game.add_player(guest.username, guest)
        self._add_named_bot(game, "Bot One")
        host_player = game.get_player_by_id(host.uuid)
        assert host_player is not None
        game.execute_action(host_player, "toggle_spectator")
        game.flush_menus()
        game.execute_action(host_player, "start_game")
        game.flush_menus()
        assert game.status == "playing"

        deleted = await self.server._delete_account_and_evict(
            guest.username,
            {
                "type": "disconnect",
                "reason": "Account deleted",
                "reconnect": False,
            },
        )

        assert deleted
        assert self.server._tables.get_table(table.table_id) is table
        assert table.has_online_spectator_host()
        assert self.server._tables.find_user_table(guest.username) is None
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
        replacement_base_name = replacement.bot_name_base

        assert table.reset_game()
        assert table.game is not None
        fresh_bot = next(
            player
            for player in table.game.players
            if player.is_bot and player.name == replacement_name
        )
        assert fresh_bot.id != guest.uuid
        assert fresh_bot.replaced_human is False
        assert fresh_bot.bot_name_base == replacement_base_name

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
        assert "table_join.ogg" in self._sound_names(host)
        assert "table_join.ogg" in self._sound_names(guest)
        assert "reconnect.ogg" not in self._sound_names(host)

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
