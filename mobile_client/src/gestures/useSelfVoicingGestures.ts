import { useEffect, useMemo, useRef } from "react";
import {
  DeviceEventEmitter,
  NativeModules,
  PanResponder,
  Platform,
  type GestureResponderEvent,
  type PanResponderGestureState,
} from "react-native";

import {
  type GestureDirection,
  type GestureRecognizerConfig,
  type GestureTouch,
  type GestureTouchFrame,
  type RecognizedGesture,
  SelfVoicingGestureRecognizer,
} from "./SelfVoicingGestureRecognizer";

export type GestureCallbacks = {
  enabled: boolean;
  globalToggleEnabled?: boolean;
  isNativeTextInputTarget?: (target: unknown) => boolean;
  isTextInputEditing?: () => boolean;
  onDoubleTap: () => void;
  onDoubleTapHold: () => void;
  onGesture?: (gesture: RecognizedGesture) => void;
  onSingleFingerSwipe: (direction: GestureDirection) => void;
  onSingleFingerSwipeHold?: (direction: GestureDirection) => void;
  onThreeFingerSwipe: (direction: GestureDirection) => void;
  onThreeFingerTripleTap: () => void;
  onTwoFingerSwipe: (direction: GestureDirection) => void;
  onTwoFingerTap: () => void;
};

type NativeTouchPoint = {
  identifier?: number | string;
  locationX?: number;
  locationY?: number;
  pageX?: number;
  pageY?: number;
};

type NativeGestureConfiguration = {
  doubleTapSlopDp?: number;
  longPressTimeoutMs?: number;
  multiTapTimeoutMs?: number;
  pathSampleDistanceDp?: number;
  singleFingerSwipeConfirmDistanceDp?: number;
  touchSlopDp?: number;
};

type NativeGestureInputModule = {
  available?: boolean;
  eventName?: string;
};

type NativeGestureFrame = {
  activeTouchCount?: number;
  changedTouches?: NativeTouchPoint[];
  phase?: GestureFramePhase;
  startsGesture?: boolean;
  timestamp?: number;
  touches?: NativeTouchPoint[];
};

type GestureFramePhase = "end" | "move" | "start";

const STANDARD_LONG_PRESS_TIMEOUT_MS = 500;
const SWIPE_HOLD_REPEAT_MS = 170;

const nativeGestureConfiguration =
  Platform.OS === "android"
    ? NativeModules.PlayAuralGestureConfiguration as NativeGestureConfiguration | undefined
    : undefined;

const nativeGestureInput =
  Platform.OS === "android"
    ? NativeModules.PlayAuralGestureInput as NativeGestureInputModule | undefined
    : undefined;
const nativeGestureEventName =
  typeof nativeGestureInput?.eventName === "string" && nativeGestureInput.eventName.length > 0
    ? nativeGestureInput.eventName
    : "PlayAuralGestureFrames";
const usesNativeMultiTouchInput = nativeGestureInput?.available === true;

const positiveFiniteNumber = (value: unknown): number | undefined =>
  typeof value === "number" && Number.isFinite(value) && value > 0
    ? value
    : undefined;

const nativePathSampleDistance = positiveFiniteNumber(
  nativeGestureConfiguration?.pathSampleDistanceDp,
);
const nativeMultiTapTimeout = positiveFiniteNumber(
  nativeGestureConfiguration?.multiTapTimeoutMs,
);
const NATIVE_RECOGNIZER_CONFIG: Partial<GestureRecognizerConfig> = {
  doubleTapSlopDp: positiveFiniteNumber(
    nativeGestureConfiguration?.doubleTapSlopDp,
  ),
  minimumSegmentDistanceDp: nativePathSampleDistance,
  multiTapTimeoutMs: nativeMultiTapTimeout,
  pathSampleDistanceDp: nativePathSampleDistance,
  singleFingerSwipeConfirmDistanceDp: positiveFiniteNumber(
    nativeGestureConfiguration?.singleFingerSwipeConfirmDistanceDp,
  ),
  tapTransitionTimeoutMs: nativeMultiTapTimeout,
  touchSlopDp: positiveFiniteNumber(nativeGestureConfiguration?.touchSlopDp),
};

Object.keys(NATIVE_RECOGNIZER_CONFIG).forEach((key) => {
  const configKey = key as keyof GestureRecognizerConfig;
  if (NATIVE_RECOGNIZER_CONFIG[configKey] === undefined) {
    delete NATIVE_RECOGNIZER_CONFIG[configKey];
  }
});

