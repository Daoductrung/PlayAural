import { StatusBar } from "expo-status-bar";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as SecureStore from "expo-secure-store";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  BackHandler,
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
  PongPacket,
  RegisterResponsePacket,
  RequestInputPacket,
  RequestPasswordResetResponsePacket,
  ServerPacket,
  SpeakPacket,
  SubmitResetCodeResponsePacket,
  UpdateLocalePacket,
  UpdatePreferencePacket,
} from "../network/packets";
import { BufferStore, type BufferName } from "../state/BufferStore";
import { TtsManager } from "../tts/TtsManager";

const MOBILE_CLIENT_VERSION = "1.0.2";
const MOBILE_BUILD_STAMP = "2026-04-11 14:18:24 +07:00";
const DEFAULT_SERVER_URL = "wss://playaural.ddt.one:443";
const APK_DOWNLOAD_URL =
  "https://github.com/Daoductrung/PlayAural/releases/latest/download/PlayAural.apk";
const CLIENT_CONFIG_STORAGE_KEY = "playaural.mobile.clientConfig";
const CLIENT_PASSWORD_STORAGE_KEY = "playaural.mobile.password";

type AppMode = "chat" | "history" | "main" | "shortcuts";
type AuthMode = "forgot" | "login" | "register" | "reset";

type FocusableMenuItem = {
  id?: string;
  text: string;
};

type MenuState = {
  escapeBehavior: string;
  focusIndex: number;
  gridEnabled: boolean;
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
  kind: "input" | "message" | "send";
  text: string;
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
  gridWidth: 1,
  items: [],
  menuId: "",
};

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

