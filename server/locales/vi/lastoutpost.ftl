game-name-lastoutpost = Tiền Đồn Cuối Cùng
lo-root-vitals = Máu { $hp }/{ $maximum }; AP { $ap }; { $item }.
lo-root-spectator = Đang theo dõi Tiền Đồn Cuối Cùng.
lo-menu-attack = Tấn công
lo-menu-move = Di chuyển
lo-menu-equipment = Vũ khí và nạp đạn
lo-menu-support = Cứu trợ và hàng hóa
lo-menu-interact = Mục tiêu và công sự
lo-menu-supplies = Tiếp tế và nâng cấp
lo-menu-back = Về menu chính
lo-menu-available = { $menu }; Có hành động
lo-menu-equipment-state = { lo-menu-equipment }: { $weapon }; trong súng { $loaded }, dự trữ { $reserve }.
lo-shop-balance = Tín dụng: { $credits }.
lo-shop-done = Đóng cửa hàng
lo-help-shop-done = Đóng cửa hàng, không kết thúc lượt. E hoặc X cũng đóng cửa hàng.
lo-key-finish-or-end = Sẵn sàng, đóng cửa hàng hoặc kết thúc lượt
lo-menu-close-information = Đóng bảng thông tin trước.
lo-help-menu-attack = Chọn mục tiêu bắn, đâm dao hoặc ném lựu đạn.
lo-help-menu-move = Lối đi, chi phí di chuyển và tình hình tại điểm đến.
lo-help-menu-equipment = Nạp đạn hoặc đổi vũ khí. Đổi vũ khí không tốn AP.
lo-help-menu-support = { $party_size ->
    [1] Tự chữa trị hoặc đặt hàng xuống.
   *[other] Chữa trị, cứu đồng đội hoặc chuyển hàng.
    }
lo-help-menu-interact = Khôi phục điện, sửa vô tuyến, mở cổng hoặc sửa rào chắn.
lo-help-menu-supplies = Mua vật tư và nâng cấp. Mua xong vẫn ở cửa hàng. X để quay lại.
lo-help-menu-back = Về menu chính, tại nút của nhóm vừa mở.
lo-empty-attack = Không có mục tiêu.
lo-empty-move = Không có lối đi đang mở.
lo-empty-equipment = Không có thao tác vũ khí.
lo-empty-preparation = Không dùng được khi chuẩn bị.
lo-empty-support = Không có thao tác cứu trợ hay chuyển hàng.
lo-empty-interact = Không có thao tác tại đây.
lo-empty-supplies = Không có vật tư để mua tại đây.
lo-move-location = { $zone }. { $description }
lo-destination = { $party_size ->
    [1] { $zone }; { $ap } AP. Địch: { $inside } trong khu, { $outside } ngoài rào. { $barricade }
   *[other] { $zone }; { $ap } AP. Địch: { $inside } trong khu, { $outside } ngoài rào. Đồng đội: { $survivors }. { $barricade }
    }
lo-destination-survivor = { $name } ({ $condition })
lo-destination-barricade = Lối địch tràn vào; rào chắn còn { $strength } độ bền.
lo-enemies = Xem thây ma
lo-help-enemies = Địch trong tầm xếp trước, rồi đến địch xa hơn và tiếp viện. Muốn tấn công vẫn cần đến lượt, đủ AP và đạn.
lo-enemies-context = Mục tiêu tính từ { $zone }.
lo-enemies-spectator-context = Tổng quan từ { $zone }.
lo-enemies-empty = Không có địch trên bản đồ.
lo-enemy-detail = { $pack }. Máu từng con: { $health }. { $distance } { $access }
lo-enemy-distance = Khoảng cách: { $count ->
    [one] { $count } chặng.
   *[other] { $count } chặng.
    }
lo-enemy-unreachable = Không có lối đi.
lo-enemy-barricade = Sau rào chắn có độ bền { $strength }; chưa thể tấn công.
lo-enemy-reach = Trong tầm: { $actions }.
lo-enemy-reposition = Ngoài tầm của trang bị hiện tại.
lo-enemy-observe = Góc nhìn người xem.
lo-health = Kiểm tra máu
lo-help-health = Máu hiện tại và thời hạn được cứu nếu đã gục.
lo-health-report = Máu { $hp }/{ $maximum }. { $condition }.
lo-health-upright = Còn sức chiến đấu
lo-health-downed = { $party_size ->
    [1] Đã gục
   *[other] Đã gục; còn { $phases } lượt địch để cứu
    }
lo-health-awaiting-recovery = Đang chờ hồi phục sau đợt
lo-slot-primary = Cầm súng chính
lo-slot-sidearm = Cầm súng ngắn
lo-error-slot-empty = Chưa có súng chính.
lo-error-preparation = Không thể chiến đấu khi đang chuẩn bị.
lo-option-voices = Lời thoại nhân vật: { $enabled }
lo-change-voices = Lời thoại nhân vật: { $enabled }.
lo-desc-voices = Lời thoại tiếng Anh, có thể có chửi thề. Thông báo chiến thuật dùng ngôn ngữ bạn chọn.
lo-you = Bạn
lo-team = { $party_size ->
    [1] Người sống sót
   *[other] Cả đội
    }
lo-none = Không có
lo-yes = Có
lo-no = Không
lo-inside = bên trong
lo-outside = bên ngoài rào chắn
lo-message = { $text }
lo-term-none = { lo-none }
lo-term-courtyard = Sân Trong
lo-term-gatehouse = Nhà Gác
lo-term-workshop = Xưởng Sửa Chữa
lo-term-infirmary = Trạm Quân Y
lo-term-loading = Bãi Bốc Dỡ
lo-term-generator = Phòng Máy Phát
lo-term-pump = Nhà Bơm
lo-term-roof = Mái Trạm Vô Tuyến
lo-term-walker = { $count ->
    [one] Xác sống
   *[other] Xác sống
    }
