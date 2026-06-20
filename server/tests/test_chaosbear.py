"""
Tests for the Chaos Bear game.
"""

import json
from pathlib import Path
import re
from unittest.mock import patch

from ..games.chaosbear.game import ChaosBearGame, ChaosBearPlayer
from ..messages.localization import Localization
from ..users.test_user import MockUser
from ..users.bot import Bot


LOCALES_DIR = Path(__file__).parent.parent / "locales"
DOCS_DIR = Path(__file__).parent.parent / "documentation" / "content"


def advance_ticks(game: ChaosBearGame, ticks: int = 60) -> None:
    """Advance the Chaos Bear game by a bounded number of ticks."""
    for _ in range(ticks):
        game.on_tick()


def spoken(user: MockUser) -> list[str]:
    return user.get_spoken_messages()


def ftl_messages(text: str) -> dict[str, set[str]]:
    """Return Fluent message keys and the variables referenced by each key."""
    messages: dict[str, set[str]] = {}
    current_key: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        if line and not line.startswith((" ", "\t")) and "=" in line:
            if current_key is not None:
                messages[current_key] = set(
                    re.findall(
                        r"\{\s*\$([a-zA-Z_][\w-]*)",
                        "\n".join(current_lines),
                    )
                )
            current_key = line.split("=", 1)[0].strip()
            current_lines = [line]
        elif current_key is not None:
            current_lines.append(line)
    if current_key is not None:
        messages[current_key] = set(
            re.findall(r"\{\s*\$([a-zA-Z_][\w-]*)", "\n".join(current_lines))
        )
    return messages


class TestChaosBearGameUnit:
    """Unit tests for Chaos Bear game functions."""

    def test_game_creation(self):
        """Test creating a new Chaos Bear game."""
        game = ChaosBearGame()
        assert game.get_name() == "Chaos Bear"
        assert game.get_type() == "chaosbear"
        assert game.get_category() == "arcade"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 4
        assert game.relevant_preferences == ["brief_announcements"]

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = ChaosBearGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, ChaosBearPlayer)
        assert player.alive is True
        assert player.position == 0

    def test_initial_game_state(self):
        """Test initial game state."""
        game = ChaosBearGame()
        assert game.bear_position == 0
        assert game.bear_energy == 1
        assert game.round_number == 0

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        game.bear_position = 5
        game.bear_energy = 3
        game.round_number = 2
        game.players[0].position = 10

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["bear_position"] == 5
        assert data["bear_energy"] == 3
        assert data["round_number"] == 2
        assert data["players"][0]["position"] == 10

        # Deserialize
        loaded_game = ChaosBearGame.from_json(json_str)
        assert loaded_game.bear_position == 5
        assert loaded_game.bear_energy == 3
        assert loaded_game.round_number == 2
        assert loaded_game.players[0].position == 10


class TestChaosBearPlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = ChaosBearGame()

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game for many ticks
        max_ticks = 20000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_four_player_game_completes(self):
        """Test that a 4-player bot game completes."""
        game = ChaosBearGame()

        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        max_ticks = 30000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestChaosBearPersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Set various state
        game.bear_position = 5
        game.bear_energy = 3
        game.round_number = 2
        game.players[0].position = 10
        game.players[0].alive = True

        # Save
        json_str = game.to_json()

        # Load
        loaded = ChaosBearGame.from_json(json_str)

        # Verify state
        assert loaded.game_active is True
        assert loaded.bear_position == 5
        assert loaded.bear_energy == 3
        assert loaded.round_number == 2
        assert loaded.players[0].position == 10
        assert loaded.players[0].alive is True

    def test_roll_sequence_resumes_after_restore(self):
        """A pending movement sequence should resume after save/load."""
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)

        game.on_start()
        game.reset_turn_order()

        with patch("server.games.chaosbear.game.random.randint") as mock_rand:
            mock_rand.side_effect = [4, 1, 1, 1, 1]
            game._action_roll_dice(player1, "roll_dice")

        assert game.has_active_sequence(sequence_id="turn_flow") is True

        payload = game.to_json()
        restored = ChaosBearGame.from_json(payload)
        restored.attach_user(player1.id, user1)
        restored.attach_user(player2.id, user2)

        for _ in range(40):
            restored.on_tick()

        restored_player1 = restored.get_player_by_id(player1.id)
        restored_player2 = restored.get_player_by_id(player2.id)
        assert restored_player1 is not None
        assert restored_player2 is not None
        assert restored_player1.position == 34
        assert restored.current_player == restored_player2


