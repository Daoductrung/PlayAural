game-name-pirates = Hải Tặc: Những Vùng Biển Thất Lạc

# Thiết lập và diễn biến vòng
pirates-welcome = Chào mừng đến với Hải Tặc: Những Vùng Biển Thất Lạc. Hãy dong buồm trên hải trình bốn mươi ô biển, thu hồi đá quý và qua mặt các thủy thủ đoàn đối địch.
pirates-welcome-brief = Chào mừng đến với Hải Tặc: Những Vùng Biển Thất Lạc.
pirates-oceans = Hải trình của bạn đi qua { $oceans }.
pirates-gems-placed = Cả { $total } viên đá quý đã được giấu dọc hải trình. Khi viên cuối cùng được thu hồi, tàu có kho báu giá trị nhất sẽ thắng.
pirates-gems-placed-brief = { $total } viên đá quý đã được giấu dọc hải trình.
pirates-golden-moon = Trăng Vàng mọc trong vòng { $round }. Mọi phần thưởng XP trong vòng này đều được nhân ba.
pirates-golden-moon-brief = Trăng Vàng: XP nhân ba trong vòng { $round }.
pirates-turn-you = Đến lượt bạn trong vòng { $round }. Tàu bạn đang ở ô { $position }, thuộc { $ocean }.
pirates-turn-you-brief = Đến lượt bạn. Ô { $position }.
pirates-turn = Đến lượt { $player } trong vòng { $round }, tại ô { $position }, thuộc { $ocean }.
pirates-turn-brief = Đến lượt { $player }.

# Di chuyển và thông tin hải đồ
pirates-move-left = Dong buồm một ô sang trái
pirates-move-right = Dong buồm một ô sang phải
pirates-move-2-left = Dong buồm hai ô sang trái
pirates-move-2-right = Dong buồm hai ô sang phải
pirates-move-3-left = Dong buồm ba ô sang trái
pirates-move-3-right = Dong buồm ba ô sang phải
pirates-move-you = Bạn dong buồm { $tiles } { $tiles ->
    [one] ô
   *[other] ô
} sang { $direction }, đến ô { $position } thuộc { $ocean }.
pirates-move-you-brief = Bạn dong buồm đến ô { $position }.
pirates-move = { $player } dong buồm { $tiles } { $tiles ->
    [one] ô
   *[other] ô
} sang { $direction }, đến ô { $position } thuộc { $ocean }.
pirates-move-brief = { $player } dong buồm đến ô { $position }.
pirates-map-edge = Bạn không thể đi xa hơn theo hướng đó; ô { $position } là rìa hải trình. Hãy chọn hành động khác.
pirates-dir-left = trái
pirates-dir-right = phải
pirates-your-position = Tàu bạn đang ở ô { $position }, khu vực { $sector }, thuộc { $ocean }.
pirates-check-position = Kiểm tra vị trí
pirates-check-moon = Kiểm tra Trăng Vàng
pirates-moon-active = Trăng Vàng đang hiện diện trong vòng { $round }. XP được nhân ba. Các thủy thủ đoàn đã thu hồi { $collected } trên { $total } viên đá quý; còn lại { $remaining } viên.
pirates-moon-inactive = Trăng Vàng chưa hiện diện trong vòng { $round }. Trăng sẽ trở lại sau { $rounds } { $rounds ->
    [one] vòng
   *[other] vòng
}. Các thủy thủ đoàn đã thu hồi { $collected } trên { $total } viên đá quý; còn lại { $remaining } viên.

