import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  configureBrowserAudioSession,
  createAudioBufferFromChannels,
  createAudioEngine,
} from "../audio.js";

function gainNode() {
  return {
    gain: {
      value: 1,
      setValueAtTime(value) {
        this.value = value;
      },
    },
    connect() {},
  };
}

test("browser audio sessions distinguish playback from microphone capture", () => {
  const assigned = [];
  let type = "auto";
  const session = {
    get type() {
      return type;
    },
    set type(value) {
      assigned.push(value);
      type = value;
    },
  };

  assert.equal(configureBrowserAudioSession(session), true);
  assert.equal(type, "playback");
  assert.equal(configureBrowserAudioSession(session, true), true);
  assert.equal(type, "play-and-record");
  assert.deepEqual(assigned, ["playback", "play-and-record"]);
  assert.equal(configureBrowserAudioSession(null), false);
  assert.equal(configureBrowserAudioSession(Object.freeze({ type: "auto" })), false);
});

test("decoded Vorbis channels become a validated AudioBuffer", () => {
  const copied = [];
  const context = {
    createBuffer(channelCount, sampleCount, sampleRate) {
      assert.deepEqual([channelCount, sampleCount, sampleRate], [2, 3, 48000]);
      return {
        copyToChannel(channel, index) {
          copied.push([index, [...channel]]);
        },
      };
    },
  };
  const decoded = {
    sampleRate: 48000,
    channels: [
      new Float32Array([0, 0.25, -0.25]),
      new Float32Array([0, -0.5, 0.5]),
    ],
  };

  assert.ok(createAudioBufferFromChannels(context, decoded));
  assert.deepEqual(copied, [
    [0, [0, 0.25, -0.25]],
    [1, [0, -0.5, 0.5]],
  ]);
  assert.equal(createAudioBufferFromChannels(context, {
    sampleRate: 48000,
    channels: [new Float32Array(2), new Float32Array(3)],
  }), null);
  assert.equal(createAudioBufferFromChannels(context, {
    sampleRate: 0,
    channels: [new Float32Array(3)],
  }), null);
});

test("audio engine configures the session before constructing Web Audio", async () => {
  const previousWindow = globalThis.window;
  const previousDocument = globalThis.document;
  const events = [];
  let sessionType = "auto";
  let context;

  class FakeAudioContext extends EventTarget {
    static initialState = "running";

    constructor() {
      super();
      events.push("context");
      context = this;
      this.state = FakeAudioContext.initialState;
      this.currentTime = 1;
      this.destination = {};
      this.resumeCalls = 0;
      this.suspendCalls = 0;
    }

    createGain() {
      return gainNode();
    }

    async resume() {
      this.resumeCalls += 1;
      this.state = "running";
      this.dispatchEvent(new Event("statechange"));
    }

    async suspend() {
      this.suspendCalls += 1;
      this.state = "suspended";
      this.dispatchEvent(new Event("statechange"));
    }
  }

  const audioSession = {
    get type() {
      return sessionType;
    },
    set type(value) {
      sessionType = value;
      events.push(`session:${value}`);
    },
  };
  globalThis.window = {
    AudioContext: FakeAudioContext,
    navigator: { audioSession },
  };
  globalThis.document = { visibilityState: "visible" };

  try {
    const engine = createAudioEngine();
    assert.deepEqual(events.slice(0, 2), ["session:playback", "context"]);

    engine.setMicrophoneActive(true);
    assert.equal(sessionType, "play-and-record");
    engine.setMicrophoneActive(false);
    assert.equal(sessionType, "playback");

    context.state = "interrupted";
    assert.equal(await engine.unlock(), true);
    assert.equal(context.resumeCalls, 1);

    context.currentTime = 5;
    assert.deepEqual(
      await Promise.all([
        engine.recoverAfterForeground(),
        engine.recoverAfterForeground(),
      ]),
      [true, true],
    );
    assert.equal(context.suspendCalls, 1);
    assert.equal(context.resumeCalls, 2);

    FakeAudioContext.initialState = "suspended";
    const lockedEngine = createAudioEngine();
    assert.equal(await lockedEngine.recoverAfterForeground(), false);
    assert.equal(context.resumeCalls, 0);
    assert.equal(await lockedEngine.unlock(), true);
    assert.equal(context.resumeCalls, 1);
  } finally {
    globalThis.window = previousWindow;
    globalThis.document = previousDocument;
  }
});

