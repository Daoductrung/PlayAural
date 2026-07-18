"""Public-information-only strategy for Exploding Kittens bots."""

from __future__ import annotations

from collections import Counter
from math import comb
import random
from typing import TYPE_CHECKING

from .cards import (
    ATTACK,
    CARD_COUNTS,
    CAT_KINDS,
    DEFUSE,
    EXPLODING_KITTEN,
    FAVOR,
    NOPE,
    REQUESTABLE_KINDS,
    SEE_FUTURE,
    SHUFFLE,
    SKIP,
    ExplodingKittensCard,
)
from .state import (
    ACTION_ATTACK,
    ACTION_FAVOR,
    ACTION_PAIR,
    ACTION_SEE_FUTURE,
    ACTION_SHUFFLE,
    ACTION_SKIP,
    ACTION_TRIPLE,
    PHASE_COMBO,
    PHASE_DEFUSE,
    PHASE_FAVOR_GIVE,
    PHASE_NOPE,
    PHASE_NORMAL,
    PHASE_REINSERT,
    PHASE_REQUEST,
    PHASE_TARGET,
)

if TYPE_CHECKING:
    from .game import ExplodingKittensGame
    from .player import ExplodingKittensPlayer


COMBO_MINIMUM_UTILITY = 0.75


def _hand_counts(player: "ExplodingKittensPlayer") -> Counter[str]:
    return Counter(card.kind for card in player.hand)


def _card_action(player: "ExplodingKittensPlayer", kind: str) -> str | None:
    card = next((card for card in player.hand if card.kind == kind), None)
    return f"play_card_{card.id}" if card else None