# Trạng thái và kết quả
pirates-check-status = Kiểm tra tình hình thủy thủ đoàn
pirates-check-status-detailed = Tình hình thủy thủ đoàn chi tiết
pirates-status-line = { $player }: cấp { $level}; tổng { $xp } XP, đã có { $progress } trên { $needed } XP để lên cấp; { $points }; { $gem_count } { $gem_count ->
    [one] viên đá quý
   *[other] viên đá quý
}{ $detail ->
    [yes] ; ô { $position } thuộc { $ocean }; kho báu: { $gems }; hiệu ứng đang có: { $skills }
   *[no] { "" }
}.
pirates-end-score-line = { $rank }. { $player}: { $points }, cấp { $level }
pirates-all-gems-collected = Viên đá quý cuối cùng đã được thu hồi. Các thủy thủ đoàn đang so kho báu.
pirates-all-gems-collected-brief = Đã thu hồi viên đá quý cuối cùng.
pirates-you-win = Bạn thắng với { $score } điểm.
pirates-you-win-brief = Bạn thắng: { $score } điểm.
pirates-winner = { $player } thắng với { $score } điểm.
pirates-winner-brief = { $player } thắng: { $score } điểm.
pirates-you-tie = Bạn đồng hạng nhất với { $players }, cùng đạt { $score } điểm.
pirates-you-tie-brief = Bạn đồng hạng nhất với { $score } điểm.
pirates-players-tie = { $players } đồng hạng nhất với { $score } điểm.
pirates-players-tie-brief = { $players } đồng hạng với { $score } điểm.

# Đá quý và XP
pirates-gem-found-you = Bạn thu hồi được { $gem }, trị giá { $value } { $value ->
    [one] điểm
   *[other] điểm
}. Kho báu trên tàu bạn hiện trị giá { $score } điểm; ngoài biển còn { $remaining } viên.
pirates-gem-found-you-brief = Bạn thu hồi được { $gem }. Điểm: { $score }.
pirates-gem-found = { $player } thu hồi được { $gem }, trị giá { $value } { $value ->
    [one] điểm
   *[other] điểm
}. Kho báu của họ hiện trị giá { $score } điểm; ngoài biển còn { $remaining } viên.
pirates-gem-found-brief = { $player } thu hồi được { $gem }.
pirates-xp-gained-you = Bạn nhận { $xp } XP nhờ { $reason ->
    [gem] thu hồi một viên đá quý
    [attack] bắn đại bác trúng mục tiêu
    [defense] đẩy lùi một đợt pháo kích
   *[other] hoàn thành một hành động
}. Bạn hiện có tổng cộng { $total } XP.
pirates-xp-gained-you-brief = Bạn nhận { $xp } XP. Tổng: { $total }.
pirates-xp-gained-player = { $player } nhận { $xp } XP nhờ { $reason ->
    [gem] thu hồi một viên đá quý
    [attack] bắn đại bác trúng mục tiêu
    [defense] đẩy lùi một đợt pháo kích
   *[other] hoàn thành một hành động
}, nâng tổng XP lên { $total }.
pirates-xp-gained-player-brief = { $player } nhận { $xp } XP.
pirates-level-up-you = Bạn đạt cấp { $level }.
pirates-level-up-you-brief = Bạn đạt cấp { $level }.
pirates-level-up = { $player } đạt cấp { $level }.
pirates-level-up-brief = { $player } đạt cấp { $level }.
pirates-level-up-multiple-you = Bạn tăng { $levels } cấp và đạt cấp { $level }.
pirates-level-up-multiple-you-brief = Bạn đạt cấp { $level }.
pirates-level-up-multiple = { $player } tăng { $levels } cấp và đạt cấp { $level }.
pirates-level-up-multiple-brief = { $player } đạt cấp { $level }.
pirates-skills-unlocked-you = Ở cấp { $level }, bạn mở khóa { $skills }.
pirates-skills-unlocked-you-brief = Bạn mở khóa { $skills }.
pirates-skills-unlocked = Ở cấp { $level }, { $player } mở khóa { $skills }.
pirates-skills-unlocked-brief = { $player } mở khóa { $skills }.

