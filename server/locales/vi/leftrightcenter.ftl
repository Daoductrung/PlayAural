game-name-leftrightcenter = Trái, Giữa, Phải

lrc-roll = Gieo { $count } viên xúc xắc
lrc-roll-label = Gieo xúc xắc

lrc-face-left = Trái
lrc-face-center = Giữa
lrc-face-right = Phải
lrc-face-dot = Chấm

lrc-you-roll = Bạn gieo được { $results }.
lrc-player-rolls = { $player } gieo được { $results }.
lrc-you-roll-brief = Bạn: { $results }.
lrc-player-rolls-brief = { $player }: { $results }.

lrc-you-pass-left = Bạn chuyển { $count } chip sang trái cho { $target }. Bạn còn { $remaining } chip; { $target } hiện có { $target_total } chip.
lrc-player-passes-left = { $player } chuyển { $count } chip sang trái cho { $target }. { $player } còn { $remaining } chip; { $target } hiện có { $target_total } chip.
lrc-you-pass-left-brief = Bạn, sang trái cho { $target }: { $count }. Còn: { $remaining }.
lrc-player-passes-left-brief = { $player }, sang trái cho { $target }: { $count }. Còn: { $remaining }.

lrc-you-pass-right = Bạn chuyển { $count } chip sang phải cho { $target }. Bạn còn { $remaining } chip; { $target } hiện có { $target_total } chip.
lrc-player-passes-right = { $player } chuyển { $count } chip sang phải cho { $target }. { $player } còn { $remaining } chip; { $target } hiện có { $target_total } chip.
lrc-you-pass-right-brief = Bạn, sang phải cho { $target }: { $count }. Còn: { $remaining }.
lrc-player-passes-right-brief = { $player }, sang phải cho { $target }: { $count }. Còn: { $remaining }.

lrc-you-pass-center = Bạn bỏ { $count } chip vào hũ giữa. Bạn còn { $remaining } chip; hũ giữa hiện có { $center } chip.
lrc-player-passes-center = { $player } bỏ { $count } chip vào hũ giữa. { $player } còn { $remaining } chip; hũ giữa hiện có { $center } chip.
lrc-you-pass-center-brief = Bạn, vào giữa: { $count }. Còn: { $remaining }. Hũ giữa: { $center }.
lrc-player-passes-center-brief = { $player }, vào giữa: { $count }. Còn: { $remaining }. Hũ giữa: { $center }.

lrc-you-keep-all = Tất cả xúc xắc của bạn đều ra Chấm, nên bạn giữ nguyên { $count } chip.
lrc-player-keeps-all = Tất cả xúc xắc của { $player } đều ra Chấm, nên { GENDER_TERM($player_gender, "subject") } giữ nguyên { $count } chip.
lrc-you-keep-all-brief = Bạn: không chuyển chip; còn { $count }.
lrc-player-keeps-all-brief = { $player }: không chuyển chip; còn { $count }.

lrc-you-skip-no-chips = Bạn không còn chip nên lượt này được bỏ qua. Bạn vẫn còn trong cuộc và có thể nhận chip từ hai người ngồi cạnh.
lrc-player-skips-no-chips = { $player } không còn chip nên lượt này được bỏ qua. { GENDER_TERM($player_gender, "subject-capitalized") } vẫn còn trong cuộc và có thể nhận chip từ hai người ngồi cạnh.
lrc-you-skip-no-chips-brief = Bạn: hết chip; bỏ lượt.
lrc-player-skips-no-chips-brief = { $player }: hết chip; bỏ lượt.

lrc-you-win = Bạn là người cuối cùng còn chip và giành chiến thắng với { $count } chip trước mặt. Bạn nhận thêm { $center } chip trong hũ giữa.
lrc-player-wins = { $player } là người cuối cùng còn chip và giành chiến thắng với { $count } chip trước mặt. { GENDER_TERM($player_gender, "subject-capitalized") } nhận thêm { $center } chip trong hũ giữa.
lrc-you-win-brief = Bạn thắng. Trước mặt: { $count }. Hũ giữa: { $center }.
lrc-player-wins-brief = { $player } thắng. Trước mặt: { $count }. Hũ giữa: { $center }.

lrc-roll-already-resolving = Lượt gieo của bạn đang được xử lý. Hãy chờ chuyển chip xong.
lrc-no-chips-to-roll = Bạn không có chip để gieo. Hệ thống sẽ tự động bỏ qua lượt của bạn.

lrc-center-pot = Hũ giữa: { $count } chip.
lrc-check-center = Kiểm tra hũ giữa
lrc-check-last-roll = Xem lần gieo gần nhất
lrc-last-roll-none = Chưa có ai gieo xúc xắc.
lrc-last-roll-you = Lần gieo gần nhất của bạn là { $results }.
lrc-last-roll-player = Lần gieo gần nhất của { $player } là { $results }.

lrc-set-starting-chips = Số chip ban đầu: { $count }
lrc-enter-starting-chips = Nhập số chip ban đầu:
lrc-option-changed-starting-chips = Đã đặt số chip ban đầu thành { $count }.
leftrightcenter-desc-starting-chips = Số chip ban đầu của mỗi người trong Trái, Giữa, Phải (mặc định 3, phạm vi 1-10).
lrc-error-starting-chips-invalid = Số chip ban đầu phải từ { $min } đến { $max }; giá trị hiện tại là { $count }.

lrc-line-format = { $player }: { $chips } chip
