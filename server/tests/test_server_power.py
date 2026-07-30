from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from ..core import power as power_module
from ..core.power import PowerAction, ScheduledPowerOperation, ServerPowerManager
from ..core.server import Server
from ..games.pig.game import PigGame
from ..messages.localization import Localization
from ..persistence.database import Database
from ..tables.manager import TableManager
from ..tables.table import Table
from ..users.base import MenuItem
from ..users.test_user import MockUser


class DummyClient:
    def __init__(self, username: str):
        self.username = username
        self.address = ("127.0.0.1", 0)
        self.authenticated = True
        self.retired = False
        self.session_ready = True

    async def send(self, packet: dict) -> None:
        return None


def _item_ids(items: list[str | MenuItem]) -> list[str | None]:
    return [item.id if isinstance(item, MenuItem) else None for item in items]


def test_power_countdown_points_follow_tiered_schedule() -> None:
    points = ServerPowerManager._announcement_points(7200)

    assert points[:4] == [7200, 5400, 3600, 1800]
    assert 600 in points
    assert 300 in points
    assert 60 in points
    assert 30 in points
    assert points[-10:] == list(range(10, 0, -1))


@pytest.mark.asyncio
async def test_power_countdown_waits_after_final_one(monkeypatch) -> None:
    now = 0.0

    def fake_monotonic() -> float:
        return now

    async def fake_sleep(seconds: float) -> None:
        nonlocal now
        now += seconds

    server = Server()
    manager = ServerPowerManager(server)
    seen: list[tuple[int, float]] = []

    async def fake_broadcast(
        operation: ScheduledPowerOperation, seconds_remaining: int
    ) -> None:
        seen.append((seconds_remaining, now))

    monkeypatch.setattr(power_module, "monotonic", fake_monotonic)
    monkeypatch.setattr(power_module.asyncio, "sleep", fake_sleep)
    manager.broadcast_countdown = fake_broadcast  # type: ignore[method-assign]

    operation = ScheduledPowerOperation(
        operation_id="op",
        action=PowerAction.REBOOT,
        delay_seconds=10,
        requested_by="Dev",
        reason_id="update",
    )

    await manager._run_countdown(operation)

    assert seen[0] == (10, 0.0)
    assert seen[-1] == (1, 9.0)
    assert now == 10.0


