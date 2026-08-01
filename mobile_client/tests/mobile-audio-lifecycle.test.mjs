import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

import ts from "typescript";

async function loadPlaybackLifecycle() {
  const source = await readFile(
    new URL("../src/audio/playbackLifecycle.ts", import.meta.url),
    "utf8",
  );
  const compiled = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
    },
    fileName: "playbackLifecycle.ts",
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(compiled, { exports: module.exports, module });
  return module.exports;
}

test("completed one-shots are terminal", async () => {
  const { isTerminalNativePlaybackStatus } = await loadPlaybackLifecycle();

  assert.equal(isTerminalNativePlaybackStatus({
    didJustFinish: true,
    isLoaded: true,
    isLooping: false,
  }), true);
});

test("automatic loop boundaries never dispose the native source", async () => {
  const { isTerminalNativePlaybackStatus } = await loadPlaybackLifecycle();

  assert.equal(isTerminalNativePlaybackStatus({
    didJustFinish: true,
    isLoaded: true,
    isLooping: true,
  }), false);
});

test("progress and unloaded callbacks are not terminal", async () => {
  const { isTerminalNativePlaybackStatus } = await loadPlaybackLifecycle();

  assert.equal(isTerminalNativePlaybackStatus({
    didJustFinish: false,
    isLoaded: true,
    isLooping: false,
  }), false);
  assert.equal(isTerminalNativePlaybackStatus({
    didJustFinish: true,
    isLoaded: false,
  }), false);
});

test("the manager applies the terminal guard to its shared native source path", async () => {
  const source = await readFile(
    new URL("../src/audio/MobileAudioManager.ts", import.meta.url),
    "utf8",
  );

  assert.match(
    source,
    /player\.setOnPlaybackStatusUpdate\([\s\S]*?isTerminalNativePlaybackStatus\(status\)/,
  );
  assert.match(source, /isLooping:\s*looping/);
  assert.match(source, /Boolean\(packet\.loop\)/);
  assert.match(source, /packet\.loop\s*\?\?\s*true/);
});
