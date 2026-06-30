import { createA11y } from "./a11y.js";
import { createAudioEngine } from "./audio.js";
import { installKeybinds } from "./keybinds.js";
import { createNetworkClient, loadPacketValidator } from "./network.js";
import { createStore } from "./store.js";
import { AVAILABLE_LOCALES, DEFAULT_LOCALE, loadLocaleBundle, normalizeLocale } from "./locales/index.js";
import { createHistoryView } from "./ui/history.js";
import { createMenuView } from "./ui/menus.js";

const CLIENT_VERSION = String(window.PLAYAURAL_WEB_VERSION || "1.0.4.7");
const WEB_CLIENT_CONFIG = window.PLAYAURAL_WEB_CONFIG || {};
const DEFAULT_SERVER_URL = String(
  WEB_CLIENT_CONFIG.serverUrl
  || window.PLAYAURAL_SERVER_URL
  || "wss://playaural.ddt.one:443",
).trim();
const CONFIG_KEY = "playaural_config";
const REMEMBER_KEY = "pa_remember";
const USER_KEY = "pa_user";
const PASS_KEY = "pa_pass";
const LANG_KEY = "pa_lang";
const RECONNECT_WINDOW_MS = 30000;
const RECONNECT_INITIAL_DELAY_MS = 1000;
const RECONNECT_MAX_DELAY_MS = 10000;
const SERVER_RESTART_RECONNECT_DELAY_MS = 3000;
const WEB_SPEECH_PREF_MIN = 10;
const WEB_SPEECH_PREF_NORMAL = 100;
const WEB_SPEECH_PREF_MAX = 300;
const WEB_SPEECH_RATE_MIN = 0.1;
const WEB_SPEECH_RATE_NORMAL = 1;
const WEB_SPEECH_RATE_MAX = 10;
const MESSAGE_ALIASES = {
  "voice-unavailable": "voice-chat-unavailable",
};
const RECAPTCHA_SITE_KEY = String(
  window.PLAYAURAL_RECAPTCHA_SITE_KEY || window.RECAPTCHA_SITE_KEY || "",
).trim();

let recaptchaReadyPromise = null;

function byId(id) {
  return document.getElementById(id);
}

function clampNumber(value, min, max, fallback = min) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return fallback;
  }
  return Math.max(min, Math.min(max, number));
}

function snapNumberToStep(value, min, max, fallback = min, step = 1) {
  const bounded = clampNumber(value, min, max, fallback);
  const parsedStep = Number(step);
  if (!Number.isFinite(parsedStep) || parsedStep <= 1) {
    return Math.round(bounded);
  }
  const snapped = Math.round((bounded - min) / parsedStep) * parsedStep + min;
  return clampNumber(snapped, min, max, fallback);
}

function safeJsonParse(value, fallback) {
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
}

function normalizeBuffer(buffer) {
  if (buffer === "chats") {
    return "chat";
  }
  if (["game", "system", "chat", "misc"].includes(buffer)) {
    return buffer;
  }
  return "misc";
}

function webSpeechRateFromPreference(value) {
  const pref = clampNumber(value, WEB_SPEECH_PREF_MIN, WEB_SPEECH_PREF_MAX, WEB_SPEECH_PREF_NORMAL);
  if (pref <= WEB_SPEECH_PREF_NORMAL) {
    return clampNumber(pref / WEB_SPEECH_PREF_NORMAL, WEB_SPEECH_RATE_MIN, WEB_SPEECH_RATE_NORMAL, WEB_SPEECH_RATE_NORMAL);
  }
  const ratio = (pref - WEB_SPEECH_PREF_NORMAL) / (WEB_SPEECH_PREF_MAX - WEB_SPEECH_PREF_NORMAL);
  return clampNumber(
    WEB_SPEECH_RATE_NORMAL + ratio * (WEB_SPEECH_RATE_MAX - WEB_SPEECH_RATE_NORMAL),
    WEB_SPEECH_RATE_MIN,
    WEB_SPEECH_RATE_MAX,
    WEB_SPEECH_RATE_NORMAL,
  );
}

function detectClientPlatform() {
  const nav = window.navigator || {};
  const userAgentDataPlatform = String(nav.userAgentData?.platform || "").trim();
  const userAgentDataMobile = nav.userAgentData?.mobile === true;
  const platform = String(userAgentDataPlatform || nav.platform || "").trim();
  const userAgent = String(nav.userAgent || "");
  const maxTouchPoints = Number(nav.maxTouchPoints || 0);
  const probe = `${platform} ${userAgent}`.toLowerCase();

  if (/iphone|ipod/.test(probe)) {
    return "iOS";
  }
  if (/ipad/.test(probe) || (platform === "MacIntel" && maxTouchPoints > 1)) {
    return "iPadOS";
  }
  if (/android/.test(probe) || (userAgentDataMobile && /linux/.test(probe))) {
    return "Android";
  }
  if (/windows|win32|win64|wow64/.test(probe)) {
    return "Windows";
  }
  if (/macintosh|mac os|macintel|macppc|mac68k/.test(probe)) {
    return "macOS";
  }
  if (/cros/.test(probe)) {
    return "ChromeOS";
  }
  if (/linux|x11/.test(probe)) {
    return "Linux";
  }
  return platform || "";
}

function clientAuthMetadata() {
  const platform = detectClientPlatform();
  return {
    client: "web",
    ...(platform ? { platform } : {}),
  };
}

function storageGet(key, remember = true) {
  const store = remember ? localStorage : sessionStorage;
  try {
    return store.getItem(key) || "";
  } catch {
    return "";
  }
}

function storageSet(key, value, remember = true) {
  const store = remember ? localStorage : sessionStorage;
  try {
    store.setItem(key, value);
  } catch {
    // Storage may be unavailable in hardened/private contexts.
  }
}

function storageRemove(key) {
  for (const store of [localStorage, sessionStorage]) {
    try {
      store.removeItem(key);
    } catch {
      // Ignore inaccessible storage.
    }
  }
}

function setRecaptchaVisibility(visible) {
  document.body?.classList.toggle("recaptcha-hidden", !visible);
}

async function ensureRecaptchaReady() {
  if (!RECAPTCHA_SITE_KEY) {
    return true;
  }
  if (typeof window.grecaptcha !== "undefined" && typeof window.grecaptcha.ready === "function") {
    await new Promise((resolve) => window.grecaptcha.ready(resolve));
    return true;
  }
  if (!recaptchaReadyPromise) {
    recaptchaReadyPromise = new Promise((resolve) => {
      const existing = document.querySelector('script[data-recaptcha="playaural"]');
      if (existing) {
        existing.addEventListener("load", () => {
          if (typeof window.grecaptcha !== "undefined" && typeof window.grecaptcha.ready === "function") {
            window.grecaptcha.ready(() => resolve(true));
          } else {
            resolve(false);
          }
        }, { once: true });
        existing.addEventListener("error", () => resolve(false), { once: true });
        return;
      }
      const script = document.createElement("script");
      script.src = `https://www.google.com/recaptcha/api.js?render=${encodeURIComponent(RECAPTCHA_SITE_KEY)}`;
      script.async = true;
      script.defer = true;
      script.dataset.recaptcha = "playaural";
      script.addEventListener("load", () => {
        if (typeof window.grecaptcha !== "undefined" && typeof window.grecaptcha.ready === "function") {
          window.grecaptcha.ready(() => resolve(true));
        } else {
          resolve(false);
        }
      }, { once: true });
      script.addEventListener("error", () => resolve(false), { once: true });
      document.head.appendChild(script);
    });
  }
  return recaptchaReadyPromise;
}

async function getCaptchaTokenResult(action) {
  if (!RECAPTCHA_SITE_KEY) {
    return { ok: true, token: "" };
  }
  const captchaReady = await ensureRecaptchaReady();
  if (!captchaReady || typeof window.grecaptcha === "undefined") {
    return { ok: false, token: "", reason: "auth-error-captcha-unavailable" };
  }
  try {
    const token = await window.grecaptcha.execute(RECAPTCHA_SITE_KEY, { action });
    if (!token) {
      return { ok: false, token: "", reason: "auth-error-captcha-unavailable" };
    }
    return { ok: true, token };
  } catch {
    return { ok: false, token: "", reason: "auth-error-captcha-execute-failed" };
  }
}

const Localization = {
  locale: DEFAULT_LOCALE,
  strings: {},
  fallback: {},

  resolveKey(key) {
    return MESSAGE_ALIASES[key] || key;
  },

  async load(locale) {
    const bundle = await loadLocaleBundle(locale);
    this.locale = bundle.locale;
    this.strings = bundle.messages;
    this.fallback = bundle.fallback;
    document.documentElement.lang = bundle.locale;
    storageSet(LANG_KEY, bundle.locale);
  },

  has(key) {
    const lookupKey = this.resolveKey(key);
    return Object.prototype.hasOwnProperty.call(this.strings, lookupKey)
      || Object.prototype.hasOwnProperty.call(this.fallback, lookupKey);
  },

  get(key, params = {}) {
    if (!key) {
      return "";
    }
    const lookupKey = this.resolveKey(key);
    let value = this.strings[lookupKey] ?? this.fallback[lookupKey] ?? key;
    for (const [name, raw] of Object.entries(params || {})) {
      const replacement = String(raw);
      value = value
        .replaceAll(`{${name}}`, replacement)
        .replaceAll(`{$${name}}`, replacement);
    }
    return value;
  },
};

class WebSpeechManager {
  constructor({ getPreferences }) {
    this.getPreferences = getPreferences;
    this.voices = [];
    this.targetVoice = null;
    this.queue = [];
    this.playing = false;
    this.timeoutId = null;
    this.keepAliveId = null;
    this.currentUtterance = null;
    this.activeText = "";
    this.token = 0;
    this.lastSpeechMode = null;
    this.lastSpeechRate = null;
    this.lastSpeechVoice = null;
    this.voiceSignature = "";
    this.voiceRefreshTimers = [];

    if (window.speechSynthesis) {
      this.refreshVoices();
      const handleVoicesChanged = () => {
        this.refreshVoices();
        this.updateTargetVoice();
        this.onVoicesChanged?.();
      };
      if (typeof window.speechSynthesis.addEventListener === "function") {
        window.speechSynthesis.addEventListener("voiceschanged", handleVoicesChanged);
      } else {
        window.speechSynthesis.onvoiceschanged = handleVoicesChanged;
      }
    }
  }

  applyPreferences() {
    const prefs = this.getPreferences();
    const speechMode = prefs.speech_mode || "aria";
    const speechRate = prefs.speech_rate;
    const speechVoice = prefs.speech_voice || "";
    const hasPreviousPrefs = this.lastSpeechMode !== null;
    const speechSettingsChanged = hasPreviousPrefs && (
      this.lastSpeechMode !== speechMode
      || this.lastSpeechRate !== speechRate
      || this.lastSpeechVoice !== speechVoice
    );
    this.lastSpeechMode = speechMode;
    this.lastSpeechRate = speechRate;
    this.lastSpeechVoice = speechVoice;

    this.updateTargetVoice();
    if (speechMode === "web_speech") {
      this.startKeepAlive();
      if (speechSettingsChanged) {
        this.replayActiveSpeechForSettingsChange();
      }
    } else {
      this.stopKeepAlive();
      this.cancel();
    }
  }

  updateTargetVoice() {
    const prefs = this.getPreferences();
    if (!window.speechSynthesis || !prefs.speech_voice || prefs.speech_voice === "default") {
      this.targetVoice = null;
      return;
    }
    if (!this.voices.length) {
      this.refreshVoices();
    }
    this.targetVoice = this.findVoice(prefs.speech_voice);
  }

  refreshVoices() {
    const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    const uniqueVoices = [];
    const seen = new Set();
    for (const voice of voices) {
      const key = [
        voice.voiceURI || "",
        voice.name || "",
        voice.lang || "",
        voice.localService ? "local" : "remote",
        voice.default ? "default" : "",
      ].join("|");
      if (seen.has(key)) {
        continue;
      }
      seen.add(key);
      uniqueVoices.push(voice);
    }
    this.voices = uniqueVoices;
    this.voiceSignature = uniqueVoices
      .map((voice) => [
        this.voiceValue(voice),
        voice.name || "",
        voice.lang || "",
        voice.default ? "default" : "",
      ].join("|"))
      .join("\u001f");
    return this.voices.slice();
  }

  clearVoiceRefreshTimers() {
    for (const timer of this.voiceRefreshTimers) {
      window.clearTimeout(timer);
    }
    this.voiceRefreshTimers = [];
  }

  requestVoiceRefresh() {
    if (!window.speechSynthesis) {
      return [];
    }
    this.clearVoiceRefreshTimers();
    const run = () => {
      const before = this.voiceSignature;
      const voices = this.refreshVoices();
      this.updateTargetVoice();
      if (this.voiceSignature !== before) {
        this.onVoicesChanged?.();
      }
      return voices;
    };
    const voices = run();
    this.warmUp();
    for (const delay of [100, 350, 800, 1500, 3000]) {
      const timer = window.setTimeout(run, delay);
      this.voiceRefreshTimers.push(timer);
    }
    return voices;
  }

  voiceValue(voice) {
    if (!voice) {
      return "";
    }
    if (voice.voiceURI) {
      return voice.voiceURI;
    }
    return `${voice.name || ""}|${voice.lang || ""}`;
  }

