import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  MAX_AUDIO_POSITION,
  TABLE_RADIUS,
  audioGainAt,
  audioMotionPosition,
  createAudioSpatializer,
  distanceAttenuationGain,
  normalizeAudioGainAutomation,
  normalizeAudioMotion,
  normalizeAudioPosition,
  normalizeDistanceAttenuation,
  panFromPosition,
  setAudioSpatializerPosition,
  toWebAudioPosition,
} from "../spatial_audio.js";

const CONFORMANCE = JSON.parse(readFileSync(
  new URL("../../audio_protocol_v3_conformance.json", import.meta.url),
  "utf8",
));

function audioParam() {
  return {
    calls: [],
    setValueAtTime(value, time) {
      this.calls.push([value, time]);
    },
  };
}

test("audio positions are finite, bounded triples", () => {
  assert.deepEqual(normalizeAudioPosition([2, -1, 0.5]), [2, -1, 0.5]);
  assert.equal(normalizeAudioPosition(undefined), undefined);
  assert.equal(normalizeAudioPosition(null), undefined);
  for (const invalid of [
    [1, 2],
    [1, 2, 3, 4],
    "1,2,3",
    ["1", 2, 3],
    [true, 0, 0],
    [Infinity, 0, 0],
    [MAX_AUDIO_POSITION + 1, 0, 0],
  ]) {
    assert.equal(normalizeAudioPosition(invalid), null);
  }
});

test("server coordinates map to Web Audio without losing elevation", () => {
  assert.deepEqual(toWebAudioPosition([2, 3, 4]), [2, 4, -3]);
  assert.equal(panFromPosition([0, -2, 0]), 0);
  assert.equal(panFromPosition([2, 0, 0]), 1);
  assert.equal(panFromPosition([-2, 0, 0]), -1);
});

test("positioned sources use full Web Audio HRTF with neutral distance gain", () => {
  const panner = {
    positionX: audioParam(),
    positionY: audioParam(),
    positionZ: audioParam(),
  };
  const context = { currentTime: 7, createPanner: () => panner };

  assert.equal(createAudioSpatializer(context, { position: [2, 3, 4] }), panner);
  assert.equal(panner.panningModel, "HRTF");
  assert.equal(panner.distanceModel, "inverse");
  assert.equal(panner.refDistance, TABLE_RADIUS);
  assert.equal(panner.maxDistance, MAX_AUDIO_POSITION);
  assert.equal(panner.rolloffFactor, 0);
  assert.deepEqual(panner.positionX.calls, [[2, 7]]);
  assert.deepEqual(panner.positionY.calls, [[4, 7]]);
  assert.deepEqual(panner.positionZ.calls, [[-3, 7]]);

  const colocated = {
    positionX: audioParam(),
    positionY: audioParam(),
    positionZ: audioParam(),
  };
  assert.equal(
    createAudioSpatializer({ currentTime: 8, createPanner: () => colocated }, {
      position: [0, 0, 0],
    }),
    colocated,
  );
  setAudioSpatializerPosition(colocated, { currentTime: 9 }, [1, 2, 3]);
  assert.deepEqual(colocated.positionX.calls.at(-1), [1, 9]);
  assert.deepEqual(colocated.positionY.calls.at(-1), [3, 9]);
  assert.deepEqual(colocated.positionZ.calls.at(-1), [-2, 9]);
});

test("older PannerNode and stereo-only browsers retain directional fallback", () => {
  const legacy = { calls: [], setPosition(...values) { this.calls.push(values); } };
  assert.equal(
    createAudioSpatializer({ currentTime: 0, createPanner: () => legacy }, {
      position: [0, -2, 1],
    }),
    legacy,
  );
  assert.deepEqual(legacy.calls, [[0, 1, 2]]);

  const stereo = { pan: { value: 0 } };
  assert.equal(
    createAudioSpatializer({ createStereoPanner: () => stereo }, {
      position: [-2, 0, 0],
      pan: 0,
    }),
    stereo,
  );
  assert.equal(stereo.pan.value, -1);

  const degraded = { pan: { value: 0 } };
  assert.equal(
    createAudioSpatializer({
      createPanner() { throw new Error("HRTF unavailable"); },
      createStereoPanner: () => degraded,
    }, { position: [2, 0, 0] }),
    degraded,
  );
  assert.equal(degraded.pan.value, 1);

  const colocated = { pan: { value: 1 } };
  assert.equal(
    createAudioSpatializer({
      createPanner() { throw new Error("co-located sources are not directional"); },
      createStereoPanner: () => colocated,
    }, { position: [0, 0, 0] }),
    colocated,
  );
  assert.equal(colocated.pan.value, 0);
});

test("malformed positions never create an audio node", () => {
  assert.equal(createAudioSpatializer({ createPanner() { throw new Error(); } }, {
    position: [NaN, 0, 0],
  }), null);
});

test("distance attenuation matches the shared protocol vectors", () => {
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

test("attenuation is strict, bounded, and can be explicitly disabled", () => {
  assert.deepEqual(normalizeDistanceAttenuation({ model: "none" }), { model: "none" });
  assert.equal(distanceAttenuationGain([100, 0, 0], { model: "none" }), 1);
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

test("motion curves match the shared protocol vectors", () => {
  for (const vector of CONFORMANCE.motion) {
    const motion = normalizeAudioMotion(vector.automation);
    assert.ok(motion);
    assert.deepEqual(audioMotionPosition(motion), vector.expected_position, vector.id);
  }
});

test("motion validation rejects partial and out-of-range objects", () => {
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

test("source-gain automation matches the shared protocol vectors", () => {
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
    origin_gain: -0.1,
    destination_gain: 1,
    duration_ms: 100,
    elapsed_ms: 0,
    easing: "linear",
  }), null);
});
