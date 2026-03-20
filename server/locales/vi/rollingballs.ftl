# Thông báo trò chơi Bóng Lăn (Rolling Balls)
# Lưu ý: Các thông báo chung như bắt đầu vòng, bắt đầu lượt nằm trong games.ftl

# Tên trò chơi
game-name-rollingballs = Bóng Lăn

# Hành động trong lượt
rb-take = Rút { $count } { $count ->
    [one] quả bóng
    *[other] quả bóng
}
rb-reshuffle-action = Xóc lại ống (còn { $remaining } lần)
rb-view-pipe-action = Xem trộm ống (còn { $remaining } lần)

# Sự kiện rút bóng
rb-you-take = Bạn đã rút { $count } { $count ->
    [one] quả bóng
    *[other] quả bóng
}!
rb-player-takes = { $player } đã rút { $count } { $count ->
    [one] quả bóng
    *[other] quả bóng
}!
rb-ball-plus = Bóng số { $num }: { $description }! Được cộng { $value } điểm!
rb-ball-minus = Bóng số { $num }: { $description }! Bị trừ { $value } điểm!
rb-ball-zero = Bóng số { $num }: { $description }! Không mất điểm!
rb-new-score = Điểm của { $player }: { $score } điểm.

# Sự kiện xóc lại ống
rb-you-reshuffle = Bạn vừa xóc lại ống!
rb-player-reshuffles = { $player } vừa xóc lại ống!
rb-reshuffled = Chiếc ống đã được xóc tung lên!
rb-reshuffle-penalty = { $player } bị trừ { $points } { $points ->
    [one] điểm
    *[other] điểm
} vì tội xóc lại ống.

# Xem trộm ống
rb-view-pipe-header = Trong ống đang có { $count } quả bóng:
rb-view-pipe-ball = { $num }: { $description }. Giá trị: { $value } điểm.

# Bắt đầu trò chơi
rb-pipe-filled = Ống đã được nạp đầy với { $count } quả bóng!
rb-balls-remaining = Còn { $count } quả bóng trong ống.

# Kết thúc trò chơi
rb-pipe-empty = Ống đã trống không!
rb-score-line = { $player }: { $score } điểm.
rb-winner = Người chiến thắng là { $player } với { $score } điểm!
rb-you-win = Chúc mừng! Bạn đã thắng với { $score } điểm!
rb-tie = Trận đấu hòa giữa { $players } với { $score } điểm!
rb-line-format = { $rank }. { $player }: { $points }

# Tùy chọn
rb-set-min-take = Số bóng tối thiểu phải rút mỗi lượt: { $count }
rb-enter-min-take = Nhập số lượng bóng tối thiểu phải rút (từ 1 đến 5):
rb-option-changed-min-take = Số bóng rút tối thiểu đã được đặt là { $count }.

rb-set-max-take = Số bóng tối đa được rút mỗi lượt: { $count }
rb-enter-max-take = Nhập số lượng bóng tối đa được rút (từ 1 đến 5):
rb-option-changed-max-take = Số bóng rút tối đa đã được đặt là { $count }.

rb-set-view-pipe-limit = Số lần được xem trộm ống: { $count }
rb-enter-view-pipe-limit = Nhập số lần được xem trộm ống (0 để tắt, tối đa 100):
rb-option-changed-view-pipe-limit = Số lần xem trộm ống đã được đặt là { $count }.

rb-set-reshuffle-limit = Số lần được xóc lại ống: { $count }
rb-enter-reshuffle-limit = Nhập số lần được xóc lại ống (0 để tắt, tối đa 100):
rb-option-changed-reshuffle-limit = Số lần xóc lại ống đã được đặt là { $count }.

rb-set-reshuffle-penalty = Điểm phạt khi xóc lại ống: { $points }
rb-enter-reshuffle-penalty = Nhập điểm phạt khi xóc lại ống (từ 0 đến 5):
rb-option-changed-reshuffle-penalty = Điểm phạt xóc lại ống đã được đặt là { $points }.

rb-set-ball-pack = Bộ bóng: { $pack }
rb-select-ball-pack = Chọn chủ đề bộ bóng muốn chơi:
rb-option-changed-ball-pack = Bộ bóng đã được đặt là { $pack }.

# Lý do hành động bị vô hiệu hóa
rb-not-enough-balls = Không còn đủ bóng trong ống.
rb-no-reshuffles-left = Bạn đã hết quyền xóc lại ống.
rb-already-reshuffled = Bạn đã xóc lại ống trong lượt này rồi.
rb-no-views-left = Bạn đã hết quyền xem trộm ống.

