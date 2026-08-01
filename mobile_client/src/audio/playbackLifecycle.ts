export type NativePlaybackStatusSnapshot = {
  didJustFinish?: boolean;
  isLoaded: boolean;
  isLooping?: boolean;
};

/**
 * ExpoAV reports `didJustFinish` at every automatic loop boundary on Android.
 * Only a completed one-shot is terminal; a looping source must remain owned by
 * the audio manager so the native player can continue into its next cycle.
 */
export function isTerminalNativePlaybackStatus(
  status: NativePlaybackStatusSnapshot,
): boolean {
  return status.isLoaded
    && status.didJustFinish === true
    && status.isLooping !== true;
}
