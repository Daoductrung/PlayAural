export const VOICE_SETTINGS_PROTOCOL_VERSION = 1;
export const VOICE_PERSONAL_VOLUME_MIN = 10;
export const VOICE_PERSONAL_VOLUME_MAX = 100;
export const VOICE_PERSONAL_VOLUME_STEP = 10;
export const MAX_VOICE_SETTINGS_IDENTITIES = 256;
export const MAX_VOICE_IDENTITY_LENGTH = 128;

export function parseVoiceSettings(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return null;
  }
  const keys = Object.keys(payload).sort().join(",");
  if (keys !== "context_id,host_muted,participants,type,version"
      || payload.type !== "voice_settings"
      || payload.version !== VOICE_SETTINGS_PROTOCOL_VERSION
      || typeof payload.host_muted !== "boolean"
      || typeof payload.context_id !== "string"
      || !payload.context_id.trim()
      || payload.context_id !== payload.context_id.trim()
      || payload.context_id.length > MAX_VOICE_IDENTITY_LENGTH
      || !Array.isArray(payload.participants)
      || payload.participants.length > MAX_VOICE_SETTINGS_IDENTITIES) {
    return null;
  }
  const participants = new Map();
  for (const entry of payload.participants) {
    if (!entry || typeof entry !== "object" || Array.isArray(entry)
        || Object.keys(entry).sort().join(",") !== "muted,participant_id,volume"
        || typeof entry.participant_id !== "string"
        || !entry.participant_id.trim()
        || entry.participant_id !== entry.participant_id.trim()
        || entry.participant_id.length > MAX_VOICE_IDENTITY_LENGTH
        || participants.has(entry.participant_id)
        || !Number.isInteger(entry.volume)
        || entry.volume < VOICE_PERSONAL_VOLUME_MIN
        || entry.volume > VOICE_PERSONAL_VOLUME_MAX
        || (entry.volume - VOICE_PERSONAL_VOLUME_MIN) % VOICE_PERSONAL_VOLUME_STEP !== 0
        || typeof entry.muted !== "boolean") {
      return null;
    }
    participants.set(entry.participant_id, {
      muted: entry.muted,
      volume: entry.volume / 100,
    });
  }
  return {
    contextId: payload.context_id,
    hostMuted: payload.host_muted,
    participants,
  };
}
