import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import test from "node:test";

import {
  patchExpoAudioRouting,
  resolveExpoAudioModulePath,
} from "../scripts/patch-expo-audio-routing.mjs";
import {
  patchLiveKitAppleMediaRouting,
  resolveLiveKitAppleModulePath,
  resolveLiveKitPackageRoot,
} from "../scripts/patch-livekit-media-routing.mjs";

const upstreamSource = `class AudioModule {
  fun configure(mode: AudioMode) {
      updatePlaySoundThroughEarpiece(mode.shouldRouteThroughEarpiece ?: false)
  }
}`;

test("guards Android routing behind an explicitly supplied option", () => {
  const result = patchExpoAudioRouting(upstreamSource);

  assert.equal(result.changed, true);
  assert.match(
    result.source,
    /mode\.shouldRouteThroughEarpiece\?\.let \{ shouldRouteThroughEarpiece ->/,
  );
  assert.doesNotMatch(
    result.source,
    /shouldRouteThroughEarpiece \?: false/,
  );
});

test("is idempotent after the routing guard is installed", () => {
  const first = patchExpoAudioRouting(upstreamSource);
  const second = patchExpoAudioRouting(first.source);

  assert.equal(second.changed, false);
  assert.equal(second.source, first.source);
});

test("fails closed when an expo-audio upgrade changes the native implementation", () => {
  assert.throws(
    () => patchExpoAudioRouting("class AudioModule"),
    /Unsupported expo-audio AudioModule\.kt routing implementation/,
  );
});

test("the installed expo-audio source has the routing guard", async () => {
  const source = await readFile(resolveExpoAudioModulePath(), "utf8");
  const result = patchExpoAudioRouting(source);

  assert.equal(result.changed, false);
});

test("Android builds expo-audio from the guarded local source", async () => {
  const packageJson = JSON.parse(
    await readFile(new URL("../package.json", import.meta.url), "utf8"),
  );

  assert.ok(
    packageJson.expo?.autolinking?.android?.buildFromSource?.includes("expo-audio"),
  );
});

const upstreamLiveKitAppleSource = `class LivekitReactNativeModule {
    init() {
        config.categoryOptions = [.allowAirPlay, .allowBluetooth, .allowBluetoothA2DP, .defaultToSpeaker]
        config.mode = AVAudioSession.Mode.videoChat.rawValue
    }
    configure() {
        if useEarpiece {
            rtcConfig.categoryOptions = [.allowAirPlay, .allowBluetooth, .allowBluetoothA2DP]
            rtcConfig.mode = AVAudioSession.Mode.voiceChat.rawValue
        } else {
            rtcConfig.categoryOptions = [.allowAirPlay, .allowBluetooth, .allowBluetoothA2DP, .defaultToSpeaker]
            rtcConfig.mode = AVAudioSession.Mode.videoChat.rawValue
        }
    }
}`;

test("patches LiveKit iOS to default mode with A2DP-only Bluetooth routing", () => {
  const result = patchLiveKitAppleMediaRouting(upstreamLiveKitAppleSource);

  assert.equal(result.changed, true);
  assert.doesNotMatch(result.source, /Mode\.(?:voiceChat|videoChat)/);
  assert.equal(
    result.source.match(/Mode\.default\.rawValue \/\/ PlayAural media routing/g)?.length,
    3,
  );
  assert.doesNotMatch(result.source, /\.allowBluetooth,/);
  assert.equal(
    result.source.match(/PlayAural A2DP media routing/g)?.length,
    3,
  );
});

test("the LiveKit iOS routing patch is idempotent and fails closed", () => {
  const first = patchLiveKitAppleMediaRouting(upstreamLiveKitAppleSource);
  const second = patchLiveKitAppleMediaRouting(first.source);

  assert.equal(second.changed, false);
  assert.equal(second.source, first.source);
  assert.throws(
    () => patchLiveKitAppleMediaRouting("class LivekitReactNativeModule {}"),
    /Unsupported @livekit\/react-native iOS audio implementation/,
  );
});

test("the installed LiveKit iOS source preserves default-mode A2DP routing", async () => {
  const source = await readFile(resolveLiveKitAppleModulePath(), "utf8");
  const result = patchLiveKitAppleMediaRouting(source);

  assert.equal(result.changed, false);
  assert.doesNotMatch(source, /AVAudioSession\.Mode\.(?:voiceChat|videoChat)/);
  assert.doesNotMatch(source, /\.allowBluetooth,/);
});

test("the installed LiveKit Android media type is normal music playback", async () => {
  const source = await readFile(
    resolve(
      resolveLiveKitPackageRoot(),
      "android/src/main/java/com/livekit/reactnative/audio/AudioType.kt",
    ),
    "utf8",
  );
  const mediaType = source.match(
    /class MediaAudioType[\s\S]*?class CommunicationAudioType/,
  )?.[0] ?? "";

  assert.match(mediaType, /AudioManager\.MODE_NORMAL/);
  assert.match(mediaType, /AudioAttributes\.USAGE_MEDIA/);
  assert.match(mediaType, /AudioManager\.STREAM_MUSIC/);
  assert.doesNotMatch(mediaType, /MODE_IN_COMMUNICATION|STREAM_VOICE_CALL/);
});

test("PlayAural pins media routing in configuration and runtime policy", async () => {
  const appConfig = JSON.parse(
    await readFile(new URL("../app.json", import.meta.url), "utf8"),
  );
  const liveKitPlugin = appConfig.expo.plugins.find(
    (plugin) => Array.isArray(plugin) && plugin[0] === "@livekit/react-native-expo-plugin",
  );
  assert.equal(liveKitPlugin?.[1]?.android?.audioType, "media");

  const indexSource = await readFile(new URL("../index.ts", import.meta.url), "utf8");
  assert.match(indexSource, /registerGlobals\(\{ autoConfigureAudioSession: false \}\)/);

  const voiceSource = await readFile(
    new URL("../src/voice/MobileVoiceManager.ts", import.meta.url),
    "utf8",
  );
  assert.match(voiceSource, /audioMode: "normal"/);
  assert.match(voiceSource, /audioStreamType: "music"/);
  assert.match(voiceSource, /audioAttributesUsageType: "media"/);
  assert.match(voiceSource, /forceHandleAudioRouting: false/);
  assert.doesNotMatch(voiceSource, /preferredOutputList\s*:/);
  assert.doesNotMatch(voiceSource, /"allowBluetooth",/);
  assert.doesNotMatch(voiceSource, /audioMode: "(?:voiceChat|videoChat)"/);
});

test("voice routing remains independent from every gameplay audio path", async () => {
  const audioSource = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );
  assert.match(audioSource, /from "expo-av"/);
  assert.match(audioSource, /from "expo-audio"/);
  assert.match(audioSource, /InterruptionModeAndroid\.DuckOthers/);
  assert.match(audioSource, /interruptionMode: "mixWithOthers"/);
  assert.match(audioSource, /kind: "sfx"/);
  assert.match(audioSource, /kind: "music"/);
  assert.match(audioSource, /kind: "ambience"/);

  const voiceSource = await readFile(
    new URL("../src/voice/MobileVoiceManager.ts", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(voiceSource, /MobileAudioManager|expo-av|expo-audio/);
  assert.doesNotMatch(
    voiceSource,
    /stopAll|stopAllManagedAudio|setIsAudioActiveAsync/,
  );

  const appSource = await readFile(
    new URL("../src/app/PlayAuralApp.tsx", import.meta.url),
    "utf8",
  );
  const refreshCalls = appSource.match(/audio\.refreshPlaybackState\(\)/g) ?? [];
  assert.ok(refreshCalls.length >= 4);
});
