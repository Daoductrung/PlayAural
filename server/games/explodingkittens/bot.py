"""Public-information-only strategy for Exploding Kittens bots."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import comb, exp
import random
from typing import TYPE_CHECKING, TypeVar

from .cards import (
    ATTACK,
    CARD_COUNTS,
    CAT_KINDS,
    DEFUSE,
    EXPLODING_KITTEN,
    FAVOR,
    NOPE,
    REQUESTABLE_KINDS,
    SEE_FUTURE_CARD_COUNT,
    SEE_FUTURE,
    SHUFFLE,
    SKIP,
    ExplodingKittensCard,
    active_defuse_count,
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


ChoiceT = TypeVar("ChoiceT")


@dataclass(frozen=True)
class NightmarePolicy:
    """Central tuning surface for the public-information bot policy."""

    late_game_min_cards: int = 8
    late_game_cards_per_player: int = 3
    mixed_action_window: float = 0.75
    mixed_action_temperature: float = 1.15
    mixed_target_window: float = 1.25
    mixed_request_window: float = 1.0
    mixed_combo_window: float = 0.75
    mixed_nope_window: float = 1.0
    mixed_favor_give_window: float = 0.25
    defuse_absent_value: float = 82.0
    defuse_single_value: float = 52.0
    defuse_multiple_value: float = 27.0
    defuse_risk_bonus: float = 18.0
    nope_scarce_value: float = 19.0
    nope_plentiful_value: float = 13.0
    nope_duel_bonus: float = 4.0
    attack_value: float = 18.0
    attack_response_bonus: float = 14.0
    skip_value: float = 14.0
    skip_risk_bonus: float = 8.0
    shuffle_value: float = 12.0
    shuffle_known_kitten_bonus: float = 10.0
    future_value: float = 10.0
    future_no_defuse_bonus: float = 4.0
    favor_value: float = 6.0
    cat_value: float = 2.0
    defuse_probability_cap: float = 0.9
    defuse_probability_floor: float = 0.52
    defuse_probability_per_card: float = 0.045
    defuse_play_decay: float = 0.55
    threat_hand_weight: float = 1.7
    threat_defuse_weight: float = 9.0
    threat_nope_weight: float = 4.0
    threat_next_player_bonus: float = 2.5
    kitten_no_defuse_bonus: float = 1.5
    kitten_control_escape_discount: float = 0.65
    kitten_nope_escape_factor: float = 0.35
    known_placement_weight: float = 1.35
    favor_small_hand_weight: float = 5.0
    cat_combo_spend_value: float = 1.5
    retained_set_value_factor: float = 0.55
    triple_threat_weight: float = 0.12
    combo_minimum_utility: float = 1.0
    own_attack_effect: float = 20.0
    own_attack_risk_effect: float = 28.0
    own_skip_effect: float = 9.0
    own_skip_risk_effect: float = 22.0
    own_shuffle_danger_effect: float = 25.0
    own_shuffle_safe_effect: float = -15.0
    own_shuffle_unknown_effect: float = 2.0
    own_favor_effect: float = 10.0
    own_pair_effect: float = 12.0
    own_triple_effect: float = 18.0
    own_future_effect: float = 11.0
    own_other_effect: float = 4.0
    missing_triple_effect: float = -1.0
    favor_target_base_effect: float = 7.0
    attack_target_base_effect: float = 18.0
    attack_turn_base_effect: float = 8.0
    attack_turn_risk_effect: float = 45.0
    stackable_attack_effect: float = 14.0
    stackable_attack_duel_bonus: float = 8.0
    attack_duel_observer_effect: float = -16.0
    attack_other_observer_effect: float = 2.0
    shuffle_danger_effect: float = 18.0
    shuffle_safe_effect: float = -14.0
    shuffle_duel_unknown_effect: float = -3.0
    future_duel_effect: float = -10.0
    future_threat_effect: float = -3.0
    skip_duel_effect: float = -8.0
    skip_other_effect: float = -1.0
    steal_duel_effect: float = -12.0
    steal_other_effect: float = -3.0
    nope_scarce_threshold: float = 9.0
    nope_plentiful_threshold: float = 5.0
    nope_duel_discount: float = 2.0
    nope_late_game_discount: float = 1.5
    nope_minimum_threshold: float = 3.0
    favor_combo_protection: float = 8.0
    favor_emergency_control_protection: float = 30.0
    reinsert_knowledge_survival: float = 0.84
    reinsert_unsafe_score: float = -1000.0
    reinsert_self_score: float = -80.0
    reinsert_best_probability: float = 0.65
    reinsert_second_probability: float = 0.25
    reinsert_search_cycles: int = 2
    weaponize_defuse_probability: float = 0.35
    no_defuse_death_cost: float = 112.0
    defused_kitten_cost: float = 32.0
    draw_base_utility: float = 12.0
    future_information_weight: float = 2.4
    future_control_bonus: float = 1.8
    future_retention_cost: float = 0.32
    attack_base_utility: float = 4.5
    attack_pressure_weight: float = 12.0
    attack_retention_cost: float = 0.34
    skip_single_turn_bonus: float = 5.0
    skip_multi_turn_bonus: float = 1.0
    skip_retention_cost: float = 0.34
    shuffle_base_utility: float = 2.0
    shuffle_knowledge_weight: float = 1.0
    shuffle_retention_cost: float = 0.28
    shuffle_risk_cost: float = 0.3
    combo_urgency_cost: float = 5.0
    favor_threat_weight: float = 0.16
    favor_retention_cost: float = 0.35
    favor_risk_cost: float = 3.0

    def __post_init__(self) -> None:
        if self.mixed_action_temperature <= 0:
            raise ValueError("mixed_action_temperature must be positive")
        if min(
            self.mixed_action_window,
            self.mixed_target_window,
            self.mixed_request_window,
            self.mixed_combo_window,
            self.mixed_nope_window,
            self.mixed_favor_give_window,
        ) < 0:
            raise ValueError("mixed-strategy windows must not be negative")
        if not 0 <= self.reinsert_knowledge_survival <= 1:
            raise ValueError("reinsert_knowledge_survival must be a probability")
        if not 0 <= self.reinsert_best_probability <= 1:
            raise ValueError("reinsert_best_probability must be a probability")
        if not 0 <= self.reinsert_second_probability <= 1:
            raise ValueError("reinsert_second_probability must be a probability")
        if (
            self.reinsert_best_probability + self.reinsert_second_probability
            > 1
        ):
            raise ValueError("reinsertion choice probabilities must not exceed one")


POLICY = NightmarePolicy()


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
        return self.deck_size <= max(
            POLICY.late_game_min_cards,
            self.alive_count * POLICY.late_game_cards_per_player,
        )


@dataclass(frozen=True)
class ComboPlan:
    """A legal combo whose expected gain exceeds the cards it consumes."""

    utility: float
    size: int
    card_kind: str


def _mixed_choice(
    candidates: list[tuple[float, ChoiceT]],
    *,
    window: float | None = None,
) -> ChoiceT:
    """Sample among near-equivalent moves while preserving clear tactics.

    The utility window prevents randomness from making an objectively large
    blunder. Softmax sampling makes genuinely close choices hard to read.
    """
    utility_window = POLICY.mixed_action_window if window is None else window
    best_score = max(score for score, _ in candidates)
    viable = [
        candidate
        for candidate in candidates
        if candidate[0] >= best_score - utility_window
    ]
    if len(viable) == 1:
        return viable[0][1]
    weights = [
        exp((score - best_score) / POLICY.mixed_action_temperature)
        for score, _ in viable
    ]
    return random.choices(viable, weights=weights, k=1)[0][1]  # nosec B311


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
    return _estimated_forced_draw_risk(game, player, 1)


def _estimated_forced_draw_risk(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    turns: int,
) -> float:
    """Estimate hitting any Kitten across consecutive forced draws."""
    if turns <= 0:
        return 0.0
    if not game.deck:
        return 1.0

    draw_count = min(turns, len(game.deck))
    known_cards = game._known_future_cards(player)
    known_kittens = game._known_kitten_positions(player)
    known_positions = {
        index: card.kind
        for index, card in enumerate(known_cards)
    }
    known_positions.update(
        {position: EXPLODING_KITTEN for position in known_kittens.values()}
    )
    if any(
        position < draw_count and kind == EXPLODING_KITTEN
        for position, kind in known_positions.items()
    ):
        return 1.0

    kittens_remaining = max(0, len(game.alive_players) - 1)
    known_kitten_ids = set(known_kittens)
    known_kitten_ids.update(
        card.id for card in known_cards if card.kind == EXPLODING_KITTEN
    )
    unknown_kittens = max(0, kittens_remaining - len(known_kitten_ids))
    known_slot_count = len(known_positions)
    unknown_slots = max(0, len(game.deck) - known_slot_count)
    known_horizon_slots = sum(position < draw_count for position in known_positions)
    unknown_draws = max(0, draw_count - known_horizon_slots)
    if unknown_draws == 0 or unknown_kittens == 0:
        return 0.0
    if unknown_slots <= 0 or unknown_draws > unknown_slots - unknown_kittens:
        return 1.0
    safe_slots = unknown_slots - unknown_kittens
    return 1.0 - comb(safe_slots, unknown_draws) / comb(unknown_slots, unknown_draws)


def _turn_profile(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> TurnProfile:
    risk = _estimated_draw_risk(game, player)
    turns = max(1, game.turns_remaining)
    effective_risk = _estimated_forced_draw_risk(game, player, turns)
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
            value = POLICY.defuse_absent_value
        elif counts[DEFUSE] == 1:
            value = POLICY.defuse_single_value
        else:
            value = POLICY.defuse_multiple_value
        return value + POLICY.defuse_risk_bonus * profile.effective_risk
    if kind == NOPE:
        value = (
            POLICY.nope_scarce_value
            if counts[NOPE] <= 1
            else POLICY.nope_plentiful_value
        )
        return value + (POLICY.nope_duel_bonus if profile.is_duel else 0.0)
    if kind == ATTACK:
        return POLICY.attack_value + (
            POLICY.attack_response_bonus if profile.under_attack else 0.0
        )
    if kind == SKIP:
        return POLICY.skip_value + POLICY.skip_risk_bonus * profile.effective_risk
    if kind == SHUFFLE:
        return POLICY.shuffle_value + (
            POLICY.shuffle_known_kitten_bonus
            if profile.known_top_kind == EXPLODING_KITTEN
            else 0.0
        )
    if kind == SEE_FUTURE:
        return POLICY.future_value + (
            POLICY.future_no_defuse_bonus if profile.defuse_count == 0 else 0.0
        )
    if kind == FAVOR:
        return POLICY.favor_value
    if kind in CAT_KINDS:
        return POLICY.cat_value
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
    counts[DEFUSE] = active_defuse_count(len(game.turn_player_ids))
    seen_ids: set[int] = set()
    for card in (*player.hand, *game.discard_pile, *game._known_future_cards(player)):
        if card.id in seen_ids:
            continue
        seen_ids.add(card.id)
        counts[card.kind] -= 1
    for kind in list(counts):
        counts[kind] = max(0, counts[kind])
    return counts


def _public_unknown_population(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
) -> int:
    """Return publicly countable non-Kitten slots outside this bot's hand."""
    opponent_cards = sum(
        len(opponent.hand)
        for opponent in game.alive_players
        if opponent.id != player.id
    )
    kittens_in_deck = max(0, len(game.alive_players) - 1)
    deck_non_kittens = max(0, len(game.deck) - kittens_in_deck)
    known_non_kittens = sum(
        card.kind != EXPLODING_KITTEN
        for card in game._known_future_cards(player)
    )
    return max(0, opponent_cards + deck_non_kittens - known_non_kittens)


