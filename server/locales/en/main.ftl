auth-username-password-required = Username and password are required.
auth-registration-success = Registration successful! You can now log in with your credentials.
auth-username-taken = Username already taken. Please choose a different username.
auth-username-reserved-bot = This name is reserved for PlayAural bots. Please choose a different username.
auth-registration-error = Registration failed due to a server error. Please try again.
auth-error-wrong-password = Incorrect password.
auth-error-user-not-found = User does not exist.
auth-kicked-logged-in-elsewhere = You have been disconnected because your account was logged in from another device.

chat-global = { $player } says globally: { $message }
dev-announcement-broadcast = { $dev } is a developer of PlayAural.
admin-announcement-broadcast = { $admin } is an administrator of PlayAural.

admin-smtp-updated-success = SMTP setting updated successfully
admin-smtp-settings = SMTP Settings
email-reset-subject = PlayAural Password Reset Code
email-reset-body = Hello { $username },\n\nYou requested a password reset for your PlayAural account.\nYour 6-digit reset code is: { $code }\n\nThis code will expire in 15 minutes.\nIf you did not request this, please ignore this email.
email-reset-body-html = <p>Hi { $username },</p>
    <p>We received a request to reset the password for your PlayAural account.</p>
    <p>Your 6-digit recovery code is:</p>
    <h2>{ $code }</h2>
    <p>This code will expire in exactly 15 minutes.</p>
    <p>If you did not request this, please ignore this email. Your account remains secure.</p>
    <p>Best regards,<br>Trung</p>
email-test-subject = PlayAural SMTP Test
email-test-body = This is a test email from the PlayAural server verifying your SMTP configuration.
email-test-body-html = <p>Hello,</p>
    <p>This is a test email from the PlayAural server.</p>
    <p>If you are reading this, your SMTP configuration is successfully sending HTML emails.</p>
smtp-test-sending = Testing connection, please wait...
smtp-test-success = Test email sent successfully to { $email }!
smtp-test-failed = Failed to send test email: { $error }
smtp-host = Host: { $value }
smtp-port = Port: { $value }
smtp-username = Username: { $value }
smtp-password = Password: { $value }
smtp-from-email = From Email: { $value }
smtp-from-name = From Name: { $value }
smtp-encryption = Encryption: { $value }
smtp-test-connection = Test Connection
smtp-not-set = Not set
smtp-prompt-host = Enter SMTP Host (e.g., smtp.gmail.com):
smtp-prompt-port = Enter SMTP Port (e.g., 587 or 465):
smtp-prompt-username = Enter SMTP Username:
smtp-prompt-password = Enter SMTP Password:
smtp-prompt-from-email = Enter From Email address:
smtp-prompt-from-name = Enter From Name (e.g., PlayAural Support):
smtp-prompt-test-email = Enter target email address for test:
smtp-enc-none = No encryption
smtp-enc-ssl = Use SSL
smtp-enc-tls = Enable TLS encryption automatically (STARTTLS)
smtp-current-enc = * { $value }

main-menu-title = Main Menu

play = Play
view-active-tables = View active tables
options = Options
logout = Logout
back = Back
go-back = Go back
context-menu = Context menu.
no-actions-available = No actions available.
table-new-host-promoted = { $player } is now the table host.
return-to-lobby = Return to lobby
return-to-table = Return to table
create-table = Create a new table
leave-table = Leave table
start-game = Start game
add-bot = Add bot
remove-bot = Remove bot
actions-menu = Actions menu
save-table = Save table
whose-turn = Whose turn
whos-at-table = Who's at the table
check-scores = Check scores
check-scores-detailed = Detailed scores

game-player-skipped = { $player } is skipped.

table-created = { $host } created a new { $game } table.
table-created-broadcast = { $host } created a new { $game } table.
table-joined = { $player } joined the table.
table-left = { $player } left the table.
new-host = { $player } is now the host.
waiting-for-players = Waiting for players. {$min} min, { $max } max.
game-starting = Game starting!
table-listing = { $host }'s table ({ $count } users)
table-listing-one = { $host }'s table ({ $count } user)
table-listing-with = { $host }'s table ({ $count } users) with { $members }
table-listing-game = { $game }: { $host }'s table ({ $count } users)
table-listing-game-one = { $game }: { $host }'s table ({ $count } user)
table-listing-game-with = { $game }: { $host }'s table ({ $count } users) with { $members }
table-listing-game-status = { $game } [{ $status }]: { $host }'s table ({ $count } users)
table-listing-game-one-status = { $game } [{ $status }]: { $host }'s table ({ $count } user)
table-listing-game-with-status = { $game } [{ $status }]: { $host }'s table ({ $count } users) with { $members }
table-status-waiting = Waiting
table-status-playing = Playing
table-status-finished = Finished
table-not-exists = Table no longer exists.
table-full = Table is full.
player-replaced-by-bot = { $bot } is now playing on behalf of { $player }.
player-reclaimed-from-bot = { $player } has returned and taken their seat back from { $bot }.
player-took-over = { $player } has taken their seat back from { $bot }.
spectator-joined = Joined { $host }'s table as a spectator.

