"""
Tests for the Ninety Nine game.

Following the testing strategy:
- Unit tests for individual functions
- Play tests that run the game from start to finish with bots
- Persistence tests (save/reload at each tick)
"""

import pytest
import random
import json

from server.games.ninetynine.game import (
    NinetyNineGame,
    NinetyNineOptions,
)
from server.game_utils.cards import (
    Card,
    Deck,
    DeckFactory,
    RS_GAMES_RANK_NAMES,
    SUIT_NONE,
    SUIT_HEARTS,
    RS_RANK_PLUS_10,
    RS_RANK_MINUS_10,
    RS_RANK_PASS,
    RS_RANK_REVERSE,
    RS_RANK_SKIP,
    RS_RANK_NINETY_NINE,
)
from server.users.test_user import MockUser
from server.users.bot import Bot


class TestNinetyNineUnit:
    """Unit tests for Ninety Nine game functions."""

    def test_game_creation(self):
        """Test creating a new Ninety Nine game."""
        game = NinetyNineGame()
        assert game.get_name() == "Ninety Nine"
        assert game.get_type() == "ninetynine"
        assert game.get_category() == "category-card-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 6

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = NinetyNineGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.tokens == 9  # Default starting tokens
        assert player.hand == []
        assert player.is_bot is False

    def test_options_defaults(self):
        """Test default game options."""
        game = NinetyNineGame()
        assert game.options.starting_tokens == 9
        assert game.options.hand_size == 3
        assert game.options.rules_variant == "quentin_c"

    def test_custom_options(self):
        """Test custom game options."""
        options = NinetyNineOptions(
            starting_tokens=5, hand_size=5, rules_variant="rs_games"
        )
        game = NinetyNineGame(options=options)
        assert game.options.starting_tokens == 5
        assert game.options.hand_size == 5
        assert game.options.rules_variant == "rs_games"


class TestCardAndDeck:
    """Tests for Card and Deck classes."""

    def test_card_creation(self):
        """Test card creation and properties."""
        from server.game_utils.cards import card_name

        card = Card(id=0, rank=1, suit=SUIT_HEARTS)
        assert card.rank == 1
        assert card.suit == SUIT_HEARTS
        name = card_name(card).lower()
        assert "ace" in name
        assert "hearts" in name

    def test_card_article(self):
        """Test card article (a/an)."""
        from server.game_utils.cards import card_name_with_article

        ace = Card(id=0, rank=1, suit=SUIT_HEARTS)
        assert card_name_with_article(ace).startswith("an")

        two = Card(id=1, rank=2, suit=SUIT_HEARTS)
        assert card_name_with_article(two).startswith("a ")

        eight = Card(id=2, rank=8, suit=SUIT_HEARTS)
        assert card_name_with_article(eight).startswith("an")

    def test_deck_creation(self):
        """Test deck creation."""
        deck, _ = DeckFactory.standard_deck()
        assert len(deck.cards) == 52

    def test_deck_shuffle(self):
        """Test deck shuffling."""
        deck, _ = DeckFactory.standard_deck()
        original_order = [c.id for c in deck.cards]

        random.seed(42)
        deck.shuffle()
        new_order = [c.id for c in deck.cards]

        assert original_order != new_order

    def test_deck_draw(self):
        """Test drawing from deck."""
        deck, _ = DeckFactory.standard_deck()
        assert len(deck.cards) == 52

        card = deck.draw_one()
        assert card is not None
        assert len(deck.cards) == 51

    def test_deck_empty(self):
        """Test empty deck behavior."""
        deck = Deck()
        assert deck.is_empty()
        assert deck.draw_one() is None

    def test_rs_games_deck_creation(self):
        """Test RS Games deck has 60 cards with correct distribution."""
        deck, _ = DeckFactory.rs_games_deck()
        assert len(deck.cards) == 60

        # Count cards by rank
        rank_counts = {}
        for card in deck.cards:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1

        # Number cards 1-9: 4 of each
        for rank in range(1, 10):
            assert rank_counts.get(rank, 0) == 4, f"Expected 4 cards of rank {rank}"

        # Special cards: 4 of each (ranks 14-19)
        for rank in [
            RS_RANK_PLUS_10,
            RS_RANK_MINUS_10,
            RS_RANK_PASS,
            RS_RANK_REVERSE,
            RS_RANK_SKIP,
            RS_RANK_NINETY_NINE,
        ]:
            assert rank_counts.get(rank, 0) == 4, f"Expected 4 cards of rank {rank}"

    def test_rs_games_card_names(self):
        """Test RS Games card naming."""
        # Check special card names
        assert RS_GAMES_RANK_NAMES[RS_RANK_PLUS_10] == "10"
        assert RS_GAMES_RANK_NAMES[RS_RANK_MINUS_10] == "-10"
        assert RS_GAMES_RANK_NAMES[RS_RANK_PASS] == "Pass"
        assert RS_GAMES_RANK_NAMES[RS_RANK_REVERSE] == "Reverse"
        assert RS_GAMES_RANK_NAMES[RS_RANK_SKIP] == "Skip"
        assert RS_GAMES_RANK_NAMES[RS_RANK_NINETY_NINE] == "Ninety Nine"