lo-term-hound = { $count ->
    [one] Chó thây ma
   *[other] Chó thây ma
    }
lo-term-brute = { $count ->
    [one] Thây ma khổng lồ
   *[other] Thây ma khổng lồ
    }
lo-term-pistol = Súng ngắn M1911
lo-term-rifle = Súng trường AK
lo-term-shotgun = Súng hoa cải
lo-term-marksman = Súng trường thiện xạ
lo-term-knife = Dao
lo-term-medkit = Túi cứu thương
lo-term-grenade = Lựu đạn
lo-term-endurance = Bền Bỉ
lo-term-medic = Cứu Hộ
lo-term-quickhands = Thao Tác Nhanh
lo-term-combat = Lượt người chơi
lo-term-resolving = Đang thực hiện hành động
lo-term-reloading = Đang nạp đạn
lo-term-prep = Chuẩn bị
lo-term-finished = Kết thúc
lo-term-dempsey = Dempsey
lo-term-nikolai = Nikolai
lo-term-takeo = Takeo
lo-term-richtofen = Richtofen
lo-term-victory = { $party_size ->
    [1] Sống sót
   *[other] Cả đội sống sót
    }
lo-term-objectives = Chưa sửa xong máy vô tuyến hoặc máy phát điện
lo-term-overwhelmed = { $party_size ->
    [1] Bị áp đảo
   *[other] Cả đội đã bị áp đảo
    }
lo-term-overrun = Hết thời hạn của đợt
lo-turn-resolving = { lo-error-resolving }
lo-turn-prep = { $survivor_count ->
    [1] Đang chuẩn bị. Chọn Sẵn sàng để bắt đầu đợt mới.
   *[other] Đang chuẩn bị. Cả đội sẵn sàng sẽ bắt đầu đợt mới.
    }
lo-map = Bản đồ và nhóm địch
lo-forecast = Dự báo lượt địch
lo-inventory = Trang bị và vật tư
lo-help-map = Đường đi, rào chắn, nhóm địch và lịch tiếp viện. Hướng nghe cố định là bắc.
lo-help-forecast = Lượt địch kế tiếp nếu không ai hành động thêm.
lo-help-inventory = Tín dụng, vũ khí, vật tư của bạn và linh kiện để sửa chữa, làm mục tiêu.
lo-header = Đợt { $wave }; chu kỳ { $cycle }/{ $limit }. { $phase }. { $zone }. Máu { $hp }; AP { $ap }; tín dụng { $credits }; linh kiện { $parts }.
lo-spectator-header = Đang xem. Đợt { $wave }; chu kỳ { $cycle }. { $phase }; linh kiện { $parts }.
lo-objectives = Mục tiêu
lo-survivor = { $name } ({ $character }): { $zone }; máu { $hp }/{ $maximum }; AP { $ap }. { $condition }; sẵn sàng { $ready }; thủ thế { $guard }.
lo-zone = { $zone }: { $description } Lối đang mở: { $links }. Địch: { $enemies }. { $barrier } Chỗ áp sát: { $frontage }.
lo-pack = { $count } { $kind }, { $zone }, { $side }; tổng máu { $hp }
lo-incoming = { $zone }: { $count } quân tiếp viện sau lượt địch thứ { $cycle }; hành động từ lượt thứ { $first }.
lo-forecast-caveat = Nếu không ai hành động thêm. Thây ma khổng lồ chiếm hai chỗ áp sát; các loại khác chiếm một. Địch chưa áp sát được vẫn cản nhiệm vụ. Xem dự báo không tốn lượt.
lo-weapon-status = { $name }, { $weapon }: đạn trong súng { $ammo }, dự trữ { $reserve }; sát thương { $damage } mỗi mục tiêu, tối đa { $targets } mục tiêu; tầm { $minimum } đến { $maximum }; đang cầm { $equipped }.
lo-kit-status = { $name }: { $credits } tín dụng; { $medkits } túi cứu thương, { $grenades } lựu đạn; kỹ năng { $perks }.
lo-action-label = { $action }: { $detail } ({ $ap } AP)
lo-action-label-simple = { $action } ({ $ap } AP)
lo-reload-detail = { $weapon }; trong súng { $loaded }/{ $capacity }, dự trữ { $reserve }
lo-attack-detail = { $weapon }, đạn trong súng { $ammo }; { $target }
lo-price = { $item }, { $cost } tín dụng
lo-ammo-price = { $item }, { $amount } viên dự trữ giá { $cost } tín dụng
lo-parts-price = { $item }, { $cost } linh kiện
lo-work-price = { $item }, { $done } trên { $total } bước, cần trả { $cost } linh kiện
lo-verb-fire = Bắn
lo-verb-knife = Đâm dao
lo-verb-reload = Nạp đạn
lo-verb-grenade = Ném lựu đạn
lo-verb-heal = Dùng túi cứu thương
lo-verb-revive = Cứu dậy
lo-verb-open = Mở cổng
lo-verb-repair = Sửa rào chắn
lo-verb-work = Sửa thiết bị
lo-verb-ammo = Mua đạn
lo-verb-buy = Mua trang bị
lo-verb-perk = Mua kỹ năng
lo-verb-upgrade = Nâng cấp súng chính
lo-verb-equip = Đổi vũ khí
lo-verb-ready = Sẵn sàng cho đợt tiếp theo
lo-verb-end = Kết thúc lượt
lo-help-fire = Bắn con ít máu nhất trong nhóm trước. Súng hoa cải trúng tối đa hai con. Rào chưa bị phá sẽ che chắn cho địch bên ngoài.
lo-help-knife = 1 sát thương; 1 AP; cùng khu. Không cần đạn.
lo-help-move = 1 AP mỗi chặng; 2 AP khi rời khu có địch. Mang hàng tốn thêm 1 AP.
lo-help-reload = 1 AP; đạn dự trữ vào súng khi nạp xong. Vẫn đi được. Thao Tác Nhanh miễn AP cho lần nạp đầu mỗi đợt.
lo-help-grenade = { $party_size ->
    [1] 3 sát thương, tối đa bốn địch; 1 AP. Cùng khu hoặc khu liền kề nhìn thấy được. Chỉ trúng địch đã vào trong.
   *[other] 3 sát thương, tối đa bốn địch; 1 AP. Cùng khu hoặc khu liền kề nhìn thấy được. Chỉ trúng địch đã vào trong, không hại đồng đội.
    }
