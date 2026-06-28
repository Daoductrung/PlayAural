"""Tests for 21 (Survival Rules)."""

from pathlib import Path
import re

from ..game_utils.cards import Card, Deck
from ..game_utils.options import IntOption
from ..games.twentyone.game import (
    MODIFIER_ALL_IN_SILENCE,
    MODIFIER_BREAK,
    MODIFIER_DRAW_2,
    MODIFIER_DRAW_SILENCE,
    MODIFIER_MIND_TAX,
    MODIFIER_RAISE_2,
    MODIFIER_SHARED_CACHE,
    MODIFIER_SWAP_DRAW,
    MODIFIER_TARGET_24,
    SOUND_TURN,
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


def menu_item_ids(user: MockUser, menu_id: str) -> list[str | None]:
    menu = user.menus.get(menu_id)
    if not menu:
        return []
    return [getattr(item, "id", None) for item in menu["items"]]


def ftl_messages(text: str) -> dict[str, set[str]]:
    messages: dict[str, set[str]] = {}
    current_key: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+)\s*=", line)
        if match:
            if current_key is not None:
                messages[current_key] = set(re.findall(r"\$([A-Za-z0-9_-]+)", "\n".join(current_lines)))
            current_key = match.group(1)
            current_lines = [line]
        elif current_key is not None:
            current_lines.append(line)
    if current_key is not None:
        messages[current_key] = set(re.findall(r"\$([A-Za-z0-9_-]+)", "\n".join(current_lines)))
    return messages


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


def test_turn_sound_only_plays_for_current_player_and_respects_preference() -> None:
    game, alice_user, bob_user = make_started_game()
    alice, _bob = game.players
    game.turn_index = 0
    alice_user.preferences.play_turn_sound = True
    bob_user.preferences.play_turn_sound = True
    alice_user.messages.clear()
    bob_user.messages.clear()

    game.announce_turn(turn_sound=SOUND_TURN)

    assert SOUND_TURN in alice_user.get_sounds_played()
    assert SOUND_TURN not in bob_user.get_sounds_played()

    alice_user.preferences.play_turn_sound = False
    alice_user.messages.clear()
    bob_user.messages.clear()

    game.announce_turn(turn_sound=SOUND_TURN)

    assert SOUND_TURN not in alice_user.get_sounds_played()
    assert SOUND_TURN not in bob_user.get_sounds_played()
    assert any("It is your turn." in text for text in speech_texts(alice_user))
    assert any(f"It is {alice.name}'s turn." in text for text in speech_texts(bob_user))


def test_turn_handoff_does_not_play_turn_sound_for_bystanders() -> None:
    game, players = make_started_game_n(3)
    p0, p1, p2 = players
    user0 = game.get_user(p0)
    user1 = game.get_user(p1)
    user2 = game.get_user(p2)
    assert user0 is not None
    assert user1 is not None
    assert user2 is not None
    p0.hand = [Card(id=1, rank=9, suit=0), Card(id=2, rank=8, suit=0)]
    game.turn_index = 0
    for user in (user0, user1, user2):
        user.preferences.play_turn_sound = True
        user.messages.clear()

    game._action_stand(p0, "stand")

    assert SOUND_TURN not in user0.get_sounds_played()
    assert SOUND_TURN in user1.get_sounds_played()
    assert SOUND_TURN not in user2.get_sounds_played()
    assert not any(
        sound == "turn.ogg" or sound.endswith("/turn.ogg") or "begin turn" in sound
        for sound in user2.get_sounds_played()
    )


def test_bot_hits_when_later_multiplayer_opponent_is_a_standing_threat() -> None:
    game, players = make_started_game_n(3)
    bot, weak_opponent, strong_opponent = players
    bot.hand = [Card(id=1, rank=10, suit=0), Card(id=2, rank=9, suit=0)]
    weak_opponent.hand = [Card(id=3, rank=1, suit=0), Card(id=4, rank=2, suit=0)]
    strong_opponent.hand = [
        Card(id=5, rank=1, suit=0),
        Card(id=6, rank=9, suit=0),
        Card(id=7, rank=5, suit=0),
    ]
    weak_opponent.stand_pending = True
    strong_opponent.stand_pending = True
    game.deck = Deck(
        cards=[
            Card(id=8, rank=1, suit=0),
            Card(id=9, rank=2, suit=0),
            Card(id=10, rank=11, suit=0),
        ]
    )

    assert game._bot_choose_hit_or_stand(bot) == "hit"


