auth-username-password-required = Yêu cầu tên đăng nhập và mật khẩu.
auth-registration-success = Đăng ký thành công! Giờ bạn có thể đăng nhập.
auth-username-taken = Tên đăng nhập đã có người dùng. Vui lòng chọn tên khác.
auth-username-reserved-bot = Tên này được dành riêng cho bot PlayAural. Vui lòng chọn tên đăng nhập khác.
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
return-to-table = Trở lại bàn
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
player-replaced-by-bot = { $bot } đang chơi thay cho { $player }.
player-reclaimed-from-bot = { $player } đã trở lại và lấy lại chỗ từ { $bot }.
player-took-over = { $player } đã lấy lại chỗ từ { $bot }.
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
online-user-not-in-game = Menu chính
online-user-waiting-approval = Đang chờ duyệt
presence-status-main-menu = Menu chính
presence-status-waiting-table = Đang chờ tại bàn { $game }
presence-status-playing = Đang chơi { $game }
presence-status-spectating = Đang xem { $game }
presence-status-watching-table = Đang xem tại bàn { $game }
presence-status-reviewing-results = Đang xem kết quả { $game }
presence-status-spectating-results = Đang xem kết quả { $game }
user-role-dev = Nhà phát triển
user-role-admin = Quản trị viên
user-role-user = Người dùng
client-type-web = Web
client-type-python = Máy tính
client-type-mobile = Di động
client-type-with-platform = { $client } ({ $platform })
online-user-full-entry = { $username } ({ $role }, { $client }, { $language }): { $status }
online-user-actions-title = Hành động cho { $username }
user-not-online-anymore = Người dùng này không còn trực tuyến.
close-menu = Đóng

language = Ngôn ngữ
language-option = Ngôn ngữ: { $language }
language-changed = Ngôn ngữ đã được đặt là { $language }.
language-menu-entry =
    { $official ->
        [true] { $language }. Ngôn ngữ chính thức của PlayAural. Người dịch: { $translators }.
       *[false] { $language }. Bản dịch cộng đồng. Người dịch: { $translators }.
    }
language-menu-entry-missing-metadata = { $language }. Chưa có thông tin người dịch.
language-menu-current-entry = Hiện tại: { $entry }

option-on = Bật
option-off = Tắt

# Điều khiển trong menu tùy chọn nhiều lựa chọn
option-back = Quay lại
option-select-all = Chọn tất cả
option-deselect-all = Bỏ chọn tất cả
option-selected-count = Đã chọn { $count }
option-deselected-count = Đã bỏ chọn { $count }
option-min-selected = Bạn phải chọn ít nhất { $count }.
option-max-selected = Bạn chỉ được chọn tối đa { $count }.

turn-sound-option = Âm thanh báo lượt: { $status }

custom-bot-names-option = Tên bot tùy chỉnh: { $status }
confirm-destructive-option = Xác nhận hành động rủi ro: { $status }
clear-kept-option = Xóa xúc xắc đã giữ khi gieo: { $status }
option-notify-table-created = Thông báo khi có bàn mới: { $status }
option-notify-user-presence = Thông báo người dùng trực tuyến/ngoại tuyến: { $status }
option-notify-friend-presence = Thông báo trạng thái bạn bè: { $status }
dice-keeping-style-option = Kiểu giữ xúc xắc: { $style }
dice-keeping-style-changed = Kiểu giữ xúc xắc đã đặt thành { $style }.
dice-keeping-style-indexes = Theo vị trí
dice-keeping-style-values = Theo giá trị

# Tách tùy chỉnh cá nhân: chung và trò chơi
general-options = Tùy chỉnh chung
game-options = Tùy chỉnh trò chơi

