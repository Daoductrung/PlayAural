import { useCallback, useLayoutEffect, useRef } from "react";
import { Platform, ScrollView, type NativeScrollEvent, type NativeSyntheticEvent } from "react-native";

type MeasurableNode = {
  measureInWindow?: (callback: (x: number, y: number, width: number, height: number) => void) => void;
  scrollIntoView?: (options: { block: "nearest"; inline: "nearest" }) => void;
};

// Scroll only enough to reveal focus. Oversized controls start at their top;
// passive repaints and native touch scrolling otherwise retain their position.
export function focusScrollOffset(offset: number, top: number, height: number, viewportTop: number, viewportHeight: number): number {
  if (viewportHeight <= 0 || height <= 0) return offset;
  if (top < viewportTop || height > viewportHeight) return Math.max(0, offset + top - viewportTop);
  return Math.max(0, offset + Math.max(0, top + height - viewportTop - viewportHeight));
}

export function useFocusScroll(focusKey: string | null, nodes: { current: Map<string, unknown> }, horizontal: boolean | "both" = false) {
  const ref = useRef<ScrollView | null>(null);
  const offset = useRef({ x: 0, y: 0 });
  const revision = useRef(0);
  const frame = useRef<ReturnType<typeof requestAnimationFrame> | null>(null);
  const revealFocus = useCallback(() => {
    const request = ++revision.current;
    if (frame.current !== null) cancelAnimationFrame(frame.current);
    frame.current = requestAnimationFrame(() => {
      frame.current = null;
      const scroll = ref.current;
      const node = focusKey ? nodes.current.get(focusKey) as MeasurableNode | undefined : undefined;
      if (!scroll || !node) return;
      const isCurrent = () => request === revision.current && ref.current === scroll && nodes.current.get(focusKey!) === node;
      if (Platform.OS === "web") {
        node.scrollIntoView?.({ block: "nearest", inline: "nearest" });
        return;
      }
      scroll.getNativeScrollRef()?.measureInWindow((viewportLeft, viewportTop, viewportWidth, viewportHeight) => {
        if (!isCurrent()) return;
        node.measureInWindow?.((left, top, width, height) => {
          if (!isCurrent()) return;
          const x = horizontal !== false
            ? focusScrollOffset(offset.current.x, left, width, viewportLeft, viewportWidth) : offset.current.x;
          const y = horizontal !== true
            ? focusScrollOffset(offset.current.y, top, height, viewportTop, viewportHeight) : offset.current.y;
          if (x !== offset.current.x || y !== offset.current.y) {
            offset.current = { x, y };
            scroll.scrollTo({ ...(horizontal !== false ? { x } : {}), ...(horizontal !== true ? { y } : {}), animated: false });
          }
        });
      });
    });
  }, [focusKey, horizontal, nodes]);

  useLayoutEffect(() => {
    revealFocus();
    return () => {
      revision.current += 1;
      if (frame.current !== null) cancelAnimationFrame(frame.current);
    };
  }, [revealFocus]);

  const attachScroll = useCallback((node: ScrollView | null) => {
    if (ref.current !== node) offset.current = { x: 0, y: 0 };
    ref.current = node;
  }, []);

  return {
    ref: attachScroll,
    // Self-voicing owns the drag stream while it has a focus target. Native
    // dragging must not compete with it; scrollTo still reveals focus.
    scrollEnabled: focusKey === null,
    onLayout: revealFocus,
    onContentSizeChange: revealFocus,
    onScroll: (event: NativeSyntheticEvent<NativeScrollEvent>) => {
      offset.current = { ...event.nativeEvent.contentOffset };
    },
    scrollEventThrottle: 16,
    keyboardShouldPersistTaps: "handled" as const,
  };
}
