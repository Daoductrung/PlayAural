import { Platform } from "react-native";
import {
  Room,
  RoomEvent,
  Track,
  type RemoteParticipant,
  type RemoteTrackPublication,
} from "livekit-client";

type NativeLiveKitModule = typeof import("@livekit/react-native");
type VoiceBootstrapGlobal = typeof globalThis & {
  __PLAYAURAL_NATIVE_VOICE_BOOTSTRAP_ERROR__?: string;
};

export type MobileVoiceConnectionState = "connected" | "connecting" | "disconnected";

export type VoiceJoinInfoPacket = {
  context_id?: string;
  provider?: string;
  room?: string;
  room_label?: string;
  scope?: string;
  token: string;
  url: string;
};

type VoiceCallbacks = {
  onConnected?: () => void;
  onDisconnect?: (reason: "connection_lost") => void;
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
  private localDisconnectRequested = false;
  private intent = 0;
  private nativeAudioSessionStarted = false;
  private remoteAudioElements = new Map<string, HTMLAudioElement>();
  private webAudioContainer: HTMLDivElement | null = null;

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
    void this.joinInternal(packet, intent);
  }

  leave(notify = true): void {
    this.nextIntent();
    void this.leaveInternal(notify);
  }

  setMicrophoneEnabled(enabled: boolean): void {
    void this.setMicrophoneEnabledInternal(enabled);
  }

  shutdown(): void {
    this.nextIntent();
    void this.leaveInternal(false);
  }

  private nextIntent(): number {
    this.intent += 1;
    return this.intent;
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
      if (Platform.OS === "web" && track.kind === Track.Kind.Audio) {
        this.attachWebTrack(track as Track, publication, participant);
      }
    });

    room.on(RoomEvent.TrackUnsubscribed, (track, publication) => {
      if (Platform.OS === "web" && track.kind === Track.Kind.Audio) {
        this.detachWebTrack(publication);
      }
    });

    room.on(RoomEvent.Disconnected, () => {
      const wasConnected = this.connected;
      const expectedDisconnect = this.localDisconnectRequested;
      this.connected = false;
      this.cleanupWebAudioElements();
      this.room = null;
      this.setMicState(false);
      this.setState("disconnected");
      void this.stopNativeAudioSession();
      if (wasConnected && !expectedDisconnect) {
        this.callbacks.onDisconnect?.("connection_lost");
      }
      this.localDisconnectRequested = false;
    });

    room.on(RoomEvent.MediaDevicesError, () => {
      this.callbacks.onStatus?.("voice-chat-mic-denied", true);
    });
  }

  private async setMicrophoneEnabledInternal(enabled: boolean): Promise<void> {
    if (!this.room || !this.connected) {
      this.callbacks.onStatus?.("voice-chat-not-connected", true);
      return;
    }
    if (this.micBusy || enabled === this.micEnabled) {
      return;
    }

    this.micBusy = true;
    try {
      await this.room.localParticipant.setMicrophoneEnabled(enabled);
      this.setMicState(enabled);
      this.callbacks.onStatus?.(enabled ? "voice-chat-mic-on" : "voice-chat-mic-off", true);
    } catch {
      this.setMicState(false);
      this.callbacks.onStatus?.("voice-chat-mic-denied", true);
    } finally {
      this.micBusy = false;
    }
  }

  private async leaveInternal(notify: boolean): Promise<void> {
    const room = this.room;
    this.room = null;

    if (room) {
      this.localDisconnectRequested = true;
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
    this.cleanupWebAudioElements();
    await this.stopNativeAudioSession();
    this.setMicState(false);
    this.setState("disconnected");
    if (notify) {
      this.callbacks.onStatus?.("voice-chat-left", true);
    }
    this.localDisconnectRequested = false;
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

    await liveKitNative.AudioSession.configureAudio({
      android: {
        preferredOutputList: ["bluetooth", "headset", "speaker", "earpiece"],
        audioTypeOptions: liveKitNative.AndroidAudioTypePresets.communication,
      },
      ios: {
        defaultOutput: "speaker",
      },
    });
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
}