@pytest.mark.asyncio
async def test_power_finalization_failure_unlocks_manager(monkeypatch) -> None:
    now = 0.0

    def fake_monotonic() -> float:
        return now

    async def fake_sleep(seconds: float) -> None:
        nonlocal now
        now += seconds

    server = Server()
    dev = MockUser("Dev")
    dev.connection = DummyClient("Dev")
    server._users = {"Dev": dev}
    manager = ServerPowerManager(server)

    async def fake_broadcast(
        operation: ScheduledPowerOperation, seconds_remaining: int
    ) -> None:
        return None

    async def fail_finalization(operation: ScheduledPowerOperation) -> None:
        raise RuntimeError("checkpoint failed")

    monkeypatch.setattr(power_module, "monotonic", fake_monotonic)
    monkeypatch.setattr(power_module.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(server, "_finalize_power_operation", fail_finalization)
    manager.broadcast_countdown = fake_broadcast  # type: ignore[method-assign]

    operation = ScheduledPowerOperation(
        operation_id="op",
        action=PowerAction.REBOOT,
        delay_seconds=10,
        requested_by="Dev",
        reason_id="update",
    )
    manager._operation = operation

    await manager._run(operation)

    assert not manager.is_finalizing
    assert manager.active_operation is None
    assert not manager.is_scheduled


def test_active_table_checkpoints_replace_and_prune(tmp_path) -> None:
    db = Database(tmp_path / "power.db")
    db.connect()
    try:
        table = Table(table_id="abc", game_type="pig", host="Alice")
        table.members = []
        db.save_all_tables(
            [table],
            checkpoint_kind="planned_reboot",
            checkpoint_expires_at=(datetime.now() + timedelta(hours=1)).isoformat(),
            checkpoint_operation_id="op1",
        )

        loaded = db.load_all_tables()
        assert len(loaded) == 1
        assert getattr(loaded[0], "_checkpoint_kind") == "planned_reboot"

        db.save_all_tables([])
        assert db.load_all_tables() == []

        db.save_all_tables([table], checkpoint_kind="planned_reboot")
        old = (datetime.now() - timedelta(days=2)).isoformat()
        db._conn.execute(
            "UPDATE tables SET checkpoint_created_at = ?",
            (old,),
        )
        db._conn.commit()
        db.prune_old_records()
        assert db.load_all_tables() == []
    finally:
        db.close()


def test_admin_power_menu_is_dev_only(tmp_path) -> None:
    server = Server(db_path=tmp_path / "power.db")
    admin = MockUser("Admin")
    admin.trust_level = 2
    dev = MockUser("Dev")
    dev.trust_level = 3

    server.admin_manager._show_admin_menu(admin)
    server.admin_manager._show_admin_menu(dev)

    assert "server_power" not in _item_ids(admin.get_current_menu_items("admin_menu"))
    assert "server_power" in _item_ids(dev.get_current_menu_items("admin_menu"))


@pytest.mark.asyncio
async def test_legacy_power_chat_commands_do_not_schedule(tmp_path) -> None:
    server = Server(db_path=tmp_path / "power.db")
    dev = MockUser("Dev")
    dev.trust_level = 3
    dev.connection = DummyClient("Dev")
    server._users = {"Dev": dev}

    server.db.connect()
    try:
        await server._handle_chat(
            DummyClient("Dev"),
            {"type": "chat", "convo": "global", "message": "/reboot"},
        )
    finally:
        server.db.close()

    assert not server.power_manager.is_scheduled
    assert dev.get_last_spoken() == Localization.get(
        dev.locale, "server-power-command-removed"
    )


@pytest.mark.asyncio
async def test_power_finalizing_disconnect_skips_bot_takeover(tmp_path) -> None:
    server = Server(db_path=tmp_path / "power.db")
    server.db.connect()
    server._tables = TableManager()
    server._tables._server = server
    server._pending_disconnects = {}
    server._pending_invites = {}
    server._voice_presence_by_user = {}
    server._voice_join_authorizations_by_user = {}
    server._audio_input_devices_by_user = {}
    server._user_states = {}

    alice_client = DummyClient("Alice")
    alice = MockUser("Alice")
    alice.connection = alice_client
    bob = MockUser("Bob")
    bob.connection = DummyClient("Bob")
    server._users = {"Alice": alice, "Bob": bob}

    table = server._tables.create_table("pig", "Alice", alice)
    table.add_member("Bob", bob)
    game = PigGame()
    game.add_player("Alice", alice)
    game.add_player("Bob", bob)
    game.status = "playing"
    table.game = game
    game._table = table
    table.status = "playing"
    server.power_manager._finalizing = True

    try:
        await server._on_client_disconnect(alice_client)
    finally:
        server.db.close()

    player = game.get_player_by_id(alice.uuid)
    assert player is not None
    assert not player.is_bot


def test_power_restore_waiting_lobby_prunes_stale_game_users(tmp_path) -> None:
    server = Server(db_path=tmp_path / "power.db")
    server._tables = TableManager()
    server._tables._server = server

    alice = MockUser("Alice")
    bob = MockUser("Bob")
    server._users = {"Alice": alice}

    table = server._tables.create_table("pig", "Alice", alice)
    table.add_member("Bob", bob)
    game = PigGame()
    game.add_player("Alice", alice)
    game.add_player("Bob", bob)
    game.status = "waiting"
    table.game = game
    game._table = table

    assert bob.uuid in game._users

    table.mark_power_restored(0)
    table.on_tick()

    assert [member.username for member in table.members] == ["Alice"]
    assert game.get_player_by_id(bob.uuid) is None
    assert bob.uuid not in game._users
    assert bob.uuid not in game.player_action_sets


def _make_restored_playing_pig_table(tmp_path):
    server = Server(db_path=tmp_path / "power.db")
    server._tables = TableManager()
    server._tables._server = server

    alice = MockUser("Alice", uuid="alice")
    bob = MockUser("Bob", uuid="bob")
    alice.connection = DummyClient("Alice")
    bob.connection = DummyClient("Bob")

    table = server._tables.create_table("pig", "Alice", alice)
    table.add_member("Bob", bob)
    game = PigGame()
    game.setup_keybinds()
    game.add_player("Alice", alice)
    game.add_player("Bob", bob)
    game.status = "playing"
    game.host = "Alice"
    table.game = game
    game._table = table
    table.status = "playing"
    table.mark_power_restored(180)
    return server, table, game, alice, bob


def _add_restored_player(table, game, username: str, uuid: str) -> MockUser:
    user = MockUser(username, uuid=uuid)
    user.connection = DummyClient(username)
    table.add_member(username, user)
    game.add_player(username, user)
    return user


def _attach_restored_players(server, table, game, *users: MockUser) -> None:
    server._users = {user.username: user for user in users}
    game._users.clear()
    table._users.clear()
    for user in users:
        table.attach_user(user.username, user)
        game.attach_user(user.uuid, user)
        server._set_in_game_state(user, table.table_id)


@pytest.mark.asyncio
async def test_power_restore_grace_blocks_game_keybind_with_feedback(tmp_path) -> None:
    server, table, game, alice, bob = _make_restored_playing_pig_table(tmp_path)
    _attach_restored_players(server, table, game, alice)
    alice.clear_messages()

    await server._handle_keybind(
        alice.connection,
        {"type": "keybind", "key": "s"},
    )

    expected = Localization.get(
        alice.locale,
        "server-power-restore-input-blocked",
        seconds=table.power_restore_remaining_seconds(),
        players="Bob",
    )
    assert alice.get_last_spoken() == expected


@pytest.mark.asyncio
async def test_power_restore_grace_allows_leave_confirmation_and_cancel(
    tmp_path,
) -> None:
    server, table, game, alice, bob = _make_restored_playing_pig_table(tmp_path)
    _attach_restored_players(server, table, game, alice)
    alice.clear_messages()

    await server._handle_menu(
        alice.connection,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "web_leave_table",
        },
    )

    assert "leave_game_confirm" in alice.menus
    assert alice.get_last_spoken() == Localization.get(
        alice.locale,
        "confirm-leave-game",
    )

    await server._handle_menu(
        alice.connection,
        {
            "type": "menu",
            "menu_id": "leave_game_confirm",
            "selection_id": "no",
        },
    )

    assert table.get_user("Alice") is alice
    assert server._user_states[alice.username]["menu"] == "in_game"