# Tùy chỉnh trò chơi (khai báo, có ghi đè theo từng trò chơi)
pref-category-display = Hiển thị
pref-set-brief-announcements = Thông báo ngắn gọn: { $status }
pref-changed-brief-announcements = Thông báo ngắn gọn { $status }.
pref-desc-brief-announcements = Rút ngắn thông báo nước đi và sự kiện trong trò chơi; tắt để nghe lời tường thuật đầy đủ hơn.
pref-category-sounds = Âm thanh
pref-category-gameplay = Lối chơi
pref-category-dice = Xúc xắc
pref-default = Mặc định
pref-per-game-for = { $game }: { $value }
pref-reset-all = Đặt lại tất cả tùy chỉnh trò chơi
pref-reset-category = Đặt lại tùy chỉnh { $category }
pref-reset-done = Đã đặt lại tùy chỉnh trò chơi.
pref-set-play-turn-sound = Âm thanh báo lượt: { $status }
pref-set-confirm-destructive-actions = Xác nhận hành động rủi ro: { $status }
pref-set-allow-custom-bot-names = Tên bot tùy chỉnh: { $status }
pref-set-clear-kept-on-roll = Xóa xúc xắc đã giữ khi gieo: { $status }
pref-set-dice-keeping-style = Kiểu giữ xúc xắc: { $choice }
pref-changed-play-turn-sound = Âm thanh báo lượt { $status }.
pref-changed-confirm-destructive-actions = Xác nhận hành động rủi ro { $status }.
pref-changed-allow-custom-bot-names = Tên bot tùy chỉnh { $status }.
pref-changed-clear-kept-on-roll = Xóa xúc xắc đã giữ khi gieo { $status }.
pref-changed-dice-keeping-style = Đã đặt kiểu giữ xúc xắc thành { $choice }.
pref-desc-play-turn-sound = Phát âm thanh khi đến lượt của bạn.
pref-desc-confirm-destructive-actions = Hỏi xác nhận trước các hành động rủi ro hoặc không thể hoàn tác, chẳng hạn như bỏ lượt trong Pusoy Dos.
pref-desc-allow-custom-bot-names = Cho phép bạn đặt tên tùy chỉnh cho các bot bạn thêm vào bàn.
pref-desc-clear-kept-on-roll = Trong các trò xúc xắc có hỗ trợ, chẳng hạn Yahtzee, thả tất cả xúc xắc đang giữ sau mỗi lần gieo. Lần gieo tiếp theo sẽ gieo lại tất cả, trừ những viên bạn giữ lại; khi dùng Theo giá trị, nhấn Shift+1-6 để giữ viên có mặt tương ứng.
pref-desc-dice-keeping-style = Theo vị trí: dùng phím 1-5, hoặc 1-6 trong 1-4-24, để đổi trạng thái từng viên theo vị trí. Theo giá trị: dùng phím 1-6 để thả một viên đang giữ có mặt tương ứng, và Shift+1-6 để giữ lại một viên đã thả. Trong giai đoạn đổi của Tradeoff, phím 1-6 giữ lại một viên cùng mặt, còn Shift+1-6 đánh dấu một viên để đổi; trong giai đoạn lấy, phím số thường 1-6 lấy một viên cùng mặt từ hũ chung.

cancel = Hủy
no-bot-names-available = Không có tên bot nào.
enter-bot-name = Nhập tên bot
bot-name-invalid-length = Tên bot phải dài từ 3 đến 30 ký tự.
bot-name-invalid-characters = Tên bot chỉ được dùng chữ cái, số và khoảng trắng.
bot-name-already-used = Một người chơi hoặc bot với tên này đã có tại bàn.
bot-name-registered-account = Tên này thuộc về một tài khoản đã đăng ký. Vui lòng chọn tên bot khác.
table-name-already-used = Một người chơi hoặc bot với tên này đã có tại bàn.
no-options-available = Không có tùy chọn nào.
no-scores-available = Chưa có điểm số.

option-desc-generic = { $label }. Mặc định: { $default }.
option-desc-integer = { $label }. Nhập một số nguyên từ { $min } đến { $max }. Mặc định: { $default }.
option-desc-number = { $label }. Nhập một số từ { $min } đến { $max }. Mặc định: { $default }.
option-desc-menu = { $label }. Chọn một trong các mục: { $choices }. Mặc định: { $default }.
option-desc-bool = { $label }. Kích hoạt mục này để bật hoặc tắt tùy chỉnh. Mặc định: { $default }.
option-desc-multiselect = { $label }. Đang chọn: { $selected }. Số lựa chọn tối thiểu: { $min }. Số lựa chọn tối đa: { $max }. Mặc định chọn: { $default }.
option-desc-no-choices = hiện không có lựa chọn nào
option-desc-none-selected = không có
option-desc-no-maximum = không giới hạn

