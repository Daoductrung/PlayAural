game-round-start = Vòng { $round }.
game-round-end = Vòng { $round } hoàn tất.
game-turn-start = Đến lượt { $player }.
game-turn-start-you = Đến lượt bạn.
game-turn-start-player = Đến lượt { $player }.
game-no-turn = Hiện không phải lượt của ai.

game-score-line = { $player }: { $score } { $unit }
game-score-line-target = { $player }: { $score }/{ $target } { $unit }
game-score-unit-points = { $count ->
    [one] điểm
   *[other] điểm
}
game-score-unit-chips = { $count ->
    [one] chip
   *[other] chip
}
game-score-unit-coins = { $count ->
    [one] xu
   *[other] xu
}
game-score-unit-health = máu
game-score-unit-ninetynine-tokens = { $count ->
    [one] thẻ
   *[other] thẻ
}
game-score-unit-tokens-home = { $count ->
    [one] quân về đích
   *[other] quân về đích
}
game-score-unit-pawns-home = { $count ->
    [one] quân về nhà
   *[other] quân về nhà
}
game-score-unit-hand-wins = { $count ->
    [one] ván thắng
   *[other] ván thắng
}
game-score-unit-light = quang năng
game-final-scores-header = Điểm tổng kết:

game-winner = { $player } thắng!
game-winner-score = { $player } thắng với { $score } điểm!
game-tiebreaker = Hòa! Vào vòng phân định thắng thua!
game-tiebreaker-players = Hòa giữa { $players }! Vào vòng phân định thắng thua!
game-eliminated = { $player } đã bị loại với { $score } điểm.

game-set-target-score = Điểm mục tiêu: { $score }
game-enter-target-score = Nhập điểm mục tiêu:
game-option-changed-target = Điểm mục tiêu đã được đặt là { $score }.

game-set-team-mode = Chế độ đội: { $mode }
game-select-team-mode = Chọn chế độ đội
game-option-changed-team = Chế độ đội đã được đặt là { $mode }.
game-team-mode-individual = Cá nhân
game-team-mode-x-teams-of-y = { $num_teams } đội, mỗi đội { $team_size } người
game-team-name = Đội { $index }
team-arrangement-started = Bắt đầu sắp xếp đội. Hãy kiểm tra đội hình, đổi người nếu cần, rồi xác nhận để bắt đầu.
team-arrangement-confirm = Xác nhận đội và bắt đầu
team-arrangement-read = Đọc đội hình
team-arrangement-select-member-action = Chọn thành viên đội
team-arrangement-select-member = Chọn một thành viên đội
team-arrangement-select-swap-target = Chọn người chơi để đổi chỗ
team-arrangement-swap-member = Chọn mục tiêu đổi chỗ
team-arrangement-swap-member-selected = Đổi { $player } với...
team-arrangement-cancel = Hủy sắp xếp đội
team-arrangement-line = { $team }: { $members }
team-arrangement-turn-order = Thứ tự lượt: { $players }
team-arrangement-member-option = { $player }, { $team }, { $selected }
team-arrangement-selected = đã chọn
team-arrangement-not-selected = chưa chọn
team-arrangement-member-selected = Đã chọn { $player } ở { $team }. Hãy chọn một người ở đội khác để đổi chỗ.
team-arrangement-swapped = { $first } và { $second } đã đổi đội cho nhau.
team-arrangement-cancelled = Đã hủy sắp xếp đội.
team-arrangement-cancelled-roster = Đã hủy sắp xếp đội vì danh sách người chơi thay đổi.
team-arrangement-refreshed = Danh sách người chơi đã thay đổi. Đội hình đã được sắp xếp lại.
team-arrangement-in-progress = Hãy hoàn tất hoặc hủy sắp xếp đội trước.
team-arrangement-not-active = Hiện không có phiên sắp xếp đội.
team-arrangement-select-first = Hãy chọn một thành viên đội trước.
team-arrangement-player-missing = Người chơi đó không còn trong phiên sắp xếp đội.
team-arrangement-same-team = Hãy chọn một người ở đội khác.
team-arrangement-swap-failed = Không thể đổi chỗ hai thành viên đội đó.

