"""Rules, accessibility, persistence, and bot coverage for Skip-Bo."""

import json
import random
from itertools import product
from pathlib import Path

import pytest

from ..game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ..games.registry import GameRegistry
from ..games.skipbo import cards
from ..games.skipbo.cards import SkipBoCard
from ..games.skipbo.game import (
    BUILDING_PILE_COUNT,
    DISCARD_PILE_COUNT,
    HAND_SIZE,
    MIN_MATCH_TARGET,
    NEXT_ROUND_SEQUENCE_ID,
    SCORING_MATCH,
    SETUP_BEGINNER,
    SOUND_DISCARD_FAMILY,
    SOUND_DRAW_FAMILY,
    SOUND_GAME_WIN,
    SOUND_PLAY_FAMILY,
    SOUND_SHUFFLE_FAMILY,
    STOCK_SHORT,
    STOCK_SHORT_FIFTEEN,
    SkipBoGame,
    SkipBoOptions,
    SkipBoPlayer,
)
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]
Localization.init(ROOT / "server" / "locales")


def card(card_id: int, value: int) -> SkipBoCard:
    return SkipBoCard(id=card_id, value=value)


def locale_keys(path: Path) -> set[str]:
    return {
        line.split("=", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        and not line.lstrip().startswith("#")
        and "=" in line
        and not line[0].isspace()
    }


def make_game(
    player_count: int = 2,
    *,
    start: bool = False,
    bots: bool = False,
    client_type: str = "python",
    seed: int = 1,
    **option_overrides,
) -> SkipBoGame:
    game = SkipBoGame(options=SkipBoOptions(**option_overrides))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        user = (
            Bot(name, uuid=f"p{index + 1}")
            if bots
            else MockUser(name, uuid=f"p{index + 1}")
        )
        if not bots:
            user.client_type = client_type
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        random.seed(seed)
        game.on_start()
        game.flush_menus()
    return game


def set_turn(game: SkipBoGame, player: SkipBoPlayer) -> None:
    game.current_player = player
    game.refresh_menus()
    game.flush_menus()


def choice(
    game: SkipBoGame,
    player: SkipBoPlayer,
    *,
    source: str,
    building: int = 0,
    owner: SkipBoPlayer | None = None,
):
    return next(
        item
        for item in game._legal_play_choices(player)
        if item.source_kind == source
        and item.building_pile_index == building
        and (owner is None or item.owner.id == owner.id)
    )


def count_cards(game: SkipBoGame) -> int:
    return sum(
        [
            len(game.deck),
            len(game.completed_cards),
            *(len(pile) for pile in game.building_piles),
            *(len(player.hand) for player in game.players),
            *(len(player.stock_pile) for player in game.players),
            *(len(pile) for player in game.players for pile in player.discard_piles),
        ]
    )


def sound_names(user: MockUser) -> list[str]:
    return [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound"
    ]


def test_registration_metadata_and_defaults() -> None:
    assert GameRegistry.get("skipbo") is SkipBoGame
    assert SkipBoGame.get_name() == "Skip-Bo"
    assert SkipBoGame.get_name_key() == "game-name-skipbo"
    assert SkipBoGame.get_category() == "cards"
    assert SkipBoGame.get_min_players() == 2
    assert SkipBoGame.get_max_players() == 6
    assert SkipBoGame.get_supported_leaderboards() == [
        "wins",
        "rating",
        "games_played",
    ]

    options = SkipBoOptions()
    assert options.stock_mode == "standard"
    assert options.setup_mode == "classic"
    assert options.scoring_mode == "single"
    assert options.winning_score == 500
    assert options.team_mode == "individual"


def test_official_deck_composition() -> None:
    deck = cards.build_deck()
    assert len(deck) == cards.DECK_SIZE == 168
    assert len({item.id for item in deck}) == cards.DECK_SIZE
    assert sum(item.is_wild for item in deck) == cards.WILD_COUNT == 24
    for value in range(cards.MIN_NUMBER, cards.MAX_NUMBER + 1):
        assert sum(item.value == value for item in deck) == cards.NUMBER_COPIES


def test_localization_and_documentation_are_present_and_paired() -> None:
    en = ROOT / "server" / "locales" / "en" / "skipbo.ftl"
    vi = ROOT / "server" / "locales" / "vi" / "skipbo.ftl"
    assert en.exists()
    assert vi.exists()
    assert locale_keys(en) == locale_keys(vi)
    assert (
        ROOT / "server" / "documentation" / "content" / "en" / "games" / "skipbo.md"
    ).exists()
    assert (
        ROOT / "server" / "documentation" / "content" / "vi" / "games" / "skipbo.md"
    ).exists()


@pytest.mark.parametrize(
    ("player_count", "expected_stock"),
    [(2, 30), (4, 30), (5, 20), (6, 20)],
)
def test_standard_stock_size_follows_official_player_chart(
    player_count: int, expected_stock: int
) -> None:
    game = make_game(player_count, start=True)
    assert {len(player.stock_pile) for player in game.get_active_players()} == {
        expected_stock
    }
    assert len(game.deck) == cards.DECK_SIZE - player_count * expected_stock - HAND_SIZE


def test_short_game_deals_ten_stock_cards() -> None:
    game = make_game(6, start=True, stock_mode=STOCK_SHORT)
    assert all(len(player.stock_pile) == 10 for player in game.get_active_players())


def test_current_official_fifteen_card_quick_game() -> None:
    game = make_game(6, start=True, stock_mode=STOCK_SHORT_FIFTEEN)
    assert all(len(player.stock_pile) == 15 for player in game.get_active_players())


def test_beginner_setup_seeds_all_discard_and_building_spaces() -> None:
    game = make_game(4, start=True, setup_mode=SETUP_BEGINNER)

    assert all(
        len(pile) == 1 for player in game.players for pile in player.discard_piles
    )
    assert all(
        (value == 0 and not pile) or (1 <= value <= 11 and len(pile) == 1)
        for pile, value in zip(game.building_piles, game.building_values, strict=True)
    )
    assert count_cards(game) == cards.DECK_SIZE


def test_beginner_setup_immediately_completes_and_counts_seeded_twelves() -> None:
    game = make_game(2)
    pop_order = [
        *(card(3000 + index, 5) for index in range(8)),
        card(3010, 1),
        card(3011, 12),
        card(3012, 0),
        card(3013, 7),
    ]
    game.deck = list(reversed(pop_order))

    completed = game._deal_beginner_setup(game.players)

    assert completed == 1
    assert [item.value for item in game.completed_cards] == [12]
    assert game.building_values == [1, 0, 1, 7]
    assert [[item.value for item in pile] for pile in game.building_piles] == [
        [1],
        [],
        [0],
        [7],
    ]


@pytest.mark.parametrize(
    ("player_count", "team_mode", "valid"),
    [
        (4, "2v2", True),
        (6, "2v2v2", True),
        (3, "2v2", False),
        (6, "2v2", False),
        (4, "2v2v2", False),
        (4, "3v3", False),
    ],
)
def test_partnership_modes_require_official_two_player_teams(
    player_count: int, team_mode: str, valid: bool
) -> None:
    game = make_game(player_count, team_mode=team_mode)
    errors = game.prestart_validate()
    assert ("skipbo-error-partnership-player-count" not in errors) is valid


def test_prestart_validation_rejects_corrupt_option_values() -> None:
    game = make_game(2)
    game.options.stock_mode = "marathon"
    game.options.setup_mode = "advanced"
    game.options.scoring_mode = "mystery"
    game.options.winning_score = 10
    errors = game.prestart_validate()
    assert "skipbo-error-invalid-stock-mode" in errors
    assert "skipbo-error-invalid-setup-mode" in errors
    assert "skipbo-error-invalid-scoring-mode" in errors

    game.options.scoring_mode = SCORING_MATCH
    errors = game.prestart_validate()
    assert (
        "skipbo-error-winning-score-range",
        {"value": 10, "min": 25, "max": 5000},
    ) in errors

    game.options.winning_score = "500"
    errors = game.prestart_validate()
    assert (
        "skipbo-error-winning-score-range",
        {"value": "500", "min": 25, "max": 5000},
    ) in errors


def test_match_target_option_is_visible_only_for_scored_matches() -> None:
    options = SkipBoOptions()
    assert options.is_option_visible("winning_score") is False

    options.scoring_mode = SCORING_MATCH
    assert options.is_option_visible("winning_score") is True


def test_start_announcement_distinguishes_single_and_scored_games() -> None:
    single = make_game(2, start=True)
    single_messages = single.get_user(single.players[0]).get_spoken_messages()
    assert any(message.startswith("The game begins.") for message in single_messages)
    assert all("Scored game 1" not in message for message in single_messages)

    scored = make_game(2, start=True, scoring_mode=SCORING_MATCH)
    scored_messages = scored.get_user(scored.players[0]).get_spoken_messages()
    assert any(
        message.startswith("Scored game 1 begins.") for message in scored_messages
    )


def test_start_draws_only_for_the_first_player_and_announces_public_stock_tops() -> (
    None
):
    game = make_game(2, start=True)
    current = game.current_player
    other = next(player for player in game.get_active_players() if player != current)
    assert isinstance(current, SkipBoPlayer)
    assert isinstance(other, SkipBoPlayer)
    assert len(current.hand) == 5
    assert other.hand == []

    current_user = game.get_user(current)
    other_user = game.get_user(other)
    assert current_user is not None and other_user is not None
    assert any(
        "Your face-up stock card" in text for text in current_user.get_spoken_messages()
    )
    assert any(
        f"{current.name}'s face-up stock card" in text
        for text in other_user.get_spoken_messages()
    )


def test_legal_sources_include_hand_stock_and_discard() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = [card(1000, 1), card(1001, 7)]
    player.stock_pile = [card(1002, 1)]
    player.discard_piles = [[card(1003, 1)], [], [], []]
    game.building_piles = [[] for _ in range(4)]

    choices = game._legal_play_choices(player)
    assert {item.source_kind for item in choices} == {"hand", "stock", "discard"}
    assert all(item.needed_value == 1 for item in choices)
    assert {item.building_pile_index for item in choices} == {0, 1, 2, 3}


def test_wild_can_take_the_next_value_on_any_building_pile() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = [card(1100, 0)]
    game.building_piles = [
        [card(1200 + value, value) for value in range(1, size + 1)]
        for size in (0, 3, 7, 11)
    ]
    game.building_values = [0, 3, 7, 11]

    choices = [
        item for item in game._legal_play_choices(player) if item.source_kind == "hand"
    ]
    assert [item.needed_value for item in choices] == [1, 4, 8, 12]


def test_playing_the_last_hand_card_refills_immediately_and_keeps_the_turn() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = [card(1300, 1)]
    player.stock_pile = [card(1301, 9)]
    game.building_piles = [[] for _ in range(4)]
    game.deck = [card(1400 + value, value) for value in range(2, 8)]
    original_turn = game.turn_index

    game._action_play(player, choice(game, player, source="hand").action_id)

    assert len(player.hand) == 5
    assert game.turn_index == original_turn
    assert len(game.building_piles[0]) == 1
    assert any(
        "immediately draw 5 cards" in text
        for text in game.get_user(player).get_spoken_messages()
    )


def test_discarding_the_last_hand_card_does_not_refill_until_next_turn() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = [card(1500, 8)]
    game.deck = [card(1501 + value, value) for value in range(1, 8)]

    game._action_end_turn(player, "2", "end_turn_1500")
    game.flush_menus()

    assert player.hand == []
    assert player.discard_piles[2][-1].value == 8
    assert game.current_player != player
    assert game.get_user(player).menus["turn_menu"]["selection_id"] == (
        "skipbo_hand_empty"
    )


def test_discard_selector_locks_other_gameplay_until_submitted() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = [card(1550, 1), card(1551, 9)]
    player.stock_pile = [card(1552, 8)]
    game.building_piles = [[] for _ in range(BUILDING_PILE_COUNT)]
    game.building_values = [0 for _ in range(BUILDING_PILE_COUNT)]
    game.refresh_menus()
    game.flush_menus()

    play_action = choice(game, player, source="hand", building=0).action_id
    game.execute_action(player, "end_turn_1551")

    user = game.get_user(player)
    assert user is not None
    assert game._pending_actions[player.id] == "end_turn_1551"
    assert "action_input_menu" in user.menus

    user.clear_messages()
    game.execute_action(player, play_action)

    assert user.get_last_spoken() == "Choose a discard pile first."
    assert [item.id for item in player.hand] == [1550, 1551]
    assert game.building_piles[0] == []

    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "2",
        },
    )

    assert player.id not in game._pending_actions
    assert [item.id for item in player.hand] == [1550]
    assert player.discard_piles[2][-1].id == 1551
    assert game.current_player != player
    assert user.menus["turn_menu"]["selection_id"] == "end_turn_1550"