general-desc-profile = Xem và chỉnh sửa thông tin hồ sơ công khai của bạn.
general-desc-friends = Quản lý bạn bè, lời mời kết bạn, tin nhắn riêng và thao tác với bàn của bạn bè.
general-desc-my-stats = Xem số ván thắng, thua, xếp hạng và các thống kê trò chơi có hỗ trợ.
general-desc-general-options = Điều chỉnh ngôn ngữ, âm thanh, hỗ trợ tiếp cận và thông báo dùng chung cho tài khoản.
general-desc-game-options = Điều chỉnh các tùy chỉnh lối chơi có thể áp dụng chung hoặc riêng cho từng trò chơi có hỗ trợ.
general-desc-language = Chọn ngôn ngữ dùng cho menu, thông báo và tài liệu của máy chủ khi có bản dịch.
general-desc-audio = Điều chỉnh âm lượng nhạc, hiệu ứng, môi trường, trò chuyện thoại, âm thanh gõ phím và thiết bị đầu vào trên máy khách máy tính.
general-desc-accessibility = Điều chỉnh cách đọc nội dung, nhập liệu và hành vi hỗ trợ tiếp cận đang có trên thiết bị này.
general-desc-notifications = Chọn các thông báo trò chuyện, trạng thái hiện diện và tạo bàn mà bạn muốn nghe.
general-desc-music-volume = Thay đổi âm lượng nhạc nền. Đặt thành Tắt để tắt nhạc.
general-desc-sound-volume = Thay đổi âm lượng hiệu ứng trò chơi. Hiệu ứng luôn giữ ít nhất mười phần trăm để các tín hiệu quan trọng vẫn nghe được.
general-desc-ambience-volume = Thay đổi âm lượng âm thanh môi trường. Đặt thành Tắt để tắt âm thanh môi trường.
general-desc-voice-volume = Thay đổi âm lượng phát lại của trò chuyện thoại trong bàn.
general-desc-audio-input-device = Chọn micrô hoặc thiết bị đầu vào mà máy khách máy tính dùng cho trò chuyện thoại.
general-desc-play-typing-sounds = Phát âm thanh gõ phím nhỏ khi bạn nhập chữ trong các ô nhập liệu của máy khách.
general-desc-web-speech-settings = Cấu hình giọng đọc trên web, gồm chế độ ARIA live hoặc Web Speech, tốc độ đọc và giọng đọc.
general-desc-mobile-speech-settings = Cấu hình bộ máy đọc, giọng đọc và tốc độ đọc trên di động.
general-desc-invert-multiline-enter = Đổi vai trò gửi và xuống dòng trong các ô nhập nhiều dòng trên máy khách máy tính.
general-desc-mute-global-chat = Không tự động đọc tin nhắn ở kênh chung.
general-desc-mute-table-chat = Không tự động đọc tin nhắn trò chuyện trong bàn.
general-desc-notify-user-presence = Thông báo khi người dùng trực tuyến hoặc ngoại tuyến.
general-desc-notify-friend-presence = Thông báo khi bạn bè của bạn trực tuyến hoặc ngoại tuyến.
general-desc-notify-table-created = Thông báo khi có bàn công khai mới được tạo.
general-desc-speech-mode = Chọn để máy khách web gửi thông báo cho trình đọc màn hình qua ARIA live hoặc tự đọc bằng Web Speech API của trình duyệt.
general-desc-speech-rate = Thay đổi tốc độ đọc của máy khách web.
general-desc-speech-voice = Chọn giọng đọc dùng cho Web Speech API của máy khách web, hoặc quay về giọng mặc định của trình duyệt.
general-desc-mobile-tts-engine = Chọn bộ máy đọc trên di động. Android hiện dùng bộ máy do hệ thống quản lý.
general-desc-mobile-tts-voice = Chọn giọng đọc trên di động, hoặc quay về giọng mặc định của hệ thống.
general-desc-mobile-tts-rate = Thay đổi tốc độ đọc trên di động.

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
game-category-filter = Thể loại: { $category }
game-category-filter-option = { $category } ({ $count })
game-category-all = Tất cả
game-category-cards = Trò chơi bài
game-category-poker = Trò chơi poker
game-category-dice = Trò chơi xúc xắc
game-category-board = Trò chơi bàn cờ
game-category-arcade = Trò chơi arcade
game-category-misc = Khác
no-games-in-category = Không có trò chơi nào trong thể loại này.
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
action-start-needs-more-players = Chưa thể bắt đầu. Số người đang tham gia: { $current }. Tối thiểu: { $minimum }.
action-start-has-too-many-players = Chưa thể bắt đầu. Số người đang tham gia: { $current }. Tối đa: { $maximum }.
action-start-requires-exact-players = Chưa thể bắt đầu. Số người đang tham gia: { $current }. Yêu cầu đúng: { $required }.
action-no-bots = Không có bot nào để xóa.
action-bots-cannot = Bot không thể làm điều này.
action-no-scores = Chưa có điểm số nào.

