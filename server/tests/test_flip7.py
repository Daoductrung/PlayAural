"""Tests for the Flip 7 card game."""

from pathlib import Path
import json

from ..games.flip7.game import (
    ACTION_COPIES,
    CARD_DOUBLE,
    CARD_FLIP_THREE,
    CARD_FREEZE,
    CARD_MODIFIER,
    CARD_NUMBER,
    CARD_SECOND_CHANCE,
    CHOICE_FLIP_THREE,
    CHOICE_FREEZE,
    CHOICE_SECOND_CHANCE,
    CONTINUE_FLOW,
    FLIP_SEVEN_BONUS,
    FLIP_SEVEN_TARGET,
    MAX_NUMBER,
    MODIFIER_VALUES,
    OUTCOME_CHOICE,
    OUTCOME_OK,
    OUTCOME_PENDING,
    PHASE_MATCH_END,
    PHASE_PLAYING,
    PHASE_ROUND_END,
    STATUS_BUSTED,
    STATUS_PLAYING,
    STATUS_STAYED,
    TAG_FLOW,
    Flip7Card,
    Flip7Game,
    Flip7Options,
    Flip7PendingAction,
)
from ..games.flip7 import audio
from ..games.registry import GameRegistry
from ..game_utils.audio_duration import measure_audio_duration_ticks
from ..game_utils.sequence_runner_mixin import (
    SequenceBeat,
    SequenceOperation,
)
from ..game_utils.stats_helpers import RATING_COMPETITORS_KEY
from ..messages.localization import Localization
from ..ui.keybinds import KeybindState
from ..users.bot import Bot
from ..users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]


def _card(kind, value=0, uid=0):
    return Flip7Card(kind=kind, value=value, uid=uid)


def _make_game(
    player_count=2,
    *,
    start=True,
    bot_all=False,
    target_score=200,
    mobile_user=False,
    locales=None,
):
    game = Flip7Game(options=Flip7Options(target_score=target_score))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        locale = locales[index] if locales else "en"
        if bot_all:
            user = Bot(name, uuid=f"p{index + 1}", locale=locale)
        else:
            user = MockUser(name, uuid=f"p{index + 1}", locale=locale)
        if mobile_user:
            user.client_type = "mobile"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
        game.flush_menus()
    return game


def advance_until(game, condition, max_ticks: int = 4000) -> bool:
    for _ in range(max_ticks):
        game.on_tick()
        game.flush_menus()
        if condition():
            return True
    return condition()


def _deal_number_cards(game, values):
    """Deal one number card per active player in a deterministic deal order."""
    game.cancel_sequences_by_tag(TAG_FLOW)
    game.pending_choice = None
    game.drawn_card = None
    game.deck = []
    game.phase = PHASE_PLAYING
    game.round = 1
    game.dealer_index = 0
    players = game._active()
    count = len(players)
    ordered = [players[(1 + i) % count] for i in range(count)]
    values_by_player = dict(zip((p.id for p in players), values))
    game.deal_order = [p.id for p in ordered]
    for player in ordered:
        value = values_by_player[player.id]
        player.cards = [_card(CARD_NUMBER, value, uid=value)]
        player.cards_drawn += 1
        player.round_status = STATUS_PLAYING
    game._begin_turn_order()
    game.status = "playing"
    return game


def _resolve(game, player, card, *, forced=False, continuation=CONTINUE_FLOW):
    """Start and finish one reveal flow for a known card."""
    game._resolve_card(
        player,
        card,
        forced=forced,
        continuation=continuation,
        pending_owner=player.id if forced else None,
    )
    assert advance_until(game, lambda: game.drawn_card is None)


def _take_from_deck(game, kind, value=None):
    card = next(
        c for c in game.deck if c.kind == kind and (value is None or c.value == value)
    )
    game.deck.remove(card)
    return card


def _effect_payload(player, card, uid, outcome=OUTCOME_PENDING):
    return {
        "target_id": player.id,
        "kind": card.kind,
        "value": card.value,
        "uid": uid,
        "forced": True,
        "outcome": outcome,
        "pending_owner": player.id,
    }


