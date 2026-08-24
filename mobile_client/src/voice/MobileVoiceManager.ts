import { Platform } from "react-native";
import {
  Room,
  RoomEvent,
  Track,
  type RemoteParticipant,
  type RemoteTrackPublication,
} from "livekit-client";
import type { AppleAudioConfiguration } from "@livekit/react-native";
import type { VoiceJoinInfoPacket } from "../network/packets";

type NativeLiveKitModule = typeof import("@livekit/react-native");
type VoiceBootstrapGlobal = typeof globalThis & {
  __PLAYAURAL_NATIVE_VOICE_BOOTSTRAP_ERROR__?: string;
};

export type MobileVoiceConnectionState = "connected" | "connecting" | "disconnected";

type VoiceCallbacks = {
  onConnected?: () => void;
  onDisconnect?: (reason: "connection_lost") => void;
  onMicBusy?: (busy: boolean) => void;
  onMicState?: (enabled: boolean) => void;
  onState?: (state: MobileVoiceConnectionState) => void;
  onStatus?: (messageKeyOrText: string, speak: boolean) => void;
};

export class MobileVoiceManager {
  private callbacks: VoiceCallbacks = {};
  private room: Room | null = null;
  private state: MobileVoiceConnectionState = "disconnected";
  private micEnabled = false;
  private micBusy = false;
  private connected = false;
  private intent = 0;
  private nativeAudioSessionStarted = false;
  private lifecycleTail: Promise<void> = Promise.resolve();
  private expectedDisconnectRooms = new WeakSet<Room>();
  private remoteAudioElements = new Map<string, HTMLAudioElement>();
  private webAudioContainer: HTMLDivElement | null = null;
  // Voice volume: 0.1-1.0, applied to all remote audio elements
  private _voiceVolume = 0.8;

  setCallbacks(callbacks: VoiceCallbacks): void {
    this.callbacks = callbacks;
  }

  get supported(): boolean {
    if (Platform.OS === "web") {
      return true;
    }
    return this.getNativeLiveKitModule() !== null;
  }

  get connectionState(): MobileVoiceConnectionState {
    return this.state;
  }

  get microphoneEnabled(): boolean {
    return this.micEnabled;
  }

  join(packet: VoiceJoinInfoPacket): void {
    const intent = this.nextIntent();
    this.queueLifecycle(() => this.joinInternal(packet, intent));
  }

  leave(notify = true): void {
    this.nextIntent();
    this.queueLifecycle(() => this.leaveInternal(notify));
  }

  setMicrophoneEnabled(enabled: boolean): void {
    if (this.micBusy) {
      return;
    }
    this.setMicBusy(true);
    const intent = this.intent;
    this.queueLifecycle(() => this.setMicrophoneEnabledInternal(enabled, intent));
  }

  configureIdleAudioProfile(): void {
    this.queueLifecycle(() => this.configureIdleAudioProfileInternal());
  }

  refreshAudioSession(): void {
    this.queueLifecycle(() => this.refreshAudioSessionInternal());
  }

  shutdown(): void {
    this.nextIntent();
    this.queueLifecycle(() => this.leaveInternal(false));
  }

  setVoiceVolume(volume: number): void {
    // Clamp to 0.1-1.0 range.
    const clamped = Number.isFinite(volume) ? Math.max(0.1, Math.min(1.0, volume)) : 0.8;
    this._voiceVolume = clamped;
    // Apply to all currently playing remote audio elements
    this.remoteAudioElements.forEach((element) => {
      element.volume = clamped;
    });
  }

  private nextIntent(): number {
    this.intent += 1;
    return this.intent;
  }

  private queueLifecycle(operation: () => Promise<void>): void {
    const run = this.lifecycleTail.then(operation, operation);
    this.lifecycleTail = run.catch(() => undefined);
  }

  private isCurrentIntent(intent: number): boolean {
    return this.intent === intent;
  }

  private setState(state: MobileVoiceConnectionState): void {
    this.state = state;
    this.callbacks.onState?.(state);
  }

  private setMicState(enabled: boolean): void {
    this.micEnabled = enabled;
    this.callbacks.onMicState?.(enabled);
  }