# Các mục trong Bộ bóng
rb-pack-all = Trộn lẫn các bộ bóng
rb-pack-international = Du lịch Quốc tế
rb-ball-paris-pickpocket = Bị móc túi ở Paris
rb-ball-lost-luggage-in-london = Thất lạc hành lý ở London
rb-ball-tokyo-train-delay = Tàu cao tốc Tokyo bị trễ
rb-ball-sahara-sandstorm = Bão cát Sahara
rb-ball-venice-flood = Triều cường ngập Venice
rb-ball-new-york-traffic = Kẹt xe ở New York
rb-ball-amazon-mosquito-swarm = Đàn muỗi Amazon tấn công
rb-ball-berlin-club-rejected = Bị bảo kê quán bar Berlin đuổi
rb-ball-spilled-coffee-in-rome = Đổ cà phê ở Rome
rb-ball-sydney-sunburn = Cháy nắng ở Sydney
rb-ball-istanbul-bazaar-scam = Bị chém đẹp ở chợ Istanbul
rb-ball-moscow-blizzard = Bão tuyết Moscow
rb-ball-dubai-heatwave = Nắng nóng vỡ đầu ở Dubai
rb-ball-mexico-city-smog = Bụi mịn Mexico City
rb-ball-cairo-camel-spit = Lạc đà Cairo phun nước bọt
rb-ball-athens-ruins-trip = Trượt chân ngã ở tàn tích Athens
rb-ball-rio-carnival-hangover = Say bí tỉ ở Lễ hội Rio
rb-ball-bali-belly = Tào tháo rượt ở Bali
rb-ball-swiss-alps-avalanche = Lở tuyết trên dãy Alps
rb-ball-amsterdam-bicycle-crash = Tai nạn xe đạp ở Amsterdam
rb-ball-bangkok-tuk-tuk-breakdown = Xe Tuk-Tuk xịt lốp ở Bangkok
rb-ball-iceland-volcano-ash = Tro bụi núi lửa Iceland
rb-ball-cape-town-wind = Gió thổi bay người ở Cape Town
rb-ball-neutral-passport = Hộ chiếu bình thường
rb-ball-airport-layover = Vật vờ chờ quá cảnh
rb-ball-hotel-lobby = Ngồi chờ ở sảnh khách sạn
rb-ball-tourist-map = Bản đồ du lịch
rb-ball-souvenir-magnet = Nam châm gắn tủ lạnh
rb-ball-free-museum-day = Ngày tham quan bảo tàng miễn phí
rb-ball-street-food-snack = Ăn vặt lề đường
rb-ball-post-card-home = Gửi bưu thiếp về nhà
rb-ball-friendly-local = Dân địa phương thân thiện
rb-ball-sunny-day = Một ngày nắng đẹp
rb-ball-eiffel-tower-view = Ngắm tháp Eiffel
rb-ball-taj-mahal-sunrise = Bình minh ở đền Taj Mahal
rb-ball-great-wall-hike = Leo Vạn Lý Trường Thành
rb-ball-machu-picchu-climb = Chinh phục Machu Picchu
rb-ball-kyoto-cherry-blossoms = Ngắm hoa anh đào ở Kyoto
rb-ball-colosseum-tour = Tham quan Đấu trường La Mã
rb-ball-pyramids-exploration = Khám phá Kim Tự Tháp
rb-ball-santorini-sunset = Hoàng hôn ở Santorini
rb-ball-aurora-borealis = Chiêm ngưỡng Bắc Cực Quang
rb-ball-safari-lion-sighting = Thấy sư tử đi dạo ở Safari
rb-ball-bora-bora-villa = Ở villa xịn tại Bora Bora
rb-ball-maldives-scuba = Lặn biển ngắm san hô Maldives
rb-ball-niagara-falls-boat = Du thuyền qua Thác Niagara
rb-ball-grand-canyon-heli = Đi trực thăng ngắm Grand Canyon
rb-ball-serengeti-migration = Xem cuộc đại di cư ở Serengeti
rb-ball-first-class-upgrade = Được nâng hạng vé máy bay First Class
rb-ball-lottery-in-macau = Trúng độc đắc ở Macau
rb-ball-private-jet = Bao trọn chuyên cơ riêng
rb-ball-royal-palace-invite = Nhận thiệp mời vào Cung điện Hoàng gia
rb-ball-world-tour-ticket = Vé đi vòng quanh thế giới

