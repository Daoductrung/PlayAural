import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  HISTORY_BUFFER_LIMIT,
  HISTORY_BUFFER_ORDER,
  createStore,
  normalizeHistoryBuffer,
  normalizeMutedHistoryBuffers,
} from "../store.js";
import {
  HISTORY_COMPACT_MEDIA_QUERY,
  HISTORY_TOUCH_MEDIA_QUERY,
  createHistoryView,
} from "../ui/history.js";

class FakeElement {
  constructor() {
    this.attributes = new Map();
    this.children = [];
    this.hidden = false;
    this.listeners = new Map();
    this.options = [];
    this.scrollHeight = 0;
    this.scrollTop = 0;
    this.textContent = "";
    this.value = "";
  }

  addEventListener(type, listener) {
    this.listeners.set(type, listener);
  }

  contains(element) {
    return element === this || this.children.some((child) => (
      child === element || child?.contains?.(element)
    ));
  }

  dispatch(type) {
    return this.listeners.get(type)?.({ currentTarget: this, type });
  }

  focus() {
    document.activeElement = this;
  }

  getAttribute(name) {
    return this.attributes.get(name) ?? null;
  }

  replaceChildren(...children) {
    this.children = children;
  }

  setAttribute(name, value) {
    this.attributes.set(name, String(value));
  }
}

const strings = {
  "buffer-all": "All",
  "buffer-chat": "Chat",
  "buffer-game": "Game",
  "buffer-system": "System",
  "buffer-misc": "Misc",
  "buffer-name-all": "all",
  "buffer-name-chat": "Chat",
  "buffer-name-game": "game",
  "buffer-name-system": "system",
  "buffer-name-misc": "misc",
  "buffer-status-muted": "muted",
  "buffer-status-unmuted": "unmuted",
  "main-status-muted-suffix": ", muted",
  "main-buffer-status": "Buffer {name} {status}.",
  "main-buffer-info": "{name}{status}. {count} items",
  "main-buffer-empty": "Buffer empty.",
  "history-buffer-muted-name": "[Muted] {name}",
  "history-buffer-mute": "Mute {name} buffer",
  "history-buffer-unmute": "Unmute {name} buffer",
  "history-buffer-muted-by-all": "The {name} buffer is muted by All. Select All to unmute it.",
  "history-buffer-muted-empty": "The {name} buffer is muted. Unmute it to show its history.",
};

function localize(key, params = {}) {
  let value = strings[key] ?? key;
  for (const [name, replacement] of Object.entries(params)) {
    value = value.replaceAll(`{${name}}`, String(replacement));
  }
  return value;
}

function createFixture(initialMutedBuffers = [], { compact = false, touchLike = false } = {}) {
  globalThis.window = {
    matchMedia: (query) => ({
      matches: query === HISTORY_TOUCH_MEDIA_QUERY ? touchLike : (
        query === HISTORY_COMPACT_MEDIA_QUERY && compact
      ),
    }),
  };
  globalThis.requestAnimationFrame = (callback) => {
    callback();
    return 1;
  };
  globalThis.document = {
    activeElement: null,
    createDocumentFragment() {
      return {
        children: [],
        appendChild(child) {
          this.children.push(child);
        },
      };
    },
    createElement() {
      return new FakeElement();
    },
  };

  const historyEl = new FakeElement();
  const historyLogEl = new FakeElement();
  const historyContentEl = new FakeElement();
  const historyToggleEl = new FakeElement();
  const bufferSelectEl = new FakeElement();
  const bufferMuteEl = new FakeElement();
  const bufferControlsEl = new FakeElement();
  bufferControlsEl.children = [bufferSelectEl, bufferMuteEl];
  historyContentEl.children = [historyEl, historyLogEl];
  bufferSelectEl.options = HISTORY_BUFFER_ORDER.map((value) => {
    const option = new FakeElement();
    option.value = value;
    return option;
  });
  bufferSelectEl.value = "all";
  bufferSelectEl.closest = (selector) => (
    selector === ".history-buffer-controls" ? bufferControlsEl : null
  );

  const announcements = [];
  const store = createStore();
  const view = createHistoryView({
    store,
    historyEl,
    historyLogEl,
    historyContentEl,
    historyToggleEl,
    bufferSelectEl,
    bufferMuteEl,
    announceFeedback: (text) => announcements.push(text),
    initialMutedBuffers,
    localize,
    localizeBufferName: (name) => strings[`buffer-name-${name}`],
  });
  return {
    announcements,
    bufferMuteEl,
    bufferSelectEl,
    historyContentEl,
    historyEl,
    historyLogEl,
    historyToggleEl,
    store,
    view,
  };
}

