import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

import ts from "typescript";

async function loadPlaybackLifecycle() {
  const source = await readFile(
    new URL("../src/audio/playbackLifecycle.ts", import.meta.url),
    "utf8",
  );
  const compiled = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
    },
    fileName: "playbackLifecycle.ts",
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(compiled, { exports: module.exports, module });
  return module.exports;
}

test("completed one-shots are terminal", async () => {
  const { isTerminalNativePlaybackStatus } = await loadPlaybackLifecycle();

  assert.equal(isTerminalNativePlaybackStatus({
    didJustFinish: true,
    isLoaded: true,
    isLooping: false,
  }), true);
});

test("automatic loop boundaries never dispose the native source", async () => {
  const { isTerminalNativePlaybackStatus } = await loadPlaybackLifecycle();

  assert.equal(isTerminalNativePlaybackStatus({
    didJustFinish: true,
    isLoaded: true,
    isLooping: true,
  }), false);
});

test("progress and unloaded callbacks are not terminal", async () => {
  const { isTerminalNativePlaybackStatus } = await loadPlaybackLifecycle();

  assert.equal(isTerminalNativePlaybackStatus({
    didJustFinish: false,
    isLoaded: true,
    isLooping: false,
  }), false);
  assert.equal(isTerminalNativePlaybackStatus({
    didJustFinish: true,
    isLoaded: false,
  }), false);
});

test("the manager applies the terminal guard to its shared native source path", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(
    source,
    /player\.setOnPlaybackStatusUpdate\([\s\S]*?isTerminalNativePlaybackStatus\(status\)/,
  );
  assert.match(source, /isLooping:\s*looping/);
  assert.match(source, /Boolean\(packet\.loop\)/);
  assert.match(source, /packet\.loop\s*\?\?\s*true/);
});

test("numbered assets remain exact and families remain explicit", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /const hasAsset = Boolean\(packet\.asset\)/);
  assert.match(source, /const hasFamily = Boolean\(packet\.family\)/);
  assert.match(source, /hasFamily && \(!family \|\| packet\.loop\)/);
  assert.match(
    source,
    /const resolvedAsset = asset \|\| this\.chooseSoundFamilyVariant\(family\)/,
  );
  assert.match(source, /asset: resolvedAsset/);
});

test("the mobile command boundary validates spatial positions before playback", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /const position = normalizeAudioPosition\(packet\.position\)/);
  assert.match(source, /const attenuation = normalizeDistanceAttenuation\(packet\.attenuation\)/);
  assert.match(source, /position === null/);
  assert.match(source, /attenuation === null/);
  assert.match(source, /position !== undefined && packet\.command !== "play"/);
  assert.match(source, /attenuation !== undefined && position === undefined/);
  assert.match(source, /Math\.round\(panFromPosition\(position\) \* 100\)/);
  assert.match(source, /\* source\.distanceGain/);
});

test("the mobile command boundary owns motion lifecycle and stale cancellation", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /const motion = normalizeAudioMotion\(packet\.motion\)/);
  assert.match(source, /case "update":[\s\S]*?this\.startSourceMotion/);
  assert.match(source, /this\.commandMotions\.set\(handle, runtime\)/);
  assert.match(source, /setAudioSpatializerPosition/);
  assert.match(source, /source\.distanceGain = distanceAttenuationGain/);
  assert.match(source, /this\.clearSourceMotion\(source\.handle\)/);
});

test("source gain is independent, automatable, and generation guarded", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /packet\.gain === undefined \? 1 : normalizeAudioGain\(packet\.gain\)/);
  assert.match(source, /normalizeAudioGainAutomation\(packet\.gain_automation\)/);
  assert.match(source, /\* source\.sourceGain/);
  assert.match(source, /this\.commandGainAutomations\.set\(handle, runtime\)/);
  assert.match(source, /source\.sourceGain = audioGainAt/);
  assert.match(source, /this\.clearSourceGainAutomation\(source\.handle\)/);
  assert.match(
    source,
    /detachSourceHandle[\s\S]*?clearSourceMotion\(source\.handle\)[\s\S]*?clearSourceGainAutomation\(source\.handle\)/,
  );
});

