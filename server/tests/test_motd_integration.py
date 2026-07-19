import pytest
from unittest.mock import MagicMock, AsyncMock

from server.core.server import Server
from server.auth.auth import AuthManager
from server.users.network_user import NetworkUser

@pytest.fixture
def mock_server(tmp_path):
    # Initialize basic server
    server = Server(db_path=tmp_path / "test_db.sqlite")
    server._db.connect()
    server._auth = AuthManager(server._db)

    # Init user
    server._db.create_user("admin_user", "hash", "en", 2, True)

    user = NetworkUser("admin_user", "en", MagicMock(), trust_level=2, approved=True)
    user.connection.send = AsyncMock()
    user.connection.username = "admin_user"
    server._users["admin_user"] = user

    yield server, user

    # Teardown
    server._db.close()

@pytest.mark.asyncio
async def test_motd_admin_flow(mock_server):
    server, user = mock_server

    # 1. Admin clicks Manage MOTD in admin_menu
    server._user_states["admin_user"] = {"menu": "admin_menu"}
    await server._handle_menu(user.connection, {"selection_id": "manage_motd"})

    # Verify we are now in manage_motd_menu
    assert server._user_states["admin_user"]["menu"] == "manage_motd_menu"

    # 2. Admin clicks Create/Update MOTD
    await server._handle_menu(user.connection, {"selection_id": "create_update"})

    assert server._user_states["admin_user"]["menu"] == "admin_localized_text_menu"
    assert server._user_states["admin_user"]["localized_text_context"] == {
        "version": 1
    }

    # Invalid version input returns to the editor without losing the draft.
    await server._handle_menu(
        user.connection, {"selection_id": "localized_text_version"}
    )
    await server._handle_editbox(user.connection, {
        "input_id": "admin_localized_text_input",
        "text": "abc"
    })

    assert server._user_states["admin_user"]["menu"] == "admin_localized_text_menu"
    assert server._user_states["admin_user"]["localized_text_context"]["version"] == 1

    await server._handle_menu(
        user.connection, {"selection_id": "localized_text_version"}
    )
    await server._handle_editbox(user.connection, {
        "input_id": "admin_localized_text_input",
        "text": "2"
    })

    # Official languages are edited in any order; the community locale is skipped.
    for language in ("vi", "en"):
        await server._handle_menu(
            user.connection,
            {"selection_id": f"localized_text_locale_{language}"},
        )
        await server._handle_editbox(
            user.connection,
            {
                "input_id": "admin_localized_text_input",
                "text": f"Message for {language}",
            },
        )

    await server._handle_menu(
        user.connection, {"selection_id": "localized_text_submit"}
    )

    # Verify MOTD is created and we are back to manage_motd_menu
    assert server._user_states["admin_user"]["menu"] == "manage_motd_menu"

    # Check DB
    version = server._db.get_highest_motd_version()
    assert version == 2
    assert server._db.get_motd(version, "en") == "Message for en"
    assert server._db.get_motd(version, "vi") == "Message for vi"
    assert server._db.get_motd(version, "fa") == "Message for en"

    # 5. Admin clicks View
    await server._handle_menu(user.connection, {"selection_id": "view"})
    assert server._user_states["admin_user"]["menu"] == "view_motd_menu"
    motd_items = user._current_menus["view_motd_menu"]["items"]
    assert all(item.get("id") == "" for item in motd_items[:-1])
    assert motd_items[-1].get("id") == "back"

    # Admin clicks back from view
    await server._handle_menu(user.connection, {"selection_id": "back"})
    assert server._user_states["admin_user"]["menu"] == "manage_motd_menu"

    # 6. Admin clicks Delete
    await server._handle_menu(user.connection, {"selection_id": "delete"})
    assert server._user_states["admin_user"]["menu"] == "manage_motd_menu"
    assert server._db.get_highest_motd_version() == 0

    # 7. Admin clicks Delete again (empty delete check)
    user.speak_l = MagicMock()
    await server._handle_menu(user.connection, {"selection_id": "delete"})
    user.speak_l.assert_called_with("motd-delete-empty", buffer="system")

