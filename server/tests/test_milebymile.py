"""
Tests for the Mile by Mile game.
"""

import json
import random

from ..games.milebymile.game import (
    MileByMileGame,
    MileByMilePlayer,
    MileByMileOptions,
    RaceState,
)
from ..games.milebymile.cards import Card, CardType, HazardType, SafetyType
from ..users.test_user import MockUser
from ..users.bot import Bot


def speech_texts(user: MockUser) -> list[str]:
    return [message.data["text"] for message in user.messages if message.type == "speak"]


class TestMileByMileGameUnit:
    """Unit tests for Mile by Mile game functions."""

    def test_game_creation(self):
        """Test creating a new Mile by Mile game."""
        game = MileByMileGame()
        assert game.get_name() == "Mile by Mile"
        assert game.get_type() == "milebymile"
        assert game.get_category() == "cards"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 9

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = MileByMileGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, MileByMilePlayer)
        assert player.hand == []

    def test_options_defaults(self):
        """Test default game options."""
        game = MileByMileGame()
        assert game.options.round_distance == 1000
        assert game.options.winning_score == 5000

    def test_custom_options(self):
        """Test custom game options."""
        options = MileByMileOptions(round_distance=700, winning_score=3000)
        game = MileByMileGame(options=options)
        assert game.options.round_distance == 700
        assert game.options.winning_score == 3000


