import assert from "node:assert/strict";
import test from "node:test";

import { copyTextToClipboard } from "../clipboard.js";

test("clipboard writes the exact page text through the modern API", async () => {
  const writes = [];
  const copied = await copyTextToClipboard("first\nsecond", {
    navigatorObject: { clipboard: { writeText: async (text) => writes.push(text) } },
    documentObject: null,
  });

  assert.equal(copied, true);
  assert.deepEqual(writes, ["first\nsecond"]);
});

test("clipboard reports denied modern writes without mutating the document", async () => {
  let created = false;
  const copied = await copyTextToClipboard("private page", {
    navigatorObject: { clipboard: { writeText: async () => { throw new Error("denied"); } } },
    documentObject: { createElement: () => { created = true; } },
  });

  assert.equal(copied, false);
  assert.equal(created, false);
});

test("clipboard uses a synchronous fallback when the modern API is absent", async () => {
  const state = {
    appended: false,
    removed: false,
    restored: false,
    selected: false,
    value: "",
  };
  const previousFocus = {
    focus: ({ preventScroll }) => { state.restored = preventScroll === true; },
  };
  const textarea = {
    style: {},
    setAttribute: () => {},
    focus: () => {},
    select: () => { state.selected = true; },
    remove: () => { state.removed = true; },
    set value(value) { state.value = value; },
  };
  const copied = await copyTextToClipboard("only this page", {
    navigatorObject: {},
    documentObject: {
      activeElement: previousFocus,
      body: { appendChild: () => { state.appended = true; } },
      createElement: () => textarea,
      execCommand: (command) => command === "copy",
    },
  });

  assert.equal(copied, true);
  assert.deepEqual(state, {
    appended: true,
    removed: true,
    restored: true,
    selected: true,
    value: "only this page",
  });
});

test("clipboard failures are contained and clean up temporary controls", async () => {
  let removed = false;
  let restored = false;
  const textarea = {
    style: {},
    setAttribute: () => {},
    focus: () => { throw new Error("focus denied"); },
    select: () => {},
    remove: () => { removed = true; },
    set value(_value) {},
  };

  assert.equal(await copyTextToClipboard("payload", {
    navigatorObject: {},
    documentObject: {
      activeElement: { focus: () => { restored = true; } },
      body: { appendChild: () => {} },
      createElement: () => textarea,
    },
  }), false);
  assert.equal(removed, true);
  assert.equal(restored, true);

  const throwingNavigator = {};
  Object.defineProperty(throwingNavigator, "clipboard", {
    get() { throw new Error("blocked"); },
  });
  assert.equal(await copyTextToClipboard("payload", {
    navigatorObject: throwingNavigator,
    documentObject: null,
  }), false);
});
