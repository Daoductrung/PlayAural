import asyncio
from concurrent.futures import Future
from threading import Event

import pytest

from ..audio import SameTurnAudioBatcher
from ..core.server import (
    HOST_GAME_SWITCH_ACTION_PREFIX,
    HOST_GAME_SWITCH_CONFIRM_MENU,
    HOST_GAME_SWITCH_MENU,
    Server,
)
from ..games.crazyeights.game import CrazyEightsGame
from ..games.chess.bot import BotSearchJob
from ..games.chess.game import ChessGame
from ..games.pig.game import PigGame, PigOptions
from ..game_utils.sequence_runner_mixin import SequenceBeat
from ..messages.localization import Localization
from ..tables import table as table_module
from ..ui.confirmation import CONFIRMATION_PROMPT_ITEM_ID
from ..users.bot import Bot
from ..users.test_user import MockUser


def _menu_ids(user: MockUser, menu_id: str) -> list[str | None]:
    return [item.id for item in user.get_current_menu_items(menu_id) or []]


def _make_table(*, host_spectates: bool = False):
    server = Server(db_path=":memory:")
    server._db.connect()
    host = MockUser("Host", uuid="host-id")
    player = MockUser("Player", uuid="player-id")
    observer = MockUser("Observer", uuid="observer-id")
    server._users = {
        host.username: host,
        player.username: player,
        observer.username: observer,
    }

    table = server._tables.create_table("pig", host.username, host)
    game = PigGame(options=PigOptions(target_score=75))
    table.game = game
    game._table = table
    game.initialize_lobby(host.username, host)
    server._set_in_game_state(host, table.table_id)

    assert table.add_member(player.username, player)
    game.add_player(player.username, player)
    server._set_in_game_state(player, table.table_id)

    if host_spectates:
        table.members[0].is_spectator = True
        game.get_player_by_id(host.uuid).is_spectator = True

    bot_user = Bot("Table Jester", uuid="bot-id")
    bot_player = game.add_player(bot_user.username, bot_user)
    bot_player.bot_name_base = "Table Jester"
    game.status = "playing"
    game.game_active = True
    game._sync_table_status()
    return server, table, game, host, player, observer, bot_player