test("history buffer names and muted preferences stay canonical", () => {
  assert.deepEqual(HISTORY_BUFFER_ORDER, ["all", "chat", "game", "system", "misc"]);
  assert.equal(normalizeHistoryBuffer("chats"), "chat");
  assert.equal(normalizeHistoryBuffer("unknown"), "misc");
  assert.deepEqual(
    normalizeMutedHistoryBuffers(["system", "chats", "unknown", null, "all", "chat"]),
    ["all", "chat", "system"],
  );
  assert.deepEqual(normalizeMutedHistoryBuffers(null), []);
});

test("history storage remains bounded per source and combined buffer", () => {
  const store = createStore();
  for (let index = 0; index <= HISTORY_BUFFER_LIMIT; index += 1) {
    store.addHistory("game", `message ${index}`);
  }
  assert.equal(store.state.historyBuffers.game.length, HISTORY_BUFFER_LIMIT);
  assert.equal(store.state.historyBuffers.all.length, HISTORY_BUFFER_LIMIT);
  assert.equal(store.state.historyBuffers.game[0], "message 1");
});

test("history renderer follows pointer mode and compact layouts remain collapsible", () => {
  const desktop = createFixture();
  assert.equal(desktop.historyEl.hidden, false);
  assert.equal(desktop.historyLogEl.hidden, true);
  assert.equal(desktop.historyContentEl.hidden, false);
  assert.equal(desktop.historyToggleEl.getAttribute("aria-expanded"), "true");

  const touch = createFixture([], { compact: true, touchLike: true });
  assert.equal(touch.historyContentEl.hidden, true);
  assert.equal(touch.historyEl.hidden, true);
  assert.equal(touch.historyLogEl.hidden, false);
  assert.equal(touch.historyToggleEl.getAttribute("aria-expanded"), "false");
  assert.equal(touch.historyToggleEl.tabIndex, 0);
  touch.historyToggleEl.dispatch("click");
  assert.equal(touch.historyContentEl.hidden, false);
  assert.equal(touch.historyEl.hidden, true);
  assert.equal(touch.historyLogEl.hidden, false);

  const narrowDesktop = createFixture([], { compact: true });
  assert.equal(narrowDesktop.historyContentEl.hidden, true);
  assert.equal(narrowDesktop.historyEl.hidden, false);
  assert.equal(narrowDesktop.historyLogEl.hidden, true);
  narrowDesktop.historyToggleEl.dispatch("click");
  assert.equal(narrowDesktop.historyContentEl.hidden, false);
  assert.equal(narrowDesktop.historyToggleEl.getAttribute("aria-expanded"), "true");
});

test("history updates and reopening a collapsed panel scroll to the latest message", () => {
  const desktop = createFixture();
  desktop.historyEl.scrollHeight = 480;
  desktop.historyLogEl.scrollHeight = 640;
  desktop.view.addEntry("latest game event", { buffer: "game" });
  assert.equal(desktop.historyEl.scrollTop, 480);
  assert.equal(desktop.historyLogEl.scrollTop, 640);

  const repeated = createFixture();
  repeated.historyEl.scrollHeight = 900;
  for (let index = 0; index < HISTORY_BUFFER_LIMIT; index += 1) {
    repeated.view.addEntry("repeated event", { buffer: "game", announce: false });
  }
  repeated.historyEl.scrollTop = 0;
  repeated.view.addEntry("repeated event", { buffer: "game", announce: false });
  assert.equal(repeated.historyEl.scrollTop, 900);

  const compact = createFixture([], { compact: true, touchLike: true });
  compact.historyLogEl.scrollHeight = 720;
  compact.view.addEntry("received while closed", { buffer: "system" });
  compact.historyLogEl.scrollTop = 0;
  compact.view.setCollapsed(false);
  assert.equal(compact.historyLogEl.scrollTop, 720);

  document.activeElement = compact.historyLogEl;
  compact.view.setCollapsed(true);
  assert.equal(document.activeElement, compact.historyToggleEl);
});

test("All mute marks every option and blocks child mute changes", () => {
  const fixture = createFixture(["all", "chats", "unknown"]);
  assert.deepEqual(fixture.view.getMutedBuffers(), ["all", "chat"]);
  assert.deepEqual(
    fixture.bufferSelectEl.options.map((option) => option.textContent),
    ["[Muted] All", "[Muted] Chat", "[Muted] Game", "[Muted] System", "[Muted] Misc"],
  );
  assert.equal(fixture.bufferMuteEl.textContent, "Unmute all buffer");
  assert.equal(fixture.bufferMuteEl.getAttribute("aria-pressed"), "true");

  fixture.bufferSelectEl.value = "system";
  fixture.bufferSelectEl.dispatch("change");
  assert.equal(fixture.store.state.historyBuffer, "system");
  assert.equal(
    fixture.bufferMuteEl.textContent,
    "The system buffer is muted by All. Select All to unmute it.",
  );
  assert.equal(fixture.view.toggleCurrentBufferMute(), false);
  assert.deepEqual(fixture.view.getMutedBuffers(), ["all", "chat"]);
  assert.equal(
    fixture.announcements.at(-1),
    "The system buffer is muted by All. Select All to unmute it.",
  );
});

