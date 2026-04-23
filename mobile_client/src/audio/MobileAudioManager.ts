import { Audio as ExpoAudio, InterruptionModeAndroid, InterruptionModeIOS } from "expo-av";
import type { AVPlaybackSource, AVPlaybackStatus, AVPlaybackStatusToSet } from "expo-av";
import { Asset } from "expo-asset";
import { requireNativeModule } from "expo-modules-core";
import { Platform } from "react-native";

import { soundManifest } from "../generated/soundManifest";
import { ENABLE_CLIENT_DEBUG_LOGS } from "../utils/debug";

type ManagedNativePlayer = {
  player: ExpoAudio.Sound;
  sourceKey: string;
};

type ManagedWebStream = {
  element: HTMLAudioElement;
  gainNode: GainNode;
  sourceKey: string;
  sourceNode: MediaElementAudioSourceNode;
};

type WebBusName = "ambience" | "music";

type WebSfxHandle = {
  gain: GainNode;
  panner: StereoPannerNode | null;
  source: AudioBufferSourceNode;
};

type DesiredMusicRequest = {
  looping: boolean;
  name: string;
};

type DesiredAmbienceRequest = {
  intro: string;
  loop: string;
  outro: string;
};

type AmbiencePhase = "idle" | "intro" | "loop" | "outro";

const DEBUG_PREFIX = "PLAYAURAL_DEBUG Audio";

type AndroidNativeAudioMode = {
  interruptionModeAndroid: number;
  shouldDuckAndroid: boolean;
  staysActiveInBackground: boolean;
};

type ExponentAVModule = {
  setAudioMode(mode: AndroidNativeAudioMode): Promise<void>;
};

const exponentAV = Platform.OS === "android"
  ? requireNativeModule<ExponentAVModule>("ExponentAV")
  : null;

export class MobileAudioManager {
  private initialized = false;
  private nativeAudioModeReady = false;
  private nativeAudioModeLoading: Promise<void> | null = null;
  private musicPlayer: ManagedNativePlayer | null = null;
  private ambienceIntroPlayer: ManagedNativePlayer | null = null;
  private ambienceLoopPlayer: ManagedNativePlayer | null = null;
  private ambienceOutroPlayer: ManagedNativePlayer | null = null;
  private ambienceOutroKey: string | null = null;
  private ambiencePhase: AmbiencePhase = "idle";
  private ambiencePlaybackId = 0;
  private sfxPlayers = new Set<ExpoAudio.Sound>();
  private retiringMusicPlayers = new Set<ExpoAudio.Sound>();
  private musicVolume = 0.2;
  private ambienceVolume = 0.3;
  private musicTransitionId = 0;
  private musicFadeInterval: ReturnType<typeof setInterval> | null = null;
  private nativeSourceCache = new Map<string, AVPlaybackSource>();
  private nativeSourceLoading = new Map<string, Promise<AVPlaybackSource | null>>();
  private nativeSoundVolumes = new WeakMap<ExpoAudio.Sound, number>();
  private desiredMusicRequest: DesiredMusicRequest | null = null;
  private desiredAmbienceRequest: DesiredAmbienceRequest | null = null;

  private webAudioContext: AudioContext | null = null;
  private webMasterGain: GainNode | null = null;
  private webMusicBus: GainNode | null = null;
  private webSfxBus: GainNode | null = null;
  private webAmbienceBus: GainNode | null = null;
  private webBufferCache = new Map<string, AudioBuffer>();
  private webBufferLoading = new Map<string, Promise<AudioBuffer | null>>();
  private webSfxRefs = new Set<WebSfxHandle>();
  private webMusicPlayer: ManagedWebStream | null = null;
  private webAmbienceIntroPlayer: ManagedWebStream | null = null;
  private webAmbienceLoopPlayer: ManagedWebStream | null = null;
  private webAmbienceOutroPlayer: ManagedWebStream | null = null;
  private webRetiringMusicPlayers = new Set<ManagedWebStream>();
  private webPendingMusicRequest: { looping: boolean; name: string } | null = null;
  private webPendingAmbienceRequest: { intro: string; loop: string; outro: string } | null = null;
  private webUriCache = new Map<string, string>();

  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    if (Platform.OS !== "web") {
      await this.ensureNativeAudioMode();
    }

