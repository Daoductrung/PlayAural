// Shared Web and native-renderer spatial policy. Android and iOS consume the
// same validated values through the Cosmos-backed Expo module.

import type {
  AudioGainAutomationPacket,
  AudioMotionPacket,
  DistanceAttenuationPacket,
} from "../network/packets";

export type AudioPosition = readonly [number, number, number];
export type DistanceAttenuation = Readonly<DistanceAttenuationPacket>;
export type AudioMotion = Readonly<{
  origin_position: AudioPosition;
  destination_position: AudioPosition;
  duration_ms: number;
  elapsed_ms: number;
  easing: AudioMotionPacket["easing"];
}>;
export type AudioGainAutomation = Readonly<AudioGainAutomationPacket>;

export const MAX_AUDIO_POSITION = 1000;
const ATTENUATION_PRECISION_SCALE = 1_000_000;
export const MAX_AUDIO_DISTANCE = Math.ceil(
  Math.sqrt(3) * MAX_AUDIO_POSITION * ATTENUATION_PRECISION_SCALE,
) / ATTENUATION_PRECISION_SCALE;
export const MAX_AUDIO_ROLLOFF = 16;
export const MAX_AUDIO_AUTOMATION_MS = 3_600_000;
export const TABLE_RADIUS = 2;
const ATTENUATION_MODELS = new Set(["none", "linear", "inverse", "exponential"]);
const MOTION_EASINGS = new Set(["linear", "ease-in", "ease-out", "ease-in-out"]);

export function normalizeAudioPosition(
  value: unknown,
): AudioPosition | null | undefined {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (!Array.isArray(value) || value.length !== 3) {
    return null;
  }
  if (value.some(
    (coordinate) => !Number.isFinite(coordinate)
      || Math.abs(coordinate) > MAX_AUDIO_POSITION,
  )) {
    return null;
  }
  return Object.freeze([...value]) as AudioPosition;
}

export function panFromPosition(position: AudioPosition): number {
  const [x, y] = position;
  const horizontalDistance = Math.hypot(x, y);
  return horizontalDistance < 1e-6
    ? 0
    : Math.max(-1, Math.min(1, x / horizontalDistance));
}

export function normalizeDistanceAttenuation(
  value: unknown,
): DistanceAttenuation | null | undefined {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const fields = value as Record<string, unknown>;
  const model = fields.model;
  if (typeof model !== "string" || !ATTENUATION_MODELS.has(model)) {
    return null;
  }
  const keys = Object.keys(fields).sort();
  const expected = model === "none"
    ? ["model"]
    : [
      "max_distance",
      "max_gain",
      "min_gain",
      "model",
      "reference_distance",
      "rolloff_factor",
    ];
  if (keys.length !== expected.length || keys.some((key, index) => key !== expected[index])) {
    return null;
  }
  if (model === "none") {
    return Object.freeze({ model: "none" });
  }
  const referenceDistance = fields.reference_distance;
  const maxDistance = fields.max_distance;
  const rolloffFactor = fields.rolloff_factor;
  const minGain = fields.min_gain;
  const maxGain = fields.max_gain;
  if (![referenceDistance, maxDistance, rolloffFactor, minGain, maxGain].every(
    (item) => typeof item === "number" && Number.isFinite(item),
  )) {
    return null;
  }
  const reference = referenceDistance as number;
  const maximum = maxDistance as number;
  const rolloff = rolloffFactor as number;
  const minimumGain = minGain as number;
  const maximumGain = maxGain as number;
  const maximumRolloff = model === "linear" ? 1 : MAX_AUDIO_ROLLOFF;
  if (
    !(reference > 0 && reference < maximum)
    || maximum > MAX_AUDIO_DISTANCE
    || rolloff <= 0
    || rolloff > maximumRolloff
    || minimumGain < 0
    || minimumGain > maximumGain
    || maximumGain > 1
  ) {
    return null;
  }
  return Object.freeze({
    model: model as DistanceAttenuation["model"],
    reference_distance: reference,
    max_distance: maximum,
    rolloff_factor: rolloff,
    min_gain: minimumGain,
    max_gain: maximumGain,
  });
}

export function distanceAttenuationGain(
  position: AudioPosition | undefined,
  attenuation: unknown,
): number {
  const normalized = normalizeDistanceAttenuation(attenuation);
  if (normalized === null) {
    throw new TypeError("Invalid audio attenuation");
  }
  if (!normalized || normalized.model === "none") {
    return 1;
  }
  if (!position) {
    throw new TypeError("Audio attenuation requires a spatial position");
  }
  const referenceDistance = normalized.reference_distance;
  const maxDistance = normalized.max_distance;
  const rolloffFactor = normalized.rolloff_factor;
  const minGain = normalized.min_gain;
  const maxGain = normalized.max_gain;
  const distance = Math.hypot(...position);
  const clampedDistance = Math.min(
    Math.max(distance, referenceDistance),
    maxDistance,
  );
  let gain: number;
  if (normalized.model === "linear") {
    gain = 1 - rolloffFactor * (
      (clampedDistance - referenceDistance)
      / (maxDistance - referenceDistance)
    );
  } else if (normalized.model === "inverse") {
    gain = referenceDistance / (
      referenceDistance
      + rolloffFactor * (clampedDistance - referenceDistance)
    );
  } else {
    gain = (clampedDistance / referenceDistance) ** -rolloffFactor;
  }
  return Math.max(minGain, Math.min(maxGain, gain));
}

