from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
import random

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import MenuOption, option_field
from ...game_utils.cards import Card, DeckFactory, card_name
from ...game_utils.turn_timer_mixin import TurnTimerMixin
from ...game_utils.poker_timer import PokerTurnTimer
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

from .bot import bot_think
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


TURN_TIMER_CHOICES = ["10", "15", "20", "30", "45", "60", "90", "0"]
TURN_TIMER_LABELS = {
    "10": "tienlen-timer-10",
    "15": "tienlen-timer-15",
    "20": "tienlen-timer-20",
    "30": "tienlen-timer-30",
    "45": "tienlen-timer-45",
    "60": "tienlen-timer-60",
    "90": "tienlen-timer-90",
    "0": "tienlen-timer-unlimited",
}

VARIANT_CHOICES = [SOUTHERN_VARIANT, NORTHERN_VARIANT]
VARIANT_LABELS = {
    SOUTHERN_VARIANT: "tienlen-variant-south",
    NORTHERN_VARIANT: "tienlen-variant-north",
}

MATCH_CHOICES = ["20", "50", "100", "200"]
MATCH_LABELS = {
    "20": "tienlen-target-20",
    "50": "tienlen-target-50",
    "100": "tienlen-target-100",
    "200": "tienlen-target-200",
}

LEGACY_MATCH_TARGETS = {
    "1": 50,
    "3": 100,
    "5": 200,
}

STAKE_COINS = 10
INSTANT_WIN_PAYMENT_UNITS = {
    "tienlen-instant-dragon": 9,
    "tienlen-instant-six-consecutive-pairs": 8,
    "tienlen-instant-four-triples": 7,
    "tienlen-instant-two-four-of-a-kind": 6,
    "tienlen-instant-same-color": 5,
    "tienlen-instant-three-consecutive-triples": 5,
    "tienlen-instant-five-consecutive-pairs": 4,
    "tienlen-instant-four-twos": 3,
    "tienlen-instant-six-pairs": 2,
}
INSTANT_WIN_REASON_PRIORITY = {
    reason: units for reason, units in INSTANT_WIN_PAYMENT_UNITS.items()
}

SOUND_MUSIC = "game_ninetynine/mus.ogg"
SOUND_PLAY_SINGLE = [
    "game_cards/discard1.ogg",
    "game_cards/discard2.ogg",
    "game_cards/discard3.ogg",
]
SOUND_PLAY_MULTI = [
    "game_cards/play1.ogg",
    "game_cards/play2.ogg",
    "game_cards/play3.ogg",
    "game_cards/play4.ogg",
]
SOUND_SHUFFLE = [
    "game_cards/shuffle1.ogg",
    "game_cards/shuffle2.ogg",
    "game_cards/shuffle3.ogg",
]
SOUND_DEAL = [
    "game_cards/draw1.ogg",
    "game_cards/draw2.ogg",
    "game_cards/draw3.ogg",
    "game_cards/draw4.ogg",
]
SOUND_WIN_HAND = "game_uno/winround.ogg"
SOUND_WIN_GAME = "game_uno/wingame.ogg"
SOUND_INSTANT_WIN = "game_coup/challengesuccess.ogg"
SOUND_SPECIAL_CHOP = "game_crazyeights/hitmark.ogg"
SOUND_ELIMINATED = "game_uno/loseround.ogg"


@dataclass
class TienLenPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    selected_cards: set[int] = field(default_factory=set)
    coins: int = 0
    hand_wins: int = 0
    eliminated: bool = False
    passed_this_trick: bool = False
    passed_combo_turn: int = 0
    pass_confirm_ticks: int = 0


@dataclass
class TienLenPayment(DataClassJSONMixin):
    payer_id: str
    receiver_id: str
    amount: int


@dataclass
class TienLenOptions(GameOptions):
    variant: str = option_field(
        MenuOption(
            choices=VARIANT_CHOICES,
            choice_labels=VARIANT_LABELS,
            default=SOUTHERN_VARIANT,
            value_key="choice",
            label="tienlen-set-variant",
            prompt="tienlen-select-variant",
            change_msg="tienlen-option-changed-variant",
        )
    )
    match_length: str = option_field(
        MenuOption(
            choices=MATCH_CHOICES,
            choice_labels=MATCH_LABELS,
            default="50",
            value_key="choice",
            label="tienlen-set-coin-target",
            prompt="tienlen-select-coin-target",
            change_msg="tienlen-option-changed-coin-target",
            description="tienlen-desc-match-length",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            choice_labels=TURN_TIMER_LABELS,
            default="0",
            value_key="choice",
            label="tienlen-set-turn-timer",
            prompt="tienlen-select-turn-timer",
            change_msg="tienlen-option-changed-turn-timer",
        )
    )