  findVoice(value) {
    const target = String(value || "");
    if (!target || target === "default") {
      return null;
    }
    if (!this.voices.length) {
      this.refreshVoices();
    }
    return this.voices.find((voice) => (
      voice.voiceURI === target
      || voice.name === target
      || this.voiceValue(voice) === target
    )) || null;
  }

  warmUp() {
    if (!window.speechSynthesis) {
      return;
    }
    try {
      const utterance = new SpeechSynthesisUtterance("");
      utterance.volume = 0;
      window.speechSynthesis.speak(utterance);
    } catch {
      // Warm-up is best-effort only.
    }
  }

  chunkText(text, maxLength = 170) {
    const source = String(text || "").trim();
    if (!source) {
      return [];
    }
    if (source.length <= maxLength) {
      return [source];
    }
    const chunks = [];
    let remaining = source;
    while (remaining.length > maxLength) {
      let split = -1;
      for (const mark of [".", "!", "?", ";", ","]) {
        const index = remaining.lastIndexOf(mark, maxLength);
        if (index > split) {
          split = index;
        }
      }
      if (split < 0) {
        split = remaining.lastIndexOf(" ", maxLength);
      }
      if (split < 0) {
        split = maxLength;
      } else {
        split += 1;
      }
      chunks.push(remaining.slice(0, split).trim());
      remaining = remaining.slice(split).trim();
    }
    if (remaining) {
      chunks.push(remaining);
    }
    return chunks;
  }

  speak(text) {
    if (!window.speechSynthesis) {
      return;
    }
    for (const chunk of this.chunkText(text)) {
      this.queue.push(chunk);
    }
    this.processQueue();
  }

  speakNow(text) {
    this.cancel();
    this.speak(text);
  }

