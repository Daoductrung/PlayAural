console.log("Game.js initialized.");
const CLIENT_VERSION = "0.1.4";

class Localization {
    static strings = {}; // Loaded from window.LOCALES (locales.js)
    static locale = "en";

    static async load(locale) {
        if (window.LOCALES && window.LOCALES[locale]) {
            this.strings = window.LOCALES[locale];
            this.locale = locale;
            console.log(`Loaded locale from script: ${locale}`);
            return;
        }

        // Method 2: Fetch JSON - Works for http://
        try {
            const response = await fetch(`locales/${locale}.json`);
            if (!response.ok) throw new Error(`Failed to load locale ${locale} via fetch`);
            this.strings = await response.json();
            this.locale = locale;
            console.log(`Loaded locale via fetch: ${locale}`);
        } catch (err) {
            console.warn("Localization fetch failed (normal if offline/file://):", err);

            // Fallback: If we tried to load a locale not in LOCALES and fetch failed, 
            // try falling back to 'en' from LOCALES if available
            if (window.LOCALES && window.LOCALES['en']) {
                this.strings = window.LOCALES['en'];
                console.log("Fell back to built-in English");
            } else {
                // Hard fallback (Should not be reached if locales.js is loaded)
                this.strings = {};
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
        this.currentAudio = null;

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
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
    }

    playNext() {
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
            this.client.play_music(filename, false); // looping=false because playlist handles loop
            this.currentAudio = this.client.currentMusic;
        } else {
            // Play as sound
            const path = `sounds/${filename}`;
            this.currentAudio = new Audio(path);
            this.currentAudio.volume = this.client.soundVolume;
            this.currentAudio.play().catch(e => console.warn("Playlist play error:", e));
        }

        // Setup next track callback
        if (this.currentAudio) {
            this.currentAudio.onended = () => {
                this.playNext();
            };
        }
    }
}

class GameClient {
    constructor() {
        this.socket = null;
        this.audioContext = null;
        this.isConnected = false;
        this.manualDisconnect = false;

        // UI Elements
        this.loginScreen = document.getElementById('login-screen');
        this.registerScreen = document.getElementById('register-screen');
        this.gameScreen = document.getElementById('game-screen');

        this.loginForm = document.getElementById('login-form');
        this.registerForm = document.getElementById('register-form');

        this.statusMsg = document.getElementById('login-status');
        this.regStatusMsg = document.getElementById('register-status');

        // Initialize preferences (default values matching server)
        this.preferences = {
            play_turn_sound: true,
            music_volume: 20,
            ambience_volume: 20,
            mute_global_chat: false,
            mute_table_chat: false,
            notify_table_created: true,
            play_typing_sounds: true
        };
        this.announcer = document.getElementById('announcer');
        this.menuArea = document.getElementById('menu-area');

        // Tabs
        this.tabs = document.querySelectorAll('.tab-btn');
        this.tabContents = document.querySelectorAll('.tab-content');
        this.activeTab = 'content-menu';

        // Chat & History
        this.chatHistory = document.getElementById('chat-history');
        this.historyLog = document.getElementById('history-log');
        this.chatForm = document.getElementById('chat-form');
        this.chatInput = document.getElementById('chat-input');

        // Audio Settings
        this.musicVolume = 0.2; // Default 20%
        this.soundVolume = 1.0;
        this.ambienceVolume = 0.3;

        // State
        this.currentMusic = null;
        this.currentMusicName = null;
        this.currentAmbience = null;
        this.playlists = {}; // ID -> Playlist
        this.currentAnnouncerIndex = 0; // For rotating between dual aria-live regions

        // Speech Queue System
        this.speechQueue = [];
        this.isSpeaking = false;
        this.speechDelay = 200; // 0.2 seconds delay for fast responsiveness while maintaining queue order

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

        // Players Tab
        document.getElementById('btn-list-online').onclick = () => {
            this.sendListOnline(false);
        };
        document.getElementById('btn-list-online-games').onclick = () => {
            this.sendListOnline(true);
        };

        // Table Options Removed (Used to be btn-table-options)

        // Initialize Audio Context on first interaction (Touch included)
        const initAudioOnce = () => {
            this.initAudio();
            // Remove listeners after first successful init
            if (this.audioContext && this.audioContext.state === 'running') {
                document.removeEventListener('click', initAudioOnce);
                document.removeEventListener('keydown', initAudioOnce);
                document.removeEventListener('touchstart', initAudioOnce);
            }
        };

        document.addEventListener('click', initAudioOnce);
        document.addEventListener('keydown', initAudioOnce);
        document.addEventListener('touchstart', initAudioOnce);

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

        // Detect iOS
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

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
                }
                if (config.soundVolume !== undefined) {
                    this.soundVolume = config.soundVolume;
                }
                if (config.ambienceVolume !== undefined) {
                    this.ambienceVolume = config.ambienceVolume;
                }

