import type { ReactNode } from "react";
import { Platform, ScrollView, StyleSheet, requireNativeComponent, type ViewProps, type ViewStyle } from "react-native";
import { useFocusScroll } from "./useFocusScroll";

type NativeBoardProps = ViewProps & { panningEnabled: boolean; focusTarget: string | null };
const NativeBoardViewport = Platform.OS === "android"
  ? requireNativeComponent<NativeBoardProps>("PlayAuralBoardViewport") : null;

type Props = {
  children: ReactNode;
  contentWidth: number;
  focusKey: string | null;
  nodes: { current: Map<string, unknown> };
};

export function BoardViewport({ children, contentWidth, focusKey, nodes }: Props) {
  // Android resolves the latest semantic target in native layout. No round trip
  // through JS measurement, scroll events, or animation completion gates speech.
  const scroll = useFocusScroll(NativeBoardViewport ? null : focusKey, nodes, "both");
  if (NativeBoardViewport) {
    return (
      <NativeBoardViewport panningEnabled={focusKey === null} focusTarget={focusKey} style={styles.viewport}>
        {children}
      </NativeBoardViewport>
    );
  }
  return (
    <ScrollView
      {...scroll}
      directionalLockEnabled={false}
      contentContainerStyle={{ width: contentWidth }}
      style={[styles.viewport, Platform.OS === "web" ? styles.webPanning : undefined]}
    >
      {children}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  // Yoga must measure scroll content beyond the viewport. A regular clipped
  // View can otherwise cap the reported content size when cell labels reflow.
  viewport: { flex: 1, overflow: "scroll" },
  webPanning: { overflowX: "auto", overflowY: "auto" } as ViewStyle,
});
