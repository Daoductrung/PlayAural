import type { AVPlaybackSource } from "expo-av";
import { requireOptionalNativeModule } from "expo-modules-core";
import { Platform } from "react-native";

export type NativeSpatialAudioRuntimeConfig = Readonly<{
  endedPollIntervalMilliseconds: number;
  hrtfFrameSize: number;
  maxSources: number;
  parameterSmoothingMilliseconds: number;
}>;

export const DEFAULT_NATIVE_SPATIAL_AUDIO_CONFIG: NativeSpatialAudioRuntimeConfig = Object.freeze({
  endedPollIntervalMilliseconds: 50,
  hrtfFrameSize: 512,
  maxSources: 96,
  parameterSmoothingMilliseconds: 5,
});

const NATIVE_SIGNED_INTEGER_MAX = 2_147_483_647;

function isNativeSpatialAudioConfigValid(
  config: NativeSpatialAudioRuntimeConfig,
): boolean {
  return Number.isInteger(config.endedPollIntervalMilliseconds)
    && config.endedPollIntervalMilliseconds > 0
    && config.endedPollIntervalMilliseconds <= NATIVE_SIGNED_INTEGER_MAX
    && Number.isInteger(config.hrtfFrameSize)
    && config.hrtfFrameSize > 0
    && config.hrtfFrameSize <= NATIVE_SIGNED_INTEGER_MAX
    && Number.isInteger(config.maxSources)
    && config.maxSources > 0
    && config.maxSources <= NATIVE_SIGNED_INTEGER_MAX
    && Number.isInteger(config.parameterSmoothingMilliseconds)
    && config.parameterSmoothingMilliseconds >= 0
    && config.parameterSmoothingMilliseconds <= NATIVE_SIGNED_INTEGER_MAX;
}

export type NativeSpatialAudioSourceSpec = Readonly<{
  introPath?: string;
  loopPath: string;
  outroPath?: string;
  playIntro: boolean;
  looping: boolean;
  streamFromDisk: boolean;
  startPaused: boolean;
  volume: number;
  pitch: number;
  position: readonly [number, number, number];
}>;

export type NativeSpatialAudioSequenceSpec = Readonly<{
  paths: readonly string[];
  nextStartRatios: readonly number[];
  startPaused: boolean;
  volume: number;
  pitch: number;
  position: readonly [number, number, number];
  spatialBlend: number;
}>;

export type NativeSpatialAudioSequenceTiming = Readonly<{
  durationsMilliseconds: readonly number[];
  startLeadMilliseconds: number;
}>;

type NativeSpatialAudioCapabilities = {
  available: boolean;
  hrtf: boolean;
  sampleRate: number;
};

type NativeSpatialAudioBridge = {
  initialize(
    hrtfFrameSize: number,
    parameterSmoothingMilliseconds: number,
    maxSources: number,
  ): Promise<NativeSpatialAudioCapabilities>;
  createSource(sourceId: string, options: {
    introPath: string | null;
    loopPath: string;
    outroPath: string | null;
    playIntro: boolean;
    looping: boolean;
    streamFromDisk: boolean;
    startPaused: boolean;
    volume: number;
    pitch: number;
    x: number;
    y: number;
    z: number;
    spatialBlend: number;
    sequencePaths?: readonly string[];
    sequenceNextStartRatios?: readonly number[];
  }): Promise<readonly number[]>;
  setParameters(
    sourceId: string,
    volume: number,
    pitch: number,
    x: number,
    y: number,
    z: number,
    spatialBlend: number,
  ): boolean;
  pauseSource(sourceId: string): boolean;
  resumeSource(sourceId: string): boolean;
  requestOutro(sourceId: string, finishLoopBoundary: boolean): boolean;
  destroySource(sourceId: string): void;
  drainEndedSources(): string[];
  shutdown(): void;
};