spectate = Spectate
now-playing = { $player } is now playing.
now-spectating = { $player } is now spectating.
spectator-left = { $player } stopped spectating.

welcome = Welcome to PlayAural!
goodbye = Goodbye!

user-online = { $player } came online.
user-offline = { $player } went offline.
friend-online = Your friend { $player } is now online.
friend-offline = Your friend { $player } went offline.
permission-denied = You do not have permission to perform this action on a Developer.
kick-user = Kick User
kick-broadcast = { $target } was kicked by { $actor }.
you-were-kicked = You have been kicked by { $actor }.
user-not-online = User { $target } is not online.
kick-immune = You cannot kick this user.
kick-confirm = Are you sure you want to kick { $player }?
no-users-to-kick = No users available to kick.
usage-kick = Usage: /kick <username>
online-users-none = No users online.
online-users-one = 1 user: { $users }
online-users-many = { $count } users: { $users }
online-user-not-in-game = Main menu
online-user-waiting-approval = Waiting for approval
presence-status-main-menu = Main menu
presence-status-waiting-table = Waiting at { $game } table
presence-status-playing = Playing { $game }
presence-status-spectating = Spectating { $game }
presence-status-watching-table = Watching { $game } table
presence-status-reviewing-results = Reviewing { $game } results
presence-status-spectating-results = Watching { $game } results
user-role-dev = Developer
user-role-admin = Admin
user-role-user = User
client-type-web = Web
client-type-python = Desktop
client-type-mobile = Mobile
client-type-with-platform = { $client } ({ $platform })
online-user-full-entry = { $username } ({ $role }, { $client }, { $language }): { $status }
online-user-actions-title = Actions for { $username }
user-not-online-anymore = This user is no longer online.
close-menu = Close

language = Language
language-option = Language: { $language }
language-changed = Language set to { $language }.
language-menu-entry =
    { $official ->
        [true] { $language }. Official PlayAural language. Translators: { $translators }.
       *[false] { $language }. Community translation. Translators: { $translators }.
    }
language-menu-entry-missing-metadata = { $language }. Translator metadata unavailable.
language-menu-current-entry = Current: { $entry }

option-on = On
option-off = Off

# Multi-select option sub-menu controls
option-back = Back
option-select-all = Select all
option-deselect-all = Deselect all
option-selected-count = { $count } selected
option-deselected-count = { $count } deselected
option-min-selected = You must select at least { $count }.
option-max-selected = You can select at most { $count }.

turn-sound-option = Turn sound: { $status }

custom-bot-names-option = Custom bot names: { $status }
confirm-destructive-option = Confirm risky actions: { $status }
clear-kept-option = Clear kept dice when rolling: { $status }
option-notify-table-created = Notify when table created: { $status }
option-notify-user-presence = User online/offline notifications: { $status }
option-notify-friend-presence = Friend online/offline notifications: { $status }
dice-keeping-style-option = Dice keeping style: { $style }
dice-keeping-style-changed = Dice keeping style set to { $style }.
dice-keeping-style-indexes = Dice indexes
dice-keeping-style-values = Dice values

# Personal options split: general vs game options
general-options = General options
game-options = Game options

# Game Options (declarative preferences with per-game overrides)
pref-category-display = Display
pref-set-brief-announcements = Brief announcements: { $status }
pref-changed-brief-announcements = Brief announcements { $status }.
pref-desc-brief-announcements = Shorten in-game move and event announcements; turn off for fuller spoken commentary.
pref-category-sounds = Sounds
pref-category-gameplay = Gameplay
pref-category-dice = Dice
pref-default = Default
pref-per-game-for = { $game }: { $value }
pref-reset-all = Reset all game options
pref-reset-category = Reset { $category } options
pref-reset-done = Game options reset.
pref-set-play-turn-sound = Turn sound: { $status }
pref-set-confirm-destructive-actions = Confirm risky actions: { $status }
pref-set-allow-custom-bot-names = Custom bot names: { $status }
pref-set-clear-kept-on-roll = Clear kept dice when rolling: { $status }
pref-set-dice-keeping-style = Dice keeping style: { $choice }
pref-changed-play-turn-sound = Turn sound { $status }.
pref-changed-confirm-destructive-actions = Confirm risky actions { $status }.
pref-changed-allow-custom-bot-names = Custom bot names { $status }.
pref-changed-clear-kept-on-roll = Clear kept dice when rolling { $status }.
pref-changed-dice-keeping-style = Dice keeping style set to { $choice }.
pref-desc-play-turn-sound = Play a sound when it becomes your turn.
pref-desc-confirm-destructive-actions = Ask for confirmation before risky or irreversible actions, such as passing in Pusoy Dos.
pref-desc-allow-custom-bot-names = Let you set custom names for bots you add to a table.
pref-desc-clear-kept-on-roll = In supported dice games such as Yahtzee, release every kept die after each roll. Your next roll rerolls all dice unless you keep some again; with Dice values, use Shift+1-6 to keep matching dice.
pref-desc-dice-keeping-style = Dice indexes: use 1-5, or 1-6 in Midnight, to toggle dice by position. Dice values: use 1-6 to release one kept die with that face value and Shift+1-6 to keep one matching released die. During Tradeoff's trading phase, 1-6 keeps one matching die and Shift+1-6 marks one for trading; during the taking phase, plain 1-6 takes a matching die from the pool.

