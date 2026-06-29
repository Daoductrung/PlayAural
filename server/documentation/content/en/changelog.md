Changelog

Monday 29 June 2026

New Additions:
- 21 (Survival Rules) now supports two to four players, with survival results across every remaining player and target choices for Change Cards that affect an opponent.
- Administration now includes Server Power Management for scheduling reboots or shutdowns with clear reasons, multilingual custom reasons, countdown warnings, and planned reboots that preserve active tables while clients reconnect.
- Large server menus now support search and 100-item pages with clear page ranges, First page, Previous page, Next page, and Last page controls.
- Unban User and Unmute User now show each active penalty's expiration, remaining time, reason, and issuing admin.

Bug Fixes:
- Who's at the table now lists active players before spectators and clearly reports online, offline, voice chat, and bot takeover status.
- Who's at the table and related roster menus now keep Back available, avoid duplicate or empty menu states, and preserve focus during refreshes.
- Online Players and other auto-refreshing lists now update without duplicating rows, losing Escape or Back behavior, or stealing focus while you are navigating.
- Mobile TalkBack mode now keeps server announcements responsive, interrupts old speech when you move focus, and avoids delayed or repeated messages.
- 21 (Survival Rules) bots now make stronger choices in two-, three-, and four-player matches, and its action buttons, target menus, focus handling, and turn sound behave more consistently.
- Color Game now keeps all-in confirmation inside the selected color's betting menu so you can press the same All-in choice again to confirm.
- Ludo now explains that you must move a piece before rolling again when a roll has already produced a legal move.
- Sorry! now explains that you must choose a legal move before drawing again after a card has already been drawn.

Friday 26 June 2026

New Additions:
- Who's at the table is now an interactive roster with a table summary, each person's roles, host actions, friend actions, and bot removal where available.
- Online Players now opens the full friend actions menu directly when you select someone who is already your friend.
- Pirates of the Lost Seas now shows Check position to touch players during live games.
- Desktop and web Voice Chat now use Alt+V to join or leave and Alt+Shift+V to mute or unmute the microphone.
- Mobile menu click and activation sounds have been refreshed.

Bug Fixes:
- Host Management pass-host, kick, and kick-and-ban lists now refresh automatically when people join or leave the table.
- Your own row in Online Players and Who's at the table is now read-only so you cannot accidentally act on yourself.
- The desktop client now applies server language changes immediately without requiring a restart.
- Desktop sound effect volume changes now affect sounds that are already playing.
- The mobile TTS voice menu now selects system voices correctly and safely keeps saved voices when Android temporarily returns an empty voice list.
- TalkBack mode now drops stale queued server announcements after you move around the screen instead of repeating old messages later.
- The web update/version mismatch message is now localized instead of showing raw English fallback text.

Thursday 25 June 2026

New Additions:
- The web version has been rebuilt into a fuller PlayAural client with stronger keyboard navigation, touch layout, voice chat, password recovery, CAPTCHA support, stable history buffers, and a clearer low-vision interface.
- The web version now tries to reconnect for up to 30 seconds after a network drop or server restart before showing a clear failure message.
- Dead Man's Poker now uses one contextual Fold button instead of separate Fold and Coward's Fold buttons.
- Dead Man's Poker now opens Read table and Read revolvers as modern live status screens.