def _target_has_probability(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    target: "ExplodingKittensPlayer",
    kind: str,
) -> float:
    """Estimate a target's card from public counts and public play history."""
    counts = _public_unknown_counts(game, player)
    modeled_population = sum(counts.values())
    population = _public_unknown_population(game, player)
    remaining = (
        round(counts[kind] * population / modeled_population)
        if modeled_population > 0
        else 0
    )
    remaining = min(population, remaining)
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
            probability = max(
                probability,
                min(
                    POLICY.defuse_probability_cap,
                    POLICY.defuse_probability_floor
                    + POLICY.defuse_probability_per_card * sample,
                ),
            )
        else:
            probability *= POLICY.defuse_play_decay**played
    return min(1.0, max(0.0, probability))


def _best_request(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    target: "ExplodingKittensPlayer",
) -> tuple[str, float]:
    return max(
        _request_utilities(game, player, target),
        key=lambda request: request[1],
    )


def _request_utilities(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    target: "ExplodingKittensPlayer",
) -> list[tuple[str, float]]:
    return [
        (
            kind,
            _target_has_probability(game, player, target, kind)
            * _card_value(game, player, kind),
        )
        for kind in REQUESTABLE_KINDS
    ]


def _mixed_request(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    target: "ExplodingKittensPlayer",
) -> str:
    return _mixed_choice(
        [
            (utility, kind)
            for kind, utility in _request_utilities(game, player, target)
        ],
        window=POLICY.mixed_request_window,
    )


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
    score = len(target.hand) * POLICY.threat_hand_weight
    score += POLICY.threat_defuse_weight * _target_has_probability(
        game, player, target, DEFUSE
    )
    score += POLICY.threat_nope_weight * _target_has_probability(
        game, player, target, NOPE
    )
    if next_player is not None and next_player.id == target.id:
        score += POLICY.threat_next_player_bonus
    return score


