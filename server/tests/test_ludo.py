"""
Tests for the Ludo game.

Unit tests, action tests, play tests with bots, and persistence tests.
"""

import json
import random

import pytest

from ..games.ludo.game import (
    LudoGame,
    LudoOptions,
    LudoPlayer,
    LudoToken,
    COLOR_STARTS,
    COLOR_ENTRIES,
    HOME_COLUMN_LENGTH,
    TRACK_LENGTH,
    ALL_START_POSITIONS,
    SAFE_SQUARES,
)
from ..users.test_user import MockUser
from ..users.bot import Bot


class TestLudoUnit:
    """Unit tests for Ludo game functions."""

    def test_game_creation(self):
        game = LudoGame()
        assert game.get_name() == "Ludo"
        assert game.get_type() == "ludo"
        assert game.get_category() == "category-board-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 4

    def test_player_creation(self):
        game = LudoGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        assert player.name == "Alice"
        assert player.is_bot is False

    def test_options_defaults(self):
        game = LudoGame()
        assert game.options.max_consecutive_sixes == 3
        assert game.options.safe_start_squares is True

    def test_custom_options(self):
        options = LudoOptions(max_consecutive_sixes=5, safe_start_squares=False)
        game = LudoGame(options=options)
        assert game.options.max_consecutive_sixes == 5
        assert game.options.safe_start_squares is False

    def test_color_assignment(self):
        game = LudoGame()
        users = [MockUser(f"P{i}") for i in range(4)]
        for u in users:
            game.add_player(u.username, u)
        game.on_start()

        colors = [p.color for p in game.players]
        assert colors == ["red", "blue", "green", "yellow"]

    def test_token_initialization(self):
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        for player in game.players:
            assert len(player.tokens) == 4
            for j, token in enumerate(player.tokens):
                assert token.state == "yard"
                assert token.position == 0
                assert token.token_number == j + 1

    def test_can_token_move_yard(self):
        game = LudoGame()
        token = LudoToken(state="yard", position=0, token_number=1)
        assert game._can_token_move(token, 6) is True
        assert game._can_token_move(token, 5) is False
        assert game._can_token_move(token, 1) is False

    def test_can_token_move_track(self):
        game = LudoGame()
        token = LudoToken(state="track", position=10, token_number=1)
        assert game._can_token_move(token, 1) is True
        assert game._can_token_move(token, 6) is True

    def test_can_token_move_home_column(self):
        game = LudoGame()
        token = LudoToken(state="home_column", position=3, token_number=1)
        assert game._can_token_move(token, 3) is True  # reaches exactly 6
        assert game._can_token_move(token, 4) is False  # overshoots
        assert game._can_token_move(token, 2) is True

    def test_can_token_move_finished(self):
        game = LudoGame()
        token = LudoToken(state="finished", position=6, token_number=1)
        assert game._can_token_move(token, 1) is False

    def test_safe_squares_fixed(self):
        game = LudoGame()
        game.options.safe_start_squares = False
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()
        player = game.players[0]

        for sq in SAFE_SQUARES:
            assert game._is_safe_square(sq, player) is True
        assert game._is_safe_square(10, player) is False

    def test_safe_squares_with_start_option(self):
        """When safe_start_squares is on, ALL players' start squares are safe."""
        game = LudoGame()
        game.options.safe_start_squares = True
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()
        player = game.players[0]  # Red

        # All start positions should be safe, not just the moving player's
        for pos in ALL_START_POSITIONS:
            assert game._is_safe_square(pos, player) is True

    def test_safe_squares_without_start_option(self):
        game = LudoGame()
        game.options.safe_start_squares = False
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()
        player = game.players[0]

        for pos in ALL_START_POSITIONS:
            if pos not in SAFE_SQUARES:
                assert game._is_safe_square(pos, player) is False

    def test_track_wrapping(self):
        """Test that track positions wrap correctly at 52."""
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        # Use Blue (home_entry=12) and put token well past entry
        # so it doesn't trigger home column logic
        player = game.players[1]  # Blue, home_entry=12
        token = player.tokens[0]
        token.state = "track"
        token.position = 50

        # Blue's home_entry is 12, so position 50 -> 50+5=55, not crossing 12
        # Wraps: (55-1) % 52 + 1 = 54 % 52 + 1 = 2 + 1 = 3
        game._move_token(player, token, 5)
        assert token.position == 3
        assert token.state == "track"

    def test_enter_home_column(self):
        """Token entering home column from track."""
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        player = game.players[0]  # Red, home_entry=51
        token = player.tokens[0]
        token.state = "track"
        token.position = 49  # 2 away from home entry

        game._move_token(player, token, 4)
        # overshoot = 49 + 4 - 51 = 2
        assert token.state == "home_column"
        assert token.position == 2

    def test_finish_from_home_column(self):
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        player = game.players[0]
        token = player.tokens[0]
        token.state = "home_column"
        token.position = 4

        game._move_token(player, token, 2)
        assert token.state == "finished"
        assert player.finished_count == 1

    def test_finish_from_track(self):
        """Token finishing directly from track (overshoot >= home_column_length)."""
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        player = game.players[0]  # Red, home_entry=51
        token = player.tokens[0]
        token.state = "track"
        token.position = 49

        # Move 8: overshoot = 49 + 8 - 51 = 6 >= HOME_COLUMN_LENGTH
        game._move_token(player, token, 8)
        assert token.state == "finished"
        assert player.finished_count == 1

    def test_capture(self):
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        attacker = game.players[0]  # Red
        victim = game.players[1]  # Blue

        # Put victim token on track at position 10 (not safe)
        victim.tokens[0].state = "track"
        victim.tokens[0].position = 10

        # Put attacker token on track nearby
        attacker.tokens[0].state = "track"
        attacker.tokens[0].position = 8

        game._move_token(attacker, attacker.tokens[0], 2)
        assert attacker.tokens[0].position == 10
        assert victim.tokens[0].state == "yard"
        assert victim.tokens[0].position == 0

    def test_no_capture_on_safe_square(self):
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        attacker = game.players[0]
        victim = game.players[1]

        # Put victim on safe square 9
        victim.tokens[0].state = "track"
        victim.tokens[0].position = 9

        attacker.tokens[0].state = "track"
        attacker.tokens[0].position = 7

        game._move_token(attacker, attacker.tokens[0], 2)
        assert attacker.tokens[0].position == 9
        # Victim should NOT be captured
        assert victim.tokens[0].state == "track"
        assert victim.tokens[0].position == 9

    def test_capture_all_tokens_in_opponent_stack(self):
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        attacker = game.players[0]
        victim = game.players[1]

        victim.tokens[0].state = "track"
        victim.tokens[0].position = 10
        victim.tokens[1].state = "track"
        victim.tokens[1].position = 10

        attacker.tokens[0].state = "track"
        attacker.tokens[0].position = 8

        game._move_token(attacker, attacker.tokens[0], 2)

        assert attacker.tokens[0].position == 10
        assert victim.tokens[0].state == "yard"
        assert victim.tokens[0].position == 0
        assert victim.tokens[1].state == "yard"
        assert victim.tokens[1].position == 0

    def test_capture_multiple_opponents_on_same_square(self):
        game = LudoGame()
        for i in range(3):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        attacker = game.players[0]
        victim_one = game.players[1]
        victim_two = game.players[2]

        victim_one.tokens[0].state = "track"
        victim_one.tokens[0].position = 10
        victim_two.tokens[0].state = "track"
        victim_two.tokens[0].position = 10

        attacker.tokens[0].state = "track"
        attacker.tokens[0].position = 8

        game._move_token(attacker, attacker.tokens[0], 2)

        assert victim_one.tokens[0].state == "yard"
        assert victim_two.tokens[0].state == "yard"

    def test_own_stack_is_not_captured(self):
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        player = game.players[0]

        player.tokens[0].state = "track"
        player.tokens[0].position = 8
        player.tokens[1].state = "track"
        player.tokens[1].position = 10

        game._move_token(player, player.tokens[0], 2)

        assert player.tokens[0].state == "track"
        assert player.tokens[0].position == 10
        assert player.tokens[1].state == "track"
        assert player.tokens[1].position == 10

    def test_enter_board_from_yard(self):
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        player = game.players[0]  # Red
        token = player.tokens[0]
        assert token.state == "yard"

        game._move_token(player, token, 6)
        assert token.state == "track"
        assert token.position == COLOR_STARTS["red"]

    def test_enter_board_from_yard_can_capture_on_unsafe_start_square(self):
        game = LudoGame(options=LudoOptions(safe_start_squares=False))
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        attacker = game.players[0]
        victim = game.players[1]
        victim.tokens[0].state = "track"
        victim.tokens[0].position = COLOR_STARTS["red"]

        game._move_token(attacker, attacker.tokens[0], 6)

        assert attacker.tokens[0].position == COLOR_STARTS["red"]
        assert victim.tokens[0].state == "yard"

    def test_non_red_token_enters_home_column_across_wrap_boundary(self):
        game = LudoGame()
        for i in range(2):
            game.add_player(f"P{i}", MockUser(f"P{i}"))
        game.on_start()

        player = game.players[1]  # Blue, home entry 12
        token = player.tokens[0]
        token.state = "track"
        token.position = 11

        game._move_token(player, token, 2)

        assert token.state == "home_column"
        assert token.position == 1

    def test_token_index_from_action(self):
        game = LudoGame()
        assert game._token_index_from_action("move_token_1") == 0
        assert game._token_index_from_action("move_token_4") == 3
        assert game._token_index_from_action("move_token_5") is None
        assert game._token_index_from_action("roll_dice") is None

    def test_serialization(self):
        game = LudoGame()
        u1 = MockUser("Alice")
        u2 = MockUser("Bob")
        game.add_player("Alice", u1)
        game.add_player("Bob", u2)
        game.on_start()

        # Modify some state
        game.players[0].tokens[0].state = "track"
        game.players[0].tokens[0].position = 15
        game.players[0].finished_count = 1
        game.last_roll = 4
        game.consecutive_sixes = 2

        json_str = game.to_json()
        data = json.loads(json_str)

        assert data["last_roll"] == 4
        assert data["consecutive_sixes"] == 2

        loaded = LudoGame.from_json(json_str)
        assert loaded.last_roll == 4
        assert loaded.consecutive_sixes == 2
        assert loaded.players[0].tokens[0].state == "track"
        assert loaded.players[0].tokens[0].position == 15
        assert loaded.players[0].finished_count == 1