    this.debug("initialize", Platform.OS);
    this.initialized = true;
  }

  shutdown(): void {
    this.cancelMusicFade();
    ++this.musicTransitionId;
    ++this.ambiencePlaybackId;
    this.desiredMusicRequest = null;
    this.desiredAmbienceRequest = null;
    this.ambienceOutroKey = null;
    this.ambiencePhase = "idle";
    this.webPendingMusicRequest = null;
    this.webPendingAmbienceRequest = null;

    for (const player of this.retiringMusicPlayers) {
      this.disposeNativeSound(player);
    }
    this.retiringMusicPlayers.clear();

    for (const player of this.sfxPlayers) {
      this.disposeNativeSound(player);
    }
    this.sfxPlayers.clear();

    if (this.musicPlayer) {
      this.disposeNativeSound(this.musicPlayer.player);
      this.musicPlayer = null;
    }
    if (this.ambienceIntroPlayer) {
      this.disposeNativeSound(this.ambienceIntroPlayer.player);
      this.ambienceIntroPlayer = null;
    }
    if (this.ambienceLoopPlayer) {
      this.disposeNativeSound(this.ambienceLoopPlayer.player);
      this.ambienceLoopPlayer = null;
    }
    if (this.ambienceOutroPlayer) {
      this.disposeNativeSound(this.ambienceOutroPlayer.player);
      this.ambienceOutroPlayer = null;
    }

    if (this.webMusicPlayer) {
      this.disposeWebStream(this.webMusicPlayer);
      this.webMusicPlayer = null;
    }
    if (this.webAmbienceIntroPlayer) {
      this.disposeWebStream(this.webAmbienceIntroPlayer);
      this.webAmbienceIntroPlayer = null;
    }
    if (this.webAmbienceLoopPlayer) {
      this.disposeWebStream(this.webAmbienceLoopPlayer);
      this.webAmbienceLoopPlayer = null;
    }
    if (this.webAmbienceOutroPlayer) {
      this.disposeWebStream(this.webAmbienceOutroPlayer);
      this.webAmbienceOutroPlayer = null;
    }
    for (const player of this.webRetiringMusicPlayers) {
      this.disposeWebStream(player);
    }
    this.webRetiringMusicPlayers.clear();
    for (const handle of this.webSfxRefs) {
      try {
        handle.source.stop();
      } catch {
        // Ignore stop races for already-ended web sounds.
      }
      this.disposeWebSfx(handle);
    }
    this.webSfxRefs.clear();
    this.initialized = false;
  }

  async handleUserInteraction(): Promise<void> {
    if (Platform.OS !== "web") {
      return;
    }
    this.debug("user-interaction", "");
    await this.ensureWebAudioReady();
    if (this.webPendingMusicRequest) {
      const pending = this.webPendingMusicRequest;
      this.webPendingMusicRequest = null;
      if (this.musicVolume > 0) {
        await this.playWebMusic(pending.name, pending.looping);
      }
    }
    if (this.webPendingAmbienceRequest) {
      const pending = this.webPendingAmbienceRequest;
      this.webPendingAmbienceRequest = null;
      if (this.ambienceVolume > 0) {
        await this.playWebAmbience(pending.loop, pending.intro, pending.outro);
      }
    }
  }

  setMusicVolume(volume: number): void {
    const wasMuted = this.musicVolume <= 0;
    this.musicVolume = Math.max(0, Math.min(1, volume));
    if (this.musicVolume <= 0) {
      this.webPendingMusicRequest = null;
      this.stopMusic(false, false);
      return;
    }

    if (this.musicPlayer) {
      this.setNativeSoundVolume(this.musicPlayer.player, this.musicVolume);
    }

    if (this.webAudioContext && this.webMusicBus) {
      this.webMusicBus.gain.setTargetAtTime(
        this.musicVolume,
        this.webAudioContext.currentTime,
        0.05,
      );
    }

    if (wasMuted && !this.musicPlayer && this.desiredMusicRequest) {
      void this.playMusic(this.desiredMusicRequest.name, this.desiredMusicRequest.looping);
    }
  }

  setAmbienceVolume(volume: number): void {
    const wasMuted = this.ambienceVolume <= 0;
    this.ambienceVolume = Math.max(0, Math.min(1, volume));
    if (this.ambienceVolume <= 0) {
      this.webPendingAmbienceRequest = null;
      this.stopAmbience(true, false);
      return;
    }

    if (this.ambienceLoopPlayer) {
      this.setNativeSoundVolume(this.ambienceLoopPlayer.player, this.ambienceVolume);
    }
    if (this.ambienceIntroPlayer) {
      this.setNativeSoundVolume(this.ambienceIntroPlayer.player, this.ambienceVolume);
    }
    if (this.ambienceOutroPlayer) {
      this.setNativeSoundVolume(this.ambienceOutroPlayer.player, this.ambienceVolume);
    }

    if (this.webAudioContext && this.webAmbienceBus) {
      this.webAmbienceBus.gain.setTargetAtTime(
        this.ambienceVolume,
        this.webAudioContext.currentTime,
        0.05,
      );
    }

    if (
      wasMuted &&
      !this.ambienceIntroPlayer &&
      !this.ambienceLoopPlayer &&
      !this.ambienceOutroPlayer &&
      this.desiredAmbienceRequest
    ) {
      void this.playAmbience(
        this.desiredAmbienceRequest.loop,
        this.desiredAmbienceRequest.intro,
        this.desiredAmbienceRequest.outro,
      );
    }
  }

  getMusicVolume(): number {
    return this.musicVolume;
  }

  getAmbienceVolume(): number {
    return this.ambienceVolume;
  }

  refreshPlaybackState(): void {
    if (Platform.OS === "web") {
      return;
    }

    if (this.musicPlayer) {
      this.setNativeSoundVolume(this.musicPlayer.player, this.musicVolume);
      void this.musicPlayer.player.playAsync().catch(() => undefined);
    } else if (this.musicVolume > 0 && this.desiredMusicRequest) {
      void this.playMusic(this.desiredMusicRequest.name, this.desiredMusicRequest.looping);
    }

    if (this.ambienceIntroPlayer) {
      this.setNativeSoundVolume(this.ambienceIntroPlayer.player, this.ambienceVolume);
      void this.ambienceIntroPlayer.player.playAsync().catch(() => undefined);
    }
    if (this.ambienceLoopPlayer) {
      this.setNativeSoundVolume(this.ambienceLoopPlayer.player, this.ambienceVolume);
      void this.ambienceLoopPlayer.player.playAsync().catch(() => undefined);
    }
    if (this.ambienceOutroPlayer) {
      this.setNativeSoundVolume(this.ambienceOutroPlayer.player, this.ambienceVolume);
      void this.ambienceOutroPlayer.player.playAsync().catch(() => undefined);
    }
    if (
      !this.ambienceIntroPlayer &&
      !this.ambienceLoopPlayer &&
      !this.ambienceOutroPlayer &&
      this.ambienceVolume > 0 &&
      this.desiredAmbienceRequest
    ) {
      void this.playAmbience(
        this.desiredAmbienceRequest.loop,
        this.desiredAmbienceRequest.intro,
        this.desiredAmbienceRequest.outro,
      );
    }
  }

  async playSound(
    name: string,
    options: { volume?: number; pitch?: number; pan?: number } = {},
  ): Promise<boolean> {
    this.debug("play-sound-request", name);
    if (Platform.OS === "web") {
      return this.playWebSound(name, options);
    }

    await this.initialize();
    return this.playNativeSound(name, options);
  }

  async playMusic(name: string, looping = true): Promise<boolean> {
    this.debug("play-music-request", name);
    this.desiredMusicRequest = { looping, name };
    if (this.musicVolume <= 0) {
      this.webPendingMusicRequest = null;
      this.stopMusic(false, false);
      return false;
    }
    if (Platform.OS === "web") {
      return this.playWebMusic(name, looping);
    }

    await this.initialize();
    const transitionId = ++this.musicTransitionId;
    const source = await this.resolveNativeSource(name);
    if (!source) {
      return false;
    }
    if (this.musicPlayer?.sourceKey === name) {
      this.cancelMusicFade();
      void this.musicPlayer.player.setIsLoopingAsync(looping).catch(() => undefined);
      this.setNativeSoundVolume(this.musicPlayer.player, this.musicVolume);
      void this.musicPlayer.player.playAsync().catch(() => undefined);
      return true;
    }

    const player = await this.createNativeSound(
      source,
      {
        isLooping: looping,
        progressUpdateIntervalMillis: 250,
        shouldPlay: true,
        volume: 0,
      },
    );
    if (!player) {
      return false;
    }
    if (transitionId !== this.musicTransitionId) {
      this.disposeNativeSound(player);
      return false;
    }
    const nextMusicPlayer = { player, sourceKey: name };
    const previousMusicPlayer = this.musicPlayer;
    this.musicPlayer = nextMusicPlayer;
    if (previousMusicPlayer) {
      this.retiringMusicPlayers.add(previousMusicPlayer.player);
    }

    this.cancelMusicFade();
    this.musicFadeInterval = setInterval(() => {
      if (transitionId !== this.musicTransitionId) {
        this.cancelMusicFade();
        return;
      }

      const step = 0.05;
      const currentVolume = this.getTargetNativePlayerVolume(nextMusicPlayer.player);
      const nextVolume = Math.min(this.musicVolume, currentVolume + step);
      this.setNativeSoundVolume(nextMusicPlayer.player, nextVolume);

      this.fadeRetiringMusicPlayers(step);

      if (nextVolume >= this.musicVolume && this.retiringMusicPlayers.size === 0) {
        this.cancelMusicFade();
      }
    }, 50);
    return true;
  }

  stopMusic(fade = true, clearRequested = true): void {
    if (clearRequested) {
      this.desiredMusicRequest = null;
    }

    if (Platform.OS === "web") {
      this.stopWebMusic(fade);
      return;
    }

    if (!this.musicPlayer) {
      if (!fade) {
        this.cancelMusicFade();
        this.clearRetiringMusicPlayers();
      }
      return;
    }

    const current = this.musicPlayer;
    this.musicPlayer = null;
    ++this.musicTransitionId;
    if (!fade) {
      this.cancelMusicFade();
      this.disposeNativeSound(current.player);
      this.clearRetiringMusicPlayers();
      return;
    }

    this.retiringMusicPlayers.add(current.player);
    this.cancelMusicFade();
    this.musicFadeInterval = setInterval(() => {
      this.fadeRetiringMusicPlayers(0.05);
      if (this.retiringMusicPlayers.size === 0) {
        this.cancelMusicFade();
      }
    }, 50);
  }

  async playAmbience(loop: string, intro = "", outro = ""): Promise<boolean> {
    this.debug("play-ambience-request", loop);
    this.desiredAmbienceRequest = { intro, loop, outro };
    if (this.ambienceVolume <= 0) {
      this.webPendingAmbienceRequest = null;
      this.stopAmbience(true, false);
      return false;
    }
    if (Platform.OS === "web") {
      return this.playWebAmbience(loop, intro, outro);
    }

    await this.initialize();
    this.stopAmbience(true, false);
    const playbackId = ++this.ambiencePlaybackId;

    this.ambienceOutroKey = outro || null;

    const loopSource = await this.resolveNativeSource(loop);
    if (!loopSource) {
      return false;
    }

    const startLoop = () => {
      if (playbackId !== this.ambiencePlaybackId) {
        return;
      }
      void this.createNativeSound(
        loopSource,
        {
          isLooping: true,
          progressUpdateIntervalMillis: 250,
          shouldPlay: true,
          volume: this.ambienceVolume,
        },
      ).then((loopPlayer) => {
        if (!loopPlayer) {
          if (playbackId === this.ambiencePlaybackId) {
            this.ambiencePhase = "idle";
          }
          return;
        }
        if (playbackId !== this.ambiencePlaybackId) {
          this.disposeNativeSound(loopPlayer);
          return;
        }
        this.ambienceLoopPlayer = { player: loopPlayer, sourceKey: loop };
        this.ambiencePhase = "loop";
      });
    };

    const introSource = intro ? await this.resolveNativeSource(intro) : null;
    if (introSource) {
      let introPlayerRef: ExpoAudio.Sound | null = null;
      const introPlayer = await this.createNativeSound(
        introSource,
        {
          isLooping: false,
          progressUpdateIntervalMillis: 80,
          shouldPlay: true,
          volume: this.ambienceVolume,
        },
        () => {
          if (this.ambienceIntroPlayer?.player === introPlayerRef) {
            this.ambienceIntroPlayer = null;
          }
          if (introPlayerRef) {
            this.disposeNativeSound(introPlayerRef);
          }
          startLoop();
        },
      );
      if (!introPlayer) {
        return false;
      }
      introPlayerRef = introPlayer;
      if (playbackId !== this.ambiencePlaybackId) {
        this.disposeNativeSound(introPlayer);
        return false;
      }
      this.ambienceIntroPlayer = { player: introPlayer, sourceKey: intro };
      this.ambiencePhase = "intro";
      return true;
    }

    startLoop();
    return true;
  }

  stopAmbience(force = false, clearRequested = true): void {
    if (clearRequested) {
      this.desiredAmbienceRequest = null;
    }

    if (Platform.OS === "web") {
      this.stopWebAmbience(force);
      return;
    }

    const phaseAtStop = this.ambiencePhase;
    ++this.ambiencePlaybackId;

    if (this.ambienceIntroPlayer) {
      this.disposeNativeSound(this.ambienceIntroPlayer.player);
      this.ambienceIntroPlayer = null;
    }

    if (this.ambienceLoopPlayer) {
      this.disposeNativeSound(this.ambienceLoopPlayer.player);
      this.ambienceLoopPlayer = null;
    }

    if (this.ambienceOutroPlayer) {
      if (!force && phaseAtStop === "outro") {
        return;
      }
      this.disposeNativeSound(this.ambienceOutroPlayer.player);
      this.ambienceOutroPlayer = null;
    }

    this.ambiencePhase = "idle";

    if (!force && phaseAtStop === "loop" && this.ambienceOutroKey) {
      if (this.ambienceVolume <= 0) {
        this.ambienceOutroKey = null;
        return;
      }
      const outroSource = this.resolveNativeSourceSync(this.ambienceOutroKey);
      if (!outroSource) {
        return;
      }
      const outroKey = this.ambienceOutroKey;
      void this.createNativeSound(
        outroSource,
        {
          isLooping: false,
          progressUpdateIntervalMillis: 80,
          shouldPlay: true,
          volume: this.ambienceVolume,
        },
      ).then((outroPlayer) => {
        if (!outroPlayer) {
          return;
        }
        outroPlayer.setOnPlaybackStatusUpdate((status: AVPlaybackStatus) => {
          if (!status.isLoaded || !status.didJustFinish) {
            return;
          }
          if (this.ambienceOutroPlayer?.player === outroPlayer) {
            this.ambienceOutroPlayer = null;
          }
          this.ambiencePhase = "idle";
          this.disposeNativeSound(outroPlayer);
        });
        this.ambienceOutroPlayer = { player: outroPlayer, sourceKey: outroKey };
        this.ambiencePhase = "outro";
      });
    }
  }

  private resolveSource(name: string): AVPlaybackSource | null {
    const normalized = name.replaceAll("\\", "/");
    const assetId = soundManifest[normalized];
    if (typeof assetId === "number") {
      return assetId;
    }
    return null;
  }

  private async resolveNativeSource(name: string): Promise<AVPlaybackSource | null> {
    const normalized = name.replaceAll("\\", "/");
    const cached = this.nativeSourceCache.get(normalized);
    if (cached) {
      return cached;
    }

    const loading = this.nativeSourceLoading.get(normalized);
    if (loading) {
      return loading;
    }

    const loadPromise = (async () => {
      const directSource = this.resolveSource(normalized);
      if (!directSource) {
        return null;
      }
      if (typeof directSource !== "number") {
        this.nativeSourceCache.set(normalized, directSource);
        return directSource;
      }

      try {
        const assets = await Asset.loadAsync(directSource);
        const asset = assets[0] ?? Asset.fromModule(directSource);
        const resolvedSource: AVPlaybackSource =
          asset.localUri
            ? { uri: asset.localUri }
            : asset.uri
              ? { uri: asset.uri }
              : directSource;
        this.nativeSourceCache.set(normalized, resolvedSource);
        return resolvedSource;
      } catch (error) {
        console.warn(`MobileAudioManager: failed to resolve native asset for ${normalized}.`, error);
        this.nativeSourceCache.set(normalized, directSource);
        return directSource;
      } finally {
        this.nativeSourceLoading.delete(normalized);
      }
    })();

    this.nativeSourceLoading.set(normalized, loadPromise);
    return loadPromise;
  }

  private resolveNativeSourceSync(name: string): AVPlaybackSource | null {
    const normalized = name.replaceAll("\\", "/");
    return this.nativeSourceCache.get(normalized) ?? this.resolveSource(normalized);
  }

  private async ensureNativeAudioMode(): Promise<void> {
    if (Platform.OS === "web" || this.nativeAudioModeReady) {
      return;
    }
    if (this.nativeAudioModeLoading) {
      return this.nativeAudioModeLoading;
    }

    this.nativeAudioModeLoading = (Platform.OS === "android"
      ? this.ensureAndroidAudioMode()
      : ExpoAudio.setAudioModeAsync({
          allowsRecordingIOS: false,
          interruptionModeIOS: InterruptionModeIOS.MixWithOthers,
          playsInSilentModeIOS: true,
          staysActiveInBackground: true,
        })
    ).then(() => {
      this.nativeAudioModeReady = true;
    }).finally(() => {
      this.nativeAudioModeLoading = null;
    });

    return this.nativeAudioModeLoading;
  }

  private async ensureAndroidAudioMode(): Promise<void> {
    if (!exponentAV) {
      return;
    }

    await exponentAV.setAudioMode({
      interruptionModeAndroid: InterruptionModeAndroid.DuckOthers,
      shouldDuckAndroid: false,
      staysActiveInBackground: true,
    });
  }

  private async createNativeSound(
    source: AVPlaybackSource,
    status: AVPlaybackStatusToSet,
    onFinished?: () => void,
  ): Promise<ExpoAudio.Sound | null> {
    const sound = new ExpoAudio.Sound();
    if (onFinished) {
      sound.setOnPlaybackStatusUpdate((playbackStatus: AVPlaybackStatus) => {
        if (!playbackStatus.isLoaded || !playbackStatus.didJustFinish) {
          return;
        }
        sound.setOnPlaybackStatusUpdate(null);
        onFinished();
      });
    }

    try {
      await sound.loadAsync(source, status);
      this.nativeSoundVolumes.set(sound, status.volume ?? 1);
      return sound;
    } catch (error) {
      console.warn("MobileAudioManager: native sound load failed.", error);
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

  private setNativeSoundVolume(sound: ExpoAudio.Sound, volume: number): void {
    const clamped = Math.max(0, Math.min(1, volume));
    this.nativeSoundVolumes.set(sound, clamped);
    void sound.setVolumeAsync(clamped).catch(() => undefined);
  }

  private getTargetNativePlayerVolume(sound: ExpoAudio.Sound): number {
    return this.nativeSoundVolumes.get(sound) ?? 0;
  }

  private async resolveWebUri(name: string): Promise<string | null> {
    const normalized = name.replaceAll("\\", "/");
    const cached = this.webUriCache.get(normalized);
    if (cached) {
      return cached;
    }
    const assetId = (soundManifest as Record<string, unknown>)[normalized];
    if (!assetId) {
      console.warn(`MobileAudioManager: web asset not found for ${normalized}.`);
      return null;
    }

    try {
      if (typeof assetId === "string") {
        this.webUriCache.set(normalized, assetId);
        this.debug("web-uri-resolved-string", normalized);
        return assetId;
      }

      if (typeof assetId === "object") {
        const candidate = assetId as {
          default?: string | { uri?: string };
          src?: string;
          uri?: string;
        };
        const resolvedObjectUri =
          candidate.uri ||
          candidate.src ||
          (typeof candidate.default === "string" ? candidate.default : candidate.default?.uri) ||
          null;
        if (resolvedObjectUri) {
          this.webUriCache.set(normalized, resolvedObjectUri);
          this.debug("web-uri-resolved-object", normalized);
          return resolvedObjectUri;
        }
      }

      if (typeof assetId !== "number") {
        console.warn(`MobileAudioManager: unsupported web asset shape for ${normalized}.`);
        return null;
      }

      const assets = await Asset.loadAsync(assetId);
      const asset = assets[0] ?? Asset.fromModule(assetId);
      const resolved = asset.localUri ?? asset.uri ?? null;
      if (!resolved) {
        console.warn(`MobileAudioManager: resolved empty web uri for ${normalized}.`);
        return null;
      }
      this.webUriCache.set(normalized, resolved);
      return resolved;
    } catch (error) {
      console.warn(`MobileAudioManager: failed to resolve web uri for ${normalized}.`, error);
      return null;
    }
  }

  private cancelMusicFade(): void {
    if (this.musicFadeInterval) {
      clearInterval(this.musicFadeInterval);
      this.musicFadeInterval = null;
    }
  }

  private fadeRetiringMusicPlayers(step: number): void {
    for (const player of [...this.retiringMusicPlayers]) {
      const nextVolume = Math.max(0, this.getTargetNativePlayerVolume(player) - step);
      this.setNativeSoundVolume(player, nextVolume);
      if (nextVolume <= 0.001) {
        this.disposeNativeSound(player);
        this.retiringMusicPlayers.delete(player);
      }
    }
  }

  private clearRetiringMusicPlayers(): void {
    for (const player of this.retiringMusicPlayers) {
      this.disposeNativeSound(player);
    }
    this.retiringMusicPlayers.clear();
  }

  private async playNativeSound(
    name: string,
    options: { volume?: number; pitch?: number; pan?: number } = {},
  ): Promise<boolean> {
    const source = await this.resolveNativeSource(name);
    if (!source) {
      return false;
    }

    const sound = new ExpoAudio.Sound();
    const volume = Math.max(0, Math.min(1, options.volume ?? 1));
    const pitch = options.pitch && options.pitch > 0 ? options.pitch : 1;
    const pan = this.normalizePan(options.pan ?? 0);
    const initialStatus: AVPlaybackStatusToSet = {
      isLooping: false,
      progressUpdateIntervalMillis: 100,
      rate: pitch,
      shouldCorrectPitch: true,
      shouldPlay: true,
      volume,
      ...(Platform.OS === "android"
        ? {
            androidImplementation: "MediaPlayer" as const,
            audioPan: pan,
          }
        : {}),
    };

    sound.setOnPlaybackStatusUpdate((status: AVPlaybackStatus) => {
      if (!status.isLoaded) {
        return;
      }
      if (status.didJustFinish) {
        sound.setOnPlaybackStatusUpdate(null);
        this.sfxPlayers.delete(sound);
        this.nativeSoundVolumes.delete(sound);
        void sound.unloadAsync();
      }
    });

    try {
      await sound.loadAsync(source, initialStatus);
      this.nativeSoundVolumes.set(sound, volume);
      this.sfxPlayers.add(sound);
      return true;
    } catch (error) {
      console.warn("MobileAudioManager: native sound playback failed.", error);
      sound.setOnPlaybackStatusUpdate(null);
      void sound.unloadAsync().catch(() => undefined);
      return false;
    }
  }

  private async playWebSound(
    name: string,
    options: { volume?: number; pitch?: number; pan?: number } = {},
  ): Promise<boolean> {
    const context = await this.ensureWebAudioReady();
    const bus = this.webSfxBus;
    if (!context || !bus) {
      console.warn(`MobileAudioManager: web sound context unavailable for ${name}.`);
      return false;
    }

    const buffer = await this.loadWebBuffer(name);
    if (!buffer) {
      console.warn(`MobileAudioManager: web sound buffer unavailable for ${name}.`);
      return false;
    }

    const source = context.createBufferSource();
    source.buffer = buffer;
    source.playbackRate.value = options.pitch && options.pitch > 0 ? options.pitch : 1;

    const gain = context.createGain();
    gain.gain.value = Math.max(0, Math.min(1, options.volume ?? 1));

    const panner = typeof context.createStereoPanner === "function"
      ? context.createStereoPanner()
      : null;
    if (panner) {
      panner.pan.value = this.normalizePan(options.pan ?? 0);
      source.connect(panner);
      panner.connect(gain);
    } else {
      source.connect(gain);
    }

    gain.connect(bus);
    const handle: WebSfxHandle = { gain, panner, source };
    this.webSfxRefs.add(handle);
    source.onended = () => {
      this.disposeWebSfx(handle);
    };
    source.start(0);
    this.debug("play-sound-started", name);
    return true;
  }

  private async playWebMusic(name: string, looping: boolean): Promise<boolean> {
    if (this.musicVolume <= 0) {
      this.webPendingMusicRequest = null;
      this.stopWebMusic(false);
      return false;
    }
    const context = await this.ensureWebAudioReady();
    if (!context) {
      console.warn(`MobileAudioManager: web music context unavailable for ${name}.`);
      return false;
    }

    if (this.webMusicPlayer?.sourceKey === name) {
      this.webMusicPlayer.element.loop = looping;
      this.cancelMusicFade();
      try {
        await this.webMusicPlayer.element.play();
        return true;
      } catch (error) {
        console.warn("MobileAudioManager: web music resume failed.", error);
        return false;
      }
    }

    const nextPlayer = await this.createWebStream(name, looping, "music");
    if (!nextPlayer) {
      return false;
    }

    nextPlayer.gainNode.gain.value = 0;
    try {
      await nextPlayer.element.play();
    } catch (error) {
      console.warn("MobileAudioManager: web music playback failed.", error);
      this.webPendingMusicRequest = { looping, name };
      this.disposeWebStream(nextPlayer);
      return false;
    }

    const previousMusicPlayer = this.webMusicPlayer;
    this.webMusicPlayer = nextPlayer;
    const transitionId = ++this.musicTransitionId;
    if (previousMusicPlayer) {
      this.webRetiringMusicPlayers.add(previousMusicPlayer);
    }

    this.cancelMusicFade();
    this.musicFadeInterval = setInterval(() => {
      if (transitionId !== this.musicTransitionId) {
        this.cancelMusicFade();
        return;
      }

      const step = 0.05;
      const nextVolume = Math.min(1, nextPlayer.gainNode.gain.value + step);
      nextPlayer.gainNode.gain.value = nextVolume;

      for (const player of [...this.webRetiringMusicPlayers]) {
        const faded = Math.max(0, player.gainNode.gain.value - step);
        player.gainNode.gain.value = faded;
        if (faded <= 0.001) {
          this.disposeWebStream(player);
          this.webRetiringMusicPlayers.delete(player);
        }
      }

      if (nextVolume >= 1 && this.webRetiringMusicPlayers.size === 0) {
        this.cancelMusicFade();
      }
    }, 50);

    return true;
  }

  private stopWebMusic(fade: boolean): void {
    this.webPendingMusicRequest = null;
    if (!this.webMusicPlayer) {
      return;
    }

    const current = this.webMusicPlayer;
    this.webMusicPlayer = null;
    ++this.musicTransitionId;

    if (!fade) {
      this.cancelMusicFade();
      this.disposeWebStream(current);
      for (const player of this.webRetiringMusicPlayers) {
        this.disposeWebStream(player);
      }
      this.webRetiringMusicPlayers.clear();
      return;
    }

    this.webRetiringMusicPlayers.add(current);
    this.cancelMusicFade();
    this.musicFadeInterval = setInterval(() => {
      for (const player of [...this.webRetiringMusicPlayers]) {
        const nextVolume = Math.max(0, player.gainNode.gain.value - 0.05);
        player.gainNode.gain.value = nextVolume;
        if (nextVolume <= 0.001) {
          this.disposeWebStream(player);
          this.webRetiringMusicPlayers.delete(player);
        }
      }
      if (this.webRetiringMusicPlayers.size === 0) {
        this.cancelMusicFade();
      }
    }, 50);
  }

  private async playWebAmbience(loop: string, intro = "", outro = ""): Promise<boolean> {
    if (this.ambienceVolume <= 0) {
      this.webPendingAmbienceRequest = null;
      this.stopWebAmbience(true);
      return false;
    }
    const context = await this.ensureWebAudioReady();
    if (!context) {
      console.warn(`MobileAudioManager: web ambience context unavailable for ${loop}.`);
      return false;
    }

    this.stopWebAmbience(true);
    const playbackId = ++this.ambiencePlaybackId;
    this.ambienceOutroKey = outro || null;

    const startLoop = async (): Promise<boolean> => {
      if (playbackId !== this.ambiencePlaybackId) {
        return false;
      }
      const loopPlayer = await this.createWebStream(loop, true, "ambience");
      if (!loopPlayer) {
        return false;
      }
      this.webAmbienceLoopPlayer = loopPlayer;
      try {
        await loopPlayer.element.play();
        this.ambiencePhase = "loop";
        return true;
      } catch (error) {
        console.warn("MobileAudioManager: web ambience loop playback failed.", error);
        this.webPendingAmbienceRequest = { intro, loop, outro };
        this.disposeWebStream(loopPlayer);
        this.webAmbienceLoopPlayer = null;
        this.ambiencePhase = "idle";
        return false;
      }
    };

    if (intro) {
      const introPlayer = await this.createWebStream(intro, false, "ambience");
      if (introPlayer) {
        this.webAmbienceIntroPlayer = introPlayer;
        this.ambiencePhase = "intro";
        introPlayer.element.onended = () => {
          this.disposeWebStream(introPlayer);
          this.webAmbienceIntroPlayer = null;
          void startLoop();
        };
        try {
          await introPlayer.element.play();
          return true;
        } catch (error) {
          console.warn("MobileAudioManager: web ambience intro playback failed.", error);
          this.webPendingAmbienceRequest = { intro, loop, outro };
          this.disposeWebStream(introPlayer);
          this.webAmbienceIntroPlayer = null;
          this.ambiencePhase = "idle";
          return false;
        }
      }
    }

    return startLoop();
  }

  private stopWebAmbience(force: boolean): void {
    this.webPendingAmbienceRequest = null;
    const phaseAtStop = this.ambiencePhase;
    ++this.ambiencePlaybackId;
    if (this.webAmbienceIntroPlayer) {
      this.disposeWebStream(this.webAmbienceIntroPlayer);
      this.webAmbienceIntroPlayer = null;
    }

    if (this.webAmbienceLoopPlayer) {
      this.disposeWebStream(this.webAmbienceLoopPlayer);
      this.webAmbienceLoopPlayer = null;
    }

    if (this.webAmbienceOutroPlayer) {
      if (!force && phaseAtStop === "outro") {
        return;
      }
      this.disposeWebStream(this.webAmbienceOutroPlayer);
      this.webAmbienceOutroPlayer = null;
    }

    this.ambiencePhase = "idle";

    if (!force && phaseAtStop === "loop" && this.ambienceOutroKey) {
      void this.createWebStream(this.ambienceOutroKey, false, "ambience").then((outroPlayer) => {
        if (!outroPlayer) {
          return;
        }
        this.webAmbienceOutroPlayer = outroPlayer;
        this.ambiencePhase = "outro";
        outroPlayer.element.onended = () => {
          this.disposeWebStream(outroPlayer);
          if (this.webAmbienceOutroPlayer === outroPlayer) {
            this.webAmbienceOutroPlayer = null;
          }
          this.ambiencePhase = "idle";
        };
        void outroPlayer.element.play().catch((error) => {
          console.warn("MobileAudioManager: web ambience outro playback failed.", error);
          this.disposeWebStream(outroPlayer);
          if (this.webAmbienceOutroPlayer === outroPlayer) {
            this.webAmbienceOutroPlayer = null;
          }
          this.ambiencePhase = "idle";
        });
      });
    }
  }

  private async ensureWebAudioReady(): Promise<AudioContext | null> {
    if (typeof window === "undefined") {
      return null;
    }

    if (!this.webAudioContext) {
      const AudioContextClass =
        window.AudioContext ||
        (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (!AudioContextClass) {
        console.warn("MobileAudioManager: browser does not provide AudioContext.");
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
      this.webSfxBus.gain.value = 1;
      this.webAmbienceBus.gain.value = this.ambienceVolume;
    }

    if (this.webAudioContext.state === "suspended") {
      try {
        await this.webAudioContext.resume();
      } catch (error) {
        console.warn("MobileAudioManager: failed to resume AudioContext.", error);
      }
    }

    return this.webAudioContext;
  }

  private async loadWebBuffer(name: string): Promise<AudioBuffer | null> {
    const normalized = name.replaceAll("\\", "/");
    const cached = this.webBufferCache.get(normalized);
    if (cached) {
      return cached;
    }

    const loading = this.webBufferLoading.get(normalized);
    if (loading) {
      return loading;
    }

    const loadPromise = (async () => {
      const context = await this.ensureWebAudioReady();
      const uri = await this.resolveWebUri(normalized);
      if (!context || !uri) {
        return null;
      }

      try {
        const response = await fetch(uri);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const arrayBuffer = await response.arrayBuffer();
        const decoded = await context.decodeAudioData(arrayBuffer.slice(0));
        this.webBufferCache.set(normalized, decoded);
        this.debug("web-buffer-loaded", normalized);
        return decoded;
      } catch (error) {
        console.warn(`MobileAudioManager: failed to load web sound ${normalized}.`, error);
        return null;
      } finally {
        this.webBufferLoading.delete(normalized);
      }
    })();

    this.webBufferLoading.set(normalized, loadPromise);
    return loadPromise;
  }

  private async createWebStream(
    name: string,
    looping: boolean,
    bus: WebBusName,
  ): Promise<ManagedWebStream | null> {
    const context = await this.ensureWebAudioReady();
    const uri = await this.resolveWebUri(name);
    const busNode = bus === "music" ? this.webMusicBus : this.webAmbienceBus;
    if (!context || !uri || !busNode) {
      return null;
    }

    const element = new Audio(uri);
    element.loop = looping;
    element.preload = "auto";

    try {
      const sourceNode = context.createMediaElementSource(element);
      const gainNode = context.createGain();
      gainNode.gain.value = 1;
      sourceNode.connect(gainNode);
      gainNode.connect(busNode);
      return {
        element,
        gainNode,
        sourceKey: name,
        sourceNode,
      };
    } catch (error) {
      console.warn(`MobileAudioManager: failed to create web stream for ${name}.`, error);
      return null;
    }
  }

  private disposeWebStream(stream: ManagedWebStream): void {
    stream.element.pause();
    stream.element.currentTime = 0;
    stream.element.onended = null;
    try {
      stream.sourceNode.disconnect();
    } catch {
      // Ignore double-disconnect cleanup on ended/stop races.
    }
    try {
      stream.gainNode.disconnect();
    } catch {
      // Ignore double-disconnect cleanup on ended/stop races.
    }
  }

  private disposeWebSfx(handle: WebSfxHandle): void {
    try {
      handle.source.disconnect();
    } catch {
      // Ignore double-disconnect cleanup on ended/stop races.
    }
    try {
      handle.gain.disconnect();
    } catch {
      // Ignore double-disconnect cleanup on ended/stop races.
    }
    try {
      handle.panner?.disconnect();
    } catch {
      // Ignore double-disconnect cleanup on ended/stop races.
    }
    this.webSfxRefs.delete(handle);
  }

  private normalizePan(value: number): number {
    if (!Number.isFinite(value)) {
      return 0;
    }
    if (Math.abs(value) > 1) {
      return Math.max(-1, Math.min(1, value / 100));
    }
    return Math.max(-1, Math.min(1, value));
  }

  private debug(event: string, value: string): void {
    if (!ENABLE_CLIENT_DEBUG_LOGS || typeof console === "undefined") {
      return;
    }
    console.info(DEBUG_PREFIX, event, value || "");
  }
}
