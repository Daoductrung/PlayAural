type Subscription = { remove(): void };
type Environment = {
  readScreenReader(): Promise<boolean>;
  onScreenReaderChange(listener: (enabled: boolean) => void): Subscription;
  onAppStateChange(listener: (state: string) => void): Subscription;
  onFocus?: (listener: () => void) => Subscription;
  onBlur?: (listener: () => void) => Subscription;
  initialAppState: string | null;
};

// Subscribe before querying. An older promise must never undo a newer native
// event, a foreground query, or disposal. Query failures preserve known state.
export function observeSpeechEnvironment(
  environment: Environment,
  onScreenReader: (enabled: boolean) => void,
  onSpeechContextChanged: () => void,
): () => void {
  let disposed = false;
  let revision = 0;
  let reader: boolean | undefined;
  let suspended = environment.initialAppState !== "active";
  const apply = (enabled: boolean) => {
    const changed = reader !== undefined && reader !== enabled;
    reader = enabled;
    onScreenReader(enabled);
    // A settings screen or notification shade owns UI speech while we are
    // suspended. Resume will rebind and restore the current app focus.
    if (changed && !suspended) onSpeechContextChanged();
  };
  const query = () => {
    const request = ++revision;
    void environment.readScreenReader().then((enabled) => {
      if (!disposed && request === revision) apply(enabled);
    }).catch(() => {});
  };
  const resume = () => {
    if (disposed) return;
    if (suspended) {
      suspended = false;
      onSpeechContextChanged();
    }
    query();
  };
  const subscriptions = [
    environment.onScreenReaderChange((enabled) => {
      if (disposed) return;
      revision += 1;
      apply(enabled);
    }),
    environment.onAppStateChange((state) => {
      if (state === "active") resume();
      else suspended = true;
    }),
    environment.onBlur?.(() => { suspended = true; }),
    environment.onFocus?.(resume),
  ];
  query();
  return () => {
    disposed = true;
    revision += 1;
    subscriptions.forEach((subscription) => subscription?.remove());
  };
}
