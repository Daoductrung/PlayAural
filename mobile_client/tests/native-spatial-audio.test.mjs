import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

import ts from "typescript";

import { verifySteamAudioSdk } from "../scripts/verify-steam-audio-sdk.mjs";

async function loadNativeSpatialAudio(bridge) {
  const source = await readFile(
    new URL("../src/audio/nativeSpatialAudio.ts", import.meta.url),
    "utf8",
  );
  const compiled = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
    },
    fileName: "nativeSpatialAudio.ts",
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(compiled, {
    console,
    decodeURIComponent,
    exports: module.exports,
    module,
    require: (specifier) => {
      if (specifier === "expo-modules-core") {
        return { requireOptionalNativeModule: () => bridge };
      }
      if (specifier === "react-native") {
        return { Platform: { OS: "android" } };
      }
      throw new Error(`Unexpected test dependency: ${specifier}`);
    },
  });
  return module.exports;
}

function createBridge(overrides = {}) {
  return {
    createSource: async () => [],
    destroySource: () => undefined,
    drainEndedSources: () => [],
    initialize: async () => ({ available: true, hrtf: true, sampleRate: 48_000 }),
    pauseSource: () => true,
    requestOutro: () => true,
    resumeSource: () => true,
    setSequenceSegmentParameters: () => true,
    setParameters: () => true,
    shutdown: () => undefined,
    ...overrides,
  };
}

test("the checked-in Steam Audio SDK matches its fail-closed manifest", async () => {
  const verified = await verifySteamAudioSdk();

  assert.deepEqual(verified.sort(), [
    "LICENSE.md",
    "THIRDPARTY.md",
    "TRADEMARK_RIGHTS.md",
    "android/arm64-v8a/libphonon.so",
    "android/armeabi-v7a/libphonon.so",
    "android/x86/libphonon.so",
    "android/x86_64/libphonon.so",
    "ios/libphonon.a",
    "phonon.dll",
    "phonon.h",
    "phonon.lib",
    "phonon_version.h",
  ]);
});

test("the EAS archive keeps mobile install verification scripts", async () => {
  const ignore = await readFile(
    new URL("../../.easignore", import.meta.url),
    "utf8",
  );

  assert.match(ignore, /^\/scripts\/$/m);
  assert.doesNotMatch(ignore, /^scripts\/$/m);
});

test("native file paths accept local assets and reject non-filesystem URIs", async () => {
  const { playbackSourceFilePath } = await loadNativeSpatialAudio(createBridge());

  assert.equal(
    playbackSourceFilePath({ uri: "file:///data/user/0/audio%20cue.ogg" }),
    "/data/user/0/audio cue.ogg",
  );
  assert.equal(
    playbackSourceFilePath({ uri: "file://localhost/private/audio.ogg" }),
    "/private/audio.ogg",
  );
  assert.equal(playbackSourceFilePath({ uri: "asset:/audio.ogg" }), null);
  assert.equal(playbackSourceFilePath({ uri: "https://example.test/audio.ogg" }), null);
  assert.equal(playbackSourceFilePath(42), null);
});

test("the adapter forwards configurable engine, source, and 3D parameters", async () => {
  const calls = [];
  const bridge = createBridge({
    initialize: async (...args) => {
      calls.push(["initialize", ...args]);
      return { available: true, hrtf: true, sampleRate: 48_000 };
    },
    createSource: async (...args) => calls.push(["createSource", ...args]),
    setParameters: (...args) => {
      calls.push(["setParameters", ...args]);
      return true;
    },
  });
  const {
    DEFAULT_NATIVE_SPATIAL_AUDIO_CONFIG,
    NativeSpatialAudio,
  } = await loadNativeSpatialAudio(bridge);
  const audio = new NativeSpatialAudio(DEFAULT_NATIVE_SPATIAL_AUDIO_CONFIG);

  assert.equal(await audio.createSource("source:1", {
    introPath: "/intro.ogg",
    loopPath: "/loop.ogg",
    outroPath: "/outro.ogg",
    playIntro: true,
    looping: true,
    streamFromDisk: true,
    startPaused: true,
    volume: 0.35,
    pitch: 1.1,
    position: [3, -2, 7],
  }), true);
  assert.equal(audio.setParameters("source:1", 0.4, 1.25, [3, -2, 7]), true);
  assert.deepEqual(calls[0], [
    "initialize",
    DEFAULT_NATIVE_SPATIAL_AUDIO_CONFIG.hrtfFrameSize,
    DEFAULT_NATIVE_SPATIAL_AUDIO_CONFIG.parameterSmoothingMilliseconds,
    DEFAULT_NATIVE_SPATIAL_AUDIO_CONFIG.maxSources,
  ]);
  assert.deepEqual(JSON.parse(JSON.stringify(calls[1])), [
    "createSource",
    "source:1",
    {
      introPath: "/intro.ogg",
      loopPath: "/loop.ogg",
      outroPath: "/outro.ogg",
      playIntro: true,
      looping: true,
      streamFromDisk: true,
      startPaused: true,
      volume: 0.35,
      pitch: 1.1,
      x: 3,
      y: -2,
      z: 7,
      spatialBlend: 1,
    },
  ]);
  assert.deepEqual(calls[2], [
    "setParameters",
    "source:1",
    0.4,
    1.25,
    3,
    -2,
    7,
    1,
  ]);
});

