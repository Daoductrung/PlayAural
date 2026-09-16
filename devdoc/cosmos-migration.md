# Replacing sound_lib with Cosmos on the Windows client

Plan written 14 September 2026. Cosmos is the CalmComputers audio library: a Rust wrapper over miniaudio (playback, mixing, buses, effects) and Steam Audio (HRTF), with Python bindings built by maturin. It lives in the CalmComputers knowledge base under code/cosmos rust and will move to its own repository as part of this work.

The goal is 3D spatial audio on the desktop client with no regression in what already works: one-shot effects with pan and pitch, managed loops, music with intro and outro splicing, ambience layers, buses, ducking, fades, and the versioned audio protocol shared with the web and mobile clients.

## 1. What we found

### 1.1 The client side is already abstracted

sound_manager.py never touches BASS directly except in one place. Every stream it manages is a duck-typed object with play, stop, pause, is_playing, volume, looping and pan, created by SoundCacher. The one direct BASS use is the end-of-stream sync in `_on_stream_end`, which is used to splice ambience outros and music intros at a loop boundary; it already has a polling fallback when the sync cannot be registered. test_sound_manager.py replaces the sound_cacher module with a fake, so the existing tests describe the interface a replacement must satisfy and will keep running unchanged.

That means the swap is a new SoundCacher implementation plus removal of the pybass import, not a rewrite of the 1200-line manager.

### 1.2 Threading is the real constraint

Packets arrive on a websocket thread and are handed to the main thread with wx.CallAfter, so all play calls originate on the main thread. But the manager runs fades, bus fades and end-of-sound watchers on daemon threads, and those threads set volume and read is_playing on the stream objects directly.

Cosmos's Python classes are declared unsendable: pyo3 raises if they are touched from any thread other than the one that created them. The manager wraps every stream call in try/except, so nothing would crash; fades would simply stop working and sounds would never be released. The fix belongs in Cosmos, not the client (section 3.1).

### 1.3 Cosmos has no "plain stereo" mode

Setting volume or pitch on a Cosmos sound re-runs spatialization, which recomputes pan from the sound's 3D position. A sound that was given a pan of 0.3 and then a volume of 0.5 ends up centred. The stationary flag also forces pan to zero. Since most of PlayAural's cues are plain panned sounds, Cosmos needs a direct mode where pan and volume are applied verbatim (section 3.2).

### 1.4 The build was blocked on two things, both now resolved

* The original Windows Steam Audio runtime was incomplete. The repository now
  carries the complete official Steam Audio 4.8.1 Windows, Android, and iOS
  artifact set, with upstream licenses and fail-closed SHA-256 verification.
* bindgen needs libclang. LLVM turned out to be installed, so the bindings were generated once with LIBCLANG_PATH set and are now committed under each sys crate's src/. bindgen is behind the optional `regen-bindings` feature, so nobody else needs LLVM.

Everything else in the toolchain is present: cargo 1.97, uv (which provides maturin through `uvx`), and Python 3.11 in the client venv.

### 1.5 There is no 3D data to play yet

At the start of this migration no game sent positions and the protocol was at
version 2. The completed cross-client work is described in section 10; current
clients use protocol version 3 and share position, attenuation, and automation
semantics.

### 1.6 Licensing improves

sound_lib wraps BASS, which is free only for non-commercial use. Cosmos retains
the MIT license declared in the original repository import, miniaudio is public
domain or MIT-0, and Steam Audio is Apache-2.0. These are separate grants; the
Cosmos MIT license does not relicense Steam Audio or its bundled dependencies.

Apache-2.0 is compatible with GPLv3, but the Apache Software Foundation and the
Free Software Foundation both state that it is not compatible with GPLv2 for a
combined derivative work. PlayAural is GPL-2.0-only, so this document must not
claim blanket compatibility. Release distributors must review the way each
Apache-2.0 component is combined and distributed, and obtain qualified legal
advice or an appropriate licensing solution where required. The authoritative
inventory and upstream notices are in `THIRD_PARTY_NOTICES.md`.

## 2. Design decisions

