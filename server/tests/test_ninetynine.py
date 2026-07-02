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

from ..games.ninetynine.game import (
    NinetyNineGame,
    NinetyNineOptions,
    PENALTY_MILESTONE_99,
    ROUND_TRANSITION_SECONDS,
    DRAW_TIMEOUT_TICKS,
)
from ..game_utils.cards import (
    Card,
    Deck,
    DeckFactory,
    N99_SPECIAL_RANK_NAMES,
    SUIT_NONE,
    SUIT_HEARTS,
    N99_RANK_PLUS_10,
    N99_RANK_MINUS_10,
    N99_RANK_PASS,
    N99_RANK_REVERSE,
    N99_RANK_SKIP,
    N99_RANK_NINETY_NINE,
)
from pathlib import Path
from ..users.test_user import MockUser
from ..users.bot import Bot
from ..users.base import MenuItem
from server.messages.localization import Localization


class TestNinetyNineUnit:
    """Unit tests for Ninety Nine game functions."""

    @classmethod
    def setup_class(cls):
        Localization.init(Path(__file__).parent.parent / "locales")
        Localization.preload_bundles()

    def test_game_creation(self):
        """Test creating a new Ninety Nine game."""
        game = NinetyNineGame()
        assert game.get_name() == "Ninety Nine"
        assert game.get_type() == "ninetynine"
        assert game.get_category() == "cards"
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
        assert game.options.rules_variant == "standard"

    def test_custom_options(self):
        """Test custom game options."""
        options = NinetyNineOptions(
            starting_tokens=5, hand_size=5, rules_variant="action_cards"
        )
        game = NinetyNineGame(options=options)
        assert game.options.starting_tokens == 5
        assert game.options.hand_size == 5
        assert game.options.rules_variant == "action_cards"

    def test_prestart_validate_rejects_impossible_deal(self):
        """Hand size must fit the selected deck before the game starts."""
        game = NinetyNineGame(options=NinetyNineOptions(hand_size=13))
        for name in ["Alice", "Bob", "Carol", "Dan", "Eve"]:
            game.add_player(name, MockUser(name))

        errors = game.prestart_validate()

        assert any(
            isinstance(error, tuple)
            and error[0] == "ninetynine-error-too-many-cards"
            for error in errors
        )


class TestCardAndDeck:
    """Tests for Card and Deck classes."""

    @classmethod
    def setup_class(cls):
        Localization.init(Path(__file__).parent.parent / "locales")
        Localization.preload_bundles()

    def test_card_creation(self):
        """Test card creation and properties."""
        from ..game_utils.cards import card_name

        card = Card(id=0, rank=1, suit=SUIT_HEARTS)
        assert card.rank == 1
        assert card.suit == SUIT_HEARTS
        name = card_name(card, "en").lower()
        assert "ace" in name
        assert "hearts" in name

    def test_card_article(self):
        """Test card article (a/an)."""
        from ..game_utils.cards import card_name_with_article

        ace = Card(id=0, rank=1, suit=SUIT_HEARTS)
        assert card_name_with_article(ace, "en").startswith("an")

        two = Card(id=1, rank=2, suit=SUIT_HEARTS)
        assert card_name_with_article(two, "en").startswith("a ")

        eight = Card(id=2, rank=8, suit=SUIT_HEARTS)
        assert card_name_with_article(eight, "en").startswith("an")

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

    def test_n99_action_deck_creation(self):
        """Test N99 action deck has 60 cards with correct distribution."""
        deck, _ = DeckFactory.n99_action_deck()
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
            N99_RANK_PLUS_10,
            N99_RANK_MINUS_10,
            N99_RANK_PASS,
            N99_RANK_REVERSE,
            N99_RANK_SKIP,
            N99_RANK_NINETY_NINE,
        ]:
            assert rank_counts.get(rank, 0) == 4, f"Expected 4 cards of rank {rank}"

    def test_n99_action_card_names(self):
        """Test N99 action card naming."""
        # Check special card names
        assert N99_SPECIAL_RANK_NAMES[N99_RANK_PLUS_10] == "10"
        assert N99_SPECIAL_RANK_NAMES[N99_RANK_MINUS_10] == "-10"
        assert N99_SPECIAL_RANK_NAMES[N99_RANK_PASS] == "Pass"
        assert N99_SPECIAL_RANK_NAMES[N99_RANK_REVERSE] == "Reverse"
        assert N99_SPECIAL_RANK_NAMES[N99_RANK_SKIP] == "Skip"
        assert N99_SPECIAL_RANK_NAMES[N99_RANK_NINETY_NINE] == "Ninety Nine"