class TestLudoActions:
    """Test action visibility and enablement."""

    def setup_method(self):
        self.game = LudoGame()
        self.u1 = MockUser("Alice")
        self.u2 = MockUser("Bob")
        self.p1 = self.game.add_player("Alice", self.u1)
        self.p2 = self.game.add_player("Bob", self.u2)
        self.game.on_start()

    def test_roll_visible_for_current_player(self):
        visible = self.game.get_all_visible_actions(self.p1)
        visible_ids = [a.action.id for a in visible]
        assert "roll_dice" in visible_ids

    def test_roll_hidden_for_other_player(self):
        visible = self.game.get_all_visible_actions(self.p2)
        visible_ids = [a.action.id for a in visible]
        assert "roll_dice" not in visible_ids

    def test_move_tokens_hidden_before_roll(self):
        visible = self.game.get_all_visible_actions(self.p1)
        visible_ids = [a.action.id for a in visible]
        for i in range(1, 5):
            assert f"move_token_{i}" not in visible_ids

    def test_move_tokens_visible_after_roll_with_options(self):
        # Give player multiple moveable tokens
        self.p1.tokens[0].state = "track"
        self.p1.tokens[0].position = 5
        self.p1.tokens[1].state = "track"
        self.p1.tokens[1].position = 10
        self.game.last_roll = 3
        self.p1.move_options = {
            0: "Token 1 (position 5)",
            1: "Token 2 (position 10)",
        }

        visible = self.game.get_all_visible_actions(self.p1)
        visible_ids = [a.action.id for a in visible]
        assert "move_token_1" in visible_ids
        assert "move_token_2" in visible_ids
        assert "move_token_3" not in visible_ids
        assert "roll_dice" not in visible_ids  # Should be hidden when move_options set

    def test_check_board_always_enabled(self):
        result = self.game._is_check_board_enabled(self.p1)
        assert result is None

    def test_check_board_shows_player_info(self):
        self.game.execute_action(self.p1, "check_board")
        spoken = self.u1.get_spoken_messages()
        assert any("Alice" in msg for msg in spoken)

    def test_choose_token_prompt_is_announced(self, monkeypatch):
        self.p1.tokens[0].state = "track"
        self.p1.tokens[0].position = 5
        self.u1.clear_messages()

        def fake_randint(start, end):
            if (start, end) == (1, 6):
                return 6
            return 1

        monkeypatch.setattr(random, "randint", fake_randint)

        self.game.execute_action(self.p1, "roll_dice")

        spoken = self.u1.get_spoken_messages()
        assert any("Select token to move" in msg for msg in spoken)

    def test_web_standard_actions_follow_project_order(self):
        self.u1.client_type = "web"

        standard_set = self.game.create_standard_action_set(self.p1)
        order = standard_set._order

        check_board_idx = order.index("check_board")
        check_scores_idx = order.index("check_scores")
        whose_turn_idx = order.index("whose_turn")
        whos_at_table_idx = order.index("whos_at_table")

        assert check_board_idx < check_scores_idx
        assert check_scores_idx < whose_turn_idx
        assert whose_turn_idx < whos_at_table_idx