cancel = Cancel
no-bot-names-available = No bot names available.
enter-bot-name = Enter bot name
bot-name-invalid-length = Bot names must be 3 to 30 characters.
bot-name-invalid-characters = Bot names can only contain letters, numbers, and spaces.
bot-name-already-used = A player or bot with this name is already at this table.
bot-name-registered-account = This name belongs to a registered account. Please choose a different bot name.
table-name-already-used = A player or bot with this name is already at this table.
no-options-available = No options available.
no-scores-available = No scores available.

option-desc-generic = { $label }. Default: { $default }.
option-desc-integer = { $label }. Enter a whole number from { $min } to { $max }. Default: { $default }.
option-desc-number = { $label }. Enter a number from { $min } to { $max }. Default: { $default }.
option-desc-menu = { $label }. Choose one of: { $choices }. Default: { $default }.
option-desc-bool = { $label }. Activate this item to switch the setting on or off. Default: { $default }.
option-desc-multiselect = { $label }. Selected now: { $selected }. Minimum selections: { $min }. Maximum selections: { $max }. Selected by default: { $default }.
option-desc-no-choices = no choices are currently available
option-desc-none-selected = none
option-desc-no-maximum = no maximum

general-desc-profile = View and edit your public profile details.
general-desc-friends = Manage friends, friend requests, private messages, and friend table actions.
general-desc-my-stats = Review your wins, losses, ratings, and supported game statistics.
general-desc-general-options = Adjust account-wide language, audio, accessibility, and notification settings.
general-desc-game-options = Adjust gameplay preferences that can apply globally or to supported games.
general-desc-language = Choose the language used by server menus, messages, and documentation when available.
general-desc-audio = Adjust music, sound effects, ambience, voice chat volume, typing sounds, and desktop input device settings.
general-desc-accessibility = Adjust accessibility-related reading, input, and client behavior available on this device.
general-desc-notifications = Choose which chat, presence, and table creation notifications you want to hear.
general-desc-music-volume = Change background music volume. Setting it to Off silences music.
general-desc-sound-volume = Change game sound effect volume. Sound effects stay at least ten percent so important cues remain audible.
general-desc-ambience-volume = Change background ambience volume. Setting it to Off silences ambience.
general-desc-voice-volume = Change table voice chat playback volume.
general-desc-audio-input-device = Choose the microphone or input device used by the desktop client for voice chat.
general-desc-play-typing-sounds = Play small typing sounds while entering text in client edit fields.
general-desc-web-speech-settings = Configure browser speech output, including ARIA live or Web Speech mode, speech speed, and voice.
general-desc-mobile-speech-settings = Configure mobile text-to-speech engine, voice, and speech speed.
general-desc-invert-multiline-enter = Swap the send and newline behavior for multiline text fields on the desktop client.
general-desc-mute-global-chat = Stop global chat messages from being spoken automatically.
general-desc-mute-table-chat = Stop table chat messages from being spoken automatically.
general-desc-notify-user-presence = Announce when users come online or go offline.
general-desc-notify-friend-presence = Announce when your friends come online or go offline.
general-desc-notify-table-created = Announce when a new public table is created.
general-desc-speech-mode = Choose whether the web client sends announcements to the screen reader through ARIA live or speaks them with the browser's Web Speech API.
general-desc-speech-rate = Change the web client's speech speed.
general-desc-speech-voice = Choose the voice used by the web client's Web Speech API, or return to the browser default.
general-desc-mobile-tts-engine = Choose the mobile text-to-speech engine. Android currently uses the system-managed engine.
general-desc-mobile-tts-voice = Choose the mobile text-to-speech voice, or return to the system default.
general-desc-mobile-tts-rate = Change the mobile text-to-speech speed.

saved-tables = Saved Tables
no-saved-tables = You have no saved tables.
no-active-tables = No active tables.
no-active-tables-all = No active tables available.
no-active-tables-waiting = No waiting tables available.
no-active-tables-playing = No playing tables available.
active-tables-filter = Filter: { $filter }
filter-name-all = All
filter-name-waiting = Waiting
filter-name-playing = Playing
game-category-filter = Category: { $category }
game-category-filter-option = { $category } ({ $count })
game-category-all = All
game-category-cards = Card Games
game-category-poker = Poker Games
game-category-dice = Dice Games
game-category-board = Board Games
game-category-arcade = Arcade Games
game-category-misc = Miscellaneous
no-games-in-category = No games available in this category.
restore-table = Restore
delete-saved-table = Delete
saved-table-deleted = Saved table deleted.
missing-players = Cannot restore: these players are not available: { $players }
table-restored = Table restored! All players have been transferred.
table-saved-destroying = Table saved! Returning to main menu.
game-type-not-found = Game type no longer exists.

