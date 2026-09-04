from pathlib import Path

import pytest

from ..core import server as server_module
from ..core.server import ONLINE_USERS_SPOKEN_NAME_LIMIT, Server
from ..tables.manager import TableManager
from ..users.test_user import MockUser
from ..users.network_user import NetworkUser
from ..messages.localization import Localization

# Ensure games are registered for name lookups.
from .. import games  # noqa: F401


class DummyClient:
    def __init__(self, username: str):
        self.username = username


def _make_server() -> Server:
    Localization.init(Path(__file__).resolve().parents[1] / "locales")
    server = Server.__new__(Server)
    server._tables = TableManager()
    server._user_states = {}
    server._users = {}
    return server


def _menu_texts(user: MockUser, menu_id: str) -> list[str]:
    items = user.menus.get(menu_id, {}).get("items", [])
    texts: list[str] = []
    for item in items:
        texts.append(item.text if hasattr(item, "text") else item)
    return texts


def _menu_ids(user: MockUser, menu_id: str) -> list[str]:
    items = user.get_current_menu_items(menu_id) or []
    return [item.id for item in items]


@pytest.fixture
def social_server(tmp_path):
    server = Server(
        db_path=str(tmp_path / "online_social.db"),
        locales_dir=Path(__file__).resolve().parents[1] / "locales",
    )
    server._db.connect()
    for name in ("Alice", "Viewer", "Zara"):
        record = server._db.create_user(name, "hash", approved=True)
        server._users[name] = NetworkUser(
            name, "en", connection=None, uuid=record.uuid, approved=True,
        )
    try:
        yield server
    finally:
        server._db.close()


async def _select(server, viewer, item_id):
    await server._handle_menu(
        DummyClient(viewer.username),
        {
            "type": "menu",
            "menu_id": server._user_states[viewer.username]["menu"],
            "selection_id": item_id,
        },
    )


@pytest.mark.asyncio
async def test_online_account_actions_stay_open_when_target_disconnects(social_server, monkeypatch):
    server = social_server
    monkeypatch.setattr(server_module, "ONLINE_USERS_PAGE_SIZE", 2)
    viewer = server._users["Viewer"]
    server._show_main_menu(viewer)
    server._nav_push(viewer, server._show_online_users_menu, 2)
    await _select(server, viewer, "online_Zara")
    menu_id = server._user_states[viewer.username]["menu"]
    stack = list(server._user_states[viewer.username]["_stack"])
    viewer.get_queued_messages()

    server._users.pop("Zara")
    server.on_user_presence_changed()

    assert server._user_states[viewer.username]["menu"] == menu_id
    assert server._user_states[viewer.username]["_stack"] == stack
    assert viewer.get_queued_messages() == []
    await _select(server, viewer, "view_profile")
    assert server._user_states[viewer.username]["menu"] == "public_profile_menu"
    await _select(server, viewer, "back")
    assert server._user_states[viewer.username]["menu"] == menu_id
    await _select(server, viewer, "back")
    assert server._user_states[viewer.username]["menu"] == "online_users"
    assert server._user_states[viewer.username]["online_users_page"] == 1
    await _select(server, viewer, "back")
    assert server._user_states[viewer.username]["menu"] == "main_menu"


@pytest.mark.asyncio
async def test_online_account_actions_keep_identity_when_friendship_changes(social_server):
    server = social_server
    viewer = server._users["Viewer"]
    target = server._users["Zara"]
    server._show_main_menu(viewer)
    await server._handle_list_online_with_games(DummyClient(viewer.username))
    await _select(server, viewer, "online_Zara")
    menu_id = server._user_states[viewer.username]["menu"]
    viewer.get_queued_messages()
    server._db.send_friend_request(viewer.uuid, target.uuid)
    server._db.accept_friend_request(viewer.uuid, target.uuid)
    server.on_social_relationships_changed(viewer.uuid, target.uuid)
    assert server._user_states[viewer.username]["menu"] == menu_id
    packets = viewer.get_queued_messages()
    assert len(packets) == 1 and packets[0]["type"] == "menu"
    assert "selection_id" not in packets[0] and "position" not in packets[0]
    assert "send_pm" in [item["id"] for item in packets[0]["items"]]


