# PlayAural Mobile Client

The PlayAural mobile client is an Android-first Expo and React Native application for the PlayAural multiplayer game platform. It uses the same WebSocket protocol and sound directory layout as the other clients while providing self-voicing navigation, gesture-driven gameplay, and accessible text entry for mobile devices.

PlayAural-authored mobile-client software is licensed under the **GNU General
Public License, version 2 only**. Third-party code and assets retain their own
terms; see [License](#license).

## Current Scope

The mobile client focuses on:

- self-voicing gameplay and menu navigation
- synchronized game audio, music, ambience, and TTS
- account access, saved credentials, and reconnect flow
- touch-client table interaction shared with the server's menu system
- table-based real-time voice chat with listen-only join, microphone toggle, and table-context cleanup

## Features

- Self-voicing gesture navigation for menus, game actions, chat, and filtered message history
- Selectable All, Chat, Private Messages, Game, System, and Misc history buffers with per-buffer speech and notification muting
- Real mobile identity on the server with `client: "mobile"`
- Touch-client game menus shared with the web client through server-side capability checks
- Login, registration, password reset, saved credentials, and auto-login
- Local configuration storage with AsyncStorage
- Credential storage with SecureStore
- Bundled sound pack playback with music fades, seamless ambience stems, sound effects, and native Steam Audio HRTF for positioned sources
- Mobile-specific TTS voice, engine, and rate preferences with safe device fallback
- Server-synchronized account preferences
- LiveKit-based table voice chat integrated with the shared server authorization flow
- Version and sound-pack checks before gameplay
- Android APK builds through EAS

## Project Layout

```text
mobile_client/
|-- app.json
|-- eas.json
|-- package.json
|-- locales/
|   |-- en/client.json
|   `-- vi/client.json
|-- native/
|   `-- android/BoardViewportManager.kt
|-- modules/
|   `-- playaural-spatial-audio/
|       |-- android/
|       |-- ios/
|       `-- src/
|-- scripts/
|   |-- generate-sound-manifest.mjs
|   `-- verify-steam-audio-sdk.mjs
|-- sounds/
|-- src/
|   |-- app/
|   |-- audio/
|   |-- generated/
|   |-- gestures/
|   |   |-- SelfVoicingGestureRecognizer.ts
|   |   `-- useSelfVoicingGestures.ts
|   |-- i18n/
|   |-- network/
|   |-- state/
|   |-- tts/
|   `-- voice/
`-- tsconfig.json
```

The `sounds/` directory intentionally mirrors the desktop sound-pack layout. A sound pack can be copied into `mobile_client/sounds/` without renaming folders.

## Requirements

- Node.js LTS
- npm
- Android device, emulator, iOS device, simulator, or browser for runtime testing
- EAS CLI for cloud Android builds
- Optional: Android Debug Bridge (`adb`) for USB port forwarding

## Setup

Install dependencies:

```bash
cd mobile_client
cmd /c npm install
```

Installation is intentionally fail-closed. The `postinstall` chain verifies the
pinned Steam Audio SDK version, checksums, Android ELF architectures and 16 KiB
load alignment, then applies and verifies the guarded Expo Audio, Expo Speech,
and LiveKit routing patches. An install failure must be investigated; do not
skip the scripts for a release build.

Generate the bundled sound manifest after changing `sounds/`:

```bash
cmd /c npm run generate:sounds
```

Run TypeScript validation:

```bash
cmd /c npm run typecheck
```

Run the spatial-audio protocol, native lifecycle, source-budget, routing, and
SDK-integrity tests:

```bash
cmd /c npm run test:audio-lifecycle
cmd /c npm run test:android-audio-routing
cmd /c npm run test:licenses
cmd /c npm run verify:native-spatial-audio
```

Run the deterministic self-voicing gesture recognizer tests:

```bash
cmd /c npm run test:gestures
```

Run the speech lifecycle, announcement ordering, accessibility handoff, and
native dependency guard tests:

```bash
cmd /c npm run test:tts
```

Native speech waits for engine readiness and serializes interruptions. Failed
bindings and missing start callbacks receive bounded recovery; completion uses
native playback state rather than a text-length timeout. Recovery budgets are
injectable through `NativeSpeechDriver` because the native speech API exposes
no binding deadline. Engine names, voices, language support, and input limits
come from device capabilities or user preferences. Screen-reader detection
never changes the saved self-voicing preference.

The `postinstall` script applies a guarded Android Expo Speech lifecycle repair.
Android must build `expo-speech` from source, as configured in `package.json`;
its precompiled artifact does not contain the repair. See
`patches/expo-speech/README.md` for dependency upgrade and device checks.

## Running the Client

On the landing screen, choose **Language** to open the list of bundled
languages. The current language is marked and receives initial focus. Selecting
a language returns to the form; Back keeps the current language. Both paths
restore focus to the Language button and preserve any text already entered.
Community translations use English for any missing messages.

The landing form scrolls on smaller screens and when the keyboard is open.
Device safe-area insets keep controls clear of system bars and display cutouts.
Self-voicing follows the visible control order and scrolls focused controls into
view. During play, the menu uses the available screen space; **Help and gestures**
contains the gesture instructions and build information. Help is also available
from Shortcuts. Turning self-voicing off exposes the native navigation tabs.

Android Back and the self-voicing Back gesture close the currently visible
dialog or input before navigating the underlying screen. Closing Chat, History,
or Shortcuts returns focus to the game menu. Server menus retain their own Back
behavior across live updates, including the online user list.

Game boards scroll vertically and horizontally when they exceed the available
space. Cells keep readable text and usable touch targets at larger system font
sizes. Self-voicing navigation brings the focused cell into view on both axes
without waiting for scrolling before moving the cursor or speaking. With
self-voicing off, drag in any direction; with TalkBack on, use two fingers.
Chat, message history, and long input prompts also scroll, including when the
keyboard is open.

Android boards use a single native viewport for both axes, with the platform's
gesture detection, inertia, clamped content bounds, and directional accessibility
scroll actions. This avoids axis locking between nested scroll views. The Expo
plugin copies `native/android/BoardViewportManager.kt` into the generated Android
project during prebuild. Keep changes in that source file, and rerun prebuild
before building. Device checks must cover curved and diagonal TalkBack two-finger
drags, directional accessibility actions, enlarged text, self-voicing handoffs,
and live row reflow that leaves the overall board bounds unchanged. One-finger
tests alone do not validate screen-reader scrolling.

Message history is kept only in memory, with a configurable `BufferStore`
capacity of 500 messages per buffer by default. New messages preserve the
focused message by identity; the oldest entries are pruned at the capacity.
Returning to the login screen clears all buffers and the chat draft. History
is never written to device storage and does not survive an app restart.
The selected filter returns to All with a new login session. Muted-buffer
choices are client settings stored in AsyncStorage, matching the desktop and
web clients; they persist across sessions without persisting message content.
Muting hides the selected buffer and suppresses its TTS and related notification
audio while retaining its bounded source history. New entries from a directly
muted source are omitted from the combined All view. Muting All suppresses
every buffer until All is unmuted. Unmuting an individual source merges its
retained messages back into All in their original arrival order without
duplicating entries that were already there.

Run the language-menu, landing navigation, and focus visibility checks with:

```bash
cmd /c npm run test:navigation
```

Start the Expo dev server:

```bash
cd mobile_client
npx expo start
```

Run the web test runtime:

```bash
cd mobile_client
npx expo start --web -c
```

The web runtime is a development and testing target. Browser TTS voices can differ from Android TTS voices because the browser uses the Web Speech API while Android uses the device TTS service through Expo Speech.

Voice chat UI state and server packet flow can be tested in the web runtime, but native Android routing, microphone permission behavior, and multi-finger gesture behavior still require device or emulator validation.

Android self-voicing reads touch slop, double-tap timing/slop, physical swipe sampling distances, and the user's long-press timeout from the generated native `PlayAuralGestureConfiguration` module. Multi-finger gestures use the observing `PlayAuralGestureInput` module so every raw Android pointer transition and batched movement sample reaches the recognizer without depending on React Native responder touch counts. The observer never consumes the event; normal React Native input continues through the activity unchanged. Non-Android builds use the recognizer's documented platform-neutral fallbacks.

Test self-voicing gestures with the system screen reader suspended. Android accessibility services that request multi-finger gestures receive three-finger input before the foreground application; enabling two-finger passthrough does not pass ordinary three-finger taps through to PlayAural. Native screen-reader mode remains available through the dedicated self-voicing toggle when TalkBack is active.

## Server Connection

The default production server URL is stored in `src/app/PlayAuralApp.tsx` as `DEFAULT_SERVER_URL`:

```text
wss://playaural.ddt.one:443
```

For local server testing, change that constant to a local WebSocket URL such as:

```text
ws://127.0.0.1:8000
```

If testing on a physical Android device over USB, forward the local server port:

```bash
adb reverse tcp:8000 tcp:8000
```

With the reverse tunnel active, `ws://127.0.0.1:8000` on the device reaches the server running on the development computer.

For LAN testing, use the computer's LAN IP address instead:

```text
ws://192.168.1.50:8000
```

The phone and development computer must be on the same network, and the firewall must allow the server port.

## Version and Build Metadata

Mobile version and build identifiers are stored in:

- `src/app/PlayAuralApp.tsx`: `MOBILE_CLIENT_VERSION`
- `src/app/PlayAuralApp.tsx`: `MOBILE_BUILD_STAMP`
- `app.json`: `expo.version`
- `package.json`: package version
- `package-lock.json`: locked root package version

The client sends `MOBILE_CLIENT_VERSION` to the server during authorization. The UI displays `MOBILE_BUILD_STAMP` on the login screen for build verification.

## Sound Manifest

The generated sound manifest is written to:

```text
src/generated/soundManifest.ts
```

Regenerate it whenever sound files are added, removed, or renamed:

```bash
cmd /c npm run generate:sounds
```

## Native Spatial Audio

Positioned sounds on Android and physical iOS devices use the local
`playaural-spatial-audio` Expo module. The module shares the canonical Cosmos C
renderer with the desktop client: miniaudio owns the real-time source graph and
Steam Audio 4.8.1 performs binaural HRTF rendering. It supports one-shots,
moving stable-handle sources, pitch, independent gain and distance attenuation,
and sample-scheduled ambience intro/loop/outro stems.

The official Steam Audio headers and libraries are stored under
`../cosmos/steamaudio-sys/phonon/`. `UPSTREAM.json` pins every required Windows,
Android, and iOS artifact by SHA-256. Android packages `armeabi-v7a`, `arm64-v8a`,
`x86`, and `x86_64`; all checked-in Android libraries must remain 16 KiB page
aligned. Do not replace one architecture, a header, or a license in isolation.
Run `npm run verify:native-spatial-audio` after any SDK update.

The native renderer does not choose an output device or acquire a competing
audio-focus/session lease. Expo AV remains the application audio-focus
coordinator, and the OS-selected wired, Bluetooth, earpiece, or speaker route is
preserved. If the module or HRTF initialization is unavailable, positioned
playback falls back to the existing platform renderer without changing the
server protocol. The iOS Simulator deliberately uses that fallback because the
official pinned iOS Steam Audio library is device-only.

### Android Audio Routing Guard

`npm install` applies a guarded Expo Audio native patch that prevents the
gapless ambience playlist engine from overriding Android's selected wired,
Bluetooth, earpiece, or speaker route. The patch is intentionally fail-closed:
if an Expo Audio upgrade changes the affected native implementation, install
fails so the routing behavior must be reviewed before a build can ship. Android
autolinking also compiles Expo Audio from this guarded local source instead of
using Expo's otherwise-unpatched precompiled artifact.

Validate the installed dependency and the patch's regression cases with:

```bash
cmd /c npm run test:android-audio-routing
```

## Local Android Builds

PlayAural can be built locally on Windows without using Expo cloud builds. This is useful for fast device testing, gesture debugging, voice-chat verification, and release candidate validation before distribution.

### Local Build Requirements

- Node.js LTS and npm
- Java 17
- Android Studio
- Android SDK Platform 36
- Android SDK Build-tools 36.0.0
- Android SDK Platform-tools
- Android NDK `27.1.12297006`
- CMake `3.22.1`

The local shell environment must expose:

- `JAVA_HOME`
- `ANDROID_HOME`
- `ANDROID_SDK_ROOT`
- `%JAVA_HOME%\\bin`
- `%ANDROID_SDK_ROOT%\\platform-tools`
- `%ANDROID_SDK_ROOT%\\cmdline-tools\\latest\\bin`

After configuring those variables, open a fresh terminal and verify:

```bash
java -version
adb version
sdkmanager --list_installed
```

Install the native toolchain from Android Studio's SDK Manager or with:

```bash
sdkmanager "platforms;android-36" "build-tools;36.0.0" "platform-tools" "ndk;27.1.12297006" "cmake;3.22.1"
```

The installed SDK list should include those exact platform, build-tools, NDK,
and CMake entries. The full PlayAural repository checkout is required: the
local Expo module compiles shared source and verified SDK artifacts from the
repository-level `cosmos/` directory.

### Generate the Native Android Project

The Expo project does not need the generated Android directory in version control. Create or refresh it locally when needed:

```bash
cd mobile_client
cmd /c npm install
cmd /c npx expo prebuild --clean --platform android
```

This creates `mobile_client/android/` on the local machine and autolinks the
native spatial-audio module. Treat that directory as generated build
infrastructure rather than shared source. Use `--clean` whenever native module,
plugin, or app configuration changes so stale generated files cannot mask a
build problem.

### Build a Local Release APK

From the generated Android directory:

```bash
cd mobile_client\android
.\gradlew.bat :app:assembleRelease
```

The release APK is written to:

```text
mobile_client\android\app\build\outputs\apk\release\app-release.apk
```

### Local Signing

If a developer needs an officially signed APK, the release keystore and signing credentials must be configured locally in the generated Android project. Do not commit keystores, signing passwords, or credential-bearing `gradle.properties` files.

If local signing is not configured, Gradle can still be used for local testing builds, but release-signing setup remains a local responsibility.

For a USB-connected development device, verify `adb devices`, then use
`npx expo run:android --device` or build and install the generated debug APK.
Native HRTF, wired/Bluetooth route preservation, audio focus, lifecycle resume,
and device performance must be validated on physical hardware; browser and
Node tests cannot substitute for those checks.

## Local iOS Builds

iOS native builds require macOS, a compatible Xcode installation, CocoaPods,
and the same full repository checkout. Generate a clean native project and run
on a physical arm64 device with:

```bash
cd mobile_client
npm install
npx expo prebuild --clean --platform ios
npx pod-install
npx expo run:ios --device --configuration Release
```

The generated pod links the pinned device `libphonon.a` and compiles the shared
Cosmos/miniaudio renderer. Simulator builds compile an explicit unsupported
stub and exercise the platform fallback instead of falsely reporting HRTF.

### Cloud Builds with EAS

Install and authenticate EAS CLI:

```bash
npm install -g eas-cli
eas login
```

Build the preview APK:

```bash
cd mobile_client
eas build --platform android --profile preview
```

Build the production profile:

```bash
cd mobile_client
eas build --platform android --profile production
```

Build profiles are configured in `eas.json`. Expo app metadata is configured in `app.json`.
EAS commands are run from `mobile_client/`, but the upload is rooted at the Git
repository so the `cosmos/` source and SDK artifacts retain the paths expected
by CMake and CocoaPods. The root `.easignore` excludes unrelated components and
all generated Rust, Python, Gradle, and npm state. Before changing that file or
the repository layout, inspect an upload with:

```bash
eas build:inspect --platform android --stage archive --profile preview --output ../.mobile_eas_stage --force
```

Confirm the archive contains `mobile_client/modules/playaural-spatial-audio/`,
`cosmos/cosmos-audio/csrc/`, `cosmos/miniaudio-sys/miniaudio/`, and the complete
`cosmos/steamaudio-sys/phonon/` manifest before dispatching a cloud build.

## App Identity

The Android package name and iOS bundle identifier are public application identifiers:

- `app.json`: `expo.android.package`
- `app.json`: `expo.ios.bundleIdentifier`

The EAS project id in `app.json` identifies the Expo project used for cloud builds. It is not an authentication token and is safe to keep in the public repository. Do not commit Expo access tokens, keystores, signing credentials, local credentials, `.env` secrets, or generated build output.

## Generated Files and Local Artifacts

The repository tracks source files, configuration files, locale files, and the generated sound manifest. The repository does not track generated build output or dependency folders such as:

- `mobile_client/node_modules/`
- `mobile_client/android/`
- `mobile_client/ios/`
- `mobile_client/modules/*/android/.cxx/`
- `mobile_client/modules/*/android/build/`
- `mobile_client/.expo/`
- `mobile_client/dist/`
- `.mobile_eas_stage/`

## License

PlayAural is licensed under the **GNU General Public License, version 2 only**.
See `../LICENSE` for the full text. That license covers PlayAural-authored
software and does not relicense third-party code, audio, or other assets.
Direct dependency licenses and the complete notices for checked-in Cosmos,
miniaudio, stb_vorbis, Steam Audio, and patched Expo source are documented in
`../THIRD_PARTY_NOTICES.md`; read its Apache-2.0/GPL-2.0 compatibility warning
before distributing a native binary.
