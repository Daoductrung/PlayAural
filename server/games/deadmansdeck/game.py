"""Dead Man's Deck game implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, GameOptions, Player
from ..categories import CATEGORY_CARDS
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem
from .bot import bot_think as _bot_think


RANK_ACE = "ace"
RANK_KING = "king"
RANK_QUEEN = "queen"
RANK_JOKER = "joker"
TARGET_RANKS = [RANK_ACE, RANK_KING, RANK_QUEEN]
DECK_COUNTS = {
    RANK_ACE: 6,
    RANK_KING: 6,
    RANK_QUEEN: 6,
    RANK_JOKER: 2,
}
CARD_SORT_ORDER = {
    RANK_KING: 0,
    RANK_QUEEN: 1,
    RANK_ACE: 2,
    RANK_JOKER: 3,
}

HAND_SIZE = 5
MAX_CLAIM_CARDS = 3
CHAMBER_COUNT = 6
TICKS_PER_SECOND = 20
RELOAD_EXTRA_WAIT_TICKS = TICKS_PER_SECOND
COCK_TO_OUTCOME_DELAY_TICKS = 2 * TICKS_PER_SECOND
PREPARATION_INTRO_TICKS = 8 * TICKS_PER_SECOND

PHASE_PREPARING = "preparing"
PHASE_ROUND_START = "round_start"
PHASE_PLAYING = "playing"
PHASE_CLAIM = "claim"
PHASE_CHALLENGE = "challenge"
PHASE_ROULETTE = "roulette"
PHASE_GAME_OVER = "game_over"

SOUND_MUSIC = "game_deadmansdeck/music.ogg"
SOUND_INTRO = "game_deadmansdeck/intro.ogg"
SOUND_ROUND_START = "game_deadmansdeck/round_start.ogg"
SOUND_REVOLVER_SPIN = "game_deadmansdeck/revolver_spin.ogg"
SOUND_COCK = "game_deadmansdeck/cock.ogg"
SOUND_EMPTY_CLICK = "game_deadmansdeck/empty_click.ogg"
SOUND_EMPTY_CASINGS = [
    "game_deadmansdeck/empty_casing1.ogg",
    "game_deadmansdeck/empty_casing2.ogg",
    "game_deadmansdeck/empty_casing3.ogg",
]
SOUND_GUNSHOT = "game_deadmansdeck/gunshot.ogg"
SOUND_BULLET_HIT = "game_deadmansdeck/bullet_hit.ogg"
SOUND_BODY_FALLS = [
    "game_deadmansdeck/body_fall1.ogg",
    "game_deadmansdeck/body_fall2.ogg",
]
SOUND_GAME_OVER = "game_deadmansdeck/game_over.ogg"

SOUND_SHUFFLES = [
    "game_cards/shuffle1.ogg",
    "game_cards/shuffle2.ogg",
    "game_cards/shuffle3.ogg",
]
SOUND_PLAYS = [
    "game_cards/play1.ogg",
    "game_cards/play2.ogg",
    "game_cards/play3.ogg",
    "game_cards/play4.ogg",
]
SOUND_REVEAL = "game_cards/small_shuffle.ogg"
SOUND_CHALLENGE = "game_coup/challenge.ogg"
SOUND_CHALLENGE_SUCCESS = "game_coup/challengesuccess.ogg"
SOUND_CHALLENGE_FAIL = "game_coup/challengefail.ogg"

AUDIO_DURATIONS_TICKS = {
    "game_cards/shuffle1.ogg": 27,
    "game_cards/shuffle2.ogg": 28,
    "game_cards/shuffle3.ogg": 26,
    "game_cards/play1.ogg": 18,
    "game_cards/play2.ogg": 21,
    "game_cards/play3.ogg": 21,
    "game_cards/play4.ogg": 21,
    "game_cards/small_shuffle.ogg": 22,
    "game_coup/challenge.ogg": 45,
    "game_coup/challengesuccess.ogg": 42,
    "game_coup/challengefail.ogg": 15,
    "game_deadmansdeck/intro.ogg": PREPARATION_INTRO_TICKS,
    "game_deadmansdeck/round_start.ogg": 46,
    "game_deadmansdeck/revolver_spin.ogg": 60,
    "game_deadmansdeck/cock.ogg": 20,
    "game_deadmansdeck/empty_click.ogg": 13,
    "game_deadmansdeck/empty_casing1.ogg": 69,
    "game_deadmansdeck/empty_casing2.ogg": 64,
    "game_deadmansdeck/empty_casing3.ogg": 70,
    "game_deadmansdeck/gunshot.ogg": 60,
    "game_deadmansdeck/bullet_hit.ogg": 22,
    "game_deadmansdeck/body_fall1.ogg": 14,
    "game_deadmansdeck/body_fall2.ogg": 13,
    "game_deadmansdeck/game_over.ogg": 87,
}
REVOLVER_PREPARATION_DELAY_TICKS = (
    AUDIO_DURATIONS_TICKS[SOUND_REVOLVER_SPIN] + RELOAD_EXTRA_WAIT_TICKS
)
LATEST_REVOLVER_PREPARATION_START_TICKS = max(
    0, PREPARATION_INTRO_TICKS - REVOLVER_PREPARATION_DELAY_TICKS
)


@dataclass
class DeadMansDeckCard(DataClassJSONMixin):
    """A simplified Dead Man's Deck card."""

    id: int
    rank: str


@dataclass
class DeadMansDeckClaim(DataClassJSONMixin):
    """The most recent face-down claim."""

    player_id: str
    player_name: str
    cards: list[DeadMansDeckCard] = field(default_factory=list)
    target_rank: str = ""

    @property
    def count(self) -> int:
        return len(self.cards)


@dataclass
class DeadMansDeckPlayer(Player):
    """Player state for Dead Man's Deck."""

    hand: list[DeadMansDeckCard] = field(default_factory=list)
    selected_card_ids: list[int] = field(default_factory=list)
    eliminated: bool = False
    bullet_position: int = 0
    chamber_index: int = 0
    revolver_prepared: bool = False
    correct_challenges: int = 0
    failed_challenges: int = 0
    successful_bluffs: int = 0
    truthful_claims: int = 0
    roulette_survivals: int = 0