class TestCardValues:
    """Tests for card value calculations."""

    def test_standard_values(self):
        """Test card values in standard variant."""
        game = NinetyNineGame()

        # 3, 5-8 are face value (4 is reverse)
        for rank in [3, 5, 6, 7, 8]:
            card = Card(id=rank, rank=rank, suit=SUIT_HEARTS)
            assert game.calculate_card_value(card, 50) == rank

        # 4 is reverse (adds 4)
        card = Card(id=4, rank=4, suit=SUIT_HEARTS)
        assert game.calculate_card_value(card, 50) == 4

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
        self.game.flush_menus()
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

    def test_two_halving_66_to_33_has_no_milestone_penalty(self):
        """Moving down to 33 from 66 should not penalize or add extra chatter."""
        self.player1.tokens = 9
        self.player2.tokens = 9
        self.user1.clear_messages()
        self.user2.clear_messages()

        round_ended = self.game._check_milestones(
            self.player1, old_count=66, new_count=33, value=-33, card_rank=2
        )

        assert not round_ended
        assert self.player1.tokens == 9
        assert self.player2.tokens == 9
        assert self.user1.get_spoken_messages() == []
        assert self.user2.get_spoken_messages() == []

    def test_negative_crossing_66_has_no_milestone_penalty(self):
        """Moving down past 66 should not trigger milestone token loss."""
        self.player1.tokens = 9
        self.player2.tokens = 9
        self.user1.clear_messages()
        self.user2.clear_messages()

        round_ended = self.game._check_milestones(
            self.player1, old_count=75, new_count=65, value=-10, card_rank=10
        )

        assert not round_ended
        assert self.player1.tokens == 9
        assert self.player2.tokens == 9
        assert self.user1.get_spoken_messages() == []
        assert self.user2.get_spoken_messages() == []

    def test_bust_audio_routes_lose_to_loser_and_win_to_others(self):
        """The busted player should hear lose, while others and spectators hear win."""
        spectator_user = MockUser("Spec")
        spectator = self.game.add_player("Spec", spectator_user)
        spectator.is_spectator = True

        self.user1.clear_messages()
        self.user2.clear_messages()
        spectator_user.clear_messages()

        self.game._player_busts(self.player1)

        assert self.user1.get_sounds_played()[-1] == "game_ninetynine/lose2.ogg"
        assert self.user2.get_sounds_played()[-1] == "game_pig/win.ogg"
        assert spectator_user.get_sounds_played()[-1] == "game_pig/win.ogg"

    def test_milestone_99_audio_routes_win_to_scorer_and_lose_to_losers(self):
        """Landing on 99 should give the scoring player the win sound and losers the lose sound."""
        spectator_user = MockUser("Spec")
        spectator = self.game.add_player("Spec", spectator_user)
        spectator.is_spectator = True

        self.user1.clear_messages()
        self.user2.clear_messages()
        spectator_user.clear_messages()

        self.game._others_lose_tokens(self.player1, PENALTY_MILESTONE_99, "99")

        assert self.user1.get_sounds_played()[-1] == "game_pig/win.ogg"
        assert self.user2.get_sounds_played()[-1] == "game_ninetynine/lose2.ogg"
        assert spectator_user.get_sounds_played()[-1] == "game_pig/win.ogg"

    def test_draw_recycles_older_discards_and_preserves_top_discard(self):
        """When the stock is empty, the live top discard should not be redrawn."""
        older_discard_1 = Card(id=501, rank=5, suit=SUIT_HEARTS)
        older_discard_2 = Card(id=502, rank=6, suit=SUIT_HEARTS)
        top_discard = Card(id=503, rank=7, suit=SUIT_HEARTS)
        self.game.deck.cards = []
        self.game.discard_pile = [older_discard_1, older_discard_2, top_discard]

        drawn = self.game._draw_card()

        assert drawn in {older_discard_1, older_discard_2}
        assert drawn != top_discard
        assert self.game.discard_pile == [top_discard]

    def test_draw_returns_none_when_only_top_discard_remains(self):
        """A lone live discard should stay in place until another card is played."""
        top_discard = Card(id=504, rank=7, suit=SUIT_HEARTS)
        self.game.deck.cards = []
        self.game.discard_pile = [top_discard]

        assert self.game._draw_card() is None
        assert self.game.discard_pile == [top_discard]


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
        game.flush_menus()

        max_ticks = 3000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()
            game.flush_menus()

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
        game.flush_menus()

        max_ticks = 5000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()
            game.flush_menus()

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
        game.flush_menus()

        max_ticks = 5000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()
            game.flush_menus()

        assert not game.game_active

    def test_action_cards_variant(self):
        """Test action cards variant."""
        random.seed(111)

        game = NinetyNineGame(
            options=NinetyNineOptions(starting_tokens=3, rules_variant="action_cards")
        )
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.setup_keybinds()
        game.on_start()
        game.flush_menus()

        max_ticks = 5000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            game.on_tick()
            game.flush_menus()

        assert not game.game_active

    def test_manual_draw_passes_turn_immediately(self):
        """In manual-draw mode, playing a card advances the turn at once and
        opens a private draw window for the mover — the table never blocks on
        the draw."""
        game = NinetyNineGame(options=NinetyNineOptions(autodraw=False))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)

        game.setup_keybinds()
        game.on_start()
        game.flush_menus()
        game.alive_player_ids = [player1.id, player2.id]
        game.set_turn_players([player1, player2])
        game.turn_index = 0
        game.count = 50
        player1.hand = [Card(id=99, rank=5, suit=SUIT_HEARTS)]
        game._update_turn_actions(player1)

        game.execute_action(player1, "card_slot_1")

        # Turn moved on at once; player1 holds an open draw window and has not
        # yet redrawn the card they played.
        assert game.current_player == player2
        assert player1.draw_timeout_ticks > 0
        assert player1.hand == []

    def test_manual_draw_window_lapse_forfeits_topup(self):
        """A human who lets the draw window lapse forfeits the top-up; the turn
        order is untouched because it advanced when they played."""
        game = NinetyNineGame(options=NinetyNineOptions(autodraw=False))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)

        game.setup_keybinds()
        game.on_start()
        game.flush_menus()
        game.alive_player_ids = [player1.id, player2.id]
        game.set_turn_players([player1, player2])
        game.turn_index = 0
        game.count = 50
        # Two cards so the lapse leaves a non-empty hand (no out-of-cards penalty).
        player1.hand = [
            Card(id=1, rank=5, suit=SUIT_HEARTS),
            Card(id=2, rank=4, suit=SUIT_HEARTS),
        ]
        game._update_turn_actions(player1)

        game.execute_action(player1, "card_slot_1")
        assert game.current_player == player2
        assert player1.draw_timeout_ticks > 0

        for _ in range(DRAW_TIMEOUT_TICKS + 1):
            game.on_tick()
            game.flush_menus()

        assert player1.draw_timeout_ticks == 0
        assert len(player1.hand) == 1  # forfeited the top-up
        assert game.current_player == player2  # turn order untouched

    def test_manual_draw_lands_focus_on_drawn_card(self):
        """Drawing should land the drawer's cursor on the card they drew, wherever
        it sorts into the hand — not on whatever slot the cursor last occupied."""
        game = NinetyNineGame(options=NinetyNineOptions(autodraw=False))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        game.setup_keybinds()
        game.on_start()
        game.flush_menus()
        game.alive_player_ids = [player1.id, player2.id]
        game.set_turn_players([player1, player2])
        game.turn_index = 0
        game.count = 50
        player1.hand = [
            Card(id=1, rank=3, suit=SUIT_HEARTS),
            Card(id=2, rank=9, suit=SUIT_HEARTS),
        ]
        # Open the draw window and rig the deck so the next draw is a known card
        # that sorts into the middle of the hand.
        player1.draw_timeout_ticks = DRAW_TIMEOUT_TICKS
        game.deck.cards = [Card(id=3, rank=6, suit=SUIT_HEARTS)]
        before_ids = {c.id for c in player1.hand}
        user1.messages.clear()

        game._action_draw_card(player1, "draw_card")
        game.flush_menus()

        drawn = next(c for c in player1.hand if c.id not in before_ids)
        expected_slot = f"card_slot_{player1.hand.index(drawn) + 1}"
        sel = None
        for msg in user1.messages:
            if msg.type == "show_menu" and msg.data.get("menu_id") == "turn_menu":
                sel = msg.data.get("selection_id")
        assert sel == expected_slot

    def test_manual_draw_without_available_card_speaks_feedback(self):
        """A manual draw that cannot recycle any card should not fail silently."""
        game = NinetyNineGame(options=NinetyNineOptions(autodraw=False))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        game.setup_keybinds()
        game.on_start()
        game.flush_menus()
        game.alive_player_ids = [player1.id, player2.id]
        game.deck.cards = []
        game.discard_pile = [Card(id=910, rank=7, suit=SUIT_HEARTS)]
        player1.draw_timeout_ticks = DRAW_TIMEOUT_TICKS
        user1.clear_messages()

        game._action_draw_card(player1, "draw_card")

        assert player1.draw_timeout_ticks == 0
        assert user1.get_last_spoken() == (
            "No card is available to draw. Continue with your current hand."
        )

    def test_milestone_elimination_does_not_wedge_manual_draw(self):
        """A player eliminated by a milestone-pass penalty on their own play must
        not be left holding an open draw window that strands the round.

        Crossing 66 costs the mover a token; if it was their last, they are
        eliminated while the round continues. Three players keep the game alive
        so the dead-mover path is reachable.
        """
        game = NinetyNineGame(options=NinetyNineOptions(autodraw=False))
        users = [MockUser(n) for n in ["Alice", "Bob", "Carol"]]
        players = [game.add_player(u.username, u) for u in users]
        game.setup_keybinds()
        game.on_start()
        game.flush_menus()
        game.alive_player_ids = [p.id for p in players]
        game.set_turn_players(players)
        game.turn_index = 0
        game.count = 63
        players[0].tokens = 1  # one token: passing 66 eliminates them
        for p in players[1:]:
            p.tokens = 3
        # A plain 5 takes 63 -> 68, passing the 66 milestone.
        players[0].hand = [Card(id=901, rank=5, suit=SUIT_HEARTS)]
        game._update_turn_actions(players[0])

        game.execute_action(players[0], "card_slot_1")

        # Eliminated, round still live, and crucially holding no draw window:
        # the dead-mover guard skips the draw entirely.
        assert players[0].tokens == 0
        assert players[0].id not in game.alive_player_ids
        assert game.game_active
        assert players[0].draw_timeout_ticks == 0
        # Turn has moved on to a living player who can actually act.
        assert game.current_player in players[1:]
        # Ticking must not spin on the dead seat.
        for _ in range(DRAW_TIMEOUT_TICKS + 5):
            game.on_tick()
            game.flush_menus()
        assert game.current_player in players[1:]

    def test_action_cards_bot_prefers_forcing_no_safe_response(self):
        """Bot should prefer a move that leaves the next player with no safe action-card play."""
        game = NinetyNineGame(options=NinetyNineOptions(rules_variant="action_cards"))
        bot_user = Bot("Bot1")
        opp_user = MockUser("Player2")
        bot_player = game.add_player("Bot1", bot_user)
        opp_player = game.add_player("Player2", opp_user)

        game.setup_keybinds()
        game.on_start()
        game.flush_menus()
        game.alive_player_ids = [bot_player.id, opp_player.id]
        game.set_turn_players([bot_player, opp_player])
        game.turn_index = 0
        game.count = 87
        bot_player.hand = [
            Card(id=1, rank=1, suit=SUIT_NONE),
            Card(id=2, rank=9, suit=SUIT_NONE),
            Card(id=3, rank=N99_RANK_PLUS_10, suit=SUIT_NONE),
        ]
        opp_player.hand = [
            Card(id=4, rank=8, suit=SUIT_NONE),
            Card(id=5, rank=9, suit=SUIT_NONE),
            Card(id=6, rank=N99_RANK_PLUS_10, suit=SUIT_NONE),
        ]

        assert game.bot_think(bot_player) in {"card_slot_2", "card_slot_3"}

    def test_eliminated_players_are_not_dealt_next_round(self):
        """Eliminated players should not keep stale hands or rejoin new rounds."""
        game = NinetyNineGame()
        users = [MockUser(name) for name in ["Alice", "Bob", "Carol"]]
        players = [game.add_player(user.username, user) for user in users]
        game.setup_keybinds()
        game.on_start()
        game.flush_menus()

        eliminated = players[2]
        eliminated.tokens = 0
        eliminated.hand = [Card(id=900, rank=5, suit=SUIT_HEARTS)]
        game._eliminate_player(eliminated)
        game._start_round()

        assert eliminated.hand == []
        assert eliminated.id not in game.alive_player_ids
        assert eliminated.id not in game.turn_player_ids
        assert all(len(player.hand) == game.options.hand_size for player in players[:2])

    def test_round_start_rotates_to_random_alive_player(self, monkeypatch):
        """Each round should keep seating order but choose a random first player."""
        game = NinetyNineGame()
        players = [
            game.add_player(name, MockUser(name))
            for name in ["Alice", "Bob", "Carol", "Dan"]
        ]
        game.status = "playing"
        game.game_active = True
        for player in players:
            player.tokens = game.options.starting_tokens
        monkeypatch.setattr(game, "_choose_round_start_index", lambda count: 2)

        game._start_round()

        assert game.turn_player_ids == [p.id for p in players[2:] + players[:2]]

    def test_round_transition_waits_before_starting_next_round(self):
        """Round-ending plays should pause before the next deal."""
        game = NinetyNineGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        game.setup_keybinds()
        game.on_start()
        game.flush_menus()
        game.alive_player_ids = [player1.id, player2.id]
        game.set_turn_players([player1, player2])
        game.turn_index = 0
        game.count = 95
        player1.hand = [Card(id=901, rank=12, suit=SUIT_HEARTS)]
        player2.hand = [Card(id=902, rank=5, suit=SUIT_HEARTS)]
        # Rebuild player1's turn actions so card_slot_1 reflects the overridden
        # hand. Without this it keeps the input-request of whatever card on_start
        # randomly dealt to slot 1 (an ace/ten opens a choice dialog instead of
        # playing), making the test depend on the deal rather than the rules.
        game._update_turn_actions(player1)
        round_before = game.round

        game.execute_action(player1, "card_slot_1")

        assert game.round == round_before
        assert game.round_timer_state == "counting"
        assert game.round_timer_ticks == ROUND_TRANSITION_SECONDS * 20
        assert game.active_sequences == []

        for _ in range(game.round_timer_ticks - 1):
            game.on_tick()
            game.flush_menus()
        assert game.round == round_before
        assert game.round_timer_state == "counting"

        game.on_tick()
        game.flush_menus()
        assert game.round == round_before + 1
        assert game.round_timer_state == "idle"
        assert game.round_timer_ticks == 0

    def test_host_can_pause_and_skip_round_transition_timer(self):
        """The host can pause the next-round timer and press P again to skip it."""
        game = NinetyNineGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        game.host = "Alice"
        game.setup_keybinds()
        game.on_start()
        game.flush_menus()
        round_before = game.round

        game._schedule_next_round()
        assert game._is_pause_timer_enabled(player1) is None
        assert game._is_pause_timer_enabled(player2) == "action-not-host"
        ticks_before_pause = game.round_timer_ticks

        user1.clear_messages()
        game._action_pause_timer(player1, "pause_timer")

        assert game.round_timer_state == "paused"
        assert game.round_timer_ticks == ticks_before_pause
        assert user1.get_last_spoken() == (
            "Alice has paused the game (press p to start the next round)."
        )

        for _ in range(5):
            game.on_tick()
            game.flush_menus()

        assert game.round == round_before
        assert game.round_timer_state == "paused"
        assert game.round_timer_ticks == ticks_before_pause

        game._action_pause_timer(player1, "pause_timer")
        game.flush_menus()

        assert game.round == round_before + 1
        assert game.round_timer_state == "idle"
        assert game.round_timer_ticks == 0

    def test_paused_round_timer_survives_restore(self):
        """A restored paused timer should stay paused until the host skips it."""
        game = NinetyNineGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.host = "Alice"
        game.setup_keybinds()
        game.on_start()
        game._schedule_next_round()
        game._action_pause_timer(player1, "pause_timer")
        round_before = game.round
        ticks_before_restore = game.round_timer_ticks

        restored = NinetyNineGame.from_json(game.to_json())
        restored.rebuild_runtime_state()

        for _ in range(5):
            restored.on_tick()

        assert restored.round == round_before
        assert restored.round_timer_state == "paused"
        assert restored.round_timer_ticks == ticks_before_restore

        restored._action_pause_timer(restored.players[0], "pause_timer")

        assert restored.round == round_before + 1
        assert restored.round_timer_state == "idle"
        assert restored.round_timer_ticks == 0

    def test_menu_rebuild_refreshes_card_labels_for_reclaimed_locale(self):
        """Rebuilt dynamic card actions should use the currently attached user locale."""
        from ..game_utils.cards import card_name

        game = NinetyNineGame()
        user = MockUser("Alice", locale="vi")
        opponent_user = MockUser("Bob")
        player = game.add_player("Alice", user)
        opponent = game.add_player("Bob", opponent_user)
        game.setup_keybinds()
        game.on_start()
        game.flush_menus()
        game.alive_player_ids = [player.id, opponent.id]
        game.set_turn_players([player, opponent])
        card = Card(id=903, rank=1, suit=SUIT_HEARTS)
        player.hand = [card]

        game._users.pop(player.id, None)
        game._update_turn_actions(player)
        action = game.get_action_set(player, "turn").get_action("card_slot_1")
        assert action is not None
        assert action.label == card_name(card, "en")

        game.attach_user(player.id, user)
        game.refresh_menus(player)
        game.flush_menus()
        items = user.get_current_menu_items("turn_menu")
        check_count_action = game.get_action_set(player, "standard").get_action("check_count")

        assert items is not None
        assert any(
            isinstance(item, MenuItem)
            and item.id == "card_slot_1"
            and item.text == card_name(card, "vi")
            for item in items
        )
        assert check_count_action is not None
        assert (
            game.resolve_action(player, check_count_action).label
            == Localization.get("vi", "ninetynine-check-count")
        )


