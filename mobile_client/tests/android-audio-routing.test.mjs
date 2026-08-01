import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  patchExpoAudioRouting,
  resolveExpoAudioModulePath,
} from "../scripts/patch-expo-audio-routing.mjs";

const upstreamSource = `class AudioModule {
  fun configure(mode: AudioMode) {
      updatePlaySoundThroughEarpiece(mode.shouldRouteThroughEarpiece ?: false)
  }
}`;

test("guards Android routing behind an explicitly supplied option", () => {
  const result = patchExpoAudioRouting(upstreamSource);

  assert.equal(result.changed, true);
  assert.match(
    result.source,
    /mode\.shouldRouteThroughEarpiece\?\.let \{ shouldRouteThroughEarpiece ->/,
  );
  assert.doesNotMatch(
    result.source,
    /shouldRouteThroughEarpiece \?: false/,
  );
});

test("is idempotent after the routing guard is installed", () => {
  const first = patchExpoAudioRouting(upstreamSource);
  const second = patchExpoAudioRouting(first.source);

  assert.equal(second.changed, false);
  assert.equal(second.source, first.source);
});

test("fails closed when an expo-audio upgrade changes the native implementation", () => {
  assert.throws(
    () => patchExpoAudioRouting("class AudioModule"),
    /Unsupported expo-audio AudioModule\.kt routing implementation/,
  );
});

test("the installed expo-audio source has the routing guard", async () => {
  const source = await readFile(resolveExpoAudioModulePath(), "utf8");
  const result = patchExpoAudioRouting(source);

  assert.equal(result.changed, false);
});

test("Android builds expo-audio from the guarded local source", async () => {
  const packageJson = JSON.parse(
    await readFile(new URL("../package.json", import.meta.url), "utf8"),
  );

  assert.ok(
    packageJson.expo?.autolinking?.android?.buildFromSource?.includes("expo-audio"),
  );
});
