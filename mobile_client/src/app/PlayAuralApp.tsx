import { StatusBar } from "expo-status-bar";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Audio as ExpoAudio } from "expo-av";
import * as SecureStore from "expo-secure-store";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ComponentProps,
  type ComponentType,
  type MutableRefObject,
  type SetStateAction,
} from "react";
import {
  AccessibilityInfo,
  AppState,
  BackHandler,
  Keyboard,
  KeyboardAvoidingView,
  Linking,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  findNodeHandle,
  useWindowDimensions,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { MobileAudioManager } from "../audio/MobileAudioManager";
import { requestAndroidBatteryOptimizationExemptionOnce } from "../background/AndroidBatteryOptimization";
import { androidForegroundService } from "../background/AndroidForegroundService";
import { useSelfVoicingGestures } from "../gestures/useSelfVoicingGestures";
import { bundledSoundVersion } from "../generated/soundManifest";
import { MobileLocalization, resolveMobileLocale, type MobileLocale } from "../i18n/localization";
import { PlayAuralConnection } from "../network/PlayAuralConnection";
import {
  clientAuthMetadata,
  getClientReleasePlatform,
} from "../network/clientInfo";
import { resolveMenuFocusIndex } from "./menuFocus";
import { useFocusScroll } from "./useFocusScroll";
import { useAnchoredFocus } from "./useAnchoredFocus";
import { gridCellSizeForViewport } from "./gridLayout";
import { BoardViewport } from "./BoardViewport";
import type {
  AuthorizeSuccessPacket,
  AudioCommandPacket,
  ChatPacket,
  DisconnectPacket,
  ForceExitPacket,
  LoginFailedPacket,
  MenuItemData,
  MenuPacket,
  MenuSelectionPacket,
  RegisterResponsePacket,
  RemoveEditboxPacket,
  RemoveMenuPacket,
  RequestInputPacket,
  RequestPasswordResetResponsePacket,
  ServerPacket,
  SpeakPacket,
  SubmitResetCodeResponsePacket,
  TableContextPacket,
  UpdateLocalePacket,
  UpdatePreferencePacket,
  VoiceContextClosedPacket,
  VoiceJoinErrorPacket,
  VoiceJoinInfoPacket,
  VoiceLeaveAckPacket,
} from "../network/packets";
import {
  BUFFER_NAMES,
  BufferStore,
  normalizeBufferName,
  type BufferName,
} from "../state/BufferStore";
import { TtsManager, type TtsVoiceOption } from "../tts/TtsManager";
import { observeSpeechEnvironment } from "../tts/observeSpeechEnvironment";
import { ENABLE_CLIENT_DEBUG_LOGS } from "../utils/debug";
import { MobileVoiceManager, type MobileVoiceConnectionState } from "../voice/MobileVoiceManager";

const MOBILE_CLIENT_VERSION = "1.0.4.16";
const MOBILE_BUILD_STAMP = "2026-08-27 17:14:09 +07:00";
const DEFAULT_SERVER_URL = "wss://playaural.ddt.one:443";
const CLIENT_CONFIG_STORAGE_KEY = "playaural.mobile.clientConfig";
const CLIENT_PASSWORD_STORAGE_KEY = "playaural.mobile.password";
const CLIENT_SV_STORAGE_KEY = "playaural.mobile.selfVoicing";
const CLIENT_MIC_PERMISSION_REQUESTED_STORAGE_KEY = "playaural.mobile.voiceMicPermissionRequested";
const WEB_SCREEN_READER_SUPPORT = Platform.OS === "web";
const NATIVE_FOCUS_DELAY_MS = 80;
const NATIVE_FOCUS_MAX_ATTEMPTS = 8;
const NATIVE_MENU_FOCUS_REQUEST_TTL_MS = 3000;
const NATIVE_FOCUS_RESET_GUARD_MS = 900;
const CONNECTION_AUDIO_ASSET = "connectloop.ogg";
const CONNECTION_AUDIO_HANDLE = "client:connection";
const CONNECTION_AUDIO_LAYER = "connection";

type ReleaseDownloadInfo = {
  target?: string;
  url?: string;
};

function releaseDownloadUrl(info: ReleaseDownloadInfo | undefined): string {
  const expectedTarget = getClientReleasePlatform();
  const target = String(info?.target || "").trim().toLowerCase();
  const url = String(info?.url || "").trim();

  if (
    target === expectedTarget
    && /^https:\/\/\S+$/i.test(url)
  ) {
    return url;
  }

  // Untargeted legacy metadata may contain a desktop archive, so it must not
  // be opened by a mobile client.
  return "";
}

type ServerAuthResponseContext = "login" | "password_reset" | "register" | "reset_code";

const SERVER_AUTH_RESPONSE_KEYS: Record<ServerAuthResponseContext, Record<string, string>> = {
  login: {
    captcha_failed: "error-captcha-failed",
    captcha_missing: "error-captcha-failed",
    rate_limit: "auth-error-rate-limit",
    user_not_found: "auth-error-user-not-found",
    username_ambiguous: "auth-error-username-ambiguous",
    version_mismatch: "auth-error-version-mismatch",
    wrong_password: "auth-error-wrong-password",
  },
  password_reset: {
    captcha_failed: "error-captcha-failed",
    captcha_missing: "error-captcha-failed",
    email_empty: "error-email-empty",
    rate_limit: "error-rate-limit-login",
    smtp_error: "error-smtp-send-failed",
    smtp_not_configured: "error-smtp-not-configured",
  },
  register: {
    captcha_failed: "error-captcha-failed",
    captcha_missing: "error-captcha-failed",
    email_empty: "error-email-empty",
    email_invalid: "error-email-invalid",
    email_taken: "error-email-taken",
    password_weak: "auth-error-password-weak",
    rate_limit: "error-rate-limit-register",
    server_error: "auth-registration-error",
    username_invalid_chars: "auth-error-username-invalid-chars",
    username_length: "auth-error-username-length",
    username_reserved_bot: "auth-username-reserved-bot",
    username_taken: "auth-username-taken",
  },
  reset_code: {
    captcha_failed: "error-captcha-failed",
    captcha_missing: "error-captcha-failed",
    invalid_code: "error-invalid-reset-code",
    missing_fields: "auth-username-password-required",
    password_weak: "auth-error-password-weak",
    rate_limit: "error-rate-limit-login",
    user_not_found: "error-invalid-reset-code",
  },
};

type AppMode = "chat" | "history" | "main" | "shortcuts";
type AuthMode = "forgot" | "login" | "register" | "reset";

type ScreenReaderAnnouncement = {
  id: number;
  text: string;
};

type AccessibilityFocusNode = Parameters<typeof findNodeHandle>[0] | { focus?: () => void };
type AccessibilityOrderedViewProps = ComponentProps<typeof View> & {
  experimental_accessibilityOrder?: string[];
};

const AccessibilityOrderedView = View as ComponentType<AccessibilityOrderedViewProps>;

type FocusableMenuItem = {
  id?: string;
  selectionValue?: string | null;
  text: string;
  sound?: string;
};

type MenuState = {
  escapeBehavior: string;
  focusIndex: number;
  gridEnabled: boolean;
  gridHeight: number;
  gridWidth: number;
  items: FocusableMenuItem[];
  menuId: string;
};

type InputState = {
  defaultValue: string;
  inputId: string;
  maxLength?: number;
  multiline: boolean;
  prompt: string;
  readOnly: boolean;
};

type InputOverlayFocus = 0 | 1;
type DialogFocusIndex = number;

type ChatFocusItem = {
  id: string;
  kind: "close" | "input" | "message" | "send" | "voiceJoin" | "voiceLeave" | "voiceMic";
  text: string;
};

type HistoryFocusItem = {
  id: string;
  kind: "buffer" | "empty" | "message" | "mute";
  text: string;
};

type VoiceCapability = {
  enabled: boolean;
  provider: string;
  tokenTtlSeconds: number;
  url: string;
};

type VoiceContextState = {
  contextId: string;
  scope: "table";
};

type DialogAction = {
  id: string;
  checked?: boolean;
  text: string;
  variant?: "danger" | "primary" | "secondary";
  onPress: () => void;
};

type DialogState = {
  buttons: DialogAction[];
  focusIndex: DialogFocusIndex;
  id: string;
  message: string;
  title: string;
  returnFocusKey?: string;
};

type ShortcutActionId =
  | "ambience_down"
  | "ambience_up"
  | "friends"
  | "help"
  | "list_online"
  | "list_online_with_games"
  | "music_down"
  | "music_up"
  | "options"
  | "ping";

type ShortcutItem = {
  id: ShortcutActionId;
  text: string;
};

type AuthFocusableItem = {
  action:
    | "clear_saved_account"
    | "connect"
    | "exit_app"
    | "focus_forgot_email"
    | "focus_password"
    | "focus_register_confirm_password"
    | "focus_register_email"
    | "focus_reset_code"
    | "focus_reset_confirm_password"
    | "focus_reset_email"
    | "focus_reset_password"
    | "focus_username"
    | "submit_forgot"
    | "submit_register"
    | "submit_reset"
    | "switch_forgot"
    | "switch_login"
    | "switch_register"
    | "open_locale"
    | "help";
  id: string;
  text: string;
};

type StoredClientConfig = {
  appLocale: MobileLocale;
  preferences: Record<string, unknown>;
  registerEmail: string;
  serverUrl: string;
  username: string;
};

const defaultMenuState: MenuState = {
  escapeBehavior: "keybind",
  focusIndex: 0,
  gridEnabled: false,
  gridHeight: 0,
  gridWidth: 1,
  items: [],
  menuId: "",
};

const PROTECTED_TRANSIENT_MENU_IDS = new Set(["action_input_menu", "actions_menu", "status_box"]);

function isProtectedTransientMenu(menuId: string | undefined): boolean {
  return menuId !== undefined && PROTECTED_TRANSIENT_MENU_IDS.has(menuId);
}

function shouldAutoFocusUnsolicitedMenu(menuId: string, previousMenuId: string): boolean {
  if (!previousMenuId) {
    return true;
  }
  if (menuId === previousMenuId) {
    return false;
  }
  return menuId !== "turn_menu";
}

function menuItemAccessibilityKey(menuId: string, item: { id?: string } | undefined, index: number): string {
  const identity = item?.id !== undefined && item.id !== null
    ? `id:${String(item.id)}`
    : `text:${index}:${String((item as { text?: string } | undefined)?.text ?? "")}`;
  return `menu:${menuId}:${identity}`;
}

function detectPreferredLocale(): MobileLocale {
  const deviceLocale = Intl.DateTimeFormat().resolvedOptions().locale?.toLowerCase?.() ?? "en";
  return resolveMobileLocale(deviceLocale);
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function normalizeMenuItems(items: Array<string | MenuItemData>): FocusableMenuItem[] {
  return items.map((item) => {
    if (typeof item === "string") {
      return { text: item };
    }
    return {
      id: item.id,
      selectionValue: item.selection_value ?? null,
      sound: item.sound,
      text: item.text,
    };
  });
}

function getDefaultAuthFocusId(mode: AuthMode): string {
  if (mode === "forgot") {
    return "field-forgot-email";
  }
  if (mode === "reset") {
    return "field-reset-email";
  }
  return "field-username";
}

function formatChatMessage(localization: MobileLocalization, packet: ChatPacket): string {
  const sender = packet.sender?.trim() || localization.t("chat-unknown-sender");
  const message = packet.message || "";
  if (packet.convo === "global") {
    return localization.t("chat-global", { message, player: sender });
  }
  if (packet.convo === "announcement") {
    return localization.t("chat-announcement", { message });
  }
  if (packet.convo === "private" || packet.convo === "pm") {
    return localization.t("chat-private", { message, player: sender });
  }
  return localization.t("chat-local", { message, player: sender });
}

function nextLinearIndex(current: number, length: number, direction: "up" | "down"): number {
  if (length <= 0) {
    return 0;
  }
  if (direction === "up") {
    return Math.max(0, current - 1);
  }
  return Math.min(length - 1, current + 1);
}

function nextGridIndex(
  current: number,
  length: number,
  width: number,
  direction: "up" | "down" | "left" | "right",
): number {
  if (length <= 0) {
    return 0;
  }
  const safeWidth = Math.max(1, width);
  const currentRow = Math.floor(current / safeWidth);
  const currentColumn = current % safeWidth;
  if (direction === "left") {
    return currentColumn === 0 ? current : current - 1;
  }
  if (direction === "right") {
    const nextIndex = current + 1;
    if (nextIndex >= length || Math.floor(nextIndex / safeWidth) !== currentRow) {
      return current;
    }
    return nextIndex;
  }
  if (direction === "up") {
    return Math.max(0, current - safeWidth);
  }
  return Math.min(length - 1, current + safeWidth);
}

function serverSpeechRateToExpoRate(value: unknown): number {
  const numeric = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(numeric)) {
    return 1;
  }
  const clamped = clamp(numeric, 50, 200);
  if (clamped <= 100) {
    return clamped / 100;
  }
  return Math.pow(10, (clamped - 100) / 100);
}

function compactVoiceIdentifier(identifier: string): string {
  const trimmed = identifier.trim();
  if (!trimmed) {
    return "";
  }
  const segments = trimmed.split(/[:./]/).filter(Boolean);
  return segments[segments.length - 1] || trimmed;
}

function localizeVoiceQuality(localization: MobileLocalization, quality: string | undefined): string {
  const normalized = String(quality || "").trim().toLowerCase();
  if (normalized === "enhanced") {
    return localization.t("mobile-tts-quality-enhanced");
  }
  if (normalized === "default") {
    return localization.t("mobile-tts-quality-default");
  }
  return String(quality || "").trim();
}

function formatMobileVoiceLabel(
  voice: TtsVoiceOption,
  localization: MobileLocalization,
): string {
  const name = voice.label || voice.language || voice.id;
  const parts = [name];
  const language = voice.language.trim();
  if (language) {
    parts.push(language);
  }
  const quality = localizeVoiceQuality(localization, voice.quality);
  if (quality) {
    parts.push(quality);
  }
  if (voice.isDefault) {
    parts.push(localization.t("mobile-tts-system-default"));
  }
  const compactIdentifier = compactVoiceIdentifier(voice.id);
  if (
    compactIdentifier &&
    compactIdentifier !== name &&
    compactIdentifier !== language &&
    !name.includes(compactIdentifier)
  ) {
    parts.push(compactIdentifier);
  }
  return parts.join(", ");
}

function normalizePreferenceKey(key: string): string {
  const normalizedBySyncKey: Record<string, string> = {
    "mobile/tts_engine": "mobile_tts_engine",
    "mobile/tts_rate": "mobile_tts_rate",
    "mobile/tts_voice": "mobile_tts_voice",
  };
  const keyParts = key.split("/");
  return normalizedBySyncKey[key] ?? keyParts[keyParts.length - 1];
}

function formatTextInputSpeech(
  localization: Pick<MobileLocalization, "t">,
  label: string,
  value: string,
  options?: { readOnly?: boolean; secure?: boolean },
): string {
  const trimmedValue = value.trim();
  if (options?.secure) {
    return value.length === 0
      ? localization.t("text-input-secure-empty", { label })
      : localization.t("text-input-secure-count", { count: value.length, label });
  }
  if (trimmedValue.length === 0) {
    return localization.t(options?.readOnly ? "text-input-readonly-empty" : "text-input-empty", { label });
  }
  return localization.t(options?.readOnly ? "text-input-readonly-value" : "text-input-value", {
    label,
    value,
  });
}

function extractPreferenceUpdates(packet: UpdatePreferencePacket | AuthorizeSuccessPacket): Record<string, unknown> {
  if ("preferences" in packet && packet.preferences) {
    return packet.preferences;
  }
  if ("key" in packet && packet.key) {
    return { [normalizePreferenceKey(packet.key)]: packet.value };
  }
  return {};
}

function toLocalizationParams(params: Record<string, unknown> | undefined): Record<string, string | number> {
  const normalized: Record<string, string | number> = {};
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (typeof value === "string" || typeof value === "number") {
      normalized[key] = value;
    } else if (typeof value === "boolean") {
      normalized[key] = value ? "true" : "false";
    }
  });
  return normalized;
}

