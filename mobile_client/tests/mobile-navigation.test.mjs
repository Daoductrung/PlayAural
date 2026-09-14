import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import ts from "typescript";

const appUrl = new URL("../src/app/PlayAuralApp.tsx", import.meta.url);
const app = ts.createSourceFile(appUrl.pathname, readFileSync(appUrl, "utf8"), ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const declarations = new Map();
const effects = [];
function visit(node) {
  if (ts.isVariableDeclaration(node)) declarations.set(node.name.getText(app), node.initializer);
  if (ts.isCallExpression(node) && node.expression.getText(app) === "useEffect") effects.push(node);
  ts.forEachChild(node, visit);
}
visit(app);

function compile(source, scope = {}) {
  const module = { exports: {} };
  const js = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
  }).outputText;
  new Function("module", "exports", ...Object.keys(scope), js)(module, module.exports, ...Object.values(scope));
  return module.exports;
}
function handler(name, scope) {
  const expression = ts.createPrinter().printNode(ts.EmitHint.Expression, declarations.get(name), app);
  return compile(`module.exports = ${expression};`, { useCallback: (fn) => fn, useMemo: (fn) => fn(), ...scope });
}
function localizationModule(url) {
  if (url.pathname.endsWith(".json")) return JSON.parse(readFileSync(url, "utf8"));
  return compile(readFileSync(url, "utf8"), {
    require: (id) => localizationModule(new URL(id.endsWith(".json") ? id : `${id}.ts`, url)),
  });
}
const { MobileLocalization } = localizationModule(new URL("../src/i18n/localization.ts", import.meta.url));
const { BUFFER_NAMES, BufferStore, normalizeBufferName } = compile(
  readFileSync(new URL("../src/state/BufferStore.ts", import.meta.url), "utf8"),
);

function languageHarness(locale = "vi", overrides = {}) {
  const localization = new MobileLocalization();
  localization.setLocale(locale);
  const calls = [];
  const dialogStateRef = { current: null };
  const scope = {
    localization, appLocale: localization.getLocale(), storageReady: true, connected: false, dialogStateRef,
    openDialog: (dialog) => { dialogStateRef.current = dialog; },
    closeDialog: () => { dialogStateRef.current = null; calls.push("close"); },
    applyLocale: (value) => { calls.push(["locale", value]); localization.setLocale(value); },
    announceInterfaceFeedback: (value) => calls.push(["feedback", value]),
    tts: { stop: () => calls.push("stop"), setCurrentUiTextProvider: () => {} },
    ...overrides,
  };
  return { open: handler("openLanguageMenu", scope), scope, calls, localization, dialogStateRef };
}

test("language menu discovers every bundled catalog, uses stable ids, and focuses the current choice", () => {
  const h = languageHarness(); h.open();
  const menu = h.dialogStateRef.current;
  const languages = h.localization.getAvailableLocales();
  assert.deepEqual(menu.buttons.slice(0, -1).map((row) => row.id), languages.map((locale) => `locale:${locale}`));
  assert.equal(menu.buttons[menu.focusIndex].id, "locale:vi");
  assert.equal(menu.buttons.filter((row) => row.checked).length, 1);
  assert.equal(menu.buttons.at(-1).id, "cancel");
  assert.equal(menu.returnFocusKey, "auth:locale");
  assert.deepEqual(h.calls, [], "Opening the selector must not change the language");
});

test("locale metadata exposes text direction without changing locale resolution", () => {
  const localization = new MobileLocalization();
  assert.equal(localization.getTextDirection("fa"), "rtl");
  assert.equal(localization.getTextDirection("fa-IR"), "rtl");
  assert.equal(localization.getTextDirection("en"), "ltr");
  assert.equal(localization.getTextDirection("unsupported-locale"), "ltr");
});

test("text direction follows the app locale without enabling global layout mirroring", () => {
  const source = readFileSync(appUrl, "utf8");
  assert.match(source, /getTextDirection\(appLocale\)/u);
  assert.match(source, /direction: "rtl",\s+writingDirection: "rtl"/u);
  assert.match(source, /direction: "ltr",\s+writingDirection: "ltr"/u);
  assert.doesNotMatch(source, /I18nManager/u);
});

test("selecting a language closes the menu and announces in the newly selected locale", () => {
  const h = languageHarness("en"); h.open();
  h.dialogStateRef.current.buttons.find((row) => row.id === "locale:vi").onPress();
  assert.equal(h.dialogStateRef.current, null);
  assert.deepEqual(h.calls.slice(0, 3), ["close", "stop", ["locale", "vi"]]);
  assert.deepEqual(h.calls[3], ["feedback", "Ngôn ngữ: Tiếng Việt."]);
});