lo-help-heal = 1 túi cứu thương và 1 AP; hồi tối đa 3 máu cho người còn đứng cùng khu.
lo-help-revive = Cứu dậy với 2 máu; 2 AP, hoặc 1 AP nếu có Cứu Hộ. Cùng khu. Không thêm lượt.
lo-help-revive-preview = { lo-help-revive } Nếu không hành động thêm, { $target } sẽ còn { $health } máu sau lượt địch kế tiếp.
lo-gate-link = { $origin } đến { $destination }
lo-gate-service = Cổng kỹ thuật
lo-gate-shortcut = Lối tắt Trạm Quân Y
lo-gate-roof = Cổng lên trạm vô tuyến
lo-gate-crossing = Lối qua bãi hàng
lo-gate-bulkhead = Cửa ngăn nước
lo-gate-status = { $gate }: đã mở { $opened }; { $cost } linh kiện; cần điện { $power }. Lối đi: { $routes }. Chỗ áp sát sau khi mở: { $frontages }.
lo-help-open-routes = { $cost } linh kiện; 1 AP; khu bạn đứng phải trống địch. Mở vĩnh viễn { $routes } cho cả hai bên. Cần điện: { $power }. Chỗ áp sát sau khi mở: { $frontages }.
lo-frontage-site = { $zone }, { $count } chỗ áp sát
lo-gate-opened-routes = Lối mới cho cả hai bên: { $routes }.
lo-defense-until-clear = Tiếp tục giữ { $zone } đến hết đợt; địch vẫn gây hại cho trạm.
lo-help-repair = 1 linh kiện và 1 AP; hồi 2 độ bền rào, tối đa 4. Một lần mỗi chu kỳ; không được có địch trong khu.
lo-help-work = 1 AP mỗi bước. Dùng số linh kiện ghi trên nút khi bắt đầu sửa. Không được có địch trong khu; vô tuyến cần điện.
lo-help-ammo = Dự trữ tối đa ba băng. Khi chiến đấu, mua tại điểm tiếp tế nếu không có địch trong khu. Khi chuẩn bị, mua ở mọi nơi.
lo-help-buy = Chỉ mua khi chuẩn bị. Súng chính mới thay súng cũ. Mua lần đầu có đạn; mua lại giữ đạn cũ. Không hoàn tiền.
lo-help-perk = Cần điện; tối đa hai kỹ năng. Bền Bỉ: +2 máu. Cứu Hộ: cứu dậy với 1 AP. Thao Tác Nhanh: lần nạp đầu mỗi đợt không tốn AP.
lo-help-upgrade = Cần điện; 500 tín dụng mỗi loại súng. Sát thương: AK 4, hoa cải 6, thiện xạ 9.
lo-help-equip = Đổi vũ khí; không tốn AP.
lo-help-ready = { $survivor_count ->
    [1] Bắt đầu đợt tiếp theo.
   *[other] Bật hoặc hủy sẵn sàng. Cả đội sẵn sàng sẽ bắt đầu đợt mới. Hủy sẵn sàng để mua tiếp.
    }
lo-help-end = { $party_size ->
    [1] Bỏ AP còn lại. Đến lượt địch hành động.
   *[other] Bỏ AP còn lại. Địch hành động khi cả đội hết lượt.
    }
lo-error-unavailable = Không dùng được trong giai đoạn này.
lo-error-stale = Lựa chọn này không còn hiệu lực.
lo-error-turn = { action-not-your-turn }
lo-error-down = Bạn đã gục.
lo-error-ready = Hủy sẵn sàng trước khi mua.
lo-error-ap = Không đủ AP.
lo-error-range = Mục tiêu ngoài tầm hoặc bị khuất.
lo-error-ammo = Không đủ đạn trong súng.
lo-error-grenade = Đã hết lựu đạn.
lo-error-medkit = Đã hết túi cứu thương.
lo-error-engaged = Dọn sạch địch trong khu trước.
lo-error-complete = Mục tiêu này đã hoàn thành.
lo-error-power = Khôi phục điện trước.
lo-error-parts = Không đủ linh kiện.
lo-error-credits = Không đủ tín dụng.
lo-error-equipped = Bạn đang cầm vũ khí này.
lo-error-resolving = Đang thực hiện hành động.
lo-event-wave = Đợt { $amount }; { $count } địch. { $deployment }.
lo-deployment-now = { $count } địch đang ở bên ngoài
lo-deployment-later = { $count } địch đến sau lượt địch { $cycle }
lo-event-final_warning = Đợt cuối. Còn { $amount } bước khôi phục; cần trả { $count } linh kiện. Hoàn tất hạ tầng và nhiệm vụ trước khi hết đợt.
lo-event-clear = { $party_size ->
    [1] Qua đợt { $amount }. +{ $count } tín dụng; +3 linh kiện. Hồi { $healing } máu, hoặc đứng dậy với { $recovery } máu nếu đã gục. Nhận tối đa { $ammo } viên súng ngắn dự trữ. Bắt đầu chuẩn bị.
   *[other] Qua đợt { $amount }. Mỗi người nhận { $count } tín dụng và tối đa { $ammo } viên súng ngắn dự trữ. Người còn đứng hồi { $healing } máu; người đã gục trở lại với { $recovery } máu. Đội: +3 linh kiện. Bắt đầu chuẩn bị.
    }