def _locale_keys(path: Path) -> set[str]:
    return {
        line.split("=", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        and not line.lstrip().startswith("#")
        and "=" in line
        and not line[0].isspace()
    }


# ---------------------------------------------------------------------------
# Metadata / registration / options
# ---------------------------------------------------------------------------


def test_flip7_registration_metadata_and_leaderboards():
    assert GameRegistry.get("flip7") is Flip7Game
    game = Flip7Game()
    assert game.get_name() == "Flip 7"
    assert game.get_type() == "flip7"
    assert game.get_category() == "cards"
    assert (game.get_min_players(), game.get_max_players()) == (3, 10)
    assert game.get_supported_leaderboards() == [
        "wins",
        "total_score",
        "high_score",
        "rating",
        "games_played",
    ]


def test_flip7_options_defaults():
    assert Flip7Options().target_score == 200
    game = Flip7Game(options=Flip7Options(target_score=50))
    assert game.options.target_score == 50


def test_flip7_localization_and_documentation_are_present():
    expected = _locale_keys(ROOT / "server" / "locales" / "en" / "flip7.ftl")
    for locale in ("en", "es", "pt", "vi"):
        ftl = ROOT / "server" / "locales" / locale / "flip7.ftl"
        doc = (
            ROOT / "server" / "documentation" / "content" / locale / "games" / "flip7.md"
        )
        assert ftl.exists(), ftl
        assert doc.exists(), doc
        assert _locale_keys(ftl) == expected


# ---------------------------------------------------------------------------
# Deck
# ---------------------------------------------------------------------------


def test_flip7_deck_composition():
    deck = Flip7Game.build_deck()
    assert len(deck) == 94
    assert len({c.uid for c in deck}) == 94

    kinds = {kind: [c for c in deck if c.kind == kind] for kind in set(c.kind for c in deck)}
    numbers = kinds[CARD_NUMBER]
    assert len(numbers) == 1 + sum(range(1, MAX_NUMBER + 1))
    assert len(kinds[CARD_MODIFIER]) == len(MODIFIER_VALUES)
    assert len(kinds[CARD_DOUBLE]) == 1
    assert len(kinds[CARD_SECOND_CHANCE]) == ACTION_COPIES
    assert len(kinds[CARD_FREEZE]) == ACTION_COPIES
    assert len(kinds[CARD_FLIP_THREE]) == ACTION_COPIES

    # Each value v appears exactly v times: one zero, one ace, six sixes, etc.
    for value in range(1, MAX_NUMBER + 1):
        assert len([c for c in numbers if c.value == value]) == value
    assert [c.value for c in kinds[CARD_MODIFIER]] == list(MODIFIER_VALUES)


# ---------------------------------------------------------------------------
# Startup / play
# ---------------------------------------------------------------------------


def test_flip7_start_initializes_round_and_players():
    game = _make_game(player_count=3)
    assert game.status == "playing"
    assert game.phase == PHASE_PLAYING
    assert game.round == 1
    assert [p.total_score for p in game.players] == [0, 0, 0]
    assert [p.round_status for p in game.players] == [
        STATUS_PLAYING,
        STATUS_PLAYING,
        STATUS_PLAYING,
    ]
    assert game._total_cards_in_play() == 94
    assert game.options.target_score == 200


def test_flip7_initial_deal_gives_every_player_one_number_card():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    first, second = game.players
    # Dealer is Player1, so Player2 is dealt first and gets the top card (4).
    assert first.numbers == [3]
    assert second.numbers == [4]
    assert first.total_score == 0


def test_flip7_hit_draws_a_card_into_the_area():
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [3, 4])
    actor = game.current_player
    game.deck = [_card(CARD_NUMBER, 9, uid=100)]
    game.before_menu_build(actor)
    game.execute_action(actor, "hit")
    assert actor.cards_drawn == 2
    assert advance_until(
        game, lambda: game.drawn_card is None and 9 in actor.numbers
    )
    assert 9 in actor.numbers
    assert actor.round_status == STATUS_PLAYING


def test_flip7_hit_disabled_while_dealing():
    game = _make_game(player_count=2)
    for player in game.players:
        assert game._is_hit_enabled(player) == "flip7-error-wait-card"


def test_flip7_hit_disabled_for_waiting_player_after_deal():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    game.deck = [_card(CARD_NUMBER, 9, uid=100)]
    actor = game.current_player
    waiting = next(p for p in game.players if p is not actor)
    assert game._is_hit_enabled(actor) is None
    assert game._is_hit_enabled(waiting) == "action-not-your-turn"


def test_flip7_stay_disabled_without_cards():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    waiting = next(p for p in game.players if p is not game.current_player)
    waiting.cards = []
    game.turn_index = game.turn_player_ids.index(waiting.id)
    assert game._is_stay_enabled(waiting) == "flip7-error-no-cards-to-bank"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def test_flip7_round_points_double_before_modifiers():
    game = _make_game(player_count=2, start=False)
    player = game.players[0]
    player.cards = [
        _card(CARD_NUMBER, 3, uid=1),
        _card(CARD_NUMBER, 5, uid=2),
        _card(CARD_MODIFIER, 2, uid=3),
    ]
    assert game.round_points(player) == 10
    player.cards.append(_card(CARD_DOUBLE, uid=4))
    assert game.round_points(player) == 18
    player.cards.append(_card(CARD_MODIFIER, 10, uid=5))
    assert game.round_points(player) == 28


def test_flip7_repeated_number_busts_without_second_chance():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [7, 8])
    first = game.players[0]
    duplicate = _card(CARD_NUMBER, 7, uid=100)
    _resolve(game, first, duplicate)
    assert first.round_status == STATUS_BUSTED
    assert first.busts == 1
    assert first.numbers == [7]
    assert duplicate in game.discard


def test_flip7_second_chance_saves_against_repeated_number():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [7, 8])
    first = game.players[0]
    first.cards.append(_card(CARD_SECOND_CHANCE, uid=200))
    duplicate = _card(CARD_NUMBER, 7, uid=100)
    _resolve(game, first, duplicate)
    assert first.second_chance is False
    assert first.round_status == STATUS_PLAYING
    assert first.numbers == [7]


def test_flip7_seven_unique_numbers_scores_bonus_and_ends_round():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [1, 2])
    first = game.players[0]
    first.cards.extend(_card(CARD_NUMBER, v, uid=10 + v) for v in (2, 3, 4, 5, 6))
    _resolve(game, first, _card(CARD_NUMBER, 7, uid=99))
    assert FLIP_SEVEN_TARGET == 7
    assert advance_until(game, lambda: game.phase != PHASE_PLAYING)
    assert first.flip_sevens == 1
    assert first.total_score == sum(range(1, 8)) + FLIP_SEVEN_BONUS
    assert first.numbers == []
    assert game.phase in (PHASE_ROUND_END, PHASE_MATCH_END)


# ---------------------------------------------------------------------------
# Targeted choices
# ---------------------------------------------------------------------------


def test_flip7_freeze_card_opens_a_targeted_choice():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    actor = game.players[0]
    _resolve(game, actor, _card(CARD_FREEZE, uid=1))
    assert game.pending_choice is not None
    assert game.pending_choice.kind == CHOICE_FREEZE
    assert game.pending_choice.actor_id == actor.id
    assert len(game._choice_targets()) == 3