action-not-your-turn = It's not your turn.
action-not-playing = The game hasn't started.
action-spectator = Spectators cannot do this.
action-not-host = Only the host can do this.
action-not-available = That action isn't available right now.
action-game-in-progress = Cannot do this while the game is in progress.
action-need-more-players = Need more players to start.
action-table-full = The table is full.
action-start-needs-more-players = Cannot start. Active players: { $current }. Minimum required: { $minimum }.
action-start-has-too-many-players = Cannot start. Active players: { $current }. Maximum allowed: { $maximum }.
action-start-requires-exact-players = Cannot start. Active players: { $current }. Required: exactly { $required }.
action-no-bots = There are no bots to remove.
action-bots-cannot = Bots cannot do this.
action-no-scores = No scores available yet.

options-category-audio = Audio
options-category-accessibility = Accessibility
options-category-notifications = Notifications
options-category-game = Game

music-volume-option = Music Volume: { $value }%
sound-volume-option = Sound Effects Volume: { $value }%
ambience-volume-option = Ambience Volume: { $value }%
voice-volume-option = Voice Chat Volume: { $value }%
volume-choice-off = Off
volume-choice-percent = { $value }%
volume-choice-current = { $label } (current)
audio-input-device-option = Audio Input Device: { $device }
audio-input-device-default = System Default Input Device

mute-global-chat-option = Mute Global Chat: { $status }
mute-table-chat-option = Mute Table Chat: { $status }
invert-multiline-enter-option = Invert Enter Key Behavior: { $status }
play-typing-sounds-option = Play Typing Sounds: { $status }
enter-music-volume = Enter music volume (0-100)
enter-ambience-volume = Enter ambience volume (0-100)
enter-voice-volume = Enter voice chat volume (10-100)
invalid-volume = Invalid volume.

dice-not-rolled = You haven't rolled yet.
dice-no-dice = No dice available.
table-no-players = No players.
table-players-one = { $count } player: { $players }.
table-players-many = { $count } players: { $players }.
table-spectators = Spectators: { $spectators }.
table-host-suffix = (Host)
table-voice-chat-suffix = (in voice chat)
table-members-summary = Table summary: { $total } { $total ->
    [one] seat
   *[other] seats
}; { $real } { $real ->
    [one] real person
   *[other] real people
}, { $bots } { $bots ->
    [one] bot
   *[other] bots
}; { $active } active, { $spectators } spectating.
table-members-empty = No table members are currently listed. Use Back to return and refresh the table view.
table-member-entry = { $player }: { $status }
table-member-status-host = Host
table-member-status-player = Player
table-member-status-spectator = Spectator
table-member-status-bot = Bot
table-member-status-online = Online
table-member-status-offline = Offline
table-member-status-voice-chat = in voice chat
table-member-status-bot-takeover = bot playing on their behalf: { $bot }
table-member-no-actions = No available actions for { $player }.
table-member-left = That person is no longer at this table.
table-member-bot-left = That bot is no longer at this table.
game-over = Game Over
game-final-scores = Final Scores
game-points = { $count } { $count ->
    [one] point
   *[other] points
}

leaderboards = Leaderboards
leaderboard-no-data = No leaderboard data yet for this game.

leaderboard-type-wins = Win Leaders
leaderboard-type-rating = Skill Rating
leaderboard-type-total-score = Total Score
leaderboard-type-high-score = High Score
leaderboard-type-games-played = Games Played
leaderboard-type-avg-points-per-turn = Avg Points Per Turn
leaderboard-type-best-single-turn = Best Single Turn
leaderboard-type-score-per-round = Score Per Round
leaderboard-type-most-enemies-defeated = Most Enemies Defeated
leaderboard-type-deepest-wave-reached = Deepest Wave Reached


leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] win
   *[other] wins
} { $losses } { $losses ->
    [one] loss
   *[other] losses
}, { $percentage }% winrate
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-games-entry = { $rank }. { $player }: { $value } games
leaderboard-avg-entry = { $rank }. { $player }: { $value }

leaderboard-no-player-stats = You haven't played this game yet.

leaderboard-no-ratings = No rating data yet for this game.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } rating ({ $mu } ± { $sigma })
leaderboard-no-player-rating = You don't have a rating for this game yet.

my-stats = My Stats
my-stats-select-game = Select a game to view your stats
my-stats-no-data = You haven't played this game yet.
my-stats-no-games = You haven't played any games yet.
my-stats-header = { $game } - Your Stats
my-stats-wins = Wins: { $value }
my-stats-losses = Losses: { $value }
my-stats-winrate = Win rate: { $value }%
my-stats-games-played = Games played: { $value }
my-stats-total-score = Total score: { $value }
my-stats-high-score = High score: { $value }
my-stats-rating = Skill rating: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = No skill rating yet
my-stats-avg-per-turn = Avg points per turn: { $value }
my-stats-best-turn = Best single turn: { $value }
my-stats-score-per-round = Score per round: { $value }
my-stats-most-enemies-defeated = Most Enemies Defeated: { $value }
my-stats-deepest-wave-reached = Deepest Wave Reached: { $value }

