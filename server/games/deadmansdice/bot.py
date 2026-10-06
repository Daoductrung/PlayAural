"""Non-cheating probability-based bot strategy for Dead Man's Dice."""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import comb

from .constants import DIE_SIDES

PUBLIC_CLAIM_WEIGHT = 0.025
ENDANGERED_CLAIM_WEIGHT = 0.015
MAX_PUBLIC_CLAIM_EVIDENCE = 0.10
DECISION_JITTER = 0.025
NORMAL_RISK_COST = 1.0
LETHAL_RISK_COST = 1.65
NORMAL_CHALLENGE_REWARD = 1.0
LETHAL_CHALLENGE_REWARD = 1.45
CHALLENGE_CONFIDENCE_MARGIN = 0.04
SPOT_ON_CONFIDENCE_MARGIN = 0.03
ENDANGERED_SPOT_ON_REWARD = 0.45
SAFE_BLUFF_CHANCE = 0.13
LETHAL_BLUFF_CHANCE = 0.05
MIN_BLUFF_TRUTH = 0.30
MAX_BLUFF_TRUTH = 0.60
MAX_BLUFF_SCORE_GAP = 0.14
NEAR_BEST_SCORE_GAP = 0.045
NORMAL_BID_TRUTH_TARGET = 0.68
LETHAL_BID_TRUTH_TARGET = 0.78


@dataclass(frozen=True)
class BotObservation:
    """Private dice plus the public information a human opponent can inspect."""

    own_dice: tuple[int, ...]
    unknown_dice: int
    maximum_quantity: int
    ones_are_wild: bool
    poison_doses: int
    poison_limit: int
    current_quantity: int = 0
    current_face: int = 0
    bid_history: tuple[tuple[int, int, bool], ...] = ()
    bidder_poison_doses: int = 0
    opponent_poison_doses: tuple[int, ...] = ()


@dataclass(frozen=True)
class BotDecision:
    """A complete action plan so face and quantity are chosen together."""

    action: str
    quantity: int | None = None


def is_legal_bid(
    quantity: int,
    face: int,
    current_quantity: int,
    current_face: int,
    maximum_quantity: int,
) -> bool:
    """Return whether a bid strictly raises the quantity/face ladder."""

    if (
        quantity < 1
        or quantity > maximum_quantity
        or face not in range(1, DIE_SIDES + 1)
    ):
        return False
    if current_quantity == 0:
        return True
    return quantity > current_quantity or (
        quantity == current_quantity and face > current_face
    )


def bid_truth_probability(
    observation: BotObservation, quantity: int, face: int
) -> float:
    """Calculate the chance that at least ``quantity`` matching dice exist."""

    own_matches = _own_match_count(observation, face)
    needed = quantity - own_matches
    if needed <= 0:
        return 1.0
    if needed > observation.unknown_dice:
        return 0.0
    probability = _unknown_match_probability(observation.ones_are_wild, face)
    return sum(
        _binomial_probability(observation.unknown_dice, matches, probability)
        for matches in range(needed, observation.unknown_dice + 1)
    )


def perceived_truth_probability(
    observation: BotObservation, quantity: int, face: int
) -> float:
    """Temper raw odds with the table's public claims without treating them as fact."""

    probability = bid_truth_probability(observation, quantity, face)
    supporting_claims = sum(
        1
        for claimed_quantity, claimed_face, is_own_bid in observation.bid_history
        if not is_own_bid and claimed_face == face and claimed_quantity <= quantity
    )
    if not supporting_claims:
        return probability

    # A bid is weak evidence, never privileged information. A player one dose from
    # elimination has more reason to bluff, so the current claim receives less weight.
    bidder_in_danger = (
        observation.poison_limit > 0
        and observation.bidder_poison_doses >= observation.poison_limit - 1
    )
    evidence_per_claim = (
        ENDANGERED_CLAIM_WEIGHT if bidder_in_danger else PUBLIC_CLAIM_WEIGHT
    )
    evidence = min(MAX_PUBLIC_CLAIM_EVIDENCE, supporting_claims * evidence_per_claim)
    return probability + ((1.0 - probability) * evidence)


def bid_exact_probability(
    observation: BotObservation, quantity: int, face: int
) -> float:
    """Calculate the chance that exactly ``quantity`` matching dice exist."""

    own_matches = _own_match_count(observation, face)
    needed = quantity - own_matches
    if needed < 0 or needed > observation.unknown_dice:
        return 0.0
    return _binomial_probability(
        observation.unknown_dice,
        needed,
        _unknown_match_probability(observation.ones_are_wild, face),
    )


