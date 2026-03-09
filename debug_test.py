import pytest
from unittest.mock import MagicMock, AsyncMock

from server.core.server import Server
from server.auth.auth import AuthManager
from server.users.network_user import NetworkUser
from server.messages.localization import Localization
from server.persistence.database import Database

@pytest.fixture
def mock_server(tmp_path):
    server = Server(db_path=tmp_path / "test_db.sqlite")
    server._db.connect()
    server._auth = AuthManager(server._db)

    Localization._locales_dir = None
    Localization._bundles = {}
    Localization.get_available_languages = MagicMock(return_value={"en": "English", "vi": "Vietnamese"})

    server._db.create_user("admin_user", "hash", "en", 2, True)
    user = NetworkUser("admin_user", "en", MagicMock(), trust_level=2, approved=True)
    user.connection.send = AsyncMock()
    user.connection.username = "admin_user"
    server._users["admin_user"] = user

    yield server, user
    server._db.close()

@pytest.mark.asyncio
async def test_debug(mock_server):
    server, user = mock_server

    server._db.create_user("gamer", "hash", "en", 1, True)

    client = MagicMock()
    client.username = "gamer"
    client.authenticated = True
    client.send = AsyncMock()

    gamer_user = NetworkUser("gamer", "en", client)
    gamer_user._uuid = server._db.get_user("gamer").uuid # ensure uuid matches DB
    server._users["gamer"] = gamer_user

    table = server._tables.create_table("holdem", "gamer", gamer_user)

    mock_game = MagicMock()
    mock_game.status = "playing"
    mock_game.players = [MagicMock(id=gamer_user.uuid, name="gamer", is_bot=False)]
    mock_game._users = {gamer_user.uuid: gamer_user}

    def mock_get_player_by_id(pid):
        for p in mock_game.players:
            if p.id == pid:
                return p
        return None
    mock_game.get_player_by_id = mock_get_player_by_id
    table.game = mock_game

    # Check _restore_user_state logic directly
    server._user_states["gamer"] = {"menu": "motd_menu", "motd_version": 1}
    server._restore_user_state(gamer_user, "gamer")
    print(server._user_states["gamer"])
