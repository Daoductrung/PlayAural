"""Dead Man's Dice, a hidden-dice bluffing and survival game."""

from __future__ import annotations

import random
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone

from mashumaro.mixins.json import DataClassJSONMixin

from ...audio import AudioSequenceSegment, seat_position
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.dice import roll_dice
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import MenuOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...game_utils.stats_helpers import (
    RATING_COMPETITORS_KEY,
    rating_competitors_from_scores,
)
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem, User
from ..base import Game, GameOptions, Player
from ..categories import CATEGORY_DICE
from ..registry import register_game
from . import audio as dice_audio
from .bot import BotObservation, choose_decision, is_legal_bid
from .bot import choose_quantity as choose_bot_quantity
from .constants import (
    DICE_PER_PLAYER,
    DIE_SIDES,
    MAX_POISON_DOSES,
    RULESET_BASIC,
    RULESET_TRADITIONAL,
    SUPPORTED_RULESETS,
)

BOT_THINK_TICKS = (32, 64)

RESULT_LIAR_BIDDER_LOST = "liar_bidder_lost"
RESULT_LIAR_CHALLENGER_LOST = "liar_challenger_lost"
RESULT_SPOT_CORRECT = "spot_correct"
RESULT_SPOT_WRONG = "spot_wrong"

SEQUENCE_OPENING = "deadmansdice_opening"
SEQUENCE_CHALLENGE = "deadmansdice_challenge"

RULE_LABEL_KEYS = {
    RULESET_TRADITIONAL: "deadmansdice-rules-traditional",
    RULESET_BASIC: "deadmansdice-rules-basic",
}
TABLE_RULE_KEYS = {
    RULESET_TRADITIONAL: "deadmansdice-table-rule-traditional",
    RULESET_BASIC: "deadmansdice-table-rule-basic",
}
MATCH_SETUP_KEYS = {
    RULESET_TRADITIONAL: "deadmansdice-match-setup-traditional",
    RULESET_BASIC: "deadmansdice-match-setup-basic",
}
CHALLENGE_RESULT_KEYS = {
    RESULT_LIAR_BIDDER_LOST: (
        "deadmansdice-your-bid-too-high",
        "deadmansdice-player-bid-too-high",
    ),
    RESULT_LIAR_CHALLENGER_LOST: (
        "deadmansdice-you-challenged-truth",
        "deadmansdice-player-challenged-truth",
    ),
    RESULT_SPOT_CORRECT: (
        "deadmansdice-your-spot-on-correct",
        "deadmansdice-player-spot-on-correct",
    ),
    RESULT_SPOT_WRONG: (
        "deadmansdice-your-spot-on-wrong",
        "deadmansdice-player-spot-on-wrong",
    ),
}
LAST_RESULT_PUBLIC_KEYS = {
    RESULT_LIAR_BIDDER_LOST: "deadmansdice-last-result-liar-bidder-lost",
    RESULT_LIAR_CHALLENGER_LOST: "deadmansdice-last-result-liar-challenger-lost",
    RESULT_SPOT_CORRECT: "deadmansdice-last-result-spot-correct",
    RESULT_SPOT_WRONG: "deadmansdice-last-result-spot-wrong",
}
LAST_RESULT_PERSONAL_KEYS = {
    RESULT_LIAR_BIDDER_LOST: "deadmansdice-last-result-liar-bidder-lost-you",
    RESULT_LIAR_CHALLENGER_LOST: (
        "deadmansdice-last-result-liar-challenger-lost-you"
    ),
    RESULT_SPOT_CORRECT: "deadmansdice-last-result-spot-correct-you",
    RESULT_SPOT_WRONG: "deadmansdice-last-result-spot-wrong-you",
}


@dataclass
class BidRecord(DataClassJSONMixin):
    """One public bid, stored with immutable identity and historical name."""

    player_id: str
    player_name: str
    quantity: int
    face: int


@dataclass
class DiceReveal(DataClassJSONMixin):
    """One player's dice in a completed public reveal."""

    player_id: str
    player_name: str
    dice: list[int] = field(default_factory=list)


@dataclass
class DeadMansDicePlayer(Player):
    """Persistent per-seat state for Dead Man's Dice."""

    dice: list[int] = field(default_factory=list)
    poison_doses: int = 0
    eliminated: bool = False
    eliminated_round: int = 0
    bids_made: int = 0
    liar_calls: int = 0
    spot_on_calls: int = 0


@dataclass
class DeadMansDiceOptions(GameOptions):
    """Host-selectable rules for Dead Man's Dice."""

    ruleset: str = option_field(
        MenuOption(
            default=RULESET_TRADITIONAL,
            choices=[RULESET_TRADITIONAL, RULESET_BASIC],
            value_key="rules",
            choice_labels={
                RULESET_TRADITIONAL: "deadmansdice-rules-traditional",
                RULESET_BASIC: "deadmansdice-rules-basic",
            },
            label="deadmansdice-set-rules",
            prompt="deadmansdice-select-rules",
            change_msg="deadmansdice-option-changed-rules",
            description="deadmansdice-rules-description",
        )
    )


