"""Tests for Coup game."""

import pytest
from server.games.coup.game import CoupGame
from server.games.coup.cards import Character, Card
from server.users.test_user import MockUser

@pytest.fixture
def game():
    """Create a new Coup game with 2 players."""
    g = CoupGame()
    g.players.append(g.create_player("player1", "Alice"))
    g.players.append(g.create_player("player2", "Bob"))

    # Attach mock users
    g.attach_user("player1", MockUser("Alice", "player1"))
    g.attach_user("player2", MockUser("Bob", "player2"))

    g.on_start()
    return g

def advance_ticks(game, ticks=100):
    game.sound_scheduler_tick += ticks
    game.on_tick()

def test_income(game):
    """Test the income action."""
    alice = game.get_player_by_name("Alice")
    initial_coins = alice.coins
    game._action_income(alice, "income")
    advance_ticks(game, 100)
    assert alice.coins == initial_coins + 1
    assert game.current_player.name == "Bob"

def test_coup_action(game):
    """Test the coup action."""
    alice = game.get_player_by_name("Alice")
    bob = game.get_player_by_name("Bob")

    alice.coins = 7
    game._action_coup(alice, "Bob", "coup")
    advance_ticks(game, 150)

    assert alice.coins == 0
    assert game.turn_phase == "losing_influence"
    assert game.active_target_id == bob.id

    # Bob loses an influence
    game._action_lose_influence(bob, "lose_influence_0")
    advance_ticks(game, 100)
    assert len(bob.live_influences) == 1
    assert game.current_player.name == "Bob"

def test_foreign_aid_and_block(game):
    """Test foreign aid and block."""
    alice = game.get_player_by_name("Alice")
    bob = game.get_player_by_name("Bob")

    game._action_foreign_aid(alice, "foreign_aid")
    advance_ticks(game, 100)

    assert game.turn_phase == "action_declared"
    assert game.active_action == "foreign_aid"
    assert game.active_claimer_id == alice.id

    # Bob blocks
    game._action_block(bob, "block")
    advance_ticks(game, 150)

    assert game.turn_phase == "waiting_block"
    assert game.active_claimer_id == bob.id

def test_assassinate_and_challenge(game):
    """Test assassinate and challenge."""
    alice = game.get_player_by_name("Alice")
    bob = game.get_player_by_name("Bob")

    # Force Alice to not have Assassin to guarantee she loses the challenge
    alice.influences = [Card(Character.DUKE), Card(Character.CONTESSA)]
    alice.coins = 3

    game._action_assassinate(alice, "Bob", "assassinate")
    advance_ticks(game, 100)

    assert game.turn_phase == "action_declared"
    assert game.active_target_id == bob.id

    # Bob challenges Alice
    game._action_challenge(bob, "challenge")
    advance_ticks(game, 150)
    advance_ticks(game, 50)

    # Alice failed challenge (didn't have Assassin)
    # So Alice loses an influence immediately, and action fails.
    assert game.turn_phase == "losing_influence"
    assert game.active_target_id == alice.id

    # Alice chooses to lose the first one
    game._action_lose_influence(alice, "lose_influence_0")
    advance_ticks(game, 100)

    assert len(alice.live_influences) == 1

    # Turn ends
    assert game.current_player.name == "Bob"

def test_steal_block_and_failed_challenge(game):
    """Test steal, Ambassador block, and the blocker successfully defending a challenge."""
    alice = game.get_player_by_name("Alice")
    bob = game.get_player_by_name("Bob")

    alice.coins = 2
    bob.coins = 2
    # Bob has an Ambassador
    bob.influences = [Card(Character.AMBASSADOR), Card(Character.CONTESSA)]

    game._action_steal(alice, "Bob", "steal")
    advance_ticks(game, 100)
    assert game.turn_phase == "action_declared"

    # Bob blocks with Ambassador
    game._action_block(bob, "block")
    advance_ticks(game, 100)
    assert game.turn_phase == "waiting_block"
    assert game.active_claimer_id == bob.id
    assert game.original_claimer_id == alice.id

    # Alice challenges Bob's block
    game._action_challenge(alice, "challenge")
    advance_ticks(game, 150)
    advance_ticks(game, 50)

    # Bob DOES have the Ambassador, so the challenge fails (Alice is wrong)
    # Alice loses influence
    assert game.turn_phase == "losing_influence"
    assert game.active_target_id == alice.id

    # Bob successfully blocked, meaning Alice's steal fails and turn should end after she loses influence
    assert getattr(game, "_next_action_after_lose", "end_turn") == "end_turn"

    # Alice chooses to lose the first one
    game._action_lose_influence(alice, "lose_influence_0")
    advance_ticks(game, 100)
    assert len(alice.live_influences) == 1

    # Turn ends
    assert game.current_player.name == "Bob"
    # Coins didn't change because steal failed
    assert alice.coins == 2
    assert bob.coins == 2
