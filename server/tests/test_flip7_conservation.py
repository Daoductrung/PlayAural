"""Physical deck regressions: real cards, timed callbacks, and saved states."""

import json
from collections import Counter

import pytest

from ..games.flip7.game import (
    Flip7Game, Flip7PendingAction, CARD_NUMBER, CARD_MODIFIER, CARD_DOUBLE,
    CARD_SECOND_CHANCE, CARD_FREEZE, CARD_FLIP_THREE, CONTINUE_FLOW,
    PHASE_PLAYING, STATUS_BUSTED, STATUS_STAYED, TAG_FLOW,
)
from ..users.test_user import MockUser


def make_game():
    game = Flip7Game()
    for i in range(3):
        user = MockUser(f"Player{i}", uuid=f"p{i}")
        game.add_player(user.username, user)
    game.host = "Player0"
    game.on_start()
    game.cancel_sequences_by_tag(TAG_FLOW)
    game._discard_pending_cards()
    game.deck.extend(game.discard)
    game.discard = []
    game.deal_index = len(game.deal_order)
    return game


def take(game, kind, value=None):
    card = next(c for c in game.deck if c.kind == kind and
                (value is None or c.value == value))
    game.deck.remove(card)
    return card


def inventory(game):
    # Independent enumeration so a bug in the production counter cannot hide loss.
    cards = list(game.deck) + list(game.discard)
    cards += [c for p in game.players for c in p.cards]
    cards += [p.card for p in game.pending_actions]
    if game.pending_choice and game.pending_choice.card:
        cards.append(game.pending_choice.card)
    if game.drawn_card:
        cards.append(game.drawn_card)
    return Counter((c.uid, c.kind, c.value) for c in cards)


def conserved(game, *, restore=False):
    expected = Counter((c.uid, c.kind, c.value) for c in game.build_deck())
    assert inventory(game) == expected
    assert game._total_cards_in_play() == 94
    if restore:
        loaded = Flip7Game.from_json(game.to_json())
        assert inventory(loaded) == expected
        return loaded


def tick_until(game, condition):
    for _ in range(2000):
        if condition():
            return
        game.on_tick()
        game.flush_menus()
        conserved(game)
    pytest.fail("Timed card flow did not complete")


def reveal(game, player, card, *, forced=False):
    game._resolve_card(player, card, forced=forced, continuation=CONTINUE_FLOW,
                       pending_owner=player.id)
    conserved(game, restore=True)
    tick_until(game, lambda: game.drawn_card is None)
    conserved(game, restore=True)


@pytest.mark.parametrize("kind", [CARD_NUMBER, CARD_MODIFIER, CARD_DOUBLE,
                                 CARD_SECOND_CHANCE])
def test_reveal_keeps_exact_object_and_round_cleanup(kind):
    game = make_game()
    player = game.players[0]
    card = take(game, kind)
    reveal(game, player, card)
    assert any(c is card for c in player.cards)
    game._end_round()
    assert any(c is card for c in game.discard)
    conserved(game, restore=True)
    game._start_round()
    conserved(game, restore=True)


def test_second_chance_consumes_its_owners_exact_card():
    game = make_game()
    first, second, _ = game.players
    protection = take(game, CARD_SECOND_CHANCE)
    other_protection = take(game, CARD_SECOND_CHANCE)
    first.cards.extend([take(game, CARD_NUMBER, 7), protection])
    second.cards.append(other_protection)
    duplicate = take(game, CARD_NUMBER, 7)
    reveal(game, first, duplicate)
    assert not first.second_chance
    assert second.second_chance
    assert protection in game.discard and duplicate in game.discard
    assert any(c is other_protection for c in second.cards)
    conserved(game, restore=True)


@pytest.mark.parametrize("give", [False, True])
def test_duplicate_second_chance_is_given_or_discarded(give):
    game = make_game()
    actor, target, other = game.players
    actor.cards.append(take(game, CARD_SECOND_CHANCE))
    other.round_status = STATUS_STAYED
    if not give:
        target.round_status = STATUS_STAYED
    card = take(game, CARD_SECOND_CHANCE)
    reveal(game, actor, card)
    if give:
        game = conserved(game, restore=True)
        actor, target, _ = game.players
        game._consume_choice(actor, target)
        assert card in target.cards
    else:
        assert card in game.discard
    conserved(game, restore=True)


@pytest.mark.parametrize("kind", [CARD_FREEZE, CARD_FLIP_THREE])
def test_action_card_is_discarded_once_after_saved_choice(kind):
    game = make_game()
    card = take(game, kind)
    reveal(game, game.players[0], card)
    assert game.pending_choice.card is card
    game = conserved(game, restore=True)
    # Forced draws use known numbers, not random nested actions.
    numbers = [take(game, CARD_NUMBER, value) for value in (2, 3, 4)]
    game.deck.extend(numbers)
    game._consume_choice(game.players[0], game.players[1])
    assert sum(c.uid == card.uid for c in game.discard) == 1
    tick_until(game, lambda: game.flip_state is None and game.drawn_card is None)
    conserved(game, restore=True)


@pytest.mark.parametrize("ending", ["bust", "flip7", "bank"])
def test_round_end_conditions_preserve_all_cards(ending):
    game = make_game()
    actor = game.players[0]
    if ending == "bank":
        actor.cards.append(take(game, CARD_NUMBER, 5))
        actor.round_status = STATUS_STAYED
        game._end_round()
    else:
        values = [7] if ending == "bust" else [1, 2, 3, 4, 5, 6]
        actor.cards.extend(take(game, CARD_NUMBER, v) for v in values)
        reveal(game, actor, take(game, CARD_NUMBER, 7))
        if ending == "bust":
            assert actor.round_status == STATUS_BUSTED
            game._end_round()
        else:
            tick_until(game, lambda: game.phase != PHASE_PLAYING)
    conserved(game, restore=True)