                // Restore preferences
                if (config.preferences) {
                    this.preferences = { ...this.preferences, ...config.preferences };
                    console.log("Restored preferences:", this.preferences);
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

        // Save Credentials if Auto-Login checked
        if (this.lastUser && this.lastPass) {
            const autoLogin = document.getElementById('chk-auto-login').checked;
            if (autoLogin) {
                localStorage.setItem('pa_user', this.lastUser);
                localStorage.setItem('pa_pass', this.lastPass);
            }
        }
    }

    initAudio() {
        if (!this.audioContext) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContext();
            console.log("Audio Context Initialized");
        }
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume().then(() => {
                console.log("Audio Context Resumed");
            }).catch(e => console.warn("Audio resume failed", e));
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
            if (c.id === 'content-history') {
                // Special handling for history: Keep it in DOM but hidden visually
                c.classList.remove('hidden'); // Ensure standard hidden is off
                c.classList.add('background-active');
            } else {
                c.classList.add('hidden');
                c.classList.remove('background-active'); // Ensure no stray class (though unlikely)
            }
        });

        // Activate target
        const activeTabBtn = document.querySelector(`.tab-btn[aria-controls="${tabId}"]`);
        const activeContent = document.getElementById(tabId);

        if (activeTabBtn && activeContent) {
            activeTabBtn.classList.add('active');
            activeTabBtn.setAttribute('aria-selected', 'true');

            if (tabId === 'content-history') {
                activeContent.classList.remove('background-active');
                activeContent.classList.remove('hidden');
                // Scroll to bottom when becoming visible
                if (this.historyLog) {
                    this.historyLog.scrollTop = this.historyLog.scrollHeight;
                }
            } else {
                activeContent.classList.remove('hidden');
            }

            this.activeTab = tabId;
        }
    }



    addToChatLog(message, sender, senderClass) {
        const container = this.chatHistory;
        const entry = document.createElement('div');
        entry.className = "log-entry";

        const time = new Date().toLocaleTimeString();
        let html = "";

        if (sender) {
            html += `<span class="log-sender ${senderClass}">${sender}:</span> `;
        }

        html += `<span class="log-msg">${message}</span>`;
        // html += ` <span class="log-time">[${time}]</span>`; // Optional time for mobile to save space? 
        // User didn't specify, but mobile screen is small. Let's keep it but small.

        entry.innerHTML = html;
        container.appendChild(entry);
        container.scrollTop = container.scrollHeight;
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
        // Try to init/resume audio context if needed
        if (!this.audioContext) {
            this.initAudio();
        }
        if (this.audioContext && this.audioContext.state === 'suspended') {
            try {
                await this.audioContext.resume();
            } catch (e) {
                console.warn("Auto-resume failed in play_sound", e);
            }
        }

        const pan = options.pan !== undefined ? options.pan : 0.0; // -1.0 to 1.0
        const pitch = options.pitch !== undefined ? options.pitch : 1.0; // 0.0 to 2.0+
        let volMultiplier = 1.0;

        if (options.volume !== undefined) {
            volMultiplier = options.volume;
        }

        const path = `sounds/${filename}`;

        // Strategy: Use Web Audio API if available (for Pitch/Pan), fallback to HTML5 Audio
        // Check if context is running AND not local file protocol (to avoid CORS)
        const isLocalFile = window.location.protocol === 'file:';

        if (this.audioContext && this.audioContext.state === 'running' && !isLocalFile) {
            try {
                // Fetch and Decode
                const response = await fetch(path);
                const arrayBuffer = await response.arrayBuffer();
                const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);

                // Create Nodes
                const source = this.audioContext.createBufferSource();
                source.buffer = audioBuffer;
                source.playbackRate.value = pitch;

                const gainNode = this.audioContext.createGain();
                gainNode.gain.value = this.soundVolume * volMultiplier;

                const panner = this.audioContext.createStereoPanner();
                panner.pan.value = Math.max(-1, Math.min(1, pan));

                // Connect
                source.connect(panner);
                panner.connect(gainNode);
                gainNode.connect(this.audioContext.destination);

                source.start(0);
                return; // Success

            } catch (e) {
                console.warn(`Web Audio API playback failed for ${path}, falling back:`, e);
            }
        }

        // Fallback: Simple Audio Element
        try {
            const audio = new Audio(path);
            audio.volume = Math.max(0, Math.min(1, this.soundVolume * volMultiplier));
            await audio.play();
        } catch (e) {
            console.error(`Fallback playback failed for ${path}:`, e);
        }
    }



    speak(text, params = {}) {
        // Debug localization params
        console.log(`Queueing Speech: ${text}`, params);

        const localized = Localization.get(text, params);
        this.speechQueue.push(localized);
        this.processSpeechQueue();
    }

    processSpeechQueue() {
        if (this.isSpeaking || this.speechQueue.length === 0) return;

        this.isSpeaking = true;
        const message = this.speechQueue.shift();

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
        // If controlled by playlist, loop might be false

        if (this.currentMusic && this.currentMusicName === filename && !this.currentMusic.paused) {
            // If existing is already playing same file
            // Update loop parameter just in case
            this.currentMusic.loop = loop;
            return;
        }

        if (this.currentMusic) {
            this.stop_music();
        }
        if (!this.audioContext || !filename) return;

        const path = `sounds/${filename}`;
        const audio = new Audio(path);
        audio.loop = loop;
        audio.volume = this.musicVolume;

        // Handle ended event for looping if not set natively (though audio.loop does it)
        // If not looping, we might need to notify playlist. 
        // Logic: Playlist sets loop=false, listens to onended.

        audio.play().catch(e => console.warn(`Failed to play music: ${path}`, e));

        this.currentMusic = audio;
        this.currentMusicName = filename;
    }

    stop_music() {
        if (this.currentMusic) {
            this.currentMusic.pause();
            this.currentMusic = null;
            this.currentMusicName = null;
        }
    }

    play_ambience(filename) {
        if (this.currentAmbience) {
            this.stop_ambience();
        }
        if (!this.audioContext || !filename) return;

        const path = `sounds/${filename}`;
        const audio = new Audio(path);
        audio.loop = true;
        audio.volume = this.ambienceVolume;
        audio.play().catch(e => console.warn(`Failed to play ambience: ${path}`, e));
        this.currentAmbience = audio;
    }

    stop_ambience() {
        if (this.currentAmbience) {
            this.currentAmbience.pause();
            this.currentAmbience = null;
        }
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

    // New method to encapsulate chat processing logic
    on_receive_chat(packet) {
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

        } else if (packet.convo === "announcement") {
            logClass = "log-channel-system";
            const prefix = Localization.get("chat-prefix-announcement") || Localization.get("system-announcement");
            displaySender = prefix;
            speakText = `${prefix}: ${packet.message}`;
            soundName = "notify.ogg";

        } else if (packet.convo === "local" || packet.convo === "table" || packet.convo === "game") {
            logClass = "log-channel-table";
            const tagKey = (packet.convo === "local") ? "chat-prefix-local" : "chat-prefix-table";
            const prefix = Localization.get(tagKey);
            displaySender = `${prefix} ${sender}`;
            speakText = `${sender}: ${packet.message}`;
            soundName = "chatlocal.ogg";

        } else {
            // Default / System messages
            const prefix = Localization.get("chat-prefix-system");
            displaySender = `${prefix} ${sender}`;
            speakText = `${packet.message}`;
        }

        if (shouldSpeak) {
            this.play_sound(soundName);
            this.speak(speakText);
        }

        this.addToChatLog(packet.message, displaySender, logClass);
    }



    handlePreferenceUpdate(packet) {
        console.log("Updating preference (RAW):", packet);

        // Merge new preferences (bulk update from authorize)
        if (packet.preferences) {
            this.preferences = { ...this.preferences, ...packet.preferences };
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
        }
        this.saveConfig();
        console.log("Current Preferences Snapshot:", JSON.stringify(this.preferences));
    }

    handlePacket(packet) {
        switch (packet.type) {
            case "login_failed":
                this.socket.close();
                const reasonKey = "auth-error-" + (packet.reason || "unknown").replace(/_/g, '-');
                const errorText = Localization.get(reasonKey) || Localization.get("login-info-failed");

                this.manualDisconnect = true;
                this.disconnectReason = errorText;
                break;

            case "register_response":
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
                this.disconnectReason = null; // Clear any previous error
                console.log("Authorized as:", packet.username);

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
                if (packet.loop) this.play_ambience(packet.loop);
                break;
            case "stop_ambience":
                this.stop_ambience();
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
                this.renderMenu({ items: [] }); // Clear menu
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
                    const tagKey = (packet.convo === "local") ? "chat-prefix-local" : "chat-prefix-table";
                    const prefix = Localization.get(tagKey);
                    displaySender = `${prefix} ${sender}`;
                    speakText = `${sender}: ${packet.message}`;
                    soundName = "chatlocal.ogg";

                    if (this.preferences.mute_table_chat === true) {
                        shouldSpeak = false;
                    } else {
                        // console.log("PLAYING: Table Chat (Not Muted)");
                    }
                } else {
                    // Default / System messages
                    const prefix = Localization.get("chat-prefix-system");
                    displaySender = `${prefix} ${sender}`;
                    speakText = `${packet.message}`;
                }

                if (shouldSpeak) {
                    this.play_sound(soundName);
                    this.speak(speakText);
                }

                this.addToChatLog(packet.message, displaySender, logClass);
                break;

            case "menu":
                this.renderMenu(packet);
                break;

            case "update_menu":
                this.renderMenu(packet);
                break;

            case "update_options_lists":
                // Store server options (game variants, etc) for potential use
                if (packet.options) {
                    this.serverOptions = packet.options;
                    console.log("Updated server options:", this.serverOptions);
                }
                break;

            case "request_input":
                this.showInput(packet);
                break;

            case "game_list":
                this.renderGameList(packet);
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

            case "stop_music":
                this.stop_music();
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

            // Removed/Simplified handlers
            // Removed/Simplified handlers
            // case "open_client_options": handled by server menu now

            case "pong":
                // Simplified ping without UI
                if (this.pingStart) {
                    const latency = Date.now() - this.pingStart;
                    this.speak_l("main-ping-result", { value: latency });
                    this.play_sound("pingstop.ogg");
                    this.pingStart = null;
                }
                break;

            case "force_exit":
                alert(packet.reason || "You have been disconnected.");
                this.socket.close();
                window.close();
                break;

            case "table_create":
                this.play_sound("notify.ogg");
                this.speak_l("table-created-notify");
                break;
        }
    }

    renderMenu(packet) {
        this.switchTab('content-menu');

        let newItems = packet.items || [];
        const isSameMenu = this.currentMenuId === packet.menu_id;

        // WEB-SPECIFIC: Filter out Special Buttons FIRST
        const specialIds = {
            "web_actions_menu": { container: document.getElementById('web-actions-container'), cls: "web-action-btn" },
            "web_leave_table": { container: document.getElementById('web-leave-container'), cls: "web-leave-btn danger-btn" }
        };

        const webButtons = {};
        newItems = newItems.filter(item => {
            const id = (typeof item === 'string') ? null : item.id;
            if (id && specialIds[id]) {
                webButtons[id] = item;
                return false; // Remove from main list
            }
            return true;
        });

        // Always Update Web Buttons
        for (const [id, config] of Object.entries(specialIds)) {
            if (!config.container) continue;

            const item = webButtons[id];
            if (item) {
                config.container.innerHTML = "";
                const newBtn = document.createElement('button');
                newBtn.innerText = item.text || item.id;
                newBtn.className = config.cls;
                newBtn.onclick = () => {
                    this.play_sound("menuclick.ogg");
                    this.sendMenuSelection(packet.menu_id, 0, id);
                };
                config.container.appendChild(newBtn);
            } else if (!isSameMenu) {
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
                const firstBtn = this.menuArea.querySelector('.menu-item');
                if (firstBtn) firstBtn.focus();
            }

            return;
        }

        // --- Diffing Logic (Same Menu ID) ---
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
        const btn = document.createElement('button');
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
        if (id) {
            btn.dataset.id = id;
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
            btn.disabled = true;
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
        btn.ontouchmove = cancelPress;
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

        // F1 for Ping (Parity)
        if (e.key === 'F1') {
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

    connect(serverUrl, username, password) {
        const targetMsg = this.isRegistering ? this.regStatusMsg : this.statusMsg;
        targetMsg.innerText = Localization.get('status-connecting');

        // Store credentials for reconnect
        this.lastUrl = serverUrl;
        this.lastUser = username;
        this.lastPass = password;

        this.shouldReconnect = true; // Default to allowing reconnects

        if (!serverUrl.startsWith('ws://') && !serverUrl.startsWith('wss://')) {
            targetMsg.innerText = Localization.get('status-invalid-url');
            return;
        }

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
                    this.socket.send(JSON.stringify({
                        type: "register",
                        username: username,
                        password: password,
                        email: document.getElementById('reg-email').value.trim() || "",
                        locale: Localization.locale
                    }));
                } else {
                    this.statusMsg.innerText = Localization.get("status-authenticating");
                    this.socket.send(JSON.stringify({
                        type: "authorize",
                        username: username,
                        password: password,
                        version: CLIENT_VERSION,
                        client: "web"
                    }));
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
            };

            this.socket.onerror = (err) => {
                console.error("WebSocket Error:", err);
                const targetMsg = this.isRegistering ? this.regStatusMsg : this.statusMsg;
                if (targetMsg) targetMsg.innerText = Localization.get("status-connection-error");
            };

        } catch (err) {
            const targetMsg = this.isRegistering ? this.regStatusMsg : this.statusMsg;
            if (targetMsg) targetMsg.innerText = Localization.get("status-invalid-url");
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
        if (this.currentMusic) {
            this.currentMusic.volume = vol;
        }
        this.saveConfig();
    }

    setSoundVolume(vol) {
        this.soundVolume = vol;
        this.saveConfig();
    }

    setAmbienceVolume(vol) {
        this.ambienceVolume = vol;
        if (this.currentAmbience) {
            this.currentAmbience.volume = vol;
        }
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
        input.setAttribute('aria-label', promptText);

        const submitBtn = document.createElement('button');
        submitBtn.innerText = Localization.get("input-submit");
        submitBtn.className = "primary-btn";
        submitBtn.style.marginTop = "10px";

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

        input.focus();
        input.select(); // Auto-select text for easy replacement
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

        // Load Auto-login capability
        const storedUser = localStorage.getItem('pa_user');
        const storedPass = localStorage.getItem('pa_pass'); // Warning: Insecure for prod, ok for proto

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
    }

    setLanguage(lang) {
        Localization.load(lang).then(() => {
            localStorage.setItem('pa_lang', lang);
            this.updateUIText();
        });
    }

    showLanding() {
        this.landingScreen.classList.remove('hidden');
        this.loginScreen.classList.add('hidden');
        this.registerScreen.classList.add('hidden');
        this.gameScreen.classList.add('hidden');

        // Re-check auto-login state
        const storedUser = localStorage.getItem('pa_user');
        if (storedUser) {
            document.getElementById('landing-actions').classList.add('hidden');
            document.getElementById('saved-session-view').classList.remove('hidden');
        } else {
            document.getElementById('landing-actions').classList.remove('hidden');
            document.getElementById('saved-session-view').classList.add('hidden');
        }
    }

    showLogin() {
        this.landingScreen.classList.add('hidden');
        this.loginScreen.classList.remove('hidden');
        this.registerScreen.classList.add('hidden');
        this.gameScreen.classList.add('hidden');

        // Reset registration flag to ensure we don't accidentally register again
        this.isRegistering = false;
        if (this.regStatusMsg) this.regStatusMsg.innerText = "";
        if (this.statusMsg) this.statusMsg.innerText = "";


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
        this.landingScreen.classList.add('hidden');
        this.loginScreen.classList.add('hidden');
        this.registerScreen.classList.remove('hidden');
        this.gameScreen.classList.add('hidden');
    }

    showGame() {
        this.landingScreen.classList.add('hidden');
        this.loginScreen.classList.add('hidden');
        this.registerScreen.classList.add('hidden');
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
            localStorage.setItem('pa_user', username);
            localStorage.setItem('pa_pass', password);
        } else {
            // Only clear ONLY if user explicitly unchecked? 
            // Or usually we don't clear unless they say "Remove Account".
            // Implementation: Update lastUser/Pass, but saving to LS only if checked.
        }

        this.connect(serverUrl, username, password);
    }

    autoLoginConnection() {
        const storedUser = localStorage.getItem('pa_user');
        const storedPass = localStorage.getItem('pa_pass');
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

    register() {
        const serverUrl = document.getElementById('reg-server-url').value;
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;
        const confirm = document.getElementById('reg-password-confirm').value;
        const email = document.getElementById('reg-email').value;

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
        this.lastUser = null;
        this.lastPass = null;
        this.showLanding();
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
            if (loginScreen.querySelector('#link-no-account'))
                loginScreen.querySelector('#link-no-account').innerText = Localization.get('link-no-account');
            // Back button (hardcoded "Back" in HTML usually, or add key)
            const backBtn = loginScreen.querySelector('.text-btn');
            if (backBtn) backBtn.innerText = Localization.get('go-back') || "Back";
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

        if (tabMenu) tabMenu.innerText = Localization.get('tab-menu');
        if (tabChat) tabChat.innerText = Localization.get('tab-chat');
        if (tabPlayers) tabPlayers.innerText = Localization.get('tab-players');

        // Chat section
        const chatInput = document.getElementById('chat-input');
        const chatSendBtn = document.getElementById('btn-chat-send');

        if (chatInput) {
            chatInput.placeholder = Localization.get('chat-input-placeholder');
            chatInput.setAttribute('aria-label', Localization.get('chat-input-label'));
        }
        if (chatSendBtn) chatSendBtn.innerText = Localization.get('btn-chat-send');

        // Players section
        const playersTitle = document.getElementById('players-title');
        const btnListOnline = document.getElementById('btn-list-online');
        const btnListOnlineGames = document.getElementById('btn-list-online-games');
        const playersInstruction = document.getElementById('players-instruction');

        if (playersTitle) playersTitle.innerText = Localization.get('players-title');
        if (btnListOnline) btnListOnline.innerText = Localization.get('btn-list-online');
        if (btnListOnlineGames) btnListOnlineGames.innerText = Localization.get('btn-list-online-games');
        if (playersInstruction) playersInstruction.innerText = Localization.get('players-instruction');

        const connStatus = document.getElementById('connection-status');
        if (connStatus && connStatus.innerText.trim() !== "") {
            if (this.isConnected) {
                connStatus.innerText = Localization.get("status-connected");
            }
        }
    }
}

// Start app
window.onload = function () {
    window.Game = new GameClient();
    window.Game.initLanding();

    // Prevent default form submissions
    document.getElementById('login-form').onsubmit = function (e) { e.preventDefault(); Game.connectToGame(); return false; };
    document.getElementById('register-form').onsubmit = function (e) { e.preventDefault(); Game.register(); return false; };
    document.getElementById('chat-form').onsubmit = function (e) { e.preventDefault(); Game.sendChat(); return false; };
};