Bug Fixes:
- Five Card Draw now returns you to the main betting menu immediately after drawing cards or standing pat.
- Texas Hold'em and Five Card Draw now stop showing gameplay actions to busted players.
- Dead Man's Poker now lets Call and All-in both call an opponent's all-in amount correctly.
- Friends and player lists now distinguish people in the main menu from people waiting at a table.
- End-of-game result screens are now individual, so closing your results no longer closes another player's results.
- End-of-game result screens no longer disappear when someone joins or leaves the table.
- Game-over screens now stay responsive if a match ends while you are reading another menu such as Friends or Options.
- Host Management invite, pass-host, kick, and kick-and-ban flows now stay open after an action so hosts can keep managing the table.
- The mobile game connection now stays alive when the app is minimized or the screen is off.
- Mobile voice chat microphones now keep transmitting in the background on devices that previously stopped after several seconds.
- Mobile voice chat no longer forces game audio into mono.
- Mobile self-voicing gestures now respond more reliably during play.
- Mobile edit boxes now read their contents more reliably in self-voicing mode.
- Mobile TTS voice changes now apply more reliably without restarting.
- Mobile TTS speed changes now apply more reliably without restarting.
- Mobile TalkBack focus now stays inside active game menus more reliably when self-voicing is off.
- Web Tab navigation now cycles through the menu, history, and chat during play.
- Web Escape navigation now works from more server menus, including online player lists.
- Web input prompts now choose single-line or multiline fields from the server's request type and submit single-line inputs with Enter.
- Web menu sounds now follow desktop-style navigation feedback more closely.
- Web typing sounds now play during input prompts.
- Web F4 buffer muting now works from the active buffer.
- Web music and ambience volume shortcuts now adjust the active browser audio.
- Web ARIA live and Web Speech output now avoids skipped messages more reliably.
- Web buffer-reading shortcuts now work in Web Speech mode.
- Web voice selection and speech speed controls are clearer across Windows, Android, iOS, and macOS.
- Web localization and connection messages are clearer in English and Vietnamese.
- Android browsers now report Android instead of Linux in the online players list.

Sunday 21 June 2026

New Additions:
- Yahtzee now supports solo practice without affecting competitive rankings.
- Yahtzee now lets players and spectators press Shift+C to check any player's scorecard.
- Pirates of the Lost Seas Portal now includes a Random destination that can choose any valid map space, including empty seas.
- Rolling Balls now includes richer and more accurate Around the World and Journey Through Vietnam ball sets.
- Rolling Balls documentation now clearly credits the original open-source PlayPalace project.
- Chaos Bear now supports Brief announcements.
- Farkle's default Target Score is now 1000.

Bug Fixes:
- The platform-wide turn announcement now tells the active player "It is your turn" while everyone else hears whose turn it is.
- Chess timeout and check announcements now use separate personal and public wording.
- Citadels final winner announcements now use separate personal and public wording.
- Sorry! final winner announcements now use separate personal and public wording.
- UNO elimination, scoring, and final winner announcements now use separate personal and public wording.
- Age of Heroes battle summaries now use separate attacker, defender, and observer wording.
- Menu focus now restores more reliably when returning from Administration, Host Management, Options, table menus, status screens, and action prompts.
- The Start game option now stays visible in waiting rooms and explains setup problems when selected.
- Dice keeping preferences now explain Dice indexes and Dice values more clearly and only appear in games that use them.
- Yahtzee standard score checks now show real Yahtzee totals.
- Yahtzee scoring a category now returns touch focus to Roll dice.
- Chess takeback acceptance no longer resolves the game as a draw.
- Chess undo history is cleaned up correctly.
- Chess keeps Enter Move visible as a stable focus anchor and returns touch focus there after submitting a move.
- Pirates of the Lost Seas Sailor's Instinct no longer creates blank choices.
- Pirates of the Lost Seas bot strategy is stronger and uses skills more intelligently.
- Pirates of the Lost Seas skill balance, skill messages, and Portal lock-in feedback are clearer.
- Rolling Balls rules, manuals, ball terminology, and announcements are clearer in English and Vietnamese.
- Mile by Mile now explains distance-card limits clearly and allows legal cards that do not pass the finish.
- Mile by Mile now respects Require exact finish and over-finish options correctly.
- Mile by Mile discard prompts now restore focus to the card you came from.
- Snakes and Ladders now gives clearer start, ladder, snake, bounce-back, exact-finish, and winning announcements.
- Midnight now keeps roll and score-lock focus steadier for touch clients.
- Threes now keeps dice result, roll, and score menu focus steadier for touch clients.
- Toss Up now returns touch focus gently after banking without stealing it during normal navigation.
- Pig now returns touch focus gently after holding without stealing it during normal navigation.
- Tradeoff now keeps roll, trade, and score menus steadier for touch clients.
- Bunko now keeps roll and status menus steadier for touch clients.
- Farkle now keeps dice-choice and roll menus steadier for touch clients.
- Color Game now keeps betting and status menus steadier for touch clients.
- Light Turret now keeps fire, upgrade, and status menus steadier for touch clients.
- Left Right Center now keeps roll and chip-status menus steadier for touch clients.
- Metal Pipe now keeps action and status menus steadier for touch clients.
- Farkle bots now make stronger risk-versus-reward decisions.
- Rolling Balls bots now make stronger decisions.
- Tradeoff bots now make stronger decisions.
- Pirates of the Lost Seas bots now use movement, attacks, and skills more strategically.
- UNO now preserves a pending Draw stack correctly when a Draw card wins the hand.
- Cards Against Humanity now gives clearer feedback for submissions, judging, multi-judge setup, larger hand sizes, and English-only card text.
- Cards Against Humanity sound cues now route correctly across clients.

