"""Strategic bot evaluation for Mile by Mile."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import math
from typing import TYPE_CHECKING, Iterable

from .cards import (
    HAZARD_TO_REMEDY,
    HAZARD_TO_SAFETY,
    Card,
    CardType,
    HazardType,
    RemedyType,
    SafetyType,
)
from .player import MileByMilePlayer
from .state import RaceState

if TYPE_CHECKING:
    from .game import MileByMileGame


CardKey = tuple[str, str]


def _raw(value: str | Enum) -> str:
    """Normalize string enums for card-count keys."""
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def _card_key(card: Card) -> CardKey:
    return (_raw(card.card_type), _raw(card.value))


@dataclass(frozen=True)
class BotCardKnowledge:
    """Card counts available from public information and the bot's own hand."""

    unseen: dict[CardKey, int]
    discarded: dict[CardKey, int]
    unseen_total: int

    def unseen_count(self, card_type: str | Enum, value: str | Enum) -> int:
        return self.unseen.get((_raw(card_type), _raw(value)), 0)

    def discarded_count(self, card_type: str | Enum, value: str | Enum) -> int:
        return self.discarded.get((_raw(card_type), _raw(value)), 0)

    def probability_in_slots(
        self,
        card_type: str | Enum,
        value: str | Enum,
        slots: int,
    ) -> float:
        """Estimate whether at least one matching unseen card occupies known slots."""
        copies = self.unseen_count(card_type, value)
        population = self.unseen_total
        draws = min(max(0, slots), population)
        if copies <= 0 or population <= 0 or draws <= 0:
            return 0.0
        if copies >= population:
            return 1.0

        probability_none = 1.0
        for draw_index in range(draws):
            remaining_population = population - draw_index
            remaining_nonmatches = max(0, population - copies - draw_index)
            probability_none *= remaining_nonmatches / remaining_population
        return max(0.0, min(1.0, 1.0 - probability_none))


def build_card_knowledge(
    game: MileByMileGame,
    player: MileByMilePlayer,
) -> BotCardKnowledge:
    """Build a no-cheating card count from deck composition and visible cards."""
    attack_multiplier = 2 if game.options.rig_game == "2x_attacks" else 1
    defense_multiplier = 2 if game.options.rig_game == "2x_defenses" else 1
    composition: Counter[CardKey] = Counter()

    for distance, count in (("25", 10), ("50", 10), ("75", 10), ("100", 12), ("200", 4)):
        composition[(_raw(CardType.DISTANCE), distance)] = count
    for hazard, count in (
        (HazardType.OUT_OF_GAS, 3),
        (HazardType.FLAT_TIRE, 3),
        (HazardType.ACCIDENT, 3),
        (HazardType.SPEED_LIMIT, 4),
        (HazardType.STOP, 5),
    ):
        composition[(_raw(CardType.HAZARD), _raw(hazard))] = (
            count * attack_multiplier
        )
    for remedy, count in (
        (RemedyType.GASOLINE, 6),
        (RemedyType.SPARE_TIRE, 6),
        (RemedyType.REPAIRS, 6),
        (RemedyType.END_OF_LIMIT, 6),
        (RemedyType.ROLL, 14),
    ):
        composition[(_raw(CardType.REMEDY), _raw(remedy))] = (
            count * defense_multiplier
        )
    for safety in (
        SafetyType.EXTRA_TANK,
        SafetyType.PUNCTURE_PROOF,
        SafetyType.DRIVING_ACE,
        SafetyType.RIGHT_OF_WAY,
    ):
        composition[(_raw(CardType.SAFETY), _raw(safety))] = 1
    if game.options.karma_rule:
        composition[(_raw(CardType.SPECIAL), "false_virtue")] = 2

    visible: list[Card] = [*player.hand, *game.discard_pile, *game.protections_pile]
    for race_state in game.race_states:
        visible.extend(race_state.battle_pile)

    observed: Counter[CardKey] = Counter()
    observed_instances: set[tuple[int, CardKey]] = set()
    for card in visible:
        key = _card_key(card)
        identity = (card.id, key)
        if identity in observed_instances:
            continue
        observed_instances.add(identity)
        observed[key] += 1

    unseen = {
        key: max(0, total - observed.get(key, 0))
        for key, total in composition.items()
    }
    discarded = Counter(_card_key(card) for card in game.discard_pile)
    return BotCardKnowledge(
        unseen=unseen,
        discarded=dict(discarded),
        unseen_total=sum(unseen.values()),
    )