def test_flip7_choice_action_stops_a_chosen_player():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    actor = game.players[0]
    target = game.players[1]
    _resolve(game, actor, _card(CARD_FREEZE, uid=1))
    game.before_menu_build(actor)
    game.execute_action(actor, f"choose_freeze_{target.id}")
    assert target.round_status == STATUS_STAYED
    assert game.pending_choice is None
    assert target.total_score == 0


def test_flip7_freeze_alone_stops_the_last_playing_player():
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [3, 4])
    actor = game.players[0]
    game.players[1].round_status = STATUS_BUSTED
    _resolve(game, actor, _card(CARD_FREEZE, uid=1))
    assert actor.round_status == STATUS_STAYED
    assert game.pending_choice is None


def test_flip7_second_chance_sets_aside_when_not_held():
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [3, 4])
    actor = game.players[0]
    _resolve(game, actor, _card(CARD_SECOND_CHANCE, uid=1))
    assert actor.second_chance is True
    assert game.pending_choice is None


def test_flip7_held_second_chance_opens_choice_to_pass_it_on():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    actor = game.players[0]
    actor.cards.append(_card(CARD_SECOND_CHANCE, uid=50))
    _resolve(game, actor, _card(CARD_SECOND_CHANCE, uid=1))
    assert game.pending_choice.kind == CHOICE_SECOND_CHANCE
    assert game.pending_choice.actor_id == actor.id
    targets = game._choice_targets()
    assert actor not in targets
    assert len(targets) == 2


def test_flip7_given_second_chance_lands_on_a_target():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    actor = game.players[0]
    target = game.players[2]
    actor.cards.append(_card(CARD_SECOND_CHANCE, uid=50))
    _resolve(game, actor, _card(CARD_SECOND_CHANCE, uid=1))
    game.before_menu_build(actor)
    game.execute_action(actor, f"choose_second_chance_{target.id}")
    assert target.second_chance is True
    assert game.pending_choice is None


# ---------------------------------------------------------------------------
# Flip Three
# ---------------------------------------------------------------------------


def test_flip7_flip_three_forced_draws_apply_cards():
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [3, 4])
    target = game.players[1]
    game.deck = [_card(CARD_NUMBER, v, uid=10 + v) for v in (3, 5, 6)]
    game._start_flip_three(target)
    assert game.flip_state is not None
    assert advance_until(game, lambda: game.flip_state is None)
    assert sorted(c.value for c in target.cards) == [3, 4, 5, 6]
    assert target.round_status == STATUS_PLAYING


def test_flip7_forced_action_cards_defer_only_flip_three_and_freeze():
    game = _make_game(player_count=3)
    target = game.players[1]
    freeze = _card(CARD_FREEZE, uid=1)
    flip_three = _card(CARD_FLIP_THREE, uid=3)
    chance = _card(CARD_SECOND_CHANCE, uid=2)

    # Only Flip Three and Freeze wait for the three forced flips to finish.
    assert game._get_card_outcome(target, freeze, forced=True) == OUTCOME_PENDING
    assert game._get_card_outcome(target, flip_three, forced=True) == OUTCOME_PENDING
    # A Second Chance is never deferred, so it can still spend itself on a
    # duplicate later in the very same Flip Three.
    assert game._get_card_outcome(target, chance, forced=True) == OUTCOME_OK

    game.drawn_card = freeze
    game._apply_card_effect(_effect_payload(target, freeze, uid=1))
    game.drawn_card = chance
    game._apply_card_effect(_effect_payload(target, chance, uid=2, outcome=OUTCOME_OK))

    assert [p.kind for p in game.pending_actions] == [CARD_FREEZE]
    assert all(p.owner_id == target.id for p in game.pending_actions)
    assert chance in target.cards
    assert game.pending_choice is None


def test_flip7_forced_second_chance_saves_a_duplicate_in_the_same_flip_three():
    # Publisher rule: holding a 7, a Flip Three revealing Second Chance, 7, 8
    # sets the Second Chance aside, spends it on the duplicate 7, then reveals 8.
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [11, 7, 12])
    target = game.players[1]
    game.deck = [
        _card(CARD_NUMBER, 8, uid=3),
        _card(CARD_NUMBER, 7, uid=2),
        _card(CARD_SECOND_CHANCE, uid=1),
    ]
    game._start_flip_three(target)
    assert advance_until(game, lambda: game.flip_state is None)

    assert target.round_status == STATUS_PLAYING
    assert sorted(c.value for c in target.cards) == [7, 8]
    assert not any(c.kind == CARD_SECOND_CHANCE for c in target.cards)
    assert sorted(c.value for c in game.discard if c.kind == CARD_NUMBER) == [7]
    assert game.pending_actions == []


def test_flip7_forced_second_chance_opens_a_choice_when_already_held():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [11, 7, 12])
    target = game.players[1]
    target.cards.append(_card(CARD_SECOND_CHANCE, uid=90))
    game.deck = [
        _card(CARD_NUMBER, 4, uid=3),
        _card(CARD_NUMBER, 3, uid=2),
        _card(CARD_SECOND_CHANCE, uid=1),
    ]
    game._start_flip_three(target)
    assert advance_until(game, lambda: game.pending_choice is not None)

    assert game.pending_choice is not None
    assert game.pending_choice.kind == CHOICE_SECOND_CHANCE
    assert game.pending_choice.actor_id == target.id
    assert game.pending_choice.card is not None
    assert game.pending_choice.card.kind == CARD_SECOND_CHANCE

    recipient = game.players[2]
    game.before_menu_build(target)
    game.execute_action(target, f"choose_second_chance_{recipient.id}")

    assert advance_until(
        game, lambda: game.flip_state is None and game.drawn_card is None
    )
    assert recipient.second_chance is True
    assert sorted(target.numbers) == [3, 4, 7]