options-category-audio = Âm thanh
options-category-accessibility = Hỗ trợ tiếp cận
options-category-notifications = Thông báo
options-category-game = Trò chơi

music-volume-option = Âm lượng nhạc: { $value }%
sound-volume-option = Âm lượng hiệu ứng: { $value }%
ambience-volume-option = Âm lượng môi trường: { $value }%
voice-volume-option = Âm lượng trò chuyện thoại: { $value }%
volume-choice-off = Tắt
volume-choice-percent = { $value }%
volume-choice-current = { $label } (hiện tại)
audio-input-device-option = Thiết bị đầu vào âm thanh: { $device }
audio-input-device-default = Thiết bị đầu vào mặc định của hệ thống

mute-global-chat-option = Tắt tiếng trò chuyện chung: { $status }
mute-table-chat-option = Tắt tiếng trò chuyện trong bàn: { $status }
invert-multiline-enter-option = Đảo ngược phím Enter: { $status }
play-typing-sounds-option = Âm thanh gõ phím: { $status }
enter-music-volume = Nhập âm lượng nhạc (0-100)
enter-ambience-volume = Nhập âm lượng môi trường (0-100)
enter-voice-volume = Nhập âm lượng trò chuyện thoại (10-100)
invalid-volume = Âm lượng không hợp lệ.

