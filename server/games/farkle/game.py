"""
Farkle Game Implementation.

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
from ...game_utils.dice import DiceSet, random_dice_throw_sound
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


RISK_CONFIRM_TICKS = 200
RISK_CONFIRM_SECONDS = 10
RISKY_ROLL_TARGET_FRACTION = 5
BOT_FARKLE_PROBABILITY_BY_DICE = {
    1: 2 / 3,
    2: 4 / 9,
    3: 5 / 18,
    4: 17 / 108,
    5: 25 / 324,
    6: 5 / 216,
}
# Expected future value, scaled to PlayAural's compact Farkle scores. These
# keep the bot aggressive with high-value six/five-dice rolls and cautious with
# one/two-dice rolls where Farkle risk dominates.
BOT_EXPECTED_GAIN_BY_DICE = {
    1: 26,
    2: 25,
    3: 29,
    4: 38,
    5: 49,
    6: 71,
}
BOT_BANK_MARGIN = 1.03
BOT_CLOSE_GAP_FRACTION = 8
BOT_FAR_GAP_FRACTION = 4
BOT_MEANINGFUL_TURN_FRACTION = 10


@dataclass
class FarklePlayer(Player):
    """Player state for Farkle game."""

    score: int = 0  # Permanent score (banked points)
    turn_score: int = 0  # Points accumulated this turn (lost on farkle)
    dice: DiceSet = field(default_factory=lambda: DiceSet(num_dice=6))  # Dice state
    banked_dice: list[int] = field(default_factory=list)  # Dice taken this turn
    has_taken_combo: bool = False  # True after taking a combo (enables roll)
    pending_risky_action: str = ""
    risky_confirm_ticks: int = 0
    # Stats tracking
    turns_taken: int = 0  # Number of turns completed (for avg points per turn)


@dataclass
class FarkleOptions(GameOptions):
    """Options for Farkle game."""

    target_score: int = option_field(
        IntOption(
            default=1000,
            min_val=500,
            max_val=5000,
            value_key="score",
            label="farkle-set-target-score",
            prompt="farkle-enter-target-score",
            change_msg="farkle-option-changed-target",
        )
    )
    min_entrance_score: int = option_field(
        IntOption(
            default=50,
            min_val=0,
            max_val=5000,
            value_key="score",
            label="farkle-set-entrance-score",
            prompt="farkle-enter-entrance-score",
            change_msg="farkle-option-changed-entrance",
        )
    )
    min_bank_score: int = option_field(
        IntOption(
            default=30,
            min_val=0,
            max_val=5000,
            value_key="score",
            label="farkle-set-bank-score",
            prompt="farkle-enter-bank-score",
            change_msg="farkle-option-changed-bank",
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

    relevant_preferences = ["brief_announcements", "confirm_destructive_actions"]

    players: list[FarklePlayer] = field(default_factory=list)
    options: FarkleOptions = field(default_factory=FarkleOptions)
    tiebreaker_player_names: list[str] = field(default_factory=list)

    @classmethod
    def get_name(cls) -> str:
        return "Farkle"

    @classmethod
    def get_type(cls) -> str:
        return "farkle"

    @classmethod
    def get_category(cls) -> str:
        return "dice"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 20

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "total_score", "high_score", "rating", "games_played"]

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
            banked_dice=[],
            has_taken_combo=False,
        )

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

    def _broadcast_actor_l(
        self,
        actor: FarklePlayer,
        personal_key: str,
        others_key: str,
        *,
        brief_personal_key: str | None = None,
        brief_others_key: str | None = None,
        **kwargs,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            is_actor = listener is actor
            key = personal_key if is_actor else others_key
            if self._wants_brief(user):
                if is_actor and brief_personal_key:
                    key = brief_personal_key
                elif not is_actor and brief_others_key:
                    key = brief_others_key

            payload = dict(kwargs)
            if not is_actor:
                payload["player"] = actor.name
            user.speak_l(key, buffer="game", **payload)

    def _broadcast_global_l(
        self,
        full_key: str,
        brief_key: str | None = None,
        **kwargs,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = brief_key if brief_key and self._wants_brief(user) else full_key
            user.speak_l(key, buffer="game", **kwargs)

    def _format_dice(self, dice: list[int]) -> str:
        return ", ".join(str(die) for die in dice)

    def _clear_risky_confirmation(self, player: FarklePlayer) -> None:
        player.pending_risky_action = ""
        player.risky_confirm_ticks = 0

    def _bank_minimum(self, player: FarklePlayer) -> int:
        return (
            self.options.min_entrance_score
            if player.score == 0
            else self.options.min_bank_score
        )

    def _can_bank_points(self, player: FarklePlayer) -> bool:
        return player.turn_score > 0 and (
            player.has_taken_combo or len(player.dice.values) == 0
        )

    def _risky_roll_threshold(self, player: FarklePlayer) -> int:
        return max(
            self._bank_minimum(player),
            max(1, self.options.target_score // RISKY_ROLL_TARGET_FRACTION),
        )

    def _should_confirm_risky_roll(self, player: FarklePlayer) -> bool:
        if player.is_bot:
            self._clear_risky_confirmation(player)
            return False
        if self._is_bank_enabled(player) is not None:
            self._clear_risky_confirmation(player)
            return False
        if player.turn_score < self._risky_roll_threshold(player):
            self._clear_risky_confirmation(player)
            return False

        user = self.get_user(player)
        if not user or not user.preferences.get_effective(
            "confirm_destructive_actions", game_type=self.get_type()
        ):
            self._clear_risky_confirmation(player)
            return False

        signature = f"roll:{player.turn_score}:{self._format_dice(player.dice.values)}"
        if (
            player.pending_risky_action == signature
            and player.risky_confirm_ticks > 0
        ):
            self._clear_risky_confirmation(player)
            return False

        player.pending_risky_action = signature
        player.risky_confirm_ticks = RISK_CONFIRM_TICKS
        user.speak_l(
            "farkle-confirm-risky-roll",
            buffer="game",
            points=player.turn_score,
            seconds=RISK_CONFIRM_SECONDS,
        )
        return True

    def _round_players(self) -> list[FarklePlayer]:
        active = [
            player
            for player in self.get_active_players()
            if isinstance(player, FarklePlayer)
        ]
        if not self.tiebreaker_player_names:
            return active
        finalists = set(self.tiebreaker_player_names)
        return [player for player in active if player.name in finalists]

    def _finish_with_winner(self, winner: FarklePlayer) -> None:
        self.play_sound("game_pig/win.ogg")
        self._broadcast_actor_l(
            winner,
            "farkle-you-win",
            "farkle-winner",
            brief_personal_key="farkle-you-win-brief",
            brief_others_key="farkle-winner-brief",
            score=winner.score,
        )
        self.finish_game()

    def before_menu_build(self, player: Player) -> None:
        super().before_menu_build(player)
        if isinstance(player, FarklePlayer):
            self.update_scoring_actions(player)

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
                show_in_actions_menu=False,
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
                id="check_turn_score",
                label=Localization.get(locale, "farkle-check-turn-score"),
                handler="_action_check_turn_score",
                is_enabled="_is_check_turn_score_enabled",
                is_hidden="_is_check_turn_score_hidden",
            )
        )

        if self.is_touch_client(user):
            target_order = ["check_turn_score", "check_scores", "whose_turn", "whos_at_table"]
            self._order_touch_standard_actions(action_set, target_order)
        return action_set

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Keep score checks visible for touch clients while playing."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Keep turn checks visible for touch clients while playing."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Keep table presence visible for touch clients."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        user = None
        if hasattr(self, "host_username") and self.host_username:
            player = self.get_player(self.host_username)
            if player:
                user = self.get_user(player)
        locale = user.locale if user else "en"

        # Turn action keybinds
        self.define_keybind(
            "r",
            Localization.get(locale, "farkle-roll-label"),
            ["roll"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "b",
            Localization.get(locale, "farkle-bank-label"),
            ["bank"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "c",
            Localization.get(locale, "farkle-check-turn-score"),
            ["check_turn_score"],
            state=KeybindState.ACTIVE,
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
        combos = get_available_combinations(player.dice.values)

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
                show_in_actions_menu=False,
            )
            turn_set._order.append(action_id)

        # Add roll, bank, check_turn_score after scoring actions
        for action_id in ["roll", "bank", "check_turn_score"]:
            if action_id in turn_set._actions:
                turn_set._order.append(action_id)

    def _first_scoring_action_id(self, player: FarklePlayer) -> str | None:
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return None
        return next(
            (action_id for action_id in turn_set._order if action_id.startswith("score_")),
            None,
        )

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
        can_roll = len(farkle_player.dice.values) == 0 or farkle_player.has_taken_combo
        if not can_roll:
            return "farkle-must-take-combo"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        """Check if roll action is hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
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
        if not self._can_bank_points(farkle_player):
            return "farkle-cannot-bank"

        # Check minimal scores
        minimum = self._bank_minimum(farkle_player)
        if farkle_player.turn_score < minimum:
            key = (
                "farkle-must-reach-entrance-score"
                if farkle_player.score == 0
                else "farkle-must-reach-bank-score"
            )
            return (key, {"points": minimum})

        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Check if bank action is hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        farkle_player: FarklePlayer = player  # type: ignore
        if not self._can_bank_points(farkle_player):
            return Visibility.HIDDEN

        # Check minimal scores (hide if criteria not met, same as can_bank check)
        if farkle_player.turn_score < self._bank_minimum(farkle_player):
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
        """Check turn score: visible for web clients during play, keybind-only for desktop."""
        if self.status != "playing":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
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
        if len(player.dice.values) > 0:
            return len(player.dice.values)
        else:
            num_dice = 6 - len(player.banked_dice)
            if num_dice == 0:
                num_dice = 6  # Hot dice
            return num_dice

    def _combo_dice_to_keep(
        self, dice: list[int], combo_type: str, number: int
    ) -> list[int]:
        """Return the exact dice consumed by a scoring combination."""
        if combo_type == COMBO_SINGLE_1:
            return [1]
        if combo_type == COMBO_SINGLE_5:
            return [5]
        if combo_type == COMBO_THREE_OF_KIND:
            return [number] * 3
        if combo_type == COMBO_FOUR_OF_KIND:
            return [number] * 4
        if combo_type == COMBO_FIVE_OF_KIND:
            return [number] * 5
        if combo_type == COMBO_SIX_OF_KIND:
            return [number] * 6
        if combo_type == COMBO_LARGE_STRAIGHT:
            return [1, 2, 3, 4, 5, 6]
        if combo_type == COMBO_SMALL_STRAIGHT:
            counts = count_dice(dice)
            if all(counts[i] >= 1 for i in range(1, 6)):
                return [1, 2, 3, 4, 5]
            return [2, 3, 4, 5, 6]
        if combo_type in (
            COMBO_THREE_PAIRS,
            COMBO_DOUBLE_TRIPLETS,
            COMBO_FULL_HOUSE,
        ):
            return list(dice)
        return []

    def _dice_after_combo(
        self, dice: list[int], combo_type: str, number: int
    ) -> list[int]:
        remaining = list(dice)
        for die in self._combo_dice_to_keep(dice, combo_type, number):
            remaining.remove(die)
        return remaining

    def _bot_combo_value(
        self,
        player: FarklePlayer,
        combo_type: str,
        number: int,
        points: int,
    ) -> tuple[float, int, int]:
        remaining = self._dice_after_combo(player.dice.values, combo_type, number)
        next_roll_count = len(remaining) if remaining else 6
        future_gain = BOT_EXPECTED_GAIN_BY_DICE[next_roll_count]
        # Prefer states that score now and leave richer future rolls. The third
        # tuple item breaks near-ties toward using more dice, especially hot dice.
        return (points + future_gain, points, -len(remaining))

    def _bot_best_scoring_action(
        self,
        player: FarklePlayer,
        resolved,
    ) -> str | None:
        enabled_score_ids = {
            ra.action.id
            for ra in resolved
            if ra.enabled and ra.action.id.startswith("score_")
        }
        if not enabled_score_ids:
            return None

        best_action_id: str | None = None
        best_value: tuple[float, int, int] | None = None
        for combo_type, number, points in get_available_combinations(player.dice.values):
            action_id = f"score_{combo_type}_{number}"
            if action_id not in enabled_score_ids:
                continue
            value = self._bot_combo_value(player, combo_type, number, points)
            if best_value is None or value > best_value:
                best_value = value
                best_action_id = action_id
        return best_action_id

    def _bot_should_bank(
        self,
        player: FarklePlayer,
        *,
        roll_enabled: bool,
        bank_enabled: bool,
    ) -> bool:
        if not bank_enabled:
            return False
        if not roll_enabled:
            return True

        dice_to_roll = self._get_roll_dice_count(player)
        potential_total = player.score + player.turn_score
        score_to_beat = self._score_to_beat(player)

        # If an opponent has already crossed the target, bank only when this
        # turn is enough to take the lead. Otherwise the bot must keep pushing.
        if score_to_beat is not None:
            return potential_total > score_to_beat

        if potential_total >= self.options.target_score:
            return True

        farkle_probability = BOT_FARKLE_PROBABILITY_BY_DICE[dice_to_roll]
        expected_gain = BOT_EXPECTED_GAIN_BY_DICE[dice_to_roll]
        roll_value = (1 - farkle_probability) * (player.turn_score + expected_gain)
        bank_value = float(player.turn_score)
        leader_score = self._bot_leader_score(player)
        margin = self._bot_contextual_bank_margin(
            player,
            dice_to_roll=dice_to_roll,
            potential_total=potential_total,
            leader_score=leader_score,
        )

        return roll_value <= bank_value * margin

    def _bot_leader_score(self, player: FarklePlayer) -> int:
        return max(
            (
                other.score
                for other in self._round_players()
                if other is not player
            ),
            default=0,
        )

    def _bot_contextual_bank_margin(
        self,
        player: FarklePlayer,
        *,
        dice_to_roll: int,
        potential_total: int,
        leader_score: int,
    ) -> float:
        """Tune bot risk tolerance from score pressure and dice danger."""
        target = max(1, self.options.target_score)
        current_gap = max(0, leader_score - player.score)
        bank_gap = max(0, leader_score - potential_total)
        close_gap = max(50, target // BOT_CLOSE_GAP_FRACTION)
        far_gap = max(150, target // BOT_FAR_GAP_FRACTION)
        meaningful_turn = max(
            self._bank_minimum(player),
            target // BOT_MEANINGFUL_TURN_FRACTION,
        )

        margin = BOT_BANK_MARGIN
        if potential_total >= leader_score:
            margin += 0.12
        elif bank_gap <= close_gap:
            margin += 0.08
        elif current_gap and player.turn_score >= max(
            meaningful_turn,
            int(current_gap * 0.6),
        ):
            margin += 0.04
        elif bank_gap >= far_gap and player.turn_score < meaningful_turn:
            margin -= 0.08

        if dice_to_roll == 1:
            margin += 0.20
        elif dice_to_roll == 2:
            margin += 0.10
        elif dice_to_roll >= 5 and bank_gap > close_gap and potential_total < target:
            margin -= 0.05

        if player.turn_score >= max(meaningful_turn * 2, target // 4):
            margin += 0.05

        return max(0.75, margin)

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action."""
        farkle_player: FarklePlayer = player  # type: ignore

        if self._should_confirm_risky_roll(farkle_player):
            self.request_menu_focus(farkle_player, "roll")
            return

        self._clear_risky_confirmation(farkle_player)

        # Check for hot dice (all 6 banked) and reset
        if len(farkle_player.dice.values) == 0:
            num_dice = 6 - len(farkle_player.banked_dice)
            if num_dice == 0:
                # Hot dice! Reset banked dice and roll all 6
                farkle_player.banked_dice = []
                num_dice = 6
        else:
            num_dice = len(farkle_player.dice.values)

        self._broadcast_actor_l(
            farkle_player,
            "farkle-you-roll",
            "farkle-player-rolls",
            brief_personal_key="farkle-you-roll-brief",
            brief_others_key="farkle-player-rolls-brief",
            count=num_dice,
        )
        self.play_sound(random_dice_throw_sound())

        # Jolt bot to pause before next action
        BotHelper.jolt_bot(player, ticks=random.randint(10, 20))

        # Roll the dice
        farkle_player.dice.num_dice = num_dice
        farkle_player.dice.reset()
        farkle_player.dice.roll()
        farkle_player.dice.values.sort()

        # Announce the roll
        dice_str = self._format_dice(farkle_player.dice.values)
        self._broadcast_global_l(
            "farkle-roll-result",
            "farkle-roll-result-brief",
            dice=dice_str,
        )

        # Check for farkle
        if not has_scoring_dice(farkle_player.dice.values):
            self.play_sound("game_farkle/farkle.ogg")
            lost_points = farkle_player.turn_score
            self._broadcast_actor_l(
                farkle_player,
                "farkle-you-farkle",
                "farkle-player-farkles",
                brief_personal_key="farkle-you-farkle-brief",
                brief_others_key="farkle-player-farkles-brief",
                points=lost_points,
            )
            # Track turn (farkle = 0 points banked)
            farkle_player.turns_taken += 1
            farkle_player.turn_score = 0
            farkle_player.dice.reset()
            farkle_player.banked_dice = []
            farkle_player.has_taken_combo = False
            self.end_turn()
            return

        # Reset combo flag after roll
        farkle_player.has_taken_combo = False

        # Update scoring actions based on new roll
        self.update_scoring_actions(farkle_player)
        focus = self._first_scoring_action_id(farkle_player)
        if focus:
            self.request_menu_focus(farkle_player, focus)
        self.refresh_menus(farkle_player)

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
            user = self.get_user(player)
            if user:
                user.speak_l("farkle-invalid-combo-action", buffer="game")
            return

        # Validate that the combo is actually available in the current roll
        if not has_combination(farkle_player.dice.values, combo_type, number):
            # Combo no longer available (stale menu state), refresh the menu
            self.update_scoring_actions(farkle_player)
            focus = self._first_scoring_action_id(farkle_player)
            if focus:
                self.request_menu_focus(farkle_player, focus)
            user = self.get_user(player)
            if user:
                user.speak_l("farkle-combo-no-longer-available", buffer="game")
            self.refresh_menus(farkle_player)
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
        self._clear_risky_confirmation(farkle_player)
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            
            # Get combo name in this user's locale
            combo_name = self._get_combo_name(combo_type, number, user.locale)
            
            if p == player:
                key = (
                    "farkle-you-take-combo-brief"
                    if self._wants_brief(user)
                    else "farkle-you-take-combo"
                )
                user.speak_l(key, buffer="game", combo=combo_name, points=points)
            else:
                key = (
                    "farkle-player-takes-combo-brief"
                    if self._wants_brief(user)
                    else "farkle-player-takes-combo"
                )
                user.speak_l(
                    key,
                    buffer="game",
                    player=player.name,
                    combo=combo_name,
                    points=points,
                )

        # Check for hot dice
        if len(farkle_player.banked_dice) == 6 and len(farkle_player.dice.values) == 0:
            self._broadcast_actor_l(
                farkle_player,
                "farkle-you-hot-dice",
                "farkle-player-hot-dice",
                brief_personal_key="farkle-you-hot-dice-brief",
                brief_others_key="farkle-player-hot-dice-brief",
            )
            self.play_sound("game_farkle/hotdice.ogg")

        # Mark that we've taken a combo
        farkle_player.has_taken_combo = True

        # Update actions
        self.update_scoring_actions(farkle_player)
        self.refresh_menus(farkle_player)

    def _remove_combo_dice(
        self, player: FarklePlayer, combo_type: str, number: int
    ) -> None:
        """Remove dice from dice.values for the given combination."""
        for die in self._combo_dice_to_keep(player.dice.values, combo_type, number):
            player.dice.values.remove(die)
            player.banked_dice.append(die)

    def _action_bank(self, player: Player, action_id: str) -> None:
        """Handle bank action."""
        farkle_player: FarklePlayer = player  # type: ignore
        banked_points = farkle_player.turn_score

        # Track stats before resetting
        farkle_player.turns_taken += 1

        # Add turn score to permanent score
        farkle_player.score += banked_points

        # Sync to TeamManager for score actions
        self._team_manager.add_to_team_score(player.name, banked_points)

        self.play_sound(f"game_farkle/bank{random.randint(1, 3)}.ogg")
        self._clear_risky_confirmation(farkle_player)

        self._broadcast_actor_l(
            farkle_player,
            "farkle-you-bank",
            "farkle-player-banks",
            brief_personal_key="farkle-you-bank-brief",
            brief_others_key="farkle-player-banks-brief",
            points=banked_points,
            total=farkle_player.score,
        )

        # Reset turn state
        farkle_player.turn_score = 0
        farkle_player.dice.reset()
        farkle_player.banked_dice = []
        farkle_player.has_taken_combo = False

        user = self.get_user(farkle_player)
        if self.is_touch_client(user):
            self.request_menu_focus(farkle_player, "roll")

        self.end_turn()

    def _action_check_turn_score(self, player: Player, action_id: str) -> None:
        """Handle check turn score action."""
        user = self.get_user(player)
        if not user:
            return

        # locale = user.locale if user else "en" # locale is accessed inside speak_l if needed, or we pass args
        
        current = self.current_player
        if current:
            farkle_current: FarklePlayer = current  # type: ignore
            if current is player:
                user.speak_l(
                    "farkle-your-turn-score",
                    buffer="game",
                    points=farkle_current.turn_score,
                )
            else:
                user.speak_l(
                    "farkle-turn-score",
                    buffer="game",
                    player=current.name,
                    points=farkle_current.turn_score,
                )
        else:
            user.speak_l("farkle-no-turn", buffer="game")

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        """Validate Farkle setup options before the game starts."""
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        target = self.options.target_score
        if self.options.min_entrance_score > target:
            errors.append(
                (
                    "farkle-error-entrance-above-target",
                    {"entrance": self.options.min_entrance_score, "target": target},
                )
            )
        if self.options.min_bank_score > target:
            errors.append(
                (
                    "farkle-error-bank-above-target",
                    {"bank": self.options.min_bank_score, "target": target},
                )
            )
        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.tiebreaker_player_names = []

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
            farkle_p.dice.reset()
            farkle_p.banked_dice = []
            farkle_p.has_taken_combo = False
            farkle_p.turns_taken = 0
            self._clear_risky_confirmation(farkle_p)

        # Play intro music (using pig music as placeholder)
        self.play_music("game_pig/mus.ogg")

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        round_players = self._round_players()
        if not round_players:
            return
        if len(round_players) == 1 and self.tiebreaker_player_names:
            self._finish_with_winner(round_players[0])
            return

        self.round += 1

        # Refresh turn order
        self.set_turn_players(round_players)

        if self.tiebreaker_player_names:
            for listener in self.players:
                user = self.get_user(listener)
                if user:
                    names = Localization.format_list_and(
                        user.locale, [player.name for player in round_players]
                    )
                    user.speak_l(
                        "farkle-tiebreaker-round-start",
                        buffer="game",
                        round=self.round,
                        players=names,
                    )
        else:
            self.broadcast_l("game-round-start", buffer="game", round=self.round)

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        farkle_player: FarklePlayer = player  # type: ignore

        # Reset turn state
        farkle_player.turn_score = 0
        farkle_player.dice.reset()
        farkle_player.banked_dice = []
        farkle_player.has_taken_combo = False
        self._clear_risky_confirmation(farkle_player)

        # Clear stale scoring actions from previous turn (current_roll is empty now)
        self.update_scoring_actions(farkle_player)

        # Announce turn
        self.announce_turn()

        # Set up bot if needed
        if player.is_bot:
            BotHelper.set_target(player, 0)  # Bot will calculate during think

        # Rebuild menus
        self.refresh_menus()

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI and scheduled sounds."""
        super().on_tick()
        self.process_scheduled_sounds()
        for player in self.players:
            if isinstance(player, FarklePlayer) and player.risky_confirm_ticks > 0:
                player.risky_confirm_ticks -= 1
                if player.risky_confirm_ticks <= 0:
                    self._clear_risky_confirmation(player)

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

        # Check roll/bank enabled state
        roll_enabled = self._is_roll_enabled(player) is None
        bank_enabled = self._is_bank_enabled(player) is None

        # Keeping scoring dice is risk-free and can only improve the eventual
        # bank. Do it before considering whether to bank or roll.
        scoring_action = self._bot_best_scoring_action(player, resolved)
        if scoring_action:
            return scoring_action

        if self._bot_should_bank(
            player,
            roll_enabled=roll_enabled,
            bank_enabled=bank_enabled,
        ):
            return "bank"

        if roll_enabled:
            return "roll"

        if bank_enabled:
            return "bank"

        return None

    def _score_to_beat(self, player: FarklePlayer) -> int | None:
        score_to_beat = None
        for other in self._round_players():
            if other is player:
                continue
            if other.score >= self.options.target_score:
                if score_to_beat is None or other.score > score_to_beat:
                    score_to_beat = other.score
        return score_to_beat

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
        round_players = self._round_players()
        winners: list[FarklePlayer] = []
        high_score = 0

        for p in round_players:
            if p.score >= self.options.target_score:
                if p.score > high_score:
                    winners = [p]
                    high_score = p.score
                elif p.score == high_score:
                    winners.append(p)

        if len(winners) == 1:
            self.tiebreaker_player_names = []
            self._finish_with_winner(winners[0])
        elif len(winners) > 1:
            # Tie - announce winners
            names = [w.name for w in winners]
            for p in self.players:
                user = self.get_user(p)
                if user:
                    names_str = Localization.format_list_and(user.locale, names)
                    user.speak_l("farkle-winners-tie", buffer="game", players=names_str)

            self.tiebreaker_player_names = names
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
                "total_score": farkle_p.score,
            }

        winner = sorted_players[0] if sorted_players else None
        winner_farkle: FarklePlayer = winner  # type: ignore
        winner_ids = [
            player.id
            for player in sorted_players
            if winner_farkle and player.score == winner_farkle.score  # type: ignore
        ]

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult.from_player(p)
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": winner_ids,
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
        previous_score = None
        rank = 0
        displayed = 0
        for name, score in final_scores.items():
            displayed += 1
            if score != previous_score:
                rank = displayed
                previous_score = score
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(
                Localization.get(
                    locale,
                    "farkle-line-format",
                    rank=rank,
                    player=name,
                    points=points_str,
                )
            )

        return lines

    def end_turn(self, jolt_min: int = 20, jolt_max: int = 30) -> None:
        """End the current player's turn."""
        BotHelper.jolt_bots(self, ticks=random.randint(jolt_min, jolt_max))
        self._on_turn_end()
