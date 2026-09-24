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

import { soundFamilies, soundManifest } from "../generated/soundManifest";
import type { AudioCommandPacket, AudioKind } from "../network/packets";
import { isTerminalNativePlaybackStatus } from "./playbackLifecycle";
import {
  audioGainAt,
  audioMotionProgress,
  audioMotionPosition,
  createWebAudioSpatializer,
  distanceAttenuationGain,
  normalizeAudioGain,
  normalizeAudioGainAutomation,
  normalizeAudioMotion,
  normalizeAudioPosition,
  normalizeAudioSequenceSegments,
  normalizeDistanceAttenuation,
  panFromPosition,
  setAudioSpatializerPosition,
} from "./spatialAudio";
import type {
  AudioGainAutomation,
  AudioMotion,
  AudioPosition,
  AudioSequenceSegment,
  DistanceAttenuation,
} from "./spatialAudio";
import {
  NativeSpatialAudio,
  playbackSourceFilePath,
} from "./nativeSpatialAudio";

type CommandAudioSource = {
  active: boolean;
  asset: string;
  baseVolume: number;
  bus: string;
  createdAt: number;
  attenuation: DistanceAttenuation | undefined;
  distanceGain: number;
  sourceGain: number;
  ducking: Map<string, number>;
  envelope: number;
  fadeToken: number;
  generation: number;
  handle: string;
  key: string;
  kind: AudioKind;
  nativePlayer: ExpoAudio.Sound | null;
  nativeSpatialId: string | null;
  nativeSpatialCompletionTimer: ReturnType<typeof setTimeout> | null;
  nativeSpatialSequence: boolean;
  nativeSpatialStem: boolean;
  nativeSpatialBlend: number;
  nativeStem: NativeStemState | null;
  nativeSequence: NativeSequenceState | null;
  onEnded: (() => void) | null;
  outro: string;
  paused: boolean;
  pitch: number;
  priority: number;
  position: AudioPosition | undefined;
  pan: number;
  sequenceTimer: ReturnType<typeof setInterval> | null;
  sequenceStartTimer: ReturnType<typeof setTimeout> | null;
  target: string;
  webGain: GainNode | null;
  webNode: AudioBufferSourceNode | MediaElementAudioSourceNode | null;
  webNodes: Set<AudioBufferSourceNode>;
  webStem: WebStemState | null;
  webElement: HTMLAudioElement | null;
  webPanner: AudioNode | null;
  webSequenceTracks: WebSequenceTrack[];
  webTailAnalyser: AnalyserNode | null;
  webTailTimer: ReturnType<typeof setTimeout> | null;
};

type WebSequenceTrack = {
  durationMilliseconds: number;
  node: AudioBufferSourceNode;
  output: GainNode;
  panner: AudioNode | null;
  segment: AudioSequenceSegment;
  startsAtMilliseconds: number;
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
  outroNode: AudioBufferSourceNode | null;
  outroScheduled: boolean;
  outroStartsAt: number;
};

type NativeSequenceState = {
  startTimers: Set<ReturnType<typeof setTimeout>>;
  tracks: NativeSequenceTrack[];
};

type NativeSpatialSequenceTrack = {
  durationMilliseconds: number;
  finalParametersApplied: boolean;
  segment: AudioSequenceSegment;
  startsAtMilliseconds: number;
};

type NativeSequenceTrack = {
  durationMilliseconds: number;
  ended: boolean;
  player: ExpoAudio.Sound;
  segment: AudioSequenceSegment;
  startsAtMilliseconds: number;
};

type SourceMotionRuntime = {
  generation: number;
  handle: string;
  kind: AudioKind;
  motion: AudioMotion;
  startedAt: number;
  timer: ReturnType<typeof setInterval> | null;
};

type SourceGainRuntime = {
  automation: AudioGainAutomation;
  generation: number;
  handle: string;
  kind: AudioKind;
  startedAt: number;
  timer: ReturnType<typeof setInterval> | null;
};

type SourceLoadReservation = Readonly<{
  asset: string;
  kind: AudioKind;
  slot: string;
}>;

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
  | "gain"
  | "handle"
  | "layer"
  | "loop"
  | "pitch"
  | "position"
  | "attenuation"
  | "priority"
  | "scope"
  | "volume"
>;

type ExponentAVModule = {
  setAudioMode(mode: AndroidNativeAudioMode): Promise<void>;
};

const AUDIO_PROTOCOL_VERSION = 3;
const AUDIO_OUTPUT_BUFFERS = new Set(["chat", "private", "game", "system", "misc"]);
const MAX_ACTIVE_EFFECTS = 64;
const MAX_ACTIVE_LAYERS = 32;
const MAX_CACHED_EFFECTS = 128;
const MAX_CACHED_BUFFER_BYTES = 96 * 1024 * 1024;
const MAX_CACHED_ASSET_URIS = 512;
const MAX_GENERATION_ENTRIES = 512;
const MAX_FADE_MS = 60_000;
const SOURCE_AUTOMATION_INTERVAL_MS = 1000 / 60;
const WEB_AUDIO_TAIL_FFT_SIZE = 256;
const WEB_AUDIO_TAIL_POLL_MS = 16;
const WEB_AUDIO_TAIL_SILENCE_POLLS = 2;
const WEB_AUDIO_TAIL_TIMEOUT_MS = 2000;
const FINITE_SFX_LAUNCH_TIMEOUT_MS = 5000;
const NATIVE_SPATIAL_COMPLETION_GRACE_MS = WEB_AUDIO_TAIL_TIMEOUT_MS;

