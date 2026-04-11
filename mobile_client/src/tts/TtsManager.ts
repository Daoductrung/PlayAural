import * as Speech from "expo-speech";
import type { Voice } from "expo-speech";

type SpeechChannel = "announcement" | "ui";

type SpeechStartOptions = {
  interruptAnnouncement?: boolean;
  interruptUi?: boolean;
};

type AnnouncementStartOptions = {
  remember?: boolean;
};

type AnnouncementQueueItem = {
  remember: boolean;
  text: string;
};

export type TtsVoiceOption = {
  id: string;
  isDefault: boolean;
  label: string;
  language: string;
};

const DEBUG_PREFIX = "PLAYAURAL_DEBUG TTS";
const MIN_SPEECH_RATE = 0.1;
const MAX_SPEECH_RATE = 10;

export class TtsManager {
  private lastAnnouncementText = "";
  private language = "en";
  private rate = 2.0;
  private uiVoice: string | undefined;
  private announcementVoice: string | undefined;
  private nativeVoices: Voice[] = [];
  private webVoices: SpeechSynthesisVoice[] = [];
  private webVoicesReadyPromise: Promise<SpeechSynthesisVoice[]> | null = null;
  private activeChannel: SpeechChannel | null = null;
  private activeText = "";
  private announcementQueue: AnnouncementQueueItem[] = [];
  private token = 0;
  private currentUiTextProvider: (() => string | null) | null = null;
  private pendingPassiveUiText: string | null = null;

  setLanguage(language: string): void {
    this.language = language || "en";
  }

  setRate(rate: number): void {
    this.rate = Math.max(MIN_SPEECH_RATE, Math.min(MAX_SPEECH_RATE, rate));
    this.replayActiveSpeechForSettingsChange();
  }

  setVoice(voice: string | undefined): void {
    this.uiVoice = voice || undefined;
    this.announcementVoice = voice || undefined;
    this.replayActiveSpeechForSettingsChange();
  }

  async setMobileVoice(voice: string | undefined): Promise<void> {
    const requestedVoice = voice || undefined;
    if (!requestedVoice) {
      this.setVoice(undefined);
      return;
    }

    // Apply the requested identifier immediately so the next utterance uses it
    // while the async voice list validation resolves.
    this.setVoice(requestedVoice);

    const voices = await this.getAvailableVoiceOptions();
    const found = voices.find((candidate) => candidate.id === requestedVoice);
    if (!found) {
      this.debug("voice-fallback-default", requestedVoice);
      this.setVoice(undefined);
      return;
    }
    this.setVoice(found.id);
  }

  setUiVoice(voice: string | undefined): void {
    this.uiVoice = voice || undefined;
    this.replayActiveSpeechForSettingsChange();
  }

  setAnnouncementVoice(voice: string | undefined): void {
    this.announcementVoice = voice || undefined;
    this.replayActiveSpeechForSettingsChange();
  }

  async getAvailableVoiceOptions(): Promise<TtsVoiceOption[]> {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      this.webVoices = await this.ensureWebVoicesLoaded();
      return this.webVoices.map((voice) => ({
        id: voice.voiceURI || voice.name,
        isDefault: voice.default,
        label: voice.name,
        language: voice.lang,
      }));
    }

