"""
Rolling Balls Game Implementation for PlayAural.

Take turns picking 1, 2, or 3 balls from a pipe. Watch out for negative balls!
The player with the most points when the pipe empties wins.
"""

from dataclasses import dataclass, field
from datetime import datetime
import json
import random
from pathlib import Path
from typing import Any

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.stats_helpers import (
    RATING_COMPETITORS_KEY,
    rating_competitors_from_scores,
)
from ...game_utils.options import (
    IntOption,
    MultiSelectOption,
    multi_select_field,
    option_field,
)
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...game_utils.teams import TeamManager
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem

from .bot import bot_think


BALL_VALUES = tuple(range(-5, 6))
PIPE_SIZE_BY_PLAYER_COUNT = {2: 25, 3: 35, 4: 50}
PIPE_PREVIEW_MIN = 6
PIPE_PREVIEW_MAX = 10
RESHUFFLE_WINDOW = 15
RESHUFFLE_MIN_BALLS = 6
DRAW_SEQUENCE_ID = "rollingballs_draw"
DRAW_SEQUENCE_TAG = "rollingballs_draw"
DRAW_START_DELAY_TICKS = 8
BALL_SOUND_DELAY_TICKS = 1
BALL_REVEAL_DELAY_TICKS = 11
DRAW_FINISH_DELAY_TICKS = 15

_ball_packs: dict[str, dict[str, int]] | None = None


def load_ball_packs() -> dict[str, dict[str, int]]:
    """Load ball packs from JSON file. Results are cached."""
    global _ball_packs
    if _ball_packs is None:
        packs_path = Path(__file__).parent / "ball_packs.json"
        with open(packs_path, "r", encoding="utf-8") as f:
            _ball_packs = json.load(f)
    return _ball_packs


def get_pack_names() -> list[str]:
    """Get available pack IDs."""
    return list(load_ball_packs().keys())


def get_pack_labels() -> dict[str, str]:
    """Get localization keys for ball packs (each pack id is its own loc key)."""
    return {pack: pack for pack in load_ball_packs().keys()}


@dataclass
class RollingBallsPlayer(Player):
    """Player state for Rolling Balls game."""

    has_reshuffled: bool = False  # Reset each turn
    view_pipe_uses: int = 0  # Total uses this game
    reshuffle_uses: int = 0  # Total uses this game
    last_viewed_pipe: list[dict] | None = None  # Snapshot of pipe at last view
    bot_pipe_memory: int = 0  # Balls from front the bot remembers (bots only)


@dataclass
class RollingBallsOptions(GameOptions):
    """Options for Rolling Balls game."""

    min_take: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=5,
            value_key="count",
            label="rb-set-min-take",
            prompt="rb-enter-min-take",
            change_msg="rb-option-changed-min-take",
        )
    )
    max_take: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=5,
            value_key="count",
            label="rb-set-max-take",
            prompt="rb-enter-max-take",
            change_msg="rb-option-changed-max-take",
        )
    )
    view_pipe_limit: int = option_field(
        IntOption(
            default=5,
            min_val=0,
            max_val=100,
            value_key="count",
            label="rb-set-view-pipe-limit",
            prompt="rb-enter-view-pipe-limit",
            change_msg="rb-option-changed-view-pipe-limit",
        )
    )
    reshuffle_limit: int = option_field(
        IntOption(
            default=3,
            min_val=0,
            max_val=100,
            value_key="count",
            label="rb-set-reshuffle-limit",
            prompt="rb-enter-reshuffle-limit",
            change_msg="rb-option-changed-reshuffle-limit",
        )
    )
    reshuffle_penalty: int = option_field(
        IntOption(
            default=1,
            min_val=0,
            max_val=5,
            value_key="points",
            label="rb-set-reshuffle-penalty",
            prompt="rb-enter-reshuffle-penalty",
            change_msg="rb-option-changed-reshuffle-penalty",
        ),
        visible_when=("reshuffle_limit", lambda value: value > 0),
    )
    ball_packs: list[str] = multi_select_field(
        MultiSelectOption(
            default=[get_pack_names()[0]],
            choices=get_pack_names,
            choice_labels=get_pack_labels(),
            label="rb-set-ball-packs",
            change_msg="rb-option-changed-ball-packs",
            min_selected=1,
            show_bulk_actions=True,
        )
    )


