// Shared Web Audio spatialization policy for every server-driven source.
// Server coordinates are listener-relative: +X right, +Y forward, +Z up.

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

export function normalizeAudioPosition(value) {
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
  return Object.freeze([...value]);
}

export function panFromPosition(position) {
  const [x, y] = position;
  const horizontalDistance = Math.hypot(x, y);
  return horizontalDistance < 1e-6
    ? 0
    : Math.max(-1, Math.min(1, x / horizontalDistance));
}

export function normalizeDistanceAttenuation(value) {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const model = value.model;
  if (!ATTENUATION_MODELS.has(model)) {
    return null;
  }
  const keys = Object.keys(value).sort();
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
    return Object.freeze({ model });
  }
  const {
    reference_distance: referenceDistance,
    max_distance: maxDistance,
    rolloff_factor: rolloffFactor,
    min_gain: minGain,
    max_gain: maxGain,
  } = value;
  if (![referenceDistance, maxDistance, rolloffFactor, minGain, maxGain].every(
    (item) => typeof item === "number" && Number.isFinite(item),
  )) {
    return null;
  }
  const maximumRolloff = model === "linear" ? 1 : MAX_AUDIO_ROLLOFF;
  if (
    !(referenceDistance > 0 && referenceDistance < maxDistance)
    || maxDistance > MAX_AUDIO_DISTANCE
    || rolloffFactor <= 0
    || rolloffFactor > maximumRolloff
    || minGain < 0
    || minGain > maxGain
    || maxGain > 1
  ) {
    return null;
  }
  return Object.freeze({
    model,
    reference_distance: referenceDistance,
    max_distance: maxDistance,
    rolloff_factor: rolloffFactor,
    min_gain: minGain,
    max_gain: maxGain,
  });
}

export function distanceAttenuationGain(position, attenuation) {
  const normalized = normalizeDistanceAttenuation(attenuation);
  if (normalized === null) {
    throw new TypeError("Invalid audio attenuation");
  }
  if (normalized === undefined || normalized.model === "none") {
    return 1;
  }
  if (!position) {
    throw new TypeError("Audio attenuation requires a spatial position");
  }
  const distance = Math.hypot(...position);
  const clampedDistance = Math.min(
    Math.max(distance, normalized.reference_distance),
    normalized.max_distance,
  );
  let gain;
  if (normalized.model === "linear") {
    gain = 1 - normalized.rolloff_factor * (
      (clampedDistance - normalized.reference_distance)
      / (normalized.max_distance - normalized.reference_distance)
    );
  } else if (normalized.model === "inverse") {
    gain = normalized.reference_distance / (
      normalized.reference_distance
      + normalized.rolloff_factor
      * (clampedDistance - normalized.reference_distance)
    );
  } else {
    gain = (clampedDistance / normalized.reference_distance)
      ** -normalized.rolloff_factor;
  }
  return Math.max(normalized.min_gain, Math.min(normalized.max_gain, gain));
}

export function normalizeAudioMotion(value) {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const keys = Object.keys(value).sort();
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
  const origin = normalizeAudioPosition(value.origin_position);
  const destination = normalizeAudioPosition(value.destination_position);
  if (!origin || !destination) {
    return null;
  }
  if (
    !Number.isSafeInteger(value.duration_ms)
    || value.duration_ms <= 0
    || value.duration_ms > MAX_AUDIO_AUTOMATION_MS
    || !Number.isSafeInteger(value.elapsed_ms)
    || value.elapsed_ms < 0
    || value.elapsed_ms > value.duration_ms
    || !MOTION_EASINGS.has(value.easing)
  ) {
    return null;
  }
  return Object.freeze({
    origin_position: origin,
    destination_position: destination,
    duration_ms: value.duration_ms,
    elapsed_ms: value.elapsed_ms,
    easing: value.easing,
  });
}

export function normalizeAudioGain(value) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 1
    ? value
    : null;
}

