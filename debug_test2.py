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

    await server._on_client_disconnect(client)

    server._db.create_motd(1, {"en": "New MOTD"})

    new_client = MagicMock()
    new_client.username = "gamer"
    new_client.authenticated = True
    new_client.send = AsyncMock()

    packet = {
        "username": "gamer",
        "password": "hash",
        "client": "python",
        "version": "0.1.6"
    }

    server._auth.authenticate = MagicMock(return_value=True)
    server._ws_server = MagicMock()
    server._ws_server.get_client_by_username = MagicMock(return_value=None)

    await server._handle_authorize(new_client, packet)

    print(f"User state after MOTD: {server._user_states['gamer']}")

    new_gamer_user = server._users["gamer"]

    # ensure uuid in user matches what is in players list
    print(f"new_gamer_user.uuid: {new_gamer_user.uuid}")
    print(f"player id in game: {mock_game.players[0].id}")
    print(f"Table members: {[m.username for m in table.members]}")

    await server._handle_menu(new_client, {"selection_id": "ok"})
    print(f"Final state: {server._user_states['gamer']}")
