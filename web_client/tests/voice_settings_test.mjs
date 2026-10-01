import assert from "node:assert/strict";
import test from "node:test";

import { parseVoiceSettings } from "../voice_settings.js";


test("voice settings snapshots are validated and normalized atomically", () => {
  const parsed = parseVoiceSettings({
    type: "voice_settings",
    version: 1,
    context_id: "table-one",
    host_muted: true,
    participants: [
      { participant_id: "uuid-bob", volume: 40, muted: false },
      { participant_id: "uuid-carol", volume: 100, muted: true },
    ],
  });

  assert.equal(parsed.contextId, "table-one");
  assert.equal(parsed.hostMuted, true);
  assert.deepEqual(parsed.participants.get("uuid-bob"), {
    muted: false,
    volume: 0.4,
  });
  assert.deepEqual(parsed.participants.get("uuid-carol"), {
    muted: true,
    volume: 1,
  });
});


test("voice settings reject spoofed, duplicate, and off-scale values", () => {
  const base = {
    type: "voice_settings",
    version: 1,
    context_id: "table-one",
    host_muted: false,
    participants: [],
  };
  const { type: _type, ...missingType } = base;
  assert.equal(parseVoiceSettings(missingType), null);
  assert.equal(parseVoiceSettings({ ...base, unexpected: true }), null);
  assert.equal(parseVoiceSettings({ ...base, type: "audio" }), null);
  assert.equal(parseVoiceSettings({ ...base, context_id: " table-one" }), null);
  assert.equal(parseVoiceSettings({
    ...base,
    participants: [{ participant_id: " uuid-bob", volume: 40, muted: false }],
  }), null);
  assert.equal(parseVoiceSettings({
    ...base,
    participants: [{ participant_id: "uuid-bob", volume: 41, muted: false }],
  }), null);
  assert.equal(parseVoiceSettings({
    ...base,
    participants: [
      { participant_id: "uuid-bob", volume: 40, muted: false },
      { participant_id: "uuid-bob", volume: 50, muted: true },
    ],
  }), null);
});