predict-outcomes = Predict outcomes
predict-header = Predicted Outcomes (by skill rating)
predict-note-multiplayer = Win percentages are shown only for 2-player matches. With 3 or more human players, only skill ratings are shown.
predict-entry = { $rank }. { $player } (rating: { $rating })
predict-entry-2p = { $rank }. { $player } (rating: { $rating }, { $probability }% win chance)
predict-unavailable = Rating predictions are not available.
predict-need-players = Need at least 2 human players for predictions.
action-need-more-humans = Need more human players.
confirm-leave-game = Are you sure you want to leave the table?
confirm-yes = Yes
confirm-no = No

administration = Administration

account-approval = Account Approval
no-pending-accounts = No pending accounts.
approve-account = Approve
decline-account = Decline
account-approved = { $player }'s account has been approved.
account-declined = { $player }'s account has been declined and deleted.

waiting-for-approval = Your account is waiting for approval by an administrator. Please wait...
account-approved-welcome = Your account has been approved! Welcome to PlayAural!
account-declined-goodbye = Your account request has been declined.

account-request = account request
account-action = account action taken

promote-admin = Promote Admin
demote-admin = Demote Admin
ban-user = Ban User
unban-user = Unban User
no-users-to-promote = No users available to promote.
no-admins-to-demote = No admins available to demote.
admin-search-users = Search by username
admin-search-users-current = Search by username. Current search: { $query }.
admin-search-prompt = Enter all or part of a username to search. Leave blank to browse all results by page.
menu-page-summary = Showing { $start }-{ $end } of { $total } entries. Page { $page } of { $pages }.
menu-page-summary-query = Search "{ $query }": showing { $start }-{ $end } of { $total } entries. Page { $page } of { $pages }.
menu-page-refresh = Refresh list
menu-list-refreshed = List refreshed.
menu-page-first = First page
menu-page-previous = Previous page
menu-page-next = Next page
menu-page-last = Last page
admin-search-no-results = No matching users found. Use Search by username to try a different term.
confirm-promote = Are you sure you want to promote { $player } to admin?
confirm-demote = Are you sure you want to demote { $player } from admin?
broadcast-to-all = Announce to all users
broadcast-to-admins = Announce to admins only
broadcast-to-nobody = Silent (no announcement)
promote-announcement = { $player } has been promoted to admin!
promote-announcement-you = You have been promoted to admin!
demote-announcement = { $player } has been demoted from admin.
demote-announcement-you = You have been demoted from admin.
not-admin-anymore = You are no longer an admin and cannot perform this action.
dev-only-action = This action is restricted to Developers only.

ban-duration-1h = 1 hour
ban-duration-6h = 6 hours
ban-duration-12h = 12 hours
ban-duration-1d = 1 day
ban-duration-3d = 3 days
ban-duration-1w = 1 week
ban-duration-1m = 1 month
ban-duration-permanent = Permanent

reason-spam = Spam
reason-harassment = Harassment
reason-cheating = Cheating
reason-inappropriate = Inappropriate behavior
reason-custom = Other / Custom

no-users-to-ban = No users available to ban.
no-banned-users = No users are currently banned.
admin-active-ban-entry = { $username }. Ban expiration: { $expires }. Reason: { $reason }. Issued by: { $admin }.
admin-active-mute-entry = { $username }. Mute expiration: { $expires }. Reason: { $reason }. Issued by: { $admin }.
admin-penalty-expiry-permanent = permanent
admin-penalty-expiry-unknown = unknown expiration
admin-penalty-expiry-expired = already expired
admin-penalty-expiry-timed = { $date } ({ $remaining } remaining)
admin-penalty-reason-unknown = unspecified reason
admin-penalty-admin-unknown = unknown administrator
admin-penalty-remaining-days = { $count ->
    [one] 1 day
   *[other] { $count } days
}
admin-penalty-remaining-hours = { $count ->
    [one] 1 hour
   *[other] { $count } hours
}
admin-penalty-remaining-minutes = { $count ->
    [one] 1 minute
   *[other] { $count } minutes
}
admin-penalty-remaining-less-minute = less than 1 minute

ban-broadcast = { $target } has been banned by { $actor } for { $reason }. Duration: { $duration }.
unban-broadcast = { $target } has been unbanned by { $actor }.

banned-menu-title = Account Banned
banned-reason = Reason: { $reason }
banned-expires = Expires: { $expires }
banned-permanent = Expires: Permanent
disconnect = Disconnect


mute-user = Mute User
unmute-user = Unmute User
no-users-to-mute = No users available to mute.
no-muted-users = No users are currently muted.
mute-duration-5m = 5 minutes
mute-duration-15m = 15 minutes
mute-duration-30m = 30 minutes
mute-duration-1h = 1 hour
mute-duration-6h = 6 hours
mute-duration-1d = 1 day
mute-duration-permanent = Permanent
mute-broadcast = { $target } has been muted by { $actor } for { $reason }. Duration: { $duration }.
unmute-broadcast = { $target } has been unmuted by { $actor }.
you-have-been-muted = You have been muted. Reason: { $reason }. Duration: { $duration }.
you-have-been-unmuted = You have been unmuted. You can chat again.
muted-remaining-seconds = You are muted. { $seconds } seconds remaining.
muted-remaining-minutes = You are muted. { $minutes } minutes remaining.
muted-permanent = You are permanently muted. Contact an administrator for more information.
auto-muted-seconds = You have been temporarily muted for spamming. { $seconds } seconds remaining.
auto-muted-minutes = You have been temporarily muted for spamming. { $minutes } minutes remaining.
auto-muted-applied-seconds = You have been auto-muted for { $seconds } seconds due to excessive chat spam.
auto-muted-applied-minutes = You have been auto-muted for { $minutes } minutes due to excessive chat spam.
chat-rate-limited = Slow down! You are sending messages too quickly.
chat-global-disabled-send = Global chat is disabled in your options. Turn global chat back on before sending global messages.
chat-table-disabled-send = Table chat is disabled in your options. Turn table chat back on before sending table messages.
admin-spam-alert = Warning: { $username } is spamming chat excessively and has been auto-muted.

