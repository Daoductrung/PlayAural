# Expo Speech lifecycle repair

The reviewed Expo Speech 55.0.17 Android module retains a lazy engine after
initialization failure or activity destruction. It also leaves startup requests
queued after stop, ignores immediate native speak errors, and does not clear
completed startup queues. The replacement keeps the Expo module contract and
adds `reset` for PlayAural's speech driver.

All native state runs on the main looper. Initialization callbacks are posted
after construction and checked against the current generation. Stop clears
pending speech; reset and teardown release the engine, reject pending discovery,
and retire utterances. Speech uses media attributes without requesting audio
focus or selecting an output device. No utterance text is logged or persisted.

The JS driver owns readiness deadlines, bounded retries, current utterance
cancellation, native input-length chunking, and completion polling after speech
starts. Its recovery policy is injectable; Android and iOS do not supply binding
or callback deadlines. Recovery first retries with the current engine's default
voice. If that engine still cannot start, Android discovers installed engines,
prefers system engines without relying on package-name allowlists, and tries a
bounded set until one starts. The working runtime fallback remains active until
the speech environment is refreshed; the user's synchronized engine and voice
preferences are never overwritten. Errors received after speech starts are not
replayed, because doing so could duplicate already-audible text.

## Dependency updates

`scripts/patch-expo-speech-lifecycle.mjs` compares the complete upstream source
hash and fails closed on an unreviewed implementation. The source fixture in
`tests/fixtures/expo-speech/` is copied from Expo's published sources artifact;
Expo's MIT license is included here. Review upstream changes, update the repair
and fixture together, and update the guard only after that review. Keep the
`expo-speech` Android `buildFromSource` entry and postinstall command.

## Validation

Run `npm run typecheck` and `npm run test:tts`, then build a native APK. Browser
tests cannot validate Android binding, TalkBack, or media routing. On a device:

1. Launch with TalkBack enabled, disable it, and navigate with self-voicing.
2. Switch self-voicing off/on with and without a native screen reader.
3. Return from Home, Android settings, and the notification shade; repeat while
   speech or voice discovery is pending.
4. Interrupt speech rapidly and read a long announcement at different rates.
5. Terminate the system TTS service during a controlled test; verify a later
   utterance rebinds without restarting PlayAural.
6. Verify native speech start/completion callbacks and the selected media route.
   Restore accessibility settings and remove temporary device artifacts.

The implementation follows Android's [TextToSpeech lifecycle](https://developer.android.com/reference/android/speech/tts/TextToSpeech)
and [utterance callbacks](https://developer.android.com/reference/android/speech/tts/UtteranceProgressListener).
The [Unity Accessibility Plugin Android implementation](https://github.com/mikrima/UnityAccessibilityPlugin/blob/main/Assets/UAP/NativePlugins%7E/Android/AndroidTTS.java)
also separates readiness, stopping, and native speaking-state checks. No Unity
code or fixed engine names are used here.