def test_completing_twelve_clears_the_building_slot_for_recycling() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = [card(1600, 12), card(1601, 4)]
    game.building_piles[0] = [card(1700 + value, value) for value in range(1, 12)]
    game.building_values[0] = 11

    game._action_play(player, choice(game, player, source="hand").action_id)

    assert game.building_piles[0] == []
    assert len(game.completed_cards) == 12
    assert {item.value for item in game.completed_cards if not item.is_wild} == set(
        range(1, 13)
    )


def test_completing_a_building_pile_makes_cards_available_for_an_empty_hand() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = []
    player.stock_pile = [card(1750, 9), card(1751, 12)]
    game.deck = []
    game.completed_cards = []
    game.building_piles[0] = [card(1760 + value, value) for value in range(1, 12)]
    game.building_values[0] = 11

    game._action_play(player, choice(game, player, source="stock").action_id)

    assert len(player.hand) == HAND_SIZE
    assert len(game.deck) == 7
    assert game.completed_cards == []


def test_completed_building_cards_are_recycled_only_when_draw_pile_is_empty() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    player.hand = [card(1800, 4)] * 4
    game.deck = []
    game.completed_cards = [card(1810, 1), card(1811, 2)]

    random.seed(4)
    drawn = game._draw_to_five(player, reason="turn")

    assert drawn == 1
    assert len(player.hand) == 5
    assert len(game.deck) == 1
    assert game.completed_cards == []