export function normalizeAudioGainAutomation(value) {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const keys = Object.keys(value).sort();
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
  const origin = normalizeAudioGain(value.origin_gain);
  const destination = normalizeAudioGain(value.destination_gain);
  if (
    origin === null
    || destination === null
    || !Number.isSafeInteger(value.duration_ms)
    || value.duration_ms <= 0
    || value.duration_ms > MAX_AUDIO_AUTOMATION_MS
    || !Number.isSafeInteger(value.elapsed_ms)
    || value.elapsed_ms < 0
    || value.elapsed_ms > value.duration_ms
    || !MOTION_EASINGS.has(value.easing)
  ) {
    return null;
  }
  return Object.freeze({
    origin_gain: origin,
    destination_gain: destination,
    duration_ms: value.duration_ms,
    elapsed_ms: value.elapsed_ms,
    easing: value.easing,
  });
}

export function audioMotionProgress(progress, easing) {
  const bounded = Math.max(0, Math.min(1, progress));
  if (easing === "linear") return bounded;
  if (easing === "ease-in") return bounded * bounded;
  if (easing === "ease-out") return 1 - ((1 - bounded) ** 2);
  if (easing === "ease-in-out") {
    return bounded < 0.5
      ? 2 * bounded * bounded
      : 1 - (((-2 * bounded + 2) ** 2) / 2);
  }
  throw new TypeError("Unknown audio motion easing");
}

export function audioMotionPosition(motion, elapsedMs = undefined) {
  const normalized = normalizeAudioMotion(motion);
  if (!normalized) {
    throw new TypeError("Invalid audio motion");
  }
  const elapsed = elapsedMs ?? normalized.elapsed_ms;
  const ratio = audioMotionProgress(
    elapsed / normalized.duration_ms,
    normalized.easing,
  );
  return Object.freeze(normalized.origin_position.map(
    (origin, index) => origin
      + ((normalized.destination_position[index] - origin) * ratio),
  ));
}

export function audioGainAt(automation, elapsedMs = undefined) {
  const normalized = normalizeAudioGainAutomation(automation);
  if (!normalized) {
    throw new TypeError("Invalid audio gain automation");
  }
  const elapsed = elapsedMs ?? normalized.elapsed_ms;
  const ratio = audioMotionProgress(
    elapsed / normalized.duration_ms,
    normalized.easing,
  );
  return normalized.origin_gain
    + ((normalized.destination_gain - normalized.origin_gain) * ratio);
}

export function toWebAudioPosition(position) {
  const [x, y, z] = position;
  // Web Audio's default listener faces -Z with +Y up.
  return Object.freeze([x, z, -y]);
}

export function setAudioSpatializerPosition(panner, context, position) {
  const [x, y, z] = toWebAudioPosition(position);
  if (
    panner.positionX?.setValueAtTime
    && panner.positionY?.setValueAtTime
    && panner.positionZ?.setValueAtTime
  ) {
    panner.positionX.setValueAtTime(x, context.currentTime);
    panner.positionY.setValueAtTime(y, context.currentTime);
    panner.positionZ.setValueAtTime(z, context.currentTime);
  } else if (typeof panner.setPosition === "function") {
    panner.setPosition(x, y, z);
  } else if (panner.pan) {
    panner.pan.setValueAtTime?.(panFromPosition(position), context.currentTime);
    if (!panner.pan.setValueAtTime) {
      panner.pan.value = panFromPosition(position);
    }
  }
}

export function createAudioSpatializer(context, { position, pan = 0 } = {}) {
  const normalizedPosition = normalizeAudioPosition(position);
  if (normalizedPosition === null) {
    return null;
  }
  if (
    normalizedPosition
    && typeof context.createPanner === "function"
  ) {
    try {
      const panner = context.createPanner();
      panner.panningModel = "HRTF";
      // Direction and distance gain are deliberately separate: the shared
      // mixer applies the validated protocol curve exactly once.
      panner.distanceModel = "inverse";
      panner.refDistance = TABLE_RADIUS;
      panner.maxDistance = MAX_AUDIO_POSITION;
      panner.rolloffFactor = 0;
      setAudioSpatializerPosition(panner, context, normalizedPosition);
      return panner;
    } catch {
      // A partial Web Audio implementation still gets the stereo fallback.
    }
  }
  if (typeof context.createStereoPanner === "function") {
    try {
      const panner = context.createStereoPanner();
      const fallbackPan = normalizedPosition
        ? panFromPosition(normalizedPosition)
        : Math.max(-1, Math.min(1, Number.isFinite(Number(pan)) ? Number(pan) : 0));
      panner.pan.value = fallbackPan;
      return panner;
    } catch {
      // Direct connection is the final capability fallback.
    }
  }
  return undefined;
}