function isHrtfPanner(node: AudioNode | null | undefined): boolean {
  return Boolean(
    node
    && "panningModel" in node
    && (node as PannerNode).panningModel === "HRTF"
  );
}

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
  private nativeSpatialAudio = new NativeSpatialAudio();
  private nativeSpatialIdsInUse = new Set<string>();
  private nativeSpatialSources = new Map<string, string>();
  private nativeSpatialPollingTimer: ReturnType<typeof setInterval> | null = null;
  private nativeSpatialSequence = 0;

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
  private commandMotions = new Map<string, SourceMotionRuntime>();
  private commandGainAutomations = new Map<string, SourceGainRuntime>();
  private sourceLoadReservations = new Set<SourceLoadReservation>();
  private commandPausedMusicHandles = new Set<string>();
  private commandBusGains = new Map<string, number>();
  private commandBusFadeTokens = new Map<string, number>();
  private commandDucking = new Map<string, Map<string, number>>();
  private finiteSfxLaunchQueue: Promise<void> = Promise.resolve();
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
    this.sourceLoadReservations.clear();
    this.stopNativeSpatialCompletionPolling();
    this.nativeSpatialAudio.shutdown();
    this.nativeSpatialIdsInUse.clear();
    this.nativeSpatialSources.clear();
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
      && source.distanceGain > 0
      && source.sourceGain > 0
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
      if (source.nativeSequence && !source.paused) {
        const now = this.audioClockMs();
        for (const track of source.nativeSequence.tracks) {
          if (!track.ended && now >= track.startsAtMilliseconds) {
            void track.player.playAsync().catch(() => undefined);
          }
        }
      }
      if (source.nativeSpatialId && !source.paused) {
        this.nativeSpatialAudio.resumeSource(source.nativeSpatialId);
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

  async playSoundFamily(
    family: string,
    options: { volume?: number; pitch?: number; pan?: number } = {},
  ): Promise<boolean> {
    return this.handleAudioCommand({
      type: "audio",
      version: AUDIO_PROTOCOL_VERSION,
      command: "play",
      kind: "sfx",
      family,
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
    const position = normalizeAudioPosition(packet.position);
    const attenuation = normalizeDistanceAttenuation(packet.attenuation);
    const motion = normalizeAudioMotion(packet.motion);
    const gain = packet.gain === undefined ? 1 : normalizeAudioGain(packet.gain);
    const gainAutomation = normalizeAudioGainAutomation(packet.gain_automation);
    const sequenceSegments = normalizeAudioSequenceSegments(packet.segments);
    if (
      position === null
      || attenuation === null
      || motion === null
      || gain === null
      || gainAutomation === null
      || sequenceSegments === null
      || (position !== undefined && packet.command !== "play")
      || (attenuation !== undefined && packet.command !== "play")
      || (attenuation !== undefined && position === undefined)
      || (motion !== undefined && packet.command !== "update")
      || (Object.prototype.hasOwnProperty.call(packet, "gain") && packet.command !== "play")
      || (gainAutomation !== undefined && packet.command !== "update")
      || (sequenceSegments !== undefined && packet.command !== "play")
    ) {
      return false;
    }
    packet = {
      ...packet,
      position: position ? [...position] : undefined,
      attenuation,
      motion,
      gain,
      gain_automation: gainAutomation,
      segments: sequenceSegments?.map((segment) => ({
        asset: segment.asset,
        position: segment.position
          ? [segment.position[0], segment.position[1], segment.position[2]]
          : null,
        destination_position: segment.destination_position
          ? [
              segment.destination_position[0],
              segment.destination_position[1],
              segment.destination_position[2],
            ]
          : null,
        attenuation: segment.attenuation ?? null,
        gain: segment.gain,
        easing: segment.easing,
        next_start_ratio: segment.next_start_ratio,
      })),
      pan: position
        ? packet.pan ?? Math.round(panFromPosition(position) * 100)
        : packet.pan,
    };
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
          !packet.kind
          || !["sfx", "music", "ambience"].includes(packet.kind)
          || !packet.handle
          || (motion === undefined && gainAutomation === undefined)
        ) {
          return false;
        }
        return (
          (motion === undefined
            || this.startSourceMotion(packet.kind, packet.handle, motion))
          && (gainAutomation === undefined
            || this.startSourceGainAutomation(
              packet.kind,
              packet.handle,
              gainAutomation,
            ))
        );
      case "play":
        if (!packet.kind || !["sfx", "music", "ambience"].includes(packet.kind)) {
          return false;
        }
        if (packet.kind === "sfx") {
          // Family selection is explicit. A numbered asset remains an exact
          // path and never enters the randomized family lookup below.
          const hasAsset = Boolean(packet.asset);
          const hasFamily = Boolean(packet.family);
          const hasSequence = Boolean(packet.segments?.length);
          if ([hasAsset, hasFamily, hasSequence].filter(Boolean).length !== 1) {
            return false;
          }
          const asset = hasAsset ? this.normalizeAsset(packet.asset || "") : "";
          const family = hasFamily ? this.normalizeFamily(packet.family || "") : "";
          if (
            hasAsset && !asset
            || hasFamily && (!family || packet.loop)
            || hasSequence && (
              !packet.handle
              || Boolean(packet.loop)
              || Boolean(packet.intro)
              || Boolean(packet.outro)
              || packet.position !== undefined
              || packet.attenuation !== undefined
              || packet.gain !== 1
            )
          ) {
            return false;
          }
          if (hasSequence) {
            return this.queueFiniteSfx(packet, true);
          }
          const resolvedAsset = asset || this.chooseSoundFamilyVariant(family);
          if (!resolvedAsset) {
            return false;
          }
          return this.queueFiniteSfx({
            ...packet,
            asset: resolvedAsset,
            family: undefined,
          }, false);
        }
        if (packet.family || !this.normalizeAsset(packet.asset || "")) {
          return false;
        }
        return this.playManagedLayer(packet);
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

  private normalizeFamily(name: string): string {
    const normalized = String(name || "").trim().replaceAll("\\", "/");
    if (!normalized || normalized.split("/").at(-1)?.includes(".")) {
      return "";
    }
    return this.normalizeAsset(`${normalized}1.ogg`) ? normalized : "";
  }

  private soundFamilyVariants(name: string): readonly string[] {
    const family = this.normalizeFamily(name);
    if (!family || !Object.prototype.hasOwnProperty.call(soundFamilies, family)) {
      return [];
    }
    return soundFamilies[family] ?? [];
  }

  private chooseSoundFamilyVariant(name: string): string {
    const variants = this.soundFamilyVariants(name);
    return variants.length
      ? variants[Math.floor(Math.random() * variants.length)]
      : "";
  }

  private validId(value: string): boolean {
    return /^[A-Za-z0-9_.:-]{1,128}$/.test(value);
  }

  private target(packet: AudioCommandPacket): string {
    return `${packet.kind ?? ""}:${packet.scope ?? "global"}:${packet.context ?? ""}:${packet.layer ?? "main"}`;
  }

  private nextGeneration(handle: string): number {
    this.clearSourceMotion(handle);
    this.clearSourceGainAutomation(handle);
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
      this.clearSourceMotion(removable);
      this.clearSourceGainAutomation(removable);
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

  private sourceSpatialFields(packet: AudioCommandPacket): Pick<
    CommandAudioSource,
    "attenuation" | "distanceGain" | "position"
  > {
    const position = normalizeAudioPosition(packet.position);
    const attenuation = normalizeDistanceAttenuation(packet.attenuation);
    if (
      position === null
      || attenuation === null
      || (attenuation !== undefined && position === undefined)
    ) {
      throw new TypeError("Invalid spatial audio packet");
    }
    return {
      position,
      attenuation,
      distanceGain: distanceAttenuationGain(position, attenuation),
    };
  }

  private buildSource(
    packet: AudioCommandPacket,
    asset: string,
    handle: string,
    generation: number,
    target: string,
    key: string,
    kind: AudioKind,
    outro = this.normalizeAsset(packet.outro || ""),
  ): CommandAudioSource {
    return {
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
      nativeSpatialId: null,
      nativeSpatialCompletionTimer: null,
      nativeSpatialSequence: false,
      nativeSpatialStem: false,
      nativeSpatialBlend: 1,
      nativeStem: null,
      nativeSequence: null,
      onEnded: null,
      outro,
      paused: false,
      pitch: this.clamp(packet.pitch, 25, 400, 100) / 100,
      priority: this.clamp(packet.priority, -100, 100, 0),
      ...this.sourceSpatialFields(packet),
      sourceGain: packet.gain ?? 1,
      pan: this.clamp(packet.pan, -100, 100, 0),
      sequenceTimer: null,
      sequenceStartTimer: null,
      target,
      webGain: null,
      webNode: null,
      webNodes: new Set(),
      webStem: null,
      webElement: null,
      webPanner: null,
      webSequenceTracks: [],
      webTailAnalyser: null,
      webTailTimer: null,
    };
  }

  private sourceMixGain(source: CommandAudioSource): number {
    const mix = source.baseVolume
      * (this.commandBusGains.get(source.bus) ?? 1)
      * this.duckGain(source.bus)
      * source.envelope;
    return Platform.OS === "web" ? mix : mix * this.masterGain(source.kind);
  }

  private outputGain(source: CommandAudioSource): number {
    return this.sourceMixGain(source) * source.distanceGain * source.sourceGain;
  }

  private synchronizePendingAutomation(source: CommandAudioSource): void {
    const motion = this.commandMotions.get(source.handle);
    if (
      motion
      && motion.generation === source.generation
      && motion.kind === source.kind
    ) {
      const elapsed = Math.min(
        motion.motion.duration_ms,
        Math.max(0, this.audioClockMs() - motion.startedAt),
      );
      source.position = audioMotionPosition(motion.motion, elapsed);
      source.pan = Math.round(panFromPosition(source.position) * 100);
      source.distanceGain = distanceAttenuationGain(
        source.position,
        source.attenuation,
      );
    }
    const gainAutomation = this.commandGainAutomations.get(source.handle);
    if (
      gainAutomation
      && gainAutomation.generation === source.generation
      && gainAutomation.kind === source.kind
    ) {
      const elapsed = Math.min(
        gainAutomation.automation.duration_ms,
        Math.max(0, this.audioClockMs() - gainAutomation.startedAt),
      );
      source.sourceGain = audioGainAt(gainAutomation.automation, elapsed);
    }
  }

  private audioClockMs(): number {
    if (Platform.OS === "web" && this.webAudioContext) {
      return this.webAudioContext.currentTime * 1000;
    }
    return globalThis.performance?.now?.() ?? Date.now();
  }

  private clearSourceMotion(handle: string): void {
    const runtime = this.commandMotions.get(handle);
    if (runtime?.timer) {
      clearInterval(runtime.timer);
    }
    this.commandMotions.delete(handle);
  }

  private applySourceMotion(runtime: SourceMotionRuntime): boolean {
    if (
      this.commandMotions.get(runtime.handle) !== runtime
      || this.commandGenerations.get(runtime.handle) !== runtime.generation
    ) {
      return true;
    }
    const elapsed = Math.min(
      runtime.motion.duration_ms,
      Math.max(0, this.audioClockMs() - runtime.startedAt),
    );
    const sourceKey = this.commandHandles.get(runtime.handle);
    const source = sourceKey ? this.commandSources.get(sourceKey) : undefined;
    if (source) {
      if (source.kind !== runtime.kind || source.generation !== runtime.generation) {
        this.clearSourceMotion(runtime.handle);
        return true;
      }
      const position = audioMotionPosition(runtime.motion, elapsed);
      source.position = position;
      source.pan = Math.round(panFromPosition(position) * 100);
      if (source.webPanner && this.webAudioContext) {
        setAudioSpatializerPosition(
          source.webPanner,
          this.webAudioContext,
          position,
        );
      }
      source.distanceGain = distanceAttenuationGain(
        position,
        source.attenuation,
      );
      this.setAbsoluteVolume(source, this.outputGain(source));
    }
    if (elapsed >= runtime.motion.duration_ms) {
      if (source) {
        this.clearSourceMotion(runtime.handle);
      } else if (runtime.timer) {
        // The update can finish while a cold asset is still loading. Stop the
        // polling timer but retain the destination for register() to consume.
        clearInterval(runtime.timer);
        runtime.timer = null;
      }
      return true;
    }
    return false;
  }

  private startSourceMotion(
    kind: AudioKind,
    handle: string,
    motion: AudioMotion,
  ): boolean {
    const generation = this.commandGenerations.get(handle);
    const sourceKey = this.commandHandles.get(handle);
    const source = sourceKey ? this.commandSources.get(sourceKey) : undefined;
    if (source && source.kind !== kind) {
      return false;
    }
    if (generation === undefined) {
      return true;
    }
    this.clearSourceMotion(handle);
    const runtime: SourceMotionRuntime = {
      generation,
      handle,
      kind,
      motion,
      startedAt: this.audioClockMs() - motion.elapsed_ms,
      timer: null,
    };
    this.commandMotions.set(handle, runtime);
    const complete = this.applySourceMotion(runtime);
    if (!complete && this.commandMotions.get(handle) === runtime) {
      runtime.timer = setInterval(() => {
        this.applySourceMotion(runtime);
      }, SOURCE_AUTOMATION_INTERVAL_MS);
    }
    return true;
  }

  private clearSourceGainAutomation(handle: string): void {
    const runtime = this.commandGainAutomations.get(handle);
    if (runtime?.timer) {
      clearInterval(runtime.timer);
    }
    this.commandGainAutomations.delete(handle);
  }

  private applySourceGainAutomation(runtime: SourceGainRuntime): boolean {
    if (
      this.commandGainAutomations.get(runtime.handle) !== runtime
      || this.commandGenerations.get(runtime.handle) !== runtime.generation
    ) {
      return true;
    }
    const elapsed = Math.min(
      runtime.automation.duration_ms,
      Math.max(0, this.audioClockMs() - runtime.startedAt),
    );
    const sourceKey = this.commandHandles.get(runtime.handle);
    const source = sourceKey ? this.commandSources.get(sourceKey) : undefined;
    if (source) {
      if (source.kind !== runtime.kind || source.generation !== runtime.generation) {
        this.clearSourceGainAutomation(runtime.handle);
        return true;
      }
      source.sourceGain = audioGainAt(runtime.automation, elapsed);
      this.setAbsoluteVolume(source, this.outputGain(source));
    }
    if (elapsed >= runtime.automation.duration_ms) {
      if (source) {
        this.clearSourceGainAutomation(runtime.handle);
      } else if (runtime.timer) {
        // Preserve the completed value across asynchronous source creation,
        // while avoiding an idle interval for a value that can no longer move.
        clearInterval(runtime.timer);
        runtime.timer = null;
      }
      return true;
    }
    return false;
  }

  private startSourceGainAutomation(
    kind: AudioKind,
    handle: string,
    automation: AudioGainAutomation,
  ): boolean {
    const generation = this.commandGenerations.get(handle);
    const sourceKey = this.commandHandles.get(handle);
    const source = sourceKey ? this.commandSources.get(sourceKey) : undefined;
    if (source && source.kind !== kind) {
      return false;
    }
    if (generation === undefined) {
      return true;
    }
    this.clearSourceGainAutomation(handle);
    const runtime: SourceGainRuntime = {
      generation,
      handle,
      kind,
      automation,
      startedAt: this.audioClockMs() - automation.elapsed_ms,
      timer: null,
    };
    this.commandGainAutomations.set(handle, runtime);
    const complete = this.applySourceGainAutomation(runtime);
    if (!complete && this.commandGainAutomations.get(handle) === runtime) {
      runtime.timer = setInterval(() => {
        this.applySourceGainAutomation(runtime);
      }, SOURCE_AUTOMATION_INTERVAL_MS);
    }
    return true;
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
    if (source.nativeSpatialId) {
      this.nativeSpatialAudio.setParameters(
        source.nativeSpatialId,
        source.nativeSpatialSequence
          ? this.clamp(this.sourceMixGain(source), 0, 1, 0)
          : bounded,
        source.pitch,
        source.position ?? [0, 0, 0],
        source.nativeSpatialBlend,
      );
    }
    if (source.nativePlayer) {
      this.setNativeSoundVolume(
        source.nativePlayer,
        bounded,
        Platform.OS === "android" && source.kind === "sfx"
          ? source.pan / 100
          : undefined,
      );
    }
    if (source.nativeStem) {
      source.nativeStem.playlist.volume = bounded;
    }
    if (source.nativeSequence) {
      const now = this.audioClockMs();
      for (const track of source.nativeSequence.tracks) {
        const elapsed = now - track.startsAtMilliseconds;
        const active = !track.ended && elapsed >= 0;
        const position = this.sequencePosition(
          track.segment,
          Math.min(track.durationMilliseconds, Math.max(0, elapsed)),
          track.durationMilliseconds,
        );
        const trackVolume = active
          ? this.sourceMixGain(source)
            * track.segment.gain
            * distanceAttenuationGain(position, track.segment.attenuation)
          : 0;
        this.setNativeSoundVolume(
          track.player,
          trackVolume,
          Platform.OS === "android"
            ? position !== undefined
              ? panFromPosition(position)
              : source.pan / 100
            : undefined,
        );
      }
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
    if (source.nativeSpatialId) {
      this.nativeSpatialSources.set(source.nativeSpatialId, source.key);
      this.ensureNativeSpatialCompletionPolling();
    }
    const motion = this.commandMotions.get(source.handle);
    if (motion) {
      this.applySourceMotion(motion);
    }
    const gainAutomation = this.commandGainAutomations.get(source.handle);
    if (gainAutomation) {
      this.applySourceGainAutomation(gainAutomation);
    }
    this.stateListener?.();
  }

  private nextNativeSpatialId(): string {
    for (let attempts = 0; attempts <= this.nativeSpatialIdsInUse.size; attempts += 1) {
      this.nativeSpatialSequence += 1;
      if (!Number.isSafeInteger(this.nativeSpatialSequence)) {
        this.nativeSpatialSequence = 1;
      }
      const sourceId = `source:${this.nativeSpatialSequence}`;
      if (!this.nativeSpatialIdsInUse.has(sourceId)) {
        this.nativeSpatialIdsInUse.add(sourceId);
        return sourceId;
      }
    }
    throw new Error("Native spatial-audio source identifier space is exhausted");
  }

  private releaseNativeSpatialId(sourceId: string): void {
    this.nativeSpatialIdsInUse.delete(sourceId);
  }

  private ensureNativeSpatialCompletionPolling(): void {
    if (this.nativeSpatialPollingTimer) {
      return;
    }
    this.nativeSpatialPollingTimer = setInterval(() => {
      for (const sourceId of this.nativeSpatialAudio.drainEndedSources()) {
        const key = this.nativeSpatialSources.get(sourceId);
        const source = key ? this.commandSources.get(key) : undefined;
        if (!key || !source || source.nativeSpatialId !== sourceId) {
          this.nativeSpatialSources.delete(sourceId);
          this.releaseNativeSpatialId(sourceId);
          continue;
        }
        const onEnded = source.onEnded;
        this.dispose(key);
        onEnded?.();
      }
      if (!this.nativeSpatialSources.size) {
        this.stopNativeSpatialCompletionPolling();
      }
    }, this.nativeSpatialAudio.config.endedPollIntervalMilliseconds);
  }

  private stopNativeSpatialCompletionPolling(): void {
    if (this.nativeSpatialPollingTimer) {
      clearInterval(this.nativeSpatialPollingTimer);
      this.nativeSpatialPollingTimer = null;
    }
  }

  private dispose(key: string): void {
    const source = this.commandSources.get(key);
    if (!source) {
      return;
    }
    source.active = false;
    if (source.sequenceTimer) {
      clearInterval(source.sequenceTimer);
      source.sequenceTimer = null;
    }
    if (source.sequenceStartTimer) {
      clearTimeout(source.sequenceStartTimer);
      source.sequenceStartTimer = null;
    }
    if (source.webTailTimer) {
      clearTimeout(source.webTailTimer);
      source.webTailTimer = null;
    }
    this.commandSources.delete(key);
    this.commandDucking.delete(key);
    if (this.commandHandles.get(source.handle) === key) {
      this.clearSourceMotion(source.handle);
      this.clearSourceGainAutomation(source.handle);
      this.commandHandles.delete(source.handle);
    }
    if (source.target && this.commandTargets.get(source.target) === key) {
      this.commandTargets.delete(source.target);
    }
    if (source.nativePlayer) {
      this.disposeNativeSound(source.nativePlayer);
    }
    if (source.nativeSpatialId) {
      if (source.nativeSpatialCompletionTimer) {
        clearTimeout(source.nativeSpatialCompletionTimer);
        source.nativeSpatialCompletionTimer = null;
      }
      if (this.nativeSpatialSources.get(source.nativeSpatialId) === key) {
        this.nativeSpatialSources.delete(source.nativeSpatialId);
      }
      this.nativeSpatialAudio.destroySource(source.nativeSpatialId);
      this.releaseNativeSpatialId(source.nativeSpatialId);
      source.nativeSpatialId = null;
      source.nativeSpatialSequence = false;
      if (!this.nativeSpatialSources.size) {
        this.stopNativeSpatialCompletionPolling();
      }
    }
    if (source.nativeStem) {
      source.nativeStem.statusSubscription.remove();
      source.nativeStem.trackSubscription.remove();
      source.nativeStem.playlist.destroy();
      source.nativeStem = null;
    }
    if (source.nativeSequence) {
      for (const timer of source.nativeSequence.startTimers) {
        clearTimeout(timer);
      }
      for (const track of source.nativeSequence.tracks) {
        this.disposeNativeSound(track.player);
      }
      source.nativeSequence = null;
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
      source.webTailAnalyser?.disconnect();
    } catch {
      // Ignore double-disconnect races.
    }
    for (const track of source.webSequenceTracks) {
      try {
        track.panner?.disconnect();
      } catch {
        // Ignore already-disconnected sequence panners.
      }
      try {
        track.output.disconnect();
      } catch {
        // Ignore already-disconnected sequence gain nodes.
      }
    }
    source.webSequenceTracks = [];
    try {
      source.webGain?.disconnect();
    } catch {
      // Ignore double-disconnect races.
    }
    this.refreshMix();
    this.stateListener?.();
  }

  private disposeWebSourceAfterTail(source: CommandAudioSource): void {
    if (!source.active) {
      return;
    }
    if (source.sequenceTimer) {
      clearInterval(source.sequenceTimer);
      source.sequenceTimer = null;
    }
    const analyser = source.webTailAnalyser;
    if (!analyser) {
      this.dispose(source.key);
      return;
    }
    const samples = new Float32Array(analyser.fftSize);
    const startedAt = this.audioClockMs();
    let silentPolls = 0;
    const poll = () => {
      source.webTailTimer = null;
      if (!source.active) {
        return;
      }
      try {
        analyser.getFloatTimeDomainData(samples);
      } catch {
        this.dispose(source.key);
        return;
      }
      silentPolls = samples.every((sample) => sample === 0)
        ? silentPolls + 1
        : 0;
      if (
        silentPolls >= WEB_AUDIO_TAIL_SILENCE_POLLS
        || this.audioClockMs() - startedAt >= WEB_AUDIO_TAIL_TIMEOUT_MS
      ) {
        this.dispose(source.key);
        return;
      }
      source.webTailTimer = setTimeout(poll, WEB_AUDIO_TAIL_POLL_MS);
    };
    source.webTailTimer = setTimeout(poll, WEB_AUDIO_TAIL_POLL_MS);
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
    const seamlessStem = Boolean(
      source.nativeSpatialStem || source.nativeStem || source.webStem,
    );
    if (
      playOutro
      && source.outro
      && seamlessStem
      && (
        this.scheduleNativeSpatialStemOutro(source, outroMode)
        ||
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
        if (source.nativeSpatialId) {
          this.nativeSpatialAudio.pauseSource(source.nativeSpatialId);
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
            pitch: source.pitch * 100,
            position: source.position ? [...source.position] : undefined,
            attenuation: source.attenuation,
            gain: source.sourceGain,
            pan: source.pan,
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
    this.clearSourceMotion(source.handle);
    this.clearSourceGainAutomation(source.handle);
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

  private scheduleNativeSpatialStemOutro(
    source: CommandAudioSource,
    mode: "immediate" | "boundary",
  ): boolean {
    if (
      !source.nativeSpatialStem
      || !source.nativeSpatialId
      || !source.outro
      || !this.nativeSpatialAudio.requestOutro(
        source.nativeSpatialId,
        mode === "boundary",
      )
    ) {
      return false;
    }
    source.asset = source.outro;
    source.outro = "";
    this.detachSourceHandle(source);
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
      || stem.loopDuration <= 0
    ) {
      return false;
    }
    if (stem.outroScheduled) {
      if (mode === "boundary" || context.currentTime >= stem.outroStartsAt) {
        source.asset = source.outro;
        source.outro = "";
        this.detachSourceHandle(source);
        return true;
      }
      const scheduledNode = stem.outroNode;
      stem.outroNode = null;
      stem.outroScheduled = false;
      stem.outroStartsAt = 0;
      if (scheduledNode) {
        try { scheduledNode.stop(); } catch { /* Already stopped. */ }
        try { scheduledNode.disconnect(); } catch { /* Already disconnected. */ }
        source.webNodes.delete(scheduledNode);
      }
    }
    const elapsed = Math.max(0, context.currentTime - stem.loopStartedAt);
    const cycles = Math.floor(elapsed / stem.loopDuration) + 1;
    const boundary = mode === "boundary"
      ? stem.loopStartedAt + (Math.max(1, cycles) * stem.loopDuration)
      : context.currentTime + 0.02;
    return this.scheduleWebStemOutroAt(source, boundary, true);
  }

  private scheduleWebStemOutroAt(
    source: CommandAudioSource,
    boundary: number,
    detachHandle: boolean,
  ): boolean {
    const context = this.webAudioContext;
    const stem = source.webStem;
    if (
      !context
      || !source.webGain
      || !stem?.outroBuffer
      || stem.outroScheduled
      || !Number.isFinite(boundary)
      || boundary < context.currentTime
    ) {
      return false;
    }
    const outroNode = context.createBufferSource();
    outroNode.buffer = stem.outroBuffer;
    outroNode.playbackRate.value = source.pitch;
    outroNode.connect(source.webPanner ?? source.webGain);
    try {
      stem.loopNode.stop(boundary);
      outroNode.start(boundary);
    } catch {
      outroNode.disconnect();
      return false;
    }
    source.webNodes.add(outroNode);
    stem.outroScheduled = true;
    stem.outroNode = outroNode;
    stem.outroStartsAt = boundary;
    if (detachHandle) {
      source.asset = source.outro;
      source.outro = "";
      this.detachSourceHandle(source);
    }
    outroNode.addEventListener("ended", () => {
      if (source.webStem?.outroNode === outroNode) {
        this.dispose(source.key);
      }
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

  private async resolveNativeFilePath(name: string): Promise<string | null> {
    return playbackSourceFilePath(await this.resolveNativeSource(name));
  }

  private async attachNativeSpatialSource(
    source: CommandAudioSource,
    looping: boolean,
    isCurrent: () => boolean,
  ): Promise<boolean> {
    const position = source.position;
    if (!position) {
      return false;
    }
    const loopPath = await this.resolveNativeFilePath(source.asset);
    if (!loopPath || !isCurrent()) {
      return false;
    }
    if (source.kind === "music") {
      source.paused = this.commandPausedMusicHandles.has(source.handle);
    }
    this.synchronizePendingAutomation(source);
    const initialPosition = source.position ?? position;
    const sourceId = this.nextNativeSpatialId();
    const created = await this.nativeSpatialAudio.createSource(sourceId, {
      loopPath,
      looping,
      playIntro: false,
      streamFromDisk: source.kind !== "sfx",
      startPaused: true,
      volume: this.outputGain(source),
      pitch: source.pitch,
      position: initialPosition,
    });
    if (!created || !isCurrent()) {
      if (created) {
        this.nativeSpatialAudio.destroySource(sourceId);
      }
      this.releaseNativeSpatialId(sourceId);
      return false;
    }
    if (source.kind === "music") {
      source.paused = this.commandPausedMusicHandles.has(source.handle);
    }
    this.synchronizePendingAutomation(source);
    source.nativeSpatialId = sourceId;
    const currentPosition = source.position ?? initialPosition;
    if (
      !this.nativeSpatialAudio.setParameters(
        sourceId,
        this.outputGain(source),
        source.pitch,
        currentPosition,
      )
      || (!source.paused && !this.nativeSpatialAudio.resumeSource(sourceId))
    ) {
      this.nativeSpatialAudio.destroySource(sourceId);
      this.releaseNativeSpatialId(sourceId);
      source.nativeSpatialId = null;
      return false;
    }
    return true;
  }

  private async createNativeSpatialStemSource(
    packet: AudioCommandPacket,
    handle: string,
    generation: number,
    target: string,
    targetGeneration: number,
  ): Promise<CommandAudioSource | null> {
    if (!normalizeAudioPosition(packet.position)) {
      return null;
    }
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
    const [introPath, loopPath, outroPath] = await Promise.all([
      intro ? this.resolveNativeFilePath(intro) : Promise.resolve(null),
      this.resolveNativeFilePath(loop),
      outro ? this.resolveNativeFilePath(outro) : Promise.resolve(null),
    ]);
    if (
      !loopPath
      || (intro && !introPath)
      || (outro && !outroPath)
      || !isCurrent()
    ) {
      return null;
    }
    const key = `${handle}:${Date.now()}:${Math.random()}`;
    const source = this.buildSource(
      packet,
      loop,
      handle,
      generation,
      target,
      key,
      "ambience",
      outro,
    );
    const position = source.position;
    if (!position) {
      return null;
    }
    this.synchronizePendingAutomation(source);
    const initialPosition = source.position ?? position;
    const sourceId = this.nextNativeSpatialId();
    const created = await this.nativeSpatialAudio.createSource(sourceId, {
      introPath: introPath ?? undefined,
      loopPath,
      outroPath: outroPath ?? undefined,
      playIntro: Boolean(introPath),
      looping: packet.loop !== false,
      streamFromDisk: true,
      startPaused: true,
      volume: this.outputGain(source),
      pitch: source.pitch,
      position: initialPosition,
    });
    if (!created || !isCurrent()) {
      if (created) {
        this.nativeSpatialAudio.destroySource(sourceId);
      }
      this.releaseNativeSpatialId(sourceId);
      return null;
    }
    this.synchronizePendingAutomation(source);
    source.nativeSpatialId = sourceId;
    source.nativeSpatialStem = true;
    if (
      !this.nativeSpatialAudio.setParameters(
        sourceId,
        this.outputGain(source),
        source.pitch,
        source.position ?? initialPosition,
      )
      || !this.nativeSpatialAudio.resumeSource(sourceId)
    ) {
      this.nativeSpatialAudio.destroySource(sourceId);
      this.releaseNativeSpatialId(sourceId);
      source.nativeSpatialId = null;
      return null;
    }
    this.register(source);
    if (packet.fade_in_ms) {
      this.fade(source, 1, packet.fade_in_ms);
    }
    return source;
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
    const source = this.buildSource(
      packet,
      loop,
      handle,
      generation,
      target,
      key,
      kind,
      outro,
    );
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
    playlist.playbackRate = source.pitch;
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
    const panner = createWebAudioSpatializer(context, {
      position: normalizeAudioPosition(packet.position) ?? undefined,
      pan: this.clamp(packet.pan, -100, 100, 0) / 100,
    });
    panner?.connect(gain);
    gain.connect(bus);
    const introNode = introBuffer ? context.createBufferSource() : null;
    const loopNode = context.createBufferSource();
    const pitch = this.clamp(packet.pitch, 25, 400, 100) / 100;
    const startAt = context.currentTime + 0.03;
    const loopStartedAt = startAt + ((introBuffer?.duration || 0) / pitch);
    const loopDuration = loopBuffer.duration / pitch;
    if (introNode) {
      introNode.buffer = introBuffer;
      introNode.playbackRate.value = pitch;
      introNode.connect(panner ?? gain);
    }
    loopNode.buffer = loopBuffer;
    loopNode.loop = packet.loop !== false;
    loopNode.playbackRate.value = pitch;
    loopNode.connect(panner ?? gain);
    const key = `${handle}:${Date.now()}:${Math.random()}`;
    const webNodes = new Set<AudioBufferSourceNode>([loopNode]);
    if (introNode) {
      webNodes.add(introNode);
    }
    const source: CommandAudioSource = {
      ...this.buildSource(
        packet,
        loop,
        handle,
        generation,
        target,
        key,
        "ambience",
        outro,
      ),
      webGain: gain,
      webNode: loopNode,
      webNodes,
      webStem: {
        loopDuration,
        loopNode,
        loopStartedAt,
        outroBuffer,
        outroNode: null,
        outroScheduled: false,
        outroStartsAt: 0,
      },
      webElement: null,
      webPanner: panner ?? null,
    };
    gain.gain.value = this.outputGain(source);
    this.register(source);
    introNode?.start(startAt);
    loopNode.start(loopStartedAt);
    if (!loopNode.loop) {
      const naturalOutroAt = loopStartedAt + loopDuration;
      if (!this.scheduleWebStemOutroAt(source, naturalOutroAt, false)) {
        loopNode.addEventListener("ended", () => this.dispose(key), { once: true });
      }
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
    const source = this.buildSource(
      packet,
      asset,
      handle,
      generation,
      target,
      key,
      kind,
    );
    source.onEnded = onEnded ?? null;

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
        node.playbackRate.value = source.pitch;
        const panner = createWebAudioSpatializer(context, {
          position: source.position,
          pan: source.pan / 100,
        });
        if (panner) {
          node.connect(panner);
          panner.connect(gain);
        } else {
          node.connect(gain);
        }
        if (isHrtfPanner(panner)) {
          const analyser = context.createAnalyser();
          analyser.fftSize = WEB_AUDIO_TAIL_FFT_SIZE;
          gain.connect(analyser);
          analyser.connect(bus);
          source.webTailAnalyser = analyser;
        } else {
          gain.connect(bus);
        }
        source.webNode = node;
        source.webNodes.add(node);
        source.webPanner = panner ?? null;
        this.register(source);
        node.onended = () => {
          this.disposeWebSourceAfterTail(source);
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
        element.playbackRate = source.pitch;
        element.preservesPitch = false;
        const node = context.createMediaElementSource(element);
        const panner = createWebAudioSpatializer(context, {
          position: source.position,
          pan: source.pan / 100,
        });
        if (panner) {
          node.connect(panner);
          panner.connect(gain);
        } else {
          node.connect(gain);
        }
        gain.connect(bus);
        source.webElement = element;
        source.webNode = node;
        source.webPanner = panner ?? null;
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
      source.paused = kind === "music"
        && this.commandPausedMusicHandles.has(handle);
      if (await this.attachNativeSpatialSource(source, looping, isCurrent)) {
        this.register(source);
      } else {
        if (!isCurrent()) {
          return null;
        }
        const resolved = await this.resolveNativeSource(asset);
        if (!resolved || !isCurrent()) {
          return null;
        }
        const player = await this.createNativeSound(
          resolved,
          {
            isLooping: looping,
            progressUpdateIntervalMillis: 100,
            rate: source.pitch,
            shouldCorrectPitch: false,
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
        if (kind === "music") {
          source.paused = this.commandPausedMusicHandles.has(handle);
        }
        source.nativePlayer = player;
        this.register(source);
        player.setOnPlaybackStatusUpdate((status: AVPlaybackStatus) => {
          if (!isTerminalNativePlaybackStatus(status)) {
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
    }

    if (packet.fade_in_ms && !source.paused) {
      this.fade(source, 1, packet.fade_in_ms);
    }
    return source;
  }

  private reserveEffectSlot(
    packet: AudioCommandPacket,
    asset: string,
    handle: string,
  ): (() => void) | null {
    for (const reservation of this.sourceLoadReservations) {
      if (reservation.kind === "sfx" && reservation.slot === handle) {
        this.sourceLoadReservations.delete(reservation);
      }
    }
    const incomingPriority = this.clamp(packet.priority, -100, 100, 0);
    const pendingEffects = [...this.sourceLoadReservations].filter(
      (reservation) => reservation.kind === "sfx",
    );
    const limit = this.clamp(packet.max_instances, 0, MAX_ACTIVE_EFFECTS, 0);
    const pendingMatching = pendingEffects.filter(
      (reservation) => reservation.asset === asset,
    ).length;
    let effects = [...this.commandSources.values()].filter(
      (source) => source.kind === "sfx",
    );
    let matching = effects.filter((source) => source.asset === asset);
    if (limit && matching.length + pendingMatching >= limit) {
      matching.sort((left, right) => (
        left.priority - right.priority || left.createdAt - right.createdAt
      ));
      const victim = matching[0];
      if (!victim || victim.priority > incomingPriority) {
        return null;
      }
      this.stopKey(victim.key, 0, false, false);
    }
    effects = [...this.commandSources.values()].filter(
      (source) => source.kind === "sfx",
    );
    if (effects.length + pendingEffects.length >= MAX_ACTIVE_EFFECTS) {
      effects.sort((left, right) => (
        left.priority - right.priority || left.createdAt - right.createdAt
      ));
      const victim = effects[0];
      if (!victim || victim.priority > incomingPriority) {
        return null;
      }
      this.stopKey(victim.key, 0, false, false);
    }
    const reservation = Object.freeze({ asset, kind: "sfx" as const, slot: handle });
    this.sourceLoadReservations.add(reservation);
    return () => {
      this.sourceLoadReservations.delete(reservation);
    };
  }

  private reserveLayerSlot(
    packet: AudioCommandPacket,
    kind: AudioKind,
    target: string,
  ): (() => void) | null {
    for (const reservation of this.sourceLoadReservations) {
      if (reservation.kind !== "sfx" && reservation.slot === target) {
        this.sourceLoadReservations.delete(reservation);
      }
    }
    const pendingLayers = [...this.sourceLoadReservations].filter(
      (reservation) => reservation.kind !== "sfx",
    );
    const layers = [...this.commandSources.values()].filter(
      (source) => source.kind !== "sfx",
    );
    if (layers.length + pendingLayers.length >= MAX_ACTIVE_LAYERS) {
      const currentKey = this.commandTargets.get(target);
      const current = currentKey ? this.commandSources.get(currentKey) : undefined;
      layers.sort((left, right) => (
        left.priority - right.priority || left.createdAt - right.createdAt
      ));
      const victim = current ?? layers[0];
      const incomingPriority = this.clamp(packet.priority, -100, 100, 0);
      if (!victim || (!current && victim.priority > incomingPriority)) {
        return null;
      }
      this.stopKey(victim.key, 0, false, false);
    }
    const reservation = Object.freeze({ asset: "", kind, slot: target });
    this.sourceLoadReservations.add(reservation);
    return () => {
      this.sourceLoadReservations.delete(reservation);
    };
  }

  private sequencePosition(
    segment: AudioSequenceSegment,
    elapsedMilliseconds: number,
    durationMilliseconds: number,
  ): AudioPosition | undefined {
    if (!segment.position) {
      return undefined;
    }
    if (!segment.destination_position) {
      return segment.position;
    }
    const progress = audioMotionProgress(
      durationMilliseconds > 0
        ? this.clamp(elapsedMilliseconds / durationMilliseconds, 0, 1, 0)
        : 1,
      segment.easing,
    );
    return [
      segment.position[0]
        + ((segment.destination_position[0] - segment.position[0]) * progress),
      segment.position[1]
        + ((segment.destination_position[1] - segment.position[1]) * progress),
      segment.position[2]
        + ((segment.destination_position[2] - segment.position[2]) * progress),
    ];
  }

  private scheduleSequenceFade(
    source: CommandAudioSource,
    startsAtMilliseconds: number,
    fadeInMilliseconds: number,
  ): void {
    if (!fadeInMilliseconds) {
      return;
    }
    const begin = () => {
      source.sequenceStartTimer = null;
      if (source.active) {
        this.fade(source, 1, fadeInMilliseconds);
      }
    };
    const delay = Math.max(0, startsAtMilliseconds - this.audioClockMs());
    if (delay <= 0) {
      begin();
    } else {
      source.sequenceStartTimer = setTimeout(begin, delay);
    }
  }

  private async createWebSequenceSource(
    packet: AudioCommandPacket,
    segments: readonly AudioSequenceSegment[],
    handle: string,
    generation: number,
    assetKey: string,
  ): Promise<CommandAudioSource | null> {
    const context = await this.ensureWebAudioReady();
    const isCurrent = () => this.commandGenerations.get(handle) === generation;
    if (!context || !isCurrent()) {
      return null;
    }
    const buffers = await Promise.all(
      segments.map((segment) => this.loadWebBuffer(segment.asset)),
    );
    const bus = await this.webBus("sfx", String(packet.bus || "sfx"));
    if (buffers.some((buffer) => !buffer) || !bus || !isCurrent()) {
      return null;
    }
    const gain = context.createGain();
    const key = `${handle}:${Date.now()}:${Math.random()}`;
    const source = this.buildSource(
      {
        ...packet,
        position: undefined,
        attenuation: undefined,
        gain: 1,
      },
      assetKey,
      handle,
      generation,
      "",
      key,
      "sfx",
    );
    source.webGain = gain;
    const startsAtMilliseconds = (context.currentTime * 1000) + 50;
    let cursorMilliseconds = startsAtMilliseconds;
    let completionTrack: WebSequenceTrack | null = null;
    let completionAtMilliseconds = startsAtMilliseconds;

    for (let index = 0; index < segments.length; index += 1) {
      const segment = segments[index];
      const buffer = buffers[index];
      if (!buffer) {
        this.dispose(key);
        return null;
      }
      const node = context.createBufferSource();
      const output = context.createGain();
      const panner = createWebAudioSpatializer(context, {
        position: segment.position,
        pan: segment.position
          ? panFromPosition(segment.position)
          : this.clamp(packet.pan, -100, 100, 0) / 100,
      });
      const durationMilliseconds = buffer.duration * 1000 / source.pitch;
      node.buffer = buffer;
      node.playbackRate.value = source.pitch;
      if (panner) {
        node.connect(panner);
        panner.connect(output);
      } else {
        node.connect(output);
      }
      output.connect(gain);
      output.gain.value = segment.gain * distanceAttenuationGain(
        segment.position,
        segment.attenuation,
      );
      source.webNodes.add(node);
      const track = {
        durationMilliseconds,
        node,
        output,
        panner: panner ?? null,
        segment,
        startsAtMilliseconds: cursorMilliseconds,
      };
      source.webSequenceTracks.push(track);
      const segmentEndMilliseconds = cursorMilliseconds + durationMilliseconds;
      if (segmentEndMilliseconds >= completionAtMilliseconds) {
        completionAtMilliseconds = segmentEndMilliseconds;
        completionTrack = track;
      }
      cursorMilliseconds += durationMilliseconds * segment.next_start_ratio;
    }
    if (source.webSequenceTracks.some((track) => isHrtfPanner(track.panner))) {
      const analyser = context.createAnalyser();
      analyser.fftSize = WEB_AUDIO_TAIL_FFT_SIZE;
      gain.connect(analyser);
      analyser.connect(bus);
      source.webTailAnalyser = analyser;
    } else {
      gain.connect(bus);
    }
    source.webNode = source.webSequenceTracks.length
      ? [...source.webNodes][0] ?? null
      : null;
    gain.gain.value = this.outputGain(source);
    this.register(source);
    try {
      let index = 0;
      for (const node of source.webNodes) {
        node.start(source.webSequenceTracks[index].startsAtMilliseconds / 1000);
        index += 1;
      }
    } catch {
      this.dispose(key);
      return null;
    }
    completionTrack?.node.addEventListener(
      "ended",
      () => this.disposeWebSourceAfterTail(source),
      { once: true },
    );
    if (source.webSequenceTracks.some((track) => track.segment.destination_position)) {
      source.sequenceTimer = setInterval(() => {
        if (!source.active || !this.webAudioContext) {
          return;
        }
        const now = this.webAudioContext.currentTime * 1000;
        for (const track of source.webSequenceTracks) {
          const elapsed = now - track.startsAtMilliseconds;
          if (
            elapsed < 0
            || elapsed > track.durationMilliseconds
            || !track.segment.destination_position
          ) {
            continue;
          }
          const position = this.sequencePosition(
            track.segment,
            elapsed,
            track.durationMilliseconds,
          );
          if (position && track.panner) {
            setAudioSpatializerPosition(track.panner, this.webAudioContext, position);
          }
          track.output.gain.setValueAtTime(
            track.segment.gain * distanceAttenuationGain(
              position,
              track.segment.attenuation,
            ),
            this.webAudioContext.currentTime,
          );
        }
      }, SOURCE_AUTOMATION_INTERVAL_MS);
    }
    this.scheduleSequenceFade(source, startsAtMilliseconds, packet.fade_in_ms ?? 0);
    return source;
  }

  private async createNativeSequenceSource(
    packet: AudioCommandPacket,
    segments: readonly AudioSequenceSegment[],
    handle: string,
    generation: number,
    assetKey: string,
  ): Promise<CommandAudioSource | null> {
    await this.initialize();
    const isCurrent = () => this.commandGenerations.get(handle) === generation;
    const paths = await Promise.all(
      segments.map((segment) => this.resolveNativeFilePath(segment.asset)),
    );
    if (paths.some((path) => !path) || !isCurrent()) {
      return null;
    }
    const key = `${handle}:${Date.now()}:${Math.random()}`;
    const source = this.buildSource(
      {
        ...packet,
        position: undefined,
        attenuation: undefined,
        gain: 1,
      },
      assetKey,
      handle,
      generation,
      "",
      key,
      "sfx",
    );
    source.nativeSpatialBlend = 0;
    const sourceId = this.nextNativeSpatialId();
    const timing = await this.nativeSpatialAudio.createSequence(sourceId, {
      paths: paths as string[],
      nextStartRatios: segments.map((segment) => segment.next_start_ratio),
      startPaused: true,
      volume: this.sourceMixGain(source),
      pitch: source.pitch,
      position: [0, 0, 0],
      spatialBlend: 0,
    });
    if (!timing || !isCurrent()) {
      if (timing) {
        this.nativeSpatialAudio.destroySource(sourceId);
      }
      this.releaseNativeSpatialId(sourceId);
      return null;
    }
    source.nativeSpatialId = sourceId;
    const durations = timing.durationsMilliseconds;
    let segmentCursor = 0;
    const tracks: NativeSpatialSequenceTrack[] = durations.map(
      (durationMilliseconds, index) => {
        const track = {
          durationMilliseconds,
          finalParametersApplied: !segments[index].destination_position,
          segment: segments[index],
          startsAtMilliseconds: segmentCursor,
        };
        segmentCursor += durationMilliseconds * segments[index].next_start_ratio;
        return track;
      },
    );
    source.nativeSpatialSequence = true;
    const applyTrackParameters = (
      track: NativeSpatialSequenceTrack,
      index: number,
      localElapsed: number,
    ) => {
      const position = this.sequencePosition(
        track.segment,
        localElapsed,
        track.durationMilliseconds,
      );
      return this.nativeSpatialAudio.setSequenceSegmentParameters(
        sourceId,
        index,
        track.segment.gain * distanceAttenuationGain(
          position,
          track.segment.attenuation,
        ),
        position ?? [0, 0, 0],
        position ? 1 : 0,
      );
    };
    if (tracks.some((track, index) => !applyTrackParameters(track, index, 0))) {
      this.nativeSpatialAudio.destroySource(sourceId);
      this.releaseNativeSpatialId(sourceId);
      return null;
    }
    this.register(source);
    const resumeStartedAt = this.audioClockMs();
    if (!this.nativeSpatialAudio.resumeSource(sourceId)) {
      this.dispose(key);
      return null;
    }
    const resumeFinishedAt = this.audioClockMs();
    // The native engine schedules during the synchronous bridge call. Its
    // midpoint bounds the JS/native clock estimate to half the bridge latency.
    const startsAtMilliseconds = (
      (resumeStartedAt + resumeFinishedAt) / 2
    ) + timing.startLeadMilliseconds;
    for (const track of tracks) {
      track.startsAtMilliseconds += startsAtMilliseconds;
    }
    const update = () => {
      if (!source.active) {
        return;
      }
      const now = this.audioClockMs();
      let allFinal = true;
      for (let index = 0; index < tracks.length; index += 1) {
        const track = tracks[index];
        const elapsed = now - track.startsAtMilliseconds;
        if (elapsed < 0) {
          allFinal = false;
          continue;
        }
        if (track.finalParametersApplied) {
          continue;
        }
        const localElapsed = Math.min(track.durationMilliseconds, elapsed);
        if (!applyTrackParameters(track, index, localElapsed)) {
          this.dispose(key);
          return;
        }
        track.finalParametersApplied = elapsed >= track.durationMilliseconds;
        allFinal = allFinal && track.finalParametersApplied;
      }
      if (allFinal && source.sequenceTimer) {
        clearInterval(source.sequenceTimer);
        source.sequenceTimer = null;
      }
    };
    if (tracks.some((track) => track.segment.destination_position)) {
      update();
      source.sequenceTimer = setInterval(update, SOURCE_AUTOMATION_INTERVAL_MS);
    }
    const completionAtMilliseconds = tracks.reduce(
      (latest, track) => Math.max(
        latest,
        track.startsAtMilliseconds + track.durationMilliseconds,
      ),
      startsAtMilliseconds,
    );
    source.nativeSpatialCompletionTimer = setTimeout(() => {
      source.nativeSpatialCompletionTimer = null;
      if (
        source.active
        && source.nativeSpatialId === sourceId
        && this.commandSources.get(key) === source
      ) {
        // Native completion polling normally retires the source as soon as
        // every decoded segment and HRTF tail has drained. This guard only
        // runs well after that boundary, preventing a missed native callback
        // from retaining renderers until later finite SFX can no longer start.
        this.dispose(key);
      }
    }, Math.max(
      0,
      completionAtMilliseconds
        - this.audioClockMs()
        + NATIVE_SPATIAL_COMPLETION_GRACE_MS,
    ));
    this.scheduleSequenceFade(source, startsAtMilliseconds, packet.fade_in_ms ?? 0);
    return source;
  }

  private async createNativeSequenceFallbackSource(
    packet: AudioCommandPacket,
    segments: readonly AudioSequenceSegment[],
    handle: string,
    generation: number,
    assetKey: string,
  ): Promise<CommandAudioSource | null> {
    const isCurrent = () => this.commandGenerations.get(handle) === generation;
    const resolvedSources = await Promise.all(
      segments.map((segment) => this.resolveNativeSource(segment.asset)),
    );
    if (resolvedSources.some((resolved) => !resolved) || !isCurrent()) {
      return null;
    }
    const first = segments[0];
    const key = `${handle}:${Date.now()}:${Math.random()}`;
    const source = this.buildSource(
      {
        ...packet,
        position: first.position ? [...first.position] : undefined,
        attenuation: first.attenuation,
        gain: first.gain,
      },
      assetKey,
      handle,
      generation,
      "",
      key,
      "sfx",
    );
    const players = await Promise.all(
      resolvedSources.map((resolved) => this.createNativeSound(
        resolved as AVPlaybackSource,
        {
          isLooping: false,
          progressUpdateIntervalMillis: SOURCE_AUTOMATION_INTERVAL_MS,
          rate: source.pitch,
          shouldCorrectPitch: false,
          shouldPlay: false,
          volume: 0,
        },
      )),
    );
    if (players.some((player) => !player) || !isCurrent()) {
      for (const player of players) {
        if (player) {
          this.disposeNativeSound(player);
        }
      }
      return null;
    }
    const loadedPlayers = players as ExpoAudio.Sound[];
    let statuses: AVPlaybackStatus[];
    try {
      statuses = await Promise.all(
        loadedPlayers.map((player) => player.getStatusAsync()),
      );
    } catch {
      loadedPlayers.forEach((player) => this.disposeNativeSound(player));
      return null;
    }
    if (
      !isCurrent()
      || statuses.some((status) => (
        !status.isLoaded
        || !Number.isFinite(status.durationMillis)
        || !status.durationMillis
      ))
    ) {
      loadedPlayers.forEach((player) => this.disposeNativeSound(player));
      return null;
    }
    const startsAtMilliseconds = this.audioClockMs() + 50;
    let cursorMilliseconds = startsAtMilliseconds;
    const tracks: NativeSequenceTrack[] = loadedPlayers.map((player, index) => {
      const status = statuses[index];
      const durationMilliseconds = status.isLoaded
        ? (status.durationMillis as number) / source.pitch
        : 0;
      const track = {
        durationMilliseconds,
        ended: false,
        player,
        segment: segments[index],
        startsAtMilliseconds: cursorMilliseconds,
      };
      cursorMilliseconds += durationMilliseconds * segments[index].next_start_ratio;
      return track;
    });
    const startTimers = new Set<ReturnType<typeof setTimeout>>();
    source.nativeSequence = { startTimers, tracks };
    this.register(source);
    for (const track of tracks) {
      track.player.setOnPlaybackStatusUpdate((status: AVPlaybackStatus) => {
        if (!isTerminalNativePlaybackStatus(status) || track.ended) {
          return;
        }
        track.ended = true;
        if (tracks.every((candidate) => candidate.ended)) {
          this.dispose(key);
        }
      });
      const timer = setTimeout(() => {
        startTimers.delete(timer);
        if (!source.active || !isCurrent()) {
          return;
        }
        void track.player.playAsync().catch(() => this.dispose(key));
      }, Math.max(0, track.startsAtMilliseconds - this.audioClockMs()));
      startTimers.add(timer);
    }
    this.setAbsoluteVolume(source, this.outputGain(source));
    source.sequenceTimer = setInterval(() => {
      if (source.active) {
        this.setAbsoluteVolume(source, this.outputGain(source));
      }
    }, SOURCE_AUTOMATION_INTERVAL_MS);
    if (packet.fade_in_ms) {
      this.fade(source, 1, packet.fade_in_ms);
    }
    return source;
  }

  private primeFiniteSfx(packet: AudioCommandPacket): Promise<unknown> {
    const assets = packet.segments?.length
      ? packet.segments.map((segment) => segment.asset)
      : [packet.asset || ""];
    if (Platform.OS === "web") {
      return Promise.all(assets.map((asset) => this.loadWebBuffer(asset)));
    }
    return Promise.all(assets.map((asset) => this.resolveNativeSource(asset)));
  }

  private queueFiniteSfx(
    packet: AudioCommandPacket,
    sequence: boolean,
  ): Promise<boolean> {
    const handle = String(
      packet.handle || `sfx:${Date.now()}:${Math.random()}`,
    );
    const generation = this.nextGeneration(handle);
    const oldKey = this.commandHandles.get(handle);
    if (oldKey) {
      this.stopKey(oldKey, packet.fade_out_ms ?? 0, false, false);
    }
    const queuedPacket = { ...packet, handle };
    // Asset resolution begins concurrently, while source creation remains in
    // packet order so a cached report cannot overtake a projectile or impact.
    // A failed native allocation or asset load must not own that queue forever:
    // invalidate its generation after a bounded cold-load window so later SFX
    // can continue and any late completion tears itself down as stale.
    const preload = this.primeFiniteSfx(queuedPacket);
    const launch = this.finiteSfxLaunchQueue
      .catch(() => undefined)
      .then(async () => {
        let timeout: ReturnType<typeof setTimeout> | null = null;
        const timedOut = new Promise<boolean>((resolve) => {
          timeout = setTimeout(() => {
            if (this.commandGenerations.get(handle) === generation) {
              this.nextGeneration(handle);
            }
            resolve(false);
          }, FINITE_SFX_LAUNCH_TIMEOUT_MS);
        });
        const playback = (async () => {
          await preload;
          if (this.commandGenerations.get(handle) !== generation) {
            return false;
          }
          return sequence
            ? this.playManagedSequence(queuedPacket, generation)
            : this.playManagedEffect(queuedPacket, generation);
        })();
        try {
          return await Promise.race([
            playback,
            timedOut,
          ]);
        } catch (error) {
          console.warn("Finite SFX launch failed.", error);
          return false;
        } finally {
          if (timeout) {
            clearTimeout(timeout);
          }
        }
      });
    this.finiteSfxLaunchQueue = launch.then(
      () => undefined,
      () => undefined,
    );
    return launch;
  }

  private async playManagedSequence(
    packet: AudioCommandPacket,
    expectedGeneration?: number,
  ): Promise<boolean> {
    const parsedSegments = normalizeAudioSequenceSegments(packet.segments);
    if (!parsedSegments?.length || !packet.handle) {
      return false;
    }
    const segments = parsedSegments.map((segment) => ({
      ...segment,
      asset: this.normalizeAsset(segment.asset),
    }));
    if (segments.some((segment) => !segment.asset)) {
      return false;
    }
    const handle = String(packet.handle);
    const assetKey = `sequence:${segments.map(
      (segment) => `${segment.asset.length}:${segment.asset}`,
    ).join("")}`;
    const releaseReservation = this.reserveEffectSlot(packet, assetKey, handle);
    if (!releaseReservation) {
      return false;
    }
    try {
      const generation = expectedGeneration ?? this.nextGeneration(handle);
      if (
        expectedGeneration !== undefined
        && this.commandGenerations.get(handle) !== expectedGeneration
      ) {
        return false;
      }
      if (expectedGeneration === undefined) {
        const oldKey = this.commandHandles.get(handle);
        if (oldKey) {
          this.stopKey(oldKey, packet.fade_out_ms ?? 0, false, false);
        }
      }
      return Boolean(
        Platform.OS === "web"
          ? await this.createWebSequenceSource(
            packet,
            segments,
            handle,
            generation,
            assetKey,
          )
          : (await this.createNativeSequenceSource(
              packet,
              segments,
              handle,
              generation,
              assetKey,
            )) ?? await this.createNativeSequenceFallbackSource(
              packet,
              segments,
              handle,
              generation,
              assetKey,
            ),
      );
    } finally {
      releaseReservation();
    }
  }

  private async playManagedEffect(
    packet: AudioCommandPacket,
    expectedGeneration?: number,
  ): Promise<boolean> {
    const asset = this.normalizeAsset(packet.asset || "");
    if (!asset) {
      return false;
    }
    const handle = String(
      packet.handle || `sfx:${Date.now()}:${Math.random()}`,
    );
    const releaseReservation = this.reserveEffectSlot(packet, asset, handle);
    if (!releaseReservation) {
      return false;
    }
    try {
      const generation = expectedGeneration ?? this.nextGeneration(handle);
      if (
        expectedGeneration !== undefined
        && this.commandGenerations.get(handle) !== expectedGeneration
      ) {
        return false;
      }
      if (expectedGeneration === undefined) {
        const oldKey = this.commandHandles.get(handle);
        if (oldKey) {
          this.stopKey(oldKey, packet.fade_out_ms ?? 0, false, false);
        }
      }
      return Boolean(await this.createSource(
        packet,
        asset,
        handle,
        generation,
        "",
        Boolean(packet.loop),
      ));
    } finally {
      releaseReservation();
    }
  }

  private async playManagedLayer(packet: AudioCommandPacket): Promise<boolean> {
    const kind = packet.kind;
    const asset = this.normalizeAsset(packet.asset || "");
    if (!kind || !asset) {
      return false;
    }
    const target = this.target(packet);
    const releaseReservation = this.reserveLayerSlot(packet, kind, target);
    if (!releaseReservation) {
      return false;
    }
    try {
      return await this.playManagedLayerReserved(packet, kind, asset, target);
    } finally {
      releaseReservation();
    }
  }

  private async playManagedLayerReserved(
    packet: AudioCommandPacket,
    kind: AudioKind,
    asset: string,
    target: string,
  ): Promise<boolean> {
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
          : (await this.createNativeSpatialStemSource(
            packet,
            handle,
            generation,
            target,
            targetGeneration,
          )) ?? await this.createNativeStemSource(
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
    if (source.nativeSpatialId) {
      this.nativeSpatialAudio.resumeSource(source.nativeSpatialId);
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
        // ExpoAV remains the single Android audio-focus coordinator. The
        // playlist engine only supplies gapless ambience stems and must not
        // compete with accessibility speech or change the system output route.
        interruptionMode: "mixWithOthers",
        playsInSilentMode: true,
        shouldPlayInBackground: true,
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
    pan?: number,
  ): void {
    const bounded = this.clamp(volume, 0, 1, 0);
    this.nativeSoundVolumes.set(sound, bounded);
    void sound.setVolumeAsync(bounded, pan).catch(() => undefined);
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