def test_active_building_cards_are_never_recycled_into_the_draw_pile() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    player.hand = [card(1820, 4)] * 4
    game.deck = []
    game.completed_cards = []
    game.building_piles = [
        [card(1830, 1), card(1831, 2), card(1832, 3)],
        [card(1833, 1), card(1834, 2)],
        [],
        [],
    ]
    game.building_values = [3, 2, 0, 0]

    drawn = game._draw_to_five(player, reason="turn")

    assert drawn == 0
    assert game.deck == []
    assert [[item.value for item in pile] for pile in game.building_piles] == [
        [1, 2, 3],
        [1, 2],
        [],
        [],
    ]
    assert game.building_values == [3, 2, 0, 0]
    assert game._draw_available() is False


def test_playing_stock_reveals_the_next_card_publicly() -> None:
    game = make_game(2, start=True)
    player, observer = game.players[:2]
    set_turn(game, player)
    player.hand = [card(1900, 8)]
    player.stock_pile = [card(1901, 7), card(1902, 1)]
    game.building_piles = [[] for _ in range(4)]
    game.get_user(player).clear_messages()
    game.get_user(observer).clear_messages()

    game._action_play(player, choice(game, player, source="stock").action_id)

    assert player.stock_pile[-1].value == 7
    assert any(
        "Your next face-up stock card is 7" in text
        for text in game.get_user(player).get_spoken_messages()
    )
    assert any(
        f"{player.name}'s next face-up stock card is 7" in text
        for text in game.get_user(observer).get_spoken_messages()
    )


