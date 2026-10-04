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
        "winner_ids": [alice.uuid],
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
        "winner_ids": [bob.uuid],
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
        "winner_ids": [alice.uuid],
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


def test_get_top_player_game_stats_casts_mixed_storage_types_numerically(db):
    database, alice, bob = db

    cursor = database._conn.cursor()
    cursor.execute(
        """
        INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
        VALUES (?, 'battle', 'custom_most_enemies_defeated_high', ?)
        """,
        (alice.uuid, "18"),
    )
    cursor.execute(
        """
        INSERT INTO player_game_stats (player_id, game_type, stat_key, stat_value)
        VALUES (?, 'battle', 'custom_most_enemies_defeated_high', ?)
        """,
        (bob.uuid, 19),
    )
    database._conn.commit()

    top_scores = database.get_top_player_game_stats("battle", "custom_most_enemies_defeated_high", limit=10)

    assert top_scores[0][1] == "Bob"
    assert top_scores[0][2] == 19.0
    assert top_scores[1][1] == "Alice"
    assert top_scores[1][2] == 18.0

def test_get_top_wins_with_losses(db):
    database, alice, bob = db

    players = [
        (alice.uuid, "Alice", False),
        (bob.uuid, "Bob", False)
    ]

    custom_data = {
        "winner_name": "Alice",
        "winner_ids": [alice.uuid],
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


def test_result_and_rating_updates_roll_back_together(db):
    database, alice, bob = db
    players = [
        (alice.uuid, "Alice", False),
        (bob.uuid, "Bob", False),
    ]

    with pytest.raises(ValueError, match="every human result participant"):
        database.save_game_result(
            "pig",
            datetime.now().isoformat(),
            100,
            players,
            {"winner_ids": [alice.uuid]},
            rating_updates={"not-a-participant": (30.0, 7.0)},
        )

    assert database.get_game_stats("pig") == []
    assert database.get_all_player_game_stats(alice.uuid, "pig") == {}
    assert database.get_player_rating("not-a-participant", "pig") is None


def test_partial_rating_settlement_rolls_back_entire_result(db):
    database, alice, bob = db
    players = [
        (alice.uuid, "Alice", False),
        (bob.uuid, "Bob", False),
    ]

    with pytest.raises(ValueError, match="every human result participant"):
        database.save_game_result(
            "pig",
            datetime.now().isoformat(),
            100,
            players,
            {"winner_ids": [alice.uuid]},
            rating_updates={alice.uuid: (30.0, 7.0)},
        )

    assert database.get_game_stats("pig") == []
    assert database.get_all_player_game_stats(alice.uuid, "pig") == {}
    assert database.get_player_rating(alice.uuid, "pig") is None


def test_duplicate_result_identity_is_rejected_before_persistence(db):
    database, alice, _bob = db
    players = [
        (alice.uuid, "Alice", False),
        (alice.uuid, "Alice duplicate", False),
    ]

    with pytest.raises(ValueError, match="duplicate player ids"):
        database.save_game_result(
            "pig",
            datetime.now().isoformat(),
            100,
            players,
            {"winner_ids": [alice.uuid]},
        )

    assert database.get_game_stats("pig") == []
    assert database.get_all_player_game_stats(alice.uuid, "pig") == {}


@pytest.mark.parametrize(
    ("mu", "sigma"),
    [
        (float("nan"), 1.0),
        (float("inf"), 1.0),
        (25.0, 0.0),
        (25.0, float("inf")),
    ],
)
def test_rating_writes_reject_invalid_numeric_values(db, mu, sigma):
    database, alice, _bob = db

    with pytest.raises(ValueError):
        database.set_player_rating(alice.uuid, "pig", mu, sigma)

    assert database.get_player_rating(alice.uuid, "pig") is None


def test_invalid_legacy_rating_is_not_exposed_or_ranked(db, caplog):
    database, alice, bob = db
    database._conn.execute(
        """
        INSERT INTO player_ratings (player_id, game_type, mu, sigma)
        VALUES (?, ?, ?, ?)
        """,
        (alice.uuid, "pig", float("inf"), 1.0),
    )
    database.set_player_rating(bob.uuid, "pig", 25.0, 8.0)

    assert database.get_player_rating(alice.uuid, "pig") is None
    leaderboard = database.get_rating_leaderboard("pig", 1, confidence_z=3.0)
    assert [entry[0] for entry in leaderboard] == [bob.uuid]
    assert "Ignoring invalid stored rating" in caplog.text


def test_rating_leaderboard_uses_conservative_skill_score(db):
    database, alice, bob = db
    database.set_player_rating(alice.uuid, "pig", 30.0, 8.0)
    database.set_player_rating(bob.uuid, "pig", 28.0, 2.0)

    leaderboard = database.get_rating_leaderboard(
        "pig",
        10,
        confidence_z=3.0,
    )

    assert [entry[0] for entry in leaderboard] == [bob.uuid, alice.uuid]


def test_zero_score_replaces_a_negative_personal_high_score(db):
    database, alice, _bob = db
    players = [(alice.uuid, "Alice", False)]

    database.save_game_result(
        "pig",
        datetime.now().isoformat(),
        100,
        players,
        {"winner_ids": [], "final_scores": {"Alice": -4}},
    )
    database.save_game_result(
        "pig",
        datetime.now().isoformat(),
        100,
        players,
        {"winner_ids": [], "final_scores": {"Alice": 0}},
    )

    stats = database.get_all_player_game_stats(alice.uuid, "pig")
    assert stats["total_score"] == -4.0
    assert stats["high_score"] == 0.0


def test_battle_custom_max_stats_persist_with_correct_keys(db):
    database, alice, bob = db

    players = [
        (alice.uuid, "Alice", False),
        (bob.uuid, "Bob", False),
    ]

    custom_data = {
        "player_stats": {
            alice.uuid: {"survival_kills": 7, "deepest_wave": 4},
            bob.uuid: {"survival_kills": 5, "deepest_wave": 3},
        }
    }

    database.save_game_result("battle", datetime.now().isoformat(), 100, players, custom_data)

    alice_stats = database.get_all_player_game_stats(alice.uuid, "battle")
    bob_stats = database.get_all_player_game_stats(bob.uuid, "battle")

    assert alice_stats["games_played"] == 1.0
    assert alice_stats["custom_most_enemies_defeated_high"] == 7.0
    assert alice_stats["custom_deepest_wave_reached_high"] == 4.0
    assert "custom_most_enemies_defeated" not in alice_stats
    assert "custom_deepest_wave_reached" not in alice_stats

    assert bob_stats["games_played"] == 1.0
    assert bob_stats["custom_most_enemies_defeated_high"] == 5.0
    assert bob_stats["custom_deepest_wave_reached_high"] == 3.0