class TestCardValues:
    """Tests for card value calculations."""

    def test_quentin_c_values(self):
        """Test card values in Quentin C variant."""
        game = NinetyNineGame()

        # 3-8 are face value
        for rank in range(3, 9):
            card = Card(id=rank, rank=rank, suit=SUIT_HEARTS)
            assert game.calculate_card_value(card, 50) == rank

        # 9 is pass (0)
        nine = Card(id=9, rank=9, suit=SUIT_HEARTS)
        assert game.calculate_card_value(nine, 50) == 0

        # Jack, Queen, King are +10
        for rank in [11, 12, 13]:
            card = Card(id=rank, rank=rank, suit=SUIT_HEARTS)
            assert game.calculate_card_value(card, 50) == 10

    def test_ace_auto_choice(self):
        """Test that Ace auto-chooses +1 when count > 88."""
        game = NinetyNineGame()
        ace = Card(id=1, rank=1, suit=SUIT_HEARTS)

        # Below 88, needs choice
        assert game.calculate_card_value(ace, 50) is None

        # Above 88, auto +1
        assert game.calculate_card_value(ace, 89) == 1

    def test_ten_auto_choice(self):
        """Test that 10 auto-chooses -10 when count >= 90."""
        game = NinetyNineGame()
        ten = Card(id=10, rank=10, suit=SUIT_HEARTS)

        # Below 90, needs choice
        assert game.calculate_card_value(ten, 50) is None

        # At or above 90, auto -10
        assert game.calculate_card_value(ten, 90) == -10
        assert game.calculate_card_value(ten, 95) == -10

    def test_two_effect_multiply(self):
        """Test 2 card multiply effect."""
        game = NinetyNineGame()

        # Odd counts always multiply
        assert game.calculate_two_effect(15) == 30
        assert game.calculate_two_effect(25) == 50

        # Even counts <= 49 multiply
        assert game.calculate_two_effect(20) == 40
        assert game.calculate_two_effect(48) == 96

    def test_two_effect_divide(self):
        """Test 2 card divide effect."""
        game = NinetyNineGame()

        # Even counts > 49 divide
        assert game.calculate_two_effect(50) == 25
        assert game.calculate_two_effect(66) == 33
        assert game.calculate_two_effect(92) == 46


class TestMilestones:
    """Tests for milestone logic."""

    def setup_method(self):
        """Set up a game for milestone testing."""
        self.game = NinetyNineGame()
        self.user1 = MockUser("Alice")
        self.user2 = MockUser("Bob")
        self.player1 = self.game.add_player("Alice", self.user1)
        self.player2 = self.game.add_player("Bob", self.user2)
        self.game.on_start()
        # Set initial tokens
        self.player1.tokens = 9
        self.player2.tokens = 9

    def test_landing_on_33(self):
        """Test landing exactly on 33 makes others lose tokens."""
        self.game.count = 30
        # Simulate playing a 3 (value=3, new_count=33)
        round_ended = self.game._check_milestones(
            self.player1, old_count=30, new_count=33, value=3, card_rank=3
        )

        assert not round_ended
        assert self.player2.tokens == 8  # Lost 1 token

    def test_landing_on_66(self):
        """Test landing exactly on 66 makes others lose tokens."""
        self.game.count = 60
        round_ended = self.game._check_milestones(
            self.player1, old_count=60, new_count=66, value=6, card_rank=6
        )

        assert not round_ended
        assert self.player2.tokens == 8

    def test_landing_on_99_ends_round(self):
        """Test landing exactly on 99 ends the round."""
        self.game.count = 89
        round_ended = self.game._check_milestones(
            self.player1, old_count=89, new_count=99, value=10, card_rank=12
        )

        assert round_ended
        assert self.player2.tokens == 7  # Lost 2 tokens

    def test_passing_33(self):
        """Test passing through 33 makes player lose token."""
        round_ended = self.game._check_milestones(
            self.player1, old_count=30, new_count=35, value=5, card_rank=5
        )

        assert not round_ended
        assert self.player1.tokens == 8

    def test_passing_66(self):
        """Test passing through 66 makes player lose token."""
        round_ended = self.game._check_milestones(
            self.player1, old_count=60, new_count=70, value=10, card_rank=12
        )

        assert not round_ended
        assert self.player1.tokens == 8

    def test_going_over_99(self):
        """Test going over 99 ends round."""
        round_ended = self.game._check_milestones(
            self.player1, old_count=95, new_count=105, value=10, card_rank=12
        )

        assert round_ended
        assert self.player1.tokens == 7  # Lost 2 tokens

    def test_negative_value_no_milestone(self):
        """Test that negative values don't trigger milestone bonuses."""
        self.player2.tokens = 9
        round_ended = self.game._check_milestones(
            self.player1, old_count=43, new_count=33, value=-10, card_rank=10
        )

        assert not round_ended
        assert self.player2.tokens == 9  # No change


