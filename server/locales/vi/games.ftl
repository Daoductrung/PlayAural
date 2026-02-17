# Shared game messages for PlayAural
# These messages are common across multiple games

# Game names
game-name-ninetynine = Ninety Nine

# Round and turn flow
game-round-start = Vòng { $round }.
game-round-end = Vòng { $round } hoàn tất.
game-turn-start = Lượt của { $player }.
game-no-turn = Hiện không phải lượt của ai.

# Score display
game-scores-header = Điểm hiện tại:
game-score-line = { $player }: { $score } điểm
game-score-line-target = { $player }: { $score }/{ $target } điểm
game-points = { $count } { $count ->
    [one] điểm
   *[other] điểm
}
game-final-scores-header = Điểm tổng kết:

# Win/loss
game-winner = { $player } thắng!
game-winner-score = { $player } thắng với { $score } điểm!
game-tiebreaker = Hòa! Vào vòng phân định thắng thua!
game-tiebreaker-players = Hòa giữa { $players }! Vào vòng phân định thắng thua!
game-eliminated = { $player } đã bị loại với { $score } điểm.

# Common options
game-set-target-score = Điểm mục tiêu: { $score }
game-enter-target-score = Nhập điểm mục tiêu:
game-option-changed-target = Điểm mục tiêu đã được đặt là { $score }.

game-set-team-mode = Chế độ đội: { $mode }
game-select-team-mode = Chọn chế độ đội
game-option-changed-team = Chế độ đội đã được đặt là { $mode }.
game-team-mode-individual = Cá nhân
game-team-mode-x-teams-of-y = { $num_teams } đội, mỗi đội { $team_size } người
game-team-name = Đội { $index }

# Boolean option values
option-on = bật
option-off = tắt

# Status box
status-box-closed = Đã đóng thông tin trạng thái.

# Game end
game-leave = Rời trò chơi

# Round timer
round-timer-paused = { $player } đã tạm dừng trò chơi (nhấn p để bắt đầu vòng tiếp theo).
round-timer-resumed = Đồng hồ vòng chơi đã chạy lại.
round-timer-countdown = Vòng tiếp theo trong { $seconds } giây...

# Dice games - keeping/releasing dice
dice-keeping = Giữ lại { $value }.
dice-rerolling = Gieo lại { $value }.
dice-locked = Viên xúc xắc đó đã bị khóa và không thể thay đổi.
dice-status-label-locked = { $value } (đã khóa)
dice-status-label-kept = { $value } (đang giữ)

# Dealing (card games)
game-deal-counter = Chia ván { $current }/{ $total }.
game-you-deal = Bạn chia bài.
game-player-deals = { $player } chia bài.

# Card names
card-name = { $rank } { $suit }
no-cards = Không có bài

# Suit names
suit-diamonds = rô
suit-clubs = tép
suit-hearts = cơ
suit-spades = bích

# Rank names
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
rank-jack = J
rank-jack-plural = J
rank-queen = Q
rank-queen-plural = Q
rank-king = K
rank-king-plural = K

# Poker hand descriptions
poker-high-card-with = Mậu thầu { $high }, kèm { $rest }
poker-high-card = Mậu thầu { $high }
poker-pair-with = Đôi { $pair }, kèm { $rest }
poker-pair = Đôi { $pair }
poker-two-pair-with = Hai đôi, { $high } và { $low }, kèm { $kicker }
poker-two-pair = Hai đôi, { $high } và { $low }
poker-trips-with = Bộ ba { $trips }, kèm { $rest }
poker-trips = Bộ ba { $trips }
poker-straight-high = Sảnh tới { $high }
poker-flush-high-with = Thùng dẫn đầu bởi { $high }, kèm { $rest }
poker-full-house = Cù lũ, { $trips } đè { $pair }
poker-quads-with = Tứ quý { $quads }, kèm { $kicker }
poker-quads = Tứ quý { $quads }
poker-straight-flush-high = Thùng phá sảnh tới { $high }
poker-unknown-hand = Bài không xác định

# Validation errors (common across games)
game-error-invalid-team-mode = Chế độ đội đã chọn không hợp lệ với số lượng người chơi hiện tại.

# Documentation
documentation-menu = Tài liệu
introduction = Giới thiệu
community-rules = Nội quy cộng đồng
global-keys = Phím tắt toàn cục
game-rules = Luật chơi
document-not-found = Không tìm thấy tài liệu.
help = Trợ giúp
