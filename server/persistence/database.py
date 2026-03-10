"""SQLite database for persistence."""

import sqlite3
import json
from pathlib import Path
from dataclasses import dataclass

from ..tables.table import Table


@dataclass
class UserRecord:
    """A user record from the database."""

    id: int
    username: str
    password_hash: str
    uuid: str  # Persistent unique identifier for stats tracking
    locale: str = "en"
    preferences_json: str = "{}"
    trust_level: int = 1  # 1 = player, 2 = admin
    approved: bool = False  # Whether the account has been approved by an admin
    email: str = ""
    bio: str = ""
    motd_version: int = 0
    gender: str = "Not set"
    registration_date: str = ""


@dataclass
class BanRecord:
    """A ban record from the database."""

    id: int
    username: str
    admin_username: str
    reason_key: str
    issued_at: str
    expires_at: str | None


@dataclass
class SavedTableRecord:
    """A saved table record from the database."""

    id: int
    username: str
    save_name: str
    game_type: str
    game_json: str
    members_json: str
    saved_at: str


class Database:
    """
    SQLite database for PlayAural persistence.

    Stores users and tables as specified in persistence.md.
    """

    def __init__(self, db_path: str | Path = "PlayAural.db"):
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Connect to the database and create tables if needed."""
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()
        self.prune_old_records()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        self._conn.execute("PRAGMA foreign_keys = ON;")
        cursor = self._conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
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
                gender TEXT DEFAULT 'Not set',
                registration_date TEXT DEFAULT ''
            )
        """)

        # Tables table (game tables)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tables (
                table_id TEXT PRIMARY KEY,
                game_type TEXT NOT NULL,
                host TEXT NOT NULL,
                members_json TEXT NOT NULL,
                game_json TEXT,
                status TEXT DEFAULT 'waiting'
            )
        """)

        # Saved tables (user-saved game states)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                save_name TEXT NOT NULL,
                game_type TEXT NOT NULL,
                game_json TEXT NOT NULL,
                members_json TEXT NOT NULL,
                saved_at TEXT NOT NULL
            )
        """)

        # Game results (for statistics)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration_ticks INTEGER,
                custom_data TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_result_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER REFERENCES game_results(id) ON DELETE CASCADE,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                is_bot INTEGER NOT NULL
            )
        """)

        # Indexes for game results
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_results_type
            ON game_results(game_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_results_timestamp
            ON game_results(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_result_players_player
            ON game_result_players(player_id)
        """)

        # Player ratings (for skill-based matchmaking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_ratings (
                player_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                mu REAL NOT NULL,
                sigma REAL NOT NULL,
                PRIMARY KEY (player_id, game_type)
            )
        """)

        # Bans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                admin_username TEXT NOT NULL,
                reason_key TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                expires_at TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bans_username
            ON bans(username)
        """)

        # Player game stats (aggregated stats for leaderboards)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_game_stats (
                player_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                stat_key TEXT NOT NULL,
                stat_value REAL NOT NULL,
                PRIMARY KEY (player_id, game_type, stat_key)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_game_stats_leaderboard
            ON player_game_stats(game_type, stat_key, stat_value DESC)
        """)


        # MOTD table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS motd (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                language TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        # Additional indexes for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_uuid
            ON users(uuid)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_result_players_result
            ON game_result_players(result_id)
        """)

        self._conn.commit()

        # Run migrations for existing databases
        self._run_migrations()

    def _run_migrations(self) -> None:
        """Run database migrations for existing databases."""
        cursor = self._conn.cursor()

        # Check which columns exist in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]

        if "trust_level" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN trust_level INTEGER DEFAULT 1")
            self._conn.commit()

        if "approved" not in columns:
            # Add approved column - existing users are auto-approved
            cursor.execute("ALTER TABLE users ADD COLUMN approved INTEGER DEFAULT 0")
            cursor.execute("UPDATE users SET approved = 1")  # Approve all existing users
            self._conn.commit()

        if "email" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
            self._conn.commit()

        if "bio" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''")
            self._conn.commit()

        if "motd_version" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN motd_version INTEGER DEFAULT 0")
            self._conn.commit()

        if "gender" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT 'Not set'")
            self._conn.commit()

        if "registration_date" not in columns:
            from datetime import datetime
            cursor.execute("ALTER TABLE users ADD COLUMN registration_date TEXT DEFAULT ''")
            # Backfill existing users with current timestamp
            now_iso = datetime.now().isoformat()
            cursor.execute("UPDATE users SET registration_date = ? WHERE registration_date = ''", (now_iso,))
            self._conn.commit()

        # Check if bans table exists (migration for existing databases)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bans'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    admin_username TEXT NOT NULL,
                    reason_key TEXT NOT NULL,
                    issued_at TEXT NOT NULL,
                    expires_at TEXT
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bans_username
                ON bans(username)
            """)
            self._conn.commit()

        # Check if player_game_stats needs backfilling
        cursor.execute("SELECT COUNT(*) FROM player_game_stats")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT COUNT(*) FROM game_results")
            if cursor.fetchone()[0] > 0:
                print("Running one-time backfill of player_game_stats from historical game results...")
                self._backfill_player_game_stats()

    def _backfill_player_game_stats(self) -> None:
        """Backfill player_game_stats from historical game results."""
        from ..game_utils.stats_extractor import StatsExtractor

        cursor = self._conn.cursor()

        # Get all game results
        cursor.execute("SELECT id, game_type, custom_data FROM game_results ORDER BY id ASC")
        results = cursor.fetchall()

        for row in results:
            result_id = row["id"]
            game_type = row["game_type"]
            try:
                custom_data = json.loads(row["custom_data"]) if row["custom_data"] else {}
            except Exception:
                custom_data = {}

            # Get players for this game
            cursor.execute("SELECT player_id, player_name, is_bot FROM game_result_players WHERE result_id = ?", (result_id,))
            players = [(p["player_id"], p["player_name"], bool(p["is_bot"])) for p in cursor.fetchall()]

            # Apply incremental updates exactly as we would for a new game
            from ..game_utils.game_result import GameResult, PlayerResult

            # Reconstruct GameResult
            from datetime import datetime
            gr = GameResult(
                game_type=game_type,
                timestamp=datetime.now().isoformat(),
                duration_ticks=0,
                player_results=[PlayerResult(player_id=pid, player_name=name, is_bot=is_bot) for pid, name, is_bot in players],
                custom_data=custom_data
            )

            # Only process if there are human players
            if not gr.has_human_players():
                continue

            updates = StatsExtractor.extract_incremental_stats(gr)
            for player_id, stats in updates.items():
                for stat_key, stat_value in stats.items():
                    if stat_key.endswith("_high"):
                        # For high scores, use MAX
                        base_key = stat_key[:-5]  # strip '_high'
                        cursor.execute("""
                            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(player_id, game_type, stat_key)
                            DO UPDATE SET stat_value = MAX(stat_value, excluded.stat_value)
                        """, (player_id, game_type, base_key, float(stat_value)))
                    else:
                        # For others (wins, total_score, games_played), use SUM
                        cursor.execute("""
                            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(player_id, game_type, stat_key)
                            DO UPDATE SET stat_value = stat_value + excluded.stat_value
                        """, (player_id, game_type, stat_key, float(stat_value)))

        self._conn.commit()
        print("Backfill completed.")

    def prune_old_records(self) -> None:
        """
        Prune historical bloat from the database to save space.
        - game_results: Older than 30 days.
        - saved_tables: Older than 365 days.
        - bans: Expired more than 30 days ago.
        """
        import datetime
        import logging
        from datetime import timedelta

        now = datetime.datetime.now()
        thirty_days_ago = (now - timedelta(days=30)).isoformat()
        one_year_ago = (now - timedelta(days=365)).isoformat()

        cursor = self._conn.cursor()

        # 1. Prune game_results (ON DELETE CASCADE handles game_result_players)
        cursor.execute("DELETE FROM game_results WHERE timestamp < ?", (thirty_days_ago,))
        deleted_games = cursor.rowcount

        # 2. Prune saved_tables
        cursor.execute("DELETE FROM saved_tables WHERE saved_at < ?", (one_year_ago,))
        deleted_saves = cursor.rowcount

        # 3. Prune expired bans (keep them around for 30 days post-expiry for admin logs, then drop)
        cursor.execute("DELETE FROM bans WHERE expires_at IS NOT NULL AND expires_at < ?", (thirty_days_ago,))
        deleted_bans = cursor.rowcount

        self._conn.commit()

        # Log results
        logger = logging.getLogger("playaural.db.prune")
        if deleted_games > 0 or deleted_saves > 0 or deleted_bans > 0:
             logger.info(f"Database Pruning: Deleted {deleted_games} old game results, {deleted_saves} old saved tables, and {deleted_bans} expired bans.")
        else:
             logger.info("Database Pruning: 0 records deleted (no old data found).")

        # Also print to standard output for explicit CLI visibility on startup
        if deleted_games > 0 or deleted_saves > 0 or deleted_bans > 0:
             print(f"Database Pruning: Cleaned up {deleted_games} game_results, {deleted_saves} saved_tables, and {deleted_bans} bans.")

    # User operations

    def get_user(self, username: str) -> UserRecord | None:
        """Get a user by username."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, uuid, locale, preferences_json, trust_level, approved, email, bio, motd_version, gender, registration_date FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
        if row:
            return UserRecord(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                uuid=row["uuid"],
                locale=row["locale"] or "en",
                preferences_json=row["preferences_json"] or "{}",
                trust_level=row["trust_level"] if row["trust_level"] is not None else 1,
                approved=bool(row["approved"]) if row["approved"] is not None else False,
                email=row["email"] or "",
                bio=row["bio"] or "",
                motd_version=row["motd_version"] if "motd_version" in row.keys() else 0,
                gender=row["gender"] if "gender" in row.keys() else "Not set",
                registration_date=row["registration_date"] if "registration_date" in row.keys() else "",
            )
        return None

    def create_user(
        self, username: str, password_hash: str, locale: str = "en", trust_level: int = 1, approved: bool = False, email: str = "", bio: str = ""
    ) -> UserRecord:
        """Create a new user with a generated UUID."""
        import uuid as uuid_module
        from datetime import datetime
        user_uuid = str(uuid_module.uuid4())
        now_iso = datetime.now().isoformat()
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, uuid, locale, trust_level, approved, email, bio, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (username, password_hash, user_uuid, locale, trust_level, 1 if approved else 0, email, bio, now_iso),
        )
        self._conn.commit()
        return UserRecord(
            id=cursor.lastrowid,
            username=username,
            password_hash=password_hash,
            uuid=user_uuid,
            locale=locale,
            trust_level=trust_level,
            approved=approved,
            email=email,
            bio=bio,
            registration_date=now_iso,
        )

    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    def update_user_locale(self, username: str, locale: str) -> None:
        """Update a user's locale."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET locale = ? WHERE username = ?", (locale, username)
        )
        self._conn.commit()

    def update_user_preferences(self, username: str, preferences_json: str) -> None:
        """Update a user's preferences."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET preferences_json = ? WHERE username = ?",
            (preferences_json, username),
        )
        self._conn.commit()

    def update_user_password(self, username: str, password_hash: str) -> None:
        """Update a user's password hash."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (password_hash, username),
        )
        self._conn.commit()

    def update_user_email(self, username: str, email: str) -> None:
        """Update a user's email."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET email = ? WHERE username = ?",
            (email, username),
        )
        self._conn.commit()

    def update_user_bio(self, username: str, bio: str) -> None:
        """Update a user's bio."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET bio = ? WHERE username = ?",
            (bio, username),
        )
        self._conn.commit()

    def update_user_gender(self, username: str, gender: str) -> None:
        """Update a user's gender."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET gender = ? WHERE username = ?",
            (gender, username),
        )
        self._conn.commit()

    def get_user_count(self) -> int:
        """Get the total number of users in the database."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

    def initialize_trust_levels(self) -> str | None:
        """
        Initialize trust levels for users who don't have one set.

        Sets all users without a trust level to 1 (player).
        If there's exactly one user and they have no trust level, sets them to 2 (admin).

        Returns:
            The username of the user promoted to admin, or None if no promotion occurred.
        """
        cursor = self._conn.cursor()

        # Check if there's exactly one user with no trust level set
        cursor.execute("SELECT id, username FROM users WHERE trust_level IS NULL")
        users_without_trust = cursor.fetchall()

        promoted_user = None

        if len(users_without_trust) == 1:
            # Check if this is the only user in the database
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            if total_users == 1:
                # First and only user - make them developer
                username = users_without_trust[0]["username"]
                cursor.execute(
                    "UPDATE users SET trust_level = 3 WHERE id = ?",
                    (users_without_trust[0]["id"],),
                )
                promoted_user = username

        # Set all remaining users without trust level to 1 (player)
        cursor.execute("UPDATE users SET trust_level = 1 WHERE trust_level IS NULL")
        self._conn.commit()

        return promoted_user

    def update_user_trust_level(self, username: str, trust_level: int) -> None:
        """Update a user's trust level."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET trust_level = ? WHERE username = ?",
            (trust_level, username),
        )
        self._conn.commit()

    def update_user_motd_version(self, username: str, motd_version: int) -> None:
        """Update a user's motd version."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET motd_version = ? WHERE username = ?",
            (motd_version, username),
        )
        self._conn.commit()

    def get_pending_users(self) -> list[UserRecord]:
        """Get all users who are not yet approved."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, uuid, locale, preferences_json, trust_level, approved, email, bio, motd_version, gender, registration_date FROM users WHERE approved = 0"
        )
        users = []
        for row in cursor.fetchall():
            users.append(UserRecord(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                uuid=row["uuid"],
                locale=row["locale"] or "en",
                preferences_json=row["preferences_json"] or "{}",
                trust_level=row["trust_level"] if row["trust_level"] is not None else 1,
                approved=False,
                email=row["email"] or "",
                bio=row["bio"] or "",
                motd_version=row["motd_version"] if "motd_version" in row.keys() else 0,
                gender=row["gender"] if "gender" in row.keys() else "Not set",
                registration_date=row["registration_date"] if "registration_date" in row.keys() else "",
            ))
        return users

    def approve_user(self, username: str) -> bool:
        """Approve a user account. Returns True if user was found and approved."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET approved = 1 WHERE username = ?",
            (username,),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def delete_user(self, username: str) -> bool:
        """Delete a user account and safely clean up orphaned metadata. Returns True if user was found and deleted."""
        user = self.get_user(username)
        if not user:
            return False

        cursor = self._conn.cursor()

        # Delete dependent data using explicit soft keys (username/uuid)
        cursor.execute("DELETE FROM player_game_stats WHERE player_id = ?", (user.uuid,))
        cursor.execute("DELETE FROM player_ratings WHERE player_id = ?", (user.uuid,))
        cursor.execute("DELETE FROM saved_tables WHERE username = ?", (username,))
        cursor.execute("DELETE FROM bans WHERE username = ?", (username,))

        # Anonymize historical game data rather than deleting it to preserve integrity
        # for other players in those matches.
        cursor.execute(
            "UPDATE game_result_players SET player_id = 'deleted', player_name = 'Deleted User' WHERE player_id = ?",
            (user.uuid,)
        )

        # Finally delete the user
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))

        self._conn.commit()
        return cursor.rowcount > 0

    def get_non_admin_users(self) -> list[UserRecord]:
        """Get all approved users who are not admins (trust_level < 2)."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, uuid, locale, preferences_json, trust_level, approved, email, bio, motd_version, gender, registration_date FROM users WHERE approved = 1 AND trust_level < 2 ORDER BY username"
        )
        users = []
        for row in cursor.fetchall():
            users.append(UserRecord(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                uuid=row["uuid"],
                locale=row["locale"] or "en",
                preferences_json=row["preferences_json"] or "{}",
                trust_level=row["trust_level"] if row["trust_level"] is not None else 1,
                approved=True,
                email=row["email"] or "",
                bio=row["bio"] or "",
                motd_version=row["motd_version"] if "motd_version" in row.keys() else 0,
                gender=row["gender"] if "gender" in row.keys() else "Not set",
                registration_date=row["registration_date"] if "registration_date" in row.keys() else "",
            ))
        return users

    def get_admin_users(self) -> list[UserRecord]:
        """Get all users who are admins (trust_level >= 2)."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, uuid, locale, preferences_json, trust_level, approved, email, bio, motd_version, gender, registration_date FROM users WHERE trust_level >= 2 ORDER BY username"
        )
        users = []
        for row in cursor.fetchall():
            users.append(UserRecord(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                uuid=row["uuid"],
                locale=row["locale"] or "en",
                preferences_json=row["preferences_json"] or "{}",
                trust_level=row["trust_level"],
                approved=bool(row["approved"]) if row["approved"] is not None else False,
                email=row["email"] or "",
                bio=row["bio"] or "",
                motd_version=row["motd_version"] if "motd_version" in row.keys() else 0,
                gender=row["gender"] if "gender" in row.keys() else "Not set",
                registration_date=row["registration_date"] if "registration_date" in row.keys() else "",
            ))
        return users


    # MOTD operations

    def get_highest_motd_version(self) -> int:
        """Get the highest motd version currently active."""
        cursor = self._conn.cursor()
        try:
            cursor.execute("SELECT MAX(version) FROM motd")
            row = cursor.fetchone()
            return row[0] if row[0] is not None else 0
        except sqlite3.OperationalError:
            return 0

    def get_motd(self, version: int, language: str) -> str | None:
        """Get a motd message for a specific version and language."""
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                "SELECT message FROM motd WHERE version = ? AND language = ?",
                (version, language)
            )
            row = cursor.fetchone()
            if row:
                return row["message"]

            # Fallback to English
            cursor.execute(
                "SELECT message FROM motd WHERE version = ? AND language = 'en'",
                (version,)
            )
            row = cursor.fetchone()
            if row:
                return row["message"]

            # Fallback to any language
            cursor.execute(
                "SELECT message FROM motd WHERE version = ? LIMIT 1",
                (version,)
            )
            row = cursor.fetchone()
            if row:
                return row["message"]
            return None
        except sqlite3.OperationalError:
            return None

    def get_active_motd(self, language: str) -> tuple[int, str] | None:
        """Get the active (highest version) motd and message for a language."""
        version = self.get_highest_motd_version()
        if version == 0:
            return None

        message = self.get_motd(version, language)
        if message:
            return (version, message)
        return None

    def create_motd(self, version: int, translations: dict[str, str]) -> None:
        """Create a new motd version with translations and delete old versions."""
        cursor = self._conn.cursor()

        # Delete existing MOTDs
        self.delete_motd()

        for language, message in translations.items():
            cursor.execute(
                "INSERT INTO motd (version, language, message) VALUES (?, ?, ?)",
                (version, language, message)
            )

        self._conn.commit()

    def delete_motd(self) -> None:
        """Delete all motd records."""
        cursor = self._conn.cursor()
        try:
            cursor.execute("DELETE FROM motd")
            self._conn.commit()
        except sqlite3.OperationalError:
            pass

    # Ban operations

    def ban_user(self, username: str, admin_username: str, reason_key: str, expires_at: str | None) -> BanRecord:
        """Ban a user."""
        from datetime import datetime
        issued_at = datetime.now().isoformat()
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO bans (username, admin_username, reason_key, issued_at, expires_at) VALUES (?, ?, ?, ?, ?)",
            (username, admin_username, reason_key, issued_at, expires_at),
        )
        self._conn.commit()
        return BanRecord(
            id=cursor.lastrowid,
            username=username,
            admin_username=admin_username,
            reason_key=reason_key,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def unban_user(self, username: str) -> bool:
        """Unban a user by removing their active bans. Returns True if unbanned."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM bans WHERE username = ?", (username,))
        self._conn.commit()
        return cursor.rowcount > 0

    def get_active_ban(self, username: str) -> BanRecord | None:
        """Get the active ban for a user, if any. Clears expired bans."""
        from datetime import datetime
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, username, admin_username, reason_key, issued_at, expires_at FROM bans WHERE username = ? ORDER BY issued_at DESC",
            (username,),
        )

        now = datetime.now().isoformat()
        active_ban = None
        expired_ids = []

        for row in cursor.fetchall():
            expires_at = row["expires_at"]
            if expires_at and expires_at <= now:
                expired_ids.append(row["id"])
            elif not active_ban:
                # Keep the most recent active ban
                active_ban = BanRecord(
                    id=row["id"],
                    username=row["username"],
                    admin_username=row["admin_username"],
                    reason_key=row["reason_key"],
                    issued_at=row["issued_at"],
                    expires_at=row["expires_at"],
                )
            else:
                # If there are multiple active bans, we only return one but we might want to clean up others?
                # Actually, standard logic is just return the first active one we find
                pass

        # Cleanup expired bans
        if expired_ids:
            for ban_id in expired_ids:
                cursor.execute("DELETE FROM bans WHERE id = ?", (ban_id,))
            self._conn.commit()

        return active_ban

    def get_all_banned_users(self) -> list[str]:
        """Get a list of all currently banned usernames."""
        from datetime import datetime
        now = datetime.now().isoformat()
        cursor = self._conn.cursor()
        # Find usernames where they have at least one active ban
        cursor.execute(
            "SELECT DISTINCT username FROM bans WHERE expires_at IS NULL OR expires_at > ?",
            (now,)
        )
        return [row["username"] for row in cursor.fetchall()]

    # Table operations

    def save_table(self, table: Table) -> None:
        """Save a table to the database."""
        cursor = self._conn.cursor()

        # Serialize members
        members_json = json.dumps(
            [
                {"username": m.username, "is_spectator": m.is_spectator}
                for m in table.members
            ]
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO tables (table_id, game_type, host, members_json, game_json, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                table.table_id,
                table.game_type,
                table.host,
                members_json,
                table.game_json,
                table.status,
            ),
        )
        self._conn.commit()

    def load_table(self, table_id: str) -> Table | None:
        """Load a table from the database."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM tables WHERE table_id = ?", (table_id,))
        row = cursor.fetchone()
        if not row:
            return None

        # Deserialize members
        members_data = json.loads(row["members_json"])
        from ..tables.table import TableMember

        members = [
            TableMember(username=m["username"], is_spectator=m["is_spectator"])
            for m in members_data
        ]

        return Table(
            table_id=row["table_id"],
            game_type=row["game_type"],
            host=row["host"],
            members=members,
            game_json=row["game_json"],
            status=row["status"],
        )

    def load_all_tables(self) -> list[Table]:
        """Load all tables from the database."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT table_id FROM tables")
        tables = []
        for row in cursor.fetchall():
            table = self.load_table(row["table_id"])
            if table:
                tables.append(table)
        return tables

    def delete_table(self, table_id: str) -> None:
        """Delete a table from the database."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM tables WHERE table_id = ?", (table_id,))
        self._conn.commit()

    def delete_all_tables(self) -> None:
        """Delete all tables from the database."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM tables")
        self._conn.commit()

    def save_all_tables(self, tables: list[Table]) -> None:
        """Save multiple tables."""
        for table in tables:
            self.save_table(table)

    # Saved table operations (user-saved game states)

    def save_user_table(
        self,
        username: str,
        save_name: str,
        game_type: str,
        game_json: str,
        members_json: str,
    ) -> SavedTableRecord:
        """Save a table state to a user's saved tables."""
        from datetime import datetime

        saved_at = datetime.now().isoformat()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO saved_tables (username, save_name, game_type, game_json, members_json, saved_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (username, save_name, game_type, game_json, members_json, saved_at),
        )
        self._conn.commit()

        return SavedTableRecord(
            id=cursor.lastrowid,
            username=username,
            save_name=save_name,
            game_type=game_type,
            game_json=game_json,
            members_json=members_json,
            saved_at=saved_at,
        )

    def get_user_saved_tables(self, username: str) -> list[SavedTableRecord]:
        """Get all saved tables for a user."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM saved_tables WHERE username = ? ORDER BY saved_at DESC",
            (username,),
        )
        records = []
        for row in cursor.fetchall():
            records.append(
                SavedTableRecord(
                    id=row["id"],
                    username=row["username"],
                    save_name=row["save_name"],
                    game_type=row["game_type"],
                    game_json=row["game_json"],
                    members_json=row["members_json"],
                    saved_at=row["saved_at"],
                )
            )
        return records

    def get_saved_table(self, save_id: int) -> SavedTableRecord | None:
        """Get a saved table by ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM saved_tables WHERE id = ?", (save_id,))
        row = cursor.fetchone()
        if not row:
            return None

        return SavedTableRecord(
            id=row["id"],
            username=row["username"],
            save_name=row["save_name"],
            game_type=row["game_type"],
            game_json=row["game_json"],
            members_json=row["members_json"],
            saved_at=row["saved_at"],
        )

    def delete_saved_table(self, save_id: int) -> None:
        """Delete a saved table."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM saved_tables WHERE id = ?", (save_id,))
        self._conn.commit()

    # Game result operations (statistics)

    def save_game_result(
        self,
        game_type: str,
        timestamp: str,
        duration_ticks: int,
        players: list[tuple[str, str, bool]],  # (player_id, player_name, is_bot)
        custom_data: dict | None = None,
    ) -> int:
        """
        Save a game result to the database.

        Args:
            game_type: The game type identifier
            timestamp: ISO format timestamp
            duration_ticks: Game duration in ticks
            players: List of (player_id, player_name, is_bot) tuples
            custom_data: Game-specific result data

        Returns:
            The result ID
        """
        cursor = self._conn.cursor()

        # Insert the main result record
        cursor.execute(
            """
            INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data)
            VALUES (?, ?, ?, ?)
            """,
            (
                game_type,
                timestamp,
                duration_ticks,
                json.dumps(custom_data) if custom_data else None,
            ),
        )
        result_id = cursor.lastrowid

        # Insert player records
        for player_id, player_name, is_bot in players:
            cursor.execute(
                """
                INSERT INTO game_result_players (result_id, player_id, player_name, is_bot)
                VALUES (?, ?, ?, ?)
                """,
                (result_id, player_id, player_name, 1 if is_bot else 0),
            )

        # Update player_game_stats
        from ..game_utils.game_result import GameResult, PlayerResult
        from ..game_utils.stats_extractor import StatsExtractor

        # We temporarily build a GameResult just for the extractor
        from datetime import datetime
        gr = GameResult(
            game_type=game_type,
            timestamp=datetime.now().isoformat(),
            duration_ticks=duration_ticks,
            player_results=[PlayerResult(player_id=pid, player_name=name, is_bot=is_bot) for pid, name, is_bot in players],
            custom_data=custom_data or {}
        )

        if gr.has_human_players():
            updates = StatsExtractor.extract_incremental_stats(gr)
            for p_id, stats in updates.items():
                for stat_key, stat_value in stats.items():
                    if stat_key.endswith("_high"):
                        # For high scores, use MAX
                        base_key = stat_key[:-5]  # strip '_high'
                        cursor.execute("""
                            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(player_id, game_type, stat_key)
                            DO UPDATE SET stat_value = MAX(stat_value, excluded.stat_value)
                        """, (p_id, game_type, base_key, float(stat_value)))
                    else:
                        # For others (wins, total_score, games_played), use SUM
                        cursor.execute("""
                            INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(player_id, game_type, stat_key)
                            DO UPDATE SET stat_value = stat_value + excluded.stat_value
                        """, (p_id, game_type, stat_key, float(stat_value)))

        self._conn.commit()
        return result_id

    def get_player_game_history(
        self,
        player_id: str,
        game_type: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        Get a player's game history.

        Args:
            player_id: The player ID to look up
            game_type: Optional filter by game type
            limit: Maximum number of results

        Returns:
            List of game result dictionaries
        """
        cursor = self._conn.cursor()

        if game_type:
            cursor.execute(
                """
                SELECT gr.id, gr.game_type, gr.timestamp, gr.duration_ticks, gr.custom_data
                FROM game_results gr
                INNER JOIN game_result_players grp ON gr.id = grp.result_id
                WHERE grp.player_id = ? AND gr.game_type = ?
                ORDER BY gr.timestamp DESC
                LIMIT ?
                """,
                (player_id, game_type, limit),
            )
        else:
            cursor.execute(
                """
                SELECT gr.id, gr.game_type, gr.timestamp, gr.duration_ticks, gr.custom_data
                FROM game_results gr
                INNER JOIN game_result_players grp ON gr.id = grp.result_id
                WHERE grp.player_id = ?
                ORDER BY gr.timestamp DESC
                LIMIT ?
                """,
                (player_id, limit),
            )

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "game_type": row["game_type"],
                "timestamp": row["timestamp"],
                "duration_ticks": row["duration_ticks"],
                "custom_data": json.loads(row["custom_data"]) if row["custom_data"] else {},
            })
        return results

    def get_game_result_players(self, result_id: int) -> list[dict]:
        """Get all players for a specific game result."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT player_id, player_name, is_bot
            FROM game_result_players
            WHERE result_id = ?
            """,
            (result_id,),
        )
        return [
            {
                "player_id": row["player_id"],
                "player_name": row["player_name"],
                "is_bot": bool(row["is_bot"]),
            }
            for row in cursor.fetchall()
        ]

    def get_game_stats(self, game_type: str, limit: int | None = None) -> list[tuple]:
        """
        Get game results for a game type.

        Args:
            game_type: The game type to query
            limit: Optional maximum number of results

        Returns:
            List of tuples: (id, game_type, timestamp, duration_ticks, custom_data)
        """
        cursor = self._conn.cursor()

        if limit:
            cursor.execute(
                """
                SELECT id, game_type, timestamp, duration_ticks, custom_data
                FROM game_results
                WHERE game_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (game_type, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, game_type, timestamp, duration_ticks, custom_data
                FROM game_results
                WHERE game_type = ?
                ORDER BY timestamp DESC
                """,
                (game_type,),
            )

        return [
            (row["id"], row["game_type"], row["timestamp"], row["duration_ticks"], row["custom_data"])
            for row in cursor.fetchall()
        ]

    def get_game_stats_aggregate(self, game_type: str) -> dict:
        """
        Get aggregate statistics for a game type.

        Returns:
            Dictionary with total_games, total_duration_ticks, etc.
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_games,
                SUM(duration_ticks) as total_duration,
                AVG(duration_ticks) as avg_duration
            FROM game_results
            WHERE game_type = ?
            """,
            (game_type,),
        )
        row = cursor.fetchone()
        return {
            "total_games": row["total_games"] or 0,
            "total_duration_ticks": row["total_duration"] or 0,
            "avg_duration_ticks": row["avg_duration"] or 0,
        }

    def get_player_stats(self, player_id: str, game_type: str | None = None) -> dict:
        """
        Get statistics for a player.

        Args:
            player_id: The player ID
            game_type: Optional filter by game type

        Returns:
            Dictionary with games_played, etc.
        """
        cursor = self._conn.cursor()

        if game_type:
            cursor.execute(
                """
                SELECT COUNT(*) as games_played
                FROM game_result_players grp
                INNER JOIN game_results gr ON grp.result_id = gr.id
                WHERE grp.player_id = ? AND gr.game_type = ?
                """,
                (player_id, game_type),
            )
        else:
            cursor.execute(
                """
                SELECT COUNT(*) as games_played
                FROM game_result_players
                WHERE player_id = ?
                """,
                (player_id,),
            )

        row = cursor.fetchone()
        return {
            "games_played": row["games_played"] or 0,
        }

    def get_top_player_game_stats(self, game_type: str, stat_key: str, limit: int = 10) -> list[tuple[str, str, float]]:
        """
        Get the top players for a specific stat in a specific game.
        Returns list of (player_id, player_name, stat_value).
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT pgs.player_id, u.username as player_name, pgs.stat_value
            FROM player_game_stats pgs
            LEFT JOIN users u ON pgs.player_id = u.uuid
            WHERE pgs.game_type = ? AND pgs.stat_key = ?
            ORDER BY pgs.stat_value DESC
            LIMIT ?
            """,
            (game_type, stat_key, limit),
        )
        return [(row["player_id"], row["player_name"] or row["player_id"], row["stat_value"]) for row in cursor.fetchall()]

    def get_top_wins_with_losses(self, game_type: str, limit: int = 10) -> list[tuple[str, str, float, float]]:
        """
        Get the top players by wins along with their losses to avoid N+1 queries.
        Returns list of (player_id, player_name, wins, losses).
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT
                pgs_w.player_id,
                u.username as player_name,
                pgs_w.stat_value as wins,
                COALESCE(pgs_l.stat_value, 0) as losses
            FROM player_game_stats pgs_w
            LEFT JOIN player_game_stats pgs_l
                ON pgs_w.player_id = pgs_l.player_id AND pgs_w.game_type = pgs_l.game_type AND pgs_l.stat_key = 'losses'
            LEFT JOIN users u ON pgs_w.player_id = u.uuid
            WHERE pgs_w.game_type = ? AND pgs_w.stat_key = 'wins'
            ORDER BY pgs_w.stat_value DESC
            LIMIT ?
            """,
            (game_type, limit),
        )
        return [(row["player_id"], row["player_name"] or row["player_id"], row["wins"], row["losses"]) for row in cursor.fetchall()]

    def get_top_ratio_stats(self, game_type: str, num_key: str, denom_key: str) -> list[tuple[str, str, float, float]]:
        """
        Get numerator and denominator stats for all players for a game type, returning them so they can be sorted.
        Returns list of (player_id, player_name, total_num, total_denom).
        """
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT p_num.player_id, u.username, p_num.stat_value, p_denom.stat_value
            FROM player_game_stats p_num
            JOIN player_game_stats p_denom
                ON p_num.player_id = p_denom.player_id
               AND p_num.game_type = p_denom.game_type
               AND p_denom.stat_key = ?
            LEFT JOIN users u ON p_num.player_id = u.uuid
            WHERE p_num.game_type = ? AND p_num.stat_key = ?
        """, (denom_key, game_type, num_key))
        return [(row[0], row[1] or row[0], row[2], row[3]) for row in cursor.fetchall()]

    def get_user_name_by_uuid(self, uuid: str) -> str | None:
        """Look up a username by UUID efficiently."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT username FROM users WHERE uuid = ?", (uuid,))
        row = cursor.fetchone()
        return row["username"] if row else None

    def get_all_player_game_stats(self, player_id: str, game_type: str) -> dict[str, float]:
        """Get all pre-calculated stats for a specific player and game."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT stat_key, stat_value
            FROM player_game_stats
            WHERE player_id = ? AND game_type = ?
            """,
            (player_id, game_type)
        )
        return {row["stat_key"]: row["stat_value"] for row in cursor.fetchall()}

    # Player rating operations

    def get_player_rating(
        self, player_id: str, game_type: str
    ) -> tuple[float, float] | None:
        """
        Get a player's rating for a game type.

        Returns:
            (mu, sigma) tuple or None if no rating exists
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT mu, sigma FROM player_ratings
            WHERE player_id = ? AND game_type = ?
            """,
            (player_id, game_type),
        )
        row = cursor.fetchone()
        if row:
            return (row["mu"], row["sigma"])
        return None

    def set_player_rating(
        self, player_id: str, game_type: str, mu: float, sigma: float
    ) -> None:
        """Set or update a player's rating for a game type."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO player_ratings (player_id, game_type, mu, sigma)
            VALUES (?, ?, ?, ?)
            """,
            (player_id, game_type, mu, sigma),
        )
        self._conn.commit()

    def get_rating_leaderboard(
        self, game_type: str, limit: int = 10
    ) -> list[tuple[str, str, float, float]]:
        """
        Get the rating leaderboard for a game type.

        Returns:
            List of (player_id, player_name, mu, sigma) tuples sorted by ordinal descending
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT pr.player_id, u.username as player_name, pr.mu, pr.sigma,
                   (pr.mu - 3 * pr.sigma) as ordinal
            FROM player_ratings pr
            LEFT JOIN users u ON pr.player_id = u.uuid
            WHERE pr.game_type = ?
            ORDER BY ordinal DESC
            LIMIT ?
            """,
            (game_type, limit),
        )
        return [(row["player_id"], row["player_name"] or row["player_id"], row["mu"], row["sigma"]) for row in cursor.fetchall()]
