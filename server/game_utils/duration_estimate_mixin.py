"""Mixin providing game duration estimation via simulation."""

import subprocess
import sys
import json as json_module
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..games.base import Player
    from ..users.base import User


class DurationEstimateMixin:
    """Mixin providing game duration estimation by running CLI simulations.

    Expects on the Game class:
        - self._estimate_threads: list
        - self._estimate_results: list
        - self._estimate_errors: list
        - self._estimate_running: bool
        - self._estimate_lock: threading.Lock
        - self.players: list[Player]
        - self.get_user(player) -> User | None
        - self.broadcast_l() / self.broadcast()
        - self.get_type() -> str
        - self.get_min_players() -> int
        - self.TICKS_PER_SECOND: int (inherited from GameSoundMixin or defined locally)
    """

    # Constants
    NUM_ESTIMATE_SIMULATIONS = 10  # Number of simulations to run for estimation
    HUMAN_SPEED_MULTIPLIER = 2  # How much slower humans are than bots (override per game)
    TICKS_PER_SECOND = 20  # 50ms per tick (may be overridden by GameSoundMixin)

    def _action_estimate_duration(self, player: "Player", action_id: str) -> None:
        """Start duration estimation by spawning CLI simulation threads."""
        if self._estimate_running:
            user = self.get_user(player)
            if user:
                user.speak_l("estimate-already-running")
            return

        # Build the options string for CLI
        options_args = []
        if hasattr(self, "options"):
            for field_name in self.options.__dataclass_fields__:
                value = getattr(self.options, field_name)
                options_args.extend(["-o", f"{field_name}={value}"])

        # Determine number of bots (use current player count, minimum 2)
        num_bots = max(len([p for p in self.players if not p.is_spectator]), self.get_min_players())

        # Build CLI command
        cli_path = Path(__file__).parent.parent / "cli.py"
        base_cmd = [
            sys.executable, str(cli_path), "simulate",
            self.get_type(),
            "--bots", str(num_bots),
            "--json", "--quiet"
        ] + options_args

        # Reset results
        self._estimate_results = []
        self._estimate_errors = []
        self._estimate_threads = []

        # Spawn simulation threads
        def run_simulation():
            try:
                result = subprocess.run(
                    base_cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout per simulation
                )
                if result.returncode == 0 and result.stdout:
                    data = json_module.loads(result.stdout)
                    if "ticks" in data and not data.get("timed_out", False):
                        with self._estimate_lock:
                            self._estimate_results.append(data["ticks"])
                elif result.stderr:
                    with self._estimate_lock:
                        self._estimate_errors.append(result.stderr.strip()[:200])
            except Exception as e:
                with self._estimate_lock:
                    self._estimate_errors.append(str(e)[:200])

        for _ in range(self.NUM_ESTIMATE_SIMULATIONS):
            thread = threading.Thread(target=run_simulation, daemon=True)
            thread.start()
            self._estimate_threads.append(thread)

        if self._estimate_threads:
            self._estimate_running = True
            self.broadcast_l("estimate-computing")
        else:
            self.broadcast_l("estimate-error")

    def check_estimate_completion(self) -> None:
        """Check if duration estimation simulations have completed.

        Called automatically from on_tick().
        """
        if not self._estimate_running or not self._estimate_threads:
            return

        # Check if all threads have completed
        all_done = all(not t.is_alive() for t in self._estimate_threads)
        if not all_done:
            return

        # Get results (already collected by threads)
        with self._estimate_lock:
            tick_counts = list(self._estimate_results)
            errors = list(self._estimate_errors)

        # Clean up
        self._estimate_threads = []
        self._estimate_results = []
        self._estimate_errors = []
        self._estimate_running = False

        # Calculate and announce result
        if tick_counts:
            # Calculate statistics
            avg_ticks = sum(tick_counts) / len(tick_counts)
            std_dev_ticks = self._calculate_std_dev(tick_counts, avg_ticks)
            outliers = self._detect_outliers(tick_counts)

            # Format times
            bot_time = self._format_duration(avg_ticks)
            std_dev = self._format_duration(std_dev_ticks)
            human_time = self._format_duration(avg_ticks * self.HUMAN_SPEED_MULTIPLIER)

            # Format outlier info
            if outliers:
                outlier_info = f"{len(outliers)} outlier{'s' if len(outliers) > 1 else ''} removed. "
            else:
                outlier_info = ""

            self.broadcast_l(
                "estimate-result",
                bot_time=bot_time,
                std_dev=std_dev,
                outlier_info=outlier_info,
                human_time=human_time,
            )
        else:
            if errors:
                # Show the first error for debugging
                self.broadcast(f"Estimation failed: {errors[0][:200]}")
            else:
                self.broadcast_l("estimate-error")

    def _calculate_std_dev(self, values: list[int], mean: float) -> float:
        """Calculate standard deviation of a list of values."""
        if len(values) < 2:
            return 0.0
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def _detect_outliers(self, values: list[int]) -> list[int]:
        """Detect outliers using IQR method. Returns list of outlier values."""
        if len(values) < 4:
            return []

        sorted_vals = sorted(values)
        n = len(sorted_vals)
        q1 = sorted_vals[n // 4]
        q3 = sorted_vals[(3 * n) // 4]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        return [v for v in values if v < lower_bound or v > upper_bound]

    def _format_duration(self, ticks: float) -> str:
        """Format a tick count as a human-readable duration string.

        Args:
            ticks: Number of game ticks (50ms each).

        Returns:
            Formatted string like "1:23:45" or "5:30" or "45 seconds".
        """
        # Convert ticks to seconds (50ms per tick = 20 ticks per second)
        total_seconds = int(ticks / self.TICKS_PER_SECOND)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        elif minutes > 0:
            return f"{minutes}:{seconds:02d}"
        else:
            return f"{seconds} seconds"
