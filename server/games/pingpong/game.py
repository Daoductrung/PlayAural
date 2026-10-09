"""Audio-first, server-authoritative table tennis for PlayAural."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import (
    MenuOption,
    TeamModeOption,
    get_option_meta,
    option_field,
)
from ...game_utils.stats_helpers import (
    RATING_COMPETITORS_KEY,
    rating_competitors_from_scores,
)
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem


TICKS_PER_SECOND = 20
TABLE_WIDTH_METERS = 1.525
TABLE_LENGTH_METERS = 2.74
NET_HEIGHT_METERS = 0.1525

PHASE_SERVE = "serve"
PHASE_FLIGHT = "flight"
PHASE_AIM_RETURN = "aim_return"
PHASE_POINT_PAUSE = "point_pause"

BEST_OF_CHOICES = ["1", "3", "5", "7"]
BEST_OF_LABELS = {
    "1": "pingpong-best-of-one",
    "3": "pingpong-best-of-three",
    "5": "pingpong-best-of-five",
    "7": "pingpong-best-of-seven",
}
PACE_CHOICES = ["relaxed", "standard", "fast"]
PACE_LABELS = {
    "relaxed": "pingpong-pace-relaxed",
    "standard": "pingpong-pace-standard",
    "fast": "pingpong-pace-fast",
}
PACE_BASE_TICKS = {"relaxed": 23, "standard": 18, "fast": 14}
PACE_RETURN_TICKS = {"relaxed": 26, "standard": 22, "fast": 18}
PACE_AIM_TICKS = {"relaxed": 10, "standard": 9, "fast": 8}
BOT_DIFFICULTY_CHOICES = ["easy", "normal", "hard"]
BOT_DIFFICULTY_LABELS = {
    "easy": "pingpong-bot-easy",
    "normal": "pingpong-bot-normal",
    "hard": "pingpong-bot-hard",
}
BOT_ACCURACY = {"easy": 0.70, "normal": 0.84, "hard": 0.94}
TABLE_LANGUAGES = ["en", "es", "pt", "vi", "fa"]

SIDE_LIMIT = 0.88
DEPTH_MIN = 0.0
DEPTH_MAX = 1.0
LANE_X = 0.55
POINT_PAUSE_TICKS = 8
SERVE_BOT_DELAY = 14
PADDLE_SPEED_PER_TICK = 0.12
PADDLE_REACH = 0.24
PADDLE_ASSET = "game_pingpong/paddle.ogg"
TABLE_ASSET = "game_pingpong/table.ogg"
NET_ASSET = "game_pingpong/net.ogg"


@dataclass
class PingPongPlayer(Player):
    """Per-player match and court state."""

    points: int = 0
    games_won: int = 0
    court_x: float = 0.0
    paddle_target_x: float = 0.0
    court_depth: float = 0.48
    response_lane: str = ""
    shot_lane: str = "center"
    successful_returns: int = 0
    missed_returns: int = 0
    longest_rally: int = 0


@dataclass
class PingPongOptions(GameOptions):
    """Host-configurable table tennis options."""

    team_mode: str = option_field(
        TeamModeOption(
            default="individual",
            value_key="mode",
            choices=["individual", "2v2"],
            label="game-set-team-mode",
            prompt="game-select-team-mode",
            change_msg="game-option-changed-team",
            description="pingpong-desc-team-mode",
        )
    )
    best_of: str = option_field(
        MenuOption(
            default="3",
            choices=BEST_OF_CHOICES,
            choice_labels=BEST_OF_LABELS,
            value_key="format",
            label="pingpong-set-best-of",
            prompt="pingpong-select-best-of",
            change_msg="pingpong-option-changed-best-of",
            description="pingpong-desc-best-of",
        )
    )
    pace: str = option_field(
        MenuOption(
            default="standard",
            choices=PACE_CHOICES,
            choice_labels=PACE_LABELS,
            value_key="pace",
            label="pingpong-set-pace",
            prompt="pingpong-select-pace",
            change_msg="pingpong-option-changed-pace",
            description="pingpong-desc-pace",
        )
    )
    bot_difficulty: str = option_field(
        MenuOption(
            default="normal",
            choices=BOT_DIFFICULTY_CHOICES,
            choice_labels=BOT_DIFFICULTY_LABELS,
            value_key="difficulty",
            label="pingpong-set-bot-difficulty",
            prompt="pingpong-select-bot-difficulty",
            change_msg="pingpong-option-changed-bot-difficulty",
            description="pingpong-desc-bot-difficulty",
        )
    )
    table_language: str = option_field(
        MenuOption(
            default="en",
            choices=TABLE_LANGUAGES,
            choice_labels={
                "en": "pingpong-language-en",
                "es": "pingpong-language-es",
                "pt": "pingpong-language-pt",
                "vi": "pingpong-language-vi",
                "fa": "pingpong-language-fa",
            },
            value_key="language",
            label="pingpong-set-language",
            prompt="pingpong-select-language",
            change_msg="pingpong-option-changed-language",
            description="pingpong-desc-language",
        )
    )

    def create_options_action_set(
        self, game: "PingPongGame", player: PingPongPlayer
    ) -> ActionSet:
        action_set = ActionSet(name="options")
        self._populate_action_set(action_set, game, player, self.table_language)
        return action_set

    def update_options_labels(self, game: "PingPongGame") -> None:
        for player in game.players:
            action_set = game.get_action_set(player, "options")
            if action_set is None:
                game.add_action_set(player, self.create_options_action_set(game, player))
                continue
            action_set._actions.clear()
            action_set._order.clear()
            self._populate_action_set(
                action_set, game, player, self.table_language
            )


@dataclass
@register_game
class PingPongGame(Game):
    """Accessible singles and doubles table tennis with spatial timed returns."""

    players: list[PingPongPlayer] = field(default_factory=list)
    options: PingPongOptions = field(default_factory=PingPongOptions)
    score_unit_key = "game-score-unit-games"

    phase: str = PHASE_SERVE
    initial_server_index: int = 0
    serving_player_id: str = ""
    hitting_player_id: str = ""
    receiving_player_id: str = ""
    point_pause_ticks: int = 0
    game_number: int = 1
    rally_count: int = 0
    match_longest_rally: int = 0

    ball_target_x: float = 0.0
    ball_target_depth: float = 0.5
    ball_launch_x: float = 0.0
    ball_total_ticks: int = 0
    ball_ticks_remaining: int = 0
    ball_bounce_tick: int = 0
    ball_bounced: bool = False
    return_window_ticks: int = 0
    ball_generation: int = 0
    bot_serve_ticks: int = 0
    bot_swing_tick: int = -1
    bot_reaction_ticks: int = 0
    bot_planned_lane: str = ""
    serve_bounce_ticks: int = 0
    aim_return_ticks: int = 0
    pending_return_hitter_id: str = ""
    pending_return_receiver_id: str = ""
    pending_return_depth: float = 0.5
    pending_return_timing: int = 0
    bot_aim_x: float = 0.0
    bot_aim_depth: float = 0.5
    winner_id: str = ""
    winner_team_index: int = -1
    service_rotation_ids: list[str] = field(default_factory=list)
    ends_swapped: bool = False
    deciding_end_changed: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "Table Tennis"

    @classmethod
    def get_type(cls) -> str:
        return "pingpong"

    @classmethod
    def get_category(cls) -> str:
        return "arcade"

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
    ) -> PingPongPlayer:
        return PingPongPlayer(id=player_id, name=name, is_bot=is_bot)

    @staticmethod
    def _language_from_playaural(locale: str) -> str:
        language = str(locale or "en").lower().replace("_", "-").split("-", 1)[0]
        return language if language in TABLE_LANGUAGES else "en"

    def initialize_lobby(self, host_name: str, host_user) -> None:
        self.options.table_language = self._language_from_playaural(host_user.locale)
        super().initialize_lobby(host_name, host_user)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = list(super().prestart_validate())
        active = self._active_pingpong_players()
        team_mode_error = self._validate_team_mode(self.options.team_mode)
        if team_mode_error:
            errors.append(team_mode_error)
        if self.options.team_mode == "individual" and len(active) != 2:
            errors.append(("pingpong-error-singles-players", {"count": len(active)}))
        if self.options.team_mode == "2v2" and len(active) != 4:
            errors.append(("pingpong-error-doubles-players", {"count": len(active)}))
        if self.options.best_of not in BEST_OF_CHOICES:
            errors.append("pingpong-error-best-of")
        if self.options.pace not in PACE_CHOICES:
            errors.append("pingpong-error-pace")
        if self.options.bot_difficulty not in BOT_DIFFICULTY_CHOICES:
            errors.append("pingpong-error-bot-difficulty")
        if self.options.table_language not in TABLE_LANGUAGES:
            errors.append("pingpong-error-language")
        return errors

    def _active_pingpong_players(self) -> list[PingPongPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, PingPongPlayer)
        ]

    def _locale(self, player: Player) -> str:
        return self.options.table_language

    def broadcast_l(
        self,
        message_id: str,
        buffer: str = "game",
        exclude: Player | None = None,
        **kwargs,
    ) -> None:
        locale = self.options.table_language
        resolved = self._resolve_broadcast_kwargs(locale, kwargs)
        self.broadcast(
            Localization.get(locale, message_id, **resolved),
            buffer=buffer,
            exclude=exclude,
        )

    def _broadcast_option_change(self, meta, value) -> None:
        locale = self.options.table_language
        kwargs = meta.get_change_kwargs_localized(value, locale)
        self.broadcast(
            Localization.get(locale, meta.change_msg, **kwargs),
            buffer="system",
        )

    def _handle_option_change(self, option_name: str, value: str) -> None:
        previous_language = self.options.table_language
        super()._handle_option_change(option_name, value)
        if (
            option_name == "table_language"
            and self.options.table_language != previous_language
        ):
            self._rebuild_localized_controls()

    def _option_description_text(
        self, player: Player, menu_item_id: str
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
        self, action: Action, player: Player, user, options: list[str]
    ):
        items = super()._build_action_menu_input_items(
            action, player, user, options
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
                    str(item.id), self.options.table_language
                )
            )
        return items

    def _rebuild_localized_controls(self) -> None:
        self._keybinds.clear()
        self.setup_keybinds()
        for player in self.players:
            self.player_action_sets[player.id] = []
            self.setup_player_actions(player)
        self.refresh_menus()

    def _refresh_realtime_touch_menus(self) -> None:
        """Avoid rebuilding desktop menus in the middle of a live rally."""
        for player in self.players:
            if self.is_touch_client(self.get_user(player)):
                self.refresh_menus(player)

    def _opponent(self, player: PingPongPlayer) -> PingPongPlayer | None:
        player_team = self._team_manager.get_team(player.name)
        return next(
            (
                candidate
                for candidate in self._active_pingpong_players()
                if candidate.id != player.id
                and (
                    player_team is None
                    or self._team_manager.get_team(candidate.name) is not player_team
                )
            ),
            None,
        )

    def _player(self, player_id: str) -> PingPongPlayer | None:
        player = self.get_player_by_id(player_id)
        return player if isinstance(player, PingPongPlayer) else None

    def _sets_needed(self) -> int:
        return int(self.options.best_of) // 2 + 1

    def _team_for_player(self, player: PingPongPlayer):
        return self._team_manager.get_team(player.name)

    def _team_players(self, team_index: int) -> list[PingPongPlayer]:
        return [
            player
            for player in self._active_pingpong_players()
            if (team := self._team_for_player(player)) and team.index == team_index
        ]

    def _team_points(self, team_index: int) -> int:
        players = self._team_players(team_index)
        return players[0].points if players else 0

    def _set_team_points(self, team_index: int, points: int) -> None:
        for player in self._team_players(team_index):
            player.points = points

    def _set_team_games(self, team_index: int, games: int) -> None:
        for player in self._team_players(team_index):
            player.games_won = games

    def _other_team_player(self, player: PingPongPlayer) -> PingPongPlayer | None:
        team = self._team_for_player(player)
        if not team:
            return None
        other_team = next(
            (candidate for candidate in self._team_manager.teams if candidate.index != team.index),
            None,
        )
        if not other_team:
            return None
        preferred = self._player(self.hitting_player_id)
        if preferred and preferred.name in other_team.members:
            return preferred
        return next(
            (
                candidate
                for candidate in self._active_pingpong_players()
                if candidate.name in other_team.members
            ),
            None,
        )

    def _next_rotation_player(self, player: PingPongPlayer) -> PingPongPlayer | None:
        if player.id not in self.service_rotation_ids:
            return self._opponent(player)
        index = self.service_rotation_ids.index(player.id)
        return self._player(
            self.service_rotation_ids[(index + 1) % len(self.service_rotation_ids)]
        )

    def _sync_scores(self) -> None:
        for team in self._team_manager.teams:
            players = self._team_players(team.index)
            team.total_score = players[0].games_won if players else 0

    def _set_required_player(self, player: PingPongPlayer | None) -> None:
        if player and player.id in self.turn_player_ids:
            self.turn_index = self.turn_player_ids.index(player.id)

    # ------------------------------------------------------------------
    # Actions and keybinds
    # ------------------------------------------------------------------

    def _is_play_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return (
            Visibility.VISIBLE
            if self.is_touch_client(self.get_user(player))
            else Visibility.HIDDEN
        )

    def _is_move_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_serve_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, PingPongPlayer):
            return "pingpong-error-not-player"
        if self.phase == PHASE_POINT_PAUSE:
            return None
        if self.phase != PHASE_SERVE:
            return "pingpong-serve-between-points"
        if player.id != self.serving_player_id:
            return None
        return None

    def _is_hit_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, PingPongPlayer):
            return "pingpong-error-not-player"
        if self.phase == PHASE_SERVE:
            return "pingpong-press-c-to-serve"
        if self.phase == PHASE_FLIGHT and player.id != self.receiving_player_id:
            return None
        if self.phase == PHASE_POINT_PAUSE:
            return None
        return None

    def create_turn_action_set(self, player: PingPongPlayer) -> ActionSet:
        locale = self._locale(player)
        show_in_menu = self.is_touch_client(self.get_user(player))
        action_set = ActionSet(name="turn")
        for action_id, label_key, handler in (
            ("aim_left", "pingpong-aim-left", "_action_aim_left"),
            ("aim_right", "pingpong-aim-right", "_action_aim_right"),
            ("aim_center", "pingpong-aim-center", "_action_aim_center"),
        ):
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(locale, label_key),
                    handler=handler,
                    is_enabled="_is_move_enabled",
                    is_hidden="_is_play_action_hidden",
                    show_in_actions_menu=show_in_menu,
                )
            )
        action_set.add(
            Action(
                id="serve_ball",
                label=Localization.get(locale, "pingpong-serve-ball"),
                handler="_action_serve_ball",
                is_enabled="_is_serve_enabled",
                is_hidden="_is_play_action_hidden",
                show_in_actions_menu=show_in_menu,
            )
        )
        action_set.add(
            Action(
                id="hit_ball",
                label=Localization.get(locale, "pingpong-hit-ball"),
                handler="_action_hit_ball",
                is_enabled="_is_hit_enabled",
                is_hidden="_is_play_action_hidden",
                show_in_actions_menu=show_in_menu,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        for action_id, label_key, handler, spectators in (
            (
                "read_position",
                "pingpong-read-position",
                "_action_read_position",
                False,
            ),
            ("read_match", "pingpong-read-match", "_action_read_match", True),
        ):
            action_set.add(
                Action(
                    id=action_id,
                    label=Localization.get(self._locale(player), label_key),
                    handler=handler,
                    is_enabled="_is_info_enabled",
                    is_hidden="_is_info_hidden",
                    include_spectators=spectators,
                )
            )
        user = self.get_user(player)
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                ["read_position", "read_match", "check_scores", "whose_turn", "whos_at_table"],
            )
        return action_set

    def _is_info_enabled(self, player: Player) -> str | None:
        return None if self.status == "playing" else "action-not-playing"

    def _is_info_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return (
            Visibility.VISIBLE
            if self.is_touch_client(self.get_user(player))
            else Visibility.HIDDEN
        )

    def setup_keybinds(self) -> None:
        self._keybinds.clear()
        super().setup_keybinds()
        bindings = (
            ("left", "pingpong-aim-left", "aim_left", False),
            ("right", "pingpong-aim-right", "aim_right", False),
            ("up", "pingpong-aim-center", "aim_center", False),
            ("c", "pingpong-serve-ball", "serve_ball", False),
            ("x", "pingpong-hit-ball", "hit_ball", False),
            ("p", "pingpong-read-position", "read_position", False),
            ("m", "pingpong-read-match", "read_match", True),
        )
        for key, label_key, action_id, spectators in bindings:
            self.define_keybind(
                key,
                Localization.get(self.options.table_language, label_key),
                [action_id],
                state=KeybindState.ACTIVE,
                include_spectators=spectators,
            )

    # ------------------------------------------------------------------
    # Movement and information
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    def _choose_response_lane(self, player: Player, lane: str) -> None:
        if not isinstance(player, PingPongPlayer):
            return
        if self.phase == PHASE_AIM_RETURN and player.id == self.pending_return_hitter_id:
            self._finalize_aimed_return(player, lane)
            return
        player.response_lane = lane
        player.paddle_target_x = {
            "left": -LANE_X,
            "center": 0.0,
            "right": LANE_X,
        }[lane]
        if self.phase == PHASE_SERVE and player.id == self.serving_player_id:
            player.shot_lane = lane

    def _move_paddles(self) -> None:
        """Move every paddle through the court instead of teleporting it."""
        for player in self._active_pingpong_players():
            delta = player.paddle_target_x - player.court_x
            if abs(delta) <= PADDLE_SPEED_PER_TICK:
                player.court_x = player.paddle_target_x
            elif delta:
                player.court_x += PADDLE_SPEED_PER_TICK if delta > 0 else -PADDLE_SPEED_PER_TICK
            player.court_x = round(self._clamp(player.court_x, -SIDE_LIMIT, SIDE_LIMIT), 3)

    def _action_aim_left(self, player: Player, action_id: str) -> None:
        self._choose_response_lane(player, "left")

    def _action_aim_right(self, player: Player, action_id: str) -> None:
        self._choose_response_lane(player, "right")

    def _action_aim_center(self, player: Player, action_id: str) -> None:
        self._choose_response_lane(player, "center")

    def _horizontal_key(self, x: float) -> str:
        if x < -0.18:
            return "pingpong-position-left"
        if x > 0.18:
            return "pingpong-position-right"
        return "pingpong-position-center"

    def _depth_key(self, depth: float) -> str:
        if depth < 0.30:
            return "pingpong-position-close"
        if depth > 0.70:
            return "pingpong-position-far"
        return "pingpong-position-middle"

    def _position_text(self, locale: str, player: PingPongPlayer) -> str:
        return Localization.get(
            locale,
            "pingpong-position-summary",
            horizontal=Localization.get(locale, self._horizontal_key(player.court_x)),
        )

    def _action_read_position(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if isinstance(player, PingPongPlayer):
            locale = self.options.table_language
            user.speak(
                self._position_text(locale, player), buffer="game"
            )
            if self.phase == PHASE_FLIGHT and player.id == self.receiving_player_id:
                user.speak(
                    Localization.get(
                        locale,
                        "pingpong-ball-status",
                        side=Localization.get(locale, self._horizontal_key(self.ball_target_x)),
                        depth=Localization.get(locale, self._depth_key(self.ball_target_depth)),
                        bounced=str(self.ball_bounced).lower(),
                    ),
                    buffer="game",
                )

    def _match_items(self, locale: str) -> list[MenuItem]:
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "pingpong-match-summary",
                    game=self.game_number,
                    best_of=int(self.options.best_of),
                    rally=self.rally_count,
                ),
                id="match",
            )
        ]
        for team in sorted(self._team_manager.teams, key=lambda item: item.index):
            players = self._team_players(team.index)
            if not players:
                continue
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "pingpong-player-score",
                        player=self._team_manager.get_team_name(team, locale),
                        games=players[0].games_won,
                        points=players[0].points,
                    ),
                    id=f"team:{team.index}",
                )
            )
        return items

    def _action_read_match(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            self.live_status_box(
                player,
                "pingpong_match",
                lambda _player, _live_user: self._match_items(
                    self.options.table_language
                ),
                focus_id="match",
            )

    # ------------------------------------------------------------------
    # Match flow
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        self.stop_replayable_audio()
        self.clear_scheduled_sounds()
        self.status = "playing"
        self.game_active = True
        self._sync_table_status()
        self.round = 1
        self.game_number = 1
        self.initial_server_index = 0
        self.phase = PHASE_SERVE
        self.point_pause_ticks = 0
        self.rally_count = 0
        self.match_longest_rally = 0
        self.winner_id = ""
        self.winner_team_index = -1
        self.ends_swapped = False
        self.deciding_end_changed = False

        active = self._active_pingpong_players()
        self._setup_team_manager_for_start(self.options.team_mode, active)
        ordered = [
            player
            for player in self._get_team_turn_players(active)
            if isinstance(player, PingPongPlayer)
        ]
        self.set_turn_players(ordered)
        self.service_rotation_ids = [player.id for player in ordered]
        self.initial_server_index = random.randrange(len(ordered))
        for player in active:
            player.points = 0
            player.games_won = 0
            player.court_x = 0.0
            player.paddle_target_x = 0.0
            player.court_depth = 0.48
            player.response_lane = ""
            player.shot_lane = "center"
            player.successful_returns = 0
            player.missed_returns = 0
            player.longest_rally = 0
        self._sync_scores()
        self.serving_player_id = self.service_rotation_ids[self.initial_server_index]
        self._prepare_serve(announce=False)
        server = self._player(self.serving_player_id)
        if server:
            self._announce_serve(server)
        self.refresh_menus()

    def _server_index_for_score(self) -> int:
        total = sum(self._team_points(team.index) for team in self._team_manager.teams)
        if total < 20:
            offset = total // 2
        else:
            offset = 10 + (total - 20)
        return (self.initial_server_index + offset) % len(self.service_rotation_ids)

    def _prepare_serve(self, *, announce: bool = True) -> None:
        if len(self.service_rotation_ids) not in (2, 4):
            return
        self.phase = PHASE_SERVE
        self.rally_count = 0
        server_index = self._server_index_for_score()
        self.serving_player_id = self.service_rotation_ids[server_index]
        self.receiving_player_id = self.service_rotation_ids[
            (server_index + 1) % len(self.service_rotation_ids)
        ]
        self.hitting_player_id = ""
        self.ball_ticks_remaining = 0
        self.ball_bounced = False
        self.return_window_ticks = 0
        self.bot_swing_tick = -1
        self.bot_reaction_ticks = 0
        self.bot_planned_lane = ""
        self.serve_bounce_ticks = 0
        self.aim_return_ticks = 0
        self.pending_return_hitter_id = ""
        self.pending_return_receiver_id = ""
        server = self._player(self.serving_player_id)
        if server:
            server.response_lane = ""
            server.court_x = 0.0
            server.paddle_target_x = 0.0
            server.shot_lane = "center"
        self._set_required_player(server)
        self.bot_serve_ticks = SERVE_BOT_DELAY if server and server.is_bot else 0
        if announce and server:
            self._announce_serve(server)
        self.refresh_menus()

    def _announce_serve(self, server: PingPongPlayer) -> None:
        text = Localization.get(
            self.options.table_language,
            "pingpong-serve-announcement",
            player=server.name,
        )
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            user.speak(text, buffer="game")

    def _action_serve_ball(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PingPongPlayer):
            return
        if self.phase == PHASE_SERVE and player.id == self.serving_player_id:
            self._serve(player)

    def _action_hit_ball(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PingPongPlayer):
            return
        if self.phase == PHASE_FLIGHT and player.id == self.receiving_player_id:
            self._attempt_return(player)

    def _serve(self, server: PingPongPlayer) -> None:
        receiver = self._player(self.receiving_player_id)
        if not receiver:
            return
        # The server chooses the placement with Left, Up, or Right before C.
        serve_lane = (
            random.choice(("left", "center", "right"))
            if server.is_bot
            else (server.shot_lane or "center")
        )
        target_x = {
            "left": -LANE_X,
            "center": 0.0,
            "right": LANE_X,
        }[serve_lane]
        if self.options.team_mode == "2v2":
            # In doubles every serve lands in the receiver's right half.  The
            # three controls still choose a distinct point inside that legal box.
            target_x = {"left": 0.18, "center": 0.44, "right": 0.70}[serve_lane]
        if server.is_bot:
            target_x += random.uniform(-0.05, 0.05)
        target_depth = self._clamp(
            0.50
            + (server.court_depth - 0.5) * 0.55
            + (random.uniform(-0.10, 0.10) if server.is_bot else 0.0),
            0.12,
            0.88,
        )
        self.rally_count = 0
        self._launch_ball(server, receiver, target_x, target_depth, is_serve=True)

    def _flight_ticks(self, rally_count: int, target_depth: float = 0.5) -> int:
        base = PACE_BASE_TICKS.get(self.options.pace, PACE_BASE_TICKS["standard"])
        acceleration = min(5, rally_count // 3)
        depth_adjustment = int(round((target_depth - 0.5) * 4))
        return max(9, base - acceleration + depth_adjustment)

    def _launch_ball(
        self,
        hitter: PingPongPlayer,
        receiver: PingPongPlayer,
        target_x: float,
        target_depth: float,
        *,
        is_serve: bool = False,
        play_paddle: bool = True,
    ) -> None:
        self.phase = PHASE_FLIGHT
        self.hitting_player_id = hitter.id
        self.receiving_player_id = receiver.id
        self.ball_launch_x = hitter.court_x
        self.ball_target_x = round(self._clamp(target_x, -0.76, 0.76), 3)
        self.ball_target_depth = round(self._clamp(target_depth, 0.08, 0.92), 3)
        self.ball_total_ticks = self._flight_ticks(
            self.rally_count, self.ball_target_depth
        )
        self.ball_ticks_remaining = self.ball_total_ticks
        self.ball_bounce_tick = max(4, int(round(self.ball_total_ticks * 0.42)))
        self.ball_bounced = False
        self.return_window_ticks = 0
        self.ball_generation += 1
        self.serve_bounce_ticks = 3 if is_serve else 0
        receiver.response_lane = ""
        receiver.shot_lane = "center"
        self._set_required_player(receiver)
        if play_paddle:
            self._play_paddle_hit(hitter)
        self._plan_bot_return(receiver)
        self._refresh_realtime_touch_menus()

    def _plan_bot_return(self, receiver: PingPongPlayer) -> None:
        self.bot_swing_tick = -1
        if not receiver.is_bot:
            return
        accuracy = BOT_ACCURACY.get(self.options.bot_difficulty, BOT_ACCURACY["normal"])
        depth_error = (1.0 - accuracy) * random.uniform(-0.9, 0.9)
        target_lane = self._lane_for_x(self.ball_target_x)
        if random.random() <= accuracy:
            self.bot_planned_lane = target_lane
        else:
            self.bot_planned_lane = random.choice(
                [lane for lane in ("left", "center", "right") if lane != target_lane]
            )
        self.bot_reaction_ticks = {"easy": 4, "normal": 3, "hard": 2}.get(
            self.options.bot_difficulty, 3
        )
        next_opponent = self._next_rotation_player(receiver)
        if next_opponent and random.random() <= accuracy:
            receiver.shot_lane = "left" if next_opponent.court_x >= 0 else "right"
        else:
            receiver.shot_lane = random.choice(("left", "center", "right"))
        self.bot_aim_x = {
            "left": -LANE_X,
            "center": 0.0,
            "right": LANE_X,
        }[self.bot_planned_lane]
        self.bot_aim_depth = self._clamp(
            self.ball_target_depth + depth_error, DEPTH_MIN, DEPTH_MAX
        )
        window = PACE_RETURN_TICKS.get(self.options.pace, PACE_RETURN_TICKS["standard"])
        ideal = max(2, int(round(window * 0.58)))
        timing_error = random.choices([-2, -1, 0, 1, 2], weights=[1, 4, 10, 4, 1])[0]
        if random.random() > accuracy:
            timing_error += random.choice([-3, 3])
        self.bot_swing_tick = max(2, min(window - 2, ideal + timing_error))

    def _attempt_return(self, player: PingPongPlayer) -> None:
        if not self.ball_bounced:
            self._play_net_hit(player)
            self._award_point_to_opponent(player, "early")
            return
        if self.return_window_ticks <= 0:
            player.missed_returns += 1
            self._award_point_to_opponent(player, "late")
            return

        if abs(player.court_x - self.ball_target_x) > PADDLE_REACH:
            player.missed_returns += 1
            self._award_point_to_opponent(player, "out-of-reach")
            return
        opponent = self._next_rotation_player(player)
        if not opponent:
            return
        window = PACE_RETURN_TICKS.get(self.options.pace, PACE_RETURN_TICKS["standard"])
        ideal_tick = max(2, int(round(window * 0.58)))
        signed_timing = self.return_window_ticks - ideal_tick
        self.pending_return_depth = self._clamp(
            0.50 + (0.5 - player.court_depth) * 0.64 + signed_timing * 0.035,
            0.10,
            0.90,
        )
        self.phase = PHASE_AIM_RETURN
        self.aim_return_ticks = PACE_AIM_TICKS.get(
            self.options.pace, PACE_AIM_TICKS["standard"]
        )
        self.pending_return_hitter_id = player.id
        self.pending_return_receiver_id = opponent.id
        self.pending_return_timing = signed_timing
        self._play_paddle_hit(player)
        self._set_required_player(player)
        self._refresh_realtime_touch_menus()
        if player.is_bot:
            self._finalize_aimed_return(player, player.shot_lane)

    def _finalize_aimed_return(self, player: PingPongPlayer, lane: str) -> None:
        if self.phase != PHASE_AIM_RETURN or player.id != self.pending_return_hitter_id:
            return
        opponent = self._player(self.pending_return_receiver_id)
        if not opponent:
            return
        player.shot_lane = lane
        timing_limit = max(8, int(round(
            PACE_RETURN_TICKS.get(self.options.pace, PACE_RETURN_TICKS["standard"])
            * 0.46
        )))
        if abs(self.pending_return_timing) > timing_limit:
            self.aim_return_ticks = 0
            self.pending_return_hitter_id = ""
            self.pending_return_receiver_id = ""
            if self.pending_return_timing > 0:
                self._play_net_hit(player)
                self._award_point_to_opponent(player, "net")
            else:
                self._award_point_to_opponent(player, "late")
            return
        player.successful_returns += 1
        self.rally_count += 1
        self.match_longest_rally = max(self.match_longest_rally, self.rally_count)
        player.longest_rally = max(player.longest_rally, self.rally_count)
        target_x = self._clamp(
            {"left": -LANE_X, "center": 0.0, "right": LANE_X}[lane]
            - self.pending_return_timing * 0.02,
            -0.74,
            0.74,
        )
        target_depth = self.pending_return_depth
        self.aim_return_ticks = 0
        self.pending_return_hitter_id = ""
        self.pending_return_receiver_id = ""
        self._launch_ball(
            player,
            opponent,
            target_x,
            target_depth,
            play_paddle=False,
        )

    def _award_point_to_opponent(self, loser: PingPongPlayer, reason: str) -> None:
        winner = self._other_team_player(loser)
        if winner:
            self._award_point(winner, reason, loser)

    def _award_point(
        self, winner: PingPongPlayer, reason: str, loser: PingPongPlayer
    ) -> None:
        winner_team = self._team_for_player(winner)
        loser_team = self._team_for_player(loser)
        if not winner_team or not loser_team:
            return
        self._set_team_points(winner_team.index, self._team_points(winner_team.index) + 1)
        if (
            self.game_number == int(self.options.best_of)
            and not self.deciding_end_changed
            and self._team_points(winner_team.index) >= 5
        ):
            self.ends_swapped = not self.ends_swapped
            self.deciding_end_changed = True
        first_team, second_team = sorted(self._team_manager.teams, key=lambda team: team.index)
        first_name = self._team_manager.get_team_name(first_team, self.options.table_language)
        second_name = self._team_manager.get_team_name(second_team, self.options.table_language)
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            user.announce(
                Localization.get(
                    self.options.table_language,
                    "pingpong-score-announcement",
                    first=first_name,
                    first_points=self._team_points(first_team.index),
                    second=second_name,
                    second_points=self._team_points(second_team.index),
                ),
                buffer="game",
            )

        if self._game_is_won(
            self._team_points(winner_team.index), self._team_points(loser_team.index)
        ):
            self._finish_game_in_match(winner_team.index, loser_team.index)
            return
        self.phase = PHASE_POINT_PAUSE
        self.point_pause_ticks = POINT_PAUSE_TICKS
        self._set_required_player(winner)
        self.refresh_menus()

    @staticmethod
    def _game_is_won(leader: int | PingPongPlayer, opponent: int | PingPongPlayer) -> bool:
        leader_points = leader.points if isinstance(leader, PingPongPlayer) else leader
        opponent_points = opponent.points if isinstance(opponent, PingPongPlayer) else opponent
        return leader_points >= 11 and leader_points - opponent_points >= 2

    def _finish_game_in_match(
        self, winner_team_index: int, loser_team_index: int
    ) -> None:
        winner_players = self._team_players(winner_team_index)
        loser_players = self._team_players(loser_team_index)
        if not winner_players or not loser_players:
            return
        games_won = winner_players[0].games_won + 1
        self._set_team_games(winner_team_index, games_won)
        self._sync_scores()
        winner_team = self._team_manager.teams[winner_team_index]
        winner_name = self._team_manager.get_team_name(
            winner_team, self.options.table_language
        )
        self.broadcast_l(
            "pingpong-game-won",
            buffer="game",
            player=winner_name,
            winner_points=self._team_points(winner_team_index),
            loser_points=self._team_points(loser_team_index),
            games=games_won,
        )
        if games_won >= self._sets_needed():
            self._finish_match(winner_team_index)
            return
        for player in self._active_pingpong_players():
            player.points = 0
            player.court_x = 0.0
            player.paddle_target_x = 0.0
            player.court_depth = 0.48
            player.response_lane = ""
            player.shot_lane = "center"
        self.game_number += 1
        self.round = self.game_number
        self.initial_server_index = (
            self.initial_server_index + (1 if len(self.service_rotation_ids) == 2 else 1)
        ) % len(self.service_rotation_ids)
        self.ends_swapped = not self.ends_swapped
        self.deciding_end_changed = False
        self.phase = PHASE_POINT_PAUSE
        self.point_pause_ticks = POINT_PAUSE_TICKS * 2
        self.refresh_menus()

    def _finish_match(self, winner_team_index: int) -> None:
        winners = self._team_players(winner_team_index)
        if not winners:
            return
        winner = winners[0]
        winner_team = self._team_manager.teams[winner_team_index]
        winner_name = self._team_manager.get_team_name(
            winner_team, self.options.table_language
        )
        self.winner_id = winner.id
        self.winner_team_index = winner_team_index
        self.status = "finished"
        self.game_active = False
        self._sync_table_status()
        self.stop_replayable_audio()
        self.play_sound("gamewin.ogg")
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = (
                "pingpong-you-win-match"
                if any(listener.id == teammate.id for teammate in winners)
                else "pingpong-player-wins-match"
            )
            kwargs = {
                "games": winners[0].games_won,
                "longest": self.match_longest_rally,
            }
            if not any(listener.id == teammate.id for teammate in winners):
                kwargs["player"] = winner_name
            user.speak(
                Localization.get(self.options.table_language, key, **kwargs),
                buffer="game",
            )
        self.refresh_menus()
        self.finish_game()

    # ------------------------------------------------------------------
    # Audio scene
    # ------------------------------------------------------------------

    @staticmethod
    def _lane_for_x(x: float) -> str:
        if x < -0.18:
            return "left"
        if x > 0.18:
            return "right"
        return "center"

    @staticmethod
    def _stereo_pan(x: float) -> int:
        return int(round(max(-1.0, min(1.0, x / 0.76)) * 92))

    def _listener_points(
        self, listener: PingPongPlayer
    ) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
        receiver_view = listener.id == self.receiving_player_id
        if receiver_view:
            start = (-self.ball_launch_x, 3.25, 0.72)
            bounce = (self.ball_target_x, 1.05 + self.ball_target_depth * 0.75, 0.10)
            end = (self.ball_target_x, 0.18 + self.ball_target_depth * 0.58, 0.34)
        else:
            start = (self.ball_launch_x, 0.28, 0.48)
            bounce = (-self.ball_target_x, 1.65 - self.ball_target_depth * 0.45, 0.10)
            end = (-self.ball_target_x, 3.25, 0.72)
        return start, bounce, end

    def _play_paddle_hit(self, hitter: PingPongPlayer) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            position = (
                (hitter.court_x, 0.25, 0.45)
                if listener.id == hitter.id
                else (-hitter.court_x, 3.15, 0.58)
            )
            user.play_sound(
                PADDLE_ASSET,
                position=position,
                pan=self._stereo_pan(position[0]),
                volume=100,
                buffer="game",
            )

    def _play_table_bounce(self, reference: PingPongPlayer, *, server_side: bool = False) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if server_side:
                near = listener.id == reference.id
                position = (
                    reference.court_x if near else -reference.court_x,
                    0.78 if near else 2.48,
                    0.02,
                )
            else:
                _, bounce, _ = self._listener_points(listener)
                position = bounce
            user.play_sound(
                TABLE_ASSET,
                position=(position[0] * 3.2, position[1], position[2]),
                pan=self._stereo_pan(position[0]),
                volume=100,
                buffer="game",
            )

    def _play_net_hit(self, hitter: PingPongPlayer) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            near_side = listener.id == hitter.id
            user.play_sound(
                NET_ASSET,
                position=(0.0, 1.32 if near_side else 1.42, 0.16),
                pan=0,
                volume=90,
                buffer="game",
            )

    # ------------------------------------------------------------------
    # Tick and bots
    # ------------------------------------------------------------------

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()
        if self.status != "playing":
            return
        self._move_paddles()

        if self.phase == PHASE_POINT_PAUSE:
            if self.point_pause_ticks > 0:
                self.point_pause_ticks -= 1
            if self.point_pause_ticks <= 0:
                self._prepare_serve()
            return

        if self.phase == PHASE_SERVE:
            server = self._player(self.serving_player_id)
            if server and server.is_bot:
                self.bot_serve_ticks -= 1
                if self.bot_serve_ticks <= 0:
                    self._serve(server)
            return

        if self.phase == PHASE_AIM_RETURN:
            self.aim_return_ticks -= 1
            if self.aim_return_ticks <= 0:
                hitter = self._player(self.pending_return_hitter_id)
                if hitter:
                    self._finalize_aimed_return(hitter, "center")
            return

        if self.phase != PHASE_FLIGHT:
            return

        receiver = self._player(self.receiving_player_id)
        if not receiver:
            return

        if self.serve_bounce_ticks > 0:
            self.serve_bounce_ticks -= 1
            if self.serve_bounce_ticks == 0:
                hitter = self._player(self.hitting_player_id)
                if hitter:
                    self._play_table_bounce(hitter, server_side=True)
        self.ball_ticks_remaining -= 1
        if not self.ball_bounced and self.ball_ticks_remaining <= self.ball_bounce_tick:
            self.ball_bounced = True
            self.return_window_ticks = PACE_RETURN_TICKS.get(
                self.options.pace, PACE_RETURN_TICKS["standard"]
            )
            self._play_table_bounce(receiver)

        if receiver.is_bot and self.ball_bounced and self.bot_reaction_ticks > 0:
            self.bot_reaction_ticks -= 1
            if self.bot_reaction_ticks == 0 and self.bot_planned_lane:
                receiver.response_lane = self.bot_planned_lane
                receiver.paddle_target_x = {
                    "left": -LANE_X,
                    "center": 0.0,
                    "right": LANE_X,
                }[self.bot_planned_lane]

        if (
            receiver.is_bot
            and self.ball_bounced
            and self.return_window_ticks <= self.bot_swing_tick
        ):
            self._attempt_return(receiver)
            return

        if self.ball_bounced:
            self.return_window_ticks -= 1

        if self.ball_bounced and self.return_window_ticks <= 0:
            receiver.missed_returns += 1
            self._award_point_to_opponent(receiver, "passed")

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def build_game_result(self) -> GameResult:
        players = sorted(
            self._active_pingpong_players(),
            key=lambda player: (player.games_won, player.points),
            reverse=True,
        )
        winner_ids = (
            [player.id for player in self._team_players(self.winner_team_index)]
            if self.winner_team_index >= 0
            else []
        )
        scores = {player.name: player.games_won for player in players}
        competitors = []
        for team in self._team_manager.teams:
            members = self._team_players(team.index)
            competitors.append(
                ([player.id for player in members], members[0].games_won if members else 0)
            )
        winner_name = None
        if self.winner_team_index >= 0:
            winner_name = self._team_manager.get_team_name(
                self._team_manager.teams[self.winner_team_index],
                self.options.table_language,
            )
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[PlayerResult.from_player(player) for player in players],
            custom_data={
                "winner_ids": winner_ids,
                "winner_name": winner_name,
                "final_scores": scores,
                "games_won": scores,
                "longest_rally": self.match_longest_rally,
                "best_of": int(self.options.best_of),
                "pace": self.options.pace,
                "team_mode": self.options.team_mode,
                RATING_COMPETITORS_KEY: rating_competitors_from_scores(
                    competitors
                ),
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        for player in result.player_results:
            games = result.custom_data.get("games_won", {}).get(player.player_name, 0)
            lines.append(
                Localization.get(
                    locale,
                    "pingpong-end-player-line",
                    player=player.player_name,
                    games=games,
                )
            )
        lines.append(
            Localization.get(
                locale,
                "pingpong-end-longest-rally",
                count=result.custom_data.get("longest_rally", 0),
            )
        )
        return lines
