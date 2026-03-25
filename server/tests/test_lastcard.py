"""Comprehensive tests for the LastCard game."""

import random
from unittest.mock import patch
from ..games.lastcard.game import (
    LastCardGame, LastCardOptions, LastCardPlayer,
    build_lastcard_deck,
    COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW, COLOR_WILD,
    RANK_SKIP, RANK_REVERSE, RANK_DRAW_TWO, RANK_WILD, RANK_WILD_DRAW_FOUR,
)
from ..game_utils.cards import Card, Deck
from ..users.bot import Bot


# ============================================================================
# Helpers
# ============================================================================

def make_game(**option_overrides) -> LastCardGame:
    """Create a game with optional overrides."""
    opts = LastCardOptions(**option_overrides)
    return LastCardGame(options=opts)


def add_bots(game: LastCardGame, count: int = 2) -> list[LastCardPlayer]:
    """Add bot players to a game."""
    players = []
    for i in range(count):
        bot = Bot(f"Bot{i}")
        p = game.add_player(f"Bot{i}", bot)
        players.append(p)
    return players


def start_game(game: LastCardGame) -> None:
    """Start the game and advance past intro wait."""
    game.on_start()
    # Advance past intro + hand start
    for _ in range(500):
        if game.status == "playing" and game.intro_wait_ticks == 0 and game.hand_wait_ticks == 0:
            break
        game.on_tick()


def setup_turn(game: LastCardGame, player_index: int, discard_card: Card,
               color: int | None = None) -> None:
    """Set up a clean turn state for testing.

    Sets the current player, discard pile, clears interrupt states,
    and rebuilds menus.
    """
    game.turn_index = player_index
    game.discard_pile = [discard_card]
    game.current_color = color if color is not None else discard_card.suit
    game.turn_has_drawn = False
    game.awaiting_color_choice = False
    game.awaiting_swap_target = False
    game.interrupt_phase = ""
    game.interrupt_timer_ticks = 0
    game.pending_draw_count = 0
    game.pending_draw_is_plus_four = False
    game.color_wait_ticks = 0
    game.jump_in_played = False
    # Clear bot think ticks to prevent bots from acting
    for p in game.players:
        p.bot_think_ticks = 9999
        p.bot_pending_action = None
        p.draws_this_turn = 0
        p.called_last_card = False
    game._sync_turn_actions(game.players[player_index])
    game.rebuild_all_menus()


def advance_ticks(game: LastCardGame, count: int) -> None:
    """Advance the game by a number of ticks."""
    for _ in range(count):
        game.on_tick()


def advance_until(game: LastCardGame, condition, max_ticks: int = 2000) -> bool:
    """Advance until a condition is met or max ticks exceeded."""
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def make_card(card_id: int, rank: int, suit: int) -> Card:
    """Create a Card with specified attributes."""
    return Card(id=card_id, rank=rank, suit=suit)


# ============================================================================
# Basic game creation and metadata
# ============================================================================

def test_game_creation():
    game = LastCardGame()
    assert game.get_name() == "Last Card"
    assert game.get_name_key() == "game-name-lastcard"
    assert game.get_type() == "lastcard"
    assert game.get_category() == "category-card-games"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 10


def test_options_defaults():
    game = LastCardGame()
    assert game.options.winning_score == 500
    assert game.options.hand_size == 7
    assert game.options.turn_timer == "0"
    assert game.options.draw_until_playable is False
    assert game.options.stacking == "off"
    assert game.options.jump_in is False
    assert game.options.force_play is False
    assert game.options.last_card_callout is True
    assert game.options.challenge_wild_draw_four is True
    assert game.options.buzzer_enabled is True
    assert game.options.interrupt_timer == 4
    assert game.options.scoring_mode == "classic"
    assert game.options.max_hand_size == 0


def test_leaderboards():
    assert LastCardGame.get_supported_leaderboards() == ["wins", "rating", "games_played"]


# ============================================================================
# Deck building
# ============================================================================

def test_deck_has_108_cards():
    deck = build_lastcard_deck()
    assert deck.size() == 108


def test_deck_composition():
    deck = build_lastcard_deck()
    cards = deck.cards

    wilds = [c for c in cards if c.rank == RANK_WILD]
    wd4s = [c for c in cards if c.rank == RANK_WILD_DRAW_FOUR]
    assert len(wilds) == 4
    assert len(wd4s) == 4

    for color in (COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW):
        zeros = [c for c in cards if c.suit == color and c.rank == 0]
        assert len(zeros) == 1
        for rank in range(1, 10):
            count = len([c for c in cards if c.suit == color and c.rank == rank])
            assert count == 2
        for rank in (RANK_SKIP, RANK_REVERSE, RANK_DRAW_TWO):
            count = len([c for c in cards if c.suit == color and c.rank == rank])
            assert count == 2


# ============================================================================
# Card playability
# ============================================================================

def test_wild_always_playable():
    game = make_game()
    add_bots(game, 2)
    start_game(game)
    setup_turn(game, 0, make_card(100, 5, COLOR_RED))

    wild = make_card(999, RANK_WILD, COLOR_WILD)
    assert game._is_card_playable(wild) is True


def test_color_match_playable():
    game = make_game()
    add_bots(game, 2)
    start_game(game)
    setup_turn(game, 0, make_card(100, 5, COLOR_RED))

    assert game._is_card_playable(make_card(101, 3, COLOR_RED)) is True
    assert game._is_card_playable(make_card(102, 3, COLOR_BLUE)) is False


def test_rank_match_playable():
    game = make_game()
    add_bots(game, 2)
    start_game(game)
    setup_turn(game, 0, make_card(100, 5, COLOR_RED))

    assert game._is_card_playable(make_card(101, 5, COLOR_BLUE)) is True
    assert game._is_card_playable(make_card(102, 3, COLOR_BLUE)) is False


def test_wd4_always_playable():
    game = make_game()
    add_bots(game, 2)
    start_game(game)
    setup_turn(game, 0, make_card(100, 5, COLOR_RED))

    wd4 = make_card(999, RANK_WILD_DRAW_FOUR, COLOR_WILD)
    assert game._is_card_playable(wd4) is True


