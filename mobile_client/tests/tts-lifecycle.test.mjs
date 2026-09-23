import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";
import ts from "typescript";

const flush = () => new Promise(setImmediate);
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};

async function load(name, globals = {}) {
  const source = await readFile(new URL(`../src/tts/${name}.ts`, import.meta.url), "utf8");
  const compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(compiled, { module, exports: module.exports, setTimeout, clearTimeout, ...globals });
  return module.exports;
}

async function fixture(policyOverrides = {}) {
  let now = 0, nextId = 0;
  const timers = new Map();
  const clock = {
    setTimeout: (callback, delay) => { const id = ++nextId; timers.set(id, { callback, at: now + delay }); return id; },
    clearTimeout: (id) => timers.delete(id),
  };
  const advance = async (ms) => {
    const until = now + ms;
    while (true) {
      const next = [...timers.entries()].filter(([, t]) => t.at <= until).sort((a, b) => a[1].at - b[1].at)[0];
      if (!next) break;
      now = next[1].at; timers.delete(next[0]); next[1].callback(); await flush();
    }
    now = until; await flush();
  };
  const calls = [], utterances = [];
  const backend = {
    maxSpeechInputLength: 4000,
    getVoices: async () => { calls.push("voices"); return [{ identifier: "installed" }]; },
    stop: async () => { calls.push("stop"); },
    reset: async () => { calls.push("reset"); },
    speak: async (text, options) => { calls.push(`speak:${text}`); utterances.push({ text, options }); },
    isSpeaking: async () => true,
  };
  const { NativeSpeechDriver } = await load("NativeSpeechDriver", clock);
  const driver = new NativeSpeechDriver(backend, {
    operationTimeoutMs: 100, startTimeoutMs: 100, completionPollMs: 10, recoveryAttempts: 1,
    ...policyOverrides,
  });
  return { driver, backend, calls, utterances, advance, timers };
}

test("startup waits for readiness and cancellation prevents delayed speech", async () => {
  const f = await fixture(); const ready = deferred();
  f.backend.getVoices = () => ready.promise;
  f.driver.speak("cancelled", {}); await flush();
  assert.equal(f.utterances.length, 0);
  f.driver.stop(); ready.resolve([]); await flush();
  assert.equal(f.utterances.length, 0);
  assert.equal(f.timers.size, 0);
});

test("interruptions await native stop; only the latest request starts", async () => {
  const f = await fixture(); const stopped = deferred();
  f.backend.stop = () => stopped.promise;
  f.driver.speak("old", {}); f.driver.speak("current", {}); await flush();
  assert.equal(f.utterances.length, 0);
  stopped.resolve(); await flush();
  assert.deepEqual(f.utterances.map((u) => u.text), ["current"]);
  f.driver.stop(); await flush();
});

test("failed initialization rebinds and speaks without restarting the app", async () => {
  const f = await fixture(); let attempts = 0;
  f.backend.getVoices = async () => { if (attempts++ === 0) throw new Error("bind failed"); return []; };
  f.driver.speak("recovered", {}); await flush();
  assert.equal(attempts, 2); assert.ok(f.calls.includes("reset"));
  assert.equal(f.utterances[0].text, "recovered");
  f.driver.stop(); await flush();
});

test("a transient initialization failure does not blacklist an untried preferred voice", async () => {
  const f = await fixture(); let voiceQueries = 0;
  f.backend.getVoices = async () => {
    if (voiceQueries++ === 0) throw new Error("temporary initialization failure");
    return [{ identifier: "installed" }];
  };
  f.backend.speak = async (text, options) => {
    f.utterances.push({ text, options });
    options.onDone();
  };

  f.driver.speak("recover", { voice: "installed" });
  for (let index = 0; index < 8; index++) await flush();
  assert.equal(f.utterances[0].options.voice, undefined);

  f.driver.speak("retry preferred voice", { voice: "installed" });
  for (let index = 0; index < 5; index++) await flush();
  assert.equal(f.utterances.at(-1).options.voice, "installed");
});

