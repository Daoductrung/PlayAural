export type GestureDirection = "up" | "down" | "left" | "right";

export type RecognizedGesture =
  | {
      fingers: number;
      kind: "swipe";
      path: GestureDirection[];
    }
  | {
      fingers: number;
      kind: "tap";
      taps: number;
    };

export type GestureTouch = {
  id: number | string;
  x: number;
  y: number;
};

export type GestureTouchFrame = {
  activeTouchCount?: number;
  changedTouches?: GestureTouch[];
  timestamp: number;
  touches: GestureTouch[];
  valid?: boolean;
};

export type GestureRecognizerConfig = {
  doubleTapSlopDp: number;
  maximumFingerCount: number;
  maximumTapCount: number;
  minimumSingleFingerMultiTapGapMs: number;
  minimumSegmentDistanceDp: number;
  multiFingerMultiTapTimeoutMs: number;
  multiTapTimeoutMs: number;
  pathSampleDistanceDp: number;
  singleFingerSwipeConfirmDistanceDp: number;
  tapTransitionTimeoutMs: number;
  touchSlopDp: number;
  turnCosineThreshold: number;
};

const ANDROID_TOUCH_SLOP_DP = 8;
const ANDROID_DOUBLE_TAP_SLOP_DP = 100;
const ANDROID_DOUBLE_TAP_TIMEOUT_MS = 300;
const ANDROID_DOUBLE_TAP_MIN_TIME_MS = 40;
const ACCESSIBLE_MULTI_FINGER_TAP_TIMEOUT_MS = 760;
const MILLIMETERS_PER_INCH = 25.4;
const DIPS_PER_INCH = 160;
const TALKBACK_SAMPLE_DISTANCE_MM = 2.5;
const TALKBACK_SINGLE_FINGER_SWIPE_CONFIRM_DISTANCE_MM = 10;
const CARDINAL_CORNER_COSINE_TOLERANCE = 0.05;

const millimetersToDips = (millimeters: number) =>
  (millimeters * DIPS_PER_INCH) / MILLIMETERS_PER_INCH;

/**
 * Defaults derive from Android ViewConfiguration and TalkBack's gesture sampling.
 * React Native reports touch coordinates in density-independent points, so the
 * Android dp constants can be used without device-specific pixel conversion.
 * PlayAural deliberately has no swipe-velocity cutoff: unlike an Android
 * AccessibilityService, it does not need to distinguish a swipe from touch
 * exploration, and slow deliberate gestures must remain usable.
 */
export const DEFAULT_GESTURE_RECOGNIZER_CONFIG: Readonly<GestureRecognizerConfig> =
  Object.freeze({
    doubleTapSlopDp: ANDROID_DOUBLE_TAP_SLOP_DP,
    maximumFingerCount: 4,
    maximumTapCount: 3,
    minimumSingleFingerMultiTapGapMs: ANDROID_DOUBLE_TAP_MIN_TIME_MS,
    minimumSegmentDistanceDp: millimetersToDips(TALKBACK_SAMPLE_DISTANCE_MM),
    // Multi-finger chords take longer to place accurately than one-finger
    // activation taps. Preserve PlayAural's field-tested accessible window.
    multiFingerMultiTapTimeoutMs: ACCESSIBLE_MULTI_FINGER_TAP_TIMEOUT_MS,
    multiTapTimeoutMs: ANDROID_DOUBLE_TAP_TIMEOUT_MS,
    pathSampleDistanceDp: millimetersToDips(TALKBACK_SAMPLE_DISTANCE_MM),
    singleFingerSwipeConfirmDistanceDp: millimetersToDips(
      TALKBACK_SINGLE_FINGER_SWIPE_CONFIRM_DISTANCE_MM,
    ),
    // Pointer changes cross the React Native bridge and can be coalesced. A
    // full double-tap window retains TalkBack's per-transition reset behavior
    // without rejecting deliberately staggered multi-finger chords.
    tapTransitionTimeoutMs: ANDROID_DOUBLE_TAP_TIMEOUT_MS,
    touchSlopDp: ANDROID_TOUCH_SLOP_DP,
    // TalkBack splits after a perpendicular turn (dot product < 0). Include a
    // narrow tolerance so an ideal 90-degree path, which produces exactly 0,
    // is not rejected merely because it has no human overshoot.
    turnCosineThreshold: CARDINAL_CORNER_COSINE_TOLERANCE,
  });