@pytest.mark.asyncio
async def test_motd_login_interception(mock_server):
    server, user = mock_server

    # Setup MOTD with a rollback version (e.g. version 2, while user is on 5)
    server._db.create_motd(2, {"en": "Line 1\nLine 2", "vi": "Dong 1\nDong 2"})

    # Setup test user for login, simulate they have seen version 5
    user_record = server._db.create_user("test_user", "hash", "en", 1, True, email="test@test.com")
    server._db.update_user_motd_version("test_user", 5)

    # Since we bypass network auth for tests, let's call _handle_authorize logic manually
    client = MagicMock()
    client.username = "test_user"
    client.ip_address = "127.0.0.1"
    client.authenticated = True
    client.send = AsyncMock()
    client.close = AsyncMock()

    from server.core.server import LATEST_CLIENT_VERSION
    # Call auth handle
    packet = {
        "username": "test_user",
        "password": "hash",
        "client": "python",
        "version": LATEST_CLIENT_VERSION
    }

    # Mock auth check
    server._auth.authenticate = MagicMock(return_value=True)
    server._ws_server = MagicMock()
    server._ws_server.get_client_by_username = MagicMock(return_value=None)
    server._rate_limiter = MagicMock()
    server._rate_limiter.is_login_allowed = MagicMock(return_value=True)
    server._rate_limiter.clear_failed_logins = MagicMock()

    # We must explicitly add the new user object manually just like authorize success does internally
    # since we mocked out get_client_by_username etc, but the authorize method initializes the NetworkUser
    # However we'll just let _handle_authorize run which adds them to _users dictionary

    await server._handle_authorize(client, packet)

    # Verify user was intercepted and shown MOTD menu because 2 != 5
    assert server._user_states["test_user"]["menu"] == "motd_menu"
    assert server._user_states["test_user"]["motd_version"] == 2
    test_network_user = server._users["test_user"]
    motd_items = test_network_user._current_menus["motd_menu"]["items"]
    assert all(item.get("id") == "" for item in motd_items[:-1])
    assert motd_items[-1].get("id") == "ok"

    # Simulate clicking OK
    await server._handle_menu(test_network_user.connection, {"selection_id": "ok"})

    # Verify user is sent to main menu and DB is updated to 2
    assert server._user_states["test_user"]["menu"] == "main_menu"

    # Check DB update
    record = server._db.get_user("test_user")
    assert record.motd_version == 2

@pytest.mark.asyncio
async def test_motd_reconnect_game_state(mock_server):
    server, user = mock_server

    # 1. Setup user in an active game
    server._db.create_user("gamer", "hash", "en", 1, True, email="test@test.com")

    # Create network user
    client = MagicMock()
    client.username = "gamer"
    client.ip_address = "127.0.0.1"
    client.authenticated = True
    client.send = AsyncMock()
    client.close = AsyncMock()

    gamer_user = NetworkUser("gamer", "en", client)
    gamer_user._uuid = server._db.get_user("gamer").uuid # ensure uuid matches DB
    server._users["gamer"] = gamer_user

    # Put user in a table
    table = server._tables.create_table("holdem", "gamer", gamer_user)

    # Need a mock game
    mock_game = MagicMock()
    mock_game.status = "playing"
    mock_game.players = [MagicMock(id=gamer_user.uuid, name="gamer", is_bot=False)]
    mock_game._users = {gamer_user.uuid: gamer_user}

    # This matches the signature game.get_player_by_id(uuid)
    def mock_get_player_by_id(pid):
        for p in mock_game.players:
            if p.id == pid:
                return p
        return None

    mock_game.get_player_by_id = mock_get_player_by_id

    table.game = mock_game

    # 2. Simulate disconnect
    await server._on_client_disconnect(client)
    # Disconnect removes the user from self._users and self._user_states, but table logic usually replaces with bot
    mock_game.players[0].is_bot = True

    # 3. Admin creates MOTD
    server._db.create_motd(1, {"en": "New MOTD"})

    # 4. User reconnects
    new_client = MagicMock()
    new_client.username = "gamer"
    new_client.ip_address = "127.0.0.1"
    new_client.authenticated = True
    new_client.send = AsyncMock()

    from server.core.server import LATEST_CLIENT_VERSION
    packet = {
        "username": "gamer",
        "password": "hash",
        "client": "python",
        "version": LATEST_CLIENT_VERSION
    }

    server._auth.authenticate = MagicMock(return_value=True)
    server._ws_server = MagicMock()
    server._ws_server.get_client_by_username = MagicMock(return_value=None)

    server._rate_limiter = MagicMock()
    server._rate_limiter.is_login_allowed = MagicMock(return_value=True)
    server._rate_limiter.clear_failed_logins = MagicMock()

    # Handle authorize -> Should trigger MOTD menu
    await server._handle_authorize(new_client, packet)

    # Verify trapped in MOTD menu
    assert server._user_states["gamer"]["menu"] == "motd_menu"
    assert server._user_states["gamer"]["motd_version"] == 1

    # 5. User clicks OK
    new_gamer_user = server._users["gamer"]

    # Mock game handle event to assert it doesn't get called (the fix)
    mock_game.handle_event = MagicMock()

    await server._handle_menu(new_client, {"selection_id": "ok"})

    # 6. Verify game restored and NOT sent to main menu
    assert server._user_states["gamer"]["menu"] == "in_game"
    assert server._user_states["gamer"]["table_id"] == table.table_id
    assert mock_game.players[0].is_bot == False

    # Also verify that the MOTD selection didn't accidentally leak to the game handle_event
    mock_game.handle_event.assert_not_called()
