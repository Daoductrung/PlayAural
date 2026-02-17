# Ninety Nine - Vietnamese Localization
# Messages match v10 exactly

# Game info
ninetynine-name = Ninety Nine
ninetynine-description = Một trò chơi bài nơi người chơi cố gắng không để tổng điểm vượt quá 99. Người cuối cùng còn trụ lại sẽ thắng!

# Round
ninetynine-round = Vòng { $round }.

# Turn
ninetynine-player-turn = Lượt của { $player }.

# Playing cards - match v10 exactly
ninetynine-you-play = Bạn đánh lá { $card }. Tổng điểm giờ là { $count }.
ninetynine-player-plays = { $player } đánh lá { $card }. Tổng điểm giờ là { $count }.

# Direction reverse
ninetynine-direction-reverses = Chiều chơi bị đảo ngược!

# Skip
ninetynine-player-skipped = { $player } bị mất lượt.

# Token loss - match v10 exactly
ninetynine-you-lose-tokens = Bạn mất { $amount } { $amount ->
    [one] thẻ
   *[other] thẻ
}.
ninetynine-player-loses-tokens = { $player } mất { $amount } { $amount ->
    [one] thẻ
   *[other] thẻ
}.

# Elimination
ninetynine-player-eliminated = { $player } đã bị loại!

# Game end
ninetynine-player-wins = { $player } thắng trò chơi!
ninetynine-end-score = { $rank }. { $player }: { $tokens } { $tokens ->
    [one] thẻ
   *[other] thẻ
}

# Dealing
ninetynine-you-deal = Bạn chia bài.
ninetynine-player-deals = { $player } chia bài.

# Drawing cards
ninetynine-you-draw = Bạn rút lá { $card }.
ninetynine-player-draws = { $player } rút một lá bài.

# No valid cards
ninetynine-no-valid-cards = { $player } không có lá bài nào để tổng điểm không vượt quá 99!

# Status - for C key
ninetynine-current-count = Tổng điểm hiện tại là { $count }.

# Ace choice
ninetynine-ace-choice = Chọn giá trị cho lá Át: +1 hay +11?
ninetynine-ace-add-eleven = Cộng 11
ninetynine-ace-add-one = Cộng 1

# Ten choice
ninetynine-ten-choice = Chọn giá trị cho lá 10: +10 hay -10?
ninetynine-ten-add = Cộng 10
ninetynine-ten-subtract = Trừ 10
ninetynine-choice-1 = Lựa chọn 1
ninetynine-choice-2 = Lựa chọn 2

# Manual draw
ninetynine-draw-card = Rút bài
ninetynine-draw-prompt = Vui lòng rút một lá bài.

# Options
ninetynine-set-tokens = Số thẻ ban đầu: { $tokens }
ninetynine-enter-tokens = Nhập số thẻ ban đầu:
ninetynine-option-changed-tokens = Số thẻ ban đầu đã được đặt là { $tokens }.
ninetynine-set-rules = Biến thể luật: { $rules }
ninetynine-select-rules = Chọn biến thể luật
ninetynine-option-changed-rules = Biến thể luật đã được đặt là { $rules }.
ninetynine-set-hand-size = Số bài trên tay: { $size }
ninetynine-enter-hand-size = Nhập số bài trên tay:
ninetynine-option-changed-hand-size = Số bài trên tay đã được đặt là { $size }.
ninetynine-set-autodraw = Tự động rút bài: { $enabled }
ninetynine-option-changed-autodraw = Tự động rút bài: { $enabled }.

# Rules variant announcements (shown at game start)
ninetynine-rules-quentin = Luật Quentin C.
ninetynine-rules-rsgames = Luật RS Games.

# Rules variant choices (for menu display)
ninetynine-rules-variant-quentin_c = Quentin C
ninetynine-rules-variant-rs_games = RS Games

# Disabled action reasons
ninetynine-choose-first = Bạn cần đưa ra lựa chọn trước.
ninetynine-draw-first = Bạn cần rút bài trước.
ninetynine-check-count = Kiểm tra tổng điểm