def test_flip7_forced_extra_second_chance_without_a_target_resumes_flip_three():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [11, 7, 12])
    target = game.players[1]
    for uid, player in enumerate(game.players, start=90):
        player.cards.append(_card(CARD_SECOND_CHANCE, uid=uid))
    extra = _card(CARD_SECOND_CHANCE, uid=1)
    game.deck = [
        _card(CARD_NUMBER, 4, uid=3),
        _card(CARD_NUMBER, 3, uid=2),
        extra,
    ]

    game._start_flip_three(target)

    assert advance_until(
        game, lambda: game.flip_state is None and game.drawn_card is None
    )
    assert game.pending_choice is None
    assert extra in game.discard
    assert sorted(target.numbers) == [3, 4, 7]


def test_flip7_bust_discards_only_the_busted_recipients_pending_cards():
    # An outer Freeze stays queued when a nested Flip Three recipient busts.
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [11, 4, 12])
    outer, nested, _third = game.players
    outer_freeze = _card(CARD_FREEZE, uid=1)
    game.pending_actions = [
        Flip7PendingAction(kind=CARD_FREEZE, owner_id=outer.id, card=outer_freeze),
        Flip7PendingAction(
            kind=CARD_FLIP_THREE,
            owner_id=nested.id,
            card=_card(CARD_FLIP_THREE, uid=2),
        ),
    ]

    game._flip_bust_abort(nested.id)

    # The outer Freeze survives and is now offered, not thrown away.
    assert outer_freeze not in game.discard
    assert all(p.card is not outer_freeze for p in game.pending_actions)
    assert game.pending_choice is not None
    assert game.pending_choice.kind == CHOICE_FREEZE
    assert game.pending_choice.actor_id == outer.id
    assert _card(CARD_FLIP_THREE, uid=2) in game.discard


def test_flip7_frozen_owner_still_resolves_its_queued_action_cards():
    # Being frozen is not busting: revealed Flip Three/Freeze cards resolve.
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [11, 4, 12])
    owner, target, _third = game.players
    owner.round_status = STATUS_STAYED
    frozen = _card(CARD_FREEZE, uid=1)
    game.pending_actions = [
        Flip7PendingAction(kind=CARD_FREEZE, owner_id=owner.id, card=frozen)
    ]

    game._resolve_pending_flow()

    # The frozen owner is offered the choice instead of losing the card.
    assert game.pending_actions == []
    assert frozen not in game.discard
    assert game.pending_choice is not None
    assert game.pending_choice.kind == CHOICE_FREEZE
    assert game.pending_choice.actor_id == owner.id


def test_flip7_missing_owner_recovery_keeps_other_owners_cards():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [11, 4, 12])
    _first, gone, survivor = game.players
    lost = _card(CARD_FLIP_THREE, uid=1)
    kept = _card(CARD_FREEZE, uid=2)
    game.pending_actions = [
        Flip7PendingAction(kind=CARD_FLIP_THREE, owner_id=gone.id, card=lost),
        Flip7PendingAction(kind=CARD_FREEZE, owner_id=survivor.id, card=kept),
    ]
    game.remove_player(gone.id)

    game._resolve_pending_flow()

    # The survivor's Freeze is resolved, not destroyed by the missing owner.
    assert lost in game.discard
    assert kept not in game.discard
    assert all(p.card is not kept for p in game.pending_actions)
    assert game.pending_choice is not None
    assert game.pending_choice.actor_id == survivor.id


def test_flip7_flip_three_forced_bust_aborts_the_flow():
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [11, 9])
    target = game.players[1]
    game.deck = [_card(CARD_NUMBER, v, uid=v) for v in (9, 10)]
    game._start_flip_three(target)
    assert game.flip_state is not None
    assert advance_until(game, lambda: game.flip_state is None)
    assert target.round_status == STATUS_BUSTED
    assert sorted(c.value for c in target.cards) == [9, 10]
    assert game.pending_actions == []


def test_flip7_flip_three_queue_opens_choice_for_the_recipient():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [11, 4, 12])
    target = game.players[1]
    game.deck = [_card(CARD_FREEZE, uid=1), _card(CARD_NUMBER, 7, uid=2),
                 _card(CARD_NUMBER, 8, uid=3)]
    game._start_flip_three(target)
    assert advance_until(
        game,
        lambda: (
            game.flip_state is None
            and game.pending_choice is not None
            and game.drawn_card is None
        ),
    )
    assert game.pending_choice.kind == CHOICE_FREEZE
    assert game._choice_actor() is target
    assert 7 in target.numbers and 8 in target.numbers


def test_flip7_flip_three_discover_of_seven_ends_flow_with_award():
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [1, 2])
    target = game.players[1]
    target.cards = [_card(CARD_NUMBER, v, uid=10 + v) for v in range(1, 7)]
    game.deck = [_card(CARD_NUMBER, FLIP_SEVEN_TARGET, uid=7)]
    game._start_flip_three(target)
    assert advance_until(game, lambda: game.phase != PHASE_PLAYING)
    assert game.flip_state is None
    assert target.flip_sevens == 1
    assert target.total_score == sum(range(1, 8)) + FLIP_SEVEN_BONUS


# ---------------------------------------------------------------------------
# Round and match end
# ---------------------------------------------------------------------------


def test_flip7_end_round_scores_stayers_and_zeroes_busters():
    game = _make_game(player_count=2)
    first, second = game.players
    first.cards = [
        _card(CARD_NUMBER, 3, uid=1),
        _card(CARD_NUMBER, 5, uid=2),
        _card(CARD_MODIFIER, 2, uid=3),
    ]
    first.round_status = STATUS_STAYED
    second.cards = [_card(CARD_NUMBER, 4, uid=4)]
    second.round_status = STATUS_BUSTED
    game.phase = PHASE_PLAYING

    game._end_round()

    assert first.total_score == 10
    assert second.total_score == 0
    assert game._team_manager.get_team(first.name).total_score == 10
    assert game.phase == PHASE_ROUND_END
    assert first.numbers == [] and first.modifiers == []
    assert second.numbers == []


