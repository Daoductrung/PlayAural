category-card-games = Game bài
category-dice-games = Game xúc xắc
category-board-games = Game bàn cờ
category-rb-play-center = Trung tâm RB Play
category-poker = Poker
category-uncategorized = Chưa phân loại

auth-username-password-required = Yêu cầu tên đăng nhập và mật khẩu.
auth-registration-success = Đăng ký thành công! Giờ bạn có thể đăng nhập.
auth-username-taken = Tên đăng nhập đã có người dùng. Vui lòng chọn tên khác.
auth-registration-error = Đăng ký thất bại do lỗi máy chủ. Vui lòng thử lại.
auth-error-wrong-password = Sai mật khẩu.
auth-error-user-not-found = Người dùng không tồn tại.
auth-kicked-logged-in-elsewhere = Bạn đã bị ngắt kết nối vì tài khoản của bạn vừa được đăng nhập từ một thiết bị khác.

chat-global = { $player } nói chung: { $message }
dev-announcement-broadcast = { $dev } là nhà phát triển của PlayAural.
admin-announcement-broadcast = { $admin } là quản trị viên của PlayAural.

admin-smtp-updated-success = Đã cập nhật thiết lập SMTP thành công
admin-smtp-settings = Cài đặt SMTP
email-reset-subject = Mã khôi phục mật khẩu PlayAural
email-reset-body = Chào { $username },\n\nBạn đã yêu cầu khôi phục mật khẩu cho tài khoản PlayAural của mình.\nMã khôi phục 6 số của bạn là: { $code }\n\nMã này sẽ hết hạn sau 15 phút.\nNếu bạn không yêu cầu điều này, vui lòng bỏ qua email này.
email-reset-body-html = <p>Chào { $username },</p>
    <p>Chúng tôi nhận được yêu cầu khôi phục mật khẩu cho tài khoản PlayAural của bạn.</p>
    <p>Mã khôi phục 6 số của bạn là:</p>
    <h2>{ $code }</h2>
    <p>Mã này sẽ hết hạn sau đúng 15 phút.</p>
    <p>Nếu bạn không yêu cầu điều này, vui lòng bỏ qua email này. Tài khoản của bạn vẫn an toàn.</p>
    <p>Trân trọng,<br>Trung</p>
email-test-subject = Bài kiểm tra SMTP PlayAural
email-test-body = Đây là email kiểm tra từ máy chủ PlayAural xác minh cấu hình SMTP của bạn.
email-test-body-html = <p>Xin chào,</p>
    <p>Đây là email kiểm tra từ máy chủ PlayAural.</p>
    <p>Nếu bạn đang đọc được dòng này, điều đó có nghĩa cấu hình SMTP của bạn đã gửi email HTML thành công.</p>
smtp-test-sending = Đang kiểm tra kết nối, vui lòng chờ...
smtp-test-success = Gửi email kiểm tra thành công đến { $email }!
smtp-test-failed = Lỗi gửi email kiểm tra: { $error }
smtp-host = Máy chủ: { $value }
smtp-port = Cổng: { $value }
smtp-username = Tên đăng nhập: { $value }
smtp-password = Mật khẩu: { $value }
smtp-from-email = Email người gửi: { $value }
smtp-from-name = Tên người gửi: { $value }
smtp-encryption = Mã hóa: { $value }
smtp-test-connection = Kiểm tra kết nối
smtp-not-set = Chưa đặt
smtp-prompt-host = Nhập Máy chủ SMTP (ví dụ: smtp.gmail.com):
smtp-prompt-port = Nhập Cổng SMTP (ví dụ: 587 hoặc 465):
smtp-prompt-username = Nhập Tên đăng nhập SMTP:
smtp-prompt-password = Nhập Mật khẩu SMTP:
smtp-prompt-from-email = Nhập Địa chỉ Email người gửi:
smtp-prompt-from-name = Nhập Tên người gửi (ví dụ: PlayAural Support):
smtp-prompt-test-email = Nhập địa chỉ email đích để kiểm tra:
smtp-enc-none = Không mã hóa
smtp-enc-ssl = Sử dụng SSL
smtp-enc-tls = Tự động bật mã hóa TLS (STARTTLS)
smtp-current-enc = * { $value }

