"""Bot helper for managing AI player actions.

This is a stateless helper that operates on serialized Player fields:
- player.bot_think_ticks: Ticks until bot can act
- player.bot_pending_action: Action to execute when ready
- player.bot_target: Game-specific target value
"""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..games.base import Game, Player


class BotHelper:
    """
    Stateless helper for managing bot AI in games.

    All bot state is stored in Player fields for serialization.
    This class just provides utility methods for manipulating that state.

    Usage:
        # In game on_tick:
        BotHelper.on_tick(self)

        # Implement bot_think in your game:
        def bot_think(self, player: Player) -> str | None:
            return "roll"

        # When something happens that should make bots pause:
        BotHelper.jolt_bots(game, ticks=10)
    """

    # Default think ticks when not specified
    DEFAULT_THINK_TICKS = 5

    @staticmethod
    def jolt_bots(
        game: "Game", ticks: int | None = None, players: list["Player"] | None = None
    ) -> None:
        """
        Make bots pause before they can act.

        Args:
            game: The game instance.
            ticks: How many ticks to pause. Uses DEFAULT_THINK_TICKS if None.
            players: Specific players to jolt. All bots in game if None.
        """
        pause_ticks = ticks if ticks is not None else BotHelper.DEFAULT_THINK_TICKS

        target_players = players if players is not None else game.players
        for player in target_players:
            if player.is_bot:
                player.bot_think_ticks = pause_ticks
                player.bot_pending_action = None

    @staticmethod
    def jolt_bot(player: "Player", ticks: int | None = None) -> None:
        """Jolt a single bot."""
        if player.is_bot:
            pause_ticks = ticks if ticks is not None else BotHelper.DEFAULT_THINK_TICKS
            player.bot_think_ticks = pause_ticks
            player.bot_pending_action = None

    @staticmethod
    def set_target(player: "Player", target: int | None) -> None:
        """Set a game-specific target for a bot."""
        player.bot_target = target

    @staticmethod
    def get_target(player: "Player") -> int | None:
        """Get the game-specific target for a bot."""
        return player.bot_target

    @staticmethod
    def process_bot_action(
        bot: "Player",
        think_fn: Callable[[], str | None],
        execute_fn: Callable[[str], None],
    ) -> bool:
        """
        Process a single bot's action cycle: think -> pending -> execute.

        This encapsulates the common pattern for bot action handling:
        1. Count down think ticks if bot is still "thinking"
        2. Execute pending action if one exists
        3. Otherwise, call think function to decide what to do

        Args:
            bot: The bot player to process.
            think_fn: A callable that returns an action_id (or None if no action).
            execute_fn: A callable that takes an action_id and executes it.

        Returns:
            True if the bot took an action (executed or set pending), False if still thinking.

        Example usage:
            BotHelper.process_bot_action(
                bot=player,
                think_fn=lambda: self.bot_think(player),
                execute_fn=lambda action_id: self.execute_action(player, action_id),
            )
        """
        # Count down thinking time
        if bot.bot_think_ticks > 0:
            bot.bot_think_ticks -= 1
            return False

        # Execute pending action if we have one
        if bot.bot_pending_action:
            action_id = bot.bot_pending_action
            bot.bot_pending_action = None
            execute_fn(action_id)
            return True

        # Ask what this bot should do
        action_id = think_fn()
        if action_id:
            bot.bot_pending_action = action_id
            return True

        return False

    @staticmethod
    def on_tick(game: "Game", debug: bool = False) -> None:
        """
        Process bot actions for a tick.

        Call this from your game's on_tick() method.
        """
        # Only process if game is active and playing
        if not game.game_active or game.status != "playing":
            return

        # Get current player - only they can act in turn-based games
        current = game.current_player
        if debug:
            print(
                f"[BotHelper] current={current.name if current else None}, is_bot={current.is_bot if current else None}, turn_index={game.turn_index}"
            )
        if not current or not current.is_bot:
            return

        # Count down thinking time
        if current.bot_think_ticks > 0:
            current.bot_think_ticks -= 1
            return

        # Execute pending action if we have one
        if current.bot_pending_action:
            action_id = current.bot_pending_action
            current.bot_pending_action = None
            game.execute_action(current, action_id)
            return

        # Ask game what this bot should do
        if hasattr(game, "bot_think"):
            action_id = game.bot_think(current)
            if action_id:
                current.bot_pending_action = action_id
