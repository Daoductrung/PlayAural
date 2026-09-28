# Bản địa hóa Ống Sắt

game-name-metalpipe = Ống Sắt

metalpipe-mode-single = Một cú phang
metalpipe-mode-multiple = Phang liên hoàn
metalpipe-self-bonk-allowed = cho phép tự phang
metalpipe-self-bonk-blocked = không cho tự phang

metalpipe-game-start = Ống Sắt bắt đầu ở chế độ { $mode }. Cây ống sẽ tự chọn toàn bộ diễn biến.
metalpipe-game-start-brief = Ống Sắt: { $mode }.

metalpipe-you-hit-other = Bạn vung ống sắt và phang trúng { $bonked }. { $bonked } bị loại.
metalpipe-player-hits-you = { $bonker } vung ống sắt và phang trúng bạn. Bạn bị loại.
metalpipe-player-hits-other = { $bonker } vung ống sắt và phang trúng { $bonked }. { $bonked } bị loại.
metalpipe-you-hit-self = Bạn tự phang ống sắt vào mình và bị loại.
metalpipe-player-hits-self = { $bonker } phang ống sắt vào { GENDER_TERM($bonker_gender, "reflexive") } và bị loại.

metalpipe-you-hit-other-brief = Bạn phang { $bonked }. { $bonked } bị loại.
metalpipe-player-hits-you-brief = { $bonker } phang bạn. Bạn bị loại.
metalpipe-player-hits-other-brief = { $bonker } phang { $bonked }. { $bonked } bị loại.
metalpipe-you-hit-self-brief = Bạn tự phang. Bị loại.
metalpipe-player-hits-self-brief = { $bonker } tự phang. Bị loại.

metalpipe-you-win = Bạn thắng. Cây ống đã phán quyết.
metalpipe-you-win-with-others = Bạn thắng cùng { $players }. Cây ống đã phán quyết.
metalpipe-players-win = { $players } thắng. Cây ống đã phán quyết.
metalpipe-you-win-brief = Bạn thắng.
metalpipe-you-win-with-others-brief = Bạn và { $players } thắng.
metalpipe-players-win-brief = Thắng: { $players }.
metalpipe-no-winner = Cây ống không chừa lại người thắng.
metalpipe-no-winner-brief = Không có người thắng.

metalpipe-check-status = Xem trạng thái ống sắt
metalpipe-status-mode = Chế độ: { $mode }; { $self_bonk }.
metalpipe-status-progress = Số cú phang đã xử lý: { $count }. Còn đứng vững: { $alive } trên { $total }.
metalpipe-status-awaiting = Cây ống chưa giáng xuống.
metalpipe-status-last-other = Cú phang gần nhất: { $bonker } phang { $bonked }.
metalpipe-status-last-self = Cú phang gần nhất: { $bonker } phang { GENDER_TERM($bonker_gender, "reflexive") }.
metalpipe-status-player = { $player}: { $status }.
metalpipe-status-alive = Còn đứng vững
metalpipe-status-eliminated = Đã bị loại
metalpipe-no-turn-automatic = Ống Sắt đang tự xử lý. Còn { $alive } người đứng vững, và không ai có lượt thủ công.

metalpipe-final-results = Kết quả Ống Sắt
metalpipe-end-winner = Người thắng: { $player }.
metalpipe-end-winners = Người thắng: { $players }.
metalpipe-line-format = { $player}: { $status }

metalpipe-set-multiple-bonks = Phang liên hoàn: { $enabled }
metalpipe-option-changed-multiple-bonks = Phang liên hoàn đã được đặt thành { $enabled }.
metalpipe-desc-multiple-bonks = Khi bật, cây ống tiếp tục chọn người vung ống và mục tiêu cho đến khi chỉ còn một người đứng vững (mặc định tắt).
metalpipe-set-allow-self-bonk = Cho phép tự phang: { $enabled }
metalpipe-option-changed-allow-self-bonk = Cho phép tự phang đã được đặt thành { $enabled }.
metalpipe-desc-allow-self-bonk = Khi bật, người được chọn để vung ống cũng có thể trở thành mục tiêu (mặc định bật).
