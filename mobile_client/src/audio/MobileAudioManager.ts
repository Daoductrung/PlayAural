import {
  Audio as ExpoAudio,
  InterruptionModeAndroid,
  InterruptionModeIOS,
} from "expo-av";
import type {
  AVPlaybackSource,
  AVPlaybackStatus,
  AVPlaybackStatusToSet,
} from "expo-av";
import {
  createAudioPlaylist,
  setAudioModeAsync as setModernAudioModeAsync,
} from "expo-audio";
import type {
  AudioPlaylist,
  AudioPlaylistStatus,
  AudioSource as ModernAudioSource,
} from "expo-audio";
import { Asset } from "expo-asset";
import { requireNativeModule } from "expo-modules-core";
import { Platform } from "react-native";

import { soundManifest } from "../generated/soundManifest";
import type { AudioCommandPacket, AudioKind } from "../network/packets";

type CommandAudioSource = {
  active: boolean;
  asset: string;
  baseVolume: number;
  bus: string;
  createdAt: number;
  ducking: Map<string, number>;
  envelope: number;
  fadeToken: number;
  generation: number;
  handle: string;
  key: string;
  kind: AudioKind;
  nativePlayer: ExpoAudio.Sound | null;
  nativeStem: NativeStemState | null;
  outro: string;
  paused: boolean;
  priority: number;
  target: string;
  webGain: GainNode | null;
  webNode: AudioBufferSourceNode | MediaElementAudioSourceNode | null;
  webNodes: Set<AudioBufferSourceNode>;
  webStem: WebStemState | null;
  webElement: HTMLAudioElement | null;
  webPanner: StereoPannerNode | null;
};

type NativeStemState = {
  loopIndex: number;
  outroIndex: number;
  outroRequested: boolean;
  playlist: AudioPlaylist;
  statusSubscription: { remove(): void };
  trackSubscription: { remove(): void };
};

type WebStemState = {
  loopDuration: number;
  loopNode: AudioBufferSourceNode;
  loopStartedAt: number;
  outroBuffer: AudioBuffer | null;
  outroScheduled: boolean;
};

type AndroidNativeAudioMode = {
  interruptionModeAndroid: number;
  shouldDuckAndroid: boolean;
  staysActiveInBackground: boolean;
};

type MusicPlaybackOptions = Pick<
  AudioCommandPacket,
  | "bus"
  | "context"
  | "fade_in_ms"
  | "fade_out_ms"
  | "handle"
  | "layer"
  | "loop"
  | "priority"
  | "scope"
  | "volume"
>;

type ExponentAVModule = {
  setAudioMode(mode: AndroidNativeAudioMode): Promise<void>;
};

const AUDIO_PROTOCOL_VERSION = 1;
const MAX_ACTIVE_EFFECTS = 64;
const MAX_ACTIVE_LAYERS = 32;
const MAX_CACHED_EFFECTS = 128;
const MAX_CACHED_BUFFER_BYTES = 96 * 1024 * 1024;
const MAX_CACHED_ASSET_URIS = 512;
const MAX_GENERATION_ENTRIES = 512;
const MAX_FADE_MS = 60_000;

const exponentAV = Platform.OS === "android"
  ? requireNativeModule<ExponentAVModule>("ExponentAV")
  : null;

export class MobileAudioManager {
  private initialized = false;
  private nativeAudioModeReady = false;
  private nativeAudioModeLoading: Promise<void> | null = null;
  private musicVolume = 0.2;
  private soundVolume = 1;
  private ambienceVolume = 0.3;

  private nativeSourceCache = new Map<string, AVPlaybackSource>();
  private nativeSourceLoading = new Map<string, Promise<AVPlaybackSource | null>>();
  private nativeSoundVolumes = new WeakMap<ExpoAudio.Sound, number>();

  private webAudioContext: AudioContext | null = null;
  private webMasterGain: GainNode | null = null;
  private webMusicBus: GainNode | null = null;
  private webSfxBus: GainNode | null = null;
  private webAmbienceBus: GainNode | null = null;
  private webBufferCache = new Map<string, AudioBuffer>();
  private webBufferCacheBytes = 0;
  private webBufferLoading = new Map<string, Promise<AudioBuffer | null>>();
  private webUriCache = new Map<string, string>();
  private webCommandBuses = new Map<
    string,
    { bus: string; kind: AudioKind; node: GainNode }
  >();

