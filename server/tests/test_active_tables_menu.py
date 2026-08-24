from pathlib import Path

from ..core.server import Server
from ..users.test_user import MockUser
from ..messages.localization import Localization

# Ensure games are registered for name lookups.
from .. import games  # noqa: F401


def _menu_texts(user: MockUser, menu_id: str) -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    texts: list[str] = []
    for item in items:
        texts.append(item.text if hasattr(item, "text") else item)
    return texts


def _menu_ids(user: MockUser, menu_id: str) -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    return [item.id for item in items]


def _make_server() -> Server:
    return Server(
        db_path=":memory:",
        locales_dir=Path(__file__).resolve().parents[1] / "locales",
    )


def test_active_tables_menu_lists_members_without_host() -> None:
    server = _make_server()
    host = MockUser("Bob")
    sue = MockUser("Sue")
    jim = MockUser("Jim")
    viewer = MockUser("Alice")
    server._users = {"Bob": host, "Sue": sue, "Jim": jim, "Alice": viewer}
    table = server._tables.create_table("pig", "Bob", host)
    table.add_member("Sue", sue, as_spectator=False)
    table.add_member("Jim", jim, as_spectator=True)

    from ..games.pig.game import PigGame
    table.game = PigGame()

    server._show_active_tables_menu(viewer)

    texts = _menu_texts(viewer, "active_tables_menu")
    expected = (
        "Pig [Waiting]: Bob's table. 2 players: Bob and Sue; "
        "Spectator: Jim."
    )
    assert expected in texts

    vi_viewer = MockUser("VietnameseViewer", locale="vi")
    server._users[vi_viewer.username] = vi_viewer
    server._show_active_tables_menu(vi_viewer)
    vi_texts = _menu_texts(vi_viewer, "active_tables_menu")
    vi_expected = (
        "Pig [Đang chờ]: Bàn của Bob. 2 người chơi: Bob và Sue; "
        "Khán giả: Jim."
    )
    assert vi_expected in vi_texts


def test_active_tables_menu_singular_player_format() -> None:
    server = _make_server()
    host = MockUser("Kate")
    viewer = MockUser("Alice")
    server._users = {"Kate": host, "Alice": viewer}
    table = server._tables.create_table("farkle", "Kate", host)

    from ..games.farkle.game import FarkleGame
    table.game = FarkleGame()

    server._show_active_tables_menu(viewer)

    texts = _menu_texts(viewer, "active_tables_menu")
    expected = "Farkle [Waiting]: Kate's table. 1 player: Kate."
    assert expected in texts


def test_active_tables_menu_separates_players_bots_and_spectators() -> None:
    server = _make_server()
    host = MockUser("n3x")
    viewer = MockUser("Alice")
    spectators = [MockUser(f"Watcher{index}") for index in range(1, 5)]
    server._users = {
        host.username: host,
        viewer.username: viewer,
        **{spectator.username: spectator for spectator in spectators},
    }
    table = server._tables.create_table("pig", host.username, host)

    from ..games.pig.game import PigGame
    from ..users.bot import Bot

    game = PigGame()
    table.game = game
    game._table = table
    game.initialize_lobby(host.username, host)
    bot = Bot("Botty")
    game.add_player(bot.username, bot)
    for spectator in spectators:
        table.add_member(spectator.username, spectator, as_spectator=True)
        game.add_spectator(spectator.username, spectator)

    server._show_active_tables_menu(viewer)

    texts = _menu_texts(viewer, "active_tables_menu")
    expected = (
        "Pig [Waiting]: n3x's table. 1 player: n3x; "
        "1 bot; Spectators: Watcher1, Watcher2, and Watcher3; plus 1 more."
    )
    assert expected in texts
    listing = next(text for text in texts if text.startswith("Pig [Waiting]"))
    assert "Botty" not in listing
    assert "Watcher4" not in listing

    vi_viewer = MockUser("VietnameseViewer", locale="vi")
    server._users[vi_viewer.username] = vi_viewer
    server._show_active_tables_menu(vi_viewer)
    vi_expected = (
        "Pig [Đang chờ]: Bàn của n3x. 1 người chơi: n3x; "
        "1 bot; Khán giả: Watcher1, Watcher2 và Watcher3; cùng 1 người khác."
    )
    assert vi_expected in _menu_texts(vi_viewer, "active_tables_menu")