test("unmuting All restores independent direct mute state", () => {
  const fixture = createFixture(["all", "chat"]);
  assert.equal(fixture.view.toggleCurrentBufferMute(), true);
  assert.deepEqual(fixture.view.getMutedBuffers(), ["chat"]);
  assert.deepEqual(
    fixture.bufferSelectEl.options.map((option) => option.textContent),
    ["All", "[Muted] Chat", "Game", "System", "Misc"],
  );
  assert.equal(fixture.bufferMuteEl.textContent, "Mute all buffer");
  assert.equal(fixture.bufferMuteEl.getAttribute("aria-pressed"), "false");
});

test("direct and global mutes retain the same history semantics as mobile", () => {
  const fixture = createFixture(["chat"]);
  assert.equal(fixture.view.addEntry("quiet chat", { buffer: "chat" }), false);
  assert.deepEqual(fixture.store.state.historyBuffers.chat, ["quiet chat"]);
  assert.deepEqual(fixture.store.state.historyBuffers.all, []);

  fixture.view.setMutedBuffers(["all"]);
  assert.equal(fixture.view.addEntry("quiet game", { buffer: "game" }), false);
  assert.deepEqual(fixture.store.state.historyBuffers.game, ["quiet game"]);
  assert.deepEqual(fixture.store.state.historyBuffers.all, ["quiet game"]);
  fixture.view.olderMessage();
  assert.equal(
    fixture.announcements.at(-1),
    "The all buffer is muted. Unmute it to show its history.",
  );
});

test("chat notification sounds remain behind effective buffer output gating", async () => {
  const appSource = await readFile(new URL("../app.js", import.meta.url), "utf8");
  const handlerStart = appSource.indexOf("  handleChatPacket(packet) {");
  const handlerEnd = appSource.indexOf("  isGameMenu(menuId) {", handlerStart);
  assert.ok(handlerStart >= 0 && handlerEnd > handlerStart, "handleChatPacket should remain independently testable");
  const handler = appSource.slice(handlerStart, handlerEnd);
  assert.match(handler, /const outputAllowed = this\.historyView\.addEntry/);
  assert.match(
    handler,
    /if \(shouldSpeak && outputAllowed\) \{[\s\S]*?this\.audio\.playSound/,
  );
});

test("the in-game tab order keeps collapsed History keyboard-reachable", async () => {
  const appSource = await readFile(new URL("../app.js", import.meta.url), "utf8");
  const handlerStart = appSource.indexOf("  installInGameTabTrap() {");
  const handlerEnd = appSource.indexOf("\n  focusHistory() {", handlerStart);
  assert.ok(handlerStart >= 0 && handlerEnd > handlerStart);
  const handler = appSource.slice(handlerStart, handlerEnd);
  assert.match(
    handler,
    /this\.elements\.menuList,[\s\S]*?this\.elements\.historyToggle,[\s\S]*?this\.elements\.historyBuffer,[\s\S]*?this\.elements\.historyBufferMute,[\s\S]*?historyTarget,[\s\S]*?this\.elements\.chatInput/,
  );
});

test("Web buffer terminology matches the mobile English and Vietnamese catalogs", async () => {
  const [webEnglish, webVietnamese, mobileEnglish, mobileVietnamese] = await Promise.all([
    import("../locales/en.js").then((module) => module.default),
    import("../locales/vi.js").then((module) => module.default),
    readFile(new URL("../../mobile_client/locales/en/client.json", import.meta.url), "utf8").then(JSON.parse),
    readFile(new URL("../../mobile_client/locales/vi/client.json", import.meta.url), "utf8").then(JSON.parse),
  ]);
  const keys = [
    "history-buffer-muted-name",
    "history-buffer-mute",
    "history-buffer-unmute",
    "history-buffer-muted-by-all",
    "history-buffer-muted-empty",
    "main-status-muted-suffix",
  ];
  for (const key of keys) {
    assert.equal(webEnglish[key], mobileEnglish[key], `English ${key}`);
    assert.equal(webVietnamese[key], mobileVietnamese[key], `Vietnamese ${key}`);
  }
});