@pytest.mark.asyncio
async def test_repeated_online_list_shortcut_preserves_page_and_stack(social_server, monkeypatch):
    server = social_server
    monkeypatch.setattr(server_module, "ONLINE_USERS_PAGE_SIZE", 2)
    viewer = server._users["Viewer"]
    server._show_main_menu(viewer)
    server._nav_push(viewer, server._show_online_users_menu, 2)
    stack = list(server._user_states[viewer.username]["_stack"])
    viewer.get_queued_messages()
    for _ in range(3):
        await server._handle_list_online_with_games(DummyClient(viewer.username))
    assert server._user_states[viewer.username]["online_users_page"] == 2
    assert server._user_states[viewer.username]["_stack"] == stack
    assert viewer.get_queued_messages() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["actions", "profile", "blocked"])
async def test_deleted_account_keeps_social_surface_and_back_stack(social_server, surface):
    server = social_server
    viewer = server._users["Viewer"]
    target = server._users["Zara"]
    server._show_main_menu(viewer)
    if surface == "blocked":
        server._db.block_user(viewer.uuid, target.uuid)
        server._nav_push(viewer, server._show_blocked_users_menu)
        await _select(server, viewer, "blocked_Zara")
        parent_menu = "blocked_users_menu"
    else:
        await server._handle_list_online_with_games(DummyClient(viewer.username))
        await _select(server, viewer, "online_Zara")
        parent_menu = "online_users"
        if surface == "profile":
            await _select(server, viewer, "view_profile")
            parent_menu = "friend_actions_menu"
    menu_id = server._user_states[viewer.username]["menu"]
    stack = list(server._user_states[viewer.username]["_stack"])
    viewer.get_queued_messages()

    assert await server._delete_account_and_evict("Zara", {"type": "disconnect"})

    assert server._user_states[viewer.username]["menu"] == menu_id
    assert server._user_states[viewer.username]["_stack"] == stack
    packets = viewer.get_queued_messages()
    assert len(packets) == 1 and packets[0]["type"] == "menu"
    assert [item["id"] for item in packets[0]["items"]] == ["account_unavailable", "back"]
    assert "position" not in packets[0] and "selection_id" not in packets[0]
    server.on_user_presence_changed()
    assert viewer.get_queued_messages() == []
    # A packet from the previous rendering cannot reopen an obsolete action.
    await _select(server, viewer, "view_profile")
    assert viewer.get_queued_messages() == []
    await _select(server, viewer, "back")
    assert server._user_states[viewer.username]["menu"] == parent_menu
    if surface == "profile":
        await _select(server, viewer, "back")
        assert server._user_states[viewer.username]["menu"] == "online_users"
    await _select(server, viewer, "back")
    assert server._user_states[viewer.username]["menu"] == "main_menu"


@pytest.mark.asyncio
async def test_account_deleted_before_pm_selection_cannot_open_input(social_server):
    server = social_server
    viewer = server._users["Viewer"]
    target = server._users["Zara"]
    server._db.send_friend_request(viewer.uuid, target.uuid)
    server._db.accept_friend_request(viewer.uuid, target.uuid)
    server._show_main_menu(viewer)
    server._nav_push(viewer, server._show_friend_actions_menu, "Zara")
    viewer.get_queued_messages()
    # Reproduce a queued selection arriving before the passive refresh.
    server._db.delete_user("Zara")

    await _select(server, viewer, "send_pm")

    assert server._user_states[viewer.username]["menu"] == "friend_actions_menu"
    assert not server._user_states[viewer.username].get("_transient")
    packets = viewer.get_queued_messages()
    assert [packet["type"] for packet in packets] == ["speak", "menu"]
    assert packets[0]["text"] == Localization.get(viewer.locale, "user-account-unavailable")
    await _select(server, viewer, "back")
    assert server._user_states[viewer.username]["menu"] == "main_menu"


@pytest.mark.asyncio
@pytest.mark.parametrize("disappearance", ["disconnect", "ban"])
async def test_stale_online_selection_refreshes_without_pushing(social_server, disappearance):
    server = social_server
    viewer = server._users["Viewer"]
    server._show_main_menu(viewer)
    await server._handle_list_online_with_games(DummyClient(viewer.username))
    stack = list(server._user_states[viewer.username]["_stack"])
    viewer.get_queued_messages()
    if disappearance == "disconnect":
        server._users.pop("Zara")
    else:
        server._user_states["Zara"] = {"menu": "banned_menu"}

    await _select(server, viewer, "online_Zara")

    assert server._user_states[viewer.username]["menu"] == "online_users"
    assert server._user_states[viewer.username]["_stack"] == stack
    packets = viewer.get_queued_messages()
    assert [packet["type"] for packet in packets] == ["speak", "menu"]
    assert "position" not in packets[1] and "selection_id" not in packets[1]
    assert "online_Zara" not in [item["id"] for item in packets[1]["items"]]


