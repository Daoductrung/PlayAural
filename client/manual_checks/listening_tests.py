"""Audible listening tests for positioned audio, through the real client.

Run from the client directory, with headphones on:

    uv run python manual_checks\\listening_tests.py [scenario ...]

Scenarios: oneshot, intro, boundary, chain. All four run in that order when
none is named, each after a printed 3-second countdown so the terminal can be
read while listening. README.md beside this file says what to expect.
"""
import importlib.util
from pathlib import Path
import sys
import time

CLIENT_DIR = Path.cwd()
if not (CLIENT_DIR / "sound_manager.py").exists():
    sys.exit("run this from the client directory")
sys.path.insert(0, str(CLIENT_DIR))
spec = importlib.util.spec_from_file_location("sound_manager_listening", CLIENT_DIR / "sound_manager.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

manager = module.SoundManager()
manager.set_spatial_mode("headphones")
print("hrtf available:", manager.hrtf_available, "| spatial mode:", manager.spatial_mode)
if not manager.hrtf_available:
    sys.exit("Steam Audio HRTF is unavailable; nothing here would be binaural")

ONE_SHOT = "battle/appear1.ogg"     # 1185 ms
CLICK = "menuclick.ogg"             # 750 ms
INTRO = "game_pirates/am_intro.ogg"  # 5941 ms
LOOP = "game_pirates/amloop.ogg"     # 121850 ms
OUTRO = "game_pirates/am_outro.ogg"  # 3277 ms
NO_ATTENUATION = {"model": "none"}


def say(text):
    print(f"[{time.strftime('%H:%M:%S')}] {text}", flush=True)


def countdown(title):
    print()
    say(f"next: {title}")
    for n in (3, 2, 1):
        say(str(n))
        time.sleep(1)


def segment(asset, position):
    return {
        "asset": asset,
        "position": position,
        "destination_position": None,
        "attenuation": None if position is None else NO_ATTENUATION,
        "gain": 1,
        "easing": "linear",
    }


def play_chain(handle, assets_and_positions):
    ok = manager.handle_audio_command({
        "type": "audio",
        "version": 3,
        "command": "play",
        "kind": "sfx",
        "handle": handle,
        "segments": [segment(asset, position) for asset, position in assets_and_positions],
    })
    assert ok is True, f"chain {handle} was refused"


def wait_for_handle_release(handle, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if handle not in manager._sources:
            return True
        time.sleep(0.02)
    return False


def oneshot():
    countdown("positioned one-shots: front right, front left, then directly behind")
    for label, position in (("front-right", [3, 2, 0]), ("front-left", [-3, 2, 0]), ("behind", [0, -3, 0])):
        say(f"one-shot {label}")
        play_chain(f"listen:oneshot:{label}", [(ONE_SHOT, position)])
        time.sleep(1.8)
    say("one-shots done")


def intro():
    countdown("ambience with an intro, front right: 6 s of intro, then the loop must take over")
    manager.ambience(INTRO, LOOP, OUTRO, handle="listen:intro", fade_in_ms=0, fade_out_ms=0,
                     position=(3, 2, 0), attenuation=NO_ATTENUATION)
    say("intro started; the loop should take over at about 6 s")
    time.sleep(5.9)
    say("boundary now")
    time.sleep(6)
    say("stopping with an immediate outro")
    manager.stop_ambience(handle="listen:intro", fade_ms=0, outro_mode="immediate")
    time.sleep(3.6)
    say("intro scenario done")


def boundary():
    countdown("boundary outro, front left: a 6 s loop, stop requested at 3 s, outro only after the loop's end")
    manager.ambience("", INTRO, OUTRO, handle="listen:boundary", play_intro=False, fade_in_ms=0,
                     fade_out_ms=0, position=(-3, 2, 0), attenuation=NO_ATTENUATION)
    say("loop started (it is the intro material, looping)")
    time.sleep(3)
    say("stop requested at the boundary; nothing should change yet")
    manager.stop_ambience(handle="listen:boundary", fade_ms=0, outro_mode="boundary")
    time.sleep(2.9)
    say("loop end: the outro should start now")
    time.sleep(3.6)
    say("boundary scenario done")


def chain():
    countdown("chain of five clicks alternating centred and positioned, 750 ms apart")
    play_chain("listen:chain", [
        (CLICK, None), (CLICK, [3, 1, 0]), (CLICK, None), (CLICK, [-3, 1, 0]), (CLICK, None),
    ])
    say("chain started: centre, right, centre, left, centre")
    released = wait_for_handle_release("listen:chain", 5 * 0.75 + 2)
    say("chain released cleanly" if released else "chain handle was NOT released")


SCENARIOS = {"oneshot": oneshot, "intro": intro, "boundary": boundary, "chain": chain}
chosen = sys.argv[1:] or list(SCENARIOS)
for name in chosen:
    SCENARIOS[name]()
    time.sleep(1.5)
say("all done")
