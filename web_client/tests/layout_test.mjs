import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { installKeybinds } from "../keybinds.js";
import { createCollapsiblePanel, installCollapsiblePanels } from "../ui/collapsiblePanels.js";
import { isMenuItemActionable, normalizeServerMenuItems } from "../ui/menus.js";

class FakeElement {
  constructor({ expanded = "true", hidden = false } = {}) {
    this.attributes = new Map([["aria-expanded", expanded]]);
    this.children = [];
    this.hidden = hidden;
    this.listeners = new Map();
  }

  addEventListener(type, listener) {
    this.listeners.set(type, listener);
  }

  contains(element) {
    return element === this || this.children.some((child) => child === element || child.contains?.(element));
  }

  dispatch(type) {
    this.listeners.get(type)?.({ currentTarget: this, type });
  }

  focus() {
    document.activeElement = this;
  }

  getAttribute(name) {
    return this.attributes.get(name) ?? null;
  }

  setAttribute(name, value) {
    this.attributes.set(name, String(value));
  }
}

test("read-only and legacy text menu rows are never actionable", () => {
  assert.equal(isMenuItemActionable({ id: "confirm", text: "Confirm" }), true);
  assert.equal(isMenuItemActionable({ id: "summary", read_only: true, text: "Summary" }), false);
  assert.equal(isMenuItemActionable({ text: "Legacy information" }), false);
  assert.equal(isMenuItemActionable("Legacy information"), false);
});

test("server menu normalization preserves read-only and copy directive semantics", () => {
  const directive = {
    version: 1,
    text: "first\nsecond",
    success_text: "Copied.",
    failure_text: "Failed.",
  };
  const items = normalizeServerMenuItems([
    { id: "summary", read_only: true, text: "Summary" },
    { id: "copy_page", text: "Copy", copy_directive: directive },
    { id: "invalid_copy", text: "Invalid copy", copy_directive: null },
    "Legacy information",
    null,
  ]);

  assert.equal(isMenuItemActionable(items[0]), false);
  assert.equal(isMenuItemActionable(items[1]), true);
  assert.equal(items[1].copyDirectivePresent, true);
  assert.deepEqual(items[1].copyDirective, directive);
  assert.equal(items[2].copyDirectivePresent, true);
  assert.equal(items[2].copyDirective, null);
  assert.equal(isMenuItemActionable(items[2]), true);
  assert.equal(isMenuItemActionable(items[3]), false);
  assert.equal(isMenuItemActionable(items[4]), false);
});

test("collapsible panels honor markup defaults and keep state synchronized", () => {
  globalThis.document = { activeElement: null };
  const toggle = new FakeElement({ expanded: "false" });
  const content = new FakeElement();
  const panel = createCollapsiblePanel({ toggleEl: toggle, contentEl: content });

  assert.equal(panel.isCollapsed(), true);
  assert.equal(content.hidden, true);
  assert.equal(toggle.getAttribute("aria-expanded"), "false");

  toggle.dispatch("click");
  assert.equal(panel.isCollapsed(), false);
  assert.equal(content.hidden, false);
  assert.equal(toggle.getAttribute("aria-expanded"), "true");
});

test("collapsing a panel moves focus out of content before hiding it", () => {
  const toggle = new FakeElement();
  const content = new FakeElement();
  const child = new FakeElement();
  content.children.push(child);
  globalThis.document = { activeElement: child };

  const panel = createCollapsiblePanel({ toggleEl: toggle, contentEl: content });
  panel.setCollapsed(true);

  assert.equal(document.activeElement, toggle);
  assert.equal(content.hidden, true);
  assert.equal(toggle.getAttribute("aria-expanded"), "false");
});

test("the installer creates one controller per complete panel", () => {
  globalThis.document = { activeElement: null };
  const completePanel = {
    dataset: { collapsiblePanel: "chat" },
    querySelector(selector) {
      return selector === ".collapsible-panel-toggle" ? new FakeElement() : new FakeElement();
    },
  };
  const incompletePanel = {
    dataset: { collapsiblePanel: "incomplete" },
    querySelector: () => null,
  };
  const root = { querySelectorAll: () => [completePanel, incompletePanel] };

  const panels = installCollapsiblePanels(root);
  assert.equal(panels.size, 1);
  assert.equal(panels.get("chat")?.isCollapsed(), false);
});

