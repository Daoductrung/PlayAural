# Ninety Nine - Bản dịch Tiếng Việt
# Các thông báo khớp chính xác với bản v10

# Thông tin trò chơi
ninetynine-name = Chín Mươi Chín
ninetynine-description = Một trò chơi bài mà người chơi cố gắng tránh làm tổng điểm vượt quá 99. Người trụ lại cuối cùng sẽ chiến thắng!

# Vòng chơi
ninetynine-round = Vòng { $round }.

# Lượt chơi
ninetynine-player-turn = Lượt của { $player }.

# Đánh bài - khớp chính xác với v10
ninetynine-you-play = Bạn đánh lá { $card }. Tổng điểm hiện là { $count }.
ninetynine-player-plays = { $player } đánh lá { $card }. Tổng điểm hiện là { $count }.

# Đổi chiều
ninetynine-direction-reverses = Đổi chiều chơi!

# Mất lượt
ninetynine-player-skipped = { $player } bị mất lượt.

# Mất xu - khớp chính xác với v10
ninetynine-you-lose-tokens = Bạn mất { $amount } { $amount ->
    [one] xu
   *[other] xu
}.
ninetynine-player-loses-tokens = { $player } mất { $amount } { $amount ->
    [one] xu
   *[other] xu
}.

# Loại bỏ
ninetynine-player-eliminated = { $player } đã bị loại!

# Kết thúc trò chơi
ninetynine-player-wins = { $player } thắng trò chơi!
ninetynine-end-score = { $rank }. { $player }: { $tokens } { $tokens ->
    [one] xu
   *[other] xu
}

# Chia bài
ninetynine-you-deal = Bạn chia bài.
ninetynine-player-deals = { $player } chia bài.

# Rút bài
ninetynine-you-draw = Bạn rút lá { $card }.
ninetynine-player-draws = { $player } rút một lá bài.

# Không có bài hợp lệ
ninetynine-no-valid-cards = { $player } không có bài hợp lệ để không vượt quá 99!

# Trạng thái - cho phím C
ninetynine-current-count = Tổng điểm đang là { $count }.

# Lựa chọn cho quân Át
ninetynine-ace-choice = Đánh Át tính là +1 hay +11?
ninetynine-ace-add-eleven = Cộng 11
ninetynine-ace-add-one = Cộng 1

# Lựa chọn cho quân 10
ninetynine-ten-choice = Đánh 10 tính là +10 hay -10?
ninetynine-ten-add = Cộng 10
ninetynine-ten-subtract = Trừ 10
ninetynine-choice-1 = Lựa chọn 1
ninetynine-choice-2 = Lựa chọn 2

# Rút bài thủ công
ninetynine-draw-card = Rút bài
ninetynine-draw-prompt = Nhấn Space hoặc D để rút bài.

# Tùy chọn
ninetynine-set-tokens = Số xu khởi điểm: { $tokens }
ninetynine-enter-tokens = Nhập số xu khởi điểm:
ninetynine-option-changed-tokens = Số xu khởi điểm được đặt là { $tokens }.
ninetynine-set-rules = Biến thể luật: { $rules }
ninetynine-select-rules = Chọn biến thể luật
ninetynine-option-changed-rules = Biến thể luật được đặt là { $rules }.
ninetynine-set-hand-size = Số bài trên tay: { $size }
ninetynine-enter-hand-size = Nhập số bài trên tay:
ninetynine-option-changed-hand-size = Số bài trên tay được đặt là { $size }.
ninetynine-set-autodraw = Tự động rút bài: { $enabled }
ninetynine-option-changed-autodraw = Tự động rút bài được đặt là { $enabled }.

# Thông báo biến thể luật (hiển thị khi bắt đầu game)
ninetynine-rules-quentin = Luật Quentin C.
ninetynine-rules-rsgames = Luật RS Games.

# Các lựa chọn biến thể luật (hiển thị trong menu)
ninetynine-rules-variant-quentin_c = Quentin C
ninetynine-rules-variant-rs_games = RS Games

# Lý do hành động bị vô hiệu hóa
ninetynine-choose-first = Bạn cần đưa ra lựa chọn trước.
ninetynine-draw-first = Bạn cần rút bài trước.
ninetynine-check-count = Kiểm tra tổng điểm