# Giao chiến bằng đại bác
pirates-cannonball = Bắn đại bác
pirates-select-cannon-target = Chọn tàu trong tầm đại bác
pirates-target-option = { $player }, cách { $distance } { $distance ->
    [one] ô
   *[other] ô
}, có { $score } điểm, đang chở { $gems } { $gems ->
    [one] viên đá quý
   *[other] viên đá quý
}
pirates-target-unavailable = Tàu không còn khả dụng
pirates-no-targets = Không có tàu đối địch nào trong tầm đại bác { $range } ô hiện tại. Hãy di chuyển hoặc chọn kỹ năng khác.
pirates-target-out-of-range = { $target } không còn nằm trong tầm đại bác { $range } ô tính từ vị trí { $position } của bạn. Hãy chọn hành động khác.
pirates-attack-you-fire = Bạn bắn đại bác vào { $target }.
pirates-attack-you-fire-brief = Bạn bắn vào { $target }.
pirates-attack-incoming = { $attacker } bắn đại bác vào bạn.
pirates-attack-incoming-brief = { $attacker } bắn vào bạn.
pirates-attack-fired = { $attacker } bắn đại bác vào { $defender }.
pirates-attack-fired-brief = { $attacker } bắn vào { $defender }.
pirates-combat-rolls-you = Xúc xắc tấn công của bạn là { $attack_die}, cộng { $attack_bonus}, thành { $attack_total}. Xúc xắc phòng thủ của { $defender } là { $defense_die}, cộng { $defense_bonus}, thành { $defense_total}.
pirates-combat-rolls-you-brief = Công { $attack_total}; thủ { $defense_total}.
pirates-combat-rolls-defender = { $attacker } tấn công với { $attack_die}, cộng { $attack_bonus}, thành { $attack_total}. Xúc xắc phòng thủ của bạn là { $defense_die}, cộng { $defense_bonus}, thành { $defense_total}.
pirates-combat-rolls-defender-brief = Công { $attack_total}; thủ của bạn { $defense_total}.
pirates-combat-rolls-observer = { $attacker } tấn công với { $attack_die}, cộng { $attack_bonus}, thành { $attack_total}. { $defender } phòng thủ với { $defense_die}, cộng { $defense_bonus}, thành { $defense_total}.
pirates-combat-rolls-observer-brief = { $attacker } { $attack_total}; { $defender } { $defense_total}.
pirates-attack-hit-you = Trúng đích. Tổng { $attack_total } của bạn thắng tổng { $defense_total } của { $target}; hãy chọn một hành động áp mạn đang khả dụng.
pirates-attack-hit-you-brief = Bạn bắn trúng { $target }, { $attack_total } thắng { $defense_total}.
pirates-attack-hit-them = { $attacker } bắn trúng bạn, { $attack_total } thắng { $defense_total}, và giờ có thể áp mạn tàu bạn.
pirates-attack-hit-them-brief = { $attacker } bắn trúng bạn, { $attack_total } thắng { $defense_total}.
pirates-attack-hit = { $attacker } bắn trúng { $defender }, { $attack_total } thắng { $defense_total}, và có thể áp mạn.
pirates-attack-hit-brief = { $attacker } bắn trúng { $defender }.
pirates-attack-hit-no-boarding-you = Trúng đích. Tổng { $attack_total } của bạn thắng tổng { $defense_total } của { $target}. Phát Chiến Hạm này cho XP nhưng không cho quyền áp mạn.
pirates-attack-hit-no-boarding-you-brief = Bạn bắn trúng { $target }, { $attack_total } thắng { $defense_total}; không áp mạn.
pirates-attack-hit-no-boarding-them = { $attacker } bắn trúng bạn, { $attack_total } thắng { $defense_total}. Phát Chiến Hạm không cho quyền áp mạn.
pirates-attack-hit-no-boarding-them-brief = { $attacker } bắn trúng bạn; không áp mạn.
pirates-attack-hit-no-boarding = { $attacker } bắn trúng { $defender }, { $attack_total } thắng { $defense_total}. Phát Chiến Hạm này không cho quyền áp mạn.
pirates-attack-hit-no-boarding-brief = { $attacker } bắn trúng { $defender}; không áp mạn.
pirates-attack-miss-you = Tổng tấn công { $attack_total } của bạn không thắng tổng phòng thủ { $defense_total } của { $target}. Lượt của bạn kết thúc.
pirates-attack-miss-you-brief = Bạn bắn trượt { $target }, { $attack_total } thua { $defense_total}.
pirates-attack-miss-them = Bạn đẩy lùi { $attacker } với tổng phòng thủ { $defense_total } trước tổng tấn công { $attack_total}.
pirates-attack-miss-them-brief = Bạn đẩy lùi { $attacker }, { $defense_total } thắng { $attack_total}.
pirates-attack-miss = { $defender } đẩy lùi { $attacker }, { $defense_total } thắng { $attack_total}.
pirates-attack-miss-brief = { $attacker } bắn trượt { $defender }.

