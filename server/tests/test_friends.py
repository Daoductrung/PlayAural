import pytest
from unittest.mock import MagicMock
from server.auth.auth import AuthManager
from server.persistence.database import Database
from server.core.server import Server
from server.users.network_user import NetworkUser
import tempfile
import os


class MockClient:
    def __init__(self, address: str):
        self.sent_messages = []
        self.ip_address = "127.0.0.1"
        self.address = address
        self.username = None
        self.authenticated = False
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

class TestFriendsSystem:
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

    def test_send_request_and_duplicate(self):
        self.db.create_user("alice", "hash")
        self.db.create_user("bob", "hash")

        u_alice = self.db.get_user("alice")
        u_bob = self.db.get_user("bob")

        # 1. Send Request
        res = self.db.send_friend_request(u_alice.uuid, u_bob.uuid)
        assert res == "sent"

        # 2. Try sending again (Duplicate)
        res2 = self.db.send_friend_request(u_alice.uuid, u_bob.uuid)
        assert res2 == "duplicate"

    def test_cross_request_instant_accept(self):
        self.db.create_user("alice", "hash")
        self.db.create_user("bob", "hash")

        u_alice = self.db.get_user("alice")
        u_bob = self.db.get_user("bob")

        # Alice sends to Bob
        self.db.send_friend_request(u_alice.uuid, u_bob.uuid)

        # Bob unknowingly sends to Alice -> Should instantly accept
        res = self.db.send_friend_request(u_bob.uuid, u_alice.uuid)
        assert res == "accepted"

        # Verify they are friends
        friends_alice = self.db.get_friends(u_alice.uuid)
        assert len(friends_alice) == 1
        assert friends_alice[0] == u_bob.uuid

    @pytest.mark.asyncio
    async def test_grouped_offline_notifications(self):
        # We need to use NetworkUser object to test the actual grouped output logic
        self.db.create_user("alice", "hash")
        u_alice = self.db.get_user("alice")

        # Add a bunch of offline notifications
        self.db.add_notification(u_alice.uuid, "bob", "friend_request_received")
        self.db.add_notification(u_alice.uuid, "charlie", "friend_request_received")
        self.db.add_notification(u_alice.uuid, "dave", "friend_accepted")
        self.db.add_notification(u_alice.uuid, "eve", "friend_accepted")

        client = MagicMock()
        client.username = "alice"
        network_user = NetworkUser("alice", "en", client, uuid=u_alice.uuid)
        network_user.speak_l = MagicMock()
        network_user.play_sound = MagicMock()

        self.server._process_offline_notifications(network_user)

        # 1. Ensure TTS was called only TWICE (grouped) despite 4 notifications
        assert network_user.speak_l.call_count == 2

        # 2. Ensure sound was called TWICE
        assert network_user.play_sound.call_count == 2

        # Check actual DB is clear
        assert len(self.db.get_and_clear_notifications(u_alice.uuid)) == 0

    def test_account_deletion_cleanup(self):
        self.db.create_user("alice", "hash")
        self.db.create_user("bob", "hash")
        u_alice = self.db.get_user("alice")
        u_bob = self.db.get_user("bob")

        # Make them friends
        self.db.send_friend_request(u_alice.uuid, u_bob.uuid)
        self.db.accept_friend_request(u_alice.uuid, u_bob.uuid)

        assert len(self.db.get_friends(u_alice.uuid)) == 1

        # Add a notification
        self.db.add_notification(u_bob.uuid, "alice", "friend_removed")

        # Delete Alice
        self.db.delete_user("alice")

        # Verify Bob has NO friends
        assert len(self.db.get_friends(u_bob.uuid)) == 0

        # Verify Bob has NO notifications from Alice
        assert len(self.db.get_and_clear_notifications(u_bob.uuid)) == 0

    @pytest.mark.asyncio
    async def test_friends_list_marks_case_variant_login_as_online(self):
        self.server._auth.register("Alice", "Password123")
        self.server._auth.register("Bob", "Password123")

        alice_record = self.db.get_user("Alice")
        bob_record = self.db.get_user("Bob")
        assert alice_record is not None
        assert bob_record is not None

        self.db.send_friend_request(alice_record.uuid, bob_record.uuid)
        self.db.accept_friend_request(alice_record.uuid, bob_record.uuid)

        alice_client = MockClient("127.0.0.1:10001")
        self.server._ws_server.bind_client(alice_client)
        await self.server._handle_authorize(
            alice_client,
            {
                "type": "authorize",
                "client": "python",
                "username": "alice",
                "password": "Password123",
                "version": "1.0.0",
            },
        )

        bob_client = MagicMock()
        bob_user = NetworkUser("Bob", "en", bob_client, uuid=bob_record.uuid, approved=True)
        items = self.server._get_friends_list_menu_items(bob_user)

        assert any(item.id == "friend_Alice" and "In Lobby" in item.text for item in items)
