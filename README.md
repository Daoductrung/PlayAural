# PlayAural

PlayAural is an audio-first online multiplayer gaming platform designed for blind and low-vision players, while still being welcoming to anyone who enjoys accessible games. It brings together classic board games, card games, dice games, and social games in one shared online space with spoken feedback, sound design, multiplayer tables, and cross-client play.

PlayAural is built upon the open-source foundation of [PlayPalace](https://github.com/XGDevGroup/PlayPalace11).

## Play Now

You can use PlayAural in two main ways:

- Download the latest app builds from the repository’s **Releases** section.
- Play directly on the web at [play.ddt.one](https://play.ddt.one).

## What PlayAural Offers

PlayAural focuses on accessibility first.

- Audio-first gameplay with speech and sound cues
- Online multiplayer tables
- Support for desktop, web, and mobile play
- English and Vietnamese language support
- A growing catalog of card, dice, board, and social games

The project includes:

- A game server that manages accounts, tables, matchmaking flow, ratings, persistence, and game rules
- A desktop client
- A web client
- A mobile client

## Accessibility Focus

PlayAural is designed so players can understand and enjoy the full game state through audio.

- The desktop client supports keyboard-first play and screen readers
- The web client works in the browser with touch-friendly controls
- The mobile client is built around self-voicing gesture navigation
- Game actions, status changes, and outcomes are communicated through speech and sound

## Game Library

PlayAural includes a broad mix of multiplayer games, including:

- Card games such as Blackjack, Last Card, Pusoy Dos, Tien Len, Scopa, Ninety Nine, and Mile by Mile
- Dice games such as Farkle, Bunko, Yahtzee, Pig, Left Right Center, and Color Game
- Board and strategy games such as Chess, Battleship, Backgammon, Sorry!, Ludo, Snakes and Ladders, and Dominos
- Social and bluffing games such as Coup
- Larger original experiences such as Pirates of the Lost Seas

The game catalog continues to expand over time. Now 32 games in total.

## Languages

PlayAural currently supports:

- English
- Vietnamese

## Project Structure

The repository is organized into four main parts:

- `server/` — the central multiplayer game server
- `client/` — the desktop client
- `web_client/` — the browser client
- `mobile_client/` — the mobile client

There are also shared localization files, per-game documentation, tests, and build/configuration files throughout the repository.

## Open Source

PlayAural is an open-source project. The project source is available here on GitHub, and public releases are distributed through the repository’s Releases page.

## License

This project is licensed under the **GNU GENERAL PUBLIC LICENSE**. See [LICENSE](LICENSE) for the full text.
