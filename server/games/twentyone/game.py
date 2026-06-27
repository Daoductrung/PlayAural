from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.action_guard_mixin import ActionGuardMixin
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.cards import Card, Deck, card_name
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from .bot import bot_think as compute_bot_think
from ...ui.keybinds import KeybindState


MODIFIER_RAISE_1 = "raise_1"
MODIFIER_RAISE_2 = "raise_2"
MODIFIER_RAISE_2_PLUS = "raise_2_plus"
MODIFIER_DRAW_2 = "draw_2"
MODIFIER_DRAW_3 = "draw_3"
MODIFIER_DRAW_4 = "draw_4"
MODIFIER_DRAW_5 = "draw_5"
MODIFIER_DRAW_6 = "draw_6"
MODIFIER_DRAW_7 = "draw_7"
MODIFIER_SCRAP = "scrap"
MODIFIER_RECYCLE = "recycle"
MODIFIER_SWAP_DRAW = "swap_draw"
MODIFIER_REDRAFT = "redraft"
MODIFIER_REDRAFT_PLUS = "redraft_plus"
MODIFIER_GUARD = "guard"
MODIFIER_GUARD_PLUS = "guard_plus"
MODIFIER_BREAK = "break_effect"
MODIFIER_BREAK_PLUS = "break_all"
MODIFIER_LOCKDOWN = "lockdown"
MODIFIER_PRECISION_DRAW = "precision_draw"
MODIFIER_PRECISION_DRAW_PLUS = "precision_draw_plus"
MODIFIER_PRIME_DRAW = "prime_draw"
MODIFIER_TARGET_17 = "target_17"
MODIFIER_TARGET_24 = "target_24"
MODIFIER_TARGET_27 = "target_27"
MODIFIER_SALVAGE = "salvage"
MODIFIER_AID_RIVAL = "aid_rival"
MODIFIER_BREAK_SHIELDS = "break_shields"
MODIFIER_BREAK_SHIELDS_PLUS = "break_shields_plus"
MODIFIER_SHARED_CACHE = "shared_cache"
MODIFIER_HAND_TAX = "hand_tax"
MODIFIER_HAND_TAX_PLUS = "hand_tax_plus"
MODIFIER_MIND_TAX = "mind_tax"
MODIFIER_MIND_TAX_PLUS = "mind_tax_plus"
MODIFIER_ARCANE_CACHE = "arcane_cache"
MODIFIER_HEX_DRAW = "hex_draw"
MODIFIER_DARK_BARGAIN = "dark_bargain"
MODIFIER_ESCAPE_ROUTE = "escape_route"
MODIFIER_EXACT_21_SURGE = "exact_21_surge"
MODIFIER_ROUND_ERASE = "round_erase"
MODIFIER_DRAW_SILENCE = "draw_silence"
MODIFIER_ALL_IN_SILENCE = "all_in_silence"

MODIFIER_POOL = (
    MODIFIER_RAISE_1,
    MODIFIER_RAISE_2,
    MODIFIER_RAISE_2_PLUS,
    MODIFIER_DRAW_2,
    MODIFIER_DRAW_3,
    MODIFIER_DRAW_4,
    MODIFIER_DRAW_5,
    MODIFIER_DRAW_6,
    MODIFIER_DRAW_7,
    MODIFIER_SCRAP,
    MODIFIER_RECYCLE,
    MODIFIER_SWAP_DRAW,
    MODIFIER_REDRAFT,
    MODIFIER_REDRAFT_PLUS,
    MODIFIER_GUARD,
    MODIFIER_GUARD_PLUS,
    MODIFIER_BREAK,
    MODIFIER_BREAK_PLUS,
    MODIFIER_LOCKDOWN,
    MODIFIER_PRECISION_DRAW,
    MODIFIER_PRECISION_DRAW_PLUS,
    MODIFIER_PRIME_DRAW,
    MODIFIER_TARGET_17,
    MODIFIER_TARGET_24,
    MODIFIER_TARGET_27,
    MODIFIER_SALVAGE,
    MODIFIER_AID_RIVAL,
    MODIFIER_BREAK_SHIELDS,
    MODIFIER_BREAK_SHIELDS_PLUS,
    MODIFIER_SHARED_CACHE,
    MODIFIER_HAND_TAX,
    MODIFIER_HAND_TAX_PLUS,
    MODIFIER_MIND_TAX,
    MODIFIER_MIND_TAX_PLUS,
    MODIFIER_ARCANE_CACHE,
    MODIFIER_HEX_DRAW,
    MODIFIER_DARK_BARGAIN,
    MODIFIER_ESCAPE_ROUTE,
    MODIFIER_EXACT_21_SURGE,
    MODIFIER_ROUND_ERASE,
    MODIFIER_DRAW_SILENCE,
    MODIFIER_ALL_IN_SILENCE,
)

DEFAULT_MODIFIER_DRAW_WEIGHT = 100
ENHANCED_MODIFIER_DRAW_WEIGHT = DEFAULT_MODIFIER_DRAW_WEIGHT // 2
DOUBLE_ENHANCED_MODIFIER_DRAW_WEIGHT = ENHANCED_MODIFIER_DRAW_WEIGHT // 2
ENDGAME_MODIFIER_DRAW_WEIGHT = 10
TRIPLE_ENHANCED_MODIFIER_DRAW_WEIGHT = ENDGAME_MODIFIER_DRAW_WEIGHT

# Most change cards are equally likely. For card families where an enhanced
# version adds change-card gain on top of a base effect, reduce draw odds by tier:
# enhanced = 50% of base, double enhanced = 25% of base.
MODIFIER_DRAW_WEIGHTS = {modifier: DEFAULT_MODIFIER_DRAW_WEIGHT for modifier in MODIFIER_POOL}
MODIFIER_DRAW_WEIGHTS.update(
    {
        MODIFIER_RAISE_2: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_RAISE_2_PLUS: DOUBLE_ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_GUARD_PLUS: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_REDRAFT_PLUS: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_BREAK_PLUS: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_LOCKDOWN: DOUBLE_ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_PRECISION_DRAW_PLUS: DOUBLE_ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_PRIME_DRAW: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_BREAK_SHIELDS_PLUS: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_HAND_TAX: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_HAND_TAX_PLUS: DOUBLE_ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_MIND_TAX_PLUS: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_HEX_DRAW: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_ESCAPE_ROUTE: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_EXACT_21_SURGE: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_DRAW_SILENCE: ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_DARK_BARGAIN: DOUBLE_ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_ROUND_ERASE: TRIPLE_ENHANCED_MODIFIER_DRAW_WEIGHT,
        MODIFIER_ALL_IN_SILENCE: ENDGAME_MODIFIER_DRAW_WEIGHT,
    }
)

MODIFIER_LABELS = {
    modifier: f"twentyone-modifier-label-{modifier.replace('_', '-')}" for modifier in MODIFIER_POOL
}
MODIFIER_HELP = tuple(MODIFIER_POOL)
MODIFIER_HELP_MAP = {
    modifier: f"twentyone-modifier-help-{modifier.replace('_', '-')}" for modifier in MODIFIER_POOL
}

TABLE_EFFECT_MODIFIERS = {
    MODIFIER_RAISE_1,
    MODIFIER_RAISE_2,
    MODIFIER_RAISE_2_PLUS,
    MODIFIER_GUARD,
    MODIFIER_GUARD_PLUS,
    MODIFIER_LOCKDOWN,
    MODIFIER_PRECISION_DRAW_PLUS,
    MODIFIER_TARGET_17,
    MODIFIER_TARGET_24,
    MODIFIER_TARGET_27,
    MODIFIER_SALVAGE,
    MODIFIER_BREAK_SHIELDS,
    MODIFIER_BREAK_SHIELDS_PLUS,
    MODIFIER_HAND_TAX,
    MODIFIER_HAND_TAX_PLUS,
    MODIFIER_MIND_TAX,
    MODIFIER_MIND_TAX_PLUS,
    MODIFIER_ARCANE_CACHE,
    MODIFIER_DARK_BARGAIN,
    MODIFIER_ESCAPE_ROUTE,
    MODIFIER_EXACT_21_SURGE,
    MODIFIER_DRAW_SILENCE,
    MODIFIER_ALL_IN_SILENCE,
}

TARGET_VALUE_MODIFIERS = {
    MODIFIER_TARGET_17: 17,
    MODIFIER_TARGET_24: 24,
    MODIFIER_TARGET_27: 27,
}

EXACT_DRAW_MODIFIERS = {
    MODIFIER_DRAW_2,
    MODIFIER_DRAW_3,
    MODIFIER_DRAW_4,
    MODIFIER_DRAW_5,
    MODIFIER_DRAW_6,
    MODIFIER_DRAW_7,
}

SELF_DRAW_MODIFIERS = {
    *EXACT_DRAW_MODIFIERS,
    MODIFIER_PRECISION_DRAW,
    MODIFIER_PRECISION_DRAW_PLUS,
    MODIFIER_PRIME_DRAW,
    MODIFIER_DARK_BARGAIN,
}

OPPONENT_DRAW_MODIFIERS = {
    MODIFIER_AID_RIVAL,
    MODIFIER_HEX_DRAW,
}

# Persistent table effects that act ON a chosen opponent. When played in a 3+
# player game the actor picks one opponent and the effect remembers them (stored
# in table_modifier_targets), so its damage/lock keeps hitting that same player
# until it expires. Self effects (guard, salvage, arcane_cache, target changes)
# are NOT in this set and store target None.
TARGETED_TABLE_EFFECTS = {
    MODIFIER_RAISE_1,
    MODIFIER_RAISE_2,
    MODIFIER_RAISE_2_PLUS,
    MODIFIER_PRECISION_DRAW_PLUS,
    MODIFIER_BREAK_SHIELDS,
    MODIFIER_BREAK_SHIELDS_PLUS,
    MODIFIER_HAND_TAX,
    MODIFIER_HAND_TAX_PLUS,
    MODIFIER_DARK_BARGAIN,
    MODIFIER_EXACT_21_SURGE,
    MODIFIER_DRAW_SILENCE,
    MODIFIER_ALL_IN_SILENCE,
    MODIFIER_LOCKDOWN,
    MODIFIER_MIND_TAX,
    MODIFIER_MIND_TAX_PLUS,
}

# One-shot change cards that act on a single chosen opponent (resolve
# immediately, no lasting table effect).
ONE_SHOT_TARGET_MODIFIERS = {
    MODIFIER_SCRAP,
    MODIFIER_SWAP_DRAW,
    MODIFIER_HEX_DRAW,
    MODIFIER_AID_RIVAL,
    MODIFIER_BREAK,
    MODIFIER_BREAK_PLUS,
}

# Every change card whose effect lands on one chosen opponent. With 3+ players
# these prompt the actor to pick a target; with a single opponent the choice is
# implicit and no prompt is shown.
SINGLE_TARGET_MODIFIERS = TARGETED_TABLE_EFFECTS | ONE_SHOT_TARGET_MODIFIERS

TABLE_EFFECT_LIMIT = 5
LocalizedArgsFactory = Callable[[str], dict[str, object]]
CardAnnouncement = tuple[str, str, LocalizedArgsFactory]

SOUND_ROUND_START = "game_pig/roundstart.ogg"
SOUND_ROUND_DEAL = "game_cards/draw2.ogg"
SOUND_ROUND_RESOLVE = "game_cards/small_shuffle.ogg"
SOUND_TURN = "game_3cardpoker/turn.ogg"
SOUND_HIT = "game_cards/draw3.ogg"
SOUND_STAND = "game_blackjack/stand.ogg"
SOUND_OPPONENT_STAND = "game_pig/turn.ogg"
SOUND_CHANGE_MENU_OPEN = "menuclick.ogg"
SOUND_PLAY_CHANGE_CARD = "game_cards/play1.ogg"
SOUND_MOD_RAISE = "game_3cardpoker/bet.ogg"
SOUND_MOD_DEFEND = "game_blackjack/doubledown.ogg"
SOUND_MOD_DRAW = "game_cards/draw3.ogg"
SOUND_MOD_CONTROL = "game_cards/play3.ogg"
SOUND_MOD_ENEMY = "game_cards/play4.ogg"
SOUND_MOD_ENDGAME = "game_cards/draw4.ogg"
SOUND_TARGET_17 = "game_pig/roll.ogg"
SOUND_TARGET_24 = "game_cards/shuffle2.ogg"
SOUND_TARGET_27 = "game_cards/shuffle3.ogg"
SOUND_MOD_REFRESH = "game_cards/shuffle1.ogg"
SOUND_ROUND_WIN = "game_pig/win.ogg"
SOUND_ROUND_LOSE = "game_pig/lose.ogg"
SOUND_ROUND_DRAW = "game_crazyeights/draw.ogg"
SOUND_BUST = "game_blackjack/bust1.ogg"
SOUND_DAMAGE = "game_blackjack/bust2.ogg"
SOUND_ACTION_FAIL = "game_coup/challengefail.ogg"
SOUND_EFFECT_EXPIRE = "game_cards/discard2.ogg"
SOUND_CONTROL_SUCCESS = "game_cards/play2.ogg"
SOUND_GAIN_CHANGE_CARD = "game_cards/draw1.ogg"
SOUND_LOSE_CHANGE_CARD = "game_cards/discard1.ogg"
SOUND_BET_UP = "game_3cardpoker/winbet.ogg"
SOUND_BET_DOWN = "game_cards/discard3.ogg"
SOUND_NEAR_BUST = "game_crazyeights/fivesec.ogg"
SOUND_LOCKDOWN_APPLY = "game_crazyeights/discskip.ogg"
SOUND_LOCKDOWN_ACTIVE = "game_crazyeights/expired.ogg"
SOUND_LOCKDOWN_END = "game_crazyeights/pass.ogg"
SOUND_CLOSE_WIN = "game_blackjack/win1.ogg"
SOUND_CLOSE_LOSE = "game_uno/loseround.ogg"
SOUND_DOUBLE_BUST_DRAW = "game_blackjack/bust3.ogg"
SOUND_DAMAGE_HEAVY = "game_crazyeights/hitmark.ogg"
SOUND_GAME_WIN = "game_pig/wingame.ogg"
SOUND_GAME_NO_WIN = "game_crazyeights/pileempty.ogg"

