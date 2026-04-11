import {
  createAudioPlayer,
  setAudioModeAsync,
  type AudioPlayer,
  type AudioSource,
  type AudioStatus,
} from "expo-audio";
import type { AVPlaybackSource, AVPlaybackStatus } from "expo-av";
import { Asset } from "expo-asset";
import { Platform } from "react-native";

import { soundManifest } from "../generated/soundManifest";

type ManagedPlayer = {
  player: AudioPlayer;
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

const DEBUG_PREFIX = "PLAYAURAL_DEBUG Audio";

export class MobileAudioManager {
  private initialized = false;
  private musicPlayer: ManagedPlayer | null = null;
  private ambienceIntroPlayer: ManagedPlayer | null = null;
  private ambienceLoopPlayer: ManagedPlayer | null = null;
  private ambienceOutroPlayer: ManagedPlayer | null = null;
  private ambienceOutroKey: string | null = null;
  private ambiencePlaybackId = 0;
  private sfxPlayers = new Set<AudioPlayer>();
  private retiringMusicPlayers = new Set<AudioPlayer>();
  private musicVolume = 0.2;
  private ambienceVolume = 0.3;
  private musicTransitionId = 0;
  private musicFadeInterval: ReturnType<typeof setInterval> | null = null;
  private nativeSfxPlayers = new Set<unknown>();
  private nativeSourceCache = new Map<string, AudioSource>();
  private nativeSourceLoading = new Map<string, Promise<AudioSource | null>>();
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
      await setAudioModeAsync({
        interruptionMode: "mixWithOthers",
        interruptionModeAndroid: "duckOthers",
        playsInSilentMode: true,
        shouldPlayInBackground: true,
        shouldRouteThroughEarpiece: false,
      });

      const ExpoAv = await import("expo-av");
      await ExpoAv.Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        interruptionModeAndroid: ExpoAv.InterruptionModeAndroid.DuckOthers,
        interruptionModeIOS: ExpoAv.InterruptionModeIOS.MixWithOthers,
        playThroughEarpieceAndroid: false,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: false,
        staysActiveInBackground: true,
      });
    }

    this.debug("initialize", Platform.OS);
    this.initialized = true;
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
      this.musicPlayer.player.volume = this.musicVolume;
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
      this.ambienceLoopPlayer.player.volume = this.ambienceVolume;
    }
    if (this.ambienceIntroPlayer) {
      this.ambienceIntroPlayer.player.volume = this.ambienceVolume;
    }
    if (this.ambienceOutroPlayer) {
      this.ambienceOutroPlayer.player.volume = this.ambienceVolume;
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

  async playSound(
    name: string,
    options: { volume?: number; pitch?: number; pan?: number } = {},
  ): Promise<boolean> {
    this.debug("play-sound-request", name);
    if (Platform.OS === "web") {
      return this.playWebSound(name, options);
    }

    await this.initialize();
    if (Platform.OS === "android") {
      return this.playNativePannedSound(name, options);
    }

    const source = await this.resolveNativeSource(name) as AVPlaybackSource | null;
    if (!source) {
      return false;
    }

    const player = createAudioPlayer(source, 80);
    player.volume = Math.max(0, Math.min(1, options.volume ?? 1));
    if (options.pitch && options.pitch > 0) {
      player.setPlaybackRate(options.pitch);
    }
    const subscription = player.addListener("playbackStatusUpdate", (status: AudioStatus) => {
      if (status.didJustFinish) {
        subscription.remove();
        this.sfxPlayers.delete(player);
        player.remove();
      }
    });
    this.sfxPlayers.add(player);
    player.play();
    return true;
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
    const source = await this.resolveNativeSource(name);
    if (!source) {
      return false;
    }
    if (this.musicPlayer?.sourceKey === name) {
      this.musicPlayer.player.loop = looping;
      this.cancelMusicFade();
      this.musicPlayer.player.volume = this.musicVolume;
      this.musicPlayer.player.play();
      return true;
    }

    const player = createAudioPlayer(source, 250);
    player.loop = looping;
    player.volume = 0;
    player.play();
    const nextMusicPlayer = { player, sourceKey: name };
    const previousMusicPlayer = this.musicPlayer;
    this.musicPlayer = nextMusicPlayer;
    const transitionId = ++this.musicTransitionId;
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
      const nextVolume = Math.min(this.musicVolume, nextMusicPlayer.player.volume + step);
      nextMusicPlayer.player.volume = nextVolume;

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
      return;
    }

    const current = this.musicPlayer;
    this.musicPlayer = null;
    ++this.musicTransitionId;
    if (!fade) {
      this.cancelMusicFade();
      current.player.pause();
      current.player.remove();
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
      const loopPlayer = createAudioPlayer(loopSource, 250);
      loopPlayer.loop = true;
      loopPlayer.volume = this.ambienceVolume;
      loopPlayer.play();
      this.ambienceLoopPlayer = { player: loopPlayer, sourceKey: loop };
    };

    const introSource = intro ? await this.resolveNativeSource(intro) : null;
    if (introSource) {
      const introPlayer = createAudioPlayer(introSource, 80);
      introPlayer.volume = this.ambienceVolume;
      const subscription = introPlayer.addListener("playbackStatusUpdate", (status: AudioStatus) => {
        if (status.didJustFinish) {
          subscription.remove();
          introPlayer.remove();
          this.ambienceIntroPlayer = null;
          startLoop();
        }
      });
      this.ambienceIntroPlayer = { player: introPlayer, sourceKey: intro };
      introPlayer.play();
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

    ++this.ambiencePlaybackId;

    if (this.ambienceIntroPlayer) {
      this.ambienceIntroPlayer.player.pause();
      this.ambienceIntroPlayer.player.remove();
      this.ambienceIntroPlayer = null;
    }

    if (this.ambienceLoopPlayer) {
      this.ambienceLoopPlayer.player.pause();
      this.ambienceLoopPlayer.player.remove();
      this.ambienceLoopPlayer = null;
    }

    if (this.ambienceOutroPlayer) {
      this.ambienceOutroPlayer.player.pause();
      this.ambienceOutroPlayer.player.remove();
      this.ambienceOutroPlayer = null;
    }

    if (!force && this.ambienceOutroKey) {
      if (this.ambienceVolume <= 0) {
        this.ambienceOutroKey = null;
        return;
      }
      const outroSource = this.resolveNativeSourceSync(this.ambienceOutroKey);
      if (!outroSource) {
        return;
      }
      const outroPlayer = createAudioPlayer(outroSource, 80);
      outroPlayer.volume = this.ambienceVolume;
      const subscription = outroPlayer.addListener("playbackStatusUpdate", (status: AudioStatus) => {
        if (status.didJustFinish) {
          subscription.remove();
          outroPlayer.remove();
          if (this.ambienceOutroPlayer?.player === outroPlayer) {
            this.ambienceOutroPlayer = null;
          }
        }
      });
      this.ambienceOutroPlayer = { player: outroPlayer, sourceKey: this.ambienceOutroKey };
      outroPlayer.play();
    }
  }

  private resolveSource(name: string): AudioSource | null {
    const normalized = name.replaceAll("\\", "/");
    const assetId = soundManifest[normalized];
    if (typeof assetId === "number") {
      return assetId;
    }
    return null;
  }

  private async resolveNativeSource(name: string): Promise<AudioSource | null> {
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
        const resolvedSource: AudioSource =
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

  private resolveNativeSourceSync(name: string): AudioSource | null {
    const normalized = name.replaceAll("\\", "/");
    return this.nativeSourceCache.get(normalized) ?? this.resolveSource(normalized);
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
      const nextVolume = Math.max(0, player.volume - step);
      player.volume = nextVolume;
      if (nextVolume <= 0.001) {
        player.pause();
        player.remove();
        this.retiringMusicPlayers.delete(player);
      }
    }
  }

  private clearRetiringMusicPlayers(): void {
    for (const player of this.retiringMusicPlayers) {
      player.pause();
      player.remove();
    }
    this.retiringMusicPlayers.clear();
  }

  private async playNativePannedSound(
    name: string,
    options: { volume?: number; pitch?: number; pan?: number } = {},
  ): Promise<boolean> {
    const source = await this.resolveNativeSource(name) as AVPlaybackSource | null;
    if (!source) {
      return false;
    }

    const { Audio: ExpoAvAudio } = await import("expo-av");
    const sound = new ExpoAvAudio.Sound();
    const volume = Math.max(0, Math.min(1, options.volume ?? 1));
    const pitch = options.pitch && options.pitch > 0 ? options.pitch : 1;
    const pan = this.normalizePan(options.pan ?? 0);

    sound.setOnPlaybackStatusUpdate((status: AVPlaybackStatus) => {
      if (!status.isLoaded) {
        return;
      }
      if (status.didJustFinish) {
        sound.setOnPlaybackStatusUpdate(null);
        this.nativeSfxPlayers.delete(sound);
        void sound.unloadAsync();
      }
    });

    try {
      await sound.loadAsync(source, {
        androidImplementation: "MediaPlayer",
        audioPan: pan,
        isLooping: false,
        progressUpdateIntervalMillis: 100,
        rate: pitch,
        shouldCorrectPitch: true,
        shouldPlay: true,
        volume,
      });
      this.nativeSfxPlayers.add(sound);
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
        return true;
      } catch (error) {
        console.warn("MobileAudioManager: web ambience loop playback failed.", error);
        this.webPendingAmbienceRequest = { intro, loop, outro };
        this.disposeWebStream(loopPlayer);
        this.webAmbienceLoopPlayer = null;
        return false;
      }
    };

    if (intro) {
      const introPlayer = await this.createWebStream(intro, false, "ambience");
      if (introPlayer) {
        this.webAmbienceIntroPlayer = introPlayer;
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
          return false;
        }
      }
    }

    return startLoop();
  }

  private stopWebAmbience(force: boolean): void {
    this.webPendingAmbienceRequest = null;
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
      this.disposeWebStream(this.webAmbienceOutroPlayer);
      this.webAmbienceOutroPlayer = null;
    }

    if (!force && this.ambienceOutroKey) {
      void this.createWebStream(this.ambienceOutroKey, false, "ambience").then((outroPlayer) => {
        if (!outroPlayer) {
          return;
        }
        this.webAmbienceOutroPlayer = outroPlayer;
        outroPlayer.element.onended = () => {
          this.disposeWebStream(outroPlayer);
          if (this.webAmbienceOutroPlayer === outroPlayer) {
            this.webAmbienceOutroPlayer = null;
          }
        };
        void outroPlayer.element.play().catch((error) => {
          console.warn("MobileAudioManager: web ambience outro playback failed.", error);
          this.disposeWebStream(outroPlayer);
          if (this.webAmbienceOutroPlayer === outroPlayer) {
            this.webAmbienceOutroPlayer = null;
          }
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
    if (typeof console === "undefined") {
      return;
    }
    console.info(DEBUG_PREFIX, event, value || "");
  }
}