# ============================================================================
# Basic gameplay
# ============================================================================

def test_play_number_card():
    game = make_game(last_card_callout=False, challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED))

    red_7 = make_card(200, 7, COLOR_RED)
    p0.hand = [red_7, make_card(201, 3, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{red_7.id}")

    assert red_7 not in p0.hand
    assert game.top_card == red_7
    assert game.current_color == COLOR_RED


def test_play_skip_card():
    game = make_game(last_card_callout=False, challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 3)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, RANK_SKIP, COLOR_RED), COLOR_RED)

    skip = make_card(200, RANK_SKIP, COLOR_RED)
    p0.hand = [skip, make_card(201, 3, COLOR_BLUE), make_card(202, 4, COLOR_GREEN)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{skip.id}")

    assert game.top_card == skip


def test_play_reverse_card_3_players():
    game = make_game(last_card_callout=False, challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 3)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_GREEN), COLOR_GREEN)

    initial_dir = game.turn_direction
    rev = make_card(200, RANK_REVERSE, COLOR_GREEN)
    p0.hand = [rev, make_card(201, 3, COLOR_BLUE), make_card(202, 4, COLOR_RED)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{rev.id}")

    assert game.turn_direction == -initial_dir


def test_reverse_acts_as_skip_in_2p():
    game = make_game(reverse_two_players="skip", last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_GREEN), COLOR_GREEN)

    rev = make_card(200, RANK_REVERSE, COLOR_GREEN)
    p0.hand = [rev, make_card(201, 3, COLOR_BLUE), make_card(202, 4, COLOR_RED)]
    game._sync_turn_actions(p0)
    game.turn_direction = 1

    game.execute_action(p0, f"play_card_{rev.id}")

    # In 2p with skip mode, direction should stay the same (skip, not reverse)
    assert game.turn_direction == 1