const GESTURE_INTERACTION_TIMING = Object.freeze({
  // Android honors the user's system long-press preference. Other platforms
  // retain the standard screen-reader timing.
  holdDelayMs:
    positiveFiniteNumber(nativeGestureConfiguration?.longPressTimeoutMs) ??
    STANDARD_LONG_PRESS_TIMEOUT_MS,
  // Preserve the established PlayAural continuous-navigation cadence.
  swipeHoldRepeatMs: SWIPE_HOLD_REPEAT_MS,
});

const getNativeTouchArray = (
  event: GestureResponderEvent,
  key: "changedTouches" | "touches",
): NativeTouchPoint[] => {
  const nativeEvent = event.nativeEvent as GestureResponderEvent["nativeEvent"] & {
    changedTouches?: NativeTouchPoint[];
    touches?: NativeTouchPoint[];
  };
  const touches = nativeEvent[key];
  return Array.isArray(touches) ? touches : [];
};

const toGestureTouches = (touches: NativeTouchPoint[]): GestureTouch[] | null => {
  const parsed: GestureTouch[] = [];
  for (const touch of touches) {
    const x = touch.pageX ?? touch.locationX;
    const y = touch.pageY ?? touch.locationY;
    if (
      touch.identifier === undefined ||
      typeof x !== "number" ||
      !Number.isFinite(x) ||
      typeof y !== "number" ||
      !Number.isFinite(y)
    ) {
      return null;
    }
    parsed.push({
      id: touch.identifier,
      x,
      y,
    });
  }
  return parsed;
};

const toGestureFrame = (
  event: GestureResponderEvent,
  phase: GestureFramePhase,
  gestureState?: PanResponderGestureState,
): GestureTouchFrame => {
  const nativeEvent = event.nativeEvent as GestureResponderEvent["nativeEvent"] & {
    timestamp?: number;
  };
  const changedTouches = toGestureTouches(getNativeTouchArray(event, "changedTouches"));
  const touches = toGestureTouches(getNativeTouchArray(event, "touches"));
  const responderTouchCount = gestureState?.numberActiveTouches;
  const startTouchIds = new Set(
    [...(touches ?? []), ...(changedTouches ?? [])].map((touch) => touch.id),
  );
  return {
    activeTouchCount:
      typeof responderTouchCount === "number" &&
      Number.isInteger(responderTouchCount) &&
      responderTouchCount >= 0
        ? responderTouchCount
        : phase === "start"
          ? startTouchIds.size
          : touches?.length ?? 0,
    changedTouches: changedTouches ?? [],
    timestamp:
      typeof nativeEvent.timestamp === "number" && Number.isFinite(nativeEvent.timestamp)
        ? nativeEvent.timestamp
        : Date.now(),
    touches: touches ?? [],
    valid: changedTouches !== null && touches !== null,
  };
};

const toNativeGestureFrame = (
  value: unknown,
): { frame: GestureTouchFrame; phase: GestureFramePhase | "cancel"; startsGesture: boolean } | null => {
  if (!value || typeof value !== "object") {
    return null;
  }
  const nativeFrame = value as NativeGestureFrame;
  if (
    nativeFrame.phase !== "start" &&
    nativeFrame.phase !== "move" &&
    nativeFrame.phase !== "end" &&
    nativeFrame.phase !== "cancel"
  ) {
    return null;
  }
  if (
    !Array.isArray(nativeFrame.changedTouches) ||
    !Array.isArray(nativeFrame.touches) ||
    typeof nativeFrame.activeTouchCount !== "number" ||
    !Number.isInteger(nativeFrame.activeTouchCount) ||
    nativeFrame.activeTouchCount < 0 ||
    typeof nativeFrame.timestamp !== "number" ||
    !Number.isFinite(nativeFrame.timestamp)
  ) {
    return null;
  }
  const changedTouches = toGestureTouches(nativeFrame.changedTouches);
  const touches = toGestureTouches(nativeFrame.touches);
  if (!changedTouches || !touches) {
    return null;
  }
  return {
    frame: {
      activeTouchCount: nativeFrame.activeTouchCount,
      changedTouches,
      timestamp: nativeFrame.timestamp,
      touches,
      valid: true,
    },
    phase: nativeFrame.phase,
    startsGesture: nativeFrame.startsGesture === true,
  };
};

const gestureDistance = (gestureState: PanResponderGestureState) =>
  Math.hypot(gestureState.dx, gestureState.dy);

