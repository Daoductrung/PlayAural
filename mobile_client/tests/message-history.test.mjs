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
const { BUFFER_NAMES, BufferStore, normalizeBufferName } = load("../src/state/BufferStore.ts");
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
  for (const buffer of BUFFER_NAMES) assert.deepEqual(store.getMessages(buffer), []);
  store.add("chat", "new session");
  assert.equal(oldIds.includes(store.getMessages("chat")[0].id), false);
  for (const capacity of [0, -1, NaN, Infinity, 1.5]) assert.throws(() => new BufferStore(capacity), RangeError);
});

test("buffer names stay canonical and All remains the first filter", () => {
  assert.deepEqual(BUFFER_NAMES, ["all", "chat", "private", "game", "system", "misc"]);
  assert.equal(normalizeBufferName("chats"), "chat");
  assert.equal(normalizeBufferName("unknown"), "misc");
});

test("private messages keep an independent backlog and omit direct mutes from All", () => {
  const store = new BufferStore();
  store.setMutedBuffers(["private"]);
  store.add("private", "quiet private message");

  assert.deepEqual(
    store.getMessages("private").map((item) => item.text),
    ["quiet private message"],
  );
  assert.deepEqual(store.getMessages("all"), []);
});

test("unmuting restores retained source messages to All chronologically and without duplicates", () => {
  const store = new BufferStore(3);
  store.setMutedBuffers(["private"]);
  store.add("game", "one");
  store.add("private", "same text");
  store.add("system", "same text");
  store.add("game", "four");

  assert.deepEqual(
    store.getMessages("all").map((item) => item.text),
    ["one", "same text", "four"],
  );
  store.setMutedBuffers([]);
  assert.deepEqual(
    store.getMessages("all").map((item) => item.text),
    ["same text", "same text", "four"],
  );
  assert.equal(store.getMessages("private")[0], store.getMessages("all")[0]);

  store.setMutedBuffers(["private"]);
  store.setMutedBuffers([]);
  assert.deepEqual(
    store.getMessages("all").map((item) => item.text),
    ["same text", "same text", "four"],
  );
});

test("unmuting All does not restore a source that remains directly muted", () => {
  const store = new BufferStore();
  store.setMutedBuffers(["all", "private"]);
  store.add("private", "still private");
  store.add("game", "combined while globally muted");

  store.setMutedBuffers(["private"]);
  assert.deepEqual(
    store.getMessages("all").map((item) => item.text),
    ["combined while globally muted"],
  );
  store.setMutedBuffers([]);
  assert.deepEqual(
    store.getMessages("all").map((item) => item.text),
    ["still private", "combined while globally muted"],
  );
});

test("private chat packets and buffer-scoped audio use the private mute boundary", () => {
  const appSource = readFileSync(
    new URL("../src/app/PlayAuralApp.tsx", import.meta.url),
    "utf8",
  );
  assert.match(
    appSource,
    /packet\.convo === "private"[\s\S]*?\? "private"[\s\S]*?: "chat"/,
  );
  assert.match(appSource, /else if \(buffer === "private"\) \{[\s\S]*?chatSound = "pm\.ogg"/);
  assert.match(
    appSource,
    /!audioPacket\.buffer \|\| !buffers\.isMuted\(audioPacket\.buffer\)/,
  );
});

test("muting a buffer suppresses its visible history and speech eligibility without losing its own backlog", () => {
  const store = new BufferStore(5);
  assert.equal(store.setMutedBuffers(["chat"]), true);
  store.add("chats", "quiet chat");
  store.add("game", "audible game");

  assert.equal(store.isDirectlyMuted("chat"), true);
  assert.equal(store.isMuted("chat"), true);
  assert.deepEqual(store.getVisibleMessages("chat"), []);
  assert.deepEqual(store.getMessages("chat").map((item) => item.text), ["quiet chat"]);
  assert.deepEqual(store.getMessages("all").map((item) => item.text), ["audible game"]);

  assert.equal(store.setMutedBuffers([]), true);
  assert.deepEqual(store.getVisibleMessages("chat").map((item) => item.text), ["quiet chat"]);
  assert.deepEqual(
    store.getMessages("all").map((item) => item.text),
    ["quiet chat", "audible game"],
  );
});

test("All mute applies to every buffer and restored settings reject invalid names", () => {
  const store = new BufferStore();
  assert.equal(store.setMutedBuffers(["chats", "all", "bogus", "chat"]), true);
  assert.deepEqual(store.getMutedBuffers(), ["all", "chat"]);
  for (const buffer of BUFFER_NAMES) assert.equal(store.isMuted(buffer), true);
  assert.equal(store.setMutedBuffers(["all", "chat"]), false);
  assert.equal(store.setMutedBuffers(null), true);
  for (const buffer of BUFFER_NAMES) assert.equal(store.isMuted(buffer), false);
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
