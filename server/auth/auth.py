"""Authentication and session management."""

import re
import secrets
from typing import TYPE_CHECKING

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import logging

try:
    from ..game_utils.bot_names import is_reserved_bot_name
    from ..users.identity import username_validation_error
except ImportError:  # pragma: no cover - supports direct server/cli imports
    from game_utils.bot_names import is_reserved_bot_name
    from users.identity import username_validation_error

if TYPE_CHECKING:
    from ..persistence.database import Database, UserRecord


class AuthManager:
    """
    Handles user authentication and session management.

    Uses Argon2 for password hashing (industry standard for secure password storage).
    """

    def __init__(self, database: "Database"):
        self._db = database
        self._sessions: dict[str, str] = {}  # session_token -> username
        self._hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2."""
        return self._hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its Argon2 hash."""
        try:
            self._hasher.verify(password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHashError):
            return False

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate a user.

        Returns True if credentials are valid.
        """
        user = self._db.get_user(username)
        if not user:
            return False

        return self.verify_password(password, user.password_hash)

    def register(self, username: str, password: str, locale: str = "en", email: str = "", bio: str = "") -> str:
        """
        Register a new user.

        Returns "ok" on success, or an error key:
        - "username_taken" if the username already exists
        - "username_reserved_bot" if the username is reserved for generated bots
        - "username_length" or "username_invalid_chars" if the name is invalid
        - "db_error" if the INSERT failed unexpectedly
        The first user ever registered becomes a developer (trust level 3) and is auto-approved.
        """
        validation_error = username_validation_error(username)
        if validation_error:
            return validation_error
        if self._db.user_exists(username):
            return "username_taken"
        if is_reserved_bot_name(username):
            return "username_reserved_bot"

        password_hash = self.hash_password(password)
        result = self._db.create_user(
            username,
            password_hash,
            locale,
            1,
            True,
            email,
            bio,
            promote_first_user=True,
        )
        if result is None:
            # Another connection may have claimed the same lookup key while
            # this process was hashing the password.
            if self._db.user_exists(username):
                return "username_taken"
            return "db_error"

        if result.trust_level >= 3:
            logging.info(f"User '{username}' is the first user and has been granted developer (trust level 3).")

        return "ok"

    def generate_reset_token(self, user_uuid: str) -> str:
        """
        Generate a secure 6-digit numeric reset token, hash it, and save it.
        Returns the plaintext token.
        """
        from datetime import datetime, timedelta

        # Generate cryptographically secure 6-digit numeric token
        token = f"{secrets.randbelow(1000000):06d}"

        # Hash token for storage
        token_hash = self._hasher.hash(token)

        # Set expiry to 15 minutes from now
        expires_at = (datetime.now() + timedelta(minutes=15)).isoformat()

        self._db.save_password_reset_token(user_uuid, token_hash, expires_at)

        return token

    def verify_reset_token(self, user_uuid: str, token: str) -> bool:
        """
        Verify if a provided plaintext token matches the stored active hash.
        """
        record = self._db.get_password_reset_token(user_uuid)
        if not record:
            return False

        try:
            self._hasher.verify(record["token_hash"], token)
            return True
        except (VerifyMismatchError, InvalidHashError):
            return False

    def clear_reset_token(self, user_uuid: str) -> None:
        """Clear the reset token after successful use."""
        self._db.delete_password_reset_token(user_uuid)

    def reset_password(self, username: str, new_password: str) -> bool:
        """
        Reset a user's password.

        Returns True if successful, False if user doesn't exist.
        """
        user = self._db.get_user(username)
        if not user:
            return False

        password_hash = self.hash_password(new_password)
        self._db.update_user_password(user.username, password_hash)
        return True

    def get_user(self, username: str) -> "UserRecord | None":
        """Get a user record."""
        return self._db.get_user(username)

    def create_session(self, username: str) -> str:
        """Create a session token for a user, normalizing to the canonical database username."""
        user = self._db.get_user(username)
        if not user:
            raise ValueError("Cannot create a session for an unresolved username")
        token = secrets.token_hex(32)
        self._sessions[token] = user.username
        return token

    def validate_session(self, token: str) -> str | None:
        """Validate a session token and return the username."""
        return self._sessions.get(token)

    def invalidate_session(self, token: str) -> None:
        """Invalidate a session token."""
        self._sessions.pop(token, None)

    def invalidate_user_sessions(self, username: str) -> None:
        """Invalidate all sessions for a user."""
        user = self._db.get_user(username)
        canonical_username = user.username if user else username
        to_remove = [
            token
            for token, session_username in self._sessions.items()
            if session_username == canonical_username
        ]
        for token in to_remove:
            del self._sessions[token]

def is_valid_email(email: str | None) -> bool:
    """Check if an email is valid using a standard regex format."""
    if not email:
        return False
    # Standard email format allowing custom domains
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))