main-menu-title = Menu Chính

play = Chơi
view-active-tables = Xem các bàn đang hoạt động
options = Tùy chỉnh
logout = Đăng xuất
back = Quay lại
go-back = Quay lại
context-menu = Menu ngữ cảnh.
no-actions-available = Không có hành động nào.
table-new-host-promoted = { $player } bây giờ là chủ bàn.
return-to-lobby = Trở lại phòng chờ
create-table = Tạo bàn mới
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

game-player-skipped = { $player } bị bỏ qua.

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

spectate = Xem
now-playing = { $player } đang chơi.
now-spectating = { $player } đang xem.
spectator-left = { $player } đã dừng xem.

welcome = Chào mừng đến với PlayAural!
goodbye = Tạm biệt!

user-online = { $player } đã trực tuyến.
user-offline = { $player } đã ngoại tuyến.
friend-online = Bạn của bạn { $player } hiện đã trực tuyến.
friend-offline = Bạn của bạn { $player } đã ngoại tuyến.
permission-denied = Bạn không có quyền thực hiện hành động này đối với Nhà phát triển.
kick-user = Đuổi người chơi
kick-broadcast = { $target } đã bị đuổi bởi { $actor }.
you-were-kicked = Bạn đã bị đuổi bởi { $actor }.
user-not-online = Người chơi { $target } không trực tuyến.
kick-immune = Bạn không thể đuổi người này.
kick-confirm = Bạn có chắc chắn muốn đuổi { $player } không?
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
client-type-python = Máy tính
client-type-mobile = Di động
online-user-full-entry = { $username } ({ $role }, { $client }, { $language }): { $status }
online-user-actions-title = Hành động cho { $username }
user-not-online-anymore = Người dùng này không còn trực tuyến.
close-menu = Đóng

language = Ngôn ngữ
language-option = Ngôn ngữ: { $language }
language-changed = Ngôn ngữ đã được đặt là { $language }.

option-on = Bật
option-off = Tắt

turn-sound-option = Âm thanh báo lượt: { $status }

clear-kept-option = Xóa xúc xắc đã giữ khi gieo: { $status }
option-notify-table-created-on = Thông báo khi có bàn mới: Bật
option-notify-table-created-off = Thông báo khi có bàn mới: Tắt
option-notify-user-presence-on = Thông báo người dùng trực tuyến/ngoại tuyến: Bật
option-notify-user-presence-off = Thông báo người dùng trực tuyến/ngoại tuyến: Tắt
option-notify-friend-presence-on = Thông báo trạng thái bạn bè: Bật
option-notify-friend-presence-off = Thông báo trạng thái bạn bè: Tắt
dice-keeping-style-option = Kiểu giữ xúc xắc: { $style }
dice-keeping-style-changed = Kiểu giữ xúc xắc đã đặt thành { $style }.
dice-keeping-style-indexes = Theo vị trí
dice-keeping-style-values = Theo giá trị

cancel = Hủy
no-bot-names-available = Không có tên bot nào.
enter-bot-name = Nhập tên bot
no-options-available = Không có tùy chọn nào.
no-scores-available = Chưa có điểm số.


saved-tables = Các bàn đã lưu
no-saved-tables = Bạn không có bàn nào đã lưu.
no-active-tables = Không có bàn nào đang hoạt động.
no-active-tables-all = Không có bàn nào đang hoạt động.
no-active-tables-waiting = Không có bàn nào đang chờ.
no-active-tables-playing = Không có bàn nào đang chơi.
active-tables-filter = Bộ lọc: { $filter }
filter-name-all = Tất cả
filter-name-waiting = Đang chờ
filter-name-playing = Đang chơi
restore-table = Khôi phục
delete-saved-table = Xóa
saved-table-deleted = Đã xóa bàn đã lưu.
missing-players = Không thể khôi phục: những người chơi này không có mặt: { $players }
table-restored = Đã khôi phục bàn! Tất cả người chơi đã được chuyển vào.
table-saved-destroying = Đã lưu bàn! Đang quay về menu chính.
game-type-not-found = Loại trò chơi không còn tồn tại.

