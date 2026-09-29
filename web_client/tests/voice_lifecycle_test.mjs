import assert from "node:assert/strict";
import test from "node:test";

import { retireVoiceRoom } from "../voice_lifecycle.js";

test("voice retirement completes without waiting for stalled microphone cleanup", async () => {
  let disconnectCalls = 0;
  const microphoneCleanup = new Promise(() => {});
  const room = {
    disconnect() {
      disconnectCalls += 1;
      return Promise.resolve();
    },
    localParticipant: {
      setMicrophoneEnabled(enabled) {
        assert.equal(enabled, false);
        return microphoneCleanup;
      },
    },
  };

  const retirement = retireVoiceRoom(room);
  assert.equal(disconnectCalls, 1);
  await retirement;
});

test("voice retirement contains stale SDK failures", async () => {
  await assert.doesNotReject(() => retireVoiceRoom({
    disconnect() {
      return Promise.reject(new Error("room already closed"));
    },
    localParticipant: {
      setMicrophoneEnabled() {
        throw new Error("microphone already released");
      },
    },
  }));
  await assert.doesNotReject(() => retireVoiceRoom(null));
});
