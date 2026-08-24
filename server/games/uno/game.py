from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, BoolOption, option_field
from ...game_utils.bot_helper import BotHelper
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.bot import Bot
from ...users.base import User
from . import cards
from .cards import UnoCard
from .bot import bot_think_turn, bot_think_out_of_turn, bot_choose_color

# Tick constants (20 ticks/sec).
HAND_END_TICKS = 5 * 20
WILD_TRANSITION_TICKS = 15
UNO_CALLOUT_PENALTY = 2

SCORING_FIRST = "first_to_limit"
SCORING_ELIMINATION = "elimination"

SCORING_CHOICES = [SCORING_FIRST, SCORING_ELIMINATION]
SCORING_LABELS = {
    SCORING_FIRST: "uno-scoring-first",
    SCORING_ELIMINATION: "uno-scoring-elimination",
}


@dataclass
class UnoOptions(GameOptions):
    """Options for UNO."""

    winning_score: int = option_field(
        IntOption(
            min_val=10,
            max_val=2000,
            default=300,
            value_key="score",
            label="uno-set-winning-score",
            prompt="uno-enter-winning-score",
            change_msg="uno-option-changed-winning-score",
        )
    )
    scoring_mode: str = option_field(
        MenuOption(
            choices=SCORING_CHOICES,
            default=SCORING_FIRST,
            value_key="mode",
            label="uno-set-scoring-mode",
            prompt="uno-select-scoring-mode",
            change_msg="uno-option-changed-scoring-mode",
            choice_labels=SCORING_LABELS,
        )
    )
    skip_after_draw: bool = option_field(
        BoolOption(
            default=True,
            label="uno-set-skip-after-draw",
            change_msg="uno-option-changed-skip-after-draw",
        )
    )
    responses: bool = option_field(
        BoolOption(
            default=False,
            label="uno-set-responses",
            change_msg="uno-option-changed-responses",
        )
    )
    advanced_responses: bool = option_field(
        BoolOption(
            default=False,
            label="uno-set-advanced-responses",
            change_msg="uno-option-changed-advanced-responses",
        ),
        visible_when=("responses", lambda v: bool(v)),
    )
    wait_for_draw_responses: bool = option_field(
        BoolOption(
            default=False,
            label="uno-set-wait-for-draw-responses",
            change_msg="uno-option-changed-wait-for-draw-responses",
        ),
        visible_when=("responses", lambda v: bool(v)),
    )
    bluff: bool = option_field(
        BoolOption(
            default=True,
            label="uno-set-bluff",
            change_msg="uno-option-changed-bluff",
        )
    )
    straights: bool = option_field(
        BoolOption(
            default=False,
            label="uno-set-straights",
            change_msg="uno-option-changed-straights",
        )
    )
    interceptions: bool = option_field(
        BoolOption(
            default=False,
            label="uno-set-interceptions",
            change_msg="uno-option-changed-interceptions",
        )
    )
    super_interceptions: bool = option_field(
        BoolOption(
            default=False,
            label="uno-set-super-interceptions",
            change_msg="uno-option-changed-super-interceptions",
        ),
        visible_when=("interceptions", lambda v: bool(v)),
    )
    zero_seven_rule: bool = option_field(
        BoolOption(
            default=False,
            label="uno-set-zero-seven",
            change_msg="uno-option-changed-zero-seven",
        )
    )
    free_draws: int = option_field(
        IntOption(
            min_val=0,
            max_val=999,
            default=0,
            value_key="count",
            label="uno-set-free-draws",
            prompt="uno-enter-free-draws",
            change_msg="uno-option-changed-free-draws",
        )
    )


@dataclass
class UnoPlayer(Player):
    hand: list[UnoCard] = field(default_factory=list)
    score: int = 0
    penalty_points: int = 0  # invalid-interception penalties, reset each round
    said_uno: bool = False
    uno_grace_ticks: int = 0
    uno_window_ticks: int = 0
    free_draws_used: int = 0
    card_sort_mode: str = "number"  # color | number | none
    turn_has_drawn: bool = False