def test_online_list_localizes_only_the_visible_page(monkeypatch):
    server = _make_server()
    monkeypatch.setattr(server_module, "ONLINE_USERS_PAGE_SIZE", 2)
    viewer = MockUser("Viewer")
    server._users = {name: MockUser(name) for name in ("Alice", "Bob", "Carol", "Dan")}
    formatted = []
    monkeypatch.setattr(
        server, "_format_online_user_line",
        lambda user, name: formatted.append(name) or name,
    )

    items, page = server._get_online_users_menu_items(viewer, page=2)

    assert formatted == ["Carol", "Dan"]
    assert page.items == formatted and page.total == 4
    assert [item.id for item in items][1:3] == ["online_Carol", "online_Dan"]


@pytest.mark.asyncio
async def test_empty_online_list_is_read_only_and_has_consistent_pagination():
    server = _make_server()
    viewer = MockUser("Viewer")
    items, page = server._get_online_users_menu_items(viewer, page=3)
    assert page.items == [] and page.total == 0
    assert page.page == page.total_pages == 1
    assert [item.id for item in items] == ["back", "readonly_online_empty"]
    await server._handle_online_users_selection(viewer, items[1].id, {})
    assert viewer.messages == []


@pytest.mark.asyncio
async def test_list_online_users_speaks_sorted_list() -> None:
    server = _make_server()
    alice = MockUser("Alice")
    bob = MockUser("Bob")
    server._users = {"Bob": bob, "Alice": alice}

    client = DummyClient("Alice")
    await server._handle_list_online(client)

    assert alice.messages[-1].data == {
        "text": "2 users online. Alice and Bob.",
        "buffer": "system",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("en", "4 users online. 1 developer: Trung. 1 administrator: Rory. 2 users: Alice and Bob."),
        ("vi", "4 người dùng đang trực tuyến. 1 nhà phát triển: Trung. 1 quản trị viên: Rory. 2 người dùng: Alice và Bob."),
    ],
)
async def test_online_summary_groups_staff_before_regular_users(locale, expected) -> None:
    server = _make_server()
    for name, trust in (("Bob", 1), ("Rory", 2), ("Alice", 1), ("Trung", 3)):
        account = MockUser(name, locale=locale)
        account.trust_level = trust
        server._users[name] = account

    await server._handle_list_online(DummyClient("Alice"))

    assert [message.data["text"] for message in server._users["Alice"].messages] == [expected]


@pytest.mark.asyncio
@pytest.mark.parametrize("locale", ["en", "vi"])
@pytest.mark.parametrize("regular_count", [0, 1, ONLINE_USERS_SPOKEN_NAME_LIMIT - 1, ONLINE_USERS_SPOKEN_NAME_LIMIT, ONLINE_USERS_SPOKEN_NAME_LIMIT + 1, ONLINE_USERS_SPOKEN_NAME_LIMIT + 10])
async def test_online_summary_bounds_regular_names_only(locale, regular_count) -> None:
    server = _make_server()
    staff_names = [f"Staff{index:03d}" for index in range(ONLINE_USERS_SPOKEN_NAME_LIMIT + 1)]
    regular_names = [f"User{index:03d}" for index in range(regular_count)]
    for name in regular_names + staff_names:
        account = MockUser(name, locale=locale)
        account.trust_level = 3 if name in staff_names else 1
        server._users[name] = account
    viewer = server._users[staff_names[0]]

    await server._handle_list_online(DummyClient(viewer.username))

    text = viewer.get_last_spoken()
    assert text.startswith(str(len(staff_names) + regular_count))
    for name in staff_names + regular_names[:ONLINE_USERS_SPOKEN_NAME_LIMIT]:
        assert text.count(name) == 1
    for name in regular_names[ONLINE_USERS_SPOKEN_NAME_LIMIT:]:
        assert name not in text
    remainder = regular_count - ONLINE_USERS_SPOKEN_NAME_LIMIT
    if remainder > 0:
        assert text.endswith(Localization.get(locale, "online-users-more", count=remainder) + ".")
    else:
        assert "more" not in text
        assert "người khác" not in text
    assert "administrator" not in text
    assert "quản trị viên" not in text
    assert len(viewer.messages) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("locale", "trust", "expected"),
    [
        ("en", 1, "1 user online. Alice."),
        ("en", 2, "1 user online. 1 administrator: Alice."),
        ("en", 3, "1 user online. 1 developer: Alice."),
        ("vi", 1, "1 người dùng đang trực tuyến. Alice."),
        ("vi", 2, "1 người dùng đang trực tuyến. 1 quản trị viên: Alice."),
        ("vi", 3, "1 người dùng đang trực tuyến. 1 nhà phát triển: Alice."),
    ],
)
async def test_online_summary_single_account_omits_empty_groups(locale, trust, expected) -> None:
    server = _make_server()
    viewer = MockUser("Alice", locale=locale)
    viewer.trust_level = trust
    server._users[viewer.username] = viewer
    await server._handle_list_online(DummyClient(viewer.username))
    assert viewer.get_last_spoken() == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("locale", ["en", "vi"])