def test_flip7_match_leader_is_the_unique_score_above_target():
    game = _make_game(player_count=2, start=False)
    game.game_active = True
    first, second = game.players
    first.total_score = 201
    second.total_score = 100
    assert game._match_leader() == (first, 201)

    second.total_score = 201
    assert game._match_leader() is None

    first.total_score = 100
    second.total_score = 0
    assert game._match_leader() is None


def test_flip7_match_reaches_end_phase_when_target_is_met():
    game = _make_game(player_count=2)
    first, second = game.players
    first.total_score = 198
    first.cards = [_card(CARD_NUMBER, 5, uid=1)]
    first.round_status = STATUS_STAYED
    second.round_status = STATUS_BUSTED
    game.phase = PHASE_PLAYING

    game._end_round()

    # The end screen waits until the round-end and win cues have finished.
    assert game.phase == PHASE_MATCH_END
    assert game.status != "finished"
    assert advance_until(game, lambda: game.status == "finished")
    assert first.total_score == 203


def test_flip7_round_end_cue_completes_before_the_first_card_is_dealt():
    game = _make_game(player_count=3, start=False)
    game.deck = [
        _card(CARD_NUMBER, 3, uid=31),
        _card(CARD_NUMBER, 4, uid=32),
        _card(CARD_NUMBER, 5, uid=33),
    ]
    game.on_start()
    game.flush_menus()
    # Nothing may be dealt while the round-start cue is still audible.
    assert game.drawn_card is None
    assert all(not player.cards for player in game._active())
    assert advance_until(game, lambda: game.deal_index > 0)
    assert game.drawn_card is not None


def test_flip7_match_win_cue_precedes_the_end_screen():
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [11, 12])
    winner = game.players[0]
    winner.total_score = 198
    winner.round_status = STATUS_STAYED
    game.players[1].round_status = STATUS_BUSTED

    game._end_round()

    assert game.status != "finished"
    # The winner is announced before the game is finished, not after.
    while game.status != "finished":
        game.on_tick()
        game.flush_menus()
    said = [
        message
        for message in game.get_user(winner).messages
        if message.type == "speak"
    ]
    assert said


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------


def test_flip7_turn_menu_orders_areas_below_main_actions():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    actor = game.current_player
    user = game.get_user(actor)
    game.before_menu_build(actor)
    build = game.build_menu_items(actor, user)

    ids = [item.id for item in build.items]
    assert "hit" in ids
    assert "stay" in ids
    area_ids = [item_id for item_id in ids if item_id.startswith("flip7_area_")]
    assert len(area_ids) == 2
    assert ids.index("hit") < ids.index(area_ids[0])
    assert ids.index("stay") < ids.index(area_ids[0])
    assert all(item.read_only for item in build.items if item.id in area_ids)


def test_flip7_turn_menu_swaps_to_choice_actions():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    actor = game.players[0]
    _resolve(game, actor, _card(CARD_FREEZE, uid=1))
    game.before_menu_build(actor)

    ids = [resolved.action.id for resolved in game.get_all_visible_actions(actor)]
    assert "hit" not in ids
    assert "stay" not in ids
    for target in game._choice_targets():
        assert f"choose_freeze_{target.id}" in ids


def test_flip7_information_actions_touch_visibility():
    desktop = _make_game(player_count=2)
    mobile = _make_game(player_count=2, mobile_user=True)

    for game in (desktop, mobile):
        actor = game.players[0]
        game.before_menu_build(actor)
        for action_id in ("check_area", "check_table", "check_deck"):
            action = game.find_action(actor, action_id)
            resolved = game.resolve_action(actor, action)
            assert resolved.visible is True, (action_id,)
            assert resolved.enabled is True
            # Desktop clients reach these through the actions menu, not only
            # through the table board.
            assert resolved.action.show_in_actions_menu is True, action_id
            assert resolved.action.include_spectators is (
                action_id in ("check_table", "check_deck")
            ), action_id


# ---------------------------------------------------------------------------
# Keybinds
# ---------------------------------------------------------------------------


def test_flip7_keybind_setup_states_and_actions():
    game = _make_game(player_count=2, start=False)

    def actions_for(key):
        return {tuple(keybind.actions) for keybind in game._keybinds[key]}

    assert actions_for("space") == {("hit",)}
    assert actions_for("h") == {("stay",)}
    assert actions_for("c") == {("check_area",)}
    assert actions_for("shift+c") == {("check_table",)}
    assert actions_for("d") == {("check_deck",)}

    for key in ("space", "h", "c", "shift+c", "d"):
        assert all(k.state == KeybindState.ACTIVE for k in game._keybinds[key]), key

    assert game._keybinds["shift+c"][0].include_spectators is True
    assert game._keybinds["d"][0].include_spectators is True


def test_flip7_keybind_c_speaks_the_area_even_though_standalone():
    game = _make_game(player_count=2)
    _deal_number_cards(game, [3, 4])
    actor = game.current_player
    actor.cards.append(_card(CARD_NUMBER, 5, uid=100))
    user = game.get_user(actor)
    user.clear_messages()

    game.handle_event(actor, {"type": "keybind", "key": "c"})

    spoken = [
        message.data["text"]
        for message in user.messages
        if message.type == "speak" and message.data.get("buffer") == "game"
    ]
    assert any("Total" in text for text in spoken)


def test_flip7_modifier_reveals_use_the_exact_value_cue():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    for value in (2, 4, 6, 8, 10):
        card = _card(CARD_MODIFIER, value, uid=value)
        assert game._card_reveal_sound(card, forced=False) == (
            f"game_flip7/modifier_plus_{value}.ogg"
        )


