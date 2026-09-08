import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import {
  patchExpoSpeechLifecycle, replacementPath, resolveExpoSpeechModulePath,
} from "../scripts/patch-expo-speech-lifecycle.mjs";

const upstream = (await readFile(new URL("./fixtures/expo-speech/SpeechModule.upstream.kt", import.meta.url), "utf8"))
  .replaceAll("\r\n", "\n");
const replacement = await readFile(replacementPath, "utf8");

test("speech patch accepts only reviewed upstream and is idempotent across line endings", () => {
  const result = patchExpoSpeechLifecycle(upstream, replacement);
  assert.equal(result.changed, true);
  assert.equal(result.source, replacement);
  assert.equal(patchExpoSpeechLifecycle(result.source, replacement).changed, false);
  assert.equal(patchExpoSpeechLifecycle(upstream.replaceAll("\n", "\r\n"), replacement).source, replacement);
});

test("speech patch fails closed on upstream changes or a damaged installed patch", () => {
  assert.throws(() => patchExpoSpeechLifecycle(upstream.replace("textToSpeech.shutdown()", "textToSpeech.stop()"), replacement), /Unsupported expo-speech/);
  assert.throws(() => patchExpoSpeechLifecycle(replacement.replace("generation += 1", "generation += 2"), replacement), /Unsupported expo-speech/);
});

test("installed speech module and build configuration enforce the reviewed lifecycle", async () => {
  assert.equal(patchExpoSpeechLifecycle(await readFile(resolveExpoSpeechModulePath(), "utf8"), replacement).changed, false);
  const pkg = JSON.parse(await readFile(new URL("../package.json", import.meta.url), "utf8"));
  assert.ok(pkg.expo.autolinking.android.buildFromSource.includes("expo-speech"));
  assert.match(pkg.scripts.postinstall, /patch:tts-lifecycle/);
});
