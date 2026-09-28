import assert from "node:assert/strict";
import test from "node:test";

import {
  MenuFocusContextStore,
  resolveMenuFocusIndex,
} from "../ui/menuFocus.js";

test("server modal focus contexts are bounded, validated, and one-shot", () => {
  const contexts = new MenuFocusContextStore(2);
  const first = { menuId: "turn_menu", items: [{ id: "roll" }], focusIndex: 0 };
  const third = { menuId: "turn_menu", items: [{ id: "status" }], focusIndex: 0 };
  contexts.capture("first", first);
  contexts.capture("second", first);
  contexts.capture("third", third);
  contexts.capture(" padded ", first);
  contexts.capture("x".repeat(129), first);

  assert.equal(contexts.size, 2);
  assert.equal(contexts.consume("first"), null);
  assert.equal(contexts.consume("third"), third);
  assert.equal(contexts.consume("third"), null);
});

test("a restored modal context preserves identity but explicit focus still wins", () => {
  const previous = [{ id: "roll" }, { id: "status" }, { id: "leave" }];
  const next = [{ id: "roll" }, { id: "new" }, { id: "status" }, { id: "leave" }];
  assert.equal(resolveMenuFocusIndex(previous, next, 1, { sameMenu: true }), 2);
  assert.equal(
    resolveMenuFocusIndex(previous, next, 1, { sameMenu: true, explicitIndex: 3 }),
    3,
  );
});
