import pytest
from unittest.mock import MagicMock
from server.auth.auth import AuthManager
from server.persistence.database import Database
from server.core.server import (
    FRIEND_REMOVE_CONFIRM_MENU,
    MAX_CHAT_MESSAGE_LENGTH,
    Server,
    USER_BLOCK_CONFIRM_MENU,
    VERSION,
)
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

    def _create_friendship(self):
        self.db.create_user("Alice", "hash")
        self.db.create_user("Bob", "hash")
        alice = self.db.get_user("Alice")
        bob = self.db.get_user("Bob")
        self.db.send_friend_request(alice.uuid, bob.uuid)
        self.db.accept_friend_request(alice.uuid, bob.uuid)
        return alice, bob

    def _make_network_user(self, username: str, uuid: str) -> NetworkUser:
        client = MockClient(f"127.0.0.1:{10000 + len(self.server._users)}")
        user = NetworkUser(username, "en", client, uuid=uuid, approved=True)
        self.server._users[username] = user
        return user

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
        assert self.db.send_friend_request(u_alice.uuid, "missing-user") == "unknown"

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
        for source_username in ("bob", "charlie", "dave", "eve"):
            self.db.create_user(source_username, "hash")

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
        self.db.create_user("charlie", "hash")
        u_alice = self.db.get_user("alice")
        u_bob = self.db.get_user("bob")
        u_charlie = self.db.get_user("charlie")

        # Make them friends
        self.db.send_friend_request(u_alice.uuid, u_bob.uuid)
        self.db.accept_friend_request(u_alice.uuid, u_bob.uuid)

        assert len(self.db.get_friends(u_alice.uuid)) == 1

        # Add a notification
        self.db.add_notification(u_bob.uuid, "alice", "friend_removed")
        self.db.block_user(u_alice.uuid, u_charlie.uuid)
        self.db.block_user(u_charlie.uuid, u_alice.uuid)

        # Delete Alice
        self.db.delete_user("alice")

        # Verify Bob has NO friends
        assert len(self.db.get_friends(u_bob.uuid)) == 0

        # Verify Bob has NO notifications from Alice
        assert len(self.db.get_and_clear_notifications(u_bob.uuid)) == 0
        assert self.db.get_socially_blocked_ids(u_charlie.uuid) == set()

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
                "version": VERSION,
            },
        )

        bob_client = MagicMock()
        bob_user = NetworkUser("Bob", "en", bob_client, uuid=bob_record.uuid, approved=True)
        items = self.server._get_friends_list_menu_items(bob_user)

        assert any(item.id == "friend_Alice" and "Main menu" in item.text for item in items)

        table = self.server._tables.create_table(
            "crazyeights",
            "Alice",
            self.server._users["Alice"],
        )
        try:
            items = self.server._get_friends_list_menu_items(bob_user)
            assert any(
                item.id == "friend_Alice"
                and "Waiting at Crazy Eights table" in item.text
                for item in items
            )
        finally:
            table.destroy()

    def test_friend_request_resolves_case_variant_to_registered_name(self):
        self.db.create_user("Alice", "hash")
        self.db.create_user("Nguyễn Văn An", "hash")
        alice = self.db.get_user("Alice")
        target = self.db.get_user("nguyễn văn an")
        alice_user = self._make_network_user(alice.username, alice.uuid)

        status = self.server._send_friend_request_to_record(alice_user, target)
        messages = alice_user.get_queued_messages()

        assert status == "sent"
        assert self.db.get_pending_incoming_requests(target.uuid) == [alice.uuid]
        assert any(
            packet.get("key") == "friend-request-sent"
            and packet.get("params", {}).get("username") == "Nguyễn Văn An"
            for packet in messages
        )

    @pytest.mark.asyncio
    async def test_friend_request_input_resolves_spaced_case_variant(self):
        self.db.create_user("Alice", "hash")
        self.db.create_user("Nguyễn Văn An", "hash")
        alice = self.db.get_user("Alice")
        target = self.db.get_user("Nguyễn Văn An")
        alice_user = self._make_network_user(alice.username, alice.uuid)
        alice_user.connection.username = alice.username
        self.server._user_states[alice.username] = {
            "menu": "send_friend_request_input",
        }
        self.server._restore_input_parent = MagicMock()

        await self.server._handle_editbox(
            alice_user.connection,
            {"text": "nguyễn văn an"},
        )

        assert self.db.get_pending_incoming_requests(target.uuid) == [alice.uuid]
        assert any(
            packet.get("key") == "friend-request-sent"
            and packet.get("params", {}).get("username") == "Nguyễn Văn An"
            for packet in alice_user.get_queued_messages()
        )
        self.server._restore_input_parent.assert_called_once()

    @pytest.mark.asyncio
    async def test_friends_hub_can_block_offline_user_by_username(self):
        self.db.create_user("Alice", "hash")
        self.db.create_user("Nguyễn Văn An", "hash")
        alice = self.db.get_user("Alice")
        target = self.db.get_user("Nguyễn Văn An")
        alice_user = self._make_network_user(alice.username, alice.uuid)
        alice_user.connection.username = alice.username
        self.server._show_friends_hub_menu(alice_user)

        await self.server._handle_friends_hub_selection(alice_user, "block_user")
        assert self.server._user_states[alice.username]["menu"] == "block_user_input"

        await self.server._handle_editbox(
            alice_user.connection,
            {"text": "nguyễn văn an"},
        )
        state = self.server._user_states[alice.username]
        assert state["menu"] == USER_BLOCK_CONFIRM_MENU
        assert state["target_username"] == "Nguyễn Văn An"
        assert not self.db.has_blocked(alice.uuid, target.uuid)

        await self.server._handle_user_block_confirm_selection(
            alice_user,
            "yes",
            state,
        )

        assert self.db.has_blocked(alice.uuid, target.uuid)
        assert self.server._user_states[alice.username]["menu"] == "friends_hub_menu"

    @pytest.mark.asyncio
    async def test_private_message_to_self_accepts_case_variant_without_friendship(self):
        self.db.create_user("Trung", "hash")
        record = self.db.get_user("Trung")
        user = self._make_network_user(record.username, record.uuid)

        await self.server._deliver_private_message(user, "trung", "Remember this")
        messages = user.get_queued_messages()
        speech = [packet for packet in messages if packet.get("type") == "speak"]

        assert [packet.get("key") for packet in speech] == ["pm-sent-content"]
        assert speech[0]["params"] == {
            "username": "Trung",
            "message": "Remember this",
        }

    @pytest.mark.asyncio
    async def test_private_message_command_parses_full_spaced_username(self):
        self.db.create_user("Nguyễn Văn An", "hash")
        record = self.db.get_user("Nguyễn Văn An")
        user = self._make_network_user(record.username, record.uuid)
        user.connection.username = record.username

        await self.server._handle_chat(
            user.connection,
            {
                "convo": "local",
                "message": "@nguyễn văn an Ghi chú cho tôi",
            },
        )
        messages = user.get_queued_messages()

        assert any(
            packet.get("key") == "pm-sent-content"
            and packet.get("params") == {
                "username": "Nguyễn Văn An",
                "message": "Ghi chú cho tôi",
            }
            for packet in messages
        )

    @pytest.mark.asyncio
    async def test_private_message_resolves_friend_case_variant_canonically(self):
        alice, bob = self._create_friendship()
        alice_user = self._make_network_user(alice.username, alice.uuid)
        bob_user = self._make_network_user(bob.username, bob.uuid)

        await self.server._deliver_private_message(alice_user, "bob", "Hello")
        sender_messages = alice_user.get_queued_messages()
        recipient_messages = bob_user.get_queued_messages()

        assert any(
            packet.get("key") == "pm-sent-content"
            and packet.get("params", {}).get("username") == "Bob"
            for packet in sender_messages
        )
        assert any(
            packet.get("key") == "pm-received"
            and packet.get("params", {}).get("username") == "Alice"
            for packet in recipient_messages
        )

    @pytest.mark.asyncio
    async def test_friends_list_pages_large_results(self):
        self.db.create_user("Alice", "hash")
        alice = self.db.get_user("Alice")
        alice_user = self._make_network_user(alice.username, alice.uuid)

        def latest_menu_ids(messages: list[dict]) -> list[str]:
            menu = next(
                message
                for message in reversed(messages)
                if message.get("type") == "menu"
                and message.get("menu_id") == "friends_list_menu"
            )
            ids: list[str] = []
            for item in menu.get("items", []):
                if isinstance(item, dict):
                    ids.append(item.get("id", ""))
            return ids

        for index in range(101):
            username = f"Friend{index:03d}"
            self.db.create_user(username, "hash")
            friend = self.db.get_user(username)
            self.db.send_friend_request(alice.uuid, friend.uuid)
            self.db.accept_friend_request(alice.uuid, friend.uuid)

        self.server._show_friends_list_menu(alice_user)
        ids = latest_menu_ids(alice_user.get_queued_messages())
        assert len([item_id for item_id in ids if item_id.startswith("friend_")]) == 100
        assert "friend_Friend100" not in ids
        assert "refresh" not in ids
        assert "page_next" in ids

        await self.server._handle_friends_list_selection(
            alice_user,
            "page_next",
            self.server._user_states[alice.username],
        )

        last_page_ids = latest_menu_ids(alice_user.get_queued_messages())
        assert self.server._user_states[alice.username]["friends_page"] == 2
        assert "friend_Friend100" in last_page_ids
        assert "page_previous" in last_page_ids
        assert "page_next" not in last_page_ids

    @pytest.mark.asyncio
    async def test_remove_friend_prompts_before_deleting(self):
        alice, bob = self._create_friendship()
        alice_user = self._make_network_user(alice.username, alice.uuid)
        self.server._user_states[alice.username] = {
            "menu": "friend_actions_menu",
            "target_username": bob.username,
            "_stack": [
                {"menu": "friends_hub_menu"},
                {"menu": "friends_list_menu"},
            ],
        }

        await self.server._handle_friend_actions_selection(
            alice_user,
            "remove_friend",
            self.server._user_states[alice.username],
        )

        assert bob.uuid in self.db.get_friends(alice.uuid)
        state = self.server._user_states[alice.username]
        assert state["menu"] == FRIEND_REMOVE_CONFIRM_MENU
        assert state["target_username"] == bob.username

        messages = alice_user.get_queued_messages()
        assert any(
            msg.get("type") == "speak" and msg.get("key") == "friend-remove-confirm"
            for msg in messages
        )
        menu = next(msg for msg in messages if msg.get("type") == "menu")
        assert menu["menu_id"] == FRIEND_REMOVE_CONFIRM_MENU
        assert menu["escape_behavior"] == "select_last_option"
        assert [item["id"] for item in menu["items"]] == ["yes", "no"]

    @pytest.mark.asyncio
    async def test_remove_friend_cancel_keeps_friendship_and_returns_to_actions(self):
        alice, bob = self._create_friendship()
        alice_user = self._make_network_user(alice.username, alice.uuid)
        self.server._user_states[alice.username] = {
            "menu": "friend_actions_menu",
            "target_username": bob.username,
            "_stack": [
                {"menu": "friends_hub_menu"},
                {"menu": "friends_list_menu"},
            ],
        }
        await self.server._handle_friend_actions_selection(
            alice_user,
            "remove_friend",
            self.server._user_states[alice.username],
        )

        await self.server._handle_friend_remove_confirm_selection(
            alice_user,
            "no",
            self.server._user_states[alice.username],
        )

        assert bob.uuid in self.db.get_friends(alice.uuid)
        state = self.server._user_states[alice.username]
        assert state["menu"] == "friend_actions_menu"
        assert state["target_username"] == bob.username

    @pytest.mark.asyncio
    async def test_remove_friend_confirm_deletes_and_notifies_both_users(self):
        alice, bob = self._create_friendship()
        alice_user = self._make_network_user(alice.username, alice.uuid)
        bob_user = self._make_network_user(bob.username, bob.uuid)
        self.server._user_states[alice.username] = {
            "menu": "friend_actions_menu",
            "target_username": bob.username,
            "_stack": [
                {"menu": "friends_hub_menu"},
                {"menu": "friends_list_menu"},
            ],
        }
        await self.server._handle_friend_actions_selection(
            alice_user,
            "remove_friend",
            self.server._user_states[alice.username],
        )
        alice_user.get_queued_messages()

        await self.server._handle_friend_remove_confirm_selection(
            alice_user,
            "yes",
            self.server._user_states[alice.username],
        )

        assert bob.uuid not in self.db.get_friends(alice.uuid)
        state = self.server._user_states[alice.username]
        assert state["menu"] == "friends_list_menu"
        assert state.get("_stack") == [{"menu": "friends_hub_menu"}]

        alice_messages = alice_user.get_queued_messages()
        assert any(
            msg.get("type") == "speak" and msg.get("key") == "friend-removed-success"
            for msg in alice_messages
        )
        assert any(
            msg.get("type") == "audio"
            and msg.get("asset") == "friend_removed.ogg"
            for msg in alice_messages
        )

        bob_messages = bob_user.get_queued_messages()
        assert any(
            msg.get("type") == "speak" and msg.get("key") == "friend-removed-notify"
            for msg in bob_messages
        )
        assert any(
            msg.get("type") == "audio"
            and msg.get("asset") == "friend_removed.ogg"
            for msg in bob_messages
        )

    @pytest.mark.asyncio
    async def test_remove_friend_confirm_does_not_delete_new_pending_request(self):
        alice, bob = self._create_friendship()
        alice_user = self._make_network_user(alice.username, alice.uuid)
        self.server._user_states[alice.username] = {
            "menu": "friend_actions_menu",
            "target_username": bob.username,
            "_stack": [
                {"menu": "friends_hub_menu"},
                {"menu": "friends_list_menu"},
            ],
        }
        await self.server._handle_friend_actions_selection(
            alice_user,
            "remove_friend",
            self.server._user_states[alice.username],
        )
        alice_user.get_queued_messages()

        self.db.remove_friendship(alice.uuid, bob.uuid)
        self.db.send_friend_request(bob.uuid, alice.uuid)

        await self.server._handle_friend_remove_confirm_selection(
            alice_user,
            "yes",
            self.server._user_states[alice.username],
        )

        assert bob.uuid in self.db.get_pending_incoming_requests(alice.uuid)
        messages = alice_user.get_queued_messages()
        assert any(
            msg.get("type") == "speak" and msg.get("key") == "friend-remove-not-friends"
            for msg in messages
        )
        assert not any(
            msg.get("type") == "audio"
            and msg.get("asset") == "friend_removed.ogg"
            for msg in messages
        )

    def test_block_atomically_removes_direct_social_state(self):
        alice, bob = self._create_friendship()
        self.db.add_notification(alice.uuid, bob.username, "friend_removed")
        self.db.add_notification(bob.uuid, alice.username, "friend_accepted")

        assert self.db.block_user(alice.uuid, bob.uuid) == "blocked"

        assert self.db.get_friends(alice.uuid) == []
        assert self.db.get_pending_incoming_requests(alice.uuid) == []
        assert self.db.get_pending_incoming_requests(bob.uuid) == []
        assert self.db.get_and_clear_notifications(alice.uuid) == []
        assert self.db.get_and_clear_notifications(bob.uuid) == []
        assert self.db.has_blocked(alice.uuid, bob.uuid)
        assert self.db.has_block_between(alice.uuid, bob.uuid)
        assert self.db.count_blocked_users(alice.uuid) == 1
        assert self.db.get_blocked_users(alice.uuid) == [bob.uuid]
        assert self.db.send_friend_request(alice.uuid, bob.uuid) == "blocked_by_you"
        assert self.db.send_friend_request(bob.uuid, alice.uuid) == "blocked"

    def test_unblock_is_directional_and_does_not_restore_relationships(self):
        self.db.create_user("Alice", "hash")
        self.db.create_user("Bob", "hash")
        alice = self.db.get_user("Alice")
        bob = self.db.get_user("Bob")

        assert self.db.block_user(alice.uuid, bob.uuid) == "blocked"
        assert self.db.block_user(bob.uuid, alice.uuid) == "blocked"
        assert self.db.unblock_user(alice.uuid, bob.uuid)

        assert not self.db.has_blocked(alice.uuid, bob.uuid)
        assert self.db.has_blocked(bob.uuid, alice.uuid)
        assert self.db.has_block_between(alice.uuid, bob.uuid)
        assert self.db.get_friends(alice.uuid) == []
        assert self.db.send_friend_request(alice.uuid, bob.uuid) == "blocked"

        assert self.db.unblock_user(bob.uuid, alice.uuid)
        assert not self.db.has_block_between(alice.uuid, bob.uuid)
        assert self.db.send_friend_request(alice.uuid, bob.uuid) == "sent"

    def test_declining_stale_request_cannot_delete_newer_relationship(self):
        self.db.create_user("Alice", "hash")
        self.db.create_user("Bob", "hash")
        alice = self.db.get_user("Alice")
        bob = self.db.get_user("Bob")
        assert self.db.send_friend_request(bob.uuid, alice.uuid) == "sent"

        assert self.db.decline_friend_request(bob.uuid, alice.uuid)
        assert self.db.send_friend_request(alice.uuid, bob.uuid) == "sent"
        assert self.db.send_friend_request(bob.uuid, alice.uuid) == "accepted"

        assert not self.db.decline_friend_request(bob.uuid, alice.uuid)
        assert self.db.get_friends(alice.uuid) == [bob.uuid]

    @pytest.mark.asyncio
    async def test_block_confirmation_replaces_friend_actions_without_notifying_target(self):
        alice, bob = self._create_friendship()
        alice_user = self._make_network_user(alice.username, alice.uuid)
        bob_user = self._make_network_user(bob.username, bob.uuid)
        self.server._user_states[alice.username] = {
            "menu": "friend_actions_menu",
            "target_username": bob.username,
            "_stack": [
                {"menu": "friends_hub_menu"},
                {"menu": "friends_list_menu"},
            ],
        }
        self.server._user_states[bob.username] = {"menu": "friends_hub_menu"}

        await self.server._handle_friend_actions_selection(
            alice_user,
            "block",
            self.server._user_states[alice.username],
        )
        assert self.server._user_states[alice.username]["menu"] == USER_BLOCK_CONFIRM_MENU
        assert bob.uuid in self.db.get_friends(alice.uuid)

        alice_user.get_queued_messages()
        bob_user.get_queued_messages()
        await self.server._handle_user_block_confirm_selection(
            alice_user,
            "yes",
            self.server._user_states[alice.username],
        )

        assert self.db.has_blocked(alice.uuid, bob.uuid)
        assert self.server._user_states[alice.username]["menu"] == "friend_actions_menu"
        alice_messages = alice_user.get_queued_messages()
        assert any(
            message.get("type") == "speak"
            and message.get("key") == "block-success"
            for message in alice_messages
        )
        actions_menu = next(
            message
            for message in reversed(alice_messages)
            if message.get("type") == "menu"
            and message.get("menu_id") == "friend_actions_menu"
        )
        action_ids = [item["id"] for item in actions_menu["items"]]
        assert "unblock" in action_ids
        assert "send_pm" not in action_ids
        assert "remove_friend" not in action_ids
        assert not any(
            message.get("type") == "speak"
            for message in bob_user.get_queued_messages()
        )

    def test_block_controls_cover_request_profile_and_management_menus(self):
        self.db.create_user("Alice", "hash")
        self.db.create_user("Bob", "hash")
        alice = self.db.get_user("Alice")
        bob = self.db.get_user("Bob")
        alice_user = self._make_network_user(alice.username, alice.uuid)
        assert self.db.send_friend_request(bob.uuid, alice.uuid) == "sent"

        self.server._show_friend_request_actions_menu(alice_user, bob.username)
        request_menu = next(
            message
            for message in reversed(alice_user.get_queued_messages())
            if message.get("type") == "menu"
        )
        assert [item["id"] for item in request_menu["items"]] == [
            "view_profile",
            "accept",
            "decline",
            "block",
            "back",
        ]

        assert self.db.block_user(alice.uuid, bob.uuid) == "blocked"
        hub_ids = [
            item.id for item in self.server._get_friends_hub_menu_items(alice_user)
        ]
        assert "blocked_users" in hub_ids
        blocked_items, blocked_page = self.server._get_blocked_users_menu_items(
            alice_user
        )
        assert blocked_page.total == 1
        assert [item.id for item in blocked_items] == ["blocked_Bob", "back"]

        self.server._show_public_profile(alice_user, bob.username)
        profile_menu = next(
            message
            for message in reversed(alice_user.get_queued_messages())
            if message.get("type") == "menu"
            and message.get("menu_id") == "public_profile_menu"
        )
        assert "unblock" in [item["id"] for item in profile_menu["items"]]

    @pytest.mark.asyncio
    async def test_block_prevents_private_messages_and_filters_shared_chat_both_ways(self):
        alice, bob = self._create_friendship()
        self.db.create_user("Cara", "hash")
        cara = self.db.get_user("Cara")
        alice_user = self._make_network_user(alice.username, alice.uuid)
        bob_user = self._make_network_user(bob.username, bob.uuid)
        cara_user = self._make_network_user(cara.username, cara.uuid)
        alice_user.connection.username = alice.username
        bob_user.connection.username = bob.username
        cara_user.connection.username = cara.username
        assert self.db.block_user(alice.uuid, bob.uuid) == "blocked"

        await self.server._deliver_private_message(alice_user, bob.username, "hello")
        await self.server._deliver_private_message(bob_user, alice.username, "hello")
        assert any(
            message.get("key") == "pm-error-blocked"
            for message in alice_user.get_queued_messages()
        )
        assert any(
            message.get("key") == "pm-error-blocked"
            for message in bob_user.get_queued_messages()
        )

        await self.server._handle_chat(
            alice_user.connection,
            {"type": "chat", "convo": "global", "message": "hello all"},
        )
        assert [m["message"] for m in alice_user.connection.sent_messages] == [
            "hello all"
        ]
        assert bob_user.connection.sent_messages == []
        assert [m["message"] for m in cara_user.connection.sent_messages] == [
            "hello all"
        ]

        alice_user.connection.sent_messages.clear()
        bob_user.connection.sent_messages.clear()
        cara_user.connection.sent_messages.clear()
        await self.server._handle_chat(
            bob_user.connection,
            {"type": "chat", "convo": "local", "message": "lobby hello"},
        )
        assert alice_user.connection.sent_messages == []
        assert [m["message"] for m in bob_user.connection.sent_messages] == [
            "lobby hello"
        ]
        assert [m["message"] for m in cara_user.connection.sent_messages] == [
            "lobby hello"
        ]

    @pytest.mark.asyncio
    async def test_private_message_input_uses_shared_mute_and_length_guards(self):
        alice, bob = self._create_friendship()
        alice_user = self._make_network_user(alice.username, alice.uuid)
        bob_user = self._make_network_user(bob.username, bob.uuid)
        alice_user.connection.username = alice.username
        self.server._restore_input_parent = MagicMock()

        self.db.mute_user(alice.username, "Admin", "", None)
        self.server._user_states[alice.username] = {
            "menu": "send_pm_input",
            "target_username": bob.username,
            "_transient": True,
        }
        await self.server._handle_editbox(
            alice_user.connection,
            {"text": "muted message"},
        )
        assert any(
            message.get("key") == "muted-permanent"
            for message in alice_user.get_queued_messages()
        )
        assert not any(
            message.get("key") == "pm-received"
            for message in bob_user.get_queued_messages()
        )

        self.db.unmute_user(alice.username)
        self.server._user_states[alice.username] = {
            "menu": "send_pm_input",
            "target_username": bob.username,
            "_transient": True,
        }
        await self.server._handle_editbox(
            alice_user.connection,
            {"text": "x" * (MAX_CHAT_MESSAGE_LENGTH + 1)},
        )
        assert any(
            message.get("key") == "chat-message-too-long"
            for message in alice_user.get_queued_messages()
        )

    @pytest.mark.asyncio
    async def test_mid_broadcast_block_suppresses_later_recipients(self):
        self.db.create_user("Alice", "hash")
        self.db.create_user("Bob", "hash")
        self.db.create_user("Cara", "hash")
        alice = self.db.get_user("Alice")
        bob = self.db.get_user("Bob")
        cara = self.db.get_user("Cara")
        alice_user = self._make_network_user(alice.username, alice.uuid)
        bob_user = self._make_network_user(bob.username, bob.uuid)
        cara_user = self._make_network_user(cara.username, cara.uuid)

        server = self.server

        class BlockingConnection(MockClient):
            async def send(inner_self, message):
                await super().send(message)
                server._perform_block_user(alice_user, bob.username)

        alice_connection = BlockingConnection("127.0.0.1:12000")
        alice_connection.username = alice.username
        alice_user._connection = alice_connection
        bob_user.connection.username = bob.username
        cara_user.connection.username = cara.username

        await self.server._handle_chat(
            alice_connection,
            {"type": "chat", "convo": "global", "message": "hello"},
        )

        assert [message["message"] for message in alice_connection.sent_messages] == [
            "hello"
        ]
        assert bob_user.connection.sent_messages == []
        assert [
            message["message"] for message in cara_user.connection.sent_messages
        ] == ["hello"]

    @pytest.mark.asyncio
    async def test_block_cancels_pending_table_invite_and_stale_invite_cannot_send(self):
        alice, bob = self._create_friendship()
        alice_user = self._make_network_user(alice.username, alice.uuid)
        bob_user = self._make_network_user(bob.username, bob.uuid)
        self.server._user_states[alice.username] = {"menu": "main_menu"}
        self.server._user_states[bob.username] = {"menu": "main_menu"}
        table = self.server._tables.create_table(
            "crazyeights",
            alice.username,
            alice_user,
        )
        try:
            assert await self.server._send_table_invite(
                alice_user,
                table,
                bob_user,
            )
            invite_task = self.server._pending_invites[bob.username]["task"]
            assert self.server._user_states[bob.username]["menu"] == "table_invite_prompt"

            assert self.server._perform_block_user(alice_user, bob.username)

            assert bob.username not in self.server._pending_invites
            assert invite_task.cancelled() or invite_task.cancelling()
            assert self.server._user_states[bob.username]["menu"] == "main_menu"
            assert not await self.server._send_table_invite(
                alice_user,
                table,
                bob_user,
            )
            assert bob.username not in self.server._pending_invites
        finally:
            table.destroy()


def test_blocks_survive_database_reconnect(tmp_path):
    db_path = tmp_path / "social.db"
    database = Database(db_path)
    database.connect()
    database.create_user("Alice", "hash")
    database.create_user("Bob", "hash")
    alice = database.get_user("Alice")
    bob = database.get_user("Bob")
    assert database.block_user(alice.uuid, bob.uuid) == "blocked"
    database.close()

    reopened = Database(db_path)
    reopened.connect()
    try:
        assert reopened.has_blocked(alice.uuid, bob.uuid)
        assert reopened.get_blocked_users(alice.uuid) == [bob.uuid]
    finally:
        reopened.close()