@pytest.mark.asyncio
async def test_power_restore_grace_allows_ctrl_q_leave_shortcut(tmp_path) -> None:
    server, table, game, alice, bob = _make_restored_playing_pig_table(tmp_path)
    _attach_restored_players(server, table, game, alice)
    alice.clear_messages()

    await server._handle_keybind(
        alice.connection,
        {"type": "keybind", "key": "q", "control": True},
    )

    assert "leave_game_confirm" in alice.menus
    assert alice.get_last_spoken() == Localization.get(
        alice.locale,
        "confirm-leave-game",
    )


@pytest.mark.asyncio
async def test_power_restore_voluntary_host_leave_replaces_seat_and_promotes_host(
    tmp_path,
) -> None:
    server, table, game, alice, bob = _make_restored_playing_pig_table(tmp_path)
    server.db.connect()
    try:
        _attach_restored_players(server, table, game, alice)
        alice.clear_messages()

        await server._handle_keybind(
            alice.connection,
            {"type": "keybind", "key": "q", "control": True},
        )
        await server._handle_menu(
            alice.connection,
            {
                "type": "menu",
                "menu_id": "leave_game_confirm",
                "selection_id": "yes",
            },
        )

        alice_player = game.get_player_by_id(alice.uuid)
        assert alice_player is not None
        assert alice_player.is_bot
        assert alice_player.replaced_human_name == "Alice"
        assert table.get_user("Alice") is None
        assert server._tables.find_user_table("Alice") is None
        assert server._user_states[alice.username]["menu"] == "main_menu"
        assert "Alice" not in table.power_restore_missing_player_names()
        assert table.host == "Bob"
        assert game.host == "Bob"
        assert table.is_power_restore_grace_active()
    finally:
        server.db.close()


@pytest.mark.asyncio
async def test_power_restore_host_leave_with_only_offline_humans_keeps_table_paused(
    tmp_path,
) -> None:
    server, table, game, alice, bob = _make_restored_playing_pig_table(tmp_path)
    carol = _add_restored_player(table, game, "Carol", "carol")
    server.db.connect()
    try:
        _attach_restored_players(server, table, game, alice)

        await server._handle_keybind(
            alice.connection,
            {"type": "keybind", "key": "q", "control": True},
        )
        await server._handle_menu(
            alice.connection,
            {
                "type": "menu",
                "menu_id": "leave_game_confirm",
                "selection_id": "yes",
            },
        )

        assert table.host == "Bob"
        assert table.is_power_restore_grace_active()
        assert table.power_restore_missing_player_names() == ["Bob", "Carol"]

        assert table._power_restore_started_at is not None
        table._power_restore_started_at -= table._power_restore_grace_seconds + 1
        table.on_tick()

        assert table.is_power_restore_grace_active()
        assert not table._destroyed
        assert game.get_player_by_id(bob.uuid).is_bot is False
        assert game.get_player_by_id(carol.uuid).is_bot is False
        assert table._offline_since is not None

        table._offline_since -= 301
        table.on_tick()

        assert table._destroyed
        assert server._tables.get_table(table.table_id) is None
    finally:
        server.db.close()


