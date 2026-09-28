from __future__ import annotations

import asyncio
import os
import tempfile

import pytest

from server.auth.auth import AuthManager
from server.core.server import (
    HOST_SUBSTITUTION_SEAT_MENU,
    HOST_SUBSTITUTION_SPECTATOR_MENU,
    PLAYER_SUBSTITUTION_PROMPT_MENU,
    Server,
)
from server.games.crazyeights.game import CrazyEightsGame
from server.games.pig.game import PigGame, PigOptions
from server.games.registry import GameRegistry
from server.gender import Gender
from server.messages.localization import Localization
from server.persistence.database import Database
from server.users.bot import Bot
from server.users.test_user import MockUser


class TestPlayerSubstitution:
    def setup_method(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            self.db_path = temp_file.name
        self.db = Database(self.db_path)
        self.db.connect()
        self.server = Server(db_path=self.db_path)
        self.server._db = self.db
        self.server._auth = AuthManager(self.db)

    def teardown_method(self) -> None:
        for incoming_name in list(self.server._pending_player_substitutions):
            self.server._cancel_player_substitution_request(incoming_name)
        self.db.close()
        os.unlink(self.db_path)

    def _online_user(self, username: str, *, locale: str = "en") -> MockUser:
        self.db.create_user(
            username,
            "Password123",
            approved=True,
            email=f"{username.lower()}@example.com",
        )
        record = self.db.get_user(username)
        assert record is not None
        user = MockUser(username, locale=locale, uuid=record.uuid)
        self.server._users[username] = user
        self.server._user_states[username] = {"menu": "main_menu"}
        return user

    def _playing_table_with_bot_and_spectator(self, *, game=None):
        host = self._online_user("Host")
        spectator = self._online_user("Spectator", locale="vi")
        game = game or PigGame(options=PigOptions(target_score=25))
        table = self.server._tables.create_table(game.get_type(), host.username, host)
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)

        bot_user = Bot("Botty")
        bot = game.add_player(bot_user.username, bot_user)
        game.status = "playing"
        game.game_active = True
        game.set_turn_players([game.get_player_by_id(host.uuid), bot])
        game.turn_index = 1
        game._sync_table_status()

        assert table.add_member(spectator.username, spectator, as_spectator=True)
        spectator_player = game.add_spectator(spectator.username, spectator)
        for user in (host, spectator):
            self.server._set_in_game_state(user, table.table_id)
        return host, spectator, table, game, bot, spectator_player

    def _playing_table_with_human_and_spectator(self):
        host = self._online_user("Host")
        outgoing = self._online_user("Outgoing")
        incoming = self._online_user("Incoming", locale="vi")
        game = PigGame(options=PigOptions(target_score=25))
        table = self.server._tables.create_table(game.get_type(), host.username, host)
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        assert table.add_member(outgoing.username, outgoing)
        outgoing_player = game.add_player(outgoing.username, outgoing)
        assert table.add_member(incoming.username, incoming, as_spectator=True)
        incoming_player = game.add_spectator(incoming.username, incoming)
        game.status = "playing"
        game.game_active = True
        game.set_turn_players(
            [game.get_player_by_id(host.uuid), outgoing_player]
        )
        game.turn_index = 1
        game._sync_table_status()
        for user in (host, outgoing, incoming):
            self.server._set_in_game_state(user, table.table_id)
        return (
            host,
            outgoing,
            incoming,
            table,
            game,
            outgoing_player,
            incoming_player,
        )

    @staticmethod
    def _menu_ids(user: MockUser, menu_id: str) -> list[str | None]:
        items = user.get_current_menu_items(menu_id) or []
        return [item.id for item in items]

    @staticmethod
    def _latest_menu_message(user: MockUser, menu_id: str):
        return next(
            message
            for message in reversed(user.messages)
            if message.type in {"show_menu", "update_menu"}
            and message.data.get("menu_id") == menu_id
        )

    @pytest.mark.asyncio
    async def test_bot_substitution_returns_host_and_restores_invitee_focus(self) -> None:
        host, incoming, table, game, bot, old_spectator = (
            self._playing_table_with_bot_and_spectator()
        )
        old_bot_id = bot.id
        bot.round_score = 17

        self.server._nav_push(
            host,
            self.server._show_host_management_menu,
            table,
            game_return_focus_id="host_management",
        )
        await self.server._handle_host_management_selection(
            host,
            "player_substitution",
            self.server._user_states[host.username],
        )
        assert f"substitution_seat_{old_bot_id}" in self._menu_ids(
            host,
            HOST_SUBSTITUTION_SEAT_MENU,
        )
        await self.server._handle_host_substitution_seat_selection(
            host,
            f"substitution_seat_{old_bot_id}",
            self.server._user_states[host.username],
        )
        assert f"substitution_spectator_{incoming.uuid}" in self._menu_ids(
            host,
            HOST_SUBSTITUTION_SPECTATOR_MENU,
        )
        await self.server._handle_host_substitution_spectator_selection(
            host,
            f"substitution_spectator_{incoming.uuid}",
            self.server._user_states[host.username],
        )

        assert self.server._user_states[host.username] == {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        assert any(
            message.data.get("selection_id") == "host_management"
            for message in host.messages
            if message.type in {"show_menu", "update_menu"}
        )
        assert game.get_player_by_id(old_bot_id) is bot
        assert old_spectator in game.players
        assert self.server._user_states[incoming.username]["menu"] == (
            PLAYER_SUBSTITUTION_PROMPT_MENU
        )
        prompt = self._latest_menu_message(incoming, PLAYER_SUBSTITUTION_PROMPT_MENU)
        focus_context_id = prompt.data["capture_focus_context_id"]
        assert focus_context_id

        await self.server._handle_player_substitution_prompt_selection(
            incoming,
            "accept",
            self.server._user_states[incoming.username],
        )

        transferred = game.get_player_by_id(incoming.uuid)
        assert transferred is bot
        assert transferred.round_score == 17
        assert transferred.name == incoming.username
        assert not transferred.is_bot
        assert not transferred.is_spectator
        assert transferred.reconnect_grace_ticks == 0
        assert game.current_player is transferred
        assert old_spectator not in game.players
        assert game.get_player_by_id(old_bot_id) is None
        assert game.get_user(transferred) is incoming
        assert self.server._user_states[incoming.username] == {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        assert not next(
            member
            for member in table.members
            if member.username == incoming.username
        ).is_spectator
        assert incoming.username not in self.server._pending_player_substitutions
        assert old_bot_id not in game.to_json()
        restored = PigGame.from_json(game.to_json())
        assert restored.get_player_by_id(incoming.uuid) is not None
        restored_menu = next(
            message
            for message in reversed(incoming.messages)
            if message.type == "show_menu"
            and message.data.get("restore_focus_context_id")
        )
        assert restored_menu.data["restore_focus_context_id"] == focus_context_id

    @pytest.mark.asyncio
    async def test_human_substitution_requires_both_consents_and_preserves_state(
        self,
    ) -> None:
        (
            host,
            outgoing,
            incoming,
            table,
            game,
            seat,
            old_spectator,
        ) = self._playing_table_with_human_and_spectator()
        seat.round_score = 19
        old_seat_id = seat.id

        assert self.server._send_player_substitution_request(
            host,
            table,
            seat,
            incoming,
        ) == "pending"
        assert self.server._user_states[outgoing.username]["menu"] == (
            PLAYER_SUBSTITUTION_PROMPT_MENU
        )
        assert self.server._user_states[incoming.username]["menu"] == "in_game"

        await self.server._handle_player_substitution_prompt_selection(
            outgoing,
            "accept",
            self.server._user_states[outgoing.username],
        )
        assert self.server._user_states[outgoing.username]["menu"] == "in_game"
        assert self.server._user_states[incoming.username]["menu"] == (
            PLAYER_SUBSTITUTION_PROMPT_MENU
        )
        assert game.get_player_by_id(old_seat_id) is seat

        await self.server._handle_player_substitution_prompt_selection(
            incoming,
            "accept",
            self.server._user_states[incoming.username],
        )

        assert game.get_player_by_id(incoming.uuid) is seat
        assert seat.round_score == 19
        assert seat.name == incoming.username
        assert old_spectator not in game.players
        outgoing_spectator = game.get_player_by_id(outgoing.uuid)
        assert outgoing_spectator is not None
        assert outgoing_spectator.is_spectator
        assert game.get_user(outgoing_spectator) is outgoing
        assert game.host == host.username
        assert table.host == host.username
        assert next(
            member
            for member in table.members
            if member.username == outgoing.username
        ).is_spectator
        assert not next(
            member
            for member in table.members
            if member.username == incoming.username
        ).is_spectator

    @pytest.mark.parametrize(
        ("outgoing_gender", "incoming_gender"),
        [
            (Gender.MALE, Gender.FEMALE),
            (Gender.FEMALE, Gender.MALE),
            (Gender.NON_BINARY, Gender.UNSPECIFIED),
            (Gender.UNSPECIFIED, Gender.NON_BINARY),
        ],
    )
    @pytest.mark.asyncio
    async def test_cross_gender_substitution_rebinds_every_future_identity_reference(
        self,
        outgoing_gender: Gender,
        incoming_gender: Gender,
    ) -> None:
        (
            host,
            outgoing,
            incoming,
            table,
            game,
            seat,
            _incoming_spectator,
        ) = self._playing_table_with_human_and_spectator()
        outgoing.set_gender(outgoing_gender)
        incoming.set_gender(incoming_gender)
        self.db.update_user_gender(outgoing.username, outgoing_gender.value)
        self.db.update_user_gender(incoming.username, incoming_gender.value)

        assert self.server._send_player_substitution_request(
            host,
            table,
            seat,
            incoming,
        ) == "pending"
        await self.server._handle_player_substitution_prompt_selection(
            outgoing,
            "accept",
            self.server._user_states[outgoing.username],
        )
        await self.server._handle_player_substitution_prompt_selection(
            incoming,
            "accept",
            self.server._user_states[incoming.username],
        )

        outgoing_spectator = game.get_player_by_id(outgoing.uuid)
        assert outgoing_spectator is not None
        assert game.get_player_gender(seat) is incoming_gender
        assert game.get_player_gender(outgoing_spectator) is outgoing_gender
        assert Localization.get(
            incoming.locale,
            "player-substitution-complete-player-you",
            player=outgoing.username,
            player_gender=outgoing_gender.selector,
        ) in incoming.get_spoken_messages()
        assert Localization.get(
            host.locale,
            "player-substitution-complete-player",
            player=incoming.username,
            outgoing=outgoing.username,
            outgoing_gender=outgoing_gender.selector,
        ) in host.get_spoken_messages()

        host.clear_messages()
        outgoing.clear_messages()
        game._broadcast_actor_l(
            seat,
            "pig-you-roll-result",
            "pig-player-roll-result",
            roll=4,
            total=4,
        )
        expected_future_message = Localization.get(
            "en",
            "pig-player-roll-result",
            player=incoming.username,
            player_gender=incoming_gender.selector,
            roll=4,
            total=4,
        )
        assert expected_future_message in host.get_spoken_messages()
        assert expected_future_message in outgoing.get_spoken_messages()

    @pytest.mark.asyncio
    async def test_outgoing_decline_never_prompts_incoming_or_changes_roles(self) -> None:
        (
            host,
            outgoing,
            incoming,
            table,
            game,
            seat,
            incoming_player,
        ) = self._playing_table_with_human_and_spectator()
        assert self.server._send_player_substitution_request(
            host,
            table,
            seat,
            incoming,
        ) == "pending"

        await self.server._handle_player_substitution_prompt_selection(
            outgoing,
            "decline",
            self.server._user_states[outgoing.username],
        )

        assert self.server._pending_player_substitutions == {}
        assert game.get_player_by_id(outgoing.uuid) is seat
        assert game.get_player_by_id(incoming.uuid) is incoming_player
        assert incoming_player.is_spectator
        assert all(
            message.data.get("menu_id") != PLAYER_SUBSTITUTION_PROMPT_MENU
            for message in incoming.messages
            if message.type == "show_menu"
        )

    @pytest.mark.asyncio
    async def test_incoming_decline_after_outgoing_consent_changes_no_roles(
        self,
    ) -> None:
        (
            host,
            outgoing,
            incoming,
            table,
            game,
            seat,
            incoming_player,
        ) = self._playing_table_with_human_and_spectator()
        assert self.server._send_player_substitution_request(
            host,
            table,
            seat,
            incoming,
        ) == "pending"
        await self.server._handle_player_substitution_prompt_selection(
            outgoing,
            "accept",
            self.server._user_states[outgoing.username],
        )
        await self.server._handle_player_substitution_prompt_selection(
            incoming,
            "decline",
            self.server._user_states[incoming.username],
        )

        assert self.server._pending_player_substitutions == {}
        assert game.get_player_by_id(outgoing.uuid) is seat
        assert game.get_player_by_id(incoming.uuid) is incoming_player
        assert not seat.is_spectator
        assert incoming_player.is_spectator

    @pytest.mark.asyncio
    async def test_expiry_restores_prompted_ui_without_changing_roles(
        self,
        monkeypatch,
    ) -> None:
        host, incoming, table, game, bot, incoming_player = (
            self._playing_table_with_bot_and_spectator()
        )
        assert self.server._send_player_substitution_request(
            host,
            table,
            bot,
            incoming,
        ) == "pending"
        request = self.server._pending_player_substitutions[incoming.username]
        expiry_task = request["task"]
        expiry_task.cancel()
        await asyncio.gather(expiry_task, return_exceptions=True)

        async def expire_immediately(_seconds: float) -> None:
            return None

        monkeypatch.setattr("server.core.server.asyncio.sleep", expire_immediately)
        await self.server._expire_player_substitution_request(
            incoming.username,
            request,
        )

        assert self.server._pending_player_substitutions == {}
        assert self.server._user_states[incoming.username]["menu"] == "in_game"
        assert game.get_player_by_id(bot.id) is bot
        assert bot.is_bot
        assert game.get_player_by_id(incoming.uuid) is incoming_player
        assert incoming_player.is_spectator

    @pytest.mark.asyncio
    async def test_host_can_yield_seat_and_remain_spectator_owner(self) -> None:
        host, incoming, table, game, _bot, _ = (
            self._playing_table_with_bot_and_spectator()
        )
        host.set_gender(Gender.MALE)
        incoming.set_gender(Gender.FEMALE)
        self.db.update_user_gender(host.username, Gender.MALE.value)
        self.db.update_user_gender(incoming.username, Gender.FEMALE.value)
        host_seat = game.get_player_by_id(host.uuid)
        assert host_seat is not None
        self.server._voice_presence_by_user[host.username] = {
            "scope": "table",
            "context_id": table.table_id,
        }
        self.server._voice_presence_by_user[incoming.username] = {
            "scope": "table",
            "context_id": table.table_id,
        }
        voice_before = dict(self.server._voice_presence_by_user)

        self.server._show_host_substitution_seat_menu(host, table)
        assert f"substitution_seat_{host.uuid}" in self._menu_ids(
            host,
            HOST_SUBSTITUTION_SEAT_MENU,
        )
        await self.server._handle_host_substitution_seat_selection(
            host,
            f"substitution_seat_{host.uuid}",
            self.server._user_states[host.username],
        )
        await self.server._handle_host_substitution_spectator_selection(
            host,
            f"substitution_spectator_{incoming.uuid}",
            self.server._user_states[host.username],
        )
        assert self.server._user_states[host.username]["menu"] == "in_game"
        assert Localization.get(
            host.locale,
            "player-substitution-self-offer-sent",
            player=incoming.username,
            player_gender=Gender.FEMALE.selector,
        ) in host.get_spoken_messages()
        assert Localization.get(
            incoming.locale,
            "player-substitution-request-host-seat",
            host=host.username,
            host_gender=Gender.MALE.selector,
        ) in incoming.get_spoken_messages()
        await self.server._handle_player_substitution_prompt_selection(
            incoming,
            "accept",
            self.server._user_states[incoming.username],
        )

        assert game.get_player_by_id(incoming.uuid) is host_seat
        host_spectator = game.get_player_by_id(host.uuid)
        assert host_spectator is not None and host_spectator.is_spectator
        assert game.get_player_gender(host_seat) is Gender.FEMALE
        assert game.get_player_gender(host_spectator) is Gender.MALE
        assert game.host == host.username
        assert table.host == host.username
        assert game._is_host_management_enabled(host_spectator) is None
        assert next(
            member
            for member in table.members
            if member.username == host.username
        ).is_spectator
        assert self.server._voice_presence_by_user == voice_before
        assert Localization.get(
            host.locale,
            "player-substitution-complete-outgoing-host-you",
            player=incoming.username,
        ) in host.get_spoken_messages()
        assert Localization.get(
            incoming.locale,
            "player-substitution-complete-host-player-you",
            player=host.username,
            player_gender=Gender.MALE.selector,
        ) in incoming.get_spoken_messages()

    @pytest.mark.asyncio
    async def test_duplicate_offer_for_host_seat_uses_first_person_feedback(
        self,
    ) -> None:
        host, incoming, table, game, _bot, _ = (
            self._playing_table_with_bot_and_spectator()
        )
        second = self._online_user("SecondSpectator")
        assert table.add_member(second.username, second, as_spectator=True)
        game.add_spectator(second.username, second)
        self.server._set_in_game_state(second, table.table_id)
        host_seat = game.get_player_by_id(host.uuid)
        assert host_seat is not None

        assert self.server._send_player_substitution_request(
            host,
            table,
            host_seat,
            incoming,
        ) == "pending"
        assert self.server._send_player_substitution_request(
            host,
            table,
            host_seat,
            second,
        ) is None

        assert Localization.get(
            host.locale,
            "player-substitution-self-seat-offer-pending",
        ) in host.get_spoken_messages()

    @pytest.mark.asyncio
    async def test_spectator_host_can_take_bot_seat_without_self_prompt(self) -> None:
        host, first_incoming, table, game, bot, _ = (
            self._playing_table_with_bot_and_spectator()
        )
        host_seat = game.get_player_by_id(host.uuid)
        assert host_seat is not None
        assert self.server._send_player_substitution_request(
            host,
            table,
            host_seat,
            first_incoming,
        ) == "pending"
        await self.server._handle_player_substitution_prompt_selection(
            first_incoming,
            "accept",
            self.server._user_states[first_incoming.username],
        )
        host_spectator = game.get_player_by_id(host.uuid)
        assert host_spectator is not None and host_spectator.is_spectator

        assert self.server._send_player_substitution_request(
            host,
            table,
            bot,
            host,
        ) == "completed"

        assert self.server._pending_player_substitutions == {}
        assert game.get_player_by_id(host.uuid) is bot
        assert not bot.is_spectator and not bot.is_bot
        assert game.host == host.username
        assert table.host == host.username
        assert self.server._user_states[host.username]["menu"] == "in_game"

    @pytest.mark.asyncio
    async def test_spectator_host_taking_human_seat_uses_self_perspectives(
        self,
    ) -> None:
        (
            host,
            outgoing,
            first_incoming,
            table,
            game,
            outgoing_seat,
            _,
        ) = self._playing_table_with_human_and_spectator()
        outgoing._locale = "vi"
        host.set_gender(Gender.MALE)
        outgoing.set_gender(Gender.FEMALE)
        self.db.update_user_gender(host.username, Gender.MALE.value)
        self.db.update_user_gender(outgoing.username, Gender.FEMALE.value)
        host_seat = game.get_player_by_id(host.uuid)
        assert host_seat is not None

        assert self.server._send_player_substitution_request(
            host,
            table,
            host_seat,
            first_incoming,
        ) == "pending"
        await self.server._handle_player_substitution_prompt_selection(
            first_incoming,
            "accept",
            self.server._user_states[first_incoming.username],
        )
        host_spectator = game.get_player_by_id(host.uuid)
        assert host_spectator is not None and host_spectator.is_spectator

        self.server._show_host_substitution_seat_menu(host, table)
        await self.server._handle_host_substitution_seat_selection(
            host,
            f"substitution_seat_{outgoing_seat.id}",
            self.server._user_states[host.username],
        )
        await self.server._handle_host_substitution_spectator_selection(
            host,
            f"substitution_spectator_{host.uuid}",
            self.server._user_states[host.username],
        )

        assert self.server._user_states[host.username]["menu"] == "in_game"
        assert Localization.get(
            host.locale,
            "player-substitution-self-incoming-consent-sent",
            player=outgoing.username,
            player_gender=Gender.FEMALE.selector,
        ) in host.get_spoken_messages()
        assert Localization.get(
            outgoing.locale,
            "player-substitution-request-outgoing-host-incoming",
            host=host.username,
            host_gender=Gender.MALE.selector,
        ) in outgoing.get_spoken_messages()
        repeated_name_message = Localization.get(
            outgoing.locale,
            "player-substitution-request-outgoing",
            host=host.username,
            player=host.username,
            host_gender=Gender.MALE.selector,
            player_gender=Gender.MALE.selector,
        )
        assert repeated_name_message not in outgoing.get_spoken_messages()
        assert self.server._user_states[outgoing.username]["menu"] == (
            PLAYER_SUBSTITUTION_PROMPT_MENU
        )
        assert self.server._user_states[host.username]["menu"] != (
            PLAYER_SUBSTITUTION_PROMPT_MENU
        )

        await self.server._handle_player_substitution_prompt_selection(
            outgoing,
            "accept",
            self.server._user_states[outgoing.username],
        )

        assert game.get_player_by_id(host.uuid) is outgoing_seat
        outgoing_spectator = game.get_player_by_id(outgoing.uuid)
        assert outgoing_spectator is not None
        assert game.get_player_gender(outgoing_seat) is Gender.MALE
        assert game.get_player_gender(outgoing_spectator) is Gender.FEMALE
        assert Localization.get(
            host.locale,
            "player-substitution-complete-player-you",
            player=outgoing.username,
            player_gender=Gender.FEMALE.selector,
        ) in host.get_spoken_messages()
        assert Localization.get(
            outgoing.locale,
            "player-substitution-complete-outgoing-you",
            player=host.username,
        ) in outgoing.get_spoken_messages()
        assert Localization.get(
            first_incoming.locale,
            "player-substitution-complete-player",
            player=host.username,
            outgoing=outgoing.username,
            outgoing_gender=Gender.FEMALE.selector,
        ) in first_incoming.get_spoken_messages()

    @pytest.mark.asyncio
    async def test_turn_timer_is_not_reset(self) -> None:
        host, incoming, table, game, bot, _ = (
            self._playing_table_with_bot_and_spectator(game=CrazyEightsGame())
        )
        game.timer.ticks_remaining = 37
        assert self.server._send_player_substitution_request(
            host,
            table,
            bot,
            incoming,
        ) == "pending"
        await self.server._handle_player_substitution_prompt_selection(
            incoming,
            "accept",
            self.server._user_states[incoming.username],
        )
        assert game.timer.ticks_remaining == 37
        assert game.current_player is game.get_player_by_id(incoming.uuid)

    @pytest.mark.asyncio
    async def test_blocks_and_duplicate_requests_fail_closed(self) -> None:
        host, incoming, table, _game, bot, _ = (
            self._playing_table_with_bot_and_spectator()
        )
        second = self._online_user("SecondSpectator")
        assert table.add_member(second.username, second, as_spectator=True)
        table.game.add_spectator(second.username, second)
        self.server._set_in_game_state(second, table.table_id)

        assert self.server._send_player_substitution_request(
            host,
            table,
            bot,
            incoming,
        ) == "pending"
        assert self.server._send_player_substitution_request(
            host,
            table,
            bot,
            second,
        ) is None
        self.server._cancel_player_substitution_request(incoming.username)
        assert self.db.block_user(second.uuid, host.uuid) == "blocked"
        assert second not in self.server._eligible_substitution_spectators(table)
        assert self.server._send_player_substitution_request(
            host,
            table,
            bot,
            second,
        ) is None
        assert self.server._pending_player_substitutions == {}

    @pytest.mark.asyncio
    async def test_busy_or_stale_participant_sessions_fail_closed(self) -> None:
        (
            host,
            outgoing,
            incoming,
            table,
            game,
            seat,
            _incoming_player,
        ) = self._playing_table_with_human_and_spectator()

        game._pending_actions[incoming.uuid] = "private_input"
        assert self.server._send_player_substitution_request(
            host,
            table,
            seat,
            incoming,
        ) is None
        game._pending_actions.clear()

        game._pending_actions[outgoing.uuid] = "private_input"
        assert self.server._send_player_substitution_request(
            host,
            table,
            seat,
            incoming,
        ) is None
        game._pending_actions.clear()

        stale_session = MockUser(
            incoming.username,
            locale=incoming.locale,
            uuid=incoming.uuid,
        )
        assert self.server._send_player_substitution_request(
            host,
            table,
            seat,
            stale_session,
        ) is None

        assert self.db.block_user(incoming.uuid, outgoing.uuid) == "blocked"
        assert self.server._send_player_substitution_request(
            host,
            table,
            seat,
            incoming,
        ) is None
        assert self.server._pending_player_substitutions == {}

    @pytest.mark.asyncio
    async def test_returning_reserved_owner_cancels_request(self) -> None:
        host = self._online_user("Host")
        former = self._online_user("Former")
        incoming = self._online_user("Incoming")
        table = self.server._tables.create_table("pig", host.username, host)
        game = PigGame(options=PigOptions(target_score=25))
        table.game = game
        game._table = table
        game.initialize_lobby(host.username, host)
        assert table.add_member(former.username, former)
        former_player = game.add_player(former.username, former)
        game.on_start()
        assert table.add_member(incoming.username, incoming, as_spectator=True)
        game.add_spectator(incoming.username, incoming)
        self.server._set_in_game_state(incoming, table.table_id)

        self.server._users.pop(former.username)
        game.on_player_disconnect(former.uuid)
        replacement = game.get_player_by_id(former.uuid)
        assert replacement is former_player and replacement.is_bot
        assert self.server._send_player_substitution_request(
            host,
            table,
            replacement,
            incoming,
        ) == "pending"

        self.server._users[former.username] = former
        self.server._restore_user_state(former, former.username)

        assert incoming.username not in self.server._pending_player_substitutions
        assert self.server._user_states[incoming.username]["menu"] == "in_game"
        assert game.get_player_by_id(former.uuid) is former_player
        assert not former_player.is_bot
        assert game.get_player_by_id(incoming.uuid).is_spectator

    @pytest.mark.asyncio
    async def test_game_reset_cancels_request_bound_to_old_instance(self) -> None:
        host, incoming, table, old_game, bot, _ = (
            self._playing_table_with_bot_and_spectator()
        )
        assert self.server._send_player_substitution_request(
            host,
            table,
            bot,
            incoming,
        ) == "pending"
        assert table.reset_game()
        assert table.game is not old_game
        assert self.server._pending_player_substitutions == {}
        assert self.server._user_states[incoming.username] == {
            "menu": "in_game",
            "table_id": table.table_id,
        }


def _generic_playing_game(game_class):
    game = game_class()
    game.status = "playing"
    game.game_active = True
    game.setup_player_actions = lambda _player: None
    return game


@pytest.mark.parametrize(
    "game_class",
    GameRegistry.get_all(),
    ids=lambda game_class: game_class.get_type(),
)
def test_every_game_can_substitute_a_bot_seat(game_class) -> None:
    game = _generic_playing_game(game_class)
    bot_user = Bot("Botty", uuid="old-seat-id")
    incoming_user = MockUser("Incoming", uuid="new-account-id")
    bot = game.create_player(bot_user.uuid, bot_user.username, is_bot=True)
    spectator = game.create_player(
        incoming_user.uuid,
        incoming_user.username,
        is_bot=False,
    )
    spectator.is_spectator = True
    game.players.extend([bot, spectator])
    game._users = {bot.id: bot_user, spectator.id: incoming_user}
    game.turn_player_ids = [bot.id]
    game.player_action_sets = {bot.id: [], spectator.id: []}
    game.play_private_ambience(
        bot,
        "test/seat-loop.ogg",
        handle="seat:private",
        layer="seat",
    )
    if hasattr(game, "tiebreaker_player_names"):
        game.tiebreaker_player_names = [bot.name]

    result = game.substitute_player_with_spectator(
        bot,
        spectator,
        incoming_user,
    )

    assert result.previous_controller_name == "Botty"
    assert result.replaced_human_name == ""
    assert result.outgoing_spectator is None
    assert game.players == [bot]
    assert bot.id == incoming_user.uuid
    assert game.turn_player_ids == [incoming_user.uuid]
    if hasattr(game, "tiebreaker_player_names"):
        assert game.tiebreaker_player_names == [incoming_user.username]
    assert game.get_user(bot) is incoming_user
    audio_state = next(iter(game.active_audio.values()))
    assert audio_state.recipient_ids == [incoming_user.uuid]
    assert all("old-seat-id" not in key for key in game.active_audio)
    assert "old-seat-id" not in game.to_json()
    restored = game_class.from_json(game.to_json())
    assert restored.get_player_by_id(incoming_user.uuid) is not None


@pytest.mark.parametrize(
    "game_class",
    GameRegistry.get_all(),
    ids=lambda game_class: game_class.get_type(),
)
def test_every_game_can_substitute_a_human_and_retain_host_identity(game_class) -> None:
    game = _generic_playing_game(game_class)
    outgoing_user = MockUser("Outgoing", uuid="old-seat-id")
    incoming_user = MockUser("Incoming", uuid="new-account-id")
    seat = game.create_player(
        outgoing_user.uuid,
        outgoing_user.username,
        is_bot=False,
    )
    spectator = game.create_player(
        incoming_user.uuid,
        incoming_user.username,
        is_bot=False,
    )
    spectator.is_spectator = True
    game.players.extend([seat, spectator])
    game._users = {seat.id: outgoing_user, spectator.id: incoming_user}
    game.turn_player_ids = [seat.id]
    game.player_action_sets = {seat.id: [], spectator.id: []}
    game.host = outgoing_user.username

    result = game.substitute_player_with_spectator(
        seat,
        spectator,
        incoming_user,
        outgoing_user=outgoing_user,
    )

    outgoing_spectator = result.outgoing_spectator
    assert outgoing_spectator is not None
    assert outgoing_spectator.id == outgoing_user.uuid
    assert outgoing_spectator.is_spectator
    assert game.get_user(outgoing_spectator) is outgoing_user
    assert seat.id == incoming_user.uuid
    assert game.get_user(seat) is incoming_user
    assert game.turn_player_ids == [incoming_user.uuid]
    assert game.host == outgoing_user.username
    restored = game_class.from_json(game.to_json())
    assert restored.host == outgoing_user.username
    assert restored.get_player_by_id(incoming_user.uuid) is not None
    assert restored.get_player_by_id(outgoing_user.uuid).is_spectator
