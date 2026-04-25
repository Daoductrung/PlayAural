auth-username-password-required = Username and password are required.
auth-registration-success = Registration successful! You can now log in with your credentials.
auth-username-taken = Username already taken. Please choose a different username.
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
player-replaced-by-bot = { $player } left and was replaced by a bot.
player-reclaimed-from-bot = { $player } reconnected and reclaimed their seat.
player-took-over = { $player } took over from the bot.
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
online-user-not-in-game = Not in game
online-user-waiting-approval = Waiting for approval
user-role-dev = Developer
user-role-admin = Admin
user-role-user = User
client-type-web = Web
client-type-python = Desktop
client-type-mobile = Mobile
online-user-full-entry = { $username } ({ $role }, { $client }, { $language }): { $status }
online-user-actions-title = Actions for { $username }
user-not-online-anymore = This user is no longer online.
close-menu = Close

language = Language
language-option = Language: { $language }
language-changed = Language set to { $language }.

option-on = On
option-off = Off

turn-sound-option = Turn sound: { $status }

custom-bot-names-option = Custom bot names: { $status }
clear-kept-option = Clear kept dice when rolling: { $status }
option-notify-table-created-on = Notify when table created: On
option-notify-table-created-off = Notify when table created: Off
option-notify-user-presence-on = User online/offline notifications: On
option-notify-user-presence-off = User online/offline notifications: Off
option-notify-friend-presence-on = Friend online/offline notifications: On
option-notify-friend-presence-off = Friend online/offline notifications: Off
dice-keeping-style-option = Dice keeping style: { $style }
dice-keeping-style-changed = Dice keeping style set to { $style }.
dice-keeping-style-indexes = Dice indexes
dice-keeping-style-values = Dice values

cancel = Cancel
no-bot-names-available = No bot names available.
enter-bot-name = Enter bot name
bot-name-invalid-length = Bot names must be 3 to 30 characters.
bot-name-invalid-characters = Bot names can only contain letters, numbers, and spaces.
bot-name-already-used = That bot name is already in use at this table.
no-options-available = No options available.
no-scores-available = No scores available.


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
action-no-bots = There are no bots to remove.
action-bots-cannot = Bots cannot do this.
action-no-scores = No scores available yet.

music-volume-option = Music Volume: { $value }%
ambience-volume-option = Ambience Volume: { $value }%
audio-input-device-option = Audio Input Device: { $device }
audio-input-device-default = System Default Input Device
mute-global-chat-option = Mute Global Chat: { $status }
mute-table-chat-option = Mute Table Chat: { $status }
invert-multiline-enter-option = Invert Enter Key Behavior: { $status }
play-typing-sounds-option = Play Typing Sounds: { $status }
enter-music-volume = Enter music volume (0-100)
enter-ambience-volume = Enter ambience volume (0-100)
invalid-volume = Invalid volume. Please enter a number between 0 and 100.

dice-not-rolled = You haven't rolled yet.
dice-locked = This die is locked.
dice-no-dice = No dice available.

game-turn-start = { $player }'s turn.
game-no-turn = No one's turn right now.
table-no-players = No players.
table-players-one = { $count } player: { $players }.
table-players-many = { $count } players: { $players }.
table-spectators = Spectators: { $spectators }.
table-host-suffix = (Host)
table-voice-chat-suffix = (in voice chat)
game-leave = Leave
game-over = Game Over
game-final-scores = Final Scores
game-points = { $count } { $count ->
    [one] point
   *[other] points
}
status-box-closed = Closed.
play = Play

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

ban-broadcast = { $target } has been banned by { $actor } for { $reason }. Duration: { $duration }.
unban-broadcast = { $target } has been unbanned by { $actor }.

banned-menu-title = Account Banned
banned-reason = Reason: { $reason }
banned-expires = Expires: { $expires }
banned-permanent = Expires: Permanent
disconnect = Disconnect

enter-custom-ban-reason = Enter custom ban reason:

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
enter-custom-mute-reason = Enter custom mute reason:
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
motd-prompt = Enter MOTD for { $language } (use Enter for new line, Shift+Enter to submit if multiline inverted):
motd-created = MOTD version { $version } has been successfully created.
motd-cancelled = MOTD creation cancelled.
motd-deleted = MOTD has been deleted.
motd-delete-empty = There is no active MOTD to delete.
motd-not-exists = No active MOTD exists.
motd-announcement = Message of the Day
motd-broadcast = New Message of the Day: { $message }
error-no-languages = Error: No languages found.
ok = OK

milebymile-rig-none = None
milebymile-rig-no-duplicates = No Duplicates
milebymile-rig-2x-attacks = 2x Attacks
milebymile-rig-2x-defenses = 2x Defenses
admin-broadcast-sent = Broadcast sent to { $count } users.

unknown-player = Unknown player

logout-confirm-title = Are you sure you want to logout and exit the game?
logout-confirm-yes = Yes, logout
logout-confirm-no = No, stay
goodbye = Goodbye!

system-name = System
server-restarting = Server is restarting in { $seconds } seconds...
server-restarting-now = Server is restarting now. Please reconnect shortly.
server-shutting-down = Server is shutting down in { $seconds } seconds...
server-shutting-down-now = Server is shutting down now. Goodbye!
server-error-changing-language = Error changing language: { $error }
default-save-name = { $game } - { $date }

speech-settings = Speech Settings
speech-mode-option = Speech Mode: { $status }
speech-rate-option = Speech Rate: { $value }%
speech-voice-option = Voice: { $voice }
select-voice = Select Voice
enter-speech-rate = Enter speech rate (50-300)
invalid-rate = Invalid rate. Please enter a number between 50 and 300.
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
mobile-tts-invalid-rate = Invalid rate. Please enter a number between 50 and 200.

player-kicked-offline = Player { $player } has been kicked (offline).
game-paused-host-disconnect = Game paused. Waiting for host { $player } to reconnect...
game-resumed = Host { $player } reconnected. Game resumed!
new-host = New host: { $player }

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
auth-error-rate-limit = Too many failed login attempts. Please try again in 15 minutes.

friends-my-friends = My Friends
friends-pending-requests = Pending Requests ({ $count })
friends-no-pending-requests = Pending Requests
friends-send-request = Send Friend Request
friends-list-empty = You have no friends yet.
friend-status-offline = Offline
friend-status-playing = Playing { $game }
friend-status-spectating = Spectating { $game }
friend-status-lobby = In Lobby
friend-list-entry = { $username } ({ $status })

friend-actions-title = Actions for { $username }
view-profile = View Profile
join-table = Join Table
remove-friend = Remove Friend
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
host-pass-no-candidates = (No players available to pass host to)
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