export function PlayAuralApp() {
  const initialLocale = useMemo<MobileLocale>(() => detectPreferredLocale(), []);
  const localization = useMemo(() => {
    const instance = new MobileLocalization();
    instance.setLocale(initialLocale);
    return instance;
  }, [initialLocale]);
  const buffers = useMemo(() => new BufferStore(), []);
  const tts = useMemo(() => {
    const instance = new TtsManager();
    instance.setUiEnabled(false);
    instance.setLanguage(initialLocale);
    return instance;
  }, [initialLocale]);
  const audio = useMemo(() => new MobileAudioManager(), []);
  const voice = useMemo(() => new MobileVoiceManager(), []);

  const [appLocale, setAppLocale] = useState<MobileLocale>(initialLocale);
  const [mode, setMode] = useState<AppMode>("main");
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [menuState, setMenuState] = useState<MenuState>(defaultMenuState);
  const [inputState, setInputState] = useState<InputState | null>(null);
  const [dialogState, setDialogValue] = useState<DialogState | null>(null);
  const dialogStateRef = useRef(dialogState);
  const setDialogState = useCallback((update: SetStateAction<DialogState | null>) => {
    const nextState = typeof update === "function" ? update(dialogStateRef.current) : update;
    dialogStateRef.current = nextState;
    setDialogValue(nextState);
  }, []);
  const [inputValue, setInputValue] = useState("");
  const [inputOverlayFocus, setInputOverlayFocus] = useState<InputOverlayFocus>(0);
  const [appState, setAppState] = useState(AppState.currentState);
  const [chatDraft, setChatDraft] = useState("");
  const [statusText, setStatusText] = useState(() => localization.t("status-disconnected"));
  const [authStatusText, setAuthStatusText] = useState("");
  const [historyRevision, setHistoryRevision] = useState(0);
  const [historyBuffer, setHistoryBuffer] = useState<BufferName>("all");
  const [serverUrl, setServerUrl] = useState(DEFAULT_SERVER_URL);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerConfirmPassword, setRegisterConfirmPassword] = useState("");
  const [forgotEmail, setForgotEmail] = useState("");
  const [resetEmail, setResetEmail] = useState("");
  const [resetCode, setResetCode] = useState("");
  const [resetPassword, setResetPassword] = useState("");
  const [resetConfirmPassword, setResetConfirmPassword] = useState("");
  const [audioRevision, setAudioRevision] = useState(0);
  const [connected, setConnected] = useState(false);
  const [storageReady, setStorageReady] = useState(false);
  const [lastPingStartedAt, setLastPingStartedAt] = useState<number | null>(null);
  const [shortcutFocusIndex, setShortcutFocusIndex] = useState(0);
  const [authFocusIndex, setAuthFocusIndex] = useState(0);
  const [preferences, setPreferences] = useState<Record<string, unknown>>({});
  const [selfVoicingEnabled, setSelfVoicingEnabled] = useState(true);
  const selfVoicingEnabledRef = useRef(true);
  const [screenReaderEnabled, setScreenReaderEnabled] = useState(WEB_SCREEN_READER_SUPPORT);
  const [activeTextInputKey, setActiveTextInputKey] = useState<string | null>(null);
  const [screenReaderAnnouncement, setScreenReaderAnnouncement] = useState<ScreenReaderAnnouncement>({
    id: 0,
    text: "",
  });
  const [mainPanelLayout, setMainPanelLayout] = useState({ height: 0, width: 0 });
  const [voiceCapability, setVoiceCapability] = useState<VoiceCapability>({
    enabled: false,
    provider: "",
    tokenTtlSeconds: 0,
    url: "",
  });
  const [voiceContext, setVoiceContext] = useState<VoiceContextState>({
    contextId: "",
    scope: "table",
  });
  const [voiceRequestedContextId, setVoiceRequestedContextId] = useState("");
  const [voiceStatusText, setVoiceStatusText] = useState(() => localization.t("voice-chat-not-connected"));
  const [voiceState, setVoiceState] = useState<MobileVoiceConnectionState>("disconnected");
  const [voiceMicEnabled, setVoiceMicEnabled] = useState(false);
  const [voiceMicBusy, setVoiceMicBusy] = useState(false);
  const currentMusic = useMemo(
    () => audio.getActiveLayerAssets("music").join(", "),
    [audio, audioRevision],
  );
  const currentAmbience = useMemo(
    () => audio.getActiveLayerAssets("ambience").join(", "),
    [audio, audioRevision],
  );

  const menuStateRef = useRef(menuState);
  const inputStateRef = useRef(inputState);
  const handleSystemSwipeRef = useRef<((direction: "up" | "down" | "left" | "right") => void) | null>(null);
  const lastPingStartedAtRef = useRef<number | null>(lastPingStartedAt);
  const preferencesRef = useRef<Record<string, unknown>>(preferences);
  const voiceMicBusyRef = useRef(false);
  const voiceContextRef = useRef<VoiceContextState>({
    contextId: "",
    scope: "table",
  });
  const voiceRequestedContextIdRef = useRef("");
  const voiceStateRef = useRef<MobileVoiceConnectionState>("disconnected");
  const modeRef = useRef(mode);
  const voiceJoinPendingRef = useRef(false);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectWindowStartedAtRef = useRef<number | null>(null);
  const reconnectDelayMsRef = useRef(1000);
  const reconnectAttemptsRef = useRef(0);
  const connectionAudioActiveRef = useRef(false);
  const manualDisconnectRef = useRef(false);
  const allowReconnectRef = useRef(false);
  const expectingReconnectRef = useRef(false);
  const sessionEstablishedRef = useRef(false);
  const appStateRef = useRef(appState);
  const lastPassiveUiSignatureRef = useRef<string | null>(null);
  const authModeInitializedRef = useRef(false);
  const previousAuthModeRef = useRef<AuthMode | null>(null);
  const nativeFocusTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const nativeTabTextInputFocusTimersRef = useRef(new Set<ReturnType<typeof setTimeout>>());
  const lastNativeFocusKeyRef = useRef<string | null>(null);
  const pendingNativeAccessibilityFocusKeyRef = useRef<string | null>(null);
  const pendingNativeAccessibilityFocusQueuedAtRef = useRef(0);
  const nativeFocusTargetKeyRef = useRef<string | null>(null);
  const nativeFocusTargetQueuedAtRef = useRef(0);
  const nativeFocusTargetReleaseTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const nativeScreenReaderModeRef = useRef(false);
  const nativeMenuFocusOnNextPacketRef = useRef(false);
  const nativeMenuFocusRequestedAtRef = useRef(0);
  const programmaticNativeFocusKeyRef = useRef<string | null>(null);
  const programmaticNativeFocusTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const activeTextInputKeyRef = useRef<string | null>(activeTextInputKey);
  const longPressConsumedRef = useRef<string | null>(null);
  const longPressResetTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mobileVoiceMenuGenerationRef = useRef(0);
  const voicePresenceRegisteredRef = useRef(false);
  const transientTurnMenuAllowanceRef = useRef<string | null>(null);
  const accessibilityNodeRefs = useRef(new Map<string, AccessibilityFocusNode>());
  const textInputTargetByKeyRef = useRef(new Map<string, Set<unknown>>());
  const textInputTargetsRef = useRef(new Set<unknown>());
  const credentialsRef = useRef({
    password,
    serverUrl,
    username,
  });
  const updatePromptShownRef = useRef(false);
  const autoLoginAttemptedRef = useRef(false);
  const usernameInputRef = useRef<TextInput | null>(null);
  const passwordInputRef = useRef<TextInput | null>(null);
  const registerEmailInputRef = useRef<TextInput | null>(null);
  const registerConfirmPasswordInputRef = useRef<TextInput | null>(null);
  const forgotEmailInputRef = useRef<TextInput | null>(null);
  const resetEmailInputRef = useRef<TextInput | null>(null);
  const resetCodeInputRef = useRef<TextInput | null>(null);
  const resetPasswordInputRef = useRef<TextInput | null>(null);
  const resetConfirmPasswordInputRef = useRef<TextInput | null>(null);
  const inputOverlayInputRef = useRef<TextInput | null>(null);
  const chatInputRef = useRef<TextInput | null>(null);
  const updateVoiceMicBusy = useCallback((busy: boolean) => {
    voiceMicBusyRef.current = busy;
    setVoiceMicBusy(busy);
  }, []);

  useEffect(() => {
    audio.setStateListener(() => {
      setAudioRevision((value) => value + 1);
    });
    return () => {
      audio.setStateListener(null);
    };
  }, [audio]);

  useEffect(() => {
    menuStateRef.current = menuState;
  }, [menuState]);

  useEffect(() => {
    inputStateRef.current = inputState;
  }, [inputState]);

  useEffect(() => {
    modeRef.current = mode;
  }, [mode]);

  useEffect(() => {
    lastPingStartedAtRef.current = lastPingStartedAt;
  }, [lastPingStartedAt]);

  useEffect(() => {
    appStateRef.current = appState;
  }, [appState]);

  useEffect(() => {
    preferencesRef.current = preferences;
  }, [preferences]);

  useEffect(() => {
    voiceContextRef.current = voiceContext;
  }, [voiceContext]);

  useEffect(() => {
    voiceRequestedContextIdRef.current = voiceRequestedContextId;
  }, [voiceRequestedContextId]);

  useEffect(() => {
    voiceStateRef.current = voiceState;
  }, [voiceState]);

  useEffect(() => {
    if (Platform.OS === "web") {
      return;
    }
    voice.configureIdleAudioProfile();
  }, [voice]);

  useEffect(() => {
    credentialsRef.current = {
      password,
      serverUrl,
      username,
    };
  }, [password, serverUrl, username]);

  useEffect(() => {
    tts.setUiEnabled(storageReady && selfVoicingEnabled);
    lastPassiveUiSignatureRef.current = null;
  }, [storageReady, selfVoicingEnabled, tts]);

  useEffect(() => {
    return observeSpeechEnvironment({
      initialAppState: AppState.currentState,
      readScreenReader: () => AccessibilityInfo.isScreenReaderEnabled(),
      onScreenReaderChange: (listener) => AccessibilityInfo.addEventListener("screenReaderChanged", listener),
      onAppStateChange: (listener) => AppState.addEventListener("change", listener),
      onFocus: Platform.OS === "android" ? (listener) => AppState.addEventListener("focus", listener) : undefined,
      onBlur: Platform.OS === "android" ? (listener) => AppState.addEventListener("blur", listener) : undefined,
    }, (enabled) => {
      const nativeEnabled = enabled || WEB_SCREEN_READER_SUPPORT;
      nativeScreenReaderModeRef.current = !selfVoicingEnabledRef.current && nativeEnabled;
      setScreenReaderEnabled(nativeEnabled);
    }, () => tts.refreshNativeSpeech());
  }, [tts]);

  useEffect(() => () => {
    if (nativeFocusTimerRef.current) {
      clearTimeout(nativeFocusTimerRef.current);
      nativeFocusTimerRef.current = null;
    }
    if (nativeFocusTargetReleaseTimerRef.current) {
      clearTimeout(nativeFocusTargetReleaseTimerRef.current);
      nativeFocusTargetReleaseTimerRef.current = null;
    }
    nativeTabTextInputFocusTimersRef.current.forEach((timer) => {
      clearTimeout(timer);
    });
    nativeTabTextInputFocusTimersRef.current.clear();
    if (programmaticNativeFocusTimerRef.current) {
      clearTimeout(programmaticNativeFocusTimerRef.current);
      programmaticNativeFocusTimerRef.current = null;
    }
  }, []);

  const nativeScreenReaderMode = !selfVoicingEnabled && (screenReaderEnabled || WEB_SCREEN_READER_SUPPORT);
  const selfVoicingGestureEnabled = selfVoicingEnabled;
  const selfVoicingKeyboardEnabled = selfVoicingEnabled && activeTextInputKey === null;

  useEffect(() => {
    nativeScreenReaderModeRef.current = nativeScreenReaderMode;
    if (!nativeScreenReaderMode) {
      lastNativeFocusKeyRef.current = null;
      pendingNativeAccessibilityFocusKeyRef.current = null;
      nativeFocusTargetKeyRef.current = null;
      nativeMenuFocusOnNextPacketRef.current = false;
      nativeMenuFocusRequestedAtRef.current = 0;
      if (nativeFocusTimerRef.current) {
        clearTimeout(nativeFocusTimerRef.current);
        nativeFocusTimerRef.current = null;
      }
      if (nativeFocusTargetReleaseTimerRef.current) {
        clearTimeout(nativeFocusTargetReleaseTimerRef.current);
        nativeFocusTargetReleaseTimerRef.current = null;
      }
    }
  }, [nativeScreenReaderMode]);

  const postNativeScreenReaderAnnouncement = useCallback((text: string) => {
    if (!text) {
      return;
    }
    if (Platform.OS === "web") {
      setScreenReaderAnnouncement((current) => ({
        id: current.id + 1,
        text,
      }));
    } else {
      const announceWithOptions = (
        AccessibilityInfo as typeof AccessibilityInfo & {
          announceForAccessibilityWithOptions?: (announcement: string, options: { queue?: boolean }) => void;
        }
      ).announceForAccessibilityWithOptions;
      if (announceWithOptions) {
        announceWithOptions(text, { queue: false });
      } else {
        AccessibilityInfo.announceForAccessibility(text);
      }
    }
  }, []);

  const announceForNativeScreenReader = useCallback((text: string) => {
    tts.stopAnnouncements();
    postNativeScreenReaderAnnouncement(text);
  }, [postNativeScreenReaderAnnouncement, tts]);

  const clearScheduledNativeFocus = useCallback((key?: string | null) => {
    if (!key || pendingNativeAccessibilityFocusKeyRef.current === key) {
      pendingNativeAccessibilityFocusKeyRef.current = null;
      pendingNativeAccessibilityFocusQueuedAtRef.current = 0;
    }
    if (!key || nativeFocusTargetKeyRef.current === key) {
      nativeFocusTargetKeyRef.current = null;
      nativeFocusTargetQueuedAtRef.current = 0;
    }
    if (nativeFocusTargetReleaseTimerRef.current) {
      clearTimeout(nativeFocusTargetReleaseTimerRef.current);
      nativeFocusTargetReleaseTimerRef.current = null;
    }
  }, []);

  const queueNativeAccessibilityFocus = useCallback((key: string | null) => {
    if (!key) {
      return;
    }
    pendingNativeAccessibilityFocusKeyRef.current = key;
    pendingNativeAccessibilityFocusQueuedAtRef.current = Date.now();
  }, []);

  const requestNativeMenuFocusOnNextPacket = useCallback(() => {
    nativeMenuFocusOnNextPacketRef.current = true;
    nativeMenuFocusRequestedAtRef.current = Date.now();
  }, []);

  const isNativeAccessibilityFocusKeyCurrent = useCallback((key: string): boolean => {
    const dialog = dialogStateRef.current;
    if (key.startsWith("dialog:")) {
      return Boolean(dialog?.buttons.some((button) => key === `dialog:${dialog.id}:${button.id}`));
    }
    if (dialog && key !== "screen-reader:sv-toggle") return false;
    if (!key.startsWith("menu:")) {
      return true;
    }
    const currentMenuState = menuStateRef.current;
    return (
      modeRef.current === "main" &&
      currentMenuState.items.some((item, index) =>
        menuItemAccessibilityKey(currentMenuState.menuId, item, index) === key,
      )
    );
  }, []);

  const markNativeScreenReaderInteraction = useCallback((focusKey?: string | null) => {
    if (!nativeScreenReaderMode) {
      return;
    }
    if (focusKey) {
      lastNativeFocusKeyRef.current = focusKey;
      if (programmaticNativeFocusKeyRef.current === focusKey) {
        programmaticNativeFocusKeyRef.current = null;
        if (pendingNativeAccessibilityFocusKeyRef.current === focusKey) {
          pendingNativeAccessibilityFocusKeyRef.current = null;
          pendingNativeAccessibilityFocusQueuedAtRef.current = 0;
        }
        if (programmaticNativeFocusTimerRef.current) {
          clearTimeout(programmaticNativeFocusTimerRef.current);
          programmaticNativeFocusTimerRef.current = null;
        }
      }
    }
    tts.stopAnnouncements();
    pendingNativeAccessibilityFocusKeyRef.current = null;
    pendingNativeAccessibilityFocusQueuedAtRef.current = 0;
    nativeFocusTargetKeyRef.current = null;
    nativeFocusTargetQueuedAtRef.current = 0;
    if (nativeFocusTimerRef.current) {
      clearTimeout(nativeFocusTimerRef.current);
      nativeFocusTimerRef.current = null;
    }
    if (nativeFocusTargetReleaseTimerRef.current) {
      clearTimeout(nativeFocusTargetReleaseTimerRef.current);
      nativeFocusTargetReleaseTimerRef.current = null;
    }
  }, [nativeScreenReaderMode, tts]);

  const speakServerAnnouncement = useCallback(
    (text: string, options?: { remember?: boolean }) => {
      if (!text) {
        return;
      }
      tts.speakAnnouncement(text, {
        ...options,
      });
    },
    [tts],
  );

  const registerAccessibilityNode = useCallback(
    (key: string, textInputRef?: MutableRefObject<TextInput | null>) =>
      (node: AccessibilityFocusNode | null) => {
        if (textInputRef) {
          const previousTargets = textInputTargetByKeyRef.current.get(key);
          if (previousTargets) {
            previousTargets.forEach((target) => {
              textInputTargetsRef.current.delete(target);
            });
            textInputTargetByKeyRef.current.delete(key);
          }
        }
        if (node) {
          accessibilityNodeRefs.current.set(key, node);
          if (textInputRef) {
            const nextTargets = new Set<unknown>([node]);
            if (Platform.OS !== "web") {
              const nativeTarget = findNodeHandle(node as Parameters<typeof findNodeHandle>[0]);
              if (nativeTarget != null) {
                nextTargets.add(nativeTarget);
              }
            }
            textInputTargetByKeyRef.current.set(key, nextTargets);
            nextTargets.forEach((target) => {
              textInputTargetsRef.current.add(target);
            });
          }
        } else {
          accessibilityNodeRefs.current.delete(key);
        }
        if (textInputRef) {
          textInputRef.current = node as TextInput | null;
        }
      },
    [],
  );

  const moveNativeAccessibilityFocus = useCallback((key: string | null, attempt = 0, options: { force?: boolean } = {}) => {
    if (!nativeScreenReaderMode || !key) {
      return;
    }
    if (!isNativeAccessibilityFocusKeyCurrent(key)) {
      clearScheduledNativeFocus(key);
      return;
    }
    if (!options.force && lastNativeFocusKeyRef.current === key) {
      return;
    }

    nativeFocusTargetKeyRef.current = key;
    nativeFocusTargetQueuedAtRef.current = Date.now();
    if (nativeFocusTargetReleaseTimerRef.current) {
      clearTimeout(nativeFocusTargetReleaseTimerRef.current);
    }
    nativeFocusTargetReleaseTimerRef.current = setTimeout(() => {
      if (nativeFocusTargetKeyRef.current === key) {
        clearScheduledNativeFocus(key);
      }
    }, NATIVE_FOCUS_RESET_GUARD_MS);

    const node = accessibilityNodeRefs.current.get(key);
    if (!node) {
      if (attempt < NATIVE_FOCUS_MAX_ATTEMPTS) {
        if (nativeFocusTimerRef.current) {
          clearTimeout(nativeFocusTimerRef.current);
        }
        nativeFocusTimerRef.current = setTimeout(() => {
          nativeFocusTimerRef.current = null;
          moveNativeAccessibilityFocus(key, attempt + 1, options);
        }, NATIVE_FOCUS_DELAY_MS);
      } else {
        clearScheduledNativeFocus(key);
      }
      return;
    }

    if (nativeFocusTimerRef.current) {
      clearTimeout(nativeFocusTimerRef.current);
    }

    nativeFocusTimerRef.current = setTimeout(() => {
      nativeFocusTimerRef.current = null;
      if (!isNativeAccessibilityFocusKeyCurrent(key)) {
        clearScheduledNativeFocus(key);
        return;
      }
      if (accessibilityNodeRefs.current.get(key) !== node) {
        if (attempt < NATIVE_FOCUS_MAX_ATTEMPTS) {
          moveNativeAccessibilityFocus(key, attempt + 1, options);
        } else {
          clearScheduledNativeFocus(key);
        }
        return;
      }
      lastNativeFocusKeyRef.current = key;
      if (Platform.OS === "web") {
        const focusable = node as { focus?: () => void };
        focusable.focus?.();
        return;
      }
      const reactTag = findNodeHandle(node as Parameters<typeof findNodeHandle>[0]);
      if (reactTag) {
        programmaticNativeFocusKeyRef.current = key;
        if (programmaticNativeFocusTimerRef.current) {
          clearTimeout(programmaticNativeFocusTimerRef.current);
        }
        programmaticNativeFocusTimerRef.current = setTimeout(() => {
          if (programmaticNativeFocusKeyRef.current === key) {
            programmaticNativeFocusKeyRef.current = null;
          }
          programmaticNativeFocusTimerRef.current = null;
        }, 600);
        AccessibilityInfo.setAccessibilityFocus(reactTag);
      }
    }, NATIVE_FOCUS_DELAY_MS);
  }, [clearScheduledNativeFocus, isNativeAccessibilityFocusKeyCurrent, nativeScreenReaderMode]);

  const focusChatInputForNativeReader = useCallback(() => {
    if (!nativeScreenReaderMode) {
      return;
    }

    [120, 360].forEach((delayMs) => {
      let timer: ReturnType<typeof setTimeout>;
      timer = setTimeout(() => {
        nativeTabTextInputFocusTimersRef.current.delete(timer);
        moveNativeAccessibilityFocus("chat:input", 0, { force: true });
        chatInputRef.current?.focus();
      }, delayMs);
      nativeTabTextInputFocusTimersRef.current.add(timer);
    });
  }, [moveNativeAccessibilityFocus, nativeScreenReaderMode]);

  const clearNativeTabTextInputFocusTimers = useCallback(() => {
    nativeTabTextInputFocusTimersRef.current.forEach((timer) => {
      clearTimeout(timer);
    });
    nativeTabTextInputFocusTimersRef.current.clear();
  }, []);

  const handleTextInputFocus = useCallback((key: string, onFocus?: () => void) => {
    markNativeScreenReaderInteraction(key);
    activeTextInputKeyRef.current = key;
    setActiveTextInputKey(key);
    onFocus?.();
  }, [markNativeScreenReaderInteraction]);

  const handleTextInputBlur = useCallback((key: string) => {
    setActiveTextInputKey((current) => {
      if (current !== key) {
        return current;
      }
      activeTextInputKeyRef.current = null;
      return null;
    });
  }, []);

  const isNativeTextInputTarget = useCallback((target: unknown): boolean => {
    if (textInputTargetsRef.current.has(target)) {
      return true;
    }
    if (Platform.OS !== "web" || typeof Node === "undefined" || !(target instanceof Node)) {
      return false;
    }
    for (const registeredTarget of textInputTargetsRef.current) {
      if (registeredTarget instanceof Node && registeredTarget.contains(target)) {
        return true;
      }
    }
    return false;
  }, []);

  const isTextInputEditing = useCallback((): boolean => {
    return activeTextInputKeyRef.current !== null;
  }, []);

  const addHistoryMessage = useCallback((buffer: BufferName, text: string) => {
    buffers.add(buffer, text);
    setHistoryRevision((value) => value + 1);
  }, [buffers]);

  const deliverInterfaceFeedback = useCallback(
    (text: string) => {
      if (!text) {
        return;
      }
      if (selfVoicingEnabled) {
        tts.speakUi(text, {
          interruptAnnouncement: true,
          interruptUi: true,
        });
        return;
      }
      announceForNativeScreenReader(text);
    },
    [announceForNativeScreenReader, selfVoicingEnabled, tts],
  );

  const announceInterfaceFeedback = useCallback(
    (text: string) => {
      if (!text) {
        return;
      }
      addHistoryMessage("system", text);
      deliverInterfaceFeedback(text);
    },
    [addHistoryMessage, deliverInterfaceFeedback],
  );

  const announce = (text: string, buffer: BufferName = "system", speak = true) => {
    buffers.add(buffer, text);
    setHistoryRevision((value) => value + 1);
    if (speak && !buffers.isMuted(buffer)) {
      speakServerAnnouncement(text, { remember: false });
    }
  };

  const localizeKnownServerKey = useCallback(
    (
      value: string | undefined,
      context?: ServerAuthResponseContext,
      params?: Record<string, string | number>,
    ) => {
      if (!value) {
        return "";
      }
      const mappedKey = context ? SERVER_AUTH_RESPONSE_KEYS[context][value] : undefined;
      if (mappedKey) {
        return localization.t(mappedKey, params);
      }
      if (localization.has(value)) {
        return localization.t(value, params);
      }

      const normalized = value.replace(/_/g, "-");
      const candidateKeys = [
        normalized,
        `auth-error-${normalized}`,
        `error-${normalized}`,
        `auth-${normalized}`,
      ];
      for (const key of candidateKeys) {
        if (localization.has(key)) {
          return localization.t(key, params);
        }
      }
      return "";
    },
    [localization],
  );

  const localizeServerMessage = useCallback(
    (
      message: string | undefined,
      fallbackKey = "status-disconnected",
      params?: Record<string, unknown>,
      context?: ServerAuthResponseContext,
    ) => {
      if (!message) {
        return localization.t(fallbackKey);
      }
      const localizationParams = toLocalizationParams(params);
      const localizedKeyText = localizeKnownServerKey(message, context, localizationParams);
      if (localizedKeyText) {
        return localizedKeyText;
      }
      if (message === "Connection error.") {
        return localization.t("network-connection-error");
      }
      if (message === "Malformed server packet.") {
        return localization.t("network-malformed-packet");
      }
      if (message === "Temporary request timed out.") {
        return localization.t("network-temporary-timeout");
      }
      if (message === "Connection closed.") {
        return localization.t("network-connection-closed");
      }
      if (message === "logged-out") {
        return localization.t("logout-complete");
      }
      if (message === "exit") {
        return localization.t("logout-complete");
      }
      if (message === "kicked") {
        return localization.t("session-kicked");
      }
      if (message === "banned") {
        return localization.t("session-banned");
      }
      const formatted = message;
      return Object.entries(localizationParams).reduce(
        (text, [name, value]) => text.replaceAll(`{${name}}`, String(value)).replaceAll(`{$${name}}`, String(value)),
        formatted,
      );
    },
    [localization, localizeKnownServerKey],
  );

  const localizeAuthResponse = useCallback(
    (
      response:
        | RegisterResponsePacket
        | RequestPasswordResetResponsePacket
        | SubmitResetCodeResponsePacket,
      context: Exclude<ServerAuthResponseContext, "login">,
      successKey: string,
      failureKey: string,
    ) => {
      if (response.status === "success") {
        return localizeServerMessage(response.text, successKey);
      }
      const codeText = localizeKnownServerKey(response.error, context);
      if (codeText) {
        return codeText;
      }
      return localizeServerMessage(response.text, failureKey, undefined, context);
    },
    [localizeKnownServerKey, localizeServerMessage],
  );

  const localizeSystemMessage = useCallback((message: string | undefined, fallbackKey = "status-disconnected") => {
    return localizeServerMessage(message, fallbackKey);
  }, [localizeServerMessage]);

  const resolveVoiceStatusText = useCallback((
    keyOrText: string,
    params?: Record<string, unknown>,
  ) => {
    if (localization.has(keyOrText)) {
      return localization.t(keyOrText, toLocalizationParams(params));
    }
    return localizeServerMessage(keyOrText, "voice-chat-unavailable", params);
  }, [localization, localizeServerMessage]);

  const setVoiceStatusMessage = useCallback((
    keyOrText: string,
    speak = false,
    params?: Record<string, unknown>,
  ) => {
    const text = resolveVoiceStatusText(keyOrText, params);
    setVoiceStatusText(text);

    if (keyOrText === "voice-chat-mic-on") {
      void audio.playSound("voice_mic_on.ogg");
    } else if (keyOrText === "voice-chat-mic-off") {
      void audio.playSound("voice_mic_off.ogg");
    } else if (
      keyOrText === "voice-chat-mic-denied" ||
      keyOrText === "voice-chat-mic-unsupported" ||
      keyOrText === "voice-chat-mic-permission-denied"
    ) {
      void audio.playSound("voice_mic_error.ogg");
    }

    if (speak) {
      announceInterfaceFeedback(text);
      return;
    }
    addHistoryMessage("system", text);
  }, [addHistoryMessage, announceInterfaceFeedback, audio, resolveVoiceStatusText]);

  const isTerminalExitReason = useCallback((message: string | undefined) => {
    return message === "exit" || message === "logged-out" || message === "kicked" || message === "banned";
  }, []);

  const clearReconnectTimer = useCallback(() => {
    if (!reconnectTimerRef.current) {
      return;
    }
    clearTimeout(reconnectTimerRef.current);
    reconnectTimerRef.current = null;
  }, []);

  const resetReconnectState = useCallback(() => {
    clearReconnectTimer();
    reconnectWindowStartedAtRef.current = null;
    reconnectDelayMsRef.current = 1000;
    reconnectAttemptsRef.current = 0;
    expectingReconnectRef.current = false;
  }, [clearReconnectTimer]);

  const disableAutoReconnect = useCallback(() => {
    allowReconnectRef.current = false;
    manualDisconnectRef.current = true;
    sessionEstablishedRef.current = false;
    resetReconnectState();
  }, [resetReconnectState]);

  const prepareManualConnect = useCallback(() => {
    manualDisconnectRef.current = false;
    resetReconnectState();
  }, [resetReconnectState]);

  const startConnectionAudio = useCallback(() => {
    if (connectionAudioActiveRef.current) {
      return;
    }
    connectionAudioActiveRef.current = true;
    void audio.playMusic(CONNECTION_AUDIO_ASSET, {
      bus: "music",
      fade_in_ms: 0,
      fade_out_ms: 0,
      handle: CONNECTION_AUDIO_HANDLE,
      layer: CONNECTION_AUDIO_LAYER,
      loop: true,
    });
  }, [audio]);

  const stopConnectionAudio = useCallback((fadeMs = 0) => {
    if (!connectionAudioActiveRef.current) {
      return;
    }
    connectionAudioActiveRef.current = false;
    void audio.stopMusic(CONNECTION_AUDIO_HANDLE, fadeMs);
  }, [audio]);

  useEffect(() => () => {
    clearReconnectTimer();
    if (longPressResetTimerRef.current) {
      clearTimeout(longPressResetTimerRef.current);
      longPressResetTimerRef.current = null;
    }
    void androidForegroundService.stop();
    voice.shutdown();
    audio.shutdown();
    tts.stop();
  }, [audio, clearReconnectTimer, tts, voice]);

  useEffect(() => {
    void loadStoredClientState();
  }, []);

  useEffect(() => {
    void persistClientState();
  }, [storageReady, appLocale, preferences, registerEmail, serverUrl, username, password, selfVoicingEnabled]);

  useEffect(() => {
    if (!storageReady || connected || autoLoginAttemptedRef.current) {
      return;
    }
    if (!serverUrl || !username || !password) {
      autoLoginAttemptedRef.current = true;
      return;
    }

    autoLoginAttemptedRef.current = true;
    prepareManualConnect();
    setAuthStatusText(localization.t("auth-auto-login"));
    setStatusText(localization.t("status-connecting"));
    connectionRef.current?.connect(serverUrl, username, password, MOBILE_CLIENT_VERSION);
  }, [connected, localization, password, prepareManualConnect, serverUrl, storageReady, username]);

  const applyLocale = (locale: string | undefined) => {
    const statusTranslations = ["status-disconnected", "status-connecting", "status-connected"].map((key) => ({
      key, text: localization.t(key),
    }));
    const resolvedLocale = localization.setLocale(locale);
    tts.setLanguage(resolvedLocale);
    setAppLocale(resolvedLocale);
    setStatusText((current) => {
      const status = statusTranslations.find(({ text }) => text === current);
      return status ? localization.t(status.key) : current;
    });
  };

  const loadStoredClientState = async () => {
    try {
      const [storedConfigRaw, storedPassword, storedSelfVoicing] = await Promise.all([
        AsyncStorage.getItem(CLIENT_CONFIG_STORAGE_KEY),
        SecureStore.getItemAsync(CLIENT_PASSWORD_STORAGE_KEY),
        SecureStore.getItemAsync(CLIENT_SV_STORAGE_KEY),
      ]);

      let appliedStoredLocale = false;
      if (storedConfigRaw) {
        const storedConfig = JSON.parse(storedConfigRaw) as Partial<StoredClientConfig>;
        if (storedConfig.serverUrl) {
          setServerUrl(storedConfig.serverUrl);
        }
        if (storedConfig.username) {
          setUsername(storedConfig.username);
        }
        if (storedConfig.registerEmail) {
          setRegisterEmail(storedConfig.registerEmail);
          setForgotEmail(storedConfig.registerEmail);
          setResetEmail(storedConfig.registerEmail);
        }
        if (typeof storedConfig.appLocale === "string") {
          applyLocale(storedConfig.appLocale);
          appliedStoredLocale = true;
        }
        if (storedConfig.preferences) {
          applyPreferenceUpdates(storedConfig.preferences);
        }
      }

      if (!appliedStoredLocale) {
        applyLocale(detectPreferredLocale());
      }

      if (storedPassword) {
        setPassword(storedPassword);
      }
      if (storedSelfVoicing === "0") {
        selfVoicingEnabledRef.current = false;
        setSelfVoicingEnabled(false);
      } else if (storedSelfVoicing === "1") {
        selfVoicingEnabledRef.current = true;
        setSelfVoicingEnabled(true);
      }
    } catch {
      // Ignore storage corruption and fall back to defaults.
    } finally {
      setStorageReady(true);
    }
  };

  const persistClientState = async () => {
    if (!storageReady) {
      return;
    }

    const storedConfig: StoredClientConfig = {
      appLocale,
      preferences,
      registerEmail,
      serverUrl,
      username,
    };

    try {
      await AsyncStorage.setItem(CLIENT_CONFIG_STORAGE_KEY, JSON.stringify(storedConfig));
      if (password) {
        await SecureStore.setItemAsync(CLIENT_PASSWORD_STORAGE_KEY, password);
      } else {
        await SecureStore.deleteItemAsync(CLIENT_PASSWORD_STORAGE_KEY);
      }
      await SecureStore.setItemAsync(CLIENT_SV_STORAGE_KEY, selfVoicingEnabled ? "1" : "0");
    } catch {
      // Ignore storage write failures in the UI flow.
    }
  };

  const clearSavedAccount = async () => {
    try {
      await SecureStore.deleteItemAsync(CLIENT_PASSWORD_STORAGE_KEY);
      setPassword("");
      setUsername("");
      setRegisterEmail("");
      setForgotEmail("");
      setResetEmail("");
      setAuthMode("login");
      setAuthStatusText(localization.t("auth-account-cleared"));
      autoLoginAttemptedRef.current = true;
    } catch {
      setAuthStatusText(localization.t("auth-account-clear-failed"));
    }
  };

  const updateSelfVoicing = useCallback((enabled: boolean) => {
    selfVoicingEnabledRef.current = enabled;
    nativeScreenReaderModeRef.current = !enabled && (screenReaderEnabled || WEB_SCREEN_READER_SUPPORT);
    setSelfVoicingEnabled(enabled);
    const message = localization.t(
      enabled
        ? "sv-enabled-announcement"
        : screenReaderEnabled
          ? "sv-disabled-announcement"
          : "sv-disabled-no-screen-reader-announcement",
    );
    addHistoryMessage("system", message);
    if (enabled) {
      tts.refreshNativeSpeech();
      tts.setUiEnabled(true);
      tts.speakUi(message, {
        interruptAnnouncement: true,
        interruptUi: true,
      });
      return;
    }
    if (screenReaderEnabled) {
      tts.setUiEnabled(false);
      announceForNativeScreenReader(message);
      return;
    }
    // Keep the global three-finger toggle self-confirming when no native
    // screen reader is present. Announcement speech is not disabled with the
    // UI channel, so the confirmation can finish after self-voicing turns off.
    tts.speakAnnouncement(message, {
      remember: false,
    });
    tts.setUiEnabled(false);
  }, [addHistoryMessage, announceForNativeScreenReader, localization, screenReaderEnabled, tts]);

  const toggleSelfVoicing = useCallback(() => {
    updateSelfVoicing(!selfVoicingEnabledRef.current);
  }, [updateSelfVoicing]);

  const sendVoicePresence = useCallback((state: "connected" | "connection_lost") => {
    const contextId = voiceContextRef.current.contextId;
    if (!contextId) {
      return;
    }
    connectionRef.current?.send({
      context_id: contextId,
      scope: "table",
      state,
      type: "voice_presence",
    });
  }, []);

  const sendVoiceLeave = useCallback(() => {
    const contextId = voiceContextRef.current.contextId;
    if (!contextId) {
      return;
    }
    connectionRef.current?.send({
      context_id: contextId,
      scope: "table",
      type: "voice_leave",
    });
  }, []);

  const resetVoiceUiState = useCallback((statusKey = "voice-chat-not-connected") => {
    voicePresenceRegisteredRef.current = false;
    voiceJoinPendingRef.current = false;
    setVoiceRequestedContextId("");
    setVoiceContext({
      contextId: "",
      scope: "table",
    });
    setVoiceMicEnabled(false);
    setVoiceState("disconnected");
    setVoiceStatusText(resolveVoiceStatusText(statusKey));
  }, [resolveVoiceStatusText]);

  const ensureVoiceMicrophonePermission = useCallback(async (promptIfNeeded: boolean): Promise<boolean> => {
    if (Platform.OS === "web") {
      return true;
    }
    try {
      const existing = await ExpoAudio.getPermissionsAsync();
      if (existing.granted) {
        return true;
      }
      if (!promptIfNeeded || existing.canAskAgain === false) {
        return false;
      }
      const requested = await ExpoAudio.requestPermissionsAsync();
      return requested.granted;
    } catch {
      return false;
    }
  }, []);

  const requestInitialVoicePermission = useCallback(async () => {
    if (Platform.OS === "web") {
      return;
    }
    try {
      const alreadyRequested = await AsyncStorage.getItem(CLIENT_MIC_PERMISSION_REQUESTED_STORAGE_KEY);
      if (alreadyRequested) {
        return;
      }
      await AsyncStorage.setItem(CLIENT_MIC_PERMISSION_REQUESTED_STORAGE_KEY, "1");
      const granted = await ensureVoiceMicrophonePermission(true);
      if (!granted) {
        const message = localization.t("voice-chat-mic-permission-denied");
        setStatusText(message);
        setAuthStatusText(message);
        setVoiceStatusText(message);
        announceInterfaceFeedback(message);
      }
    } catch {
      // Ignore permission bootstrap storage failures.
    }
  }, [announceInterfaceFeedback, ensureVoiceMicrophonePermission, localization]);

  const requestInitialBatteryOptimizationPermission = useCallback(async () => {
    if (Platform.OS !== "android") {
      return;
    }
    try {
      await requestAndroidBatteryOptimizationExemptionOnce(
        localization,
        announceInterfaceFeedback,
      );
    } catch {
      // The prompt is best-effort; gameplay must not be blocked by settings failures.
    }
  }, [announceInterfaceFeedback, localization]);

  useEffect(() => {
    if (!storageReady) {
      return;
    }
    let cancelled = false;
    void (async () => {
      await requestInitialVoicePermission();
      if (!cancelled) {
        await requestInitialBatteryOptimizationPermission();
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [requestInitialBatteryOptimizationPermission, requestInitialVoicePermission, storageReady]);

  const leaveVoiceChat = useCallback((options?: {
    announce?: boolean;
    clearContext?: boolean;
    sendLeave?: boolean;
    statusKey?: string;
  }) => {
    const announceStatus = options?.announce ?? true;
    const clearContext = options?.clearContext ?? false;
    const sendLeavePacket = options?.sendLeave ?? voicePresenceRegisteredRef.current;
    const statusKey = options?.statusKey ?? "voice-chat-left";

    if (sendLeavePacket && voicePresenceRegisteredRef.current) {
      sendVoiceLeave();
    }
    voicePresenceRegisteredRef.current = false;
    voiceJoinPendingRef.current = false;
    voice.leave(false);
    setVoiceRequestedContextId("");
    if (clearContext) {
      setVoiceContext({
        contextId: "",
        scope: "table",
      });
    }
    setVoiceMicEnabled(false);
    setVoiceState("disconnected");
    if (announceStatus) {
      setVoiceStatusMessage(statusKey, true);
    } else {
      setVoiceStatusText(resolveVoiceStatusText(statusKey));
    }
    audio.refreshPlaybackState();
  }, [audio, resolveVoiceStatusText, sendVoiceLeave, setVoiceStatusMessage, voice]);

  useEffect(() => {
    voice.setCallbacks({
      onConnected: () => {
        voiceJoinPendingRef.current = false;
        voicePresenceRegisteredRef.current = true;
        audio.refreshPlaybackState();
        sendVoicePresence("connected");
      },
      onDisconnect: () => {
        voiceJoinPendingRef.current = false;
        if (voicePresenceRegisteredRef.current) {
          sendVoicePresence("connection_lost");
          voicePresenceRegisteredRef.current = false;
        }
        audio.refreshPlaybackState();
        setVoiceStatusMessage("voice-chat-connection-lost", true);
      },
      onMicBusy: (busy) => {
        updateVoiceMicBusy(busy);
      },
      onMicState: (enabled) => {
        setVoiceMicEnabled(enabled);
        audio.refreshPlaybackState();
      },
      onState: (nextState) => {
        setVoiceState(nextState);
      },
      onStatus: (messageKeyOrText, speak) => {
        setVoiceStatusMessage(messageKeyOrText, speak);
      },
    });
  }, [audio, sendVoicePresence, setVoiceStatusMessage, updateVoiceMicBusy, voice]);

  const applyPreferenceUpdates = (updates: Record<string, unknown>) => {
    if (Object.keys(updates).length === 0) {
      return;
    }

    let normalizedUpdates = updates;
    let mutedBuffersChanged = false;
    if (Object.prototype.hasOwnProperty.call(updates, "muted_buffers")) {
      mutedBuffersChanged = buffers.setMutedBuffers(updates.muted_buffers);
      normalizedUpdates = {
        ...updates,
        muted_buffers: buffers.getMutedBuffers(),
      };
    }

    const merged = { ...preferencesRef.current, ...normalizedUpdates };
    preferencesRef.current = merged;
    setPreferences(merged);

    if (mutedBuffersChanged) {
      setHistoryRevision((value) => value + 1);
    }

    if (typeof merged.music_volume === "number") {
      audio.setMusicVolume(merged.music_volume / 100);
    }
    if (typeof merged.sound_volume === "number") {
      audio.setSoundVolume(merged.sound_volume / 100);
    }
    if (typeof merged.ambience_volume === "number") {
      audio.setAmbienceVolume(merged.ambience_volume / 100);
    }
    if (typeof merged.voice_volume === "number") {
      voice.setVoiceVolume(merged.voice_volume / 100);
    }
    if (merged.mobile_tts_rate !== undefined) {
      tts.setRate(serverSpeechRateToExpoRate(merged.mobile_tts_rate));
    }
    if (typeof merged.mobile_tts_voice === "string") {
      void tts.setMobileVoice(merged.mobile_tts_voice);
    }
  };

  const handleSpeakPacket = (packet: SpeakPacket) => {
    const params = toLocalizationParams(packet.params);
    const text = packet.key && localization.has(packet.key)
      ? localization.t(packet.key, params)
      : localizeServerMessage(packet.text, packet.key || "", params);
    if (!text) {
      return;
    }
    const buffer = normalizeBufferName(packet.buffer);
    buffers.add(buffer, text);
    setHistoryRevision((value) => value + 1);
    if (!packet.muted && !buffers.isMuted(buffer)) {
      speakServerAnnouncement(text);
    }
  };

  const handleRemoveMenuPacket = (packet: RemoveMenuPacket) => {
    setMenuState((previous) => {
      if (packet.menu_id && previous.menuId !== packet.menu_id) {
        return previous;
      }
      transientTurnMenuAllowanceRef.current = null;
      nativeMenuFocusOnNextPacketRef.current = false;
      nativeMenuFocusRequestedAtRef.current = 0;
      clearScheduledNativeFocus();
      menuStateRef.current = defaultMenuState;
      return defaultMenuState;
    });
  };

  const handleRemoveEditboxPacket = (packet: RemoveEditboxPacket) => {
    const currentInput = inputStateRef.current;
    if (packet.input_id && currentInput?.inputId !== packet.input_id) {
      return;
    }
    if (currentInput) {
      requestNativeMenuFocusOnNextPacket();
    }
    Keyboard.dismiss();
    activeTextInputKeyRef.current = null;
    inputStateRef.current = null;
    setActiveTextInputKey((current) => (current === "input:field" ? null : current));
    setInputState(null);
    setInputValue("");
    setInputOverlayFocus(0);
  };

  const applyMenuPacket = (packet: MenuPacket, overrideItems?: Array<string | MenuItemData>) => {
    if (inputStateRef.current) {
      return;
    }

    const items = normalizeMenuItems(overrideItems ?? packet.items ?? []);
    const itemIds = items.map((item) => item.id);
    const previous = menuStateRef.current;
    const incomingMenuId = packet.menu_id ?? previous.menuId;

    if (packet.menu_id && packet.menu_id === previous.menuId && items.length === 0) {
      transientTurnMenuAllowanceRef.current = null;
      nativeMenuFocusOnNextPacketRef.current = false;
      nativeMenuFocusRequestedAtRef.current = 0;
      clearScheduledNativeFocus();
      menuStateRef.current = defaultMenuState;
      setMenuState(defaultMenuState);
      return;
    }

    const allowTurnMenuFromTransient =
      transientTurnMenuAllowanceRef.current !== null &&
      transientTurnMenuAllowanceRef.current === previous.menuId;

    if (
      incomingMenuId === "turn_menu" &&
      isProtectedTransientMenu(previous.menuId) &&
      !allowTurnMenuFromTransient
    ) {
      return;
    }

    if (allowTurnMenuFromTransient && incomingMenuId === "turn_menu") {
      transientTurnMenuAllowanceRef.current = null;
    } else if (incomingMenuId !== previous.menuId) {
      transientTurnMenuAllowanceRef.current = null;
    }

    const isSameMenuId = previous.menuId === (packet.menu_id ?? previous.menuId);
    const directMenuActionRequestedFocus =
      nativeMenuFocusOnNextPacketRef.current &&
      Date.now() - nativeMenuFocusRequestedAtRef.current <= NATIVE_MENU_FOCUS_REQUEST_TTL_MS;
    nativeMenuFocusOnNextPacketRef.current = false;
    nativeMenuFocusRequestedAtRef.current = 0;
    let position = typeof packet.position === "number" ? packet.position : null;

    if (packet.selection_id && position === null) {
      const selectedIndex = itemIds.indexOf(packet.selection_id);
      if (selectedIndex >= 0) {
        position = selectedIndex;
      }
    }

    const focusIndex = resolveMenuFocusIndex(
      previous.items,
      items,
      previous.focusIndex,
      {
        explicitIndex: position,
        sameMenu: isSameMenuId,
      },
    );

    const nextMenuState: MenuState = {
      escapeBehavior:
        packet.escape_behavior !== undefined || !isSameMenuId
          ? packet.escape_behavior ?? "keybind"
          : previous.escapeBehavior,
      focusIndex,
      gridEnabled:
        packet.grid_enabled !== undefined || !isSameMenuId
          ? packet.grid_enabled ?? false
          : previous.gridEnabled,
      gridHeight:
        packet.grid_height !== undefined || !isSameMenuId
          ? packet.grid_height ?? 0
          : previous.gridHeight,
      gridWidth:
        packet.grid_width !== undefined || !isSameMenuId
          ? packet.grid_width ?? 1
          : previous.gridWidth,
      items,
      menuId: packet.menu_id ?? previous.menuId,
    };

    const shouldFocusNativeMenu =
      nativeScreenReaderModeRef.current &&
      modeRef.current === "main" &&
      items.length > 0 &&
      (
        directMenuActionRequestedFocus ||
        shouldAutoFocusUnsolicitedMenu(nextMenuState.menuId, previous.menuId)
      );
    if (shouldFocusNativeMenu) {
      queueNativeAccessibilityFocus(
        menuItemAccessibilityKey(
          nextMenuState.menuId,
          nextMenuState.items[nextMenuState.focusIndex],
          nextMenuState.focusIndex,
        ),
      );
    }

    menuStateRef.current = nextMenuState;
    setMenuState(nextMenuState);
  };

  const handleMenuPacket = (packet: MenuPacket) => {
    if (packet.menu_id !== "mobile_voice_selection_menu") {
      applyMenuPacket(packet);
      return;
    }

    const generation = mobileVoiceMenuGenerationRef.current + 1;
    mobileVoiceMenuGenerationRef.current = generation;
    applyMenuPacket(packet, [
      { id: "mobile_voice_loading", text: localization.t("mobile-tts-loading-voices") },
      { id: "back", text: localization.t("back") },
    ]);
    void tts.getAvailableVoiceOptions({ forceRefresh: true }).then((voices) => {
      if (
        generation !== mobileVoiceMenuGenerationRef.current ||
        menuStateRef.current.menuId !== "mobile_voice_selection_menu"
      ) {
        return;
      }
      const currentVoice = String(preferencesRef.current.mobile_tts_voice || "");
      const currentVoiceAvailable = Boolean(currentVoice) && voices.some((voice) => voice.id === currentVoice);
      const voiceItems: MenuItemData[] = [
        {
          id: "default",
          text:
            currentVoiceAvailable
              ? localization.t("mobile-tts-default-voice")
              : `* ${localization.t("mobile-tts-default-voice")}`,
        },
        ...(currentVoice && !currentVoiceAvailable ? [{
          id: "mobile_voice_current_unavailable",
          selection_value: currentVoice,
          text: `* ${localization.t("mobile-tts-current-unavailable", { value: currentVoice })}`,
        }] : []),
        ...voices.map((voice, index) => ({
          id: `mobile_voice_${index}`,
          selection_value: voice.id,
          text: `${voice.id === currentVoice ? "* " : ""}${formatMobileVoiceLabel(
            voice,
            localization,
          )}`,
        })),
        { id: "back", text: localization.t("back") },
      ];
      const selectedItem = voiceItems.find((item) => item.selection_value === currentVoice);
      applyMenuPacket(
        {
          ...packet,
          selection_id: selectedItem?.id ?? "default",
        },
        voiceItems,
      );
    }).catch(() => {
      if (
        generation !== mobileVoiceMenuGenerationRef.current ||
        menuStateRef.current.menuId !== "mobile_voice_selection_menu"
      ) {
        return;
      }
      applyMenuPacket(packet, [
        { id: "default", text: localization.t("mobile-tts-default-voice") },
        ...(preferencesRef.current.mobile_tts_voice ? [{
          id: "mobile_voice_current_unavailable",
          selection_value: String(preferencesRef.current.mobile_tts_voice),
          text: `* ${localization.t("mobile-tts-current-unavailable", {
            value: String(preferencesRef.current.mobile_tts_voice),
          })}`,
        }] : []),
        { id: "back", text: localization.t("back") },
      ]);
    });
  };

  const handleChatPacket = (packet: ChatPacket) => {
    const message = formatChatMessage(localization, packet);
    buffers.add("chat", message);
    setHistoryRevision((value) => value + 1);

    let shouldSpeak = !packet.silent;
    if (packet.convo === "global" && preferencesRef.current.mute_global_chat === true) {
      shouldSpeak = false;
    }
    if (
      (packet.convo === "local" || packet.convo === "table" || packet.convo === "game") &&
      preferencesRef.current.mute_table_chat === true
    ) {
      shouldSpeak = false;
    }

    if (shouldSpeak && !buffers.isMuted("chat")) {
      let chatSound = "chat.ogg";
      let chatSoundFamily = "";
      if (packet.convo === "local" || packet.convo === "table" || packet.convo === "game") {
        chatSound = "chatlocal.ogg";
      } else if (packet.convo === "announcement") {
        chatSoundFamily = "notify";
      }
      if (chatSoundFamily) {
        void audio.playSoundFamily(chatSoundFamily);
      } else {
        void audio.playSound(chatSound);
      }
      speakServerAnnouncement(message);
    }
  };

  const stopGameAudio = () => {
    connectionAudioActiveRef.current = false;
    audio.stopAll(800);
  };

  const resetRuntimeUiForSession = useCallback((sendVoiceLeave: boolean) => {
    leaveVoiceChat({
      announce: false,
      clearContext: true,
      sendLeave: sendVoiceLeave,
      statusKey: "voice-chat-not-connected",
    });
    connectionAudioActiveRef.current = false;
    audio.stopAll(800);
    Keyboard.dismiss();
    activeTextInputKeyRef.current = null;
    setActiveTextInputKey(null);
    transientTurnMenuAllowanceRef.current = null;
    nativeMenuFocusOnNextPacketRef.current = false;
    nativeMenuFocusRequestedAtRef.current = 0;
    clearScheduledNativeFocus();
    setMenuState(defaultMenuState);
    menuStateRef.current = defaultMenuState;
    setInputState(null);
    inputStateRef.current = null;
    setInputValue("");
  }, [audio, clearScheduledNativeFocus, leaveVoiceChat]);

  const queueReconnectAttempt = useCallback((delayMs: number, statusMessage: string, speakMessage = false) => {
    const { password: reconnectPassword, serverUrl: reconnectServerUrl, username: reconnectUsername } = credentialsRef.current;
    if (!allowReconnectRef.current || manualDisconnectRef.current || !sessionEstablishedRef.current) {
      return;
    }
    if (!reconnectServerUrl || !reconnectUsername || !reconnectPassword) {
      return;
    }

    const now = Date.now();
    if (reconnectWindowStartedAtRef.current === null) {
      reconnectWindowStartedAtRef.current = now;
      reconnectDelayMsRef.current = 1000;
      reconnectAttemptsRef.current = 0;
    }

    if (now - reconnectWindowStartedAtRef.current > 60000) {
      allowReconnectRef.current = false;
      resetReconnectState();
      const failedMessage = localization.t("reconnect-failed");
      setStatusText(failedMessage);
      setAuthStatusText(failedMessage);
      announce(failedMessage, "system");
      return;
    }

    clearReconnectTimer();
    setStatusText(statusMessage);
    if (speakMessage) {
      announce(statusMessage, "system");
    }

    reconnectTimerRef.current = setTimeout(() => {
      reconnectTimerRef.current = null;
      if (!allowReconnectRef.current || manualDisconnectRef.current || !sessionEstablishedRef.current) {
        return;
      }

      reconnectAttemptsRef.current += 1;
      const attemptMessage = localization.t("reconnect-attempting", {
        value: reconnectAttemptsRef.current,
      });
      setStatusText(attemptMessage);
      connectionRef.current?.connect(
        reconnectServerUrl,
        reconnectUsername,
        reconnectPassword,
        MOBILE_CLIENT_VERSION,
      );
      reconnectDelayMsRef.current = Math.min(Math.max(reconnectDelayMsRef.current, 1000) * 2, 10000);
    }, delayMs);
  }, [announce, clearReconnectTimer, localization, resetReconnectState]);

  useEffect(() => {
    if (Platform.OS === "web") {
      return;
    }
    const subscription = AppState.addEventListener("change", (nextState) => {
      const previousState = appStateRef.current;
      appStateRef.current = nextState;
      setAppState(nextState);
      if (nextState !== "active" && previousState === "active") {
        audio.refreshPlaybackState();
        voice.refreshAudioSession();
      }
      if (nextState === "active" && previousState !== "active") {
        audio.refreshPlaybackState();
        voice.refreshAudioSession();
        if (
          !connected &&
          !reconnectTimerRef.current &&
          allowReconnectRef.current &&
          !manualDisconnectRef.current &&
          sessionEstablishedRef.current
        ) {
          queueReconnectAttempt(0, localization.t("status-connecting"));
        }
      }
    });
    return () => {
      subscription.remove();
    };
  }, [audio, connected, localization, queueReconnectAttempt, voice]);

  useEffect(() => {
    if (Platform.OS !== "android") {
      return;
    }

    // The explicit microphone action starts the microphone-class service
    // before WebRTC publishes a track. Let that serialized transition finish
    // before this general reconciler changes the service type; when the busy
    // flag clears, the effect runs again against the authoritative voice state.
    if (voiceMicBusy) {
      return;
    }

    const hasVoiceSession = voiceState === "connected" || voiceState === "connecting";
    const hasAudibleManagedAudio = audio.hasAudibleManagedLayers();
    const shouldUseMicrophoneService = voiceMicEnabled && hasVoiceSession;
    const shouldUsePlaybackService =
      !shouldUseMicrophoneService &&
      (hasVoiceSession || (appState !== "active" && hasAudibleManagedAudio));
    const shouldUseGameplayService =
      !shouldUseMicrophoneService &&
      !shouldUsePlaybackService &&
      connected;

    if (!shouldUseMicrophoneService && !shouldUsePlaybackService && !shouldUseGameplayService) {
      void androidForegroundService.stop();
      return;
    }

    const messageKey = shouldUseMicrophoneService
      ? "background-service-voice-mic"
      : hasVoiceSession
        ? "background-service-voice"
        : shouldUsePlaybackService
          ? "background-service-audio"
          : "background-service-gameplay";

    void androidForegroundService.sync({
      message: localization.t(messageKey),
      serviceType: shouldUseMicrophoneService
        ? "microphone"
        : shouldUsePlaybackService
          ? "mediaPlayback"
          : "dataSync",
      title: localization.t("background-service-title"),
    });
  }, [appState, audio, audioRevision, connected, localization, voiceMicBusy, voiceMicEnabled, voiceState]);

  const exitApplication = useCallback(() => {
    disableAutoReconnect();
    const disconnectPromise = connectionRef.current?.disconnectAndWait(1500) ?? Promise.resolve();
    void disconnectPromise.finally(async () => {
      if (Platform.OS === "android") {
        await androidForegroundService.stop();
      }
      voice.shutdown();
      audio.shutdown();
      tts.stop();
      if (Platform.OS === "android") {
        BackHandler.exitApp();
        return;
      }
      if (Platform.OS === "web" && typeof window !== "undefined") {
        window.close();
      }
    });
  }, [audio, disableAutoReconnect, tts, voice]);

  const resetToLoginScreen = useCallback((statusMessage: string, authMessage = statusMessage) => {
    buffers.clear();
    setHistoryRevision((value) => value + 1);
    setHistoryBuffer("all");
    setChatDraft("");
    void androidForegroundService.stop();
    voice.shutdown();
    audio.shutdown();
    Keyboard.dismiss();
    activeTextInputKeyRef.current = null;
    inputStateRef.current = null;
    transientTurnMenuAllowanceRef.current = null;
    nativeMenuFocusOnNextPacketRef.current = false;
    nativeMenuFocusRequestedAtRef.current = 0;
    clearScheduledNativeFocus();
    setActiveTextInputKey(null);
    setVoiceCapability({
      enabled: false,
      provider: "",
      tokenTtlSeconds: 0,
      url: "",
    });
    resetVoiceUiState();
    setConnected(false);
    modeRef.current = "main";
    setMode("main");
    setMenuState(defaultMenuState);
    menuStateRef.current = defaultMenuState;
    setInputState(null);
    setInputValue("");
    setInputOverlayFocus(0);
    setDialogState(null);
    setAuthMode("login");
    setStatusText(statusMessage);
    setAuthStatusText(authMessage);
  }, [audio, buffers, clearScheduledNativeFocus, resetVoiceUiState, voice]);

  const handleTerminalSessionExit = useCallback((message: string, announceMessage = true) => {
    disableAutoReconnect();
    if (announceMessage) {
      announce(message, "system");
    }
    resetToLoginScreen(message);
    const disconnectPromise = connectionRef.current?.disconnectAndWait(1500) ?? Promise.resolve();
    void disconnectPromise.finally(async () => {
      if (Platform.OS === "android") {
        await androidForegroundService.stop();
      }
      tts.stop();
      if (Platform.OS === "android") {
        BackHandler.exitApp();
      }
    });
  }, [announce, disableAutoReconnect, resetToLoginScreen, tts]);

  const openDialog = useCallback((nextDialog: Omit<DialogState, "focusIndex"> & { focusIndex?: number }) => {
    Keyboard.dismiss();
    activeTextInputKeyRef.current = null;
    setActiveTextInputKey(null);
    const nextState = {
      ...nextDialog,
      focusIndex: clamp(nextDialog.focusIndex ?? 0, 0, Math.max(0, nextDialog.buttons.length - 1)),
    };
    dialogStateRef.current = nextState;
    setDialogState(nextState);
    clearScheduledNativeFocus();
    queueNativeAccessibilityFocus(`dialog:${nextState.id}:${nextState.buttons[nextState.focusIndex]?.id}`);
  }, [clearScheduledNativeFocus, queueNativeAccessibilityFocus]);

  const closeDialog = useCallback(() => {
    const returnFocusKey = dialogStateRef.current?.returnFocusKey;
    dialogStateRef.current = null;
    clearScheduledNativeFocus();
    setDialogState(null);
    if (returnFocusKey) queueNativeAccessibilityFocus(returnFocusKey);
  }, [clearScheduledNativeFocus, queueNativeAccessibilityFocus]);

  const openLanguageMenu = () => {
    if (!storageReady || connected || dialogStateRef.current) return;
    const locales = localization.getAvailableLocales();
    const buttons: DialogAction[] = locales.map((locale) => {
      const language = localization.getLocaleLabel(locale);
      const checked = locale === appLocale;
      return {
        id: `locale:${locale}`,
        checked,
        text: checked ? localization.t("locale-menu-current", { language }) : language,
        variant: "secondary",
        onPress: () => {
          if (dialogStateRef.current?.buttons !== buttons) return;
          closeDialog();
          // Stop the old-language menu before changing the TTS language.
          tts.stop();
          tts.setCurrentUiTextProvider(null);
          applyLocale(locale);
          announceInterfaceFeedback(localization.t("locale-changed", { language }));
        },
      };
    });
    buttons.push({ id: "cancel", text: localization.t("back"), variant: "secondary", onPress: closeDialog });
    openDialog({
      id: "language-selection",
      title: localization.t("locale-menu-title"),
      message: "",
      buttons,
      focusIndex: locales.indexOf(appLocale),
      returnFocusKey: "auth:locale",
    });
  };

  const openClientHelp = (returnFocusKey: string) => {
    if (!storageReady || dialogStateRef.current || inputStateRef.current) return;
    openDialog({
      id: "client-help",
      title: localization.t("client-help"),
      message: [
        localization.t("footer-gestures-line-1"),
        localization.t("footer-gestures-line-2"),
        localization.t("native-mode-help"),
        localization.t("build-label", { value: MOBILE_BUILD_STAMP }),
      ].join("\n\n"),
      buttons: [{ id: "cancel", text: localization.t("back"), onPress: closeDialog, variant: "secondary" }],
      returnFocusKey,
    });
  };

  const promptMandatoryUpdate = (
    id: string,
    title: string,
    message: string,
    downloadUrl: string,
  ) => {
    if (updatePromptShownRef.current) {
      return;
    }
    updatePromptShownRef.current = true;
    openDialog({
      buttons: [
        {
          id: "confirm",
          onPress: () => {
            closeDialog();
            if (downloadUrl) {
              void Linking.openURL(downloadUrl).finally(() => {
                exitApplication();
              });
            } else {
              exitApplication();
            }
          },
          text: localization.t("update-confirm"),
          variant: "primary",
        },
        {
          id: "cancel",
          onPress: () => {
            closeDialog();
            exitApplication();
          },
          text: localization.t("update-cancel"),
          variant: "secondary",
        },
      ],
      id,
      message,
      title,
    });
  };

  const checkVersionGates = (packet: AuthorizeSuccessPacket): boolean => {
    const latestAppVersion = packet.update_info?.version?.trim();
    if (latestAppVersion && latestAppVersion !== MOBILE_CLIENT_VERSION) {
      setStatusText(localization.t("update-required-status", { value: latestAppVersion }));
      promptMandatoryUpdate(
        "mandatory-app-update",
        localization.t("update-required-title"),
        localization.t("update-required-message", { value: latestAppVersion }),
        releaseDownloadUrl(packet.update_info),
      );
      return true;
    }

    const serverSoundVersion = packet.sounds_info?.version?.trim();
    if (serverSoundVersion && serverSoundVersion !== bundledSoundVersion) {
      setStatusText(localization.t("sounds-update-required-status", { value: serverSoundVersion }));
      promptMandatoryUpdate(
        "mandatory-sounds-update",
        localization.t("sounds-update-required-title"),
        localization.t("sounds-update-required-message", {
          current: bundledSoundVersion || localization.t("update-unknown-version"),
          latest: serverSoundVersion,
        }),
        releaseDownloadUrl(packet.sounds_info),
      );
      return true;
    }

    return false;
  };

  const connectionRef = useRef<PlayAuralConnection | null>(null);
  if (!connectionRef.current) {
    connectionRef.current = new PlayAuralConnection({
      onClose: (reason) => {
        leaveVoiceChat({
          announce: false,
          clearContext: true,
          sendLeave: false,
          statusKey: "voice-chat-not-connected",
        });
        stopGameAudio();
        setConnected(false);
        if (!allowReconnectRef.current || manualDisconnectRef.current || !sessionEstablishedRef.current) {
          if (reason) {
            setStatusText(localizeSystemMessage(reason, "status-disconnected"));
          }
          return;
        }

        if (reconnectTimerRef.current) {
          return;
        }

        const reconnectMessage = expectingReconnectRef.current
          ? localization.t("reconnect-server-restarting")
          : localization.t("connection-lost");
        setAuthStatusText(reconnectMessage);
        queueReconnectAttempt(
          expectingReconnectRef.current ? 3000 : reconnectDelayMsRef.current,
          reconnectMessage,
          !expectingReconnectRef.current,
        );
      },
      onError: (message) => {
        stopConnectionAudio();
        const localizedMessage = localizeSystemMessage(message, "network-connection-error");
        setStatusText(localizedMessage);
        if (!allowReconnectRef.current || manualDisconnectRef.current || !sessionEstablishedRef.current) {
          announce(localizedMessage, "system");
        }
      },
      onConnecting: () => {
        startConnectionAudio();
      },
      onOpen: () => {
        setStatusText(localization.t("status-connecting"));
      },
      onPacket: (packet: ServerPacket) => {
        if (ENABLE_CLIENT_DEBUG_LOGS) {
          console.info("PLAYAURAL_DEBUG Packet", packet.type);
        }
        if (packet.type === "authorize_success") {
          const authPacket = packet as AuthorizeSuccessPacket;
          stopConnectionAudio();
          if (authPacket.username) {
            credentialsRef.current.username = authPacket.username;
            setUsername(authPacket.username);
          }
          if (authPacket.reset_ui === true) {
            // Reset the previous socket before the server releases this
            // session's ordered UI and audio packets.
            resetRuntimeUiForSession(false);
          }
          manualDisconnectRef.current = false;
          allowReconnectRef.current = true;
          expectingReconnectRef.current = false;
          sessionEstablishedRef.current = true;
          resetReconnectState();
          applyLocale(authPacket.locale);
          applyPreferenceUpdates(extractPreferenceUpdates(authPacket));
          setVoiceCapability({
            enabled: authPacket.voice?.enabled === true,
            provider: String(authPacket.voice?.provider || ""),
            tokenTtlSeconds: Number(authPacket.voice?.token_ttl_seconds || 0),
            url: String(authPacket.voice?.url || ""),
          });
          resetVoiceUiState();
          requestNativeMenuFocusOnNextPacket();
          setDialogState(null);
          setConnected(true);
          setAuthMode("login");
          setAuthStatusText("");
          if (checkVersionGates(authPacket)) {
            return;
          }
          setStatusText(localization.t("status-connected"));
          announce(localization.t("status-connected"), "system");
          return;
        }

        if (packet.type === "chat") {
          handleChatPacket(packet as ChatPacket);
          return;
        }

        if (packet.type === "clear_ui") {
          resetRuntimeUiForSession(voicePresenceRegisteredRef.current);
          return;
        }

        if (packet.type === "disconnect") {
          const disconnectPacket = packet as DisconnectPacket;
          const shouldExitApplication = isTerminalExitReason(disconnectPacket.reason);
          const reason = localizeSystemMessage(disconnectPacket.reason, "status-disconnected");
          leaveVoiceChat({
            announce: false,
            clearContext: true,
            sendLeave: false,
            statusKey: "voice-chat-not-connected",
          });
          stopGameAudio();
          setConnected(false);
          if (disconnectPacket.reconnect) {
            manualDisconnectRef.current = false;
            allowReconnectRef.current = true;
            expectingReconnectRef.current = true;
            sessionEstablishedRef.current = true;
            const reconnectMessage = localization.t("reconnect-server-restarting");
            setAuthStatusText(reconnectMessage);
            queueReconnectAttempt(3000, reconnectMessage, true);
            return;
          }

          disableAutoReconnect();
          if (shouldExitApplication) {
            handleTerminalSessionExit(reason);
            return;
          }
          resetToLoginScreen(reason);
          announce(reason, "system");
          return;
        }

        if (packet.type === "force_exit") {
          const forceExitPacket = packet as ForceExitPacket;
          const reason = localizeSystemMessage(forceExitPacket.reason, "logout-complete");
          leaveVoiceChat({
            announce: false,
            clearContext: true,
            sendLeave: false,
            statusKey: "voice-chat-not-connected",
          });
          handleTerminalSessionExit(reason);
          return;
        }

        if (packet.type === "login_failed") {
          const failurePacket = packet as LoginFailedPacket;
          const reason = failurePacket.reason
            ? localizeServerMessage(failurePacket.reason, "auth-login-failed", undefined, "login")
            : localizeServerMessage(failurePacket.text, "auth-login-failed", undefined, "login");
          leaveVoiceChat({
            announce: false,
            clearContext: true,
            sendLeave: false,
            statusKey: "voice-chat-not-connected",
          });
          stopConnectionAudio();
          stopGameAudio();
          setConnected(false);
          disableAutoReconnect();
          setAuthStatusText(reason);
          setStatusText(reason);
          announce(reason, "system");
          return;
        }

        if (packet.type === "menu" || packet.type === "update_menu") {
          handleMenuPacket(packet as MenuPacket);
          return;
        }

        if (packet.type === "remove_menu") {
          handleRemoveMenuPacket(packet as RemoveMenuPacket);
          return;
        }

        if (packet.type === "remove_editbox") {
          handleRemoveEditboxPacket(packet as RemoveEditboxPacket);
          return;
        }

        if (packet.type === "audio") {
          const audioPacket = packet as AudioCommandPacket;
          void audio.handleAudioCommand(audioPacket);
          return;
        }

        if (packet.type === "request_input") {
          const inputPacket = packet as RequestInputPacket;
          nativeMenuFocusOnNextPacketRef.current = false;
          nativeMenuFocusRequestedAtRef.current = 0;
          clearScheduledNativeFocus();
          setInputState({
            defaultValue: inputPacket.default_value || "",
            inputId: inputPacket.input_id,
            maxLength: inputPacket.max_length,
            multiline: inputPacket.multiline ?? false,
            prompt: inputPacket.prompt,
            readOnly: inputPacket.read_only ?? false,
          });
          setInputOverlayFocus(0);
          setInputValue(inputPacket.default_value || "");
          announceInterfaceFeedback(localization.t("input-opened"));
          if (Platform.OS !== "web") {
            requestAnimationFrame(() => {
              inputOverlayInputRef.current?.focus();
            });
          }
          return;
        }

        if (packet.type === "speak") {
          handleSpeakPacket(packet as SpeakPacket);
          return;
        }

        if (packet.type === "pong") {
          const startedAt = lastPingStartedAtRef.current;
          if (startedAt) {
            const elapsed = Date.now() - startedAt;
            setLastPingStartedAt(null);
            announce(localization.t("shortcut-ping-result", { value: elapsed }), "system", true);
          }
          return;
        }

        if (packet.type === "table_context") {
          const contextPacket = packet as TableContextPacket;
          const contextId = String(contextPacket.table_id || "");
          const previousContextId = voiceContextRef.current.contextId;
          if (previousContextId && contextId && contextId !== previousContextId) {
            stopGameAudio();
          }
          if (
            previousContextId &&
            contextId !== previousContextId &&
            (voicePresenceRegisteredRef.current ||
              voiceJoinPendingRef.current ||
              voiceStateRef.current === "connected" ||
              voiceStateRef.current === "connecting")
          ) {
            leaveVoiceChat({
              announce: false,
              clearContext: true,
              sendLeave: voicePresenceRegisteredRef.current,
              statusKey: "voice-chat-left-table",
            });
          }
          setVoiceContext({
            contextId,
            scope: "table",
          });
          return;
        }

        if (packet.type === "voice_join_info") {
          const voicePacket = packet as VoiceJoinInfoPacket;
          const packetContextId = String(voicePacket.context_id || "");
          const packetScope = String(voicePacket.scope || "table");
          const serverRequested = voicePacket.server_requested === true;
          if (!serverRequested && !voiceJoinPendingRef.current) {
            return;
          }
          const expectedContextId = serverRequested
            ? voiceContextRef.current.contextId
            : voiceRequestedContextIdRef.current;
          if (packetScope !== "table") {
            connectionRef.current?.send({
              context_id: packetContextId,
              scope: packetScope,
              type: "voice_leave",
            });
            return;
          }
          if (
            !packetContextId
            || packetContextId !== expectedContextId
          ) {
            connectionRef.current?.send({
              context_id: packetContextId,
              scope: "table",
              type: "voice_leave",
            });
            return;
          }
          if (serverRequested && !voice.supported) {
            connectionRef.current?.send({
              context_id: packetContextId,
              scope: "table",
              type: "voice_leave",
            });
            voiceJoinPendingRef.current = false;
            setVoiceRequestedContextId("");
            setVoiceState("disconnected");
            setVoiceStatusMessage("voice-chat-sdk-missing", true);
            return;
          }
          if (serverRequested) {
            voicePresenceRegisteredRef.current = false;
            setVoiceState("connecting");
            setVoiceMicEnabled(false);
            setVoiceStatusMessage("voice-chat-joining", true);
          }
          voiceJoinPendingRef.current = false;
          setVoiceContext({
            contextId: packetContextId,
            scope: "table",
          });
          setVoiceRequestedContextId("");
          voice.join(voicePacket);
          return;
        }

        if (packet.type === "voice_join_error") {
          const voiceErrorPacket = packet as VoiceJoinErrorPacket;
          const packetContextId = String(voiceErrorPacket.context_id || "");
          if (!voiceJoinPendingRef.current) {
            return;
          }
          if (
            voiceRequestedContextIdRef.current &&
            packetContextId &&
            packetContextId !== voiceRequestedContextIdRef.current
          ) {
            return;
          }
          voiceJoinPendingRef.current = false;
          setVoiceRequestedContextId("");
          setVoiceState("disconnected");
          setVoiceMicEnabled(false);
          setVoiceStatusMessage(
            voiceErrorPacket.key || voiceErrorPacket.text || "voice-chat-unavailable",
            true,
            voiceErrorPacket.params,
          );
          return;
        }

        if (packet.type === "voice_leave_ack") {
          setVoiceRequestedContextId("");
          return;
        }

        if (packet.type === "voice_context_closed") {
          const closedPacket = packet as VoiceContextClosedPacket;
          const closedContextId = String(closedPacket.context_id || "");
          if (
            !closedContextId
            || (
              closedContextId !== voiceContextRef.current.contextId
              && closedContextId !== voiceRequestedContextIdRef.current
            )
          ) {
            return;
          }
          leaveVoiceChat({
            announce: false,
            clearContext: true,
            sendLeave: false,
            statusKey: "voice-chat-left-table",
          });
          return;
        }

        if (packet.type === "register_response") {
          const response = packet as RegisterResponsePacket;
          const text = localizeAuthResponse(
            response,
            "register",
            "auth-register-success",
            "auth-register-failed",
          );
          setAuthStatusText(text);
          announce(text, "system");
          if (response.status === "success") {
            setAuthMode("login");
            setPassword("");
            setRegisterConfirmPassword("");
          }
          return;
        }

        if (packet.type === "request_password_reset_response") {
          const response = packet as RequestPasswordResetResponsePacket;
          const text = localizeAuthResponse(
            response,
            "password_reset",
            "auth-forgot-success",
            "auth-forgot-failed",
          );
          setAuthStatusText(text);
          announce(text, "system");
          if (response.status === "success") {
            setResetEmail(forgotEmail.trim());
            setAuthMode("reset");
          }
          return;
        }

        if (packet.type === "submit_reset_code_response") {
          const response = packet as SubmitResetCodeResponsePacket;
          const text = localizeAuthResponse(
            response,
            "reset_code",
            "auth-reset-success",
            "auth-reset-failed",
          );
          setAuthStatusText(text);
          announce(text, "system");
          if (response.status === "success") {
            setAuthMode("login");
            if (response.username) {
              setUsername(response.username);
            }
            setPassword(resetPassword);
            setResetCode("");
            setResetConfirmPassword("");
            setResetPassword("");
          }
          return;
        }

        if (packet.type === "update_locale") {
          const localePacket = packet as UpdateLocalePacket;
          applyLocale(localePacket.locale);
          return;
        }

        if (packet.type === "update_preference") {
          const preferencePacket = packet as UpdatePreferencePacket;
          applyPreferenceUpdates(extractPreferenceUpdates(preferencePacket));
        }
      },
    });
  }

  useEffect(() => {
    if (ENABLE_CLIENT_DEBUG_LOGS) {
      console.info("PLAYAURAL_DEBUG App build", {
        build: MOBILE_BUILD_STAMP,
        version: MOBILE_CLIENT_VERSION,
      });
    }
    applyLocale(appLocale);
    setStatusText(localization.t("status-disconnected"));
  }, []);

  useEffect(() => {
    if (!connected && !statusText) {
      setStatusText(localization.t("status-disconnected"));
    }
  }, [connected, localization, statusText]);

  useEffect(() => {
    if (voiceState === "disconnected" && !voiceStatusText) {
      setVoiceStatusText(localization.t("voice-chat-not-connected"));
    }
  }, [localization, voiceState, voiceStatusText]);

  const connection = connectionRef.current;
  const getHistoryBufferOptionName = (buffer: BufferName): string => {
    const name = localization.t(`buffer-${buffer}`);
    return buffers.isMuted(buffer)
      ? localization.t("history-buffer-muted-name", { name })
      : name;
  };
  const historyBufferName = localization.t(`buffer-name-${historyBuffer}`);
  const historyBufferDirectlyMuted = buffers.isDirectlyMuted(historyBuffer);
  const historyBufferMuted = buffers.isMuted(historyBuffer);
  const historyBufferMutedByAll = historyBuffer !== "all" && buffers.isDirectlyMuted("all");
  const historyBufferControlText = localization.t("history-buffer-current", {
    name: getHistoryBufferOptionName(historyBuffer),
  });
  const historyMuteControlText = historyBufferMutedByAll
    ? localization.t("history-buffer-muted-by-all", { name: historyBufferName })
    : localization.t(
        historyBufferDirectlyMuted ? "history-buffer-unmute" : "history-buffer-mute",
        { name: historyBufferName },
      );
  const historyMessages = useMemo(
    () => buffers.getVisibleMessages(historyBuffer).reverse(),
    [buffers, historyBuffer, historyRevision],
  );
  const historyEmptyText = buffers.isMuted(historyBuffer)
    ? localization.t("history-buffer-muted-empty", { name: historyBufferName })
    : localization.t("history-empty");
  const historyControlFocusItems = useMemo<HistoryFocusItem[]>(() => [
    { id: "buffer", kind: "buffer", text: historyBufferControlText },
    { id: "mute", kind: "mute", text: historyMuteControlText },
  ], [historyBufferControlText, historyMuteControlText]);
  const historyFocusItems = useMemo<HistoryFocusItem[]>(() => [
    ...historyControlFocusItems,
    ...historyMessages.map((message) => ({
      id: message.id,
      kind: "message" as const,
      text: message.text,
    })),
    ...(historyMessages.length === 0
      ? [{ id: "empty", kind: "empty" as const, text: historyEmptyText }]
      : []),
  ], [historyControlFocusItems, historyEmptyText, historyMessages]);
  const chatMessages = useMemo(() => buffers.getMessages("chat").reverse(), [buffers, historyRevision]);
  const [historyIndex, setHistoryIndex] = useAnchoredFocus(historyFocusItems);
  const focusedHistoryItem = historyFocusItems[historyIndex] ?? null;
  const historyBufferFocusIndex = historyFocusItems.findIndex((item) => item.kind === "buffer");
  const historyMuteFocusIndex = historyFocusItems.findIndex((item) => item.kind === "mute");
  const historyMessageFocusOffset = historyControlFocusItems.length;
  const focusedMenuItem = menuState.items[menuState.focusIndex];
  const focusedDialogButton = dialogState?.buttons[dialogState.focusIndex] ?? null;
  const { fontScale } = useWindowDimensions();
  const gridColumnCount = Math.max(1, Math.trunc(menuState.gridWidth));
  const menuGridRows = Math.max(1, Math.ceil(menuState.items.length / gridColumnCount));
  const isGridMenu = menuState.gridEnabled && gridColumnCount > 1;
  const gridRows = useMemo(() => {
    if (!isGridMenu) return [] as FocusableMenuItem[][];
    return Array.from({ length: menuGridRows }, (_, rowIndex) =>
      menuState.items.slice(rowIndex * gridColumnCount, (rowIndex + 1) * gridColumnCount),
    );
  }, [gridColumnCount, isGridMenu, menuGridRows, menuState.items]);
  const gridGap = styles.gridMenuBoard.gap;
  const gridCellSize = gridCellSizeForViewport(
    gridColumnCount, menuGridRows, mainPanelLayout.width, mainPanelLayout.height,
    gridGap, styles.gridMenuItem.minWidth * Math.max(1, fontScale),
  );
  const gridBoardWidth = gridColumnCount * gridCellSize + gridGap * (gridColumnCount - 1);
  const chatFocusItems = useMemo<ChatFocusItem[]>(() => [
    { id: "input", kind: "input", text: localization.t("chat-input-focus") },
    { id: "send", kind: "send", text: localization.t("chat-send-button") },
    voiceState === "connected"
      ? { id: "voiceLeave", kind: "voiceLeave", text: localization.t("voice-chat-leave") }
      : {
          id: "voiceJoin",
          kind: "voiceJoin",
          text: voiceState === "connecting"
            ? localization.t("voice-chat-joining")
            : localization.t("voice-chat-join"),
        },
    ...(voiceState === "connected"
      ? [{
          id: "voiceMic",
          kind: "voiceMic" as const,
          text: localization.t(
            voiceMicEnabled ? "voice-chat-turn-off-mic" : "voice-chat-turn-on-mic",
          ),
        }]
      : []),
    { id: "close", kind: "close", text: localization.t("chat-close-button") },
    ...chatMessages.map((message) => ({
      id: message.id,
      kind: "message" as const,
      text: message.text,
    })),
  ], [appLocale, chatMessages, localization, voiceMicEnabled, voiceState]);
  const [chatFocusIndex, setChatFocusIndex] = useAnchoredFocus(chatFocusItems);
  const focusedChatItem = chatFocusItems[chatFocusIndex] ?? null;
  const getChatFocusSpeechText = useCallback(
    (item: ChatFocusItem | null): string | null => {
      if (!item) {
        return null;
      }
      if (item.kind === "input") {
        return formatTextInputSpeech(localization, item.text, chatDraft);
      }
      return item.text;
    },
    [chatDraft, localization],
  );
  const sendChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "send");
  const voiceJoinChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "voiceJoin");
  const voiceLeaveChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "voiceLeave");
  const voiceMicChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "voiceMic");
  const closeChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "close");
  const firstChatMessageFocusIndex = chatFocusItems.findIndex((item) => item.kind === "message");
  const chatMessageFocusOffset = firstChatMessageFocusIndex >= 0 ? firstChatMessageFocusIndex : chatFocusItems.length;
  const inputOverlayButtonText = localization.t(inputState?.readOnly ? "input-close-button" : "input-submit-button");
  const focusedInputOverlayText =
    inputState === null
      ? null
      : inputOverlayFocus === 0
        ? formatTextInputSpeech(localization, inputState.prompt, inputValue, { readOnly: inputState.readOnly })
        : inputOverlayButtonText;
  const shortcutItems: ShortcutItem[] = [
    { id: "options", text: localization.t("shortcut-options") },
    { id: "friends", text: localization.t("shortcut-friends") },
    { id: "ping", text: localization.t("shortcut-ping") },
    { id: "list_online", text: localization.t("shortcut-online") },
    { id: "list_online_with_games", text: localization.t("shortcut-online-games") },
    {
      id: "music_down",
      text: localization.t("shortcut-music-down", {
        value: Math.round(audio.getMusicVolume() * 100),
      }),
    },
    {
      id: "music_up",
      text: localization.t("shortcut-music-up", {
        value: Math.round(audio.getMusicVolume() * 100),
      }),
    },
    {
      id: "ambience_down",
      text: localization.t("shortcut-ambience-down", {
        value: Math.round(audio.getAmbienceVolume() * 100),
      }),
    },
    {
      id: "ambience_up",
      text: localization.t("shortcut-ambience-up", {
        value: Math.round(audio.getAmbienceVolume() * 100),
      }),
    },
    { id: "help", text: localization.t("client-help") },
  ];
  const focusedShortcutItem = shortcutItems[shortcutFocusIndex] ?? null;
  const authFocusableItems = useMemo<AuthFocusableItem[]>(() => {
    if (connected) {
      return [];
    }

    const items: AuthFocusableItem[] = [
      { action: "open_locale", id: "locale", text: `${localization.t("locale")}: ${localization.getLocaleLabel(appLocale)}` },
      { action: "switch_login", id: "tab-login", text: localization.t("auth-mode-login") },
      { action: "switch_register", id: "tab-register", text: localization.t("auth-mode-register") },
      { action: "switch_forgot", id: "tab-forgot", text: localization.t("auth-mode-forgot") },
    ];

    if (authMode === "login" || authMode === "register") {
      items.push({ action: "focus_username", id: "field-username", text: localization.t("username") });
    }
    if (authMode === "login") {
      items.push({ action: "focus_password", id: "field-password", text: localization.t("password") });
      items.push({ action: "connect", id: "button-connect", text: localization.t("auth-login-submit") });
      if (username || password) {
        items.push({
          action: "clear_saved_account",
          id: "button-clear-account",
          text: localization.t("auth-clear-account"),
        });
      }
    } else if (authMode === "register") {
      items.push({
        action: "focus_register_email",
        id: "field-register-email",
        text: localization.t("auth-email"),
      });
      items.push({ action: "focus_password", id: "field-password", text: localization.t("password") });
      items.push({
        action: "focus_register_confirm_password",
        id: "field-register-confirm-password",
        text: localization.t("auth-confirm-password"),
      });
      items.push({
        action: "submit_register",
        id: "button-register",
        text: localization.t("auth-register-submit"),
      });
    } else if (authMode === "forgot") {
      items.push({
        action: "focus_forgot_email",
        id: "field-forgot-email",
        text: localization.t("auth-email"),
      });
      items.push({
        action: "submit_forgot",
        id: "button-forgot",
        text: localization.t("auth-forgot-submit"),
      });
    } else if (authMode === "reset") {
      items.push({
        action: "focus_reset_email",
        id: "field-reset-email",
        text: localization.t("auth-email"),
      });
      items.push({
        action: "focus_reset_code",
        id: "field-reset-code",
        text: localization.t("auth-reset-code"),
      });
      items.push({
        action: "focus_reset_password",
        id: "field-reset-password",
        text: localization.t("auth-new-password"),
      });
      items.push({
        action: "focus_reset_confirm_password",
        id: "field-reset-confirm-password",
        text: localization.t("auth-confirm-password"),
      });
      items.push({
        action: "submit_reset",
        id: "button-reset",
        text: localization.t("auth-reset-submit"),
      });
    }

    items.push({ action: "help", id: "help", text: localization.t("client-help") });
    items.push({
      action: "exit_app",
      id: "button-exit",
      text: localization.t("auth-exit"),
    });

    return items;
  }, [appLocale, authMode, connected, localization, password, username]);
  const focusedAuthItem = authFocusableItems[authFocusIndex] ?? null;
  const authScroll = useFocusScroll(
    selfVoicingEnabled && !connected && !dialogState && focusedAuthItem ? `auth:${focusedAuthItem.id}` : null,
    accessibilityNodeRefs,
  );
  const menuScroll = useFocusScroll(
    selfVoicingEnabled && connected && !dialogState && !inputState && mode === "main" && !isGridMenu && focusedMenuItem
      ? menuItemAccessibilityKey(menuState.menuId, focusedMenuItem, menuState.focusIndex) : null,
    accessibilityNodeRefs,
  );
  const focusedGridKey = selfVoicingEnabled && connected && !dialogState && !inputState && mode === "main" && isGridMenu && focusedMenuItem
    ? menuItemAccessibilityKey(menuState.menuId, focusedMenuItem, menuState.focusIndex) : null;
  const chatScroll = useFocusScroll(
    selfVoicingEnabled && connected && !dialogState && !inputState && mode === "chat" && focusedChatItem
      ? `chat:${focusedChatItem.id}` : null,
    accessibilityNodeRefs,
  );
  const historyScroll = useFocusScroll(
    selfVoicingEnabled && connected && !dialogState && !inputState && mode === "history" && focusedHistoryItem
      ? `history:${focusedHistoryItem.id}` : null,
    accessibilityNodeRefs,
  );
  const inputScroll = useFocusScroll(
    selfVoicingEnabled && !dialogState && inputState ? inputOverlayFocus === 0 ? "input:field" : "input:action" : null,
    accessibilityNodeRefs,
  );
  const dialogScroll = useFocusScroll(
    selfVoicingEnabled && dialogState?.id === "language-selection" && focusedDialogButton
      ? `dialog:${dialogState.id}:${focusedDialogButton.id}` : null,
    accessibilityNodeRefs,
  );
  const shortcutScroll = useFocusScroll(
    selfVoicingEnabled && connected && !dialogState && mode === "shortcuts" && focusedShortcutItem
      ? `shortcut:${focusedShortcutItem.id}` : null,
    accessibilityNodeRefs,
  );

  const getAuthFocusSpeechText = useCallback(
    (item: AuthFocusableItem | null): string | null => {
      if (!item) {
        return null;
      }
      switch (item.id) {
        case "field-username":
          return formatTextInputSpeech(localization, item.text, username);
        case "field-password":
          return formatTextInputSpeech(localization, item.text, password, { secure: true });
        case "field-register-email":
          return formatTextInputSpeech(localization, item.text, registerEmail);
        case "field-register-confirm-password":
          return formatTextInputSpeech(localization, item.text, registerConfirmPassword, { secure: true });
        case "field-forgot-email":
          return formatTextInputSpeech(localization, item.text, forgotEmail);
        case "field-reset-email":
          return formatTextInputSpeech(localization, item.text, resetEmail);
        case "field-reset-code":
          return formatTextInputSpeech(localization, item.text, resetCode);
        case "field-reset-password":
          return formatTextInputSpeech(localization, item.text, resetPassword, { secure: true });
        case "field-reset-confirm-password":
          return formatTextInputSpeech(localization, item.text, resetConfirmPassword, { secure: true });
        default:
          return item.text;
      }
    },
    [
      forgotEmail,
      localization,
      password,
      registerConfirmPassword,
      registerEmail,
      resetCode,
      resetConfirmPassword,
      resetEmail,
      resetPassword,
      username,
    ],
  );

  useEffect(() => {
    if (!activeTextInputKey) {
      return;
    }
    if (activeTextInputKey === "chat:input" && mode !== "chat") {
      activeTextInputKeyRef.current = null;
      setActiveTextInputKey(null);
      return;
    }
    if (activeTextInputKey === "input:field" && !inputState) {
      activeTextInputKeyRef.current = null;
      setActiveTextInputKey(null);
      return;
    }
    if (activeTextInputKey.startsWith("auth:")) {
      const isVisible = !connected && authFocusableItems.some((item) => `auth:${item.id}` === activeTextInputKey);
      if (!isVisible) {
        activeTextInputKeyRef.current = null;
        setActiveTextInputKey(null);
      }
    }
  }, [activeTextInputKey, authFocusableItems, connected, inputState, mode]);

  const getCurrentUiFocusText = useCallback((): string | null => {
    if (dialogState && focusedDialogButton) {
      return focusedDialogButton.text;
    }
    if (inputState && focusedInputOverlayText) {
      return focusedInputOverlayText;
    }
    if (!connected) {
      return getAuthFocusSpeechText(focusedAuthItem);
    }
    if (mode === "main") {
      return focusedMenuItem?.text ?? (menuState.items.length === 0 ? localization.t("menu-empty") : null);
    }
    if (mode === "shortcuts") {
      return focusedShortcutItem?.text ?? null;
    }
    if (mode === "history") {
      return focusedHistoryItem?.text ?? null;
    }
    if (mode === "chat") {
      return getChatFocusSpeechText(focusedChatItem);
    }
    return null;
  }, [
    connected,
    dialogState,
    focusedAuthItem,
    focusedDialogButton?.text,
    focusedHistoryItem?.text,
    focusedChatItem?.text,
    focusedInputOverlayText,
    focusedMenuItem?.text,
    focusedShortcutItem?.text,
    getAuthFocusSpeechText,
    getChatFocusSpeechText,
    inputState,
    localization,
    menuState.items.length,
    mode,
  ]);

  const getCurrentUiFocusSignature = useCallback((): string | null => {
    if (dialogState && focusedDialogButton) {
      return `dialog:${dialogState.id}:${dialogState.focusIndex}:${focusedDialogButton.id}:${focusedDialogButton.text}`;
    }
    if (inputState && focusedInputOverlayText) {
      return `input:${inputState.inputId ?? "none"}:${inputOverlayFocus}:${focusedInputOverlayText}`;
    }
    if (!connected) {
      return focusedAuthItem
        ? `auth:${authMode}:${focusedAuthItem.id}:${getAuthFocusSpeechText(focusedAuthItem)}`
        : null;
    }
    if (mode === "main") {
      const text = focusedMenuItem?.text ?? (menuState.items.length === 0 ? localization.t("menu-empty") : null);
      if (!text) {
        return null;
      }
      return `main:${menuState.menuId}:${focusedMenuItem?.id ?? menuState.focusIndex}:${text}`;
    }
    if (mode === "shortcuts" && focusedShortcutItem) {
      return `shortcuts:${shortcutFocusIndex}:${focusedShortcutItem.id}:${focusedShortcutItem.text}`;
    }
    if (mode === "history" && focusedHistoryItem) {
      return `history:${focusedHistoryItem.id}:${focusedHistoryItem.text}`;
    }
    if (mode === "chat" && focusedChatItem) {
      return `chat:${focusedChatItem.id}:${getChatFocusSpeechText(focusedChatItem)}`;
    }
    return null;
  }, [
    authMode,
    connected,
    dialogState,
    focusedAuthItem,
    focusedChatItem,
    focusedDialogButton,
    focusedHistoryItem,
    focusedInputOverlayText,
    focusedMenuItem,
    focusedShortcutItem,
    getAuthFocusSpeechText,
    getChatFocusSpeechText,
    inputOverlayFocus,
    inputState,
    localization,
    menuState.focusIndex,
    menuState.items.length,
    menuState.menuId,
    mode,
    shortcutFocusIndex,
  ]);

  const previousAuthItemsRef = useRef(authFocusableItems);
  useEffect(() => {
    const previousItems = previousAuthItemsRef.current;
    previousAuthItemsRef.current = authFocusableItems;
    setAuthFocusIndex((current) => resolveMenuFocusIndex(previousItems, authFocusableItems, current, { sameMenu: true }));
  }, [authFocusableItems]);

  useEffect(() => {
    if (connected) {
      authModeInitializedRef.current = false;
      previousAuthModeRef.current = null;
      return;
    }

    if (!authModeInitializedRef.current) {
      authModeInitializedRef.current = true;
      previousAuthModeRef.current = authMode;
      const defaultFocusId = getDefaultAuthFocusId(authMode);
      const nextIndex = authFocusableItems.findIndex((item) => item.id === defaultFocusId);
      if (nextIndex >= 0) {
        setAuthFocusIndex(nextIndex);
      }
      return;
    }

    if (previousAuthModeRef.current !== authMode) {
      previousAuthModeRef.current = authMode;
      const defaultFocusId = getDefaultAuthFocusId(authMode);
      const nextIndex = authFocusableItems.findIndex((item) => item.id === defaultFocusId);
      if (nextIndex >= 0) {
        setAuthFocusIndex(nextIndex);
      }
      announceInterfaceFeedback(localization.t(`auth-screen-${authMode}`));
      if (!dialogStateRef.current) queueNativeAccessibilityFocus(`auth:${defaultFocusId}`);
    }
  }, [announceInterfaceFeedback, authFocusableItems, authMode, connected, localization]);

  useEffect(() => {
    tts.setCurrentUiTextProvider(getCurrentUiFocusText);
    return () => {
      tts.setCurrentUiTextProvider(null);
    };
  }, [getCurrentUiFocusText, tts]);

  useEffect(() => {
    if (!nativeScreenReaderMode) {
      return;
    }
    const pendingFocusKey = pendingNativeAccessibilityFocusKeyRef.current;
    if (!pendingFocusKey) {
      return;
    }
    if (nativeFocusTargetKeyRef.current === pendingFocusKey) {
      return;
    }
    moveNativeAccessibilityFocus(pendingFocusKey, 0, { force: true });
  }, [
    authFocusIndex,
    chatFocusIndex,
    connected,
    dialogState,
    historyIndex,
    inputOverlayFocus,
    inputState,
    focusedMenuItem?.id,
    focusedMenuItem?.text,
    menuState.focusIndex,
    menuState.items.length,
    menuState.menuId,
    mode,
    moveNativeAccessibilityFocus,
    nativeScreenReaderMode,
    shortcutFocusIndex,
  ]);

  useEffect(() => {
    if (dialogState || !inputState || inputState.readOnly) {
      return;
    }

    let cancelled = false;
    const focusInputOverlay = () => {
      if (cancelled || dialogStateRef.current || inputStateRef.current?.inputId !== inputState.inputId) {
        return;
      }
      inputOverlayInputRef.current?.focus();
    };

    const firstFocusTimer = setTimeout(focusInputOverlay, Platform.OS === "android" ? 120 : 0);
    const retryFocusTimer = setTimeout(focusInputOverlay, Platform.OS === "android" ? 360 : 80);

    return () => {
      cancelled = true;
      clearTimeout(firstFocusTimer);
      clearTimeout(retryFocusTimer);
    };
  }, [Boolean(dialogState), inputState?.inputId, inputState?.readOnly]);

  useEffect(() => {
    if (!dialogState || !storageReady) {
      return;
    }
    lastPassiveUiSignatureRef.current = getCurrentUiFocusSignature();
    const initialButton = dialogState.buttons[dialogState.focusIndex]?.text ?? "";
    const dialogIntro = [dialogState.title, dialogState.message, initialButton].filter(Boolean).join(". ");
    if (!dialogIntro) {
      return;
    }
    if (!selfVoicingEnabled) {
      const focusKey = `dialog:${dialogState.id}:${dialogState.buttons[dialogState.focusIndex]?.id}`;
      queueNativeAccessibilityFocus(focusKey);
      moveNativeAccessibilityFocus(focusKey, 0, { force: true });
      announceForNativeScreenReader(dialogIntro);
      return;
    }
    tts.speakUi(dialogIntro, {
      interruptAnnouncement: true,
      interruptUi: true,
    });
  }, [announceForNativeScreenReader, dialogState?.id, selfVoicingEnabled, storageReady, tts]);

  const focusAuthField = (action: AuthFocusableItem["action"]) => {
    if (action === "focus_username") {
      usernameInputRef.current?.focus();
      return;
    }
    if (action === "focus_password") {
      passwordInputRef.current?.focus();
      return;
    }
    if (action === "focus_register_email") {
      registerEmailInputRef.current?.focus();
      return;
    }
    if (action === "focus_register_confirm_password") {
      registerConfirmPasswordInputRef.current?.focus();
      return;
    }
    if (action === "focus_forgot_email") {
      forgotEmailInputRef.current?.focus();
      return;
    }
    if (action === "focus_reset_email") {
      resetEmailInputRef.current?.focus();
      return;
    }
    if (action === "focus_reset_code") {
      resetCodeInputRef.current?.focus();
      return;
    }
    if (action === "focus_reset_password") {
      resetPasswordInputRef.current?.focus();
      return;
    }
    if (action === "focus_reset_confirm_password") {
      resetConfirmPasswordInputRef.current?.focus();
    }
  };

  const activateAuthItem = (item: AuthFocusableItem | null) => {
    if (!item) {
      return;
    }

    if (item.action === "switch_login") {
      setAuthMode("login");
      setAuthStatusText("");
      return;
    }
    if (item.action === "switch_register") {
      setAuthMode("register");
      setAuthStatusText("");
      return;
    }
    if (item.action === "switch_forgot") {
      setAuthMode("forgot");
      setAuthStatusText("");
      return;
    }

    if (item.action.startsWith("focus_")) {
      focusAuthField(item.action);
      return;
    }
    if (item.action === "connect") {
      connect();
      return;
    }
    if (item.action === "submit_register") {
      void submitRegistration();
      return;
    }
    if (item.action === "submit_forgot") {
      void submitForgotPassword();
      return;
    }
    if (item.action === "submit_reset") {
      void submitResetPassword();
      return;
    }
    if (item.action === "clear_saved_account") {
      void clearSavedAccount();
      return;
    }
    if (item.action === "exit_app") {
      exitApplication();
      return;
    }
    if (item.action === "open_locale") {
      openLanguageMenu();
    }
    if (item.action === "help") {
      openClientHelp("auth:help");
    }
  };

  const isAuthFocused = (id: string) => !connected && focusedAuthItem?.id === id;

  const focusAuthItemById = (id: string) => {
    const nextIndex = authFocusableItems.findIndex((item) => item.id === id);
    if (nextIndex >= 0) {
      markNativeScreenReaderInteraction(`auth:${id}`);
      setAuthFocusIndex(nextIndex);
    }
  };

  const sendMenuSelection = (itemOverride?: FocusableMenuItem | null, indexOverride?: number) => {
    const currentMenuState = menuStateRef.current;
    const item = itemOverride ?? currentMenuState.items[currentMenuState.focusIndex];
    if (!item) {
      return;
    }
    if (isProtectedTransientMenu(currentMenuState.menuId)) {
      transientTurnMenuAllowanceRef.current = currentMenuState.menuId;
    }
    requestNativeMenuFocusOnNextPacket();
    const outgoing: MenuSelectionPacket = {
      menu_id: currentMenuState.menuId || undefined,
      selection: (indexOverride ?? currentMenuState.focusIndex) + 1,
      selection_id: item.id,
      type: "menu",
    };
    if (item.selectionValue !== null && item.selectionValue !== undefined) {
      outgoing.selection_value = item.selectionValue;
    }
    connection?.send(outgoing);
  };

  const sendEscapeEquivalent = (
    menuId: string,
    escapeBehavior: string,
    items: FocusableMenuItem[],
  ) => {
    if (isProtectedTransientMenu(menuId)) {
      transientTurnMenuAllowanceRef.current = menuId;
    }
    const selectionIndex = escapeBehavior === "select_last_option" ? items.length - 1
      : escapeBehavior === "select_first_option" ? 0 : null;
    if (selectionIndex !== null && !items[selectionIndex]) return;
    requestNativeMenuFocusOnNextPacket();
    if (selectionIndex !== null) {
      connection?.send({
        menu_id: menuId || undefined,
        selection: selectionIndex + 1,
        selection_id: items[selectionIndex].id,
        type: "menu",
      });
    } else if (escapeBehavior === "escape_event") {
      connection?.send({ menu_id: menuId || undefined, type: "escape" });
    } else {
      connection?.send({ menu_id: menuId || undefined, type: "keybind", key: "escape" });
    }
  };

  const openActionsMenu = () => {
    const currentMenuState = menuStateRef.current;
    requestNativeMenuFocusOnNextPacket();
    connection?.send({
      menu_id: currentMenuState.menuId || "turn_menu",
      selection: 1,
      selection_id: "web_actions_menu",
      type: "menu",
    });
  };

  const sendShiftEnter = (itemOverride?: FocusableMenuItem | null) => {
    const currentMenuState = menuStateRef.current;
    const item = itemOverride ?? currentMenuState.items[currentMenuState.focusIndex];
    requestNativeMenuFocusOnNextPacket();
    connection?.send({
      key: "shift+enter",
      menu_item_id: item?.id ?? null,
      shift: true,
      type: "keybind",
    });
  };

  const getLongPressToken = (item: FocusableMenuItem, index: number) =>
    `${menuStateRef.current.menuId}:${index}:${item.id ?? "text"}`;

  const handleMenuItemLongPress = (item: FocusableMenuItem, index: number) => {
    if (selfVoicingEnabled) {
      return;
    }
    void audio.handleUserInteraction();
    focusMenuItemAt(index);
    const token = getLongPressToken(item, index);
    longPressConsumedRef.current = token;
    if (longPressResetTimerRef.current) {
      clearTimeout(longPressResetTimerRef.current);
    }
    longPressResetTimerRef.current = setTimeout(() => {
      if (longPressConsumedRef.current === token) {
        longPressConsumedRef.current = null;
      }
      longPressResetTimerRef.current = null;
    }, 3000);
    playMenuActivateSound();
    sendShiftEnter(item);
  };

  const handleMenuItemPress = (item: FocusableMenuItem, index: number) => {
    void audio.handleUserInteraction();
    focusMenuItemAt(index);
    const token = getLongPressToken(item, index);
    if (longPressConsumedRef.current === token) {
      longPressConsumedRef.current = null;
      if (longPressResetTimerRef.current) {
        clearTimeout(longPressResetTimerRef.current);
        longPressResetTimerRef.current = null;
      }
      return;
    }
    playMenuActivateSound();
    sendMenuSelection(item, index);
  };

  const closeOverlay = () => {
    const currentMode = modeRef.current;
    if (currentMode === "main") {
      return false;
    }
    const name = localization.t(`mode-${currentMode}`);
    clearNativeTabTextInputFocusTimers();
    Keyboard.dismiss();
    activeTextInputKeyRef.current = null;
    setActiveTextInputKey(null);
    modeRef.current = "main";
    setMode("main");
    const currentMenu = menuStateRef.current;
    if (currentMenu.items.length) {
      queueNativeAccessibilityFocus(menuItemAccessibilityKey(currentMenu.menuId, currentMenu.items[currentMenu.focusIndex], currentMenu.focusIndex));
    }
    announceInterfaceFeedback(localization.t("overlay-closed", { name }));
    return true;
  };

  const toggleOverlay = (nextMode: Exclude<AppMode, "main">) => {
    const resolved = modeRef.current === nextMode ? "main" : nextMode;
    modeRef.current = resolved;
    const key = resolved === "main" ? "overlay-closed" : "overlay-opened";
    if (resolved === "shortcuts") {
      setShortcutFocusIndex(0);
    }
    if (resolved === "chat") {
      setChatFocusIndex(0);
    }
    if (resolved === "history") {
      setHistoryIndex(historyBufferFocusIndex);
    }
    setMode(resolved);
    announceInterfaceFeedback(localization.t(key, { name: localization.t(`mode-${nextMode}`) }));
  };

  const openNativeTab = (nextMode: AppMode) => {
    void audio.handleUserInteraction();
    playMenuActivateSound();
    clearNativeTabTextInputFocusTimers();

    if (nextMode === "main") {
      const previousMode = mode;
      modeRef.current = "main";
      setMode("main");
      moveNativeAccessibilityFocus(
        focusedMenuItem ? menuItemAccessibilityKey(menuState.menuId, focusedMenuItem, menuState.focusIndex) : null,
        0,
        { force: true },
      );
      if (previousMode !== "main") {
        announceForNativeScreenReader(localization.t("overlay-closed", {
          name: localization.t(`mode-${previousMode}`),
        }));
      }
      return;
    }

    if (nextMode === "shortcuts") {
      setShortcutFocusIndex(0);
      moveNativeAccessibilityFocus(shortcutItems[0] ? `shortcut:${shortcutItems[0].id}` : null, 0, { force: true });
    } else if (nextMode === "chat") {
      setChatFocusIndex(0);
      focusChatInputForNativeReader();
    } else if (nextMode === "history") {
      setHistoryIndex(historyBufferFocusIndex);
      moveNativeAccessibilityFocus("history:buffer", 0, { force: true });
    }

    modeRef.current = nextMode;
    setMode(nextMode);
    announceForNativeScreenReader(localization.t("overlay-opened", { name: localization.t(`mode-${nextMode}`) }));
  };

  const syncPreference = (key: string, value: boolean | number | string) => {
    applyPreferenceUpdates({ [normalizePreferenceKey(key)]: value });
    if (connected) {
      connection?.send({
        key,
        type: "set_preference",
        value,
      });
    }
  };

  const announceHistoryBufferInfo = (buffer: BufferName) => {
    deliverInterfaceFeedback(localization.t("main-buffer-info", {
      count: buffers.getMessages(buffer).length,
      name: localization.t(`buffer-name-${buffer}`),
      status: buffers.isMuted(buffer)
        ? localization.t("main-status-muted-suffix")
        : "",
    }));
  };

  const selectHistoryBuffer = (buffer: BufferName) => {
    setHistoryBuffer(buffer);
    setHistoryIndex(historyBufferFocusIndex);
    announceHistoryBufferInfo(buffer);
  };

  const openHistoryBufferMenu = () => {
    if (dialogStateRef.current || inputStateRef.current || modeRef.current !== "history") {
      return;
    }
    const buttons: DialogAction[] = BUFFER_NAMES.map((buffer) => ({
      checked: buffer === historyBuffer,
      id: `buffer:${buffer}`,
      onPress: () => {
        if (dialogStateRef.current?.buttons !== buttons) {
          return;
        }
        closeDialog();
        selectHistoryBuffer(buffer);
      },
      text: buffer === historyBuffer
        ? localization.t("history-buffer-menu-current", {
            name: getHistoryBufferOptionName(buffer),
          })
        : getHistoryBufferOptionName(buffer),
      variant: "secondary",
    }));
    buttons.push({
      id: "cancel",
      onPress: closeDialog,
      text: localization.t("back"),
      variant: "secondary",
    });
    openDialog({
      buttons,
      focusIndex: BUFFER_NAMES.indexOf(historyBuffer),
      id: "history-buffer-selection",
      message: "",
      returnFocusKey: "history:buffer",
      title: localization.t("history-buffer-menu-title"),
    });
  };

  const toggleHistoryBufferMute = () => {
    if (historyBufferMutedByAll) {
      deliverInterfaceFeedback(historyMuteControlText);
      return;
    }
    const nextMuted = !buffers.isDirectlyMuted(historyBuffer);
    const mutedBuffers = new Set(buffers.getMutedBuffers());
    if (nextMuted) {
      mutedBuffers.add(historyBuffer);
    } else {
      mutedBuffers.delete(historyBuffer);
    }
    applyPreferenceUpdates({
      muted_buffers: BUFFER_NAMES.filter((buffer) => mutedBuffers.has(buffer)),
    });
    setHistoryIndex(historyMuteFocusIndex);
    deliverInterfaceFeedback(localization.t("main-buffer-status", {
      name: localization.t(`buffer-name-${historyBuffer}`),
      status: localization.t(nextMuted ? "buffer-status-muted" : "buffer-status-unmuted"),
    }));
  };

  const activateHistoryItem = (item: HistoryFocusItem | null) => {
    if (!item) {
      return;
    }
    if (item.kind === "buffer") {
      openHistoryBufferMenu();
      return;
    }
    if (item.kind === "mute") {
      toggleHistoryBufferMute();
      return;
    }
    speakUserFocus(item.text);
  };

  const activateShortcut = (shortcut: ShortcutItem | null) => {
    if (!shortcut) {
      return;
    }
    if (shortcut.id === "help") {
      openClientHelp("shortcut:help");
      return;
    }
    if (shortcut.id === "options") {
      requestNativeMenuFocusOnNextPacket();
      modeRef.current = "main";
      connection?.send({ type: "open_options" });
      setMode("main");
      return;
    }
    if (shortcut.id === "friends") {
      requestNativeMenuFocusOnNextPacket();
      modeRef.current = "main";
      connection?.send({ type: "open_friends_hub" });
      setMode("main");
      return;
    }
    if (shortcut.id === "ping") {
      setLastPingStartedAt(Date.now());
      connection?.send({ type: "ping" });
      return;
    }
    if (shortcut.id === "list_online") {
      connection?.send({ type: "list_online" });
      return;
    }
    if (shortcut.id === "list_online_with_games") {
      if (menuStateRef.current.menuId === "online_users") {
        closeOverlay();
        return;
      }
      requestNativeMenuFocusOnNextPacket();
      modeRef.current = "main";
      connection?.send({ type: "list_online_with_games" });
      setMode("main");
      return;
    }
    if (shortcut.id === "music_down") {
      const nextValue = clamp(Math.round(audio.getMusicVolume() * 100) - 10, 0, 100);
      syncPreference("audio/music_volume", nextValue);
      announceInterfaceFeedback(localization.t("shortcut-music-volume", { value: nextValue }));
      return;
    }
    if (shortcut.id === "music_up") {
      const nextValue = clamp(Math.round(audio.getMusicVolume() * 100) + 10, 0, 100);
      syncPreference("audio/music_volume", nextValue);
      announceInterfaceFeedback(localization.t("shortcut-music-volume", { value: nextValue }));
      return;
    }
    if (shortcut.id === "ambience_down") {
      const nextValue = clamp(Math.round(audio.getAmbienceVolume() * 100) - 10, 0, 100);
      syncPreference("audio/ambience_volume", nextValue);
      announceInterfaceFeedback(localization.t("shortcut-ambience-volume", { value: nextValue }));
      return;
    }
    if (shortcut.id === "ambience_up") {
      const nextValue = clamp(Math.round(audio.getAmbienceVolume() * 100) + 10, 0, 100);
      syncPreference("audio/ambience_volume", nextValue);
      announceInterfaceFeedback(localization.t("shortcut-ambience-volume", { value: nextValue }));
    }
  };

  // Match desktop: an item-specific highlight sound replaces the generic click.
  const playMenuMoveSound = (item?: FocusableMenuItem | null) => {
    if (item?.sound) {
      void audio.playSound(item.sound);
      return;
    }
    void audio.playSound("menuclick.ogg", { volume: 0.5 });
  };

  const focusMenuItemAt = (index: number) => {
    setMenuState((previous) => {
      const nextIndex = clamp(index, 0, Math.max(0, previous.items.length - 1));
      markNativeScreenReaderInteraction(
        menuItemAccessibilityKey(previous.menuId, previous.items[nextIndex], nextIndex),
      );
      if (previous.focusIndex === nextIndex) {
        return previous;
      }
      playMenuMoveSound(previous.items[nextIndex]);
      const nextState = {
        ...previous,
        focusIndex: nextIndex,
      };
      menuStateRef.current = nextState;
      return nextState;
    });
  };

  const playMenuActivateSound = () => {
    void audio.playSound("menuenter.ogg", { volume: 0.5 });
  };

  const speakUserFocus = (text: string | null | undefined) => {
    if (!text) {
      return;
    }
    if (!selfVoicingEnabled) {
      announceForNativeScreenReader(text);
      return;
    }
    tts.speakUi(text, {
      interruptAnnouncement: true,
      interruptUi: true,
    });
  };

  const clearInputOverlay = () => {
    Keyboard.dismiss();
    activeTextInputKeyRef.current = null;
    inputStateRef.current = null;
    setActiveTextInputKey((current) => (current === "input:field" ? null : current));
    setInputState(null);
    setInputValue("");
    setInputOverlayFocus(0);
  };

  const cancelInputOverlay = () => {
    const currentInput = inputStateRef.current;
    if (!currentInput) {
      return;
    }
    connection?.send({
      menu_id: currentInput.inputId || undefined,
      type: "escape",
    });
    clearInputOverlay();
    announceInterfaceFeedback(localization.t("input-cancelled"));
  };

  const submitInputOverlay = () => {
    if (!inputState) {
      return;
    }
    if (inputState.readOnly) {
      clearInputOverlay();
      return;
    }
    connection?.send({
      input_id: inputState.inputId,
      text: inputValue,
      type: "editbox",
    });
    announceInterfaceFeedback(localization.t("input-submitted"));
    clearInputOverlay();
  };

  const handlePrimaryActivate = () => {
    void audio.handleUserInteraction();
    const currentDialog = dialogStateRef.current;
    if (currentDialog || dialogState) {
      if (currentDialog?.buttons === dialogState?.buttons) {
        playMenuActivateSound();
        activateDialogButton();
      }
      return;
    }
    if (!connected) {
      playMenuActivateSound();
      activateAuthItem(focusedAuthItem);
      return;
    }
    if (mode === "shortcuts") {
      playMenuActivateSound();
      activateShortcut(focusedShortcutItem);
      return;
    }
    if (mode === "history") {
      if (focusedHistoryItem) {
        playMenuActivateSound();
        activateHistoryItem(focusedHistoryItem);
      }
      return;
    }
    if (mode === "chat") {
      playMenuActivateSound();
      if (focusedChatItem?.kind === "input") {
        chatInputRef.current?.focus();
      } else if (focusedChatItem?.kind === "send") {
        submitChat();
      } else if (focusedChatItem?.kind === "voiceJoin") {
        joinVoiceChat();
      } else if (focusedChatItem?.kind === "voiceLeave") {
        leaveVoiceChat();
      } else if (focusedChatItem?.kind === "voiceMic") {
        void toggleVoiceMicrophone();
      } else if (focusedChatItem?.kind === "close") {
        closeOverlay();
      } else if (focusedChatItem?.kind === "message") {
        speakUserFocus(focusedChatItem.text);
      }
      return;
    }
    if (inputState) {
      playMenuActivateSound();
      if (inputOverlayFocus === 0) {
        inputOverlayInputRef.current?.focus();
        return;
      }
      submitInputOverlay();
      return;
    }
    playMenuActivateSound();
    sendMenuSelection();
  };

  const handleModifiedActivate = () => {
    void audio.handleUserInteraction();
    if (!connected || dialogStateRef.current || inputStateRef.current || modeRef.current !== "main") {
      return;
    }
    sendShiftEnter();
  };

  const handleBoundaryJump = (target: "bottom" | "top") => {
    void audio.handleUserInteraction();
    const currentInput = inputStateRef.current;
    const currentMode = modeRef.current;

    const boundaryIndex = (length: number) => {
      if (length <= 0) {
        return 0;
      }
      return target === "top" ? 0 : length - 1;
    };

    if (dialogStateRef.current) {
      setDialogState((current) => {
        if (!current || current.buttons.length === 0) {
          return current;
        }
        const nextIndex = boundaryIndex(current.buttons.length);
        const nextText = current.buttons[nextIndex]?.text ?? null;
        if (nextIndex !== current.focusIndex) {
          playMenuMoveSound();
        }
        speakUserFocus(nextText);
        return {
          ...current,
          focusIndex: nextIndex,
        };
      });
      return;
    }

    if (currentInput) {
      const nextFocus: InputOverlayFocus = target === "top" ? 0 : 1;
      setInputOverlayFocus(nextFocus);
      if (nextFocus !== inputOverlayFocus) {
        playMenuMoveSound();
      }
      speakUserFocus(
        nextFocus === 0
          ? formatTextInputSpeech(localization, currentInput.prompt, inputValue, { readOnly: currentInput.readOnly })
          : inputOverlayButtonText,
      );
      return;
    }

    if (!connected) {
      if (authFocusableItems.length === 0) {
        return;
      }
      const nextIndex = boundaryIndex(authFocusableItems.length);
      setAuthFocusIndex(nextIndex);
      if (nextIndex !== authFocusIndex) {
        playMenuMoveSound();
      }
      speakUserFocus(getAuthFocusSpeechText(authFocusableItems[nextIndex] ?? null));
      return;
    }

    if (currentMode === "shortcuts") {
      if (shortcutItems.length === 0) {
        return;
      }
      const nextIndex = boundaryIndex(shortcutItems.length);
      setShortcutFocusIndex(nextIndex);
      if (nextIndex !== shortcutFocusIndex) {
        playMenuMoveSound();
      }
      speakUserFocus(shortcutItems[nextIndex]?.text);
      return;
    }

    if (currentMode === "history") {
      const nextIndex = boundaryIndex(historyFocusItems.length);
      setHistoryIndex(nextIndex);
      if (nextIndex !== historyIndex) {
        playMenuMoveSound();
      }
      speakUserFocus(historyFocusItems[nextIndex]?.text);
      return;
    }

    if (currentMode === "chat") {
      if (chatFocusItems.length === 0) {
        return;
      }
      const nextIndex = boundaryIndex(chatFocusItems.length);
      setChatFocusIndex(nextIndex);
      if (nextIndex !== chatFocusIndex) {
        playMenuMoveSound();
      }
      speakUserFocus(getChatFocusSpeechText(chatFocusItems[nextIndex] ?? null));
      return;
    }

    const previous = menuStateRef.current;
    if (previous.items.length === 0) return;
    const nextIndex = boundaryIndex(previous.items.length);
    const nextState = { ...previous, focusIndex: nextIndex };
    menuStateRef.current = nextState;
    setMenuState(nextState);
    if (nextIndex !== previous.focusIndex) playMenuMoveSound(previous.items[nextIndex]);
    speakUserFocus(previous.items[nextIndex]?.text);
  };

  const handleDirectionalNavigation = (direction: "up" | "down" | "left" | "right") => {
    void audio.handleUserInteraction();
    const currentInput = inputStateRef.current;
    const currentMode = modeRef.current;
    if (dialogStateRef.current) {
      setDialogState((current) => {
        if (!current || current.buttons.length === 0) {
          return current;
        }
        const delta = direction === "left" || direction === "up" ? -1 : 1;
        const nextIndex = clamp(current.focusIndex + delta, 0, current.buttons.length - 1);
        if (nextIndex !== current.focusIndex) {
          speakUserFocus(current.buttons[nextIndex]?.text);
          playMenuMoveSound();
        }
        return {
          ...current,
          focusIndex: nextIndex,
        };
      });
      return;
    }
    if (currentInput) {
      setInputOverlayFocus((current) => {
        const next: InputOverlayFocus = direction === "left" || direction === "up" ? 0 : 1;
        if (next !== current) {
          speakUserFocus(
            next === 0
              ? formatTextInputSpeech(localization, currentInput.prompt, inputValue, { readOnly: currentInput.readOnly })
              : inputOverlayButtonText,
          );
          playMenuMoveSound();
        }
        return next;
      });
      return;
    }
    if (!connected) {
      setAuthFocusIndex((current) => {
        if (authFocusableItems.length === 0) {
          return 0;
        }
        if (direction === "up" || direction === "left") {
          const next = Math.max(0, current - 1);
          if (next !== current) {
            speakUserFocus(getAuthFocusSpeechText(authFocusableItems[next] ?? null));
            playMenuMoveSound();
          }
          return next;
        }
        if (direction === "down" || direction === "right") {
          const next = Math.min(authFocusableItems.length - 1, current + 1);
          if (next !== current) {
            speakUserFocus(getAuthFocusSpeechText(authFocusableItems[next] ?? null));
            playMenuMoveSound();
          }
          return next;
        }
        return current;
      });
      return;
    }
    if (currentMode === "shortcuts") {
      setShortcutFocusIndex((current) => {
        if (shortcutItems.length === 0) {
          return 0;
        }
        if (direction === "up" || direction === "left") {
          const next = Math.max(0, current - 1);
          if (next !== current) {
            speakUserFocus(shortcutItems[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        if (direction === "down" || direction === "right") {
          const next = Math.min(shortcutItems.length - 1, current + 1);
          if (next !== current) {
            speakUserFocus(shortcutItems[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        return current;
      });
      return;
    }
    if (currentMode === "history") {
      setHistoryIndex((current) => {
        const max = Math.max(0, historyFocusItems.length - 1);
        if (direction === "left" || direction === "down") {
          const next = Math.min(max, current + 1);
          if (next !== current) {
            speakUserFocus(historyFocusItems[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        if (direction === "right" || direction === "up") {
          const next = Math.max(0, current - 1);
          if (next !== current) {
            speakUserFocus(historyFocusItems[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        return current;
      });
      return;
    }
    if (currentMode === "chat") {
      setChatFocusIndex((current) => {
        if (chatFocusItems.length === 0) {
          return 0;
        }
        if (direction === "up" || direction === "left") {
          const next = Math.max(0, current - 1);
          if (next !== current) {
            speakUserFocus(getChatFocusSpeechText(chatFocusItems[next] ?? null));
            playMenuMoveSound();
          }
          return next;
        }
        if (direction === "down" || direction === "right") {
          const next = Math.min(chatFocusItems.length - 1, current + 1);
          if (next !== current) {
            speakUserFocus(getChatFocusSpeechText(chatFocusItems[next] ?? null));
            playMenuMoveSound();
          }
          return next;
        }
        return current;
      });
      return;
    }
    const previous = menuStateRef.current;
    if (previous.items.length === 0) return;
    const nextIndex = previous.gridEnabled
      ? nextGridIndex(previous.focusIndex, previous.items.length, previous.gridWidth, direction)
      : nextLinearIndex(
          previous.focusIndex,
          previous.items.length,
          direction === "up" || direction === "left" ? "up" : "down",
        );
    if (nextIndex === previous.focusIndex) return;
    const nextState = { ...previous, focusIndex: nextIndex };
    menuStateRef.current = nextState;
    setMenuState(nextState);
    speakUserFocus(previous.items[nextIndex]?.text);
    playMenuMoveSound(previous.items[nextIndex]);
  };

  const handleRepeatLast = () => {
    const repeated = tts.repeatLastAnnouncement();
    if (!repeated) {
      announceInterfaceFeedback(localization.t("gesture-no-last"));
    }
  };

  const logoutAndExitIfAndroid = () => {
    handleTerminalSessionExit(localization.t("logout-complete"), false);
  };

  const confirmLogout = () => {
    openDialog({
      buttons: [
        {
          id: "confirm",
          onPress: logoutAndExitIfAndroid,
          text: localization.t("logout-confirm"),
          variant: "danger",
        },
        {
          id: "cancel",
          onPress: closeDialog,
          text: localization.t("logout-cancel"),
          variant: "secondary",
        },
      ],
      id: "logout-confirmation",
      message: localization.t("logout-message"),
      title: localization.t("logout-title"),
    });
  };

  const activateDialogButton = () => {
    const current = dialogStateRef.current;
    current?.buttons[current.focusIndex]?.onPress();
  };

  const focusDialogButton = (dialog: DialogState, index: number) => {
    const current = dialogStateRef.current;
    const button = current?.buttons[index];
    if (!current || current.buttons !== dialog.buttons || !button) return;
    markNativeScreenReaderInteraction(`dialog:${current.id}:${button.id}`);
    setDialogState({ ...current, focusIndex: index });
  };

  const handleSystemSwipe = (direction: "up" | "down" | "left" | "right") => {
    void audio.handleUserInteraction();
    const currentMenuState = menuStateRef.current;
    const currentDialog = dialogStateRef.current;
    if (currentDialog) {
      if (direction === "up") {
        const cancelButton = currentDialog.buttons.find((button) => button.id === "cancel");
        cancelButton?.onPress();
      }
      return;
    }
    if (direction === "up") {
      if (inputStateRef.current) {
        cancelInputOverlay();
        return;
      }
      if (closeOverlay()) {
        return;
      }
      if (!connected) {
        exitApplication();
        return;
      }
      if (currentMenuState.menuId === "turn_menu") {
        playMenuActivateSound();
        openActionsMenu();
        return;
      }
      if (currentMenuState.menuId === "main_menu") {
        confirmLogout();
        return;
      }
      sendEscapeEquivalent(
        currentMenuState.menuId,
        currentMenuState.escapeBehavior,
        currentMenuState.items,
      );
      return;
    }
    if (inputStateRef.current || !connected) {
      return;
    }
    if (direction === "right") {
      toggleOverlay("chat");
      return;
    }
    if (direction === "left") {
      toggleOverlay("history");
      return;
    }
    if (direction === "down") {
      toggleOverlay("shortcuts");
    }
  };

  handleSystemSwipeRef.current = handleSystemSwipe;

  const showNativeNavigationTabs =
    connected && !selfVoicingEnabled && !dialogState && !inputState;

  const handleStopSpeech = () => {
    tts.stop();
  };

  useEffect(() => {
    if (Platform.OS !== "android") {
      return;
    }
    const subscription = BackHandler.addEventListener("hardwareBackPress", () => {
      handleSystemSwipeRef.current?.("up");
      return true;
    });
    return () => {
      subscription.remove();
    };
  }, []);

  useEffect(() => {
    if (Platform.OS !== "web" || selfVoicingEnabled) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !event.altKey && !event.ctrlKey && !event.metaKey) {
        event.preventDefault();
        handleSystemSwipeRef.current?.("up");
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [selfVoicingEnabled]);

  const gestures = useSelfVoicingGestures({
    enabled: selfVoicingGestureEnabled,
    globalToggleEnabled: true,
    isNativeTextInputTarget,
    isTextInputEditing,
    onDoubleTap: handlePrimaryActivate,
    onDoubleTapHold: handleModifiedActivate,
    onSingleFingerSwipe: handleDirectionalNavigation,
    onSingleFingerSwipeHold: handleDirectionalNavigation,
    onThreeFingerSwipe: (direction) => {
      if (direction === "up") {
        handleBoundaryJump("top");
        return;
      }
      if (direction === "down") {
        handleBoundaryJump("bottom");
      }
    },
    onThreeFingerTripleTap: toggleSelfVoicing,
    onTwoFingerSwipe: handleSystemSwipe,
    onTwoFingerTap: handleStopSpeech,
  });

  useEffect(() => {
    if (Platform.OS !== "web" || typeof window === "undefined" || !selfVoicingKeyboardEnabled) {
      return;
    }

    const isEditableTarget = (target: EventTarget | null): boolean => {
      if (!(target instanceof HTMLElement)) {
        return false;
      }
      const tagName = target.tagName;
      return target.isContentEditable || tagName === "INPUT" || tagName === "TEXTAREA" || tagName === "SELECT";
    };

    const onKeyDown = (event: KeyboardEvent) => {
      const editableTarget = isEditableTarget(event.target);
      const allowInputOverlayKeys = Boolean(inputStateRef.current);
      const allowChatOverlayKeys = mode === "chat";
      if (event.metaKey || event.altKey) {
        return;
      }

      if (editableTarget && !allowInputOverlayKeys && !allowChatOverlayKeys) {
        return;
      }

      if (editableTarget && allowChatOverlayKeys) {
        const handledChatKeys = new Set([
          "ArrowDown",
          "ArrowLeft",
          "ArrowRight",
          "ArrowUp",
          "Escape",
          "Enter",
        ]);
        if (!handledChatKeys.has(event.key)) {
          return;
        }
      }

      if (editableTarget && allowChatOverlayKeys && event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        submitChat();
        return;
      }

      if ((event.key === " " || event.key === "Spacebar") && event.ctrlKey) {
        event.preventDefault();
        handleStopSpeech();
        return;
      }
      if ((event.key === "r" || event.key === "R") && event.ctrlKey) {
        event.preventDefault();
        handleRepeatLast();
        return;
      }
      if (event.ctrlKey) {
        return;
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        if (event.shiftKey) {
          handleSystemSwipe("up");
        } else {
          handleDirectionalNavigation("up");
        }
        return;
      }
      if (event.key === "ArrowDown") {
        event.preventDefault();
        if (event.shiftKey) {
          handleSystemSwipe("down");
        } else {
          handleDirectionalNavigation("down");
        }
        return;
      }
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        if (event.shiftKey) {
          handleSystemSwipe("left");
        } else {
          handleDirectionalNavigation("left");
        }
        return;
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        if (event.shiftKey) {
          handleSystemSwipe("right");
        } else {
          handleDirectionalNavigation("right");
        }
        return;
      }
      if (event.key === "Enter") {
        event.preventDefault();
        if (event.shiftKey) {
          handleModifiedActivate();
        } else {
          handlePrimaryActivate();
        }
        return;
      }
      if (event.key === "Escape") {
        event.preventDefault();
        handleSystemSwipe("up");
        return;
      }
      if (event.key === "Home") {
        event.preventDefault();
        handleBoundaryJump("top");
        return;
      }
      if (event.key === "End") {
        event.preventDefault();
        handleBoundaryJump("bottom");
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [handleBoundaryJump, handleDirectionalNavigation, handleModifiedActivate, handlePrimaryActivate, handleSystemSwipe, selfVoicingKeyboardEnabled]);

  useEffect(() => {
    if (!storageReady || !selfVoicingEnabled) {
      return;
    }
    const focusSpeechOptions = {
      interruptAnnouncement: false,
      interruptUi: false,
    };

    const focusSignature = getCurrentUiFocusSignature();
    if (!focusSignature || lastPassiveUiSignatureRef.current === focusSignature) {
      return;
    }

    const focusText = getCurrentUiFocusText();
    if (focusText) {
      lastPassiveUiSignatureRef.current = focusSignature;
      tts.speakUi(focusText, focusSpeechOptions);
    }
  }, [
    storageReady,
    selfVoicingEnabled,
    authFocusIndex,
    chatDraft,
    dialogState,
    getCurrentUiFocusText,
    inputState,
    mode,
    menuState.focusIndex,
    menuState.menuId,
    historyIndex,
    chatFocusIndex,
    shortcutFocusIndex,
    getCurrentUiFocusSignature,
  ]);

  const connect = () => {
    if (!serverUrl || !username || !password) {
      const message = localization.t("login-required");
      setAuthStatusText(message);
      announceInterfaceFeedback(message);
      return;
    }
    try {
      const parsed = new URL(serverUrl);
      if (parsed.protocol !== "ws:" && parsed.protocol !== "wss:") {
        throw new Error("invalid");
      }
    } catch {
      const message = localization.t("network-invalid-url");
      setAuthStatusText(message);
      setStatusText(message);
      announceInterfaceFeedback(message);
      return;
    }
    prepareManualConnect();
    setAuthStatusText("");
    setStatusText(localization.t("status-connecting"));
    connection?.connect(serverUrl, username, password, MOBILE_CLIENT_VERSION);
  };

  const submitChat = () => {
    const trimmed = chatDraft.trim();
    if (!trimmed) {
      return;
    }
    const globalMatch = trimmed.match(/^\/(?:g|global)\s+(.+)$/i);
    const convo = globalMatch ? "global" : "local";
    const message = globalMatch ? globalMatch[1].trim() : trimmed;
    if (!message) {
      return;
    }
    connection?.send({
      convo,
      message,
      type: "chat",
    });
    setChatDraft("");
  };

  const joinVoiceChat = useCallback(() => {
    if (voiceState === "connected" || voiceState === "connecting") {
      return;
    }
    if (!connected) {
      setVoiceStatusMessage("status-disconnected", true);
      return;
    }
    if (!voiceCapability.enabled) {
      setVoiceStatusMessage("voice-chat-unavailable", true);
      return;
    }
    const contextId = voiceContextRef.current.contextId;
    if (!contextId) {
      setVoiceStatusMessage("voice-not-at-table", true);
      return;
    }
    if (!voice.supported) {
      setVoiceStatusMessage("voice-chat-sdk-missing", true);
      return;
    }
    voiceJoinPendingRef.current = true;
    setVoiceRequestedContextId(contextId);
    setVoiceState("connecting");
    setVoiceStatusMessage("voice-chat-joining", true);
    connection?.send({
      context_id: contextId,
      scope: "table",
      type: "voice_join",
    });
  }, [connected, connection, setVoiceStatusMessage, voice, voiceCapability.enabled, voiceState]);

  const toggleVoiceMicrophone = useCallback(async () => {
    if (voiceState !== "connected") {
      setVoiceStatusMessage("voice-chat-not-connected", true);
      return;
    }
    if (voiceMicBusyRef.current) {
      return;
    }
    const requestedContextId = voiceContextRef.current.contextId;
    updateVoiceMicBusy(true);
    try {
      if (!voiceMicEnabled) {
        const granted = await ensureVoiceMicrophonePermission(true);
        if (!granted) {
          updateVoiceMicBusy(false);
          setVoiceStatusMessage("voice-chat-mic-denied", true);
          return;
        }
        if (Platform.OS === "android") {
          await androidForegroundService.sync({
            message: localization.t("background-service-voice-mic"),
            serviceType: "microphone",
            title: localization.t("background-service-title"),
          });
        }
      }
      if (
        voice.connectionState !== "connected"
        || voiceContextRef.current.contextId !== requestedContextId
      ) {
        updateVoiceMicBusy(false);
        return;
      }
      voice.setMicrophoneEnabled(!voiceMicEnabled);
    } catch {
      updateVoiceMicBusy(false);
      setVoiceStatusMessage("voice-chat-mic-denied", true);
    }
  }, [ensureVoiceMicrophonePermission, localization, setVoiceStatusMessage, updateVoiceMicBusy, voice, voiceMicEnabled, voiceState]);

  const requestAuthFlow = async (
    packet: Record<string, unknown>,
    expectedType: "register_response" | "request_password_reset_response" | "submit_reset_code_response",
  ) => {
    setAuthStatusText(localization.t("status-connecting"));
    try {
      const response = await connection?.requestTemporary(
        serverUrl,
        packet as never,
        [expectedType],
      );
      if (!response) {
        throw new Error(localization.t("auth-request-failed"));
      }

      if (expectedType === "register_response") {
        const registerResponse = response as RegisterResponsePacket;
        const text = localizeAuthResponse(
          registerResponse,
          "register",
          "auth-register-success",
          "auth-register-failed",
        );
        setAuthStatusText(text);
        announceInterfaceFeedback(text);
        if (registerResponse.status === "success") {
          setAuthMode("login");
          setPassword("");
          setRegisterConfirmPassword("");
        }
        return;
      }

      if (expectedType === "request_password_reset_response") {
        const forgotResponse = response as RequestPasswordResetResponsePacket;
        const text = localizeAuthResponse(
          forgotResponse,
          "password_reset",
          "auth-forgot-success",
          "auth-forgot-failed",
        );
        setAuthStatusText(text);
        announceInterfaceFeedback(text);
        if (forgotResponse.status === "success") {
          setResetEmail(forgotEmail.trim());
          setAuthMode("reset");
        }
        return;
      }

      const resetResponse = response as SubmitResetCodeResponsePacket;
      const text = localizeAuthResponse(
        resetResponse,
        "reset_code",
        "auth-reset-success",
        "auth-reset-failed",
      );
      setAuthStatusText(text);
      announceInterfaceFeedback(text);
      if (resetResponse.status === "success") {
        setAuthMode("login");
        if (resetResponse.username) {
          setUsername(resetResponse.username);
        }
        setPassword(resetPassword);
        setResetCode("");
        setResetConfirmPassword("");
        setResetPassword("");
      }
    } catch (error) {
      const message = error instanceof Error
        ? localizeSystemMessage(error.message, "auth-request-failed")
        : localization.t("auth-request-failed");
      setAuthStatusText(message);
      announceInterfaceFeedback(message);
    }
  };

  const submitRegistration = async () => {
    if (!username.trim() || !password || !registerEmail.trim()) {
      const message = localization.t("auth-register-required");
      setAuthStatusText(message);
      announceInterfaceFeedback(message);
      return;
    }
    if (password !== registerConfirmPassword) {
      const message = localization.t("auth-password-mismatch");
      setAuthStatusText(message);
      announceInterfaceFeedback(message);
      return;
    }
    await requestAuthFlow(
      {
        ...clientAuthMetadata(),
        email: registerEmail.trim(),
        locale: appLocale,
        password,
        type: "register",
        username: username.trim(),
      },
      "register_response",
    );
  };

  const submitForgotPassword = async () => {
    if (!forgotEmail.trim()) {
      const message = localization.t("auth-email-required");
      setAuthStatusText(message);
      announceInterfaceFeedback(message);
      return;
    }
    await requestAuthFlow(
      {
        ...clientAuthMetadata(),
        email: forgotEmail.trim(),
        locale: appLocale,
        type: "request_password_reset",
      },
      "request_password_reset_response",
    );
  };

  const submitResetPassword = async () => {
    if (!resetEmail.trim() || !resetCode.trim() || !resetPassword) {
      const message = localization.t("auth-reset-required");
      setAuthStatusText(message);
      announceInterfaceFeedback(message);
      return;
    }
    if (resetPassword !== resetConfirmPassword) {
      const message = localization.t("auth-password-mismatch");
      setAuthStatusText(message);
      announceInterfaceFeedback(message);
      return;
    }
    await requestAuthFlow(
      {
        ...clientAuthMetadata(),
        code: resetCode.trim(),
        email: resetEmail.trim(),
        locale: appLocale,
        new_password: resetPassword,
        type: "submit_reset_code",
      },
      "submit_reset_code_response",
    );
  };

  const renderGridCell = (item: FocusableMenuItem, index: number) => (
    <Pressable
      accessibilityActions={[
        { name: "activate" },
        { name: "longpress" },
      ]}
      accessibilityLabel={item.text}
      accessibilityRole="button"
      accessible
      delayLongPress={350}
      key={menuItemAccessibilityKey(menuState.menuId, item, index)}
      nativeID={menuItemAccessibilityKey(menuState.menuId, item, index)}
      onAccessibilityAction={(event) => {
        void audio.handleUserInteraction();
        focusMenuItemAt(index);
        if (event.nativeEvent.actionName === "longpress") {
          playMenuActivateSound();
          sendShiftEnter(item);
          return;
        }
        playMenuActivateSound();
        sendMenuSelection(item, index);
      }}
      onFocus={() => {
        if (!selfVoicingEnabledRef.current) focusMenuItemAt(index);
      }}
      onLongPress={() => {
        handleMenuItemLongPress(item, index);
      }}
      onPress={() => {
        handleMenuItemPress(item, index);
      }}
      ref={registerAccessibilityNode(menuItemAccessibilityKey(menuState.menuId, item, index))}
      style={[
        styles.gridMenuItem,
        index === menuState.focusIndex ? styles.gridMenuItemFocused : undefined,
        { minHeight: gridCellSize, width: gridCellSize },
      ]}
    >
      <Text style={[styles.menuText, styles.gridMenuText]}>
        {item.text}
      </Text>
    </Pressable>
  );

  const renderGridBoard = () => (
    <BoardViewport key={menuState.menuId} contentWidth={gridBoardWidth} focusKey={focusedGridKey} nodes={accessibilityNodeRefs}>
      <View collapsable={false} style={[styles.gridMenuBoard, { width: gridBoardWidth }]}>
        {gridRows.map((rowItems, rowIndex) => (
          <View key={`grid-row-${rowIndex}`} style={[styles.gridMenuRow, { gap: gridGap }]}>
            {rowItems.map((item, columnIndex) => renderGridCell(item, rowIndex * gridColumnCount + columnIndex))}
          </View>
        ))}
      </View>
    </BoardViewport>
  );

  const renderMainView = () => (
    <View style={styles.panel}>
      <Text style={styles.panelTitle}>{localization.t("mode-main")}</Text>
      <View
        onLayout={(event) => {
          const { height, width } = event.nativeEvent.layout;
          setMainPanelLayout((current) => (
            current.width === width && current.height === height
              ? current
              : { height, width }
          ));
        }}
        style={styles.mainContentArea}
      >
      {isGridMenu ? (
        renderGridBoard()
      ) : (
        <ScrollView {...menuScroll} style={styles.scrollArea}>
          {menuState.items.map((item, index) => (
            <Pressable
              accessibilityActions={[
                { name: "activate" },
                { name: "longpress" },
              ]}
              accessibilityLabel={item.text}
              accessibilityRole="button"
              accessible
              delayLongPress={350}
              key={menuItemAccessibilityKey(menuState.menuId, item, index)}
              onAccessibilityAction={(event) => {
                void audio.handleUserInteraction();
                focusMenuItemAt(index);
                if (event.nativeEvent.actionName === "longpress") {
                  playMenuActivateSound();
                  sendShiftEnter(item);
                  return;
                }
                playMenuActivateSound();
                sendMenuSelection(item, index);
              }}
              onFocus={() => {
                focusMenuItemAt(index);
              }}
              onLongPress={() => {
                handleMenuItemLongPress(item, index);
              }}
              onPress={() => {
                handleMenuItemPress(item, index);
              }}
              ref={registerAccessibilityNode(menuItemAccessibilityKey(menuState.menuId, item, index))}
              style={[
                styles.menuItem,
                index === menuState.focusIndex ? styles.menuItemFocused : undefined,
              ]}
            >
              <Text style={styles.menuText}>{item.text}</Text>
            </Pressable>
          ))}
        </ScrollView>
      )}
      </View>
    </View>
  );

  const renderChatOverlay = () => (
    <View style={styles.panel}>
      <Text style={styles.panelTitle}>{localization.t("mode-chat")}</Text>
      <ScrollView {...chatScroll} style={styles.scrollArea}>
        <Text style={styles.helpText}>{localization.t("chat-input-label")}</Text>
        <View style={chatFocusIndex === 0 ? styles.authFieldFocused : undefined}>
          <TextInput
            accessibilityLabel={localization.t("chat-input-label")}
            onChangeText={setChatDraft}
            onFocus={() => {
              handleTextInputFocus("chat:input", () => {
                setChatFocusIndex(0);
              });
            }}
            onBlur={() => {
              handleTextInputBlur("chat:input");
            }}
            onSubmitEditing={submitChat}
            placeholder={localization.t("chat-placeholder")}
            placeholderTextColor="#b8c7d1"
            ref={registerAccessibilityNode("chat:input", chatInputRef)}
            showSoftInputOnFocus
            style={styles.input}
            value={chatDraft}
          />
        </View>
        <View style={styles.row}>
          <Pressable
            accessibilityLabel={localization.t("chat-send-button")}
            accessibilityRole="button"
            accessible
            onPress={() => {
              void audio.handleUserInteraction();
              submitChat();
            }}
            onFocus={() => {
              markNativeScreenReaderInteraction("chat:send");
              if (sendChatFocusIndex >= 0) {
                setChatFocusIndex(sendChatFocusIndex);
              }
            }}
            ref={registerAccessibilityNode("chat:send")}
            style={[
              styles.button,
              styles.chatActionButton,
              chatFocusIndex === sendChatFocusIndex ? styles.menuItemFocused : undefined,
            ]}
          >
            <Text style={styles.buttonText}>{localization.t("chat-send-button")}</Text>
          </Pressable>
          {voiceState === "connected" ? (
            <Pressable
              accessibilityLabel={localization.t("voice-chat-leave")}
              accessibilityRole="button"
              accessible
              onPress={() => {
                void audio.handleUserInteraction();
                leaveVoiceChat();
              }}
              onFocus={() => {
                markNativeScreenReaderInteraction("chat:voiceLeave");
                if (voiceLeaveChatFocusIndex >= 0) {
                  setChatFocusIndex(voiceLeaveChatFocusIndex);
                }
              }}
              ref={registerAccessibilityNode("chat:voiceLeave")}
              style={[
                styles.buttonSecondary,
                styles.chatActionButton,
                chatFocusIndex === voiceLeaveChatFocusIndex ? styles.menuItemFocused : undefined,
              ]}
            >
              <Text style={styles.buttonText}>{localization.t("voice-chat-leave")}</Text>
            </Pressable>
          ) : (
            <Pressable
              accessibilityLabel={
                voiceState === "connecting"
                  ? localization.t("voice-chat-joining")
                  : localization.t("voice-chat-join")
              }
              accessibilityRole="button"
              accessibilityState={{ disabled: voiceState === "connecting" }}
              accessible
              disabled={voiceState === "connecting"}
              onPress={() => {
                void audio.handleUserInteraction();
                joinVoiceChat();
              }}
              onFocus={() => {
                markNativeScreenReaderInteraction("chat:voiceJoin");
                if (voiceJoinChatFocusIndex >= 0) {
                  setChatFocusIndex(voiceJoinChatFocusIndex);
                }
              }}
              ref={registerAccessibilityNode("chat:voiceJoin")}
              style={[
                styles.buttonSecondary,
                styles.chatActionButton,
                chatFocusIndex === voiceJoinChatFocusIndex ? styles.menuItemFocused : undefined,
                voiceState === "connecting" ? styles.buttonDisabled : undefined,
              ]}
            >
              <Text style={styles.buttonText}>
                {voiceState === "connecting"
                  ? localization.t("voice-chat-joining")
                  : localization.t("voice-chat-join")}
              </Text>
            </Pressable>
          )}
          {voiceState === "connected" ? (
            <Pressable
              accessibilityLabel={localization.t(
                voiceMicEnabled ? "voice-chat-turn-off-mic" : "voice-chat-turn-on-mic",
              )}
              accessibilityRole="button"
              accessibilityState={{ disabled: voiceMicBusy, selected: voiceMicEnabled }}
              accessible
              disabled={voiceMicBusy}
              onPress={() => {
                void audio.handleUserInteraction();
                void toggleVoiceMicrophone();
              }}
              onFocus={() => {
                markNativeScreenReaderInteraction("chat:voiceMic");
                if (voiceMicChatFocusIndex >= 0) {
                  setChatFocusIndex(voiceMicChatFocusIndex);
                }
              }}
              ref={registerAccessibilityNode("chat:voiceMic")}
              style={[
                styles.buttonSecondary,
                styles.chatActionButton,
                chatFocusIndex === voiceMicChatFocusIndex ? styles.menuItemFocused : undefined,
                voiceMicBusy ? styles.buttonDisabled : undefined,
              ]}
            >
              <Text style={styles.buttonText}>
                {localization.t(voiceMicEnabled ? "voice-chat-turn-off-mic" : "voice-chat-turn-on-mic")}
              </Text>
            </Pressable>
          ) : null}
          <Pressable
            accessibilityLabel={localization.t("chat-close-button")}
            accessibilityRole="button"
            accessible
            onPress={() => {
              void audio.handleUserInteraction();
              closeOverlay();
            }}
            onFocus={() => {
              markNativeScreenReaderInteraction("chat:close");
              if (closeChatFocusIndex >= 0) {
                setChatFocusIndex(closeChatFocusIndex);
              }
            }}
            ref={registerAccessibilityNode("chat:close")}
            style={[
              styles.buttonSecondary,
              styles.chatActionButton,
              chatFocusIndex === closeChatFocusIndex ? styles.menuItemFocused : undefined,
            ]}
          >
            <Text style={styles.buttonText}>{localization.t("chat-close-button")}</Text>
          </Pressable>
        </View>
        <Text
          accessibilityLabel={voiceStatusText || localization.t("voice-chat-not-connected")}
          accessible
          style={styles.helpText}
        >
          {voiceStatusText || localization.t("voice-chat-not-connected")}
        </Text>
        {chatMessages.map((item, index) => (
          <Pressable
            accessibilityLabel={item.text}
            accessibilityRole="button"
            accessible
            key={item.id}
            onFocus={() => {
              markNativeScreenReaderInteraction(`chat:${item.id}`);
              setChatFocusIndex(chatMessageFocusOffset + index);
            }}
            onPress={() => {
              markNativeScreenReaderInteraction(`chat:${item.id}`);
              setChatFocusIndex(chatMessageFocusOffset + index);
              speakUserFocus(item.text);
            }}
            ref={registerAccessibilityNode(`chat:${item.id}`)}
            style={[
              styles.menuItem,
              chatFocusIndex === chatMessageFocusOffset + index ? styles.menuItemFocused : undefined,
            ]}
          >
            <Text style={styles.historyText}>{item.text}</Text>
          </Pressable>
        ))}
        {chatMessages.length === 0 ? (
          <Text style={styles.historyText}>{localization.t("chat-empty")}</Text>
        ) : null}
      </ScrollView>
    </View>
  );

  const renderHistoryOverlay = () => (
    <View style={styles.panel}>
      <Text style={styles.panelTitle}>{localization.t("mode-history")}</Text>
      <ScrollView {...historyScroll} style={styles.scrollArea}>
        <View style={styles.historyControls}>
          <Pressable
            accessibilityLabel={historyBufferControlText}
            accessibilityRole="button"
            aria-expanded={dialogState?.id === "history-buffer-selection"}
            accessible
            onFocus={() => {
              markNativeScreenReaderInteraction("history:buffer");
              setHistoryIndex(historyBufferFocusIndex);
            }}
            onPress={() => {
              markNativeScreenReaderInteraction("history:buffer");
              void audio.handleUserInteraction();
              setHistoryIndex(historyBufferFocusIndex);
              playMenuActivateSound();
              openHistoryBufferMenu();
            }}
            ref={registerAccessibilityNode("history:buffer")}
            style={[
              styles.buttonSecondary,
              styles.historyControlButton,
              historyIndex === historyBufferFocusIndex ? styles.menuItemFocused : undefined,
            ]}
          >
            <Text style={styles.buttonText}>{historyBufferControlText}</Text>
          </Pressable>
          <Pressable
            accessibilityLabel={historyMuteControlText}
            accessibilityRole="switch"
            aria-checked={historyBufferMuted}
            accessible
            onFocus={() => {
              markNativeScreenReaderInteraction("history:mute");
              setHistoryIndex(historyMuteFocusIndex);
            }}
            onPress={() => {
              markNativeScreenReaderInteraction("history:mute");
              void audio.handleUserInteraction();
              setHistoryIndex(historyMuteFocusIndex);
              playMenuActivateSound();
              toggleHistoryBufferMute();
            }}
            ref={registerAccessibilityNode("history:mute")}
            style={[
              historyBufferMuted ? styles.button : styles.buttonSecondary,
              styles.historyControlButton,
              historyIndex === historyMuteFocusIndex ? styles.menuItemFocused : undefined,
            ]}
          >
            <Text style={styles.buttonText}>{historyMuteControlText}</Text>
          </Pressable>
        </View>
        {historyMessages.map((item, index) => (
          <Pressable
            accessibilityLabel={item.text}
            accessibilityRole="button"
            accessible
            key={item.id}
            onFocus={() => {
              markNativeScreenReaderInteraction(`history:${item.id}`);
              setHistoryIndex(historyMessageFocusOffset + index);
            }}
            onPress={() => {
              markNativeScreenReaderInteraction(`history:${item.id}`);
              setHistoryIndex(historyMessageFocusOffset + index);
              speakUserFocus(item.text);
            }}
            ref={registerAccessibilityNode(`history:${item.id}`)}
            style={[
              styles.menuItem,
              historyIndex === historyMessageFocusOffset + index ? styles.menuItemFocused : undefined,
            ]}
          >
            <Text style={styles.historyText}>{item.text}</Text>
          </Pressable>
        ))}
        {historyMessages.length === 0 ? (
          <Text
            accessibilityLabel={historyEmptyText}
            accessible
            ref={registerAccessibilityNode("history:empty")}
            style={styles.historyText}
          >
            {historyEmptyText}
          </Text>
        ) : null}
      </ScrollView>
    </View>
  );

  const renderShortcutsOverlay = () => (
    <View style={styles.panel}>
      <Text style={styles.panelTitle}>{localization.t("shortcuts-title")}</Text>
      <ScrollView {...shortcutScroll} style={styles.scrollArea}>
        {shortcutItems.map((item, index) => (
          <Pressable
            accessibilityLabel={item.text}
            accessibilityRole="button"
            accessible
            key={item.id}
            onFocus={() => {
              markNativeScreenReaderInteraction(`shortcut:${item.id}`);
              setShortcutFocusIndex(index);
            }}
            onPress={() => {
              markNativeScreenReaderInteraction(`shortcut:${item.id}`);
              void audio.handleUserInteraction();
              setShortcutFocusIndex(index);
              playMenuActivateSound();
              activateShortcut(item);
            }}
            ref={registerAccessibilityNode(`shortcut:${item.id}`)}
            style={[
              styles.menuItem,
              index === shortcutFocusIndex ? styles.menuItemFocused : undefined,
            ]}
          >
            <Text style={styles.menuText}>{item.text}</Text>
          </Pressable>
        ))}
      </ScrollView>
      {currentMusic ? (
        <Text style={styles.helpText}>{localization.t("current-music-track", { value: currentMusic })}</Text>
      ) : null}
      {currentAmbience ? (
        <Text style={styles.helpText}>{localization.t("current-ambience-track", { value: currentAmbience })}</Text>
      ) : null}
    </View>
  );

  const renderDialogOverlay = () => {
    if (!dialogState) {
      return null;
    }

    return (
      <View accessibilityViewIsModal style={styles.inputOverlayScreen}>
        <ScrollView {...dialogScroll} style={styles.dialogScroll} contentContainerStyle={styles.dialogCard}>
          <Text accessibilityRole="header" style={styles.panelTitle}>{dialogState.title}</Text>
          {dialogState.message ? <Text style={styles.dialogMessage}>{dialogState.message}</Text> : null}
          <View style={styles.dialogButtons}>
            {dialogState.buttons.map((button, index) => (
              <Pressable
                accessibilityLabel={button.text}
                accessibilityRole={button.checked === undefined ? "button" : "radio"}
                aria-checked={button.checked}
                accessible
                key={`${dialogState.id}-${button.id}`}
                onFocus={() => {
                  focusDialogButton(dialogState, index);
                }}
                onPress={() => {
                  void audio.handleUserInteraction();
                  playMenuActivateSound();
                  if (dialogStateRef.current?.buttons === dialogState.buttons) button.onPress();
                }}
                ref={registerAccessibilityNode(`dialog:${dialogState.id}:${button.id}`)}
                style={[
                  button.variant === "danger"
                    ? styles.buttonDanger
                    : button.variant === "secondary"
                      ? styles.buttonSecondary
                      : styles.button,
                  index === dialogState.focusIndex ? styles.authFocused : undefined,
                ]}
              >
                <Text style={styles.buttonText}>{button.text}</Text>
              </Pressable>
            ))}
          </View>
        </ScrollView>
      </View>
    );
  };

  const renderOverlay = () => {
    if (mode === "chat") {
      return renderChatOverlay();
    }
    if (mode === "history") {
      return renderHistoryOverlay();
    }
    if (mode === "shortcuts") {
      return renderShortcutsOverlay();
    }
    return renderMainView();
  };

  const renderAuthSwitcher = () => (
    <View accessibilityRole="tablist" style={styles.authTabs}>
      {(["login", "register", "forgot"] as const).map((candidate) => (
        <Pressable
          accessibilityLabel={localization.t(`auth-mode-${candidate}`)}
          accessibilityRole="tab"
          aria-selected={authMode === candidate}
          accessible
          key={candidate}
          onFocus={() => {
            focusAuthItemById(`tab-${candidate}`);
          }}
          onPress={() => {
            void audio.handleUserInteraction();
            setAuthMode(candidate);
            setAuthStatusText("");
          }}
          ref={registerAccessibilityNode(`auth:tab-${candidate}`)}
          style={[
            styles.authTab,
            authMode === candidate ? styles.authTabActive : undefined,
            isAuthFocused(`tab-${candidate}`) ? styles.authFocused : undefined,
          ]}
        >
          <Text style={styles.buttonText}>{localization.t(`auth-mode-${candidate}`)}</Text>
        </Pressable>
      ))}
          {authMode === "reset" ? (
        <View style={[styles.authTab, styles.authTabActive]}>
          <Text style={styles.buttonText}>{localization.t("auth-mode-reset")}</Text>
        </View>
      ) : null}
    </View>
  );

  const renderLanguageButton = () => (
    <Pressable
      accessibilityLabel={`${localization.t("locale")}: ${localization.getLocaleLabel(appLocale)}`}
      accessibilityRole="button"
      aria-disabled={!storageReady}
      aria-expanded={dialogState?.id === "language-selection"}
      accessible
      disabled={!storageReady}
      onFocus={() => focusAuthItemById("locale")}
      onPress={() => {
        void audio.handleUserInteraction();
        focusAuthItemById("locale");
        playMenuActivateSound();
        openLanguageMenu();
      }}
      ref={registerAccessibilityNode("auth:locale")}
      style={[styles.buttonSecondary, isAuthFocused("locale") ? styles.authFocused : undefined]}
    >
      <Text style={styles.buttonText}>{localization.t("locale")}: {localization.getLocaleLabel(appLocale)}</Text>
    </Pressable>
  );

  const renderAuthCard = () => (
    <View style={styles.loginCard}>
      <Text accessibilityRole="header" style={styles.panelTitle}>{localization.t("app-title")}</Text>
      {renderLanguageButton()}
      {renderAuthSwitcher()}

      {authMode === "login" ? (
        <>
          <View style={[styles.authField, isAuthFocused("field-username") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("username")}
              autoCapitalize="none"
              onChangeText={setUsername}
              onFocus={() => {
                handleTextInputFocus("auth:field-username", () => {
                  focusAuthItemById("field-username");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-username");
              }}
              placeholder={localization.t("username")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode("auth:field-username", usernameInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={username}
            />
          </View>
          <View style={[styles.authField, isAuthFocused("field-password") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("password")}
              onChangeText={setPassword}
              onFocus={() => {
                handleTextInputFocus("auth:field-password", () => {
                  focusAuthItemById("field-password");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-password");
              }}
              placeholder={localization.t("password")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode("auth:field-password", passwordInputRef)}
              secureTextEntry
              showSoftInputOnFocus
              style={styles.input}
              value={password}
            />
          </View>
          <View style={styles.row}>
            <Pressable
              accessibilityLabel={localization.t("auth-login-submit")}
              accessibilityRole="button"
              accessible
              onFocus={() => {
                focusAuthItemById("button-connect");
              }}
              onPress={() => {
                void audio.handleUserInteraction();
                connect();
              }}
              ref={registerAccessibilityNode("auth:button-connect")}
              style={[styles.button, isAuthFocused("button-connect") ? styles.authFocused : undefined]}
            >
              <Text style={styles.buttonText}>{localization.t("auth-login-submit")}</Text>
            </Pressable>
          </View>
          {username || password ? (
            <View style={styles.row}>
              <Pressable
                accessibilityLabel={localization.t("auth-clear-account")}
                accessibilityRole="button"
                accessible
                onFocus={() => {
                  focusAuthItemById("button-clear-account");
                }}
                onPress={() => {
                  void audio.handleUserInteraction();
                  void clearSavedAccount();
                }}
                ref={registerAccessibilityNode("auth:button-clear-account")}
                style={[
                  styles.buttonSecondary,
                  isAuthFocused("button-clear-account") ? styles.authFocused : undefined,
                ]}
              >
                <Text style={styles.buttonText}>{localization.t("auth-clear-account")}</Text>
              </Pressable>
            </View>
          ) : null}
        </>
      ) : null}

      {authMode === "register" ? (
        <>
          <View style={[styles.authField, isAuthFocused("field-username") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("username")}
              autoCapitalize="none"
              onChangeText={setUsername}
              onFocus={() => {
                handleTextInputFocus("auth:field-username", () => {
                  focusAuthItemById("field-username");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-username");
              }}
              placeholder={localization.t("username")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode("auth:field-username", usernameInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={username}
            />
          </View>
          <View style={[styles.authField, isAuthFocused("field-register-email") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("auth-email")}
              autoCapitalize="none"
              keyboardType="email-address"
              onChangeText={setRegisterEmail}
              onFocus={() => {
                handleTextInputFocus("auth:field-register-email", () => {
                  focusAuthItemById("field-register-email");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-register-email");
              }}
              placeholder={localization.t("auth-email")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode("auth:field-register-email", registerEmailInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={registerEmail}
            />
          </View>
          <View style={[styles.authField, isAuthFocused("field-password") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("password")}
              onChangeText={setPassword}
              onFocus={() => {
                handleTextInputFocus("auth:field-password", () => {
                  focusAuthItemById("field-password");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-password");
              }}
              placeholder={localization.t("password")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode("auth:field-password", passwordInputRef)}
              secureTextEntry
              showSoftInputOnFocus
              style={styles.input}
              value={password}
            />
          </View>
          <View style={[styles.authField, isAuthFocused("field-register-confirm-password") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("auth-confirm-password")}
              onChangeText={setRegisterConfirmPassword}
              onFocus={() => {
                handleTextInputFocus("auth:field-register-confirm-password", () => {
                  focusAuthItemById("field-register-confirm-password");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-register-confirm-password");
              }}
              placeholder={localization.t("auth-confirm-password")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode(
                "auth:field-register-confirm-password",
                registerConfirmPasswordInputRef,
              )}
              secureTextEntry
              showSoftInputOnFocus
              style={styles.input}
              value={registerConfirmPassword}
            />
          </View>
          <Pressable
            accessibilityLabel={localization.t("auth-register-submit")}
            accessibilityRole="button"
            accessible
            onFocus={() => {
              focusAuthItemById("button-register");
            }}
            onPress={() => {
              void audio.handleUserInteraction();
              void submitRegistration();
            }}
            ref={registerAccessibilityNode("auth:button-register")}
            style={[styles.button, isAuthFocused("button-register") ? styles.authFocused : undefined]}
          >
            <Text style={styles.buttonText}>{localization.t("auth-register-submit")}</Text>
          </Pressable>
        </>
      ) : null}

      {authMode === "forgot" ? (
        <>
          <View style={[styles.authField, isAuthFocused("field-forgot-email") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("auth-email")}
              autoCapitalize="none"
              keyboardType="email-address"
              onChangeText={setForgotEmail}
              onFocus={() => {
                handleTextInputFocus("auth:field-forgot-email", () => {
                  focusAuthItemById("field-forgot-email");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-forgot-email");
              }}
              placeholder={localization.t("auth-email")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode("auth:field-forgot-email", forgotEmailInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={forgotEmail}
            />
          </View>
          <Pressable
            accessibilityLabel={localization.t("auth-forgot-submit")}
            accessibilityRole="button"
            accessible
            onFocus={() => {
              focusAuthItemById("button-forgot");
            }}
            onPress={() => {
              void audio.handleUserInteraction();
              void submitForgotPassword();
            }}
            ref={registerAccessibilityNode("auth:button-forgot")}
            style={[styles.button, isAuthFocused("button-forgot") ? styles.authFocused : undefined]}
          >
            <Text style={styles.buttonText}>{localization.t("auth-forgot-submit")}</Text>
          </Pressable>
        </>
      ) : null}

      {authMode === "reset" ? (
        <>
          <View style={[styles.authField, isAuthFocused("field-reset-email") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("auth-email")}
              autoCapitalize="none"
              keyboardType="email-address"
              onChangeText={setResetEmail}
              onFocus={() => {
                handleTextInputFocus("auth:field-reset-email", () => {
                  focusAuthItemById("field-reset-email");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-reset-email");
              }}
              placeholder={localization.t("auth-email")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode("auth:field-reset-email", resetEmailInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={resetEmail}
            />
          </View>
          <View style={[styles.authField, isAuthFocused("field-reset-code") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("auth-reset-code")}
              autoCapitalize="characters"
              onChangeText={setResetCode}
              onFocus={() => {
                handleTextInputFocus("auth:field-reset-code", () => {
                  focusAuthItemById("field-reset-code");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-reset-code");
              }}
              placeholder={localization.t("auth-reset-code")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode("auth:field-reset-code", resetCodeInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={resetCode}
            />
          </View>
          <View style={[styles.authField, isAuthFocused("field-reset-password") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("auth-new-password")}
              onChangeText={setResetPassword}
              onFocus={() => {
                handleTextInputFocus("auth:field-reset-password", () => {
                  focusAuthItemById("field-reset-password");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-reset-password");
              }}
              placeholder={localization.t("auth-new-password")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode("auth:field-reset-password", resetPasswordInputRef)}
              secureTextEntry
              showSoftInputOnFocus
              style={styles.input}
              value={resetPassword}
            />
          </View>
          <View style={[styles.authField, isAuthFocused("field-reset-confirm-password") ? styles.authFieldFocused : undefined]}>
            <TextInput
              accessibilityLabel={localization.t("auth-confirm-password")}
              onChangeText={setResetConfirmPassword}
              onFocus={() => {
                handleTextInputFocus("auth:field-reset-confirm-password", () => {
                  focusAuthItemById("field-reset-confirm-password");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-reset-confirm-password");
              }}
              placeholder={localization.t("auth-confirm-password")}
              placeholderTextColor="#b8c7d1"
              ref={registerAccessibilityNode(
                "auth:field-reset-confirm-password",
                resetConfirmPasswordInputRef,
              )}
              secureTextEntry
              showSoftInputOnFocus
              style={styles.input}
              value={resetConfirmPassword}
            />
          </View>
          <Pressable
            accessibilityLabel={localization.t("auth-reset-submit")}
            accessibilityRole="button"
            accessible
            onFocus={() => {
              focusAuthItemById("button-reset");
            }}
            onPress={() => {
              void audio.handleUserInteraction();
              void submitResetPassword();
            }}
            ref={registerAccessibilityNode("auth:button-reset")}
            style={[styles.button, isAuthFocused("button-reset") ? styles.authFocused : undefined]}
          >
            <Text style={styles.buttonText}>{localization.t("auth-reset-submit")}</Text>
          </Pressable>
        </>
      ) : null}

      {authStatusText ? <Text style={styles.helpText}>{authStatusText}</Text> : null}
      <View style={styles.row}>
        <Pressable
          accessibilityLabel={localization.t("client-help")}
          accessibilityRole="button"
          accessible
          onFocus={() => {
            focusAuthItemById("help");
          }}
          onPress={() => {
            void audio.handleUserInteraction();
            focusAuthItemById("help");
            openClientHelp("auth:help");
          }}
          ref={registerAccessibilityNode("auth:help")}
          style={[styles.buttonSecondary, isAuthFocused("help") ? styles.authFocused : undefined]}
        >
          <Text style={styles.buttonText}>
            {localization.t("client-help")}
          </Text>
        </Pressable>
        <Pressable
          accessibilityLabel={localization.t("auth-exit")}
          accessibilityRole="button"
          accessible
          onFocus={() => {
            focusAuthItemById("button-exit");
          }}
          onPress={() => {
            void audio.handleUserInteraction();
            exitApplication();
          }}
          ref={registerAccessibilityNode("auth:button-exit")}
          style={[styles.buttonDanger, isAuthFocused("button-exit") ? styles.authFocused : undefined]}
        >
          <Text style={styles.buttonText}>{localization.t("auth-exit")}</Text>
        </Pressable>
      </View>
    </View>
  );

  const renderScreenReaderOnlyControls = () => {
    if (Platform.OS === "web" && !screenReaderEnabled && !WEB_SCREEN_READER_SUPPORT) {
      return null;
    }

    return (
      <Pressable
        accessibilityLabel={localization.t(
          selfVoicingEnabled ? "sv-toggle-button-off" : "sv-toggle-button-on",
        )}
        accessibilityRole="button"
        accessibilityElementsHidden={false}
        accessible
        collapsable={false}
        focusable
        importantForAccessibility="yes"
        onFocus={() => {
          markNativeScreenReaderInteraction("screen-reader:sv-toggle");
        }}
        onPress={() => {
          void audio.handleUserInteraction();
          toggleSelfVoicing();
        }}
        nativeID="playaural-sv-toggle"
        ref={registerAccessibilityNode("screen-reader:sv-toggle")}
        style={Platform.OS === "web" ? styles.screenReaderOnly : styles.nativeScreenReaderOnlyControl}
      >
        <Text style={styles.nativeSelfVoicingToggleText}>
          {localization.t(selfVoicingEnabled ? "sv-toggle-button-off" : "sv-toggle-button-on")}
        </Text>
      </Pressable>
    );
  };

  const renderNativeNavigationTabs = () => {
    if (!showNativeNavigationTabs) {
      return null;
    }

    const tabs: Array<{ id: AppMode; label: string }> = [
      { id: "main", label: localization.t("mode-main") },
      { id: "chat", label: localization.t("mode-chat") },
      { id: "history", label: localization.t("mode-history") },
      { id: "shortcuts", label: localization.t("mode-shortcuts") },
    ];

    return (
      <View
        accessibilityLabel={localization.t("native-tabs-label")}
        accessibilityRole="tablist"
        style={styles.nativeTabBar}
      >
        {tabs.map((tab) => (
          <Pressable
            accessibilityLabel={tab.label}
            accessibilityRole="tab"
            aria-selected={mode === tab.id}
            accessible
            key={tab.id}
            onFocus={() => {
              markNativeScreenReaderInteraction(`tab:${tab.id}`);
            }}
            onPress={() => {
              openNativeTab(tab.id);
            }}
            style={[
              styles.nativeTab,
              mode === tab.id ? styles.nativeTabActive : undefined,
            ]}
          >
            <Text style={styles.nativeTabText}>{tab.label}</Text>
          </Pressable>
        ))}
      </View>
    );
  };

  return (
    <SafeAreaView
      style={styles.safeArea}
    >
      <AccessibilityOrderedView
        experimental_accessibilityOrder={["playaural-sv-toggle", "playaural-content-root"]}
        style={styles.rootAccessibilityContainer}
      >
        {renderScreenReaderOnlyControls()}
        <StatusBar style="light" />
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          nativeID="playaural-content-root"
          style={styles.container}
          {...gestures.panHandlers}
        >
        {dialogState ? renderDialogOverlay() : inputState ? (
          <View style={styles.inputOverlayScreen}>
            <ScrollView {...inputScroll} style={styles.dialogScroll} contentContainerStyle={styles.inputOverlayCard}>
              <Text style={styles.panelTitle}>{inputState.prompt}</Text>
              <View
                style={[
                  styles.inputOverlayFocusRing,
                  inputOverlayFocus === 0 ? styles.authFieldFocused : undefined,
                ]}
              >
                <TextInput
                  accessibilityLabel={inputState.prompt}
                  editable={!inputState.readOnly}
                  maxLength={inputState.maxLength}
                  multiline={inputState.multiline}
                  onChangeText={setInputValue}
                  onFocus={() => {
                    handleTextInputFocus("input:field", () => {
                      setInputOverlayFocus(0);
                    });
                  }}
                  onBlur={() => {
                    handleTextInputBlur("input:field");
                  }}
                  placeholder={inputState.prompt}
                  placeholderTextColor="#b8c7d1"
                  ref={registerAccessibilityNode("input:field", inputOverlayInputRef)}
                  selectTextOnFocus
                  showSoftInputOnFocus={!inputState.readOnly}
                  style={[styles.input, inputState.multiline ? styles.multilineInput : undefined]}
                  value={inputValue}
                />
              </View>
              <Pressable
                accessibilityLabel={inputOverlayButtonText}
                accessibilityRole="button"
                accessible
                onFocus={() => {
                  markNativeScreenReaderInteraction("input:action");
                  setInputOverlayFocus(1);
                }}
                onPress={() => {
                  void audio.handleUserInteraction();
                  submitInputOverlay();
                }}
                ref={registerAccessibilityNode("input:action")}
                style={[styles.button, inputOverlayFocus === 1 ? styles.authFocused : undefined]}
              >
                <Text style={styles.buttonText}>{inputOverlayButtonText}</Text>
              </Pressable>
            </ScrollView>
          </View>
        ) : (
          <>
            {renderNativeNavigationTabs()}
            {!connected ? (
              <ScrollView {...authScroll} style={styles.scrollArea} contentContainerStyle={styles.landingContent}>
                {renderAuthCard()}
                <Text style={styles.subtitle}>{statusText}</Text>
              </ScrollView>
            ) : renderOverlay()}

            {connected ? (
              <View style={styles.footer}>
                <Text style={[styles.subtitle, styles.footerStatus]}>{statusText}</Text>
                <Pressable
                  accessibilityLabel={localization.t("client-help")}
                  accessibilityRole="button"
                  onFocus={() => markNativeScreenReaderInteraction("client:help")}
                  onPress={() => openClientHelp("client:help")}
                  ref={registerAccessibilityNode("client:help")}
                  style={styles.buttonSecondary}
                >
                  <Text style={styles.buttonText}>{localization.t("client-help")}</Text>
                </Pressable>
              </View>
            ) : null}
          </>
        )}
        {Platform.OS === "web" ? (
          <Text
            aria-live="polite"
            key={`screen-reader-announcement-${screenReaderAnnouncement.id}`}
            style={styles.screenReaderOnly}
          >
            {screenReaderAnnouncement.text}
          </Text>
        ) : null}
        </KeyboardAvoidingView>
      </AccessibilityOrderedView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: "#0b0f14",
    flex: 1,
  },
  rootAccessibilityContainer: {
    flex: 1,
  },
  container: {
    flex: 1,
    gap: 12,
    padding: 16,
  },
  screenReaderOnly: {
    height: 1,
    left: -10000,
    opacity: 0.01,
    overflow: "hidden",
    position: "absolute",
    top: 0,
    width: 1,
  },
  nativeScreenReaderOnlyControl: {
    alignSelf: "stretch",
    backgroundColor: "#173044",
    borderColor: "#8fe5ff",
    borderRadius: 10,
    borderWidth: 2,
    justifyContent: "center",
    marginBottom: 4,
    marginHorizontal: 16,
    marginTop: 8,
    minHeight: 48,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  nativeSelfVoicingToggleText: {
    color: "#f6f7fb",
    fontSize: 16,
    fontWeight: "700",
    lineHeight: 22,
    textAlign: "center",
  },
  subtitle: {
    color: "#d0dae2",
    fontSize: 15,
    lineHeight: 21,
  },
  loginCard: {
    backgroundColor: "#18212b",
    borderColor: "#3a4a5a",
    borderRadius: 14,
    borderWidth: 1,
    gap: 10,
    padding: 14,
    width: "100%",
    maxWidth: 640,
    alignSelf: "center",
  },
  landingContent: {
    gap: 12,
    paddingBottom: 12,
  },
  authTabs: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  authTab: {
    backgroundColor: "#32414d",
    borderRadius: 10,
    borderWidth: 2,
    borderColor: "transparent",
    minHeight: 48,
    flexShrink: 1,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  authTabActive: {
    backgroundColor: "#3567e3",
  },
  authFocused: {
    borderColor: "#8fe5ff",
  },
  authFieldFocused: {
    borderColor: "#8fe5ff",
    borderRadius: 12,
    borderWidth: 3,
    padding: 2,
  },
  authField: {
    borderColor: "transparent",
    borderRadius: 12,
    borderWidth: 3,
    padding: 2,
  },
  input: {
    backgroundColor: "#0f141a",
    borderColor: "#5a6b7b",
    borderRadius: 10,
    borderWidth: 2,
    color: "#f6f7fb",
    fontSize: 16,
    lineHeight: 22,
    minHeight: 48,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  multilineInput: {
    minHeight: 120,
    textAlignVertical: "top",
  },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  button: {
    backgroundColor: "#3567e3",
    borderRadius: 10,
    borderWidth: 2,
    borderColor: "transparent",
    flexShrink: 1,
    minHeight: 48,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  chatActionButton: {
    flexShrink: 1,
  },
  buttonDisabled: {
    opacity: 0.55,
  },
  buttonSecondary: {
    backgroundColor: "#32414d",
    borderRadius: 10,
    borderWidth: 2,
    borderColor: "transparent",
    flexShrink: 1,
    minHeight: 48,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  buttonDanger: {
    backgroundColor: "#a33b36",
    borderRadius: 10,
    borderWidth: 2,
    borderColor: "transparent",
    flexShrink: 1,
    minHeight: 48,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  buttonText: {
    color: "#f6f7fb",
    fontSize: 16,
    fontWeight: "600",
    lineHeight: 22,
  },
  panel: {
    backgroundColor: "#18212b",
    borderColor: "#3a4a5a",
    borderRadius: 14,
    borderWidth: 1,
    flex: 1,
    padding: 14,
  },
  panelTitle: {
    color: "#f6f7fb",
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 10,
  },
  mainContentArea: {
    flex: 1,
    overflow: "hidden",
  },
  scrollArea: {
    flex: 1,
  },
  historyControls: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    marginBottom: 10,
  },
  historyControlButton: {
    flexGrow: 1,
    flexBasis: 140,
  },
  gridMenuBoard: {
    gap: 8,
    alignItems: "stretch",
    justifyContent: "flex-start",
    overflow: "hidden",
  },
  menuItem: {
    backgroundColor: "#0f141a",
    borderColor: "#3a4a5a",
    borderRadius: 12,
    borderWidth: 2,
    marginBottom: 8,
    minHeight: 48,
    padding: 12,
  },
  gridMenuItem: {
    minWidth: 72,
    padding: 4,
    alignItems: "center",
    backgroundColor: "#0f141a",
    borderColor: "#3a4a5a",
    borderWidth: 2,
    justifyContent: "center",
    marginBottom: 0,
    overflow: "hidden",
  },
  gridMenuItemFocused: {
    backgroundColor: "#173044",
    borderColor: "#8fe5ff",
  },
  gridMenuRow: {
    flexDirection: "row",
    overflow: "hidden",
  },
  menuItemFocused: {
    borderColor: "#8fe5ff",
    backgroundColor: "#173044",
  },
  menuText: {
    color: "#f6f7fb",
    fontSize: 16,
    lineHeight: 22,
  },
  gridMenuText: {
    includeFontPadding: false,
    textAlign: "center",
  },
  historyText: {
    color: "#e4edf4",
    fontSize: 16,
    lineHeight: 22,
    marginBottom: 8,
  },
  helpText: {
    color: "#c6d3dc",
    fontSize: 14,
    lineHeight: 20,
    marginTop: 6,
  },
  inputOverlayScreen: {
    alignItems: "center",
    flex: 1,
    justifyContent: "center",
  },
  inputOverlayCard: {
    backgroundColor: "#18212b",
    borderColor: "#3567e3",
    borderRadius: 14,
    borderWidth: 2,
    gap: 12,
    maxWidth: 640,
    padding: 16,
    width: "100%",
  },
  dialogCard: {
    backgroundColor: "#18212b",
    borderColor: "#3567e3",
    borderRadius: 14,
    borderWidth: 2,
    gap: 14,
    maxWidth: 640,
    padding: 16,
    width: "100%",
  },
  dialogScroll: {
    flexGrow: 0,
    maxWidth: 640,
    width: "100%",
  },
  dialogMessage: {
    color: "#d8e0e6",
    fontSize: 16,
    lineHeight: 22,
  },
  dialogButtons: {
    gap: 10,
  },
  inputOverlayFocusRing: {
    borderRadius: 12,
    padding: 2,
  },
  footer: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  footerStatus: {
    flexGrow: 1,
    flexShrink: 1,
  },
  nativeTabBar: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  nativeTab: {
    backgroundColor: "#32414d",
    borderColor: "#3a4a5a",
    borderRadius: 8,
    borderWidth: 2,
    flexBasis: "auto",
    flexGrow: 1,
    flexShrink: 1,
    maxWidth: "100%",
    minHeight: 48,
    paddingHorizontal: 8,
    paddingVertical: 10,
  },
  nativeTabActive: {
    backgroundColor: "#3567e3",
    borderColor: "#8fe5ff",
  },
  nativeTabText: {
    color: "#f6f7fb",
    fontSize: 14,
    fontWeight: "600",
    textAlign: "center",
  },
});
