"""
Yahtzee Game Implementation for PlayAural.

Classic dice game: roll 5 dice up to 3 times per turn, then score in one of 13 categories.
Fill all categories to complete the game. Highest total score wins.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from .bot import bot_think as yahtzee_bot_think
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.dice import DiceSet, random_dice_throw_sound
from ...game_utils.dice_game_mixin import DiceGameMixin
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


# Scoring categories
UPPER_CATEGORIES = ["ones", "twos", "threes", "fours", "fives", "sixes"]
LOWER_CATEGORIES = [
    "three_kind",
    "four_kind",
    "full_house",
    "small_straight",
    "large_straight",
    "yahtzee",
    "chance",
]
ALL_CATEGORIES = UPPER_CATEGORIES + LOWER_CATEGORIES
JOKER_FIXED_SCORES = {
    "full_house": 25,
    "small_straight": 30,
    "large_straight": 40,
}

# Category display names (for localization keys)
CATEGORY_NAMES = {
    "ones": "yahtzee-category-ones",
    "twos": "yahtzee-category-twos",
    "threes": "yahtzee-category-threes",
    "fours": "yahtzee-category-fours",
    "fives": "yahtzee-category-fives",
    "sixes": "yahtzee-category-sixes",
    "three_kind": "yahtzee-category-three-kind",
    "four_kind": "yahtzee-category-four-kind",
    "full_house": "yahtzee-category-full-house",
    "small_straight": "yahtzee-category-small-straight",
    "large_straight": "yahtzee-category-large-straight",
    "yahtzee": "yahtzee-category-yahtzee",
    "chance": "yahtzee-category-chance",
}

# Upper section target values
UPPER_VALUES = {
    "ones": 1,
    "twos": 2,
    "threes": 3,
    "fours": 4,
    "fives": 5,
    "sixes": 6,
}


def count_dice(dice: list[int]) -> dict[int, int]:
    """Count occurrences of each die value (1-6)."""
    counts = {i: 0 for i in range(1, 7)}
    for die in dice:
        counts[die] += 1
    return counts


def calculate_score(dice: list[int], category: str) -> int:
    """Calculate the score for a category given the dice."""
    if not dice or len(dice) != 5:
        return 0

    counts = count_dice(dice)
    dice_sum = sum(dice)

    # Upper section — sum of matching dice
    if category in UPPER_VALUES:
        target = UPPER_VALUES[category]
        return counts[target] * target

    # Three of a Kind — sum of all if 3+ of same
    if category == "three_kind":
        if any(c >= 3 for c in counts.values()):
            return dice_sum
        return 0

    # Four of a Kind — sum of all if 4+ of same
    if category == "four_kind":
        if any(c >= 4 for c in counts.values()):
            return dice_sum
        return 0

    # Full House — 3 of one kind + 2 of another = 25 points.
    # A five-of-a-kind only scores here through the official Joker rule,
    # which depends on the player's scorecard and is handled by the game.
    if category == "full_house":
        has_three = any(c == 3 for c in counts.values())
        has_two = any(c == 2 for c in counts.values())
        if has_three and has_two:
            return 25
        return 0

    # Small Straight — 4 consecutive = 30 points
    if category == "small_straight":
        straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
        dice_set = set(dice)
        if any(s.issubset(dice_set) for s in straights):
            return 30
        return 0

    # Large Straight — 5 consecutive = 40 points
    if category == "large_straight":
        sorted_dice = sorted(dice)
        if sorted_dice in ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6]):
            return 40
        return 0

    # Yahtzee — 5 of a kind = 50 points
    if category == "yahtzee":
        if any(c == 5 for c in counts.values()):
            return 50
        return 0

    # Chance — sum of all dice
    if category == "chance":
        return dice_sum

    return 0


def is_yahtzee(dice: list[int]) -> bool:
    """Check if dice are a Yahtzee (5 of a kind)."""
    if len(dice) != 5:
        return False
    return len(set(dice)) == 1


def yahtzee_face(dice: list[int]) -> int | None:
    """Return the die face for a five-of-a-kind roll, otherwise None."""
    if not is_yahtzee(dice):
        return None
    return dice[0]


def _default_scores() -> dict[str, int | None]:
    """Create default scoresheet with all categories unfilled."""
    return {cat: None for cat in ALL_CATEGORIES}


@dataclass
class YahtzeePlayer(Player):
    """Player state for Yahtzee game."""

    # Dice state
    dice: DiceSet = field(default_factory=lambda: DiceSet(num_dice=5, sides=6))
    rolls_left: int = 3  # Rolls remaining this turn

    # Scoresheet — None means not filled, int is the score
    scores: dict[str, int | None] = field(default_factory=_default_scores)

    # Bonuses
    yahtzee_bonus_count: int = 0  # Number of Yahtzee bonuses earned
    upper_bonus_awarded: bool = False  # Whether upper section bonus was given

    def get_upper_total(self) -> int:
        """Get total of filled upper section scores."""
        return sum(
            self.scores.get(cat) or 0
            for cat in UPPER_CATEGORIES
            if self.scores.get(cat) is not None
        )

    def get_total_score(self) -> int:
        """Get total score including bonuses."""
        total = sum(s for s in self.scores.values() if s is not None)
        if self.upper_bonus_awarded:
            total += 35
        total += self.yahtzee_bonus_count * 100
        return total

    def get_open_categories(self) -> list[str]:
        """Get list of categories not yet filled."""
        return [cat for cat in ALL_CATEGORIES if self.scores.get(cat) is None]

    def is_scoresheet_complete(self) -> bool:
        """Check if all categories are filled."""
        return all(self.scores.get(cat) is not None for cat in ALL_CATEGORIES)


@dataclass
class YahtzeeOptions(GameOptions):
    """Options for Yahtzee game."""

    num_games: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=10,
            value_key="rounds",
            label="yahtzee-set-rounds",
            prompt="yahtzee-enter-rounds",
            change_msg="yahtzee-option-changed-rounds",
        )
    )


@dataclass
@register_game
class YahtzeeGame(Game, DiceGameMixin):
    """
    Yahtzee dice game.

    Players take turns rolling 5 dice up to 3 times, keeping dice between rolls.
    After rolling, they must score in one of 13 categories. Each category can
    only be used once. The game ends when all players have filled all categories.
    Highest total score wins.
    """

    relevant_preferences = [
        "brief_announcements",
        "clear_kept_on_roll",
        "dice_keeping_style",
    ]

    players: list[YahtzeePlayer] = field(default_factory=list)
    options: YahtzeeOptions = field(default_factory=YahtzeeOptions)

    # Game tracking
    current_game: int = 0
    games_played: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Yahtzee"

    @classmethod
    def get_type(cls) -> str:
        return "yahtzee"

    @classmethod
    def get_category(cls) -> str:
        return "dice"

    @classmethod
    def get_min_players(cls) -> int:
        return 1

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "total_score", "high_score", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> YahtzeePlayer:
        return YahtzeePlayer(id=player_id, name=name, is_bot=is_bot)

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_actor_l(
        self,
        actor: YahtzeePlayer,
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

    def _scorecard_players(self) -> list[YahtzeePlayer]:
        return [
            player
            for player in self.get_active_players()
            if isinstance(player, YahtzeePlayer)
        ]

    def _is_competitive_result(self) -> bool:
        return len(self._scorecard_players()) >= 2

    def _sync_team_scores(self) -> None:
        """Mirror authoritative scorecard totals into the shared scoreboard."""
        for team in self._team_manager.teams:
            team.total_score = 0
            team.round_score = 0

        for player in self._scorecard_players():
            team = self._team_manager.get_team(player.name)
            if team:
                team.total_score = player.get_total_score()

    def _sync_score_display_names(self) -> None:
        super()._sync_score_display_names()
        self._sync_team_scores()

    def _focus_roll_after_action(self, player: YahtzeePlayer) -> None:
        """Return touch users to the stable Roll anchor after a turn-ending score."""
        if self.is_touch_client(self.get_user(player)):
            self.request_menu_focus(player, "roll")

    def _joker_face(self, player: YahtzeePlayer) -> int | None:
        """Return the Yahtzee face when the official Joker rule applies."""
        face = yahtzee_face(player.dice.values)
        if face is None:
            return None
        if player.scores.get("yahtzee") is None:
            return None
        return face

    def _matching_upper_category(self, face: int) -> str:
        return UPPER_CATEGORIES[face - 1]

    def _score_category_disabled_reason(
        self, player: YahtzeePlayer, category: str
    ) -> str | tuple[str, dict] | None:
        joker_face_value = self._joker_face(player)
        if joker_face_value is None:
            return None

        matching_upper = self._matching_upper_category(joker_face_value)
        if player.scores.get(matching_upper) is None:
            if category != matching_upper:
                return ("yahtzee-joker-upper-required", {"face": joker_face_value})
            return None

        lower_open = any(player.scores.get(cat) is None for cat in LOWER_CATEGORIES)
        if lower_open and category in UPPER_CATEGORIES:
            return ("yahtzee-joker-lower-required", {"face": joker_face_value})
        return None

    def _get_scoreable_categories(self, player: YahtzeePlayer) -> list[str]:
        return [
            category
            for category in player.get_open_categories()
            if self._score_category_disabled_reason(player, category) is None
        ]

    def _calculate_score_for_player(
        self, player: YahtzeePlayer, category: str
    ) -> int:
        joker_face_value = self._joker_face(player)
        if joker_face_value is None:
            return calculate_score(player.dice.values, category)

        matching_upper = self._matching_upper_category(joker_face_value)
        matching_upper_open = player.scores.get(matching_upper) is None
        lower_open = any(player.scores.get(cat) is None for cat in LOWER_CATEGORIES)

        if matching_upper_open:
            if category == matching_upper:
                return calculate_score(player.dice.values, category)
            return calculate_score(player.dice.values, category)

        if lower_open:
            if category in JOKER_FIXED_SCORES:
                return JOKER_FIXED_SCORES[category]
            return calculate_score(player.dice.values, category)

        if category in UPPER_CATEGORIES:
            return 0
        return calculate_score(player.dice.values, category)

    def create_turn_action_set(self, player: YahtzeePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Roll action
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "yahtzee-roll-all"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                get_label="_get_roll_label",
                show_in_actions_menu=False,
            )
        )

        # Dice toggle actions (1-5 keys) — shown after first roll
        self.add_dice_toggle_actions(action_set)

        # Scoring category actions
        for cat in ALL_CATEGORIES:
            cat_name = Localization.get(locale, CATEGORY_NAMES[cat])
            action_set.add(
                Action(
                    id=f"score_{cat}",
                    label=f"{cat_name} (- points)",
                    handler="_action_score",
                    is_enabled=f"_is_score_{cat}_enabled",
                    is_hidden=f"_is_score_{cat}_hidden",
                    get_label=f"_get_score_{cat}_label",
                    show_in_actions_menu=False,
                )
            )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()
        self.define_keybind("r", "Roll dice", ["roll"], state=KeybindState.ACTIVE)
        self.setup_dice_keybinds()
        self.define_keybind("d", "View dice", ["view_dice"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "c", "View scoresheet", ["view_scoresheet"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "shift+c",
            "View all scorecards",
            ["view_all_scorecards"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ==========================================================================
    # Action guards
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if player.is_spectator:
            return "action-spectator"
        ytz_player: YahtzeePlayer = player  # type: ignore
        if ytz_player.rolls_left <= 0:
            return "yahtzee-no-rolls-left"
        # All dice already kept — nothing to roll
        if ytz_player.dice.has_rolled and ytz_player.dice.all_decided:
            return "action-not-available"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.is_touch_client(self.get_user(player)):
            return Visibility.VISIBLE
        ytz_player: YahtzeePlayer = player  # type: ignore
        if ytz_player.rolls_left <= 0:
            return Visibility.HIDDEN
        # Hide roll when every die is already kept (nothing to reroll)
        if ytz_player.dice.has_rolled and ytz_player.dice.all_decided:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_roll_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        ytz_player: YahtzeePlayer = player  # type: ignore
        if ytz_player.dice.has_rolled:
            return Localization.get(locale, "yahtzee-roll", count=ytz_player.rolls_left)
        return Localization.get(locale, "yahtzee-roll-all")

    def _is_dice_toggle_enabled(self, player: Player, die_index: int) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        ytz_player: YahtzeePlayer = player  # type: ignore
        if not ytz_player.dice.has_rolled:
            return "dice-not-rolled"
        if ytz_player.rolls_left <= 0:
            return "yahtzee-no-rolls-left"
        return None

    def _is_dice_toggle_hidden(self, player: Player, die_index: int) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        ytz_player: YahtzeePlayer = player  # type: ignore
        if not ytz_player.dice.has_rolled or ytz_player.rolls_left <= 0:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_view_dice_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "action-spectator"
        if self.status != "playing":
            return "action-not-playing"
        if not self.current_player:
            return "action-not-available"
        return None

    def _is_view_dice_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing" and not player.is_spectator:
                return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_view_scoresheet_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "action-spectator"
        if self.status != "playing":
            return "action-not-playing"
        if not self.current_player:
            return "action-not-available"
        return None

    def _is_view_scoresheet_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing" and not player.is_spectator:
                return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_view_all_scorecards_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not self._scorecard_players():
            return "yahtzee-scorecard-no-players"
        return None

    def _is_view_all_scorecards_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user) and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ==========================================================================
    # Action handlers
    # ==========================================================================

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action."""
        ytz_player: YahtzeePlayer = player  # type: ignore

        if ytz_player.rolls_left <= 0:
            return

        # Capture which dice will be rerolled (before rolling)
        had_rolled = ytz_player.dice.has_rolled
        if had_rolled:
            kept_and_locked = set(ytz_player.dice.kept) | set(ytz_player.dice.locked)
            rolled_indices = [
                i for i in range(ytz_player.dice.num_dice) if i not in kept_and_locked
            ]
        else:
            rolled_indices = list(range(ytz_player.dice.num_dice))

        self.play_sound(random_dice_throw_sound())

        user = self.get_user(player)
        clear_kept = (
            user.preferences.get_effective("clear_kept_on_roll", game_type=self.get_type())
            if user
            else True
        )
        ytz_player.dice.roll(lock_kept=False, clear_kept=clear_kept)
        # Value-based controls normally begin with every die kept. Respect the
        # explicit clear preference instead of immediately restoring that state.
        self._apply_dice_values_defaults(ytz_player, keep_all=not clear_kept)
        ytz_player.rolls_left -= 1

        # Announce only the dice that were actually rerolled.
        # On first roll that's all five; on subsequent rolls only the unkept ones.
        dice_str = ", ".join(str(ytz_player.dice.values[i]) for i in rolled_indices)
        self._broadcast_actor_l(
            ytz_player,
            "yahtzee-you-rolled",
            "yahtzee-player-rolled",
            brief_personal_key="yahtzee-you-rolled-brief",
            brief_others_key="yahtzee-player-rolled-brief",
            dice=dice_str,
            remaining=ytz_player.rolls_left,
        )

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(15, 25))  # nosec B311

        self.refresh_menus()
        # After rolling, move focus to first die toggle so player can immediately keep/unkeep
        if ytz_player.rolls_left > 0:
            self.request_menu_focus(player, "toggle_die_0")

    def _action_score(self, player: Player, action_id: str) -> None:
        """Handle scoring in a category."""
        ytz_player: YahtzeePlayer = player  # type: ignore

        category = action_id.replace("score_", "", 1)
        if category not in ALL_CATEGORIES:
            return
        if ytz_player.scores.get(category) is not None:
            return

        if self._score_category_disabled_reason(ytz_player, category):
            return

        points = self._calculate_score_for_player(ytz_player, category)

        # Yahtzee bonus: scoring a second (or further) Yahtzee awards +100
        yahtzee_bonus = False
        if is_yahtzee(ytz_player.dice.values) and ytz_player.scores.get("yahtzee") == 50:
            ytz_player.yahtzee_bonus_count += 1
            yahtzee_bonus = True

        ytz_player.scores[category] = points

        self.play_sound("game_pig/bank.ogg")

        # Announce with category name localized per recipient
        for recipient in self.players:
            user = self.get_user(recipient)
            if not user:
                continue
            cat_name = Localization.get(user.locale, CATEGORY_NAMES[category])
            is_actor = recipient.id == player.id
            key = "yahtzee-you-scored" if is_actor else "yahtzee-player-scored"
            if self._wants_brief(user):
                key = (
                    "yahtzee-you-scored-brief"
                    if is_actor
                    else "yahtzee-player-scored-brief"
                )
            if is_actor:
                user.speak_l(
                    key,
                    buffer="game",
                    points=points,
                    category=cat_name,
                )
            else:
                user.speak_l(
                    key,
                    buffer="game",
                    player=player.name,
                    points=points,
                    category=cat_name,
                )

        if yahtzee_bonus:
            self.play_sound("game_farkle/6kind.ogg")
            self._broadcast_actor_l(
                ytz_player,
                "yahtzee-you-bonus",
                "yahtzee-player-bonus",
                brief_personal_key="yahtzee-you-bonus-brief",
                brief_others_key="yahtzee-player-bonus-brief",
            )

        # Check for upper section bonus when upper section first becomes complete
        if not ytz_player.upper_bonus_awarded:
            if all(ytz_player.scores.get(cat) is not None for cat in UPPER_CATEGORIES):
                upper_total = ytz_player.get_upper_total()
                if upper_total >= 63:
                    ytz_player.upper_bonus_awarded = True
                    self.play_sound("game_pig/win.ogg")
                    self._broadcast_actor_l(
                        ytz_player,
                        "yahtzee-you-upper-bonus",
                        "yahtzee-player-upper-bonus",
                        brief_personal_key="yahtzee-you-upper-bonus-brief",
                        brief_others_key="yahtzee-player-upper-bonus-brief",
                        total=upper_total,
                    )
                else:
                    needed = 63 - upper_total
                    self._broadcast_actor_l(
                        ytz_player,
                        "yahtzee-you-upper-bonus-missed",
                        "yahtzee-player-upper-bonus-missed",
                        brief_personal_key="yahtzee-you-upper-bonus-missed-brief",
                        brief_others_key="yahtzee-player-upper-bonus-missed-brief",
                        total=upper_total,
                        needed=needed,
                    )

        self._sync_team_scores()
        self._focus_roll_after_action(ytz_player)
        self._end_turn()

    def _action_view_dice(self, player: Player, action_id: str) -> None:
        """Announce current dice values to the requesting player."""
        current = self.current_player
        if not current:
            return

        ytz_current: YahtzeePlayer = current  # type: ignore
        user = self.get_user(player)
        if not user:
            return

        if not ytz_current.dice.has_rolled:
            user.speak_l("yahtzee-not-rolled", buffer="game")
            return

        dice_str = ytz_current.dice.format_values_only()
        kept = [
            str(ytz_current.dice.get_value(i))
            for i in range(5)
            if ytz_current.dice.is_kept(i)
        ]
        # Use player-name phrasing when the requester is not the active player
        is_own = player == current
        if kept:
            kept_str = ", ".join(kept)
            key = "yahtzee-your-dice-kept" if is_own else "yahtzee-current-dice-kept"
            kw = dict(dice=dice_str, kept=kept_str)
            if not is_own:
                kw["player"] = current.name
            user.speak_l(key, buffer="game", **kw)
        else:
            key = "yahtzee-your-dice" if is_own else "yahtzee-current-dice"
            kw = dict(dice=dice_str)
            if not is_own:
                kw["player"] = current.name
            user.speak_l(key, buffer="game", **kw)

    def _action_view_scoresheet(self, player: Player, action_id: str) -> None:
        """Show a formatted scorecard to the requesting player."""
        if not isinstance(player, YahtzeePlayer) or player.is_spectator:
            return
        self._show_player_scoresheet(player, player)

    def _scorecard_player_options(self, player: Player) -> list[str]:
        return [target.id for target in self._scorecard_players()]

    def _scorecard_player_option_label(self, player: Player, option: str) -> str:
        target = self.get_player_by_id(option)
        if isinstance(target, YahtzeePlayer) and not target.is_spectator:
            return target.name
        return option

    def _scorecard_initial_selection(
        self, player: Player, options: list[str]
    ) -> str | None:
        if not options:
            return None
        if not player.is_spectator and player.id in options:
            return player.id
        if self.current_player and self.current_player.id in options:
            return self.current_player.id
        return options[0]

    def _action_view_all_scorecards(
        self, player: Player, target_id: str, action_id: str
    ) -> None:
        """Show the selected player's scorecard to the requester."""
        target = self.get_player_by_id(target_id)
        if not isinstance(target, YahtzeePlayer) or target.is_spectator:
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "yahtzee-scorecard-player-unavailable",
                    buffer="game",
                )
            return
        self._show_player_scoresheet(player, target)

    def _show_player_scoresheet(self, viewer: Player, target: YahtzeePlayer) -> None:
        target_id = target.id
        self.live_status_box(
            viewer,
            f"yahtzee_scoresheet_{target_id}",
            lambda _player, live_user: self._scoresheet_lines_for_player(
                target_id, live_user.locale
            ),
        )

    def _scoresheet_lines_for_player(self, player_id: str, locale: str) -> list[str]:
        target = self.get_player_by_id(player_id)
        if not isinstance(target, YahtzeePlayer) or target.is_spectator:
            return [Localization.get(locale, "yahtzee-scorecard-player-unavailable")]
        return self._scoresheet_lines(target, locale)

    def _scoresheet_lines(self, target: YahtzeePlayer, locale: str) -> list[str]:
        lines = [Localization.get(locale, "yahtzee-scoresheet-header", player=target.name)]
        lines.append(Localization.get(locale, "yahtzee-scoresheet-upper"))

        for cat in UPPER_CATEGORIES:
            cat_name = Localization.get(locale, CATEGORY_NAMES[cat])
            score = target.scores.get(cat)
            if score is not None:
                lines.append(f"  {cat_name}: {score}")
            else:
                lines.append(f"  {cat_name}: -")

        upper_total = target.get_upper_total()
        if target.upper_bonus_awarded:
            lines.append(
                Localization.get(
                    locale, "yahtzee-scoresheet-upper-total-bonus", total=upper_total
                )
            )
        else:
            needed = max(0, 63 - upper_total)
            lines.append(
                Localization.get(
                    locale,
                    "yahtzee-scoresheet-upper-total-needed",
                    total=upper_total,
                    needed=needed,
                )
            )

        lines.append(Localization.get(locale, "yahtzee-scoresheet-lower"))

        for cat in LOWER_CATEGORIES:
            cat_name = Localization.get(locale, CATEGORY_NAMES[cat])
            score = target.scores.get(cat)
            if score is not None:
                lines.append(f"  {cat_name}: {score}")
            else:
                lines.append(f"  {cat_name}: -")

        yahtzee_bonus_total = target.yahtzee_bonus_count * 100
        lines.append(
            Localization.get(
                locale,
                "yahtzee-scoresheet-yahtzee-bonus",
                count=target.yahtzee_bonus_count,
                total=yahtzee_bonus_total,
            )
        )

        lines.append(
            Localization.get(
                locale,
                "yahtzee-scoresheet-grand-total",
                total=target.get_total_score(),
            )
        )

        return lines

    # ==========================================================================
    # Game flow
    # ==========================================================================

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.current_game = 0
        self.games_played = 0

        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        for p in active_players:
            self._reset_player(p)
        self._sync_team_scores()

        self.play_music("game_pig/mus.ogg")
        self._start_game()

    def _reset_player(self, player: YahtzeePlayer) -> None:
        player.dice.reset()
        player.rolls_left = 3
        player.scores = {cat: None for cat in ALL_CATEGORIES}
        player.yahtzee_bonus_count = 0
        player.upper_bonus_awarded = False

    def _start_game(self) -> None:
        self.current_game += 1
        self.broadcast_l("game-round-start", buffer="game", round=self.current_game)
        self.set_turn_players(self.get_active_players())
        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not player:
            return

        ytz_player: YahtzeePlayer = player  # type: ignore
        ytz_player.dice.reset()
        ytz_player.rolls_left = 3

        self.announce_turn()

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(10, 20))  # nosec B311

        self.refresh_menus()

    def _end_turn(self) -> None:
        player = self.current_player
        if not player:
            return

        ytz_player: YahtzeePlayer = player  # type: ignore

        if ytz_player.is_scoresheet_complete():
            active = [
                p for p in self.players
                if isinstance(p, YahtzeePlayer) and not p.is_spectator
            ]
            if all(p.is_scoresheet_complete() for p in active):
                self._end_game()
                return

        BotHelper.jolt_bots(self, ticks=random.randint(15, 25))  # nosec B311

        if self.turn_index >= len(self.turn_players) - 1:
            # End of round — wrap back to first player
            self.set_turn_players(self.get_active_players())
        else:
            self.advance_turn(announce=False)

        self._start_turn()

    def _end_game(self) -> None:
        self.games_played += 1

        active_players = [
            p for p in self.players if isinstance(p, YahtzeePlayer) and not p.is_spectator
        ]
        if not active_players:
            return

        high_score = max(p.get_total_score() for p in active_players)
        winners = [p for p in active_players if p.get_total_score() == high_score]

        self.play_sound("game_pig/win.ogg")

        if len(winners) == 1:
            self._broadcast_actor_l(
                winners[0],
                "yahtzee-you-win",
                "yahtzee-player-wins",
                score=high_score,
            )
        else:
            winner_names = [w.name for w in winners]
            for p in self.players:
                user = self.get_user(p)
                if user:
                    names_str = Localization.format_list_and(user.locale, winner_names)
                    user.speak_l(
                        "yahtzee-winners-tie",
                        players=names_str,
                        score=high_score,
                        buffer="game",
                    )

        if self.games_played < self.options.num_games:
            for p in active_players:
                self._reset_player(p)
            self._sync_team_scores()
            self._start_game()
        else:
            self.finish_game()

    def _persist_result(self, result: GameResult) -> None:
        if result.custom_data.get("competitive") is False:
            return
        super()._persist_result(result)

    # ==========================================================================
    # Action set
    # ==========================================================================

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="view_dice",
                label=Localization.get(locale, "yahtzee-view-dice"),
                handler="_action_view_dice",
                is_enabled="_is_view_dice_enabled",
                is_hidden="_is_view_dice_hidden",
            )
        )
        action_set.add(
            Action(
                id="view_scoresheet",
                label=Localization.get(locale, "yahtzee-check-scoresheet"),
                handler="_action_view_scoresheet",
                is_enabled="_is_view_scoresheet_enabled",
                is_hidden="_is_view_scoresheet_hidden",
            )
        )
        action_set.add(
            Action(
                id="view_all_scorecards",
                label=Localization.get(locale, "yahtzee-check-all-scorecards"),
                handler="_action_view_all_scorecards",
                is_enabled="_is_view_all_scorecards_enabled",
                is_hidden="_is_view_all_scorecards_hidden",
                input_request=MenuInput(
                    prompt="yahtzee-select-scorecard-player",
                    options="_scorecard_player_options",
                    option_label="_scorecard_player_option_label",
                    initial_selection="_scorecard_initial_selection",
                ),
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            info_actions = [
                "view_dice",
                "view_scoresheet",
                "view_all_scorecards",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            self._order_touch_standard_actions(action_set, info_actions)
        return action_set

    # Web-specific visibility overrides for global info actions

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    # ==========================================================================
    # Results
    # ==========================================================================

    def build_game_result(self) -> GameResult:
        active_players = [
            p for p in self.players if isinstance(p, YahtzeePlayer) and not p.is_spectator
        ]

        sorted_players = sorted(
            active_players, key=lambda p: p.get_total_score(), reverse=True
        )

        final_scores = {p.name: p.get_total_score() for p in sorted_players}
        winner = sorted_players[0] if sorted_players else None
        competitive = self._is_competitive_result()

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
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": winner.get_total_score() if winner else 0,
                "final_scores": final_scores,
                "games_played": self.games_played,
                "num_games": self.options.num_games,
                "competitive": competitive,
                "solo_mode": not competitive,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(f"{i}. {name}: {points_str}")
        return lines

    # ==========================================================================
    # Tick / Bot
    # ==========================================================================

    def on_tick(self) -> None:
        super().on_tick()
        if not self.game_active:
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: YahtzeePlayer) -> str | None:
        return yahtzee_bot_think(
            self,
            player,
            calculate_score=lambda _dice, category: self._calculate_score_for_player(
                player, category
            ),
            scoreable_categories=self._get_scoreable_categories,
            all_categories=ALL_CATEGORIES,
            upper_categories=UPPER_CATEGORIES,
        )


# =============================================================================
# Dynamic scoring category methods
# =============================================================================
# Generates _is_score_<cat>_enabled / _hidden / _get_label for every category.

def _make_score_enabled(cat: str):
    def method(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if player.is_spectator:
            return "action-spectator"
        if not player.dice.has_rolled:
            return "yahtzee-roll-first"
        if cat not in player.get_open_categories():
            return "yahtzee-category-filled"
        if not isinstance(player, YahtzeePlayer):
            return "action-not-available"
        return self._score_category_disabled_reason(player, cat)
    return method


def _make_score_hidden(cat: str):
    def method(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if not player.dice.has_rolled:
            return Visibility.HIDDEN
        if cat not in player.get_open_categories():
            return Visibility.HIDDEN
        return Visibility.VISIBLE
    return method


def _make_score_label(cat: str):
    def method(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        cat_name = Localization.get(locale, CATEGORY_NAMES[cat])
        if player.dice.has_rolled:
            points = (
                self._calculate_score_for_player(player, cat)
                if isinstance(player, YahtzeePlayer)
                else calculate_score(player.dice.values, cat)
            )
            key = f"yahtzee-score-{cat.replace('_', '-')}"
            return Localization.get(locale, key, points=points)
        return cat_name
    return method


for _cat in ALL_CATEGORIES:
    setattr(YahtzeeGame, f"_is_score_{_cat}_enabled", _make_score_enabled(_cat))
    setattr(YahtzeeGame, f"_is_score_{_cat}_hidden", _make_score_hidden(_cat))
    setattr(YahtzeeGame, f"_get_score_{_cat}_label", _make_score_label(_cat))