test("Back preserves the language and selecting the current language does not cycle", () => {
  const h = languageHarness(); h.open();
  h.dialogStateRef.current.buttons.at(-1).onPress();
  assert.equal(h.localization.getLocale(), "vi");
  assert.deepEqual(h.calls, ["close"]);
  h.open(); h.dialogStateRef.current.buttons.find((row) => row.checked).onPress();
  assert.equal(h.localization.getLocale(), "vi");
});

test("stale language activations cannot change a replaced or closed dialog", () => {
  const h = languageHarness(); h.open();
  const select = h.dialogStateRef.current.buttons[0].onPress;
  h.dialogStateRef.current = { id: "mandatory-app-update" };
  select(); assert.deepEqual(h.calls, []);
  h.dialogStateRef.current = { id: "language-selection", buttons: [] };
  select(); assert.deepEqual(h.calls, []);
  h.dialogStateRef.current = null;
  select(); assert.deepEqual(h.calls, []);
});

test("language selection waits for preferences and cannot cover an active session or another dialog", () => {
  for (const overrides of [{ storageReady: false }, { connected: true }, { dialogStateRef: { current: { id: "update" } } }]) {
    let opened = false;
    const h = languageHarness("en", { ...overrides, openDialog: () => { opened = true; } });
    h.open(); assert.equal(opened, false);
  }
});

test("community catalogs localize new menu text and unknown saved locales remain valid", () => {
  const h = languageHarness("pt-BR"); h.open();
  assert.equal(h.localization.getLocale(), "pt");
  assert.equal(h.dialogStateRef.current.title, "Escolha um idioma");
  assert.equal(h.localization.t("history-buffer-current", { name: "Game" }), "Buffer: Game");
  const unknown = languageHarness("unknown-locale"); unknown.open();
  assert.equal(unknown.dialogStateRef.current.buttons[unknown.dialogStateRef.current.focusIndex].id, "locale:en");
});

test("EN, PT, and VI navigation strings retain matching placeholders", () => {
  const en = localizationModule(new URL("../locales/en/client.json", import.meta.url));
  const pt = localizationModule(new URL("../locales/pt/client.json", import.meta.url));
  const vi = localizationModule(new URL("../locales/vi/client.json", import.meta.url));
  for (const key of [
    "locale-menu-title", "locale-menu-current", "locale-changed", "client-help",
    "history-buffer-current", "history-buffer-muted-name", "history-buffer-menu-title",
    "history-buffer-menu-current", "history-buffer-mute", "history-buffer-unmute",
    "history-buffer-muted-by-all", "history-buffer-muted-empty", "main-buffer-status", "main-buffer-info",
  ]) {
    assert.ok(en[key]); assert.ok(pt[key]); assert.ok(vi[key]);
    assert.deepEqual(en[key].match(/\{\w+\}/g), pt[key].match(/\{\w+\}/g));
    assert.deepEqual(en[key].match(/\{\w+\}/g), vi[key].match(/\{\w+\}/g));
  }
});

test("EN, PT, and VI mobile buffer terminology matches the desktop and web contracts", () => {
  const en = localizationModule(new URL("../locales/en/client.json", import.meta.url));
  const pt = localizationModule(new URL("../locales/pt/client.json", import.meta.url));
  const vi = localizationModule(new URL("../locales/vi/client.json", import.meta.url));
  const parity = {
    "buffer-all": ["All", "Tudo", "Tất cả"],
    "buffer-chat": ["Chat", "Bate-papo", "Trò chuyện"],
    "buffer-private": ["Private Messages", "Mensagens privadas", "Tin nhắn riêng"],
    "buffer-game": ["Game", "Jogo", "Trò chơi"],
    "buffer-system": ["System", "Sistema", "Hệ thống"],
    "buffer-misc": ["Misc", "Diversos", "Linh tinh"],
    "buffer-name-all": ["all", "tudo", "tất cả"],
    "buffer-name-chat": ["Chat", "Bate-papo", "Trò chuyện"],
    "buffer-name-private": ["private messages", "mensagens privadas", "tin nhắn riêng"],
    "buffer-name-game": ["game", "jogo", "trò chơi"],
    "buffer-name-system": ["system", "sistema", "hệ thống"],
    "buffer-name-misc": ["misc", "diversos", "linh tinh"],
    "buffer-status-muted": ["muted", "silenciado", "đã tắt tiếng"],
    "buffer-status-unmuted": ["unmuted", "não silenciado", "đã bật tiếng"],
    "main-status-muted-suffix": [", muted", ", silenciado", ", đã tắt tiếng"],
    "main-buffer-status": ["Buffer {name} {status}.", "Buffer {name} {status}.", "Bộ đệm {name} {status}."],
    "main-buffer-info": ["{name}{status}. {count} items", "{name}{status}. {count} itens", "{name}{status}. {count} mục"],
  };
  for (const [key, [english, portuguese, vietnamese]] of Object.entries(parity)) {
    assert.equal(en[key], english);
    assert.equal(pt[key], portuguese);
    assert.equal(vi[key], vietnamese);
  }
});

