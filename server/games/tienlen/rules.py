from __future__ import annotations

from dataclasses import dataclass

from ...game_utils.cards import Card
from .evaluator import (
    NORTHERN_VARIANT,
    SOUTHERN_VARIANT,
    TienLenCombo,
    evaluate_combo,
    get_suit_strength,
)


@dataclass(frozen=True)
class TienLenRuleSet:
    variant: str

    @property
    def opening_rank(self) -> int:
        return 3

    @property
    def opening_suit(self) -> int:
        return 4

    def evaluate(self, cards: list[Card]) -> TienLenCombo | None:
        return evaluate_combo(cards, self.variant)

    def is_two_combo(self, combo: TienLenCombo) -> bool:
        return bool(combo.cards) and all(card.rank == 2 for card in combo.cards)

    def can_lead_combo(self, combo: TienLenCombo) -> bool:
        if self.variant == SOUTHERN_VARIANT and combo.type_name == "consecutive_pairs" and combo.pair_count == 3:
            return False
        return True

    def is_special_cutter(self, combo: TienLenCombo) -> bool:
        if combo.type_name == "four_of_a_kind":
            return True
        if self.variant == SOUTHERN_VARIANT and combo.type_name == "consecutive_pairs" and combo.pair_count >= 3:
            return True
        return False

    def can_finish(self, remaining_hand: list[Card], combo: TienLenCombo) -> bool:
        if self.variant != NORTHERN_VARIANT:
            return True
        if remaining_hand and all(card.rank == 2 for card in remaining_hand):
            return False
        if not remaining_hand and any(card.rank == 2 for card in combo.cards):
            return False
        return True

    def can_bypass_pass_lock(self, current_combo: TienLenCombo, play_combo: TienLenCombo) -> bool:
        if self.variant != SOUTHERN_VARIANT:
            return False
        if not self.is_two_combo(current_combo):
            return False
        return self._beats_special(play_combo, current_combo)

    def _compare_pair_of_twos(self, play_combo: TienLenCombo, current_combo: TienLenCombo) -> bool:
        play_suits = sorted((get_suit_strength(card.suit) for card in play_combo.cards), reverse=True)
        current_suits = sorted((get_suit_strength(card.suit) for card in current_combo.cards), reverse=True)
        return play_suits > current_suits

    def _same_shape(self, play_combo: TienLenCombo, current_combo: TienLenCombo) -> bool:
        if play_combo.type_name != current_combo.type_name:
            return False
        if play_combo.card_count != current_combo.card_count:
            return False
        if play_combo.type_name == "consecutive_pairs":
            return play_combo.pair_count == current_combo.pair_count
        return True

    def _beats_same_shape_south(self, play_combo: TienLenCombo, current_combo: TienLenCombo) -> bool:
        if not self._same_shape(play_combo, current_combo):
            return False
        if play_combo.rank_strength != current_combo.rank_strength:
            return play_combo.rank_strength > current_combo.rank_strength
        return play_combo.suit_strength > current_combo.suit_strength

    def _north_structure_matches(self, play_combo: TienLenCombo, current_combo: TienLenCombo) -> bool:
        return play_combo.structure_signature == current_combo.structure_signature

    def _beats_same_shape_north(self, play_combo: TienLenCombo, current_combo: TienLenCombo) -> bool:
        if not self._same_shape(play_combo, current_combo):
            return False

        if play_combo.type_name == "pair" and play_combo.cards[0].rank == 2:
            if current_combo.cards[0].rank != 2:
                return True
            return self._compare_pair_of_twos(play_combo, current_combo)

        if not self._north_structure_matches(play_combo, current_combo):
            return False

        if play_combo.rank_strength != current_combo.rank_strength:
            return play_combo.rank_strength > current_combo.rank_strength
        return play_combo.suit_strength > current_combo.suit_strength

    def _beats_special(self, play_combo: TienLenCombo, current_combo: TienLenCombo) -> bool:
        if self.variant == NORTHERN_VARIANT:
            return (
                current_combo.type_name == "single"
                and current_combo.cards[0].rank == 2
                and play_combo.type_name == "four_of_a_kind"
            )

        if current_combo.type_name == "single" and current_combo.cards[0].rank == 2:
            return play_combo.type_name == "four_of_a_kind" or (
                play_combo.type_name == "consecutive_pairs" and play_combo.pair_count >= 3
            )

        if current_combo.type_name == "pair" and all(card.rank == 2 for card in current_combo.cards):
            return play_combo.type_name == "consecutive_pairs" and play_combo.pair_count >= 4

        if current_combo.type_name == "triple" and all(card.rank == 2 for card in current_combo.cards):
            return play_combo.type_name == "consecutive_pairs" and play_combo.pair_count >= 5

        if current_combo.type_name == "consecutive_pairs" and current_combo.pair_count == 3:
            return play_combo.type_name == "four_of_a_kind" or (
                play_combo.type_name == "consecutive_pairs" and play_combo.pair_count >= 4
            )

        if current_combo.type_name == "four_of_a_kind":
            return play_combo.type_name == "consecutive_pairs" and play_combo.pair_count >= 4

        return False

    def combo_beats(self, play_combo: TienLenCombo, current_combo: TienLenCombo) -> bool:
        if self.variant == NORTHERN_VARIANT:
            if self._beats_special(play_combo, current_combo):
                return True
            return self._beats_same_shape_north(play_combo, current_combo)

        if self._beats_special(play_combo, current_combo):
            return True
        return self._beats_same_shape_south(play_combo, current_combo)

    def validate_play(
        self,
        hand: list[Card],
        selected_cards: list[Card],
        current_combo: TienLenCombo | None,
        is_first_turn: bool,
        has_passed_this_trick: bool,
    ) -> tuple[bool, str | None, dict]:
        combo = self.evaluate(selected_cards)
        if not combo:
            return False, "tienlen-error-invalid-combo", {}

        if current_combo is None:
            if not self.can_lead_combo(combo):
                return False, "tienlen-error-cannot-lead-three-consecutive-pairs", {}
        else:
            if has_passed_this_trick and not self.can_bypass_pass_lock(current_combo, combo):
                return False, "action-not-your-turn", {}
            if not self.combo_beats(combo, current_combo):
                if combo.card_count != current_combo.card_count and combo.type_name == current_combo.type_name:
                    return False, "tienlen-error-wrong-length", {"count": current_combo.card_count}
                return False, "tienlen-error-lower-combo", {}

        if is_first_turn:
            has_opening_card = any(card.rank == self.opening_rank and card.suit == self.opening_suit for card in selected_cards)
            player_has_opening_card = any(card.rank == self.opening_rank and card.suit == self.opening_suit for card in hand)
            if player_has_opening_card and not has_opening_card:
                return False, "tienlen-error-first-turn-3s", {}

        remaining_hand = [card for card in hand if card not in selected_cards]
        if not self.can_finish(remaining_hand, combo):
            return False, "tienlen-error-cannot-finish-on-two", {}

        return True, None, {}


def get_rules(variant: str) -> TienLenRuleSet:
    if variant == NORTHERN_VARIANT:
        return TienLenRuleSet(NORTHERN_VARIANT)
    return TienLenRuleSet(SOUTHERN_VARIANT)
