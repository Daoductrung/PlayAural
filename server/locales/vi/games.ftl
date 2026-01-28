# Thông báo trò chơi chung cho PlayAural
# Các thông báo này được dùng chung cho nhiều trò chơi

# Tên trò chơi
game-name-ninetynine = Chín Mươi Chín (Ninety Nine)

# Luồng vòng chơi và lượt chơi
game-round-start = Vòng { $round }.
game-round-end = Vòng { $round } hoàn tất.
game-turn-start = Lượt của { $player }.
game-no-turn = Hiện không phải lượt của ai.

# Hiển thị điểm số
game-scores-header = Điểm số hiện tại:
game-score-line = { $player }: { $score } điểm
game-points = { $count } { $count ->
    [one] điểm
   *[other] điểm
}
game-final-scores-header = Điểm tổng kết:

# Thắng/Thua
game-winner = { $player } thắng!
game-winner-score = { $player } thắng với { $score } điểm!
game-tiebreaker = Tỉ số hòa! Vào vòng phân định thắng thua!
game-tiebreaker-players = Tỉ số hòa giữa { $players }! Vào vòng phân định thắng thua!
game-eliminated = { $player } đã bị loại với { $score } điểm.

# Các tùy chọn chung
game-set-target-score = Điểm mục tiêu: { $score }
game-enter-target-score = Nhập điểm mục tiêu:
game-option-changed-target = Điểm mục tiêu được đặt là { $score }.

game-set-team-mode = Chế độ đội: { $mode }
game-select-team-mode = Chọn chế độ đội
game-option-changed-team = Chế độ đội được đặt là { $mode }.
game-team-mode-individual = Cá nhân
game-team-mode-x-teams-of-y = { $num_teams } đội { $team_size } người
game-team-name = Đội { $index }

# Giá trị tùy chọn Boolean
option-on = bật
option-off = tắt

# Hộp trạng thái
status-box-closed = Đã đóng thông tin trạng thái.

# Kết thúc trò chơi
game-leave = Rời trò chơi

# Đồng hồ vòng chơi
round-timer-paused = { $player } đã tạm dừng trò chơi (nhấn p để bắt đầu vòng tiếp theo).
round-timer-resumed = Đồng hồ vòng chơi đã chạy lại.
round-timer-countdown = Vòng tiếp theo trong { $seconds } giây...

# Trò chơi xúc xắc - giữ/bỏ xúc xắc
dice-keeping = Giữ { $value }.
dice-rerolling = Gieo lại { $value }.
dice-locked = Xúc xắc đó đã bị khóa và không thể thay đổi.
dice-status-label-locked = { $value } (đã khóa)
dice-status-label-kept = { $value } (đã giữ)

# Chia bài (trò chơi bài)
game-deal-counter = Chia ván { $current }/{ $total }.
game-you-deal = Bạn chia bài.
game-player-deals = { $player } chia bài.

# Tên lá bài
card-name = { $rank } chất { $suit }
no-cards = Không có bài

# Tên chất bài
suit-diamonds = Rô
suit-clubs = Tép
suit-hearts = Cơ
suit-spades = Bích

# Tên quân bài (Rank)
rank-ace = Át
rank-ace-plural = Át
rank-two = 2
rank-two-plural = 2
rank-three = 3
rank-three-plural = 3
rank-four = 4
rank-four-plural = 4
rank-five = 5
rank-five-plural = 5
rank-six = 6
rank-six-plural = 6
rank-seven = 7
rank-seven-plural = 7
rank-eight = 8
rank-eight-plural = 8
rank-nine = 9
rank-nine-plural = 9
rank-ten = 10
rank-ten-plural = 10
rank-jack = Bồi (J)
rank-jack-plural = Bồi (J)
rank-queen = Đầm (Q)
rank-queen-plural = Đầm (Q)
rank-king = Già (K)
rank-king-plural = Già (K)

# Mô tả tay bài Poker
poker-high-card-with = Mậu thầu { $high }, kèm { $rest }
poker-high-card = Mậu thầu { $high }
poker-pair-with = Đôi { $pair }, kèm { $rest }
poker-pair = Đôi { $pair }
poker-two-pair-with = Hai đôi, { $high } và { $low }, kèm { $kicker }
poker-two-pair = Hai đôi, { $high } và { $low }
poker-trips-with = Bộ ba (Sám) { $trips }, kèm { $rest }
poker-trips = Bộ ba (Sám) { $trips }
poker-straight-high = Sảnh { $high } cao nhất
poker-flush-high-with = Thùng { $high } cao nhất, kèm { $rest }
poker-full-house = Cù lũ, { $trips } và { $pair }
poker-quads-with = Tứ quý { $quads }, kèm { $kicker }
poker-quads = Tứ quý { $quads }
poker-straight-flush-high = Thùng phá sảnh { $high } cao nhất
poker-unknown-hand = Bài không xác định

# Lỗi xác thực (chung cho các game)
game-error-invalid-team-mode = Chế độ đội đã chọn không hợp lệ với số lượng người chơi hiện tại.