test("game panels expose disclosures without changing the established Tab loop", async () => {
  const [html, appSource] = await Promise.all([
    readFile(new URL("../index.html", import.meta.url), "utf8"),
    readFile(new URL("../app.js", import.meta.url), "utf8"),
  ]);

  for (const name of ["chat", "volume", "shortcuts"]) {
    assert.match(html, new RegExp(`id="${name}-toggle"[\\s\\S]*?aria-controls="${name}-content"`));
  }
  assert.match(html, /id="volume-toggle"[^>]*aria-expanded="false"/);
  assert.match(html, /id="volume-content"[^>]*hidden/);
  assert.match(html, /id="chat-toggle"[^>]*aria-expanded="true"/);
  assert.match(html, /id="shortcuts-toggle"[^>]*aria-expanded="true"/);

  const trapStart = appSource.indexOf("  installInGameTabTrap() {");
  const trapEnd = appSource.indexOf("\n  isVisibleFocusTarget", trapStart);
  const trap = appSource.slice(trapStart, trapEnd);
  assert.match(
    trap,
    /this\.elements\.menuList,[\s\S]*?this\.elements\.historyToggle,[\s\S]*?this\.elements\.historyBuffer,[\s\S]*?this\.elements\.historyBufferMute,[\s\S]*?historyTarget,[\s\S]*?this\.elements\.chatInput/,
  );
  assert.doesNotMatch(trap, /chatToggle|volumeToggle|shortcutsToggle/);
  assert.match(appSource, /this\.collapsiblePanels\.get\("chat"\)\?\.setCollapsed\(false\)/);
  assert.match(
    appSource,
    /!this\.app\.elements\.gameScreen\?\.hidden[\s\S]*?this\.app\.collapsiblePanels\.get\("chat"\)\?\.isCollapsed\(\)[\s\S]*?this\.app\.announceInterface\(text\)/,
  );
});

test("touch-rendered menu cells retain hardware-keyboard navigation", () => {
  const menuButton = { tagName: "BUTTON" };
  const menuElement = { contains: (element) => element === menuButton };
  let keydown = null;
  let selected = null;
  let prevented = false;
  globalThis.document = {
    activeElement: menuButton,
    addEventListener(type, listener) {
      if (type === "keydown") {
        keydown = listener;
      }
    },
  };
  installKeybinds({
    store: {
      state: {
        connection: { authenticated: true },
        currentMenu: {
          gridEnabled: true,
          gridWidth: 12,
          items: Array.from({ length: 144 }, (_, index) => ({ id: `cell_${index}` })),
          selection: 0,
        },
      },
    },
    menuView: {
      getElement: () => menuElement,
      setSelection: (index) => {
        selected = index;
      },
    },
  });

  keydown({
    key: "End",
    altKey: false,
    ctrlKey: false,
    shiftKey: false,
    metaKey: false,
    preventDefault: () => {
      prevented = true;
    },
  });

  assert.equal(selected, 11);
  assert.equal(prevented, true);
});

test("F1 requests focused menu help while Ctrl+F1 remains How to Play", () => {
  const menuButton = { tagName: "BUTTON" };
  const menuElement = { contains: (element) => element === menuButton };
  const descriptions = [];
  const keybinds = [];
  let keydown = null;
  globalThis.document = {
    activeElement: menuButton,
    addEventListener(type, listener) {
      if (type === "keydown") {
        keydown = listener;
      }
    },
  };
  installKeybinds({
    store: {
      state: {
        connection: { authenticated: true },
        currentMenu: {
          gridEnabled: false,
          gridWidth: 1,
          items: [{ id: "status_row", read_only: true, text: "Status" }],
          menuId: "turn_menu",
          selection: 0,
        },
      },
    },
    menuView: { getElement: () => menuElement },
    sendKeybind: (packet) => keybinds.push(packet),
    sendMenuDescription: (...args) => descriptions.push(args),
  });

  const pressF1 = (control = false) => keydown({
    key: "F1",
    altKey: false,
    ctrlKey: control,
    shiftKey: false,
    metaKey: false,
    preventDefault() {},
  });

  pressF1();
  assert.deepEqual(descriptions, [["turn_menu", "status_row"]]);
  assert.deepEqual(keybinds, []);

  pressF1(true);
  assert.equal(keybinds.length, 1);
  assert.equal(keybinds[0].key, "f1");
  assert.equal(keybinds[0].control, true);
  assert.equal(keybinds[0].menu_item_id, null);
});