@pytest.mark.asyncio
async def test_power_restore_offline_successor_can_resume_after_owner_leaves(
    tmp_path,
) -> None:
    server, table, game, alice, bob = _make_restored_playing_pig_table(tmp_path)
    carol = _add_restored_player(table, game, "Carol", "carol")
    server.db.connect()
    try:
        _attach_restored_players(server, table, game, alice)

        await server._handle_keybind(
            alice.connection,
            {"type": "keybind", "key": "q", "control": True},
        )
        await server._handle_menu(
            alice.connection,
            {
                "type": "menu",
                "menu_id": "leave_game_confirm",
                "selection_id": "yes",
            },
        )

        table.attach_user("Bob", bob)
        game.attach_user(bob.uuid, bob)
        server._users = {"Bob": bob}
        assert table._power_restore_started_at is not None
        table._power_restore_started_at -= table._power_restore_grace_seconds + 1

        table.on_tick()

        assert not table.is_power_restore_grace_active()
        assert table.host == "Bob"
        assert game.host == "Bob"
        alice_player = game.get_player_by_id(alice.uuid)
        carol_player = game.get_player_by_id(carol.uuid)
        assert alice_player is not None and alice_player.is_bot
        assert carol_player is not None and carol_player.is_bot
        assert carol_player.replaced_human_name == "Carol"
        assert Localization.get(
            bob.locale,
            "server-power-restore-complete-with-bots",
        ) in bob.get_spoken_messages()
    finally:
        server.db.close()


def test_power_restore_reconnect_does_not_emit_premature_game_resumed(
    tmp_path,
) -> None:
    server, table, game, alice, bob = _make_restored_playing_pig_table(tmp_path)
    server._users = {"Alice": alice}
    game._users.clear()
    table._users.clear()

    table.attach_user("Alice", alice)
    game.attach_user(alice.uuid, alice)

    player = game.get_player_by_id(alice.uuid)
    assert player is not None
    assert player.reconnect_grace_ticks == 0
    assert Localization.get(alice.locale, "game-resumed", player="Alice") not in (
        alice.get_spoken_messages()
    )


def test_power_restore_complete_announces_after_all_players_return(
    tmp_path,
) -> None:
    server, table, game, alice, bob = _make_restored_playing_pig_table(tmp_path)
    server._users = {"Alice": alice, "Bob": bob}
    game._users.clear()
    table._users.clear()
    table.attach_user("Alice", alice)
    table.attach_user("Bob", bob)
    game.attach_user(alice.uuid, alice)
    game.attach_user(bob.uuid, bob)
    alice.clear_messages()
    bob.clear_messages()

    table.on_tick()

    expected = Localization.get(alice.locale, "server-power-restore-complete")
    assert expected in alice.get_spoken_messages()
    assert expected in bob.get_spoken_messages()
    assert not table.is_power_restore_grace_active()


def test_power_restore_no_show_host_is_replaced_and_host_promoted(
    tmp_path,
) -> None:
    server, table, game, alice, bob = _make_restored_playing_pig_table(tmp_path)
    server.db.connect()
    try:
        server._users = {"Bob": bob}
        game._users.clear()
        table._users.clear()
        table.attach_user("Bob", bob)
        game.attach_user(bob.uuid, bob)
        table.mark_power_restored(0)
        bob.clear_messages()

        table.on_tick()

        alice_player = game.get_player_by_id(alice.uuid)
        assert alice_player is not None
        assert alice_player.is_bot
        assert alice_player.replaced_human_name == "Alice"
        assert table.host == "Bob"
        assert game.host == "Bob"
        assert Localization.get(
            bob.locale,
            "table-new-host-promoted",
            player="Bob",
        ) in bob.get_spoken_messages()
        assert Localization.get(
            bob.locale,
            "server-power-restore-complete-with-bots",
        ) in bob.get_spoken_messages()
    finally:
        server.db.close()
