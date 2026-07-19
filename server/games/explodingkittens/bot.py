"""Public-information-only strategy for Exploding Kittens bots."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
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


COMBO_MINIMUM_UTILITY = 1.0


@dataclass(frozen=True)
class TurnProfile:
    """The information a strong player would use before choosing an action."""

    draw_risk: float
    effective_risk: float
    known_top_kind: str | None
    turns_remaining: int
    under_attack: bool
    defuse_count: int
    alive_count: int
    deck_size: int

    @property
    def is_duel(self) -> bool:
        return self.alive_count == 2

    @property
    def late_game(self) -> bool:
        return self.deck_size <= max(8, self.alive_count * 3)


@dataclass(frozen=True)
class ComboPlan:
    """A legal combo whose expected gain exceeds the cards it consumes."""

    utility: float
    size: int
    card_kind: str


def _hand_counts(player: "ExplodingKittensPlayer") -> Counter[str]:
    return Counter(card.kind for card in player.hand)


def _card_action(player: "ExplodingKittensPlayer", kind: str) -> str | None:
    card = next((card for card in player.hand if card.kind == kind), None)
    return f"play_card_{card.id}" if card else None


def _known_top_kind(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> str | None:
    known = game._known_future_cards(player)
    if known:
        return known[0].kind
    if 0 in game._known_kitten_positions(player).values():
        return EXPLODING_KITTEN
    return None


def _estimated_draw_risk(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> float:
    """Estimate the next draw without inspecting hidden deck contents."""
    known_top = _known_top_kind(game, player)
    if known_top is not None:
        return 1.0 if known_top == EXPLODING_KITTEN else 0.0
    if not game.deck:
        return 1.0

    known_kittens = game._known_kitten_positions(player)
    kittens_remaining = max(0, len(game.alive_players) - 1)
    unknown_kittens = max(0, kittens_remaining - len(known_kittens))
    unknown_slots = max(1, len(game.deck) - len(known_kittens))
    return min(1.0, unknown_kittens / unknown_slots)


def _turn_profile(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> TurnProfile:
    risk = _estimated_draw_risk(game, player)
    turns = max(1, game.turns_remaining)
    effective_risk = 1.0 - (1.0 - risk) ** turns
    return TurnProfile(
        draw_risk=risk,
        effective_risk=effective_risk,
        known_top_kind=_known_top_kind(game, player),
        turns_remaining=turns,
        under_attack=bool(game.attack_obligation),
        defuse_count=sum(card.kind == DEFUSE for card in player.hand),
        alive_count=len(game.alive_players),
        deck_size=len(game.deck),
    )


def _card_value(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    kind: str,
) -> float:
    """Return dynamic retention value for one card in the bot's hand."""
    profile = _turn_profile(game, player)
    counts = _hand_counts(player)
    if kind == DEFUSE:
        if counts[DEFUSE] == 0:
            value = 82.0
        elif counts[DEFUSE] == 1:
            value = 52.0
        else:
            value = 27.0
        return value + 18.0 * profile.effective_risk
    if kind == NOPE:
        return (19.0 if counts[NOPE] <= 1 else 13.0) + (4.0 if profile.is_duel else 0.0)
    if kind == ATTACK:
        return 18.0 + (14.0 if profile.under_attack else 0.0)
    if kind == SKIP:
        return 14.0 + 8.0 * profile.effective_risk
    if kind == SHUFFLE:
        return 12.0 + (10.0 if profile.known_top_kind == EXPLODING_KITTEN else 0.0)
    if kind == SEE_FUTURE:
        return 10.0 + (4.0 if profile.defuse_count == 0 else 0.0)
    if kind == FAVOR:
        return 6.0
    if kind in CAT_KINDS:
        return 2.0
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
    seen_ids: set[int] = set()
    for card in (*player.hand, *game.discard_pile, *game._known_future_cards(player)):
        if card.id in seen_ids:
            continue
        seen_ids.add(card.id)
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
    """Estimate a target's card from public counts and public play history."""
    counts = _public_unknown_counts(game, player)
    remaining = counts[kind]
    population = sum(counts.values())
    sample = min(len(target.hand), population)
    if remaining <= 0 or sample <= 0 or population <= 0:
        return 0.0
    if sample > population - remaining:
        probability = 1.0
    else:
        probability = 1.0 - comb(population - remaining, sample) / comb(population, sample)

    played = target.played_card_counts.get(kind, 0)
    if kind == DEFUSE:
        # Every player starts with one Defuse. Publicly spending it sharply lowers,
        # but cannot eliminate, the chance that the player later acquired another.
        if played == 0:
            probability = max(probability, min(0.9, 0.52 + 0.045 * sample))
        else:
            probability *= 0.55**played
    elif played:
        probability *= 0.82**played
    return min(1.0, max(0.0, probability))


