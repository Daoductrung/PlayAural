import { soundFamilies } from "./generated/soundManifest.js";
import {
  audioGainAt,
  audioMotionProgress,
  audioMotionPosition,
  createAudioSpatializer,
  distanceAttenuationGain,
  normalizeAudioGain,
  normalizeAudioGainAutomation,
  normalizeAudioMotion,
  normalizeAudioPosition,
  normalizeDistanceAttenuation,
  panFromPosition,
  setAudioSpatializerPosition,
} from "./spatial_audio.js";

const AUDIO_PROTOCOL_VERSION = 3;
const AUDIO_OUTPUT_BUFFERS = new Set(["chat", "private", "game", "system", "misc"]);
const MAX_ACTIVE_EFFECTS = 64;
const MAX_ACTIVE_LAYERS = 32;
const MAX_CACHED_EFFECTS = 128;
const MAX_CACHED_BUFFER_BYTES = 96 * 1024 * 1024;
const MAX_PENDING_EFFECTS = 32;
const MAX_GENERATION_ENTRIES = 512;
const MAX_FADE_MS = 60000;
const MAX_AUDIO_SEQUENCE_SEGMENTS = 32;
const SEQUENCE_START_LEAD_SECONDS = 0.05;
const WEB_AUDIO_TAIL_FFT_SIZE = 256;
const WEB_AUDIO_TAIL_POLL_MS = 16;
const WEB_AUDIO_TAIL_SILENCE_POLLS = 2;
const WEB_AUDIO_TAIL_TIMEOUT_MS = 2000;
const AUDIO_CONTEXT_TRANSITION_TIMEOUT_MS = 1500;
const AUDIO_CONTEXT_HEALTH_CHECK_MS = 250;
const AUDIO_SESSION_PLAYBACK = "playback";
const AUDIO_SESSION_PLAY_AND_RECORD = "play-and-record";
const VORBIS_DECODER_MODULE = "./vendor/stb-vorbis.js";

let vorbisDecoderModulePromise = null;

function clamp(value, minimum, maximum, fallback) {
  const parsed = Number(value);
  return Math.max(minimum, Math.min(maximum, Number.isFinite(parsed) ? parsed : fallback));
}

function validAsset(name) {
  const normalized = String(name || "").trim().replaceAll("\\", "/");
  if (
    !normalized
    || normalized.length > 256
    || normalized.startsWith("/")
    || normalized.includes(":")
    || normalized.includes("?")
    || normalized.includes("#")
  ) {
    return "";
  }
  const parts = normalized.split("/");
  return parts.some((part) => !part || part === "." || part === "..") ? "" : normalized;
}

function validFamily(name) {
  const normalized = String(name || "").trim().replaceAll("\\", "/");
  if (!normalized || normalized.split("/").at(-1).includes(".")) {
    return "";
  }
  return validAsset(`${normalized}1.ogg`) ? normalized : "";
}

function soundFamilyVariants(name) {
  const family = validFamily(name);
  if (!family || !Object.prototype.hasOwnProperty.call(soundFamilies, family)) {
    return [];
  }
  return soundFamilies[family] || [];
}

function resolveSoundPacket(packet) {
  // Randomization is opt-in through `family`. A numbered `asset` is always
  // validated and played as the exact path supplied by the server.
  const hasAsset = Boolean(packet.asset);
  const hasFamily = Boolean(packet.family);
  if (hasAsset === hasFamily) {
    return null;
  }
  const asset = hasAsset ? validAsset(packet.asset) : "";
  const family = hasFamily ? validFamily(packet.family) : "";
  if (hasAsset && !asset || hasFamily && !family) {
    return null;
  }
  if (!family) {
    return { ...packet, asset };
  }
  if (packet.kind && packet.kind !== "sfx" || packet.loop) {
    return null;
  }
  const variants = soundFamilyVariants(family);
  if (!variants.length) {
    return null;
  }
  const selected = variants[Math.floor(Math.random() * variants.length)];
  return { ...packet, asset: selected, family: "" };
}

function validId(value) {
  return /^[A-Za-z0-9_.:-]{1,128}$/.test(String(value || ""));
}

function normalizeDucking(ducking) {
  return new Map(Object.entries(ducking || {}).map(
    ([bus, gain]) => [String(bus), clamp(gain, 0, 100, 100) / 100],
  ));
}

function normalizeSpatialFields(packet) {
  const position = normalizeAudioPosition(packet.position);
  const attenuation = normalizeDistanceAttenuation(packet.attenuation);
  if (position === null || attenuation === null || (attenuation && !position)) {
    return null;
  }
  return {
    position,
    attenuation,
    distanceGain: distanceAttenuationGain(position, attenuation),
  };
}

function normalizeSequenceSegments(value) {
  if (value === undefined) {
    return [];
  }
  if (!Array.isArray(value) || !value.length || value.length > MAX_AUDIO_SEQUENCE_SEGMENTS) {
    return null;
  }
  const expected = [
    "asset",
    "attenuation",
    "destination_position",
    "easing",
    "gain",
    "next_start_ratio",
    "position",
  ];
  const normalized = [];
  for (const item of value) {
    if (
      !item
      || typeof item !== "object"
      || Array.isArray(item)
      || Object.keys(item).sort().join("\0") !== expected.join("\0")
    ) {
      return null;
    }
    const asset = validAsset(item.asset);
    const position = normalizeAudioPosition(item.position);
    const destination = normalizeAudioPosition(item.destination_position);
    const attenuation = normalizeDistanceAttenuation(item.attenuation);
    const gain = normalizeAudioGain(item.gain);
    const nextStartRatio = normalizeAudioGain(item.next_start_ratio);
    const easing = String(item.easing || "");
    if (
      !asset
      || position === null
      || destination === null
      || attenuation === null
      || gain === null
      || nextStartRatio === null
      || attenuation !== undefined && position === undefined
      || destination !== undefined && position === undefined
      || !["linear", "ease-in", "ease-out", "ease-in-out"].includes(easing)
      || destination === undefined && easing !== "linear"
    ) {
      return null;
    }
    normalized.push({
      asset,
      position,
      destination_position: destination,
      attenuation,
      gain,
      easing,
      next_start_ratio: nextStartRatio,
    });
  }
  return normalized;
}

function assetUrl(name, baseUrl, version) {
  const asset = validAsset(name);
  if (!asset) {
    return "";
  }
  const base = String(baseUrl || "./sounds/").replace(/\/?$/, "/");
  const url = new URL(`${base}${asset}`, window.location.href);
  if (version) {
    url.searchParams.set("v", version);
  }
  return url.href;
}