  private setMicBusy(busy: boolean): void {
    if (this.micBusy === busy) {
      return;
    }
    this.micBusy = busy;
    this.callbacks.onMicBusy?.(busy);
  }

  private async joinInternal(packet: VoiceJoinInfoPacket, intent: number): Promise<void> {
    if (!this.supported) {
      this.callbacks.onStatus?.("voice-chat-sdk-missing", true);
      this.setState("disconnected");
      return;
    }

    await this.leaveInternal(false);
    if (!this.isCurrentIntent(intent)) {
      return;
    }

    this.setState("connecting");
    try {
      await this.startNativeAudioSession();
      const room = new Room({
        adaptiveStream: false,
        dynacast: false,
      });
      this.bindRoomEvents(room);
      this.room = room;
      await room.connect(packet.url, packet.token, {
        autoSubscribe: true,
      });
      if (!this.isCurrentIntent(intent)) {
        await this.leaveInternal(false);
        return;
      }

      if (Platform.OS === "web") {
        await room.startAudio().catch(() => undefined);
        this.attachExistingWebTracks(room);
      }

      this.connected = true;
      this.setMicState(false);
      this.setState("connected");
      this.callbacks.onConnected?.();
      this.callbacks.onStatus?.("voice-chat-listen-only", true);
    } catch {
      await this.leaveInternal(false);
      if (this.isCurrentIntent(intent)) {
        this.callbacks.onStatus?.("voice-chat-connect-failed", true);
        this.setState("disconnected");
      }
    }
  }