rb-pack-vietnam = Cuộc phiêu lưu ở Việt Nam
rb-ball-stolen-motorbike = Bị đua mất xe máy
rb-ball-flooded-street-saigon = Bơi giữa đường Sài Gòn mùa mưa
rb-ball-food-poisoning-bun-mam = Đau bụng vì ăn bún mắm
rb-ball-fake-taxi-scam = Đi nhầm taxi dù
rb-ball-typhoon-in-central-vietnam = Bão đổ bộ miền Trung
rb-ball-lost-wallet-ben-thanh = Rơi ví ở chợ Bến Thành
rb-ball-traffic-jam-hanoi = Kẹt xe cứng ngắc ở Hà Nội
rb-ball-pickpocketed-in-bui-vien = Bị rạch túi ở phố Tây Bùi Viện
rb-ball-spilled-pho = Lỡ tay đổ tô phở
rb-ball-overcharged-for-coffee = Mua cà phê bị chặt chém
rb-ball-sunburn-in-mui-ne = Cháy đen thui ở Mũi Né
rb-ball-missed-train-to-sapa = Trễ chuyến tàu đi Sapa
rb-ball-loud-karaoke-next-door = Hàng xóm hát loa kẹo kéo lúc nửa đêm
rb-ball-broken-flip-flop = Đứt quai dép tổ ong
rb-ball-sudden-downpour = Mưa rào vỡ đầu
rb-ball-dog-chased-you = Bị chó rượt chạy trối chết
rb-ball-bitten-by-mosquitoes = Muỗi chích sưng vù
rb-ball-out-of-gas = Dắt bộ vì hết xăng
rb-ball-spicy-chili-bite = Cắn nhầm quả ớt hiểm
rb-ball-delayed-flight = Chuyến bay bị delay (chuyện thường ở huyện)
rb-ball-wifi-disconnected = Rớt mạng Wi-Fi
rb-ball-forgot-umbrella = Quên mang áo mưa
rb-ball-minor-scratch = Quẹt xe xước nhẹ
rb-ball-plastic-stool = Ngồi ghế nhựa chém gió
rb-ball-iced-tea-tra-da = Trà đá vỉa hè
rb-ball-waiting-for-green-light = Chờ đèn đỏ 99 giây
rb-ball-bamboo-hat = Đội nón lá
rb-ball-motorbike-helmet = Đội mũ bảo hiểm
rb-ball-tasty-banh-mi = Cắn ổ bánh mì giòn rụm
rb-ball-free-sugar-cane-juice = Được cô bán nước mía bao
rb-ball-friendly-street-vendor = Chú bán hàng rong thân thiện
rb-ball-cool-breeze = Gió thổi mát rượi
rb-ball-found-10k-vnd = Nhặt được tờ 10 cành
rb-ball-delicious-pho-bowl = Húp trọn tô phở đặc biệt
rb-ball-egg-coffee-in-hanoi = Thưởng thức cà phê trứng Hà Nội
rb-ball-boat-ride-in-ninh-binh = Ngồi đò ngắm cảnh Tràng An - Ninh Bình
rb-ball-lantern-festival-hoian = Thả hoa đăng ở Hội An
rb-ball-motorbike-road-trip = Đi phượt bằng xe máy
rb-ball-ha-long-bay-cruise = Lên du thuyền Vịnh Hạ Long
rb-ball-golden-bridge-bana-hills = Check-in Cầu Vàng Bà Nà Hills
rb-ball-phu-quoc-sunset = Ngắm hoàng hôn Phú Quốc
rb-ball-sapa-terraced-fields = Săn mây ở ruộng bậc thang Sapa
rb-ball-phong-nha-cave-exploration = Khám phá hang động Phong Nha
rb-ball-tet-holiday-lucky-money = Được lì xì ngày Tết
rb-ball-vip-ticket-to-concert = Có vé VIP xem concert idol
rb-ball-luxury-resort-stay = Nghỉ dưỡng ở resort 5 sao
rb-ball-business-class-flight = Bay khoang thương gia
rb-ball-won-lottery-vietlott = Trúng độc đắc Vietlott
rb-ball-billionaire-inheritance = Được tỷ phú thừa kế tài sản
rb-ball-found-gold-treasure = Đào được hũ vàng
rb-ball-free-house-in-district-1 = Trúng nhà mặt tiền Quận 1
rb-ball-national-hero-award = Nhận huân chương anh hùng
rb-ball-ultimate-happiness = Hạnh phúc viên mãn
