"""Tests for 21 (Survival Rules)."""

from pathlib import Path

from ..game_utils.cards import Card, Deck
from ..game_utils.options import IntOption
from ..games.twentyone.game import (
    MODIFIER_BREAK,
    MODIFIER_DRAW_2,
    MODIFIER_DRAW_SILENCE,
    MODIFIER_TARGET_24,
    TwentyOneGame,
    TwentyOneOptions,
)
from ..messages.localization import Localization
from ..users.bot import Bot
from ..users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(**option_overrides) -> tuple[TwentyOneGame, MockUser, MockUser]:
    game = TwentyOneGame(options=TwentyOneOptions(**option_overrides))
    game.setup_keybinds()
    alice_user = MockUser("Alice", uuid="p1")
    bob_user = MockUser("Bob", uuid="p2")
    game.add_player("Alice", alice_user)
    game.add_player("Bob", bob_user)
    game.host = "Alice"
    return game, alice_user, bob_user


def make_started_game(**option_overrides) -> tuple[TwentyOneGame, MockUser, MockUser]:
    game, alice_user, bob_user = make_game(**option_overrides)
    alice, bob = game.players
    alice.hp = 10
    bob.hp = 10
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([alice, bob])
    return game, alice_user, bob_user


def speech_texts(user: MockUser) -> list[str]:
    return [message.data["text"] for message in user.messages if message.type == "speak"]


def test_twentyone_documented_options_are_host_configurable() -> None:
    metas = TwentyOneOptions().get_option_metas()

    expected_ranges = {
        "starting_health": (10, 1, 100),
        "base_bet": (1, 0, 50),
        "starting_modifiers_per_round": (1, 0, 10),
        "draw_modifier_chance_percent": (35, 0, 100),
        "deck_count": (1, 1, 10),
    }

    assert set(expected_ranges).issubset(metas)
    for option_name, (default, min_val, max_val) in expected_ranges.items():
        meta = metas[option_name]
        assert isinstance(meta, IntOption)
        assert meta.default == default
        assert meta.min_val == min_val
        assert meta.max_val == max_val


def test_prestart_validation_rejects_no_damage_source_setup() -> None:
    game, _, _ = make_game(
        base_bet=0,
        starting_modifiers_per_round=0,
        draw_modifier_chance_percent=0,
    )

    assert "twentyone-error-no-damage-source" in game.prestart_validate()


def test_break_effect_uses_listener_locale_for_removed_effect_name() -> None:
    game, alice_user, bob_user = make_started_game()
    bob_user._locale = "vi"
    alice, bob = game.players
    bob.table_modifiers = [MODIFIER_TARGET_24]
    alice_user.messages.clear()
    bob_user.messages.clear()

    game._resolve_modifier(alice, MODIFIER_BREAK)

    bob_speech = " ".join(speech_texts(bob_user))
    assert "mục tiêu 24" in bob_speech
    assert "target 24" not in bob_speech


def test_hit_uses_first_and_third_person_draw_messages() -> None:
    game, alice_user, bob_user = make_started_game(draw_modifier_chance_percent=0)
    alice = game.players[0]
    game.deck = Deck(cards=[Card(id=1, rank=5, suit=0)])
    alice_user.messages.clear()
    bob_user.messages.clear()

    game._action_hit(alice, "hit")

    assert any("You draw" in text for text in speech_texts(alice_user))
    assert any("Alice draws" in text for text in speech_texts(bob_user))


def test_stand_keeps_total_private_in_third_person_messages() -> None:
    game, alice_user, bob_user = make_started_game()
    alice = game.players[0]
    alice.hand = [Card(id=1, rank=7, suit=0), Card(id=2, rank=11, suit=0)]
    alice_user.messages.clear()
    bob_user.messages.clear()

    game._action_stand(alice, "stand")

    assert any("You stand at 18." in text for text in speech_texts(alice_user))
    bob_speech = " ".join(speech_texts(bob_user))
    assert "Alice stands." in bob_speech
    assert "18" not in bob_speech

    game, alice_user, bob_user = make_started_game()
    bob_user._locale = "vi"
    alice = game.players[0]
    alice.hand = [Card(id=1, rank=7, suit=0), Card(id=2, rank=11, suit=0)]
    alice_user.messages.clear()
    bob_user.messages.clear()

    game._action_stand(alice, "stand")

    assert any("You stand at 18." in text for text in speech_texts(alice_user))
    bob_speech = " ".join(speech_texts(bob_user))
    assert "Alice dừng." in bob_speech
    assert "18" not in bob_speech