async def test_online_summary_excludes_banned_users_and_handles_empty_snapshot(locale) -> None:
    server = _make_server()
    viewer = MockUser("Viewer", locale=locale)
    hidden = MockUser("Hidden")
    hidden.trust_level = 3
    server._users = {viewer.username: viewer, hidden.username: hidden}
    server._user_states[hidden.username] = {"menu": "banned_menu"}
    await server._handle_list_online(DummyClient(viewer.username))
    assert "Hidden" not in viewer.get_last_spoken()
    assert viewer.get_last_spoken().startswith("1 ")
    server._user_states[viewer.username] = {"menu": "banned_menu"}
    await server._handle_list_online(DummyClient(viewer.username))
    assert viewer.get_last_spoken() == Localization.get(locale, "online-users-none")
    assert server._get_online_usernames() == []


@pytest.mark.asyncio
async def test_read_online_users_does_not_replace_active_input() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    server._users[viewer.username] = viewer
    server._show_online_users_menu(viewer)
    server._enter_input_state(viewer, "send_pm_input", target_username="Alice")
    state = server._user_states[viewer.username].copy()
    viewer.messages.clear()

    await server._handle_list_online(DummyClient(viewer.username))
    server.on_user_presence_changed()

    assert server._user_states[viewer.username] == state
    assert [message.type for message in viewer.messages] == ["speak"]


def test_online_list_role_order_uses_canonical_names_and_highest_role() -> None:
    server = _make_server()
    for name, trust in (("alice", 1), ("zoe", 3), ("Amy", 3), ("bob", 2), ("Alice", 2), ("Beyond", 4), ("Basic", 0)):
        account = MockUser(name)
        account.trust_level = trust
        server._users[name] = account
    assert server._get_online_usernames() == ["Amy", "Beyond", "zoe", "Alice", "bob", "alice", "Basic"]


def test_online_refresh_reorders_silently_and_skips_identical_packets() -> None:
    server = _make_server()
    viewer = NetworkUser("Viewer", "en", connection=None, approved=True)
    alice = MockUser("Alice")
    zara = MockUser("Zara")
    server._users = {"Viewer": viewer, "Alice": alice, "Zara": zara}
    server._user_states[viewer.username] = {"menu": "main_menu"}
    server._nav_push(viewer, server._show_online_users_menu, focus_page_start=True)
    stack = list(server._user_states[viewer.username]["_stack"])
    viewer.get_queued_messages()

    zara.trust_level = 2
    server.on_user_presence_changed()

    packets = viewer.get_queued_messages()
    assert len(packets) == 1
    packet = packets[0]
    assert packet["type"] == "menu"
    assert packet["menu_id"] == "online_users"
    assert [item["id"] for item in packet["items"]] == ["back", "online_Zara", "online_Alice", "readonly_online_Viewer"]
    assert "Administrator" in packet["items"][1]["text"]
    assert "selection_id" not in packet
    assert "position" not in packet
    assert server._user_states[viewer.username]["_stack"] == stack
    server.on_user_presence_changed()
    assert viewer.get_queued_messages() == []


def test_online_refresh_clamps_disappearing_page_without_focus_jump(monkeypatch) -> None:
    monkeypatch.setattr(server_module, "ONLINE_USERS_PAGE_SIZE", 2)
    server = _make_server()
    viewer = MockUser("Viewer")
    server._users = {"Viewer": viewer, "Alice": MockUser("Alice"), "Zara": MockUser("Zara")}
    server._show_online_users_menu(viewer, page=2)
    server._users.pop("Alice")
    server._users["Zara"].trust_level = 3
    server.on_user_presence_changed()
    assert server._user_states[viewer.username]["online_users_page"] == 1
    assert _menu_ids(viewer, "online_users") == ["back", "online_Zara", "readonly_online_Viewer"]
    assert viewer.menus["online_users"]["position"] is None