@dataclass(frozen=True)
class BotRaceContext:
    """Reusable strategic facts for one bot decision."""

    race_state: RaceState
    knowledge: BotCardKnowledge
    distance_needed: int
    opponent_threat: float
    finish_clinches_match: bool
    finish_delay_strength: float


class MileByMileBotStrategy:
    """Evaluate legal plays, long-term points, disruption, and hand quality."""

    def __init__(self, game: MileByMileGame) -> None:
        self.game = game

    def choose_card_action(self, player: MileByMilePlayer) -> str | None:
        """Choose the strongest legal card, or the least valuable discard."""
        if not player.hand:
            return None
        context = self._build_context(player)
        legal: list[tuple[float, int]] = []
        for slot, card in enumerate(player.hand):
            if self.game._can_play_card(player, card):
                legal.append((self.score_card(player, card, context), slot))

        if legal:
            _score, slot = max(legal, key=lambda item: (item[0], -item[1]))
        else:
            slot = max(
                range(len(player.hand)),
                key=lambda index: (
                    self.score_discard(player, player.hand[index], context),
                    -index,
                ),
            )
        return f"card_slot_{slot + 1}"

    def choose_hazard_target(
        self,
        player: MileByMilePlayer,
        card: Card,
        target_indices: Iterable[int],
    ) -> int | None:
        """Choose the opponent where this hazard has the highest expected impact."""
        context = self._build_context(player)
        targets = list(target_indices)
        if not targets:
            return None
        return max(
            targets,
            key=lambda team_index: (
                self._hazard_target_score(player, card, team_index, context),
                -team_index,
            ),
        )

    def score_card(
        self,
        player: MileByMilePlayer,
        card: Card,
        context: BotRaceContext | None = None,
    ) -> float:
        """Return the strategic utility of one legal card."""
        ctx = context or self._build_context(player)
        if card.card_type == CardType.DISTANCE:
            return self._score_distance(player, card, ctx)
        if card.card_type == CardType.REMEDY:
            return self._score_remedy(player, card, ctx)
        if card.card_type == CardType.SAFETY:
            return self._score_safety(player, card, ctx)
        if card.card_type == CardType.HAZARD:
            targets = self.game._get_valid_hazard_targets(player, card.value)
            if not targets:
                return -10_000.0
            best_target = max(
                self._hazard_target_score(player, card, target, ctx)
                for target in targets
            )
            return best_target + ctx.finish_delay_strength * 0.75
        if card.card_type == CardType.SPECIAL:
            return self._score_special(player, card, ctx)
        return 0.0

    def score_discard(
        self,
        player: MileByMilePlayer,
        card: Card,
        context: BotRaceContext | None = None,
    ) -> float:
        """Return how desirable it is to discard an otherwise dead card."""
        ctx = context or self._build_context(player)
        state = ctx.race_state
        if card.card_type == CardType.DISTANCE:
            if card.distance == 200 and state.used_200_mile_count >= 2:
                return 12_000.0
            if (
                self.game.options.only_allow_perfect_crossing
                and card.distance > ctx.distance_needed
            ):
                return 10_000.0 + card.distance
            return 3_500.0 - card.distance

        if card.card_type == CardType.REMEDY:
            remedy_frequency = {
                RemedyType.ROLL: 9_000.0,
                RemedyType.END_OF_LIMIT: 7_000.0,
                RemedyType.GASOLINE: 5_000.0,
                RemedyType.SPARE_TIRE: 5_000.0,
                RemedyType.REPAIRS: 5_000.0,
            }
            matching_hazard = next(
                (
                    hazard
                    for hazard, remedy in HAZARD_TO_REMEDY.items()
                    if remedy == card.value
                ),
                None,
            )
            future_threat = (
                ctx.knowledge.unseen_count(CardType.HAZARD, matching_hazard)
                if matching_hazard
                else 0
            )
            if matching_hazard:
                future_threat += round(
                    ctx.knowledge.discarded_count(
                        CardType.HAZARD,
                        matching_hazard,
                    )
                    * self._discard_recycle_weight()
                )
            return remedy_frequency.get(card.value, 6_000.0) - future_threat * 450.0

        if card.card_type == CardType.HAZARD:
            return 7_500.0 - self._best_hazard_target_score(player, card, ctx) * 0.25
        if card.card_type == CardType.SAFETY:
            if state.has_safety(card.value):
                return 13_000.0
            return -5_000.0
        if card.card_type == CardType.SPECIAL:
            return 11_000.0 if state.has_karma else 1_000.0
        return 5_000.0

    def _build_context(self, player: MileByMilePlayer) -> BotRaceContext:
        state = self.game.get_player_race_state(player)
        if state is None:
            state = RaceState()
        knowledge = build_card_knowledge(self.game, player)
        distance_needed = max(0, self.game.options.round_distance - state.miles)
        opponent_threat = self._opponent_finish_threat(player)
        finish_clinches = self._finish_clinches_match(player, state)
        delay_strength = self._finish_delay_strength(
            player,
            state,
            knowledge,
            distance_needed,
            opponent_threat,
            finish_clinches,
        )
        return BotRaceContext(
            race_state=state,
            knowledge=knowledge,
            distance_needed=distance_needed,
            opponent_threat=opponent_threat,
            finish_clinches_match=finish_clinches,
            finish_delay_strength=delay_strength,
        )

    def _score_distance(
        self,
        player: MileByMilePlayer,
        card: Card,
        context: BotRaceContext,
    ) -> float:
        state = context.race_state
        remaining = context.distance_needed - card.distance
        finishes = remaining <= 0
        if finishes:
            score = 13_500.0 + self._projected_finish_score(
                player,
                state,
                card,
            ) * 0.8
            if not self.game.options.only_allow_perfect_crossing and remaining == 0:
                score += 1_400.0
            if context.finish_clinches_match:
                score += 8_000.0
            score += context.opponent_threat * 6_000.0
            score -= context.finish_delay_strength * 1.8
            return score

        score = 4_800.0 + card.distance * 12.0
        score += context.opponent_threat * card.distance * 8.0
        score += context.finish_delay_strength * 0.2

        if card.distance == 200 and state.used_200_mile_count == 0:
            if self._likely_finish_without_200(player, context):
                score -= 3_200.0 * (1.0 - context.opponent_threat)

        if self.game.options.only_allow_perfect_crossing:
            if self._hand_can_make_distance(player, remaining, excluded=card):
                score += 1_500.0
            elif self.game.deck.size() <= 8:
                score -= 2_000.0
        return score

    def _score_remedy(
        self,
        player: MileByMilePlayer,
        card: Card,
        context: BotRaceContext,
    ) -> float:
        state = context.race_state
        team_bonus = 700.0 if not self.game.is_individual_mode() else 0.0
        if card.value == RemedyType.END_OF_LIMIT:
            high_miles = any(
                held.card_type == CardType.DISTANCE and held.distance > 50
                for held in player.hand
            )
            return 9_000.0 + team_bonus + (1_400.0 if high_miles else 0.0)
        if card.value == RemedyType.ROLL:
            return 12_000.0 + team_bonus

        matching_hazard = next(
            (
                hazard
                for hazard, remedy in HAZARD_TO_REMEDY.items()
                if remedy == card.value
            ),
            None,
        )
        severity = 15_000.0 if matching_hazard in state.problems else 6_000.0
        return severity + team_bonus + context.opponent_threat * 1_000.0

    def _score_safety(
        self,
        player: MileByMilePlayer,
        card: Card,
        context: BotRaceContext,
    ) -> float:
        state = context.race_state
        protected_hazards = self._hazards_for_safety(card.value)
        active_protection = any(state.has_problem(hazard) for hazard in protected_hazards)
        if active_protection:
            return 18_000.0 + context.opponent_threat * 2_000.0

        safety_count_after = len(state.safeties) + 1
        if safety_count_after == 4:
            return 18_500.0

        coup_probability = self._coup_probability(
            player,
            card.value,
            context.knowledge,
        )
        near_finish = context.distance_needed <= 200
        base = 9_000.0
        if near_finish:
            base += 10_000.0
        if context.opponent_threat >= 0.55:
            base += 3_000.0
        if self.game.deck.size() <= 8:
            base += 2_000.0

        hold_penalty = coup_probability * 8_000.0
        if context.finish_delay_strength > 0:
            hold_penalty += (
                context.finish_delay_strength * coup_probability * 2.0
            )
        return base - hold_penalty

    def _score_special(
        self,
        player: MileByMilePlayer,
        card: Card,
        context: BotRaceContext,
    ) -> float:
        if card.value != "false_virtue" or context.race_state.has_karma:
            return -10_000.0
        hazards = [held for held in player.hand if held.card_type == CardType.HAZARD]
        blocked_targets = sum(
            1
            for team_index, state in self.game.iter_teams()
            if team_index != player.team_index and state.has_karma
        )
        score = 3_000.0 + len(hazards) * 700.0 + blocked_targets * 500.0
        score += context.finish_delay_strength * 0.35
        return score

    def _best_hazard_target_score(
        self,
        player: MileByMilePlayer,
        card: Card,
        context: BotRaceContext,
    ) -> float:
        targets = self.game._get_valid_hazard_targets(player, card.value)
        if not targets:
            return 0.0
        return max(
            self._hazard_target_score(player, card, target, context)
            for target in targets
        )

    def _hazard_target_score(
        self,
        player: MileByMilePlayer,
        card: Card,
        target_index: int,
        context: BotRaceContext,
    ) -> float:
        target = self.game.race_states[target_index]
        target_remaining = max(0, self.game.options.round_distance - target.miles)
        progress = target.miles / max(1, self.game.options.round_distance)
        threat = self._state_finish_threat(target)
        score_pressure = self.game.get_team_score(target_index) / max(
            1,
            self.game.options.winning_score,
        )

        if card.value == HazardType.SPEED_LIMIT:
            impact = 2_200.0
            if target.can_play_distance():
                impact += 900.0
            if target_remaining <= 200:
                impact += 1_000.0
        else:
            impact = 3_800.0
            if target.has_any_problem():
                impact *= 0.35
            if target.can_play_distance():
                impact += 1_200.0

        matching_remedy = HAZARD_TO_REMEDY.get(card.value)
        target_slots = self._team_hand_slots(target_index)
        recovery_probability = context.knowledge.probability_in_slots(
            CardType.REMEDY,
            matching_remedy or "",
            target_slots + 2,
        )
        matching_safety = HAZARD_TO_SAFETY.get(card.value)
        coup_risk = context.knowledge.probability_in_slots(
            CardType.SAFETY,
            matching_safety or "",
            target_slots,
        )

        attacker_state = context.race_state
        if self.game.options.karma_rule and attacker_state.has_karma:
            if target.has_karma:
                return 800.0 + threat * 1_200.0 + score_pressure * 500.0
            impact -= 900.0

        return (
            impact
            + progress * 2_700.0
            + threat * 4_500.0
            + score_pressure * 1_800.0
            - recovery_probability * 1_500.0
            - coup_risk * 4_000.0
        )

    def _opponent_finish_threat(self, player: MileByMilePlayer) -> float:
        threats = [
            self._state_finish_threat(state)
            for team_index, state in self.game.iter_teams()
            if team_index != player.team_index
        ]
        return max(threats, default=0.0)

    def _state_finish_threat(self, state: RaceState) -> float:
        remaining = self.game.options.round_distance - state.miles
        if remaining <= 0:
            return 1.0
        if remaining <= 50:
            base = 0.96
        elif remaining <= 100:
            base = 0.84
        elif remaining <= 200:
            base = 0.64
        elif remaining <= 300:
            base = 0.38
        else:
            base = 0.12
        if not state.can_play_distance():
            base *= 0.42
        elif self.game._speed_limit_restricts_distance(state) and remaining > 50:
            base *= 0.75
        return base

    def _finish_clinches_match(
        self,
        player: MileByMilePlayer,
        state: RaceState,
    ) -> bool:
        team_score = self.game.get_team_score(player.team_index)
        for card in player.hand:
            if (
                card.card_type == CardType.DISTANCE
                and state.miles + card.distance >= self.game.options.round_distance
                and self.game._can_play_card(player, card)
                and team_score + self._projected_finish_score(player, state, card)
                >= self.game.options.winning_score
            ):
                return True
        return False

    def _projected_finish_score(
        self,
        player: MileByMilePlayer,
        state: RaceState,
        finishing_card: Card,
    ) -> int:
        score = self.game.options.round_distance + 400
        if self.game.deck.is_empty() and not self.game.options.reshuffle_discard_pile:
            score += 300
        if state.used_200_mile_count == 0 and finishing_card.distance != 200:
            score += 300
        safety_count = len(state.safeties)
        score += safety_count * 100
        if safety_count == 4:
            score += 300
        score += state.dirty_trick_count * 300
        if (
            not self.game.options.only_allow_perfect_crossing
            and state.miles + finishing_card.distance
            == self.game.options.round_distance
        ):
            score += 200
        if all(
            other.miles == 0
            for team_index, other in self.game.iter_teams()
            if team_index != player.team_index
        ):
            score += 500
        return score

    def _finish_delay_strength(
        self,
        player: MileByMilePlayer,
        state: RaceState,
        knowledge: BotCardKnowledge,
        distance_needed: int,
        opponent_threat: float,
        finish_clinches_match: bool,
    ) -> float:
        if (
            distance_needed <= 0
            or distance_needed > 200
            or opponent_threat >= 0.35
            or finish_clinches_match
            or self.game.deck.size() < 12
        ):
            return 0.0

        has_tempo_play = any(
            card.card_type != CardType.SAFETY
            and not (
                card.card_type == CardType.DISTANCE
                and card.distance >= distance_needed
            )
            and self.game._can_play_card(player, card)
            for card in player.hand
        )
        if not has_tempo_play:
            return 0.0

        best_coup_probability = max(
            (
                self._coup_probability(player, card.value, knowledge)
                for card in player.hand
                if card.card_type == CardType.SAFETY
                and not state.has_safety(card.value)
            ),
            default=0.0,
        )
        if best_coup_probability < 0.35:
            return 0.0
        safety_margin = best_coup_probability - 0.30
        return min(
            6_500.0,
            safety_margin * 12_000.0 * (1.0 - opponent_threat / 0.35),
        )

    def _coup_probability(
        self,
        player: MileByMilePlayer,
        safety: str,
        knowledge: BotCardKnowledge,
    ) -> float:
        own_state = self.game.get_player_race_state(player)
        if (
            self.game.options.karma_rule
            and own_state is not None
            and own_state.has_karma
        ):
            return 0.0
        hazards = self._hazards_for_safety(safety)
        remaining_hazards = sum(
            knowledge.unseen_count(CardType.HAZARD, hazard) for hazard in hazards
        )
        recycle_weight = self._discard_recycle_weight()
        recyclable_hazards = sum(
            knowledge.discarded_count(CardType.HAZARD, hazard)
            for hazard in hazards
        )
        effective_hazards = remaining_hazards + recyclable_hazards * recycle_weight
        effective_population = (
            knowledge.unseen_total
            + sum(knowledge.discarded.values()) * recycle_weight
        )
        if effective_hazards <= 0 or effective_population <= 0:
            return 0.0

        opponent_slots = sum(
            len(opponent.hand)
            for opponent in self.game.get_active_players()
            if isinstance(opponent, MileByMilePlayer)
            and opponent.team_index != player.team_index
        )
        future_exposure = min(8, max(0, self.game.deck.size() // max(1, self.game.get_num_teams())))
        draws = min(effective_population, opponent_slots + future_exposure)
        density = effective_hazards / effective_population
        probability = 1.0 - math.pow(max(0.0, 1.0 - density), draws)

        own_progress = self.game.race_states[player.team_index].miles
        opponent_progress = max(
            (
                state.miles
                for team_index, state in self.game.iter_teams()
                if team_index != player.team_index
            ),
            default=0,
        )
        if own_progress > opponent_progress:
            probability *= 1.15
        return max(0.0, min(0.95, probability))

    def _discard_recycle_weight(self) -> float:
        """Estimate whether the discard pile can return within the planning horizon."""
        if (
            not self.game.options.reshuffle_discard_pile
            or not self.game.discard_pile
        ):
            return 0.0
        turns_to_reshuffle = self.game.deck.size() / max(
            1,
            self.game.get_num_teams(),
        )
        return max(0.0, min(1.0, 1.0 - turns_to_reshuffle / 8.0))

    @staticmethod
    def _hazards_for_safety(safety: str) -> tuple[str, ...]:
        if safety == SafetyType.RIGHT_OF_WAY:
            return (HazardType.STOP, HazardType.SPEED_LIMIT)
        return tuple(
            hazard
            for hazard, matching_safety in HAZARD_TO_SAFETY.items()
            if matching_safety == safety
        )

    def _team_hand_slots(self, team_index: int) -> int:
        return sum(
            len(player.hand)
            for player in self.game.get_active_players()
            if isinstance(player, MileByMilePlayer)
            and player.team_index == team_index
        )

    def _likely_finish_without_200(
        self,
        player: MileByMilePlayer,
        context: BotRaceContext,
    ) -> bool:
        non_200_in_hand = sum(
            card.distance
            for card in player.hand
            if card.card_type == CardType.DISTANCE and card.distance < 200
        )
        if non_200_in_hand >= context.distance_needed:
            return True

        unseen_miles = sum(
            distance * context.knowledge.unseen_count(CardType.DISTANCE, str(distance))
            for distance in (25, 50, 75, 100)
        )
        expected_draws = min(8, self.game.deck.size())
        expected_miles = (
            unseen_miles * expected_draws / max(1, context.knowledge.unseen_total)
        )
        return non_200_in_hand + expected_miles >= context.distance_needed

    @staticmethod
    def _hand_can_make_distance(
        player: MileByMilePlayer,
        target: int,
        *,
        excluded: Card,
    ) -> bool:
        reachable = {0}
        skipped = False
        for card in player.hand:
            if not skipped and card is excluded:
                skipped = True
                continue
            if card.card_type != CardType.DISTANCE:
                continue
            reachable.update(
                subtotal + card.distance
                for subtotal in tuple(reachable)
                if subtotal + card.distance <= target
            )
        return target in reachable
