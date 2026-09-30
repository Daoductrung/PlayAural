# Bóng Lăn

game-name-rollingballs = Bóng Lăn

# Hành động
rb-take = Rút { $count } { $count ->
    [one] quả bóng
   *[other] quả bóng
}
rb-reshuffle-action = Xáo đoạn đầu ống (còn { $remaining } lần)
rb-view-pipe-action = Xem trước trong ống (còn { $remaining } lần)
rb-check-pipe-status = Kiểm tra trạng thái ống
rb-key-reshuffle-pipe = Xáo đoạn đầu ống
rb-key-view-pipe = Xem trước trong ống

# Rút và công bố bóng
rb-you-take = Bạn chọn rút { $count } { $count ->
    [one] quả bóng
   *[other] quả bóng
} ở đầu ống đang có { $remaining } quả.
rb-player-takes = { $player } chọn rút { $count } { $count ->
    [one] quả bóng
   *[other] quả bóng
} ở đầu ống đang có { $remaining } quả.
rb-you-take-brief = Bạn rút { $count } { $count ->
    [one] quả bóng
   *[other] quả bóng
}.
rb-player-takes-brief = { $player } rút { $count } { $count ->
    [one] quả bóng
   *[other] quả bóng
}.
rb-you-forced-take = Chỉ còn { $count } { $count ->
    [one] quả bóng
   *[other] quả bóng
}, ít hơn mức rút tối thiểu { $minimum }, nên bạn phải rút hết số còn lại.
rb-player-forced-takes = Chỉ còn { $count } { $count ->
    [one] quả bóng
   *[other] quả bóng
}, ít hơn mức rút tối thiểu { $minimum }, nên { $player } phải rút hết số còn lại.
rb-you-forced-take-brief = Bạn phải rút { $count } { $count ->
    [one] quả bóng cuối cùng
   *[other] quả bóng cuối cùng
}.
rb-player-forced-takes-brief = { $player } phải rút { $count } { $count ->
    [one] quả bóng cuối cùng
   *[other] quả bóng cuối cùng
}.

rb-your-ball-plus = Bóng số { $num } của bạn: { $description }. Cộng { $value } { $value ->
    [one] điểm
   *[other] điểm
}.
rb-player-ball-plus = Bóng số { $num } của { $player }: { $description }. Cộng { $value } { $value ->
    [one] điểm
   *[other] điểm
}.
rb-your-ball-minus = Bóng số { $num } của bạn: { $description }. Trừ { $value } { $value ->
    [one] điểm
   *[other] điểm
}.
rb-player-ball-minus = Bóng số { $num } của { $player }: { $description }. Trừ { $value } { $value ->
    [one] điểm
   *[other] điểm
}.
rb-your-ball-zero = Bóng số { $num } của bạn: { $description }. Điểm không đổi.
rb-player-ball-zero = Bóng số { $num } của { $player }: { $description }. Điểm không đổi.

rb-your-draw-summary = Lượt rút { $count } bóng của bạn có tổng giá trị { $delta } điểm. Bạn đang có { $score } điểm; trong ống còn { $remaining } bóng.
rb-player-draw-summary = Lượt rút { $count } bóng của { $player } có tổng giá trị { $delta } điểm. { $player } đang có { $score } điểm; trong ống còn { $remaining } bóng.
rb-your-draw-summary-brief = Tổng { $delta }; bạn có { $score } điểm. Còn { $remaining } bóng.
rb-player-draw-summary-brief = { $player }: tổng { $delta }, có { $score } điểm. Còn { $remaining } bóng.
rb-your-score-legacy = Bạn đang có { $score } điểm; trong ống còn { $remaining } bóng.
rb-player-score-legacy = { $player } đang có { $score } điểm; trong ống còn { $remaining } bóng.