action-not-your-turn = Chưa đến lượt của bạn.
action-not-playing = Trò chơi chưa bắt đầu.
action-spectator = Khán giả không thể làm điều này.
action-not-host = Chỉ chủ bàn mới có thể làm điều này.
action-not-available = Hiện chưa thể thực hiện thao tác này.
action-game-in-progress = Không thể làm điều này khi trò chơi đang diễn ra.
action-need-more-players = Cần thêm người chơi để bắt đầu.
action-table-full = Bàn đã đầy.
action-no-bots = Không có bot nào để xóa.
action-bots-cannot = Bot không thể làm điều này.
action-no-scores = Chưa có điểm số nào.

music-volume-option = Âm lượng nhạc: { $value }%
ambience-volume-option = Âm lượng môi trường: { $value }%
mute-global-chat-option = Tắt tiếng trò chuyện chung: { $status }
mute-table-chat-option = Tắt tiếng trò chuyện trong bàn: { $status }
invert-multiline-enter-option = Đảo ngược phím Enter: { $status }
play-typing-sounds-option = Âm thanh gõ phím: { $status }
enter-music-volume = Nhập âm lượng nhạc (0-100)
enter-ambience-volume = Nhập âm lượng môi trường (0-100)
invalid-volume = Âm lượng không hợp lệ. Vui lòng nhập số từ 0 đến 100.

dice-not-rolled = Bạn chưa gieo xúc xắc.
dice-locked = Viên xúc xắc này đã bị khóa.
dice-no-dice = Không có xúc xắc nào.

game-turn-start = Lượt của { $player }.
game-no-turn = Hiện không phải lượt của ai.
table-no-players = Không có người chơi.
table-players-one = { $count } người chơi: { $players }.
table-players-many = { $count } người chơi: { $players }.
table-spectators = Khán giả: { $spectators }.
table-host-suffix = (Chủ bàn)
game-leave = Rời khỏi
game-over = Kết thúc game
game-final-scores = Điểm tổng kết
game-points = { $count } { $count ->
    [one] điểm
   *[other] điểm
}
status-box-closed = Đã đóng.
play = Chơi

leaderboards = Bảng xếp hạng
leaderboard-no-data = Chưa có dữ liệu xếp hạng cho trò chơi này.

leaderboard-type-wins = Người thắng nhiều nhất
leaderboard-type-rating = Xếp hạng kỹ năng
leaderboard-type-total-score = Tổng điểm
leaderboard-type-high-score = Điểm cao nhất
leaderboard-type-games-played = Số ván đã chơi
leaderboard-type-avg-points-per-turn = Điểm trung bình mỗi lượt
leaderboard-type-best-single-turn = Lượt đi điểm cao nhất
leaderboard-type-score-per-round = Điểm mỗi vòng
leaderboard-type-most-enemies-defeated = Số địch hạ gục cao nhất
leaderboard-type-deepest-wave-reached = Đợt vượt sâu nhất


leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] thắng
   *[other] thắng
} { $losses } { $losses ->
    [one] thua
   *[other] thua
}, tỷ lệ thắng { $percentage }%
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-games-entry = { $rank }. { $player }: { $value } ván
leaderboard-avg-entry = { $rank }. { $player }: { $value }

leaderboard-no-player-stats = Bạn chưa chơi trò chơi này.

