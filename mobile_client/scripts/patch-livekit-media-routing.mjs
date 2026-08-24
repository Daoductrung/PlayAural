import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const UPSTREAM_INITIAL_MODE =
  "        config.mode = AVAudioSession.Mode.videoChat.rawValue";
const GUARDED_INITIAL_MODE =
  "        config.mode = AVAudioSession.Mode.default.rawValue // PlayAural media routing";
const UPSTREAM_CONFIGURED_VOICE_MODE =
  "            rtcConfig.mode = AVAudioSession.Mode.voiceChat.rawValue";
const UPSTREAM_CONFIGURED_VIDEO_MODE =
  "            rtcConfig.mode = AVAudioSession.Mode.videoChat.rawValue";
const GUARDED_CONFIGURED_MODE =
  "            rtcConfig.mode = AVAudioSession.Mode.default.rawValue // PlayAural media routing";
const UPSTREAM_BLUETOOTH_OPTIONS =
  ".allowAirPlay, .allowBluetooth, .allowBluetoothA2DP";
const GUARDED_BLUETOOTH_OPTIONS =
  ".allowAirPlay, .allowBluetoothA2DP /* PlayAural A2DP media routing */";

function occurrences(source, value) {
  return source.split(value).length - 1;
}

export function patchLiveKitAppleMediaRouting(source) {
  let patchedSource = source;
  let changed = false;
  const upstreamCounts = [
    occurrences(patchedSource, UPSTREAM_INITIAL_MODE),
    occurrences(patchedSource, UPSTREAM_CONFIGURED_VOICE_MODE),
    occurrences(patchedSource, UPSTREAM_CONFIGURED_VIDEO_MODE),
  ];
  const guardedInitialCount = occurrences(patchedSource, GUARDED_INITIAL_MODE);
  const guardedConfiguredCount = occurrences(patchedSource, GUARDED_CONFIGURED_MODE);

  if (
    upstreamCounts.every((count) => count === 1)
    && guardedInitialCount === 0
    && guardedConfiguredCount === 0
  ) {
    patchedSource = patchedSource
      .replace(UPSTREAM_INITIAL_MODE, GUARDED_INITIAL_MODE)
      .replace(UPSTREAM_CONFIGURED_VOICE_MODE, GUARDED_CONFIGURED_MODE)
      .replace(UPSTREAM_CONFIGURED_VIDEO_MODE, GUARDED_CONFIGURED_MODE);
    changed = true;
  } else if (
    upstreamCounts.some((count) => count !== 0)
    || guardedInitialCount !== 1
    || guardedConfiguredCount !== 2
  ) {
    throw new Error(
      "Unsupported @livekit/react-native iOS audio implementation. "
        + "Review the installed dependency before building PlayAural.",
    );
  }

  const upstreamBluetoothCount = occurrences(
    patchedSource,
    UPSTREAM_BLUETOOTH_OPTIONS,
  );
  const guardedBluetoothCount = occurrences(
    patchedSource,
    GUARDED_BLUETOOTH_OPTIONS,
  );
  if (upstreamBluetoothCount === 3 && guardedBluetoothCount === 0) {
    patchedSource = patchedSource.replaceAll(
      UPSTREAM_BLUETOOTH_OPTIONS,
      GUARDED_BLUETOOTH_OPTIONS,
    );
    changed = true;
  } else if (upstreamBluetoothCount !== 0 || guardedBluetoothCount !== 3) {
    throw new Error(
      "Unsupported @livekit/react-native iOS Bluetooth routing implementation. "
        + "Review the installed dependency before building PlayAural.",
    );
  }

  return { changed, source: patchedSource };
}

export function resolveLiveKitPackageRoot() {
  return resolve(
    dirname(fileURLToPath(import.meta.url)),
    "../node_modules/@livekit/react-native",
  );
}

export function resolveLiveKitAppleModulePath() {
  return resolve(resolveLiveKitPackageRoot(), "ios/LiveKitReactNativeModule.swift");
}

async function main() {
  const modulePath = resolveLiveKitAppleModulePath();
  const source = await readFile(modulePath, "utf8");
  const result = patchLiveKitAppleMediaRouting(source);
  if (result.changed) {
    await writeFile(modulePath, result.source, "utf8");
    console.log("Patched LiveKit iOS audio routing to preserve media fidelity.");
    return;
  }
  console.log("LiveKit iOS media routing is already protected.");
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : null;
if (invokedPath === fileURLToPath(import.meta.url)) {
  await main();
}