test("the adapter returns native decoded timing for atomic sequences", async () => {
  const calls = [];
  const bridge = createBridge({
    createSource: async (...args) => {
      calls.push(args);
      return [100, 250, 75];
    },
  });
  const { NativeSpatialAudio } = await loadNativeSpatialAudio(bridge);
  const audio = new NativeSpatialAudio();

  const timing = await audio.createSequence("source:sequence", {
    paths: ["/throw.ogg", "/flight.ogg", "/explosion.ogg"],
    nextStartRatios: [0, 1, 1],
    startPaused: true,
    volume: 0.8,
    pitch: 1,
    position: [0, 1, 0],
    spatialBlend: 1,
  });

  assert.deepEqual(JSON.parse(JSON.stringify(timing)), {
    durationsMilliseconds: [100, 250, 75],
    startLeadMilliseconds: 512 * 1000 / 48_000,
  });
  assert.deepEqual(JSON.parse(JSON.stringify(calls[0])), [
    "source:sequence",
    {
      introPath: null,
      loopPath: "",
      outroPath: null,
      playIntro: false,
      looping: false,
      streamFromDisk: false,
      startPaused: true,
      volume: 0.8,
      pitch: 1,
      x: 0,
      y: 1,
      z: 0,
      spatialBlend: 1,
      sequencePaths: ["/throw.ogg", "/flight.ogg", "/explosion.ogg"],
      sequenceNextStartRatios: [0, 1, 1],
    },
  ]);
});

test("the adapter forwards independent native sequence segment parameters", async () => {
  const calls = [];
  const bridge = createBridge({
    setSequenceSegmentParameters: (...args) => {
      calls.push(args);
      return true;
    },
  });
  const { NativeSpatialAudio } = await loadNativeSpatialAudio(bridge);
  const audio = new NativeSpatialAudio();

  assert.equal(await audio.initialize(), true);
  assert.equal(audio.setSequenceSegmentParameters(
    "source:sequence",
    2,
    0.35,
    [-4, 6, 1],
    1,
  ), true);
  assert.deepEqual(calls[0], [
    "source:sequence",
    2,
    0.35,
    -4,
    6,
    1,
    1,
  ]);
});

test("the adapter destroys an atomic sequence with incomplete native timing", async () => {
  const destroyed = [];
  const bridge = createBridge({
    createSource: async () => [100],
    destroySource: (sourceId) => destroyed.push(sourceId),
  });
  const { NativeSpatialAudio } = await loadNativeSpatialAudio(bridge);
  const audio = new NativeSpatialAudio();

  assert.equal(await audio.createSequence("source:invalid-sequence", {
    paths: ["/throw.ogg", "/flight.ogg"],
    nextStartRatios: [1, 1],
    startPaused: true,
    volume: 1,
    pitch: 1,
    position: [0, 0, 0],
    spatialBlend: 0,
  }), null);
  assert.deepEqual(destroyed, ["source:invalid-sequence"]);
});

test("the adapter rejects invalid sequence onset ratios before native creation", async () => {
  let createCalls = 0;
  const bridge = createBridge({
    createSource: async () => {
      createCalls += 1;
      return [100, 100];
    },
  });
  const { NativeSpatialAudio } = await loadNativeSpatialAudio(bridge);
  const audio = new NativeSpatialAudio();
  const base = {
    paths: ["/left.ogg", "/right.ogg"],
    startPaused: true,
    volume: 1,
    pitch: 1,
    position: [0, 0, 0],
    spatialBlend: 0,
  };

  assert.equal(await audio.createSequence("source:mismatch", {
    ...base,
    nextStartRatios: [1],
  }), null);
  assert.equal(await audio.createSequence("source:negative", {
    ...base,
    nextStartRatios: [1, -0.1],
  }), null);
  assert.equal(await audio.createSequence("source:overflow", {
    ...base,
    nextStartRatios: [1, 1.1],
  }), null);
  assert.equal(createCalls, 0);
});