def _estimated_draw_risk(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> float:
    known = game._known_future_cards(player)
    if known:
        return 1.0 if known[0].kind == EXPLODING_KITTEN else 0.0
    if not game.deck:
        return 1.0
    kittens_remaining = max(0, len(game.alive_players) - 1)
    return min(1.0, kittens_remaining / len(game.deck))


def _card_value(player: "ExplodingKittensPlayer", kind: str) -> float:
    counts = _hand_counts(player)
    if kind == DEFUSE:
        if counts[DEFUSE] == 0:
            return 34.0
        return 22.0 if counts[DEFUSE] == 1 else 14.0
    if kind == NOPE:
        return 18.0 if counts[NOPE] == 0 else 12.0
    if kind == ATTACK:
        return 12.0
    if kind == SKIP:
        return 11.0
    if kind == SHUFFLE:
        return 9.0
    if kind == SEE_FUTURE:
        return 8.0
    if kind == FAVOR:
        return 6.0
    if kind in CAT_KINDS:
        return 3.0
    return 0.0


def _public_unknown_counts(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> Counter[str]:
    """Estimate unseen cards without reading the deck or opponents' hands."""
    counts = Counter(
        {
            kind: count
            for kind, count in CARD_COUNTS.items()
            if kind != EXPLODING_KITTEN
        }
    )
    for card in player.hand:
        counts[card.kind] -= 1
    for card in game.discard_pile:
        counts[card.kind] -= 1
    for card in game._known_future_cards(player):
        counts[card.kind] -= 1
    for kind in list(counts):
        counts[kind] = max(0, counts[kind])
    return counts


def _target_has_probability(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    target: "ExplodingKittensPlayer",
    kind: str,
) -> float:
    counts = _public_unknown_counts(game, player)
    remaining = counts[kind]
    population = sum(counts.values())
    sample = min(len(target.hand), population)
    if remaining <= 0 or sample <= 0 or population <= 0:
        return 0.0
    if sample > population - remaining:
        return 1.0
    return 1.0 - comb(population - remaining, sample) / comb(population, sample)


def _best_request(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    target: "ExplodingKittensPlayer",
) -> tuple[str, float]:
    best_kind = REQUESTABLE_KINDS[0]
    best_utility = -1.0
    for kind in REQUESTABLE_KINDS:
        utility = _target_has_probability(game, player, target, kind) * _card_value(
            player, kind
        )
        if utility > best_utility:
            best_kind = kind
            best_utility = utility
    return best_kind, max(0.0, best_utility)


def _expected_random_card_value(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> float:
    counts = _public_unknown_counts(game, player)
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return sum(
        count * _card_value(player, kind) for kind, count in counts.items()
    ) / total


def _strongest_target(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> "ExplodingKittensPlayer | None":
    targets = game._valid_targets(player)
    if not targets:
        return None
    pending_kind = game.pending_action.kind if game.pending_action else ""
    next_player = game._next_alive_after(player.id)

    def target_score(target: "ExplodingKittensPlayer") -> tuple[float, int, int]:
        request_utility = (
            _best_request(game, player, target)[1]
            if pending_kind == ACTION_TRIPLE
            else 0.0
        )
        next_bonus = int(next_player is not None and target.id == next_player.id)
        return request_utility, len(target.hand), next_bonus

    return max(targets, key=target_score)


def _combo_spend_value(
    player: "ExplodingKittensPlayer", kind: str, size: int
) -> float:
    if kind in CAT_KINDS:
        base = 1.5
    else:
        base = {
            FAVOR: 4.0,
            SEE_FUTURE: 6.0,
            SHUFFLE: 7.0,
            SKIP: 8.0,
            ATTACK: 9.0,
            NOPE: 13.0,
            DEFUSE: 100.0,
        }.get(kind, 10.0)
    retained = _hand_counts(player)[kind] - size
    if retained > 0 and kind not in CAT_KINDS:
        base *= 0.6
    return base


def _plan_combo(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> bool:
    target = _strongest_target(game, player)
    if target is None:
        return False
    counts = _hand_counts(player)
    pair_gain = _expected_random_card_value(game, player)
    candidates: list[tuple[float, int, str]] = []
    for kind, count in counts.items():
        if kind in (DEFUSE, EXPLODING_KITTEN):
            continue
        if not game.options.advanced_combos and kind not in CAT_KINDS:
            continue
        minimum_retained = 0 if kind in CAT_KINDS else 1
        if count >= 2 + minimum_retained:
            utility = pair_gain - 2 * _combo_spend_value(player, kind, 2)
            candidates.append((utility, 2, kind))
        if game.options.advanced_combos and count >= 3 + minimum_retained:
            request_gain = _best_request(game, player, target)[1]
            utility = request_gain - 3 * _combo_spend_value(player, kind, 3)
            candidates.append((utility, 3, kind))
    if not candidates:
        return False
    utility, size, kind = max(candidates)
    if utility < COMBO_MINIMUM_UTILITY:
        return False
    player.bot_combo_kind = "triple" if size == 3 else "pair"
    player.bot_combo_card_ids = [
        card.id for card in player.hand if card.kind == kind
    ][:size]
    return True


def _pending_action_utility(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> float:
    pending = game.pending_action
    if pending is None:
        return 0.0
    if pending.actor_id == player.id:
        return {
            ACTION_ATTACK: 8.0,
            ACTION_FAVOR: 5.0,
            ACTION_PAIR: 5.0,
            ACTION_TRIPLE: 6.0,
            ACTION_SEE_FUTURE: 4.0,
            ACTION_SHUFFLE: 4.0,
            ACTION_SKIP: 3.0,
        }.get(pending.kind, 3.0)
    if pending.target_id == player.id and pending.kind in (
        ACTION_FAVOR,
        ACTION_PAIR,
        ACTION_TRIPLE,
    ):
        return -9.0
    if pending.kind == ACTION_ATTACK:
        victim = game._next_alive_after(pending.actor_id)
        return -10.0 if victim and victim.id == player.id else 1.0
    if pending.kind == ACTION_SHUFFLE:
        known = game._known_future_cards(player)
        if known:
            return 8.0 if known[0].kind == EXPLODING_KITTEN else -7.0
        return 2.5 if _estimated_draw_risk(game, player) >= 0.2 else 0.5
    if pending.kind == ACTION_SEE_FUTURE:
        return -1.0
    if pending.kind == ACTION_SKIP:
        next_player = game._next_alive_after(pending.actor_id)
        if next_player and next_player.id == player.id:
            return -4.0 * _estimated_draw_risk(game, player)
        return 0.5
    if pending.kind in (ACTION_FAVOR, ACTION_PAIR, ACTION_TRIPLE):
        return 0.75
    return 0.0


def _should_nope(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> bool:
    pending = game.pending_action
    if pending is None:
        return False
    utility = _pending_action_utility(game, player)
    nope_count = sum(card.kind == NOPE for card in player.hand)
    threshold = 1.25 if nope_count > 1 else 2.5
    if pending.nope_count % 2:
        return utility >= threshold
    return utility <= -threshold


def _least_valuable_favor_card(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> ExplodingKittensCard:
    counts = _hand_counts(player)
    known = game._known_future_cards(player)
    known_danger = bool(known and known[0].kind == EXPLODING_KITTEN)

    def give_cost(card) -> tuple[float, int]:
        value = _card_value(player, card.kind)
        if counts[card.kind] >= 2 and (
            game.options.advanced_combos or card.kind in CAT_KINDS
        ):
            value += 5.0
        if known_danger and card.kind in (ATTACK, SKIP, SHUFFLE):
            value += 20.0
        return value, card.id

    return min(player.hand, key=give_cost)


def _reinsert_action(game: "ExplodingKittensGame") -> str:
    if not game.deck:
        return "insert_0"
    ideal = min(len(game.deck), max(0, game.turns_remaining - 1))
    roll = random.random()  # nosec B311 - mixed strategy prevents predictable placement
    if roll < 0.7:
        position = ideal
    elif roll < 0.9:
        nearby = [
            position
            for position in range(
                max(0, ideal - 1), min(len(game.deck), ideal + 1) + 1
            )
            if position != ideal
        ]
        position = random.choice(nearby) if nearby else ideal  # nosec B311
    else:
        position = random.randint(0, len(game.deck))  # nosec B311
    return f"insert_{position}"


def _normal_turn(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> str:
    known = game._known_future_cards(player)
    known_kitten = bool(known and known[0].kind == EXPLODING_KITTEN)

    if known_kitten:
        for kind in (ATTACK, SKIP, SHUFFLE):
            action = _card_action(player, kind)
            if action:
                return action
        if _plan_combo(game, player):
            return "start_combo"
        favor = _card_action(player, FAVOR)
        return favor or "draw_card"

    if known:
        if _plan_combo(game, player):
            return "start_combo"
        favor = _card_action(player, FAVOR)
        return favor or "draw_card"

    risk = _estimated_draw_risk(game, player)
    has_defuse = any(card.kind == DEFUSE for card in player.hand)
    see_threshold = 0.14 if has_defuse else 0.08
    if risk >= see_threshold:
        see_future = _card_action(player, SEE_FUTURE)
        if see_future:
            return see_future

    if _plan_combo(game, player):
        return "start_combo"
    favor = _card_action(player, FAVOR)
    if favor:
        return favor

    defense_threshold = 0.2 if has_defuse else 0.1
    if risk >= defense_threshold:
        for kind in (ATTACK, SKIP, SHUFFLE):
            action = _card_action(player, kind)
            if action:
                return action
    return "draw_card"


def bot_think(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> str | None:
    """Choose a strong legal action without consulting hidden game state."""
    if game.phase == PHASE_NOPE:
        if any(card.kind == NOPE for card in player.hand) and _should_nope(game, player):
            return "play_nope"
        return "pass_nope"

    if game.phase == PHASE_DEFUSE and player.id == game.decision_player_id:
        return "use_defuse"
    if game.phase == PHASE_REINSERT and player.id == game.decision_player_id:
        return _reinsert_action(game)

    pending = game.pending_action
    if game.phase == PHASE_TARGET and pending and pending.actor_id == player.id:
        target = _strongest_target(game, player)
        if target is None:
            return "cancel_selection"
        player.bot_planned_target_id = target.id
        return f"target_{target.id}"

    if game.phase == PHASE_REQUEST and pending and pending.actor_id == player.id:
        target = next(
            (alive for alive in game.alive_players if alive.id == pending.target_id),
            None,
        )
        if target is None:
            return "cancel_selection"
        kind, _ = _best_request(game, player, target)
        player.bot_requested_kind = kind
        return f"request_{kind}"

    if game.phase == PHASE_FAVOR_GIVE and pending and pending.target_id == player.id:
        if not player.hand:
            return None
        card = _least_valuable_favor_card(game, player)
        return f"play_card_{card.id}"

    if game.phase == PHASE_COMBO and game.current_player == player:
        for card_id in player.bot_combo_card_ids:
            if card_id not in player.selected_card_ids:
                return f"play_card_{card_id}"
        return "confirm_combo"

    if game.phase == PHASE_NORMAL and game.current_player == player:
        return _normal_turn(game, player)
    return None