leaderboard-no-ratings = Chưa có dữ liệu xếp hạng cho trò chơi này.
leaderboard-rating-entry = { $rank }. { $player }: xếp hạng { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Bạn chưa có xếp hạng cho trò chơi này.

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
my-stats-score-per-round = Điểm trung bình mỗi vòng: { $value }

predict-outcomes = Dự đoán kết quả
predict-header = Kết quả dự đoán (theo xếp hạng kỹ năng)
predict-note-multiplayer = Phần trăm thắng chỉ hiển thị khi đấu 2 người. Nếu có từ 3 người chơi thật trở lên, hệ thống chỉ hiển thị xếp hạng kỹ năng.
predict-entry = { $rank }. { $player } (xếp hạng: { $rating })
predict-entry-2p = { $rank }. { $player } (xếp hạng: { $rating }, tỷ lệ thắng { $probability }%)
predict-unavailable = Dự đoán xếp hạng không khả dụng.
predict-need-players = Cần ít nhất 2 người chơi thật để dự đoán.
action-need-more-humans = Cần thêm người chơi thật.
confirm-leave-game = Bạn có chắc chắn muốn rời bàn không?
confirm-yes = Có
confirm-no = Không

administration = Quản trị

account-approval = Duyệt tài khoản
no-pending-accounts = Không có tài khoản nào chờ duyệt.
approve-account = Duyệt
decline-account = Từ chối
account-approved = Tài khoản của { $player } đã được duyệt.
account-declined = Tài khoản của { $player } đã bị từ chối và xóa bỏ.

waiting-for-approval = Tài khoản của bạn đang chờ quản trị viên phê duyệt. Vui lòng đợi...
account-approved-welcome = Tài khoản của bạn đã được duyệt! Chào mừng đến với PlayAural!
account-declined-goodbye = Yêu cầu tài khoản của bạn đã bị từ chối.

account-request = yêu cầu tài khoản
account-action = đã thực hiện hành động tài khoản

promote-admin = Thăng chức Admin
demote-admin = Giáng chức Admin
ban-user = Cấm người dùng
unban-user = Bỏ cấm người dùng
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
dev-only-action = Hành động này chỉ dành cho Nhà phát triển.

ban-duration-1h = 1 giờ
ban-duration-6h = 6 giờ
ban-duration-12h = 12 giờ
ban-duration-1d = 1 ngày
ban-duration-3d = 3 ngày
ban-duration-1w = 1 tuần
ban-duration-1m = 1 tháng
ban-duration-permanent = Vĩnh viễn

reason-spam = Spam
reason-harassment = Quấy rối
reason-cheating = Gian lận
reason-inappropriate = Hành vi không phù hợp
reason-custom = Khác / Tùy chỉnh

no-users-to-ban = Không có người dùng nào để cấm.
no-banned-users = Không có người dùng nào đang bị cấm.

ban-broadcast = { $target } đã bị cấm bởi { $actor } vì { $reason }. Thời hạn: { $duration }.
unban-broadcast = { $target } đã được bỏ cấm bởi { $actor }.

banned-menu-title = Tài khoản bị cấm
banned-reason = Lý do: { $reason }
banned-expires = Hết hạn: { $expires }
banned-permanent = Hết hạn: Vĩnh viễn
disconnect = Ngắt kết nối

enter-custom-ban-reason = Nhập lý do cấm tùy chỉnh:

mute-user = Tắt tiếng người dùng
unmute-user = Bỏ tắt tiếng người dùng
no-users-to-mute = Không có người dùng nào để tắt tiếng.
no-muted-users = Không có người dùng nào đang bị tắt tiếng.
mute-duration-5m = 5 phút
mute-duration-15m = 15 phút
mute-duration-30m = 30 phút
mute-duration-1h = 1 giờ
mute-duration-6h = 6 giờ
mute-duration-1d = 1 ngày
mute-duration-permanent = Vĩnh viễn
enter-custom-mute-reason = Nhập lý do tắt tiếng tùy chỉnh:
mute-broadcast = { $target } đã bị tắt tiếng bởi { $actor } vì { $reason }. Thời hạn: { $duration }.
unmute-broadcast = { $target } đã được bỏ tắt tiếng bởi { $actor }.
you-have-been-muted = Bạn đã bị tắt tiếng. Lý do: { $reason }. Thời hạn: { $duration }.
you-have-been-unmuted = Bạn đã được bỏ tắt tiếng. Bạn có thể trò chuyện lại.
muted-remaining-seconds = Bạn đang bị tắt tiếng. Còn { $seconds } giây.
muted-remaining-minutes = Bạn đang bị tắt tiếng. Còn { $minutes } phút.
muted-permanent = Bạn đã bị tắt tiếng vĩnh viễn. Vui lòng liên hệ quản trị viên để biết thêm thông tin.
auto-muted-seconds = Bạn đã bị tắt tiếng tạm thời vì spam. Còn { $seconds } giây.
auto-muted-minutes = Bạn đã bị tắt tiếng tạm thời vì spam. Còn { $minutes } phút.
auto-muted-applied-seconds = Bạn đã bị tự động tắt tiếng { $seconds } giây vì spam quá mức.
auto-muted-applied-minutes = Bạn đã bị tự động tắt tiếng { $minutes } phút vì spam quá mức.
chat-rate-limited = Chậm lại! Bạn đang gửi tin nhắn quá nhanh.
admin-spam-alert = Cảnh báo: { $username } đang spam quá mức và đã bị tự động tắt tiếng.

broadcast-announcement = Gửi thông báo
admin-broadcast-prompt = Nhập tin nhắn để thông báo cho tất cả người dùng đang trực tuyến. (Tin nhắn này sẽ gửi tới mọi người!)
admin-broadcast-sent = Đã gửi thông báo đến { $count } người dùng.

manage-motd = Quản lý thông báo ngày (MOTD)
create-update-motd = Tạo/Cập nhật MOTD
view-motd = Xem MOTD hiện tại
delete-motd = Xóa MOTD
motd-version-prompt = Nhập số phiên bản MOTD mới (phải > 0):
invalid-motd-version = Phiên bản MOTD không hợp lệ. Phải là một số dương.
motd-prompt = Nhập MOTD cho ngôn ngữ { $language } (nhấn Enter để xuống dòng, Shift+Enter để gửi nếu đảo ngược phím):
motd-created = Đã tạo thành công MOTD phiên bản { $version }.
motd-cancelled = Đã hủy tạo MOTD.
motd-deleted = MOTD đã bị xóa.
motd-delete-empty = Không có MOTD nào đang hoạt động để xóa.
motd-not-exists = Không có MOTD nào đang hoạt động.
motd-announcement = Thông báo của ngày
motd-broadcast = Thông báo mới: { $message }
error-no-languages = Lỗi: Không tìm thấy ngôn ngữ.
ok = OK

milebymile-rig-none = Không
milebymile-rig-no-duplicates = Không trùng lặp
milebymile-rig-2x-attacks = Tấn công x2
milebymile-rig-2x-defenses = Phòng thủ x2
admin-broadcast-sent = Đã gửi thông báo đến { $count } người dùng.

unknown-player = Người chơi không xác định

logout-confirm-title = Bạn có chắc chắn muốn đăng xuất và thoát trò chơi không?
logout-confirm-yes = Có, đăng xuất
logout-confirm-no = Không, ở lại
goodbye = Tạm biệt!

system-name = Hệ thống
server-restarting = Máy chủ sẽ khởi động lại trong { $seconds } giây nữa...
server-restarting-now = Máy chủ đang khởi động lại ngay bây giờ. Vui lòng kết nối lại sau ít phút.
server-shutting-down = Máy chủ sẽ tắt trong { $seconds } giây nữa...
server-shutting-down-now = Máy chủ đang tắt ngay bây giờ. Tạm biệt!
server-error-changing-language = Lỗi khi thay đổi ngôn ngữ: { $error }
default-save-name = { $game } - { $date }

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
mobile-speech-settings = Cài đặt giọng đọc trên di động
mobile-tts-engine-option = Bộ máy đọc: { $engine }
mobile-tts-engine-system = Mặc định của hệ thống
mobile-tts-engine-system-selected = Bộ máy đọc mặc định của hệ thống
mobile-tts-engine-api-note = Bản này dùng bộ máy đọc do Android quản lý trong cài đặt hệ thống.
mobile-tts-voice-option = Giọng đọc di động: { $voice }
mobile-tts-rate-option = Tốc độ đọc di động: { $value }%
mobile-tts-enter-rate = Nhập tốc độ đọc di động (50-200)
mobile-tts-invalid-rate = Tốc độ không hợp lệ. Vui lòng nhập số từ 50 đến 200.

player-kicked-offline = Người chơi { $player } đã bị đuổi (ngoại tuyến).
game-paused-host-disconnect = Game tạm dừng. Đang chờ chủ bàn { $player } kết nối lại...
game-resumed = Chủ bàn { $player } đã kết nối lại. Tiếp tục game!
new-host = Chủ bàn mới: { $player }

auth-error-username-length = Tên đăng nhập phải dài từ 3 đến 30 ký tự.
auth-error-username-invalid-chars = Tên đăng nhập chỉ được chứa chữ cái, chữ số và dấu cách (không được có nhiều dấu cách liên tiếp hoặc ký tự đặc biệt).
auth-error-password-weak = Mật khẩu phải dài ít nhất 8 ký tự và bao gồm cả chữ và số.

personal-and-options = Cá nhân và Tùy chỉnh
profile = Hồ sơ
friends = Bạn bè
profile-registration-date = Ngày đăng ký: { $date }
profile-username = Tên đăng nhập: { $username }
profile-email = Email: { $email }
admin-view-email = Chế độ xem của Quản trị viên - Email: { $email }
profile-gender = Giới tính: { $gender }
profile-bio = Giới thiệu: { $bio }
profile-bio-empty = Chưa đặt
profile-email-empty = Chưa đặt

gender-male = Nam
gender-female = Nữ
gender-non-binary = Phi nhị giới
gender-not-set = Chưa đặt

action-set-edit = Đặt / Chỉnh sửa
action-delete = Xóa
bio-already-empty = Phần giới thiệu đã trống.
bio-deleted = Đã xóa giới thiệu.
bio-updated = Đã cập nhật giới thiệu.

enter-email = Nhập địa chỉ email mới:
email-updated = Đã cập nhật email.
enter-bio = Nhập phần giới thiệu:

gender-updated = Đã cập nhật giới tính.
no-changes-made = Không có thay đổi nào.
confirm-email-change = Bạn có chắc chắn muốn thay đổi email thành { $email } không?

mandatory-email-notice = Bạn phải thiết lập email để tiếp tục tham gia. Email của bạn là riêng tư và chỉ có bạn biết.
error-email-empty = Email là bắt buộc và không được để trống.
error-email-invalid = Định dạng email không hợp lệ. Vui lòng cung cấp một địa chỉ email chính xác.
reg-error-email = Email là bắt buộc để đăng ký.

error-email-taken = Email này đã được sử dụng bởi một tài khoản khác.

error-bio-length = Phần giới thiệu không được vượt quá 250 ký tự.
error-captcha-failed = Xác minh thất bại. Vui lòng thử lại.
error-rate-limit-login = Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau 15 phút.
error-rate-limit-register = Bạn đã đạt đến số lượng đăng ký tài khoản tối đa trong hôm nay.
auth-error-rate-limit = Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau 15 phút.

friends-my-friends = Bạn bè của tôi
friends-pending-requests = Lời mời kết bạn ({ $count })
friends-no-pending-requests = Lời mời kết bạn
friends-send-request = Gửi lời mời kết bạn
friends-list-empty = Bạn chưa có người bạn nào.
friend-status-offline = Ngoại tuyến
friend-status-playing = Đang chơi { $game }
friend-status-spectating = Đang xem { $game }
friend-status-lobby = Trong phòng chờ
friend-list-entry = { $username } ({ $status })

friend-actions-title = Hành động cho { $username }
view-profile = Xem hồ sơ
join-table = Tham gia bàn
remove-friend = Xóa bạn
already-in-table = Bạn đã ở trong bàn này rồi.
friend-removed-success = Đã xóa { $username } khỏi danh sách bạn bè của bạn.
friend-removed-notify = { $username } đã xóa bạn khỏi danh sách bạn bè.

no-pending-requests = Không có lời mời kết bạn nào đang chờ.
friend-request-from = Lời mời kết bạn từ { $username }
accept = Chấp nhận
decline = Từ chối
friend-accepted-success = Bạn và { $username } hiện đã là bạn bè.
friend-accepted-notify = { $username } đã chấp nhận lời mời kết bạn của bạn!
request-not-found = Lời mời kết bạn không còn tồn tại.
friend-declined-success = Đã từ chối lời mời kết bạn.
friend-declined-notify = { $username } đã từ chối lời mời kết bạn của bạn.

public-profile-title = Hồ sơ của { $username }
enter-friend-username = Nhập tên người dùng bạn muốn kết bạn:
friend-error-self = Bạn không thể gửi lời mời kết bạn cho chính mình.
friend-error-already-friends = Bạn đã là bạn bè với người này.
friend-error-duplicate = Bạn đã gửi một lời mời kết bạn cho người này rồi.
friend-request-sent = Đã gửi lời mời kết bạn đến { $username }.
friend-request-received = Bạn đã nhận được một lời mời kết bạn mới từ { $username }.

friends-grouped-requests = Bạn có lời mời kết bạn đang chờ từ: { $usernames }
friends-grouped-accepted = Lời mời kết bạn của bạn đã được chấp nhận bởi: { $usernames }
friends-grouped-declined = Lời mời kết bạn của bạn đã bị từ chối bởi: { $usernames }
friends-grouped-removed = Bạn đã bị xóa khỏi danh sách bạn bè bởi: { $usernames }
friends-and-others = { $names } và { $count } người khác

send-private-message = Gửi tin nhắn riêng
enter-pm-message = Nhập tin nhắn cho { $username }:
pm-error-not-friends = Bạn chỉ có thể gửi tin nhắn riêng cho bạn bè.
pm-error-offline = { $username } hiện không trực tuyến.
pm-sent-success = Đã gửi tin nhắn đến { $username }.
pm-sent-content = Bạn gửi đến { $username }: { $message }
pm-received = Tin nhắn riêng từ { $username }: { $message }

host-management = Quản lý bàn
table-spectator-suffix = (Khán giả)
host-management-set-private = Đặt bàn thành riêng tư
host-management-set-public = Đặt bàn thành công khai
host-management-invite = Mời bạn bè
host-management-pass-host = Chuyển quyền chủ bàn
host-management-kick = Đuổi người chơi
host-management-kick-ban = Đuổi và cấm người chơi
host-management-table-now-private = Bàn này hiện là riêng tư. Chỉ người được mời mới có thể tham gia.
host-management-table-now-public = Bàn này hiện là công khai.
host-invite-no-friends = (Không có bạn bè nào để mời)
host-invite-sent = Đã gửi lời mời đến { $player }.
host-invite-friend-unavailable = Người bạn đó hiện không trực tuyến.
host-invite-already-pending = Lời mời đang chờ xử lý đã được gửi cho người bạn đó.
host-invite-friend-busy = Người bạn đó đang trong một trò chơi.
host-invite-declined = { $player } đã từ chối lời mời bàn của bạn.
table-invite-received = { $host } đã mời bạn tham gia bàn { $game } của họ.
table-invite-expired = Lời mời bàn đã hết hạn.
invite-accept = Chấp nhận lời mời
invite-decline = Từ chối lời mời
host-pass-no-candidates = (Không có người chơi nào để chuyển quyền chủ bàn)
host-passed = { $player } hiện là chủ bàn.
host-pass-failed = Không thể chuyển quyền chủ bàn. Người chơi có thể đã rời bàn.
host-kick-no-candidates = (Không có người chơi nào để đuổi)
host-kick-invalid-target = Mục tiêu đuổi không hợp lệ.
host-kick-broadcast = { $player } đã bị đuổi khỏi bàn.
host-kick-ban-broadcast = { $player } đã bị đuổi và cấm khỏi bàn.
host-kick-you = Bạn đã bị { $host } đuổi khỏi bàn.
host-kick-ban-you = Bạn đã bị { $host } đuổi và cấm khỏi bàn.
table-you-are-banned = Bạn bị cấm khỏi bàn này.
table-private-invite-only = Bàn này là riêng tư. Bạn cần được chủ bàn mời để tham gia.

error-smtp-not-configured = Tính năng khôi phục mật khẩu hiện đang bị quản trị viên vô hiệu hóa.
error-email-not-found = Không tìm thấy tài khoản nào với địa chỉ email đó.
success-reset-email-sent = Mã khôi phục đã được gửi đến địa chỉ email của bạn.
error-smtp-send-failed = Không thể gửi email khôi phục. Vui lòng thử lại sau.
error-invalid-reset-code = Mã khôi phục không hợp lệ hoặc đã hết hạn.
success-password-reset = Mật khẩu của bạn đã được đặt lại thành công. Bây giờ bạn có thể đăng nhập.
