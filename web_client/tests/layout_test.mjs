import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { installKeybinds } from "../keybinds.js";
import { createCollapsiblePanel, installCollapsiblePanels } from "../ui/collapsiblePanels.js";

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

test("the offline shell precaches the disclosure module", async () => {
  const serviceWorker = await readFile(new URL("../sw.js", import.meta.url), "utf8");
  assert.match(serviceWorker, /\.\/ui\/collapsiblePanels\.js/);
});
