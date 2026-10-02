"""Bot AI for Dead Man's Poker."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random
from typing import TYPE_CHECKING

from ...game_utils.cards import Card
from ...game_utils.poker_evaluator import best_hand

if TYPE_CHECKING:
    from .game import DeadMansPokerGame, DeadMansPokerPlayer


PHASE_DECISION = "decision"
PHASE_ALL_IN_RESPONSE = "all_in_response"
PHASE_SWITCH = "switch"
MAX_BULLETS = 8
STARTING_BULLETS = 1
SHOWDOWN_EQUITY_SAMPLES = 180
SWITCH_EQUITY_SAMPLES = 120
SWITCH_CHOICE_EQUITY_SAMPLES = 140


@dataclass(frozen=True)
class HandProfile:
    """Compact board-aware evaluation used by bot decisions."""

    score: tuple[int, tuple[int, ...]]
    board_score: tuple[int, tuple[int, ...]]
    category: int
    private_improves_board: bool
    private_pair: bool
    high_private: int
    board_pressure: int
    draw_potential: int
    improvement_outs: int
    opponents: int
    risk: float


@dataclass(frozen=True)
class ShowdownEquity:
    """Approximate outcome rates from visible cards only."""

    win_rate: float
    tie_rate: float

    @property
    def safe_rate(self) -> float:
        return self.win_rate + self.tie_rate


@dataclass(frozen=True)
class SwitchEvaluation:
    """Expected value of switching one private card."""

    discard_index: int
    improvement_rate: float
    category_gain_rate: float
    average_gain: float
    keeps_current_draw: bool


def bot_think(game: "DeadMansPokerGame", player: "DeadMansPokerPlayer") -> str | None:
    """Return the next legal bot action."""
    if player.eliminated or player.folded_this_hand or not player.active_in_hand:
        return None
    if game.current_player != player:
        return None

    if game.phase == PHASE_SWITCH:
        return _choose_switch_replacement(game, player)

    profile = _profile(game, player)

    if game.phase == PHASE_ALL_IN_RESPONSE:
        if _should_match_all_in(game, player, profile):
            return "call"
        return "fold"

    if game.phase != PHASE_DECISION:
        return None

    if _should_use_switch(game, player, profile):
        return "switch_card"

    if _should_use_coward_fold(game, player, profile):
        return "fold"

    if _should_all_in(game, player, profile):
        return "all_in"

    if _should_fold(game, player, profile):
        return "fold"
    return "call"


def bot_record_switch_result(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    discarded: Card | None,
    chosen: Card | None,
) -> None:
    """Record bot-only switch outcome context for later mixed decisions."""
    if not player.is_bot:
        return
    if player.bot_switch_round_stage <= 0:
        player.bot_switch_round_stage = game.round_stage
    if not player.bot_switch_plan:
        before_hand = _reconstruct_pre_switch_hand(player.hand, discarded, chosen)
        before_profile = _profile_for_cards(game, player, before_hand)
        player.bot_switch_plan = _fallback_switch_plan(before_profile)
    profile = _profile(game, player)
    player.bot_switch_missed = _switch_result_missed_plan(player.bot_switch_plan, profile)


def bot_select_switch_card(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    options: list[str],
) -> str | None:
    """Choose which private card to switch."""
    if not options or len(player.hand) < 2:
        return options[0] if options else None
    evaluation = _best_switch_evaluation(game, player, options=options)
    if evaluation:
        return str(evaluation.discard_index)

    # Fallback for malformed test states with no sensible probability sample.
    community = game.revealed_community_cards
    best_option = options[0]
    best_keep_value: tuple = (-1, (), -1, -1)
    for option in options:
        try:
            discard_index = int(option)
        except ValueError:
            continue
        if discard_index < 0 or discard_index >= len(player.hand):
            continue
        kept_private = [
            card for index, card in enumerate(player.hand) if index != discard_index
        ]
        keep_cards = kept_private + community
        keep_score = _score_cards(keep_cards)
        keep_value = (
            keep_score[0],
            keep_score[1],
            _draw_potential(keep_cards),
            max((_rank_value(card.rank) for card in kept_private), default=0),
        )
        if keep_value > best_keep_value:
            best_keep_value = keep_value
            best_option = option
    return best_option


def _choose_switch_replacement(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
) -> str | None:
    if game.pending_switch_player_id != player.id:
        return None
    if not game.pending_switch_candidates:
        return None
    best_index = 0
    best_value: tuple = (-1.0, -1.0, -1, (), -1, -1)
    discarded = (
        player.hand[game.pending_switch_card_index]
        if 0 <= game.pending_switch_card_index < len(player.hand)
        else None
    )
    offered_cards = list(game.pending_switch_candidates)
    unavailable_cards = offered_cards + ([discarded] if discarded else [])
    for index, candidate in enumerate(game.pending_switch_candidates):
        trial = list(player.hand)
        if 0 <= game.pending_switch_card_index < len(trial):
            trial[game.pending_switch_card_index] = candidate
        cards = trial + game.revealed_community_cards
        score = _score_cards(cards)
        equity = _estimate_showdown_equity(
            game,
            player,
            hand=trial,
            extra_known_cards=unavailable_cards,
            samples=SWITCH_CHOICE_EQUITY_SAMPLES,
            salt=f"switch-choice:{candidate.rank}:{candidate.suit}",
        )
        value = (
            equity.safe_rate,
            equity.win_rate,
            score[0],
            score[1],
            _draw_potential(cards),
            _rank_value(candidate.rank),
        )
        if value > best_value:
            best_value = value
            best_index = index
    return f"choose_switch_{best_index}"


def _should_use_switch(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    profile: HandProfile,
) -> bool:
    if player.used_switch or game.revealed_community_count >= 5:
        return False
    if profile.category >= 3 and profile.private_improves_board:
        return False
    if profile.private_pair and profile.high_private >= 11:
        return False

    evaluation = _best_switch_evaluation(game, player)
    if not evaluation:
        return False

    preflop_rescue = (
        game.revealed_community_count == 0
        and not profile.private_pair
        and profile.high_private <= 9
        and evaluation.improvement_rate >= 0.68
    )
    terrible_hand = (
        game.revealed_community_count >= 3
        and profile.category == 0
        and profile.high_private <= 10
        and profile.draw_potential <= 1
        and evaluation.improvement_rate >= 0.42
    )
    board_context_problem = (
        profile.category <= 1
        and profile.board_pressure >= 2
        and not profile.private_pair
        and evaluation.category_gain_rate >= 0.16
    )
    strategic_draw_chase = (
        profile.category <= 1
        and profile.draw_potential >= 2
        and evaluation.keeps_current_draw
        and evaluation.category_gain_rate >= 0.18
    )
    clear_upgrade_available = (
        game.revealed_community_count >= 3
        and profile.category <= 1
        and evaluation.improvement_rate >= 0.58
        and evaluation.category_gain_rate >= 0.24
    )
    if not (
        preflop_rescue
        or terrible_hand
        or board_context_problem
        or strategic_draw_chase
        or clear_upgrade_available
    ):
        return False

    chance = 0.42 if preflop_rescue else 0.64
    if terrible_hand:
        chance += 0.14
    if strategic_draw_chase:
        chance += 0.12
    if evaluation.category_gain_rate >= 0.35:
        chance += 0.08
    if game.revealed_community_count == 4:
        chance += 0.10

    if player.committed_bullets >= 5:
        chance += 0.06
    if random.random() >= min(0.92, chance):  # nosec B311
        return False

    player.bot_switch_round_stage = game.round_stage
    player.bot_switch_plan = _switch_plan_name(profile, evaluation)
    player.bot_switch_missed = False
    player.bot_switch_float_bias = random.random()  # nosec B311
    return True


def _switch_plan_name(profile: HandProfile, evaluation: SwitchEvaluation) -> str:
    if profile.draw_potential >= 2 and evaluation.keeps_current_draw:
        return "draw"
    if (
        profile.category == 0
        and profile.high_private <= 10
        and profile.draw_potential <= 1
    ):
        return "rescue"
    if profile.board_pressure >= 2 and not profile.private_pair:
        return "pressure"
    return "upgrade"


def _fallback_switch_plan(profile: HandProfile) -> str:
    if profile.draw_potential >= 2:
        return "draw"
    if profile.category == 0 and profile.high_private <= 10:
        return "rescue"
    if profile.board_pressure >= 2:
        return "pressure"
    return "upgrade"


def _switch_result_missed_plan(plan: str, profile: HandProfile) -> bool:
    if plan == "draw":
        return profile.category < 4
    if plan == "rescue":
        return (
            profile.category == 0
            and not profile.private_improves_board
            and profile.improvement_outs <= 6
        )
    if plan == "pressure":
        return profile.category <= 1 and profile.improvement_outs <= 5
    return profile.category == 0 and not profile.private_improves_board


def _missed_switch_fold_decision(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    profile: HandProfile,
) -> bool | None:
    if not player.used_switch or not player.bot_switch_missed:
        return None
    if player.bot_switch_round_stage not in {2, 3}:
        return None
    if game.round_stage not in {2, 3}:
        return None
    if profile.category >= 2:
        return False

    fold_chance = 0.50 if game.round_stage == 2 else 0.58
    if profile.draw_potential <= 1:
        fold_chance += 0.12
    if profile.improvement_outs <= 4:
        fold_chance += 0.08
    elif profile.improvement_outs >= 10:
        fold_chance -= 0.10
    if player.committed_bullets >= 4:
        fold_chance -= 0.12
    if profile.high_private >= 13:
        fold_chance -= 0.08
    if profile.board_pressure >= 3:
        fold_chance -= 0.08
    if player.bot_switch_float_bias >= 0.70:
        fold_chance -= 0.16
    elif player.bot_switch_float_bias <= 0.20:
        fold_chance += 0.08
    if player.bot_switch_plan == "draw" and profile.draw_potential >= 2:
        fold_chance -= 0.14

    fold_chance = min(0.82, max(0.24, fold_chance))
    return random.random() < fold_chance  # nosec B311


def _should_use_coward_fold(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    profile: HandProfile,
) -> bool:
    if player.used_coward_fold or player.acted_this_hand or player.switched_this_turn:
        return False
    if player.committed_bullets != 1:
        return False
    if game.revealed_community_count > 0:
        return False
    return (
        profile.category == 0
        and profile.high_private <= 9
        and random.random() < 0.16  # nosec B311
    )


def _should_match_all_in(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    profile: HandProfile,
) -> bool:
    fold_survival = _roulette_survival_chance(player.committed_bullets)
    if player.committed_bullets >= MAX_BULLETS:
        return True

    equity = _estimate_showdown_equity(game, player)
    losing_survival = _roulette_survival_chance(MAX_BULLETS)
    call_survival = equity.safe_rate + ((1.0 - equity.safe_rate) * losing_survival)

    if profile.category >= 4 and profile.private_improves_board:
        return True
    if (
        game.round_stage <= 2
        and profile.category == 0
        and profile.draw_potential == 0
        and profile.high_private <= 11
        and call_survival <= fold_survival + 0.18
    ):
        return False

    aggression_bonus = 0.0
    if profile.category >= 2 and profile.private_improves_board:
        aggression_bonus += 0.08
    if profile.category == 1 and profile.private_improves_board:
        aggression_bonus += 0.04
    if profile.draw_potential >= 2 and game.revealed_community_count < 5:
        aggression_bonus += 0.05
    if profile.improvement_outs >= 10 and game.revealed_community_count < 5:
        aggression_bonus += 0.04
    if player.committed_bullets >= 5:
        aggression_bonus += 0.03

    caution_margin = 0.08
    if player.committed_bullets >= 5:
        caution_margin = 0.02
    elif game.round_stage >= 4 or game.revealed_community_count >= 5:
        caution_margin = 0.04
    if profile.category == 0 and profile.draw_potential <= 1:
        caution_margin += 0.06
    if profile.improvement_outs <= 3 and game.revealed_community_count < 5:
        caution_margin += 0.04
    if profile.opponents >= 2:
        caution_margin += 0.04

    return call_survival + aggression_bonus >= fold_survival + caution_margin


def _should_all_in(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    profile: HandProfile,
) -> bool:
    if (
        player.switched_this_turn
        or game.round_stage < 2
        or game.revealed_community_count < 3
    ):
        return False
    if player.committed_bullets >= MAX_BULLETS:
        return False
    opponents = len(game.active_hand_players) - 1
    if opponents <= 0:
        return False
    equity = _estimate_showdown_equity(game, player)
    if profile.category >= 5 and profile.private_improves_board:
        return True
    if (
        profile.category >= 3
        and profile.private_improves_board
        and equity.win_rate >= 0.48
    ):
        return random.random() < 0.62  # nosec B311
    if (
        profile.category >= 2
        and profile.board_pressure <= 2
        and equity.win_rate >= 0.42
    ):
        return random.random() < 0.38  # nosec B311
    if (
        player.committed_bullets >= 5
        and profile.category >= 1
        and equity.safe_rate >= 0.50
    ):
        return random.random() < 0.44  # nosec B311
    if (
        profile.opponents == 1
        and profile.risk <= 0.38
        and profile.board_pressure >= 2
        and equity.safe_rate >= 0.34
        and profile.improvement_outs >= 6
        and random.random() < 0.12  # nosec B311
    ):
        return True
    return False


def _should_fold(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    profile: HandProfile,
) -> bool:
    if not player.acted_this_hand and player.committed_bullets == STARTING_BULLETS:
        return False
    if player.committed_bullets >= 5:
        return False
    if profile.category >= 2:
        return False
    if profile.category == 1 and profile.private_improves_board:
        return False
    post_switch_fold = _missed_switch_fold_decision(game, player, profile)
    if post_switch_fold is not None:
        return post_switch_fold
    if game.revealed_community_count < 3:
        return profile.category == 0 and random.random() < 0.08  # nosec B311
    if (
        profile.category == 0
        and not profile.private_improves_board
        and profile.board_pressure >= 3
        and profile.risk >= 0.38
    ):
        return random.random() < 0.30  # nosec B311
    if profile.category == 0 and profile.risk >= 0.50:
        return random.random() < 0.18  # nosec B311
    return profile.category == 0 and random.random() < 0.06  # nosec B311


def _profile(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
) -> HandProfile:
    community = game.revealed_community_cards
    full_cards = player.hand + community
    score = _score_cards(full_cards)
    board_score = _score_cards(community)
    private_ranks = [_rank_value(card.rank) for card in player.hand]
    private_pair = len(private_ranks) == 2 and private_ranks[0] == private_ranks[1]
    return HandProfile(
        score=score,
        board_score=board_score,
        category=score[0],
        private_improves_board=score > board_score,
        private_pair=private_pair,
        high_private=max(private_ranks, default=0),
        board_pressure=_board_pressure(community),
        draw_potential=_draw_potential(full_cards),
        improvement_outs=_one_card_improvement_outs(
            full_cards,
            player.known_dead_cards,
        ),
        opponents=max(0, len(game.active_hand_players) - 1),
        risk=player.committed_bullets / MAX_BULLETS,
    )


def _profile_for_cards(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    hand: list[Card],
) -> HandProfile:
    community = game.revealed_community_cards
    full_cards = hand + community
    score = _score_cards(full_cards)
    board_score = _score_cards(community)
    private_ranks = [_rank_value(card.rank) for card in hand]
    private_pair = len(private_ranks) == 2 and private_ranks[0] == private_ranks[1]
    return HandProfile(
        score=score,
        board_score=board_score,
        category=score[0],
        private_improves_board=score > board_score,
        private_pair=private_pair,
        high_private=max(private_ranks, default=0),
        board_pressure=_board_pressure(community),
        draw_potential=_draw_potential(full_cards),
        improvement_outs=_one_card_improvement_outs(
            full_cards,
            player.known_dead_cards,
        ),
        opponents=max(0, len(game.active_hand_players) - 1),
        risk=player.committed_bullets / MAX_BULLETS,
    )


def _estimate_showdown_equity(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    *,
    hand: list[Card] | None = None,
    extra_known_cards: list[Card] | None = None,
    samples: int = SHOWDOWN_EQUITY_SAMPLES,
    salt: str = "showdown-equity",
) -> ShowdownEquity:
    private_hand = list(player.hand if hand is None else hand)
    revealed = list(game.revealed_community_cards)
    needed_community = max(0, 5 - len(revealed))
    opponents = max(1, len(game.active_hand_players) - 1)
    known_cards = private_hand + revealed + player.known_dead_cards
    if extra_known_cards:
        known_cards.extend(extra_known_cards)
    deck = _unknown_standard_cards(known_cards)
    if len(deck) < needed_community + (opponents * 2):
        return ShowdownEquity(win_rate=0.0, tie_rate=0.0)

    rng = random.Random(_visible_seed(game, player, salt, hand=private_hand))
    wins = 0
    ties = 0
    for _ in range(max(1, samples)):
        pool = list(deck)
        rng.shuffle(pool)
        final_community = revealed + pool[:needed_community]
        index = needed_community
        hero_score, _best_cards = best_hand(private_hand + final_community)
        best_opponent_score: tuple[int, tuple[int, ...]] | None = None
        for _opponent in range(opponents):
            opponent_hand = pool[index : index + 2]
            index += 2
            opponent_score, _best_cards = best_hand(opponent_hand + final_community)
            if best_opponent_score is None or opponent_score > best_opponent_score:
                best_opponent_score = opponent_score
        if best_opponent_score is None or hero_score > best_opponent_score:
            wins += 1
        elif hero_score == best_opponent_score:
            ties += 1

    sample_count = max(1, samples)
    return ShowdownEquity(
        win_rate=wins / sample_count,
        tie_rate=ties / sample_count,
    )


def _best_switch_evaluation(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    *,
    options: list[str] | None = None,
) -> SwitchEvaluation | None:
    if len(player.hand) != 2:
        return None
    option_indexes: list[int] = []
    raw_options = (
        options
        if options is not None
        else [str(index) for index in range(len(player.hand))]
    )
    for option in raw_options:
        try:
            index = int(option)
        except ValueError:
            continue
        if 0 <= index < len(player.hand):
            option_indexes.append(index)
    if not option_indexes:
        return None

    community = game.revealed_community_cards
    current_cards = player.hand + community
    current_score = _score_cards(current_cards)
    current_value = _score_value(current_score)
    current_draw = _draw_potential(current_cards)
    candidate_count = game.switch_candidate_count
    deck = _unknown_standard_cards(current_cards + player.known_dead_cards)
    if candidate_count <= 0 or len(deck) < candidate_count:
        return None

    evaluations: list[SwitchEvaluation] = []
    for discard_index in option_indexes:
        kept_private = [
            card for index, card in enumerate(player.hand) if index != discard_index
        ]
        keep_cards = kept_private + community
        keeps_current_draw = bool(
            current_draw >= 2 and _draw_potential(keep_cards) >= 1
        )
        rng = random.Random(
            _visible_seed(game, player, f"switch-equity:{discard_index}")
        )
        improvements = 0
        category_gains = 0
        total_gain = 0.0
        for _ in range(SWITCH_EQUITY_SAMPLES):
            candidates = rng.sample(deck, candidate_count)
            best_score = max(
                _score_cards(kept_private + [candidate] + community)
                for candidate in candidates
            )
            if best_score > current_score:
                improvements += 1
            if best_score[0] > current_score[0]:
                category_gains += 1
            total_gain += _score_value(best_score) - current_value
        evaluations.append(
            SwitchEvaluation(
                discard_index=discard_index,
                improvement_rate=improvements / SWITCH_EQUITY_SAMPLES,
                category_gain_rate=category_gains / SWITCH_EQUITY_SAMPLES,
                average_gain=total_gain / SWITCH_EQUITY_SAMPLES,
                keeps_current_draw=keeps_current_draw,
            )
        )

    return max(
        evaluations,
        key=lambda evaluation: (
            evaluation.average_gain,
            evaluation.category_gain_rate,
            evaluation.improvement_rate,
            -evaluation.discard_index,
        ),
    )


def _reconstruct_pre_switch_hand(
    current_hand: list[Card],
    discarded: Card | None,
    chosen: Card | None,
) -> list[Card]:
    if discarded is None or chosen is None:
        return list(current_hand)
    restored = [card for card in current_hand if card.id != chosen.id]
    restored.append(discarded)
    return restored[:2]


def _unknown_standard_cards(known_cards: list[Card]) -> list[Card]:
    known = {(card.rank, card.suit) for card in known_cards}
    return [
        Card(id=(suit * 100) + rank, rank=rank, suit=suit)
        for suit in range(1, 5)
        for rank in range(1, 14)
        if (rank, suit) not in known
    ]


def _visible_seed(
    game: "DeadMansPokerGame",
    player: "DeadMansPokerPlayer",
    salt: str,
    *,
    hand: list[Card] | None = None,
) -> str:
    visible_cards = (
        list(player.hand if hand is None else hand)
        + game.revealed_community_cards
        + player.known_dead_cards
    )
    card_key = ",".join(
        f"{card.rank}:{card.suit}"
        for card in sorted(
            visible_cards,
            key=lambda card: (card.suit, card.rank),
        )
    )
    return "|".join(
        [
            salt,
            str(game.hand_number),
            str(game.round_stage),
            str(game.revealed_community_count),
            player.id,
            card_key,
            str(len(game.active_hand_players)),
        ]
    )


def _roulette_survival_chance(bullets: int) -> float:
    if bullets <= 0:
        return 1.0
    if bullets >= MAX_BULLETS:
        return 0.05
    return max(0.0, (MAX_BULLETS - bullets) / MAX_BULLETS)


def _score_value(score: tuple[int, tuple[int, ...]]) -> float:
    category, tiebreakers = score
    value = float(category * 1000)
    divisor = 15.0
    for rank in tiebreakers:
        value += rank / divisor
        divisor *= 15.0
    return value


def _one_card_improvement_outs(
    cards: list[Card],
    unavailable_cards: list[Card] | None = None,
) -> int:
    if len(cards) >= 7:
        return 0
    current_score = _score_cards(cards)
    return sum(
        1
        for candidate in _unknown_standard_cards(cards + (unavailable_cards or []))
        if _score_cards(cards + [candidate]) > current_score
    )


def _score_cards(cards) -> tuple[int, tuple[int, ...]]:
    if len(cards) >= 5:
        score, _best_cards = best_hand(cards)
        return score
    return _partial_score(cards)


def _partial_score(cards) -> tuple[int, tuple[int, ...]]:
    if len(cards) >= 5:
        score, _ = best_hand(cards)
        return score
    values = sorted((_rank_value(card.rank) for card in cards), reverse=True)
    counts = Counter(values)
    if not counts:
        return (0, ())
    grouped = sorted(
        ((count, rank) for rank, count in counts.items()),
        key=lambda item: (item[0], item[1]),
        reverse=True,
    )
    max_count = grouped[0][0]
    if max_count >= 3:
        trips = grouped[0][1]
        kickers = tuple(value for value in values if value != trips)
        return (3, (trips, *kickers))
    pairs = sum(1 for count in counts.values() if count == 2)
    if pairs >= 2:
        pair_ranks = sorted(
            [rank for rank, count in counts.items() if count == 2],
            reverse=True,
        )
        kickers = tuple(value for value in values if value not in pair_ranks)
        return (2, (*pair_ranks[:2], *kickers))
    if pairs == 1:
        pair = next(rank for rank, count in counts.items() if count == 2)
        kickers = tuple(value for value in values if value != pair)
        return (1, (pair, *kickers))
    return (0, tuple(values))


def _board_pressure(cards) -> int:
    if not cards:
        return 0
    score = _score_cards(cards)
    pressure = min(3, score[0])
    values = [_rank_value(card.rank) for card in cards]
    counts = Counter(values)
    if any(count >= 2 for count in counts.values()):
        pressure += 1
    suit_counts = Counter(card.suit for card in cards)
    max_suit = max(suit_counts.values(), default=0)
    if max_suit >= 4:
        pressure += 2
    elif max_suit >= 3:
        pressure += 1
    if _straight_draw_score(values) >= 1:
        pressure += 1
    return min(5, pressure)


def _draw_potential(cards) -> int:
    values = [_rank_value(card.rank) for card in cards]
    suit_counts = Counter(card.suit for card in cards)
    max_suit = max(suit_counts.values(), default=0)
    potential = 0
    if max_suit >= 4:
        potential += 2
    elif max_suit >= 3:
        potential += 1
    potential += _straight_draw_score(values)
    return min(4, potential)


def _straight_draw_score(values: list[int]) -> int:
    unique = set(values)
    if 14 in unique:
        unique.add(1)
    best = 0
    for low in range(1, 11):
        hits = sum(1 for value in range(low, low + 5) if value in unique)
        if hits >= 5:
            best = max(best, 2)
        elif hits == 4:
            best = max(best, 1)
    return best


def _rank_value(rank: int) -> int:
    return 14 if rank == 1 else rank