type Point = {
  x: number;
  y: number;
};

type PointerTrace = {
  current: Point;
  down: Point;
  samples: Point[];
};

type GestureSession = {
  activeIds: Set<string>;
  activeTouchCount: number;
  activeTopologyComplete: boolean;
  consumed: boolean;
  fingerCount: number;
  invalid: boolean;
  lastTransitionAt: number;
  pointerOrder: string[];
  pointers: Map<string, PointerTrace>;
  startedAt: number;
  tapTransitionsValid: boolean;
};

type TapSequence = {
  completedAt: number;
  count: number;
  points: Point[];
};

const pointDistance = (first: Point, second: Point) =>
  Math.hypot(second.x - first.x, second.y - first.y);

const clonePoint = (point: Point): Point => ({ x: point.x, y: point.y });

const touchKey = (touch: GestureTouch) => `${typeof touch.id}:${String(touch.id)}`;

const toDirection = (deltaX: number, deltaY: number): GestureDirection => {
  if (Math.abs(deltaX) > Math.abs(deltaY)) {
    return deltaX < 0 ? "left" : "right";
  }
  return deltaY < 0 ? "up" : "down";
};

const normalizeVector = (deltaX: number, deltaY: number): Point | null => {
  const length = Math.hypot(deltaX, deltaY);
  if (length === 0) {
    return null;
  }
  return { x: deltaX / length, y: deltaY / length };
};

const appendSample = (
  samples: Point[],
  point: Point,
  minimumDistance: number,
  force = false,
) => {
  const previous = samples[samples.length - 1];
  const movedFarEnough = previous && (
    Math.abs(point.x - previous.x) >= minimumDistance ||
    Math.abs(point.y - previous.y) >= minimumDistance
  );
  if (!previous || force || movedFarEnough) {
    if (!previous || previous.x !== point.x || previous.y !== point.y) {
      samples.push(clonePoint(point));
    }
  }
};

const pathLength = (points: Point[]) => {
  let total = 0;
  for (let index = 1; index < points.length; index += 1) {
    total += pointDistance(points[index - 1], points[index]);
  }
  return total;
};

/**
 * Reduces a sampled stroke to cardinal segments. This follows TalkBack's
 * averaged-vector delimiter approach, which is deliberately tolerant of
 * curved corners and small hand tremors while preserving reversals.
 */
export function classifyGesturePath(
  points: ReadonlyArray<Point>,
  config: Readonly<GestureRecognizerConfig> = DEFAULT_GESTURE_RECOGNIZER_CONFIG,
): GestureDirection[] | null {
  if (points.length < 2) {
    return null;
  }

  const delimiters: Point[] = [clonePoint(points[0])];
  let lastDelimiter = delimiters[0];
  let vectorSumX = 0;
  let vectorSumY = 0;
  let vectorCount = 0;
  let latestLength = 0;

  for (let index = 1; index < points.length; index += 1) {
    const next = points[index];
    if (vectorCount > 0) {
      const averageX = vectorSumX / vectorCount;
      const averageY = vectorSumY / vectorCount;
      const possibleDelimiter = {
        x: lastDelimiter.x + latestLength * averageX,
        y: lastDelimiter.y + latestLength * averageY,
      };
      const nextVector = normalizeVector(
        next.x - possibleDelimiter.x,
        next.y - possibleDelimiter.y,
      );
      if (nextVector) {
        const dotProduct = averageX * nextVector.x + averageY * nextVector.y;
        if (
          dotProduct < config.turnCosineThreshold &&
          pointDistance(lastDelimiter, possibleDelimiter) >=
            config.minimumSegmentDistanceDp
        ) {
          delimiters.push(possibleDelimiter);
          lastDelimiter = possibleDelimiter;
          vectorSumX = 0;
          vectorSumY = 0;
          vectorCount = 0;
          latestLength = 0;
        }
      }
    }

    const vector = normalizeVector(next.x - lastDelimiter.x, next.y - lastDelimiter.y);
    if (!vector) {
      continue;
    }
    latestLength = pointDistance(lastDelimiter, next);
    vectorSumX += vector.x;
    vectorSumY += vector.y;
    vectorCount += 1;
  }

  const finalPoint = points[points.length - 1];
  if (
    pointDistance(lastDelimiter, finalPoint) >= config.minimumSegmentDistanceDp
  ) {
    delimiters.push(clonePoint(finalPoint));
  }
  if (delimiters.length < 2) {
    return null;
  }

  const directions = delimiters.slice(1).map((point, index) => {
    const previous = delimiters[index];
    return toDirection(point.x - previous.x, point.y - previous.y);
  });
  return directions.filter(
    (direction, index) => index === 0 || direction !== directions[index - 1],
  );
}

