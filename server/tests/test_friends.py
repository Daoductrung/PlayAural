import pytest
from unittest.mock import MagicMock
from server.persistence.database import Database
from server.core.server import Server
from server.users.network_user import NetworkUser
import tempfile
import os

class TestFriendsSystem:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_file.close()
        self.db = Database(self.temp_file.name)
        self.db.connect()

        self.server = Server(db_path=self.temp_file.name)
        self.server._db = self.db

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