test("completed updates survive native source creation", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(
    source,
    /elapsed >= runtime\.motion\.duration_ms[\s\S]*?if \(source\) \{\s*this\.clearSourceMotion/,
  );
  assert.match(
    source,
    /const complete = this\.applySourceMotion\(runtime\);\s*if \(!complete/,
  );
  assert.match(
    source,
    /elapsed >= runtime\.automation\.duration_ms[\s\S]*?if \(source\) \{\s*this\.clearSourceGainAutomation/,
  );
  assert.match(
    source,
    /const complete = this\.applySourceGainAutomation\(runtime\);\s*if \(!complete/,
  );
});

test("async source creation reserves bounded mixer capacity", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /sourceLoadReservations = new Set<SourceLoadReservation>/);
  assert.match(
    source,
    /matching\.length \+ pendingMatching >= limit/,
  );
  assert.match(
    source,
    /effects\.length \+ pendingEffects\.length >= MAX_ACTIVE_EFFECTS/,
  );
  assert.match(
    source,
    /layers\.length \+ pendingLayers\.length >= MAX_ACTIVE_LAYERS/,
  );
  assert.match(
    source,
    /reservation\.slot === handle[\s\S]*?sourceLoadReservations\.delete\(reservation\)/,
  );
  assert.match(
    source,
    /reservation\.slot === target[\s\S]*?sourceLoadReservations\.delete\(reservation\)/,
  );
  assert.match(
    source,
    /try \{[\s\S]*?createSource\([\s\S]*?finally \{\s*releaseReservation\(\)/,
  );
  assert.match(source, /shutdown\(\)[\s\S]*?sourceLoadReservations\.clear\(\)/);
});

test("finite SFX preload concurrently and launch in command order", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /finiteSfxLaunchQueue: Promise<void> = Promise\.resolve\(\)/);
  assert.match(
    source,
    /const preload = this\.primeFiniteSfx\(queuedPacket\)[\s\S]*?const launch = this\.finiteSfxLaunchQueue/,
  );
  assert.match(
    source,
    /cursorMilliseconds \+= durationMilliseconds \* segment\.next_start_ratio/,
  );
  assert.match(
    source,
    /durationMilliseconds \* segments\[index\]\.next_start_ratio/,
  );
  assert.match(
    source,
    /await preload[\s\S]*?this\.playManagedSequence\(queuedPacket, generation\)[\s\S]*?this\.playManagedEffect\(queuedPacket, generation\)/,
  );
  assert.match(
    source,
    /expectedGeneration \?\? this\.nextGeneration\(handle\)/,
  );
});

test("managed layer pitch reaches native, element, and seamless stem paths", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /pitch: this\.clamp\(packet\.pitch, 25, 400, 100\) \/ 100/);
  assert.match(source, /playlist\.playbackRate = source\.pitch/);
  assert.match(source, /introNode\.playbackRate\.value = pitch/);
  assert.match(source, /loopNode\.playbackRate\.value = pitch/);
  assert.match(source, /outroNode\.playbackRate\.value = source\.pitch/);
  assert.match(source, /const loopDuration = loopBuffer\.duration \/ pitch/);
  assert.match(source, /webStem: \{\s*loopDuration,/);
  assert.match(source, /element\.playbackRate = source\.pitch/);
  assert.match(source, /element\.preservesPitch = false/);
  assert.match(source, /shouldCorrectPitch: false/);
  assert.match(source, /pitch: source\.pitch \* 100/);
});

test("mobile Web non-looping stems schedule their outro on the audio clock", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /scheduleWebStemOutroAt\(/);
  assert.match(source, /outroNode\.start\(boundary\)/);
  assert.match(
    source,
    /if \(!loopNode\.loop\)[\s\S]*?naturalOutroAt[\s\S]*?scheduleWebStemOutroAt\(source, naturalOutroAt, false\)/,
  );
  assert.match(
    source,
    /stem\.outroScheduled[\s\S]*?scheduledNode\.stop\(\)[\s\S]*?source\.webNodes\.delete\(scheduledNode\)/,
  );
  assert.match(source, /source\.webStem\?\.outroNode === outroNode/);
});

test("mobile Web HRTF sources drain their rendered tails before disposal", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /disposeWebSourceAfterTail\(source: CommandAudioSource\)/);
  assert.match(source, /analyser\.getFloatTimeDomainData\(samples\)/);
  assert.match(source, /silentPolls >= WEB_AUDIO_TAIL_SILENCE_POLLS/);
  assert.match(source, /gain\.connect\(analyser\)/);
  assert.ok(
    source.match(/this\.disposeWebSourceAfterTail\(source\)/g)?.length >= 2,
    "one-shot and atomic sequence completion must both preserve HRTF tails",
  );
});

test("native source identifiers remain unique across wraparound and async loads", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /nativeSpatialIdsInUse = new Set<string>/);
  assert.match(
    source,
    /attempts <= this\.nativeSpatialIdsInUse\.size[\s\S]*?!this\.nativeSpatialIdsInUse\.has\(sourceId\)[\s\S]*?nativeSpatialIdsInUse\.add\(sourceId\)/,
  );
  assert.match(source, /releaseNativeSpatialId\(sourceId: string\)/);
  assert.match(source, /shutdown\(\)[\s\S]*?nativeSpatialIdsInUse\.clear\(\)/);
  assert.ok(
    source.match(/releaseNativeSpatialId\(sourceId\)/g)?.length >= 4,
    "every native creation failure path must release its reserved identifier",
  );
});

test("stale native completion reports cannot retain reserved identifiers", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(
    source,
    /if \(!key \|\| !source \|\| source\.nativeSpatialId !== sourceId\) \{\s*this\.nativeSpatialSources\.delete\(sourceId\);\s*this\.releaseNativeSpatialId\(sourceId\);/,
  );
});