lo-event-fire = { $actor } bắn { $item } tại { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife = { $actor } đâm dao tại { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade = { $actor } cho nổ lựu đạn tại { $zone }. { $hits }. { lo-combat-kills }
lo-event-move = { $actor } đi từ { $origin } đến { $zone }.
lo-event-reload = { $actor } nạp { $amount } viên vào { $item }.
lo-reload-start = { $actor } đang nạp đạn.
lo-reload-start-personal = Đang nạp đạn.
lo-error-reloading = { lo-reload-start-personal }
lo-event-heal = { $actor } chữa cho { $target }; máu hiện tại { $amount }.
lo-event-revive = { $actor } cứu { $target } dậy với { $amount } máu.
lo-event-open = { $actor } mở { $item }; còn { $amount } linh kiện. { $routes }
lo-event-repair = { $actor } sửa rào tại { $zone } lên { $amount } độ bền.
lo-event-work = { $count ->
    [1] { $actor } đã khôi phục { $item } tại { $zone }.
   *[0] { $actor } sửa { $item } tại { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo = { $actor } mua { $amount } viên cho { $item }, trả { $count } tín dụng.
lo-event-buy = { $actor } mua { $item }; còn { $amount } tín dụng.
lo-event-perk = { $actor } nhận kỹ năng { $item }.
lo-event-upgrade = { $actor } nâng cấp { $item }.
lo-event-equip = { $actor } đổi sang { $item }.
lo-event-ready = { $actor } { $amount ->
    [1] sẵn sàng cho đợt tiếp theo.
   *[0] chưa sẵn sàng.
    }
lo-event-end = { $actor } đã kết thúc lượt.
lo-event-barrier = { $zone }: rào chịu { $count } đòn từ { $item }; còn { $amount } độ bền.
lo-event-enter = { $count } { $item } đã vào { $zone }.
lo-event-approach = { $count } { $item } đi từ { $origin } đến { $zone }.
lo-event-hurt = { $target } chịu { $count } đòn từ { $item }, tổng { $amount } sát thương tại { $zone }.
lo-event-down = { $target } đã gục tại { $zone }. Còn hai lượt địch kế tiếp để cứu.
lo-event-incapacitated = { $target } không thể hành động cho đến đợt tiếp theo.
lo-event-recovery = { $target } đã dùng lần hồi phục cuối. Máu { $amount }; lượt tới { $count } AP. Hàng ở lại nơi ngã xuống.
lo-event-arrivals = { $count } địch tiếp viện ngoài rào. Chúng hành động từ lượt địch sau.
lo-event-finish = { $item }. Số đợt đã dọn sạch: { $amount } trên { $waves }.
lo-result-cycles = Số lượt địch: { $count }.
lo-error-magazine-full = Súng đang cầm đã đầy đạn.
lo-error-reserve-empty = Đã hết đạn dự trữ.
lo-error-barrier-full = Rào chắn đã đủ độ bền.
lo-error-already-repaired = Rào này đã được sửa trong chu kỳ này.
lo-error-weapon-owned = Bạn đã mang súng chính này.
lo-error-kit-capacity = Đã mang đủ túi cứu thương.
lo-error-grenade-capacity = Đã mang đủ lựu đạn.
lo-error-ammo-capacity = Đạn dự trữ đã đầy.
lo-error-perk-owned = Bạn đã có kỹ năng này.
lo-error-perk-capacity = Đã đủ số kỹ năng.
lo-error-no-primary = Mua súng chính trước.
lo-error-upgraded = Vũ khí này đã được nâng cấp.
lo-event-heal-self = { $actor } đã dùng túi cứu thương; máu hiện tại { $amount }.
lo-event-heal-self-personal = Bạn tự chữa thương; máu hiện tại { $amount }.
lo-event-heal-target = { $actor } chữa cho bạn; máu hiện tại { $amount }.
lo-event-revive-target = { $actor } cứu bạn dậy với { $amount } máu. Bạn hành động từ chu kỳ sau.
lo-event-hurt-personal = Bạn chịu { $count } đòn từ { $item }, tổng { $amount } sát thương tại { $zone }.
lo-event-down-personal = Bạn đã gục tại { $zone }. Đội còn hai lượt địch kế tiếp để cứu bạn.
lo-event-down-solo-recovery = { $target } gục tại { $zone }. Hồi phục khẩn cấp sau khi lượt địch kết thúc { $recovery_seconds } giây.
lo-event-down-solo-recovery-personal = Bạn gục tại { $zone }. Hồi phục khẩn cấp sau khi lượt địch kết thúc { $recovery_seconds } giây.
lo-event-down-solo-final = { $target } gục tại { $zone }. Không còn người đứng vững hay lượt hồi phục.
lo-event-down-solo-final-personal = Bạn gục tại { $zone }. Không còn người đứng vững hay lượt hồi phục.
lo-event-incapacitated-personal = Bạn mất khả năng chiến đấu đến đợt sau.
lo-event-recovery-personal = Bạn đã dùng lần hồi phục cuối. Máu { $amount }; lượt tới { $count } AP. Hàng ở lại nơi bạn ngã xuống.
lo-event-fire-personal = Bạn bắn { $item } tại { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife-personal = Bạn đâm dao tại { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade-personal = Bạn ném lựu đạn tại { $zone }. { $hits }. { lo-combat-kills }
lo-event-move-personal = Bạn đi từ { $origin } đến { $zone }.
lo-event-reload-personal = Bạn nạp { $amount } viên vào { $item }.
lo-event-heal-personal = Bạn chữa cho { $target }; máu hiện tại { $amount }.
lo-event-revive-personal = Bạn cứu { $target } dậy với { $amount } máu.
lo-event-open-personal = Bạn mở { $item }; còn { $amount } linh kiện. { $routes }
lo-event-repair-personal = Bạn sửa rào tại { $zone } lên { $amount } độ bền.
lo-event-work-personal = { $count ->
    [1] Bạn đã khôi phục { $item } tại { $zone }.
   *[0] Bạn sửa { $item } tại { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo-personal = Bạn mua { $amount } viên cho { $item }, trả { $count } tín dụng.
lo-event-buy-personal = Bạn mua { $item }; còn { $amount } tín dụng.
lo-event-perk-personal = Bạn nhận kỹ năng { $item }.
lo-event-upgrade-personal = Bạn nâng cấp { $item }.
lo-event-equip-personal = Bạn đổi sang { $item }.
lo-event-ready-personal = Bạn { $amount ->
    [1] sẵn sàng cho đợt tiếp theo.
   *[0] chưa sẵn sàng.
    }
lo-event-end-personal = Bạn đã kết thúc lượt.
lo-term-horde = địch
lo-help-move-destination = { $description } { lo-help-move }
lo-zone-description-courtyard = Nền bê tông nứt nẻ bao quanh một cột cờ trơ trọi giữa sân. Xưởng Sửa Chữa nằm phía tây, Trạm Quân Y ở phía đông; phía nam là Nhà Gác, nhìn ra bóng tối ngoài hàng rào.
lo-zone-description-gatehouse = Phía nam Sân Trong, mái nhà gác đã sập, để lộ những tấm ván sàn dằm xước dưới trời đêm. Chiếc ghế gác bỏ không quay về lối vào tiền đồn, nơi hàng rào gặp con đường ngoài kia.
lo-zone-description-workshop = Dầu loang dưới những bàn sửa chữa bỏ dở, vệt gỉ chảy dài trên vách tôn. Tủ đạn kê sát tường cuối xưởng; cổng kỹ thuật dẫn về phía máy phát điện.
lo-zone-description-infirmary = Những chiếc giường hẹp kê dọc gian nhà gỗ phía đông Sân Trong. Băng gạc phủ bụi vắt trên xe đẩy đổ nghiêng, ô cửa sổ hắt ánh sáng nhợt nhạt. Một lối bên hông dẫn sang Nhà Bơm.
lo-zone-description-loading = Sàn thép hoen gỉ chạy dọc những chồng ván kê hàng trống ngoài trời. Xưởng Sửa Chữa nằm phía nam; lối phía đông dẫn vào khoảng ẩm thấp của Nhà Bơm.
lo-zone-description-generator = Sau cổng kỹ thuật của Xưởng Sửa Chữa, một cỗ máy phát điện nằm choán gian phòng bê tông. Cáp dày bò ngang sàn thép đến tủ điện sứt sẹo. Nguồn điện của tiền đồn được khôi phục tại đây.
lo-zone-description-pump = Nước ngập xâm xấp mặt sàn dưới những đường ống lớn và van gỉ sét. Vệt nước cũ hằn trên tường bê tông. Lối từ Trạm Quân Y gặp đường từ Bãi Bốc Dỡ tại đây.
lo-zone-description-roof = Cột ăng-ten nghiêng trên mái bê tông trống trải, dây chằng căng giữa nền trời. Máy vô tuyến nằm trong chiếc tủ chống mưa móp méo. Các cổng dẫn lên từ bên dưới cần điện mới mở được.
lo-option-map = Bản đồ: { $value }
lo-prompt-map = Chọn bản đồ
lo-change-map = Đã chọn bản đồ { $value }.
lo-desc-map = Tiền Đồn Bỏ Hoang: những dãy nhà xơ xác quanh khoảng sân trống. Ga Chuyển Tuyến: đường ray vắng dưới cầu vượt hẹp. Nhà Máy Ngập: các gian máy ngập nước, ngăn cách bởi những cánh cổng nặng nề.
lo-option-mode = Chế độ: { $value }
lo-prompt-mode = Chọn chế độ
lo-change-mode = Đã chọn chế độ { $value }.
lo-desc-mode = Chiến Dịch: nhiệm vụ và hạ tầng. Cố Thủ: bảo vệ trạm. Thu Hồi: vận chuyển hàng. Rút Quân Cổ Điển: tám đợt, điện, vô tuyến và chuyến vật tư cuối.
lo-extraction-route = Đợt { $wave }: chuyển vật tư từ { $pickup } đến { $destination } trong { $deadline } lượt địch. Nơi nhận và giao không được có địch bên trong. Mang hàng: thêm 1 AP mỗi lần đi, chỉ bắn súng ngắn.
lo-option-difficulty = Độ khó: { $value }
lo-prompt-difficulty = Chọn độ khó
lo-change-difficulty = Đã chọn độ khó { $value }.
lo-desc-difficulty = Tân Binh: hồi phục tốt hơn, nhiều vật tư hơn. Tiêu Chuẩn: đông địch hơn, điều kiện thay đổi. Kỳ Cựu: áp lực cao nhất, ít tín dụng, không hồi máu cho người còn đứng hay cấp đạn súng ngắn sau đợt.
lo-error-scenario = Bản đồ, chế độ hoặc độ khó không hợp lệ. Kiểm tra tùy chọn phòng chờ.
lo-event-start = { $map }. { $mode }, { $difficulty }. { $waves } đợt. Xuất phát tại { $spawn }.
lo-scenario-status = { $map }; { $mode }; { $difficulty }. { $condition }.
lo-mission-status-retrieve = Hàng tại { $cargo }; người mang { $carrier }; giao đến { $destination }. Còn { $remaining } lượt địch.
lo-mission-status-relay = Hai bảng điều khiển: { $zone } và { $destination }. Còn { $remaining } lượt địch.
lo-mission-status-hold = Giữ { $zone }: { $progress } trên { $total } lượt phòng thủ. Còn { $remaining } lượt địch.
lo-mission-help-retrieve = 1 AP để nhặt, giao, chuyển hoặc đặt hàng xuống. Không được có địch trong khu, trừ khi đặt hàng xuống. Mang hàng: thêm 1 AP mỗi lần đi, chỉ bắn súng ngắn. Gục sẽ làm rơi hàng; hạn giao không đổi.
lo-mission-help-relay = { $survivor_count ->
    [1] 1 AP mỗi trạm, không được có địch trong khu. Kích hoạt cả hai trạm; trạm đã bật không cần bật lại ở chu kỳ sau. Cuối lượt địch, cả hai nơi đều phải hết địch.
   *[other] 1 AP mỗi trạm, không được có địch trong khu. Hai người bật hai trạm trong cùng chu kỳ rồi sống sót tại đó qua lượt địch. Cuối lượt, cả hai nơi đều phải hết địch.
    }
lo-mission-help-hold = Cuối hai lượt địch, phải có người còn đứng tại điểm phòng thủ và không có địch bên trong. Bỏ trống hoặc còn địch sẽ mất một bước tiến độ. Trong Cố Thủ, tiếp tục giữ trạm đến hết đợt; quá hạn làm mất độ bền.
lo-terminal-status = { $zone }: người kích hoạt { $actor }.
lo-verb-mission = Thực hiện nhiệm vụ
lo-verb-handoff = Chuyển kiện hàng
lo-verb-drop = Đặt kiện hàng xuống
lo-verb-guard = Thủ thế
lo-help-mission = 1 AP; thực hiện nhiệm vụ tại đây khi không có địch trong khu.
lo-help-handoff = 1 AP; chuyển hàng cho đồng đội còn đứng cùng khu, khi không có địch bên trong.
lo-help-drop = 1 AP; đặt hàng xuống. Di chuyển và bắn súng chính trở lại bình thường.
lo-help-guard = 1 AP; đỡ đòn kế tiếp trong khu, giảm một sát thương. Hết hiệu lực ở chu kỳ sau; không cộng dồn hay kéo địch từ xa.
lo-error-guarded = Bạn đã thủ thế.
lo-error-carrying = Mang hàng không bắn được súng chính. Dùng súng ngắn hoặc đặt hàng xuống.
lo-error-terminal = Bảng điều khiển này đã được kích hoạt.
lo-error-relay-partner = Cần người khác kích hoạt bảng còn lại.
lo-task-activate = Kích hoạt bảng này; điểm phối hợp: { $zone }
lo-task-pickup = Nhặt hàng để giao đến { $zone }
lo-task-deliver = Giao hàng tại { $zone }
lo-event-mission_complete = { $party_size ->
    [1] Hoàn thành { $item }: { $sites }. +{ $count } tín dụng; +1 linh kiện. { $defense }
   *[other] Hoàn thành { $item }: { $sites }. Mỗi người +{ $count } tín dụng; đội +1 linh kiện. { $defense }
    }
lo-event-mission_failed = Thất bại: { $item }. Tổng nhiệm vụ thất bại: { $amount }.
lo-event-mission_clock = { $item }: còn { $amount } lượt địch.
lo-event-mission_pressure = Tiếng động kéo { $count } xác sống đến ngoài { $zone }. Chúng hành động từ lượt địch sau.
lo-event-hold_progress = Phòng thủ tại { $zone }: giữ được { $amount } trên { $count } lượt.
lo-event-core_damage = Trạm tại { $zone } mất { $amount } độ bền; còn { $count }.
lo-event-relay_reset = Trạm tiếp sóng: { $item }.
lo-event-cargo_lost = Hàng rơi tại { $zone }.
lo-event-condition = { $item }. Tiếp viện đầu tiên sau lượt địch { $amount }.
lo-term-outpost = Tiền Đồn Bỏ Hoang
lo-term-switchyard = Ga Chuyển Tuyến
lo-term-floodworks = Nhà Máy Ngập
lo-term-operations = Chiến Dịch
lo-term-siege = Cố Thủ
lo-term-salvage = Thu Hồi
lo-term-classic = Rút Quân Cổ Điển
lo-term-recruit = Tân Binh
lo-term-standard = Tiêu Chuẩn
lo-term-veteran = Kỳ Cựu
lo-term-retrieve = Thu hồi hàng
lo-term-relay = Phối hợp nối trạm
lo-term-hold = Giữ khu vực
lo-term-mission_quota = Không đạt yêu cầu nhiệm vụ
lo-term-core_lost = Trạm bị phá hủy
lo-term-latched = các trạm đã bật vẫn sẵn sàng
lo-term-reset = cần kích hoạt lại cả hai trạm trong cùng chu kỳ
lo-term-condition-normal = Điều kiện bình thường
lo-term-condition-rush = Tiếp viện sớm
lo-term-condition-fog = Sương mù: súng chỉ bắn xa một chặng
lo-term-condition-battering = Bầy phá rào: thêm một sát thương lên rào
lo-term-condition-shortage = Thiếu vật tư: mỗi băng dự trữ giá 90 tín dụng
lo-term-depot = Nhà Ga
lo-term-west_tracks = Đường Ray Tây
lo-term-east_tracks = Đường Ray Đông
lo-term-signal_box = Nhà Tín Hiệu
lo-term-freight = Bãi Hàng
lo-term-maintenance = Xưởng Bảo Dưỡng
lo-term-switchgear = Phòng Điện
lo-term-overpass = Cầu Vượt
lo-term-tower = Tháp Vô Tuyến
lo-term-tunnel = Hầm Đường Sắt
lo-term-quay = Bến Đổ Bộ
lo-term-foyer = Sảnh Dẫn Nước
lo-term-canal = Kênh Thoát
lo-term-filter = Bể Lọc
lo-term-control = Phòng Điều Khiển
lo-term-laboratory = Phòng Thí Nghiệm
lo-term-archive = Kho Vật Tư
lo-term-turbine = Gian Tuabin
lo-term-skybridge = Cầu Vô Tuyến
lo-term-clinic = Trạm Y Tế
lo-event-guard = { $actor } thủ thế: đỡ đòn kế tiếp, giảm một sát thương.
lo-event-guard-personal = Bạn thủ thế: đỡ đòn kế tiếp, giảm một sát thương.
lo-event-cargo_pickup = { $actor } nhặt hàng tại { $zone } để giao đến { $origin }.
lo-event-cargo_pickup-personal = Bạn nhặt hàng tại { $zone } để giao đến { $origin }.
lo-event-cargo_deliver = { $actor } giao hàng tại { $zone }.
lo-event-cargo_deliver-personal = Bạn giao hàng tại { $zone }.
lo-event-cargo_drop = { $actor } đặt hàng xuống tại { $zone }.
lo-event-cargo_drop-personal = Bạn đặt hàng xuống tại { $zone }.
lo-event-cargo_handoff = { $actor } chuyển hàng cho { $target } tại { $zone }.
lo-event-cargo_handoff-personal = Bạn chuyển hàng cho { $target } tại { $zone }.
lo-event-relay_armed = { $actor } kích hoạt bảng tại { $zone }; đã bật { $amount } bảng.
lo-event-relay_armed-personal = Bạn kích hoạt bảng tại { $zone }; đã bật { $amount } bảng.
lo-event-cargo_handoff-target = { $actor } chuyển kiện hàng cho bạn tại { $zone }.
lo-zone-description-depot = Những hàng ghế trống quay về bảng giờ tàu chỉ còn lịch hủy chuyến. Bụi phủ mờ nền bê tông. Hai đầu sảnh mở ra các đường ray phía tây và phía đông.
lo-zone-description-west_tracks = Lối đi lát thép men theo đường ray hoen gỉ dưới những đèn tín hiệu đã tắt. Những cọc rào đánh dấu rìa sân ga; qua khỏi Nhà Ga, Nhà Tín Hiệu nhô lên ở phía bắc.
lo-zone-description-east_tracks = Những toa tàu trống nằm cạnh lối đi bằng thép cong vênh. Đường ray kéo dài vào bóng tối ngoài hàng rào; phía bắc mở ra Bãi Hàng.
lo-zone-description-signal_box = Dãy cần gạt chen kín căn nhà gỗ, bên trên là sơ đồ đường tàu bạc màu. Cửa sổ nhìn xuống đường ray phía tây. Các lối bên hông dẫn đến Xưởng Bảo Dưỡng và bậc lên Cầu Vượt.
lo-zone-description-freight = Những thùng hàng khổng lồ sừng sững trên bãi lát thép móp méo. Xích buông lủng lẳng từ khung bốc dỡ. Cổng bãi hàng chặn lối lên Cầu Vượt; một đường khác dẫn vào Hầm Đường Sắt.
lo-zone-description-maintenance = Bánh tàu tháo rời và dụng cụ bám dầu nằm dọc vách tôn. Tủ đạn kê trên nền bê tông lấm bẩn, cạnh cổng kỹ thuật dẫn sang Phòng Điện.
lo-zone-description-switchgear = Sau cổng kỹ thuật là gian phòng bê tông với những dãy cầu dao lớn. Cáp điện luồn dưới các tấm sàn thép, nhãn cảnh báo bong khỏi cửa tủ. Khôi phục điện cho nhà ga tại đây.
lo-zone-description-overpass = Mặt cầu bằng lưới thép bắc qua đường tàu, chỉ có lan can mảnh chắn khoảng trống bên dưới. Nhà Tín Hiệu và Bãi Hàng nằm phía dưới; Tháp Vô Tuyến vươn lên ở phía bắc.
lo-zone-description-tower = Bàn vô tuyến và chiếc ghế gỗ sờn cũ chiếm gần hết căn phòng trên cao. Qua các ô cửa sổ là toàn cảnh sân ga. Các cổng dẫn lên tháp cần điện mới mở được.
lo-zone-description-tunnel = Đường ray mất hút trong hầm bê tông loang muội đen và vệt nước thấm. Bãi Hàng nằm phía sau; một lối bên hông dẫn lên cổng Tháp Vô Tuyến.
lo-zone-description-quay = Ván bến cong vênh nhô trên mặt nước đen, dây neo buông lỏng xuống mép. Đây là rìa phía nam của nhà máy. Phía trước, cửa bê tông mở vào Sảnh Dẫn Nước.
lo-zone-description-foyer = Vệt nước ố leo trên tường bê tông, dưới tấm sơ đồ thoát hiểm bạc màu. Sảnh hẹp chia hai lối: phía tây ra Kênh Thoát, phía đông vào Kho Vật Tư.
lo-zone-description-canal = Nước nông chảy giữa hai bờ bê tông cao, cuốn rong vụn từ bên ngoài vào. Dòng kênh vòng lên phía bắc tới Bể Lọc; sảnh nằm ở phía đông.
lo-zone-description-filter = Nước ngập quanh những dãy bể lọc tắc nghẽn, dưới vách kim loại hoen gỉ. Cổng kỹ thuật dẫn về phía tuabin; một cửa ngăn nước nặng nề chia gian này với Phòng Điều Khiển.
lo-zone-description-control = Dãy đồng hồ đo và màn hình rạn nứt chạy dọc nền kim loại. Phía đông thông sang Phòng Thí Nghiệm, phía tây là cửa ngăn nước; lối phía bắc dẫn lên Cầu Vô Tuyến.
lo-zone-description-laboratory = Lọ mẫu đục màu chen kín mặt bàn, mảnh kính lấp loáng trên nền bê tông. Các cửa nối với Kho Vật Tư, Phòng Điều Khiển và Trạm Y Tế đều dẫn qua gian làm việc bỏ hoang này.
lo-zone-description-archive = Sổ sách trương nước trĩu trên kệ gỗ, cạnh những thùng vật tư đóng kín. Tủ đạn nằm ở góc khô ráo nhất. Phía tây là sảnh, phía bắc là Phòng Thí Nghiệm.
lo-zone-description-turbine = Những khối tuabin khổng lồ chiếm gian nhà kim loại cao rộng. Lối đi giữa chúng được ghép bằng các tấm thép bảo trì. Bảng cấp điện nằm dưới đường lên Cầu Vô Tuyến.
lo-zone-description-skybridge = Cây cầu thép hẹp treo trên các gian phía bắc nhà máy, phơi mình trong gió. Tủ vô tuyến nằm dưới cột ăng-ten; đường từ Phòng Điều Khiển, Trạm Y Tế và Gian Tuabin cùng dẫn về đây.
lo-zone-description-clinic = Rèm bạc màu ngăn những giường khám trong gian phòng bê tông. Hơi ẩm đã len dưới các tủ thuốc. Phòng Thí Nghiệm nằm phía nam; một lối khác dẫn lên Cầu Vô Tuyến.
lo-event-mission_start-retrieve = Chuyển hàng: { $zone } đến { $origin }. Hạn: { $amount } lượt địch.
lo-event-mission_start-relay = Tiếp sóng: { $zone } và { $origin }. Hạn: { $amount } lượt địch.
lo-event-mission_start-hold = Giữ { $zone }. Hạn: { $amount } lượt địch.
lo-error-visibility = Sương mù chặn đường bắn xa hơn một chặng.
lo-help-weapon = Sát thương { $damage }; nâng cấp { $upgraded }; { $targets } mục tiêu; tầm { $minimum }–{ $maximum }; băng { $magazine } viên; { $rounds } viên mỗi lần bắn; { $price } tín dụng. Thay súng chính; không hoàn tiền.
lo-error-barricade = Rào chắn chặn đòn tấn công.
lo-combat-hit = { $enemy }: { $damage } sát thương
lo-combat-outside = { $zone }, { lo-outside }
lo-objective-generator = Nguồn điện
lo-objective-radio = Vô tuyến
lo-combat-kills = { $count ->
    [0] { "" }
    [one] Hạ 1 địch.
   *[other] Hạ { $count } địch.
    }
lo-shop-ready = Mua xong và sẵn sàng
lo-help-shop-ready = E đóng cửa hàng và đánh dấu sẵn sàng. X quay lại, không đánh dấu sẵn sàng.
lo-already-ready = { $party_size ->
    [1] Đã sẵn sàng.
   *[other] Bạn đã sẵn sàng. Đang chờ đồng đội.
    }
lo-help-teammates = { $party_size ->
    [1] Vị trí, máu và nhân vật của bạn.
   *[other] Vị trí, máu, thời hạn cứu hộ và nhân vật của từng đồng đội.
    }
lo-help-objectives = Điều kiện thắng, tiến độ khôi phục hạ tầng và nhiệm vụ hiện tại.
lo-teammates = { $party_size ->
    [1] Nhân vật
   *[other] Đồng đội
    }
lo-required = Bắt buộc
lo-optional = Tùy chọn
lo-complete = Đã hoàn thành
lo-incomplete = Chưa hoàn thành
lo-objective-waves = Bắt buộc: vượt qua mọi đợt. Đã qua { $completed }/{ $total } đợt.
lo-objective-missions = Bắt buộc: hoàn thành { $total } nhiệm vụ. Đã xong { $completed }; thất bại { $failed }.
lo-objective-bonus-missions = Nhiệm vụ: đã xong { $completed }; thất bại { $failed }.
lo-objective-integrity = Bắt buộc: giữ trạm không bị phá hủy. Độ bền { $current }/{ $total }.
lo-objective-project = { $project }, { $zone }: { $requirement }. { $state }; tiến độ { $progress }/{ $total }. Còn { $remaining } bước, cần { $cost } linh kiện, chưa tính cổng dẫn vào nếu còn đóng.
lo-mission-idle = Chưa có nhiệm vụ đang diễn ra.
lo-verb-unready = Hủy sẵn sàng

lo-health-recovering = Đã gục; hồi phục khẩn cấp sau khi lượt địch kết thúc { $recovery_seconds } giây
lo-inventory-parts = { $party_size ->
    [1] Linh kiện: { $parts }.
   *[other] Linh kiện chung: { $parts }.
    }
lo-board-lineup = { $count ->
    [1] Một người sống sót
   *[other] Đội { $count }: { $humans } người chơi, { $bots } bot
    }
lo-board-original = Không có bot chơi thay
lo-board-takeover = Có bot chơi thay
leaderboard-lo-clear-entry = { $rank }. { $player }: { $value } lượt bầy xác sống.
lo-personal-record = { $name }: { $value } lượt bầy xác sống.
lo-record-unranked = Không xếp hạng: đội hình ban đầu đã thay đổi.
