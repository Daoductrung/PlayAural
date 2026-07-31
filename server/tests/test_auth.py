import pytest
from server.auth.auth import AuthManager
from server.persistence.database import Database
from server.core.server import Server, VERSION, WELCOME_SOUND
from server.users.network_user import NetworkUser
import tempfile
import os
import asyncio

class MockClient:
    def __init__(self):
        self.sent_messages = []
        self.ip_address = "127.0.0.1"
        self.address = "127.0.0.1:12345"
        self.username = None
        self.authenticated = False
        self.retired = False
        self.closed = False

    async def send(self, message):
        self.sent_messages.append(message)

    async def close(self):
        self.closed = True


class DummyWebSocketServer:
    def __init__(self):
        self._clients_by_address = {}
        self._clients_by_username = {}

    def bind_client(self, client):
        self._clients_by_address[client.address] = client

    def get_client_by_username(self, username):
        return self._clients_by_username.get(username)

    def register_client_username(self, address, username):
        client = self._clients_by_address.get(address)
        if client is not None:
            self._clients_by_username[username] = client

    def unregister_client_username(self, username, client):
        if self._clients_by_username.get(username) is client:
            self._clients_by_username.pop(username, None)


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
    async def test_registration_rejects_generated_bot_name(self):
        client = MockClient()
        packet = {
            "username": "Pho Pixel",
            "password": "Password123",
            "email": "botname@test.com",
        }

        await self.server._handle_register(client, packet)

        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "username_reserved_bot"
        assert self.db.get_user("Pho Pixel") is None

    @pytest.mark.asyncio
    async def test_registration_rejects_active_runtime_bot_name(self):
        class FakePlayer:
            def __init__(self, name, is_bot):
                self.name = name
                self.is_bot = is_bot

        class FakeGame:
            players = [FakePlayer("Pho Pixel 2", True), FakePlayer("Human", False)]

        class FakeTable:
            game = FakeGame()

        self.server._tables.get_all_tables = lambda: [FakeTable()]
        client = MockClient()
        packet = {
            "username": "pho pixel 2",
            "password": "Password123",
            "email": "runtimebot@test.com",
        }

        await self.server._handle_register(client, packet)

        assert client.sent_messages[-1]["status"] == "error"
        assert client.sent_messages[-1]["error"] == "username_reserved_bot"
        assert self.db.get_user("pho pixel 2") is None

    def test_auth_manager_rejects_generated_bot_name(self):
        result = self.server._auth.register("Omega Alpha", "Password123")

        assert result == "username_reserved_bot"
        assert self.db.get_user("Omega Alpha") is None

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
    async def test_python_and_mobile_registration_bypass_captcha_while_web_requires_it(self, monkeypatch):
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

        mobile_client = MockClient()
        await self.server._handle_register(
            mobile_client,
            {
                "type": "register",
                "client": "mobile",
                "username": "mobileuser",
                "password": "Password123",
                "email": "mobile@test.com",
                "locale": "en",
            },
        )
        assert mobile_client.sent_messages[-1]["status"] == "success"
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
    async def test_python_and_mobile_authorize_bypass_captcha_while_web_requires_it(self, monkeypatch):
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
                "version": VERSION,
            },
        )
        assert python_client.sent_messages[0]["type"] == "authorize_success"
        assert calls == []

        mobile_client = MockClient()
        await self.server._handle_authorize(
            mobile_client,
            {
                "type": "authorize",
                "client": "mobile",
                "username": "authuser",
                "password": "Password123",
                "version": VERSION,
            },
        )
        assert mobile_client.sent_messages[0]["type"] == "authorize_success"
        assert calls == []

        web_client = MockClient()
        await self.server._handle_authorize(
            web_client,
            {
                "type": "authorize",
                "client": "web",
                "username": "authuser",
                "password": "Password123",
                "version": VERSION,
            },
        )
        assert web_client.sent_messages[-1]["type"] == "login_failed"
        assert web_client.sent_messages[-1]["reason"] == "captcha_missing"
        assert web_client.closed is True
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_python_and_mobile_password_reset_request_bypass_captcha_while_web_requires_it(self, monkeypatch):
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

        mobile_client = MockClient()
        await self.server._handle_request_password_reset(
            mobile_client,
            {
                "type": "request_password_reset",
                "client": "mobile",
                "email": "reset@test.com",
                "locale": "en",
            },
        )
        assert mobile_client.sent_messages[-1]["status"] == "error"
        assert mobile_client.sent_messages[-1]["error"] == "smtp_not_configured"
        assert calls == []

        self.server._rate_limiter._password_resets.clear()

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
    async def test_python_and_mobile_submit_reset_code_bypass_captcha_while_web_requires_it(self, monkeypatch):
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
        mobile_client = MockClient()
        await self.server._handle_submit_reset_code(
            mobile_client,
            {
                "type": "submit_reset_code",
                "client": "mobile",
                "email": "reset@test.com",
                "code": token,
                "new_password": "MobilePass123",
                "locale": "en",
            },
        )
        assert mobile_client.sent_messages[-1]["status"] == "success"
        assert calls == []
        assert self.server._auth.authenticate("resetuser", "MobilePass123")

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
                    "version": VERSION,
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
                "version": VERSION,
            },
        )
        assert blocked_client.sent_messages[-1]["type"] == "login_failed"
        assert blocked_client.sent_messages[-1]["reason"] == "rate_limit"
        assert blocked_client.closed is True

    @pytest.mark.asyncio
    async def test_authorize_normalizes_to_canonical_username(self):
        self.server._auth.register("Alice", "Password123")
        client = MockClient()
        self.server._ws_server.bind_client(client)

        await self.server._handle_authorize(
            client,
            {
                "type": "authorize",
                "client": "python",
                "username": "alice",
                "password": "Password123",
                "version": VERSION,
            },
        )

        assert client.username == "Alice"
        assert "Alice" in self.server._users
        assert "alice" not in self.server._users
        assert self.server._ws_server.get_client_by_username("Alice") is client
        assert client.sent_messages[0]["type"] == "authorize_success"
        assert client.sent_messages[0]["username"] == "Alice"

    @pytest.mark.asyncio
    async def test_outdated_native_client_gets_updater_without_owning_session(self):
        self.server._auth.register("Alice", "Password123")
        current_client = MockClient()
        outdated_client = MockClient()
        outdated_client.address = "127.0.0.1:23456"
        self.server._ws_server.bind_client(current_client)
        self.server._ws_server.bind_client(outdated_client)

        current_packet = {
            "type": "authorize",
            "client": "python",
            "username": "Alice",
            "password": "Password123",
            "version": VERSION,
        }
        await self.server._handle_authorize(current_client, current_packet)
        current_user = self.server._users["Alice"]

        await self.server._handle_authorize(
            outdated_client,
            {
                **current_packet,
                "client": "mobile",
                "version": "0.0.1",
            },
        )

        assert len(outdated_client.sent_messages) == 1
        update_packet = outdated_client.sent_messages[0]
        assert update_packet["type"] == "authorize_success"
        assert update_packet["username"] == "Alice"
        assert update_packet["update_info"]["version"] == VERSION
        assert update_packet["update_info"]["url"]
        assert update_packet["sounds_info"]["version"]
        assert update_packet["reset_ui"] is True
        assert outdated_client.username is None
        assert outdated_client.authenticated is False
        assert outdated_client.retired is True
        assert current_client.closed is False
        assert self.server._users["Alice"] is current_user
        assert self.server._ws_server.get_client_by_username("Alice") is current_client

        await self.server._on_client_message(outdated_client, {"type": "ping"})
        assert len(outdated_client.sent_messages) == 1

    @pytest.mark.parametrize("client_type", ["python", "web", "mobile"])
    @pytest.mark.asyncio
    async def test_authorize_unwinds_logout_prompt_and_orders_welcome_audio(
        self,
        client_type,
    ):
        record = self.db.create_user(
            "Alice",
            "hash",
            approved=True,
            email="alice@example.com",
        )
        self.server._user_states[record.username] = {
            "menu": "logout_confirm_menu",
            "_stack": [
                {
                    "menu": "main_menu",
                    "_last_selection_id": "logout",
                    "_restore_focus_id": "logout",
                },
            ],
        }
        client = MockClient()
        self.server._ws_server.bind_client(client)

        await self.server._activate_authenticated_session(
            client,
            canonical_username=record.username,
            client_type=client_type,
            client_platform="test",
            user_record=record,
        )

        assert client.sent_messages[0]["type"] == "authorize_success"
        restored_state = self.server._user_states[record.username]
        assert restored_state["menu"] == "main_menu"
        assert restored_state.get("_stack", []) == []
        assert "_last_selection_id" not in restored_state
        assert "_restore_focus_id" not in restored_state

        queued = self.server._users[record.username].get_queued_messages()
        welcome_indexes = [
            index
            for index, packet in enumerate(queued)
            if (
                packet.get("type") == "audio"
                and packet.get("command") == "play"
                and packet.get("kind") == "sfx"
                and packet.get("asset") == WELCOME_SOUND
            )
        ]
        assert len(welcome_indexes) == 1
        welcome_index = welcome_indexes[0]
        assert queued[welcome_index]["priority"] == 100
        assert queued[welcome_index]["max_instances"] == 1
        assert any(
            index < welcome_index
            and packet.get("type") == "audio"
            and packet.get("command") == "stop_all"
            for index, packet in enumerate(queued)
        )
        assert any(
            index < welcome_index
            and packet.get("type") == "audio"
            and packet.get("command") == "play"
            and packet.get("kind") == "music"
            for index, packet in enumerate(queued)
        )
        assert not any(
            index > welcome_index
            and packet.get("type") == "audio"
            and packet.get("command") == "stop_all"
            for index, packet in enumerate(queued)
        )

    @pytest.mark.asyncio
    async def test_confirmed_logout_discards_resumable_ui_state(self):
        client = MockClient()
        user = NetworkUser("Alice", "en", client, approved=True)
        self.server._users[user.username] = user
        self.server._user_states[user.username] = {
            "menu": "logout_confirm_menu",
            "_stack": [{"menu": "main_menu"}],
        }
        self.server._deferred_navigation[user.username] = (
            self.server._show_main_menu,
            (),
            {},
        )

        async def skip_failsafe(_user):
            return None

        self.server._failsafe_close = skip_failsafe
        await self.server._handle_logout_confirm_selection(user, "yes")
        await asyncio.sleep(0)

        assert client.sent_messages == [{"type": "force_exit"}]
        assert user.username not in self.server._user_states
        assert user.username not in self.server._deferred_navigation

    @pytest.mark.asyncio
    async def test_authorize_kicks_existing_session_across_case_variants(self):
        self.server._auth.register("Alice", "Password123")

        first_client = MockClient()
        second_client = MockClient()
        second_client.address = "127.0.0.1:23456"
        self.server._ws_server.bind_client(first_client)
        self.server._ws_server.bind_client(second_client)

        await self.server._handle_authorize(
            first_client,
            {
                "type": "authorize",
                "client": "python",
                "username": "Alice",
                "password": "Password123",
                "version": VERSION,
            },
        )

        await self.server._handle_authorize(
            second_client,
            {
                "type": "authorize",
                "client": "python",
                "username": "alice",
                "password": "Password123",
                "version": VERSION,
            },
        )

        assert first_client.closed is True
        assert first_client.sent_messages[-1]["type"] == "disconnect"
        assert second_client.username == "Alice"
        assert self.server._ws_server.get_client_by_username("Alice") is second_client

    @pytest.mark.asyncio
    async def test_retired_session_disconnect_cannot_clean_up_replacement(self):
        self.server._auth.register("Alice", "Password123")

        first_client = MockClient()
        second_client = MockClient()
        second_client.address = "127.0.0.1:23456"
        self.server._ws_server.bind_client(first_client)
        self.server._ws_server.bind_client(second_client)

        auth_packet = {
            "type": "authorize",
            "client": "python",
            "username": "Alice",
            "password": "Password123",
            "version": VERSION,
        }
        await self.server._handle_authorize(first_client, auth_packet)
        await self.server._handle_authorize(second_client, auth_packet)

        replacement = self.server._users["Alice"]
        self.server._user_states["Alice"] = {"menu": "options_menu"}
        self.server._voice_presence_by_user["Alice"] = {
            "scope": "table",
            "context_id": "test-table",
        }
        self.server._audio_input_devices_by_user["Alice"] = [
            {"id": "mic", "name": "Microphone"}
        ]

        await self.server._on_client_disconnect(first_client)

        assert self.server._users["Alice"] is replacement
        assert replacement.connection is second_client
        assert self.server._user_states["Alice"] == {"menu": "options_menu"}
        assert "Alice" in self.server._voice_presence_by_user
        assert "Alice" in self.server._audio_input_devices_by_user

    @pytest.mark.asyncio
    async def test_retired_session_packets_cannot_mutate_replacement(self):
        self.server._auth.register("Alice", "Password123")

        first_client = MockClient()
        second_client = MockClient()
        second_client.address = "127.0.0.1:23456"
        self.server._ws_server.bind_client(first_client)
        self.server._ws_server.bind_client(second_client)

        auth_packet = {
            "type": "authorize",
            "client": "python",
            "username": "Alice",
            "password": "Password123",
            "version": VERSION,
        }
        await self.server._handle_authorize(first_client, auth_packet)
        await self.server._handle_authorize(second_client, auth_packet)

        ping_clients = []

        async def record_ping(client):
            ping_clients.append(client)

        self.server._handle_ping = record_ping
        # Even if a stale transport object is maliciously toggled back to an
        # authenticated-looking state, object ownership remains authoritative.
        first_client.authenticated = True
        first_client.retired = False
        await self.server._on_client_message(first_client, {"type": "ping"})
        await self.server._on_client_message(second_client, {"type": "ping"})

        assert ping_clients == [second_client]

    @pytest.mark.asyncio
    async def test_account_management_packets_require_pristine_preauth_socket(self):
        calls = []

        async def record_call(client, packet):
            calls.append((client, packet["type"]))

        self.server._handle_register = record_call
        self.server._handle_request_password_reset = record_call
        self.server._handle_submit_reset_code = record_call

        active_client = MockClient()
        active_client.username = "Alice"
        active_client.authenticated = True
        retired_client = MockClient()
        retired_client.retired = True
        for packet_type in (
            "register",
            "request_password_reset",
            "submit_reset_code",
        ):
            await self.server._on_client_message(
                active_client,
                {"type": packet_type},
            )
            await self.server._on_client_message(
                retired_client,
                {"type": packet_type},
            )

        assert calls == []

        fresh_client = MockClient()
        for packet_type in (
            "register",
            "request_password_reset",
            "submit_reset_code",
        ):
            await self.server._on_client_message(
                fresh_client,
                {"type": packet_type},
            )

        assert [packet_type for _, packet_type in calls] == [
            "register",
            "request_password_reset",
            "submit_reset_code",
        ]

    @pytest.mark.asyncio
    async def test_motd_defers_but_preserves_live_handover_semantics(self):
        record = self.db.create_user(
            "Alice",
            "Password123",
            approved=True,
            email="alice@example.com",
        )
        self.db.create_motd(1, {"en": "Important update"})
        self.server._auth.authenticate = lambda username, password: True

        old_client = MockClient()
        old_client.username = record.username
        old_client.authenticated = True
        old_client.session_ready = True
        self.server._ws_server.bind_client(old_client)
        self.server._ws_server.register_client_username(
            old_client.address,
            record.username,
        )
        old_user = NetworkUser(
            record.username,
            record.locale,
            old_client,
            uuid=record.uuid,
            approved=True,
        )
        self.server._users[record.username] = old_user
        self.server._user_states[record.username] = {"menu": "main_menu"}

        new_client = MockClient()
        new_client.address = "127.0.0.1:23456"
        self.server._ws_server.bind_client(new_client)
        presence_refreshes = 0

        def record_presence_refresh():
            nonlocal presence_refreshes
            presence_refreshes += 1

        self.server.on_user_presence_changed = record_presence_refresh
        await self.server._handle_authorize(
            new_client,
            {
                "type": "authorize",
                "client": "mobile",
                "username": record.username,
                "password": "Password123",
                "version": VERSION,
            },
        )

        new_user = self.server._users[record.username]
        assert new_user.session_handover_pending is True
        assert self.server._user_states[record.username]["menu"] == "motd_menu"
        assert presence_refreshes == 1

        await self.server._handle_motd_selection(
            new_user,
            "ok",
            self.server._user_states[record.username],
        )

        assert new_user.session_handover_pending is False
        assert self.server._user_states[record.username]["menu"] == "main_menu"

    @pytest.mark.asyncio
    async def test_disconnect_does_not_reset_account_rate_limits(self):
        self.server._auth.register("Alice", "Password123")
        client = MockClient()
        self.server._ws_server.bind_client(client)
        await self.server._handle_authorize(
            client,
            {
                "type": "authorize",
                "client": "python",
                "username": "Alice",
                "password": "Password123",
                "version": VERSION,
            },
        )

        for _ in range(self.server._chat_rate_limiter.BUCKET_CAPACITY):
            assert self.server._chat_rate_limiter.try_consume("Alice")[0]
        assert not self.server._chat_rate_limiter.try_consume("Alice")[0]
        assert self.server._voice_rate_limiter.try_consume("Alice")
        assert self.server._voice_rate_limiter.try_consume("Alice")
        assert not self.server._voice_rate_limiter.try_consume("Alice")

        await self.server._on_client_disconnect(client)

        assert not self.server._chat_rate_limiter.try_consume("Alice")[0]
        assert not self.server._voice_rate_limiter.try_consume("Alice")
        for task in self.server._pending_disconnects.values():
            task.cancel()
        for task in self.server._pending_session_state_cleanups.values():
            task.cancel()

    @pytest.mark.asyncio
    async def test_simultaneous_authorizations_leave_exactly_one_owner(self):
        self.server._auth.register("Alice", "Password123")
        first_client = MockClient()
        second_client = MockClient()
        second_client.address = "127.0.0.1:23456"
        self.server._ws_server.bind_client(first_client)
        self.server._ws_server.bind_client(second_client)
        packet = {
            "type": "authorize",
            "client": "python",
            "username": "Alice",
            "password": "Password123",
            "version": VERSION,
        }

        await asyncio.gather(
            self.server._handle_authorize(first_client, packet),
            self.server._handle_authorize(second_client, packet),
        )

        winner = self.server._ws_server.get_client_by_username("Alice")
        assert winner in {first_client, second_client}
        assert self.server._users["Alice"].connection is winner
        loser = second_client if winner is first_client else first_client
        assert loser.closed is True
        assert loser.retired is True
        assert winner.retired is False

    @pytest.mark.asyncio
    async def test_account_deletion_invalidates_login_waiting_on_session_lock(self):
        self.server._auth.register("Alice", "Password123")
        client = MockClient()
        self.server._ws_server.bind_client(client)
        packet = {
            "type": "authorize",
            "client": "python",
            "username": "Alice",
            "password": "Password123",
            "version": VERSION,
        }

        account_lock = self.server._session_lock_for("Alice")
        await account_lock.acquire()
        delete_task = asyncio.create_task(
            self.server._delete_account_and_evict(
                "Alice",
                {
                    "type": "disconnect",
                    "reason": "Account deleted",
                    "reconnect": False,
                },
            )
        )
        await asyncio.sleep(0)
        authorize_task = asyncio.create_task(
            self.server._handle_authorize(client, packet)
        )
        await asyncio.sleep(0)
        account_lock.release()

        deleted, _ = await asyncio.gather(delete_task, authorize_task)

        assert deleted is True
        assert self.db.get_user("Alice") is None
        assert "Alice" not in self.server._users
        assert client.authenticated is False
        assert client.sent_messages[-1]["type"] == "login_failed"
        assert client.sent_messages[-1]["reason"] == "user_not_found"

    @pytest.mark.asyncio
    async def test_output_is_held_until_session_restore_is_ready(self):
        client = MockClient()
        client.username = "Alice"
        client.authenticated = True
        client.session_ready = False
        self.server._ws_server.bind_client(client)
        self.server._ws_server.register_client_username(
            client.address,
            client.username,
        )
        user = NetworkUser("Alice", "en", client)
        self.server._users["Alice"] = user
        user.speak("Held during handover", buffer="system")

        self.server._flush_user_messages()
        await asyncio.sleep(0)
        assert client.sent_messages == []
        assert len(user._message_queue) == 1

        client.session_ready = True
        self.server._flush_user_messages()
        await asyncio.sleep(0)
        assert client.sent_messages == [
            {
                "type": "speak",
                "text": "Held during handover",
                "buffer": "system",
            }
        ]
