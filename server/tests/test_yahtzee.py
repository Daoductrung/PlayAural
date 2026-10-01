"""
Tests for the Yahtzee game.
"""

import json
from pathlib import Path
import re

from ..games.yahtzee.game import (
    YahtzeeGame,
    YahtzeePlayer,
    YahtzeeOptions,
    calculate_score,
    is_yahtzee,
    count_dice,
    ALL_CATEGORIES,
    UPPER_CATEGORIES,
    LOWER_CATEGORIES,
)
from ..game_utils.stats_extractor import StatsExtractor
from ..users.base import MenuItem
from ..users.test_user import MockUser
from ..users.bot import Bot
from ..users.preferences import DiceKeepingStyle


LOCALES_DIR = Path(__file__).parent.parent / "locales"


def _ftl_messages(text: str) -> dict[str, set[str]]:
    messages: dict[str, set[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line and not line[0].isspace() and "=" in line and not line.startswith("#"):
            current = line.split("=", 1)[0].strip()
            messages[current] = set(re.findall(r"\{\s*\$(\w+)", line))
            continue
        if current:
            messages[current].update(re.findall(r"\{\s*\$(\w+)", line))
    return messages


def _menu_texts(items: list[str | MenuItem]) -> list[str]:
    return [item.text if isinstance(item, MenuItem) else item for item in items]


class TestYahtzeeScoring:
    """Unit tests for Yahtzee scoring functions."""

    def test_count_dice(self):
        """Test dice counting."""
        counts = count_dice([1, 1, 2, 3, 3])
        assert counts[1] == 2
        assert counts[2] == 1
        assert counts[3] == 2
        assert counts[4] == 0
        assert counts[5] == 0
        assert counts[6] == 0

    def test_is_yahtzee(self):
        """Test Yahtzee detection."""
        assert is_yahtzee([5, 5, 5, 5, 5]) is True
        assert is_yahtzee([1, 1, 1, 1, 1]) is True
        assert is_yahtzee([5, 5, 5, 5, 4]) is False
        assert is_yahtzee([1, 2, 3, 4, 5]) is False
        assert is_yahtzee([]) is False
        assert is_yahtzee([5, 5, 5, 5]) is False

    def test_upper_section_scoring(self):
        """Test upper section category scoring."""
        dice = [1, 1, 2, 3, 6]
        assert calculate_score(dice, "ones") == 2  # 1+1
        assert calculate_score(dice, "twos") == 2  # 2
        assert calculate_score(dice, "threes") == 3  # 3
        assert calculate_score(dice, "fours") == 0  # no 4s
        assert calculate_score(dice, "fives") == 0  # no 5s
        assert calculate_score(dice, "sixes") == 6  # 6

    def test_three_of_a_kind(self):
        """Test three of a kind scoring."""
        assert calculate_score([3, 3, 3, 1, 2], "three_kind") == 12  # sum all
        assert calculate_score([5, 5, 5, 5, 1], "three_kind") == 21  # 4 of a kind counts
        assert calculate_score([1, 2, 3, 4, 5], "three_kind") == 0  # no three of a kind

    def test_four_of_a_kind(self):
        """Test four of a kind scoring."""
        assert calculate_score([4, 4, 4, 4, 2], "four_kind") == 18  # sum all
        assert calculate_score([6, 6, 6, 6, 6], "four_kind") == 30  # yahtzee counts
        assert calculate_score([3, 3, 3, 1, 2], "four_kind") == 0  # only three

    def test_full_house(self):
        """Test full house scoring."""
        assert calculate_score([2, 2, 3, 3, 3], "full_house") == 25
        assert calculate_score([5, 5, 5, 2, 2], "full_house") == 25
        assert calculate_score([1, 1, 1, 1, 1], "full_house") == 0  # Joker rule is scorecard-based
        assert calculate_score([1, 1, 2, 3, 3], "full_house") == 0
        assert calculate_score([1, 2, 3, 4, 5], "full_house") == 0

    def test_small_straight(self):
        """Test small straight scoring."""
        assert calculate_score([1, 2, 3, 4, 6], "small_straight") == 30
        assert calculate_score([2, 3, 4, 5, 1], "small_straight") == 30
        assert calculate_score([3, 4, 5, 6, 1], "small_straight") == 30
        assert calculate_score([1, 2, 3, 5, 6], "small_straight") == 0

    def test_large_straight(self):
        """Test large straight scoring."""
        assert calculate_score([1, 2, 3, 4, 5], "large_straight") == 40
        assert calculate_score([2, 3, 4, 5, 6], "large_straight") == 40
        assert calculate_score([1, 2, 3, 4, 6], "large_straight") == 0

    def test_yahtzee_scoring(self):
        """Test Yahtzee category scoring."""
        assert calculate_score([6, 6, 6, 6, 6], "yahtzee") == 50
        assert calculate_score([1, 1, 1, 1, 1], "yahtzee") == 50
        assert calculate_score([5, 5, 5, 5, 4], "yahtzee") == 0

    def test_chance_scoring(self):
        """Test chance category scoring."""
        assert calculate_score([1, 2, 3, 4, 5], "chance") == 15
        assert calculate_score([6, 6, 6, 6, 6], "chance") == 30
        assert calculate_score([1, 1, 1, 1, 1], "chance") == 5


class TestYahtzeePlayer:
    """Tests for YahtzeePlayer."""

    def test_player_defaults(self):
        """Test player default values."""
        player = YahtzeePlayer(id="123", name="Test")
        assert player.dice.num_dice == 5
        assert player.dice.has_rolled is False
        assert player.dice.kept == []
        assert player.rolls_left == 3
        assert all(player.scores.get(cat) is None for cat in ALL_CATEGORIES)
        assert player.yahtzee_bonus_count == 0
        assert player.upper_bonus_awarded is False

    def test_get_upper_total(self):
        """Test upper section total calculation."""
        player = YahtzeePlayer(id="123", name="Test")
        player.scores["ones"] = 3
        player.scores["twos"] = 6
        player.scores["threes"] = 9
        assert player.get_upper_total() == 18

    def test_get_total_score(self):
        """Test total score calculation with bonuses."""
        player = YahtzeePlayer(id="123", name="Test")
        # Fill upper section to get bonus
        player.scores["ones"] = 3
        player.scores["twos"] = 6
        player.scores["threes"] = 12
        player.scores["fours"] = 16
        player.scores["fives"] = 15
        player.scores["sixes"] = 18  # Total = 70 >= 63, bonus!
        player.upper_bonus_awarded = True

        # Add some lower section scores
        player.scores["yahtzee"] = 50
        player.scores["chance"] = 20

        # Add a yahtzee bonus
        player.yahtzee_bonus_count = 1

        total = player.get_total_score()
        # 70 (upper) + 35 (bonus) + 50 (yahtzee) + 20 (chance) + 100 (yahtzee bonus) = 275
        assert total == 275


class TestYahtzeeGameUnit:
    """Unit tests for Yahtzee game functions."""

    def test_game_creation(self):
        """Test creating a new Yahtzee game."""
        game = YahtzeeGame()
        assert game.get_name() == "Yahtzee"
        assert game.get_type() == "yahtzee"
        assert game.get_category() == "dice"
        assert game.get_min_players() == 1
        assert game.get_max_players() == 4
        assert game.relevant_preferences == [
            "brief_announcements",
            "clear_kept_on_roll",
            "dice_keeping_style",
        ]

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, YahtzeePlayer)

    def test_options_defaults(self):
        """Test default game options."""
        game = YahtzeeGame()
        assert game.options.num_games == 1

    def test_custom_options(self):
        """Test custom game options."""
        options = YahtzeeOptions(num_games=3)
        game = YahtzeeGame(options=options)
        assert game.options.num_games == 3

    def test_joker_rule_forces_matching_upper_box_first(self):
        """A later Yahtzee must score the matching upper box when it is open."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player: YahtzeePlayer = game.add_player("Alice", user)  # type: ignore[assignment]
        game.on_start()

        player.dice.values = [6, 6, 6, 6, 6]
        player.scores["yahtzee"] = 50

        assert game._calculate_score_for_player(player, "sixes") == 30
        assert game._is_score_sixes_enabled(player) is None
        assert game._is_score_full_house_enabled(player) == (
            "yahtzee-joker-upper-required",
            {"face": 6},
        )

    def test_joker_rule_scores_fixed_lower_categories_after_upper_is_filled(self):
        """Joker lower-section fixed scores apply only after the matching upper box is filled."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player: YahtzeePlayer = game.add_player("Alice", user)  # type: ignore[assignment]
        game.on_start()

        player.dice.values = [4, 4, 4, 4, 4]
        player.scores["yahtzee"] = 50
        player.scores["fours"] = 20

        assert game._calculate_score_for_player(player, "full_house") == 25
        assert game._calculate_score_for_player(player, "small_straight") == 30
        assert game._calculate_score_for_player(player, "large_straight") == 40
        assert game._is_score_full_house_enabled(player) is None
        assert game._is_score_ones_enabled(player) == (
            "yahtzee-joker-lower-required",
            {"face": 4},
        )

        player.scores["yahtzee"] = 0
        assert game._calculate_score_for_player(player, "full_house") == 25

    def test_joker_rule_allows_zero_upper_when_lower_section_is_full(self):
        """If matching upper and every lower category are filled, any open upper box scores zero."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player: YahtzeePlayer = game.add_player("Alice", user)  # type: ignore[assignment]
        game.on_start()

        player.dice.values = [5, 5, 5, 5, 5]
        player.scores["fives"] = 25
        for category in LOWER_CATEGORIES:
            player.scores[category] = 1
        player.scores["yahtzee"] = 50
        player.scores["ones"] = None

        assert game._is_score_ones_enabled(player) is None
        assert game._calculate_score_for_player(player, "ones") == 0

    def test_own_scorecard_uses_requesting_player_not_current_turn(self):
        """The C shortcut/status action should open the requester's own scorecard."""
        game = YahtzeeGame()
        alice_user = MockUser("Alice")
        bob_user = MockUser("Bob")
        game.add_player("Alice", alice_user)
        bob: YahtzeePlayer = game.add_player("Bob", bob_user)  # type: ignore[assignment]
        game.on_start()

        bob.scores["twos"] = 4
        game.execute_action(bob, "view_scoresheet")

        status_items = bob_user.get_current_menu_items("status_box")
        assert status_items is not None
        texts = _menu_texts(status_items)
        assert texts[0] == "Bob's Scorecard"
        assert "  Twos: 4" in texts

    def test_all_scorecards_menu_is_spectator_accessible(self):
        """Shift+C opens a player selector and can show any active player's scorecard."""
        game = YahtzeeGame()
        alice_user = MockUser("Alice")
        bob_user = MockUser("Bob")
        watcher_user = MockUser("Watcher")
        alice = game.add_player("Alice", alice_user)
        bob: YahtzeePlayer = game.add_player("Bob", bob_user)  # type: ignore[assignment]
        watcher = game.add_spectator("Watcher", watcher_user)
        game.on_start()

        bob.scores["threes"] = 9
        game.execute_action(watcher, "view_all_scorecards")

        menu = watcher_user.menus["action_input_menu"]
        assert menu["selection_id"] == alice.id
        assert [item.id for item in menu["items"][:2]] == [alice.id, bob.id]
        assert _menu_texts(menu["items"][:2]) == ["Alice", "Bob"]

        game.handle_event(
            watcher,
            {
                "type": "menu",
                "menu_id": "action_input_menu",
                "selection_id": bob.id,
            },
        )

        status_items = watcher_user.get_current_menu_items("status_box")
        assert status_items is not None
        texts = _menu_texts(status_items)
        assert texts[0] == "Bob's Scorecard"
        assert "  Threes: 9" in texts

    def test_all_scorecard_keybind_and_action_include_spectators(self):
        """The spectator-capable Shift+C binding must match the action metadata."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.setup_keybinds()
        action = game.create_standard_action_set(player).get_action("view_all_scorecards")

        assert action is not None
        assert action.include_spectators is True
        assert any(binding.include_spectators for binding in game._keybinds["shift+c"])

    def test_brief_announcements_are_per_listener(self, monkeypatch):
        """Brief announcements shorten only the listeners who enabled the option."""
        game = YahtzeeGame()
        alice_user = MockUser("Alice")
        bob_user = MockUser("Bob")
        bob_user.preferences.brief_announcements = True
        alice: YahtzeePlayer = game.add_player("Alice", alice_user)  # type: ignore[assignment]
        game.add_player("Bob", bob_user)
        game.on_start()
        alice_user.clear_messages()
        bob_user.clear_messages()

        monkeypatch.setattr("server.game_utils.dice.random.randint", lambda _a, _b: 3)
        game.execute_action(alice, "roll")

        assert alice_user.get_last_spoken() == (
            "You rolled: 3, 3, 3, 3, 3. 2 rolls left."
        )
        assert bob_user.get_last_spoken() == "Alice rolled: 3, 3, 3, 3, 3."

    def test_standard_scoreboard_syncs_from_scorecard_totals(self):
        """S/Shift+S should report the authoritative Yahtzee scorecard totals."""
        game = YahtzeeGame()
        alice_user = MockUser("Alice")
        bob_user = MockUser("Bob")
        alice: YahtzeePlayer = game.add_player("Alice", alice_user)  # type: ignore[assignment]
        bob: YahtzeePlayer = game.add_player("Bob", bob_user)  # type: ignore[assignment]
        game.on_start()

        alice.dice.values = [6, 6, 6, 6, 6]
        game.execute_action(alice, "score_sixes")
        bob.dice.values = [5, 5, 5, 1, 1]
        game.execute_action(bob, "score_full_house")

        alice_user.clear_messages()
        game.execute_action(alice, "check_scores")

        spoken = alice_user.get_spoken_messages()
        assert any("Alice: 30 points" in message for message in spoken)
        assert any("Bob: 25 points" in message for message in spoken)
        assert game.team_manager.get_team("Alice").total_score == 30
        assert game.team_manager.get_team("Bob").total_score == 25

    def test_touch_focus_returns_to_roll_after_scoring(self):
        """A touch user who scores should land back on the persistent Roll anchor."""
        game = YahtzeeGame()
        alice_user = MockUser("Alice")
        bob_user = MockUser("Bob")
        alice_user.client_type = "web"
        alice: YahtzeePlayer = game.add_player("Alice", alice_user)  # type: ignore[assignment]
        game.add_player("Bob", bob_user)
        game.on_start()

        alice.dice.values = [1, 1, 1, 2, 3]
        game.execute_action(alice, "score_ones")
        game.flush_menus()

        menu = alice_user.menus["turn_menu"]
        assert menu["selection_id"] == "roll"
        assert any(getattr(item, "id", None) == "roll" for item in menu["items"])

    def test_solo_yahtzee_result_is_marked_non_competitive(self):
        """Solo Yahtzee should not feed competitive leaderboard/stat extractors."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player: YahtzeePlayer = game.add_player("Alice", user)  # type: ignore[assignment]
        game.on_start()
        player.scores["yahtzee"] = 50

        result = game.build_game_result()

        assert result.custom_data["competitive"] is False
        assert result.custom_data["solo_mode"] is True
        assert StatsExtractor.extract_incremental_stats(result) == {}

    def test_solo_yahtzee_result_is_not_persisted(self):
        """Solo practice games should not write global result/stat records."""
        game = YahtzeeGame()
        game.add_player("Alice", MockUser("Alice"))
        game.on_start()
        result = game.build_game_result()

        class FakeTable:
            def __init__(self) -> None:
                self.saved: list = []
                self._db = None

            def save_game_result(self, saved_result, *, rating_updates=None) -> None:
                self.saved.append(saved_result)

        table = FakeTable()
        game._table = table

        game._persist_result(result)

        assert table.saved == []

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = YahtzeeGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert len(data["players"]) == 2
        assert "dice" in data["players"][0]
        assert "scores" in data["players"][0]

        # Deserialize
        loaded_game = YahtzeeGame.from_json(json_str)
        assert len(loaded_game.players) == 2


class TestYahtzeePlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = YahtzeeGame()
        game.options.num_games = 1

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game for many ticks (13 categories * 2 players = 26 turns minimum)
        max_ticks = 5000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_single_player_game_completes(self):
        """Test that a single-player bot game completes."""
        game = YahtzeeGame()

        bot = Bot("Bot1")
        game.add_player("Bot1", bot)

        game.on_start()

        max_ticks = 3000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_value_style_defaults_to_all_kept_when_clear_is_off(self):
        """Value controls release dice from an all-kept post-roll state."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        user.preferences.dice_keeping_style = DiceKeepingStyle.VALUE_BASED
        user.preferences.clear_kept_on_roll = False
        player = game.add_player("Alice", user)
        game.on_start()

        game.execute_action(player, "roll")

        assert player.dice.kept == [0, 1, 2, 3, 4]
        value = player.dice.values[0]
        game.execute_action(player, f"dice_key_{value}")
        assert len(player.dice.kept) == 4
        assert 0 not in player.dice.kept

    def test_value_style_honors_clear_kept_after_every_roll(self, monkeypatch):
        """Clear-kept must not be overwritten by value-mode defaults."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        user.preferences.dice_keeping_style = DiceKeepingStyle.VALUE_BASED
        user.preferences.clear_kept_on_roll = True
        player = game.add_player("Alice", user)
        game.on_start()

        game.execute_action(player, "roll")
        assert player.dice.kept == []

        value = player.dice.values[0]
        game.execute_action(player, f"dice_unkeep_{value}")
        assert player.dice.kept == [0]
        kept_value = player.dice.values[0]

        monkeypatch.setattr(
            "server.game_utils.dice.random.randint",
            lambda _minimum, _maximum: 6 if kept_value != 6 else 5,
        )
        game.execute_action(player, "roll")

        assert player.dice.values[0] == kept_value
        assert player.dice.kept == []

    def test_four_player_game_completes(self):
        """Test that a 4-player bot game completes."""
        game = YahtzeeGame()

        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        max_ticks = 10000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestYahtzeePersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = YahtzeeGame(options=YahtzeeOptions(num_games=2))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        alice: YahtzeePlayer = game.players[0]  # type: ignore
        alice.scores["ones"] = 3
        alice.scores["twos"] = 6
        alice.yahtzee_bonus_count = 1

        # Save
        json_str = game.to_json()

        # Load
        loaded = YahtzeeGame.from_json(json_str)
        loaded_alice: YahtzeePlayer = loaded.players[0]  # type: ignore

        # Verify state
        assert loaded.game_active is True
        assert loaded.options.num_games == 2
        assert loaded_alice.scores["ones"] == 3
        assert loaded_alice.scores["twos"] == 6
        assert loaded_alice.yahtzee_bonus_count == 1


def test_yahtzee_locale_key_and_variable_parity() -> None:
    en_text = (LOCALES_DIR / "en" / "yahtzee.ftl").read_text(encoding="utf-8")
    vi_text = (LOCALES_DIR / "vi" / "yahtzee.ftl").read_text(encoding="utf-8")

    assert _ftl_messages(en_text) == _ftl_messages(vi_text)