@dataclass
@register_game
class TienLenGame(Game, TurnTimerMixin):
    relevant_preferences = ["confirm_destructive_actions"]

    players: list[TienLenPlayer] = field(default_factory=list)
    options: TienLenOptions = field(default_factory=TienLenOptions)
    score_unit_key = "game-score-unit-coins"

    current_combo: TienLenCombo | None = None
    trick_winner_id: str | None = None
    trick_cards: list[Card] = field(default_factory=list)
    trick_play_id: int = 0
    trick_lead_fallback_id: str | None = None
    hand_payments: list[TienLenPayment] = field(default_factory=list)
    hand_winner_id: str | None = None
    finishing_order_ids: list[str] = field(default_factory=list)
    is_first_turn: bool = True
    hand_wait_ticks: int = 0
    intro_wait_ticks: int = 0
    round: int = 0

    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._timer_warning_played = False

    @classmethod
    def get_name(cls) -> str:
        return "Tien Len"

    @classmethod
    def get_type(cls) -> str:
        return "tienlen"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> TienLenPlayer:
        return TienLenPlayer(id=player_id, name=name, is_bot=is_bot)

    def _starting_coins(self) -> int:
        if self.options.match_length in LEGACY_MATCH_TARGETS:
            return LEGACY_MATCH_TARGETS[self.options.match_length]
        return int(self.options.match_length)

    def get_score_target(self) -> int | None:
        return None

    @property
    def timer_warning_sound(self) -> str:
        return "game_crazyeights/fivesec.ogg"

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _rules(self):
        return get_rules(self.options.variant)

    def prestart_validate(self) -> list:
        errors = super().prestart_validate()
        if self.options.variant not in VARIANT_CHOICES:
            errors.append("tienlen-error-invalid-variant")
        if (
            self.options.match_length not in MATCH_CHOICES
            and self.options.match_length not in LEGACY_MATCH_TARGETS
        ):
            errors.append("tienlen-error-invalid-starting-coins")
        if self.options.turn_timer not in TURN_TIMER_CHOICES:
            errors.append("tienlen-error-invalid-turn-timer")
        return errors

    def _all_tienlen_players(self) -> list[TienLenPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, TienLenPlayer)
        ]

    def _tienlen_players(self) -> list[TienLenPlayer]:
        return [
            player
            for player in self._all_tienlen_players()
            if not player.eliminated
        ]

    def _players_still_in_hand(self) -> list[TienLenPlayer]:
        return [
            player
            for player in self._tienlen_players()
            if player.hand and player.id not in self.finishing_order_ids
        ]

    def _card_name(self, card: Card, locale: str) -> str:
        if self.options.variant != SOUTHERN_VARIANT or not locale.startswith("vi"):
            return card_name(card, locale)
        rank = Localization.get(locale, f"tienlen-south-rank-{card.rank}")
        suit = Localization.get(locale, f"tienlen-south-suit-{card.suit}")
        return Localization.get(locale, "tienlen-south-card-name", rank=rank, suit=suit)

    def _read_cards(self, cards: list[Card], locale: str) -> str:
        if not cards:
            return Localization.get(locale, "no-cards")
        names = [self._card_name(card, locale) for card in cards]
        return Localization.format_list_and(locale, names)

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.current_combo = None
        self.trick_winner_id = None
        self.trick_cards = []
        self.hand_payments = []
        self.hand_winner_id = None
        self.finishing_order_ids = []

        starting_coins = self._starting_coins()
        for player in self.get_active_players():
            if isinstance(player, TienLenPlayer):
                player.coins = starting_coins
                player.hand_wins = 0
                player.eliminated = False
                player.hand = []
                player.selected_cards.clear()
                player.passed_this_trick = False
                player.passed_combo_turn = 0
                player.pass_confirm_ticks = 0

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([player.name for player in self.get_active_players()])
        self._sync_team_scores()

        self.play_music(SOUND_MUSIC)
        self.broadcast_l("tienlen-game-start", buffer="game")
        self._start_new_hand()

    def _six_pairs(self, hand: list[Card]) -> bool:
        rank_counts = Counter(card.rank for card in hand)
        return sum(count // 2 for count in rank_counts.values()) == 6

    def _six_consecutive_pairs(self, hand: list[Card]) -> bool:
        return self._longest_consecutive_pair_run(hand) >= 6

    def _four_triples(self, hand: list[Card]) -> bool:
        return sum(1 for count in Counter(card.rank for card in hand).values() if count >= 3) >= 4

    def _two_four_of_a_kind(self, hand: list[Card]) -> bool:
        return sum(1 for count in Counter(card.rank for card in hand).values() if count == 4) >= 2

    def _same_color_instant(self, hand: list[Card]) -> bool:
        black_count = sum(1 for card in hand if card.suit in (2, 4))
        red_count = sum(1 for card in hand if card.suit in (1, 3))
        return black_count >= 12 or red_count >= 12

    def _four_twos(self, hand: list[Card]) -> bool:
        return sum(1 for card in hand if card.rank == 2) == 4

    def _dragon_sequence(self, hand: list[Card]) -> bool:
        required_ranks = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1}
        return required_ranks.issubset({card.rank for card in hand})

    def _three_consecutive_triples(self, hand: list[Card]) -> bool:
        triple_strengths = sorted(
            get_rank_strength(rank)
            for rank, count in Counter(card.rank for card in hand).items()
            if count >= 3 and rank != 2
        )
        run_length = 1
        for previous, current in zip(triple_strengths, triple_strengths[1:]):
            if current == previous + 1:
                run_length += 1
                if run_length >= 3:
                    return True
            else:
                run_length = 1
        return False

    def _five_consecutive_pairs(self, hand: list[Card]) -> bool:
        return self._longest_consecutive_pair_run(hand) >= 5

    def _longest_consecutive_pair_run(self, hand: list[Card]) -> int:
        pair_strengths = sorted(
            get_rank_strength(rank)
            for rank, count in Counter(card.rank for card in hand).items()
            if count >= 2 and rank != 2
        )
        if not pair_strengths:
            return 0
        longest = 1
        run_length = 1
        for previous, current in zip(pair_strengths, pair_strengths[1:]):
            if current == previous + 1:
                run_length += 1
                longest = max(longest, run_length)
            else:
                run_length = 1
        return longest

    def _instant_win_reason(self, player: TienLenPlayer) -> str | None:
        if self.options.variant != SOUTHERN_VARIANT:
            return None
        reason_checks = {
            "tienlen-instant-dragon": self._dragon_sequence(player.hand),
            "tienlen-instant-six-consecutive-pairs": self._six_consecutive_pairs(player.hand),
            "tienlen-instant-four-triples": self._four_triples(player.hand),
            "tienlen-instant-two-four-of-a-kind": self._two_four_of_a_kind(player.hand),
            "tienlen-instant-same-color": self._same_color_instant(player.hand),
            "tienlen-instant-three-consecutive-triples": self._three_consecutive_triples(player.hand),
            "tienlen-instant-five-consecutive-pairs": self._five_consecutive_pairs(player.hand),
            "tienlen-instant-four-twos": self._four_twos(player.hand),
            "tienlen-instant-six-pairs": self._six_pairs(player.hand),
        }
        reasons = [reason for reason, matched in reason_checks.items() if matched]
        if not reasons:
            return None
        return max(reasons, key=lambda reason: INSTANT_WIN_REASON_PRIORITY.get(reason, 0))

    def _find_instant_winner(
        self, players: list[TienLenPlayer]
    ) -> tuple[TienLenPlayer, str] | None:
        candidates: list[tuple[int, int, TienLenPlayer, str]] = []
        for player in players:
            reason_key = self._instant_win_reason(player)
            if not reason_key:
                continue
            strongest_card = max((card_strength(card) for card in player.hand), default=0)
            candidates.append(
                (
                    INSTANT_WIN_REASON_PRIORITY.get(reason_key, 0),
                    strongest_card,
                    player,
                    reason_key,
                )
            )
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        _, _, winner, reason_key = candidates[0]
        return winner, reason_key

    def _handle_instant_win(
        self,
        winner: TienLenPlayer,
        reason_key: str,
        players: list[TienLenPlayer],
    ) -> None:
        others = [player for player in players if player.id != winner.id]
        others.sort(
            key=lambda player: (
                len(player.hand),
                max((card_strength(card) for card in player.hand), default=0),
            )
        )
        self.finishing_order_ids = [winner.id] + [player.id for player in others]
        self.play_sound(SOUND_INSTANT_WIN)
        self._finish_hand(instant_winner=winner, instant_reason_key=reason_key)

    def _start_new_hand(self) -> None:
        active = self._tienlen_players()
        if len(active) <= 1:
            winner = active[0] if active else None
            if winner:
                self.play_sound(SOUND_WIN_GAME)
                self._broadcast_game_over(winner)
            self.finish_game()
            return

        self.round += 1
        self.is_first_turn = True
        self.current_combo = None
        self.trick_winner_id = None
        self.trick_cards = []
        self.trick_play_id = 0
        self.trick_lead_fallback_id = None
        self.hand_payments = []
        self.finishing_order_ids = []

        for player in self._all_tienlen_players():
            player.hand = []
            player.selected_cards.clear()
            player.passed_this_trick = False
            player.passed_combo_turn = 0
            player.pass_confirm_ticks = 0

        deck, _ = DeckFactory.standard_deck()
        deck.shuffle()
        for _ in range(13):
            for player in active:
                card = deck.draw_one()
                if card:
                    player.hand.append(card)

        rules = self._rules()
        start_player = None
        for player in active:
            player.hand = sort_cards(player.hand)
            if any(card.rank == rules.opening_rank and card.suit == rules.opening_suit for card in player.hand):
                start_player = player
                break

        if self.hand_winner_id:
            previous_winner = self.get_player_by_id(self.hand_winner_id)
            if previous_winner and previous_winner in active:
                start_player = previous_winner

        if not start_player:
            start_player = min(
                (
                    player
                    for player in active
                    if isinstance(player, TienLenPlayer) and player.hand
                ),
                key=lambda player: card_strength(player.hand[0]),
            )

        self.set_turn_players(active)
        if start_player:
            self.turn_index = self.turn_player_ids.index(start_player.id)

        self.broadcast_l("tienlen-new-hand", buffer="game", round=self.round)
        self.schedule_sound(random.choice(SOUND_SHUFFLE), 10, volume=100)
        self.schedule_sound(random.choice(SOUND_DEAL), 20, volume=100)
        self.schedule_sound(random.choice(SOUND_DEAL), 25, volume=100)

        for player in active:
            user = self.get_user(player)
            if user:
                user.speak_l("tienlen-dealt", buffer="game", cards=self._read_cards(player.hand, user.locale))

        instant = self._find_instant_winner(active)
        if instant:
            instant_winner, reason_key = instant
            self._handle_instant_win(instant_winner, reason_key, active)
            return

        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not player or not isinstance(player, TienLenPlayer):
            return

        for active_player in self._tienlen_players():
            active_player.pass_confirm_ticks = 0

        if self._finish_hand_if_ready():
            return

        if not player.hand:
            self.advance_turn(announce=False)
            self._start_turn()
            return

        if self.trick_winner_id == player.id:
            self._clear_current_trick()
        elif self._all_available_players_passed():
            self._lead_after_unbeaten_combo()
            return

        if player.passed_this_trick and not self._can_passed_player_act_on_current_combo(player):
            self.advance_turn(announce=False)
            self._start_turn()
            return

        self.announce_turn()
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(18, 30))
        self.start_turn_timer()
        self.refresh_menus()

    def _all_available_players_passed(self) -> bool:
        if self.current_combo is None:
            return False
        remaining = self._players_still_in_hand()
        if not remaining:
            return False
        if self.trick_winner_id in {player.id for player in remaining}:
            eligible = [player for player in remaining if player.id != self.trick_winner_id]
        else:
            eligible = remaining
        return bool(eligible) and all(
            self._has_player_declined_current_combo(player) for player in eligible
        )

    def _has_current_chop_window(self) -> bool:
        return (
            self.options.variant == SOUTHERN_VARIANT
            and self.current_combo is not None
            and self._rules().has_chop_window(self.current_combo)
        )

    def _has_player_declined_current_combo(self, player: TienLenPlayer) -> bool:
        if self.current_combo is None:
            return False
        if self._has_current_chop_window():
            return self.trick_play_id > 0 and player.passed_combo_turn == self.trick_play_id
        return player.passed_this_trick

    def _can_passed_player_act_on_current_combo(self, player: TienLenPlayer) -> bool:
        return (
            self._has_current_chop_window()
            and not self._has_player_declined_current_combo(player)
        )

    def _ensure_trick_play_marker(self) -> None:
        if self.current_combo is not None and self.trick_play_id <= 0:
            self.trick_play_id = 1

    def _clear_current_trick(self) -> None:
        self.current_combo = None
        self.trick_cards = []
        self.trick_winner_id = None
        self.trick_play_id = 0
        self.trick_lead_fallback_id = None
        for active_player in self._tienlen_players():
            active_player.passed_this_trick = False
            active_player.passed_combo_turn = 0

    def _next_player_with_cards_after(self, player_id: str | None) -> TienLenPlayer | None:
        if not self.turn_player_ids:
            return None
        try:
            start_index = self.turn_player_ids.index(player_id or "")
        except ValueError:
            start_index = self.turn_index
        for offset in range(1, len(self.turn_player_ids) + 1):
            candidate = self.get_player_by_id(
                self.turn_player_ids[(start_index + offset) % len(self.turn_player_ids)]
            )
            if (
                isinstance(candidate, TienLenPlayer)
                and candidate.hand
                and candidate.id not in self.finishing_order_ids
                and not candidate.eliminated
            ):
                return candidate
        return None

    def _lead_after_unbeaten_combo(self) -> None:
        winner = self.get_player_by_id(self.trick_winner_id)
        leader: TienLenPlayer | None = None
        if (
            isinstance(winner, TienLenPlayer)
            and winner.id in self.turn_player_ids
            and winner.hand
            and winner.id not in self.finishing_order_ids
            and not winner.eliminated
        ):
            leader = winner
        else:
            fallback = self.get_player_by_id(self.trick_lead_fallback_id)
            if (
                isinstance(fallback, TienLenPlayer)
                and fallback.id in self.turn_player_ids
                and fallback.hand
                and fallback.id not in self.finishing_order_ids
                and not fallback.eliminated
            ):
                leader = fallback
            else:
                leader = self._next_player_with_cards_after(self.trick_winner_id)
        self._clear_current_trick()
        if leader:
            self.current_player = leader
        self._start_turn()

    def _add_hand_payment(
        self,
        payer: TienLenPlayer,
        receiver: TienLenPlayer,
        amount: int,
    ) -> None:
        if amount <= 0 or payer.id == receiver.id:
            return
        self.hand_payments.append(TienLenPayment(payer.id, receiver.id, amount))

    def _two_penalty_units(self, card: Card) -> int:
        return 2 if card.suit in (1, 3) else 1

    def _consecutive_pair_penalty_units(self, hand: list[Card]) -> int:
        pair_strengths = sorted(
            get_rank_strength(rank)
            for rank, count in Counter(card.rank for card in hand).items()
            if count >= 2 and rank != 2
        )
        if not pair_strengths:
            return 0
        units = 0
        run_length = 1
        for previous, current in zip(pair_strengths, pair_strengths[1:]):
            if current == previous + 1:
                run_length += 1
            else:
                units += self._consecutive_pair_run_units(run_length)
                run_length = 1
        units += self._consecutive_pair_run_units(run_length)
        return units

    def _consecutive_pair_run_units(self, run_length: int) -> int:
        if run_length < 3:
            return 0
        if run_length == 3:
            return 1
        if run_length == 4:
            return 4
        return run_length

    def _combo_penalty_units(self, combo: TienLenCombo) -> int:
        units = sum(self._two_penalty_units(card) for card in combo.cards if card.rank == 2)
        if combo.type_name == "four_of_a_kind":
            units += 3
        elif combo.type_name == "consecutive_pairs":
            units += self._consecutive_pair_run_units(combo.pair_count)
        return units

    def _leftover_penalty_amount(self, player: TienLenPlayer) -> int:
        units = sum(self._two_penalty_units(card) for card in player.hand if card.rank == 2)
        rank_counts = Counter(card.rank for card in player.hand)
        units += 3 * sum(1 for rank, count in rank_counts.items() if rank != 2 and count == 4)
        if self.options.variant == SOUTHERN_VARIANT:
            units += self._consecutive_pair_penalty_units(player.hand)
        return units * STAKE_COINS

    def _record_chop_payment(
        self,
        chopper: TienLenPlayer,
        chopped: TienLenPlayer,
        chopped_combo: TienLenCombo,
    ) -> None:
        amount = self._combo_penalty_units(chopped_combo) * STAKE_COINS
        if amount <= 0:
            return
        self._add_hand_payment(chopped, chopper, amount)
        self._broadcast_chop_payment(chopper, chopped, amount)

    def _add_rank_payments(self, ordered: list[TienLenPlayer]) -> None:
        if not ordered:
            return
        winner = ordered[0]
        for place, payer in enumerate(ordered[1:], 2):
            self._add_hand_payment(payer, winner, (place - 1) * STAKE_COINS)

    def _add_instant_win_payments(
        self,
        winner: TienLenPlayer,
        ordered: list[TienLenPlayer],
        reason_key: str,
    ) -> None:
        amount = INSTANT_WIN_PAYMENT_UNITS.get(reason_key, 2) * STAKE_COINS
        for player in ordered:
            if player.id != winner.id:
                self._add_hand_payment(player, winner, amount)

    def _add_leftover_penalties(
        self,
        winner: TienLenPlayer,
        ordered: list[TienLenPlayer],
    ) -> None:
        for player in ordered[1:]:
            amount = self._leftover_penalty_amount(player)
            if amount <= 0:
                continue
            self._add_hand_payment(player, winner, amount)
            self._broadcast_leftover_penalty(player, amount)

    def _settle_hand_payments(self, players: list[TienLenPlayer]) -> dict[str, int]:
        deltas = {player.id: 0 for player in players}
        balances = {player.id: player.coins for player in players}
        players_by_id = {player.id: player for player in players}
        for payment in self.hand_payments:
            payer = players_by_id.get(payment.payer_id)
            receiver = players_by_id.get(payment.receiver_id)
            if not payer or not receiver:
                continue
            paid = min(payment.amount, balances[payer.id])
            if paid <= 0:
                continue
            balances[payer.id] -= paid
            balances[receiver.id] += paid
            deltas[payer.id] -= paid
            deltas[receiver.id] += paid
        for player in players:
            player.coins = balances[player.id]
        self.hand_payments = []
        return deltas

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return

        if self.intro_wait_ticks > 0:
            self.intro_wait_ticks -= 1
            if self.intro_wait_ticks == 0:
                self._start_new_hand()
            return

        if self.hand_wait_ticks > 0:
            self.hand_wait_ticks -= 1
            if self.hand_wait_ticks == 0:
                self._start_new_hand()
            return

        for player in self._tienlen_players():
            if player.pass_confirm_ticks > 0:
                player.pass_confirm_ticks -= 1

        self.on_tick_turn_timer()
        BotHelper.on_tick(self)

    def bot_think(self, player: TienLenPlayer) -> str | None:
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return None

        ids = bot_think(self, player)
        if not ids:
            return "pass"
        player.selected_cards = set(ids)
        return "play_selected"

    def _on_turn_timeout(self) -> None:
        player = self.current_player
        if not isinstance(player, TienLenPlayer):
            return

        ids = bot_think(self, player)
        if ids:
            player.selected_cards = set(ids)
            self._action_play_selected(player, "play_selected")
            return

        if self.current_combo:
            player.pass_confirm_ticks = 1
            self._action_pass(player, "pass")

    def create_turn_action_set(self, player: TienLenPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        for card in player.hand:
            action_set.add(
                Action(
                    id=f"toggle_select_{card.id}",
                    label="",
                    handler="_action_toggle_select",
                    is_enabled="_is_card_toggle_enabled",
                    is_hidden="_is_card_toggle_hidden",
                    get_label="_get_card_label",
                    show_in_actions_menu=False,
                )
            )
        action_set.add(
            Action(
                id="play_selected",
                label="",
                handler="_action_play_selected",
                is_enabled="_is_play_selected_enabled",
                is_hidden="_is_play_selected_hidden",
                get_label="_get_play_selected_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="pass",
                label="",
                handler="_action_pass",
                is_enabled="_is_pass_enabled",
                is_hidden="_is_pass_hidden",
                get_label="_get_pass_label",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="check_trick",
                label=Localization.get(locale, "tienlen-check-trick"),
                handler="_action_check_trick",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "tienlen-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_read_hand_enabled",
                is_hidden="_is_read_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_card_counts",
                label=Localization.get(locale, "tienlen-read-card-counts"),
                handler="_action_read_card_counts",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_variant",
                label=Localization.get(locale, "tienlen-check-variant"),
                handler="_action_check_variant",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "tienlen-check-turn-timer"),
                handler="_action_check_turn_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            target_order = [
                "check_trick",
                "read_hand",
                "read_card_counts",
                "check_variant",
                "check_turn_timer",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            self._order_touch_standard_actions(action_set, target_order)

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("space", "Play Selected Cards", ["play_selected"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "Pass", ["pass"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "Check current trick", ["check_trick"], include_spectators=True)
        self.define_keybind("h", "Read your hand", ["read_hand"], include_spectators=False)
        self.define_keybind("e", "Read card counts", ["read_card_counts"], include_spectators=True)
        self.define_keybind("v", "Check variant", ["check_variant"], include_spectators=True)
        self.define_keybind("shift+t", "Turn timer", ["check_turn_timer"], include_spectators=True)

    def before_menu_build(self, player: Player) -> None:
        self._sync_turn_actions(player)

    def _sync_turn_actions(self, player: Player) -> None:
        if not isinstance(player, TienLenPlayer):
            return
        player.hand = sort_cards(player.hand)
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        turn_set.remove_by_prefix("toggle_select_")
        turn_set.remove("play_selected")
        turn_set.remove("pass")

        if self.status != "playing" or player.is_spectator:
            return
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return

        for card in player.hand:
            turn_set.add(
                Action(
                    id=f"toggle_select_{card.id}",
                    label="",
                    handler="_action_toggle_select",
                    is_enabled="_is_card_toggle_enabled",
                    is_hidden="_is_card_toggle_hidden",
                    get_label="_get_card_label",
                    show_in_actions_menu=False,
                )
            )

        if player.hand:
            turn_set.add(
                Action(
                    id="play_selected",
                    label="",
                    handler="_action_play_selected",
                    is_enabled="_is_play_selected_enabled",
                    is_hidden="_is_play_selected_hidden",
                    get_label="_get_play_selected_label",
                    show_in_actions_menu=False,
                )
            )
        if self.current_player == player:
            turn_set.add(
                Action(
                    id="pass",
                    label="",
                    handler="_action_pass",
                    is_enabled="_is_pass_enabled",
                    is_hidden="_is_pass_hidden",
                    get_label="_get_pass_label",
                    show_in_actions_menu=False,
                )
            )

    def _require_active_player(self, player: Player) -> TienLenPlayer | None:
        if not isinstance(player, TienLenPlayer):
            return None
        if player.is_spectator:
            return None
        if self.current_player != player:
            return None
        return player

    def _require_tienlen_player(self, player: Player) -> TienLenPlayer | None:
        if not isinstance(player, TienLenPlayer):
            return None
        if player.is_spectator:
            return None
        if not player.hand:
            return None
        return player

    def _selected_cards(self, player: TienLenPlayer) -> list[Card]:
        return [card for card in player.hand if card.id in player.selected_cards]

    def _opening_required_card(self, player: TienLenPlayer) -> Card | None:
        if self.hand_winner_id is not None:
            return None
        if not self.is_first_turn or self.current_combo is not None:
            return None
        rules = self._rules()
        opening_card = next(
            (
                card
                for active_player in self._tienlen_players()
                for card in active_player.hand
                if card.rank == rules.opening_rank and card.suit == rules.opening_suit
            ),
            None,
        )
        if opening_card:
            return opening_card if opening_card in player.hand else None
        return min(player.hand, key=card_strength) if player.hand else None

    def _can_play_out_of_turn_chop(
        self,
        player: TienLenPlayer,
        selected: list[Card] | None = None,
    ) -> bool:
        if self.current_player == player:
            return False
        if self.options.variant != SOUTHERN_VARIANT or self.current_combo is None:
            return False
        if player.id not in self.turn_player_ids or not player.hand:
            return False
        rules = self._rules()
        selected_cards = selected if selected is not None else self._selected_cards(player)
        combo = rules.evaluate(selected_cards)
        if not combo:
            return False
        return rules.can_play_out_of_turn(self.current_combo, combo)

    def _send_error(self, player: TienLenPlayer, msg_key: str, **kwargs) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l(msg_key, buffer="game", **kwargs)

    def _action_toggle_select(self, player: Player, action_id: str) -> None:
        active_player = self._require_active_player(player) or (
            player if isinstance(player, TienLenPlayer) and not player.is_spectator else None
        )
        if not isinstance(active_player, TienLenPlayer):
            return
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return
        if card_id in active_player.selected_cards:
            active_player.selected_cards.remove(card_id)
        else:
            active_player.selected_cards.add(card_id)
        self.refresh_menus(active_player)

    def _action_play_selected(self, player: Player, action_id: str) -> None:
        active_player = self._require_tienlen_player(player)
        if not active_player:
            return

        if not active_player.selected_cards:
            self._send_error(active_player, "tienlen-error-no-cards")
            return

        selected = self._selected_cards(active_player)
        out_of_turn_chop = self.current_player != active_player
        if out_of_turn_chop:
            if not self._can_play_out_of_turn_chop(active_player, selected):
                self._send_error(active_player, "tienlen-error-not-your-turn-chop")
                return
            self.turn_index = self.turn_player_ids.index(active_player.id)

        required_opening_card = self._opening_required_card(active_player)
        if required_opening_card and required_opening_card not in selected:
            self._send_error(
                active_player,
                "tienlen-error-opening-card-required",
                card=self._card_name(required_opening_card, self._player_locale(active_player)),
            )
            return

        rules = self._rules()
        previous_combo = self.current_combo
        previous_winner = self.get_player_by_id(self.trick_winner_id)
        is_valid, error_key, error_kwargs = rules.validate_play(
            active_player.hand,
            selected,
            self.current_combo,
            self.is_first_turn,
            active_player.passed_this_trick,
        )
        if not is_valid:
            self._send_error(active_player, error_key or "tienlen-error-invalid-combo", **error_kwargs)
            return

        combo = rules.evaluate(selected)
        if not combo:
            self._send_error(active_player, "tienlen-error-invalid-combo")
            return

        if (
            previous_combo is not None
            and isinstance(previous_winner, TienLenPlayer)
            and rules.is_chop(combo, previous_combo)
        ):
            self._record_chop_payment(active_player, previous_winner, previous_combo)

        for card in selected:
            active_player.hand.remove(card)
        active_player.hand = sort_cards(active_player.hand)
        active_player.selected_cards.clear()
        active_player.pass_confirm_ticks = 0
        active_player.passed_this_trick = False
        active_player.passed_combo_turn = 0
        self.current_combo = combo
        self.trick_cards = combo.cards[:]
        self.trick_winner_id = active_player.id
        self.trick_play_id += 1
        next_player = self._next_player_with_cards_after(active_player.id)
        self.trick_lead_fallback_id = next_player.id if next_player else None
        self.is_first_turn = False

        if len(selected) > 1:
            self.play_sound(random.choice(SOUND_PLAY_MULTI))
        else:
            self.play_sound(random.choice(SOUND_PLAY_SINGLE))
        if rules.is_special_cutter(combo):
            self.play_sound(SOUND_SPECIAL_CHOP)

        self._broadcast_play(active_player, combo)

        if len(active_player.hand) == 1:
            self.broadcast_personal_l(
                active_player,
                "tienlen-you-one-card",
                "tienlen-one-card",
                buffer="game",
            )

        if not active_player.hand:
            self._player_finishes(active_player)
            return

        self.advance_turn(announce=False)
        self._start_turn()

    def _action_pass(self, player: Player, action_id: str) -> None:
        active_player = self._require_active_player(player)
        if not active_player:
            return
        if not self.current_combo:
            self._send_error(active_player, "tienlen-error-must-play")
            return
        if not active_player.is_bot and active_player.pass_confirm_ticks == 0:
            user = self.get_user(active_player)
            if user:
                wants_confirm = user.preferences.get_effective(
                    "confirm_destructive_actions", game_type=self.get_type()
                )
                if wants_confirm:
                    active_player.pass_confirm_ticks = 200
                    user.speak_l("tienlen-confirm-pass", buffer="game")
                    return
        self._ensure_trick_play_marker()
        active_player.passed_this_trick = True
        active_player.passed_combo_turn = self.trick_play_id
        active_player.pass_confirm_ticks = 0
        active_player.selected_cards.clear()
        self._broadcast_pass(active_player)
        self.advance_turn(announce=False)
        self._start_turn()

    def _action_check_trick(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if not self.current_combo:
            user.speak_l("tienlen-trick-empty", buffer="game")
            return
        trick_winner = self.get_player_by_id(self.trick_winner_id)
        winner_name = trick_winner.name if trick_winner else Localization.get(user.locale, "unknown-player")
        combo_name = Localization.get(user.locale, f"tienlen-combo-{self.current_combo.type_name}")
        user.speak_l(
            "tienlen-trick-status",
            buffer="game",
            player=winner_name,
            combo=combo_name,
            cards=self._read_cards(self.trick_cards, user.locale),
        )

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        if not isinstance(player, TienLenPlayer):
            return
        user = self.get_user(player)
        if user:
            player.hand = sort_cards(player.hand)
            user.speak_l("tienlen-your-hand", buffer="game", cards=self._read_cards(player.hand, user.locale))

    def _action_read_card_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = []
        for active_player in self.get_active_players():
            if isinstance(active_player, TienLenPlayer):
                if active_player.eliminated:
                    lines.append(
                        Localization.get(
                            user.locale,
                            "tienlen-card-count-eliminated-line",
                            player=active_player.name,
                        )
                    )
                else:
                    lines.append(
                        Localization.get(
                            user.locale,
                            "tienlen-card-count-line",
                            player=active_player.name,
                            count=len(active_player.hand),
                        )
                    )
        if lines:
            user.speak("; ".join(lines), buffer="game")

    def _action_check_variant(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak_l(
            "tienlen-variant-status",
            buffer="game",
            variant=Localization.get(user.locale, VARIANT_LABELS[self.options.variant]),
        )

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("tienlen-timer-disabled", buffer="game")
        else:
            user.speak_l("tienlen-timer-remaining", buffer="game", seconds=remaining)

    def _get_card_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, TienLenPlayer):
            return action_id
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        card = next((card for card in player.hand if card.id == card_id), None)
        if not card:
            return action_id
        locale = self._player_locale(player)
        name = self._card_name(card, locale)
        if card_id in player.selected_cards:
            return Localization.get(locale, "tienlen-card-selected", card=name)
        return Localization.get(locale, "tienlen-card-unselected", card=name)

    def _get_play_selected_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, TienLenPlayer):
            return action_id
        locale = self._player_locale(player)
        if not player.selected_cards:
            return Localization.get(locale, "tienlen-play-none")
        selected = [card for card in player.hand if card.id in player.selected_cards]
        combo = evaluate_combo(selected, self.options.variant)
        if not combo:
            return Localization.get(locale, "tienlen-play-invalid")
        combo_name = Localization.get(locale, f"tienlen-combo-{combo.type_name}")
        return Localization.get(locale, "tienlen-play-combo", combo=combo_name)

    def _get_pass_label(self, player: Player, action_id: str) -> str:
        return Localization.get(self._player_locale(player), "tienlen-pass")

    def _is_turn_action_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if isinstance(player, TienLenPlayer) and not player.hand:
            return "tienlen-error-already-finished"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.hand_wait_ticks > 0:
            return "action-wait-for-hand"
        if self.intro_wait_ticks > 0:
            return "action-wait-for-intro"
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_play_selected_enabled(self, player: Player) -> str | None:
        base = self._is_card_toggle_enabled(player)
        if base:
            return base
        if not isinstance(player, TienLenPlayer):
            return "action-not-available"
        if self.current_player == player:
            return None
        if self._can_play_out_of_turn_chop(player):
            return None
        return "tienlen-error-not-your-turn-chop"

    def _is_play_selected_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        if not isinstance(player, TienLenPlayer) or not player.hand:
            return Visibility.HIDDEN
        if self.current_player == player:
            return Visibility.VISIBLE
        if self._can_play_out_of_turn_chop(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_card_toggle_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if isinstance(player, TienLenPlayer) and not player.hand:
            return "tienlen-error-already-finished"
        if self.hand_wait_ticks > 0:
            return "action-wait-for-hand"
        if self.intro_wait_ticks > 0:
            return "action-wait-for-intro"
        return None

    def _is_card_toggle_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        if isinstance(player, TienLenPlayer) and not player.hand:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_pass_enabled(self, player: Player) -> str | None:
        if not self.current_combo:
            return "tienlen-error-must-play"
        return self._is_turn_action_enabled(player)

    def _is_pass_hidden(self, player: Player) -> Visibility:
        if not self.current_combo:
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_read_hand_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "action-spectator"
        return self._is_check_enabled(player)

    def _is_read_hand_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return self._is_check_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _speak_actor_message(
        self,
        actor: TienLenPlayer,
        listener: Player,
        self_key: str,
        other_key: str,
        **kwargs,
    ) -> None:
        user = self.get_user(listener)
        if not user:
            return
        if listener.id == actor.id:
            user.speak_l(self_key, buffer="game", **kwargs)
        else:
            user.speak_l(other_key, buffer="game", player=actor.name, **kwargs)

    def _broadcast_play(self, player: TienLenPlayer, combo: TienLenCombo) -> None:
        for table_player in self.players:
            user = self.get_user(table_player)
            if not user:
                continue
            combo_name = Localization.get(user.locale, f"tienlen-combo-{combo.type_name}")
            cards = self._read_cards(combo.cards, user.locale)
            if combo.type_name == "single":
                self._speak_actor_message(
                    player,
                    table_player,
                    "tienlen-you-play-single",
                    "tienlen-player-plays-single",
                    card=cards,
                )
            else:
                self._speak_actor_message(
                    player,
                    table_player,
                    "tienlen-you-play-combo",
                    "tienlen-player-plays-combo",
                    combo=combo_name,
                    cards=cards,
                )

    def _broadcast_pass(self, player: TienLenPlayer) -> None:
        for table_player in self.players:
            self._speak_actor_message(
                player,
                table_player,
                "tienlen-you-pass",
                "tienlen-player-passes",
            )

    def _broadcast_chop_payment(
        self,
        chopper: TienLenPlayer,
        chopped: TienLenPlayer,
        amount: int,
    ) -> None:
        for table_player in self.players:
            user = self.get_user(table_player)
            if not user:
                continue
            if table_player.id == chopper.id:
                user.speak_l(
                    "tienlen-you-chop-payment",
                    buffer="game",
                    player=chopped.name,
                    amount=amount,
                )
            elif table_player.id == chopped.id:
                user.speak_l(
                    "tienlen-you-are-chopped-payment",
                    buffer="game",
                    player=chopper.name,
                    amount=amount,
                )
            else:
                user.speak_l(
                    "tienlen-player-chop-payment",
                    buffer="game",
                    chopper=chopper.name,
                    chopped=chopped.name,
                    amount=amount,
                )

    def _broadcast_leftover_penalty(self, player: TienLenPlayer, amount: int) -> None:
        for table_player in self.players:
            self._speak_actor_message(
                player,
                table_player,
                "tienlen-you-leftover-penalty",
                "tienlen-player-leftover-penalty",
                amount=amount,
            )

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for player in self.players:
            if isinstance(player, TienLenPlayer):
                team = self._team_manager.get_team(player.name)
                if team:
                    team.total_score = player.coins

    def _broadcast_player_finishes(self, player: TienLenPlayer, place: int) -> None:
        for table_player in self.players:
            self._speak_actor_message(
                player,
                table_player,
                "tienlen-you-finish-place",
                "tienlen-player-finishes-place",
                place=place,
            )

    def _player_finishes(self, player: TienLenPlayer) -> None:
        if player.id not in self.finishing_order_ids:
            self.finishing_order_ids.append(player.id)
            self._broadcast_player_finishes(player, len(self.finishing_order_ids))
        self.play_sound(SOUND_WIN_HAND)

        if self._finish_hand_if_ready():
            return

        old_order = list(self.turn_player_ids)
        try:
            old_index = old_order.index(player.id)
        except ValueError:
            old_index = self.turn_index

        remaining = self._players_still_in_hand()
        self.set_turn_players(remaining)
        remaining_ids = set(self.turn_player_ids)
        next_id = None
        for offset in range(1, len(old_order) + 1):
            candidate = old_order[(old_index + offset) % len(old_order)]
            if candidate in remaining_ids:
                next_id = candidate
                break
        if next_id is None and self.turn_player_ids:
            next_id = self.turn_player_ids[0]
        if next_id:
            self.turn_index = self.turn_player_ids.index(next_id)
        self._start_turn()

    def _finish_hand_if_ready(self) -> bool:
        remaining = self._players_still_in_hand()
        if len(remaining) > 1:
            return False
        if remaining and remaining[0].id not in self.finishing_order_ids:
            self.finishing_order_ids.append(remaining[0].id)
        self._finish_hand()
        return True

    def _finalize_finishing_order(self) -> list[TienLenPlayer]:
        active_by_id = {player.id: player for player in self._tienlen_players()}
        ordered: list[TienLenPlayer] = []
        for player_id in self.finishing_order_ids:
            player = active_by_id.get(player_id)
            if player and player not in ordered:
                ordered.append(player)
        remaining = [player for player in active_by_id.values() if player not in ordered]
        remaining.sort(
            key=lambda player: (
                len(player.hand),
                max((card_strength(card) for card in player.hand), default=0),
            )
        )
        ordered.extend(remaining)
        return ordered

    def _finish_hand(
        self,
        *,
        instant_winner: TienLenPlayer | None = None,
        instant_reason_key: str | None = None,
    ) -> None:
        ordered = self._finalize_finishing_order()
        if not ordered:
            return

        winner = instant_winner or ordered[0]
        if instant_winner:
            if instant_reason_key:
                self._add_instant_win_payments(instant_winner, ordered, instant_reason_key)
        else:
            self._add_rank_payments(ordered)
            self._add_leftover_penalties(winner, ordered)

        deltas = self._settle_hand_payments(ordered)
        self.hand_winner_id = None if instant_winner else winner.id
        self._sync_team_scores()

        if instant_winner and instant_reason_key:
            self._broadcast_instant_win(instant_winner, instant_reason_key)

        for table_player in self.players:
            self._speak_actor_message(
                winner,
                table_player,
                "tienlen-you-win-hand",
                "tienlen-player-wins-hand",
            )
        for index, player in enumerate(ordered, 1):
            self.broadcast_l(
                "tienlen-hand-settlement-line",
                buffer="game",
                place=index,
                player=player.name,
                change=self._format_coin_delta(deltas[player.id]),
                total=player.coins,
            )

        newly_eliminated = [
            player
            for player in ordered
            if player.coins <= 0 and not player.eliminated
        ]
        for player in newly_eliminated:
            player.eliminated = True
            player.hand = []
            player.selected_cards.clear()
            self.play_sound(SOUND_ELIMINATED)
            self._broadcast_eliminated(player)

        remaining = self._tienlen_players()
        if newly_eliminated and len(remaining) > 1:
            self.broadcast_l("tienlen-players-remaining", buffer="game", count=len(remaining))

        if len(remaining) <= 1:
            match_winner = (
                remaining[0] if remaining else max(ordered, key=lambda player: player.coins)
            )
            self.play_sound(SOUND_WIN_GAME)
            self._broadcast_game_over(match_winner)
            self.finish_game()
            return

        self.hand_wait_ticks = 5 * 20
        self.refresh_menus()

    def _broadcast_instant_win(self, winner: TienLenPlayer, reason_key: str) -> None:
        for table_player in self.players:
            user = self.get_user(table_player)
            if not user:
                continue
            reason = Localization.get(user.locale, reason_key)
            if table_player.id == winner.id:
                user.speak_l("tienlen-you-instant-win", buffer="game", reason=reason)
            else:
                user.speak_l(
                    "tienlen-player-instant-wins",
                    buffer="game",
                    player=winner.name,
                    reason=reason,
                )

    def _broadcast_eliminated(self, player: TienLenPlayer) -> None:
        for table_player in self.players:
            self._speak_actor_message(
                player,
                table_player,
                "tienlen-you-eliminated",
                "tienlen-player-eliminated",
            )

    def _broadcast_game_over(self, winner: TienLenPlayer) -> None:
        for table_player in self.players:
            user = self.get_user(table_player)
            if not user:
                continue
            if table_player.id == winner.id:
                user.speak_l("tienlen-you-win-match", buffer="game", coins=winner.coins)
            else:
                user.speak_l(
                    "tienlen-player-wins-match",
                    buffer="game",
                    player=winner.name,
                    coins=winner.coins,
                )

    def _format_coin_delta(self, delta: int) -> str:
        if delta > 0:
            return f"+{delta}"
        return str(delta)

    def build_game_result(self) -> GameResult:
        active_players = [player for player in self.players if not player.is_spectator]
        tienlen_players = [
            player for player in active_players if isinstance(player, TienLenPlayer)
        ]
        winner = max(
            (player for player in tienlen_players if not player.eliminated),
            key=lambda player: (
                player.coins,
                -len(player.hand),
                -card_strength(player.hand[0]) if player.hand else 0,
            ),
            default=None,
        )
        if winner is None:
            winner = max(
                tienlen_players,
                key=lambda player: (
                    player.coins,
                    -len(player.hand),
                    -card_strength(player.hand[0]) if player.hand else 0,
                ),
                default=None,
            )
        final_scores = {
            player.name: player.coins
            for player in tienlen_players
        }
        final_eliminated = {
            player.name: player.eliminated
            for player in tienlen_players
        }
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=player.id,
                    player_name=player.name,
                    is_bot=player.is_bot and not player.replaced_human,
                )
                for player in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "winner_score": winner.coins if winner else 0,
                "final_scores": final_scores,
                "final_eliminated": final_eliminated,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_scores = result.custom_data.get("final_scores", {})
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
        for index, (name, score) in enumerate(sorted_scores, 1):
            lines.append(Localization.get(locale, "tienlen-line-format", rank=index, player=name, score=score))
        return lines