Wednesday 17 June 2026

New Additions:
- UNO now has full beginner-friendly documentation in English and Vietnamese.
- Chess now supports typed move input using common chess notation and coordinate-style moves.
- Chess now has a stronger bounded bot.
- Battle now supports Team Battle through the standard team setup flow.
- Battle fighter skills are completed, rebalanced, and explained in-game.
- Live status boxes now let scoreboards, boards, standings, rosters, and other status screens stay open and refresh while the game changes.

Bug Fixes:
- Coup now has clearer announcements and steadier screen reader menus.
- Citadels now has clearer announcements and safer setup feedback.
- Backgammon now has clearer announcements and steadier screen reader menus.
- Battle now has clearer announcements and safer skill feedback.
- Battleship now has clearer announcements and steadier deployment menus.
- Chess now has clearer announcements and steadier move-entry menus.
- Crazy Eights now has clearer announcements and steadier suit-choice menus.
- Chaos Bear now has clearer announcements and steadier screen reader menus.
- Dead Man's Deck now has clearer announcements and steadier action menus.
- Dead Man's Poker now has clearer announcements and steadier betting menus.
- Senet now has clearer announcements and steadier board menus.
- Ludo now has clearer announcements and steadier piece menus.
- Sorry! now has clearer announcements and steadier pawn menus.
- Threes now has clearer announcements and steadier dice menus.
- 21 (Survival Rules) now has clearer announcements and safer action feedback.
- Chess now follows standard full-move counting and gives shorter Brief announcements when enabled.
- Battleship now gives clearer deployment and firing feedback.
- Battleship manual ship placement uses the isolated placement menu again.
- Battleship now reports each player's deployment readiness when checking whose turn during setup.
- Crazy Eights now handles Wild 8 suit choice more like UNO and avoids irrelevant not-your-turn errors for suit shortcuts.
- Dead Man's Poker keeps touch action menus anchored during card exchanges and table events.
- Dead Man's Poker showdown announcements are less repetitive and tied hands are reported as draws.
- Dead Man's Poker bots now play more aggressively and intelligently.
- Dead Man's Deck gives clearer rule feedback, status information, bluffing, challenge, and survival announcements.
- Coup now applies the official two-player first-turn coin rule even when the first player is a bot.
- Coup exchange menus now keep selected cards visible and mark exchanged cards.
- Citadels now gives clearer build, character, and scoring feedback.
- Senet now handles spectators correctly and uses standard S and Shift+S score shortcuts.
- Senet no longer overwrites another open menu during board refreshes.
- Backgammon now makes Brief announcements genuinely brief.
- Ludo now makes Brief announcements genuinely brief.
- Sorry! now makes Brief announcements genuinely brief.
- Backgammon now gives a clear error if you try to move before rolling.
- Ludo keeps touch focus steadier after rolls, automatic moves, and manual piece choices.
- Sorry! keeps touch focus steadier after draws, automatic moves, and manual pawn choices.
- Sorry! move prompts now include each pawn's current position.
- Midnight and Farkle now move focus to the first dice choice after a roll asks you to keep dice.
- 21 (Survival Rules) no longer reveals an opponent's hidden total when they stand.
- 21 (Survival Rules) now explains when an active effect prevents drawing.
- Age of Heroes now handles declined or unavailable road-building requests safely.
- Basic score checks now speak each player or team separately.
- Detailed score checks now use clear line-by-line status screens where appropriate.
- Leaderboard menus now hide games that do not support leaderboards.
- Old unsupported leaderboard data is cleaned up safely.
- Table invites can no longer be declined by pressing the invite title.
- Table invites that arrive while you are typing wait until you finish the input.
- The Play category filter no longer leaks into Documentation, Leaderboards, or My Stats.
- Documentation pages render escaped Markdown more consistently.
- Desktop Ctrl+F1 How to Play no longer leaves the action menu empty after closing the rules screen.