function sourceId() {
  return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`;
}

export function configureBrowserAudioSession(audioSession, microphoneActive = false) {
  if (!audioSession) {
    return false;
  }
  const type = microphoneActive
    ? AUDIO_SESSION_PLAY_AND_RECORD
    : AUDIO_SESSION_PLAYBACK;
  try {
    if (audioSession.type !== type) {
      audioSession.type = type;
    }
    return audioSession.type === type;
  } catch {
    return false;
  }
}

export function createAudioBufferFromChannels(context, decoded) {
  const channels = decoded?.channels;
  const sampleRate = Number(decoded?.sampleRate);
  const sampleCount = channels?.[0]?.length;
  if (
    !context
    || !Array.isArray(channels)
    || !channels.length
    || !Number.isInteger(sampleRate)
    || sampleRate <= 0
    || !Number.isInteger(sampleCount)
    || sampleCount <= 0
    || channels.some(
      (channel) => !(channel instanceof Float32Array) || channel.length !== sampleCount,
    )
  ) {
    return null;
  }
  try {
    const buffer = context.createBuffer(channels.length, sampleCount, sampleRate);
    channels.forEach((channel, index) => {
      if (typeof buffer.copyToChannel === "function") {
        buffer.copyToChannel(channel, index);
      } else {
        buffer.getChannelData(index).set(channel);
      }
    });
    return buffer;
  } catch {
    return null;
  }
}

async function decodeVorbisFallback(context, bytes) {
  if (!vorbisDecoderModulePromise) {
    vorbisDecoderModulePromise = import(VORBIS_DECODER_MODULE)
      .then(async ({ StbVorbis }) => {
        await StbVorbis.ready;
        return StbVorbis;
      })
      .catch(() => {
        vorbisDecoderModulePromise = null;
        return null;
      });
  }
  const decoder = await vorbisDecoderModulePromise;
  if (!decoder) {
    return null;
  }
  try {
    return createAudioBufferFromChannels(context, decoder.decode(bytes));
  } catch {
    return null;
  }
}

export function createAudioEngine(options = {}) {
  const audioSession = options.audioSession === undefined
    ? window.navigator?.audioSession
    : options.audioSession;
  let microphoneActive = false;
  configureBrowserAudioSession(audioSession, microphoneActive);
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  const context = AudioContextClass ? new AudioContextClass() : null;
  const masters = {};
  const busNodes = new Map();
  const busGains = new Map();
  const duckRequests = new Map();
  const sources = new Map();
  const handles = new Map();
  const targets = new Map();
  const generations = new Map();
  const targetGenerations = new Map();
  const motions = new Map();
  const gainAutomations = new Map();
  const effectBuffers = new Map();
  const effectBufferSizes = new Map();
  let effectBufferBytes = 0;
  const pendingEffects = [];
  const pendingMusic = new Map();
  const pendingAmbiences = new Map();
  const pausedMusicHandles = new Set();
  let finiteSfxLaunchQueue = Promise.resolve();
  let contextRecovery = null;
  let foregroundRecovery = null;
  let contextHasRun = context?.state === "running";

  let soundBaseUrl = options.soundBaseUrl || "./sounds/";
  let soundVersion = String(options.soundVersion || "");
  let muted = false;
  const masterValues = {
    sfx: clamp(options.effectsVolumePercent ?? 100, 0, 100, 100) / 100,
    music: clamp(options.musicVolumePercent ?? 20, 0, 100, 20) / 100,
    ambience: clamp(options.ambienceVolumePercent ?? 100, 0, 100, 100) / 100,
  };

  if (context) {
    for (const kind of ["sfx", "music", "ambience"]) {
      masters[kind] = context.createGain();
      masters[kind].gain.value = masterValues[kind];
      masters[kind].connect(context.destination);
    }
    context.addEventListener?.("statechange", () => {
      if (context.state === "running") {
        contextHasRun = true;
        retryPendingPlayback();
      }
    });
  }

  function nextGeneration(handle) {
    motions.delete(handle);
    gainAutomations.delete(handle);
    const next = (generations.get(handle) || 0) + 1;
    generations.delete(handle);
    generations.set(handle, next);
    while (generations.size > MAX_GENERATION_ENTRIES) {
      const removable = [...generations.keys()].find(
        (candidate) => !handles.has(candidate),
      );
      if (!removable) {
        break;
      }
      generations.delete(removable);
      motions.delete(removable);
      gainAutomations.delete(removable);
    }
    return next;
  }

  function targetOf(packet) {
    return `${packet.kind || ""}:${packet.scope || "global"}:${packet.context || ""}:${packet.layer || "main"}`;
  }

  function nextTargetGeneration(target) {
    const next = (targetGenerations.get(target) || 0) + 1;
    targetGenerations.delete(target);
    targetGenerations.set(target, next);
    while (targetGenerations.size > MAX_GENERATION_ENTRIES) {
      const removable = [...targetGenerations.keys()].find(
        (candidate) => !targets.has(candidate) && !pendingAmbiences.has(candidate),
      );
      if (!removable) {
        break;
      }
      targetGenerations.delete(removable);
    }
    return next;
  }

  function duckGain(bus) {
    let gain = 1;
    for (const request of duckRequests.values()) {
      if (request.has(bus)) {
        gain = Math.min(gain, request.get(bus));
      }
    }
    return gain;
  }

  function effectiveBusGain(bus) {
    return (busGains.get(bus) ?? 1) * duckGain(bus);
  }

  function refreshBus(bus) {
    for (const [key, record] of busNodes) {
      if (record.bus !== bus) {
        continue;
      }
      record.node.gain.setValueAtTime(effectiveBusGain(bus), context.currentTime);
    }
    for (const source of sources.values()) {
      if (!source.output && source.bus === bus && source.audio) {
        source.audio.volume = muted ? 0 : (source.mixLevel ?? source.baseVolume)
          * source.distanceGain * source.sourceGain
          * masterValues[source.kind] * effectiveBusGain(bus);
      }
    }
  }

  function refreshDucking() {
    const names = new Set([...busGains.keys()]);
    for (const request of duckRequests.values()) {
      for (const bus of request.keys()) {
        names.add(bus);
      }
    }
    for (const source of sources.values()) {
      names.add(source.bus);
    }
    for (const bus of names) {
      refreshBus(bus);
    }
  }

  function busNode(kind, bus) {
    if (!context) {
      return null;
    }
    const key = `${kind}:${bus}`;
    if (!busNodes.has(key)) {
      const node = context.createGain();
      node.gain.value = effectiveBusGain(bus);
      node.connect(masters[kind] || context.destination);
      busNodes.set(key, { kind, bus, node });
    }
    return busNodes.get(key).node;
  }

  function setOutputValue(source, value) {
    const bounded = clamp(value, 0, 1, 0);
    source.mixLevel = bounded;
    const effective = bounded * source.distanceGain * source.sourceGain;
    if (source.output && context) {
      source.output.gain.setValueAtTime(effective, context.currentTime);
    } else if (source.audio) {
      source.audio.volume = muted ? 0 : effective
        * masterValues[source.kind] * effectiveBusGain(source.bus);
    }
  }

  function audioClockMs() {
    return context ? context.currentTime * 1000 : performance.now();
  }

  function applyMotionFrame(record) {
    if (
      motions.get(record.handle) !== record
      || generations.get(record.handle) !== record.generation
    ) {
      return true;
    }
    const elapsed = Math.min(
      record.motion.duration_ms,
      Math.max(0, audioClockMs() - record.startedAt),
    );
    const sourceKey = handles.get(record.handle);
    const source = sourceKey ? sources.get(sourceKey) : null;
    if (source) {
      if (source.kind !== record.kind || source.generation !== record.generation) {
        motions.delete(record.handle);
        return true;
      }
      const position = audioMotionPosition(record.motion, elapsed);
      source.position = position;
      source.pan = panFromPosition(position) * 100;
      if (source.panner && context) {
        setAudioSpatializerPosition(source.panner, context, position);
      }
      source.distanceGain = distanceAttenuationGain(position, source.attenuation);
      setOutputValue(source, outputValue(source));
    }
    if (elapsed >= record.motion.duration_ms) {
      // An update can finish while a cold asset is still decoding. Retain its
      // final value until register() installs that generation; otherwise the
      // late source would remain forever at the play packet's old position.
      if (source) {
        motions.delete(record.handle);
      }
      return true;
    }
    return false;
  }

  function scheduleMotionFrame(record) {
    const schedule = window.requestAnimationFrame
      || ((callback) => window.setTimeout(callback, 16));
    schedule(() => {
      if (!applyMotionFrame(record)) {
        scheduleMotionFrame(record);
      }
    });
  }

  function startSourceMotion(kind, handle, motion) {
    const generation = generations.get(handle);
    const sourceKey = handles.get(handle);
    const source = sourceKey ? sources.get(sourceKey) : null;
    if (source && source.kind !== kind) {
      return false;
    }
    if (generation === undefined) {
      return true;
    }
    const record = {
      handle,
      kind,
      generation,
      motion,
      startedAt: audioClockMs() - motion.elapsed_ms,
    };
    motions.set(handle, record);
    const complete = applyMotionFrame(record);
    if (!complete && motions.get(handle) === record) {
      scheduleMotionFrame(record);
    }
    return true;
  }

  function applyGainFrame(record) {
    if (
      gainAutomations.get(record.handle) !== record
      || generations.get(record.handle) !== record.generation
    ) {
      return true;
    }
    const elapsed = Math.min(
      record.automation.duration_ms,
      Math.max(0, audioClockMs() - record.startedAt),
    );
    const sourceKey = handles.get(record.handle);
    const source = sourceKey ? sources.get(sourceKey) : null;
    if (source) {
      if (source.kind !== record.kind || source.generation !== record.generation) {
        gainAutomations.delete(record.handle);
        return true;
      }
      source.sourceGain = audioGainAt(record.automation, elapsed);
      setOutputValue(source, outputValue(source));
    }
    if (elapsed >= record.automation.duration_ms) {
      // Keep a completed update until an asynchronously loaded source has
      // consumed its destination value. nextGeneration() still bounds and
      // invalidates records for sources that never install.
      if (source) {
        gainAutomations.delete(record.handle);
      }
      return true;
    }
    return false;
  }

  function scheduleGainFrame(record) {
    const schedule = window.requestAnimationFrame
      || ((callback) => window.setTimeout(callback, 16));
    schedule(() => {
      if (!applyGainFrame(record)) {
        scheduleGainFrame(record);
      }
    });
  }

  function startSourceGainAutomation(kind, handle, automation) {
    const generation = generations.get(handle);
    const sourceKey = handles.get(handle);
    const source = sourceKey ? sources.get(sourceKey) : null;
    if (source && source.kind !== kind) {
      return false;
    }
    if (generation === undefined) {
      return true;
    }
    const record = {
      handle,
      kind,
      generation,
      automation,
      startedAt: audioClockMs() - automation.elapsed_ms,
    };
    gainAutomations.set(handle, record);
    const complete = applyGainFrame(record);
    if (!complete && gainAutomations.get(handle) === record) {
      scheduleGainFrame(record);
    }
    return true;
  }

  function cancelPendingHandle(handle) {
    const resolved = String(handle || "");
    if (!resolved) {
      return;
    }
    for (let index = pendingEffects.length - 1; index >= 0; index -= 1) {
      if (pendingEffects[index].handle === resolved) {
        pendingEffects.splice(index, 1);
      }
    }
    for (const [target, packet] of pendingMusic) {
      if (packet.handle === resolved) {
        pendingMusic.delete(target);
      }
    }
    for (const [target, packet] of pendingAmbiences) {
      if (packet.handle === resolved) {
        pendingAmbiences.delete(target);
      }
    }
  }

  function outputValue(source) {
    return source.mixLevel ?? source.baseVolume;
  }

  function fade(source, to, durationMs) {
    const duration = clamp(durationMs, 0, MAX_FADE_MS, 0);
    const start = outputValue(source);
    source.fadeToken += 1;
    const fadeToken = source.fadeToken;
    if (!duration) {
      setOutputValue(source, to);
      return Promise.resolve(true);
    }
    return new Promise((resolve) => {
      const started = performance.now();
      const tick = (now) => {
        if (!source.active || source.fadeToken !== fadeToken) {
          resolve(false);
          return;
        }
        const ratio = Math.min(1, (now - started) / duration);
        setOutputValue(source, start + ((to - start) * ratio));
        if (ratio >= 1) {
          resolve(true);
        } else {
          requestAnimationFrame(tick);
        }
      };
      requestAnimationFrame(tick);
    });
  }

  function cleanup(key) {
    const source = sources.get(key);
    if (!source) {
      return;
    }
    source.active = false;
    sources.delete(key);
    duckRequests.delete(key);
    if (handles.get(source.handle) === key) {
      motions.delete(source.handle);
      gainAutomations.delete(source.handle);
      handles.delete(source.handle);
    }
    if (source.target && targets.get(source.target) === key) {
      targets.delete(source.target);
    }
    if (source.sequenceFadeTimer) {
      clearTimeout(source.sequenceFadeTimer);
    }
    if (source.tailCleanupTimer) {
      clearTimeout(source.tailCleanupTimer);
    }
    for (const node of source.nodes || []) {
      try { node.disconnect(); } catch { /* already disconnected */ }
    }
    for (const track of source.sequenceTracks || []) {
      try { track.panner?.disconnect(); } catch { /* already disconnected */ }
      try { track.output?.disconnect(); } catch { /* already disconnected */ }
    }
    try { source.tailAnalyser?.disconnect(); } catch { /* already disconnected */ }
    try { source.node?.disconnect(); } catch { /* already disconnected */ }
    try { source.panner?.disconnect(); } catch { /* already disconnected */ }
    try { source.output?.disconnect(); } catch { /* already disconnected */ }
    refreshDucking();
  }

  function cleanupAfterRenderedTail(source) {
    if (!source.active) {
      return;
    }
    const analyser = source.tailAnalyser;
    if (!analyser) {
      cleanup(source.key);
      return;
    }
    const samples = new Float32Array(analyser.fftSize);
    const startedAt = performance.now();
    let silentPolls = 0;
    const poll = () => {
      source.tailCleanupTimer = null;
      if (!source.active) {
        return;
      }
      try {
        analyser.getFloatTimeDomainData(samples);
      } catch {
        cleanup(source.key);
        return;
      }
      silentPolls = samples.every((sample) => sample === 0)
        ? silentPolls + 1
        : 0;
      if (
        silentPolls >= WEB_AUDIO_TAIL_SILENCE_POLLS
        || performance.now() - startedAt >= WEB_AUDIO_TAIL_TIMEOUT_MS
      ) {
        cleanup(source.key);
        return;
      }
      source.tailCleanupTimer = setTimeout(poll, WEB_AUDIO_TAIL_POLL_MS);
    };
    source.tailCleanupTimer = setTimeout(poll, WEB_AUDIO_TAIL_POLL_MS);
  }

  async function stopKey(
    key,
    fadeMs = 0,
    { pause = false, outro = false, outroMode = "immediate" } = {},
  ) {
    const source = sources.get(key);
    if (!source) {
      return;
    }
    if (
      outro
      && source.seamless
      && source.stem
      && scheduleStemOutro(source, outroMode)
    ) {
      return;
    }
    if (pause) {
      source.paused = true;
    }
    const duration = clamp(fadeMs, 0, MAX_FADE_MS, 0);
    let completed = true;
    if (duration) {
      completed = await fade(source, 0, duration);
    } else {
      source.fadeToken += 1;
      setOutputValue(source, 0);
    }
    if (!completed || !source.active) {
      return;
    }
    if (pause && source.buffer && context) {
      const elapsed = Math.max(0, context.currentTime - source.startedAt)
        * source.playbackRate;
      source.bufferOffset = source.loop && source.buffer.duration > 0
        ? elapsed % source.buffer.duration
        : Math.min(elapsed, source.buffer.duration);
      source.nodeToken += 1;
      for (const node of source.nodes) {
        try { node.stop(); } catch { /* already stopped */ }
        try { node.disconnect(); } catch { /* already disconnected */ }
      }
      source.nodes.clear();
      source.node = null;
      return;
    }
    if (pause && source.audio) {
      source.audio.pause();
      return;
    }
    try {
      const nodes = source.nodes?.size ? source.nodes : [source.node];
      for (const node of nodes) {
        if (node?.stop) {
          try {
            node.stop();
          } catch {
            // A sibling segment may already have ended.
          }
        }
      }
      if (source.audio) {
        source.audio.pause();
        source.audio.currentTime = 0;
      }
    } catch {
      // The source may already have ended.
    }
    // A segmented stem owns its outro on the same decoded timeline. If stop
    // arrives before the loop phase, never fall back to loading and playing
    // that outro as an unrelated clip.
    const outroAsset = outro && !source.stem ? source.outro : "";
    const kind = source.kind;
    const bus = source.bus;
    cleanup(key);
    if (outroAsset) {
      const outroHandle = `outro:${sourceId()}`;
      const outroPacket = {
        kind,
        asset: outroAsset,
        handle: outroHandle,
        bus,
        volume: source.baseVolume * 100,
        pitch: source.playbackRate * 100,
        position: source.position,
        attenuation: source.attenuation,
        gain: source.sourceGain,
        pan: source.pan,
        loop: false,
      };
      const outroGeneration = nextGeneration(outroHandle);
      if (source.buffer && context) {
        const outroTarget = `outro:${outroHandle}`;
        const outroTargetGeneration = nextTargetGeneration(outroTarget);
        void playBufferedLayer(
          outroPacket,
          outroTarget,
          outroHandle,
          outroGeneration,
          outroTargetGeneration,
        ).then((played) => {
          if (
            !played
            && generations.get(outroHandle) === outroGeneration
            && targetGenerations.get(outroTarget) === outroTargetGeneration
          ) {
            playElement(
              outroPacket,
              outroTarget,
              outroGeneration,
            );
          }
        });
      } else {
        playElement(outroPacket, "", outroGeneration);
      }
    }
  }

  function scheduleStemOutro(source, mode = "immediate") {
    if (
      !context
      || !source.stem?.outroBuffer
      || source.stem.loopDuration <= 0
    ) {
      return false;
    }
    if (source.stem.outroScheduled) {
      if (
        mode === "boundary"
        || context.currentTime >= source.stem.outroStartsAt
      ) {
        source.outro = "";
        if (handles.get(source.handle) === source.key) {
          handles.delete(source.handle);
        }
        motions.delete(source.handle);
        gainAutomations.delete(source.handle);
        return true;
      }
      const scheduledNode = source.stem.outroNode;
      source.stem.outroNode = null;
      source.stem.outroScheduled = false;
      source.stem.outroStartsAt = 0;
      if (scheduledNode) {
        try { scheduledNode.stop(); } catch { /* already stopped */ }
        try { scheduledNode.disconnect(); } catch { /* already disconnected */ }
        source.nodes.delete(scheduledNode);
      }
    }
    const elapsed = Math.max(0, context.currentTime - source.stem.loopStartedAt);
    const cycles = Math.floor(elapsed / source.stem.loopDuration) + 1;
    const boundary = mode === "boundary"
      ? source.stem.loopStartedAt + (
        Math.max(1, cycles) * source.stem.loopDuration
      )
      : context.currentTime + 0.02;
    return scheduleStemOutroAt(source, boundary, true);
  }

  function scheduleStemOutroAt(source, boundary, detachHandle) {
    if (
      !context
      || !source.stem?.outroBuffer
      || source.stem.outroScheduled
      || !Number.isFinite(boundary)
      || boundary < context.currentTime
    ) {
      return false;
    }
    const outroNode = context.createBufferSource();
    outroNode.buffer = source.stem.outroBuffer;
    outroNode.playbackRate.value = source.stem.playbackRate;
    outroNode.connect(source.panner || source.output);
    source.nodes.add(outroNode);
    try {
      source.stem.loopNode.stop(boundary);
      outroNode.start(boundary);
    } catch {
      try { outroNode.disconnect(); } catch { /* not connected */ }
      source.nodes.delete(outroNode);
      return false;
    }
    source.stem.outroScheduled = true;
    source.stem.outroNode = outroNode;
    source.stem.outroRequestedAt = context.currentTime;
    source.stem.outroStartsAt = boundary;
    if (detachHandle) {
      source.outro = "";
      if (handles.get(source.handle) === source.key) {
        handles.delete(source.handle);
      }
      motions.delete(source.handle);
      gainAutomations.delete(source.handle);
    }
    outroNode.addEventListener("ended", () => {
      if (source.stem?.outroNode === outroNode) {
        cleanup(source.key);
      }
    }, { once: true });
    return true;
  }

  function register(source) {
    sources.set(source.key, source);
    handles.set(source.handle, source.key);
    if (source.target) {
      targets.set(source.target, source.key);
    }
    if (source.ducking?.size) {
      duckRequests.set(source.key, source.ducking);
      refreshDucking();
    }
    const motion = motions.get(source.handle);
    if (motion) {
      applyMotionFrame(motion);
    }
    const gainAutomation = gainAutomations.get(source.handle);
    if (gainAutomation) {
      applyGainFrame(gainAutomation);
    }
  }

  function retireTarget(target, fadeMs) {
    const key = targets.get(target);
    if (key) {
      targets.delete(target);
      stopKey(key, fadeMs);
    }
  }

  async function loadEffect(asset) {
    const url = assetUrl(asset, soundBaseUrl, soundVersion);
    if (!url || !context) {
      return null;
    }
    if (effectBuffers.has(url)) {
      const cached = effectBuffers.get(url);
      effectBuffers.delete(url);
      effectBuffers.set(url, cached);
      return cached;
    }
    if (!effectBuffers.has(url)) {
      let request;
      request = fetch(url)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Audio HTTP ${response.status}`);
          }
          return response.arrayBuffer();
        })
        .then(async (bytes) => {
          try {
            const decoded = await context.decodeAudioData(bytes.slice(0));
            if (decoded) {
              return decoded;
            }
          } catch {
            // WebKit before Safari 18.4 cannot decode the Ogg container.
          }
          return asset.toLowerCase().endsWith(".ogg")
            ? decodeVorbisFallback(context, bytes)
            : null;
        })
        .then((buffer) => {
          if (!buffer) {
            throw new Error("Unsupported audio asset");
          }
          if (effectBuffers.get(url) === request) {
            const size = buffer.length * buffer.numberOfChannels * 4;
            effectBufferSizes.set(url, size);
            effectBufferBytes += size;
            while (
              effectBuffers.size > MAX_CACHED_EFFECTS
              || effectBufferBytes > MAX_CACHED_BUFFER_BYTES
            ) {
              const oldest = effectBuffers.keys().next().value;
              if (oldest === undefined) {
                break;
              }
              effectBuffers.delete(oldest);
              effectBufferBytes -= effectBufferSizes.get(oldest) || 0;
              effectBufferSizes.delete(oldest);
            }
          }
          return buffer;
        })
        .catch(() => {
          if (effectBuffers.get(url) === request) {
            effectBuffers.delete(url);
            effectBufferBytes -= effectBufferSizes.get(url) || 0;
            effectBufferSizes.delete(url);
          }
          return null;
        });
      effectBuffers.set(url, request);
      while (effectBuffers.size > MAX_CACHED_EFFECTS) {
        const oldest = effectBuffers.keys().next().value;
        effectBuffers.delete(oldest);
        effectBufferBytes -= effectBufferSizes.get(oldest) || 0;
        effectBufferSizes.delete(oldest);
      }
    }
    return effectBuffers.get(url);
  }

  function enforceEffectLimits(asset, priority, maxInstances) {
    const effects = [...sources.values()].filter((source) => source.kind === "sfx");
    const matching = effects.filter((source) => source.asset === asset);
    const limit = clamp(maxInstances, 0, MAX_ACTIVE_EFFECTS, 0);
    const pool = limit && matching.length >= limit
      ? matching
      : effects.length >= MAX_ACTIVE_EFFECTS ? effects : [];
    if (!pool.length) {
      return true;
    }
    pool.sort((a, b) => a.priority - b.priority || a.createdAt - b.createdAt);
    if (pool[0].priority > priority) {
      return false;
    }
    stopKey(pool[0].key, 0);
    return true;
  }

  async function playBufferedEffect(packet, handle, generation) {
    if (!context) {
      return false;
    }
    if (context.state !== "running") {
      if (pendingEffects.length >= MAX_PENDING_EFFECTS) {
        pendingEffects.shift();
      }
      pendingEffects.push({ ...packet, handle, _generation: generation });
      return true;
    }
    const buffer = await loadEffect(packet.asset);
    if (!buffer || generations.get(handle) !== generation) {
      return false;
    }
    const priority = clamp(packet.priority, -100, 100, 0);
    if (!enforceEffectLimits(packet.asset, priority, packet.max_instances)) {
      return true;
    }

    const node = context.createBufferSource();
    const output = context.createGain();
    const baseVolume = clamp(packet.volume, 0, 100, 100) / 100;
    const playbackRate = clamp(packet.pitch, 25, 400, 100) / 100;
    output.gain.value = 0;
    node.buffer = buffer;
    node.loop = Boolean(packet.loop);
    node.playbackRate.value = playbackRate;
    const panner = createAudioSpatializer(context, {
      position: packet.position,
      pan: clamp(packet.pan, -100, 100, 0) / 100,
    });
    if (panner) {
      node.connect(panner);
      panner.connect(output);
    } else {
      node.connect(output);
    }
    const bus = busNode("sfx", packet.bus || "sfx");
    const tailAnalyser = panner?.panningModel === "HRTF"
      ? context.createAnalyser()
      : null;
    if (tailAnalyser) {
      tailAnalyser.fftSize = WEB_AUDIO_TAIL_FFT_SIZE;
      output.connect(tailAnalyser);
      tailAnalyser.connect(bus);
    } else {
      output.connect(bus);
    }
    const key = sourceId();
    const ducking = normalizeDucking(packet.ducking);
    const source = {
      key,
      handle,
      generation,
      kind: "sfx",
      bus: String(packet.bus || "sfx"),
      asset: packet.asset,
      priority,
      createdAt: performance.now(),
      baseVolume,
      attenuation: packet.attenuation,
      distanceGain: distanceAttenuationGain(packet.position, packet.attenuation),
      sourceGain: packet.gain ?? 1,
      playbackRate,
      node,
      output,
      panner,
      audio: null,
      target: "",
      outro: "",
      ducking,
      active: true,
      paused: false,
      mixLevel: packet.fade_in_ms ? 0 : baseVolume,
      fadeToken: 0,
      nodes: new Set([node]),
      seamless: false,
      stem: null,
      position: packet.position,
      pan: clamp(packet.pan, -100, 100, 0),
      tailAnalyser,
      tailCleanupTimer: null,
    };
    setOutputValue(source, packet.fade_in_ms ? 0 : baseVolume);
    register(source);
    node.addEventListener(
      "ended",
      () => cleanupAfterRenderedTail(source),
      { once: true },
    );
    node.start();
    if (packet.fade_in_ms) {
      fade(source, baseVolume, packet.fade_in_ms);
    }
    return true;
  }

  async function playBufferedSequence(packet, handle, generation) {
    if (!context) {
      return false;
    }
    if (context.state !== "running") {
      if (pendingEffects.length >= MAX_PENDING_EFFECTS) {
        pendingEffects.shift();
      }
      pendingEffects.push({ ...packet, handle, _generation: generation });
      return true;
    }
    const segments = packet.segments;
    const buffers = await Promise.all(segments.map((segment) => loadEffect(segment.asset)));
    if (
      buffers.some((buffer) => !buffer)
      || generations.get(handle) !== generation
    ) {
      return false;
    }
    const assetKey = `sequence:${segments.map(
      (segment) => `${segment.asset.length}:${segment.asset}`,
    ).join("")}`;
    const priority = clamp(packet.priority, -100, 100, 0);
    if (!enforceEffectLimits(assetKey, priority, packet.max_instances)) {
      return true;
    }

    const output = context.createGain();
    output.gain.value = 0;
    const bus = busNode("sfx", packet.bus || "sfx");
    const baseVolume = clamp(packet.volume, 0, 100, 100) / 100;
    const playbackRate = clamp(packet.pitch, 25, 400, 100) / 100;
    const key = sourceId();
    const startAt = context.currentTime + SEQUENCE_START_LEAD_SECONDS;
    let cursor = startAt;
    let completionAt = startAt;
    let completionTrack = null;
    const nodes = new Set();
    const sequenceTracks = [];

    for (let index = 0; index < segments.length; index += 1) {
      const segment = segments[index];
      const buffer = buffers[index];
      const node = context.createBufferSource();
      const segmentOutput = context.createGain();
      const panner = createAudioSpatializer(context, {
        position: segment.position,
        pan: segment.position
          ? panFromPosition(segment.position)
          : clamp(packet.pan, -100, 100, 0) / 100,
      });
      node.buffer = buffer;
      node.playbackRate.value = playbackRate;
      if (panner) {
        node.connect(panner);
        panner.connect(segmentOutput);
      } else {
        node.connect(segmentOutput);
      }
      segmentOutput.connect(output);
      const duration = buffer.duration / playbackRate;
      const distanceGain = distanceAttenuationGain(
        segment.position,
        segment.attenuation,
      );
      segmentOutput.gain.setValueAtTime(distanceGain * segment.gain, cursor);
      const track = {
        node,
        output: segmentOutput,
        panner,
        segment,
        startsAt: cursor,
        duration,
      };
      sequenceTracks.push(track);
      nodes.add(node);
      const segmentEnd = cursor + duration;
      if (segmentEnd >= completionAt) {
        completionAt = segmentEnd;
        completionTrack = track;
      }
      cursor += duration * segment.next_start_ratio;
    }

    const tailAnalyser = sequenceTracks.some(
      (track) => track.panner?.panningModel === "HRTF",
    ) ? context.createAnalyser() : null;
    if (tailAnalyser) {
      tailAnalyser.fftSize = WEB_AUDIO_TAIL_FFT_SIZE;
      output.connect(tailAnalyser);
      tailAnalyser.connect(bus);
    } else {
      output.connect(bus);
    }

    const source = {
      key,
      handle,
      generation,
      kind: "sfx",
      bus: String(packet.bus || "sfx"),
      asset: assetKey,
      priority,
      createdAt: performance.now(),
      baseVolume,
      attenuation: undefined,
      distanceGain: 1,
      sourceGain: 1,
      playbackRate,
      node: sequenceTracks[0].node,
      output,
      panner: null,
      audio: null,
      target: "",
      outro: "",
      ducking: normalizeDucking(packet.ducking),
      active: true,
      paused: false,
      mixLevel: packet.fade_in_ms ? 0 : baseVolume,
      fadeToken: 0,
      nodes,
      seamless: true,
      stem: null,
      position: segments[0].position,
      pan: clamp(packet.pan, -100, 100, 0),
      sequenceTracks,
      sequenceFadeTimer: null,
      tailAnalyser,
      tailCleanupTimer: null,
    };
    setOutputValue(source, packet.fade_in_ms ? 0 : baseVolume);
    register(source);
    try {
      for (const track of sequenceTracks) {
        track.node.start(track.startsAt);
      }
    } catch {
      for (const track of sequenceTracks) {
        try { track.node.stop(); } catch { /* not started or already stopped */ }
      }
      cleanup(key);
      return false;
    }
    completionTrack.node.addEventListener(
      "ended",
      () => cleanupAfterRenderedTail(source),
      { once: true },
    );

    const scheduleMotion = (track) => {
      if (!track.segment.destination_position || !track.segment.position) {
        return;
      }
      const update = () => {
        if (!source.active || generations.get(handle) !== generation) {
          return;
        }
        const elapsed = Math.min(
          track.duration,
          Math.max(0, context.currentTime - track.startsAt),
        );
        const ratio = audioMotionProgress(
          track.duration > 0 ? elapsed / track.duration : 1,
          track.segment.easing,
        );
        const position = track.segment.position.map((origin, coordinate) => (
          origin + (
            (track.segment.destination_position[coordinate] - origin) * ratio
          )
        ));
        if (track.panner) {
          setAudioSpatializerPosition(track.panner, context, position);
        }
        track.output.gain.setValueAtTime(
          distanceAttenuationGain(position, track.segment.attenuation)
            * track.segment.gain,
          context.currentTime,
        );
        if (elapsed < track.duration) {
          requestAnimationFrame(update);
        }
      };
      requestAnimationFrame(update);
    };
    sequenceTracks.forEach(scheduleMotion);
    if (packet.fade_in_ms) {
      source.sequenceFadeTimer = setTimeout(() => {
        source.sequenceFadeTimer = null;
        if (source.active && generations.get(handle) === generation) {
          fade(source, baseVolume, packet.fade_in_ms);
        }
      }, Math.max(0, (startAt - context.currentTime) * 1000));
    }
    return true;
  }

  function createElement(asset) {
    const url = assetUrl(asset, soundBaseUrl, soundVersion);
    if (!url) {
      return null;
    }
    const audio = new Audio();
    audio.preload = "auto";
    audio.src = url;
    return { audio, url };
  }

  function connectElement(audio, kind, bus, packet) {
    if (!context) {
      return { node: null, output: null, panner: null };
    }
    try {
      const node = context.createMediaElementSource(audio);
      const output = context.createGain();
      const panner = createAudioSpatializer(context, {
        position: packet.position,
        pan: clamp(packet.pan, -100, 100, 0) / 100,
      });
      if (panner) {
        node.connect(panner);
        panner.connect(output);
      } else {
        node.connect(output);
      }
      output.connect(busNode(kind, bus));
      return { node, output, panner: panner || null };
    } catch {
      return { node: null, output: null, panner: null };
    }
  }

  function safePlay(source, pending) {
    try {
      const result = source.audio.play();
      if (result?.catch) {
        result.catch(() => {
          if (source.active) {
            pending(source);
          }
        });
      }
    } catch {
      if (source.active) {
        pending(source);
      }
    }
  }

  function playElement(
    packet,
    target = "",
    generation = null,
    onEnded = null,
    onPlaybackFailure = null,
  ) {
    const created = createElement(packet.asset);
    if (!created) {
      return null;
    }
    const handle = String(packet.handle || `${packet.kind}:${sourceId()}`);
    const expectedGeneration = generation ?? nextGeneration(handle);
    if (generations.get(handle) !== expectedGeneration) {
      return null;
    }
    const { audio } = created;
    const kind = packet.kind;
    const bus = String(packet.bus || kind);
    const connected = connectElement(audio, kind, bus, packet);
    const baseVolume = clamp(packet.volume, 0, 100, 100) / 100;
    audio.loop = Boolean(packet.loop);
    audio.muted = muted;
    const playbackRate = clamp(packet.pitch, 25, 400, 100) / 100;
    audio.playbackRate = playbackRate;
    audio.preservesPitch = false;
    const key = sourceId();
    const source = {
      key,
      handle,
      generation: expectedGeneration,
      kind,
      bus,
      asset: packet.asset,
      priority: clamp(packet.priority, -100, 100, 0),
      createdAt: performance.now(),
      baseVolume,
      attenuation: packet.attenuation,
      distanceGain: distanceAttenuationGain(packet.position, packet.attenuation),
      sourceGain: packet.gain ?? 1,
      playbackRate,
      node: connected.node,
      output: connected.output,
      panner: connected.panner,
      audio,
      target,
      outro: validAsset(packet.outro),
      ducking: normalizeDucking(packet.ducking),
      active: true,
      paused: false,
      mixLevel: packet.fade_in_ms ? 0 : baseVolume,
      fadeToken: 0,
      nodes: new Set(),
      seamless: false,
      stem: null,
      buffer: null,
      bufferOffset: 0,
      startedAt: 0,
      nodeToken: 0,
      position: packet.position,
      pan: clamp(packet.pan, -100, 100, 0),
    };
    setOutputValue(source, packet.fade_in_ms ? 0 : baseVolume);
    register(source);
    audio.addEventListener("ended", () => {
      cleanup(key);
      onEnded?.();
    }, { once: true });
    let playbackFailureHandled = false;
    const handlePlaybackFailure = () => {
      if (playbackFailureHandled || !source.active) {
        return;
      }
      playbackFailureHandled = true;
      if (onPlaybackFailure) {
        onPlaybackFailure(source);
        return;
      }
      if (kind === "music") {
        pendingMusic.set(target || targetOf(packet), { ...packet, handle });
      } else if (kind === "ambience") {
        pendingAmbiences.set(target, { ...packet, handle });
      } else if (pendingEffects.length < MAX_PENDING_EFFECTS) {
        pendingEffects.push({
          ...packet,
          handle,
          _generation: expectedGeneration,
        });
      }
      try { audio.pause(); } catch { /* playback never started */ }
      cleanup(key);
    };
    audio.addEventListener("error", handlePlaybackFailure, { once: true });
    safePlay(source, handlePlaybackFailure);
    if (packet.fade_in_ms) {
      fade(source, baseVolume, packet.fade_in_ms);
    }
    return source;
  }

  function startBufferedLayerNode(source, offset = 0) {
    if (!context || !source.buffer || !source.active) {
      return false;
    }
    const node = context.createBufferSource();
    node.buffer = source.buffer;
    node.loop = source.loop;
    node.playbackRate.value = source.playbackRate;
    node.connect(source.panner || source.output);
    const boundedOffset = source.buffer.duration > 0
      ? Math.min(Math.max(0, offset), source.buffer.duration)
      : 0;
    source.nodeToken += 1;
    const nodeToken = source.nodeToken;
    source.node = node;
    source.nodes.add(node);
    source.startedAt = context.currentTime - (boundedOffset / source.playbackRate);
    node.addEventListener("ended", () => {
      source.nodes.delete(node);
      if (
        source.active
        && !source.paused
        && !source.loop
        && source.nodeToken === nodeToken
      ) {
        cleanup(source.key);
        source.onEnded?.();
      }
    }, { once: true });
    try {
      node.start(0, boundedOffset);
      return true;
    } catch {
      source.nodes.delete(node);
      try { node.disconnect(); } catch { /* not connected */ }
      return false;
    }
  }

  async function playBufferedLayer(
    packet,
    target,
    handle,
    generation,
    targetGeneration,
    onEnded = null,
  ) {
    const kind = packet.kind;
    if (!context || !["music", "ambience"].includes(kind)) {
      return false;
    }
    if (context.state !== "running") {
      (kind === "music" ? pendingMusic : pendingAmbiences)
        .set(target, { ...packet, handle });
      return true;
    }
    const buffer = await loadEffect(packet.asset);
    if (
      !buffer
      || generations.get(handle) !== generation
      || targetGenerations.get(target) !== targetGeneration
    ) {
      return false;
    }
    if (kind === "music" && pausedMusicHandles.has(handle)) {
      pendingMusic.set(target, { ...packet, handle });
      return true;
    }
    const output = context.createGain();
    const panner = createAudioSpatializer(context, {
      position: packet.position,
      pan: clamp(packet.pan, -100, 100, 0) / 100,
    });
    panner?.connect(output);
    const bus = String(packet.bus || kind);
    const baseVolume = clamp(packet.volume, 0, 100, 100) / 100;
    const playbackRate = clamp(packet.pitch, 25, 400, 100) / 100;
    output.gain.value = 0;
    output.connect(busNode(kind, bus));
    const key = sourceId();
    const source = {
      key,
      handle,
      generation,
      kind,
      bus,
      asset: packet.asset,
      priority: clamp(packet.priority, -100, 100, 0),
      createdAt: performance.now(),
      baseVolume,
      attenuation: packet.attenuation,
      distanceGain: distanceAttenuationGain(packet.position, packet.attenuation),
      sourceGain: packet.gain ?? 1,
      playbackRate,
      node: null,
      output,
      panner: panner || null,
      audio: null,
      target,
      outro: validAsset(packet.outro),
      ducking: normalizeDucking(packet.ducking),
      active: true,
      paused: false,
      mixLevel: packet.fade_in_ms ? 0 : baseVolume,
      fadeToken: 0,
      nodes: new Set(),
      seamless: false,
      stem: null,
      buffer,
      bufferOffset: 0,
      startedAt: 0,
      nodeToken: 0,
      loop: packet.loop !== false,
      onEnded,
      position: packet.position,
      pan: clamp(packet.pan, -100, 100, 0),
    };
    setOutputValue(source, packet.fade_in_ms ? 0 : baseVolume);
    register(source);
    if (!startBufferedLayerNode(source)) {
      cleanup(key);
      return false;
    }
    if (packet.fade_in_ms) {
      fade(source, baseVolume, packet.fade_in_ms);
    }
    return true;
  }

  async function playBufferedStem(
    packet,
    target,
    handle,
    generation,
    targetGeneration,
  ) {
    if (!context) {
      return false;
    }
    if (context.state !== "running") {
      pendingAmbiences.set(target, { ...packet, handle });
      return true;
    }
    const introAsset = packet.play_intro === false ? "" : validAsset(packet.intro);
    const loopAsset = validAsset(packet.asset);
    const outroAsset = validAsset(packet.outro);
    const [introBuffer, loopBuffer, outroBuffer] = await Promise.all([
      introAsset ? loadEffect(introAsset) : Promise.resolve(null),
      loadEffect(loopAsset),
      outroAsset ? loadEffect(outroAsset) : Promise.resolve(null),
    ]);
    if (
      !loopBuffer
      || generations.get(handle) !== generation
      || targetGenerations.get(target) !== targetGeneration
    ) {
      return false;
    }

    const output = context.createGain();
    const panner = createAudioSpatializer(context, {
      position: packet.position,
      pan: clamp(packet.pan, -100, 100, 0) / 100,
    });
    panner?.connect(output);
    const bus = String(packet.bus || "ambience");
    const baseVolume = clamp(packet.volume, 0, 100, 100) / 100;
    output.gain.value = 0;
    output.connect(busNode("ambience", bus));
    const introNode = introBuffer ? context.createBufferSource() : null;
    const loopNode = context.createBufferSource();
    const playbackRate = clamp(packet.pitch, 25, 400, 100) / 100;
    const startAt = context.currentTime + 0.03;
    const loopStartedAt = startAt + ((introBuffer?.duration || 0) / playbackRate);
    if (introNode) {
      introNode.buffer = introBuffer;
      introNode.playbackRate.value = playbackRate;
      introNode.connect(panner || output);
    }
    loopNode.buffer = loopBuffer;
    loopNode.loop = packet.loop !== false;
    loopNode.playbackRate.value = playbackRate;
    loopNode.connect(panner || output);
    const key = sourceId();
    const nodes = new Set([loopNode]);
    if (introNode) {
      nodes.add(introNode);
    }
    const source = {
      key,
      handle,
      generation,
      kind: "ambience",
      bus,
      asset: loopAsset,
      priority: clamp(packet.priority, -100, 100, 0),
      createdAt: performance.now(),
      baseVolume,
      attenuation: packet.attenuation,
      distanceGain: distanceAttenuationGain(packet.position, packet.attenuation),
      sourceGain: packet.gain ?? 1,
      playbackRate,
      node: loopNode,
      nodes,
      output,
      panner: panner || null,
      audio: null,
      target,
      outro: outroAsset,
      ducking: normalizeDucking(packet.ducking),
      active: true,
      paused: false,
      mixLevel: packet.fade_in_ms ? 0 : baseVolume,
      fadeToken: 0,
      seamless: true,
      stem: {
        introNode,
        loopNode,
        loopStartedAt,
        loopDuration: loopBuffer.duration / playbackRate,
        playbackRate,
        outroBuffer,
        outroNode: null,
        outroScheduled: false,
        outroRequestedAt: 0,
        outroStartsAt: 0,
      },
      buffer: null,
      bufferOffset: 0,
      startedAt: 0,
      nodeToken: 0,
      position: packet.position,
      pan: clamp(packet.pan, -100, 100, 0),
    };
    setOutputValue(source, packet.fade_in_ms ? 0 : baseVolume);
    register(source);
    if (introNode) {
      introNode.start(startAt);
    }
    loopNode.start(loopStartedAt);
    if (!loopNode.loop) {
      const naturalOutroAt = loopStartedAt + source.stem.loopDuration;
      if (!scheduleStemOutroAt(source, naturalOutroAt, false)) {
        loopNode.addEventListener("ended", () => cleanup(key), { once: true });
      }
    }
    if (packet.fade_in_ms) {
      fade(source, baseVolume, packet.fade_in_ms);
    }
    return true;
  }

  async function playSound(packet) {
    if (packet.segments?.length) {
      const handle = String(packet.handle || "");
      if (!handle) {
        return "";
      }
      cancelPendingHandle(handle);
      const generation = packet._generation ?? nextGeneration(handle);
      if (packet._generation !== undefined && generations.get(handle) !== generation) {
        return "";
      }
      const oldKey = handles.get(handle);
      if (oldKey) {
        await stopKey(oldKey, packet.fade_out_ms || 0);
      }
      return await playBufferedSequence(packet, handle, generation) ? handle : "";
    }
    const resolvedPacket = resolveSoundPacket(packet);
    const spatial = normalizeSpatialFields(packet);
    if (!resolvedPacket || !spatial) {
      return "";
    }
    const normalized = {
      ...resolvedPacket,
      kind: "sfx",
      asset: resolvedPacket.asset,
      bus: packet.bus || "sfx",
      volume: packet.volume ?? 100,
      pan: packet.pan ?? 0,
      pitch: packet.pitch ?? 100,
      position: spatial.position,
      attenuation: spatial.attenuation,
    };
    const handle = String(packet.handle || `sfx:${sourceId()}`);
    cancelPendingHandle(handle);
    const generation = packet._generation ?? nextGeneration(handle);
    if (packet._generation !== undefined && generations.get(handle) !== generation) {
      return "";
    }
    const oldKey = handles.get(handle);
    if (oldKey) {
      await stopKey(oldKey, packet.fade_out_ms || 0);
    }
    if (!await playBufferedEffect(normalized, handle, generation)) {
      playElement({ ...normalized, handle }, "", generation);
    }
    return handle;
  }

  function queueFiniteSound(packet) {
    const handle = String(packet.handle || `sfx:${sourceId()}`);
    cancelPendingHandle(handle);
    const generation = nextGeneration(handle);
    const queuedPacket = { ...packet, handle, _generation: generation };
    const assets = queuedPacket.segments?.length
      ? queuedPacket.segments.map((segment) => segment.asset)
      : [queuedPacket.asset];
    // Begin decoding immediately, but serialize the moment each finite source
    // is started. Cached reports must not overtake an uncached projectile chain.
    const preload = context
      ? Promise.all(assets.map((asset) => loadEffect(asset)))
      : Promise.resolve();
    const launch = finiteSfxLaunchQueue
      .catch(() => undefined)
      .then(async () => {
        await preload;
        if (generations.get(handle) !== generation) {
          return;
        }
        await playSound(queuedPacket);
      });
    finiteSfxLaunchQueue = launch.catch(() => undefined);
  }

  function playLayer(packet) {
    const kind = packet.kind;
    const asset = validAsset(packet.asset);
    const spatial = normalizeSpatialFields(packet);
    if (!asset || !["music", "ambience"].includes(kind) || !spatial) {
      return "";
    }
    const target = targetOf(packet);
    const layers = [...sources.values()].filter((source) => source.kind !== "sfx");
    if (!targets.has(target) && layers.length >= MAX_ACTIVE_LAYERS) {
      layers.sort((left, right) => (
        left.priority - right.priority || left.createdAt - right.createdAt
      ));
      const incomingPriority = clamp(packet.priority, -100, 100, 0);
      if (layers[0].priority > incomingPriority) {
        return "";
      }
      stopKey(layers[0].key, 0);
    }
    const handle = String(packet.handle || `${kind}:${target}`);
    if (kind === "music") {
      pausedMusicHandles.delete(handle);
    }
    const generation = nextGeneration(handle);
    const targetGeneration = nextTargetGeneration(target);
    if (kind === "music") {
      pendingMusic.delete(target);
    }
    retireTarget(target, packet.fade_out_ms || 0);
    const normalized = {
      ...packet,
      asset,
      handle,
      loop: packet.loop ?? true,
      bus: packet.bus || kind,
      volume: packet.volume ?? 100,
      position: spatial.position,
      attenuation: spatial.attenuation,
    };
    const intro = kind === "ambience" && packet.play_intro !== false
      ? validAsset(packet.intro)
      : "";
    const outro = kind === "ambience" ? validAsset(packet.outro) : "";
    if (kind === "ambience" && packet.seamless !== false && (intro || outro)) {
      void playBufferedStem(
        normalized,
        target,
        handle,
        generation,
        targetGeneration,
      ).then((played) => {
        if (
          !played
          && generations.get(handle) === generation
          && targetGenerations.get(target) === targetGeneration
        ) {
          playElement(normalized, target, generation);
        }
      });
      return handle;
    }
    const playElementWithBufferedFallback = (layerPacket, onEnded = null) => {
      const fallbackToBufferedLayer = (failedSource) => {
        if (
          generations.get(handle) !== generation
          || targetGenerations.get(target) !== targetGeneration
        ) {
          return;
        }
        if (
          kind === "music"
          && (pausedMusicHandles.has(handle) || failedSource.paused)
        ) {
          void stopKey(failedSource.key, 0).then(() => {
            if (
              pausedMusicHandles.has(handle)
              && generations.get(handle) === generation
              && targetGenerations.get(target) === targetGeneration
            ) {
              pendingMusic.set(target, normalized);
            }
          });
          return;
        }
        void stopKey(failedSource.key, 0).then(() => (
          playBufferedLayer(
            layerPacket,
            target,
            handle,
            generation,
            targetGeneration,
            onEnded,
          )
        )).then((played) => {
          if (
            !played
            && generations.get(handle) === generation
            && targetGenerations.get(target) === targetGeneration
          ) {
            (kind === "music" ? pendingMusic : pendingAmbiences)
              .set(target, normalized);
          }
        });
      };
      return playElement(
        layerPacket,
        target,
        generation,
        onEnded,
        fallbackToBufferedLayer,
      );
    };
    if (!intro) {
      playElementWithBufferedFallback(normalized);
      return handle;
    }
    playElementWithBufferedFallback(
      { ...normalized, asset: intro, loop: false, outro: "" },
      () => {
        if (
          generations.get(handle) === generation
          && targetGenerations.get(target) === targetGeneration
        ) {
          playElementWithBufferedFallback(normalized);
        }
      },
    );
    return handle;
  }

  function playMusic(packet) {
    return playLayer({
      ...packet,
      kind: "music",
      asset: packet.asset,
      handle: packet.handle || "music",
      layer: packet.layer || "main",
      fade_in_ms: packet.fade_in_ms ?? 800,
      fade_out_ms: packet.fade_out_ms ?? 800,
      loop: packet.loop ?? true,
    });
  }

  function playAmbience(packet) {
    return playLayer({
      ...packet,
      kind: "ambience",
      asset: packet.asset,
      layer: packet.layer || "environment",
      fade_in_ms: packet.fade_in_ms ?? 1200,
      fade_out_ms: packet.fade_out_ms ?? 1200,
      loop: packet.loop ?? true,
    });
  }

  function stopHandle(
    handle,
    fadeMs = 0,
    pause = false,
    outro = false,
    outroMode = "immediate",
  ) {
    pausedMusicHandles.delete(String(handle));
    cancelPendingHandle(handle);
    const key = handles.get(String(handle));
    if (!key) {
      nextGeneration(String(handle));
      return;
    }
    nextGeneration(String(handle));
    stopKey(key, fadeMs, { pause, outro, outroMode });
  }

  function stopMusic(fadeMs = 800, handle = "music") {
    stopHandle(handle, fadeMs);
  }

  function pauseMusic(fadeMs = 800, handle = "music") {
    pausedMusicHandles.add(String(handle));
    const key = handles.get(handle);
    if (key) {
      stopKey(key, fadeMs, { pause: true });
    }
  }

  function resumeMusic(fadeMs = 800, handle = "music") {
    const key = handles.get(handle);
    const source = key ? sources.get(key) : null;
    pausedMusicHandles.delete(String(handle));
    if (!source) {
      for (const [target, packet] of pendingMusic) {
        if (packet.handle !== handle) {
          continue;
        }
        pendingMusic.delete(target);
        playMusic({ ...packet, fade_in_ms: fadeMs });
        return;
      }
    }
    if (!source?.paused || !source.audio) {
      if (!source?.paused || !source.buffer) {
        return;
      }
      source.paused = false;
      if (!startBufferedLayerNode(source, source.bufferOffset)) {
        cleanup(source.key);
        return;
      }
      fade(source, source.baseVolume, fadeMs);
      return;
    }
    source.paused = false;
    safePlay(source, () => {
      pendingMusic.set(source.target || targetOf({
        kind: "music",
        layer: "main",
      }), {
        kind: "music",
        asset: source.asset,
        handle,
        bus: source.bus,
        loop: source.audio.loop,
      });
    });
    fade(source, source.baseVolume, fadeMs);
  }

  function stopAmbience(packet = {}) {
    const outroMode = packet.outro_mode || "immediate";
    if (packet.all_layers) {
      for (const target of [...targetGenerations.keys()]) {
        if (target.startsWith("ambience:")) {
          nextTargetGeneration(target);
        }
      }
      pendingAmbiences.clear();
      for (const source of [...sources.values()]) {
        if (source.kind !== "ambience") {
          continue;
        }
        nextGeneration(source.handle);
        stopKey(source.key, packet.fade_out_ms ?? 1200, {
          outro: packet.play_outro !== false,
          outroMode,
        });
      }
      return;
    }
    const handle = packet.handle || "";
    const target = targetOf({
      kind: "ambience",
      scope: packet.scope || "global",
      context: packet.context || "",
      layer: packet.layer || "environment",
    });
    if (!handle) {
      nextTargetGeneration(target);
    }
    const key = handle
      ? handles.get(handle)
      : targets.get(target);
    if (key) {
      const source = sources.get(key);
      if (source) {
        nextGeneration(source.handle);
      }
      stopKey(key, packet.fade_out_ms ?? 1200, {
        outro: packet.play_outro !== false,
        outroMode,
      });
    }
    pendingAmbiences.delete(target);
  }

  function setBus(bus, gain, fadeMs = 0) {
    const name = String(bus || "");
    if (!name) {
      return;
    }
    const targetGain = clamp(gain, 0, 100, 100) / 100;
    busGains.set(name, targetGain);
    if (!context || !fadeMs) {
      refreshBus(name);
      return;
    }
    for (const record of busNodes.values()) {
      if (record.bus === name) {
        record.node.gain.cancelScheduledValues(context.currentTime);
        record.node.gain.setValueAtTime(
          record.node.gain.value,
          context.currentTime,
        );
        record.node.gain.linearRampToValueAtTime(
          targetGain * duckGain(name),
          context.currentTime + (clamp(fadeMs, 0, MAX_FADE_MS, 0) / 1000),
        );
      }
    }
  }

  function handleAudioCommand(packet) {
    if (!packet || typeof packet !== "object" || Array.isArray(packet)) {
      return false;
    }
    if (packet.version !== AUDIO_PROTOCOL_VERSION) {
      return false;
    }
    const spatial = normalizeSpatialFields(packet);
    const motion = normalizeAudioMotion(packet.motion);
    const gain = packet.gain === undefined ? 1 : normalizeAudioGain(packet.gain);
    const gainAutomation = normalizeAudioGainAutomation(packet.gain_automation);
    const sequenceSegments = normalizeSequenceSegments(packet.segments);
    if (
      !spatial
      || motion === null
      || gain === null
      || gainAutomation === null
      || sequenceSegments === null
      || (spatial.position !== undefined && packet.command !== "play")
      || (spatial.attenuation !== undefined && packet.command !== "play")
      || (motion !== undefined && packet.command !== "update")
      || (Object.hasOwn(packet, "gain") && packet.command !== "play")
      || (gainAutomation !== undefined && packet.command !== "update")
      || sequenceSegments.length && (
        packet.command !== "play"
        || packet.kind !== "sfx"
        || packet.loop
        || spatial.position !== undefined
        || spatial.attenuation !== undefined
        || gain !== 1
        || packet.intro
        || packet.outro
        || !packet.handle
      )
    ) {
      return false;
    }
    packet = {
      ...packet,
      position: spatial.position,
      attenuation: spatial.attenuation,
      motion,
      gain,
      gain_automation: gainAutomation,
      segments: sequenceSegments,
    };
    for (const field of ["handle", "bus", "context", "layer"]) {
      if (packet[field] && !validId(packet[field])) {
        return false;
      }
    }
    if (!["global", "player", "context"].includes(packet.scope || "global")) {
      return false;
    }
    const outroMode = packet.outro_mode || "immediate";
    if (!["immediate", "boundary"].includes(outroMode)) {
      return false;
    }
    if (
      packet.all_layers
      && (
        packet.command !== "stop"
        || packet.kind !== "ambience"
        || packet.handle
      )
    ) {
      return false;
    }
    if (packet.play_outros && packet.command !== "stop_all") {
      return false;
    }
    const ducking = packet.ducking || {};
    if (
      typeof ducking !== "object"
      || Array.isArray(ducking)
      || Object.keys(ducking).length > 32
    ) {
      return false;
    }
    if (Object.keys(ducking).some((bus) => !validId(bus))) {
      return false;
    }
    if (packet.family && packet.command !== "play") {
      return false;
    }
    if (
      packet.buffer
      && (
        typeof packet.buffer !== "string"
        || !AUDIO_OUTPUT_BUFFERS.has(packet.buffer)
        || packet.command !== "play"
        || packet.kind !== "sfx"
        || Boolean(packet.loop)
      )
    ) {
      return false;
    }
    switch (packet.command) {
      case "update":
        if (
          !["sfx", "music", "ambience"].includes(packet.kind)
          || !packet.handle
          || (!motion && !gainAutomation)
        ) {
          return false;
        }
        return (
          (!motion || startSourceMotion(packet.kind, packet.handle, motion))
          && (!gainAutomation || startSourceGainAutomation(
            packet.kind,
            packet.handle,
            gainAutomation,
          ))
        );
      case "play":
        if (!["sfx", "music", "ambience"].includes(packet.kind)) {
          return false;
        }
        if (packet.kind === "sfx") {
          if (sequenceSegments.length) {
            if (packet.asset || packet.family) {
              return false;
            }
            queueFiniteSound(packet);
            return true;
          }
          const resolvedPacket = resolveSoundPacket(packet);
          if (!resolvedPacket) {
            return false;
          }
          queueFiniteSound(resolvedPacket);
        } else {
          if (packet.family || !validAsset(packet.asset)) {
            return false;
          }
          playLayer(packet);
        }
        return true;
      case "stop": {
        if (
          !["sfx", "music", "ambience"].includes(packet.kind)
          || (["sfx", "music"].includes(packet.kind) && !packet.handle)
        ) {
          return false;
        }
        if (packet.kind === "ambience" && !packet.handle) {
          stopAmbience(packet);
        } else {
          stopHandle(
            packet.handle,
            packet.fade_out_ms || 0,
            false,
            packet.kind === "ambience" && packet.play_outro !== false,
            outroMode,
          );
        }
        return true;
      }
      case "pause":
        if (packet.kind !== "music" || !packet.handle) {
          return false;
        }
        pauseMusic(packet.fade_out_ms || 0, packet.handle);
        return true;
      case "resume":
        if (packet.kind !== "music" || !packet.handle) {
          return false;
        }
        resumeMusic(packet.fade_in_ms || 0, packet.handle);
        return true;
      case "set_bus":
        if (!packet.bus) {
          return false;
        }
        setBus(packet.bus, packet.volume, packet.fade_in_ms || 0);
        return true;
      case "stop_all":
        stopAll(packet.fade_out_ms || 0, {
          playOutros: packet.play_outros === true,
          outroMode,
        });
        return true;
      default:
        return false;
    }
  }

  function waitForContextTransition(transition) {
    return new Promise((resolve) => {
      let settled = false;
      const finish = (result) => {
        if (settled) {
          return;
        }
        settled = true;
        clearTimeout(timer);
        resolve(result);
      };
      const timer = setTimeout(
        () => finish(false),
        AUDIO_CONTEXT_TRANSITION_TIMEOUT_MS,
      );
      Promise.resolve(transition).then(() => finish(true), () => finish(false));
    });
  }

  function recoverContext({ restartRunning = false } = {}) {
    configureBrowserAudioSession(audioSession, microphoneActive);
    if (!context) {
      retryPendingPlayback();
      return Promise.resolve(true);
    }
    if (context.state === "closed") {
      return Promise.resolve(false);
    }
    if (contextRecovery) {
      return contextRecovery;
    }
    const recovery = (async () => {
      if (
        restartRunning
        && context.state === "running"
        && typeof context.suspend === "function"
      ) {
        let transition;
        try {
          transition = context.suspend();
        } catch {
          transition = null;
        }
        if (transition) {
          await waitForContextTransition(transition);
        }
      }
      if (context.state !== "running" && typeof context.resume === "function") {
        let transition;
        try {
          transition = context.resume();
        } catch {
          transition = null;
        }
        if (transition) {
          await waitForContextTransition(transition);
        }
      }
      if (context.state === "running") {
        contextHasRun = true;
        retryPendingPlayback();
        return true;
      }
      return false;
    })();
    contextRecovery = recovery;
    return recovery.finally(() => {
      if (contextRecovery === recovery) {
        contextRecovery = null;
      }
    });
  }

  function unlock() {
    return recoverContext();
  }

  function recoverAfterForeground() {
    if (!context || !contextHasRun) {
      configureBrowserAudioSession(audioSession, microphoneActive);
      return Promise.resolve(!context);
    }
    if (foregroundRecovery) {
      return foregroundRecovery;
    }
    const recovery = (async () => {
      if (!await recoverContext()) {
        return false;
      }
      const observedTime = context.currentTime;
      await new Promise((resolve) => setTimeout(resolve, AUDIO_CONTEXT_HEALTH_CHECK_MS));
      if (
        typeof document !== "undefined"
        && document.visibilityState === "hidden"
      ) {
        return false;
      }
      if (context.state !== "running") {
        return recoverContext();
      }
      if (context.currentTime <= observedTime) {
        return recoverContext({ restartRunning: true });
      }
      retryPendingPlayback();
      return true;
    })();
    foregroundRecovery = recovery;
    return recovery.finally(() => {
      if (foregroundRecovery === recovery) {
        foregroundRecovery = null;
      }
    });
  }

  function setMicrophoneActive(active) {
    microphoneActive = Boolean(active);
    const configured = configureBrowserAudioSession(audioSession, microphoneActive);
    if (!microphoneActive && context && context.state !== "running") {
      void recoverContext();
    }
    return configured;
  }

  function retryPendingPlayback() {
    if (context && context.state !== "running") {
      return false;
    }
    const queuedMusic = [...pendingMusic.entries()];
    pendingMusic.clear();
    for (const [target, packet] of queuedMusic) {
      if (pausedMusicHandles.has(String(packet.handle || "music"))) {
        pendingMusic.set(target, packet);
        continue;
      }
      playMusic(packet);
    }
    for (const packet of pendingAmbiences.values()) {
      playAmbience(packet);
    }
    pendingAmbiences.clear();
    for (const packet of pendingEffects.splice(0)) {
      const handle = packet.handle;
      const generation = packet._generation;
      if (generations.get(handle) !== generation) {
        continue;
      }
      const oldKey = handles.get(handle);
      const ready = oldKey ? stopKey(oldKey, 0) : Promise.resolve();
      ready
        .then(() => (
          packet.segments?.length
            ? playBufferedSequence(packet, handle, generation)
            : playBufferedEffect(packet, handle, generation)
        ))
        .then((played) => {
          if (
            !played
            && !packet.segments?.length
            && generations.get(handle) === generation
          ) {
            playElement(packet, "", generation);
          }
        });
    }
    return true;
  }

  function preloadEffects(names = []) {
    for (const name of names) {
      const asset = validAsset(name);
      if (asset) {
        loadEffect(asset);
      }
    }
  }

  function preloadEffectFamily(family) {
    preloadEffects(soundFamilyVariants(family));
  }

  function setMaster(kind, percent) {
    const bounded = clamp(percent, 0, 100, 100);
    masterValues[kind] = bounded / 100;
    if (masters[kind] && context) {
      masters[kind].gain.setValueAtTime(
        muted ? 0 : masterValues[kind],
        context.currentTime,
      );
    }
    for (const source of sources.values()) {
      if (source.kind === kind && !source.output) {
        setOutputValue(source, source.mixLevel ?? source.baseVolume);
      }
    }
    return bounded;
  }

  function setMusicVolumePercent(percent) {
    return setMaster("music", percent);
  }

  function setAmbienceVolumePercent(percent) {
    return setMaster("ambience", percent);
  }

  function setEffectsVolumePercent(percent) {
    return setMaster("sfx", percent);
  }

  function setMuted(nextMuted) {
    muted = Boolean(nextMuted);
    for (const kind of ["sfx", "music", "ambience"]) {
      if (masters[kind] && context) {
        masters[kind].gain.setValueAtTime(
          muted ? 0 : masterValues[kind],
          context.currentTime,
        );
      }
    }
    for (const source of sources.values()) {
      if (source.audio) {
        source.audio.muted = muted;
      }
    }
  }

  function stopAll(
    fadeMs = 0,
    { playOutros = false, outroMode = "immediate" } = {},
  ) {
    pendingMusic.clear();
    pendingAmbiences.clear();
    pendingEffects.length = 0;
    pausedMusicHandles.clear();
    for (const handle of [...generations.keys()]) {
      nextGeneration(handle);
    }
    for (const target of [...targetGenerations.keys()]) {
      nextTargetGeneration(target);
    }
    for (const source of [...sources.values()]) {
      stopKey(source.key, fadeMs, {
        outro: playOutros && source.kind === "ambience",
        outroMode,
      });
    }
  }

  function setSoundVersion(version) {
    const next = String(version || "");
    if (next !== soundVersion) {
      soundVersion = next;
      effectBuffers.clear();
      effectBufferSizes.clear();
      effectBufferBytes = 0;
    }
  }

  function getDiagnostics() {
    return Object.freeze({
      sourceCount: sources.size,
      handleCount: handles.size,
      activeHandles: Object.freeze([...handles.keys()]),
      targetCount: targets.size,
      pausedCount: [...sources.values()].filter((source) => source.paused).length,
      duckRequestCount: duckRequests.size,
      pendingCount: pendingEffects.length
        + pendingMusic.size
        + pendingAmbiences.size,
      bufferedMusicCount: [...sources.values()].filter(
        (source) => source.kind === "music" && source.buffer,
      ).length,
      buses: Object.freeze(Object.fromEntries(busGains)),
      stemCount: [...sources.values()].filter((source) => source.stem).length,
      scheduledOutroCount: [...sources.values()].filter(
        (source) => source.stem?.outroScheduled,
      ).length,
      scheduledOutroMixLevels: Object.freeze(
        [...sources.values()]
          .filter((source) => source.stem?.outroScheduled)
          .map((source) => source.mixLevel),
      ),
      scheduledOutroDelays: Object.freeze(
        [...sources.values()]
          .filter((source) => source.stem?.outroScheduled)
          .map(
            (source) => (
              source.stem.outroStartsAt - source.stem.outroRequestedAt
            ),
          ),
      ),
      loopPhaseStemCount: [...sources.values()].filter(
        (source) => (
          source.stem
          && context
          && context.currentTime >= source.stem.loopStartedAt
          && !source.stem.outroScheduled
        ),
      ).length,
      spatialSourceCount: [...sources.values()].filter(
        (source) => source.position && source.panner,
      ).length,
      attenuatedSourceCount: [...sources.values()].filter(
        (source) => source.distanceGain < 1,
      ).length,
      movingSourceCount: motions.size,
      automatedGainSourceCount: gainAutomations.size,
    });
  }

  return {
    unlock,
    recoverAfterForeground,
    setMicrophoneActive,
    handleAudioCommand,
    playSound,
    playMusic,
    playAmbience,
    pauseMusic,
    resumeMusic,
    stopMusic,
    stopAmbience,
    stopAll,
    setBus,
    setMusicVolumePercent,
    setAmbienceVolumePercent,
    setEffectsVolumePercent,
    getMusicVolumePercent: () => Math.round(masterValues.music * 100),
    getAmbienceVolumePercent: () => Math.round(masterValues.ambience * 100),
    getEffectsVolumePercent: () => Math.round(masterValues.sfx * 100),
    setSoundVersion,
    preloadEffects,
    preloadEffectFamily,
    setMuted,
    isMuted: () => muted,
    retryPendingPlayback,
    getDiagnostics,
    setSoundBaseUrl: (value) => { soundBaseUrl = value; },
  };
}
