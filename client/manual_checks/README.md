# Manual audio checks

Scripts that need a real audio device or a listener, so they are not part of the test suite. Run each from the client directory. The offline scheduling test that needs no device is cosmos/miniaudio-sys/tests/scheduled_start.rs, run with `cargo test -p miniaudio-sys` from the cosmos directory.

## hrtf_checks.py

Silent. Checks that HRTF sounds report finishing, and measures the idle cost of holding finished HRTF sounds. Accepted on 19 September 2026 with the Cosmos 0.3.1 wheel: every row finishes within about 20 ms of the asset's length, and 300 held finished sounds cost about 6% of a core (29% on 0.3.0).

    uv run python manual_checks\hrtf_checks.py sounds\battle\appear1.ogg

## listening_tests.py

Audible, in headphone mode. Accepted by ear on 19 September 2026. Name one scenario or run all four.

    uv run python manual_checks\listening_tests.py [oneshot|intro|boundary|chain ...]

What to expect:

1. **oneshot**: the same sound front right, then front left, then directly behind, 2 s apart. Left and right are mirror images at the same loudness, outside the head. Behind is centred, duller and slightly quieter, with the top end rolled off.
2. **intro**: the pirates intro plays for 6 s from the front right, then the loop takes over. A hiccup of 5 to 25 ms at the handoff is the polling gap described in devdoc/audio-review-2026-09.md, desktop item 1, until the loop is scheduled instead. 12 s in, the loop cuts and the 3 s outro plays at once from the same position.
3. **boundary**: the intro material loops from the front left. A stop is requested at 3 s and nothing changes; at the 6 s loop end the outro starts with no silence between.
4. **chain**: five menu clicks exactly 750 ms apart, centre, right, centre, left, centre. The rhythm is even; a lurch at a change between centred and positioned would be a gap or overlap at the change of kind. The script also reports whether the chain's handle was released.
