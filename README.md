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
- English and Vietnamese localization across the platform
- Table-based real-time voice chat across the first-party clients, authorized by the game server and carried by a dedicated media service

## Platform Components

PlayAural is organized around the following components:

- `server/` - Python async WebSocket game server with authentication, tables, persistence, moderation, localization, and game rules
- `client/` - wxPython desktop client with keyboard-first screen reader UX, local sound playback, and integrated table voice chat
- `web_client/` - Vanilla JavaScript PWA with browser TTS, touch-friendly menus, and integrated table voice chat
- `mobile_client/` - Expo / React Native client with self-voicing gesture navigation, mobile audio, accessible text entry, and integrated table voice chat
- `server/voice/` and `deployment/voice/` - voice authorization logic, deployment examples, and LiveKit-oriented server configuration

## Accessibility

PlayAural is designed so the full state of the platform can be followed without depending on visuals.

- The desktop client supports keyboard-first play and screen readers.
- The web client supports browser-based play with ARIA-friendly controls.
- The mobile client provides self-voicing navigation and gesture-driven interaction.
- Game actions, chat, score changes, and outcomes are communicated through speech and sound.

## Game Catalog

PlayAural currently includes **34 games** across multiple categories:

- Card games such as Blackjack, Last Card, Crazy Eights, Pusoy Dos, Tien Len, Scopa, Ninety Nine, Mile by Mile, and Citadels
- Dice games such as Farkle, Bunko, Yahtzee, Pig, Left Right Center, and Color Game
- Board and strategy games such as Chess, Battleship, Backgammon, Sorry!, Ludo, Snakes and Ladders, and Dominos
- Social and bluffing games such as Coup
- Original action and strategy titles such as Battle, Chaos Bear, Pirates of the Lost Seas, Rolling Balls, Toss Up, and Light Turret

## Voice Chat

PlayAural separates voice authorization from media transport.

- The game server verifies whether a player is allowed to join the current table's voice chat.
- A dedicated LiveKit-based voice service carries the real-time media stream.
- The server issues short-lived join tokens and keeps voice membership tied to table context.
- Voice presence announcements and related sounds are synchronized with the normal table lifecycle.

## Languages

PlayAural currently supports:

- English
- Vietnamese

## Repository Layout

- `server/` - server runtime, games, tests, docs, and deployment scripts
- `client/` - desktop client source, sounds, locales, and packaging assets
- `web_client/` - browser client source, service worker, locales, and static assets
- `mobile_client/` - Expo application, mobile locales, sounds, build configuration, and voice integration
- `deployment/` - deployment-specific configuration examples

## Open Source

PlayAural is released as open-source software. Public source code and release builds are distributed through this repository.

## License

This project is licensed under the **GNU GENERAL PUBLIC LICENSE**. See [LICENSE](LICENSE) for the full text.