export function useSelfVoicingGestures(callbacks: GestureCallbacks) {
  const callbacksRef = useRef(callbacks);
  const recognizer = useMemo(
    () => new SelfVoicingGestureRecognizer(NATIVE_RECOGNIZER_CONFIG),
    [],
  );
  const nativeMultiTouchRecognizer = useMemo(
    () => new SelfVoicingGestureRecognizer(NATIVE_RECOGNIZER_CONFIG),
    [],
  );
  const doubleTapHoldTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const swipeHoldStartTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const swipeHoldRepeatTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const committedSwipeRef = useRef<RecognizedGesture | null>(null);
  const nativeMultiTouchActiveRef = useRef(false);

  // Responder callbacks are intentionally stable; update their live behavior
  // synchronously so an overlay transition cannot leave one event on stale UI.
  callbacksRef.current = callbacks;

  const clearDoubleTapHold = () => {
    if (doubleTapHoldTimerRef.current) {
      clearTimeout(doubleTapHoldTimerRef.current);
      doubleTapHoldTimerRef.current = null;
    }
  };

  const stopSwipeHold = () => {
    if (swipeHoldStartTimerRef.current) {
      clearTimeout(swipeHoldStartTimerRef.current);
      swipeHoldStartTimerRef.current = null;
    }
    if (swipeHoldRepeatTimerRef.current) {
      clearInterval(swipeHoldRepeatTimerRef.current);
      swipeHoldRepeatTimerRef.current = null;
    }
  };

  const resetResponderGesture = (clearTapHistory = false) => {
    clearDoubleTapHold();
    stopSwipeHold();
    if (clearTapHistory) {
      recognizer.clear();
    } else {
      recognizer.cancel();
    }
  };

  const resetActiveGesture = (clearTapHistory = false) => {
    resetResponderGesture(clearTapHistory);
    committedSwipeRef.current = null;
  };

  const handleResponderCancellation = () => {
    if (usesNativeMultiTouchInput && nativeMultiTouchActiveRef.current) {
      resetResponderGesture(true);
    } else {
      resetActiveGesture(true);
    }
  };

  useEffect(
    () => () => {
      resetActiveGesture(true);
      nativeMultiTouchRecognizer.clear();
      nativeMultiTouchActiveRef.current = false;
    },
    [],
  );

  const dispatchGesture = (
    gesture: RecognizedGesture,
    sourceRecognizer = recognizer,
  ) => {
    const current = callbacksRef.current;
    current.onGesture?.(gesture);

    if (gesture.kind === "tap") {
      if (
        gesture.fingers === 3 &&
        gesture.taps === 3 &&
        current.globalToggleEnabled !== false
      ) {
        sourceRecognizer.resetTapSequence(gesture.fingers);
        current.onThreeFingerTripleTap();
        return;
      }
      if (!current.enabled) {
        return;
      }
      if (gesture.fingers === 1 && gesture.taps === 2) {
        sourceRecognizer.resetTapSequence(gesture.fingers);
        current.onDoubleTap();
      } else if (gesture.fingers === 2 && gesture.taps === 1) {
        sourceRecognizer.resetTapSequence(gesture.fingers);
        current.onTwoFingerTap();
      }
      return;
    }

    if (!current.enabled || gesture.path.length !== 1) {
      return;
    }
    const direction = gesture.path[0];
    if (gesture.fingers === 1) {
      current.onSingleFingerSwipe(direction);
    } else if (gesture.fingers === 2) {
      current.onTwoFingerSwipe(direction);
    } else if (gesture.fingers === 3) {
      current.onThreeFingerSwipe(direction);
    }
  };

  const beginDoubleTapHoldIfEligible = () => {
    clearDoubleTapHold();
    if (
      !callbacksRef.current.enabled ||
      recognizer.getCurrentTapOrdinal(1) !== 2 ||
      !recognizer.isActiveTapCandidate(1)
    ) {
      return;
    }
    doubleTapHoldTimerRef.current = setTimeout(() => {
      doubleTapHoldTimerRef.current = null;
      if (
        !callbacksRef.current.enabled ||
        recognizer.getCurrentTapOrdinal(1) !== 2 ||
        !recognizer.isActiveTapCandidate(1)
      ) {
        return;
      }
      recognizer.consumeActiveGesture();
      recognizer.resetTapSequence(1);
      callbacksRef.current.onDoubleTapHold();
    }, GESTURE_INTERACTION_TIMING.holdDelayMs);
  };

  const beginSwipeHold = (direction: GestureDirection) => {
    stopSwipeHold();
    swipeHoldStartTimerRef.current = setTimeout(() => {
      swipeHoldStartTimerRef.current = null;
      const committed = committedSwipeRef.current;
      if (
        !callbacksRef.current.enabled ||
        !committed ||
        committed.kind !== "swipe" ||
        committed.fingers !== 1 ||
        committed.path.length !== 1 ||
        committed.path[0] !== direction ||
        recognizer.getActiveFingerCount() !== 1
      ) {
        stopSwipeHold();
        return;
      }
      const repeat =
        callbacksRef.current.onSingleFingerSwipeHold ??
        callbacksRef.current.onSingleFingerSwipe;
      repeat(direction);
      swipeHoldRepeatTimerRef.current = setInterval(() => {
        if (
          !callbacksRef.current.enabled ||
          recognizer.getActiveFingerCount() !== 1
        ) {
          stopSwipeHold();
          return;
        }
        const nextRepeat =
          callbacksRef.current.onSingleFingerSwipeHold ??
          callbacksRef.current.onSingleFingerSwipe;
        nextRepeat(direction);
      }, GESTURE_INTERACTION_TIMING.swipeHoldRepeatMs);
    }, GESTURE_INTERACTION_TIMING.holdDelayMs);
  };

  const dispatchStraightSwipeAsSoonAsRecognized = (
    sourceRecognizer = recognizer,
  ) => {
    if (committedSwipeRef.current) {
      return;
    }
    const preview = sourceRecognizer.getSwipePreview();
    if (
      !callbacksRef.current.enabled ||
      !preview ||
      preview.fingers > 3 ||
      preview.path.length !== 1
    ) {
      return;
    }

    const gesture: RecognizedGesture = {
      fingers: preview.fingers,
      kind: "swipe",
      path: preview.path,
    };
    committedSwipeRef.current = gesture;
    sourceRecognizer.consumeActiveGesture(true);
    dispatchGesture(gesture, sourceRecognizer);
    if (gesture.fingers === 1) {
      beginSwipeHold(gesture.path[0]);
    }
  };

  const shouldClaimGesture = (
    event: GestureResponderEvent,
    gestureState: PanResponderGestureState,
    moving: boolean,
  ) => {
    const current = callbacksRef.current;
    const touchCount = Math.max(
      event.nativeEvent.touches.length,
      gestureState.numberActiveTouches,
      1,
    );
    if (current.globalToggleEnabled !== false && touchCount >= 3) {
      return true;
    }
    if (!current.enabled) {
      return false;
    }
    if (touchCount >= 2) {
      return true;
    }
    const isTextInput =
      current.isNativeTextInputTarget?.(event.nativeEvent.target) ?? false;
    if (!isTextInput) {
      return true;
    }
    return Boolean(
      moving &&
        current.isTextInputEditing?.() &&
        gestureDistance(gestureState) >= recognizer.config.touchSlopDp,
    );
  };

  const handleGestureEnd = (
    event: GestureResponderEvent,
    gestureState?: PanResponderGestureState,
  ) => {
    if (usesNativeMultiTouchInput && nativeMultiTouchActiveRef.current) {
      resetResponderGesture(true);
      return;
    }
    clearDoubleTapHold();
    stopSwipeHold();
    const frame = toGestureFrame(event, "end", gestureState);
    const gesture = recognizer.end(frame);
    if (gesture) {
      dispatchGesture(gesture);
    }
    if (recognizer.getActiveFingerCount() === 0) {
      committedSwipeRef.current = null;
    }
  };

  const handleGestureMove = (
    event: GestureResponderEvent,
    gestureState?: PanResponderGestureState,
  ) => {
    if (usesNativeMultiTouchInput && nativeMultiTouchActiveRef.current) {
      resetResponderGesture(true);
      return;
    }
    const frame = toGestureFrame(event, "move", gestureState);
    recognizer.move(frame);
    if (!recognizer.isActiveTapCandidate(1)) {
      clearDoubleTapHold();
    }
    dispatchStraightSwipeAsSoonAsRecognized();
  };

  const handleGestureStart = (
    event: GestureResponderEvent,
    gestureState?: PanResponderGestureState,
  ) => {
    const frame = toGestureFrame(event, "start", gestureState);
    const activeTouchCount = frame.activeTouchCount ?? frame.touches.length;
    if (
      usesNativeMultiTouchInput &&
      (nativeMultiTouchActiveRef.current || activeTouchCount >= 2)
    ) {
      nativeMultiTouchActiveRef.current = true;
      resetResponderGesture(true);
      return;
    }
    recognizer.start(frame);
    if (recognizer.getActiveFingerCount() !== 1) {
      clearDoubleTapHold();
      stopSwipeHold();
    }
  };

  useEffect(() => {
    if (!usesNativeMultiTouchInput || !nativeGestureInput) {
      return undefined;
    }

    const subscription = DeviceEventEmitter.addListener(nativeGestureEventName, (payload: unknown) => {
      const frames =
        payload && typeof payload === "object" && Array.isArray((payload as { frames?: unknown }).frames)
          ? (payload as { frames: unknown[] }).frames.map(toNativeGestureFrame)
          : null;
      if (!frames || frames.length === 0 || frames.some((frame) => frame === null)) {
        nativeMultiTouchRecognizer.clear();
        nativeMultiTouchActiveRef.current = false;
        resetActiveGesture(true);
        return;
      }

      nativeMultiTouchActiveRef.current = true;
      resetResponderGesture(true);
      for (const parsed of frames) {
        if (!parsed) {
          continue;
        }
        if (parsed.startsGesture) {
          nativeMultiTouchRecognizer.cancel();
          committedSwipeRef.current = null;
        }
        if (parsed.phase === "cancel") {
          nativeMultiTouchRecognizer.clear();
          committedSwipeRef.current = null;
          nativeMultiTouchActiveRef.current = false;
          continue;
        }
        if (parsed.phase === "start") {
          nativeMultiTouchRecognizer.start(parsed.frame);
          continue;
        }
        if (parsed.phase === "move") {
          nativeMultiTouchRecognizer.move(parsed.frame);
          dispatchStraightSwipeAsSoonAsRecognized(nativeMultiTouchRecognizer);
          continue;
        }

        const gesture = nativeMultiTouchRecognizer.end(parsed.frame);
        if (gesture) {
          dispatchGesture(gesture, nativeMultiTouchRecognizer);
        }
        if (nativeMultiTouchRecognizer.getActiveFingerCount() === 0) {
          committedSwipeRef.current = null;
          nativeMultiTouchActiveRef.current = false;
        }
      }
    });

    return () => {
      subscription.remove();
      nativeMultiTouchRecognizer.clear();
      nativeMultiTouchActiveRef.current = false;
    };
  }, []);

  return useMemo(() => {
    const panResponder = PanResponder.create({
      onMoveShouldSetPanResponder: (event, gestureState) =>
        shouldClaimGesture(event, gestureState, true),
      onMoveShouldSetPanResponderCapture: (event, gestureState) =>
        shouldClaimGesture(event, gestureState, true),
      onPanResponderEnd: (event, gestureState) => {
        handleGestureEnd(event, gestureState);
      },
      onPanResponderGrant: (event, gestureState) => {
        resetActiveGesture();
        const frame = toGestureFrame(event, "start", gestureState);
        if (
          frame.touches.length === 1 &&
          Number.isFinite(gestureState.x0) &&
          Number.isFinite(gestureState.y0)
        ) {
          recognizer.start({
            ...frame,
            touches: [
              {
                ...frame.touches[0],
                x: gestureState.x0,
                y: gestureState.y0,
              },
            ],
          });
          recognizer.move(frame);
        } else {
          recognizer.start(frame);
        }
        beginDoubleTapHoldIfEligible();
      },
      onPanResponderMove: (event, gestureState) => {
        handleGestureMove(event, gestureState);
      },
      onPanResponderReject: () => {
        handleResponderCancellation();
      },
      onPanResponderRelease: (event, gestureState) => {
        handleGestureEnd(event, gestureState);
      },
      onPanResponderStart: (event, gestureState) => {
        handleGestureStart(event, gestureState);
      },
      onPanResponderTerminate: () => {
        handleResponderCancellation();
      },
      // Once a self-voicing gesture begins, keep one owner for the complete
      // pointer stream. Changing responders mid-chord is indistinguishable
      // from a missing finger and was the main source of intermittent input.
      onPanResponderTerminationRequest: () => false,
      onShouldBlockNativeResponder: () => true,
      onStartShouldSetPanResponder: (event, gestureState) =>
        shouldClaimGesture(event, gestureState, false),
      onStartShouldSetPanResponderCapture: (event, gestureState) =>
        shouldClaimGesture(event, gestureState, false),
    });

    return {
      ...panResponder,
      panHandlers: {
        ...panResponder.panHandlers,
        // Raw touch callbacks cover pointer transitions even when Fabric does
        // not surface an intermediate transition through PanResponder. The
        // recognizer is idempotent for duplicate frames, so both streams feed
        // one authoritative session without competing gesture trackers.
        onTouchCancel: () => {
          handleResponderCancellation();
        },
        onTouchEnd: (event: GestureResponderEvent) => {
          handleGestureEnd(event);
        },
        onTouchMove: (event: GestureResponderEvent) => {
          handleGestureMove(event);
        },
        onTouchStart: (event: GestureResponderEvent) => {
          handleGestureStart(event);
        },
      },
    };
  }, []);
}
