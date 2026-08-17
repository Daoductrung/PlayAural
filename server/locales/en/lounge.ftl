# Lounge chat room messages

game-name-lounge = Lounge

# Room lifecycle
lounge-welcome = Welcome to the Lounge. This table is only for talking: use table chat, play emotes, and open the room tools from your menu.
lounge-welcome-spectator = Welcome to the Lounge. You are watching, so you can read the room and follow the chat, but emotes and room tools stay with the people seated.
lounge-cannot-start = The Lounge is always open, so there is no game to start. Chat, emotes and room tools are available to everyone the moment they sit down.
lounge-no-bots = The Lounge is a room for people, so bots cannot be added here. Invite someone from the players list instead.
lounge-no-save = A Lounge is a live room, so there is nothing to save. The room closes on its own when the last person leaves.

# Emote labels
lounge-emote-wave = Wave
lounge-emote-laugh = Laugh
lounge-emote-applaud = Applaud
lounge-emote-boo = Boo
lounge-emote-toast = Raise a toast
lounge-emote-facepalm = Facepalm
lounge-emote-think = Think it over
lounge-emote-celebrate = Celebrate
lounge-emote-description = Play this emote, with its sound, for everyone in the room.

# Emote announcements
lounge-emote-wave-you = You wave at the room.
lounge-emote-wave-other = { $player } waves at the room.
lounge-emote-laugh-you = You burst out laughing.
lounge-emote-laugh-other = { $player } bursts out laughing.
lounge-emote-applaud-you = You applaud.
lounge-emote-applaud-other = { $player } applauds.
lounge-emote-boo-you = You boo.
lounge-emote-boo-other = { $player } boos.
lounge-emote-toast-you = You raise a toast to the room.
lounge-emote-toast-other = { $player } raises a toast to the room.
lounge-emote-facepalm-you = You facepalm.
lounge-emote-facepalm-other = { $player } facepalms.
lounge-emote-think-you = You think it over in silence.
lounge-emote-think-other = { $player } thinks it over in silence.
lounge-emote-celebrate-you = You celebrate.
lounge-emote-celebrate-other = { $player } celebrates.

# Nudge
lounge-nudge = Nudge someone
lounge-nudge-description = Send a private sound and a short message to one person in the room.
lounge-nudge-prompt = Choose who to nudge
lounge-nudge-you = You nudge { $target }.
lounge-nudge-target = { $player } nudges you.
lounge-nudge-other = { $player } nudges { $target }.
lounge-nudge-no-targets = There is nobody else in the room to nudge yet. Wait for someone to sit down.
lounge-nudge-target-left = { $target } is no longer in the room, so the nudge was not sent.
lounge-nudge-self = You cannot nudge yourself. Pick another person in the room.

# Party tools
lounge-roll-dice = Roll two dice
lounge-roll-dice-description = Roll two six-sided dice out loud for the whole room.
lounge-roll-you = You roll { $first } and { $second }, for a total of { $total }.
lounge-roll-other = { $player } rolls { $first } and { $second }, for a total of { $total }.
lounge-flip-coin = Flip a coin
lounge-flip-coin-description = Flip a coin out loud for the whole room.
lounge-flip-you = You flip a coin and it lands on { $side }.
lounge-flip-other = { $player } flips a coin and it lands on { $side }.
lounge-coin-heads = heads
lounge-coin-tails = tails

# Away
lounge-mark-away = Mark yourself away
lounge-mark-back = Come back from away
lounge-away-description = Tell the room you have stepped away. You stay seated and can come back at any time.
lounge-away-you = You are now marked as away. You keep your seat, and everyone can see you stepped out.
lounge-away-other = { $player } is now away.
lounge-back-you = You are back from away.
lounge-back-other = { $player } is back.