test("stored muted-buffer preferences are migrated to canonical values", () => {
  const buffers = new BufferStore();
  const preferencesRef = { current: { retained: "value" } };
  let persistedPreferences = null;
  let revision = 0;
  const applyPreferenceUpdates = handler("applyPreferenceUpdates", {
    buffers,
    preferencesRef,
    setHistoryRevision: (update) => { revision = update(revision); },
    setPreferences: (value) => { persistedPreferences = value; },
  });

  applyPreferenceUpdates({ muted_buffers: ["chats", "bogus", "all", "chat"] });
  assert.deepEqual(preferencesRef.current, {
    retained: "value",
    muted_buffers: ["all", "chat"],
  });
  assert.deepEqual(persistedPreferences, preferencesRef.current);
  assert.equal(revision, 1);

  applyPreferenceUpdates({ muted_buffers: ["all", "chat"] });
  assert.deepEqual(preferencesRef.current.muted_buffers, ["all", "chat"]);
  assert.equal(revision, 1, "An equivalent canonical preference must not repaint History");
});

test("History buffer selection is ordered, modal-safe, and restores its opener", () => {
  const calls = [];
  const dialogStateRef = { current: null };
  const openHistoryBufferMenu = handler("openHistoryBufferMenu", {
    BUFFER_NAMES,
    closeDialog: () => { dialogStateRef.current = null; calls.push("close"); },
    dialogStateRef,
    getHistoryBufferOptionName: (buffer) => buffer === "game" ? "[Muted] Game" : buffer,
    historyBuffer: "game",
    inputStateRef: { current: null },
    localization: {
      t: (key, params = {}) => key === "history-buffer-menu-current"
        ? `${params.name}. Current buffer.` : key,
    },
    modeRef: { current: "history" },
    openDialog: (dialog) => { dialogStateRef.current = dialog; },
    selectHistoryBuffer: (buffer) => calls.push(["select", buffer]),
  });

  openHistoryBufferMenu();
  const dialog = dialogStateRef.current;
  assert.deepEqual(dialog.buttons.slice(0, -1).map((button) => button.id),
    BUFFER_NAMES.map((buffer) => `buffer:${buffer}`));
  assert.equal(dialog.buttons[0].id, "buffer:all");
  assert.equal(dialog.buttons[dialog.focusIndex].id, "buffer:game");
  assert.equal(dialog.buttons[dialog.focusIndex].checked, true);
  assert.equal(dialog.buttons[dialog.focusIndex].text, "[Muted] Game. Current buffer.");
  assert.equal(dialog.buttons.at(-1).id, "cancel");
  assert.equal(dialog.returnFocusKey, "history:buffer");

  const selectChat = dialog.buttons.find((button) => button.id === "buffer:chat").onPress;
  dialogStateRef.current = { id: "replacement", buttons: [] };
  selectChat();
  assert.deepEqual(calls, [], "A stale selector must not change the active filter");
  dialogStateRef.current = dialog;
  selectChat();
  assert.deepEqual(calls, ["close", ["select", "chat"]]);
});

test("History mute updates direct settings but explains inherited All mute", () => {
  const directBuffers = new BufferStore();
  const updates = [];
  const feedback = [];
  let focusIndex = 0;
  handler("toggleHistoryBufferMute", {
    BUFFER_NAMES,
    applyPreferenceUpdates: (value) => updates.push(value),
    buffers: directBuffers,
    deliverInterfaceFeedback: (value) => feedback.push(value),
    historyBuffer: "chat",
    historyBufferMutedByAll: false,
    historyMuteFocusIndex: 4,
    historyMuteControlText: "Mute Chat",
    localization: { t: (key, params = {}) => `${key}:${params.name ?? ""}:${params.status ?? ""}` },
    setHistoryIndex: (value) => { focusIndex = value; },
  })();
  assert.deepEqual(updates, [{ muted_buffers: ["chat"] }]);
  assert.equal(focusIndex, 4);
  assert.equal(feedback.length, 1);

  updates.length = 0;
  feedback.length = 0;
  directBuffers.setMutedBuffers(["all"]);
  handler("toggleHistoryBufferMute", {
    BUFFER_NAMES,
    applyPreferenceUpdates: (value) => updates.push(value),
    buffers: directBuffers,
    deliverInterfaceFeedback: (value) => feedback.push(value),
    historyBuffer: "chat",
    historyBufferMutedByAll: true,
    historyMuteFocusIndex: 4,
    historyMuteControlText: "Chat is muted by All",
    localization: { t: (key) => key },
    setHistoryIndex: () => {},
  })();
  assert.deepEqual(updates, []);
  assert.deepEqual(feedback, ["Chat is muted by All"]);
});

