"""Tests for the mute CRUD operations in the database."""

import pytest
import uuid
import datetime
from datetime import timedelta
from server.persistence.database import Database


@pytest.fixture
def db():
    """In-memory database for testing."""
    database = Database(":memory:")
    database.connect()
    yield database
    database.close()


def _create_user(db, username, password="test123"):
    """Helper to create a user in the database."""
    user_uuid = str(uuid.uuid4())
    db._conn.execute(
        "INSERT INTO users (uuid, username, password_hash, trust_level, approved) VALUES (?, ?, ?, 1, 1)",
        (user_uuid, username, password),
    )
    db._conn.commit()


class TestMuteUser:
    def test_mute_user_with_expiry(self, db):
        _create_user(db, "alice")
        expires = (datetime.datetime.now() + timedelta(hours=1)).isoformat()
        record = db.mute_user("alice", "admin", "reason-spam", expires)
        assert record.username == "alice"
        assert record.admin_username == "admin"
        assert record.reason == "reason-spam"
        assert record.expires_at == expires

    def test_mute_user_permanent(self, db):
        _create_user(db, "alice")
        record = db.mute_user("alice", "admin", "reason-harassment", None)
        assert record.username == "alice"
        assert record.expires_at is None

    def test_mute_replaces_existing(self, db):
        _create_user(db, "alice")
        db.mute_user("alice", "admin1", "reason-spam", None)
        db.mute_user("alice", "admin2", "reason-harassment", None)
        # Only the latest mute should be active
        record = db.get_active_mute("alice")
        assert record is not None
        assert record.admin_username == "admin2"
        assert record.reason == "reason-harassment"


class TestUnmuteUser:
    def test_unmute_existing(self, db):
        _create_user(db, "alice")
        db.mute_user("alice", "admin", "reason-spam", None)
        result = db.unmute_user("alice")
        assert result is True
        assert db.get_active_mute("alice") is None

    def test_unmute_nonexistent(self, db):
        result = db.unmute_user("alice")
        assert result is False


class TestGetActiveMute:
    def test_no_mute(self, db):
        assert db.get_active_mute("alice") is None

    def test_active_mute(self, db):
        _create_user(db, "alice")
        expires = (datetime.datetime.now() + timedelta(hours=1)).isoformat()
        db.mute_user("alice", "admin", "reason-spam", expires)
        record = db.get_active_mute("alice")
        assert record is not None
        assert record.username == "alice"

    def test_expired_mute_cleaned_up(self, db):
        _create_user(db, "alice")
        expired = (datetime.datetime.now() - timedelta(hours=1)).isoformat()
        db.mute_user("alice", "admin", "reason-spam", expired)
        record = db.get_active_mute("alice")
        assert record is None

    def test_permanent_mute_always_active(self, db):
        _create_user(db, "alice")
        db.mute_user("alice", "admin", "reason-spam", None)
        record = db.get_active_mute("alice")
        assert record is not None
        assert record.expires_at is None


class TestGetAllMutedUsers:
    def test_empty(self, db):
        assert db.get_all_muted_users() == []

    def test_lists_muted(self, db):
        _create_user(db, "alice")
        _create_user(db, "bob")
        db.mute_user("alice", "admin", "spam", None)
        future = (datetime.datetime.now() + timedelta(hours=1)).isoformat()
        db.mute_user("bob", "admin", "spam", future)
        muted = db.get_all_muted_users()
        assert set(muted) == {"alice", "bob"}

    def test_excludes_expired(self, db):
        _create_user(db, "alice")
        _create_user(db, "bob")
        expired = (datetime.datetime.now() - timedelta(hours=1)).isoformat()
        db.mute_user("alice", "admin", "spam", expired)
        db.mute_user("bob", "admin", "spam", None)
        muted = db.get_all_muted_users()
        assert muted == ["bob"]