# Xáo bóng
rb-you-reshuffle = Bạn xáo { $count } quả bóng đầu ống. { $penalty ->
    [0] Bạn không bị phạt điểm
   *[other] Bạn bị trừ { $penalty } điểm
}; hiện bạn có { $score } điểm và còn { $remaining } lần xáo.
rb-player-reshuffles = { $player } xáo { $count } quả bóng đầu ống. { $penalty ->
    [0] { $player } không bị phạt điểm
   *[other] { $player } bị trừ { $penalty } điểm
}; hiện { GENDER_TERM($player_gender, "subject-have") } { $score } điểm và còn { $remaining } lần xáo.
rb-you-reshuffle-brief = Bạn xáo { $count } bóng; phạt { $penalty }, điểm { $score }, còn { $remaining } lần.
rb-player-reshuffles-brief = { $player } xáo { $count } bóng; phạt { $penalty }, điểm { $score }, còn { $remaining } lần.

# Xem trước và trạng thái ống
rb-view-pipe-header = Đang hiển thị { $shown } quả tiếp theo trong tổng số { $total } quả. Bạn còn { $remaining } lượt xem nội dung mới.
rb-view-pipe-ball = { $num }: { $description }. Giá trị: { $value } điểm.
rb-status-pipe = Vòng { $round }. Trong ống còn { $count } quả bóng.
rb-status-take-range = Mỗi lượt bình thường phải rút từ { $min } đến { $max } quả bóng.
rb-status-turn = Lượt hiện tại: { $player }.
rb-status-resources = Bạn còn { $views } lượt xem nội dung mới và { $reshuffles } lần xáo.

# Bắt đầu và vòng chơi
rb-pipe-filled = Ống đã được nạp { $count } quả bóng không trùng nhau từ: { $packs }.
rb-round-start = Vòng { $round } bắt đầu; trong ống còn { $count } quả bóng.
rb-round-start-brief = Vòng { $round }; còn { $count } bóng.

# Kết thúc
rb-pipe-empty = Ống đã hết bóng.
rb-winner = { $player } thắng với { $score } điểm.
rb-you-win = Bạn thắng với { $score } điểm.
rb-you-tie = Bạn đồng chiến thắng cùng { $players }; mỗi người đạt { $score } điểm.
rb-tie = { $players } đồng chiến thắng với { $score } điểm.
rb-line-format = { $rank }. { $player }: { $points }

# Tùy chọn
rb-set-min-take = Số bóng rút tối thiểu mỗi lượt: { $count }
rb-enter-min-take = Nhập số bóng rút tối thiểu mỗi lượt, từ 1 đến 5:
rb-option-changed-min-take = Đã đặt số bóng rút tối thiểu mỗi lượt là { $count }.
rollingballs-desc-min-take = Số bóng tối thiểu người chơi phải lấy trong một lượt (mặc định 1, phạm vi 1-5).
rb-set-max-take = Số bóng rút tối đa mỗi lượt: { $count }
rb-enter-max-take = Nhập số bóng rút tối đa mỗi lượt, từ 1 đến 5:
rb-option-changed-max-take = Đã đặt số bóng rút tối đa mỗi lượt là { $count }.
rollingballs-desc-max-take = Số bóng tối đa người chơi được lấy trong một lượt. Trò chơi không thể bắt đầu nếu mức này thấp hơn số bóng tối thiểu (mặc định 3, phạm vi 1-5).
rb-set-view-pipe-limit = Lượt xem nội dung mới cho mỗi người: { $count }
rb-enter-view-pipe-limit = Nhập số lượt xem nội dung mới cho mỗi người, từ 0 đến 100; nhập 0 để tắt:
rb-option-changed-view-pipe-limit = Đã đặt số lượt xem nội dung mới cho mỗi người là { $count }.
rollingballs-desc-view-pipe-limit = Số bóng sắp tới có thể xem trước trong ống. Đặt 0 để tắt xem trước (mặc định 5, phạm vi 0-100).
rb-set-reshuffle-limit = Số lần xáo cho mỗi người: { $count }
rb-enter-reshuffle-limit = Nhập số lần xáo cho mỗi người, từ 0 đến 100; nhập 0 để tắt:
rb-option-changed-reshuffle-limit = Đã đặt số lần xáo cho mỗi người là { $count }.
rollingballs-desc-reshuffle-limit = Số lần xào lại có sẵn trước khi ống bóng cạn (mặc định 3, phạm vi 0-100).
rb-set-reshuffle-penalty = Điểm phạt mỗi lần xáo: { $points } điểm
rb-enter-reshuffle-penalty = Nhập điểm phạt mỗi lần xáo, từ 0 đến 5 điểm:
rb-option-changed-reshuffle-penalty = Đã đặt điểm phạt mỗi lần xáo là { $points } điểm.
rollingballs-desc-reshuffle-penalty = Điểm phạt áp dụng khi dùng xào lại. Tùy chọn này chỉ xuất hiện khi người chơi có lượt xào lại (mặc định 1, phạm vi 0-5).
rb-set-ball-packs = Bộ bóng (đã chọn { $count } trên { $total })
rb-option-changed-ball-packs = Đã thay đổi các bộ bóng được chọn.
rollingballs-desc-ball-packs = Chọn các bộ bóng theo chủ đề được đưa vào ống. Phải giữ lại ít nhất một bộ.