def test_actor_and_observer_hear_distinct_play_and_discard_messages() -> None:
    game = make_game(2, start=True)
    player, observer = game.players[:2]
    set_turn(game, player)
    player.hand = [card(2000, 1), card(2001, 9)]
    game.building_piles = [[] for _ in range(4)]
    actor_user = game.get_user(player)
    observer_user = game.get_user(observer)
    actor_user.clear_messages()
    observer_user.clear_messages()

    game._action_play(player, choice(game, player, source="hand").action_id)
    assert any(
        text.startswith("You play 1") for text in actor_user.get_spoken_messages()
    )
    assert any(
        text.startswith(f"{player.name} plays 1")
        for text in observer_user.get_spoken_messages()
    )

    actor_user.clear_messages()
    observer_user.clear_messages()
    game._action_end_turn(player, "0", "end_turn_2001")
    assert any(
        text.startswith("You discard 9") for text in actor_user.get_spoken_messages()
    )
    assert any(
        text.startswith(f"{player.name} discards 9")
        for text in observer_user.get_spoken_messages()
    )


def test_shared_card_sounds_cover_setup_draw_play_discard_turn_and_victory() -> None:
    game = make_game(2, start=True, seed=2)
    player, observer = game.players[:2]
    player_user = game.get_user(player)
    observer_user = game.get_user(observer)
    assert isinstance(player_user, MockUser)
    assert isinstance(observer_user, MockUser)

    opening_sounds = sound_names(player_user) + sound_names(observer_user)
    assert SOUND_SHUFFLE_FAMILY in opening_sounds
    assert SOUND_DRAW_FAMILY in opening_sounds
    assert "turn.ogg" in sound_names(game.get_user(game.current_player))

    set_turn(game, player)
    player.hand = [card(2050, 1), card(2051, 9)]
    player.stock_pile = [card(2052, 8)]
    game.building_piles = [[] for _ in range(BUILDING_PILE_COUNT)]
    game.building_values = [0 for _ in range(BUILDING_PILE_COUNT)]
    player_user.clear_messages()
    observer_user.clear_messages()

    game._action_play(player, choice(game, player, source="hand").action_id)
    assert SOUND_PLAY_FAMILY in sound_names(player_user)

    player_user.clear_messages()
    observer_user.clear_messages()
    game._action_end_turn(player, "0", "end_turn_2051")
    assert SOUND_DISCARD_FAMILY in sound_names(player_user)

    set_turn(game, player)
    player.hand = [card(2053, 9)]
    player.stock_pile = [card(2054, 1)]
    game.building_piles = [[] for _ in range(BUILDING_PILE_COUNT)]
    game.building_values = [0 for _ in range(BUILDING_PILE_COUNT)]
    player_user.clear_messages()
    observer_user.clear_messages()

    game._action_play(player, choice(game, player, source="stock").action_id)
    assert sound_names(player_user).count(SOUND_GAME_WIN) == 1


