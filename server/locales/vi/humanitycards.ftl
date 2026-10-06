# Bản địa hóa Humanity Cards (Cards Against Humanity)

game-name-humanitycards = Cards Against Humanity

# Tùy chọn
hc-set-winning-score = Điểm để thắng: { $score }
hc-enter-winning-score = Nhập điểm để thắng:
hc-option-changed-winning-score = Điểm để thắng đã đặt thành { $score }.
hc-desc-winning-score = Số lá bài thắng mà một người chơi cần giành được để thắng cả ván (mặc định 7, phạm vi 3-20).

hc-set-hand-size = Số bài trên tay: { $count }
hc-enter-hand-size = Nhập số bài trên tay:
hc-option-changed-hand-size = Số bài trên tay đã đặt thành { $count }.
hc-desc-hand-size = Số lá bài trả lời mỗi người chơi giữ sau mỗi lần bốc bù. Tay bài lớn hơn có nhiều lựa chọn hơn nhưng vòng chơi có thể kéo dài hơn (mặc định 10, phạm vi 5-15).

hc-set-card-language = Ngôn ngữ lá bài: { $language }
hc-select-card-language = Chọn ngôn ngữ lá bài
hc-option-changed-card-language = Ngôn ngữ lá bài đã đặt thành { $language }.
hc-desc-card-language = Quy định ngôn ngữ của mọi lá câu hỏi và câu trả lời trong ván, độc lập với ngôn ngữ giao diện của từng người chơi (mặc định Tiếng Anh; các lựa chọn gồm Tiếng Anh, Tiếng Tây Ban Nha và Tiếng Bồ Đào Nha (Brazil)).
hc-card-language-pt-br = Tiếng Bồ Đào Nha (Brazil)
hc-card-blank = chỗ trống
hc-card-same-again = lặp lại chính lá bài đó

hc-set-card-packs = Bộ bài (đã chọn { $count } trên { $total })
hc-option-changed-card-packs = Đã thay đổi lựa chọn bộ bài.
hc-desc-card-packs = Chọn các bộ bài câu hỏi và câu trả lời tiếng Anh sẽ được xào vào ván. Những lá trùng khớp hoàn toàn giữa các bộ chỉ được đưa vào một lần. Phải giữ lại ít nhất một bộ bài.
hc-pack-group-current = Bộ chính Hoa Kỳ hiện hành
hc-pack-group-main-decks = Các phiên bản bộ chính
hc-pack-group-official-add-ons = Các bản mở rộng và bộ bài chính thức
hc-pack-group-family = Phiên bản gia đình
hc-pack-group-community = Các bộ bài cộng đồng
hc-pack-group-all = Tất cả bộ bài

hc-set-czar-selection = Cách chọn trọng tài: { $mode }
hc-select-czar-selection = Chọn cách chỉ định trọng tài
hc-option-changed-czar-selection = Cách chọn trọng tài đã đặt thành { $mode }.
hc-desc-czar-selection = Quy định ai làm trọng tài mỗi vòng: luân phiên theo chỗ ngồi, chọn ngẫu nhiên, hoặc người vừa thắng vòng gần nhất.

hc-set-num-judges = Số trọng tài: { $count }
hc-enter-num-judges = Nhập số trọng tài:
hc-option-changed-num-judges = Số trọng tài đã đặt thành { $count }.
hc-desc-num-judges = Số trọng tài cùng chấm mỗi vòng. Số này phải thấp hơn số người chơi để luôn có ít nhất một người nộp bài; khi có nhiều trọng tài, bất kỳ trọng tài nào cũng có thể chọn bài thắng (mặc định 1, phạm vi 1-3).

hc-czar-rotating = Luân phiên
hc-czar-random = Ngẫu nhiên
hc-czar-winner = Người thắng gần nhất

# Diễn biến trò chơi
hc-game-starting = Đang xáo bài...
hc-dealing-cards = Chia { $count } lá bài cho mỗi người chơi.
hc-round-start = Vòng { $round }.

# Thông báo trọng tài
hc-judge-is = { $judges } { $count ->
    [1] là trọng tài
   *[other] là các trọng tài
}.
hc-you-are-judge = Bạn là trọng tài vòng này.
hc-you-and-others-are-judges = Bạn và { $judges } là các trọng tài vòng này.

# Lá bài đen
hc-black-card = Câu hỏi là: { $text }
hc-black-card-draw = Trước tiên, bốc thêm { $count } lá.
hc-black-card-pick = Chọn { $count } lá.
hc-view-black-card = Xem lá bài câu hỏi

