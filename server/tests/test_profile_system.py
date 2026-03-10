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