@dataclass
class DeadMansDeckOptions(GameOptions):
    """Dead Man's Deck uses fixed canonical rules in this first version."""


@dataclass
@register_game
class DeadMansDeckGame(Game):
    """A deception card game with roulette-style elimination."""

    players: list[DeadMansDeckPlayer] = field(default_factory=list)
    options: DeadMansDeckOptions = field(default_factory=DeadMansDeckOptions)

    deck: list[DeadMansDeckCard] = field(default_factory=list)
    target_rank: str = ""
    phase: str = PHASE_PREPARING
    last_claim: DeadMansDeckClaim | None = None
    round_order_ids: list[str] = field(default_factory=list)
    next_round_starter_id: str = ""
    pending_challenger_id: str = ""
    pending_accused_id: str = ""
    pending_penalty_player_id: str = ""
    pending_challenge_success: bool = False
    winner_id: str = ""

    @classmethod
    def get_name(cls) -> str:
        return "Dead Man's Deck"

    @classmethod
    def get_type(cls) -> str:
        return "deadmansdeck"

    @classmethod
    def get_category(cls) -> str:
        return CATEGORY_CARDS

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
        self, player_id: str, name: str, is_bot: bool = False
    ) -> DeadMansDeckPlayer:
        return DeadMansDeckPlayer(id=player_id, name=name, is_bot=is_bot)

    @property
    def alive_players(self) -> list[DeadMansDeckPlayer]:
        return [
            p
            for p in self.get_active_players()
            if isinstance(p, DeadMansDeckPlayer) and not p.eliminated
        ]

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.phase = PHASE_PREPARING
        self.winner_id = ""
        self.last_claim = None
        self.next_round_starter_id = ""
        self.clear_scheduled_sounds()
        self.cancel_all_sequences()

        for player in self.get_active_players():
            dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
            dmd_player.hand.clear()
            dmd_player.selected_card_ids.clear()
            dmd_player.eliminated = False
            dmd_player.bullet_position = random.randint(0, CHAMBER_COUNT - 1)
            dmd_player.chamber_index = 0
            dmd_player.revolver_prepared = False
            dmd_player.correct_challenges = 0
            dmd_player.failed_challenges = 0
            dmd_player.successful_bluffs = 0
            dmd_player.truthful_claims = 0
            dmd_player.roulette_survivals = 0

        self._start_preparation_sequence()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

        if not self.game_active:
            return
        if self.is_sequence_bot_paused():
            return
        if self.phase != PHASE_PLAYING:
            return

        BotHelper.on_tick(self)

    def _sound_ticks(self, sound: str) -> int:
        return AUDIO_DURATIONS_TICKS.get(sound, 0)

    def _random_shuffle_sound(self) -> str:
        return random.choice(SOUND_SHUFFLES)  # nosec B311

    def _random_play_sound(self) -> str:
        return random.choice(SOUND_PLAYS)  # nosec B311

    def _random_empty_casing_sound(self) -> str:
        return random.choice(SOUND_EMPTY_CASINGS)  # nosec B311

    def _random_body_fall_sound(self) -> str:
        return random.choice(SOUND_BODY_FALLS)  # nosec B311

    def _preparation_pan_values(self, player_count: int) -> list[int]:
        if player_count <= 0:
            return []
        if player_count == 1:
            return [0]
        if player_count == 2:
            return [-25, 25]

        step = 100 / (player_count - 1)
        return [round(-50 + (step * index)) for index in range(player_count)]

    def _preparation_load_start_ticks(self, player_count: int) -> list[int]:
        if player_count <= 0:
            return []
        latest_start = LATEST_REVOLVER_PREPARATION_START_TICKS
        if latest_start <= 0:
            return [0 for _ in range(player_count)]

        candidates = list(range(1, latest_start + 1))
        if len(candidates) >= player_count:
            return random.sample(candidates, player_count)  # nosec B311
        return [
            random.randint(0, latest_start)  # nosec B311
            for _ in range(player_count)
        ]

    def _card_sort_key(self, card: DeadMansDeckCard) -> tuple[int, int]:
        return (CARD_SORT_ORDER.get(card.rank, len(CARD_SORT_ORDER)), card.id)

    def _sort_hand(self, player: DeadMansDeckPlayer) -> None:
        player.hand.sort(key=self._card_sort_key)

    def _sorted_cards(
        self,
        cards: list[DeadMansDeckCard],
    ) -> list[DeadMansDeckCard]:
        return sorted(cards, key=self._card_sort_key)

    def _build_deck(self) -> list[DeadMansDeckCard]:
        cards = []
        next_id = 1
        for rank, count in DECK_COUNTS.items():
            for _ in range(count):
                cards.append(DeadMansDeckCard(id=next_id, rank=rank))
                next_id += 1
        random.shuffle(cards)
        return cards

    def _deal_round_hands(self) -> None:
        self.deck = self._build_deck()
        for player in self.alive_players:
            player.hand = []
            player.selected_card_ids.clear()
            for _ in range(HAND_SIZE):
                if self.deck:
                    player.hand.append(self.deck.pop())
            self._sort_hand(player)

    def _clear_round_hands(self) -> None:
        for player in self.alive_players:
            player.hand.clear()
            player.selected_card_ids.clear()

    def _start_preparation_sequence(self) -> None:
        players = self.alive_players[:]
        pans = self._preparation_pan_values(len(players))
        load_start_ticks = self._preparation_load_start_ticks(len(players))
        events: list[tuple[int, int, SequenceOperation]] = [
            (
                0,
                0,
                SequenceOperation.sound_op(SOUND_INTRO),
            ),
            (
                0,
                1,
                SequenceOperation.callback_op("announce_prepare_revolvers"),
            )
        ]

        for index, player in enumerate(players):
            start_tick = load_start_ticks[index]
            pan = pans[index]
            events.append(
                (
                    start_tick,
                    0,
                    SequenceOperation.sound_op(SOUND_REVOLVER_SPIN, pan=pan),
                )
            )
            events.append(
                (
                    start_tick + REVOLVER_PREPARATION_DELAY_TICKS,
                    0,
                    SequenceOperation.callback_op(
                        "mark_revolver_prepared",
                        {"player_id": player.id},
                    ),
                )
            )

        events.append(
            (
                PREPARATION_INTRO_TICKS,
                50,
                SequenceOperation.callback_op("start_preparation_music"),
            )
        )
        events.append(
            (
                PREPARATION_INTRO_TICKS,
                99,
                SequenceOperation.callback_op("finish_preparation"),
            )
        )
        self.start_sequence(
            "deadmansdeck_preparation",
            self._build_timed_sequence_beats(events),
            tag="deadmansdeck_preparation",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

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

    def _start_round(self) -> None:
        if self._check_game_end():
            return

        self.round += 1
        self.phase = PHASE_ROUND_START
        self.target_rank = random.choice(TARGET_RANKS)  # nosec B311
        self.last_claim = None
        self.pending_challenger_id = ""
        self.pending_accused_id = ""
        self.pending_penalty_player_id = ""
        self.pending_challenge_success = False

        ordered_players = self._round_order()
        self.round_order_ids = [p.id for p in ordered_players]
        self.next_round_starter_id = ""
        self.set_turn_players(ordered_players)
        self._clear_round_hands()
        self.refresh_menus()

        shuffle_sound = self._random_shuffle_sound()
        self.start_sequence(
            "deadmansdeck_round_start",
            [
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(SOUND_ROUND_START)],
                    delay_after_ticks=self._sound_ticks(SOUND_ROUND_START),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(shuffle_sound)],
                    delay_after_ticks=self._sound_ticks(shuffle_sound),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("announce_round_start")],
                ),
            ],
            tag="deadmansdeck_round_start",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _round_order(self) -> list[DeadMansDeckPlayer]:
        alive = self.alive_players[:]
        if not alive:
            return []

        starter_id = self._round_starter_id(alive)
        if not starter_id:
            random.shuffle(alive)
            return alive

        previous_order = [
            player
            for player_id in self.round_order_ids
            if isinstance(player := self.get_player_by_id(player_id), DeadMansDeckPlayer)
            and not player.eliminated
        ]
        previous_ids = {player.id for player in previous_order}
        missing = [player for player in alive if player.id not in previous_ids]
        random.shuffle(missing)
        ordered = previous_order + missing
        starter_index = next(
            (index for index, player in enumerate(ordered) if player.id == starter_id),
            None,
        )
        if starter_index is None:
            random.shuffle(alive)
            return alive
        return ordered[starter_index:] + ordered[:starter_index]

    def _round_starter_id(self, alive: list[DeadMansDeckPlayer]) -> str:
        alive_ids = {player.id for player in alive}
        if self.next_round_starter_id in alive_ids:
            return self.next_round_starter_id
        if not self.next_round_starter_id or not self.round_order_ids:
            return ""
        try:
            previous_index = self.round_order_ids.index(self.next_round_starter_id)
        except ValueError:
            return ""
        for offset in range(1, len(self.round_order_ids) + 1):
            candidate_id = self.round_order_ids[
                (previous_index + offset) % len(self.round_order_ids)
            ]
            if candidate_id in alive_ids:
                return candidate_id
        return ""

    def _announce_round_start(self) -> None:
        self._deal_round_hands()
        self.phase = PHASE_PLAYING
        for listener in self.players:
            user = self.get_user(listener)
            if user:
                user.speak_l(
                    "deadmansdeck-round-start",
                    buffer="game",
                    round=self.round,
                    target=self._rank_name(self.target_rank, user.locale, plural=True),
                )
        self._broadcast_turn_order()
        self._speak_private_hands()
        self._start_turn()

    def _broadcast_turn_order(self) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            names = [
                player.name
                for player_id in self.round_order_ids
                if (player := self.get_player_by_id(player_id)) is not None
            ]
            order = Localization.format_list_and(user.locale, names)
            user.speak_l("deadmansdeck-turn-order", buffer="game", order=order)

    def _speak_private_hands(self) -> None:
        for player in self.alive_players:
            user = self.get_user(player)
            if not user:
                continue
            user.speak_l(
                "deadmansdeck-your-hand",
                buffer="game",
                cards=self._format_cards(player.hand, user.locale),
            )

    def _broadcast_challenge_call(
        self,
        challenger: DeadMansDeckPlayer,
        accused: DeadMansDeckPlayer,
        *,
        forced: bool,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == challenger.id:
                user.speak_l(
                    "deadmansdeck-you-forced-liar-call"
                    if forced
                    else "deadmansdeck-you-call-liar",
                    buffer="game",
                    accused=accused.name,
                )
            elif listener.id == accused.id:
                user.speak_l(
                    "deadmansdeck-forced-liar-call-you"
                    if forced
                    else "deadmansdeck-player-calls-you-liar",
                    buffer="game",
                    challenger=challenger.name,
                )
            else:
                user.speak_l(
                    "deadmansdeck-forced-liar-call"
                    if forced
                    else "deadmansdeck-player-calls-liar",
                    buffer="game",
                    challenger=challenger.name,
                    accused=accused.name,
                )

    def _broadcast_challenge_result(
        self,
        challenger: DeadMansDeckPlayer,
        accused: DeadMansDeckPlayer,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if self.pending_challenge_success:
                if listener.id == challenger.id:
                    user.speak_l(
                        "deadmansdeck-you-caught-bluff",
                        buffer="game",
                        accused=accused.name,
                    )
                elif listener.id == accused.id:
                    user.speak_l(
                        "deadmansdeck-your-bluff-caught",
                        buffer="game",
                        challenger=challenger.name,
                    )
                else:
                    user.speak_l(
                        "deadmansdeck-bluff-caught",
                        buffer="game",
                        challenger=challenger.name,
                        accused=accused.name,
                    )
            else:
                if listener.id == challenger.id:
                    user.speak_l(
                        "deadmansdeck-you-wrong-challenge",
                        buffer="game",
                        accused=accused.name,
                    )
                elif listener.id == accused.id:
                    user.speak_l(
                        "deadmansdeck-your-truthful-claim",
                        buffer="game",
                        challenger=challenger.name,
                    )
                else:
                    user.speak_l(
                        "deadmansdeck-truthful-claim",
                        buffer="game",
                        challenger=challenger.name,
                        accused=accused.name,
                    )

    def _start_turn(self) -> None:
        if self.phase != PHASE_PLAYING:
            return
        if self._check_game_end():
            return

        guard = 0
        while guard <= len(self.turn_players):
            guard += 1
            player = self.current_player
            if not isinstance(player, DeadMansDeckPlayer) or player.eliminated:
                self.advance_turn(announce=False)
                continue

            forced = self._forced_challenger()
            if forced:
                self.current_player = forced
                self.broadcast_personal_l(
                    forced,
                    "deadmansdeck-you-forced-challenge",
                    "deadmansdeck-forced-challenge",
                    buffer="game",
                )
                self._start_challenge_sequence(forced, forced=True)
                return

            if player.hand:
                break

            self.broadcast_personal_l(
                player,
                "deadmansdeck-you-skipped-no-cards",
                "deadmansdeck-player-skipped-no-cards",
                buffer="game",
            )
            self.advance_turn(announce=False)
        else:
            self._start_round()
            return

        player = self.current_player
        if not isinstance(player, DeadMansDeckPlayer):
            return

        self.announce_turn()
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(12, 24))
        self.refresh_menus()

    def _advance_after_claim(self) -> None:
        if self._check_game_end():
            return

        forced = self._forced_challenger()
        if forced:
            self.current_player = forced
        else:
            self.advance_turn(announce=False)
        self._start_turn()

    def _forced_challenger(self) -> DeadMansDeckPlayer | None:
        if not self.last_claim:
            return None

        alive = self.alive_players
        if len(alive) < 2:
            return None

        players_with_cards = [p for p in alive if p.hand]
        if len(players_with_cards) > 1:
            return None

        if len(players_with_cards) == 1:
            only_player = players_with_cards[0]
            if only_player.id != self.last_claim.player_id:
                return only_player

        ordered = self.turn_players or alive
        start = self.turn_index % len(ordered) if ordered else 0
        for offset in range(len(ordered)):
            player = ordered[(start + offset) % len(ordered)]
            if (
                isinstance(player, DeadMansDeckPlayer)
                and not player.eliminated
                and player.id != self.last_claim.player_id
            ):
                return player
        return None

    def create_turn_action_set(self, player: DeadMansDeckPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        action_set.add(
            Action(
                id="call_liar",
                label=Localization.get(locale, "deadmansdeck-call-liar"),
                handler="_action_call_liar",
                is_enabled="_is_call_liar_enabled",
                is_hidden="_is_call_liar_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="play_selected",
                label=Localization.get(locale, "deadmansdeck-play-selected"),
                handler="_action_play_selected",
                is_enabled="_is_play_selected_enabled",
                is_hidden="_is_play_selected_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="clear_selection",
                label=Localization.get(locale, "deadmansdeck-clear-selection"),
                handler="_action_clear_selection",
                is_enabled="_is_clear_selection_enabled",
                is_hidden="_is_clear_selection_hidden",
                show_in_actions_menu=False,
            )
        )
        self._sync_turn_actions(player, action_set)
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = super().create_standard_action_set(player)

        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "deadmansdeck-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_read_hand_enabled",
                is_hidden="_is_read_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_table",
                label=Localization.get(locale, "deadmansdeck-read-table"),
                handler="_action_read_table",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_revolvers",
                label=Localization.get(locale, "deadmansdeck-read-revolvers"),
                handler="_action_read_revolvers",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_card_counts",
                label=Localization.get(locale, "deadmansdeck-read-card-counts"),
                handler="_action_read_card_counts",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "read_hand",
                    "read_table",
                    "read_card_counts",
                    "read_revolvers",
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("c", "Call liar", ["call_liar"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "Play selected cards", ["play_selected"], state=KeybindState.ACTIVE)
        self.define_keybind("x", "Clear selected cards", ["clear_selection"], state=KeybindState.ACTIVE)
        self.define_keybind("h", "Read hand", ["read_hand"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "v",
            "Read table",
            ["read_table"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "r",
            "Read revolvers",
            ["read_revolvers"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "e",
            "Read card counts",
            ["read_card_counts"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def before_menu_build(self, player: Player) -> None:
        if not isinstance(player, DeadMansDeckPlayer):
            return
        self._sync_turn_actions(player)

    def _sync_turn_actions(
        self,
        player: Player,
        action_set: ActionSet | None = None,
    ) -> None:
        if action_set is None:
            action_set = self.get_action_set(player, "turn")
        if action_set is None:
            return
        if not isinstance(player, DeadMansDeckPlayer):
            return

        action_set.remove_by_prefix("select_card_")
        dmd_player = player
        self._sort_hand(dmd_player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        for card in dmd_player.hand:
            action_set.add(
                Action(
                    id=f"select_card_{card.id}",
                    label=self._select_card_label(dmd_player, card, locale),
                    handler="_action_select_card",
                    is_enabled="_is_select_card_enabled",
                    is_hidden="_is_select_card_hidden",
                    get_label="_get_select_card_label",
                    show_in_actions_menu=False,
                )
            )

        card_ids = [f"select_card_{card.id}" for card in dmd_player.hand]
        top = ["call_liar"]
        bottom = ["play_selected", "clear_selection"]
        action_set._order = (
            [aid for aid in top if action_set.get_action(aid)]
            + card_ids
            + [aid for aid in bottom if action_set.get_action(aid)]
        )

    def _is_current_player_action_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.phase != PHASE_PLAYING:
            return "deadmansdeck-action-sequence-running"
        if self.is_sequence_gameplay_locked():
            return "deadmansdeck-action-sequence-running"
        if player.is_spectator:
            return "action-spectator"
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        if dmd_player.eliminated:
            return "deadmansdeck-action-eliminated"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_select_card_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        if dmd_player.eliminated:
            return "deadmansdeck-action-eliminated"
        card = self._card_for_action(player, action_id)
        if not card:
            return "deadmansdeck-card-not-found"
        return None

    def _is_select_card_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        if dmd_player.eliminated:
            return Visibility.HIDDEN
        return Visibility.VISIBLE if dmd_player.hand else Visibility.HIDDEN

    def _select_card_block_reason(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        if dmd_player.eliminated:
            return "deadmansdeck-action-eliminated"
        if self.phase != PHASE_PLAYING or self.is_sequence_gameplay_locked():
            return "deadmansdeck-action-sequence-running"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _get_select_card_label(self, player: Player, action_id: str) -> str:
        card = self._card_for_action(player, action_id)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if not card:
            return Localization.get(locale, "deadmansdeck-card-not-found")
        return self._select_card_label(player, card, locale)  # type: ignore[arg-type]

    def _select_card_label(
        self,
        player: DeadMansDeckPlayer,
        card: DeadMansDeckCard,
        locale: str,
    ) -> str:
        key = (
            "deadmansdeck-selected-card-label"
            if card.id in player.selected_card_ids
            else "deadmansdeck-card-label"
        )
        return Localization.get(locale, key, card=self._card_name(card, locale))

    def _is_play_selected_enabled(self, player: Player) -> str | None:
        disabled = self._is_current_player_action_enabled(player)
        if disabled:
            return disabled
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        selected_count = len(dmd_player.selected_card_ids)
        if selected_count < 1:
            return "deadmansdeck-select-card-first"
        if selected_count > MAX_CLAIM_CARDS:
            return "deadmansdeck-too-many-selected"
        return None

    def _is_play_selected_hidden(self, player: Player) -> Visibility:
        if self._is_current_player_action_enabled(player):
            return Visibility.HIDDEN
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        if dmd_player.selected_card_ids:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_clear_selection_enabled(self, player: Player) -> str | None:
        disabled = self._is_current_player_action_enabled(player)
        if disabled:
            return disabled
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        if not dmd_player.selected_card_ids:
            return "deadmansdeck-select-card-first"
        return None

    def _is_clear_selection_hidden(self, player: Player) -> Visibility:
        if self._is_current_player_action_enabled(player):
            return Visibility.HIDDEN
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        return Visibility.VISIBLE if dmd_player.selected_card_ids else Visibility.HIDDEN

    def _is_call_liar_enabled(self, player: Player) -> str | None:
        disabled = self._is_current_player_action_enabled(player)
        if disabled:
            return disabled
        if not self.last_claim:
            return "deadmansdeck-no-claim-to-challenge"
        if self.last_claim.player_id == player.id:
            return "deadmansdeck-cannot-challenge-self"
        return None

    def _is_call_liar_hidden(self, player: Player) -> Visibility:
        if self._is_current_player_action_enabled(player):
            return Visibility.HIDDEN
        if not self.last_claim or self.last_claim.player_id == player.id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_read_hand_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_read_hand_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing" and not player.is_spectator:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_public_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_public_info_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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

    def _action_select_card(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        block_reason = self._select_card_block_reason(player)
        if block_reason:
            if user:
                user.speak_l(block_reason, buffer="game")
            return

        card = self._card_for_action(player, action_id)
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        if not card:
            if user:
                user.speak_l("deadmansdeck-card-not-found", buffer="game")
            return

        if card.id in dmd_player.selected_card_ids:
            dmd_player.selected_card_ids.remove(card.id)
            key = "deadmansdeck-card-unselected"
        else:
            if len(dmd_player.selected_card_ids) >= MAX_CLAIM_CARDS:
                if user:
                    user.speak_l("deadmansdeck-too-many-selected", buffer="game")
                return
            dmd_player.selected_card_ids.append(card.id)
            key = "deadmansdeck-card-selected"

        if user:
            user.speak_l(key, buffer="game", card=self._card_name(card, user.locale))
        self.request_menu_focus(player, action_id)

    def _action_clear_selection(self, player: Player, action_id: str) -> None:
        disabled = self._is_clear_selection_enabled(player)
        user = self.get_user(player)
        if disabled:
            if user:
                user.speak_l(disabled, buffer="game")
            return
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        dmd_player.selected_card_ids.clear()
        if user:
            user.speak_l(
                "deadmansdeck-selection-cleared",
                buffer="game",
                history=False,
            )
        self.refresh_menus(player)

    def _action_play_selected(self, player: Player, action_id: str) -> None:
        disabled = self._is_play_selected_enabled(player)
        user = self.get_user(player)
        if disabled:
            if user:
                user.speak_l(disabled, buffer="game")
            return
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        selected_cards = self._selected_cards(dmd_player)
        if not (1 <= len(selected_cards) <= MAX_CLAIM_CARDS):
            if user:
                user.speak_l("deadmansdeck-select-card-first", buffer="game")
            return

        self._accept_previous_claim()
        selected_ids = {card.id for card in selected_cards}
        dmd_player.hand = [card for card in dmd_player.hand if card.id not in selected_ids]
        self._sort_hand(dmd_player)
        dmd_player.selected_card_ids.clear()
        self.last_claim = DeadMansDeckClaim(
            player_id=dmd_player.id,
            player_name=dmd_player.name,
            cards=selected_cards,
            target_rank=self.target_rank,
        )
        self.phase = PHASE_CLAIM
        self.refresh_menus()

        play_sound = self._random_play_sound()
        self.start_sequence(
            "deadmansdeck_claim",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(play_sound),
                        SequenceOperation.callback_op(
                            "announce_claim",
                            {"player_id": dmd_player.id},
                        ),
                    ],
                    delay_after_ticks=self._sound_ticks(play_sound),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("finish_claim")],
                ),
            ],
            tag="deadmansdeck_claim",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _action_call_liar(self, player: Player, action_id: str) -> None:
        disabled = self._is_call_liar_enabled(player)
        user = self.get_user(player)
        if disabled:
            if user:
                user.speak_l(disabled, buffer="game")
            return
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        self._start_challenge_sequence(dmd_player, forced=False)

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        if dmd_player.eliminated:
            user.speak_l("deadmansdeck-you-are-eliminated", buffer="game")
            return
        if dmd_player.hand:
            user.speak_l(
                "deadmansdeck-your-hand",
                buffer="game",
                cards=self._format_cards(dmd_player.hand, user.locale),
            )
        else:
            user.speak_l("deadmansdeck-hand-empty", buffer="game")

    def _action_read_card_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        first_player = next(iter(self.get_active_players()), None)
        self.live_status_box(
            player,
            "deadmansdeck_card_counts",
            lambda _player, live_user: self._card_count_items(live_user.locale),
            focus_id=f"cards:{first_player.id}" if first_player else None,
        )

    def _action_read_table(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        self.live_status_box(
            player,
            "deadmansdeck_table",
            lambda _player, live_user: self._table_status_items(live_user.locale),
            focus_id="round",
        )

    def _action_read_revolvers(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self.live_status_box(
            player,
            "deadmansdeck_revolvers",
            lambda _player, live_user: self._revolver_status_items(live_user.locale),
            focus_id="header",
        )

    def _card_count_items(self, locale: str) -> list[MenuItem]:
        items: list[MenuItem] = []
        for table_player in self.get_active_players():
            dmd_player: DeadMansDeckPlayer = table_player  # type: ignore[assignment]
            if dmd_player.eliminated:
                text = Localization.get(
                    locale,
                    "deadmansdeck-card-count-eliminated",
                    player=dmd_player.name,
                )
            else:
                text = Localization.get(
                    locale,
                    "deadmansdeck-card-count-line",
                    player=dmd_player.name,
                    count=len(dmd_player.hand),
                )
            items.append(MenuItem(text=text, id=f"cards:{dmd_player.id}"))
        return items

    def _table_status_items(self, locale: str) -> list[MenuItem]:
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "deadmansdeck-table-round",
                    round=self.round,
                    target=(
                        self._rank_name(self.target_rank, locale, plural=True)
                        if self.target_rank
                        else Localization.get(
                            locale,
                            "deadmansdeck-table-target-pending",
                        )
                    ),
                ),
                id="round",
            )
        ]
        current = self.current_player
        if current:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "deadmansdeck-table-current-turn",
                        player=current.name,
                    ),
                    id="current_turn",
                )
            )
        if self.last_claim:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "deadmansdeck-table-last-claim",
                        player=self.last_claim.player_name,
                        claim=self._claim_text(
                            self.last_claim.count,
                            self.last_claim.target_rank,
                            locale,
                        ),
                    ),
                    id="last_claim",
                )
            )
        else:
            items.append(
                MenuItem(
                    text=Localization.get(locale, "deadmansdeck-table-no-claim"),
                    id="last_claim",
                )
            )

        alive_names = [p.name for p in self.alive_players]
        items.append(
            MenuItem(
                text=Localization.get(
                    locale,
                    "deadmansdeck-table-alive",
                    players=Localization.format_list_and(locale, alive_names),
                ),
                id="alive",
            )
        )
        eliminated = [
            p.name
            for p in self.get_active_players()
            if isinstance(p, DeadMansDeckPlayer) and p.eliminated
        ]
        if eliminated:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "deadmansdeck-table-eliminated",
                        players=Localization.format_list_and(locale, eliminated),
                    ),
                    id="eliminated",
                )
            )
        return items

    def _revolver_status_items(self, locale: str) -> list[MenuItem]:
        items = [
            MenuItem(
                text=Localization.get(locale, "deadmansdeck-revolvers-header"),
                id="header",
            )
        ]
        for table_player in self.get_active_players():
            dmd_player: DeadMansDeckPlayer = table_player  # type: ignore[assignment]
            if dmd_player.eliminated:
                items.append(
                    MenuItem(
                        text=Localization.get(
                            locale,
                            "deadmansdeck-revolver-eliminated",
                            player=dmd_player.name,
                        ),
                        id=f"revolver:{dmd_player.id}",
                    )
                )
                continue
            remaining = max(1, CHAMBER_COUNT - dmd_player.chamber_index)
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "deadmansdeck-revolver-status",
                        player=dmd_player.name,
                        survived=dmd_player.chamber_index,
                        remaining=remaining,
                    ),
                    id=f"revolver:{dmd_player.id}",
                )
            )
        return items

    def _card_for_action(
        self,
        player: Player,
        action_id: str | None,
    ) -> DeadMansDeckCard | None:
        if not action_id or not action_id.startswith("select_card_"):
            return None
        try:
            card_id = int(action_id.removeprefix("select_card_"))
        except ValueError:
            return None
        dmd_player: DeadMansDeckPlayer = player  # type: ignore[assignment]
        for card in dmd_player.hand:
            if card.id == card_id:
                return card
        return None

    def _selected_cards(self, player: DeadMansDeckPlayer) -> list[DeadMansDeckCard]:
        selected_ids = set(player.selected_card_ids)
        return [card for card in player.hand if card.id in selected_ids]

    def _accept_previous_claim(self) -> None:
        if not self.last_claim:
            return

        claimer = self.get_player_by_id(self.last_claim.player_id)
        if isinstance(claimer, DeadMansDeckPlayer):
            if self._is_truthful_claim(self.last_claim):
                claimer.truthful_claims += 1
            else:
                claimer.successful_bluffs += 1

    def _start_challenge_sequence(
        self,
        challenger: DeadMansDeckPlayer,
        *,
        forced: bool,
    ) -> None:
        if not self.last_claim:
            return

        truthful = self._is_truthful_claim(self.last_claim)
        self.pending_challenger_id = challenger.id
        self.pending_accused_id = self.last_claim.player_id
        self.pending_challenge_success = not truthful
        self.pending_penalty_player_id = (
            self.last_claim.player_id if not truthful else challenger.id
        )
        self.phase = PHASE_CHALLENGE
        self.refresh_menus()

        result_sound = (
            SOUND_CHALLENGE_SUCCESS
            if self.pending_challenge_success
            else SOUND_CHALLENGE_FAIL
        )
        self.start_sequence(
            "deadmansdeck_challenge",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_CHALLENGE),
                        SequenceOperation.callback_op(
                            "announce_challenge",
                            {"challenger_id": challenger.id, "forced": forced},
                        ),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_CHALLENGE),
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_REVEAL),
                        SequenceOperation.callback_op("announce_revealed_cards"),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_REVEAL),
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(result_sound),
                        SequenceOperation.callback_op("announce_challenge_result"),
                    ],
                    delay_after_ticks=self._sound_ticks(result_sound),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("finish_challenge")],
                ),
            ],
            tag="deadmansdeck_challenge",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _announce_revealed_cards(self) -> None:
        claim = self.last_claim
        accused = self.get_player_by_id(self.pending_accused_id)
        if not claim or not isinstance(accused, DeadMansDeckPlayer):
            return

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id == accused.id:
                user.speak_l(
                    "deadmansdeck-your-revealed-cards",
                    buffer="game",
                    cards=self._format_cards(claim.cards, user.locale),
                )
            else:
                user.speak_l(
                    "deadmansdeck-revealed-cards",
                    buffer="game",
                    player=accused.name,
                    cards=self._format_cards(claim.cards, user.locale),
                )

    def _announce_challenge_result(self) -> None:
        challenger = self.get_player_by_id(self.pending_challenger_id)
        accused = self.get_player_by_id(self.pending_accused_id)
        penalty_player = self.get_player_by_id(self.pending_penalty_player_id)

        if (
            not isinstance(challenger, DeadMansDeckPlayer)
            or not isinstance(accused, DeadMansDeckPlayer)
            or not isinstance(penalty_player, DeadMansDeckPlayer)
        ):
            return

        if self.pending_challenge_success:
            challenger.correct_challenges += 1
        else:
            challenger.failed_challenges += 1
            accused.truthful_claims += 1
        self._broadcast_challenge_result(challenger, accused)

    def _finish_challenge(self) -> None:
        penalty_player = self.get_player_by_id(self.pending_penalty_player_id)
        if not isinstance(penalty_player, DeadMansDeckPlayer):
            self.phase = PHASE_PLAYING
            self._start_round()
            return

        self.last_claim = None
        self.next_round_starter_id = penalty_player.id
        self._start_roulette_sequence(penalty_player)

    def _start_roulette_sequence(self, player: DeadMansDeckPlayer) -> None:
        self.phase = PHASE_ROULETTE
        self.pending_penalty_player_id = player.id
        lethal = player.chamber_index == player.bullet_position
        self.broadcast_personal_l(
            player,
            "deadmansdeck-you-face-revolver",
            "deadmansdeck-roulette-start",
            buffer="game",
        )
        self.refresh_menus()

        if lethal:
            body_fall = self._random_body_fall_sound()
            beats = [
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(SOUND_COCK)],
                    delay_after_ticks=COCK_TO_OUTCOME_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_GUNSHOT),
                        SequenceOperation.sound_op(SOUND_BULLET_HIT),
                        SequenceOperation.callback_op("announce_roulette_elimination"),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_GUNSHOT),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(body_fall)],
                    delay_after_ticks=self._sound_ticks(body_fall),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("finish_roulette_elimination")],
                ),
            ]
        else:
            casing_sound = self._random_empty_casing_sound()
            beats = [
                SequenceBeat(
                    ops=[SequenceOperation.sound_op(SOUND_COCK)],
                    delay_after_ticks=COCK_TO_OUTCOME_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_EMPTY_CLICK),
                        SequenceOperation.sound_op(casing_sound),
                        SequenceOperation.callback_op("announce_roulette_survival"),
                    ],
                    delay_after_ticks=max(
                        self._sound_ticks(SOUND_EMPTY_CLICK),
                        self._sound_ticks(casing_sound),
                    ),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("finish_roulette_survival")],
                ),
            ]

        self.start_sequence(
            "deadmansdeck_roulette",
            beats,
            tag="deadmansdeck_roulette",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _announce_roulette_survival(self) -> None:
        player = self.get_player_by_id(self.pending_penalty_player_id)
        if not isinstance(player, DeadMansDeckPlayer) or player.eliminated:
            return

        player.chamber_index += 1
        player.roulette_survivals += 1
        remaining = max(1, CHAMBER_COUNT - player.chamber_index)
        self.broadcast_personal_l(
            player,
            "deadmansdeck-you-roulette-survived",
            "deadmansdeck-roulette-survived",
            buffer="game",
            remaining=remaining,
        )
        self.refresh_menus()

    def _finish_roulette_survival(self) -> None:
        self._start_round()

    def _announce_roulette_elimination(self) -> None:
        player = self.get_player_by_id(self.pending_penalty_player_id)
        if not isinstance(player, DeadMansDeckPlayer) or player.eliminated:
            return

        player.eliminated = True
        player.hand.clear()
        player.selected_card_ids.clear()
        self.broadcast_personal_l(
            player,
            "deadmansdeck-you-eliminated-by-gun",
            "deadmansdeck-player-eliminated",
            buffer="game",
        )
        self.refresh_menus()

    def _finish_roulette_elimination(self) -> None:
        if not self._check_game_end():
            self._start_round()

    def _check_game_end(self) -> bool:
        alive = self.alive_players
        if len(alive) == 1:
            self._start_game_over_sequence(alive[0])
            return True
        if len(alive) == 0 and self.get_active_players():
            self._start_game_over_sequence(None)
            return True
        return False

    def _start_game_over_sequence(self, winner: DeadMansDeckPlayer | None) -> None:
        if self.phase == PHASE_GAME_OVER or self.status == "finished":
            return
        self.phase = PHASE_GAME_OVER
        self.winner_id = winner.id if winner else ""
        self.cancel_sequences_by_tag("deadmansdeck_round_start")
        self.cancel_sequences_by_tag("deadmansdeck_claim")
        self.cancel_sequences_by_tag("deadmansdeck_challenge")
        self.cancel_sequences_by_tag("deadmansdeck_roulette")
        self.start_sequence(
            "deadmansdeck_game_over",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(SOUND_GAME_OVER),
                        SequenceOperation.callback_op("announce_game_over"),
                    ],
                    delay_after_ticks=self._sound_ticks(SOUND_GAME_OVER),
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("finish_game")],
                ),
            ],
            tag="deadmansdeck_game_over",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        del sequence_id
        if callback_id == "announce_prepare_revolvers":
            self.broadcast_l("deadmansdeck-prepare-revolver", buffer="game")
            return

        if callback_id == "mark_revolver_prepared":
            player = self.get_player_by_id(payload.get("player_id", ""))
            if isinstance(player, DeadMansDeckPlayer):
                player.revolver_prepared = True
            return

        if callback_id == "start_preparation_music":
            self.play_music(SOUND_MUSIC)
            return

        if callback_id == "finish_preparation":
            self._start_round()
            return

        if callback_id == "announce_round_start":
            self._announce_round_start()
            return

        if callback_id == "announce_claim":
            player = self.get_player_by_id(payload.get("player_id", ""))
            if self.last_claim and isinstance(player, DeadMansDeckPlayer):
                for listener in self.players:
                    user = self.get_user(listener)
                    if not user:
                        continue
                    claim_text = self._claim_text(
                        self.last_claim.count,
                        self.last_claim.target_rank,
                        user.locale,
                    )
                    if listener.id == player.id:
                        user.speak_l(
                            "deadmansdeck-you-claim",
                            buffer="game",
                            claim=claim_text,
                        )
                    else:
                        user.speak_l(
                            "deadmansdeck-player-claims",
                            buffer="game",
                            player=player.name,
                            claim=claim_text,
                        )
                if not player.hand:
                    self.broadcast_personal_l(
                        player,
                        "deadmansdeck-you-out-of-cards",
                        "deadmansdeck-player-out-of-cards",
                        buffer="game",
                    )
            return

        if callback_id == "finish_claim":
            self.phase = PHASE_PLAYING
            self._advance_after_claim()
            return

        if callback_id == "announce_challenge":
            challenger = self.get_player_by_id(payload.get("challenger_id", ""))
            accused = self.get_player_by_id(self.pending_accused_id)
            if isinstance(challenger, DeadMansDeckPlayer) and isinstance(
                accused,
                DeadMansDeckPlayer,
            ):
                self._broadcast_challenge_call(
                    challenger,
                    accused,
                    forced=bool(payload.get("forced")),
                )
            return

        if callback_id == "announce_revealed_cards":
            self._announce_revealed_cards()
            return

        if callback_id == "announce_challenge_result":
            self._announce_challenge_result()
            return

        if callback_id == "finish_challenge":
            self._finish_challenge()
            return

        if callback_id == "announce_roulette_survival":
            self._announce_roulette_survival()
            return

        if callback_id == "finish_roulette_survival":
            self._finish_roulette_survival()
            return

        if callback_id == "announce_roulette_elimination":
            self._announce_roulette_elimination()
            return

        if callback_id == "finish_roulette_elimination":
            self._finish_roulette_elimination()
            return

        if callback_id == "announce_game_over":
            winner = self.get_player_by_id(self.winner_id) if self.winner_id else None
            if winner:
                self.broadcast_personal_l(
                    winner,
                    "deadmansdeck-you-win-game",
                    "deadmansdeck-player-wins",
                    buffer="game",
                )
            else:
                self.broadcast_l("deadmansdeck-no-winner", buffer="game")
            return

        if callback_id == "finish_game":
            self.finish_game()

    def _is_truthful_claim(self, claim: DeadMansDeckClaim) -> bool:
        return all(card.rank in {claim.target_rank, RANK_JOKER} for card in claim.cards)

    def _rank_name(self, rank: str, locale: str, *, plural: bool = False) -> str:
        suffix = "-plural" if plural else ""
        return Localization.get(locale, f"deadmansdeck-rank-{rank}{suffix}")

    def _card_name(self, card: DeadMansDeckCard, locale: str) -> str:
        return self._rank_name(card.rank, locale)

    def _format_cards(self, cards: list[DeadMansDeckCard], locale: str) -> str:
        if not cards:
            return Localization.get(locale, "deadmansdeck-no-cards")
        names = [self._card_name(card, locale) for card in self._sorted_cards(cards)]
        return Localization.format_list_and(locale, names)

    def _claim_text(self, count: int, rank: str, locale: str) -> str:
        return Localization.get(
            locale,
            "deadmansdeck-claim-text",
            count=count,
            rank=self._rank_name(rank, locale, plural=count != 1),
        )

    def bot_think(self, player: DeadMansDeckPlayer) -> str | None:
        return _bot_think(self, player)

    def build_game_result(self) -> GameResult:
        active_players = [
            p for p in self.get_active_players() if isinstance(p, DeadMansDeckPlayer)
        ]
        winner = self.get_player_by_id(self.winner_id) if self.winner_id else None
        winner_ids = [winner.id] if winner else []
        rankings = sorted(
            active_players,
            key=lambda p: (0 if p.id == self.winner_id else 1, p.eliminated, p.name),
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
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot and not p.replaced_human,
                )
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": winner_ids,
                "rounds_played": self.round,
                "team_rankings": team_rankings,
                "player_stats": {
                    p.name: {
                        "correct_challenges": p.correct_challenges,
                        "failed_challenges": p.failed_challenges,
                        "successful_bluffs": p.successful_bluffs,
                        "truthful_claims": p.truthful_claims,
                        "roulette_survivals": p.roulette_survivals,
                        "eliminated": p.eliminated,
                    }
                    for p in active_players
                },
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "deadmansdeck-results-header")]
        winner_name = result.custom_data.get("winner_name")
        if winner_name:
            lines.append(Localization.get(locale, "deadmansdeck-results-winner", player=winner_name))

        stats = result.custom_data.get("player_stats", {})
        for player in result.player_results:
            data = stats.get(player.player_name, {})
            status_key = (
                "deadmansdeck-results-survived"
                if player.player_name == winner_name
                else "deadmansdeck-results-eliminated"
            )
            lines.append(
                Localization.get(
                    locale,
                    "deadmansdeck-results-line",
                    player=player.player_name,
                    status=Localization.get(locale, status_key),
                    correct=data.get("correct_challenges", 0),
                    bluffs=data.get("successful_bluffs", 0),
                    survivals=data.get("roulette_survivals", 0),
                )
            )
        return lines