  private bindRoomEvents(room: Room): void {
    room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
      if (this.room !== room) {
        return;
      }
      if (Platform.OS === "web" && track.kind === Track.Kind.Audio) {
        this.attachWebTrack(track as Track, publication, participant);
      }
    });

    room.on(RoomEvent.TrackUnsubscribed, (track, publication) => {
      if (this.room !== room) {
        return;
      }
      if (Platform.OS === "web" && track.kind === Track.Kind.Audio) {
        this.detachWebTrack(publication);
      }
    });

    room.on(RoomEvent.Disconnected, () => {
      this.queueLifecycle(() => this.handleRoomDisconnected(room));
    });

    room.on(RoomEvent.MediaDevicesError, () => {
      if (this.room !== room) {
        return;
      }
      this.callbacks.onStatus?.("voice-chat-mic-denied", true);
    });
  }

  private async handleRoomDisconnected(room: Room): Promise<void> {
    const expectedDisconnect = this.expectedDisconnectRooms.has(room);
    this.expectedDisconnectRooms.delete(room);
    if (this.room !== room) {
      return;
    }

    const wasConnected = this.connected;
    this.connected = false;
    this.cleanupWebAudioElements();
    this.room = null;
    this.setMicBusy(false);
    this.setMicState(false);
    this.setState("disconnected");
    await this.stopNativeAudioSession();
    await this.configureIdleAudioProfileInternal();
    if (wasConnected && !expectedDisconnect) {
      this.callbacks.onDisconnect?.("connection_lost");
    }
  }

  private async setMicrophoneEnabledInternal(
    enabled: boolean,
    intent: number,
  ): Promise<void> {
    try {
      if (!this.isCurrentIntent(intent)) {
        return;
      }
      if (!this.room || !this.connected) {
        this.callbacks.onStatus?.("voice-chat-not-connected", true);
        return;
      }
      if (enabled === this.micEnabled) {
        return;
      }

      const room = this.room;
      if (enabled) {
        await this.applyNativeMediaAudioProfile(true);
      }
      if (!this.isCurrentIntent(intent) || this.room !== room) {
        await this.applyNativeMediaAudioProfile(false);
        return;
      }

      await room.localParticipant.setMicrophoneEnabled(enabled);
      if (!this.isCurrentIntent(intent) || this.room !== room || !this.connected) {
        if (enabled) {
          await room.localParticipant.setMicrophoneEnabled(false).catch(() => undefined);
        }
        await this.applyNativeMediaAudioProfile(false);
        return;
      }

      // Reassert the media policy after WebRTC creates or removes its input
      // track so no dependency callback can leave a call-oriented mode active.
      await this.applyNativeMediaAudioProfile(enabled);
      this.setMicState(enabled);
      this.callbacks.onStatus?.(enabled ? "voice-chat-mic-on" : "voice-chat-mic-off", true);
    } catch {
      this.setMicState(false);
      await this.applyNativeMediaAudioProfile(false).catch(() => undefined);
      this.callbacks.onStatus?.("voice-chat-mic-denied", true);
    } finally {
      this.setMicBusy(false);
    }
  }

  private async leaveInternal(notify: boolean): Promise<void> {
    const room = this.room;
    this.room = null;

    if (room) {
      this.expectedDisconnectRooms.add(room);
      try {
        await room.localParticipant.setMicrophoneEnabled(false);
      } catch {
        // Ignore microphone cleanup failures during leave.
      }
      try {
        await room.disconnect();
      } catch {
        // Ignore disconnect races during leave.
      }
    }

    this.connected = false;
    this.setMicBusy(false);
    this.cleanupWebAudioElements();
    await this.stopNativeAudioSession();
    await this.configureIdleAudioProfileInternal();
    this.setMicState(false);
    this.setState("disconnected");
    if (notify) {
      this.callbacks.onStatus?.("voice-chat-left", true);
    }
  }

  private attachExistingWebTracks(room: Room): void {
    room.remoteParticipants.forEach((participant) => {
      participant.trackPublications.forEach((publication) => {
        const track = publication.track;
        if (track && track.kind === Track.Kind.Audio) {
          this.attachWebTrack(track as Track, publication, participant);
        }
      });
    });
  }

  private attachWebTrack(
    track: Track,
    publication: RemoteTrackPublication,
    participant: RemoteParticipant,
  ): void {
    if (Platform.OS !== "web" || typeof document === "undefined" || typeof (track as Track & { attach?: () => HTMLMediaElement }).attach !== "function") {
      return;
    }

    const key = publication.trackSid || track.sid || participant.identity;
    if (!key || this.remoteAudioElements.has(key)) {
      return;
    }

    const element = (track as Track & { attach: () => HTMLMediaElement }).attach();
    if (!(element instanceof HTMLAudioElement)) {
      return;
    }

    element.autoplay = true;
    element.controls = false;
    element.hidden = true;
    element.setAttribute("aria-hidden", "true");
    element.volume = this._voiceVolume;
    this.ensureWebAudioContainer().appendChild(element);
    const playResult = element.play();
    if (playResult && typeof playResult.catch === "function") {
      playResult.catch(() => undefined);
    }
    this.remoteAudioElements.set(key, element);
  }

  private detachWebTrack(publication: RemoteTrackPublication): void {
    const key = publication.trackSid;
    if (!key) {
      return;
    }
    const element = this.remoteAudioElements.get(key);
    if (element?.parentNode) {
      element.parentNode.removeChild(element);
    }
    this.remoteAudioElements.delete(key);
  }

  private cleanupWebAudioElements(): void {
    this.remoteAudioElements.forEach((element) => {
      if (element.parentNode) {
        element.parentNode.removeChild(element);
      }
    });
    this.remoteAudioElements.clear();
    if (this.webAudioContainer?.parentNode) {
      this.webAudioContainer.parentNode.removeChild(this.webAudioContainer);
    }
    this.webAudioContainer = null;
  }

  private ensureWebAudioContainer(): HTMLDivElement {
    if (this.webAudioContainer) {
      return this.webAudioContainer;
    }
    const container = document.createElement("div");
    container.hidden = true;
    container.setAttribute("aria-hidden", "true");
    document.body.appendChild(container);
    this.webAudioContainer = container;
    return container;
  }

  private getNativeLiveKitModule(): NativeLiveKitModule | null {
    if (Platform.OS === "web") {
      return null;
    }
    if ((globalThis as VoiceBootstrapGlobal).__PLAYAURAL_NATIVE_VOICE_BOOTSTRAP_ERROR__) {
      return null;
    }
    try {
      return require("@livekit/react-native") as NativeLiveKitModule;
    } catch {
      return null;
    }
  }

  private async startNativeAudioSession(): Promise<void> {
    const liveKitNative = this.getNativeLiveKitModule();
    if (!liveKitNative || this.nativeAudioSessionStarted) {
      return;
    }

    await this.applyNativeMediaAudioProfile(false, liveKitNative);
    await liveKitNative.AudioSession.startAudioSession();
    this.nativeAudioSessionStarted = true;
  }

  private async stopNativeAudioSession(): Promise<void> {
    const liveKitNative = this.getNativeLiveKitModule();
    if (!liveKitNative || !this.nativeAudioSessionStarted) {
      return;
    }

    try {
      await liveKitNative.AudioSession.stopAudioSession();
    } finally {
      this.nativeAudioSessionStarted = false;
    }
  }

  private async refreshAudioSessionInternal(): Promise<void> {
    const liveKitNative = this.getNativeLiveKitModule();
    if (!liveKitNative || !this.room || Platform.OS === "web") {
      return;
    }

    try {
      await this.applyNativeMediaAudioProfile(this.micEnabled, liveKitNative);
      await liveKitNative.AudioSession.startAudioSession();
      this.nativeAudioSessionStarted = true;
    } catch {
      // Ignore audio-session refresh failures; the existing room state remains authoritative.
    }
  }

  private async configureIdleAudioProfileInternal(): Promise<void> {
    const liveKitNative = this.getNativeLiveKitModule();
    if (!liveKitNative || Platform.OS === "web") {
      return;
    }

    try {
      await this.applyNativeMediaAudioProfile(false, liveKitNative);
    } catch {
      // Ignore idle-profile restore failures; they should not block gameplay audio.
    }
  }

  private async applyNativeMediaAudioProfile(
    microphoneEnabled: boolean,
    liveKitNative = this.getNativeLiveKitModule(),
  ): Promise<void> {
    if (!liveKitNative || Platform.OS === "web") {
      return;
    }
    if (Platform.OS === "android") {
      await liveKitNative.AudioSession.configureAudio({
        android: {
          // MODE_NORMAL delegates wired/Bluetooth/speaker selection to
          // Android. Supplying a preferred-output list would reintroduce
          // call-style device routing through LiveKit's AudioSwitch layer.
          audioTypeOptions: this.getAndroidMediaVoiceAudioOptions(liveKitNative),
        },
      });
      return;
    }
    if (Platform.OS === "ios") {
      await liveKitNative.AudioSession.setAppleAudioConfiguration(
        this.getAppleMediaVoiceAudioOptions(microphoneEnabled),
      );
    }
  }

  private getAndroidMediaVoiceAudioOptions(liveKitNative: NativeLiveKitModule) {
    return {
      ...liveKitNative.AndroidAudioTypePresets.media,
      // Pin every field that distinguishes media from call routing so an
      // upstream preset change cannot silently opt PlayAural into mono voice.
      audioMode: "normal" as const,
      audioStreamType: "music" as const,
      audioAttributesUsageType: "media" as const,
      audioAttributesContentType: "music" as const,
      audioFocusMode: "gainTransientMayDuck" as const,
      manageAudioFocus: false,
      forceHandleAudioRouting: false,
    };
  }

  private getAppleMediaVoiceAudioOptions(
    microphoneEnabled: boolean,
  ): AppleAudioConfiguration {
    if (microphoneEnabled) {
      // Recording requires playAndRecord, but the default mode deliberately
      // avoids voiceChat/videoChat processing and preserves media fidelity.
      return {
        audioCategory: "playAndRecord",
        audioCategoryOptions: [
          "allowAirPlay",
          // Keep Bluetooth on stereo A2DP. Enabling the HFP option gives the
          // mono hands-free route priority whenever microphone input is used.
          "allowBluetoothA2DP",
          "defaultToSpeaker",
          "mixWithOthers",
        ],
        audioMode: "default",
      };
    }
    return {
      audioCategory: "playback",
      audioCategoryOptions: [
        "allowAirPlay",
        "allowBluetoothA2DP",
        "mixWithOthers",
      ],
      audioMode: "default",
    };
  }
}