# Lý do vô hiệu hóa và kiểm tra thiết lập
rb-draw-resolving = Hãy chờ lượt công bố bóng hiện tại của { $player } kết thúc rồi mới thực hiện hành động khác với ống.
rb-take-not-your-turn = Bạn chưa thể rút { $count } bóng vì đang là lượt của { $player }.
rb-take-outside-range = Bạn chọn rút { $count } bóng, nhưng ván này chỉ cho phép rút từ { $min } đến { $max } bóng trong lượt bình thường.
rb-not-enough-balls = Bạn chọn rút { $count } bóng, nhưng trong ống chỉ còn { $remaining } bóng.
rb-reshuffle-not-your-turn = Bạn chưa thể xáo bóng vì đang là lượt của { $player }.
rb-no-reshuffles-left = Bạn đã dùng hết { $limit } lần xáo trong ván này.
rb-already-reshuffled = Bạn đã xáo bóng trong lượt này. Hãy rút bóng để kết thúc lượt.
rb-not-enough-balls-to-reshuffle = Cần ít nhất { $required } bóng để xáo, nhưng trong ống chỉ còn { $remaining } bóng. Hãy rút bóng thay vì xáo.
rb-no-views-left = Nội dung đầu ống đã thay đổi và bạn đã dùng hết { $limit } lượt xem nội dung mới. Nếu ống chưa đổi, bạn vẫn có thể mở lại lần xem gần nhất.
rb-error-min-take-invalid = Mức rút tối thiểu đang là { $count }; giá trị hợp lệ là từ { $min } đến { $max }.
rb-error-max-take-invalid = Mức rút tối đa đang là { $count }; giá trị hợp lệ là từ { $min } đến { $max }.
rb-error-take-range-conflict = Mức rút tối thiểu là { $min }, cao hơn mức tối đa { $max }. Hãy giảm mức tối thiểu hoặc tăng mức tối đa trước khi bắt đầu.
rb-error-view-limit-invalid = Giới hạn xem đang là { $count }; giá trị hợp lệ là từ { $min } đến { $max }.
rb-error-reshuffle-limit-invalid = Giới hạn xáo đang là { $count }; giá trị hợp lệ là từ { $min } đến { $max }.
rb-error-reshuffle-penalty-invalid = Điểm phạt xáo đang là { $points }; giá trị hợp lệ là từ { $min } đến { $max } điểm.
rb-error-no-ball-packs = Hãy chọn ít nhất một bộ bóng trước khi bắt đầu Bóng Lăn.
rb-error-invalid-ball-packs = Lựa chọn hiện có { $count } { $count ->
    [one] bộ bóng không còn khả dụng
   *[other] bộ bóng không còn khả dụng
}. Hãy bỏ các bộ này trước khi bắt đầu.