def test_flip7_forced_action_reveals_keep_their_own_cue():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    expected = {
        CARD_FREEZE: "game_flip7/freeze.ogg",
        CARD_FLIP_THREE: "game_flip7/flip_three.ogg",
        CARD_SECOND_CHANCE: "game_flip7/second_chance.ogg",
    }
    for kind, cue in expected.items():
        card = _card(kind, uid=1)
        assert game._card_reveal_sound(card, forced=True) == cue
        assert game._card_reveal_sound(card, forced=False) == cue


def test_flip7_audio_fallback_metadata_matches_every_shipped_asset():
    # Server-only deployments cannot measure assets, so the fallback table must
    # equal the real durations of the exact files that ship with each client.
    repository_root = ROOT
    for key, declared in audio.AUDIO_DURATIONS_TICKS.items():
        if not key.startswith("game_flip7/") or not key.endswith(".ogg"):
            continue
        measured = measure_audio_duration_ticks(
            repository_root / "client" / "sounds" / key,
            ticks_per_second=audio.TICKS_PER_SECOND,
        )
        assert measured is not None, key
        assert declared == measured, f"{key}: table={declared} asset={measured}"


def test_flip7_deal_reveals_announce_cards_and_schedule_sound():
    game = _make_game(player_count=2)
    # The live deck is shuffled; pin a known run of number cards so both
    # opening reveals are deterministic and no dealt action card pauses the
    # deal waiting for a human choice.
    game.deck = [
        _card(CARD_NUMBER, value, uid=300 + value)
        for value in (12, 11, 10, 9, 8, 7)
    ]
    for player in game.players:
        game.get_user(player).clear_messages()

    for _ in range(2500):
        game.on_tick()
        if all(
            any(
                message.type == "speak"
                and message.data.get("buffer") == "game"
                and "Card:" in message.data.get("text", "")
                for message in game.get_user(player).messages
            )
            for player in game.players
        ):
            break

    for player in game.players:
        spoken = [
            message.data["text"]
            for message in game.get_user(player).messages
            if message.type == "speak"
            and message.data.get("buffer") == "game"
        ]
        assert any("Card:" in text for text in spoken), spoken
        assert any(
            message.type == "play_sound"
            for message in game.get_user(player).messages
        )


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def test_flip7_game_state_serializes_round_trip():
    game = _make_game(player_count=2)
    first = game.players[0]
    first.cards = [
        _take_from_deck(game, CARD_NUMBER, 2),
        _take_from_deck(game, CARD_NUMBER, 7),
        _take_from_deck(game, CARD_MODIFIER, 4),
    ]
    first.total_score = 33
    first.round_status = STATUS_STAYED

    raw = game.to_json()
    data = json.loads(raw)
    assert data["round"] == 1

    loaded = Flip7Game.from_json(raw)
    assert loaded.options.target_score == 200
    loaded_first = loaded.players[0]
    assert loaded_first.numbers == [2, 7]
    assert loaded_first.modifiers == [4]
    assert loaded_first.total_score == 33
    assert loaded_first.round_status == STATUS_STAYED


# ---------------------------------------------------------------------------
# Bot completion
# ---------------------------------------------------------------------------


def test_flip7_bots_play_a_full_match_to_finished():
    game = _make_game(player_count=3, start=True, bot_all=True, target_score=50)
    assert advance_until(game, lambda: game.status == "finished", max_ticks=60000)
    assert game.phase == PHASE_MATCH_END
    scores = [p.total_score for p in game.players]
    assert max(scores) >= 50


def test_flip7_bot_current_player_answers_choice_while_sequences_pause_bots():
    game = _make_game(player_count=3, start=True, bot_all=True)
    _deal_number_cards(game, [3, 4, 5])
    actor = game.current_player
    assert actor.is_bot is True

    # A long trainer sequence keeps bot decision-making paused while the
    # current player must answer a targetable card. During the initial deal
    # or a Flip Three the reveal sequence similarly pauses bots, so the
    # choice must not wait for BotHelper.on_tick to become live again.
    game.start_sequence(
        "flip7_test_pause_bots",
        [
            SequenceBeat.pause(1000),
            SequenceBeat(ops=[SequenceOperation.callback_op("test_noop")]),
        ],
        tag=TAG_FLOW,
        lock_scope=game.SEQUENCE_LOCK_GAMEPLAY,
        pause_bots=True,
    )
    result = game._open_choice(CHOICE_FREEZE, actor, card=_card(CARD_FREEZE, uid=1))
    assert result == OUTCOME_CHOICE
    game.flush_menus()
    assert game._choice_actor() is actor
    assert game.is_sequence_bot_paused() is True

    assert advance_until(game, lambda: game.pending_choice is None, max_ticks=300)
    assert any(p.round_status == STATUS_STAYED for p in game.players)


# ---------------------------------------------------------------------------
# Nested resolution and per-listener wording
# ---------------------------------------------------------------------------


def _spoken(user):
    return [
        message.data["text"]
        for message in user.messages
        if message.type == "speak"
    ]