# Giai đoạn nộp bài
hc-select-cards = Chọn { $count } { $count ->
    [one] lá bài
   *[other] lá bài
} từ tay bạn.
hc-card-selected = { $text }, đã chọn
hc-card-selected-position = { $text }, đã chọn ở vị trí { $position }
hc-card-not-selected = { $text }
hc-submit-cards = Nộp bài (đã chọn { $selected } trên { $required })
hc-submission-progress = { $submitted } trên { $total } người chơi đã nộp bài.
hc-already-submitted = Bạn đã nộp bài rồi.
hc-you-submitted = Bạn đã nộp bài.
hc-player-submitted = { $player } đã nộp bài { GENDER_TERM($player_gender, "possessive-determiner") }.
hc-judge-cannot-submit = Bạn là trọng tài vòng này, nên không thể nộp câu trả lời.
hc-not-submission-phase = Bạn chỉ có thể chọn và nộp bài trắng trong giai đoạn nộp bài.
hc-card-not-in-hand = Vị trí lá bài đó không có trong tay bạn.
hc-judge-has-no-submission = Trọng tài không có bài nộp để xem trước trong vòng này.
hc-no-submission-active = Hiện không có bài nộp nào để xem trước.
hc-wrong-card-count = Bạn cần chọn đúng { $count } { $count ->
    [one] lá bài
   *[other] lá bài
}.
hc-selection-full = Bạn đã chọn đủ { $count } lá bài. Hãy bỏ chọn một lá trước khi chọn lá khác.

# Giai đoạn chấm bài
hc-judging-start = Đã đủ bài! Đến lúc chấm.
hc-choose-best-card = Chọn lá bài hay nhất
hc-choose-best-card-for = Chọn lá bài hay nhất khớp với: { $prompt }
hc-card-number = Lá bài { $number }
hc-submission-number = Bài nộp { $number }
hc-only-judges-pick = Chỉ trọng tài mới có thể chọn bài thắng cuộc.
hc-not-judging-phase = Bạn chỉ có thể chọn bài thắng trong giai đoạn chấm bài.
hc-submission-not-available = Bài nộp đó không còn khả dụng.

# Kết quả
hc-you-win-round = Bạn thắng vòng này! Điểm của bạn hiện là { $score }.
hc-player-wins-round = { $player } thắng vòng này! Điểm: { $score }.
hc-score-line = { $player }: { $score } { $score ->
    [one] điểm
   *[other] điểm
}
hc-final-score-line = { $rank }. { $player }: { $score } điểm
hc-all-submissions = Các bài khác:
hc-your-winning-answer = Câu trả lời thắng cuộc của bạn: { $text }
hc-winning-answer-player = Câu trả lời thắng cuộc của { $player }: { $text }
hc-your-other-submission = Bài nộp khác của bạn: { $text }
hc-other-submission-player = { $player }: { $text }

# Xem
hc-preview-submission = Xem trước bài nộp của bạn
hc-view-submission = Xem bài nộp của bạn
hc-preview-submission-text = Xem trước: { $text }
hc-your-submission = Bài nộp của bạn: { $text }
hc-select-cards-first = Hãy chọn ít nhất 1 lá bài trước.
hc-review-hand = Xem bài trên tay
hc-hand-empty = Bạn chưa có bài trên tay.
hc-hand-card = Lá { $number }: { $text }
hc-hand-card-selected = Lá { $number }: { $text }, đã chọn ở vị trí { $position }
hc-review-answers = Xem lại các câu trả lời
hc-answer-line = Câu trả lời { $number }: { $text }
hc-no-answers-to-review = Hiện không có câu trả lời nào để xem lại.

# Chiến thắng
hc-game-winner = { $player } thắng với { $score } điểm!
hc-you-win = Bạn thắng với { $score } điểm!

# Quản lý bộ bài
hc-deck-reshuffled = Chồng bài trắng đã bỏ được xáo lại vào bộ bài.
hc-black-deck-reshuffled = Chồng bài đen đã bỏ được xáo lại vào bộ bài.
hc-not-enough-cards = Không đủ bài. Hãy thử bật thêm bộ bài.
hc-error-too-many-judges = { $judges } trọng tài cần ít nhất { $required } người chơi, nhưng bàn này chỉ có { $players }. Hãy giảm số trọng tài hoặc thêm người chơi.
hc-error-no-valid-packs = Chưa chọn bộ bài hợp lệ nào. Hãy chọn ít nhất một bộ bài trước khi bắt đầu.
hc-error-no-black-cards = Các bộ bài đã chọn không có lá bài đen nào. Hãy chọn bộ bài khác trước khi bắt đầu.
hc-error-not-enough-white-cards = { $players } người chơi với số bài trên tay là { $hand_size } cần ít nhất { $needed } lá bài trắng, nhưng các bộ đã chọn chỉ có { $available } lá. Hãy bật thêm bộ bài hoặc giảm số bài trên tay.
hc-error-pick-exceeds-hand-size = Các bộ bài đã chọn có lá yêu cầu { $pick } câu trả lời, nhưng số bài trên tay chỉ là { $hand_size }. Hãy tăng số bài trên tay hoặc chọn bộ bài khác.

# Quản lý bài trên tay
hc-toggle-card-keybind = Chọn/bỏ chọn lá bài { $number }
hc-submit-cards-keybind = Nộp bài

# Lượt của ai / trọng tài là ai
hc-whose-judge = Ai đang làm trọng tài
hc-waiting-for = Đang chờ { $names } nộp bài.
hc-all-submitted-waiting-judge = Tất cả người chơi đã nộp bài. Đang chờ { $judge } chấm bài.
