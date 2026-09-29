game-name-threes = Ba điểm

threes-roll = Gieo xúc xắc
threes-bank = Chốt điểm và kết thúc lượt
threes-check-hand = Kiểm tra xúc xắc

threes-you-rolled = Bạn gieo được: { $dice }.
threes-you-rolled-brief = Gieo { $dice }.
threes-player-rolled = { $player } gieo được: { $dice }.
threes-player-rolled-brief = { $player }: { $dice }.

threes-turn-you = Đến lượt bạn ở vòng { $round } trên { $total }. Tổng điểm hiện tại của bạn là { $score }; ai có tổng thấp nhất sẽ thắng.
threes-turn-you-brief = Đến lượt bạn. Tổng { $score }.
threes-turn-other = Đến lượt { $player } ở vòng { $round } trên { $total }. Tổng điểm hiện tại { GENDER_TERM($player_gender, "possessive-determiner") } là { $score }.
threes-turn-other-brief = Đến lượt { $player }. Tổng { $score }.

threes-you-keep = Bạn giữ viên số { $index }, mặt { $die }.
threes-you-keep-brief = Giữ { $die }.
threes-player-keeps = { $player } giữ viên số { $index }, mặt { $die }.
threes-player-keeps-brief = { $player } giữ { $die }.
threes-you-unkeep = Bạn bỏ giữ viên số { $index }, mặt { $die }, để có thể gieo lại.
threes-you-unkeep-brief = Gieo lại { $die }.
threes-player-unkeeps = { $player } bỏ giữ viên số { $index }, mặt { $die }, để có thể gieo lại.
threes-player-unkeeps-brief = { $player } gieo lại { $die }.

threes-your-dice = Xúc xắc của bạn là { $dice }. Nếu chốt ngay, lượt này có { $score } điểm, còn { $remaining } viên chưa khóa.
threes-player-dice = Xúc xắc của { $player } là { $dice }. Nếu chốt ngay, lượt này có { $score } điểm, còn { $remaining } viên chưa khóa.
threes-no-dice-yet = Bạn chưa gieo xúc xắc trong lượt này.
threes-dice-locked = đã khóa
threes-dice-kept = đang giữ
threes-dice-format-status = { $value } ({ $status })
threes-die-index = Viên { $index }
threes-die-value = Giữ { $value }
threes-die-kept-label = Gieo lại { $value }
threes-die-locked-label = { $value } đã khóa

threes-you-scored = Bạn ghi { $score } điểm trong lượt này. Tổng điểm của bạn hiện là { $total }.
threes-you-scored-brief = Ghi { $score }. Tổng { $total }.
threes-scored = { $player } ghi { $score } điểm trong lượt này. Tổng điểm { GENDER_TERM($player_gender, "possessive-determiner") } hiện là { $total }.
threes-scored-brief = { $player }: { $score }, tổng { $total }.
threes-you-shot-moon = Bạn chạm trăng với năm mặt 6 và ghi { $score } điểm. Tổng điểm của bạn hiện là { $total }.
threes-you-shot-moon-brief = Chạm trăng: { $score }. Tổng { $total }.
threes-shot-moon = { $player } chạm trăng với năm mặt 6 và ghi { $score } điểm. Tổng điểm { GENDER_TERM($player_gender, "possessive-determiner") } hiện là { $total }.
threes-shot-moon-brief = { $player } chạm trăng: { $score }, tổng { $total }.

threes-round-start = Bắt đầu vòng { $round } trên { $total }.
threes-round-start-brief = Vòng { $round }.
threes-round-scores-header = Điểm sau vòng { $round }:
threes-round-scores-header-brief = Điểm vòng { $round }:
threes-score-pair = { $player }: { $score }

threes-winner = { $player } thắng với { $score } điểm!
threes-winner-you = Bạn thắng Ba điểm với { $score } điểm!
threes-winner-you-brief = Bạn thắng với { $score }.
threes-winner-other = { $player } thắng Ba điểm với { $score } điểm!
threes-winner-other-brief = { $player } thắng với { $score }.
threes-tie = { $players } hòa nhau ở tổng thấp nhất với { $score } điểm!
threes-tie-brief = Hòa: { $players }, { $score }.
threes-tie-you = Bạn hòa với { $players } ở tổng thấp nhất là { $score } điểm!
threes-tie-you-brief = Bạn hòa với { $players } ở { $score }.

threes-set-rounds = Số vòng: { $rounds }
threes-enter-rounds = Nhập số vòng:
threes-option-changed-rounds = Số vòng đã được đặt thành { $rounds }.
threes-desc-rounds = Số vòng sẽ chơi. Mỗi người chơi một lượt trong mỗi vòng, và tổng điểm thấp nhất sẽ thắng (mặc định 10, phạm vi 1-20).

threes-error-roll-not-playing = Bạn không thể gieo vì Ba điểm chưa bắt đầu.
threes-error-roll-no-turn = Bạn không thể gieo vì hiện không có lượt chơi đang hoạt động.
threes-error-roll-not-your-turn = Bạn chưa thể gieo vì đang là lượt của { $player }.
threes-error-roll-last-die = Bạn không thể gieo lại vì chỉ còn một viên chưa khóa; lượt này phải được tính điểm ngay.
threes-error-roll-must-keep = Hãy giữ ít nhất một viên chưa khóa trước khi gieo lại.
threes-error-bank-not-playing = Bạn không thể chốt điểm vì Ba điểm chưa bắt đầu.
threes-error-bank-no-turn = Bạn không thể chốt điểm vì hiện không có lượt chơi đang hoạt động.
threes-error-bank-not-your-turn = Bạn chưa thể chốt điểm vì đang là lượt của { $player }.
threes-error-bank-roll-first = Hãy gieo xúc xắc trước khi chốt điểm lượt này.
threes-error-bank-keep-all = Hãy giữ tất cả các viên chưa khóa trước khi chốt điểm, để toàn bộ lượt chơi đã được quyết định.
threes-error-check-not-playing = Chỉ có thể kiểm tra xúc xắc sau khi Ba điểm đã bắt đầu.
threes-error-check-no-turn = Không thể kiểm tra xúc xắc vì hiện không có lượt chơi đang hoạt động.
threes-error-check-your-dice-not-rolled = Bạn chưa gieo, nên hiện chưa có xúc xắc để kiểm tra.
threes-error-check-player-dice-not-rolled = { $player } chưa gieo, nên hiện chưa có xúc xắc để kiểm tra.
threes-error-toggle-last-die = Bạn không thể đổi viên chưa khóa cuối cùng; lượt này phải được tính điểm từ đây.
threes-error-rounds-out-of-range = Ba điểm không thể bắt đầu với { $rounds } vòng. Hãy chọn từ { $min } đến { $max }.
threes-invalid-die-index = Viên xúc xắc đó không khả dụng trong lượt Ba điểm này.

threes-must-keep = Bạn phải giữ ít nhất một viên trước khi gieo lại.
threes-must-bank = Bạn phải chốt điểm ngay.
threes-roll-first = Bạn cần gieo xúc xắc trước.
threes-keep-all-first = Hãy giữ tất cả xúc xắc trước khi chốt điểm.
threes-last-die = Đây là viên xúc xắc cuối cùng của bạn.

threes-line-format = { $rank }. { $player }: { $points }
