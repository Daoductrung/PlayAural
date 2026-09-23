import type { SpeechOptions, Voice } from "expo-speech";

export interface NativeSpeechBackend {
  maxSpeechInputLength: number;
  getEngines?(): Promise<SpeechEngine[]>;
  getVoices(): Promise<Voice[]>;
  speak(text: string, options: SpeechOptions): Promise<void>;
  stop(): Promise<void>;
  reset(): Promise<void>;
  selectEngine?(identifier: string): Promise<void>;
  isSpeaking(): Promise<boolean>;
}

export type SpeechEngine = {
  identifier: string;
  isDefault?: boolean;
  isSystem?: boolean;
  label?: string;
};

export type SpeechRecoveryPolicy = {
  completionPollMs: number;
  maxEngineFallbacks?: number;
  operationTimeoutMs: number;
  recoveryAttempts: number;
  startTimeoutMs: number;
};

// Android exposes no binding/start deadline. These are injectable recovery
// budgets, not estimates of how long text takes to speak. Never cut off speech
// because of its length or the user's selected rate.
export const DEFAULT_SPEECH_RECOVERY_POLICY = {
  operationTimeoutMs: 10000,
  startTimeoutMs: 10000,
  completionPollMs: 1000,
  recoveryAttempts: 1,
  maxEngineFallbacks: 8,
} satisfies Required<SpeechRecoveryPolicy>;

class SpeechAttemptError extends Error {
  constructor(error: unknown, readonly started: boolean) {
    super(error instanceof Error ? error.message : String(error));
    this.name = "SpeechAttemptError";
  }
}

function policyInteger(value: number | undefined, fallback: number, minimum: number): number {
  if (value === undefined || !Number.isSafeInteger(value) || value < minimum) return fallback;
  return value;
}

export class NativeSpeechDriver {
  private generation = 0;
  private control: Promise<void> = Promise.resolve();
  private controlRevision = 0;
  private resetPending = false;
  private activeEngine: string | undefined;
  private engineGeneration = 0;
  private engineReadiness: Promise<SpeechEngine[]> | null = null;
  private engines: SpeechEngine[] | null = null;
  private failedVoiceKey: string | null = null;
  private voices: Voice[] | null = null;
  private readiness: Promise<Voice[]> | null = null;
  private voiceGeneration = 0;
  private timer: ReturnType<typeof setTimeout> | null = null;
  private cancelUtterance: (() => void) | null = null;
  private readonly policy: Required<SpeechRecoveryPolicy>;