@pytest.mark.asyncio
async def test_promotion_and_demotion_refresh_open_online_list(tmp_path) -> None:
    server = Server(
        db_path=str(tmp_path / "online_roles.db"),
        locales_dir=Path(__file__).resolve().parents[1] / "locales",
    )
    server._db.connect()
    try:
        accounts = {}
        for name, trust in (("Developer", 3), ("Viewer", 1), ("Zara", 1)):
            record = server._db.create_user(name, "hash", trust_level=trust, approved=True)
            account = NetworkUser(
                name, "en", connection=None, uuid=record.uuid,
                trust_level=trust, approved=True,
            )
            accounts[name] = account
            server._users[name] = account
        viewer = accounts["Viewer"]
        server._show_main_menu(viewer)
        server._nav_push(viewer, server._show_online_users_menu)
        stack = list(server._user_states[viewer.username]["_stack"])
        viewer.get_queued_messages()

        for change, expected_ids, expected_role in (
            (server.admin_manager._promote_to_admin, ["back", "online_Developer", "online_Zara", "readonly_online_Viewer"], "Administrator"),
            (server.admin_manager._demote_from_admin, ["back", "online_Developer", "readonly_online_Viewer", "online_Zara"], "User"),
        ):
            await change(accounts["Developer"], "Zara", "nobody")
            packets = viewer.get_queued_messages()
            assert len(packets) == 1
            assert packets[0]["type"] == "menu"
            assert [item["id"] for item in packets[0]["items"]] == expected_ids
            assert any(item["text"].startswith(f"Zara ({expected_role},") for item in packets[0]["items"])
            assert "position" not in packets[0]
            assert "selection_id" not in packets[0]
            assert server._user_states[viewer.username]["_stack"] == stack
            server.on_user_presence_changed()
            assert viewer.get_queued_messages() == []
        await server._handle_online_users_selection(viewer, "back", server._user_states[viewer.username])
        assert server._user_states[viewer.username]["menu"] == "main_menu"
    finally:
        server._db.close()


def test_online_users_menu_formats_game_names() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    bob = MockUser("Bob")
    alice = MockUser("Alice")
    carol = MockUser("Carol")
    server._users = {"Viewer": viewer, "Bob": bob, "Alice": alice, "Carol": carol}

    table = server._tables.create_table("crazyeights", "Bob", bob)
    table.add_member("Carol", carol, as_spectator=True)

    server._show_online_users_menu(viewer)

    texts = _menu_texts(viewer, "online_users")
    assert "Bob (User, Desktop, English): Waiting at Crazy Eights table" in texts
    assert "Carol (User, Desktop, English): Watching Crazy Eights table" in texts
    assert "Alice (User, Desktop, English): Main menu" in texts


def test_online_users_menu_renders_current_user_as_read_only() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    alice = MockUser("Alice")
    server._users = {"Viewer": viewer, "Alice": alice}

    server._show_online_users_menu(viewer)

    items = viewer.get_current_menu_items("online_users") or []
    own_item = next(item for item in items if item.text.startswith("Viewer "))
    assert own_item.id == "readonly_online_Viewer"


@pytest.mark.asyncio
async def test_online_users_menu_initial_open_focuses_first_player() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    alice = MockUser("Alice")
    server._users = {"Viewer": viewer, "Alice": alice}

    await server._handle_list_online_with_games(DummyClient("Viewer"))

    ids = _menu_ids(viewer, "online_users")
    assert ids[1] == "online_Alice"
    assert viewer.menus["online_users"]["position"] == 2


def test_client_platform_sanitizer_bounds_untrusted_display_text() -> None:
    sanitized = Server._sanitize_client_platform("<Windows>\n<script>AMD64</script>" * 3)
    assert sanitized.startswith("Windows scriptAMD64/script")
    assert "<" not in sanitized
    assert ">" not in sanitized
    assert "\n" not in sanitized
    assert len(sanitized) == 40


