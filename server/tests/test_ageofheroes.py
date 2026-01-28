"""Tests for Age of Heroes game implementation."""

from pathlib import Path

from server.games.ageofheroes.game import (
    AgeOfHeroesGame,
    AgeOfHeroesPlayer,
    AgeOfHeroesOptions,
)
from server.games.ageofheroes.cards import (
    Card,
    Deck,
    CardType,
    ResourceType,
    SpecialResourceType,
    EventType,
    MANDATORY_EVENTS,
    DISASTER_EVENTS,
)
from server.games.ageofheroes.state import (
    Tribe,
    TribeState,
    WarState,
    GamePhase,
    PlaySubPhase,
    ActionType,
    WarGoal,
    BuildingType,
    BUILDING_COSTS,
    TRIBE_SPECIAL_RESOURCE,
)
from server.games.ageofheroes.construction import (
    can_build,
    has_resources,
    get_affordable_buildings,
)
from server.games.ageofheroes.combat import (
    can_declare_war,
    get_valid_war_targets,
    get_valid_war_goals,
)
from server.games.ageofheroes.bot import (
    bot_select_action,
    score_card_for_discard,
)
from server.games.registry import GameRegistry
from server.users.test_user import MockUser
from server.messages.localization import Localization

# Initialize localization for tests
_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


class TestCardSystem:
    """Tests for card system."""

    def test_card_types(self):
        """Test card type enumeration."""
        assert CardType.RESOURCE == "resource"
        assert CardType.SPECIAL == "special"
        assert CardType.EVENT == "event"

    def test_resource_types(self):
        """Test resource type enumeration."""
        assert ResourceType.IRON == "iron"
        assert ResourceType.WOOD == "wood"
        assert ResourceType.GRAIN == "grain"
        assert ResourceType.STONE == "stone"
        assert ResourceType.GOLD == "gold"

    def test_special_resource_types(self):
        """Test special resource types."""
        assert SpecialResourceType.LIMESTONE == "limestone"
        assert SpecialResourceType.CONCRETE == "concrete"
        assert SpecialResourceType.MARBLE == "marble"

    def test_event_types(self):
        """Test event type enumeration."""
        assert EventType.POPULATION_GROWTH == "population_growth"
        assert EventType.EARTHQUAKE == "earthquake"
        assert EventType.OLYMPICS == "olympics"
        assert EventType.HERO == "hero"

    def test_card_creation(self):
        """Test creating cards."""
        card = Card(id=0, card_type=CardType.RESOURCE, subtype=ResourceType.IRON)
        assert card.id == 0
        assert card.card_type == CardType.RESOURCE
        assert card.subtype == ResourceType.IRON

    def test_card_is_resource(self):
        """Test card type checking."""
        resource = Card(id=0, card_type=CardType.RESOURCE, subtype=ResourceType.IRON)
        special = Card(id=1, card_type=CardType.SPECIAL, subtype=SpecialResourceType.MARBLE)
        event = Card(id=2, card_type=CardType.EVENT, subtype=EventType.HERO)

        assert resource.is_resource()
        assert not resource.is_special_resource()
        assert not resource.is_event()

        assert not special.is_resource()
        assert special.is_special_resource()

        assert event.is_event()

    def test_mandatory_events(self):
        """Test mandatory event checking."""
        pop_growth = Card(id=0, card_type=CardType.EVENT, subtype=EventType.POPULATION_GROWTH)
        earthquake = Card(id=1, card_type=CardType.EVENT, subtype=EventType.EARTHQUAKE)
        olympics = Card(id=2, card_type=CardType.EVENT, subtype=EventType.OLYMPICS)

        assert pop_growth.is_mandatory_event()
        assert earthquake.is_mandatory_event()
        assert not olympics.is_mandatory_event()

    def test_disaster_events(self):
        """Test disaster event checking."""
        earthquake = Card(id=0, card_type=CardType.EVENT, subtype=EventType.EARTHQUAKE)
        eruption = Card(id=1, card_type=CardType.EVENT, subtype=EventType.ERUPTION)
        pop_growth = Card(id=2, card_type=CardType.EVENT, subtype=EventType.POPULATION_GROWTH)

        assert earthquake.is_disaster()
        assert eruption.is_disaster()
        assert not pop_growth.is_disaster()


class TestDeck:
    """Tests for deck functionality."""

    def test_deck_creation(self):
        """Test creating a deck."""
        deck = Deck()
        assert deck.size() == 0
        assert deck.is_empty()

    def test_build_standard_deck(self):
        """Test building standard deck."""
        deck = Deck()
        deck.build_standard_deck(num_players=4)

        # Should have cards
        assert deck.size() > 0

        # Check resource cards (12 of each standard + 6 gold = 54)
        resource_count = sum(
            1 for c in deck.cards if c.card_type == CardType.RESOURCE
        )
        assert resource_count == 54

        # Check special resources (only for 4 tribes, 6 each = 24)
        special_count = sum(
            1 for c in deck.cards if c.card_type == CardType.SPECIAL
        )
        assert special_count == 24

    def test_deck_draw(self):
        """Test drawing cards."""
        deck = Deck()
        deck.build_standard_deck(num_players=2)
        initial_size = deck.size()

        cards = deck.draw(3)
        assert len(cards) == 3
        assert deck.size() == initial_size - 3

    def test_deck_draw_one(self):
        """Test drawing single card."""
        deck = Deck()
        deck.build_standard_deck(num_players=2)

        card = deck.draw_one()
        assert card is not None
        assert isinstance(card, Card)

    def test_deck_shuffle(self):
        """Test deck shuffling."""
        deck1 = Deck()
        deck2 = Deck()
        deck1.build_standard_deck(num_players=2)
        deck2.build_standard_deck(num_players=2)

        # Get card IDs before shuffle
        ids1 = [c.id for c in deck1.cards]
        ids2 = [c.id for c in deck2.cards]

        # Same cards
        assert sorted(ids1) == sorted(ids2)