@pytest.mark.asyncio
async def test_host_switches_game_without_replacing_the_table_session() -> None:
    server, table, old_game, host, player, observer, old_bot = _make_table(
        host_spectates=True
    )
    table.is_private = True
    table.ban_user("banned-account")
    table.mark_power_restored(180)
    server._voice_presence_by_user[host.username] = {
        "scope": "table",
        "context_id": table.table_id,
    }
    old_table_id = table.table_id
    old_bot_base = old_bot.bot_name_base
    old_bot.round_score = 41
    old_game.play_music("test/old-game.ogg")
    old_game.current_music = "legacy/old-game.ogg"
    old_game.current_ambience = "legacy/old-ambience.ogg"
    old_game.current_ambience_outro = "legacy/old-outro.ogg"
    old_game.schedule_sound("test/delayed.ogg", delay_ticks=100)
    old_game.start_sequence(
        "old-game-sequence",
        [SequenceBeat.pause(100)],
        start_immediately=False,
    )
    stale_audio_batch: list[bool] = []
    old_game._table_presence_audio_batcher = SameTurnAudioBatcher()
    old_game._table_presence_audio_batcher.queue(
        "old-game-cue",
        lambda: stale_audio_batch.append(True),
    )
    for user in (host, player, observer):
        user.clear_messages()

    await server._handle_host_game_switch_confirm_selection(
        host,
        "yes",
        {
            "table_id": table.table_id,
            "target_game_type": "crazyeights",
        },
    )
    await asyncio.sleep(0)

    assert server._tables.get_table(old_table_id) is table
    assert table.table_id == old_table_id
    assert table.game_type == "crazyeights"
    assert isinstance(table.game, CrazyEightsGame)
    assert table.game is not old_game
    assert table.game.status == "waiting"
    assert table.status == "waiting"
    assert table.host == host.username
    assert table.is_private is True
    assert table.is_banned("banned-account")
    assert table.is_power_restore_grace_active() is False
    assert table._power_restore_started_at is None
    assert old_game._destroyed is True
    assert old_game._table is None
    assert old_game._users == {}
    assert old_game.active_audio == {}
    assert old_game.current_music == ""
    assert old_game.current_ambience == ""
    assert old_game.current_ambience_outro == ""
    assert old_game.scheduled_sounds == []
    assert old_game.active_sequences == []
    assert old_game.player_action_sets == {}
    assert old_game._keybinds == {}
    assert stale_audio_batch == []

    new_host = table.game.get_player_by_id(host.uuid)
    new_player = table.game.get_player_by_id(player.uuid)
    new_bot = next(candidate for candidate in table.game.players if candidate.is_bot)
    assert new_host is not None and new_host.is_spectator
    assert new_player is not None and not new_player.is_spectator
    assert new_bot.bot_name_base == old_bot_base
    assert not hasattr(new_bot, "round_score")
    assert new_bot.score == 0
    assert table.game.options.winning_score == 500
    assert table.game.active_audio == {}
    assert table.game.scheduled_sounds == []
    assert table.game.active_sequences == []
    assert [candidate.id for candidate in table.game.players] == [
        host.uuid,
        player.uuid,
        old_bot.id,
    ]
    assert [member.is_spectator for member in table.members] == [True, False]
    assert server._tables.find_user_table(host.username) is table
    assert server._tables.find_user_table(player.username) is table
    assert server._voice_presence_by_user[host.username]["context_id"] == old_table_id
    assert server._user_states[host.username] == {
        "menu": "in_game",
        "table_id": old_table_id,
    }
    assert server._user_states[player.username] == {
        "menu": "in_game",
        "table_id": old_table_id,
    }

    host_text = " ".join(host.get_spoken_messages())
    player_text = " ".join(player.get_spoken_messages())
    assert "You switched this table" in host_text
    assert "Host switched this table" in player_text
    assert not observer.get_spoken_messages()
    for participant in (host, player):
        assert any(
            message.type == "audio"
            and message.data.get("command") == "stop_all"
            for message in participant.messages
        )
        assert any(message.type == "clear_ui" for message in participant.messages)
        assert any(
            message.type == "table_context"
            and message.data.get("table_id") == old_table_id
            for message in participant.messages
        )
        assert participant.get_current_menu_items("turn_menu")


@pytest.mark.asyncio
async def test_switch_menu_confirms_and_filters_games_that_cannot_hold_roster() -> None:
    server, table, old_game, host, _player, _observer, _bot = _make_table()
    server._open_host_management_from_game(host, table)

    await server._handle_host_management_selection(
        host,
        "switch_game",
        {"table_id": table.table_id},
    )

    assert server._user_states[host.username]["menu"] == HOST_GAME_SWITCH_MENU
    switch_ids = _menu_ids(host, HOST_GAME_SWITCH_MENU)
    assert f"{HOST_GAME_SWITCH_ACTION_PREFIX}crazyeights" in switch_ids
    assert f"{HOST_GAME_SWITCH_ACTION_PREFIX}chess" not in switch_ids

    await server._handle_host_game_switch_selection(
        host,
        f"{HOST_GAME_SWITCH_ACTION_PREFIX}crazyeights",
        server._user_states[host.username],
    )

    assert server._user_states[host.username]["menu"] == HOST_GAME_SWITCH_CONFIRM_MENU
    assert _menu_ids(host, HOST_GAME_SWITCH_CONFIRM_MENU) == [
        CONFIRMATION_PROMPT_ITEM_ID,
        "yes",
        "no",
    ]

    await server._handle_host_game_switch_confirm_selection(
        host,
        "no",
        server._user_states[host.username],
    )
    assert table.game is old_game
    assert server._user_states[host.username]["menu"] == HOST_GAME_SWITCH_MENU