test("missing initialization and start callbacks have bounded recovery", async () => {
  const f = await fixture(); let attempts = 0, errors = 0;
  f.backend.isSpeaking = async () => false;
  f.backend.getVoices = () => ++attempts === 1 ? new Promise(() => {}) : Promise.resolve([]);
  f.driver.speak("silent", { onError: () => errors++ }); await flush();
  await f.advance(100); assert.equal(f.utterances.length, 1);
  await f.advance(100); assert.equal(errors, 1);
  assert.equal(f.timers.size, 0);
});

test("a missing start retries once and late callbacks cannot finish the replacement", async () => {
  const f = await fixture(); let done = 0;
  f.backend.isSpeaking = async () => false;
  f.driver.speak("retry", { onDone: () => done++ }); await flush();
  const stale = f.utterances[0].options;
  await f.advance(100);
  assert.equal(f.utterances.length, 2);
  stale.onDone(); await flush(); assert.equal(done, 0);
  f.utterances[1].options.onStart(); f.utterances[1].options.onDone(); await flush();
  assert.equal(done, 1); assert.equal(f.timers.size, 0);
});

test("long or slow speech is never cut off by a text-duration estimate", async () => {
  const f = await fixture(); let done = 0;
  f.driver.speak("slow speech", { rate: 0.1, onDone: () => done++ }); await flush();
  f.utterances[0].options.onStart(); await f.advance(2000);
  assert.equal(done, 0); assert.equal(f.utterances.length, 1);
  f.backend.isSpeaking = async () => false; await f.advance(10);
  assert.equal(done, 1); assert.equal(f.timers.size, 0);
});

test("a lost start callback does not restart speech that is already playing", async () => {
  const f = await fixture(); let done = 0;
  f.driver.speak("already playing", { onDone: () => done++ }); await flush();
  await f.advance(200);
  assert.equal(f.utterances.length, 1); assert.equal(done, 0);
  f.backend.isSpeaking = async () => false; await f.advance(10);
  assert.equal(done, 1); assert.equal(f.timers.size, 0);
});

test("stale completion and health-query results cannot affect a new utterance", async () => {
  const f = await fixture(); const status = deferred(); let oldDone = 0, newDone = 0;
  f.backend.isSpeaking = () => status.promise;
  f.driver.speak("old", { onDone: () => oldDone++ }); await flush();
  const old = f.utterances[0].options; old.onStart(); await f.advance(10);
  f.driver.speak("new", { onDone: () => newDone++ }); await flush();
  old.onStopped(); status.resolve(false); await flush();
  assert.equal(oldDone, 0); assert.equal(newDone, 0);
  f.utterances[1].options.onDone(); await flush(); assert.equal(newDone, 1);
});

test("engine changes invalidate voice discovery and unavailable voices fall back safely", async () => {
  const f = await fixture(); const oldVoices = deferred(); let requests = 0;
  f.backend.getVoices = () => ++requests === 1 ? oldVoices.promise : Promise.resolve([{ identifier: "new" }]);
  const previous = f.driver.getVoices(); await flush(); f.driver.reset();
  f.driver.speak("current", { voice: "installed" }); await flush();
  oldVoices.resolve([{ identifier: "installed" }]);
  assert.equal((await previous)[0].identifier, "new"); await flush();
  assert.equal(f.utterances[0].options.voice, undefined);
  assert.equal((await f.driver.getVoices())[0].identifier, "new");
  f.driver.stop(); await flush();
});

test("all concurrent voice readers follow an engine replacement", async () => {
  const f = await fixture(); const stale = deferred(); let requests = 0;
  f.backend.getVoices = () => ++requests === 1 ? stale.promise : Promise.resolve([{ identifier: "current" }]);
  const first = f.driver.getVoices(); await flush();
  const second = f.driver.getVoices(); await flush();
  f.driver.reset(); await flush();
  stale.resolve([{ identifier: "old" }]);
  assert.equal((await first)[0].identifier, "current");
  assert.equal((await second)[0].identifier, "current");
  assert.equal(requests, 2);
});