# Bộ bóng
rb-pack-international = Vòng quanh thế giới
rb-pack-vietnam = Hành trình Việt Nam

# Vòng quanh thế giới: -5
rb-ball-paris-pickpocket = Mất hộ chiếu và ví khi đang ở nước ngoài
rb-ball-lost-luggage-in-london = Phải đi cấp cứu giữa chuyến đi
rb-ball-tokyo-train-delay = Lỡ chuyến nối quốc tế cuối ngày
rb-ball-sahara-sandstorm = Phải sơ tán vì thời tiết nguy hiểm
rb-ball-passport-lost-before-flight = Thất lạc hộ chiếu trước giờ khởi hành
# Vòng quanh thế giới: -4
rb-ball-venice-flood = Nơi lưu trú đóng cửa vì ngập
rb-ball-new-york-traffic = Chuyến bay đêm bị hủy
rb-ball-amazon-mosquito-swarm = Hành lý thiết yếu bị gửi nhầm sang nước khác
rb-ball-berlin-club-rejected = Đến nơi mới biết khách sạn không có tên đặt phòng
rb-ball-hotel-booking-vanished = Tuyến đường núi đóng nhiều ngày
# Vòng quanh thế giới: -3
rb-ball-spilled-coffee-in-rome = Điện thoại nứt màn hình lúc chuyển chặng
rb-ball-sydney-sunburn = Kiệt sức vì nóng, phải hủy chuyến đi trong ngày
rb-ball-istanbul-bazaar-scam = Tour đã trả trước bất ngờ bị hủy
rb-ball-moscow-blizzard = Tàu mắc kẹt vì bão tuyết
rb-ball-dubai-heatwave = Xe thuê bị hỏng giữa đường
# Vòng quanh thế giới: -2
rb-ball-mexico-city-smog = Phải đổi lịch trình vì chất lượng không khí kém
rb-ball-cairo-camel-spit = Say xe trên chặng đường dài
rb-ball-athens-ruins-trip = Bong gân khi đi bộ tham quan
rb-ball-rio-carnival-hangover = Ngủ quên, lỡ tour buổi sáng
rb-ball-bali-belly = Đau bụng, mất nửa ngày khám phá
# Vòng quanh thế giới: -1
rb-ball-swiss-alps-avalanche = Đường mòn ngắm cảnh tạm đóng để bảo đảm an toàn
rb-ball-amsterdam-bicycle-crash = Xe đạp bị xẹp lốp
rb-ball-bangkok-tuk-tuk-breakdown = Xe tuk-tuk chết máy giữa dòng xe
rb-ball-iceland-volcano-ash = Cảnh báo thời tiết làm chuyến bay chậm
rb-ball-cape-town-wind = Điểm ngắm cảnh đóng cửa vì gió mạnh
# Vòng quanh thế giới: 0
rb-ball-neutral-passport = Thêm một dấu mộc vào hộ chiếu
rb-ball-airport-layover = Khoảng chờ yên tĩnh ở sân bay
rb-ball-hotel-lobby = Ngồi chờ tại sảnh khách sạn
rb-ball-tourist-map = Mở bản đồ thành phố
rb-ball-souvenir-magnet = Chọn một chiếc nam châm lưu niệm
# Vòng quanh thế giới: +1
rb-ball-free-museum-day = Được vào bảo tàng miễn phí
rb-ball-street-food-snack = Món ăn đường phố ngon bất ngờ
rb-ball-post-card-home = Gửi bưu thiếp về nhà
rb-ball-friendly-local = Được người địa phương nhiệt tình chỉ đường
rb-ball-sunny-day = Thời tiết hoàn hảo để khám phá
# Vòng quanh thế giới: +2
rb-ball-eiffel-tower-view = Ngắm Paris từ tháp Eiffel
rb-ball-taj-mahal-sunrise = Bình minh tại Taj Mahal
rb-ball-great-wall-hike = Đi bộ trên Vạn Lý Trường Thành
rb-ball-machu-picchu-climb = Buổi sáng ở Machu Picchu
rb-ball-kyoto-cherry-blossoms = Ngắm hoa anh đào tại Kyoto
# Vòng quanh thế giới: +3
rb-ball-colosseum-tour = Tham quan Đấu trường La Mã cùng hướng dẫn viên
rb-ball-pyramids-exploration = Khám phá quần thể kim tự tháp Giza
rb-ball-santorini-sunset = Ngắm hoàng hôn Santorini
rb-ball-aurora-borealis = Bắc cực quang rực sáng trên đầu
rb-ball-safari-lion-sighting = Gặp động vật hoang dã trong chuyến safari có trách nhiệm
# Vòng quanh thế giới: +4
rb-ball-bora-bora-villa = Nghỉ bên đầm phá Bora Bora
rb-ball-maldives-scuba = Lặn ngắm rạn san hô Maldives
rb-ball-niagara-falls-boat = Đi thuyền dưới thác Niagara
rb-ball-grand-canyon-heli = Ngắm Grand Canyon từ trên không
rb-ball-serengeti-migration = Chứng kiến cuộc đại di cư ở Serengeti
# Vòng quanh thế giới: +5
rb-ball-first-class-upgrade = Bất ngờ được nâng lên khoang hạng nhất
rb-ball-lottery-in-macau = Trúng thẻ đi tàu dùng suốt một năm
rb-ball-private-jet = Chuyến hải trình khám phá đảo chỉ có một lần trong đời
rb-ball-royal-palace-invite = Tham quan bảo tàng riêng sau giờ đóng cửa
rb-ball-world-tour-ticket = Tấm vé vòng quanh thế giới

