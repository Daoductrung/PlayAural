const AUDIO_PROTOCOL_VERSION = 1;
const MAX_ACTIVE_EFFECTS = 64;
const MAX_ACTIVE_LAYERS = 32;
const MAX_CACHED_EFFECTS = 128;
const MAX_CACHED_BUFFER_BYTES = 96 * 1024 * 1024;
const MAX_PENDING_EFFECTS = 32;
const MAX_GENERATION_ENTRIES = 512;
const MAX_FADE_MS = 60000;

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

function validId(value) {
  return /^[A-Za-z0-9_.:-]{1,128}$/.test(String(value || ""));
}

function normalizeDucking(ducking) {
  return new Map(Object.entries(ducking || {}).map(
    ([bus, gain]) => [String(bus), clamp(gain, 0, 100, 100) / 100],
  ));
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

export function createAudioEngine(options = {}) {
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
  const effectBuffers = new Map();
  const effectBufferSizes = new Map();
  let effectBufferBytes = 0;
  const pendingEffects = [];
  const pendingMusic = new Map();
  const pendingAmbiences = new Map();
  const pausedMusicHandles = new Set();

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
  }

  function nextGeneration(handle) {
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
    if (source.output && context) {
      source.output.gain.setValueAtTime(bounded, context.currentTime);
    } else if (source.audio) {
      source.audio.volume = muted ? 0 : bounded
        * masterValues[source.kind] * effectiveBusGain(source.bus);
    }
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
      handles.delete(source.handle);
    }
    if (source.target && targets.get(source.target) === key) {
      targets.delete(source.target);
    }
    for (const node of source.nodes || []) {
      try { node.disconnect(); } catch { /* already disconnected */ }
    }
    try { source.node?.disconnect(); } catch { /* already disconnected */ }
    try { source.panner?.disconnect(); } catch { /* already disconnected */ }
    try { source.output?.disconnect(); } catch { /* already disconnected */ }
    refreshDucking();
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
      const elapsed = Math.max(0, context.currentTime - source.startedAt);
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
      playElement({
        kind,
        asset: outroAsset,
        handle: outroHandle,
        bus,
        volume: source.baseVolume * 100,
        loop: false,
      }, "", nextGeneration(outroHandle));
    }
  }

  function scheduleStemOutro(source, mode = "immediate") {
    if (
      !context
      || !source.stem?.outroBuffer
      || source.stem.outroScheduled
      || context.currentTime < source.stem.loopStartedAt
      || source.stem.loopDuration <= 0
    ) {
      return false;
    }
    const elapsed = Math.max(0, context.currentTime - source.stem.loopStartedAt);
    const cycles = Math.floor(elapsed / source.stem.loopDuration) + 1;
    const boundary = mode === "boundary"
      ? source.stem.loopStartedAt + (cycles * source.stem.loopDuration)
      : context.currentTime + 0.02;
    const outroNode = context.createBufferSource();
    outroNode.buffer = source.stem.outroBuffer;
    outroNode.connect(source.output);
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
    source.stem.outroRequestedAt = context.currentTime;
    source.stem.outroStartsAt = boundary;
    source.outro = "";
    if (handles.get(source.handle) === source.key) {
      handles.delete(source.handle);
    }
    outroNode.addEventListener("ended", () => cleanup(source.key), { once: true });
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
        .then((bytes) => context.decodeAudioData(bytes))
        .then((buffer) => {
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
    output.gain.value = packet.fade_in_ms ? 0 : baseVolume;
    node.buffer = buffer;
    node.loop = Boolean(packet.loop);
    node.playbackRate.value = clamp(packet.pitch, 25, 400, 100) / 100;
    let panner = null;
    if (typeof context.createStereoPanner === "function") {
      panner = context.createStereoPanner();
      panner.pan.value = clamp(packet.pan, -100, 100, 0) / 100;
      node.connect(panner);
      panner.connect(output);
    } else {
      node.connect(output);
    }
    output.connect(busNode("sfx", packet.bus || "sfx"));
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
    };
    register(source);
    node.addEventListener("ended", () => cleanup(key), { once: true });
    node.start();
    if (packet.fade_in_ms) {
      fade(source, baseVolume, packet.fade_in_ms);
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

  function connectElement(audio, kind, bus) {
    if (!context) {
      return { output: null, panner: null };
    }
    try {
      const node = context.createMediaElementSource(audio);
      const output = context.createGain();
      node.connect(output);
      output.connect(busNode(kind, bus));
      return { output, panner: node };
    } catch {
      return { output: null, panner: null };
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
    const connected = connectElement(audio, kind, bus);
    const baseVolume = clamp(packet.volume, 0, 100, 100) / 100;
    audio.loop = Boolean(packet.loop);
    audio.muted = muted;
    audio.playbackRate = kind === "sfx"
      ? clamp(packet.pitch, 25, 400, 100) / 100
      : 1;
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
      node: null,
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
    node.connect(source.output);
    const boundedOffset = source.buffer.duration > 0
      ? Math.min(Math.max(0, offset), source.buffer.duration)
      : 0;
    source.nodeToken += 1;
    const nodeToken = source.nodeToken;
    source.node = node;
    source.nodes.add(node);
    source.startedAt = context.currentTime - boundedOffset;
    node.addEventListener("ended", () => {
      source.nodes.delete(node);
      if (
        source.active
        && !source.paused
        && !source.loop
        && source.nodeToken === nodeToken
      ) {
        cleanup(source.key);
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
  ) {
    if (!context) {
      return false;
    }
    if (context.state !== "running") {
      pendingMusic.set(target, { ...packet, handle });
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
    if (pausedMusicHandles.has(handle)) {
      pendingMusic.set(target, { ...packet, handle });
      return true;
    }
    const output = context.createGain();
    const bus = String(packet.bus || "music");
    const baseVolume = clamp(packet.volume, 0, 100, 100) / 100;
    output.gain.value = packet.fade_in_ms ? 0 : baseVolume;
    output.connect(busNode("music", bus));
    const key = sourceId();
    const source = {
      key,
      handle,
      generation,
      kind: "music",
      bus,
      asset: packet.asset,
      priority: clamp(packet.priority, -100, 100, 0),
      createdAt: performance.now(),
      baseVolume,
      node: null,
      output,
      panner: null,
      audio: null,
      target,
      outro: "",
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
    };
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
    const bus = String(packet.bus || "ambience");
    const baseVolume = clamp(packet.volume, 0, 100, 100) / 100;
    output.gain.value = packet.fade_in_ms ? 0 : baseVolume;
    output.connect(busNode("ambience", bus));
    const introNode = introBuffer ? context.createBufferSource() : null;
    const loopNode = context.createBufferSource();
    const startAt = context.currentTime + 0.03;
    const loopStartedAt = startAt + (introBuffer?.duration || 0);
    if (introNode) {
      introNode.buffer = introBuffer;
      introNode.connect(output);
    }
    loopNode.buffer = loopBuffer;
    loopNode.loop = packet.loop !== false;
    loopNode.connect(output);
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
      node: loopNode,
      nodes,
      output,
      panner: null,
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
        loopDuration: loopBuffer.duration,
        outroBuffer,
        outroScheduled: false,
        outroRequestedAt: 0,
        outroStartsAt: 0,
      },
      buffer: null,
      bufferOffset: 0,
      startedAt: 0,
      nodeToken: 0,
    };
    register(source);
    if (introNode) {
      introNode.start(startAt);
    }
    loopNode.start(loopStartedAt);
    if (!loopNode.loop) {
      loopNode.addEventListener("ended", () => cleanup(key), { once: true });
    }
    if (packet.fade_in_ms) {
      fade(source, baseVolume, packet.fade_in_ms);
    }
    return true;
  }

  async function playSound(packet) {
    const asset = validAsset(packet.asset || packet.name || packet.sound);
    if (!asset) {
      return "";
    }
    const normalized = {
      ...packet,
      kind: "sfx",
      asset,
      bus: packet.bus || "sfx",
      volume: packet.volume ?? 100,
      pan: packet.pan ?? 0,
      pitch: packet.pitch ?? 100,
    };
    const handle = String(packet.handle || `sfx:${sourceId()}`);
    cancelPendingHandle(handle);
    const generation = nextGeneration(handle);
    const oldKey = handles.get(handle);
    if (oldKey) {
      await stopKey(oldKey, packet.fade_out_ms || 0);
    }
    if (!await playBufferedEffect(normalized, handle, generation)) {
      playElement({ ...normalized, handle }, "", generation);
    }
    return handle;
  }

  function playLayer(packet) {
    const kind = packet.kind;
    const asset = validAsset(packet.asset);
    if (!asset || !["music", "ambience"].includes(kind)) {
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
    if (!intro) {
      const fallbackToBufferedMusic = kind === "music"
        ? (failedSource) => {
            if (
              generations.get(handle) !== generation
              || targetGenerations.get(target) !== targetGeneration
            ) {
              return;
            }
            if (pausedMusicHandles.has(handle) || failedSource.paused) {
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
                normalized,
                target,
                handle,
                generation,
                targetGeneration,
              )
            )).then((played) => {
              if (
                !played
                && generations.get(handle) === generation
                && targetGenerations.get(target) === targetGeneration
              ) {
                pendingMusic.set(target, normalized);
              }
            });
          }
        : null;
      playElement(
        normalized,
        target,
        generation,
        null,
        fallbackToBufferedMusic,
      );
      return handle;
    }
    playElement(
      { ...normalized, asset: intro, loop: false, outro: "" },
      target,
      generation,
      () => {
        if (generations.get(handle) === generation) {
          playElement(normalized, target, generation);
        }
      },
    );
    return handle;
  }

  function playMusic(packet) {
    return playLayer({
      ...packet,
      kind: "music",
      asset: packet.asset || packet.name || packet.music,
      handle: packet.handle || "music",
      layer: packet.layer || "main",
      fade_in_ms: packet.fade_in_ms ?? 800,
      fade_out_ms: packet.fade_out_ms ?? 800,
      loop: packet.loop ?? packet.looping ?? true,
    });
  }

  function playAmbience(packet) {
    return playLayer({
      ...packet,
      kind: "ambience",
      asset: packet.asset || packet.loop,
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
    if (Number(packet.version) !== AUDIO_PROTOCOL_VERSION) {
      return false;
    }
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
    switch (packet.command) {
      case "play":
        if (
          !["sfx", "music", "ambience"].includes(packet.kind)
          || !validAsset(packet.asset)
        ) {
          return false;
        }
        if (packet.kind === "sfx") {
          playSound(packet);
        } else {
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

  async function unlock() {
    if (context?.state === "suspended") {
      await context.resume().catch(() => null);
    }
    retryPendingPlayback();
    return !context || context.state === "running";
  }

  function retryPendingPlayback() {
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
        .then(() => playBufferedEffect(packet, handle, generation))
        .then((played) => {
          if (!played && generations.get(handle) === generation) {
            playElement(packet, "", generation);
          }
        });
    }
  }

  function preloadEffects(names = []) {
    for (const name of names) {
      const asset = validAsset(name);
      if (asset) {
        loadEffect(asset);
      }
    }
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
    });
  }

  return {
    unlock,
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
    setMuted,
    isMuted: () => muted,
    retryPendingPlayback,
    getDiagnostics,
    setSoundBaseUrl: (value) => { soundBaseUrl = value; },
  };
}