broadcast-announcement = Broadcast Announcement
admin-broadcast-prompt = Enter the message to broadcast to all online users. (This will be sent to everyone!)
admin-broadcast-sent = Broadcast sent to { $count } users.

manage-motd = Manage MOTD
create-update-motd = Create/Update MOTD
view-motd = View Active MOTD
delete-motd = Delete MOTD
motd-version-prompt = Enter the new MOTD Version number (must be > 0):
invalid-motd-version = Invalid MOTD version. It must be a positive number.
motd-created = MOTD version { $version } has been successfully created.
motd-deleted = MOTD has been deleted.
motd-delete-empty = There is no active MOTD to delete.
motd-not-exists = No active MOTD exists.
motd-announcement = Message of the Day
motd-broadcast = New Message of the Day: { $message }
error-no-languages = Error: No languages found.
ok = OK

admin-localized-text-subject-motd = Message of the Day
admin-localized-text-subject-power = server power reason
admin-localized-text-subject-ban = custom ban reason
admin-localized-text-subject-mute = custom mute reason
admin-localized-text-instructions = Edit the { $subject } translations. Official languages are required. Community languages are optional and use { $fallback } when empty.
admin-localized-text-motd-version = MOTD version: { $version }
admin-localized-text-official-heading = Official languages, required
admin-localized-text-community-heading = Community languages, optional
admin-localized-text-field = { $language }: { $status }
admin-localized-text-required-set = entered, required
admin-localized-text-required-missing = not entered, required
admin-localized-text-optional-set = entered, optional
admin-localized-text-optional-fallback = not entered, optional, uses fallback
admin-localized-text-prompt = Enter the { $subject } in { $language }. Maximum { $max } characters.
admin-localized-text-too-long = That translation is too long. The maximum is { $max } characters.
admin-localized-text-missing-required = Enter all required translations first. Missing: { $languages }.
admin-localized-text-publish-motd = Publish MOTD
admin-localized-text-continue = Continue
admin-localized-text-apply-ban = Apply ban
admin-localized-text-apply-mute = Apply mute

unknown-player = Unknown player

logout-confirm-title = Are you sure you want to logout and exit the game?
logout-confirm-yes = Yes, logout
logout-confirm-no = No, stay

system-name = System
server-restarting = Server is restarting in { $seconds } seconds...
server-restarting-now = Server is restarting now. Please reconnect shortly.
server-shutting-down = Server is shutting down in { $seconds } seconds...
server-shutting-down-now = Server is shutting down now. Goodbye!
server-power-management = Server Power Management
server-power-reboot = Reboot Server
server-power-shutdown = Shutdown Server
server-power-cancel = Cancel Scheduled Power Action
server-power-active-status = Scheduled { $action }. Reason: { $reason }.
server-power-action-reboot = reboot
server-power-action-shutdown = shutdown
server-power-delay-30s = In 30 seconds
server-power-delay-1m = In 1 minute
server-power-delay-5m = In 5 minutes
server-power-delay-10m = In 10 minutes
server-power-delay-30m = In 30 minutes
server-power-delay-1h = In 1 hour
server-power-delay-2h = In 2 hours
server-power-delay-custom = Custom delay in minutes
server-power-custom-delay-prompt = Enter the delay in minutes, from 1 to { $max }:
server-power-invalid-custom-delay = Invalid delay. Enter a whole number of minutes from 1 to { $max }.
server-power-reason-update = Update
server-power-reason-maintenance = Maintenance
server-power-reason-security = Security
server-power-reason-technical = Technical issue
server-power-reason-custom = Custom reason
server-power-reason-unspecified = unspecified reason
server-power-confirm-summary = Confirm server { $action } in { $duration }. Reason: { $reason }.
server-power-scheduled = Scheduled server { $action } in { $duration }.
server-power-already-scheduled = A server power action is already scheduled. Cancel it before scheduling another.
server-power-cancel-none = No server power action is currently scheduled.
server-power-cancelled = Scheduled server power action cancelled.
server-power-cancelled-broadcast = { $admin } cancelled the scheduled server { $action }.
server-power-command-removed = The /reboot and /stop chat commands have been removed. Use Administration, Server Power Management instead.
server-power-finalizing-input-blocked = The server is finalizing a reboot or shutdown. Please wait for the client to disconnect.
server-power-finalize-failed = The scheduled server { $action } could not finish safely. The server is staying online; please contact an administrator.
server-power-reboot-warning = Server reboot in { $duration }. Reason: { $reason }. Do not disconnect manually; your client will reconnect automatically, and active tables will be preserved.
server-power-shutdown-warning = Server shutdown in { $duration }. Reason: { $reason }. The server is going offline; save any games you want to keep before the shutdown.
server-power-reboot-now = Server is rebooting now. Reason: { $reason }. Do not disconnect manually; your client will reconnect automatically, and active tables will be preserved.
server-power-shutdown-now = Server is shutting down now. Reason: { $reason }. The server is going offline.
server-power-restore-waiting = This table was restored after a planned reboot. Waiting up to { $seconds } seconds for the other players to reconnect before replacing missing seats with bots.
server-power-restore-input-blocked = This table is still recovering from the planned reboot. Gameplay is paused for up to { $seconds } more seconds while waiting for { $players }; please try again after the grace period ends.
server-power-restore-missing-players-fallback = the remaining players
server-power-restore-complete = All active players have reconnected after the planned reboot. Game resumed.
server-power-restore-complete-with-bots = Reconnect grace ended after the planned reboot. Missing seats were replaced with bots, and the game is resuming.
duration-seconds = { $count ->
    [one] 1 second
   *[other] { $count } seconds
}
duration-minutes = { $count ->
    [one] 1 minute
   *[other] { $count } minutes
}
duration-hours = { $count ->
    [one] 1 hour
   *[other] { $count } hours
}
duration-minutes-seconds = { $minutes } minutes and { $seconds } seconds
duration-hours-minutes = { $hours } hours and { $minutes } minutes
server-error-changing-language = Error changing language: { $error }
default-save-name = { $game } - { $date }

