import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";
import ts from "typescript";

const appSource = await readFile(
  new URL("../src/app/PlayAuralApp.tsx", import.meta.url),
  "utf8",
);
const queueSource = await readFile(
  new URL("../src/accessibility/PoliteAnnouncementQueue.ts", import.meta.url),
  "utf8",
);

function queueFixture(capacity = 3) {
  const module = { exports: {} };
  vm.runInNewContext(ts.transpileModule(queueSource, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText, { module, exports: module.exports });
  const frames = new Map(); const output = []; let nextHandle = 0;
  const scheduler = {
    cancel: (handle) => frames.delete(handle),
    request: (callback) => { const handle = ++nextHandle; frames.set(handle, callback); return handle; },
  };
  const queue = new module.exports.PoliteAnnouncementQueue((text) => output.push(text), capacity, scheduler);
  const runFrame = () => {
    const entry = frames.entries().next().value;
    assert.ok(entry, "expected a queued animation frame");
    frames.delete(entry[0]); entry[1]();
  };
  return { frames, output, queue, runFrame };
}

test("server announcements use the screen reader whenever self-voicing is off", () => {
  assert.match(
    appSource,
    /if \(!selfVoicingEnabledRef\.current\) \{\s*if \(nativeScreenReaderModeRef\.current\) \{\s*postNativeScreenReaderAnnouncement\(text, \{ queue: true \}\);\s*\}\s*return;/,
  );
  assert.match(
    appSource,
    /tts\.stop\(\);\s*tts\.setUiEnabled\(false\);\s*if \(nativeReaderEnabled\)/,
  );
  assert.match(
    appSource,
    /if \(!nativeScreenReaderMode\) \{\s*screenReaderAnnouncementQueue\.clear\(\);/,
  );
});

test("Android and Web announcements use alternating polite live regions", () => {
  assert.match(appSource, /Platform\.OS !== "ios" \? \[0, 1\]\.map/);
  assert.match(
    appSource,
    /accessibilityLiveRegion=\{Platform\.OS === "android" \? "polite" : undefined\}/,
  );
  assert.match(appSource, /screenReaderAnnouncement\.id % 2 === slot/);
  assert.match(appSource, /new PoliteAnnouncementQueue/);
  assert.match(queueSource, /this\.pending\.length > this\.capacity/);
  assert.doesNotMatch(appSource, /AccessibilityInfo\.announceForAccessibility\(/);
});

test("screen-reader interaction clears pending live-region content", () => {
  assert.match(
    appSource,
    /const announceForNativeScreenReader[\s\S]*if \(!nativeScreenReaderModeRef\.current\) \{\s*return;/,
  );
  assert.match(
    appSource,
    /const markNativeScreenReaderInteraction[\s\S]*tts\.stopAnnouncements\(\);\s*clearScreenReaderAnnouncements\(\);/,
  );
  assert.match(
    appSource,
    /announceForAccessibilityWithOptions\(text, \{\s*queue: options\.queue \?\? true,/,
  );
});

test("polite announcements publish once per frame in FIFO order, including duplicates", () => {
  const f = queueFixture();
  f.queue.enqueue("same"); f.queue.enqueue("second"); f.queue.enqueue("same");
  assert.equal(f.frames.size, 1);
  f.runFrame(); f.runFrame(); f.runFrame();
  assert.deepEqual(f.output, ["same", "second", "same"]);
  assert.equal(f.frames.size, 0);
});

test("interaction cancels pending announcements and bounded overflow keeps the newest", () => {
  const f = queueFixture(2);
  f.queue.enqueue("discarded first");
  f.queue.enqueue("kept second");
  f.queue.enqueue("kept third");
  f.runFrame();
  assert.deepEqual(f.output, ["kept second"]);

  f.queue.enqueue("stale");
  f.queue.enqueue("current", { interrupt: true });
  assert.deepEqual(f.output, ["kept second", ""]);
  assert.equal(f.frames.size, 1);
  f.runFrame();
  assert.deepEqual(f.output, ["kept second", "", "current"]);

  f.queue.dispose();
  f.queue.enqueue("ignored");
  assert.equal(f.frames.size, 0);
});

test("clearing an idle queue does not publish redundant blank updates", () => {
  const f = queueFixture();
  f.queue.clear();
  assert.deepEqual(f.output, []);

  f.queue.enqueue("published");
  f.runFrame();
  f.queue.clear();
  f.queue.clear();
  assert.deepEqual(f.output, ["published", ""]);
});
