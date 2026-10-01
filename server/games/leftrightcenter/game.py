"""Left Center Right dice game implementation."""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.dice import random_dice_throw_sound
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.stats_helpers import (
    RATING_COMPETITORS_KEY,
    rating_competitors_from_scores,
)
from ...game_utils.options import IntOption, option_field
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


DICE_FACES = ("left", "center", "right", "dot", "dot", "dot")
VALID_DICE_FACES = frozenset(DICE_FACES)
ROLL_SEQUENCE_ID = "lrc_roll"
ROLL_SEQUENCE_TAG = "lrc_roll"
ROLL_TO_TRANSFER_DELAY_TICKS = 10
TRANSFER_SOUND_DELAY_TICKS = 10


@dataclass
class LeftRightCenterPlayer(Player):
    """Per-player Left Center Right state."""

    chips: int = 0


@dataclass
class LeftRightCenterOptions(GameOptions):
    """Host-configurable Left Center Right settings."""

    starting_chips: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=10,
            value_key="count",
            label="lrc-set-starting-chips",
            prompt="lrc-enter-starting-chips",
            change_msg="lrc-option-changed-starting-chips",
        )
    )


@dataclass
@register_game
class LeftRightCenterGame(Game):
    """Classic Left Center Right with a configurable starting stack."""

    relevant_preferences = ["brief_announcements"]

    players: list[LeftRightCenterPlayer] = field(default_factory=list)
    options: LeftRightCenterOptions = field(default_factory=LeftRightCenterOptions)
    score_unit_key = "game-score-unit-chips"
    center_pot: int = 0
    last_roll: list[str] = field(default_factory=list)
    last_roll_player_id: str = ""

    @classmethod
    def get_name(cls) -> str:
        return "Left Center Right"

    @classmethod
    def get_type(cls) -> str:
        return "leftrightcenter"

    @classmethod
    def get_category(cls) -> str:
        return "dice"

    @classmethod
    def get_min_players(cls) -> int:
        return 3

    @classmethod
    def get_max_players(cls) -> int:
        return 20

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> LeftRightCenterPlayer:
        return LeftRightCenterPlayer(id=player_id, name=name, is_bot=is_bot)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _active_lrc_players(self) -> list[LeftRightCenterPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, LeftRightCenterPlayer)
        ]

    def _broadcast_actor_l(
        self,
        actor: LeftRightCenterPlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast an event using each listener's perspective and verbosity."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            is_actor = listener.id == actor.id
            key = personal_key if is_actor else others_key
            if self._wants_brief(user):
                if is_actor and brief_personal_key:
                    key = brief_personal_key
                elif not is_actor and brief_others_key:
                    key = brief_others_key

            payload = dict(kwargs)
            if not is_actor:
                payload["player"] = actor
            payload = self._resolve_broadcast_kwargs(user.locale, payload)
            user.speak_l(key, buffer="game", **payload)

    def _localized_faces(self, locale: str, faces: list[str]) -> str:
        localized = [
            Localization.get(locale, f"lrc-face-{face}") for face in faces
        ]
        return Localization.format_list_and(locale, localized)

    # ======================================================================
    # Actions and visibility
    # ======================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if not isinstance(player, LeftRightCenterPlayer) or player.chips <= 0:
            return "lrc-no-chips-to-roll"
        if self.is_sequence_gameplay_locked():
            return "lrc-roll-already-resolving"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_info_action_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_info_action_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def create_turn_action_set(self, player: LeftRightCenterPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(self._player_locale(player), "lrc-roll", count=0),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                get_label="_get_roll_label",
                show_in_actions_menu=False,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        action_set.add(
            Action(
                id="check_center",
                label=Localization.get(locale, "lrc-check-center"),
                handler="_action_check_center",
                is_enabled="_is_info_action_enabled",
                is_hidden="_is_info_action_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_last_roll",
                label=Localization.get(locale, "lrc-check-last-roll"),
                handler="_action_check_last_roll",
                is_enabled="_is_info_action_enabled",
                is_hidden="_is_info_action_hidden",
                include_spectators=True,
            )
        )

        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "check_center",
                    "check_last_roll",
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()

        host_user = None
        if self.host:
            host_player = self.get_player_by_name(self.host)
            if host_player:
                host_user = self.get_user(host_player)
        locale = host_user.locale if host_user else "en"

        self.define_keybind(
            "r",
            Localization.get(locale, "lrc-roll-label"),
            ["roll"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "c",
            Localization.get(locale, "lrc-check-center"),
            ["check_center"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "d",
            Localization.get(locale, "lrc-check-last-roll"),
            ["check_last_roll"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ======================================================================
    # Game flow
    # ======================================================================

    def on_start(self) -> None:
        self.cancel_sequences_by_tag(ROLL_SEQUENCE_TAG)
        self.clear_scheduled_sounds()
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.center_pot = 0
        self.last_roll = []
        self.last_roll_player_id = ""

        active_players = self._active_lrc_players()
        for player in active_players:
            player.chips = self.options.starting_chips

        self.team_manager.team_mode = "individual"
        self.team_manager.setup_teams([player.name for player in active_players])
        self._sync_team_scores()
        self.set_turn_players(active_players)
        self.play_music("game_pig/mus.ogg")
        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, LeftRightCenterPlayer):
            return
        if self._check_for_winner():
            return

        if player.chips <= 0:
            self._broadcast_actor_l(
                player,
                "lrc-you-skip-no-chips",
                "lrc-player-skips-no-chips",
                brief_personal_key="lrc-you-skip-no-chips-brief",
                brief_others_key="lrc-player-skips-no-chips-brief",
            )
            self._end_turn()
            return

        self.announce_turn()
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(5, 10))
        self.refresh_menus()

    def _end_turn(self) -> None:
        if self._check_for_winner():
            return
        self.advance_turn(announce=False)
        self._start_turn()

    def _get_left_right(
        self, player: LeftRightCenterPlayer
    ) -> tuple[LeftRightCenterPlayer, LeftRightCenterPlayer] | None:
        order = self._active_lrc_players()
        if player not in order or len(order) < 2:
            return None
        index = order.index(player)
        return order[(index - 1) % len(order)], order[(index + 1) % len(order)]

    def _broadcast_roll_results(
        self, player: LeftRightCenterPlayer, faces: list[str]
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            results = self._localized_faces(user.locale, faces)
            is_actor = listener.id == player.id
            if self._wants_brief(user):
                key = "lrc-you-roll-brief" if is_actor else "lrc-player-rolls-brief"
            else:
                key = "lrc-you-roll" if is_actor else "lrc-player-rolls"
            kwargs = {"results": results}
            if not is_actor:
                kwargs["player"] = player.name
            user.speak_l(key, buffer="game", **kwargs)

    def _transfer_sound_beats(self, faces: list[str]) -> list[SequenceBeat]:
        beats: list[SequenceBeat] = []
        for face in ("left", "right", "center"):
            sound = (
                "game_ninetynine/lose1_other.ogg"
                if face == "center"
                else "game_ninetynine/lose1_you.ogg"
            )
            pan = -50 if face == "left" else 50 if face == "right" else 0
            for _ in range(faces.count(face)):
                beats.append(
                    SequenceBeat(
                        ops=[SequenceOperation.sound_op(sound, pan=pan)],
                        delay_after_ticks=TRANSFER_SOUND_DELAY_TICKS,
                    )
                )
        return beats

    def _action_roll(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LeftRightCenterPlayer):
            return
        if self.has_active_sequence(tag=ROLL_SEQUENCE_TAG):
            return

        roll_count = min(3, max(0, player.chips))
        if roll_count <= 0:
            user = self.get_user(player)
            if user:
                user.speak_l("lrc-no-chips-to-roll", buffer="game")
            return

        faces = [random.choice(DICE_FACES) for _ in range(roll_count)]
        self.last_roll = list(faces)
        self.last_roll_player_id = player.id
        self._broadcast_roll_results(player, faces)

        payload = {"player_id": player.id, "faces": list(faces)}
        beats = [
            SequenceBeat(
                ops=[SequenceOperation.sound_op(random_dice_throw_sound())],
                delay_after_ticks=ROLL_TO_TRANSFER_DELAY_TICKS,
            ),
            SequenceBeat(
                ops=[SequenceOperation.callback_op("resolve_roll", payload)]
            ),
            *self._transfer_sound_beats(faces),
            SequenceBeat(
                ops=[SequenceOperation.callback_op("complete_roll", payload)]
            ),
        ]
        self.start_sequence(
            ROLL_SEQUENCE_ID,
            beats,
            tag=ROLL_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )
        self.refresh_menus(player)

    def _validated_roll_payload(
        self, payload: dict, *, require_current_chip_count: bool
    ) -> tuple[LeftRightCenterPlayer, list[str]] | None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not isinstance(player, LeftRightCenterPlayer):
            return None
        if player is not self.current_player or player not in self.get_active_players():
            return None

        raw_faces = payload.get("faces", [])
        if not isinstance(raw_faces, list):
            return None
        faces = [str(face) for face in raw_faces]
        if not faces or any(face not in VALID_DICE_FACES for face in faces):
            return None
        if len(faces) > 3:
            return None
        if (
            require_current_chip_count
            and len(faces) != min(3, max(0, player.chips))
        ):
            return None
        return player, faces

    def _resolve_roll(self, player: LeftRightCenterPlayer, faces: list[str]) -> None:
        neighbors = self._get_left_right(player)
        if not neighbors:
            return
        left_player, right_player = neighbors

        left_count = faces.count("left")
        right_count = faces.count("right")
        center_count = faces.count("center")
        moved_count = left_count + right_count + center_count
        if moved_count > player.chips:
            return

        player.chips -= moved_count
        left_player.chips += left_count
        right_player.chips += right_count
        self.center_pot += center_count
        self._sync_team_scores()

        if left_count:
            self._broadcast_actor_l(
                player,
                "lrc-you-pass-left",
                "lrc-player-passes-left",
                brief_personal_key="lrc-you-pass-left-brief",
                brief_others_key="lrc-player-passes-left-brief",
                target=left_player.name,
                count=left_count,
                remaining=player.chips,
                target_total=left_player.chips,
            )
        if right_count:
            self._broadcast_actor_l(
                player,
                "lrc-you-pass-right",
                "lrc-player-passes-right",
                brief_personal_key="lrc-you-pass-right-brief",
                brief_others_key="lrc-player-passes-right-brief",
                target=right_player.name,
                count=right_count,
                remaining=player.chips,
                target_total=right_player.chips,
            )
        if center_count:
            self._broadcast_actor_l(
                player,
                "lrc-you-pass-center",
                "lrc-player-passes-center",
                brief_personal_key="lrc-you-pass-center-brief",
                brief_others_key="lrc-player-passes-center-brief",
                count=center_count,
                remaining=player.chips,
                center=self.center_pot,
            )
        if moved_count == 0:
            self._broadcast_actor_l(
                player,
                "lrc-you-keep-all",
                "lrc-player-keeps-all",
                brief_personal_key="lrc-you-keep-all-brief",
                brief_others_key="lrc-player-keeps-all-brief",
                count=player.chips,
            )
        self.refresh_menus()

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if sequence_id != ROLL_SEQUENCE_ID or self.status != "playing":
            return

        validated = self._validated_roll_payload(
            payload,
            require_current_chip_count=callback_id == "resolve_roll",
        )
        if not validated:
            return
        player, faces = validated

        if callback_id == "resolve_roll":
            self._resolve_roll(player, faces)
        elif callback_id == "complete_roll":
            self._end_turn()

    def _check_for_winner(self) -> bool:
        players_with_chips = [
            player for player in self._active_lrc_players() if player.chips > 0
        ]
        if len(players_with_chips) != 1:
            return False

        winner = players_with_chips[0]
        self._broadcast_actor_l(
            winner,
            "lrc-you-win",
            "lrc-player-wins",
            brief_personal_key="lrc-you-win-brief",
            brief_others_key="lrc-player-wins-brief",
            count=winner.chips,
            center=self.center_pot,
        )
        self.play_sound("game_pig/win.ogg")
        self.finish_game()
        return True

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if self.status == "playing" and not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def bot_think(self, player: LeftRightCenterPlayer) -> str | None:
        return "roll"

    # ======================================================================
    # Information and validation
    # ======================================================================

    def _action_check_center(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l("lrc-center-pot", buffer="game", count=self.center_pot)

    def _action_check_last_roll(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        roller = self.get_player_by_id(self.last_roll_player_id)
        if not roller or not self.last_roll:
            user.speak_l("lrc-last-roll-none", buffer="game")
            return

        results = self._localized_faces(user.locale, self.last_roll)
        if roller.id == player.id:
            user.speak_l("lrc-last-roll-you", buffer="game", results=results)
        else:
            user.speak_l(
                "lrc-last-roll-player",
                buffer="game",
                player=roller.name,
                results=results,
            )

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if not 1 <= self.options.starting_chips <= 10:
            errors.append(
                (
                    "lrc-error-starting-chips-invalid",
                    {"count": self.options.starting_chips, "min": 1, "max": 10},
                )
            )
        return errors

    def _sync_team_scores(self) -> None:
        for team in self.team_manager.teams:
            team.total_score = 0
        for player in self._active_lrc_players():
            team = self.team_manager.get_team(player.name)
            if team:
                team.total_score = player.chips

    def _get_roll_label(self, player: Player, action_id: str) -> str:
        count = (
            min(3, max(0, player.chips))
            if isinstance(player, LeftRightCenterPlayer)
            else 0
        )
        return Localization.get(self._player_locale(player), "lrc-roll", count=count)

    # ======================================================================
    # Results
    # ======================================================================

    def build_game_result(self) -> GameResult:
        ranked_players = sorted(
            self._active_lrc_players(), key=lambda player: player.chips, reverse=True
        )
        winners = [player for player in ranked_players if player.chips > 0]
        winner = winners[0] if len(winners) == 1 else None
        rankings = [
            {"members": [player.name], "score": player.chips}
            for player in ranked_players
        ]
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(player)
                for player in ranked_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "center_pot": self.center_pot,
                "final_chips": {
                    player.name: player.chips for player in ranked_players
                },
                "rankings": rankings,
                "team_rankings": rankings,
                RATING_COMPETITORS_KEY: rating_competitors_from_scores(
                    ([player.id], player.chips) for player in ranked_players
                ),
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores-header")]
        final_chips = result.custom_data.get("final_chips", {})
        for name, chips in final_chips.items():
            lines.append(
                Localization.get(
                    locale, "lrc-line-format", player=name, chips=chips
                )
            )
        lines.append(
            Localization.get(
                locale,
                "lrc-center-pot",
                count=result.custom_data.get("center_pot", 0),
            )
        )
        return lines