def test_reshuffle_leaves_held_and_pending_cards_untouched():
    game = make_game()
    held = take(game, CARD_SECOND_CHANCE)
    game.players[0].cards.append(held)
    pending = take(game, CARD_FREEZE)
    game.pending_actions.append(Flip7PendingAction(pending.kind, "p0", pending))
    game.discard = game.deck
    game.deck = []
    available = {c.uid for c in game.discard}
    drawn = game._draw_card()
    game.drawn_card = drawn
    assert drawn.uid in available
    assert {c.uid for c in game.deck} == available - {drawn.uid}
    assert game.players[0].cards == [held]
    assert game.pending_actions[0].card is pending
    assert not game._reshuffle_discard()
    conserved(game, restore=True)


def test_round_end_during_reveal_discards_pending_card():
    game = make_game()
    card = take(game, CARD_FREEZE)
    game._resolve_card(game.players[0], card, forced=False, continuation=CONTINUE_FLOW)
    game = conserved(game, restore=True)
    game._end_round()
    assert card in game.discard
    conserved(game, restore=True)


def test_restore_reveal_continues_without_creating_a_second_card():
    game = make_game()
    card = take(game, CARD_NUMBER, 8)
    game._resolve_card(game.players[0], card, forced=False, continuation=CONTINUE_FLOW)
    game = conserved(game, restore=True)
    tick_until(game, lambda: game.drawn_card is None)
    assert card in game.players[0].cards
    game._apply_card_effect({"uid": card.uid, "target_id": "p0", "kind": card.kind})
    conserved(game, restore=True)


def test_missing_recipient_does_not_lose_revealed_card():
    game = make_game()
    card = take(game, CARD_NUMBER, 5)
    game.drawn_card = card
    game._apply_card_effect({"uid": card.uid, "target_id": "missing"})
    assert any(c is card for c in game.discard)
    conserved(game, restore=True)


@pytest.mark.parametrize("kind", [CARD_FREEZE, CARD_FLIP_THREE, CARD_SECOND_CHANCE])
def test_forced_pending_cards_survive_save_and_early_abort(kind):
    game = make_game()
    card = take(game, kind)
    reveal(game, game.players[0], card, forced=True)
    assert game.pending_actions[0].card is card
    game = conserved(game, restore=True)
    game._flip_bust_abort("p0")
    assert card in game.discard
    conserved(game, restore=True)


def test_saved_active_flip_three_preserves_reveals_and_held_cards():
    game = make_game()
    # Keep each forced draw deterministic, including a saved duplicate.
    target = game.players[1]
    target.cards.extend([take(game, CARD_NUMBER, 7), take(game, CARD_SECOND_CHANCE)])
    game.deck.extend([take(game, CARD_NUMBER, v) for v in (8, 9, 7)])
    game._start_flip_three(target)
    game = conserved(game, restore=True)
    tick_until(game, lambda: game.flip_state is None and game.drawn_card is None)
    assert game.players[1].numbers == [7, 8, 9]
    assert not game.players[1].second_chance
    conserved(game, restore=True)


def test_flip_three_forced_action_card_belongs_to_the_recipient():
    # The player who draws during Flip Three owns the forced action card and
    # decides how to spend it; the chooser must never open that choice.
    game = make_game()
    chooser, target, _ = game.players
    freeze = take(game, CARD_FREEZE)
    game.deck.extend([freeze, take(game, CARD_NUMBER, 7), take(game, CARD_NUMBER, 8)])
    game._start_flip_three(target)
    assert game.flip_state is not None and game.flip_state.target_id == target.id
    game = conserved(game, restore=True)
    tick_until(game, lambda: game.flip_state is None and game.drawn_card is None)
    assert game.pending_choice is not None
    assert game.pending_choice.actor_id == target.id
    assert game.pending_choice.actor_id != chooser.id
    assert game.pending_choice.kind == CARD_FREEZE
    assert game.pending_choice.card.uid == freeze.uid
    conserved(game, restore=True)


def test_flip_three_self_targeted_action_card_belongs_to_the_actor():
    game = make_game()
    actor, _, _ = game.players
    freeze = take(game, CARD_FREEZE)
    game.deck.extend([freeze, take(game, CARD_NUMBER, 7), take(game, CARD_NUMBER, 8)])
    game._start_flip_three(actor)
    game = conserved(game, restore=True)
    tick_until(game, lambda: game.flip_state is None and game.drawn_card is None)
    assert game.pending_choice is not None
    assert game.pending_choice.actor_id == actor.id
    assert game.pending_choice.card.uid == freeze.uid
    conserved(game, restore=True)


def test_many_rounds_recycle_original_cards_without_new_identities():
    game = make_game()
    original = {c.uid: c for c in game._physical_cards()}
    for _ in range(20):
        # Consume the remaining pile, then end the round with held cards.
        game.players[0].cards.extend(game.deck)
        game.deck = []
        game._end_round()
        conserved(game, restore=True)
        game._start_round()
        conserved(game, restore=True)
        assert all(c is original[c.uid] for c in game._physical_cards())


@pytest.mark.parametrize("damage", ["legacy", "missing", "duplicate"])
def test_unsafe_save_is_rejected_without_guessing_cards(damage):
    data = json.loads(make_game().to_json())
    if damage == "legacy":
        data.pop("card_state_version")
    elif damage == "missing":
        data["deck"].pop()
    else:
        data["deck"][0] = data["deck"][1]
    with pytest.raises(ValueError):
        Flip7Game.from_dict(data)
