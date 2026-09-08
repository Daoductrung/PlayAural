import { SafeAreaProvider, initialWindowMetrics } from "react-native-safe-area-context";
import { PlayAuralApp } from "./src/app/PlayAuralApp";

export default function App() {
  return (
    <SafeAreaProvider initialMetrics={initialWindowMetrics}>
      <PlayAuralApp />
    </SafeAreaProvider>
  );
}