def test_hit_blocked_by_draw_lock_speaks_effect_reason() -> None:
    game, alice_user, bob_user = make_started_game(draw_modifier_chance_percent=0)
    alice, bob = game.players
    bob.table_modifiers = [MODIFIER_DRAW_SILENCE]
    game.deck = Deck(cards=[Card(id=1, rank=5, suit=0)])
    turn_set = game.create_turn_action_set(alice)
    hit_action = turn_set.get_action("hit")
    assert hit_action is not None

    resolved = turn_set.resolve_action(game, alice, hit_action)

    assert resolved.enabled

    alice_user.messages.clear()
    bob_user.messages.clear()
    game.execute_action(alice, "hit")

    assert alice.hand == []
    alice_speech = " ".join(speech_texts(alice_user))
    bob_speech = " ".join(speech_texts(bob_user))
    assert "You cannot draw because no draw for you!" in alice_speech
    assert "blocking number-card draws" in alice_speech
    assert "Alice cannot draw because no draw for you!" in bob_speech


def test_hit_is_disabled_when_deck_is_empty() -> None:
    game, _, _ = make_started_game()
    alice = game.players[0]
    game.deck = Deck(cards=[])
    turn_set = game.create_turn_action_set(alice)
    hit_action = turn_set.get_action("hit")
    assert hit_action is not None

    resolved = turn_set.resolve_action(game, alice, hit_action)

    assert not resolved.enabled
    assert resolved.disabled_reason == "twentyone-deck-empty-must-stand"


def test_bot_stands_when_deck_is_empty() -> None:
    game = TwentyOneGame()
    game.setup_keybinds()
    bot_player = game.add_player("Bot", Bot("Bot", uuid="p1"))
    human = game.add_player("Human", MockUser("Human", uuid="p2"))
    bot_player.hp = 10
    human.hp = 10
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.deck = Deck(cards=[])
    game.set_turn_players([bot_player, human])

    assert game.bot_think(bot_player) == "stand"


def test_change_card_menu_shows_blocked_cards_and_reports_reason() -> None:
    game, alice_user, _ = make_started_game()
    alice, bob = game.players
    alice.modifiers = [MODIFIER_DRAW_2]
    bob.table_modifiers = [MODIFIER_DRAW_SILENCE]
    game.deck = Deck(cards=[Card(id=2, rank=2, suit=0)])
    alice_user.messages.clear()

    options = game._options_for_play_modifier(alice)

    assert len(options) == 1
    assert "unavailable:" in options[0]
    assert game._is_play_modifier_enabled(alice) is None

    game._action_play_modifier(alice, options[0], "play_modifier")

    assert alice.modifiers == [MODIFIER_DRAW_2]
    speech = " ".join(speech_texts(alice_user))
    assert "You cannot play draw 2" in speech
    assert "draw-blocking effect" in speech


def test_change_card_menu_preserves_all_hand_indexes_with_unplayable_cards() -> None:
    game, alice_user, _ = make_started_game()
    alice, bob = game.players
    alice.modifiers = [MODIFIER_BREAK, MODIFIER_TARGET_24]
    bob.table_modifiers = []
    game.deck = Deck(cards=[Card(id=2, rank=2, suit=0)])
    alice_user.messages.clear()

    options = game._options_for_play_modifier(alice)

    assert len(options) == 2
    assert options[0].startswith("1:")
    assert "unavailable:" in options[0]
    assert options[1].startswith("2:")

    game._action_play_modifier(alice, options[0], "play_modifier")

    assert alice.modifiers == [MODIFIER_BREAK, MODIFIER_TARGET_24]
    assert any("no active table effects" in text for text in speech_texts(alice_user))


# ---------------------------------------------------------------------------
# Multiplayer (3+ players)
# ---------------------------------------------------------------------------


def make_started_game_n(count: int) -> tuple[TwentyOneGame, list]:
    """Start a game with `count` players, all at 10 HP, in the turns phase."""
    game = TwentyOneGame()
    game.setup_keybinds()
    for i in range(count):
        game.add_player(f"P{i}", MockUser(f"P{i}", uuid=f"p{i}"))
    game.host = "P0"
    for player in game.players:
        player.hp = 10
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players(list(game.players))
    return game, list(game.players)


def test_supports_up_to_four_players() -> None:
    assert TwentyOneGame.get_max_players() == 4


def test_round_outcome_unique_best_non_bust_wins() -> None:
    game, players = make_started_game_n(3)
    # Totals 19, 20, 22 with target 21: 20 is the unique closest non-bust.
    winners = game._resolve_round_outcome(players, [19, 20, 22], 21)
    assert winners == [players[1].id]


def test_round_outcome_tie_for_best_is_a_draw() -> None:
    game, players = make_started_game_n(3)
    # Two players tie at 21 (target); a tie for best means no winner.
    winners = game._resolve_round_outcome(players, [21, 21, 18], 21)
    assert winners == []


def test_round_outcome_all_bust_closest_wins() -> None:
    game, players = make_started_game_n(3)
    # Everyone over 21: 22 is closest to the target.
    winners = game._resolve_round_outcome(players, [25, 22, 30], 21)
    assert winners == [players[1].id]


