import pytest
import sqlite3
import json
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

def test_prune_old_records(db):
    cursor = db._conn.cursor()

    now = datetime.datetime.now()
    recent = now - timedelta(days=10)
    old_game = now - timedelta(days=40)
    old_save = now - timedelta(days=400)
    old_ban = now - timedelta(days=40)
    future = now + timedelta(days=10)

    db.create_user("mute_active", "hash")
    db.create_user("mute_expired", "hash")

    # Insert game_results
    cursor.execute("INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data) VALUES (?, ?, ?, ?)",
                   ("pig", recent.isoformat(), 100, "{}"))
    recent_game_id = cursor.lastrowid

    cursor.execute("INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data) VALUES (?, ?, ?, ?)",
                   ("pig", old_game.isoformat(), 100, "{}"))
    old_game_id = cursor.lastrowid

    # Insert children to test CASCADE
    cursor.execute("INSERT INTO game_result_players (result_id, player_id, player_name, is_bot) VALUES (?, 'u1', 'p1', 0)", (recent_game_id,))
    cursor.execute("INSERT INTO game_result_players (result_id, player_id, player_name, is_bot) VALUES (?, 'u2', 'p2', 0)", (old_game_id,))

    # Insert saved_tables
    cursor.execute("INSERT INTO saved_tables (username, save_name, game_type, game_json, members_json, saved_at) VALUES (?, ?, ?, ?, ?, ?)",
                   ("p1", "Recent", "pig", "{}", "[]", recent.isoformat()))
    cursor.execute("INSERT INTO saved_tables (username, save_name, game_type, game_json, members_json, saved_at) VALUES (?, ?, ?, ?, ?, ?)",
                   ("p1", "Old", "pig", "{}", "[]", old_save.isoformat()))

    # Insert bans
    cursor.execute("INSERT INTO bans (username, admin_username, reason_key, issued_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                   ("b1", "admin", "reason", old_game.isoformat(), recent.isoformat())) # Expired recently
    cursor.execute("INSERT INTO bans (username, admin_username, reason_key, issued_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                   ("b2", "admin", "reason", old_save.isoformat(), old_ban.isoformat())) # Expired long ago

    # Insert mutes
    cursor.execute("INSERT INTO mutes (username, admin_username, reason, issued_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                   ("mute_active", "admin", "reason", recent.isoformat(), future.isoformat()))
    cursor.execute("INSERT INTO mutes (username, admin_username, reason, issued_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                   ("mute_expired", "admin", "reason", old_game.isoformat(), recent.isoformat()))
    cursor.execute("INSERT INTO mutes (username, admin_username, reason, issued_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                   ("mute_orphan", "admin", "reason", recent.isoformat(), future.isoformat()))

    db._conn.commit()

    # Run pruner
    db.prune_old_records()

    # Check game results and cascade
    cursor.execute("SELECT id FROM game_results")
    games = [row[0] for row in cursor.fetchall()]
    assert recent_game_id in games
    assert old_game_id not in games

    cursor.execute("SELECT result_id FROM game_result_players")
    players = [row[0] for row in cursor.fetchall()]
    assert recent_game_id in players
    assert old_game_id not in players # Cascaded!

    # Check saved tables
    cursor.execute("SELECT save_name FROM saved_tables")
    saves = [row[0] for row in cursor.fetchall()]
    assert "Recent" in saves
    assert "Old" not in saves

    # Check bans
    cursor.execute("SELECT username FROM bans")
    bans = [row[0] for row in cursor.fetchall()]
    assert "b1" in bans
    assert "b2" not in bans

    # Check mutes
    cursor.execute("SELECT username FROM mutes")
    mutes = [row[0] for row in cursor.fetchall()]
    assert "mute_active" in mutes
    assert "mute_expired" not in mutes
    assert "mute_orphan" not in mutes

def test_connect_can_skip_pruning_for_short_cli_operations(tmp_path):
    db_path = tmp_path / "PlayAural.db"
    database = Database(db_path)
    database.connect()

    old_game = datetime.datetime.now() - timedelta(days=40)
    cursor = database._conn.cursor()
    cursor.execute(
        "INSERT INTO game_results (game_type, timestamp, duration_ticks, custom_data) VALUES (?, ?, ?, ?)",
        ("pig", old_game.isoformat(), 100, "{}"),
    )
    database._conn.commit()
    database.close()

    database = Database(db_path)
    database.connect(prune=False)
    cursor = database._conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM game_results")
    assert cursor.fetchone()[0] == 1
    database.close()

    database = Database(db_path)
    database.connect(prune=True)
    cursor = database._conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM game_results")
    assert cursor.fetchone()[0] == 0
    database.close()

def test_delete_user_cascades(db):
    db.create_user("Alice", "hash")
    alice = db.get_user("Alice")

    cursor = db._conn.cursor()

    # Insert fake data across all tables
    cursor.execute("INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value) VALUES (?, 'pig', 'wins', 1)", (alice.uuid,))
    cursor.execute("INSERT INTO player_ratings (player_id, game_type, mu, sigma) VALUES (?, 'pig', 25.0, 8.0)", (alice.uuid,))
    cursor.execute("INSERT INTO saved_tables (username, save_name, game_type, game_json, members_json, saved_at) VALUES (?, 'save', 'pig', '', '', '')", ("Alice",))
    cursor.execute("INSERT INTO bans (username, admin_username, reason_key, issued_at, expires_at) VALUES (?, 'admin', 'r', '', '')", ("Alice",))
    cursor.execute("INSERT INTO mutes (username, admin_username, reason, issued_at, expires_at) VALUES (?, 'admin', 'r', '', '')", ("Alice",))
    db._conn.commit()

    # Run delete
    assert db.delete_user("Alice") is True

    # Verify everything is gone
    cursor.execute("SELECT COUNT(*) FROM player_game_stats")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM player_ratings")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM saved_tables")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM bans")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM mutes")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT COUNT(*) FROM users")
    assert cursor.fetchone()[0] == 0
