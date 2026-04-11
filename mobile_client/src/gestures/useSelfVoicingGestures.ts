import { useEffect, useMemo, useRef } from "react";
import { PanResponder, type GestureResponderEvent, type PanResponderGestureState } from "react-native";

type SwipeDirection = "up" | "down" | "left" | "right";

type GestureCallbacks = {
  enabled: boolean;
  onDoubleTap: () => void;
  onDoubleTapHold: () => void;
  onSingleFingerSwipe: (direction: SwipeDirection) => void;
  onThreeFingerSwipe: (direction: SwipeDirection) => void;
  onThreeFingerTap: () => void;
  onTwoFingerSwipe: (direction: SwipeDirection) => void;
  onTwoFingerTap: () => void;
};

type TouchTrack = {
  consumed: boolean;
  maxTouches: number;
  moved: boolean;
};

const DOUBLE_TAP_WINDOW_MS = 350;
const DOUBLE_TAP_HOLD_MS = 350;
const MOVE_TOLERANCE = 8;
const SWIPE_THRESHOLD = 20;

export function useSelfVoicingGestures(callbacks: GestureCallbacks) {
  const callbacksRef = useRef(callbacks);
  const touchTrackRef = useRef<TouchTrack | null>(null);
  const lastSingleTapAtRef = useRef(0);
  const holdTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearHoldTimer = () => {
    if (holdTimerRef.current) {
      clearTimeout(holdTimerRef.current);
      holdTimerRef.current = null;
    }
  };

  useEffect(() => {
    callbacksRef.current = callbacks;
  }, [callbacks]);

  useEffect(() => clearHoldTimer, []);

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

  return useMemo(
    () =>
      PanResponder.create({
        onMoveShouldSetPanResponder: () => callbacksRef.current.enabled,
        onMoveShouldSetPanResponderCapture: () => callbacksRef.current.enabled,
        onPanResponderGrant: (event: GestureResponderEvent) => {
          const touches = event.nativeEvent.touches.length || 1;
          touchTrackRef.current = {
            consumed: false,
            maxTouches: touches,
            moved: false,
          };
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
        },
        onPanResponderRelease: (_event: GestureResponderEvent, gestureState: PanResponderGestureState) => {
          clearHoldTimer();
          const track = touchTrackRef.current;
          touchTrackRef.current = null;
          if (!track || track.consumed) {
            return;
          }

          const direction = classifySwipe(gestureState);
          if (direction) {
            if (track.maxTouches >= 3) {
              callbacksRef.current.onThreeFingerSwipe(direction);
            } else if (track.maxTouches >= 2) {
              callbacksRef.current.onTwoFingerSwipe(direction);
            } else {
              callbacksRef.current.onSingleFingerSwipe(direction);
            }
            return;
          }

          if (track.maxTouches >= 3) {
            callbacksRef.current.onThreeFingerTap();
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
        },
        onStartShouldSetPanResponder: () => callbacksRef.current.enabled,
        onStartShouldSetPanResponderCapture: () => callbacksRef.current.enabled,
      }),
    [],
  );
}