function loadNativeBridge(): NativeSpatialAudioBridge | null {
  if (Platform.OS === "web") {
    return null;
  }
  try {
    return requireOptionalNativeModule<NativeSpatialAudioBridge>(
      "PlayAuralSpatialAudio",
    );
  } catch (error) {
    console.warn("Native spatial-audio module discovery failed.", error);
    return null;
  }
}

export function playbackSourceFilePath(source: AVPlaybackSource | null): string | null {
  if (!source || typeof source === "number" || !("uri" in source)) {
    return null;
  }
  const uri = String(source.uri || "");
  if (uri.startsWith("/")) {
    return uri;
  }
  if (!uri.startsWith("file://")) {
    return null;
  }
  try {
    const decoded = decodeURIComponent(uri.slice("file://".length));
    if (!decoded || decoded.includes("\0")) {
      return null;
    }
    return decoded.startsWith("localhost/")
      ? decoded.slice("localhost".length)
      : decoded;
  } catch {
    return null;
  }
}

export class NativeSpatialAudio {
  private readonly bridge = loadNativeBridge();
  private initialization: Promise<boolean> | null = null;
  private ready = false;
  private failed = false;
  private lifecycleGeneration = 0;
  private sampleRate = 0;

  readonly config: NativeSpatialAudioRuntimeConfig;

  constructor(config: NativeSpatialAudioRuntimeConfig = DEFAULT_NATIVE_SPATIAL_AUDIO_CONFIG) {
    this.config = Object.freeze({ ...config });
  }

  async initialize(): Promise<boolean> {
    if (this.ready) {
      return true;
    }
    if (!this.bridge || this.failed) {
      return false;
    }
    if (!isNativeSpatialAudioConfigValid(this.config)) {
      this.failed = true;
      console.warn("Native spatial-audio configuration is invalid.");
      return false;
    }
    if (!this.initialization) {
      const lifecycleGeneration = this.lifecycleGeneration;
      const initialization = this.bridge.initialize(
        this.config.hrtfFrameSize,
        this.config.parameterSmoothingMilliseconds,
        this.config.maxSources,
      ).then((capabilities) => {
        if (this.lifecycleGeneration !== lifecycleGeneration) {
          this.bridge?.shutdown();
          return false;
        }
        this.ready = Boolean(
          capabilities.available
          && capabilities.hrtf
          && Number.isInteger(capabilities.sampleRate)
          && capabilities.sampleRate > 0,
        );
        this.sampleRate = this.ready ? capabilities.sampleRate : 0;
        this.failed = !this.ready;
        if (!this.ready) {
          this.bridge?.shutdown();
        }
        return this.ready;
      }).catch((error) => {
        if (this.lifecycleGeneration !== lifecycleGeneration) {
          return false;
        }
        this.bridge?.shutdown();
        this.failed = true;
        console.warn(
          "Native Steam Audio HRTF is unavailable; using the platform audio fallback.",
          error,
        );
        return false;
      }).finally(() => {
        if (this.initialization === initialization) {
          this.initialization = null;
        }
      });
      this.initialization = initialization;
    }
    return this.initialization;
  }

  async createSource(sourceId: string, spec: NativeSpatialAudioSourceSpec): Promise<boolean> {
    const lifecycleGeneration = this.lifecycleGeneration;
    if (!await this.initialize() || !this.bridge) {
      return false;
    }
    try {
      await this.bridge.createSource(sourceId, {
        introPath: spec.introPath ?? null,
        loopPath: spec.loopPath,
        outroPath: spec.outroPath ?? null,
        playIntro: spec.playIntro,
        looping: spec.looping,
        streamFromDisk: spec.streamFromDisk,
        startPaused: spec.startPaused,
        volume: spec.volume,
        pitch: spec.pitch,
        x: spec.position[0],
        y: spec.position[1],
        z: spec.position[2],
        spatialBlend: 1,
      });
      if (this.lifecycleGeneration !== lifecycleGeneration) {
        this.bridge.destroySource(sourceId);
        return false;
      }
      return true;
    } catch (error) {
      try {
        this.bridge.destroySource(sourceId);
      } catch {
        // Creation may have failed before native ownership was registered.
      }
      console.warn("Native spatial-audio source creation failed.", error);
      return false;
    }
  }

