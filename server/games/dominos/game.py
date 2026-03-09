"""
Dominos Game Implementation for PlayAural.

A classic tile-based game where players match pips.
Features Draw, Block, and All Fives game modes.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random
import uuid

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility, MenuInput
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

from .bot import bot_think


@dataclass
class Tile:
    """A Domino tile."""
    end1: int
    end2: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def pips(self) -> int:
        return self.end1 + self.end2

    @property
    def is_double(self) -> bool:
        return self.end1 == self.end2

    def matches(self, value: int) -> bool:
        """Check if either end matches the given value."""
        return self.end1 == value or self.end2 == value

    def to_string(self, locale: str = "en") -> str:
        """Get the localized string representation of the tile."""
        return Localization.get(locale, "dominos-tile-name", end1=self.end1, end2=self.end2)


@dataclass
class DominosPlayer(Player):
    """Player state for Dominos."""
    hand: list[Tile] = field(default_factory=list)
    score: int = 0


@dataclass
class DominosOptions(GameOptions):
    """Options for Dominos game."""
    target_score: int = option_field(
        MenuOption(
            default=100,
            value_key="score",
            choices=[50, 100, 150, 250],
            choice_labels={
                50: "50",
                100: "100",
                150: "150",
                250: "250",
            },
            label="game-set-target-score",
            prompt="game-enter-target-score",
            change_msg="game-option-changed-target",
        )
    )
    game_mode: str = option_field(
        MenuOption(
            default="draw",
            value_key="mode",
            choices=["draw", "block", "all_fives"],
            choice_labels={
                "draw": "dominos-mode-draw",
                "block": "dominos-mode-block",
                "all_fives": "dominos-mode-all-fives",
            },
            label="dominos-set-mode",
            prompt="dominos-select-mode",
            change_msg="dominos-option-changed-mode",
        )
    )


@dataclass
@register_game
class DominosGame(Game):
    """
    Dominos - A tile matching game.
    """

    players: list[DominosPlayer] = field(default_factory=list)
    options: DominosOptions = field(default_factory=DominosOptions)

    # Game State
    boneyard: list[Tile] = field(default_factory=list)
    board: list[Tile] = field(default_factory=list)

    # -1 means the board is completely empty
    left_end: int = -1
    right_end: int = -1

    # Track if the exposed end is a double (for All Fives scoring)
    left_is_double: bool = False
    right_is_double: bool = False

    consecutive_passes: int = 0
    starting_player_index: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Dominos"

    @classmethod
    def get_type(cls) -> str:
        return "dominos"

    @classmethod
    def get_category(cls) -> str:
        return "category-board-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        # Explicitly exclude "total_score" and "high_score" per requirements
        return ["rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> DominosPlayer:
        return DominosPlayer(id=player_id, name=name, is_bot=is_bot)

    def _get_playable_tiles(self, player: DominosPlayer) -> list[Tile]:
        """Returns a list of tiles in the player's hand that can be played."""
        if self.left_end == -1 and self.right_end == -1:
            return player.hand.copy()

        playable = []
        for tile in player.hand:
            if tile.matches(self.left_end) or tile.matches(self.right_end):
                playable.append(tile)
        return playable

    def _can_play(self, player: DominosPlayer) -> bool:
        """Check if the player has at least one playable tile."""
        return len(self._get_playable_tiles(player)) > 0

    def _sort_hand(self, player: DominosPlayer) -> None:
        """Sort tiles by total pips, then end1."""
        player.hand.sort(key=lambda t: (t.pips, max(t.end1, t.end2), min(t.end1, t.end2)), reverse=True)

    # ==========================================================================
    # Action Sets & Visibility
    # ==========================================================================

    def create_turn_action_set(self, player: DominosPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # The actual tiles will be added dynamically in _update_turn_actions

        # Keybind-only actions
        action_set.add(
            Action(
                id="check_board",
                label=Localization.get(locale, "dominos-check-board"),
                handler="_action_check_board",
                is_enabled="_is_check_enabled",
                is_hidden="_is_hidden_always",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="check_hands",
                label=Localization.get(locale, "dominos-check-hands"),
                handler="_action_check_hands",
                is_enabled="_is_check_enabled",
                is_hidden="_is_hidden_always",
                show_in_actions_menu=False,
            )
        )

        return action_set

    # WEB-SPECIFIC: Target order for Standard Actions
    web_target_order = ["check_board", "check_hands", "check_scores", "whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)

        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            locale = user.locale

            if not action_set.get_action("check_board"):
                 action_set.add(
                    Action(
                        id="check_board",
                        label=Localization.get(locale, "dominos-check-board"),
                        handler="_action_check_board",
                        is_enabled="_is_check_enabled",
                        is_hidden="_is_check_board_hidden_web",
                    )
                )
            if not action_set.get_action("check_hands"):
                 action_set.add(
                    Action(
                        id="check_hands",
                        label=Localization.get(locale, "dominos-check-hands"),
                        handler="_action_check_hands",
                        is_enabled="_is_check_enabled",
                        is_hidden="_is_check_hands_hidden_web",
                    )
                )

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
        super().setup_keybinds()

        user = None
        if hasattr(self, 'host_username') and self.host_username:
             player = self.get_player(self.host_username)
             if player:
                 user = self.get_user(player)
        locale = user.locale if user else "en"

        self.define_keybind("c", Localization.get(locale, "dominos-check-board"), ["check_board"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("h", Localization.get(locale, "dominos-check-hands"), ["check_hands"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("space", Localization.get(locale, "dominos-draw"), ["draw_tile"], state=KeybindState.ACTIVE)
        self.define_keybind("p", Localization.get(locale, "dominos-pass"), ["pass_turn"], state=KeybindState.ACTIVE)

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_hidden_always(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_check_board_hidden_web(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web" and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_hands_hidden_web(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web" and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

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

    def _is_tile_enabled(self, player: Player, action_id: str = None) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"

        # We need the tile ID. It's safe to parse here because _is_tile_enabled is called during resolution.
        if not action_id:
            return None # Not strictly checking yet

        tile_id = action_id.split("_", 2)[-1]

        dominos_player: DominosPlayer = player # type: ignore
        tile = next((t for t in dominos_player.hand if t.id == tile_id), None)

        if not tile:
            return "dominos-invalid-tile"

        if self.left_end != -1 and self.right_end != -1:
            if not tile.matches(self.left_end) and not tile.matches(self.right_end):
                return "dominos-cannot-play-tile"

        return None

    def _is_tile_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_draw_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.options.game_mode == "block":
            return "dominos-mode-no-draw"
        if not self.boneyard:
            return "dominos-boneyard-empty"

        dominos_player: DominosPlayer = player # type: ignore
        if self._can_play(dominos_player):
            return "dominos-can-play"

        return None

    def _is_draw_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        # Always hide from the visual menu, let it be keybind only, except for Web client?
        # Standard PlayAural often hides draw actions in card games if they're keybound,
        # but let's make it visible so it's clear what to do, OR keep it hidden and rely on keybind Space.
        # User requested: "For the Draw action, strictly use only the Space key. Do not use the 'd' key."
        # However, they also said: "rely on the standard PlayAural action list navigation".
        # Draw is usually visible if you MUST draw.
        dominos_player: DominosPlayer = player # type: ignore
        if self._can_play(dominos_player):
            return Visibility.HIDDEN
        if self.options.game_mode == "block" or not self.boneyard:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_pass_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"

        dominos_player: DominosPlayer = player # type: ignore
        if self._can_play(dominos_player):
            return "dominos-can-play"

        if self.options.game_mode != "block" and self.boneyard:
             return "dominos-must-draw"

        return None

    def _is_pass_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN

        dominos_player: DominosPlayer = player # type: ignore
        if self._can_play(dominos_player):
            return Visibility.HIDDEN
        if self.options.game_mode != "block" and self.boneyard:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_left_right_options(self, player: Player) -> list[str]:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return [
            Localization.get(locale, "dominos-left", pips=self.left_end),
            Localization.get(locale, "dominos-right", pips=self.right_end)
        ]

    def _bot_select_left_right(self, player: Player) -> str:
        # Bots just pick Left or Right at random if both are valid
        user = self.get_user(player)
        locale = user.locale if user else "en"
        options = [
            Localization.get(locale, "dominos-left", pips=self.left_end),
            Localization.get(locale, "dominos-right", pips=self.right_end)
        ]
        return random.choice(options)

    def _update_turn_actions(self, player: DominosPlayer) -> None:
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        user = self.get_user(player)
        locale = user.locale if user else "en"

        is_current = self.current_player == player

        # Remove dynamic tile actions
        turn_set.remove_by_prefix("play_tile_")
        turn_set.remove("draw_tile")
        turn_set.remove("pass_turn")

        if self.status == "playing" and not player.is_spectator:
            # We add all tiles to the menu. The _is_tile_enabled function will gray them out if they are unplayable.
            for tile in player.hand:
                action_id = f"play_tile_{tile.id}"

                # Check if this tile needs a Left/Right prompt
                # It only needs a prompt if it matches BOTH ends, AND the ends are different
                # If ends are the same (e.g., both 4), there's no strategic difference, but we might still prompt?
                # User said: "If the selected tile matches BOTH open ends."
                # If board is empty, any tile matches (left=-1, right=-1). But it's only one placement.
                needs_prompt = False
                if self.left_end != -1 and self.right_end != -1:
                    if tile.matches(self.left_end) and tile.matches(self.right_end) and self.left_end != self.right_end:
                         # Wait, if left_end == right_end, playing it on the left vs right doesn't matter functionally,
                         # but maybe we should still prompt or just auto-play. Let's strictly auto-play if ends are identical
                         # to reduce unnecessary prompts. Actually, let's just prompt if it matches both.
                         # Wait, if both ends are 4, playing a 4-5 on left makes ends 5 and 4. Playing on right makes ends 4 and 5.
                         # Strategically identical. We can just auto play.
                         if self.left_end != self.right_end:
                             needs_prompt = True

                input_request = None
                if is_current and needs_prompt:
                     input_request = MenuInput(
                        prompt="dominos-prompt-side",
                        options="_get_left_right_options",
                        bot_select="_bot_select_left_right",
                     )

                turn_set.add(
                    Action(
                        id=action_id,
                        label=tile.to_string(locale),
                        handler="_action_play_tile",
                        is_enabled="_is_tile_enabled",
                        is_hidden="_is_tile_hidden",
                        input_request=input_request,
                        show_in_actions_menu=True,
                    )
                )

            # Draw action
            turn_set.add(
                Action(
                    id="draw_tile",
                    label=Localization.get(locale, "dominos-draw"),
                    handler="_action_draw",
                    is_enabled="_is_draw_enabled",
                    is_hidden="_is_draw_hidden",
                    show_in_actions_menu=True,
                )
            )

            # Pass action
            turn_set.add(
                Action(
                    id="pass_turn",
                    label=Localization.get(locale, "dominos-pass"),
                    handler="_action_pass",
                    is_enabled="_is_pass_enabled",
                    is_hidden="_is_pass_hidden",
                    show_in_actions_menu=True,
                )
            )

            # WEB-SPECIFIC: For web, prioritize draw/pass to top if they must be used
            if user and getattr(user, "client_type", "") == "web" and is_current:
                 if not self._can_play(player):
                      if "draw_tile" in turn_set._order:
                          turn_set._order.remove("draw_tile")
                          turn_set._order.insert(0, "draw_tile")
                      if "pass_turn" in turn_set._order:
                          turn_set._order.remove("pass_turn")
                          turn_set._order.insert(0, "pass_turn")

    def _update_all_turn_actions(self) -> None:
        for player in self.players:
            if isinstance(player, DominosPlayer):
                self._update_turn_actions(player)

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        active_players = self.get_active_players()
        for p in active_players:
            p.score = 0

        self.play_music("game_pig/mus.ogg")  # Using pig music as default happy music

        # Decide starting player randomly for the first round
        self.starting_player_index = random.randint(0, len(active_players) - 1)

        self._start_round()

    def _create_boneyard(self) -> None:
        """Create a standard double-six set of dominos."""
        self.boneyard = []
        for i in range(7):
            for j in range(i, 7):
                self.boneyard.append(Tile(i, j))
        random.shuffle(self.boneyard)

    def _start_round(self) -> None:
        self.round += 1
        self.board = []
        self.left_end = -1
        self.right_end = -1
        self.left_is_double = False
        self.right_is_double = False
        self.consecutive_passes = 0

        active_players = self.get_active_players()
        self.set_turn_players(active_players)
        self.turn_index = self.starting_player_index

        self._create_boneyard()

        # Deal tiles (usually 7 for 2-4 players)
        # If 4 players, 28 tiles total, 0 in boneyard (unless we deal fewer?)
        # Standard draw rules: 7 tiles for 2, 3, or 4 players. For 4 players, boneyard is empty!
        # This is standard.
        tiles_to_deal = 7
        for player in active_players:
            player.hand = [self.boneyard.pop() for _ in range(tiles_to_deal)]
            self._sort_hand(player)

        # Shuffle sounds
        shuffle_sound = random.choice(["shuffle1.ogg", "shuffle2.ogg"])
        self.play_sound(f"game_dominos/{shuffle_sound}")

        self.broadcast_l("game-round-start", round=self.round)

        first_player = self.turn_players[self.turn_index]
        self.broadcast_l("dominos-first-player", player=first_player.name)

        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not player:
            return

        self.announce_turn()

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(15, 30))

        self._update_all_turn_actions()
        self.rebuild_all_menus()

    def _advance_turn(self) -> None:
        self.advance_turn(announce=False)
        self._start_turn()

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_play_tile(self, player: Player, *args) -> None:
        if not isinstance(player, DominosPlayer):
            return

        if self.current_player != player:
            return

        input_value = None
        if len(args) == 1:
            action_id = args[0]
        elif len(args) == 2:
            action_id, input_value = args
        else:
            return

        tile_id = action_id.split("_", 2)[-1]
        tile = next((t for t in player.hand if t.id == tile_id), None)

        if not tile:
            return

        # Determine side
        side = None
        user = self.get_user(player)
        locale = user.locale if user else "en"

        if self.left_end == -1 and self.right_end == -1:
            # First tile
            side = "first"
            self.left_end = tile.end1
            self.right_end = tile.end2
            if tile.is_double:
                self.left_is_double = True
                self.right_is_double = True
            else:
                self.left_is_double = False
                self.right_is_double = False
        else:
            matches_left = tile.matches(self.left_end)
            matches_right = tile.matches(self.right_end)

            if matches_left and matches_right and self.left_end != self.right_end:
                # Requires input
                if not input_value:
                    return # Should have input

                left_str = Localization.get(locale, "dominos-left", pips=self.left_end)
                right_str = Localization.get(locale, "dominos-right", pips=self.right_end)

                if input_value == left_str:
                    side = "left"
                elif input_value == right_str:
                    side = "right"
                else:
                    return # Invalid input
            else:
                # Auto-play on the valid side (or either side if left_end == right_end)
                if matches_left:
                    side = "left"
                elif matches_right:
                    side = "right"
                else:
                    return # Shouldn't happen due to enabled checks

        if side == "left":
            # Update left end
            self.left_end = tile.end2 if tile.end1 == self.left_end else tile.end1
            self.left_is_double = tile.is_double
        elif side == "right":
            # Update right end
            self.right_end = tile.end1 if tile.end2 == self.right_end else tile.end2
            self.right_is_double = tile.is_double

        # Play tile
        player.hand.remove(tile)
        self.board.append(tile)
        self.consecutive_passes = 0

        self.play_sound("game_dominos/knock.ogg")

        # Announce play
        for p in self.players:
            u = self.get_user(p)
            if not u: continue

            t_str = tile.to_string(u.locale)

            if side == "first":
                 msg = Localization.get(u.locale, "dominos-played-first", tile=t_str)
            else:
                 side_str = Localization.get(u.locale, f"dominos-side-{side}")
                 msg = Localization.get(u.locale, "dominos-played-side", tile=t_str, side=side_str)

            if p == player:
                 u.speak_l("dominos-you-played", buffer="game", msg=msg)
            else:
                 u.speak_l("dominos-player-played", buffer="game", player=player.name, msg=msg)

        # All Fives Check
        if self.options.game_mode == "all_fives":
            self._check_all_fives(player)

        self._check_round_end()

    def _check_all_fives(self, player: DominosPlayer) -> None:
        """Calculate score for All Fives mode."""
        if self.left_end == -1 or self.right_end == -1:
            return

        total = 0

        # If it's the very first tile and it's a double, it acts as a single entity
        # with total pips (left + right). To avoid double-counting the first double tile,
        # we check if board has only 1 tile.
        if len(self.board) == 1:
            tile = self.board[0]
            total = tile.pips
        else:
            left_val = self.left_end * 2 if self.left_is_double else self.left_end
            right_val = self.right_end * 2 if self.right_is_double else self.right_end
            total = left_val + right_val

        if total > 0 and total % 5 == 0:
            player.score += total
            points = total // 5

            # Play tokens
            for _ in range(points):
                snd = random.choice([1, 2, 3, 4, 5, 6, 7])
                self.play_sound(f"game_squares/token{snd}.ogg")

            self.broadcast_l("dominos-scored-fives", player=player.name, points=total)

            # Check for win immediately in All Fives? Yes, target_score can be reached mid-round.
            if player.score >= self.options.target_score:
                self._declare_winner(player)
                return

    def _action_draw(self, player: Player, action_id: str) -> None:
        if not isinstance(player, DominosPlayer):
            return

        if self.current_player != player:
            return

        if not self.boneyard:
            return

        tile = self.boneyard.pop()
        player.hand.append(tile)
        self._sort_hand(player)

        self.play_sound("game_cards/draw1.ogg")

        for p in self.players:
            u = self.get_user(p)
            if not u: continue

            if p == player:
                u.speak_l("dominos-you-drew", buffer="game", tile=tile.to_string(u.locale))
            else:
                u.speak_l("dominos-player-drew", buffer="game", player=player.name)

        # In Draw mode, they must keep drawing until they can play.
        # We do NOT advance the turn. We just update actions and wait.
        # The engine will now see they have a playable tile (or they need to draw again).

        # Bot logic needs a jolt to act again if it still can't play or if it can
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(10, 20))

        self._update_all_turn_actions()
        self.rebuild_all_menus()

    def _action_pass(self, player: Player, action_id: str) -> None:
        if not isinstance(player, DominosPlayer):
            return

        if self.current_player != player:
            return

        self.consecutive_passes += 1

        self.play_sound("game_dominos/blocked.ogg")
        self.broadcast_l("dominos-player-passed", player=player.name)

        self._check_round_end()

    def _action_check_board(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user: return

        if self.left_end == -1 and self.right_end == -1:
            user.speak_l("dominos-board-empty", buffer="game")
        else:
            user.speak_l("dominos-board-status", buffer="game", left=self.left_end, right=self.right_end)

    def _action_check_hands(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user: return

        for p in self.get_active_players():
            if isinstance(p, DominosPlayer):
                user.speak_l("dominos-hand-count", buffer="game", player=p.name, count=len(p.hand))

    # ==========================================================================
    # Round & Game End
    # ==========================================================================

    def _check_round_end(self) -> None:
        if not self.game_active:
            return

        active_players = self.get_active_players()

        # Condition 1: Domino (Empty hand)
        winner = None
        for player in active_players:
            if isinstance(player, DominosPlayer) and len(player.hand) == 0:
                winner = player
                break

        # Condition 2: Blocked Game
        blocked = self.consecutive_passes >= len(active_players)

        if winner:
            self.play_sound("game_pig/win.ogg") # Small win sound for round
            self.broadcast_l("dominos-domino", player=winner.name)
            self._score_round(winner, blocked=False)
        elif blocked:
            self.play_sound("game_pig/lose.ogg")
            self.broadcast_l("dominos-game-blocked")
            # Find player with lowest pips
            min_pips = float('inf')
            for p in active_players:
                if isinstance(p, DominosPlayer):
                    pips = sum(t.pips for t in p.hand)
                    if pips < min_pips:
                        min_pips = pips
                        winner = p

            # If tie for lowest pips, it's a tie, no one scores in standard dominos.
            # But let's check if there's a strict single winner
            lowest_count = sum(1 for p in active_players if isinstance(p, DominosPlayer) and sum(t.pips for t in p.hand) == min_pips)

            if lowest_count == 1 and winner:
                self.broadcast_l("dominos-lowest-pips", player=winner.name, pips=min_pips)
                self._score_round(winner, blocked=True)
            else:
                self.broadcast_l("dominos-tie")
                # Advance starting player
                self.starting_player_index = (self.starting_player_index + 1) % len(active_players)
                self._start_round()
        else:
            self._advance_turn()

    def _score_round(self, winner: DominosPlayer, blocked: bool) -> None:
        total_opponent_pips = 0
        winner_pips = sum(t.pips for t in winner.hand)

        for player in self.get_active_players():
            if isinstance(player, DominosPlayer) and player != winner:
                pips = sum(t.pips for t in player.hand)
                total_opponent_pips += pips

        # In blocked game, winner's pips are subtracted from the opponents' total
        points = total_opponent_pips
        if blocked:
            points = max(0, total_opponent_pips - winner_pips)

        winner.score += points
        self.broadcast_l("dominos-awarded-points", player=winner.name, points=points, total=winner.score)

        if winner.score >= self.options.target_score:
            self._declare_winner(winner)
        else:
            # Winner starts next round
            active_players = self.get_active_players()
            self.starting_player_index = active_players.index(winner)
            self._start_round()

    def _declare_winner(self, winner: DominosPlayer) -> None:
        self.play_sound("game_pig/wingame.ogg")
        self.broadcast_l("game-player-wins", player=winner.name)
        self.finish_game()

    def build_game_result(self) -> GameResult:
        sorted_players = sorted(
            [p for p in self.get_active_players() if isinstance(p, DominosPlayer)],
            key=lambda p: p.score,
            reverse=True
        )

        final_scores = {p.name: p.score for p in sorted_players}
        winner = sorted_players[0] if sorted_players else None

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(player_id=p.id, player_name=p.name, is_bot=p.is_bot)
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": winner.score if winner else 0,
                "final_scores": final_scores,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
                "game_mode": self.options.game_mode,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(
                Localization.get(locale, "dominos-line-format", rank=i, player=name, points=points_str)
            )

        return lines

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def on_tick(self) -> None:
        super().on_tick()
        if not self.game_active:
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: DominosPlayer) -> str | None:
        return bot_think(self, player)