@pytest.mark.asyncio
async def test_stale_incompatible_switch_is_rejected_without_mutation() -> None:
    server, table, old_game, host, _player, _observer, _bot = _make_table()
    host.clear_messages()

    await server._handle_host_game_switch_confirm_selection(
        host,
        "yes",
        {
            "table_id": table.table_id,
            "target_game_type": "chess",
            "_stack": [
                {
                    "menu": HOST_GAME_SWITCH_MENU,
                    "table_id": table.table_id,
                    "game_switch_page": 1,
                    "game_switch_page_count": 1,
                }
            ],
        },
    )

    assert table.game is old_game
    assert table.game_type == "pig"
    assert "supports at most 2 active seats" in " ".join(
        host.get_spoken_messages()
    )


def test_switch_fails_closed_when_live_member_is_missing_from_game_roster() -> None:
    server, table, old_game, host, player, _observer, _bot = _make_table()
    old_game.players = [
        candidate
        for candidate in old_game.players
        if candidate.id != player.uuid
    ]

    with pytest.raises(ValueError):
        table.game_transition_active_seat_count()

    items, page = server._get_host_game_switch_menu_items(host, table)
    assert page.items == []
    assert [item.id for item in items] == [
        "game_switch_roster_invalid",
        "back",
    ]
    assert not table.transition_to_game("crazyeights")
    assert table.game is old_game
    assert table.game_type == "pig"
    assert table.get_user(player.username) is player


@pytest.mark.asyncio
async def test_switch_cancels_invitation_bound_to_old_game() -> None:
    server, table, _old_game, host, _player, observer, _bot = _make_table()
    invite_id = "a" * 32
    server._pending_invites[observer.username] = {
        "invite_id": invite_id,
        "table_id": table.table_id,
        "host_username": host.username,
        "host_uuid": host.uuid,
        "invitee_uuid": observer.uuid,
        "game_type": table.game_type,
        "game_name": "Pig",
        "task": None,
        "deferred": False,
    }
    server._user_states[observer.username] = {
        "menu": "table_invite_prompt",
        "table_id": table.table_id,
        "invite_id": invite_id,
        "prev_state": {"menu": "main_menu"},
    }
    observer.clear_messages()

    await server._handle_host_game_switch_confirm_selection(
        host,
        "yes",
        {
            "table_id": table.table_id,
            "target_game_type": "crazyeights",
        },
    )

    assert observer.username not in server._pending_invites
    assert server._user_states[observer.username]["menu"] == "main_menu"
    assert Localization.get(
        observer.locale,
        "table-invite-no-longer-available",
    ) in observer.get_spoken_messages()


def test_invitation_consent_is_bound_to_the_selected_game_type(
    monkeypatch,
) -> None:
    server, table, old_game, host, _player, observer, _bot = _make_table()
    monkeypatch.setattr(
        server,
        "_table_invite_eligibility_error",
        lambda _host, _table, _invitee: None,
    )
    invite = {
        "invite_id": "b" * 32,
        "table_id": table.table_id,
        "host_username": host.username,
        "host_uuid": host.uuid,
        "invitee_uuid": observer.uuid,
        "game_type": old_game.get_type(),
        "game_name": "Pig",
    }
    assert server._resolve_valid_pending_table_invite(observer, invite) is table

    replacement = CrazyEightsGame()
    replacement._table = table
    table._game = replacement
    table.game_type = replacement.get_type()
    assert server._resolve_valid_pending_table_invite(observer, invite) is None


def test_transition_releases_offline_reservation_and_keeps_replacement_bot() -> None:
    server = Server(db_path=":memory:")
    server._db.connect()
    host = MockUser("Host", uuid="host-id")
    guest = MockUser("Guest", uuid="guest-id")
    server._users = {host.username: host, guest.username: guest}
    table = server._tables.create_table("pig", host.username, host)
    game = PigGame()
    table.game = game
    game._table = table
    game.initialize_lobby(host.username, host)
    assert table.add_member(guest.username, guest)
    guest_player = game.add_player(guest.username, guest)
    game.status = "playing"
    game.game_active = True
    server._users.pop(guest.username)
    game.on_player_disconnect(guest.uuid)
    assert guest_player.is_bot and guest_player.replaced_human

    assert table.transition_to_game("crazyeights")

    assert [member.username for member in table.members] == [host.username]
    assert server._tables.find_user_table(guest.username) is None
    transitioned_bot = next(
        candidate for candidate in table.game.players if candidate.is_bot
    )
    assert transitioned_bot.id != guest.uuid
    assert transitioned_bot.replaced_human is False
    assert transitioned_bot.bot_name_base == guest_player.bot_name_base


