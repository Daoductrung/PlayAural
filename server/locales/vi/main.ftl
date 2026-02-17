# Main UI messages for PlayAural

# Game categories
category-card-games = Game bài
category-dice-games = Game xúc xắc
category-board-games = Game bàn cờ
category-rb-play-center = Trung tâm RB Play
category-poker = Poker
category-uncategorized = Chưa phân loại

# Authentication
auth-username-password-required = Yêu cầu tên đăng nhập và mật khẩu.
auth-registration-success = Đăng ký thành công! Giờ bạn có thể đăng nhập.
auth-username-taken = Tên đăng nhập đã có người dùng. Vui lòng chọn tên khác.
auth-error-wrong-password = Sai mật khẩu.
auth-error-user-not-found = Người dùng không tồn tại.
chat-language-english = Tiếng Anh
chat-global = { $player } nói với tất cả: { $message }
dev-announcement-broadcast = { $dev } là nhà phát triển của PlayAural.
admin-announcement-broadcast = { $admin } là quản trị viên của PlayAural.

# Menu titles
main-menu-title = Menu Chính
play-menu-title = Chơi
categories-menu-title = Các thể loại game
tables-menu-title = Các bàn đang có

# Menu items
play = Chơi
view-active-tables = Xem các bàn đang chơi
options = Tùy chỉnh
logout = Đăng xuất
back = Quay lại
go-back = Quay lại
context-menu = Menu ngữ cảnh.
no-actions-available = Không có hành động nào.
create-table = Tạo bàn mới
join-as-player = Tham gia chơi
join-as-spectator = Tham gia xem
leave-table = Rời bàn
start-game = Bắt đầu game
add-bot = Thêm Bot
remove-bot = Xóa Bot
actions-menu = Menu hành động
save-table = Lưu bàn
whose-turn = Lượt của ai
whos-at-table = Ai đang ở trong bàn
check-scores = Xem điểm
check-scores-detailed = Xem điểm chi tiết

# Turn messages
game-player-skipped = { $player } bị bỏ qua.

# Table messages
table-created = { $host } đã tạo bàn chơi { $game } mới.
table-created-broadcast = { $host } đã tạo bàn chơi { $game } mới.
table-joined = { $player } đã tham gia bàn.
table-left = { $player } đã rời bàn.
new-host = { $player } giờ là chủ bàn.
waiting-for-players = Đang chờ người chơi. Tối thiểu {$min}, tối đa { $max }.
game-starting = Trò chơi bắt đầu!
table-listing = Bàn của { $host } ({ $count } người)
table-listing-one = Bàn của { $host } ({ $count } người)
table-listing-with = Bàn của { $host } ({ $count } người) cùng với { $members }
table-listing-game = { $game }: Bàn của { $host } ({ $count } người)
table-listing-game-one = { $game }: Bàn của { $host } ({ $count } người)
table-listing-game-with = { $game }: Bàn của { $host } ({ $count } người) cùng với { $members }
table-listing-game-status = { $game } [{ $status }]: Bàn của { $host } ({ $count } người)
table-listing-game-one-status = { $game } [{ $status }]: Bàn của { $host } ({ $count } người)
table-listing-game-with-status = { $game } [{ $status }]: Bàn của { $host } ({ $count } người) cùng với { $members }
table-status-waiting = Đang chờ
table-status-playing = Đang chơi
table-status-finished = Đã xong
table-not-exists = Bàn chơi không còn tồn tại.
table-full = Bàn đã đầy.
player-replaced-by-bot = { $player } đã thoát và được thay thế bằng Bot.
player-reclaimed-from-bot = { $player } đã kết nối lại và lấy lại vị trí của mình.
player-took-over = { $player } đã thay thế Bot.
player-rejoined = { $player } đã vào lại trò chơi.
spectator-joined = Đã tham gia bàn của { $host } với tư cách khán giả.

# Spectator mode
spectate = Xem
now-playing = { $player } đang chơi.
now-spectating = { $player } đang xem.
spectator-left = { $player } đã dừng xem.

# General
welcome = Chào mừng đến với PlayAural!
goodbye = Tạm biệt!