@dataclass
@register_game
class RollingBallsGame(Game):
    """
    Rolling Balls pipe game.

    Players take turns picking 1, 2, or 3 balls from a pipe. Each ball has
    a value from -5 to +5 with a flavor description. The player with the
    highest score when the pipe empties wins.
    """

    relevant_preferences = ["brief_announcements"]

    players: list[RollingBallsPlayer] = field(default_factory=list)
    options: RollingBallsOptions = field(default_factory=RollingBallsOptions)
    pipe: list[dict] = field(default_factory=list)
    _team_manager: TeamManager = field(default_factory=TeamManager)
    # Legacy mid-draw state retained only to migrate saves from the old timer flow.
    _ball_reveal_queue: list[dict] = field(default_factory=list)
    _ball_reveal_tick: int = 0
    _ball_reveal_player_id: str = ""

    @classmethod
    def get_name(cls) -> str:
        return "Rolling Balls"

    @classmethod
    def get_type(cls) -> str:
        return "rollingballs"

    @classmethod
    def get_category(cls) -> str:
        return "misc"

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
    ) -> RollingBallsPlayer:
        """Create a new player with Rolling Balls state."""
        return RollingBallsPlayer(id=player_id, name=name, is_bot=is_bot)

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: RollingBallsPlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast with listener-specific perspective and verbosity."""
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

    def _broadcast_global_l(
        self, full_key: str, brief_key: str | None = None, **kwargs
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _active_rolling_players(self) -> list[RollingBallsPlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, RollingBallsPlayer)
        ]

    def _preview_size(self) -> int:
        return min(
            PIPE_PREVIEW_MAX,
            max(PIPE_PREVIEW_MIN, self.options.max_take * 2),
        )

    def _pipe_preview(self) -> list[dict]:
        return [
            {"value": ball["value"], "description_key": ball["description_key"]}
            for ball in self.pipe[: self._preview_size()]
        ]

    # ==========================================================================
    # Option change handling
    # ==========================================================================

    def _handle_option_change(self, option_name: str, value: str) -> None:
        """Handle option changes that affect the stable take controls."""
        super()._handle_option_change(option_name, value)

        if option_name in {"min_take", "max_take"}:
            self._rebuild_turn_actions()

    def _rebuild_turn_actions(self) -> None:
        """Rebuild the turn action set for all players to reflect min/max take changes."""
        for player in self.players:
            turn_set = self.get_action_set(player, "turn")
            if turn_set:
                # Remove old take actions
                turn_set.remove_by_prefix("take_")
                # Add new take actions
                user = self.get_user(player)
                locale = user.locale if user else "en"
                for n in range(1, 6):
                    turn_set.add(
                        Action(
                            id=f"take_{n}",
                            label=Localization.get(locale, "rb-take", count=n),
                            handler="_action_take",
                            is_enabled="_is_take_enabled",
                            is_hidden="_is_take_hidden",
                            show_in_actions_menu=False,
                        )
                    )
        self.refresh_menus()

    # ==========================================================================
    # Pipe management
    # ==========================================================================

    def _get_active_packs(self) -> list[str]:
        """Get list of active pack IDs."""
        packs = load_ball_packs()
        selected = [pack_id for pack_id in self.options.ball_packs if pack_id in packs]
        return selected or [get_pack_names()[0]]

    def fill_pipe(self) -> int:
        """Fill a varied pipe with an approximately even value distribution."""
        player_count = len(self.get_active_players())
        total_balls = PIPE_SIZE_BY_PLAYER_COUNT.get(
            min(4, max(2, player_count)), 25
        )

        packs = load_ball_packs()
        buckets: dict[int, list[tuple[str, int]]] = {
            value: [] for value in BALL_VALUES
        }
        for pack_id in self._get_active_packs():
            for description_key, value in packs.get(pack_id, {}).items():
                if value in buckets:
                    buckets[value].append((description_key, value))

        base_count, extra_count = divmod(total_balls, len(BALL_VALUES))
        extra_values = set(random.sample(list(BALL_VALUES), extra_count))
        selected: list[tuple[str, int]] = []
        for value in BALL_VALUES:
            count = base_count + (1 if value in extra_values else 0)
            bucket = buckets[value]
            if len(bucket) < count:
                raise ValueError(
                    f"Ball packs do not provide {count} unique entries for value {value}"
                )
            selected.extend(random.sample(bucket, count))

        random.shuffle(selected)
        self.pipe = [
            {"value": value, "description_key": description_key}
            for description_key, value in selected
        ]
        return len(self.pipe)

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: RollingBallsPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Take N balls: always create 1..5 so the number keybinds always
        # resolve to a real action; the min/max range is enforced by
        # _is_take_enabled / _is_take_hidden.
        for n in range(1, 6):
            action_set.add(
                Action(
                    id=f"take_{n}",
                    label=Localization.get(locale, "rb-take", count=n),
                    handler="_action_take",
                    is_enabled="_is_take_enabled",
                    is_hidden="_is_take_hidden",
                    show_in_actions_menu=False,
                )
            )

        return action_set

    touch_standard_order = [
        "check_pipe_status",
        "view_pipe",
        "reshuffle",
        "check_scores",
        "whose_turn",
        "whos_at_table",
    ]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        rb_player = player if isinstance(player, RollingBallsPlayer) else None

        action_set.add(
            Action(
                id="check_pipe_status",
                label=Localization.get(locale, "rb-check-pipe-status"),
                handler="_action_check_pipe_status",
                is_enabled="_is_pipe_status_enabled",
                is_hidden="_is_pipe_status_hidden",
                include_spectators=True,
            )
        )

        remaining = max(
            0,
            self.options.view_pipe_limit
            - (rb_player.view_pipe_uses if rb_player else 0),
        )
        action_set.add(
            Action(
                id="view_pipe",
                label=Localization.get(
                    locale, "rb-view-pipe-action", remaining=remaining
                ),
                handler="_action_view_pipe",
                is_enabled="_is_view_pipe_enabled",
                is_hidden="_is_view_pipe_hidden",
                get_label="_get_view_pipe_label",
            )
        )

        remaining = max(
            0,
            self.options.reshuffle_limit
            - (rb_player.reshuffle_uses if rb_player else 0),
        )
        action_set.add(
            Action(
                id="reshuffle",
                label=Localization.get(
                    locale, "rb-reshuffle-action", remaining=remaining
                ),
                handler="_action_reshuffle",
                is_enabled="_is_reshuffle_enabled",
                is_hidden="_is_reshuffle_hidden",
                get_label="_get_reshuffle_label",
            )
        )

        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set, self.touch_standard_order
            )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        for n in range(1, 6):
            label = Localization.get("en", "rb-take", count=n)
            self.define_keybind(
                str(n), label, [f"take_{n}"], state=KeybindState.ACTIVE
            )
        self.define_keybind(
            "d",
            Localization.get("en", "rb-key-reshuffle-pipe"),
            ["reshuffle"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "p",
            Localization.get("en", "rb-key-view-pipe"),
            ["view_pipe"],
            state=KeybindState.ACTIVE,
            include_spectators=False,
        )
        self.define_keybind(
            "c",
            Localization.get("en", "rb-check-pipe-status"),
            ["check_pipe_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ==========================================================================
    # is_enabled callbacks
    # ==========================================================================

    def _draw_in_progress_reason(self) -> tuple[str, dict] | None:
        sequence = self._get_sequence(DRAW_SEQUENCE_ID)
        if sequence is None:
            return None
        actor = self.get_player_by_id(str(sequence.metadata.get("player_id", "")))
        return (
            "rb-draw-resolving",
            {"player": actor.name if actor else ""},
        )

    def _is_take_enabled(
        self, player: Player, action_id: str
    ) -> str | tuple[str, dict] | None:
        count = int(action_id.removeprefix("take_"))
        resolving = self._draw_in_progress_reason()
        if resolving:
            return resolving
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return (
                "rb-take-not-your-turn",
                {
                    "count": count,
                    "player": self.current_player.name if self.current_player else "",
                },
            )
        if count < self.options.min_take or count > self.options.max_take:
            return (
                "rb-take-outside-range",
                {
                    "count": count,
                    "min": self.options.min_take,
                    "max": self.options.max_take,
                },
            )
        if len(self.pipe) < count:
            return (
                "rb-not-enough-balls",
                {"count": count, "remaining": len(self.pipe)},
            )
        return None

    def _is_reshuffle_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        resolving = self._draw_in_progress_reason()
        if resolving:
            return resolving
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return (
                "rb-reshuffle-not-your-turn",
                {"player": self.current_player.name if self.current_player else ""},
            )
        rb_player: RollingBallsPlayer = player  # type: ignore
        if rb_player.reshuffle_uses >= self.options.reshuffle_limit:
            return (
                "rb-no-reshuffles-left",
                {"limit": self.options.reshuffle_limit},
            )
        if rb_player.has_reshuffled:
            return "rb-already-reshuffled"
        if len(self.pipe) < RESHUFFLE_MIN_BALLS:
            return (
                "rb-not-enough-balls-to-reshuffle",
                {
                    "remaining": len(self.pipe),
                    "required": RESHUFFLE_MIN_BALLS,
                },
            )
        return None

    def _is_view_pipe_enabled(
        self, player: Player
    ) -> str | tuple[str, dict] | None:
        resolving = self._draw_in_progress_reason()
        if resolving:
            return resolving
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        rb_player: RollingBallsPlayer = player  # type: ignore
        current_preview = self._pipe_preview()
        if (
            rb_player.view_pipe_uses >= self.options.view_pipe_limit
            and rb_player.last_viewed_pipe != current_preview
        ):
            return (
                "rb-no-views-left",
                {"limit": self.options.view_pipe_limit},
            )
        return None

    def _is_pipe_status_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    # ==========================================================================
    # is_hidden callbacks
    # ==========================================================================

    def _is_take_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        count = int(action_id.removeprefix("take_"))
        if count < self.options.min_take or count > self.options.max_take:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_reshuffle_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.options.reshuffle_limit > 0 and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_view_pipe_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.options.view_pipe_limit > 0 and self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_pipe_status_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return (
                Visibility.VISIBLE
                if self.status == "playing"
                else Visibility.HIDDEN
            )
        return Visibility.HIDDEN

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Keep the standard table action available to touch clients."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Keep the standard turn action available to touch clients."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Keep the standard score action available to touch clients."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    # ==========================================================================
    # get_label callbacks
    # ==========================================================================

    def _get_reshuffle_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        rb_player: RollingBallsPlayer = player  # type: ignore
        remaining = max(0, self.options.reshuffle_limit - rb_player.reshuffle_uses)
        return Localization.get(locale, "rb-reshuffle-action", remaining=remaining)

    def _get_view_pipe_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        rb_player: RollingBallsPlayer = player  # type: ignore
        remaining = max(0, self.options.view_pipe_limit - rb_player.view_pipe_uses)
        return Localization.get(locale, "rb-view-pipe-action", remaining=remaining)

    # ==========================================================================
    # Action handlers
    # ==========================================================================

    def _action_take(self, player: Player, action_id: str) -> None:
        count = int(action_id.removeprefix("take_"))
        if isinstance(player, RollingBallsPlayer):
            self._begin_take(player, count)

    def _ball_payload(self, ball: dict, num: int) -> dict[str, Any]:
        return {
            "num": num,
            "value": int(ball["value"]),
            "description_key": str(ball["description_key"]),
        }

    def _draw_beats(
        self,
        player: RollingBallsPlayer,
        balls: list[dict],
        *,
        resolve: bool,
        forced: bool,
        legacy: bool = False,
        initial_delay: int = DRAW_START_DELAY_TICKS,
    ) -> list[SequenceBeat]:
        payload = {
            "player_id": player.id,
            "balls": [
                self._ball_payload(ball, int(ball.get("num", index)))
                for index, ball in enumerate(balls, 1)
            ],
            "forced": forced,
            "legacy": legacy,
        }
        beats = [
            SequenceBeat(
                ops=[
                    SequenceOperation.sound_op(
                        f"game_rollingballs/take{random.randint(1, 3)}.ogg"
                    )
                ],
                delay_after_ticks=max(0, initial_delay),
            )
        ]
        if resolve:
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op("resolve_draw", payload)
                    ]
                )
            )

        for index, ball in enumerate(payload["balls"]):
            is_last = index == len(payload["balls"]) - 1
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.sound_op(
                            "game_rollingballs/takeball.ogg"
                        ),
                        SequenceOperation.callback_op(
                            "announce_ball",
                            {"player_id": player.id, "ball": ball},
                        ),
                    ],
                    delay_after_ticks=BALL_SOUND_DELAY_TICKS,
                )
            )
            value = int(ball["value"])
            if value:
                beats.append(
                    SequenceBeat(
                        ops=[
                            SequenceOperation.sound_op(
                                f"game_rollingballs/"
                                f"{'plus' if value > 0 else 'minus'}"
                                f"{min(5, abs(value))}.ogg",
                                volume=80 if value > 0 else 100,
                            )
                        ],
                        delay_after_ticks=(
                            0 if is_last else BALL_REVEAL_DELAY_TICKS
                        ),
                    )
                )
            else:
                beats.append(
                    SequenceBeat.pause(
                        0 if is_last else BALL_REVEAL_DELAY_TICKS
                    )
                )

        beats.extend(
            [
                SequenceBeat.pause(DRAW_FINISH_DELAY_TICKS),
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op("complete_draw", payload)
                    ]
                ),
            ]
        )
        return beats

    def _begin_take(
        self, player: RollingBallsPlayer, count: int, *, forced: bool = False
    ) -> None:
        """Lock the chosen prefix into a serialized reveal sequence."""
        if self.has_active_sequence(tag=DRAW_SEQUENCE_TAG):
            return
        count = min(max(0, count), len(self.pipe))
        if count <= 0:
            return

        balls = [dict(ball) for ball in self.pipe[:count]]
        if forced:
            self._broadcast_actor_l(
                player,
                "rb-you-forced-take",
                "rb-player-forced-takes",
                brief_personal_key="rb-you-forced-take-brief",
                brief_others_key="rb-player-forced-takes-brief",
                count=count,
                minimum=self.options.min_take,
            )
        else:
            self._broadcast_actor_l(
                player,
                "rb-you-take",
                "rb-player-takes",
                brief_personal_key="rb-you-take-brief",
                brief_others_key="rb-player-takes-brief",
                count=count,
                remaining=len(self.pipe),
            )

        self.start_sequence(
            DRAW_SEQUENCE_ID,
            self._draw_beats(player, balls, resolve=True, forced=forced),
            tag=DRAW_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
            metadata={"player_id": player.id, "count": count},
            replace_existing=False,
        )
        self.refresh_menus()

    def _validated_draw_payload(
        self, payload: dict
    ) -> tuple[RollingBallsPlayer, list[dict]] | None:
        player = self.get_player_by_id(str(payload.get("player_id", "")))
        raw_balls = payload.get("balls")
        if not isinstance(player, RollingBallsPlayer) or not isinstance(raw_balls, list):
            return None
        if player is not self.current_player or player not in self.get_active_players():
            return None

        balls: list[dict] = []
        for raw_ball in raw_balls:
            if not isinstance(raw_ball, dict):
                return None
            try:
                num = int(raw_ball.get("num", 0))
                value = int(raw_ball["value"])
                description_key = str(raw_ball["description_key"])
            except (KeyError, TypeError, ValueError):
                return None
            if num <= 0 or value not in BALL_VALUES or not description_key:
                return None
            balls.append(
                {
                    "num": num,
                    "value": value,
                    "description_key": description_key,
                }
            )
        return player, balls

    def _resolve_draw(self, player: RollingBallsPlayer, balls: list[dict]) -> bool:
        expected_prefix = [
            {
                "value": int(ball["value"]),
                "description_key": str(ball["description_key"]),
            }
            for ball in balls
        ]
        actual_prefix = [
            {
                "value": int(ball["value"]),
                "description_key": str(ball["description_key"]),
            }
            for ball in self.pipe[: len(balls)]
        ]
        if actual_prefix != expected_prefix:
            return False

        self.pipe = self.pipe[len(balls) :]
        for ball in balls:
            self._team_manager.add_to_team_score(player.name, int(ball["value"]))

        for candidate in self.players:
            if isinstance(candidate, RollingBallsPlayer) and candidate.is_bot:
                candidate.bot_pipe_memory = max(
                    0, candidate.bot_pipe_memory - len(balls)
                )
        self.refresh_menus()
        return True

    def _announce_ball(
        self, player: RollingBallsPlayer, ball: dict
    ) -> None:
        value = int(ball["value"])
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if self._wants_brief(user):
                continue

            description = Localization.get(
                user.locale, str(ball["description_key"])
            )
            is_actor = listener.id == player.id
            payload = {
                "num": int(ball["num"]),
                "description": description,
                "value": abs(value),
            }
            if not is_actor:
                payload["player"] = player.name
            if value > 0:
                key = "rb-your-ball-plus" if is_actor else "rb-player-ball-plus"
            elif value < 0:
                key = "rb-your-ball-minus" if is_actor else "rb-player-ball-minus"
            else:
                key = "rb-your-ball-zero" if is_actor else "rb-player-ball-zero"
                payload.pop("value")
            user.speak_l(key, buffer="game", **payload)

    def _complete_draw(
        self,
        player: RollingBallsPlayer,
        balls: list[dict],
        *,
        legacy: bool,
    ) -> None:
        team = self._team_manager.get_team(player.name)
        score = team.total_score if team else 0
        delta = sum(int(ball["value"]) for ball in balls)
        if legacy:
            self._broadcast_actor_l(
                player,
                "rb-your-score-legacy",
                "rb-player-score-legacy",
                score=score,
                remaining=len(self.pipe),
            )
        else:
            self._broadcast_actor_l(
                player,
                "rb-your-draw-summary",
                "rb-player-draw-summary",
                brief_personal_key="rb-your-draw-summary-brief",
                brief_others_key="rb-player-draw-summary-brief",
                count=len(balls),
                delta=delta,
                score=score,
                remaining=len(self.pipe),
            )
        self.end_turn()

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if sequence_id != DRAW_SEQUENCE_ID or self.status != "playing":
            return
        if callback_id == "announce_ball":
            player = self.get_player_by_id(str(payload.get("player_id", "")))
            raw_ball = payload.get("ball")
            if isinstance(player, RollingBallsPlayer) and isinstance(raw_ball, dict):
                self._announce_ball(player, raw_ball)
            return

        validated = self._validated_draw_payload(payload)
        if not validated:
            self.cancel_sequence(sequence_id)
            return
        player, balls = validated
        if callback_id == "resolve_draw":
            if not self._resolve_draw(player, balls):
                self.cancel_sequence(sequence_id)
        elif callback_id == "complete_draw":
            self._complete_draw(
                player, balls, legacy=bool(payload.get("legacy", False))
            )

    def _action_reshuffle(self, player: Player, action_id: str) -> None:
        """Reshuffle a portion of the pipe."""
        if not isinstance(player, RollingBallsPlayer):
            return
        rb_player: RollingBallsPlayer = player  # type: ignore
        self.play_sound(
            f"game_rollingballs/disrupt{random.randint(1, 2)}.ogg"  # nosec B311
        )

        shuffle_count = min(len(self.pipe), RESHUFFLE_WINDOW)
        section = self.pipe[:shuffle_count]
        original = list(section)
        random.shuffle(section)
        if section == original:
            section = section[1:] + section[:1]
        self.pipe[:shuffle_count] = section

        for p in self.players:
            if isinstance(p, RollingBallsPlayer) and p.is_bot:
                p.bot_pipe_memory = 0

        penalty = self.options.reshuffle_penalty
        if penalty > 0:
            self._team_manager.add_to_team_score(player.name, -penalty)

        rb_player.has_reshuffled = True
        rb_player.reshuffle_uses += 1
        team = self._team_manager.get_team(player.name)
        score = team.total_score if team else 0
        self._broadcast_actor_l(
            player,
            "rb-you-reshuffle",
            "rb-player-reshuffles",
            brief_personal_key="rb-you-reshuffle-brief",
            brief_others_key="rb-player-reshuffles-brief",
            count=shuffle_count,
            penalty=penalty,
            score=score,
            remaining=max(0, self.options.reshuffle_limit - rb_player.reshuffle_uses),
        )

        BotHelper.jolt_bot(player, ticks=random.randint(8, 12))  # nosec B311
        self.refresh_menus()

    def _action_view_pipe(self, player: Player, action_id: str) -> None:
        """Preview the strategic front section of the pipe privately."""
        if not isinstance(player, RollingBallsPlayer):
            return
        rb_player: RollingBallsPlayer = player  # type: ignore
        user = self.get_user(player)
        if not user:
            return

        preview = self._pipe_preview()
        if rb_player.last_viewed_pipe != preview:
            rb_player.view_pipe_uses += 1
            rb_player.last_viewed_pipe = [dict(ball) for ball in preview]

        locale = user.locale
        lines = [
            Localization.get(
                locale,
                "rb-view-pipe-header",
                shown=len(preview),
                total=len(self.pipe),
                remaining=max(
                    0, self.options.view_pipe_limit - rb_player.view_pipe_uses
                ),
            )
        ]
        for i, ball in enumerate(preview, 1):
            desc = Localization.get(locale, ball["description_key"])
            lines.append(
                Localization.get(
                    locale,
                    "rb-view-pipe-ball",
                    num=i,
                    description=desc,
                    value=ball["value"],
                )
            )
        self.status_box(player, lines)
        self.refresh_menus()

    def _pipe_status_items(self, player: Player, locale: str) -> list[MenuItem]:
        current_name = self.current_player.name if self.current_player else ""
        items = [
            MenuItem(
                text=Localization.get(
                    locale,
                    "rb-status-pipe",
                    count=len(self.pipe),
                    round=self.round,
                ),
                id="pipe",
            ),
            MenuItem(
                text=Localization.get(
                    locale,
                    "rb-status-take-range",
                    min=self.options.min_take,
                    max=self.options.max_take,
                ),
                id="range",
            ),
            MenuItem(
                text=Localization.get(
                    locale, "rb-status-turn", player=current_name
                ),
                id="turn",
            ),
        ]
        if isinstance(player, RollingBallsPlayer) and not player.is_spectator:
            items.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "rb-status-resources",
                        views=max(
                            0,
                            self.options.view_pipe_limit
                            - player.view_pipe_uses,
                        ),
                        reshuffles=max(
                            0,
                            self.options.reshuffle_limit
                            - player.reshuffle_uses,
                        ),
                    ),
                    id="resources",
                )
            )
        return items

    def _action_check_pipe_status(self, player: Player, action_id: str) -> None:
        self.live_status_box(
            player,
            "rollingballs_pipe_status",
            lambda live_player, live_user: self._pipe_status_items(
                live_player, live_user.locale
            ),
            focus_id="pipe",
        )

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        if not 1 <= self.options.min_take <= 5:
            errors.append(
                (
                    "rb-error-min-take-invalid",
                    {"count": self.options.min_take, "min": 1, "max": 5},
                )
            )
        if not 1 <= self.options.max_take <= 5:
            errors.append(
                (
                    "rb-error-max-take-invalid",
                    {"count": self.options.max_take, "min": 1, "max": 5},
                )
            )
        if self.options.min_take > self.options.max_take:
            errors.append(
                (
                    "rb-error-take-range-conflict",
                    {
                        "min": self.options.min_take,
                        "max": self.options.max_take,
                    },
                )
            )
        if not 0 <= self.options.view_pipe_limit <= 100:
            errors.append(
                (
                    "rb-error-view-limit-invalid",
                    {
                        "count": self.options.view_pipe_limit,
                        "min": 0,
                        "max": 100,
                    },
                )
            )
        if not 0 <= self.options.reshuffle_limit <= 100:
            errors.append(
                (
                    "rb-error-reshuffle-limit-invalid",
                    {
                        "count": self.options.reshuffle_limit,
                        "min": 0,
                        "max": 100,
                    },
                )
            )
        if not 0 <= self.options.reshuffle_penalty <= 5:
            errors.append(
                (
                    "rb-error-reshuffle-penalty-invalid",
                    {
                        "points": self.options.reshuffle_penalty,
                        "min": 0,
                        "max": 5,
                    },
                )
            )

        available_packs = set(get_pack_names())
        selected_packs = list(self.options.ball_packs)
        invalid_packs = [pack for pack in selected_packs if pack not in available_packs]
        if not selected_packs:
            errors.append("rb-error-no-ball-packs")
        elif invalid_packs:
            errors.append(
                (
                    "rb-error-invalid-ball-packs",
                    {"count": len(invalid_packs)},
                )
            )
        return errors

    # ==========================================================================
    # Game lifecycle
    # ==========================================================================

    def rebuild_runtime_state(self) -> None:
        super().rebuild_runtime_state()
        if (
            self.status == "playing"
            and self._ball_reveal_player_id
            and not self.has_active_sequence(tag=DRAW_SEQUENCE_TAG)
        ):
            player = self.get_player_by_id(self._ball_reveal_player_id)
            if isinstance(player, RollingBallsPlayer):
                initial_delay = max(
                    0, self._ball_reveal_tick - self.sound_scheduler_tick
                )
                balls = [dict(ball) for ball in self._ball_reveal_queue]
                self.start_sequence(
                    DRAW_SEQUENCE_ID,
                    self._draw_beats(
                        player,
                        balls,
                        resolve=False,
                        forced=False,
                        legacy=True,
                        initial_delay=initial_delay,
                    ),
                    tag=DRAW_SEQUENCE_TAG,
                    lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
                    pause_bots=True,
                    metadata={"player_id": player.id, "count": len(balls)},
                    replace_existing=False,
                )
        self._ball_reveal_queue = []
        self._ball_reveal_tick = 0
        self._ball_reveal_player_id = ""

    def on_start(self) -> None:
        """Called when the game starts."""
        self.cancel_sequences_by_tag(DRAW_SEQUENCE_TAG)
        self.clear_scheduled_sounds()
        self._ball_reveal_queue = []
        self._ball_reveal_tick = 0
        self._ball_reveal_player_id = ""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        # Set up teams based on active players (using team_mode logic like Pig)
        active_players = self._active_rolling_players()
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Initialize turn order
        self.set_turn_players(active_players)

        # Reset player state
        for p in active_players:
            rb_p: RollingBallsPlayer = p  # type: ignore
            rb_p.has_reshuffled = False
            rb_p.view_pipe_uses = 0
            rb_p.reshuffle_uses = 0
            rb_p.last_viewed_pipe = None
            rb_p.bot_pipe_memory = 0

        # Fill pipe
        total_balls = self.fill_pipe()

        self.play_music("game_pig/mus.ogg")

        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            pack_names = [
                Localization.get(user.locale, pack_id)
                for pack_id in self._get_active_packs()
            ]
            user.speak_l(
                "rb-pipe-filled",
                buffer="game",
                count=total_balls,
                packs=Localization.format_list_and(user.locale, pack_names),
            )

        # Pipe filling sounds
        delay = 0
        for _ in range(10):
            self.schedule_sound(
                f"game_uno/intercept{random.randint(1, 4)}.ogg",  # nosec B311
                delay_ticks=delay,
            )
            delay += 3  # ~150ms at 20 ticks/sec

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1

        self.set_turn_players(self._active_rolling_players())

        self.play_sound("game_pig/roundstart.ogg", volume=60)
        self._broadcast_global_l(
            "rb-round-start",
            "rb-round-start-brief",
            round=self.round,
            count=len(self.pipe),
        )

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not isinstance(player, RollingBallsPlayer):
            return
        if not self.pipe:
            self._announce_winner()
            return

        player.has_reshuffled = False

        if 0 < len(self.pipe) < self.options.min_take:
            self._begin_take(player, len(self.pipe), forced=True)
            return

        self.announce_turn(turn_sound="game_3cardpoker/turn.ogg")

        if player.is_bot:
            BotHelper.set_target(player, 0)

        self.refresh_menus()

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI, ball reveals, and scheduled sounds."""
        super().on_tick()
        self.process_scheduled_sounds()

        if not self.game_active:
            return

        self.process_sequences()
        if not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def _get_bot_perceived_pipe(self, player: RollingBallsPlayer) -> list[dict]:
        """Get the pipe as the bot perceives it, with limited information."""
        preview = self._pipe_preview()
        if (
            player.view_pipe_uses < self.options.view_pipe_limit
            and player.last_viewed_pipe != preview
        ):
            player.view_pipe_uses += 1
            player.last_viewed_pipe = [dict(ball) for ball in preview]
            player.bot_pipe_memory = len(preview)
            self.refresh_menus()

        perceived = []
        for i, ball in enumerate(self.pipe):
            if i < player.bot_pipe_memory:
                perceived.append(ball)
            else:
                perceived.append({**ball, "value": 0})
        return perceived

    def bot_think(self, player: RollingBallsPlayer) -> str | None:
        """Bot AI decision making."""
        return bot_think(self, player)

    def _on_turn_end(self) -> None:
        """Handle end of a player's turn."""
        # Check if pipe is empty
        if not self.pipe:
            self._announce_winner()
            return

        # Check if round is over
        if self.turn_index >= len(self.turn_players) - 1:
            self._on_round_end()
        else:
            self.advance_turn(announce=False)
            self._start_turn()

    def _on_round_end(self) -> None:
        """Handle end of a round."""
        if not self.pipe:
            self._announce_winner()
        else:
            self._start_round()

    def _announce_winner(self) -> None:
        """Announce the winner and finish the game."""
        self.broadcast_l("rb-pipe-empty", buffer="game")

        sorted_teams = self._sorted_teams()
        high_score = sorted_teams[0].total_score if sorted_teams else 0
        winning_teams = [
            team for team in sorted_teams if team.total_score == high_score
        ]
        winner_names = {
            member for team in winning_teams for member in team.members
        }

        if len(winning_teams) == 1:
            winning_team = winning_teams[0]
            self.play_sound("game_rollingballs/wingame.ogg")
            for p in self.players:
                user = self.get_user(p)
                if user:
                    team_name = self._team_manager.get_team_name(winning_team, user.locale)
                    if p.name in winning_team.members:
                        user.speak_l("rb-you-win", score=high_score, buffer="game")
                    else:
                        user.speak_l("rb-winner", player=team_name, score=high_score, buffer="game")
        else:
            self.play_sound("game_rollingballs/wingame.ogg")
            for p in self.players:
                user = self.get_user(p)
                if user:
                    team_names = [
                        self._team_manager.get_team_name(team, user.locale)
                        for team in winning_teams
                    ]
                    if p.name in winner_names:
                        other_names = [
                            name for name in team_names if name != p.name
                        ]
                        user.speak_l(
                            "rb-you-tie",
                            players=Localization.format_list_and(
                                user.locale, other_names
                            ),
                            score=high_score,
                            buffer="game",
                        )
                    else:
                        user.speak_l(
                            "rb-tie",
                            players=Localization.format_list_and(
                                user.locale, team_names
                            ),
                            score=high_score,
                            buffer="game",
                        )

        self.finish_game()

    def _sorted_teams(self):
        return self._team_manager.get_sorted_teams(
            by_score=True, descending=True
        )

    def finish_game(self, show_end_screen: bool = True) -> None:
        self.cancel_sequences_by_tag(DRAW_SEQUENCE_TAG)
        self._ball_reveal_queue = []
        self._ball_reveal_tick = 0
        self._ball_reveal_player_id = ""
        for player in self.players:
            if isinstance(player, RollingBallsPlayer):
                player.last_viewed_pipe = None
                player.bot_pipe_memory = 0
                player.has_reshuffled = False
        super().finish_game(show_end_screen=show_end_screen)

    def build_game_result(self) -> GameResult:
        """Build the game result using TeamManager."""
        sorted_teams = self._sorted_teams()
        high_score = sorted_teams[0].total_score if sorted_teams else 0
        winners = [
            team for team in sorted_teams if team.total_score == high_score
        ]

        final_scores = {}
        team_rankings = []
        previous_score: int | None = None
        rank = 0
        for index, team in enumerate(sorted_teams, 1):
            if team.total_score != previous_score:
                rank = index
                previous_score = team.total_score
            name = self._team_manager.get_team_name(team)
            final_scores[name] = team.total_score

            team_rankings.append(
                {
                    "index": team.index,
                    "members": team.members,
                    "rank": rank,
                    "score": team.total_score,
                    "is_individual": True,
                }
            )

        winning_names = {
            member for winner in winners for member in winner.members
        }
        winner_ids = [
            player.id
            for player in self._active_rolling_players()
            if player.name in winning_names
        ]
        active_by_name = {
            player.name: player.id for player in self._active_rolling_players()
        }
        rating_competitors = rating_competitors_from_scores(
            (
                (
                    [active_by_name[name] for name in team.members if name in active_by_name],
                    team.total_score,
                )
                for team in sorted_teams
            )
        )

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(p)
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": (
                    self._team_manager.get_team_name(winners[0])
                    if len(winners) == 1
                    else None
                ),
                "winner_ids": winner_ids,
                "winner_score": high_score,
                "final_scores": final_scores,
                "team_rankings": team_rankings,
                RATING_COMPETITORS_KEY: rating_competitors,
                "rounds_played": self.round,
                "team_mode": "individual",
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen."""
        lines = [Localization.get(locale, "game-final-scores")]

        team_rankings = result.custom_data.get("team_rankings")

        if team_rankings:
            for i, data in enumerate(team_rankings, 1):
                if data.get("is_individual") and data.get("members"):
                    name = data["members"][0]
                else:
                    name = Localization.get(locale, "game-team-name", index=data["index"] + 1)

                score = data["score"]
                points_str = Localization.get(locale, "game-points", count=score)
                lines.append(
                    Localization.get(
                        locale,
                        "rb-line-format",
                        rank=data.get("rank", i),
                        player=name,
                        points=points_str,
                    )
                )
        else:
            final_scores = result.custom_data.get("final_scores", {})
            for i, (name, score) in enumerate(final_scores.items(), 1):
                points_str = Localization.get(locale, "game-points", count=score)
                lines.append(
                    Localization.get(
                        locale,
                        "rb-line-format",
                        rank=i,
                        player=name,
                        points=points_str,
                    )
                )

        return lines

    def end_turn(self, jolt_min: int = 20, jolt_max: int = 30) -> None:
        """End the current player's turn."""
        BotHelper.jolt_bots(self, ticks=random.randint(jolt_min, jolt_max))  # nosec B311
        self._on_turn_end()