test("server speech is retained but never voiced through a muted or malformed buffer", () => {
  const buffers = new BufferStore();
  const spoken = [];
  let revision = 0;
  const handleSpeakPacket = handler("handleSpeakPacket", {
    buffers,
    localization: { has: () => false, t: (key) => key },
    localizeServerMessage: (text) => text,
    normalizeBufferName,
    setHistoryRevision: (update) => { revision = update(revision); },
    speakServerAnnouncement: (text) => spoken.push(text),
    toLocalizationParams: () => ({}),
  });

  handleSpeakPacket({ buffer: "game", text: "game update" });
  buffers.setMutedBuffers(["chat"]);
  handleSpeakPacket({ buffer: "chat", text: "quiet chat" });
  handleSpeakPacket({ buffer: "unknown", text: "fallback output" });
  handleSpeakPacket({ buffer: "system", muted: true, text: "server-muted" });

  assert.deepEqual(spoken, ["game update", "fallback output"]);
  assert.deepEqual(buffers.getMessages("chat").map((item) => item.text), ["quiet chat"]);
  assert.deepEqual(buffers.getMessages("misc").map((item) => item.text), ["fallback output"]);
  assert.equal(buffers.getMessages("all").some((item) => item.text === "quiet chat"), false);
  assert.equal(revision, 4);
});

test("chat buffer mute suppresses its notification sound and TTS in both speech modes", () => {
  const buffers = new BufferStore();
  buffers.setMutedBuffers(["chat"]);
  const effects = [];
  let revision = 0;
  const handleChatPacket = handler("handleChatPacket", {
    audio: {
      playSound: (asset) => effects.push(["sound", asset]),
      playSoundFamily: (family) => effects.push(["family", family]),
    },
    buffers,
    formatChatMessage: (_localization, packet) => packet.message,
    localization: {},
    preferencesRef: { current: {} },
    setHistoryRevision: (update) => { revision = update(revision); },
    speakServerAnnouncement: (text) => effects.push(["speech", text]),
  });

  handleChatPacket({ convo: "global", message: "quiet chat" });
  assert.deepEqual(effects, []);
  assert.deepEqual(buffers.getMessages("chat").map((item) => item.text), ["quiet chat"]);
  assert.deepEqual(buffers.getMessages("all"), []);
  assert.equal(revision, 1);
});

test("self-voicing History visits the buffer controls before newest-first messages", () => {
  const historyControlFocusItems = handler("historyControlFocusItems", {
    historyBufferControlText: "Buffer: All",
    historyMuteControlText: "Mute all buffer",
  });
  const items = handler("historyFocusItems", {
    historyControlFocusItems,
    historyEmptyText: "Buffer empty.",
    historyMessages: [
      { id: "message:2", text: "newest" },
      { id: "message:1", text: "oldest" },
    ],
  });
  assert.deepEqual(items.map(({ id, kind }) => [id, kind]), [
    ["buffer", "buffer"],
    ["mute", "mute"],
    ["message:2", "message"],
    ["message:1", "message"],
  ]);
});

test("empty History keeps both controls and a stable spoken empty row", () => {
  const historyControlFocusItems = handler("historyControlFocusItems", {
    historyBufferControlText: "Buffer: Game",
    historyMuteControlText: "Unmute game buffer",
  });
  const items = handler("historyFocusItems", {
    historyControlFocusItems,
    historyEmptyText: "The game buffer is muted.",
    historyMessages: [],
  });
  assert.deepEqual(items.map(({ id, kind, text }) => [id, kind, text]), [
    ["buffer", "buffer", "Buffer: Game"],
    ["mute", "mute", "Unmute game buffer"],
    ["empty", "empty", "The game buffer is muted."],
  ]);
});

test("self-voicing auth order follows the displayed controls and never includes hidden fields", () => {
  const localization = new MobileLocalization();
  for (const authMode of ["login", "register", "forgot", "reset"]) {
    const items = handler("authFocusableItems", { connected: false, localization, appLocale: "en", authMode, username: "", password: "" });
    const ids = items.map((item) => item.id);
    assert.deepEqual(ids.slice(0, 4), ["locale", "tab-login", "tab-register", "tab-forgot"]);
    assert.equal(ids.includes("field-username"), authMode === "login" || authMode === "register");
    assert.deepEqual(ids.slice(-2), ["help", "button-exit"]);
  }
});

test("dialog focus text and identity take precedence over the hidden landing form", () => {
  const scope = {
    connected: false, dialogState: { id: "language-selection", focusIndex: 1 },
    focusedDialogButton: { id: "locale:es", text: "Español" },
    focusedAuthItem: { id: "field-password" }, inputState: null,
    focusedInputOverlayText: null, focusedHistoryItem: null, focusedChatItem: null,
    focusedMenuItem: null, focusedShortcutItem: null,
    getAuthFocusSpeechText: () => "Hidden password", getChatFocusSpeechText: () => null,
    localization: new MobileLocalization(), menuState: { items: [], focusIndex: 0 }, mode: "main",
    authMode: "login", chatFocusIndex: 0, historyIndex: 0, inputOverlayFocus: 0, shortcutFocusIndex: 0,
  };
  assert.equal(handler("getCurrentUiFocusText", scope)(), "Español");
  assert.equal(handler("getCurrentUiFocusSignature", scope)(), "dialog:language-selection:1:locale:es:Español");
});