# Hành trình Việt Nam: -5
rb-ball-stolen-motorbike = Mất hộ chiếu và ví giữa hành trình
rb-ball-flooded-street-saigon = Phải chuyển chỗ ở khẩn cấp vì ngập
rb-ball-food-poisoning-bun-mam = Sự cố sức khỏe làm gián đoạn chuyến đi
rb-ball-fake-taxi-scam = Xe gặp sự cố khiến bạn lỡ chuyến bay
rb-ball-passport-lost-at-airport = Thất lạc hộ chiếu tại sân bay
# Hành trình Việt Nam: -4
rb-ball-typhoon-in-central-vietnam = Phải sơ tán vì bão ở duyên hải miền Trung
rb-ball-lost-wallet-ben-thanh = Hành lý thiết yếu thất lạc khi chuyển chặng
rb-ball-traffic-jam-hanoi = Chuyến tàu đêm bị hủy
rb-ball-pickpocketed-in-bui-vien = Mất điện thoại ở khu phố đông người
rb-ball-mountain-road-landslide = Đèo núi đóng vì sạt lở
# Hành trình Việt Nam: -3
rb-ball-spilled-pho = Máy ảnh hỏng vì cơn mưa bất chợt
rb-ball-overcharged-for-coffee = Khách sạn nhầm thông tin đặt phòng
rb-ball-sunburn-in-mui-ne = Kiệt sức vì nóng ở Mũi Né
rb-ball-missed-train-to-sapa = Lỡ chuyến tàu đêm đi Lào Cai
rb-ball-loud-karaoke-next-door = Mất ngủ trước giờ khởi hành sớm
# Hành trình Việt Nam: -2
rb-ball-broken-flip-flop = Đứt quai dép giữa chuyến đi bộ
rb-ball-sudden-downpour = Gặp mưa rào nhiệt đới bất chợt
rb-ball-dog-chased-you = Xuống nhầm điểm xe buýt cách xa khách sạn
rb-ball-bitten-by-mosquitoes = Một tối bị muỗi đốt liên tục
rb-ball-out-of-gas = Xe máy hết xăng giữa đường
# Hành trình Việt Nam: -1
rb-ball-spicy-chili-bite = Cắn phải miếng ớt cay ngoài dự kiến
rb-ball-delayed-flight = Chuyến bay nội địa chậm một lúc
rb-ball-wifi-disconnected = Sóng yếu khi lên vùng núi
rb-ball-forgot-umbrella = Để quên áo mưa ở khách sạn
rb-ball-minor-scratch = Rẽ nhầm đường trong khu phố cổ
# Hành trình Việt Nam: 0
rb-ball-plastic-stool = Ngồi nghỉ trên chiếc ghế nhựa vỉa hè
rb-ball-iced-tea-tra-da = Uống một ly trà đá
rb-ball-waiting-for-green-light = Chờ qua một nhịp đèn đỏ dài
rb-ball-bamboo-hat = Thử đội nón lá
rb-ball-motorbike-helmet = Cài quai mũ bảo hiểm
# Hành trình Việt Nam: +1
rb-ball-tasty-banh-mi = Ăn ổ bánh mì giòn cho bữa sáng
rb-ball-free-sugar-cane-juice = Uống ly nước mía tươi
rb-ball-friendly-street-vendor = Được cô chú tiểu thương đón tiếp niềm nở
rb-ball-cool-breeze = Gió mát sau cơn mưa
rb-ball-found-10k-vnd = Đi xe buýt địa phương vừa rẻ vừa tiện
# Hành trình Việt Nam: +2
rb-ball-delicious-pho-bowl = Thưởng thức tô phở thơm lừng
rb-ball-egg-coffee-in-hanoi = Nhâm nhi cà phê trứng Hà Nội
rb-ball-boat-ride-in-ninh-binh = Ngồi thuyền khám phá Quần thể danh thắng Tràng An
rb-ball-lantern-festival-hoian = Dạo Phố cổ Hội An trong đêm đèn lồng
rb-ball-motorbike-road-trip = Đi thuyền giữa vườn cây ở Đồng bằng sông Cửu Long
# Hành trình Việt Nam: +3
rb-ball-ha-long-bay-cruise = Du ngoạn Vịnh Hạ Long - quần đảo Cát Bà
rb-ball-golden-bridge-bana-hills = Ngắm Cầu Vàng trên Bà Nà Hills
rb-ball-phu-quoc-sunset = Ngắm hoàng hôn Phú Quốc
rb-ball-sapa-terraced-fields = Ngắm ruộng bậc thang quanh Sa Pa
rb-ball-phong-nha-cave-exploration = Khám phá hang động Phong Nha - Kẻ Bàng
# Hành trình Việt Nam: +4
rb-ball-tet-holiday-lucky-money = Sum họp và nhận lì xì ngày Tết
rb-ball-vip-ticket-to-concert = Đón bình minh trên cung đường Hà Giang
rb-ball-luxury-resort-stay = Tham gia hoạt động bảo tồn cùng cộng đồng ở Côn Đảo
rb-ball-business-class-flight = Nằm khoang giường ngắm cảnh trên tàu Thống Nhất
rb-ball-won-lottery-vietlott = Đêm lễ hội giữa Quần thể di tích Cố đô Huế
# Hành trình Việt Nam: +5
rb-ball-billionaire-inheritance = Thám hiểm hang Sơn Đoòng
rb-ball-found-gold-treasure = Học nghề thủ công riêng cùng nghệ nhân bậc thầy
rb-ball-free-house-in-district-1 = Một tháng xuyên Việt bằng đường sắt
rb-ball-national-hero-award = Trở thành khách quý trong lễ hội làng
rb-ball-ultimate-happiness = Hành trình trong mơ từ Hà Giang đến Cà Mau