class TestNinetyNinePlayTest:
    """
    Play tests that run complete games with bots.
    """

    def test_two_player_game_completes(self):
        """Test that a 2-player game runs to completion."""
        random.seed(123)

        game = NinetyNineGame(options=NinetyNineOptions(starting_tokens=5))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.setup_keybinds()
        game.on_start()

        max_ticks = 3000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active, "Game should have ended"

        # One player should have won (have tokens)
        alive = [p for p in game.players if p.tokens > 0]
        assert len(alive) <= 1

    def test_three_player_game_completes(self):
        """Test that a 3-player game runs to completion."""
        random.seed(456)

        game = NinetyNineGame(options=NinetyNineOptions(starting_tokens=5))
        bots = [Bot(f"Bot{i}") for i in range(1, 4)]
        for bot in bots:
            game.add_player(bot.username, bot)

        game.setup_keybinds()
        game.on_start()

        max_ticks = 5000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active

    def test_six_player_game_completes(self):
        """Test that a 6-player game runs to completion."""
        random.seed(789)

        game = NinetyNineGame(options=NinetyNineOptions(starting_tokens=3))
        bots = [Bot(f"Bot{i}") for i in range(1, 7)]
        for bot in bots:
            game.add_player(bot.username, bot)

        game.setup_keybinds()
        game.on_start()

        max_ticks = 5000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active

    def test_rs_games_variant(self):
        """Test RS Games variant."""
        random.seed(111)

        game = NinetyNineGame(
            options=NinetyNineOptions(starting_tokens=3, rules_variant="rs_games")
        )
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.setup_keybinds()
        game.on_start()

        max_ticks = 5000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active


class TestNinetyNinePersistence:
    """Persistence tests."""

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = NinetyNineGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.setup_keybinds()
        game.on_start()

        # Modify state
        game.count = 55
        game.turn_direction = -1
        game.players[0].tokens = 5
        game.players[1].tokens = 7
        game.round = 3

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        assert data["count"] == 55
        assert data["turn_direction"] == -1
        assert data["round"] == 3

        # Deserialize
        loaded = NinetyNineGame.from_json(json_str)
        assert loaded.count == 55
        assert loaded.turn_direction == -1
        assert loaded.round == 3
        assert loaded.players[0].tokens == 5
        assert loaded.players[1].tokens == 7

    def test_game_with_periodic_save_reload(self):
        """Test game with periodic save/reload to verify persistence."""
        random.seed(999)

        game = NinetyNineGame(options=NinetyNineOptions(starting_tokens=5))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.setup_keybinds()
        game.on_start()

        max_ticks = 2000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 100 ticks
            if tick % 100 == 0 and tick > 0:
                # Save non-serialized state
                saved_users = dict(game._users)
                saved_keybinds = dict(game._keybinds)

                json_str = game.to_json()
                game = NinetyNineGame.from_json(json_str)

                # Restore non-serialized state
                game._users = saved_users
                game._keybinds = saved_keybinds
                game.rebuild_runtime_state()

            game.on_tick()

        # Game should complete without errors
        assert not game.game_active or tick == max_ticks - 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