test("closing a local menu restores its opener without changing speech preferences", () => {
  const effects = [];
  const dialogStateRef = { current: { returnFocusKey: "auth:locale" } };
  handler("closeDialog", {
    dialogStateRef,
    clearScheduledNativeFocus: () => effects.push("clear"),
    setDialogState: (value) => effects.push(value),
    queueNativeAccessibilityFocus: (key) => effects.push(key),
  })();
  assert.equal(dialogStateRef.current, null);
  assert.deepEqual(effects, ["clear", null, "auth:locale"]);
});

test("a delayed Help activation cannot replace another dialog or cover server input", () => {
  for (const state of ["loading", "dialog", "input", "ready"]) {
    const opened = [];
    handler("openClientHelp", {
      storageReady: state !== "loading",
      dialogStateRef: { current: state === "dialog" ? { id: "mandatory-app-update" } : null },
      inputStateRef: { current: state === "input" ? { inputId: "server-input" } : null },
      localization: new MobileLocalization(), MOBILE_BUILD_STAMP: "test", closeDialog: () => {},
      openDialog: (dialog) => opened.push(dialog),
    })("client:help");
    assert.equal(opened.length, state === "ready" ? 1 : 0);
    if (opened.length) assert.equal(opened[0].returnFocusKey, "client:help");
  }
});

test("late dialog focus events cannot move focus or interrupt speech in a replacement dialog", () => {
  const rendered = { id: "language-selection", buttons: [{ id: "locale:en" }, { id: "cancel" }], focusIndex: 0 };
  const calls = [];
  const dialogStateRef = { current: { id: "mandatory-app-update", buttons: [{ id: "confirm" }], focusIndex: 0 } };
  const focus = handler("focusDialogButton", {
    dialogStateRef,
    markNativeScreenReaderInteraction: (key) => calls.push(key),
    setDialogState: (value) => { dialogStateRef.current = value; calls.push(value.focusIndex); },
  });
  focus(rendered, 1);
  assert.deepEqual(calls, []);
  dialogStateRef.current = null;
  focus(rendered, 0);
  assert.deepEqual(calls, []);
  dialogStateRef.current = rendered;
  focus(rendered, 99);
  assert.deepEqual(calls, []);
  focus(rendered, 1);
  assert.deepEqual(calls, ["dialog:language-selection:cancel", 1]);
});

test("input focus waits for a covering dialog to close and rejects superseded timers", () => {
  const effect = effects.find((node) => node.arguments[0].getText(app).includes("const focusInputOverlay ="));
  const expression = ts.createPrinter().printNode(ts.EmitHint.Expression, effect, app);
  const inputState = { inputId: "pending-input", readOnly: false };
  const dialogStateRef = { current: { id: "client-help" } };
  const timers = [];
  let focused = 0;
  const scope = {
    inputState, inputStateRef: { current: inputState }, dialogStateRef,
    inputOverlayInputRef: { current: { focus: () => { focused += 1; } } },
    Platform: { OS: "android" },
    useEffect: (run, dependencies) => ({ run, dependencies }),
    setTimeout: (fn) => { timers.push(fn); return timers.length; }, clearTimeout: () => {},
  };
  const covered = compile(`module.exports = ${expression};`, { ...scope, dialogState: dialogStateRef.current });
  covered.run();
  assert.equal(timers.length, 0);
  dialogStateRef.current = null;
  const uncovered = compile(`module.exports = ${expression};`, { ...scope, dialogState: null });
  assert.notDeepEqual(uncovered.dependencies, covered.dependencies, "Closing Help must reschedule pending input focus");
  const cleanup = uncovered.run();
  timers[0]();
  assert.equal(focused, 1);
  dialogStateRef.current = { id: "replacement" };
  timers[1]();
  assert.equal(focused, 1);
  dialogStateRef.current = null;
  cleanup();
  timers[1]();
  assert.equal(focused, 1);
});

test("a modified activation cannot act on a hidden game menu through an overlay", () => {
  for (const overlay of ["dialog", "input", "chat", "history", "shortcuts", "main"]) {
    let sent = false;
    handler("handleModifiedActivate", {
      audio: { handleUserInteraction: () => {} }, connected: true,
      dialogStateRef: { current: overlay === "dialog" ? {} : null },
      inputStateRef: { current: overlay === "input" ? {} : null },
      modeRef: { current: ["dialog", "input"].includes(overlay) ? "main" : overlay },
      sendShiftEnter: () => { sent = true; },
    })();
    assert.equal(sent, overlay === "main");
  }
});

