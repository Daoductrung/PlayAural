import pytest
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path
import json
import datetime

from server.core.server import Server
from server.users.network_user import NetworkUser
from server.messages.localization import Localization
from server.persistence.database import Database

@pytest.fixture(autouse=True)
def setup_localization(tmp_path):
    """Setup localization dynamically so we don't rely on existing files."""
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(exist_ok=True)
    en_dir = locales_dir / "en"
    en_dir.mkdir(exist_ok=True)
    (en_dir / "main.ftl").write_text("""
profile = Profile
profile-registration-date = Registration Date: { $date }
profile-username = Username: { $username }
profile-email = Email: { $email }
profile-display-name = Display Name: { $name }
profile-gender = Gender: { $gender }
profile-bio = Bio: { $status }
profile-not-set = Not set
profile-bio-set = Set
profile-bio-edit = Edit Bio
profile-bio-delete = Delete Bio
profile-bio-already-empty = Your bio is already empty.
profile-bio-deleted = Bio deleted successfully.
profile-gender-male = Male
profile-gender-female = Female
profile-gender-non-binary = Non-binary
profile-gender-none = Not set
profile-updated = Profile updated successfully.
profile-error-email = Invalid email address.
profile-error-display-name-length = Name too long.
profile-error-bio-length = Bio too long.
back = Back
""")
    Localization.init(locales_dir)
    Localization.preload_bundles()
    yield
    Localization._bundles.clear()

@pytest.fixture
def test_db():
    db = Database(":memory:")
    db.connect()
    yield db
    db.close()

@pytest.fixture
def mock_server(test_db):
    server = Server(db_path=":memory:")
    server._db = test_db

    # Create test user
    test_db.create_user("testuser", "hash123", "en", 1, True, "test@example.com", "My bio")

    client = MagicMock()
    client.username = "testuser"
    user = NetworkUser("testuser", "en", client)
    user._uuid = test_db.get_user("testuser").uuid
    server._users["testuser"] = user
    return server, user

@pytest.mark.asyncio
async def test_profile_menu_rendering(mock_server):
    server, user = mock_server
    user.show_menu = MagicMock()

    server._show_profile_menu(user)
    user.show_menu.assert_called_once()

    args, kwargs = user.show_menu.call_args
    assert args[0] == "profile_menu"

    items = args[1]
    # Check if read-only ID logic is applied
    assert items[0].id is None  # Registration date
    assert items[1].id is None  # Username
    assert items[2].id == "edit_email"
    assert items[3].id == "edit_display_name"
    assert items[4].id == "edit_gender"
    assert items[5].id == "edit_bio"
    assert items[6].id == "back"

@pytest.mark.asyncio
async def test_profile_bio_delete_empty(mock_server):
    server, user = mock_server
    # Clear bio
    server._db.update_user_profile("testuser", "", "test@example.com", "", "Male")
    user.speak_l = MagicMock()

    await server._handle_bio_menu_selection(user, "bio_delete")
    user.speak_l.assert_called_with("profile-bio-already-empty")

@pytest.mark.asyncio
async def test_profile_bio_delete_success(mock_server):
    server, user = mock_server
    user.speak_l = MagicMock()

    await server._handle_bio_menu_selection(user, "bio_delete")

    user.speak_l.assert_called_with("profile-bio-deleted")
    record = server._db.get_user("testuser")
    assert record.bio == ""

@pytest.mark.asyncio
async def test_profile_gender_update(mock_server):
    server, user = mock_server

    await server._handle_gender_menu_selection(user, "gender_female")

    record = server._db.get_user("testuser")
    assert record.gender == "Female"

@pytest.mark.asyncio
async def test_profile_input_validations(mock_server):
    server, user = mock_server
    user.speak_l = MagicMock()

    state = {"menu": "email_input"}
    packet = {"text": "invalid_email"}

    await server._handle_profile_input(user, packet, state)
    user.speak_l.assert_called_with("profile-error-email")

    # Valid email
    packet = {"text": "valid@email.com"}
    await server._handle_profile_input(user, packet, state)
    record = server._db.get_user("testuser")
    assert record.email == "valid@email.com"

def test_database_profile_migration(tmp_path):
    # Create an old schema manually without profile fields
    db_path = tmp_path / "old_db.sqlite"
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            uuid TEXT NOT NULL,
            locale TEXT DEFAULT 'en',
            preferences_json TEXT DEFAULT '{}',
            trust_level INTEGER DEFAULT 1,
            approved INTEGER DEFAULT 0,
            email TEXT DEFAULT '',
            bio TEXT DEFAULT '',
            motd_version INTEGER DEFAULT 0
        )
    """)
    conn.execute(
        "INSERT INTO users (username, password_hash, uuid) VALUES ('olduser', 'hash', 'uuid1')"
    )
    conn.commit()
    conn.close()

    # Now use the Database class to run migrations
    db = Database(str(db_path))
    db.connect()

    # Check if the new columns are available
    user_record = db.get_user("olduser")
    assert user_record is not None
    assert user_record.display_name == ""
    assert user_record.gender == ""
    assert user_record.registration_date == datetime.datetime.now().strftime("%Y-%m-%d")

    db.close()

@pytest.mark.asyncio
async def test_profile_display_name_length(mock_server):
    server, user = mock_server
    user.speak_l = MagicMock()

    state = {"menu": "display_name_input"}
    packet = {"text": "A" * 31}

    await server._handle_profile_input(user, packet, state)
    user.speak_l.assert_called_with("profile-error-display-name-length")

    # Valid name
    packet = {"text": "Valid Name"}
    await server._handle_profile_input(user, packet, state)
    record = server._db.get_user("testuser")
    assert record.display_name == "Valid Name"