test("voice discovery waits for a reset queued after the request was made", async () => {
  const f = await fixture(); const reset = deferred();
  f.backend.reset = () => reset.promise;
  const voices = f.driver.getVoices(); f.driver.reset(); await flush();
  assert.equal(f.calls.includes("voices"), false);
  reset.resolve(); await voices;
  assert.equal(f.calls.includes("voices"), true);
});

test("a replacement discovery failure rejects all readers without an unbounded retry", async () => {
  const f = await fixture(); const stale = deferred(); let requests = 0;
  f.backend.getVoices = () => ++requests === 1 ? stale.promise : Promise.reject(new Error("unavailable"));
  const first = f.driver.getVoices().catch((error) => error); await flush();
  const second = f.driver.getVoices().catch((error) => error); await flush();
  f.driver.reset(); stale.resolve([{ identifier: "old" }]); await flush();
  assert.equal((await first).message, "unavailable");
  assert.equal((await second).message, "unavailable");
  assert.equal(requests, 2);
});

test("a timed-out voice-only query releases its native initialization request", async () => {
  const f = await fixture();
  f.backend.getVoices = () => new Promise(() => {});
  const result = f.driver.getVoices().catch((error) => error);
  await flush(); await f.advance(100);
  assert.match((await result).message, /timed out/);
  assert.ok(f.calls.includes("reset"));
  assert.equal(f.timers.size, 0);
});

test("rapid requests coalesce behind a stalled stop without losing a requested reset", async () => {
  const f = await fixture(); let stops = 0;
  f.backend.stop = () => { stops++; return new Promise(() => {}); };
  f.driver.speak("stale", {}); await flush();
  f.driver.reset();
  for (let i = 0; i < 20; i++) f.driver.speak(`focus ${i}`, {});
  await f.advance(100);
  assert.deepEqual(f.utterances.map((u) => u.text), ["focus 19"]);
  assert.equal(stops, 1);
  assert.ok(f.calls.includes("reset"));
  f.driver.stop(); await f.advance(100);
});

test("native rejection retries with default voice and propagates permanent failure once", async () => {
  const f = await fixture(); let errors = 0;
  f.backend.speak = async (text, options) => { f.utterances.push({ text, options }); throw new Error("engine failed"); };
  f.driver.speak("test", { voice: "installed", onError: () => errors++ }); await flush();
  assert.equal(f.utterances.length, 2); assert.equal(f.utterances[0].options.voice, "installed");
  assert.equal(f.utterances[1].options.voice, undefined); assert.equal(errors, 1);
  assert.equal(f.timers.size, 0);
});

test("a failed preferred voice is bypassed on later utterances without losing the preference", async () => {
  const f = await fixture();
  f.backend.speak = async (text, options) => {
    f.utterances.push({ text, options });
    if (options.voice) throw new Error("voice failed");
    options.onDone();
  };
  f.driver.speak("first", { voice: "installed" });
  await flush(); await flush(); await flush();
  assert.deepEqual(f.utterances.map((entry) => entry.options.voice), ["installed", undefined]);

  f.driver.speak("second", { voice: "installed" });
  await flush(); await flush();
  assert.equal(f.utterances.at(-1).text, "second");
  assert.equal(f.utterances.at(-1).options.voice, undefined);
});

test("an engine error after speech starts is reported without replaying audible text", async () => {
  const f = await fixture(); let errors = 0;
  f.driver.speak("do not repeat", { onError: () => errors++ }); await flush();
  f.utterances[0].options.onStart();
  f.utterances[0].options.onError(new Error("late engine failure"));
  await flush();
  assert.equal(f.utterances.length, 1);
  assert.equal(errors, 1);
});