# User presence announcements
user-online = { $player } đã trực tuyến.
user-offline = { $player } đã ngoại tuyến.
user-is-admin = { $player } là quản trị viên của PlayAural.
user-is-dev = { $player } là Nhà phát triển của PlayAural.
permission-denied = Bạn không có quyền thực hiện hành động này đối với Nhà phát triển.
kick-user = Đuổi người chơi
kick-broadcast = { $target } đã bị đuổi bởi { $actor }.
you-were-kicked = Bạn đã bị đuổi bởi { $actor }.
user-not-online = Người chơi { $target } không trực tuyến.
kick-immune = Bạn không thể đuổi người này.
kick-confirm = Bạn có chắc chắn muốn đuổi { $player } không?
kick-menu-title = Đuổi người chơi
kick-confirm-menu-title = Xác nhận đuổi người chơi
no-users-to-kick = Không có người dùng nào để đuổi.
usage-kick = Cách dùng: /kick <tên_người_dùng>
online-users-none = Không có ai trực tuyến.
online-users-one = 1 người: { $users }
online-users-many = { $count } người: { $users }
online-user-not-in-game = Chưa vào game
online-user-waiting-approval = Đang chờ duyệt
user-role-dev = Nhà phát triển
user-role-admin = Quản trị viên
user-role-user = Người dùng
client-type-web = Web
client-type-desktop = Desktop
client-type-python = Python
online-user-full-entry = { $username } ({ $role }, { $client }): { $status }

# Options
language = Ngôn ngữ
language-option = Ngôn ngữ: { $language }
language-changed = Ngôn ngữ đã được đặt là { $language }.

# Boolean option states
option-on = Bật
option-off = Tắt

# Sound options
turn-sound-option = Âm thanh báo lượt: { $status }

# Dice options
clear-kept-option = Xóa xúc xắc đã giữ khi gieo: { $status }
option-notify-table-created-on = Thông báo khi có bàn mới: Bật
option-notify-table-created-off = Thông báo khi có bàn mới: Tắt
dice-keeping-style-option = Kiểu giữ xúc xắc: { $style }
dice-keeping-style-changed = Kiểu giữ xúc xắc đã đặt thành { $style }.
dice-keeping-style-indexes = Theo vị trí
dice-keeping-style-values = Theo giá trị

# Bot names
cancel = Hủy
no-bot-names-available = Không có tên bot nào.
select-bot-name = Chọn tên cho bot
enter-bot-name = Nhập tên bot
no-options-available = Không có tùy chọn nào.
no-scores-available = Chưa có điểm số.

# Duration estimation
estimate-duration = Ước tính thời gian
estimate-computing = Đang tính toán thời gian chơi ước tính...
estimate-result = Bot trung bình: { $bot_time } (± { $std_dev }). { $outlier_info }Ước tính người chơi: { $human_time }.
estimate-error = Không thể ước tính thời gian.
estimate-already-running = Đang trong quá trình ước tính thời gian.

# Save/Restore
saved-tables = Các bàn đã lưu
no-saved-tables = Bạn không có bàn nào đã lưu.
no-active-tables = Không có bàn nào đang hoạt động.
restore-table = Khôi phục
delete-saved-table = Xóa
saved-table-deleted = Đã xóa bàn đã lưu.
missing-players = Không thể khôi phục: những người chơi này không có mặt: { $players }
table-restored = Đã khôi phục bàn! Tất cả người chơi đã được chuyển vào.
table-saved-destroying = Đã lưu bàn! Đang quay về menu chính.
game-type-not-found = Loại trò chơi không còn tồn tại.

# Action disabled reasons
action-not-your-turn = Chưa đến lượt của bạn.
action-not-playing = Trò chơi chưa bắt đầu.
action-spectator = Khán giả không thể làm điều này.
action-not-host = Chỉ chủ bàn mới có thể làm điều này.
action-game-in-progress = Không thể làm điều này khi trò chơi đang diễn ra.
action-need-more-players = Cần thêm người chơi để bắt đầu.
action-table-full = Bàn đã đầy.
action-no-bots = Không có bot nào để xóa.
action-bots-cannot = Bot không thể làm điều này.
action-no-scores = Chưa có điểm số nào.

# Enhanced Options
music-volume-option = Âm lượng nhạc: { $value }%
ambience-volume-option = Âm lượng môi trường: { $value }%
mute-global-chat-option = Tắt tiếng chat chung: { $status }
mute-table-chat-option = Tắt tiếng chat trong bàn: { $status }
invert-multiline-enter-option = Đảo ngược phím Enter: { $status }
play-typing-sounds-option = Âm thanh gõ phím: { $status }
enter-music-volume = Nhập âm lượng nhạc (0-100)
enter-ambience-volume = Nhập âm lượng môi trường (0-100)
invalid-volume = Âm lượng không hợp lệ. Vui lòng nhập số từ 0 đến 100.

