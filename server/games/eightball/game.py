"""Accessible, skill-driven Eight-Ball Pool for PlayAural."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import math
import random

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.client_types import is_touch_client
from ...game_utils.menu_management_mixin import MenuBuild
from ...game_utils.options import (
    BoolOption, IntOption, MenuOption, get_option_meta, option_field,
)
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from .bot import DEFAULT_DIFFICULTY, DIFFICULTIES, choose_shot_plan
from .physics import (
    BALL_RADIUS, BALL_RESTITUTION, FRICTION_PER_60HZ,
    SIMULATION_HZ, STOP_SPEED, TABLE_SIZES,
    Ball, PhysicsEvent, ShotResult, build_cutthroat_rack, build_rack, shot_speed,
    get_table_geometry, simulate_shot,
)

GROUP_SOLIDS = "solids"
GROUP_STRIPES = "stripes"
MODE_SINGLES = "eightball_singles"
MODE_DOUBLES = "eightball_doubles"
MODE_CUTTHROAT = "cutthroat_five"
MODE_CHOICES = [MODE_SINGLES, MODE_DOUBLES, MODE_CUTTHROAT]
MODE_PLAYERS = {MODE_SINGLES: 2, MODE_DOUBLES: 4, MODE_CUTTHROAT: 5}
TABLE_LANGUAGES = ["en", "es", "pt"]
PHYSICS_PLAYBACK_RATE = 3.0
SHOT_SEQUENCE_ID = "eightball-shot"
LAG_SEQUENCE_ID = "eightball-lag-shot"
SOUND_ROOT = "game_eightball"


@dataclass
class EightBallPlayer(Player):
    team_index: int = -1
    protected_balls: list[int] = field(default_factory=list)
    group: str = ""
    aim_angle: float = 180.0
    power: int = 55
    spin: int = 0
    side_spin: int = 0
    cue_elevation: int = 0
    called_ball: int = -1
    called_pocket: int = -1
    safety: bool = False
    fouls: int = 0
    potted_balls: list[int] = field(default_factory=list)
    frames_won: int = 0
    cursor_x: float = 25.0
    cursor_y: float = 0.0
    pocket_cursor: int = -1
    focused_ball: int = -1
    last_aim_feedback: str = ""


@dataclass
class EightBallOptions(GameOptions):
    play_mode: str = option_field(
        MenuOption(
            default=MODE_SINGLES, choices=MODE_CHOICES, value_key="mode",
            label="eightball-option-mode", prompt="eightball-option-mode-prompt",
            change_msg="eightball-option-mode-changed",
            description="eightball-option-mode-description",
            choice_labels={mode: f"eightball-mode-{mode}" for mode in MODE_CHOICES},
        )
    )
    table_size: str = option_field(
        MenuOption(
            default="9ft", choices=list(TABLE_SIZES), value_key="table_size",
            label="eightball-option-table-size",
            prompt="eightball-option-table-size-prompt",
            change_msg="eightball-option-table-size-changed",
            description="eightball-option-table-size-description",
            choice_labels={size: f"eightball-table-size-{size}" for size in TABLE_SIZES},
        )
    )
    power_assistance: bool = option_field(
        BoolOption(
            default=True,
            label="eightball-option-power-assistance",
            change_msg="eightball-option-power-assistance-changed",
            description="eightball-option-power-assistance-description",
        )
    )
    table_language: str = option_field(
        MenuOption(
            default="en", choices=TABLE_LANGUAGES, value_key="language",
            label="eightball-option-language", prompt="eightball-option-language-prompt",
            change_msg="eightball-option-language-changed",
            description="eightball-option-language-description",
            choice_labels={
                "en": "eightball-language-en",
                "es": "eightball-language-es",
                "pt": "eightball-language-pt",
            },
        )
    )
    frames_to_win: int = option_field(
        IntOption(
            default=1, min_val=1, max_val=10, value_key="frames_to_win",
            label="eightball-option-frames", prompt="eightball-option-frames-prompt",
            change_msg="eightball-option-frames-changed",
            description="eightball-option-frames-description",
        )
    )
    bot_difficulty: str = option_field(
        MenuOption(
            default=DEFAULT_DIFFICULTY, choices=list(DIFFICULTIES),
            choice_labels={level: f"eightball-difficulty-{level}" for level in DIFFICULTIES},
            value_key="bot_difficulty", label="eightball-option-bot-difficulty",
            prompt="eightball-option-bot-difficulty-prompt",
            change_msg="eightball-option-bot-difficulty-changed",
            description="eightball-option-bot-difficulty-description",
        )
    )

    def create_options_action_set(
        self, game: "EightBallGame", player: EightBallPlayer,
    ) -> ActionSet:
        action_set = ActionSet(name="options")
        self._populate_action_set(action_set, game, player, self.table_language)
        return action_set

    def update_options_labels(self, game: "EightBallGame") -> None:
        for player in game.players:
            action_set = game.get_action_set(player, "options")
            if action_set is None:
                game.add_action_set(player, self.create_options_action_set(game, player))
                continue
            action_set._actions.clear()
            action_set._order.clear()
            self._populate_action_set(
                action_set, game, player, self.table_language,
            )


@register_game
@dataclass
class EightBallGame(Game):
    """Two-player Eight-Ball using server-side physics and spatial audio."""

    players: list[EightBallPlayer] = field(default_factory=list)
    options: EightBallOptions = field(default_factory=EightBallOptions)
    balls: list[Ball] = field(default_factory=list)
    table_open: bool = True
    break_shot: bool = True
    ball_in_hand: bool = False
    frame_number: int = 1
    breaker_index: int = 0
    winner_id: str = ""
    pending_shot: ShotResult | None = None
    shot_player_id: str = ""
    shot_group_before: str = ""
    shot_remaining_before: int = 0
    shot_legal_targets_before: list[int] = field(default_factory=list)
    shot_was_break: bool = False
    ball_in_hand_head_string: bool = False
    break_decision: str = ""
    break_offender_id: str = ""
    lag_active: bool = False
    lag_break_choice_pending: bool = False
    lag_player_ids: list[str] = field(default_factory=list)
    lag_results: dict[str, float] = field(default_factory=dict)
    lag_bad_players: list[str] = field(default_factory=list)
    lag_winner_id: str = ""
    cutthroat_eliminated_ids: list[str] = field(default_factory=list)
    cutthroat_elimination_order: list[str] = field(default_factory=list)
    shot_preview_cache: dict[str, ShotResult] = field(default_factory=dict)

    @classmethod
    def get_name(cls) -> str:
        return "Pool"

    @classmethod
    def get_name_key(cls) -> str:
        return "game-name-eightball"

    @classmethod
    def get_type(cls) -> str:
        return "eightball"

    @classmethod
    def get_category(cls) -> str:
        return "arcade"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 5

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> EightBallPlayer:
        return EightBallPlayer(id=player_id, name=name, is_bot=is_bot)

    @staticmethod
    def _language_from_playaural(locale: str) -> str:
        language = str(locale or "en").lower().replace("_", "-").split("-", 1)[0]
        return language if language in TABLE_LANGUAGES else "en"

    def initialize_lobby(self, host_name: str, host_user) -> None:
        # A new table starts in its creator's supported PlayAural language.
        # Unsupported locales, including Vietnamese for this game, use English.
        self.options.table_language = self._language_from_playaural(host_user.locale)
        super().initialize_lobby(host_name, host_user)

    def get_active_players(self) -> list[EightBallPlayer]:
        return [player for player in self.players if not player.is_spectator]

    def _locale(self, player: Player) -> str:
        return self.options.table_language

    def _configured_team_mode(self) -> str:
        return "2v2" if self.options.play_mode == MODE_DOUBLES else "individual"

    @property
    def _table_geometry(self):
        return get_table_geometry(self.options.table_size)

    @property
    def _pockets(self) -> tuple[tuple[float, float], ...]:
        return self._table_geometry.pockets

    @property
    def _pocket_aim_points(self) -> tuple[tuple[float, float], ...]:
        return self._table_geometry.pocket_aim_points

    def _team_arrangement_lines(self, locale: str) -> list[str]:
        return super()._team_arrangement_lines(self.options.table_language)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        required = MODE_PLAYERS[self.options.play_mode]
        current = len(self.get_active_players())
        if current != required:
            errors.append(("eightball-mode-player-count", {"required": required}))
        return errors

    def broadcast_l(
        self, message_id: str, buffer: str = "game",
        exclude: Player | None = None, **kwargs,
    ) -> None:
        locale = self.options.table_language
        resolved = self._resolve_broadcast_kwargs(locale, kwargs)
        text = Localization.get(locale, message_id, **resolved)
        self.broadcast(text, buffer=buffer, exclude=exclude)

    def broadcast_personal_l(
        self, player: Player, personal_message_id: str,
        others_message_id: str, buffer: str = "game", **kwargs,
    ) -> None:
        locale = self.options.table_language
        resolved = self._resolve_broadcast_kwargs(locale, kwargs)
        user = self.get_user(player)
        if user:
            user.speak(Localization.get(locale, personal_message_id, **resolved), buffer)
        others = Localization.get(
            locale, others_message_id, player=player.name, **resolved
        )
        for other in self.players:
            if other is player:
                continue
            other_user = self.get_user(other)
            if other_user:
                other_user.speak(others, buffer)

    def _broadcast_winners_l(
        self, winners: list[EightBallPlayer], personal_message_id: str,
        others_message_id: str, **kwargs,
    ) -> None:
        winner_ids = {winner.id for winner in winners}
        locale = self.options.table_language
        resolved = self._resolve_broadcast_kwargs(locale, kwargs)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            message_id = (
                personal_message_id if listener.id in winner_ids
                else others_message_id
            )
            user.speak(Localization.get(locale, message_id, **resolved), "game")

    def _broadcast_option_change(self, meta, value) -> None:
        locale = self.options.table_language
        kwargs = (
            meta.get_change_kwargs_localized(value, locale)
            if hasattr(meta, "get_change_kwargs_localized")
            else meta.get_change_kwargs(value)
        )
        self.broadcast(
            Localization.get(locale, meta.change_msg, **kwargs), buffer="system"
        )

    # Actions ---------------------------------------------------------------

    def _handle_option_change(self, option_name: str, value: str) -> None:
        previous_language = self.options.table_language
        super()._handle_option_change(option_name, value)
        if (
            option_name == "table_language"
            and self.options.table_language != previous_language
        ):
            self._rebuild_localized_controls()

    def _option_description_text(
        self, player: Player, menu_item_id: str,
    ) -> str | None:
        option_name = menu_item_id
        for prefix in ("set_", "toggle_"):
            if option_name.startswith(prefix):
                option_name = option_name.removeprefix(prefix)
                break
        meta = get_option_meta(type(self.options), option_name)
        if meta is None:
            return None
        return meta.get_description(
            self.options.table_language,
            getattr(self.options, option_name, meta.default),
            game=self,
            player=player,
        )

    def _build_action_menu_input_items(
        self, action: Action, player: Player, user, options: list[str],
    ):
        items = super()._build_action_menu_input_items(
            action, player, user, options,
        )
        if not action.id.startswith("set_"):
            return items
        option_name = action.id.removeprefix("set_")
        meta = get_option_meta(type(self.options), option_name)
        if not isinstance(meta, MenuOption):
            return items
        for item in items:
            item.text = (
                Localization.get(self.options.table_language, "cancel")
                if item.id == "_cancel"
                else meta.get_localized_choice(
                    str(item.id), self.options.table_language,
                )
            )
        return items

    def _rebuild_localized_controls(self) -> None:
        """Recreate cached controls after the table language changes."""
        self._keybinds.clear()
        self.setup_keybinds()
        for player in self.players:
            self.player_action_sets[player.id] = []
            self.setup_player_actions(player)
        self.refresh_menus()

    def setup_keybinds(self) -> None:
        # This method may run again after restoring a table or changing its
        # language. Rebuild from scratch so Ctrl+F1 never lists duplicates.
        self._keybinds.clear()
        super().setup_keybinds()
        locale = self.options.table_language
        binds = (
            ("left", "eightball-action-turn-left", "turn_left"),
            ("right", "eightball-action-turn-right", "turn_right"),
            ("ctrl+left", "eightball-action-turn-left-fine", "turn_left_fine"),
            ("ctrl+right", "eightball-action-turn-right-fine", "turn_right_fine"),
            ("ctrl+shift+left", "eightball-action-turn-left-medium", "turn_left_medium"),
            ("ctrl+shift+right", "eightball-action-turn-right-medium", "turn_right_medium"),
            ("shift+left", "eightball-action-turn-left-fast", "turn_left_fast"),
            ("shift+right", "eightball-action-turn-right-fast", "turn_right_fast"),
            ("up", "eightball-action-move-forward", "move_forward"),
            ("down", "eightball-action-move-backward", "move_backward"),
            ("shift+up", "eightball-action-move-forward-fast", "move_forward_fast"),
            ("shift+down", "eightball-action-move-backward-fast", "move_backward_fast"),
            ("pageup", "eightball-action-spin-up", "spin_up"),
            ("pagedown", "eightball-action-spin-down", "spin_down"),
            ("home", "eightball-action-side-spin-left", "side_spin_left"),
            ("end", "eightball-action-side-spin-right", "side_spin_right"),
            ("ctrl+up", "eightball-action-elevation-up", "elevation_up"),
            ("ctrl+down", "eightball-action-elevation-down", "elevation_down"),
            ("x", "eightball-action-power-up", "power_up"),
            ("shift+x", "eightball-action-power-down", "power_down"),
            ("b", "eightball-action-call-ball", "call_ball"),
            ("m", "eightball-action-locate-ball", "locate_ball"),
            ("shift+m", "eightball-action-next-ball", "next_ball"),
            ("p", "eightball-action-call-pocket", "call_pocket"),
            ("shift+y", "eightball-action-safety", "toggle_safety"),
            ("1", "eightball-break-option-1", "break_option_1"),
            ("2", "eightball-break-option-2", "break_option_2"),
            ("3", "eightball-break-option-3", "break_option_3"),
            ("space", "eightball-action-shoot", "shoot"),
            ("enter", "eightball-action-shoot", "shoot"),
        )
        for key, label_key, action in binds:
            self.define_keybind(
                key, Localization.get(locale, label_key), [action],
                state=KeybindState.ACTIVE,
            )
        for key, label_key, action in (
            ("l", "eightball-action-probe-line", "probe_line"),
            ("c", "eightball-action-pockets-info", "pockets_info"),
            ("v", "eightball-action-table-overview", "table_overview"),
            ("e", "eightball-action-cue-status", "cue_status"),
        ):
            self.define_keybind(
                key, Localization.get(locale, label_key), [action],
                state=KeybindState.ACTIVE,
                include_spectators=True,
            )

    def _turn_disabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player is not player:
            return "action-not-your-turn"
        if self.lag_active:
            if action_id not in {"shoot", "power_up", "power_down"}:
                return "eightball-lag-required"
            return None
        if self.lag_break_choice_pending:
            return "eightball-lag-break-choice-required"
        if self.break_decision:
            return "eightball-break-decision-required"
        if self.is_sequence_gameplay_locked():
            return "eightball-action-resolving"
        return None

    def _turn_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        return (
            Visibility.HIDDEN
            if self.status != "playing" or player.is_spectator
            or self.lag_break_choice_pending
            or (self.lag_active and action_id not in {"shoot", "power_up", "power_down"})
            else Visibility.VISIBLE
        )

    def _lag_break_choice_disabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | None:
        if not self.lag_break_choice_pending:
            return "eightball-no-lag-break-choice"
        if player.is_spectator or player.id != self.lag_winner_id:
            return "action-not-your-turn"
        return None

    def _lag_break_choice_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        return (
            Visibility.VISIBLE
            if self.lag_break_choice_pending and player.id == self.lag_winner_id
            else Visibility.HIDDEN
        )

    def _always_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        return None

    def _always_visible(self, player: Player, *, action_id: str | None = None) -> Visibility:
        return Visibility.VISIBLE

    def _info_visible(self, player: Player, *, action_id: str | None = None) -> Visibility:
        return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN

    def create_turn_action_set(self, player: EightBallPlayer) -> ActionSet:
        locale = self._locale(player)
        action_set = ActionSet(name="turn")
        for choice in ("self", "opponent"):
            action_set.add(Action(
                id=f"lag_break_{choice}",
                label=Localization.get(locale, f"eightball-lag-break-{choice}"),
                handler=f"_action_lag_break_{choice}",
                is_enabled="_lag_break_choice_disabled",
                is_hidden="_lag_break_choice_hidden",
            ))
        specs = (
            ("shoot", "eightball-action-shoot", "_action_shoot"),
            ("turn_left", "eightball-action-turn-left", "_action_turn_left"),
            ("turn_right", "eightball-action-turn-right", "_action_turn_right"),
            ("turn_left_fine", "eightball-action-turn-left-fine", "_action_turn_left_fine"),
            ("turn_right_fine", "eightball-action-turn-right-fine", "_action_turn_right_fine"),
            ("turn_left_medium", "eightball-action-turn-left-medium", "_action_turn_left_medium"),
            ("turn_right_medium", "eightball-action-turn-right-medium", "_action_turn_right_medium"),
            ("turn_left_fast", "eightball-action-turn-left-fast", "_action_turn_left_fast"),
            ("turn_right_fast", "eightball-action-turn-right-fast", "_action_turn_right_fast"),
            ("move_forward", "eightball-action-move-forward", "_action_move_forward"),
            ("move_backward", "eightball-action-move-backward", "_action_move_backward"),
            ("move_forward_fast", "eightball-action-move-forward-fast", "_action_move_forward_fast"),
            ("move_backward_fast", "eightball-action-move-backward-fast", "_action_move_backward_fast"),
            ("spin_up", "eightball-action-spin-up", "_action_spin_up"),
            ("spin_down", "eightball-action-spin-down", "_action_spin_down"),
            ("side_spin_left", "eightball-action-side-spin-left", "_action_side_spin_left"),
            ("side_spin_right", "eightball-action-side-spin-right", "_action_side_spin_right"),
            ("elevation_up", "eightball-action-elevation-up", "_action_elevation_up"),
            ("elevation_down", "eightball-action-elevation-down", "_action_elevation_down"),
            ("power_up", "eightball-action-power-up", "_action_power_up"),
            ("power_down", "eightball-action-power-down", "_action_power_down"),
        )
        for action_id, label_key, handler in specs:
            action_set.add(Action(
                id=action_id, label=Localization.get(locale, label_key), handler=handler,
                is_enabled="_turn_disabled", is_hidden="_turn_hidden",
                show_in_actions_menu=False,
            ))
        action_set.add(Action(
            id="call_ball", label=Localization.get(locale, "eightball-action-call-ball"),
            handler="_action_call_ball", is_enabled="_call_disabled", is_hidden="_turn_hidden",
            show_in_actions_menu=False,
        ))
        action_set.add(Action(
            id="locate_ball", label=Localization.get(locale, "eightball-action-locate-ball"),
            handler="_action_locate_ball", is_enabled="_locate_ball_disabled", is_hidden="_turn_hidden",
            input_request=MenuInput(
                prompt="eightball-locate-ball-prompt",
                options="_locate_ball_options",
                option_label="_locate_ball_label",
                initial_selection="_locate_ball_initial",
                locks_gameplay=True,
            ),
            show_in_actions_menu=False,
        ))
        action_set.add(Action(
            id="next_ball", label=Localization.get(locale, "eightball-action-next-ball"),
            handler="_action_next_ball", is_enabled="_locate_ball_disabled", is_hidden="_turn_hidden",
            show_in_actions_menu=False,
        ))
        action_set.add(Action(
            id="call_pocket", label=Localization.get(locale, "eightball-action-call-pocket"),
            handler="_action_call_pocket", is_enabled="_call_pocket_disabled", is_hidden="_turn_hidden",
            input_request=MenuInput(
                prompt="eightball-call-pocket-prompt",
                options="_call_pocket_options",
                option_label="_call_pocket_label",
                initial_selection="_call_pocket_initial",
                locks_gameplay=True,
            ),
            show_in_actions_menu=False,
        ))
        action_set.add(Action(
            id="toggle_safety", label=Localization.get(locale, "eightball-action-safety"),
            handler="_action_toggle_safety", is_enabled="_call_disabled", is_hidden="_turn_hidden",
            show_in_actions_menu=False,
        ))
        for number in (1, 2, 3):
            action_set.add(Action(
                id=f"break_option_{number}",
                label=Localization.get(locale, f"eightball-break-option-{number}"),
                handler=f"_action_break_option_{number}",
                is_enabled="_break_decision_disabled",
                is_hidden="_break_decision_hidden",
                show_in_actions_menu=False,
            ))
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._locale(player)
        specs = (
            ("probe_line", "eightball-action-probe-line", "_action_probe_line"),
            ("pockets_info", "eightball-action-pockets-info", "_action_pockets_info"),
            ("table_overview", "eightball-action-table-overview", "_action_table_overview"),
            ("cue_status", "eightball-action-cue-status", "_action_cue_status"),
        )
        for action_id, label_key, handler in specs:
            action_set.add(Action(
                id=action_id, label=Localization.get(locale, label_key), handler=handler,
                is_enabled="_always_enabled", is_hidden="_info_visible",
                include_spectators=True,
            ))
        self._order_touch_standard_actions(
            action_set, ["probe_line", "pockets_info", "table_overview", "cue_status"]
        )
        return action_set

    def build_menu_items(self, player: Player, user) -> MenuBuild:
        """Give desktop clients a real key-controlled 3D play surface.

        Plain arrow keys navigate a populated desktop menu locally and never
        reach server keybinds. An empty active turn menu lets the desktop client
        route all four arrows to movement. Touch clients retain visible buttons.
        """
        if (
            self.status == "playing"
            and not self.lag_active
            and not self.lag_break_choice_pending
            and not is_touch_client(user)
        ):
            return MenuBuild(items=[])
        return super().build_menu_items(player, user)

    # Lifecycle -------------------------------------------------------------

    def on_start(self) -> None:
        self.clear_scheduled_sounds()
        self.cancel_all_sequences()
        self.status = "playing"
        self.game_active = True
        self._sync_table_status()
        active = self.get_active_players()
        self._setup_team_manager_for_start(self._configured_team_mode(), active)
        ordered = self._get_team_turn_players(active)
        self.set_turn_players(ordered)
        self.breaker_index = 0
        self.frame_number = 1
        self.winner_id = ""
        self.break_decision = ""
        self.break_offender_id = ""
        self.lag_active = False
        self.lag_break_choice_pending = False
        self.lag_player_ids = []
        self.lag_results = {}
        self.lag_bad_players = []
        self.lag_winner_id = ""
        self.cutthroat_eliminated_ids = []
        self.cutthroat_elimination_order = []
        for player in active:
            player.frames_won = 0
            player.fouls = 0
            player.protected_balls = []
        self.broadcast_l(
            "eightball-game-start", buffer="game",
            players=len(active), target=self.options.frames_to_win,
        )
        # Full mode rules remain in the game help.  Speaking them here, then
        # the lag instructions, frame instructions and turn announcement made
        # the opening unnecessarily noisy for returning players.
        if self.options.play_mode == MODE_CUTTHROAT:
            self.breaker_index = 0
            self._start_frame()
        else:
            self._start_lag()

    def _assign_cutthroat_groups(self) -> None:
        for index, player in enumerate(self.turn_players):
            start = index * 3 + 1
            player.protected_balls = list(range(start, start + 3))
            self.broadcast_personal_l(
                player,
                "eightball-cutthroat-group-you",
                "eightball-cutthroat-group-player",
                balls=", ".join(str(number) for number in player.protected_balls),
            )

    def _start_lag(self) -> None:
        self.balls = []
        self.lag_active = True
        self.lag_break_choice_pending = False
        lag_players = (
            self.turn_players[:2]
            if self.options.play_mode == MODE_DOUBLES
            else self.get_active_players()
        )
        self.lag_player_ids = [player.id for player in lag_players]
        self.lag_results = {}
        self.lag_bad_players = []
        self.lag_winner_id = ""
        for player in self.get_active_players():
            player.power = 50
        self.turn_index = 0
        self.broadcast_l("eightball-lag-intro", buffer="game")
        self._start_lag_turn()

    def _start_lag_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, EightBallPlayer):
            return
        self.broadcast_personal_l(player, "eightball-lag-your-turn", "eightball-lag-player-turn")
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(8, 14))
        self.refresh_menus()

    def _take_lag_shot(self, player: EightBallPlayer) -> None:
        geometry = self._table_geometry
        lag_ball = Ball(number=0, x=geometry.half_width - BALL_RADIUS, y=0.0)
        # Real strokes with the same intended strength are not microscopically
        # identical. Equal, very small execution variation for every human and
        # bot prevents a deterministic same-power tie without favouring a seat.
        executed_power = max(10.0, min(100.0, player.power + random.uniform(-0.45, 0.45)))
        result = simulate_shot(
            [lag_ball], 180.0, executed_power, table_size=self.options.table_size,
        )
        final_ball = next(ball for ball in result.balls if ball.number == 0)
        foot_contacts = [
            event for event in result.events
            if event.kind == "rail" and event.x < 0
        ]
        head_contacts = [
            event for event in result.events
            if event.kind == "rail" and event.x > 0
        ]
        bad_reason = ""
        if result.cue_scratch or result.off_table:
            bad_reason = "off-table"
        elif not foot_contacts:
            bad_reason = "no-foot-cushion"
        elif len(foot_contacts) > 1:
            bad_reason = "multiple-foot-cushions"
        elif head_contacts:
            bad_reason = "head-cushion"
        distance = max(0.0, geometry.half_width - BALL_RADIUS - final_ball.x)
        beats = self._physics_sequence_beats(result)
        beats.append(SequenceBeat(ops=[SequenceOperation.callback_op(
            "resolve-lag",
            {
                "player_id": player.id,
                "distance": distance,
                "bad_reason": bad_reason,
            },
        )]))
        self.start_sequence(
            LAG_SEQUENCE_ID, beats, tag="eightball-lag-shot",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY, pause_bots=True,
        )

    def _resolve_lag_shot(self, payload: dict) -> None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        if not isinstance(player, EightBallPlayer) or not self.lag_active:
            return
        distance = float(payload.get("distance", 0.0))
        bad_reason = str(payload.get("bad_reason", ""))
        self.lag_results[player.id] = distance
        if bad_reason:
            self.lag_bad_players.append(player.id)
            self.broadcast_personal_l(
                player, f"eightball-lag-bad-{bad_reason}-you",
                f"eightball-lag-bad-{bad_reason}-player",
            )
        else:
            self.broadcast_personal_l(
                player, "eightball-lag-result-you", "eightball-lag-result-player",
                distance=f"{distance:.1f}",
            )
        if len(self.lag_results) < len(self.lag_player_ids):
            self.advance_turn(announce=False)
            self._start_lag_turn()
            return
        self._finish_lag()

    def _finish_lag(self) -> None:
        valid = [player_id for player_id in self.lag_player_ids if player_id not in self.lag_bad_players]
        if not valid:
            self.broadcast_l("eightball-lag-redo-both-bad", buffer="game")
            self._start_lag()
            return
        if len(valid) == 2 and abs(self.lag_results[valid[0]] - self.lag_results[valid[1]]) < 0.05:
            self.broadcast_l("eightball-lag-redo-tie", buffer="game")
            self._start_lag()
            return
        winner_id = min(valid, key=lambda player_id: self.lag_results[player_id])
        winner = self.get_player_by_id(winner_id)
        if not isinstance(winner, EightBallPlayer):
            return
        self.lag_active = False
        self.lag_winner_id = winner.id
        self.lag_break_choice_pending = True
        self.turn_index = self.turn_players.index(winner)
        self.broadcast_personal_l(
            winner, "eightball-lag-win-you", "eightball-lag-win-player"
        )
        if winner.is_bot:
            BotHelper.jolt_bot(winner, ticks=random.randint(6, 10))
        self.refresh_menus()

    def _action_lag_break_self(
        self, player: EightBallPlayer, action_id: str | None = None
    ) -> None:
        self._choose_first_break(player)

    def _action_lag_break_opponent(
        self, player: EightBallPlayer, action_id: str | None = None
    ) -> None:
        opponent = self._opponent(player)
        if opponent:
            self._choose_first_break(opponent)

    def _choose_first_break(self, breaker: EightBallPlayer) -> None:
        if not self.lag_break_choice_pending:
            return
        self.lag_break_choice_pending = False
        self.breaker_index = self.turn_players.index(breaker)
        self.broadcast_personal_l(
            breaker,
            "eightball-first-break-you",
            "eightball-first-break-player",
        )
        self._start_frame()

    def _start_frame(self) -> None:
        self.balls = (
            build_cutthroat_rack(table_size=self.options.table_size)
            if self.options.play_mode == MODE_CUTTHROAT
            else build_rack(randomize=True, table_size=self.options.table_size)
        )
        self.table_open = True
        self.break_shot = True
        self.ball_in_hand = False
        self.ball_in_hand_head_string = False
        self.break_decision = ""
        self.break_offender_id = ""
        self.pending_shot = None
        self.shot_legal_targets_before = []
        self.cutthroat_eliminated_ids = []
        self.cutthroat_elimination_order = []
        for player in self.get_active_players():
            player.group = ""
            player.aim_angle = 180.0
            player.power = 55
            player.spin = 0
            player.side_spin = 0
            player.cue_elevation = 0
            player.called_ball = -1
            player.called_pocket = -1
            player.safety = False
            player.potted_balls.clear()
            player.cursor_x = self._table_geometry.half_width / 2.0
            player.cursor_y = 0.0
            player.pocket_cursor = -1
            player.focused_ball = -1
            player.last_aim_feedback = ""
        if self.options.play_mode == MODE_CUTTHROAT:
            self._assign_cutthroat_groups()
        if self.turn_players:
            self.turn_index = self.breaker_index % len(self.turn_players)
        self.play_sound("menuclick.ogg", volume=80)
        self.broadcast_l(
            "eightball-frame-start", buffer="game", frame=self.frame_number,
        )
        self._start_turn()

    def _start_turn(self) -> None:
        current = self.current_player
        if not isinstance(current, EightBallPlayer):
            return
        self.broadcast_personal_l(
            current, "eightball-your-turn", "eightball-player-turn"
        )
        if current.is_bot:
            BotHelper.jolt_bot(current, ticks=random.randint(12, 22))
        else:
            self._update_spatial_focus(current, force=True)
        self.refresh_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    # Cue control -----------------------------------------------------------

    def _action_turn_left(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        if self.ball_in_hand:
            self._move_cue(player, -1.0, 0.0)
        else:
            self._strafe(player, -1.0)

    def _action_turn_right(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        if self.ball_in_hand:
            self._move_cue(player, 1.0, 0.0)
        else:
            self._strafe(player, 1.0)

    def _action_turn_left_fine(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        if self.ball_in_hand:
            self._move_cue(player, -0.2, 0.0)
        else:
            self._turn_view(player, 1.0)

    def _action_turn_right_fine(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        if self.ball_in_hand:
            self._move_cue(player, 0.2, 0.0)
        else:
            self._turn_view(player, -1.0)

    def _action_turn_left_medium(
        self, player: EightBallPlayer, action_id: str | None = None,
    ) -> None:
        if self.ball_in_hand:
            self._move_cue(player, -1.0, 0.0)
        else:
            self._turn_view(player, 10.0)

    def _action_turn_right_medium(
        self, player: EightBallPlayer, action_id: str | None = None,
    ) -> None:
        if self.ball_in_hand:
            self._move_cue(player, 1.0, 0.0)
        else:
            self._turn_view(player, -10.0)

    def _action_turn_left_fast(
        self, player: EightBallPlayer, action_id: str | None = None,
    ) -> None:
        if self.ball_in_hand:
            self._move_cue(player, -5.0, 0.0)
        else:
            self._turn_view(player, 45.0)

    def _action_turn_right_fast(
        self, player: EightBallPlayer, action_id: str | None = None,
    ) -> None:
        if self.ball_in_hand:
            self._move_cue(player, 5.0, 0.0)
        else:
            self._turn_view(player, -45.0)

    def _action_move_forward(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        self._walk(player, 1.0)

    def _action_move_backward(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        self._walk(player, -1.0)

    def _action_move_forward_fast(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        self._walk(player, 5.0)

    def _action_move_backward_fast(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        self._walk(player, -5.0)

    def _turn_view(self, player: EightBallPlayer, degrees: float) -> None:
        player.aim_angle = round((player.aim_angle + degrees) % 360.0, 1)
        radians = math.radians(player.aim_angle)
        self.play_sound(
            "menuclick.ogg", volume=45, audience=player,
            position=self._audio_position(math.cos(radians) * 4.0, math.sin(radians) * 4.0),
        )
        self._update_spatial_focus(player)
        self._announce_aim_feedback(player)

    def _walk(self, player: EightBallPlayer, distance: float) -> None:
        if self.ball_in_hand:
            self._move_cue(player, 0.0, distance)
            return
        radians = math.radians(player.aim_angle)
        geometry = self._table_geometry
        old_x, old_y = player.cursor_x, player.cursor_y
        player.cursor_x = round(max(
            -geometry.half_width,
            min(geometry.half_width, player.cursor_x + math.cos(radians) * distance),
        ), 1)
        player.cursor_y = round(max(
            -geometry.half_height,
            min(geometry.half_height, player.cursor_y + math.sin(radians) * distance),
        ), 1)
        moved = (player.cursor_x, player.cursor_y) != (old_x, old_y)
        self.play_sound(
            "menuclick.ogg" if moved else f"{SOUND_ROOT}/rail.ogg",
            volume=38 if moved else 60, audience=player,
        )
        self._update_spatial_focus(player)
        self._snap_to_called_pocket_if_reached(player, old_x, old_y)

    def _snap_to_called_pocket_if_reached(
        self, player: EightBallPlayer, old_x: float, old_y: float,
    ) -> None:
        """Finish pocket navigation without oscillating around its coordinate."""
        pocket = player.called_pocket
        if not 0 <= pocket < len(self._pockets):
            return
        target_x, target_y = self._pockets[pocket]
        step_x, step_y = player.cursor_x - old_x, player.cursor_y - old_y
        step_squared = step_x * step_x + step_y * step_y
        if step_squared <= 1e-9:
            return
        progress = max(0.0, min(
            1.0,
            ((target_x - old_x) * step_x + (target_y - old_y) * step_y)
            / step_squared,
        ))
        closest_x = old_x + progress * step_x
        closest_y = old_y + progress * step_y
        closest_distance = math.hypot(target_x - closest_x, target_y - closest_y)
        current_distance = math.hypot(target_x - player.cursor_x, target_y - player.cursor_y)
        if min(closest_distance, current_distance) > 0.75:
            return
        player.cursor_x, player.cursor_y = target_x, target_y
        self._announce_pocket(player, pocket, called=True)

    def _strafe(self, player: EightBallPlayer, distance: float) -> None:
        radians = math.radians(player.aim_angle)
        geometry = self._table_geometry
        old_x, old_y = player.cursor_x, player.cursor_y
        player.cursor_x = round(max(
            -geometry.half_width,
            min(geometry.half_width, player.cursor_x + math.sin(radians) * distance),
        ), 1)
        player.cursor_y = round(max(
            -geometry.half_height,
            min(geometry.half_height, player.cursor_y - math.cos(radians) * distance),
        ), 1)
        moved = (player.cursor_x, player.cursor_y) != (old_x, old_y)
        self.play_sound(
            "menuclick.ogg" if moved else f"{SOUND_ROOT}/rail.ogg",
            volume=38 if moved else 60, audience=player,
        )
        self._update_spatial_focus(player)
        self._snap_to_called_pocket_if_reached(player, old_x, old_y)

    def _action_spin_up(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        player.spin = min(2, player.spin + 1)
        self._speak_personal(player, "eightball-spin-level", spin=player.spin)
        self.play_sound("menuclick.ogg", pitch=100 + player.spin * 8, volume=55)
        self.refresh_menus()

    def _action_spin_down(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        player.spin = max(-2, player.spin - 1)
        self._speak_personal(player, "eightball-spin-level", spin=player.spin)
        self.play_sound("menuclick.ogg", pitch=100 + player.spin * 8, volume=55)
        self.refresh_menus()

    def _action_side_spin_left(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        player.side_spin = max(-2, player.side_spin - 1)
        self._speak_personal(player, "eightball-side-spin-level", spin=player.side_spin)
        self.play_sound("menuclick.ogg", pitch=85 + player.side_spin * 8, volume=55)

    def _action_side_spin_right(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        player.side_spin = min(2, player.side_spin + 1)
        self._speak_personal(player, "eightball-side-spin-level", spin=player.side_spin)
        self.play_sound("menuclick.ogg", pitch=115 + player.side_spin * 8, volume=55)

    def _action_elevation_up(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        player.cue_elevation = min(45, player.cue_elevation + 5)
        self._speak_personal(player, "eightball-elevation-level", elevation=player.cue_elevation)
        self.play_sound("menuclick.ogg", pitch=100 + player.cue_elevation, volume=55)

    def _action_elevation_down(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        player.cue_elevation = max(0, player.cue_elevation - 5)
        self._speak_personal(player, "eightball-elevation-level", elevation=player.cue_elevation)
        self.play_sound("menuclick.ogg", pitch=100 + player.cue_elevation, volume=55)

    def _action_power_up(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        player.power = min(100, player.power + 5)
        self._power_feedback(player)

    def _action_power_down(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        player.power = max(10, player.power - 5)
        self._power_feedback(player)

    def _power_feedback(self, player: EightBallPlayer) -> None:
        if not self.options.power_assistance:
            self._speak_personal(player, "eightball-power-level", power=player.power)
            self.play_sound("menuclick.ogg", volume=55, pitch=65 + player.power)
            self.refresh_menus()
            return
        has_complete_call = (
            self._ball(player.called_ball) is not None
            and 0 <= player.called_pocket < len(self._pockets)
        )
        selected_pots = (
            has_complete_call
            and self._called_ball_pots_in_preview(player, player.power)
        )
        minimum = self._minimum_direct_power(player, require_aligned=True)
        if minimum is None:
            if selected_pots:
                self._speak_personal(
                    player, "eightball-power-level-sufficient",
                    power=player.power, number=player.called_ball,
                )
            elif not has_complete_call:
                self._speak_personal(
                    player, "eightball-power-level", power=player.power,
                )
            else:
                reach_minimum = self._minimum_direct_power(
                    player, require_aligned=True, confirm_pot=False,
                )
                if reach_minimum is not None:
                    self._speak_personal(
                        player, "eightball-power-level-reach-only",
                        power=player.power, minimum=reach_minimum,
                        number=player.called_ball,
                    )
                else:
                    key = (
                        "eightball-power-level-unavailable-side-spin"
                        if player.side_spin != 0
                        else "eightball-power-level-unavailable"
                    )
                    self._speak_personal(
                        player, key, power=player.power,
                        number=player.called_ball,
                    )
        elif selected_pots:
            self._speak_personal(
                player, "eightball-power-level-sufficient",
                power=player.power, number=player.called_ball,
            )
        else:
            self._speak_personal(
                player, "eightball-power-level-insufficient",
                power=player.power, minimum=minimum, number=player.called_ball,
            )
        self.play_sound("menuclick.ogg", volume=55, pitch=65 + player.power)
        self.refresh_menus()

    # Break decisions ------------------------------------------------------

    def _break_decision_disabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | None:
        if not self.break_decision:
            return "eightball-no-break-decision"
        if player.is_spectator or self.current_player is not player:
            return "action-not-your-turn"
        if action_id == "break_option_3" and self.break_decision != "illegal":
            return "eightball-no-break-option-three"
        return None

    def _break_decision_hidden(
        self, player: Player, *, action_id: str | None = None
    ) -> Visibility:
        if not self.break_decision or self.current_player is not player:
            return Visibility.HIDDEN
        if action_id == "break_option_3" and self.break_decision != "illegal":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _set_break_decision(
        self, kind: str, offender: EightBallPlayer, chooser: EightBallPlayer
    ) -> None:
        self.break_decision = kind
        self.break_offender_id = offender.id
        self.turn_index = next(
            index for index, candidate in enumerate(self.turn_players) if candidate.id == chooser.id
        )
        self.broadcast_personal_l(
            chooser, f"eightball-break-decision-{kind}-you",
            f"eightball-break-decision-{kind}-player",
        )
        if chooser.is_bot:
            BotHelper.jolt_bot(chooser, ticks=random.randint(8, 14))
        self.refresh_menus()

    def _action_break_option_1(
        self, player: EightBallPlayer, action_id: str | None = None
    ) -> None:
        kind = self.break_decision
        self.break_decision = ""
        if kind in {"eight_legal", "eight_foul"}:
            self._spot_eight()
        if kind == "eight_foul":
            self._prepare_ball_in_hand(head_string=True)
        elif kind == "break_foul":
            cue = self._ball(0)
            if cue is None or cue.potted:
                self._prepare_ball_in_hand(head_string=True)
        elif kind == "cutthroat_illegal":
            cue = self._ball(0)
            if cue is None or cue.potted:
                self._prepare_ball_in_hand(head_string=True)
        self._start_turn()

    def _action_break_option_2(
        self, player: EightBallPlayer, action_id: str | None = None
    ) -> None:
        kind = self.break_decision
        self.break_decision = ""
        if kind == "break_foul":
            self._prepare_ball_in_hand(head_string=True)
            self._start_turn()
            return
        self._rerack_for_break(player)

    def _action_break_option_3(
        self, player: EightBallPlayer, action_id: str | None = None
    ) -> None:
        if self.break_decision != "illegal":
            return
        offender = self.get_player_by_id(self.break_offender_id)
        self.break_decision = ""
        if isinstance(offender, EightBallPlayer):
            self._rerack_for_break(offender)

    def _rerack_for_break(self, breaker: EightBallPlayer) -> None:
        self.breaker_index = next(
            index for index, candidate in enumerate(self.turn_players) if candidate.id == breaker.id
        )
        self._start_frame()

    # Called shots ---------------------------------------------------------

    def _call_disabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        reason = self._turn_disabled(player, action_id=action_id)
        if reason:
            return reason
        if self.options.play_mode == MODE_CUTTHROAT:
            return "eightball-cutthroat-no-call"
        if self.break_shot or self.ball_in_hand:
            return "eightball-call-not-available"
        return None

    def _call_pocket_disabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | None:
        reason = self._call_disabled(player, action_id=action_id)
        if reason:
            return reason
        if not isinstance(player, EightBallPlayer) or player.called_ball < 0:
            return "eightball-call-ball-first"
        return None

    def _action_call_ball(
        self, player: EightBallPlayer, action_id: str | None = None
    ) -> None:
        number = player.focused_ball
        if number < 0:
            self._speak_personal(player, "eightball-no-ball-focused")
            return
        if number not in self._legal_targets(player):
            self._speak_personal(
                player, "eightball-ball-not-legal", number=number,
                expected=", ".join(str(value) for value in sorted(self._legal_targets(player))),
            )
            return
        if player.called_ball != number:
            player.called_pocket = -1
        player.called_ball = number
        player.safety = False
        player.last_aim_feedback = ""
        self._speak_personal(player, "eightball-called-ball", number=number)

    def _locate_ball_disabled(
        self, player: Player, *, action_id: str | None = None,
    ) -> str | None:
        reason = self._turn_disabled(player, action_id=action_id)
        if reason:
            return reason
        if self.ball_in_hand:
            return "eightball-locate-unavailable-placement"
        return None

    def _locate_ball_options(self, player: Player) -> list[str]:
        return [
            str(ball.number) for ball in sorted(self.balls, key=lambda item: item.number)
            if ball.number != 0 and not ball.potted
        ]

    def _locate_ball_label(self, player: Player, value: str) -> str:
        ball = self._ball(int(value))
        if ball is None or not isinstance(player, EightBallPlayer):
            return value
        dx, dy = ball.x - player.cursor_x, ball.y - player.cursor_y
        world_angle = math.degrees(math.atan2(dy, dx))
        relative = (world_angle - player.aim_angle + 180.0) % 360.0 - 180.0
        direction = Localization.get(
            self._locale(player), self._relative_direction_key(relative),
        )
        return Localization.get(
            self._locale(player), "eightball-locate-ball-label",
            number=ball.number, direction=direction,
            distance=max(0, int(round(math.hypot(dx, dy)))),
        )

    def _locate_ball_initial(self, player: Player, options: list[str]) -> str:
        if not options or not isinstance(player, EightBallPlayer):
            return ""
        if str(player.focused_ball) in options:
            return str(player.focused_ball)
        return min(
            options,
            key=lambda value: math.hypot(
                self._ball(int(value)).x - player.cursor_x,
                self._ball(int(value)).y - player.cursor_y,
            ),
        )

    def _focus_ball_directly(self, player: EightBallPlayer, number: int) -> None:
        ball = self._ball(number)
        if ball is None or ball.potted or number == 0:
            self._speak_personal(player, "eightball-no-ball-focused")
            return
        player.cursor_x, player.cursor_y = ball.x, ball.y
        player.focused_ball = number
        self.play_sound(
            f"{SOUND_ROOT}/collision.ogg", volume=55, audience=player,
            position=self._relative_audio_position(player, ball.x, ball.y),
        )
        self._speak_personal(player, "eightball-ball-located", number=number)

    def _action_locate_ball(
        self, player: EightBallPlayer, selected: str, action_id: str,
    ) -> None:
        try:
            number = int(selected)
        except (TypeError, ValueError):
            self._speak_personal(player, "eightball-no-ball-focused")
            return
        self._focus_ball_directly(player, number)

    def _action_next_ball(
        self, player: EightBallPlayer, action_id: str | None = None,
    ) -> None:
        options = self._locate_ball_options(player)
        if not options:
            self._speak_personal(player, "eightball-no-ball-focused")
            return
        current = str(player.focused_ball)
        if current in options:
            number = int(options[(options.index(current) + 1) % len(options)])
        else:
            number = int(self._locate_ball_initial(player, options))
        self._focus_ball_directly(player, number)

    def _call_pocket_options(self, player: Player) -> list[str]:
        return [str(index) for index in range(len(self._pockets))]

    def _call_pocket_label(self, player: Player, value: str) -> str:
        pocket = int(value)
        ball = self._ball(player.called_ball) if isinstance(player, EightBallPlayer) else None
        if ball is None:
            return Localization.get(
                self._locale(player), "eightball-called-pocket-label", pocket=pocket + 1
            )
        x, y = self._pocket_aim_points[pocket]
        distance = int(round(math.hypot(x - ball.x, y - ball.y)))
        return Localization.get(
            self._locale(player), "eightball-pocket-option-distance",
            pocket=pocket + 1, distance=distance, number=ball.number,
        )

    def _call_pocket_initial(self, player: Player, options: list[str]) -> str:
        if not isinstance(player, EightBallPlayer) or not options:
            return ""
        selected = str(player.called_pocket)
        if selected in options:
            return selected
        ball = self._ball(player.called_ball)
        if ball is None:
            return options[0]
        return min(
            options,
            key=lambda value: math.hypot(
                self._pocket_aim_points[int(value)][0] - ball.x,
                self._pocket_aim_points[int(value)][1] - ball.y,
            ),
        )

    def _action_call_pocket(
        self, player: EightBallPlayer, selected: str, action_id: str
    ) -> None:
        try:
            pocket = int(selected)
        except (TypeError, ValueError):
            self._speak_personal(player, "eightball-pocket-not-valid")
            return
        if not 0 <= pocket < len(self._pockets):
            self._speak_personal(player, "eightball-pocket-not-valid")
            return
        player.called_pocket = pocket
        player.safety = False
        player.pocket_cursor = (pocket + 1) % len(self._pockets)
        player.last_aim_feedback = ""
        self._speak_personal(player, "eightball-called-pocket", pocket=pocket + 1)
        self._announce_aim_feedback(player)

    def _action_toggle_safety(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        player.safety = not player.safety
        if player.safety:
            player.called_ball = player.called_pocket = -1
            player.last_aim_feedback = ""
        self._speak_personal(
            player, "eightball-safety-declared" if player.safety else "eightball-safety-cancelled"
        )

    def _move_cue(self, player: EightBallPlayer, dx: float, dy: float) -> None:
        cue = self._ball(0)
        if cue is None:
            return
        old_x, old_y = cue.x, cue.y
        geometry = self._table_geometry
        head_string = geometry.half_width / 2.0
        minimum_x = (
            head_string + BALL_RADIUS
            if self.ball_in_hand_head_string
            else -geometry.half_width + BALL_RADIUS
        )
        cue.x = max(minimum_x, min(geometry.half_width - BALL_RADIUS, cue.x + dx))
        cue.y = max(
            -geometry.half_height + BALL_RADIUS,
            min(geometry.half_height - BALL_RADIUS, cue.y + dy),
        )
        if self._cue_overlaps_object(cue):
            cue.x, cue.y = old_x, old_y
            self._speak_personal(player, "eightball-placement-blocked")
            return
        player.cursor_x, player.cursor_y = cue.x, cue.y
        self.play_sound(
            "menuclick.ogg", volume=50,
            position=self._audio_position(cue.x, cue.y),
        )
        self._speak_personal(
            player, "eightball-placement-position", x=f"{cue.x:.1f}", y=f"{cue.y:.1f}"
        )
        self._update_spatial_focus(player)

    # Shot ------------------------------------------------------------------

    def _action_shoot(self, player: EightBallPlayer, action_id: str | None = None) -> None:
        if self.lag_active:
            if self._turn_disabled(player, action_id="shoot"):
                return
            self._take_lag_shot(player)
            return
        if self._turn_disabled(player):
            return
        if self.ball_in_hand:
            cue = self._ball(0)
            if cue is None or self._cue_overlaps_object(cue):
                self._speak_personal(player, "eightball-placement-blocked")
                return
            self.ball_in_hand = False
            self.ball_in_hand_head_string = False
            self.broadcast_personal_l(
                player, "eightball-placement-confirmed-you", "eightball-placement-confirmed-player"
            )
            self.refresh_menus()
            return
        if (
            self.options.play_mode != MODE_CUTTHROAT
            and not self.break_shot and not player.safety and (
            player.called_ball < 0 or player.called_pocket < 0
            )
        ):
            self._speak_personal(player, "eightball-call-required")
            return
        self.shot_player_id = player.id
        effective_group = player.group
        if self.table_open and player.called_ball == 8:
            if not self._active_group(GROUP_SOLIDS):
                effective_group = GROUP_SOLIDS
            elif not self._active_group(GROUP_STRIPES):
                effective_group = GROUP_STRIPES
        self.shot_group_before = effective_group
        self.shot_remaining_before = len(self._active_group(effective_group)) if effective_group else 7
        self.shot_legal_targets_before = sorted(self._legal_targets(player))
        self.shot_was_break = self.break_shot
        self.pending_shot = self._preview_shot(player, player.power)
        self._start_shot_sequence()

    def _start_shot_sequence(self) -> None:
        if self.pending_shot is None:
            return
        beats = self._physics_sequence_beats(self.pending_shot)
        beats.append(SequenceBeat(ops=[SequenceOperation.callback_op("resolve-shot")]))
        self.start_sequence(
            SHOT_SEQUENCE_ID, beats, tag="eightball-shot",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY, pause_bots=True,
        )

    @staticmethod
    def _physics_sequence_beats(result: ShotResult) -> list[SequenceBeat]:
        grouped: dict[int, list[PhysicsEvent]] = {}
        for event in result.events:
            playback_tick = int(event.tick / PHYSICS_PLAYBACK_RATE)
            grouped.setdefault(playback_tick, []).append(event)
        beats: list[SequenceBeat] = []
        event_ticks = sorted(grouped)
        playback_duration = max(1, math.ceil(result.duration_ticks / PHYSICS_PLAYBACK_RATE))
        for index, tick in enumerate(event_ticks):
            next_tick = (
                event_ticks[index + 1]
                if index + 1 < len(event_ticks)
                else max(tick + 1, playback_duration)
            )
            beats.append(SequenceBeat(
                ops=[SequenceOperation.callback_op("physics-audio", event.to_dict()) for event in grouped[tick]],
                delay_after_ticks=max(1, next_tick - tick),
            ))
        return beats

    def on_sequence_callback(self, sequence_id: str, callback_id: str, payload: dict) -> None:
        if sequence_id not in {SHOT_SEQUENCE_ID, LAG_SEQUENCE_ID}:
            return
        if callback_id == "physics-audio":
            self._play_physics_event(PhysicsEvent.from_dict(payload))
        elif callback_id == "resolve-shot":
            self._resolve_shot()
        elif callback_id == "resolve-lag":
            self._resolve_lag_shot(payload)

    def _play_physics_event(self, event: PhysicsEvent) -> None:
        sounds = {"cue": "cue.ogg", "collision": "collision.ogg", "rail": "rail.ogg", "land": "rail.ogg", "off_table": "rail.ogg", "pocket": "pocket.ogg"}
        filename = sounds.get(event.kind)
        if filename:
            for listener in self.players:
                if listener.is_spectator:
                    position = self._audio_position(event.x, event.y, event.z)
                elif isinstance(listener, EightBallPlayer):
                    position = self._relative_audio_position(listener, event.x, event.y, event.z)
                else:
                    continue
                self.play_sound(
                    f"{SOUND_ROOT}/{filename}",
                    volume=max(32, min(100, int(45 + event.strength * 55))),
                    position=position, max_instances=10, audience=listener,
                )

    def _resolve_shot(self) -> None:
        result = self.pending_shot
        shooter = self.get_player_by_id(self.shot_player_id)
        if result is None or not isinstance(shooter, EightBallPlayer):
            self.pending_shot = None
            return
        self.balls = result.balls
        self.pending_shot = None
        was_break = self.shot_was_break
        self.break_shot = False
        object_pots = [number for number in result.potted if number != 0]
        if self.options.play_mode == MODE_CUTTHROAT:
            self._resolve_cutthroat_shot(shooter, result, object_pots, was_break)
            return
        legal_targets = self._legal_targets_from_snapshot()
        if was_break:
            rail_count = len({n for n in result.rail_balls if n != 0})
            illegal_break = not object_pots and rail_count < 4
            foul = result.cue_scratch or result.first_contact < 0 or bool(result.off_table)
        else:
            illegal_break = False
            foul = (
                result.cue_scratch or result.first_contact < 0
                or result.first_contact not in legal_targets
                or bool(result.off_table)
                or (not result.rail_after_contact and not object_pots)
            )
        called_made = any(
            ball.number == shooter.called_ball
            and ball.potted
            and ball.pocket_potted == shooter.called_pocket
            for ball in result.balls
        )
        if foul:
            shooter.fouls += 1
        if was_break:
            opponent = self._opponent(shooter)
            self._announce_pots(shooter, [number for number in object_pots if number != 8])
            if 8 in object_pots or 8 in result.off_table:
                if foul and opponent:
                    self._set_break_decision("eight_foul", shooter, opponent)
                else:
                    self._set_break_decision("eight_legal", shooter, shooter)
                return
            if foul and opponent:
                self._set_break_decision("break_foul", shooter, opponent)
                return
            if illegal_break and opponent:
                self._set_break_decision("illegal", shooter, opponent)
                return
        if 8 in object_pots or 8 in result.off_table:
            self._announce_pots(shooter, object_pots)
            legal_eight = (
                not was_break and bool(self.shot_group_before)
                and self.shot_remaining_before == 0 and not foul and called_made
                and shooter.called_ball == 8
            )
            if legal_eight:
                self._win_frame(shooter)
            else:
                opponent = self._opponent(shooter)
                if opponent:
                    self.broadcast_personal_l(
                        shooter,
                        "eightball-illegal-eight-you",
                        "eightball-illegal-eight-player",
                    )
                    self._win_frame(opponent)
            return
        if self.table_open and not was_break and not foul and called_made:
            assignable = shooter.called_ball if shooter.called_ball != 8 else None
            if assignable is not None:
                shooter_group = GROUP_SOLIDS if assignable <= 7 else GROUP_STRIPES
                opponent_group = GROUP_STRIPES if shooter_group == GROUP_SOLIDS else GROUP_SOLIDS
                if self.options.play_mode == MODE_DOUBLES:
                    shooter_team = self.team_manager.get_team(shooter.name)
                    for candidate in self.get_active_players():
                        same_team = self.team_manager.get_team(candidate.name) is shooter_team
                        candidate.group = shooter_group if same_team else opponent_group
                else:
                    shooter.group = shooter_group
                    opponent = self._opponent(shooter)
                    if opponent:
                        opponent.group = opponent_group
                self.table_open = False
                self.broadcast_personal_l(
                    shooter,
                    "eightball-group-assigned-you",
                    "eightball-group-assigned-player",
                    group=lambda locale: Localization.get(locale, f"eightball-group-{shooter_group}"),
                )
        self._announce_pots(shooter, object_pots)
        if foul:
            self._announce_foul_reasons(
                shooter, result, legal_targets, object_pots, was_break=was_break
            )
        self._continue_or_pass(
            shooter, object_pots, foul, was_break=was_break, called_made=called_made
        )

    def _resolve_cutthroat_shot(
        self, shooter: EightBallPlayer, result: ShotResult,
        object_pots: list[int], was_break: bool,
    ) -> None:
        opponent_numbers = set(range(1, 16)) - set(shooter.protected_balls)
        if was_break:
            rail_count = len({number for number in result.rail_balls if number != 0})
            illegal_break = not object_pots and rail_count < 4
            foul = result.cue_scratch or result.first_contact < 0 or bool(result.off_table)
        else:
            illegal_break = False
            foul = (
                result.cue_scratch or result.first_contact < 0
                or result.first_contact not in opponent_numbers
                or bool(result.off_table)
                or (not result.rail_after_contact and not object_pots)
            )
        self._announce_pots(shooter, object_pots)
        if illegal_break:
            incoming = self._next_cutthroat_player(shooter)
            if incoming:
                self._set_break_decision("cutthroat_illegal", shooter, incoming)
            return
        if foul:
            shooter.fouls += 1
            self._announce_foul_reasons(
                shooter, result, opponent_numbers, object_pots, was_break=was_break
            )
            self._restore_cutthroat_penalty(shooter, object_pots, result.off_table)
        self._refresh_cutthroat_eliminations()
        survivors = [
            player for player in self.get_active_players()
            if player.id not in self.cutthroat_eliminated_ids
        ]
        if len(survivors) == 1:
            self._clear_call(shooter)
            self._win_frame(survivors[0])
            return
        legal_pot = bool(object_pots)
        self._clear_call(shooter)
        if legal_pot and not foul and shooter.id not in self.cutthroat_eliminated_ids:
            self.broadcast_personal_l(
                shooter,
                "eightball-continue-turn-you",
                "eightball-continue-turn-player",
            )
            self._start_turn()
            return
        if not foul:
            self.broadcast_personal_l(
                shooter, "eightball-legal-miss-you", "eightball-legal-miss-player"
            )
        self._advance_cutthroat_turn(shooter)
        if foul and result.cue_scratch:
            self._prepare_ball_in_hand(head_string=True)
        self._start_turn()

    def _restore_cutthroat_penalty(
        self, offender: EightBallPlayer, object_pots: list[int], off_table: list[int]
    ) -> None:
        # Under the published BCA Cutthroat rules, an opponent's ball made on
        # an illegal shot is spotted, every jumped object ball is spotted, and
        # the foul penalty additionally restores one previously pocketed ball
        # for every opponent who has one available.
        current_illegal = set(off_table) - {0}
        for number in object_pots:
            if number not in offender.protected_balls:
                current_illegal.add(number)
        for number in sorted(current_illegal):
            self._spot_number(number)
            self.broadcast_personal_l(
                offender,
                "eightball-cutthroat-illegal-ball-restored-you",
                "eightball-cutthroat-illegal-ball-restored-player",
                ball=number,
            )

        for player in self.get_active_players():
            if player is offender:
                continue
            candidates = sorted(
                number for number in player.protected_balls
                if number not in current_illegal
                and (ball := self._ball(number)) is not None and ball.potted
            )
            if candidates:
                self._spot_number(candidates[0])
                self.broadcast_personal_l(
                    player,
                    "eightball-cutthroat-restored-you",
                    "eightball-cutthroat-restored-player",
                    ball=candidates[0],
                )

    def _spot_number(self, number: int) -> None:
        ball = self._ball(number)
        if ball is None:
            return
        ball.potted = False
        ball.pocket_potted = -1
        ball.vx = ball.vy = ball.vz = 0.0
        ball.z = 0.0
        geometry = self._table_geometry
        foot_spot = -geometry.half_width / 2.0
        spacing = BALL_RADIUS * 2.05
        toward_foot_rail = int(
            (geometry.half_width - BALL_RADIUS + foot_spot) // spacing
        )
        positions = [
            foot_spot - offset * spacing for offset in range(toward_foot_rail + 1)
        ]
        positions.extend(
            foot_spot + offset * spacing
            for offset in range(
                1, int((geometry.half_width - foot_spot) // spacing) + 1,
            )
        )
        for x in positions:
            ball.x = x
            ball.y = 0.0
            if not any(
                other.number != number and not other.potted
                and math.hypot(other.x - ball.x, other.y - ball.y) < BALL_RADIUS * 2.01
                for other in self.balls
            ):
                return

    def _refresh_cutthroat_eliminations(self) -> None:
        previous = set(self.cutthroat_eliminated_ids)
        eliminated = []
        for player in self.get_active_players():
            alive = any(
                (ball := self._ball(number)) is not None and not ball.potted
                for number in player.protected_balls
            )
            if not alive:
                eliminated.append(player.id)
                if player.id not in previous:
                    self.cutthroat_elimination_order.append(player.id)
                    self.broadcast_personal_l(
                        player,
                        "eightball-cutthroat-eliminated-you",
                        "eightball-cutthroat-eliminated-player",
                    )
            elif player.id in previous:
                self.cutthroat_elimination_order = [
                    player_id for player_id in self.cutthroat_elimination_order
                    if player_id != player.id
                ]
                self.broadcast_personal_l(
                    player,
                    "eightball-cutthroat-reinstated-you",
                    "eightball-cutthroat-reinstated-player",
                )
        self.cutthroat_eliminated_ids = eliminated

    def _next_cutthroat_player(self, player: EightBallPlayer) -> EightBallPlayer | None:
        if not self.turn_players:
            return None
        start = self.turn_players.index(player)
        for offset in range(1, len(self.turn_players) + 1):
            candidate = self.turn_players[(start + offset) % len(self.turn_players)]
            if candidate.id not in self.cutthroat_eliminated_ids:
                return candidate
        return None

    def _advance_cutthroat_turn(self, shooter: EightBallPlayer) -> None:
        next_player = self._next_cutthroat_player(shooter)
        if next_player:
            self.turn_index = self.turn_players.index(next_player)
            self.refresh_menus()

    def _continue_or_pass(
        self, shooter: EightBallPlayer, object_pots: list[int], foul: bool, *,
        was_break: bool, called_made: bool,
    ) -> None:
        legal_pot = bool(object_pots) if was_break else called_made
        declared_safety = shooter.safety
        self._clear_call(shooter)
        if legal_pot and not foul and not declared_safety:
            self.broadcast_personal_l(
                shooter,
                "eightball-continue-turn-you",
                "eightball-continue-turn-player",
            )
            if self.options.play_mode == MODE_DOUBLES:
                self.turn_index = (self.turn_index + 2) % len(self.turn_player_ids)
                self.refresh_menus()
            self._start_turn()
            return
        if not foul and not declared_safety:
            self.broadcast_personal_l(
                shooter, "eightball-legal-miss-you", "eightball-legal-miss-player"
            )
        self.advance_turn(announce=False)
        if foul:
            self._prepare_ball_in_hand()
        self._start_turn()

    def _announce_foul_reasons(
        self, shooter: EightBallPlayer, result: ShotResult,
        legal_targets: set[int], object_pots: list[int], *, was_break: bool,
    ) -> None:
        if result.cue_scratch:
            self.broadcast_personal_l(
                shooter, "eightball-foul-scratch-you", "eightball-foul-scratch-player"
            )
        if result.first_contact < 0:
            self.broadcast_personal_l(
                shooter, "eightball-foul-no-contact-you", "eightball-foul-no-contact-player"
            )
        elif not was_break and result.first_contact not in legal_targets:
            expected = ", ".join(str(number) for number in sorted(legal_targets))
            self.broadcast_personal_l(
                shooter, "eightball-foul-wrong-first-you", "eightball-foul-wrong-first-player",
                ball=result.first_contact, expected=expected,
            )
        if result.off_table:
            self.broadcast_personal_l(
                shooter, "eightball-foul-off-table-you", "eightball-foul-off-table-player",
                balls=", ".join(str(number) for number in result.off_table),
            )
        if (
            not was_break and result.first_contact >= 0
            and not result.rail_after_contact and not object_pots
        ):
            self.broadcast_personal_l(
                shooter, "eightball-foul-no-rail-you", "eightball-foul-no-rail-player"
            )
        if self.options.play_mode != MODE_CUTTHROAT and shooter.group:
            remaining = sorted(self._legal_targets(shooter))
            self.broadcast_personal_l(
                shooter,
                "eightball-remaining-targets-you",
                "eightball-remaining-targets-player",
                balls=", ".join(str(number) for number in remaining),
            )

    @staticmethod
    def _clear_call(player: EightBallPlayer) -> None:
        player.called_ball = -1
        player.called_pocket = -1
        player.safety = False
        player.spin = 0
        player.side_spin = 0
        player.cue_elevation = 0
        player.last_aim_feedback = ""

    def _prepare_ball_in_hand(self, *, head_string: bool = False) -> None:
        geometry = self._table_geometry
        head_spot = geometry.half_width / 2.0
        cue = self._ball(0)
        if cue is None:
            cue = Ball(number=0, x=head_spot, y=0.0)
            self.balls.append(cue)
        cue.potted = False
        cue.pocket_potted = -1
        cue.vx = cue.vy = cue.vz = 0.0
        cue.z = 0.0
        safe_edge = geometry.half_width - BALL_RADIUS
        if head_string:
            positions = tuple(
                min(safe_edge, head_spot + offset)
                for offset in (5.0, 10.0, 15.0, 20.0, 2.0)
            )
        else:
            positions = (
                head_spot, head_spot + 5.0, head_spot - 5.0,
                head_spot + 10.0, head_spot - 10.0,
            )
        for x in positions:
            cue.x, cue.y = x, 0.0
            if not self._cue_overlaps_object(cue):
                break
        self.ball_in_hand = True
        self.ball_in_hand_head_string = head_string
        current = self.current_player
        if isinstance(current, EightBallPlayer):
            self.broadcast_personal_l(
                current, "eightball-ball-in-hand-you", "eightball-ball-in-hand-player"
            )

    # Frames ----------------------------------------------------------------

    def _win_frame(self, winner: EightBallPlayer) -> None:
        winners = [winner]
        if self.options.play_mode == MODE_DOUBLES:
            team = self.team_manager.get_team(winner.name)
            winners = [
                player for player in self.get_active_players()
                if self.team_manager.get_team(player.name) is team
            ]
        for player in winners:
            player.frames_won += 1
        winner_text = Localization.format_list_and(
            self.options.table_language, [player.name for player in winners]
        )
        self.play_sound("game_pig/wingame.ogg", volume=100)
        if winner.frames_won >= self.options.frames_to_win:
            self.winner_id = winner.id
            self._broadcast_winners_l(
                winners,
                "eightball-you-win-match",
                "eightball-player-wins-match",
                winner=winner_text, score=self._score_text(),
            )
            self.finish_game()
            return
        self._broadcast_winners_l(
            winners,
            "eightball-you-win-frame",
            "eightball-player-wins-frame",
            winner=winner_text, score=self._score_text(),
            target=self.options.frames_to_win,
        )
        self.frame_number += 1
        if self.options.play_mode == MODE_CUTTHROAT:
            # Published Cutthroat starts the next game in order of elimination,
            # with the previous winner last.
            ordered_ids = [
                player_id for player_id in self.cutthroat_elimination_order
                if player_id != winner.id
            ] + [winner.id]
            by_id = {player.id: player for player in self.turn_players}
            self.set_turn_players([by_id[player_id] for player_id in ordered_ids])
            self.breaker_index = 0
        else:
            self.breaker_index = (self.breaker_index + 1) % len(self.turn_players)
        self._start_frame()

    def build_game_result(self) -> GameResult:
        winners = []
        winner = self.get_player_by_id(self.winner_id)
        if isinstance(winner, EightBallPlayer):
            if self.options.play_mode == MODE_DOUBLES:
                team = self.team_manager.get_team(winner.name)
                winners = [
                    player for player in self.get_active_players()
                    if self.team_manager.get_team(player.name) is team
                ]
            else:
                winners = [winner]
        winner_names = Localization.format_list_and(
            self.options.table_language, [player.name for player in winners]
        )
        return GameResult(
            game_type=self.get_type(), timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(p.id, p.name, p.is_bot and not p.replaced_human)
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_id": self.winner_id,
                "winner": winner_names,
                "scores": {p.id: p.frames_won for p in self.get_active_players()},
                "rankings": [[player.id for player in winners]] if winners else [],
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        locale = self.options.table_language
        lines = [Localization.get(locale, "eightball-end-title")]
        lines.append(Localization.get(
            locale, "eightball-player-wins-match",
            winner=result.custom_data.get("winner", ""), score=self._score_text(),
        ))
        for player in self.get_active_players():
            lines.append(Localization.get(
                locale, "eightball-end-score", player=player.name, score=player.frames_won
            ))
        return lines

    # Bot -------------------------------------------------------------------

    def bot_think(self, player: EightBallPlayer) -> str | None:
        if player is not self.current_player or self.is_sequence_gameplay_locked():
            return None
        if self.lag_active:
            player.power = self._best_lag_power()
            return "shoot"
        if self.lag_break_choice_pending and player.id == self.lag_winner_id:
            return "lag_break_self"
        if self.break_decision:
            return "break_option_1" if self.break_decision == "eight_legal" else "break_option_2"
        if self.ball_in_hand:
            self._place_cue_for_bot()
            self.ball_in_hand = False
            self.ball_in_hand_head_string = False
        (
            player.aim_angle, player.power, player.spin,
            player.called_ball, player.called_pocket,
        ) = choose_shot_plan(
            self.balls, self._legal_targets(player), self.options.bot_difficulty,
            break_shot=self.break_shot, table_size=self.options.table_size,
        )
        return "shoot"

    def _best_lag_power(self) -> int:
        geometry = self._table_geometry
        best: tuple[float, int] | None = None
        for power in range(10, 101, 5):
            result = simulate_shot(
                [Ball(number=0, x=geometry.half_width - BALL_RADIUS, y=0.0)],
                180.0, power, table_size=self.options.table_size,
            )
            ball = result.balls[0]
            foot_contacts = sum(
                event.kind == "rail" and event.x < 0 for event in result.events
            )
            head_contacts = any(
                event.kind == "rail" and event.x > 0 for event in result.events
            )
            if foot_contacts != 1 or head_contacts or result.cue_scratch or result.off_table:
                continue
            distance = geometry.half_width - BALL_RADIUS - ball.x
            candidate = (distance, power)
            if best is None or candidate < best:
                best = candidate
        return 50 if best is None else best[1]

    def _place_cue_for_bot(self) -> None:
        cue = self._ball(0)
        if cue is None:
            return
        geometry = self._table_geometry
        head_spot = geometry.half_width / 2.0
        safe_edge = geometry.half_width - BALL_RADIUS
        if self.ball_in_hand_head_string:
            positions = tuple(
                min(safe_edge, head_spot + offset)
                for offset in (5.0, 10.0, 15.0, 20.0, 2.0)
            )
        else:
            positions = (
                head_spot, head_spot - 5.0, head_spot + 5.0,
                head_spot - 10.0, head_spot + 10.0,
            )
        for x in positions:
            for y in (0.0, -6.0, 6.0, -12.0, 12.0):
                cue.x, cue.y = x, y
                if not self._cue_overlaps_object(cue):
                    return

    # Information -----------------------------------------------------------

    def _action_probe_line(self, player: Player, action_id: str | None = None) -> None:
        shooter = player if isinstance(player, EightBallPlayer) and not player.is_spectator else self.current_player
        if not isinstance(shooter, EightBallPlayer):
            return
        hit = self._raycast(shooter.aim_angle)
        if hit is None:
            self._speak_personal(player, "eightball-probe-rail", angle=int(shooter.aim_angle))
        else:
            number, distance = hit
            self._speak_personal(
                player, "eightball-probe-ball", number=number, distance=f"{distance:.1f}"
            )
            ball = self._ball(number)
            if ball:
                self.play_sound(
                    f"{SOUND_ROOT}/collision.ogg", volume=45,
                    position=self._audio_position(ball.x, ball.y),
                )

    def _update_spatial_focus(self, player: EightBallPlayer, *, force: bool = False) -> None:
        number = self._focused_ball(player)
        changed = number != player.focused_ball
        player.focused_ball = number
        if number >= 0:
            ball = self._ball(number)
            if force or changed:
                self._speak_personal(player, "eightball-focus-ball", number=number)
            if ball:
                # Repeating the spatial collision cue lets a player walk away
                # and back to the same focused ball without the ball becoming
                # acoustically invisible merely because its id did not change.
                self.play_sound(
                    f"{SOUND_ROOT}/collision.ogg", volume=42, audience=player,
                    position=self._relative_audio_position(player, ball.x, ball.y),
                )

    def _focused_ball(self, player: EightBallPlayer) -> int:
        radians = math.radians(player.aim_angle)
        ux, uy = math.cos(radians), math.sin(radians)
        best: tuple[int, float, float] | None = None
        for ball in self.balls:
            if ball.potted or ball.number == 0:
                continue
            dx, dy = ball.x - player.cursor_x, ball.y - player.cursor_y
            distance = math.hypot(dx, dy)
            forward = dx * ux + dy * uy
            sideways = abs(dx * uy - dy * ux)
            if distance <= BALL_RADIUS * 3.0:
                score = (0, distance)
            elif forward > 0 and sideways <= BALL_RADIUS * 2.25:
                score = (1, forward)
            else:
                continue
            candidate = (score[0], score[1], ball.number)
            if best is None or candidate < best:
                best = candidate
        return -1 if best is None else best[2]

    def _announce_aim_feedback(self, player: EightBallPlayer) -> None:
        cue = self._ball(0)
        target = self._ball(player.called_ball)
        if (
            cue is None or cue.potted or target is None or target.potted
            or not 0 <= player.called_pocket < len(self._pockets)
        ):
            return
        pocket_x, pocket_y = self._pocket_aim_points[player.called_pocket]
        object_dx, object_dy = pocket_x - target.x, pocket_y - target.y
        object_length = math.hypot(object_dx, object_dy)
        if object_length <= 0:
            return
        object_ux, object_uy = object_dx / object_length, object_dy / object_length
        ghost_x = target.x - object_ux * BALL_RADIUS * 2.0
        ghost_y = target.y - object_uy * BALL_RADIUS * 2.0

        required = math.degrees(math.atan2(ghost_y - cue.y, ghost_x - cue.x)) % 360.0
        error = (required - player.aim_angle + 180.0) % 360.0 - 180.0
        if abs(error) <= 0.5001:
            # Keyboard aiming moves in whole degrees. Snap only the final
            # sub-degree remainder so the closest Ctrl+Arrow position is the
            # exact physical contact line.
            player.aim_angle = round(required, 3)
            error = 0.0
        if abs(error) >= 0.5:
            degrees = max(1, int(round(abs(error))))
            key = "eightball-aim-error-left" if error > 0 else "eightball-aim-error-right"
            self._speak_aim_once(player, key, degrees=degrees)
            return

        blocker = self._line_blocker(cue.x, cue.y, ghost_x, ghost_y, {0, target.number})
        if blocker is not None:
            self._speak_aim_once(player, "eightball-aim-blocked-cue", blocker=blocker)
            return
        blocker = self._line_blocker(
            target.x, target.y, pocket_x, pocket_y, {0, target.number}
        )
        if blocker is not None:
            self._speak_aim_once(player, "eightball-aim-blocked-object", blocker=blocker)
            return
        # Arrow navigation must stay immediate.  The former implementation
        # searched as many as nineteen full physics previews here, which made
        # Ctrl+Arrow appear to freeze exactly when the aim became aligned.
        # Report the analytical reach value while aiming; X performs the
        # authoritative pot check for the selected force.
        reach_minimum = None
        if self.options.power_assistance:
            reach_minimum = self._minimum_direct_power(
                player, require_aligned=False, confirm_pot=False,
            )
        if reach_minimum is not None:
            self._speak_aim_once(
                player, "eightball-aim-ahead-power-reach-only",
                number=player.called_ball, minimum=reach_minimum,
            )
        elif self.options.power_assistance and player.side_spin != 0:
            self._speak_aim_once(
                player, "eightball-aim-ahead-power-side-spin",
                number=player.called_ball,
            )
        elif self.options.power_assistance:
            self._speak_aim_once(
                player, "eightball-aim-ahead-power-unavailable",
                number=player.called_ball,
            )
        else:
            self._speak_aim_once(player, "eightball-aim-ahead")

    def _minimum_direct_power(
        self, player: EightBallPlayer, *, require_aligned: bool,
        confirm_pot: bool = True,
    ) -> int | None:
        """Calculate the first 5-percent power step that reaches the called pocket.

        This follows the same friction, restitution, ball size, elevation and
        pocket capture values as the authoritative simulation. It is offered
        only for an unobstructed called shot; side spin can change the object
        ball's direction and therefore deliberately disables the prediction.
        """
        cue = self._ball(0)
        target = self._ball(player.called_ball)
        if (
            cue is None or cue.potted or target is None or target.potted
            or not 0 <= player.called_pocket < len(self._pockets)
            or player.side_spin != 0
        ):
            return None
        pocket_x, pocket_y = self._pocket_aim_points[player.called_pocket]
        object_dx, object_dy = pocket_x - target.x, pocket_y - target.y
        object_length = math.hypot(object_dx, object_dy)
        if object_length <= 1e-9:
            return 10
        object_ux, object_uy = object_dx / object_length, object_dy / object_length
        ghost_x = target.x - object_ux * BALL_RADIUS * 2.0
        ghost_y = target.y - object_uy * BALL_RADIUS * 2.0
        cue_dx, cue_dy = ghost_x - cue.x, ghost_y - cue.y
        cue_distance = math.hypot(cue_dx, cue_dy)
        if cue_distance <= 1e-9:
            return None
        cue_ux, cue_uy = cue_dx / cue_distance, cue_dy / cue_distance
        required = math.degrees(math.atan2(cue_dy, cue_dx)) % 360.0
        error = (required - player.aim_angle + 180.0) % 360.0 - 180.0
        if require_aligned and abs(error) >= 0.5:
            return None
        if self._line_blocker(cue.x, cue.y, ghost_x, ghost_y, {0, target.number}) is not None:
            return None
        if self._line_blocker(
            target.x, target.y, pocket_x, pocket_y, {0, target.number}
        ) is not None:
            return None
        transfer = (
            (1.0 + BALL_RESTITUTION) * 0.5
            * max(0.0, cue_ux * object_ux + cue_uy * object_uy)
        )
        if transfer <= 1e-9:
            return None
        friction = FRICTION_PER_60HZ ** (60.0 / SIMULATION_HZ)
        speed_loss_per_unit = (1.0 - friction) * SIMULATION_HZ
        required_travel = object_length
        elevation = math.radians(max(0.0, min(45.0, player.cue_elevation)))
        calculated_minimum: int | None = None
        for power in range(10, 101, 5):
            cue_speed = shot_speed(power) * math.cos(elevation)
            speed_at_contact = max(
                0.0, cue_speed - speed_loss_per_unit * cue_distance
            )
            object_speed = speed_at_contact * transfer
            available_travel = max(
                0.0, (object_speed - STOP_SPEED) / speed_loss_per_unit
            )
            if available_travel >= required_travel:
                calculated_minimum = power
                break
        if calculated_minimum is None:
            return None
        if not confirm_pot:
            return calculated_minimum
        # This authoritative search runs only when the player changes force,
        # never from an arrow-key aiming action.  Starting at the analytical
        # reach threshold normally needs one or two cached two-ball previews,
        # while still returning the first real five-percent step that pots.
        for power in range(calculated_minimum, 101, 5):
            if self._called_ball_pots_in_direct_preview(player, power):
                return power
        return None

    def _shot_preview_key(self, player: EightBallPlayer, power: int) -> str:
        ball_state = tuple(
            (
                ball.number, round(ball.x, 5), round(ball.y, 5), round(ball.z, 5),
                ball.potted, ball.pocket_potted,
            )
            for ball in self.balls
        )
        return repr((
            ball_state, round(player.aim_angle, 3), power, player.spin,
            player.side_spin, player.cue_elevation, self.options.table_size,
        ))

    def _preview_shot(self, player: EightBallPlayer, power: int) -> ShotResult:
        key = self._shot_preview_key(player, power)
        cached = self.shot_preview_cache.get(key)
        if cached is not None:
            return cached
        if len(self.shot_preview_cache) >= 64:
            self.shot_preview_cache.clear()
        result = simulate_shot(
            self.balls, player.aim_angle, power, player.spin,
            player.side_spin, player.cue_elevation,
            table_size=self.options.table_size,
        )
        self.shot_preview_cache[key] = result
        return result

    def _called_ball_pots_in_preview(
        self, player: EightBallPlayer, power: int,
    ) -> bool:
        result = self._preview_shot(player, power)
        return any(
            ball.number == player.called_ball
            and ball.potted
            and ball.pocket_potted == player.called_pocket
            for ball in result.balls
        )

    def _called_ball_pots_in_direct_preview(
        self, player: EightBallPlayer, power: int,
    ) -> bool:
        cue = self._ball(0)
        target = self._ball(player.called_ball)
        if cue is None or target is None:
            return False
        key = "direct:" + repr((
            cue.to_dict(), target.to_dict(), round(player.aim_angle, 3), power,
            player.spin, player.side_spin, player.cue_elevation,
            player.called_pocket, self.options.table_size,
        ))
        result = self.shot_preview_cache.get(key)
        if result is None:
            if len(self.shot_preview_cache) >= 64:
                self.shot_preview_cache.clear()
            result = simulate_shot(
                [cue, target], player.aim_angle, power, player.spin,
                player.side_spin, player.cue_elevation,
                table_size=self.options.table_size,
            )
            self.shot_preview_cache[key] = result
        return any(
            ball.number == player.called_ball
            and ball.potted
            and ball.pocket_potted == player.called_pocket
            for ball in result.balls
        )

    def _speak_aim_once(self, player: EightBallPlayer, key: str, **kwargs) -> None:
        signature = f"{key}:{sorted(kwargs.items())}"
        if signature == player.last_aim_feedback:
            return
        player.last_aim_feedback = signature
        self._speak_personal(player, key, **kwargs)

    def _line_blocker(
        self, start_x: float, start_y: float, end_x: float, end_y: float,
        ignored: set[int],
    ) -> int | None:
        dx, dy = end_x - start_x, end_y - start_y
        length_squared = dx * dx + dy * dy
        if length_squared <= 0:
            return None
        nearest: tuple[float, int] | None = None
        for ball in self.balls:
            if ball.potted or ball.number in ignored:
                continue
            progress = ((ball.x - start_x) * dx + (ball.y - start_y) * dy) / length_squared
            if not 0.0 < progress < 1.0:
                continue
            closest_x = start_x + progress * dx
            closest_y = start_y + progress * dy
            if math.hypot(ball.x - closest_x, ball.y - closest_y) < BALL_RADIUS * 2.0:
                candidate = (progress, ball.number)
                if nearest is None or candidate < nearest:
                    nearest = candidate
        return None if nearest is None else nearest[1]

    def _action_pockets_info(self, player: Player, action_id: str | None = None) -> None:
        navigator = player if isinstance(player, EightBallPlayer) else self.current_player
        if not isinstance(navigator, EightBallPlayer):
            return
        if navigator.called_pocket >= 0:
            pocket = navigator.called_pocket
            self._announce_pocket(navigator, pocket, audience=player, called=True)
            return
        if navigator.pocket_cursor < 0:
            navigator.pocket_cursor = min(
                range(len(self._pockets)),
                key=lambda index: math.hypot(
                    self._pockets[index][0] - navigator.cursor_x,
                    self._pockets[index][1] - navigator.cursor_y,
                ),
            )
        pocket = navigator.pocket_cursor
        navigator.pocket_cursor = (pocket + 1) % len(self._pockets)
        self._announce_pocket(navigator, pocket, audience=player)

    def _announce_pocket(
        self, navigator: EightBallPlayer, pocket: int, *,
        audience: Player | None = None, called: bool = False,
    ) -> None:
        listener = audience or navigator
        x, y = self._pockets[pocket]
        distance = math.hypot(x - navigator.cursor_x, y - navigator.cursor_y)
        if distance <= 1e-6:
            self._speak_personal(
                listener,
                "eightball-called-pocket-here" if called else "eightball-pocket-reading-here",
                pocket=pocket + 1,
            )
            self.play_sound(
                f"{SOUND_ROOT}/pocket.ogg", volume=48, audience=listener,
                position=self._relative_audio_position(navigator, x, y),
            )
            return
        world_angle = math.degrees(math.atan2(y - navigator.cursor_y, x - navigator.cursor_x))
        relative = (world_angle - navigator.aim_angle + 180.0) % 360.0 - 180.0
        direction_key = self._relative_direction_key(relative)
        if distance < 1.0:
            message_key = (
                "eightball-called-pocket-near" if called else "eightball-pocket-reading-near"
            )
        else:
            message_key = (
                "eightball-called-pocket-simple" if called else "eightball-pocket-reading-simple"
            )
        self._speak_personal(
            listener,
            message_key,
            pocket=pocket + 1,
            direction=Localization.get(self._locale(listener), direction_key),
            distance=max(1, int(round(distance))),
        )
        self.play_sound(
            f"{SOUND_ROOT}/pocket.ogg", volume=48, audience=listener,
            position=self._relative_audio_position(navigator, x, y),
        )

    @staticmethod
    def _relative_direction_key(relative_angle: float) -> str:
        directions = (
            "eightball-direction-front",
            "eightball-direction-front-left",
            "eightball-direction-left",
            "eightball-direction-back-left",
            "eightball-direction-back",
            "eightball-direction-back-right",
            "eightball-direction-right",
            "eightball-direction-front-right",
        )
        return directions[int((relative_angle + 22.5) // 45.0) % 8]

    def _action_table_overview(self, player: Player, action_id: str | None = None) -> None:
        cue = self._ball(0)
        if cue:
            self._speak_personal(
                player, "eightball-table-overview", x=f"{cue.x:.1f}", y=f"{cue.y:.1f}",
                solids=len(self._active_group(GROUP_SOLIDS)),
                stripes=len(self._active_group(GROUP_STRIPES)), score=self._score_text(),
            )

    def _action_cue_status(self, player: Player, action_id: str | None = None) -> None:
        shooter = player if isinstance(player, EightBallPlayer) and not player.is_spectator else self.current_player
        if isinstance(shooter, EightBallPlayer):
            self._speak_personal(
                player, "eightball-cue-status", angle=f"{shooter.aim_angle:.1f}",
                power=shooter.power, spin=shooter.spin, side_spin=shooter.side_spin,
                elevation=shooter.cue_elevation,
                called_ball=shooter.called_ball if shooter.called_ball >= 0 else "--",
                called_pocket=shooter.called_pocket + 1 if shooter.called_pocket >= 0 else "--",
                x=f"{shooter.cursor_x:.1f}", y=f"{shooter.cursor_y:.1f}",
            )

    # Helpers ---------------------------------------------------------------

    def _ball(self, number: int) -> Ball | None:
        return next((ball for ball in self.balls if ball.number == number), None)

    def _active_group(self, group: str) -> list[Ball]:
        return [ball for ball in self.balls if not ball.potted and self._number_group(ball.number) == group]

    @staticmethod
    def _number_group(number: int) -> str:
        if 1 <= number <= 7:
            return GROUP_SOLIDS
        if 9 <= number <= 15:
            return GROUP_STRIPES
        return "eight" if number == 8 else "cue"

    def _opponent(self, player: EightBallPlayer) -> EightBallPlayer | None:
        if self.options.play_mode == MODE_DOUBLES:
            team = self.team_manager.get_team(player.name)
            return next(
                (
                    other for other in self.turn_players
                    if self.team_manager.get_team(other.name) is not team
                ),
                None,
            )
        return next((other for other in self.get_active_players() if other.id != player.id), None)

    def _legal_targets(self, player: EightBallPlayer) -> set[int]:
        if self.options.play_mode == MODE_CUTTHROAT:
            return {
                ball.number for ball in self.balls
                if not ball.potted and ball.number != 0
                and ball.number not in player.protected_balls
            }
        if self.table_open or not player.group:
            targets = {ball.number for ball in self.balls if not ball.potted and ball.number not in (0, 8)}
            if not self._active_group(GROUP_SOLIDS) or not self._active_group(GROUP_STRIPES):
                eight = self._ball(8)
                if eight and not eight.potted:
                    targets.add(8)
            return targets
        remaining = self._active_group(player.group)
        return {ball.number for ball in remaining} if remaining else {8}

    def _legal_targets_from_snapshot(self) -> set[int]:
        if self.shot_legal_targets_before:
            return set(self.shot_legal_targets_before)
        if self.shot_group_before and self.shot_remaining_before == 0:
            return {8}
        if not self.shot_group_before or self.table_open:
            return {number for number in range(1, 16) if number != 8}
        return set(range(1, 8)) if self.shot_group_before == GROUP_SOLIDS else set(range(9, 16))

    def _cue_overlaps_object(self, cue: Ball) -> bool:
        return any(
            not ball.potted and ball.number != 0
            and math.hypot(ball.x - cue.x, ball.y - cue.y) < BALL_RADIUS * 2.05
            for ball in self.balls
        )

    def _raycast(self, angle: float) -> tuple[int, float] | None:
        cue = self._ball(0)
        if cue is None:
            return None
        radians = math.radians(angle)
        ux, uy = math.cos(radians), math.sin(radians)
        best: tuple[int, float] | None = None
        for ball in self.balls:
            if ball.potted or ball.number == 0:
                continue
            dx, dy = ball.x - cue.x, ball.y - cue.y
            forward = dx * ux + dy * uy
            sideways = abs(dx * uy - dy * ux)
            if forward > 0 and sideways <= BALL_RADIUS * 2.0 and (best is None or forward < best[1]):
                best = (ball.number, forward)
        return best

    def _spot_eight(self) -> None:
        eight = self._ball(8)
        if eight is None:
            return
        eight.potted = False
        eight.pocket_potted = -1
        eight.z = 0.0
        eight.vx = eight.vy = eight.vz = 0.0
        foot_spot = -self._table_geometry.half_width / 2.0
        for x in (foot_spot + offset for offset in (0.0, 5.0, 10.0, 15.0, 20.0, 25.0)):
            eight.x, eight.y = x, 0.0
            if not any(
                ball.number != 8 and not ball.potted
                and math.hypot(ball.x - x, ball.y) < BALL_RADIUS * 2.05
                for ball in self.balls
            ):
                break

    def _announce_pots(self, shooter: EightBallPlayer, numbers: list[int]) -> None:
        if numbers:
            shooter.potted_balls.extend(number for number in numbers if number not in shooter.potted_balls)
            self.broadcast_personal_l(
                shooter,
                "eightball-balls-potted-you",
                "eightball-balls-potted-player",
                buffer="game",
                balls=", ".join(map(str, numbers)),
            )

    def _score_text(self) -> str:
        if self.options.play_mode == MODE_DOUBLES and self.team_manager.teams:
            return " - ".join(
                f"{' / '.join(team.members)}: "
                f"{next((player.frames_won for player in self.get_active_players() if player.name in team.members), 0)}"
                for team in sorted(self.team_manager.teams, key=lambda item: item.index)
            )
        return " - ".join(f"{player.name}: {player.frames_won}" for player in self.get_active_players())

    def _speak_personal(self, player: Player, key: str, **kwargs) -> None:
        user = self.get_user(player)
        if user:
            user.speak(
                Localization.get(self.options.table_language, key, **kwargs),
                buffer="game",
            )

    @staticmethod
    def _audio_position(x: float, y: float, z: float = 0.0) -> tuple[float, float, float]:
        return (round(x / 5.0, 3), round(y / 5.0, 3), round(z, 3))

    def _relative_audio_position(
        self, player: EightBallPlayer, x: float, y: float, z: float = 0.0
    ) -> tuple[float, float, float]:
        dx, dy = x - player.cursor_x, y - player.cursor_y
        radians = math.radians(player.aim_angle)
        # The client listener is fixed facing +Y. Rotate world coordinates into
        # the player's current first-person frame so turning also turns the
        # complete sound field instead of merely changing a numeric angle.
        local_x = dx * math.sin(radians) - dy * math.cos(radians)
        local_y = dx * math.cos(radians) + dy * math.sin(radians)
        return self._audio_position(local_x, local_y, z)