# Áp mạn
pirates-resolve-boarding = Xử lý áp mạn
pirates-select-boarding-action = Đại bác đã bắn trúng. Hãy chọn cách xử lý cuộc áp mạn
pirates-boarding-steal = Thử cướp một viên đá quý
pirates-boarding-push-left = Húc tàu phòng thủ sang trái
pirates-boarding-push-right = Húc tàu phòng thủ sang phải
pirates-boarding-option-unknown = Hành động áp mạn không xác định
pirates-must-resolve-boarding = Hãy xử lý cuộc áp mạn đang chờ trước khi thực hiện hành động khác trong lượt.
pirates-no-pending-boarding = Bạn không có cuộc áp mạn nào đang chờ xử lý.
pirates-boarding-stale = Cuộc áp mạn đang chờ không còn tàu phòng thủ hợp lệ nên đã bị hủy. Hãy chọn hành động khác trong lượt.
pirates-boarding-option-unavailable = { $action } không còn khả dụng khi đối đầu { $defender }. Hãy chọn một phương án áp mạn hiện có.
pirates-push-you = Bạn húc { $target } sang { $direction }, từ ô { $old_pos } đến ô { $new_pos }, khiến { GENDER_TERM($target_gender, "object") } trôi { $distance } ô. Hiệu ứng Tốc Độ Húc Mạn góp thêm { $bonus } ô.
pirates-push-you-brief = Bạn húc { $target } đến ô { $position }.
pirates-push-them = { $attacker } húc bạn sang { $direction }, từ ô { $old_pos } đến ô { $new_pos }, khiến bạn trôi { $distance } ô.
pirates-push-them-brief = { $attacker } húc bạn đến ô { $position }.
pirates-push = { $attacker } húc { $defender } sang { $direction }, từ ô { $old_pos } đến ô { $new_pos }, một quãng { $distance } ô.
pirates-push-brief = { $attacker } húc { $defender } đến ô { $position }.
pirates-steal-rolls-you = Tổng cướp của bạn là { $steal}; tổng canh giữ của { $target } là { $defend}.
pirates-steal-rolls-you-brief = Cướp { $steal}; canh giữ { $defend}.
pirates-steal-rolls-defender = Tổng cướp của { $attacker } là { $steal}; tổng canh giữ của bạn là { $defend}.
pirates-steal-rolls-defender-brief = Cướp { $steal}; canh giữ của bạn { $defend}.
pirates-steal-rolls-observer = { $attacker } thử cướp của { $defender}: cướp { $steal}, canh giữ { $defend}.
pirates-steal-rolls-observer-brief = { $attacker } cướp với { $steal }, đối đầu { $defender } với { $defend}.
pirates-steal-success-you = Bạn cướp được { $gem } từ { $target }. Kho báu của bạn trị giá { $attacker_score } điểm; { GENDER_TERM($target_gender, "possessive-pronoun") } trị giá { $defender_score } điểm.
pirates-steal-success-you-brief = Bạn cướp được { $gem } từ { $target }.
pirates-steal-success-them = { $attacker } cướp mất { $gem } của bạn. Kho báu { GENDER_TERM($attacker_gender, "possessive-determiner") } trị giá { $attacker_score } điểm; của bạn trị giá { $defender_score } điểm.
pirates-steal-success-them-brief = { $attacker } cướp mất { $gem } của bạn.
pirates-steal-success = { $attacker } cướp { $gem } từ { $defender }. Kho báu của họ giờ lần lượt trị giá { $attacker_score } và { $defender_score } điểm.
pirates-steal-success-brief = { $attacker } cướp { $gem } từ { $defender }.
pirates-steal-failed-you = Tổng cướp { $steal } của bạn không thắng tổng canh giữ { $defend } của { $target}. Bạn không cướp được gì.
pirates-steal-failed-you-brief = Bạn cướp thất bại, { $steal } thua { $defend}.
pirates-steal-failed-defender = Bạn chặn được vụ cướp của { $attacker }, { $defend } thắng { $steal}, và giữ nguyên kho báu.
pirates-steal-failed-defender-brief = Bạn chặn được vụ cướp của { $attacker }.
pirates-steal-failed = { $defender } chặn được vụ cướp của { $attacker }, { $defend } thắng { $steal}.
pirates-steal-failed-brief = { $attacker } không cướp được của { $defender }.
pirates-steal-no-gems-you = Bạn không thể cướp của { $target } vì { GENDER_TERM($target_gender, "subject") } không còn chở đá quý. Hãy chọn húc tàu.
pirates-steal-no-gems-you-brief = { $target } không có đá quý để cướp.
pirates-steal-no-gems-defender = { $attacker } không thể cướp của bạn vì tàu bạn không chở đá quý.
pirates-steal-no-gems-defender-brief = Bạn không có đá quý để { $attacker } cướp.
pirates-steal-no-gems = { $attacker } không thể cướp của { $defender } vì tàu phòng thủ không chở đá quý.
pirates-steal-no-gems-brief = { $defender } không có đá quý để cướp.