# Topic
lounge-set-topic = Set the room topic
lounge-set-topic-description = Only the host can change what this room is about. Everyone hears the new topic.
lounge-set-topic-prompt = Type the new room topic, or send it empty to clear the current one
lounge-read-topic = Read the room topic
lounge-read-topic-description = Hear what this room is about right now.
lounge-topic-set-you = You set the room topic to: { $topic }
lounge-topic-set-other = { $player } set the room topic to: { $topic }
lounge-topic-cleared-you = You cleared the room topic.
lounge-topic-cleared-other = { $player } cleared the room topic.
lounge-topic-unchanged = The room topic already says exactly that, so nothing changed.
lounge-topic-already-empty = The room has no topic to clear.
lounge-topic-current = Room topic, set by { $player }: { $topic }
lounge-topic-none = This room has no topic yet. The host can set one from the room tools.
lounge-topic-not-host = Only the host can set the room topic. Ask { $host } to change it.
lounge-topic-too-long = That topic is too long. Keep it to { $max } characters or fewer; yours had { $count }.
lounge-topic-unreadable = That topic had no readable text in it, so the room topic was left as it was.

# Room information
lounge-room-info = Room information
lounge-room-info-description = Read the topic, who is here, who is away, and the current room settings.
lounge-info-host = Host: { $host }.
lounge-info-topic = Topic: { $topic }
lounge-info-topic-none = Topic: not set yet.
lounge-info-topic-author = Topic set by { $player }.
lounge-info-people = Seated: { $count } { $count ->
        [one] person
       *[other] people
    }.
lounge-info-spectators = Watching: { $count }.
lounge-info-away = Away right now: { $count }.
lounge-info-emotes = Emotes played in this room: { $count }.
lounge-info-person = { $player }
lounge-info-person-host = { $player } (host)
lounge-info-person-away = { $player } (away)
lounge-info-person-host-away = { $player } (host, away)
lounge-info-person-spectator = { $player } (watching)
lounge-info-settings = Room settings: emotes { $emotes }, nudges { $nudges }, dice and coin { $party }, waiting time between room actions { $cooldown } { $cooldown ->
        [one] second
       *[other] seconds
    }.

# Blocked actions
lounge-emotes-disabled = Emotes are turned off in this room. The host can turn them back on in the room settings.
lounge-nudges-disabled = Nudges are turned off in this room. The host can turn them back on in the room settings.
lounge-party-tools-disabled = Dice and coin flips are turned off in this room. The host can turn them back on in the room settings.
lounge-cooldown-wait = Wait { $seconds } more { $seconds ->
        [one] second
       *[other] seconds
    } before your next emote, nudge, dice roll or coin flip.
lounge-spectator-blocked = Only people seated in the room can do that. Take a seat first if you want to join in.

# Options
lounge-set-allow-emotes = Emotes: { $enabled }
lounge-option-changed-allow-emotes = Emotes set to { $enabled }.
lounge-desc-allow-emotes = When enabled, everyone seated can play emotes with their sounds for the whole room (default on).
lounge-set-allow-nudges = Nudges: { $enabled }
lounge-option-changed-allow-nudges = Nudges set to { $enabled }.
lounge-desc-allow-nudges = When enabled, everyone seated can send one person a private nudge sound (default on).
lounge-set-allow-party-tools = Dice and coin: { $enabled }
lounge-option-changed-allow-party-tools = Dice and coin set to { $enabled }.
lounge-desc-allow-party-tools = When enabled, everyone seated can roll two dice or flip a coin for the room (default on).
lounge-set-action-cooldown = Waiting time between room actions: { $seconds } { $seconds ->
        [one] second
       *[other] seconds
    }
lounge-prompt-action-cooldown = Enter how many seconds each person must wait between emotes, nudges, dice rolls and coin flips
lounge-option-changed-action-cooldown = Waiting time between room actions set to { $seconds } { $seconds ->
        [one] second
       *[other] seconds
    }.
lounge-desc-action-cooldown = How long each person waits between emotes, nudges, dice rolls and coin flips, so the room stays comfortable to listen to (default 3 seconds, range 0-60).