# Dice actions
dice-not-rolled = Bạn chưa gieo xúc xắc.
dice-locked = Viên xúc xắc này đã bị khóa.
dice-no-dice = Không có xúc xắc nào.

# Game actions
game-turn-start = Lượt của { $player }.
game-no-turn = Hiện không phải lượt của ai.
table-no-players = Không có người chơi.
table-players-one = { $count } người chơi: { $players }.
table-players-many = { $count } người chơi: { $players }.
table-spectators = Khán giả: { $spectators }.
game-leave = Rời khỏi
game-over = Kết thúc game
game-final-scores = Điểm tổng kết
game-points = { $count } { $count ->
    [one] điểm
   *[other] điểm
}
status-box-closed = Đã đóng.
play = Chơi

# Leaderboards
leaderboards = Bảng xếp hạng
leaderboards-menu-title = Bảng xếp hạng
leaderboards-select-game = Chọn trò chơi để xem bảng xếp hạng
leaderboard-no-data = Chưa có dữ liệu xếp hạng cho trò chơi này.

# Leaderboard types
leaderboard-type-wins = Người thắng nhiều nhất
leaderboard-type-rating = Xếp hạng kỹ năng
leaderboard-type-total-score = Tổng điểm
leaderboard-type-high-score = Điểm cao nhất
leaderboard-type-games-played = Số ván đã chơi
leaderboard-type-avg-points-per-turn = Điểm trung bình mỗi lượt
leaderboard-type-best-single-turn = Lượt đi điểm cao nhất
leaderboard-type-score-per-round = Điểm mỗi vòng

# Leaderboard headers
leaderboard-wins-header = { $game } - Người thắng nhiều nhất
leaderboard-total-score-header = { $game } - Tổng điểm
leaderboard-high-score-header = { $game } - Điểm cao nhất
leaderboard-games-played-header = { $game } - Số ván đã chơi
leaderboard-rating-header = { $game } - Xếp hạng kỹ năng
leaderboard-avg-points-header = { $game } - Điểm trung bình mỗi lượt
leaderboard-best-turn-header = { $game } - Lượt đi điểm cao nhất
leaderboard-score-per-round-header = { $game } - Điểm mỗi vòng

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] thắng
   *[other] thắng
} { $losses } { $losses ->
    [one] thua
   *[other] thua
}, tỷ lệ thắng { $percentage }%
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: trung bình { $value }
leaderboard-games-entry = { $rank }. { $player }: { $value } ván

# Player stats
leaderboard-player-stats = Thống kê của bạn: { $wins } thắng, { $losses } thua (tỷ lệ thắng { $percentage }%)
leaderboard-no-player-stats = Bạn chưa chơi trò chơi này.

# Skill rating leaderboard
leaderboard-no-ratings = Chưa có dữ liệu xếp hạng cho trò chơi này.
leaderboard-rating-entry = { $rank }. { $player }: xếp hạng { $rating } ({ $mu } ± { $sigma })
leaderboard-player-rating = Xếp hạng của bạn: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Bạn chưa có xếp hạng cho trò chơi này.

# My Stats menu
my-stats = Thống kê của tôi
my-stats-select-game = Chọn trò chơi để xem thống kê
my-stats-no-data = Bạn chưa chơi trò chơi này.
my-stats-no-games = Bạn chưa chơi ván nào.
my-stats-header = { $game } - Thống kê của bạn
my-stats-wins = Thắng: { $value }
my-stats-losses = Thua: { $value }
my-stats-winrate = Tỷ lệ thắng: { $value }%
my-stats-games-played = Số ván đã chơi: { $value }
my-stats-total-score = Tổng điểm: { $value }
my-stats-high-score = Điểm cao nhất: { $value }
my-stats-rating = Xếp hạng kỹ năng: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Chưa có xếp hạng kỹ năng
my-stats-avg-per-turn = Điểm trung bình mỗi lượt: { $value }
my-stats-best-turn = Lượt đi điểm cao nhất: { $value }

# Prediction system
predict-outcomes = Dự đoán kết quả
predict-header = Kết quả dự đoán (theo xếp hạng kỹ năng)
predict-entry = { $rank }. { $player } (xếp hạng: { $rating })
predict-entry-2p = { $rank }. { $player } (xếp hạng: { $rating }, tỷ lệ thắng { $probability }%)
predict-unavailable = Dự đoán xếp hạng không khả dụng.
predict-need-players = Cần ít nhất 2 người chơi thật để dự đoán.
action-need-more-humans = Cần thêm người chơi thật.
confirm-leave-game = Bạn có chắc chắn muốn rời bàn không?
confirm-yes = Có
confirm-no = Không

