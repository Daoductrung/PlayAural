console.log("Game.js initialized.");
const CLIENT_VERSION = "1.0.1";

// reCAPTCHA v3 site key — replace with your production key before launch.
// When empty, CAPTCHA is skipped entirely (graceful degradation for dev).
const RECAPTCHA_SITE_KEY = "";
let recaptchaReadyPromise = null;

function setRecaptchaVisibility(visible) {
    document.body?.classList.toggle('recaptcha-hidden', !visible);
}

async function ensureRecaptchaReady() {
    if (!RECAPTCHA_SITE_KEY) {
        return false;
    }

    if (typeof grecaptcha !== 'undefined' && typeof grecaptcha.ready === 'function') {
        await new Promise(resolve => grecaptcha.ready(resolve));
        return true;
    }

    if (!recaptchaReadyPromise) {
        recaptchaReadyPromise = new Promise((resolve) => {
            const existing = document.querySelector('script[data-recaptcha="playaural"]');
            if (existing) {
                existing.addEventListener('load', () => {
                    if (typeof grecaptcha !== 'undefined' && typeof grecaptcha.ready === 'function') {
                        grecaptcha.ready(() => resolve(true));
                    } else {
                        resolve(false);
                    }
                }, { once: true });
                existing.addEventListener('error', () => resolve(false), { once: true });
                return;
            }

            const script = document.createElement('script');
            script.src = `https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}`;
            script.async = true;
            script.defer = true;
            script.dataset.recaptcha = "playaural";
            script.onload = () => {
                if (typeof grecaptcha !== 'undefined' && typeof grecaptcha.ready === 'function') {
                    grecaptcha.ready(() => resolve(true));
                } else {
                    resolve(false);
                }
            };
            script.onerror = () => {
                console.warn("Failed to load reCAPTCHA script.");
                resolve(false);
            };
            document.head.appendChild(script);
        });
    }

    return await recaptchaReadyPromise;
}

/**
 * Get a reCAPTCHA v3 token for the given action.
 * Returns a structured result so auth flows can stop locally when
 * reCAPTCHA is blocked or fails to execute.
 */
async function getCaptchaTokenResult(action) {
    if (!RECAPTCHA_SITE_KEY) {
        return { ok: true, token: "", skipped: true };
    }

    const captchaReady = await ensureRecaptchaReady();
    if (!captchaReady || typeof grecaptcha === 'undefined') {
        return { ok: false, token: "", reason: "auth-error-captcha-unavailable" };
    }

    try {
        const token = await grecaptcha.execute(RECAPTCHA_SITE_KEY, { action });
        if (!token) {
            return { ok: false, token: "", reason: "auth-error-captcha-unavailable" };
        }
        return { ok: true, token };
    } catch (err) {
        console.warn("reCAPTCHA token error:", err);
        return { ok: false, token: "", reason: "auth-error-captcha-execute-failed" };
    }
}

class Localization {
    static strings = {}; // Loaded from window.LOCALES (locales.js)
    static locale = "en";

    static applyDocumentLanguage(locale) {
        if (document?.documentElement) {
            document.documentElement.lang = locale || "en";
        }
    }

    static async load(locale) {
        if (window.LOCALES && window.LOCALES[locale]) {
            this.strings = window.LOCALES[locale];
            this.locale = locale;
            this.applyDocumentLanguage(locale);
            console.log(`Loaded locale from script: ${locale}`);
            return;
        }

        // Method 2: Fetch JSON - Works for http://
        try {
            const response = await fetch(`locales/${locale}.json`);
            if (!response.ok) throw new Error(`Failed to load locale ${locale} via fetch`);
            this.strings = await response.json();
            this.locale = locale;
            this.applyDocumentLanguage(locale);
            console.log(`Loaded locale via fetch: ${locale}`);
        } catch (err) {
            console.warn("Localization fetch failed (normal if offline/file://):", err);

            // Fallback: If we tried to load a locale not in LOCALES and fetch failed, 
            // try falling back to 'en' from LOCALES if available
            if (window.LOCALES && window.LOCALES['en']) {
                this.strings = window.LOCALES['en'];
                this.locale = "en";
                this.applyDocumentLanguage("en");
                console.log("Fell back to built-in English");
            } else {
                // Hard fallback (Should not be reached if locales.js is loaded)
                this.strings = {};
                this.locale = "en";
                this.applyDocumentLanguage("en");
                console.error("Critical: No localization data found!");
            }
        }
    }

    static get(key, params = {}) {
        let str = this.strings[key] || key;

        // Handle parameters: {key} and {$key}
        // Also check if params is actually the object we want, or if it's nested
        // Sometimes server sends params flat in the packet, sometimes in 'params' dict

        const data = params || {};

        for (const [k, v] of Object.entries(data)) {
            // Replace {key}
            str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
            // Replace {$key} (Fluent style)
            str = str.replace(new RegExp(`\\{\\$${k}\\}`, 'g'), v);
        }
        return str;
    }
    static has(key) {
        return Object.prototype.hasOwnProperty.call(this.strings, key);
    }
}




class SoundManager {
    constructor(gameClient) {
        this.client = gameClient;
        this.ctx = null;
        this.masterGain = null;
        this.musicGain = null;
        this.sfxGain = null;
        this.ambienceGain = null;

        // Assets
        this.cache = new Map(); // url -> AudioBuffer (for SFX only)
        this.loading = new Map(); // url -> Promise

        // State - Streaming Audio Elements
        this.currentMusicElement = null;
        this.currentMusicSource = null; // MediaElementSource
        this.currentMusicUrl = null;
        this.currentMusicGain = null; // fade gain

        this.ambienceIntroElement = null;
        this.ambienceLoopElement = null;
        this.ambienceOutroElement = null;

        this.ambienceIntroSource = null;
        this.ambienceLoopSource = null;
        this.ambienceOutroSource = null;

        this.ambienceState = 'stopped'; // stopped, loading, intro, looping, outro
        this.ambienceConfig = null; // {intro, loop, outro}

        // Settings (managed by GameClient, but mirrored here for direct access)
        this.settings = {
            musicVolume: 0.2,
            sfxVolume: 1.0,
            ambienceVolume: 0.3
        };
        this.wakeLockSource = null;
    }

    init() {
        if (this.ctx) return;

        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioContext();

        // Create Bus Structure
        this.masterGain = this.ctx.createGain();
        this.masterGain.connect(this.ctx.destination);

        this.musicGain = this.ctx.createGain();
        this.musicGain.connect(this.masterGain);

        this.sfxGain = this.ctx.createGain();
        this.sfxGain.connect(this.masterGain);

        this.ambienceGain = this.ctx.createGain();
        this.ambienceGain.connect(this.masterGain);

        this.updateVolumes();
        console.log("SoundManager: Audio Context Initialized");
    }

    async resume() {
        if (!this.ctx) this.init();
        if (this.ctx.state === 'suspended') {
            await this.ctx.resume();
            console.log("SoundManager: Audio Context Resumed");
        }
    }

    updateVolumes() {
        if (!this.ctx) return;
        const now = this.ctx.currentTime;

        const targetMusic = this.settings.musicVolume;

        // Use setTargetAtTime for smooth volume transitions (0.1s time constant)
        this.musicGain.gain.setTargetAtTime(targetMusic, now, 0.1);
        this.sfxGain.gain.setTargetAtTime(this.settings.sfxVolume, now, 0.1);
        this.ambienceGain.gain.setTargetAtTime(this.settings.ambienceVolume, now, 0.1);

        // Update elements directly if not yet connected (e.g. cross-origin fallback)
        if (this.currentMusicElement && !this.currentMusicSource) {
            this.currentMusicElement.volume = targetMusic;
        }
    }

    setVolume(type, value) {
        if (type === 'music') this.settings.musicVolume = value;
        if (type === 'sound') this.settings.sfxVolume = value;
        if (type === 'ambience') this.settings.ambienceVolume = value;
        this.updateVolumes();
    }

    // --- Audio Wake-Lock (Android Fix) ---
    // Plays a continuous, completely silent buffer to prevent the AudioContext
    // and associated services (like SpeechSynthesis) from suspending.
    startAudioWakeLock() {
        if (!this.ctx || this.wakeLockSource) return;

        console.log("SoundManager: Starting Audio Wake-Lock...");
        try {
            // Create a short silent buffer (1 second of silence)
            const buffer = this.ctx.createBuffer(1, this.ctx.sampleRate, this.ctx.sampleRate);
            this.wakeLockSource = this.ctx.createBufferSource();
            this.wakeLockSource.buffer = buffer;
            this.wakeLockSource.loop = true;

            // Connect to destination via a 0 volume gain node for absolute silence
            const silence = this.ctx.createGain();
            silence.gain.value = 0;

            this.wakeLockSource.connect(silence);
            silence.connect(this.ctx.destination);

            this.wakeLockSource.start(0);
        } catch (e) {
            console.error("SoundManager: Failed to start Audio Wake-Lock", e);
        }
    }

    stopAudioWakeLock() {
        if (this.wakeLockSource) {
            console.log("SoundManager: Stopping Audio Wake-Lock.");
            try {
                this.wakeLockSource.stop();
                this.wakeLockSource.disconnect();
            } catch (e) { }
            this.wakeLockSource = null;
        }
    }

    // --- Helper for Streaming Audio ---
    createAudioElement(url) {
        const audio = new Audio();
        // audio.crossOrigin = "anonymous"; // If loading from CDNs later
        audio.src = url;
        return audio;
    }

    connectElement(audio, gainNode) {
        if (!this.ctx || !gainNode) return false;
        try {
            const source = this.ctx.createMediaElementSource(audio);
            source.connect(gainNode);
            return source;
        } catch (e) {
            console.warn("SoundManager: Failed to connect element source (CORS?)", e);
            // Fallback: Audio element plays directly to destination (no bus effects/volume control via Web Audio)
            // Manual volume control required
            return null;
        }
    }