def test_partnership_can_use_partner_stock_and_discard_but_not_partner_hand() -> None:
    game = make_game(4, start=True, team_mode="2v2")
    player = game.players[0]
    partner = game.players[2]
    set_turn(game, player)
    player.hand = [card(2100, 9)]
    player.stock_pile = [card(2101, 8)]
    partner.hand = [card(2102, 1)]
    partner.stock_pile = [card(2103, 1)]
    partner.discard_piles = [[card(2104, 1)], [], [], []]
    game.building_piles = [[] for _ in range(4)]

    choices = game._legal_play_choices(player)
    assert any(
        item.source_kind == "stock" and item.owner is partner for item in choices
    )
    assert any(
        item.source_kind == "discard" and item.owner is partner for item in choices
    )
    assert all(item.card.id != 2102 for item in choices)


def test_partnership_round_ends_only_after_both_stock_piles_are_empty() -> None:
    game = make_game(4, start=True, team_mode="2v2", scoring_mode=SCORING_MATCH)
    player = game.players[0]
    partner = game.players[2]
    set_turn(game, player)
    player.stock_pile = [card(2200, 9)]
    partner.stock_pile = [card(2201, 1)]
    game.building_piles = [[] for _ in range(4)]

    game._action_play(
        player,
        choice(game, player, source="stock", owner=partner).action_id,
    )
    assert partner.stock_pile == []
    assert player.stock_pile
    assert not game.has_active_sequence(sequence_id=NEXT_ROUND_SEQUENCE_ID)
    assert game.status == "playing"


def test_official_scoring_is_twenty_five_plus_five_per_opposing_stock_card() -> None:
    game = make_game(
        2,
        start=True,
        scoring_mode=SCORING_MATCH,
        winning_score=500,
    )
    winner, loser = game.players[:2]
    set_turn(game, winner)
    winner.stock_pile = [card(2300, 1)]
    loser.stock_pile = [card(2301, 4), card(2302, 5), card(2303, 6)]
    game.building_piles = [[] for _ in range(4)]

    game._action_play(winner, choice(game, winner, source="stock").action_id)

    team = game._team_manager.get_team(winner.name)
    assert team is not None
    assert team.total_score == 40
    assert winner.score == 40
    assert game.has_active_sequence(sequence_id=NEXT_ROUND_SEQUENCE_ID)


def test_scored_match_rotates_dealer_and_starts_next_game_after_sequence() -> None:
    game = make_game(2, start=True, scoring_mode=SCORING_MATCH, winning_score=500)
    winner, loser = game.players[:2]
    set_turn(game, winner)
    initial_dealer = game.dealer_index
    winner.stock_pile = [card(2400, 1)]
    loser.stock_pile = [card(2401, 2)]
    game.building_piles = [[] for _ in range(4)]

    game._action_play(winner, choice(game, winner, source="stock").action_id)
    for _ in range(61):
        game.on_tick()

    assert game.round == 2
    assert game.dealer_index == (initial_dealer + 1) % 2
    assert not game.has_active_sequence(sequence_id=NEXT_ROUND_SEQUENCE_ID)
    assert all(len(player.stock_pile) == 30 for player in game.players)


def test_single_game_finishes_as_soon_as_a_stock_pile_is_empty() -> None:
    game = make_game(2, start=True)
    winner, loser = game.players[:2]
    set_turn(game, winner)
    winner.stock_pile = [card(2500, 1)]
    loser.stock_pile = [card(2501, 2), card(2502, 3)]
    game.building_piles = [[] for _ in range(4)]
    winner_user = game.get_user(winner)
    loser_user = game.get_user(loser)
    winner_user.clear_messages()
    loser_user.clear_messages()

    game._action_play(winner, choice(game, winner, source="stock").action_id)

    assert game.status == "finished"
    assert game.game_active is False
    assert game.winner_team_index == game._team_manager.get_team(winner.name).index
    assert any(
        message == "You empty your stock pile and win the game."
        for message in winner_user.get_spoken_messages()
    )
    assert any(
        message == f"{winner.name} empties their stock pile and wins the game."
        for message in loser_user.get_spoken_messages()
    )
    assert all(
        "scored game" not in message.lower() and "match" not in message.lower()
        for message in winner_user.get_spoken_messages()
    )


def test_scored_game_announces_both_game_and_match_wins_at_the_target() -> None:
    game = make_game(2, start=True, scoring_mode=SCORING_MATCH, winning_score=25)
    winner, loser = game.players[:2]
    set_turn(game, winner)
    winner.stock_pile = [card(2550, 1)]
    loser.stock_pile = [card(2551, 2)]
    game.building_piles = [[] for _ in range(BUILDING_PILE_COUNT)]
    winner_user = game.get_user(winner)
    winner_user.clear_messages()

    game._action_play(winner, choice(game, winner, source="stock").action_id)

    messages = winner_user.get_spoken_messages()
    assert any("win scored game 1" in message for message in messages)
    assert any("win the Skip-Bo match" in message for message in messages)
    assert sound_names(winner_user).count(SOUND_GAME_WIN) == 1