# Administration
administration = Quản trị
admin-menu-title = Quản trị

# Account approval
account-approval = Duyệt tài khoản
account-approval-menu-title = Duyệt tài khoản
no-pending-accounts = Không có tài khoản nào chờ duyệt.
approve-account = Duyệt
decline-account = Từ chối
account-approved = Tài khoản của { $player } đã được duyệt.
account-declined = Tài khoản của { $player } đã bị từ chối và xóa bỏ.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Tài khoản của bạn đang chờ quản trị viên phê duyệt. Vui lòng đợi...
account-approved-welcome = Tài khoản của bạn đã được duyệt! Chào mừng đến với PlayAural!
account-declined-goodbye = Yêu cầu tài khoản của bạn đã bị từ chối.

# Admin notifications for account requests
account-request = yêu cầu tài khoản
account-action = đã thực hiện hành động tài khoản

# Admin promotion/demotion
promote-admin = Thăng chức Admin
demote-admin = Giáng chức Admin
promote-admin-menu-title = Thăng chức Admin
demote-admin-menu-title = Giáng chức Admin
no-users-to-promote = Không có người dùng nào để thăng chức.
no-admins-to-demote = Không có admin nào để giáng chức.
confirm-promote = Bạn có chắc muốn thăng chức admin cho { $player }?
confirm-demote = Bạn có chắc muốn giáng chức admin của { $player }?
broadcast-to-all = Thông báo cho tất cả người dùng
broadcast-to-admins = Chỉ thông báo cho các admin
broadcast-to-nobody = Im lặng (không thông báo)
promote-announcement = { $player } đã được thăng chức thành admin!
promote-announcement-you = Bạn đã được thăng chức thành admin!
demote-announcement = { $player } đã bị giáng chức khỏi vị trí admin.
demote-announcement-you = Bạn đã bị giáng chức khỏi vị trí admin.
not-admin-anymore = Bạn không còn là admin và không thể thực hiện hành động này.

# Broadcast
broadcast-announcement = Gửi thông báo
admin-broadcast-prompt = Nhập tin nhắn để thông báo cho tất cả người dùng đang trực tuyến. (Tin nhắn này sẽ gửi tới mọi người!)
admin-broadcast-sent = Đã gửi thông báo đến { $count } người dùng.

# Mile by Mile Deck Rigging
milebymile-rig-none = Không
milebymile-rig-no-duplicates = Không trùng lặp
milebymile-rig-2x-attacks = Tấn công x2
milebymile-rig-2x-defenses = Phòng thủ x2
admin-broadcast-sent = Đã gửi thông báo đến { $count } người dùng.

# Players
unknown-player = Người chơi không xác định

# Logout
logout-confirm-title = Bạn có chắc chắn muốn đăng xuất và thoát trò chơi không?
logout-confirm-yes = Có, đăng xuất
logout-confirm-no = Không, ở lại
goodbye = Tạm biệt!

# System messages
system-name = Hệ thống
server-restarting = Máy chủ sẽ khởi động lại trong { $seconds } giây nữa...
server-shutting-down = Máy chủ sẽ tắt trong { $seconds } giây nữa...
server-error-changing-language = Lỗi khi thay đổi ngôn ngữ: { $error }
default-save-name = { $game } - { $date }

# Speech Settings (Web)
speech-settings = Cài đặt giọng đọc
speech-mode-option = Chế độ đọc: { $status }
speech-rate-option = Tốc độ đọc: { $value }%
speech-voice-option = Giọng đọc: { $voice }
select-voice = Chọn giọng đọc
enter-speech-rate = Nhập tốc độ đọc (50-300)
invalid-rate = Tốc độ không hợp lệ. Vui lòng nhập số từ 50 đến 300.
mode-aria = Aria-live
mode-web-speech = Web Speech API
default-voice = Giọng mặc định

# Auto-kick and Pause notifications
player-kicked-offline = Người chơi { $player } đã bị đuổi (ngoại tuyến).
game-paused-host-disconnect = Game tạm dừng. Đang chờ chủ bàn { $player } kết nối lại...
game-resumed = Chủ bàn { $player } đã kết nối lại. Tiếp tục game!
new-host = Chủ bàn mới: { $player }