Tuesday 9 June 2026

New Additions:
- Age of Heroes was added with localized menus and documentation.
- Metal Pipe was added with localized menus and documentation.
- Nine was added with localized menus and documentation.
- Senet was added with localized menus and documentation.
- Cards Against Humanity was added with localized menus and documentation.
- 21 (Survival Rules) was added with localized menus and documentation.
- UNO was added as the replacement for Last Card.
- The Play menu now has a category filter for browsing games by type.
- Options are now split into clearer General Options and Game Options sections.
- Game Options now support per-game preference overrides.
- Confirm risky actions and Brief announcements were added as personal game options where games benefit from them.
- Sound Effects Volume was added alongside Music, Ambience, and Voice Chat volume.
- Mobile now has top navigation tabs for Main, Chat, History, and Shortcuts when self-voicing is off.
- Web and mobile clients now honor per-item highlight sounds, including Backgammon board square sounds.

Bug Fixes:
- Scopa now has clearer rules, better prompts, and more natural announcements.
- Blackjack now has clearer rules, better prompts, and more natural announcements.
- Ninety Nine now has clearer rules, better prompts, and more natural announcements.
- Mile by Mile now has clearer rules, better prompts, and more natural announcements.
- Dominos now has clearer rules, better prompts, and more natural announcements.
- 21 now has clearer rules, better prompts, and more natural announcements.
- Tien Len now has clearer rules, better prompts, and more natural announcements.
- Pusoy Dos now has clearer rules, better prompts, and more natural announcements.
- Five Card Draw now has clearer rules, better prompts, and more natural announcements.
- Texas Hold'em now has clearer rules, better prompts, and more natural announcements.
- Ludo now has clearer rules, better prompts, and more natural announcements.
- Sorry! now has clearer rules, better prompts, and more natural announcements.
- Backgammon now has clearer rules, better prompts, and more natural announcements.
- Citadels now has clearer rules, better prompts, and more natural announcements.
- Blackjack now skips bankrupt players, uses chips consistently, locks bets when confirmed, and spaces out dealer card draws.
- Ninety Nine now excludes eliminated players from future dealing.
- Ninety Nine now starts each new round with a random first player and pauses briefly between rounds.
- Ninety Nine now restores localized menus correctly after reconnecting.
- Ninety Nine now fixes a rare count overflow bug.
- Dead Man's Poker now tracks showdown wins correctly and handles ties with clearer draw announcements.
- Dead Man's Poker now allows one card swap per hand and blocks first-round All-in actions.
- Mile by Mile now recognizes Dirty Trick when the correct safety card is played during the reaction window.
- Mile by Mile unplayable cards now explain the reason and offer discard or cancel.
- Dominos now keeps spinner branches stable.
- Dominos now lets the correct opening player choose their opening tile.
- Tien Len now follows Southern and Northern rule details more closely.
- Tien Len now supports continued play for remaining places, instant wins, chopping rules, Southern Vietnamese terminology, and coin scoring.
- Pusoy Dos now validates rules more strictly.
- Pusoy Dos now gives clearer localized messages.
- Pusoy Dos bots now make better decisions.
- Pusoy Dos risky passes now use safer confirmation handling.
- Five Card Draw now keeps useful information actions available on touch clients during the hand.
- Texas Hold'em now keeps useful information actions available on touch clients during the hand.
- Ludo now respects each player's Brief announcements preference.
- Sorry! now respects each player's Brief announcements preference.
- Ludo now keeps screen reader focus routed to the next useful action after direct roll or move interactions.
- Sorry! now keeps screen reader focus routed to the next useful action after direct draw or move interactions.
- Touch clients now keep primary actions visible as focus anchors while still speaking clear errors when actions are not allowed.
- Turn sounds are more consistent.
- Crazy Eights spectator join and leave sounds now play again.
- Table join and leave sounds now also play for kicks and bans.
- Cards Against Humanity now uses its dedicated sound effects.
- Human players can no longer register names reserved for bots.
- Bots can no longer impersonate human players at the same table.
- Mobile status details now appear at the bottom of the screen reader order instead of before the main game content.
- Desktop shortcut routing is more reliable for recently added grid and board games.

