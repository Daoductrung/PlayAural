import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import ts from "typescript";

const sourceUrl = new URL(
  "../src/gestures/SelfVoicingGestureRecognizer.ts",
  import.meta.url,
);
const source = await readFile(sourceUrl, "utf8");
const hookSource = await readFile(
  new URL("../src/gestures/useSelfVoicingGestures.ts", import.meta.url),
  "utf8",
);
const appSource = await readFile(
  new URL("../src/app/PlayAuralApp.tsx", import.meta.url),
  "utf8",
);
const androidPluginSource = await readFile(
  new URL("../plugins/withPlayAuralBackgroundService.js", import.meta.url),
  "utf8",
);
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ES2022,
    target: ts.ScriptTarget.ES2022,
  },
  fileName: sourceUrl.pathname,
}).outputText;
const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`;
const {
  classifyGesturePath,
  SelfVoicingGestureRecognizer,
} = await import(moduleUrl);

test("loads device-specific Android gesture thresholds through the native package", () => {
  assert.match(androidPluginSource, /class GestureConfigurationModule/);
  assert.match(androidPluginSource, /ViewConfiguration\.get\(reactContext\)/);
  assert.match(androidPluginSource, /ViewConfiguration\.getLongPressTimeout\(\)/);
  assert.match(androidPluginSource, /TypedValue\.COMPLEX_UNIT_MM/);
  assert.match(androidPluginSource, /GestureConfigurationModule\(reactContext\)/);
  assert.match(androidPluginSource, /class GestureInputModule/);
  assert.match(androidPluginSource, /override fun dispatchTouchEvent\(event: MotionEvent\)/);
  assert.match(androidPluginSource, /event\.getHistoricalX\(pointerIndex, historyIndex\)/);
  assert.match(androidPluginSource, /reactContext\.emitDeviceEvent\(EVENT_NAME, payload\)/);
  assert.match(androidPluginSource, /GestureInputModule\(reactContext\)/);
  assert.match(hookSource, /NativeModules\.PlayAuralGestureConfiguration/);
  assert.match(hookSource, /NativeModules\.PlayAuralGestureInput/);
  assert.match(hookSource, /DeviceEventEmitter\.addListener\(nativeGestureEventName/);
  assert.match(hookSource, /nativeMultiTouchRecognizer/);
  assert.match(hookSource, /NATIVE_RECOGNIZER_CONFIG/);
  assert.match(hookSource, /gestureState\?\.numberActiveTouches/);
  assert.match(hookSource, /dispatchStraightSwipeAsSoonAsRecognized/);
  assert.match(hookSource, /onTouchStart/);
  assert.match(hookSource, /onTouchEnd/);
});

test("native multi-touch arbitration cannot dispatch a pending one-finger activation", () => {
  const responderRecognizer = new SelfVoicingGestureRecognizer();
  const nativeRecognizer = new SelfVoicingGestureRecognizer();

  assert.equal(
    performTap(responderRecognizer, 0, [point(1, 60, 60)])?.taps,
    1,
  );
  responderRecognizer.start(frame(180, [point(2, 60, 60)]));

  // The authoritative Android stream reaches two fingers, so the responder
  // candidate and its one-finger sequence are discarded before any lift can
  // be interpreted as the second half of a double tap.
  responderRecognizer.clear();
  nativeRecognizer.start(frame(180, [point(2, 60, 60)], [point(2, 60, 60)], 1));
  nativeRecognizer.start(
    frame(
      200,
      [point(2, 60, 60), point(3, 120, 60)],
      [point(3, 120, 60)],
      2,
    ),
  );

  assert.equal(
    responderRecognizer.end(frame(260, [], [point(2, 60, 60)], 0)),
    null,
  );
  assert.equal(
    nativeRecognizer.end(
      frame(240, [point(3, 120, 60)], [point(2, 60, 60)], 1),
    ),
    null,
  );
  assert.deepEqual(
    nativeRecognizer.end(frame(260, [], [point(3, 120, 60)], 0)),
    { fingers: 2, kind: "tap", taps: 1 },
  );
});

test("overlay gestures resolve from synchronous mode state", () => {
  assert.match(
    appSource,
    /const resolved = modeRef\.current === nextMode \? "main" : nextMode;/,
  );
  assert.match(appSource, /modeRef\.current = resolved;/);
  assert.match(appSource, /setMode\(resolved\);/);
});

test("self-voicing disable remains audible without a native screen reader", () => {
  assert.match(
    appSource,
    /if \(screenReaderEnabled\) \{[\s\S]*announceForNativeScreenReader\(message\);/,
  );
  assert.match(
    appSource,
    /tts\.speakAnnouncement\(message, \{[\s\S]*remember: false,[\s\S]*\}\);[\s\S]*tts\.setUiEnabled\(false\);/,
  );
});

test("self-voicing toggles resolve from synchronous state", () => {
  assert.match(appSource, /selfVoicingEnabledRef\.current = enabled;/);
  assert.match(
    appSource,
    /updateSelfVoicing\(!selfVoicingEnabledRef\.current\);/,
  );
});

const point = (id, x, y) => ({ id, x, y });
const frame = (timestamp, touches, changedTouches = [], activeTouchCount) => ({
  ...(activeTouchCount === undefined ? {} : { activeTouchCount }),
  changedTouches,
  timestamp,
  touches,
});

function beginChord(recognizer, timestamp, points) {
  for (let index = 0; index < points.length; index += 1) {
    recognizer.start(frame(timestamp + index * 20, points.slice(0, index + 1)));
  }
}

function finishChord(recognizer, timestamp, points) {
  let result = null;
  for (let index = 0; index < points.length; index += 1) {
    const remaining = points.slice(index + 1);
    result = recognizer.end(
      frame(timestamp + index * 20, remaining, [points[index]]),
    );
  }
  return result;
}

function performTap(recognizer, timestamp, points) {
  beginChord(recognizer, timestamp, points);
  return finishChord(recognizer, timestamp + 80, points);
}

function performDuplicatedBridgeTap(recognizer, timestamp, points) {
  for (let index = 0; index < points.length; index += 1) {
    const active = points.slice(0, index + 1);
    const transition = frame(
      timestamp + index * 20,
      active,
      [points[index]],
      active.length,
    );
    recognizer.start(transition);
    recognizer.start(transition);
  }

  let result = null;
  for (let index = 0; index < points.length; index += 1) {
    const remaining = points.slice(index + 1);
    const transition = frame(
      timestamp + 80 + index * 20,
      remaining,
      [points[index]],
      remaining.length,
    );
    result = recognizer.end(transition) ?? result;
    result = recognizer.end(transition) ?? result;
  }
  return result;
}

function performSwipe(recognizer, timestamp, starts, movements) {
  beginChord(recognizer, timestamp, starts);
  for (let index = 0; index < movements.length; index += 1) {
    recognizer.move(frame(timestamp + 80 + index * 30, movements[index]));
  }
  return finishChord(
    recognizer,
    timestamp + 80 + movements.length * 30,
    movements[movements.length - 1],
  );
}

const directionDelta = Object.freeze({
  down: [0, 80],
  left: [-80, 0],
  right: [80, 0],
  up: [0, -80],
});

function pointsForPath(start, directions) {
  const points = [{ x: start.x, y: start.y }];
  let current = points[0];
  for (const direction of directions) {
    const [deltaX, deltaY] = directionDelta[direction];
    const midpoint = {
      x: current.x + deltaX / 2,
      y: current.y + deltaY / 2,
    };
    current = {
      x: current.x + deltaX,
      y: current.y + deltaY,
    };
    points.push(midpoint, current);
  }
  return points;
}

test("classifies straight and multi-direction paths", () => {
  assert.deepEqual(
    classifyGesturePath([
      { x: 100, y: 100 },
      { x: 100, y: 60 },
      { x: 100, y: 20 },
    ]),
    ["up"],
  );
  assert.deepEqual(
    classifyGesturePath([
      { x: 100, y: 100 },
      { x: 100, y: 60 },
      { x: 100, y: 20 },
      { x: 60, y: 20 },
      { x: 20, y: 20 },
    ]),
    ["up", "left"],
  );
  assert.deepEqual(
    classifyGesturePath([
      { x: 100, y: 100 },
      { x: 60, y: 100 },
      { x: 20, y: 100 },
      { x: 60, y: 100 },
      { x: 100, y: 100 },
    ]),
    ["left", "right"],
  );
  assert.deepEqual(
    classifyGesturePath([
      { x: 100, y: 100 },
      { x: 100, y: 60 },
      { x: 100, y: 20 },
      { x: 60, y: 20 },
      { x: 20, y: 20 },
      { x: 20, y: 60 },
      { x: 20, y: 100 },
    ]),
    ["up", "left", "down"],
  );
  assert.deepEqual(
    classifyGesturePath([
      { x: 100, y: 100 },
      { x: 103, y: 82 },
      { x: 97, y: 63 },
      { x: 102, y: 44 },
      { x: 99, y: 25 },
    ]),
    ["up"],
  );
});

test("uses native-style confirmation distances for single and multi-finger swipes", () => {
  const recognizer = new SelfVoicingGestureRecognizer();

  assert.equal(
    performSwipe(recognizer, 0, [point(1, 40, 20)], [
      [point(1, 40, 45)],
      [point(1, 40, 70)],
    ]),
    null,
  );
  assert.deepEqual(
    performSwipe(recognizer, 400, [point(2, 40, 20)], [
      [point(2, 40, 60)],
      [point(2, 40, 90)],
    ]),
    { fingers: 1, kind: "swipe", path: ["down"] },
  );

  assert.deepEqual(
    performSwipe(
      recognizer,
      800,
      [point(3, 40, 20), point(4, 100, 20)],
      [[point(3, 40, 42), point(4, 100, 42)]],
    ),
    { fingers: 2, kind: "swipe", path: ["down"] },
  );
});

test("recognizes consecutive two-finger swipes without suppressing the second", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const starts = [point(1, 40, 20), point(2, 100, 20)];
  const moved = [
    [point(1, 40, 60), point(2, 100, 60)],
    [point(1, 40, 110), point(2, 100, 110)],
  ];

  assert.deepEqual(performSwipe(recognizer, 0, starts, moved), {
    fingers: 2,
    kind: "swipe",
    path: ["down"],
  });
  assert.deepEqual(performSwipe(recognizer, 400, starts, moved), {
    fingers: 2,
    kind: "swipe",
    path: ["down"],
  });
});

test("recognizes a long run of consecutive two-finger overlay toggles", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  for (let index = 0; index < 100; index += 1) {
    const firstId = index * 2 + 1;
    const starts = [point(firstId, 40, 20), point(firstId + 1, 100, 20)];
    const moved = [
      [point(firstId, 40, 60), point(firstId + 1, 100, 60)],
      [point(firstId, 40, 110), point(firstId + 1, 100, 110)],
    ];
    assert.deepEqual(performSwipe(recognizer, index * 400, starts, moved), {
      fingers: 2,
      kind: "swipe",
      path: ["down"],
    });
  }
});

test("tracks all three pointer paths through staggered lifts", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const starts = [
    point(11, 30, 140),
    point(12, 90, 140),
    point(13, 150, 140),
  ];
  const result = performSwipe(recognizer, 0, starts, [
    [point(11, 30, 100), point(12, 90, 100), point(13, 150, 100)],
    [point(11, 30, 50), point(12, 90, 50), point(13, 150, 50)],
  ]);

  assert.deepEqual(result, {
    fingers: 3,
    kind: "swipe",
    path: ["up"],
  });
});

test("recognizes a three-finger triple tap with new pointer ids on every tap", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const taps = [
    [point(1, 30, 80), point(2, 90, 80), point(3, 150, 80)],
    [point(4, 34, 84), point(5, 94, 84), point(6, 154, 84)],
    [point(7, 28, 78), point(8, 88, 78), point(9, 148, 78)],
  ];

  assert.deepEqual(performTap(recognizer, 0, taps[0]), {
    fingers: 3,
    kind: "tap",
    taps: 1,
  });
  assert.deepEqual(performTap(recognizer, 600, taps[1]), {
    fingers: 3,
    kind: "tap",
    taps: 2,
  });
  assert.deepEqual(performTap(recognizer, 1200, taps[2]), {
    fingers: 3,
    kind: "tap",
    taps: 3,
  });
});

test("recognizes rapid three-finger taps without a one-finger minimum-gap rule", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const taps = [
    [point(1, 30, 80), point(2, 90, 80), point(3, 150, 80)],
    [point(4, 32, 82), point(5, 92, 82), point(6, 152, 82)],
    [point(7, 28, 78), point(8, 88, 78), point(9, 148, 78)],
  ];

  assert.equal(performTap(recognizer, 0, taps[0])?.taps, 1);
  assert.equal(performTap(recognizer, 140, taps[1])?.taps, 2);
  assert.equal(performTap(recognizer, 280, taps[2])?.taps, 3);
});

test("does not merge out-of-order multi-finger tap timestamps", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const first = [point(1, 30, 80), point(2, 90, 80), point(3, 150, 80)];
  const second = [point(4, 30, 80), point(5, 90, 80), point(6, 150, 80)];

  assert.equal(performTap(recognizer, 100, first)?.taps, 1);
  assert.equal(performTap(recognizer, 200, second)?.taps, 1);
});

test("recognizes rapid three-finger triple taps through duplicate bridge frames", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  let timestamp = 0;
  let nextId = 1;
  for (let tap = 1; tap <= 3; tap += 1) {
    const points = [
      point(nextId, 30, 80),
      point(nextId + 1, 90, 80),
      point(nextId + 2, 150, 80),
    ];
    nextId += 3;
    assert.deepEqual(
      performDuplicatedBridgeTap(recognizer, timestamp, points),
      { fingers: 3, kind: "tap", taps: tap },
    );
    timestamp += 140;
  }
});

test("recognizes repeated three-finger triple taps with jitter and fresh ids", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  let timestamp = 0;
  let nextId = 1;
  for (let sequence = 0; sequence < 20; sequence += 1) {
    for (let tapOrdinal = 1; tapOrdinal <= 3; tapOrdinal += 1) {
      const jitter = ((sequence + tapOrdinal) % 5) - 2;
      const points = [
        point(nextId, 30 + jitter, 80 - jitter),
        point(nextId + 1, 90 - jitter, 80 + jitter),
        point(nextId + 2, 150 + jitter, 80 + jitter),
      ];
      nextId += 3;
      assert.deepEqual(performTap(recognizer, timestamp, points), {
        fingers: 3,
        kind: "tap",
        taps: tapOrdinal,
      });
      timestamp += 600;
    }
  }
});

test("tracks one-finger double-tap ordinals and expires stale sequences", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  assert.deepEqual(performTap(recognizer, 0, [point(1, 60, 60)]), {
    fingers: 1,
    kind: "tap",
    taps: 1,
  });

  recognizer.start(frame(200, [point(2, 64, 64)]));
  assert.equal(recognizer.getCurrentTapOrdinal(1), 2);
  assert.deepEqual(
    recognizer.end(frame(260, [], [point(2, 64, 64)])),
    {
      fingers: 1,
      kind: "tap",
      taps: 2,
    },
  );

  assert.deepEqual(performTap(recognizer, 900, [point(3, 60, 60)]), {
    fingers: 1,
    kind: "tap",
    taps: 1,
  });
});

test("allows completed tap actions to consume their sequence history", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const firstTap = [point(1, 60, 60)];
  const secondTap = [point(2, 62, 62)];
  assert.equal(performTap(recognizer, 0, firstTap)?.taps, 1);
  assert.equal(performTap(recognizer, 200, secondTap)?.taps, 2);

  recognizer.resetTapSequence(1);

  assert.equal(performTap(recognizer, 400, [point(3, 60, 60)])?.taps, 1);
});

test("expires a partial three-finger multi-tap sequence", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const first = [point(1, 30, 60), point(2, 90, 60), point(3, 150, 60)];
  const second = [point(4, 30, 60), point(5, 90, 60), point(6, 150, 60)];
  assert.equal(performTap(recognizer, 0, first)?.taps, 1);
  assert.equal(performTap(recognizer, 1000, second)?.taps, 1);
});

test("restarts a tap sequence when taps are implausibly close", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  assert.equal(performTap(recognizer, 0, [point(1, 60, 60)])?.taps, 1);
  assert.equal(performTap(recognizer, 100, [point(2, 60, 60)])?.taps, 1);
  assert.equal(performTap(recognizer, 300, [point(3, 60, 60)])?.taps, 2);
});

test("classifies a moving three-finger chord as a swipe rather than a tap", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const starts = [point(1, 20, 20), point(2, 80, 20), point(3, 140, 20)];
  beginChord(recognizer, 0, starts);
  recognizer.move(
    frame(100, [point(1, 20, 45), point(2, 80, 45), point(3, 140, 45)]),
  );

  assert.deepEqual(
    finishChord(
      recognizer,
      140,
      [point(1, 20, 45), point(2, 80, 45), point(3, 140, 45)],
    ),
    {
      fingers: 3,
      kind: "swipe",
      path: ["down"],
    },
  );
});

test("preserves original finger-down points when later fingers join", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  recognizer.start(frame(0, [point(1, 20, 20)]));
  recognizer.move(frame(40, [point(1, 60, 20)]));
  recognizer.start(frame(60, [point(1, 60, 20), point(2, 90, 20)]));
  recognizer.start(
    frame(80, [point(1, 60, 20), point(2, 90, 20), point(3, 150, 20)]),
  );

  assert.equal(
    finishChord(
      recognizer,
      120,
      [point(1, 60, 20), point(2, 90, 20), point(3, 150, 20)],
    ),
    null,
  );
});

test("accepts ordinary multi-finger tap tremor inside scaled touch slop", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const starts = [point(1, 20, 20), point(2, 80, 20), point(3, 140, 20)];
  beginChord(recognizer, 0, starts);
  recognizer.move(
    frame(60, [point(1, 27, 25), point(2, 74, 27), point(3, 146, 15)]),
  );

  assert.deepEqual(
    finishChord(
      recognizer,
      100,
      [point(1, 27, 25), point(2, 74, 27), point(3, 146, 15)],
    ),
    { fingers: 3, kind: "tap", taps: 1 },
  );
});

test("recognizes coordinated multi-finger directional paths", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const starts = [point(1, 80, 140), point(2, 140, 140)];
  const result = performSwipe(recognizer, 0, starts, [
    [point(1, 80, 100), point(2, 140, 100)],
    [point(1, 80, 60), point(2, 140, 60)],
    [point(1, 40, 60), point(2, 100, 60)],
    [point(1, 0, 60), point(2, 60, 60)],
  ]);

  assert.deepEqual(result, {
    fingers: 2,
    kind: "swipe",
    path: ["up", "left"],
  });
});

test("classifies every ordered two-direction cardinal gesture", () => {
  const directions = Object.keys(directionDelta);
  for (const first of directions) {
    for (const second of directions) {
      if (first === second) {
        continue;
      }
      const path = pointsForPath({ x: 200, y: 200 }, [first, second]);
      assert.deepEqual(classifyGesturePath(path), [first, second]);
    }
  }
});

test("recognizes coordinated paths from one through four fingers", () => {
  for (let fingers = 1; fingers <= 4; fingers += 1) {
    const recognizer = new SelfVoicingGestureRecognizer();
    const perFingerPaths = Array.from({ length: fingers }, (_unused, index) =>
      pointsForPath({ x: 220 + index * 45, y: 220 }, ["up", "left"]),
    );
    const starts = perFingerPaths.map((path, index) =>
      point(index + 1, path[0].x, path[0].y),
    );
    const movements = perFingerPaths[0].slice(1).map((_unused, sampleIndex) =>
      perFingerPaths.map((path, pointerIndex) =>
        point(pointerIndex + 1, path[sampleIndex + 1].x, path[sampleIndex + 1].y),
      ),
    );
    assert.deepEqual(performSwipe(recognizer, 0, starts, movements), {
      fingers,
      kind: "swipe",
      path: ["up", "left"],
    });
  }
});

test("supports four-finger recognition for future gesture mappings", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const starts = [
    point(1, 20, 20),
    point(2, 70, 20),
    point(3, 120, 20),
    point(4, 170, 20),
  ];
  const result = performSwipe(recognizer, 0, starts, [
    [
      point(1, 20, 60),
      point(2, 70, 60),
      point(3, 120, 60),
      point(4, 170, 60),
    ],
    [
      point(1, 20, 110),
      point(2, 70, 110),
      point(3, 120, 110),
      point(4, 170, 110),
    ],
  ]);

  assert.deepEqual(result, {
    fingers: 4,
    kind: "swipe",
    path: ["down"],
  });
});

test("rejects a multi-finger swipe when the pointers disagree", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const starts = [point(1, 40, 80), point(2, 100, 80)];
  const result = performSwipe(recognizer, 0, starts, [
    [point(1, 40, 30), point(2, 100, 130)],
    [point(1, 40, 0), point(2, 100, 160)],
  ]);

  assert.equal(result, null);
});

test("rejects pointer replacement inside an active chord", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  recognizer.start(frame(0, [point(1, 20, 20), point(2, 80, 20)]));
  recognizer.start(frame(30, [point(1, 20, 20), point(3, 140, 20)]));

  assert.equal(
    finishChord(recognizer, 80, [point(1, 20, 20), point(3, 140, 20)]),
    null,
  );
});

test("tracks a coalesced pointer-down transition observed on move", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  recognizer.start(frame(0, [point(1, 20, 20)]));
  recognizer.move(frame(30, [point(1, 20, 20), point(2, 80, 20)]));
  recognizer.move(frame(90, [point(1, 20, 70), point(2, 80, 70)]));

  assert.deepEqual(
    finishChord(recognizer, 130, [point(1, 20, 70), point(2, 80, 70)]),
    { fingers: 2, kind: "swipe", path: ["down"] },
  );
});

test("uses changed touches to recover an incomplete bridged pointer-down frame", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const first = point(1, 20, 20);
  const second = point(2, 80, 20);
  recognizer.start(frame(0, [first], [first], 1));
  recognizer.start(frame(20, [first], [second], 2));
  recognizer.move(
    frame(80, [point(1, 20, 70), point(2, 80, 70)], [], 2),
  );

  assert.equal(
    recognizer.end(frame(120, [point(2, 80, 70)], [point(1, 20, 70)], 1)),
    null,
  );
  assert.deepEqual(
    recognizer.end(frame(140, [], [point(2, 80, 70)], 0)),
    { fingers: 2, kind: "swipe", path: ["down"] },
  );
});

test("does not finalize on an incomplete intermediate pointer-up frame", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const starts = [point(1, 20, 20), point(2, 80, 20)];
  recognizer.start(frame(0, starts, starts, 2));
  recognizer.move(
    frame(60, [point(1, 20, 70), point(2, 80, 70)], [], 2),
  );

  assert.equal(
    recognizer.end(frame(100, [], [point(1, 20, 70)], 1)),
    null,
  );
  assert.equal(recognizer.getActiveFingerCount(), 1);
  assert.deepEqual(
    recognizer.end(frame(120, [], [point(2, 80, 70)], 0)),
    { fingers: 2, kind: "swipe", path: ["down"] },
  );
});

test("never downgrades a reported multi-finger chord to a one-finger tap", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const onlyBridgedPointer = point(1, 40, 40);
  recognizer.start(frame(0, [onlyBridgedPointer], [onlyBridgedPointer], 3));

  assert.equal(
    recognizer.end(frame(80, [], [onlyBridgedPointer], 0)),
    null,
  );
  assert.deepEqual(
    performTap(recognizer, 200, [point(2, 40, 40)]),
    { fingers: 1, kind: "tap", taps: 1 },
  );
});

test("accepts duplicate raw-touch and responder transition frames", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const starts = [point(1, 20, 20), point(2, 80, 20)];
  recognizer.start(frame(0, starts, [starts[1]], 2));
  recognizer.start(frame(0, starts, [starts[1]], 2));
  recognizer.move(
    frame(60, [point(1, 20, 70), point(2, 80, 70)], [], 2),
  );
  recognizer.move(
    frame(60, [point(1, 20, 70), point(2, 80, 70)], [], 2),
  );

  assert.equal(
    recognizer.end(frame(100, [point(2, 80, 70)], [point(1, 20, 70)], 1)),
    null,
  );
  assert.equal(
    recognizer.end(frame(100, [point(2, 80, 70)], [point(1, 20, 70)], 1)),
    null,
  );
  assert.deepEqual(
    recognizer.end(frame(120, [], [point(2, 80, 70)], 0)),
    { fingers: 2, kind: "swipe", path: ["down"] },
  );
});

test("an intervening chord clears incompatible tap-sequence history", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  assert.equal(performTap(recognizer, 0, [point(1, 40, 40)])?.taps, 1);
  assert.equal(
    performTap(recognizer, 180, [point(2, 20, 40), point(3, 80, 40)])?.fingers,
    2,
  );
  assert.deepEqual(
    performTap(recognizer, 360, [point(4, 40, 40)]),
    { fingers: 1, kind: "tap", taps: 1 },
  );
});

test("an incomplete multi-finger chord breaks a pending one-finger tap sequence", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  assert.equal(performTap(recognizer, 0, [point(1, 40, 40)])?.taps, 1);

  const onlyBridgedPointer = point(2, 40, 40);
  recognizer.start(frame(160, [onlyBridgedPointer], [onlyBridgedPointer], 3));
  assert.equal(
    recognizer.end(frame(220, [], [onlyBridgedPointer], 0)),
    null,
  );

  assert.deepEqual(
    performTap(recognizer, 320, [point(3, 40, 40)]),
    { fingers: 1, kind: "tap", taps: 1 },
  );
});

test("a consumed swipe can explicitly break pending tap sequences", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  assert.equal(performTap(recognizer, 0, [point(1, 40, 40)])?.taps, 1);

  recognizer.start(frame(160, [point(2, 40, 40)]));
  recognizer.move(frame(220, [point(2, 40, 100)]));
  recognizer.consumeActiveGesture(true);
  assert.equal(
    recognizer.end(frame(240, [], [point(2, 40, 100)])),
    null,
  );

  assert.deepEqual(
    performTap(recognizer, 320, [point(3, 40, 40)]),
    { fingers: 1, kind: "tap", taps: 1 },
  );
});

test("rejects a finger that returns after a coalesced partial lift", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  recognizer.start(frame(0, [point(1, 20, 20), point(2, 80, 20)]));
  recognizer.move(frame(40, [point(1, 20, 20)]));
  recognizer.move(frame(80, [point(1, 20, 20), point(2, 80, 20)]));

  assert.equal(
    finishChord(recognizer, 120, [point(1, 20, 20), point(2, 80, 20)]),
    null,
  );
});

test("fails closed when a native touch frame is malformed", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  recognizer.start(frame(0, [point(1, 20, 20)]));
  recognizer.move({ timestamp: 40, touches: [], valid: false });

  assert.equal(
    recognizer.end(frame(80, [], [point(1, 20, 20)])),
    null,
  );
});

test("rejects chords beyond the configured finger limit", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  const points = [
    point(1, 20, 20),
    point(2, 60, 20),
    point(3, 100, 20),
    point(4, 140, 20),
    point(5, 180, 20),
  ];
  beginChord(recognizer, 0, points);
  assert.equal(finishChord(recognizer, 120, points), null);
});

test("invalidates tap chords with excessively delayed pointer transitions", () => {
  const recognizer = new SelfVoicingGestureRecognizer({
    tapTransitionTimeoutMs: 100,
  });
  recognizer.start(frame(0, [point(1, 20, 20)]));
  recognizer.start(frame(150, [point(1, 20, 20), point(2, 80, 20)]));

  assert.equal(
    finishChord(recognizer, 200, [point(1, 20, 20), point(2, 80, 20)]),
    null,
  );
});

test("cancel drops only the active chord while clear also drops tap history", () => {
  const recognizer = new SelfVoicingGestureRecognizer();
  assert.equal(performTap(recognizer, 0, [point(1, 60, 60)])?.taps, 1);

  recognizer.start(frame(200, [point(2, 60, 60)]));
  recognizer.cancel();
  assert.equal(performTap(recognizer, 300, [point(3, 60, 60)])?.taps, 2);

  recognizer.clear();
  assert.equal(performTap(recognizer, 500, [point(4, 60, 60)])?.taps, 1);
});
