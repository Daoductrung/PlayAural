import { StatusBar } from "expo-status-bar";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Audio as ExpoAudio } from "expo-av";
import * as SecureStore from "expo-secure-store";
import { useCallback, useEffect, useMemo, useRef, useState, type MutableRefObject } from "react";
import {
  AccessibilityInfo,
  BackHandler,
  Keyboard,
  KeyboardAvoidingView,
  Linking,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  findNodeHandle,
} from "react-native";

import { MobileAudioManager } from "../audio/MobileAudioManager";
import { useSelfVoicingGestures } from "../gestures/useSelfVoicingGestures";
import { bundledSoundVersion } from "../generated/soundManifest";
import { MobileLocalization } from "../i18n/localization";
import { PlayAuralConnection } from "../network/PlayAuralConnection";
import type {
  AuthorizeSuccessPacket,
  ChatPacket,
  DisconnectPacket,
  ForceExitPacket,
  LoginFailedPacket,
  MenuItemData,
  MenuPacket,
  PlayAmbiencePacket,
  PlayMusicPacket,
  PlaySoundPacket,
  RegisterResponsePacket,
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
import { BufferStore, type BufferName } from "../state/BufferStore";
import { TtsManager } from "../tts/TtsManager";
import { ENABLE_CLIENT_DEBUG_LOGS } from "../utils/debug";
import { MobileVoiceManager, type MobileVoiceConnectionState } from "../voice/MobileVoiceManager";

const MOBILE_CLIENT_VERSION = "1.0.4";
const MOBILE_BUILD_STAMP = "2026-04-14 19:37:43 +07:00";
const DEFAULT_SERVER_URL = "wss://playaural.ddt.one:443";
const APK_DOWNLOAD_URL =
  "https://github.com/Daoductrung/PlayAural/releases/latest/download/PlayAural.apk";
const CLIENT_CONFIG_STORAGE_KEY = "playaural.mobile.clientConfig";
const CLIENT_PASSWORD_STORAGE_KEY = "playaural.mobile.password";
const CLIENT_SV_STORAGE_KEY = "playaural.mobile.selfVoicing";
const CLIENT_MIC_PERMISSION_REQUESTED_STORAGE_KEY = "playaural.mobile.voiceMicPermissionRequested";
const WEB_SCREEN_READER_SUPPORT = Platform.OS === "web";
const NATIVE_FOCUS_DELAY_MS = 80;

type ServerAuthResponseContext = "login" | "password_reset" | "register" | "reset_code";

const SERVER_AUTH_RESPONSE_KEYS: Record<ServerAuthResponseContext, Record<string, string>> = {
  login: {
    captcha_failed: "error-captcha-failed",
    captcha_missing: "error-captcha-failed",
    rate_limit: "auth-error-rate-limit",
    user_not_found: "auth-error-user-not-found",
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

type FocusableMenuItem = {
  id?: string;
  text: string;
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
  kind: "close" | "input" | "message" | "send" | "voiceJoin" | "voiceLeave" | "voiceMic";
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
  id: "cancel" | "confirm";
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
};

type ShortcutActionId =
  | "ambience_down"
  | "ambience_up"
  | "friends"
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
    | "focus_register_bio"
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
    | "toggle_locale";
  id: string;
  text: string;
};

type StoredClientConfig = {
  appLocale: "en" | "vi";
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

function detectPreferredLocale(): "en" | "vi" {
  const deviceLocale = Intl.DateTimeFormat().resolvedOptions().locale?.toLowerCase?.() ?? "en";
  return deviceLocale.startsWith("vi") ? "vi" : "en";
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function normalizeMenuItems(items: Array<string | MenuItemData>): FocusableMenuItem[] {
  return items.map((item) => (typeof item === "string" ? { text: item } : item));
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

function formatMobileVoiceLabel(name: string, language: string, isDefault: boolean, defaultLabel: string): string {
  const parts = [name];
  if (language) {
    parts.push(language);
  }
  if (isDefault) {
    parts.push(defaultLabel);
  }
  return parts.join(", ");
}

function extractPreferenceUpdates(packet: UpdatePreferencePacket | AuthorizeSuccessPacket): Record<string, unknown> {
  if ("preferences" in packet && packet.preferences) {
    return packet.preferences;
  }
  if ("key" in packet && packet.key) {
    const keyParts = packet.key.split("/");
    const normalizedKey = keyParts[keyParts.length - 1];
    return { [normalizedKey]: packet.value };
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
  const localization = useMemo(() => new MobileLocalization(), []);
  const buffers = useMemo(() => new BufferStore(), []);
  const tts = useMemo(() => new TtsManager(), []);
  const audio = useMemo(() => new MobileAudioManager(), []);
  const voice = useMemo(() => new MobileVoiceManager(), []);

  const [appLocale, setAppLocale] = useState<"en" | "vi">(detectPreferredLocale);
  const [mode, setMode] = useState<AppMode>("main");
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [menuState, setMenuState] = useState<MenuState>(defaultMenuState);
  const [inputState, setInputState] = useState<InputState | null>(null);
  const [dialogState, setDialogState] = useState<DialogState | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [inputOverlayFocus, setInputOverlayFocus] = useState<InputOverlayFocus>(0);
  const [chatDraft, setChatDraft] = useState("");
  const [statusText, setStatusText] = useState("");
  const [authStatusText, setAuthStatusText] = useState("");
  const [, setHistoryRevision] = useState(0);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [serverUrl, setServerUrl] = useState(DEFAULT_SERVER_URL);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerBio, setRegisterBio] = useState("");
  const [registerConfirmPassword, setRegisterConfirmPassword] = useState("");
  const [forgotEmail, setForgotEmail] = useState("");
  const [resetEmail, setResetEmail] = useState("");
  const [resetCode, setResetCode] = useState("");
  const [resetPassword, setResetPassword] = useState("");
  const [resetConfirmPassword, setResetConfirmPassword] = useState("");
  const [currentMusic, setCurrentMusic] = useState("");
  const [currentAmbience, setCurrentAmbience] = useState("");
  const [connected, setConnected] = useState(false);
  const [storageReady, setStorageReady] = useState(false);
  const [lastPingStartedAt, setLastPingStartedAt] = useState<number | null>(null);
  const [shortcutFocusIndex, setShortcutFocusIndex] = useState(0);
  const [chatFocusIndex, setChatFocusIndex] = useState(0);
  const [authFocusIndex, setAuthFocusIndex] = useState(0);
  const [preferences, setPreferences] = useState<Record<string, unknown>>({});
  const [selfVoicingEnabled, setSelfVoicingEnabled] = useState(true);
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
  const [voiceStatusText, setVoiceStatusText] = useState("");
  const [voiceState, setVoiceState] = useState<MobileVoiceConnectionState>("disconnected");
  const [voiceMicEnabled, setVoiceMicEnabled] = useState(false);

  const menuStateRef = useRef(menuState);
  const inputStateRef = useRef(inputState);
  const handleSystemSwipeRef = useRef<((direction: "up" | "down" | "left" | "right") => void) | null>(null);
  const lastPingStartedAtRef = useRef<number | null>(lastPingStartedAt);
  const preferencesRef = useRef<Record<string, unknown>>(preferences);
  const voiceContextRef = useRef<VoiceContextState>({
    contextId: "",
    scope: "table",
  });
  const voiceRequestedContextIdRef = useRef("");
  const voiceStateRef = useRef<MobileVoiceConnectionState>("disconnected");
  const voiceJoinPendingRef = useRef(false);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectWindowStartedAtRef = useRef<number | null>(null);
  const reconnectDelayMsRef = useRef(1000);
  const reconnectAttemptsRef = useRef(0);
  const manualDisconnectRef = useRef(false);
  const allowReconnectRef = useRef(false);
  const expectingReconnectRef = useRef(false);
  const sessionEstablishedRef = useRef(false);
  const lastPassiveUiSignatureRef = useRef<string | null>(null);
  const authModeInitializedRef = useRef(false);
  const previousAuthModeRef = useRef<AuthMode | null>(null);
  const nativeFocusTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastNativeFocusKeyRef = useRef<string | null>(null);
  const activeTextInputKeyRef = useRef<string | null>(activeTextInputKey);
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
  const registerBioInputRef = useRef<TextInput | null>(null);
  const forgotEmailInputRef = useRef<TextInput | null>(null);
  const resetEmailInputRef = useRef<TextInput | null>(null);
  const resetCodeInputRef = useRef<TextInput | null>(null);
  const resetPasswordInputRef = useRef<TextInput | null>(null);
  const resetConfirmPasswordInputRef = useRef<TextInput | null>(null);
  const inputOverlayInputRef = useRef<TextInput | null>(null);
  const chatInputRef = useRef<TextInput | null>(null);

  useEffect(() => {
    menuStateRef.current = menuState;
  }, [menuState]);

  useEffect(() => {
    inputStateRef.current = inputState;
  }, [inputState]);

  useEffect(() => {
    lastPingStartedAtRef.current = lastPingStartedAt;
  }, [lastPingStartedAt]);

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
    credentialsRef.current = {
      password,
      serverUrl,
      username,
    };
  }, [password, serverUrl, username]);

  useEffect(() => {
    tts.setUiEnabled(selfVoicingEnabled);
    lastPassiveUiSignatureRef.current = null;
  }, [selfVoicingEnabled, tts]);

  useEffect(() => {
    let active = true;
    void AccessibilityInfo.isScreenReaderEnabled()
      .then((enabled) => {
        if (!active) {
          return;
        }
        setScreenReaderEnabled(enabled || WEB_SCREEN_READER_SUPPORT);
      })
      .catch(() => {
        if (active) {
          setScreenReaderEnabled(WEB_SCREEN_READER_SUPPORT);
        }
      });

    const subscription = AccessibilityInfo.addEventListener("screenReaderChanged", (enabled) => {
      setScreenReaderEnabled(enabled || WEB_SCREEN_READER_SUPPORT);
    });

    return () => {
      active = false;
      subscription.remove();
    };
  }, []);

  useEffect(() => () => {
    if (nativeFocusTimerRef.current) {
      clearTimeout(nativeFocusTimerRef.current);
      nativeFocusTimerRef.current = null;
    }
  }, []);

  const nativeScreenReaderMode = !selfVoicingEnabled && (screenReaderEnabled || WEB_SCREEN_READER_SUPPORT);
  const selfVoicingGestureEnabled = selfVoicingEnabled;
  const selfVoicingKeyboardEnabled = selfVoicingEnabled && activeTextInputKey === null;

  useEffect(() => {
    if (!nativeScreenReaderMode) {
      lastNativeFocusKeyRef.current = null;
    }
  }, [nativeScreenReaderMode]);

  const announceForNativeScreenReader = useCallback((text: string) => {
    if (!text) {
      return;
    }
    setScreenReaderAnnouncement((current) => ({
      id: current.id + 1,
      text,
    }));
    if (Platform.OS !== "web") {
      AccessibilityInfo.announceForAccessibility(text);
    }
  }, []);

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

  const moveNativeAccessibilityFocus = useCallback((key: string | null, attempt = 0) => {
    if (!nativeScreenReaderMode || !key) {
      return;
    }
    if (lastNativeFocusKeyRef.current === key) {
      return;
    }

    const node = accessibilityNodeRefs.current.get(key);
    if (!node) {
      if (attempt < 4) {
        if (nativeFocusTimerRef.current) {
          clearTimeout(nativeFocusTimerRef.current);
        }
        nativeFocusTimerRef.current = setTimeout(() => {
          nativeFocusTimerRef.current = null;
          moveNativeAccessibilityFocus(key, attempt + 1);
        }, NATIVE_FOCUS_DELAY_MS);
      }
      return;
    }

    if (nativeFocusTimerRef.current) {
      clearTimeout(nativeFocusTimerRef.current);
    }

    nativeFocusTimerRef.current = setTimeout(() => {
      nativeFocusTimerRef.current = null;
      lastNativeFocusKeyRef.current = key;
      if (Platform.OS === "web") {
        const focusable = node as { focus?: () => void };
        focusable.focus?.();
        return;
      }
      const reactTag = findNodeHandle(node as Parameters<typeof findNodeHandle>[0]);
      if (reactTag) {
        AccessibilityInfo.setAccessibilityFocus(reactTag);
      }
    }, NATIVE_FOCUS_DELAY_MS);
  }, [nativeScreenReaderMode]);

  const handleTextInputFocus = useCallback((key: string, onFocus?: () => void) => {
    activeTextInputKeyRef.current = key;
    setActiveTextInputKey(key);
    onFocus?.();
  }, []);

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

  const announceInterfaceFeedback = useCallback(
    (text: string) => {
      if (!text) {
        return;
      }
      addHistoryMessage("system", text);
      if (selfVoicingEnabled) {
        tts.speakUi(text, {
          interruptAnnouncement: true,
          interruptUi: true,
        });
        return;
      }
      announceForNativeScreenReader(text);
    },
    [addHistoryMessage, announceForNativeScreenReader, selfVoicingEnabled, tts],
  );

  const announce = (text: string, buffer: BufferName = "system", speak = true) => {
    buffers.add(buffer, text);
    setHistoryRevision((value) => value + 1);
    if (speak && !buffers.isMuted(buffer)) {
      if (Platform.OS !== "web" && nativeScreenReaderMode) {
        announceForNativeScreenReader(text);
        return;
      }
      tts.speakAnnouncement(text, { remember: false });
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

  useEffect(() => () => {
    clearReconnectTimer();
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
    localization.setLocale(locale);
    tts.setLanguage(locale || "en");
    setAppLocale(localization.getLocale());
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
        if (storedConfig.appLocale === "en" || storedConfig.appLocale === "vi") {
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
        setSelfVoicingEnabled(false);
      } else if (storedSelfVoicing === "1") {
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
    setSelfVoicingEnabled(enabled);
    const message = localization.t(enabled ? "sv-enabled-announcement" : "sv-disabled-announcement");
    addHistoryMessage("system", message);
    if (enabled) {
      tts.setUiEnabled(true);
      tts.speakUi(message, {
        interruptAnnouncement: true,
        interruptUi: true,
      });
      return;
    }
    tts.setUiEnabled(false);
    announceForNativeScreenReader(message);
  }, [addHistoryMessage, announceForNativeScreenReader, localization, tts]);

  const toggleSelfVoicing = useCallback(() => {
    updateSelfVoicing(!selfVoicingEnabled);
  }, [selfVoicingEnabled, updateSelfVoicing]);

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

  useEffect(() => {
    if (!storageReady) {
      return;
    }
    void requestInitialVoicePermission();
  }, [requestInitialVoicePermission, storageReady]);

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
  }, [audio, sendVoicePresence, setVoiceStatusMessage, voice]);

  const applyPreferenceUpdates = (updates: Record<string, unknown>) => {
    if (Object.keys(updates).length === 0) {
      return;
    }

    const merged = { ...preferencesRef.current, ...updates };
    preferencesRef.current = merged;
    setPreferences(merged);

    if (typeof merged.music_volume === "number") {
      audio.setMusicVolume(merged.music_volume / 100);
    }
    if (typeof merged.ambience_volume === "number") {
      audio.setAmbienceVolume(merged.ambience_volume / 100);
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
    const buffer = (packet.buffer ?? "misc") as BufferName;
    buffers.add(buffer, text);
    setHistoryRevision((value) => value + 1);
    if (!packet.muted && !buffers.isMuted(buffer)) {
      if (Platform.OS !== "web" && nativeScreenReaderMode) {
        announceForNativeScreenReader(text);
        return;
      }
      tts.speakAnnouncement(text);
    }
  };

  const applyMenuPacket = (packet: MenuPacket, overrideItems?: Array<string | MenuItemData>) => {
    if (inputStateRef.current) {
      return;
    }

    const items = normalizeMenuItems(overrideItems ?? packet.items ?? []);
    const itemIds = items.map((item) => item.id);
    const previous = menuStateRef.current;
    const incomingMenuId = packet.menu_id ?? previous.menuId;
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
    let position = typeof packet.position === "number" ? packet.position : null;

    if (packet.selection_id && position === null) {
      const selectedIndex = itemIds.indexOf(packet.selection_id);
      if (selectedIndex >= 0) {
        position = selectedIndex;
      }
    }

    const focusIndex =
      position !== null && items.length > 0
        ? clamp(position, 0, items.length - 1)
        : isSameMenuId && items.length > 0
          ? clamp(previous.focusIndex, 0, items.length - 1)
          : 0;

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

    menuStateRef.current = nextMenuState;
    setMenuState(nextMenuState);
  };

  const handleMenuPacket = (packet: MenuPacket) => {
    if (packet.menu_id !== "mobile_voice_selection_menu") {
      applyMenuPacket(packet);
      return;
    }

    applyMenuPacket(packet, [
      { id: "back", text: localization.t("mobile-tts-loading-voices") },
    ]);
    void tts.getAvailableVoiceOptions().then((voices) => {
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
        ...voices.map((voice) => ({
          id: voice.id,
          text: `${voice.id === currentVoice ? "* " : ""}${formatMobileVoiceLabel(
            voice.label,
            voice.language,
            voice.isDefault,
            localization.t("mobile-tts-system-default"),
          )}`,
        })),
        { id: "back", text: localization.t("back") },
      ];
      applyMenuPacket(packet, voiceItems);
    }).catch(() => {
      applyMenuPacket(packet, [
        { id: "default", text: localization.t("mobile-tts-default-voice") },
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
      if (packet.convo === "local" || packet.convo === "table" || packet.convo === "game") {
        chatSound = "chatlocal.ogg";
      } else if (packet.convo === "announcement") {
        chatSound = "notify.ogg";
      }
      void audio.playSound(chatSound);
      tts.speakAnnouncement(message);
    }
  };

  const stopGameAudio = (forceAmbience = true) => {
    audio.stopMusic(false);
    audio.stopAmbience(forceAmbience);
    setCurrentMusic("");
    setCurrentAmbience("");
  };

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

  const exitApplication = () => {
    disableAutoReconnect();
    connectionRef.current?.disconnect();
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
  };

  const resetToLoginScreen = useCallback((statusMessage: string, authMessage = statusMessage) => {
    voice.shutdown();
    audio.shutdown();
    setVoiceCapability({
      enabled: false,
      provider: "",
      tokenTtlSeconds: 0,
      url: "",
    });
    resetVoiceUiState();
    setConnected(false);
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
  }, [audio, resetVoiceUiState, voice]);

  const handleTerminalSessionExit = useCallback((message: string, announceMessage = true) => {
    disableAutoReconnect();
    connectionRef.current?.disconnect();
    voice.shutdown();
    audio.shutdown();
    tts.stop();
    if (announceMessage) {
      announce(message, "system");
    }
    resetToLoginScreen(message);
    if (Platform.OS === "android") {
      BackHandler.exitApp();
    }
  }, [announce, audio, disableAutoReconnect, resetToLoginScreen, tts, voice]);

  const openDialog = useCallback((nextDialog: Omit<DialogState, "focusIndex">) => {
    setDialogState({
      ...nextDialog,
      focusIndex: 0,
    });
  }, []);

  const closeDialog = useCallback(() => {
    setDialogState(null);
  }, []);

  const promptMandatoryUpdate = (id: string, title: string, message: string) => {
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
            void Linking.openURL(APK_DOWNLOAD_URL).finally(() => {
              exitApplication();
            });
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
        const localizedMessage = localizeSystemMessage(message, "network-connection-error");
        setStatusText(localizedMessage);
        if (!allowReconnectRef.current || manualDisconnectRef.current || !sessionEstablishedRef.current) {
          announce(localizedMessage, "system");
        }
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
          setConnected(true);
          setAuthMode("login");
          setAuthStatusText("");
          if (checkVersionGates(authPacket)) {
            return;
          }
          void audio.playSound("welcome.ogg", { volume: 1 });
          setStatusText(localization.t("status-connected"));
          announce(localization.t("status-connected"), "system");
          return;
        }

        if (packet.type === "chat") {
          handleChatPacket(packet as ChatPacket);
          return;
        }

        if (packet.type === "clear_ui") {
          leaveVoiceChat({
            announce: false,
            clearContext: true,
            sendLeave: voicePresenceRegisteredRef.current,
            statusKey: "voice-chat-not-connected",
          });
          stopGameAudio(true);
          setMenuState(defaultMenuState);
          menuStateRef.current = defaultMenuState;
          setInputState(null);
          setInputValue("");
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
          stopGameAudio(true);
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
          stopGameAudio(true);
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

        if (packet.type === "play_ambience") {
          const ambiencePacket = packet as PlayAmbiencePacket;
          setCurrentAmbience(ambiencePacket.loop || "");
          void audio.playAmbience(
            ambiencePacket.loop || "",
            ambiencePacket.intro || "",
            ambiencePacket.outro || "",
          );
          return;
        }

        if (packet.type === "play_music") {
          const musicPacket = packet as PlayMusicPacket;
          setCurrentMusic(musicPacket.name || "");
          void audio.playMusic(musicPacket.name || "", musicPacket.looping ?? true);
          return;
        }

        if (packet.type === "play_sound") {
          const soundPacket = packet as PlaySoundPacket;
          if (soundPacket.name) {
            void audio.playSound(soundPacket.name, {
              pan: (soundPacket.pan ?? 0) / 100,
              pitch: (soundPacket.pitch ?? 100) / 100,
              volume: (soundPacket.volume ?? 100) / 100,
            });
          }
          return;
        }

        if (packet.type === "request_input") {
          const inputPacket = packet as RequestInputPacket;
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

        if (packet.type === "stop_ambience") {
          setCurrentAmbience("");
          audio.stopAmbience();
          return;
        }

        if (packet.type === "stop_music") {
          setCurrentMusic("");
          audio.stopMusic();
          return;
        }

        if (packet.type === "pong") {
          const startedAt = lastPingStartedAtRef.current;
          if (startedAt) {
            const elapsed = Date.now() - startedAt;
            setLastPingStartedAt(null);
            announceInterfaceFeedback(localization.t("shortcut-ping-result", { value: elapsed }));
          }
          return;
        }

        if (packet.type === "table_context") {
          const contextPacket = packet as TableContextPacket;
          const contextId = String(contextPacket.table_id || "");
          const previousContextId = voiceContextRef.current.contextId;
          if (previousContextId && contextId && contextId !== previousContextId) {
            stopGameAudio(true);
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
          if (!voiceJoinPendingRef.current) {
            return;
          }
          if (!packetContextId || packetContextId !== voiceRequestedContextIdRef.current) {
            return;
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
            closedContextId &&
            closedContextId !== voiceContextRef.current.contextId &&
            closedContextId !== voiceRequestedContextIdRef.current
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
            setRegisterBio("");
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
  const historyMessages = buffers.getMessages("all").reverse();
  const chatMessages = buffers.getMessages("chat").reverse();
  const focusedHistoryMessage = historyMessages[historyIndex] ?? null;
  const focusedMenuItem = menuState.items[menuState.focusIndex];
  const focusedDialogButton = dialogState?.buttons[dialogState.focusIndex] ?? null;
  const menuGridRows = menuState.gridEnabled
    ? Math.max(1, menuState.gridHeight || Math.ceil(menuState.items.length / Math.max(1, menuState.gridWidth)))
    : 0;
  const gridGap = 8;
  const gridPanelHeightAllowance = 68;
  const gridContentWidth = Math.max(0, mainPanelLayout.width);
  const gridContentHeight = Math.max(0, mainPanelLayout.height - gridPanelHeightAllowance);
  const gridCellWidth =
    menuState.gridEnabled && menuState.gridWidth > 1 && gridContentWidth > 0
      ? Math.max(
          28,
          Math.floor((gridContentWidth - gridGap * (menuState.gridWidth - 1)) / menuState.gridWidth),
        )
      : null;
  const gridCellHeight =
    menuState.gridEnabled && menuGridRows > 0 && gridContentHeight > 0
      ? Math.max(28, Math.floor((gridContentHeight - gridGap * (menuGridRows - 1)) / menuGridRows))
      : null;
  const gridCellSize =
    gridCellWidth !== null && gridCellHeight !== null
      ? Math.max(28, Math.min(gridCellWidth, gridCellHeight))
      : null;
  const chatFocusItems: ChatFocusItem[] = [
    { kind: "input", text: localization.t("chat-input-focus") },
    { kind: "send", text: localization.t("chat-send-button") },
    voiceState === "connected"
      ? { kind: "voiceLeave", text: localization.t("voice-chat-leave") }
      : {
          kind: "voiceJoin",
          text: voiceState === "connecting"
            ? localization.t("voice-chat-joining")
            : localization.t("voice-chat-join"),
        },
    ...(voiceState === "connected"
      ? [{
          kind: "voiceMic" as const,
          text: localization.t(
            voiceMicEnabled ? "voice-chat-turn-off-mic" : "voice-chat-turn-on-mic",
          ),
        }]
      : []),
    { kind: "close", text: localization.t("chat-close-button") },
    ...chatMessages.map((message) => ({
      kind: "message" as const,
      text: message.text,
    })),
  ];
  const focusedChatItem = chatFocusItems[chatFocusIndex] ?? null;
  const sendChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "send");
  const voiceJoinChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "voiceJoin");
  const voiceLeaveChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "voiceLeave");
  const voiceMicChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "voiceMic");
  const closeChatFocusIndex = chatFocusItems.findIndex((item) => item.kind === "close");
  const firstChatMessageFocusIndex = chatFocusItems.findIndex((item) => item.kind === "message");
  const chatMessageFocusOffset = firstChatMessageFocusIndex >= 0 ? firstChatMessageFocusIndex : chatFocusItems.length;
  const inputOverlayButtonText = localization.t(inputState?.readOnly ? "input-close-button" : "input-submit-button");
  const focusedInputOverlayText =
    inputState === null ? null : inputOverlayFocus === 0 ? inputState.prompt : inputOverlayButtonText;
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
  ];
  const focusedShortcutItem = shortcutItems[shortcutFocusIndex] ?? null;
  const authFocusableItems = useMemo<AuthFocusableItem[]>(() => {
    if (connected) {
      return [];
    }

    const items: AuthFocusableItem[] = [
      { action: "toggle_locale", id: "locale", text: `${localization.t("locale")}: ${appLocale.toUpperCase()}` },
      { action: "focus_username", id: "field-username", text: localization.t("username") },
    ];

    if (authMode === "login") {
      items.push({ action: "focus_password", id: "field-password", text: localization.t("password") });
      items.push({ action: "connect", id: "button-connect", text: localization.t("connect") });
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
      items.push({ action: "focus_register_bio", id: "field-register-bio", text: localization.t("auth-bio") });
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

    items.push(...([
      { action: "switch_login" as const, id: "tab-login", text: localization.t("auth-mode-login") },
      { action: "switch_register" as const, id: "tab-register", text: localization.t("auth-mode-register") },
      { action: "switch_forgot" as const, id: "tab-forgot", text: localization.t("auth-mode-forgot") },
    ]));
    items.push({
      action: "exit_app",
      id: "button-exit",
      text: localization.t("auth-exit"),
    });

    return items;
  }, [appLocale, authMode, connected, localization, password, username]);
  const focusedAuthItem = authFocusableItems[authFocusIndex] ?? null;

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
    if (!connected) {
      return focusedAuthItem?.text ?? null;
    }
    if (dialogState && focusedDialogButton) {
      return focusedDialogButton.text;
    }
    if (inputState && focusedInputOverlayText) {
      return focusedInputOverlayText;
    }
    if (mode === "main") {
      return focusedMenuItem?.text ?? (menuState.items.length === 0 ? localization.t("menu-empty") : null);
    }
    if (mode === "shortcuts") {
      return focusedShortcutItem?.text ?? null;
    }
    if (mode === "history") {
      return focusedHistoryMessage?.text ?? null;
    }
    if (mode === "chat") {
      return focusedChatItem?.text ?? null;
    }
    return null;
  }, [
    connected,
    dialogState,
    focusedAuthItem?.text,
    focusedDialogButton?.text,
    focusedHistoryMessage?.text,
    focusedChatItem?.text,
    focusedInputOverlayText,
    focusedMenuItem?.text,
    focusedShortcutItem?.text,
    inputState,
    localization,
    menuState.items.length,
    mode,
  ]);

  const getCurrentUiFocusSignature = useCallback((): string | null => {
    if (!connected) {
      return focusedAuthItem
        ? `auth:${authMode}:${focusedAuthItem.id}:${focusedAuthItem.text}`
        : null;
    }
    if (dialogState && focusedDialogButton) {
      return `dialog:${dialogState.id}:${dialogState.focusIndex}:${focusedDialogButton.id}:${focusedDialogButton.text}`;
    }
    if (inputState && focusedInputOverlayText) {
      return `input:${inputState.inputId ?? "none"}:${inputOverlayFocus}:${focusedInputOverlayText}`;
    }
    if (mode === "main") {
      const text = focusedMenuItem?.text ?? (menuState.items.length === 0 ? localization.t("menu-empty") : null);
      if (!text) {
        return null;
      }
      return `main:${menuState.menuId}:${menuState.focusIndex}:${focusedMenuItem?.id ?? "none"}:${text}`;
    }
    if (mode === "shortcuts" && focusedShortcutItem) {
      return `shortcuts:${shortcutFocusIndex}:${focusedShortcutItem.id}:${focusedShortcutItem.text}`;
    }
    if (mode === "history" && focusedHistoryMessage) {
      return `history:${historyIndex}:${focusedHistoryMessage.timestamp}:${focusedHistoryMessage.text}`;
    }
    if (mode === "chat" && focusedChatItem) {
      return `chat:${chatFocusIndex}:${focusedChatItem.kind}:${focusedChatItem.text}`;
    }
    return null;
  }, [
    authMode,
    chatFocusIndex,
    connected,
    dialogState,
    focusedAuthItem,
    focusedChatItem,
    focusedDialogButton,
    focusedHistoryMessage,
    focusedInputOverlayText,
    focusedMenuItem,
    focusedShortcutItem,
    historyIndex,
    inputOverlayFocus,
    inputState,
    localization,
    menuState.focusIndex,
    menuState.items.length,
    menuState.menuId,
    mode,
    shortcutFocusIndex,
  ]);

  const getCurrentNativeFocusKey = useCallback((): string | null => {
    if (!connected) {
      return focusedAuthItem ? `auth:${focusedAuthItem.id}` : null;
    }
    if (dialogState && focusedDialogButton) {
      return `dialog:${dialogState.id}:${focusedDialogButton.id}`;
    }
    if (inputState) {
      return inputOverlayFocus === 0 ? "input:field" : "input:action";
    }
    if (mode === "main") {
      return focusedMenuItem ? `menu:${menuState.menuId}:${menuState.focusIndex}` : null;
    }
    if (mode === "shortcuts" && focusedShortcutItem) {
      return `shortcut:${focusedShortcutItem.id}`;
    }
    if (mode === "history") {
      return "history:content";
    }
    if (mode === "chat") {
      if (focusedChatItem?.kind === "input") {
        return "chat:input";
      }
      if (focusedChatItem?.kind === "send") {
        return "chat:send";
      }
      if (focusedChatItem?.kind === "voiceJoin") {
        return "chat:voiceJoin";
      }
      if (focusedChatItem?.kind === "voiceLeave") {
        return "chat:voiceLeave";
      }
      if (focusedChatItem?.kind === "voiceMic") {
        return "chat:voiceMic";
      }
      if (focusedChatItem?.kind === "close") {
        return "chat:close";
      }
      if (focusedChatItem?.kind === "message" && firstChatMessageFocusIndex >= 0) {
        return `chat:message:${chatFocusIndex - firstChatMessageFocusIndex}`;
      }
    }
    return null;
  }, [
    chatFocusIndex,
    connected,
    dialogState,
    firstChatMessageFocusIndex,
    focusedAuthItem,
    focusedChatItem,
    focusedDialogButton,
    focusedMenuItem,
    focusedShortcutItem,
    inputOverlayFocus,
    inputState,
    menuState.focusIndex,
    menuState.menuId,
    mode,
  ]);

  useEffect(() => {
    setAuthFocusIndex((current) => clamp(current, 0, Math.max(0, authFocusableItems.length - 1)));
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
    }
  }, [announceInterfaceFeedback, authFocusableItems, authMode, connected, localization]);

  useEffect(() => {
    setChatFocusIndex((current) => clamp(current, 0, Math.max(0, chatFocusItems.length - 1)));
  }, [chatFocusItems.length]);

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
    moveNativeAccessibilityFocus(getCurrentNativeFocusKey());
  }, [
    authFocusIndex,
    chatFocusIndex,
    connected,
    dialogState,
    getCurrentNativeFocusKey,
    historyIndex,
    inputOverlayFocus,
    inputState,
    menuState.focusIndex,
    menuState.menuId,
    mode,
    moveNativeAccessibilityFocus,
    nativeScreenReaderMode,
    shortcutFocusIndex,
  ]);

  useEffect(() => {
    if (!inputState || inputState.readOnly) {
      return;
    }

    let cancelled = false;
    const focusInputOverlay = () => {
      if (cancelled || inputStateRef.current?.inputId !== inputState.inputId) {
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
  }, [inputState?.inputId, inputState?.readOnly]);

  useEffect(() => {
    if (!dialogState) {
      return;
    }
    const initialButton = dialogState.buttons[dialogState.focusIndex]?.text ?? "";
    const dialogIntro = [dialogState.title, dialogState.message, initialButton].filter(Boolean).join(". ");
    if (!dialogIntro) {
      return;
    }
    tts.speakUi(dialogIntro, {
      interruptAnnouncement: true,
      interruptUi: true,
    });
  }, [dialogState?.id]);

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
    if (action === "focus_register_bio") {
      registerBioInputRef.current?.focus();
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
    if (item.action === "toggle_locale") {
      applyLocale(appLocale === "en" ? "vi" : "en");
    }
  };

  const isAuthFocused = (id: string) => !connected && focusedAuthItem?.id === id;

  const focusAuthItemById = (id: string) => {
    const nextIndex = authFocusableItems.findIndex((item) => item.id === id);
    if (nextIndex >= 0) {
      setAuthFocusIndex(nextIndex);
    }
  };

  const focusMenuItemAt = (index: number) => {
    setMenuState((previous) => {
      if (previous.focusIndex === index) {
        return previous;
      }
      const nextState = {
        ...previous,
        focusIndex: clamp(index, 0, Math.max(0, previous.items.length - 1)),
      };
      menuStateRef.current = nextState;
      return nextState;
    });
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
    connection?.send({
      menu_id: currentMenuState.menuId || undefined,
      selection: (indexOverride ?? currentMenuState.focusIndex) + 1,
      selection_id: item.id,
      type: "menu",
    });
  };

  const sendEscape = () => {
    const currentMenuState = menuStateRef.current;
    if (isProtectedTransientMenu(currentMenuState.menuId)) {
      transientTurnMenuAllowanceRef.current = currentMenuState.menuId;
    }
    connection?.send({
      menu_id: currentMenuState.menuId || undefined,
      type: "escape",
    });
  };

  const sendEscapeEquivalent = (
    menuId: string,
    escapeBehavior: string,
    items: FocusableMenuItem[],
  ) => {
    if (isProtectedTransientMenu(menuId)) {
      transientTurnMenuAllowanceRef.current = menuId;
    }
    if (escapeBehavior === "select_last_option") {
      const lastIndex = items.length - 1;
      if (lastIndex >= 0) {
        const item = items[lastIndex];
        connection?.send({
          menu_id: menuId || undefined,
          selection: lastIndex + 1,
          selection_id: item?.id,
          type: "menu",
        });
      }
      return;
    }

    if (escapeBehavior === "select_first_option") {
      if (items.length > 0) {
        const item = items[0];
        connection?.send({
          menu_id: menuId || undefined,
          selection: 1,
          selection_id: item?.id,
          type: "menu",
        });
      }
      return;
    }

    sendEscape();
  };

  const openActionsMenu = () => {
    const currentMenuState = menuStateRef.current;
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
    connection?.send({
      key: "shift+enter",
      menu_item_id: item?.id ?? null,
      shift: true,
      type: "keybind",
    });
  };

  const closeOverlay = () => {
    if (mode === "main") {
      return false;
    }
    const name = localization.t(`mode-${mode}`);
    setMode("main");
    announceInterfaceFeedback(localization.t("overlay-closed", { name }));
    return true;
  };

  const toggleOverlay = (nextMode: Exclude<AppMode, "main">) => {
    setMode((current) => {
      const resolved = current === nextMode ? "main" : nextMode;
      const key = resolved === "main" ? "overlay-closed" : "overlay-opened";
      if (resolved === "shortcuts") {
        setShortcutFocusIndex(0);
      }
      if (resolved === "chat") {
        setChatFocusIndex(0);
      }
      if (resolved === "history") {
        setHistoryIndex(0);
      }
      announceInterfaceFeedback(localization.t(key, { name: localization.t(`mode-${nextMode}`) }));
      return resolved;
    });
  };

  const syncPreference = (key: string, value: boolean | number | string) => {
    const keyParts = key.split("/");
    const flatKey = keyParts[keyParts.length - 1];
    applyPreferenceUpdates({ [flatKey]: value });
    if (connected) {
      connection?.send({
        key,
        type: "set_preference",
        value,
      });
    }
  };

  const activateShortcut = (shortcut: ShortcutItem | null) => {
    if (!shortcut) {
      return;
    }
    if (shortcut.id === "options") {
      connection?.send({ type: "open_options" });
      setMode("main");
      return;
    }
    if (shortcut.id === "friends") {
      connection?.send({ type: "open_friends_hub" });
      setMode("main");
      return;
    }
    if (shortcut.id === "ping") {
      setLastPingStartedAt(Date.now());
      connection?.send({ type: "ping" });
      announceInterfaceFeedback(localization.t("shortcut-ping-sent"));
      return;
    }
    if (shortcut.id === "list_online") {
      connection?.send({ type: "list_online" });
      setMode("main");
      return;
    }
    if (shortcut.id === "list_online_with_games") {
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

  const playMenuMoveSound = () => {
    void audio.playSound("menuclick.ogg", { volume: 0.5 });
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

  const submitInputOverlay = () => {
    if (!inputState) {
      return;
    }
    if (inputState.readOnly) {
      Keyboard.dismiss();
      activeTextInputKeyRef.current = null;
      setActiveTextInputKey((current) => (current === "input:field" ? null : current));
      setInputState(null);
      setInputValue("");
      setInputOverlayFocus(0);
      return;
    }
    connection?.send({
      input_id: inputState.inputId,
      text: inputValue,
      type: "editbox",
    });
    announceInterfaceFeedback(localization.t("input-submitted"));
    Keyboard.dismiss();
    activeTextInputKeyRef.current = null;
    setActiveTextInputKey((current) => (current === "input:field" ? null : current));
    setInputState(null);
    setInputValue("");
    setInputOverlayFocus(0);
  };

  const handlePrimaryActivate = () => {
    void audio.handleUserInteraction();
    if (dialogState) {
      playMenuActivateSound();
      activateDialogButton();
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
      if (focusedHistoryMessage) {
        playMenuActivateSound();
        tts.speakUi(focusedHistoryMessage.text);
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
    if (!connected) {
      return;
    }
    sendShiftEnter();
  };

  const handleBoundaryJump = (target: "bottom" | "top") => {
    void audio.handleUserInteraction();

    const boundaryIndex = (length: number) => {
      if (length <= 0) {
        return 0;
      }
      return target === "top" ? 0 : length - 1;
    };

    if (dialogState) {
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

    if (inputState) {
      const nextFocus: InputOverlayFocus = target === "top" ? 0 : 1;
      setInputOverlayFocus(nextFocus);
      if (nextFocus !== inputOverlayFocus) {
        playMenuMoveSound();
      }
      speakUserFocus(nextFocus === 0 ? inputState.prompt : inputOverlayButtonText);
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
      speakUserFocus(authFocusableItems[nextIndex]?.text);
      return;
    }

    if (mode === "shortcuts") {
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

    if (mode === "history") {
      if (historyMessages.length === 0) {
        speakUserFocus(localization.t("history-empty"));
        return;
      }
      const nextIndex = boundaryIndex(historyMessages.length);
      setHistoryIndex(nextIndex);
      if (nextIndex !== historyIndex) {
        playMenuMoveSound();
      }
      speakUserFocus(historyMessages[nextIndex]?.text);
      return;
    }

    if (mode === "chat") {
      if (chatFocusItems.length === 0) {
        return;
      }
      const nextIndex = boundaryIndex(chatFocusItems.length);
      setChatFocusIndex(nextIndex);
      if (nextIndex !== chatFocusIndex) {
        playMenuMoveSound();
      }
      speakUserFocus(chatFocusItems[nextIndex]?.text);
      return;
    }

    setMenuState((previous) => {
      if (previous.items.length === 0) {
        return previous;
      }
      const nextIndex = boundaryIndex(previous.items.length);
      if (nextIndex !== previous.focusIndex) {
        playMenuMoveSound();
      }
      speakUserFocus(previous.items[nextIndex]?.text);
      const nextState = {
        ...previous,
        focusIndex: nextIndex,
      };
      menuStateRef.current = nextState;
      return nextState;
    });
  };

  const handleDirectionalNavigation = (direction: "up" | "down" | "left" | "right") => {
    void audio.handleUserInteraction();
    if (dialogState) {
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
    if (inputState) {
      setInputOverlayFocus((current) => {
        const next: InputOverlayFocus = direction === "left" || direction === "up" ? 0 : 1;
        if (next !== current) {
          speakUserFocus(next === 0 ? inputState.prompt : inputOverlayButtonText);
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
            speakUserFocus(authFocusableItems[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        if (direction === "down" || direction === "right") {
          const next = Math.min(authFocusableItems.length - 1, current + 1);
          if (next !== current) {
            speakUserFocus(authFocusableItems[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        return current;
      });
      return;
    }
    if (mode === "shortcuts") {
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
    if (mode === "history") {
      setHistoryIndex((current) => {
        const max = Math.max(0, historyMessages.length - 1);
        if (direction === "left" || direction === "down") {
          const next = Math.min(max, current + 1);
          if (next !== current) {
            speakUserFocus(historyMessages[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        if (direction === "right" || direction === "up") {
          const next = Math.max(0, current - 1);
          if (next !== current) {
            speakUserFocus(historyMessages[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        return current;
      });
      return;
    }
    if (mode === "chat") {
      setChatFocusIndex((current) => {
        if (chatFocusItems.length === 0) {
          return 0;
        }
        if (direction === "up" || direction === "left") {
          const next = Math.max(0, current - 1);
          if (next !== current) {
            speakUserFocus(chatFocusItems[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        if (direction === "down" || direction === "right") {
          const next = Math.min(chatFocusItems.length - 1, current + 1);
          if (next !== current) {
            speakUserFocus(chatFocusItems[next]?.text);
            playMenuMoveSound();
          }
          return next;
        }
        return current;
      });
      return;
    }
    setMenuState((previous) => {
      if (previous.items.length === 0) {
        return previous;
      }
      const nextIndex = previous.gridEnabled
        ? nextGridIndex(previous.focusIndex, previous.items.length, previous.gridWidth, direction)
        : nextLinearIndex(
            previous.focusIndex,
            previous.items.length,
            direction === "up" || direction === "left" ? "up" : "down",
          );
      const nextState = {
        ...previous,
        focusIndex: nextIndex,
      };
      if (nextIndex !== previous.focusIndex) {
        speakUserFocus(previous.items[nextIndex]?.text);
        playMenuMoveSound();
      }
      menuStateRef.current = nextState;
      return nextState;
    });
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
    focusedDialogButton?.onPress();
  };

  const handleSystemSwipe = (direction: "up" | "down" | "left" | "right") => {
    void audio.handleUserInteraction();
    const currentMenuState = menuStateRef.current;
    if (dialogState) {
      if (direction === "up") {
        const cancelButton = dialogState.buttons.find((button) => button.id === "cancel");
        cancelButton?.onPress();
      }
      return;
    }
    if (direction === "up") {
      if (closeOverlay()) {
        return;
      }
      if (inputState) {
        Keyboard.dismiss();
        activeTextInputKeyRef.current = null;
        setActiveTextInputKey((current) => (current === "input:field" ? null : current));
        setInputState(null);
        setInputValue("");
        setInputOverlayFocus(0);
        announceInterfaceFeedback(localization.t("input-cancelled"));
        return;
      }
      if (connected && mode === "main" && currentMenuState.menuId === "turn_menu") {
        playMenuActivateSound();
        openActionsMenu();
        return;
      }
      if (connected && mode === "main" && currentMenuState.menuId === "main_menu") {
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
    if (inputState) {
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

  const fallbackPrimaryActionLabel = useMemo(() => {
    if (mode !== "main") {
      return localization.t("native-fallback-back");
    }
    if (menuState.menuId === "turn_menu") {
      return localization.t("native-fallback-actions");
    }
    return localization.t("native-fallback-back");
  }, [localization, menuState.menuId, mode]);

  const showNativeFallbackButtons =
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

  const gestures = useSelfVoicingGestures({
    enabled: selfVoicingGestureEnabled,
    globalToggleEnabled: true,
    isNativeTextInputTarget,
    isTextInputEditing,
    onDoubleTap: handlePrimaryActivate,
    onDoubleTapHold: handleModifiedActivate,
    onSingleFingerSwipe: handleDirectionalNavigation,
    onThreeFingerSwipe: (direction) => {
      if (direction === "up") {
        handleBoundaryJump("top");
        return;
      }
      if (direction === "down") {
        handleBoundaryJump("bottom");
      }
    },
    onThreeFingerTap: handleRepeatLast,
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
    if (!selfVoicingEnabled) {
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

    if (!connected) {
      if (focusedAuthItem?.text) {
        lastPassiveUiSignatureRef.current = focusSignature;
        tts.speakUi(focusedAuthItem.text, focusSpeechOptions);
      }
      return;
    }
    if (dialogState && focusedDialogButton) {
      lastPassiveUiSignatureRef.current = focusSignature;
      tts.speakUi(focusedDialogButton.text, focusSpeechOptions);
      return;
    }
    if (inputState && focusedInputOverlayText) {
      lastPassiveUiSignatureRef.current = focusSignature;
      tts.speakUi(focusedInputOverlayText, focusSpeechOptions);
      return;
    }
    if (mode === "main") {
      if (focusedMenuItem?.text) {
        lastPassiveUiSignatureRef.current = focusSignature;
        tts.speakUi(focusedMenuItem.text, focusSpeechOptions);
      } else if (menuState.items.length === 0) {
        lastPassiveUiSignatureRef.current = focusSignature;
        tts.speakUi(localization.t("menu-empty"), focusSpeechOptions);
      }
      return;
    }
    if (mode === "shortcuts" && focusedShortcutItem) {
      lastPassiveUiSignatureRef.current = focusSignature;
      tts.speakUi(focusedShortcutItem.text, focusSpeechOptions);
      return;
    }
    if (mode === "history" && focusedHistoryMessage) {
      lastPassiveUiSignatureRef.current = focusSignature;
      tts.speakUi(focusedHistoryMessage.text, focusSpeechOptions);
      return;
    }
    if (mode === "chat" && focusedChatItem) {
      lastPassiveUiSignatureRef.current = focusSignature;
      tts.speakUi(focusedChatItem.text, focusSpeechOptions);
    }
  }, [
    connected,
    selfVoicingEnabled,
    authFocusIndex,
    dialogState,
    focusedAuthItem?.text,
    focusedDialogButton?.text,
    focusedInputOverlayText,
    inputState,
    mode,
    menuState.focusIndex,
    menuState.menuId,
    focusedMenuItem?.text,
    historyIndex,
    focusedHistoryMessage?.text,
    focusedChatItem?.text,
    chatFocusIndex,
    focusedShortcutItem?.text,
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
    if (!voiceMicEnabled) {
      const granted = await ensureVoiceMicrophonePermission(true);
      if (!granted) {
        setVoiceStatusMessage("voice-chat-mic-denied", true);
        return;
      }
    }
    voice.setMicrophoneEnabled(!voiceMicEnabled);
  }, [ensureVoiceMicrophonePermission, setVoiceStatusMessage, voice, voiceMicEnabled, voiceState]);

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
          setRegisterBio("");
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
        bio: registerBio.trim(),
        client: "mobile",
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
        client: "mobile",
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
        client: "mobile",
        code: resetCode.trim(),
        email: resetEmail.trim(),
        locale: appLocale,
        new_password: resetPassword,
        type: "submit_reset_code",
      },
      "submit_reset_code_response",
    );
  };

  const renderMainView = () => (
    <View
      onLayout={(event) => {
        const { height, width } = event.nativeEvent.layout;
        setMainPanelLayout((current) => (
          current.width === width && current.height === height
            ? current
            : { height, width }
        ));
      }}
      style={styles.panel}
    >
      <Text style={styles.panelTitle}>{localization.t("mode-main")}</Text>
      {menuState.gridEnabled && menuState.gridWidth > 1 ? (
        <View style={styles.gridMenuArea}>
          {menuState.items.map((item, index) => (
            <Pressable
              accessibilityActions={[
                { name: "activate" },
                { name: "longpress" },
              ]}
              accessibilityLabel={item.text}
              accessibilityRole="button"
              accessible
              key={`${item.id ?? "text"}-${index}`}
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
              onPress={() => {
                void audio.handleUserInteraction();
                focusMenuItemAt(index);
                playMenuActivateSound();
                sendMenuSelection(item, index);
              }}
              ref={registerAccessibilityNode(`menu:${menuState.menuId}:${index}`)}
              style={[
                styles.menuItem,
                styles.gridMenuItem,
                index === menuState.focusIndex ? styles.menuItemFocused : undefined,
                gridCellSize !== null
                  ? {
                      flexBasis: gridCellSize,
                      minHeight: gridCellSize,
                      minWidth: gridCellSize,
                      width: gridCellSize,
                    }
                  : {
                      flexBasis: `${100 / Math.max(1, menuState.gridWidth)}%`,
                    },
              ]}
            >
              <Text style={styles.menuText}>{item.text}</Text>
            </Pressable>
          ))}
        </View>
      ) : (
        <ScrollView style={styles.scrollArea}>
          {menuState.items.map((item, index) => (
            <Pressable
              accessibilityActions={[
                { name: "activate" },
                { name: "longpress" },
              ]}
              accessibilityLabel={item.text}
              accessibilityRole="button"
              accessible
              key={`${item.id ?? "text"}-${index}`}
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
              onPress={() => {
                void audio.handleUserInteraction();
                focusMenuItemAt(index);
                playMenuActivateSound();
                sendMenuSelection(item, index);
              }}
              ref={registerAccessibilityNode(`menu:${menuState.menuId}:${index}`)}
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
  );

  const renderChatOverlay = () => (
    <View style={styles.panel}>
      <Text style={styles.panelTitle}>{localization.t("mode-chat")}</Text>
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
          placeholderTextColor="#7f8a93"
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
            accessibilityState={{ selected: voiceMicEnabled }}
            accessible
            onPress={() => {
              void audio.handleUserInteraction();
              void toggleVoiceMicrophone();
            }}
            onFocus={() => {
              if (voiceMicChatFocusIndex >= 0) {
                setChatFocusIndex(voiceMicChatFocusIndex);
              }
            }}
            ref={registerAccessibilityNode("chat:voiceMic")}
            style={[
              styles.buttonSecondary,
              styles.chatActionButton,
              chatFocusIndex === voiceMicChatFocusIndex ? styles.menuItemFocused : undefined,
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
      <ScrollView style={styles.scrollArea}>
        {chatMessages.map((item, index) => (
          <Pressable
            accessibilityLabel={item.text}
            accessibilityRole="button"
            accessible
            key={`chat-${item.timestamp}-${index}`}
            onFocus={() => {
              setChatFocusIndex(chatMessageFocusOffset + index);
            }}
            onPress={() => {
              setChatFocusIndex(chatMessageFocusOffset + index);
              speakUserFocus(item.text);
            }}
            ref={registerAccessibilityNode(`chat:message:${index}`)}
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
      <Text
        accessibilityLabel={focusedHistoryMessage?.text ?? localization.t("history-empty")}
        accessible
        ref={registerAccessibilityNode("history:content")}
        style={styles.historyText}
      >
        {focusedHistoryMessage?.text ?? localization.t("history-empty")}
      </Text>
      <Text style={styles.helpText}>
        {historyMessages.length ? `${historyIndex + 1} / ${historyMessages.length}` : ""}
      </Text>
    </View>
  );

  const renderShortcutsOverlay = () => (
    <View style={styles.panel}>
      <Text style={styles.panelTitle}>{localization.t("shortcuts-title")}</Text>
      <ScrollView style={styles.scrollArea}>
        {shortcutItems.map((item, index) => (
          <Pressable
            accessibilityLabel={item.text}
            accessibilityRole="button"
            accessible
            key={item.id}
            onFocus={() => {
              setShortcutFocusIndex(index);
            }}
            onPress={() => {
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
      <View style={styles.inputOverlayScreen}>
        <View style={styles.dialogCard}>
          <Text style={styles.panelTitle}>{dialogState.title}</Text>
          <Text style={styles.dialogMessage}>{dialogState.message}</Text>
          <View style={styles.dialogButtons}>
            {dialogState.buttons.map((button, index) => (
              <Pressable
                accessibilityLabel={button.text}
                accessibilityRole="button"
                accessible
                key={`${dialogState.id}-${button.id}`}
                onFocus={() => {
                  setDialogState((current) => current ? { ...current, focusIndex: index } : current);
                }}
                onPress={() => {
                  void audio.handleUserInteraction();
                  button.onPress();
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
        </View>
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
    <View style={styles.authTabs}>
      {(["login", "register", "forgot"] as const).map((candidate) => (
        <Pressable
          accessibilityLabel={localization.t(`auth-mode-${candidate}`)}
          accessibilityRole="button"
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
        <Pressable
          ref={registerAccessibilityNode("auth:tab-reset")}
          style={[styles.authTab, styles.authTabActive]}
        >
          <Text style={styles.buttonText}>{localization.t("auth-mode-reset")}</Text>
        </Pressable>
      ) : null}
    </View>
  );

  const renderAuthCard = () => (
    <View style={styles.loginCard}>
      {renderAuthSwitcher()}

      {authMode === "login" ? (
        <>
          <View style={isAuthFocused("field-username") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
              ref={registerAccessibilityNode("auth:field-username", usernameInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={username}
            />
          </View>
          <View style={isAuthFocused("field-password") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
              ref={registerAccessibilityNode("auth:field-password", passwordInputRef)}
              secureTextEntry
              showSoftInputOnFocus
              style={styles.input}
              value={password}
            />
          </View>
          <View style={styles.row}>
            <Pressable
              accessibilityLabel={localization.t("connect")}
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
              <Text style={styles.buttonText}>{localization.t("connect")}</Text>
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
          <View style={isAuthFocused("field-username") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
              ref={registerAccessibilityNode("auth:field-username", usernameInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={username}
            />
          </View>
          <View style={isAuthFocused("field-register-email") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
              ref={registerAccessibilityNode("auth:field-register-email", registerEmailInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={registerEmail}
            />
          </View>
          <View style={isAuthFocused("field-password") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
              ref={registerAccessibilityNode("auth:field-password", passwordInputRef)}
              secureTextEntry
              showSoftInputOnFocus
              style={styles.input}
              value={password}
            />
          </View>
          <View style={isAuthFocused("field-register-confirm-password") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
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
          <View style={isAuthFocused("field-register-bio") ? styles.authFieldFocused : undefined}>
            <TextInput
              accessibilityLabel={localization.t("auth-bio")}
              multiline
              onChangeText={setRegisterBio}
              onFocus={() => {
                handleTextInputFocus("auth:field-register-bio", () => {
                  focusAuthItemById("field-register-bio");
                });
              }}
              onBlur={() => {
                handleTextInputBlur("auth:field-register-bio");
              }}
              placeholder={localization.t("auth-bio")}
              placeholderTextColor="#7f8a93"
              ref={registerAccessibilityNode("auth:field-register-bio", registerBioInputRef)}
              showSoftInputOnFocus
              style={[styles.input, styles.multilineInput]}
              value={registerBio}
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
          <View style={isAuthFocused("field-forgot-email") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
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
          <View style={isAuthFocused("field-reset-email") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
              ref={registerAccessibilityNode("auth:field-reset-email", resetEmailInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={resetEmail}
            />
          </View>
          <View style={isAuthFocused("field-reset-code") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
              ref={registerAccessibilityNode("auth:field-reset-code", resetCodeInputRef)}
              showSoftInputOnFocus
              style={styles.input}
              value={resetCode}
            />
          </View>
          <View style={isAuthFocused("field-reset-password") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
              ref={registerAccessibilityNode("auth:field-reset-password", resetPasswordInputRef)}
              secureTextEntry
              showSoftInputOnFocus
              style={styles.input}
              value={resetPassword}
            />
          </View>
          <View style={isAuthFocused("field-reset-confirm-password") ? styles.authFieldFocused : undefined}>
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
              placeholderTextColor="#7f8a93"
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
          accessibilityLabel={`${localization.t("locale")}: ${appLocale.toUpperCase()}`}
          accessibilityRole="button"
          accessible
          onFocus={() => {
            focusAuthItemById("locale");
          }}
          onPress={() => {
            void audio.handleUserInteraction();
            applyLocale(appLocale === "en" ? "vi" : "en");
          }}
          ref={registerAccessibilityNode("auth:locale")}
          style={[styles.buttonSecondary, isAuthFocused("locale") ? styles.authFocused : undefined]}
        >
          <Text style={styles.buttonText}>
            {localization.t("locale")}: {appLocale.toUpperCase()}
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
        onPress={() => {
          void audio.handleUserInteraction();
          toggleSelfVoicing();
        }}
        ref={registerAccessibilityNode("screen-reader:sv-toggle")}
        style={Platform.OS === "web" ? styles.screenReaderOnly : styles.nativeScreenReaderOnlyControl}
      >
        <Text>{localization.t(selfVoicingEnabled ? "sv-toggle-button-off" : "sv-toggle-button-on")}</Text>
      </Pressable>
    );
  };

  const renderNativeFallbackBar = () => {
    if (!showNativeFallbackButtons) {
      return null;
    }

    const fallbackButtons = [
      {
        id: "primary",
        label: fallbackPrimaryActionLabel,
        onPress: () => {
          void audio.handleUserInteraction();
          handleSystemSwipe("up");
        },
      },
      {
        id: "chat",
        label: localization.t("mode-chat"),
        onPress: () => {
          void audio.handleUserInteraction();
          toggleOverlay("chat");
        },
      },
      {
        id: "history",
        label: localization.t("mode-history"),
        onPress: () => {
          void audio.handleUserInteraction();
          toggleOverlay("history");
        },
      },
      {
        id: "shortcuts",
        label: localization.t("mode-shortcuts"),
        onPress: () => {
          void audio.handleUserInteraction();
          toggleOverlay("shortcuts");
        },
      },
    ];

    return (
      <View style={styles.nativeFallbackBar}>
        {fallbackButtons.map((button) => (
          <Pressable
            accessibilityLabel={button.label}
            accessibilityRole="button"
            accessible
            key={button.id}
            onPress={button.onPress}
            style={styles.nativeFallbackButton}
          >
            <Text style={styles.buttonText}>{button.label}</Text>
          </Pressable>
        ))}
      </View>
    );
  };

  return (
    <SafeAreaView
      style={styles.safeArea}
      {...gestures.panHandlers}
    >
      <StatusBar style="light" />
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.container}
      >
        {renderScreenReaderOnlyControls()}
        {dialogState ? renderDialogOverlay() : inputState ? (
          <View style={styles.inputOverlayScreen}>
            <View style={styles.inputOverlayCard}>
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
                  placeholderTextColor="#7f8a93"
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
            </View>
          </View>
        ) : (
          <>
            <View style={styles.header}>
              <Text style={styles.title}>{localization.t("app-title")}</Text>
              <Text style={styles.subtitle}>{statusText}</Text>
              <Text style={styles.subtitle}>Client: Mobile</Text>
              <Text style={styles.subtitle}>Build: {MOBILE_BUILD_STAMP}</Text>
            </View>

            {!connected ? renderAuthCard() : null}
            {renderOverlay()}
            {renderNativeFallbackBar()}

            <View style={styles.footer}>
              <Text style={styles.helpText}>{localization.t("footer-gestures-line-1")}</Text>
              <Text style={styles.helpText}>{localization.t("footer-gestures-line-2")}</Text>
              <Text style={styles.helpText}>
                {connected ? localization.t("status-connected") : localization.t("status-disconnected")} |{" "}
                {mode}
              </Text>
            </View>
            <Text
              accessibilityLiveRegion="polite"
              key={`screen-reader-announcement-${screenReaderAnnouncement.id}`}
              style={styles.screenReaderOnly}
            >
              {screenReaderAnnouncement.text}
            </Text>
          </>
        )}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: "#11161d",
    flex: 1,
  },
  container: {
    flex: 1,
    gap: 12,
    padding: 16,
  },
  header: {
    gap: 4,
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
    height: 48,
    opacity: 0.01,
    position: "absolute",
    right: 8,
    top: 8,
    width: 48,
    zIndex: 10,
  },
  title: {
    color: "#f6f7fb",
    fontSize: 28,
    fontWeight: "700",
  },
  subtitle: {
    color: "#b6c1ca",
    fontSize: 14,
  },
  loginCard: {
    backgroundColor: "#1a222d",
    borderRadius: 14,
    gap: 10,
    padding: 14,
  },
  authTabs: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  authTab: {
    backgroundColor: "#32414d",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  authTabActive: {
    backgroundColor: "#3567e3",
  },
  authFocused: {
    borderColor: "#7fd4ff",
    borderWidth: 2,
  },
  authFieldFocused: {
    borderColor: "#7fd4ff",
    borderRadius: 12,
    borderWidth: 2,
    padding: 2,
  },
  input: {
    backgroundColor: "#0f141a",
    borderColor: "#293746",
    borderRadius: 10,
    borderWidth: 1,
    color: "#f6f7fb",
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
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  buttonDanger: {
    backgroundColor: "#a33b36",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  buttonText: {
    color: "#f6f7fb",
    fontWeight: "600",
  },
  panel: {
    backgroundColor: "#1a222d",
    borderRadius: 14,
    flex: 1,
    padding: 14,
  },
  panelTitle: {
    color: "#f6f7fb",
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 10,
  },
  scrollArea: {
    flex: 1,
  },
  gridMenuArea: {
    alignContent: "flex-start",
    flex: 1,
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  menuItem: {
    backgroundColor: "#11161d",
    borderColor: "#263443",
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 8,
    padding: 12,
  },
  gridMenuItem: {
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 0,
    paddingHorizontal: 6,
    paddingVertical: 6,
  },
  menuItemFocused: {
    borderColor: "#7fd4ff",
    borderWidth: 2,
  },
  menuText: {
    color: "#f6f7fb",
    fontSize: 16,
  },
  historyText: {
    color: "#d8e0e6",
    fontSize: 15,
    marginBottom: 8,
  },
  helpText: {
    color: "#9dacb8",
    fontSize: 12,
    marginTop: 6,
  },
  inputOverlayScreen: {
    alignItems: "center",
    flex: 1,
    justifyContent: "center",
  },
  inputOverlayCard: {
    backgroundColor: "#1b2430",
    borderColor: "#3567e3",
    borderRadius: 14,
    borderWidth: 1,
    gap: 12,
    maxWidth: 640,
    padding: 16,
    width: "100%",
  },
  dialogCard: {
    backgroundColor: "#1b2430",
    borderColor: "#3567e3",
    borderRadius: 14,
    borderWidth: 1,
    gap: 14,
    maxWidth: 640,
    padding: 16,
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
    gap: 2,
  },
  nativeFallbackBar: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    justifyContent: "space-between",
  },
  nativeFallbackButton: {
    backgroundColor: "#32414d",
    borderRadius: 10,
    flexBasis: "48%",
    flexGrow: 1,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
});