dice-not-rolled = Bạn chưa gieo xúc xắc.
dice-no-dice = Không có xúc xắc nào.
table-no-players = Không có người chơi.
table-players-one = { $count } người chơi: { $players }.
table-players-many = { $count } người chơi: { $players }.
table-spectators = Khán giả: { $spectators }.
table-host-suffix = (Chủ bàn)
table-voice-chat-suffix = (đang tham gia trò chuyện thoại)
table-members-summary = Tóm tắt bàn: { $total } chỗ; { $real } người thật, { $bots } bot; { $active } đang tham gia, { $spectators } đang xem.
table-members-empty = Hiện chưa có ai được liệt kê ở bàn này. Hãy dùng Quay lại để trở về và làm mới màn hình bàn.
table-member-entry = { $player }: { $status }
table-member-status-host = Chủ bàn
table-member-status-player = Người chơi
table-member-status-spectator = Khán giả
table-member-status-bot = Bot
table-member-status-online = Trực tuyến
table-member-status-offline = Ngoại tuyến
table-member-status-voice-chat = đang trong trò chuyện thoại
table-member-status-bot-takeover = bot đang chơi thay: { $bot }
table-member-no-actions = Không có hành động nào cho { $player }.
table-member-left = Người này không còn ở bàn này.
table-member-bot-left = Bot này không còn ở bàn này.
game-over = Kết thúc game
game-final-scores = Điểm tổng kết
game-points = { $count } { $count ->
    [one] điểm
   *[other] điểm
}

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
my-stats-most-enemies-defeated = Số địch hạ gục cao nhất: { $value }
my-stats-deepest-wave-reached = Đợt vượt sâu nhất: { $value }

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
admin-search-users = Tìm theo tên người dùng
admin-search-users-current = Tìm theo tên người dùng. Đang tìm: { $query }.
admin-search-prompt = Nhập toàn bộ hoặc một phần tên người dùng để tìm. Để trống để duyệt toàn bộ kết quả theo từng trang.
menu-page-summary = Đang hiển thị mục { $start }-{ $end } trong tổng số { $total } mục. Trang { $page } trên { $pages }.
menu-page-summary-query = Tìm "{ $query }": đang hiển thị mục { $start }-{ $end } trong tổng số { $total } mục. Trang { $page } trên { $pages }.
menu-page-refresh = Làm mới danh sách
menu-list-refreshed = Đã làm mới danh sách.
menu-page-first = Trang đầu
menu-page-previous = Trang trước
menu-page-next = Trang sau
menu-page-last = Trang cuối
admin-search-no-results = Không tìm thấy người dùng phù hợp. Hãy dùng Tìm theo tên người dùng để thử từ khóa khác.
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
admin-active-ban-entry = { $username }. Lệnh cấm hết hạn: { $expires }. Lý do: { $reason }. Admin thực hiện: { $admin }.
admin-active-mute-entry = { $username }. Lệnh tắt tiếng hết hạn: { $expires }. Lý do: { $reason }. Admin thực hiện: { $admin }.
admin-penalty-expiry-permanent = vĩnh viễn
admin-penalty-expiry-unknown = không rõ thời hạn
admin-penalty-expiry-expired = đã hết hạn
admin-penalty-expiry-timed = { $date } (còn { $remaining })
admin-penalty-reason-unknown = chưa ghi lý do
admin-penalty-admin-unknown = admin không xác định
admin-penalty-remaining-days = { $count ->
    [one] 1 ngày
   *[other] { $count } ngày
}
admin-penalty-remaining-hours = { $count ->
    [one] 1 giờ
   *[other] { $count } giờ
}
admin-penalty-remaining-minutes = { $count ->
    [one] 1 phút
   *[other] { $count } phút
}
admin-penalty-remaining-less-minute = dưới 1 phút

ban-broadcast = { $target } đã bị cấm bởi { $actor } vì { $reason }. Thời hạn: { $duration }.
unban-broadcast = { $target } đã được bỏ cấm bởi { $actor }.

banned-menu-title = Tài khoản bị cấm
banned-reason = Lý do: { $reason }
banned-expires = Hết hạn: { $expires }
banned-permanent = Hết hạn: Vĩnh viễn
disconnect = Ngắt kết nối


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
chat-global-disabled-send = Trò chuyện chung đang bị tắt trong tùy chọn của bạn. Hãy bật lại trò chuyện chung trước khi gửi tin nhắn chung.
chat-table-disabled-send = Trò chuyện trong bàn đang bị tắt trong tùy chọn của bạn. Hãy bật lại trò chuyện trong bàn trước khi gửi tin nhắn trong bàn.
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
motd-created = Đã tạo thành công MOTD phiên bản { $version }.
motd-deleted = MOTD đã bị xóa.
motd-delete-empty = Không có MOTD nào đang hoạt động để xóa.
motd-not-exists = Không có MOTD nào đang hoạt động.
motd-announcement = Thông báo của ngày
motd-broadcast = Thông báo mới: { $message }
error-no-languages = Lỗi: Không tìm thấy ngôn ngữ.
ok = OK

