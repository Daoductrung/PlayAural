import re

with open("server/persistence/database.py", "r") as f:
    content = f.read()

# 1. Add motd table creation
motd_table_sql = """
        # MOTD table
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS motd (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                language TEXT NOT NULL,
                message TEXT NOT NULL
            )
        \"\"\")

        # Additional indexes for fast lookups"""
content = content.replace("        # Additional indexes for fast lookups", motd_table_sql)

# 2. Add motd_version to migration
migration_sql = """        if "bio" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''")
            self._conn.commit()

        if "motd_version" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN motd_version INTEGER DEFAULT 0")
            self._conn.commit()"""
content = content.replace("        if \"bio\" not in columns:\n            cursor.execute(\"ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''\")\n            self._conn.commit()", migration_sql)

# 3. Add motd_version to UserRecord
user_record_orig = """@dataclass
class UserRecord:
    \"\"\"A user record from the database.\"\"\"

    id: int
    username: str
    password_hash: str
    uuid: str  # Persistent unique identifier for stats tracking
    locale: str = "en"
    preferences_json: str = "{}"
    trust_level: int = 1  # 1 = player, 2 = admin
    approved: bool = False  # Whether the account has been approved by an admin
    email: str = ""
    bio: str = \"\""""
user_record_new = user_record_orig + "\n    motd_version: int = 0"
content = content.replace(user_record_orig, user_record_new)

# 4. Add get_motd and create_motd methods before ban operations
motd_methods = """
    # MOTD operations

    def get_highest_motd_version(self) -> int:
        \"\"\"Get the highest motd version currently active.\"\"\"
        cursor = self._conn.cursor()
        try:
            cursor.execute("SELECT MAX(version) FROM motd")
            row = cursor.fetchone()
            return row[0] if row[0] is not None else 0
        except sqlite3.OperationalError:
            return 0

    def get_motd(self, version: int, language: str) -> str | None:
        \"\"\"Get a motd message for a specific version and language.\"\"\"
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
        \"\"\"Get the active (highest version) motd and message for a language.\"\"\"
        version = self.get_highest_motd_version()
        if version == 0:
            return None

        message = self.get_motd(version, language)
        if message:
            return (version, message)
        return None

    def create_motd(self, translations: dict[str, str]) -> int:
        \"\"\"Create a new motd version with translations and delete old versions.\"\"\"
        cursor = self._conn.cursor()

        # Find the next version
        try:
            cursor.execute("SELECT MAX(motd_version) FROM users")
            row = cursor.fetchone()
            next_version = (row[0] if row[0] is not None else 0) + 1
        except sqlite3.OperationalError:
            next_version = 1

        # Delete existing MOTDs
        self.delete_motd()

        for language, message in translations.items():
            cursor.execute(
                "INSERT INTO motd (version, language, message) VALUES (?, ?, ?)",
                (next_version, language, message)
            )

        self._conn.commit()
        return next_version

    def delete_motd(self) -> None:
        \"\"\"Delete all motd records.\"\"\"
        cursor = self._conn.cursor()
        try:
            cursor.execute("DELETE FROM motd")
            self._conn.commit()
        except sqlite3.OperationalError:
            pass

    # Ban operations"""
content = content.replace("    # Ban operations", motd_methods)

# 5. Add update_user_motd_version
update_motd_sql = """    def update_user_trust_level(self, username: str, trust_level: int) -> None:
        \"\"\"Update a user's trust level.\"\"\"
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET trust_level = ? WHERE username = ?",
            (trust_level, username),
        )
        self._conn.commit()

    def update_user_motd_version(self, username: str, motd_version: int) -> None:
        \"\"\"Update a user's motd version.\"\"\"
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET motd_version = ? WHERE username = ?",
            (motd_version, username),
        )
        self._conn.commit()"""
content = content.replace("""    def update_user_trust_level(self, username: str, trust_level: int) -> None:
        \"\"\"Update a user's trust level.\"\"\"
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET trust_level = ? WHERE username = ?",
            (trust_level, username),
        )
        self._conn.commit()""", update_motd_sql)

# Rewrite user methods to handle motd_version
# We'll use regex to update the SELECT and INSERT statements and the UserRecord creation

# get_user
def replace_get_user(m):
    return m.group(0).replace(
        "SELECT id, username, password_hash, uuid, locale, preferences_json, trust_level, approved, email, bio FROM users",
        "SELECT id, username, password_hash, uuid, locale, preferences_json, trust_level, approved, email, bio, motd_version FROM users"
    ).replace(
        'bio=row["bio"] or "",\n            )',
        'bio=row["bio"] or "",\n                motd_version=row["motd_version"] if "motd_version" in row.keys() else 0,\n            )'
    )
content = re.sub(r'    def get_user.*?return None', replace_get_user, content, flags=re.DOTALL)

# create_user
def replace_create_user(m):
    return m.group(0).replace(
        "locale, trust_level, approved, email, bio) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        "locale, trust_level, approved, email, bio, motd_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    ).replace(
        "(username, password_hash, user_uuid, locale, trust_level, 1 if approved else 0, email, bio),",
        "(username, password_hash, user_uuid, locale, trust_level, 1 if approved else 0, email, bio, 0),"
    ).replace(
        'bio=bio,\n        )',
        'bio=bio,\n            motd_version=0,\n        )'
    )
content = re.sub(r'    def create_user.*?motd_version=0,\n        \)', replace_create_user, content, flags=re.DOTALL)

# other user getters
def replace_other_users(m):
    return m.group(0).replace(
        "SELECT id, username, password_hash, uuid, locale, preferences_json, trust_level, approved, email, bio FROM users",
        "SELECT id, username, password_hash, uuid, locale, preferences_json, trust_level, approved, email, bio, motd_version FROM users"
    ).replace(
        'bio=row["bio"] or "",\n            ))',
        'bio=row["bio"] or "",\n                motd_version=row["motd_version"] if "motd_version" in row.keys() else 0,\n            ))'
    )
content = re.sub(r'    def get_pending_users.*?return users', replace_other_users, content, flags=re.DOTALL)
content = re.sub(r'    def get_non_admin_users.*?return users', replace_other_users, content, flags=re.DOTALL)
content = re.sub(r'    def get_admin_users.*?return users', replace_other_users, content, flags=re.DOTALL)


with open("server/persistence/database.py", "w") as f:
    f.write(content)