# Kỹ năng và trạng thái kỹ năng
pirates-use-skill = Sử dụng kỹ năng
pirates-select-skill = Chọn một kỹ năng đã mở khóa
pirates-unknown-skill = Kỹ năng không xác định
pirates-skill-error = { $message }
pirates-skill-selection-stale = Kỹ năng vừa chọn không còn khả dụng ở cấp độ hoặc trạng thái hiện tại. Hãy mở lại trình đơn kỹ năng và chọn một kỹ năng đang dùng được.
pirates-req-level = { $skill } yêu cầu cấp { $required}; bạn đang ở cấp { $current}.
pirates-requires-level = { $action ->
    [move_2] Dong buồm hai ô
    [move_3] Dong buồm ba ô
   *[other] Hành động đó
} yêu cầu cấp { $required}; bạn đang ở cấp { $current}.
pirates-skill-cooldown = { $name } còn hồi phục trong { $turns } lượt của bạn.
pirates-skill-active = { $name } đang có hiệu lực trong { $turns } lượt nữa của bạn.
pirates-skill-already-activated-this-turn = Bạn đã kích hoạt một cường hóa chiến đấu trong lượt này. Tiếp theo hãy di chuyển hoặc bắn đại bác.
pirates-skill-no-uses = La Bàn Tầm Ngọc đã hết số lần dùng trong ván này.
pirates-skill-no-gems = La Bàn Tầm Ngọc không tìm được mục tiêu vì không còn đá quý chưa thu hồi.
pirates-skill-no-targets = Không có tàu đối địch nào trong tầm { $range } ô hiện tại của kỹ năng này.
pirates-skill-incompatible = Không thể kích hoạt { $skill } khi { $active } đang có hiệu lực. Hãy đợi hiệu ứng hiện tại kết thúc.
pirates-battleship-after-buff = Không thể triển khai Chiến Hạm sau khi bạn đã kích hoạt cường hóa chiến đấu trong lượt này. Hãy dùng cường hóa với một phát đại bác thường hoặc chờ đến lượt sau.
pirates-menu-active = { $name } (còn hiệu lực { $turns } lượt)
pirates-menu-cooldown = { $name } (còn hồi phục { $turns } lượt)
pirates-menu-activate = Kích hoạt { $name }
pirates-menu-gem-seeker = { $name } (còn { $uses } lần dùng)
pirates-active-skill-status = { $skill }, còn { $turns } lượt
pirates-no-active-skills = không có
pirates-skill-activated = { $player } kích hoạt { $skill}. { $effect }
pirates-skill-activated-brief = { $player } kích hoạt { $skill}.
pirates-buff-expired-you = Hiệu ứng { $skill } của bạn kết thúc trước khi lượt này bắt đầu.
pirates-buff-expired-you-brief = { $skill } của bạn đã hết hiệu lực.
pirates-buff-expired = Hiệu ứng { $skill } của { $player } kết thúc trước khi lượt { GENDER_TERM($player_gender, "possessive-determiner") } bắt đầu.
pirates-buff-expired-brief = { $skill } của { $player } đã hết hiệu lực.

pirates-skill-instinct-name = Trực Giác Thủy Thủ
pirates-skill-instinct-desc = Xem tám khu vực gồm năm ô, cùng số đá quý chưa thu hồi và tàu đối địch trong từng khu vực. Hành động xem thông tin này không kết thúc lượt.
pirates-instinct-header = Hải đồ Trực Giác Thủy Thủ, chia thành tám khu vực:
pirates-instinct-sector = Khu vực { $sector}, từ ô { $start } đến { $end}: { $gems } { $gems ->
    [one] viên đá quý chưa thu hồi
   *[other] viên đá quý chưa thu hồi
}, { $players } { $players ->
    [one] tàu đối địch
   *[other] tàu đối địch
}.