speech-settings = Speech Settings
speech-mode-option = Speech Mode: { $status }
speech-rate-option = Speech Rate: { $value }%
speech-voice-option = Voice: { $voice }
select-voice = Select Voice
enter-speech-rate = Enter speech rate (50-300)
invalid-rate = Invalid speech rate. Use a value between 50 and 300.
mode-aria = Aria-live
mode-web-speech = Web Speech API
default-voice = Default Voice
mobile-speech-settings = Mobile Speech Settings
mobile-tts-engine-option = TTS Engine: { $engine }
mobile-tts-engine-system = System default
mobile-tts-engine-system-selected = System default TTS engine
mobile-tts-engine-api-note = Android engine selection is managed by system settings in this build.
mobile-tts-voice-option = Mobile Voice: { $voice }
mobile-tts-rate-option = Mobile Speech Rate: { $value }%
mobile-tts-enter-rate = Enter mobile speech rate (50-200)
mobile-tts-invalid-rate = Invalid mobile speech rate. Use a value between 50 and 200.

player-kicked-offline = Player { $player } has been kicked (offline).
game-paused-host-disconnect = Game paused. Waiting for { $player } to reconnect...
game-resumed = { $player } reconnected. Game resumed!

auth-error-username-length = Username must be between 3 and 30 characters.
auth-error-username-invalid-chars = Username may only contain letters, numbers, and spaces (no consecutive spaces, and no special characters).
auth-error-password-weak = Password must be at least 8 characters long and contain both letters and numbers.

personal-and-options = Personal and Options
profile = Profile
friends = Friends
profile-registration-date = Registration Date: { $date }
profile-username = Username: { $username }
profile-email = Email: { $email }
admin-view-email = Admin View - Email: { $email }
profile-gender = Gender: { $gender }
profile-bio = Bio: { $bio }
profile-bio-empty = Not set
profile-email-empty = Not set

gender-male = Male
gender-female = Female
gender-non-binary = Non-binary
gender-not-set = Not set

action-set-edit = Set / Edit
action-delete = Delete
bio-already-empty = Bio is already empty.
bio-deleted = Bio deleted.
bio-updated = Bio updated.

enter-email = Enter new email address:
email-updated = Email address updated.
enter-bio = Enter your bio:

gender-updated = Gender updated.
no-changes-made = No changes made.
confirm-email-change = Are you sure you want to change your email to { $email }?

mandatory-email-notice = You must set an email to continue participating. Your email is private and only known to you.
error-email-empty = Email is mandatory and cannot be empty.
error-email-invalid = Invalid email format. Please provide a valid email address.
reg-error-email = Email is required to register.

error-email-taken = This email is already in use by another account.

error-bio-length = Bio must not exceed 250 characters.
error-captcha-failed = Verification failed. Please try again.
error-rate-limit-login = Too many failed login attempts. Please try again in 15 minutes.
error-rate-limit-register = You have reached the maximum number of account registrations for today.
auth-error-rate-limit = { error-rate-limit-login }

friends-my-friends = My Friends
friends-pending-requests = Pending Requests ({ $count })
friends-no-pending-requests = Pending Requests
friends-send-request = Send Friend Request
friends-list-empty = You have no friends yet.
friend-status-offline = Offline
friend-status-playing = Playing { $game }
friend-status-spectating = Spectating { $game }
friend-status-lobby = Main menu
friend-list-entry = { $username } ({ $status })

