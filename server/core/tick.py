"""Tick scheduler for game updates."""

import asyncio
import logging
from typing import Callable


class TickScheduler:
    """
    Schedules game ticks at a fixed interval (50ms).

    The tick callback is called synchronously within the async context.
    This keeps game logic simple while allowing async network I/O.
    """

    TICK_INTERVAL_MS = 50
    TICK_INTERVAL_S = TICK_INTERVAL_MS / 1000.0

    def __init__(self, on_tick: Callable[[], None]):
        self._on_tick = on_tick
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the tick scheduler."""
        self._running = True
        self._task = asyncio.create_task(self._tick_loop())

    async def stop(self) -> None:
        """Stop the tick scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _tick_loop(self) -> None:
        """Main tick loop."""
        while self._running:
            try:
                # Call tick callback synchronously
                self._on_tick()
            except Exception as e:
                logging.error(f"Error in tick: {e}", exc_info=True)

            # Sleep for tick interval
            await asyncio.sleep(self.TICK_INTERVAL_S)