class TestTribeState:
    """Tests for tribe state."""

    def test_tribe_state_creation(self):
        """Test creating tribe state."""
        state = TribeState(tribe=Tribe.EGYPTIANS)
        assert state.tribe == Tribe.EGYPTIANS
        assert state.cities == 1
        assert state.armies == 1
        assert state.generals == 0
        assert state.monument_progress == 0

    def test_get_available_armies(self):
        """Test available army calculation."""
        state = TribeState(tribe=Tribe.EGYPTIANS)
        state.armies = 5
        state.earthquaked_armies = 2
        state.returning_armies = 1

        assert state.get_available_armies() == 2

    def test_get_special_resource(self):
        """Test getting tribe's special resource."""
        state = TribeState(tribe=Tribe.EGYPTIANS)
        assert state.get_special_resource() == SpecialResourceType.LIMESTONE

        state2 = TribeState(tribe=Tribe.GREEKS)
        assert state2.get_special_resource() == SpecialResourceType.MARBLE

    def test_is_eliminated(self):
        """Test elimination check."""
        state = TribeState(tribe=Tribe.EGYPTIANS)
        assert not state.is_eliminated()

        state.cities = 0
        assert state.is_eliminated()

    def test_process_end_of_turn(self):
        """Test end of turn processing."""
        state = TribeState(tribe=Tribe.EGYPTIANS)
        state.returning_armies = 2
        state.returning_generals = 1
        state.earthquaked_armies = 3

        armies, generals, recovered = state.process_end_of_turn()

        assert armies == 2
        assert generals == 1
        assert recovered == 3
        assert state.returning_armies == 0
        assert state.returning_generals == 0
        assert state.earthquaked_armies == 0


class TestBuildingCosts:
    """Tests for building costs."""

    def test_army_cost(self):
        """Test army building cost."""
        cost = BUILDING_COSTS[BuildingType.ARMY]
        assert ResourceType.IRON in cost
        assert cost.count(ResourceType.GRAIN) == 2

    def test_city_cost(self):
        """Test city building cost."""
        cost = BUILDING_COSTS[BuildingType.CITY]
        assert cost.count(ResourceType.WOOD) == 2
        assert ResourceType.STONE in cost

    def test_fortress_cost(self):
        """Test fortress building cost."""
        cost = BUILDING_COSTS[BuildingType.FORTRESS]
        assert ResourceType.IRON in cost
        assert ResourceType.WOOD in cost
        assert ResourceType.STONE in cost


class TestConstruction:
    """Tests for construction system."""

    def test_has_resources(self):
        """Test resource checking."""
        player = AgeOfHeroesPlayer(id="test", name="Test")
        player.hand = [
            Card(id=0, card_type=CardType.RESOURCE, subtype=ResourceType.IRON),
            Card(id=1, card_type=CardType.RESOURCE, subtype=ResourceType.GRAIN),
            Card(id=2, card_type=CardType.RESOURCE, subtype=ResourceType.GRAIN),
        ]

        # Can afford army (Iron + 2 Grain)
        army_cost = BUILDING_COSTS[BuildingType.ARMY]
        assert has_resources(player, army_cost)

        # Cannot afford city (2 Wood + Stone)
        city_cost = BUILDING_COSTS[BuildingType.CITY]
        assert not has_resources(player, city_cost)


class TestWarState:
    """Tests for war state."""

    def test_war_state_creation(self):
        """Test creating war state."""
        war = WarState()
        assert war.attacker_index == -1
        assert war.defender_index == -1
        assert war.goal == ""

    def test_get_total_armies(self):
        """Test total army calculation."""
        war = WarState()
        war.attacker_armies = 3
        war.attacker_heroes = 2

        assert war.get_attacker_total_armies() == 5

    def test_is_both_prepared(self):
        """Test preparation check."""
        war = WarState()
        assert not war.is_both_prepared()

        war.attacker_prepared = True
        assert not war.is_both_prepared()

        war.defender_prepared = True
        assert war.is_both_prepared()

    def test_reset(self):
        """Test resetting war state."""
        war = WarState()
        war.attacker_index = 0
        war.defender_index = 1
        war.goal = WarGoal.CONQUEST
        war.attacker_armies = 5

        war.reset()

        assert war.attacker_index == -1
        assert war.goal == ""
        assert war.attacker_armies == 0


