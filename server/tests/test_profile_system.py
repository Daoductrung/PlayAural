import pytest
from server.persistence.database import Database
import tempfile
import os

class TestProfileSystem:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_file.close()
        self.db = Database(self.temp_file.name)
        self.db.connect()

    def teardown_method(self):
        self.db.close()
        os.unlink(self.temp_file.name)

    def test_user_creation_with_new_fields(self):
        user = self.db.create_user("profileuser", "hash", email="test@test.com", bio="Hello")
        assert user.email == "test@test.com"
        assert user.bio == "Hello"
        assert user.gender == "Not set"
        assert user.registration_date != ""

    def test_profile_updates(self):
        self.db.create_user("updateuser", "hash")

        self.db.update_user_email("updateuser", "new@test.com")
        self.db.update_user_bio("updateuser", "New Bio")
        self.db.update_user_gender("updateuser", "Male")

        user = self.db.get_user("updateuser")
        assert user.email == "new@test.com"
        assert user.bio == "New Bio"
        assert user.gender == "Male"

    def test_anonymize_on_deletion(self):
        # 1. Create a user
        user = self.db.create_user("deleted_player", "hash")

        # 2. Insert a fake game result for them
        result_id = self.db.save_game_result("pig", "2024-01-01", 100, [(user.uuid, user.username, False)])

        # Verify it exists
        players = self.db.get_game_result_players(result_id)
        assert len(players) == 1
        assert players[0]["player_name"] == "deleted_player"
        assert players[0]["player_id"] == user.uuid

        # 3. Delete the user
        self.db.delete_user("deleted_player")

        # 4. Verify game result is anonymized, not deleted
        players_after = self.db.get_game_result_players(result_id)
        assert len(players_after) == 1
        assert players_after[0]["player_name"] == "Deleted User"
        assert players_after[0]["player_id"] == "deleted"


    @pytest.mark.asyncio
    async def test_email_update_flow(self):
        from server.core.server import Server
        from unittest.mock import MagicMock

        server = Server(db_path=self.temp_file.name)
        server._db = self.db

        self.db.create_user("email_user", "hash")

        user = MagicMock()
        user.username = "email_user"
        user.locale = "en"
        user.uuid = "123"
        server._users["email_user"] = user
        server._user_states["email_user"] = {"menu": "email_input"}

        client = MagicMock()
        client.username = "email_user"

        # 1. Update from empty (direct update)
        packet = {"text": "first@test.com"}
        await server._handle_editbox(client, packet)

        db_user = self.db.get_user("email_user")
        assert db_user.email == "first@test.com"
        user.speak_l.assert_called_with("email-updated", buffer="system")

        # Reset mock
        user.speak_l.reset_mock()

        # 2. Try to update same email (no-op)
        server._user_states["email_user"] = {"menu": "email_input"}
        packet = {"text": "first@test.com"}
        await server._handle_editbox(client, packet)

        user.speak_l.assert_called_with("no-changes-made", buffer="system")

        # Reset mock
        user.speak_l.reset_mock()

        # 3. Change to new email (should show confirmation menu)
        server._user_states["email_user"] = {"menu": "email_input"}
        packet = {"text": "second@test.com"}
        await server._handle_editbox(client, packet)

        # Ensure it didn't update yet
        db_user = self.db.get_user("email_user")
        assert db_user.email == "first@test.com"

        # Verify it went to confirmation menu
        assert server._user_states["email_user"]["menu"] == "email_confirm_menu"
        assert server._user_states["email_user"]["pending_email"] == "second@test.com"

        # 4. Accept confirmation
        await server._handle_email_confirm_selection(user, "yes", server._user_states["email_user"])
        db_user = self.db.get_user("email_user")
        assert db_user.email == "second@test.com"

    @pytest.mark.asyncio
    async def test_email_uniqueness_update(self):
        from server.core.server import Server
        from unittest.mock import MagicMock

        server = Server(db_path=self.temp_file.name)
        server._db = self.db

        # 1. Create two users
        self.db.create_user("user_a", "hash", email="user_a@test.com")
        self.db.create_user("user_b", "hash")

        user = MagicMock()
        user.username = "user_b"
        user.locale = "en"
        user.uuid = "123"
        server._users["user_b"] = user
        server._user_states["user_b"] = {"menu": "email_input"}

        client = MagicMock()
        client.username = "user_b"

        # 2. Try to update user_b's email to user_a's email
        packet = {"text": "user_a@test.com"}
        await server._handle_editbox(client, packet)

        db_user = self.db.get_user("user_b")
        assert db_user.email == ""
        user.speak_l.assert_called_with("error-email-taken", buffer="system")

    @pytest.mark.asyncio
    async def test_bio_length_limit(self):
        from server.core.server import Server
        from unittest.mock import MagicMock

        server = Server(db_path=self.temp_file.name)
        server._db = self.db

        self.db.create_user("bio_user", "hash")

        user = MagicMock()
        user.username = "bio_user"
        user.locale = "en"
        user.uuid = "123"
        user.trust_level = 1
        server._users["bio_user"] = user
        server._user_states["bio_user"] = {"menu": "bio_input"}

        client = MagicMock()
        client.username = "bio_user"

        # 1. Valid bio
        packet = {"text": "A valid bio"}
        await server._handle_editbox(client, packet)

        db_user = self.db.get_user("bio_user")
        assert db_user.bio == "A valid bio"
        user.speak_l.assert_called_with("bio-updated", buffer="system")

        # 2. Too long bio
        server._user_states["bio_user"] = {"menu": "bio_input"}
        packet = {"text": "a" * 251}
        await server._handle_editbox(client, packet)

        db_user = self.db.get_user("bio_user")
        # Should not have updated
        assert db_user.bio == "A valid bio"
        user.speak_l.assert_called_with("error-bio-length", buffer="system")
