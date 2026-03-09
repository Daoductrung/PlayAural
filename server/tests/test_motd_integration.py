import pytest
from unittest.mock import MagicMock, AsyncMock

from server.core.server import Server
from server.auth.auth import AuthManager
from server.users.network_user import NetworkUser
from server.messages.localization import Localization
from server.persistence.database import Database

@pytest.fixture
def mock_server(tmp_path):
    # Initialize basic server
    server = Server(db_path=tmp_path / "test_db.sqlite")
    server._db.connect()
    server._auth = AuthManager(server._db)

    # Mock localization for tests
    Localization._locales_dir = None
    Localization._bundles = {}

    # Let's mock Localization.get_available_languages directly
    orig_get_available = Localization.get_available_languages
    Localization.get_available_languages = MagicMock(return_value={"en": "English", "vi": "Vietnamese"})

    # Init user
    server._db.create_user("admin_user", "hash", "en", 2, True)

    user = NetworkUser("admin_user", "en", MagicMock(), trust_level=2, approved=True)
    user.connection.send = AsyncMock()
    user.connection.username = "admin_user"
    server._users["admin_user"] = user

    yield server, user

    # Teardown
    Localization.get_available_languages = orig_get_available
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

    # Verify we are prompted for the first language (en or vi depending on dict order, mocked as en, vi)
    assert server._user_states["admin_user"]["menu"] == "admin_motd_input"
    assert "pending_languages" in server._user_states["admin_user"]
    # Which language? Check the keys from mock
    pending = server._user_states["admin_user"]["pending_languages"]
    first_lang = pending[0] if pending else "en"

    # 3. Simulate input for the first language via editbox
    await server._handle_editbox(user.connection, {
        "input_id": f"motd_message_{first_lang}",
        "text": f"Message for {first_lang}"
    })

    # Verify we are prompted for the next language
    assert server._user_states["admin_user"]["menu"] == "admin_motd_input"
    pending = server._user_states["admin_user"]["pending_languages"]
    assert len(pending) == 1
    second_lang = pending[0]

    # 4. Simulate input for the second language via editbox
    await server._handle_editbox(user.connection, {
        "input_id": f"motd_message_{second_lang}",
        "text": f"Message for {second_lang}"
    })

    # Verify MOTD is created and we are back to manage_motd_menu
    assert server._user_states["admin_user"]["menu"] == "manage_motd_menu"

    # Check DB
    version = server._db.get_highest_motd_version()
    assert version == 1
    assert server._db.get_motd(version, first_lang) == f"Message for {first_lang}"

    # 5. Admin clicks View
    await server._handle_menu(user.connection, {"selection_id": "view"})
    assert server._user_states["admin_user"]["menu"] == "view_motd_menu"

    # Admin clicks back from view
    await server._handle_menu(user.connection, {"selection_id": "back"})
    assert server._user_states["admin_user"]["menu"] == "manage_motd_menu"

    # 6. Admin clicks Delete
    await server._handle_menu(user.connection, {"selection_id": "delete"})
    assert server._user_states["admin_user"]["menu"] == "manage_motd_menu"
    assert server._db.get_highest_motd_version() == 0

@pytest.mark.asyncio
async def test_motd_login_interception(mock_server):
    server, user = mock_server

    # Setup MOTD
    server._db.create_motd({"en": "Line 1\nLine 2", "vi": "Dong 1\nDong 2"})

    # Setup test user for login
    server._db.create_user("test_user", "hash", "en", 1, True)

    # Since we bypass network auth for tests, let's call _handle_authorize logic manually
    client = MagicMock()
    client.username = "test_user"
    client.authenticated = True
    client.send = AsyncMock()
    client.close = AsyncMock()

    # Call auth handle
    packet = {
        "username": "test_user",
        "password": "hash",
        "client": "python",
        "version": "0.1.6"
    }

    # Mock auth check
    server._auth.authenticate = MagicMock(return_value=True)
    server._ws_server = MagicMock()
    server._ws_server.get_client_by_username = MagicMock(return_value=None)

    await server._handle_authorize(client, packet)

    # Verify user was intercepted and shown MOTD menu
    assert server._user_states["test_user"]["menu"] == "motd_menu"
    assert server._user_states["test_user"]["motd_version"] == 1

    # Simulate clicking OK
    test_network_user = server._users["test_user"]
    await server._handle_menu(test_network_user.connection, {"selection_id": "ok"})

    # Verify user is sent to main menu and DB is updated
    assert server._user_states["test_user"]["menu"] == "main_menu"

    # Check DB update
    record = server._db.get_user("test_user")
    assert record.motd_version == 1