friend-actions-title = Actions for { $username }
view-profile = View Profile
join-table = Join Table
remove-friend = Remove Friend
friend-remove-confirm = Remove { $username } from your friends list?
friend-remove-not-friends = { $username } is no longer in your friends list.
already-in-table = You are already in this table.
friend-removed-success = { $username } has been removed from your friends list.
friend-removed-notify = { $username } has removed you from their friends list.

no-pending-requests = No pending requests.
friend-request-from = Friend request from { $username }
accept = Accept
decline = Decline
friend-accepted-success = You are now friends with { $username }.
friend-accepted-notify = { $username } has accepted your friend request!
request-not-found = Friend request no longer exists.
friend-declined-success = Friend request declined.
friend-declined-notify = { $username } declined your friend request.

public-profile-title = { $username }'s Profile
enter-friend-username = Enter the username of the person you want to friend:
friend-error-self = You cannot send a friend request to yourself.
friend-error-already-friends = You are already friends with this user.
friend-error-duplicate = You already have a pending friend request to this user.
friend-request-sent = Friend request sent to { $username }.
friend-request-received = You have received a new friend request from { $username }.

friends-grouped-requests = You have pending friend requests from: { $usernames }
friends-grouped-accepted = Your friend requests were accepted by: { $usernames }
friends-grouped-declined = Your friend requests were declined by: { $usernames }
friends-grouped-removed = You were removed from the friends list by: { $usernames }
friends-and-others = { $names } and { $count } { $count ->
    [one] other
   *[other] others
}

send-private-message = Send Private Message
enter-pm-message = Enter your message for { $username }:
pm-error-not-friends = You can only send private messages to friends.
pm-error-offline = { $username } is not currently online.
pm-sent-success = Message sent to { $username }.
pm-sent-content = You to { $username }: { $message }
pm-received = Private message from { $username }: { $message }

host-management = Host Management
table-spectator-suffix = (Spectator)
host-management-set-private = Set Table to Private
host-management-set-public = Set Table to Public
host-management-invite = Invite a Friend
host-management-pass-host = Pass Host to Another Player
host-management-kick = Kick a Player
host-management-kick-ban = Kick and Ban a Player
host-management-restart-game = Restart Game
host-management-table-now-private = This table is now private. Only invited players can join.
host-management-table-now-public = This table is now public.
host-restart-confirm = Restart the current game and return this table to the waiting room? Current players and voice chat will stay connected, but the current match will be cancelled.
host-restart-broadcast = { $player } restarted the game. The table is back in the waiting room.
host-restart-not-playing = There is no active game to restart.
host-invite-no-friends = (No friends available to invite)
host-invite-sent = Invite sent to { $player }.
host-invite-friend-unavailable = That friend is not currently online.
host-invite-already-pending = An invite is already pending for that friend.
host-invite-friend-busy = That friend is already in a game.
host-invite-declined = { $player } declined your table invite.
table-invite-received = { $host } has invited you to their { $game } table.
table-invite-queued = { $host } invited you to their { $game } table. Finish your current input to respond.
table-invite-expired = The table invite has expired.
invite-accept = Accept Invite
invite-decline = Decline Invite
host-management-no-longer-host = You are no longer the host of this table.
host-pass-no-candidates = (No players available to pass host to)
host-pass-no-longer-host = You passed host to another player. You are no longer the host of this table.
host-passed = { $player } is now the host.
host-pass-failed = Failed to transfer host. The player may have left.
host-kick-no-candidates = (No players available to kick)
host-kick-invalid-target = Invalid kick target.
host-kick-broadcast = { $player } has been kicked from the table.
host-kick-ban-broadcast = { $player } has been kicked and banned from the table.
host-kick-you = You have been kicked from the table by { $host }.
host-kick-ban-you = You have been kicked and banned from the table by { $host }.
table-you-are-banned = You are banned from this table.
table-private-invite-only = This table is private. You must receive an invite from the host to join.

voice-room-table-label = { $game } table voice
voice-unavailable = Voice chat is not available right now.
voice-invalid-context = That voice room request is invalid.
voice-not-at-table = You have not joined a table yet. Join a table before starting voice chat.
voice-not-in-context = You must be at that table before joining its voice chat.
voice-rate-limited = Slow down. Voice chat is changing too quickly right now.
voice-muted-seconds = You are muted and cannot join voice chat. { $seconds } seconds remaining.
voice-muted-minutes = You are muted and cannot join voice chat. { $minutes } minutes remaining.
voice-muted-permanent = You are muted and cannot join voice chat.
voice-status-connected = { $player } connected to the table's voice chat.
voice-status-disconnected = { $player } disconnected from the voice chat.
voice-status-connection-lost = { $player } lost connection and was removed from the voice chat.
voice-status-left-table = { $player } left the table and left the voice chat.

error-smtp-not-configured = Password recovery is currently disabled by the administrator.
error-email-not-found = No account found with that email address.
success-reset-email-sent = A reset code has been sent to your email address.
error-smtp-send-failed = Failed to send the reset email. Please try again later.
error-invalid-reset-code = Invalid or expired reset code.
success-password-reset = Your password has been successfully reset. You can now log in.
