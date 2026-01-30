"""Authentication and session management."""

import hashlib
import secrets
from typing import TYPE_CHECKING

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import logging

if TYPE_CHECKING:
    from ..persistence.database import Database, UserRecord


class AuthManager:
    """
    Handles user authentication and session management.

    Uses Argon2 for password hashing (industry standard for secure password storage).
    Supports migration from legacy SHA-256 hashes.
    """

    def __init__(self, database: "Database"):
        self._db = database
        self._sessions: dict[str, str] = {}  # session_token -> username
        self._hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2."""
        return self._hasher.hash(password)

    def _hash_password_sha256(self, password: str) -> str:
        """Legacy SHA-256 hash for migration support."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _is_legacy_hash(self, password_hash: str) -> bool:
        """Check if a hash is a legacy SHA-256 hash (64 hex characters)."""
        return len(password_hash) == 64 and all(c in '0123456789abcdef' for c in password_hash.lower())

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash (supports both Argon2 and legacy SHA-256)."""
        # Try Argon2 first
        try:
            self._hasher.verify(password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHashError):
            pass

        # Fall back to SHA-256 for legacy hashes
        if self._is_legacy_hash(password_hash):
            return self._hash_password_sha256(password) == password_hash

        return False

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate a user.

        Returns True if credentials are valid.
        Also upgrades legacy SHA-256 hashes to Argon2 on successful login.
        """
        user = self._db.get_user(username)
        if not user:
            return False

        if not self.verify_password(password, user.password_hash):
            return False

        # Upgrade legacy hash to Argon2 on successful login
        if self._is_legacy_hash(user.password_hash):
            new_hash = self.hash_password(password)
            self._db.update_user_password(username, new_hash)

        return True

    def register(self, username: str, password: str, locale: str = "en", email: str = "", bio: str = "") -> bool:
        """
        Register a new user.

        Returns True if registration successful, False if username taken.
        The first user ever registered becomes an admin (trust level 2) and is auto-approved.
        """
        if self._db.user_exists(username):
            return False

        # Check if this is the first user - they become developer and are auto-approved
        is_first_user = self._db.get_user_count() == 0
        trust_level = 3 if is_first_user else 1
        approved = True  # Auto-approve all users as requested

        password_hash = self.hash_password(password)
        self._db.create_user(username, password_hash, locale, trust_level, approved, email, bio)

        if is_first_user:
            logging.info(f"User '{username}' is the first user and has been granted developer (trust level 3).")

        return True

    def reset_password(self, username: str, new_password: str) -> bool:
        """
        Reset a user's password.

        Returns True if successful, False if user doesn't exist.
        """
        if not self._db.user_exists(username):
            return False

        password_hash = self.hash_password(new_password)
        self._db.update_user_password(username, password_hash)
        return True

    def get_user(self, username: str) -> "UserRecord | None":
        """Get a user record."""
        return self._db.get_user(username)

    def create_session(self, username: str) -> str:
        """Create a session token for a user."""
        token = secrets.token_hex(32)
        self._sessions[token] = username
        return token

    def validate_session(self, token: str) -> str | None:
        """Validate a session token and return the username."""
        return self._sessions.get(token)

    def invalidate_session(self, token: str) -> None:
        """Invalidate a session token."""
        self._sessions.pop(token, None)

    def invalidate_user_sessions(self, username: str) -> None:
        """Invalidate all sessions for a user."""
        to_remove = [t for t, u in self._sessions.items() if u == username]
        for token in to_remove:
            del self._sessions[token]