class TestLudoConsecutiveSixes:
    """Test the consecutive-6 penalty mechanic."""

    def setup_method(self):
        self.game = LudoGame()
        self.u1 = MockUser("Alice")
        self.u2 = MockUser("Bob")
        self.p1 = self.game.add_player("Alice", self.u1)
        self.p2 = self.game.add_player("Bob", self.u2)
        self.game.on_start()

    def test_extra_turn_on_six(self):
        # Put a token on track so the 6 has a valid move
        self.p1.tokens[0].state = "track"
        self.p1.tokens[0].position = 10

        # Force roll of 6
        random.seed(0)
        for seed in range(1000):
            random.seed(seed)
            if random.randint(1, 6) == 6:
                random.seed(seed)
                break

        old_player = self.game.current_player
        self.game.execute_action(self.p1, "roll_dice")
        # After rolling 6 with only one moveable token, it auto-moves
        # and grants extra turn — current player stays the same
        assert self.game.current_player == old_player

    def test_penalty_after_max_sixes(self):
        """Rolling max consecutive 6s should undo all moves from this turn."""
        self.game.options.max_consecutive_sixes = 2

        # Put a token on track
        self.p1.tokens[0].state = "track"
        self.p1.tokens[0].position = 10

        # Save initial state for comparison
        initial_pos = self.p1.tokens[0].position

        # Simulate two consecutive 6s
        self.game.consecutive_sixes = 1
        self.game.last_roll = 6
        self.game.extra_turn = False

        # The turn_start_state was saved at turn start
        # Force a roll of 6 and execute
        for seed in range(1000):
            random.seed(seed)
            if random.randint(1, 6) == 6:
                random.seed(seed)
                break

        self.game.execute_action(self.p1, "roll_dice")

        # After penalty, token should be back to initial state
        # (from turn_start_state restore)
        assert self.p1.tokens[0].position == initial_pos

    def test_first_six_triggers_penalty_when_limit_is_one(self):
        self.game.options.max_consecutive_sixes = 1
        token = self.p1.tokens[0]
        self.game.turn_start_state = self.game._save_turn_state()

        self.game._move_token(self.p1, token, 6)
        assert token.state == "track"

        self.game.last_roll = 6
        self.game._after_move(self.p1)

        assert token.state == "yard"
        assert token.position == 0

    def test_no_penalty_when_disabled(self):
        """max_consecutive_sixes=0 should disable the penalty."""
        self.game.options.max_consecutive_sixes = 0

        self.p1.tokens[0].state = "track"
        self.p1.tokens[0].position = 10

        # Simulate high consecutive sixes
        self.game.consecutive_sixes = 10
        self.game.last_roll = 6

        for seed in range(1000):
            random.seed(seed)
            if random.randint(1, 6) == 6:
                random.seed(seed)
                break

        old_player = self.game.current_player
        self.game.execute_action(self.p1, "roll_dice")
        # Should still be same player's turn (extra turn granted, no penalty)
        assert self.game.current_player == old_player


