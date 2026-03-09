import pytest
import sqlite3
from pathlib import Path
from server.persistence.database import Database

@pytest.fixture
def db(tmp_path: Path) -> Database:
    db_path = tmp_path / "test_playaural.db"
    database = Database(db_path)
    database.connect()

    # Init users
    database.create_user("admin", "hash", "en", 2, True)
    database.create_user("user1", "hash", "en", 1, True)
    database.create_user("user2", "hash", "vi", 1, True)

    yield database
    database.close()

def test_motd_creation_and_retrieval(db: Database):
    assert db.get_highest_motd_version() == 0
    assert db.get_active_motd("en") is None

    translations = {
        "en": "Hello world",
        "vi": "Xin chao"
    }

    db.create_motd(1, translations)
    assert db.get_highest_motd_version() == 1

    # Check English
    en_motd = db.get_active_motd("en")
    assert en_motd[0] == 1
    assert en_motd[1] == "Hello world"

    # Check Vietnamese
    vi_motd = db.get_active_motd("vi")
    assert vi_motd[0] == 1
    assert vi_motd[1] == "Xin chao"

    # Check fallback to en for unknown language
    es_motd = db.get_active_motd("es")
    assert es_motd[0] == 1
    assert es_motd[1] == "Hello world"

    # Check fallback to random if en doesn't exist
    db.delete_motd()
    db.create_motd(1, {"vi": "Xin chao"})
    fr_motd = db.get_active_motd("fr")
    assert fr_motd[1] == "Xin chao"

def test_motd_version_increment_after_user_ack(db: Database):
    # Set motd_version for a user to simulate they read an old MOTD
    db.update_user_motd_version("user1", 6)

    user = db.get_user("user1")
    assert user.motd_version == 6

    # Create MOTD with version 7 manually
    db.create_motd(7, {"en": "Testing 2"})
    assert db.get_highest_motd_version() == 7

def test_motd_deletion(db: Database):
    db.create_motd(1, {"en": "To be deleted"})
    assert db.get_highest_motd_version() > 0

    db.delete_motd()
    assert db.get_highest_motd_version() == 0
    assert db.get_active_motd("en") is None
