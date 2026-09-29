game-name-bingo = Bingo

bingo-pattern-line = Bất kỳ hàng nào
bingo-pattern-four-corners = Bốn góc
bingo-pattern-letter-x = Chữ X
bingo-pattern-blackout = Kín cả thẻ

bingo-call-interval-5 = 5 giây
bingo-call-interval-15 = 15 giây
bingo-call-interval-30 = 30 giây
bingo-call-interval-45 = 45 giây
bingo-call-interval-60 = 60 giây

bingo-set-pattern = Mẫu thắng: { $pattern }
bingo-select-pattern = Chọn mẫu thắng:
bingo-option-changed-pattern = Mẫu thắng hiện là { $pattern }.
bingo-desc-pattern = Mẫu mà một thẻ phải hoàn thành để thắng. Bất kỳ hàng nào chấp nhận một hàng ngang, cột dọc, hoặc đường chéo đầy đủ. Bốn góc yêu cầu cả bốn ô góc. Chữ X yêu cầu cả hai đường chéo. Kín cả thẻ yêu cầu toàn bộ thẻ.

bingo-set-call-interval = Đọc số mỗi { $seconds }
bingo-select-call-interval = Chọn khoảng thời gian đọc số:
bingo-option-changed-interval = Số mới sẽ được đọc mỗi { $seconds }.
bingo-desc-call-interval = Thời gian người đọc số chờ giữa mỗi lần thông báo số (mặc định 15, phạm vi từ 5 đến 60 giây).

bingo-cell-free = Ô miễn phí.
bingo-cell-marked = { $letter } { $number }, đã đánh dấu.
bingo-cell-unmarked = { $letter } { $number }, chưa đánh dấu.
bingo-cell-is-free = Ô này đã là ô miễn phí.
bingo-you-already-won = Bạn đã có Bingo trong vòng này rồi.

bingo-you-mark = Đã đánh dấu { $letter } { $number }.
bingo-you-unmark = Đã bỏ đánh dấu { $letter } { $number }.

bingo-claim-bingo = Hô Bingo!
bingo-repeat-call = Lặp lại số vừa đọc
bingo-check-called = Xem các số đã đọc
bingo-no-calls-yet = Chưa có số nào được đọc.
bingo-claim-in-progress = Đang kiểm tra một yêu cầu Bingo khác. Hãy thử lại sau một chút.
bingo-claim-in-progress-you = Yêu cầu của bạn đang được kiểm tra.
bingo-claim-wait-for-call = Hãy đợi số đang được rút được thông báo, rồi thử lại.
bingo-claim-unchanged = Thẻ của bạn không thay đổi kể từ lần bị từ chối trước. Hãy đánh dấu thêm một số hoặc đợi lượt đọc số tiếp theo rồi hãy hô Bingo lại.
bingo-checking-claim-you = Bạn hô Bingo. Đang kiểm tra thẻ của bạn...
bingo-checking-claim = { $player } hô Bingo. Đang kiểm tra thẻ...
bingo-whose-turn-checking = Đang kiểm tra thẻ của { $player }...
bingo-whose-turn-checking-you = Thẻ của bạn đang được kiểm tra...
bingo-whose-turn-drawing = Đang rút số tiếp theo...
bingo-whose-turn-waiting = { $seconds ->
    [one] Số tiếp theo sau { $seconds } giây.
   *[other] Số tiếp theo sau { $seconds } giây.
}
bingo-claim-incorrect-you = Thẻ không hợp lệ.
bingo-claim-incorrect = Thẻ của { $player } không hợp lệ.
bingo-claim-incomplete-you = Bạn chưa hoàn thành mẫu thắng.
bingo-claim-incomplete = { $player } chưa hoàn thành mẫu thắng.
bingo-marked-number-not-called = Bạn đã đánh dấu { $letter } { $number }, nhưng số đó chưa được đọc.

bingo-last-call = { $letter } { $number }

bingo-status-called-count = Đã đọc { $count } trên { $total } số.
bingo-status-called-entry = { $letter } { $number }

bingo-game-start = Bingo bắt đầu! Mẫu thắng: { $pattern }. Một số mới sẽ được đọc mỗi { $interval } giây. Đánh dấu thẻ của bạn, rồi nhấn B để hô Bingo khi có Bingo.
bingo-game-start-touch = Bingo bắt đầu! Mẫu thắng: { $pattern }. Một số mới sẽ được đọc mỗi { $interval } giây. Đánh dấu thẻ của bạn, rồi dùng thao tác chạm và giữ của ứng dụng ở bất kỳ đâu trên thẻ, hoặc chọn Hô Bingo, để hô Bingo khi có Bingo.
bingo-game-start-spectator = Bingo bắt đầu! Mẫu thắng: { $pattern }. Một số mới sẽ được đọc mỗi { $interval } giây.
bingo-number-called = { $letter } { $number }

bingo-claim-correct-you = Đúng rồi! Thẻ hợp lệ. Bạn thắng với { $numbers }!
bingo-claim-correct = Đúng rồi! Thẻ hợp lệ. { $player } thắng với { $numbers }!
bingo-claim-correct-no-numbers-you = Đúng rồi! Thẻ hợp lệ. Bạn thắng!
bingo-claim-correct-no-numbers = Đúng rồi! Thẻ hợp lệ. { $player } thắng!
bingo-deck-exhausted = Đã đọc hết 75 số. Vòng chơi kết thúc tại đây.

bingo-error-invalid-interval = "{ $value }" không phải là khoảng thời gian đọc số hợp lệ.
bingo-error-invalid-pattern = { $value } không phải là mẫu thắng hợp lệ.

bingo-end-calls = { $count ->
    [one] Đã đọc { $count } số trong vòng này.
   *[other] Đã đọc { $count } số trong vòng này.
}
bingo-end-winner-line = Người thắng: { $player }
bingo-end-no-winner = Không có yêu cầu Bingo hợp lệ nào được thực hiện trong vòng này.