test("Back cancels the current dialog when a server update replaced the rendered one", () => {
  const effects = [];
  handler("handleSystemSwipe", {
    audio: { handleUserInteraction: () => {} }, menuStateRef: { current: {} },
    dialogStateRef: { current: { buttons: [{ id: "cancel", onPress: () => effects.push("current") }] } },
    dialogState: { buttons: [{ id: "cancel", onPress: () => effects.push("stale") }] },
  })("up");
  assert.deepEqual(effects, ["current"]);
});

test("a queued activation never confirms a replacement dialog", () => {
  let activated = false;
  handler("handlePrimaryActivate", {
    audio: { handleUserInteraction: () => {} },
    dialogState: { buttons: [] }, dialogStateRef: { current: { buttons: [] } },
    playMenuActivateSound: () => {}, activateDialogButton: () => { activated = true; },
  })();
  assert.equal(activated, false);
});

const { focusScrollOffset } = compile(readFileSync(new URL("../src/app/useFocusScroll.ts", import.meta.url), "utf8"), {
  require: () => ({}),
});
test("focus scrolling handles visible, clipped, oversized, and unmeasured rows without unnecessary jumps", () => {
  assert.equal(focusScrollOffset(100, 120, 48, 100, 300), 100);
  assert.equal(focusScrollOffset(100, 70, 48, 100, 300), 70);
  assert.equal(focusScrollOffset(100, 380, 48, 100, 300), 128);
  assert.equal(focusScrollOffset(100, 80, 500, 100, 300), 80);
  assert.equal(focusScrollOffset(10, 0, 48, 100, 300), 0);
  assert.equal(focusScrollOffset(100, 500, 48, 100, 0), 100);
});

test("late native measurements cannot scroll a removed focus target or an unmounted screen", () => {
  const frames = new Map();
  const cleanups = [];
  let frameId = 0;
  let finishMeasurement;
  const scrolls = [];
  const node = { measureInWindow: (callback) => { finishMeasurement = callback; } };
  const nodes = { current: new Map([["choice", node]]) };
  const { useFocusScroll } = compile(readFileSync(new URL("../src/app/useFocusScroll.ts", import.meta.url), "utf8"), {
    require: (id) => id === "react" ? {
      useRef: (current) => ({ current }),
      useCallback: (fn) => fn,
      useLayoutEffect: (fn) => cleanups.push(fn()),
    } : { Platform: { OS: "android" } },
    requestAnimationFrame: (fn) => { frames.set(++frameId, fn); return frameId; },
    cancelAnimationFrame: (id) => frames.delete(id),
  });
  const props = useFocusScroll("choice", nodes);
  props.ref({
    getNativeScrollRef: () => ({ measureInWindow: (callback) => callback(0, 100, 300, 400) }),
    scrollTo: (value) => scrolls.push(value),
  });
  const flush = () => { const pending = [...frames.values()]; frames.clear(); pending.forEach((fn) => fn()); };
  flush();
  nodes.current.delete("choice");
  finishMeasurement(0, 800, 300, 48);
  assert.deepEqual(scrolls, []);
  nodes.current.set("choice", node);
  props.onLayout(); flush();
  cleanups.forEach((cleanup) => cleanup());
  finishMeasurement(0, 800, 300, 48);
  assert.deepEqual(scrolls, []);
});

test("Back uses the visible input before the local tab hidden underneath it", () => {
  const calls = [];
  handler("handleSystemSwipe", {
    audio: { handleUserInteraction: () => {} }, menuStateRef: { current: { menuId: "online_users" } },
    dialogStateRef: { current: null }, inputStateRef: { current: { inputId: "pending" } },
    cancelInputOverlay: () => calls.push("cancel-input"), closeOverlay: () => calls.push("close-tab"),
  })("up");
  assert.deepEqual(calls, ["cancel-input"]);
});

test("Back after leaving Shortcuts reads current tab state instead of consuming a stale overlay close", () => {
  const sent = [];
  const modeRef = { current: "main" };
  const closeOverlay = handler("closeOverlay", { mode: "shortcuts", modeRef });
  handler("handleSystemSwipe", {
    mode: "shortcuts", modeRef, connected: true, closeOverlay,
    audio: { handleUserInteraction: () => {} }, dialogStateRef: { current: null }, inputStateRef: { current: null },
    menuStateRef: { current: { menuId: "online_users", escapeBehavior: "escape_event", items: [{ id: "back" }] } },
    sendEscapeEquivalent: (...args) => sent.push(args),
  })("up");
  assert.deepEqual(sent, [["online_users", "escape_event", [{ id: "back" }]]]);
});