def test_bot_stands_when_leading_all_multiplayer_opponents() -> None:
    game, players = make_started_game_n(4)
    bot, p1, p2, p3 = players
    bot.hand = [Card(id=1, rank=10, suit=0), Card(id=2, rank=10, suit=0)]
    p1.hand = [Card(id=3, rank=1, suit=0), Card(id=4, rank=4, suit=0)]
    p2.hand = [Card(id=5, rank=1, suit=0), Card(id=6, rank=5, suit=0)]
    p3.hand = [Card(id=7, rank=1, suit=0), Card(id=8, rank=6, suit=0)]
    game.deck = Deck(cards=[Card(id=9, rank=1, suit=0), Card(id=10, rank=2, suit=0)])

    assert game._bot_choose_hit_or_stand(bot) == "stand"


def test_bot_targets_strongest_valid_opponent_for_harmful_change_card() -> None:
    game, players = make_started_game_n(3)
    bot, weak_opponent, strong_opponent = players
    bot.modifiers = [MODIFIER_DRAW_SILENCE]
    weak_opponent.hand = [Card(id=1, rank=1, suit=0), Card(id=2, rank=2, suit=0)]
    weak_opponent.hp = 4
    strong_opponent.hand = [
        Card(id=3, rank=1, suit=0),
        Card(id=4, rank=9, suit=0),
        Card(id=5, rank=5, suit=0),
    ]
    strong_opponent.hp = 12
    game.pending_target_modifier[bot.id] = 0

    assert (
        game._bot_select_target(bot, [weak_opponent.id, strong_opponent.id])
        == strong_opponent.id
    )


def test_bot_targets_weakest_valid_opponent_for_shared_cache() -> None:
    game, players = make_started_game_n(3)
    bot, weak_opponent, strong_opponent = players
    bot.modifiers = [MODIFIER_SHARED_CACHE]
    weak_opponent.hand = [Card(id=1, rank=1, suit=0), Card(id=2, rank=2, suit=0)]
    weak_opponent.hp = 3
    strong_opponent.hand = [
        Card(id=3, rank=1, suit=0),
        Card(id=4, rank=9, suit=0),
        Card(id=5, rank=5, suit=0),
    ]
    strong_opponent.hp = 12
    game.pending_target_modifier[bot.id] = 0

    assert (
        game._bot_select_target(bot, [weak_opponent.id, strong_opponent.id])
        == weak_opponent.id
    )


def test_bot_values_swap_when_own_last_card_caused_a_bust() -> None:
    game, _, _ = make_started_game()
    bot, opponent = game.players
    bot.hand = [
        Card(id=1, rank=10, suit=0),
        Card(id=2, rank=4, suit=0),
        Card(id=3, rank=10, suit=0),
    ]
    bot.last_drawn_card_id = 3
    opponent.hand = [Card(id=4, rank=5, suit=0), Card(id=5, rank=2, suit=0)]
    opponent.last_drawn_card_id = 5
    bot.modifiers = [MODIFIER_SWAP_DRAW]

    assert game._bot_choose_modifier_to_play(bot) == MODIFIER_SWAP_DRAW


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


def test_all_in_silence_targets_one_opponent_and_keeps_owner_risk() -> None:
    game, players = make_started_game_n(3)
    p0, p1, p2 = players
    base = game.options.base_bet

    game._place_table_effect(p0, MODIFIER_ALL_IN_SILENCE, target=p2)

    assert game._draws_locked_for(p2) is True
    assert game._draws_locked_for(p1) is False
    assert game._current_bet(p0) == base + 100
    assert game._current_bet(p2) == base + 100
    assert game._current_bet(p1) == base


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


def test_target_selection_menu_focuses_first_target_after_second_card() -> None:
    game, players = make_started_game_n(3)
    p0, p1, p2 = players
    user0 = game.get_user(p0)
    assert user0 is not None
    p0.modifiers = [MODIFIER_TARGET_24, MODIFIER_RAISE_2]
    game.turn_index = 0

    options = game._options_for_play_modifier(p0)
    game._action_play_modifier(p0, options[1], "play_modifier")

    assert user0.menus["action_input_menu"]["selection_id"] == p1.id
    assert menu_item_ids(user0, "action_input_menu")[:2] == [p1.id, p2.id]


