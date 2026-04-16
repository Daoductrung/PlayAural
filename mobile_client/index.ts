import { registerRootComponent } from "expo";
import { Platform } from "react-native";

import App from "./App";

if (Platform.OS !== "web") {
  const { registerGlobals } = require("@livekit/react-native") as typeof import("@livekit/react-native");
  registerGlobals();
}

registerRootComponent(App);