test("Back routes server escape contracts like desktop and never selects an empty menu", () => {
  for (const behavior of ["escape_event", "keybind", "select_first_option", "select_last_option"]) {
    const sent = [];
    const send = handler("sendEscapeEquivalent", {
      isProtectedTransientMenu: () => false, requestNativeMenuFocusOnNextPacket: () => {},
      connection: { send: (packet) => sent.push(packet) },
    });
    send("menu", behavior, [{ id: "first" }, { id: "last" }]);
    const expected = behavior === "escape_event" ? { type: "escape", menu_id: "menu" }
      : behavior === "keybind" ? { type: "keybind", menu_id: "menu", key: "escape" }
      : { type: "menu", menu_id: "menu", selection: behavior === "select_first_option" ? 1 : 2,
          selection_id: behavior === "select_first_option" ? "first" : "last" };
    assert.deepEqual(sent, [expected]);
    if (behavior.startsWith("select_")) {
      send("menu", behavior, []);
      assert.equal(sent.length, 1);
    }
  }
});

test("Back from the landing screen exits locally and cannot send a server action", () => {
  let exited = false;
  handler("handleSystemSwipe", {
    audio: { handleUserInteraction: () => {} }, menuStateRef: { current: {} }, connected: false,
    dialogStateRef: { current: null }, inputStateRef: { current: null }, closeOverlay: () => false,
    exitApplication: () => { exited = true; },
  })("up");
  assert.equal(exited, true);
});

test("online-list refreshes preserve escape behavior and stable focus through repeated presence changes", () => {
  const { resolveMenuFocusIndex } = compile(readFileSync(new URL("../src/app/menuFocus.ts", import.meta.url), "utf8"));
  const menuStateRef = { current: { menuId: "main_menu", items: [], focusIndex: 0 } };
  const normalize = app.statements.find((node) => ts.isFunctionDeclaration(node) && node.name.text === "normalizeMenuItems");
  const normalizeMenuItems = compile(`module.exports = ${normalize.getText(app)};`);
  const apply = handler("applyMenuPacket", {
    inputStateRef: { current: null }, menuStateRef, normalizeMenuItems, resolveMenuFocusIndex,
    transientTurnMenuAllowanceRef: { current: null }, isProtectedTransientMenu: () => false,
    nativeMenuFocusOnNextPacketRef: { current: false }, nativeMenuFocusRequestedAtRef: { current: 0 },
    nativeScreenReaderModeRef: { current: false }, setMenuState: (state) => { menuStateRef.current = state; },
  });
  const back = { id: "back", text: "Close" };
  const alice = { id: "online_alice", text: "Alice" };
  apply({ type: "menu", menu_id: "online_users", escape_behavior: "escape_event", items: [back, alice], selection_id: alice.id });
  for (const extras of [[{ id: "online_bob", text: "Bob" }], [], [{ id: "online_chris", text: "Chris" }]]) {
    apply({ type: "update_menu", menu_id: "online_users", items: [back, ...extras, alice] });
    assert.equal(menuStateRef.current.escapeBehavior, "escape_event");
    assert.equal(menuStateRef.current.items[menuStateRef.current.focusIndex].id, alice.id);
  }
  apply({ type: "menu", menu_id: "turn_menu", items: [{ id: "play", text: "Play" }] });
  assert.equal(menuStateRef.current.escapeBehavior, "keybind");
});

test("board geometry preserves readable controls for wide, tall, small, and large grids", () => {
  const { gridCellSizeForViewport } = compile(readFileSync(new URL("../src/app/gridLayout.ts", import.meta.url), "utf8"));
  for (const [columns, rows] of [[2, 2], [8, 8], [30, 2], [2, 30], [30, 30]]) {
    for (const minimum of [48, 96]) {
      const size = gridCellSizeForViewport(columns, rows, 320, 400, 8, minimum);
      assert.ok(size >= minimum);
      if (columns * minimum > 320 || rows * minimum > 400) assert.equal(size, minimum);
    }
  }
  assert.equal(gridCellSizeForViewport(8, 8, 0, 0, 8, 72), 72);
});

test("horizontal focus reveal scrolls the correct axis and uses the actual scroll offset", () => {
  const frames = [];
  const scrolls = [];
  const { useFocusScroll } = compile(readFileSync(new URL("../src/app/useFocusScroll.ts", import.meta.url), "utf8"), {
    require: (id) => id === "react" ? {
      useRef: (current) => ({ current }), useCallback: (fn) => fn, useLayoutEffect: (fn) => fn(),
    } : { Platform: { OS: "android" } },
    requestAnimationFrame: (fn) => { frames.push(fn); return frames.length; }, cancelAnimationFrame: () => {},
  });
  const props = useFocusScroll("cell", { current: new Map([["cell", { measureInWindow: (fn) => fn(400, 20, 72, 72) }]]) }, true);
  assert.equal(props.scrollEnabled, false, "Native dragging must yield to self-voicing gestures");
  assert.equal(useFocusScroll(null, { current: new Map() }, true).scrollEnabled, true);
  props.ref({ getNativeScrollRef: () => ({ measureInWindow: (fn) => fn(20, 20, 300, 400) }), scrollTo: (value) => scrolls.push(value) });
  props.onScroll({ nativeEvent: { contentOffset: { x: 90, y: 0 } } });
  frames[0]();
  assert.deepEqual(scrolls, [{ x: 242, animated: false }]);
});

