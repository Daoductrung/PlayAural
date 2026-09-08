import { ENABLE_CLIENT_DEBUG_LOGS } from "../utils/debug";
import { NativeSpeechDriver } from "./NativeSpeechDriver";
import { createExpoSpeechBackend } from "./expoSpeechBackend";

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
  quality?: string;
};

const DEBUG_PREFIX = "PLAYAURAL_DEBUG TTS";
const MIN_SPEECH_RATE = 0.1;
const MAX_SPEECH_RATE = 10;

export class TtsManager {
  private lastAnnouncementText = "";
  private language = "en";
  private rate = 2.0;
  private uiEnabled = true;
  private uiVoice: string | undefined;
  private announcementVoice: string | undefined;
  private webVoices: SpeechSynthesisVoice[] = [];
  private webVoicesReadyPromise: Promise<SpeechSynthesisVoice[]> | null = null;
  private activeChannel: SpeechChannel | null = null;
  private activeText = "";
  private announcementQueue: AnnouncementQueueItem[] = [];
  private token = 0;
  private nativeDriver: NativeSpeechDriver | null = null;
  private currentUiTextProvider: (() => string | null) | null = null;
  private pendingPassiveUiText: string | null = null;

  setLanguage(language: string): void {
    const next = language || "en";
    if (this.language === next) return;
    this.language = next;
    this.replayActiveSpeechForSettingsChange();
  }

  setRate(rate: number): void {
    if (!Number.isFinite(rate)) return;
    const next = Math.max(MIN_SPEECH_RATE, Math.min(MAX_SPEECH_RATE, rate));
    if (next === this.rate) return;
    this.rate = next;
    this.replayActiveSpeechForSettingsChange();
  }

  setVoice(voice: string | undefined): void {
    if (this.uiVoice === (voice || undefined) && this.announcementVoice === (voice || undefined)) return;
    this.uiVoice = voice || undefined;
    this.announcementVoice = voice || undefined;
    this.replayActiveSpeechForSettingsChange();
  }

  async setMobileVoice(voice: string | undefined): Promise<void> {
    // Preserve the preference across transient discovery failures and engine
    // changes. The driver validates it against the current engine before every
    // utterance, so an unavailable identifier never reaches native speech.
    this.setVoice(voice || undefined);
  }

  setUiVoice(voice: string | undefined): void {
    if (this.uiVoice === (voice || undefined)) return;
    this.uiVoice = voice || undefined;
    this.replayActiveSpeechForSettingsChange();
  }

  setAnnouncementVoice(voice: string | undefined): void {
    if (this.announcementVoice === (voice || undefined)) return;
    this.announcementVoice = voice || undefined;
    this.replayActiveSpeechForSettingsChange();
  }

  async getAvailableVoiceOptions(options: { forceRefresh?: boolean } = {}): Promise<TtsVoiceOption[]> {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      if (options.forceRefresh || this.webVoices.length === 0) {
        this.webVoices = await this.ensureWebVoicesLoaded();
      }
      return this.normalizeVoiceOptions(this.webVoices.map((voice) => ({
        id: voice.voiceURI || voice.name,
        isDefault: voice.default,
        label: voice.name,
        language: voice.lang,
      })));
    }

