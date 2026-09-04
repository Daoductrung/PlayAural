import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import ts from "typescript";

const sourceUrl = new URL("../src/app/PlayAuralApp.tsx", import.meta.url);
const source = ts.createSourceFile(
  sourceUrl.pathname,
  await readFile(sourceUrl, "utf8"),
  ts.ScriptTarget.Latest,
  true,
  ts.ScriptKind.TSX,
);
let initializer;
function visit(node) {
  if (ts.isVariableDeclaration(node) && node.name.getText(source) === "activateShortcut") {
    initializer = node.initializer;
  }
  ts.forEachChild(node, visit);
}
visit(source);
assert.ok(initializer, "The app must expose its shortcut activation handler");
const printed = ts.createPrinter().printNode(ts.EmitHint.Expression, initializer, source);
const compiled = ts.transpileModule(`const activateShortcut = ${printed};`, {
  compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 },
}).outputText;

function harness(menuId = "turn_menu", connected = true) {
  const effects = [];
  const modeRef = { current: "shortcuts" };
  const activate = new Function(
    "connection", "modeRef", "setMode", "requestNativeMenuFocusOnNextPacket",
    "menuStateRef", "closeOverlay",
    `${compiled}\nreturn activateShortcut;`,
  )(
    connected ? { send: (packet) => effects.push(packet) } : null,
    modeRef,
    (mode) => effects.push({ mode }),
    () => effects.push("request-next-menu-focus"),
    { current: { menuId } },
    () => { modeRef.current = "main"; effects.push("close-overlay"); },
  );
  return { activate, effects, modeRef };
}

test("reading online users sends only a speech request and keeps Shortcuts focused", () => {
  const { activate, effects, modeRef } = harness();
  activate({ id: "list_online" });
  assert.deepEqual(effects, [{ type: "list_online" }]);
  assert.equal(modeRef.current, "shortcuts");
});

test("reading online users with no connection does not arm deferred focus", () => {
  const { activate, effects, modeRef } = harness("turn_menu", false);
  activate({ id: "list_online" });
  assert.deepEqual(effects, []);
  assert.equal(modeRef.current, "shortcuts");
});

test("opening a different online list requests menu focus and dismisses Shortcuts", () => {
  const { activate, effects, modeRef } = harness();
  activate({ id: "list_online_with_games" });
  assert.deepEqual(effects, [
    "request-next-menu-focus", { type: "list_online_with_games" }, { mode: "main" },
  ]);
  assert.equal(modeRef.current, "main");
});

test("returning to the existing online list does not leave a pending focus request", () => {
  const { activate, effects, modeRef } = harness("online_users");
  activate({ id: "list_online_with_games" });
  assert.deepEqual(effects, ["close-overlay"]);
  assert.equal(modeRef.current, "main");
});
