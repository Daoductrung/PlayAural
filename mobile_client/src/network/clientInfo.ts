import { Platform } from "react-native";

export type ClientAuthMetadata = {
  client: "mobile";
  platform?: string;
  release_platform: ClientReleasePlatform;
};

export type ClientReleasePlatform = "android" | "ios" | "web" | "unknown";

const ANDROID_API_VERSION_NAMES: Record<number, string> = {
  23: "6.0",
  24: "7.0",
  25: "7.1",
  26: "8.0",
  27: "8.1",
  28: "9",
  29: "10",
  30: "11",
  31: "12",
  32: "12L",
  33: "13",
  34: "14",
  35: "15",
  36: "16",
};

function cleanPart(value: unknown): string {
  if (typeof value !== "string" && typeof value !== "number") {
    return "";
  }
  return String(value).replace(/\s+/g, " ").trim();
}

function platformConstants(): Record<string, unknown> {
  return (Platform.constants ?? {}) as Record<string, unknown>;
}

function androidApiLevel(): number | null {
  const value = Platform.Version;
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function androidReleaseLabel(): string {
  const constants = platformConstants();
  const release = cleanPart(constants.Release ?? constants.release);
  const api = androidApiLevel();
  const versionName = release || (api !== null ? ANDROID_API_VERSION_NAMES[api] || "" : "");
  const apiLabel = api !== null ? `API ${api}` : "";

  if (versionName && apiLabel) {
    return `Android ${versionName} (${apiLabel})`;
  }
  if (versionName) {
    return `Android ${versionName}`;
  }
  if (apiLabel) {
    return `Android (${apiLabel})`;
  }
  return "Android";
}

function nativePlatformLabel(): string {
  if (Platform.OS === "android") {
    return androidReleaseLabel();
  }
  if (Platform.OS === "ios") {
    const version = cleanPart(Platform.Version);
    return version ? `iOS ${version}` : "iOS";
  }
  if (Platform.OS === "web") {
    return "Web";
  }
  const os = cleanPart(Platform.OS);
  const version = cleanPart(Platform.Version);
  return [os || "Unknown OS", version].filter(Boolean).join(" ");
}

export function getClientPlatformLabel(): string {
  return nativePlatformLabel().slice(0, 60);
}

export function getClientReleasePlatform(): ClientReleasePlatform {
  if (Platform.OS === "android" || Platform.OS === "ios" || Platform.OS === "web") {
    return Platform.OS;
  }
  return "unknown";
}

export function clientAuthMetadata(): ClientAuthMetadata {
  const platform = getClientPlatformLabel();
  return {
    client: "mobile",
    release_platform: getClientReleasePlatform(),
    ...(platform ? { platform } : {}),
  };
}