def test_flip7_nested_flip_three_resolves_the_inner_choice_before_the_queue():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [11, 4, 12])
    target, nested_target = game.players[1], game.players[2]

    # The outer Flip Three turns a Flip Three first, so the inner choice must
    # be answered by its own recipient before the outer queue moves on.
    game.deck = (
        [_card(CARD_NUMBER, v, uid=40 + v) for v in range(10)]
        + [_card(CARD_NUMBER, v, uid=10 + v) for v in (1, 2, 3)]
        + [_card(CARD_NUMBER, v, uid=10 + v) for v in (5, 6)]
        + [_card(CARD_FLIP_THREE, uid=1)]
    )
    game._start_flip_three(target)
    assert advance_until(
        game,
        lambda: (
            game.flip_state is None
            and game.drawn_card is None
            and game.pending_choice is not None
        ),
    )
    assert game.pending_choice.kind == CHOICE_FLIP_THREE
    assert game._choice_actor() is target
    assert sorted(target.numbers) == [4, 5, 6]

    game.before_menu_build(target)
    game.execute_action(target, f"choose_flip_three_{nested_target.id}")
    # The nested flip owns progress and the queued card was consumed once.
    assert game.flip_state is not None
    assert game.flip_state.target_id == nested_target.id
    assert game.pending_choice is None
    assert game.pending_actions == []
    assert [card.uid for card in game._physical_cards()].count(1) == 1

    assert advance_until(
        game, lambda: game.flip_state is None and game.drawn_card is None
    )
    assert sorted(nested_target.numbers) == [1, 2, 3, 12]
    assert [card.uid for card in game._physical_cards()].count(1) == 1
    assert game.phase == PHASE_PLAYING


def test_flip7_nested_flip_three_actions_resolve_before_outer_queue_remainder():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [11, 4, 12])
    outer, nested, _third = game.players
    outer_flip = _card(CARD_FLIP_THREE, uid=1)
    outer_freeze = _card(CARD_FREEZE, uid=2)
    nested_freeze = _card(CARD_FREEZE, uid=3)
    game.pending_actions = [
        Flip7PendingAction(
            kind=CARD_FLIP_THREE, owner_id=outer.id, card=outer_flip
        ),
        Flip7PendingAction(
            kind=CARD_FREEZE, owner_id=outer.id, card=outer_freeze
        ),
    ]
    game.deck = [
        _card(CARD_NUMBER, 6, uid=6),
        _card(CARD_NUMBER, 5, uid=5),
        nested_freeze,
    ]

    game._resolve_pending_flow()
    assert game.pending_choice is not None
    assert game.pending_choice.kind == CHOICE_FLIP_THREE
    assert game._choice_actor() is outer

    game.before_menu_build(outer)
    game.execute_action(outer, f"choose_flip_three_{nested.id}")
    assert advance_until(
        game,
        lambda: game.flip_state is None and game.pending_choice is not None,
    )

    # The inner Freeze is offered before the outer Freeze that was suspended
    # behind the nested Flip Three.
    assert game.pending_choice.kind == CHOICE_FREEZE
    assert game._choice_actor() is nested
    assert [pending.card for pending in game.pending_actions] == [outer_freeze]


def test_flip7_freeze_targeting_self_uses_personal_and_third_person_forms():
    game = _make_game(player_count=2, start=False, locales=("en", "vi"))
    _deal_number_cards(game, [3, 4])
    actor, observer = game.players
    actor_user, observer_user = game.get_user(actor), game.get_user(observer)
    _resolve(game, actor, _card(CARD_FREEZE, uid=1))
    actor_user.clear_messages()
    observer_user.clear_messages()

    game.before_menu_build(actor)
    game.execute_action(actor, f"choose_freeze_{actor.id}")

    assert actor.round_status == STATUS_STAYED
    # The actor hears the first-person form; everyone else the third-person one.
    assert any("You stop yourself and keep" in t for t in _spoken(actor_user))
    assert not any("stop yourself" in t for t in _spoken(observer_user))
    # The Vietnamese observer receives the same fact localized, not English.
    assert any("d\u1eebng l\u1ea1i" in t for t in _spoken(observer_user))
    assert all("You stop yourself" not in t for t in _spoken(observer_user))


def test_flip7_flip_three_targeting_self_uses_personal_and_third_person_forms():
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [3, 4])
    actor, observer = game.players
    actor_user, observer_user = game.get_user(actor), game.get_user(observer)
    game.deck = [_card(CARD_NUMBER, v, uid=10 + v) for v in (6, 7, 8)]
    _resolve(game, actor, _card(CARD_FLIP_THREE, uid=1))
    actor_user.clear_messages()
    observer_user.clear_messages()

    game.before_menu_build(actor)
    game.execute_action(actor, f"choose_flip_three_{actor.id}")

    assert any("You flip three cards" in t for t in _spoken(actor_user))
    assert any("flips three cards" in t for t in _spoken(observer_user))
    assert not any("You flip three cards" in t for t in _spoken(observer_user))
    # The self-targeted flip reveals on the owner's own area and never becomes
    # a pending flow that another player has to answer.
    assert game.pending_choice is None
    assert advance_until(
        game, lambda: game.flip_state is None and game.drawn_card is None
    )
    assert sorted(actor.numbers) == [3, 6, 7, 8]
    assert sorted(observer.numbers) == [4]


def test_flip7_pending_action_recipient_hears_the_personal_discard_warning():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    owner, observer = game.players[1], game.players[0]
    freeze = _card(CARD_FREEZE, uid=1)
    owner.round_status = STATUS_BUSTED
    game.pending_actions = [
        Flip7PendingAction(kind=CARD_FREEZE, owner_id=owner.id, card=freeze)
    ]
    owner_user, observer_user = game.get_user(owner), game.get_user(observer)
    owner_user.clear_messages()
    observer_user.clear_messages()

    game._resolve_pending_flow()

    assert game.pending_actions == []
    assert freeze in game.discard
    assert any("held action cards are discarded" in t for t in _spoken(owner_user))
    assert any("held action cards are discarded" in t for t in _spoken(observer_user))


# ---------------------------------------------------------------------------
# Menus, spectators, and results
# ---------------------------------------------------------------------------


