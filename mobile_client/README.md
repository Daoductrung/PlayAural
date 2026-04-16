# PlayAural Mobile Client

The PlayAural mobile client is an Android-first Expo and React Native application for the PlayAural multiplayer game platform. It uses the same WebSocket protocol and sound directory layout as the other clients while providing self-voicing navigation, gesture-driven gameplay, and accessible text entry for mobile devices.

The mobile client is part of PlayAural and is licensed under the **GNU GENERAL PUBLIC LICENSE**.

## Current Scope

The mobile client focuses on:

- self-voicing gameplay and menu navigation
- synchronized game audio, music, ambience, and TTS
- account access, saved credentials, and reconnect flow
- touch-client table interaction shared with the server's menu system
- table-based real-time voice chat with listen-only join, microphone toggle, and table-context cleanup

## Features

- Self-voicing gesture navigation for menus, game actions, chat, and message history
- Real mobile identity on the server with `client: "mobile"`
- Touch-client game menus shared with the web client through server-side capability checks
- Login, registration, password reset, saved credentials, and auto-login
- Local configuration storage with AsyncStorage
- Credential storage with SecureStore
- Bundled sound pack playback with music fades, ambience, sound effects, and positional audio
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
|-- scripts/
|   `-- generate-sound-manifest.mjs
|-- sounds/
|-- src/
|   |-- app/
|   |-- audio/
|   |-- generated/
|   |-- gestures/
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
- Android device, emulator, or browser for web-runtime testing
- EAS CLI for cloud Android builds
- Optional: Android Debug Bridge (`adb`) for USB port forwarding

## Setup

Install dependencies:

```bash
cd mobile_client
cmd /c npm install
```

Generate the bundled sound manifest after changing `sounds/`:

```bash
cmd /c npm run generate:sounds
```

Run TypeScript validation:

```bash
cmd /c npm run typecheck
```

## Running the Client

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

## Local Android Builds

PlayAural can be built locally on Windows without using Expo cloud builds. This is useful for fast device testing, gesture debugging, voice-chat verification, and release candidate validation before distribution.

### Local Build Requirements

- Node.js LTS and npm
- Java 17
- Android Studio
- Android SDK Platform 35
- Android SDK Build-tools 35.0.0
- Android SDK Platform-tools

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

The installed SDK list should include `platforms;android-35`, `build-tools;35.0.0`, and `platform-tools`.

### Generate the Native Android Project

The Expo project does not need the generated Android directory in version control. Create or refresh it locally when needed:

```bash
cd mobile_client
cmd /c npm install
npx expo prebuild --platform android
```

This creates `mobile_client/android/` on the local machine. Treat that directory as generated build infrastructure rather than shared source.

### Build a Local Release APK

From the generated Android directory:

```bash
cd mobile_client\android
.\gradlew.bat clean
.\gradlew.bat assembleRelease
```

The release APK is written to:

```text
mobile_client\android\app\build\outputs\apk\release\app-release.apk
```

### Local Signing

If a developer needs an officially signed APK, the release keystore and signing credentials must be configured locally in the generated Android project. Do not commit keystores, signing passwords, or credential-bearing `gradle.properties` files.

If local signing is not configured, Gradle can still be used for local testing builds, but release-signing setup remains a local responsibility.

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

## App Identity

The Android package name and iOS bundle identifier are public application identifiers:

- `app.json`: `expo.android.package`
- `app.json`: `expo.ios.bundleIdentifier`

The EAS project id in `app.json` identifies the Expo project used for cloud builds. It is not an authentication token and is safe to keep in the public repository. Do not commit Expo access tokens, keystores, signing credentials, local credentials, `.env` secrets, or generated build output.

## Generated Files and Local Artifacts

The repository tracks source files, configuration files, locale files, and the generated sound manifest. The repository does not track generated build output or dependency folders such as:

- `mobile_client/node_modules/`
- `mobile_client/android/`
- `mobile_client/.expo/`
- `mobile_client/dist/`
- `.mobile_eas_stage/`

## License

PlayAural is licensed under the **GNU GENERAL PUBLIC LICENSE**. See `../LICENSE` for the full license text.