class TestNinetyNineChoiceDialogs:
    """Regression tests for shared choice dialogs and turn checks."""

    def setup_method(self):
        self.game = NinetyNineGame()
        self.user1 = MockUser("Alice")
        self.user2 = MockUser("Bob")
        self.player1 = self.game.add_player("Alice", self.user1)
        self.player2 = self.game.add_player("Bob", self.user2)
        self.game.setup_keybinds()
        self.game.on_start()
        self.game.flush_menus()
        self.game.alive_player_ids = [self.player1.id, self.player2.id]
        self.game.set_turn_players([self.player1, self.player2])
        self.game.turn_index = 0
        self.game.count = 50
        self.player1.hand = []
        self.player2.hand = [Card(id=999, rank=5, suit=SUIT_HEARTS)]
        self.game.pending_choice = None
        self.game.pending_card_index = -1
        self.game._update_all_turn_actions()

    def _menu_items(self) -> list[MenuItem]:
        items = self.user1.get_current_menu_items("action_input_menu")
        assert items is not None
        assert all(isinstance(item, MenuItem) for item in items)
        return items  # type: ignore[return-value]

    def test_out_of_turn_choice_card_does_not_open_dialog(self):
        """Out-of-turn clicks should announce the turn block before opening a choice menu."""
        self.player1.hand = [Card(id=1, rank=1, suit=SUIT_HEARTS)]
        self.game.turn_index = 1
        self.game._update_turn_actions(self.player1)
        self.user1.clear_messages()

        self.game.execute_action(self.player1, "card_slot_1")

        assert self.user1.get_last_spoken() == "It's not your turn."
        assert "action_input_menu" not in self.user1.menus

    def test_out_of_turn_card_actions_are_visible_but_disabled(self):
        """Hand cards should anchor focus without appearing currently playable."""
        self.player1.hand = [Card(id=5, rank=5, suit=SUIT_HEARTS)]
        self.game.turn_index = 1
        self.game._update_turn_actions(self.player1)

        action_set = self.game.get_action_set(self.player1, "turn")
        assert action_set is not None
        action = action_set.get_action("card_slot_1")
        assert action is not None

        resolved = action_set.resolve_action(self.game, self.player1, action)

        assert resolved.visible is True
        assert resolved.enabled is False
        assert resolved.disabled_reason == "action-not-your-turn"

    def test_ace_choice_dialog_includes_cancel(self):
        """Ace choices should use the shared action input menu with a cancel item."""
        self.player1.hand = [Card(id=1, rank=1, suit=SUIT_HEARTS)]
        self.game._update_turn_actions(self.player1)

        self.game.execute_action(self.player1, "card_slot_1")

        items = self._menu_items()
        assert [item.text for item in items[:-1]] == ["Add 11", "Add 1"]
        assert items[-1].id == "_cancel"

    def test_ten_choice_dialog_includes_cancel(self):
        """Ten choices should use the same shared menu flow."""
        self.player1.hand = [Card(id=10, rank=10, suit=SUIT_HEARTS)]
        self.game._update_turn_actions(self.player1)

        self.game.execute_action(self.player1, "card_slot_1")

        items = self._menu_items()
        assert [item.text for item in items[:-1]] == ["Add 10", "Subtract 10"]
        assert items[-1].id == "_cancel"

    def test_choice_input_resolves_card_play(self):
        """Submitting a choice should play the card immediately with the selected value."""
        self.player1.hand = [Card(id=1, rank=1, suit=SUIT_HEARTS)]
        self.game._update_turn_actions(self.player1)

        self.game.execute_action(self.player1, "card_slot_1", "Add 11")

        assert self.game.count == 61
        assert all(card.id != 1 for card in self.player1.hand)
        assert self.game.pending_choice is None
        assert self.game.current_player == self.player2

    def test_single_valid_choice_auto_selects_instead_of_opening_dialog(self):
        """Single-outcome Ace plays should not open a choice dialog."""
        self.game.count = 97
        self.player1.hand = [Card(id=1, rank=1, suit=SUIT_HEARTS)]
        self.game._update_turn_actions(self.player1)
        self.user1.clear_messages()

        self.game.execute_action(self.player1, "card_slot_1")

        assert "action_input_menu" not in self.user1.menus
        assert self.game.count == 98
        assert all(card.id != 1 for card in self.player1.hand)
        assert self.game.current_player == self.player2

    def test_legacy_pending_choice_uses_shared_menu_and_cancel(self):
        """Saved pending choices should still reopen through the same dialog style."""
        self.player1.hand = [Card(id=10, rank=10, suit=SUIT_HEARTS)]
        self.game.pending_choice = "ten"
        self.game.pending_card_index = 0
        self.game._update_turn_actions(self.player1)

        action = self.game.get_action_set(self.player1, "turn").get_action("resolve_choice")
        assert action is not None
        self.game.execute_action(self.player1, "resolve_choice")

        items = self._menu_items()
        assert [item.text for item in items[:-1]] == ["Add 10", "Subtract 10"]
        assert items[-1].id == "_cancel"

    def test_legacy_single_valid_choice_auto_resolves(self):
        """Saved pending choices with one valid outcome should not reopen a dialog."""
        # Use a synthetic id well outside the deck's range so the auto-drawn
        # replacement card can't coincidentally share it (the deck contains a
        # real id=1 card; colliding made this assertion depend on the deal).
        ace_id = 9001
        self.game.count = 97
        self.player1.hand = [Card(id=ace_id, rank=1, suit=SUIT_HEARTS)]
        self.game.pending_choice = "ace"
        self.game.pending_card_index = 0
        self.game._update_turn_actions(self.player1)

        self.game.execute_action(self.player1, "resolve_choice")

        assert "action_input_menu" not in self.user1.menus
        assert self.game.count == 98
        assert all(card.id != ace_id for card in self.player1.hand)

    def test_subtract_ten_floors_at_zero(self):
        """Negative-value plays should never push the count below zero."""
        self.game.count = 5
        self.player1.hand = [Card(id=10, rank=10, suit=SUIT_HEARTS)]
        self.game._update_turn_actions(self.player1)

        self.game.execute_action(self.player1, "card_slot_1", "Subtract 10")

        assert self.game.count == 0

    def test_corrupt_negative_count_is_repaired_before_two_effect(self):
        """A stale negative count should not be doubled into a larger negative value."""
        self.game.count = -7_104_963_754_562
        self.player1.hand = [Card(id=2, rank=2, suit=SUIT_HEARTS)]
        self.game._update_turn_actions(self.player1)

        self.game.execute_action(self.player1, "card_slot_1")

        assert self.game.count == 0


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
        game.flush_menus()

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
        game.flush_menus()

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
            game.flush_menus()

        # Game should complete without errors
        assert not game.game_active or tick == max_ticks - 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