const matchPointSets = (
  previous: Point[],
  current: Point[],
  maximumDistance: number,
) => {
  if (previous.length !== current.length) {
    return false;
  }
  const unmatched = new Set(previous.map((_point, index) => index));
  for (const point of current) {
    let nearestIndex = -1;
    let nearestDistance = Number.POSITIVE_INFINITY;
    for (const index of unmatched) {
      const distance = pointDistance(previous[index], point);
      if (distance < nearestDistance) {
        nearestDistance = distance;
        nearestIndex = index;
      }
    }
    if (nearestIndex < 0 || nearestDistance > maximumDistance) {
      return false;
    }
    unmatched.delete(nearestIndex);
  }
  return true;
};

export class SelfVoicingGestureRecognizer {
  readonly config: Readonly<GestureRecognizerConfig>;

  private session: GestureSession | null = null;
  private readonly tapSequences = new Map<number, TapSequence>();

  constructor(config: Partial<GestureRecognizerConfig> = {}) {
    this.config = Object.freeze({
      ...DEFAULT_GESTURE_RECOGNIZER_CONFIG,
      ...config,
    });
  }

  cancel() {
    this.session = null;
  }

  clear() {
    this.session = null;
    this.tapSequences.clear();
  }

  consumeActiveGesture(clearTapSequences = false) {
    if (this.session) {
      this.session.consumed = true;
    }
    if (clearTapSequences) {
      this.tapSequences.clear();
    }
  }

  getActiveFingerCount() {
    return this.session?.activeTouchCount ?? 0;
  }

  resetTapSequence(fingers: number) {
    this.tapSequences.delete(fingers);
  }

  getCurrentTapOrdinal(fingers: number) {
    const session = this.session;
    if (!session || session.fingerCount !== fingers || session.invalid) {
      return 0;
    }
    const currentPoints = this.getSessionStartPoints(session);
    const previous = this.tapSequences.get(fingers);
    if (
      !previous ||
      !this.canContinueTapSequence(
        previous,
        currentPoints,
        session.startedAt,
        fingers,
      )
    ) {
      return 1;
    }
    return Math.min(previous.count + 1, this.config.maximumTapCount);
  }

  isActiveTapCandidate(fingers: number) {
    const session = this.session;
    if (
      !session ||
      session.fingerCount !== fingers ||
      session.invalid ||
      session.consumed ||
      !session.tapTransitionsValid
    ) {
      return false;
    }
    const maximumDrift = this.config.touchSlopDp * fingers;
    const pointerIds = session.pointerOrder.slice(0, fingers);
    return pointerIds.length === fingers && pointerIds.every((id) => {
      const trace = session.pointers.get(id);
      return Boolean(
        trace &&
          trace.samples.every(
            (point) => pointDistance(trace.down, point) <= maximumDrift,
          ),
      );
    });
  }

  getSwipePreview(): { fingers: number; path: GestureDirection[] } | null {
    const session = this.session;
    if (!session || session.invalid || session.consumed || session.fingerCount === 0) {
      return null;
    }
    const path = this.classifySessionSwipe(session);
    return path ? { fingers: session.fingerCount, path } : null;
  }

  start(frame: GestureTouchFrame) {
    if (!this.session) {
      this.session = {
        activeIds: new Set(),
        activeTopologyComplete: true,
        activeTouchCount: 0,
        consumed: false,
        fingerCount: 0,
        invalid: false,
        lastTransitionAt: frame.timestamp,
        pointerOrder: [],
        pointers: new Map(),
        startedAt: frame.timestamp,
        tapTransitionsValid: true,
      };
    }

    const session = this.session;
    if (frame.valid === false) {
      session.invalid = true;
      return;
    }
    this.ingestTouches(
      session,
      [...frame.touches, ...(frame.changedTouches ?? [])],
      false,
    );
    this.updateActivePointers(
      session,
      frame.touches,
      frame.activeTouchCount,
      frame.timestamp,
    );
  }

