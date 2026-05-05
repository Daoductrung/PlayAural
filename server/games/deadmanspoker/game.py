"""Dead Man's Poker game implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, GameOptions, Player
from ..categories import CATEGORY_POKER
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.cards import Card, Deck, DeckFactory, card_name, read_cards
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.poker_evaluator import best_hand, describe_hand, describe_partial_hand
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from .bot import bot_select_switch_card as _bot_select_switch_card
from .bot import bot_think as _bot_think


PHASE_MATCH_START = "match_start"
PHASE_HAND_SETUP = "hand_setup"
PHASE_DECISION = "decision"
PHASE_SWITCH = "switch"
PHASE_COMMUNITY_REVEAL = "community_reveal"
PHASE_ALL_IN_RESPONSE = "all_in_response"
PHASE_SHOWDOWN = "showdown"
PHASE_ROULETTE = "roulette"
PHASE_HAND_CLEANUP = "hand_cleanup"
PHASE_GAME_OVER = "game_over"

HAND_SIZE = 2
COMMUNITY_CARD_COUNT = 5
MAX_BULLETS = 8
STARTING_BULLETS = 1
ROUND_SOUND_DELAY_TICKS = 40
PRIVATE_REVEAL_DELAY_TICKS = 40
EMPTY_CLICK_TO_UNLOAD_TICKS = 20
ROULETTE_POST_SPIN_WAIT_TICKS = (20, 40)
ROULETTE_POST_COCK_WAIT_TICKS = (40, 60)
EIGHT_BULLET_DEATH_CHANCE = 0.95

SOUND_MUSIC = "game_deadmansdeck/music.ogg"
SOUND_COCK = "game_deadmansdeck/cock.ogg"
SOUND_BULLET_HIT = "game_deadmansdeck/bullet_hit.ogg"
SOUND_GAME_OVER = "game_deadmansdeck/game_over.ogg"

SOUND_GAME_START = "game_deadmanspoker/game_start.ogg"
SOUND_SHUFFLE = "game_deadmanspoker/shuffle.ogg"
SOUND_DEAL_CARD = "game_deadmanspoker/deal_card.ogg"
SOUND_COMMUNITY_CARDS_ARRIVE = "game_deadmanspoker/community_cards_arrive.ogg"
SOUND_ROUNDS = {
    1: "game_deadmanspoker/round_1.ogg",
    2: "game_deadmanspoker/round_2.ogg",
    3: "game_deadmanspoker/round_3.ogg",
    4: "game_deadmanspoker/round_4.ogg",
}
SOUND_CALL = "game_deadmanspoker/call.ogg"
SOUND_ALL_IN = "game_deadmanspoker/all_in.ogg"
SOUND_FOLD = "game_deadmanspoker/fold.ogg"
SOUND_SWITCH_CARD = "game_deadmanspoker/switch_card.ogg"
SOUND_REVEAL_CARD = "game_deadmanspoker/reveal_card.ogg"
SOUND_REVEAL_THREE_CARDS = "game_deadmanspoker/reveal_three_cards.ogg"
SOUND_REVEAL_PRIVATE_CARDS = "game_deadmanspoker/reveal_private_cards.ogg"
SOUND_PICK_UP_BULLETS = "game_deadmanspoker/pick_up_bullets.ogg"
SOUND_PICK_UP_GUN = "game_deadmanspoker/pick_up_gun.ogg"
SOUND_LOAD_BULLET = "game_deadmanspoker/load_bullet.ogg"
SOUND_SPIN_CYLINDER = "game_deadmanspoker/spin_cylinder.ogg"
SOUND_EMPTY_CLICK = "game_deadmanspoker/empty_click.ogg"
SOUND_UNLOAD_BULLET = "game_deadmanspoker/unload_bullet.ogg"
SOUND_PLACE_BULLETS = [
    "game_deadmanspoker/place_bullet1.ogg",
    "game_deadmanspoker/place_bullet2.ogg",
    "game_deadmanspoker/place_bullet3.ogg",
    "game_deadmanspoker/place_bullet4.ogg",
]
SOUND_GUNSHOTS = [
    "game_deadmanspoker/gunshot1.ogg",
    "game_deadmanspoker/gunshot2.ogg",
    "game_deadmanspoker/gunshot3.ogg",
    "game_deadmanspoker/gunshot4.ogg",
    "game_deadmanspoker/gunshot5.ogg",
]
SOUND_DEATH_SIGNAL = "game_deadmanspoker/death_signal.ogg"

AUDIO_DURATIONS_TICKS = {
    SOUND_ALL_IN: 94,
    SOUND_CALL: 66,
    SOUND_COMMUNITY_CARDS_ARRIVE: 32,
    SOUND_DEAL_CARD: 18,
    SOUND_DEATH_SIGNAL: 150,
    SOUND_EMPTY_CLICK: 10,
    SOUND_FOLD: 28,
    SOUND_GAME_START: 132,
    "game_deadmanspoker/gunshot1.ogg": 150,
    "game_deadmanspoker/gunshot2.ogg": 150,
    "game_deadmanspoker/gunshot3.ogg": 150,
    "game_deadmanspoker/gunshot4.ogg": 150,
    "game_deadmanspoker/gunshot5.ogg": 150,
    SOUND_LOAD_BULLET: 19,
    SOUND_PICK_UP_BULLETS: 4,
    SOUND_PICK_UP_GUN: 17,
    "game_deadmanspoker/place_bullet1.ogg": 47,
    "game_deadmanspoker/place_bullet2.ogg": 44,
    "game_deadmanspoker/place_bullet3.ogg": 48,
    "game_deadmanspoker/place_bullet4.ogg": 45,
    SOUND_REVEAL_CARD: 74,
    SOUND_REVEAL_PRIVATE_CARDS: 20,
    SOUND_REVEAL_THREE_CARDS: 72,
    "game_deadmanspoker/round_1.ogg": ROUND_SOUND_DELAY_TICKS,
    "game_deadmanspoker/round_2.ogg": ROUND_SOUND_DELAY_TICKS,
    "game_deadmanspoker/round_3.ogg": ROUND_SOUND_DELAY_TICKS,
    "game_deadmanspoker/round_4.ogg": ROUND_SOUND_DELAY_TICKS,
    SOUND_SHUFFLE: 43,
    SOUND_SPIN_CYLINDER: 20,
    SOUND_SWITCH_CARD: 36,
    SOUND_UNLOAD_BULLET: 38,
    SOUND_COCK: 20,
    SOUND_BULLET_HIT: 22,
    SOUND_GAME_OVER: 87,
}


@dataclass
class DeadMansPokerPlayer(Player):
    """Player state for Dead Man's Poker."""

    hand: list[Card] = field(default_factory=list)
    eliminated: bool = False
    folded_this_hand: bool = False
    active_in_hand: bool = False
    committed_bullets: int = 0
    acted_this_round: bool = False
    acted_this_hand: bool = False
    used_coward_fold: bool = False
    used_switch: bool = False
    matched_all_in: bool = False
    hands_won: int = 0
    folds_survived: int = 0
    showdowns_won: int = 0
    showdowns_lost: int = 0
    all_ins_initiated: int = 0
    all_ins_matched: int = 0
    bullets_risked: int = 0


@dataclass
class DeadMansPokerOptions(GameOptions):
    """Dead Man's Poker uses fixed canonical rules in v1."""