def test_target_selection_cancel_clears_pending_target_prompt() -> None:
    game, players = make_started_game_n(3)
    p0 = players[0]
    p0.modifiers = [MODIFIER_RAISE_2]
    game.turn_index = 0

    options = game._options_for_play_modifier(p0)
    game._action_play_modifier(p0, options[0], "play_modifier")
    assert p0.id in game.pending_target_modifier

    game.handle_event(
        p0,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "_cancel",
        },
    )

    assert p0.id not in game.pending_target_modifier
    visible_ids = [resolved.action.id for resolved in game.get_all_visible_actions(p0)]
    assert "select_target" not in visible_ids
    assert p0.modifiers == [MODIFIER_RAISE_2]


def test_target_options_filter_to_legal_opponents() -> None:
    from ..games.twentyone.game import MODIFIER_RAISE_2

    game, players = make_started_game_n(3)
    p0, p1, p2 = players
    p0.modifiers = [MODIFIER_BREAK]
    p2.table_modifiers = [MODIFIER_RAISE_2]
    p2.table_modifier_targets = [None]
    game.turn_index = 0

    options = game._options_for_play_modifier(p0)
    game._action_play_modifier(p0, options[0], "play_modifier")

    assert game._target_options(p0) == [p2.id]
    game._action_select_target(p0, p2.id, "select_target")
    assert p2.table_modifiers == []
    assert p1.table_modifiers == []


def test_invalid_selected_target_does_not_spend_card() -> None:
    game, players = make_started_game_n(3)
    p0, p1, _p2 = players
    p0.modifiers = [MODIFIER_BREAK]
    game.pending_target_modifier[p0.id] = 0

    game._action_select_target(p0, p1.id, "select_target")

    assert p0.modifiers == [MODIFIER_BREAK]
    assert p0.id not in game.pending_target_modifier


def test_shared_cache_rewards_chosen_opponent_only() -> None:
    game, players = make_started_game_n(3)
    p0, p1, p2 = players
    p0.modifiers = [MODIFIER_SHARED_CACHE]
    p1.modifiers = []
    p2.modifiers = []
    game.turn_index = 0

    options = game._options_for_play_modifier(p0)
    game._action_play_modifier(p0, options[0], "play_modifier")
    game._action_select_target(p0, p2.id, "select_target")

    assert len(p0.modifiers) == 1
    assert p1.modifiers == []
    assert len(p2.modifiers) == 1


def test_mind_tax_only_hits_chosen_target_at_round_end() -> None:
    game, players = make_started_game_n(3)
    p0, p1, p2 = players
    p1.modifiers = [MODIFIER_DRAW_2, MODIFIER_DRAW_2]
    p2.modifiers = [MODIFIER_DRAW_2, MODIFIER_DRAW_2, MODIFIER_DRAW_2]
    game._place_table_effect(p0, MODIFIER_MIND_TAX, target=p2)

    game._apply_round_end_change_card_effects(players)

    assert len(p1.modifiers) == 2
    assert len(p2.modifiers) == 2


def test_targeted_effects_render_their_target_in_status_reads() -> None:
    from ..games.twentyone.game import MODIFIER_RAISE_2

    game, players = make_started_game_n(3)
    p0, _p1, p2 = players
    game._place_table_effect(p0, MODIFIER_RAISE_2, target=p2)

    rendered = game._render_table_effect_list("en", p0)

    assert "on P2" in rendered


def test_single_target_card_skips_prompt_with_one_opponent() -> None:
    from ..games.twentyone.game import MODIFIER_RAISE_2

    game, _, _ = make_started_game()
    alice, bob = game.players
    alice.modifiers = [MODIFIER_RAISE_2]
    base = game.options.base_bet

    options = game._options_for_play_modifier(alice)
    game._action_play_modifier(alice, options[0], "play_modifier")

    # Only one opponent: resolves immediately, no pending target prompt, and the
    # raise lands on the sole opponent. (raise_2 grants a random reward card, so
    # assert on the effect, not the exact remaining hand.)
    assert alice.id not in game.pending_target_modifier
    assert game._current_bet(bob) == base + 2