def test_settle_round_damages_all_non_winners() -> None:
    game, players = make_started_game_n(3)
    p0, p1, p2 = players
    # Give each a deterministic hand: p1 wins at 20, others lose.
    p0.hand = [Card(id=1, rank=9, suit=0), Card(id=2, rank=10, suit=0)]  # 19
    p1.hand = [Card(id=3, rank=10, suit=0), Card(id=4, rank=10, suit=0)]  # 20
    p2.hand = [Card(id=5, rank=10, suit=0), Card(id=6, rank=10, suit=0), Card(id=7, rank=5, suit=0)]  # 25 bust
    for p in players:
        p.stand_pending = True

    game._settle_round()
    assert game.pending_round_winner_ids == (p1.id,)

    # Resolve the pending round and check only non-winners lost HP.
    game.round_resolution_wait_ticks = 1
    game._resolve_pending_round()
    assert p1.hp == 10  # winner unharmed
    assert p0.hp < 10  # non-winners took damage
    assert p2.hp < 10


def test_targeted_raise_only_affects_chosen_opponent() -> None:
    from ..games.twentyone.game import MODIFIER_RAISE_2

    game, players = make_started_game_n(3)
    p0, p1, p2 = players
    base = game.options.base_bet

    # p0 plays raise_2 targeting p2 specifically.
    game._place_table_effect(p0, MODIFIER_RAISE_2, target=p2)

    # Only p2's incoming bet/damage should rise; p1 stays at base.
    assert game._current_bet(p2) == base + 2
    assert game._current_bet(p1) == base


def test_targeted_draw_lock_only_locks_chosen_opponent() -> None:
    game, players = make_started_game_n(3)
    p0, p1, p2 = players

    game._place_table_effect(p0, MODIFIER_DRAW_SILENCE, target=p2)

    assert game._draws_locked_for(p2) is True
    assert game._draws_locked_for(p1) is False


def test_single_target_card_prompts_then_hits_chosen_opponent() -> None:
    from ..games.twentyone.game import MODIFIER_RAISE_2

    game, players = make_started_game_n(3)
    p0, p1, p2 = players
    base = game.options.base_bet
    p0.modifiers = [MODIFIER_RAISE_2]
    game.turn_index = 0  # p0 to act

    # Play the card: with two opponents this should stash and prompt, not resolve.
    options = game._options_for_play_modifier(p0)
    game._action_play_modifier(p0, options[0], "play_modifier")
    assert p0.id in game.pending_target_modifier
    assert MODIFIER_RAISE_2 in p0.modifiers  # not spent yet

    # Choose p2 as the target.
    game._action_select_target(p0, p2.id, "select_target")
    assert p0.id not in game.pending_target_modifier
    # raise_2 lands on p2 only (raise grants a reward card, so just check the bet).
    assert game._current_bet(p2) == base + 2
    assert game._current_bet(p1) == base


def test_single_target_card_skips_prompt_with_one_opponent() -> None:
    from ..games.twentyone.game import MODIFIER_RAISE_2

    game, _, _ = make_started_game()
    alice, bob = game.players
    alice.modifiers = [MODIFIER_RAISE_2]
    base = game.options.base_bet

    options = game._options_for_play_modifier(alice)
    game._action_play_modifier(alice, options[0], "play_modifier")

    # Only one opponent: resolves immediately, no pending target prompt.
    assert alice.id not in game.pending_target_modifier
    assert MODIFIER_RAISE_2 not in alice.modifiers  # spent
    assert game._current_bet(bob) == base + 2


def test_select_target_cancel_keeps_card() -> None:
    from ..games.twentyone.game import MODIFIER_RAISE_2

    game, players = make_started_game_n(3)
    p0 = players[0]
    p0.modifiers = [MODIFIER_RAISE_2]
    game.turn_index = 0

    options = game._options_for_play_modifier(p0)
    game._action_play_modifier(p0, options[0], "play_modifier")
    game._action_select_target(p0, "_cancel", "select_target")

    assert p0.id not in game.pending_target_modifier
    assert p0.modifiers == [MODIFIER_RAISE_2]  # card not spent on cancel


def test_table_effect_lists_stay_in_sync_on_expiry() -> None:
    from ..games.twentyone.game import MODIFIER_GUARD, TABLE_EFFECT_LIMIT

    game, players = make_started_game_n(2)
    p0 = players[0]
    # Overflow the table beyond the limit; both parallel lists must stay aligned.
    for _ in range(TABLE_EFFECT_LIMIT + 2):
        game._place_table_effect(p0, MODIFIER_GUARD)

    assert len(p0.table_modifiers) == TABLE_EFFECT_LIMIT
    assert len(p0.table_modifier_targets) == len(p0.table_modifiers)