pirates-skill-portal-name = Cổng Dịch Chuyển
pirates-skill-portal-desc = Chọn một vùng biển khác có tàu đối địch, hoặc chọn Ngẫu nhiên để dịch chuyển đến bất kỳ ô nào trên bản đồ. Hồi phục: 3 lượt của bạn.
pirates-resolve-portal = Chọn đích Cổng Dịch Chuyển
pirates-select-portal-ocean = Chọn vùng biển khác có tàu đối địch, hoặc chọn Ngẫu nhiên để đến bất kỳ ô nào
pirates-portal-option = { $ocean }; tàu: { $ships}; { $gems } { $gems ->
    [one] viên đá quý chưa thu hồi
   *[other] viên đá quý chưa thu hồi
}
pirates-portal-option-random = Ô ngẫu nhiên trên bản đồ
pirates-portal-option-unavailable = Vùng biển đó không phải đích Cổng Dịch Chuyển hợp lệ vì đó là vùng biển hiện tại của bạn hoặc không có tàu đối địch tại đó. Hãy chọn đích khác.
pirates-must-resolve-portal = Vì bạn đã dùng Cổng Dịch Chuyển, lượt của bạn bị khóa vào kỹ năng này. Hãy chọn một đích, hoặc chọn Ngẫu nhiên, để hoàn tất Cổng Dịch Chuyển và kết thúc lượt.
pirates-no-pending-portal = Bạn không có đích Cổng Dịch Chuyển nào đang chờ xử lý.
pirates-portal-no-ships = Không có đích Cổng Dịch Chuyển cụ thể ở vùng biển có tàu đối địch, nhưng Ngẫu nhiên vẫn có thể đưa bạn đến bất kỳ ô nào trên bản đồ.
pirates-portal-fizzle-you = Đích Cổng Dịch Chuyển của bạn không còn hợp lệ. Hãy chọn Ngẫu nhiên để dịch chuyển đến bất kỳ đâu trên bản đồ, hoặc chọn một đích hợp lệ khác.
pirates-portal-fizzle-you-brief = Hãy chọn Ngẫu nhiên hoặc một đích Cổng Dịch Chuyển hợp lệ khác.
pirates-portal-fizzle = Đích Cổng Dịch Chuyển của { $player } không còn hợp lệ.
pirates-portal-fizzle-brief = { $player } cần chọn đích Cổng Dịch Chuyển khác.
pirates-portal-success-you = Bạn đi qua Cổng Dịch Chuyển đến { $ocean}, xuất hiện tại ô { $position}. Kỹ năng hồi phục trong 3 lượt của bạn.
pirates-portal-success-you-brief = Bạn dịch chuyển đến ô { $position } thuộc { $ocean}.
pirates-portal-success = { $player } đi qua Cổng Dịch Chuyển đến { $ocean}, xuất hiện tại ô { $position}.
pirates-portal-success-brief = { $player } dịch chuyển đến ô { $position}.

pirates-skill-seeker-name = La Bàn Tầm Ngọc
pirates-skill-seeker-desc = Tiết lộ chính xác vị trí của một viên đá quý chưa thu hồi. Có 3 lần dùng mỗi ván; sử dụng không kết thúc lượt.
pirates-gem-seeker-reveal = La Bàn Tầm Ngọc tìm thấy { $gem } ở ô { $position}. Bạn còn { $uses } lần dùng trong ván này.

pirates-skill-sword-name = Kiếm Khách
pirates-skill-sword-desc = Nhận +2 tấn công trong 3 lượt của bạn. Hồi phục: 6 lượt. Không thể chồng với Thuyền Trưởng Lão Luyện.
pirates-sword-fighter-activated = Bạn kích hoạt Kiếm Khách: +{ $bonus } tấn công trong { $turns } lượt của bạn. Hồi phục: { $cooldown } lượt. Bạn vẫn có thể di chuyển hoặc bắn trong lượt này.
pirates-sword-fighter-activated-brief = Kiếm Khách có hiệu lực: +{ $bonus } tấn công.