Tuesday 5 May 2026

New Additions:
- Dead Man's Poker was added with full beginner documentation and English/Vietnamese localization.
- Options were reorganized into categorized submenus.
- Voice Chat Volume was added to Options.
- Desktop now supports the Voice Chat Volume control.
- Web now supports the Voice Chat Volume control.
- Mobile now supports the Voice Chat Volume control.

Bug Fixes:
- Dead Man's Deck intro audio timing was refined for a smoother cinematic start.
- Options submenu return paths now restore more reliably after editing values or backing out.

Saturday 2 May 2026

New Additions:
- Team arrangement was added so hosts can assign and swap teams before supported team games.
- Friend deletion now asks for confirmation before removing someone.

Bug Fixes:
- Score checks now announce exact score units for each game instead of generic terms.
- Score checks now show replacement bot names correctly when a disconnected player has been taken over.

Wednesday 29 April 2026

New Additions:
- Replacement bots now use a different bot name instead of taking the disconnected player's exact name.
- Disconnected players can reclaim their exact seat while the current match is still ongoing.
- Lobby cleanup now converts disconnected seated players into reclaimable replacement bots before the host starts a match.
- Seat handoff sounds and announcements now identify both the original human and the replacement bot.

Bug Fixes:
- Custom bot names can no longer match anyone at the table or any registered player.
- Disconnected spectators are now removed before a match begins.

Tuesday 28 April 2026

New Additions:
- Dead Man's Deck was added with beginner documentation.
- Dead Man's Deck is fully localized in English and Vietnamese.

Sunday 26 April 2026

New Additions:
- Adding a bot now automatically assigns a random bot name unless Custom bot names is enabled.
- Custom bot names now require unique names from 3 to 30 characters.

Bug Fixes:
- Table invites that arrive while you are typing in an input box now wait safely until you finish.
- Reclaiming a seat from a replacement bot now announces the return to the whole table.
- Invalid slash commands no longer broadcast as regular chat messages.
- Mobile input cancel actions no longer freeze the menu.
- Mobile self-voicing gestures are smoother and more reliable.

Thursday 23 April 2026

New Additions:
- Citadels was added with comprehensive documentation.
- Citadels is fully localized in English and Vietnamese.
- Mobile gained experimental background-running support.

Bug Fixes:
- Desktop interface internals were optimized for smoother and more stable play.
- Mobile ping checks now return results when self-voicing is off.
- Mobile players can now discard Mile by Mile cards with the screen reader long-press gesture.
- Mobile device language detection is smoother on first launch.
- Mobile network connection threads are more stable and responsive.

Sunday 19 April 2026

New Additions:
- Host Management now has Restart Game to return a table to the waiting room without recreating it.
- Ninety Nine choice cards such as 10 and Ace now include Cancel.
- Ninety Nine now gives clear Not your turn feedback.
- Mile by Mile now gives clear Not your turn feedback.
- Scopa now gives clear Not your turn feedback.

Bug Fixes:
- Ambience and background music from a previous table no longer continue after switching tables.
- Desktop chat input works better with Vietnamese keyboards.
- Mobile players can navigate back from the in-game action menu more reliably.
- Mobile ambience and background music no longer cut out when joining voice chat.
- Mobile game notifications now reach the system screen reader when self-voicing is off.
- Mobile screen reader focus is steadier when using the system screen reader.
- Mobile grid boards such as Battleship and Chess now display and navigate more reliably.

Thursday 16 April 2026

New Additions:
- Real-time table Voice Chat was added.
- Desktop now includes table Voice Chat controls.
- Desktop now lets you choose an audio input device for Voice Chat.
- Mobile now includes table Voice Chat in the Chat tab.
- Web now includes table Voice Chat in the Chat area.

Tuesday 14 April 2026

New Additions:
- Battle skill descriptions were added directly inside the skill menu.
- Table-created notification sounds were added.
- Table invite notification sounds were added.

Bug Fixes:
- Chaos Bear gameplay was rebalanced for fairer matches.
- Battle no longer freezes in a rare match-ending case.
- Battle now plays clearer sounds for destroyed fighters, eliminated players, and match victory.