1. Cosmos becomes thread-safe at the Rust level. The client keeps its current thread structure so the diff there stays small and its tests stay valid. Moving the client to a single main-thread tick timer is a worthwhile later cleanup, not part of this migration.
2. Positions are absolute, in the listener's frame. The listener is always at the origin facing +Y and the client never tracks listener state. The server computes each recipient's own view of a sound before sending, which fits how PlayAural already fans packets out per user and makes reconnect replay trivial.
3. The server sends pan alongside position, derived from it, so a renderer may
   retain stereo-pan capability fallback. Pan is derived from position, never
   the other way round, so there is one source of truth.
4. Spatial mode is a client option with three values: off (pan only, current behaviour), stereo (Cosmos basic spatialization, works on speakers) and headphones (HRTF). Default is headphones, since that is what the feature is for, and the option is persisted with the other audio settings.
5. Cosmos lives in this repository under cosmos/, and the wheel Rory builds from it is committed at client/vendor/ and installed as a path dependency. The friend never needs Rust, LLVM or maturin. The wheel is built against the stable ABI so one file serves Python 3.11 and later. (Rory's decision on 14 September 2026: a separate Cosmos repository can come later if a different version warrants it.)
6. One sound object per playback, loaded by path. miniaudio's resource manager caches decoded audio, so SoundCacher's byte cache and its GC-protection list go away.

## 3. Cosmos work (Rust, in the CalmComputers repository)

### 3.1 Thread safety

* Replace Rc<RefCell<T>> with Arc<Mutex<T>> for AudioEngine, Sound and SoundGroup, and update SoundRef and SoundGroupRef.
* Add `unsafe impl Send` for the structs that hold miniaudio pointers, with a comment citing miniaudio's documented thread safety for sound start, stop and property setters. All mutation is serialised by the Mutex anyway.
* Check miniaudio_phonon.c: the binaural node's direction is written by the caller thread and read by the audio thread. Confirm the writes are single aligned floats or make them atomic.
* Remove `unsendable` from the audio pyclasses. Keep it on ScreenReader and Window, which PlayAural does not use.
* Dropping a Sound from a Python garbage-collection thread must uninit it cleanly; today an unsendable object dropped off-thread is leaked.

### 3.2 Direct pan mode

* Add a spatial mode to Sound: direct, basic, hrtf. Default stays basic so existing examples behave as before.
* In direct mode, update_spatialization applies base_pan, base_volume and base_pitch verbatim and skips distance and angle maths. Store base_pan on the struct; set_pan updates it in every mode.
* Expose it in Python as a string property, matching the easing convention already used by tween_pitch.

### 3.3 End-of-sound signalling

Not required: the client already polls is_playing at 50 ms and at_end is exposed. If boundary outro splicing sounds loose in listening tests, add a miniaudio end callback later. Note it as a possible follow-up, not a blocker.

### 3.4 Build and packaging

* Commit the bindgen output for miniaudio-sys and steamaudio-sys and put bindgen behind a `regen-bindings` cargo feature. Windows x64 only for now.
* Add the abi3-py311 feature to pyo3 so the wheel is cp311-abi3-win_amd64.
* Verify the maturin include rule places phonon.dll in the cosmos package directory next to cosmos.pyd, and that `import cosmos` works from a clean venv.
* Move code/cosmos rust to its own repository (repos/cosmos locally), including phonon.dll and the phonon headers. PlayAural is public, so the release that hosts the wheel must be public too.
* Tag a release and attach the wheel.

### 3.5 Cosmos smoke test

A short Python script, kept in the Cosmos repository: create a manager, load one of PlayAural's ogg files, play it panned in direct mode, set volume from a second thread, then play it positioned in hrtf mode at four compass points. This is the check that sections 3.1 and 3.2 landed.

## 4. Client work (PlayAural, client/)

### 4.1 New backend module

Add client/cosmos_backend.py containing:

* CosmosStream: wraps one cosmos.Sound and exposes play, stop, pause, is_playing, looping, volume, pan and pitch with the semantics FakeStream in the tests describes. Adds position and spatial_mode.
* SoundCacher: same constructor and method names as today (create, play, pin, unpin, clean, refs) so sound_manager.py and its tests need no interface change. Owns the cosmos.SoundManager. Pinning becomes a plain set of live streams; there is no byte cache.
* The spatial mode is read once from the audio options and applied to each stream at creation: direct when no position is given or mode is off, basic for stereo, hrtf for headphones.

### 4.2 sound_manager.py

* Delete the pybass import and the body of `_on_stream_end`; return None so the existing polling fallback is used.
* Thread `position` through play, `_create_stream` and `_play_layer`, and read it in handle_audio_command as an optional list of three finite numbers, ignoring anything else.
* Nothing else changes. Run test_sound_manager.py before and after.

### 4.3 Options and UI

* Add the spatial mode to client_options["audio"], the options dialog, and a Fluent string per locale for the three values (English first; other locales fall back to English by design).
* main_window.py applies it on startup next to the three volume settings.

### 4.4 Packaging

* pyproject.toml and requirements.txt: remove sound-lib, add the cosmos wheel URL with a win32 platform marker.
* PlayAural.spec: replace sound_lib with cosmos in hiddenimports and the collect_all loop so cosmos.pyd and phonon.dll ship in _internal.
* build_prod.bat: replace sound_lib in BUILD_DEPS_CHECK.
* client.py: the CWD comment mentions sound_lib; update it.
* Update the client's uv.lock.

### 4.5 Client tests

Existing tests keep passing because they never import the backend. Add tests/test_cosmos_backend.py that skips when cosmos is not importable and otherwise checks: create returns a stream with the requested pan, volume, pitch and looping; volume set from a worker thread takes effect; a positioned stream reports the position back.

## 5. Server work (PlayAural, server/)

### 5.1 Protocol

* AudioCommand and AudioPlaybackState gain `position: list[float] | None`, validated as three finite floats in a bounded range. to_packet omits it when None. Version stays 2.
* When position is set and pan was not given explicitly, derive pan from position so pan-only clients hear a sensible stereo image.

### 5.2 Seat geometry helper

One function in game_utils, used by every game rather than reimplemented:

```
listener at origin, facing +Y, table radius r = 2
N seated players, listener sits at index s, sound belongs to seat i
k = (i - s) mod N                 (0 is the listener's own seat)
phi = pi + 2*pi*k/N               (clockwise from straight ahead)
position = (r*sin(phi), r*cos(phi), 0)
pan = round(100 * sin(phi))
```

Sounds from the listener's own seat are sent unpositioned. With four players the next seat clockwise lands hard left, the seat across is straight ahead and the previous seat hard right, which matches how seat panning reads today. Table radius defines geometry only; distance gain remains neutral unless the command carries an explicit attenuation policy.

Because k depends on the listener, the server builds the command per recipient. game_sound_mixin already resolves recipients in `_audio_recipients`; add a `seat_of` argument to broadcast_sound that triggers per-recipient dispatch.

### 5.3 Rollout by game

1. Bang saloon heal (a row of drinks), Dead Man's Poker roulette and Dead Man's Deck preparation: these already pan by seat, so they become the first positioned sounds and the derived pan must reproduce their current stereo image closely enough that nobody notices on the web client.
2. Turn and presence cues table-wide: whose turn, joins, leaves, chat from a seat.
3. Arcade games last. They have no spatial state to draw from yet, so they need design first, which is the friend's territory.

## 6. Order of work

1. Done 14 September 2026: bindings generated and committed, clean build without LLVM, Cosmos moved into cosmos/.
2. Done 14 September 2026: thread safety, direct mode, abi3 wheel at client/vendor/, smoke-tested.
3. Done 14 September 2026, unreleased: client backend, packaging, spatial option and the client side of the position field. Automated coverage includes the real engine when an audio device is available. Still to do before release: build with build_prod.bat and listen through a full session, paying attention to ambience outros and music intros, which now rely on polling rather than an engine callback.
4. Done 14 September 2026: the server side. AudioCommand and AudioPlaybackState carry an optional position, validated and rounded, with pan derived from it when none was given; the geometry helpers (`direction_position`, `clock_position`, `seat_position`) live in server/audio.py; `broadcast_sound` and `play_sound` accept `position=` for one point in every listener's frame or `seat_of=player` for a per-listener seat position. The temporary clock-direction tuning menu used during development has been removed from the player-facing main menu.
5. Next: the three pilot games (Bang saloon heal, Dead Man's Poker roulette, Dead Man's Deck preparation), then table-wide cues, then arcade design.

Step 3 is the point of no return for sound_lib. The later protocol-v3 work in section 10 deliberately extends spatial and managed-source behavior across every client.

## 7. Open questions for Rory

1. Default spatial mode: headphones, as implemented, or stereo to be safe for speaker users? The option is in the Audio tab of client options either way.

### 7.1 Resolved

* Cosmos lives in this repository, not its own. The DLL is committed here.
* LLVM was already installed; no install was needed.

## 8. How to rebuild the wheel

From the repository root, on Windows:

```
cd cosmos\cosmos-python
uvx maturin build --release --interpreter ..\..\client\.venv\Scripts\python.exe
copy ..\target\wheels\cosmos-0.3.0-cp311-abi3-win_amd64.whl ..\..\client\vendor\
cd ..\..\client
uv sync --extra dev
```

Bump the version in cosmos/cosmos-python/Cargo.toml and pyproject.toml together, rename the wheel reference in client/pyproject.toml and requirements.txt, and delete the old wheel. Cosmos source changes that do not change the wheel are pointless to the client; the wheel is what ships.

To regenerate the C bindings after updating miniaudio.h or phonon.h, set LIBCLANG_PATH to the LLVM bin directory and build with `--features regen-bindings` once; the result is written back into src/bindings.rs of each sys crate.

## 9. Risks

* miniaudio caches decoded audio by path. The client's updater replaces files under sounds/ at runtime; a replaced file stays stale until restart. Acceptable, but worth a note in the updater's user message.
* Cosmos configures Steam Audio with a fixed processing frame. Desktop requests
  a matching graph period; the mobile renderer uses a bounded fixed-frame
  adapter so arbitrary device callback sizes do not disable HRTF or drop a
  final partial block and effect tail. `hrtf_available` remains exposed for
  desktop capability reporting.
* Pitch: BASS changed sample rate, Cosmos calls ma_sound_set_pitch; both shift speed and pitch together, so cues sound the same.
* Steam Audio per-source binaural effects cost CPU. The manager caps effects at 64, which is well within budget on any modern machine, but the number is worth watching in the pirates ambience-heavy scenes.

## 10. Cross-client HRTF hardening (15 September 2026)

The cross-client spatial pass is implemented without weakening the existing
ambience-stem lifecycle. Explicit attenuation advances the audio command
contract to protocol version 3:

* Cosmos now publishes HRTF direction, spatial blend, and interpolation as one
  lock-free snapshot. Audio-thread reads are bounded and reuse their last good
  snapshot if a control update is interrupted. Bilinear interpolation and full
  HRTF blend are explicit policy rather than consequences of source distance.
* Every Cosmos engine owns its resource manager. The process-wide Steam Audio
  context is reference-counted, so creating or destroying a second manager
  cannot invalidate the first manager's cache or HRTF effects.
* Web Audio sources with `position` use `PannerNode` in `HRTF` mode, including
  buffered effects, media-element fallbacks, music, and seamless ambience
  intro/loop/outro stems. Server coordinates map to Web Audio as
  `(x, y, z) -> (x, z, -y)`. Stereo pan remains the capability fallback.
* Expo Web uses the same validation, coordinate mapping, and HRTF graph. Native
  Android and physical iOS devices use the Cosmos/miniaudio Expo module with
  Steam Audio HRTF; platform playback remains the capability fallback. The
  native engine does not take audio focus, mutate the iOS session, or select an
  output route.
* Server and all clients reject malformed, non-finite, or out-of-range
  positions. A steady position is valid only on `play`; continuous changes use
  the complete, validated `motion` object on a stable-handle `update` command.

Distance attenuation is explicit command data. Omission or `{model: "none"}`
keeps directional spatialization at full level. `linear`, `inverse`, and
`exponential` carry reference distance, maximum distance, rolloff, and gain
limits with no client-side defaults. Desktop, Web, and mobile evaluate the same
bounded formulas in their mixer; Cosmos and browser panners remain
distance-neutral so gain is never applied twice. Replayable layers retain the
policy through save/reconnect, and intro/loop/outro segments keep one spatial
position and gain envelope.

### 10.1 Native mobile implementation

Native mobile HRTF is implemented as the local `playaural-spatial-audio` Expo
module over the shared Cosmos C renderer:

* The official Steam Audio 4.8.1 SDK is pinned as one reviewed artifact set:
  Windows x64, all four Android ABIs, the iOS device archive, headers, license,
  trademark terms, upstream third-party notices, and SHA-256 manifest. Mobile
  installation fails closed if an artifact, architecture, version, or Android
  16 KiB load alignment differs.
* Android uses a dedicated miniaudio media device without requesting audio
  focus or choosing an output. ExpoAV remains the focus coordinator and the
  system-selected wired, Bluetooth, earpiece, or speaker route is preserved.
* iOS runs inside the existing application audio session and never changes its
  category or activation. The official Steam Audio archive is device-only, so
  simulator builds use an explicit unsupported stub and the platform fallback.
* The native module exposes validated semantic source operations rather than
  raw pointers. JavaScript owns protocol, handle generations, source budgets,
  attenuation, automation, fades, buses, and lifecycle policy. Native code owns
  the real-time graph, HRTF processing, sample-scheduled stems, terminal state,
  and bounded fixed-frame/tail adaptation.
* Async loads reserve mixer capacity and unique native IDs before native work
  begins. Replacement generations, shutdown, and failed creation release those
  reservations and cannot resurrect or alias a stale source.

The module renders positioned one-shots and managed loops, continuous movement,
source gain, pitch, and phase-contiguous intro/loop/outro ambience. An
unavailable native module or failed HRTF initialization falls back to platform
playback without changing protocol semantics.

### 10.2 Next protocol slices

Implement these in lockstep across server, desktop, Web, and mobile. Do not add
a field that one first-party client silently interprets differently.

1. **Done: source-parameter automation.** A stable-handle `update` carries
   complete origin/destination positions, duration, elapsed time, and a named
   quadratic easing curve. The server advances trajectory state at game ticks;
   each client interpolates smoothly on its audio clock, so moving loops do not
   depend on packet frequency. Save/reconnect resumes an unfinished trajectory,
   and replacement or stop generations cancel it. The same update may carry a
   complete source-gain automation independently or concurrently; gain remains
   separate from authored volume, distance attenuation, fades, buses, ducking,
   and user master volume. A 3D footstep remains a one-shot `play` at a point.
   Future filter automation should extend this validated parameter system
   rather than introduce parallel packet types.
2. **Done: explicit distance policy.** Protocol version 3 carries named,
   bounded attenuation models. All first-party mixers use the same formulas and
   units, while native/browser renderer defaults are neutralized.
3. **Done: environmental zone blending.** An environment is independently
   addressable ambience layers. Normalized boundary weights drive configurable
   linear or equal-power source-gain automation between neighboring layers;
   stable context/layer identities preserve unrelated ambience. Layers stay
   running at zero gain for phase-coherent return transitions. Authored
   intro-to-loop and loop-to-outro seams remain contiguous, and stop still
   defaults to the immediate loop-to-outro splice.
4. **Environmental acoustics.** Add occlusion/transmission and early/reflection
   sends only after the direct-source contract is stable. These are source or
   bus parameters, not game-specific packet types.
5. **Budgets and verification.** Cross-client attenuation and automation now
   run against one protocol-v3 conformance corpus instead of four copied sets
   of expected values. Remaining work is to establish device-class voice/HRTF
   budgets, priority-based virtualization, underrun telemetry, coordinate
   golden tests, offline impulse-response comparisons, sample-boundary stem
   tests, moving-source stress tests, and physical wired/Bluetooth/speaker
   routing tests.

Replayable motion, source gain, and environmental layers belong in
`active_audio` and follow their table/save lifecycle. One-shot footsteps, mixer
interpolation state, and diagnostic counters stay runtime-only. A save made
during automation records a well-defined current/destination state and
remaining duration rather than a process-monotonic timestamp.
