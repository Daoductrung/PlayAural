import { useEffect, useMemo, useRef } from "react";
import { PanResponder, type GestureResponderEvent, type PanResponderGestureState } from "react-native";

type SwipeDirection = "up" | "down" | "left" | "right";

type GestureCallbacks = {
  enabled: boolean;
  globalToggleEnabled?: boolean;
  isNativeTextInputTarget?: (target: unknown) => boolean;
  isTextInputEditing?: () => boolean;
  onDoubleTap: () => void;
  onDoubleTapHold: () => void;
  onSingleFingerSwipe: (direction: SwipeDirection) => void;
  onThreeFingerSwipe: (direction: SwipeDirection) => void;
  onThreeFingerTap: () => void;
  onThreeFingerTripleTap: () => void;
  onTwoFingerSwipe: (direction: SwipeDirection) => void;
  onTwoFingerTap: () => void;
};

type TouchTrack = {
  consumed: boolean;
  maxTouches: number;
  moved: boolean;
};

type MultiTouchTrack = {
  consumed: boolean;
  gestureTouches: 2 | 3;
  lastX: number;
  lastY: number;
  moved: boolean;
  startX: number;
  startY: number;
};

type NativeTouchPoint = {
  identifier?: number;
  locationX?: number;
  locationY?: number;
  pageX?: number;
  pageY?: number;
};

const DOUBLE_TAP_WINDOW_MS = 350;
const DOUBLE_TAP_HOLD_MS = 350;
const MULTI_TOUCH_REPEAT_WINDOW_MS = 200;
const MULTI_TOUCH_DOMINANCE_RATIO = 1.25;
const THREE_FINGER_TAP_WINDOW_MS = 650;
const MOVE_TOLERANCE = 4;
const SWIPE_THRESHOLD = 14;

