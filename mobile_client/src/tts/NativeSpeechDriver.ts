import type { SpeechOptions, Voice } from "expo-speech";

export interface NativeSpeechBackend {
  maxSpeechInputLength: number;
  getVoices(): Promise<Voice[]>;
  speak(text: string, options: SpeechOptions): Promise<void>;
  stop(): Promise<void>;
  reset(): Promise<void>;
  isSpeaking(): Promise<boolean>;
}

// Android exposes no binding/start deadline. These are injectable recovery
// budgets, not estimates of how long text takes to speak. Never cut off speech
// because of its length or the user's selected rate.
export const DEFAULT_SPEECH_RECOVERY_POLICY = {
  operationTimeoutMs: 10000,
  startTimeoutMs: 10000,
  completionPollMs: 1000,
  recoveryAttempts: 1,
};

export class NativeSpeechDriver {
  private generation = 0;
  private control: Promise<void> = Promise.resolve();
  private controlRevision = 0;
  private resetPending = false;
  private voices: Voice[] | null = null;
  private readiness: Promise<Voice[]> | null = null;
  private voiceGeneration = 0;
  private timer: ReturnType<typeof setTimeout> | null = null;
  private cancelUtterance: (() => void) | null = null;

  constructor(
    private readonly backend: NativeSpeechBackend,
    private readonly policy = DEFAULT_SPEECH_RECOVERY_POLICY,
  ) {}

  private async bounded<T>(operation: Promise<T>): Promise<T> {
    let timer: ReturnType<typeof setTimeout> | undefined;
    try {
      return await Promise.race([
        operation,
        new Promise<never>((_, reject) => {
          timer = setTimeout(() => reject(new Error("TTS operation timed out")), this.policy.operationTimeoutMs);
        }),
      ]);
    } finally {
      clearTimeout(timer);
    }
  }

  async getVoices(forceRefresh = false): Promise<Voice[]> {
    let control: Promise<void>;
    do {
      control = this.control;
      await control;
    } while (control !== this.control);
    if (forceRefresh) this.voices = null;
    if (this.voices !== null) return this.voices;
    if (this.readiness) return this.readiness;
    const generation = this.voiceGeneration;
    // Share the guarded result with every caller, not the raw native promise.
    // Separate success/failure handlers keep a replacement request's failure
    // from being mistaken for another stale result and retried indefinitely.
    const pending = this.bounded(Promise.resolve().then(() => this.backend.getVoices())).then(
      (voices) => {
        if (generation !== this.voiceGeneration) return this.getVoices();
        this.voices = voices;
        return voices;
      },
      (error) => {
        if (generation !== this.voiceGeneration) return this.getVoices();
        this.enqueueControl(true); // Also retire hung voice-only initialization.
        throw error;
      },
    ).finally(() => {
      if (this.readiness === pending) this.readiness = null;
    });
    this.readiness = pending;
    return pending;
  }

  private invalidate(): number {
    this.generation += 1;
    clearTimeout(this.timer ?? undefined);
    this.timer = null;
    this.cancelUtterance?.();
    this.cancelUtterance = null;
    return this.generation;
  }

  private enqueueControl(reset: boolean): void {
    if (reset) {
      this.voiceGeneration += 1;
      this.voices = null;
      this.readiness = null;
    }
    this.resetPending ||= reset;
    const revision = ++this.controlRevision;
    this.control = this.control.then(() => {
      // A slow native call must not leave every superseded navigation request
      // waiting through another timeout. Keep only the latest pending control,
      // retaining any engine reset requested by earlier coalesced operations.
      if (revision !== this.controlRevision) return;
      const shouldReset = this.resetPending;
      this.resetPending = false;
      return this.bounded(shouldReset ? this.backend.reset() : this.backend.stop());
    }).catch(() => {
      this.voices = null;
    });
  }

  stop(): void {
    this.invalidate();
    this.enqueueControl(false);
  }

  reset(): void {
    this.invalidate();
    this.enqueueControl(true);
  }

  speak(text: string, options: SpeechOptions): void {
    const generation = this.invalidate();
    this.enqueueControl(false);
    void this.run(text, options, generation);
  }

  private async run(text: string, options: SpeechOptions, generation: number): Promise<void> {
    let remaining = text;
    while (remaining && generation === this.generation) {
      // Respect the native engine's limit and don't split UTF-16 surrogate pairs.
      let end = Math.min(remaining.length, this.backend.maxSpeechInputLength);
      if (end < remaining.length && /[\uD800-\uDBFF]/u.test(remaining[end - 1])) end -= 1;
      if (end < remaining.length) {
        const boundary = remaining.slice(0, end).search(/\s+\S*$/u);
        if (boundary > 0) end = boundary;
      }
      const chunk = remaining.slice(0, end);
      let completed = false;
      for (let attempt = 0; attempt <= this.policy.recoveryAttempts; attempt += 1) {
        try {
          await this.control;
          if (generation !== this.generation) return;
          const voices = await this.getVoices();
          if (generation !== this.generation) return;
          const voice = attempt === 0 && voices.some((item) => item.identifier === options.voice)
            ? options.voice : undefined;
          await this.utter(chunk, { ...options, voice }, generation);
          completed = true;
          break;
        } catch (error) {
          if (generation !== this.generation) return;
          if (attempt === this.policy.recoveryAttempts) {
            this.enqueueControl(true);
            options.onError?.(error instanceof Error ? error : new Error(String(error)));
            return;
          }
          this.enqueueControl(true);
        }
      }
      if (!completed || generation !== this.generation) return;
      remaining = remaining.slice(end);
    }
    if (generation === this.generation) options.onDone?.();
  }

  private utter(text: string, options: SpeechOptions, generation: number): Promise<void> {
    return new Promise((resolve, reject) => {
      let settled = false;
      let started = false;
      const finish = (error?: Error) => {
        if (settled) return;
        settled = true;
        if (generation === this.generation) {
          clearTimeout(this.timer ?? undefined);
          this.timer = null;
          this.cancelUtterance = null;
        }
        if (error) reject(error);
        else resolve();
      };
      this.cancelUtterance = () => finish();
      const poll = () => {
        this.timer = setTimeout(() => {
          if (generation !== this.generation || settled) return;
          void this.bounded(Promise.resolve().then(() => this.backend.isSpeaking())).then((speaking) => {
            if (generation !== this.generation || settled) return;
            if (speaking) poll();
            else {
              this.enqueueControl(false); // Release listeners even when Done was lost.
              finish();
            }
          }).catch((error: Error) => finish(error));
        }, this.policy.completionPollMs);
      };
      const onStarted = () => {
        if (generation !== this.generation || settled || started) return;
        started = true;
        clearTimeout(this.timer ?? undefined);
        options.onStart?.();
        if (generation === this.generation && !settled) poll();
      };
      this.timer = setTimeout(() => {
        void this.bounded(Promise.resolve().then(() => this.backend.isSpeaking())).then((speaking) => {
          if (generation !== this.generation || settled || started) return;
          if (speaking) onStarted(); // Some engines lose the start event, too.
          else finish(new Error("TTS did not start"));
        }).catch((error: Error) => {
          if (!started) finish(error);
        });
      }, this.policy.startTimeoutMs);
      void Promise.resolve().then(() => {
        if (generation !== this.generation || settled) return;
        return this.backend.speak(text, {
          ...options,
          onStart: onStarted,
          onDone: () => finish(),
          onStopped: () => finish(new Error("TTS was interrupted")),
          onError: (error) => finish(error),
        });
      }).catch((error: Error) => finish(error));
    });
  }
}