admin-localized-text-subject-motd = thông báo trong ngày
admin-localized-text-subject-power = lý do tắt hoặc khởi động lại máy chủ
admin-localized-text-subject-ban = lý do cấm tùy chỉnh
admin-localized-text-subject-mute = lý do tắt tiếng tùy chỉnh
admin-localized-text-instructions = Chỉnh sửa bản dịch { $subject }. Các ngôn ngữ chính thức là bắt buộc. Các ngôn ngữ cộng đồng là tùy chọn và sẽ dùng { $fallback } nếu để trống.
admin-localized-text-motd-version = Phiên bản MOTD: { $version }
admin-localized-text-official-heading = Ngôn ngữ chính thức, bắt buộc
admin-localized-text-community-heading = Ngôn ngữ cộng đồng, tùy chọn
admin-localized-text-field = { $language }: { $status }
admin-localized-text-required-set = đã nhập, bắt buộc
admin-localized-text-required-missing = chưa nhập, bắt buộc
admin-localized-text-optional-set = đã nhập, tùy chọn
admin-localized-text-optional-fallback = chưa nhập, tùy chọn, dùng ngôn ngữ dự phòng
admin-localized-text-prompt = Nhập { $subject } bằng { $language }. Tối đa { $max } ký tự.
admin-localized-text-too-long = Bản dịch quá dài. Giới hạn là { $max } ký tự.
admin-localized-text-missing-required = Hãy nhập đủ các bản dịch bắt buộc trước. Còn thiếu: { $languages }.
admin-localized-text-publish-motd = Đăng MOTD
admin-localized-text-continue = Tiếp tục
admin-localized-text-apply-ban = Áp dụng lệnh cấm
admin-localized-text-apply-mute = Áp dụng lệnh tắt tiếng

unknown-player = Người chơi không xác định

logout-confirm-title = Bạn có chắc chắn muốn đăng xuất và thoát trò chơi không?
logout-confirm-yes = Có, đăng xuất
logout-confirm-no = Không, ở lại

system-name = Hệ thống
server-restarting = Máy chủ sẽ khởi động lại trong { $seconds } giây nữa...
server-restarting-now = Máy chủ đang khởi động lại ngay bây giờ. Vui lòng kết nối lại sau ít phút.
server-shutting-down = Máy chủ sẽ tắt trong { $seconds } giây nữa...
server-shutting-down-now = Máy chủ đang tắt ngay bây giờ. Tạm biệt!
server-power-management = Quản lý nguồn máy chủ
server-power-reboot = Khởi động lại máy chủ
server-power-shutdown = Tắt máy chủ
server-power-cancel = Hủy lịch tắt hoặc khởi động lại
server-power-active-status = Đã lên lịch { $action }. Lý do: { $reason }.
server-power-action-reboot = khởi động lại
server-power-action-shutdown = tắt máy chủ
server-power-delay-30s = Sau 30 giây
server-power-delay-1m = Sau 1 phút
server-power-delay-5m = Sau 5 phút
server-power-delay-10m = Sau 10 phút
server-power-delay-30m = Sau 30 phút
server-power-delay-1h = Sau 1 giờ
server-power-delay-2h = Sau 2 giờ
server-power-delay-custom = Tùy chỉnh số phút
server-power-custom-delay-prompt = Nhập thời gian chờ tính bằng phút, từ 1 đến { $max }:
server-power-invalid-custom-delay = Thời gian chờ không hợp lệ. Vui lòng nhập một số phút nguyên từ 1 đến { $max }.
server-power-reason-update = Cập nhật
server-power-reason-maintenance = Bảo trì
server-power-reason-security = Bảo mật
server-power-reason-technical = Sự cố kỹ thuật
server-power-reason-custom = Lý do tùy chỉnh
server-power-reason-unspecified = chưa nêu lý do
server-power-confirm-summary = Xác nhận { $action } sau { $duration }. Lý do: { $reason }.
server-power-scheduled = Đã lên lịch { $action } sau { $duration }.
server-power-already-scheduled = Đã có một lịch tắt hoặc khởi động lại máy chủ. Hãy hủy lịch hiện tại trước khi tạo lịch mới.
server-power-cancel-none = Hiện không có lịch tắt hoặc khởi động lại máy chủ nào.
server-power-cancelled = Đã hủy lịch tắt hoặc khởi động lại máy chủ.
server-power-cancelled-broadcast = { $admin } đã hủy lịch { $action } máy chủ.
server-power-command-removed = Lệnh chat /reboot và /stop đã được gỡ bỏ. Vui lòng dùng Quản trị, Quản lý nguồn máy chủ.
server-power-finalizing-input-blocked = Máy chủ đang hoàn tất quá trình khởi động lại hoặc tắt. Vui lòng chờ máy khách tự ngắt kết nối.
server-power-finalize-failed = Không thể hoàn tất lịch { $action } một cách an toàn. Máy chủ vẫn đang hoạt động; vui lòng liên hệ quản trị viên.
server-power-reboot-warning = Máy chủ sẽ khởi động lại sau { $duration }. Lý do: { $reason }. Đừng tự ngắt kết nối; máy khách sẽ tự kết nối lại, và các bàn đang chơi sẽ được giữ nguyên.
server-power-shutdown-warning = Máy chủ sẽ tắt sau { $duration }. Lý do: { $reason }. Máy chủ sắp ngoại tuyến; hãy lưu các ván bạn muốn giữ trước khi máy chủ tắt.
server-power-reboot-now = Máy chủ đang khởi động lại ngay bây giờ. Lý do: { $reason }. Đừng tự ngắt kết nối; máy khách sẽ tự kết nối lại, và các bàn đang chơi sẽ được giữ nguyên.
server-power-shutdown-now = Máy chủ đang tắt ngay bây giờ. Lý do: { $reason }. Máy chủ sẽ ngoại tuyến.
server-power-restore-waiting = Bàn này đã được khôi phục sau một lần khởi động lại theo lịch. Đang chờ tối đa { $seconds } giây để người chơi khác kết nối lại trước khi thay ghế vắng bằng bot.
server-power-restore-input-blocked = Bàn này vẫn đang khôi phục sau lần khởi động lại theo lịch. Game tạm dừng tối đa { $seconds } giây nữa trong khi chờ { $players }; vui lòng thử lại sau khi hết thời gian chờ.
server-power-restore-missing-players-fallback = những người chơi còn lại
server-power-restore-complete = Tất cả người chơi đang chơi đã kết nối lại sau lần khởi động lại theo lịch. Game tiếp tục.
server-power-restore-complete-with-bots = Đã hết thời gian chờ kết nối lại sau lần khởi động lại theo lịch. Các ghế vắng đã được thay bằng bot, và game đang tiếp tục.
duration-seconds = { $count } giây
duration-minutes = { $count } phút
duration-hours = { $count } giờ
duration-minutes-seconds = { $minutes } phút và { $seconds } giây
duration-hours-minutes = { $hours } giờ và { $minutes } phút
server-error-changing-language = Lỗi khi thay đổi ngôn ngữ: { $error }
default-save-name = { $game } - { $date }