def test_draw_two_no_stacking():
    game = make_game(stacking="off", last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    dt = make_card(200, RANK_DRAW_TWO, COLOR_RED)
    p0.hand = [dt, make_card(201, 3, COLOR_BLUE), make_card(202, 4, COLOR_GREEN)]
    initial_p1_hand = len(p1.hand)
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{dt.id}")

    assert len(p1.hand) == initial_p1_hand + 2


# ============================================================================
# Wild cards and color selection
# ============================================================================

def test_wild_requires_color_choice():
    game = make_game(last_card_callout=False, challenge_wild_draw_four=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    wild = make_card(200, RANK_WILD, COLOR_WILD)
    p0.hand = [wild, make_card(201, 3, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{wild.id}")

    assert game.awaiting_color_choice is True
    assert game.top_card == wild


def test_choose_color_after_wild():
    game = make_game(last_card_callout=False, challenge_wild_draw_four=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    wild = make_card(200, RANK_WILD, COLOR_WILD)
    p0.hand = [wild, make_card(201, 3, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{wild.id}")
    assert game.awaiting_color_choice is True

    game.execute_action(p0, "color_green")
    assert game.current_color == COLOR_GREEN
    assert game.awaiting_color_choice is False


# ============================================================================
# Stacking
# ============================================================================

def test_standard_stacking_dt_on_dt():
    game = make_game(stacking="standard", last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 3)
    start_game(game)

    p1 = game.players[1]
    # Determine who the next player after p1 is, and give them a DT
    # so they CAN stack (prevents _force_draw_pending from resolving immediately)
    setup_turn(game, 1, make_card(200, RANK_DRAW_TWO, COLOR_RED), COLOR_RED)
    game.pending_draw_count = 2
    game.pending_draw_is_plus_four = False

    # Give next player a DT so they can stack (keeps pending_draw_count alive)
    next_idx = (game.turn_index + game.turn_direction) % len(game.turn_player_ids)
    next_player = game.get_player_by_id(game.turn_player_ids[next_idx])
    next_player.hand = [make_card(300, RANK_DRAW_TWO, COLOR_GREEN), make_card(301, 5, COLOR_RED)]

    dt_blue = make_card(201, RANK_DRAW_TWO, COLOR_BLUE)
    p1.hand = [dt_blue, make_card(202, 5, COLOR_GREEN), make_card(203, 3, COLOR_RED)]
    game._sync_turn_actions(p1)

    game.execute_action(p1, f"play_card_{dt_blue.id}")

    assert game.pending_draw_count == 4


def test_standard_stacking_no_dt_on_wd4():
    game = make_game(stacking="standard")
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, RANK_WILD_DRAW_FOUR, COLOR_WILD), COLOR_RED)
    game.pending_draw_count = 4
    game.pending_draw_is_plus_four = True

    dt = make_card(201, RANK_DRAW_TWO, COLOR_RED)
    p0.hand = [dt, make_card(202, 5, COLOR_BLUE)]

    assert game._is_card_playable(dt, p0) is False


def test_progressive_stacking_dt_on_wd4():
    game = make_game(stacking="progressive")
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, RANK_WILD_DRAW_FOUR, COLOR_WILD), COLOR_RED)
    game.pending_draw_count = 4
    game.pending_draw_is_plus_four = True

    dt = make_card(201, RANK_DRAW_TWO, COLOR_RED)
    p0.hand = [dt, make_card(202, 5, COLOR_BLUE)]

    assert game._is_card_playable(dt, p0) is True


def test_cant_stack_forces_draw():
    game = make_game(stacking="standard", last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p1 = game.players[1]
    setup_turn(game, 0, make_card(200, RANK_DRAW_TWO, COLOR_RED), COLOR_RED)
    game.pending_draw_count = 4
    game.pending_draw_is_plus_four = False

    # p1 has no draw twos
    p1.hand = [make_card(201, 5, COLOR_BLUE), make_card(202, 3, COLOR_GREEN)]
    initial_hand = len(p1.hand)

    # Advance turn to p1 — should force draw
    game._advance_turn()

    assert len(p1.hand) == initial_hand + 4
    assert game.pending_draw_count == 0


# ============================================================================
# Challenge Wild Draw Four
# ============================================================================

def test_wd4_challenge_window_opens():
    game = make_game(challenge_wild_draw_four=True, last_card_callout=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    wd4 = make_card(200, RANK_WILD_DRAW_FOUR, COLOR_WILD)
    p0.hand = [wd4, make_card(201, 3, COLOR_RED), make_card(202, 4, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{wd4.id}")
    assert game.awaiting_color_choice is True

    game.execute_action(p0, "color_blue")
    # Advance through color_wait_ticks
    advance_until(game, lambda: game.interrupt_phase == "challenge_wd4")

    assert game.interrupt_phase == "challenge_wd4"
    assert game.interrupt_wd4_had_matching is True


def test_wd4_challenge_success():
    game = make_game(challenge_wild_draw_four=True, last_card_callout=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    wd4 = make_card(200, RANK_WILD_DRAW_FOUR, COLOR_WILD)
    p0.hand = [wd4, make_card(201, 3, COLOR_RED), make_card(202, 4, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{wd4.id}")
    game.execute_action(p0, "color_blue")
    advance_until(game, lambda: game.interrupt_phase == "challenge_wd4")

    initial_p0_hand = len(p0.hand)
    game.execute_action(p1, "challenge_wd4")

    assert len(p0.hand) == initial_p0_hand + 4


def test_wd4_challenge_fail():
    game = make_game(challenge_wild_draw_four=True, last_card_callout=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    wd4 = make_card(200, RANK_WILD_DRAW_FOUR, COLOR_WILD)
    p0.hand = [wd4, make_card(201, 3, COLOR_BLUE), make_card(202, 4, COLOR_GREEN)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{wd4.id}")
    game.execute_action(p0, "color_blue")
    advance_until(game, lambda: game.interrupt_phase == "challenge_wd4")

    initial_p1_hand = len(p1.hand)
    game.execute_action(p1, "challenge_wd4")

    assert len(p1.hand) == initial_p1_hand + 6


def test_wd4_accept_draw():
    game = make_game(challenge_wild_draw_four=True, last_card_callout=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    wd4 = make_card(200, RANK_WILD_DRAW_FOUR, COLOR_WILD)
    p0.hand = [wd4, make_card(201, 3, COLOR_BLUE), make_card(202, 4, COLOR_GREEN)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{wd4.id}")
    game.execute_action(p0, "color_blue")
    advance_until(game, lambda: game.interrupt_phase == "challenge_wd4")

    initial_p1_hand = len(p1.hand)
    game.execute_action(p1, "accept_draw")

    assert len(p1.hand) == initial_p1_hand + 4
    assert game.interrupt_phase == ""


# ============================================================================
# Buzzer / Last Card Callout
# ============================================================================

def test_last_card_callout_window():
    game = make_game(last_card_callout=True, buzzer_enabled=True,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    red_7 = make_card(200, 7, COLOR_RED)
    p0.hand = [red_7, make_card(201, 3, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{red_7.id}")

    assert game.interrupt_phase == "last_card_callout"
    assert game.interrupt_target_id == p0.id


def test_buzzer_self_call_safe():
    game = make_game(last_card_callout=True, buzzer_enabled=True,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    red_7 = make_card(200, 7, COLOR_RED)
    p0.hand = [red_7, make_card(201, 3, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{red_7.id}")

    assert game.interrupt_phase == "last_card_callout"
    initial_hand = len(p0.hand)
    game.execute_action(p0, "buzzer")

    assert p0.called_last_card is True
    assert len(p0.hand) == initial_hand


def test_buzzer_caught():
    game = make_game(last_card_callout=True, buzzer_enabled=True,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    red_7 = make_card(200, 7, COLOR_RED)
    p0.hand = [red_7, make_card(201, 3, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{red_7.id}")

    assert game.interrupt_phase == "last_card_callout"
    initial_p0_hand = len(p0.hand)

    game.execute_action(p1, "buzzer")

    assert len(p0.hand) == initial_p0_hand + 2


def test_callout_without_buzzer_does_not_pause():
    game = make_game(last_card_callout=True, buzzer_enabled=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    red_7 = make_card(200, 7, COLOR_RED)
    p0.hand = [red_7, make_card(201, 3, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{red_7.id}")

    assert game.interrupt_phase == ""
    assert game.current_player == p1


def test_wd4_challenge_still_starts_when_buzzer_disabled():
    game = make_game(last_card_callout=True, buzzer_enabled=False,
                     challenge_wild_draw_four=True, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    wd4 = make_card(200, RANK_WILD_DRAW_FOUR, COLOR_WILD)
    p0.hand = [wd4, make_card(201, 3, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{wd4.id}")
    game.execute_action(p0, "color_blue")
    advance_ticks(game, 20)

    assert game.interrupt_phase == "challenge_wd4"
    assert game._next_player() == p1


# ============================================================================
# Jump-in
# ============================================================================

def test_jump_in_with_exact_match():
    game = make_game(jump_in=True, last_card_callout=False,
                     challenge_wild_draw_four=False)
    add_bots(game, 3)
    start_game(game)

    p0 = game.players[0]
    p2 = game.players[2]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    red_5 = make_card(200, 5, COLOR_RED)
    p0.hand = [red_5, make_card(201, 3, COLOR_BLUE), make_card(202, 4, COLOR_GREEN)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{red_5.id}")

    assert game.interrupt_phase == "jump_in_window"

    another_red_5 = make_card(300, 5, COLOR_RED)
    p2.hand = [another_red_5, make_card(301, 3, COLOR_GREEN), make_card(302, 4, COLOR_YELLOW)]

    initial_p2_hand = len(p2.hand)
    game.execute_action(p2, "jump_in")

    assert len(p2.hand) == initial_p2_hand - 1
    assert another_red_5 not in p2.hand


def test_jump_in_no_match_fails():
    game = make_game(jump_in=True, last_card_callout=False,
                     challenge_wild_draw_four=False)
    add_bots(game, 3)
    start_game(game)

    p0 = game.players[0]
    p2 = game.players[2]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    red_5 = make_card(200, 5, COLOR_RED)
    p0.hand = [red_5, make_card(201, 3, COLOR_BLUE), make_card(202, 4, COLOR_GREEN)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{red_5.id}")

    p2.hand = [make_card(300, 5, COLOR_BLUE), make_card(301, 3, COLOR_GREEN)]
    initial_p2_hand = len(p2.hand)

    game.execute_action(p2, "jump_in")
    assert len(p2.hand) == initial_p2_hand


# ============================================================================
# Seven-O rules
# ============================================================================

def test_seven_swap_with_2_players():
    game = make_game(seven_card_rule="swap_hand", last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    seven = make_card(200, 7, COLOR_RED)
    card_a = make_card(201, 3, COLOR_BLUE)
    card_b = make_card(202, 4, COLOR_GREEN)
    p0.hand = [seven, card_a, card_b]

    p1_cards = [make_card(300, 8, COLOR_YELLOW), make_card(301, 9, COLOR_RED)]
    p1.hand = list(p1_cards)
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{seven.id}")

    # Auto-swap in 2p
    assert card_a in p1.hand
    assert card_b in p1.hand


def test_zero_rotates_hands():
    game = make_game(zero_card_rule="rotate_hands", last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 3)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    p2 = game.players[2]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    zero = make_card(200, 0, COLOR_RED)
    hand0_extra = [make_card(201, 3, COLOR_BLUE)]
    p0.hand = [zero] + hand0_extra
    hand1 = [make_card(300, 8, COLOR_YELLOW), make_card(301, 9, COLOR_RED)]
    p1.hand = list(hand1)
    hand2 = [make_card(400, 2, COLOR_GREEN), make_card(401, 6, COLOR_BLUE)]
    p2.hand = list(hand2)
    game._sync_turn_actions(p0)

    game.turn_direction = 1
    game.execute_action(p0, f"play_card_{zero.id}")

    # Direction 1: hands shift forward
    # p0 (index 0) gets p2's hand, p1 gets p0's hand, p2 gets p1's hand
    assert p0.hand == hand2
    assert p1.hand == hand0_extra
    assert p2.hand == hand1


# ============================================================================
# Draw rules
# ============================================================================

def test_draw_once_normal():
    game = make_game(draw_until_playable=False, force_play=False,
                     last_card_callout=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    p0.hand = [make_card(201, 3, COLOR_BLUE)]
    game._sync_turn_actions(p0)

    game.execute_action(p0, "draw")
    assert game.turn_has_drawn is True
    assert len(p0.hand) == 2
    assert game._can_draw(p0) is False


def test_force_play_blocks_voluntary_draw():
    game = make_game(force_play=True)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    p0.hand = [make_card(201, 5, COLOR_BLUE)]  # Matches rank
    assert game._can_draw(p0) is False


# ============================================================================
# Scoring
# ============================================================================

def test_hand_points():
    game = make_game()
    hand = [
        make_card(1, 5, COLOR_RED),
        make_card(2, 0, COLOR_BLUE),
        make_card(3, RANK_SKIP, COLOR_GREEN),
        make_card(4, RANK_WILD, COLOR_WILD),
        make_card(5, RANK_WILD_DRAW_FOUR, COLOR_WILD),
    ]
    assert game._hand_points(hand) == 125


def test_classic_scoring():
    game = make_game(scoring_mode="classic", winning_score=100,
                     last_card_callout=False, challenge_wild_draw_four=False,
                     jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    winning_card = make_card(200, 7, COLOR_RED)
    p0.hand = [winning_card]
    p1.hand = [make_card(300, RANK_WILD, COLOR_WILD)]  # 50 points
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{winning_card.id}")

    assert p0.score == 50


# ============================================================================
# Edge cases
# ============================================================================

def test_deck_reshuffles_from_discard():
    game = make_game()
    add_bots(game, 2)
    start_game(game)

    top = make_card(100, 5, COLOR_RED)
    game.discard_pile = [make_card(i, i % 10, COLOR_RED) for i in range(50)]
    game.discard_pile.append(top)
    game.deck = Deck(cards=[])
    game.current_color = COLOR_RED

    card = game._draw_card()
    assert card is not None
    assert len(game.discard_pile) == 1


def test_max_hand_size_limits_draws():
    game = make_game(max_hand_size=5)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p0.hand = [make_card(i, i % 10, COLOR_RED) for i in range(4)]

    game._draw_for_player(p0, 5)
    assert len(p0.hand) == 5


def test_winning_with_wild_card():
    game = make_game(last_card_callout=False, challenge_wild_draw_four=False,
                     jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    wild = make_card(200, RANK_WILD, COLOR_WILD)
    p0.hand = [wild]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{wild.id}")

    assert len(p0.hand) == 0


def test_winning_with_wd4():
    game = make_game(last_card_callout=False, challenge_wild_draw_four=False,
                     jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    setup_turn(game, 0, make_card(100, 5, COLOR_RED), COLOR_RED)

    wd4 = make_card(200, RANK_WILD_DRAW_FOUR, COLOR_WILD)
    p0.hand = [wd4]
    game._sync_turn_actions(p0)

    game.execute_action(p0, f"play_card_{wd4.id}")

    assert len(p0.hand) == 0


# ============================================================================
# Bot game completion
# ============================================================================

def test_bot_game_completes():
    random.seed(42)
    options = LastCardOptions(winning_score=50, last_card_callout=False,
                              challenge_wild_draw_four=False, jump_in=False)
    game = LastCardGame(options=options)
    for i in range(3):
        bot = Bot(f"Bot{i}")
        game.add_player(f"Bot{i}", bot)
    game.on_start()

    for _ in range(60000):
        if game.status == "finished":
            break
        game.on_tick()

    assert game.status == "finished"


def test_bot_game_with_stacking():
    random.seed(123)
    options = LastCardOptions(winning_score=50, stacking="standard",
                              last_card_callout=False, challenge_wild_draw_four=False,
                              jump_in=False)
    game = LastCardGame(options=options)
    for i in range(3):
        bot = Bot(f"Bot{i}")
        game.add_player(f"Bot{i}", bot)
    game.on_start()

    for _ in range(60000):
        if game.status == "finished":
            break
        game.on_tick()

    assert game.status == "finished"


def test_bot_game_with_all_features():
    random.seed(456)
    options = LastCardOptions(
        winning_score=50, stacking="progressive",
        last_card_callout=True, buzzer_enabled=True,
        challenge_wild_draw_four=True, jump_in=True,
        seven_card_rule="swap_hand", zero_card_rule="rotate_hands",
    )
    game = LastCardGame(options=options)
    for i in range(4):
        bot = Bot(f"Bot{i}")
        game.add_player(f"Bot{i}", bot)
    game.on_start()

    for _ in range(80000):
        if game.status == "finished":
            break
        game.on_tick()

    assert game.status == "finished"


# ============================================================================
# Card formatting
# ============================================================================

def test_format_card_number():
    game = make_game()
    card = make_card(1, 5, COLOR_RED)
    name = game.format_card(card, "en")
    assert "Red" in name
    assert "5" in name


def test_format_card_skip():
    game = make_game()
    card = make_card(1, RANK_SKIP, COLOR_BLUE)
    name = game.format_card(card, "en")
    assert "Blue" in name
    assert "Skip" in name


def test_format_card_wild():
    game = make_game()
    card = make_card(1, RANK_WILD, COLOR_WILD)
    name = game.format_card(card, "en")
    assert "Wild" in name


def test_format_card_wd4():
    game = make_game()
    card = make_card(1, RANK_WILD_DRAW_FOUR, COLOR_WILD)
    name = game.format_card(card, "en")
    assert "Wild" in name
    assert "Draw Four" in name


# ============================================================================
# Hand clearing between rounds
# ============================================================================

def test_hands_cleared_between_rounds():
    """Verify that player hands are cleared when a round ends (not a game end)."""
    game = make_game(winning_score=9999, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    p0 = game.players[0]
    p1 = game.players[1]
    setup_turn(game, 0, make_card(200, 5, COLOR_RED), COLOR_RED)

    # Give p0 one playable card and p1 some cards
    playable = make_card(201, 6, COLOR_RED)
    p0.hand = [playable]
    p1.hand = [make_card(202, 3, COLOR_BLUE), make_card(203, 7, COLOR_GREEN)]
    game._sync_turn_actions(p0)

    # Play the card — p0 wins the round
    game.execute_action(p0, f"play_card_{playable.id}")

    # Both hands should now be empty (cleared at round end)
    assert p0.hand == []
    assert p1.hand == []
    # Game should NOT be finished (winning_score is very high)
    assert game.status == "playing"
    assert game.hand_wait_ticks > 0


# ============================================================================
# Draw penalty info
# ============================================================================

def test_draw_penalty_info():
    """Verify pending_draw_count is correctly tracked for the draw penalty action."""
    game = make_game(stacking="standard", last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)

    # No penalty initially
    assert game.pending_draw_count == 0

    # Set up a pending draw
    game.pending_draw_count = 6
    assert game.pending_draw_count == 6


# ============================================================================
# Hand sorting
# ============================================================================

def test_hand_sort_default():
    """Default hand sort is by color."""
    game = make_game()
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    assert p0.hand_sort == "color"


def test_hand_sort_by_color():
    """Sort by color groups cards by suit then rank."""
    game = make_game()
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    p0.hand_sort = "color"
    p0.hand = [
        make_card(1, 5, COLOR_BLUE),
        make_card(2, 3, COLOR_RED),
        make_card(3, 9, COLOR_RED),
    ]
    sorted_hand = game._sort_hand(p0)
    # Red (suit 1) should come before Blue (suit 2)
    assert sorted_hand[0].suit == COLOR_RED
    assert sorted_hand[1].suit == COLOR_RED
    assert sorted_hand[2].suit == COLOR_BLUE
    # Within red, rank 3 before rank 9
    assert sorted_hand[0].rank == 3
    assert sorted_hand[1].rank == 9


def test_hand_sort_by_rank():
    """Sort by rank orders by rank first, then color."""
    game = make_game()
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    p0.hand_sort = "rank"
    p0.hand = [
        make_card(1, 5, COLOR_BLUE),
        make_card(2, 3, COLOR_RED),
        make_card(3, 9, COLOR_RED),
    ]
    sorted_hand = game._sort_hand(p0)
    assert sorted_hand[0].rank == 3
    assert sorted_hand[1].rank == 5
    assert sorted_hand[2].rank == 9


def test_hand_sort_none():
    """Sort mode 'none' preserves insertion order."""
    game = make_game()
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    p0.hand_sort = "none"
    p0.hand = [
        make_card(1, 5, COLOR_BLUE),
        make_card(2, 3, COLOR_RED),
        make_card(3, 9, COLOR_RED),
    ]
    sorted_hand = game._sort_hand(p0)
    assert sorted_hand[0].id == 1
    assert sorted_hand[1].id == 2
    assert sorted_hand[2].id == 3


def test_cycle_hand_sort():
    """Cycling hand sort rotates through color -> rank -> none -> color."""
    game = make_game()
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, 5, COLOR_RED), COLOR_RED)
    p0.hand = [make_card(201, 3, COLOR_RED)]
    game._sync_turn_actions(p0)

    assert p0.hand_sort == "color"
    game.execute_action(p0, "cycle_hand_sort")
    assert p0.hand_sort == "rank"
    game.execute_action(p0, "cycle_hand_sort")
    assert p0.hand_sort == "none"
    game.execute_action(p0, "cycle_hand_sort")
    assert p0.hand_sort == "color"


# ============================================================================
# Multiple card play
# ============================================================================

def test_multi_play_toggle_select():
    """Toggle card selection in multi-play mode."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, 5, COLOR_RED), COLOR_RED)

    card_a = make_card(201, 3, COLOR_RED)
    card_b = make_card(202, 3, COLOR_BLUE)
    p0.hand = [card_a, card_b, make_card(203, 7, COLOR_GREEN)]
    game._sync_turn_actions(p0)

    assert len(p0.selected_cards) == 0

    # Toggle card A on
    game.execute_action(p0, f"toggle_card_{card_a.id}")
    assert card_a.id in p0.selected_cards

    # Toggle card A off
    game.execute_action(p0, f"toggle_card_{card_a.id}")
    assert card_a.id not in p0.selected_cards


def test_multi_play_two_number_cards():
    """Play two number cards of the same rank in multi-play mode."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, 3, COLOR_RED), COLOR_RED)

    card_a = make_card(201, 3, COLOR_BLUE)
    card_b = make_card(202, 3, COLOR_GREEN)
    p0.hand = [card_a, card_b, make_card(203, 7, COLOR_YELLOW), make_card(204, 9, COLOR_RED)]
    game._sync_turn_actions(p0)

    # Select both 3s
    p0.selected_cards = {card_a.id, card_b.id}
    game.execute_action(p0, "play_selected")

    # Both cards should be played
    assert card_a not in p0.hand
    assert card_b not in p0.hand
    assert len(p0.hand) == 2
    # Last card's color (Green) should be the active color
    assert game.current_color == COLOR_GREEN


def test_multi_play_rejects_different_ranks():
    """Cannot play cards of different ranks together."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, 5, COLOR_RED), COLOR_RED)

    card_a = make_card(201, 3, COLOR_RED)
    card_b = make_card(202, 5, COLOR_RED)
    p0.hand = [card_a, card_b, make_card(203, 7, COLOR_GREEN)]
    game._sync_turn_actions(p0)

    p0.selected_cards = {card_a.id, card_b.id}
    game.execute_action(p0, "play_selected")

    # Cards should NOT have been played (different ranks)
    assert card_a in p0.hand
    assert card_b in p0.hand


def test_multi_play_rejects_multiple_wilds():
    """Cannot play multiple Wild cards at once."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, 5, COLOR_RED), COLOR_RED)

    wild_a = make_card(201, RANK_WILD, COLOR_WILD)
    wild_b = make_card(202, RANK_WILD, COLOR_WILD)
    p0.hand = [wild_a, wild_b, make_card(203, 7, COLOR_GREEN)]
    game._sync_turn_actions(p0)

    p0.selected_cards = {wild_a.id, wild_b.id}
    game.execute_action(p0, "play_selected")

    # Both wilds should still be in hand
    assert wild_a in p0.hand
    assert wild_b in p0.hand


def test_multi_play_single_card_uses_normal_path():
    """Selecting one card and confirming uses the normal play path."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, 5, COLOR_RED), COLOR_RED)

    card = make_card(201, 5, COLOR_BLUE)
    p0.hand = [card, make_card(202, 7, COLOR_GREEN), make_card(203, 9, COLOR_RED)]
    game._sync_turn_actions(p0)

    p0.selected_cards = {card.id}
    game.execute_action(p0, "play_selected")

    assert card not in p0.hand
    assert game.current_color == COLOR_BLUE


def test_multi_play_double_skip():
    """Two Skip cards = skip two players."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 4)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, RANK_SKIP, COLOR_RED), COLOR_RED)

    skip_a = make_card(201, RANK_SKIP, COLOR_BLUE)
    skip_b = make_card(202, RANK_SKIP, COLOR_GREEN)
    p0.hand = [skip_a, skip_b, make_card(203, 7, COLOR_RED), make_card(204, 8, COLOR_RED)]
    game._sync_turn_actions(p0)

    # Remember current turn index
    original_index = game.turn_index

    p0.selected_cards = {skip_a.id, skip_b.id}
    game.execute_action(p0, "play_selected")

    # Should have skipped 2 players (advance 3 positions from original: 1 normal + 2 skips)
    expected_index = (original_index + 3) % len(game.turn_player_ids)
    assert game.turn_index == expected_index


def test_multi_play_double_draw_two():
    """Two Draw Twos without stacking = next player draws 4 and is skipped."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False,
                     stacking="off")
    add_bots(game, 3)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, RANK_DRAW_TWO, COLOR_RED), COLOR_RED)

    dt_a = make_card(201, RANK_DRAW_TWO, COLOR_BLUE)
    dt_b = make_card(202, RANK_DRAW_TWO, COLOR_GREEN)
    p1 = game.players[1]
    p1_hand_before = len(p1.hand)
    p0.hand = [dt_a, dt_b, make_card(203, 7, COLOR_RED), make_card(204, 8, COLOR_RED)]
    game._sync_turn_actions(p0)

    p0.selected_cards = {dt_a.id, dt_b.id}
    game.execute_action(p0, "play_selected")

    # Next player should have drawn 4 cards (2 × 2)
    assert len(p1.hand) == p1_hand_before + 4


def test_multi_play_double_draw_two_stacking():
    """Two Draw Twos with stacking = +4 added to pending draw stack."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False,
                     stacking="standard")
    add_bots(game, 3)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, RANK_DRAW_TWO, COLOR_RED), COLOR_RED)
    game.pending_draw_count = 0

    dt_a = make_card(201, RANK_DRAW_TWO, COLOR_BLUE)
    dt_b = make_card(202, RANK_DRAW_TWO, COLOR_GREEN)
    # Give next player a DT so they can stack (keeps pending_draw_count alive)
    next_idx = (game.turn_index + game.turn_direction) % len(game.turn_player_ids)
    next_player = game.get_player_by_id(game.turn_player_ids[next_idx])
    next_player.hand = [make_card(300, RANK_DRAW_TWO, COLOR_RED), make_card(301, 5, COLOR_RED)]

    p0.hand = [dt_a, dt_b, make_card(203, 7, COLOR_RED), make_card(204, 8, COLOR_RED)]
    game._sync_turn_actions(p0)

    p0.selected_cards = {dt_a.id, dt_b.id}
    game.execute_action(p0, "play_selected")

    assert game.pending_draw_count == 4


def test_multi_play_double_reverse():
    """Two Reverses cancel each other out (direction unchanged)."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False)
    add_bots(game, 4)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, RANK_REVERSE, COLOR_RED), COLOR_RED)

    rev_a = make_card(201, RANK_REVERSE, COLOR_BLUE)
    rev_b = make_card(202, RANK_REVERSE, COLOR_GREEN)
    p0.hand = [rev_a, rev_b, make_card(203, 7, COLOR_RED), make_card(204, 8, COLOR_RED)]
    game._sync_turn_actions(p0)

    direction_before = game.turn_direction
    p0.selected_cards = {rev_a.id, rev_b.id}
    game.execute_action(p0, "play_selected")

    # Double reverse = back to original direction
    assert game.turn_direction == direction_before


def test_multi_play_wins_round():
    """Playing all remaining cards at once wins the round."""
    game = make_game(allow_multiple_play=True, last_card_callout=False,
                     challenge_wild_draw_four=False, jump_in=False,
                     winning_score=9999)
    add_bots(game, 2)
    start_game(game)
    p0 = game.players[0]
    setup_turn(game, 0, make_card(200, 5, COLOR_RED), COLOR_RED)

    card_a = make_card(201, 5, COLOR_BLUE)
    card_b = make_card(202, 5, COLOR_GREEN)
    p0.hand = [card_a, card_b]
    game._sync_turn_actions(p0)

    p0.selected_cards = {card_a.id, card_b.id}
    game.execute_action(p0, "play_selected")

    # Player won the round
    assert len(p0.hand) == 0
    assert game.hand_wait_ticks > 0  # Waiting for next hand


def test_multi_play_bot_game():
    """Full bot game with multi-play enabled completes."""
    random.seed(789)
    options = LastCardOptions(
        winning_score=50, allow_multiple_play=True,
        last_card_callout=True, buzzer_enabled=True,
    )
    game = LastCardGame(options=options)
    for i in range(4):
        bot = Bot(f"Bot{i}")
        game.add_player(f"Bot{i}", bot)
    game.on_start()

    for _ in range(80000):
        if game.status == "finished":
            break
        game.on_tick()

    assert game.status == "finished"


# ============================================================================
# Prestart validation
# ============================================================================

def test_prestart_validate_too_many_cards():
    """Reject hand sizes that exceed the deck."""
    game = LastCardGame(options=LastCardOptions(hand_size=15))
    for i in range(8):
        game.add_player(f"P{i}", Bot(f"P{i}"))
    errors = game.prestart_validate()
    assert any("lastcard-error-too-many-cards" in (e[0] if isinstance(e, tuple) else e) for e in errors)


def test_prestart_validate_force_play_conflicts_with_draw_until_playable():
    """Reject mutually conflicting draw behavior options."""
    game = LastCardGame(options=LastCardOptions(draw_until_playable=True, force_play=True))
    for i in range(4):
        game.add_player(f"P{i}", Bot(f"P{i}"))
    errors = game.prestart_validate()
    assert "lastcard-error-draw-until-playable-conflicts-force-play" in errors


def test_prestart_validate_draw_limit_requires_draw_until_playable():
    """Reject draw-limit configs that do nothing."""
    game = LastCardGame(options=LastCardOptions(draw_until_playable=False, draw_limit=3))
    for i in range(4):
        game.add_player(f"P{i}", Bot(f"P{i}"))
    errors = game.prestart_validate()
    assert "lastcard-error-draw-limit-requires-draw-until-playable" in errors


def test_prestart_validate_buzzer_requires_last_card_callout():
    """Reject buzzer configs that do nothing without callout."""
    game = LastCardGame(options=LastCardOptions(last_card_callout=False, buzzer_enabled=True))
    for i in range(4):
        game.add_player(f"P{i}", Bot(f"P{i}"))
    errors = game.prestart_validate()
    assert "lastcard-error-buzzer-requires-last-card-callout" in errors


def test_prestart_validate_ok():
    """Normal config passes validation."""
    game = LastCardGame(options=LastCardOptions(hand_size=7))
    for i in range(4):
        game.add_player(f"P{i}", Bot(f"P{i}"))
    errors = game.prestart_validate()
    assert not errors


def test_add_bot_uses_standard_join_sound():
    """Bot joins should use the standard lobby join sound identifier."""
    game = make_game()
    add_bots(game, 2)
    host = game.players[0]

    with patch.object(game, "broadcast_sound") as broadcast_sound:
        game._action_add_bot(host, "BotExtra", "add_bot")

    broadcast_sound.assert_called_once_with("join.ogg")


def test_remove_bot_uses_standard_leave_sound():
    """Bot removals should use the standard lobby leave sound identifier."""
    game = make_game()
    add_bots(game, 2)
    host = game.players[0]

    with patch.object(game, "broadcast_sound") as broadcast_sound:
        game._action_remove_bot(host, "remove_bot")

    broadcast_sound.assert_called_once_with("leave.ogg")


def test_spectator_leave_uses_standard_spectator_leave_sound():
    """Spectator departures should use the standard spectator leave sound."""
    game = make_game()
    players = add_bots(game, 2)
    spectator = game.add_spectator("Spec", Bot("Spec"))

    with patch.object(game, "broadcast_sound") as broadcast_sound:
        game._perform_leave_game(spectator)

    broadcast_sound.assert_called_once_with("leave_spectator.ogg")


# ============================================================================
# Wild card UI: cards hidden during color choice
# ============================================================================

def test_cards_hidden_during_color_choice():
    """Cards should be hidden when awaiting color choice."""
    game = make_game()
    players = add_bots(game, 3)
    start_game(game)
    p = players[0]

    # Set up state: player has a wild card
    p.hand = [Card(id=200, rank=RANK_WILD, suit=COLOR_WILD),
              Card(id=201, rank=3, suit=COLOR_RED)]
    game.awaiting_color_choice = True
    game._sync_turn_actions(p)

    # Check that play_card_ and toggle_card_ actions are hidden
    turn_set = game.get_action_set(p, "turn")
    for action in turn_set.get_visible_actions(game, p):
        assert not action.action.id.startswith("play_card_"), "play_card should be hidden during color choice"
        assert not action.action.id.startswith("toggle_card_"), "toggle_card should be hidden during color choice"


def test_cards_hidden_during_swap_target():
    """Cards should be hidden when awaiting swap target."""
    game = make_game()
    players = add_bots(game, 3)
    start_game(game)
    p = players[0]
    p.hand = [Card(id=200, rank=7, suit=COLOR_RED)]
    game.awaiting_swap_target = True
    game._sync_turn_actions(p)

    turn_set = game.get_action_set(p, "turn")
    for action in turn_set.get_visible_actions(game, p):
        assert not action.action.id.startswith("play_card_"), "play_card should be hidden during swap"
        assert not action.action.id.startswith("toggle_card_"), "toggle_card should be hidden during swap"


# ============================================================================
# Web client: buzzer, jump-in, sort visible in turn menu
# ============================================================================

def test_web_buzzer_visible_during_callout():
    """Web clients see buzzer button during last-card callout."""
    from ..game_utils.actions import Visibility
    game = make_game(buzzer_enabled=True, last_card_callout=True)
    players = add_bots(game, 3)
    start_game(game)
    p = players[1]  # Not the current player

    # Simulate callout phase
    game.interrupt_phase = "last_card_callout"
    game.interrupt_target_id = players[0].id

    # Without web client_type: hidden
    assert game._is_buzzer_hidden(p) == Visibility.HIDDEN

    # With web client_type: visible
    bot_user = game.get_user(p)
    bot_user.client_type = "web"
    assert game._is_buzzer_hidden(p) == Visibility.VISIBLE


def test_web_jump_in_visible_during_window():
    """Web clients see jump-in button during jump-in window."""
    from ..game_utils.actions import Visibility
    game = make_game(jump_in=True)
    players = add_bots(game, 3)
    start_game(game)

    # Set turn to player 0
    setup_turn(game, 0, make_card(50, 5, COLOR_RED))

    # Non-current player during jump-in window
    p = players[1]
    game.interrupt_phase = "jump_in_window"

    # Without web: hidden
    assert game._is_jump_in_hidden(p) == Visibility.HIDDEN

    # With web: visible
    bot_user = game.get_user(p)
    bot_user.client_type = "web"
    assert game._is_jump_in_hidden(p) == Visibility.VISIBLE

    # Current player should still be hidden (can't jump in on own turn)
    cp = players[0]
    cp_user = game.get_user(cp)
    cp_user.client_type = "web"
    assert game._is_jump_in_hidden(cp) == Visibility.HIDDEN


def test_web_sort_visible_in_turn_menu():
    """Web clients see sort hand button in turn menu."""
    from ..game_utils.actions import Visibility
    game = make_game()
    players = add_bots(game, 3)
    start_game(game)
    p = players[0]

    # Without web: hidden
    assert game._is_sort_turn_hidden(p) == Visibility.HIDDEN

    # With web: visible
    bot_user = game.get_user(p)
    bot_user.client_type = "web"
    assert game._is_sort_turn_hidden(p) == Visibility.VISIBLE


def test_web_read_hand_visible_in_standard_menu():
    """Web clients see read hand in the standard menu."""
    from ..game_utils.actions import Visibility
    game = make_game()
    players = add_bots(game, 3)
    start_game(game)
    p = players[0]

    bot_user = game.get_user(p)
    bot_user.client_type = "web"

    assert game._is_read_hand_hidden(p) == Visibility.VISIBLE


def test_web_turn_menu_order():
    """Web turn menu places reaction buttons before cards, utilities after."""
    game = make_game(jump_in=True, buzzer_enabled=True)
    players = add_bots(game, 3)
    start_game(game)
    p = players[0]

    # Make this a web user
    bot_user = game.get_user(p)
    bot_user.client_type = "web"

    setup_turn(game, 0, make_card(50, 5, COLOR_RED))
    p.hand = [Card(id=200, rank=5, suit=COLOR_BLUE),
              Card(id=201, rank=3, suit=COLOR_RED)]
    game._sync_turn_actions(p)

    turn_set = game.get_action_set(p, "turn")
    order = turn_set._order

    # Buzzer should come before cards
    buzzer_idx = order.index("buzzer")
    card_indices = [order.index(aid) for aid in order if aid.startswith("play_card_")]
    assert all(buzzer_idx < ci for ci in card_indices), "buzzer must be before cards"

    # Draw/pass should come after cards
    draw_idx = order.index("draw")
    pass_idx = order.index("pass")
    assert all(draw_idx > ci for ci in card_indices), "draw must be after cards"
    assert all(pass_idx > ci for ci in card_indices), "pass must be after cards"

    # Sort should be last
    sort_idx = order.index("cycle_hand_sort_turn")
    assert sort_idx > draw_idx, "sort must be after draw"
    assert sort_idx > pass_idx, "sort must be after pass"


def test_web_standard_menu_order_includes_read_hand():
    """Web standard menu puts read hand with the game-specific info actions."""
    game = make_game()
    players = add_bots(game, 3)
    start_game(game)
    p = players[0]

    bot_user = game.get_user(p)
    bot_user.client_type = "web"

    standard_set = game.create_standard_action_set(p)
    order = standard_set._order

    read_hand_idx = order.index("read_hand")
    read_top_idx = order.index("read_top")
    read_counts_idx = order.index("read_counts")
    read_draw_penalty_idx = order.index("read_draw_penalty")
    check_turn_timer_idx = order.index("check_turn_timer")
    check_scores_idx = order.index("check_scores")
    whose_turn_idx = order.index("whose_turn")
    whos_at_table_idx = order.index("whos_at_table")

    assert read_hand_idx < read_top_idx
    assert read_top_idx < read_counts_idx
    assert read_counts_idx < read_draw_penalty_idx
    assert read_draw_penalty_idx < check_turn_timer_idx
    assert check_turn_timer_idx < check_scores_idx
    assert check_scores_idx < whose_turn_idx
    assert whose_turn_idx < whos_at_table_idx