def test_target_named_in_announcement_with_multiple_opponents() -> None:
    from ..games.twentyone.game import MODIFIER_RAISE_2

    game, players = make_started_game_n(3)
    p0, _p1, p2 = players
    p0.modifiers = [MODIFIER_RAISE_2]
    game.turn_index = 0
    user2 = game.get_user(p2)
    user2.messages.clear()

    options = game._options_for_play_modifier(p0)
    game._action_play_modifier(p0, options[0], "play_modifier")
    game._action_select_target(p0, p2.id, "select_target")

    # A bystander hears who the card was aimed at.
    speech = " ".join(speech_texts(user2))
    assert "on" in speech and p2.name in speech


def test_target_not_named_with_single_opponent() -> None:
    from ..games.twentyone.game import MODIFIER_RAISE_2

    game, alice_user, bob_user = make_started_game()
    alice, bob = game.players
    alice.modifiers = [MODIFIER_RAISE_2]
    bob_user.messages.clear()

    options = game._options_for_play_modifier(alice)
    game._action_play_modifier(alice, options[0], "play_modifier")

    # Two-player game keeps the plain phrasing (no "on <name>").
    speech = " ".join(speech_texts(bob_user))
    assert "plays" in speech
    assert " on " not in speech


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


def test_core_actions_remain_visible_between_rounds_for_desktop_and_touch() -> None:
    game, players = make_started_game_n(3)
    p0 = players[0]
    user0 = game.get_user(p0)
    assert user0 is not None
    game.phase = "between_rounds"

    for client_type in ("python", "mobile"):
        user0.client_type = client_type
        game.refresh_menus(p0)
        game.flush_menus()

        assert menu_item_ids(user0, "turn_menu")[:3] == [
            "hit",
            "stand",
            "play_modifier",
        ]


def test_touch_play_change_card_with_empty_inventory_explains_state() -> None:
    game, players = make_started_game_n(2)
    p0 = players[0]
    user0 = game.get_user(p0)
    assert user0 is not None
    user0.client_type = "mobile"
    p0.modifiers = []
    game.turn_index = 0
    user0.messages.clear()

    game.handle_event(
        p0,
        {"type": "menu", "menu_id": "turn_menu", "selection_id": "play_modifier"},
    )

    assert any("do not have any Change Cards" in text for text in speech_texts(user0))


def test_touch_draw_between_rounds_explains_state() -> None:
    game, players = make_started_game_n(2)
    p0 = players[0]
    user0 = game.get_user(p0)
    assert user0 is not None
    user0.client_type = "mobile"
    game.phase = "between_rounds"
    user0.messages.clear()

    game.handle_event(
        p0,
        {"type": "menu", "menu_id": "turn_menu", "selection_id": "hit"},
    )

    assert any("round is resolving" in text for text in speech_texts(user0))


def test_touch_stand_when_eliminated_explains_state() -> None:
    game, players = make_started_game_n(3)
    p0 = players[0]
    user0 = game.get_user(p0)
    assert user0 is not None
    user0.client_type = "mobile"
    p0.hp = 0
    game.turn_index = 1
    user0.messages.clear()

    game.handle_event(
        p0,
        {"type": "menu", "menu_id": "turn_menu", "selection_id": "stand"},
    )

    assert any("eliminated from this match" in text for text in speech_texts(user0))


def test_table_effect_lists_stay_in_sync_on_expiry() -> None:
    from ..games.twentyone.game import MODIFIER_GUARD, TABLE_EFFECT_LIMIT

    game, players = make_started_game_n(2)
    p0 = players[0]
    # Overflow the table beyond the limit; both parallel lists must stay aligned.
    for _ in range(TABLE_EFFECT_LIMIT + 2):
        game._place_table_effect(p0, MODIFIER_GUARD)

    assert len(p0.table_modifiers) == TABLE_EFFECT_LIMIT
    assert len(p0.table_modifier_targets) == len(p0.table_modifiers)


def test_twentyone_locale_key_and_variable_parity() -> None:
    en_text = (_locales_dir / "en" / "twentyone.ftl").read_text(encoding="utf-8")
    vi_text = (_locales_dir / "vi" / "twentyone.ftl").read_text(encoding="utf-8")

    assert ftl_messages(en_text) == ftl_messages(vi_text)
