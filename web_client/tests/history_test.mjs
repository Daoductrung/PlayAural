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
  "buffer-private": "Private Messages",
  "buffer-game": "Game",
  "buffer-system": "System",
  "buffer-misc": "Misc",
  "buffer-name-all": "all",
  "buffer-name-chat": "Chat",
  "buffer-name-private": "private messages",
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
  assert.deepEqual(HISTORY_BUFFER_ORDER, ["all", "chat", "private", "game", "system", "misc"]);
  assert.equal(normalizeHistoryBuffer("chats"), "chat");
  assert.equal(normalizeHistoryBuffer("unknown"), "misc");
  assert.deepEqual(
    normalizeMutedHistoryBuffers(["system", "chats", "unknown", null, "all", "chat"]),
    ["all", "chat", "system"],
  );
  assert.deepEqual(normalizeMutedHistoryBuffers(null), []);
});

test("the Web selector renders Private Messages immediately after Chat", async () => {
  const html = await readFile(new URL("../index.html", import.meta.url), "utf8");
  const optionValues = [...html.matchAll(/<option[^>]+value="(all|chat|private|game|system|misc)"/g)]
    .map((match) => match[1]);
  assert.deepEqual(optionValues, HISTORY_BUFFER_ORDER);
});

test("history storage remains bounded per source and combined buffer", () => {
  const store = createStore();
  for (let index = 0; index <= HISTORY_BUFFER_LIMIT; index += 1) {
    store.addHistory("game", `message ${index}`);
  }
  assert.equal(store.state.historyBuffers.game.length, HISTORY_BUFFER_LIMIT);
  assert.equal(store.state.historyBuffers.all.length, HISTORY_BUFFER_LIMIT);
  assert.equal(store.state.historyBuffers.game[0].text, "message 1");
});

test("ending a Web session clears every history buffer without reusing identities", () => {
  const store = createStore();
  store.addHistory("private", "sensitive message");
  const previousId = store.state.historyBuffers.private[0].id;
  store.setHistoryBuffer("private");

  assert.equal(store.clearHistory(), true);
  assert.equal(store.state.historyBuffer, "all");
  for (const buffer of HISTORY_BUFFER_ORDER) {
    assert.deepEqual(store.state.historyBuffers[buffer], []);
  }
  assert.equal(store.clearHistory(), false);

  store.addHistory("private", "next session");
  assert.notEqual(store.state.historyBuffers.private[0].id, previousId);
});