export function PlayAuralApp() {
  const localization = useMemo(() => new MobileLocalization(), []);
  const buffers = useMemo(() => new BufferStore(), []);
  const tts = useMemo(() => new TtsManager(), []);
  const audio = useMemo(() => new MobileAudioManager(), []);

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
  const [historyRevision, setHistoryRevision] = useState(0);
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

  const menuStateRef = useRef(menuState);
  const inputStateRef = useRef(inputState);
  const handleSystemSwipeRef = useRef<((direction: "up" | "down" | "left" | "right") => void) | null>(null);
  const lastPingStartedAtRef = useRef<number | null>(lastPingStartedAt);
  const preferencesRef = useRef<Record<string, unknown>>(preferences);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectWindowStartedAtRef = useRef<number | null>(null);
  const reconnectDelayMsRef = useRef(1000);
  const reconnectAttemptsRef = useRef(0);
  const manualDisconnectRef = useRef(false);
  const allowReconnectRef = useRef(false);
  const expectingReconnectRef = useRef(false);
  const sessionEstablishedRef = useRef(false);
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
    credentialsRef.current = {
      password,
      serverUrl,
      username,
    };
  }, [password, serverUrl, username]);

  const announce = (text: string, buffer: BufferName = "system", speak = true) => {
    buffers.add(buffer, text);
    setHistoryRevision((value) => value + 1);
    if (speak && !buffers.isMuted(buffer)) {
      tts.speakAnnouncement(text, { remember: false });
    }
  };

  const localizeSystemMessage = useCallback((message: string | undefined, fallbackKey = "status-disconnected") => {
    if (!message) {
      return localization.t(fallbackKey);
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
    return message;
  }, [localization]);

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

  useEffect(() => {
    void audio.initialize();
  }, [audio]);

  useEffect(() => () => {
    clearReconnectTimer();
  }, [clearReconnectTimer]);

  useEffect(() => {
    void loadStoredClientState();
  }, []);

  useEffect(() => {
    void persistClientState();
  }, [storageReady, appLocale, preferences, registerEmail, serverUrl, username, password]);

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
      const [storedConfigRaw, storedPassword] = await Promise.all([
        AsyncStorage.getItem(CLIENT_CONFIG_STORAGE_KEY),
        SecureStore.getItemAsync(CLIENT_PASSWORD_STORAGE_KEY),
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
    if (!packet.text) {
      return;
    }
    const buffer = (packet.buffer ?? "misc") as BufferName;
    buffers.add(buffer, packet.text);
    setHistoryRevision((value) => value + 1);
    if (!packet.muted && !buffers.isMuted(buffer)) {
      tts.speakAnnouncement(packet.text);
    }
  };

  const applyMenuPacket = (packet: MenuPacket, overrideItems?: Array<string | MenuItemData>) => {
    if (inputStateRef.current) {
      return;
    }

    const items = normalizeMenuItems(overrideItems ?? packet.items ?? []);
    const itemIds = items.map((item) => item.id);
    const previous = menuStateRef.current;
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
    stopGameAudio(true);
    tts.stop();
    if (Platform.OS === "android") {
      BackHandler.exitApp();
    }
  };

  const resetToLoginScreen = useCallback((statusMessage: string, authMessage = statusMessage) => {
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
  }, []);

  const handleTerminalSessionExit = useCallback((message: string, announceMessage = true) => {
    disableAutoReconnect();
    connectionRef.current?.disconnect();
    stopGameAudio(true);
    tts.stop();
    if (announceMessage) {
      announce(message, "system");
    }
    resetToLoginScreen(message);
    if (Platform.OS === "android") {
      BackHandler.exitApp();
    }
  }, [announce, disableAutoReconnect, resetToLoginScreen, tts]);

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
        console.info("PLAYAURAL_DEBUG Packet", packet.type);
        if (packet.type === "authorize_success") {
          const authPacket = packet as AuthorizeSuccessPacket;
          manualDisconnectRef.current = false;
          allowReconnectRef.current = true;
          expectingReconnectRef.current = false;
          sessionEstablishedRef.current = true;
          resetReconnectState();
          applyLocale(authPacket.locale);
          applyPreferenceUpdates(extractPreferenceUpdates(authPacket));
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
          handleTerminalSessionExit(reason);
          return;
        }

        if (packet.type === "login_failed") {
          const failurePacket = packet as LoginFailedPacket;
          const reason = localizeSystemMessage(
            failurePacket.text || failurePacket.reason,
            "auth-login-failed",
          );
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
          announce(localization.t("input-opened"), "system");
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
          const _pongPacket = packet as PongPacket;
          const startedAt = lastPingStartedAtRef.current;
          if (startedAt) {
            const elapsed = Date.now() - startedAt;
            setLastPingStartedAt(null);
            announce(localization.t("shortcut-ping-result", { value: elapsed }), "system");
          }
          return;
        }

        if (packet.type === "register_response") {
          const response = packet as RegisterResponsePacket;
          const text =
            response.text ||
            (response.status === "success"
              ? localization.t("auth-register-success")
              : localization.t("auth-register-failed"));
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
          const text =
            response.text ||
            (response.status === "success"
              ? localization.t("auth-forgot-success")
              : localization.t("auth-forgot-failed"));
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
          const text =
            response.text ||
            (response.status === "success"
              ? localization.t("auth-reset-success")
              : localization.t("auth-reset-failed"));
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
    console.info("PLAYAURAL_DEBUG App build", {
      build: MOBILE_BUILD_STAMP,
      version: MOBILE_CLIENT_VERSION,
    });
    applyLocale(appLocale);
    setStatusText(localization.t("status-disconnected"));
  }, []);

  useEffect(() => {
    if (!connected && !statusText) {
      setStatusText(localization.t("status-disconnected"));
    }
  }, [connected, localization, statusText]);

  const connection = connectionRef.current;
  const historyMessages = buffers.getMessages("all").reverse();
  const chatMessages = buffers.getMessages("chat").reverse();
  const focusedHistoryMessage = historyMessages[historyIndex] ?? null;
  const focusedMenuItem = menuState.items[menuState.focusIndex];
  const focusedDialogButton = dialogState?.buttons[dialogState.focusIndex] ?? null;
  const chatFocusItems: ChatFocusItem[] = [
    { kind: "input", text: localization.t("chat-input-focus") },
    { kind: "send", text: localization.t("chat-send-button") },
    ...chatMessages.map((message, index) => ({
      kind: "message" as const,
      text: message.text,
    })),
  ];
  const focusedChatItem = chatFocusItems[chatFocusIndex] ?? null;
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

    items.push(...(["login", "register", "forgot"] as const).map((candidate) => ({
      action: "toggle_locale" as const,
      id: `tab-${candidate}`,
      text: localization.t(`auth-mode-${candidate}`),
    })));

    return items;
  }, [appLocale, authMode, connected, localization, password, username]);
  const focusedAuthItem = authFocusableItems[authFocusIndex] ?? null;

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

  useEffect(() => {
    setAuthFocusIndex((current) => clamp(current, 0, Math.max(0, authFocusableItems.length - 1)));
  }, [authFocusableItems]);

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

    if (item.id === "tab-login") {
      setAuthMode("login");
      setAuthStatusText("");
      return;
    }
    if (item.id === "tab-register") {
      setAuthMode("register");
      setAuthStatusText("");
      return;
    }
    if (item.id === "tab-forgot") {
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
    const item = itemOverride ?? menuState.items[menuState.focusIndex];
    if (!item) {
      return;
    }
    connection?.send({
      menu_id: menuState.menuId || undefined,
      selection: (indexOverride ?? menuState.focusIndex) + 1,
      selection_id: item.id,
      type: "menu",
    });
  };

  const sendEscape = () => {
    connection?.send({
      menu_id: menuState.menuId || undefined,
      type: "escape",
    });
  };

  const sendEscapeEquivalent = (
    menuId: string,
    escapeBehavior: string,
    items: FocusableMenuItem[],
  ) => {
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
    connection?.send({
      menu_id: menuState.menuId || "turn_menu",
      selection: 1,
      selection_id: "web_actions_menu",
      type: "menu",
    });
  };

  const sendShiftEnter = (itemOverride?: FocusableMenuItem | null) => {
    const item = itemOverride ?? menuState.items[menuState.focusIndex];
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
    announce(localization.t("overlay-closed", { name }), "system");
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
      announce(localization.t(key, { name: localization.t(`mode-${nextMode}`) }), "system");
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
      announce(localization.t("shortcut-ping-sent"), "system");
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
      announce(localization.t("shortcut-music-volume", { value: nextValue }), "system");
      return;
    }
    if (shortcut.id === "music_up") {
      const nextValue = clamp(Math.round(audio.getMusicVolume() * 100) + 10, 0, 100);
      syncPreference("audio/music_volume", nextValue);
      announce(localization.t("shortcut-music-volume", { value: nextValue }), "system");
      return;
    }
    if (shortcut.id === "ambience_down") {
      const nextValue = clamp(Math.round(audio.getAmbienceVolume() * 100) - 10, 0, 100);
      syncPreference("audio/ambience_volume", nextValue);
      announce(localization.t("shortcut-ambience-volume", { value: nextValue }), "system");
      return;
    }
    if (shortcut.id === "ambience_up") {
      const nextValue = clamp(Math.round(audio.getAmbienceVolume() * 100) + 10, 0, 100);
      syncPreference("audio/ambience_volume", nextValue);
      announce(localization.t("shortcut-ambience-volume", { value: nextValue }), "system");
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
    announce(localization.t("input-submitted"), "system");
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
      announce(localization.t("gesture-no-last"), "system");
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
        setInputState(null);
        setInputValue("");
        setInputOverlayFocus(0);
        announce(localization.t("input-cancelled"), "system");
        return;
      }
      if (connected && mode === "main" && menuState.menuId === "turn_menu") {
        playMenuActivateSound();
        openActionsMenu();
        return;
      }
      if (connected && mode === "main" && menuState.menuId === "main_menu") {
        confirmLogout();
        return;
      }
      sendEscapeEquivalent(menuState.menuId, menuState.escapeBehavior, menuState.items);
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

  const handleStopSpeech = () => {
    tts.stop();
    announce(localization.t("gesture-stop-tts"), "system", false);
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
    enabled: true,
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
    onTwoFingerSwipe: handleSystemSwipe,
    onTwoFingerTap: handleStopSpeech,
  });

  useEffect(() => {
    if (Platform.OS !== "web" || typeof window === "undefined") {
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
  }, [handleBoundaryJump, handleDirectionalNavigation, handleModifiedActivate, handlePrimaryActivate, handleSystemSwipe]);

  useEffect(() => {
    const focusSpeechOptions = {
      interruptAnnouncement: false,
      interruptUi: false,
    };

    if (!connected) {
      if (focusedAuthItem?.text) {
        tts.speakUi(focusedAuthItem.text, focusSpeechOptions);
      }
      return;
    }
    if (dialogState && focusedDialogButton) {
      tts.speakUi(focusedDialogButton.text, focusSpeechOptions);
      return;
    }
    if (inputState && focusedInputOverlayText) {
      tts.speakUi(focusedInputOverlayText, focusSpeechOptions);
      return;
    }
    if (mode === "main") {
      if (focusedMenuItem?.text) {
        tts.speakUi(focusedMenuItem.text, focusSpeechOptions);
      } else if (menuState.items.length === 0) {
        tts.speakUi(localization.t("menu-empty"), focusSpeechOptions);
      }
      return;
    }
    if (mode === "shortcuts" && focusedShortcutItem) {
      tts.speakUi(focusedShortcutItem.text, focusSpeechOptions);
      return;
    }
    if (mode === "history" && focusedHistoryMessage) {
      tts.speakUi(focusedHistoryMessage.text, focusSpeechOptions);
      return;
    }
    if (mode === "chat" && focusedChatItem) {
      tts.speakUi(focusedChatItem.text, focusSpeechOptions);
    }
  }, [
    connected,
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
  ]);

  const connect = () => {
    if (!serverUrl || !username || !password) {
      const message = localization.t("login-required");
      setAuthStatusText(message);
      announce(message, "system");
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
      announce(message, "system");
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
        const text =
          registerResponse.text ||
          (registerResponse.status === "success"
            ? localization.t("auth-register-success")
            : localization.t("auth-register-failed"));
        setAuthStatusText(text);
        announce(text, "system");
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
        const text =
          forgotResponse.text ||
          (forgotResponse.status === "success"
            ? localization.t("auth-forgot-success")
            : localization.t("auth-forgot-failed"));
        setAuthStatusText(text);
        announce(text, "system");
        if (forgotResponse.status === "success") {
          setResetEmail(forgotEmail.trim());
          setAuthMode("reset");
        }
        return;
      }

      const resetResponse = response as SubmitResetCodeResponsePacket;
      const text =
        resetResponse.text ||
        (resetResponse.status === "success"
          ? localization.t("auth-reset-success")
          : localization.t("auth-reset-failed"));
      setAuthStatusText(text);
      announce(text, "system");
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
      announce(message, "system");
    }
  };

  const submitRegistration = async () => {
    if (!username.trim() || !password || !registerEmail.trim()) {
      const message = localization.t("auth-register-required");
      setAuthStatusText(message);
      announce(message, "system");
      return;
    }
    if (password !== registerConfirmPassword) {
      const message = localization.t("auth-password-mismatch");
      setAuthStatusText(message);
      announce(message, "system");
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
      announce(message, "system");
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
      announce(message, "system");
      return;
    }
    if (resetPassword !== resetConfirmPassword) {
      const message = localization.t("auth-password-mismatch");
      setAuthStatusText(message);
      announce(message, "system");
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
    <View style={styles.panel}>
      <Text style={styles.panelTitle}>{localization.t("mode-main")}</Text>
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
            style={[
              styles.menuItem,
              index === menuState.focusIndex ? styles.menuItemFocused : undefined,
            ]}
          >
            <Text style={styles.menuText}>{item.text}</Text>
          </Pressable>
        ))}
      </ScrollView>
    </View>
  );

  const renderChatOverlay = () => (
    <View style={styles.panel}>
      <Text style={styles.panelTitle}>{localization.t("mode-chat")}</Text>
      <Text style={styles.helpText}>{localization.t("chat-input-label")}</Text>
      <View style={chatFocusIndex === 0 ? styles.authFieldFocused : undefined}>
        <TextInput
          onChangeText={setChatDraft}
          onFocus={() => {
            setChatFocusIndex(0);
          }}
          onSubmitEditing={submitChat}
          placeholder={localization.t("chat-placeholder")}
          placeholderTextColor="#7f8a93"
          ref={chatInputRef}
          style={styles.input}
          value={chatDraft}
        />
      </View>
      <Pressable
        accessibilityLabel={localization.t("chat-send-button")}
        accessibilityRole="button"
        accessible
        onPress={() => {
          void audio.handleUserInteraction();
          submitChat();
        }}
        onFocus={() => {
          setChatFocusIndex(1);
        }}
        style={[
          styles.button,
          chatFocusIndex === 1 ? styles.menuItemFocused : undefined,
        ]}
      >
        <Text style={styles.buttonText}>{localization.t("chat-send-button")}</Text>
      </Pressable>
      <ScrollView style={styles.scrollArea}>
        {chatMessages.map((item, index) => (
          <Pressable
            accessibilityLabel={item.text}
            accessibilityRole="button"
            accessible
            key={`chat-${item.timestamp}-${index}`}
            onFocus={() => {
              setChatFocusIndex(index + 2);
            }}
            onPress={() => {
              setChatFocusIndex(index + 2);
              speakUserFocus(item.text);
            }}
            style={[
              styles.menuItem,
              chatFocusIndex === index + 2 ? styles.menuItemFocused : undefined,
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
      <Text style={styles.historyText}>
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
        <Pressable style={[styles.authTab, styles.authTabActive]}>
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
              autoCapitalize="none"
              onChangeText={setUsername}
              onFocus={() => {
                focusAuthItemById("field-username");
              }}
              placeholder={localization.t("username")}
              placeholderTextColor="#7f8a93"
              ref={usernameInputRef}
              style={styles.input}
              value={username}
            />
          </View>
          <View style={isAuthFocused("field-password") ? styles.authFieldFocused : undefined}>
            <TextInput
              onChangeText={setPassword}
              onFocus={() => {
                focusAuthItemById("field-password");
              }}
              placeholder={localization.t("password")}
              placeholderTextColor="#7f8a93"
              ref={passwordInputRef}
              secureTextEntry
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
              autoCapitalize="none"
              onChangeText={setUsername}
              onFocus={() => {
                focusAuthItemById("field-username");
              }}
              placeholder={localization.t("username")}
              placeholderTextColor="#7f8a93"
              ref={usernameInputRef}
              style={styles.input}
              value={username}
            />
          </View>
          <View style={isAuthFocused("field-register-email") ? styles.authFieldFocused : undefined}>
            <TextInput
              autoCapitalize="none"
              keyboardType="email-address"
              onChangeText={setRegisterEmail}
              onFocus={() => {
                focusAuthItemById("field-register-email");
              }}
              placeholder={localization.t("auth-email")}
              placeholderTextColor="#7f8a93"
              ref={registerEmailInputRef}
              style={styles.input}
              value={registerEmail}
            />
          </View>
          <View style={isAuthFocused("field-password") ? styles.authFieldFocused : undefined}>
            <TextInput
              onChangeText={setPassword}
              onFocus={() => {
                focusAuthItemById("field-password");
              }}
              placeholder={localization.t("password")}
              placeholderTextColor="#7f8a93"
              ref={passwordInputRef}
              secureTextEntry
              style={styles.input}
              value={password}
            />
          </View>
          <View style={isAuthFocused("field-register-confirm-password") ? styles.authFieldFocused : undefined}>
            <TextInput
              onChangeText={setRegisterConfirmPassword}
              onFocus={() => {
                focusAuthItemById("field-register-confirm-password");
              }}
              placeholder={localization.t("auth-confirm-password")}
              placeholderTextColor="#7f8a93"
              ref={registerConfirmPasswordInputRef}
              secureTextEntry
              style={styles.input}
              value={registerConfirmPassword}
            />
          </View>
          <View style={isAuthFocused("field-register-bio") ? styles.authFieldFocused : undefined}>
            <TextInput
              multiline
              onChangeText={setRegisterBio}
              onFocus={() => {
                focusAuthItemById("field-register-bio");
              }}
              placeholder={localization.t("auth-bio")}
              placeholderTextColor="#7f8a93"
              ref={registerBioInputRef}
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
              autoCapitalize="none"
              keyboardType="email-address"
              onChangeText={setForgotEmail}
              onFocus={() => {
                focusAuthItemById("field-forgot-email");
              }}
              placeholder={localization.t("auth-email")}
              placeholderTextColor="#7f8a93"
              ref={forgotEmailInputRef}
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
              autoCapitalize="none"
              keyboardType="email-address"
              onChangeText={setResetEmail}
              onFocus={() => {
                focusAuthItemById("field-reset-email");
              }}
              placeholder={localization.t("auth-email")}
              placeholderTextColor="#7f8a93"
              ref={resetEmailInputRef}
              style={styles.input}
              value={resetEmail}
            />
          </View>
          <View style={isAuthFocused("field-reset-code") ? styles.authFieldFocused : undefined}>
            <TextInput
              autoCapitalize="characters"
              onChangeText={setResetCode}
              onFocus={() => {
                focusAuthItemById("field-reset-code");
              }}
              placeholder={localization.t("auth-reset-code")}
              placeholderTextColor="#7f8a93"
              ref={resetCodeInputRef}
              style={styles.input}
              value={resetCode}
            />
          </View>
          <View style={isAuthFocused("field-reset-password") ? styles.authFieldFocused : undefined}>
            <TextInput
              onChangeText={setResetPassword}
              onFocus={() => {
                focusAuthItemById("field-reset-password");
              }}
              placeholder={localization.t("auth-new-password")}
              placeholderTextColor="#7f8a93"
              ref={resetPasswordInputRef}
              secureTextEntry
              style={styles.input}
              value={resetPassword}
            />
          </View>
          <View style={isAuthFocused("field-reset-confirm-password") ? styles.authFieldFocused : undefined}>
            <TextInput
              onChangeText={setResetConfirmPassword}
              onFocus={() => {
                focusAuthItemById("field-reset-confirm-password");
              }}
              placeholder={localization.t("auth-confirm-password")}
              placeholderTextColor="#7f8a93"
              ref={resetConfirmPasswordInputRef}
              secureTextEntry
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
          style={[styles.buttonSecondary, isAuthFocused("locale") ? styles.authFocused : undefined]}
        >
          <Text style={styles.buttonText}>
            {localization.t("locale")}: {appLocale.toUpperCase()}
          </Text>
        </Pressable>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea} {...gestures.panHandlers}>
      <StatusBar style="light" />
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.container}
      >
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
                  editable={!inputState.readOnly}
                  maxLength={inputState.maxLength}
                  multiline={inputState.multiline}
                  onChangeText={setInputValue}
                  onFocus={() => {
                    setInputOverlayFocus(0);
                  }}
                  placeholder={inputState.prompt}
                  placeholderTextColor="#7f8a93"
                  ref={inputOverlayInputRef}
                  selectTextOnFocus
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

            <View style={styles.footer}>
              <Text style={styles.helpText}>{localization.t("footer-gestures-line-1")}</Text>
              <Text style={styles.helpText}>{localization.t("footer-gestures-line-2")}</Text>
              <Text style={styles.helpText}>
                {connected ? localization.t("status-connected") : localization.t("status-disconnected")} |{" "}
                {mode}
              </Text>
            </View>
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
    gap: 10,
  },
  button: {
    backgroundColor: "#3567e3",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
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
  menuItem: {
    backgroundColor: "#11161d",
    borderColor: "#263443",
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 8,
    padding: 12,
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
});