test("shutdown invalidates an initialization that completes late", async () => {
  let resolveInitialization;
  let shutdownCalls = 0;
  const bridge = createBridge({
    initialize: () => new Promise((resolve) => {
      resolveInitialization = resolve;
    }),
    shutdown: () => { shutdownCalls += 1; },
  });
  const { NativeSpatialAudio } = await loadNativeSpatialAudio(bridge);
  const audio = new NativeSpatialAudio();
  const initialization = audio.initialize();

  audio.shutdown();
  resolveInitialization({ available: true, hrtf: true, sampleRate: 48_000 });

  assert.equal(await initialization, false);
  assert.equal(shutdownCalls, 2);
});

test("invalid native configuration is rejected before crossing the bridge", async () => {
  let initializationCalls = 0;
  const bridge = createBridge({
    initialize: async () => {
      initializationCalls += 1;
      return { available: true, hrtf: true, sampleRate: 48_000 };
    },
  });
  const { NativeSpatialAudio } = await loadNativeSpatialAudio(bridge);
  const audio = new NativeSpatialAudio({
    endedPollIntervalMilliseconds: 0,
    hrtfFrameSize: 512,
    maxSources: 96,
    parameterSmoothingMilliseconds: 5,
  });

  assert.equal(await audio.initialize(), false);
  assert.equal(initializationCalls, 0);
});

test("invalid native capabilities retire the partially initialized bridge", async () => {
  let shutdownCalls = 0;
  const bridge = createBridge({
    initialize: async () => ({ available: true, hrtf: true, sampleRate: 0 }),
    shutdown: () => { shutdownCalls += 1; },
  });
  const { NativeSpatialAudio } = await loadNativeSpatialAudio(bridge);
  const audio = new NativeSpatialAudio();

  assert.equal(await audio.initialize(), false);
  assert.equal(shutdownCalls, 1);
});

test("failed native creation retires any partially registered source", async () => {
  const destroyed = [];
  const bridge = createBridge({
    createSource: async () => {
      throw new Error("bridge rejected after partial creation");
    },
    destroySource: (sourceId) => destroyed.push(sourceId),
  });
  const { NativeSpatialAudio } = await loadNativeSpatialAudio(bridge);
  const audio = new NativeSpatialAudio();

  assert.equal(await audio.createSource("source:partial", {
    loopPath: "/loop.ogg",
    playIntro: false,
    looping: false,
    streamFromDisk: false,
    startPaused: true,
    volume: 1,
    pitch: 1,
    position: [0, 1, 0],
  }), false);
  assert.deepEqual(destroyed, ["source:partial"]);
});