  finishUtterance(token) {
    if (token !== this.token || !this.playing) {
      return;
    }
    if (this.timeoutId) {
      window.clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
    this.playing = false;
    this.currentUtterance = null;
    this.activeText = "";
    window.setTimeout(() => this.processQueue(), 0);
  }

  estimateSpeechTimeoutMs(text, rate) {
    const effectiveRate = Math.max(0.2, Number(rate) || 1);
    const estimated = 5000 + (String(text || "").length * 120) / effectiveRate;
    return Math.max(6000, Math.min(120000, Math.ceil(estimated)));
  }

  processQueue() {
    if (this.playing || !this.queue.length || !window.speechSynthesis) {
      return;
    }
    const text = this.queue.shift();
    if (!text) {
      this.processQueue();
      return;
    }
    this.playing = true;
    this.activeText = text;
    const token = ++this.token;
    try {
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }
    } catch {
      // Continue with a fresh utterance below.
    }

    const utterance = new SpeechSynthesisUtterance(text);
    const prefs = this.getPreferences();
    utterance.rate = webSpeechRateFromPreference(prefs.speech_rate);
    utterance.lang = this.targetVoice?.lang || Localization.locale || "en";
    if (this.targetVoice) {
      utterance.voice = this.targetVoice;
    }

    const finish = () => this.finishUtterance(token);
    utterance.onend = finish;
    utterance.onerror = finish;
    this.currentUtterance = utterance;
    this.timeoutId = window.setTimeout(() => {
      if (token !== this.token || !this.playing) {
        return;
      }
      try {
        window.speechSynthesis.cancel();
      } catch {
        // Timeout recovery is best-effort.
      }
      this.finishUtterance(token);
    }, this.estimateSpeechTimeoutMs(text, utterance.rate));
    try {
      window.speechSynthesis.speak(utterance);
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }
    } catch {
      this.finishUtterance(token);
    }
  }

  cancel() {
    this.token += 1;
    this.queue = [];
    this.playing = false;
    this.currentUtterance = null;
    this.activeText = "";
    if (this.timeoutId) {
      window.clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
    try {
      window.speechSynthesis?.cancel();
    } catch {
      // Ignore engine reset failures.
    }
  }

  replayActiveSpeechForSettingsChange() {
    if (!window.speechSynthesis || !this.playing || !this.activeText) {
      return;
    }
    const active = this.activeText;
    const pending = this.queue.slice();
    this.token += 1;
    this.queue = [active, ...pending];
    this.playing = false;
    this.currentUtterance = null;
    this.activeText = "";
    if (this.timeoutId) {
      window.clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
    try {
      window.speechSynthesis.cancel();
    } catch {
      // Ignore engine reset failures.
    }
    this.processQueue();
  }

  startKeepAlive() {
    if (!window.speechSynthesis || this.keepAliveId) {
      return;
    }
    this.keepAliveId = window.setInterval(() => {
      if (document.hidden || this.playing || this.queue.length) {
        return;
      }
      try {
        const utterance = new SpeechSynthesisUtterance(" ");
        utterance.volume = 0;
        window.speechSynthesis.speak(utterance);
      } catch {
        // Keep-alive is best-effort.
      }
    }, 25000);
  }

  stopKeepAlive() {
    if (this.keepAliveId) {
      window.clearInterval(this.keepAliveId);
      this.keepAliveId = null;
    }
  }

  getVoices() {
    if (window.speechSynthesis && !this.voices.length) {
      this.refreshVoices();
    }
    return this.voices.slice();
  }
}

class Playlist {
  constructor(app, id, tracks = [], options = {}) {
    this.app = app;
    this.id = id;
    this.tracks = Array.isArray(tracks) ? tracks.slice() : [];
    this.audioType = options.audio_type || "music";
    this.shuffle = Boolean(options.shuffle);
    this.repeats = options.repeats ?? true;
    this.autoRemove = Boolean(options.auto_remove);
    this.index = 0;
    this.running = false;
  }

  start() {
    if (!this.tracks.length) {
      return;
    }
    this.running = true;
    this.index = 0;
    if (this.shuffle) {
      for (let i = this.tracks.length - 1; i > 0; i -= 1) {
        const j = Math.floor(Math.random() * (i + 1));
        [this.tracks[i], this.tracks[j]] = [this.tracks[j], this.tracks[i]];
      }
    }
    this.playNext();
  }

  stop() {
    this.running = false;
    if (this.audioType === "music") {
      this.app.audio.stopMusic();
    } else if (this.audioType === "ambience") {
      this.app.audio.stopAmbience();
    }
  }

  playNext() {
    if (!this.running || !this.tracks.length) {
      return;
    }
    if (this.index >= this.tracks.length) {
      if (!this.repeats) {
        this.running = false;
        if (this.autoRemove) {
          this.app.removePlaylist(this.id);
        }
        return;
      }
      this.index = 0;
    }
    const track = this.tracks[this.index];
    this.index += 1;
    const onEnded = () => this.playNext();
    const name = typeof track === "string" ? track : (track?.name || track?.filename || "");
    if (!name) {
      this.playNext();
      return;
    }
    if (this.audioType === "sound") {
      this.app.audio.playSound({ name, onEnded });
    } else if (this.audioType === "ambience") {
      this.app.audio.playAmbience({ loop: name });
    } else {
      this.app.audio.playMusic({ name, looping: false, onEnded });
    }
  }
}

class VoiceChatManager {
  constructor(app) {
    this.app = app;
    this.room = null;
    this.state = "disconnected";
    this.capability = { enabled: false, provider: "", url: "" };
    this.currentTableContextId = "";
    this.requestedContextId = "";
    this.joinGeneration = 0;
    this.context = { scope: "table", contextId: "" };
    this.presenceRegistered = false;
    this.expectedDisconnect = false;
    this.pendingJoin = false;
    this.micEnabled = false;
    this.micTogglePending = null;
    this.remoteAudio = new Map();
    this.volume = 0.8;
    this.statusKeyOrText = "voice-chat-not-connected";
    this.statusParams = {};
  }

  setCapability(capability) {
    this.capability = capability || { enabled: false, provider: "", url: "" };
    this.updateUI();
  }

  setVolume(percent) {
    this.volume = clampNumber(percent, 0, 100, 80) / 100;
    for (const element of this.remoteAudio.values()) {
      element.volume = this.volume;
    }
  }

  setTableContext(tableId) {
    const previous = this.currentTableContextId || "";
    this.currentTableContextId = tableId || "";
    if (previous && this.currentTableContextId && previous !== this.currentTableContextId) {
      this.app.removeAllPlaylists();
      this.app.audio.stopMusic();
      this.app.audio.stopAmbience();
    }
    if (!this.currentTableContextId) {
      if (this.state === "connected" || this.state === "connecting") {
        this.cleanup(false, false);
      }
      this.requestedContextId = "";
    }
    this.updateUI();
  }

  localize(keyOrText, params = {}) {
    return Localization.has(keyOrText) ? Localization.get(keyOrText, params) : String(keyOrText || "");
  }

  setStatus(keyOrText, speak = false, params = {}) {
    this.statusKeyOrText = keyOrText || "voice-chat-not-connected";
    this.statusParams = { ...params };
    const text = this.localize(this.statusKeyOrText, this.statusParams);
    if (this.app.elements.voiceStatus) {
      this.app.elements.voiceStatus.textContent = text;
    }
    if (speak && text) {
      this.app.speak(text, { buffer: "system" });
    }
  }

  resolveMessage(packet, defaultKey = "voice-chat-unavailable") {
    if (packet?.key && Localization.has(packet.key)) {
      return Localization.get(packet.key, packet.params || {});
    }
    if (packet?.text) {
      return packet.text;
    }
    return Localization.get(defaultKey);
  }

  sendPresence(state) {
    return this.app.send({
      type: "voice_presence",
      state,
      scope: this.context.scope || "table",
      context_id: this.context.contextId || "",
    });
  }

  updateUI() {
    const connected = this.state === "connected";
    const connecting = this.state === "connecting";
    const micBusy = this.micTogglePending !== null;
    const { voiceJoinBtn, voiceLeaveBtn, voiceMicBtn, voiceStatus } = this.app.elements;
    if (voiceJoinBtn) {
      voiceJoinBtn.textContent = Localization.get(connecting ? "voice-chat-joining" : "voice-chat-join");
      voiceJoinBtn.disabled = connecting || connected;
      voiceJoinBtn.hidden = connected;
    }
    if (voiceLeaveBtn) {
      voiceLeaveBtn.textContent = Localization.get("voice-chat-leave");
      voiceLeaveBtn.disabled = connecting && !this.room;
      voiceLeaveBtn.hidden = !connected;
    }
    if (voiceMicBtn) {
      voiceMicBtn.textContent = Localization.get(this.micEnabled ? "voice-chat-turn-off-mic" : "voice-chat-turn-on-mic");
      voiceMicBtn.setAttribute("aria-pressed", this.micEnabled ? "true" : "false");
      voiceMicBtn.disabled = !connected || micBusy;
      voiceMicBtn.hidden = !connected;
    }
    if (voiceStatus) {
      voiceStatus.textContent = this.localize(this.statusKeyOrText, this.statusParams);
    }
  }

  join() {
    if (this.state === "connected" || this.pendingJoin) {
      return;
    }
    if (!this.app.isConnected()) {
      this.setStatus("status-disconnected", true);
      return;
    }
    if (!this.capability || this.capability.enabled !== true) {
      this.setStatus("voice-chat-unavailable", true);
      return;
    }
    if (!this.currentTableContextId) {
      this.setStatus("voice-not-at-table", true);
      return;
    }
    if (!window.LivekitClient || !window.LivekitClient.Room) {
      this.setStatus("voice-chat-sdk-missing", true);
      return;
    }
    this.joinGeneration += 1;
    this.requestedContextId = this.currentTableContextId;
    this.pendingJoin = true;
    this.state = "connecting";
    this.setStatus("voice-chat-joining", true);
    this.updateUI();
    this.app.send({
      type: "voice_join",
      scope: "table",
      context_id: this.requestedContextId,
    });
  }

  async connect(packet, joinGeneration) {
    if (!this.pendingJoin && this.state !== "connecting") {
      return;
    }
    if (this.requestedContextId && (packet.context_id || "") !== this.requestedContextId) {
      return;
    }
    const LK = window.LivekitClient;
    if (!LK || !LK.Room) {
      this.pendingJoin = false;
      this.state = "disconnected";
      this.requestedContextId = "";
      this.setStatus("voice-chat-sdk-missing", true);
      this.updateUI();
      return;
    }

    await this.cleanup(false, false, false);
    const room = new LK.Room({ adaptiveStream: false, dynacast: false });
    this.expectedDisconnect = false;
    this.room = room;
    this.state = "connecting";
    this.context = {
      scope: packet.scope || "table",
      contextId: packet.context_id || "",
    };
    this.updateUI();

    room.on("trackSubscribed", (track, publication, participant) => {
      this.attachTrack(track, publication, participant);
    });
    room.on("trackUnsubscribed", (track, publication) => {
      this.detachTrack(track, publication);
    });
    room.on("disconnected", () => {
      const wasConnected = this.state === "connected";
      const expected = this.expectedDisconnect;
      this.expectedDisconnect = false;
      this.cleanupElements();
      this.room = null;
      this.pendingJoin = false;
      this.micEnabled = false;
      this.micTogglePending = null;
      this.state = "disconnected";
      if (wasConnected && !expected && this.presenceRegistered) {
        this.sendPresence("connection_lost");
        this.presenceRegistered = false;
      }
      this.updateUI();
      if (wasConnected) {
        this.setStatus("voice-chat-left", false);
      }
    });

    try {
      await room.connect(packet.url, packet.token, { autoSubscribe: true });
      if (joinGeneration !== this.joinGeneration) {
        room.disconnect();
        return;
      }
      this.pendingJoin = false;
      this.state = "connected";
      this.micEnabled = false;
      this.attachExistingTracks(room);
      this.presenceRegistered = this.sendPresence("connected");
      this.requestedContextId = "";
      this.setStatus("voice-chat-listen-only", true);
    } catch (error) {
      console.warn("Voice Chat connection failed:", error);
      await this.cleanup(false, false);
      this.setStatus("voice-chat-connect-failed", true);
    } finally {
      this.updateUI();
    }
  }

  attachExistingTracks(room) {
    if (!room?.remoteParticipants) {
      return;
    }
    room.remoteParticipants.forEach((participant) => {
      participant.trackPublications?.forEach((publication) => {
        if (publication?.track) {
          this.attachTrack(publication.track, publication, participant);
        }
      });
    });
  }

  attachTrack(track, publication, participant) {
    if (!track || track.kind !== "audio" || typeof track.attach !== "function") {
      return;
    }
    const key = publication?.trackSid || track.sid || track.mediaStreamTrack?.id || participant?.identity;
    if (!key || this.remoteAudio.has(key)) {
      return;
    }
    const element = track.attach();
    element.autoplay = true;
    element.controls = false;
    element.dataset.voiceTrack = key;
    element.setAttribute("aria-hidden", "true");
    element.volume = this.volume;
    this.remoteAudio.set(key, element);
    this.app.elements.voiceAudioContainer?.appendChild(element);
    const result = element.play();
    if (result && typeof result.catch === "function") {
      result.catch((error) => console.warn("Voice Chat audio playback was blocked:", error));
    }
  }

  detachTrack(track, publication) {
    const key = publication?.trackSid || track?.sid || track?.mediaStreamTrack?.id;
    if (!key || !this.remoteAudio.has(key)) {
      return;
    }
    const element = this.remoteAudio.get(key);
    element?.parentNode?.removeChild(element);
    this.remoteAudio.delete(key);
  }

  cleanupElements() {
    for (const element of this.remoteAudio.values()) {
      element?.parentNode?.removeChild(element);
    }
    this.remoteAudio.clear();
    this.app.elements.voiceAudioContainer?.replaceChildren();
  }

  async cleanup(sendLeave = true, announce = true, cancelJoin = true) {
    const room = this.room;
    if (cancelJoin && (this.state === "connecting" || this.pendingJoin)) {
      this.joinGeneration += 1;
    }
    this.pendingJoin = false;
    this.micEnabled = false;
    this.micTogglePending = null;
    this.requestedContextId = "";
    this.state = "disconnected";
    this.room = null;
    this.cleanupElements();
    if (room) {
      this.expectedDisconnect = true;
      try {
        await room.localParticipant?.setMicrophoneEnabled(false);
      } catch {
        // Ignore cleanup failures.
      }
      room.disconnect();
    }
    if (sendLeave && this.presenceRegistered && this.app.isConnected()) {
      this.app.send({
        type: "voice_leave",
        scope: this.context.scope || "table",
        context_id: this.context.contextId || "",
      });
    }
    this.presenceRegistered = false;
    this.context = { scope: "table", contextId: "" };
    if (announce) {
      this.setStatus("voice-chat-left", true);
    }
    this.updateUI();
  }

  leave() {
    this.cleanup(true, true);
  }

  async toggleMic() {
    if (!this.room || this.state !== "connected") {
      this.setStatus("voice-chat-not-connected", true);
      return;
    }
    if (this.micTogglePending !== null) {
      return;
    }
    const enable = !this.micEnabled;
    if (enable && (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia)) {
      this.app.audio.playSound({ name: "voice_mic_error.ogg" });
      this.setStatus("voice-chat-mic-unsupported", true);
      return;
    }
    this.micTogglePending = enable;
    this.updateUI();
    try {
      await this.room.localParticipant.setMicrophoneEnabled(enable);
      this.micEnabled = enable;
      this.app.audio.playSound({ name: enable ? "voice_mic_on.ogg" : "voice_mic_off.ogg" });
      this.setStatus(enable ? "voice-chat-mic-on" : "voice-chat-mic-off", true);
    } catch (error) {
      console.warn("Voice Chat microphone toggle failed:", error);
      this.micEnabled = false;
      if (enable) {
        this.app.audio.playSound({ name: "voice_mic_error.ogg" });
      }
      if (error && (error.name === "NotAllowedError" || error.name === "PermissionDeniedError")) {
        this.setStatus("voice-chat-mic-denied", true);
      } else {
        this.setStatus("voice-chat-connect-failed", true);
      }
    } finally {
      this.micTogglePending = null;
      this.updateUI();
    }
  }
}

class PlayAuralWebApp {
  constructor({ validator }) {
    this.validator = validator;
    this.store = createStore();
    this.a11y = createA11y({
      politeEl: byId("live-polite"),
      assertiveEl: byId("live-assertive"),
    });
    this.audio = createAudioEngine({ soundBaseUrl: "./sounds" });
    this.preferences = {
      mute_global_chat: false,
      mute_table_chat: false,
      play_turn_sound: true,
      notify_table_created: true,
      music_volume: 10,
      sound_volume: 100,
      ambience_volume: 20,
      voice_volume: 80,
      speech_mode: "aria",
      speech_rate: 100,
      speech_voice: "",
      muted_buffers: [],
    };
    this.webSpeech = new WebSpeechManager({ getPreferences: () => this.preferences });
    this.elements = this.collectElements();
    this.webSpeech.onVoicesChanged = () => this.refreshVoiceSelectionMenuIfOpen();
    this.network = createNetworkClient({
      validator,
      onStatus: (status) => this.handleNetworkStatus(status),
      onPacket: (packet) => this.handlePacket(packet),
      onError: (message, params) => this.handleNetworkError(message, params),
    });

    this.lastUser = "";
    this.lastPass = "";
    this.lastUrl = DEFAULT_SERVER_URL;
    this.shouldReconnect = false;
    this.manualDisconnect = false;
    this.reconnectAttempts = 0;
    this.reconnectStartedAt = 0;
    this.reconnectDelayMs = RECONNECT_INITIAL_DELAY_MS;
    this.reconnectTimer = null;
    this.reconnectDeadlineTimer = null;
    this.sessionEstablished = false;
    this.currentAuthStatusEl = this.elements.loginStatus;
    this.currentTableContextId = "";
    this.webActionsItem = null;
    this.webActionsMenuId = "";
    this.focusMenuOnNextPacket = false;
    this.pendingInput = null;
    this.pingStart = null;
    this.playlists = {};
    this.connectionStatusMessage = "status-disconnected";
    this.connectionStatusParams = {};
    this.connectionStatusError = false;
    this.deferredPrompt = null;
    this.isIOS = (
      /iPad|iPhone|iPod/.test(navigator.userAgent)
      || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1)
    ) && !window.MSStream;
    this.voice = new VoiceChatManager(this);

    this.historyView = createHistoryView({
      store: this.store,
      historyEl: this.elements.history,
      historyLogEl: this.elements.historyLog,
      historyContentEl: this.elements.historyContent,
      historyToggleEl: this.elements.historyToggle,
      bufferSelectEl: this.elements.historyBuffer,
      a11y: this.a11y,
      announceFeedback: (text, options = {}) => this.announceInterface(text, options),
      onMutedBuffersChange: (buffers) => {
        this.preferences.muted_buffers = buffers;
        this.saveLocalConfig();
      },
      localize: (key, params) => Localization.get(key, params),
      localizeBufferName: (name) => this.localizeBufferName(name),
    });
    this.menuView = createMenuView({
      store: this.store,
      listEl: this.elements.menuList,
      onActivate: (item, index) => this.activateMenuItem(item, index),
      onSelectionSound: (item) => this.playSelectionSound(item),
      onActivateSound: () => this.audio.playSound({ name: "menuenter.ogg", volume: 50 }),
      onBoundaryRepeat: (text) => {
        if (text) {
          this.speak(text, { buffer: "misc", assertive: true, noHistory: true });
        }
      },
      onContextAction: (item) => this.sendKeybind("enter", item?.id || "", { shift: true }),
      getDefaultLabel: () => Localization.get("game-menu-label"),
    });
  }

  collectElements() {
    return {
      authScreen: byId("auth-screen"),
      gameScreen: byId("game-screen"),
      authTitle: byId("auth-title"),
      authIntro: byId("auth-intro"),
      languageSelect: byId("language-select"),
      installBtn: byId("btn-install-pwa"),
      installInstruction: byId("install-instruction"),
      savedSessionView: byId("saved-session-view"),
      savedSessionLabel: byId("saved-session-label"),
      playNowBtn: byId("btn-play-now"),
      removeAccountBtn: byId("btn-remove-account"),
      loginPanel: byId("login-panel"),
      registerPanel: byId("register-panel"),
      forgotPanel: byId("forgot-panel"),
      resetPanel: byId("reset-panel"),
      showLoginBtn: byId("btn-show-login"),
      showRegisterBtn: byId("btn-show-register"),
      showForgotBtn: byId("btn-show-forgot-password"),
      loginForm: byId("login-form"),
      registerForm: byId("register-form"),
      forgotForm: byId("forgot-password-form"),
      resetForm: byId("reset-password-form"),
      username: byId("username"),
      password: byId("password"),
      remember: byId("chk-auto-login"),
      regUsername: byId("reg-username"),
      regEmail: byId("reg-email"),
      regPassword: byId("reg-password"),
      regPasswordConfirm: byId("reg-password-confirm"),
      forgotEmail: byId("forgot-email"),
      resetCode: byId("reset-code"),
      newPassword: byId("new-password"),
      confirmNewPassword: byId("confirm-new-password"),
      loginStatus: byId("login-status"),
      registerStatus: byId("register-status"),
      forgotStatus: byId("forgot-password-status"),
      resetStatus: byId("reset-password-status"),
      soundVolume: byId("sound-volume"),
      musicVolume: byId("music-volume"),
      ambienceVolume: byId("ambience-volume"),
      voiceVolume: byId("voice-volume"),
      soundVolumeValue: byId("sound-volume-value"),
      musicVolumeValue: byId("music-volume-value"),
      ambienceVolumeValue: byId("ambience-volume-value"),
      voiceVolumeValue: byId("voice-volume-value"),
      audioMute: byId("audio-mute"),
      menuList: byId("menu-list"),
      actionsBtn: byId("actions-btn"),
      inlineInput: byId("inline-input"),
      inlineInputPrompt: byId("inline-input-prompt"),
      inlineInputText: byId("inline-input-text"),
      inlineInputValue: byId("inline-input-value"),
      inlineInputSubmit: byId("inline-input-submit"),
      inlineInputCancel: byId("inline-input-cancel"),
      history: byId("history"),
      historyLog: byId("history-log"),
      historyContent: byId("history-content"),
      historyToggle: byId("history-toggle"),
      historyBuffer: byId("history-buffer"),
      chatForm: byId("chat-form"),
      chatInput: byId("chat-input"),
      voiceJoinBtn: byId("btn-voice-join"),
      voiceLeaveBtn: byId("btn-voice-leave"),
      voiceMicBtn: byId("btn-voice-mic"),
      voiceStatus: byId("voice-chat-status"),
      voiceAudioContainer: byId("voice-chat-audio"),
      listOnlineBtn: byId("btn-list-online"),
      listOnlineGamesBtn: byId("btn-list-online-games"),
      openFriendsBtn: byId("btn-open-friends"),
      openOptionsBtn: byId("btn-open-options"),
      checkPingBtn: byId("btn-check-ping"),
    };
  }

  async init() {
    this.loadLocalConfig();
    this.populateLanguageSelect();
    await Localization.load(storageGet(LANG_KEY) || this.elements.languageSelect?.value || DEFAULT_LOCALE);
    this.applyLocalization();
    this.applyPreferences();
    this.bindEvents();
    this.renderSavedSession();
    this.updateConnectionStatus("status-disconnected");
    this.voice.updateUI();
    setRecaptchaVisibility(false);
  }

  populateLanguageSelect() {
    if (!this.elements.languageSelect) {
      return;
    }
    const previous = this.elements.languageSelect.value || storageGet(LANG_KEY) || DEFAULT_LOCALE;
    const normalized = normalizeLocale(previous);
    this.elements.languageSelect.replaceChildren();
    for (const [code, label] of Object.entries(AVAILABLE_LOCALES)) {
      const option = document.createElement("option");
      option.value = code;
      option.textContent = label;
      this.elements.languageSelect.appendChild(option);
    }
    this.elements.languageSelect.value = AVAILABLE_LOCALES[normalized] ? normalized : DEFAULT_LOCALE;
  }

  bindEvents() {
    this.elements.languageSelect?.addEventListener("change", async () => {
      await Localization.load(this.elements.languageSelect.value);
      this.applyLocalization();
      this.voice.updateUI();
      this.saveLocalConfig();
    });

    this.elements.showLoginBtn?.addEventListener("click", () => this.showAuthPanel("login"));
    this.elements.showRegisterBtn?.addEventListener("click", () => this.showAuthPanel("register"));
    this.elements.showForgotBtn?.addEventListener("click", () => this.showAuthPanel("forgot"));
    this.elements.playNowBtn?.addEventListener("click", () => this.playSavedSession());
    this.elements.removeAccountBtn?.addEventListener("click", () => this.removeSavedAccount());
    this.elements.loginForm?.addEventListener("submit", (event) => {
      event.preventDefault();
      this.login();
    });
    this.elements.registerForm?.addEventListener("submit", (event) => {
      event.preventDefault();
      this.register();
    });
    this.elements.forgotForm?.addEventListener("submit", (event) => {
      event.preventDefault();
      this.requestPasswordReset();
    });
    this.elements.resetForm?.addEventListener("submit", (event) => {
      event.preventDefault();
      this.submitResetCode();
    });
    this.elements.actionsBtn?.addEventListener("click", () => this.openWebActionsMenu());
    this.elements.inlineInputSubmit?.addEventListener("click", () => this.submitInlineInput());
    this.elements.inlineInputCancel?.addEventListener("click", () => this.cancelInlineInput());
    for (const input of [this.elements.inlineInputText, this.elements.inlineInputValue]) {
      input?.addEventListener("keydown", (event) => this.handleInlineInputKeydown(event));
    }
    this.elements.chatForm?.addEventListener("submit", (event) => {
      event.preventDefault();
      this.sendChatFromInput();
    });
    this.elements.voiceJoinBtn?.addEventListener("click", () => this.voice.join());
    this.elements.voiceLeaveBtn?.addEventListener("click", () => this.voice.leave());
    this.elements.voiceMicBtn?.addEventListener("click", () => this.voice.toggleMic());
    this.elements.listOnlineBtn?.addEventListener("click", () => this.sendListOnline(false));
    this.elements.listOnlineGamesBtn?.addEventListener("click", () => this.sendListOnline(true));
    this.elements.openFriendsBtn?.addEventListener("click", () => this.openFriendsHub());
    this.elements.openOptionsBtn?.addEventListener("click", () => this.openOptionsMenu());
    this.elements.checkPingBtn?.addEventListener("click", () => this.sendPing());
    this.elements.installBtn?.addEventListener("click", () => this.installPwa());
    this.elements.audioMute?.addEventListener("change", () => {
      this.audio.setMuted(this.elements.audioMute.checked);
    });
    this.bindVolumeControl(this.elements.soundVolume, "audio/sound_volume", "sound_volume", 10, 100, 10);
    this.bindVolumeControl(this.elements.musicVolume, "audio/music_volume", "music_volume", 0, 100, 10);
    this.bindVolumeControl(this.elements.ambienceVolume, "audio/ambience_volume", "ambience_volume", 0, 100, 10);
    this.bindVolumeControl(this.elements.voiceVolume, "audio/voice_volume", "voice_volume", 10, 100, 10);

    installKeybinds({
      store: this.store,
      menuView: this.menuView,
      sendMenuSelection: (index) => {
        const item = this.store.state.currentMenu.items[index];
        this.activateMenuItem(item, index);
      },
      historyView: this.historyView,
      sendKeybind: (key, menuItemId, modifiers) => this.sendKeybind(key, menuItemId, modifiers),
      sendEscape: () => this.sendEscape(),
      sendListOnline: () => this.sendListOnline(false),
      sendListOnlineWithGames: () => this.sendListOnline(true),
      onFocusMenu: () => this.focusMenu(),
      onFocusChat: () => this.focusChat(),
      onToggleVoiceChat: () => this.toggleVoiceChatShortcut(),
      onToggleVoiceMic: () => this.voice.toggleMic(),
      onFocusHistory: () => this.focusHistory(),
      onOpenFriends: () => this.openFriendsHub(),
      onOpenAdmin: () => this.openAdminMenu(),
      onOpenOptions: () => this.openOptionsMenu(),
      onPreviousBuffer: () => this.historyView.previousBuffer(),
      onNextBuffer: () => this.historyView.nextBuffer(),
      onFirstBuffer: () => this.historyView.firstBuffer(),
      onLastBuffer: () => this.historyView.lastBuffer(),
      onOlderMessage: () => this.historyView.olderMessage(),
      onNewerMessage: () => this.historyView.newerMessage(),
      onOldestMessage: () => this.historyView.oldestMessage(),
      onNewestMessage: () => this.historyView.newestMessage(),
      onToggleBufferMute: () => this.historyView.toggleCurrentBufferMute(),
      onToggleTableChat: () => this.toggleChatMute("table"),
      onToggleGlobalChat: () => this.toggleChatMute("global"),
      onAmbienceDown: () => this.adjustVolumePreference("ambience_volume", "audio/ambience_volume", -10, 0, 100, 10),
      onAmbienceUp: () => this.adjustVolumePreference("ambience_volume", "audio/ambience_volume", 10, 0, 100, 10),
      onMusicDown: () => this.adjustVolumePreference("music_volume", "audio/music_volume", -10, 0, 100, 10),
      onMusicUp: () => this.adjustVolumePreference("music_volume", "audio/music_volume", 10, 0, 100, 10),
      onPing: () => this.sendPing(),
      isModalOpen: () => Boolean(!this.elements.inlineInput?.hidden),
      a11y: this.a11y,
    });
    this.installInGameTabTrap();

    const unlock = () => {
      this.audio.unlock().then((unlocked) => this.store.setAudioUnlocked(unlocked));
      this.webSpeech.warmUp();
    };
    document.addEventListener("pointerdown", unlock, { passive: true });
    document.addEventListener("keydown", unlock);
    document.addEventListener("touchstart", unlock, { passive: true });

    window.addEventListener("beforeinstallprompt", (event) => {
      if (this.isStandalone()) {
        return;
      }
      event.preventDefault();
      this.deferredPrompt = event;
      if (this.elements.installBtn) {
        this.elements.installBtn.hidden = false;
      }
    });
    window.addEventListener("appinstalled", () => {
      this.deferredPrompt = null;
      if (this.elements.installBtn) {
        this.elements.installBtn.hidden = true;
      }
    });
  }

  installInGameTabTrap() {
    const isVisible = (element) => Boolean(element && !element.hidden && element.getClientRects().length > 0);
    const focusTarget = (target) => {
      if (target === this.elements.menuList) {
        this.menuView.focusSelection();
        return;
      }
      target?.focus?.({ preventScroll: true });
    };
    const getHistoryTarget = () => {
      if (isVisible(this.elements.history)) {
        return this.elements.history;
      }
      if (isVisible(this.elements.historyLog)) {
        return this.elements.historyLog;
      }
      return null;
    };

    document.addEventListener("keydown", (event) => {
      if (event.key !== "Tab") {
        return;
      }
      if (!this.store.state.connection.authenticated || this.elements.gameScreen?.hidden) {
        return;
      }

      const historyTarget = getHistoryTarget();
      const targets = [
        this.elements.menuList,
        historyTarget,
        this.elements.chatInput,
      ].filter(isVisible);

      const inlineTarget = this.getActiveInlineInputElement();
      if (!this.elements.inlineInput?.hidden && isVisible(inlineTarget)) {
        targets.push(inlineTarget);
      }
      if (!targets.length) {
        return;
      }

      const active = document.activeElement;
      let activeIndex = targets.indexOf(active);
      if (activeIndex < 0 && this.elements.menuList?.contains(active)) {
        activeIndex = targets.indexOf(this.elements.menuList);
      }
      if (activeIndex < 0 && this.elements.gameScreen?.contains(active)) {
        event.preventDefault();
        focusTarget(targets[event.shiftKey ? targets.length - 1 : 0]);
        return;
      }
      if (activeIndex < 0) {
        return;
      }

      event.preventDefault();
      const delta = event.shiftKey ? -1 : 1;
      const nextIndex = (activeIndex + delta + targets.length) % targets.length;
      focusTarget(targets[nextIndex]);
    }, true);
  }

  isVisibleFocusTarget(element) {
    return Boolean(
      element
      && !element.hidden
      && typeof element.focus === "function"
      && element.getClientRects().length > 0
    );
  }

  focusMenu() {
    if (!this.elements.gameScreen?.hidden) {
      this.menuView.focusSelection();
    }
  }

  focusChat() {
    if (this.isVisibleFocusTarget(this.elements.chatInput)) {
      this.elements.chatInput.focus({ preventScroll: true });
    }
  }

  toggleVoiceChatShortcut() {
    if (this.voice.state === "connected") {
      this.voice.leave();
      return;
    }
    this.voice.join();
  }

  focusHistory() {
    const target = [
      this.elements.history,
      this.elements.historyLog,
      this.elements.historyToggle,
    ].find((element) => this.isVisibleFocusTarget(element));
    target?.focus({ preventScroll: true });
  }

  bindVolumeControl(element, serverKey, flatKey, min, max, step = 1) {
    if (!element) {
      return;
    }
    element.min = String(min);
    element.max = String(max);
    element.step = String(step);
    element.addEventListener("input", () => {
      const value = snapNumberToStep(element.value, min, max, this.preferences[flatKey] ?? max, step);
      element.value = String(value);
      this.preferences[flatKey] = value;
      this.applyPreferences();
    });
    element.addEventListener("change", () => {
      const value = snapNumberToStep(element.value, min, max, this.preferences[flatKey] ?? max, step);
      element.value = String(value);
      this.preferences[flatKey] = value;
      this.applyPreferences();
      this.saveLocalConfig();
      if (this.isConnected()) {
        this.send({ type: "set_preference", key: serverKey, value });
      }
    });
  }

  adjustVolumePreference(flatKey, serverKey, delta, min, max, step = 1) {
    const current = snapNumberToStep(this.preferences[flatKey] ?? max, min, max, max, step);
    const value = snapNumberToStep(current + delta, min, max, current, step);
    this.preferences[flatKey] = value;
    this.applyPreferences();
    this.saveLocalConfig();
    if (this.isConnected()) {
      this.send({ type: "set_preference", key: serverKey, value });
    }
    const messageKey = flatKey === "ambience_volume"
      ? "main-ambience-volume"
      : flatKey === "music_volume"
        ? "main-music-volume"
        : "";
    const message = messageKey ? Localization.get(messageKey, { value }) : `${value}%`;
    this.speak(message, { buffer: "system", noHistory: true });
  }

  applyLocalization() {
    const e = this.elements;
    document.title = Localization.get("app-title");
    const pairs = [
      [e.authTitle, "landing-title"],
      [e.authIntro, "intro-text"],
      [byId("language-label"), "language-label"],
      [e.installBtn, "btn-install"],
      [e.playNowBtn, "btn-play"],
      [e.removeAccountBtn, "btn-remove-account"],
      [e.showLoginBtn, "btn-enter"],
      [e.showRegisterBtn, "btn-register"],
      [e.showForgotBtn, "login-btn-forgot-password"],
      [byId("login-username-label"), "login-username-label"],
      [byId("login-password-label"), "login-password-label"],
      [byId("label-auto-login"), "label-auto-login"],
      [byId("login-btn"), "login-btn"],
      [byId("reg-username-label"), "reg-username-label"],
      [byId("reg-email-label"), "reg-email-label"],
      [byId("reg-password-label"), "reg-password-label"],
      [byId("label-confirm-password"), "label-confirm-password"],
      [byId("btn-register"), "btn-register"],
      [byId("forgot-password-prompt"), "forgot-password-prompt"],
      [byId("forgot-email-label"), "reg-email-label"],
      [byId("btn-send-reset-code"), "btn-send-code"],
      [byId("reset-password-title"), "reset-password-title"],
      [byId("reset-code-instructions"), "reset-code-instructions"],
      [byId("reset-code-label"), "reset-code-prompt"],
      [byId("new-password-label"), "new-password-prompt"],
      [byId("confirm-new-password-label"), "label-confirm-password"],
      [byId("btn-submit-reset"), "btn-submit-reset"],
      [byId("audio-sound-label"), "audio-sound"],
      [byId("audio-music-label"), "audio-music"],
      [byId("audio-ambience-label"), "audio-ambience"],
      [byId("audio-voice-label"), "audio-voice"],
      [byId("audio-mute-label"), "audio-mute"],
      [byId("menu-heading"), "tab-menu"],
      [e.actionsBtn, "context-menu"],
      [byId("history-heading"), "tab-history"],
      [byId("history-buffer-label"), "history-buffer-label"],
      [byId("buffer-option-all"), "buffer-all"],
      [byId("buffer-option-chat"), "buffer-chat"],
      [byId("buffer-option-game"), "buffer-game"],
      [byId("buffer-option-system"), "buffer-system"],
      [byId("buffer-option-misc"), "buffer-misc"],
      [byId("chat-heading"), "chat-heading"],
      [byId("chat-input-label"), "chat-input-label"],
      [byId("btn-chat-send"), "btn-chat-send"],
      [byId("voice-chat-heading"), "voice-chat-heading"],
      [byId("shortcuts-heading"), "players-title"],
      [e.listOnlineBtn, "btn-list-online"],
      [e.listOnlineGamesBtn, "btn-list-online-games"],
      [e.openFriendsBtn, "btn-open-friends"],
      [e.openOptionsBtn, "btn-open-options"],
      [e.checkPingBtn, "btn-check-ping"],
      [e.inlineInputSubmit, "input-submit"],
      [e.inlineInputCancel, "common-cancel"],
    ];
    for (const [node, key] of pairs) {
      if (node && Localization.has(key)) {
        node.textContent = Localization.get(key);
      }
    }
    const attributePairs = [
      [byId("auth-controls"), "aria-label", "auth-controls-label"],
      [byId("account-actions-nav"), "aria-label", "account-actions-label"],
      [e.gameScreen, "aria-label", "game-client-label"],
      [byId("audio-panel"), "aria-label", "audio-controls-label"],
      [e.menuList, "aria-label", "game-menu-label"],
      [e.history, "aria-label", "message-history-label"],
      [e.historyLog, "aria-label", "message-history-log-label"],
    ];
    for (const [node, attribute, key] of attributePairs) {
      if (node && Localization.has(key)) {
        node.setAttribute(attribute, Localization.get(key));
      }
    }
    if (e.languageSelect) {
      e.languageSelect.value = Localization.locale;
    }
    if (e.chatInput && Localization.has("chat-input-placeholder")) {
      e.chatInput.placeholder = Localization.get("chat-input-placeholder");
    }
    if (e.installInstruction && this.isIOS && !this.isStandalone()) {
      e.installInstruction.textContent = Localization.get("install-fail-hint");
      e.installInstruction.hidden = false;
    }
    this.renderSavedSession();
    this.updateConnectionStatus(
      this.connectionStatusMessage,
      this.connectionStatusError,
      this.connectionStatusParams,
    );
    this.updateVolumeLabels();
  }

  localizeBufferName(name) {
    const key = `buffer-name-${name}`;
    return Localization.has(key) ? Localization.get(key) : String(name || "");
  }

  showAuthPanel(panel) {
    const panels = {
      login: this.elements.loginPanel,
      register: this.elements.registerPanel,
      forgot: this.elements.forgotPanel,
      reset: this.elements.resetPanel,
    };
    const buttons = {
      login: this.elements.showLoginBtn,
      register: this.elements.showRegisterBtn,
      forgot: this.elements.showForgotBtn,
    };
    for (const [name, element] of Object.entries(panels)) {
      if (element) {
        element.hidden = name !== panel;
      }
    }
    for (const [name, button] of Object.entries(buttons)) {
      if (button) {
        const active = name === panel;
        button.classList.toggle("active", active);
        button.setAttribute("aria-current", active ? "page" : "false");
      }
    }
    setRecaptchaVisibility(panel !== "reset" && Boolean(RECAPTCHA_SITE_KEY));
  }

  showAuth() {
    this.elements.authScreen.hidden = false;
    this.elements.gameScreen.hidden = true;
    setRecaptchaVisibility(Boolean(RECAPTCHA_SITE_KEY));
  }

  showGame() {
    this.elements.authScreen.hidden = true;
    this.elements.gameScreen.hidden = false;
    setRecaptchaVisibility(false);
    requestAnimationFrame(() => this.menuView.focusSelection());
  }

  loadLocalConfig() {
    const config = safeJsonParse(storageGet(CONFIG_KEY), {});
    this.lastUrl = this.getServerUrl();
    this.preferences = { ...this.preferences, ...(config.preferences || {}) };
    this.historyView?.setMutedBuffers(this.preferences.muted_buffers || []);
    if (config.lastUsername && this.elements.username) {
      this.elements.username.value = config.lastUsername;
    }
    const remembered = storageGet(REMEMBER_KEY) === "1";
    if (this.elements.remember) {
      this.elements.remember.checked = remembered;
    }
    const savedUser = storageGet(USER_KEY, true) || storageGet(USER_KEY, false);
    const savedPass = storageGet(PASS_KEY, true) || storageGet(PASS_KEY, false);
    if (savedUser && this.elements.username) {
      this.elements.username.value = savedUser;
    }
    if (savedPass && this.elements.password) {
      this.elements.password.value = savedPass;
    }
    this.lastUser = savedUser || "";
    this.lastPass = savedPass || "";
  }

  saveLocalConfig() {
    const config = {
      lastUsername: this.elements.username?.value || this.lastUser || "",
      preferences: this.preferences,
    };
    storageSet(CONFIG_KEY, JSON.stringify(config));
    this.lastUrl = this.getServerUrl();
    if (this.lastUser && this.lastPass) {
      const remember = Boolean(this.elements.remember?.checked);
      storageSet(USER_KEY, this.lastUser, remember);
      storageSet(PASS_KEY, this.lastPass, remember);
      storageSet(REMEMBER_KEY, remember ? "1" : "0");
      if (remember) {
        sessionStorage.removeItem(USER_KEY);
        sessionStorage.removeItem(PASS_KEY);
      } else {
        localStorage.removeItem(USER_KEY);
        localStorage.removeItem(PASS_KEY);
      }
    }
    this.renderSavedSession();
  }

  getServerUrl() {
    return DEFAULT_SERVER_URL;
  }

  isValidServerUrl(serverUrl) {
    return serverUrl.startsWith("ws://") || serverUrl.startsWith("wss://");
  }

  renderSavedSession() {
    const user = storageGet(USER_KEY, true) || storageGet(USER_KEY, false);
    if (!this.elements.savedSessionView || !this.elements.savedSessionLabel) {
      return;
    }
    this.elements.savedSessionView.hidden = !user;
    if (user) {
      this.elements.savedSessionLabel.textContent = Localization.get("logged-in-as", { username: user });
    }
  }

  removeSavedAccount() {
    storageRemove(USER_KEY);
    storageRemove(PASS_KEY);
    storageRemove(REMEMBER_KEY);
    this.lastUser = "";
    this.lastPass = "";
    if (this.elements.password) {
      this.elements.password.value = "";
    }
    if (this.elements.remember) {
      this.elements.remember.checked = false;
    }
    this.renderSavedSession();
  }

  playSavedSession() {
    const user = storageGet(USER_KEY, true) || storageGet(USER_KEY, false);
    const pass = storageGet(PASS_KEY, true) || storageGet(PASS_KEY, false);
    if (user && pass) {
      if (this.elements.username) {
        this.elements.username.value = user;
      }
      if (this.elements.password) {
        this.elements.password.value = pass;
      }
      this.login();
    }
  }

  applyPreferences() {
    const soundVolume = snapNumberToStep(this.preferences.sound_volume, 10, 100, 100, 10);
    const musicVolume = snapNumberToStep(this.preferences.music_volume, 0, 100, 10, 10);
    const ambienceVolume = snapNumberToStep(this.preferences.ambience_volume, 0, 100, 20, 10);
    const voiceVolume = snapNumberToStep(this.preferences.voice_volume, 10, 100, 80, 10);
    this.preferences.sound_volume = soundVolume;
    this.preferences.music_volume = musicVolume;
    this.preferences.ambience_volume = ambienceVolume;
    this.preferences.voice_volume = voiceVolume;
    this.audio.setEffectsVolumePercent(soundVolume);
    this.audio.setMusicVolumePercent(musicVolume);
    this.audio.setAmbienceVolumePercent(ambienceVolume);
    this.voice.setVolume(voiceVolume);
    this.webSpeech.applyPreferences();
    this.updateVolumeLabels();
  }

  updateVolumeLabels() {
    const pairs = [
      [this.elements.soundVolume, this.elements.soundVolumeValue, this.preferences.sound_volume],
      [this.elements.musicVolume, this.elements.musicVolumeValue, this.preferences.music_volume],
      [this.elements.ambienceVolume, this.elements.ambienceVolumeValue, this.preferences.ambience_volume],
      [this.elements.voiceVolume, this.elements.voiceVolumeValue, this.preferences.voice_volume],
    ];
    for (const [input, output, value] of pairs) {
      if (input) {
        input.value = String(value);
      }
      if (output) {
        output.textContent = `${value}%`;
      }
    }
  }

  localError(message, statusEl = this.currentAuthStatusEl, params = {}) {
    const text = Localization.has(message) ? Localization.get(message, params) : String(message || "");
    if (statusEl) {
      statusEl.textContent = text;
      statusEl.classList.add("error");
    }
    if (text) {
      this.speak(text, { buffer: "system", assertive: true });
    }
  }

  authResponseSucceeded(packet) {
    return packet?.success === true || packet?.status === "success";
  }

  authCodeToKey(code) {
    const map = {
      wrong_password: "auth-error-wrong-password",
      user_not_found: "auth-error-user-not-found",
      version_mismatch: "auth-error-version-mismatch",
      rate_limit: "auth-error-rate-limit",
      captcha_missing: "auth-error-captcha-unavailable",
      captcha_failed: "auth-error-captcha-execute-failed",
      username_taken: "auth-username-taken",
      username_reserved_bot: "auth-username-reserved-bot",
      username_length: "auth-error-username-length",
      password_weak: "auth-error-password-weak",
      email_empty: "error-email-empty",
      email_invalid: "error-email-invalid",
      email_taken: "error-email-taken",
    };
    return map[code] || code || "";
  }

  authResponseMessage(packet, successKey, errorKey = "common-error") {
    const code = packet?.key || packet?.error || packet?.reason || "";
    const mapped = this.authCodeToKey(code);
    if (mapped && Localization.has(mapped)) {
      return mapped;
    }
    if (packet?.text) {
      return packet.text;
    }
    if (mapped) {
      return mapped;
    }
    return this.authResponseSucceeded(packet) ? successKey : errorKey;
  }

  setAuthStatus(textOrKey, statusEl = this.currentAuthStatusEl, error = false) {
    const text = Localization.has(textOrKey) ? Localization.get(textOrKey) : String(textOrKey || "");
    if (statusEl) {
      statusEl.textContent = text;
      statusEl.classList.toggle("error", error);
    }
    if (text) {
      this.a11y.announce(text, { assertive: error });
    }
  }

  async login() {
    const username = this.elements.username?.value.trim() || "";
    const password = this.elements.password?.value || "";
    const serverUrl = this.getServerUrl();
    if (!this.isValidServerUrl(serverUrl)) {
      this.localError("status-invalid-url", this.elements.loginStatus);
      return;
    }
    if (!username || !password) {
      this.localError("common-error", this.elements.loginStatus);
      return;
    }
    this.currentAuthStatusEl = this.elements.loginStatus;
    this.setAuthStatus("status-authenticating", this.elements.loginStatus);
    const captcha = await getCaptchaTokenResult("login");
    if (!captcha.ok) {
      this.localError(captcha.reason, this.elements.loginStatus);
      return;
    }
    const packet = {
      ...clientAuthMetadata(),
      type: "authorize",
      username,
      password,
      version: CLIENT_VERSION,
    };
    if (captcha.token) {
      packet.captcha_token = captcha.token;
    }
    this.lastUser = username;
    this.lastPass = password;
    this.lastUrl = serverUrl;
    this.shouldReconnect = true;
    this.manualDisconnect = false;
    this.network.connect({ serverUrl, authPacket: packet });
  }

  async register() {
    const username = this.elements.regUsername?.value.trim() || "";
    const email = this.elements.regEmail?.value.trim() || "";
    const password = this.elements.regPassword?.value || "";
    const confirm = this.elements.regPasswordConfirm?.value || "";
    const serverUrl = this.getServerUrl();
    if (!this.isValidServerUrl(serverUrl)) {
      this.localError("status-invalid-url", this.elements.registerStatus);
      return;
    }
    if (!email) {
      this.localError("error-email-empty", this.elements.registerStatus);
      return;
    }
    if (password !== confirm) {
      this.localError("reg-error-password-match", this.elements.registerStatus);
      return;
    }
    this.currentAuthStatusEl = this.elements.registerStatus;
    this.setAuthStatus("status-sending-registration", this.elements.registerStatus);
    const captcha = await getCaptchaTokenResult("register");
    if (!captcha.ok) {
      this.localError(captcha.reason, this.elements.registerStatus);
      return;
    }
    const packet = {
      ...clientAuthMetadata(),
      type: "register",
      username,
      password,
      email,
      locale: Localization.locale,
    };
    if (captcha.token) {
      packet.captcha_token = captcha.token;
    }
    this.shouldReconnect = false;
    this.manualDisconnect = true;
    this.network.connect({ serverUrl, authPacket: packet });
  }

  async requestPasswordReset() {
    const email = this.elements.forgotEmail?.value.trim() || "";
    if (!email) {
      this.localError("error-email-empty", this.elements.forgotStatus);
      return;
    }
    const serverUrl = this.getServerUrl();
    const captcha = await getCaptchaTokenResult("request_password_reset");
    if (!captcha.ok) {
      this.localError(captcha.reason, this.elements.forgotStatus);
      return;
    }
    this.sendOneShotAuthPacket(serverUrl, {
      type: "request_password_reset",
      email,
      locale: Localization.locale,
      captcha_token: captcha.token,
    }, this.elements.forgotStatus, (packet) => {
      const success = this.authResponseSucceeded(packet);
      const message = this.authResponseMessage(packet, "reset-code-instructions");
      this.setAuthStatus(message, this.elements.forgotStatus, !success);
      if (success) {
        this.showAuthPanel("reset");
      }
    });
  }

  async submitResetCode() {
    const email = this.elements.forgotEmail?.value.trim() || "";
    const code = this.elements.resetCode?.value.trim() || "";
    const password = this.elements.newPassword?.value || "";
    const confirm = this.elements.confirmNewPassword?.value || "";
    if (password !== confirm) {
      this.localError("error-password-mismatch", this.elements.resetStatus);
      return;
    }
    const serverUrl = this.getServerUrl();
    const captcha = await getCaptchaTokenResult("submit_reset_code");
    if (!captcha.ok) {
      this.localError(captcha.reason, this.elements.resetStatus);
      return;
    }
    this.sendOneShotAuthPacket(serverUrl, {
      type: "submit_reset_code",
      email,
      code,
      new_password: password,
      locale: Localization.locale,
      captcha_token: captcha.token,
    }, this.elements.resetStatus, (packet) => {
      const success = this.authResponseSucceeded(packet);
      const message = this.authResponseMessage(packet, "reset-password-success");
      this.setAuthStatus(message, this.elements.resetStatus, !success);
      if (success) {
        this.showAuthPanel("login");
      }
    });
  }

  sendOneShotAuthPacket(serverUrl, packet, statusEl, onResponse) {
    if (!this.isValidServerUrl(serverUrl)) {
      this.localError("status-invalid-url", statusEl);
      return;
    }
    this.setAuthStatus("status-connecting", statusEl);
    try {
      const ws = new WebSocket(serverUrl);
      const expected = `${packet.type}_response`;
      ws.addEventListener("open", () => ws.send(JSON.stringify(packet)), { once: true });
      ws.addEventListener("message", (event) => {
        const response = safeJsonParse(event.data, {});
        if (response.type === expected) {
          onResponse(response);
          ws.close();
        }
      });
      ws.addEventListener("error", () => this.localError("status-connection-error", statusEl), { once: true });
    } catch {
      this.localError("status-connection-error", statusEl);
    }
  }

  handleNetworkStatus(status) {
    this.store.setConnection({ status });
    const reconnecting = this.isReconnectEligible() && this.reconnectStartedAt > 0;
    if (status === "connected") {
      this.updateConnectionStatus(reconnecting ? "main-reconnecting" : "status-authenticating");
      return;
    }
    if (status === "connecting") {
      if (!reconnecting) {
        this.updateConnectionStatus("status-connecting");
      }
      return;
    }
    if (status === "error") {
      if (!this.isReconnectEligible()) {
        this.updateConnectionStatus("status-connection-error", true);
      }
      return;
    }
    if (status === "disconnected") {
      this.store.setConnection({ authenticated: false });
      this.cleanupRuntime();
      if (this.isReconnectEligible()) {
        this.startReconnectWindow({
          statusKey: "main-attempting-reconnect",
          speak: this.reconnectStartedAt === 0,
        });
      } else {
        this.updateConnectionStatus("status-disconnected");
        this.showAuth();
      }
    }
  }

  handleNetworkError(message, params = {}) {
    if (this.isReconnectEligible()) {
      console.warn("Network error while reconnecting:", message, params);
      return;
    }
    this.localError(message, this.currentAuthStatusEl, params);
  }

  updateConnectionStatus(keyOrText, error = false, params = {}) {
    this.connectionStatusMessage = keyOrText;
    this.connectionStatusParams = params && typeof params === "object" ? { ...params } : {};
    this.connectionStatusError = error;
    const text = Localization.has(keyOrText)
      ? Localization.get(keyOrText, this.connectionStatusParams)
      : String(keyOrText || "");
    if (this.currentAuthStatusEl && !this.elements.authScreen.hidden) {
      this.currentAuthStatusEl.textContent = text;
      this.currentAuthStatusEl.classList.toggle("error", error);
    }
  }

  isReconnectEligible() {
    return Boolean(
      this.shouldReconnect
      && !this.manualDisconnect
      && this.sessionEstablished
      && this.lastUser
      && this.lastPass
      && this.lastUrl
    );
  }

  resetReconnectState() {
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.reconnectDeadlineTimer) {
      window.clearTimeout(this.reconnectDeadlineTimer);
      this.reconnectDeadlineTimer = null;
    }
    this.reconnectAttempts = 0;
    this.reconnectStartedAt = 0;
    this.reconnectDelayMs = RECONNECT_INITIAL_DELAY_MS;
  }

  startReconnectWindow({
    initialDelayMs = 0,
    statusKey = "main-attempting-reconnect",
    params = {},
    speak = true,
  } = {}) {
    if (!this.isReconnectEligible()) {
      return;
    }
    const startingWindow = !this.reconnectStartedAt;
    if (startingWindow) {
      this.reconnectStartedAt = Date.now();
      this.reconnectDelayMs = RECONNECT_INITIAL_DELAY_MS;
      this.reconnectAttempts = 0;
      this.reconnectDeadlineTimer = window.setTimeout(() => {
        if (this.isReconnectEligible()) {
          this.failReconnect();
        }
      }, RECONNECT_WINDOW_MS);
    }
    const retryDelayMs = startingWindow
      ? initialDelayMs
      : Math.max(initialDelayMs, this.reconnectDelayMs);
    this.updateConnectionStatus(statusKey, false, params);
    if (speak) {
      this.speak(statusKey, {
        params,
        buffer: "system",
        assertive: true,
      });
    }
    this.scheduleReconnectAttempt(retryDelayMs);
  }

  scheduleReconnectAttempt(delayMs = this.reconnectDelayMs) {
    if (!this.isReconnectEligible()) {
      return;
    }
    if (this.reconnectTimer) {
      return;
    }
    const startedAt = this.reconnectStartedAt || Date.now();
    this.reconnectStartedAt = startedAt;
    const remainingMs = RECONNECT_WINDOW_MS - (Date.now() - startedAt);
    if (remainingMs <= 0) {
      this.failReconnect();
      return;
    }
    const delay = Math.max(0, Math.min(delayMs, remainingMs));
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null;
      this.performReconnectAttempt();
    }, delay);
  }

  performReconnectAttempt() {
    if (!this.isReconnectEligible()) {
      return;
    }
    const elapsedMs = Date.now() - (this.reconnectStartedAt || Date.now());
    if (elapsedMs > RECONNECT_WINDOW_MS) {
      this.failReconnect();
      return;
    }
    this.reconnectAttempts += 1;
    this.updateConnectionStatus("main-reconnecting");
    this.network.connect({
      serverUrl: this.lastUrl,
      authPacket: {
        ...clientAuthMetadata(),
        type: "authorize",
        username: this.lastUser,
        password: this.lastPass,
        version: CLIENT_VERSION,
      },
    });
    this.reconnectDelayMs = Math.min(
      Math.max(this.reconnectDelayMs, RECONNECT_INITIAL_DELAY_MS) * 2,
      RECONNECT_MAX_DELAY_MS,
    );
  }

  failReconnect() {
    this.shouldReconnect = false;
    this.manualDisconnect = true;
    this.sessionEstablished = false;
    this.resetReconnectState();
    this.network.disconnect();
    this.cleanupRuntime(true);
    this.store.setConnection({ authenticated: false, status: "disconnected" });
    this.showAuth();
    this.updateConnectionStatus("main-reconnect-failed", true);
    this.speak("main-reconnect-failed", {
      buffer: "system",
      assertive: true,
    });
  }

  disconnectManually() {
    this.shouldReconnect = false;
    this.manualDisconnect = true;
    this.sessionEstablished = false;
    this.resetReconnectState();
    this.network.disconnect();
    this.store.setConnection({ authenticated: false, status: "disconnected" });
    this.cleanupRuntime(true);
    this.showAuth();
    this.updateConnectionStatus("status-disconnected");
  }

  cleanupRuntime(full = false) {
    this.voice.cleanup(false, false);
    this.removeAllPlaylists();
    this.audio.stopAll();
    this.webSpeech.cancel();
    this.hideInlineInput();
    this.webActionsItem = null;
    this.webActionsMenuId = "";
    this.currentTableContextId = "";
    if (full) {
      this.store.clearUi();
    }
  }

  isConnected() {
    return this.network.isConnected();
  }

  send(packet) {
    return this.network.send(packet);
  }

  announceInterface(textOrKey, options = {}) {
    const {
      params = {},
      assertive = false,
      interrupt = false,
    } = options;
    const text = Localization.has(textOrKey) ? Localization.get(textOrKey, params) : String(textOrKey || "");
    if (!text) {
      return;
    }
    if (this.preferences.speech_mode === "web_speech") {
      if (interrupt) {
        this.webSpeech.speakNow(text);
      } else {
        this.webSpeech.speak(text);
      }
    } else {
      this.a11y.announce(text, { assertive });
    }
  }

  speak(textOrKey, options = {}) {
    const {
      params = {},
      buffer = "misc",
      assertive = false,
      noHistory = false,
      muted = false,
    } = options;
    const text = Localization.has(textOrKey) ? Localization.get(textOrKey, params) : String(textOrKey || "");
    if (!text) {
      return;
    }
    const normalizedBuffer = normalizeBuffer(buffer);
    let outputAllowed = !this.historyView.isBufferMuted(normalizedBuffer);
    if (!noHistory) {
      outputAllowed = this.historyView.addEntry(text, { buffer: normalizedBuffer, announce: false });
    }
    if (muted || !outputAllowed) {
      return;
    }
    if (this.preferences.speech_mode === "web_speech") {
      this.webSpeech.speak(text);
    } else {
      this.a11y.announce(text, { assertive });
    }
  }

  handlePacket(packet) {
    switch (packet.type) {
      case "login_failed":
        this.handleLoginFailed(packet);
        break;
      case "register_response":
        this.handleRegisterResponse(packet);
        break;
      case "authorize_success":
        this.handleAuthorizeSuccess(packet);
        break;
      case "speak":
        this.speak(packet.text || "", {
          buffer: normalizeBuffer(packet.buffer || "misc"),
          assertive: packet.buffer === "system",
          muted: packet.muted === true,
        });
        break;
      case "voice_join_info":
        this.voice.connect(packet, this.voice.joinGeneration);
        break;
      case "voice_join_error":
        this.handleVoiceJoinError(packet);
        break;
      case "voice_leave_ack":
        break;
      case "table_context":
        this.currentTableContextId = packet.table_id || "";
        this.voice.setTableContext(this.currentTableContextId);
        break;
      case "voice_context_closed":
        this.handleVoiceContextClosed(packet);
        break;
      case "disconnect":
        this.handleServerDisconnect(packet);
        break;
      case "force_exit":
        this.handleForceExit(packet);
        break;
      case "play_sound":
        this.audio.playSound(packet);
        break;
      case "play_music":
        this.audio.playMusic(packet);
        break;
      case "stop_music":
        this.audio.stopMusic();
        break;
      case "play_ambience":
        this.audio.playAmbience(packet);
        break;
      case "stop_ambience":
        this.audio.stopAmbience();
        break;
      case "add_playlist":
        this.addPlaylist(packet);
        break;
      case "start_playlist":
        this.startPlaylist(packet.playlist_id);
        break;
      case "remove_playlist":
        this.removePlaylist(packet.playlist_id);
        break;
      case "clear_ui":
        this.cleanupRuntime(true);
        break;
      case "chat":
        this.handleChatPacket(packet);
        break;
      case "menu":
      case "update_menu":
        this.handleMenuPacket(packet);
        break;
      case "update_options_lists":
        this.store.setServerOptions(packet.options || {});
        break;
      case "request_input":
        this.showInlineInput(packet);
        break;
      case "update_locale":
        if (packet.locale) {
          Localization.load(packet.locale).then(() => this.applyLocalization());
        }
        break;
      case "update_preference":
        this.handlePreferenceUpdate(packet);
        break;
      case "get_playlist_duration":
        this.handlePlaylistDurationRequest(packet);
        break;
      case "pong":
        this.handlePong();
        break;
      case "table_create":
        this.audio.playSound({ name: "notify.ogg" });
        if (this.preferences.notify_table_created !== false) {
          this.speak(Localization.get("table-created-notify"), { buffer: "system" });
        }
        break;
      default:
        console.warn("Unhandled packet:", packet);
        break;
    }
  }

  handleLoginFailed(packet) {
    this.shouldReconnect = false;
    this.manualDisconnect = true;
    this.sessionEstablished = false;
    this.resetReconnectState();
    const message = this.authResponseMessage(packet, "", "auth-error-wrong-password");
    this.localError(message, this.elements.loginStatus);
    this.network.disconnect();
    this.showAuthPanel("login");
  }

  handleRegisterResponse(packet) {
    const success = this.authResponseSucceeded(packet);
    const message = this.authResponseMessage(packet, "auth-registration-success");
    this.setAuthStatus(message, this.elements.registerStatus, !success);
    if (success) {
      this.showAuthPanel("login");
      if (this.elements.username && this.elements.regUsername) {
        this.elements.username.value = this.elements.regUsername.value;
      }
    }
    this.network.disconnect();
  }

  handleAuthorizeSuccess(packet) {
    this.sessionEstablished = true;
    this.shouldReconnect = true;
    this.manualDisconnect = false;
    this.resetReconnectState();
    this.store.setConnection({
      authenticated: true,
      username: packet.username || this.lastUser,
      serverUrl: this.lastUrl,
      status: "connected",
    });
    this.voice.setCapability(packet.voice || { enabled: false, provider: "", url: "" });
    if (packet.username) {
      this.lastUser = packet.username;
    }
    if (packet.sounds_info?.version) {
      this.audio.setSoundVersion(packet.sounds_info.version);
    } else if (packet.sounds_version) {
      this.audio.setSoundVersion(packet.sounds_version);
    }
    if (packet.locale && packet.locale !== Localization.locale) {
      Localization.load(packet.locale).then(() => this.applyLocalization());
    }
    if (packet.preferences) {
      this.handlePreferenceUpdate(packet);
    } else {
      this.applyPreferences();
    }
    this.saveLocalConfig();
    this.updateConnectionStatus("status-connected");
    this.showGame();
    this.speak("welcome", {
      params: { username: this.lastUser },
      buffer: "system",
    });
    this.audio.playSound({ name: "welcome.ogg" });
  }

  handleServerDisconnect(packet) {
    if (packet.reconnect === true) {
      this.shouldReconnect = true;
      this.manualDisconnect = false;
      this.sessionEstablished = true;
      this.cleanupRuntime();
      this.network.disconnect();
      this.store.setConnection({ authenticated: false, status: "disconnected" });
      this.startReconnectWindow({
        initialDelayMs: SERVER_RESTART_RECONNECT_DELAY_MS,
        statusKey: "main-reconnecting-in-3s",
        params: { seconds: Math.round(SERVER_RESTART_RECONNECT_DELAY_MS / 1000) },
        speak: true,
      });
      return;
    }
    if (packet.reconnect === false) {
      this.shouldReconnect = false;
      this.manualDisconnect = true;
      this.sessionEstablished = false;
      this.resetReconnectState();
    }
    const reason = packet.reason ? Localization.get(packet.reason) : Localization.get("status-disconnected");
    this.speak(reason, { buffer: "system", assertive: true });
    this.network.disconnect();
    this.store.setConnection({ authenticated: false, status: "disconnected" });
    if (!this.shouldReconnect) {
      this.showAuth();
    }
    this.updateConnectionStatus(reason, true);
  }

  handleForceExit(packet) {
    this.shouldReconnect = false;
    this.manualDisconnect = true;
    this.sessionEstablished = false;
    this.resetReconnectState();
    const reason = packet.reason ? Localization.get(packet.reason) : Localization.get("status-disconnected");
    this.speak(reason, { buffer: "system", assertive: true });
    this.network.disconnect();
    this.store.setConnection({ authenticated: false, status: "disconnected" });
    this.cleanupRuntime(true);
    this.showAuth();
    this.updateConnectionStatus(reason, true);
  }

  handleVoiceJoinError(packet) {
    if (
      (packet.context_id || "")
      && this.voice.requestedContextId
      && (packet.context_id || "") !== this.voice.requestedContextId
    ) {
      return;
    }
    this.voice.pendingJoin = false;
    this.voice.state = "disconnected";
    this.voice.micEnabled = false;
    this.voice.micTogglePending = null;
    this.voice.requestedContextId = "";
    this.voice.presenceRegistered = false;
    this.voice.context = { scope: "table", contextId: "" };
    this.voice.updateUI();
    this.voice.setStatus(this.voice.resolveMessage(packet), false);
  }

  handleVoiceContextClosed(packet) {
    if (
      this.voice.state === "connecting"
      && (packet.scope || "table") === "table"
      && (packet.context_id || "") === this.voice.requestedContextId
    ) {
      this.voice.cleanup(false, false);
      return;
    }
    if (
      this.voice.state !== "disconnected"
      && (packet.scope || "table") === (this.voice.context.scope || "table")
      && (packet.context_id || "") === (this.voice.context.contextId || "")
    ) {
      this.voice.cleanup(false, false);
    }
  }

  handleChatPacket(packet) {
    const sender = packet.sender || Localization.get("chat-sender-system");
    let prefix = Localization.get("chat-prefix-system");
    let speakText = packet.message || "";
    let soundName = "chat.ogg";
    let shouldSpeak = !packet.silent;
    const convo = packet.convo || "system";

    if (convo === "global") {
      prefix = `${Localization.get("chat-prefix-global")} ${sender}`;
      speakText = `${sender}: ${packet.message || ""}`;
      shouldSpeak = shouldSpeak && this.preferences.mute_global_chat !== true;
    } else if (convo === "announcement") {
      prefix = Localization.get("chat-prefix-announcement");
      speakText = `${prefix}: ${packet.message || ""}`;
      soundName = "notify.ogg";
    } else if (["local", "table", "game"].includes(convo)) {
      const tableLike = convo !== "local" || this.isGameMenu(this.store.state.currentMenu.menuId);
      prefix = `${Localization.get(tableLike ? "chat-prefix-table" : "chat-prefix-local")} ${sender}`;
      speakText = `${sender}: ${packet.message || ""}`;
      soundName = "chatlocal.ogg";
      shouldSpeak = shouldSpeak && this.preferences.mute_table_chat !== true;
    }

    const display = `${prefix}: ${packet.message || ""}`;
    const outputAllowed = this.historyView.addEntry(display, { buffer: "chat", announce: false });
    if (shouldSpeak && outputAllowed) {
      this.audio.playSound({ name: soundName });
      this.speak(speakText, { buffer: "chat", noHistory: true });
    }
  }

  isGameMenu(menuId) {
    return [
      "turn_menu",
      "actions_menu",
      "action_input_menu",
      "action_input_editbox",
      "status_box",
      "game_over",
      "leave_game_confirm",
    ].includes(menuId);
  }

  normalizeMenuItems(items) {
    return (Array.isArray(items) ? items : []).map((item) => {
      if (typeof item === "string") {
        return { text: item, id: null, sound: "" };
      }
      return {
        text: String(item?.text ?? item?.label ?? ""),
        id: item?.id ?? null,
        sound: item?.sound || "",
        selectionValue: item?.selectionValue ?? item?.selection_value ?? null,
      };
    });
  }

  voiceLanguageLabel(lang) {
    const code = String(lang || "").trim();
    if (!code) {
      return "";
    }
    try {
      const displayNames = new Intl.DisplayNames([Localization.locale || "en"], { type: "language" });
      const label = displayNames.of(code);
      if (label && label.toLowerCase() !== code.toLowerCase()) {
        return `${label} (${code})`;
      }
    } catch {
      // Older browsers may not support Intl.DisplayNames for BCP-47 tags.
    }
    return code;
  }

  stableVoiceItemId(voice, usedIds) {
    const source = this.webSpeech.voiceValue(voice) || `${voice.name || ""}|${voice.lang || ""}`;
    let hash = 0;
    for (let index = 0; index < source.length; index += 1) {
      hash = ((hash << 5) - hash + source.charCodeAt(index)) | 0;
    }
    const base = `web_voice_${Math.abs(hash).toString(36)}`;
    let id = base;
    let suffix = 2;
    while (usedIds.has(id)) {
      id = `${base}_${suffix}`;
      suffix += 1;
    }
    usedIds.add(id);
    return id;
  }

  voiceLabel(voice) {
    const parts = [voice.name || Localization.get("default-voice")];
    const language = this.voiceLanguageLabel(voice.lang);
    if (language) {
      parts.push(language);
    }
    if (voice.default) {
      parts.push(Localization.get("default-voice"));
    }
    return parts.join(", ");
  }

  buildVoiceSelectionItems() {
    const voices = this.webSpeech.getVoices();
    const usedIds = new Set(["default", "back"]);
    const items = [{
      text: Localization.get("default-voice"),
      id: "default",
      sound: "",
      selectionValue: "",
    }];
    for (const voice of voices) {
      items.push({
        text: this.voiceLabel(voice),
        id: this.stableVoiceItemId(voice, usedIds),
        sound: "",
        selectionValue: this.webSpeech.voiceValue(voice),
      });
    }
    if (!voices.length) {
      items.push({
        text: Localization.get("no-voices-found"),
        id: null,
        sound: "",
      });
    }
    items.push({ text: Localization.get("go-back"), id: "back", sound: "" });
    return items;
  }

  refreshVoiceSelectionMenuIfOpen() {
    if (this.store.state.currentMenu.menuId !== "voice_selection_menu") {
      return;
    }
    const previousSelectionId = this.store.state.currentMenu.items[this.store.state.currentMenu.selection]?.id || "";
    const items = this.buildVoiceSelectionItems();
    const selection = Math.max(0, items.findIndex((item) => item.id === previousSelectionId));
    this.store.setMenu({ items, selection });
  }

  handleMenuPacket(packet) {
    this.hideInlineInput();
    let items = this.normalizeMenuItems(packet.items);
    if (packet.menu_id === "voice_selection_menu") {
      this.webSpeech.requestVoiceRefresh();
      items = this.buildVoiceSelectionItems();
    }

    this.webActionsItem = null;
    this.webActionsMenuId = packet.menu_id || this.store.state.currentMenu.menuId || "";
    items = items.filter((item) => {
      if (item.id === "web_actions_menu") {
        this.webActionsItem = item;
        return false;
      }
      return true;
    });

    const previousMenu = this.store.state.currentMenu;
    const oldFocusedId = this.focusedMenuItemId() || previousMenu.items[previousMenu.selection]?.id || "";
    let selection = 0;
    if (packet.selection_id !== undefined && packet.selection_id !== null) {
      const index = items.findIndex((item) => item.id === packet.selection_id);
      if (index >= 0) {
        selection = index;
      }
    } else if (packet.position !== undefined && packet.position !== null) {
      selection = clampNumber(packet.position, 0, Math.max(0, items.length - 1), 0);
    } else if (previousMenu.menuId === packet.menu_id && oldFocusedId) {
      const index = items.findIndex((item) => item.id === oldFocusedId);
      selection = index >= 0 ? index : clampNumber(previousMenu.selection, 0, Math.max(0, items.length - 1), 0);
    } else if (previousMenu.menuId === packet.menu_id) {
      selection = clampNumber(previousMenu.selection, 0, Math.max(0, items.length - 1), 0);
    }

    const title = packet.title || this.titleFromMenuId(packet.menu_id);
    const shouldFocus = this.shouldFocusMenuAfterPacket(previousMenu.menuId, packet.menu_id);
    this.store.setMenu({
      menuId: packet.menu_id || null,
      title,
      items,
      selection,
      multiletterEnabled: packet.multiletter_enabled !== undefined
        ? Boolean(packet.multiletter_enabled)
        : previousMenu.multiletterEnabled,
      escapeBehavior: packet.escape_behavior || previousMenu.escapeBehavior || "keybind",
      gridEnabled: Boolean(packet.grid_enabled),
      gridWidth: Math.max(1, Number(packet.grid_width) || 1),
    });
    this.updateActionsButton();
    this.audio.preloadEffects?.(items.map((item) => item.sound).filter(Boolean));
    if (shouldFocus) {
      requestAnimationFrame(() => this.menuView.focusSelection());
    }
  }

  shouldFocusMenuAfterPacket(previousMenuId, nextMenuId) {
    if (this.focusMenuOnNextPacket) {
      this.focusMenuOnNextPacket = false;
      return true;
    }
    const active = document.activeElement;
    if (!active || active === document.body) {
      return true;
    }
    if (this.elements.menuList?.contains(active)) {
      return true;
    }
    if (!previousMenuId || previousMenuId !== nextMenuId) {
      return false;
    }
    return false;
  }

  focusedMenuItemId() {
    const active = document.activeElement;
    if (!active) {
      return "";
    }
    const row = active.closest?.("[data-item-id]");
    if (row && this.elements.menuList?.contains(row)) {
      return row.dataset.itemId || "";
    }
    return "";
  }

  titleFromMenuId(menuId) {
    if (!menuId) {
      return Localization.get("tab-menu");
    }
    return String(menuId)
      .replace(/_/g, " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  updateActionsButton() {
    if (!this.elements.actionsBtn) {
      return;
    }
    this.elements.actionsBtn.hidden = !this.webActionsItem;
    if (this.webActionsItem) {
      this.elements.actionsBtn.textContent = this.webActionsItem.text || Localization.get("context-menu");
    }
  }

  activateMenuItem(item, index) {
    if (!item || item.id === null || item.id === undefined) {
      return;
    }
    this.focusMenuOnNextPacket = true;
    const packet = {
      type: "menu",
      menu_id: this.store.state.currentMenu.menuId,
      selection: index + 1,
      selection_id: item.id,
    };
    if (item.selectionValue !== null && item.selectionValue !== undefined) {
      packet.selection_value = item.selectionValue;
    }
    this.send(packet);
  }

  playSelectionSound(item) {
    if (item?.sound) {
      this.audio.playSound({ name: item.sound });
    } else {
      this.audio.playSound({ name: "menuclick.ogg", volume: 50 });
    }
    if (this.preferences.speech_mode === "web_speech" && item?.text) {
      this.webSpeech.speakNow(item.text);
    }
  }

  sendEscape() {
    if (!this.isConnected()) {
      return;
    }
    if (!this.elements.inlineInput?.hidden) {
      this.cancelInlineInput();
      return;
    }
    const menu = this.store.state.currentMenu;
    const behavior = menu.escapeBehavior || "keybind";
    if (behavior === "escape_event") {
      this.focusMenuOnNextPacket = true;
      this.send({
        type: "escape",
        menu_id: menu.menuId,
      });
      return;
    }
    if (behavior === "back") {
      this.focusMenuOnNextPacket = true;
      this.send({
        type: "menu",
        menu_id: menu.menuId,
        selection_id: "back",
      });
      return;
    }
    if (behavior === "select_last_option" || behavior === "select_first_option") {
      const index = behavior === "select_last_option" ? menu.items.length - 1 : 0;
      const item = menu.items[index];
      if (item) {
        this.focusMenuOnNextPacket = true;
        this.audio.playSound({ name: "menuenter.ogg", volume: 50 });
        this.send({
          type: "menu",
          menu_id: menu.menuId,
          selection: index + 1,
          selection_id: item.id,
        });
      }
      return;
    }
    this.sendKeybind("escape", this.focusedMenuItemId());
  }

  sendKeybind(key, menuItemId = "", modifiers = {}) {
    if (!this.isConnected()) {
      return false;
    }
    if (typeof key === "object" && key !== null) {
      return this.send({
        type: "keybind",
        key: key.key,
        menu_id: key.menu_id ?? this.store.state.currentMenu.menuId,
        menu_index: key.menu_index ?? (this.store.state.currentMenu.selection + 1),
        menu_item_id: key.menu_item_id ?? this.focusedMenuItemId() ?? "",
        shift: Boolean(key.shift),
        control: Boolean(key.control ?? key.ctrl),
        alt: Boolean(key.alt),
        meta: Boolean(key.meta),
      });
    }
    return this.send({
      type: "keybind",
      key,
      menu_id: this.store.state.currentMenu.menuId,
      menu_index: this.store.state.currentMenu.selection + 1,
      menu_item_id: menuItemId || this.focusedMenuItemId() || "",
      shift: Boolean(modifiers.shift),
      control: Boolean(modifiers.ctrl || modifiers.control),
      alt: Boolean(modifiers.alt),
      meta: Boolean(modifiers.meta),
    });
  }

  openWebActionsMenu() {
    if (!this.webActionsItem || !this.isConnected()) {
      return;
    }
    this.focusMenuOnNextPacket = true;
    this.send({
      type: "menu",
      menu_id: this.webActionsMenuId || this.store.state.currentMenu.menuId,
      selection_id: "web_actions_menu",
    });
  }

  getActiveInlineInputElement() {
    const singleLine = this.elements.inlineInputText;
    const multiline = this.elements.inlineInputValue;
    if (singleLine && !singleLine.hidden) {
      return singleLine;
    }
    if (multiline && !multiline.hidden) {
      return multiline;
    }
    return null;
  }

  isTypingSoundKey(event) {
    if (
      event.ctrlKey
      || event.altKey
      || event.metaKey
      || event.isComposing
      || event.key.length !== 1
    ) {
      return false;
    }
    const input = this.getActiveInlineInputElement();
    if (!input || input.readOnly || input.disabled) {
      return false;
    }
    const code = event.key.charCodeAt(0);
    return code >= 32;
  }

  playTypingSound() {
    if (this.preferences.play_typing_sounds === false) {
      return;
    }
    const soundNum = Math.floor(Math.random() * 4) + 1;
    this.audio.playSound({ name: `typing${soundNum}.ogg`, volume: 50 });
  }

  handleInlineInputKeydown(event) {
    if (!this.pendingInput || event.isComposing) {
      return;
    }
    const activeInput = this.getActiveInlineInputElement();
    const isMultiline = activeInput === this.elements.inlineInputValue && !activeInput.hidden;

    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      this.cancelInlineInput();
      return;
    }

    if (event.key === "Enter") {
      const modified = event.shiftKey || event.ctrlKey;
      const hasNonTextModifier = event.altKey || event.metaKey;
      const inverted = this.preferences.invert_multiline_enter_behavior === true;
      const shouldSubmit = !isMultiline
        || activeInput?.readOnly
        || (!inverted && !modified && !hasNonTextModifier)
        || (inverted && modified && !hasNonTextModifier);

      if (shouldSubmit) {
        event.preventDefault();
        event.stopPropagation();
        this.submitInlineInput();
      }
      return;
    }

    if (this.isTypingSoundKey(event)) {
      this.playTypingSound();
    }
  }

  showInlineInput(packet) {
    this.pendingInput = packet;
    const prompt = packet.prompt || packet.title || "";
    const multiline = packet.multiline === true;
    const activeInput = multiline ? this.elements.inlineInputValue : this.elements.inlineInputText;
    const inactiveInput = multiline ? this.elements.inlineInputText : this.elements.inlineInputValue;

    if (this.elements.inlineInputPrompt) {
      this.elements.inlineInputPrompt.textContent = prompt;
      if (activeInput?.id) {
        this.elements.inlineInputPrompt.setAttribute("for", activeInput.id);
      }
    }
    if (inactiveInput) {
      inactiveInput.hidden = true;
      inactiveInput.value = "";
      inactiveInput.readOnly = false;
      inactiveInput.removeAttribute("maxlength");
      inactiveInput.removeAttribute("aria-label");
    }
    if (activeInput) {
      activeInput.hidden = false;
      activeInput.value = packet.default_value || "";
      activeInput.readOnly = Boolean(packet.read_only);
      activeInput.setAttribute("aria-label", prompt);
      if (packet.max_length) {
        activeInput.maxLength = Number(packet.max_length);
      } else {
        activeInput.removeAttribute("maxlength");
      }
    }
    if (this.elements.inlineInput) {
      this.elements.inlineInput.hidden = false;
    }
    this.speak(prompt, { buffer: "system", noHistory: true });
    requestAnimationFrame(() => {
      activeInput?.focus?.({ preventScroll: false });
      try {
        activeInput?.select?.();
      } catch {
        activeInput?.setSelectionRange?.(0, activeInput.value.length);
      }
    });
  }

  hideInlineInput() {
    this.pendingInput = null;
    if (this.elements.inlineInput) {
      this.elements.inlineInput.hidden = true;
    }
    for (const input of [this.elements.inlineInputText, this.elements.inlineInputValue]) {
      if (!input) {
        continue;
      }
      input.hidden = input === this.elements.inlineInputValue;
      input.value = "";
      input.readOnly = false;
      input.removeAttribute("maxlength");
      input.removeAttribute("aria-label");
    }
  }

  submitInlineInput() {
    if (!this.pendingInput) {
      return;
    }
    const value = this.getActiveInlineInputElement()?.value || "";
    this.send({
      type: "editbox",
      input_id: this.pendingInput.input_id,
      text: value,
      value,
    });
    this.hideInlineInput();
    this.focusMenuOnNextPacket = true;
  }

  cancelInlineInput() {
    if (!this.pendingInput) {
      return;
    }
    this.send({
      type: "editbox",
      input_id: this.pendingInput.input_id,
      text: "",
      value: "",
      cancelled: true,
      cancel: true,
    });
    this.hideInlineInput();
    this.focusMenuOnNextPacket = true;
  }

  sendChatFromInput() {
    const raw = this.elements.chatInput?.value.trim() || "";
    if (!raw || !this.isConnected()) {
      return;
    }
    if (raw.startsWith("/")) {
      this.handleChatCommand(raw);
    } else if (raw.startsWith(".")) {
      const message = raw.slice(1).trim();
      if (message) {
        this.send({ type: "chat", convo: "global", message });
      }
    } else {
      this.send({ type: "chat", convo: "local", message: raw });
    }
    this.elements.chatInput.value = "";
  }

  handleChatCommand(raw) {
    const parts = raw.split(" ");
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1).join(" ");
    if (["/g", "/global", "/shout", "/s"].includes(cmd)) {
      this.send({ type: "chat", convo: "global", message: args });
      return true;
    }
    if (["/adm", "/adms", "/admin", "/admins", "/dev", "/devs"].includes(cmd)) {
      this.send({ type: "admins_cmd" });
      return true;
    }
    if (["/broadcast", "/bcast", "/announce", "/notify", "/alert"].includes(cmd)) {
      this.send({ type: "broadcast_cmd", message: args });
      return true;
    }
    if (["/reboot", "/restart", "/stop", "/shutdown", "/exit", "/kick"].includes(cmd)) {
      this.send({ type: "chat", convo: "global", message: raw });
      return true;
    }
    this.send({ type: "slash_command", command: cmd.slice(1), args });
    return true;
  }

  sendListOnline(includeGames = false) {
    if (!this.isConnected()) {
      return;
    }
    this.send({ type: includeGames ? "list_online_with_games" : "list_online" });
    this.speak(includeGames ? "requesting-game-list" : "requesting-player-list", { buffer: "system" });
  }

  openFriendsHub() {
    if (this.send({ type: "open_friends_hub" })) {
      this.speak(Localization.get("requesting-friends-hub"), { buffer: "system" });
    }
  }

  openAdminMenu() {
    if (this.send({ type: "open_admin_menu" })) {
      this.speak(Localization.get("requesting-admin-menu"), { buffer: "system" });
    }
  }

  openOptionsMenu() {
    if (this.send({ type: "open_options" })) {
      this.speak(Localization.get("requesting-options"), { buffer: "system" });
    }
  }

  sendPing() {
    if (!this.isConnected()) {
      return;
    }
    this.pingStart = Date.now();
    this.audio.playSound({ name: "pingstart.ogg" });
    this.send({ type: "ping" });
  }

  toggleChatMute(scope) {
    if (!this.isConnected()) {
      return;
    }
    const isGlobal = scope === "global";
    const flatKey = isGlobal ? "mute_global_chat" : "mute_table_chat";
    const serverKey = isGlobal ? "social/mute_global_chat" : "social/mute_table_chat";
    const nextValue = this.preferences[flatKey] !== true;
    this.preferences[flatKey] = nextValue;
    this.saveLocalConfig();
    this.send({ type: "set_preference", key: serverKey, value: nextValue });
    const scopeKey = isGlobal ? "main-chat-scope-global" : "main-chat-scope-table";
    const statusKey = nextValue
      ? "main-chat-mute-state-muted"
      : "main-chat-mute-state-unmuted";
    this.speak("main-chat-mute-status", {
      params: {
        scope: Localization.get(scopeKey),
        status: Localization.get(statusKey),
      },
      buffer: "system",
      noHistory: true,
    });
  }

  handlePong() {
    if (!this.pingStart) {
      return;
    }
    const latency = Date.now() - this.pingStart;
    this.pingStart = null;
    this.audio.playSound({ name: "pingstop.ogg" });
    this.speak("main-ping-result", {
      params: { value: latency },
      buffer: "system",
    });
  }

  handlePreferenceUpdate(packet) {
    let updates = {};
    if (packet.preferences) {
      updates = packet.preferences;
      this.preferences = { ...this.preferences, ...updates };
    } else if (packet.key) {
      const flatKey = String(packet.key).split("/").pop();
      this.preferences[flatKey] = packet.value;
      updates[flatKey] = packet.value;
    }
    this.applyPreferences();
    if (updates.muted_buffers !== undefined) {
      this.historyView.setMutedBuffers(updates.muted_buffers || []);
    }
    if (updates.speech_voice !== undefined || updates.speech_mode !== undefined || updates.speech_rate !== undefined) {
      this.webSpeech.applyPreferences();
    }
    this.saveLocalConfig();
  }

  addPlaylist(packet) {
    const id = packet.playlist_id || "music_playlist";
    this.removePlaylist(id);
    const playlist = new Playlist(this, id, packet.tracks, {
      audio_type: packet.audio_type,
      shuffle: packet.shuffle_tracks,
      repeats: packet.repeats,
      auto_remove: packet.auto_remove,
    });
    this.playlists[id] = playlist;
    if (packet.auto_start) {
      playlist.start();
    }
  }

  startPlaylist(id) {
    const playlist = this.playlists[id];
    if (playlist) {
      playlist.start();
    }
  }

  removePlaylist(id) {
    if (this.playlists[id]) {
      this.playlists[id].stop();
      delete this.playlists[id];
    }
  }

  removeAllPlaylists() {
    for (const id of Object.keys(this.playlists)) {
      this.removePlaylist(id);
    }
  }

  handlePlaylistDurationRequest(packet) {
    if (!packet.playlist_id || !this.playlists[packet.playlist_id]) {
      return;
    }
    this.send({
      type: "playlist_duration_response",
      request_id: packet.request_id,
      playlist_id: packet.playlist_id,
      duration_type: packet.duration_type,
      duration: 0,
    });
  }

  isStandalone() {
    return window.matchMedia?.("(display-mode: standalone)").matches || window.navigator.standalone === true;
  }

  installPwa() {
    if (this.deferredPrompt) {
      this.deferredPrompt.prompt();
      this.deferredPrompt.userChoice.finally(() => {
        this.deferredPrompt = null;
        if (this.elements.installBtn) {
          this.elements.installBtn.hidden = true;
        }
      });
    } else if (this.elements.installInstruction) {
      this.elements.installInstruction.textContent = Localization.get("install-fail-hint");
      this.elements.installInstruction.hidden = false;
    }
  }
}

async function bootstrap() {
  const validator = await loadPacketValidator();
  const app = new PlayAuralWebApp({ validator });
  await app.init();
  window.playAuralWebClient = app;
}

bootstrap().catch((error) => {
  console.error("PlayAural web client failed to start.", error);
  const target = byId("live-assertive") || document.body;
  const message = document.createElement("p");
  message.textContent = Localization.get("startup-error");
  target.appendChild(message);
});
