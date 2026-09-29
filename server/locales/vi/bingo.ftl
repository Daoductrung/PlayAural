game-name-bingo = Bingo

bingo-pattern-line = Một đường bất kỳ
bingo-pattern-four-corners = Bốn góc
bingo-pattern-letter-x = Hình chữ X
bingo-pattern-blackout = Phủ kín thẻ

bingo-call-interval-5 = 5 giây
bingo-call-interval-15 = 15 giây
bingo-call-interval-30 = 30 giây
bingo-call-interval-45 = 45 giây
bingo-call-interval-60 = 60 giây

bingo-set-pattern = Mẫu thắng: { $pattern }
bingo-select-pattern = Chọn mẫu thắng:
bingo-option-changed-pattern = Mẫu thắng hiện là { $pattern }.
bingo-desc-pattern = Mẫu cần hoàn thành để thắng. Một đường bất kỳ gồm đủ năm ô theo hàng ngang, cột dọc hoặc đường chéo. Bốn góc cần cả bốn ô góc. Hình chữ X cần cả hai đường chéo. Phủ kín thẻ cần toàn bộ các ô.

bingo-set-call-interval = Nhịp xướng số: { $seconds }
bingo-select-call-interval = Chọn nhịp xướng số:
bingo-option-changed-interval = Nhịp xướng số dự kiến hiện là { $seconds }.
bingo-desc-call-interval = Thời gian dự kiến từ lúc xướng một số đến số kế tiếp. Trò chơi luôn dành một khoảng ngắn để người chơi hô Bingo, nên nhịp nhanh nhất có thể kéo dài hơn một chút.

bingo-cell-free = Ô miễn phí ở giữa, đã được đánh dấu sẵn.
bingo-cell-marked = { $letter } { $number }, đã đánh dấu.
bingo-cell-unmarked = { $letter } { $number }, chưa đánh dấu.
bingo-cell-is-free = Ô miễn phí ở giữa đã được đánh dấu sẵn.
bingo-you-already-won = Bạn đã có Bingo trong vòng này rồi.

bingo-you-mark = Đã đánh dấu { $letter } { $number }.
bingo-you-unmark = Đã bỏ đánh dấu { $letter } { $number }.

bingo-claim-bingo = Hô Bingo!
bingo-repeat-call = Nghe lại số vừa xướng
bingo-check-called = Xem các số đã xướng
bingo-no-calls-yet = Chưa có số nào được xướng.
bingo-claim-in-progress = Đang kiểm tra lời hô Bingo của người khác. Vui lòng đợi một chút.
bingo-claim-in-progress-you = Lời hô Bingo của bạn đang được kiểm tra.
bingo-claim-wait-for-call = Hãy đợi số đang được rút được xướng lên rồi thử lại.
bingo-claim-unchanged = Thẻ của bạn chưa thay đổi kể từ lần kiểm tra không thành công. Hãy đánh dấu hoặc bỏ dấu ở một ô, hoặc chờ số tiếp theo rồi hô Bingo lại.
bingo-checking-claim-you = Bạn hô Bingo! Đang kiểm tra thẻ của bạn...
bingo-checking-claim = { $player } hô Bingo! Đang kiểm tra thẻ...
bingo-whose-turn-checking = Đang kiểm tra thẻ của { $player }...
bingo-whose-turn-checking-you = Thẻ của bạn đang được kiểm tra...
bingo-whose-turn-checking-card = Đang kiểm tra một thẻ Bingo...
bingo-whose-turn-drawing = Số tiếp theo đang được rút...
bingo-whose-turn-waiting = { $seconds ->
    [one] Số tiếp theo sau { $seconds } giây.
   *[other] Số tiếp theo sau { $seconds } giây.
}
bingo-claim-incorrect-you = Thẻ của bạn chưa có Bingo hợp lệ.
bingo-claim-incorrect = Thẻ của { $player } chưa có Bingo hợp lệ.
bingo-claim-incomplete-you = Thẻ của bạn chưa hoàn thành mẫu thắng.
bingo-claim-incomplete = Thẻ của { $player } chưa hoàn thành mẫu thắng.
bingo-marked-number-not-called = Bạn đã đánh dấu { $letter } { $number }, nhưng số này chưa được xướng.

bingo-last-call = Số vừa xướng: { $letter } { $number }

bingo-status-called-count = Đã xướng { $count } trên tổng số { $total } số.
bingo-status-called-entry = { $letter } { $number }

bingo-game-start = Vòng Bingo bắt đầu! Mẫu thắng là { $pattern }. Các số sẽ được xướng theo nhịp dự kiến một số mỗi { $interval } giây, đồng thời luôn chừa thời gian để hô Bingo. Hãy đánh dấu thẻ rồi nhấn B khi bạn đã sẵn sàng.
bingo-game-start-touch = Vòng Bingo bắt đầu! Mẫu thắng là { $pattern }. Các số sẽ được xướng theo nhịp dự kiến một số mỗi { $interval } giây, đồng thời luôn chừa thời gian để hô Bingo. Hãy đánh dấu thẻ, rồi dùng thao tác chạm giữ trên thẻ hoặc chọn Hô Bingo.
bingo-game-start-spectator = Vòng Bingo bắt đầu! Mẫu thắng là { $pattern }. Các số sẽ được xướng theo nhịp dự kiến một số mỗi { $interval } giây, đồng thời luôn chừa thời gian để người chơi hô Bingo.
bingo-number-called = { $letter } { $number }

bingo-claim-correct-you = Bingo! Bạn thắng với { $numbers }!
bingo-claim-correct = Bingo! { $player } thắng với { $numbers }!
bingo-claim-correct-no-numbers-you = Bingo! Bạn thắng!
bingo-claim-correct-no-numbers = Bingo! { $player } thắng!
bingo-deck-exhausted = Cả 75 số đã được xướng nhưng không ai hô Bingo hợp lệ. Vòng chơi kết thúc mà không có người thắng.

bingo-error-invalid-interval = "{ $value }" không phải là nhịp xướng số hợp lệ.
bingo-error-invalid-pattern = { $value } không phải là mẫu thắng hợp lệ.

bingo-end-calls = { $count ->
    [one] Đã xướng { $count } số trong vòng này.
   *[other] Đã xướng { $count } số trong vòng này.
}
bingo-end-winner-line = Người thắng: { $player }
bingo-end-no-winner = Không ai hô Bingo hợp lệ trong vòng này.