  move(frame: GestureTouchFrame) {
    const session = this.session;
    if (!session) {
      return;
    }
    if (frame.valid === false) {
      session.invalid = true;
      return;
    }
    this.ingestTouches(
      session,
      [...frame.touches, ...(frame.changedTouches ?? [])],
      true,
    );
    // React Native may coalesce a pointer transition into a move frame. Treat
    // every frame as authoritative for topology, not only explicit starts.
    this.updateActivePointers(
      session,
      frame.touches,
      frame.activeTouchCount,
      frame.timestamp,
    );
  }

  end(frame: GestureTouchFrame): RecognizedGesture | null {
    const session = this.session;
    if (!session) {
      return null;
    }
    if (frame.valid === false) {
      session.invalid = true;
    }

    const endingTouches = frame.changedTouches ?? [];
    this.ingestTouches(session, [...frame.touches, ...endingTouches], true, true);
    this.updateActivePointers(
      session,
      frame.touches,
      frame.activeTouchCount,
      frame.timestamp,
    );

    if (session.activeTouchCount > 0) {
      return null;
    }

    this.session = null;
    if (session.consumed || session.fingerCount === 0) {
      return null;
    }
    if (session.invalid) {
      this.tapSequences.clear();
      return null;
    }

    const tap = this.finishTap(session, frame.timestamp);
    if (tap) {
      return tap;
    }
    const path = this.classifySessionSwipe(session);
    if (!path) {
      this.tapSequences.clear();
      return null;
    }
    this.tapSequences.clear();
    return {
      fingers: session.fingerCount,
      kind: "swipe",
      path,
    };
  }

  private canContinueTapSequence(
    previous: TapSequence,
    currentPoints: Point[],
    startedAt: number,
    fingers: number,
  ) {
    const gap = startedAt - previous.completedAt;
    const maximumGap =
      fingers >= 3
        ? this.config.multiFingerMultiTapTimeoutMs
        : this.config.multiTapTimeoutMs;
    const minimumGap =
      fingers === 1 ? this.config.minimumSingleFingerMultiTapGapMs : 0;
    return (
      gap >= minimumGap &&
      gap <= maximumGap &&
      matchPointSets(
        previous.points,
        currentPoints,
        this.config.doubleTapSlopDp * fingers,
      )
    );
  }

  private classifySessionSwipe(session: GestureSession) {
    const traces = session.pointerOrder
      .slice(0, session.fingerCount)
      .map((id) => session.pointers.get(id))
      .filter((trace): trace is PointerTrace => Boolean(trace));
    if (traces.length !== session.fingerCount) {
      return null;
    }

    const paths = traces.map((trace) => classifyGesturePath(trace.samples, this.config));
    const reference = paths[0];
    if (!reference || reference.length === 0) {
      return null;
    }
    const minimumTravel = Math.max(
      this.config.minimumSegmentDistanceDp * reference.length,
      session.fingerCount === 1
        ? this.config.singleFingerSwipeConfirmDistanceDp
        : this.config.touchSlopDp * session.fingerCount,
    );
    for (let index = 0; index < traces.length; index += 1) {
      const path = paths[index];
      if (
        !path ||
        path.length !== reference.length ||
        path.some((direction, directionIndex) => direction !== reference[directionIndex]) ||
        pathLength(traces[index].samples) < minimumTravel
      ) {
        return null;
      }
    }
    return reference;
  }

  private finishTap(session: GestureSession, timestamp: number): RecognizedGesture | null {
    if (!session.tapTransitionsValid) {
      return null;
    }
    const maximumDrift = this.config.touchSlopDp * session.fingerCount;
    const traces = session.pointerOrder
      .slice(0, session.fingerCount)
      .map((id) => session.pointers.get(id))
      .filter((trace): trace is PointerTrace => Boolean(trace));
    if (
      traces.length !== session.fingerCount ||
      traces.some((trace) =>
        trace.samples.some((point) => pointDistance(trace.down, point) > maximumDrift),
      )
    ) {
      return null;
    }

    const points = traces.map((trace) => clonePoint(trace.down));
    for (const fingers of this.tapSequences.keys()) {
      if (fingers !== session.fingerCount) {
        this.tapSequences.delete(fingers);
      }
    }
    const previous = this.tapSequences.get(session.fingerCount);
    const count =
      previous &&
      this.canContinueTapSequence(previous, points, session.startedAt, session.fingerCount)
        ? previous.count + 1
        : 1;
    if (count >= this.config.maximumTapCount) {
      this.tapSequences.delete(session.fingerCount);
    } else {
      this.tapSequences.set(session.fingerCount, {
        completedAt: timestamp,
        count,
        points,
      });
    }
    return {
      fingers: session.fingerCount,
      kind: "tap",
      taps: count,
    };
  }