pirates-skill-push-name = Tốc Độ Húc Mạn
pirates-skill-push-desc = Tăng 2 ô cho khoảng cách húc tàu sau khi áp mạn trong 3 lượt của bạn. Hồi phục: 6 lượt.
pirates-push-activated = Bạn kích hoạt Tốc Độ Húc Mạn: +{ $bonus } ô khi húc tàu trong { $turns } lượt của bạn. Hồi phục: { $cooldown } lượt. Bạn vẫn có thể di chuyển hoặc bắn trong lượt này.
pirates-push-activated-brief = Tốc Độ Húc Mạn có hiệu lực: +{ $bonus } ô húc tàu.

pirates-skill-captain-name = Thuyền Trưởng Lão Luyện
pirates-skill-captain-desc = Nhận +1 tấn công và +1 phòng thủ trong 4 lượt của bạn. Hồi phục: 7 lượt. Không thể chồng với Kiếm Khách.
pirates-skilled-captain-activated = Bạn kích hoạt Thuyền Trưởng Lão Luyện: +{ $attack } tấn công và +{ $defense } phòng thủ trong { $turns } lượt của bạn. Hồi phục: { $cooldown } lượt. Bạn vẫn có thể di chuyển hoặc bắn trong lượt này.
pirates-skilled-captain-activated-brief = Thuyền Trưởng Lão Luyện có hiệu lực: +{ $attack } tấn công, +{ $defense } phòng thủ.

pirates-skill-battleship-name = Chiến Hạm
pirates-skill-battleship-desc = Bắn hai phát đại bác do thủy thủ đoàn chọn mục tiêu, nhưng phát trúng không cho quyền áp mạn. Kỹ năng kết thúc lượt. Hồi phục: 4 lượt.
pirates-battleship-activated = Bạn triển khai Chiến Hạm để bắn { $shots } phát đại bác. Thủy thủ đoàn chọn mục tiêu giá trị nhất trong tầm cho từng phát; phát trúng không cho quyền áp mạn. Hồi phục: { $cooldown } lượt.
pirates-battleship-activated-brief = Bạn triển khai Chiến Hạm để bắn { $shots } phát.
pirates-battleship-activated-player = { $player } triển khai Chiến Hạm để bắn { $shots } phát đại bác. Phát trúng từ kỹ năng này không cho quyền áp mạn.
pirates-battleship-activated-player-brief = { $player } triển khai Chiến Hạm.
pirates-battleship-shot = Thủy thủ đoàn của bạn bắn phát Chiến Hạm thứ { $shot } vào { $target}.
pirates-battleship-shot-brief = Phát { $shot } vào { $target}.
pirates-battleship-shot-player = Thủy thủ đoàn của { $player } bắn phát Chiến Hạm thứ { $shot } vào { $target}.
pirates-battleship-shot-player-brief = { $player } bắn vào { $target}.
pirates-battleship-no-targets = Thủy thủ đoàn của bạn không thể bắn phát thứ { $shot } vì không còn tàu đối địch nào trong tầm { $range } ô. Chiến Hạm kết thúc.
pirates-battleship-no-targets-brief = Không có mục tiêu cho phát { $shot}.
pirates-battleship-no-targets-player = { $player } không thể bắn phát Chiến Hạm thứ { $shot } vì không còn tàu đối địch nào trong tầm { $range } ô.
pirates-battleship-no-targets-player-brief = { $player } không có mục tiêu cho phát { $shot}.

pirates-skill-devastation-name = Hỏa Lực Tầm Xa
pirates-skill-devastation-desc = Tăng tầm đại bác thường từ 5 lên 10 ô trong 3 lượt của bạn. Hồi phục: 10 lượt. Không tương thích với Chiến Hạm.
pirates-double-devastation-activated = Bạn kích hoạt Hỏa Lực Tầm Xa: tầm đại bác tăng lên { $range } ô trong { $turns } lượt của bạn. Hồi phục: { $cooldown } lượt. Bạn vẫn có thể di chuyển hoặc bắn trong lượt này.
pirates-double-devastation-activated-brief = Hỏa Lực Tầm Xa có hiệu lực: tầm { $range } ô.