BETWEEN_ROUND_WAIT_TICKS = 100
BETWEEN_ROUND_RESOLVE_DELAY_TICKS = 20
BOT_DRAW_STAND_DELAY_TICKS = 40


@dataclass
class TwentyOneOptions(GameOptions):
    """Survival 21 defaults for Play Palace PvP."""

    starting_health: int = option_field(
        IntOption(
            default=10,
            min_val=1,
            max_val=100,
            value_key="hp",
            label="twentyone-option-starting-health",
            prompt="twentyone-option-enter-starting-health",
            change_msg="twentyone-option-changed-starting-health",
        )
    )
    base_bet: int = option_field(
        IntOption(
            default=1,
            min_val=0,
            max_val=50,
            value_key="bet",
            label="twentyone-option-base-bet",
            prompt="twentyone-option-enter-base-bet",
            change_msg="twentyone-option-changed-base-bet",
        )
    )
    starting_modifiers_per_round: int = option_field(
        IntOption(
            default=1,
            min_val=0,
            max_val=10,
            value_key="count",
            label="twentyone-option-starting-change-cards",
            prompt="twentyone-option-enter-starting-change-cards",
            change_msg="twentyone-option-changed-starting-change-cards",
        )
    )
    draw_modifier_chance_percent: int = option_field(
        IntOption(
            default=35,
            min_val=0,
            max_val=100,
            value_key="percent",
            label="twentyone-option-draw-change-chance",
            prompt="twentyone-option-enter-draw-change-chance",
            change_msg="twentyone-option-changed-draw-change-chance",
        )
    )
    deck_count: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=10,
            value_key="count",
            label="twentyone-option-deck-count",
            prompt="twentyone-option-enter-deck-count",
            change_msg="twentyone-option-changed-deck-count",
        )
    )
    next_round_wait_ticks: int = BETWEEN_ROUND_WAIT_TICKS


@dataclass
class TwentyOnePlayer(Player):
    """Player state for Survival 21."""

    hand: list[Card] = field(default_factory=list)
    hp: int = 0
    modifiers: list[str] = field(default_factory=list)
    table_modifiers: list[str] = field(default_factory=list)
    # Parallel to table_modifiers: the player id each persistent effect targets,
    # or None for self / table-wide effects. Kept in lock-step with
    # table_modifiers so every mutation of one updates the other. Stored as plain
    # strings/None to stay serialization-friendly.
    table_modifier_targets: list[str | None] = field(default_factory=list)
    stand_pending: bool = False
    last_drawn_card_id: int | None = None
    turn_modifier_plays: int = 0


