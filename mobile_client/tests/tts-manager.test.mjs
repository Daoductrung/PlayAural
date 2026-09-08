import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";
import ts from "typescript";

async function fixture() {
  const calls = [], utterances = [];
  class Driver {
    stop() { calls.push("stop"); }
    reset() { calls.push("reset"); }
    getVoices() { return Promise.resolve([]); }
    speak(text, options) { utterances.push({ text, options }); }
  }
  const source = await readFile(new URL("../src/tts/TtsManager.ts", import.meta.url), "utf8");
  const module = { exports: {} };
  const compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  vm.runInNewContext(compiled, {
    module, exports: module.exports, setTimeout, clearTimeout,
    require: (id) => {
      if (id.endsWith("/debug")) return { ENABLE_CLIENT_DEBUG_LOGS: false };
      if (id.endsWith("/NativeSpeechDriver")) return { NativeSpeechDriver: Driver };
      if (id.endsWith("/expoSpeechBackend")) return { createExpoSpeechBackend: () => ({}) };
      throw new Error(`Unexpected dependency: ${id}`);
    },
  });
  const manager = new module.exports.TtsManager();
  const finish = () => utterances.at(-1).options.onDone();
  return { manager, calls, utterances, finish };
}

test("announcements keep their order ahead of passive focus speech", async () => {
  const f = await fixture();
  f.manager.speakUi("focus");
  f.manager.speakAnnouncement("first"); f.manager.speakAnnouncement("second");
  f.manager.speakUi("new focus", { interruptAnnouncement: false, interruptUi: false });
  f.finish(); f.finish(); f.finish();
  assert.deepEqual(f.utterances.map((u) => u.text), ["focus", "first", "second", "new focus"]);
});

test("native screen-reader mode suppresses only self-voiced UI and preserves game announcements", async () => {
  const f = await fixture();
  f.manager.speakUi("old focus"); f.manager.speakAnnouncement("game event");
  const old = f.utterances[0].options;
  f.manager.setUiEnabled(false); f.manager.speakUi("hidden focus");
  old.onDone();
  assert.deepEqual(f.utterances.map((u) => u.text), ["old focus", "game event"]);
  f.manager.stopAnnouncements(); f.finish();
  assert.equal(f.utterances.length, 2);
});

test("a handoff restores the current announcement and preserves queued events", async () => {
  const f = await fixture();
  f.manager.setCurrentUiTextProvider(() => "current focus");
  f.manager.speakAnnouncement("active"); f.manager.speakAnnouncement("queued");
  const stale = f.utterances[0].options;
  f.manager.refreshNativeSpeech(); stale.onDone();
  assert.deepEqual(f.utterances.map((u) => u.text), ["active", "active"]);
  f.finish(); f.finish();
  assert.deepEqual(f.utterances.map((u) => u.text), ["active", "active", "queued"]);
  assert.ok(f.calls.includes("reset"));
});

test("equal settings and non-finite rates never interrupt current speech", async () => {
  const f = await fixture();
  f.manager.speakUi("focus");
  f.manager.setRate(2); f.manager.setRate(NaN); f.manager.setRate(Infinity);
  f.manager.setLanguage("en"); f.manager.setVoice(undefined);
  assert.equal(f.utterances.length, 1);
  f.manager.setRate(1); assert.equal(f.utterances.length, 2);
});

test("voice preferences are retained for validation against each new native engine", async () => {
  const f = await fixture();
  await f.manager.setMobileVoice("temporarily unavailable");
  f.manager.speakUi("focus");
  assert.equal(f.utterances[0].options.voice, "temporarily unavailable");
  f.manager.refreshNativeSpeech();
  assert.equal(f.utterances[1].options.voice, "temporarily unavailable");
});

test("enabling self-voicing restores current focus; stopping suppresses all stale callbacks", async () => {
  const f = await fixture();
  f.manager.setUiEnabled(false); f.manager.setCurrentUiTextProvider(() => "current focus");
  f.manager.refreshNativeSpeech(); assert.equal(f.utterances.length, 0);
  f.manager.setUiEnabled(true); assert.equal(f.utterances[0].text, "current focus");
  f.manager.speakAnnouncement("queued"); f.manager.stop(); f.finish();
  assert.equal(f.utterances.length, 1);
});