@register_game
@dataclass
class UnoGame(Game):
    """UNO game implementation."""

    players: list[UnoPlayer] = field(default_factory=list)
    options: UnoOptions = field(default_factory=UnoOptions)

    deck: list[UnoCard] = field(default_factory=list)
    discard_pile: list[UnoCard] = field(default_factory=list)
    current_color: int | None = None

    awaiting_wild_color: bool = False
    wild_color_player_id: str = ""
    pending_wild_type: str = ""
    wild_wait_ticks: int = 0
    opening_wild_color: bool = False

    dealer_index: int = -1

    last_player_id: str = ""  # who played the current top (straights / bluff anchor)

    # Draw-stack obligation (Phase 2 stacking). In core play, draw-two / draw-four
    # resolve immediately and these stay at 0 / "".
    cards_to_draw: int = 0
    draw_type: str = ""

    # Bluff (Phase 2).
    bluff_challenge_available: bool = False
    is_bluff: bool = False

    # Deferred round end while a draw obligation is still being resolved (Phase 2,
    # wait_for_draw_responses).
    pending_round_winner_id: str = ""

    # Seven-swap target selection (Phase 2, zero_seven_rule).
    awaiting_swap_target: bool = False
    swap_player_id: str = ""
    # When a seven is intercepted, the interceptor "takes the floor" and replays
    # after the swap, instead of the turn advancing.
    swap_replay: bool = False

    # Straights (Phase 3).
    straight_color: int | None = None
    straight_value: int | None = None
    straight_dir: int = 0  # 0 unset, +1 ascending, -1 descending

    intro_wait_ticks: int = 0
    hand_wait_ticks: int = 0

    consecutive_passes: int = 0  # blocked-hand detection

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> UnoPlayer:
        return UnoPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Metadata
    # ==========================================================================

    @classmethod
    def get_name(cls) -> str:
        return "UNO"

    @classmethod
    def get_type(cls) -> str:
        return "uno"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 10

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    # ==========================================================================
    # Lobby roster
    # ==========================================================================

    def _action_add_bot(self, player: Player, bot_name: str, action_id: str) -> None:
        bot_name = self._resolve_add_bot_name(player, bot_name)
        if bot_name is None:
            return
        bot = self.add_player(bot_name, Bot(bot_name))
        self.broadcast_l("table-joined", buffer="game", player=bot_name)
        self.play_table_join_sound(bot, is_bot=True)
        self.refresh_menus()

    def _action_remove_bot(self, player: Player, action_id: str) -> None:
        for i in range(len(self.players) - 1, -1, -1):
            if self.players[i].is_bot:
                bot = self.players[i]
                self.remove_player(bot.id)
                self.play_table_leave_sound(bot, is_bot=True)
                break
        self.refresh_menus()

    def _perform_leave_game(self, player: Player) -> None:
        if player.is_spectator:
            self.remove_spectator(player.id)
            if self._table:
                self._table.remove_member(player.name)
            self.play_table_leave_sound(player, is_spectator=True)
            self.refresh_menus()
            return

        if self.status == "playing" and not player.is_bot:
            other_humans = any(
                not p.is_bot and not p.is_spectator and p.id != player.id
                for p in self.players
            )
            if other_humans:
                if self._replace_with_bot(player):
                    self.play_table_leave_sound(
                        player,
                        is_bot=False,
                        is_spectator=False,
                    )
                self.refresh_menus()
                return

        was_bot = player.is_bot
        self.remove_player(player.id)
        self.play_table_leave_sound(
            player,
            is_bot=was_bot,
            is_spectator=False,
        )
        if self.status == "waiting" and self._table:
            self._table.remove_member(player.name)

        has_humans = any(not p.is_bot and not p.is_spectator for p in self.players)
        if not has_humans:
            self.destroy()
            return
        self.refresh_menus()

    # ==========================================================================
    # Action sets / keybinds
    # ==========================================================================

    def create_turn_action_set(self, player: UnoPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        self._populate_turn_actions(action_set, player)
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="read_top",
                label=Localization.get(locale, "uno-read-top"),
                handler="_action_read_top",
                is_enabled="_is_info_enabled",
                is_hidden="_is_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_color",
                label=Localization.get(locale, "uno-read-color"),
                handler="_action_read_color",
                is_enabled="_is_info_enabled",
                is_hidden="_is_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_counts",
                label=Localization.get(locale, "uno-read-counts"),
                handler="_action_read_counts",
                is_enabled="_is_info_enabled",
                is_hidden="_is_info_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "uno-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_info_enabled",
                is_hidden="_is_info_hidden",
            )
        )
        action_set.add(
            Action(
                id="sort_color",
                label=Localization.get(locale, "uno-sort-color"),
                handler="_action_sort_color",
                is_enabled="_is_info_enabled",
                is_hidden="_is_info_hidden",
            )
        )
        action_set.add(
            Action(
                id="sort_number",
                label=Localization.get(locale, "uno-sort-number"),
                handler="_action_sort_number",
                is_enabled="_is_info_enabled",
                is_hidden="_is_info_hidden",
            )
        )

        if self.is_touch_client(user):
            target_order = [
                "read_top",
                "read_color",
                "read_counts",
                "read_hand",
                "sort_color",
                "sort_number",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            self._order_touch_standard_actions(action_set, target_order)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("space", "Draw", ["draw"], state=KeybindState.ACTIVE)
        self.define_keybind("u", "Say UNO or call out", ["uno"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "Read top card", ["read_top"], include_spectators=True)
        self.define_keybind("v", "Read current color", ["read_color"], include_spectators=True)
        self.define_keybind("e", "Read counts", ["read_counts"], include_spectators=True)
        self.define_keybind("d", "Read your hand value", ["read_hand"])
        self.define_keybind("shift+c", "Sort by color", ["sort_color"])
        self.define_keybind("shift+n", "Sort by number", ["sort_number"])
        # Color selection (active only while choosing a wild color).
        self.define_keybind("r", "Choose red", ["color_red"], state=KeybindState.ACTIVE)
        self.define_keybind("y", "Choose yellow", ["color_yellow"], state=KeybindState.ACTIVE)
        self.define_keybind("g", "Choose green", ["color_green"], state=KeybindState.ACTIVE)
        self.define_keybind("b", "Choose blue", ["color_blue"], state=KeybindState.ACTIVE)

    # ==========================================================================
    # Menu syncing
    # ==========================================================================

    def before_menu_build(self, player: Player) -> None:
        self._sync_turn_actions(player)

    def _sync_turn_actions(self, player: Player) -> None:
        if not isinstance(player, UnoPlayer):
            return
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return
        turn_set.remove_by_prefix("play_card_")
        turn_set.remove_by_prefix("swap_target_")
        for aid in (
            "draw", "pass", "uno", "bluff_challenge",
            "color_red", "color_yellow", "color_green", "color_blue",
        ):
            turn_set.remove(aid)
        self._populate_turn_actions(turn_set, player)

    def _populate_turn_actions(self, turn_set: ActionSet, player: UnoPlayer) -> None:
        if self.status != "playing" or player.is_spectator:
            return
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return
        locale = self._player_locale(player)

        # Card buttons (sorted for display).
        for card in self._sorted_hand(player):
            turn_set.add(
                Action(
                    id=f"play_card_{card.id}",
                    label="",
                    handler="_action_play_card",
                    is_enabled="_is_play_card_enabled",
                    is_hidden="_is_play_card_hidden",
                    get_label="_get_card_label",
                    show_in_actions_menu=False,
                )
            )

        # Color choice actions are always registered (so their keybinds resolve);
        # they are hidden/disabled unless this player must choose a wild color.
        for cid, col in (
            ("color_red", cards.RED), ("color_yellow", cards.YELLOW),
            ("color_green", cards.GREEN), ("color_blue", cards.BLUE),
        ):
            turn_set.add(
                Action(
                    id=cid,
                    label=cards.color_name(col, locale),
                    handler="_action_choose_color",
                    is_enabled="_is_color_choice_enabled",
                    is_hidden="_is_color_choice_hidden",
                    show_in_actions_menu=False,
                )
            )

        # Seven-swap target selection.
        if self.awaiting_swap_target and self.swap_player_id == player.id:
            for other in self.alive_players:
                if other.id == player.id:
                    continue
                turn_set.add(
                    Action(
                        id=f"swap_target_{other.id}",
                        label=Localization.get(locale, "uno-swap-with", player=other.name),
                        handler="_action_choose_swap",
                        is_enabled="_is_swap_choice_enabled",
                        is_hidden="_is_swap_choice_hidden",
                        show_in_actions_menu=False,
                    )
                )
            # Declining the swap is a legitimate choice for a seven.
            turn_set.add(
                Action(
                    id="swap_target_none",
                    label=Localization.get(locale, "uno-swap-none"),
                    handler="_action_choose_swap",
                    is_enabled="_is_swap_choice_enabled",
                    is_hidden="_is_swap_choice_hidden",
                    show_in_actions_menu=False,
                )
            )

        # Bluff challenge (the player facing a Wild Draw Four, never its player).
        if (
            self.bluff_challenge_available
            and self.current_player == player
            and player.id != self.last_player_id
        ):
            turn_set.add(
                Action(
                    id="bluff_challenge",
                    label=Localization.get(locale, "uno-bluff-challenge"),
                    handler="_action_bluff_challenge",
                    is_enabled="_is_bluff_enabled",
                    is_hidden="_is_bluff_hidden",
                    show_in_actions_menu=False,
                )
            )

        # UNO say / call-out.
        turn_set.add(
            Action(
                id="uno",
                label=Localization.get(locale, "uno-say-uno"),
                handler="_action_uno",
                is_enabled="_is_uno_enabled",
                is_hidden="_is_uno_hidden",
                show_in_actions_menu=False,
            )
        )

        # Draw (current player only). There is no pass: drawing an unplayable
        # card skips the turn automatically. Draw-penalty skip behavior is
        # resolved separately in _accept_draw_obligation.
        if (
            self.current_player == player
            and not self._is_wild_locked()
            and not self.awaiting_swap_target
        ):
            turn_set.add(
                Action(
                    id="draw",
                    label=Localization.get(locale, "uno-draw"),
                    handler="_action_draw",
                    is_enabled="_is_draw_enabled",
                    is_hidden="_is_draw_hidden",
                    show_in_actions_menu=False,
                )
            )

        user = self.get_user(player)
        if self.is_touch_client(user) and "uno" in turn_set._order:
            turn_set._order.remove("uno")
            turn_set._order.insert(0, "uno")

    # ==========================================================================
    # Game flow
    # ==========================================================================

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = super().prestart_validate()
        if not self.options.responses:
            if self.options.advanced_responses:
                errors.append("uno-error-advanced-responses-require-responses")
            if self.options.wait_for_draw_responses:
                errors.append("uno-error-wait-responses-require-responses")
        if not self.options.interceptions and self.options.super_interceptions:
            errors.append("uno-error-super-interceptions-require-interceptions")
        return errors

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self.round = 0
        self.turn_direction = 1
        self.awaiting_wild_color = False
        self.wild_wait_ticks = 0
        self._normalize_options()
        self._sync_table_status()

        self.play_music("game_uno/music.ogg")

        active_players = self.get_active_players()
        self.set_turn_players(active_players)
        for p in active_players:
            if isinstance(p, UnoPlayer):
                p.score = 0
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])
        self._sync_team_scores()

        # Begin the first hand immediately (no intro delay).
        self._start_new_hand()

    def _normalize_options(self) -> None:
        """Silently correct invalid option combinations before play.

        Dependent options have no effect without their parent, so a stale
        combination (e.g. super interceptions on while interceptions are off)
        is cleared rather than allowed to take effect surprisingly.
        """
        o = self.options
        if not o.interceptions and o.super_interceptions:
            o.super_interceptions = False
        if not o.responses and o.advanced_responses:
            o.advanced_responses = False
        if not o.responses and o.wait_for_draw_responses:
            o.wait_for_draw_responses = False

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return
        if self.wild_wait_ticks > 0:
            self.wild_wait_ticks -= 1
            if self.wild_wait_ticks == 0:
                self._advance_turn()
            return
        if self.hand_wait_ticks > 0:
            self.hand_wait_ticks -= 1
            if self.hand_wait_ticks == 0:
                self._start_new_hand()
            return
        if self.intro_wait_ticks > 0:
            self.intro_wait_ticks -= 1
            if self.intro_wait_ticks == 0:
                self._start_new_hand()
            return

        self._tick_uno_window()
        self._tick_out_of_turn_bots()
        BotHelper.on_tick(self)
        self._resolve_stuck_turn()

    def _resolve_stuck_turn(self) -> None:
        """Safety net: end a turn that can neither play nor draw.

        With no pass action, a player who has already drawn (or cannot draw) and
        has nothing playable must have their turn ended by the engine. This also
        covers the case where an out-of-turn interception or straight changes the
        top card after the current player drew a then-playable card.
        """
        if (
            self.awaiting_wild_color
            or self.awaiting_swap_target
            or self.wild_wait_ticks > 0
            or self.hand_wait_ticks > 0
            or self.intro_wait_ticks > 0
            or self.cards_to_draw > 0
            or self.bluff_challenge_available
        ):
            return
        player = self.current_player
        if not isinstance(player, UnoPlayer):
            return
        if self._has_playable(player) or self._can_draw(player):
            return
        self._auto_skip(player)

    def _start_new_hand(self) -> None:
        self.round += 1
        self.turn_direction = 1
        self.turn_skip_count = 0
        self.awaiting_wild_color = False
        self.wild_color_player_id = ""
        self.pending_wild_type = ""
        self.wild_wait_ticks = 0
        self.opening_wild_color = False
        self.cards_to_draw = 0
        self.draw_type = ""
        self.bluff_challenge_available = False
        self.is_bluff = False
        self.pending_round_winner_id = ""
        self.awaiting_swap_target = False
        self.swap_player_id = ""
        self.swap_replay = False
        self.last_player_id = ""
        self.consecutive_passes = 0
        self._clear_straight()

        alive = self.alive_players
        if len(alive) <= 1:
            self._end_game(alive[0] if alive else None)
            return

        self.broadcast_l("uno-new-hand", buffer="game", round=self.round)
        self.play_sound(f"game_cards/shuffle{random.randint(1, 3)}.ogg")

        self.deck = cards.build_deck()
        cards.shuffle(self.deck)
        self.discard_pile = []
        self.current_color = None

        for p in alive:
            p.hand = []
            p.said_uno = False
            p.uno_grace_ticks = 0
            p.uno_window_ticks = 0
            p.penalty_points = 0
            p.free_draws_used = 0
            p.turn_has_drawn = False

        for _ in range(7):
            for p in alive:
                card = self._draw_card()
                if card:
                    p.hand.append(card)

        # Rotate dealer / first player.
        self.dealer_index = (self.dealer_index + 1) % len(self.turn_player_ids)
        self.turn_index = (self.dealer_index + 1) % len(self.turn_player_ids)

        start_card = self._draw_start_card()
        if start_card:
            self.discard_pile.append(start_card)
            self.current_color = None if start_card.color == cards.WILD else start_card.color
            self.last_player_id = ""
            self._broadcast_start_card(start_card)
            self.broadcast_l("uno-dealt-cards", buffer="game", cards=7)
            if self._apply_start_card_effect(start_card):
                return

        self._start_turn()

    def _draw_start_card(self) -> UnoCard | None:
        """Flip the opening card, re-flipping only Wild Draw Four per UNO rules."""
        while self.deck:
            card = self.deck.pop()
            if card.type == cards.WILD_DRAW_FOUR:
                self.deck.append(card)
                cards.shuffle(self.deck)
                continue
            return card
        return None

    def _apply_start_card_effect(self, card: UnoCard) -> bool:
        """Apply official opening-card effects.

        Returns True when play is paused waiting for an opening Wild color.
        """
        if card.type == cards.NUMBER:
            return False
        if card.type == cards.SKIP:
            skipped = self.current_player
            if skipped:
                self.on_player_skipped(skipped)
            self.turn_index = (
                self.turn_index + self.turn_direction
            ) % len(self.turn_player_ids)
            return False
        if card.type == cards.DRAW_TWO:
            target = self.current_player
            if isinstance(target, UnoPlayer):
                self._draw_for_player(target, 2)
                self.on_player_skipped(target)
            self.turn_index = (
                self.turn_index + self.turn_direction
            ) % len(self.turn_player_ids)
            return False
        if card.type == cards.REVERSE:
            self.reverse_turn_direction()
            self.broadcast_l("uno-direction-reversed", buffer="game")
            self.turn_index = self.dealer_index % len(self.turn_player_ids)
            return False
        if card.type == cards.WILD_CARD:
            chooser = self.current_player
            if not isinstance(chooser, UnoPlayer):
                return False
            self.awaiting_wild_color = True
            self.opening_wild_color = True
            self.wild_color_player_id = chooser.id
            self.pending_wild_type = ""
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p.id == chooser.id:
                    user.speak_l("uno-choose-opening-color-you", buffer="game")
                else:
                    user.speak_l(
                        "uno-choose-opening-color-player",
                        buffer="game",
                        player=chooser.name,
                    )
            if chooser.is_bot:
                BotHelper.jolt_bot(chooser, ticks=random.randint(15, 25))
            self.request_menu_focus(chooser, "color_red")
            self.refresh_menus()
            return True
        return False

    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, UnoPlayer):
            return
        player.turn_has_drawn = False
        player.free_draws_used = 0
        # Clear any stale out-of-turn pending action for the new current player.
        player.bot_pending_action = None

        # A draw obligation the player cannot respond to (and cannot challenge)
        # is resolved automatically. When draw penalties skip the target, resolve
        # it without first announcing a turn that is never taken.
        forced_draw = (
            self.cards_to_draw > 0
            and not self.bluff_challenge_available
            and not self._has_playable(player)
        )
        if forced_draw and self.options.skip_after_draw:
            self._accept_draw_obligation(player)
            return

        self.announce_turn()
        if forced_draw:
            self._accept_draw_obligation(player)
            return
        # Truly stuck: nothing playable and the deck is exhausted. Skip the turn.
        if (
            self.cards_to_draw == 0
            and not self._has_playable(player)
            and not self._can_draw(player)
        ):
            self._auto_skip(player)
            return
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 35))
        self.refresh_menus()

    def _auto_skip(self, player: UnoPlayer) -> None:
        """End a player's turn when they cannot play (no pass action exists)."""
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            if p.id == player.id:
                user.speak_l("uno-you-cant-play", buffer="game")
            else:
                user.speak_l("uno-cant-play", buffer="game", player=player.name)
        self.consecutive_passes += 1
        if self.consecutive_passes >= len(self.alive_players) and not self._deck_has_cards():
            self._handle_blocked_hand()
            return
        self._advance_turn()

    def _advance_turn(self) -> None:
        self.advance_turn(announce=False)
        self._start_turn()

    def on_player_skipped(self, player: Player) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            if p.id == player.id:
                user.speak_l("uno-you-skipped", buffer="game")
            else:
                user.speak_l("game-player-skipped", buffer="game", player=player.name)

    # ==========================================================================
    # Turn actions
    # ==========================================================================

    def _action_play_card(self, player: Player, action_id: str) -> None:
        if not isinstance(player, UnoPlayer):
            return
        if (
            self._is_wild_locked()
            or self.awaiting_swap_target
            or self.hand_wait_ticks > 0
            or self.intro_wait_ticks > 0
        ):
            user = self.get_user(player)
            if user:
                user.speak_l(self._blocked_action_reason(player), buffer="game")
            return
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return

        # Out-of-turn plays: interceptions and straights.
        if self.current_player != player:
            self._handle_out_of_turn_play(player, card)
            return

        if not self._is_card_playable(card):
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "uno-cannot-play-that",
                    buffer="game",
                    card=cards.format_card(card, user.locale),
                    reason=self._card_unplayable_reason(card, user.locale),
                )
            return

        self._close_uno_windows_for_started_action()
        self._place_card(player, card)

    # ------------------------------------------------------------------
    # Out-of-turn plays (interceptions / straights, Phase 3)
    # ------------------------------------------------------------------

    def _oot_options_on(self) -> bool:
        return (
            self.options.interceptions
            or self.options.super_interceptions
            or self.options.straights
        )

    def _handle_out_of_turn_play(self, player: UnoPlayer, card: UnoCard) -> None:
        if (
            self._is_wild_locked()
            or self.awaiting_swap_target
            or self.cards_to_draw > 0
            or self.hand_wait_ticks > 0
            or self.intro_wait_ticks > 0
        ):
            return
        kind = self._oot_kind(player, card)
        if kind == "straight":
            self._resolve_straight(player, card)
            return
        if kind in ("interception", "super"):
            self._close_uno_windows_for_started_action()
            self._resolve_interception(player, card)
            return
        # Invalid out-of-turn play.
        user = self.get_user(player)
        if self.options.interceptions or self.options.super_interceptions:
            player.penalty_points += 3
            if user:
                user.speak_l(
                    "uno-bad-intercept",
                    buffer="game",
                    points=3,
                )
        elif user:
            user.speak_l("uno-not-your-turn", buffer="game")

    def _oot_kind(self, player: UnoPlayer, card: UnoCard) -> str | None:
        """Classify an out-of-turn play: 'straight', 'interception', 'super', or None."""
        top = self.top_card
        # Straight: the last player continues a same-color number run.
        if (
            self.options.straights
            and self.last_player_id == player.id
            and card.type == cards.NUMBER
            and top is not None
            and top.type == cards.NUMBER
            and self.straight_color is not None
            and card.color == self.straight_color
            and self.straight_value is not None
        ):
            step = self._straight_step(self.straight_value, card.value)
            if step is not None and self.straight_dir in (0, step):
                return "straight"
        # Interception: exact match of the current top.
        if card.type in cards.WILD_TYPES or top is None or top.type in cards.WILD_TYPES:
            return None
        if self.options.interceptions and card.color == top.color and card.type == top.type:
            if card.type != cards.NUMBER or card.value == top.value:
                return "interception"
        if self.options.super_interceptions and card.type == top.type:
            if card.type != cards.NUMBER or card.value == top.value:
                return "super"
        return None

    def _resolve_interception(self, player: UnoPlayer, card: UnoCard) -> None:
        player.hand.remove(card)
        self.discard_pile.append(card)
        self.last_player_id = player.id
        self.bluff_challenge_available = False
        self.consecutive_passes = 0
        self.play_sound(f"game_uno/intercept{random.randint(1, 4)}.ogg")
        self.current_color = card.color
        self._broadcast_intercept(player, card)
        # Announce UNO only after the play, so the card is heard first.
        self._maybe_open_uno_window(player)
        self._set_straight_anchor(card)
        self._jolt_reaction_bots()
        if len(player.hand) == 0:
            self._end_round(player)
            return
        self.current_player = player
        if card.type == cards.NUMBER:
            # Number interception: the interceptor takes the floor and plays again.
            # A seven first opens the swap (and freezes), then replays after it.
            if self._is_seven_swap(card):
                self._begin_seven_swap(player, replay=True)
                return
            self._apply_card_effects(card)  # 0-rotate when the rule is on
            self.current_player = player
            self._start_turn()
        else:
            # Action interception (skip / reverse / draw-two): resolves exactly as
            # if the interceptor had played it on their own turn — skip moves two
            # seats on, reverse flips then moves one, draw-two punishes the left —
            # and then play advances normally.
            self._apply_card_effects(card)
            self._advance_turn()

    def _resolve_straight(self, player: UnoPlayer, card: UnoCard) -> None:
        player.hand.remove(card)
        self.discard_pile.append(card)
        self.last_player_id = player.id
        self.consecutive_passes = 0
        self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")
        if self.straight_dir == 0 and self.straight_value is not None:
            self.straight_dir = self._straight_step(self.straight_value, card.value) or 1
        self.straight_color = card.color
        self.straight_value = card.value
        self.current_color = card.color
        self._broadcast_play(player, card)
        # Announce UNO only after the play, so the card is heard first.
        self._maybe_open_uno_window(player)
        self._jolt_reaction_bots()
        if len(player.hand) == 0:
            self._end_round(player)
            return
        # The seven-swap / zero-rotate effects apply even when the number is
        # played as a straight continuation.
        if self._is_seven_swap(card):
            self._begin_seven_swap(player)
            return
        if card.value == 0 and self.options.zero_seven_rule:
            self._rotate_hands()
        # A straight is an extra play; the turn pointer does not move.
        self.refresh_menus()

    @staticmethod
    def _straight_step(from_value: int, to_value: int) -> int | None:
        """Direction of a one-step straight move from ``from_value`` to
        ``to_value``, with wrap-around across the 0..9 number range: 9->0 counts
        as a +1 (ascending) step and 0->9 as a -1 (descending) step. Returns +1,
        -1, or None when the two values are not adjacent."""
        if (to_value - from_value) % 10 == 1:
            return 1
        if (from_value - to_value) % 10 == 1:
            return -1
        return None

    def _set_straight_anchor(self, card: UnoCard) -> None:
        if not self.options.straights:
            self._clear_straight()
            return
        if card.type == cards.NUMBER:
            self.straight_color = card.color
            self.straight_value = card.value
            self.straight_dir = 0
        else:
            self._clear_straight()

    def _jolt_reaction_bots(self) -> None:
        """Give every bot a human-like reaction delay after a card is played, so
        interception / straight reactions are staggered instead of instant."""
        if not self._oot_options_on():
            return
        for p in self.alive_players:
            if p.is_bot:
                BotHelper.jolt_bot(p, ticks=random.randint(10, 25))

    def _place_card(self, player: UnoPlayer, card: UnoCard) -> None:
        """Remove a card from a player's hand and resolve its effects."""
        player.hand.remove(card)
        self.discard_pile.append(card)
        self.last_player_id = player.id
        self.bluff_challenge_available = False
        player.turn_has_drawn = False
        self.consecutive_passes = 0

        self._play_card_sound(card)
        self._jolt_reaction_bots()

        is_wild = card.type in cards.WILD_TYPES

        if is_wild and len(player.hand) > 0:
            # Record bluff potential before the color changes: a Wild Draw Four is
            # a bluff if the player still holds a card of the current color.
            self.is_bluff = (
                card.type == cards.WILD_DRAW_FOUR
                and self.options.bluff
                and any(c.color == self.current_color for c in player.hand)
            )
            self._broadcast_play(player, card)
            # Announce UNO only after the play, so the card is heard first.
            self._maybe_open_uno_window(player)
            self.awaiting_wild_color = True
            self.wild_color_player_id = player.id
            self.pending_wild_type = card.type
            self._clear_straight()
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(15, 25))
            self.request_menu_focus(player, "color_red")
            return

        if not is_wild:
            self.current_color = card.color
        self._broadcast_play(player, card)
        # Announce UNO only after the play, so the card is heard first.
        self._maybe_open_uno_window(player)

        if len(player.hand) == 0:
            self._resolve_winning_play(player, card)
            return

        # Draw-two passes a draw obligation to the next player.
        if card.type == cards.DRAW_TWO:
            self._extend_obligation(cards.DRAW_TWO)
            self._advance_turn()
            return

        # Advanced response: a skip/reverse played against a pending draw
        # obligation is defensive — it passes the obligation to the next player
        # rather than absorbing it. Crucially it must NOT apply its normal
        # skip/bounce effect, which in a two-player game would send the turn
        # straight back to the responder and trap them with the very draw they
        # are deflecting. Reverse still flips direction with three or more.
        if self.cards_to_draw > 0:
            if card.type == cards.REVERSE and len(self.turn_player_ids) > 2:
                self.reverse_turn_direction()
                self.broadcast_l("uno-direction-reversed", buffer="game")
            self._clear_straight()
            self._advance_turn()
            return

        # Seven-swap: freeze the game until a swap target is chosen.
        if self._is_seven_swap(card):
            self._begin_seven_swap(player)
            return

        self._set_straight_anchor(card)
        self._apply_card_effects(card)
        self._advance_turn()

    def _begin_seven_swap(self, player: UnoPlayer, replay: bool = False) -> None:
        """Open the swap menu for the player who played a seven and freeze play
        for everyone else until they choose (or decline). With ``replay`` the
        player keeps the floor and plays again after the swap (interception);
        otherwise the post-swap turn flow is decided in ``_action_choose_swap``."""
        self.awaiting_swap_target = True
        self.swap_player_id = player.id
        self.swap_replay = replay
        user = self.get_user(player)
        if user and not player.is_bot:
            user.speak_l("uno-choose-swap", buffer="game")
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(15, 25))
        self.refresh_menus()

    def _resolve_winning_play(self, player: UnoPlayer, card: UnoCard) -> None:
        """Handle a play that empties the hand (round end)."""
        is_draw_card = card.type in (cards.DRAW_TWO, cards.WILD_DRAW_FOUR)
        if (
            is_draw_card
            and self.options.wait_for_draw_responses
            and self._stacking_on()
        ):
            # Let the next player stack or counter before the round is awarded.
            self._extend_obligation(card.type)
            if card.type == cards.WILD_DRAW_FOUR and self.options.bluff:
                self.bluff_challenge_available = True
            self.pending_round_winner_id = player.id
            self._advance_turn()
            return
        # Terminal draw effects still apply when a draw card is the last card.
        # Any obligation the winner inherited and is now passing along (e.g. a
        # pending Draw Two they responded to with this card) must carry over, so
        # the victim draws the full accumulated stack plus this card's own value.
        if card.type == cards.DRAW_TWO:
            nxt = self._next_player()
            if nxt:
                self._draw_for_player(nxt, self.cards_to_draw + 2)
        elif card.type == cards.WILD_DRAW_FOUR:
            nxt = self._next_player()
            if nxt:
                self._draw_for_player(nxt, self.cards_to_draw + 4)
        self.cards_to_draw = 0
        self.draw_type = ""
        self._end_round(player)

    def _apply_card_effects(self, card: UnoCard) -> None:
        """Card effects for the immediate (non-obligation) path."""
        two_player = len(self.turn_player_ids) == 2
        if card.type == cards.SKIP:
            self.skip_next_players(1)
        elif card.type == cards.REVERSE:
            if two_player:
                self.skip_next_players(1)
            else:
                self.reverse_turn_direction()
                self.broadcast_l("uno-direction-reversed", buffer="game")
        elif card.type == cards.DRAW_TWO:
            # Reached only via an interception (in-turn draw-twos use the
            # obligation path). The drawee loses the turn only with skip-after-draw.
            nxt = self._next_player()
            if nxt:
                self._draw_for_player(nxt, 2)
            if self.options.skip_after_draw:
                self.skip_next_players(1)
        elif card.type == cards.NUMBER and card.value == 0 and self.options.zero_seven_rule:
            self._rotate_hands()
        # Seven-swap is handled before this (it needs a target choice).

    # ------------------------------------------------------------------
    # Draw-obligation helpers (Phase 2)
    # ------------------------------------------------------------------

    def _stacking_on(self) -> bool:
        return self.options.responses or self.options.advanced_responses

    def _creates_obligation(self, card_type: str) -> bool:
        """Draw cards always pass a draw obligation to the next player, who
        resolves it on their turn (respond if stacking, challenge if bluffs are
        on, otherwise draw — and only lose the turn if skip-after-draw is on)."""
        return card_type in (cards.DRAW_TWO, cards.WILD_DRAW_FOUR)

    def _extend_obligation(self, card_type: str) -> None:
        self.cards_to_draw += 2 if card_type == cards.DRAW_TWO else 4
        self.draw_type = card_type

    def _is_response_playable(self, card: UnoCard) -> bool:
        """Whether a card may be played to respond to a pending draw obligation."""
        if not self._stacking_on():
            return False
        top = self.top_card
        if card.type == cards.WILD_DRAW_FOUR:
            return True
        if card.type == cards.DRAW_TWO:
            return card.color == self.current_color or (top is not None and top.type == cards.DRAW_TWO)
        if self.options.advanced_responses:
            if card.type in (cards.SKIP, cards.REVERSE):
                return card.color == self.current_color or (top is not None and card.type == top.type)
            if card.type == cards.WILD_CARD:
                return True
        return False

    def _accept_draw_obligation(self, player: UnoPlayer) -> None:
        """Player takes the accumulated draw penalty.

        The legacy field name is ``skip_after_draw``; the option now represents
        the official draw-penalty rule. With it on, Draw Two / Wild Draw Four
        penalties skip the target. Ordinary one-card draws are handled by
        _action_draw and still allow a playable drawn card to be played.
        """
        self.bluff_challenge_available = False
        count = self.cards_to_draw
        self._draw_for_player(player, count)
        self.cards_to_draw = 0
        self.draw_type = ""
        player.turn_has_drawn = True
        if self.pending_round_winner_id:
            self._finish_pending_round()
            return
        if self.options.skip_after_draw:
            self._advance_turn()
            return
        # Keep the turn: play a card if able, otherwise the turn ends normally.
        if self._has_playable(player):
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(10, 20))
            self.refresh_menus()
        else:
            self._auto_skip(player)

    def _finish_pending_round(self) -> None:
        winner = self.get_player_by_id(self.pending_round_winner_id)
        self.pending_round_winner_id = ""
        if isinstance(winner, UnoPlayer):
            self._end_round(winner)

    def _is_seven_swap(self, card: UnoCard) -> bool:
        return (
            card.type == cards.NUMBER
            and card.value == 7
            and self.options.zero_seven_rule
            and len(self.alive_players) > 1
        )

    def _rotate_hands(self) -> None:
        alive = self.alive_players
        if len(alive) < 2:
            return
        hands = [p.hand for p in alive]
        n = len(alive)
        for i, p in enumerate(alive):
            p.hand = hands[(i + self.turn_direction) % n]
        self.play_sound("game_uno/handchange.ogg")
        self.broadcast_l("uno-rotate-hands", buffer="game")
        self.refresh_menus()

    def _action_choose_swap(self, player: Player, action_id: str) -> None:
        if not isinstance(player, UnoPlayer):
            return
        if not self.awaiting_swap_target or self.swap_player_id != player.id:
            return
        # Post-swap turn flow:
        #   - replay: an intercepted seven keeps the floor and plays again
        #   - in-turn seven: the turn advances
        #   - out-of-turn straight seven: the turn pointer does not move
        replay = self.swap_replay
        self.swap_replay = False
        was_current = self.current_player is not None and self.current_player.id == player.id
        target_id = action_id[len("swap_target_"):]
        if target_id == "none":
            # Declining to swap is a valid choice for a seven.
            self.awaiting_swap_target = False
            self.swap_player_id = ""
            self._broadcast_actor(player, "uno-you-swap-none", "uno-swap-none-other")
        else:
            target = self.get_player_by_id(target_id)
            if not isinstance(target, UnoPlayer) or target.id == player.id:
                return
            player.hand, target.hand = target.hand, player.hand
            self.awaiting_swap_target = False
            self.swap_player_id = ""
            self.play_sound("game_uno/handchange.ogg")
            for q in self.players:
                user = self.get_user(q)
                if not user:
                    continue
                if q.id == player.id:
                    user.speak_l("uno-you-swap", buffer="game", target=target.name)
                elif q.id == target.id:
                    user.speak_l("uno-swap-with-you", buffer="game", player=player.name)
                else:
                    user.speak_l(
                        "uno-swap-hands", buffer="game", player=player.name, target=target.name
                    )
        if replay:
            self.current_player = player
            self._start_turn()
        elif was_current:
            self._advance_turn()
        else:
            self.refresh_menus()

    def _action_bluff_challenge(self, player: Player, action_id: str) -> None:
        p = self._require_current(player)
        if not p or not self.bluff_challenge_available:
            return
        self._close_uno_windows_for_started_action()
        self.bluff_challenge_available = False
        bluffer = self.get_player_by_id(self.last_player_id)
        draw_penalty = self.cards_to_draw
        # The bluff message states the draw, so suppress the separate draw line.
        challenge_succeeded = self.is_bluff and isinstance(bluffer, UnoPlayer)
        if challenge_succeeded:
            self._draw_for_player(bluffer, draw_penalty, announce=False)
            self._broadcast_actor(
                bluffer, "uno-you-bluff-caught", "uno-bluff-caught", count=draw_penalty
            )
        else:
            challenger_penalty = draw_penalty + 2
            self._draw_for_player(p, challenger_penalty, announce=False)
            self._broadcast_actor(
                p, "uno-you-bluff-wrong", "uno-bluff-wrong", count=challenger_penalty
            )
        self.cards_to_draw = 0
        self.draw_type = ""
        self.is_bluff = False
        if self.pending_round_winner_id:
            if challenge_succeeded:
                self.pending_round_winner_id = ""
                if self._has_playable(p) or self._can_draw(p):
                    if p.is_bot:
                        BotHelper.jolt_bot(p, ticks=random.randint(10, 20))
                    self.refresh_menus()
                else:
                    self._auto_skip(p)
                return
            self._finish_pending_round()
            return
        if challenge_succeeded:
            if self._has_playable(p) or self._can_draw(p):
                if p.is_bot:
                    BotHelper.jolt_bot(p, ticks=random.randint(10, 20))
                self.refresh_menus()
            else:
                self._auto_skip(p)
            return
        self._advance_turn()

    def _action_choose_color(self, player: Player, action_id: str) -> None:
        if not isinstance(player, UnoPlayer):
            return
        if not self.awaiting_wild_color or self.wild_color_player_id != player.id:
            return
        color = cards.color_from_action(action_id)
        if color is None:
            return
        self.current_color = color
        self.awaiting_wild_color = False
        self.play_sound("game_uno/wild.ogg")
        snd = cards.color_sound(color)
        if snd:
            self.schedule_sound(snd, delay_ticks=10)
        self._broadcast_color_chosen(player, color)

        if self.opening_wild_color:
            self.opening_wild_color = False
            self.pending_wild_type = ""
            self.wild_color_player_id = ""
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(15, 25))
            self._start_turn()
            self._focus_after_color_choice(player, color)
            return

        if self.pending_wild_type == cards.WILD_DRAW_FOUR:
            # Pass the draw obligation; the next player resolves it on their turn
            # (challenge if bluffs are on, otherwise draw).
            self._extend_obligation(cards.WILD_DRAW_FOUR)
            if self.options.bluff:
                self.bluff_challenge_available = True

        self.pending_wild_type = ""
        self.wild_color_player_id = ""
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(15, 25))
        self.wild_wait_ticks = WILD_TRANSITION_TICKS
        self._focus_after_color_choice(player, color)

    def _action_draw(self, player: Player, action_id: str) -> None:
        p = self._require_current(player)
        if not p or self._is_wild_locked() or self.awaiting_swap_target:
            return
        # Accepting a pending draw obligation.
        if self.cards_to_draw > 0:
            self._close_uno_windows_for_started_action()
            self._accept_draw_obligation(p)
            return
        if not self._can_draw(p):
            return
        had_playable = self._has_playable(p)
        card = self._draw_card()
        if not card:
            return
        self._close_uno_windows_for_started_action()
        p.hand.append(card)
        p.turn_has_drawn = True
        if had_playable and self.options.free_draws > 0:
            p.free_draws_used += 1
        playable = self._is_card_playable(card)
        user = self.get_user(p)
        if playable and user:
            user.play_sound("game_uno/playable.ogg")
            for other in self.players:
                if other.id != p.id:
                    ou = self.get_user(other)
                    if ou:
                        ou.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")
        else:
            self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")
        self._broadcast_draw(p, 1)

        # Jump focus to the card just drawn, whether or not it can be played, so
        # the player always lands on what they drew.
        self.request_menu_focus(p, f"play_card_{card.id}")

        # A free draw (drawn while already holding playable cards) keeps the turn.
        if playable or had_playable:
            self.consecutive_passes = 0
            if p.is_bot:
                BotHelper.jolt_bot(p, ticks=random.randint(15, 25))
            return
        # Drew an unplayable card with nothing else to play: skip the turn.
        self._auto_skip(p)

    def _handle_blocked_hand(self) -> None:
        """No card can be played and the deck is exhausted: lowest hand wins."""
        alive = self.alive_players
        if not alive:
            return
        winner = min(alive, key=lambda p: cards.hand_points(p.hand))
        self.broadcast_l("uno-hand-blocked", buffer="game")
        self._end_round(winner)

    def _action_uno(self, player: Player, action_id: str) -> None:
        if not isinstance(player, UnoPlayer) or player.is_spectator:
            return
        if player not in self.alive_players:
            return
        # Announce UNO for self.
        if len(player.hand) == 1 and not player.said_uno:
            player.said_uno = True
            player.uno_grace_ticks = 0
            player.uno_window_ticks = 0
            self.play_sound("game_uno/uno.ogg")
            self._broadcast_uno(player)
            self.refresh_menus()
            return
        # Call out someone who is in their open window.
        target = self._callable_target(player)
        if target:
            # The call-out message states the draw, so draw silently.
            self._draw_for_player(target, UNO_CALLOUT_PENALTY, announce=False)
            self.play_sound("game_uno/buzzerpress.ogg")
            for q in self.players:
                user = self.get_user(q)
                if not user:
                    continue
                if q.id == player.id:
                    user.speak_l(
                        "uno-you-callout",
                        buffer="game",
                        player=target.name,
                        count=UNO_CALLOUT_PENALTY,
                    )
                elif q.id == target.id:
                    user.speak_l(
                        "uno-callout-you",
                        buffer="game",
                        caller=player.name,
                        count=UNO_CALLOUT_PENALTY,
                    )
                else:
                    user.speak_l(
                        "uno-callout",
                        buffer="game",
                        caller=player.name,
                        player=target.name,
                        count=UNO_CALLOUT_PENALTY,
                    )
            target.uno_grace_ticks = 0
            target.uno_window_ticks = 0
            self.refresh_menus()
            return

        user = self.get_user(player)
        if user:
            if len(player.hand) == 1 and player.said_uno:
                user.speak_l("uno-error-already-said-uno", buffer="game")
            else:
                user.speak_l("uno-error-no-uno-call", buffer="game")

    # ==========================================================================
    # Info actions
    # ==========================================================================

    def _action_read_top(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        top = self.top_card
        if not top:
            user.speak_l("uno-no-top", buffer="game")
            return
        user.speak_l("uno-top-card", buffer="game", card=cards.format_card(top, user.locale))

    def _action_read_color(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if self.current_color is None:
            user.speak_l("uno-no-top", buffer="game")
            return
        user.speak_l(
            "uno-color-is", buffer="game",
            color=cards.color_name(self.current_color, user.locale),
        )

    def _action_read_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        parts = [
            Localization.get(user.locale, "uno-count-you", count=len(p.hand))
            if p.id == player.id
            else Localization.get(
                user.locale, "uno-count-player", player=p.name, count=len(p.hand)
            )
            for p in self.alive_players
        ]
        parts.append(Localization.get(user.locale, "uno-deck-count", count=len(self.deck)))
        user.speak(", ".join(parts), buffer="game")

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user or not isinstance(player, UnoPlayer):
            return
        user.speak_l(
            "uno-read-hand-value", buffer="game",
            count=len(player.hand), points=cards.hand_points(player.hand),
        )

    def _action_sort_color(self, player: Player, action_id: str) -> None:
        if not isinstance(player, UnoPlayer):
            return
        player.card_sort_mode = "color"
        user = self.get_user(player)
        if user:
            user.speak_l("uno-sorting-color", buffer="game")
        self.refresh_menus(player)

    def _action_sort_number(self, player: Player, action_id: str) -> None:
        if not isinstance(player, UnoPlayer):
            return
        player.card_sort_mode = "number"
        user = self.get_user(player)
        if user:
            user.speak_l("uno-sorting-number", buffer="game")
        self.refresh_menus(player)

    # ==========================================================================
    # Enable / hide callbacks
    # ==========================================================================

    def _require_current(self, player: Player) -> UnoPlayer | None:
        if not isinstance(player, UnoPlayer) or player.is_spectator:
            return None
        if self.current_player != player:
            return None
        return player

    def _blocked_action_reason(self, player: Player) -> str:
        if self.awaiting_wild_color:
            if isinstance(player, UnoPlayer) and player.id == self.wild_color_player_id:
                return "uno-error-choose-color-first"
            return "uno-error-wait-color-choice"
        if self.wild_wait_ticks > 0:
            return "uno-error-wild-transition"
        if self.awaiting_swap_target:
            if isinstance(player, UnoPlayer) and player.id == self.swap_player_id:
                return "uno-error-choose-swap-first"
            return "uno-error-wait-swap-choice"
        if self.hand_wait_ticks > 0:
            return "uno-error-wait-next-hand"
        if self.intro_wait_ticks > 0:
            return "uno-error-wait-intro"
        return "action-not-available"

    def _is_play_card_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_play_card_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        # While a seven-swap target is being chosen, no card may be played; the
        # swap chooser sees only the swap options.
        if self.awaiting_swap_target:
            return Visibility.HIDDEN
        if not isinstance(player, UnoPlayer) or not action_id:
            return Visibility.HIDDEN
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return Visibility.HIDDEN
        if not any(c.id == card_id for c in player.hand):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_draw_enabled(self, player: Player) -> str | None:
        if self._is_wild_locked() or self.awaiting_swap_target:
            return "action-not-available"
        if self.current_player != player:
            return "action-not-your-turn"
        if not isinstance(player, UnoPlayer):
            return "action-not-available"
        # Accepting a draw obligation is always available.
        if self.cards_to_draw > 0:
            return None
        if not self._can_draw(player):
            return "action-not-available"
        return None

    def _is_draw_hidden(self, player: Player) -> Visibility:
        if self._is_draw_enabled(player) is None:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_color_choice_enabled(self, player: Player) -> str | None:
        if not self.awaiting_wild_color or self.wild_color_player_id != player.id:
            return "action-not-available"
        return None

    def _is_color_choice_hidden(self, player: Player) -> Visibility:
        if not self.awaiting_wild_color or self.wild_color_player_id != player.id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_bluff_enabled(self, player: Player) -> str | None:
        # The player who played the Wild Draw Four cannot challenge their own card.
        if (
            not self.bluff_challenge_available
            or self.current_player != player
            or player.id == self.last_player_id
        ):
            return "action-not-available"
        return None

    def _is_bluff_hidden(self, player: Player) -> Visibility:
        if (
            self.bluff_challenge_available
            and self.current_player == player
            and player.id != self.last_player_id
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_swap_choice_enabled(self, player: Player) -> str | None:
        if not self.awaiting_swap_target or self.swap_player_id != player.id:
            return "action-not-available"
        return None

    def _is_swap_choice_hidden(self, player: Player) -> Visibility:
        if not self.awaiting_swap_target or self.swap_player_id != player.id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_uno_enabled(self, player: Player) -> str | None:
        if not isinstance(player, UnoPlayer) or player.is_spectator:
            return "action-not-available"
        if player not in self.alive_players:
            return "action-not-available"
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return None
        if len(player.hand) == 1 and not player.said_uno:
            return None
        if self._callable_target(player):
            return None
        if len(player.hand) == 1 and player.said_uno:
            return "uno-error-already-said-uno"
        return "uno-error-no-uno-call"

    def _is_uno_hidden(self, player: Player) -> Visibility:
        if not isinstance(player, UnoPlayer) or player.is_spectator:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_info_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def get_score_sort_descending(self) -> bool:
        """High totals lead in winner-score mode; low totals lead in elimination."""
        return self.options.scoring_mode != SCORING_ELIMINATION

    def _uno_score_players(self) -> list[UnoPlayer]:
        players = [
            p for p in self.get_active_players()
            if isinstance(p, UnoPlayer)
        ]
        return sorted(
            players,
            key=lambda p: p.score,
            reverse=self.get_score_sort_descending(),
        )

    def _format_uno_score_line(self, player: UnoPlayer, locale: str) -> str:
        if self.options.scoring_mode == SCORING_ELIMINATION:
            key = "uno-score-line-elimination"
        else:
            key = "uno-score-line-first"
        return Localization.get(
            locale,
            key,
            player=player.name,
            score=player.score,
            target=self.options.winning_score,
        )

    def _uno_score_lines(self, locale: str) -> list[str]:
        return [
            self._format_uno_score_line(p, locale)
            for p in self._uno_score_players()
        ]

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = self._uno_score_lines(user.locale)
        if not lines:
            user.speak_l("no-scores-available", buffer="game")
            return
        for line in lines:
            user.speak(line, buffer="game")

    def _detailed_score_lines(self, locale: str) -> list[str]:
        return self._uno_score_lines(locale)

    # ==========================================================================
    # UNO call-out window
    # ==========================================================================

    def _maybe_open_uno_window(self, player: UnoPlayer) -> None:
        """Open the UNO window if the player just dropped to a single card."""
        if len(player.hand) == 1 and not player.said_uno:
            self._open_uno_window(player)

    def _open_uno_window(self, player: UnoPlayer) -> None:
        player.uno_grace_ticks = 0
        player.uno_window_ticks = 1
        # Bots usually remember to announce immediately.
        if player.is_bot and random.random() < 0.9:
            player.said_uno = True
            player.uno_grace_ticks = 0
            player.uno_window_ticks = 0
            self.play_sound("game_uno/uno.ogg")
            self._broadcast_uno(player)

    def _tick_uno_window(self) -> None:
        for p in self.alive_players:
            if len(p.hand) != 1:
                # Drawing back above one card clears a stale UNO declaration, so a
                # player who later returns to one card must announce again (and can).
                p.said_uno = False
                p.uno_grace_ticks = 0
                p.uno_window_ticks = 0
                continue
            if p.said_uno:
                p.uno_grace_ticks = 0
                p.uno_window_ticks = 0
                continue
            p.uno_grace_ticks = 0

    def _close_uno_windows_for_started_action(self) -> None:
        """Close outstanding UNO call-out windows once the next play/draw starts."""
        for p in self.alive_players:
            p.uno_grace_ticks = 0
            p.uno_window_ticks = 0

    def _callable_target(self, caller: Player) -> UnoPlayer | None:
        for p in self.alive_players:
            if p.id == caller.id:
                continue
            if len(p.hand) == 1 and not p.said_uno and p.uno_window_ticks > 0:
                return p
        return None

    # ==========================================================================
    # Out-of-turn bots (Age of Heroes pattern)
    # ==========================================================================

    def _tick_out_of_turn_bots(self) -> None:
        if self.awaiting_wild_color or self.wild_wait_ticks > 0:
            return
        if self.awaiting_swap_target:
            # A seven-swap freezes normal out-of-turn play. Only the swap chooser
            # acts, and only when they are not the current player (an in-turn
            # seven is driven by the normal bot tick instead).
            swapper = self.get_player_by_id(self.swap_player_id)
            if (
                isinstance(swapper, UnoPlayer)
                and swapper.is_bot
                and swapper is not self.current_player
            ):
                BotHelper.process_bot_action(
                    bot=swapper,
                    think_fn=lambda: bot_think_out_of_turn(self, swapper),
                    execute_fn=lambda action_id: self.execute_action(swapper, action_id),
                )
            return
        for p in list(self.alive_players):
            if not p.is_bot or p is self.current_player:
                continue
            BotHelper.process_bot_action(
                bot=p,
                think_fn=lambda p=p: bot_think_out_of_turn(self, p),
                execute_fn=lambda action_id, p=p: self.execute_action(p, action_id),
            )

    def bot_think(self, player: UnoPlayer) -> str | None:
        return bot_think_turn(self, player)

    # ==========================================================================
    # Card helpers
    # ==========================================================================

    @property
    def top_card(self) -> UnoCard | None:
        return self.discard_pile[-1] if self.discard_pile else None

    @property
    def alive_players(self) -> list[UnoPlayer]:
        result = []
        for pid in self.turn_player_ids:
            p = self.get_player_by_id(pid)
            if isinstance(p, UnoPlayer):
                result.append(p)
        return result

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _sorted_hand(self, player: UnoPlayer) -> list[UnoCard]:
        if player.card_sort_mode == "number":
            return sorted(player.hand, key=cards.sort_key_by_number)
        if player.card_sort_mode == "none":
            return list(player.hand)
        return sorted(player.hand, key=cards.sort_key_by_color)

    def _focus_after_color_choice(self, player: UnoPlayer, color: int) -> None:
        for card in self._sorted_hand(player):
            if card.color == color:
                self.request_menu_focus(player, f"play_card_{card.id}")
                return

        self._sync_turn_actions(player)
        visible_actions = self.get_all_visible_actions(player)
        if visible_actions:
            self.request_menu_focus(player, visible_actions[0].action.id)
        else:
            self.refresh_menus(player)

    def _is_card_playable(self, card: UnoCard) -> bool:
        if self._is_wild_locked() or self.awaiting_swap_target:
            return False
        # While a draw obligation is pending, only valid response cards play.
        if self.cards_to_draw > 0:
            return self._is_response_playable(card)
        if card.type in cards.WILD_TYPES:
            return True
        top = self.top_card
        if not top:
            return True
        if card.color == self.current_color:
            return True
        if card.type == cards.NUMBER and top.type == cards.NUMBER and card.value == top.value:
            return True
        if card.type != cards.NUMBER and card.type == top.type:
            return True
        return False

    def _card_unplayable_reason(self, card: UnoCard, locale: str) -> str:
        if self.cards_to_draw > 0:
            if self._stacking_on():
                return Localization.get(
                    locale,
                    "uno-reason-draw-stack-response",
                    count=self.cards_to_draw,
                )
            return Localization.get(
                locale,
                "uno-reason-draw-stack-no-response",
                count=self.cards_to_draw,
            )
        top = self.top_card
        if top:
            return Localization.get(
                locale,
                "uno-reason-match-required",
                top=cards.format_card(top, locale),
                color=cards.color_name(self.current_color or top.color, locale),
            )
        return Localization.get(locale, "uno-reason-card-not-available")

    def _has_playable(self, player: UnoPlayer) -> bool:
        return any(self._is_card_playable(c) for c in player.hand)

    def get_playable_indices(self, player: UnoPlayer) -> list[int]:
        return [i for i, c in enumerate(player.hand) if self._is_card_playable(c)]

    def _is_wild_locked(self) -> bool:
        return self.awaiting_wild_color or self.wild_wait_ticks > 0

    def _can_draw(self, player: UnoPlayer) -> bool:
        if self._is_wild_locked() or player.turn_has_drawn:
            return False
        if not self._has_playable(player):
            return self._deck_has_cards()
        # Free draws: may draw despite a playable card (humans only).
        if self.options.free_draws > 0 and not player.is_bot:
            if player.free_draws_used < self.options.free_draws:
                return self._deck_has_cards()
        return False

    def _deck_has_cards(self) -> bool:
        return bool(self.deck) or len(self.discard_pile) > 1

    def _draw_card(self) -> UnoCard | None:
        if not self.deck:
            self._reshuffle_discard()
        if not self.deck:
            return None
        return self.deck.pop()

    def _reshuffle_discard(self) -> None:
        if len(self.discard_pile) <= 1:
            return
        top = self.discard_pile[-1]
        rest = self.discard_pile[:-1]
        self.discard_pile = [top]
        self.deck.extend(rest)
        cards.shuffle(self.deck)
        self.play_sound("game_cards/small_shuffle.ogg")
        self.broadcast_l("uno-reshuffle", buffer="game")

    def _draw_for_player(self, player: UnoPlayer, count: int, announce: bool = True) -> None:
        drew = 0
        for _ in range(count):
            card = self._draw_card()
            if not card:
                break
            player.hand.append(card)
            drew += 1
        if drew > 0:
            self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")
            if announce:
                self._broadcast_draw(player, drew)

    def _next_player(self) -> UnoPlayer | None:
        if not self.turn_player_ids:
            return None
        idx = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
        p = self.get_player_by_id(self.turn_player_ids[idx])
        return p if isinstance(p, UnoPlayer) else None

    def _clear_straight(self) -> None:
        self.straight_color = None
        self.straight_value = None
        self.straight_dir = 0

    # ==========================================================================
    # Broadcasts
    # ==========================================================================

    def _broadcast_start_card(self, card: UnoCard) -> None:
        dealer = (
            self.get_player_by_id(self.turn_player_ids[self.dealer_index])
            if self.turn_player_ids and self.dealer_index >= 0
            else None
        )
        dealer_name = dealer.name if dealer else "?"
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            card_name = cards.format_card(card, user.locale)
            if dealer and p.id == dealer.id:
                user.speak_l("uno-you-start-card", buffer="game", card=card_name)
            else:
                user.speak_l(
                    "uno-start-card", buffer="game", player=dealer_name,
                    card=card_name,
                )
            if card.color != cards.WILD:
                user.speak_l(
                    "uno-current-color", buffer="game",
                    color=cards.color_name(card.color, user.locale),
                )

    def _broadcast_actor(self, actor: UnoPlayer, you_key: str, other_key: str, **kwargs) -> None:
        """Speak a you-key to the actor and an other-key (with $player) to the rest."""
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            if p.id == actor.id:
                user.speak_l(you_key, buffer="game", **kwargs)
            else:
                user.speak_l(other_key, buffer="game", player=actor.name, **kwargs)

    def _broadcast_card(self, player: UnoPlayer, card: UnoCard, you_key: str, other_key: str) -> None:
        """Announce a card play/intercept, with second-person to the actor."""
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            card_str = cards.format_card(card, user.locale)
            if p.id == player.id:
                user.speak_l(you_key, buffer="game", card=card_str)
            else:
                user.speak_l(other_key, buffer="game", player=player.name, card=card_str)

    def _broadcast_play(self, player: UnoPlayer, card: UnoCard) -> None:
        self._broadcast_card(player, card, "uno-you-play", "uno-player-plays")

    def _broadcast_intercept(self, player: UnoPlayer, card: UnoCard) -> None:
        self._broadcast_card(player, card, "uno-you-intercept", "uno-player-intercepts")

    def _broadcast_color_chosen(self, player: UnoPlayer, color: int) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            color_name = cards.color_name(color, user.locale)
            if p.id == player.id:
                user.speak_l("uno-you-choose-color", buffer="game", color=color_name)
            else:
                user.speak_l(
                    "uno-player-chooses-color", buffer="game",
                    player=player.name, color=color_name,
                )

    def _broadcast_draw(self, player: UnoPlayer, count: int) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            if p.id == player.id:
                key = "uno-you-draw-one" if count == 1 else "uno-you-draw-many"
                user.speak_l(key, buffer="game", count=count)
            else:
                key = "uno-player-draws-one" if count == 1 else "uno-player-draws-many"
                user.speak_l(key, buffer="game", player=player.name, count=count)

    def _broadcast_uno(self, player: UnoPlayer) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            if p.id == player.id:
                user.speak_l("uno-you-say-uno", buffer="game")
            else:
                user.speak_l("uno-says-uno", buffer="game", player=player.name)

    def _play_card_sound(self, card: UnoCard) -> None:
        if card.type == cards.SKIP:
            self.play_sound("game_uno/skip.ogg")
        elif card.type == cards.REVERSE:
            self.play_sound("game_uno/reverse.ogg", volume=50)
        elif card.type == cards.WILD_DRAW_FOUR:
            self.play_sound("game_uno/wild4.ogg")
        else:
            self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")

    def _get_card_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, UnoPlayer):
            return action_id
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return action_id
        return cards.format_card(card, self._player_locale(player))

    # ==========================================================================
    # Scoring / round + game end
    # ==========================================================================

    def _end_round(self, winner: UnoPlayer) -> None:
        self.play_sound("game_uno/winround.ogg")
        self._broadcast_actor(winner, "uno-you-win-round", "uno-round-winner")

        losers: list[tuple[UnoPlayer, int]] = []
        for p in self.alive_players:
            if p.id == winner.id:
                continue
            losers.append((p, cards.hand_points(p.hand) + p.penalty_points))

        if self.options.scoring_mode == SCORING_ELIMINATION:
            self._score_elimination(winner, losers)
        else:
            self._score_first_to_limit(winner, losers)

        if self.status == "finished":
            return
        self._sync_team_scores()
        self.hand_wait_ticks = HAND_END_TICKS
        self.refresh_menus()

    def _score_first_to_limit(self, winner: UnoPlayer, losers: list[tuple[UnoPlayer, int]]) -> None:
        total = sum(pts for _, pts in losers)
        real_winner = self.get_player_by_id(winner.id)
        if isinstance(real_winner, UnoPlayer):
            real_winner.score += total
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            parts = [
                self._format_round_points_from(user.locale, lp, pts, listener=p)
                for lp, pts in losers
            ]
            details = (
                Localization.format_list_and(user.locale, parts)
                if parts else Localization.get(user.locale, "uno-round-details-none")
            )
            if p.id == winner.id:
                user.speak_l("uno-round-summary-you", buffer="game", details=details, total=total)
            else:
                user.speak_l(
                    "uno-round-summary", buffer="game",
                    player=winner.name, details=details, total=total,
                )
        if isinstance(real_winner, UnoPlayer) and real_winner.score >= self.options.winning_score:
            self._end_game(real_winner)

    def _score_elimination(self, winner: UnoPlayer, losers: list[tuple[UnoPlayer, int]]) -> None:
        for lp, pts in losers:
            lp.score += pts
            if lp.penalty_points > 0:
                self._broadcast_actor(
                    lp,
                    "uno-you-add-penalty-points-with-interception",
                    "uno-player-adds-penalty-points-with-interception",
                    points=pts,
                    hand_points=pts - lp.penalty_points,
                    penalty=lp.penalty_points,
                )
            else:
                self._broadcast_actor(
                    lp,
                    "uno-you-add-penalty-points",
                    "uno-player-adds-penalty-points",
                    points=pts,
                )

        eliminated = [p for p in self.alive_players if p.score >= self.options.winning_score]
        if eliminated:
            self.play_sound("game_uno/loseround.ogg")
        for p in eliminated:
            p.hand = []
            self._broadcast_actor(
                p,
                "uno-you-are-eliminated",
                "uno-player-is-eliminated",
                limit=self.options.winning_score,
            )
            self.turn_player_ids = [pid for pid in self.turn_player_ids if pid != p.id]

        survivors = self.alive_players
        if len(survivors) <= 1:
            self._end_game(survivors[0] if survivors else None)

    def _end_game(self, winner: UnoPlayer | None) -> None:
        self.play_sound("game_uno/wingame.ogg")
        if winner:
            self._broadcast_actor(
                winner,
                "uno-you-win-game",
                "uno-player-wins-game",
                score=winner.score,
                mode=self.options.scoring_mode,
            )
        else:
            self.broadcast_l("uno-game-tie", buffer="game")
        self._sync_team_scores()
        self.finish_game()

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.get_active_players():
            team = self._team_manager.get_team(p.name)
            if team and isinstance(p, UnoPlayer):
                team.total_score = p.score

    def _format_round_points_from(
        self,
        locale: str,
        player: UnoPlayer,
        points: int,
        listener: Player | None = None,
    ) -> str:
        self_perspective = listener is not None and listener.id == player.id
        if player.penalty_points <= 0:
            key = (
                "uno-round-points-from-you"
                if self_perspective
                else "uno-round-points-from"
            )
            return Localization.get(
                locale,
                key,
                points=points,
                player=player.name,
            )
        key = (
            "uno-round-points-from-you-with-interception"
            if self_perspective
            else "uno-round-points-from-with-interception"
        )
        return Localization.get(
            locale,
            key,
            points=points,
            hand_points=points - player.penalty_points,
            penalty=player.penalty_points,
            player=player.name,
        )

    def build_game_result(self) -> GameResult:
        active = [p for p in self.players if not p.is_spectator]
        if self.options.scoring_mode == SCORING_ELIMINATION:
            # Survivors win; lowest score otherwise.
            survivors = self.alive_players
            winner = survivors[0] if len(survivors) == 1 else None
            if winner is None and active:
                winner = min(active, key=lambda p: p.score)
        else:
            winner = max(active, key=lambda p: p.score, default=None)
        final_scores = {p.name: p.score for p in active}
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
                for p in active
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "winner_score": winner.score if winner else 0,
                "final_scores": final_scores,
                "scoring_mode": self.options.scoring_mode,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_scores = result.custom_data.get("final_scores", {})
        elim = result.custom_data.get("scoring_mode") == SCORING_ELIMINATION
        ordered = sorted(final_scores.items(), key=lambda kv: kv[1], reverse=not elim)
        for i, (name, score) in enumerate(ordered, 1):
            lines.append(
                Localization.get(locale, "uno-line-format", rank=i, player=name, score=score)
            )
        return lines
