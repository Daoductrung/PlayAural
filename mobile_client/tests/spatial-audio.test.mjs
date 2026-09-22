import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

import ts from "typescript";

const CONFORMANCE = JSON.parse(await readFile(
  new URL("../../audio_protocol_v3_conformance.json", import.meta.url),
  "utf8",
));

async function loadSpatialAudio() {
  const source = await readFile(
    new URL("../src/audio/spatialAudio.ts", import.meta.url),
    "utf8",
  );
  const compiled = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
    },
    fileName: "spatialAudio.ts",
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(compiled, { exports: module.exports, module });
  return module.exports;
}

test("mobile web validates and converts all three spatial axes", async () => {
  const {
    MAX_AUDIO_POSITION,
    normalizeAudioPosition,
    toWebAudioPosition,
  } = await loadSpatialAudio();

  assert.deepEqual([...normalizeAudioPosition([2, -3, 4])], [2, -3, 4]);
  assert.deepEqual([...toWebAudioPosition([2, -3, 4])], [2, 4, 3]);
  assert.equal(normalizeAudioPosition([MAX_AUDIO_POSITION + 1, 0, 0]), null);
  assert.equal(normalizeAudioPosition([0, Number.NaN, 0]), null);
  assert.equal(normalizeAudioPosition(["2", 0, 0]), null);
  assert.equal(normalizeAudioPosition([true, 0, 0]), null);
  assert.equal(normalizeAudioPosition([0, 0]), null);
});

test("mobile web creates an HRTF panner and retains stereo fallback", async () => {
  const {
    TABLE_RADIUS,
    createWebAudioSpatializer,
    setAudioSpatializerPosition,
  } = await loadSpatialAudio();
  const values = () => ({
    seen: [],
    setValueAtTime(value, time) { this.seen.push([value, time]); },
  });
  const panner = {
    positionX: values(),
    positionY: values(),
    positionZ: values(),
  };
  const context = { currentTime: 4, createPanner: () => panner };
  assert.equal(
    createWebAudioSpatializer(context, { position: [2, 3, 4] }),
    panner,
  );
  assert.equal(panner.panningModel, "HRTF");
  assert.equal(panner.refDistance, TABLE_RADIUS);
  assert.equal(panner.rolloffFactor, 0);
  assert.deepEqual(panner.positionX.seen, [[2, 4]]);
  assert.deepEqual(panner.positionY.seen, [[4, 4]]);
  assert.deepEqual(panner.positionZ.seen, [[-3, 4]]);

  const colocatedPanner = {
    positionX: values(),
    positionY: values(),
    positionZ: values(),
  };
  assert.equal(
    createWebAudioSpatializer(
      { currentTime: 5, createPanner: () => colocatedPanner },
      { position: [0, 0, 0] },
    ),
    colocatedPanner,
  );
  setAudioSpatializerPosition(
    colocatedPanner,
    { currentTime: 6 },
    [1, 2, 3],
  );
  assert.deepEqual([...colocatedPanner.positionX.seen.at(-1)], [1, 6]);
  assert.deepEqual([...colocatedPanner.positionY.seen.at(-1)], [3, 6]);
  assert.deepEqual([...colocatedPanner.positionZ.seen.at(-1)], [-2, 6]);

  const stereo = { pan: { value: 0 } };
  assert.equal(
    createWebAudioSpatializer(
      { createStereoPanner: () => stereo },
      { position: [-2, 0, 0] },
    ),
    stereo,
  );
  assert.equal(stereo.pan.value, -1);

  const degraded = { pan: { value: 0 } };
  assert.equal(
    createWebAudioSpatializer(
      {
        createPanner() { throw new Error("HRTF unavailable"); },
        createStereoPanner: () => degraded,
      },
      { position: [2, 0, 0] },
    ),
    degraded,
  );
  assert.equal(degraded.pan.value, 1);

  const colocated = { pan: { value: 1 } };
  assert.equal(
    createWebAudioSpatializer(
      {
        createPanner() { throw new Error("co-located sources are not directional"); },
        createStereoPanner: () => colocated,
      },
      { position: [0, 0, 0] },
    ),
    colocated,
  );
  assert.equal(colocated.pan.value, 0);
});

test("mobile distance attenuation matches the shared protocol vectors", async () => {
  const {
    distanceAttenuationGain,
    normalizeDistanceAttenuation,
  } = await loadSpatialAudio();
  assert.equal(CONFORMANCE.protocol_version, 3);
  for (const vector of CONFORMANCE.distance_attenuation) {
    const attenuation = normalizeDistanceAttenuation(vector.attenuation);
    assert.ok(attenuation);
    assert.ok(
      Math.abs(distanceAttenuationGain(vector.position, attenuation) - vector.expected_gain) < 1e-12,
      vector.id,
    );
  }
});

