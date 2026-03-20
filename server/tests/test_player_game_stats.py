import pytest
import sqlite3
import json
from datetime import datetime
from server.persistence.database import Database
from server.game_utils.game_result import GameResult, PlayerResult

@pytest.fixture
def db():
    """In-memory database for testing."""
    database = Database(":memory:")
    database.connect()

    # We need a user record for the JOINs to work and return a username
    database.create_user("Alice", "hash", trust_level=1)
    alice_record = database.get_user("Alice")

    database.create_user("Bob", "hash", trust_level=1)
    bob_record = database.get_user("Bob")

    yield database, alice_record, bob_record
    database.close()

def test_save_game_result_updates_stats(db):
    database, alice, bob = db

    # Simulate a game result
    players = [
        (alice.uuid, "Alice", False),
        (bob.uuid, "Bob", False)
    ]

    # Note: save_game_result internally uses StatsExtractor, so it will extract wins, scores, etc.
    custom_data = {
        "winner_name": "Alice",
        "final_scores": {
            "Alice": 100,
            "Bob": 50
        }
    }

    # Save first game
    database.save_game_result("pig", datetime.now().isoformat(), 100, players, custom_data)

    # Check Alice's stats
    alice_stats = database.get_all_player_game_stats(alice.uuid, "pig")
    assert alice_stats["games_played"] == 1.0
    assert alice_stats["wins"] == 1.0
    assert alice_stats.get("losses", 0) == 0
    assert alice_stats["total_score"] == 100.0
    assert alice_stats["high_score"] == 100.0

    # Check Bob's stats
    bob_stats = database.get_all_player_game_stats(bob.uuid, "pig")
    assert bob_stats["games_played"] == 1.0
    assert bob_stats["losses"] == 1.0
    assert bob_stats.get("wins", 0) == 0
    assert bob_stats["total_score"] == 50.0
    assert bob_stats["high_score"] == 50.0

    # Save a second game where Bob wins and gets a new high score
    custom_data_2 = {
        "winner_name": "Bob",
        "final_scores": {
            "Alice": 80,
            "Bob": 120
        }
    }
    database.save_game_result("pig", datetime.now().isoformat(), 100, players, custom_data_2)

    # Verify aggregation
    alice_stats = database.get_all_player_game_stats(alice.uuid, "pig")
    assert alice_stats["games_played"] == 2.0
    assert alice_stats["wins"] == 1.0
    assert alice_stats["losses"] == 1.0
    assert alice_stats["total_score"] == 180.0
    assert alice_stats["high_score"] == 100.0  # Max logic works

    bob_stats = database.get_all_player_game_stats(bob.uuid, "pig")
    assert bob_stats["games_played"] == 2.0
    assert bob_stats["wins"] == 1.0
    assert bob_stats["losses"] == 1.0
    assert bob_stats["total_score"] == 170.0
    assert bob_stats["high_score"] == 120.0  # Max logic works

def test_get_top_player_game_stats(db):
    database, alice, bob = db

    players = [
        (alice.uuid, "Alice", False),
        (bob.uuid, "Bob", False)
    ]

    custom_data = {
        "winner_name": "Alice",
        "final_scores": {
            "Alice": 100,
            "Bob": 50
        }
    }

    database.save_game_result("pig", datetime.now().isoformat(), 100, players, custom_data)

    top_scores = database.get_top_player_game_stats("pig", "total_score", limit=10)

    # Result format: (player_id, player_name, stat_value)
    assert len(top_scores) == 2
    assert top_scores[0][1] == "Alice"
    assert top_scores[0][2] == 100.0
    assert top_scores[1][1] == "Bob"
    assert top_scores[1][2] == 50.0

def test_get_top_wins_with_losses(db):
    database, alice, bob = db

    players = [
        (alice.uuid, "Alice", False),
        (bob.uuid, "Bob", False)
    ]

    custom_data = {
        "winner_name": "Alice",
        "final_scores": {
            "Alice": 100,
            "Bob": 50
        }
    }

    database.save_game_result("pig", datetime.now().isoformat(), 100, players, custom_data)

    top_wins = database.get_top_wins_with_losses("pig", limit=10)

    # Result format: (player_id, player_name, wins, losses)
    assert len(top_wins) == 1  # Only Alice has wins
    assert top_wins[0][1] == "Alice"
    assert top_wins[0][2] == 1.0 # wins
    assert top_wins[0][3] == 0.0 # losses

