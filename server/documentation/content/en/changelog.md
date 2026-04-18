Changelog

Sunday 19 April 2026

Server Updates:

Added a new Restart Game option to the Host Management menu. This is highly useful if you want to start a new match immediately without having to leave and recreate the table. When you restart the game, all table settings and current players remain safely in place.

Fixed a bug where ambient sounds and background music from a previous table would sometimes continue playing after you switched to a different table.

Added a Cancel option to cards that require a choice in Ninety Nine, such as the 10 or Ace, allowing you to back out and change your mind.

Added a clear Not your turn voice feedback if you try to make a move when it is not your turn in games like Ninety Nine, Mile by Mile, and Scopa.

Desktop Client Updates:

Fixed a minor issue with the chat input box when using a Vietnamese keyboard.

Mobile Client Updates:

Fixed an issue where players were sometimes unable to navigate back from the in-game action menu.

Fixed a bug where ambient sounds and background music would abruptly cut out when connecting to the voice chat.

Fixed an issue where in-game notifications were not being sent to the device's system screen reader when the built-in self-voicing mode was turned off.

Fixed an issue with the screen reader focus jumping unexpectedly, ensuring a more stable experience when playing with a system screen reader instead of self-voicing.

Significantly improved the grid board system for games like Battleship and Chess. The grid now displays correctly, and the swiping experience to navigate the grid while using self-voicing has been greatly enhanced.

Thursday 16 April 2026

Server Updates:

Added a real-time voice chat system directly inside the game tables. This feature is only active when you are joined at a table.

How it works: Upon joining a table, you will have the option to join the voice chat. Once joined, you can immediately hear other players. However, to speak and participate in the discussion, you need to turn on your microphone.

Desktop Client Updates:

Integrated the new voice chat system. You can press Alt and V to focus directly on the voice chat area, or use the Tab key to navigate to it if you are using a screen reader while in the game.

Added an audio input selection option, allowing you to choose your preferred microphone to use for voice chat.

Mobile Client Updates:

Integrated the voice chat system. This feature is located inside the Chat tab.

To access it, swipe right with two fingers to open the chat if you are using the built-in self-voicing mode, or tap the Chat button if you are using your device's native screen reader instead of self-voicing.

Web Client Updates:

Integrated the voice chat system. Simply open the Chat tab on the web client interface to see the voice chat options.

Tuesday 14 April 2026

Server Updates:

Rebalanced the gameplay in Chaos Bear to make matches fairer and more engaging.

Battle game updates: Fixed a rare bug that could cause the game to freeze. Added sound effects for when a fighter is destroyed and when a player is eliminated. Added an sound effect for the overall match victory.

Added detailed skill descriptions directly inside the skill menu for Battle. You can now learn exactly what an ability does right in the middle of the game without needing to read the documentation.

Added an audio notification when a new table is created. This sound is enabled by default, but you can turn it off in the Options menu if you prefer.

Added an audio notification whenever someone invites you to join their table. This invite alert is always on and cannot be disabled to ensure you never miss a request from your friends.

Monday 13 April 2026

Server Updates:

Added a new game called Battle, complete with comprehensive beginner documentation. The game is fully localized in both English and Vietnamese.

Fixed a bug where the table join sound would sometimes incorrectly play immediately after a game round ended.

Fixed an issue in Backgammon where spectators watching a match would sometimes falsely receive a notification that they were holding the doubling cube.

Fixed an exploit in Crazy Eights where a player, after playing an 8 (wild-card) to change the suit, could quickly play another card of the new suit before the game passed the turn to the next player.

Mobile Client Updates:

Added an option to disable the built-in self-voicing mode and its custom gestures if you prefer to play the game using your device's native system screen reader.

Please note: The button to toggle self-voicing on or off can only be focused and read by your system screen reader; the game's internal self-voicing system cannot see this button.

When self-voicing is turned off, quick swipe gestures for actions like opening the chat or using shortcuts will be displayed as standard on-screen buttons for easy tapping.

Saturday 11 April 2026

Mobile Client Updates:

Officially launched the PlayAural mobile application. Currently, the app is only available for Android devices.

Integrated a built-in self-voicing feature. This allows you to fully enjoy the game with your device's system screen reader turned off. We highly recommend playing with your system screen reader disabled, as it allows you to use our custom quick gestures smoothly and without any interference.

Thursday 9 April 2026

Server Updates:

Added a new game called Color Game, complete with comprehensive documentation for beginners. The game is fully localized in both English and Vietnamese.

Tien Len updates: Cards in your hand are now automatically sorted from lowest to highest for easier management. Also added clearer and more detailed voice feedback when you attempt an invalid play.

