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

test("community catalogs fall back for new menu text and unknown saved locales remain valid", () => {
  const h = languageHarness("pt-BR"); h.open();
  assert.equal(h.localization.getLocale(), "pt");
  assert.equal(h.dialogStateRef.current.title, "Choose a language");
  const unknown = languageHarness("unknown-locale"); unknown.open();
  assert.equal(unknown.dialogStateRef.current.buttons[unknown.dialogStateRef.current.focusIndex].id, "locale:en");
});

test("EN and VI navigation strings retain matching placeholders", () => {
  const en = localizationModule(new URL("../locales/en/client.json", import.meta.url));
  const vi = localizationModule(new URL("../locales/vi/client.json", import.meta.url));
  for (const key of ["locale-menu-title", "locale-menu-current", "locale-changed", "client-help"]) {
    assert.ok(en[key]); assert.ok(vi[key]);
    assert.deepEqual(en[key].match(/\{\w+\}/g), vi[key].match(/\{\w+\}/g));
  }
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
    focusedInputOverlayText: null, focusedHistoryMessage: null, focusedChatItem: null,
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