speech-settings = Cài đặt giọng đọc
speech-mode-option = Chế độ đọc: { $status }
speech-rate-option = Tốc độ đọc: { $value }%
speech-voice-option = Giọng đọc: { $voice }
select-voice = Chọn giọng đọc
enter-speech-rate = Nhập tốc độ đọc (50-300)
invalid-rate = Tốc độ đọc không hợp lệ. Vui lòng dùng giá trị từ 50 đến 300.
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
mobile-tts-invalid-rate = Tốc độ đọc di động không hợp lệ. Vui lòng dùng giá trị từ 50 đến 200.

player-kicked-offline = Người chơi { $player } đã bị đuổi (ngoại tuyến).
game-paused-host-disconnect = Game tạm dừng. Đang chờ { $player } kết nối lại...
game-resumed = { $player } đã kết nối lại. Tiếp tục game!

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
auth-error-rate-limit = { error-rate-limit-login }

friends-my-friends = Bạn bè của tôi
friends-pending-requests = Lời mời kết bạn ({ $count })
friends-no-pending-requests = Lời mời kết bạn
friends-send-request = Gửi lời mời kết bạn
friends-list-empty = Bạn chưa có người bạn nào.
friend-status-offline = Ngoại tuyến
friend-status-playing = Đang chơi { $game }
friend-status-spectating = Đang xem { $game }
friend-status-lobby = Menu chính
friend-list-entry = { $username } ({ $status })