def _kitten_target_value(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    target: "ExplodingKittensPlayer",
) -> float:
    """Value of making a particular opponent encounter the next Kitten."""
    defuse_probability = _target_has_probability(
        game, player, target, DEFUSE
    )
    control_probabilities = [
        _target_has_probability(game, player, target, kind)
        for kind in (ATTACK, SKIP, SHUFFLE)
    ]
    control_escape_probability = 1.0
    for probability in control_probabilities:
        control_escape_probability *= 1.0 - probability
    control_escape_probability = 1.0 - control_escape_probability
    if any(card.kind == NOPE for card in player.hand):
        control_escape_probability *= POLICY.kitten_nope_escape_factor
    vulnerability = 1.0 + (
        POLICY.kitten_no_defuse_bonus * (1.0 - defuse_probability)
    )
    control_factor = 1.0 - (
        POLICY.kitten_control_escape_discount * control_escape_probability
    )
    return _target_threat(game, player, target) * vulnerability * control_factor


def _opponent_knowledge_pressure(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> float:
    """Value of erasing opponents' publicly inferable private knowledge.

    A reinsertion is announced, so everyone fairly knows that its actor knows
    the Kitten's location even though only that actor knows the position.  We
    deliberately inspect only whether such knowledge exists, never its secret
    card id or depth.
    """
    return max(
        (
            _target_threat(game, player, opponent)
            * (
                min(
                    SEE_FUTURE_CARD_COUNT,
                    len(opponent.known_future_card_ids),
                )
                / SEE_FUTURE_CARD_COUNT
                + (
                    POLICY.known_placement_weight
                    if opponent.known_kitten_positions
                    else 0.0
                )
            )
            for opponent in game.alive_players
            if opponent.id != player.id
            and (
                opponent.known_future_card_ids
                or opponent.known_kitten_positions
            )
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

    def target_score(target: "ExplodingKittensPlayer") -> float:
        threat = _target_threat(game, player, target)
        if pending_kind == ACTION_TRIPLE:
            tactical_value = _best_request(game, player, target)[1]
        elif pending_kind == ACTION_FAVOR:
            tactical_value = threat + POLICY.favor_small_hand_weight / max(
                1, len(target.hand)
            )
        else:
            tactical_value = threat
        return tactical_value

    return _mixed_choice(
        [(target_score(target), target) for target in targets],
        window=POLICY.mixed_target_window,
    )


def _combo_spend_value(
    game: "ExplodingKittensGame",
    player: "ExplodingKittensPlayer",
    kind: str,
    size: int,
) -> float:
    if kind in CAT_KINDS:
        return POLICY.cat_combo_spend_value * size
    retained = _hand_counts(player)[kind] - size
    per_card = _card_value(game, player, kind)
    if retained > 0:
        per_card *= POLICY.retained_set_value_factor
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
        + POLICY.triple_threat_weight * _target_threat(game, player, target)
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
    viable = [
        plan
        for plan in candidates
        if plan.utility >= POLICY.combo_minimum_utility
    ]
    if not viable:
        return None
    return _mixed_choice(
        [(plan.utility, plan) for plan in viable],
        window=POLICY.mixed_combo_window,
    )


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
            return (
                POLICY.own_attack_effect
                + POLICY.own_attack_risk_effect * profile.effective_risk
            )
        if pending.kind == ACTION_SKIP:
            return (
                POLICY.own_skip_effect
                + POLICY.own_skip_risk_effect * profile.draw_risk
            )
        if pending.kind == ACTION_SHUFFLE:
            if profile.known_top_kind == EXPLODING_KITTEN:
                return POLICY.own_shuffle_danger_effect
            if profile.known_top_kind is not None:
                return POLICY.own_shuffle_safe_effect
            return POLICY.own_shuffle_unknown_effect
        return {
            ACTION_FAVOR: POLICY.own_favor_effect,
            ACTION_PAIR: POLICY.own_pair_effect,
            ACTION_TRIPLE: POLICY.own_triple_effect,
            ACTION_SEE_FUTURE: POLICY.own_future_effect,
        }.get(pending.kind, POLICY.own_other_effect)

    if pending.target_id == player.id:
        if pending.kind == ACTION_TRIPLE:
            requested = pending.requested_kind
            if any(card.kind == requested for card in player.hand):
                return -_card_value(game, player, requested)
            return POLICY.missing_triple_effect
        if pending.kind == ACTION_FAVOR:
            cheapest = min(
                (_card_value(game, player, card.kind) for card in player.hand),
                default=0.0,
            )
            return -(POLICY.favor_target_base_effect + cheapest)
        if pending.kind == ACTION_PAIR:
            # A pair steals a uniformly random card.  Nope only the expected
            # loss, rather than reacting as though the best card is certain to
            # be stolen.
            expected_loss = sum(
                _card_value(game, player, card.kind) for card in player.hand
            ) / max(1, len(player.hand))
            return -expected_loss

    if pending.kind == ACTION_ATTACK:
        victim = game._next_alive_after(pending.actor_id)
        if victim and victim.id == player.id:
            # Let the Attack resolve when it can be stacked.  Spending a Nope
            # here throws away the stronger response and gives the attacker
            # another opportunity to act.
            if any(card.kind == ATTACK for card in player.hand):
                return POLICY.stackable_attack_effect + (
                    POLICY.stackable_attack_duel_bonus if profile.is_duel else 0.0
                )
            transferred_turns = game.turns_remaining + 2 if game.attack_obligation else 2
            return -(
                POLICY.attack_target_base_effect
                + transferred_turns
                * (
                    POLICY.attack_turn_base_effect
                    + POLICY.attack_turn_risk_effect * profile.draw_risk
                )
            )
        if profile.is_duel:
            return POLICY.attack_duel_observer_effect
        return POLICY.attack_other_observer_effect

    if pending.kind == ACTION_SHUFFLE:
        if profile.known_top_kind == EXPLODING_KITTEN:
            return POLICY.shuffle_danger_effect
        if profile.known_top_kind is not None:
            return POLICY.shuffle_safe_effect
        return POLICY.shuffle_duel_unknown_effect if profile.is_duel else 0.0

    if pending.kind == ACTION_SEE_FUTURE:
        if profile.is_duel:
            return POLICY.future_duel_effect
        actor_hand_size = len(getattr(actor, "hand", []))
        return (
            POLICY.future_threat_effect
            if actor_hand_size >= len(player.hand)
            else 0.0
        )

    if pending.kind == ACTION_SKIP:
        return POLICY.skip_duel_effect if profile.is_duel else POLICY.skip_other_effect

    if pending.kind in (ACTION_FAVOR, ACTION_PAIR, ACTION_TRIPLE):
        if profile.is_duel:
            return POLICY.steal_duel_effect
        return POLICY.steal_other_effect
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
    threshold = (
        POLICY.nope_plentiful_threshold
        if nope_count > 1
        else POLICY.nope_scarce_threshold
    )
    if profile.is_duel:
        threshold -= POLICY.nope_duel_discount
    if profile.late_game:
        threshold -= POLICY.nope_late_game_discount
    effective_threshold = max(POLICY.nope_minimum_threshold, threshold)
    net_gain = gain_from_nope - effective_threshold
    return _mixed_choice(
        [(0.0, False), (net_gain, True)],
        window=POLICY.mixed_nope_window,
    )


def _least_valuable_favor_card(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> ExplodingKittensCard:
    counts = _hand_counts(player)
    profile = _turn_profile(game, player)

    def give_cost(card: ExplodingKittensCard) -> float:
        value = _card_value(game, player, card.kind)
        combo_allowed = game.options.advanced_combos or card.kind in CAT_KINDS
        if combo_allowed and counts[card.kind] in (2, 3):
            value += POLICY.favor_combo_protection
        if profile.known_top_kind == EXPLODING_KITTEN and card.kind in (
            ATTACK,
            SKIP,
            SHUFFLE,
        ):
            value += POLICY.favor_emergency_control_protection
        return value

    return _mixed_choice(
        [(-give_cost(card), card) for card in player.hand],
        window=POLICY.mixed_favor_give_window,
    )


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
    search_end = min(
        len(game.deck),
        safe_start
        + max(
            POLICY.reinsert_search_cycles,
            len(drawers) * POLICY.reinsert_search_cycles,
        ),
    )

    def placement_score(position: int) -> float:
        if position < own_forced_draws:
            return POLICY.reinsert_unsafe_score
        if not drawers:
            return -float(position)
        draw_offset = position - own_forced_draws
        target = drawers[draw_offset % len(drawers)]
        if target.id == player.id:
            return POLICY.reinsert_self_score - draw_offset
        # Deep placements are less trustworthy: every intervening turn gives
        # opponents another opportunity to Shuffle away our private knowledge.
        knowledge_survival = POLICY.reinsert_knowledge_survival**draw_offset
        return _kitten_target_value(game, player, target) * knowledge_survival

    ranked = sorted(
        range(safe_start, search_end + 1),
        key=lambda position: (placement_score(position), -position),
        reverse=True,
    )
    best = ranked[0] if ranked else safe_start
    roll = random.random()  # nosec B311 - private mixed placement prevents easy reads
    second_choice_limit = (
        POLICY.reinsert_best_probability + POLICY.reinsert_second_probability
    )
    if roll < POLICY.reinsert_best_probability or len(ranked) == 1:
        position = best
    elif roll < second_choice_limit:
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

    # With one card, Shuffle is a permutation of a singleton and changes
    # nothing.  Preserve it as combo material even when that card is known to
    # be the Kitten.
    singleton_deck = len(game.deck) == 1

    # Stacking an Attack transfers every outstanding turn plus two more.
    if profile.under_attack and actions[ATTACK] and profile.effective_risk > 0:
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
        if (
            profile.is_duel
            and profile.defuse_count >= 2
            and next_defuse_chance < POLICY.weaponize_defuse_probability
        ):
            return "draw_card"
        if actions[SHUFFLE] and not singleton_deck:
            return actions[SHUFFLE]
        return "draw_card"

    # Exact knowledge of a safe top card is more valuable than speculative play.
    if profile.known_top_kind is not None:
        return "draw_card"

    death_cost = (
        POLICY.no_defuse_death_cost
        if profile.defuse_count == 0
        else POLICY.defused_kitten_cost
    )
    draw_score = POLICY.draw_base_utility - profile.effective_risk * death_cost
    candidates: list[tuple[float, str]] = [(draw_score, "draw_card")]

    if actions[SEE_FUTURE]:
        control_cards = sum(bool(actions[kind]) for kind in (ATTACK, SKIP, SHUFFLE))
        information = (
            profile.draw_risk
            * (1.0 - profile.draw_risk)
            * death_cost
            * POLICY.future_information_weight
        )
        score = (
            information
            + POLICY.future_control_bonus * control_cards
            - POLICY.future_retention_cost
            * _card_value(game, player, SEE_FUTURE)
        )
        candidates.append((score, actions[SEE_FUTURE]))

    if actions[ATTACK]:
        next_player = game._next_alive_after(player.id)
        next_risk = (
            # The top card is shared, but another player's See the Future or
            # reinsertion depth is private.  Evaluate the transfer using only
            # this bot's information set.
            _estimated_draw_risk(game, player)
            if next_player is not None
            else profile.draw_risk
        )
        transferred_turns = profile.turns_remaining + 2 if profile.under_attack else 2
        score = (
            POLICY.attack_base_utility
            + profile.effective_risk * death_cost
            + transferred_turns * next_risk * POLICY.attack_pressure_weight
            - POLICY.attack_retention_cost * _card_value(game, player, ATTACK)
        )
        candidates.append((score, actions[ATTACK]))

    if actions[SKIP]:
        score = (
            profile.draw_risk * death_cost
            + (
                POLICY.skip_single_turn_bonus
                if profile.turns_remaining == 1
                else POLICY.skip_multi_turn_bonus
            )
            - POLICY.skip_retention_cost * _card_value(game, player, SKIP)
        )
        candidates.append((score, actions[SKIP]))

    if actions[SHUFFLE] and not singleton_deck:
        knowledge_pressure = _opponent_knowledge_pressure(game, player)
        if knowledge_pressure > 0:
            score = (
                POLICY.shuffle_base_utility
                + POLICY.shuffle_knowledge_weight * knowledge_pressure
                - POLICY.shuffle_retention_cost
                * _card_value(game, player, SHUFFLE)
                - POLICY.shuffle_risk_cost * profile.effective_risk * death_cost
            )
            candidates.append((score, actions[SHUFFLE]))

    combo_plan = _best_combo_plan(game, player)
    if combo_plan is not None:
        urgency_discount = POLICY.combo_urgency_cost * profile.effective_risk
        candidates.append((combo_plan.utility - urgency_discount, "start_combo"))

    if actions[FAVOR]:
        target = _strongest_target(game, player)
        if target is not None:
            score = (
                POLICY.favor_threat_weight
                * _target_threat(game, player, target)
                + POLICY.favor_small_hand_weight / max(1, len(target.hand))
                - POLICY.favor_retention_cost * _card_value(game, player, FAVOR)
                - POLICY.favor_risk_cost * profile.effective_risk
            )
            candidates.append((score, actions[FAVOR]))

    action = _mixed_choice(candidates)
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
        kind = _mixed_request(game, player, target)
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
