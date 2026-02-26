"""
Mixin for dice-based games that use the DiceSet keep/lock mechanics.

Provides shared functionality for games like Threes and Yahtzee that have
dice toggling via 1-5/1-6 keys depending on user preferences.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .actions import Action, ActionSet, Visibility
from ..ui.keybinds import KeybindState
from ..users.preferences import DiceKeepingStyle

if TYPE_CHECKING:
    from ..games.base import Player


class DiceGameMixin:
    """
    Mixin providing dice toggle actions for games using DiceSet.

    Supports two dice keeping styles:
    - Dice indexes: Keys 1-5 toggle dice by index
    - Dice values: Keys 1-6 reroll by face value, shift+1-6 keep by value

    Expects the game class to have:
    - self.get_user(player) -> User
    - self.get_action_set(player, name) -> ActionSet
    - self.rebuild_player_menu(player)
    - Player objects with a `dice: DiceSet` attribute

    Games must implement these methods for dice action state:
    - _is_dice_toggle_enabled(self, player, die_index) -> str | None
    - _is_dice_toggle_hidden(self, player, die_index) -> Visibility
    - _get_dice_toggle_label(self, player, die_index) -> str

    Usage:
        class MyGame(Game, DiceGameMixin):
            def create_turn_action_set(self, player):
                action_set = ActionSet(name="turn")
                self.add_dice_toggle_actions(action_set)
                # ... add other actions
                return action_set

            def setup_keybinds(self):
                super().setup_keybinds()
                self.setup_dice_keybinds()
    """

    def add_dice_toggle_actions(self, action_set: ActionSet, num_dice: int = 5) -> None:
        """
        Add dice toggle actions to an action set.

        Adds both index-based toggle actions (for menu items) and
        keybind-triggered actions that respect user preferences.

        Args:
            action_set: The ActionSet to add actions to.
            num_dice: Number of dice (default 5).
        """
        # Menu item actions - always toggle by index
        for i in range(num_dice):
            action_set.add(
                Action(
                    id=f"toggle_die_{i}",
                    label=f"Die {i + 1}",
                    handler="_action_toggle_die",
                    is_enabled=f"_is_toggle_die_{i}_enabled",
                    is_hidden=f"_is_toggle_die_{i}_hidden",
                    get_label=f"_get_toggle_die_{i}_label",
                    show_in_actions_menu=False,
                )
            )

        # Keybind actions for keys 1-6 (respects user preference)
        # These are hidden but enabled - they're only triggered via keybinds
        for v in range(1, 7):
            action_set.add(
                Action(
                    id=f"dice_key_{v}",
                    label=f"Dice key {v}",
                    handler="_action_dice_key",
                    is_enabled="_is_dice_key_enabled",
                    is_hidden="_is_dice_key_hidden",
                    get_label="_get_dice_key_label",
                    show_in_actions_menu=False,
                )
            )
            # Shift+key actions for dice values style keeping
            action_set.add(
                Action(
                    id=f"dice_unkeep_{v}",
                    label=f"Unkeep {v}",
                    handler="_action_dice_unkeep",
                    is_enabled="_is_dice_unkeep_enabled",
                    is_hidden="_is_dice_key_hidden",
                    get_label="_get_dice_unkeep_label",
                    show_in_actions_menu=False,
                )
            )

    def setup_dice_keybinds(self, num_dice: int = 5) -> None:
        """
        Set up keybinds for dice toggling.

        Defines keybinds for both styles:
        - Keys 1-6 trigger dice_key_X (style determines behavior)
        - Shift+1-6 trigger dice_unkeep_X (dice values style only)

        Args:
            num_dice: Number of dice (default 5).
        """
        # Keys 1-6 for keeping/toggling
        for v in range(1, 7):
            self.define_keybind(
                str(v),
                f"Dice key {v}",
                [f"dice_key_{v}"],
                state=KeybindState.ACTIVE,
            )
            # Shift+1-6 for unkeeping (Quentin C style)
            self.define_keybind(
                f"shift+{v}",
                f"Unkeep dice {v}",
                [f"dice_unkeep_{v}"],
                state=KeybindState.ACTIVE,
            )

    # ==========================================================================
    # Default is_enabled / is_hidden implementations (games can override)
    # ==========================================================================

    def _is_dice_key_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        """Enable dice keybind actions based on game state and keeping style."""
        if self.status != "playing":
            return "action-not-playing"
        if not action_id:
            return None
        user = self.get_user(player)
        style = user.preferences.dice_keeping_style if user else DiceKeepingStyle.PlayAural
        try:
            key_num = int(action_id.split("_")[-1])
        except ValueError:
            return "action-not-available"
        if hasattr(player, "dice"):
            if style == DiceKeepingStyle.QUENTIN_C:
                if key_num > player.dice.sides:
                    return "action-not-available"
            elif key_num > player.dice.num_dice:
                return "action-not-available"
        if hasattr(self, "_is_dice_toggle_enabled"):
            if style == DiceKeepingStyle.PlayAural:
                die_index = key_num - 1
            else:
                die_index = 0
            if hasattr(player, "dice") and die_index >= player.dice.num_dice:
                return "action-not-available"
            toggle_reason = self._is_dice_toggle_enabled(player, die_index)
            if toggle_reason is not None:
                return "action-not-available"
        if style == DiceKeepingStyle.QUENTIN_C and hasattr(player, "dice"):
            if not self._has_kept_value(player, key_num):
                return "action-not-available"
        return None

    def _is_dice_unkeep_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        """Only enable unkeep keybinds for dice values style."""
        if self.status != "playing":
            return "action-not-playing"
        user = self.get_user(player)
        style = user.preferences.dice_keeping_style if user else DiceKeepingStyle.PlayAural
        if style != DiceKeepingStyle.QUENTIN_C:
            return "action-not-available"
        if action_id:
            try:
                key_num = int(action_id.split("_")[-1])
            except ValueError:
                return "action-not-available"
            if hasattr(player, "dice") and key_num > player.dice.sides:
                return "action-not-available"
        if hasattr(self, "_is_dice_toggle_enabled"):
            toggle_reason = self._is_dice_toggle_enabled(player, 0)
            if toggle_reason is not None:
                return "action-not-available"
        if hasattr(player, "dice"):
            if not self._has_unkept_value(player, key_num):
                return "action-not-available"
        return None

    def _get_dice_key_label(self, player: Player, action_id: str) -> str:
        """Label for dice_key actions in the actions menu."""
        try:
            key_num = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        user = self.get_user(player)
        style = user.preferences.dice_keeping_style if user else DiceKeepingStyle.PlayAural
        if style == DiceKeepingStyle.PlayAural and hasattr(player, "dice"):
            die_index = key_num - 1
            if die_index >= player.dice.num_dice:
                return f"Keep die {key_num}"
            if player.dice.is_kept(die_index):
                return f"Reroll die {key_num}"
            return f"Keep die {key_num}"
        return f"Reroll {key_num}"

    def _get_dice_unkeep_label(self, player: Player, action_id: str) -> str:
        """Label for dice_unkeep actions in the actions menu."""
        try:
            key_num = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        return f"Keep {key_num}"

    def _apply_dice_values_defaults(self, player: Player) -> None:
        """In dice values style, default to keeping all dice after a roll."""
        user = self.get_user(player)
        style = user.preferences.dice_keeping_style if user else DiceKeepingStyle.PlayAural
        if style != DiceKeepingStyle.QUENTIN_C:
            return
        if not hasattr(player, "dice"):
            return
        dice = player.dice
        if not dice.has_rolled:
            return
        dice.kept = list(range(dice.num_dice))

    def _has_kept_value(self, player: Player, value: int) -> bool:
        if not hasattr(player, "dice"):
            return False
        dice = player.dice
        if not dice.has_rolled:
            return False
        for i in range(dice.num_dice):
            if dice.is_locked(i) or not dice.is_kept(i):
                continue
            if dice.get_value(i) == value:
                return True
        return False

    def _has_unkept_value(self, player: Player, value: int) -> bool:
        if not hasattr(player, "dice"):
            return False
        dice = player.dice
        if not dice.has_rolled:
            return False
        for i in range(dice.num_dice):
            if dice.is_locked(i) or dice.is_kept(i):
                continue
            if dice.get_value(i) == value:
                return True
        return False

    def _is_dice_key_hidden(self, player: Player) -> Visibility:
        """Dice keybind actions are always hidden (keybind only)."""
        return Visibility.HIDDEN

    # Per-die enabled/hidden/label methods - delegate to generic versions
    # These use action_id to extract die index, so they work for any number of dice
    # Games must implement _is_dice_toggle_enabled, _is_dice_toggle_hidden, _get_dice_toggle_label

    def _is_toggle_die_0_enabled(self, player: Player, *, action_id: str = None) -> str | None:
        die_index = int(action_id.split("_")[-1]) if action_id else 0
        return self._is_dice_toggle_enabled(player, die_index)

    def _is_toggle_die_1_enabled(self, player: Player, *, action_id: str = None) -> str | None:
        die_index = int(action_id.split("_")[-1]) if action_id else 1
        return self._is_dice_toggle_enabled(player, die_index)

    def _is_toggle_die_2_enabled(self, player: Player, *, action_id: str = None) -> str | None:
        die_index = int(action_id.split("_")[-1]) if action_id else 2
        return self._is_dice_toggle_enabled(player, die_index)

    def _is_toggle_die_3_enabled(self, player: Player, *, action_id: str = None) -> str | None:
        die_index = int(action_id.split("_")[-1]) if action_id else 3
        return self._is_dice_toggle_enabled(player, die_index)

    def _is_toggle_die_4_enabled(self, player: Player, *, action_id: str = None) -> str | None:
        die_index = int(action_id.split("_")[-1]) if action_id else 4
        return self._is_dice_toggle_enabled(player, die_index)

    def _is_toggle_die_5_enabled(self, player: Player, *, action_id: str = None) -> str | None:
        die_index = int(action_id.split("_")[-1]) if action_id else 5
        return self._is_dice_toggle_enabled(player, die_index)

    def _is_toggle_die_0_hidden(self, player: Player, *, action_id: str = None) -> Visibility:
        die_index = int(action_id.split("_")[-1]) if action_id else 0
        return self._is_dice_toggle_hidden(player, die_index)

    def _is_toggle_die_1_hidden(self, player: Player, *, action_id: str = None) -> Visibility:
        die_index = int(action_id.split("_")[-1]) if action_id else 1
        return self._is_dice_toggle_hidden(player, die_index)

    def _is_toggle_die_2_hidden(self, player: Player, *, action_id: str = None) -> Visibility:
        die_index = int(action_id.split("_")[-1]) if action_id else 2
        return self._is_dice_toggle_hidden(player, die_index)

    def _is_toggle_die_3_hidden(self, player: Player, *, action_id: str = None) -> Visibility:
        die_index = int(action_id.split("_")[-1]) if action_id else 3
        return self._is_dice_toggle_hidden(player, die_index)

    def _is_toggle_die_4_hidden(self, player: Player, *, action_id: str = None) -> Visibility:
        die_index = int(action_id.split("_")[-1]) if action_id else 4
        return self._is_dice_toggle_hidden(player, die_index)

    def _is_toggle_die_5_hidden(self, player: Player, *, action_id: str = None) -> Visibility:
        die_index = int(action_id.split("_")[-1]) if action_id else 5
        return self._is_dice_toggle_hidden(player, die_index)

    def _get_toggle_die_0_label(self, player: Player, action_id: str) -> str:
        die_index = int(action_id.split("_")[-1])
        return self._get_dice_toggle_label(player, die_index)

    def _get_toggle_die_1_label(self, player: Player, action_id: str) -> str:
        die_index = int(action_id.split("_")[-1])
        return self._get_dice_toggle_label(player, die_index)

    def _get_toggle_die_2_label(self, player: Player, action_id: str) -> str:
        die_index = int(action_id.split("_")[-1])
        return self._get_dice_toggle_label(player, die_index)

    def _get_toggle_die_3_label(self, player: Player, action_id: str) -> str:
        die_index = int(action_id.split("_")[-1])
        return self._get_dice_toggle_label(player, die_index)

    def _get_toggle_die_4_label(self, player: Player, action_id: str) -> str:
        die_index = int(action_id.split("_")[-1])
        return self._get_dice_toggle_label(player, die_index)

    def _get_toggle_die_5_label(self, player: Player, action_id: str) -> str:
        die_index = int(action_id.split("_")[-1])
        return self._get_dice_toggle_label(player, die_index)

    # Default implementations - games should override these
    def _is_dice_toggle_enabled(self, player: Player, die_index: int) -> str | None:
        """Check if toggling die at index is enabled. Override in game class."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if not hasattr(player, "dice"):
            return "dice-no-dice"
        if not player.dice.has_rolled:
            return "dice-not-rolled"
        if player.dice.is_locked(die_index):
            return "dice-locked"
        return None

    def _is_dice_toggle_hidden(self, player: Player, die_index: int) -> Visibility:
        """Check if die toggle action is hidden. Override in game class."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if not hasattr(player, "dice"):
            return Visibility.HIDDEN
        if not player.dice.has_rolled:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_dice_toggle_label(self, player: Player, die_index: int) -> str:
        """Get label for die toggle action. Override in game class."""
        if not hasattr(player, "dice"):
            return f"Die {die_index + 1}"
        
        # Determine locale
        user = self.get_user(player)
        locale = user.locale if user else "en"

        die_val = player.dice.get_value(die_index)
        if die_val is None:
            return f"Die {die_index + 1}"
        if player.dice.is_locked(die_index):
             from ..messages.localization import Localization
             return Localization.get(locale, "dice-status-label-locked", value=die_val)
        if player.dice.is_kept(die_index):
             from ..messages.localization import Localization
             return Localization.get(locale, "dice-status-label-kept", value=die_val)
        return str(die_val)

    # Single toggle handler for all dice (extracts index from action ID)
    def _action_toggle_die(self, player: Player, action_id: str) -> None:
        """Handle toggle_die_X action by extracting die index from action ID."""
        # Extract die index from action ID (e.g., "toggle_die_0" -> 0)
        die_index = int(action_id.split("_")[-1])
        self._toggle_die(player, die_index)

    # Single keybind handler for dice keys (extracts key number from action ID)
    def _action_dice_key(self, player: Player, action_id: str) -> None:
        """Handle dice_key_X action by extracting key number from action ID."""
        # Extract key number from action ID (e.g., "dice_key_1" -> 1)
        key_num = int(action_id.split("_")[-1])
        self._handle_dice_key(player, key_num)

    # Single handler for shift+key unkeeping (extracts value from action ID)
    def _action_dice_unkeep(self, player: Player, action_id: str) -> None:
        """Handle dice_unkeep_X action by extracting value from action ID."""
        # Extract value from action ID (e.g., "dice_unkeep_1" -> 1)
        value = int(action_id.split("_")[-1])
        self._handle_dice_unkeep(player, value)

    def _handle_dice_key(self, player: Player, key_num: int) -> None:
        """
        Handle a dice key press (1-6).

        Behavior depends on user's dice keeping style preference:
        - Dice indexes: Toggle die at index (key_num - 1)
        - Dice values: Reroll first kept die with face value key_num
        """
        user = self.get_user(player)
        if not user:
            return

        style = user.preferences.dice_keeping_style

        if style == DiceKeepingStyle.PlayAural:
            # Toggle by index - check if die index is valid
            die_index = key_num - 1
            if hasattr(player, "dice") and die_index < player.dice.num_dice:
                self._toggle_die(player, die_index)
        else:
            # Dice values style: reroll by face value
            self._unkeep_by_value(player, key_num)

    def _handle_dice_unkeep(self, player: Player, value: int) -> None:
        """
        Handle shift+key press for unkeeping by value.

        Only works in dice values style. Silent in dice indexes style.
        """
        user = self.get_user(player)
        if not user:
            return

        style = user.preferences.dice_keeping_style

        if style == DiceKeepingStyle.QUENTIN_C:
            self._keep_by_value(player, value)
        # Silent in dice indexes style

    def _toggle_die(self, player: Player, die_index: int) -> None:
        """
        Toggle keeping a die by index.

        Handles the common logic for toggling dice in games using DiceSet.
        Speaks the appropriate message (keeping/rerolling/locked).
        """
        if not hasattr(player, "dice"):
            return

        user = self.get_user(player)
        result = player.dice.toggle_keep(die_index)

        if result is None:
            # Die is locked
            if user:
                user.speak_l("dice-locked")
            return

        die_val = player.dice.get_value(die_index)
        if result:
            # Now kept
            if user:
                user.speak_l("dice-keeping", value=die_val)
        else:
            # Now unkept
            if user:
                user.speak_l("dice-rerolling", value=die_val)

        self.rebuild_player_menu(player)

    def _keep_by_value(self, player: Player, value: int) -> None:
        """
        Keep the first unkept die with the given face value.

        Used in dice values style. Silent if no unkept die with that value exists.
        """
        if not hasattr(player, "dice"):
            return

        user = self.get_user(player)
        dice = player.dice

        # Find first unkept, unlocked die with this value
        for i in range(dice.num_dice):
            if not dice.is_locked(i) and not dice.is_kept(i):
                if dice.get_value(i) == value:
                    dice.keep(i)
                    if user:
                        user.speak_l("dice-keeping", value=value)
                    self.rebuild_player_menu(player)
                    return

        # No matching die found - silent

    def _unkeep_by_value(self, player: Player, value: int) -> None:
        """
        Unkeep the first kept die with the given face value.

        Used in dice values style. Silent if no kept die with that value exists.
        """
        if not hasattr(player, "dice"):
            return

        user = self.get_user(player)
        dice = player.dice

        # Find first kept (but not locked) die with this value
        for i in range(dice.num_dice):
            if dice.is_kept(i) and not dice.is_locked(i):
                if dice.get_value(i) == value:
                    dice.unkeep(i)
                    if user:
                        user.speak_l("dice-rerolling", value=value)
                    self.rebuild_player_menu(player)
                    return

        # No matching die found - silent