def test_flip7_choice_menu_uses_stable_target_ids_and_focuses_the_first_target():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    actor = game.players[0]
    actor_user = game.get_user(actor)

    _resolve(game, actor, _card(CARD_FREEZE, uid=1))
    targets = game._choice_targets()
    choice_ids = [f"choose_freeze_{target.id}" for target in targets]
    item_ids = [item.id for item in actor_user.menus["turn_menu"]["items"]]
    assert item_ids[: len(choice_ids)] == choice_ids
    assert "hit" not in item_ids and "stay" not in item_ids

    turn_updates = [
        message
        for message in actor_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_updates[-1].data.get("selection_id") == choice_ids[0]


def test_flip7_pending_choice_keeps_unrelated_players_turn_rows_stable():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    actor, observer, third = game.players
    observer_user, third_user = game.get_user(observer), game.get_user(third)
    game.flush_menus()

    baseline = {}
    for player in (observer, third):
        baseline[player.id] = [
            item.id
            for item in game.get_user(player).menus["turn_menu"]["items"]
            if not item.id.startswith("flip7_area_")
        ]
    assert baseline[observer.id] == [
        "hit",
        "stay",
        "check_area",
        "check_table",
        "check_deck",
    ]

    _resolve(game, actor, _card(CARD_FREEZE, uid=1))

    # One player's private decision must not empty anyone else's turn menu:
    # their stable rows survive as disabled controls with the waiting reason.
    for player, user in ((observer, observer_user), (third, third_user)):
        item_ids = [item.id for item in user.menus["turn_menu"]["items"]]
        persistent = [
            item_id for item_id in item_ids if not item_id.startswith("flip7_area_")
        ]
        assert persistent == baseline[player.id]
        assert game._is_hit_enabled(player) == "flip7-error-wait-choice"
        assert game._is_stay_enabled(player) == "flip7-error-wait-choice"

    # The actor alone sees the decision menu, and it still focuses a target.
    actor_items = [
        item.id for item in game.get_user(actor).menus["turn_menu"]["items"]
    ]
    assert actor_items[0].startswith("choose_freeze_")


def test_flip7_pending_choice_repeated_builds_preserve_set_order_and_focus():
    # before_menu_build() must be idempotent while another player chooses.
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    actor, observer, third = game.players
    observer_user = game.get_user(observer)
    game.flush_menus()

    _resolve(game, actor, _card(CARD_FREEZE, uid=1))

    def snapshot(user):
        return [
            item.id for item in user.menus["turn_menu"]["items"]
        ]

    first = snapshot(observer_user)
    assert first[:2] == ["hit", "stay"]
    # The retained rows must be reported, or the set is torn down every build.
    assert game._desired_turn_action_ids(observer) == ["hit", "stay"]

    for _ in range(5):
        game.before_menu_build(observer)
        game.flush_menus()
        assert snapshot(observer_user) == first

    turn_updates = [
        message
        for message in observer_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    # A same-menu repaint without a focus directive must not move focus.
    assert turn_updates[-1].data.get("selection_id") is None


def test_flip7_spectators_read_public_information_but_not_private_areas():
    game = _make_game(player_count=3, start=False)
    _deal_number_cards(game, [3, 4, 5])
    watcher = game.players[2]
    watcher.is_spectator = True
    user = game.get_user(watcher)

    game.before_menu_build(watcher)
    for action_id in ("check_table", "check_deck"):
        resolved = game.resolve_action(watcher, game.find_action(watcher, action_id))
        assert resolved.visible is True, action_id
        assert resolved.enabled is True, action_id
    private = game.resolve_action(watcher, game.find_action(watcher, "check_area"))
    assert private.visible is False

    user.clear_messages()
    game.execute_action(watcher, "check_deck")
    assert any("Deck:" in text for text in _spoken(user))


def test_flip7_result_binds_winner_and_players_to_immutable_account_ids():
    game = _make_game(player_count=2, start=False)
    first, second = game.players
    first.total_score = 210
    second.total_score = 100
    first.cards_drawn = 9
    first.busts = 2
    first.flip_sevens = 1

    result = game.build_game_result()

    assert result.custom_data["winner_ids"] == [first.id]
    assert result.custom_data["winner_name"] == first.name
    assert result.custom_data["winner_score"] == 210
    assert [entry.player_id for entry in result.player_results] == [
        first.id,
        second.id,
    ]
    # Names are historical snapshots; identity stays the immutable account id.
    assert first.name not in result.custom_data["winner_ids"]
    assert result.custom_data["player_stats"][first.name] == {
        "total_score": 210,
        "rounds_busted": 2,
        "flip_sevens": 1,
        "cards_drawn": 9,
    }
    assert result.custom_data[RATING_COMPETITORS_KEY] == [
        {"player_ids": [first.id], "rank": 0},
        {"player_ids": [second.id], "rank": 1},
    ]


def test_flip7_empty_deck_reshuffles_the_discard_pile():
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [3, 4])
    user = game.get_user(game.players[0])
    game.deck = []
    game.discard = [_card(CARD_NUMBER, 7, uid=50), _card(CARD_MODIFIER, 4, uid=51)]
    user.clear_messages()

    card = game._draw_card()

    assert card is not None
    assert len(game.deck) == 1
    assert game.discard == []
    assert any("reshuffled" in text for text in _spoken(user))
    assert any("shuffle" in name for name in user.get_sounds_played())


def test_flip7_freeze_target_label_formats_target_name_in_portuguese():
    Localization._bundles.clear()
    Localization._bundle_cache_by_dir.clear()
    Localization.preload_bundles()
    game = _make_game(player_count=2, start=False)
    _deal_number_cards(game, [7, 5])
    actor = game.players[0]
    target = game.players[1]
    _resolve(game, actor, _card(CARD_FREEZE, uid=1))

    label = Localization.get("pt", "flip7-target-freeze", target=target.name, points=game.round_points(target))
    assert target.name in label
    assert "Faça target" not in label
    assert f"Faça {target.name} congelar (5 pontos)" in label