option-on = bật
option-off = tắt

status-box-closed = Đã đóng thông tin trạng thái.

game-leave = Rời trò chơi

round-timer-paused = { $player } đã tạm dừng trò chơi (nhấn p để bắt đầu vòng tiếp theo).
round-timer-resumed = Đồng hồ vòng chơi đã chạy lại.
round-timer-countdown = Vòng tiếp theo trong { $seconds } giây...

dice-keeping = Giữ lại { $value }.
dice-rerolling = Gieo lại { $value }.
dice-locked = Viên xúc xắc đó đã bị khóa và không thể thay đổi.
dice-status-label-locked = { $value } (đã khóa)
dice-status-label-kept = { $value } (đang giữ)

game-deal-counter = Chia ván { $current }/{ $total }.
game-you-deal = Bạn chia bài.
game-player-deals = { $player } chia bài.

card-name = { $rank } { $suit }
no-cards = Không có bài

suit-diamonds = rô
suit-clubs = tép
suit-hearts = cơ
suit-spades = bích

rank-ace = Át
rank-two = 2
rank-three = 3
rank-four = 4
rank-five = 5
rank-six = 6
rank-seven = 7
rank-eight = 8
rank-nine = 9
rank-ten = 10
rank-jack = J
rank-queen = Q
rank-king = K

rank-ace-plural = Át
rank-two-plural = 2
rank-three-plural = 3
rank-four-plural = 4
rank-five-plural = 5
rank-six-plural = 6
rank-seven-plural = 7
rank-eight-plural = 8
rank-nine-plural = 9
rank-ten-plural = 10
rank-jack-plural = J
rank-queen-plural = Q
rank-king-plural = K


poker-high-card-with = Mậu thầu { $high }, kèm { $rest }
poker-high-card = Mậu thầu { $high }
poker-pair-with = Đôi { $pair }, kèm { $rest }
poker-pair = Đôi { $pair }
poker-two-pair-with = Hai đôi, { $high } và { $low }, kèm { $kicker }
poker-two-pair = Hai đôi, { $high } và { $low }
poker-trips-with = Sám cô { $trips }, kèm { $rest }
poker-trips = Sám cô { $trips }
poker-straight-high = Sảnh tới { $high }
poker-flush-high-with = Thùng { $high } cao, kèm { $rest }
poker-full-house = Cù lũ, { $trips } trên { $pair }
poker-quads-with = Tứ quý { $quads }, kèm { $kicker }
poker-quads = Tứ quý { $quads }
poker-royal-flush = Sảnh chúa
poker-straight-flush-high = Thùng phá sảnh tới { $high }
poker-unknown-hand = Bài không xác định

game-error-invalid-team-mode = Chế độ đội đã chọn không hợp lệ với số lượng người chơi hiện tại.

documentation-menu = Tài liệu
introduction = Giới thiệu
community-rules = Nội quy cộng đồng
global-keys = Điều khiển toàn cục
game-rules = Luật chơi
changelog = Nhật ký thay đổi
donation = Quyên góp
contact = Liên hệ
document-not-found = Không tìm thấy tài liệu.
help = Trợ giúp

# Game Info (Ctrl+I)
game-info = Thông tin trò chơi
game-info-header = Thông tin trò chơi hiện tại
game-info-name = Trò chơi: {$game}
game-info-players = Người chơi: {$count}
game-info-host = Chủ phòng: {$host}
game-info-status = Trạng thái: {$status}
game-info-status-waiting = Đang chờ trong phòng
game-info-status-playing = Đang chơi
game-info-options-header = Cài đặt:
game-info-no-options = Trò chơi này không có tùy chọn cấu hình.

# How to Play (Ctrl+F1)
how-to-play = Cách chơi
game-rules-not-available = Luật chơi cho {$game} chưa có sẵn.