friend-actions-title = Hành động cho { $username }
view-profile = Xem hồ sơ
join-table = Tham gia bàn
remove-friend = Xóa bạn
friend-remove-confirm = Xóa { $username } khỏi danh sách bạn bè của bạn?
friend-remove-not-friends = { $username } không còn trong danh sách bạn bè của bạn.
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
host-management-restart-game = Khởi động lại ván chơi
host-management-table-now-private = Bàn này hiện là riêng tư. Chỉ người được mời mới có thể tham gia.
host-management-table-now-public = Bàn này hiện là công khai.
host-restart-confirm = Khởi động lại ván hiện tại và đưa bàn về phòng chờ? Người chơi hiện tại và trò chuyện thoại vẫn được giữ nguyên, nhưng ván đang chơi sẽ bị hủy.
host-restart-broadcast = { $player } đã khởi động lại ván chơi. Bàn đã trở về phòng chờ.
host-restart-not-playing = Hiện không có ván nào đang chơi để khởi động lại.
host-invite-no-friends = (Không có bạn bè nào để mời)
host-invite-sent = Đã gửi lời mời đến { $player }.
host-invite-friend-unavailable = Người bạn đó hiện không trực tuyến.
host-invite-already-pending = Lời mời đang chờ xử lý đã được gửi cho người bạn đó.
host-invite-friend-busy = Người bạn đó đang trong một trò chơi.
host-invite-declined = { $player } đã từ chối lời mời bàn của bạn.
table-invite-received = { $host } đã mời bạn tham gia bàn { $game } của họ.
table-invite-queued = { $host } đã mời bạn tham gia bàn { $game } của họ. Hãy hoàn tất phần nhập hiện tại để trả lời.
table-invite-expired = Lời mời bàn đã hết hạn.
invite-accept = Chấp nhận lời mời
invite-decline = Từ chối lời mời
host-management-no-longer-host = Bạn không còn là chủ bàn này.
host-pass-no-candidates = (Không có người chơi nào để chuyển quyền chủ bàn)
host-pass-no-longer-host = Bạn đã chuyển quyền chủ bàn cho người chơi khác. Bạn không còn là chủ bàn này nữa.
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

voice-room-table-label = Thoại bàn { $game }
voice-unavailable = Trò chuyện thoại hiện chưa khả dụng.
voice-invalid-context = Yêu cầu vào phòng thoại không hợp lệ.
voice-not-at-table = Bạn chưa tham gia bàn nào. Hãy vào một bàn trước khi bắt đầu trò chuyện thoại.
voice-not-in-context = Bạn cần ở trong bàn đó trước khi tham gia trò chuyện thoại.
voice-rate-limited = Hãy chậm lại. Bạn đang thay đổi trạng thái trò chuyện thoại quá nhanh.
voice-muted-seconds = Bạn đang bị tắt tiếng và không thể tham gia trò chuyện thoại. Còn { $seconds } giây.
voice-muted-minutes = Bạn đang bị tắt tiếng và không thể tham gia trò chuyện thoại. Còn { $minutes } phút.
voice-muted-permanent = Bạn đang bị tắt tiếng và không thể tham gia trò chuyện thoại.
voice-status-connected = { $player } đã kết nối vào trò chuyện thoại của bàn.
voice-status-disconnected = { $player } đã ngắt kết nối khỏi trò chuyện thoại.
voice-status-connection-lost = { $player } bị mất kết nối và đã bị đưa ra khỏi trò chuyện thoại.
voice-status-left-table = { $player } đã rời bàn và rời khỏi trò chuyện thoại.

error-smtp-not-configured = Tính năng khôi phục mật khẩu hiện đang bị quản trị viên vô hiệu hóa.
error-email-not-found = Không tìm thấy tài khoản nào với địa chỉ email đó.
success-reset-email-sent = Mã khôi phục đã được gửi đến địa chỉ email của bạn.
error-smtp-send-failed = Không thể gửi email khôi phục. Vui lòng thử lại sau.
error-invalid-reset-code = Mã khôi phục không hợp lệ hoặc đã hết hạn.
success-password-reset = Mật khẩu của bạn đã được đặt lại thành công. Bây giờ bạn có thể đăng nhập.