test("mobile rejects incomplete and out-of-range attenuation", async () => {
  const {
    distanceAttenuationGain,
    normalizeDistanceAttenuation,
  } = await loadSpatialAudio();
  for (const invalid of [
    { model: "linear" },
    {
      model: "linear",
      reference_distance: 2,
      max_distance: 10,
      rolloff_factor: 0,
      min_gain: 0,
      max_gain: 1,
    },
    {
      model: "linear",
      reference_distance: 2,
      max_distance: 10,
      rolloff_factor: 2,
      min_gain: 0,
      max_gain: 1,
    },
    {
      model: "inverse",
      reference_distance: 10,
      max_distance: 2,
      rolloff_factor: 1,
      min_gain: 0,
      max_gain: 1,
    },
    { model: "none", min_gain: 0 },
  ]) {
    assert.equal(normalizeDistanceAttenuation(invalid), null);
  }
  assert.throws(() => distanceAttenuationGain(undefined, {
    model: "inverse",
    reference_distance: 2,
    max_distance: 10,
    rolloff_factor: 1,
    min_gain: 0,
    max_gain: 1,
  }), /requires a spatial position/);
});

test("mobile motion curves match the shared protocol vectors", async () => {
  const {
    audioMotionPosition,
    normalizeAudioMotion,
  } = await loadSpatialAudio();
  for (const vector of CONFORMANCE.motion) {
    const motion = normalizeAudioMotion(vector.automation);
    assert.ok(motion);
    assert.deepEqual(
      [...audioMotionPosition(motion)],
      vector.expected_position,
      vector.id,
    );
  }
});

test("mobile rejects partial and out-of-range motion", async () => {
  const { normalizeAudioMotion } = await loadSpatialAudio();
  for (const invalid of [
    { origin_position: [0, 0, 0] },
    {
      origin_position: [0, 0, 0],
      destination_position: [1, 0, 0],
      duration_ms: 0,
      elapsed_ms: 0,
      easing: "linear",
    },
    {
      origin_position: [0, 0, 0],
      destination_position: [1, 0, 0],
      duration_ms: 100,
      elapsed_ms: 101,
      easing: "linear",
    },
    {
      origin_position: [0, 0, 0],
      destination_position: [1, 0, 0],
      duration_ms: 100,
      elapsed_ms: 0,
      easing: "unknown",
    },
  ]) {
    assert.equal(normalizeAudioMotion(invalid), null);
  }
});

test("mobile source-gain automation matches the shared protocol vectors", async () => {
  const { audioGainAt, normalizeAudioGainAutomation } = await loadSpatialAudio();
  for (const vector of CONFORMANCE.source_gain) {
    const automation = normalizeAudioGainAutomation(vector.automation);
    assert.ok(automation);
    assert.ok(
      Math.abs(audioGainAt(automation) - vector.expected_gain) < 1e-12,
      vector.id,
    );
  }
  assert.equal(normalizeAudioGainAutomation({ origin_gain: 0 }), null);
  assert.equal(normalizeAudioGainAutomation({
    origin_gain: 0,
    destination_gain: 1.1,
    duration_ms: 100,
    elapsed_ms: 0,
    easing: "linear",
  }), null);
});

test("mobile validates complete finite audio sequences atomically", async () => {
  const { normalizeAudioSequenceSegments } = await loadSpatialAudio();
  const segments = normalizeAudioSequenceSegments([
    {
      asset: "throw.ogg",
      position: [0, 1, 0],
      destination_position: null,
      attenuation: null,
      gain: 1,
      easing: "linear",
      next_start_ratio: 0.5,
    },
    {
      asset: "flight.ogg",
      position: [0, 1, 0],
      destination_position: [8, 14, -2],
      attenuation: { model: "none" },
      gain: 0.75,
      easing: "ease-out",
      next_start_ratio: 1,
    },
  ]);
  assert.equal(segments.length, 2);
  assert.deepEqual([...segments[1].destination_position], [8, 14, -2]);
  assert.equal(segments[0].next_start_ratio, 0.5);
  assert.equal(normalizeAudioSequenceSegments([{
    asset: "flight.ogg",
    position: null,
    destination_position: [1, 2, 3],
    attenuation: null,
    gain: 1,
    easing: "linear",
    next_start_ratio: 1,
  }]), null);
  assert.equal(normalizeAudioSequenceSegments([{
    asset: "flight.ogg",
    position: [0, 0, 0],
    destination_position: null,
    attenuation: null,
    gain: 1,
    easing: "ease-out",
    next_start_ratio: 1,
  }]), null);
  assert.equal(normalizeAudioSequenceSegments([{
    asset: "step.ogg",
    position: null,
    destination_position: null,
    attenuation: null,
    gain: 1,
    easing: "linear",
    next_start_ratio: 1.1,
  }]), null);
});
