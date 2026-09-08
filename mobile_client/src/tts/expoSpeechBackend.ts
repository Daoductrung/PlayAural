import { requireNativeModule } from "expo";
import { Platform } from "react-native";
import type { SpeechOptions, Voice } from "expo-speech";

import type { NativeSpeechBackend } from "./NativeSpeechDriver";

type SpeechEvent = { id: string; error?: string; charIndex?: number; charLength?: number };
type SpeechModule = {
  addListener(name: string, listener: (event: SpeechEvent) => void): { remove(): void };
  maxSpeechInputLength: number;
  getVoices(): Promise<Voice[]>;
  speak(id: string, text: string, options: SpeechOptions): Promise<void>;
  stop(): Promise<void>;
  reset(): Promise<void>;
  isSpeaking(): Promise<boolean>;
};

// The native module outlives an individual React app/manager instance.
let nextUtteranceId = 0;

export function createExpoSpeechBackend(): NativeSpeechBackend {
  const native = requireNativeModule<SpeechModule>("ExpoSpeech");
  let cleanup = () => {};
  return {
    maxSpeechInputLength: native.maxSpeechInputLength ?? Number.MAX_SAFE_INTEGER,
    getVoices: () => native.getVoices(),
    isSpeaking: () => native.isSpeaking(),
    stop: async () => {
      cleanup();
      await native.stop();
    },
    reset: async () => {
      cleanup();
      if (Platform.OS === "android") await native.reset();
      else await native.stop();
    },
    speak: async (text, options) => {
      cleanup();
      const id = String(++nextUtteranceId);
      const subscriptions: { remove(): void }[] = [];
      const clear = () => subscriptions.splice(0).forEach((subscription) => subscription.remove());
      cleanup = clear;
      const listen = (name: string, callback: (event: SpeechEvent) => void, terminal = false) => {
        subscriptions.push(native.addListener(name, (event) => {
          if (event.id !== id) return;
          if (terminal) clear();
          callback(event);
        }));
      };
      listen("Exponent.speakingStarted", () => options.onStart?.());
      listen("Exponent.speakingDone", () => options.onDone?.(), true);
      listen("Exponent.speakingStopped", () => options.onStopped?.(), true);
      listen("Exponent.speakingError", (event) => options.onError?.(new Error(event.error)), true);
      try {
        // Native receives only serializable settings; callbacks stay in JS.
        const { language, voice, rate, pitch, volume, useApplicationAudioSession } = options;
        await native.speak(id, text, { language, voice, rate, pitch, volume, useApplicationAudioSession });
      } catch (error) {
        clear();
        throw error;
      }
    },
  };
}