def test_serialization_preserves_every_pile_and_active_round_transition() -> None:
    game = make_game(4, start=True, team_mode="2v2", scoring_mode=SCORING_MATCH)
    game.building_piles[0] = [card(2601, 1), card(2602, 0)]
    game.building_values[0] = 2
    game.completed_cards = [card(2603, 3)]
    game.players[0].discard_piles[3] = [card(2604, 8), card(2605, 7)]
    game._team_manager.teams[0].total_score = 125
    game.start_sequence(
        NEXT_ROUND_SEQUENCE_ID,
        [
            SequenceBeat.pause(20),
            SequenceBeat(ops=[SequenceOperation.callback_op("start_next_round")]),
        ],
        tag="skipbo_round_transition",
        lock_scope=game.SEQUENCE_LOCK_GAMEPLAY,
        pause_bots=True,
    )

    payload = json.loads(game.to_json())
    loaded = SkipBoGame.from_json(json.dumps(payload))

    assert loaded.options.team_mode == "2v2"
    assert [item.value for item in loaded.building_piles[0]] == [1, 0]
    assert loaded.building_values[0] == 2
    assert loaded.completed_cards[0].value == 3
    assert [item.value for item in loaded.players[0].discard_piles[3]] == [8, 7]
    assert loaded._team_manager.teams[0].total_score == 125
    assert loaded.has_active_sequence(sequence_id=NEXT_ROUND_SEQUENCE_ID)


def test_discard_selector_has_four_contextual_stable_options() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.discard_piles = [[], [card(2700, 6)], [], []]

    assert game._options_for_discard_pile(player) == ["0", "1", "2", "3"]
    assert game._discard_pile_option_label(player, "0") == "Discard pile 1: empty"
    assert game._discard_pile_option_label(player, "1") == "Discard pile 2: 6 on top"


def test_desktop_inspection_actions_stay_in_the_actions_menu() -> None:
    game = make_game(2, start=True)
    player = game.current_player
    assert isinstance(player, SkipBoPlayer)

    inspection_ids = {
        "read_building_piles",
        "read_stock_piles",
        "read_own_discard_piles",
        "read_discard_piles",
    }
    visible_ids = {
        resolved.action.id for resolved in game.get_all_visible_actions(player)
    }
    enabled_ids = {
        resolved.action.id for resolved in game.get_all_enabled_actions(player)
    }

    assert inspection_ids.isdisjoint(visible_ids)
    assert inspection_ids <= enabled_ids
    assert all(
        "read_hand" not in binding.actions
        for bindings in game._keybinds.values()
        for binding in bindings
    )


def test_touch_inspection_actions_follow_the_standard_utility_order() -> None:
    game = make_game(2, start=True, client_type="mobile")
    current = game.current_player
    assert isinstance(current, SkipBoPlayer)
    current_ids = [
        resolved.action.id for resolved in game.get_all_visible_actions(current)
    ]
    ordered_info = [
        "read_building_piles",
        "read_stock_piles",
        "read_own_discard_piles",
        "read_discard_piles",
    ]
    assert [
        action_id for action_id in current_ids if action_id in ordered_info
    ] == ordered_info


def test_hand_cards_remain_private_and_report_off_turn_activation() -> None:
    game = make_game(2, start=True)
    current = game.current_player
    assert isinstance(current, SkipBoPlayer)
    waiting = next(player for player in game.players if player is not current)
    assert isinstance(waiting, SkipBoPlayer)
    waiting.hand = [card(2710, 4), card(2711, 0)]
    game.refresh_menus(waiting)
    game.flush_menus()

    user = game.get_user(waiting)
    assert user is not None
    hand_items = user.menus["turn_menu"]["items"][:2]
    assert [(item.id, item.text, item.read_only) for item in hand_items] == [
        ("end_turn_2710", "Hand: 4", False),
        ("end_turn_2711", "Hand: Skip-Bo wild", False),
    ]

    user.clear_messages()
    game.execute_action(waiting, "end_turn_2710")
    assert user.get_last_spoken() == "It's not your turn."
    assert [item.id for item in waiting.hand] == [2710, 2711]

    user.set_locale("vi")
    user.clear_messages()
    game.execute_action(waiting, "end_turn_2711")
    assert user.get_last_spoken() == "Chưa đến lượt của bạn."
    assert [item.id for item in waiting.hand] == [2710, 2711]

    current_user = game.get_user(current)
    assert current_user is not None
    assert all(
        item.id not in {"end_turn_2710", "end_turn_2711"}
        for item in current_user.menus["turn_menu"]["items"]
    )

    set_turn(game, waiting)
    active_items = {item.id: item for item in user.menus["turn_menu"]["items"]}
    assert active_items["end_turn_2710"].read_only is False
    assert active_items["end_turn_2711"].read_only is False


