"""Accessible implementation of the official base game Zombie Dice."""

from __future__ import annotations

import random
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import ClassVar

from ...audio import AudioSequenceSegment, Position, seat_position
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
from ...users.base import MenuItem, User
from ..base import Game, GameOptions, Player
from ..categories import CATEGORY_DICE
from ..registry import register_game
from . import audio as zombie_audio
from .bot import BotObservation, choose_action
from .rules import (
    BRAIN,
    COLORS,
    DICE_PER_ROLL,
    FOOTPRINT,
    MAX_TARGET_SCORE,
    MIN_TARGET_SCORE,
    OFFICIAL_TARGET_SCORE,
    SHOTGUN,
    SHOTGUNS_TO_BUST,
    DicePool,
    RollResult,
    draw_colors,
    has_complete_die_set,
    roll_colors,
)

BOT_THINK_TICKS = (36, 60)
ROLL_SEQUENCE_ID = "zombiedice_roll"
ROLL_SEQUENCE_TAG = "zombiedice_roll"
ROLL_AUDIO_PLAN_KEYS = frozenset(
    {"shake", "land", "shotguns", "flybys", "impacts", "casings", "bust"}
)


@dataclass
class ZombieDiceOptions(GameOptions):
    """The one meaningful base-game configuration: match length."""

    target_score: int = option_field(
        IntOption(
            default=OFFICIAL_TARGET_SCORE,
            min_val=MIN_TARGET_SCORE,
            max_val=MAX_TARGET_SCORE,
            value_key="score",
            label="zombiedice-set-target-score",
            prompt="zombiedice-enter-target-score",
            change_msg="zombiedice-option-changed-target-score",
            description="zombiedice-desc-target-score",
        )
    )


@dataclass
class ZombieDicePlayer(Player):
    """Persistent match statistics for one Zombie Dice seat."""

    turns_taken: int = 0
    rolls_made: int = 0
    brains_banked: int = 0
    busts: int = 0
    best_turn: int = 0