def test_transition_uses_the_authoritative_replacement_session() -> None:
    server, table, _old_game, old_host, _player, _observer, _bot = _make_table()
    replacement_session = MockUser(
        old_host.username,
        locale="vi",
        uuid=old_host.uuid,
    )
    server._users[old_host.username] = replacement_session
    old_host.clear_messages()
    replacement_session.clear_messages()

    assert table.transition_to_game("crazyeights")

    host_player = table.game.get_player_by_id(old_host.uuid)
    assert table.get_user(old_host.username) is replacement_session
    assert table.game.get_user(host_player) is replacement_session
    assert replacement_session in table.game._users.values()
    assert old_host not in table.game._users.values()
    assert any(
        message.type == "audio" and message.data.get("command") == "stop_all"
        for message in replacement_session.messages
    )
    assert not any(
        message.type == "audio" and message.data.get("command") == "stop_all"
        for message in old_host.messages
    )


def test_transition_never_infers_stale_membership_from_a_reused_username() -> None:
    server, table, _old_game, _host, player, _observer, _bot = _make_table()
    replacement_account = MockUser(player.username, uuid="different-account-id")
    table._users.pop(player.username)
    server._users[player.username] = replacement_account

    assert table.transition_to_game("crazyeights")

    assert all(member.username != player.username for member in table.members)
    assert table.game.get_player_by_id(player.uuid) is None
    assert table.game.get_player_by_id(replacement_account.uuid) is None
    assert server._tables.find_user_table(player.username) is None


def test_transition_preparation_failure_leaves_current_game_untouched(
    monkeypatch,
) -> None:
    server, table, old_game, host, player, _observer, bot = _make_table()
    old_members = list(table.members)
    old_users = dict(table._users)
    old_bot_user = old_game._users[bot.id]
    old_bot_name = old_bot_user.username

    class BrokenGame(CrazyEightsGame):
        def to_json(self) -> str:
            raise RuntimeError("target serialization failed")

    original_get_game_class = table_module.get_game_class
    monkeypatch.setattr(
        table_module,
        "get_game_class",
        lambda game_type: (
            BrokenGame
            if game_type == "broken"
            else original_get_game_class(game_type)
        ),
    )
    host.clear_messages()
    player.clear_messages()

    assert table.transition_to_game("broken") is False

    assert table.game is old_game
    assert table.game_type == "pig"
    assert table.members == old_members
    assert table._users == old_users
    assert old_game._destroyed is False
    assert old_game._table is table
    assert old_game._users[bot.id] is old_bot_user
    assert old_bot_user.username == old_bot_name
    assert not any(
        message.type == "audio" and message.data.get("command") == "stop_all"
        for user in (host, player)
        for message in user.messages
    )


def test_transition_cancels_and_forgets_chess_bot_searches() -> None:
    server = Server(db_path=":memory:")
    server._db.connect()
    host = MockUser("Host", uuid="host-id")
    server._users = {host.username: host}
    table = server._tables.create_table("chess", host.username, host)
    game = ChessGame()
    table.game = game
    game._table = table
    game.initialize_lobby(host.username, host)

    pending = Future()
    cancel_event = Event()
    game._chess_bot_jobs[host.uuid] = BotSearchJob(
        signature="old-position",
        future=pending,
        cancel_event=cancel_event,
    )

    assert table.transition_to_game("pig")

    assert cancel_event.is_set()
    assert pending.cancelled()
    assert game._chess_bot_jobs == {}
    assert game._destroyed is True
    assert game._table is None
