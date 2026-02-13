# Main UI messages for PlayAural

# Game categories
category-card-games = Card Games
category-dice-games = Dice Games
category-board-games = Board Games
category-rb-play-center = RB Play Center
category-poker = Poker
category-uncategorized = Uncategorized

# Authentication
auth-username-password-required = Username and password are required.
auth-registration-success = Registration successful! You can now log in with your credentials.
auth-username-taken = Username already taken. Please choose a different username.
auth-error-wrong-password = Incorrect password.
auth-error-user-not-found = User does not exist.
chat-language-english = English
chat-global = { $player } says globally: { $message }
dev-announcement-broadcast = { $dev } is a developer of PlayAural.
admin-announcement-broadcast = { $admin } is an administrator of PlayAural.

# Menu titles
main-menu-title = Main Menu
play-menu-title = Play
categories-menu-title = Game Categories
tables-menu-title = Available Tables

# Menu items
play = Play
view-active-tables = View active tables
options = Options
logout = Logout
back = Back
go-back = Go back
context-menu = Context menu.
no-actions-available = No actions available.
create-table = Create a new table
join-as-player = Join as player
join-as-spectator = Join as spectator
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

# Turn messages
game-player-skipped = { $player } is skipped.

# Table messages
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
player-rejoined = { $player } has rejoined the game.
spectator-joined = Joined { $host }'s table as a spectator.

# Spectator mode
spectate = Spectate
now-playing = { $player } is now playing.
now-spectating = { $player } is now spectating.
spectator-left = { $player } stopped spectating.

# General
welcome = Welcome to PlayAural!
goodbye = Goodbye!

# User presence announcements
user-online = { $player } came online.
user-offline = { $player } went offline.
user-is-admin = { $player } is an administrator of PlayAural.
user-is-dev = { $player } is the Developer of PlayAural.
permission-denied = You do not have permission to perform this action on a Developer.
kick-user = Kick User
kick-broadcast = { $target } was kicked by { $actor }.
you-were-kicked = You have been kicked by { $actor }.
user-not-online = User { $target } is not online.
kick-immune = You cannot kick this user.
kick-confirm = Are you sure you want to kick { $player }?
kick-menu-title = Kick User
kick-confirm-menu-title = Confirm Kick User
no-users-to-kick = No users available to kick.
usage-kick = Usage: /kick <username>
online-users-none = No users online.
online-users-one = 1 user: { $users }
online-users-many = { $count } users: { $users }
online-user-not-in-game = Not in game
online-user-waiting-approval = Waiting for approval

# Options
language = Language
language-option = Language: { $language }
language-changed = Language set to { $language }.

# Boolean option states
option-on = On
option-off = Off

# Sound options
turn-sound-option = Turn sound: { $status }

# Dice options
clear-kept-option = Clear kept dice when rolling: { $status }
option-notify-table-created-on = Notify when table created: On
option-notify-table-created-off = Notify when table created: Off
dice-keeping-style-option = Dice keeping style: { $style }
dice-keeping-style-changed = Dice keeping style set to { $style }.
dice-keeping-style-indexes = Dice indexes
dice-keeping-style-values = Dice values

# Bot names
cancel = Cancel
no-bot-names-available = No bot names available.
select-bot-name = Select a name for the bot
enter-bot-name = Enter bot name
no-options-available = No options available.
no-scores-available = No scores available.

# Duration estimation
estimate-duration = Estimate duration
estimate-computing = Computing estimated game duration...
estimate-result = Bot average: { $bot_time } (± { $std_dev }). { $outlier_info }Estimated human time: { $human_time }.
estimate-error = Could not estimate duration.
estimate-already-running = Duration estimation already in progress.

# Save/Restore
saved-tables = Saved Tables
no-saved-tables = You have no saved tables.
no-active-tables = No active tables.
restore-table = Restore
delete-saved-table = Delete
saved-table-deleted = Saved table deleted.
missing-players = Cannot restore: these players are not available: { $players }
table-restored = Table restored! All players have been transferred.
table-saved-destroying = Table saved! Returning to main menu.
game-type-not-found = Game type no longer exists.

# Action disabled reasons
action-not-your-turn = It's not your turn.
action-not-playing = The game hasn't started.
action-spectator = Spectators cannot do this.
action-not-host = Only the host can do this.
action-game-in-progress = Cannot do this while the game is in progress.
action-need-more-players = Need more players to start.
action-table-full = The table is full.
action-no-bots = There are no bots to remove.
action-bots-cannot = Bots cannot do this.
action-no-scores = No scores available yet.

# Enhanced Options
music-volume-option = Music Volume: { $value }%
ambience-volume-option = Ambience Volume: { $value }%
mute-global-chat-option = Mute Global Chat: { $status }
mute-table-chat-option = Mute Table Chat: { $status }
invert-multiline-enter-option = Invert Enter Key Behavior: { $status }
play-typing-sounds-option = Play Typing Sounds: { $status }
enter-music-volume = Enter music volume (0-100)
enter-ambience-volume = Enter ambience volume (0-100)
invalid-volume = Invalid volume. Please enter a number between 0 and 100.