class TestChaosBearBalance:
    """Regression tests for Chaos Bear balance adjustments."""

    def test_round_opener_rotates_each_round(self):
        """The same seat should not always open every round."""
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        user3 = MockUser("Cara")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        player3 = game.add_player("Cara", user3)

        game.on_start()
        assert game.current_player == player1

        game._next_round_step()
        assert game.current_player == player2

        game._next_round_step()
        assert game.current_player == player3

    def test_round_opener_skips_eliminated_seat(self):
        """Round rotation should skip seats that were caught by the bear."""
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        user3 = MockUser("Cara")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        player3 = game.add_player("Cara", user3)

        game.on_start()
        assert game.current_player == player1

        player2.alive = False
        game._next_round_step()
        assert game.current_player == player3

    def test_tiredness_card_keeps_draw_surge(self):
        """Energy cards should still advance the player after the draw rebalance."""
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()
        player1.position = 30
        game.bear_energy = 3
        user1.clear_messages()
        user2.clear_messages()

        with patch("server.games.chaosbear.game.random.randint") as mock_rand:
            mock_rand.side_effect = [1, 2, 1, 1]
            game._action_draw_card(player1, "draw_card")

        advance_ticks(game)

        assert player1.position == 33
        assert game.bear_energy == 2
        assert (
            Localization.get("en", "chaosbear-draw-card-you")
            in user1.get_spoken_messages()
        )
        assert Localization.get(
            "en", "chaosbear-draw-card-other", player="Alice"
        ) in user2.get_spoken_messages()
        assert Localization.get(
            "en",
            "chaosbear-card-tiredness-you",
            position=33,
            gap=33,
            energy=2,
        ) in user1.get_spoken_messages()
        assert Localization.get(
            "en",
            "chaosbear-card-tiredness-other",
            player="Alice",
            position=33,
            gap=33,
            energy=2,
        ) in user2.get_spoken_messages()

    def test_backward_push_cancels_draw_surge(self):
        """Backward push should cancel the surge instead of sending the player behind start."""
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()
        player1.position = 30

        with patch("server.games.chaosbear.game.random.randint") as mock_rand:
            mock_rand.side_effect = [1, 4]
            game._action_draw_card(player1, "draw_card")

        advance_ticks(game)

        assert player1.position == 30


