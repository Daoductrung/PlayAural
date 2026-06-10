# Bản địa hóa Senet

game-name-senet = Senet

# Bắt đầu trò chơi
senet-game-started = { $p1 } là người chơi 1, { $p2 } là người chơi 2. { $first } đi trước.

# Tung que
senet-throw-you = Bạn tung được { $result }.{ $bonus ->
    [yes] {" "}Được tung thêm!
   *[no] {""}
}
senet-throw-other = { $player } tung được { $result }.{ $bonus ->
    [yes] {" "}Được tung thêm!
   *[no] {""}
}

# Di chuyển
senet-move-you = Bạn di chuyển từ ô { $from } đến ô { $to }.
senet-move-other = { $player } di chuyển từ ô { $from } đến ô { $to }.
senet-swap-you = Bạn đổi chỗ với { $opponent } tại ô { $to }. { $opponent } lui về ô { $from }.
senet-swap-other = { $player } đổi chỗ với { $opponent } tại ô { $to }. { $opponent } lui về ô { $from }.
senet-bearoff-you = Bạn đưa quân ra ngoài từ ô { $from }. Còn lại { $remaining } quân.
senet-bearoff-other = { $player } đưa quân ra ngoài từ ô { $from }. Còn lại { $remaining } quân.
senet-water-you = Bạn rơi vào Ngôi Nhà Nước! Quân bị đưa đến ô { $dest }.
senet-water-other = { $player } rơi vào Ngôi Nhà Nước! Quân bị đưa đến ô { $dest }.
senet-happiness-you = Bạn đã đến Ngôi Nhà Hạnh Phúc.
senet-happiness-other = { $player } đã đến Ngôi Nhà Hạnh Phúc.
senet-horus-auto-you = Quân của bạn rời Nhà Horus vì hàng đầu của bạn đã trống. Còn lại { $remaining } quân.
senet-horus-auto-other = Quân của { $player } rời Nhà Horus vì hàng đầu của họ đã trống. Còn lại { $remaining } quân.

# Không có nước đi
senet-no-moves-you = Bạn không có nước đi hợp lệ.
senet-no-moves-other = { $player } không có nước đi hợp lệ.

# Nhãn ô
senet-sq-empty = { $sq }
senet-sq-own = { $sq }, quân của bạn
senet-sq-opponent = { $sq }, { $owner }
senet-sq-empty-special = { $sq }, { $name }
senet-sq-own-special = { $sq }, { $name }, quân của bạn
senet-sq-opponent-special = { $sq }, { $name }, { $owner }

# Tên ô đặc biệt
senet-house-rebirth = Tái Sinh
senet-house-happiness = Hạnh Phúc
senet-house-water = Nước
senet-house-three-truths = Ba Sự Thật
senet-house-re-atum = Re-Atum
senet-house-horus = Horus

# Trạng thái
senet-status = { $p1 }: { $off1 } quân ra. { $p2 }: { $off2 } quân ra.{ $phase ->
    [throwing] {" "}Đang chờ tung.
   *[moving] {" "}Kết quả: { $roll }.
}
senet-sticks = { $result }
senet-sticks-none = Chưa tung.

# Chiến thắng
senet-wins-you = Bạn thắng! Tất cả quân của bạn đã vượt qua ngôi nhà cuối cùng.
senet-wins-other = { $player } thắng! Tất cả quân của họ đã vượt qua ngôi nhà cuối cùng.

# Nhãn hành động
senet-check-status = Trạng thái
senet-check-sticks = Kết quả que
senet-next-piece = Quân tiếp theo
senet-previous-piece = Quân trước
senet-score = { $p1 }: { $off1 } quân. { $p2 }: { $off2 } quân.

# Lỗi
senet-not-your-piece = Đây không phải quân của bạn.
senet-no-piece-there = Không có quân tại ô này.
senet-no-moves-from-here = Không có nước đi hợp lệ từ ô này.
senet-need-throw-first = Bạn cần tung que trước khi chọn quân để di chuyển.
senet-no-movable-pieces = Không quân nào của bạn có thể đi với kết quả tung hiện tại.
senet-error-exactly-two-players = Senet cần đúng 2 người chơi đang tham gia. Hiện có { $count } người chơi.

# Tùy chọn
senet-option-bot-difficulty = Độ khó bot: { $bot_difficulty }
senet-option-select-bot-difficulty = Chọn độ khó bot
senet-option-changed-bot-difficulty = Độ khó bot đã được đặt thành { $bot_difficulty }.
senet-difficulty-random = Ngẫu nhiên
senet-difficulty-simple = Đơn giản