# Dice actions
dice-not-rolled = You haven't rolled yet.
dice-locked = This die is locked.
dice-no-dice = No dice available.

# Game actions
game-turn-start = { $player }'s turn.
game-no-turn = No one's turn right now.
table-no-players = No players.
table-players-one = { $count } player: { $players }.
table-players-many = { $count } players: { $players }.
table-spectators = Spectators: { $spectators }.
game-leave = Leave
game-over = Game Over
game-final-scores = Final Scores
game-points = { $count } { $count ->
    [one] point
   *[other] points
}
status-box-closed = Closed.
play = Play

# Leaderboards
leaderboards = Leaderboards
leaderboards-menu-title = Leaderboards
leaderboards-select-game = Select a game to view its leaderboard
leaderboard-no-data = No leaderboard data yet for this game.

# Leaderboard types
leaderboard-type-wins = Win Leaders
leaderboard-type-rating = Skill Rating
leaderboard-type-total-score = Total Score
leaderboard-type-high-score = High Score
leaderboard-type-games-played = Games Played
leaderboard-type-avg-points-per-turn = Avg Points Per Turn
leaderboard-type-best-single-turn = Best Single Turn
leaderboard-type-score-per-round = Score Per Round

# Leaderboard headers
leaderboard-wins-header = { $game } - Win Leaders
leaderboard-total-score-header = { $game } - Total Score
leaderboard-high-score-header = { $game } - High Score
leaderboard-games-played-header = { $game } - Games Played
leaderboard-rating-header = { $game } - Skill Ratings
leaderboard-avg-points-header = { $game } - Avg Points Per Turn
leaderboard-best-turn-header = { $game } - Best Single Turn
leaderboard-score-per-round-header = { $game } - Score Per Round

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] win
   *[other] wins
} { $losses } { $losses ->
    [one] loss
   *[other] losses
}, { $percentage }% winrate
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } avg
leaderboard-games-entry = { $rank }. { $player }: { $value } games

# Player stats
leaderboard-player-stats = Your stats: { $wins } wins, { $losses } losses ({ $percentage }% win rate)
leaderboard-no-player-stats = You haven't played this game yet.

# Skill rating leaderboard
leaderboard-no-ratings = No rating data yet for this game.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } rating ({ $mu } ± { $sigma })
leaderboard-player-rating = Your rating: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = You don't have a rating for this game yet.

# My Stats menu
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

# Prediction system
predict-outcomes = Predict outcomes
predict-header = Predicted Outcomes (by skill rating)
predict-entry = { $rank }. { $player } (rating: { $rating })
predict-entry-2p = { $rank }. { $player } (rating: { $rating }, { $probability }% win chance)
predict-unavailable = Rating predictions are not available.
predict-need-players = Need at least 2 human players for predictions.
action-need-more-humans = Need more human players.
confirm-leave-game = Are you sure you want to leave the table?
confirm-yes = Yes
confirm-no = No

# Administration
administration = Administration
admin-menu-title = Administration

# Account approval
account-approval = Account Approval
account-approval-menu-title = Account Approval
no-pending-accounts = No pending accounts.
approve-account = Approve
decline-account = Decline
account-approved = { $player }'s account has been approved.
account-declined = { $player }'s account has been declined and deleted.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Your account is waiting for approval by an administrator. Please wait...
account-approved-welcome = Your account has been approved! Welcome to PlayAural!
account-declined-goodbye = Your account request has been declined.

# Admin notifications for account requests
account-request = account request
account-action = account action taken

# Admin promotion/demotion
promote-admin = Promote Admin
demote-admin = Demote Admin
promote-admin-menu-title = Promote Admin
demote-admin-menu-title = Demote Admin
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

# Broadcast
broadcast-announcement = Broadcast Announcement
admin-broadcast-prompt = Enter the message to broadcast to all online users. (This will be sent to everyone!)
admin-broadcast-sent = Broadcast sent to { $count } users.

# Mile by Mile Deck Rigging
milebymile-rig-none = None
milebymile-rig-no-duplicates = No Duplicates
milebymile-rig-2x-attacks = 2x Attacks
milebymile-rig-2x-defenses = 2x Defenses
admin-broadcast-sent = Broadcast sent to { $count } users.

# Players
unknown-player = Unknown player

# Logout
logout-confirm-title = Are you sure you want to logout and exit the game?
logout-confirm-yes = Yes, logout
logout-confirm-no = No, stay
goodbye = Goodbye!

# System messages
system-name = System
server-restarting = Server is restarting in { $seconds } seconds...
server-shutting-down = Server is shutting down in { $seconds } seconds...
server-error-changing-language = Error changing language: { $error }
default-save-name = { $game } - { $date }

# Speech Settings (Web)
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

# Auto-kick and Pause notifications
player-kicked-offline = Player { $player } has been kicked (offline).
game-paused-host-disconnect = Game paused. Waiting for host { $player } to reconnect...
game-resumed = Host { $player } reconnected. Game resumed!
new-host = New host: { $player }