export function normalizeAudioMotion(
  value: unknown,
): AudioMotion | null | undefined {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const fields = value as Record<string, unknown>;
  const keys = Object.keys(fields).sort();
  const expected = [
    "destination_position",
    "duration_ms",
    "easing",
    "elapsed_ms",
    "origin_position",
  ];
  if (keys.length !== expected.length || keys.some((key, index) => key !== expected[index])) {
    return null;
  }
  const origin = normalizeAudioPosition(fields.origin_position);
  const destination = normalizeAudioPosition(fields.destination_position);
  const duration = fields.duration_ms;
  const elapsed = fields.elapsed_ms;
  const easing = fields.easing;
  if (
    !origin
    || !destination
    || !Number.isSafeInteger(duration)
    || (duration as number) <= 0
    || (duration as number) > MAX_AUDIO_AUTOMATION_MS
    || !Number.isSafeInteger(elapsed)
    || (elapsed as number) < 0
    || (elapsed as number) > (duration as number)
    || typeof easing !== "string"
    || !MOTION_EASINGS.has(easing)
  ) {
    return null;
  }
  return Object.freeze({
    origin_position: origin,
    destination_position: destination,
    duration_ms: duration as number,
    elapsed_ms: elapsed as number,
    easing: easing as AudioMotion["easing"],
  });
}

export function normalizeAudioGain(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 1
    ? value
    : null;
}

export function normalizeAudioGainAutomation(
  value: unknown,
): AudioGainAutomation | null | undefined {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const fields = value as Record<string, unknown>;
  const keys = Object.keys(fields).sort();
  const expected = [
    "destination_gain",
    "duration_ms",
    "easing",
    "elapsed_ms",
    "origin_gain",
  ];
  if (keys.length !== expected.length || keys.some((key, index) => key !== expected[index])) {
    return null;
  }
  const origin = normalizeAudioGain(fields.origin_gain);
  const destination = normalizeAudioGain(fields.destination_gain);
  const duration = fields.duration_ms;
  const elapsed = fields.elapsed_ms;
  const easing = fields.easing;
  if (
    origin === null
    || destination === null
    || !Number.isSafeInteger(duration)
    || (duration as number) <= 0
    || (duration as number) > MAX_AUDIO_AUTOMATION_MS
    || !Number.isSafeInteger(elapsed)
    || (elapsed as number) < 0
    || (elapsed as number) > (duration as number)
    || typeof easing !== "string"
    || !MOTION_EASINGS.has(easing)
  ) {
    return null;
  }
  return Object.freeze({
    origin_gain: origin,
    destination_gain: destination,
    duration_ms: duration as number,
    elapsed_ms: elapsed as number,
    easing: easing as AudioGainAutomation["easing"],
  });
}

export function audioMotionProgress(
  progress: number,
  easing: AudioMotion["easing"],
): number {
  const bounded = Math.max(0, Math.min(1, progress));
  if (easing === "linear") return bounded;
  if (easing === "ease-in") return bounded * bounded;
  if (easing === "ease-out") return 1 - ((1 - bounded) ** 2);
  return bounded < 0.5
    ? 2 * bounded * bounded
    : 1 - (((-2 * bounded + 2) ** 2) / 2);
}

export function audioMotionPosition(
  motion: AudioMotion,
  elapsedMs = motion.elapsed_ms,
): AudioPosition {
  const ratio = audioMotionProgress(
    elapsedMs / motion.duration_ms,
    motion.easing,
  );
  return Object.freeze(motion.origin_position.map(
    (origin, index) => origin
      + ((motion.destination_position[index] - origin) * ratio),
  )) as unknown as AudioPosition;
}

export function audioGainAt(
  automation: AudioGainAutomation,
  elapsedMs = automation.elapsed_ms,
): number {
  const ratio = audioMotionProgress(
    elapsedMs / automation.duration_ms,
    automation.easing,
  );
  return automation.origin_gain
    + ((automation.destination_gain - automation.origin_gain) * ratio);
}

export function toWebAudioPosition(
  position: AudioPosition,
): AudioPosition {
  const [x, y, z] = position;
  return Object.freeze([x, z, -y]);
}

export function setAudioSpatializerPosition(
  panner: AudioNode,
  context: AudioContext,
  position: AudioPosition,
): void {
  const [x, y, z] = toWebAudioPosition(position);
  const positioned = panner as PannerNode;
  if (
    positioned.positionX?.setValueAtTime
    && positioned.positionY?.setValueAtTime
    && positioned.positionZ?.setValueAtTime
  ) {
    positioned.positionX.setValueAtTime(x, context.currentTime);
    positioned.positionY.setValueAtTime(y, context.currentTime);
    positioned.positionZ.setValueAtTime(z, context.currentTime);
  } else if (typeof positioned.setPosition === "function") {
    positioned.setPosition(x, y, z);
  } else {
    const stereo = panner as StereoPannerNode;
    stereo.pan?.setValueAtTime(panFromPosition(position), context.currentTime);
  }
}

export function createWebAudioSpatializer(
  context: AudioContext,
  { position, pan = 0 }: { position?: AudioPosition; pan?: number } = {},
): AudioNode | undefined {
  if (
    position
    && typeof context.createPanner === "function"
  ) {
    try {
      const panner = context.createPanner();
      panner.panningModel = "HRTF";
      panner.distanceModel = "inverse";
      panner.refDistance = TABLE_RADIUS;
      panner.maxDistance = MAX_AUDIO_POSITION;
      panner.rolloffFactor = 0;
      setAudioSpatializerPosition(panner, context, position);
      return panner;
    } catch {
      // Preserve directional stereo on partial Web Audio implementations.
    }
  }
  if (typeof context.createStereoPanner === "function") {
    try {
      const panner = context.createStereoPanner();
      panner.pan.value = position
        ? panFromPosition(position)
        : Math.max(-1, Math.min(1, Number.isFinite(pan) ? pan : 0));
      return panner;
    } catch {
      // Direct connection is the final capability fallback.
    }
  }
  return undefined;
}
