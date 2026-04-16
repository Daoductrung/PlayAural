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

type DirectTouchTrack = {
  consumed: boolean;
  endX: number;
  endY: number;
  maxTouches: number;
  moved: boolean;
  startX: number;
  startY: number;
};

const DOUBLE_TAP_WINDOW_MS = 350;
const DOUBLE_TAP_HOLD_MS = 350;
const THREE_FINGER_TAP_WINDOW_MS = 650;
const MOVE_TOLERANCE = 4;
const SWIPE_THRESHOLD = 14;

export function useSelfVoicingGestures(callbacks: GestureCallbacks) {
  const callbacksRef = useRef(callbacks);
  const touchTrackRef = useRef<TouchTrack | null>(null);
  const directTouchTrackRef = useRef<DirectTouchTrack | null>(null);
  const lastSingleTapAtRef = useRef(0);
  const lastThreeFingerTapAtRef = useRef(0);
  const threeFingerTapCountRef = useRef(0);
  const holdTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingThreeFingerTapTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const suppressPanReleaseRef = useRef(false);

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

  const getTouchPoint = (event: GestureResponderEvent): { x: number; y: number } => {
    const nativeEvent = event.nativeEvent as GestureResponderEvent["nativeEvent"] & {
      pageX?: number;
      pageY?: number;
    };
    return {
      x: nativeEvent.pageX ?? nativeEvent.locationX ?? 0,
      y: nativeEvent.pageY ?? nativeEvent.locationY ?? 0,
    };
  };

  const classifySwipe = (gestureState: PanResponderGestureState): SwipeDirection | null => {
    return classifySwipeDelta(gestureState.dx, gestureState.dy);
  };

  const classifySwipeDelta = (dx: number, dy: number): SwipeDirection | null => {
    if (Math.max(Math.abs(dx), Math.abs(dy)) < SWIPE_THRESHOLD) {
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
    const touches = event.nativeEvent.touches.length || 1;
    const point = getTouchPoint(event);
    const current = directTouchTrackRef.current;
    if (!current) {
      directTouchTrackRef.current = {
        consumed: false,
        endX: point.x,
        endY: point.y,
        maxTouches: touches,
        moved: false,
        startX: point.x,
        startY: point.y,
      };
    } else {
      current.endX = point.x;
      current.endY = point.y;
      current.maxTouches = Math.max(current.maxTouches, touches);
    }
    if (touches >= 2) {
      suppressPanReleaseRef.current = true;
      clearHoldTimer();
    }
  };

  const handleDirectTouchMove = (event: GestureResponderEvent) => {
    const current = directTouchTrackRef.current;
    if (!current) {
      return;
    }
    current.maxTouches = Math.max(current.maxTouches, event.nativeEvent.touches.length || current.maxTouches);
    const point = getTouchPoint(event);
    current.endX = point.x;
    current.endY = point.y;
    if (Math.max(Math.abs(point.x - current.startX), Math.abs(point.y - current.startY)) > MOVE_TOLERANCE) {
      current.moved = true;
      clearHoldTimer();
    }
    if (!callbacksRef.current.enabled) {
      return;
    }
    if (current.consumed || current.maxTouches < 2) {
      return;
    }
    const direction = classifySwipeDelta(current.endX - current.startX, current.endY - current.startY);
    if (!direction) {
      return;
    }
    current.consumed = true;
    suppressPanReleaseRef.current = true;
    dispatchSwipe(direction, current.maxTouches);
  };

  const handleDirectTouchEnd = (event: GestureResponderEvent) => {
    const current = directTouchTrackRef.current;
    if (!current) {
      return;
    }
    const point = getTouchPoint(event);
    current.endX = point.x;
    current.endY = point.y;
    if (event.nativeEvent.touches.length > 0) {
      return;
    }
    directTouchTrackRef.current = null;
    if (current.maxTouches < 2) {
      suppressPanReleaseRef.current = false;
      return;
    }
    suppressPanReleaseRef.current = true;
    clearHoldTimer();
    if (current.consumed) {
      return;
    }
    const direction = classifySwipeDelta(current.endX - current.startX, current.endY - current.startY);
    if (direction && callbacksRef.current.enabled) {
      dispatchSwipe(direction, current.maxTouches);
      return;
    }
    if (current.maxTouches >= 3) {
      registerThreeFingerTap();
      return;
    }
    if (!callbacksRef.current.enabled) {
      return;
    }
    callbacksRef.current.onTwoFingerTap();
  };

  const handleDirectTouchCancel = () => {
    if (directTouchTrackRef.current?.maxTouches && directTouchTrackRef.current.maxTouches >= 2) {
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