class TestChaosBearUx:
    """Regression tests for Chaos Bear accessibility and messaging."""

    def test_brief_intro_is_selected_per_listener(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        user1.preferences.brief_announcements = True
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        assert Localization.get("en", "chaosbear-intro-brief") in spoken(user1)
        assert Localization.get("en", "chaosbear-intro-1") not in spoken(user1)
        assert Localization.get("en", "chaosbear-intro-1") in spoken(user2)
        assert Localization.get("en", "chaosbear-intro-2") in spoken(user2)
        assert Localization.get("en", "chaosbear-intro-3") in spoken(user2)

    def test_roll_and_move_use_personal_and_observer_messages(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()
        user1.clear_messages()
        user2.clear_messages()

        def deterministic_randint(low: int, high: int) -> int:
            if (low, high) == (1, 6):
                return 4
            return low

        with patch(
            "server.games.chaosbear.game.random.randint",
            side_effect=deterministic_randint,
        ):
            game._action_roll_dice(player1, "roll_dice")
            advance_ticks(game, 40)

        assert Localization.get(
            "en", "chaosbear-roll-you", roll=4
        ) in user1.get_spoken_messages()
        assert Localization.get(
            "en", "chaosbear-roll-other", player="Alice", roll=4
        ) in user2.get_spoken_messages()
        assert Localization.get(
            "en", "chaosbear-position-you", position=34, gap=34
        ) in user1.get_spoken_messages()
        assert Localization.get(
            "en",
            "chaosbear-position-other",
            player="Alice",
            position=34,
            gap=34,
        ) in user2.get_spoken_messages()

    def test_brief_roll_and_move_are_selected_per_listener(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        user1.preferences.brief_announcements = True
        player1 = game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()
        user1.clear_messages()
        user2.clear_messages()

        def deterministic_randint(low: int, high: int) -> int:
            if (low, high) == (1, 6):
                return 4
            return low

        with patch(
            "server.games.chaosbear.game.random.randint",
            side_effect=deterministic_randint,
        ):
            game._action_roll_dice(player1, "roll_dice")
            advance_ticks(game, 40)

        assert Localization.get(
            "en", "chaosbear-roll-you-brief", roll=4
        ) in spoken(user1)
        assert Localization.get(
            "en", "chaosbear-position-you-brief", position=34, gap=34
        ) in spoken(user1)
        assert Localization.get(
            "en", "chaosbear-position-you", position=34, gap=34
        ) not in spoken(user1)
        assert Localization.get(
            "en",
            "chaosbear-position-other",
            player="Alice",
            position=34,
            gap=34,
        ) in spoken(user2)

    def test_brief_card_effect_survives_sequence_restore(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        user1.preferences.brief_announcements = True
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)

        game.on_start()
        player1.position = 30
        game.bear_energy = 3
        user1.clear_messages()
        user2.clear_messages()

        with patch("server.games.chaosbear.game.random.randint") as mock_rand:
            mock_rand.side_effect = [1, 2, 1, 1]
            game._action_draw_card(player1, "draw_card")

        payload = game.to_json()
        restored = ChaosBearGame.from_json(payload)
        restored.attach_user(player1.id, user1)
        restored.attach_user(player2.id, user2)
        user1.clear_messages()
        user2.clear_messages()

        advance_ticks(restored)

        assert Localization.get(
            "en",
            "chaosbear-card-tiredness-you-brief",
            position=33,
            energy=2,
        ) in spoken(user1)
        assert Localization.get(
            "en",
            "chaosbear-card-tiredness-you",
            position=33,
            gap=33,
            energy=2,
        ) not in spoken(user1)
        assert Localization.get(
            "en",
            "chaosbear-card-tiredness-other",
            player="Alice",
            position=33,
            gap=33,
            energy=2,
        ) in spoken(user2)

    def test_global_bear_events_use_brief_per_listener(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        user1.preferences.brief_announcements = True
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()
        user1.clear_messages()
        user2.clear_messages()

        game.on_sequence_callback(
            "turn_flow",
            "bear_roll_result",
            {"roll": 3, "energy": 4, "total": 7},
        )
        game.on_sequence_callback("turn_flow", "bear_energy_up", {"energy": 5})
        game.on_sequence_callback("turn_flow", "bear_move", {"pos": 42})
        game.on_sequence_callback("turn_flow", "bear_feast", {"energy": 2})

        assert Localization.get(
            "en", "chaosbear-bear-roll-brief", roll=3, energy=4, total=7
        ) in spoken(user1)
        assert Localization.get(
            "en", "chaosbear-bear-energy-up-brief", energy=5
        ) in spoken(user1)
        assert Localization.get(
            "en", "chaosbear-bear-position-brief", position=42
        ) in spoken(user1)
        assert Localization.get(
            "en", "chaosbear-bear-feast-brief", energy=2
        ) in spoken(user1)
        assert Localization.get(
            "en", "chaosbear-bear-roll", roll=3, energy=4, total=7
        ) in spoken(user2)
        assert Localization.get(
            "en", "chaosbear-bear-position", position=42
        ) in spoken(user2)

    def test_contextual_disabled_reasons(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        game.on_start()
        user1.clear_messages()
        user2.clear_messages()

        game.execute_action(player2, "roll_dice")
        assert user2.get_last_spoken() == Localization.get(
            "en", "chaosbear-error-roll-not-your-turn"
        )

        player1.position = 31
        game.execute_action(player1, "draw_card")
        assert user1.get_last_spoken() == Localization.get(
            "en", "chaosbear-error-draw-not-on-multiple"
        )

        player1.alive = False
        game._action_roll_dice(player1, "roll_dice")
        assert user1.get_last_spoken() == Localization.get(
            "en",
            "chaosbear-error-roll-caught",
            position=31,
            bear_position=0,
        )

    def test_turn_actions_remain_visible_and_disabled_out_of_turn(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        user1.client_type = "mobile"
        user2.client_type = "web"
        game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        game.on_start()

        visible = {
            resolved.action.id: resolved
            for resolved in game.get_all_visible_actions(player2)
        }

        assert "roll_dice" in visible
        assert visible["roll_dice"].enabled is False
        assert (
            visible["roll_dice"].disabled_reason
            == "chaosbear-error-roll-not-your-turn"
        )
        assert "draw_card" in visible

    def test_spectator_can_open_status_box(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        watcher = MockUser("Watcher")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        spectator = game.add_spectator("Watcher", watcher)

        game.on_start()
        watcher.clear_messages()

        game._action_check_status(spectator, "check_status")

        assert "status_box" in watcher.menus
        lines = [item.text for item in watcher.menus["status_box"]["items"]]
        assert lines[0] == Localization.get("en", "chaosbear-status-header")
        assert any("Alice" in line for line in lines)
        assert any("The bear" in line for line in lines)

    def test_bear_turn_ignores_base_spectator_records(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        watcher = MockUser("Watcher")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.add_spectator("Watcher", watcher)

        game.on_start()

        game._bear_turn()

        assert game.has_active_sequence(sequence_id="turn_flow") is True

    def test_distance_tiebreak_result_records_winner_id(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        game.on_start()
        player1.alive = False
        player1.position = 45
        player2.alive = False
        player2.position = 43
        user1.clear_messages()
        user2.clear_messages()

        assert game._check_for_winner() is True

        result = game.build_game_result()
        assert result.custom_data["winner_name"] == "Alice"
        assert result.custom_data["winner_ids"] == [player1.id]
        assert result.custom_data["is_tie"] is False
        assert Localization.get(
            "en", "chaosbear-distance-winner-you", position=45
        ) in user1.get_spoken_messages()
        assert Localization.get(
            "en",
            "chaosbear-distance-winner-other",
            player="Alice",
            position=45,
        ) in user2.get_spoken_messages()

    def test_distance_tie_records_tied_players_without_winner(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        game.on_start()
        player1.alive = False
        player1.position = 45
        player2.alive = False
        player2.position = 45
        user1.clear_messages()
        user2.clear_messages()

        assert game._check_for_winner() is True

        result = game.build_game_result()
        assert result.custom_data["winner_name"] is None
        assert result.custom_data["winner_ids"] == []
        assert result.custom_data["is_tie"] is True
        assert set(result.custom_data["tied_ids"]) == {player1.id, player2.id}
        assert any(
            message.startswith("You tie for the distance lead at square 45")
            for message in user1.get_spoken_messages()
        )
        assert any(
            message.startswith("You tie for the distance lead at square 45")
            for message in user2.get_spoken_messages()
        )

    def test_brief_distance_tie_uses_listener_specific_wording(self):
        game = ChaosBearGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        watcher = MockUser("Watcher")
        user1.preferences.brief_announcements = True
        player1 = game.add_player("Alice", user1)
        player2 = game.add_player("Bob", user2)
        game.add_spectator("Watcher", watcher)
        game.on_start()
        player1.alive = False
        player1.position = 45
        player2.alive = False
        player2.position = 45
        user1.clear_messages()
        user2.clear_messages()
        watcher.clear_messages()

        assert game._check_for_winner() is True

        assert Localization.get(
            "en", "chaosbear-tie-you-brief", position=45, players="Bob"
        ) in spoken(user1)
        assert any(
            message.startswith("You tie for the distance lead at square 45")
            for message in spoken(user2)
        )
        assert Localization.get(
            "en", "chaosbear-tie", position=45, players="Alice and Bob"
        ) in spoken(watcher)

    def test_localization_parity_and_manual_terms(self):
        en_text = (LOCALES_DIR / "en" / "chaosbear.ftl").read_text(encoding="utf-8")
        vi_text = (LOCALES_DIR / "vi" / "chaosbear.ftl").read_text(encoding="utf-8")
        en_messages = ftl_messages(en_text)
        vi_messages = ftl_messages(vi_text)

        assert en_messages.keys() == vi_messages.keys()
        assert en_messages == vi_messages

        en_doc = (
            DOCS_DIR / "en" / "games" / "chaosbear.md"
        ).read_text(encoding="utf-8")
        vi_doc = (
            DOCS_DIR / "vi" / "games" / "chaosbear.md"
        ).read_text(encoding="utf-8")

        assert "Brief Announcements" in en_doc
        assert "Thông báo ngắn gọn" in vi_doc
        assert "Tiredness" in en_doc
        assert "Kiệt sức" in vi_doc
        assert "Random Gift" in en_doc
        assert "Quà bất ngờ" in vi_doc