test("ending a Web session resets message navigation for the next login", () => {
  const fixture = createFixture();
  for (const text of ["old one", "old two", "old three"]) {
    fixture.view.addEntry(text, { buffer: "game", announce: false });
  }
  fixture.view.oldestMessage();

  fixture.view.clearHistory();
  for (const text of ["new one", "new two", "new three"]) {
    fixture.view.addEntry(text, { buffer: "game", announce: false });
  }
  fixture.view.olderMessage();

  assert.equal(fixture.announcements.at(-1), "new two");
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

test("message navigation announces history text instead of entry objects", () => {
  const fixture = createFixture();
  fixture.view.addEntry("oldest message", { buffer: "game", announce: false });
  fixture.view.addEntry("middle message", { buffer: "game", announce: false });
  fixture.view.addEntry("newest message", { buffer: "game", announce: false });

  fixture.view.olderMessage();
  assert.equal(fixture.announcements.at(-1), "middle message");
  fixture.view.newerMessage();
  assert.equal(fixture.announcements.at(-1), "newest message");
  fixture.view.oldestMessage();
  assert.equal(fixture.announcements.at(-1), "oldest message");
  fixture.view.newestMessage();
  assert.equal(fixture.announcements.at(-1), "newest message");
  assert.equal(fixture.announcements.includes("[object Object]"), false);
});

test("history rendering tolerates legacy string entries during a PWA update", () => {
  const fixture = createFixture();
  fixture.store.state.historyBuffers.all.push("legacy cached message");
  fixture.store.state.historyRevisions.all += 1;

  fixture.view.render();
  fixture.view.newestMessage();

  assert.equal(fixture.historyEl.value, "legacy cached message");
  assert.equal(
    fixture.historyLogEl.children[0].children[0].textContent,
    "legacy cached message",
  );
  assert.equal(fixture.announcements.at(-1), "legacy cached message");
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
    ["[Muted] All", "[Muted] Chat", "[Muted] Private Messages", "[Muted] Game", "[Muted] System", "[Muted] Misc"],
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
    ["All", "[Muted] Chat", "Private Messages", "Game", "System", "Misc"],
  );
  assert.equal(fixture.bufferMuteEl.textContent, "Mute all buffer");
  assert.equal(fixture.bufferMuteEl.getAttribute("aria-pressed"), "false");
});

test("direct and global mutes retain the same history semantics as mobile", () => {
  const fixture = createFixture(["chat"]);
  assert.equal(fixture.view.addEntry("quiet chat", { buffer: "chat" }), false);
  assert.deepEqual(fixture.store.state.historyBuffers.chat.map((item) => item.text), ["quiet chat"]);
  assert.deepEqual(fixture.store.state.historyBuffers.all, []);

  fixture.view.setMutedBuffers(["private"]);
  assert.equal(fixture.view.addEntry("quiet private message", { buffer: "private" }), false);
  assert.deepEqual(
    fixture.store.state.historyBuffers.private.map((item) => item.text),
    ["quiet private message"],
  );
  assert.deepEqual(
    fixture.store.state.historyBuffers.all.map((item) => item.text),
    ["quiet chat"],
  );

  fixture.view.setMutedBuffers(["all"]);
  assert.equal(fixture.view.addEntry("quiet game", { buffer: "game" }), false);
  assert.deepEqual(fixture.store.state.historyBuffers.game.map((item) => item.text), ["quiet game"]);
  assert.deepEqual(
    fixture.store.state.historyBuffers.all.map((item) => item.text),
    ["quiet chat", "quiet private message", "quiet game"],
  );
  fixture.view.olderMessage();
  assert.equal(
    fixture.announcements.at(-1),
    "The all buffer is muted. Unmute it to show its history.",
  );
});

test("unmuting merges retained messages into All by identity, arrival order, and capacity", () => {
  const fixture = createFixture(["private"]);
  fixture.view.addEntry("one", { buffer: "game", announce: false });
  fixture.view.addEntry("same text", { buffer: "private", announce: false });
  fixture.view.addEntry("same text", { buffer: "system", announce: false });

  fixture.view.setMutedBuffers([]);
  assert.deepEqual(
    fixture.store.state.historyBuffers.all.map((item) => item.text),
    ["one", "same text", "same text"],
  );
  assert.equal(
    fixture.store.state.historyBuffers.private[0],
    fixture.store.state.historyBuffers.all[1],
  );

  fixture.view.setMutedBuffers(["private"]);
  fixture.view.setMutedBuffers([]);
  assert.deepEqual(
    fixture.store.state.historyBuffers.all.map((item) => item.text),
    ["one", "same text", "same text"],
  );

  const cappedStore = createStore();
  cappedStore.addHistory("private", "hidden oldest", { includeAll: false });
  for (let index = 0; index < HISTORY_BUFFER_LIMIT; index += 1) {
    cappedStore.addHistory("game", `visible ${index}`);
  }
  cappedStore.mergeHistoryIntoAll(["private"]);
  assert.equal(cappedStore.state.historyBuffers.all.length, HISTORY_BUFFER_LIMIT);
  assert.equal(cappedStore.state.historyBuffers.all[0].text, "visible 0");
});

test("the Web mute control restores the selected source backlog to All", () => {
  const fixture = createFixture(["private"]);
  fixture.view.addEntry("quiet private message", { buffer: "private", announce: false });
  fixture.store.setHistoryBuffer("private");

  assert.equal(fixture.view.toggleCurrentBufferMute(), true);
  assert.deepEqual(fixture.view.getMutedBuffers(), []);
  assert.deepEqual(
    fixture.store.state.historyBuffers.all.map((item) => item.text),
    ["quiet private message"],
  );
});

test("unmuting All leaves sources with their own direct mute excluded", () => {
  const fixture = createFixture(["all", "private"]);
  fixture.view.addEntry("still private", { buffer: "private", announce: false });
  fixture.view.addEntry("combined while globally muted", { buffer: "game", announce: false });

  fixture.view.setMutedBuffers(["private"]);
  assert.deepEqual(
    fixture.store.state.historyBuffers.all.map((item) => item.text),
    ["combined while globally muted"],
  );
  fixture.view.setMutedBuffers([]);
  assert.deepEqual(
    fixture.store.state.historyBuffers.all.map((item) => item.text),
    ["still private", "combined while globally muted"],
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
  assert.match(handler, /historyBuffer = convo === "private" \? "private" : "chat"/);
  assert.match(handler, /soundName = "pm\.ogg"/);
});

test("buffer-scoped audio commands are suppressed by effective mute state", async () => {
  const appSource = await readFile(new URL("../app.js", import.meta.url), "utf8");
  assert.match(
    appSource,
    /case "audio":[\s\S]*?!this\.historyView\.isBufferMuted\(normalizeHistoryBuffer\(packet\.buffer\)\)[\s\S]*?this\.audio\.handleAudioCommand\(packet\)/,
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

test("Web buffer terminology matches the mobile English, Portuguese, and Vietnamese catalogs", async () => {
  const [webEnglish, webPortuguese, webVietnamese, mobileEnglish, mobilePortuguese, mobileVietnamese] = await Promise.all([
    import("../locales/en.js").then((module) => module.default),
    import("../locales/pt.js").then((module) => module.default),
    import("../locales/vi.js").then((module) => module.default),
    readFile(new URL("../../mobile_client/locales/en/client.json", import.meta.url), "utf8").then(JSON.parse),
    readFile(new URL("../../mobile_client/locales/pt/client.json", import.meta.url), "utf8").then(JSON.parse),
    readFile(new URL("../../mobile_client/locales/vi/client.json", import.meta.url), "utf8").then(JSON.parse),
  ]);
  const keys = [
    "buffer-all",
    "buffer-chat",
    "buffer-private",
    "buffer-game",
    "buffer-system",
    "buffer-misc",
    "buffer-name-all",
    "buffer-name-chat",
    "buffer-name-private",
    "buffer-name-game",
    "buffer-name-system",
    "buffer-name-misc",
    "buffer-status-muted",
    "buffer-status-unmuted",
    "main-buffer-status",
    "main-buffer-info",
    "history-buffer-muted-name",
    "history-buffer-mute",
    "history-buffer-unmute",
    "history-buffer-muted-by-all",
    "history-buffer-muted-empty",
    "main-status-muted-suffix",
  ];
  for (const key of keys) {
    assert.equal(webEnglish[key], mobileEnglish[key], `English ${key}`);
    assert.equal(webPortuguese[key], mobilePortuguese[key], `Portuguese ${key}`);
    assert.equal(webVietnamese[key], mobileVietnamese[key], `Vietnamese ${key}`);
  }
});
