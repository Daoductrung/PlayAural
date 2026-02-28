import sqlite3
import os

db_path = "playaural.db"
if os.path.exists(db_path):
    os.remove(db_path)

from server.persistence.database import Database

db = Database(db_path)
db.connect()

cursor = db._conn.cursor()
cursor.execute("PRAGMA table_info(bans)")
columns = [row[1] for row in cursor.fetchall()]
print("Bans columns:", columns)

try:
    db.ban_user("test", "admin", "reason_spam", None)
    active = db.get_active_ban("test")
    print("Ban record:", active)
except Exception as e:
    print("Error:", e)

db.close()