class TestAgeOfHeroesGame:
    """Tests for main game class."""

    def test_game_registration(self):
        """Test that Age of Heroes is registered."""
        game_class = GameRegistry.get("ageofheroes")
        assert game_class is not None
        assert game_class.get_name() == "Age of Heroes"
        assert game_class.get_category() == "category-uncategorized"

    def test_game_creation(self):
        """Test creating a new game."""
        game = AgeOfHeroesGame()
        assert game.status == "waiting"
        assert len(game.players) == 0
        assert game.phase == GamePhase.SETUP

    def test_player_creation(self):
        """Test player creation."""
        player = AgeOfHeroesPlayer(id="test-uuid", name="Test", is_bot=False)
        assert player.id == "test-uuid"
        assert player.name == "Test"
        assert player.hand == []
        assert player.tribe_state is None

    def test_options_defaults(self):
        """Test default options."""
        options = AgeOfHeroesOptions()
        assert options.victory_cities == 5
        assert options.neighbor_roads_only is True

    def test_player_limits(self):
        """Test player limits."""
        assert AgeOfHeroesGame.get_min_players() == 2
        assert AgeOfHeroesGame.get_max_players() == 6

    def test_serialization(self):
        """Test game serialization."""
        import json

        game = AgeOfHeroesGame()
        user = MockUser("Player1")
        game.add_player("Player1", user)

        # Modify some state
        game.options.victory_cities = 4
        game.current_day = 3

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert "players" in data
        assert len(data["players"]) == 1

        # Deserialize
        game2 = AgeOfHeroesGame.from_json(json_str)
        assert len(game2.players) == 1
        assert game2.players[0].name == "Player1"
        assert game2.options.victory_cities == 4
        assert game2.current_day == 3


class TestBotAI:
    """Tests for bot AI."""

    def test_score_card_for_discard(self):
        """Test card scoring for discard decisions."""
        player = AgeOfHeroesPlayer(id="test", name="Test")
        player.tribe_state = TribeState(tribe=Tribe.EGYPTIANS)

        # Own special resource should never be discarded
        own_special = Card(
            id=0, card_type=CardType.SPECIAL, subtype=SpecialResourceType.LIMESTONE
        )
        assert score_card_for_discard(own_special, player) == 0

        # Hero card should have low discard score (valuable)
        hero = Card(id=1, card_type=CardType.EVENT, subtype=EventType.HERO)
        hero_score = score_card_for_discard(hero, player)
        assert hero_score < 50

        # Hunger (disaster) should have high discard score
        hunger = Card(id=2, card_type=CardType.EVENT, subtype=EventType.HUNGER)
        hunger_score = score_card_for_discard(hunger, player)
        assert hunger_score > hero_score


class TestGameFlow:
    """Tests for game flow."""

    def test_game_start(self):
        """Test starting a game."""
        game = AgeOfHeroesGame()
        user1 = MockUser("Player1")
        user2 = MockUser("Player2")
        game.add_player("Player1", user1)
        game.add_player("Player2", user2)

        game.on_start()

        assert game.status == "playing"
        assert game.phase == GamePhase.SETUP
        # Players should have tribes assigned
        assert game.players[0].tribe_state is not None
        assert game.players[1].tribe_state is not None

    def test_tribes_assigned(self):
        """Test tribe assignment."""
        game = AgeOfHeroesGame()
        for i in range(4):
            user = MockUser(f"Player{i}")
            game.add_player(f"Player{i}", user)

        game.on_start()

        # All players should have different tribes
        tribes = [p.tribe_state.tribe for p in game.players]
        assert len(set(tribes)) == 4


class TestPlayTest:
    """Integration tests for complete game play."""

    def test_two_player_bot_game_runs(self):
        """Test that a 2-player bot game can run for some ticks."""
        from server.users.bot import Bot

        game = AgeOfHeroesGame()
        game.options.victory_cities = 3  # Lower for faster test

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run for some ticks to verify no crashes
        for _ in range(500):
            if game.status == "finished":
                break
            game.on_tick()

        # Game should either be finished or still playing
        assert game.status in ("playing", "finished")

    def test_four_player_game(self):
        """Test a 4-player game."""
        from server.users.bot import Bot

        game = AgeOfHeroesGame()

        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        assert len(game.players) == 4
        # All should have unique tribes
        tribes = [p.tribe_state.tribe for p in game.players]
        assert len(set(tribes)) == 4


class TestPersistence:
    """Tests for game persistence/serialization."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved."""
        game = AgeOfHeroesGame()
        user1 = MockUser("Player1")
        user2 = MockUser("Player2")
        game.add_player("Player1", user1)
        game.add_player("Player2", user2)

        game.on_start()

        # Modify state
        game.players[0].tribe_state.cities = 3
        game.players[0].tribe_state.monument_progress = 2
        game.current_day = 5

        # Serialize and deserialize
        data = game.to_dict()
        game2 = AgeOfHeroesGame.from_dict(data)

        assert game2.players[0].tribe_state.cities == 3
        assert game2.players[0].tribe_state.monument_progress == 2
        assert game2.current_day == 5