def _best_request(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    target: "ExplodingKittensPlayer",
) -> tuple[str, float]:
    best_kind = REQUESTABLE_KINDS[0]
    best_utility = -1.0
    for kind in REQUESTABLE_KINDS:
        probability = _target_has_probability(game, player, target, kind)
        utility = probability * _card_value(game, player, kind)
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
        count * _card_value(game, player, kind) for kind, count in counts.items()
    ) / total


def _target_threat(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    target: "ExplodingKittensPlayer",
) -> float:
    next_player = game._next_alive_after(player.id)
    score = len(target.hand) * 1.7
    score += 9.0 * _target_has_probability(game, player, target, DEFUSE)
    score += 4.0 * _target_has_probability(game, player, target, NOPE)
    if next_player is not None and next_player.id == target.id:
        score += 2.5
    return score


def _opponent_knowledge_pressure(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> float:
    """Value of erasing opponents' publicly inferable future knowledge."""
    return max(
        (
            _target_threat(game, player, opponent)
            * min(3, len(opponent.known_future_card_ids))
            / 3.0
            for opponent in game.alive_players
            if opponent.id != player.id and opponent.known_future_card_ids
        ),
        default=0.0,
    )


def _strongest_target(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> "ExplodingKittensPlayer | None":
    targets = game._valid_targets(player)
    if not targets:
        return None
    pending_kind = game.pending_action.kind if game.pending_action else ""

    def target_score(target: "ExplodingKittensPlayer") -> tuple[float, float, int]:
        threat = _target_threat(game, player, target)
        if pending_kind == ACTION_TRIPLE:
            tactical_value = _best_request(game, player, target)[1]
        elif pending_kind == ACTION_FAVOR:
            tactical_value = threat + 5.0 / max(1, len(target.hand))
        else:
            tactical_value = threat
        return tactical_value, threat, len(target.hand)

    return max(targets, key=target_score)


def _combo_spend_value(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    kind: str,
    size: int,
) -> float:
    if kind in CAT_KINDS:
        return 1.5 * size
    retained = _hand_counts(player)[kind] - size
    per_card = _card_value(game, player, kind)
    if retained > 0:
        per_card *= 0.55
    return per_card * size


def _best_combo_plan(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> ComboPlan | None:
    targets = game._valid_targets(player)
    if not targets:
        return None
    counts = _hand_counts(player)
    pair_gain = _expected_random_card_value(game, player)
    triple_gain = max(
        _best_request(game, player, target)[1]
        + 0.12 * _target_threat(game, player, target)
        for target in targets
    )
    candidates: list[ComboPlan] = []
    for kind, count in counts.items():
        if kind in (DEFUSE, EXPLODING_KITTEN):
            continue
        if not game.options.advanced_combos and kind not in CAT_KINDS:
            continue
        if count >= 2:
            utility = pair_gain - _combo_spend_value(game, player, kind, 2)
            candidates.append(ComboPlan(utility, 2, kind))
        if game.options.advanced_combos and count >= 3:
            utility = triple_gain - _combo_spend_value(game, player, kind, 3)
            candidates.append(ComboPlan(utility, 3, kind))
    if not candidates:
        return None
    plan = max(candidates, key=lambda candidate: (candidate.utility, candidate.size))
    return plan if plan.utility >= COMBO_MINIMUM_UTILITY else None


def _apply_combo_plan(
    player: "ExplodingKittensPlayer", plan: ComboPlan
) -> None:
    player.bot_combo_kind = "triple" if plan.size == 3 else "pair"
    player.bot_combo_card_ids = [
        card.id for card in player.hand if card.kind == plan.card_kind
    ][: plan.size]


def _pending_action_effect(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> float:
    """Value to this bot if the underlying pending action resolves."""
    pending = game.pending_action
    if pending is None:
        return 0.0
    profile = _turn_profile(game, player)
    actor = game.get_player_by_id(pending.actor_id)

    if pending.actor_id == player.id:
        if pending.kind == ACTION_ATTACK:
            return 20.0 + 28.0 * profile.effective_risk
        if pending.kind == ACTION_SKIP:
            return 9.0 + 22.0 * profile.draw_risk
        if pending.kind == ACTION_SHUFFLE:
            if profile.known_top_kind == EXPLODING_KITTEN:
                return 25.0
            if profile.known_top_kind is not None:
                return -15.0
            return 2.0
        return {
            ACTION_FAVOR: 10.0,
            ACTION_PAIR: 12.0,
            ACTION_TRIPLE: 18.0,
            ACTION_SEE_FUTURE: 11.0,
        }.get(pending.kind, 4.0)

    if pending.target_id == player.id:
        if pending.kind == ACTION_TRIPLE:
            requested = pending.requested_kind
            if any(card.kind == requested for card in player.hand):
                return -_card_value(game, player, requested)
            return -1.0
        if pending.kind == ACTION_FAVOR:
            cheapest = min(
                (_card_value(game, player, card.kind) for card in player.hand),
                default=0.0,
            )
            return -(7.0 + cheapest)
        if pending.kind == ACTION_PAIR:
            average = sum(
                _card_value(game, player, card.kind) for card in player.hand
            ) / max(1, len(player.hand))
            return -(6.0 + average)

    if pending.kind == ACTION_ATTACK:
        victim = game._next_alive_after(pending.actor_id)
        if victim and victim.id == player.id:
            transferred_turns = game.turns_remaining + 2 if game.attack_obligation else 2
            return -(18.0 + transferred_turns * (8.0 + 45.0 * profile.draw_risk))
        if profile.is_duel:
            return -16.0
        return 2.0

    if pending.kind == ACTION_SHUFFLE:
        if profile.known_top_kind == EXPLODING_KITTEN:
            return 18.0
        if profile.known_top_kind is not None:
            return -14.0
        return -3.0 if profile.is_duel else 0.0

    if pending.kind == ACTION_SEE_FUTURE:
        if profile.is_duel:
            return -10.0
        actor_hand_size = len(getattr(actor, "hand", []))
        return -3.0 if actor_hand_size >= len(player.hand) else 0.0

    if pending.kind == ACTION_SKIP:
        return -8.0 if profile.is_duel else -1.0

    if pending.kind in (ACTION_FAVOR, ACTION_PAIR, ACTION_TRIPLE):
        if profile.is_duel:
            return -12.0
        return -3.0
    return 0.0


def _should_nope(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> bool:
    pending = game.pending_action
    if pending is None:
        return False
    effect = _pending_action_effect(game, player)
    gain_from_nope = effect if pending.nope_count % 2 else -effect
    nope_count = sum(card.kind == NOPE for card in player.hand)
    profile = _turn_profile(game, player)
    threshold = 5.0 if nope_count > 1 else 9.0
    if profile.is_duel:
        threshold -= 2.0
    if profile.late_game:
        threshold -= 1.5
    return gain_from_nope >= max(3.0, threshold)


def _least_valuable_favor_card(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> ExplodingKittensCard:
    counts = _hand_counts(player)
    profile = _turn_profile(game, player)

    def give_cost(card: ExplodingKittensCard) -> tuple[float, int]:
        value = _card_value(game, player, card.kind)
        combo_allowed = game.options.advanced_combos or card.kind in CAT_KINDS
        if combo_allowed and counts[card.kind] in (2, 3):
            value += 8.0
        if profile.known_top_kind == EXPLODING_KITTEN and card.kind in (
            ATTACK,
            SKIP,
            SHUFFLE,
        ):
            value += 30.0
        return value, card.id

    return min(player.hand, key=give_cost)


def _future_drawers(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> list["ExplodingKittensPlayer"]:
    alive_by_id = {alive.id: alive for alive in game.alive_players}
    if player.id not in game.turn_player_ids:
        return []
    start = game.turn_player_ids.index(player.id)
    return [
        alive_by_id[player_id]
        for offset in range(1, len(game.turn_player_ids) + 1)
        if (player_id := game.turn_player_ids[(start + offset) % len(game.turn_player_ids)])
        in alive_by_id
    ]


def _reinsert_action(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> str:
    if not game.deck:
        return "insert_0"
    own_forced_draws = max(0, game.turns_remaining - 1)
    safe_start = min(len(game.deck), own_forced_draws)
    drawers = _future_drawers(game, player)
    search_end = min(len(game.deck), safe_start + max(2, len(drawers) * 2))

    def placement_score(position: int) -> float:
        if position < own_forced_draws:
            return -1000.0
        if not drawers:
            return -float(position)
        draw_offset = position - own_forced_draws
        target = drawers[draw_offset % len(drawers)]
        if target.id == player.id:
            return -80.0 - draw_offset
        immediacy = 0.88**draw_offset
        return _target_threat(game, player, target) * immediacy

    ranked = sorted(
        range(safe_start, search_end + 1),
        key=lambda position: (placement_score(position), -position),
        reverse=True,
    )
    best = ranked[0] if ranked else safe_start
    roll = random.random()  # nosec B311 - private mixed placement prevents easy reads
    if roll < 0.8 or len(ranked) == 1:
        position = best
    elif roll < 0.95:
        position = ranked[1]
    else:
        position = random.randint(safe_start, len(game.deck))  # nosec B311
    return f"insert_{position}"


def _normal_turn(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> str:
    profile = _turn_profile(game, player)
    actions = {
        kind: _card_action(player, kind)
        for kind in (ATTACK, SKIP, SHUFFLE, SEE_FUTURE, FAVOR)
    }

    # Stacking an Attack transfers every outstanding turn plus two more.
    if profile.under_attack and actions[ATTACK]:
        return actions[ATTACK]

    if profile.known_top_kind == EXPLODING_KITTEN:
        if actions[ATTACK]:
            return actions[ATTACK]
        if actions[SKIP]:
            return actions[SKIP]
        next_player = game._next_alive_after(player.id)
        next_defuse_chance = (
            _target_has_probability(game, player, next_player, DEFUSE)
            if next_player is not None
            else 1.0
        )
        if profile.is_duel and profile.defuse_count >= 2 and next_defuse_chance < 0.35:
            return "draw_card"
        if actions[SHUFFLE]:
            return actions[SHUFFLE]
        return "draw_card"

    # Exact knowledge of a safe top card is more valuable than speculative play.
    if profile.known_top_kind is not None:
        return "draw_card"

    death_cost = 112.0 if profile.defuse_count == 0 else 32.0
    draw_score = 12.0 - profile.effective_risk * death_cost
    candidates: list[tuple[float, int, str]] = [(draw_score, 0, "draw_card")]

    if actions[SEE_FUTURE]:
        control_cards = sum(bool(actions[kind]) for kind in (ATTACK, SKIP, SHUFFLE))
        information = profile.draw_risk * (1.0 - profile.draw_risk) * death_cost * 2.4
        score = information + 1.8 * control_cards - 0.32 * _card_value(
            game, player, SEE_FUTURE
        )
        candidates.append((score, 5, actions[SEE_FUTURE]))

    if actions[ATTACK]:
        next_player = game._next_alive_after(player.id)
        next_risk = (
            _estimated_draw_risk(game, next_player)
            if next_player is not None
            else profile.draw_risk
        )
        transferred_turns = profile.turns_remaining + 2 if profile.under_attack else 2
        score = (
            4.5
            + profile.effective_risk * death_cost
            + transferred_turns * next_risk * 12.0
            - 0.34 * _card_value(game, player, ATTACK)
        )
        candidates.append((score, 4, actions[ATTACK]))

    if actions[SKIP]:
        score = (
            profile.draw_risk * death_cost
            + (5.0 if profile.turns_remaining == 1 else 1.0)
            - 0.34 * _card_value(game, player, SKIP)
        )
        candidates.append((score, 3, actions[SKIP]))

    if actions[SHUFFLE]:
        knowledge_pressure = _opponent_knowledge_pressure(game, player)
        if knowledge_pressure > 0:
            score = (
                2.0
                + 0.8 * knowledge_pressure
                - 0.28 * _card_value(game, player, SHUFFLE)
                - 0.3 * profile.effective_risk * death_cost
            )
            candidates.append((score, 3, actions[SHUFFLE]))

    combo_plan = _best_combo_plan(game, player)
    if combo_plan is not None:
        urgency_discount = 5.0 * profile.effective_risk
        candidates.append((combo_plan.utility - urgency_discount, 2, "start_combo"))

    if actions[FAVOR]:
        target = _strongest_target(game, player)
        if target is not None:
            score = (
                0.16 * _target_threat(game, player, target)
                + 5.0 / max(1, len(target.hand))
                - 0.35 * _card_value(game, player, FAVOR)
                - 3.0 * profile.effective_risk
            )
            candidates.append((score, 1, actions[FAVOR]))

    _, _, action = max(candidates, key=lambda candidate: (candidate[0], candidate[1]))
    if action == "start_combo" and combo_plan is not None:
        _apply_combo_plan(player, combo_plan)
    return action


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
        return _reinsert_action(game, player)

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
        held_ids = {card.id for card in player.hand}
        if not player.bot_combo_card_ids or any(
            card_id not in held_ids for card_id in player.bot_combo_card_ids
        ):
            plan = _best_combo_plan(game, player)
            if plan is None:
                return "cancel_selection"
            _apply_combo_plan(player, plan)
        for card_id in player.bot_combo_card_ids:
            if card_id not in player.selected_card_ids:
                return f"play_card_{card_id}"
        return "confirm_combo"

    if game.phase == PHASE_NORMAL and game.current_player == player:
        return _normal_turn(game, player)
    return None
