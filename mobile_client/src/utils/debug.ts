export const ENABLE_CLIENT_DEBUG_LOGS =
  (typeof __DEV__ !== "undefined" && __DEV__) ||
  (typeof process !== "undefined" && process.env?.NODE_ENV !== "production");
