# PlayAural

PlayAural is an audio-first online multiplayer gaming platform designed for blind and low-vision players, while remaining welcoming to anyone who wants accessible, speech-friendly games. It combines spoken feedback, structured sound design, multiplayer tables, and synchronized game logic across desktop, web, and mobile clients.

PlayAural is built upon the open-source foundation of [PlayPalace](https://github.com/XGDevGroup/PlayPalace11).

## Play Now

- Download the latest app builds from the repository's **Releases** page.
- Play in the browser at [play.ddt.one](https://play.ddt.one).

## Core Features

- Audio-first gameplay with TTS and sound cues for menus, turns, results, and status changes
- Online multiplayer tables with hosts, spectators, bots, scores, saves, and reconnect handling
- Desktop, web, and mobile clients using the same WebSocket game protocol
- English and Vietnamese localization across the platform, with safe English fallback for partial community translations
- Table-based real-time voice chat across the first-party clients, authorized by the game server and carried by a dedicated media service

## Platform Components

PlayAural is organized around the following components:

- `server/` - Python async WebSocket game server with authentication, tables, persistence, moderation, localization, and game rules
- `client/` - wxPython desktop client with keyboard-first screen reader UX, local sound playback, and integrated table voice chat
- `web_client/` - Modular vanilla JavaScript PWA with ARIA live announcements, desktop-style keyboard navigation, touch-friendly menus, browser audio and Web Speech support, capped history buffers, localized UI strings, and integrated table voice chat
- `mobile_client/` - Expo / React Native client with self-voicing gesture navigation, mobile audio, accessible text entry, and integrated table voice chat
- `server/voice/` and `deployment/voice/` - voice authorization logic, deployment examples, and LiveKit-oriented server configuration

## Accessibility

PlayAural is designed so the full state of the platform can be followed without depending on visuals.

- The desktop client supports keyboard-first play and screen readers.
- The web client supports browser-based play with ARIA live output, screen-reader-friendly menu focus, desktop-style shortcuts, touch controls, and browser speech or native screen-reader announcements.
- The mobile client provides self-voicing navigation and gesture-driven interaction.
- Game actions, chat, score changes, and outcomes are communicated through speech and sound.

## Game Catalog

PlayAural currently includes **43 games** across backend categories:

- Card games such as Blackjack, Crazy Eights, UNO, Exploding Kittens, Pusoy Dos, Tien Len, Scopa, Ninety Nine, Mile by Mile, Citadels, Coup, Dead Man's Deck, Dominos, Nine, 21, Cards Against Humanity, and Age of Heroes
- Poker games such as Texas Hold'em, Five Card Draw, and Dead Man's Poker
- Dice games such as Farkle, Bunko, Yahtzee, Pig, Left Center Right, Color Game, Toss Up, Tradeoff, Threes, and 1-4-24
- Board games such as Chess, Battleship, Backgammon, Senet, Sorry!, Ludo, and Snakes and Ladders
- Original arcade-style titles such as Battle, Chaos Bear, Light Turret, and Pirates of the Lost Seas
- Miscellaneous games such as Rolling Balls and Metal Pipe

The Play menu includes a persisted category filter with dynamic game counts so players can quickly narrow the catalog by genre.

## Voice Chat

PlayAural separates voice authorization from media transport.

- The game server verifies whether a player is allowed to join the current table's voice chat.
- A dedicated LiveKit-based voice service carries the real-time media stream.
- The server issues short-lived join tokens and keeps voice membership tied to table context.
- Voice presence announcements and related sounds are synchronized with the normal table lifecycle.

## Supported Languages

PlayAural currently supports the following languages:

- English (EN) - official default language, maintained by the PlayAural core team
- Vietnamese (VI) - official default language, maintained by Trung and the PlayAural core team
- Persian (FA) - community translation, maintained by Hamid Rezaei

Community translators should follow [TRANSLATING.md](TRANSLATING.md). Partial
translations are supported safely: missing strings and missing translated
documentation fall back to English rather than displaying raw translation keys.

## Repository Layout

- `server/` - server runtime, games, tests, docs, and deployment scripts
- `client/` - desktop client source, sounds, locales, and packaging assets
- `web_client/` - modular browser client source, service worker, split locale bundles, static assets, Web Audio/Web Speech handling, and table voice integration
- `mobile_client/` - Expo application, mobile locales, sounds, build configuration, and voice integration
- `deployment/` - deployment-specific configuration examples

## Web Client

The browser client is a standalone PWA served from `web_client/`.

- `game.js` defines the web client version and bootstraps the runtime.
- `app.js`, `store.js`, `network.js`, `audio.js`, `a11y.js`, and `keybinds.js` handle the client shell, WebSocket protocol, state, sound, speech, accessibility announcements, and keyboard commands.
- `ui/menus.js` and `ui/history.js` render the active game menu and message history with stable focus, touch activation, capped buffers, and coalesced updates for mobile performance.
- `locales/manifest.js`, `locales/index.js`, and the locale catalog files provide browser-client UI strings and language metadata.
- `sw.js` provides the PWA shell cache for offline startup assets.

The web client uses the same server packets as the desktop and mobile clients. It supports single-line and multiline server input requests, browser Web Speech voice selection with a default voice option, ARIA live announcements at the end of the reading order, local sound/music/ambience playback, and LiveKit table voice chat authorized by the game server.

## Open Source

PlayAural is released as open-source software. Public source code and release builds are distributed through this repository.

## License

This project is licensed under the **GNU GENERAL PUBLIC LICENSE**. See [LICENSE](LICENSE) for the full text.