    // --- SFX (Short sounds, kept as Buffer) ---
    async loadBuffer(filename) {
        if (!filename) return null;
        const versionParam = this.client.soundsVersion ? `?v=${this.client.soundsVersion}` : '';
        const url = `sounds/${filename}${versionParam}`;

        if (this.cache.has(url)) return this.cache.get(url);
        if (this.loading.has(url)) return this.loading.get(url);

        const loadPromise = fetch(url)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.arrayBuffer();
            })
            .then(arrayBuffer => this.ctx.decodeAudioData(arrayBuffer))
            .then(audioBuffer => {
                this.cache.set(url, audioBuffer);
                this.loading.delete(url);
                return audioBuffer;
            })
            .catch(err => {
                console.warn(`SoundManager: Failed to load ${url}`, err);
                this.loading.delete(url);
                return null;
            });

        this.loading.set(url, loadPromise);
        return loadPromise;
    }

    async playSound(filename, { volume = 1.0, pan = 0.0, pitch = 1.0 } = {}) {
        await this.resume();
        const buffer = await this.loadBuffer(filename);
        if (!buffer) return null;

        const source = this.ctx.createBufferSource();
        source.buffer = buffer;
        source.playbackRate.value = pitch;

        const panner = this.ctx.createStereoPanner();
        panner.pan.value = Math.max(-1, Math.min(1, pan));

        const gain = this.ctx.createGain();
        gain.gain.value = volume;

        // Chain: source -> panner -> localGain -> sfxBus
        source.connect(panner);
        panner.connect(gain);
        gain.connect(this.sfxGain);

        source.start(0);
        return source;
    }

    // --- Streaming Music ---
    async playMusic(filename, loop = true) {
        if (this.currentMusicUrl === filename && this.currentMusicElement && !this.currentMusicElement.paused) {
            // Already playing this track
            this.currentMusicElement.loop = loop;
            return;
        }

        await this.resume();
        const versionParam = this.client.soundsVersion ? `?v=${this.client.soundsVersion}` : '';
        const url = `sounds/${filename}${versionParam}`;

        // Crossfade: Fade out existing
        this.stopMusic(true);

        const audio = this.createAudioElement(url);
        audio.loop = loop;
        audio.preload = "auto";

        // Connect to Web Audio
        // Create a local gain for fade-in
        const fadeGain = this.ctx.createGain();
        fadeGain.gain.value = 0; // Start silent

        const source = this.connectElement(audio, fadeGain);
        if (source) {
            fadeGain.connect(this.musicGain);
        } else {
            // Fallback if connection failed (CORS), play directly
            // We can't do fancy fade-in easily without Web Audio, just set volume
            audio.volume = this.settings.musicVolume;
        }

        try {
            await audio.play();
        } catch (e) {
            console.warn("SoundManager: Music play failed (autoplay?)", e);
            return;
        }

        // Fade in logic if Web Audio connected
        if (source) {
            const now = this.ctx.currentTime;
            fadeGain.gain.linearRampToValueAtTime(1.0, now + 1.0);
        }

        this.currentMusicElement = audio;
        this.currentMusicSource = source;
        this.currentMusicGain = fadeGain;
        this.currentMusicUrl = filename;
    }

    stopMusic(fade = true) {
        if (!this.currentMusicElement) return;

        const audio = this.currentMusicElement;
        const source = this.currentMusicSource;
        const gain = this.currentMusicGain;

        // Detach current reference
        this.currentMusicElement = null;
        this.currentMusicSource = null;
        this.currentMusicGain = null;
        this.currentMusicUrl = null;

        if (fade && gain && this.ctx) {
            const now = this.ctx.currentTime;
            try { gain.gain.cancelScheduledValues(now); } catch (e) { }
            gain.gain.setValueAtTime(gain.gain.value, now);
            gain.gain.linearRampToValueAtTime(0, now + 1.0);

            setTimeout(() => {
                audio.pause();
                audio.src = ""; // Unload
                if (source) source.disconnect();
                gain.disconnect();
            }, 1100);
        } else {
            audio.pause();
            audio.src = "";
            if (source) source.disconnect();
            if (gain) gain.disconnect();
        }
    }

    // --- Streaming Ambience ---
    async playAmbience(intro, loopFile, outro) {
        await this.resume();

        // Stop any existing ambience immediately (force stop)
        this.stopAmbience(true);

        this.ambienceConfig = { intro, loop: loopFile, outro };
        this.ambienceState = 'loading';

        // Helper to prepare element
        const prepare = (filename, loop) => {
            if (!filename) return null;
            const versionParam = this.client.soundsVersion ? `?v=${this.client.soundsVersion}` : '';
            const audio = this.createAudioElement(`sounds/${filename}${versionParam}`);
            audio.loop = loop;
            audio.preload = "auto";
            return audio;
        };

        const introEl = prepare(intro, false);
        const loopEl = prepare(loopFile, true);
        const outroEl = prepare(outro, false);

        if (introEl) {
            this.ambienceState = 'intro';
            this.ambienceIntroElement = introEl;
            this.ambienceIntroSource = this.connectElement(introEl, this.ambienceGain);

            // Chain events
            introEl.onended = () => {
                if (this.ambienceState === 'intro') {
                    this._startAmbienceLoop(loopEl);
                }
            };

            try { await introEl.play(); } catch (e) { console.warn("Ambience intro play error", e); }
        } else {
            this._startAmbienceLoop(loopEl);
        }

        // Store references for later cleanup
        this.ambienceLoopElement = loopEl;
        this.ambienceOutroElement = outroEl;
    }

    async _startAmbienceLoop(loopEl) {
        if (this.ambienceState === 'stopped') return;
        if (!loopEl) return;

        this.ambienceState = 'looping';
        this.ambienceLoopSource = this.connectElement(loopEl, this.ambienceGain);

        try { await loopEl.play(); } catch (e) { console.warn("Ambience loop play error", e); }
    }

    stopAmbience(force = false) {
        const prevState = this.ambienceState;
        this.ambienceState = 'stopped';

        // Stop active elements
        const stopEl = (el, src) => {
            if (el) {
                el.pause();
                el.src = "";
                el.onended = null;
                if (src) src.disconnect();
            }
        };

        // Always stop intro and loop
        stopEl(this.ambienceIntroElement, this.ambienceIntroSource);
        stopEl(this.ambienceLoopElement, this.ambienceLoopSource);
        this.ambienceIntroElement = null;
        this.ambienceLoopElement = null;
        this.ambienceIntroSource = null;
        this.ambienceLoopSource = null;

        // Outro: play gracefully on non-force stop, kill on force stop
        if (!force && this.ambienceOutroElement && prevState !== 'stopped' && prevState !== 'loading') {
            // Play outro — keep references so a future force stop can cancel it
            this.ambienceOutroSource = this.connectElement(this.ambienceOutroElement, this.ambienceGain);
            this.ambienceOutroElement.onended = () => {
                stopEl(this.ambienceOutroElement, this.ambienceOutroSource);
                this.ambienceOutroElement = null;
                this.ambienceOutroSource = null;
            };
            try { this.ambienceOutroElement.play(); } catch (e) { }
        } else {
            // Force stop or no outro — clean up everything
            stopEl(this.ambienceOutroElement, this.ambienceOutroSource);
            this.ambienceOutroElement = null;
            this.ambienceOutroSource = null;
        }

        if (force) this.ambienceConfig = null;
    }
}


class Playlist {
    constructor(client, id, tracks, options = {}) {
        this.client = client;
        this.id = id;
        this.originalTracks = [...tracks];
        this.tracks = [...tracks];
        this.audioType = options.audio_type || "music";
        this.shuffle = options.shuffle || false;
        this.repeats = options.repeats !== undefined ? options.repeats : 1; // 0 = infinite
        this.autoRemove = options.auto_remove !== undefined ? options.auto_remove : true;

        this.currentIndex = 0;
        this.currentRepeat = 1;
        this.active = false;
        this.currentAudioSource = null; // We track source node now

        if (this.shuffle) {
            this.shuffleTracks();
        }
    }

    shuffleTracks() {
        for (let i = this.tracks.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.tracks[i], this.tracks[j]] = [this.tracks[j], this.tracks[i]];
        }
    }

    start() {
        this.active = true;
        this.playNext();
    }

    stop() {
        this.active = false;
        // If playing SFX (playlist managed), stop it.
        // If playing Music, GameClient/SoundManager handles it (mostly).
        // Actually, if we are controlling music, we should stop it too?
        // Python: playlist.stop just stops logic, sound manager handles playback.
        if (this.audioType !== "music" && this.currentAudioSource) {
            try { this.currentAudioSource.stop(); } catch (e) { }
            this.currentAudioSource = null;
        }
    }

    async playNext() {
        if (!this.active || this.tracks.length === 0) return;

        // Check if playlist finished
        if (this.currentIndex >= this.tracks.length) {
            this.currentIndex = 0;
            this.currentRepeat++;

            // Check repeats (if not infinite 0)
            if (this.repeats !== 0 && this.currentRepeat > this.repeats) {
                this.stop();
                if (this.autoRemove) {
                    this.client.removePlaylist(this.id);
                }
                return;
            }
        }

        const filename = this.tracks[this.currentIndex];
        this.currentIndex++;

        if (this.audioType === "music") {
            // Play as music (replaces current music)
            // Note: playMusic is now async, so we MUST await it to ensure source is active
            // and correct before attaching onended listener.
            // loop=false because playlist handles the sequence.
            await this.client.soundManager.playMusic(filename, false);

            // Now currentMusicSource is guaranteed to be the new one
            if (this.client.soundManager.currentMusicSource) {
                this.client.soundManager.currentMusicSource.onended = () => this.playNext();
            }

        } else {
            // Play as sound
            const source = await this.client.soundManager.playSound(filename, {
                volume: 1.0 // Playlist volume?
            });

            if (source) {
                this.currentAudioSource = source;
                source.onended = () => {
                    this.playNext();
                };
            }
        }
    }
}

class GameClient {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.manualDisconnect = false;

        // UI Elements
        this.loginScreen = document.getElementById('login-screen');
        this.registerScreen = document.getElementById('register-screen');
        this.forgotPasswordScreen = document.getElementById('forgot-password-screen');
        this.resetPasswordScreen = document.getElementById('reset-password-screen');
        this.gameScreen = document.getElementById('game-screen');

        this.loginForm = document.getElementById('login-form');
        this.registerForm = document.getElementById('register-form');
        this.forgotPasswordForm = document.getElementById('forgot-password-form');
        this.resetPasswordForm = document.getElementById('reset-password-form');

        this.statusMsg = document.getElementById('login-status');
        this.regStatusMsg = document.getElementById('register-status');
        this.forgotStatusMsg = document.getElementById('forgot-password-status');
        this.resetStatusMsg = document.getElementById('reset-password-status');

        // Initialize preferences (default values matching server)
        this.preferences = {
            play_turn_sound: true,
            music_volume: 20,
            ambience_volume: 20,
            mute_global_chat: false,
            mute_table_chat: false,
            notify_table_created: true,
            play_typing_sounds: true,
            speech_mode: "aria",
            speech_rate: 100,
            speech_voice: ""
        };
        this.menuArea = document.getElementById('menu-area');

        // Tabs
        this.tabs = document.querySelectorAll('.tab-btn');
        this.tabContents = document.querySelectorAll('.tab-content');
        this.activeTab = 'content-menu';

        // Chat & History
        this.chatHistory = document.getElementById('chat-history');
        this.ttsHistoryLog = document.getElementById('tts-history-log');
        this.chatForm = document.getElementById('chat-form');
        this.chatInput = document.getElementById('chat-input');

        // Audio Settings
        this.musicVolume = 0.2; // Default 20%
        this.soundVolume = 1.0;
        this.ambienceVolume = 0.3;

        // Audio System
        this.soundManager = new SoundManager(this);
        this.soundManager.setVolume('music', this.musicVolume);
        // Note: musicVolume init value is 0.2
        this.soundManager.setVolume('sound', this.soundVolume);
        this.soundManager.setVolume('ambience', this.ambienceVolume);


        this.soundsVersion = null;

        // Speech Queue System (ARIA)
        this.speechQueue = [];
        this.isSpeaking = false;
        this.currentAnnouncerIndex = 0;
        this.speechDelay = 200;

        // Speech Debounce State
        this.lastAnnouncementText = "";
        this.lastAnnouncementTime = 0;

        // Voice Caching (Latency Optimization)
        this.cachedVoices = [];
        this.targetVoice = null;

        // Web Speech API Queue System (Manual Management for Android Stability)
        this.ttsQueue = [];
        this.isTTSPlaying = false;
        this.ttsTimeout = null;
        this.ttsKeepAliveInterval = null; // Periodic silent "kick" for Android engine

        // Reconnection state
        this.reconnectAttempts = 0;
        this.reconnectTimer = null;
        this.connectionAttemptInProgress = false;
        this.connectionAttemptTimer = null;


        // Load Localization
        // Default to 'en', but prefer stored preference if available (loaded in loadConfig -> clientOptions but we are in constructor here)
        // Actually constructor calls loadConfig() at end.
        // Let's rely on server 'update_locale' to set final locale, or load 'en' first.
        Localization.load("en").then(() => {
            console.log("Localization ready");
            this.updateUIText();
        });

