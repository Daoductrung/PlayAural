"""
Left Right Center (LRC) Game Implementation for PlayAural v0.1.0.

Players roll up to 3 dice (limited by chips they hold). Each die result
passes a chip left/right/center or keeps it. Center chips are removed
from play. Last player holding chips wins.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


DICE_FACES = ["left", "right", "center", "dot", "dot", "dot"]


@dataclass
class LeftRightCenterPlayer(Player):
    """Player state for Left Right Center."""

    chips: int = 0


@dataclass
class LeftRightCenterOptions(GameOptions):
    """Options for Left Right Center."""

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
    """Left Right Center dice game."""

    players: list[LeftRightCenterPlayer] = field(default_factory=list)
    options: LeftRightCenterOptions = field(default_factory=LeftRightCenterOptions)
    center_pot: int = 0
    turn_delay_ticks: int = 0

    def __post_init__(self):
        super().__post_init__()
        self._pending_turn_advance = False
        self._pending_roll = None
        self._roll_delay_ticks = 0

    @classmethod
    def get_name(cls) -> str:
        return "Left Right Center"

    @classmethod
    def get_type(cls) -> str:
        return "leftrightcenter"

    @classmethod
    def get_category(cls) -> str:
        return "category-dice-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 20

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> LeftRightCenterPlayer:
        return LeftRightCenterPlayer(id=player_id, name=name, is_bot=is_bot, chips=0)

    # ==========================================================================
    # Turn action availability
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if isinstance(player, LeftRightCenterPlayer) and player.chips == 0:
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

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: LeftRightCenterPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "lrc-roll", count=0),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                get_label="_get_roll_label",
            )
        )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        
        # Need locale for keybinds as this method is called after initialize_lobby
        # Note: server.py initialize_lobby calls setup_keybinds *after* adding host player.
        # But we need to ensure we have access to locale.
        # However, setup_keybinds is on the Game instance, not Player.
        # Where do we get locale?
        # self.players is a dict.
        # We can try to use the host's locale or default to 'en'?
        # Actually, setup_keybinds is usually called once. Keybinds are global definitions.
        # Wait, if `locale` is not passed to setup_keybinds, where does it come from?
        # It's NOT a local variable here!
        # In `initialize_lobby` (where setup_keybinds is called), we verify if we can access user logic.
        # But wait, `setup_keybinds` in my previous edits for `NinetyNine`, `MileByMile` etc didn't have `user = ...` logic inside `setup_keybinds`?
        # Actually, I edited `create_turn_action_set`, NOT `setup_keybinds` in previous tool calls!
        # `setup_keybinds` does NOT receive player/user.
        # And Keybind definitions are static per game instance!
        #
        # CRITICAL REALIZATION: `Localization.get` inside `setup_keybinds` is meaningless if it depends on a single user's locale,
        # because keybinds are shared across the game instance which might have multiple players with different locales?
        # OR does `define_keybind` store the localized string?
        # If `define_keybind` stores the string, then it uses whatever locale is active when `setup_keybinds` runs.
        # `initialize_lobby` runs when the first player creates the table. So it uses the HOST's locale.
        # This means all players see the HOST's language for keybind help?
        # This is an architectural limitation I must accept for now, OR `Localization.get` should be deferred?
        # `Action` labels use `Localization.get(locale, ...)` dynamically in `create_turn_action_set` (per player).
        # Keybinds descriptions... are they sent to client as static strings?
        # If so, yes, they will be in Host's language.
        # But I need to get `locale` in `setup_keybinds`. it is NOT defined.
        #
        # I MUST ADD logic to get locale in `setup_keybinds`!!
        # `initialize_lobby` passes `user`. But `setup_keybinds` doesn't take args.
        # I can get it from `self.players[self.host_username]` if set?
        # Or I need to fetch the host user again.
        
        # Let's see how I did it in `create_turn_action_set` -> I used `self.get_user(player)`.
        # in `setup_keybinds`, I don't have `player`.
        # But `self.host_username` should be set by `initialize_lobby` before calling `setup_keybinds`?
        # Let's check `lobby_actions_mixin.py` or `server.py`.
        # `server.py`: `game.initialize_lobby(user.username, user)`
        # `LobbyActionsMixin.initialize_lobby`:
        #    self.host_username = host_name
        #    self.add_player(host_name, host_user) ...
        #    self.setup_keybinds()
        # So `self.host_username` IS available.
        
        user = None
        if hasattr(self, 'host_username') and self.host_username:
             # We need to find the user object. 
             # self.get_player(self.host_username) returns Player object.
             # self.get_user(player) returns User object.
             # This seems safe.
             player = self.get_player(self.host_username)
             if player:
                 user = self.get_user(player)
        
        locale = user.locale if user else "en"

        self.define_keybind(
            "r", Localization.get(locale, "lrc-roll-label"), ["roll"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "c",
            Localization.get("en", "lrc-check-center"),
            ["check_center"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="check_center",
                label=Localization.get(locale, "lrc-check-center"),
                handler="_action_check_center",
                is_enabled="_is_check_center_enabled",
                is_hidden="_is_check_center_hidden",
            )
        )
        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            target_order = [
                "check_center",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            # Put target items FIRST
            final_order = []
            for aid in target_order:
                if action_set.get_action(aid):
                    final_order.append(aid)
            
            # Then add remaining items
            for aid in action_set._order:
                if aid not in target_order:
                    final_order.append(aid)
            
            action_set._order = final_order

        return action_set

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
    # Game flow
    # ==========================================================================

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.center_pot = 0
        self.turn_delay_ticks = 0
        self._pending_turn_advance = False
        self._pending_roll = None
        self._roll_delay_ticks = 0

        for player in self.players:
            player.chips = self.options.starting_chips

        # Set up individual team scores so the default scoreboard works
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in self.players])
        self._sync_team_scores()

        # Initialize turn order with all active players
        self.set_turn_players(self.get_active_players())
        self.play_music("game_pig/mus.ogg")
        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not player:
            return

        if self._check_for_winner():
            return

        self.announce_turn()
        if isinstance(player, LeftRightCenterPlayer) and player.chips == 0:
            self.broadcast_l("lrc-no-chips", player=player.name)
            self.end_turn()
            return
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(5, 10))

        self.rebuild_all_menus()

    def _end_turn(self) -> None:
        if self._check_for_winner():
            return
        self.advance_turn(announce=False)
        self._start_turn()

    def _get_turn_order(self) -> list[LeftRightCenterPlayer]:
        return [p for p in self.players if not p.is_spectator]

    def _get_left_right(self, player: LeftRightCenterPlayer) -> tuple[LeftRightCenterPlayer, LeftRightCenterPlayer]:
        order = self._get_turn_order()
        if not order:
            return (player, player)
        idx = order.index(player)
        left_player = order[(idx - 1) % len(order)]
        right_player = order[(idx + 1) % len(order)]
        return left_player, right_player

    def _broadcast_roll_results(self, player: LeftRightCenterPlayer, faces: list[str]) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            locale = user.locale
            localized_faces = [Localization.get(locale, f"lrc-face-{face}") for face in faces]
            results_text = Localization.format_list_and(locale, localized_faces)
            user.speak_l("lrc-roll-results", buffer="game", player=player.name, results=results_text)

    def _action_roll(self, player: Player, action_id: str) -> None:
        lrc_player: LeftRightCenterPlayer = player  # type: ignore

        roll_count = min(3, lrc_player.chips)

        if roll_count == 0:
            # No chips: skip roll output entirely and move on
            self.end_turn()
            return
        self.play_sound("game_pig/roll.ogg")

        faces = [random.choice(DICE_FACES) for _ in range(roll_count)]
        self._broadcast_roll_results(lrc_player, faces)

        # Delay the chip movements slightly for pacing
        self._pending_roll = {
            "player_id": lrc_player.id,
            "faces": faces,
        }
        self._roll_delay_ticks = 10
        return

    def _resolve_pending_roll(self) -> None:
        if not self._pending_roll:
            return
        player = self.get_player_by_id(self._pending_roll["player_id"])
        if not player:
            self._pending_roll = None
            return
        lrc_player: LeftRightCenterPlayer = player  # type: ignore
        faces = list(self._pending_roll["faces"])
        self._pending_roll = None

        left_player, right_player = self._get_left_right(lrc_player)

        sound_delay = 0
        left_count = faces.count("left")
        right_count = faces.count("right")
        center_count = faces.count("center")

        if left_count:
            lrc_player.chips -= left_count
            left_player.chips += left_count
            self.broadcast_l(
                "lrc-pass-left",
                player=lrc_player.name,
                target=left_player.name,
                count=left_count,
            )
            for _ in range(left_count):
                self.schedule_sound(
                    "game_ninetynine/lose1_you.ogg", delay_ticks=sound_delay, pan=-50
                )
                sound_delay += 10

        if right_count:
            lrc_player.chips -= right_count
            right_player.chips += right_count
            self.broadcast_l(
                "lrc-pass-right",
                player=lrc_player.name,
                target=right_player.name,
                count=right_count,
            )
            for _ in range(right_count):
                self.schedule_sound(
                    "game_ninetynine/lose1_you.ogg", delay_ticks=sound_delay, pan=50
                )
                sound_delay += 10

        if center_count:
            lrc_player.chips -= center_count
            self.center_pot += center_count
            self.broadcast_l(
                "lrc-pass-center",
                player=lrc_player.name,
                count=center_count,
            )
            for _ in range(center_count):
                self.schedule_sound(
                    "game_ninetynine/lose1_other.ogg", delay_ticks=sound_delay
                )
                sound_delay += 10

        self._sync_team_scores()
        self.end_turn(delay_ticks=sound_delay)

    def _check_for_winner(self) -> bool:
        active = self.get_active_players()
        players_with_chips = [p for p in active if p.chips > 0]
        if len(players_with_chips) == 1:
            winner = players_with_chips[0]
            self.broadcast_l("lrc-winner", player=winner.name, count=winner.chips)
            self.play_sound("game_pig/win.ogg")
            self.finish_game()
            return True
        return False

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if self._roll_delay_ticks > 0:
            self._roll_delay_ticks -= 1
            if self._roll_delay_ticks == 0:
                self._resolve_pending_roll()
            return
        if self.turn_delay_ticks > 0:
            self.turn_delay_ticks -= 1
            return
        if self._pending_turn_advance:
            self._pending_turn_advance = False
            self._end_turn()
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: LeftRightCenterPlayer) -> str | None:
        return "roll"

    def _is_check_center_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_center_hidden(self, player: Player) -> Visibility:
        """Override: Web visible when playing."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return Visibility.HIDDEN

    def _action_check_center(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak_l("lrc-center-pot", buffer="game", count=self.center_pot)

    def end_turn(self, delay_ticks: int = 0) -> None:
        """End the current turn with optional delay for turn resolution."""
        current = self.current_player
        if current and current.is_bot:
            BotHelper.jolt_bot(current, ticks=random.randint(10, 15))
        if delay_ticks > 0:
            self.turn_delay_ticks = delay_ticks
            self._pending_turn_advance = True
            return
        self._end_turn()

    def _sync_team_scores(self) -> None:
        """Mirror player chips into TeamManager totals for scoreboard output."""
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.players:
            team = self._team_manager.get_team(p.name)
            if team:
                team.total_score = p.chips

    def _get_roll_label(self, player: Player, action_id: str) -> str:
        lrc_player: LeftRightCenterPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        count = min(3, max(0, lrc_player.chips))
        return Localization.get(locale, "lrc-roll", count=count)

    # Use default announce_turn() (includes per-user turn sound preference)

    def build_game_result(self) -> GameResult:
        active_players = self.get_active_players()
        players_with_chips = [p for p in active_players if p.chips > 0]
        winner = players_with_chips[0] if len(players_with_chips) == 1 else None
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot,
                )
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "center_pot": self.center_pot,
                "final_chips": {p.name: p.chips for p in self.players},
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores-header")]
        final_chips = result.custom_data.get("final_chips", {})
        for name, chips in final_chips.items():
            lines.append(
                Localization.get(locale, "lrc-line-format", player=name, chips=chips)
            )
        lines.append(Localization.get(locale, "lrc-center-pot", count=result.custom_data.get("center_pot", 0)))
        return lines
