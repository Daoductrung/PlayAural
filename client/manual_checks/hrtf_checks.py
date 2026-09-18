"""Acceptance checks for the Cosmos HRTF tail handling, against the installed wheel.

Run from the client directory, silently (every sound is at volume 0):

    uv run python manual_checks\\hrtf_checks.py sounds\\battle\\appear1.ogg

On the 0.3.0 wheel, check 1 said NEVER for both HRTF rows and check 2 climbed
by about 0.1% of a core per finished sound (12%, 20%, 29%). From 0.3.1, every
row ends near the asset's length and check 2 stays low; what remains at a few
hundred held sounds is the graph walking nodes still attached to the endpoint,
which the client avoids by dropping finished sounds.
"""
import sys
import time

import cosmos

path = sys.argv[1]
manager = cosmos.SoundManager()
print("hrtf available:", manager.hrtf_available, "engine rate:", manager.sample_rate)


def hrtf(sound):
    sound.spatial_mode = "hrtf"
    sound.set_position(3.0, 2.0, 0.0)


def hrtf_at_listener(sound):
    sound.spatial_mode = "hrtf"


def new_sound(configure):
    sound = manager.create_sound()
    configure(sound)
    sound.load(path)
    sound.volume = 0.0
    return sound


print("\n1. When does `playing` go false?")
unstarted = new_sound(hrtf)
time.sleep(0.2)
print("unstarted hrtf sound reports playing:", unstarted.playing, "(want False)")
for label, configure in (
    ("basic", lambda sound: None),
    ("hrtf positioned", hrtf),
    ("hrtf at listener", hrtf_at_listener),
):
    sound = new_sound(configure)
    length_ms = sound.length
    sound.play()
    started = time.perf_counter()
    finished_at = None
    while time.perf_counter() - started < length_ms / 1000 + 3.0:
        if not sound.playing:
            finished_at = time.perf_counter() - started
            break
        time.sleep(0.005)
    print(
        f"{label}: length {length_ms} ms, playing went false at",
        "NEVER (3 s past the end)" if finished_at is None else f"{finished_at * 1000:.0f} ms",
    )


def idle_cpu(seconds=3.0):
    wall = time.perf_counter()
    cpu = time.process_time()
    time.sleep(seconds)
    return (time.process_time() - cpu) / (time.perf_counter() - wall) * 100


print("\n2. Idle cost of finished HRTF sounds that are still held")
print(f"no sounds: {idle_cpu():.1f}% of one core")
held = []
for _ in range(3):
    for _ in range(100):
        sound = new_sound(hrtf)
        sound.play()
        held.append(sound)
    time.sleep(held[0].length / 1000 * 1.2 + 0.5)
    still = sum(1 for sound in held if sound.playing)
    print(
        f"{len(held)} finished sounds, {still} still report playing: "
        f"{idle_cpu():.1f}% of one core"
    )