def test_waiting_player_with_no_dealt_hand_gets_accurate_vietnamese_status() -> None:
    game = make_game(2, start=True)
    current = game.current_player
    waiting = next(player for player in game.players if player is not current)
    user = game.get_user(waiting)
    assert user is not None
    user.set_locale("vi")

    game.refresh_menus(waiting)
    game.flush_menus()

    first_item = user.menus["turn_menu"]["items"][0]
    assert first_item.id == "skipbo_hand_empty"
    assert first_item.text == "Bạn chưa có bài trên tay."


def test_discard_inspection_opens_single_target_directly() -> None:
    game = make_game(2, start=True)
    viewer, target = game.players
    target.discard_piles[1] = [card(2720, 7)]

    game.execute_action(viewer, "read_discard_piles")

    user = game.get_user(viewer)
    assert user is not None
    assert "action_input_menu" not in user.menus
    status_text = [item.text for item in user.menus["status_box"]["items"]]
    assert status_text[0] == f"{target.name}'s discard piles:"
    assert status_text[2] == "Discard pile 2: 7 on top, 1 card total."


def test_discard_inspection_uses_stable_player_ids_and_excludes_self() -> None:
    game = make_game(3, start=True)
    viewer = game.players[0]

    game.execute_action(viewer, "read_discard_piles")

    user = game.get_user(viewer)
    assert user is not None
    items = user.menus["action_input_menu"]["items"]
    assert [item.id for item in items] == ["p2", "p3", "_cancel"]
    assert [item.text for item in items[:-1]] == ["Player2", "Player3"]


def test_touch_spectator_can_inspect_any_player_but_no_private_cards() -> None:
    game = make_game(2, start=True)
    spectator_user = MockUser("Watcher", uuid="watcher")
    spectator_user.client_type = "mobile"
    spectator = game.add_spectator("Watcher", spectator_user)
    game.refresh_menus(spectator)
    game.flush_menus()

    visible_ids = {
        resolved.action.id for resolved in game.get_all_visible_actions(spectator)
    }
    enabled_ids = {
        resolved.action.id for resolved in game.get_all_enabled_actions(spectator)
    }

    assert {
        "read_building_piles",
        "read_stock_piles",
        "read_discard_piles",
    } <= visible_ids
    assert "read_own_discard_piles" not in enabled_ids
    assert game._discard_owner_options(spectator) == ["p1", "p2"]
    assert all(
        not item.id.startswith("end_turn_")
        for item in spectator_user.menus["turn_menu"]["items"]
    )


def test_own_discard_piles_have_a_dedicated_private_action() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    player.discard_piles[0] = [card(2730, 3)]

    game.execute_action(player, "read_own_discard_piles")

    user = game.get_user(player)
    assert user is not None
    status_text = [item.text for item in user.menus["status_box"]["items"]]
    assert status_text[0] == "Your discard piles:"
    assert status_text[1] == "Discard pile 1: 3 on top, 1 card total."


def test_live_pile_status_rows_use_stable_semantic_ids() -> None:
    game = make_game(2, start=True)
    player = game.players[0]

    assert [item.id for item in game._building_status_lines("en")] == [
        "skipbo_building_0",
        "skipbo_building_1",
        "skipbo_building_2",
        "skipbo_building_3",
        "skipbo_draw_pool",
    ]
    assert [item.id for item in game._stock_status_lines("en")] == [
        "skipbo_stock_p1",
        "skipbo_stock_p2",
    ]
    assert [item.id for item in game._discard_status_lines(player, "en")] == [
        "skipbo_discard_header_p1",
        "skipbo_discard_p1_0",
        "skipbo_discard_p1_1",
        "skipbo_discard_p1_2",
        "skipbo_discard_p1_3",
    ]


def test_play_labels_are_compact_and_complete() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = [card(2740, 0)]
    player.stock_pile = [card(2741, 9)]
    game.building_piles = [[] for _ in range(BUILDING_PILE_COUNT)]
    game.building_values = [0 for _ in range(BUILDING_PILE_COUNT)]

    play = choice(game, player, source="hand", building=0)

    assert game._get_play_label(player, play.action_id) == (
        "Skip-Bo as 1 — hand to pile 1"
    )


