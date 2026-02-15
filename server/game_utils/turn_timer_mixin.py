"""Mixin for turn timer logic in games."""

from typing import Any, Protocol

from .poker_timer import PokerTurnTimer


class TurnTimerGameProtocol(Protocol):
    """Protocol for games using TurnTimerMixin."""
    timer: PokerTurnTimer
    options: Any  # Must have turn_timer attribute
    
    def play_sound(self, sound: str) -> None: ...
    def _on_turn_timeout(self) -> None: ...


class TurnTimerMixin:
    """Mixin for managing turn timers.
    
    Requires the class to have:
    - self.timer: PokerTurnTimer
    - self.options: object with 'turn_timer' attribute (str)
    - self.play_sound(sound: str)
    - _on_turn_timeout() -> implement this!
    """

    # _timer_warning_played is initialized in start_turn_timer or __post_init__ of subclass

    def start_turn_timer(self) -> None:
        """Start the turn timer based on game options."""
        # Reset warning flag
        self._timer_warning_played = False
        
        try:
            # Handle both string "30" and int 30
            seconds = int(self.options.turn_timer)
        except (ValueError, AttributeError):
            seconds = 0
            
        if seconds <= 0:
            self.timer.clear()
            return

        self.timer.start(seconds)

    def stop_turn_timer(self) -> None:
        """Stop/clear the turn timer."""
        self.timer.clear()
        self._timer_warning_played = False

    def on_tick_turn_timer(self) -> None:
        """Called every tick to update timer and check for timeout."""
        if self.timer.tick():
            self._on_turn_timeout()
        
        self._maybe_play_timer_warning()

    def _maybe_play_timer_warning(self) -> None:
        """Play warning sound if time is running out."""
        if self._timer_warning_played:
            return

        # Check if actual timer is active/has meaningful duration
        try:
            total_seconds = int(self.options.turn_timer)
        except (ValueError, AttributeError):
            total_seconds = 0
            
        # Don't warn for very short timers or unlimited
        if total_seconds < 20:
            return

        remaining = self.timer.seconds_remaining()
        if remaining == 5:
            self._timer_warning_played = True
            # Use a sound that exists in common path or let game specific?
            # CrazyEights uses: game_crazyeights/fivesec.ogg
            # Holdem/Draw don't seem to have a warning sound implemented in the snippet I saw?
            # Let's check CrazyEights usage. It uses game_crazyeights/fivesec.ogg.
            # Holdem snippet didn't show `_maybe_play_timer_warning`.
            # I will try to play a generic sound or game specific if overridden.
            # For now, I'll assume we can use the crazyeights one or I should let the game override the sound name?
            # Actually, to be safe, I'll defer sound to a helper or just use the one from CrazyEights if available,
            # or maybe "game_pig/turn.ogg" is not right.
            # Let's define a method for the sound name.
            
            self.play_sound(self._get_timer_warning_sound())

    def _get_timer_warning_sound(self) -> str:
        """Get the warning sound file path. Warning: Default assumes CrazyEights asset."""
        return "game_crazyeights/fivesec.ogg"

    def _on_turn_timeout(self) -> None:
        """Hook called when timer expires. Must be implemented by subclass."""
        raise NotImplementedError
