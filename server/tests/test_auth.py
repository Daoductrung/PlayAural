import pytest
from server.auth.auth import AuthManager
from server.persistence.database import Database
from server.core.server import Server
import tempfile
import os

class MockClient:
    def __init__(self):
        self.sent_messages = []

    async def send(self, message):
        self.sent_messages.append(message)


class TestAuthSecurity:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_file.close()
        self.db = Database(self.temp_file.name)
        self.db.connect()
        self.server = Server(db_path=self.temp_file.name)
        self.server._db = self.db
        self.server._auth = AuthManager(self.db)
        # Avoid creating the actual websocket server
        self.server._ws_server = None

    def teardown_method(self):
        self.db.close()
        os.unlink(self.temp_file.name)

    @pytest.mark.asyncio
    async def test_username_length_validation(self):
        client = MockClient()

        # Test too short
        packet = {"username": "ab", "password": "Password123"}
        await self.server._handle_register(client, packet)
        assert len(client.sent_messages) == 1
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "username_length"

        # Test too long
        packet = {"username": "a" * 31, "password": "Password123"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "username_length"

    @pytest.mark.asyncio
    async def test_password_strength_validation(self):
        client = MockClient()

        # Test too short
        packet = {"username": "validuser", "password": "Pass1"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "password_weak"

        # Test no numbers
        packet = {"username": "validuser", "password": "PasswordOnlyLetters"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "password_weak"

        # Test no letters
        packet = {"username": "validuser", "password": "123456789"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "password_weak"

    @pytest.mark.asyncio
    async def test_valid_registration(self):
        client = MockClient()
        packet = {"username": "validuser", "password": "Password123"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "success"

        # Check user is in db
        user = self.db.get_user("validuser")
        assert user is not None