    try {
      const voices = await this.getNativeDriver().getVoices(options.forceRefresh);
      return this.normalizeVoiceOptions(voices.map((voice) => ({
        id: voice.identifier,
        isDefault: false,
        label: voice.name,
        language: voice.language,
        quality: String(voice.quality || ""),
      })));
    } catch (error) {
      this.debug("voice-list-error", error instanceof Error ? error.message : String(error));
      return [];
    }
  }

  setCurrentUiTextProvider(provider: (() => string | null) | null): void {
    this.currentUiTextProvider = provider;
  }

  private getNativeDriver(): NativeSpeechDriver {
    this.nativeDriver ??= new NativeSpeechDriver(createExpoSpeechBackend());
    return this.nativeDriver;
  }

  refreshNativeSpeech(): void {
    if (typeof window !== "undefined" && "speechSynthesis" in window) return;
    this.getNativeDriver().reset();
    this.replayActiveSpeechForSettingsChange();
  }

  setUiEnabled(enabled: boolean): void {
    if (this.uiEnabled === enabled) {
      return;
    }

    this.uiEnabled = enabled;
    if (!enabled) {
      this.pendingPassiveUiText = null;
      if (this.activeChannel === "ui") {
        this.debug("disable-ui-stop-active-ui", this.activeText);
        this.activeChannel = null;
        this.activeText = "";
        this.token += 1;
        this.stopUnderlyingSpeech();
        this.startNextAnnouncement();
      }
      return;
    }

    this.refreshCurrentUiFocusForSettingsChange();
  }

  speakUi(text: string, options: SpeechStartOptions = {}): void {
    if (!this.uiEnabled || !text) {
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

  stopAnnouncements(): void {
    this.debug("stop-announcements", "");
    this.announcementQueue = [];
    if (this.activeChannel !== "announcement") {
      return;
    }
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

    // The native driver serializes every stop, initialization and start.
    this.startNativeSpeech(channel, token, text);
  }

  private startNativeSpeech(channel: SpeechChannel, token: number, text: string): void {
    if (token !== this.token || this.activeChannel !== channel || this.activeText !== text) {
      return;
    }

    try {
      this.getNativeDriver().speak(text, {
        language: this.language,
        onDone: () => {
          this.handleSpeechFinished(channel, token);
        },
        onError: (error) => {
          this.debug("native-speech-error", error.message);
          this.handleSpeechFinished(channel, token);
        },
        onStopped: () => {
          this.handleSpeechFinished(channel, token);
        },
        rate: this.rate,
        voice: channel === "announcement" ? this.announcementVoice : this.uiVoice,
      });
    } catch (error) {
      this.debug("native-speech-start-error", error instanceof Error ? error.message : String(error));
      this.handleSpeechFinished(channel, token);
    }
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
      this.speakPendingPassiveFocus();
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

    this.startSpeech("announcement", next.text, {
      remember: next.remember,
    });
    return true;
  }

  private speakPendingPassiveFocus(): void {
    const pending = this.pendingPassiveUiText;
    this.pendingPassiveUiText = null;
    if (!this.uiEnabled || !pending) {
      return;
    }
    this.speakUi(pending, {
      interruptAnnouncement: false,
      interruptUi: false,
    });
  }

  private stopUnderlyingSpeech(): void {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      return;
    }
    this.nativeDriver?.stop();
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
      this.refreshCurrentUiFocusForSettingsChange();
      return;
    }

    const channel = this.activeChannel;
    const text = this.activeText;
    const remember = channel === "announcement" && this.lastAnnouncementText === text;
    this.token += 1;
    this.stopUnderlyingSpeech();
    this.startSpeech(channel, text, { remember });
  }

  private refreshCurrentUiFocusForSettingsChange(): void {
    if (this.activeChannel === "announcement" || this.announcementQueue.length > 0) {
      const deferredText = this.currentUiTextProvider?.() ?? null;
      if (deferredText) {
        this.pendingPassiveUiText = deferredText;
      }
      return;
    }

    const text = this.currentUiTextProvider?.() ?? null;
    if (!text) {
      return;
    }

    this.speakUi(text, {
      interruptAnnouncement: false,
      interruptUi: true,
    });
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

  private normalizeVoiceOptions(options: TtsVoiceOption[]): TtsVoiceOption[] {
    const seen = new Set<string>();
    return options
      .map((voice) => {
        const id = String(voice.id || "").trim();
        const language = String(voice.language || "").trim();
        const label = String(voice.label || "").trim() || language || id;
        const quality = String(voice.quality || "").trim();
        return {
          id,
          isDefault: voice.isDefault,
          label,
          language,
          quality: quality || undefined,
        };
      })
      .filter((voice) => {
        if (!voice.id || seen.has(voice.id)) {
          return false;
        }
        seen.add(voice.id);
        return true;
      })
      .sort((left, right) => {
        const leftKey = `${left.language}\u0000${left.label}\u0000${left.id}`;
        const rightKey = `${right.language}\u0000${right.label}\u0000${right.id}`;
        return leftKey.localeCompare(rightKey);
      });
  }

  private debug(event: string, text: string): void {
    if (!ENABLE_CLIENT_DEBUG_LOGS || typeof console === "undefined") {
      return;
    }
    console.info(DEBUG_PREFIX, event, text ? { text } : "");
  }
}