@dataclass
@register_game
class ZombieDiceGame(Game):
    """Push-your-luck dice play with exact colored-die state."""

    players: list[ZombieDicePlayer] = field(default_factory=list)
    options: ZombieDiceOptions = field(default_factory=ZombieDiceOptions)

    match_order_ids: list[str] = field(default_factory=list)
    tiebreaker_player_ids: list[str] = field(default_factory=list)
    final_round_active: bool = False
    final_round_trigger_id: str = ""
    tiebreak_round: int = 0
    winner_id: str = ""

    cup: DicePool = field(default_factory=DicePool.full)
    footprints: DicePool = field(default_factory=DicePool)
    brain_dice: DicePool = field(default_factory=DicePool)
    shotgun_dice: DicePool = field(default_factory=DicePool)
    turn_brains: int = 0
    last_roll: list[RollResult] = field(default_factory=list)
    has_rolled: bool = False
    next_ambient_event_tick: int = 0

    score_unit_key: ClassVar[str] = "zombiedice-score-unit-brains"
    touch_standard_order: ClassVar[list[str]] = [
        "check_turn_totals",
        "review_turn",
        "review_table",
        "check_scores",
        "whose_turn",
        "whos_at_table",
    ]

    @classmethod
    def get_name(cls) -> str:
        return "Zombie Dice"

    @classmethod
    def get_type(cls) -> str:
        return "zombiedice"

    @classmethod
    def get_category(cls) -> str:
        return CATEGORY_DICE

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "total_score", "high_score", "rating", "games_played"]

    def create_player(
        self,
        player_id: str,
        name: str,
        is_bot: bool = False,
    ) -> ZombieDicePlayer:
        return ZombieDicePlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = list(super().prestart_validate())
        if not MIN_TARGET_SCORE <= self.options.target_score <= MAX_TARGET_SCORE:
            errors.append(
                (
                    "zombiedice-error-target-score-range",
                    {
                        "value": self.options.target_score,
                        "min": MIN_TARGET_SCORE,
                        "max": MAX_TARGET_SCORE,
                    },
                )
            )
        return errors

    # ------------------------------------------------------------------
    # Spatial audio
    # ------------------------------------------------------------------

    def attach_user(
        self,
        player_id: str,
        user: User,
        *,
        session_handover: bool = False,
    ) -> None:
        """Replay or establish the listener's scene-fixed ambience."""

        super().attach_user(
            player_id,
            user,
            session_handover=session_handover,
        )
        player = self.get_player_by_id(player_id)
        if self.status == "playing" and player is not None and not player.is_bot:
            self._ensure_listener_ambience(player)

    def _table_seats(self) -> list[ZombieDicePlayer]:
        """Return stable physical seats; spectators listen from the centre."""

        return [
            player
            for player in self.players
            if isinstance(player, ZombieDicePlayer) and not player.is_spectator
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
        """Start each missing scene source in this listener's own frame."""

        user = self.get_user(listener)
        if user is None or listener.is_bot:
            return
        seats = self._table_seats()
        listener_index = self._seat_index(listener)
        for source in zombie_audio.AMBIENCE_SOURCES:
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
            position = zombie_audio.listener_relative_scene_position(
                source.world_position,
                listener_index,
                len(seats),
            )
            self.play_private_ambience(
                listener,
                source.asset,
                layer=source.layer,
                fade_in_ms=zombie_audio.AMBIENCE_FADE_IN_MS,
                fade_out_ms=zombie_audio.AMBIENCE_FADE_OUT_MS,
                priority=zombie_audio.AMBIENCE_PRIORITY,
                position=position,
                attenuation=zombie_audio.SCENE_ATTENUATION,
                gain=source.gain,
            )

    def _start_scene_ambience(self) -> None:
        for listener in self.players:
            if not listener.is_bot:
                self._ensure_listener_ambience(listener)

    def _play_seated_segments(
        self,
        emitter: ZombieDicePlayer,
        authored_segments: list[AudioSequenceSegment],
        *,
        priority: int,
        max_instances: int = zombie_audio.TABLE_EFFECT_MAX_INSTANCES,
    ) -> None:
        """Dispatch one atomic, listener-relative table sequence per person."""

        if not authored_segments:
            return
        for listener, position in self._seated_listener_positions(emitter):
            segments = [
                replace(
                    segment,
                    position=position,
                    attenuation=(
                        zombie_audio.TABLE_ATTENUATION if position is not None else None
                    ),
                )
                for segment in authored_segments
            ]
            self.play_sound_chain(
                segments,
                buffer="game",
                priority=priority,
                max_instances=max_instances,
                audience=listener,
            )

    def _seated_listener_positions(
        self,
        emitter: ZombieDicePlayer,
    ) -> list[tuple[Player, Position | None]]:
        """Return each connected listener and the emitter in their frame."""

        seats = self._table_seats()
        seat_indexes = {player.id: index for index, player in enumerate(seats)}
        emitter_index = seat_indexes.get(emitter.id)
        listeners: list[tuple[Player, Position | None]] = []
        for listener in self.players:
            if listener.is_bot or self.get_user(listener) is None:
                continue
            listener_index = seat_indexes.get(listener.id)
            position = (
                seat_position(emitter_index, listener_index, len(seats))
                if emitter_index is not None
                else None
            )
            listeners.append((listener, position))
        return listeners

    def _select_roll_audio_plan(
        self,
        results: list[RollResult],
        *,
        busted: bool,
    ) -> dict:
        """Choose every variation before starting the serialized roll."""

        shake_bank, land_bank = zombie_audio.roll_sound_bank(len(results))
        shotgun_count = sum(result.face == SHOTGUN for result in results)
        return {
            "shake": random.choice(shake_bank),  # nosec B311
            "land": random.choice(land_bank),  # nosec B311
            "shotguns": random.sample(  # nosec B311
                zombie_audio.SOUND_SHOTGUNS,
                k=shotgun_count,
            ),
            "flybys": random.sample(  # nosec B311
                zombie_audio.SOUND_SHOT_FLYBYS,
                k=shotgun_count,
            ),
            "impacts": random.sample(  # nosec B311
                zombie_audio.SOUND_SHOT_IMPACTS,
                k=shotgun_count,
            ),
            "casings": random.sample(  # nosec B311
                zombie_audio.SOUND_SHELL_CASINGS,
                k=shotgun_count,
            ),
            "bust": (
                random.choice(zombie_audio.SOUND_BUSTS)  # nosec B311
                if busted
                else ""
            ),
        }

    @staticmethod
    def _validated_audio_assets(
        value: object,
        allowed: tuple[str, ...],
        count: int,
    ) -> list[str] | None:
        if not isinstance(value, list) or len(value) != count:
            return None
        if any(not isinstance(asset, str) for asset in value):
            return None
        assets = list(value)
        if any(asset not in allowed for asset in assets) or len(set(assets)) != count:
            return None
        return assets

    def _build_roll_audio_segments(
        self,
        plan: object,
        *,
        recycled: int,
        shotgun_count: int,
        busted: bool,
    ) -> list[AudioSequenceSegment] | None:
        """Validate a saved variation plan and build its atomic sound chain."""

        if not isinstance(plan, dict) or set(plan) != ROLL_AUDIO_PLAN_KEYS:
            return None
        shake = plan.get("shake")
        land = plan.get("land")
        shake_bank, land_bank = zombie_audio.roll_sound_bank(DICE_PER_ROLL)
        if (
            not isinstance(shake, str)
            or not isinstance(land, str)
            or shake not in shake_bank
            or land not in land_bank
        ):
            return None
        shotguns = self._validated_audio_assets(
            plan.get("shotguns"),
            zombie_audio.SOUND_SHOTGUNS,
            shotgun_count,
        )
        flybys = self._validated_audio_assets(
            plan.get("flybys"),
            zombie_audio.SOUND_SHOT_FLYBYS,
            shotgun_count,
        )
        impacts = self._validated_audio_assets(
            plan.get("impacts"),
            zombie_audio.SOUND_SHOT_IMPACTS,
            shotgun_count,
        )
        casings = self._validated_audio_assets(
            plan.get("casings"),
            zombie_audio.SOUND_SHELL_CASINGS,
            shotgun_count,
        )
        if any(assets is None for assets in (shotguns, flybys, impacts, casings)):
            return None
        bust_asset = plan.get("bust")
        if not isinstance(bust_asset, str):
            return None
        if (busted and bust_asset not in zombie_audio.SOUND_BUSTS) or (
            not busted and bust_asset != ""
        ):
            return None

        segments: list[AudioSequenceSegment] = []
        if recycled:
            segments.append(
                AudioSequenceSegment(
                    asset=zombie_audio.SOUND_CUP_REFILL,
                    gain=zombie_audio.CUP_REFILL_GAIN,
                    next_start_ratio=zombie_audio.CUP_REFILL_NEXT_RATIO,
                )
            )
        segments.extend(
            (
                AudioSequenceSegment(
                    asset=shake,
                    gain=zombie_audio.ROLL_SHAKE_GAIN,
                    next_start_ratio=zombie_audio.ROLL_SHAKE_NEXT_RATIO,
                ),
                AudioSequenceSegment(
                    asset=land,
                    gain=zombie_audio.ROLL_LAND_GAIN,
                    next_start_ratio=zombie_audio.ROLL_LAND_NEXT_RATIO,
                ),
            )
        )
        assert shotguns is not None
        assert flybys is not None
        assert impacts is not None
        assert casings is not None
        burst = shotgun_count >= zombie_audio.BULLET_BURST_MIN_SHOTGUNS
        ballistic_events: list[tuple[int, AudioSequenceSegment]] = []
        for index, (shotgun, flyby, impact, casing) in enumerate(
            zip(shotguns, flybys, impacts, casings, strict=True)
        ):
            last_shot = index == shotgun_count - 1
            report_onset_ms = (
                index * zombie_audio.BULLET_BURST_INTERVAL_MS if burst else 0
            )
            impact_onset_ms = report_onset_ms + round(
                zombie_audio.sound_milliseconds(flyby)
                * zombie_audio.FLYBY_TO_IMPACT_RATIO
            )
            ballistic_events.extend(
                [
                    (
                        report_onset_ms,
                        AudioSequenceSegment(
                            asset=shotgun,
                            gain=zombie_audio.SHOTGUN_GAIN,
                        ),
                    ),
                    (
                        report_onset_ms,
                        AudioSequenceSegment(
                            asset=flyby,
                            gain=zombie_audio.SHOT_FLYBY_GAIN,
                        ),
                    ),
                    (
                        impact_onset_ms,
                        AudioSequenceSegment(
                            asset=impact,
                            gain=zombie_audio.SHOT_IMPACT_GAIN,
                        ),
                    ),
                    (
                        impact_onset_ms,
                        AudioSequenceSegment(
                            asset=casing,
                            gain=zombie_audio.SHELL_CASING_GAIN,
                        ),
                    ),
                ]
            )
            if busted and last_shot:
                ballistic_events.append(
                    (
                        impact_onset_ms,
                        AudioSequenceSegment(
                            asset=bust_asset,
                            gain=zombie_audio.BUST_GAIN,
                        ),
                    )
                )
        scheduled_ballistics = self._schedule_audio_events(ballistic_events)
        if scheduled_ballistics is None:
            return None
        segments.extend(scheduled_ballistics)
        return segments

    @staticmethod
    def _schedule_audio_events(
        events: list[tuple[int, AudioSequenceSegment]],
    ) -> list[AudioSequenceSegment] | None:
        """Convert absolute onsets into one atomic client-clocked chain."""

        ordered = sorted(
            enumerate(events),
            key=lambda indexed: (indexed[1][0], indexed[0]),
        )
        scheduled: list[AudioSequenceSegment] = []
        for position, (_event_index, (onset_ms, segment)) in enumerate(ordered):
            if onset_ms < 0:
                return None
            next_start_ratio = 1.0
            if position + 1 < len(ordered):
                next_onset_ms = ordered[position + 1][1][0]
                duration_ms = zombie_audio.sound_milliseconds(segment.asset)
                delay_ms = next_onset_ms - onset_ms
                if duration_ms <= 0 or delay_ms < 0 or delay_ms > duration_ms:
                    return None
                next_start_ratio = delay_ms / duration_ms
            scheduled.append(replace(segment, next_start_ratio=next_start_ratio))
        return scheduled

    def _play_roll_audio(
        self,
        player: ZombieDicePlayer,
        authored_segments: list[AudioSequenceSegment],
    ) -> None:
        """Dispatch a centre-to-victim ballistic chain in every listener frame."""

        seats = self._table_seats()
        seat_indexes = {seated.id: index for index, seated in enumerate(seats)}
        target_index = seat_indexes.get(player.id)
        if target_index is None:
            return
        target_world_position = zombie_audio.table_seat_world_position(
            target_index,
            len(seats),
        )
        for listener in self.players:
            if listener.is_bot or self.get_user(listener) is None:
                continue
            listener_index = seat_indexes.get(listener.id)
            centre_position = zombie_audio.listener_relative_scene_position(
                (0.0, 0.0, 0.0),
                listener_index,
                len(seats),
            )
            ballistic_target_position = zombie_audio.listener_relative_scene_position(
                target_world_position,
                listener_index,
                len(seats),
            )
            seated_target_position = seat_position(
                target_index,
                listener_index,
                len(seats),
            )
            segments: list[AudioSequenceSegment] = []
            for segment in authored_segments:
                destination_position = None
                if segment.asset in zombie_audio.SOUND_SHOTGUNS:
                    position = centre_position
                elif segment.asset in zombie_audio.SOUND_SHOT_FLYBYS:
                    position = centre_position
                    destination_position = ballistic_target_position
                elif segment.asset in zombie_audio.SOUND_SHOT_IMPACTS:
                    position = ballistic_target_position
                elif segment.asset in zombie_audio.SOUND_SHELL_CASINGS:
                    position = centre_position
                elif segment.asset in zombie_audio.SOUND_BUSTS:
                    position = (
                        None if listener.id == player.id else ballistic_target_position
                    )
                else:
                    position = seated_target_position
                segments.append(
                    replace(
                        segment,
                        position=position,
                        destination_position=destination_position,
                        attenuation=(
                            zombie_audio.TABLE_ATTENUATION
                            if position is not None
                            else None
                        ),
                    )
                )
            self.play_sound_chain(
                segments,
                buffer="game",
                priority=zombie_audio.ROLL_PRIORITY,
                max_instances=zombie_audio.TABLE_EFFECT_MAX_INSTANCES,
                audience=listener,
            )

    def _play_bank_audio(self, player: ZombieDicePlayer, brains: int) -> None:
        if brains <= 0:
            return
        self._play_seated_segments(
            player,
            [
                AudioSequenceSegment(
                    asset=zombie_audio.SOUND_BANK_BITE,
                    gain=zombie_audio.BANK_BITE_GAIN,
                    next_start_ratio=zombie_audio.BANK_BITE_NEXT_RATIO,
                ),
                AudioSequenceSegment(
                    asset=random.choice(zombie_audio.SOUND_BANK_GROWLS),  # nosec B311
                    gain=zombie_audio.BANK_GROWL_GAIN,
                ),
            ],
            priority=zombie_audio.BANK_PRIORITY,
        )

    def _play_final_cue(self, *, repeats: int = 1) -> None:
        self.play_sound_chain(
            [
                AudioSequenceSegment(
                    asset=zombie_audio.SOUND_FINAL_HEARTBEAT,
                    gain=zombie_audio.FINAL_HEARTBEAT_GAIN,
                    next_start_ratio=(
                        zombie_audio.FINAL_HEARTBEAT_NEXT_RATIO
                        if index < repeats - 1
                        else 1.0
                    ),
                )
                for index in range(repeats)
            ],
            buffer="game",
            priority=zombie_audio.FINAL_PRIORITY,
            max_instances=1,
        )

    def _play_winner_audio(self, winner: ZombieDicePlayer) -> None:
        for listener, position in self._seated_listener_positions(winner):
            user = self.get_user(listener)
            if user is None:
                continue
            user.play_sound_family(
                zombie_audio.SOUND_WIN_ROAR_FAMILY,
                buffer="game",
                priority=zombie_audio.WIN_PRIORITY,
                max_instances=1,
                position=position,
                attenuation=(
                    zombie_audio.TABLE_ATTENUATION if position is not None else None
                ),
                gain=zombie_audio.WIN_ROAR_GAIN,
            )

    def _schedule_next_ambient_event(self, *, initial: bool = False) -> None:
        delay_range = (
            zombie_audio.WANDER_INITIAL_DELAY_TICKS
            if initial
            else zombie_audio.WANDER_INTERVAL_TICKS
        )
        self.next_ambient_event_tick = self.sound_scheduler_tick + random.randint(  # nosec B311
            *delay_range
        )

    def _play_wandering_zombie(self) -> None:
        """Play a finite zombie pass-by independently in each listener frame."""

        origin, destination = random.choice(  # nosec B311
            zombie_audio.WANDER_WORLD_ROUTES
        )
        step_assets = random.sample(  # nosec B311
            zombie_audio.SOUND_WANDER_STEPS,
            k=zombie_audio.WANDER_STEP_COUNT,
        )
        growl_asset = random.choice(zombie_audio.SOUND_WANDER_GROWLS)  # nosec B311
        step_durations = [
            max(1, zombie_audio.sound_ticks(asset)) for asset in step_assets
        ]
        total_step_duration = sum(step_durations)
        elapsed_step_duration = 0
        step_world_points = [origin]
        for duration in step_durations:
            elapsed_step_duration += duration
            step_world_points.append(
                zombie_audio.interpolate_world_position(
                    origin,
                    destination,
                    zombie_audio.WANDER_STEP_ROUTE_FRACTION
                    * elapsed_step_duration
                    / total_step_duration,
                )
            )
        world_points = [*step_world_points, destination]

        seats = self._table_seats()
        for listener in self.players:
            if listener.is_bot or self.get_user(listener) is None:
                continue
            listener_index = self._seat_index(listener)
            local_points = [
                zombie_audio.listener_relative_scene_position(
                    point,
                    listener_index,
                    len(seats),
                )
                for point in world_points
            ]
            segments = [
                AudioSequenceSegment(
                    asset=asset,
                    position=local_points[index],
                    destination_position=local_points[index + 1],
                    attenuation=zombie_audio.SCENE_ATTENUATION,
                    gain=zombie_audio.WANDER_STEP_GAIN,
                    next_start_ratio=zombie_audio.WANDER_STEP_NEXT_RATIO,
                )
                for index, asset in enumerate(step_assets)
            ]
            segments.append(
                AudioSequenceSegment(
                    asset=growl_asset,
                    position=local_points[-2],
                    destination_position=local_points[-1],
                    attenuation=zombie_audio.SCENE_ATTENUATION,
                    gain=zombie_audio.WANDER_GROWL_GAIN,
                    easing="ease-in-out",
                )
            )
            self.play_sound_chain(
                segments,
                buffer="game",
                priority=zombie_audio.WANDER_PRIORITY,
                max_instances=1,
                audience=listener,
            )

    def _maybe_play_ambient_event(self) -> None:
        if (
            self.status != "playing"
            or self.sound_scheduler_tick < self.next_ambient_event_tick
        ):
            return
        if self.active_sequences:
            self.next_ambient_event_tick = (
                self.sound_scheduler_tick + zombie_audio.WANDER_DEFER_TICKS
            )
            return
        self._play_wandering_zombie()
        self._schedule_next_ambient_event()

    # ------------------------------------------------------------------
    # Action sets and focus-stable labels
    # ------------------------------------------------------------------

    def create_turn_action_set(self, player: ZombieDicePlayer) -> ActionSet:
        locale = self._player_locale(player)
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "zombiedice-roll-first"),
                description=Localization.get(
                    locale,
                    "zombiedice-roll-first-description",
                ),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_turn_action_hidden",
                get_label="_get_roll_label",
                get_description="_get_roll_description",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="bank",
                label=Localization.get(
                    locale,
                    "zombiedice-bank",
                    brains=0,
                ),
                description=Localization.get(
                    locale,
                    "zombiedice-bank-description",
                    brains=0,
                ),
                handler="_action_bank",
                is_enabled="_is_bank_enabled",
                is_hidden="_is_bank_hidden",
                get_label="_get_bank_label",
                get_description="_get_bank_description",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        action_set.add(
            Action(
                id="check_turn_totals",
                label=Localization.get(locale, "zombiedice-check-turn-totals"),
                description=Localization.get(
                    locale,
                    "zombiedice-check-turn-totals-description",
                ),
                handler="_action_check_turn_totals",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="review_turn",
                label=Localization.get(locale, "zombiedice-review-turn"),
                description=Localization.get(
                    locale,
                    "zombiedice-review-turn-description",
                ),
                handler="_action_review_turn",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="review_table",
                label=Localization.get(locale, "zombiedice-review-table"),
                description=Localization.get(
                    locale,
                    "zombiedice-review-table-description",
                ),
                handler="_action_review_table",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_public_info_hidden",
                include_spectators=True,
            )
        )
        if self.is_touch_client(self.get_user(player)):
            self._order_touch_standard_actions(action_set, self.touch_standard_order)
        return action_set

    def before_menu_build(self, player: Player) -> None:
        """Rebuild device-specific standard ordering after live handover."""

        if self.get_action_set(player, "standard") is None:
            return
        self.remove_action_set(player, "standard")
        self.add_action_set(player, self.create_standard_action_set(player))

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        locale = self._host_locale()
        for key, label_key, action_id, spectators in (
            ("r", "zombiedice-roll-first", "roll", False),
            ("b", "zombiedice-bank-keybind", "bank", False),
            (
                "c",
                "zombiedice-check-turn-totals",
                "check_turn_totals",
                True,
            ),
            ("v", "zombiedice-review-turn", "review_turn", True),
            ("shift+v", "zombiedice-review-table", "review_table", True),
        ):
            self.define_keybind(
                key,
                Localization.get(locale, label_key),
                [action_id],
                state=KeybindState.ACTIVE,
                include_spectators=spectators,
            )

    def _turn_action_disabled_reason(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if not isinstance(player, ZombieDicePlayer):
            return "action-not-available"
        if self.current_player is not player:
            return "action-not-your-turn"
        if self.is_sequence_gameplay_locked():
            return "zombiedice-error-roll-resolving"
        return None

    def _is_roll_enabled(self, player: Player) -> str | None:
        return self._turn_action_disabled_reason(player)

    def _is_bank_enabled(self, player: Player) -> str | None:
        reason = self._turn_action_disabled_reason(player)
        if reason:
            return reason
        if not self.has_rolled:
            return "zombiedice-error-roll-before-stopping"
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_bank_hidden(self, player: Player) -> Visibility:
        if self._is_turn_action_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN
        if self.current_player is not player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE if self.has_rolled else Visibility.HIDDEN

    def _get_roll_label(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        if self.current_player is not player or not self.has_rolled:
            return Localization.get(locale, "zombiedice-roll-first")
        return Localization.get(
            locale,
            "zombiedice-roll-again",
            brains=self.turn_brains,
        )

    def _get_roll_description(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        if self.current_player is not player or not self.has_rolled:
            return Localization.get(locale, "zombiedice-roll-first-description")
        return Localization.get(
            locale,
            "zombiedice-roll-again-description",
            footprints=self.footprints.total,
            draw=DICE_PER_ROLL - self.footprints.total,
            brains=self.turn_brains,
        )

    def _get_bank_label(self, player: Player, action_id: str) -> str:
        return Localization.get(
            self._player_locale(player),
            "zombiedice-bank",
            brains=self.turn_brains,
        )

    def _get_bank_description(self, player: Player, action_id: str) -> str:
        return Localization.get(
            self._player_locale(player),
            "zombiedice-bank-description",
            brains=self.turn_brains,
        )

    def _is_public_info_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "action-not-playing"

    def _is_public_info_hidden(self, player: Player) -> Visibility:
        if self.status == "playing" and self.is_touch_client(self.get_user(player)):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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

    # ------------------------------------------------------------------
    # Match and turn lifecycle
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 1
        self.final_round_active = False
        self.final_round_trigger_id = ""
        self.tiebreaker_player_ids.clear()
        self.tiebreak_round = 0
        self.winner_id = ""
        self.next_ambient_event_tick = 0
        self.clear_scheduled_sounds()
        self.cancel_all_sequences()

        active_players = [
            player
            for player in self.get_active_players()
            if isinstance(player, ZombieDicePlayer)
        ]
        random.shuffle(active_players)  # nosec B311 - gameplay randomness
        self.match_order_ids = [player.id for player in active_players]
        self.set_turn_players(active_players)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([player.name for player in active_players])
        for player in active_players:
            player.turns_taken = 0
            player.rolls_made = 0
            player.brains_banked = 0
            player.busts = 0
            player.best_turn = 0
            BotHelper.set_target(player, None)

        self._start_scene_ambience()
        self.play_music(
            zombie_audio.SOUND_MUSIC,
            fade_in_ms=zombie_audio.MUSIC_FADE_IN_MS,
            fade_out_ms=zombie_audio.MUSIC_FADE_OUT_MS,
            priority=zombie_audio.MUSIC_PRIORITY,
            gain=zombie_audio.MUSIC_GAIN,
        )
        self._schedule_next_ambient_event(initial=True)

        order = lambda locale: Localization.format_list_and(
            locale,
            [player.name for player in active_players],
        )
        first = active_players[0] if active_players else None
        self.broadcast_l(
            "zombiedice-game-start",
            buffer="game",
            target=self.options.target_score,
            order=order,
            first=first or "",
        )
        self._start_turn()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        self._maybe_play_ambient_event()
        if self.status == "playing" and not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, ZombieDicePlayer):
            self.refresh_menus()
            return

        self.cup = DicePool.full()
        self.footprints = DicePool()
        self.brain_dice = DicePool()
        self.shotgun_dice = DicePool()
        self.turn_brains = 0
        self.last_roll.clear()
        self.has_rolled = False
        player.turns_taken += 1

        user = self.get_user(player)
        if user and user.preferences.play_turn_sound:
            user.play_sound("turn.ogg")
        self.broadcast_personal_l(
            player,
            "zombiedice-your-turn",
            "zombiedice-player-turn",
            buffer="game",
            score=self.get_player_score(player),
        )
        if player.is_bot:
            self._jolt_bot(player)
        self.refresh_menus()

    def _complete_turn(self) -> None:
        if not self.turn_player_ids:
            self.refresh_menus()
            return
        if self.turn_index >= len(self.turn_player_ids) - 1:
            self._finish_round()
            return
        self.advance_turn(announce=False)
        self._start_turn()

    def _finish_round(self) -> None:
        if self.tiebreaker_player_ids:
            leaders = self._highest_scoring_players(self._round_players())
            if len(leaders) == 1:
                self._finish_with_winner(leaders[0])
                return
            self.tiebreaker_player_ids = [player.id for player in leaders]
            self.tiebreak_round += 1
            self._announce_tiebreak(leaders)
            self._begin_round(leaders)
            return

        if self.final_round_active:
            leaders = self._highest_scoring_players(self._ordered_active_players())
            if len(leaders) == 1:
                self._finish_with_winner(leaders[0])
                return
            self.final_round_active = False
            self.final_round_trigger_id = ""
            self.tiebreaker_player_ids = [player.id for player in leaders]
            self.tiebreak_round = 1
            self._announce_tiebreak(leaders)
            self._begin_round(leaders)
            return

        self.round += 1
        self._begin_round(self._ordered_active_players())

    def _begin_round(self, players: list[ZombieDicePlayer]) -> None:
        if not players:
            self.set_turn_players([])
            self.refresh_menus()
            return
        if len(players) == 1 and self.tiebreaker_player_ids:
            self._finish_with_winner(players[0])
            return
        self.set_turn_players(players)
        self._start_turn()

    def _ordered_active_players(self) -> list[ZombieDicePlayer]:
        active = {
            player.id: player
            for player in self.get_active_players()
            if isinstance(player, ZombieDicePlayer)
        }
        ordered = [
            active[player_id]
            for player_id in self.match_order_ids
            if player_id in active
        ]
        ordered.extend(player for player in active.values() if player not in ordered)
        return ordered

    def _round_players(self) -> list[ZombieDicePlayer]:
        if not self.tiebreaker_player_ids:
            return self._ordered_active_players()
        finalists = set(self.tiebreaker_player_ids)
        return [
            player
            for player in self._ordered_active_players()
            if player.id in finalists
        ]

    def _highest_scoring_players(
        self,
        players: list[ZombieDicePlayer],
    ) -> list[ZombieDicePlayer]:
        if not players:
            return []
        high_score = max(self.get_player_score(player) for player in players)
        return [
            player for player in players if self.get_player_score(player) == high_score
        ]

    def _announce_tiebreak(self, leaders: list[ZombieDicePlayer]) -> None:
        players = lambda locale: Localization.format_list_and(
            locale,
            [player.name for player in leaders],
        )
        self._play_final_cue(repeats=2)
        self.broadcast_l(
            "zombiedice-tiebreak-start",
            buffer="game",
            players=players,
            round=self.tiebreak_round,
            score=self.get_player_score(leaders[0]) if leaders else 0,
        )

    def _finish_with_winner(self, winner: ZombieDicePlayer) -> None:
        self.winner_id = winner.id
        self.final_round_active = False
        self.final_round_trigger_id = ""
        self.tiebreaker_player_ids.clear()
        self._play_winner_audio(winner)
        self.broadcast_personal_l(
            winner,
            "zombiedice-you-win",
            "zombiedice-player-wins",
            buffer="game",
            score=self.get_player_score(winner),
        )
        self.finish_game()

    # ------------------------------------------------------------------
    # Dice actions
    # ------------------------------------------------------------------

    def _action_roll(self, player: Player, action_id: str) -> None:
        if (
            not isinstance(player, ZombieDicePlayer)
            or player is not self.current_player
            or self.has_active_sequence(tag=ROLL_SEQUENCE_TAG)
        ):
            return

        draw_count = DICE_PER_ROLL - self.footprints.total
        working_cup = self.cup.copy()
        recycled = 0
        if working_cup.total < DICE_PER_ROLL:
            recycled = self.brain_dice.total
            working_cup.add_pool(self.brain_dice)

        colors = self.footprints.colors()
        colors.extend(draw_colors(working_cup, draw_count))
        random.shuffle(colors)  # nosec B311 - presentation-neutral roll order
        results = roll_colors(colors)
        busted = (
            self.shotgun_dice.total + sum(result.face == SHOTGUN for result in results)
            >= SHOTGUNS_TO_BUST
        )
        audio_plan = self._select_roll_audio_plan(results, busted=busted)
        segments = self._build_roll_audio_segments(
            audio_plan,
            recycled=recycled,
            shotgun_count=sum(result.face == SHOTGUN for result in results),
            busted=busted,
        )
        if segments is None:
            return
        payload = {
            "player_id": player.id,
            "results": [
                {"color": result.color, "face": result.face} for result in results
            ],
            "cup_after_draw": {color: working_cup.count(color) for color in COLORS},
            "recycled": recycled,
            "busted": busted,
            "audio_plan": audio_plan,
        }
        result_delay_ticks = zombie_audio.roll_result_delay_ticks(
            [(segment.asset, segment.next_start_ratio) for segment in segments]
        )
        self.start_sequence(
            ROLL_SEQUENCE_ID,
            [
                SequenceBeat.after_audio(
                    result_delay_ticks,
                    ops=[
                        SequenceOperation.callback_op(
                            "play_roll_audio",
                            payload,
                        )
                    ],
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("resolve_roll", payload)]
                ),
            ],
            tag=ROLL_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            replace_existing=False,
        )
        self.refresh_menus(player)

    @staticmethod
    def _pool_from_roll_payload(value: object) -> DicePool | None:
        if not isinstance(value, dict) or set(value) != set(COLORS):
            return None
        if any(type(value[color]) is not int for color in COLORS):
            return None
        try:
            return DicePool(**{color: value[color] for color in COLORS})
        except (TypeError, ValueError):
            return None

    def _validated_roll_payload(
        self,
        payload: dict,
    ) -> (
        tuple[
            ZombieDicePlayer,
            list[RollResult],
            DicePool,
            int,
            bool,
            list[AudioSequenceSegment],
        ]
        | None
    ):
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if (
            not isinstance(player, ZombieDicePlayer)
            or player is not self.current_player
            or player not in self.get_active_players()
            or self.status != "playing"
            or not self._turn_dice_are_complete()
        ):
            return None

        raw_results = payload.get("results")
        if not isinstance(raw_results, list) or len(raw_results) != DICE_PER_ROLL:
            return None
        try:
            results = [
                RollResult(
                    color=str(result["color"]),
                    face=str(result["face"]),
                )
                for result in raw_results
                if isinstance(result, dict) and set(result) == {"color", "face"}
            ]
        except (KeyError, TypeError, ValueError):
            return None
        if len(results) != DICE_PER_ROLL:
            return None

        cup_after_draw = self._pool_from_roll_payload(payload.get("cup_after_draw"))
        recycled = payload.get("recycled")
        busted = payload.get("busted")
        if (
            cup_after_draw is None
            or type(recycled) is not int
            or recycled < 0
            or type(busted) is not bool
        ):
            return None

        expected_cup = self.cup.copy()
        expected_recycled = 0
        if expected_cup.total < DICE_PER_ROLL:
            expected_recycled = self.brain_dice.total
            expected_cup.add_pool(self.brain_dice)
        if recycled != expected_recycled:
            return None

        rolled_colors = DicePool()
        for result in results:
            rolled_colors.add(result.color)
        try:
            for color in self.footprints.colors():
                rolled_colors.remove(color)
            for color in rolled_colors.colors():
                expected_cup.remove(color)
        except ValueError:
            return None
        if (
            rolled_colors.total != DICE_PER_ROLL - self.footprints.total
            or expected_cup != cup_after_draw
        ):
            return None

        shotgun_count = sum(result.face == SHOTGUN for result in results)
        if busted != (self.shotgun_dice.total + shotgun_count >= SHOTGUNS_TO_BUST):
            return None
        segments = self._build_roll_audio_segments(
            payload.get("audio_plan"),
            recycled=recycled,
            shotgun_count=shotgun_count,
            busted=busted,
        )
        if segments is None:
            return None
        return player, results, cup_after_draw, recycled, busted, segments

    def _resolve_roll(self, payload: dict) -> None:
        validated = self._validated_roll_payload(payload)
        if validated is None:
            return
        player, results, cup_after_draw, recycled, busted, _segments = validated

        if recycled:
            self.broadcast_personal_l(
                player,
                "zombiedice-you-refill-cup",
                "zombiedice-player-refills-cup",
                buffer="game",
                count=recycled,
                brains=self.turn_brains,
            )
            self.brain_dice.clear()
        self.cup = cup_after_draw
        self.footprints.clear()
        self.last_roll = results
        self.has_rolled = True
        player.rolls_made += 1

        for result in results:
            if result.face == BRAIN:
                self.turn_brains += 1
                self.brain_dice.add(result.color)
            elif result.face == FOOTPRINT:
                self.footprints.add(result.color)
            else:
                self.shotgun_dice.add(result.color)

        if not self._turn_dice_are_complete():
            raise RuntimeError("Zombie Dice color conservation failed after a roll")

        result_text = lambda locale: self._format_roll(results, locale)
        if busted:
            lost = self.turn_brains
            player.busts += 1
            self.broadcast_personal_l(
                player,
                "zombiedice-you-bust",
                "zombiedice-player-busts",
                buffer="game",
                results=result_text,
                shotguns=self.shotgun_dice.total,
                brains=lost,
            )
            self._complete_turn()
            return

        self.broadcast_personal_l(
            player,
            "zombiedice-you-roll",
            "zombiedice-player-rolls",
            buffer="game",
            results=result_text,
        )
        if player.is_bot:
            self._jolt_bot(player)
        self.refresh_menus()

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        if sequence_id != ROLL_SEQUENCE_ID:
            super().on_sequence_callback(sequence_id, callback_id, payload)
            return
        validated = self._validated_roll_payload(payload)
        if validated is None:
            return
        player, _results, _cup, _recycled, _busted, segments = validated
        if callback_id == "play_roll_audio":
            self._play_roll_audio(player, segments)
        elif callback_id == "resolve_roll":
            self._resolve_roll(payload)

    def _action_bank(self, player: Player, action_id: str) -> None:
        if (
            not isinstance(player, ZombieDicePlayer)
            or self.is_sequence_gameplay_locked()
        ):
            return

        banked = self.turn_brains
        self._team_manager.add_to_team_score(player.name, banked)
        total = self.get_player_score(player)
        player.brains_banked += banked
        player.best_turn = max(player.best_turn, banked)
        self._play_bank_audio(player, banked)
        self.broadcast_personal_l(
            player,
            "zombiedice-you-bank",
            "zombiedice-player-banks",
            buffer="game",
            brains=banked,
            total=total,
        )

        if (
            not self.final_round_active
            and not self.tiebreaker_player_ids
            and total >= self.options.target_score
        ):
            self.final_round_active = True
            self.final_round_trigger_id = player.id
            remaining = len(self.turn_player_ids) - self.turn_index - 1
            if remaining:
                self._play_final_cue()
                self.broadcast_personal_l(
                    player,
                    "zombiedice-you-trigger-final-round",
                    "zombiedice-player-triggers-final-round",
                    buffer="game",
                    score=total,
                    remaining=remaining,
                )

        user = self.get_user(player)
        if self.is_touch_client(user):
            self.request_menu_focus(player, "roll")

        self._complete_turn()

    def get_player_score(self, player: ZombieDicePlayer) -> int:
        team = self._team_manager.get_team(player.name)
        return team.total_score if team else 0

    def _turn_dice_are_complete(self) -> bool:
        return has_complete_die_set(
            self.cup,
            self.footprints,
            self.brain_dice,
            self.shotgun_dice,
        )

    # ------------------------------------------------------------------
    # Public status views
    # ------------------------------------------------------------------

    def _action_check_turn_totals(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user is None:
            return
        current = self.current_player
        if not isinstance(current, ZombieDicePlayer):
            user.speak_l("zombiedice-status-no-turn", buffer="game")
            return
        totals = {
            "brains": self.turn_brains,
            "shotguns": self.shotgun_dice.total,
            "footprints": self.footprints.total,
        }
        if current.id == player.id:
            user.speak_l("zombiedice-your-turn-totals", buffer="game", **totals)
        else:
            user.speak_l(
                "zombiedice-player-turn-totals",
                buffer="game",
                player=current.name,
                **totals,
            )

    def _action_review_turn(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "zombiedice_turn",
            self._build_turn_status,
            focus_id="turn_header",
        )

    def _action_review_table(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "zombiedice_table",
            self._build_table_status,
            focus_id="table_header",
        )

    def _build_turn_status(self, viewer: Player, user) -> list[MenuItem]:
        locale = user.locale
        current = self.current_player
        if not isinstance(current, ZombieDicePlayer):
            return [
                MenuItem(
                    text=Localization.get(locale, "zombiedice-status-no-turn"),
                    id="turn_header",
                )
            ]

        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "zombiedice-status-turn-you"
                    if current.id == viewer.id
                    else "zombiedice-status-turn-player",
                    player=current.name,
                    score=self.get_player_score(current),
                ),
                id="turn_header",
            ),
            MenuItem(
                text=Localization.get(
                    locale,
                    "zombiedice-status-turn-totals",
                    brains=self.turn_brains,
                    shotguns=self.shotgun_dice.total,
                    footprints=self.footprints.total,
                ),
                id="turn_totals",
            ),
            MenuItem(
                text=Localization.get(
                    locale,
                    "zombiedice-status-cup",
                    count=self.cup.total,
                ),
                id="cup",
            ),
            MenuItem(
                text=Localization.get(
                    locale,
                    "zombiedice-status-footprints",
                    dice=self._format_pool(self.footprints, locale),
                ),
                id="footprints",
            ),
            MenuItem(
                text=Localization.get(
                    locale,
                    "zombiedice-status-brain-dice",
                    dice=self._format_pool(self.brain_dice, locale),
                ),
                id="brain_dice",
            ),
            MenuItem(
                text=Localization.get(
                    locale,
                    "zombiedice-status-shotgun-dice",
                    dice=self._format_pool(self.shotgun_dice, locale),
                ),
                id="shotgun_dice",
            ),
        ]
        if self.last_roll:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "zombiedice-status-last-roll",
                        results=self._format_roll(self.last_roll, locale),
                    ),
                    id="last_roll",
                )
            )
        else:
            items.append(
                MenuItem(
                    text=Localization.get(locale, "zombiedice-status-awaiting-roll"),
                    id="last_roll",
                )
            )
        return items

    def _build_table_status(self, viewer: Player, user) -> list[MenuItem]:
        locale = user.locale
        in_tiebreak = bool(self.tiebreaker_player_ids)
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    (
                        "zombiedice-status-table-header-tiebreak"
                        if in_tiebreak
                        else "zombiedice-status-table-header"
                    ),
                    target=self.options.target_score,
                    round=self.round,
                ),
                id="table_header",
            )
        ]
        if self.tiebreaker_player_ids:
            finalists = self._round_players()
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "zombiedice-status-tiebreak",
                        round=self.tiebreak_round,
                        players=Localization.format_list_and(
                            locale,
                            [player.name for player in finalists],
                        ),
                    ),
                    id="phase",
                )
            )
        elif self.final_round_active:
            trigger = self.get_player_by_id(self.final_round_trigger_id)
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "zombiedice-status-final-round",
                        player=trigger.name if trigger else "",
                    ),
                    id="phase",
                )
            )
        else:
            items.append(
                MenuItem(
                    text=Localization.get(locale, "zombiedice-status-main-round"),
                    id="phase",
                )
            )

        current = self.current_player
        if current:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "zombiedice-status-current-you"
                        if current.id == viewer.id
                        else "zombiedice-status-current-player",
                        player=current.name,
                    ),
                    id="current_turn",
                )
            )

        turn_order = self._round_players()
        if turn_order:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "zombiedice-status-turn-order",
                        players=Localization.format_list_and(
                            locale,
                            [player.name for player in turn_order],
                        ),
                    ),
                    id="turn_order",
                )
            )

        for player in self._ordered_active_players():
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "zombiedice-status-score-you"
                        if player.id == viewer.id
                        else "zombiedice-status-score-player",
                        player=player.name,
                        score=self.get_player_score(player),
                    ),
                    id=f"score:{player.id}",
                )
            )
        return items

    def _format_pool(self, pool: DicePool, locale: str) -> str:
        if not pool.total:
            return Localization.get(locale, "zombiedice-no-dice")
        return Localization.format_list_and(
            locale,
            [
                Localization.get(
                    locale,
                    "zombiedice-pool-color",
                    count=pool.count(color),
                    color=Localization.get(locale, f"zombiedice-color-{color}"),
                )
                for color in COLORS
                if pool.count(color)
            ],
        )

    def _format_roll(self, results: list[RollResult], locale: str) -> str:
        return Localization.format_list_and(
            locale,
            [
                Localization.get(
                    locale,
                    "zombiedice-roll-result",
                    color=Localization.get(
                        locale,
                        f"zombiedice-color-{result.color}",
                    ),
                    face=Localization.get(
                        locale,
                        f"zombiedice-face-{result.face}",
                    ),
                )
                for result in results
            ],
        )

    # ------------------------------------------------------------------
    # Bot policy
    # ------------------------------------------------------------------

    def _jolt_bot(self, player: ZombieDicePlayer) -> None:
        BotHelper.jolt_bot(
            player,
            ticks=random.randint(*BOT_THINK_TICKS),  # nosec B311
        )

    def _bot_observation(self, player: ZombieDicePlayer) -> BotObservation:
        round_players = self._round_players()
        opponents = [other for other in round_players if other.id != player.id]
        try:
            current_index = round_players.index(player)
        except ValueError:
            later_opponents: list[ZombieDicePlayer] = []
        else:
            later_opponents = round_players[current_index + 1 :]
        return BotObservation(
            cup=self.cup.copy(),
            footprints=self.footprints.copy(),
            brain_dice=self.brain_dice.copy(),
            shotguns=self.shotgun_dice.total,
            turn_brains=self.turn_brains,
            banked_score=self.get_player_score(player),
            target_score=self.options.target_score,
            score_to_beat=max(
                (self.get_player_score(other) for other in opponents),
                default=0,
            ),
            final_round_active=self.final_round_active,
            in_tiebreaker=bool(self.tiebreaker_player_ids),
            has_rolled=self.has_rolled,
            later_opponent_score=max(
                (self.get_player_score(other) for other in later_opponents),
                default=0,
            ),
        )

    def bot_think(self, player: ZombieDicePlayer) -> str | None:
        if self.current_player is not player:
            return None
        return choose_action(self._bot_observation(player))

    # ------------------------------------------------------------------
    # Localization and results
    # ------------------------------------------------------------------

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _host_locale(self) -> str:
        host_player = self.get_player_by_name(self.host) if self.host else None
        return self._player_locale(host_player) if host_player else "en"

    def build_game_result(self) -> GameResult:
        players = self._ordered_active_players()
        ranked = sorted(
            players,
            key=lambda player: (-self.get_player_score(player), player.name),
        )
        final_scores = {
            player.name: self.get_player_score(player) for player in players
        }
        rankings = []
        previous_score: int | None = None
        current_rank = 0
        for position, player in enumerate(ranked, 1):
            score = self.get_player_score(player)
            if score != previous_score:
                current_rank = position
                previous_score = score
            rankings.append(
                {
                    "rank": current_rank,
                    "player_id": player.id,
                    "player_name": player.name,
                    "score": score,
                }
            )
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
                "winner_score": next(
                    (
                        self.get_player_score(player)
                        for player in players
                        if player.id == self.winner_id
                    ),
                    0,
                ),
                "final_scores": final_scores,
                "rankings": rankings,
                "rounds_played": self.round,
                "tiebreak_rounds": self.tiebreak_round,
                "target_score": self.options.target_score,
                RATING_COMPETITORS_KEY: rating_competitors_from_scores(
                    ([player.id], self.get_player_score(player)) for player in ranked
                ),
                "player_stats": {
                    player.id: {
                        "turns_taken": player.turns_taken,
                        "rolls_made": player.rolls_made,
                        "brains_banked": player.brains_banked,
                        "busts": player.busts,
                        "best_turn": player.best_turn,
                    }
                    for player in players
                },
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "zombiedice-results-header")]
        winner_name = result.custom_data.get("winner_name")
        if winner_name:
            lines.append(
                Localization.get(
                    locale,
                    "zombiedice-results-winner",
                    player=winner_name,
                    score=result.custom_data.get("winner_score", 0),
                )
            )
        for entry in result.custom_data.get("rankings", []):
            lines.append(
                Localization.get(
                    locale,
                    "zombiedice-results-line",
                    rank=entry["rank"],
                    player=entry["player_name"],
                    score=entry["score"],
                )
            )
        return lines