    try {
      this.nativeVoices = await Speech.getAvailableVoicesAsync();
      return this.nativeVoices.map((voice) => ({
        id: voice.identifier,
        isDefault: false,
        label: voice.name,
        language: voice.language,
      }));
    } catch (error) {
      this.debug("voice-list-error", error instanceof Error ? error.message : String(error));
      this.nativeVoices = [];
      return [];
    }
  }

  setCurrentUiTextProvider(provider: (() => string | null) | null): void {
    this.currentUiTextProvider = provider;
  }

  speakUi(text: string, options: SpeechStartOptions = {}): void {
    if (!text) {
      return;
    }

    const interruptAnnouncement = options.interruptAnnouncement ?? true;
    const interruptUi = options.interruptUi ?? true;

    if (
      !interruptAnnouncement &&
      (this.activeChannel === "announcement" || this.announcementQueue.length > 0)
    ) {
      this.pendingPassiveUiText = text;
      this.debug("ui-deferred-for-announcement", text);
      return;
    }

    if (!interruptUi && this.activeChannel === "ui") {
      if (this.activeText === text) {
        this.debug("ui-duplicate-ignored", text);
        return;
      }
      this.pendingPassiveUiText = text;
      this.debug("ui-deferred-for-ui", text);
      return;
    }

    this.debug("speak-ui", text);
    if (interruptAnnouncement) {
      this.announcementQueue = [];
      this.pendingPassiveUiText = null;
    } else {
      this.pendingPassiveUiText = null;
    }

    this.stopUnderlyingSpeech();
    this.startSpeech("ui", text);
  }

  speakAnnouncement(text: string, options: AnnouncementStartOptions = {}): void {
    if (!text) {
      return;
    }

    this.debug("speak-announcement-request", text);
    this.announcementQueue.push({
      remember: options.remember ?? true,
      text,
    });

    if (this.activeChannel === "announcement") {
      this.debug("announcement-queued", `${this.announcementQueue.length}`);
      return;
    }

    if (this.activeChannel === "ui") {
      this.debug("announcement-waiting-for-ui", `${this.announcementQueue.length}`);
      return;
    }

    this.startNextAnnouncement();
  }

  stop(): void {
    this.debug("stop", "");
    this.announcementQueue = [];
    this.pendingPassiveUiText = null;
    this.activeChannel = null;
    this.activeText = "";
    this.token += 1;
    this.stopUnderlyingSpeech();
  }

  repeatLastAnnouncement(): string | null {
    if (!this.lastAnnouncementText) {
      return null;
    }
    const text = this.lastAnnouncementText;
    this.debug("repeat-last-announcement", text);
    this.announcementQueue = [];
    this.pendingPassiveUiText = null;
    this.stopUnderlyingSpeech();
    this.startSpeech("announcement", text, { remember: false });
    return text;
  }

  private startSpeech(channel: SpeechChannel, text: string, options: AnnouncementStartOptions = {}): void {
    const token = ++this.token;
    this.activeChannel = channel;
    this.activeText = text;
    if (channel === "announcement" && options.remember !== false) {
      this.lastAnnouncementText = text;
    }
    this.debug(`start-${channel}`, text);

    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = this.language;
      utterance.rate = this.rate;

      const voice = this.resolveWebVoice(channel);
      if (voice) {
        utterance.voice = voice;
      }

      utterance.onend = () => {
        this.handleSpeechFinished(channel, token);
      };
      utterance.onerror = (event) => {
        this.debug(`error-${channel}`, String(event.error || "unknown"));
        this.handleSpeechFinished(channel, token);
      };

      window.speechSynthesis.speak(utterance);
      return;
    }

    Speech.speak(text, {
      language: this.language,
      onDone: () => {
        this.handleSpeechFinished(channel, token);
      },
      onError: () => {
        this.handleSpeechFinished(channel, token);
      },
      onStopped: () => {
        this.handleSpeechFinished(channel, token);
      },
      rate: this.rate,
      voice: channel === "announcement" ? this.announcementVoice : this.uiVoice,
    });
  }

  private handleSpeechFinished(channel: SpeechChannel, token: number): void {
    if (token !== this.token || this.activeChannel !== channel) {
      return;
    }

    this.debug(`finish-${channel}`, "");
    this.activeChannel = null;
    this.activeText = "";

    if (this.startNextAnnouncement()) {
      return;
    }

    if (channel === "announcement") {
      this.speakCurrentPassiveFocus();
      return;
    }

    this.speakPendingPassiveFocus();
  }

  private startNextAnnouncement(): boolean {
    if (this.activeChannel !== null) {
      return this.announcementQueue.length > 0;
    }

    const next = this.announcementQueue.shift();
    if (!next) {
      return false;
    }

    this.startSpeech("announcement", next.text, { remember: next.remember });
    return true;
  }

  private speakPendingPassiveFocus(): void {
    const pending = this.pendingPassiveUiText;
    this.pendingPassiveUiText = null;
    if (!pending) {
      return;
    }
    this.speakUi(pending, {
      interruptAnnouncement: false,
      interruptUi: false,
    });
  }

  private speakCurrentPassiveFocus(): void {
    const text = this.pendingPassiveUiText || this.currentUiTextProvider?.();
    this.pendingPassiveUiText = null;
    if (!text) {
      return;
    }
    this.speakUi(text, {
      interruptAnnouncement: false,
      interruptUi: false,
    });
  }

  private stopUnderlyingSpeech(): void {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      return;
    }
    Speech.stop();
  }

  private resolveWebVoice(channel: SpeechChannel): SpeechSynthesisVoice | null {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return null;
    }

    const targetVoice = channel === "announcement" ? this.announcementVoice : this.uiVoice;
    if (!targetVoice) {
      return null;
    }

    const voices = this.webVoices.length > 0 ? this.webVoices : window.speechSynthesis.getVoices();
    return voices.find((candidate) => candidate.voiceURI === targetVoice || candidate.name === targetVoice) ?? null;
  }

  private replayActiveSpeechForSettingsChange(): void {
    if (!this.activeChannel || !this.activeText) {
      return;
    }

    const channel = this.activeChannel;
    const text = this.activeText;
    const remember = channel === "announcement" && this.lastAnnouncementText === text;
    this.token += 1;
    this.stopUnderlyingSpeech();
    this.startSpeech(channel, text, { remember });
  }

  private async ensureWebVoicesLoaded(): Promise<SpeechSynthesisVoice[]> {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return [];
    }

    const existing = window.speechSynthesis.getVoices();
    if (existing.length > 0) {
      return existing;
    }

    if (this.webVoicesReadyPromise) {
      return this.webVoicesReadyPromise;
    }

    this.webVoicesReadyPromise = new Promise<SpeechSynthesisVoice[]>((resolve) => {
      const finalize = () => {
        if (typeof window === "undefined" || !("speechSynthesis" in window)) {
          resolve([]);
          return;
        }
        const voices = window.speechSynthesis.getVoices();
        window.speechSynthesis.removeEventListener("voiceschanged", onVoicesChanged);
        this.webVoicesReadyPromise = null;
        resolve(voices);
      };

      const onVoicesChanged = () => {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
          finalize();
        }
      };

      window.speechSynthesis.addEventListener("voiceschanged", onVoicesChanged);
      window.setTimeout(finalize, 1500);
    });

    return this.webVoicesReadyPromise;
  }

  private debug(event: string, text: string): void {
    if (typeof console === "undefined") {
      return;
    }
    console.info(DEBUG_PREFIX, event, text ? { text } : "");
  }
}
