"""Flip 7 push-your-luck card game."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from mashumaro.mixins.json import DataClassJSONMixin

from .bot import bot_think
from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...game_utils.menu_management_mixin import MenuBuild
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem

FLIP_SEVEN_TARGET = 7
FLIP_SEVEN_BONUS = 15
FLIP_THREE_COUNT = 3
MAX_NUMBER = 12
MODIFIER_VALUES = (2, 4, 6, 8, 10)
ACTION_COPIES = 3

CARD_NUMBER = "number"
CARD_MODIFIER = "modifier"
CARD_DOUBLE = "double"
CARD_SECOND_CHANCE = "second_chance"
CARD_STOP = "stop"
CARD_FLIP_THREE = "flip_three"

STATUS_PLAYING = "playing"
STATUS_STAYED = "stayed"
STATUS_BUSTED = "busted"

PHASE_PLAYING = "playing"
PHASE_ROUND_END = "round_end"
PHASE_MATCH_END = "match_end"

CHOICE_STOP = "stop"
CHOICE_FLIP_THREE = "flip_three"
CHOICE_SECOND_CHANCE = "second_chance"

# Choice kinds use ids internally but hyphenated suffixes in locale keys.
CHOICE_KEY_SUFFIX = {
    CHOICE_STOP: "stop",
    CHOICE_FLIP_THREE: "flip-three",
    CHOICE_SECOND_CHANCE: "second-chance",
}

OUTCOME_OK = "ok"
OUTCOME_SAVED = "saved"
OUTCOME_BUST = "bust"
OUTCOME_FLIP7 = "flip7"
OUTCOME_CHOICE = "choice"
OUTCOME_ROUND_END = "round_end"

SEQUENCE_FLIP_THREE = "flip7_flip_three"
SEQUENCE_CARD_REVEAL_PREFIX = "flip7_card_reveal"
SEQUENCE_CARD_FLOW_PREFIX = "flip7_card_flow"
TAG_FLIP_THREE = "flip7_flip_three"
TICKS_PER_SECOND = 20
CARD_REVEAL_DELAY_TICKS = TICKS_PER_SECOND
CARD_REVEAL_POST_DELAY_TICKS = TICKS_PER_SECOND // 2
CARD_REVEAL_TOTAL_TICKS = CARD_REVEAL_DELAY_TICKS + CARD_REVEAL_POST_DELAY_TICKS
ROUND_END_PRE_DELAY_TICKS = TICKS_PER_SECOND + TICKS_PER_SECOND // 2
NEXT_ROUND_DELAY_TICKS = TICKS_PER_SECOND * 2
FLIP_THREE_GAP_TICKS = CARD_REVEAL_TOTAL_TICKS
INITIAL_DEAL_GAP_TICKS = TICKS_PER_SECOND
ROUND_START_SOUND_TICKS = TICKS_PER_SECOND * 5 // 2
FLIP_THREE_START_SOUND_TICKS = TICKS_PER_SECOND
BOT_MIN_THINK_TICKS = TICKS_PER_SECOND
BOT_MAX_THINK_TICKS = TICKS_PER_SECOND + TICKS_PER_SECOND // 2

SOUND_DEAL_VARIANTS = (
    "game_flip7/card_number1.ogg",
    "game_flip7/card_number2.ogg",
    "game_flip7/card_number3.ogg",
    "game_flip7/card_number4.ogg",
)
SOUND_SHUFFLE_VARIANTS = (
    "game_flip7/shuffle1.ogg",
    "game_flip7/shuffle2.ogg",
    "game_flip7/shuffle3.ogg",
)
SOUND_STAY_VARIANTS = (
    "game_flip7/bank_points.ogg",
)
SOUND_MODIFIER_BY_VALUE = {
    2: "game_flip7/modifier_plus_2.ogg",
    4: "game_flip7/modifier_plus_4.ogg",
    6: "game_flip7/modifier_plus_6.ogg",
    8: "game_flip7/modifier_plus_8.ogg",
    10: "game_flip7/modifier_plus_10.ogg",
}
SOUND_DOUBLE = "game_flip7/double.ogg"
SOUND_SECOND_CHANCE = "game_flip7/second_chance.ogg"
SOUND_SECOND_CHANCE_SAVE = "game_flip7/second_chance_save.ogg"
SOUND_STOP = "game_flip7/stop.ogg"
SOUND_FLIP_THREE = "game_flip7/flip_three.ogg"
SOUND_BUST = "game_flip7/bust.ogg"
SOUND_FLIP_SEVEN = "game_flip7/flip_seven.ogg"
SOUND_ROUND_START = "game_flip7/round_start.ogg"
SOUND_ROUND_END = "game_flip7/round_end.ogg"
SOUND_MATCH_WIN = "game_flip7/match_win.ogg"
SOUND_PLAY_MUSIC = "game_3cardpoker/mus.ogg"


@dataclass
class Flip7Card(DataClassJSONMixin):
    """One physical card of the 94-card Flip 7 deck."""

    kind: str
    value: int = 0
    uid: int = 0


@dataclass
class Flip7Choice(DataClassJSONMixin):
    """A pending targeted choice one player still has to make."""

    kind: str
    actor_slot: int = -1


@dataclass
class Flip7FlipState(DataClassJSONMixin):
    """In-progress Flip Three reveal."""

    target_slot: int = -1
    chooser_slot: int = -1
    remaining: int = FLIP_THREE_COUNT
    stops: int = 0
    flips: int = 0
    second_chances: int = 0


@dataclass
class Flip7Player(Player):
    """Player state for Flip 7."""

    total_score: int = 0
    numbers: list[int] = field(default_factory=list)
    modifiers: list[int] = field(default_factory=list)
    has_double: bool = False
    second_chance: bool = False
    round_status: str = STATUS_PLAYING
    hits_taken: int = 0
    busts: int = 0
    flip_sevens: int = 0


@dataclass
class Flip7Options(GameOptions):
    """Options for Flip 7."""

    target_score: int = option_field(
        IntOption(
            default=200,
            min_val=50,
            max_val=1000,
            value_key="score",
            label="flip7-set-target-score",
            prompt="flip7-enter-target-score",
            change_msg="flip7-option-changed-target",
        )
    )


@dataclass
@register_game
class Flip7Game(Game):
    """
    Flip 7: push-your-luck card game played in rounds toward a target score.

    Each round every player collects number and modifier cards. Drawing a
    number already in your area busts the round for you unless a Second Chance
    is set aside. Seven unique numbers score the Flip 7 bonus and end the round
    for everybody at once.
    """

    relevant_preferences = ["brief_announcements"]

    players: list[Flip7Player] = field(default_factory=list)
    options: Flip7Options = field(default_factory=Flip7Options)

    round: int = 0
    dealer_index: int = -1
    deck: list[Flip7Card] = field(default_factory=list)
    discard: list[Flip7Card] = field(default_factory=list)
    phase: str = PHASE_PLAYING
    deal_order: list[str] = field(default_factory=list)
    deal_index: int = 0
    deal_delay_ticks: int = 0
    pending_choice: Flip7Choice | None = None
    choice_queue: list[str] = field(default_factory=list)
    flip_state: Flip7FlipState | None = None

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @classmethod
    def get_name(cls) -> str:
        return "Flip 7"

    @classmethod
    def get_type(cls) -> str:
        return "flip7"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 10

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "total_score", "high_score", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> Flip7Player:
        return Flip7Player(id=player_id, name=name, is_bot=is_bot)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _active(self) -> list[Flip7Player]:
        return [
            p for p in self.get_active_players() if isinstance(p, Flip7Player)
        ]

    def _player_at(self, slot: int) -> Flip7Player | None:
        if 0 <= slot < len(self.players):
            player = self.players[slot]
            if isinstance(player, Flip7Player):
                return player
        return None

    def _slot_of(self, player: Player | None) -> int:
        if player is None:
            return -1
        for index, candidate in enumerate(self.players):
            if candidate is player:
                return index
        return -1

    def _locale_of(self, player: Player | None) -> str:
        user = self.get_user(player) if player else None
        return user.locale if user else "en"

    def _choice_actor(self) -> Flip7Player | None:
        if self.pending_choice is None:
            return None
        return self._player_at(self.pending_choice.actor_slot)

    def _choice_targets(self) -> list[Flip7Player]:
        if self.pending_choice is None:
            return []
        kind = self.pending_choice.kind
        actor = self._choice_actor()
        targets: list[Flip7Player] = []
        for player in self._active():
            if player.round_status != STATUS_PLAYING:
                continue
            if kind == CHOICE_SECOND_CHANCE:
                if player is actor or player.second_chance:
                    continue
            targets.append(player)
        return targets

    def _has_cards(self, player: Flip7Player) -> bool:
        return bool(player.numbers or player.modifiers or player.has_double)

    def round_points(self, player: Flip7Player) -> int:
        """Number cards doubled first, then the flat modifiers added."""
        total = sum(player.numbers)
        if player.has_double:
            total *= 2
        return total + sum(player.modifiers)

    @staticmethod
    def build_deck() -> list[Flip7Card]:
        """Build the 94-card deck: 79 numbers, 6 modifiers, 9 actions."""
        cards: list[Flip7Card] = []

        def add(kind: str, value: int = 0) -> None:
            cards.append(Flip7Card(kind=kind, value=value, uid=len(cards)))

        add(CARD_NUMBER, 0)
        for number in range(1, MAX_NUMBER + 1):
            for _ in range(number):
                add(CARD_NUMBER, number)
        for value in MODIFIER_VALUES:
            add(CARD_MODIFIER, value)
        add(CARD_DOUBLE)
        for _ in range(ACTION_COPIES):
            add(CARD_SECOND_CHANCE)
            add(CARD_STOP)
            add(CARD_FLIP_THREE)
        return cards

    def _card_label(self, card: Flip7Card, locale: str) -> str:
        if card.kind == CARD_NUMBER:
            return Localization.get(locale, "flip7-card-number", value=card.value)
        if card.kind == CARD_MODIFIER:
            return Localization.get(locale, "flip7-card-modifier", value=card.value)
        if card.kind == CARD_DOUBLE:
            return Localization.get(locale, "flip7-card-double")
        if card.kind == CARD_SECOND_CHANCE:
            return Localization.get(locale, "flip7-card-second-chance")
        if card.kind == CARD_STOP:
            return Localization.get(locale, "flip7-card-stop")
        return Localization.get(locale, "flip7-card-flip-three")

    def _draw_card(self) -> Flip7Card | None:
        if not self.deck and not self._reshuffle_discard():
            return None
        if not self.deck:
            return None
        return self.deck.pop()

    def _reshuffle_discard(self) -> bool:
        if not self.discard:
            return False
        self.deck = list(self.discard)
        self.discard = []
        random.shuffle(self.deck)
        self.play_sound(random.choice(SOUND_SHUFFLE_VARIANTS))
        self.broadcast_l("flip7-deck-reshuffled", buffer="game")
        return True

    def _discard(self, card: Flip7Card | None) -> None:
        if card is not None:
            self.discard.append(card)

    def _return_area_cards(self, player: Flip7Player) -> None:
        for value in player.numbers:
            self._discard(Flip7Card(kind=CARD_NUMBER, value=value, uid=-1))
        for value in player.modifiers:
            self._discard(Flip7Card(kind=CARD_MODIFIER, value=value, uid=-1))
        if player.has_double:
            self._discard(Flip7Card(kind=CARD_DOUBLE, uid=-1))
        player.numbers = []
        player.modifiers = []
        player.has_double = False
        player.second_chance = False

    def _next_playing_slot(self, start: int) -> int:
        total = len(self.turn_player_ids)
        if total == 0:
            return -1
        for step in range(1, total + 1):
            index = (start + step) % total
            player = self.get_player_by_id(self.turn_player_ids[index])
            if (
                isinstance(player, Flip7Player)
                and player.round_status == STATUS_PLAYING
            ):
                return index
        return -1

    def _arm_bot(self) -> None:
        player = self._active_actor()
        if player is not None and player.is_bot:
            if player.bot_think_ticks <= 0 and not player.bot_pending_action:
                player.bot_think_ticks = random.randint(
                    BOT_MIN_THINK_TICKS,
                    BOT_MAX_THINK_TICKS,
                )
            BotHelper.set_target(player, 0)

    def _active_actor(self) -> Flip7Player | None:
        if self.phase != PHASE_PLAYING or self.status != "playing":
            return None
        if self.pending_choice is not None:
            return self._choice_actor()
        if self.flip_state is not None:
            return None
        if self.deal_index < len(self.deal_order):
            return None
        current = self.current_player
        if isinstance(current, Flip7Player) and current.round_status == STATUS_PLAYING:
            return current
        return None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.dealer_index = -1
        self.deck = []
        self.discard = []
        self.deal_order = []
        self.deal_index = 0
        self.pending_choice = None
        self.choice_queue = []
        self.flip_state = None

        active = self._active()
        for player in active:
            player.total_score = 0
            player.hits_taken = 0
            player.busts = 0
            player.flip_sevens = 0

        self.set_turn_players(active)
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active])
        self._team_manager.reset_all_scores()

        self.play_music(SOUND_PLAY_MUSIC)
        self._start_round()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if not self.game_active:
            return
        self._tick_initial_deal()
        if self.deal_index < len(self.deal_order):
            self._drive_choice_bot()
            return
        if self.is_sequence_bot_paused():
            return
        BotHelper.on_tick(self)
        self._drive_choice_bot()

    def _tick_initial_deal(self) -> None:
        if self.status != "playing" or self.phase != PHASE_PLAYING:
            return
        if self.deal_index >= len(self.deal_order):
            return
        if self.pending_choice is not None or self.flip_state is not None:
            return
        if self.is_sequence_bot_paused():
            return
        self.deal_delay_ticks -= 1
        if self.deal_delay_ticks > 0:
            return
        self._deal_step()
        if self.deal_index < len(self.deal_order):
            self.deal_delay_ticks = INITIAL_DEAL_GAP_TICKS

    def _drive_choice_bot(self) -> None:
        """Answer a pending choice for a bot that is not the turn player.

        ``BotHelper.on_tick`` only ever asks ``current_player`` for a
        decision, so a forced action card turned outside the normal turn
        (during the deal, or from a Flip Three aimed at someone else) would
        otherwise wait for a human that may never come.
        """
        if self.pending_choice is None:
            return
        actor = self._choice_actor()
        if actor is None or not actor.is_bot or actor is self.current_player:
            return
        if self._is_choose_target_enabled(actor) is not None:
            return
        BotHelper.process_bot_action(
            actor,
            lambda: bot_think(self, actor),
            lambda action_id: self.execute_action(actor, action_id),
        )

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if callback_id == "card_reveal":
            self._announce_revealed_card(payload)
            return
        if callback_id == "continue_flow":
            self._continue_flow()
            return
        if callback_id == "deal_step":
            self._deal_step()
            return
        if callback_id == "end_round":
            self._end_round()
            return
        if callback_id == "start_round":
            self._start_round()
            return
        if callback_id == "bust_announce":
            self._announce_bust(payload)
            return
        if callback_id == "second_chance_save":
            self._announce_second_chance_save(payload)
            return
        if callback_id == "award_flip_seven":
            target = self.get_player_by_id(str(payload.get("target_id", "")))
            if isinstance(target, Flip7Player):
                self._award_flip_seven(target)
            return
        if sequence_id != SEQUENCE_FLIP_THREE:
            return
        if callback_id == "flip_draw":
            self._flip_draw()
        elif callback_id == "flip_finish":
            self._flip_finish()

    def bot_think(self, player: Flip7Player) -> str | None:
        return bot_think(self, player)

    def _announce_revealed_card(self, payload: dict) -> None:
        target = self.get_player_by_id(str(payload.get("target_id", "")))
        if not isinstance(target, Flip7Player):
            return
        card = Flip7Card(
            kind=str(payload.get("kind", "")),
            value=int(payload.get("value", 0)),
        )
        self.broadcast_personal_l(
            target,
            "flip7-your-card-is",
            "flip7-player-card-is",
            buffer="game",
            card=lambda locale: self._card_label(card, locale),
        )
        sound = str(payload.get("sound", ""))
        if sound:
            self.play_sound(sound)

    def _card_effect_sound(self, card: Flip7Card, *, forced: bool) -> str:
        if card.kind == CARD_MODIFIER:
            return SOUND_MODIFIER_BY_VALUE.get(card.value, "")
        if card.kind == CARD_DOUBLE:
            return SOUND_DOUBLE
        if card.kind == CARD_SECOND_CHANCE and not forced:
            return SOUND_SECOND_CHANCE
        if card.kind == CARD_STOP:
            return SOUND_STOP
        if card.kind == CARD_FLIP_THREE and not forced:
            return SOUND_FLIP_THREE
        return ""

    def _card_reveal_sound(self, card: Flip7Card, *, forced: bool) -> str:
        return self._card_effect_sound(card, forced=forced) or random.choice(
            SOUND_DEAL_VARIANTS
        )

    def _schedule_card_reveal_announcement(
        self, target: Flip7Player, card: Flip7Card, *, forced: bool
    ) -> None:
        self.start_sequence(
            f"{SEQUENCE_CARD_REVEAL_PREFIX}_{target.id}_{self.sound_scheduler_tick}_{card.uid}",
            [
                SequenceBeat.pause(CARD_REVEAL_DELAY_TICKS),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "card_reveal",
                            {
                                "target_id": target.id,
                                "kind": card.kind,
                                "value": card.value,
                                "sound": self._card_reveal_sound(
                                    card, forced=forced
                                ),
                            },
                        )
                    ]
                ),
            ],
            pause_bots=False,
        )

    def _schedule_after_card_reveal(self, callback_id: str) -> None:
        self.start_sequence(
            f"{SEQUENCE_CARD_FLOW_PREFIX}_{callback_id}_{self.sound_scheduler_tick}",
            [
                SequenceBeat.pause(CARD_REVEAL_TOTAL_TICKS),
                SequenceBeat(ops=[SequenceOperation.callback_op(callback_id)]),
            ],
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _schedule_bust_announcement(self, target: Flip7Player, value: int) -> None:
        self.start_sequence(
            f"{SEQUENCE_CARD_FLOW_PREFIX}_bust_{target.id}_{self.sound_scheduler_tick}",
            [
                SequenceBeat.pause(CARD_REVEAL_DELAY_TICKS + 1),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "bust_announce",
                            {"target_id": target.id, "value": value},
                        )
                    ]
                ),
            ],
            pause_bots=False,
        )

    def _schedule_flip_seven_award(self, target: Flip7Player) -> None:
        self.start_sequence(
            f"{SEQUENCE_CARD_FLOW_PREFIX}_flip7_{target.id}_{self.sound_scheduler_tick}",
            [
                SequenceBeat.pause(CARD_REVEAL_TOTAL_TICKS),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "award_flip_seven", {"target_id": target.id}
                        )
                    ]
                ),
            ],
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _announce_bust(self, payload: dict) -> None:
        target = self.get_player_by_id(str(payload.get("target_id", "")))
        if not isinstance(target, Flip7Player):
            return
        value = int(payload.get("value", 0))
        self.play_sound(SOUND_BUST)
        self.broadcast_personal_l(
            target,
            "flip7-you-bust",
            "flip7-player-busts",
            buffer="game",
            value=value,
        )

    def _schedule_end_round(self) -> None:
        self.start_sequence(
            f"{SEQUENCE_CARD_FLOW_PREFIX}_end_round_{self.sound_scheduler_tick}",
            [
                SequenceBeat.pause(ROUND_END_PRE_DELAY_TICKS),
                SequenceBeat(ops=[SequenceOperation.callback_op("end_round")]),
            ],
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _schedule_start_round(self) -> None:
        self.start_sequence(
            f"{SEQUENCE_CARD_FLOW_PREFIX}_start_round_{self.sound_scheduler_tick}",
            [
                SequenceBeat.pause(NEXT_ROUND_DELAY_TICKS),
                SequenceBeat(ops=[SequenceOperation.callback_op("start_round")]),
            ],
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _schedule_second_chance_save(self, target: Flip7Player, value: int) -> None:
        self.start_sequence(
            f"{SEQUENCE_CARD_FLOW_PREFIX}_save_{target.id}_{self.sound_scheduler_tick}",
            [
                SequenceBeat.pause(CARD_REVEAL_DELAY_TICKS + 1),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "second_chance_save",
                            {"target_id": target.id, "value": value},
                        )
                    ]
                ),
            ],
            pause_bots=False,
        )

    def _announce_second_chance_save(self, payload: dict) -> None:
        target = self.get_player_by_id(str(payload.get("target_id", "")))
        if not isinstance(target, Flip7Player):
            return
        value = int(payload.get("value", 0))
        self.play_sound(SOUND_SECOND_CHANCE_SAVE)
        self.broadcast_personal_l(
            target,
            "flip7-second-chance-saves-you",
            "flip7-second-chance-saves",
            buffer="game",
            value=value,
        )

    # ------------------------------------------------------------------
    # Round flow
    # ------------------------------------------------------------------

    def _start_round(self) -> None:
        self.round += 1
        self.phase = PHASE_PLAYING
        self.pending_choice = None
        self.choice_queue = []
        self.flip_state = None
        self.cancel_sequences_by_tag(TAG_FLIP_THREE)

        active = self._active()
        for player in active:
            player.numbers = []
            player.modifiers = []
            player.has_double = False
            player.second_chance = False
            player.round_status = STATUS_PLAYING
        if not active:
            return

        if not self.deck and not self._reshuffle_discard():
            self.deck = self.build_deck()
            random.shuffle(self.deck)
            self.play_sound(random.choice(SOUND_SHUFFLE_VARIANTS))

        count = len(active)
        self.dealer_index = (self.dealer_index + 1) % count
        dealer = active[self.dealer_index]
        ordered = [active[(self.dealer_index + 1 + i) % count] for i in range(count)]
        self.deal_order = [p.id for p in ordered]
        self.deal_index = 0

        self.play_sound(SOUND_ROUND_START)
        self.broadcast_l(
            "flip7-round-start",
            buffer="game",
            round=self.round,
            dealer=dealer.name,
        )
        self.deal_delay_ticks = ROUND_START_SOUND_TICKS

    def _deal_step(self) -> None:
        if self.deal_index >= len(self.deal_order):
            self._begin_turn_order()
            return

        player = self.get_player_by_id(self.deal_order[self.deal_index])
        self.deal_index += 1
        if not isinstance(player, Flip7Player):
            self._deal_step()
            return
        # A Stop/Flip card already retired this player this round: they get no
        # start-of-round card and are skipped on later deals.
        if player.round_status != STATUS_PLAYING:
            self._deal_step()
            return

        card = self._draw_card()
        if card is None:
            self._end_round(deck_empty=True)
            return

        outcome = self._resolve_card(player, card, forced=False, chooser=player)
        if outcome == OUTCOME_FLIP7:
            self._schedule_flip_seven_award(player)
            return
        if outcome == OUTCOME_ROUND_END:
            return
        if outcome == OUTCOME_CHOICE:
            self._arm_bot()
            self.refresh_menus()
            return
        # A bust only removes that player; the rest still get dealt in.
        self._schedule_after_card_reveal("deal_step")

    def _begin_turn_order(self) -> None:
        ordered = [
            player
            for player in (
                self.get_player_by_id(pid) for pid in self.deal_order
            )
            if isinstance(player, Flip7Player)
        ]
        self.set_turn_players(ordered)
        index = self._next_playing_slot(-1)
        if index < 0:
            self._schedule_end_round()
            return
        self.turn_index = index
        self.announce_turn()
        self._arm_bot()
        self.refresh_menus()

    def _continue_flow(self) -> None:
        if self.pending_choice is not None or self.flip_state is not None:
            self.refresh_menus()
            return
        if self.deal_index < len(self.deal_order):
            self.deal_delay_ticks = INITIAL_DEAL_GAP_TICKS
            self.refresh_menus()
            return
        index = self._next_playing_slot(self.turn_index)
        if index < 0:
            self._schedule_end_round()
            return
        self.turn_index = index
        self.announce_turn()
        self._arm_bot()
        self.refresh_menus()

    # ------------------------------------------------------------------
    # Card resolution
    # ------------------------------------------------------------------

    def _resolve_card(
        self,
        target: Flip7Player,
        card: Flip7Card,
        *,
        forced: bool,
        chooser: Flip7Player,
    ) -> str:
        locale = self._locale_of(target)
        self.broadcast_personal_l(
            target,
            "flip7-you-turn-card",
            "flip7-player-turns-card",
            buffer="game",
        )
        self._schedule_card_reveal_announcement(target, card, forced=forced)
        label = self._card_label(card, locale)

        if card.kind == CARD_NUMBER:
            return self._resolve_number(target, card, label)
        if card.kind == CARD_MODIFIER:
            target.modifiers.append(card.value)
            target.modifiers.sort()
            return OUTCOME_OK
        if card.kind == CARD_DOUBLE:
            target.has_double = True
            return OUTCOME_OK
        if card.kind == CARD_SECOND_CHANCE:
            return self._resolve_second_chance(target, forced=forced, chooser=chooser)
        if card.kind == CARD_STOP:
            if forced:
                assert self.flip_state is not None
                self.flip_state.stops += 1
                return OUTCOME_OK
            if len(self._stop_targets()) == 1:
                self._stop_alone(target)
                return OUTCOME_OK
            self.broadcast_personal_l(
                target,
                "flip7-you-turn-stop",
                "flip7-player-turns-stop",
                buffer="game",
            )
            return self._open_choice(CHOICE_STOP, target)
        if forced:
            assert self.flip_state is not None
            self.flip_state.flips += 1
            return OUTCOME_OK
        return self._open_choice(CHOICE_FLIP_THREE, target)

    def _resolve_number(
        self, target: Flip7Player, card: Flip7Card, label: str
    ) -> str:
        if card.value in target.numbers:
            self._discard(card)
            if target.second_chance:
                target.second_chance = False
                self._schedule_second_chance_save(target, card.value)
                return OUTCOME_SAVED
            self._bust(target, card.value)
            return OUTCOME_BUST

        target.numbers.append(card.value)
        target.numbers.sort()
        if len(target.numbers) >= FLIP_SEVEN_TARGET:
            return OUTCOME_FLIP7
        return OUTCOME_OK

    def _resolve_second_chance(
        self, target: Flip7Player, *, forced: bool, chooser: Flip7Player
    ) -> str:
        if not target.second_chance:
            target.second_chance = True
            self.broadcast_personal_l(
                target,
                "flip7-you-set-second-chance",
                "flip7-player-sets-second-chance",
                buffer="game",
            )
            return OUTCOME_OK

        if forced:
            assert self.flip_state is not None
            self.flip_state.second_chances += 1
            self.broadcast_l(
                "flip7-second-chance-held",
                buffer="game",
                player=chooser.name if chooser is not target else target.name,
            )
            return OUTCOME_OK
        return self._open_choice(CHOICE_SECOND_CHANCE, target)

    def _bust(self, target: Flip7Player, value: int) -> None:
        target.round_status = STATUS_BUSTED
        target.busts += 1
        self._schedule_bust_announcement(target, value)

    def _award_flip_seven(self, target: Flip7Player) -> None:
        target.flip_sevens += 1
        self.play_sound(SOUND_FLIP_SEVEN)
        self.broadcast_l("flip7-flip-seven", buffer="game", player=target.name)
        self._end_round(flip_seven=target)

    # ------------------------------------------------------------------
    # Targeted choices
    # ------------------------------------------------------------------

    def _choice_action_label(self, kind: str, locale: str) -> str:
        if kind == CHOICE_STOP:
            return Localization.get(locale, "flip7-card-stop")
        if kind == CHOICE_FLIP_THREE:
            return Localization.get(locale, "flip7-card-flip-three")
        return Localization.get(locale, "flip7-card-second-chance")

    def _stop_targets(self) -> list[Flip7Player]:
        return [
            player
            for player in self._active()
            if player.round_status == STATUS_PLAYING
        ]

    def _stop_alone(self, player: Flip7Player) -> None:
        player.round_status = STATUS_STAYED
        points = self.round_points(player)
        self.play_sound(random.choice(SOUND_STAY_VARIANTS))
        self.broadcast_personal_l(
            player,
            "flip7-you-stop-alone",
            "flip7-player-stops-alone",
            buffer="game",
            points=points,
        )

    def _open_choice(self, kind: str, actor: Flip7Player) -> str:
        self.pending_choice = Flip7Choice(
            kind=kind, actor_slot=self._slot_of(actor)
        )
        targets = self._choice_targets()

        if not targets:
            # Nobody left who can legally receive this card, so it is dropped.
            if kind == CHOICE_SECOND_CHANCE:
                self.broadcast_personal_l(
                    actor,
                    "flip7-you-discard-second-chance",
                    "flip7-player-discards-second-chance",
                    buffer="game",
                )
            else:
                self.broadcast_personal_l(
                    actor,
                    "flip7-you-discard-action",
                    "flip7-player-discards-action",
                    buffer="game",
                    action=self._choice_action_label(
                        kind, self._locale_of(actor)
                    ),
                )
            self._finish_choice_item()
            return OUTCOME_OK
        if kind in (CHOICE_STOP, CHOICE_FLIP_THREE) and len(targets) == 1:
            self._consume_choice(actor, targets[0])
            return OUTCOME_OK
        return OUTCOME_CHOICE

    def _consume_choice(self, actor: Flip7Player, target: Flip7Player) -> None:
        self._apply_choice(actor, target)
        self._finish_choice_item()

    def _apply_choice(self, actor: Flip7Player, target: Flip7Player) -> None:
        if self.pending_choice is None:
            return
        kind = self.pending_choice.kind
        if target.round_status != STATUS_PLAYING and kind != CHOICE_SECOND_CHANCE:
            return

        if kind == CHOICE_STOP:
            target.round_status = STATUS_STAYED
            points = self.round_points(target)
            self.play_sound(random.choice(SOUND_STAY_VARIANTS))
            self.broadcast_personal_l(
                actor,
                "flip7-you-stop-player",
                "flip7-player-stops-player",
                buffer="game",
                target=target.name,
                points=points,
            )
        elif kind == CHOICE_FLIP_THREE:
            self.broadcast_personal_l(
                actor,
                "flip7-you-flip-three",
                "flip7-player-flip-three",
                buffer="game",
                target=target.name,
            )
            self._start_flip_three(actor, target)
        else:
            target.second_chance = True
            self.broadcast_personal_l(
                actor,
                "flip7-you-give-second-chance",
                "flip7-player-gives-second-chance",
                buffer="game",
                target=target.name,
            )

    def _finish_choice_item(self) -> None:
        actor_slot = self.pending_choice.actor_slot if self.pending_choice else -1
        self.pending_choice = None
        actor = self._player_at(actor_slot)
        while self.choice_queue and actor is not None:
            kind = self.choice_queue.pop(0)
            if self._open_choice(kind, actor) == OUTCOME_CHOICE:
                return

    # ------------------------------------------------------------------
    # Flip Three
    # ------------------------------------------------------------------

    def _start_flip_three(
        self, chooser: Flip7Player, target: Flip7Player
    ) -> None:
        self.cancel_sequences_by_tag(TAG_FLIP_THREE)
        self.flip_state = Flip7FlipState(
            target_slot=self._slot_of(target),
            chooser_slot=self._slot_of(chooser),
        )
        beats: list[SequenceBeat] = []
        beats.append(
            SequenceBeat(delay_after_ticks=FLIP_THREE_START_SOUND_TICKS)
        )
        for _ in range(FLIP_THREE_COUNT):
            beats.append(
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("flip_draw")],
                    delay_after_ticks=FLIP_THREE_GAP_TICKS,
                )
            )
        beats.append(
            SequenceBeat(ops=[SequenceOperation.callback_op("flip_finish")])
        )
        self.start_sequence(
            SEQUENCE_FLIP_THREE,
            beats,
            tag=TAG_FLIP_THREE,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.refresh_menus()

    def _flip_draw(self) -> None:
        state = self.flip_state
        if state is None or state.remaining <= 0:
            return
        target = self._player_at(state.target_slot)
        if target is None or target.round_status != STATUS_PLAYING:
            self.cancel_sequence(SEQUENCE_FLIP_THREE)
            self.flip_state = None
            self._continue_flow()
            return

        card = self._draw_card()
        if card is None:
            self.cancel_sequence(SEQUENCE_FLIP_THREE)
            self.flip_state = None
            self._end_round(deck_empty=True)
            return

        state.remaining -= 1
        chooser = self._player_at(state.chooser_slot) or target
        outcome = self._resolve_card(target, card, forced=True, chooser=chooser)

        if outcome == OUTCOME_BUST:
            self.cancel_sequence(SEQUENCE_FLIP_THREE)
            self.flip_state = None
            self.broadcast_l(
                "flip7-pending-actions-discarded",
                buffer="game",
                player=target.name,
            )
            self._continue_flow()
        elif outcome == OUTCOME_FLIP7:
            self.cancel_sequence(SEQUENCE_FLIP_THREE)
            self.flip_state = None
            self._schedule_flip_seven_award(target)

    def _flip_finish(self) -> None:
        state = self.flip_state
        self.flip_state = None
        if state is None:
            self._continue_flow()
            return
        target = self._player_at(state.target_slot)
        if target is None or target.round_status != STATUS_PLAYING:
            self._continue_flow()
            return

        chooser = self._player_at(state.chooser_slot) or target
        queue = (
            [CHOICE_STOP] * state.stops
            + [CHOICE_FLIP_THREE] * state.flips
            + [CHOICE_SECOND_CHANCE] * state.second_chances
        )
        if queue:
            self.choice_queue = queue
            self._open_choice(
                CHOICE_STOP if state.stops else (
                    CHOICE_FLIP_THREE if state.flips else CHOICE_SECOND_CHANCE
                ),
                chooser,
            )
            if self.pending_choice is None:
                # Every queued card resolved on the spot; keep the round moving.
                self._continue_flow()
                return
            self._arm_bot()
            self.refresh_menus()
            return
        self._continue_flow()

    # ------------------------------------------------------------------
    # Round end
    # ------------------------------------------------------------------

    def _end_round(
        self, *, flip_seven: Flip7Player | None = None, deck_empty: bool = False
    ) -> None:
        self.cancel_sequences_by_tag(TAG_FLIP_THREE)
        self.flip_state = None
        self.pending_choice = None
        self.choice_queue = []
        self.phase = PHASE_ROUND_END

        awards: list[tuple[Flip7Player, int]] = []
        for player in self._active():
            if player is flip_seven:
                points = self.round_points(player) + FLIP_SEVEN_BONUS
            elif player.round_status in (STATUS_PLAYING, STATUS_STAYED):
                points = self.round_points(player)
            else:
                points = 0
            player.total_score += points
            self._team_manager.add_to_team_score(player.name, points)
            awards.append((player, points))

        for player, _ in awards:
            self._return_area_cards(player)

        self.play_sound(SOUND_ROUND_END)
        if deck_empty:
            self.broadcast_l("flip7-round-end-deck", buffer="game")
        else:
            self.broadcast_l(
                "flip7-round-end", buffer="game", round=self.round
            )
        for player, points in awards:
            if player.round_status == STATUS_BUSTED:
                self.broadcast_personal_l(
                    player,
                    "flip7-round-bust-you",
                    "flip7-round-bust",
                    buffer="game",
                    points=points,
                )
            else:
                self.broadcast_personal_l(
                    player,
                    "flip7-round-score-you",
                    "flip7-round-score",
                    buffer="game",
                    points=points,
                    total=player.total_score,
                )

        leader = self._match_leader()
        if leader is not None:
            self.phase = PHASE_MATCH_END
            winner, _ = leader
            self.play_sound(SOUND_MATCH_WIN)
            self.broadcast_l(
                "flip7-match-win", buffer="game", player=winner.name
            )
            self.finish_game()
            return
        self._schedule_start_round()

    def _match_leader(self) -> tuple[Flip7Player, int] | None:
        """Return the sole leader once the target is reached, else ``None``."""
        active = self._active()
        if not active:
            return None
        best = max(active, key=lambda p: p.total_score)
        if best.total_score < self.options.target_score:
            return None
        tied = [p for p in active if p.total_score == best.total_score]
        if len(tied) != 1:
            return None
        return best, best.total_score

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _desired_turn_action_ids(self, player: Player) -> list[str]:
        """Action ids this player's turn menu should currently expose."""
        choice = self.pending_choice
        if choice is not None:
            if self._choice_actor() is not player:
                return []
            return [
                f"choose_{choice.kind}_{self._slot_of(target)}"
                for target in self._choice_targets()
            ]
        return ["hit", "stay"]

    def before_menu_build(self, player: Player) -> None:
        """Keep the turn action set in sync with the current choice state.

        The turn menu changes shape entirely when a targeted choice opens, and
        turn action sets are otherwise only built once when the player joins.
        """
        super().before_menu_build(player)
        if player.is_spectator:
            return
        desired = self._desired_turn_action_ids(player)
        current = self.get_action_set(player, "turn")
        current_ids = (
            [resolved.action.id for resolved in current.get_all_actions(self, player)]
            if current is not None
            else []
        )
        if current_ids == desired:
            return
        self.remove_action_set(player, "turn")
        turn_set = self.create_turn_action_set(player)
        if turn_set is not None:
            # Insert at position 0 so the turn set stays first in the chain.
            sets = self.player_action_sets.get(player.id, [])
            sets.insert(0, turn_set)
            self.player_action_sets[player.id] = sets

    def build_menu_items(self, player: Player, user: "User") -> MenuBuild:
        """Keep the personal area summary visible in the main turn list.

        The player's own area and opponents' areas stay visible below the main
        turn actions, without exposing the information actions as menu choices.
        """
        build = super().build_menu_items(player, user)
        if self.status != "playing" or player.is_spectator:
            return build
        flip_player: Flip7Player = player  # type: ignore[assignment]
        ordered = [flip_player] + [
            other for other in self._active() if other is not flip_player
        ]
        rows: list[MenuItem] = []
        for area_player in ordered:
            for index, line in enumerate(
                self._inline_area_lines(area_player, user.locale, area_player is flip_player)
            ):
                rows.append(
                    MenuItem(
                        text=line,
                        id=f"flip7_area_{self._slot_of(area_player)}_{index}",
                        read_only=True,
                    )
                )
        turn_ids = set(self._desired_turn_action_ids(player))
        insert_at = 0
        for index, item in enumerate(build.items):
            if item.id in turn_ids:
                insert_at = index + 1
            elif insert_at:
                break
        build.items = build.items[:insert_at] + rows + build.items[insert_at:]
        return build

    def create_turn_action_set(self, player: Player) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        if self.pending_choice is not None:
            actor = self._choice_actor()
            if actor is player:
                self._build_choice_actions(action_set, player, locale)
            return action_set

        action_set.add(
            Action(
                id="hit",
                label=Localization.get(locale, "flip7-hit"),
                handler="_action_hit",
                is_enabled="_is_hit_enabled",
                is_hidden="_is_hit_hidden",
                get_label="_get_hit_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="stay",
                label=Localization.get(locale, "flip7-stay"),
                handler="_action_stay",
                is_enabled="_is_stay_enabled",
                is_hidden="_is_stay_hidden",
                get_label="_get_stay_label",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def _build_choice_actions(
        self, action_set: ActionSet, player: Player, locale: str
    ) -> None:
        if self.pending_choice is None:
            return
        kind = self.pending_choice.kind
        target_key = CHOICE_KEY_SUFFIX[kind]
        for target in self._choice_targets():
            action_id = f"choose_{kind}_{self._slot_of(target)}"
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(
                        locale,
                        f"flip7-target-{target_key}",
                        target=target.name,
                        points=self.round_points(target),
                    ),
                    handler="_action_choose_target",
                    is_enabled="_is_choose_target_enabled",
                    is_hidden="_is_choose_target_hidden",
                    show_in_actions_menu=False,
                )
            )

    def _is_hit_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_stay_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_choose_target_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_hit_enabled(self, player: Player) -> str | None:
        if self.status != "playing" or self.phase != PHASE_PLAYING:
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.pending_choice is not None:
            return "flip7-error-wait-choice"
        if self.flip_state is not None:
            return "flip7-error-wait-flip-three"
        if self.deal_index < len(self.deal_order):
            return "flip7-error-wait-dealing"
        if self.current_player is not player:
            return "action-not-your-turn"
        flip_player: Flip7Player = player  # type: ignore[assignment]
        if flip_player.round_status != STATUS_PLAYING:
            return "flip7-error-not-playing-round"
        if not self.deck and not self.discard:
            return "flip7-error-no-cards-left"
        return None

    def _is_stay_enabled(self, player: Player) -> str | None:
        if self.status != "playing" or self.phase != PHASE_PLAYING:
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.pending_choice is not None:
            return "flip7-error-wait-choice"
        if self.flip_state is not None:
            return "flip7-error-wait-flip-three"
        if self.deal_index < len(self.deal_order):
            return "flip7-error-wait-dealing"
        if self.current_player is not player:
            return "action-not-your-turn"
        flip_player: Flip7Player = player  # type: ignore[assignment]
        if flip_player.round_status != STATUS_PLAYING:
            return "flip7-error-not-playing-round"
        if not self._has_cards(flip_player):
            return "flip7-error-no-cards-to-bank"
        return None

    def _is_choose_target_enabled(self, player: Player) -> str | tuple | None:
        if self.status != "playing" or self.phase != PHASE_PLAYING:
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.pending_choice is None:
            return "flip7-error-no-choice"
        if self._choice_actor() is not player:
            return "action-not-your-turn"
        return None

    def _get_hit_label(self, player: Player, action_id: str) -> str:
        locale = self._locale_of(player)
        return Localization.get(locale, "flip7-hit")

    def _get_stay_label(self, player: Player, action_id: str) -> str:
        locale = self._locale_of(player)
        flip_player: Flip7Player = player  # type: ignore[assignment]
        return Localization.get(
            locale, "flip7-stay", points=self.round_points(flip_player)
        )

    def _action_hit(self, player: Player, action_id: str) -> None:
        if self._is_hit_enabled(player) is not None:
            return
        flip_player: Flip7Player = player  # type: ignore[assignment]
        card = self._draw_card()
        if card is None:
            self._end_round(deck_empty=True)
            return
        flip_player.hits_taken += 1
        outcome = self._resolve_card(
            flip_player, card, forced=False, chooser=flip_player
        )
        if outcome == OUTCOME_FLIP7:
            self._schedule_flip_seven_award(flip_player)
            return
        if outcome == OUTCOME_ROUND_END:
            return
        if outcome == OUTCOME_CHOICE:
            self._arm_bot()
            self.refresh_menus()
            return
        # A bust ends this player's turn; every other outcome keeps it.
        self._schedule_after_card_reveal("continue_flow")

    def _action_stay(self, player: Player, action_id: str) -> None:
        if self._is_stay_enabled(player) is not None:
            return
        flip_player: Flip7Player = player  # type: ignore[assignment]
        flip_player.round_status = STATUS_STAYED
        points = self.round_points(flip_player)
        self.play_sound(random.choice(SOUND_STAY_VARIANTS))
        self.broadcast_personal_l(
            flip_player,
            "flip7-you-stay",
            "flip7-player-stays",
            buffer="game",
            points=points,
        )
        self._continue_flow()

    def _action_choose_target(self, player: Player, action_id: str) -> None:
        if self._is_choose_target_enabled(player) is not None:
            return
        if self.pending_choice is None:
            return
        parts = action_id.rsplit("_", 1)
        if len(parts) != 2:
            return
        target = self._player_at(int(parts[1]))
        if target is None or target not in self._choice_targets():
            return
        self._consume_choice(player, target)  # type: ignore[arg-type]
        if self.pending_choice is not None:
            self._arm_bot()
            self.refresh_menus()
            return
        if self.flip_state is not None:
            return
        self._continue_flow()

    # ------------------------------------------------------------------
    # Information actions
    # ------------------------------------------------------------------

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="check_area",
                label=Localization.get(locale, "flip7-check-area"),
                handler="_action_check_area",
                is_enabled="_is_check_area_enabled",
                is_hidden="_is_check_area_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="check_table",
                label=Localization.get(locale, "flip7-check-table"),
                handler="_action_check_table",
                is_enabled="_is_check_table_enabled",
                is_hidden="_is_check_table_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="check_deck",
                label=Localization.get(locale, "flip7-check-deck"),
                handler="_action_check_deck",
                is_enabled="_is_check_deck_enabled",
                is_hidden="_is_check_deck_hidden",
                show_in_actions_menu=False,
            )
        )
        for position in range(1, 11):
            action_set.add(
                Action(
                    id=f"read_card_{position}",
                    label=Localization.get(locale, "flip7-read-card", pos=position),
                    handler="_action_read_card",
                    is_enabled="_is_read_card_enabled",
                    is_hidden="_is_read_card_hidden",
                    show_in_actions_menu=False,
                )
            )
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                ["check_area", "check_table", "check_deck", "check_scores",
                 "whose_turn", "whos_at_table"],
            )
        return action_set

    def _is_check_area_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE if self.is_touch_player(player) else Visibility.HIDDEN

    def _is_check_table_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE if self.is_touch_player(player) else Visibility.HIDDEN

    def _is_check_deck_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE if self.is_touch_player(player) else Visibility.HIDDEN

    def _is_read_card_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_read_card_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_check_area_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_check_table_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_check_deck_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "action-spectator"
        return None

    def _inline_area_lines(
        self, player: Flip7Player, locale: str, is_self: bool = True
    ) -> list[str]:
        """Compact personal area summary shown in the main turn list."""
        lines: list[str] = []
        who = Localization.get(locale, "flip7-you-label") if is_self else player.name
        status = ""
        if player.round_status == STATUS_STAYED:
            status = Localization.get(locale, "flip7-area-status-stayed")
        elif player.round_status == STATUS_BUSTED:
            status = Localization.get(locale, "flip7-area-status-busted")
        if player.numbers:
            numbers = self._read_list(locale, [str(n) for n in player.numbers])
        else:
            numbers = Localization.get(locale, "flip7-area-numbers-none")
        bonuses: list[str] = []
        bonuses.extend(f"+{m}" for m in player.modifiers)
        if player.has_double:
            bonuses.append(Localization.get(locale, "flip7-card-double"))
        if player.second_chance:
            bonuses.append(Localization.get(locale, "flip7-card-second-chance"))
        bonus_text = ""
        if bonuses:
            bonus_text = " " + Localization.get(
                locale,
                "flip7-area-bonus-suffix",
                bonuses=self._read_list(locale, bonuses),
            )
        lines.append(
            Localization.get(
                locale,
                "flip7-area-inline",
                who=who,
                status=status,
                numbers=numbers,
                points=self.round_points(player),
                bonus=bonus_text,
            )
        )
        return lines

    def _read_list(self, locale: str, items: list[str]) -> str:
        return Localization.format_list_and(locale, items)

    def _action_check_area(self, player: Player, action_id: str) -> None:
        if player.is_spectator:
            return
        flip_player: Flip7Player = player  # type: ignore[assignment]
        user = self.get_user(player)
        if user is None:
            return
        for line in self._inline_area_lines(flip_player, user.locale):
            user.speak(line, buffer="game")

    def _action_read_card(self, player: Player, action_id: str) -> None:
        if self._is_read_card_enabled(player) is not None:
            return
        user = self.get_user(player)
        if user is None:
            return
        try:
            position = int(action_id.rsplit("_", 1)[1])
        except (IndexError, ValueError):
            return
        flip_player: Flip7Player = player  # type: ignore[assignment]
        if position < 1 or position > 10:
            return
        if position > len(flip_player.numbers):
            user.speak_l(
                "flip7-no-card-position",
                buffer="game",
                pos=position,
            )
            return
        user.speak_l(
            "flip7-card-position",
            buffer="game",
            pos=position,
            value=flip_player.numbers[position - 1],
        )

    def _action_check_table(self, player: Player, action_id: str) -> None:
        if player.is_spectator:
            return
        user = self.get_user(player)
        if user is None:
            return
        locale = user.locale
        lines = [
            Localization.get(
                locale,
                "flip7-check-round",
                round=self.round,
                target=self.options.target_score,
            )
        ]
        for other in self._active():
            status_key = {
                STATUS_PLAYING: "flip7-status-playing",
                STATUS_STAYED: "flip7-status-stayed",
                STATUS_BUSTED: "flip7-status-busted",
            }[other.round_status]
            lines.append(
                Localization.get(
                    locale,
                    "flip7-table-line",
                    player=other.name,
                    status=Localization.get(locale, status_key),
                    points=self.round_points(other),
                    total=other.total_score,
                )
            )
        for line in lines:
            user.speak(line, buffer="game")

    def _action_check_deck(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user is None:
            return
        locale = user.locale
        user.speak(
            Localization.get(locale, "flip7-deck-line", count=len(self.deck)),
            buffer="game",
        )
        user.speak(
            Localization.get(locale, "flip7-discard-line", count=len(self.discard)),
            buffer="game",
        )

    # ------------------------------------------------------------------
    # Keybinds
    # ------------------------------------------------------------------

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        user = None
        if getattr(self, "host_username", ""):
            player = self.get_player_by_name(self.host_username)
            if player is not None:
                user = self.get_user(player)
        locale = user.locale if user else "en"

        self.define_keybind(
            "space",
            Localization.get(locale, "flip7-hit"),
            ["hit"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "h",
            Localization.get(locale, "flip7-stay"),
            ["stay"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "c",
            Localization.get(locale, "flip7-check-area"),
            ["check_area"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "shift+c",
            Localization.get(locale, "flip7-check-table"),
            ["check_table"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "d",
            Localization.get(locale, "flip7-check-deck"),
            ["check_deck"],
            state=KeybindState.ACTIVE,
        )
        for key, position in [(str(n), n) for n in range(1, 10)] + [("0", 10)]:
            self.define_keybind(
                key,
                Localization.get(locale, "flip7-read-card", pos=position),
                [f"read_card_{position}"],
                state=KeybindState.ACTIVE,
            )

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        return list(super().prestart_validate())

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def build_game_result(self) -> GameResult:
        sorted_players = sorted(
            self._active(), key=lambda p: p.total_score, reverse=True
        )
        final_scores = {p.name: p.total_score for p in sorted_players}
        player_stats = {
            p.name: {
                "total_score": p.total_score,
                "rounds_busted": p.busts,
                "flip_sevens": p.flip_sevens,
                "cards_drawn": p.hits_taken,
            }
            for p in sorted_players
        }
        winner = sorted_players[0] if sorted_players else None
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
                for p in self._active()
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": winner.total_score if winner else 0,
                "final_scores": final_scores,
                "player_stats": player_stats,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        previous_score: int | None = None
        rank = 0
        for displayed, (name, score) in enumerate(
            result.custom_data.get("final_scores", {}).items(), start=1
        ):
            if score != previous_score:
                rank = displayed
                previous_score = score
            lines.append(
                Localization.get(
                    locale,
                    "flip7-line-format",
                    rank=rank,
                    player=name,
                    points=Localization.get(locale, "game-points", count=score),
                )
            )
        return lines
