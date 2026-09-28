game-name-snakesandladders = Rắn và Thang
game-snakesandladders-desc = Đua từ khu vực xuất phát đến ô 100. Leo thang, trượt xuống theo rắn và trở thành người đầu tiên về đích.

snakes-roll = Gieo xúc xắc
snakes-check-positions = Xem vị trí

snakes-turn-start-you = Đến lượt bạn. Quân của bạn đang ở khu vực xuất phát, trước ô 1.
snakes-turn-start-other = Đến lượt { $player }. Quân { GENDER_TERM($player_gender, "possessive-determiner") } đang ở khu vực xuất phát, trước ô 1.
snakes-turn-you = Đến lượt bạn. Bạn đang ở ô { $position }.
snakes-turn-other = Đến lượt { $player }. { GENDER_TERM($player_gender, "subject-capitalized") } đang ở ô { $position }.

snakes-roll-you = Bạn gieo được { $roll }.
snakes-roll-other = { $player } gieo được { $roll }.
snakes-enter-you = Bạn đi từ khu vực xuất phát vào ô { $position }.
snakes-enter-other = { $player } đi từ khu vực xuất phát vào ô { $position }.
snakes-enter-you-brief = Bạn: ô { $position }.
snakes-enter-other-brief = { $player }: ô { $position }.
snakes-move-you = Bạn đi { $roll } ô, từ ô { $start } đến ô { $position }.
snakes-move-other = { $player } đi { $roll } ô, từ ô { $start } đến ô { $position }.
snakes-move-you-brief = Bạn: ô { $position }.
snakes-move-other-brief = { $player }: ô { $position }.
snakes-bounce-you = Từ ô { $start }, bạn gieo được { $roll } và đi quá ô { $target }, nên quân của bạn bật ngược từ đích về ô { $position }.
snakes-bounce-other = Từ ô { $start }, { $player } gieo được { $roll } và đi quá ô { $target }, nên quân của họ bật ngược từ đích về ô { $position }.
snakes-bounce-you-brief = Bạn bật ngược về ô { $position }.
snakes-bounce-other-brief = { $player } bật ngược về ô { $position }.
snakes-restored-bounce-you = Lần gieo đã lưu của bạn tiếp tục và bật ngược quân về ô { $position }.
snakes-restored-bounce-other = Lần gieo đã lưu của { $player } tiếp tục và bật ngược quân { GENDER_TERM($player_gender, "possessive-determiner") } về ô { $position }.
snakes-exact-miss-you = Bạn cần { $needed } để đến ô { $target }, nhưng gieo được { $roll }, nên vẫn đứng ở ô { $position }.
snakes-exact-miss-other = { $player } cần { $needed } để đến ô { $target }, nhưng gieo được { $roll }, nên { GENDER_TERM($player_gender, "subject") } vẫn đứng ở ô { $position }.
snakes-exact-miss-you-brief = Bạn cần { $needed }, gieo được { $roll } và vẫn ở ô { $position }.
snakes-exact-miss-other-brief = { $player } cần { $needed }, gieo được { $roll } và vẫn ở ô { $position }.
snakes-ladder-you = Bạn dừng ở chân thang tại ô { $start } và leo lên ô { $end }, tiến thêm { $distance } ô.
snakes-ladder-other = { $player } dừng ở chân thang tại ô { $start } và leo lên ô { $end }, tiến thêm { $distance } ô.
snakes-ladder-you-brief = Bạn leo thang từ ô { $start } lên ô { $end }.
snakes-ladder-other-brief = { $player } leo thang từ ô { $start } lên ô { $end }.
snakes-snake-you = Bạn dừng ở đầu rắn tại ô { $start } và trượt xuống đuôi rắn ở ô { $end }, lùi { $distance } ô.
snakes-snake-other = { $player } dừng ở đầu rắn tại ô { $start } và trượt xuống đuôi rắn ở ô { $end }, lùi { $distance } ô.
snakes-snake-you-brief = Bạn trượt từ ô { $start } xuống ô { $end }.
snakes-snake-other-brief = { $player } trượt từ ô { $start } xuống ô { $end }.
snakes-extra-turn-you = Bạn gieo được 6 nên được thêm một lượt từ ô { $position }.
snakes-extra-turn-other = { $player } gieo được 6 nên { GENDER_TERM($player_gender, "subject") } được thêm một lượt từ ô { $position }.
snakes-win-you = Bạn đến ô { $position } và thắng ván chơi!
snakes-win-other = { $player } đến ô { $position } và thắng ván chơi!

snakes-status-goal = Đích: ô { $target }. Luật về đích: { $rule }.
snakes-status-current-start = { $player }: khu vực xuất phát, trước ô 1. Đang đến lượt.
snakes-status-player-start = { $player }: khu vực xuất phát, trước ô 1.
snakes-status-current-position = { $player }: ô { $position }, còn { $remaining } ô đến đích. Đang đến lượt.
snakes-status-player-position = { $player }: ô { $position }, còn { $remaining } ô đến đích.
snakes-status-player-finished = { $player }: ô { $position }, đã về đích.

snakes-finish-bounce-back = Bật ngược khi đi quá đích
snakes-finish-exact-stay = Phải gieo đúng; đi quá thì đứng yên
snakes-set-finish-rule = Luật về đích: { $rule }
snakes-select-finish-rule = Chọn luật về đích
snakes-option-changed-finish-rule = Luật về đích đã đổi thành { $rule }.
snakesandladders-desc-finish-rule = Chọn gieo vượt ô 100 sẽ bật lùi lại hay người chơi phải chờ đúng số để về đích.
snakes-set-extra-turn-six = Thêm lượt khi gieo được 6: { $enabled }
snakes-option-changed-extra-turn-six = Tùy chọn thêm lượt khi gieo được 6 đã đổi thành { $enabled }.
snakesandladders-desc-extra-turn-on-six = Quy định gieo được 6 có được thêm lượt nữa hay không.

snakes-error-roll-not-playing = Bạn chỉ có thể gieo xúc xắc sau khi ván Rắn và Thang bắt đầu.
snakes-error-roll-not-your-turn = Bạn chưa thể gieo vì đang là lượt của người khác. Hãy chờ đến lượt mình.
snakes-error-roll-resolving = Lần gieo trước của bạn vẫn đang được xử lý. Hãy chờ quân đi xong và xử lý rắn hoặc thang trước khi gieo tiếp.
snakes-error-positions-not-playing = Bạn chỉ có thể xem vị trí khi ván Rắn và Thang đang diễn ra.
snakes-error-invalid-finish-rule = Luật về đích { $rule } không được hỗ trợ. Hãy chọn Bật ngược khi đi quá đích hoặc Phải gieo đúng; đi quá thì đứng yên.

snakes-end-score = { $rank }. { $player }: ô { $position }
snakes-end-score-start = { $rank }. { $player }: khu vực xuất phát, trước ô 1