class TestLudoBot:
    def test_bot_prefers_larger_stack_capture(self):
        game = LudoGame(options=LudoOptions(safe_start_squares=False))
        human = MockUser("Human")
        bot = Bot("Bot")
        victim = MockUser("Victim")
        game.add_player("Human", human)
        game.add_player("Bot", bot)
        game.add_player("Victim", victim)
        game.on_start()

        bot_player = game.players[1]
        human_player = game.players[0]
        victim_player = game.players[2]
        game.set_turn_players([bot_player, human_player, victim_player])
        game.current_player = bot_player
        game.last_roll = 2

        bot_player.tokens[0].state = "track"
        bot_player.tokens[0].position = 8
        bot_player.tokens[1].state = "track"
        bot_player.tokens[1].position = 20
        victim_player.tokens[0].state = "track"
        victim_player.tokens[0].position = 10
        victim_player.tokens[1].state = "track"
        victim_player.tokens[1].position = 10
        human_player.tokens[0].state = "track"
        human_player.tokens[0].position = 22

        bot_player.move_options = {0: "capture two", 1: "capture one"}

        assert game.bot_think(bot_player) == "move_token_1"


class TestLudoPlayTest:
    """Play tests that run complete games with bots."""

    def test_two_player_game_completes(self):
        random.seed(42)
        game = LudoGame()
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)
        game.on_start()

        max_ticks = 50000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            if tick % 200 == 0 and tick > 0:
                json_str = game.to_json()
                game = LudoGame.from_json(json_str)
                game.attach_user("Bot1", bot1)
                game.attach_user("Bot2", bot2)
                game.rebuild_runtime_state()
                for player in game.players:
                    game.setup_player_actions(player)
            game.on_tick()

        assert not game.game_active, "Game should have ended"
        winner = [p for p in game.players if p.finished_count >= 4]
        assert len(winner) == 1

    def test_four_player_game_completes(self):
        random.seed(123)
        game = LudoGame()
        bots = [Bot(f"Bot{i}") for i in range(1, 5)]
        for bot in bots:
            game.add_player(bot.username, bot)
        game.on_start()

        max_ticks = 100000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            if tick % 200 == 0 and tick > 0:
                json_str = game.to_json()
                game = LudoGame.from_json(json_str)
                for bot in bots:
                    game.attach_user(bot.username, bot)
                game.rebuild_runtime_state()
                for player in game.players:
                    game.setup_player_actions(player)
            game.on_tick()

        assert not game.game_active, "4-player game should have ended"

    def test_human_and_bot_game(self):
        random.seed(789)
        game = LudoGame()
        human = MockUser("Human")
        bot = Bot("Bot")
        game.add_player("Human", human)
        game.add_player("Bot", bot)
        game.on_start()

        max_ticks = 50000
        for tick in range(max_ticks):
            if not game.game_active:
                break
            if tick % 200 == 0 and tick > 0:
                json_str = game.to_json()
                game = LudoGame.from_json(json_str)
                game.attach_user("Human", human)
                game.attach_user("Bot", bot)
                game.rebuild_runtime_state()
                for player in game.players:
                    game.setup_player_actions(player)

            current = game.current_player
            if current and current.name == "Human" and not game.is_rolling:
                if current.move_options:
                    first_idx = next(iter(current.move_options))
                    game.execute_action(current, f"move_token_{first_idx + 1}")
                else:
                    game.execute_action(current, "roll_dice")
            game.on_tick()

        assert not game.game_active

    def test_game_with_safe_start_disabled(self):
        random.seed(456)
        game = LudoGame(options=LudoOptions(safe_start_squares=False))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)
        game.on_start()

        for tick in range(50000):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active

    def test_game_with_no_six_penalty(self):
        random.seed(321)
        game = LudoGame(options=LudoOptions(max_consecutive_sixes=0))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)
        game.on_start()

        for tick in range(50000):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active


