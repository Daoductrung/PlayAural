import pytest
from server.auth.auth import AuthManager
from server.persistence.database import Database
from server.core.server import Server
import tempfile
import os

class MockClient:
    def __init__(self):
        self.sent_messages = []
        self.ip_address = "127.0.0.1"
        self.address = "127.0.0.1:12345"
        self.username = None
        self.authenticated = False
        self.closed = False

    async def send(self, message):
        self.sent_messages.append(message)

    async def close(self):
        self.closed = True


class DummyWebSocketServer:
    def get_client_by_username(self, username):
        return None

    def register_client_username(self, address, username):
        return None


class TestAuthSecurity:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_file.close()
        self.db = Database(self.temp_file.name)
        self.db.connect()
        self.server = Server(db_path=self.temp_file.name)
        self.server._db = self.db
        self.server._auth = AuthManager(self.db)
        self.server._ws_server = DummyWebSocketServer()

    def teardown_method(self):
        self.db.close()
        os.unlink(self.temp_file.name)

    @pytest.mark.asyncio
    async def test_username_length_validation(self):
        client = MockClient()

        # Test too short
        packet = {"username": "ab", "password": "Password123", "email": "test@test.com"}
        await self.server._handle_register(client, packet)
        assert len(client.sent_messages) == 1
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "username_length"

        # Test too long
        packet = {"username": "a" * 31, "password": "Password123", "email": "test@test.com"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "username_length"

    @pytest.mark.asyncio
    async def test_password_strength_validation(self):
        client = MockClient()

        # Test too short
        packet = {"username": "validuser", "password": "Pass1", "email": "test@test.com"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "password_weak"

        # Test no numbers
        packet = {"username": "validuser", "password": "PasswordOnlyLetters", "email": "test@test.com"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "password_weak"

        # Test no letters
        packet = {"username": "validuser", "password": "123456789", "email": "test@test.com"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "password_weak"

    @pytest.mark.asyncio
    async def test_valid_registration(self):
        client = MockClient()
        packet = {"username": "validuser", "password": "Password123", "email": "test@test.com"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "success"

        # Check user is in db
        user = self.db.get_user("validuser")
        assert user is not None

    @pytest.mark.asyncio
    async def test_email_mandatory_registration(self):
        client = MockClient()

        # Test no email
        packet = {"username": "validuser", "password": "Password123"}
        await self.server._handle_register(client, packet)
        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "email_empty"

    @pytest.mark.asyncio
    async def test_email_uniqueness_registration(self):
        client = MockClient()

        # 1. Register first user
        self.db.create_user("firstuser", "hash", email="unique@test.com")

        # 2. Try to register with same email
        packet = {"username": "seconduser", "password": "Password123", "email": "unique@test.com"}
        await self.server._handle_register(client, packet)

        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "email_taken"

    @pytest.mark.asyncio
    async def test_python_registration_bypasses_captcha_while_web_requires_it(self, monkeypatch):
        calls = []

        async def fake_verify(token, remote_ip):
            calls.append((token, remote_ip))
            return False, "captcha_missing"

        monkeypatch.setattr("server.core.server.verify_captcha", fake_verify)

        python_client = MockClient()
        await self.server._handle_register(
            python_client,
            {
                "type": "register",
                "client": "python",
                "username": "pythonuser",
                "password": "Password123",
                "email": "python@test.com",
                "locale": "en",
            },
        )
        assert python_client.sent_messages[-1]["status"] == "success"
        assert calls == []

        web_client = MockClient()
        await self.server._handle_register(
            web_client,
            {
                "type": "register",
                "client": "web",
                "username": "webuser",
                "password": "Password123",
                "email": "web@test.com",
                "locale": "en",
            },
        )
        assert web_client.sent_messages[-1]["status"] == "error"
        assert web_client.sent_messages[-1]["error"] == "captcha_missing"
        assert web_client.closed is True
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_python_authorize_bypasses_captcha_while_web_requires_it(self, monkeypatch):
        calls = []

        async def fake_verify(token, remote_ip):
            calls.append((token, remote_ip))
            return False, "captcha_missing"

        monkeypatch.setattr("server.core.server.verify_captcha", fake_verify)

        self.server._auth.register("authuser", "Password123")

        python_client = MockClient()
        await self.server._handle_authorize(
            python_client,
            {
                "type": "authorize",
                "client": "python",
                "username": "authuser",
                "password": "Password123",
                "version": "1.0.0",
            },
        )
        assert python_client.sent_messages[0]["type"] == "authorize_success"
        assert calls == []

        web_client = MockClient()
        await self.server._handle_authorize(
            web_client,
            {
                "type": "authorize",
                "client": "web",
                "username": "authuser",
                "password": "Password123",
                "version": "1.0.0",
            },
        )
        assert web_client.sent_messages[-1]["type"] == "login_failed"
        assert web_client.sent_messages[-1]["reason"] == "captcha_missing"
        assert web_client.closed is True
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_python_password_reset_request_bypasses_captcha_while_web_requires_it(self, monkeypatch):
        calls = []

        async def fake_verify(token, remote_ip):
            calls.append((token, remote_ip))
            return False, "captcha_missing"

        monkeypatch.setattr("server.core.server.verify_captcha", fake_verify)

        python_client = MockClient()
        await self.server._handle_request_password_reset(
            python_client,
            {
                "type": "request_password_reset",
                "client": "python",
                "email": "reset@test.com",
                "locale": "en",
            },
        )
        assert python_client.sent_messages[-1]["status"] == "error"
        assert python_client.sent_messages[-1]["error"] == "smtp_not_configured"
        assert calls == []

        web_client = MockClient()
        await self.server._handle_request_password_reset(
            web_client,
            {
                "type": "request_password_reset",
                "client": "web",
                "email": "reset@test.com",
                "locale": "en",
            },
        )
        assert web_client.sent_messages[-1]["status"] == "error"
        assert web_client.sent_messages[-1]["error"] == "captcha_missing"
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_python_submit_reset_code_bypasses_captcha_while_web_requires_it(self, monkeypatch):
        calls = []

        async def fake_verify(token, remote_ip):
            calls.append((token, remote_ip))
            return False, "captcha_missing"

        monkeypatch.setattr("server.core.server.verify_captcha", fake_verify)

        self.server._auth.register("resetuser", "OldPassword123", email="reset@test.com")
        user_record = self.db.get_user_by_email("reset@test.com")
        assert user_record is not None
        token = self.server._auth.generate_reset_token(user_record.uuid)

        python_client = MockClient()
        await self.server._handle_submit_reset_code(
            python_client,
            {
                "type": "submit_reset_code",
                "client": "python",
                "email": "reset@test.com",
                "code": token,
                "new_password": "NewPassword123",
                "locale": "en",
            },
        )
        assert python_client.sent_messages[-1]["status"] == "success"
        assert calls == []
        assert self.server._auth.authenticate("resetuser", "NewPassword123")

        token = self.server._auth.generate_reset_token(user_record.uuid)
        web_client = MockClient()
        await self.server._handle_submit_reset_code(
            web_client,
            {
                "type": "submit_reset_code",
                "client": "web",
                "email": "reset@test.com",
                "code": token,
                "new_password": "AnotherPass123",
                "locale": "en",
            },
        )
        assert web_client.sent_messages[-1]["status"] == "error"
        assert web_client.sent_messages[-1]["error"] == "captcha_missing"
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_authorize_rate_limit_triggers_after_twenty_failed_attempts(self):
        username = "authuser"
        correct_password = "Password123"
        wrong_password = "WrongPassword123"
        self.server._auth.register(username, correct_password)

        for _ in range(self.server._rate_limiter.LOGIN_MAX_ATTEMPTS):
            client = MockClient()
            await self.server._handle_authorize(
                client,
                {
                    "type": "authorize",
                    "client": "python",
                    "username": username,
                    "password": wrong_password,
                    "version": "1.0.0",
                },
            )
            assert client.sent_messages[-1]["type"] == "login_failed"
            assert client.sent_messages[-1]["reason"] == "wrong_password"

        blocked_client = MockClient()
        await self.server._handle_authorize(
            blocked_client,
            {
                "type": "authorize",
                "client": "python",
                "username": username,
                "password": correct_password,
                "version": "1.0.0",
            },
        )
        assert blocked_client.sent_messages[-1]["type"] == "login_failed"
        assert blocked_client.sent_messages[-1]["reason"] == "rate_limit"
        assert blocked_client.closed is True
