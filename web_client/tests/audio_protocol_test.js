import { createAudioEngine } from "../audio.js";

const runButton = document.querySelector("#run");
const result = document.querySelector("#result");
const engine = createAudioEngine({ soundBaseUrl: "../sounds/" });

function command(overrides) {
  return {
    type: "audio",
    version: 1,
    command: "play",
    kind: "sfx",
    asset: "menuclick.ogg",
    ...overrides,
  };
}

async function waitFor(predicate, label, timeoutMs = 4000) {
  const deadline = performance.now() + timeoutMs;
  while (performance.now() < deadline) {
    if (predicate()) {
      return;
    }
    await new Promise((resolve) => window.setTimeout(resolve, 20));
  }
  throw new Error(`Timed out: ${label}`);
}

runButton.addEventListener("click", async () => {
  runButton.disabled = true;
  result.value = "Running";
  try {
    await engine.unlock();
    if (engine.handleAudioCommand(command({ asset: "../unsafe.ogg" }))) {
      throw new Error("Unsafe asset was accepted");
    }
    if (engine.handleAudioCommand(command({ ducking: ["music"] }))) {
      throw new Error("Malformed ducking configuration was accepted");
    }

    engine.handleAudioCommand(command({
      handle: "test:loop",
      loop: true,
      ducking: { music: 30 },
    }));
    await waitFor(
      () => engine.getDiagnostics().duckRequestCount === 1,
      "managed loop start",
    );
    engine.handleAudioCommand(command({
      command: "stop",
      handle: "test:loop",
      asset: undefined,
    }));
    await waitFor(
      () => engine.getDiagnostics().sourceCount === 0,
      "managed loop stop",
    );

    engine.handleAudioCommand(command({
      kind: "music",
      asset: "mainmus.ogg",
      handle: "test:music",
      layer: "main",
      loop: true,
      fade_in_ms: 20,
    }));
    await waitFor(() => engine.getDiagnostics().sourceCount === 1, "music start");
    engine.handleAudioCommand(command({
      command: "pause",
      kind: "music",
      asset: undefined,
      handle: "test:music",
      fade_out_ms: 20,
    }));
    await waitFor(() => engine.getDiagnostics().pausedCount === 1, "music pause");
    engine.handleAudioCommand(command({
      command: "resume",
      kind: "music",
      asset: undefined,
      handle: "test:music",
      fade_in_ms: 20,
    }));
    await waitFor(() => engine.getDiagnostics().pausedCount === 0, "music resume");

    engine.handleAudioCommand(command({
      kind: "ambience",
      asset: "game_milebymile/amloop.ogg",
      handle: "test:global-ambience",
      layer: "weather",
      loop: true,
      fade_in_ms: 20,
    }));
    engine.handleAudioCommand(command({
      kind: "ambience",
      asset: "game_bang/ambience_western_loop.ogg",
      handle: "test:private-ambience",
      scope: "player",
      context: "test-player",
      layer: "weather",
      loop: true,
      fade_in_ms: 20,
    }));
    await waitFor(
      () => engine.getDiagnostics().targetCount === 3,
      "independent ambience layers",
    );
    engine.handleAudioCommand(command({
      kind: "ambience",
      asset: "battle/crowds/ambiencefight.ogg",
      handle: "test:global-ambience-next",
      layer: "weather",
      loop: true,
      fade_in_ms: 20,
      fade_out_ms: 20,
    }));
    await waitFor(
      () => (
        engine.getDiagnostics().targetCount === 3
        && engine.getDiagnostics().sourceCount === 3
      ),
      "ambient crossfade cleanup",
    );
    engine.handleAudioCommand(command({
      command: "set_bus",
      asset: undefined,
      bus: "music",
      volume: 75,
    }));
    if (engine.getDiagnostics().buses.music !== 0.75) {
      throw new Error("Named bus gain did not update");
    }

    engine.handleAudioCommand(command({ command: "stop_all", asset: undefined }));
    await waitFor(() => engine.getDiagnostics().sourceCount === 0, "stop all");

    const originalMediaPlay = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function rejectMediaPlayback() {
      return Promise.reject(new DOMException("Synthetic media failure", "NotAllowedError"));
    };
    engine.handleAudioCommand(command({
      kind: "music",
      asset: "game_bang/music_gameplay.ogg",
      handle: "test:bang-music-fallback",
      layer: "fallback-test",
      loop: true,
      fade_in_ms: 0,
      fade_out_ms: 0,
    }));
    HTMLMediaElement.prototype.play = originalMediaPlay;
    await waitFor(
      () => engine.getDiagnostics().bufferedMusicCount === 1,
      "delayed music Web Audio fallback",
      12000,
    );
    engine.handleAudioCommand(command({
      command: "stop",
      kind: "music",
      asset: undefined,
      handle: "test:bang-music-fallback",
      fade_out_ms: 0,
    }));
    await waitFor(
      () => engine.getDiagnostics().sourceCount === 0,
      "buffered music fallback cleanup",
    );

    HTMLMediaElement.prototype.play = function rejectPausedMediaPlayback() {
      return Promise.reject(new DOMException("Synthetic media failure", "NotAllowedError"));
    };
    engine.handleAudioCommand(command({
      kind: "music",
      asset: "game_bang/music_gameplay.ogg",
      handle: "test:pending-pause",
      layer: "pending-pause-test",
      loop: true,
      fade_in_ms: 0,
      fade_out_ms: 0,
    }));
    engine.handleAudioCommand(command({
      command: "pause",
      kind: "music",
      asset: undefined,
      handle: "test:pending-pause",
      fade_out_ms: 0,
    }));
    HTMLMediaElement.prototype.play = originalMediaPlay;
    await waitFor(
      () => (
        engine.getDiagnostics().pendingCount === 1
        && engine.getDiagnostics().sourceCount === 0
      ),
      "paused pending music remains dormant",
    );
    HTMLMediaElement.prototype.play = function rejectResumedMediaPlayback() {
      return Promise.reject(new DOMException("Synthetic media failure", "NotAllowedError"));
    };
    engine.handleAudioCommand(command({
      command: "resume",
      kind: "music",
      asset: undefined,
      handle: "test:pending-pause",
      fade_in_ms: 0,
    }));
    HTMLMediaElement.prototype.play = originalMediaPlay;
    await waitFor(
      () => engine.getDiagnostics().bufferedMusicCount === 1,
      "pending music resumes through Web Audio fallback",
      12000,
    );
    engine.handleAudioCommand(command({
      command: "stop",
      kind: "music",
      asset: undefined,
      handle: "test:pending-pause",
      fade_out_ms: 0,
    }));
    await waitFor(
      () => engine.getDiagnostics().sourceCount === 0,
      "resumed pending music cleanup",
    );

    engine.handleAudioCommand(command({
      kind: "ambience",
      asset: "menuclick.ogg",
      intro: "click.ogg",
      outro: "menuenter.ogg",
      handle: "test:stem",
      layer: "stem-test",
      loop: true,
      seamless: true,
      volume: 100,
      fade_in_ms: 0,
    }));
    await waitFor(
      () => engine.getDiagnostics().stemCount === 1,
      "segmented ambience preload",
    );
    await waitFor(
      () => engine.getDiagnostics().loopPhaseStemCount === 1,
      "gapless intro-to-loop transition",
    );
    engine.handleAudioCommand(command({
      command: "stop",
      kind: "ambience",
      asset: undefined,
      handle: "test:stem",
      play_outro: true,
      fade_out_ms: 1000,
    }));
    await waitFor(
      () => engine.getDiagnostics().scheduledOutroCount === 1,
      "gapless loop-to-outro scheduling",
    );
    if (engine.getDiagnostics().scheduledOutroMixLevels[0] !== 1) {
      throw new Error("Same-stem outro was faded");
    }
    if (engine.getDiagnostics().scheduledOutroDelays[0] > 0.1) {
      throw new Error("Immediate outro waited for a loop boundary");
    }
    if (engine.getDiagnostics().targetCount !== 1) {
      throw new Error("Outro was detached from lifecycle teardown routing");
    }
    await waitFor(
      () => engine.getDiagnostics().sourceCount === 0,
      "segmented ambience outro completion",
    );
    result.value = "PASS";
  } catch (error) {
    result.value = `FAIL: ${error instanceof Error ? error.message : String(error)}`;
  } finally {
    runButton.disabled = false;
  }
});