class TestLudoPersistence:
    """Test game state persistence."""

    def test_full_state_preserved(self):
        game = LudoGame(options=LudoOptions(max_consecutive_sixes=5, safe_start_squares=False))
        u1 = MockUser("Alice")
        u2 = MockUser("Bob")
        game.add_player("Alice", u1)
        game.add_player("Bob", u2)
        game.on_start()

        # Modify state
        game.players[0].tokens[0].state = "track"
        game.players[0].tokens[0].position = 25
        game.players[0].tokens[1].state = "home_column"
        game.players[0].tokens[1].position = 3
        game.players[0].finished_count = 2
        game.last_roll = 5
        game.consecutive_sixes = 1
        game.extra_turn = True

        json_str = game.to_json()
        loaded = LudoGame.from_json(json_str)

        assert loaded.game_active is True
        assert loaded.options.max_consecutive_sixes == 5
        assert loaded.options.safe_start_squares is False
        assert loaded.last_roll == 5
        assert loaded.consecutive_sixes == 1
        assert loaded.extra_turn is True
        assert loaded.players[0].tokens[0].state == "track"
        assert loaded.players[0].tokens[0].position == 25
        assert loaded.players[0].tokens[1].state == "home_column"
        assert loaded.players[0].tokens[1].position == 3
        assert loaded.players[0].finished_count == 2

    def test_actions_work_after_reload(self):
        game = LudoGame()
        user = MockUser("Alice")
        bot = Bot("Bot")
        game.add_player("Alice", user)
        game.add_player("Bot", bot)
        game.on_start()

        # Save and reload
        json_str = game.to_json()
        game = LudoGame.from_json(json_str)
        game.attach_user("Alice", user)
        game.attach_user("Bot", bot)
        for player in game.players:
            game.setup_player_actions(player)

        actions = game.get_all_enabled_actions(game.players[0])
        assert len(actions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