def test_online_users_menu_includes_first_party_client_platforms() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    desktop = MockUser("DesktopPlayer")
    web = MockUser("WebPlayer")
    mobile = MockUser("MobilePlayer")

    desktop.client_type = "python"
    desktop.client_platform = "Windows 11 AMD64"
    web.client_type = "web"
    web.client_platform = "Windows"
    mobile.client_type = "mobile"
    mobile.client_platform = "Android 16 (API 36)"
    server._users = {
        "Viewer": viewer,
        "DesktopPlayer": desktop,
        "WebPlayer": web,
        "MobilePlayer": mobile,
    }

    server._show_online_users_menu(viewer)

    texts = _menu_texts(viewer, "online_users")
    assert "DesktopPlayer (User, Desktop (Windows 11 AMD64), English): Main menu" in texts
    assert "WebPlayer (User, Web (Windows), English): Main menu" in texts
    assert "MobilePlayer (User, Mobile (Android 16 (API 36)), English): Main menu" in texts


@pytest.mark.asyncio
async def test_online_users_menu_pages_large_lists() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    server._users = {"Viewer": viewer}
    for index in range(101):
        username = f"User{index:03d}"
        server._users[username] = MockUser(username)

    server._show_online_users_menu(viewer)

    ids = _menu_ids(viewer, "online_users")
    assert len([item_id for item_id in ids if item_id.startswith("online_")]) == 100
    assert "online_User100" not in ids
    assert "refresh" not in ids
    assert "page_next" in ids
    assert "page_last" in ids

    await server._handle_online_users_selection(
        viewer,
        "page_next",
        server._user_states[viewer.username],
    )

    second_page_ids = _menu_ids(viewer, "online_users")
    assert server._user_states[viewer.username]["online_users_page"] == 2
    assert "online_User100" in second_page_ids
    assert "page_previous" in second_page_ids
    assert "page_next" not in second_page_ids
    assert viewer.menus["online_users"]["position"] == 2


def test_online_users_menu_hides_page_navigation_for_single_page() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    alice = MockUser("Alice")
    server._users = {"Viewer": viewer, "Alice": alice}

    server._show_online_users_menu(viewer)

    ids = _menu_ids(viewer, "online_users")
    assert "refresh" not in ids
    assert "page_summary" not in ids
    assert "page_first" not in ids
    assert "page_previous" not in ids
    assert "page_next" not in ids
    assert "page_last" not in ids


@pytest.mark.asyncio
async def test_online_users_refresh_preserves_focus_and_speaks_confirmation() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    server._users = {"Viewer": viewer}

    server._show_online_users_menu(viewer)
    await server._handle_online_users_selection(
        viewer,
        "refresh",
        server._user_states[viewer.username],
    )

    ids = _menu_ids(viewer, "online_users")
    assert ids == ["back", "readonly_online_Viewer"]
    assert viewer.menus["online_users"]["position"] is None
    assert viewer.get_last_spoken() == "List refreshed."


@pytest.mark.asyncio
async def test_online_users_escape_survives_repeated_presence_refreshes(tmp_path) -> None:
    server = Server(
        db_path=str(tmp_path / "playaural.db"),
        locales_dir=Path(__file__).resolve().parents[1] / "locales",
    )
    viewer = MockUser("Viewer")
    alice = MockUser("Alice")
    server._users = {"Viewer": viewer, "Alice": alice}
    try:
        server._show_main_menu(viewer)
        server._nav_push(viewer, server._show_online_users_menu)

        for _ in range(3):
            server.on_user_presence_changed()

        state = server._user_states[viewer.username]
        assert state["menu"] == "online_users"
        assert state.get("_stack")
        assert viewer.menus["online_users"]["escape_behavior"].value == "escape_event"

        await server._handle_online_users_selection(viewer, "back", state)

        assert server._user_states[viewer.username]["menu"] == "main_menu"
    finally:
        server._db.close()


def test_online_users_menu_distinguishes_playing_and_spectating() -> None:
    server = _make_server()
    viewer = MockUser("Viewer")
    bob = MockUser("Bob")
    alice = MockUser("Alice")
    server._users = {"Viewer": viewer, "Bob": bob, "Alice": alice}

    table = server._tables.create_table("crazyeights", "Bob", bob)
    table.add_member("Alice", alice, as_spectator=True)
    table.status = "playing"

    server._show_online_users_menu(viewer)

    texts = _menu_texts(viewer, "online_users")
    assert "Bob (User, Desktop, English): Playing Crazy Eights" in texts
    assert "Alice (User, Desktop, English): Spectating Crazy Eights" in texts

