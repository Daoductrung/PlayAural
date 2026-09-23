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
        if self._task is not None and not self._task.done():
            return
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
            finally:
                self._task = None

    async def _tick_loop(self) -> None:
        """Main tick loop."""
        loop = asyncio.get_running_loop()
        deadline = loop.time()
        while self._running:
            try:
                # Call tick callback synchronously
                self._on_tick()
            except Exception as e:
                logging.error(f"Error in tick: {e}", exc_info=True)

            # Sleep until the next deadline rather than for a fixed interval,
            # so ordinary tick work and coarse timers (about 15 ms on Windows)
            # do not accumulate. If the event loop or callback misses a whole
            # deadline, skip that elapsed slot instead of replaying it with
            # back-to-back ticks: game sequences treat every tick as 50 ms and
            # must never run faster merely because a busy server fell behind.
            deadline += self.TICK_INTERVAL_S
            now = loop.time()
            if deadline <= now:
                deadline = now + self.TICK_INTERVAL_S
            await asyncio.sleep(max(0.0, deadline - now))
