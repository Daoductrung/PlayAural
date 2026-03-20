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

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...game_utils.teams import TeamManager
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

from .bot import bot_think

# Cached ball packs data
_ball_packs: dict[str, dict[str, int]] | None = None

def load_ball_packs() -> dict[str, dict[str, int]]:
    """Load ball packs from JSON file. Results are cached."""
    global _ball_packs
    if _ball_packs is None:
        packs_path = Path(__file__).parent / "ball_packs.json"
        with open(packs_path, "r", encoding="utf-8") as f:
            _ball_packs = json.load(f)
    return _ball_packs

def get_pack_names(game=None, player=None) -> list[str]:
    """Get available pack IDs."""
    packs = list(load_ball_packs().keys())
    return packs + ["rb-pack-all"]

def get_pack_labels() -> dict[str, str]:
    """Get localization keys for ball packs."""
    packs = list(load_ball_packs().keys())
    labels = {pack: pack for pack in packs}
    labels["rb-pack-all"] = "rb-pack-all"
    return labels

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
        )
    )
    ball_pack: str = option_field(
        MenuOption(
            default="rb-pack-international",
            value_key="pack",
            choices=lambda g, p: get_pack_names(),
            choice_labels=get_pack_labels(),
            label="rb-set-ball-pack",
            prompt="rb-select-ball-pack",
            change_msg="rb-option-changed-ball-pack",
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

    players: list[RollingBallsPlayer] = field(default_factory=list)
    options: RollingBallsOptions = field(default_factory=RollingBallsOptions)
    pipe: list[dict] = field(default_factory=list)
    _team_manager: TeamManager = field(default_factory=TeamManager)
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
        return "category-uncategorized"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> RollingBallsPlayer:
        """Create a new player with Rolling Balls state."""
        return RollingBallsPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Option change handling
    # ==========================================================================

    def _handle_option_change(self, option_name: str, value: str) -> None:
        """Handle option changes, rebuilding turn actions when min/max take change."""
        super()._handle_option_change(option_name, value)

        if option_name == "min_take":
            # Clamp max_take up if needed
            if self.options.max_take < self.options.min_take:
                self.options.max_take = self.options.min_take
            self._rebuild_turn_actions()
        elif option_name == "max_take":
            # Clamp min_take down if needed
            if self.options.min_take > self.options.max_take:
                self.options.min_take = self.options.max_take
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
                for n in range(self.options.min_take, self.options.max_take + 1):
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
        self.rebuild_all_menus()

    # ==========================================================================
    # Pipe management
    # ==========================================================================

    def _get_active_packs(self) -> list[str]:
        """Get list of active pack IDs."""
        if self.options.ball_pack == "rb-pack-all":
            return list(load_ball_packs().keys())
        return [self.options.ball_pack]

    def fill_pipe(self) -> int:
        """Fill the pipe with balls based on player count."""
        player_count = len(self.get_active_players())
        if player_count >= 4:
            total_balls = 50
        elif player_count == 3:
            total_balls = 35
        else:
            total_balls = 25

        # Build combined ball pool from active packs
        packs = load_ball_packs()
        ball_pool: list[tuple[str, int]] = []
        for pack_id in self._get_active_packs():
            pack = packs.get(pack_id, {})
            ball_pool.extend(pack.items())

        self.pipe = []
        for _ in range(total_balls):
            if not ball_pool:
                break
            description_key, value = random.choice(ball_pool)  # nosec B311
            self.pipe.append({"value": value, "description_key": description_key})
        return total_balls

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: RollingBallsPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # View pipe (always visible during play, doesn't require turn)
        if self.options.view_pipe_limit > 0:
            remaining = self.options.view_pipe_limit - player.view_pipe_uses
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
                    show_in_actions_menu=True,
                    include_spectators=False,  # Hidden from audience
                )
            )

        # Reshuffle pipe
        if self.options.reshuffle_limit > 0:
            remaining = self.options.reshuffle_limit - player.reshuffle_uses
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

        # Take N balls (dynamic based on min/max options)
        for n in range(self.options.min_take, self.options.max_take + 1):
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

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["check_scores", "whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)

        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            # Reordering Logic
            final_order = []
            for aid in self.web_target_order:
                if action_set.get_action(aid):
                    final_order.append(aid)

            for aid in action_set._order:
                if aid not in self.web_target_order:
                    final_order.append(aid)

            action_set._order = final_order

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        for n in range(1, 6):
            label = f"Take {n} ball{'s' if n != 1 else ''}"
            self.define_keybind(
                str(n), label, [f"take_{n}"], state=KeybindState.ACTIVE
            )
        self.define_keybind(
            "d", "Reshuffle pipe", ["reshuffle"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "p", "View pipe", ["view_pipe"], state=KeybindState.ACTIVE, include_spectators=False
        )

    # ==========================================================================
    # is_enabled callbacks
    # ==========================================================================

    def _is_take_enabled(self, player: Player, action_id: str) -> str | None:
        if self._ball_reveal_player_id:
            return "action-not-your-turn"
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        count = int(action_id.removeprefix("take_"))
        if len(self.pipe) < count:
            return "rb-not-enough-balls"
        return None

    def _is_reshuffle_enabled(self, player: Player) -> str | None:
        if self._ball_reveal_player_id:
            return "action-not-your-turn"
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        rb_player: RollingBallsPlayer = player  # type: ignore
        if rb_player.reshuffle_uses >= self.options.reshuffle_limit:
            return "rb-no-reshuffles-left"
        if rb_player.has_reshuffled:
            return "rb-already-reshuffled"
        if len(self.pipe) < 6:
            return "rb-not-enough-balls"
        return None

    def _is_view_pipe_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        rb_player: RollingBallsPlayer = player  # type: ignore
        if rb_player.view_pipe_uses >= self.options.view_pipe_limit:
            return "rb-no-views-left"
        return None

    # ==========================================================================
    # is_hidden callbacks
    # ==========================================================================

    def _is_take_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        count = int(action_id.removeprefix("take_"))
        if len(self.pipe) < count:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_reshuffle_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        rb_player: RollingBallsPlayer = player  # type: ignore
        can_reshuffle = (
            self.options.reshuffle_limit > 0
            and rb_player.reshuffle_uses < self.options.reshuffle_limit
            and not rb_player.has_reshuffled
            and len(self.pipe) >= 6
        )
        if can_reshuffle:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_view_pipe_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        rb_player: RollingBallsPlayer = player  # type: ignore
        can_view = (
            self.options.view_pipe_limit > 0
            and rb_player.view_pipe_uses < self.options.view_pipe_limit
            and self.status == "playing"
        )
        if can_view:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # WEB-SPECIFIC: Visibility Overrides

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
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
        remaining = self.options.reshuffle_limit - rb_player.reshuffle_uses
        return Localization.get(locale, "rb-reshuffle-action", remaining=remaining)

    def _get_view_pipe_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        rb_player: RollingBallsPlayer = player  # type: ignore
        remaining = self.options.view_pipe_limit - rb_player.view_pipe_uses
        return Localization.get(locale, "rb-view-pipe-action", remaining=remaining)

    # ==========================================================================
    # Action handlers
    # ==========================================================================

    def _action_take(self, player: Player, action_id: str) -> None:
        count = int(action_id.removeprefix("take_"))
        self._take_balls(player, count)

    def _take_balls(self, player: Player, count: int) -> None:
        """Take balls from the pipe, queuing reveals for on_tick."""
        rb_player: RollingBallsPlayer = player  # type: ignore

        self.broadcast_personal_l(
            player, "rb-you-take", "rb-player-takes", count=count, buffer="game"
        )
        self.play_sound(f"game_rollingballs/take{random.randint(1,3)}.ogg")

        # Pop balls from pipe and queue them for reveal
        balls = []
        for _ in range(count):
            if not self.pipe:
                break
            balls.append(self.pipe.pop(0))

        # Erode bot pipe memory (balls removed from front)
        taken = len(balls)
        for p in self.players:
            rb_p: RollingBallsPlayer = p  # type: ignore
            if rb_p.is_bot:
                rb_p.bot_pipe_memory = max(0, rb_p.bot_pipe_memory - taken)

        # Apply scores immediately (game state is updated now)
        for ball in balls:
            self._team_manager.add_to_team_score(player.name, ball["value"])

        # Queue balls for synchronized sound+speech reveal in on_tick
        for i, ball in enumerate(balls, 1):
            ball["num"] = i
        self._ball_reveal_queue = balls
        self._ball_reveal_player_id = player.id
        self._ball_reveal_tick = self.sound_scheduler_tick + 8  # ~400 ms initial delay

    def _reveal_next_ball(self) -> None:
        """Reveal the next ball from the queue with synchronized sound and speech."""
        ball = self._ball_reveal_queue.pop(0)
        ball_num = ball["num"]

        # Play value sound and broadcast description
        value = ball["value"]
        description_key = ball["description_key"]
        abs_value = abs(value)
        sound_value = abs_value if abs_value <=5 else 5

        # Play takeball sound immediately, schedule value sound 1 tick later
        self.play_sound("game_rollingballs/takeball.ogg")

        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue

            description = Localization.get(user.locale, description_key)
            if value > 0:
                user.speak_l(
                    "rb-ball-plus", num=ball_num, description=description, value=abs_value, buffer="game"
                )
            elif value < 0:
                user.speak_l(
                    "rb-ball-minus", num=ball_num, description=description, value=abs_value, buffer="game"
                )
            else:
                user.speak_l("rb-ball-zero", num=ball_num, description=description, buffer="game")

        if value > 0:
            self.schedule_sound(f"game_rollingballs/plus{sound_value}.ogg", delay_ticks=1, volume=80)
        elif value < 0:
            self.schedule_sound(f"game_rollingballs/minus{sound_value}.ogg", delay_ticks=1)

        if self._ball_reveal_queue:
            # More balls to reveal - schedule next in 1200ms (24 ticks)
            self._ball_reveal_tick = self.sound_scheduler_tick + 12
        else:
            # All balls revealed - finish after 1500ms delay
            self._ball_reveal_tick = self.sound_scheduler_tick + 15

    def _finish_ball_reveals(self) -> None:
        """Announce score and end turn after all balls are revealed."""
        player = self.get_player_by_id(self._ball_reveal_player_id)
        self._ball_reveal_player_id = ""

        if not player:
            return

        team = self._team_manager.get_team(player.name)
        score = team.total_score if team else 0

        self.broadcast_l("rb-new-score", player=player.name, score=score, buffer="game")
        self.end_turn()

    def _action_reshuffle(self, player: Player, action_id: str) -> None:
        """Reshuffle a portion of the pipe."""
        rb_player: RollingBallsPlayer = player  # type: ignore

        self.broadcast_personal_l(
            player, "rb-you-reshuffle", "rb-player-reshuffles", buffer="game"
        )
        self.play_sound(
            f"game_rollingballs/disrupt{random.randint(1, 2)}.ogg"  # nosec B311
        )

        # Shuffle the first min(len(pipe), 15) balls
        shuffle_count = min(len(self.pipe), 15)
        section = self.pipe[:shuffle_count]
        random.shuffle(section)
        self.pipe[:shuffle_count] = section

        # Invalidate bot pipe memory (pipe order changed)
        for p in self.players:
            rb_p: RollingBallsPlayer = p  # type: ignore
            if rb_p.is_bot:
                rb_p.bot_pipe_memory = 0

        self.broadcast_l("rb-reshuffled", buffer="game")

        # Apply penalty
        if self.options.reshuffle_penalty > 0:
            self._team_manager.add_to_team_score(player.name, -self.options.reshuffle_penalty)
            self.broadcast_l(
                "rb-reshuffle-penalty",
                player=player.name,
                points=self.options.reshuffle_penalty,
                buffer="game"
            )

        rb_player.has_reshuffled = True
        rb_player.reshuffle_uses += 1

        # Jolt bot
        BotHelper.jolt_bot(player, ticks=random.randint(8, 12))  # nosec B311

        # Rebuild menus to reflect updated remaining count
        self.rebuild_all_menus()

    def _action_view_pipe(self, player: Player, action_id: str) -> None:
        """View the pipe contents (private to the requesting player)."""
        rb_player: RollingBallsPlayer = player  # type: ignore
        user = self.get_user(player)
        if not user:
            return

        # Only count as a use if the pipe changed since last view
        if rb_player.last_viewed_pipe != self.pipe:
            rb_player.view_pipe_uses += 1
            rb_player.last_viewed_pipe = [b.copy() for b in self.pipe]

        locale = user.locale

        # Build pipe contents as a status box
        lines = [Localization.get(locale, "rb-view-pipe-header", count=len(self.pipe))]
        for i, ball in enumerate(self.pipe, 1):
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

        # Rebuild menus to reflect updated remaining count
        self.rebuild_all_menus()


    # ==========================================================================
    # Game lifecycle
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        # Set up teams based on active players (using team_mode logic like Pig)
        active_players = self.get_active_players()
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

        # Play music
        self.play_music("game_pig/mus.ogg")

        # Announce
        self.broadcast_l("rb-pipe-filled", count=total_balls, buffer="game")

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

        # Refresh turn order
        self.set_turn_players(self.get_active_players())

        self.play_sound("game_pig/roundstart.ogg", volume=60)
        self.broadcast_l("game-round-start", round=self.round, buffer="game")
        self.broadcast_l("rb-balls-remaining", count=len(self.pipe), buffer="game")

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        rb_player: RollingBallsPlayer = player  # type: ignore
        rb_player.has_reshuffled = False

        # If remaining balls are below minimum take, auto-take them
        if 0 < len(self.pipe) < self.options.min_take:
            self._take_balls(player, len(self.pipe))
            return

        # Announce turn
        self.announce_turn(turn_sound="game_3cardpoker/turn.ogg")

        # Set up bot if needed
        if player.is_bot:
            BotHelper.set_target(player, 0)

        self.rebuild_all_menus()

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI, ball reveals, and scheduled sounds."""
        super().on_tick()
        self.process_scheduled_sounds()

        if not self.game_active:
            return

        # Process ball reveal queue (blocks bot actions while active)
        if self._ball_reveal_player_id:
            if self.sound_scheduler_tick >= self._ball_reveal_tick:
                if self._ball_reveal_queue:
                    self._reveal_next_ball()
                else:
                    self._finish_ball_reveals()
            return

        BotHelper.on_tick(self)

    def _get_bot_perceived_pipe(self, player: RollingBallsPlayer) -> list[dict]:
        """Get the pipe as the bot perceives it, with limited information."""
        # Auto-use a view if available and the pipe has changed
        if (
            player.view_pipe_uses < self.options.view_pipe_limit
            and player.last_viewed_pipe != self.pipe
        ):
            player.view_pipe_uses += 1
            player.last_viewed_pipe = [b.copy() for b in self.pipe]
            player.bot_pipe_memory = min(6, len(self.pipe))
            self.rebuild_all_menus()

        perceived = []
        for i, ball in enumerate(self.pipe):
            if i < player.bot_pipe_memory:
                perceived.append(ball)
            else:
                perceived.append({
                    **ball,
                    "value": random.randint(-5, 5),  # nosec B311
                })
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

        sorted_teams = self._team_manager.get_sorted_teams(
            by_score=True, descending=True
        )

        winning_teams = []
        high_score = sorted_teams[0].total_score if sorted_teams else 0
        for team in sorted_teams:
            if team.total_score == high_score:
                winning_teams.append(team)
            else:
                break

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
            # Tie
            team_names = [self._team_manager.get_team_name(t) for t in winning_teams]
            for p in self.players:
                user = self.get_user(p)
                if user:
                    names_str = Localization.format_list_and(user.locale, team_names)
                    user.speak_l("rb-tie", players=names_str, score=high_score, buffer="game")

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result using TeamManager."""
        sorted_teams = self._team_manager.get_sorted_teams(
            by_score=True, descending=True
        )
        winner = sorted_teams[0] if sorted_teams else None

        final_scores = {}
        team_rankings = []
        for team in sorted_teams:
            name = self._team_manager.get_team_name(team)
            final_scores[name] = team.total_score

            team_rankings.append({
                "index": team.index,
                "members": team.members,
                "score": team.total_score,
                "name_legacy": name,
                "is_individual": True
            })

        winner_ids = []
        if winner:
            active_players = self.get_active_players()
            name_to_id = {p.name: p.id for p in active_players}
            for member_name in winner.members:
                if member_name in name_to_id:
                    winner_ids.append(name_to_id[member_name])

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
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": self._team_manager.get_team_name(winner) if winner else None,
                "winner_ids": winner_ids,
                "winner_score": winner.total_score if winner else 0,
                "final_scores": final_scores,
                "team_rankings": team_rankings,
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
                # Let's use a standard format for it
                lines.append(Localization.get(locale, "rb-line-format", rank=i, player=name, points=points_str))
        else:
            final_scores = result.custom_data.get("final_scores", {})
            for i, (name, score) in enumerate(final_scores.items(), 1):
                points_str = Localization.get(locale, "game-points", count=score)
                lines.append(Localization.get(locale, "rb-line-format", rank=i, player=name, points=points_str))

        return lines

    def end_turn(self, jolt_min: int = 20, jolt_max: int = 30) -> None:
        """End the current player's turn."""
        BotHelper.jolt_bots(self, ticks=random.randint(jolt_min, jolt_max))  # nosec B311
        self._on_turn_end()
