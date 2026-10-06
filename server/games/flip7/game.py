"""Flip 7 push-your-luck card game.

Each round every player collects number and modifier cards. Drawing a number
already in your area busts the round for you unless a Second Chance is set
aside. Seven unique numbers score the Flip 7 bonus and end the round for
everybody at once. Freeze and Flip Three cards target another player, and
Second Chance cards are given away while the round runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import random

from mashumaro.mixins.json import DataClassJSONMixin

from . import audio
from .bot import bot_think
from .constants import (
    ACTION_COPIES,
    BOT_MAX_THINK_TICKS,
    BOT_MIN_THINK_TICKS,
    CARD_DOUBLE,
    CARD_FLIP_THREE,
    CARD_FREEZE,
    CARD_MODIFIER,
    CARD_NUMBER,
    CARD_SECOND_CHANCE,
    CHOICE_FLIP_THREE,
    CHOICE_FREEZE,
    CHOICE_KEY_SUFFIX,
    CHOICE_SECOND_CHANCE,
    CONTINUE_FLOW,
    FLIP_SEVEN_BONUS,
    FLIP_SEVEN_TARGET,
    FLIP_THREE_COUNT,
    MAX_NUMBER,
    MIN_REVEAL_SPEECH_TICKS,
    MODIFIER_VALUES,
    NEXT_FLIP_DRAW,
    OUTCOME_BUST,
    OUTCOME_CHOICE,
    OUTCOME_FLIP7,
    OUTCOME_FLOW,
    OUTCOME_OK,
    OUTCOME_PENDING,
    OUTCOME_SAVED,
    OUTCOME_STOP_ALONE,
    PHASE_MATCH_END,
    PHASE_PLAYING,
    PHASE_ROUND_END,
    SEQUENCE_CARD_FLOW_PREFIX,
    SEQUENCE_MATCH_END_PREFIX,
    SEQUENCE_ROUND_START_PREFIX,
    STATUS_BUSTED,
    STATUS_PLAYING,
    STATUS_STAYED,
    TAG_FLOW,
    TICKS_PER_SECOND,
    TURN_CARD_TICKS,
)
from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...game_utils.stats_helpers import (
    RATING_COMPETITORS_KEY,
    rating_competitors_from_scores,
)
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

# Small fixed gap after a card's effect announcement before the flow moves on.
EFFECT_GAP_TICKS = TICKS_PER_SECOND // 2

# Continuation ids routed by active card sequences. "deal_step" is both a
# leading beat and a continuation, so it lives on as a string.
FLIP_BUST_ABORT = "flip_bust_abort"
AFTER_CHOICE = "after_choice"


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
    actor_id: str = ""
    card: Flip7Card | None = None


@dataclass
class Flip7PendingAction(DataClassJSONMixin):
    """A forced action card one player owes a target choice for."""

    kind: str
    owner_id: str
    card: Flip7Card


@dataclass
class Flip7FlipState(DataClassJSONMixin):
    """In-progress Flip Three reveal."""

    target_id: str
    remaining: int = FLIP_THREE_COUNT
    pending_action_count: int = 0


@dataclass
class Flip7Player(Player):
    """Player state for Flip 7."""

    total_score: int = 0
    cards: list[Flip7Card] = field(default_factory=list)
    round_status: str = STATUS_PLAYING
    cards_drawn: int = 0
    busts: int = 0
    flip_sevens: int = 0

    @property
    def second_chance(self) -> bool:
        return any(c.kind == CARD_SECOND_CHANCE for c in self.cards)

    @property
    def numbers(self) -> list[int]:
        return sorted(c.value for c in self.cards if c.kind == CARD_NUMBER)

    @property
    def modifiers(self) -> list[int]:
        return sorted(c.value for c in self.cards if c.kind == CARD_MODIFIER)

    @property
    def has_double(self) -> bool:
        return any(c.kind == CARD_DOUBLE for c in self.cards)


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

    Each turn a player draws a card resolved through one timed reveal flow.
    Status changes happen only inside flow callbacks, so a disconnect mid-reveal
    replays the exact same outcome after reconnecting.
    """

    players: list[Flip7Player] = field(default_factory=list)
    options: Flip7Options = field(default_factory=Flip7Options)

    round: int = 0
    dealer_index: int = -1
    deck: list[Flip7Card] = field(default_factory=list)
    discard: list[Flip7Card] = field(default_factory=list)
    phase: str = PHASE_PLAYING
    deal_order: list[str] = field(default_factory=list)
    deal_index: int = 0
    pending_choice: Flip7Choice | None = None
    pending_actions: list[Flip7PendingAction] = field(default_factory=list)
    flip_state: Flip7FlipState | None = None
    drawn_card: Flip7Card | None = None

    @classmethod
    def __post_deserialize__(cls, self):
        cards = self._physical_cards()
        if cards:
            expected = {c.uid: (c.kind, c.value) for c in self.build_deck()}
            actual = {c.uid: (c.kind, c.value) for c in cards}
            if len(cards) != len(expected) or actual != expected:
                raise ValueError("Invalid Flip 7 physical deck")
        return self

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
        # The published game is a 3+ player race. The official two-player
        # variant is a different challenge and is not implemented here.
        return 3

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

    def _locale_of(self, player: Player | None) -> str:
        user = self.get_user(player) if player else None
        return user.locale if user else "en"

    def _playing_players(self) -> list[Flip7Player]:
        return [
            player
            for player in self._active()
            if player.round_status == STATUS_PLAYING
        ]

    def _choice_actor(self) -> Flip7Player | None:
        if self.pending_choice is None:
            return None
        player = self.get_player_by_id(self.pending_choice.actor_id)
        if isinstance(player, Flip7Player):
            return player
        return None

    def _choice_targets(self) -> list[Flip7Player]:
        if self.pending_choice is None:
            return []
        kind = self.pending_choice.kind
        actor = self._choice_actor()
        targets: list[Flip7Player] = []
        for player in self._playing_players():
            if kind == CHOICE_SECOND_CHANCE:
                if player is actor or player.second_chance:
                    continue
            targets.append(player)
        return targets

    def round_points(self, player: Flip7Player) -> int:
        """Number cards doubled first, then the flat modifiers added."""
        total = sum(player.numbers)
        if player.has_double:
            total *= 2
        return total + sum(player.modifiers)

    def _total_cards_in_play(self) -> int:
        """Count every physical card, including cards mid-resolution."""
        return len(self._physical_cards())

    def _physical_cards(self) -> list[Flip7Card]:
        cards = self.deck + self.discard
        for player in self.players:
            cards.extend(player.cards)
        cards.extend(pending.card for pending in self.pending_actions)
        if self.drawn_card is not None:
            cards.append(self.drawn_card)
        if self.pending_choice is not None and self.pending_choice.card is not None:
            cards.append(self.pending_choice.card)
        return cards

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
            add(CARD_FREEZE)
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
        if card.kind == CARD_FREEZE:
            return Localization.get(locale, "flip7-card-freeze")
        if card.kind == CARD_FLIP_THREE:
            return Localization.get(locale, "flip7-card-flip-three")
        raise ValueError(f"Unknown Flip 7 card kind: {card.kind!r}")

    def _draw_card(self) -> Flip7Card:
        if not self.deck and not self._reshuffle_discard():
            raise RuntimeError("Flip 7 physical deck was exhausted")
        return self.deck.pop()

    def _reshuffle_discard(self) -> bool:
        if self.deck:
            return False
        if not self.discard:
            return False
        self.deck = list(self.discard)
        self.discard = []
        random.shuffle(self.deck)
        self.play_sound_family(audio.SOUND_SHUFFLE_FAMILY)
        self.broadcast_l("flip7-deck-reshuffled", buffer="game")
        return True

    def _return_area_cards(self, player: Flip7Player) -> None:
        self.discard.extend(player.cards)
        player.cards = []

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
        if self.status != "playing" or self.phase != PHASE_PLAYING:
            return None
        if self.pending_choice is not None:
            return self._choice_actor()
        if self.flip_state is not None:
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
        self.deck = self.build_deck()
        random.shuffle(self.deck)
        self.discard = []
        self.deal_order = []
        self.deal_index = 0
        self.pending_choice = None
        self.pending_actions = []
        self.flip_state = None
        self.drawn_card = None

        active = self._active()
        for player in active:
            player.total_score = 0
            player.cards = []
            player.round_status = STATUS_PLAYING
            player.cards_drawn = 0
            player.busts = 0
            player.flip_sevens = 0

        self.set_turn_players(active)
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active])
        self._team_manager.reset_all_scores()

        self.play_music(audio.SOUND_PLAY_MUSIC)
        self._start_round()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if not self.game_active:
            return
        self._drive_choice_bot()
        if self.is_sequence_bot_paused():
            return
        BotHelper.on_tick(self)

    def _drive_choice_bot(self) -> None:
        """Answer an open targeted choice for a bot.

        ``BotHelper.on_tick`` only asks ``current_player`` for a decision.
        Action cards can instead leave a non-turn bot responsible for a target
        choice, so this path drives that bot as soon as gameplay is unlocked.
        The shared enabled predicate still prevents any bot from acting during
        a gameplay-locking sequence.
        """
        if self.pending_choice is None:
            return
        actor = self._choice_actor()
        if actor is None or not actor.is_bot:
            return
        if actor is self.current_player and not self.is_sequence_bot_paused():
            return
        if self._is_choose_target_enabled(actor) is not None:
            return
        BotHelper.process_bot_action(
            actor,
            lambda: self.bot_think(actor),
            lambda action_id: self.execute_action(actor, action_id),
        )

    def bot_think(self, player: Flip7Player) -> str | None:
        return bot_think(self, player)

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if callback_id == "card_reveal":
            self._announce_revealed_card(payload)
            return
        if callback_id == "card_effect":
            self._apply_card_effect(payload)
            return
        if callback_id == "deal_step":
            self._deal_step()
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
        if callback_id == "end_round_flip7":
            target = self.get_player_by_id(str(payload.get("target_id", "")))
            if isinstance(target, Flip7Player):
                self._end_round(flip_seven=target)
            return
        if callback_id == "stop_alone":
            self._announce_stop_alone(payload)
            return
        if callback_id == AFTER_CHOICE:
            self._after_choice_flow()
            return
        if callback_id == CONTINUE_FLOW:
            self._continue_flow()
            return
        if callback_id == NEXT_FLIP_DRAW:
            self._flip_draw()
            return
        if callback_id == FLIP_BUST_ABORT:
            self._flip_bust_abort(str(payload.get("target_id", "")))
            return
        if callback_id == "match_win":
            self._announce_match_win(payload)
            return
        if callback_id == "finish_match":
            self.finish_game()
            return

    # ------------------------------------------------------------------
    # Card reveal flow
    # ------------------------------------------------------------------

    def _flow_id(
        self,
        kind: str,
        player: Flip7Player,
        suffix: object = "",
    ) -> str:
        return f"{kind}_{player.id}_{self.sound_scheduler_tick}_{suffix}"

    def _play_reveal_sound(self, sound: str) -> None:
        if sound.endswith(".ogg"):
            self.play_sound(sound)
        else:
            self.play_sound_family(sound)

    def _card_reveal_sound(self, card: Flip7Card) -> str:
        if card.kind == CARD_NUMBER:
            return audio.SOUND_CARD_NUMBER_FAMILY
        if card.kind == CARD_MODIFIER:
            # Pick the exact +N asset: a family would let clients pick a
            # semantically different modifier.
            return audio.SOUND_MODIFIER_BY_VALUE[card.value]
        if card.kind == CARD_DOUBLE:
            return audio.SOUND_DOUBLE
        if card.kind == CARD_SECOND_CHANCE:
            return audio.SOUND_SECOND_CHANCE
        if card.kind == CARD_FREEZE:
            return audio.SOUND_FREEZE
        if card.kind == CARD_FLIP_THREE:
            return audio.SOUND_FLIP_THREE
        raise ValueError(f"Unknown Flip 7 card kind: {card.kind!r}")

    def _reveal_wait_beat(
        self,
        reveal_sound: str,
        ops: list[SequenceOperation],
    ) -> SequenceBeat:
        """Reveal beat measured to its cue, floored long enough to speak."""
        beat = SequenceBeat.after_audio(audio.sound_ticks(reveal_sound), ops=ops)
        if beat.delay_after_ticks < MIN_REVEAL_SPEECH_TICKS:
            beat.delay_after_ticks = MIN_REVEAL_SPEECH_TICKS
        return beat

    def _card_flow_tail(
        self,
        outcome: str,
        card: Flip7Card,
        *,
        forced: bool,
        player: Flip7Player,
        continuation: str,
    ) -> list[SequenceBeat]:
        """Beat tail that turns a resolved outcome into audio plus progress."""
        if outcome == OUTCOME_CHOICE:
            return []
        if outcome == OUTCOME_SAVED:
            return [
                SequenceBeat.after_audio(
                    audio.sound_ticks(audio.SOUND_SECOND_CHANCE_SAVE),
                    ops=[
                        SequenceOperation.sound_op(audio.SOUND_SECOND_CHANCE_SAVE),
                        SequenceOperation.callback_op(
                            "second_chance_save",
                            {
                                "target_id": player.id,
                                "value": card.value,
                            },
                        ),
                    ],
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op(continuation)]
                ),
            ]
        if outcome == OUTCOME_BUST:
            to_continue = FLIP_BUST_ABORT if forced else continuation
            payload = {"target_id": player.id} if forced else {}
            return [
                SequenceBeat.after_audio(
                    audio.sound_ticks(audio.SOUND_BUST),
                    ops=[
                        SequenceOperation.sound_op(audio.SOUND_BUST),
                        SequenceOperation.callback_op(
                            "bust_announce",
                            {
                                "target_id": player.id,
                                "value": card.value,
                            },
                        ),
                    ],
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op(to_continue, payload)]
                ),
            ]
        if outcome == OUTCOME_FLIP7:
            # The following beat keeps the sequence alive past the cue so the
            # round-end announcements never overlap the Flip Seven reveal.
            return [
                SequenceBeat.after_audio(
                    audio.sound_ticks(audio.SOUND_FLIP_SEVEN),
                    ops=[
                        SequenceOperation.sound_op(audio.SOUND_FLIP_SEVEN),
                        SequenceOperation.callback_op(
                            "award_flip_seven",
                            {"target_id": player.id},
                        ),
                    ],
                ),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "end_round_flip7",
                            {"target_id": player.id},
                        )
                    ]
                ),
            ]
        if outcome == OUTCOME_STOP_ALONE:
            return [
                SequenceBeat.after_audio(
                    audio.sound_ticks(audio.SOUND_STAY),
                    ops=[
                        SequenceOperation.sound_op(audio.SOUND_STAY),
                        SequenceOperation.callback_op(
                            "stop_alone",
                            {
                                "target_id": player.id,
                                "points": self.round_points(player),
                            },
                        ),
                    ],
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op(continuation)]
                ),
            ]
        # OK / PENDING: nothing else to show, just move on.
        return [SequenceBeat(ops=[SequenceOperation.callback_op(continuation)])]

    def _resolve_card(
        self,
        player: Flip7Player,
        card: Flip7Card,
        *,
        forced: bool,
        continuation: str,
        pending_owner: str | None = None,
    ) -> None:
        """Start one timed reveal flow for the given card and recipient."""
        self.drawn_card = card
        player.cards_drawn += 1
        self.broadcast_personal_l(
            player,
            "flip7-you-turn-card",
            "flip7-player-turns-card",
            buffer="game",
        )

        outcome = self._get_card_outcome(player, card, forced=forced)
        reveal_sound = self._card_reveal_sound(card)
        beats = [
            SequenceBeat.pause(TURN_CARD_TICKS),
            self._reveal_wait_beat(
                reveal_sound,
                [
                    SequenceOperation.callback_op(
                        "card_reveal",
                        {
                            "target_id": player.id,
                            "kind": card.kind,
                            "value": card.value,
                            "sound": reveal_sound,
                        },
                    )
                ],
            ),
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "card_effect",
                        {
                            "target_id": player.id,
                            "kind": card.kind,
                            "value": card.value,
                            "uid": card.uid,
                            "forced": forced,
                            "outcome": outcome,
                            "pending_owner": pending_owner,
                        },
                    )
                ],
                delay_after_ticks=EFFECT_GAP_TICKS,
            ),
        ]
        beats.extend(
            self._card_flow_tail(
                outcome,
                card,
                forced=forced,
                player=player,
                continuation=continuation,
            )
        )
        self.start_sequence(
            self._flow_id(
                SEQUENCE_CARD_FLOW_PREFIX,
                player,
                suffix=card.uid,
            ),
            beats,
            tag=TAG_FLOW,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _get_card_outcome(
        self,
        player: Flip7Player,
        card: Flip7Card,
        *,
        forced: bool,
    ) -> str:
        """Compute what a drawn card will do, before any state mutates.

        Call state changes only in the matching ``_apply_card_effect`` branch so
        a replayed flow always lands in the same place.
        """
        if card.kind == CARD_NUMBER:
            if card.value in player.numbers:
                return OUTCOME_SAVED if player.second_chance else OUTCOME_BUST
            if len(player.numbers) + 1 >= FLIP_SEVEN_TARGET:
                return OUTCOME_FLIP7
            return OUTCOME_OK
        if card.kind == CARD_MODIFIER:
            return OUTCOME_OK
        if card.kind == CARD_DOUBLE:
            return OUTCOME_OK
        if card.kind == CARD_SECOND_CHANCE:
            # Second Chance is never deferred, not even while a Flip Three is
            # still revealing: the official rule lets it be set aside and spend
            # itself on a duplicate later in that same Flip Three. Only Flip
            # Three and Freeze wait for the three flips to finish.
            if not player.second_chance:
                return OUTCOME_OK
            return OUTCOME_CHOICE
        if card.kind == CARD_FREEZE:
            if forced:
                return OUTCOME_PENDING
            if len(self._playing_players()) == 1:
                return OUTCOME_STOP_ALONE
            return OUTCOME_CHOICE
        # CARD_FLIP_THREE
        if forced:
            return OUTCOME_PENDING
        return OUTCOME_CHOICE

    def _announce_revealed_card(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("target_id", "")))
        if not isinstance(player, Flip7Player):
            return
        card = Flip7Card(
            kind=str(payload.get("kind", "")),
            value=int(payload.get("value", 0)),
        )
        sound = str(payload.get("sound", ""))
        if sound:
            self._play_reveal_sound(sound)
        self.broadcast_personal_l(
            player,
            "flip7-your-card-is",
            "flip7-player-card-is",
            buffer="game",
            card=lambda locale: self._card_label(card, locale),
        )

    def _apply_card_effect(self, payload: dict) -> None:
        card = self.drawn_card
        if card is None or card.uid != int(payload.get("uid", -1)):
            return
        # Transfer ownership before invoking effects, which may synchronously
        # draw another card or finish the round. Stale callbacks cannot clone it.
        self.drawn_card = None
        player = self.get_player_by_id(str(payload.get("target_id", "")))
        if not isinstance(player, Flip7Player):
            self.discard.append(card)
            return
        outcome = str(payload.get("outcome", OUTCOME_OK))
        forced = bool(payload.get("forced", False))

        if outcome == OUTCOME_PENDING:
            pending = Flip7PendingAction(
                kind=card.kind,
                owner_id=str(payload.get("pending_owner") or ""),
                card=card,
            )
            state = self.flip_state
            if state is None:
                self.pending_actions.append(pending)
            else:
                # A nested Flip Three must resolve all of the actions it
                # reveals before returning to the suspended outer queue. Keep
                # this flip's cards in reveal order at the head of that queue.
                insert_at = max(
                    0,
                    min(state.pending_action_count, len(self.pending_actions)),
                )
                self.pending_actions.insert(insert_at, pending)
                state.pending_action_count += 1
            return

        if card.kind == CARD_NUMBER:
            self._apply_number(player, card, outcome)
        elif card.kind == CARD_MODIFIER:
            player.cards.append(card)
        elif card.kind == CARD_DOUBLE:
            player.cards.append(card)
        elif card.kind == CARD_SECOND_CHANCE:
            self._apply_second_chance(player, card, outcome)
        elif card.kind == CARD_FREEZE:
            self._apply_freeze(player, card, outcome)
        elif card.kind == CARD_FLIP_THREE:
            self._apply_flip_three(player, card, outcome)

    def _apply_number(self, player: Flip7Player, card: Flip7Card, outcome: str) -> None:
        if outcome in (OUTCOME_SAVED, OUTCOME_BUST):
            self.discard.append(card)
            if outcome == OUTCOME_SAVED:
                held = next(c for c in player.cards if c.kind == CARD_SECOND_CHANCE)
                player.cards.remove(held)
                self.discard.append(held)
            else:
                player.round_status = STATUS_BUSTED
                player.busts += 1
            return
        player.cards.append(card)

    def _set_second_chance(self, player: Flip7Player, card: Flip7Card) -> None:
        player.cards.append(card)
        self.broadcast_personal_l(
            player,
            "flip7-you-set-second-chance",
            "flip7-player-sets-second-chance",
            buffer="game",
        )

    def _apply_second_chance(
        self, player: Flip7Player, card: Flip7Card, outcome: str
    ) -> None:
        if not player.second_chance:
            self._set_second_chance(player, card)
            return
        if outcome != OUTCOME_CHOICE:
            return
        self._resolve_choice_open(CHOICE_SECOND_CHANCE, player, card)

    def _apply_freeze(
        self, player: Flip7Player, card: Flip7Card, outcome: str
    ) -> None:
        if outcome == OUTCOME_STOP_ALONE:
            player.round_status = STATUS_STAYED
            self.discard.append(card)
            return
        if outcome == OUTCOME_CHOICE:
            self._resolve_choice_open(CHOICE_FREEZE, player, card)

    def _apply_flip_three(
        self, player: Flip7Player, card: Flip7Card, outcome: str
    ) -> None:
        if outcome == OUTCOME_CHOICE:
            self._resolve_choice_open(CHOICE_FLIP_THREE, player, card)

    def _resolve_choice_open(
        self, kind: str, actor: Flip7Player, card: Flip7Card
    ) -> None:
        """Open a card-draw choice and either resume or hand off the flow."""
        result = self._open_choice(kind, actor, card=card)
        if result == OUTCOME_FLOW:
            return
        if result == OUTCOME_CHOICE:
            return
        self._after_choice_flow()

    def _announce_bust(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("target_id", "")))
        if not isinstance(player, Flip7Player):
            return
        value = int(payload.get("value", 0))
        self.broadcast_personal_l(
            player,
            "flip7-you-bust",
            "flip7-player-busts",
            buffer="game",
            value=value,
        )

    def _announce_second_chance_save(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("target_id", "")))
        if not isinstance(player, Flip7Player):
            return
        value = int(payload.get("value", 0))
        self.broadcast_personal_l(
            player,
            "flip7-second-chance-saves-you",
            "flip7-second-chance-saves",
            buffer="game",
            value=value,
        )

    def _announce_stop_alone(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("target_id", "")))
        if not isinstance(player, Flip7Player):
            return
        points = int(payload.get("points", 0))
        self.broadcast_personal_l(
            player,
            "flip7-you-stop-alone",
            "flip7-player-stops-alone",
            buffer="game",
            points=points,
        )

    def _award_flip_seven(self, player: Flip7Player) -> None:
        player.flip_sevens += 1
        self.broadcast_personal_l(
            player, "flip7-flip-seven-you", "flip7-flip-seven", buffer="game"
        )

    def _discard_pending_actions_for(self, owner_id: str) -> list[Flip7PendingAction]:
        """Drop and discard only the queued action cards one owner revealed."""
        kept: list[Flip7PendingAction] = []
        dropped: list[Flip7PendingAction] = []
        for pending in self.pending_actions:
            if pending.owner_id == owner_id:
                dropped.append(pending)
            else:
                kept.append(pending)
        for pending in dropped:
            self.discard.append(pending.card)
        self.pending_actions = kept
        return dropped

    def _flip_bust_abort(self, target_id: str) -> None:
        self.flip_state = None
        # A bust only voids the action cards that busted recipient revealed.
        # An outer player's queued Freeze stays queued and resolvable.
        if self._discard_pending_actions_for(target_id):
            player = self.get_player_by_id(target_id)
            if isinstance(player, Flip7Player):
                self.broadcast_personal_l(
                    player,
                    "flip7-you-pending-bust-discarded",
                    "flip7-player-pending-bust-discarded",
                    buffer="game",
                )
        self._continue_flow()

    # ------------------------------------------------------------------
    # Targeted choices
    # ------------------------------------------------------------------

    def _open_choice(
        self,
        kind: str,
        actor: Flip7Player,
        *,
        card: Flip7Card | None = None,
    ) -> str:
        self.pending_choice = Flip7Choice(
            kind=kind, actor_id=actor.id, card=card
        )
        targets = self._choice_targets()

        if not targets:
            if card is not None:
                self.discard.append(card)
            self._announce_discarded_action(actor, kind, card)
            self.pending_choice = None
            return OUTCOME_OK
        if kind in (CHOICE_FREEZE, CHOICE_FLIP_THREE) and len(targets) == 1:
            self._consume_choice(actor, targets[0])
            return OUTCOME_FLOW
        self._arm_bot()
        self.refresh_menus(actor)
        if not actor.is_bot and actor.id:
            first = targets[0]
            self.request_menu_focus(
                actor, f"choose_{kind}_{first.id}"
            )
        return OUTCOME_CHOICE

    def _announce_discarded_action(
        self, actor: Flip7Player, kind: str, card: Flip7Card | None
    ) -> None:
        if kind == CHOICE_SECOND_CHANCE:
            self.broadcast_personal_l(
                actor,
                "flip7-you-discard-second-chance",
                "flip7-player-discards-second-chance",
                buffer="game",
            )
            return
        if card is not None:
            action = lambda locale: self._card_label(card, locale)
        else:
            action = lambda locale: Localization.get(locale, "flip7-card-freeze")
        self.broadcast_personal_l(
            actor,
            "flip7-you-discard-action",
            "flip7-player-discards-action",
            buffer="game",
            action=action,
        )

    def _consume_choice(self, actor: Flip7Player, target: Flip7Player) -> None:
        choice = self.pending_choice
        if choice is None:
            return
        card = choice.card
        self.pending_choice = None
        if self._apply_choice(actor, target, card, choice.kind):
            return
        self._after_choice_flow()

    def _apply_choice(
        self,
        actor: Flip7Player,
        target: Flip7Player,
        card: Flip7Card | None,
        kind: str,
    ) -> bool:
        """Resolve one choice; return True when a flow/flip now owns progress."""
        if kind == CHOICE_FREEZE:
            if card is not None:
                self.discard.append(card)
            target.round_status = STATUS_STAYED
            points = self.round_points(target)
            self.play_sound(audio.SOUND_STAY)
            if target is actor:
                self.broadcast_personal_l(
                    actor,
                    "flip7-you-stop-yourself",
                    "flip7-player-stops-themself",
                    buffer="game",
                    points=points,
                )
            else:
                self.broadcast_personal_l(
                    actor,
                    "flip7-you-stop-player",
                    "flip7-player-stops-player",
                    buffer="game",
                    target=target,
                    points=points,
                )
            self._start_bank_flow(AFTER_CHOICE, target)
            return True
        if kind == CHOICE_FLIP_THREE:
            if card is not None:
                self.discard.append(card)
            if target is actor:
                self.broadcast_personal_l(
                    actor,
                    "flip7-you-flip-three-self",
                    "flip7-player-flips-three-self",
                    buffer="game",
                )
            else:
                self.broadcast_personal_l(
                    actor,
                    "flip7-you-flip-three",
                    "flip7-player-flip-three",
                    buffer="game",
                    target=target,
                )
            self._start_flip_three(target)
            return True
        # CHOICE_SECOND_CHANCE
        if card is not None:
            target.cards.append(card)
        self.broadcast_personal_l(
            actor,
            "flip7-you-give-second-chance",
            "flip7-player-gives-second-chance",
            buffer="game",
            target=target,
        )
        return False

    def _start_bank_flow(self, continuation: str, player: Flip7Player) -> None:
        self.start_sequence(
            self._flow_id(SEQUENCE_CARD_FLOW_PREFIX, player, suffix="bank"),
            [
                SequenceBeat.after_audio(audio.sound_ticks(audio.SOUND_STAY)),
                SequenceBeat(ops=[SequenceOperation.callback_op(continuation)]),
            ],
            tag=TAG_FLOW,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _after_choice_flow(self) -> None:
        if self.flip_state is not None:
            # A Second Chance revealed by Flip Three is resolved immediately.
            # Once it has been given away (or discarded because no recipient
            # exists), resume the unfinished forced reveals.
            self._flip_draw()
            return
        if self.pending_actions:
            self._resolve_pending_flow()
        else:
            self._continue_flow()

    def _resolve_pending_flow(self) -> None:
        """Resolve queued forced action cards one targeted choice at a time."""
        while self.pending_actions:
            pending = self.pending_actions[0]
            owner = self.get_player_by_id(pending.owner_id)
            # A missing or busted owner voids only that owner's queued cards.
            # A frozen/stopped owner is not busting: the official Flip Three
            # rule still resolves the Flip Three/Freeze cards it revealed.
            if owner is None or owner.round_status == STATUS_BUSTED:
                dropped = self._discard_pending_actions_for(pending.owner_id)
                if owner is not None and dropped:
                    self.broadcast_personal_l(
                        owner,
                        "flip7-you-pending-bust-discarded",
                        "flip7-player-pending-bust-discarded",
                        buffer="game",
                    )
                continue
            self.pending_actions.pop(0)
            result = self._open_choice(pending.kind, owner, card=pending.card)
            if result == OUTCOME_CHOICE:
                return
            if result == OUTCOME_FLOW:
                return
        self._continue_flow()

    # ------------------------------------------------------------------
    # Flip Three
    # ------------------------------------------------------------------

    def _start_flip_three(self, target: Flip7Player) -> None:
        self.flip_state = Flip7FlipState(target_id=target.id)
        self._flip_draw()

    def _flip_draw(self) -> None:
        state = self.flip_state
        if state is None:
            return
        if state.remaining <= 0:
            self.flip_state = None
            self._flip_finish()
            return

        target = self.get_player_by_id(state.target_id)
        if not isinstance(target, Flip7Player):
            self.flip_state = None
            self._continue_flow()
            return
        if target.round_status != STATUS_PLAYING:
            self.flip_state = None
            self._flip_bust_abort(target.id)
            return

        card = self._draw_card()
        state.remaining -= 1
        self._resolve_card(
            target,
            card,
            forced=True,
            continuation=NEXT_FLIP_DRAW,
            pending_owner=target.id,
        )

    def _flip_finish(self) -> None:
        self.flip_state = None
        if self.pending_actions:
            self._resolve_pending_flow()
        else:
            self._continue_flow()

    # ------------------------------------------------------------------
    # Round flow
    # ------------------------------------------------------------------

    def _start_round(self) -> None:
        self.cancel_sequences_by_tag(TAG_FLOW)
        self._discard_pending_cards()
        self.round += 1
        self.phase = PHASE_PLAYING
        self.pending_choice = None
        self.pending_actions = []
        self.flip_state = None
        self.drawn_card = None

        active = self._active()
        for player in self.players:
            self._return_area_cards(player)
        for player in active:
            player.round_status = STATUS_PLAYING
        if not active:
            return

        if not self.deck:
            self._reshuffle_discard()

        count = len(active)
        self.dealer_index = (self.dealer_index + 1) % count
        dealer = active[self.dealer_index]
        ordered = [active[(self.dealer_index + 1 + i) % count] for i in range(count)]
        self.deal_order = [p.id for p in ordered]
        self.deal_index = 0

        self.play_sound(audio.SOUND_ROUND_START)
        self.broadcast_l(
            "flip7-round-start",
            buffer="game",
            round=self.round,
            dealer=dealer.name,
        )
        self.start_sequence(
            self._flow_id(SEQUENCE_ROUND_START_PREFIX, dealer, suffix="deal"),
            [
                # Sequence ops run at the START of a beat, so the cue needs its
                # own beat before the first card may be dealt.
                SequenceBeat.after_audio(audio.sound_ticks(audio.SOUND_ROUND_START)),
                SequenceBeat(ops=[SequenceOperation.callback_op("deal_step")]),
            ],
            tag=TAG_FLOW,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _deal_step(self) -> None:
        if self.deal_index >= len(self.deal_order):
            self._begin_turn_order()
            return

        player = self.get_player_by_id(self.deal_order[self.deal_index])
        self.deal_index += 1
        if not isinstance(player, Flip7Player):
            self._deal_step()
            return
        # A Freeze/Flip card already retired this player this round: they get
        # no start-of-round card and are skipped on later deals.
        if player.round_status != STATUS_PLAYING:
            self._deal_step()
            return

        card = self._draw_card()
        self._resolve_card(player, card, forced=False, continuation="deal_step")

    def _begin_turn_order(self) -> None:
        ordered = [
            player
            for player in (
                self.get_player_by_id(pid) for pid in self.deal_order
            )
            if isinstance(player, Flip7Player)
        ]
        self.deal_index = len(self.deal_order)
        self.set_turn_players(ordered)
        index = self._next_playing_slot(-1)
        if index < 0:
            self._end_round()
            return
        self.turn_index = index
        self.announce_turn()
        self._arm_bot()
        self.refresh_menus()

    def _continue_flow(self) -> None:
        if self.pending_choice is not None:
            self.refresh_menus()
            return
        if self.flip_state is not None:
            self.refresh_menus()
            return
        if self.pending_actions:
            self._resolve_pending_flow()
            return
        if self.deal_index < len(self.deal_order):
            self._deal_step()
            return
        index = self._next_playing_slot(self.turn_index)
        if index < 0:
            self._end_round()
            return
        self.turn_index = index
        self.announce_turn()
        self._arm_bot()
        self.refresh_menus()

    # ------------------------------------------------------------------
    # Round end
    # ------------------------------------------------------------------

    def _schedule_start_round(self) -> None:
        self.start_sequence(
            self._flow_id(SEQUENCE_ROUND_START_PREFIX, self._active()[0], suffix="next"),
            [
                SequenceBeat.after_audio(audio.sound_ticks(audio.SOUND_ROUND_END)),
                SequenceBeat(ops=[SequenceOperation.callback_op("start_round")]),
            ],
            tag=TAG_FLOW,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _discard_pending_cards(self) -> None:
        if self.pending_choice is not None:
            if self.pending_choice.card is not None:
                self.discard.append(self.pending_choice.card)
            self.pending_choice = None
        for pending in self.pending_actions:
            self.discard.append(pending.card)
        self.pending_actions = []
        if self.drawn_card is not None:
            self.discard.append(self.drawn_card)
        self.drawn_card = None

    def _end_round(self, *, flip_seven: Flip7Player | None = None) -> None:
        self.cancel_sequences_by_tag(TAG_FLOW)
        self.phase = PHASE_ROUND_END
        self.flip_state = None
        self._discard_pending_cards()

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

        for player in self.players:
            self._return_area_cards(player)

        self.play_sound(audio.SOUND_ROUND_END)
        self.broadcast_l("flip7-round-end", buffer="game", round=self.round)
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
            # Let the round-end cue, then the win cue and its announcement,
            # finish before the end screen replaces them.
            self.start_sequence(
                self._flow_id(SEQUENCE_MATCH_END_PREFIX, winner, suffix="win"),
                [
                    SequenceBeat.after_audio(audio.sound_ticks(audio.SOUND_ROUND_END)),
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op(audio.SOUND_MATCH_WIN),
                            SequenceOperation.callback_op(
                                "match_win",
                                {"winner_id": winner.id},
                            ),
                        ]
                    ),
                    SequenceBeat.after_audio(audio.sound_ticks(audio.SOUND_MATCH_WIN)),
                    SequenceBeat(ops=[SequenceOperation.callback_op("finish_match")]),
                ],
                tag=TAG_FLOW,
                lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                pause_bots=True,
            )
            return
        self._schedule_start_round()

    def _announce_match_win(self, payload: dict) -> None:
        winner = self.get_player_by_id(str(payload.get("winner_id", "")))
        if not isinstance(winner, Flip7Player):
            return
        self.broadcast_personal_l(
            winner, "flip7-match-win-you", "flip7-match-win", buffer="game"
        )

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
                # Non-actors keep their stable disabled hit/stay rows, exactly
                # as create_turn_action_set builds them. Reporting [] here would
                # make every before_menu_build() destroy and rebuild the set.
                return ["hit", "stay"]
            return [
                f"choose_{choice.kind}_{target.id}"
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

    def create_turn_action_set(self, player: Player) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        if self.pending_choice is not None:
            actor = self._choice_actor()
            if actor is player:
                # Only the actor's menu is replaced by the private decision.
                self._build_choice_actions(action_set, player, locale)
                return action_set
            # Everyone else keeps their own stable turn rows so their menu and
            # focus do not churn for one player's private choice; those rows
            # stay disabled with the localized waiting reason.

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
                label=Localization.get(locale, "flip7-stay-base"),
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
            action_id = f"choose_{kind}_{target.id}"
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
        if self.is_sequence_gameplay_locked():
            return "flip7-error-wait-card"
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
        return None

    def _is_stay_enabled(self, player: Player) -> str | None:
        if self.status != "playing" or self.phase != PHASE_PLAYING:
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.is_sequence_gameplay_locked():
            return "flip7-error-wait-card"
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
        if not flip_player.cards:
            return "flip7-error-no-cards-to-bank"
        return None

    def _is_choose_target_enabled(self, player: Player) -> str | None:
        if self.status != "playing" or self.phase != PHASE_PLAYING:
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.pending_choice is None:
            return "flip7-error-no-choice"
        if self._choice_actor() is not player:
            return "action-not-your-turn"
        if self.is_sequence_gameplay_locked():
            return "flip7-error-wait-card"
        return None

    def _get_hit_label(self, player: Player, action_id: str) -> str:
        locale = self._locale_of(player)
        return Localization.get(locale, "flip7-hit")

    def _get_stay_label(self, player: Player, action_id: str) -> str:
        locale = self._locale_of(player)
        flip_player: Flip7Player = player  # type: ignore[assignment]
        if flip_player.round_status == STATUS_STAYED:
            return Localization.get(locale, "flip7-stay-banked")
        if flip_player.round_status != STATUS_PLAYING:
            return Localization.get(locale, "flip7-stay-base")
        return Localization.get(
            locale, "flip7-stay", points=self.round_points(flip_player)
        )

    def _action_hit(self, player: Player, action_id: str) -> None:
        if self._is_hit_enabled(player) is not None:
            return
        flip_player: Flip7Player = player  # type: ignore[assignment]
        card = self._draw_card()
        self._resolve_card(
            flip_player, card, forced=False, continuation=CONTINUE_FLOW
        )

    def _action_stay(self, player: Player, action_id: str) -> None:
        if self._is_stay_enabled(player) is not None:
            return
        flip_player: Flip7Player = player  # type: ignore[assignment]
        flip_player.round_status = STATUS_STAYED
        # Repaint this player's persistent control immediately so its label no
        # longer advertises points that have already been banked.  The turn
        # advances only after the bank cue finishes.
        self.refresh_menus(flip_player)
        points = self.round_points(flip_player)
        self.play_sound(audio.SOUND_STAY)
        self.broadcast_personal_l(
            flip_player,
            "flip7-you-stay",
            "flip7-player-stays",
            buffer="game",
            points=points,
        )
        self._start_bank_flow(CONTINUE_FLOW, flip_player)

    def _action_choose_target(self, player: Player, action_id: str) -> None:
        if self._is_choose_target_enabled(player) is not None:
            return
        target_id = action_id.rsplit("_", 1)[-1]
        target = self.get_player_by_id(target_id)
        if target is None or target not in self._choice_targets():
            return
        flip_player: Flip7Player = player  # type: ignore[assignment]
        self._consume_choice(flip_player, target)  # type: ignore[arg-type]

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
            )
        )
        action_set.add(
            Action(
                id="check_table",
                label=Localization.get(locale, "flip7-check-table"),
                handler="_action_check_table",
                is_enabled="_is_check_table_enabled",
                is_hidden="_is_check_table_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_deck",
                label=Localization.get(locale, "flip7-check-deck"),
                handler="_action_check_deck",
                is_enabled="_is_check_deck_enabled",
                is_hidden="_is_check_deck_hidden",
                include_spectators=True,
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
        return self._touch_information_visibility(player)

    def _is_check_table_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return self._touch_information_visibility(player)

    def _is_check_deck_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return self._touch_information_visibility(player)

    def _touch_information_visibility(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_area_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_check_table_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_deck_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        if self.status == "playing" and self.is_touch_client(self.get_user(player)):
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        if self.is_touch_client(self.get_user(player)):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        if self.status == "playing" and self.is_touch_client(self.get_user(player)):
            return Visibility.VISIBLE
        return super()._is_check_scores_hidden(player)

    def _area_line(
        self, player: Flip7Player, locale: str, is_self: bool = True
    ) -> str:
        """Build a compact, complete summary of one public player area."""
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
        bonuses.extend(
            Localization.get(locale, "flip7-card-modifier", value=m)
            for m in player.modifiers
        )
        if player.has_double:
            bonuses.append(Localization.get(locale, "flip7-card-double"))
        if player.second_chance:
            bonuses.append(Localization.get(locale, "flip7-card-second-chance"))
        if bonuses:
            return Localization.get(
                locale,
                "flip7-area-inline-with-bonuses",
                who=who,
                status=status,
                numbers=numbers,
                points=self.round_points(player),
                bonuses=self._read_list(locale, bonuses),
            )
        return Localization.get(
            locale,
            "flip7-area-inline",
            who=who,
            status=status,
            numbers=numbers,
            points=self.round_points(player),
        )

    def _read_list(self, locale: str, items: list[str]) -> str:
        return Localization.format_list_and(locale, items)

    def _action_check_area(self, player: Player, action_id: str) -> None:
        if player.is_spectator:
            return
        flip_player: Flip7Player = player  # type: ignore[assignment]
        user = self.get_user(player)
        if user is None:
            return
        user.speak(self._area_line(flip_player, user.locale), buffer="game")

    def _action_check_table(self, player: Player, action_id: str) -> None:
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
            lines.append(
                Localization.get(
                    locale,
                    "flip7-table-line",
                    area=self._area_line(
                        other,
                        locale,
                        is_self=other is player,
                    ),
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
            Localization.get(locale, "flip7-stay-base"),
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
            include_spectators=True,
        )
        self.define_keybind(
            "d",
            Localization.get(locale, "flip7-check-deck"),
            ["check_deck"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

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
                "cards_drawn": p.cards_drawn,
            }
            for p in sorted_players
        }
        winner = sorted_players[0] if sorted_players else None
        rating_competitors = rating_competitors_from_scores(
            ([player.id], player.total_score) for player in sorted_players
        )
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(p) for p in self._active()
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "winner_score": winner.total_score if winner else 0,
                "final_scores": final_scores,
                "player_stats": player_stats,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
                RATING_COMPETITORS_KEY: rating_competitors,
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
