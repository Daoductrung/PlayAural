from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

from ...game_utils.cards import Card
from .evaluator import (
    NORTHERN_VARIANT,
    SOUTHERN_VARIANT,
    TienLenCombo,
    card_strength,
    evaluate_combo,
    get_rank_strength,
    sort_cards,
)
from .rules import get_rules

if TYPE_CHECKING:
    from .game import TienLenGame, TienLenPlayer


def _combo_key(combo: TienLenCombo) -> tuple[int, ...]:
    return tuple(sorted(card.id for card in combo.cards))


def _group_by_rank(hand: list[Card]) -> dict[int, list[Card]]:
    groups: dict[int, list[Card]] = {}
    for card in hand:
        groups.setdefault(card.rank, []).append(card)
    for cards in groups.values():
        cards.sort(key=card_strength)
    return groups


def _choose_pair(cards: list[Card], variant: str) -> list[Card] | None:
    if len(cards) < 2:
        return None
    if variant == SOUTHERN_VARIANT or cards[0].rank == 2:
        return cards[:2]
    for combo_cards in combinations(cards, 2):
        candidate = list(combo_cards)
        if evaluate_combo(candidate, variant):
            return candidate
    return None


def _generate_straights(hand: list[Card], variant: str, exact_length: int | None = None) -> list[list[Card]]:
    results: list[list[Card]] = []
    if variant == NORTHERN_VARIANT:
        by_suit: dict[int, list[Card]] = {}
        for card in sort_cards(hand):
            by_suit.setdefault(card.suit, []).append(card)
        for suit_cards in by_suit.values():
            for start in range(len(suit_cards)):
                current = [suit_cards[start]]
                for index in range(start + 1, len(suit_cards)):
                    if get_rank_strength(suit_cards[index].rank) == get_rank_strength(current[-1].rank) + 1:
                        current.append(suit_cards[index])
                        if len(current) >= 3 and (exact_length is None or len(current) == exact_length):
                            results.append(current[:])
                        if exact_length is not None and len(current) >= exact_length:
                            break
                    else:
                        break
        return results

    rank_groups = _group_by_rank(hand)
    valid_ranks = sorted(rank for rank in rank_groups if rank != 2)
    for start_index in range(len(valid_ranks)):
        chosen: list[Card] = []
        previous_strength: int | None = None
        for rank in valid_ranks[start_index:]:
            strength = get_rank_strength(rank)
            if previous_strength is not None and strength != previous_strength + 1:
                break
            chosen.append(rank_groups[rank][0])
            previous_strength = strength
            if len(chosen) >= 3 and (exact_length is None or len(chosen) == exact_length):
                results.append(chosen[:])
            if exact_length is not None and len(chosen) >= exact_length:
                break
    return results


def _generate_consecutive_pairs(hand: list[Card], exact_pairs: int | None = None) -> list[list[Card]]:
    groups = _group_by_rank(hand)
    ranks = sorted(rank for rank, cards in groups.items() if len(cards) >= 2 and rank != 2)
    results: list[list[Card]] = []
    for start_index in range(len(ranks)):
        chosen: list[Card] = []
        previous_strength: int | None = None
        pair_count = 0
        for rank in ranks[start_index:]:
            strength = get_rank_strength(rank)
            if previous_strength is not None and strength != previous_strength + 1:
                break
            chosen.extend(groups[rank][:2])
            pair_count += 1
            previous_strength = strength
            if pair_count >= 3 and (exact_pairs is None or pair_count == exact_pairs):
                results.append(chosen[:])
            if exact_pairs is not None and pair_count >= exact_pairs:
                break
    return results


def _special_targets(hand: list[Card], current_combo: TienLenCombo, variant: str) -> list[list[Card]]:
    results: list[list[Card]] = []
    groups = _group_by_rank(hand)

    if current_combo.type_name == "single" and current_combo.cards[0].rank == 2:
        for cards in groups.values():
            if len(cards) == 4:
                results.append(cards[:])
        if variant == SOUTHERN_VARIANT:
            results.extend(_generate_consecutive_pairs(hand))

    if variant == SOUTHERN_VARIANT and current_combo.type_name == "pair" and all(card.rank == 2 for card in current_combo.cards):
        results.extend(_generate_consecutive_pairs(hand, exact_pairs=4))

    if variant == SOUTHERN_VARIANT and current_combo.type_name == "triple" and all(card.rank == 2 for card in current_combo.cards):
        results.extend(_generate_consecutive_pairs(hand, exact_pairs=5))

    if variant == SOUTHERN_VARIANT and current_combo.type_name == "consecutive_pairs" and current_combo.pair_count == 3:
        for cards in groups.values():
            if len(cards) == 4:
                results.append(cards[:])
        results.extend(_generate_consecutive_pairs(hand, exact_pairs=4))

    if variant == SOUTHERN_VARIANT and current_combo.type_name == "four_of_a_kind":
        results.extend(_generate_consecutive_pairs(hand, exact_pairs=4))

    return results


