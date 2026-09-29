/**
 * Retire one LiveKit room without letting slow microphone cleanup delay the
 * media disconnect. Cleanup failures are contained because session teardown
 * must continue even when a device or SDK operation is already stale.
 */
export async function retireVoiceRoom(room) {
  if (!room) {
    return;
  }

  let disconnectTask = Promise.resolve();
  try {
    // Disconnect first so device cleanup can never keep media connected.
    disconnectTask = Promise.resolve(room.disconnect()).catch(() => {});
  } catch {
    // Ignore a room that was already disconnected.
  }
  try {
    // This is best-effort because some browser/device stacks can leave the
    // returned promise pending after the room itself has already closed.
    void Promise.resolve(
      room.localParticipant?.setMicrophoneEnabled(false),
    ).catch(() => {});
  } catch {
    // Ignore a microphone that was already released.
  }
  await disconnectTask;
}