Monday 13 April 2026

New Additions:
- Battle was added with beginner documentation.
- Battle is fully localized in English and Vietnamese.
- Mobile now lets players disable self-voicing and use the device's system screen reader instead.
- Mobile shows standard on-screen buttons for chat and shortcuts when self-voicing is off.

Bug Fixes:
- Table join sounds no longer incorrectly play immediately after a game round ends.
- Backgammon spectators no longer receive false doubling-cube holder messages.
- Crazy Eights no longer lets a player play another card immediately after changing suit with a wild 8.

Saturday 11 April 2026

New Additions:
- The PlayAural mobile app launched for Android.
- The mobile app includes built-in self-voicing for playing without the system screen reader.

Thursday 9 April 2026

New Additions:
- Color Game was added with beginner documentation.
- Color Game is fully localized in English and Vietnamese.

Bug Fixes:
- Tien Len now sorts cards from lowest to highest and gives clearer invalid-play feedback.
- Pusoy Dos now sorts cards from lowest to highest.
- Ninety Nine bots now make more natural decisions.

Tuesday 7 April 2026

New Additions:
- Tien Len was added with Southern and Northern rule variants.
- Tien Len is fully localized in English and Vietnamese.

Monday 6 April 2026

New Additions:
- Bunko was added with complete rules and beginner documentation.
- Bunko is fully localized in English and Vietnamese.

Friday 3 April 2026

New Additions:
- Sorry! was added with complete rules and beginner documentation.
- Sorry! is fully localized in English and Vietnamese.

Thursday 2 April 2026

New Additions:
- Players replaced by a bot can reclaim their original seat through invites or the join menu.
- Joining a new table while already in a game now leaves the current match safely first.

Bug Fixes:
- Private table visibility and table switching are more reliable.
- Windows startup and runtime reliability were improved.

Wednesday 1 April 2026

New Additions:
- Chess was added with complete rules and documentation.
- Backgammon was added with complete rules and documentation.
- Chess includes clock presets, draw offers, undo requests, and automatic draw detection.
- Backgammon includes the doubling cube and international tournament rules.
- Chess is fully localized in English and Vietnamese.
- Backgammon is fully localized in English and Vietnamese.

Tuesday 31 March 2026

New Additions:
- Ludo was added with complete rules and detailed documentation.
- Ludo uses natural English and Vietnamese terminology.

Sunday 29 March 2026

New Additions:
- The online users list now displays each player's current language.
- Coup bots now remember play patterns, bluff strategically, adapt to game phases, and fight harder to survive.

Bug Fixes:
- Friends list online statuses now handle username capitalization consistently.
- Duplicate logins caused by different username capitalization are blocked.
- The online users list now focuses the first person instead of the Back button.
- Coup players are now eliminated correctly after losing all influence cards.
- Coup exchange counts now work correctly when the deck is nearly empty.
- Desktop focus stays steadier in auto-refreshing lists such as Friends.
- Desktop Escape now works more reliably after background menu refreshes.
- Web cursor management now keeps list navigation stable during auto-refreshes.

Friday 27 March 2026

New Additions:
- Web poker action buttons were reordered so important mobile actions are easier to reach.
- Poker invalid actions now give clearer feedback.
- Several poker buttons were renamed from Reveal to Read for clarity.
- Five Card Draw first and second betting round announcements are now distinct.

Bug Fixes:
- Texas Hold'em and Five Card Draw now hide Fold, Call, Raise, and similar action buttons after a hand ends or during showdown.
- Poker betting limits now allow a player to go fully All-in.
- Poker announcements now use clearer grammar and report actual uncontested-pot profit.
- Five Card Draw now announces the betting phase before announcing whose turn it is.
- Poker winner announcements now use the correct game sound channel.

Wednesday 25 March 2026

New Additions:
- PlayAural launched as an audio-first online gaming platform for blind players.
- The first release included 25 games across card, dice, strategy, and social game families.
- The desktop client launched with native screen reader support and low latency.
- The web client launched with a mobile-friendly layout.
- English and Vietnamese support launched across the platform.
- Player accounts launched with saved progress, skill ratings, friends, and chat.
- Spectator mode launched for listening to active tables.
- Desktop keyboard shortcuts and mobile-friendly button layouts launched.