def generate_candidate_combos(hand: list[Card], variant: str, current_combo: TienLenCombo | None) -> list[TienLenCombo]:
    combos: dict[tuple[int, ...], TienLenCombo] = {}

    def add(cards: list[Card]) -> None:
        combo = evaluate_combo(cards, variant)
        if combo:
            combos.setdefault(_combo_key(combo), combo)

    ordered = sort_cards(hand)
    if current_combo is None:
        for card in ordered:
            add([card])
        groups = _group_by_rank(ordered)
        for cards in groups.values():
            pair = _choose_pair(cards, variant)
            if pair:
                add(pair)
            if len(cards) >= 3:
                add(cards[:3])
            if len(cards) == 4:
                add(cards[:4])
        for straight in _generate_straights(ordered, variant):
            add(straight)
        if variant == SOUTHERN_VARIANT:
            for consecutive_pairs in _generate_consecutive_pairs(ordered):
                add(consecutive_pairs)
        return list(combos.values())

    if current_combo.type_name == "single":
        for card in ordered:
            add([card])
    elif current_combo.type_name == "pair":
        for cards in _group_by_rank(ordered).values():
            pair = _choose_pair(cards, variant)
            if pair:
                add(pair)
    elif current_combo.type_name == "triple":
        for cards in _group_by_rank(ordered).values():
            if len(cards) >= 3:
                add(cards[:3])
    elif current_combo.type_name == "four_of_a_kind":
        for cards in _group_by_rank(ordered).values():
            if len(cards) == 4:
                add(cards[:4])
    elif current_combo.type_name == "straight":
        for straight in _generate_straights(ordered, variant, exact_length=current_combo.card_count):
            add(straight)
    elif current_combo.type_name == "consecutive_pairs" and variant == SOUTHERN_VARIANT:
        for consecutive_pairs in _generate_consecutive_pairs(ordered, exact_pairs=current_combo.pair_count):
            add(consecutive_pairs)

    for special in _special_targets(ordered, current_combo, variant):
        add(special)

    rules = get_rules(variant)
    return [combo for combo in combos.values() if rules.combo_beats(combo, current_combo)]


def _combo_score(combo: TienLenCombo, current_combo: TienLenCombo | None) -> tuple[int, int, int, int]:
    special_penalty = 0
    if combo.type_name == "four_of_a_kind":
        special_penalty = 30
    elif combo.type_name == "consecutive_pairs":
        special_penalty = 20 + combo.pair_count
    elif combo.type_name == "single" and combo.cards[0].rank == 2:
        special_penalty = 15
    elif combo.type_name == "pair" and combo.cards[0].rank == 2:
        special_penalty = 18
    elif combo.type_name == "triple" and combo.cards[0].rank == 2:
        special_penalty = 22

    if current_combo is None:
        return (combo.card_count, -special_penalty, -combo.rank_strength, -combo.suit_strength)
    return (-special_penalty, -combo.card_count, -combo.rank_strength, -combo.suit_strength)


def bot_think(game: "TienLenGame", player: "TienLenPlayer") -> list[int]:
    rules = get_rules(game.options.variant)
    hand = sort_cards(player.hand)
    current_combo = game.current_combo

    candidates = generate_candidate_combos(hand, game.options.variant, current_combo)
    if not candidates:
        return []

    if game.is_first_turn:
        opening_candidates = [
            combo
            for combo in candidates
            if any(card.rank == rules.opening_rank and card.suit == rules.opening_suit for card in combo.cards)
        ]
        if opening_candidates:
            candidates = opening_candidates

    legal: list[TienLenCombo] = []
    for combo in candidates:
        is_valid, _, _ = rules.validate_play(
            hand,
            combo.cards,
            current_combo,
            game.is_first_turn,
            player.passed_this_trick,
        )
        if is_valid:
            legal.append(combo)

    if not legal:
        return []

    legal.sort(key=lambda combo: _combo_score(combo, current_combo), reverse=True)
    return [card.id for card in legal[0].cards]