export function useSelfVoicingGestures(callbacks: GestureCallbacks) {
  const callbacksRef = useRef(callbacks);
  const touchTrackRef = useRef<TouchTrack | null>(null);
  const directTouchTrackRef = useRef<MultiTouchTrack | null>(null);
  const lastSingleTapAtRef = useRef(0);
  const lastThreeFingerTapAtRef = useRef(0);
  const threeFingerTapCountRef = useRef(0);
  const holdTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingThreeFingerTapTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const suppressPanReleaseRef = useRef(false);
  const lastMultiTouchDispatchRef = useRef<{ at: number; key: string } | null>(null);

  const clearHoldTimer = () => {
    if (holdTimerRef.current) {
      clearTimeout(holdTimerRef.current);
      holdTimerRef.current = null;
    }
  };

  const clearPendingThreeFingerTapTimer = () => {
    if (pendingThreeFingerTapTimerRef.current) {
      clearTimeout(pendingThreeFingerTapTimerRef.current);
      pendingThreeFingerTapTimerRef.current = null;
    }
  };

  useEffect(() => {
    callbacksRef.current = callbacks;
  }, [callbacks]);

  useEffect(() => () => {
    clearHoldTimer();
    clearPendingThreeFingerTapTimer();
  }, []);

  const getTouchArray = (
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

  const getCentroid = (touches: NativeTouchPoint[]): { x: number; y: number } | null => {
    if (!touches.length) {
      return null;
    }
    const totals = touches.reduce(
      (accumulator, touch) => ({
        x: accumulator.x + (touch.pageX ?? touch.locationX ?? 0),
        y: accumulator.y + (touch.pageY ?? touch.locationY ?? 0),
      }),
      { x: 0, y: 0 },
    );
    return {
      x: totals.x / touches.length,
      y: totals.y / touches.length,
    };
  };

  const getActiveTouchPoint = (event: GestureResponderEvent): { count: number; x: number; y: number } | null => {
    const activeTouches = getTouchArray(event, "touches");
    const centroid = getCentroid(activeTouches);
    if (!centroid) {
      return null;
    }
    return {
      count: activeTouches.length,
      x: centroid.x,
      y: centroid.y,
    };
  };

  const normalizeMultiTouchCount = (activeTouches: number): 0 | 2 | 3 => {
    if (activeTouches >= 3) {
      return 3;
    }
    if (activeTouches >= 2) {
      return 2;
    }
    return 0;
  };

  const beginMultiTouchTrack = (touches: 2 | 3, x: number, y: number): MultiTouchTrack => {
    return {
      consumed: false,
      gestureTouches: touches,
      lastX: x,
      lastY: y,
      moved: false,
      startX: x,
      startY: y,
    };
  };

  const resetMultiTouchTrack = (track: MultiTouchTrack, touches: 2 | 3, x: number, y: number) => {
    track.consumed = false;
    track.gestureTouches = touches;
    track.lastX = x;
    track.lastY = y;
    track.moved = false;
    track.startX = x;
    track.startY = y;
  };

  const classifySwipe = (gestureState: PanResponderGestureState): SwipeDirection | null => {
    const { dx, dy } = gestureState;
    if (Math.max(Math.abs(dx), Math.abs(dy)) < SWIPE_THRESHOLD) {
      return null;
    }
    if (Math.abs(dx) > Math.abs(dy)) {
      return dx > 0 ? "right" : "left";
    }
    return dy > 0 ? "down" : "up";
  };

  const classifySwipeDelta = (dx: number, dy: number): SwipeDirection | null => {
    if (Math.max(Math.abs(dx), Math.abs(dy)) < SWIPE_THRESHOLD) {
      return null;
    }
    const minAxis = Math.min(Math.abs(dx), Math.abs(dy));
    if (minAxis > 0 && Math.max(Math.abs(dx), Math.abs(dy)) / minAxis < MULTI_TOUCH_DOMINANCE_RATIO) {
      return null;
    }
    if (Math.abs(dx) > Math.abs(dy)) {
      return dx > 0 ? "right" : "left";
    }
    return dy > 0 ? "down" : "up";
  };

  const beginHoldDetection = () => {
    clearHoldTimer();
    holdTimerRef.current = setTimeout(() => {
      const track = touchTrackRef.current;
      if (!track || track.moved || track.consumed || track.maxTouches !== 1) {
        return;
      }
      track.consumed = true;
      callbacksRef.current.onDoubleTapHold();
    }, DOUBLE_TAP_HOLD_MS);
  };

  const dispatchSwipe = (direction: SwipeDirection, maxTouches: number) => {
    if (maxTouches >= 2) {
      const key = `swipe:${maxTouches}:${direction}`;
      const now = Date.now();
      const previous = lastMultiTouchDispatchRef.current;
      if (
        previous &&
        previous.key === key &&
        now - previous.at <= MULTI_TOUCH_REPEAT_WINDOW_MS
      ) {
        return;
      }
      lastMultiTouchDispatchRef.current = { at: now, key };
    }
    if (maxTouches >= 3) {
      callbacksRef.current.onThreeFingerSwipe(direction);
      return;
    }
    if (maxTouches >= 2) {
      callbacksRef.current.onTwoFingerSwipe(direction);
      return;
    }
    callbacksRef.current.onSingleFingerSwipe(direction);
  };

  const registerThreeFingerTap = () => {
    const callbacks = callbacksRef.current;
    const now = Date.now();
    if (now - lastThreeFingerTapAtRef.current > THREE_FINGER_TAP_WINDOW_MS) {
      threeFingerTapCountRef.current = 0;
    }
    lastThreeFingerTapAtRef.current = now;
    threeFingerTapCountRef.current += 1;

    if (threeFingerTapCountRef.current >= 3 && callbacks.globalToggleEnabled !== false) {
      threeFingerTapCountRef.current = 0;
      clearPendingThreeFingerTapTimer();
      callbacks.onThreeFingerTripleTap();
      return;
    }

    if (!callbacks.enabled) {
      return;
    }

    clearPendingThreeFingerTapTimer();
    pendingThreeFingerTapTimerRef.current = setTimeout(() => {
      pendingThreeFingerTapTimerRef.current = null;
      if (threeFingerTapCountRef.current === 1) {
        threeFingerTapCountRef.current = 0;
        callbacksRef.current.onThreeFingerTap();
      }
    }, THREE_FINGER_TAP_WINDOW_MS);
  };

  const handleDirectTouchStart = (event: GestureResponderEvent) => {
    const point = getActiveTouchPoint(event);
    const multiTouchCount = normalizeMultiTouchCount(point?.count ?? 0);
    if (!point || multiTouchCount === 0) {
      return;
    }
    const current = directTouchTrackRef.current;
    if (!current) {
      directTouchTrackRef.current = beginMultiTouchTrack(multiTouchCount, point.x, point.y);
    } else if (multiTouchCount > current.gestureTouches) {
      resetMultiTouchTrack(current, multiTouchCount, point.x, point.y);
    } else {
      current.lastX = point.x;
      current.lastY = point.y;
    }
    if (touchTrackRef.current) {
      touchTrackRef.current.consumed = true;
    }
    suppressPanReleaseRef.current = true;
    clearHoldTimer();
  };

  const handleDirectTouchMove = (event: GestureResponderEvent) => {
    const current = directTouchTrackRef.current;
    if (!current) {
      return;
    }
    const point = getActiveTouchPoint(event);
    if (!point) {
      return;
    }
    const multiTouchCount = normalizeMultiTouchCount(point.count);
    if (multiTouchCount === 0) {
      return;
    }
    if (multiTouchCount > current.gestureTouches) {
      resetMultiTouchTrack(current, multiTouchCount, point.x, point.y);
      return;
    }
    current.lastX = point.x;
    current.lastY = point.y;
    if (Math.max(Math.abs(point.x - current.startX), Math.abs(point.y - current.startY)) > MOVE_TOLERANCE) {
      current.moved = true;
      clearHoldTimer();
    }
    if (!callbacksRef.current.enabled) {
      return;
    }
    if (current.consumed || multiTouchCount < current.gestureTouches) {
      return;
    }
    const dx = current.lastX - current.startX;
    const dy = current.lastY - current.startY;
    const direction = classifySwipeDelta(dx, dy);
    if (!direction) {
      return;
    }
    current.consumed = true;
    suppressPanReleaseRef.current = true;
    dispatchSwipe(direction, current.gestureTouches);
  };

  const handleDirectTouchEnd = (event: GestureResponderEvent) => {
    const current = directTouchTrackRef.current;
    if (!current) {
      return;
    }
    const activePoint = getActiveTouchPoint(event);
    const activeMultiTouchCount = normalizeMultiTouchCount(activePoint?.count ?? 0);
    if (activePoint && activeMultiTouchCount >= current.gestureTouches) {
      current.lastX = activePoint.x;
      current.lastY = activePoint.y;
    }
    if (getTouchArray(event, "touches").length > 0) {
      return;
    }
    directTouchTrackRef.current = null;
    suppressPanReleaseRef.current = true;
    clearHoldTimer();
    if (current.consumed) {
      return;
    }
    const direction = classifySwipeDelta(current.lastX - current.startX, current.lastY - current.startY);
    if (direction && callbacksRef.current.enabled) {
      dispatchSwipe(direction, current.gestureTouches);
      return;
    }
    if (current.gestureTouches >= 3) {
      registerThreeFingerTap();
      return;
    }
    if (!callbacksRef.current.enabled) {
      return;
    }
    const now = Date.now();
    const previous = lastMultiTouchDispatchRef.current;
    if (
      previous &&
      previous.key === `tap:${current.gestureTouches}` &&
      now - previous.at <= MULTI_TOUCH_REPEAT_WINDOW_MS
    ) {
      return;
    }
    lastMultiTouchDispatchRef.current = { at: now, key: `tap:${current.gestureTouches}` };
    callbacksRef.current.onTwoFingerTap();
  };

  const handleDirectTouchCancel = () => {
    if (directTouchTrackRef.current) {
      suppressPanReleaseRef.current = true;
    }
    directTouchTrackRef.current = null;
    clearHoldTimer();
  };

  const isTextInputTarget = (event: GestureResponderEvent): boolean => {
    return callbacksRef.current.isNativeTextInputTarget?.(event.nativeEvent.target) ?? false;
  };

  const shouldHandleStartGesture = (event: GestureResponderEvent): boolean => {
    const callbacks = callbacksRef.current;
    if (!callbacks.enabled) {
      return false;
    }
    if ((event.nativeEvent.touches.length || 1) !== 1) {
      return false;
    }
    return !isTextInputTarget(event);
  };

  const shouldHandleMoveGesture = (
    event: GestureResponderEvent,
    gestureState: PanResponderGestureState,
  ): boolean => {
    const callbacks = callbacksRef.current;
    if (!callbacks.enabled) {
      return false;
    }
    if ((event.nativeEvent.touches.length || gestureState.numberActiveTouches || 1) !== 1) {
      return false;
    }
    if (Math.max(Math.abs(gestureState.dx), Math.abs(gestureState.dy)) < SWIPE_THRESHOLD) {
      return false;
    }
    if (isTextInputTarget(event)) {
      return callbacks.isTextInputEditing?.() ?? false;
    }
    return true;
  };

  return useMemo(
    () => {
      const panResponder = PanResponder.create({
        onMoveShouldSetPanResponder: shouldHandleMoveGesture,
        onMoveShouldSetPanResponderCapture: shouldHandleMoveGesture,
        onPanResponderGrant: (event: GestureResponderEvent) => {
          const touches = event.nativeEvent.touches.length || 1;
          touchTrackRef.current = {
            consumed: false,
            maxTouches: touches,
            moved: false,
          };
          if (touches >= 2) {
            suppressPanReleaseRef.current = true;
          }
          if (touches === 1 && Date.now() - lastSingleTapAtRef.current <= DOUBLE_TAP_WINDOW_MS) {
            beginHoldDetection();
          } else {
            clearHoldTimer();
          }
        },
        onPanResponderMove: (event: GestureResponderEvent, gestureState: PanResponderGestureState) => {
          const track = touchTrackRef.current;
          if (!track) {
            return;
          }
          track.maxTouches = Math.max(track.maxTouches, event.nativeEvent.touches.length || track.maxTouches);
          if (track.maxTouches >= 2) {
            track.consumed = true;
            suppressPanReleaseRef.current = true;
            clearHoldTimer();
            return;
          }
          if (Math.max(Math.abs(gestureState.dx), Math.abs(gestureState.dy)) > MOVE_TOLERANCE) {
            track.moved = true;
            clearHoldTimer();
          }
          if (track.consumed) {
            return;
          }
          const direction = classifySwipe(gestureState);
          if (!direction) {
            return;
          }
          track.consumed = true;
          dispatchSwipe(direction, track.maxTouches);
        },
        onPanResponderRelease: (_event: GestureResponderEvent, gestureState: PanResponderGestureState) => {
          clearHoldTimer();
          const track = touchTrackRef.current;
          touchTrackRef.current = null;
          if (suppressPanReleaseRef.current) {
            suppressPanReleaseRef.current = false;
            return;
          }
          if (!track || track.consumed) {
            return;
          }

          const direction = classifySwipe(gestureState);
          if (direction) {
            dispatchSwipe(direction, track.maxTouches);
            return;
          }

          if (track.maxTouches >= 3) {
            return;
          }
          if (track.maxTouches === 2) {
            callbacksRef.current.onTwoFingerTap();
            return;
          }

          const now = Date.now();
          if (now - lastSingleTapAtRef.current <= DOUBLE_TAP_WINDOW_MS) {
            lastSingleTapAtRef.current = 0;
            callbacksRef.current.onDoubleTap();
            return;
          }
          lastSingleTapAtRef.current = now;
        },
        onPanResponderTerminate: () => {
          clearHoldTimer();
          touchTrackRef.current = null;
          suppressPanReleaseRef.current = false;
        },
        onStartShouldSetPanResponder: shouldHandleStartGesture,
        // Capture non-text controls while SV is active so visible Pressables do
        // not receive normal taps. TextInput starts must still pass through for
        // native keyboard activation.
        onStartShouldSetPanResponderCapture: shouldHandleStartGesture,
      });

      return {
        ...panResponder,
        panHandlers: {
          ...panResponder.panHandlers,
          onTouchCancel: handleDirectTouchCancel,
          onTouchEnd: handleDirectTouchEnd,
          onTouchMove: handleDirectTouchMove,
          onTouchStart: handleDirectTouchStart,
        },
      };
    },
    [],
  );
}
