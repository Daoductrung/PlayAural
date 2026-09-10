import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import ts from "typescript";

function load(path, require = () => ({})) {
  const source = readFileSync(new URL(path, import.meta.url), "utf8");
  const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
  const module = { exports: {} };
  new Function("module", "exports", "require", js)(module, module.exports, require);
  return module.exports;
}
const { BufferStore } = load("../src/state/BufferStore.ts");
const menuFocus = load("../src/app/menuFocus.ts");

test("message buffers cap each audience independently and share stable identities with All", () => {
  const store = new BufferStore(3);
  for (let index = 0; index < 8; index++) store.add(index % 2 ? "chat" : "game", `message ${index}`);
  assert.deepEqual(store.getMessages("all").map((item) => item.text), ["message 5", "message 6", "message 7"]);
  assert.deepEqual(store.getMessages("chat").map((item) => item.text), ["message 3", "message 5", "message 7"]);
  assert.equal(store.getMessages("chat").at(-1).id, store.getMessages("all").at(-1).id);
  store.getMessages("chat").pop();
  assert.equal(store.getMessages("chat").length, 3);
});

test("clearing a session drops every buffer without reusing stale message identities", () => {
  const store = new BufferStore(2);
  store.add("chat", "first"); store.add("all", "second");
  assert.equal(store.getMessages("all").length, 2);
  const oldIds = store.getMessages("all").map((item) => item.id);
  store.clear(); store.clear();
  for (const buffer of ["all", "chat", "game", "system", "misc"]) assert.deepEqual(store.getMessages(buffer), []);
  store.add("chat", "new session");
  assert.equal(oldIds.includes(store.getMessages("chat")[0].id), false);
  for (const capacity of [0, -1, NaN, Infinity, 1.5]) assert.throws(() => new BufferStore(capacity), RangeError);
});

test("message focus survives prepend, trimming, empty lists, and functional navigation before repaint", () => {
  let state;
  const { useAnchoredFocus } = load("../src/app/useAnchoredFocus.ts", (id) => id === "react" ? {
    useState: (initial) => {
      state ??= initial;
      return [state, (update) => { state = typeof update === "function" ? update(state) : update; }];
    }, useCallback: (fn) => fn,
  } : menuFocus);
  const a = { id: "a" }, b = { id: "b" }, c = { id: "c" };
  const original = [a, b];
  let [index, select] = useAnchoredFocus(original);
  const unchanged = state;
  select(0);
  assert.equal(state, unchanged, "Repeated native focus does not schedule a redundant repaint");
  select(1);
  [index, select] = useAnchoredFocus([c, a, b]);
  assert.equal(index, 2, "The same message remains selected as new messages arrive");
  select((current) => current - 1);
  [index] = useAnchoredFocus([c, a]);
  assert.equal(index, 1);
  [index] = useAnchoredFocus([c]);
  assert.equal(index, 0);
  [index] = useAnchoredFocus([]);
  assert.equal(index, 0);
});