test("message-history punctuation shortcuts keep their established dispatch", () => {
  const menuElement = { contains: () => false };
  const calls = [];
  let keydown = null;
  globalThis.document = {
    activeElement: menuElement,
    addEventListener(type, listener) {
      if (type === "keydown") {
        keydown = listener;
      }
    },
  };
  installKeybinds({
    store: {
      state: {
        connection: { authenticated: true },
        currentMenu: {
          gridEnabled: false,
          gridWidth: 1,
          items: [],
          selection: 0,
        },
      },
    },
    menuView: { getElement: () => menuElement },
    onOlderMessage: () => calls.push("older"),
    onNewerMessage: () => calls.push("newer"),
    onOldestMessage: () => calls.push("oldest"),
    onNewestMessage: () => calls.push("newest"),
  });

  for (const [key, shiftKey] of [[",", false], [".", false], ["<", true], [">", true]]) {
    keydown({
      key,
      altKey: false,
      ctrlKey: false,
      shiftKey,
      metaKey: false,
      preventDefault() {},
    });
  }

  assert.deepEqual(calls, ["older", "newer", "oldest", "newest"]);
});

test("large grids retain accessible cells and pan on both axes", async () => {
  const css = await readFile(new URL("../style.css", import.meta.url), "utf8");
  const gridStart = css.indexOf(".menu-list.grid-mode {");
  const gridEnd = css.indexOf("\n}", gridStart);
  const gridRule = css.slice(gridStart, gridEnd);

  assert.match(css, /--control-min:\s*44px/);
  assert.match(css, /--grid-cell-min:\s*72px/);
  assert.match(gridRule, /repeat\(var\(--grid-cols\), minmax\(var\(--grid-cell-min\), 1fr\)\)/);
  assert.match(gridRule, /touch-action:\s*pan-x pan-y/);
  assert.match(css, /\.menu-list \{[\s\S]*?overflow:\s*auto/);
  assert.match(css, /\.menu-list \{[\s\S]*?-webkit-overflow-scrolling:\s*touch/);
  assert.match(css, /\.menu-list \{[\s\S]*?max-height:\s*56vh;[\s\S]*?max-height:\s*56dvh/);
  assert.match(css, /\.game-grid > \* \{[\s\S]*?min-width:\s*0/);
  assert.match(css, /\.grid-mode \.menu-item \{[\s\S]*?overflow-wrap:\s*anywhere/);
});

test("every Web locale provides the disclosure headings without obsolete labels", async () => {
  for (const locale of ["en", "vi", "fa", "es", "pt"]) {
    const messages = await import(`../locales/${locale}.js`).then((module) => module.default);
    for (const key of ["chat-heading", "volume-heading", "shortcuts-heading"]) {
      assert.ok(messages[key], `${locale} is missing ${key}`);
    }
    assert.equal(messages["audio-controls-label"], undefined);
    assert.equal(messages["players-title"], undefined);
  }
});

test("locale metadata identifies Persian as right-to-left", async () => {
  const { LOCALE_METADATA } = await import("../locales/manifest.js");
  assert.equal(LOCALE_METADATA.fa.direction, "rtl");
  assert.equal(LOCALE_METADATA.en.direction || "ltr", "ltr");

  const appSource = await readFile(new URL("../app.js", import.meta.url), "utf8");
  assert.match(
    appSource,
    /document\.documentElement\.dir = LOCALE_METADATA\[bundle\.locale\]\?\.direction \|\| "ltr"/,
  );
});

test("locale bundle changes preserve packet order and authentication chrome", async () => {
  const source = await readFile(new URL("../app.js", import.meta.url), "utf8");
  const packetHandler = source.split("  handlePacket(packet) {", 2)[1].split(
    "\n  beginLocaleUpdate(locale)",
    1,
  )[0];
  assert.match(
    packetHandler,
    /this\.localeUpdateBarrier && packet\.type !== "update_locale"/u,
  );
  assert.match(packetHandler, /this\.localeUpdateGeneration === generation/u);
  assert.match(packetHandler, /this\.handlePacket\(packet\)/u);
  assert.match(packetHandler, /this\.beginLocaleUpdate\(packet\.locale\)/u);

  const updater = source.split("  beginLocaleUpdate(locale) {", 2)[1].split(
    "\n  handleLoginFailed(packet)",
    1,
  )[0];
  assert.match(updater, /const previous = this\.localeUpdateBarrier \|\| Promise\.resolve\(\)/u);
  assert.match(updater, /Localization\.load\(locale/u);
  assert.match(updater, /shouldApply:/u);
  assert.match(updater, /this\.localeUpdateGeneration === generation/u);
  assert.match(updater, /this\.applyLocalization\(\)/u);

  const authorization = source.split("  handleAuthorizeSuccess(packet) {", 2)[1].split(
    "\n  retireLocalSession(",
    1,
  )[0];
  assert.match(
    authorization,
    /this\.beginLocaleUpdate\(packet\.locale\)\.then\(\(applied\)/u,
  );
  assert.match(authorization, /if \(applied\)/u);

  const cleanup = source.split("  cleanupRuntime(full = false) {", 2)[1].split(
    "\n  clearSessionHistory()",
    1,
  )[0];
  assert.match(cleanup, /this\.localeUpdateGeneration \+= 1/u);
  assert.match(cleanup, /this\.localeUpdateBarrier = null/u);
});

test("the offline shell precaches the updated UI modules", async () => {
  const serviceWorker = await readFile(new URL("../sw.js", import.meta.url), "utf8");
  assert.match(serviceWorker, /playaural-web-v1\.0\.5\.1-shell-18/u);
  for (const asset of [
    "store.js",
    "spatial_audio.js",
    "ui/history.js",
    "ui/collapsiblePanels.js",
    "vendor/stb-vorbis.js",
  ]) {
    assert.match(serviceWorker, new RegExp(`\\./${asset.replace("/", "\\/")}`));
  }
});

test("the checked-in Web vendors carry complete dependency notices", async () => {
  const [bundle, lockText, notices] = await Promise.all([
    readFile(new URL("../vendor/livekit-client.umd.js", import.meta.url), "utf8"),
    readFile(new URL("../package-lock.json", import.meta.url), "utf8"),
    readFile(new URL("../vendor/THIRD_PARTY_NOTICES.md", import.meta.url), "utf8"),
  ]);
  const lock = JSON.parse(lockText);
  assert.match(bundle, /2\.18\.2/);
  for (const path of Object.keys(lock.packages)) {
    if (!path.startsWith("node_modules/") || path.startsWith("node_modules/@types/")) {
      continue;
    }
    const packageName = path.slice("node_modules/".length);
    assert.ok(
      notices.includes(`| \`${packageName}\``),
      `missing bundled dependency notice for ${packageName}`,
    );
  }
  for (const file of [
    "Apache-2.0.txt",
    "buf-protobuf-BSD-3-Clause.txt",
    "events-MIT.txt",
    "jose-MIT.txt",
    "loglevel-MIT.txt",
    "sdp-MIT.txt",
    "sdp-transform-MIT.txt",
    "tslib-0BSD.txt",
    "typed-emitter-MIT.txt",
    "webrtc-adapter-BSD-3-Clause.txt",
    "stb_vorbis-MIT-or-Public-Domain.txt",
  ]) {
    assert.ok(
      (await readFile(new URL(`../vendor/licenses/${file}`, import.meta.url), "utf8")).trim(),
      `${file} must contain its license text`,
    );
  }
  assert.ok(
    (await readFile(new URL("../vendor/LIVEKIT_NOTICE", import.meta.url), "utf8")).trim(),
  );
});