@dataclass
@register_game
class DeadMansDiceGame(Game):
    """Server-authoritative five-dice bluffing with poison elimination."""

    players: list[DeadMansDicePlayer] = field(default_factory=list)
    options: DeadMansDiceOptions = field(default_factory=DeadMansDiceOptions)
    current_bid_quantity: int = 0
    current_bid_face: int = 0
    current_bidder_id: str = ""
    bid_history: list[BidRecord] = field(default_factory=list)
    winner_id: str = ""
    last_reveal_round: int = 0
    last_reveal: list[DiceReveal] = field(default_factory=list)
    last_reveal_quantity: int = 0
    last_reveal_face: int = 0
    last_reveal_actual: int = 0
    last_reveal_result: str = ""
    last_reveal_result_player_id: str = ""
    last_reveal_result_player_name: str = ""
    next_ambient_event_tick: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Dead Man's Dice"

    @classmethod
    def get_type(cls) -> str:
        return "deadmansdice"

    @classmethod
    def get_category(cls) -> str:
        return CATEGORY_DICE

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def supports_score_actions(self) -> bool:
        return False

    def create_player(
        self,
        player_id: str,
        name: str,
        is_bot: bool = False,
    ) -> DeadMansDicePlayer:
        return DeadMansDicePlayer(id=player_id, name=name, is_bot=is_bot)

    @property
    def alive_players(self) -> list[DeadMansDicePlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, DeadMansDicePlayer) and not player.eliminated
        ]

    @property
    def maximum_bid_quantity(self) -> int:
        return len(self.alive_players) * DICE_PER_PLAYER

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if self.options.ruleset not in SUPPORTED_RULESETS:
            errors.append("deadmansdice-error-rules-invalid")
        return errors

    def attach_user(
        self,
        player_id: str,
        user: User,
        *,
        session_handover: bool = False,
    ) -> None:
        """Replay or establish the listener's room-fixed spatial ambience."""

        super().attach_user(
            player_id,
            user,
            session_handover=session_handover,
        )
        player = self.get_player_by_id(player_id)
        if self.status == "playing" and player is not None and not player.is_bot:
            self._ensure_listener_ambience(player)
            opening = self._get_sequence(SEQUENCE_OPENING)
            if opening is not None and opening.current_index >= 1:
                user.speak_l("deadmansdice-intro", buffer="game")
            if opening is not None and opening.current_index >= 2:
                self._speak_match_setup(user)

    def _table_seats(self) -> list[DeadMansDicePlayer]:
        """Return stable physical seats; spectators listen from the centre."""

        return [
            player
            for player in self.players
            if isinstance(player, DeadMansDicePlayer) and not player.is_spectator
        ]

    def _seat_index(self, player: Player) -> int | None:
        return next(
            (
                index
                for index, seated in enumerate(self._table_seats())
                if seated.id == player.id
            ),
            None,
        )

    def _ensure_listener_ambience(self, listener: Player) -> None:
        """Start each missing room source in this listener's own frame."""

        user = self.get_user(listener)
        if user is None or listener.is_bot:
            return
        seats = self._table_seats()
        listener_index = self._seat_index(listener)
        for source in dice_audio.AMBIENCE_SOURCES:
            already_active = any(
                state.kind == "ambience"
                and state.scope == "player"
                and state.context == listener.id
                and state.layer == source.layer
                and listener.id in state.recipient_ids
                for state in self.active_audio.values()
            )
            if already_active:
                continue
            position = dice_audio.listener_relative_room_position(
                source.world_position,
                listener_index,
                len(seats),
            )
            self.play_private_ambience(
                listener,
                source.asset,
                layer=source.layer,
                fade_in_ms=dice_audio.AMBIENCE_FADE_IN_MS,
                fade_out_ms=dice_audio.AMBIENCE_FADE_OUT_MS,
                priority=dice_audio.AMBIENCE_PRIORITY,
                position=position,
                attenuation=dice_audio.ROOM_ATTENUATION,
                gain=source.gain,
            )

    def _start_room_ambience(self) -> None:
        for listener in self.players:
            if not listener.is_bot:
                self._ensure_listener_ambience(listener)

    def _play_room_one_shot(
        self,
        asset: str,
        world_position: tuple[float, float, float],
    ) -> None:
        """Play one room-fixed detail in every listener's local frame."""

        seats = self._table_seats()
        for listener in self.players:
            if listener.is_bot or self.get_user(listener) is None:
                continue
            position = dice_audio.listener_relative_room_position(
                world_position,
                self._seat_index(listener),
                len(seats),
            )
            self.play_sound_chain(
                [
                    AudioSequenceSegment(
                        asset=asset,
                        position=position,
                        attenuation=dice_audio.ROOM_ATTENUATION,
                        gain=dice_audio.AMBIENT_EVENT_GAIN,
                    )
                ],
                buffer="game",
                priority=dice_audio.AMBIENT_EVENT_PRIORITY,
                max_instances=1,
                audience=listener,
            )

    def _schedule_next_ambient_event(self) -> None:
        self.next_ambient_event_tick = self.sound_scheduler_tick + random.randint(  # nosec B311
            *dice_audio.AMBIENT_EVENT_INTERVAL_TICKS
        )

    def _maybe_play_ambient_event(self) -> None:
        if (
            self.status != "playing"
            or self.sound_scheduler_tick < self.next_ambient_event_tick
        ):
            return
        if self.active_sequences:
            self.next_ambient_event_tick = (
                self.sound_scheduler_tick + dice_audio.AMBIENT_EVENT_DEFER_TICKS
            )
            return
        self._play_room_one_shot(
            random.choice(dice_audio.SOUND_AMBIENT_EVENTS),  # nosec B311
            random.choice(dice_audio.AMBIENT_EVENT_WORLD_POSITIONS),  # nosec B311
        )
        self._schedule_next_ambient_event()

    def _play_seated_segments(
        self,
        events: list[tuple[DeadMansDicePlayer, AudioSequenceSegment]],
        *,
        priority: int,
    ) -> None:
        """Dispatch one atomic, listener-relative table sequence per person."""

        if not events:
            return
        seats = self._table_seats()
        seat_indexes = {player.id: index for index, player in enumerate(seats)}
        for listener in self.players:
            if listener.is_bot or self.get_user(listener) is None:
                continue
            listener_index = seat_indexes.get(listener.id)
            segments: list[AudioSequenceSegment] = []
            for emitter, authored_segment in events:
                emitter_index = seat_indexes.get(emitter.id)
                position = (
                    seat_position(emitter_index, listener_index, len(seats))
                    if emitter_index is not None
                    else None
                )
                segments.append(
                    replace(
                        authored_segment,
                        position=position,
                        attenuation=(
                            dice_audio.TABLE_EFFECT_ATTENUATION
                            if position is not None
                            else None
                        ),
                    )
                )
            self.play_sound_chain(
                segments,
                buffer="game",
                priority=priority,
                max_instances=dice_audio.TABLE_EFFECT_MAX_INSTANCES,
                audience=listener,
            )

    def _play_seated_sequence(
        self,
        events: list[tuple[DeadMansDicePlayer, str]],
        *,
        gain: float,
        priority: int,
        next_start_ratio: float = 1.0,
    ) -> None:
        self._play_seated_segments(
            [
                (
                    emitter,
                    AudioSequenceSegment(
                        asset=asset,
                        gain=gain,
                        next_start_ratio=next_start_ratio,
                    ),
                )
                for emitter, asset in events
            ],
            priority=priority,
        )

    def _play_round_shakes(self) -> None:
        players = self.alive_players
        shake_assets = random.sample(  # nosec B311
            dice_audio.SOUND_DICE_SHAKES,
            k=len(players),
        )
        self._play_seated_sequence(
            list(zip(players, shake_assets, strict=True)),
            gain=dice_audio.DICE_SHAKE_GAIN,
            priority=dice_audio.PRIORITY_DICE_SHAKE,
            next_start_ratio=0.0,
        )

    def _play_bid_tap(self, player: DeadMansDicePlayer) -> None:
        self._play_seated_sequence(
            [
                (player, random.choice(dice_audio.SOUND_BID_TAPS))  # nosec B311
            ],
            gain=dice_audio.BID_TAP_GAIN,
            priority=dice_audio.PRIORITY_BID,
        )

    def _play_challenge(self, player: DeadMansDicePlayer, *, spot_on: bool) -> None:
        self._play_seated_sequence(
            [
                (
                    player,
                    (
                        dice_audio.SOUND_CALL_SPOT_ON
                        if spot_on
                        else dice_audio.SOUND_CALL_LIAR
                    ),
                )
            ],
            gain=dice_audio.CHALLENGE_GAIN,
            priority=dice_audio.PRIORITY_CHALLENGE,
        )

    def _play_reveal(self, player: DeadMansDicePlayer) -> None:
        self._play_seated_sequence(
            [(player, dice_audio.SOUND_CUP_REVEAL)],
            gain=dice_audio.CUP_REVEAL_GAIN,
            priority=dice_audio.PRIORITY_REVEAL,
        )

    def _play_poison_outcomes(
        self,
        targets: list[DeadMansDicePlayer],
        poison_assets: dict[str, str],
        lethal_ids: set[str],
    ) -> None:
        events: list[tuple[DeadMansDicePlayer, AudioSequenceSegment]] = []
        for index, player in enumerate(targets):
            events.append(
                (
                    player,
                    AudioSequenceSegment(
                        asset=poison_assets[player.id],
                        gain=dice_audio.POISON_DRINK_GAIN,
                        next_start_ratio=(
                            dice_audio.POISON_DRINK_STAGGER_RATIO
                            if index < len(targets) - 1
                            else 1.0
                        ),
                    ),
                )
            )
        for player in targets:
            if player.id not in lethal_ids:
                continue
            events.extend(
                [
                    (
                        player,
                        AudioSequenceSegment(
                            asset=dice_audio.SOUND_DEATH_CHOKE,
                            gain=dice_audio.DEATH_CHOKE_GAIN,
                            next_start_ratio=dice_audio.DEATH_CHOKE_TO_FALL_RATIO,
                        ),
                    ),
                    (
                        player,
                        AudioSequenceSegment(
                            asset=dice_audio.SOUND_DEATH_HEADFALL,
                            gain=dice_audio.DEATH_HEADFALL_GAIN,
                        ),
                    ),
                ]
            )
        self._play_seated_segments(
            events,
            priority=dice_audio.PRIORITY_POISON,
        )

    def _play_win(self) -> None:
        self.play_sound_chain(
            [
                AudioSequenceSegment(
                    asset=dice_audio.SOUND_WIN,
                    gain=dice_audio.WIN_GAIN,
                )
            ],
            buffer="game",
            priority=dice_audio.PRIORITY_WIN,
            max_instances=1,
        )

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.current_bid_quantity = 0
        self.current_bid_face = 0
        self.current_bidder_id = ""
        self.bid_history.clear()
        self.winner_id = ""
        self.last_reveal_round = 0
        self.last_reveal.clear()
        self.last_reveal_quantity = 0
        self.last_reveal_face = 0
        self.last_reveal_actual = 0
        self.last_reveal_result = ""
        self.last_reveal_result_player_id = ""
        self.last_reveal_result_player_name = ""
        self.next_ambient_event_tick = 0
        self.clear_scheduled_sounds()
        self.cancel_all_sequences()

        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, DeadMansDicePlayer)
        ]
        for player in active_players:
            player.dice.clear()
            player.poison_doses = 0
            player.eliminated = False
            player.eliminated_round = 0
            player.bids_made = 0
            player.liar_calls = 0
            player.spot_on_calls = 0

        self._start_room_ambience()
        self.play_music(
            dice_audio.SOUND_MUSIC,
            fade_in_ms=dice_audio.MUSIC_FADE_IN_MS,
            fade_out_ms=dice_audio.MUSIC_FADE_OUT_MS,
            priority=dice_audio.MUSIC_PRIORITY,
            gain=dice_audio.MUSIC_GAIN,
        )
        self._schedule_next_ambient_event()

        initial_order = list(active_players)
        random.shuffle(initial_order)  # nosec B311
        self.set_turn_players([])
        self.start_sequence(
            SEQUENCE_OPENING,
            [
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("announce_intro")],
                    delay_after_ticks=dice_audio.OPENING_SETUP_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("announce_match_setup")],
                    delay_after_ticks=dice_audio.OPENING_ROLL_DELAY_TICKS,
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("start_first_round")]
                ),
            ],
            tag=SEQUENCE_OPENING,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={
                "starter_id": initial_order[0].id if initial_order else "",
                "turn_order_ids": [player.id for player in initial_order],
            },
        )
        self.refresh_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        self._maybe_play_ambient_event()
        if self.status == "playing" and not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def _start_round(self, starter_id: str) -> None:
        alive = self.alive_players
        if len(alive) <= 1:
            self._finish_match()
            return

        self.round += 1
        self.current_bid_quantity = 0
        self.current_bid_face = 0
        self.current_bidder_id = ""
        self.bid_history.clear()

        for player in self.get_active_players():
            if not isinstance(player, DeadMansDicePlayer):
                continue
            BotHelper.set_target(player, None)
            player.dice = (
                roll_dice(DICE_PER_PLAYER, DIE_SIDES) if not player.eliminated else []
            )

        ordered = self._round_order(starter_id)
        self.set_turn_players(ordered)
        self._play_round_shakes()
        self.broadcast_l(
            "deadmansdice-round-start",
            buffer="game",
            round=self.round,
            players=len(ordered),
            dice=len(ordered) * DICE_PER_PLAYER,
        )
        for player in ordered:
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "deadmansdice-your-dice",
                    buffer="game",
                    dice=self._format_dice(player.dice, user.locale),
                )

        self.announce_turn()
        self._jolt_current_bot()
        self.refresh_menus()

    def _round_order(self, starter_id: str) -> list[DeadMansDicePlayer]:
        alive_by_id = {player.id: player for player in self.alive_players}
        ordered = [
            alive_by_id[player_id]
            for player_id in self.turn_player_ids
            if player_id in alive_by_id
        ]
        ordered.extend(player for player in self.alive_players if player not in ordered)
        if not ordered:
            return []
        start_index = next(
            (index for index, player in enumerate(ordered) if player.id == starter_id),
            0,
        )
        return ordered[start_index:] + ordered[:start_index]

    def _jolt_current_bot(self) -> None:
        current = self.current_player
        if current and current.is_bot:
            BotHelper.jolt_bot(
                current,
                ticks=random.randint(*BOT_THINK_TICKS),  # nosec B311
            )

    def _advance_bidding_turn(self) -> None:
        self.advance_turn(announce=False)
        self.announce_turn()
        self._jolt_current_bot()
        self.refresh_menus()

    def _is_opening_sequence_active(self) -> bool:
        return self.has_active_sequence(sequence_id=SEQUENCE_OPENING)

    # ------------------------------------------------------------------
    # Actions and input
    # ------------------------------------------------------------------

    def create_turn_action_set(self, player: DeadMansDicePlayer) -> ActionSet:
        locale = self._player_locale(player)
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="call_liar",
                label=Localization.get(locale, "deadmansdice-call-liar"),
                description=Localization.get(
                    locale,
                    "deadmansdice-call-liar-description",
                ),
                handler="_action_call_liar",
                is_enabled="_is_call_liar_enabled",
                is_hidden="_is_turn_action_hidden",
                get_label="_get_call_liar_label",
                get_description="_get_call_liar_description",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="call_spot_on",
                label=Localization.get(locale, "deadmansdice-call-spot-on"),
                description=Localization.get(
                    locale,
                    "deadmansdice-call-spot-on-description",
                ),
                handler="_action_call_spot_on",
                is_enabled="_is_call_spot_on_enabled",
                is_hidden="_is_turn_action_hidden",
                get_label="_get_call_spot_on_label",
                get_description="_get_call_spot_on_description",
                show_in_actions_menu=False,
            )
        )
        for face in range(1, DIE_SIDES + 1):
            action_set.add(
                Action(
                    id=f"bid_face_{face}",
                    label=Localization.get(
                        locale,
                        "deadmansdice-bid-face",
                        face=self._face_label(locale, face),
                    ),
                    handler="_action_bid",
                    is_enabled="_is_bid_face_enabled",
                    is_hidden="_is_turn_action_hidden",
                    get_label="_get_bid_face_label",
                    get_description="_get_bid_face_description",
                    input_request=MenuInput(
                        prompt="deadmansdice-select-bid-quantity",
                        options="_bid_quantity_options",
                        option_label="_bid_quantity_label",
                        bot_select="_bot_select_bid_quantity",
                        locks_gameplay=True,
                    ),
                    show_in_actions_menu=False,
                )
            )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        action_set.add(
            Action(
                id="read_dice",
                label=Localization.get(locale, "deadmansdice-read-dice"),
                description=Localization.get(
                    locale,
                    "deadmansdice-read-dice-description",
                ),
                handler="_action_read_dice",
                is_enabled="_is_read_dice_enabled",
                is_hidden="_is_private_info_hidden",
            )
        )
        for action_id, label_key, description_key, handler in (
            (
                "read_table",
                "deadmansdice-read-table",
                "deadmansdice-read-table-description",
                "_action_read_table",
            ),
            (
                "review_bids",
                "deadmansdice-review-bids",
                "deadmansdice-review-bids-description",
                "_action_review_bids",
            ),
            (
                "review_last_reveal",
                "deadmansdice-review-last-reveal",
                "deadmansdice-review-last-reveal-description",
                "_action_review_last_reveal",
            ),
        ):
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(locale, label_key),
                    description=Localization.get(locale, description_key),
                    handler=handler,
                    is_enabled=(
                        "_is_last_reveal_enabled"
                        if action_id == "review_last_reveal"
                        else (
                            "_is_bid_history_enabled"
                            if action_id == "review_bids"
                            else "_is_public_info_enabled"
                        )
                    ),
                    is_hidden="_is_public_info_hidden",
                    include_spectators=True,
                )
            )

        if self.is_touch_client(self.get_user(player)):
            self._order_touch_standard_actions(
                action_set,
                [
                    "read_dice",
                    "read_table",
                    "review_bids",
                    "review_last_reveal",
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def before_menu_build(self, player: Player) -> None:
        """Rebuild device-dependent standard ordering after a live handover."""

        if self.get_action_set(player, "standard") is None:
            return
        self.remove_action_set(player, "standard")
        self.add_action_set(player, self.create_standard_action_set(player))

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        locale = self._host_locale()
        for face in range(1, DIE_SIDES + 1):
            self.define_keybind(
                str(face),
                Localization.get(
                    locale,
                    "deadmansdice-bid-face",
                    face=self._face_label(locale, face),
                ),
                [f"bid_face_{face}"],
                state=KeybindState.ACTIVE,
            )
        for key, label_key, action_id, spectators in (
            ("c", "deadmansdice-call-liar", "call_liar", False),
            ("o", "deadmansdice-call-spot-on", "call_spot_on", False),
            ("d", "deadmansdice-read-dice", "read_dice", False),
            ("v", "deadmansdice-read-table", "read_table", True),
            ("b", "deadmansdice-review-bids", "review_bids", True),
            ("r", "deadmansdice-review-last-reveal", "review_last_reveal", True),
        ):
            self.define_keybind(
                key,
                Localization.get(locale, label_key),
                [action_id],
                state=KeybindState.ACTIVE,
                include_spectators=spectators,
            )

    def _is_mutating_turn_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self._is_opening_sequence_active():
            return "deadmansdice-action-opening"
        if self.is_sequence_gameplay_locked():
            return "deadmansdice-action-sequence-running"
        if player.is_spectator:
            return "action-spectator"
        if not isinstance(player, DeadMansDicePlayer):
            return "action-not-available"
        if player.eliminated:
            return "deadmansdice-action-eliminated"
        if self.current_player is not player:
            return "action-not-your-turn"
        if self._gameplay_input_lock_owner(exclude_player_id=player.id):
            return "deadmansdice-action-selection-open"
        return None

    def _is_bid_face_enabled(
        self,
        player: Player,
        *,
        action_id: str | None = None,
    ) -> str | None:
        error = self._is_mutating_turn_enabled(player)
        if error:
            return error
        face = self._face_from_action(action_id)
        if face is None or not self._legal_quantities(face):
            return "deadmansdice-action-face-unavailable"
        return None

    def _is_call_liar_enabled(self, player: Player) -> str | None:
        error = self._is_mutating_turn_enabled(player)
        if error:
            return error
        if not self.current_bid_quantity:
            return "deadmansdice-action-no-bid"
        return None

    def _is_call_spot_on_enabled(self, player: Player) -> str | None:
        return self._is_call_liar_enabled(player)

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        if (
            self.status != "playing"
            or self._is_opening_sequence_active()
            or player.is_spectator
        ):
            return Visibility.HIDDEN
        if isinstance(player, DeadMansDicePlayer) and not player.eliminated:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_read_dice_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, DeadMansDicePlayer) or player.is_spectator:
            return "action-spectator"
        if player.eliminated:
            return "deadmansdice-action-eliminated"
        if self._is_opening_sequence_active():
            return "deadmansdice-action-opening-no-dice"
        if len(player.dice) != DICE_PER_PLAYER:
            return "deadmansdice-action-no-dice"
        return None

    def _is_public_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_bid_history_enabled(self, player: Player) -> str | None:
        error = self._is_public_info_enabled(player)
        if error:
            return error
        if self._is_opening_sequence_active():
            return "deadmansdice-action-opening-no-bids"
        return None

    def _is_last_reveal_enabled(self, player: Player) -> str | None:
        error = self._is_public_info_enabled(player)
        if error:
            return error
        if not self.last_reveal:
            return "deadmansdice-action-no-last-reveal"
        return None

    def _is_private_info_hidden(self, player: Player) -> Visibility:
        if not self.is_touch_client(self.get_user(player)):
            return Visibility.HIDDEN
        return (
            Visibility.VISIBLE
            if self._is_read_dice_enabled(player) is None
            else Visibility.HIDDEN
        )

    def _is_public_info_hidden(self, player: Player) -> Visibility:
        if not self.is_touch_client(self.get_user(player)):
            return Visibility.HIDDEN
        return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        if self.is_touch_client(self.get_user(player)) and self.status == "playing":
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        if self.is_touch_client(self.get_user(player)):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _get_bid_face_label(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        face = self._face_from_action(action_id) or 1
        legal = self._legal_quantities(face)
        if not self.current_bid_quantity or not legal:
            key = "deadmansdice-bid-face"
            kwargs = {"face": self._face_label(locale, face)}
        else:
            key = "deadmansdice-bid-face-minimum"
            kwargs = {
                "face": self._face_label(locale, face),
                "minimum": min(legal),
            }
        return Localization.get(locale, key, **kwargs)

    def _get_call_liar_label(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        if not self.current_bid_quantity:
            return Localization.get(locale, "deadmansdice-call-liar")
        return Localization.get(
            locale,
            "deadmansdice-call-liar-current",
            quantity=self.current_bid_quantity,
            face=self._face_label(
                locale,
                self.current_bid_face,
                quantity=self.current_bid_quantity,
            ),
        )

    def _get_call_liar_description(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        if not self.current_bid_quantity:
            return Localization.get(locale, "deadmansdice-call-liar-description")
        return Localization.get(
            locale,
            "deadmansdice-call-liar-current-description",
            quantity=self.current_bid_quantity,
            face=self._face_label(
                locale,
                self.current_bid_face,
                quantity=self.current_bid_quantity,
            ),
        )

    def _get_call_spot_on_label(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        if not self.current_bid_quantity:
            return Localization.get(locale, "deadmansdice-call-spot-on")
        return Localization.get(
            locale,
            "deadmansdice-call-spot-on-current",
            quantity=self.current_bid_quantity,
            face=self._face_label(
                locale,
                self.current_bid_face,
                quantity=self.current_bid_quantity,
            ),
        )

    def _get_call_spot_on_description(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        if not self.current_bid_quantity:
            return Localization.get(locale, "deadmansdice-call-spot-on-description")
        return Localization.get(
            locale,
            "deadmansdice-call-spot-on-current-description",
            quantity=self.current_bid_quantity,
            face=self._face_label(
                locale,
                self.current_bid_face,
                quantity=self.current_bid_quantity,
            ),
        )

    def _get_bid_face_description(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        face = self._face_from_action(action_id) or 1
        return Localization.get(
            locale,
            "deadmansdice-bid-face-description",
            face=self._face_label(locale, face),
        )

    def _bid_quantity_options(self, player: Player) -> list[str]:
        face = self._pending_bid_face(player)
        return (
            [str(quantity) for quantity in self._legal_quantities(face)] if face else []
        )

    def _bid_quantity_label(self, player: Player, option: str) -> str:
        locale = self._player_locale(player)
        face = self._pending_bid_face(player) or 1
        return Localization.get(
            locale,
            "deadmansdice-bid-option",
            quantity=int(option),
            face=self._face_label(locale, face, quantity=int(option)),
        )

    def _on_action_menu_input_opened(
        self,
        action: Action,
        player: Player,
    ) -> None:
        """Announce the selected face once when its quantity picker opens."""

        face = self._face_from_action(action.id)
        user = self.get_user(player)
        if face is None or not user:
            super()._on_action_menu_input_opened(action, player)
            return
        user.speak_l(
            "deadmansdice-select-bid-quantity-for-face",
            buffer="game",
            history=False,
            face=self._face_label(user.locale, face),
        )

    def _bot_select_bid_quantity(
        self,
        player: DeadMansDicePlayer,
        options: list[str],
    ) -> str | None:
        face = self._pending_bid_face(player)
        if face is None:
            return None
        quantities = [int(option) for option in options]
        target = BotHelper.get_target(player)
        BotHelper.set_target(player, None)
        if target in quantities:
            return str(target)
        return str(
            choose_bot_quantity(
                self._bot_observation(player),
                face,
                quantities,
            )
        )

    def _action_bid(
        self,
        player: Player,
        input_value: str,
        action_id: str,
    ) -> None:
        if not isinstance(player, DeadMansDicePlayer):
            return
        face = self._face_from_action(action_id)
        try:
            quantity = int(input_value)
        except (TypeError, ValueError):
            self._speak_action_disabled_reason(
                player, "deadmansdice-action-invalid-bid"
            )
            return
        if face is None or quantity not in self._legal_quantities(face):
            self._speak_action_disabled_reason(
                player, "deadmansdice-action-invalid-bid"
            )
            return

        self.current_bid_quantity = quantity
        self.current_bid_face = face
        self.current_bidder_id = player.id
        self.bid_history.append(
            BidRecord(
                player_id=player.id,
                player_name=player.name,
                quantity=quantity,
                face=face,
            )
        )
        player.bids_made += 1
        self._play_bid_tap(player)
        self.broadcast_personal_l(
            player,
            "deadmansdice-you-bid",
            "deadmansdice-player-bids",
            buffer="game",
            quantity=quantity,
            face=lambda locale: self._face_label(locale, face, quantity=quantity),
        )
        self._advance_bidding_turn()

    def _action_call_liar(self, player: Player, action_id: str) -> None:
        if (
            not isinstance(player, DeadMansDicePlayer)
            or not self.current_bid_quantity
            or self.is_sequence_gameplay_locked()
        ):
            return
        bidder = self.get_player_by_id(self.current_bidder_id)
        if not isinstance(bidder, DeadMansDicePlayer):
            return
        player.liar_calls += 1
        self._play_challenge(player, spot_on=False)
        self.broadcast_personal_l(
            player,
            "deadmansdice-you-call-liar",
            "deadmansdice-player-calls-liar",
            buffer="game",
            bidder=bidder,
            quantity=self.current_bid_quantity,
            face=lambda locale: self._face_label(
                locale,
                self.current_bid_face,
                quantity=self.current_bid_quantity,
            ),
        )

        actual = self._actual_count(self.current_bid_face)
        if actual < self.current_bid_quantity:
            loser = bidder
            result = RESULT_LIAR_BIDDER_LOST
        else:
            loser = player
            result = RESULT_LIAR_CHALLENGER_LOST
        self._start_challenge_sequence(
            actual=actual,
            result=result,
            result_player_id=loser.id,
            target_ids=[loser.id],
            starter_id=loser.id,
        )

    def _action_call_spot_on(self, player: Player, action_id: str) -> None:
        if (
            not isinstance(player, DeadMansDicePlayer)
            or not self.current_bid_quantity
            or self.is_sequence_gameplay_locked()
        ):
            return
        bidder = self.get_player_by_id(self.current_bidder_id)
        if not isinstance(bidder, DeadMansDicePlayer):
            return
        player.spot_on_calls += 1
        self._play_challenge(player, spot_on=True)
        self.broadcast_personal_l(
            player,
            "deadmansdice-you-call-spot-on",
            "deadmansdice-player-calls-spot-on",
            buffer="game",
            bidder=bidder,
            quantity=self.current_bid_quantity,
            face=lambda locale: self._face_label(
                locale,
                self.current_bid_face,
                quantity=self.current_bid_quantity,
            ),
        )

        actual = self._actual_count(self.current_bid_face)
        order = list(self.turn_player_ids)
        if actual == self.current_bid_quantity:
            result = RESULT_SPOT_CORRECT
            targets = [
                candidate for candidate in self.alive_players if candidate is not player
            ]
        else:
            result = RESULT_SPOT_WRONG
            targets = [player]
        self._start_challenge_sequence(
            actual=actual,
            result=result,
            result_player_id=player.id,
            target_ids=[target.id for target in targets],
            starter_id=player.id,
            old_order=order,
        )

    # ------------------------------------------------------------------
    # Challenge resolution
    # ------------------------------------------------------------------

    def _start_challenge_sequence(
        self,
        *,
        actual: int,
        result: str,
        result_player_id: str,
        target_ids: list[str],
        starter_id: str,
        old_order: list[str] | None = None,
    ) -> None:
        reveals = [
            {
                "player_id": player.id,
                "player_name": player.name,
                "dice": list(player.dice),
            }
            for player in self.alive_players
        ]
        targets = [
            target
            for target_id in target_ids
            if isinstance(
                target := self.get_player_by_id(target_id),
                DeadMansDicePlayer,
            )
            and not target.eliminated
        ]
        poison_assets = {
            target.id: random.choice(dice_audio.SOUND_POISON_DRINKS)  # nosec B311
            for target in targets
        }
        lethal_ids = [
            target.id
            for target in targets
            if target.poison_doses + 1 >= MAX_POISON_DOSES
        ]
        poison_timeline = [
            (
                poison_assets[target.id],
                (
                    dice_audio.POISON_DRINK_STAGGER_RATIO
                    if index < len(targets) - 1
                    else 1.0
                ),
            )
            for index, target in enumerate(targets)
        ]
        for _lethal_id in lethal_ids:
            poison_timeline.extend(
                [
                    (
                        dice_audio.SOUND_DEATH_CHOKE,
                        dice_audio.DEATH_CHOKE_TO_FALL_RATIO,
                    ),
                    (dice_audio.SOUND_DEATH_HEADFALL, 1.0),
                ]
            )
        poison_duration = dice_audio.finite_sequence_duration_ticks(poison_timeline)

        reveal_delay = (
            dice_audio.sound_ticks(dice_audio.SOUND_CUP_REVEAL)
            + dice_audio.REVEAL_ANNOUNCEMENT_PAUSE_TICKS
        )
        beats = [
            SequenceBeat.after_audio(
                max(
                    dice_audio.sound_ticks(dice_audio.SOUND_CALL_LIAR),
                    dice_audio.sound_ticks(dice_audio.SOUND_CALL_SPOT_ON),
                ),
                wait_ratio=dice_audio.CHALLENGE_WAIT_RATIO,
            ),
            SequenceBeat(ops=[SequenceOperation.callback_op("begin_reveal")]),
        ]
        beats.extend(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "reveal_player",
                        {"index": index},
                    )
                ],
                delay_after_ticks=reveal_delay,
            )
            for index in range(len(reveals))
        )
        beats.extend(
            [
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("announce_reveal_total")],
                    delay_after_ticks=dice_audio.REVEAL_TOTAL_PAUSE_TICKS,
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("announce_challenge_result")],
                    delay_after_ticks=dice_audio.RESULT_ANNOUNCEMENT_PAUSE_TICKS,
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("resolve_poison")],
                    delay_after_ticks=(
                        poison_duration + dice_audio.POST_POISON_PAUSE_TICKS
                    ),
                ),
            ]
        )
        if lethal_ids:
            beats.append(
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("announce_eliminations")],
                    delay_after_ticks=(dice_audio.ELIMINATION_ANNOUNCEMENT_PAUSE_TICKS),
                )
            )
        beats.append(
            SequenceBeat(
                ops=[SequenceOperation.callback_op("continue_after_challenge")]
            )
        )
        self.start_sequence(
            SEQUENCE_CHALLENGE,
            beats,
            tag=SEQUENCE_CHALLENGE,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={
                "actual": actual,
                "result": result,
                "result_player_id": result_player_id,
                "reveals": reveals,
                "target_ids": [target.id for target in targets],
                "poison_assets": poison_assets,
                "lethal_ids": lethal_ids,
                "starter_id": starter_id,
                "old_order": list(old_order or self.turn_player_ids),
            },
        )
        self.refresh_menus()

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        if sequence_id == SEQUENCE_OPENING:
            self._handle_opening_callback(callback_id)
            return
        if sequence_id != SEQUENCE_CHALLENGE:
            super().on_sequence_callback(sequence_id, callback_id, payload)
            return
        sequence = self._get_sequence(sequence_id)
        if sequence is None:
            return
        metadata = sequence.metadata
        result_player = self.get_player_by_id(str(metadata["result_player_id"]))
        if not isinstance(result_player, DeadMansDicePlayer):
            self.cancel_sequence(sequence_id)
            return

        if callback_id == "begin_reveal":
            self._begin_reveal()
            return

        if callback_id == "reveal_player":
            self._reveal_player(metadata, int(payload.get("index", -1)))
            return

        if callback_id == "announce_reveal_total":
            self._announce_reveal_total(int(metadata["actual"]))
            return

        if callback_id == "announce_challenge_result":
            result = str(metadata["result"])
            self.last_reveal_result = result
            self.last_reveal_result_player_id = result_player.id
            self.last_reveal_result_player_name = result_player.name
            self._announce_challenge_result(result, result_player)
            self.refresh_menus()
            return

        if callback_id == "resolve_poison":
            self._apply_poison_batch(
                self._challenge_targets(metadata),
                {
                    str(player_id): str(asset)
                    for player_id, asset in metadata["poison_assets"].items()
                },
                {str(player_id) for player_id in metadata["lethal_ids"]},
            )
            return

        if callback_id == "announce_eliminations":
            self._announce_eliminations(
                [str(player_id) for player_id in metadata["lethal_ids"]]
            )
            return

        if callback_id == "continue_after_challenge":
            self._continue_after_challenge(
                str(metadata["starter_id"]),
                [str(player_id) for player_id in metadata["old_order"]],
            )

    def _handle_opening_callback(self, callback_id: str) -> None:
        sequence = self._get_sequence(SEQUENCE_OPENING)
        if sequence is None:
            return
        if callback_id == "announce_intro":
            self.broadcast_l("deadmansdice-intro", buffer="game")
            return
        if callback_id == "announce_match_setup":
            self.broadcast_l(
                self._match_setup_key(),
                buffer="game",
                players=len(self.alive_players),
                rules=lambda locale: self._rules_label(locale),
            )
            return
        if callback_id == "start_first_round":
            alive_by_id = {player.id: player for player in self.alive_players}
            turn_order_ids = [
                str(player_id)
                for player_id in sequence.metadata.get("turn_order_ids", [])
            ]
            initial_order = [
                alive_by_id[player_id]
                for player_id in turn_order_ids
                if player_id in alive_by_id
            ]
            initial_order.extend(
                player for player in self.alive_players if player not in initial_order
            )
            self.set_turn_players(initial_order)
            self._start_round(str(sequence.metadata.get("starter_id", "")))

    def _challenge_targets(self, metadata: dict) -> list[DeadMansDicePlayer]:
        return [
            target
            for target_id in metadata["target_ids"]
            if isinstance(
                target := self.get_player_by_id(str(target_id)),
                DeadMansDicePlayer,
            )
        ]

    def _announce_challenge_result(
        self,
        result: str,
        result_player: DeadMansDicePlayer,
    ) -> None:
        personal_key, public_key = CHALLENGE_RESULT_KEYS[result]
        self.broadcast_personal_l(
            result_player,
            personal_key,
            public_key,
            buffer="game",
        )

    def _begin_reveal(self) -> None:
        self.last_reveal_round = self.round
        self.last_reveal.clear()
        self.last_reveal_quantity = self.current_bid_quantity
        self.last_reveal_face = self.current_bid_face
        self.last_reveal_actual = 0
        self.last_reveal_result = ""
        self.last_reveal_result_player_id = ""
        self.last_reveal_result_player_name = ""

    def _reveal_player(self, metadata: dict, index: int) -> None:
        reveals = metadata["reveals"]
        if not 0 <= index < len(reveals):
            return
        serialized = reveals[index]
        player_id = str(serialized["player_id"])
        if any(reveal.player_id == player_id for reveal in self.last_reveal):
            return
        player = self.get_player_by_id(player_id)
        if not isinstance(player, DeadMansDicePlayer):
            return
        reveal = DiceReveal(
            player_id=player_id,
            player_name=str(serialized["player_name"]),
            dice=[int(value) for value in serialized["dice"]],
        )
        self.last_reveal.append(reveal)
        self._play_reveal(player)
        self.broadcast_personal_l(
            player,
            "deadmansdice-your-cup-reveals",
            "deadmansdice-player-cup-reveals",
            buffer="game",
            dice=lambda locale: self._format_dice(reveal.dice, locale),
        )
        self.refresh_menus()

    def _announce_reveal_total(self, actual: int) -> None:
        self.last_reveal_actual = actual
        self.broadcast_l(
            "deadmansdice-reveal-total",
            buffer="game",
            quantity=self.current_bid_quantity,
            face=lambda locale: self._face_label(
                locale,
                self.current_bid_face,
                quantity=self.current_bid_quantity,
            ),
            actual=actual,
        )

    def _apply_poison_batch(
        self,
        targets: list[DeadMansDicePlayer],
        poison_assets: dict[str, str],
        lethal_ids: set[str],
    ) -> None:
        active_targets = [target for target in targets if not target.eliminated]
        selected_assets = {
            player.id: (
                poison_assets.get(player.id, dice_audio.SOUND_POISON_DRINKS[0])
                if poison_assets.get(player.id) in dice_audio.SOUND_POISON_DRINKS
                else dice_audio.SOUND_POISON_DRINKS[0]
            )
            for player in active_targets
        }
        self._play_poison_outcomes(active_targets, selected_assets, lethal_ids)
        for player in active_targets:
            player.poison_doses += 1
            self.broadcast_personal_l(
                player,
                "deadmansdice-you-drink-poison",
                "deadmansdice-player-drinks-poison",
                buffer="game",
                doses=player.poison_doses,
                maximum=MAX_POISON_DOSES,
            )
            if player.poison_doses < MAX_POISON_DOSES:
                continue
            player.eliminated = True
            player.eliminated_round = self.round
            player.dice.clear()
        self.refresh_menus()

    def _announce_eliminations(self, lethal_ids: list[str]) -> None:
        for player_id in lethal_ids:
            player = self.get_player_by_id(player_id)
            if not isinstance(player, DeadMansDicePlayer) or not player.eliminated:
                continue
            self.broadcast_personal_l(
                player,
                "deadmansdice-you-eliminated",
                "deadmansdice-player-eliminated",
                buffer="game",
            )

    def _continue_after_challenge(
        self, preferred_id: str, old_order: list[str]
    ) -> None:
        if len(self.alive_players) <= 1:
            self._finish_match()
            return
        starter_id = self._next_alive_id(preferred_id, old_order)
        self._start_round(starter_id)

    def _next_alive_id(self, preferred_id: str, old_order: list[str]) -> str:
        alive_ids = {player.id for player in self.alive_players}
        if preferred_id in alive_ids:
            return preferred_id
        if not old_order:
            return next(iter(alive_ids), "")
        try:
            start = old_order.index(preferred_id)
        except ValueError:
            start = -1
        for offset in range(1, len(old_order) + 1):
            candidate = old_order[(start + offset) % len(old_order)]
            if candidate in alive_ids:
                return candidate
        return next(iter(alive_ids), "")

    def _finish_match(self) -> None:
        winner = self.alive_players[0] if len(self.alive_players) == 1 else None
        self.winner_id = winner.id if winner else ""
        if winner:
            self._play_win()
            self.broadcast_personal_l(
                winner,
                "deadmansdice-you-win",
                "deadmansdice-player-wins",
                buffer="game",
            )
        self.finish_game()

    # ------------------------------------------------------------------
    # Information views
    # ------------------------------------------------------------------

    def _action_read_dice(self, player: Player, action_id: str) -> None:
        if not isinstance(player, DeadMansDicePlayer):
            return
        user = self.get_user(player)
        if user:
            user.speak_l(
                "deadmansdice-your-dice",
                buffer="game",
                dice=self._format_dice(player.dice, user.locale),
            )

    def _action_read_table(self, player: Player, action_id: str) -> None:
        self.live_status_box(player, "deadmansdice_table", self._build_table_status)

    def _action_review_bids(self, player: Player, action_id: str) -> None:
        self.live_status_box(player, "deadmansdice_bids", self._build_bid_status)

    def _action_review_last_reveal(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "deadmansdice_last_reveal",
            self._build_last_reveal_status,
        )

    def _build_table_status(self, player: Player, user) -> list[MenuItem]:
        locale = user.locale
        opening = self._is_opening_sequence_active()
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    (
                        "deadmansdice-table-opening-header"
                        if opening
                        else "deadmansdice-table-header"
                    ),
                    rules=self._rules_label(locale),
                    round=self.round,
                ),
                id="header",
            )
        ]
        items.append(
            MenuItem(
                text=Localization.get(
                    locale,
                    (
                        "deadmansdice-table-pool-opening"
                        if opening
                        else "deadmansdice-table-pool"
                    ),
                    players=len(self.alive_players),
                    dice=self.maximum_bid_quantity,
                ),
                id="pool",
            )
        )
        items.append(
            MenuItem(
                text=Localization.get(
                    locale,
                    self._table_rule_key(),
                ),
                id="rule_detail",
            )
        )
        bidder = self.get_player_by_id(self.current_bidder_id)
        if self.current_bid_quantity and bidder:
            bid_text = Localization.get(
                locale,
                (
                    "deadmansdice-table-current-bid-you"
                    if bidder.id == player.id
                    else "deadmansdice-table-current-bid"
                ),
                quantity=self.current_bid_quantity,
                face=self._face_label(
                    locale,
                    self.current_bid_face,
                    quantity=self.current_bid_quantity,
                ),
                player=bidder.name,
            )
        else:
            bid_text = Localization.get(locale, "deadmansdice-table-no-bid")
        items.append(MenuItem(text=bid_text, id="current_bid"))

        current = self.current_player
        if current is None or opening:
            turn_text = Localization.get(locale, "deadmansdice-table-no-turn")
        elif current.id == player.id:
            turn_text = Localization.get(locale, "deadmansdice-table-turn-you")
        else:
            turn_text = Localization.get(
                locale,
                "deadmansdice-table-turn",
                player=current.name,
            )
        items.append(MenuItem(text=turn_text, id="turn"))
        for table_player in self.get_active_players():
            if not isinstance(table_player, DeadMansDicePlayer):
                continue
            if table_player.id == player.id:
                key = (
                    "deadmansdice-table-player-you-eliminated"
                    if table_player.eliminated
                    else "deadmansdice-table-player-you"
                )
            else:
                key = (
                    "deadmansdice-table-player-eliminated"
                    if table_player.eliminated
                    else "deadmansdice-table-player"
                )
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        key,
                        player=table_player.name,
                        doses=table_player.poison_doses,
                        maximum=MAX_POISON_DOSES,
                    ),
                    id=f"player:{table_player.id}",
                )
            )
        return items

    def _build_bid_status(self, player: Player, user) -> list[MenuItem]:
        locale = user.locale
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "deadmansdice-bids-header",
                    round=self.round,
                ),
                id="header",
            )
        ]
        if not self.bid_history:
            items.append(
                MenuItem(
                    text=Localization.get(locale, "deadmansdice-bids-none"),
                    id="none",
                )
            )
            return items
        for index, bid in enumerate(self.bid_history, 1):
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        (
                            "deadmansdice-bids-line-you"
                            if bid.player_id == player.id
                            else "deadmansdice-bids-line"
                        ),
                        index=index,
                        player=bid.player_name,
                        quantity=bid.quantity,
                        face=self._face_label(
                            locale,
                            bid.face,
                            quantity=bid.quantity,
                        ),
                    ),
                    id=f"bid:{index}:{bid.player_id}",
                )
            )
        return items

    def _build_last_reveal_status(self, player: Player, user) -> list[MenuItem]:
        locale = user.locale
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "deadmansdice-last-reveal-header",
                    round=self.last_reveal_round,
                ),
                id="header",
            )
        ]
        for reveal in self.last_reveal:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        (
                            "deadmansdice-last-reveal-player-you"
                            if reveal.player_id == player.id
                            else "deadmansdice-last-reveal-player"
                        ),
                        player=reveal.player_name,
                        dice=self._format_dice(reveal.dice, locale),
                    ),
                    id=f"player:{reveal.player_id}",
                )
            )
        if self.last_reveal_result:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "deadmansdice-last-reveal-result",
                        quantity=self.last_reveal_quantity,
                        face=self._face_label(
                            locale,
                            self.last_reveal_face,
                            quantity=self.last_reveal_quantity,
                        ),
                        actual=self.last_reveal_actual,
                        result=self._last_result_text(locale, player),
                    ),
                    id=f"result:{self.last_reveal_result_player_id}",
                )
            )
        else:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "deadmansdice-last-reveal-pending",
                    ),
                    id="result:pending",
                )
            )
        return items

    # ------------------------------------------------------------------
    # Rules, formatting, and bots
    # ------------------------------------------------------------------

    def _legal_quantities(self, face: int | None) -> list[int]:
        if face is None:
            return []
        return [
            quantity
            for quantity in range(1, self.maximum_bid_quantity + 1)
            if is_legal_bid(
                quantity,
                face,
                self.current_bid_quantity,
                self.current_bid_face,
                self.maximum_bid_quantity,
            )
        ]

    def _actual_count(self, face: int) -> int:
        dice = [value for player in self.alive_players for value in player.dice]
        if self.options.ruleset == RULESET_TRADITIONAL and face != 1:
            return sum(value in {1, face} for value in dice)
        return dice.count(face)

    def _bot_observation(self, player: DeadMansDicePlayer) -> BotObservation:
        bidder = self.get_player_by_id(self.current_bidder_id)
        return BotObservation(
            own_dice=tuple(player.dice),
            unknown_dice=max(0, self.maximum_bid_quantity - len(player.dice)),
            maximum_quantity=self.maximum_bid_quantity,
            ones_are_wild=self.options.ruleset == RULESET_TRADITIONAL,
            poison_doses=player.poison_doses,
            poison_limit=MAX_POISON_DOSES,
            current_quantity=self.current_bid_quantity,
            current_face=self.current_bid_face,
            bid_history=tuple(
                (bid.quantity, bid.face, bid.player_id == player.id)
                for bid in self.bid_history
            ),
            bidder_poison_doses=(
                bidder.poison_doses if isinstance(bidder, DeadMansDicePlayer) else 0
            ),
            opponent_poison_doses=tuple(
                opponent.poison_doses
                for opponent in self.alive_players
                if opponent is not player
            ),
        )

    def bot_think(self, player: DeadMansDicePlayer) -> str | None:
        if self._is_mutating_turn_enabled(player):
            return None
        decision = choose_decision(self._bot_observation(player))
        BotHelper.set_target(player, decision.quantity)
        return decision.action

    def _face_from_action(self, action_id: str | None) -> int | None:
        if not action_id or not action_id.startswith("bid_face_"):
            return None
        try:
            face = int(action_id.removeprefix("bid_face_"))
        except ValueError:
            return None
        return face if 1 <= face <= DIE_SIDES else None

    def _pending_bid_face(self, player: Player) -> int | None:
        return self._face_from_action(self._pending_actions.get(player.id))

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _host_locale(self) -> str:
        host_player = self.get_player_by_name(self.host) if self.host else None
        return self._player_locale(host_player) if host_player else "en"

    def _rules_label(self, locale: str) -> str:
        return Localization.get(
            locale,
            RULE_LABEL_KEYS.get(
                self.options.ruleset,
                "deadmansdice-rules-unsupported",
            ),
        )

    def _match_setup_key(self) -> str:
        return MATCH_SETUP_KEYS.get(
            self.options.ruleset,
            "deadmansdice-match-setup-unsupported",
        )

    def _speak_match_setup(self, user: User) -> None:
        user.speak_l(
            self._match_setup_key(),
            buffer="game",
            players=len(self.alive_players),
            rules=self._rules_label(user.locale),
        )

    def _table_rule_key(self) -> str:
        return TABLE_RULE_KEYS.get(
            self.options.ruleset,
            "deadmansdice-table-rule-unsupported",
        )

    def _face_label(
        self,
        locale: str,
        face: int,
        *,
        quantity: int | None = None,
    ) -> str:
        suffix = "-singular" if quantity == 1 else ""
        return Localization.get(locale, f"deadmansdice-face-{face}{suffix}")

    def _format_dice(self, dice: list[int], locale: str) -> str:
        return Localization.format_list(
            locale,
            [str(value) for value in sorted(dice)],
        )

    def _last_result_text(self, locale: str, viewer: Player) -> str:
        personal = viewer.id == self.last_reveal_result_player_id
        keys = LAST_RESULT_PERSONAL_KEYS if personal else LAST_RESULT_PUBLIC_KEYS
        return Localization.get(
            locale,
            keys.get(
                self.last_reveal_result,
                "deadmansdice-last-result-unavailable",
            ),
            player=self.last_reveal_result_player_name,
        )

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def build_game_result(self) -> GameResult:
        players = [
            player
            for player in self.get_active_players()
            if isinstance(player, DeadMansDicePlayer)
        ]
        ranked = sorted(
            players,
            key=lambda player: (
                player.id == self.winner_id,
                player.eliminated_round,
                -player.poison_doses,
                player.name,
            ),
            reverse=True,
        )
        score_by_id = {
            player.id: (
                self.round + 1
                if player.id == self.winner_id
                else player.eliminated_round
            )
            for player in players
        }
        rankings = [
            {
                "members": [player.name],
                "score": score_by_id[player.id],
                "is_individual": True,
            }
            for player in ranked
        ]
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[PlayerResult.from_player(player) for player in players],
            custom_data={
                "winner_name": next(
                    (player.name for player in players if player.id == self.winner_id),
                    None,
                ),
                "winner_ids": [self.winner_id] if self.winner_id else [],
                "rounds_played": self.round,
                "ruleset": self.options.ruleset,
                "team_rankings": rankings,
                RATING_COMPETITORS_KEY: rating_competitors_from_scores(
                    ([player.id], score_by_id[player.id]) for player in ranked
                ),
                "player_stats": {
                    player.id: {
                        "bids_made": player.bids_made,
                        "liar_calls": player.liar_calls,
                        "spot_on_calls": player.spot_on_calls,
                        "poison_doses": player.poison_doses,
                        "eliminated": player.eliminated,
                    }
                    for player in players
                },
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "deadmansdice-results-header")]
        winner_name = result.custom_data.get("winner_name")
        if winner_name:
            lines.append(
                Localization.get(
                    locale,
                    "deadmansdice-results-winner",
                    player=winner_name,
                )
            )
        stats = result.custom_data.get("player_stats", {})
        winner_ids = set(result.custom_data.get("winner_ids", []))
        for player in result.player_results:
            data = stats.get(player.player_id, {})
            status = Localization.get(
                locale,
                (
                    "deadmansdice-results-survived"
                    if player.player_id in winner_ids
                    else "deadmansdice-results-eliminated"
                ),
            )
            lines.append(
                Localization.get(
                    locale,
                    "deadmansdice-results-line",
                    player=player.player_name,
                    status=status,
                    bids=data.get("bids_made", 0),
                    challenges=data.get("liar_calls", 0),
                    spots=data.get("spot_on_calls", 0),
                    poison=data.get("poison_doses", 0),
                )
            )
        return lines