test("a silent default engine falls back to an installed system engine and keeps using it", async () => {
  const f = await fixture(); let selected = "broken.default"; const selections = [];
  f.backend.getEngines = async () => [
    { identifier: "broken.default", isDefault: true, isSystem: false, label: "Broken" },
    { identifier: "working.system", isDefault: false, isSystem: true, label: "Working" },
  ];
  f.backend.selectEngine = async (identifier) => { selected = identifier; selections.push(identifier); };
  f.backend.reset = async () => { selected = "broken.default"; f.calls.push("reset"); };
  f.backend.speak = async (text, options) => {
    f.utterances.push({ engine: selected, text, options });
    if (selected === "broken.default") throw new Error("engine failed");
    options.onDone();
  };

  f.driver.speak("recover", {});
  for (let index = 0; index < 10; index++) await flush();
  assert.equal(f.utterances.at(-1).engine, "working.system");
  assert.deepEqual(selections, ["working.system"]);

  f.driver.speak("stay recovered", {});
  for (let index = 0; index < 5; index++) await flush();
  assert.equal(f.utterances.at(-1).engine, "working.system");
  assert.deepEqual(selections, ["working.system"]);
});

test("engine fallback is bounded and prioritizes installed system engines", async () => {
  const f = await fixture({ maxEngineFallbacks: 1 }); let selected = "broken.default", errors = 0;
  const selections = [];
  f.backend.getEngines = async () => [
    { identifier: "broken.default", isDefault: true, label: "Default" },
    { identifier: "third.party", label: "A third-party engine" },
    { identifier: "working.system", isSystem: true, label: "System engine" },
  ];
  f.backend.selectEngine = async (identifier) => { selected = identifier; selections.push(identifier); };
  f.backend.speak = async (text, options) => {
    f.utterances.push({ engine: selected, text, options });
    throw new Error("engine failed");
  };

  f.driver.speak("bounded recovery", { onError: () => errors++ });
  for (let index = 0; index < 12; index++) await flush();
  assert.deepEqual(selections, ["working.system"]);
  assert.equal(errors, 1);
});

test("invalid recovery budgets fall back to finite defaults", async () => {
  const f = await fixture({ maxEngineFallbacks: Infinity, recoveryAttempts: 0 });
  const selections = []; let errors = 0;
  f.backend.getEngines = async () => [
    { identifier: "broken.default", isDefault: true },
    ...Array.from({ length: 12 }, (_, index) => ({ identifier: `fallback.${index}` })),
  ];
  f.backend.selectEngine = async (identifier) => { selections.push(identifier); };
  f.backend.speak = async () => { throw new Error("engine failed"); };

  f.driver.speak("bounded invalid policy", { onError: () => errors++ });
  for (let index = 0; index < 20; index++) await flush();
  assert.equal(selections.length, 8);
  assert.equal(errors, 1);
});

test("engine discovery completing after reset cannot restore a stale fallback catalog", async () => {
  const f = await fixture(); const staleCatalog = deferred(); let catalogRequests = 0;
  let selected = "broken.default"; const selections = [];
  f.backend.getEngines = () => ++catalogRequests === 1
    ? staleCatalog.promise
    : Promise.resolve([
      { identifier: "broken.default", isDefault: true, label: "Default" },
      { identifier: "current.system", isSystem: true, label: "Current" },
    ]);
  f.backend.selectEngine = async (identifier) => { selected = identifier; selections.push(identifier); };
  f.backend.reset = async () => { selected = "broken.default"; f.calls.push("reset"); };
  f.backend.speak = async (text, options) => {
    f.utterances.push({ engine: selected, text, options });
    if (selected === "current.system") options.onDone();
    else throw new Error("engine failed");
  };

  f.driver.speak("stale request", {});
  await flush(); await flush();
  assert.equal(catalogRequests, 1);
  f.driver.reset();
  f.driver.speak("current request", {});
  for (let index = 0; index < 5; index++) await flush();
  assert.equal(catalogRequests, 2);
  staleCatalog.resolve([
    { identifier: "broken.default", isDefault: true, label: "Default" },
    { identifier: "stale.system", isSystem: true, label: "Stale" },
  ]);
  for (let index = 0; index < 12; index++) await flush();
  assert.deepEqual(selections, ["current.system"]);
  assert.equal(f.utterances.at(-1).text, "current request");
});