test("the mobile manager routes positioned sources and seamless stems through HRTF", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(source, /const position = source\.position;\s*if \(!position\) \{/);
  assert.match(source, /attachNativeSpatialSource\(source, looping, isCurrent\)/);
  assert.match(source, /createNativeSpatialStemSource/);
  assert.match(source, /startPaused: true/);
  assert.match(source, /synchronizePendingAutomation\(source\)/);
  assert.match(source, /nativeSpatialAudio\.setParameters/);
  assert.match(source, /nativeSpatialAudio\.resumeSource/);
  assert.match(source, /source\.distanceGain = distanceAttenuationGain/);
  assert.match(source, /nativeSpatialAudio\.requestOutro/);
  assert.match(source, /nativeSpatialAudio\.drainEndedSources/);
  assert.match(source, /nativeSpatialAudio\.createSequence/);
  assert.match(source, /nativeSpatialAudio\.setSequenceSegmentParameters/);
  assert.match(source, /timing\.durationsMilliseconds/);
  assert.match(source, /resumeStartedAt[\s\S]*?resumeFinishedAt/);
  assert.match(
    source,
    /durationMilliseconds \* segments\[index\]\.next_start_ratio/,
  );
  assert.match(source, /setTimeout\([\s\S]*?track\.player\.playAsync/);
});

test("native playback preserves platform route and session ownership", async () => {
  const implementation = await readFile(
    new URL("../../cosmos/miniaudio-sys/miniaudio/miniaudio_impl.c", import.meta.url),
    "utf8",
  );
  const mobileCore = await readFile(
    new URL("../../cosmos/cosmos-audio/csrc/cosmos_mobile.c", import.meta.url),
    "utf8",
  );
  const phononNode = await readFile(
    new URL(
      "../../cosmos/cosmos-audio/csrc/miniaudio_phonon.c",
      import.meta.url,
    ),
    "utf8",
  );

  assert.match(implementation, /playback\.pDeviceID = NULL/);
  assert.match(implementation, /opensl\.streamType = ma_opensl_stream_type_media/);
  assert.match(implementation, /aaudio\.usage = ma_aaudio_usage_media/);
  assert.match(implementation, /aaudio\.contentType = ma_aaudio_content_type_music/);
  assert.match(implementation, /sessionCategory = ma_ios_session_category_none/);
  assert.match(implementation, /noAudioSessionActivate = MA_TRUE/);
  assert.match(implementation, /noAudioSessionDeactivate = MA_TRUE/);
  assert.match(
    implementation,
    /decodedSampleRate = pCosmosEngine->device\.sampleRate/,
  );
  const teardown = implementation.slice(
    implementation.indexOf("void ma_engine_uninit_with_caching"),
  );
  assert.ok(
    teardown.indexOf("ma_engine_uninit(pEngine)")
      < teardown.indexOf("ma_device_uninit(&pCosmosEngine->device)"),
    "the engine must stop its external device before that device is uninitialized",
  );
  assert.ok(
    teardown.indexOf("ma_device_uninit(&pCosmosEngine->device)")
      < teardown.indexOf("ma_resource_manager_uninit(&pCosmosEngine->resourceManager)"),
    "the device callback must retire before its resource manager",
  );
  assert.doesNotMatch(mobileCore, /set_attenuation|set_min_distance|set_max_distance/);
  assert.match(mobileCore, /if \(config->start_paused\)[\s\S]*?source->paused = MA_TRUE;/);
  assert.match(mobileCore, /if \(!source->started\) \{[\s\S]*?source_schedule_initial\(source\)/);
  assert.match(mobileCore, /ma_phonon_binaural_node_init_with_tail_processing/);
  assert.match(mobileCore, /ma_phonon_binaural_node_begin_tail_drain/);
  assert.match(mobileCore, /ma_phonon_binaural_node_tail_remaining/);
  assert.match(mobileCore, /pitched_frame_duration/);
  assert.match(mobileCore, /ma_sound_get_data_format\([\s\S]*?&segment->sample_rate/);
  assert.match(
    mobileCore,
    /\(long double\)engine_sample_rate[\s\S]*?\(long double\)source_sample_rate/,
  );
  assert.match(mobileCore, /source->started && source->pitch != pitch/);
  assert.match(mobileCore, /ma_sound_group_set_pitch\(&source->group, 1\.0f\)/);
  assert.match(mobileCore, /source_set_segment_pitch\(source, pitch\)/);
  assert.match(
    mobileCore,
    /ma_sound_set_pitch\(&source->sequence\[sequence_index\]\.sound, pitch\)/,
  );
  assert.match(mobileCore, /cosmos_mobile_source_set_sequence_segment_parameters/);
  assert.match(mobileCore, /segment->binaural_node/);
  assert.match(mobileCore, /source->active_renderers|owner->active_renderers/);
  assert.match(
    mobileCore,
    /\(config->sequence_paths == NULL\) != \(config->sequence_count == 0\)/,
  );
  assert.match(mobileCore, /config->sequence_next_start_ratios\[index\]/);
  assert.match(mobileCore, /ratio_frame_duration/);
  assert.match(mobileCore, /sequence_segment->next_start_ratio/);
  assert.match(
    mobileCore,
    /required_cycles = ceill\([\s\S]*?source->loop\.sample_rate[\s\S]*?engine_sample_rate/,
  );
  assert.match(mobileCore, /steam_y = z \/ length/);
  assert.match(mobileCore, /steam_z = -y \/ length/);
  assert.match(phononNode, /ma_phonon_binaural_tail_node_process_pcm_frames/);
  assert.match(phononNode, /tailDrainRequested/);
  assert.match(phononNode, /drainingTail \? offeredInputFrames : consumedInputFrames/);
  assert.match(phononNode, /bufferedInputFrames/);
  assert.match(phononNode, /ppFramesIn == NULL/);
  assert.match(phononNode, /iplBinauralEffectGetTail/);
  assert.match(
    phononNode,
    /g_ma_phonon_binaural_tail_node_vtable[\s\S]*?MA_NODE_FLAG_CONTINUOUS_PROCESSING/,
  );
});

test("native bridges fail safely on allocation, conversion, and integer boundaries", async () => {
  const androidBridge = await readFile(
    new URL(
      "../modules/playaural-spatial-audio/android/src/main/c/NativeSpatialAudioBridge.c",
      import.meta.url,
    ),
    "utf8",
  );
  const iosModule = await readFile(
    new URL(
      "../modules/playaural-spatial-audio/ios/PlayAuralSpatialAudioModule.swift",
      import.meta.url,
    ),
    "utf8",
  );

  assert.match(androidBridge, /return \(\*env\)->ExceptionCheck\(env\) \? NULL : output/);
  assert.match(androidBridge, /if \(output == NULL\) \{\s*cosmos_mobile_engine_destroy\(engine\)/);
  assert.match(androidBridge, /if \(loop_chars == NULL\) \{\s*goto cleanup/);
  assert.match(androidBridge, /cosmos_mobile_source_destroy\(source\);\s*return NULL/);
  assert.match(iosModule, /Int32\(exactly: hrtfFrameSize\)/);
  assert.match(iosModule, /!path\.utf8\.contains\(0\)/);
});
