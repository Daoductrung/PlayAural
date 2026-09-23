"""Regressions found by reviewing the v3 audio protocol against real numbers."""

import asyncio
import random
import time

import pytest

from ..audio import AudioGainAutomation, AudioMotion, DistanceAttenuation
from ..core.tick import TickScheduler
from ..games.pig.game import PigGame
from ..tables.manager import TableManager
from ..users.test_user import MockUser


def test_motion_to_the_coordinate_limit_never_leaves_the_valid_range() -> None:
    # -399.389 + (1000 - -399.389) * 1.0 is 1000.0000000000001 in floats.
    motion = AudioMotion((-399.389, 0, 0), (1000, 0, 0), 100, 100)
    assert motion.position_at() == (1000.0, 0.0, 0.0)

    generator = random.Random(3)
    for _ in range(2000):
        origin = tuple(round(generator.uniform(-1000, 1000), 3) for _ in range(3))
        destination = tuple(generator.choice((-1000, 1000)) for _ in range(3))
        motion = AudioMotion(origin, destination, 1000)
        for elapsed in (0, 1, 333, 999, 1000):
            motion.position_at(elapsed)
        assert motion.position_at(1000) == tuple(map(float, destination))


def test_gain_automation_lands_exactly_and_stays_between_its_endpoints() -> None:
    generator = random.Random(5)
    for _ in range(2000):
        origin = round(generator.random(), 3)
        destination = round(generator.random(), 3)
        automation = AudioGainAutomation(origin, destination, 1000, easing="ease-out")
        assert automation.gain_at(1000) == destination
        for elapsed in (0, 1, 500, 999):
            assert min(origin, destination) <= automation.gain_at(elapsed) <= max(
                origin, destination
            )


def test_a_moving_source_at_the_limit_does_not_stop_the_game_tick() -> None:
    game = PigGame()
    alice = MockUser("Alice")
    game.add_player("Alice", alice)
    game.status = "playing"
    handle = game.play_sound(
        "engine.ogg", loop=True, handle="car", persist=True, position=(-399.389, 0, 0)
    )
    game.move_sound(handle, (1000, 0, 0), 100)

    for _ in range(4):
        game.on_tick()

    state = next(iter(game.active_audio.values()))
    assert state.position == (1000.0, 0.0, 0.0)
    assert state.motion is None


@pytest.mark.parametrize(
    "distances",
    [
        {"reference_distance": 4e-7, "max_distance": 10},
        {"reference_distance": 1.0000001, "max_distance": 1.0000002},
    ],
)
def test_attenuation_is_validated_as_clients_will_receive_it(distances) -> None:
    # Both rounded to a degenerate curve that then divided by zero.
    with pytest.raises(ValueError):
        DistanceAttenuation(
            model="inverse", rolloff_factor=1, min_gain=0, max_gain=1, **distances
        )


def test_finite_effects_do_not_accumulate_in_the_ownership_mirror() -> None:
    user = MockUser("Alice")
    for index in range(50):
        user.play_sound("click.ogg", handle=f"click:{index}")
    assert not user._runtime_audio_states

    user.play_sound("engine.ogg", loop=True, handle="engine")
    assert user.has_managed_audio("sfx", handle="engine")
    # A finite effect reusing the handle still replaces the loop on the client.
    user.play_sound("click.ogg", handle="engine")
    assert not user.has_managed_audio("sfx", handle="engine")


def test_one_failing_table_does_not_cost_the_others_their_tick() -> None:
    class StubTable:
        def __init__(self, table_id, fails):
            self.table_id = table_id
            self.fails = fails
            self.ticks = 0

        def on_tick(self):
            if self.fails:
                raise RuntimeError("broken table")
            self.ticks += 1

    manager = TableManager()
    broken, healthy = StubTable("a", True), StubTable("b", False)
    manager._tables = {"a": broken, "b": healthy}

    manager.on_tick()

    assert healthy.ticks == 1


def test_ticks_average_the_nominal_interval_despite_tick_work() -> None:
    async def run() -> int:
        ticks = 0

        def on_tick() -> None:
            nonlocal ticks
            ticks += 1

        scheduler = TickScheduler(on_tick)
        await scheduler.start()
        await asyncio.sleep(1.0)
        await scheduler.stop()
        return ticks

    # A fixed sleep after the work gave about 16 ticks a second on Windows.
    assert 18 <= asyncio.run(run()) <= 22


def test_missed_tick_deadlines_are_skipped_instead_of_replayed_in_a_burst() -> None:
    async def run() -> list[float]:
        tick_times: list[float] = []
        enough_ticks = asyncio.Event()

        def on_tick() -> None:
            tick_times.append(asyncio.get_running_loop().time())
            if len(tick_times) == 1:
                # Model one table traversal that overruns multiple deadlines.
                time.sleep(TickScheduler.TICK_INTERVAL_S * 2.5)
            if len(tick_times) == 3:
                enough_ticks.set()

        scheduler = TickScheduler(on_tick)
        await scheduler.start()
        await asyncio.wait_for(enough_ticks.wait(), timeout=1.0)
        await scheduler.stop()
        return tick_times

    tick_times = asyncio.run(run())

    # The old catch-up loop emitted the second and third callbacks together.
    assert tick_times[2] - tick_times[1] >= TickScheduler.TICK_INTERVAL_S * 0.75


def test_starting_a_running_tick_scheduler_is_idempotent() -> None:
    async def run() -> None:
        scheduler = TickScheduler(lambda: None)
        await scheduler.start()
        first_task = scheduler._task
        await scheduler.start()
        assert scheduler._task is first_task
        await scheduler.stop()
        assert scheduler._task is None

    asyncio.run(run())