  private getSessionStartPoints(session: GestureSession) {
    return session.pointerOrder
      .slice(0, session.fingerCount)
      .map((id) => session.pointers.get(id))
      .filter((trace): trace is PointerTrace => Boolean(trace))
      .map((trace) => clonePoint(trace.down));
  }

  private ingestTouches(
    session: GestureSession,
    touches: GestureTouch[],
    sample: boolean,
    forceSample = false,
  ) {
    const seen = new Set<string>();
    for (const touch of touches) {
      const id = touchKey(touch);
      if (seen.has(id)) {
        continue;
      }
      seen.add(id);
      const point = { x: touch.x, y: touch.y };
      let trace = session.pointers.get(id);
      if (!trace) {
        trace = {
          current: clonePoint(point),
          down: clonePoint(point),
          samples: [clonePoint(point)],
        };
        session.pointers.set(id, trace);
        session.pointerOrder.push(id);
      } else {
        trace.current = clonePoint(point);
      }
      if (sample) {
        appendSample(
          trace.samples,
          point,
          this.config.pathSampleDistanceDp,
          forceSample,
        );
      }
    }
  }

  private resetClassificationBases(session: GestureSession) {
    for (const id of session.activeIds) {
      const trace = session.pointers.get(id);
      if (!trace) {
        continue;
      }
      trace.samples = [clonePoint(trace.current)];
    }
  }

  private updateActivePointers(
    session: GestureSession,
    touches: GestureTouch[],
    reportedActiveTouchCount: number | undefined,
    timestamp: number,
  ) {
    const hasValidReportedCount =
      typeof reportedActiveTouchCount === "number" &&
      Number.isInteger(reportedActiveTouchCount) &&
      reportedActiveTouchCount >= 0;
    const activeTouchCount =
      hasValidReportedCount
        ? (reportedActiveTouchCount as number)
        : touches.length;
    const previousIds = session.activeIds;
    const nextIds = new Set(touches.map(touchKey));
    const previousCount = session.activeTouchCount;
    const nextCount = activeTouchCount;
    const topologyComplete = touches.length === activeTouchCount;
    const addedPointer = [...nextIds].some((id) => !previousIds.has(id));
    const removedPointer = [...previousIds].some((id) => !nextIds.has(id));

    if (
      session.activeTopologyComplete &&
      topologyComplete &&
      previousCount > 0 &&
      nextCount === previousCount &&
      addedPointer &&
      removedPointer
    ) {
      // A pointer was replaced without an observable transition. Continuing
      // would merge two physical fingers into one logical chord.
      session.invalid = true;
    }

    if (nextCount !== previousCount) {
      if (
        previousCount > 0 &&
        timestamp - session.lastTransitionAt > this.config.tapTransitionTimeoutMs
      ) {
        session.tapTransitionsValid = false;
      }
      session.lastTransitionAt = timestamp;
    }

    session.activeTouchCount = nextCount;
    session.activeTopologyComplete = topologyComplete;
    if (topologyComplete) {
      session.activeIds = nextIds;
    } else if (nextCount === 0) {
      session.activeIds = new Set();
    } else {
      // A bridged frame can briefly omit an unchanged pointer. Retain known
      // active ids and add every pointer the frame did carry; the reported
      // count still prevents the chord from being finalized or downgraded.
      session.activeIds = new Set([...previousIds, ...nextIds]);
    }

    const observedFingerCount = Math.max(nextCount, touches.length);
    if (observedFingerCount > session.fingerCount) {
      session.fingerCount = observedFingerCount;
      if (observedFingerCount > this.config.maximumFingerCount) {
        session.invalid = true;
      }
      this.resetClassificationBases(session);
    } else if (previousCount < session.fingerCount && nextCount > previousCount) {
      // A finger returned before the chord fully ended. Treat the stream as
      // ambiguous instead of turning it into an accidental extra tap.
      session.invalid = true;
    }
  }
}