@dataclass
@register_game
class TwentyOneGame(ActionGuardMixin, Game):
    """Survival 21 ruleset with tactical modifier cards."""

    score_unit_key = "game-score-unit-health"

    players: list[TwentyOnePlayer] = field(default_factory=list)
    options: TwentyOneOptions = field(default_factory=TwentyOneOptions)
    deck: Deck | None = None
    phase: str = "lobby"  # lobby, turns, between_rounds, finished
    round_number: int = 0
    round_starter_index: int = 0
    next_round_wait_ticks: int = 0
    round_resolution_wait_ticks: int = 0
    # Round resolution state. These describe every alive player at settle time,
    # not just two, so 3+ player games resolve correctly. They are serialized,
    # so keep them JSON-friendly (lists/dicts of primitives).
    pending_round_player_ids: tuple[str, ...] | None = None
    pending_round_totals: tuple[int, ...] = ()
    pending_round_winner_ids: tuple[str, ...] = ()
    pending_round_target: int = 21
    modifier_used_since_last_stand_resolution: bool = False
    # When a single-target card is awaiting its target pick, the index of that
    # card in the actor's hand is stashed here (per player id).
    pending_target_modifier: dict[str, int] = field(default_factory=dict)

    @classmethod
    def get_name(cls) -> str:
        return "21 (Survival Rules)"

    @classmethod
    def get_name_key(cls) -> str:
        return "game-name-twentyone"

    @classmethod
    def get_type(cls) -> str:
        return "twentyone"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = list(super().prestart_validate())
        if (
            self.options.base_bet == 0
            and self.options.starting_modifiers_per_round == 0
            and self.options.draw_modifier_chance_percent == 0
        ):
            errors.append("twentyone-error-no-damage-source")
        return errors

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> TwentyOnePlayer:
        return TwentyOnePlayer(id=player_id, name=name, is_bot=is_bot)

    def _is_turn_action_enabled(self, player: Player) -> str | None:
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        if self.phase != "turns":
            return "action-not-available"
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        return self.turn_action_visibility(
            player,
            require_current_player=False,
            extra_condition=self.phase == "turns",
        )

    def _is_hit_enabled(self, player: Player) -> str | None:
        error = self._is_turn_action_enabled(player)
        if error:
            return error
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return "action-not-available"
        if not self.deck or self.deck.is_empty():
            return "twentyone-deck-empty-must-stand"
        return None

    def _is_play_modifier_enabled(self, player: Player) -> str | None:
        error = self._is_turn_action_enabled(player)
        if error:
            return error
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return "action-not-available"
        if not p.modifiers:
            return "action-not-available"
        return None

    def _is_play_modifier_hidden(self, player: Player) -> Visibility:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p or not p.modifiers:
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_touch_private_info_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_always_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_check_scores_hidden(player)

    def create_turn_action_set(self, player: TwentyOnePlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="hit",
                label=Localization.get(locale, "blackjack-hit"),
                handler="_action_hit",
                is_enabled="_is_hit_enabled",
                is_hidden="_is_turn_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="stand",
                label=Localization.get(locale, "blackjack-stand"),
                handler="_action_stand",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="play_modifier",
                label=Localization.get(locale, "twentyone-play-change-card"),
                handler="_action_play_modifier",
                is_enabled="_is_play_modifier_enabled",
                is_hidden="_is_play_modifier_hidden",
                input_request=MenuInput(
                    prompt="twentyone-select-change-card",
                    options="_options_for_play_modifier",
                    bot_select="_bot_select_play_modifier",
                ),
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="select_target",
                label=Localization.get(locale, "twentyone-select-target"),
                handler="_action_select_target",
                is_enabled="_is_select_target_enabled",
                is_hidden="_is_select_target_hidden",
                input_request=MenuInput(
                    prompt="twentyone-select-target-prompt",
                    options="_target_options",
                    bot_select="_bot_select_target",
                    option_label="_target_option_label",
                ),
                show_in_actions_menu=False,
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="check_21_status",
                label=Localization.get(locale, "twentyone-check-status"),
                handler="_action_check_status",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="modifier_guide",
                label=Localization.get(locale, "twentyone-change-card-guide"),
                handler="_action_modifier_guide",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_21_opponent_face_up",
                label=Localization.get(locale, "twentyone-read-opponent-face-up"),
                handler="_action_read_opponent_face_up",
                is_enabled="_is_check_enabled",
                is_hidden="_is_touch_private_info_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_21_hand",
                label=Localization.get(locale, "twentyone-read-current-hand"),
                handler="_action_read_current_hand",
                is_enabled="_is_check_enabled",
                is_hidden="_is_touch_private_info_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_21_bets",
                label=Localization.get(locale, "twentyone-read-current-bets"),
                handler="_action_read_current_bets",
                is_enabled="_is_check_enabled",
                is_hidden="_is_touch_private_info_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_21_active_effects",
                label=Localization.get(locale, "twentyone-read-active-effects"),
                handler="_action_read_active_effects",
                is_enabled="_is_check_enabled",
                is_hidden="_is_touch_private_info_hidden",
            )
        )
        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "modifier_guide",
                    "check_21_status",
                    "read_21_opponent_face_up",
                    "read_21_hand",
                    "read_21_bets",
                    "read_21_active_effects",
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind(
            "1", Localization.get("en", "blackjack-hit"), ["hit"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "2", Localization.get("en", "blackjack-stand"), ["stand"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "3",
            Localization.get("en", "twentyone-play-change-card"),
            ["play_modifier"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "4",
            Localization.get("en", "twentyone-check-status"),
            ["check_21_status"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "c",
            Localization.get("en", "twentyone-change-card-guide"),
            ["modifier_guide"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "o",
            Localization.get("en", "twentyone-read-opponent-face-up"),
            ["read_21_opponent_face_up"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "r",
            Localization.get("en", "twentyone-read-current-hand"),
            ["read_21_hand"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "w",
            Localization.get("en", "twentyone-read-current-bets"),
            ["read_21_bets"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "e",
            Localization.get("en", "twentyone-read-active-effects"),
            ["read_21_active_effects"],
            state=KeybindState.ACTIVE,
        )

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _render_modifier(self, locale: str, modifier: str) -> str:
        key = MODIFIER_LABELS.get(modifier)
        if not key:
            return modifier
        label = Localization.get(locale, key)
        return modifier if label == key else label

    def _render_modifier_list(self, locale: str, modifiers: list[str]) -> str:
        if not modifiers:
            return Localization.get(locale, "twentyone-none")
        return ", ".join(self._render_modifier(locale, modifier) for modifier in modifiers)

    @staticmethod
    def _render_card(locale: str, card: Card) -> str:
        return f"{card_name(card, locale)} ({card.rank})"

    def _broadcast_l_with_locale_args(
        self,
        message_id: str,
        args_for_locale: LocalizedArgsFactory,
        *,
        buffer: str = "game",
        exclude: Player | None = None,
    ) -> None:
        """Broadcast with per-recipient localized kwargs."""
        for participant in self.players:
            if participant is exclude:
                continue
            locale = self._player_locale(participant)
            kwargs = args_for_locale(locale)
            localized = Localization.get(locale, message_id, **kwargs)
            if hasattr(self, "record_transcript_event"):
                self.record_transcript_event(participant, localized, buffer)
            user = self.get_user(participant)
            if user:
                user.speak_l(message_id, buffer=buffer, **kwargs)

    def _broadcast_personal_l_with_locale_args(
        self,
        actor: TwentyOnePlayer,
        personal_message_id: str,
        others_message_id: str,
        args_for_locale: LocalizedArgsFactory,
        *,
        buffer: str = "game",
    ) -> None:
        """Personalized broadcast with per-recipient localized kwargs."""
        actor_locale = self._player_locale(actor)
        actor_kwargs = args_for_locale(actor_locale)
        actor_text = Localization.get(actor_locale, personal_message_id, **actor_kwargs)
        if hasattr(self, "record_transcript_event"):
            self.record_transcript_event(actor, actor_text, buffer)
        actor_user = self.get_user(actor)
        if actor_user:
            actor_user.speak_l(personal_message_id, buffer=buffer, **actor_kwargs)

        for participant in self.players:
            if participant is actor:
                continue
            locale = self._player_locale(participant)
            kwargs = args_for_locale(locale)
            localized = Localization.get(
                locale, others_message_id, player=actor.name, **kwargs
            )
            if hasattr(self, "record_transcript_event"):
                self.record_transcript_event(participant, localized, buffer)
            user = self.get_user(participant)
            if user:
                user.speak_l(others_message_id, buffer=buffer, player=actor.name, **kwargs)

    def _broadcast_personal_l(
        self,
        actor: TwentyOnePlayer,
        personal_message_id: str,
        others_message_id: str,
        *,
        buffer: str = "game",
        **kwargs: object,
    ) -> None:
        self._broadcast_personal_l_with_locale_args(
            actor,
            personal_message_id,
            others_message_id,
            lambda locale: dict(kwargs),
            buffer=buffer,
        )

    def _modifier_help(self, locale: str, modifier: str) -> str:
        key = MODIFIER_HELP_MAP.get(modifier)
        if not key:
            return ""
        help_text = Localization.get(locale, key)
        return "" if help_text == key else help_text

    @staticmethod
    def _menu_help_text(label: str, description: str) -> str:
        """Drop duplicate "<label>:" prefix so menus speak the card name once."""
        prefix, separator, remainder = description.partition(":")
        if separator and prefix.strip().casefold() == label.strip().casefold():
            return remainder.strip()
        return description

    def _options_for_play_modifier(self, player: Player) -> list[str]:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return []
        locale = self._player_locale(p)
        options: list[str] = []
        for display_index, modifier in enumerate(p.modifiers, start=1):
            label = self._render_modifier(locale, modifier)
            description = self._modifier_help(locale, modifier)
            reason = self._modifier_unplayable_reason(p, modifier, locale)
            if description:
                description = self._menu_help_text(label, description)
            if reason:
                unavailable = Localization.get(
                    locale, "twentyone-change-card-unavailable", reason=reason
                )
                description = f"{description} - {unavailable}" if description else unavailable
            if description:
                options.append(f"{display_index}:{label} - {description}")
            else:
                options.append(f"{display_index}:{label}")
        return options

    def _bot_select_play_modifier(self, player: Player, options: list[str]) -> str | None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return None
        modifier = self._bot_choose_modifier_to_play(p)
        if not modifier:
            return None
        for index, held_modifier in enumerate(p.modifiers):
            if held_modifier != modifier:
                continue
            if not self._is_single_modifier_playable(p, held_modifier):
                continue
            option_prefix = f"{index + 1}:"
            return next(
                (option for option in options if option.startswith(option_prefix)),
                None,
            )
        return None

    @staticmethod
    def _parse_modifier_option(option_value: str) -> int | None:
        try:
            prefix = option_value.split(":", 1)[0]
            return int(prefix)
        except (ValueError, IndexError):
            return None

    def _request_action_input(self, action: Action, player: Player) -> None:
        super()._request_action_input(action, player)
        if action.id != "play_modifier":
            return
        if self._pending_actions.get(player.id) != action.id:
            return
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        self._play_sound_for_player(p, SOUND_CHANGE_MENU_OPEN, volume=65)

    def _action_hit(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return

        if self._draws_locked_for(p):
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            self._announce_draw_locked(p)
            self.refresh_menus()
            return

        card = self._draw_card()
        if not card:
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            self._broadcast_personal_l(
                p,
                "twentyone-you-cannot-hit-empty-deck",
                "twentyone-player-cannot-hit-empty-deck",
            )
            self.refresh_menus()
            return

        self.play_sound(SOUND_HIT, volume=80)
        self._clear_pending_stands()
        self._add_card_to_hand(
            p,
            card,
            announcement=(
                "twentyone-you-draw-card",
                "twentyone-player-draws-card",
                lambda locale: {"card": self._render_card(locale, card)},
            ),
            reveal_to_others=True,
        )
        p.stand_pending = False

        chance = max(0, min(100, self.options.draw_modifier_chance_percent))
        if random.randint(1, 100) <= chance:  # nosec B311
            self._give_random_modifiers(p, 1, announce=True)

        self.refresh_menus()

    def _action_stand(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return

        self._play_sound_for_player(p, SOUND_STAND)
        self._play_opponent_stand_sound(p)
        p.stand_pending = True
        self._broadcast_personal_l(
            p,
            "twentyone-you-stand",
            "twentyone-player-stands",
            total=self._hand_total(p),
        )

        if self._both_players_standing():
            self.play_sound(SOUND_ROUND_RESOLVE, volume=65)
            self._settle_round()
            return

        self._advance_turn_after_action()

    def _action_play_modifier(self, player: Player, selected: str, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return

        choice_number = self._parse_modifier_option(selected)
        if choice_number is None:
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            self._speak_private_l(p, "twentyone-change-card-selection-invalid")
            return

        choice_index = choice_number - 1
        if choice_index < 0 or choice_index >= len(p.modifiers):
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            self._speak_private_l(p, "twentyone-change-card-selection-invalid")
            return

        modifier = p.modifiers[choice_index]
        if not self._is_single_modifier_playable(p, modifier):
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            self._speak_unplayable_modifier(p, modifier)
            return

        # Single-target cards need a target when more than one opponent exists.
        # Stash the chosen card and prompt for the target instead of resolving.
        opponents = self._opponents_of(p)
        if modifier in SINGLE_TARGET_MODIFIERS and len(opponents) > 1:
            self.pending_target_modifier[p.id] = choice_index
            self._request_select_target(p)
            return

        # Otherwise resolve now against the sole opponent (or no target).
        p.modifiers.pop(choice_index)
        self._resolve_played_modifier(p, modifier, opponents[0] if opponents else None)

    def _request_select_target(self, player: TwentyOnePlayer) -> None:
        """Prompt the actor to choose which opponent a stashed card hits."""
        if player.is_bot:
            options = self._target_options(player)
            chosen = self._bot_select_target(player, options) if options else None
            self._action_select_target(
                player, chosen if chosen is not None else "", "select_target"
            )
            return
        action = self.find_action(player, "select_target")
        if action:
            self._request_action_input(action, player)

    def _action_select_target(
        self, player: Player, selected: str, action_id: str
    ) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        choice_index = self.pending_target_modifier.pop(p.id, None)
        if choice_index is None:
            return
        if selected == "_cancel" or not selected:
            # Player backed out; the card was never spent, so just refresh.
            self.refresh_menus()
            return
        if choice_index < 0 or choice_index >= len(p.modifiers):
            self.refresh_menus()
            return

        target = self.get_player_by_id(self._extract_target_id(selected))
        if not isinstance(target, TwentyOnePlayer):
            self.refresh_menus()
            return

        modifier = p.modifiers.pop(choice_index)
        self._resolve_played_modifier(p, modifier, target)

    def _is_select_target_enabled(self, player: Player) -> str | None:
        if player.id not in self.pending_target_modifier:
            return "action-not-available"
        return None

    def _is_select_target_hidden(self, player: Player) -> Visibility:
        if player.id in self.pending_target_modifier:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _target_options(self, player: Player) -> list[str]:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return []
        # Option VALUES are raw opponent ids; the menu shows _target_option_label.
        return [opponent.id for opponent in self._opponents_of(p)]

    def _target_option_label(self, player: Player, option_value: str) -> str:
        locale = self._player_locale(player)
        opponent = self.get_player_by_id(option_value)
        if not isinstance(opponent, TwentyOnePlayer):
            return option_value
        shown_cards = self._opponent_visible_cards(opponent)
        shown_total = sum(card.rank for card in shown_cards)
        return Localization.get(
            locale,
            "twentyone-target-option",
            player=opponent.name,
            hp=opponent.hp,
            shown_total=shown_total,
        )

    @staticmethod
    def _extract_target_id(option_value: str) -> str:
        return option_value.strip()

    def _bot_select_target(self, player: Player, options: list[str]) -> str | None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p or not options:
            return None
        # Aim at the most threatening opponent: highest visible total, then
        # lowest HP as a tiebreak.
        opponents = self._opponents_of(p)
        if not opponents:
            return None
        threat = max(
            opponents,
            key=lambda o: (
                sum(card.rank for card in self._opponent_visible_cards(o)),
                -o.hp,
            ),
        )
        return threat.id if threat.id in options else options[0]

    def _resolve_played_modifier(
        self,
        p: TwentyOnePlayer,
        modifier: str,
        opponent: TwentyOnePlayer | None,
    ) -> None:
        my_bet_before = self._current_bet(p)
        opp_bet_before = self._current_bet(opponent) if opponent else my_bet_before
        self._play_modifier_sound(modifier)
        self._clear_pending_stands()
        self._announce_modifier_play(p, modifier, opponent)
        self._resolve_modifier(p, modifier, target=opponent)
        self._finish_modifier_play(p, opponent, my_bet_before, opp_bet_before)

    def _announce_modifier_play(
        self,
        p: TwentyOnePlayer,
        modifier: str,
        opponent: TwentyOnePlayer | None,
    ) -> None:
        has_desc = any(self._modifier_help(loc, modifier) for loc in ("en", "vi"))
        # Name the victim only when the card targets one of several opponents,
        # so the choice is visible to the table. Otherwise keep the plain form.
        name_target = (
            opponent is not None
            and modifier in SINGLE_TARGET_MODIFIERS
            and len(self._opponents_of(p)) > 1
        )

        if name_target:
            personal, others = (
                ("twentyone-you-play-modifier-on", "twentyone-player-plays-modifier-on")
                if has_desc
                else (
                    "twentyone-you-play-modifier-on-no-desc",
                    "twentyone-player-plays-modifier-on-no-desc",
                )
            )
            self._broadcast_personal_l_with_locale_args(
                p,
                personal,
                others,
                lambda locale: {
                    "modifier": self._render_modifier(locale, modifier),
                    "target": opponent.name,
                    **(
                        {"description": self._modifier_help(locale, modifier)}
                        if has_desc
                        else {}
                    ),
                },
            )
            return

        if has_desc:
            self._broadcast_personal_l_with_locale_args(
                p,
                "twentyone-you-play-modifier",
                "twentyone-player-plays-modifier",
                lambda locale: {
                    "modifier": self._render_modifier(locale, modifier),
                    "description": self._modifier_help(locale, modifier),
                },
            )
        else:
            self._broadcast_personal_l_with_locale_args(
                p,
                "twentyone-you-play-modifier-no-desc",
                "twentyone-player-plays-modifier-no-desc",
                lambda locale: {"modifier": self._render_modifier(locale, modifier)},
            )

    def _finish_modifier_play(
        self,
        p: TwentyOnePlayer,
        opponent: TwentyOnePlayer | None,
        my_bet_before: int,
        opp_bet_before: int,
    ) -> None:
        p.turn_modifier_plays += 1
        self._handle_mind_tax_break(p)
        self.modifier_used_since_last_stand_resolution = True
        self._trigger_harvest_rewards()
        if self.phase != "turns":
            self.refresh_menus()
            return
        if opponent:
            self._play_bet_change_sounds(p, opponent, my_bet_before, opp_bet_before)
        self.refresh_menus()

    def _action_check_status(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        locale = self._player_locale(p)
        target = self._current_target()
        bet = self._current_bet(p)
        none_text = Localization.get(locale, "twentyone-none")
        hand_text = ", ".join(str(card.rank) for card in p.hand) if p.hand else none_text
        modifiers_text = self._render_modifier_list(locale, p.modifiers)
        table_text = self._render_modifier_list(locale, p.table_modifiers)
        user.speak_l(
            "twentyone-check-status-response",
            buffer="game",
            target=target,
            hp=p.hp,
            bet=bet,
            hand=hand_text,
            total=self._hand_total(p),
            modifiers=modifiers_text,
            effects=table_text,
        )
        user.speak_l("twentyone-check-status-guide-hint", buffer="game")
        for opponent in self._opponents_of(p):
            shown_cards = self._opponent_visible_cards(opponent)
            shown_text = (
                ", ".join(str(card.rank) for card in shown_cards) if shown_cards else none_text
            )
            shown_total = sum(card.rank for card in shown_cards)
            user.speak_l(
                "twentyone-check-status-opponent",
                buffer="game",
                player=opponent.name,
                hp=opponent.hp,
                bet=self._current_bet(opponent),
                shown_cards=shown_text,
                shown_total=shown_total,
            )

    def _action_modifier_guide(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        locale = self._player_locale(p)
        lines = [Localization.get(locale, "twentyone-change-card-guide-header")]
        for modifier_id in MODIFIER_HELP:
            name = self._render_modifier(locale, modifier_id)
            description = self._modifier_help(locale, modifier_id)
            lines.append(
                Localization.get(
                    locale,
                    "twentyone-change-card-guide-entry",
                    name=name,
                    description=description,
                )
            )
        lines.append(Localization.get(locale, "twentyone-change-card-guide-footer"))
        self.status_box(p, lines)

    def _action_read_opponent_face_up(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return
        opponents = self._opponents_of(p)
        if not opponents:
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            user.speak_l("twentyone-no-opponent-available", buffer="game")
            return

        locale = self._player_locale(p)
        none_text = Localization.get(locale, "twentyone-none")
        for opponent in opponents:
            shown_cards = self._opponent_visible_cards(opponent)
            shown_text = (
                ", ".join(str(card.rank) for card in shown_cards) if shown_cards else none_text
            )
            shown_total = sum(card.rank for card in shown_cards)
            user.speak_l(
                "twentyone-opponent-face-up-response",
                buffer="game",
                player=opponent.name,
                shown_cards=shown_text,
                shown_total=shown_total,
            )

    def _action_read_current_hand(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        hand_text = (
            ", ".join(str(card.rank) for card in p.hand)
            if p.hand
            else Localization.get(
                self._player_locale(p),
                "twentyone-none",
            )
        )
        user.speak_l(
            "twentyone-read-hand-response",
            buffer="game",
            hand=hand_text,
            total=self._hand_total(p),
        )

    def _action_read_current_bets(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        my_bet = self._current_bet(p)
        opponents = self._opponents_of(p)
        if not opponents:
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            user.speak_l("twentyone-read-bet-response-single", buffer="game", bet=my_bet)
            return

        locale = self._player_locale(p)
        entries = [(p, my_bet)] + [(opp, self._current_bet(opp)) for opp in opponents]
        bets_text = ". ".join(
            Localization.get(locale, "twentyone-read-bet-line", player=who.name, bet=amount)
            for who, amount in entries
        )
        user.speak_l(
            "twentyone-read-bet-response",
            buffer="game",
            bets=bets_text,
        )

    def _action_read_active_effects(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        locale = self._player_locale(p)
        my_effects = self._render_modifier_list(locale, p.table_modifiers)
        opponents = self._opponents_of(p)
        if not opponents:
            user.speak_l(
                "twentyone-active-effects-single",
                buffer="game",
                player=p.name,
                effects=my_effects,
            )
            return

        entries = [(p, my_effects)] + [
            (opp, self._render_modifier_list(locale, opp.table_modifiers))
            for opp in opponents
        ]
        lines_text = ". ".join(
            Localization.get(
                locale, "twentyone-active-effects-line", player=who.name, effects=effects
            )
            for who, effects in entries
        )
        user.speak_l(
            "twentyone-active-effects-all",
            buffer="game",
            lines=lines_text,
        )

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self.phase = "turns"
        self.round_number = 0
        self.round_starter_index = 0
        self.next_round_wait_ticks = 0
        self._clear_pending_round_resolution()
        self.modifier_used_since_last_stand_resolution = False

        active = self.get_active_players()
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active])
        self._team_manager.reset_all_scores()

        for player in active:
            if not isinstance(player, TwentyOnePlayer):
                continue
            player.hp = max(1, self.options.starting_health)
            player.hand.clear()
            player.modifiers.clear()
            self._clear_table_effects(player)
            player.stand_pending = False
            player.last_drawn_card_id = None
            player.turn_modifier_plays = 0

        self._sync_hp_scores()
        self._start_round(rotate_starter=False)

    def on_tick(self) -> None:
        super().on_tick()
        if not self.game_active or self.status != "playing":
            return

        if self.phase == "between_rounds":
            if self.round_resolution_wait_ticks > 0:
                self.round_resolution_wait_ticks -= 1
                if self.round_resolution_wait_ticks == 0:
                    self._resolve_pending_round()
                    if self.phase != "between_rounds":
                        return
            if self.next_round_wait_ticks > 0:
                self.next_round_wait_ticks -= 1
            if self.next_round_wait_ticks <= 0 and self.pending_round_player_ids is None:
                self._start_round(rotate_starter=True)
            return

        if self.phase == "turns":
            self._process_bot_turn()

    def _start_round(self, *, rotate_starter: bool) -> None:
        alive = self._alive_players()
        if len(alive) <= 1:
            self._end_game(alive[0] if alive else None)
            return

        if rotate_starter:
            self.round_starter_index = (self.round_starter_index + 1) % len(alive)
        if self.round_starter_index >= len(alive):
            self.round_starter_index = 0

        self.phase = "turns"
        self.round_number += 1
        self.next_round_wait_ticks = 0
        self._clear_pending_round_resolution()
        self.pending_target_modifier.clear()
        self.modifier_used_since_last_stand_resolution = False
        self.play_sound(SOUND_ROUND_START, volume=70)

        self._build_round_deck()

        for player in alive:
            player.hand.clear()
            self._clear_table_effects(player)
            player.stand_pending = False
            player.last_drawn_card_id = None
            player.turn_modifier_plays = 0
            self._give_random_modifiers(
                player, self.options.starting_modifiers_per_round, announce=False
            )

        for deal_round in range(2):
            for player in alive:
                card = self._draw_card()
                if card:
                    reveal = deal_round > 0
                    self._add_card_to_hand(
                        player, card, announcement=None, reveal_to_others=reveal
                    )
        self.play_sound(SOUND_ROUND_DEAL, volume=60)

        self.set_turn_players(alive, reset_index=True)
        self.turn_index = self.round_starter_index

        self.broadcast_l(
            "twentyone-round-begins", round=self.round_number, target=self._current_target(), buffer="game"
        )
        for player in alive:
            shown = self._peek_last_drawn_card(player)
            if shown:
                self._broadcast_personal_l_with_locale_args(
                    player,
                    "twentyone-you-show-card",
                    "twentyone-player-shows-card",
                    lambda locale: {"card": self._render_card(locale, shown)},
                )
            else:
                self._broadcast_personal_l(
                    player,
                    "twentyone-you-receive-cards",
                    "twentyone-player-receives-cards",
                )
            user = self.get_user(player)
            if user:
                if player.hand:
                    user.speak_l(
                        "twentyone-your-hidden-card",
                        buffer="game",
                        rank=player.hand[0].rank,
                    )
                if shown:
                    user.speak_l(
                        "twentyone-your-shown-card",
                        buffer="game",
                        rank=shown.rank,
                    )
                user.speak_l("twentyone-your-total", buffer="game", total=self._hand_total(player))
                modifiers_text = self._render_modifier_list(user.locale, player.modifiers)
                user.speak_l("twentyone-your-change-cards", buffer="game", cards=modifiers_text)

        current = self.current_player
        if current:
            current.turn_modifier_plays = 0
            self.announce_turn(turn_sound=SOUND_TURN)
            self._play_target_reminder_sound(current)
            if self._modifiers_locked_for(current):
                self._play_sound_for_player(current, SOUND_LOCKDOWN_ACTIVE, volume=65)
        self.refresh_menus()

    def _advance_turn_after_action(self) -> None:
        if self.phase != "turns":
            return
        self.advance_turn(announce=False)
        current = self.current_player
        if current:
            # Mind-tax break thresholds are per turn, so reset when a new turn begins.
            current.turn_modifier_plays = 0
            self.announce_turn(turn_sound=SOUND_TURN)
            self._play_target_reminder_sound(current)
            if self._modifiers_locked_for(current):
                self._play_sound_for_player(current, SOUND_LOCKDOWN_ACTIVE, volume=65)
        self.refresh_menus()

    def _settle_round(self) -> None:
        players = self._alive_players()
        if len(players) < 2:
            self._end_game(players[0] if players else None)
            return

        self.phase = "between_rounds"
        target = self._current_target()
        totals = [self._hand_total(p) for p in players]

        self._announce_round_reveals(*players)
        self.broadcast_l(
            "twentyone-round-totals",
            target=target,
            totals=self._format_round_totals(players, totals),
            buffer="game",
        )

        winner_ids = self._resolve_round_outcome(players, totals, target)
        self.pending_round_player_ids = tuple(p.id for p in players)
        self.pending_round_totals = tuple(totals)
        self.pending_round_winner_ids = tuple(winner_ids)
        self.pending_round_target = target
        self.round_resolution_wait_ticks = BETWEEN_ROUND_RESOLVE_DELAY_TICKS

        configured_wait = max(0, self.options.next_round_wait_ticks)
        self.next_round_wait_ticks = max(BETWEEN_ROUND_WAIT_TICKS, configured_wait)
        self.refresh_menus()

    def _format_round_totals(
        self, players: list[TwentyOnePlayer], totals: list[int]
    ) -> str:
        return ", ".join(f"{p.name} {total}" for p, total in zip(players, totals))

    def _clear_pending_round_resolution(self) -> None:
        self.round_resolution_wait_ticks = 0
        self.pending_round_player_ids = None
        self.pending_round_totals = ()
        self.pending_round_winner_ids = ()
        self.pending_round_target = 21

    def _announce_round_reveals(self, *players: TwentyOnePlayer) -> None:
        for player in players:
            if not player.hand:
                continue
            hidden_card = player.hand[0]
            self._broadcast_personal_l_with_locale_args(
                player,
                "twentyone-your-hidden-card-was",
                "twentyone-player-hidden-card-was",
                lambda locale, card=hidden_card: {"card": self._render_card(locale, card)},
            )

    def _resolve_pending_round(self) -> None:
        player_ids = self.pending_round_player_ids
        if not player_ids:
            self._clear_pending_round_resolution()
            return

        players: list[TwentyOnePlayer] = []
        for pid in player_ids:
            candidate = self.get_player_by_id(pid)
            if not isinstance(candidate, TwentyOnePlayer):
                self._clear_pending_round_resolution()
                return
            players.append(candidate)

        target = self.pending_round_target
        totals = list(self.pending_round_totals)
        winner_ids = set(self.pending_round_winner_ids)
        busts = {p.id: total > target for p, total in zip(players, totals)}

        winners = [p for p in players if p.id in winner_ids]
        losers = [p for p in players if p.id not in winner_ids]

        # Everyone but the winner(s) takes damage equal to their current bet.
        for loser in losers:
            self._apply_round_loss_damage(loser)

        # Announce the result from each player's perspective.
        if not winners:
            # Exact tie for best total: nobody wins, everyone takes damage.
            self.broadcast_l("twentyone-round-draw-damage", buffer="game")
        else:
            for winner in winners:
                self._broadcast_personal_l(
                    winner,
                    "twentyone-you-win-round",
                    "twentyone-player-wins-round",
                )

        self._play_round_outcome_sounds(players, winner_ids, totals, target)
        self._apply_round_end_change_card_effects(players)

        # Bust call-outs.
        busted = [p for p in players if busts[p.id]]
        if len(busted) == len(players) and players:
            self.broadcast_l("twentyone-both-busted-closer", buffer="game")
            for p in busted:
                self._play_sound_for_player(p, SOUND_BUST)
        else:
            for p in busted:
                self._broadcast_personal_l(
                    p,
                    "twentyone-you-busted",
                    "twentyone-player-busted",
                )
                self._play_sound_for_player(p, SOUND_BUST)

        self._sync_hp_scores()
        self._clear_pending_round_resolution()
        survivors = self._alive_players()
        if len(survivors) <= 1:
            self._end_game(survivors[0] if survivors else None)
            return
        self.refresh_menus()

    def _process_bot_turn(self) -> None:
        current = self.current_player
        if not isinstance(current, TwentyOnePlayer) or not current.is_bot:
            return

        if current.bot_think_ticks > 0:
            current.bot_think_ticks -= 1
            if current.bot_think_ticks > 0:
                return

        if current.bot_pending_action:
            action_id = current.bot_pending_action
            current.bot_pending_action = None
            self.execute_action(current, action_id)
            return

        action_id = self.bot_think(current)
        if not action_id:
            return
        current.bot_pending_action = action_id
        if action_id in {"hit", "stand"}:
            current.bot_think_ticks = BOT_DRAW_STAND_DELAY_TICKS

    @staticmethod
    def _resolve_round_outcome(
        players: list[TwentyOnePlayer], totals: list[int], target: int
    ) -> list[str]:
        """Return the id(s) of the round winner.

        Winner is closest to the target without busting. If every player busts,
        the closest to the target wins. A unique best total wins outright; an
        exact tie for best means nobody wins (everyone takes damage), matching
        the original two-player rule where equal totals were a draw.
        """
        if not players:
            return []

        entries = list(zip(players, totals))
        non_bust = [(p, total) for p, total in entries if total <= target]
        pool = non_bust if non_bust else entries

        # Among the pool, "best" = closest to target. For non-bust that is the
        # highest total; for the all-bust pool it is the smallest distance.
        def distance(total: int) -> int:
            return abs(target - total)

        best_distance = min(distance(total) for _p, total in pool)
        best = [p for p, total in pool if distance(total) == best_distance]

        # Unique best wins; a tie for best is a draw (no winner).
        if len(best) == 1:
            return [best[0].id]
        return []

    def _apply_round_loss_damage(self, loser: TwentyOnePlayer) -> None:
        if MODIFIER_ESCAPE_ROUTE in loser.table_modifiers:
            self._remove_table_effect_by_value(loser, MODIFIER_ESCAPE_ROUTE)
            self.play_sound(SOUND_EFFECT_EXPIRE, volume=70)
            self._broadcast_personal_l_with_locale_args(
                loser,
                "twentyone-you-avoid-damage-with-effect",
                "twentyone-player-avoids-damage-with-effect",
                lambda locale: {
                    "effect": self._render_modifier(locale, MODIFIER_ESCAPE_ROUTE)
                },
            )
            return

        damage = max(0, self._current_bet(loser))
        if damage <= 0:
            self._broadcast_personal_l(
                loser,
                "twentyone-you-lose-zero-bet",
                "twentyone-player-loses-zero-bet",
            )
            return
        loser.hp = max(0, loser.hp - damage)
        if damage >= 5:
            self._play_sound_for_player(loser, SOUND_DAMAGE_HEAVY)
        else:
            self._play_sound_for_player(loser, SOUND_DAMAGE)
        self._broadcast_personal_l(
            loser,
            "twentyone-you-take-damage",
            "twentyone-player-takes-damage",
            damage=damage,
            hp=loser.hp,
        )

    def _end_game(self, winner: TwentyOnePlayer | None) -> None:
        self.phase = "finished"
        if winner:
            self._play_sound_for_player(winner, SOUND_GAME_WIN, volume=80)
            self._broadcast_personal_l(
                winner,
                "twentyone-you-win-game",
                "twentyone-player-wins-game",
                hp=winner.hp,
            )
        else:
            self.play_sound(SOUND_GAME_NO_WIN, volume=75)
            self.broadcast_l("twentyone-game-no-winner", buffer="game")
        self.finish_game()

    def _play_round_outcome_sounds(
        self,
        players: list[TwentyOnePlayer],
        winner_ids: set[str],
        totals: list[int],
        target: int,
    ) -> None:
        busts = {p.id: total > target for p, total in zip(players, totals)}

        # No winner: a draw. Everyone busting gets the double-bust cue.
        if not winner_ids:
            all_bust = all(busts.values()) and bool(players)
            for p in players:
                self._play_sound_for_player(
                    p, SOUND_DOUBLE_BUST_DRAW if all_bust else SOUND_ROUND_DRAW
                )
            return

        # A round is "close" when the winning margin over the best loser is <= 1
        # and nobody busted, mirroring the original two-player feel.
        non_bust_totals = [total for p, total in zip(players, totals) if not busts[p.id]]
        winner_total = max(
            (total for p, total in zip(players, totals) if p.id in winner_ids),
            default=0,
        )
        runner_up = max(
            (t for t in non_bust_totals if t < winner_total), default=winner_total
        )
        close_margin = (winner_total - runner_up) <= 1 and not any(busts.values())

        for p in players:
            if p.id in winner_ids:
                self._play_sound_for_player(
                    p, SOUND_CLOSE_WIN if close_margin else SOUND_ROUND_WIN
                )
            else:
                self._play_sound_for_player(
                    p, SOUND_CLOSE_LOSE if close_margin else SOUND_ROUND_LOSE
                )

    def _play_sound_for_player(
        self, player: TwentyOnePlayer, sound_name: str, *, volume: int = 100
    ) -> None:
        user = self.get_user(player)
        if user:
            user.play_sound(sound_name, volume=volume)

    def _play_opponent_stand_sound(self, player: TwentyOnePlayer) -> None:
        for other in self._alive_players():
            if other.id != player.id:
                self._play_sound_for_player(other, SOUND_OPPONENT_STAND, volume=70)

    def _play_modifier_sound(self, modifier: str) -> None:
        if modifier in (MODIFIER_ROUND_ERASE, MODIFIER_ALL_IN_SILENCE):
            self.play_sound(SOUND_MOD_ENDGAME, volume=75)
            return
        if modifier in (
            MODIFIER_BREAK_SHIELDS,
            MODIFIER_BREAK_SHIELDS_PLUS,
            MODIFIER_HAND_TAX,
            MODIFIER_HAND_TAX_PLUS,
            MODIFIER_MIND_TAX,
            MODIFIER_MIND_TAX_PLUS,
            MODIFIER_ESCAPE_ROUTE,
            MODIFIER_DRAW_SILENCE,
        ):
            self.play_sound(SOUND_MOD_ENEMY, volume=75)
            return
        if modifier in (
            MODIFIER_RAISE_1,
            MODIFIER_RAISE_2,
            MODIFIER_RAISE_2_PLUS,
            MODIFIER_EXACT_21_SURGE,
        ):
            self.play_sound(SOUND_MOD_RAISE, volume=75)
            return
        if modifier in (MODIFIER_GUARD, MODIFIER_GUARD_PLUS):
            self.play_sound(SOUND_MOD_DEFEND, volume=75)
            return
        if modifier in (
            MODIFIER_DRAW_2,
            MODIFIER_DRAW_3,
            MODIFIER_DRAW_4,
            MODIFIER_DRAW_5,
            MODIFIER_DRAW_6,
            MODIFIER_DRAW_7,
            MODIFIER_PRECISION_DRAW,
            MODIFIER_PRECISION_DRAW_PLUS,
            MODIFIER_PRIME_DRAW,
            MODIFIER_HEX_DRAW,
            MODIFIER_DARK_BARGAIN,
        ):
            self.play_sound(SOUND_MOD_DRAW, volume=75)
            return
        if modifier in TARGET_VALUE_MODIFIERS:
            self._play_target_change_sound(modifier)
            return
        if modifier in (
            MODIFIER_REDRAFT,
            MODIFIER_REDRAFT_PLUS,
            MODIFIER_SHARED_CACHE,
            MODIFIER_ARCANE_CACHE,
        ):
            self.play_sound(SOUND_MOD_REFRESH, volume=75)
            return
        if modifier in (
            MODIFIER_SCRAP,
            MODIFIER_RECYCLE,
            MODIFIER_SWAP_DRAW,
            MODIFIER_BREAK,
            MODIFIER_BREAK_PLUS,
            MODIFIER_LOCKDOWN,
            MODIFIER_AID_RIVAL,
        ):
            self.play_sound(SOUND_MOD_CONTROL, volume=75)
            return
        self.play_sound(SOUND_PLAY_CHANGE_CARD, volume=75)

    def _play_target_change_sound(self, modifier: str) -> None:
        if modifier == MODIFIER_TARGET_17:
            self.play_sound(SOUND_TARGET_17, volume=75)
            return
        if modifier == MODIFIER_TARGET_24:
            self.play_sound(SOUND_TARGET_24, volume=75)
            return
        if modifier == MODIFIER_TARGET_27:
            self.play_sound(SOUND_TARGET_27, volume=75)
            return
        self.play_sound(SOUND_TARGET_17, volume=75)

    def _play_target_reminder_sound(self, player: TwentyOnePlayer) -> None:
        target = self._current_target()
        if target == 21:
            return
        if target == 17:
            self._play_sound_for_player(player, SOUND_TARGET_17, volume=60)
            return
        if target == 24:
            self._play_sound_for_player(player, SOUND_TARGET_24, volume=60)
            return
        if target == 27:
            self._play_sound_for_player(player, SOUND_TARGET_27, volume=60)

    def _play_bet_change_sounds(
        self,
        player: TwentyOnePlayer,
        opponent: TwentyOnePlayer,
        my_bet_before: int,
        opp_bet_before: int,
    ) -> None:
        my_bet_after = self._current_bet(player)
        opp_bet_after = self._current_bet(opponent)

        if my_bet_after > my_bet_before:
            self._play_sound_for_player(player, SOUND_BET_UP, volume=70)
        elif my_bet_after < my_bet_before:
            self._play_sound_for_player(player, SOUND_BET_DOWN, volume=70)

        if opp_bet_after > opp_bet_before:
            self._play_sound_for_player(opponent, SOUND_BET_UP, volume=70)
        elif opp_bet_after < opp_bet_before:
            self._play_sound_for_player(opponent, SOUND_BET_DOWN, volume=70)

    def _play_near_bust_sounds(self, player: TwentyOnePlayer) -> None:
        total = self._hand_total(player)
        target = self._current_target()
        if total != target:
            return

        self._play_sound_for_player(player, SOUND_NEAR_BUST, volume=65)

    def bot_think(self, player: TwentyOnePlayer) -> str | None:
        return compute_bot_think(self, player)

    @staticmethod
    def _bot_choose_hit_or_stand(
        opponent: TwentyOnePlayer,
        total: int,
        opp_total: float,
        target: int,
    ) -> str:
        if total < target - 2:
            return "hit"
        if opponent.stand_pending and total < opp_total and total <= target:
            return "hit"
        return "stand"

    def _bot_choose_modifier_to_play(self, player: TwentyOnePlayer) -> str | None:
        playable = self._playable_modifiers(player)
        if not playable:
            return None

        opponent = self._opponent_of(player)
        if not opponent:
            return playable[0]

        target = self._current_target()
        total = self._hand_total(player)
        estimated_opp_total = self._bot_estimate_opponent_total(player, opponent)
        likely_losing = self._bot_is_likely_losing(
            player, opponent, total, estimated_opp_total, target
        )
        confident_winning = self._bot_is_confident_winning(
            player, opponent, total, estimated_opp_total, target
        )
        needs_new_cards = self._bot_needs_new_change_cards(
            player, playable, likely_losing, confident_winning
        )

        best_modifier: str | None = None
        best_score = 0.0
        for modifier in playable:
            score = self._bot_modifier_score(
                player,
                opponent,
                modifier,
                total,
                target,
                likely_losing=likely_losing,
                confident_winning=confident_winning,
                needs_new_cards=needs_new_cards,
            )
            if score > best_score:
                best_score = score
                best_modifier = modifier
        return best_modifier

    def _bot_estimate_opponent_total(
        self, player: TwentyOnePlayer, opponent: TwentyOnePlayer
    ) -> float:
        visible_cards = self._opponent_visible_cards(opponent)
        visible_total = float(sum(card.rank for card in visible_cards))
        if not opponent.hand:
            return visible_total
        return visible_total + self._bot_expected_hidden_rank(player, opponent)

    def _bot_expected_hidden_rank(
        self, player: TwentyOnePlayer, opponent: TwentyOnePlayer
    ) -> float:
        counts = {rank: max(0, self.options.deck_count) for rank in range(1, 12)}
        for card in player.hand:
            if counts.get(card.rank, 0) > 0:
                counts[card.rank] -= 1
        for card in self._opponent_visible_cards(opponent):
            if counts.get(card.rank, 0) > 0:
                counts[card.rank] -= 1

        remaining = sum(counts.values())
        if remaining <= 0:
            return 6.0
        weighted = sum(rank * count for rank, count in counts.items())
        return weighted / remaining

    def _bot_is_likely_losing(
        self,
        player: TwentyOnePlayer,
        opponent: TwentyOnePlayer,
        total: int,
        estimated_opp_total: float,
        target: int,
    ) -> bool:
        if total > target:
            return True
        if opponent.stand_pending and estimated_opp_total > total:
            return True
        if total + 1.0 < estimated_opp_total:
            return True
        return player.hp <= opponent.hp and total < target - 3

    @staticmethod
    def _bot_is_confident_winning(
        player: TwentyOnePlayer,
        opponent: TwentyOnePlayer,
        total: int,
        estimated_opp_total: float,
        target: int,
    ) -> bool:
        if total > target:
            return False
        if opponent.stand_pending:
            return total >= estimated_opp_total
        if total >= target - 1 and total >= estimated_opp_total + 1:
            return True
        return player.hp > opponent.hp and total >= estimated_opp_total + 2

    def _bot_needs_new_change_cards(
        self,
        player: TwentyOnePlayer,
        playable: list[str],
        likely_losing: bool,
        confident_winning: bool,
    ) -> bool:
        non_redraft = [m for m in playable if m not in (MODIFIER_REDRAFT, MODIFIER_REDRAFT_PLUS)]
        if not non_redraft:
            return True
        if len(non_redraft) == 1 and likely_losing:
            return True
        if likely_losing and not any(
            self._bot_has_immediate_round_impact(player, m, confident_winning=confident_winning)
            for m in non_redraft
        ):
            return True
        return False

    def _bot_has_immediate_round_impact(
        self,
        player: TwentyOnePlayer,
        modifier: str,
        *,
        confident_winning: bool,
    ) -> bool:
        if modifier in (
            MODIFIER_PRECISION_DRAW,
            MODIFIER_PRECISION_DRAW_PLUS,
            MODIFIER_PRIME_DRAW,
            MODIFIER_DRAW_2,
            MODIFIER_DRAW_3,
            MODIFIER_DRAW_4,
            MODIFIER_DRAW_5,
            MODIFIER_DRAW_6,
            MODIFIER_DRAW_7,
            MODIFIER_GUARD,
            MODIFIER_GUARD_PLUS,
            MODIFIER_TARGET_24,
            MODIFIER_TARGET_27,
            MODIFIER_BREAK,
            MODIFIER_BREAK_PLUS,
            MODIFIER_SWAP_DRAW,
            MODIFIER_SCRAP,
            MODIFIER_RECYCLE,
            MODIFIER_BREAK_SHIELDS,
            MODIFIER_BREAK_SHIELDS_PLUS,
            MODIFIER_SHARED_CACHE,
            MODIFIER_HAND_TAX,
            MODIFIER_HAND_TAX_PLUS,
            MODIFIER_MIND_TAX,
            MODIFIER_MIND_TAX_PLUS,
            MODIFIER_ARCANE_CACHE,
            MODIFIER_HEX_DRAW,
            MODIFIER_DARK_BARGAIN,
            MODIFIER_ESCAPE_ROUTE,
            MODIFIER_EXACT_21_SURGE,
            MODIFIER_ROUND_ERASE,
            MODIFIER_DRAW_SILENCE,
            MODIFIER_ALL_IN_SILENCE,
        ):
            return True
        if modifier in (MODIFIER_RAISE_1, MODIFIER_RAISE_2, MODIFIER_RAISE_2_PLUS):
            return confident_winning
        return False

    def _bot_modifier_score(
        self,
        player: TwentyOnePlayer,
        opponent: TwentyOnePlayer,
        modifier: str,
        total: int,
        target: int,
        *,
        likely_losing: bool,
        confident_winning: bool,
        needs_new_cards: bool,
    ) -> float:
        gap = target - total
        opponent_last = self._peek_last_drawn_card(opponent)
        own_last = self._peek_last_drawn_card(player)

        if modifier == MODIFIER_REDRAFT:
            return 7.0 if needs_new_cards else -8.0
        if modifier == MODIFIER_REDRAFT_PLUS:
            return 8.0 if needs_new_cards else -8.0

        if modifier == MODIFIER_GUARD:
            return 9.0 if likely_losing else -3.0
        if modifier == MODIFIER_GUARD_PLUS:
            return 10.0 if likely_losing else -3.0

        if modifier == MODIFIER_RAISE_1:
            return 6.0 if confident_winning else -4.0
        if modifier == MODIFIER_RAISE_2:
            return 7.0 if confident_winning else -4.0
        if modifier == MODIFIER_RAISE_2_PLUS:
            return 8.0 if confident_winning else -4.0

        if modifier == MODIFIER_PRECISION_DRAW:
            return 8.0 if gap > 0 else -4.0
        if modifier == MODIFIER_PRECISION_DRAW_PLUS:
            if gap > 0:
                return 8.5
            return 6.0 if confident_winning else -3.0
        if modifier == MODIFIER_PRIME_DRAW:
            return 7.5 if gap > 0 else -4.0

        if modifier in (
            MODIFIER_DRAW_2,
            MODIFIER_DRAW_3,
            MODIFIER_DRAW_4,
            MODIFIER_DRAW_5,
            MODIFIER_DRAW_6,
            MODIFIER_DRAW_7,
        ):
            rank = int(modifier.split("_")[1])
            if gap <= 0:
                return -6.0
            if rank > gap:
                return -5.0
            closeness = 1.0 if rank == gap else 0.0
            return 6.0 + closeness

        if modifier == MODIFIER_TARGET_24:
            return 9.0 if total > target else -5.0
        if modifier == MODIFIER_TARGET_27:
            return 9.5 if total > target + 2 else -6.0
        if modifier == MODIFIER_TARGET_17:
            return 3.0 if confident_winning and total >= 17 else -6.0

        if modifier == MODIFIER_SCRAP:
            if opponent_last and likely_losing:
                return 6.0 + (opponent_last.rank / 20.0)
            return -2.0
        if modifier == MODIFIER_RECYCLE:
            if own_last and total > target:
                return 8.0
            return -3.0
        if modifier == MODIFIER_SWAP_DRAW:
            if own_last and opponent_last and opponent_last.rank > own_last.rank and likely_losing:
                return 7.0
            return -3.0

        if modifier == MODIFIER_BREAK:
            return 6.5 if likely_losing and opponent.table_modifiers else -2.0
        if modifier == MODIFIER_BREAK_PLUS:
            return 7.0 if likely_losing and opponent.table_modifiers else -2.0
        if modifier == MODIFIER_LOCKDOWN:
            if likely_losing and opponent.modifiers:
                return 7.5
            return 4.0 if confident_winning and opponent.modifiers else -2.0

        if modifier == MODIFIER_BREAK_SHIELDS:
            return 7.0 if confident_winning else -3.0
        if modifier == MODIFIER_BREAK_SHIELDS_PLUS:
            return 8.0 if confident_winning else -3.0
        if modifier == MODIFIER_SHARED_CACHE:
            return 2.0 if likely_losing else -3.0
        if modifier == MODIFIER_HAND_TAX:
            return 7.0 if confident_winning else -3.0
        if modifier == MODIFIER_HAND_TAX_PLUS:
            return 8.0 if confident_winning else -3.0
        if modifier == MODIFIER_MIND_TAX:
            return 6.5 if likely_losing else -2.0
        if modifier == MODIFIER_MIND_TAX_PLUS:
            return 7.0 if likely_losing else -2.0
        if modifier == MODIFIER_ARCANE_CACHE:
            return 7.5 if needs_new_cards else -2.0
        if modifier == MODIFIER_HEX_DRAW:
            return -8.0
        if modifier == MODIFIER_DARK_BARGAIN:
            return 8.0 if confident_winning else -5.0
        if modifier == MODIFIER_ESCAPE_ROUTE:
            return 6.0 if likely_losing else -1.0
        if modifier == MODIFIER_EXACT_21_SURGE:
            return 9.0 if total == 21 else -4.0
        if modifier == MODIFIER_ROUND_ERASE:
            return 8.0 if likely_losing else -8.0
        if modifier == MODIFIER_DRAW_SILENCE:
            return 6.0 if confident_winning else -1.0
        if modifier == MODIFIER_ALL_IN_SILENCE:
            return 9.0 if confident_winning else -9.0

        if modifier == MODIFIER_SALVAGE:
            return 2.0 if likely_losing else -2.0
        if modifier == MODIFIER_AID_RIVAL:
            return -20.0
        return -1.0

    def _resolve_modifier(
        self,
        player: TwentyOnePlayer,
        modifier: str,
        target: TwentyOnePlayer | None = None,
    ) -> None:
        # `target` is the opponent the actor chose for this card. Defaults to the
        # first opponent so 2-player games (and callers that don't pick) behave
        # exactly as before.
        opponent = target if target is not None else self._opponent_of(player)
        if not opponent:
            return

        if modifier == MODIFIER_RAISE_1:
            self._place_table_effect(player, modifier, target=opponent)
            self._give_random_modifiers(player, 1, announce=True)
            return

        if modifier == MODIFIER_RAISE_2:
            self._place_table_effect(player, modifier, target=opponent)
            self._give_random_modifiers(player, 1, announce=True)
            return

        if modifier == MODIFIER_RAISE_2_PLUS:
            self._place_table_effect(player, modifier, target=opponent)
            removed = self._extract_last_drawn_card(opponent)
            if removed:
                self._return_card_to_top_of_deck(removed)
                self._broadcast_personal_l(
                    opponent,
                    "twentyone-your-last-face-up-returned",
                    "twentyone-player-last-face-up-returned",
                )
            self._give_random_modifiers(player, 1, announce=True)
            return

        if modifier == MODIFIER_BREAK_SHIELDS:
            removed_count = self._remove_guard_effects(player, limit=3)
            if removed_count > 0:
                self._broadcast_personal_l(
                    player,
                    "twentyone-you-remove-defend-effects",
                    "twentyone-player-removes-defend-effects",
                    count=removed_count,
                )
            self._place_table_effect(player, modifier, target=opponent)
            return

        if modifier == MODIFIER_BREAK_SHIELDS_PLUS:
            removed_count = self._remove_guard_effects(player, limit=2)
            if removed_count > 0:
                self._broadcast_personal_l(
                    player,
                    "twentyone-you-remove-defend-effects",
                    "twentyone-player-removes-defend-effects",
                    count=removed_count,
                )
            self._place_table_effect(player, modifier, target=opponent)
            return

        if modifier == MODIFIER_SHARED_CACHE:
            self._give_random_modifiers(player, 1, announce=True)
            self._give_random_modifiers(opponent, 1, announce=True)
            return

        if modifier in (
            MODIFIER_DRAW_2,
            MODIFIER_DRAW_3,
            MODIFIER_DRAW_4,
            MODIFIER_DRAW_5,
            MODIFIER_DRAW_6,
            MODIFIER_DRAW_7,
        ):
            if self._draws_locked_for(player):
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self._announce_draw_locked(player)
                return
            rank = int(modifier.split("_")[1])
            card = self._draw_specific_rank(rank)
            if card:
                self._add_card_to_hand(
                    player,
                    card,
                    announcement=(
                        "twentyone-you-draw-card-from",
                        "twentyone-player-draws-card-from",
                        lambda locale: {
                            "card": self._render_card(locale, card),
                            "modifier": self._render_modifier(locale, modifier),
                        },
                    ),
                    reveal_to_others=True,
                )
                player.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-no-rank-card", rank=rank, buffer="game")
            return

        if modifier == MODIFIER_SCRAP:
            removed = self._extract_last_drawn_card(opponent)
            if removed:
                self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
                self._return_card_to_top_of_deck(removed)
                self._broadcast_personal_l(
                    opponent,
                    "twentyone-your-last-face-up-returned",
                    "twentyone-player-last-face-up-returned",
                )
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-no-face-up-remove", buffer="game")
            return

        if modifier == MODIFIER_RECYCLE:
            removed = self._extract_last_drawn_card(player)
            if removed:
                self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
                self._return_card_to_top_of_deck(removed)
                self._broadcast_personal_l(
                    player,
                    "twentyone-your-last-face-up-returned",
                    "twentyone-player-last-face-up-returned",
                )
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-no-face-up-return", buffer="game")
            return

        if modifier == MODIFIER_SWAP_DRAW:
            player_recent = self._peek_last_drawn_card(player)
            opponent_recent = self._peek_last_drawn_card(opponent)
            if not player_recent or not opponent_recent:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-exchange-needs-face-up", buffer="game")
                return

            first = self._extract_last_drawn_card(player)
            second = self._extract_last_drawn_card(opponent)
            if not first or not second:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-exchange-failed", buffer="game")
                return

            player.hand.append(second)
            player.last_drawn_card_id = second.id
            opponent.hand.append(first)
            opponent.last_drawn_card_id = first.id
            player.stand_pending = False
            opponent.stand_pending = False
            self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
            self.broadcast_l("twentyone-exchange-resolves", buffer="game")
            return

        if modifier == MODIFIER_REDRAFT:
            self._discard_random_modifiers(player, 2, announce_sound=True)
            self._give_random_modifiers(player, 3, announce=True)
            return

        if modifier == MODIFIER_REDRAFT_PLUS:
            self._discard_random_modifiers(player, 1, announce_sound=True)
            self._give_random_modifiers(player, 4, announce=True)
            return

        if modifier == MODIFIER_ARCANE_CACHE:
            self._place_table_effect(player, modifier, target=opponent)
            self._give_random_modifiers(player, 3, announce=True)
            return

        if modifier == MODIFIER_HEX_DRAW:
            self._discard_random_modifiers(player, 1, announce_sound=True)
            if self._draws_locked_for(opponent):
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self._announce_draw_locked(opponent)
                return
            card = self._draw_highest_card()
            if card:
                self._add_card_to_hand(
                    opponent,
                    card,
                    announcement=(
                        "twentyone-you-draw-card-from",
                        "twentyone-player-draws-card-from",
                        lambda locale: {
                            "card": self._render_card(locale, card),
                            "modifier": self._render_modifier(locale, MODIFIER_HEX_DRAW),
                        },
                    ),
                    reveal_to_others=True,
                )
                opponent.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self._broadcast_l_with_locale_args(
                    "twentyone-modifier-found-no-card",
                    lambda locale: {
                        "modifier": self._render_modifier(locale, MODIFIER_HEX_DRAW)
                    },
                )
            return

        if modifier == MODIFIER_DARK_BARGAIN:
            self._place_table_effect(player, modifier, target=opponent)
            discard_count = len(player.modifiers) // 2
            self._discard_random_modifiers(player, discard_count, announce_sound=True)
            if self._draws_locked_for(player):
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self._announce_draw_locked(player)
                return
            card = self._draw_best_possible_card(player)
            if card:
                self._add_card_to_hand(
                    player,
                    card,
                    announcement=(
                        "twentyone-you-draw-card-from",
                        "twentyone-player-draws-card-from",
                        lambda locale: {
                            "card": self._render_card(locale, card),
                            "modifier": self._render_modifier(locale, MODIFIER_DARK_BARGAIN),
                        },
                    ),
                    reveal_to_others=True,
                )
                player.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self._broadcast_l_with_locale_args(
                    "twentyone-modifier-found-no-card",
                    lambda locale: {
                        "modifier": self._render_modifier(locale, MODIFIER_DARK_BARGAIN)
                    },
                )
            return

        if modifier == MODIFIER_ROUND_ERASE:
            self.phase = "between_rounds"
            self.next_round_wait_ticks = 0
            self._clear_pending_round_resolution()
            self.broadcast_l("twentyone-round-erased", buffer="game")
            return

        if modifier in TABLE_EFFECT_MODIFIERS:
            self._place_table_effect(player, modifier, target=opponent)
            if modifier in TARGET_VALUE_MODIFIERS:
                self.broadcast_l("twentyone-target-changed", target=self._current_target(), buffer="game")
            return

        if modifier == MODIFIER_BREAK:
            removed = self._pop_last_table_effect(opponent)
            if removed:
                self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
                if removed == MODIFIER_LOCKDOWN:
                    self.play_sound(SOUND_LOCKDOWN_END, volume=70)
                self._broadcast_personal_l_with_locale_args(
                    player,
                    "twentyone-you-destroy-effect",
                    "twentyone-player-destroys-effect",
                    lambda locale: {"effect": self._render_modifier(locale, removed)},
                )
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-no-effect-destroy", buffer="game")
            return

        if modifier == MODIFIER_BREAK_PLUS:
            if opponent.table_modifiers:
                count = len(opponent.table_modifiers)
                had_lockdown = MODIFIER_LOCKDOWN in opponent.table_modifiers
                self._clear_table_effects(opponent)
                self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
                if had_lockdown:
                    self.play_sound(SOUND_LOCKDOWN_END, volume=70)
                self._broadcast_personal_l(
                    player,
                    "twentyone-you-destroy-all-effects",
                    "twentyone-player-destroys-all-effects",
                    count=count,
                )
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-no-effects-destroy", buffer="game")
            return

        if modifier == MODIFIER_LOCKDOWN:
            if opponent.table_modifiers:
                self._clear_table_effects(opponent)
                self._broadcast_personal_l(
                    player,
                    "twentyone-you-clear-effects",
                    "twentyone-player-clears-effects",
                )
            self._place_table_effect(player, modifier, target=opponent)
            self.play_sound(SOUND_LOCKDOWN_APPLY, volume=75)
            return

        if modifier == MODIFIER_PRECISION_DRAW:
            if self._draws_locked_for(player):
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self._announce_draw_locked(player)
                return
            card = self._draw_best_possible_card(player)
            if card:
                self._add_card_to_hand(
                    player,
                    card,
                    announcement=(
                        "twentyone-you-draw-card-from",
                        "twentyone-player-draws-card-from",
                        lambda locale: {
                            "card": self._render_card(locale, card),
                            "modifier": self._render_modifier(locale, MODIFIER_PRECISION_DRAW),
                        },
                    ),
                    reveal_to_others=True,
                )
                player.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-precision-draw-none", buffer="game")
            return

        if modifier == MODIFIER_PRECISION_DRAW_PLUS:
            self._place_table_effect(player, modifier, target=opponent)
            if self._draws_locked_for(player):
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self._announce_draw_locked(player)
                return
            card = self._draw_best_possible_card(player)
            if card:
                self._add_card_to_hand(
                    player,
                    card,
                    announcement=(
                        "twentyone-you-draw-card-from",
                        "twentyone-player-draws-card-from",
                        lambda locale: {
                            "card": self._render_card(locale, card),
                            "modifier": self._render_modifier(
                                locale, MODIFIER_PRECISION_DRAW_PLUS
                            ),
                        },
                    ),
                    reveal_to_others=True,
                )
                player.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-precision-draw-plus-none", buffer="game")
            return

        if modifier == MODIFIER_PRIME_DRAW:
            if self._draws_locked_for(player):
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self._announce_draw_locked(player)
                return
            card = self._draw_best_possible_card(player)
            if card:
                self._add_card_to_hand(
                    player,
                    card,
                    announcement=(
                        "twentyone-you-draw-card-from",
                        "twentyone-player-draws-card-from",
                        lambda locale: {
                            "card": self._render_card(locale, card),
                            "modifier": self._render_modifier(locale, MODIFIER_PRIME_DRAW),
                        },
                    ),
                    reveal_to_others=True,
                )
                player.stand_pending = False
            self._give_random_modifiers(player, 2, announce=True)
            return

        if modifier in TARGET_VALUE_MODIFIERS:
            self._place_table_effect(player, modifier, target=opponent)
            self.broadcast_l("twentyone-target-changed", target=self._current_target(), buffer="game")
            return

        if modifier == MODIFIER_SALVAGE:
            self._place_table_effect(player, modifier, target=opponent)
            return

        if modifier == MODIFIER_AID_RIVAL:
            if self._draws_locked_for(opponent):
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self._announce_draw_locked(opponent)
                return
            card = self._draw_best_possible_card(opponent)
            if card:
                self._add_card_to_hand(
                    opponent,
                    card,
                    announcement=(
                        "twentyone-you-draw-card-from",
                        "twentyone-player-draws-card-from",
                        lambda locale: {
                            "card": self._render_card(locale, card),
                            "modifier": self._render_modifier(locale, MODIFIER_AID_RIVAL),
                        },
                    ),
                    reveal_to_others=True,
                )
                opponent.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast_l("twentyone-aid-rival-none", buffer="game")

    def _alive_players(self) -> list[TwentyOnePlayer]:
        return [p for p in self.get_active_players() if isinstance(p, TwentyOnePlayer) and p.hp > 0]

    def _opponent_of(self, player: TwentyOnePlayer) -> TwentyOnePlayer | None:
        for other in self._alive_players():
            if other.id != player.id:
                return other
        return None

    def _opponents_of(self, player: TwentyOnePlayer) -> list[TwentyOnePlayer]:
        return [other for other in self._alive_players() if other.id != player.id]

    def _both_players_standing(self) -> bool:
        players = self._alive_players()
        if len(players) < 2:
            return False
        return all(p.stand_pending for p in players)

    def _clear_pending_stands(self) -> None:
        players = self._alive_players()
        if not any(p.stand_pending for p in players):
            return
        for p in players:
            p.stand_pending = False

    def _hand_total(self, player: TwentyOnePlayer) -> int:
        return sum(card.rank for card in player.hand)

    @staticmethod
    def _opponent_visible_cards(player: TwentyOnePlayer) -> list[Card]:
        if len(player.hand) <= 1:
            return []
        return player.hand[1:]

    def _current_target(self) -> int:
        for player in self._alive_players():
            for modifier in reversed(player.table_modifiers):
                if modifier in TARGET_VALUE_MODIFIERS:
                    return TARGET_VALUE_MODIFIERS[modifier]
        return 21

    def _current_bet(self, player: TwentyOnePlayer) -> int:
        base = max(0, self.options.base_bet)
        opponents = self._opponents_of(player)
        if not opponents:
            return base

        # Sum every opponent's raise/tax effects that are aimed at this player.
        increase = 0
        for opponent in opponents:
            for modifier, target_id in self._table_effect_pairs(opponent):
                # None target = legacy/untargeted effect that hits any opponent.
                if target_id is not None and target_id != player.id:
                    continue
                if modifier == MODIFIER_RAISE_1:
                    increase += 1
                elif modifier == MODIFIER_RAISE_2:
                    increase += 2
                elif modifier == MODIFIER_RAISE_2_PLUS:
                    increase += 2
                elif modifier == MODIFIER_PRECISION_DRAW_PLUS:
                    increase += 5
                elif modifier == MODIFIER_BREAK_SHIELDS:
                    increase += 3
                elif modifier == MODIFIER_BREAK_SHIELDS_PLUS:
                    increase += 5
                elif modifier == MODIFIER_HAND_TAX:
                    increase += len(player.modifiers) // 2
                elif modifier == MODIFIER_HAND_TAX_PLUS:
                    increase += len(player.modifiers)
                elif modifier == MODIFIER_DARK_BARGAIN:
                    increase += 10
                elif modifier == MODIFIER_EXACT_21_SURGE and self._hand_total(opponent) == 21:
                    increase += 21

        reduction = 0
        self_penalty = 0
        for modifier in player.table_modifiers:
            if modifier == MODIFIER_GUARD:
                reduction += 1
            elif modifier == MODIFIER_GUARD_PLUS:
                reduction += 2
            elif modifier == MODIFIER_ARCANE_CACHE:
                self_penalty += 1

        # "game over" is global pressure on everyone but its owner.
        global_pressure = 0
        for participant in self._alive_players():
            if participant.id == player.id:
                continue
            global_pressure += participant.table_modifiers.count(MODIFIER_ALL_IN_SILENCE) * 100

        return max(0, base + increase - reduction + self_penalty + global_pressure)

    def _modifiers_locked_for(self, player: TwentyOnePlayer) -> bool:
        return any(
            self._has_effect_targeting(opponent, MODIFIER_LOCKDOWN, player)
            for opponent in self._opponents_of(player)
        )

    def _playable_modifiers(self, player: TwentyOnePlayer) -> list[str]:
        return [
            modifier
            for modifier in player.modifiers
            if self._is_single_modifier_playable(player, modifier)
        ]

    def _is_single_modifier_playable(self, player: TwentyOnePlayer, modifier: str) -> bool:
        return self._modifier_unplayable_reason(player, modifier, "en") is None

    def _modifier_unplayable_reason(
        self, player: TwentyOnePlayer, modifier: str, locale: str
    ) -> str | None:
        if self._modifiers_locked_for(player):
            return Localization.get(
                locale,
                "twentyone-unplayable-change-cards-locked",
                effect=self._render_modifier(locale, MODIFIER_LOCKDOWN),
            )
        if modifier not in MODIFIER_POOL:
            return Localization.get(locale, "twentyone-unplayable-unknown-change-card")

        opponent = self._opponent_of(player)

        if modifier in SELF_DRAW_MODIFIERS:
            if self._draws_locked_for(player):
                return Localization.get(locale, "twentyone-unplayable-self-draw-locked")
            if not self.deck or self.deck.is_empty():
                return Localization.get(locale, "twentyone-unplayable-empty-deck")
            if modifier in EXACT_DRAW_MODIFIERS:
                rank = int(modifier.split("_")[1])
                if not self._deck_has_rank(rank):
                    return Localization.get(
                        locale, "twentyone-unplayable-rank-missing", rank=rank
                    )
            if modifier in TABLE_EFFECT_MODIFIERS and len(player.table_modifiers) >= TABLE_EFFECT_LIMIT:
                return Localization.get(
                    locale, "twentyone-unplayable-table-full", limit=TABLE_EFFECT_LIMIT
                )

        if modifier in OPPONENT_DRAW_MODIFIERS:
            if not opponent:
                return Localization.get(locale, "twentyone-unplayable-no-opponent")
            if self._draws_locked_for(opponent):
                return Localization.get(locale, "twentyone-unplayable-target-draw-locked")
            if not self.deck or self.deck.is_empty():
                return Localization.get(locale, "twentyone-unplayable-empty-deck")

        if modifier == MODIFIER_BREAK_SHIELDS:
            count = self._count_defense_effects(player)
            if count < 3:
                return Localization.get(
                    locale,
                    "twentyone-unplayable-need-defend-effects",
                    required=3,
                    count=count,
                )
            if len(player.table_modifiers) >= TABLE_EFFECT_LIMIT:
                return Localization.get(
                    locale, "twentyone-unplayable-table-full", limit=TABLE_EFFECT_LIMIT
                )
            return None
        if modifier == MODIFIER_BREAK_SHIELDS_PLUS:
            count = self._count_defense_effects(player)
            if count < 2:
                return Localization.get(
                    locale,
                    "twentyone-unplayable-need-defend-effects",
                    required=2,
                    count=count,
                )
            if len(player.table_modifiers) >= TABLE_EFFECT_LIMIT:
                return Localization.get(
                    locale, "twentyone-unplayable-table-full", limit=TABLE_EFFECT_LIMIT
                )
            return None
        if modifier == MODIFIER_DARK_BARGAIN and len(player.modifiers) < 3:
            # Requires at least two additional change cards so half-discard is meaningful.
            return Localization.get(locale, "twentyone-unplayable-dark-bargain-cost")

        if modifier in TABLE_EFFECT_MODIFIERS:
            if modifier in TARGET_VALUE_MODIFIERS:
                target = TARGET_VALUE_MODIFIERS[modifier]
                if target == self._current_target():
                    return Localization.get(
                        locale, "twentyone-unplayable-target-already-active", target=target
                    )
                return None
            if len(player.table_modifiers) >= TABLE_EFFECT_LIMIT:
                return Localization.get(
                    locale, "twentyone-unplayable-table-full", limit=TABLE_EFFECT_LIMIT
                )
            return None

        if not opponent:
            return Localization.get(locale, "twentyone-unplayable-no-opponent")

        if modifier == MODIFIER_SCRAP:
            if self._peek_last_drawn_card(opponent) is None:
                return Localization.get(locale, "twentyone-unplayable-no-opponent-face-up")
            return None
        if modifier == MODIFIER_RECYCLE:
            if self._peek_last_drawn_card(player) is None:
                return Localization.get(locale, "twentyone-unplayable-no-own-face-up")
            return None
        if modifier == MODIFIER_SWAP_DRAW:
            has_own = self._peek_last_drawn_card(player) is not None
            has_opponent = self._peek_last_drawn_card(opponent) is not None
            if not has_own and not has_opponent:
                return Localization.get(locale, "twentyone-unplayable-swap-needs-both")
            if not has_own:
                return Localization.get(locale, "twentyone-unplayable-swap-needs-yours")
            if not has_opponent:
                return Localization.get(locale, "twentyone-unplayable-swap-needs-opponent")
            return None
        if modifier == MODIFIER_BREAK:
            if not opponent.table_modifiers:
                return Localization.get(locale, "twentyone-unplayable-no-opponent-effects")
            return None
        if modifier == MODIFIER_BREAK_PLUS:
            if not opponent.table_modifiers:
                return Localization.get(locale, "twentyone-unplayable-no-opponent-effects")
            return None
        if modifier == MODIFIER_HEX_DRAW:
            # Requires one additional change card to pay the discard cost.
            if len(player.modifiers) < 2:
                return Localization.get(locale, "twentyone-unplayable-hex-cost")
            return None
        return None

    def _speak_unplayable_modifier(self, player: TwentyOnePlayer, modifier: str) -> None:
        locale = self._player_locale(player)
        reason = self._modifier_unplayable_reason(player, modifier, locale)
        if not reason:
            return
        self._speak_private_l(
            player,
            "twentyone-change-card-not-playable",
            card=self._render_modifier(locale, modifier),
            reason=reason,
        )

    def _place_table_effect(
        self,
        player: TwentyOnePlayer,
        modifier: str,
        target: TwentyOnePlayer | None = None,
    ) -> None:
        if modifier in TARGET_VALUE_MODIFIERS:
            for p in self._alive_players():
                self._set_table_modifiers(
                    p,
                    [
                        (mod, tid)
                        for mod, tid in self._table_effect_pairs(p)
                        if mod not in TARGET_VALUE_MODIFIERS
                    ],
                )

        # Only targeted effects remember a victim; self / table-wide effects
        # always store None even if a target is passed in.
        target_id = (
            target.id if (target is not None and modifier in TARGETED_TABLE_EFFECTS) else None
        )
        player.table_modifiers.append(modifier)
        player.table_modifier_targets.append(target_id)
        while len(player.table_modifiers) > TABLE_EFFECT_LIMIT:
            removed = player.table_modifiers.pop(0)
            player.table_modifier_targets.pop(0)
            self.play_sound(SOUND_EFFECT_EXPIRE, volume=70)
            if removed == MODIFIER_LOCKDOWN:
                self.play_sound(SOUND_LOCKDOWN_END, volume=70)
            self._broadcast_personal_l_with_locale_args(
                player,
                "twentyone-your-effect-expires",
                "twentyone-player-effect-expires",
                lambda locale, removed=removed: {
                    "effect": self._render_modifier(locale, removed)
                },
            )

    @staticmethod
    def _table_effect_pairs(player: TwentyOnePlayer) -> list[tuple[str, str | None]]:
        """The table effects as (modifier, target_id) pairs, kept in sync."""
        targets = player.table_modifier_targets
        return [
            (mod, targets[i] if i < len(targets) else None)
            for i, mod in enumerate(player.table_modifiers)
        ]

    @staticmethod
    def _set_table_modifiers(
        player: TwentyOnePlayer, pairs: list[tuple[str, str | None]]
    ) -> None:
        player.table_modifiers = [mod for mod, _tid in pairs]
        player.table_modifier_targets = [tid for _mod, tid in pairs]

    def _clear_table_effects(self, player: TwentyOnePlayer) -> None:
        player.table_modifiers.clear()
        player.table_modifier_targets.clear()

    def _remove_table_effect_by_value(
        self, player: TwentyOnePlayer, modifier: str
    ) -> bool:
        """Remove the first instance of `modifier` and its paired target."""
        try:
            index = player.table_modifiers.index(modifier)
        except ValueError:
            return False
        player.table_modifiers.pop(index)
        if index < len(player.table_modifier_targets):
            player.table_modifier_targets.pop(index)
        return True

    def _pop_last_table_effect(self, player: TwentyOnePlayer) -> str | None:
        if not player.table_modifiers:
            return None
        if player.table_modifier_targets:
            player.table_modifier_targets.pop()
        return player.table_modifiers.pop()

    def _draw_lock_effect_for(self, player: TwentyOnePlayer) -> str | None:
        opponents = self._opponents_of(player)
        if not opponents:
            return None
        # "game over" locks everyone's draws; "no draw for you!" locks only its
        # chosen target.
        for opponent in opponents:
            if MODIFIER_ALL_IN_SILENCE in opponent.table_modifiers:
                return MODIFIER_ALL_IN_SILENCE
        for opponent in opponents:
            if self._has_effect_targeting(opponent, MODIFIER_DRAW_SILENCE, player):
                return MODIFIER_DRAW_SILENCE
        return None

    def _draws_locked_for(self, player: TwentyOnePlayer) -> bool:
        return self._draw_lock_effect_for(player) is not None

    def _announce_draw_locked(self, player: TwentyOnePlayer) -> None:
        effect = self._draw_lock_effect_for(player)
        if not effect:
            return
        self._broadcast_personal_l_with_locale_args(
            player,
            "twentyone-you-cannot-draw-effect",
            "twentyone-player-cannot-draw-effect",
            lambda locale: {"effect": self._render_modifier(locale, effect)},
        )

    def _remove_guard_effects(self, player: TwentyOnePlayer, *, limit: int) -> int:
        removed = 0
        retained: list[tuple[str, str | None]] = []
        for effect, target_id in self._table_effect_pairs(player):
            if effect in (MODIFIER_GUARD, MODIFIER_GUARD_PLUS) and removed < limit:
                removed += 1
                continue
            retained.append((effect, target_id))
        self._set_table_modifiers(player, retained)
        return removed

    @staticmethod
    def _count_defense_effects(player: TwentyOnePlayer) -> int:
        return sum(
            1
            for effect in player.table_modifiers
            if effect in (MODIFIER_GUARD, MODIFIER_GUARD_PLUS)
        )

    def _draw_highest_card(self) -> Card | None:
        if not self.deck or self.deck.is_empty():
            return None
        highest_index = max(
            range(len(self.deck.cards)), key=lambda index: self.deck.cards[index].rank
        )
        return self.deck.cards.pop(highest_index)

    def _handle_mind_tax_break(self, actor: TwentyOnePlayer) -> None:
        # A mind-tax breaks when the player it targets plays enough cards in a
        # turn. Find any opponent holding such an effect aimed at the actor.
        breaks = (
            (MODIFIER_MIND_TAX, 2),
            (MODIFIER_MIND_TAX_PLUS, 3),
        )
        for effect, threshold in breaks:
            if actor.turn_modifier_plays < threshold:
                continue
            for owner in self._opponents_of(actor):
                if not self._has_effect_targeting(owner, effect, actor):
                    continue
                self._remove_table_effect_by_value(owner, effect)
                self.play_sound(SOUND_EFFECT_EXPIRE, volume=70)
                self._broadcast_personal_l_with_locale_args(
                    owner,
                    "twentyone-your-effect-breaks",
                    "twentyone-player-effect-breaks",
                    lambda locale, effect=effect: {
                        "effect": self._render_modifier(locale, effect)
                    },
                )

    def _has_effect_targeting(
        self, owner: TwentyOnePlayer, modifier: str, target: TwentyOnePlayer
    ) -> bool:
        # A None target means the effect was placed without an explicit victim
        # (e.g. legacy two-player state); treat it as hitting any opponent.
        return any(
            mod == modifier and (tid == target.id or tid is None)
            for mod, tid in self._table_effect_pairs(owner)
        )

    def _apply_round_end_change_card_effects(
        self, players: list[TwentyOnePlayer]
    ) -> None:
        # Each owner's mind-tax effects apply to every other player. (Target
        # locking arrives in a later phase; until then these hit all opponents.)
        for owner in players:
            targets = [p for p in players if p.id != owner.id]
            for target in targets:
                if MODIFIER_MIND_TAX_PLUS in owner.table_modifiers and target.modifiers:
                    count = len(target.modifiers)
                    self._discard_random_modifiers(target, count, announce_sound=True)
                    self._broadcast_personal_l_with_locale_args(
                        target,
                        "twentyone-you-discard-all-change-cards",
                        "twentyone-player-discards-all-change-cards",
                        lambda locale, count=count: {
                            "count": count,
                            "effect": self._render_modifier(locale, MODIFIER_MIND_TAX_PLUS),
                        },
                    )
                    continue

                if MODIFIER_MIND_TAX in owner.table_modifiers and target.modifiers:
                    count = len(target.modifiers) // 2
                    if count > 0:
                        self._discard_random_modifiers(target, count, announce_sound=True)
                        self._broadcast_personal_l_with_locale_args(
                            target,
                            "twentyone-you-discard-change-cards",
                            "twentyone-player-discards-change-cards",
                            lambda locale, count=count: {
                                "count": count,
                                "effect": self._render_modifier(locale, MODIFIER_MIND_TAX),
                            },
                        )

    def _trigger_harvest_rewards(self) -> None:
        for player in self._alive_players():
            if MODIFIER_SALVAGE in player.table_modifiers:
                self._give_random_modifiers(player, 1, announce=True)

    def _build_round_deck(self) -> None:
        cards: list[Card] = []
        card_id = self.round_number * 1000
        deck_count = max(1, self.options.deck_count)
        for _ in range(deck_count):
            for rank in range(1, 12):
                cards.append(Card(id=card_id, rank=rank, suit=0))
                card_id += 1
        self.deck = Deck(cards=cards)
        self.deck.shuffle()

    def _draw_card(self) -> Card | None:
        if not self.deck:
            return None
        if self.deck.is_empty():
            return None
        return self.deck.draw_one()

    def _draw_specific_rank(self, rank: int) -> Card | None:
        if not self.deck:
            return None
        if self.deck.is_empty():
            return None

        for index, card in enumerate(self.deck.cards):
            if card.rank == rank:
                return self.deck.cards.pop(index)
        return None

    def _deck_has_rank(self, rank: int) -> bool:
        return bool(self.deck and any(card.rank == rank for card in self.deck.cards))

    def _draw_best_possible_card(self, player: TwentyOnePlayer) -> Card | None:
        if not self.deck:
            return None
        if not self.deck or self.deck.is_empty():
            return None

        target = self._current_target()
        current = self._hand_total(player)
        best_index = -1
        best_value = -1
        for index, card in enumerate(self.deck.cards):
            value = card.rank
            projected = current + value
            if projected <= target and value > best_value:
                best_value = value
                best_index = index

        if best_index >= 0:
            return self.deck.cards.pop(best_index)

        lowest_index = min(
            range(len(self.deck.cards)),
            key=lambda index: self.deck.cards[index].rank,
        )
        return self.deck.cards.pop(lowest_index)

    def _add_card_to_hand(
        self,
        player: TwentyOnePlayer,
        card: Card,
        *,
        announcement: CardAnnouncement | None,
        reveal_to_others: bool = True,
    ) -> None:
        player.hand.append(card)
        player.last_drawn_card_id = card.id if reveal_to_others else None
        if announcement:
            if reveal_to_others:
                personal_message_id, others_message_id, args_for_locale = announcement
                self._broadcast_personal_l_with_locale_args(
                    player,
                    personal_message_id,
                    others_message_id,
                    args_for_locale,
                )
            else:
                self._speak_private_l(
                    player,
                    "twentyone-player-receives-hidden-card-private",
                    rank=card.rank,
                )
                self.broadcast_l(
                    "twentyone-player-receives-hidden-card",
                    player=player.name,
                    exclude=player, buffer="game",
                )
            self._play_near_bust_sounds(player)

    def _speak_private_l(self, player: TwentyOnePlayer, message_id: str, **kwargs) -> None:
        locale = self._player_locale(player)
        localized = Localization.get(locale, message_id, **kwargs)
        if hasattr(self, "record_transcript_event"):
            self.record_transcript_event(player, localized, "game")
        user = self.get_user(player)
        if user:
            user.speak_l(message_id, buffer="game", **kwargs)

    def _return_card_to_top_of_deck(self, card: Card) -> None:
        if not self.deck:
            self.deck = Deck(cards=[card])
            return
        self.deck.add_top([card])

    def _peek_last_drawn_card(self, player: TwentyOnePlayer) -> Card | None:
        if player.last_drawn_card_id is None:
            return None
        for card in player.hand:
            if card.id == player.last_drawn_card_id:
                return card
        return None

    def _extract_last_drawn_card(self, player: TwentyOnePlayer) -> Card | None:
        card = self._peek_last_drawn_card(player)
        if not card:
            return None
        for index, hand_card in enumerate(player.hand):
            if hand_card.id == card.id:
                removed = player.hand.pop(index)
                player.last_drawn_card_id = None
                return removed
        return None

    def _give_random_modifiers(
        self, player: TwentyOnePlayer, count: int, *, announce: bool
    ) -> None:
        for _ in range(max(0, count)):
            modifier = self._draw_weighted_modifier()
            player.modifiers.append(modifier)
            if announce:
                self._play_sound_for_player(player, SOUND_GAIN_CHANGE_CARD, volume=70)
                self._speak_private_l(
                    player,
                    "twentyone-you-gain-change-card",
                    card=self._render_modifier(self._player_locale(player), modifier),
                )
                self.broadcast_l(
                    "twentyone-player-gains-change-card",
                    player=player.name,
                    exclude=player, buffer="game",
                )

    def _draw_weighted_modifier(self) -> str:
        weights = [MODIFIER_DRAW_WEIGHTS[modifier] for modifier in MODIFIER_POOL]
        return random.choices(MODIFIER_POOL, weights=weights, k=1)[0]  # nosec B311

    def _discard_random_modifiers(
        self,
        player: TwentyOnePlayer,
        count: int,
        *,
        announce_sound: bool = False,
    ) -> None:
        for _ in range(min(max(0, count), len(player.modifiers))):
            index = random.randrange(len(player.modifiers))  # nosec B311
            player.modifiers.pop(index)
            if announce_sound:
                self._play_sound_for_player(player, SOUND_LOSE_CHANGE_CARD, volume=70)

    def _sync_hp_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for player in self.players:
            if not isinstance(player, TwentyOnePlayer) or player.is_spectator:
                continue
            team = self._team_manager.get_team(player.name)
            if team:
                team.total_score = player.hp

    def build_game_result(self) -> GameResult:
        players = [p for p in self.players if isinstance(p, TwentyOnePlayer) and not p.is_spectator]
        winner = max(players, key=lambda p: p.hp, default=None)
        final_hp = {p.name: p.hp for p in players}

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
                for p in players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_hp": winner.hp if winner else 0,
                "final_hp": final_hp,
                "rounds_played": self.round_number,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_hp = result.custom_data.get("final_hp", {})
        sorted_hp = sorted(final_hp.items(), key=lambda item: item[1], reverse=True)
        for index, (name, hp) in enumerate(sorted_hp, 1):
            lines.append(
                Localization.get(locale, "twentyone-final-hp-line", rank=index, player=name, hp=hp)
            )
        return lines