def test_play_focus_follows_the_same_building_pile_when_possible() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = [card(2750, 1), card(2751, 2), card(2752, 9)]
    player.stock_pile = [card(2753, 8)]
    player.discard_piles = [[] for _ in range(DISCARD_PILE_COUNT)]
    game.building_piles = [[] for _ in range(BUILDING_PILE_COUNT)]
    game.building_values = [0 for _ in range(BUILDING_PILE_COUNT)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(
        player,
        choice(game, player, source="hand", building=0).action_id,
    )
    game.flush_menus()

    user = game.get_user(player)
    assert user is not None
    assert user.menus["turn_menu"]["selection_id"] == "play_h_2751_b_0"


def test_play_focus_falls_back_to_the_first_end_turn_card() -> None:
    game = make_game(2, start=True)
    player = game.players[0]
    set_turn(game, player)
    player.hand = [card(2760, 1), card(2761, 9), card(2762, 7)]
    player.stock_pile = [card(2763, 8)]
    player.discard_piles = [[] for _ in range(DISCARD_PILE_COUNT)]
    game.building_piles = [[] for _ in range(BUILDING_PILE_COUNT)]
    game.building_values = [0 for _ in range(BUILDING_PILE_COUNT)]
    game.refresh_menus()
    game.flush_menus()

    game.execute_action(
        player,
        choice(game, player, source="hand", building=0).action_id,
    )
    game.flush_menus()

    user = game.get_user(player)
    assert user is not None
    assert user.menus["turn_menu"]["selection_id"] == "end_turn_2762"


def test_bot_prioritizes_a_playable_stock_card() -> None:
    game = make_game(2, start=True, bots=True, stock_mode=STOCK_SHORT)
    player = game.players[0]
    set_turn(game, player)
    player.stock_pile = [card(2800, 1)]
    player.hand = [card(2801, 1), card(2802, 5)]
    game.building_piles = [[] for _ in range(4)]

    random.seed(3)
    action_id = game.bot_think(player)
    selected = game._choice_for_action(player, action_id)
    assert selected is not None
    assert selected.source_kind == "stock"


def test_two_bot_quick_game_completes_and_conserves_every_card() -> None:
    game = make_game(2, start=True, bots=True, seed=4, stock_mode=STOCK_SHORT)

    for _ in range(2_000):
        if game.status == "finished":
            break
        game.on_tick()
        game.flush_menus()

    assert game.status == "finished"
    assert count_cards(game) == cards.DECK_SIZE


def test_six_bot_beginner_game_cannot_stall_when_initial_draw_cards_run_out() -> None:
    game = make_game(6, start=True, bots=True, seed=2, setup_mode=SETUP_BEGINNER)

    for _ in range(5_000):
        if game.status == "finished":
            break
        game.on_tick()
        game.flush_menus()

    assert game.status == "finished"
    assert count_cards(game) == cards.DECK_SIZE


@pytest.mark.parametrize(
    ("team_mode", "player_count"),
    [("individual", 2), ("individual", 6), ("2v2", 4), ("2v2v2", 6)],
)
def test_every_gameplay_option_combination_completes_cleanly(
    team_mode: str, player_count: int
) -> None:
    combinations = product(
        ("standard", "short10", "short15"),
        ("classic", "beginner"),
        ("single", "match"),
    )
    for index, (stock_mode, setup_mode, scoring_mode) in enumerate(combinations):
        game = make_game(
            player_count,
            bots=True,
            stock_mode=stock_mode,
            setup_mode=setup_mode,
            scoring_mode=scoring_mode,
            winning_score=MIN_MATCH_TARGET,
            team_mode=team_mode,
        )
        assert game.prestart_validate() == []

        random.seed(100 + player_count + index)
        game.on_start()
        game.flush_menus()
        for _ in range(5_000):
            if game.status == "finished":
                break
            game.on_tick()
            game.flush_menus()

        assert game.status == "finished", (
            team_mode,
            stock_mode,
            setup_mode,
            scoring_mode,
        )
        assert count_cards(game) == cards.DECK_SIZE


def test_public_status_never_exposes_an_opponents_hand() -> None:
    game = make_game(2, start=True)
    first, second = game.players[:2]
    first.hand = [card(2900, 12)]
    second.hand = [card(2901, 4), card(2902, 5)]
    set_turn(game, first)

    public_items = (
        game._building_status_lines("en")
        + game._stock_status_lines("en")
        + game._discard_status_lines(first, "en")
    )
    assert all("hand" not in item.text.lower() for item in public_items)
    first_items = game.get_user(first).menus["turn_menu"]["items"]
    second_items = game.get_user(second).menus["turn_menu"]["items"]
    assert any(item.id == "end_turn_2900" for item in first_items)
    assert all(item.id != "end_turn_2900" for item in second_items)
    assert [item.text for item in second_items[:2]] == ["Hand: 4", "Hand: 5"]


def test_game_result_records_team_competitors_and_winner_ids() -> None:
    game = make_game(4, start=True, team_mode="2v2", scoring_mode=SCORING_MATCH)
    winning_team = game._team_manager.teams[0]
    losing_team = game._team_manager.teams[1]
    winning_team.total_score = 500
    losing_team.total_score = 275
    game.winner_team_index = winning_team.index

    result = game.build_game_result()

    assert result.custom_data["winner_ids"] == [
        game.get_player_by_name(name).id for name in winning_team.members
    ]
    competitors = result.custom_data["rating_competitors"]
    assert len(competitors) == 2
    assert competitors[0] == {
        "player_ids": [
            game.get_player_by_name(name).id for name in winning_team.members
        ],
        "rank": 0,
    }
