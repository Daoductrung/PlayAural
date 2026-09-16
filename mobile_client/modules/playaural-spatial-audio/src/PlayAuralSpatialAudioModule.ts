import { requireNativeModule } from "expo-modules-core";

export type SpatialAudioCapabilities = {
  available: boolean;
  hrtf: boolean;
  sampleRate: number;
};

export type SpatialAudioSourceOptions = {
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
  sequencePaths?: readonly string[];
  spatialBlend?: number;
};

export type SpatialAudioEngineOptions = {
  hrtfFrameSize: number;
  parameterSmoothingMilliseconds: number;
  maxSources: number;
};

export type PlayAuralSpatialAudioNativeModule = {
  initialize(options: SpatialAudioEngineOptions): Promise<SpatialAudioCapabilities>;
  createSource(sourceId: string, options: SpatialAudioSourceOptions): Promise<readonly number[]>;
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

type PlayAuralSpatialAudioBridge = {
  initialize(
    hrtfFrameSize: number,
    parameterSmoothingMilliseconds: number,
    maxSources: number,
  ): Promise<SpatialAudioCapabilities>;
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
  }): Promise<readonly number[]>;
  setParameters: PlayAuralSpatialAudioNativeModule["setParameters"];
  pauseSource: PlayAuralSpatialAudioNativeModule["pauseSource"];
  resumeSource: PlayAuralSpatialAudioNativeModule["resumeSource"];
  requestOutro: PlayAuralSpatialAudioNativeModule["requestOutro"];
  destroySource: PlayAuralSpatialAudioNativeModule["destroySource"];
  drainEndedSources: PlayAuralSpatialAudioNativeModule["drainEndedSources"];
  shutdown: PlayAuralSpatialAudioNativeModule["shutdown"];
};

const bridge = requireNativeModule<PlayAuralSpatialAudioBridge>(
  "PlayAuralSpatialAudio",
);

const module: PlayAuralSpatialAudioNativeModule = {
  initialize: (options) => bridge.initialize(
    options.hrtfFrameSize,
    options.parameterSmoothingMilliseconds,
    options.maxSources,
  ),
  createSource: (sourceId, options) => bridge.createSource(sourceId, {
    introPath: options.introPath ?? null,
    loopPath: options.loopPath,
    outroPath: options.outroPath ?? null,
    playIntro: options.playIntro,
    looping: options.looping,
    streamFromDisk: options.streamFromDisk,
    startPaused: options.startPaused,
    volume: options.volume,
    pitch: options.pitch,
    x: options.position[0],
    y: options.position[1],
    z: options.position[2],
    spatialBlend: options.spatialBlend ?? 1,
    ...(options.sequencePaths ? { sequencePaths: options.sequencePaths } : {}),
  }),
  setParameters: (...args) => bridge.setParameters(...args),
  pauseSource: (sourceId) => bridge.pauseSource(sourceId),
  resumeSource: (sourceId) => bridge.resumeSource(sourceId),
  requestOutro: (sourceId, boundary) => bridge.requestOutro(sourceId, boundary),
  destroySource: (sourceId) => bridge.destroySource(sourceId),
  drainEndedSources: () => bridge.drainEndedSources(),
  shutdown: () => bridge.shutdown(),
};

export default module;