def choose_decision(observation: BotObservation) -> BotDecision:
    """Choose a complete challenge or bid from information available to players."""

    if observation.current_quantity:
        truth = perceived_truth_probability(
            observation,
            observation.current_quantity,
            observation.current_face,
        )
        falsehood = 1.0 - truth
        exact = bid_exact_probability(
            observation,
            observation.current_quantity,
            observation.current_face,
        )
        own_dose_is_lethal = (
            observation.poison_limit > 0
            and observation.poison_doses >= observation.poison_limit - 1
        )
        bidder_dose_is_lethal = (
            observation.poison_limit > 0
            and observation.bidder_poison_doses >= observation.poison_limit - 1
        )
        endangered_opponents = sum(
            observation.poison_limit > 0 and doses >= observation.poison_limit - 1
            for doses in observation.opponent_poison_doses
        )
        jitter = random.uniform(-DECISION_JITTER, DECISION_JITTER)  # nosec B311

        risk_cost = LETHAL_RISK_COST if own_dose_is_lethal else NORMAL_RISK_COST
        liar_reward = (
            LETHAL_CHALLENGE_REWARD
            if bidder_dose_is_lethal
            else NORMAL_CHALLENGE_REWARD
        )
        liar_threshold = (
            risk_cost / (risk_cost + liar_reward)
        ) + CHALLENGE_CONFIDENCE_MARGIN
        liar_margin = falsehood - liar_threshold + jitter

        spot_reward = len(observation.opponent_poison_doses) + (
            endangered_opponents * ENDANGERED_SPOT_ON_REWARD
        )
        spot_threshold = (
            risk_cost / (risk_cost + spot_reward) + SPOT_ON_CONFIDENCE_MARGIN
            if spot_reward
            else 1.0
        )
        spot_margin = exact - spot_threshold - jitter

        if spot_margin > 0.0 and spot_margin >= liar_margin:
            return BotDecision("call_spot_on")
        if liar_margin > 0.0:
            return BotDecision("call_liar")

    legal = _legal_bids(observation)
    if not legal:
        if observation.current_quantity:
            exact = bid_exact_probability(
                observation,
                observation.current_quantity,
                observation.current_face,
            )
            falsehood = 1.0 - perceived_truth_probability(
                observation,
                observation.current_quantity,
                observation.current_face,
            )
            if exact > falsehood:
                return BotDecision("call_spot_on")
        return BotDecision("call_liar")

    face, quantity = _best_bid(observation, legal)
    return BotDecision(f"bid_face_{face}", quantity)


def choose_quantity(observation: BotObservation, face: int, options: list[int]) -> int:
    """Choose a legal quantity when no precomputed action plan is available."""

    legal = [
        quantity
        for quantity in options
        if is_legal_bid(
            quantity,
            face,
            observation.current_quantity,
            observation.current_face,
            observation.maximum_quantity,
        )
    ]
    if not legal:
        raise ValueError("No legal quantity was offered to the bot.")
    return max(legal, key=lambda quantity: _bid_score(observation, quantity, face))


def _best_bid(
    observation: BotObservation,
    legal: list[tuple[int, int]],
) -> tuple[int, int]:
    scored = [(bid, _bid_score(observation, bid[1], bid[0])) for bid in legal]
    best_score = max(score for _bid, score in scored)
    own_dose_is_lethal = (
        observation.poison_limit > 0
        and observation.poison_doses >= observation.poison_limit - 1
    )
    bluff_chance = LETHAL_BLUFF_CHANCE if own_dose_is_lethal else SAFE_BLUFF_CHANCE
    if random.random() < bluff_chance:  # nosec B311
        credible_bluffs = [
            bid
            for bid, score in scored
            if MIN_BLUFF_TRUTH
            <= perceived_truth_probability(observation, bid[1], bid[0])
            <= MAX_BLUFF_TRUTH
            and score >= best_score - MAX_BLUFF_SCORE_GAP
        ]
        if credible_bluffs:
            return random.choice(credible_bluffs)  # nosec B311
    near_best = [
        bid for bid, score in scored if score >= best_score - NEAR_BEST_SCORE_GAP
    ]
    return random.choice(near_best)  # nosec B311


def _legal_bids(observation: BotObservation) -> list[tuple[int, int]]:
    return [
        (face, quantity)
        for quantity in range(1, observation.maximum_quantity + 1)
        for face in range(1, DIE_SIDES + 1)
        if is_legal_bid(
            quantity,
            face,
            observation.current_quantity,
            observation.current_face,
            observation.maximum_quantity,
        )
    ]


def _bid_score(observation: BotObservation, quantity: int, face: int) -> float:
    truth = perceived_truth_probability(observation, quantity, face)
    own_dose_is_lethal = (
        observation.poison_limit > 0
        and observation.poison_doses >= observation.poison_limit - 1
    )
    risk_target = (
        LETHAL_BID_TRUTH_TARGET if own_dose_is_lethal else NORMAL_BID_TRUTH_TARGET
    )
    confidence_score = -abs(truth - risk_target)
    pressure = quantity / max(1, observation.maximum_quantity)
    own_support = _own_match_count(observation, face) / max(
        1, len(observation.own_dice)
    )
    return confidence_score + (pressure * 0.12) + (own_support * 0.06)


def _own_match_count(observation: BotObservation, face: int) -> int:
    if observation.ones_are_wild and face != 1:
        return sum(value in {1, face} for value in observation.own_dice)
    return observation.own_dice.count(face)


def _unknown_match_probability(ones_are_wild: bool, face: int) -> float:
    if ones_are_wild and face != 1:
        return 2.0 / 6.0
    return 1.0 / 6.0


def _binomial_probability(trials: int, successes: int, probability: float) -> float:
    return (
        comb(trials, successes)
        * (probability**successes)
        * ((1.0 - probability) ** (trials - successes))
    )
