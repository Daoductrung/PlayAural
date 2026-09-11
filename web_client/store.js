export const HISTORY_BUFFER_ORDER = Object.freeze(["all", "chat", "game", "system", "misc"]);
export const HISTORY_BUFFER_LIMIT = 500;

function createHistoryBuffers() {
  return Object.fromEntries(HISTORY_BUFFER_ORDER.map((name) => [name, []]));
}

function createHistoryRevisions() {
  return Object.fromEntries(HISTORY_BUFFER_ORDER.map((name) => [name, 0]));
}

export function normalizeHistoryBuffer(buffer) {
  if (buffer === "chats") {
    return "chat";
  }
  return HISTORY_BUFFER_ORDER.includes(buffer) ? buffer : "misc";
}

export function normalizeMutedHistoryBuffers(buffers) {
  const normalized = new Set();
  if (Array.isArray(buffers)) {
    for (const buffer of buffers) {
      if (buffer === "chats" || HISTORY_BUFFER_ORDER.includes(buffer)) {
        normalized.add(normalizeHistoryBuffer(buffer));
      }
    }
  }
  return HISTORY_BUFFER_ORDER.filter((buffer) => normalized.has(buffer));
}

function pushCapped(buffer, text) {
  buffer.push(text);
  if (buffer.length > HISTORY_BUFFER_LIMIT) {
    buffer.splice(0, buffer.length - HISTORY_BUFFER_LIMIT);
  }
}

export function createStore() {
  const state = {
    connection: {
      status: "disconnected",
      authenticated: false,
      serverUrl: "",
      username: "",
      lastError: "",
    },
    currentMenu: {
      menuId: null,
      items: [],
      selection: 0,
      multiletterEnabled: true,
      escapeBehavior: "keybind",
      gridEnabled: false,
      gridWidth: 1,
    },
    historyBuffers: createHistoryBuffers(),
    historyRevisions: createHistoryRevisions(),
    historyBuffer: "all",
    audioUnlocked: false,
    pendingInput: null,
    serverOptions: {
      games: [],
      languages: {},
    },
  };

  const listeners = new Set();

  function notify() {
    for (const listener of listeners) {
      listener(state);
    }
  }

  return {
    state,
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    setConnection(patch) {
      Object.assign(state.connection, patch);
      notify();
    },
    setMenu(menuPatch) {
      Object.assign(state.currentMenu, menuPatch);
      notify();
    },
    addHistory(buffer, text, options = {}) {
      const normalized = normalizeHistoryBuffer(buffer);
      pushCapped(state.historyBuffers[normalized], text);
      state.historyRevisions[normalized] += 1;
      if (normalized !== "all" && options.includeAll !== false) {
        pushCapped(state.historyBuffers.all, text);
        state.historyRevisions.all += 1;
      }
      notify();
    },
    clearUi() {
      state.currentMenu = {
        menuId: null,
        items: [],
        selection: 0,
        multiletterEnabled: true,
        escapeBehavior: "keybind",
        gridEnabled: false,
        gridWidth: 1,
      };
      notify();
    },
    setHistoryBuffer(buffer) {
      state.historyBuffer = HISTORY_BUFFER_ORDER.includes(buffer) ? buffer : "all";
      notify();
    },
    setAudioUnlocked(unlocked) {
      state.audioUnlocked = unlocked;
      notify();
    },
    setPendingInput(inputState) {
      state.pendingInput = inputState;
      notify();
    },
    setServerOptions(patch) {
      Object.assign(state.serverOptions, patch);
      notify();
    },
  };
}