test("long input is delivered in native-sized chunks without breaking emoji or ordering", async () => {
  const f = await fixture(); f.backend.maxSpeechInputLength = 8; let done = 0;
  const text = "one 😀 two three four";
  f.driver.speak(text, { onDone: () => done++ }); await flush();
  for (let i = 0; done === 0 && i < 20; i++) { f.utterances[i].options.onDone(); await flush(); }
  assert.equal(f.utterances.map((u) => u.text).join(""), text);
  assert.ok(f.utterances.every((u) => u.text.length <= 8 && u.text.isWellFormed()));
  assert.equal(done, 1);
});

test("repeated handoffs discard earlier initialization and leave no stopped speech behind", async () => {
  const f = await fixture();
  const started = deferred();
  const speak = f.backend.speak;
  f.backend.speak = async (...args) => { await speak(...args); started.resolve(); };
  for (let i = 0; i < 20; i++) { f.driver.reset(); f.driver.speak(String(i), {}); }
  await started.promise;
  assert.deepEqual(f.utterances.map((u) => u.text), ["19"]);
  f.driver.stop(); await flush(); assert.equal(f.timers.size, 0);
});

test("screen-reader events win over initial queries; resume resyncs; disposal is terminal", async () => {
  const { observeSpeechEnvironment } = await load("observeSpeechEnvironment");
  const listeners = {}; const queries = []; const values = []; let refreshes = 0;
  const sub = (name) => (listener) => { listeners[name] = listener; return { remove: () => delete listeners[name] }; };
  const dispose = observeSpeechEnvironment({
    initialAppState: "active", readScreenReader: () => { const q = deferred(); queries.push(q); return q.promise; },
    onScreenReaderChange: sub("reader"), onAppStateChange: sub("state"), onFocus: sub("focus"), onBlur: sub("blur"),
  }, (value) => values.push(value), () => refreshes++);
  listeners.reader(true); listeners.reader(false); queries[0].resolve(true); await flush();
  assert.deepEqual(values, [true, false]); assert.equal(refreshes, 1);
  listeners.blur(); listeners.state("background"); listeners.state("active"); listeners.focus();
  assert.equal(refreshes, 2);
  queries[1].resolve(true); queries[2].resolve(false); await flush();
  assert.equal(values.at(-1), false);
  listeners.blur(); listeners.focus(); dispose(); queries[3].resolve(true); await flush();
  assert.equal(values.at(-1), false); assert.equal(Object.keys(listeners).length, 0);
});

test("screen-reader changes in settings defer speech restoration until app focus returns", async () => {
  const { observeSpeechEnvironment } = await load("observeSpeechEnvironment");
  let reader, state; let refreshes = 0;
  const dispose = observeSpeechEnvironment({
    initialAppState: "active", readScreenReader: async () => true,
    onScreenReaderChange: (listener) => { reader = listener; return { remove() {} }; },
    onAppStateChange: (listener) => { state = listener; return { remove() {} }; },
  }, () => {}, () => refreshes++);
  await flush(); state("background"); reader(false);
  assert.equal(refreshes, 0);
  state("active"); assert.equal(refreshes, 1); dispose();
});

test("failed accessibility reads preserve the last known screen-reader state", async () => {
  const { observeSpeechEnvironment } = await load("observeSpeechEnvironment");
  let event, resume; const values = [];
  const dispose = observeSpeechEnvironment({
    initialAppState: "active", readScreenReader: async () => { throw new Error("unavailable"); },
    onScreenReaderChange: (listener) => { event = listener; return { remove() {} }; },
    onAppStateChange: (listener) => { resume = listener; return { remove() {} }; },
  }, (enabled) => values.push(enabled), () => {});
  event(true); resume("active"); await flush();
  assert.deepEqual(values, [true]); dispose();
});