        // Bind events
        // Tabs
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetId = tab.getAttribute('aria-controls');
                this.switchTab(targetId);
            });
        });

        // Shortcuts Tab
        document.getElementById('btn-list-online').onclick = () => {
            this.sendListOnline(false);
        };
        document.getElementById('btn-list-online-games').onclick = () => {
            this.sendListOnline(true);
        };
        document.getElementById('btn-open-friends').onclick = () => {
            if (!this.isConnected) return;
            this.socket.send(JSON.stringify({ type: "open_friends_hub" }));
            this.speak("requesting-friends-hub");
        };
        document.getElementById('btn-open-options').onclick = () => {
            if (!this.isConnected) return;
            this.socket.send(JSON.stringify({ type: "open_options" }));
            this.speak("requesting-options");
        };
        document.getElementById('btn-check-ping').onclick = () => {
            this.sendPing();
        };

        // Table Options Removed (Used to be btn-table-options)

        // Initialize Audio Context on first interaction (Touch included)
        const initAudioOnce = () => {
            this.soundManager.resume();

            // "Unlock" TTS on Android Chrome (Warm-up)
            // Play a silent utterance to get permissions and wake up the engine
            if (window.speechSynthesis) {
                const silent = new SpeechSynthesisUtterance("");
                silent.volume = 0; // Silent
                window.speechSynthesis.speak(silent);
                console.log("TTS Warm-up triggered.");
            }

            // Remove listeners after first successful init
            if (this.soundManager.ctx && this.soundManager.ctx.state === 'running') {
                document.removeEventListener('click', initAudioOnce);
                document.removeEventListener('keydown', initAudioOnce);
                document.removeEventListener('touchstart', initAudioOnce);
            }
        };

        document.addEventListener('click', initAudioOnce);
        document.addEventListener('keydown', initAudioOnce);
        document.addEventListener('touchstart', initAudioOnce);

        // Initialize Voices (Async)
        this.voicesLoaded = false;
        if (window.speechSynthesis) {
            // Load initial if available
            this.cachedVoices = window.speechSynthesis.getVoices();
            if (this.cachedVoices.length > 0) this.voicesLoaded = true;

            // Update when loaded/changed
            window.speechSynthesis.onvoiceschanged = () => {
                this.cachedVoices = window.speechSynthesis.getVoices();
                this.voicesLoaded = true;
                console.log(`Voices updated: ${this.cachedVoices.length} voices found.`);
                // Re-calculate target voice if needed
                if (this.preferences.speech_voice) {
                    this.updateTargetVoice();
                }
            };
        }

        // Load saved config
        this.clientOptions = {
            social: {
                mute_global_chat: false,
                mute_table_chat: false
            }
        };
        this.loadConfig();


        // PWA Install Prompt
        this.deferredPrompt = null;
        window.addEventListener('beforeinstallprompt', (e) => {
            if (this.isStandalone()) {
                return;
            }
            // Prevent Chrome 67 and earlier from automatically showing the prompt
            e.preventDefault();
            // Stash the event so it can be triggered later.
            this.deferredPrompt = e;
            // Update UI to notify the user they can add to home screen
            const installBtn = document.getElementById('btn-install-pwa');
            if (installBtn) {
                installBtn.classList.remove('hidden');
                // Ensure text is updated if localization loaded already
                if (Localization.locale) installBtn.innerText = Localization.get('btn-install');
            }
            console.log("PWA Install Prompt captured");
        });

        window.addEventListener('appinstalled', () => {
            this.deferredPrompt = null;
            const installBtn = document.getElementById('btn-install-pwa');
            if (installBtn) {
                installBtn.classList.add('hidden');
            }
        });

        // Detect iOS
        this.isIOS = (
            /iPad|iPhone|iPod/.test(navigator.userAgent) ||
            (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1)
        ) && !window.MSStream;

    }

    isStandalone() {
        return window.matchMedia?.('(display-mode: standalone)').matches || window.navigator.standalone === true;
    }

    installPWA() {
        if (!this.deferredPrompt) return;
        // Show the prompt
        this.deferredPrompt.prompt();
        // Wait for the user to respond to the prompt
        this.deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the A2HS prompt');
            } else {
                console.log('User dismissed the A2HS prompt');
            }
            this.deferredPrompt = null;
            // Hide button after use
            document.getElementById('btn-install-pwa').classList.add('hidden');
        });
    }

    loadConfig() {
        try {
            const configStr = localStorage.getItem('playaural_config');
            if (configStr) {
                const config = JSON.parse(configStr);

                // Restore connection details
                if (config.lastServer) document.getElementById('server-url').value = config.lastServer;
                if (config.lastUsername) document.getElementById('username').value = config.lastUsername;

                // Restore audio settings
                if (config.musicVolume !== undefined) {
                    this.musicVolume = config.musicVolume;
                    this.soundManager.setVolume('music', this.musicVolume);
                }
                if (config.soundVolume !== undefined) {
                    this.soundVolume = config.soundVolume;
                    this.soundManager.setVolume('sound', this.soundVolume);
                }
                if (config.ambienceVolume !== undefined) {
                    this.ambienceVolume = config.ambienceVolume;
                    this.soundManager.setVolume('ambience', this.ambienceVolume);
                }

                // Restore preferences
                if (config.preferences) {
                    this.preferences = { ...this.preferences, ...config.preferences };
                    console.log("Restored preferences:", this.preferences);

                    // Initialize TTS Keep-Alive if mode was saved as web_speech
                    if (this.preferences.speech_mode === "web_speech") {
                        this.startTTSKeepAlive();
                    }
                }
                // Legacy support
                else if (config.clientOptions) {
                    console.log("Migrating legacy clientOptions to preferences");
                    if (config.clientOptions.social) {
                        if (config.clientOptions.social.mute_global_chat !== undefined)
                            this.preferences.mute_global_chat = config.clientOptions.social.mute_global_chat;
                        if (config.clientOptions.social.mute_table_chat !== undefined)
                            this.preferences.mute_table_chat = config.clientOptions.social.mute_table_chat;
                    }
                }

                console.log("Config loaded");
            }
        } catch (e) {
            console.warn("Failed to load config", e);
        }
    }

    saveConfig() {
        const config = {
            lastServer: document.getElementById('server-url').value,
            lastUsername: document.getElementById('username').value,
            musicVolume: this.musicVolume,
            soundVolume: this.soundVolume,
            ambienceVolume: this.ambienceVolume,
            preferences: this.preferences, // Save flat preferences
        };
        localStorage.setItem('playaural_config', JSON.stringify(config));

        // Save Credentials if "Remember Me" is checked.
        // When checked: password persists in localStorage (explicit user opt-in).
        // When unchecked: password lives in sessionStorage only (cleared on browser close).
        if (this.lastUser && this.lastPass) {
            const autoLogin = document.getElementById('chk-auto-login').checked;
            if (autoLogin) {
                localStorage.setItem('pa_user', this.lastUser);
                localStorage.setItem('pa_pass', this.lastPass);
                localStorage.setItem('pa_remember', '1');
            }
        }
    }

    switchTab(tabId) {
        // Deactivate all
        this.tabs.forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
        });

        // Hide all contents
        this.tabContents.forEach(c => {
            // Note: content-history is now a standard tab. The old hidden background-active logic
            // was presumably for a different unseen history element or legacy code.
            // We just use standard hidden toggles for the new actual History tab.
            c.classList.add('hidden');
            c.classList.remove('background-active');
        });

        // Activate target
        const activeTabBtn = document.querySelector(`.tab-btn[aria-controls="${tabId}"]`);
        const activeContent = document.getElementById(tabId);

        if (activeTabBtn && activeContent) {
            activeTabBtn.classList.add('active');
            activeTabBtn.setAttribute('aria-selected', 'true');

            if (tabId === 'content-chat' && !document.getElementById('chat-history-view').classList.contains('hidden')) {
                // If chat tab is active AND looking at its own chat-history
                const chatLog = document.getElementById('chat-history');
                if (chatLog) chatLog.scrollTop = chatLog.scrollHeight;
            } else if (tabId === 'content-history') {
                if (this.ttsHistoryLog) this.ttsHistoryLog.scrollTop = 0; // Since it's prepended
            }

            activeContent.classList.remove('hidden');

            this.activeTab = tabId;

            // WEB-SPECIFIC: Toggle Special Buttons Visibility
            const actionsContainer = document.getElementById('web-actions-container');
            const leaveContainer = document.getElementById('web-leave-container');
            
            if (tabId === 'content-menu') {
                if (actionsContainer) actionsContainer.classList.remove('hidden');
                if (leaveContainer) leaveContainer.classList.remove('hidden');
            } else {
                if (actionsContainer) actionsContainer.classList.add('hidden');
                if (leaveContainer) leaveContainer.classList.add('hidden');
            }
        }
    }

    showChatHistory() {
        document.getElementById('chat-input-view').classList.add('hidden');
        document.getElementById('chat-history-view').classList.remove('hidden');
        this.speak(Localization.get('chat-history-view-active') || "Chat History");
    }

    showChatInput() {
        document.getElementById('chat-history-view').classList.add('hidden');
        document.getElementById('chat-input-view').classList.remove('hidden');
        this.speak(Localization.get('chat-input-view-active') || "Chat Input");
        setTimeout(() => {
            const input = document.getElementById('chat-input');
            if (input) input.focus();
        }, 100);
    }



    addToChatLog(message, sender, senderClass) {
        const container = this.chatHistory;
        const entry = document.createElement('div');
        entry.className = "log-entry";

        // Build with DOM nodes so server-controlled text is never parsed as HTML.
        if (sender) {
            const senderSpan = document.createElement('span');
            senderSpan.className = `log-sender ${senderClass}`;
            senderSpan.textContent = `${sender}:`;
            entry.appendChild(senderSpan);
            entry.appendChild(document.createTextNode(' '));
        }

        const msgSpan = document.createElement('span');
        msgSpan.className = 'log-msg';
        msgSpan.textContent = message;
        entry.appendChild(msgSpan);

        // NEW LOGIC: Prepend (Newest First) for mobile optimization
        if (container.firstChild) {
            container.insertBefore(entry, container.firstChild);
        } else {
            container.appendChild(entry);
        }

        // No auto-scroll needed since we are at top
        container.scrollTop = 0;
    }

    sendChat() {
        const msg = this.chatInput.value.trim();
        if (!msg || !this.socket || !this.isConnected) return;

        // Slash command parsing
        if (msg.startsWith('/')) {
            if (this.handleChatCommand(msg)) {
                this.chatInput.value = "";
                return;
            }
        }

        // Normal chat
        // Match Python client: convo="local"
        this.socket.send(JSON.stringify({
            type: "chat",
            convo: "local",
            message: msg
        }));

        this.chatInput.value = "";
    }

    handleChatCommand(msg) {
        const parts = msg.split(' ');
        const cmd = parts[0].toLowerCase();
        const args = parts.slice(1).join(' ');

        // --- Global Chat Aliases ---
        const globals = ['/g', '/global', '/shout', '/s'];
        if (globals.includes(cmd)) {
            this.socket.send(JSON.stringify({
                type: "chat",
                convo: "global",
                message: args
            }));
            return true;
        }

        // --- Admins ---
        const admins = ['/adm', '/adms', '/admin', '/admins', '/dev', '/devs'];
        if (admins.includes(cmd)) {
            this.socket.send(JSON.stringify({ type: "admins_cmd" }));
            return true;
        }

        // --- Broadcast ---
        const bcasts = ['/broadcast', '/bcast', '/announce', '/notify', '/alert'];
        if (bcasts.includes(cmd)) {
            this.socket.send(JSON.stringify({ type: "broadcast_cmd", message: args }));
            return true;
        }



        // --- Server Admin (Reboot/Stop/Kick) ---
        // These are sent as Global Chat messages for server to intercept
        const serverAdmin = ['/reboot', '/restart', '/stop', '/shutdown', '/exit', '/kick'];
        if (serverAdmin.includes(cmd)) {
            this.socket.send(JSON.stringify({
                type: "chat",
                convo: "global",
                message: msg // Construct exact message like "/kick user"
            }));
            return true;
        }

        // --- Fallback (Send as generic slash command) ---
        // This covers any other commands server might support
        this.socket.send(JSON.stringify({
            type: "slash_command",
            command: cmd.substring(1),
            args: args
        }));
        return true;
    }

    sendListOnline(includeGames = false) {
        if (!this.isConnected) {
            console.warn("Cannot list players: Not connected");
            return;
        }

        // Fix: Use correct packet type for games list
        const type = includeGames ? "list_online_with_games" : "list_online";
        const packet = { type: type };

        this.socket.send(JSON.stringify(packet));
        this.speak(includeGames ? "requesting-game-list" : "requesting-player-list");
    }



    async play_sound(filename, options = {}) {
        return this.soundManager.playSound(filename, options);
    }



    speak(text, params = {}) {
        // Debug localization params
        console.log(`Queueing Speech: ${text}`, params);

        const localized = Localization.get(text, params);

        // Add to history tab
        this.addToHistoryLog(localized);

        // Web Speech API Mode
        if (this.preferences.speech_mode === "web_speech") {
            this.speakTTS(localized);
            return;
        }

        // Aria-live Mode (Default)
        this.speechQueue.push(localized);
        this.processSpeechQueue();
    }

    addToHistoryLog(message) {
        const log = document.getElementById("tts-history-log");
        if (!log) return;

        const entry = document.createElement("div");
        entry.className = "log-entry";
        entry.tabIndex = 0; // Focusable for screen readers

        // Timestamp
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

        const timeSpan = document.createElement("span");
        timeSpan.style.color = "#888";
        timeSpan.style.marginRight = "8px";
        timeSpan.innerText = `[${timeStr}]`;

        const msgSpan = document.createElement("span");
        msgSpan.innerText = message;

        entry.appendChild(timeSpan);
        entry.appendChild(msgSpan);

        // Prepend to show newest at the top
        log.prepend(entry);

        // Optional: Keep history bounded (e.g. 100 entries)
        while (log.children.length > 100) {
            log.removeChild(log.lastChild);
        }
    }

    speakTTS(text) {
        if (!window.speechSynthesis) return;

        // Optimization: Chunk long text for Android Stability (<200 chars safe zone)
        // Split by punctuation or length
        const chunks = this.chunkText(text, 160);

        chunks.forEach(chunk => {
            this.ttsQueue.push(chunk);
        });

        this.processTTSQueue();
    }

    chunkText(text, maxLength) {
        if (text.length <= maxLength) return [text];

        const chunks = [];
        let remaining = text;

        while (remaining.length > 0) {
            if (remaining.length <= maxLength) {
                chunks.push(remaining);
                break;
            }

            // Find best split point (punctuation) within the limit
            let splitIndex = -1;
            const punctuations = ['.', '!', '?', ';', ','];

            for (const p of punctuations) {
                const idx = remaining.lastIndexOf(p, maxLength);
                if (idx > splitIndex) splitIndex = idx;
            }

            // If no punctuation found, split by space
            if (splitIndex === -1) {
                splitIndex = remaining.lastIndexOf(' ', maxLength);
            }

            // If still no split point (one huge number?), force split
            if (splitIndex === -1) {
                splitIndex = maxLength;
            } else {
                splitIndex += 1; // Include the punctuation/space
            }

            chunks.push(remaining.substring(0, splitIndex).trim());
            remaining = remaining.substring(splitIndex).trim();
        }
        return chunks;
    }

    processTTSQueue() {
        if (this.isTTSPlaying) return;

        if (this.ttsQueue.length === 0) {
            return;
        }

        this.isTTSPlaying = true;
        const text = this.ttsQueue.shift();

        // 1. Resume (Non-blocking)
        if (window.speechSynthesis && window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
        }

        // Cancel persistent utterances
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        // 2. Optimized Voice Selection
        if (this.targetVoice) {
            utterance.voice = this.targetVoice;
        } else {
            // Fallback: Try to find in cache or fetch if empty
            if (this.cachedVoices.length === 0) {
                this.cachedVoices = window.speechSynthesis.getVoices();
            }

            if (this.preferences.speech_voice) {
                const found = this.cachedVoices.find(v => v.voiceURI === this.preferences.speech_voice);
                if (found) {
                    this.targetVoice = found;
                    utterance.voice = found;
                }
            }
        }

        // 3. Rate: Allow up to 10.0 and map 300% -> 3.0 (or higher if needed)
        let serverRate = this.preferences.speech_rate || 100;
        const rate = serverRate / 100.0;
        utterance.rate = Math.max(0.1, Math.min(rate, 10.0)); // Browser max is usually 10

        // Explicitly set language
        if (Localization.locale) {
            utterance.lang = Localization.locale;
        }

        // 4. Watchdog with "Nuclear Reset" capability
        if (this.ttsTimeout) clearTimeout(this.ttsTimeout);

        // Duration estimation
        const baseTime = (text.length * 200) / rate;
        const estimatedDuration = Math.max(4000, baseTime + 5000); // Increased min buffer to 4s

        this.ttsTimeout = setTimeout(() => {
            console.warn(`TTS Watchdog: Speech timed out after ${estimatedDuration}ms. Triggering NUCLEAR RESET.`);
            this.resetTTS(); // Hard reset
            // Skip current item to prevents loops
            this.isTTSPlaying = false;
            this.processTTSQueue();
        }, estimatedDuration);


        // Event Handling
        utterance.onstart = () => {
            console.log("TTS Started");
        };

        utterance.onend = () => {
            console.log("TTS Ended");
            if (this.ttsTimeout) clearTimeout(this.ttsTimeout);
            this.isTTSPlaying = false;
            this.processTTSQueue();
        };

        utterance.onerror = (e) => {
            console.warn("TTS Error:", e);
            if (this.ttsTimeout) clearTimeout(this.ttsTimeout);
            this.isTTSPlaying = false;
            this.processTTSQueue(); // Just proceed
        };

        // Android GC Fix: explicit reference to prevent garbage collection during playback
        this.currentUtterance = utterance;

        window.speechSynthesis.speak(utterance);

        // Final "Kick": Aggressive resume to ensure playback starts on stubborn Android devices
        if (window.speechSynthesis.paused) window.speechSynthesis.resume();
    }

    // Android Keep-Alive Mechanism
    // Periodically speaks a zero-volume silent string to prevent the Android engine 
    // from suspending during idle periods, eliminating the "wake-up" latency.
    startTTSKeepAlive() {
        if (!window.speechSynthesis || this.ttsKeepAliveInterval) return;

        console.log("Starting TTS Keep-Alive (Android Fix - 1s interval)");
        
        // Start the Audio Wake-Lock as well for maximum protection
        this.soundManager.startAudioWakeLock();

        this.ttsKeepAliveInterval = setInterval(() => {
            // Only kick if engine is NOT currently speaking to avoid interruptions
            if (!window.speechSynthesis.speaking && this.ttsQueue.length === 0) {
                const kick = new SpeechSynthesisUtterance(" "); // Non-empty but silent space
                kick.volume = 0;
                kick.rate = 10; // Fast as possible
                // Tag it to avoid watchdog interference if we ever track it
                kick._isKeepAlive = true;
                window.speechSynthesis.speak(kick);
            }
        }, 1000); // 1-second interval for aggressive wake-lock
    }

    stopTTSKeepAlive() {
        if (this.ttsKeepAliveInterval) {
            console.log("Stopping TTS Keep-Alive");
            clearInterval(this.ttsKeepAliveInterval);
            this.ttsKeepAliveInterval = null;
            
            // Stop Audio Wake-Lock
            this.soundManager.stopAudioWakeLock();
        }
    }

    // New "Nuclear Reset" for stuck Android TTS
    resetTTS() {
        console.log("Performing TTS Nuclear Reset...");
        if (!window.speechSynthesis) return;

        // 1. Cancel everything
        window.speechSynthesis.cancel();

        // 2. Toggle Pause/Resume to unstick internal state
        if (window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
        } else {
            window.speechSynthesis.pause();
            window.speechSynthesis.resume();
        }

        // 3. Nullify flags
        this.isTTSPlaying = false;
        this.ttsTimeout = null;

        // 4. Force re-fetch voices (async)
        window.speechSynthesis.getVoices();
    }

    processSpeechQueue() {
        if (this.isSpeaking || this.speechQueue.length === 0) return;

        this.isSpeaking = true;
        const message = this.speechQueue.shift();

        // DEBOUNCE: Filter duplicates within 700ms
        const now = Date.now();
        const cleanMessage = String(message).trim();

        if (cleanMessage === this.lastAnnouncementText && (now - this.lastAnnouncementTime) < 700) {
            // Skip duplicate
            console.log("Skipped duplicate speech:", cleanMessage);
            this.isSpeaking = false;
            this.processSpeechQueue(); // Process next
            return;
        }

        this.lastAnnouncementText = cleanMessage;
        this.lastAnnouncementTime = now;

        // Use dual rotating aria-live regions for real-time games
        // Alternating between regions ensures screen readers detect every announcement
        this.currentAnnouncerIndex = (this.currentAnnouncerIndex + 1) % 2;
        const announcerId = `sr-announcer-${this.currentAnnouncerIndex + 1}`;
        const srAnnouncer = document.getElementById(announcerId);

        if (srAnnouncer) {
            // Clear the region first to ensure change detection
            srAnnouncer.textContent = '';

            // Use requestAnimationFrame to ensure DOM update before setting new content
            requestAnimationFrame(() => {
                srAnnouncer.textContent = message;

                // Throttle next message
                setTimeout(() => {
                    this.isSpeaking = false;
                    this.processSpeechQueue();
                }, this.speechDelay);
            });
        }
    }



    speak_l(key, params = {}) {
        this.speak(key, params);
    }





    play_music(filename, loop = true) {
        this.soundManager.playMusic(filename, loop);
    }

    stop_music() {
        this.soundManager.stopMusic(true);
    }



    // Server packet handlers usually call this
    async on_server_play_ambience(packet) {
        await this.soundManager.playAmbience(packet.intro, packet.loop, packet.outro);
    }

    on_server_stop_ambience(packet) {
        // Python server sends: type="stop_ambience" (no force param usually)
        // But if it did, we should support it.
        const force = packet.force || false;
        this.soundManager.stopAmbience(force);
    }

    stop_ambience() {
        this.soundManager.stopAmbience();
    }

    // New Playlist Methods
    addPlaylist(packet) {
        const id = packet.playlist_id || "music_playlist";
        // Stop existing if any
        if (this.playlists[id]) {
            this.playlists[id].stop();
        }

        const playlist = new Playlist(this, id, packet.tracks, {
            audio_type: packet.audio_type,
            shuffle: packet.shuffle_tracks,
            repeats: packet.repeats,
            auto_remove: packet.auto_remove
        });

        this.playlists[id] = playlist;

        if (packet.auto_start) {
            playlist.start();
        }
    }

    startPlaylist(id) {
        if (this.playlists[id]) {
            this.playlists[id].start();
        }
    }

    removePlaylist(id) {
        if (this.playlists[id]) {
            this.playlists[id].stop();
            delete this.playlists[id];
        }
    }

    removeAllPlaylists() {
        for (const id in this.playlists) {
            this.playlists[id].stop();
        }
        this.playlists = {};
    }

    handlePreferenceUpdate(packet) {
        console.log("Updating preference (RAW):", packet);
        let updates = {};

        // Merge new preferences (bulk update from authorize)
        if (packet.preferences) {
            this.preferences = { ...this.preferences, ...packet.preferences };
            updates = packet.preferences;
            console.log("Preferences Updated (Bulk):", this.preferences);
        }
        // Single preference update (from update_preference packet)
        else if (packet.key) {
            // Server sends keys like "social/mute_global_chat"
            const keyParts = packet.key.split('/');
            const flatKey = keyParts[keyParts.length - 1];
            const value = packet.value;

            console.log(`Setting Preference: ${flatKey} = ${value} (Type: ${typeof value})`);

            // Force update
            this.preferences[flatKey] = value;
            updates[flatKey] = value;
        }

        // Apply Side Effects (Audio Volume, etc)
        if (updates.music_volume !== undefined) {
            this.setMusicVolume(updates.music_volume / 100.0);
        }
        if (updates.sound_volume !== undefined) {
            this.setSoundVolume(updates.sound_volume / 100.0);
        }
        if (updates.ambience_volume !== undefined) {
            this.setAmbienceVolume(updates.ambience_volume / 100.0);
        }

        // Handle Speech Preferences
        if (updates.speech_mode !== undefined) {
            console.log("Speech Mode set to:", updates.speech_mode);
            if (updates.speech_mode === "web_speech") {
                this.startTTSKeepAlive();
            } else {
                this.stopTTSKeepAlive();
            }
        }
        if (updates.speech_rate !== undefined) console.log("Speech Rate set to:", updates.speech_rate);
        if (updates.speech_voice !== undefined) {
            console.log("Speech Voice set to:", updates.speech_voice);
            this.updateTargetVoice();
        }

        this.saveConfig();
        console.log("Current Preferences Snapshot:", JSON.stringify(this.preferences));
    }

    updateTargetVoice() {
        if (!this.cachedVoices || !this.cachedVoices.length) return;
        const found = this.cachedVoices.find(v => v.voiceURI === this.preferences.speech_voice);
        this.targetVoice = found || null;
        if (this.targetVoice) console.log(`Target Voice cached: ${this.targetVoice.name}`);
    }

    handlePacket(packet) {
        switch (packet.type) {
            case "login_failed":
                this.socket.close();
                const reasonKey = "auth-error-" + (packet.reason || "unknown").replace(/_/g, '-');
                const errorText = Localization.get(reasonKey) || Localization.get("login-info-failed");

                this.manualDisconnect = true;
                this.disconnectReason = errorText;
                this.speak(errorText); // Ensure error is announced
                break;

            case "register_response":
                this.finishConnectionAttempt();
                if (packet.status === "success") {
                    const msg = Localization.get("auth-registration-success");
                    if (this.regStatusMsg) this.regStatusMsg.innerText = msg;
                    this.speak(msg);
                } else {
                    const errKey = "auth-" + (packet.error || "error").replace(/_/g, '-');
                    const errMsg = Localization.get(errKey) || packet.text || "Registration failed.";
                    if (this.regStatusMsg) this.regStatusMsg.innerText = errMsg;
                    this.speak(errMsg);
                }
                break;

            case "speak":
                // Handle speak packets from server
                // Server sends: text (server-localized), key (localization key), params

                // 1. Try Client-side localization (Override)
                if (packet.key && Localization.has(packet.key)) {
                    this.speak_l(packet.key, packet.params || {});
                }
                // 2. Fallback to Server-side localization (Default)
                else if (packet.text) {
                    this.speak(packet.text);
                }
                // 3. Last resort: Try key anyway
                else if (packet.key) {
                    this.speak_l(packet.key, packet.params || {});
                }
                break;

            case "authorize_success":
                this.isConnected = true;
                this.finishConnectionAttempt();
                this.disconnectReason = null; // Clear any previous error
                console.log("Authorized as:", packet.username);

                if (packet.sounds_info && packet.sounds_info.version) {
                    this.soundsVersion = packet.sounds_info.version;
                }

                // Apply server-sent locale if present
                if (packet.locale && packet.locale !== Localization.locale) {
                    console.log(`Server locale: ${packet.locale}, switching from ${Localization.locale}`);
                    Localization.load(packet.locale).then(() => {
                        this.updateUIText();
                    });
                }

                // 1. Show Game UI immediately
                this.showGame();

                // 2. Update Preferences
                if (packet.preferences) {
                    try {
                        this.handlePreferenceUpdate(packet);
                    } catch (e) {
                        console.error("Error updating preferences:", e);
                    }
                }

                // 3. Save everything
                this.saveConfig();

                // 4. Welcome message
                this.speak_l("welcome", { username: packet.username });
                this.play_sound("welcome.ogg");
                break;

            case "disconnect":
                if (packet.reconnect === false) {
                    this.shouldReconnect = false;
                    this.manualDisconnect = true;
                }
                this.socket.close();
                const targetMsg = this.isRegistering ? this.regStatusMsg : this.statusMsg;
                const reason = Localization.get(packet.reason || "status-disconnected");
                targetMsg.innerText = reason;
                this.speak(reason);
                break;

            case "force_exit":
                // Server explicitly forcing disconnect (Kick, Logout, etc)
                console.log("Force Exit received");
                this.shouldReconnect = false;
                this.manualDisconnect = true;
                this.socket.close();
                if (packet.reason) {
                    const forceReason = Localization.get(packet.reason);
                    if (this.statusMsg) this.statusMsg.innerText = forceReason;
                    this.speak(forceReason);
                }
                break;

            // Audio packets
            case "play_sound":
                if (packet.name) {
                    // Normalize standard server audio params (0-100/200 scale -> 0.0-1.0/2.0 scale)
                    const vol = (packet.volume !== undefined) ? packet.volume / 100.0 : 1.0;
                    const pan = (packet.pan !== undefined) ? packet.pan / 100.0 : 0.0;
                    const pitch = (packet.pitch !== undefined) ? packet.pitch / 100.0 : 1.0;

                    this.play_sound(packet.name, {
                        volume: vol,
                        pan: pan,
                        pitch: pitch
                    });
                }
                break;
            case "play_music":
                if (packet.name) this.play_music(packet.name, packet.looping);
                break;
            case "stop_music":
                this.stop_music();
                break;
            case "play_ambience":
                this.on_server_play_ambience(packet);
                break;
            case "stop_ambience":
                this.on_server_stop_ambience(packet);
                break;

            // Playlist packets
            case "add_playlist":
                this.addPlaylist(packet);
                break;
            case "start_playlist":
                this.startPlaylist(packet.playlist_id);
                break;
            case "remove_playlist":
                this.removePlaylist(packet.playlist_id);
                break;
            case "clear_ui": // Also clears playlists
                this.removeAllPlaylists();
                this.renderMenu({ items: [], grid_enabled: false, grid_width: 1 }); // Clear menu
                break;

            case "chat":
                // 1. Logic Parity with Python Client (on_receive_chat)
                const sender = packet.sender || "System";
                let displaySender = sender;
                let logClass = "log-channel-system"; // Default
                let soundName = "chat.ogg";
                let speakText = "";
                let shouldSpeak = true;

                if (packet.convo === "global") {
                    logClass = "log-channel-global";
                    const prefix = Localization.get("chat-prefix-global");
                    displaySender = `${prefix} ${sender}`;
                    speakText = `${sender}: ${packet.message}`;

                    if (this.preferences.mute_global_chat === true) {
                        shouldSpeak = false;
                    }

                } else if (packet.convo === "announcement") {
                    logClass = "log-channel-system";
                    const prefix = Localization.get("chat-prefix-announcement") || Localization.get("system-announcement");
                    displaySender = prefix;
                    speakText = `${prefix}: ${packet.message}`;
                    soundName = "notify.ogg";

                } else if (packet.convo === "local" || packet.convo === "table" || packet.convo === "game") {
                    logClass = "log-channel-table";

                    // Logic Parity: Determine if we are "In Game" to show [Table] vs [Local]
                    // Python client doesn't use prefixes, but user wants [Table] when in game.
                    // Server sends "local" for both.

                    let tagKey = "chat-prefix-local"; // Default

                    // Check if we are in a game context
                    const gameMenus = [
                        "turn_menu",
                        "actions_menu",
                        "action_input_menu",
                        "status_box",
                        "game_over",
                        "leave_game_confirm"
                    ];

                    if (this.currentMenuId && gameMenus.includes(this.currentMenuId)) {
                        tagKey = "chat-prefix-table";
                    }

                    // Override if server explicitly sent "table" or "game" (future proofing)
                    if (packet.convo === "table" || packet.convo === "game") {
                        tagKey = "chat-prefix-table";
                    }

                    const prefix = Localization.get(tagKey);
                    displaySender = `${prefix} ${sender}`;
                    speakText = `${sender}: ${packet.message}`;
                    soundName = "chatlocal.ogg";

                    if (this.preferences.mute_table_chat === true) {
                        shouldSpeak = false;
                    }
                } else {
                    // Default / System messages
                    const prefix = Localization.get("chat-prefix-system");
                    displaySender = `${prefix} ${sender}`;
                    speakText = `${packet.message}`;
                }

                if (shouldSpeak && !packet.silent) {
                    this.play_sound(soundName);
                    this.speak(speakText);
                }

                this.addToChatLog(packet.message, displaySender, logClass);
                break;

            case "menu":
                if (packet.menu_id === "actions_menu" || packet.menu_id === "leave_game_confirm") {
                    this.showModalMenu(packet);
                } else {
                    this.closeModal();
                    this.renderMenu(packet);
                }
                break;

            case "update_menu":
                if (packet.menu_id === "actions_menu" || packet.menu_id === "leave_game_confirm") {
                    this.showModalMenu(packet);
                } else {
                    this.renderMenu(packet);
                }
                break;

            case "update_options_lists":
                // Store server options (game variants, etc) for potential use
                if (packet.options) {
                    this.serverOptions = packet.options;
                    console.log("Updated server options:", this.serverOptions);
                }
                break;

            case "request_input":
                this.closeModal();
                this.showInput(packet);
                break;


            case "update_locale":
                // Server requests locale change
                if (packet.locale) {
                    Localization.load(packet.locale).then(() => {
                        this.speak("Locale updated to " + packet.locale);
                        this.updateUIText();
                    });
                }
                break;

            case "update_preference":
                this.handlePreferenceUpdate(packet);
                break;



            case "get_playlist_duration":
                // Server requests playlist duration info
                // This is complex timing calculation, simplified for web
                if (packet.playlist_id && this.playlists[packet.playlist_id]) {
                    const playlist = this.playlists[packet.playlist_id];
                    // Send back a response (duration not easily calculable in web without preloading)
                    this.socket.send(JSON.stringify({
                        type: "playlist_duration_response",
                        request_id: packet.request_id,
                        playlist_id: packet.playlist_id,
                        duration_type: packet.duration_type,
                        duration: 0 // Placeholder - web doesn't preload audio metadata
                    }));
                }
                break;

            case "pong":
                // Simplified ping without UI
                if (this.pingStart) {
                    const latency = Date.now() - this.pingStart;
                    this.speak_l("main-ping-result", { value: latency });
                    this.play_sound("pingstop.ogg");
                    this.pingStart = null;
                }
                break;



            case "table_create":
                this.play_sound("notify.ogg");
                this.speak_l("table-created-notify");
                break;
        }
    }

    applyMenuLayout(packet) {
        const hasGridEnabled = Object.prototype.hasOwnProperty.call(packet, "grid_enabled");
        const hasGridWidth = Object.prototype.hasOwnProperty.call(packet, "grid_width");
        const gridEnabled = hasGridEnabled
            ? !!packet.grid_enabled
            : this.menuArea.classList.contains('grid-mode');
        const gridWidth = hasGridWidth
            ? Math.max(1, parseInt(packet.grid_width, 10) || 1)
            : Math.max(1, parseInt(this.menuArea.dataset.gridWidth || "1", 10));
        const menuWrapper = this.menuArea.closest('.tab-content');

        this.menuArea.classList.toggle('grid-mode', gridEnabled);
        this.menuArea.dataset.gridWidth = String(gridWidth);
        if (menuWrapper) {
            menuWrapper.classList.toggle('grid-layout-active', gridEnabled && gridWidth > 1);
        }

        if (gridEnabled && gridWidth > 1) {
            this.menuArea.style.gridTemplateColumns = `repeat(${gridWidth}, minmax(var(--grid-cell-min-width), 1fr))`;
        } else {
            this.menuArea.style.gridTemplateColumns = '';
        }
    }

    renderMenu(packet) {
        // User Requirement: Switch to Menu tab on update, UNLESS in Chat
        if (this.activeTab !== 'content-chat') {
            this.switchTab('content-menu');
        }

        let newItems = packet.items || [];
        const isSameMenu = this.currentMenuId === packet.menu_id;

        // WEB-SPECIFIC: Filter out Special Buttons FIRST
        const specialIds = {
            "web_actions_menu": { container: document.getElementById('web-actions-container'), cls: "web-action-btn" },
            "web_leave_table": { container: document.getElementById('web-leave-container'), cls: "web-leave-btn danger-btn" }
        };

        // WEB-SPECIFIC: Voice Selection Menu Interception
        if (packet.menu_id === "voice_selection_menu") {
            const voices = window.speechSynthesis.getVoices();
            newItems = voices.map(voice => ({
                text: voice.name + (voice.default ? " (Default)" : ""),
                id: voice.voiceURI // Use URI as ID
            }));
            newItems.push({ text: Localization.get("back"), id: "back" });

            // If no voices found (async load issue?), show specific message
            if (voices.length === 0) {
                newItems = [{ text: Localization.get("no-voices-found"), id: "back" }];
            }
        }

        const webButtons = {};
        newItems = newItems.filter(item => {
            const id = (typeof item === 'string') ? null : item.id;
            if (id && specialIds[id]) {
                webButtons[id] = item;
                return false; // Remove from main list
            }
            return true;
        });

        this.applyMenuLayout(packet);

        // Always Update Web Buttons
        for (const [id, config] of Object.entries(specialIds)) {
            if (!config.container) continue;

            const item = webButtons[id];
            if (item) {
                config.container.innerHTML = "";
                const newBtn = document.createElement('div');
                newBtn.innerText = item.text || item.id;
                newBtn.className = config.cls;
                newBtn.tabIndex = 0; // Make focusable

                // Simulate button click behavior for div
                newBtn.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        if (newBtn.onclick) newBtn.onclick(e);
                    }
                });

                newBtn.onclick = () => {
                    this.play_sound("menuclick.ogg");
                    this.sendMenuSelection(packet.menu_id, 0, id);
                };
                config.container.appendChild(newBtn);
            } else if (!isSameMenu && id === "web_actions_menu") {
                // Only clear actions container on menu change (transient).
                // Leave button persists — cleared only on disconnect/screen transition.
                config.container.innerHTML = "";
            }
        }

        // Full rebuild if menu_id changed or empty or if we have no children yet
        if (!isSameMenu || !this.menuArea.children.length) {
            this.currentMenuId = packet.menu_id;
            this.menuArea.innerHTML = "";

            // Set title if provided
            const titleRaw = packet.menu_id ? packet.menu_id.replace('_', ' ').toUpperCase() : "MENU";
            document.getElementById('game-title').innerText = packet.title || titleRaw;
            // User requested NOT to announce menu titles
            // this.speak(packet.title || titleRaw);

            newItems.forEach((item, index) => {
                this.createMenuItem(item, index);
            });

            // WEB-SPECIFIC LOGIC MOVED TO TOP OF FUNCTION

            if (newItems.length > 0) {
                // FIXED: Only auto-focus first button if user is ALREADY in the menu tab.
                // Otherwise, this steals focus from Chat/Input fields!
                if (this.activeTab === 'content-menu') {
                    const firstBtn = this.menuArea.querySelector('.menu-item');
                    if (firstBtn) firstBtn.focus();
                }
            }

            return;
        }

        // --- Diffing Logic (Same Menu ID) ---
        const buttons = Array.from(this.menuArea.children).filter(el => el.classList.contains('menu-item'));

        // 1. Update existing or append new
        for (let i = 0; i < newItems.length; i++) {
            const newItem = newItems[i];

            if (i < buttons.length) {
                // Update existing button
                const btn = buttons[i];
                const text = typeof newItem === 'string' ? newItem : (newItem.text || "");
                const id = typeof newItem === 'string' ? null : newItem.id;

                if (btn.innerText !== text) {
                    btn.innerText = text;
                }

                if (id) {
                    btn.dataset.id = id;
                    btn.onclick = (e) => {
                        if (e && e.shiftKey) return;
                        this.sendMenuSelection(this.currentMenuId, i + 1, id);
                    };
                    // Update Context Menu handler
                    btn.oncontextmenu = (e) => {
                        e.preventDefault();
                        this.sendKeybind("shift+enter", id, { shift: true });
                        this.play_sound("menuclick.ogg");
                    };
                    this.enableLongPress(btn, id);
                } else {
                    btn.removeAttribute('dataset-id');
                    btn.onclick = () => {
                        this.sendMenuSelection(this.currentMenuId, i + 1);
                    };
                    btn.oncontextmenu = null;
                    this.disableLongPress(btn);
                }
            } else {
                // Append new item
                this.createMenuItem(newItem, i);
            }
        }

        // 2. Remove extra items
        while (buttons.length > newItems.length) {
            const btn = buttons.pop();
            if (btn && btn.parentNode) {
                btn.parentNode.removeChild(btn);
            }
        }
    }

    createMenuItem(item, index) {
        const btn = document.createElement('div');
        btn.className = "menu-item";

        let text = "";
        let id = null;

        if (typeof item === 'string') {
            text = item;
        } else {
            text = item.text;
            id = item.id;
        }

        btn.innerText = text;
        btn.tabIndex = 0; // Always make focusable so screen readers can navigate read-only items

        if (id) {
            btn.dataset.id = id;

            // Simulate button click behavior for div
            btn.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault(); // prevent scrolling with space
                    // Emulate the shift+enter context menu behavior if shift is held
                    if (e.shiftKey && e.key === 'Enter') {
                        if (btn.oncontextmenu) btn.oncontextmenu(e);
                    } else if (btn.onclick) {
                        btn.onclick(e);
                    }
                }
            });

            btn.onclick = (e) => {
                if (e && e.shiftKey) return; // Prevent click if Shift is held (Shift+Enter)
                this.sendMenuSelection(this.currentMenuId, index + 1, id);
            };

            // Use Context Menu (Right Click or Shift+F10) for Discard
            // Use property assignment to prevent listener stacking on reuse
            btn.oncontextmenu = (e) => {
                e.preventDefault();
                if (!id) return;
                this.sendKeybind("shift+enter", id, { shift: true });
                this.play_sound("menuclick.ogg");
            };

            this.enableLongPress(btn, id);
        } else {
            btn.setAttribute('aria-disabled', 'true');
        }

        this.menuArea.appendChild(btn);
    }

    enableLongPress(btn, id) {
        const LONG_PRESS_DURATION = 800; // ms

        // Clean up any existing timer
        if (btn._pressTimer) {
            clearTimeout(btn._pressTimer);
            btn._pressTimer = null;
        }

        const startPress = (e) => {
            // Only left click or touch
            if (e.type === 'mousedown' && e.button !== 0) return;

            // Clean up any existing timer (safety)
            if (btn._pressTimer) clearTimeout(btn._pressTimer);

            btn._pressTimer = setTimeout(() => {
                this.play_sound("menuclick.ogg"); // Feedback
                if (navigator.vibrate) navigator.vibrate(50); // Haptic feedback
                this.sendKeybind("shift+enter", id, { shift: true }); // Send "shift+enter" keybind
                btn._pressTimer = null;
            }, LONG_PRESS_DURATION);
        };

        const cancelPress = () => {
            if (btn._pressTimer) {
                clearTimeout(btn._pressTimer);
                btn._pressTimer = null;
            }
        };

        // Use on-properties to ensure immediate replacement when button is recycled
        btn.onmousedown = startPress;
        btn.ontouchstart = (e) => {
            // Passive listener behavior is default for on* properties usually
            startPress(e);
        };

        btn.onmouseup = cancelPress;
        btn.onmouseleave = cancelPress;
        btn.ontouchend = cancelPress;
        btn.ontouchmove = cancelPress; // Cancel if the user scrolls
    }

    disableLongPress(btn) {
        if (btn._pressTimer) {
            clearTimeout(btn._pressTimer);
            btn._pressTimer = null;
        }
        btn.onmousedown = null;
        btn.ontouchstart = null;
        btn.onmouseup = null;
        btn.onmouseleave = null;
        btn.ontouchend = null;
        btn.ontouchmove = null;
    }

    sendKeybind(key, targetId, modifiers = {}) {
        if (!this.isConnected) return;

        const packet = {
            type: "keybind",
            key: key,
            menu_item_id: targetId,
            shift: modifiers.shift || false,
            control: modifiers.control || false,
            alt: modifiers.alt || false
        };
        this.socket.send(JSON.stringify(packet));
        console.log("Sent Keybind:", packet);
    }

    handleGlobalKeyDown(e) {

        if (e.key === 'F1' && e.ctrlKey) {
            // Ctrl+F1: Game rules — send as keybind to server
            e.preventDefault();
            this.sendKeybind("f1", null, { control: true });
        } else if (e.key === 'F1') {
            // F1 for Ping (Parity)
            e.preventDefault();
            this.sendPing();
        }
    }


    sendPing() {
        if (!this.isConnected || !this.socket) return;
        this.pingStart = Date.now();
        this.socket.send(JSON.stringify({ type: "ping" }));
        this.play_sound("ping.ogg"); // Assuming ping.ogg exists or use a default
    }

    showLocalAuthError(reasonKey, targetMsg = null, { goToLogin = false } = {}) {
        const message = Localization.get(reasonKey) || Localization.get("common-error");

        this.shouldReconnect = false;
        this.manualDisconnect = true;
        this.finishConnectionAttempt();

        if (goToLogin) {
            this.showLogin();
            targetMsg = this.statusMsg;
        }

        if (targetMsg) {
            targetMsg.innerText = message;
        }

        this.speak(message);
        return message;
    }

    setSavedSessionPlayDisabled(disabled) {
        const playNowBtn = document.getElementById('btn-play-now');
        if (!playNowBtn) return;
        playNowBtn.disabled = disabled;
        playNowBtn.setAttribute('aria-disabled', disabled ? 'true' : 'false');
    }

    beginConnectionAttempt(targetMsg) {
        if (this.connectionAttemptInProgress) {
            return false;
        }

        this.connectionAttemptInProgress = true;
        this.setSavedSessionPlayDisabled(true);

        if (this.connectionAttemptTimer) {
            clearTimeout(this.connectionAttemptTimer);
        }

        this.connectionAttemptTimer = setTimeout(() => {
            if (!this.connectionAttemptInProgress || this.isConnected) {
                return;
            }

            const timeoutMessage = Localization.get("status-connection-error");
            this.shouldReconnect = false;
            this.manualDisconnect = true;
            this.disconnectReason = timeoutMessage;

            if (targetMsg) {
                targetMsg.innerText = timeoutMessage;
            }

            if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
                this.socket.close();
            } else {
                this.finishConnectionAttempt();
                this.speak(timeoutMessage);
            }
        }, 10000);

        return true;
    }

    finishConnectionAttempt() {
        this.connectionAttemptInProgress = false;
        if (this.connectionAttemptTimer) {
            clearTimeout(this.connectionAttemptTimer);
            this.connectionAttemptTimer = null;
        }
        this.setSavedSessionPlayDisabled(false);
    }

    async connect(serverUrl, username, password) {
        const targetMsg = this.isRegistering ? this.regStatusMsg : this.statusMsg;
        if (!this.beginConnectionAttempt(targetMsg)) {
            return;
        }
        targetMsg.innerText = Localization.get('status-connecting');

        // Store credentials for reconnect
        this.lastUrl = serverUrl;
        this.lastUser = username;
        this.lastPass = password;

        this.shouldReconnect = true; // Default to allowing reconnects

        if (!serverUrl.startsWith('ws://') && !serverUrl.startsWith('wss://')) {
            targetMsg.innerText = Localization.get('status-invalid-url');
            this.finishConnectionAttempt();
            return;
        }

        // Get CAPTCHA token before connecting (skipped when key is empty)
        const captchaAction = this.isRegistering ? "register" : "login";
        const captchaResult = await getCaptchaTokenResult(captchaAction);
        if (!captchaResult.ok) {
            this.showLocalAuthError(captchaResult.reason, targetMsg, {
                goToLogin: !this.isRegistering
            });
            return;
        }
        const captchaToken = captchaResult.token;

        if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
            this.socket.close();
        }

        try {
            this.socket = new WebSocket(serverUrl);

            this.socket.onopen = () => {
                console.log("Connected to server");
                this.reconnectAttempts = 0; // Reset reconnect counter

                if (this.isRegistering) {
                    this.regStatusMsg.innerText = Localization.get("status-sending-registration");
                    const pkt = {
                        type: "register",
                        username: username,
                        password: password,
                        email: document.getElementById('reg-email').value.trim() || "",
                        locale: Localization.locale,
                        client: "web"
                    };
                    if (captchaToken) pkt.captcha_token = captchaToken;
                    this.socket.send(JSON.stringify(pkt));
                } else {
                    this.statusMsg.innerText = Localization.get("status-authenticating");
                    const pkt = {
                        type: "authorize",
                        username: username,
                        password: password,
                        version: CLIENT_VERSION,
                        client: "web"
                    };
                    if (captchaToken) pkt.captcha_token = captchaToken;
                    this.socket.send(JSON.stringify(pkt));
                }
            };

            this.socket.onmessage = (event) => {
                try {
                    const packet = JSON.parse(event.data);
                    this.handlePacket(packet);
                } catch (err) {
                    console.error("Invalid packet:", err);
                }
            };

            this.socket.onclose = (event) => {
                console.log("Disconnected", event);
                this.isConnected = false;
                this.finishConnectionAttempt();
                const connStatus = document.getElementById('connection-status');
                if (connStatus) {
                    connStatus.innerText = Localization.get('status-disconnected');
                    setTimeout(() => {
                        connStatus.innerText = "";
                    }, 3000);
                }

                if (this.isRegistering) {
                    // Stay on register screen
                    const reason = Localization.get("status-disconnected");
                    if (this.regStatusMsg) this.regStatusMsg.innerText = reason;
                } else {
                    // Only go back to login if it was a clean exit or manual logout

                    // We now prioritize shouldReconnect flag over error codes
                    if (this.shouldReconnect && !this.manualDisconnect) {
                        this.cleanupAndReconnect();
                    } else {
                        this.showLogin();
                        const reason = this.disconnectReason || Localization.get("status-disconnected");
                        if (this.statusMsg) {
                            this.statusMsg.innerText = reason;
                            // Feature: Auto-clear status after 3 seconds to avoid cluttering screen reader navigation
                            setTimeout(() => {
                                if (this.statusMsg) this.statusMsg.innerText = "";
                            }, 3000);
                        }

                        // Always speak the reason if it's a significant disconnect
                        if (reason) this.speak(reason);
                        this.disconnectReason = null;
                    }
                }

                // Clear active playbacks
                this.stop_music();
                this.stop_ambience();

                // Stop TTS keep-alive interval and clear any pending watchdog
                this.stopTTSKeepAlive();
                if (this.ttsTimeout) {
                    clearTimeout(this.ttsTimeout);
                    this.ttsTimeout = null;
                }
                // Flush stale TTS queue so old speech doesn't replay after reconnect
                this.ttsQueue = [];
                this.isTTSPlaying = false;
                if (window.speechSynthesis) window.speechSynthesis.cancel();
            };

            this.socket.onerror = (err) => {
                console.error("WebSocket Error:", err);
                const targetMsg = this.isRegistering ? this.regStatusMsg : this.statusMsg;
                if (targetMsg) targetMsg.innerText = Localization.get("status-connection-error");
            };

        } catch (err) {
            const targetMsg = this.isRegistering ? this.regStatusMsg : this.statusMsg;
            if (targetMsg) targetMsg.innerText = Localization.get("status-invalid-url");
            this.finishConnectionAttempt();
        }
    }

    cleanupAndReconnect() {
        if (this.reconnectTimer) clearTimeout(this.reconnectTimer);

        const MAX_RETRIES = 5;
        this.reconnectAttempts = (this.reconnectAttempts || 0) + 1;

        if (this.reconnectAttempts > MAX_RETRIES) {
            this.showLogin();
            this.speak(Localization.get("status-connection-error"));
            if (this.statusMsg) this.statusMsg.innerText = Localization.get("status-connection-error");
            return;
        }

        const delay = Math.min(30000, 1000 * Math.pow(2, this.reconnectAttempts - 1));
        this.speak_l("main-reconnecting-in-3s", { seconds: delay / 1000 }); // Reuse key or generic

        console.log(`Reconnecting in ${delay}ms... (Attempt ${this.reconnectAttempts})`);

        this.reconnectTimer = setTimeout(() => {
            if (this.lastUrl && this.lastUser) {
                this.connect(this.lastUrl, this.lastUser, this.lastPass);
            }
        }, delay);
    }


    setMusicVolume(vol) {
        this.musicVolume = vol;
        this.soundManager.setVolume('music', vol);
        this.saveConfig();
    }

    setSoundVolume(vol) {
        this.soundVolume = vol;
        this.soundManager.setVolume('sound', vol);
        this.saveConfig();
    }

    setAmbienceVolume(vol) {
        this.ambienceVolume = vol;
        this.soundManager.setVolume('ambience', vol);
        this.saveConfig();
    }

    showInput(packet) {
        this.switchTab('content-menu');

        this.menuArea.innerHTML = "";
        const promptText = Localization.get(packet.prompt);
        document.getElementById('game-title').innerText = promptText;
        // Do not speak prompt - it adds to history. Use aria-label instead.

        const wrapper = document.createElement('div');
        wrapper.className = "input-wrapper";

        const input = document.createElement(packet.multiline ? 'textarea' : 'input');
        input.value = packet.default_value || "";
        if (packet.read_only) input.readOnly = true;
        if (packet.max_length) input.maxLength = packet.max_length;
        input.setAttribute('aria-label', promptText);
        // Ensure iOS Safari allows keyboard focus without extra taps
        input.style.webkitUserSelect = 'text';
        input.style.userSelect = 'text';
        input.setAttribute('inputmode', packet.multiline ? 'text' : 'text');

        const submitBtn = document.createElement('button');
        submitBtn.innerText = Localization.get("input-submit");
        submitBtn.className = "primary-btn";
        submitBtn.style.marginTop = "10px";

        // Enable Enter key to submit
        input.onkeydown = (e) => {
            if (e.key === 'Enter' && !packet.multiline) {
                e.preventDefault();
                submitBtn.click();
            }
        };

        submitBtn.onclick = () => {
            const value = input.value;
            console.log(`Submitting Input: ${value}, ID: ${packet.input_id}`);

            // Client-side instant update for options
            if (packet.input_id) {
                if (packet.input_id.includes("music") && packet.input_id.includes("volume")) {
                    const vol = parseInt(value) / 100;
                    if (!isNaN(vol)) this.setMusicVolume(vol);
                } else if (packet.input_id.includes("ambience") && packet.input_id.includes("volume")) {
                    const vol = parseInt(value) / 100;
                    if (!isNaN(vol)) this.setAmbienceVolume(vol);
                } else if (packet.input_id.includes("sound") && packet.input_id.includes("volume")) {
                    const vol = parseInt(value) / 100;
                    if (!isNaN(vol)) this.setSoundVolume(vol);
                }
            }

            this.socket.send(JSON.stringify({
                type: "editbox",
                value: value,      // Keep for legacy/robustness
                text: value,       // REQUIRED by server/game_utils/event_handling_mixin.py
                input_id: packet.input_id
            }));

            // Clear UI immediately - server will send new menu packet
            this.menuArea.innerHTML = "";
        };

        wrapper.appendChild(input);
        wrapper.appendChild(document.createElement('br'));
        wrapper.appendChild(submitBtn);
        this.menuArea.appendChild(wrapper);

        // iOS Safari requires a short delay before focus/select to reliably
        // present the virtual keyboard on the first tap.
        setTimeout(() => {
            input.focus();
            input.select();
        }, 50);
    }

    sendMenuSelection(menu_id, selection, selection_id = null) {
        if (!this.isConnected) return;

        console.log(`Sending Menu Selection: ID=${menu_id}, Seq=${selection}, ItemID=${selection_id}`);

        const packet = {
            type: "menu",
            menu_id: menu_id,
            selection: selection
        };

        if (selection_id) {
            packet.selection_id = selection_id;
        }

        this.socket.send(JSON.stringify(packet));
        this.play_sound("menuclick.ogg");
    }

    // --- UI Navigation ---
    initLanding() {
        this.landingScreen = document.getElementById('landing-screen');
        this.loginScreen = document.getElementById('login-screen');
        this.registerScreen = document.getElementById('register-screen');
        this.gameScreen = document.getElementById('game-screen');
        this.setActiveScreen("landing");

        // Load Auto-login capability.
        // When "Remember Me" was checked, pa_remember='1' and pa_pass live in localStorage.
        // Otherwise password lives in sessionStorage only (cleared on browser close).
        const storedUser = localStorage.getItem('pa_user');
        const remember = localStorage.getItem('pa_remember') === '1';
        const storedPass = remember
            ? localStorage.getItem('pa_pass')
            : sessionStorage.getItem('pa_pass');

        if (storedUser && storedPass) {
            this.lastUser = storedUser;
            this.lastPass = storedPass;

            // Show Saved Session
            document.getElementById('landing-actions').classList.add('hidden');
            document.getElementById('saved-session-view').classList.remove('hidden');

            // Update "Logged in as" text
            // We need to wait for Localization to load? 
            // Better: updateUIText will handle it, but we need to set the variable.
            this.autoLoginUser = storedUser;
        } else {
            document.getElementById('landing-actions').classList.remove('hidden');
            document.getElementById('saved-session-view').classList.add('hidden');
        }

        // Set initial language from browser or previous save
        const savedLang = localStorage.getItem('pa_lang');
        const browserLang = navigator.language.startsWith('vi') ? 'vi' : 'en';
        const targetLang = savedLang || browserLang;

        this.setLanguage(targetLang);
        this.updateCaptchaForScreen("landing");
    }

    setLanguage(lang) {
        Localization.load(lang).then(() => {
            localStorage.setItem('pa_lang', lang);
            this.updateUIText();
        });
    }

    setActiveScreen(screenName) {
        document.body?.classList.toggle('game-active', screenName === "game");
        if (document.body) {
            document.body.dataset.screen = screenName;
        }
    }

    updateCaptchaForScreen(screenName) {
        const isAuthScreen = ["login", "register", "forgot_password", "reset_password"].includes(screenName);
        const shouldShowCaptcha = isAuthScreen && !!RECAPTCHA_SITE_KEY;
        setRecaptchaVisibility(shouldShowCaptcha);

        if (shouldShowCaptcha) {
            ensureRecaptchaReady().catch((err) => {
                console.warn("reCAPTCHA preload failed:", err);
            });
        }
    }

    showLanding() {
        this.updateCaptchaForScreen("landing");
        this.setActiveScreen("landing");
        this.landingScreen.classList.remove('hidden');
        this.loginScreen.classList.add('hidden');
        this.registerScreen.classList.add('hidden');
        this.forgotPasswordScreen.classList.add('hidden');
        this.resetPasswordScreen.classList.add('hidden');
        this.gameScreen.classList.add('hidden');

        // Re-check auto-login state — require both user and a retrievable password
        const storedUser = localStorage.getItem('pa_user');
        const _remember = localStorage.getItem('pa_remember') === '1';
        const _storedPass = _remember
            ? localStorage.getItem('pa_pass')
            : sessionStorage.getItem('pa_pass');
        if (storedUser && _storedPass) {
            document.getElementById('landing-actions').classList.add('hidden');
            document.getElementById('saved-session-view').classList.remove('hidden');
        } else {
            document.getElementById('landing-actions').classList.remove('hidden');
            document.getElementById('saved-session-view').classList.add('hidden');
        }
    }

    showLogin() {
        this.updateCaptchaForScreen("login");
        this.setActiveScreen("login");
        this.landingScreen.classList.add('hidden');
        this.loginScreen.classList.remove('hidden');
        this.registerScreen.classList.add('hidden');
        this.forgotPasswordScreen.classList.add('hidden');
        this.resetPasswordScreen.classList.add('hidden');
        this.gameScreen.classList.add('hidden');

        // Clear persistent web buttons on disconnect/logout
        const leaveContainer = document.getElementById('web-leave-container');
        if (leaveContainer) leaveContainer.innerHTML = "";
        const actionsContainer = document.getElementById('web-actions-container');
        if (actionsContainer) actionsContainer.innerHTML = "";

        // Reset registration flag to ensure we don't accidentally register again
        this.isRegistering = false;
        if (this.regStatusMsg) this.regStatusMsg.innerText = "";
        if (this.statusMsg) this.statusMsg.innerText = "";


        // Restore "Remember Me" checkbox from the stored preference
        const chkAutoLogin = document.getElementById('chk-auto-login');
        if (chkAutoLogin) {
            chkAutoLogin.checked = localStorage.getItem('pa_remember') === '1';
        }

        // Safety: Stop any pending reconnects if user manually returning to login
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        // Safety: Disconnect any existing registration/game connection cleanly
        if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
            this.manualDisconnect = true; // Prevent auto-reconnect in onclose
            this.socket.close();
        }
    }

    showRegister() {
        this.updateCaptchaForScreen("register");
        this.setActiveScreen("register");
        this.landingScreen.classList.add('hidden');
        this.loginScreen.classList.add('hidden');
        this.registerScreen.classList.remove('hidden');
        this.forgotPasswordScreen.classList.add('hidden');
        this.resetPasswordScreen.classList.add('hidden');
        this.gameScreen.classList.add('hidden');
    }

    showForgotPassword() {
        this.updateCaptchaForScreen("forgot_password");
        this.setActiveScreen("forgot_password");
        this.landingScreen.classList.add('hidden');
        this.loginScreen.classList.add('hidden');
        this.registerScreen.classList.add('hidden');
        this.resetPasswordScreen.classList.add('hidden');
        this.gameScreen.classList.add('hidden');
        this.forgotPasswordScreen.classList.remove('hidden');

        if (this.forgotStatusMsg) this.forgotStatusMsg.innerText = "";
    }

    showResetPassword() {
        this.updateCaptchaForScreen("reset_password");
        this.setActiveScreen("reset_password");
        this.landingScreen.classList.add('hidden');
        this.loginScreen.classList.add('hidden');
        this.registerScreen.classList.add('hidden');
        this.forgotPasswordScreen.classList.add('hidden');
        this.gameScreen.classList.add('hidden');
        this.resetPasswordScreen.classList.remove('hidden');

        if (this.resetStatusMsg) this.resetStatusMsg.innerText = "";
    }

    showGame() {
        this.updateCaptchaForScreen("game");
        this.setActiveScreen("game");
        this.landingScreen.classList.add('hidden');
        this.loginScreen.classList.add('hidden');
        this.registerScreen.classList.add('hidden');
        this.forgotPasswordScreen.classList.add('hidden');
        this.resetPasswordScreen.classList.add('hidden');
        this.gameScreen.classList.remove('hidden');
    }

    // --- Actions ---

    connectToGame() {
        const serverUrl = document.getElementById('server-url').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const autoLogin = document.getElementById('chk-auto-login').checked;

        if (!username || !password) {
            alert(Localization.get("login-error-account-not-found")); // Reuse key or generic
            return;
        }

        if (autoLogin) {
            // Explicit opt-in: persist credentials across browser sessions
            localStorage.setItem('pa_user', username);
            localStorage.setItem('pa_pass', password);
            localStorage.setItem('pa_remember', '1');
        } else {
            // No persistent remember: clear any stored password and use session only
            localStorage.removeItem('pa_pass');
            localStorage.removeItem('pa_remember');
            sessionStorage.setItem('pa_pass', password);
        }

        this.connect(serverUrl, username, password);
    }

    autoLoginConnection() {
        const storedUser = localStorage.getItem('pa_user');
        const remember = localStorage.getItem('pa_remember') === '1';
        const storedPass = remember
            ? localStorage.getItem('pa_pass')
            : sessionStorage.getItem('pa_pass');
        // Retrieve loaded URL from input (restored by loadConfig)
        const serverUrl = document.getElementById('server-url').value || "wss://playaural.ddt.one:443";

        console.log(`Auto-login: user=${storedUser}, pass exists=${!!storedPass}, url=${serverUrl}`);

        if (storedUser && storedPass) {
            this.connect(serverUrl, storedUser, storedPass);
        } else {
            console.log("Auto-login failed: missing credentials");
            this.showLogin();
        }
    }

    async requestPasswordReset() {
        const serverUrl = document.getElementById('server-url').value || "wss://playaural.ddt.one:443";
        const email = document.getElementById('forgot-email').value;

        if (!email || email.trim() === "") {
            alert(Localization.get("reg-error-email") || "Email is required.");
            return;
        }

        const captchaResult = await getCaptchaTokenResult("request_password_reset");
        if (!captchaResult.ok) {
            this.showLocalAuthError(captchaResult.reason, this.forgotStatusMsg);
            return;
        }
        const captchaToken = captchaResult.token;

        this.isRegistering = true; // Use this flag to avoid auto-login behavior on close
        this.forgotStatusMsg.innerText = Localization.get('status-connecting');

        // We temporarily connect just to send this packet
        if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
            this.socket.close();
        }

        try {
            this.socket = new WebSocket(serverUrl);
            this.socket.onopen = () => {
                this.forgotStatusMsg.innerText = "Sending request...";
                this.socket.send(JSON.stringify({
                    type: "request_password_reset",
                    email: email,
                    locale: Localization.locale,
                    client: "web",
                    captcha_token: captchaToken
                }));
            };
            this.socket.onmessage = (event) => {
                try {
                    const packet = JSON.parse(event.data);
                    if (packet.type === "request_password_reset_response") {
                        if (packet.status === "success") {
                            this.forgotStatusMsg.innerText = packet.text || "Success";
                            this.speak(packet.text || "Success");

                            // Save email for next step
                            this.resetEmail = email;

                            setTimeout(() => {
                                this.showResetPassword();
                            }, 1500);
                        } else {
                            const errMsg = packet.text || "Error";
                            this.forgotStatusMsg.innerText = errMsg;
                            this.speak(errMsg);
                        }
                        this.socket.close();
                    }
                } catch (err) {}
            };
            this.socket.onclose = () => {};
            this.socket.onerror = () => {
                this.forgotStatusMsg.innerText = Localization.get("status-connection-error");
            };
        } catch (e) {
            this.forgotStatusMsg.innerText = Localization.get("status-invalid-url");
        }
    }

    async submitResetCode() {
        const serverUrl = document.getElementById('server-url').value || "wss://playaural.ddt.one:443";
        const email = this.resetEmail || document.getElementById('forgot-email').value;
        const code = document.getElementById('reset-code').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-new-password').value;

        if (!code || !newPassword) {
            alert("Code and New Password are required.");
            return;
        }

        const hasLetters = /[a-zA-Z]/.test(newPassword);
        const hasNumbers = /[0-9]/.test(newPassword);
        if (newPassword.length < 8 || !hasLetters || !hasNumbers) {
            alert(Localization.get("auth-error-password-weak") || "Password too weak.");
            return;
        }

        if (newPassword !== confirmPassword) {
            alert(Localization.get("reg-error-password-match") || "Passwords do not match.");
            return;
        }

        const captchaResult = await getCaptchaTokenResult("submit_reset_code");
        if (!captchaResult.ok) {
            this.showLocalAuthError(captchaResult.reason, this.resetStatusMsg);
            return;
        }
        const captchaToken = captchaResult.token;

        this.isRegistering = true;
        this.resetStatusMsg.innerText = Localization.get('status-connecting');

        if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
            this.socket.close();
        }

        try {
            this.socket = new WebSocket(serverUrl);
            this.socket.onopen = () => {
                this.resetStatusMsg.innerText = "Verifying...";
                this.socket.send(JSON.stringify({
                    type: "submit_reset_code",
                    email: email,
                    code: code,
                    new_password: newPassword,
                    locale: Localization.locale,
                    client: "web",
                    captcha_token: captchaToken
                }));
            };
            this.socket.onmessage = (event) => {
                try {
                    const packet = JSON.parse(event.data);
                    if (packet.type === "submit_reset_code_response") {
                        if (packet.status === "success") {
                            this.resetStatusMsg.innerText = packet.text || "Success";
                            this.speak(packet.text || "Success");

                            setTimeout(() => {
                                this.showLogin();
                                if (packet.username) {
                                    document.getElementById('username').value = packet.username;
                                }
                                document.getElementById('password').value = newPassword;
                            }, 2000);
                        } else {
                            const errMsg = packet.text || "Error";
                            this.resetStatusMsg.innerText = errMsg;
                            this.speak(errMsg);
                        }
                        this.socket.close();
                    }
                } catch (err) {}
            };
            this.socket.onclose = () => {};
            this.socket.onerror = () => {
                this.resetStatusMsg.innerText = Localization.get("status-connection-error");
            };
        } catch (e) {
            this.resetStatusMsg.innerText = Localization.get("status-invalid-url");
        }
    }

    register() {
        const serverUrl = document.getElementById('reg-server-url').value;
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;
        const confirm = document.getElementById('reg-password-confirm').value;
        const email = document.getElementById('reg-email').value;

        if (!email || email.trim() === "") {
            alert(Localization.get("reg-error-email"));
            return;
        }

        if (username.length < 3 || username.length > 30) {
            alert(Localization.get("auth-error-username-length"));
            return;
        }

        const hasLetters = /[a-zA-Z]/.test(password);
        const hasNumbers = /[0-9]/.test(password);
        if (password.length < 8 || !hasLetters || !hasNumbers) {
            alert(Localization.get("auth-error-password-weak"));
            return;
        }

        if (password !== confirm) {
            alert(Localization.get("error-password-mismatch"));
            return;
        }

        this.isRegistering = true;
        this.connect(serverUrl, username, password);
    }

    removeAccount() {
        localStorage.removeItem('pa_user');
        localStorage.removeItem('pa_pass');
        localStorage.removeItem('pa_remember');
        sessionStorage.removeItem('pa_pass');
        this.lastUser = null;
        this.lastPass = null;
        this.showLanding();
    }

    showModalMenu(packet) {
        const modal = document.getElementById('actions-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalMenuArea = document.getElementById('modal-menu-area');
        const closeBtn = document.getElementById('btn-close-modal');

        if (!modal || !modalMenuArea) return;

        // Set title
        const titleRaw = packet.menu_id ? packet.menu_id.replace(/_/g, ' ').toUpperCase() : "ACTIONS";
        modalTitle.innerText = packet.title || titleRaw;

        // Clear and populate menu
        modalMenuArea.innerHTML = "";
        const items = packet.items || [];

        items.forEach((item, index) => {
            const btn = document.createElement('button');
            btn.className = "modal-item";
            btn.innerText = (typeof item === 'string') ? item : item.text;
            
            const itemId = (typeof item === 'string') ? null : item.id;
            btn.onclick = () => {
                this.play_sound("menuclick.ogg");
                this.sendMenuSelection(packet.menu_id, index + 1, itemId);
                // Modal will close automatically on next menu/clear_ui packet
                // but we can close it immediately for better feedback
                this.closeModal();
            };
            modalMenuArea.appendChild(btn);
        });

        // Setup close button
        closeBtn.onclick = () => {
            this.sendEscape(packet.menu_id);
            this.closeModal();
        };

        // Show the modal
        if (!modal.open) {
            modal.showModal();
            // Focus first item
            const firstBtn = modalMenuArea.querySelector('button');
            if (firstBtn) firstBtn.focus();
        }
    }

    closeModal() {
        const modal = document.getElementById('actions-modal');
        if (modal && modal.open) {
            modal.close();
            // Return focus to menu area
            this.menuArea.focus();
        }
    }

    sendEscape(menuId) {
        if (!this.isConnected) return;
        this.socket.send(JSON.stringify({
            type: "escape",
            menu_id: menuId
        }));
    }

    updateUIText() {
        console.log("Updating UI Text for locale:", Localization.locale);
        document.title = Localization.get('app-title');

        // --- Landing Screen ---
        const landing = document.getElementById('landing-screen');
        if (landing) {
            landing.querySelector('#landing-title').innerText = Localization.get('landing-title');
            landing.querySelector('#intro-text').innerText = Localization.get('intro-text');
            landing.querySelector('#btn-show-login').innerText = Localization.get('btn-enter');
            landing.querySelector('#btn-show-register').innerText = Localization.get('btn-register');

            // Saved Session
            const loggedInText = Localization.get('logged-in-as', { username: this.autoLoginUser || "User" });
            landing.querySelector('#logged-in-as').innerText = loggedInText;
            landing.querySelector('#btn-play-now').innerText = Localization.get('btn-play');
            landing.querySelector('#btn-remove-account').innerText = Localization.get('btn-remove-account');

            // Footer
            landing.querySelector('#mobile-hint').innerText = Localization.get('mobile-hint');
            landing.querySelector('#windows-hint').innerText = Localization.get('windows-hint');
            landing.querySelector('#btn-download-win').innerText = Localization.get('btn-download-win');

            const installBtn = landing.querySelector('#btn-install-pwa');
            if (installBtn) installBtn.innerText = Localization.get('btn-install');
            if (installBtn && this.isStandalone()) {
                installBtn.classList.add('hidden');
            }

            // iOS Instruction
            if (this.isIOS) {
                const instr = landing.querySelector('#install-instruction');
                instr.innerText = Localization.get('install-fail-hint');
                instr.classList.remove('hidden');
            }
        }

        // --- Login Screen ---
        const loginScreen = document.getElementById('login-screen');
        if (loginScreen) {
            loginScreen.querySelector('#login-title').innerText = Localization.get('login-title');
            loginScreen.querySelector('#login-server-label').innerText = Localization.get('login-server-label');
            loginScreen.querySelector('#login-username-label').innerText = Localization.get('login-username-label');
            loginScreen.querySelector('#login-password-label').innerText = Localization.get('login-password-label');
            loginScreen.querySelector('#label-auto-login').innerText = Localization.get('label-auto-login');
            loginScreen.querySelector('#btn-login').innerText = Localization.get('login-btn');

            const btnForgot = loginScreen.querySelector('#btn-show-forgot-password');
            if (btnForgot) btnForgot.innerText = Localization.get('login-btn-forgot-password');

            if (loginScreen.querySelector('#link-no-account'))
                loginScreen.querySelector('#link-no-account').innerText = Localization.get('link-no-account');
            // Back button (hardcoded "Back" in HTML usually, or add key)
            const backBtn = loginScreen.querySelector('.text-btn');
            if (backBtn) backBtn.innerText = Localization.get('go-back') || "Back";
        }

        // --- Forgot & Reset Password Screens ---
        const forgotScreen = document.getElementById('forgot-password-screen');
        if (forgotScreen) {
            forgotScreen.querySelector('#forgot-password-title').innerText = Localization.get('login-btn-forgot-password');
            forgotScreen.querySelector('#forgot-password-prompt').innerText = Localization.get('forgot-password-prompt');
            forgotScreen.querySelector('#btn-send-reset-code').innerText = Localization.get('btn-send-code') || "Send Code";

            const backBtn = forgotScreen.querySelector('.text-btn');
            if (backBtn) backBtn.innerText = Localization.get('go-back') || "Back";
        }

        const resetScreen = document.getElementById('reset-password-screen');
        if (resetScreen) {
            resetScreen.querySelector('#reset-password-title').innerText = Localization.get('reset-password-title') || "Reset Password";
            resetScreen.querySelector('#reset-code-instructions').innerText = Localization.get('reset-code-instructions');
            resetScreen.querySelector('#reset-code-label').innerText = Localization.get('reset-code-prompt');
            resetScreen.querySelector('#new-password-label').innerText = Localization.get('new-password-prompt');
            resetScreen.querySelector('#confirm-new-password-label').innerText = Localization.get('label-confirm-password');
            resetScreen.querySelector('#btn-submit-reset').innerText = Localization.get('btn-submit-reset') || "Reset Password";

            const cancelBtn = resetScreen.querySelector('.text-btn');
            if (cancelBtn) cancelBtn.innerText = Localization.get('common-cancel') || "Cancel";
        }

        // --- Register Screen ---
        const regScreen = document.getElementById('register-screen');
        if (regScreen) {
            regScreen.querySelector('#reg-title').innerText = Localization.get('reg-title');
            regScreen.querySelector('#reg-server-label').innerText = Localization.get('reg-server-label');
            regScreen.querySelector('#reg-username-label').innerText = Localization.get('reg-username-label');
            regScreen.querySelector('#reg-password-label').innerText = Localization.get('reg-password-label');
            regScreen.querySelector('#label-confirm-password').innerText = Localization.get('label-confirm-password');
            regScreen.querySelector('#reg-email-label').innerText = Localization.get('reg-email-label');
            regScreen.querySelector('#btn-register').innerText = Localization.get('reg-register-btn');

            const gotoLoginBtn = regScreen.querySelector('#btn-goto-login');
            if (gotoLoginBtn) gotoLoginBtn.innerText = Localization.get('btn-goto-login');

            if (regScreen.querySelector('#link-have-account'))
                regScreen.querySelector('#link-have-account').innerText = Localization.get('link-have-account');

            const backBtn = regScreen.querySelector('.text-btn');
            if (backBtn) backBtn.innerText = Localization.get('go-back') || "Back";
        }

        // --- Game UI Tabs & Content ---
        const tabMenu = document.getElementById('tab-menu');
        const tabChat = document.getElementById('tab-chat');
        const tabPlayers = document.getElementById('tab-players');
        const tabHistory = document.getElementById('tab-history');

        if (tabMenu) tabMenu.innerText = Localization.get('tab-menu');
        if (tabChat) tabChat.innerText = Localization.get('tab-chat');
        if (tabPlayers) tabPlayers.innerText = Localization.get('tab-players');
        if (tabHistory) tabHistory.innerText = Localization.get('tab-history');

        // Chat section
        const chatInput = document.getElementById('chat-input');
        const chatSendBtn = document.getElementById('btn-chat-send');

        if (chatInput) {
            chatInput.placeholder = Localization.get('chat-input-placeholder');
            chatInput.setAttribute('aria-label', Localization.get('chat-input-label'));
        }
        if (chatSendBtn) chatSendBtn.innerText = Localization.get('btn-chat-send');

        const btnViewHistory = document.getElementById('btn-view-history');
        const btnBackToInput = document.getElementById('btn-back-to-input');

        if (btnViewHistory) btnViewHistory.innerText = Localization.get('btn-view-history');
        if (btnBackToInput) btnBackToInput.innerText = Localization.get('btn-back-to-input');

        // Shortcuts section
        const playersTitle = document.getElementById('players-title');
        const btnListOnline = document.getElementById('btn-list-online');
        const btnListOnlineGames = document.getElementById('btn-list-online-games');
        const btnOpenFriends = document.getElementById('btn-open-friends');
        const btnOpenOptions = document.getElementById('btn-open-options');
        const btnCheckPing = document.getElementById('btn-check-ping');
        const playersInstruction = document.getElementById('players-instruction');

        if (playersTitle) playersTitle.innerText = Localization.get('players-title');
        if (btnListOnline) btnListOnline.innerText = Localization.get('btn-list-online');
        if (btnListOnlineGames) btnListOnlineGames.innerText = Localization.get('btn-list-online-games');
        if (btnOpenFriends) btnOpenFriends.innerText = Localization.get('btn-open-friends');
        if (btnOpenOptions) btnOpenOptions.innerText = Localization.get('btn-open-options');
        if (btnCheckPing) btnCheckPing.innerText = Localization.get('btn-check-ping');
        if (playersInstruction) playersInstruction.innerText = Localization.get('players-instruction');

        // History section
        const historyTitle = document.getElementById('history-title');
        if (historyTitle) historyTitle.innerText = Localization.get('history-title');

        const connStatus = document.getElementById('connection-status');
        if (connStatus && connStatus.innerText.trim() !== "") {
            if (this.isConnected) {
                connStatus.innerText = Localization.get("status-connected");
            }
        }
    }
}

// Start app
function bootstrapGameClient() {
    window.Game = new GameClient();
    window.Game.initLanding();

    // Prevent default form submissions
    document.getElementById('login-form').onsubmit = function (e) { e.preventDefault(); Game.connectToGame(); return false; };
    document.getElementById('register-form').onsubmit = function (e) { e.preventDefault(); Game.register(); return false; };
    document.getElementById('forgot-password-form').onsubmit = function (e) { e.preventDefault(); Game.requestPasswordReset(); return false; };
    document.getElementById('reset-password-form').onsubmit = function (e) { e.preventDefault(); Game.submitResetCode(); return false; };
    document.getElementById('chat-form').onsubmit = function (e) { e.preventDefault(); Game.sendChat(); return false; };
}

bootstrapGameClient();