test("rapid board navigation speaks and advances the latest cursor before any render or visual scroll", () => {
  const nextGridNode = app.statements.find((node) => ts.isFunctionDeclaration(node) && node.name.text === "nextGridIndex");
  const nextGridIndex = compile(`module.exports = ${nextGridNode.getText(app)};`);
  const items = Array.from({ length: 144 }, (_, index) => ({ id: `cell_${index}`, text: `Cell ${index}` }));
  const menuStateRef = { current: { menuId: "turn_menu", items, gridEnabled: true, gridWidth: 12, focusIndex: 0 } };
  const renders = [], spoken = [];
  const move = handler("handleDirectionalNavigation", {
    audio: { handleUserInteraction() {} }, dialogStateRef: { current: null }, inputStateRef: { current: null },
    connected: true, modeRef: { current: "main" },
    menuStateRef, nextGridIndex, setMenuState: (value) => renders.push(value),
    speakUserFocus: (text) => spoken.push(text), playMenuMoveSound() {},
  });
  for (let i = 0; i < 15; i++) move("right");
  assert.equal(menuStateRef.current.focusIndex, 11);
  assert.deepEqual(spoken, items.slice(1, 12).map((item) => item.text));
  for (let i = 0; i < 15; i++) move("down");
  assert.equal(menuStateRef.current.focusIndex, 143);
  move("up"); move("left");
  assert.equal(menuStateRef.current.focusIndex, 130);
  assert.equal(spoken.at(-1), "Cell 130");
  assert.equal(renders.every((value) => typeof value !== "function"), true, "Speech must not be deferred into a React updater");
});

test("a newly arrived dialog owns directional navigation before its first render", () => {
  let navigatedDialog = false;
  handler("handleDirectionalNavigation", {
    audio: { handleUserInteraction() {} }, dialogState: null,
    dialogStateRef: { current: { id: "current-dialog" } }, inputStateRef: { current: null }, modeRef: { current: "main" },
    setDialogState: () => { navigatedDialog = true; },
    setMenuState: () => assert.fail("The covered board must not receive the gesture"),
  })("right");
  assert.equal(navigatedDialog, true);
});

test("a boundary jump followed by a direction uses the new board cursor before repaint", () => {
  const nextGridNode = app.statements.find((node) => ts.isFunctionDeclaration(node) && node.name.text === "nextGridIndex");
  const nextGridIndex = compile(`module.exports = ${nextGridNode.getText(app)};`);
  const items = Array.from({ length: 144 }, (_, index) => ({ id: `cell_${index}`, text: `Cell ${index}` }));
  const menuStateRef = { current: { items, gridEnabled: true, gridWidth: 12, focusIndex: 0 } };
  const spoken = [];
  const bindings = {
    audio: { handleUserInteraction() {} }, dialogStateRef: { current: null }, inputStateRef: { current: null },
    connected: true, modeRef: { current: "main" }, menuStateRef, nextGridIndex,
    setMenuState: (value) => assert.equal(typeof value, "object"),
    speakUserFocus: (text) => spoken.push(text), playMenuMoveSound() {},
  };
  const jump = handler("handleBoundaryJump", bindings);
  const move = handler("handleDirectionalNavigation", bindings);
  jump("bottom"); move("left"); move("up");
  assert.equal(menuStateRef.current.focusIndex, 130);
  assert.deepEqual(spoken, ["Cell 143", "Cell 142", "Cell 130"]);
  jump("top"); move("right");
  assert.equal(menuStateRef.current.focusIndex, 1);
  assert.equal(spoken.at(-1), "Cell 1");
});

test("two-axis focus reveal uses one measurement and one scroll command", () => {
  const frames = [], scrolls = [];
  let measured = 0;
  const { useFocusScroll } = compile(readFileSync(new URL("../src/app/useFocusScroll.ts", import.meta.url), "utf8"), {
    require: (id) => id === "react" ? {
      useRef: (current) => ({ current }), useCallback: (fn) => fn, useLayoutEffect: (fn) => fn(),
    } : { Platform: { OS: "ios" } },
    requestAnimationFrame: (fn) => { frames.push(fn); return frames.length; }, cancelAnimationFrame() {},
  });
  const props = useFocusScroll("cell", { current: new Map([["cell", { measureInWindow: (fn) => {
    measured++; fn(500, 700, 72, 72);
  } }]]) }, "both");
  props.ref({ getNativeScrollRef: () => ({ measureInWindow: (fn) => fn(20, 100, 300, 400) }), scrollTo: (value) => scrolls.push(value) });
  props.onScroll({ nativeEvent: { contentOffset: { x: 50, y: 90 } } });
  frames[0]();
  assert.equal(measured, 1);
  assert.deepEqual(scrolls, [{ x: 302, y: 362, animated: false }]);
});