Pusoy Dos updates: Cards in your hand will now also automatically sort from lowest to highest.

Ninety Nine updates: Improved the bot AI to be slightly smarter and made minor underlying code improvements for better performance.

Tuesday 7 April 2026

Server Updates:

Added the highly anticipated card game Tien Len, featuring both Southern and Northern rule variants along with detailed documentation.

Fully localized the game in both English and Vietnamese.

Monday 6 April 2026

Server Updates:

Added a new dice game: Bunko, featuring complete gameplay rules and beginner-friendly documentation.

Fully localized the game in both English and Vietnamese.

Friday 3 April 2026

Server Updates:

Added a new game: Sorry!, featuring complete gameplay rules and beginner-friendly documentation.

Fully localized the game in both English and Vietnamese.

Thursday 2 April 2026

Server Updates:

Improved seat reclamation: If you were replaced by a bot after leaving a game, you can now seamlessly take back your original seat via invitations or the join menu without creating duplicate entries.

Safe table switching: Joining a new table while currently in a game now triggers a proper departure from your active match first. This ensures the game you left remains stable and a bot can take over correctly.

Enhanced system reliability: Added extra safety checks for private table visibility and table switching to prevent errors.

Resolved a technical background issue to ensure the platform runs more reliably across various Windows environments.

Wednesday 1 April 2026

Server Updates:

Added two new games: Chess and Backgammon, featuring complete rules and detailed documentation.

Implemented professional chess clocks with various time control presets.

Added essential match features for Chess, including draw offers, undo requests, and automatic draw detection.

Integrated standard Backgammon mechanics, including doubling cube support and international tournament rules.

Fully localized both games in English and Vietnamese.

Tuesday 31 March 2026

Server Updates:

Added a new game: Ludo, complete with full gameplay rules and detailed documentation.

Fully localized the game with natural and familiar terminology for both English and Vietnamese players.

Sunday 29 March 2026

Server Updates:

Fixed friends list online status mismatches and duplicate login issues caused by typing usernames with different uppercase and lowercase letters.

Refined the online users list so your screen reader immediately focuses on the first person in the list instead of the Back button.

Added the player's current language display to the online users list.

Fixed a critical bug in Coup where players wouldn't be eliminated even after losing all their cards, along with fixing card exchange counts when the deck is almost empty.

Massively overhauled bot AI in Coup. Bots now remember your playstyle, bluff strategically, adapt to game phases, fight aggressively to survive assassinations, and are much more competitive in one-on-one matches.

Desktop Client Updates:

Improved screen reader cursor stability for auto-refreshing menus like the friends list. Your reading position will now remain perfectly still instead of jumping around when the list updates.

Fixed a bug where the Escape key would occasionally stop working as a back button after a background menu refresh.

Web Client Updates:

Synchronized cursor management with the desktop app, ensuring smooth list navigation and perfectly stationary cursor positions during auto-refreshes on the web.

Friday 27 March 2026

Updated and applied bug fixes for Poker games, including Texas Hold'em and Five Card Draw.

Cleaned up the in-game menu: Action buttons like Fold, Call, and Raise will now hide automatically as soon as a hand ends or during the showdown, preventing accidental presses.

Reordered the button layout on the web version to provide the best experience on mobile devices. The most critical action buttons are now placed at the top of the menu for quick and easy tapping.

Fixed a betting limit bug, allowing players to go completely All-in with their entire stack.

Improved screen reader announcements to be more natural and precise, such as fixing the grammar for raise amounts and ensuring you only hear your actual profit when winning an uncontested pot.

Fixed the reading order in Five Card Draw: The game will now announce the current betting phase before announcing whose turn it is, helping you follow the flow of the game better.

Added clear voice feedback when performing an invalid action, such as trying to bet when there is no active betting round, or pressing discard keys outside the draw phase.

Changed some button labels from Reveal to Read for better clarity.

Separated the announcements for the first and second betting rounds in Five Card Draw so they are completely distinct.

Fixed minor audio routing issues to ensure all winner announcements play correctly through the game sound channel.

Wednesday 25 March 2026

Welcome to the first version of PlayAural. This is an audio-first online gaming platform designed to be fully accessible for blind players.

Added 25 different games across four categories, including card games like Ninety Nine, dice games, adventure games like Battleship, and social games like Coup.

Added a desktop application with native screen reader support and low latency.

Added a web version that is best optimized for mobile devices.

Added full bilingual support, allowing you to play in both English and Vietnamese.

Added a complete account system to save progress, skill ratings, add friends, and chat.

Added a spectator mode, allowing players to join tables and listen to ongoing games.

Added comprehensive keyboard shortcuts for desktop users and simple, easy-to-use button layouts for mobile players.