  async createSequence(
    sourceId: string,
    spec: NativeSpatialAudioSequenceSpec,
  ): Promise<NativeSpatialAudioSequenceTiming | null> {
    const lifecycleGeneration = this.lifecycleGeneration;
    if (
      !spec.paths.length
      || spec.nextStartRatios.length !== spec.paths.length
      || spec.nextStartRatios.some((ratio) => (
        !Number.isFinite(ratio) || ratio < 0 || ratio > 1
      ))
    ) {
      return null;
    }
    if (!await this.initialize() || !this.bridge || this.sampleRate <= 0) {
      return null;
    }
    try {
      const durationsMilliseconds = await this.bridge.createSource(sourceId, {
        introPath: null,
        loopPath: "",
        outroPath: null,
        playIntro: false,
        looping: false,
        streamFromDisk: false,
        startPaused: spec.startPaused,
        volume: spec.volume,
        pitch: spec.pitch,
        x: spec.position[0],
        y: spec.position[1],
        z: spec.position[2],
        spatialBlend: spec.spatialBlend,
        sequencePaths: [...spec.paths],
        sequenceNextStartRatios: [...spec.nextStartRatios],
      });
      if (
        this.lifecycleGeneration !== lifecycleGeneration
        || durationsMilliseconds.length !== spec.paths.length
        || durationsMilliseconds.some((duration) => (
          !Number.isFinite(duration) || duration <= 0
        ))
      ) {
        this.bridge.destroySource(sourceId);
        return null;
      }
      return Object.freeze({
        durationsMilliseconds: Object.freeze([...durationsMilliseconds]),
        startLeadMilliseconds: this.config.hrtfFrameSize * 1000 / this.sampleRate,
      });
    } catch (error) {
      try {
        this.bridge.destroySource(sourceId);
      } catch {
        // Creation may have failed before native ownership was registered.
      }
      console.warn("Native spatial-audio sequence creation failed.", error);
      return null;
    }
  }

  setParameters(
    sourceId: string,
    volume: number,
    pitch: number,
    position: readonly [number, number, number],
    spatialBlend = 1,
  ): boolean {
    return this.ready && Boolean(this.bridge?.setParameters(
      sourceId,
      volume,
      pitch,
      position[0],
      position[1],
      position[2],
      spatialBlend,
    ));
  }

  pauseSource(sourceId: string): boolean {
    return this.ready && Boolean(this.bridge?.pauseSource(sourceId));
  }

  resumeSource(sourceId: string): boolean {
    return this.ready && Boolean(this.bridge?.resumeSource(sourceId));
  }

  requestOutro(sourceId: string, finishLoopBoundary: boolean): boolean {
    return this.ready && Boolean(
      this.bridge?.requestOutro(sourceId, finishLoopBoundary),
    );
  }

  destroySource(sourceId: string): void {
    if (this.ready) {
      this.bridge?.destroySource(sourceId);
    }
  }

  drainEndedSources(): string[] {
    if (!this.ready || !this.bridge) {
      return [];
    }
    try {
      const ended = this.bridge.drainEndedSources();
      return Array.isArray(ended)
        ? ended.filter((sourceId): sourceId is string => typeof sourceId === "string")
        : [];
    } catch (error) {
      console.warn("Native spatial-audio completion polling failed.", error);
      return [];
    }
  }

  shutdown(): void {
    this.lifecycleGeneration += 1;
    if (this.bridge && (this.ready || this.initialization)) {
      try {
        this.bridge.shutdown();
      } catch {
        // Native module teardown is idempotent; ignore an already-retired host.
      }
    }
    this.ready = false;
    this.failed = false;
    this.sampleRate = 0;
  }
}