# Tùy chọn và kiểm tra trước ván
pirates-set-combat-xp-multiplier = Hệ số XP giao chiến: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = Nhập hệ số XP giao chiến từ 0.1 đến 3.0
pirates-option-changed-combat-xp = Hệ số XP giao chiến đã đặt thành { $combat_multiplier}.
pirates-desc-combat-xp-multiplier = Điều chỉnh XP từ phát đại bác trúng đích và lần phòng thủ thành công. Hệ số Trăng Vàng được áp dụng riêng (mặc định 1.0, phạm vi 0.1-3.0).
pirates-set-find-gem-xp-multiplier = Hệ số XP thu hồi đá quý: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = Nhập hệ số XP thu hồi đá quý từ 0.1 đến 3.0
pirates-option-changed-find-gem-xp = Hệ số XP thu hồi đá quý đã đặt thành { $find_gem_multiplier}.
pirates-desc-find-gem-xp-multiplier = Điều chỉnh XP khi một con tàu thu hồi đá quý, kể cả sau khi bị cưỡng bức di chuyển (mặc định 1.0, phạm vi 0.1-3.0).
pirates-set-gem-stealing = Cướp đá quý: { $mode }
pirates-select-gem-stealing = Chọn cách điểm cộng chiến đấu tác động đến lần đổ cướp đá quý
pirates-option-changed-stealing = Chế độ cướp đá quý đã đặt thành { $mode}.
pirates-desc-gem-stealing = Quy định có được cướp đá quý sau phát bắn trúng hay không, và điểm cộng tấn công, phòng thủ đang có có tác động đến lần đổ cướp hay không.
pirates-stealing-with-bonus = Bật, có áp dụng điểm cộng chiến đấu
pirates-stealing-no-bonus = Bật, không áp dụng điểm cộng chiến đấu
pirates-stealing-disabled = Tắt; áp mạn chỉ có thể húc tàu
pirates-error-combat-xp-range = Hệ số XP giao chiến đang là { $value}, nằm ngoài phạm vi hỗ trợ từ { $min } đến { $max}. Hãy đặt lại trong phạm vi này trước khi bắt đầu.
pirates-error-gem-xp-range = Hệ số XP thu hồi đá quý đang là { $value}, nằm ngoài phạm vi hỗ trợ từ { $min } đến { $max}. Hãy đặt lại trong phạm vi này trước khi bắt đầu.
pirates-error-stealing-mode = Chế độ cướp đá quý đã lưu, { $mode}, không được hỗ trợ. Hãy chọn một chế độ cướp đá quý trong danh sách trước khi bắt đầu.

# Tên vùng biển
pirates-ocean-rory = Đại Dương Rory
pirates-ocean-dev = Vực Sâu Lập Trình
pirates-ocean-par = Biển Thiên Đường Lập Trình Viên
pirates-ocean-pal = Hải Phận Cung Điện
pirates-ocean-sil = Eo Biển Silva
pirates-ocean-kai = Hải Lưu Kai
pirates-ocean-gam = Vịnh Game Thủ
pirates-ocean-ser = Biển Phòng Máy Chủ
pirates-ocean-bat = Vịnh Giao Tranh
pirates-ocean-cod = Kênh Biên Dịch Mã
pirates-ocean-unknown = Vùng Biển Vô Danh

# Tên đá quý
pirates-gem-0 = ngọc mắt mèo
pirates-gem-1 = hồng ngọc
pirates-gem-2 = ngọc hồng lựu
pirates-gem-3 = kim cương
pirates-gem-4 = lam ngọc
pirates-gem-5 = lục bảo
pirates-gem-6 = ngọc cung điện
pirates-gem-7 = viên ngọc nhựa khổng lồ
pirates-gem-8 = bá đạo thạch xanh
pirates-gem-9 = thạch anh tím
pirates-gem-10 = nhẫn vàng
pirates-gem-11 = cuộn thạch đỏ bá đạo
pirates-gem-12 = huyết thạch đỏ bá đạo
pirates-gem-13 = đá mặt trăng
pirates-gem-14 = ngọc lưu ly
pirates-gem-15 = hổ phách
pirates-gem-16 = thạch anh vàng
pirates-gem-17 = ngọc trai đen chắc chắn không bị nguyền rủa (tm)
pirates-gem-unknown = đá quý lạ
pirates-gem-none = không có đá quý