test("vendored fallback exactly matches and decodes with the pinned package", async () => {
  const vendoredPath = new URL("../vendor/stb-vorbis.js", import.meta.url);
  const packagePath = new URL("../node_modules/stb-vorbis/dist/index.js", import.meta.url);
  assert.equal(readFileSync(vendoredPath, "utf8"), readFileSync(packagePath, "utf8"));

  const { StbVorbis } = await import(vendoredPath.href);
  await StbVorbis.ready;
  const bytes = readFileSync(
    new URL("../sounds/buffer_category_navigation.ogg", import.meta.url),
  );
  const decoded = StbVorbis.decode(bytes);
  assert.ok(decoded.sampleRate > 0);
  assert.ok(decoded.channels.length > 0);
  assert.ok(decoded.channels[0].length > 0);
  assert.ok(decoded.channels.every(
    (channel) => channel instanceof Float32Array
      && channel.length === decoded.channels[0].length,
  ));
});

test("music and ambience fall back to buffered Vorbis playback", async () => {
  const previousWindow = globalThis.window;
  const previousDocument = globalThis.document;
  const previousAudio = globalThis.Audio;
  const previousFetch = globalThis.fetch;
  const sourceBytes = readFileSync(
    new URL("../sounds/buffer_category_navigation.ogg", import.meta.url),
  );
  const startedNodes = [];

  class RejectingAudio extends EventTarget {
    play() {
      return Promise.reject(new Error("Ogg media elements are unsupported"));
    }

    pause() {}
  }

  class FallbackAudioContext extends EventTarget {
    constructor() {
      super();
      this.state = "running";
      this.currentTime = 1;
      this.destination = {};
    }

    createGain() {
      return gainNode();
    }

    createMediaElementSource() {
      return { connect() {} };
    }

    createBuffer(channelCount, sampleCount, sampleRate) {
      const channels = Array.from(
        { length: channelCount },
        () => new Float32Array(sampleCount),
      );
      return {
        duration: sampleCount / sampleRate,
        length: sampleCount,
        numberOfChannels: channelCount,
        sampleRate,
        copyToChannel(channel, index) {
          channels[index].set(channel);
        },
      };
    }

    createBufferSource() {
      const node = new EventTarget();
      node.connect = () => {};
      node.disconnect = () => {};
      node.playbackRate = { value: 1 };
      node.start = () => { startedNodes.push(node); };
      node.stop = () => {};
      return node;
    }

    decodeAudioData() {
      return Promise.reject(new Error("Native Ogg decoding is unsupported"));
    }
  }

  globalThis.window = {
    AudioContext: FallbackAudioContext,
    location: { href: "https://example.test/" },
    navigator: {},
  };
  globalThis.document = { visibilityState: "visible" };
  globalThis.Audio = RejectingAudio;
  globalThis.fetch = async () => ({
    ok: true,
    arrayBuffer: async () => sourceBytes.buffer.slice(
      sourceBytes.byteOffset,
      sourceBytes.byteOffset + sourceBytes.byteLength,
    ),
  });

  try {
    const engine = createAudioEngine({ audioSession: null });
    const waitForStartedNodes = async (expected) => {
      const deadline = Date.now() + 2000;
      while (startedNodes.length < expected && Date.now() < deadline) {
        await new Promise((resolve) => setTimeout(resolve, 10));
      }
      assert.equal(startedNodes.length, expected);
    };
    assert.equal(engine.playMusic({
      asset: "buffer_category_navigation.ogg",
      fade_in_ms: 0,
      fade_out_ms: 0,
      handle: "test:music",
    }), "test:music");
    await waitForStartedNodes(1);
    assert.equal(engine.getDiagnostics().pendingCount, 0);

    engine.stopAll();
    assert.equal(engine.playAmbience({
      asset: "buffer_category_navigation.ogg",
      fade_in_ms: 0,
      fade_out_ms: 0,
      handle: "test:ambience",
      layer: "test",
    }), "test:ambience");
    await waitForStartedNodes(2);
    assert.equal(engine.getDiagnostics().pendingCount, 0);

    engine.stopAll();
    assert.equal(engine.playAmbience({
      asset: "buffer_category_navigation.ogg",
      fade_in_ms: 0,
      fade_out_ms: 0,
      handle: "test:stem",
      intro: "buffer_category_navigation.ogg",
      layer: "stem",
      outro: "buffer_category_navigation.ogg",
      seamless: false,
    }), "test:stem");
    await waitForStartedNodes(3);
    startedNodes[2].dispatchEvent(new Event("ended"));
    await waitForStartedNodes(4);
    engine.stopAll(0, { playOutros: true });
    await waitForStartedNodes(5);
    assert.equal(engine.getDiagnostics().pendingCount, 0);
  } finally {
    globalThis.window = previousWindow;
    globalThis.document = previousDocument;
    globalThis.Audio = previousAudio;
    globalThis.fetch = previousFetch;
  }
});