def test_active_tables_menu_identifies_spectating_host_in_bounded_preview() -> None:
    server = _make_server()
    host = MockUser("Host")
    player = MockUser("Player")
    spectators = [MockUser(f"Watcher{index}") for index in range(1, 5)]
    viewer = MockUser("Viewer")
    server._users = {
        user.username: user
        for user in [host, player, *spectators, viewer]
    }
    table = server._tables.create_table("pig", host.username, host)
    table.members[0].is_spectator = True
    table.add_member(player.username, player)
    for spectator in spectators:
        table.add_member(spectator.username, spectator, as_spectator=True)

    from ..games.pig.game import PigGame

    table.game = PigGame()
    server._show_active_tables_menu(viewer)

    texts = _menu_texts(viewer, "active_tables_menu")
    expected = (
        "Pig [Waiting]: Host's table. 1 player: Player; "
        "Spectators: Host (host), Watcher1, and Watcher2; plus 2 more."
    )
    assert expected in texts


def test_active_tables_menu_counts_replacement_without_exposing_bot_name(
    monkeypatch,
) -> None:
    server = _make_server()
    host = MockUser("Host")
    guest = MockUser("Guest")
    viewer = MockUser("Viewer")
    server._users = {
        host.username: host,
        guest.username: guest,
        viewer.username: viewer,
    }
    table = server._tables.create_table("pig", host.username, host)

    from ..games.pig.game import PigGame

    game = PigGame()
    table.game = game
    game._table = table
    game.initialize_lobby(host.username, host)
    table.add_member(guest.username, guest)
    game.add_player(guest.username, guest)
    game.on_start()
    monkeypatch.setattr(
        game,
        "_generate_available_bot_name",
        lambda _existing_names: "Substitute",
    )
    game.on_player_disconnect(guest.uuid)
    server._users.pop(guest.username)

    server._show_active_tables_menu(viewer)

    texts = _menu_texts(viewer, "active_tables_menu")
    expected = "Pig [Playing]: Host's table. 1 player: Host; 1 bot."
    assert expected in texts
    listing = next(text for text in texts if text.startswith("Pig [Playing]"))
    replacement = game.get_player_by_id(guest.uuid)
    assert replacement is not None
    assert guest.username not in listing
    assert replacement.name not in listing


def test_main_menu_includes_active_tables_option() -> None:
    server = _make_server()
    viewer = MockUser("Alice")
    server._show_main_menu(viewer)

    texts = _menu_texts(viewer, "main_menu")
    expected = Localization.get(viewer.locale, "view-active-tables")
    assert expected in texts


def test_table_lists_page_large_results() -> None:
    server = _make_server()
    viewer = MockUser("Alice")
    server._users = {"Alice": viewer}

    from ..games.pig.game import PigGame

    last_table_id = ""
    for index in range(101):
        username = f"Host{index:03d}"
        host = MockUser(username)
        server._users[username] = host
        table = server._tables.create_table("pig", username, host)
        table.game = PigGame()
        last_table_id = table.table_id

    server._show_tables_menu(viewer, "pig")
    table_ids = _menu_ids(viewer, "tables_menu")
    assert len([item_id for item_id in table_ids if item_id.startswith("table_")]) == 100
    assert f"table_{last_table_id}" not in table_ids
    assert "refresh" not in table_ids
    assert "page_next" in table_ids

    __import__("asyncio").run(
        server._handle_tables_selection(
            viewer,
            "page_last",
            server._user_states[viewer.username],
        )
    )
    last_page_ids = _menu_ids(viewer, "tables_menu")
    assert server._user_states[viewer.username]["tables_page"] == 2
    assert f"table_{last_table_id}" in last_page_ids
    assert "page_previous" in last_page_ids
    assert "page_next" not in last_page_ids

    server._show_active_tables_menu(viewer)
    active_ids = _menu_ids(viewer, "active_tables_menu")
    assert len([item_id for item_id in active_ids if item_id.startswith("table_")]) == 100
    assert f"table_{last_table_id}" not in active_ids
    assert "refresh" not in active_ids
    assert "page_next" in active_ids

    __import__("asyncio").run(
        server._handle_active_tables_selection(
            viewer,
            "page_last",
            server._user_states[viewer.username],
        )
    )
    active_last_page_ids = _menu_ids(viewer, "active_tables_menu")
    assert server._user_states[viewer.username]["active_tables_page"] == 2
    assert f"table_{last_table_id}" in active_last_page_ids
    assert "page_previous" in active_last_page_ids
    assert "page_next" not in active_last_page_ids

