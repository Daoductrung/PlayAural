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
    UNPLAYABLE_DISCARD_OPTION,
)
from ..games.milebymile.cards import Card, CardType, HazardType, SafetyType
from ..users.test_user import MockUser
from ..users.bot import Bot


def speech_texts(user: MockUser) -> list[str]:
    return [message.data["text"] for message in user.messages if message.type == "speak"]


def turn_menu_messages(user: MockUser) -> list:
    return [
        message
        for message in user.messages
        if message.type == "show_menu"
        and message.data.get("menu_id") == "turn_menu"
    ]


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
    def test_out_of_turn_dirty_trick_replaces_safety_then_draws_for_extra_turn(self):
        game = MileByMileGame()
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        bob = game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        hazard = Card(id=8990, card_type=CardType.HAZARD, value=HazardType.FLAT_TIRE)
        safety = Card(
            id=8991,
            card_type=CardType.SAFETY,
            value=SafetyType.PUNCTURE_PROOF,
        )
        fillers = [
            Card(id=8992 + index, card_type=CardType.DISTANCE, value="25")
            for index in range(5)
        ]
        replacement = Card(id=8997, card_type=CardType.DISTANCE, value="50")
        turn_draw = Card(id=8998, card_type=CardType.DISTANCE, value="75")
        alice.hand = [hazard]
        bob.hand = [safety, *fillers]
        game.deck.cards = [replacement, turn_draw]
        bob_state = game.get_player_race_state(bob)
        assert bob_state is not None
        bob_state.problems = []
        game.current_player = alice
        game._update_all_turn_actions()

        game.execute_action(alice, "card_slot_1")
        game.execute_action(bob, "card_slot_1")

        assert game.current_player == bob
        assert len(bob.hand) == 7
        assert replacement in bob.hand
        assert turn_draw in bob.hand
        assert game.deck.is_empty()
        assert hazard in game.discard_pile
        assert hazard not in bob_state.battle_pile

    def test_team_dirty_trick_refreshes_shared_state_and_grants_extra_turn(self):
        game = MileByMileGame()
        game.options.team_mode = "2v2"
        users = [
            MockUser(f"Player{i + 1}", uuid=f"p{i + 1}") for i in range(4)
        ]
        players = [game.add_player(user.username, user) for user in users]
        game.on_start()

        attacker, current_target, _attacker_partner, safety_player = players
        assert attacker.team_index == players[2].team_index
        assert current_target.team_index == safety_player.team_index

        hazard = Card(id=9000, card_type=CardType.HAZARD, value=HazardType.FLAT_TIRE)
        teammate_distance = Card(id=9001, card_type=CardType.DISTANCE, value="25")
        safety = Card(
            id=9002,
            card_type=CardType.SAFETY,
            value=SafetyType.PUNCTURE_PROOF,
        )
        responder_distance = Card(id=9003, card_type=CardType.DISTANCE, value="50")
        attacker.hand = [hazard]
        current_target.hand = [teammate_distance]
        safety_player.hand = [safety, responder_distance]
        game.deck.cards = []
        target_state = game.get_player_race_state(current_target)
        assert target_state is not None
        target_state.problems = []
        game.current_player = attacker
        game._update_all_turn_actions()

        game.execute_action(attacker, "card_slot_1")

        assert game.current_player == attacker
        assert game.dirty_trick_window_team == current_target.team_index
        assert target_state.can_play_distance() is False

        game.execute_action(safety_player, "card_slot_1")

        assert game.current_player == safety_player
        assert game.dirty_trick_window_team is None
        assert target_state.can_play_distance() is True
        teammate_action = game.find_action(current_target, "card_slot_1")
        responder_action = game.find_action(safety_player, "card_slot_1")
        assert teammate_action is not None and teammate_action.input_request is None
        assert responder_action is not None and responder_action.input_request is None

        game.execute_action(safety_player, "card_slot_1")

        assert target_state.miles == 50
        assert responder_distance not in safety_player.hand

    def test_dirty_trick_window_blocks_play_until_response_time_expires(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        bob = game.add_player("Bob", bob_user)
        game.on_start()

        hazard = Card(id=9010, card_type=CardType.HAZARD, value=HazardType.STOP)
        waiting_card = Card(id=9011, card_type=CardType.SAFETY, value=SafetyType.EXTRA_TANK)
        alice.hand = [hazard, waiting_card]
        bob.hand = [Card(id=9012, card_type=CardType.DISTANCE, value="25")]
        game.deck.cards = []
        bob_state = game.get_player_race_state(bob)
        assert bob_state is not None
        bob_state.problems = []
        game.current_player = alice
        game._update_all_turn_actions()

        game.execute_action(alice, "card_slot_1")

        assert game.current_player == alice
        assert game.dirty_trick_window_ticks > 0
        alice_user.clear_messages()
        game.execute_action(alice, "card_slot_1")
        assert alice_user.get_last_spoken() == "Wait for the Dirty Trick response."
        assert waiting_card in alice.hand

        game.dirty_trick_window_ticks = 1
        game.on_tick()

        assert game.dirty_trick_window_team is None
        assert game.current_player == bob

    def test_out_of_turn_bot_can_play_team_dirty_trick(self):
        game = MileByMileGame()
        game.options.team_mode = "2v2"
        attacker = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.add_player("Cara", MockUser("Cara", uuid="p3"))
        safety_bot = game.add_player("Bot", Bot("Bot"))
        game.on_start()

        hazard = Card(id=9020, card_type=CardType.HAZARD, value=HazardType.OUT_OF_GAS)
        safety = Card(id=9021, card_type=CardType.SAFETY, value=SafetyType.EXTRA_TANK)
        attacker.hand = [hazard]
        safety_bot.hand = [
            safety,
            Card(id=9022, card_type=CardType.DISTANCE, value="25"),
        ]
        game.deck.cards = []
        target_state = game.get_player_race_state(safety_bot)
        assert target_state is not None
        target_state.problems = []
        game.current_player = attacker
        game._update_all_turn_actions()

        game.execute_action(attacker, "card_slot_1")
        safety_bot.bot_think_ticks = 0
        game.on_tick()
        game.on_tick()

        assert game.dirty_trick_window_team is None
        assert game.current_player == safety_bot
        assert SafetyType.EXTRA_TANK in target_state.safeties

    def test_dirty_trick_window_survives_save_and_resumes_turn_once(self):
        game = MileByMileGame()
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        bob = game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        hazard = Card(id=9030, card_type=CardType.HAZARD, value=HazardType.STOP)
        alice.hand = [hazard]
        bob.hand = [Card(id=9031, card_type=CardType.DISTANCE, value="25")]
        game.deck.cards = []
        bob_state = game.get_player_race_state(bob)
        assert bob_state is not None
        bob_state.problems = []
        game.current_player = alice
        game._update_all_turn_actions()
        game.execute_action(alice, "card_slot_1")
        game.dirty_trick_window_ticks = 1

        restored = MileByMileGame.from_json(game.to_json())
        restored.rebuild_runtime_state()
        restored.on_tick()

        assert restored.dirty_trick_window_team is None
        assert restored.current_player is not None
        assert restored.current_player.name == "Bob"
        turn_index = restored.turn_index
        restored.on_tick()
        assert restored.turn_index == turn_index

    def test_normal_safety_cancels_matching_hazard_and_restores_movement(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)
        game.on_start()

        safety = Card(id=1000, card_type=CardType.SAFETY, value=SafetyType.EXTRA_TANK)
        alice.hand = [
            safety,
            Card(id=1003, card_type=CardType.DISTANCE, value="25"),
        ]
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = [HazardType.OUT_OF_GAS, HazardType.STOP]
        game.deck.cards = []
        game.current_player = alice
        game._update_turn_actions(alice)

        game.execute_action(alice, "card_slot_1")

        assert SafetyType.EXTRA_TANK in alice_state.safeties
        assert HazardType.OUT_OF_GAS not in alice_state.problems
        assert HazardType.STOP not in alice_state.problems
        assert alice_state.can_play_distance() is True
        assert game.current_player == alice

    def test_normal_safety_does_not_start_a_stopped_car_without_matching_hazard(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)
        game.on_start()

        safety = Card(id=1002, card_type=CardType.SAFETY, value=SafetyType.EXTRA_TANK)
        alice.hand = [safety]
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = [HazardType.STOP]
        game.deck.cards = []
        game.current_player = alice
        game._update_turn_actions(alice)

        game.execute_action(alice, "card_slot_1")

        assert SafetyType.EXTRA_TANK in alice_state.safeties
        assert HazardType.STOP in alice_state.problems
        assert alice_state.can_play_distance() is False

    def test_team_safety_rebuilds_teammate_distance_action(self):
        game = MileByMileGame()
        game.options.team_mode = "2v2"
        players = [
            game.add_player(
                f"Player{index + 1}",
                MockUser(f"Player{index + 1}", uuid=f"p{index + 1}"),
            )
            for index in range(4)
        ]
        game.on_start()
        safety_player, _opponent, teammate, _other_opponent = players

        safety = Card(
            id=1010,
            card_type=CardType.SAFETY,
            value=SafetyType.EXTRA_TANK,
        )
        follow_up = Card(id=1011, card_type=CardType.DISTANCE, value="25")
        teammate_distance = Card(id=1012, card_type=CardType.DISTANCE, value="50")
        safety_player.hand = [safety, follow_up]
        teammate.hand = [teammate_distance]
        game.deck.cards = []
        shared_state = game.get_player_race_state(safety_player)
        assert shared_state is not None
        shared_state.problems = [HazardType.OUT_OF_GAS, HazardType.STOP]
        game.current_player = safety_player
        game._update_all_turn_actions()
        blocked_action = game.find_action(teammate, "card_slot_1")
        assert blocked_action is not None and blocked_action.input_request is not None

        game.execute_action(safety_player, "card_slot_1")

        refreshed_action = game.find_action(teammate, "card_slot_1")
        assert game.current_player == safety_player
        assert shared_state.can_play_distance() is True
        assert refreshed_action is not None and refreshed_action.input_request is None

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


class TestMileByMileExhaustedDraws:
    def test_safety_with_no_remaining_card_does_not_strand_extra_turn(self):
        game = MileByMileGame()
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        bob = game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        safety = Card(
            id=1090,
            card_type=CardType.SAFETY,
            value=SafetyType.EXTRA_TANK,
        )
        alice.hand = [safety]
        bob.hand = [Card(id=1091, card_type=CardType.DISTANCE, value="25")]
        game.deck.cards = []
        game.discard_pile = []
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = [HazardType.OUT_OF_GAS, HazardType.STOP]
        game.current_player = alice
        game._update_all_turn_actions()

        game.execute_action(alice, "card_slot_1")

        assert game.current_player == bob

    def test_empty_hand_is_skipped_when_no_draw_source_remains(self):
        game = MileByMileGame()
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        bob = game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        alice.hand = []
        bob.hand = [Card(id=1100, card_type=CardType.DISTANCE, value="25")]
        game.deck.cards = []
        game.discard_pile = []
        game.current_player = alice

        game._start_turn()

        assert game.current_player == bob
        assert game._round_timer.is_active is False

    def test_race_ends_when_all_hands_and_draw_sources_are_empty(self):
        game = MileByMileGame()
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        bob = game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        alice.hand = []
        bob.hand = []
        game.deck.cards = []
        game.discard_pile = []
        game.current_player = alice

        game._start_turn()

        assert game._round_timer.is_active is True


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
        assert alice_user.menus["action_input_menu"]["position"] is None
        assert (
            alice_user.menus["action_input_menu"]["selection_id"]
            == UNPLAYABLE_DISCARD_OPTION
        )
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

    def test_cancel_unplayable_discard_prompt_restores_card_focus(self):
        game = MileByMileGame()
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)
        game.on_start()

        blocked_card = Card(id=2002, card_type=CardType.DISTANCE, value="100")
        alice.hand = [blocked_card]
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = [HazardType.STOP]
        game.current_player = alice
        game._update_turn_actions(alice)
        game.refresh_menus(alice)
        game.flush_menus()
        alice_user.clear_messages()

        game.handle_event(
            alice,
            {
                "type": "menu",
                "menu_id": "turn_menu",
                "selection_id": "card_slot_1",
            },
        )

        assert alice.id in game._pending_actions
        assert alice_user.menus["action_input_menu"]["selection_id"] == (
            UNPLAYABLE_DISCARD_OPTION
        )

        game.handle_event(
            alice,
            {
                "type": "menu",
                "menu_id": "action_input_menu",
                "selection_id": "_cancel",
            },
        )

        assert alice.id not in game._pending_actions
        assert alice.hand == [blocked_card]
        assert blocked_card not in game.discard_pile
        assert (
            turn_menu_messages(alice_user)[-1].data["selection_id"]
            == "card_slot_1"
        )

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

    def test_exact_finish_distance_rejection_explains_current_target_and_needed_miles(self):
        game = MileByMileGame(options=MileByMileOptions(round_distance=700))
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)
        game.on_start()

        blocked_card = Card(id=2201, card_type=CardType.DISTANCE, value="100")
        alice.hand = [blocked_card]
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = []
        alice_state.miles = 625
        game.current_player = alice
        game._update_turn_actions(alice)
        alice_user.clear_messages()

        game.execute_action(alice, "card_slot_1")

        assert alice.hand == [blocked_card]
        assert blocked_card not in game.discard_pile
        assert "generic" not in alice_user.get_last_spoken().lower()
        assert "You cannot play 100 miles" in alice_user.get_last_spoken()
        assert "you are at 625 miles" in alice_user.get_last_spoken()
        assert (
            "100-mile card would put you at 725 miles"
            in alice_user.get_last_spoken()
        )
        assert "past the 700-mile finish" in alice_user.get_last_spoken()
        assert "need exactly 75 more miles" in alice_user.get_last_spoken()

    def test_exact_finish_allows_100_and_200_when_total_stays_under_1000(self):
        game = MileByMileGame(options=MileByMileOptions(round_distance=1000))
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = []
        alice_state.miles = 625

        card_100 = Card(id=2204, card_type=CardType.DISTANCE, value="100")
        card_200 = Card(id=2205, card_type=CardType.DISTANCE, value="200")

        assert game._can_play_card(alice, card_100) is True
        assert game._can_play_card(alice, card_200) is True

    def test_exact_finish_playing_100_from_625_to_725_updates_distance(self):
        game = MileByMileGame(options=MileByMileOptions(round_distance=1000))
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        card = Card(id=2206, card_type=CardType.DISTANCE, value="100")
        alice.hand = [card]
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = []
        alice_state.miles = 625
        game.current_player = alice
        game._update_turn_actions(alice)

        game.execute_action(alice, "card_slot_1")

        assert card not in alice.hand
        assert card in game.discard_pile
        assert alice_state.miles == 725
        assert game.race_winner_team_index is None

    def test_relaxed_finish_allows_distance_card_to_pass_target(self):
        game = MileByMileGame(
            options=MileByMileOptions(
                round_distance=700,
                winning_score=5000,
                only_allow_perfect_crossing=False,
            )
        )
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        game.add_player("Bob", bob_user)
        game.on_start()

        card = Card(id=2202, card_type=CardType.DISTANCE, value="100")
        alice.hand = [card]
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = []
        alice_state.miles = 625
        game.current_player = alice
        game._update_turn_actions(alice)

        game.execute_action(alice, "card_slot_1")

        assert card not in alice.hand
        assert card in game.discard_pile
        assert alice_state.miles == 725
        assert game.race_winner_team_index == alice.team_index

    def test_relaxed_finish_still_obeys_speed_limit_before_target(self):
        game = MileByMileGame(
            options=MileByMileOptions(
                round_distance=1000,
                only_allow_perfect_crossing=False,
            )
        )
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = [HazardType.SPEED_LIMIT]
        alice_state.miles = 625

        card_50 = Card(id=2207, card_type=CardType.DISTANCE, value="50")
        card_100 = Card(id=2208, card_type=CardType.DISTANCE, value="100")
        card_200 = Card(id=2209, card_type=CardType.DISTANCE, value="200")

        assert game._can_play_card(alice, card_50) is True
        assert game._can_play_card(alice, card_100) is False
        assert game._can_play_card(alice, card_200) is False
        assert "Speed Limit" in game._get_unplayable_reason(alice, card_100, "en")

    def test_relaxed_finish_allows_speed_limit_legal_card_to_pass_target(self):
        game = MileByMileGame(
            options=MileByMileOptions(
                round_distance=700,
                winning_score=5000,
                only_allow_perfect_crossing=False,
            )
        )
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        card = Card(id=2210, card_type=CardType.DISTANCE, value="50")
        alice.hand = [card]
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = [HazardType.SPEED_LIMIT]
        alice_state.miles = 675
        game.current_player = alice
        game._update_turn_actions(alice)

        game.execute_action(alice, "card_slot_1")

        assert card not in alice.hand
        assert alice_state.miles == 725
        assert game.race_winner_team_index == alice.team_index

    def test_right_of_way_ignores_stale_speed_limit_when_playing_distance(self):
        game = MileByMileGame()
        alice = game.add_player("Alice", MockUser("Alice", uuid="p1"))
        game.add_player("Bob", MockUser("Bob", uuid="p2"))
        game.on_start()

        card = Card(id=2203, card_type=CardType.DISTANCE, value="100")
        alice_state = game.get_player_race_state(alice)
        assert alice_state is not None
        alice_state.problems = [HazardType.SPEED_LIMIT]
        alice_state.safeties = [SafetyType.RIGHT_OF_WAY]

        assert game._can_play_card(alice, card) is True


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
        game.current_race = 3
        game._team_manager.teams[alice.team_index].total_score = 900
        game._team_manager.teams[bob.team_index].total_score = 500
        game.race_winner_team_index = bob.team_index

        result = game.build_game_result()

        assert result.custom_data["winner_name"] == "Alice"
        assert result.custom_data["winner_ids"] == [alice.id]
        assert result.custom_data["winner_score"] == 900
        assert result.custom_data["rounds_played"] == 3
        assert result.custom_data["target_score"] == game.options.winning_score
        assert result.custom_data["race_distance"] == game.options.round_distance

    def test_delayed_action_bonus_when_trip_finishes_after_draw_pile_exhausted(self):
        game = MileByMileGame(
            options=MileByMileOptions(
                round_distance=300,
                winning_score=5000,
                reshuffle_discard_pile=False,
            )
        )
        alice_user = MockUser("Alice", uuid="p1")
        bob_user = MockUser("Bob", uuid="p2")
        alice = game.add_player("Alice", alice_user)
        bob = game.add_player("Bob", bob_user)
        game.on_start()

        winning_card = Card(id=4001, card_type=CardType.DISTANCE, value="100")
        alice.hand = [winning_card]
        alice_state = game.get_player_race_state(alice)
        bob_state = game.get_player_race_state(bob)
        assert alice_state is not None
        assert bob_state is not None
        alice_state.problems = []
        alice_state.miles = 200
        bob_state.miles = 25
        game.deck.cards = []
        game.discard_pile = []
        game.current_player = alice
        game._update_turn_actions(alice)
        alice_user.clear_messages()

        game.execute_action(alice, "card_slot_1")

        assert game.race_completed_after_deck_exhausted is True
        assert game.get_team_score(alice.team_index) == 1300
        assert any(
            "300 from delayed action" in text for text in speech_texts(alice_user)
        )


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

