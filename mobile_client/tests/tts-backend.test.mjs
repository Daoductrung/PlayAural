import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";
import ts from "typescript";

async function fixture(platform = "android") {
  const listeners = new Map(); const requests = []; const selectedEngines = []; let resets = 0, stops = 0;
  const native = {
    maxSpeechInputLength: platform === "android" ? 4000 : undefined,
    getEngines: async () => [{ identifier: "engine", label: "Engine", isDefault: true, isSystem: true }],
    getVoices: async () => [], isSpeaking: async () => false,
    setEngine: async (identifier) => { selectedEngines.push(identifier); },
    stop: async () => { stops++; }, reset: async () => { resets++; },
    speak: async (id, text, options) => { requests.push({ id, text, options }); },
    addListener: (event, listener) => {
      const entries = listeners.get(event) ?? new Set();
      listeners.set(event, entries); entries.add(listener);
      return { remove: () => entries.delete(listener) };
    },
  };
  const source = await readFile(new URL("../src/tts/expoSpeechBackend.ts", import.meta.url), "utf8");
  const module = { exports: {} };
  vm.runInNewContext(ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText, {
    module, exports: module.exports,
    require: (id) => {
      if (id === "expo") return { requireNativeModule: () => native };
      if (id === "react-native") return { Platform: { OS: platform } };
      throw new Error(`Unexpected dependency: ${id}`);
    },
  });
  const emit = (event, payload) => [...(listeners.get(`Exponent.${event}`) ?? [])].forEach((listener) => listener(payload));
  return {
    create: module.exports.createExpoSpeechBackend, native, requests, emit,
    listenerCount: () => [...listeners.values()].reduce((sum, entries) => sum + entries.size, 0),
    resets: () => resets, selectedEngines, stops: () => stops,
  };
}

test("recreated speech adapters cannot accept a retired adapter's utterance callbacks", async () => {
  const f = await fixture(); const first = f.create(); let done = 0;
  await first.speak("old", {}); const oldId = f.requests[0].id; await first.stop();
  const second = f.create(); await second.speak("current", { onDone: () => done++ });
  f.emit("speakingDone", { id: oldId }); assert.equal(done, 0);
  f.emit("speakingDone", { id: f.requests[1].id }); assert.equal(done, 1);
  assert.equal(f.listenerCount(), 0);
});

test("native rejection and cancellation release listeners and keep callbacks off the bridge", async () => {
  const f = await fixture(); const backend = f.create(); let starts = 0;
  await backend.speak("test", { language: "vi", onStart: () => starts++ });
  assert.equal(f.requests[0].options.language, "vi");
  assert.equal(f.requests[0].options.onStart, undefined);
  await backend.reset(); f.emit("speakingStarted", { id: f.requests[0].id });
  assert.equal(starts, 0); assert.equal(f.listenerCount(), 0); assert.equal(f.resets(), 1);
  f.native.speak = async () => { throw new Error("unavailable"); };
  await assert.rejects(backend.speak("failed", {}), /unavailable/);
  assert.equal(f.listenerCount(), 0);
});

test("Android exposes engine discovery and selection while iOS omits Android-only controls", async () => {
  const android = await fixture(); const androidBackend = android.create();
  assert.equal((await androidBackend.getEngines())[0].identifier, "engine");
  await androidBackend.selectEngine("engine");
  assert.deepEqual(android.selectedEngines, ["engine"]);

  const ios = await fixture("ios"); const iosBackend = ios.create();
  assert.equal(iosBackend.getEngines, undefined);
  assert.equal(iosBackend.selectEngine, undefined);
});

test("iOS uses its unbounded speech input and stop fallback without Android-only APIs", async () => {
  const f = await fixture("ios"); const backend = f.create();
  assert.equal(backend.maxSpeechInputLength, Number.MAX_SAFE_INTEGER);
  await backend.reset(); assert.equal(f.stops(), 1); assert.equal(f.resets(), 0);
});