  constructor(
    private readonly backend: NativeSpeechBackend,
    policy: SpeechRecoveryPolicy = DEFAULT_SPEECH_RECOVERY_POLICY,
  ) {
    this.policy = {
      completionPollMs: policyInteger(
        policy.completionPollMs,
        DEFAULT_SPEECH_RECOVERY_POLICY.completionPollMs,
        1,
      ),
      maxEngineFallbacks: policyInteger(
        policy.maxEngineFallbacks,
        DEFAULT_SPEECH_RECOVERY_POLICY.maxEngineFallbacks,
        0,
      ),
      operationTimeoutMs: policyInteger(
        policy.operationTimeoutMs,
        DEFAULT_SPEECH_RECOVERY_POLICY.operationTimeoutMs,
        1,
      ),
      recoveryAttempts: policyInteger(
        policy.recoveryAttempts,
        DEFAULT_SPEECH_RECOVERY_POLICY.recoveryAttempts,
        0,
      ),
      startTimeoutMs: policyInteger(
        policy.startTimeoutMs,
        DEFAULT_SPEECH_RECOVERY_POLICY.startTimeoutMs,
        1,
      ),
    };
  }

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
        this.activeEngine = undefined;
        this.enqueueControl(true); // Also retire hung voice-only initialization.
        throw error;
      },
    ).finally(() => {
      if (this.readiness === pending) this.readiness = null;
    });
    this.readiness = pending;
    return pending;
  }

  private async getEngines(): Promise<SpeechEngine[]> {
    if (!this.backend.getEngines) return [];
    if (this.engines !== null) return this.engines;
    if (this.engineReadiness) return this.engineReadiness;
    const generation = this.engineGeneration;
    const pending = this.bounded(Promise.resolve().then(() => this.backend.getEngines!())).then(
      (discovered) => {
        if (generation !== this.engineGeneration) return this.getEngines();
        const seen = new Set<string>();
        this.engines = discovered.flatMap((engine) => {
          const identifier = String(engine.identifier || "").trim();
          if (!identifier || seen.has(identifier)) return [];
          seen.add(identifier);
          return [{ ...engine, identifier }];
        });
        return this.engines;
      },
      (error) => {
        if (generation !== this.engineGeneration) return this.getEngines();
        throw error;
      },
    ).finally(() => {
      if (this.engineReadiness === pending) this.engineReadiness = null;
    });
    this.engineReadiness = pending;
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
    this.activeEngine = undefined;
    this.engineGeneration += 1;
    this.engineReadiness = null;
    this.engines = null;
    this.failedVoiceKey = null;
    this.enqueueControl(true);
  }

  clearFailedVoice(): void {
    this.failedVoiceKey = null;
  }

  private async selectEngine(identifier: string, generation: number): Promise<boolean> {
    if (!this.backend.selectEngine || generation !== this.generation) return false;
    this.voiceGeneration += 1;
    this.voices = null;
    this.readiness = null;
    this.resetPending = false;
    const revision = ++this.controlRevision;
    let applied = false;
    const operation = this.control.then(async () => {
      if (revision !== this.controlRevision || generation !== this.generation) return;
      await this.bounded(this.backend.selectEngine!(identifier));
      applied = true;
    });
    this.control = operation.catch(() => {
      this.voices = null;
    });
    await operation;
    if (!applied || generation !== this.generation) return false;
    this.activeEngine = identifier;
    return true;
  }

  private rebindCurrentEngine(generation: number): Promise<boolean> {
    if (this.activeEngine && this.backend.selectEngine) {
      return this.selectEngine(this.activeEngine, generation);
    }
    this.enqueueControl(true);
    return this.control.then(() => generation === this.generation);
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
      let lastError: unknown = new Error("TTS did not start");
      let engines: SpeechEngine[] = [];
      try {
        await this.control;
        if (generation !== this.generation) return;
        engines = await this.getEngines();
      } catch {
        // Engine discovery is an enhancement. The selected engine can still
        // recover through the original bounded rebind path when discovery is
        // unavailable or an older native module is in use.
      }

      for (let attempt = 0; attempt <= this.policy.recoveryAttempts; attempt += 1) {
        let attemptedVoiceKey: string | null = null;
        try {
          await this.control;
          if (generation !== this.generation) return;
          const voices = await this.getVoices();
          if (generation !== this.generation) return;
          const voiceKey = `${this.activeEngine ?? "system"}\u0000${options.voice ?? ""}`;
          const voice = attempt === 0
            && this.failedVoiceKey !== voiceKey
            && voices.some((item) => item.identifier === options.voice)
            ? options.voice : undefined;
          if (voice) attemptedVoiceKey = voiceKey;
          await this.utter(chunk, { ...options, voice }, generation);
          completed = true;
          break;
        } catch (error) {
          if (generation !== this.generation) return;
          lastError = error;
          if (error instanceof SpeechAttemptError && error.started) {
            options.onError?.(error);
            return;
          }
          if (attemptedVoiceKey) this.failedVoiceKey = attemptedVoiceKey;
          if (attempt < this.policy.recoveryAttempts) {
            if (!await this.rebindCurrentEngine(generation)) return;
          }
        }
      }

      if (!completed && this.backend.selectEngine && engines.length > 0) {
        const currentEngine = this.activeEngine
          ?? engines.find((engine) => engine.isDefault)?.identifier;
        const fallbackEngines = engines
          .filter((engine) => engine.identifier !== currentEngine)
          .sort((left, right) => {
            const systemDifference = Number(Boolean(right.isSystem)) - Number(Boolean(left.isSystem));
            if (systemDifference !== 0) return systemDifference;
            const defaultDifference = Number(Boolean(right.isDefault)) - Number(Boolean(left.isDefault));
            if (defaultDifference !== 0) return defaultDifference;
            return String(left.label || left.identifier).localeCompare(String(right.label || right.identifier));
          })
          .slice(0, this.policy.maxEngineFallbacks);

        for (const engine of fallbackEngines) {
          try {
            if (!await this.selectEngine(engine.identifier, generation)) return;
            await this.getVoices();
            if (generation !== this.generation) return;
            await this.utter(chunk, { ...options, voice: undefined }, generation);
            completed = true;
            break;
          } catch (error) {
            if (generation !== this.generation) return;
            lastError = error;
            if (error instanceof SpeechAttemptError && error.started) {
              options.onError?.(error);
              return;
            }
          }
        }
      }

      if (!completed) {
        this.activeEngine = undefined;
        this.enqueueControl(true);
        options.onError?.(lastError instanceof Error ? lastError : new Error(String(lastError)));
        return;
      }
      if (generation !== this.generation) return;
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
        if (error) reject(new SpeechAttemptError(error, started));
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