class TestRightOfWayBehavior:
    """Tests for Right of Way safety card behavior."""

    def test_right_of_way_allows_driving_when_stopped(self):
        """Right of Way should allow playing distance when only STOP is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.STOP)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is True

    def test_right_of_way_allows_driving_with_speed_limit(self):
        """Right of Way should allow playing distance when SPEED_LIMIT is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.SPEED_LIMIT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is True

    def test_right_of_way_allows_driving_with_stop_and_speed_limit(self):
        """Right of Way should allow playing distance with both STOP and SPEED_LIMIT."""
        race_state = RaceState()
        race_state.add_problem(HazardType.STOP)
        race_state.add_problem(HazardType.SPEED_LIMIT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is True

    def test_right_of_way_does_not_protect_against_accident(self):
        """Right of Way should NOT allow playing distance when ACCIDENT is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.ACCIDENT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False

    def test_right_of_way_does_not_protect_against_flat_tire(self):
        """Right of Way should NOT allow playing distance when FLAT_TIRE is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.FLAT_TIRE)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False

    def test_right_of_way_does_not_protect_against_out_of_gas(self):
        """Right of Way should NOT allow playing distance when OUT_OF_GAS is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.OUT_OF_GAS)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False

    def test_right_of_way_with_accident_and_stop(self):
        """Right of Way should NOT allow distance with ACCIDENT even if STOP also present."""
        race_state = RaceState()
        race_state.add_problem(HazardType.STOP)
        race_state.add_problem(HazardType.ACCIDENT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False


class TestMileByMileSerialization:
    """Tests for game serialization."""

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = MileByMileGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        game.current_race = 1

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["current_race"] == 1
        assert len(data["players"]) == 2

        # Deserialize
        loaded_game = MileByMileGame.from_json(json_str)
        assert loaded_game.current_race == 1


class TestMileByMilePlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = MileByMileGame()
        game.options.round_distance = 300  # Lower target for faster test
        game.options.winning_score = 1000

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game for many ticks
        max_ticks = 30000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_four_player_team_game_completes(self):
        """Test that a 4-player team game completes."""
        random.seed(12345)
        game = MileByMileGame()
        game.options.round_distance = 500
        game.options.winning_score = 1000
        game.options.team_mode = "2v2"  # Internal format

        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        # Verify teams are set up
        assert game.get_num_teams() == 2

        max_ticks = 100000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestMileByMilePersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = MileByMileGame(options=MileByMileOptions(round_distance=500))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Set various state
        game.current_race = 1

        # Save
        json_str = game.to_json()

        # Load
        loaded = MileByMileGame.from_json(json_str)

        # Verify state
        assert loaded.game_active is True
        assert loaded.current_race == 1
        assert loaded.options.round_distance == 500


class TestMileByMileTargetSelectionGuard:
    def test_out_of_turn_hazard_card_does_not_open_target_selection_menu(self):
        game = MileByMileGame()
        users = [MockUser("Alice", uuid="p1"), MockUser("Bob", uuid="p2"), MockUser("Cara", uuid="p3")]
        players = [game.add_player(user.username, user) for user in users]
        game.on_start()

        alice, bob, _cara = players
        alice_user = game.get_user(alice)
        assert alice_user is not None

        alice.hand = [Card(id=1, card_type=CardType.HAZARD, value=HazardType.STOP)]
        bob.hand = []
        game.current_player = bob
        game._update_turn_actions(alice)
        alice_user.clear_messages()

        game.execute_action(alice, "card_slot_1")

        assert alice.id not in game._pending_actions
        assert "action_input_menu" not in alice_user.menus
        assert alice_user.get_last_spoken() == "It's not your turn."


class TestMileByMileDirtyTricks:
    def test_playing_matching_safety_card_normally_counts_as_dirty_trick(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        bob = game.add_player("Bob", bob_user)
        game.on_start()

        safety = Card(id=1001, card_type=CardType.SAFETY, value=SafetyType.PUNCTURE_PROOF)
        bob.hand = [safety]
        bob_state = game.get_player_race_state(bob)
        assert bob_state is not None
        bob_state.problems = [HazardType.FLAT_TIRE, HazardType.STOP]
        game.dirty_trick_window_team = bob.team_index
        game.dirty_trick_window_hazard = HazardType.FLAT_TIRE
        game.dirty_trick_window_ticks = 140
        game.current_player = alice
        game._update_turn_actions(bob)
        alice_user.clear_messages()
        bob_user.clear_messages()

        game.execute_action(bob, "card_slot_1")

        assert SafetyType.PUNCTURE_PROOF in bob_state.safeties
        assert bob_state.dirty_trick_count == 1
        assert HazardType.FLAT_TIRE not in bob_state.problems
        assert HazardType.STOP not in bob_state.problems
        assert game.dirty_trick_window_team is None
        assert all(card.id != safety.id for card in bob.hand)
        assert safety in game.protections_pile
        assert any("You play Puncture Proof as a Dirty Trick" in text for text in speech_texts(bob_user))
        assert any("Bob plays Puncture Proof as a Dirty Trick" in text for text in speech_texts(alice_user))


class TestMileByMileUnplayableCardMenu:
    def test_unplayable_card_opens_reason_discard_menu_and_reason_is_noop(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)
        game.on_start()

        blocked_card = Card(id=2001, card_type=CardType.DISTANCE, value="100")
        alice.hand = [blocked_card]
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = [HazardType.STOP]
        game.current_player = alice
        game._update_turn_actions(alice)
        alice_user.clear_messages()

        game.execute_action(alice, "card_slot_1")

        assert alice.id in game._pending_actions
        items = alice_user.get_current_menu_items("action_input_menu")
        assert items is not None
        assert alice_user.menus["action_input_menu"]["position"] == 2
        assert [getattr(item, "id", "") for item in items] == [
            "",
            "discard_unplayable_card",
            "_cancel",
        ]
        reason_text = getattr(items[0], "text", "")
        assert "You cannot play 100 miles because you need a Green Light" in reason_text
        assert "Do you want to discard it?" in reason_text
        assert alice_user.get_last_spoken() == reason_text

        game.handle_event(
            alice,
            {
                "type": "menu",
                "menu_id": "action_input_menu",
                "selection_id": "",
            },
        )

        assert alice.id in game._pending_actions
        assert alice.hand == [blocked_card]
        assert blocked_card not in game.discard_pile
        assert game.current_player == alice

        game.handle_event(
            alice,
            {
                "type": "menu",
                "menu_id": "action_input_menu",
                "selection_id": "discard_unplayable_card",
            },
        )

        assert blocked_card not in alice.hand
        assert blocked_card in game.discard_pile
        assert game.current_player != alice

    def test_unplayable_reasons_are_specific_to_current_problem(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)
        game.on_start()
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None

        card = Card(id=2101, card_type=CardType.DISTANCE, value="100")
        alice_state.problems = [HazardType.FLAT_TIRE, HazardType.STOP]
        assert "flat tire" in game._get_unplayable_reason(alice, card, "en")

        alice_state.problems = [HazardType.SPEED_LIMIT]
        assert "Speed Limit" in game._get_unplayable_reason(alice, card, "en")

        alice_state.problems = []
        alice_state.used_200_mile_count = 2
        card_200 = Card(id=2102, card_type=CardType.DISTANCE, value="200")
        assert "two 200-mile cards" in game._get_unplayable_reason(alice, card_200, "en")


class TestMileByMileTouchOrdering:
    def test_touch_standard_actions_put_info_before_status(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        alice_user.client_type = "web"
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)

        standard_set = game.get_action_set(alice, "standard")
        assert standard_set is not None
        assert standard_set._order.index("info") < standard_set._order.index(
            "check_status"
        )

    def test_desktop_standard_actions_keep_status_before_info(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)

        standard_set = game.get_action_set(alice, "standard")
        assert standard_set is not None
        assert standard_set._order.index("check_status") < standard_set._order.index(
            "info"
        )

    def test_dirty_trick_hidden_for_touch_client_before_game_starts(self):
        """Dirty Trick button must not appear for touch clients in the lobby."""
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        alice_user.client_type = "web"
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)

        # Status is "waiting" — game not started yet
        assert game.status != "playing"
        lobby_action_ids = {
            entry.action.id for entry in game.get_all_visible_actions(alice)
        }
        assert "dirty_trick" not in lobby_action_ids

    def test_dirty_trick_visible_for_touch_client_during_active_play(self):
        """Dirty Trick button must be visible for touch clients once gameplay starts."""
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        alice_user.client_type = "web"
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)
        game.on_start()

        assert game.status == "playing"
        playing_action_ids = {
            entry.action.id for entry in game.get_all_visible_actions(alice)
        }
        assert "dirty_trick" in playing_action_ids


class TestMileByMileBroadcastsAndOptions:
    def test_hazard_broadcasts_use_actor_and_target_context(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        bob = game.add_player("Bob", bob_user)
        game.on_start()

        hazard = Card(id=3001, card_type=CardType.HAZARD, value=HazardType.STOP)
        alice.hand = [hazard]
        bob_state = game.get_player_race_state(bob)
        assert bob_state is not None
        bob_state.problems = []
        game.current_player = alice
        game._update_turn_actions(alice)
        alice_user.clear_messages()
        bob_user.clear_messages()

        game.execute_action(alice, "card_slot_1")

        assert any("You play Stop on Bob" in text for text in speech_texts(alice_user))
        assert any("Alice plays Stop on you" in text for text in speech_texts(bob_user))

    def test_exact_finish_blocks_target_not_divisible_by_25(self):
        game = MileByMileGame(options=MileByMileOptions(round_distance=333))
        game.add_player("Alice", MockUser("Alice", uuid="p1"))
        game.add_player("Bob", MockUser("Bob", uuid="p2"))

        assert "milebymile-error-perfect-distance-step" in game.prestart_validate()

        game.options.only_allow_perfect_crossing = False
        assert "milebymile-error-perfect-distance-step" not in game.prestart_validate()

    def test_game_result_winner_uses_total_score_not_last_race_winner(self):
        game = MileByMileGame()
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        bob = game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()
        game._team_manager.teams[alice.team_index].total_score = 900
        game._team_manager.teams[bob.team_index].total_score = 500
        game.race_winner_team_index = bob.team_index

        result = game.build_game_result()

        assert result.custom_data["winner_name"] == "Alice"
        assert result.custom_data["winner_ids"] == [alice.id]
        assert result.custom_data["winner_score"] == 900


def test_status_score_format_includes_localized_unit() -> None:
    game = MileByMileGame()
    alice_user = MockUser("Alice", locale="vi", uuid="p1")
    bob_user = MockUser("Bob", locale="vi", uuid="p2")
    alice = game.add_player("Alice", alice_user)
    game.add_player("Bob", bob_user)
    game.on_start()
    game._team_manager.teams[0].total_score = 0
    alice_user.clear_messages()

    game._action_check_status(alice, "check_status")

    spoken = alice_user.get_spoken_messages()
    assert spoken
    assert "unit" not in spoken[0]
    assert "điểm" in spoken[0]