@dataclass
@register_game
class DeadMansPokerGame(Game):
    """A survival poker game where bullets replace chips."""

    players: list[DeadMansPokerPlayer] = field(default_factory=list)
    options: DeadMansPokerOptions = field(default_factory=DeadMansPokerOptions)

    deck: Deck | None = None
    community: list[Card] = field(default_factory=list)
    revealed_community_count: int = 0
    hand_number: int = 0
    phase: str = PHASE_MATCH_START
    round_stage: int = 1
    first_actor_index: int = 0
    all_in_initiator_id: str = ""
    pending_switch_player_id: str = ""
    pending_switch_card_index: int = -1
    pending_switch_candidates: list[Card] = field(default_factory=list)
    pending_switch_previous_phase: str = ""
    pending_roulette_ids: list[str] = field(default_factory=list)
    pending_roulette_results: dict[str, bool] = field(default_factory=dict)
    pending_roulette_context: str = ""
    winner_id: str = ""

    @classmethod
    def get_name(cls) -> str:
        return "Dead Man's Poker"

    @classmethod
    def get_type(cls) -> str:
        return "deadmanspoker"

    @classmethod
    def get_category(cls) -> str:
        return CATEGORY_POKER

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(
        self,
        player_id: str,
        name: str,
        is_bot: bool = False,
    ) -> DeadMansPokerPlayer:
        return DeadMansPokerPlayer(id=player_id, name=name, is_bot=is_bot)

    def supports_score_actions(self) -> bool:
        return False

    @property
    def alive_players(self) -> list[DeadMansPokerPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, DeadMansPokerPlayer) and not player.eliminated
        ]

    @property
    def active_hand_players(self) -> list[DeadMansPokerPlayer]:
        return [
            player
            for player in self.alive_players
            if player.active_in_hand and not player.folded_this_hand
        ]

    @property
    def revealed_community_cards(self) -> list[Card]:
        return self.community[: self.revealed_community_count]

    def prestart_validate(self) -> list[str]:
        errors: list[str] = []
        active_count = self.get_active_player_count()
        if active_count < self.get_min_players():
            errors.append("action-need-more-players")
        if active_count > self.get_max_players():
            errors.append("action-table-full")
        return errors

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.phase = PHASE_MATCH_START
        self.hand_number = 0
        self.round = 0
        self.round_stage = 1
        self.first_actor_index = self._choose_initial_first_actor_index(
            self.get_active_player_count()
        )
        self.winner_id = ""
        self.deck = None
        self.community.clear()
        self.clear_scheduled_sounds()
        self.cancel_all_sequences()

        for player in self.get_active_players():
            dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
            dmp_player.hand.clear()
            dmp_player.eliminated = False
            dmp_player.folded_this_hand = False
            dmp_player.active_in_hand = False
            dmp_player.committed_bullets = 0
            dmp_player.acted_this_round = False
            dmp_player.acted_this_hand = False
            dmp_player.used_coward_fold = False
            dmp_player.used_switch = False
            dmp_player.matched_all_in = False
            dmp_player.hands_won = 0
            dmp_player.folds_survived = 0
            dmp_player.showdowns_won = 0
            dmp_player.showdowns_lost = 0
            dmp_player.all_ins_initiated = 0
            dmp_player.all_ins_matched = 0
            dmp_player.bullets_risked = 0

        self.start_sequence(
            "deadmanspoker_match_start",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_GAME_START),
                        SequenceOperation.callback_op("announce_match_start"),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_GAME_START),
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op("start_music"),
                        SequenceOperation.callback_op("start_new_hand"),
                    ]
                ),
            ],
            tag="deadmanspoker_match_start",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

        if not self.game_active or self.status != "playing":
            return
        if self.is_sequence_bot_paused():
            return
        if self.phase not in {PHASE_DECISION, PHASE_ALL_IN_RESPONSE, PHASE_SWITCH}:
            return
        BotHelper.on_tick(self)

    def _sound_ticks(self, sound: str) -> int:
        return AUDIO_DURATIONS_TICKS.get(sound, 0)

    def _random_place_bullet_sound(self) -> str:
        return random.choice(SOUND_PLACE_BULLETS)  # nosec B311

    def _random_gunshot_sound(self) -> str:
        return random.choice(SOUND_GUNSHOTS)  # nosec B311

    def _sort_private_hand(self, hand: list[Card]) -> list[Card]:
        return sorted(hand, key=lambda card: (14 if card.rank == 1 else card.rank, card.suit), reverse=True)

    def _choose_initial_first_actor_index(self, player_count: int) -> int:
        if player_count <= 1:
            return 0
        return random.randrange(player_count)  # nosec B311

    def _roulette_pan_values(self, player_count: int) -> list[int]:
        if player_count <= 0:
            return []
        if player_count == 1:
            return [0]
        if player_count == 2:
            return [-25, 25]
        if player_count == 3:
            return [-25, 0, 25]
        step = 100 / (player_count - 1)
        return [round(-50 + (step * index)) for index in range(player_count)]

    def _roulette_start_offsets(self, player_count: int) -> list[int]:
        if player_count <= 0:
            return []
        if player_count == 1:
            return [0]
        offsets = [0]
        offsets.extend(random.randint(1, 20) for _ in range(player_count - 1))  # nosec B311
        return sorted(offsets)

    def _build_timed_sequence_beats(
        self,
        events: list[tuple[int, int, SequenceOperation]],
    ) -> list[SequenceBeat]:
        grouped_events: list[tuple[int, list[SequenceOperation]]] = []
        for tick, _priority, operation in sorted(
            events,
            key=lambda item: (item[0], item[1]),
        ):
            if grouped_events and grouped_events[-1][0] == tick:
                grouped_events[-1][1].append(operation)
            else:
                grouped_events.append((tick, [operation]))

        beats: list[SequenceBeat] = []
        for index, (tick, operations) in enumerate(grouped_events):
            next_tick = (
                grouped_events[index + 1][0]
                if index + 1 < len(grouped_events)
                else tick
            )
            beats.append(
                SequenceBeat(
                    ops=operations,
                    delay_after_ticks=max(0, next_tick - tick),
                )
            )
        return beats

    def _start_new_hand(self) -> None:
        if self._check_game_end():
            return

        self.hand_number += 1
        self.round = self.hand_number
        self.round_stage = 1
        self.phase = PHASE_HAND_SETUP
        self.all_in_initiator_id = ""
        self.pending_switch_player_id = ""
        self.pending_switch_card_index = -1
        self.pending_switch_candidates.clear()
        self.pending_switch_previous_phase = ""
        self.pending_roulette_ids.clear()
        self.pending_roulette_results.clear()
        self.pending_roulette_context = ""
        self.revealed_community_count = 0

        self.deck, _ = DeckFactory.standard_deck()
        self.deck.shuffle()
        self.community = []

        alive = self.alive_players
        if not alive:
            self._start_game_over_sequence(None)
            return

        start_index = self.first_actor_index % len(alive)
        ordered = alive[start_index:] + alive[:start_index]
        self.first_actor_index = (start_index + 1) % len(alive)

        for player in alive:
            player.hand = []
            player.folded_this_hand = False
            player.active_in_hand = True
            player.committed_bullets = STARTING_BULLETS
            player.acted_this_round = False
            player.acted_this_hand = False
            player.matched_all_in = False

        for _ in range(HAND_SIZE):
            for player in ordered:
                if self.deck:
                    card = self.deck.draw_one()
                    if card:
                        player.hand.append(card)
        for player in ordered:
            player.hand = self._sort_private_hand(player.hand)

        if self.deck:
            self.community = self.deck.draw(COMMUNITY_CARD_COUNT)

        self.set_turn_players(ordered)
        self.rebuild_all_menus()

        beats = [
            SequenceBeat(
                ops=[
                    SequenceOperation.sound_op(SOUND_ROUNDS[1]),
                    SequenceOperation.callback_op("announce_hand_start"),
                ],
                delay_after_ticks=self._sound_ticks(SOUND_ROUNDS[1]),
            ),
            SequenceBeat(
                ops=[SequenceOperation.sound_op(SOUND_SHUFFLE)],
                delay_after_ticks=self._sound_ticks(SOUND_SHUFFLE),
            ),
        ]
        for _player in ordered:
            beats.append(
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(SOUND_DEAL_CARD)],
                    delay_after_ticks=self._sound_ticks(SOUND_DEAL_CARD),
                )
            )
        beats.extend(
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_COMMUNITY_CARDS_ARRIVE),
                        SequenceOperation.callback_op("announce_community_arrival"),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_COMMUNITY_CARDS_ARRIVE),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("begin_decision_round")]
                ),
            ]
        )
        self.start_sequence(
            "deadmanspoker_hand_start",
            beats,
            tag="deadmanspoker_hand",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _begin_decision_round(self) -> None:
        if self._check_game_end():
            return
        if len(self.active_hand_players) <= 1:
            self._start_hand_win_sequence(self.active_hand_players[0] if self.active_hand_players else None)
            return

        self.phase = PHASE_DECISION
        for player in self.active_hand_players:
            player.acted_this_round = False
        self._set_next_pending_turn()
        self.rebuild_all_menus()

    def _set_next_pending_turn(self, *, after_player_id: str = "") -> bool:
        pending = self._pending_turn_players()
        if not pending:
            return False

        ordered = [
            player
            for player in self.turn_players
            if isinstance(player, DeadMansPokerPlayer) and player in pending
        ]
        if not ordered:
            ordered = pending

        selected = ordered[0]
        if after_player_id:
            ids = [player.id for player in self.turn_players]
            if after_player_id in ids:
                start = (ids.index(after_player_id) + 1) % len(ids)
                for offset in range(len(ids)):
                    candidate = self.get_player_by_id(ids[(start + offset) % len(ids)])
                    if isinstance(candidate, DeadMansPokerPlayer) and candidate in pending:
                        selected = candidate
                        break

        self.current_player = selected
        self.announce_turn()
        if selected.is_bot:
            BotHelper.jolt_bot(selected, ticks=random.randint(10, 22))  # nosec B311
        self.rebuild_all_menus()
        return True

    def _pending_turn_players(self) -> list[DeadMansPokerPlayer]:
        active = self.active_hand_players
        if self.phase == PHASE_ALL_IN_RESPONSE:
            return [
                player
                for player in active
                if player.id != self.all_in_initiator_id and not player.matched_all_in
            ]
        if self.phase == PHASE_DECISION:
            return [player for player in active if not player.acted_this_round]
        return []

    def create_turn_action_set(self, player: DeadMansPokerPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        action_set.add(
            Action(
                id="call",
                label=Localization.get(locale, "deadmanspoker-call"),
                handler="_action_call",
                is_enabled="_is_call_enabled",
                is_hidden="_is_call_hidden",
                get_label="_get_call_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="fold",
                label=Localization.get(locale, "deadmanspoker-fold"),
                handler="_action_fold",
                is_enabled="_is_fold_enabled",
                is_hidden="_is_fold_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="coward_fold",
                label=Localization.get(locale, "deadmanspoker-coward-fold"),
                handler="_action_coward_fold",
                is_enabled="_is_coward_fold_enabled",
                is_hidden="_is_coward_fold_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="switch_card",
                label=Localization.get(locale, "deadmanspoker-switch-card"),
                handler="_action_switch_card",
                is_enabled="_is_switch_card_enabled",
                is_hidden="_is_switch_card_hidden",
                input_request=MenuInput(
                    prompt="deadmanspoker-switch-select-card",
                    options="_switch_card_options",
                    option_label="_switch_card_option_label",
                    bot_select="_bot_select_switch_card",
                ),
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="all_in",
                label=Localization.get(locale, "deadmanspoker-all-in"),
                handler="_action_all_in",
                is_enabled="_is_all_in_enabled",
                is_hidden="_is_all_in_hidden",
                show_in_actions_menu=False,
            )
        )
        for index in range(3):
            action_set.add(
                Action(
                    id=f"choose_switch_{index}",
                    label=Localization.get(
                        locale,
                        "deadmanspoker-choose-switch-placeholder",
                        index=index + 1,
                    ),
                    handler="_action_choose_switch",
                    is_enabled="_is_choose_switch_enabled",
                    is_hidden="_is_choose_switch_hidden",
                    get_label="_get_choose_switch_label",
                    show_in_actions_menu=False,
                )
            )

        if self.is_touch_client(user):
            for action in [
                Action(
                    id="read_hand",
                    label=Localization.get(locale, "deadmanspoker-read-hand"),
                    handler="_action_read_hand",
                    is_enabled="_is_read_hand_enabled",
                    is_hidden="_is_private_info_hidden",
                ),
                Action(
                    id="read_community_cards",
                    label=Localization.get(locale, "deadmanspoker-read-community-cards"),
                    handler="_action_read_community_cards",
                    is_enabled="_is_public_info_enabled",
                    is_hidden="_is_public_info_hidden",
                    include_spectators=True,
                ),
                Action(
                    id="read_hand_value",
                    label=Localization.get(locale, "deadmanspoker-read-hand-value"),
                    handler="_action_read_hand_value",
                    is_enabled="_is_read_hand_enabled",
                    is_hidden="_is_private_info_hidden",
                ),
                Action(
                    id="read_table",
                    label=Localization.get(locale, "deadmanspoker-read-table"),
                    handler="_action_read_table",
                    is_enabled="_is_public_info_enabled",
                    is_hidden="_is_public_info_hidden",
                    include_spectators=True,
                ),
                Action(
                    id="read_card_counts",
                    label=Localization.get(locale, "deadmanspoker-read-card-counts"),
                    handler="_action_read_card_counts",
                    is_enabled="_is_public_info_enabled",
                    is_hidden="_is_public_info_hidden",
                    include_spectators=True,
                ),
                Action(
                    id="read_revolvers",
                    label=Localization.get(locale, "deadmanspoker-read-revolvers"),
                    handler="_action_read_revolvers",
                    is_enabled="_is_public_info_enabled",
                    is_hidden="_is_public_info_hidden",
                    include_spectators=True,
                ),
            ]:
                action_set.add(action)

            primary_actions = ["call", "fold", "coward_fold", "switch_card", "all_in"]
            switch_actions = [f"choose_switch_{index}" for index in range(3)]
            info_actions = [
                "read_hand",
                "read_community_cards",
                "read_hand_value",
                "read_table",
                "read_card_counts",
                "read_revolvers",
            ]
            pinned = set(primary_actions) | set(switch_actions) | set(info_actions)
            rest = [action_id for action_id in action_set._order if action_id not in pinned]
            action_set._order = (
                [action_id for action_id in primary_actions if action_id in action_set._order]
                + [action_id for action_id in switch_actions if action_id in action_set._order]
                + [action_id for action_id in info_actions if action_id in action_set._order]
                + rest
            )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "deadmanspoker-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_read_hand_enabled",
                is_hidden="_is_private_info_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_hand_value",
                label=Localization.get(locale, "deadmanspoker-read-hand-value"),
                handler="_action_read_hand_value",
                is_enabled="_is_read_hand_enabled",
                is_hidden="_is_private_info_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_community_cards",
                label=Localization.get(locale, "deadmanspoker-read-community-cards"),
                handler="_action_read_community_cards",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_table",
                label=Localization.get(locale, "deadmanspoker-read-table"),
                handler="_action_read_table",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_card_counts",
                label=Localization.get(locale, "deadmanspoker-read-card-counts"),
                handler="_action_read_card_counts",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_revolvers",
                label=Localization.get(locale, "deadmanspoker-read-revolvers"),
                handler="_action_read_revolvers",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            target_order = [
                "read_hand",
                "read_community_cards",
                "read_hand_value",
                "read_table",
                "read_card_counts",
                "read_revolvers",
                "whose_turn",
                "whos_at_table",
            ]
            self._order_touch_standard_actions(action_set, target_order)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("c", "Call", ["call"], state=KeybindState.ACTIVE)
        self.define_keybind("f", "Fold", ["fold"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+f", "Coward's fold", ["coward_fold"], state=KeybindState.ACTIVE)
        self.define_keybind("d", "Switch card", ["switch_card"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+a", "All in", ["all_in"], state=KeybindState.ACTIVE)
        self.define_keybind("w", "Read hand", ["read_hand"], state=KeybindState.ACTIVE)
        self.define_keybind("g", "Hand value", ["read_hand_value"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "e",
            "Read community cards",
            ["read_community_cards"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "v",
            "Read table",
            ["read_table"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "h",
            "Read card counts",
            ["read_card_counts"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "p",
            "Read revolvers",
            ["read_revolvers"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _is_mutating_turn_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.is_sequence_gameplay_locked():
            return "deadmanspoker-action-sequence-running"
        if player.is_spectator:
            return "action-spectator"
        if not isinstance(player, DeadMansPokerPlayer):
            return "action-not-available"
        if player.eliminated:
            return "deadmanspoker-action-eliminated"
        if player.folded_this_hand or not player.active_in_hand:
            return "deadmanspoker-action-folded"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_call_enabled(self, player: Player) -> str | None:
        error = self._is_mutating_turn_enabled(player)
        if error:
            return error
        dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
        if self.phase == PHASE_ALL_IN_RESPONSE:
            if dmp_player.matched_all_in:
                return "deadmanspoker-already-matched-all-in"
            return None
        if self.phase != PHASE_DECISION:
            return "deadmanspoker-not-decision-phase"
        if dmp_player.committed_bullets >= MAX_BULLETS:
            return "deadmanspoker-max-bullets"
        return None

    def _is_fold_enabled(self, player: Player) -> str | None:
        error = self._is_mutating_turn_enabled(player)
        if error:
            return error
        if self.phase not in {PHASE_DECISION, PHASE_ALL_IN_RESPONSE}:
            return "deadmanspoker-not-decision-phase"
        if isinstance(player, DeadMansPokerPlayer):
            if (
                self.phase == PHASE_DECISION
                and not player.acted_this_hand
                and player.committed_bullets == STARTING_BULLETS
            ):
                return "deadmanspoker-fold-first-decision-use-coward"
        return None

    def _is_coward_fold_enabled(self, player: Player) -> str | None:
        error = self._is_mutating_turn_enabled(player)
        if error:
            return error
        dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
        if self.phase != PHASE_DECISION:
            return "deadmanspoker-not-decision-phase"
        if dmp_player.used_coward_fold:
            return "deadmanspoker-coward-used"
        if dmp_player.acted_this_hand or dmp_player.committed_bullets != STARTING_BULLETS:
            return "deadmanspoker-coward-first-decision-only"
        return None

    def _is_switch_card_enabled(self, player: Player) -> str | None:
        error = self._is_mutating_turn_enabled(player)
        if error:
            return error
        dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
        if self.phase != PHASE_DECISION:
            return "deadmanspoker-switch-not-now"
        if dmp_player.used_switch:
            return "deadmanspoker-switch-used"
        if self.revealed_community_count >= COMMUNITY_CARD_COUNT:
            return "deadmanspoker-switch-too-late"
        if len(dmp_player.hand) != HAND_SIZE:
            return "deadmanspoker-switch-no-cards"
        return None

    def _is_all_in_enabled(self, player: Player) -> str | None:
        error = self._is_mutating_turn_enabled(player)
        if error:
            return error
        dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
        if self.phase != PHASE_DECISION:
            return "deadmanspoker-not-decision-phase"
        if dmp_player.committed_bullets >= MAX_BULLETS:
            return "deadmanspoker-max-bullets"
        if len(self.active_hand_players) <= 1:
            return "deadmanspoker-no-opponents"
        return None

    def _is_choose_switch_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        error = self._is_mutating_turn_enabled(player)
        if error:
            return error
        if self.phase != PHASE_SWITCH:
            return "deadmanspoker-switch-not-now"
        if not isinstance(player, DeadMansPokerPlayer):
            return "action-not-available"
        if self.pending_switch_player_id != player.id:
            return "action-not-your-turn"
        index = self._switch_choice_index(action_id)
        if index < 0 or index >= len(self.pending_switch_candidates):
            return "deadmanspoker-switch-choice-missing"
        return None

    def _is_turn_action_visible(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_call_hidden(self, player: Player) -> Visibility:
        if self.phase not in {PHASE_DECISION, PHASE_ALL_IN_RESPONSE}:
            return Visibility.HIDDEN
        return self._is_turn_action_visible(player)

    def _is_fold_hidden(self, player: Player) -> Visibility:
        if self.phase not in {PHASE_DECISION, PHASE_ALL_IN_RESPONSE}:
            return Visibility.HIDDEN
        return self._is_turn_action_visible(player)

    def _is_coward_fold_hidden(self, player: Player) -> Visibility:
        if self._is_coward_fold_enabled(player) is not None:
            return Visibility.HIDDEN
        return self._is_turn_action_visible(player)

    def _is_switch_card_hidden(self, player: Player) -> Visibility:
        if self._is_switch_card_enabled(player) is not None:
            return Visibility.HIDDEN
        return self._is_turn_action_visible(player)

    def _is_all_in_hidden(self, player: Player) -> Visibility:
        if self._is_all_in_enabled(player) is not None:
            return Visibility.HIDDEN
        return self._is_turn_action_visible(player)

    def _is_choose_switch_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self._is_choose_switch_enabled(player, action_id=action_id) is not None:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_public_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_read_hand_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_public_info_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_private_info_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return self._is_public_info_hidden(player)

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

    def _get_call_label(self, player: Player, action_id: str) -> str:
        del action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if self.phase == PHASE_ALL_IN_RESPONSE:
            return Localization.get(locale, "deadmanspoker-match-all-in")
        return Localization.get(locale, "deadmanspoker-call")

    def _get_choose_switch_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        index = self._switch_choice_index(action_id)
        if 0 <= index < len(self.pending_switch_candidates):
            return Localization.get(
                locale,
                "deadmanspoker-choose-switch-card",
                card=card_name(self.pending_switch_candidates[index], locale),
            )
        return Localization.get(locale, "deadmanspoker-choose-switch-placeholder", index=index + 1)

    def _switch_card_options(self, player: Player) -> list[str]:
        if not isinstance(player, DeadMansPokerPlayer):
            return []
        return [str(index) for index in range(len(player.hand))]

    def _switch_card_option_label(self, player: Player, option: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        try:
            index = int(option)
        except ValueError:
            index = -1
        if isinstance(player, DeadMansPokerPlayer) and 0 <= index < len(player.hand):
            return Localization.get(
                locale,
                "deadmanspoker-switch-card-option",
                card=card_name(player.hand[index], locale),
            )
        return option

    def _bot_select_switch_card(self, player: Player, options: list[str]) -> str | None:
        if not isinstance(player, DeadMansPokerPlayer):
            return options[0] if options else None
        return _bot_select_switch_card(self, player, options)

    def _switch_choice_index(self, action_id: str | None) -> int:
        if not action_id or not action_id.startswith("choose_switch_"):
            return -1
        try:
            return int(action_id.removeprefix("choose_switch_"))
        except ValueError:
            return -1

    def _action_call(self, player: Player, action_id: str) -> None:
        dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
        if self.phase == PHASE_ALL_IN_RESPONSE:
            added = max(0, MAX_BULLETS - dmp_player.committed_bullets)
            dmp_player.committed_bullets = MAX_BULLETS
            dmp_player.matched_all_in = True
            dmp_player.acted_this_hand = True
            dmp_player.all_ins_matched += 1
            self._start_commit_sequence(
                dmp_player,
                added,
                action_sound=SOUND_CALL,
                announce_callback="announce_match_all_in",
                finish_callback="finish_all_in_call",
            )
            return

        dmp_player.committed_bullets += 1
        dmp_player.acted_this_round = True
        dmp_player.acted_this_hand = True
        self._start_commit_sequence(
            dmp_player,
            1,
            action_sound=SOUND_CALL,
            announce_callback="announce_call",
            finish_callback="finish_normal_call",
        )

    def _action_all_in(self, player: Player, action_id: str) -> None:
        dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
        added = max(0, MAX_BULLETS - dmp_player.committed_bullets)
        dmp_player.committed_bullets = MAX_BULLETS
        dmp_player.acted_this_round = True
        dmp_player.acted_this_hand = True
        dmp_player.matched_all_in = True
        dmp_player.all_ins_initiated += 1
        self.all_in_initiator_id = dmp_player.id
        self.phase = PHASE_ALL_IN_RESPONSE
        if self.pending_roulette_ids:
            self.pending_roulette_context = "all_in_fold"
        self._start_commit_sequence(
            dmp_player,
            added,
            action_sound=SOUND_ALL_IN,
            announce_callback="announce_all_in",
            finish_callback="finish_all_in_start",
        )

    def _action_fold(self, player: Player, action_id: str) -> None:
        self._fold_player(player, coward=False)

    def _action_coward_fold(self, player: Player, action_id: str) -> None:
        self._fold_player(player, coward=True)

    def _fold_player(self, player: Player, *, coward: bool) -> None:
        dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
        dmp_player.folded_this_hand = True
        dmp_player.active_in_hand = False
        dmp_player.acted_this_round = True
        dmp_player.acted_this_hand = True
        if coward:
            dmp_player.used_coward_fold = True
            dmp_player.committed_bullets = STARTING_BULLETS

        context = "all_in_fold" if self.phase == PHASE_ALL_IN_RESPONSE else "fold"
        if dmp_player.id not in self.pending_roulette_ids:
            self.pending_roulette_ids.append(dmp_player.id)
        self.pending_roulette_context = context
        self.start_sequence(
            "deadmanspoker_fold",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_FOLD),
                        SequenceOperation.callback_op(
                            "announce_coward_fold" if coward else "announce_fold",
                            {"player_id": dmp_player.id},
                        ),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_FOLD),
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "finish_fold",
                            {"player_id": dmp_player.id, "context": context},
                        )
                    ]
                ),
            ],
            tag="deadmanspoker_fold",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _finish_fold(self, player_id: str, context: str) -> None:
        player = self.get_player_by_id(player_id)
        if context == "all_in_fold":
            self.phase = PHASE_ALL_IN_RESPONSE
            if self._pending_turn_players():
                self._set_next_pending_turn(after_player_id=player_id)
                return
            self._start_pending_roulette()
            return

        self.phase = PHASE_DECISION
        if len(self.active_hand_players) <= 1 or not self._pending_turn_players():
            self._start_pending_roulette()
            return
        if isinstance(player, DeadMansPokerPlayer):
            self._set_next_pending_turn(after_player_id=player.id)
        else:
            self._set_next_pending_turn()

    def _action_switch_card(self, player: Player, input_value: str, action_id: str) -> None:
        del action_id
        dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
        try:
            card_index = int(input_value)
        except ValueError:
            return
        if card_index < 0 or card_index >= len(dmp_player.hand):
            return
        if not self.deck or self.deck.size() < 3:
            user = self.get_user(player)
            if user:
                user.speak_l("deadmanspoker-switch-no-deck", buffer="game")
            return

        self.pending_switch_player_id = dmp_player.id
        self.pending_switch_card_index = card_index
        self.pending_switch_candidates = self.deck.draw(3)
        self.pending_switch_previous_phase = self.phase
        self.phase = PHASE_SWITCH
        user = self.get_user(dmp_player)
        if user:
            user.speak_l(
                "deadmanspoker-switch-candidates",
                buffer="game",
                cards=read_cards(self.pending_switch_candidates, user.locale),
            )
        self.rebuild_all_menus()
        if dmp_player.is_bot:
            BotHelper.jolt_bot(dmp_player, ticks=random.randint(8, 16))  # nosec B311

    def _action_choose_switch(self, player: Player, action_id: str) -> None:
        dmp_player: DeadMansPokerPlayer = player  # type: ignore[assignment]
        index = self._switch_choice_index(action_id)
        if index < 0 or index >= len(self.pending_switch_candidates):
            return
        if self.pending_switch_player_id != dmp_player.id:
            return

        chosen = self.pending_switch_candidates[index]
        discarded = (
            dmp_player.hand[self.pending_switch_card_index]
            if 0 <= self.pending_switch_card_index < len(dmp_player.hand)
            else None
        )
        if 0 <= self.pending_switch_card_index < len(dmp_player.hand):
            dmp_player.hand[self.pending_switch_card_index] = chosen
            dmp_player.hand = self._sort_private_hand(dmp_player.hand)
        dmp_player.used_switch = True
        self.pending_switch_player_id = ""
        self.pending_switch_card_index = -1
        self.pending_switch_candidates.clear()
        self.phase = self.pending_switch_previous_phase or PHASE_DECISION
        self.pending_switch_previous_phase = ""
        self.start_sequence(
            "deadmanspoker_switch",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_SWITCH_CARD),
                        SequenceOperation.callback_op(
                            "announce_switch",
                            {
                                "player_id": dmp_player.id,
                                "discarded_rank": discarded.rank if discarded else 0,
                                "discarded_suit": discarded.suit if discarded else 0,
                            },
                        ),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_SWITCH_CARD),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("finish_switch", {"player_id": dmp_player.id})]
                ),
            ],
            tag="deadmanspoker_switch",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _start_commit_sequence(
        self,
        player: DeadMansPokerPlayer,
        added_bullets: int,
        *,
        action_sound: str,
        announce_callback: str,
        finish_callback: str,
    ) -> None:
        events: list[tuple[int, int, SequenceOperation]] = [
            (0, 0, SequenceOperation.sound_op(action_sound)),
            (
                0,
                1,
                SequenceOperation.callback_op(
                    announce_callback,
                    {"player_id": player.id, "added": added_bullets},
                ),
            ),
        ]
        current_tick = 0
        for index in range(added_bullets):
            sound = self._random_place_bullet_sound()
            events.append((current_tick, 2, SequenceOperation.sound_op(sound)))
            if added_bullets <= 1:
                current_tick += self._sound_ticks(sound)
        finish_tick = max(self._sound_ticks(action_sound), current_tick)
        events.append(
            (
                finish_tick,
                99,
                SequenceOperation.callback_op(finish_callback, {"player_id": player.id}),
            )
        )
        self.start_sequence(
            "deadmanspoker_commit",
            self._build_timed_sequence_beats(events),
            tag="deadmanspoker_commit",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _finish_normal_call(self, player_id: str) -> None:
        player = self.get_player_by_id(player_id)
        if not isinstance(player, DeadMansPokerPlayer):
            return
        if len(self.active_hand_players) <= 1:
            self._start_hand_win_sequence(self.active_hand_players[0] if self.active_hand_players else None)
            return
        if not self._pending_turn_players():
            self._complete_decision_round()
            return
        self._set_next_pending_turn(after_player_id=player.id)

    def _finish_all_in_start(self, player_id: str) -> None:
        player = self.get_player_by_id(player_id)
        if not isinstance(player, DeadMansPokerPlayer):
            return
        pending = self._pending_turn_players()
        if not pending:
            self._resolve_all_in_after_responses()
            return
        self._set_next_pending_turn(after_player_id=player.id)

    def _finish_all_in_call(self, player_id: str) -> None:
        player = self.get_player_by_id(player_id)
        if not isinstance(player, DeadMansPokerPlayer):
            return
        if not self._pending_turn_players():
            self._resolve_all_in_after_responses()
            return
        self._set_next_pending_turn(after_player_id=player.id)

    def _complete_decision_round(self) -> None:
        if self.pending_roulette_ids:
            self._start_pending_roulette()
            return
        if len(self.active_hand_players) <= 1:
            self._start_hand_win_sequence(self.active_hand_players[0] if self.active_hand_players else None)
            return
        if self.round_stage == 1:
            self._start_community_reveal_sequence(reveal_count=3, next_round=2)
            return
        if self.round_stage == 2:
            self._start_community_reveal_sequence(reveal_count=1, next_round=3)
            return
        if self.round_stage == 3:
            self._start_community_reveal_sequence(reveal_count=1, next_round=4)
            return
        self._start_showdown_sequence()

    def _start_community_reveal_sequence(self, *, reveal_count: int, next_round: int) -> None:
        self.phase = PHASE_COMMUNITY_REVEAL
        sound = SOUND_REVEAL_THREE_CARDS if reveal_count == 3 else SOUND_REVEAL_CARD
        self.start_sequence(
            "deadmanspoker_community_reveal",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(sound),
                        SequenceOperation.callback_op(
                            "reveal_community_cards",
                            {"count": reveal_count},
                        ),
                    ],
                    delay_after_ticks=self._sound_ticks(sound),
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_ROUNDS[next_round]),
                        SequenceOperation.callback_op(
                            "announce_round_stage",
                            {"round_stage": next_round},
                        ),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_ROUNDS[next_round]),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("begin_decision_round")]
                ),
            ],
            tag="deadmanspoker_community_reveal",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _resolve_all_in_after_responses(self) -> None:
        if self.pending_roulette_ids:
            self._start_pending_roulette()
            return
        if len(self.active_hand_players) <= 1:
            self._start_hand_win_sequence(self.active_hand_players[0] if self.active_hand_players else None)
            return
        self._start_showdown_sequence()

    def _start_showdown_sequence(self) -> None:
        self.phase = PHASE_SHOWDOWN
        events: list[tuple[int, int, SequenceOperation]] = []
        current_tick = 0
        remaining = COMMUNITY_CARD_COUNT - self.revealed_community_count
        while remaining > 0:
            if remaining >= 3:
                count = 3
                sound = SOUND_REVEAL_THREE_CARDS
            else:
                count = 1
                sound = SOUND_REVEAL_CARD
            events.append((current_tick, 0, SequenceOperation.sound_op(sound)))
            events.append(
                (
                    current_tick,
                    1,
                    SequenceOperation.callback_op(
                        "reveal_community_cards",
                        {"count": count},
                    ),
                )
            )
            current_tick += self._sound_ticks(sound)
            remaining -= count

        for player in self.active_hand_players:
            events.append((current_tick, 0, SequenceOperation.sound_op(SOUND_REVEAL_PRIVATE_CARDS)))
            events.append(
                (
                    current_tick,
                    1,
                    SequenceOperation.callback_op(
                        "announce_private_reveal",
                        {"player_id": player.id},
                    ),
                )
            )
            current_tick += PRIVATE_REVEAL_DELAY_TICKS

        events.append((current_tick, 99, SequenceOperation.callback_op("resolve_showdown")))
        self.start_sequence(
            "deadmanspoker_showdown",
            self._build_timed_sequence_beats(events),
            tag="deadmanspoker_showdown",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _resolve_showdown(self) -> None:
        active = self.active_hand_players
        if len(active) <= 1:
            self._start_hand_win_sequence(active[0] if active else None)
            return

        scored: list[tuple[DeadMansPokerPlayer, tuple[int, tuple[int, ...]]]] = []
        for player in active:
            score, _best_cards = best_hand(player.hand + self.community)
            scored.append((player, score))
        best_score = max(score for _player, score in scored)
        winners = [player for player, score in scored if score == best_score]
        losers = [player for player, score in scored if score != best_score]
        for winner in winners:
            winner.showdowns_won += 1
        for loser in losers:
            loser.showdowns_lost += 1
            loser.active_in_hand = False
            loser.folded_this_hand = True

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            best_text = describe_hand(best_score, user.locale)
            winner_names = Localization.format_list_and(user.locale, [p.name for p in winners])
            user.speak_l(
                "deadmanspoker-showdown-winners",
                buffer="game",
                players=winner_names,
                hand=best_text,
            )

        if not losers:
            self.broadcast_l("deadmanspoker-showdown-tie-no-penalty", buffer="game")
            self._start_new_hand()
            return

        self.pending_roulette_ids = [player.id for player in losers]
        self.pending_roulette_context = "showdown"
        self._start_pending_roulette()

    def _start_hand_win_sequence(self, winner: DeadMansPokerPlayer | None) -> None:
        self.phase = PHASE_HAND_CLEANUP
        self.start_sequence(
            "deadmanspoker_hand_win",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "announce_hand_winner",
                            {"player_id": winner.id if winner else ""},
                        )
                    ],
                    delay_after_ticks=20,
                ),
                SequenceBeat(ops=[SequenceOperation.callback_op("finish_hand")]),
            ],
            tag="deadmanspoker_hand_cleanup",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _start_pending_roulette(self) -> None:
        players = [
            player
            for player_id in self.pending_roulette_ids
            if isinstance((player := self.get_player_by_id(player_id)), DeadMansPokerPlayer)
            and not player.eliminated
        ]
        if not players:
            self._after_roulette_resolution()
            return

        self.phase = PHASE_ROULETTE
        self.pending_roulette_ids = [player.id for player in players]
        self.pending_roulette_results = {
            player.id: self._roulette_is_lethal(player.committed_bullets)
            for player in players
        }
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            user.speak_l(
                "deadmanspoker-roulette-start",
                buffer="game",
                players=Localization.format_list_and(user.locale, [player.name for player in players]),
            )

        pans = self._roulette_pan_values(len(players))
        start_offsets = self._roulette_start_offsets(len(players))
        events: list[tuple[int, int, SequenceOperation]] = []
        finish_tick = 0
        death_signal_used = False

        for index, player in enumerate(players):
            pan = pans[index]
            tick = start_offsets[index]
            events.append((tick, index, SequenceOperation.sound_op(SOUND_PICK_UP_GUN, pan=pan)))
            tick += self._sound_ticks(SOUND_PICK_UP_GUN)
            events.append((tick, index, SequenceOperation.sound_op(SOUND_PICK_UP_BULLETS, pan=pan)))
            events.append(
                (
                    tick,
                    50 + index,
                    SequenceOperation.callback_op(
                        "announce_load_bullets",
                        {"player_id": player.id, "bullets": player.committed_bullets},
                    ),
                )
            )
            tick += self._sound_ticks(SOUND_PICK_UP_BULLETS)
            for _ in range(max(0, player.committed_bullets)):
                events.append((tick, index, SequenceOperation.sound_op(SOUND_LOAD_BULLET, pan=pan)))
                tick += self._sound_ticks(SOUND_LOAD_BULLET)
            events.append((tick, index, SequenceOperation.sound_op(SOUND_SPIN_CYLINDER, pan=pan)))
            tick += self._sound_ticks(SOUND_SPIN_CYLINDER)
            tick += random.randint(*ROULETTE_POST_SPIN_WAIT_TICKS)  # nosec B311
            events.append((tick, index, SequenceOperation.sound_op(SOUND_COCK, pan=pan)))
            tick += self._sound_ticks(SOUND_COCK)
            tick += random.randint(*ROULETTE_POST_COCK_WAIT_TICKS)  # nosec B311

            if self.pending_roulette_results.get(player.id, False):
                gunshot = self._random_gunshot_sound()
                events.append((tick, index, SequenceOperation.sound_op(gunshot, pan=pan)))
                events.append((tick, 20 + index, SequenceOperation.sound_op(SOUND_BULLET_HIT, pan=pan)))
                if not death_signal_used:
                    events.append((tick, 21 + index, SequenceOperation.sound_op(SOUND_DEATH_SIGNAL, pan=pan)))
                    death_signal_used = True
                events.append(
                    (
                        tick,
                        50 + index,
                        SequenceOperation.callback_op(
                            "announce_roulette_death",
                            {"player_id": player.id},
                        ),
                    )
                )
                tick += self._sound_ticks(gunshot)
            else:
                events.append((tick, index, SequenceOperation.sound_op(SOUND_EMPTY_CLICK, pan=pan)))
                events.append(
                    (
                        tick,
                        50 + index,
                        SequenceOperation.callback_op(
                            "announce_roulette_survival",
                            {"player_id": player.id},
                        ),
                    )
                )
                tick += self._sound_ticks(SOUND_EMPTY_CLICK) + EMPTY_CLICK_TO_UNLOAD_TICKS
                events.append((tick, index, SequenceOperation.sound_op(SOUND_UNLOAD_BULLET, pan=pan)))
                tick += self._sound_ticks(SOUND_UNLOAD_BULLET)
            finish_tick = max(finish_tick, tick)

        events.append((finish_tick, 99, SequenceOperation.callback_op("finish_roulette")))
        self.start_sequence(
            "deadmanspoker_roulette",
            self._build_timed_sequence_beats(events),
            tag="deadmanspoker_roulette",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def _roulette_is_lethal(self, bullets: int) -> bool:
        if bullets <= 0:
            return False
        if bullets >= MAX_BULLETS:
            return random.random() < EIGHT_BULLET_DEATH_CHANCE  # nosec B311
        return random.random() < (bullets / MAX_BULLETS)  # nosec B311

    def _after_roulette_resolution(self) -> None:
        self.pending_roulette_ids.clear()
        self.pending_roulette_results.clear()
        context = self.pending_roulette_context
        self.pending_roulette_context = ""

        if self._check_game_end():
            return

        if context == "showdown":
            self._start_new_hand()
            return
        if len(self.active_hand_players) <= 1:
            self._start_hand_win_sequence(self.active_hand_players[0] if self.active_hand_players else None)
            return
        if context == "all_in_fold":
            self.phase = PHASE_ALL_IN_RESPONSE
            if not self._pending_turn_players():
                self._resolve_all_in_after_responses()
            else:
                self._set_next_pending_turn()
            return
        self.phase = PHASE_DECISION
        if not self._pending_turn_players():
            self._complete_decision_round()
        else:
            self._set_next_pending_turn()

    def _check_game_end(self) -> bool:
        alive = self.alive_players
        if len(alive) == 1:
            self._start_game_over_sequence(alive[0])
            return True
        if len(alive) == 0 and self.get_active_players():
            self._start_game_over_sequence(None)
            return True
        return False

    def _start_game_over_sequence(self, winner: DeadMansPokerPlayer | None) -> None:
        if self.phase == PHASE_GAME_OVER or self.status == "finished":
            return
        self.phase = PHASE_GAME_OVER
        self.winner_id = winner.id if winner else ""
        self.cancel_sequences_by_tag("deadmanspoker_hand")
        self.cancel_sequences_by_tag("deadmanspoker_commit")
        self.cancel_sequences_by_tag("deadmanspoker_community_reveal")
        self.cancel_sequences_by_tag("deadmanspoker_showdown")
        self.cancel_sequences_by_tag("deadmanspoker_roulette")
        self.start_sequence(
            "deadmanspoker_game_over",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_GAME_OVER),
                        SequenceOperation.callback_op("announce_game_over"),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_GAME_OVER),
                ),
                SequenceBeat(ops=[SequenceOperation.callback_op("finish_game")]),
            ],
            tag="deadmanspoker_game_over",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.rebuild_all_menus()

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        del sequence_id
        if callback_id == "announce_match_start":
            self.broadcast_l("deadmanspoker-match-start", buffer="game")
            return
        if callback_id == "start_music":
            self.play_music(SOUND_MUSIC)
            return
        if callback_id == "start_new_hand":
            self._start_new_hand()
            return
        if callback_id == "announce_hand_start":
            self.broadcast_l(
                "deadmanspoker-hand-start",
                buffer="game",
                hand=self.hand_number,
            )
            return
        if callback_id == "announce_community_arrival":
            self._announce_community_arrival()
            return
        if callback_id == "begin_decision_round":
            self._begin_decision_round()
            return
        if callback_id == "announce_round_stage":
            self.round_stage = int(payload.get("round_stage", self.round_stage))
            self.broadcast_l(
                "deadmanspoker-round-stage",
                buffer="game",
                round_stage=self.round_stage,
            )
            return
        if callback_id == "announce_call":
            self._announce_player_commit(payload, "deadmanspoker-player-calls")
            return
        if callback_id == "announce_match_all_in":
            self._announce_player_commit(payload, "deadmanspoker-player-matches-all-in")
            return
        if callback_id == "announce_all_in":
            self._announce_player_commit(payload, "deadmanspoker-player-all-in")
            return
        if callback_id == "finish_normal_call":
            self._finish_normal_call(str(payload.get("player_id", "")))
            return
        if callback_id == "finish_all_in_start":
            self._finish_all_in_start(str(payload.get("player_id", "")))
            return
        if callback_id == "finish_all_in_call":
            self._finish_all_in_call(str(payload.get("player_id", "")))
            return
        if callback_id == "announce_fold":
            self._announce_fold(payload, "deadmanspoker-player-folds")
            return
        if callback_id == "announce_coward_fold":
            self._announce_fold(payload, "deadmanspoker-player-coward-folds")
            return
        if callback_id == "finish_fold":
            self._finish_fold(
                str(payload.get("player_id", "")),
                str(payload.get("context", "")),
            )
            return
        if callback_id == "announce_switch":
            self._announce_switch(payload)
            return
        if callback_id == "finish_switch":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            if isinstance(player, DeadMansPokerPlayer):
                user = self.get_user(player)
                if user:
                    user.speak_l(
                        "deadmanspoker-your-hand",
                        buffer="game",
                        cards=read_cards(player.hand, user.locale),
                    )
                if player.is_bot:
                    BotHelper.jolt_bot(player, ticks=random.randint(10, 20))  # nosec B311
            self.rebuild_all_menus()
            return
        if callback_id == "reveal_community_cards":
            self._reveal_community_cards(int(payload.get("count", 0)))
            return
        if callback_id == "announce_private_reveal":
            self._announce_private_reveal(str(payload.get("player_id", "")))
            return
        if callback_id == "resolve_showdown":
            self._resolve_showdown()
            return
        if callback_id == "announce_load_bullets":
            self._announce_load_bullets(payload)
            return
        if callback_id == "announce_roulette_survival":
            self._announce_roulette_survival(str(payload.get("player_id", "")))
            return
        if callback_id == "announce_roulette_death":
            self._announce_roulette_death(str(payload.get("player_id", "")))
            return
        if callback_id == "finish_roulette":
            self._after_roulette_resolution()
            return
        if callback_id == "announce_hand_winner":
            player_id = str(payload.get("player_id", ""))
            winner = self.get_player_by_id(player_id) if player_id else None
            if isinstance(winner, DeadMansPokerPlayer):
                winner.hands_won += 1
                self.broadcast_l("deadmanspoker-hand-winner", buffer="game", player=winner.name)
            else:
                self.broadcast_l("deadmanspoker-hand-no-winner", buffer="game")
            return
        if callback_id == "finish_hand":
            if not self._check_game_end():
                self._start_new_hand()
            return
        if callback_id == "announce_game_over":
            winner = self.get_player_by_id(self.winner_id) if self.winner_id else None
            if winner:
                self.broadcast_l("deadmanspoker-player-wins", buffer="game", player=winner.name)
            else:
                self.broadcast_l("deadmanspoker-no-winner", buffer="game")
            return
        if callback_id == "finish_game":
            self.finish_game()

    def _announce_community_arrival(self) -> None:
        self.broadcast_l(
            "deadmanspoker-community-arrives",
            buffer="game",
            count=COMMUNITY_CARD_COUNT,
        )
        for player in self.alive_players:
            user = self.get_user(player)
            if not user:
                continue
            user.speak_l(
                "deadmanspoker-your-hand",
                buffer="game",
                cards=read_cards(player.hand, user.locale),
            )

    def _announce_player_commit(self, payload: dict, key: str) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not isinstance(player, DeadMansPokerPlayer):
            return
        self.broadcast_l(
            key,
            buffer="game",
            player=player.name,
            added=int(payload.get("added", 0)),
            total=player.committed_bullets,
        )

    def _announce_fold(self, payload: dict, key: str) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not isinstance(player, DeadMansPokerPlayer):
            return
        self.broadcast_l(
            key,
            buffer="game",
            player=player.name,
            bullets=player.committed_bullets,
        )

    def _announce_switch(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not isinstance(player, DeadMansPokerPlayer):
            return
        rank = int(payload.get("discarded_rank", 0))
        suit = int(payload.get("discarded_suit", 0))
        discarded = Card(id=0, rank=rank, suit=suit) if rank and suit else None
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            user.speak_l(
                "deadmanspoker-player-switches",
                buffer="game",
                player=player.name,
                card=card_name(discarded, user.locale) if discarded else "",
            )

    def _reveal_community_cards(self, count: int) -> None:
        if count <= 0:
            return
        old_count = self.revealed_community_count
        self.revealed_community_count = min(
            COMMUNITY_CARD_COUNT,
            self.revealed_community_count + count,
        )
        revealed = self.community[old_count : self.revealed_community_count]
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            user.speak_l(
                "deadmanspoker-community-revealed",
                buffer="game",
                cards=read_cards(revealed, user.locale),
                table=self._format_community(user.locale),
            )

    def _announce_private_reveal(self, player_id: str) -> None:
        player = self.get_player_by_id(player_id)
        if not isinstance(player, DeadMansPokerPlayer):
            return
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            cards = read_cards(player.hand, user.locale)
            hand_text = describe_partial_hand(player.hand + self.community, user.locale)
            user.speak_l(
                "deadmanspoker-private-reveal",
                buffer="game",
                player=player.name,
                cards=cards,
                hand=hand_text,
            )

    def _announce_load_bullets(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not player:
            return
        self.broadcast_l(
            "deadmanspoker-load-bullets",
            buffer="game",
            player=player.name,
            bullets=int(payload.get("bullets", 0)),
        )

    def _announce_roulette_survival(self, player_id: str) -> None:
        player = self.get_player_by_id(player_id)
        if not isinstance(player, DeadMansPokerPlayer) or player.eliminated:
            return
        player.folds_survived += 1
        player.bullets_risked += player.committed_bullets
        bullets = player.committed_bullets
        player.committed_bullets = 0
        self.broadcast_l(
            "deadmanspoker-roulette-survived",
            buffer="game",
            player=player.name,
            bullets=bullets,
        )

    def _announce_roulette_death(self, player_id: str) -> None:
        player = self.get_player_by_id(player_id)
        if not isinstance(player, DeadMansPokerPlayer) or player.eliminated:
            return
        player.bullets_risked += player.committed_bullets
        bullets = player.committed_bullets
        player.committed_bullets = 0
        player.eliminated = True
        player.active_in_hand = False
        player.folded_this_hand = True
        player.hand.clear()
        self.broadcast_l(
            "deadmanspoker-player-eliminated",
            buffer="game",
            player=player.name,
            bullets=bullets,
        )

    def _format_community(self, locale: str) -> str:
        if not self.revealed_community_cards:
            return Localization.get(locale, "deadmanspoker-community-none")
        return read_cards(self.revealed_community_cards, locale)

    def _format_hidden_community(self, locale: str) -> str:
        hidden = max(0, COMMUNITY_CARD_COUNT - self.revealed_community_count)
        return Localization.get(locale, "deadmanspoker-hidden-community", count=hidden)

    def _player_status_key(self, player: DeadMansPokerPlayer) -> str:
        if player.eliminated:
            return "deadmanspoker-status-eliminated"
        if player.folded_this_hand:
            return "deadmanspoker-status-folded"
        if player.active_in_hand:
            return "deadmanspoker-status-active"
        return "deadmanspoker-status-waiting"

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user or not isinstance(player, DeadMansPokerPlayer):
            return
        if player.eliminated:
            user.speak_l("deadmanspoker-you-are-eliminated", buffer="game")
            return
        if player.hand:
            user.speak_l(
                "deadmanspoker-your-hand",
                buffer="game",
                cards=read_cards(player.hand, user.locale),
            )
            return
        user.speak_l("deadmanspoker-hand-empty", buffer="game")

    def _action_read_hand_value(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user or not isinstance(player, DeadMansPokerPlayer):
            return
        if player.eliminated:
            user.speak_l("deadmanspoker-you-are-eliminated", buffer="game")
            return
        if not player.hand:
            user.speak_l("deadmanspoker-hand-empty", buffer="game")
            return
        user.speak(
            describe_partial_hand(player.hand + self.revealed_community_cards, user.locale),
            buffer="game",
        )

    def _action_read_community_cards(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak_l(
            "deadmanspoker-community-status",
            buffer="game",
            cards=self._format_community(user.locale),
            hidden=self._format_hidden_community(user.locale),
        )

    def _action_read_table(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = [
            Localization.get(
                user.locale,
                "deadmanspoker-table-hand",
                hand=self.hand_number,
                round_stage=self.round_stage,
            ),
            Localization.get(
                user.locale,
                "deadmanspoker-table-community",
                cards=self._format_community(user.locale),
                hidden=self._format_hidden_community(user.locale),
            ),
        ]
        current = self.current_player
        if current:
            lines.append(Localization.get(user.locale, "deadmanspoker-table-turn", player=current.name))
        else:
            lines.append(Localization.get(user.locale, "deadmanspoker-table-no-turn"))
        for table_player in self.get_active_players():
            if not isinstance(table_player, DeadMansPokerPlayer):
                continue
            status = Localization.get(user.locale, self._player_status_key(table_player))
            lines.append(
                Localization.get(
                    user.locale,
                    "deadmanspoker-table-player",
                    player=table_player.name,
                    bullets=table_player.committed_bullets,
                    status=status,
                )
            )
        self._speak_lines(user, lines)

    def _action_read_card_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = []
        for table_player in self.get_active_players():
            if not isinstance(table_player, DeadMansPokerPlayer):
                continue
            if table_player.eliminated:
                lines.append(
                    Localization.get(
                        user.locale,
                        "deadmanspoker-card-count-eliminated",
                        player=table_player.name,
                    )
                )
            else:
                lines.append(
                    Localization.get(
                        user.locale,
                        "deadmanspoker-card-count-line",
                        player=table_player.name,
                        count=len(table_player.hand),
                    )
                )
        self._speak_lines(user, lines)

    def _action_read_revolvers(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = [Localization.get(user.locale, "deadmanspoker-revolvers-header")]
        for table_player in self.get_active_players():
            if not isinstance(table_player, DeadMansPokerPlayer):
                continue
            if table_player.eliminated:
                lines.append(
                    Localization.get(
                        user.locale,
                        "deadmanspoker-revolver-eliminated",
                        player=table_player.name,
                    )
                )
                continue
            risk = self._risk_text(table_player.committed_bullets, user.locale)
            lines.append(
                Localization.get(
                    user.locale,
                    "deadmanspoker-revolver-status",
                    player=table_player.name,
                    bullets=table_player.committed_bullets,
                    risk=risk,
                )
            )
        self._speak_lines(user, lines)

    def _risk_text(self, bullets: int, locale: str) -> str:
        if bullets <= 0:
            return Localization.get(locale, "deadmanspoker-risk-none")
        if bullets >= MAX_BULLETS:
            return Localization.get(locale, "deadmanspoker-risk-eight")
        return Localization.get(locale, "deadmanspoker-risk-normal", bullets=bullets)

    def _speak_lines(self, user, lines: list[str]) -> None:
        user.speak(" ".join(line for line in lines if line), buffer="game")

    def bot_think(self, player: DeadMansPokerPlayer) -> str | None:
        return _bot_think(self, player)

    def build_game_result(self) -> GameResult:
        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, DeadMansPokerPlayer)
        ]
        winner = self.get_player_by_id(self.winner_id) if self.winner_id else None
        winner_ids = [winner.id] if winner else []
        rankings = sorted(
            active_players,
            key=lambda player: (
                0 if player.id == self.winner_id else 1,
                player.eliminated,
                -player.hands_won,
                player.name,
            ),
        )
        team_rankings = [
            {
                "index": index,
                "members": [player.name],
                "score": 1 if player.id == self.winner_id else 0,
                "is_individual": True,
            }
            for index, player in enumerate(rankings)
        ]

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
                "winner_ids": winner_ids,
                "hands_played": self.hand_number,
                "team_rankings": team_rankings,
                "player_stats": {
                    player.name: {
                        "hands_won": player.hands_won,
                        "showdowns_won": player.showdowns_won,
                        "showdowns_lost": player.showdowns_lost,
                        "all_ins_initiated": player.all_ins_initiated,
                        "all_ins_matched": player.all_ins_matched,
                        "folds_survived": player.folds_survived,
                        "bullets_risked": player.bullets_risked,
                        "eliminated": player.eliminated,
                    }
                    for player in active_players
                },
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "deadmanspoker-results-header")]
        winner_name = result.custom_data.get("winner_name")
        if winner_name:
            lines.append(Localization.get(locale, "deadmanspoker-results-winner", player=winner_name))
        stats = result.custom_data.get("player_stats", {})
        for player in result.player_results:
            data = stats.get(player.player_name, {})
            status_key = (
                "deadmanspoker-results-survived"
                if player.player_name == winner_name
                else "deadmanspoker-results-eliminated"
            )
            lines.append(
                Localization.get(
                    locale,
                    "deadmanspoker-results-line",
                    player=player.player_name,
                    status=Localization.get(locale, status_key),
                    hands=data.get("hands_won", 0),
                    allins=data.get("all_ins_initiated", 0),
                    survivals=data.get("folds_survived", 0),
                    bullets=data.get("bullets_risked", 0),
                )
            )
        return lines