  private commandSources = new Map<string, CommandAudioSource>();
  private commandHandles = new Map<string, string>();
  private commandTargets = new Map<string, string>();
  private commandTargetGenerations = new Map<string, number>();
  private commandGenerations = new Map<string, number>();
  private commandPausedMusicHandles = new Set<string>();
  private commandBusGains = new Map<string, number>();
  private commandBusFadeTokens = new Map<string, number>();
  private commandDucking = new Map<string, Map<string, number>>();
  private stateListener: (() => void) | null = null;

  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }
    if (Platform.OS !== "web") {
      await this.ensureNativeAudioMode();
    }
    this.initialized = true;
  }

  shutdown(): void {
    this.stopAllManagedAudio(0);
    for (const record of this.webCommandBuses.values()) {
      try {
        record.node.disconnect();
      } catch {
        // Ignore already-disconnected command buses.
      }
    }
    this.webCommandBuses.clear();
    this.initialized = false;
  }

  async handleUserInteraction(): Promise<void> {
    if (Platform.OS !== "web") {
      return;
    }
    await this.ensureWebAudioReady();
    for (const source of this.commandSources.values()) {
      if (source.active && !source.paused && source.webElement?.paused) {
        void source.webElement.play().catch(() => undefined);
      }
    }
  }

  setMusicVolume(volume: number): void {
    this.musicVolume = this.clamp(volume, 0, 1, 0.2);
    this.setWebMasterBus(this.webMusicBus, this.musicVolume);
    this.refreshMix();
    this.stateListener?.();
  }

  setAmbienceVolume(volume: number): void {
    this.ambienceVolume = this.clamp(volume, 0, 1, 0.3);
    this.setWebMasterBus(this.webAmbienceBus, this.ambienceVolume);
    this.refreshMix();
    this.stateListener?.();
  }

  setSoundVolume(volume: number): void {
    this.soundVolume = this.clamp(volume, 0, 1, 1);
    this.setWebMasterBus(this.webSfxBus, this.soundVolume);
    this.refreshMix();
    this.stateListener?.();
  }

  getMusicVolume(): number {
    return this.musicVolume;
  }

  getAmbienceVolume(): number {
    return this.ambienceVolume;
  }

  getSoundVolume(): number {
    return this.soundVolume;
  }

  setStateListener(listener: (() => void) | null): void {
    this.stateListener = listener;
    listener?.();
  }

  getActiveLayerAssets(kind: "music" | "ambience"): string[] {
    return [...this.commandSources.values()]
      .filter((source) => source.active && source.kind === kind)
      .sort((left, right) => left.createdAt - right.createdAt)
      .map((source) => source.asset);
  }

  hasAudibleManagedLayers(): boolean {
    return [...this.commandSources.values()].some((source) => (
      source.active
      && !source.paused
      && source.kind !== "sfx"
      && source.baseVolume > 0
      && this.masterGain(source.kind) > 0
      && (this.commandBusGains.get(source.bus) ?? 1) > 0
    ));
  }

  refreshPlaybackState(): void {
    this.refreshMix();
    if (Platform.OS === "web") {
      return;
    }
    for (const source of this.commandSources.values()) {
      if (source.nativePlayer && !source.paused) {
        void source.nativePlayer.playAsync().catch(() => undefined);
      }
      if (source.nativeStem && !source.paused) {
        source.nativeStem.playlist.play();
      }
    }
  }

  async playSound(
    name: string,
    options: { volume?: number; pitch?: number; pan?: number } = {},
  ): Promise<boolean> {
    const asset = this.normalizeAsset(name);
    if (!asset) {
      return false;
    }
    return this.playManagedEffect({
      type: "audio",
      version: AUDIO_PROTOCOL_VERSION,
      command: "play",
      kind: "sfx",
      asset,
      volume: (options.volume ?? 1) * 100,
      pitch: (options.pitch ?? 1) * 100,
      pan: (options.pan ?? 0) * 100,
      priority: 100,
    });
  }

  playMusic(
    name: string,
    options: MusicPlaybackOptions = {},
  ): Promise<boolean> {
    return this.handleAudioCommand({
      ...options,
      type: "audio",
      version: AUDIO_PROTOCOL_VERSION,
      command: "play",
      kind: "music",
      asset: name,
      bus: options.bus ?? "music",
      handle: options.handle ?? "music",
      layer: options.layer ?? "main",
      loop: options.loop ?? true,
    });
  }

  stopMusic(handle = "music", fadeMs = 800): Promise<boolean> {
    return this.handleAudioCommand({
      type: "audio",
      version: AUDIO_PROTOCOL_VERSION,
      command: "stop",
      kind: "music",
      handle,
      fade_out_ms: fadeMs,
    });
  }

  async handleAudioCommand(packet: AudioCommandPacket): Promise<boolean> {
    if (!packet || typeof packet !== "object" || Array.isArray(packet)) {
      return false;
    }
    if (packet.version !== AUDIO_PROTOCOL_VERSION) {
      return false;
    }
    for (const value of [
      packet.handle,
      packet.bus,
      packet.context,
      packet.layer,
    ]) {
      if (value && !this.validId(value)) {
        return false;
      }
    }
    if (!["global", "player", "context"].includes(packet.scope ?? "global")) {
      return false;
    }
    const outroMode = packet.outro_mode ?? "immediate";
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
    const ducking = packet.ducking ?? {};
    if (
      typeof ducking !== "object"
      || Array.isArray(ducking)
      || Object.keys(ducking).length > 32
    ) {
      return false;
    }
    if (Object.keys(ducking).some((bus) => !this.validId(bus))) {
      return false;
    }
    switch (packet.command) {
      case "play":
        if (
          !packet.kind
          || !["sfx", "music", "ambience"].includes(packet.kind)
          || !this.normalizeAsset(packet.asset || "")
        ) {
          return false;
        }
        return packet.kind === "sfx"
          ? this.playManagedEffect(packet)
          : this.playManagedLayer(packet);
      case "stop":
        if (
          !packet.kind
          || !["sfx", "music", "ambience"].includes(packet.kind)
          || (["sfx", "music"].includes(packet.kind) && !packet.handle)
        ) {
          return false;
        }
        this.stopManagedCommand(packet, false);
        return true;
      case "pause":
        if (packet.kind !== "music" || !packet.handle) {
          return false;
        }
        this.stopManagedCommand(packet, true);
        return true;
      case "resume":
        if (packet.kind !== "music" || !packet.handle) {
          return false;
        }
        this.resumeManagedCommand(packet);
        return true;
      case "set_bus":
        if (!packet.bus) {
          return false;
        }
        this.setCommandBusGain(
          packet.bus,
          this.clamp(packet.volume, 0, 100, 100) / 100,
          packet.fade_in_ms ?? 0,
        );
        return true;
      case "stop_all":
        this.stopAllManagedAudio(
          packet.fade_out_ms ?? 0,
          packet.play_outros === true,
          outroMode,
        );
        return true;
      default:
        return false;
    }
  }

  stopAll(fadeMs = 800): void {
    this.stopAllManagedAudio(fadeMs);
  }

  private clamp(
    value: unknown,
    minimum: number,
    maximum: number,
    fallback: number,
  ): number {
    const parsed = Number(value);
    return Math.max(
      minimum,
      Math.min(maximum, Number.isFinite(parsed) ? parsed : fallback),
    );
  }

  private normalizeAsset(name: string): string {
    const normalized = String(name || "").trim().replaceAll("\\", "/");
    if (
      !normalized
      || normalized.length > 256
      || normalized.startsWith("/")
      || normalized.includes(":")
      || normalized.includes("?")
      || normalized.includes("#")
      || normalized.split("/").some(
        (part) => !part || part === "." || part === "..",
      )
    ) {
      return "";
    }
    return normalized;
  }

  private validId(value: string): boolean {
    return /^[A-Za-z0-9_.:-]{1,128}$/.test(value);
  }

  private target(packet: AudioCommandPacket): string {
    return `${packet.kind ?? ""}:${packet.scope ?? "global"}:${packet.context ?? ""}:${packet.layer ?? "main"}`;
  }

  private nextGeneration(handle: string): number {
    const next = (this.commandGenerations.get(handle) ?? 0) + 1;
    this.commandGenerations.delete(handle);
    this.commandGenerations.set(handle, next);
    while (this.commandGenerations.size > MAX_GENERATION_ENTRIES) {
      const removable = [...this.commandGenerations.keys()].find(
        (candidate) => !this.commandHandles.has(candidate),
      );
      if (!removable) {
        break;
      }
      this.commandGenerations.delete(removable);
    }
    return next;
  }

  private nextTargetGeneration(target: string): number {
    const next = (this.commandTargetGenerations.get(target) ?? 0) + 1;
    this.commandTargetGenerations.delete(target);
    this.commandTargetGenerations.set(target, next);
    while (this.commandTargetGenerations.size > MAX_GENERATION_ENTRIES) {
      const removable = [...this.commandTargetGenerations.keys()].find(
        (candidate) => !this.commandTargets.has(candidate),
      );
      if (!removable) {
        break;
      }
      this.commandTargetGenerations.delete(removable);
    }
    return next;
  }

  private masterGain(kind: AudioKind): number {
    if (kind === "music") {
      return this.musicVolume;
    }
    if (kind === "ambience") {
      return this.ambienceVolume;
    }
    return this.soundVolume;
  }

  private duckGain(bus: string): number {
    let gain = 1;
    for (const request of this.commandDucking.values()) {
      gain = Math.min(gain, request.get(bus) ?? 1);
    }
    return gain;
  }

  private outputGain(source: CommandAudioSource): number {
    const mix = source.baseVolume
      * (this.commandBusGains.get(source.bus) ?? 1)
      * this.duckGain(source.bus)
      * source.envelope;
    return Platform.OS === "web" ? mix : mix * this.masterGain(source.kind);
  }

  private setCommandBusGain(
    bus: string,
    destination: number,
    durationMs: number,
  ): void {
    const duration = this.clamp(durationMs, 0, MAX_FADE_MS, 0);
    const start = this.commandBusGains.get(bus) ?? 1;
    const token = (this.commandBusFadeTokens.get(bus) ?? 0) + 1;
    this.commandBusFadeTokens.set(bus, token);
    if (!duration) {
      this.commandBusGains.set(bus, destination);
      this.refreshMix();
      return;
    }
    const started = Date.now();
    const timer = setInterval(() => {
      if (this.commandBusFadeTokens.get(bus) !== token) {
        clearInterval(timer);
        return;
      }
      const ratio = Math.min(1, (Date.now() - started) / duration);
      this.commandBusGains.set(
        bus,
        start + ((destination - start) * ratio),
      );
      this.refreshMix();
      if (ratio >= 1) {
        clearInterval(timer);
      }
    }, 25);
  }

  private setAbsoluteVolume(
    source: CommandAudioSource,
    volume: number,
  ): void {
    const bounded = this.clamp(volume, 0, 1, 0);
    if (source.nativePlayer) {
      this.setNativeSoundVolume(source.nativePlayer, bounded);
    }
    if (source.nativeStem) {
      source.nativeStem.playlist.volume = bounded;
    }
    if (source.webGain && this.webAudioContext) {
      source.webGain.gain.setValueAtTime(
        bounded,
        this.webAudioContext.currentTime,
      );
    }
  }

  private refreshMix(): void {
    for (const source of this.commandSources.values()) {
      if (!source.paused) {
        this.setAbsoluteVolume(source, this.outputGain(source));
      }
    }
  }

  private setWebMasterBus(bus: GainNode | null, value: number): void {
    if (bus && this.webAudioContext) {
      bus.gain.setTargetAtTime(value, this.webAudioContext.currentTime, 0.05);
    }
  }

  private async webBus(kind: AudioKind, bus: string): Promise<GainNode | null> {
    const context = await this.ensureWebAudioReady();
    if (!context) {
      return null;
    }
    const key = `${kind}:${bus}`;
    const cached = this.webCommandBuses.get(key);
    if (cached) {
      return cached.node;
    }
    const parent = kind === "sfx"
      ? this.webSfxBus
      : kind === "music"
        ? this.webMusicBus
        : this.webAmbienceBus;
    if (!parent) {
      return null;
    }
    const node = context.createGain();
    node.gain.value = 1;
    node.connect(parent);
    this.webCommandBuses.set(key, { bus, kind, node });
    return node;
  }

  private register(source: CommandAudioSource): void {
    this.commandSources.set(source.key, source);
    this.commandHandles.set(source.handle, source.key);
    if (source.target) {
      this.commandTargets.set(source.target, source.key);
    }
    if (source.ducking.size) {
      this.commandDucking.set(source.key, source.ducking);
      this.refreshMix();
    }
    this.stateListener?.();
  }

  private dispose(key: string): void {
    const source = this.commandSources.get(key);
    if (!source) {
      return;
    }
    source.active = false;
    this.commandSources.delete(key);
    this.commandDucking.delete(key);
    if (this.commandHandles.get(source.handle) === key) {
      this.commandHandles.delete(source.handle);
    }
    if (source.target && this.commandTargets.get(source.target) === key) {
      this.commandTargets.delete(source.target);
    }
    if (source.nativePlayer) {
      this.disposeNativeSound(source.nativePlayer);
    }
    if (source.nativeStem) {
      source.nativeStem.statusSubscription.remove();
      source.nativeStem.trackSubscription.remove();
      source.nativeStem.playlist.destroy();
      source.nativeStem = null;
    }
    if (source.webElement) {
      source.webElement.onended = null;
      source.webElement.pause();
      source.webElement.currentTime = 0;
    } else {
      for (const node of source.webNodes) {
        try {
          node.stop();
        } catch {
          // A sibling stem segment may already have ended.
        }
      }
    }
    for (const node of source.webNodes) {
      try {
        node.disconnect();
      } catch {
        // Ignore double-disconnect races.
      }
    }
    try {
      source.webNode?.disconnect();
    } catch {
      // Ignore double-disconnect races.
    }
    try {
      source.webPanner?.disconnect();
    } catch {
      // Ignore double-disconnect races.
    }
    try {
      source.webGain?.disconnect();
    } catch {
      // Ignore double-disconnect races.
    }
    this.refreshMix();
    this.stateListener?.();
  }

  private fade(
    source: CommandAudioSource,
    destination: number,
    durationMs: number,
    onComplete?: () => void,
  ): void {
    const duration = this.clamp(durationMs, 0, MAX_FADE_MS, 0);
    const start = source.envelope;
    source.fadeToken += 1;
    const fadeToken = source.fadeToken;
    if (!duration) {
      source.envelope = destination;
      this.setAbsoluteVolume(source, this.outputGain(source));
      onComplete?.();
      return;
    }
    const started = Date.now();
    const timer = setInterval(() => {
      if (!source.active || source.fadeToken !== fadeToken) {
        clearInterval(timer);
        return;
      }
      const ratio = Math.min(1, (Date.now() - started) / duration);
      source.envelope = start + ((destination - start) * ratio);
      this.setAbsoluteVolume(source, this.outputGain(source));
      if (ratio >= 1) {
        clearInterval(timer);
        onComplete?.();
      }
    }, 25);
  }

  private stopKey(
    key: string,
    fadeMs: number,
    pause: boolean,
    playOutro: boolean,
    outroMode: "immediate" | "boundary" = "immediate",
  ): void {
    const source = this.commandSources.get(key);
    if (!source) {
      return;
    }
    const seamlessStem = Boolean(source.nativeStem || source.webStem);
    if (
      playOutro
      && source.outro
      && seamlessStem
      && (
        this.scheduleNativeStemOutro(source, outroMode)
        || this.scheduleWebStemOutro(source, outroMode)
      )
    ) {
      return;
    }
    if (pause) {
      source.paused = true;
    }
    this.fade(source, 0, fadeMs, () => {
      if (!source.active) {
        return;
      }
      if (pause) {
        if (source.nativePlayer) {
          void source.nativePlayer.pauseAsync().catch(() => undefined);
        }
        source.nativeStem?.playlist.pause();
        source.webElement?.pause();
        this.stateListener?.();
        return;
      }
      const outro = playOutro && !seamlessStem ? source.outro : "";
      const { kind, bus, baseVolume } = source;
      this.dispose(key);
      if (outro) {
        const handle = `outro:${Date.now()}:${Math.random()}`;
        const generation = this.nextGeneration(handle);
        void this.createSource(
          {
            type: "audio",
            version: AUDIO_PROTOCOL_VERSION,
            command: "play",
            kind,
            asset: outro,
            handle,
            bus,
            volume: baseVolume * 100,
          },
          outro,
          handle,
          generation,
          "",
          false,
        );
      }
    });
  }

  private detachSourceHandle(source: CommandAudioSource): void {
    if (this.commandHandles.get(source.handle) === source.key) {
      this.commandHandles.delete(source.handle);
    }
    this.stateListener?.();
  }

  private scheduleNativeStemOutro(
    source: CommandAudioSource,
    mode: "immediate" | "boundary",
  ): boolean {
    const stem = source.nativeStem;
    if (
      !stem
      || stem.outroRequested
      || stem.outroIndex < 0
      || stem.playlist.currentIndex !== stem.loopIndex
    ) {
      return false;
    }
    stem.outroRequested = true;
    stem.playlist.loop = "none";
    source.asset = source.outro;
    source.outro = "";
    this.detachSourceHandle(source);
    if (mode === "immediate") {
      stem.playlist.skipTo(stem.outroIndex);
      stem.playlist.play();
    }
    return true;
  }

  private scheduleWebStemOutro(
    source: CommandAudioSource,
    mode: "immediate" | "boundary",
  ): boolean {
    const context = this.webAudioContext;
    const stem = source.webStem;
    if (
      !context
      || !source.webGain
      || !stem?.outroBuffer
      || stem.outroScheduled
      || context.currentTime < stem.loopStartedAt
      || stem.loopDuration <= 0
    ) {
      return false;
    }
    const elapsed = Math.max(0, context.currentTime - stem.loopStartedAt);
    const cycles = Math.floor(elapsed / stem.loopDuration) + 1;
    const boundary = mode === "boundary"
      ? stem.loopStartedAt + (cycles * stem.loopDuration)
      : context.currentTime + 0.02;
    const outroNode = context.createBufferSource();
    outroNode.buffer = stem.outroBuffer;
    outroNode.connect(source.webGain);
    try {
      stem.loopNode.stop(boundary);
      outroNode.start(boundary);
    } catch {
      outroNode.disconnect();
      return false;
    }
    source.webNodes.add(outroNode);
    stem.outroScheduled = true;
    source.asset = source.outro;
    source.outro = "";
    this.detachSourceHandle(source);
    outroNode.addEventListener("ended", () => {
      this.dispose(source.key);
    }, { once: true });
    return true;
  }

  private modernNativeSource(name: string): ModernAudioSource | null {
    const source = this.resolveSource(name);
    if (typeof source === "number") {
      return source;
    }
    if (source && typeof source === "object" && "uri" in source) {
      return { uri: String(source.uri) };
    }
    return null;
  }

  private async createNativeStemSource(
    packet: AudioCommandPacket,
    handle: string,
    generation: number,
    target: string,
    targetGeneration: number,
  ): Promise<CommandAudioSource | null> {
    await this.initialize();
    const isCurrent = () => (
      this.commandGenerations.get(handle) === generation
      && this.commandTargetGenerations.get(target) === targetGeneration
    );
    if (!isCurrent()) {
      return null;
    }
    const intro = packet.play_intro === false
      ? ""
      : this.normalizeAsset(packet.intro || "");
    const loop = this.normalizeAsset(packet.asset || "");
    const outro = this.normalizeAsset(packet.outro || "");
    const introSource = intro ? this.modernNativeSource(intro) : null;
    const loopSource = this.modernNativeSource(loop);
    const outroSource = outro ? this.modernNativeSource(outro) : null;
    if (!loopSource) {
      return null;
    }
    const playlistSources: ModernAudioSource[] = [];
    if (introSource) {
      playlistSources.push(introSource);
    }
    const loopIndex = playlistSources.length;
    playlistSources.push(loopSource);
    const outroIndex = outroSource ? playlistSources.length : -1;
    if (outroSource) {
      playlistSources.push(outroSource);
    }
    const playlist = createAudioPlaylist({
      sources: playlistSources,
      updateInterval: 50,
      loop: introSource || packet.loop === false ? "none" : "single",
    });
    const key = `${handle}:${Date.now()}:${Math.random()}`;
    const kind: AudioKind = "ambience";
    const source: CommandAudioSource = {
      active: true,
      asset: loop,
      baseVolume: this.clamp(packet.volume, 0, 100, 100) / 100,
      bus: String(packet.bus || kind),
      createdAt: Date.now(),
      ducking: new Map(
        Object.entries(packet.ducking ?? {}).map(([bus, gain]) => [
          bus,
          this.clamp(gain, 0, 100, 100) / 100,
        ]),
      ),
      envelope: packet.fade_in_ms ? 0 : 1,
      fadeToken: 0,
      generation,
      handle,
      key,
      kind,
      nativePlayer: null,
      nativeStem: null,
      outro,
      paused: false,
      priority: this.clamp(packet.priority, -100, 100, 0),
      target,
      webGain: null,
      webNode: null,
      webNodes: new Set(),
      webStem: null,
      webElement: null,
      webPanner: null,
    };
    const trackSubscription = playlist.addListener(
      "trackChanged",
      ({ currentIndex }: { currentIndex: number }) => {
        const stem = source.nativeStem;
        if (!source.active || !stem) {
          return;
        }
        if (
          currentIndex === stem.loopIndex
          && !stem.outroRequested
          && packet.loop !== false
        ) {
          playlist.loop = "single";
        } else if (currentIndex === stem.outroIndex) {
          playlist.loop = "none";
        }
      },
    );
    const statusSubscription = playlist.addListener(
      "playlistStatusUpdate",
      (status: AudioPlaylistStatus) => {
        if (source.active && status.didJustFinish) {
          this.dispose(key);
        }
      },
    );
    source.nativeStem = {
      loopIndex,
      outroIndex,
      outroRequested: false,
      playlist,
      statusSubscription,
      trackSubscription,
    };
    if (!isCurrent()) {
      statusSubscription.remove();
      trackSubscription.remove();
      playlist.destroy();
      return null;
    }
    playlist.volume = this.outputGain(source);
    this.register(source);
    playlist.play();
    if (packet.fade_in_ms) {
      this.fade(source, 1, packet.fade_in_ms);
    }
    return source;
  }

  private async createWebStemSource(
    packet: AudioCommandPacket,
    handle: string,
    generation: number,
    target: string,
    targetGeneration: number,
  ): Promise<CommandAudioSource | null> {
    const context = await this.ensureWebAudioReady();
    const isCurrent = () => (
      this.commandGenerations.get(handle) === generation
      && this.commandTargetGenerations.get(target) === targetGeneration
    );
    if (!context || !isCurrent()) {
      return null;
    }
    const intro = packet.play_intro === false
      ? ""
      : this.normalizeAsset(packet.intro || "");
    const loop = this.normalizeAsset(packet.asset || "");
    const outro = this.normalizeAsset(packet.outro || "");
    const [introBuffer, loopBuffer, outroBuffer] = await Promise.all([
      intro ? this.loadWebBuffer(intro) : Promise.resolve(null),
      this.loadWebBuffer(loop),
      outro ? this.loadWebBuffer(outro) : Promise.resolve(null),
    ]);
    const bus = await this.webBus("ambience", String(packet.bus || "ambience"));
    if (!loopBuffer || !bus || !isCurrent()) {
      return null;
    }
    const gain = context.createGain();
    gain.connect(bus);
    const introNode = introBuffer ? context.createBufferSource() : null;
    const loopNode = context.createBufferSource();
    const startAt = context.currentTime + 0.03;
    const loopStartedAt = startAt + (introBuffer?.duration || 0);
    if (introNode) {
      introNode.buffer = introBuffer;
      introNode.connect(gain);
    }
    loopNode.buffer = loopBuffer;
    loopNode.loop = packet.loop !== false;
    loopNode.connect(gain);
    const key = `${handle}:${Date.now()}:${Math.random()}`;
    const webNodes = new Set<AudioBufferSourceNode>([loopNode]);
    if (introNode) {
      webNodes.add(introNode);
    }
    const source: CommandAudioSource = {
      active: true,
      asset: loop,
      baseVolume: this.clamp(packet.volume, 0, 100, 100) / 100,
      bus: String(packet.bus || "ambience"),
      createdAt: Date.now(),
      ducking: new Map(
        Object.entries(packet.ducking ?? {}).map(([busName, duckGain]) => [
          busName,
          this.clamp(duckGain, 0, 100, 100) / 100,
        ]),
      ),
      envelope: packet.fade_in_ms ? 0 : 1,
      fadeToken: 0,
      generation,
      handle,
      key,
      kind: "ambience",
      nativePlayer: null,
      nativeStem: null,
      outro,
      paused: false,
      priority: this.clamp(packet.priority, -100, 100, 0),
      target,
      webGain: gain,
      webNode: loopNode,
      webNodes,
      webStem: {
        loopDuration: loopBuffer.duration,
        loopNode,
        loopStartedAt,
        outroBuffer,
        outroScheduled: false,
      },
      webElement: null,
      webPanner: null,
    };
    gain.gain.value = this.outputGain(source);
    this.register(source);
    introNode?.start(startAt);
    loopNode.start(loopStartedAt);
    if (!loopNode.loop) {
      loopNode.addEventListener("ended", () => this.dispose(key), { once: true });
    }
    if (packet.fade_in_ms) {
      this.fade(source, 1, packet.fade_in_ms);
    }
    return source;
  }

  private async createSource(
    packet: AudioCommandPacket,
    asset: string,
    handle: string,
    generation: number,
    target: string,
    looping: boolean,
    onEnded?: () => void,
    targetGeneration?: number,
  ): Promise<CommandAudioSource | null> {
    const kind = packet.kind;
    if (!kind) {
      return null;
    }
    const key = `${handle}:${Date.now()}:${Math.random()}`;
    const isCurrent = () => (
      this.commandGenerations.get(handle) === generation
      && (
        !target
        || targetGeneration === undefined
        || this.commandTargetGenerations.get(target) === targetGeneration
      )
    );
    const source: CommandAudioSource = {
      active: true,
      asset,
      baseVolume: this.clamp(packet.volume, 0, 100, 100) / 100,
      bus: String(packet.bus || kind),
      createdAt: Date.now(),
      ducking: new Map(
        Object.entries(packet.ducking ?? {}).map(([bus, gain]) => [
          bus,
          this.clamp(gain, 0, 100, 100) / 100,
        ]),
      ),
      envelope: packet.fade_in_ms ? 0 : 1,
      fadeToken: 0,
      generation,
      handle,
      key,
      kind,
      nativePlayer: null,
      nativeStem: null,
      outro: this.normalizeAsset(packet.outro || ""),
      paused: false,
      priority: this.clamp(packet.priority, -100, 100, 0),
      target,
      webGain: null,
      webNode: null,
      webNodes: new Set(),
      webStem: null,
      webElement: null,
      webPanner: null,
    };

    if (Platform.OS === "web") {
      const context = await this.ensureWebAudioReady();
      const bus = await this.webBus(kind, source.bus);
      if (!context || !bus || !isCurrent()) {
        return null;
      }
      const gain = context.createGain();
      gain.gain.value = this.outputGain(source);
      source.webGain = gain;
      if (kind === "sfx") {
        const buffer = await this.loadWebBuffer(asset);
        if (!buffer || !isCurrent()) {
          gain.disconnect();
          return null;
        }
        const node = context.createBufferSource();
        node.buffer = buffer;
        node.loop = looping;
        node.playbackRate.value = this.clamp(packet.pitch, 25, 400, 100) / 100;
        const panner = typeof context.createStereoPanner === "function"
          ? context.createStereoPanner()
          : null;
        if (panner) {
          panner.pan.value = this.clamp(packet.pan, -100, 100, 0) / 100;
          node.connect(panner);
          panner.connect(gain);
        } else {
          node.connect(gain);
        }
        gain.connect(bus);
        source.webNode = node;
        source.webNodes.add(node);
        source.webPanner = panner;
        this.register(source);
        node.onended = () => {
          this.dispose(key);
          onEnded?.();
        };
        node.start();
      } else {
        const uri = await this.resolveWebUri(asset);
        if (!uri || !isCurrent()) {
          gain.disconnect();
          return null;
        }
        const element = new Audio(uri);
        element.loop = looping;
        element.preload = "auto";
        const node = context.createMediaElementSource(element);
        node.connect(gain);
        gain.connect(bus);
        source.webElement = element;
        source.webNode = node;
        source.paused = kind === "music"
          && this.commandPausedMusicHandles.has(handle);
        this.register(source);
        element.onended = () => {
          this.dispose(key);
          onEnded?.();
        };
        if (!source.paused) {
          void element.play().catch(() => undefined);
        }
      }
    } else {
      await this.initialize();
      const resolved = await this.resolveNativeSource(asset);
      if (!resolved || !isCurrent()) {
        return null;
      }
      const player = await this.createNativeSound(
        resolved,
        {
          isLooping: looping,
          progressUpdateIntervalMillis: 100,
          rate: kind === "sfx"
            ? this.clamp(packet.pitch, 25, 400, 100) / 100
            : 1,
          shouldCorrectPitch: true,
          shouldPlay: false,
          volume: this.outputGain(source),
          ...(kind === "sfx" && Platform.OS === "android"
            ? {
                androidImplementation: "MediaPlayer" as const,
                audioPan: this.clamp(packet.pan, -100, 100, 0) / 100,
              }
            : {}),
        },
      );
      if (!player || !isCurrent()) {
        if (player) {
          this.disposeNativeSound(player);
        }
        return null;
      }
      source.nativePlayer = player;
      source.paused = kind === "music"
        && this.commandPausedMusicHandles.has(handle);
      this.register(source);
      player.setOnPlaybackStatusUpdate((status: AVPlaybackStatus) => {
        if (!status.isLoaded || !status.didJustFinish) {
          return;
        }
        player.setOnPlaybackStatusUpdate(null);
        this.dispose(key);
        onEnded?.();
      });
      if (!source.paused) {
        void player.playAsync().catch(() => this.dispose(key));
      }
    }

    if (packet.fade_in_ms && !source.paused) {
      this.fade(source, 1, packet.fade_in_ms);
    }
    return source;
  }

  private enforceEffectLimit(
    packet: AudioCommandPacket,
    asset: string,
  ): boolean {
    const effects = [...this.commandSources.values()].filter(
      (source) => source.kind === "sfx",
    );
    const matching = effects.filter((source) => source.asset === asset);
    const limit = this.clamp(packet.max_instances, 0, MAX_ACTIVE_EFFECTS, 0);
    const pool = limit && matching.length >= limit
      ? matching
      : effects.length >= MAX_ACTIVE_EFFECTS
        ? effects
        : [];
    if (!pool.length) {
      return true;
    }
    pool.sort((left, right) => (
      left.priority - right.priority || left.createdAt - right.createdAt
    ));
    const incomingPriority = this.clamp(packet.priority, -100, 100, 0);
    if (pool[0].priority > incomingPriority) {
      return false;
    }
    this.stopKey(pool[0].key, 0, false, false);
    return true;
  }

  private async playManagedEffect(packet: AudioCommandPacket): Promise<boolean> {
    const asset = this.normalizeAsset(packet.asset || "");
    if (!asset || !this.enforceEffectLimit(packet, asset)) {
      return false;
    }
    const handle = String(
      packet.handle || `sfx:${Date.now()}:${Math.random()}`,
    );
    const generation = this.nextGeneration(handle);
    const oldKey = this.commandHandles.get(handle);
    if (oldKey) {
      this.stopKey(oldKey, packet.fade_out_ms ?? 0, false, false);
    }
    return Boolean(await this.createSource(
      packet,
      asset,
      handle,
      generation,
      "",
      Boolean(packet.loop),
    ));
  }

  private async playManagedLayer(packet: AudioCommandPacket): Promise<boolean> {
    const kind = packet.kind;
    const asset = this.normalizeAsset(packet.asset || "");
    if (!kind || !asset) {
      return false;
    }
    const target = this.target(packet);
    const layers = [...this.commandSources.values()].filter(
      (source) => source.kind !== "sfx",
    );
    if (!this.commandTargets.has(target) && layers.length >= MAX_ACTIVE_LAYERS) {
      layers.sort((left, right) => (
        left.priority - right.priority || left.createdAt - right.createdAt
      ));
      const incomingPriority = this.clamp(packet.priority, -100, 100, 0);
      if (layers[0].priority > incomingPriority) {
        return false;
      }
      this.stopKey(layers[0].key, 0, false, false);
    }
    const handle = String(packet.handle || `${kind}:${target}`);
    if (kind === "music") {
      this.commandPausedMusicHandles.delete(handle);
    }
    const generation = this.nextGeneration(handle);
    const targetGeneration = this.nextTargetGeneration(target);
    const oldKey = this.commandTargets.get(target);
    if (oldKey) {
      this.commandTargets.delete(target);
      this.stopKey(oldKey, packet.fade_out_ms ?? 0, false, false);
    }
    const intro = kind === "ambience" && packet.play_intro !== false
      ? this.normalizeAsset(packet.intro || "")
      : "";
    const outro = kind === "ambience"
      ? this.normalizeAsset(packet.outro || "")
      : "";
    if (
      kind === "ambience"
      && packet.seamless !== false
      && (intro || outro)
    ) {
      return Boolean(
        Platform.OS === "web"
          ? await this.createWebStemSource(
              packet,
              handle,
              generation,
              target,
              targetGeneration,
            )
          : await this.createNativeStemSource(
              packet,
              handle,
              generation,
              target,
              targetGeneration,
            ),
      );
    }
    if (!intro) {
      return Boolean(await this.createSource(
        packet,
        asset,
        handle,
        generation,
        target,
        packet.loop ?? true,
        undefined,
        targetGeneration,
      ));
    }
    return Boolean(await this.createSource(
      { ...packet, outro: "" },
      intro,
      handle,
      generation,
      target,
      false,
      () => {
        if (
          this.commandGenerations.get(handle) === generation
          && this.commandTargetGenerations.get(target) === targetGeneration
        ) {
          void this.createSource(
            packet,
            asset,
            handle,
            generation,
            target,
            packet.loop ?? true,
            undefined,
            targetGeneration,
          );
        }
      },
      targetGeneration,
    ));
  }

  private stopManagedCommand(packet: AudioCommandPacket, pause: boolean): void {
    const outroMode = packet.outro_mode ?? "immediate";
    if (!pause && packet.kind === "ambience" && packet.all_layers) {
      for (const target of [...this.commandTargetGenerations.keys()]) {
        if (target.startsWith("ambience:")) {
          this.nextTargetGeneration(target);
        }
      }
      for (const source of [...this.commandSources.values()]) {
        if (source.kind !== "ambience") {
          continue;
        }
        this.nextGeneration(source.handle);
        this.stopKey(
          source.key,
          packet.fade_out_ms ?? 0,
          false,
          packet.play_outro !== false,
          outroMode,
        );
      }
      return;
    }
    const handle = String(packet.handle || "");
    if (pause && handle) {
      this.commandPausedMusicHandles.add(handle);
    } else if (handle) {
      this.commandPausedMusicHandles.delete(handle);
    }
    const target = !handle && packet.kind ? this.target(packet) : "";
    if (target && !pause) {
      this.nextTargetGeneration(target);
    }
    const key = handle
      ? this.commandHandles.get(handle)
      : target
        ? this.commandTargets.get(target)
        : undefined;
    if (!key) {
      if (handle && !pause) {
        this.nextGeneration(handle);
      }
      return;
    }
    const source = this.commandSources.get(key);
    if (!source) {
      return;
    }
    if (!pause) {
      this.nextGeneration(source.handle);
    }
    this.stopKey(
      key,
      packet.fade_out_ms ?? 0,
      pause,
      !pause && source.kind === "ambience" && packet.play_outro !== false,
      outroMode,
    );
  }

  private resumeManagedCommand(packet: AudioCommandPacket): void {
    const handle = String(packet.handle || "");
    this.commandPausedMusicHandles.delete(handle);
    const key = this.commandHandles.get(handle);
    const source = key ? this.commandSources.get(key) : null;
    if (!source?.paused) {
      return;
    }
    source.paused = false;
    this.setAbsoluteVolume(source, this.outputGain(source));
    if (source.nativePlayer) {
      void source.nativePlayer.playAsync().catch(() => undefined);
    }
    source.nativeStem?.playlist.play();
    if (source.webElement) {
      void source.webElement.play().catch(() => undefined);
    }
    this.fade(source, 1, packet.fade_in_ms ?? 0);
    this.stateListener?.();
  }

  private stopAllManagedAudio(
    fadeMs: number,
    playOutros = false,
    outroMode: "immediate" | "boundary" = "immediate",
  ): void {
    this.commandPausedMusicHandles.clear();
    for (const handle of [...this.commandGenerations.keys()]) {
      this.nextGeneration(handle);
    }
    for (const target of [...this.commandTargetGenerations.keys()]) {
      this.nextTargetGeneration(target);
    }
    for (const source of [...this.commandSources.values()]) {
      this.stopKey(
        source.key,
        fadeMs,
        false,
        playOutros && source.kind === "ambience",
        outroMode,
      );
    }
  }

  private resolveSource(name: string): AVPlaybackSource | null {
    const assetId = soundManifest[name];
    return typeof assetId === "number" ? assetId : null;
  }

  private async resolveNativeSource(
    name: string,
  ): Promise<AVPlaybackSource | null> {
    const cached = this.nativeSourceCache.get(name);
    if (cached) {
      this.nativeSourceCache.delete(name);
      this.nativeSourceCache.set(name, cached);
      return cached;
    }
    const loading = this.nativeSourceLoading.get(name);
    if (loading) {
      return loading;
    }
    const loadPromise = (async () => {
      try {
        const direct = this.resolveSource(name);
        if (!direct) {
          return null;
        }
        if (typeof direct !== "number") {
          this.cacheNativeSource(name, direct);
          return direct;
        }
        const assets = await Asset.loadAsync(direct);
        const asset = assets[0] ?? Asset.fromModule(direct);
        const resolved: AVPlaybackSource = asset.localUri
          ? { uri: asset.localUri }
          : asset.uri
            ? { uri: asset.uri }
            : direct;
        this.cacheNativeSource(name, resolved);
        return resolved;
      } catch (error) {
        console.warn(`MobileAudioManager: failed to resolve ${name}.`, error);
        return this.resolveSource(name);
      } finally {
        this.nativeSourceLoading.delete(name);
      }
    })();
    this.nativeSourceLoading.set(name, loadPromise);
    return loadPromise;
  }

  private cacheNativeSource(name: string, source: AVPlaybackSource): void {
    this.nativeSourceCache.set(name, source);
    while (this.nativeSourceCache.size > MAX_CACHED_ASSET_URIS) {
      const oldest = this.nativeSourceCache.keys().next().value;
      if (oldest === undefined) {
        break;
      }
      this.nativeSourceCache.delete(oldest);
    }
  }

  private async ensureNativeAudioMode(): Promise<void> {
    if (Platform.OS === "web" || this.nativeAudioModeReady) {
      return;
    }
    if (this.nativeAudioModeLoading) {
      return this.nativeAudioModeLoading;
    }
    this.nativeAudioModeLoading = (
      Platform.OS === "android"
        ? this.ensureAndroidAudioMode()
        : Promise.all([
            ExpoAudio.setAudioModeAsync({
              allowsRecordingIOS: false,
              interruptionModeIOS: InterruptionModeIOS.MixWithOthers,
              playsInSilentModeIOS: true,
              staysActiveInBackground: true,
            }),
            setModernAudioModeAsync({
              allowsRecording: false,
              interruptionMode: "mixWithOthers",
              playsInSilentMode: true,
              shouldPlayInBackground: true,
              shouldRouteThroughEarpiece: false,
            }),
          ]).then(() => undefined)
    ).then(() => {
      this.nativeAudioModeReady = true;
    }).finally(() => {
      this.nativeAudioModeLoading = null;
    });
    return this.nativeAudioModeLoading;
  }

  private async ensureAndroidAudioMode(): Promise<void> {
    await Promise.all([
      exponentAV?.setAudioMode({
        interruptionModeAndroid: InterruptionModeAndroid.DuckOthers,
        shouldDuckAndroid: true,
        staysActiveInBackground: true,
      }) ?? Promise.resolve(),
      setModernAudioModeAsync({
        allowsRecording: false,
        interruptionMode: "duckOthers",
        playsInSilentMode: true,
        shouldPlayInBackground: true,
        shouldRouteThroughEarpiece: false,
      }),
    ]);
  }

  private async createNativeSound(
    source: AVPlaybackSource,
    status: AVPlaybackStatusToSet,
  ): Promise<ExpoAudio.Sound | null> {
    const sound = new ExpoAudio.Sound();
    try {
      await sound.loadAsync(source, status);
      this.nativeSoundVolumes.set(sound, status.volume ?? 1);
      return sound;
    } catch (error) {
      console.warn("MobileAudioManager: native audio load failed.", error);
      sound.setOnPlaybackStatusUpdate(null);
      void sound.unloadAsync().catch(() => undefined);
      return null;
    }
  }

  private disposeNativeSound(sound: ExpoAudio.Sound): void {
    this.nativeSoundVolumes.delete(sound);
    sound.setOnPlaybackStatusUpdate(null);
    void sound.unloadAsync().catch(() => undefined);
  }

  private setNativeSoundVolume(
    sound: ExpoAudio.Sound,
    volume: number,
  ): void {
    const bounded = this.clamp(volume, 0, 1, 0);
    this.nativeSoundVolumes.set(sound, bounded);
    void sound.setVolumeAsync(bounded).catch(() => undefined);
  }

  private async ensureWebAudioReady(): Promise<AudioContext | null> {
    if (typeof window === "undefined") {
      return null;
    }
    if (!this.webAudioContext) {
      const AudioContextClass = window.AudioContext
        || (window as typeof window & {
          webkitAudioContext?: typeof AudioContext;
        }).webkitAudioContext;
      if (!AudioContextClass) {
        return null;
      }
      this.webAudioContext = new AudioContextClass();
      this.webMasterGain = this.webAudioContext.createGain();
      this.webMusicBus = this.webAudioContext.createGain();
      this.webSfxBus = this.webAudioContext.createGain();
      this.webAmbienceBus = this.webAudioContext.createGain();
      this.webMasterGain.connect(this.webAudioContext.destination);
      this.webMusicBus.connect(this.webMasterGain);
      this.webSfxBus.connect(this.webMasterGain);
      this.webAmbienceBus.connect(this.webMasterGain);
      this.webMasterGain.gain.value = 1;
      this.webMusicBus.gain.value = this.musicVolume;
      this.webSfxBus.gain.value = this.soundVolume;
      this.webAmbienceBus.gain.value = this.ambienceVolume;
    }
    if (this.webAudioContext.state === "suspended") {
      await this.webAudioContext.resume().catch(() => undefined);
    }
    return this.webAudioContext;
  }

  private async resolveWebUri(name: string): Promise<string | null> {
    const cached = this.webUriCache.get(name);
    if (cached) {
      this.webUriCache.delete(name);
      this.webUriCache.set(name, cached);
      return cached;
    }
    const assetId = (soundManifest as Record<string, unknown>)[name];
    if (!assetId) {
      return null;
    }
    try {
      if (typeof assetId === "string") {
        this.cacheWebUri(name, assetId);
        return assetId;
      }
      if (typeof assetId === "object") {
        const candidate = assetId as {
          default?: string | { uri?: string };
          src?: string;
          uri?: string;
        };
        const uri = candidate.uri
          || candidate.src
          || (typeof candidate.default === "string"
            ? candidate.default
            : candidate.default?.uri)
          || null;
        if (uri) {
          this.cacheWebUri(name, uri);
        }
        return uri;
      }
      if (typeof assetId !== "number") {
        return null;
      }
      const assets = await Asset.loadAsync(assetId);
      const asset = assets[0] ?? Asset.fromModule(assetId);
      const uri = asset.localUri ?? asset.uri ?? null;
      if (uri) {
        this.cacheWebUri(name, uri);
      }
      return uri;
    } catch (error) {
      console.warn(`MobileAudioManager: failed to resolve web ${name}.`, error);
      return null;
    }
  }

  private cacheWebUri(name: string, uri: string): void {
    this.webUriCache.set(name, uri);
    while (this.webUriCache.size > MAX_CACHED_ASSET_URIS) {
      const oldest = this.webUriCache.keys().next().value;
      if (oldest === undefined) {
        break;
      }
      this.webUriCache.delete(oldest);
    }
  }

  private async loadWebBuffer(name: string): Promise<AudioBuffer | null> {
    const cached = this.webBufferCache.get(name);
    if (cached) {
      this.webBufferCache.delete(name);
      this.webBufferCache.set(name, cached);
      return cached;
    }
    const loading = this.webBufferLoading.get(name);
    if (loading) {
      return loading;
    }
    const loadPromise = (async () => {
      const context = await this.ensureWebAudioReady();
      const uri = await this.resolveWebUri(name);
      if (!context || !uri) {
        return null;
      }
      try {
        const response = await fetch(uri);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const decoded = await context.decodeAudioData(
          (await response.arrayBuffer()).slice(0),
        );
        this.webBufferCache.set(name, decoded);
        this.webBufferCacheBytes += (
          decoded.length * decoded.numberOfChannels * 4
        );
        while (
          this.webBufferCache.size > MAX_CACHED_EFFECTS
          || this.webBufferCacheBytes > MAX_CACHED_BUFFER_BYTES
        ) {
          const oldest = this.webBufferCache.keys().next().value;
          if (oldest === undefined) {
            break;
          }
          const oldestBuffer = this.webBufferCache.get(oldest);
          if (oldestBuffer) {
            this.webBufferCacheBytes -= (
              oldestBuffer.length * oldestBuffer.numberOfChannels * 4
            );
          }
          this.webBufferCache.delete(oldest);
        }
        return decoded;
      } catch (error) {
        console.warn(`MobileAudioManager: failed to load ${name}.`, error);
        return null;
      } finally {
        this.webBufferLoading.delete(name);
      }
    })();
    this.webBufferLoading.set(name, loadPromise);
    return loadPromise;
  }
}
