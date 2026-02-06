"""
Farkle Game Implementation for PlayAural v0.1.0.

Classic dice game: score combinations and don't Farkle!
Push your luck by rolling again or bank your points.
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


@dataclass
class FarklePlayer(Player):
    """Player state for Farkle game."""

    score: int = 0  # Permanent score (banked points)
    turn_score: int = 0  # Points accumulated this turn (lost on farkle)
    current_roll: list[int] = field(default_factory=list)  # Dice available to take
    banked_dice: list[int] = field(default_factory=list)  # Dice taken this turn
    has_taken_combo: bool = False  # True after taking a combo (enables roll)
    # Stats tracking
    turns_taken: int = 0  # Number of turns completed (for avg points per turn)
    best_turn: int = 0  # Highest points banked in a single turn


@dataclass
class FarkleOptions(GameOptions):
    """Options for Farkle game."""

    target_score: int = option_field(
        IntOption(
            default=500,
            min_val=500,
            max_val=5000,
            value_key="score",
            label="farkle-set-target-score",
            prompt="farkle-enter-target-score",
            change_msg="farkle-option-changed-target",
        )
    )


# Scoring combination types
COMBO_SINGLE_1 = "single_1"
COMBO_SINGLE_5 = "single_5"
COMBO_THREE_OF_KIND = "three_of_kind"
COMBO_FOUR_OF_KIND = "four_of_kind"
COMBO_FIVE_OF_KIND = "five_of_kind"
COMBO_SIX_OF_KIND = "six_of_kind"
COMBO_SMALL_STRAIGHT = "small_straight"
COMBO_LARGE_STRAIGHT = "large_straight"
COMBO_THREE_PAIRS = "three_pairs"
COMBO_DOUBLE_TRIPLETS = "double_triplets"
COMBO_FULL_HOUSE = "full_house"

# Combo sounds
COMBO_SOUNDS = {
    COMBO_SINGLE_1: "game_farkle/point10.ogg",
    COMBO_SINGLE_5: "game_farkle/singles5.ogg",
    COMBO_THREE_OF_KIND: "game_farkle/3kind.ogg",
    COMBO_FOUR_OF_KIND: "game_farkle/4kind.ogg",
    COMBO_FIVE_OF_KIND: "game_farkle/5kind.ogg",
    COMBO_SIX_OF_KIND: "game_farkle/6kind.ogg",
    COMBO_LARGE_STRAIGHT: "game_farkle/largestraight.ogg",
    COMBO_SMALL_STRAIGHT: "game_farkle/smallstraight.ogg",
    COMBO_THREE_PAIRS: "game_farkle/3pairs.ogg",
    COMBO_DOUBLE_TRIPLETS: "game_farkle/doubletriplets.ogg",
    COMBO_FULL_HOUSE: "game_farkle/fullhouse.ogg",
}


def count_dice(dice: list[int]) -> dict[int, int]:
    """Count occurrences of each die value (1-6)."""
    counts = {i: 0 for i in range(1, 7)}
    for die in dice:
        counts[die] += 1
    return counts


def has_combination(dice: list[int], combo_type: str, number: int = 0) -> bool:
    """Check if dice contain a specific combination."""
    counts = count_dice(dice)

    if combo_type == COMBO_SINGLE_1:
        return counts[1] >= 1
    elif combo_type == COMBO_SINGLE_5:
        return counts[5] >= 1
    elif combo_type == COMBO_THREE_OF_KIND:
        return counts[number] >= 3
    elif combo_type == COMBO_FOUR_OF_KIND:
        return counts[number] >= 4
    elif combo_type == COMBO_FIVE_OF_KIND:
        return counts[number] >= 5
    elif combo_type == COMBO_SIX_OF_KIND:
        return counts[number] == 6
    elif combo_type == COMBO_LARGE_STRAIGHT:
        if len(dice) != 6:
            return False
        return all(counts[i] == 1 for i in range(1, 7))
    elif combo_type == COMBO_SMALL_STRAIGHT:
        if len(dice) < 5:
            return False
        # Check for 1-2-3-4-5
        has_1_5 = all(counts[i] >= 1 for i in range(1, 6))
        # Check for 2-3-4-5-6
        has_2_6 = all(counts[i] >= 1 for i in range(2, 7))
        return has_1_5 or has_2_6
    elif combo_type == COMBO_THREE_PAIRS:
        if len(dice) != 6:
            return False
        pairs = sum(1 for i in range(1, 7) if counts[i] == 2)
        return pairs == 3
    elif combo_type == COMBO_DOUBLE_TRIPLETS:
        if len(dice) != 6:
            return False
        triplets = sum(1 for i in range(1, 7) if counts[i] == 3)
        return triplets == 2
    elif combo_type == COMBO_FULL_HOUSE:
        if len(dice) != 6:
            return False
        has_quad = any(counts[i] == 4 for i in range(1, 7))
        has_pair = any(counts[i] == 2 for i in range(1, 7))
        return has_quad and has_pair

    return False


def get_combination_points(combo_type: str, number: int = 0) -> int:
    """Get point value for a combination."""
    if combo_type == COMBO_SINGLE_1:
        return 10
    elif combo_type == COMBO_SINGLE_5:
        return 5
    elif combo_type == COMBO_THREE_OF_KIND:
        return 100 if number == 1 else number * 10
    elif combo_type == COMBO_FOUR_OF_KIND:
        return 200 if number == 1 else number * 20
    elif combo_type == COMBO_FIVE_OF_KIND:
        return 400 if number == 1 else number * 40
    elif combo_type == COMBO_SIX_OF_KIND:
        return 800 if number == 1 else number * 80
    elif combo_type == COMBO_SMALL_STRAIGHT:
        return 100
    elif combo_type == COMBO_LARGE_STRAIGHT:
        return 200
    elif combo_type == COMBO_THREE_PAIRS:
        return 150
    elif combo_type == COMBO_DOUBLE_TRIPLETS:
        return 250
    elif combo_type == COMBO_FULL_HOUSE:
        return 150
    return 0


def has_scoring_dice(dice: list[int]) -> bool:
    """Check if dice contain any scoring combinations (for farkle detection)."""
    if not dice:
        return False

    counts = count_dice(dice)

    # Single 1s or 5s
    if counts[1] > 0 or counts[5] > 0:
        return True

    # Three or more of a kind
    if any(counts[i] >= 3 for i in range(1, 7)):
        return True

    # Large straight (1-2-3-4-5-6)
    if len(dice) == 6 and all(counts[i] == 1 for i in range(1, 7)):
        return True

    # Small straight
    if len(dice) >= 5:
        has_1_5 = all(counts[i] >= 1 for i in range(1, 6))
        has_2_6 = all(counts[i] >= 1 for i in range(2, 7))
        if has_1_5 or has_2_6:
            return True

    # Three pairs
    if len(dice) == 6:
        pairs = sum(1 for i in range(1, 7) if counts[i] == 2)
        if pairs == 3:
            return True

    # Double triplets
    if len(dice) == 6:
        triplets = sum(1 for i in range(1, 7) if counts[i] == 3)
        if triplets == 2:
            return True

    return False


def get_available_combinations(dice: list[int]) -> list[tuple[str, int, int]]:
    """Get all available scoring combinations as (combo_type, number, points) tuples."""
    combinations = []

    if not dice:
        return combinations

    counts = count_dice(dice)

    # Six of a kind (check first, highest points)
    for num in range(1, 7):
        if has_combination(dice, COMBO_SIX_OF_KIND, num):
            points = get_combination_points(COMBO_SIX_OF_KIND, num)
            combinations.append((COMBO_SIX_OF_KIND, num, points))

    # Five of a kind
    for num in range(1, 7):
        if has_combination(dice, COMBO_FIVE_OF_KIND, num):
            points = get_combination_points(COMBO_FIVE_OF_KIND, num)
            combinations.append((COMBO_FIVE_OF_KIND, num, points))

    # Four of a kind
    for num in range(1, 7):
        if has_combination(dice, COMBO_FOUR_OF_KIND, num):
            points = get_combination_points(COMBO_FOUR_OF_KIND, num)
            combinations.append((COMBO_FOUR_OF_KIND, num, points))

    # Large straight
    if has_combination(dice, COMBO_LARGE_STRAIGHT):
        points = get_combination_points(COMBO_LARGE_STRAIGHT)
        combinations.append((COMBO_LARGE_STRAIGHT, 0, points))

    # Small straight
    if has_combination(dice, COMBO_SMALL_STRAIGHT):
        points = get_combination_points(COMBO_SMALL_STRAIGHT)
        combinations.append((COMBO_SMALL_STRAIGHT, 0, points))

    # Double triplets (higher priority than three pairs)
    if has_combination(dice, COMBO_DOUBLE_TRIPLETS):
        points = get_combination_points(COMBO_DOUBLE_TRIPLETS)
        combinations.append((COMBO_DOUBLE_TRIPLETS, 0, points))

    # Full house
    if has_combination(dice, COMBO_FULL_HOUSE):
        points = get_combination_points(COMBO_FULL_HOUSE)
        combinations.append((COMBO_FULL_HOUSE, 0, points))

    # Three pairs
    if has_combination(dice, COMBO_THREE_PAIRS):
        points = get_combination_points(COMBO_THREE_PAIRS)
        combinations.append((COMBO_THREE_PAIRS, 0, points))

    # Three of a kind
    for num in range(1, 7):
        if has_combination(dice, COMBO_THREE_OF_KIND, num):
            points = get_combination_points(COMBO_THREE_OF_KIND, num)
            combinations.append((COMBO_THREE_OF_KIND, num, points))

    # Single 1s (always available if there's at least one 1)
    if counts[1] > 0:
        points = get_combination_points(COMBO_SINGLE_1)
        combinations.append((COMBO_SINGLE_1, 1, points))

    # Single 5s
    if counts[5] > 0:
        points = get_combination_points(COMBO_SINGLE_5)
        combinations.append((COMBO_SINGLE_5, 5, points))

    # Sort by points descending
    combinations.sort(key=lambda x: x[2], reverse=True)

    return combinations


@dataclass
@register_game
class FarkleGame(Game):
    """
    Farkle dice game.

    Players take turns rolling 6 dice and selecting scoring combinations.
    After each selection, they can roll remaining dice or bank their points.
    Rolling dice with no scoring combinations (Farkle!) loses all turn points.
    First player to reach the target score wins.
    """

    players: list[FarklePlayer] = field(default_factory=list)
    options: FarkleOptions = field(default_factory=FarkleOptions)

    @classmethod
    def get_name(cls) -> str:
        return "Farkle"

    @classmethod
    def get_type(cls) -> str:
        return "farkle"

    @classmethod
    def get_category(cls) -> str:
        return "category-dice-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 20

    @classmethod
    def get_leaderboard_types(cls) -> list[dict]:
        return [
            {
                "id": "avg_points_per_turn",
                "numerator": "player_stats.{player_name}.total_score",
                "denominator": "player_stats.{player_name}.turns_taken",
                "aggregate": "sum",  # sum num/sum denom across games
                "format": "avg",
                "decimals": 1,
            },
            {
                "id": "best_single_turn",
                "path": "player_stats.{player_name}.best_turn",
                "aggregate": "max",
                "format": "score",
            },
        ]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> FarklePlayer:
        """Create a new player with Farkle-specific state."""
        return FarklePlayer(
            id=player_id,
            name=name,
            is_bot=is_bot,
            score=0,
            turn_score=0,
            current_roll=[],
            banked_dice=[],
            has_taken_combo=False,
        )

    def create_turn_action_set(self, player: FarklePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Roll action
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "farkle-roll", count=6),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                get_label="_get_roll_label",
            )
        )

        # Bank action
        action_set.add(
            Action(
                id="bank",
                label=Localization.get(locale, "farkle-bank", points=0),
                handler="_action_bank",
                is_enabled="_is_bank_enabled",
                is_hidden="_is_bank_hidden",
                get_label="_get_bank_label",
            )
        )

        # Check turn score (actions menu only)
        action_set.add(
            Action(
                id="check_turn_score",
                label=Localization.get(locale, "farkle-check-turn-score"),
                handler="_action_check_turn_score",
                is_enabled="_is_check_turn_score_enabled",
                is_hidden="_is_check_turn_score_hidden",
            )
        )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            target_order = ["check_scores", "whose_turn", "whos_at_table"]
            new_order = [aid for aid in action_set._order if aid not in target_order]
            for aid in target_order:
                if action_set.get_action(aid):
                    new_order.append(aid)
            action_set._order = new_order
        return action_set

    # WEB-SPECIFIC: Visibility Overrides



    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Override: Web visible when playing."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        user = None
        if hasattr(self, 'host_username') and self.host_username:
             player = self.get_player(self.host_username)
             if player:
                 user = self.get_user(player)
        locale = user.locale if user else "en"

        # Turn action keybinds
        self.define_keybind(
            "r", Localization.get(locale, "farkle-roll-label"), ["roll"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "b", Localization.get(locale, "farkle-bank-label"), ["bank"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "c", Localization.get("en", "farkle-check-turn-score"), ["check_turn_score"], state=KeybindState.ACTIVE
        )

    def _get_combo_label(
        self, locale: str, combo_type: str, number: int, points: int
    ) -> str:
        """Get the localized label for a scoring combination."""
        if combo_type == COMBO_SINGLE_1:
            return Localization.get(locale, "farkle-take-single-one", points=points)
        elif combo_type == COMBO_SINGLE_5:
            return Localization.get(locale, "farkle-take-single-five", points=points)
        elif combo_type == COMBO_THREE_OF_KIND:
            return Localization.get(
                locale, "farkle-take-three-kind", number=number, points=points
            )
        elif combo_type == COMBO_FOUR_OF_KIND:
            return Localization.get(
                locale, "farkle-take-four-kind", number=number, points=points
            )
        elif combo_type == COMBO_FIVE_OF_KIND:
            return Localization.get(
                locale, "farkle-take-five-kind", number=number, points=points
            )
        elif combo_type == COMBO_SIX_OF_KIND:
            return Localization.get(
                locale, "farkle-take-six-kind", number=number, points=points
            )
        elif combo_type == COMBO_SMALL_STRAIGHT:
            return Localization.get(
                locale, "farkle-take-small-straight", points=points
            )
        elif combo_type == COMBO_LARGE_STRAIGHT:
            return Localization.get(
                locale, "farkle-take-large-straight", points=points
            )
        elif combo_type == COMBO_THREE_PAIRS:
            return Localization.get(locale, "farkle-take-three-pairs", points=points)
        elif combo_type == COMBO_DOUBLE_TRIPLETS:
            return Localization.get(
                locale, "farkle-take-double-triplets", points=points
            )
        elif combo_type == COMBO_FULL_HOUSE:
            return Localization.get(locale, "farkle-take-full-house", points=points)
        return Localization.get(locale, "farkle-combo-fallback", combo=combo_type, points=points)

    def _get_combo_name(self, combo_type: str, number: int, locale: str = "en") -> str:
        """Get the localized name for a combo."""
        if combo_type == COMBO_SINGLE_1:
            return Localization.get(locale, "farkle-combo-single-1")
        elif combo_type == COMBO_SINGLE_5:
            return Localization.get(locale, "farkle-combo-single-5")
        elif combo_type == COMBO_THREE_OF_KIND:
            return Localization.get(locale, "farkle-combo-three-kind", number=number)
        elif combo_type == COMBO_FOUR_OF_KIND:
            return Localization.get(locale, "farkle-combo-four-kind", number=number)
        elif combo_type == COMBO_FIVE_OF_KIND:
            return Localization.get(locale, "farkle-combo-five-kind", number=number)
        elif combo_type == COMBO_SIX_OF_KIND:
            return Localization.get(locale, "farkle-combo-six-kind", number=number)
        elif combo_type == COMBO_SMALL_STRAIGHT:
            return Localization.get(locale, "farkle-combo-small-straight")
        elif combo_type == COMBO_LARGE_STRAIGHT:
            return Localization.get(locale, "farkle-combo-large-straight")
        elif combo_type == COMBO_THREE_PAIRS:
            return Localization.get(locale, "farkle-combo-three-pairs")
        elif combo_type == COMBO_DOUBLE_TRIPLETS:
            return Localization.get(locale, "farkle-combo-double-triplets")
        elif combo_type == COMBO_FULL_HOUSE:
            return Localization.get(locale, "farkle-combo-full-house")
        return combo_type

    def update_scoring_actions(self, player: FarklePlayer) -> None:
        """Update scoring actions based on current roll.

        Scoring actions are placed BEFORE roll/bank in the menu.
        """
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Remove old scoring actions from _actions dict
        old_actions = [
            action_id
            for action_id in turn_set._actions.keys()
            if action_id.startswith("score_")
        ]
        for action_id in old_actions:
            del turn_set._actions[action_id]

        # Get available combinations
        combos = get_available_combinations(player.current_roll)

        # Rebuild the order: scoring actions first, then roll, bank, check_turn_score
        turn_set._order.clear()

        # Add scoring actions first (sorted by points, highest first)
        for combo_type, number, points in combos:
            action_id = f"score_{combo_type}_{number}"
            label = self._get_combo_label(locale, combo_type, number, points)

            turn_set._actions[action_id] = Action(
                id=action_id,
                label=label,
                handler="_action_take_combo",
                is_enabled="_is_scoring_action_enabled",
                is_hidden="_is_scoring_action_hidden",
            )
            turn_set._order.append(action_id)

        # Add roll, bank, check_turn_score after scoring actions
        for action_id in ["roll", "bank", "check_turn_score"]:
            if action_id in turn_set._actions:
                turn_set._order.append(action_id)

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        """Check if roll action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if player.is_spectator:
            return "action-spectator"
        farkle_player: FarklePlayer = player  # type: ignore
        can_roll = len(farkle_player.current_roll) == 0 or farkle_player.has_taken_combo
        if not can_roll:
            return "farkle-must-take-combo"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        """Check if roll action is hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        farkle_player: FarklePlayer = player  # type: ignore
        can_roll = len(farkle_player.current_roll) == 0 or farkle_player.has_taken_combo
        if not can_roll:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_roll_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for roll action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        farkle_player: FarklePlayer = player  # type: ignore
        num_dice = self._get_roll_dice_count(farkle_player)
        return Localization.get(locale, "farkle-roll", count=num_dice)

    def _is_bank_enabled(self, player: Player) -> str | None:
        """Check if bank action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if player.is_spectator:
            return "action-spectator"
        farkle_player: FarklePlayer = player  # type: ignore
        can_bank = farkle_player.turn_score > 0 and (
            len(farkle_player.current_roll) == 0
            or not has_scoring_dice(farkle_player.current_roll)
        )
        if not can_bank:
            return "farkle-cannot-bank"
        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Check if bank action is hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        farkle_player: FarklePlayer = player  # type: ignore
        can_bank = farkle_player.turn_score > 0 and (
            len(farkle_player.current_roll) == 0
            or not has_scoring_dice(farkle_player.current_roll)
        )
        if not can_bank:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_bank_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for bank action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        farkle_player: FarklePlayer = player  # type: ignore
        return Localization.get(locale, "farkle-bank", points=farkle_player.turn_score)

    def _is_check_turn_score_enabled(self, player: Player) -> str | None:
        """Check if check turn score action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_turn_score_hidden(self, player: Player) -> Visibility:
        """Check turn score is always hidden from menu (keybind only)."""
        return Visibility.HIDDEN

    def _is_scoring_action_enabled(self, player: Player) -> str | None:
        """Check if a scoring action is enabled (scoring actions are only created when available)."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_scoring_action_hidden(self, player: Player) -> Visibility:
        """Check if a scoring action is hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_roll_dice_count(self, player: FarklePlayer) -> int:
        """Get the number of dice that will be rolled."""
        if len(player.current_roll) > 0:
            return len(player.current_roll)
        else:
            num_dice = 6 - len(player.banked_dice)
            if num_dice == 0:
                num_dice = 6  # Hot dice
            return num_dice

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action."""
        farkle_player: FarklePlayer = player  # type: ignore

        # Check for hot dice (all 6 banked) and reset
        if len(farkle_player.current_roll) == 0:
            num_dice = 6 - len(farkle_player.banked_dice)
            if num_dice == 0:
                # Hot dice! Reset banked dice and roll all 6
                farkle_player.banked_dice = []
                num_dice = 6
        else:
            num_dice = len(farkle_player.current_roll)

        self.broadcast_l("farkle-rolls", player=player.name, count=num_dice)
        self.play_sound("game_pig/roll.ogg")

        # Jolt bot to pause before next action
        BotHelper.jolt_bot(player, ticks=random.randint(10, 20))

        # Roll the dice
        farkle_player.current_roll = sorted(
            [random.randint(1, 6) for _ in range(num_dice)]
        )

        # Announce the roll
        dice_str = ", ".join(str(d) for d in farkle_player.current_roll)
        self.broadcast_l("farkle-roll-result", dice=dice_str)

        # Check for farkle
        if not has_scoring_dice(farkle_player.current_roll):
            self.play_sound("game_farkle/farkle.ogg")
            self.broadcast_l(
                "farkle-farkle", player=player.name, points=farkle_player.turn_score
            )
            # Track turn (farkle = 0 points banked)
            farkle_player.turns_taken += 1
            farkle_player.turn_score = 0
            farkle_player.current_roll = []
            farkle_player.banked_dice = []
            self.end_turn()
            return

        # Reset combo flag after roll
        farkle_player.has_taken_combo = False

        # Update scoring actions based on new roll
        self.update_scoring_actions(farkle_player)
        self.rebuild_player_menu(farkle_player)

    def _action_take_combo(self, player: Player, action_id: str) -> None:
        """Handle taking a scoring combination."""
        farkle_player: FarklePlayer = player  # type: ignore

        # Jolt bot to pause before next action
        BotHelper.jolt_bot(player, ticks=random.randint(8, 12))

        # Parse combo type and number from action_id (e.g., "score_three_of_kind_4")
        parts = action_id.split("_", 1)[1]  # Remove "score_" prefix

        # Extract combo type and number
        if parts.startswith("single_1"):
            combo_type = COMBO_SINGLE_1
            number = 1
        elif parts.startswith("single_5"):
            combo_type = COMBO_SINGLE_5
            number = 5
        elif parts.startswith("three_of_kind"):
            combo_type = COMBO_THREE_OF_KIND
            number = int(parts.split("_")[-1])
        elif parts.startswith("four_of_kind"):
            combo_type = COMBO_FOUR_OF_KIND
            number = int(parts.split("_")[-1])
        elif parts.startswith("five_of_kind"):
            combo_type = COMBO_FIVE_OF_KIND
            number = int(parts.split("_")[-1])
        elif parts.startswith("six_of_kind"):
            combo_type = COMBO_SIX_OF_KIND
            number = int(parts.split("_")[-1])
        elif parts.startswith("small_straight"):
            combo_type = COMBO_SMALL_STRAIGHT
            number = 0
        elif parts.startswith("large_straight"):
            combo_type = COMBO_LARGE_STRAIGHT
            number = 0
        elif parts.startswith("three_pairs"):
            combo_type = COMBO_THREE_PAIRS
            number = 0
        elif parts.startswith("double_triplets"):
            combo_type = COMBO_DOUBLE_TRIPLETS
            number = 0
        elif parts.startswith("full_house"):
            combo_type = COMBO_FULL_HOUSE
            number = 0
        else:
            return  # Unknown combo

        # Validate that the combo is actually available in the current roll
        if not has_combination(farkle_player.current_roll, combo_type, number):
            # Combo no longer available (stale menu state), refresh the menu
            self.update_scoring_actions(farkle_player)
            self.rebuild_player_menu(farkle_player)
            return

        points = get_combination_points(combo_type, number)

        # Remove dice from current_roll and add to banked_dice
        self._remove_combo_dice(farkle_player, combo_type, number)

        # Add points
        farkle_player.turn_score += points

        # Play sounds
        self.play_sound("game_farkle/takepoint.ogg")
        if combo_type in COMBO_SOUNDS:
            self.schedule_sound(COMBO_SOUNDS[combo_type], delay_ticks=2)

        # Announce what was taken (localized for each player)
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            
            # Get combo name in this user's locale
            combo_name = self._get_combo_name(combo_type, number, user.locale)
            
            if p == player:
                user.speak_l(
                    "farkle-you-take-combo",
                    combo=combo_name,
                    points=points
                )
            else:
                user.speak_l(
                    "farkle-takes-combo",
                    player=player.name,
                    combo=combo_name,
                    points=points
                )

        # Check for hot dice
        if len(farkle_player.banked_dice) == 6 and len(farkle_player.current_roll) == 0:
            self.broadcast_l("farkle-hot-dice")
            self.play_sound("game_farkle/hotdice.ogg")

        # Mark that we've taken a combo
        farkle_player.has_taken_combo = True

        # Update actions
        self.update_scoring_actions(farkle_player)
        self.rebuild_player_menu(farkle_player)

    def _remove_combo_dice(
        self, player: FarklePlayer, combo_type: str, number: int
    ) -> None:
        """Remove dice from current_roll for the given combination."""
        counts = count_dice(player.current_roll)

        if combo_type == COMBO_SINGLE_1:
            # Remove one 1
            player.current_roll.remove(1)
            player.banked_dice.append(1)

        elif combo_type == COMBO_SINGLE_5:
            # Remove one 5
            player.current_roll.remove(5)
            player.banked_dice.append(5)

        elif combo_type == COMBO_THREE_OF_KIND:
            # Remove three of the number
            for _ in range(3):
                player.current_roll.remove(number)
                player.banked_dice.append(number)

        elif combo_type == COMBO_FOUR_OF_KIND:
            # Remove four of the number
            for _ in range(4):
                player.current_roll.remove(number)
                player.banked_dice.append(number)

        elif combo_type == COMBO_FIVE_OF_KIND:
            # Remove five of the number
            for _ in range(5):
                player.current_roll.remove(number)
                player.banked_dice.append(number)

        elif combo_type == COMBO_SIX_OF_KIND:
            # Remove all six of the number
            for _ in range(6):
                player.current_roll.remove(number)
                player.banked_dice.append(number)

        elif combo_type == COMBO_LARGE_STRAIGHT:
            # Remove all dice (1-6)
            player.banked_dice.extend(player.current_roll)
            player.current_roll = []

        elif combo_type == COMBO_SMALL_STRAIGHT:
            # Remove 5 dice for small straight
            counts = count_dice(player.current_roll)
            # Determine which straight we have
            has_1_5 = all(counts[i] >= 1 for i in range(1, 6))
            if has_1_5:
                needed = [1, 2, 3, 4, 5]
            else:
                needed = [2, 3, 4, 5, 6]

            for num in needed:
                player.current_roll.remove(num)
                player.banked_dice.append(num)

        elif combo_type in (
            COMBO_THREE_PAIRS,
            COMBO_DOUBLE_TRIPLETS,
            COMBO_FULL_HOUSE,
        ):
            # Remove all 6 dice
            player.banked_dice.extend(player.current_roll)
            player.current_roll = []

    def _action_bank(self, player: Player, action_id: str) -> None:
        """Handle bank action."""
        farkle_player: FarklePlayer = player  # type: ignore

        # Track stats before resetting
        farkle_player.turns_taken += 1
        if farkle_player.turn_score > farkle_player.best_turn:
            farkle_player.best_turn = farkle_player.turn_score

        # Add turn score to permanent score
        farkle_player.score += farkle_player.turn_score

        # Sync to TeamManager for score actions
        self._team_manager.add_to_team_score(player.name, farkle_player.turn_score)

        self.play_sound(f"game_farkle/bank{random.randint(1, 3)}.ogg")

        self.broadcast_l(
            "farkle-banks",
            player=player.name,
            points=farkle_player.turn_score,
            total=farkle_player.score,
        )

        # Reset turn state
        farkle_player.turn_score = 0
        farkle_player.current_roll = []
        farkle_player.banked_dice = []
        farkle_player.has_taken_combo = False

        self.end_turn()

    def _action_check_turn_score(self, player: Player, action_id: str) -> None:
        """Handle check turn score action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        
        current = self.current_player
        if current:
            farkle_current: FarklePlayer = current  # type: ignore
            self.status_box(
                player,
                [
                    Localization.get(
                        locale,
                        "farkle-turn-score",
                        player=current.name,
                        points=farkle_current.turn_score,
                    )
                ],
            )
        else:
            self.status_box(
                player, [Localization.get(locale, "farkle-no-turn")]
            )

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Set up TeamManager for score tracking (individual mode)
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Reset all player state
        for p in active_players:
            farkle_p: FarklePlayer = p  # type: ignore
            farkle_p.score = 0
            farkle_p.turn_score = 0
            farkle_p.current_roll = []
            farkle_p.banked_dice = []
            farkle_p.has_taken_combo = False

        # Play intro music (using pig music as placeholder)
        self.play_music("game_pig/mus.ogg")

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1

        # Refresh turn order
        self.set_turn_players(self.get_active_players())

        self.broadcast_l("game-round-start", round=self.round)

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        farkle_player: FarklePlayer = player  # type: ignore

        # Reset turn state
        farkle_player.turn_score = 0
        farkle_player.current_roll = []
        farkle_player.banked_dice = []
        farkle_player.has_taken_combo = False

        # Clear stale scoring actions from previous turn (current_roll is empty now)
        self.update_scoring_actions(farkle_player)

        # Announce turn
        self.announce_turn()

        # Set up bot if needed
        if player.is_bot:
            BotHelper.set_target(player, 0)  # Bot will calculate during think

        # Rebuild menus
        self.rebuild_all_menus()

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI and scheduled sounds."""
        super().on_tick()
        self.process_scheduled_sounds()

        if not self.game_active:
            return

        BotHelper.on_tick(self)

    def bot_think(self, player: FarklePlayer) -> str | None:
        """Bot AI decision making."""
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return None

        # Resolve actions to get enabled state
        resolved = turn_set.resolve_actions(self, player)

        # Take highest-value scoring combo first
        for ra in resolved:
            if ra.enabled and ra.action.id.startswith("score_"):
                return ra.action.id

        # Check roll/bank enabled state
        roll_enabled = self._is_roll_enabled(player) is None
        bank_enabled = self._is_bank_enabled(player) is None

        if roll_enabled:
            # Banking decision based on dice remaining and points
            dice_remaining = 6 - len(player.banked_dice)
            if dice_remaining == 0:
                dice_remaining = 6  # Hot dice

            # Check if someone already reached target score
            score_to_beat = None
            for other in self.players:
                if other != player:
                    other_farkle: FarklePlayer = other  # type: ignore
                    if other_farkle.score >= self.options.target_score:
                        if score_to_beat is None or other_farkle.score > score_to_beat:
                            score_to_beat = other_farkle.score

            potential_total = player.score + player.turn_score

            # If someone has already won, must beat them or bust trying
            if score_to_beat is not None and potential_total <= score_to_beat:
                return "roll"

            # Banking decision based on turn score and dice remaining
            if player.turn_score >= 35:
                # Bank probability increases as fewer dice remain
                bank_probabilities = {
                    6: 0.40,
                    5: 0.50,
                    4: 0.55,
                    3: 0.65,
                    2: 0.70,
                    1: 0.75,
                }
                bank_prob = bank_probabilities.get(dice_remaining, 0.50)

                if random.random() < bank_prob:
                    if bank_enabled:
                        return "bank"

            return "roll"

        if bank_enabled:
            return "bank"

        return None

    def _on_turn_end(self) -> None:
        """Handle end of a player's turn."""
        # Check if round is over
        if self.turn_index >= len(self.turn_players) - 1:
            self._on_round_end()
        else:
            self.advance_turn(announce=False)
            self._start_turn()

    def _on_round_end(self) -> None:
        """Handle end of a round."""
        # Check for winners
        active_players = self.get_active_players()
        winners = []
        high_score = 0

        for p in active_players:
            farkle_p: FarklePlayer = p  # type: ignore
            if farkle_p.score >= self.options.target_score:
                if farkle_p.score > high_score:
                    winners = [p]
                    high_score = farkle_p.score
                elif farkle_p.score == high_score:
                    winners.append(p)

        if len(winners) == 1:
            # Single winner
            self.play_sound("game_pig/win.ogg")
            winner_farkle: FarklePlayer = winners[0]  # type: ignore
            self.broadcast_l(
                "farkle-winner", player=winners[0].name, score=winner_farkle.score
            )
            self.finish_game()
        elif len(winners) > 1:
            # Tie - announce winners
            names = [w.name for w in winners]
            for p in self.players:
                user = self.get_user(p)
                if user:
                    names_str = Localization.format_list_and(user.locale, names)
                    user.speak_l("farkle-winners-tie", buffer="game", players=names_str)

            # Mark non-winners as spectators for tiebreaker
            winner_names = [w.name for w in winners]
            for p in active_players:
                if p.name not in winner_names:
                    p.is_spectator = True
            self._start_round()
        else:
            # No winner yet
            self._start_round()

    def build_game_result(self) -> GameResult:
        """Build the game result with Farkle-specific data."""
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )

        # Build final scores and per-player stats
        final_scores = {}
        player_stats = {}
        for p in sorted_players:
            farkle_p: FarklePlayer = p  # type: ignore
            final_scores[p.name] = farkle_p.score
            player_stats[p.name] = {
                "turns_taken": farkle_p.turns_taken,
                "best_turn": farkle_p.best_turn,
                "total_score": farkle_p.score,
            }

        winner = sorted_players[0] if sorted_players else None
        winner_farkle: FarklePlayer = winner  # type: ignore

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
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": winner_farkle.score if winner_farkle else 0,
                "final_scores": final_scores,
                "player_stats": player_stats,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Farkle game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(
                Localization.get(locale, "farkle-line-format", rank=i, player=name, points=points_str)
            )

        return lines

    def end_turn(self, jolt_min: int = 20, jolt_max: int = 30) -> None:
        """End the current player's turn."""
        BotHelper.jolt_bots(self, ticks=random.randint(jolt_min, jolt_max))
        self._on_turn_end()
