# Thông báo trò chơi Nine

# Tên và mô tả trò chơi
game-name-nine = Nine
nine-description = Một trò chơi bài Nga phổ biến, nơi người chơi xây các dãy bài theo chất.

# Kiểm tra số người chơi
nine-error-invalid-player-count = Nine dùng bộ 36 lá và chỉ xếp bàn đúng 3, 4 hoặc 6 người chơi.
nine-error-starting-nine-missing = Không tìm thấy 9 rô trên tay bất kỳ người chơi nào. Ván chơi không thể tiếp tục.

# Thông báo chia bài
nine-player-nine-deal = Chia { $cards } lá cho mỗi người chơi.

# Bắt đầu trò chơi
nine-you-start-player-announcement = Bạn có 9 rô và bắt đầu ván chơi.
nine-player-start-player-announcement = { $player } có 9 rô và bắt đầu ván chơi.
nine-you-start-player-announcement-brief = Bạn bắt đầu với 9 rô.
nine-player-start-player-announcement-brief = { $player } bắt đầu với 9 rô.

# Lượt đi
nine-you-plays-starting-nine = Bạn đánh { $card } để mở bàn.
nine-player-plays-starting-nine = { $player } đánh { $card } để mở bàn.
nine-you-plays-starting-nine-brief = Bạn đánh { $card }.
nine-player-plays-starting-nine-brief = { $player }: { $card }.

nine-you-plays-nine-suit = Bạn đánh { $card } để mở dãy { $suit }.
nine-player-plays-nine-suit = { $player } đánh { $card } để mở dãy { $suit }.
nine-you-plays-nine-suit-brief = Bạn mở dãy { $suit } bằng { $card }.
nine-player-plays-nine-suit-brief = { $player } mở dãy { $suit } bằng { $card }.

nine-you-extend-sequence = Bạn nối dãy { $suit } bằng { $card }.
nine-player-extend-sequence = { $player } nối dãy { $suit } bằng { $card }.
nine-you-extend-sequence-brief = Bạn đánh { $card } vào dãy { $suit }.
nine-player-extend-sequence-brief = { $player }: { $card } vào dãy { $suit }.

nine-you-skips-turn = Bạn không có lá hợp lệ để đánh, nên lượt của bạn bị bỏ qua.
nine-player-skips-turn = { $player } không có lá hợp lệ để đánh, nên lượt { GENDER_TERM($player_gender, "possessive-determiner") } bị bỏ qua.
nine-you-skips-turn-brief = Bạn bỏ lượt; không có lá hợp lệ.
nine-player-skips-turn-brief = { $player } bỏ lượt; không có lá hợp lệ.

# Lý do không thể đánh bài
nine-reason-not-your-turn = Chưa đến lượt bạn.
nine-reason-card-slot-gone = Lá bài đó không còn trên tay bạn. Menu bài trên tay đã được làm mới.
nine-reason-must-play-starting-nine = Nước đầu tiên phải là { $starting_card }. Chưa thể đánh { $card } trước khi bàn được mở.
nine-reason-nine-already-started = Không thể đánh { $card } vì dãy { $suit } đã được mở rồi.
nine-reason-cannot-extend = { $card } không nối được vào dãy { $suit }. Hãy đánh lá liền dưới hoặc liền trên một đầu của dãy đó.
nine-reason-unopened-suit = Không thể đánh { $card } vì dãy { $suit } chưa được mở. Hãy mở chất đó bằng lá 9 trước.
nine-reason-must-skip = Bạn không có lá hợp lệ để đánh; lượt của bạn sẽ được tự động bỏ qua.
nine-reason-generic = Lá bài đó hiện không đánh được.

# Chiến thắng
nine-you-wins-game = Bạn đã hết bài và thắng ván chơi!
nine-player-wins-game = { $player } đã hết bài và thắng ván chơi!
nine-you-wins-game-brief = Bạn thắng!
nine-player-wins-game-brief = { $player } thắng!
nine-player-game-ended = Ván Nine đã kết thúc.
nine-you-game-ended = Ván Nine đã kết thúc.

nine-you-win = Bạn thắng!
nine-you-lose = Bạn thua!
nine-final-score = Số bài còn lại: { $score }

# Trạng thái
nine-status = { $name }: còn { $cards_left } lá bài.
nine-status-sequence = Dãy { $suit }: { $sequence }.
nine-status-no-sequence = Chưa có dãy { $suit } nào được mở.
nine-sequence-range = từ { $low } đến { $high }
nine-none = không có
nine-action-check-sequences = Xem các dãy bài
nine-action-check-hand-counts = Xem số bài trên tay
nine-status-player-hand-count = { $player }: { $count } lá bài
