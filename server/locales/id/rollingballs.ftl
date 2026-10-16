game-name-rollingballs = Bola Bergulir
rb-take = Ambil { $count } { $count ->
    [one] bola
   *[other] bola
}
rb-reshuffle-action = Acak bagian depan pipa, tersisa { $remaining } kali
rb-view-pipe-action = Intip isi pipa, tersisa { $remaining } kali
rb-check-pipe-status = Periksa status pipa
rb-key-reshuffle-pipe = Acak bagian depan pipa
rb-key-view-pipe = Intip isi pipa
rb-you-take = Anda memilih mengambil { $count } { $count ->
    [one] bola
   *[other] bola
} dari bagian depan pipa yang berisi { $remaining } bola.
rb-player-takes = { $player } memilih mengambil { $count } { $count ->
    [one] bola
   *[other] bola
} dari bagian depan pipa yang berisi { $remaining } bola.
rb-you-take-brief = Anda mengambil { $count } { $count ->
    [one] bola
   *[other] bola
}.
rb-player-takes-brief = { $player } mengambil { $count } { $count ->
    [one] bola
   *[other] bola
}.
rb-you-forced-take = Hanya tersisa { $count } { $count ->
    [one] bola
   *[other] bola
}, kurang dari batas minimum { $minimum }. Anda harus mengambil semuanya.
rb-player-forced-takes = Hanya tersisa { $count } { $count ->
    [one] bola
   *[other] bola
}, kurang dari batas minimum { $minimum }. { $player } harus mengambil semuanya.
rb-you-forced-take-brief = Anda harus mengambil { $count } { $count ->
    [one] bola
   *[other] bola
} terakhir.
rb-player-forced-takes-brief = { $player } harus mengambil { $count } { $count ->
    [one] bola
   *[other] bola
} terakhir.
rb-your-ball-plus = Bola Anda nomor { $num }: { $description }. Bertambah { $value } { $value ->
    [one] poin
   *[other] poin
}.
rb-player-ball-plus = Bola { $player } nomor { $num }: { $description }. Bertambah { $value } { $value ->
    [one] poin
   *[other] poin
}.
rb-your-ball-minus = Bola Anda nomor { $num }: { $description }. Berkurang { $value } { $value ->
    [one] poin
   *[other] poin
}.
rb-player-ball-minus = Bola { $player } nomor { $num }: { $description }. Berkurang { $value } { $value ->
    [one] poin
   *[other] poin
}.
rb-your-ball-zero = Bola Anda nomor { $num }: { $description }. Skor tidak berubah.
rb-player-ball-zero = Bola { $player } nomor { $num }: { $description }. Skor tidak berubah.
rb-your-draw-summary = Total nilai { $count } bola yang Anda ambil adalah { $delta } poin. Skor Anda kini { $score }. Tersisa { $remaining } bola di dalam pipa.
rb-player-draw-summary = Total nilai { $count } bola yang diambil { $player } adalah { $delta } poin. Skor { $player } kini { $score }. Tersisa { $remaining } bola di dalam pipa.
rb-your-draw-summary-brief = Total perubahan { $delta }, skor Anda { $score }. Tersisa { $remaining } bola.
rb-player-draw-summary-brief = { $player }: total perubahan { $delta }, skor { $score }. Tersisa { $remaining } bola.
rb-your-score-legacy = Skor Anda kini { $score }. Tersisa { $remaining } bola di dalam pipa.
rb-player-score-legacy = Skor { $player } kini { $score }. Tersisa { $remaining } bola di dalam pipa.
rb-you-reshuffle = Anda mengacak { $count } bola terdepan. { $penalty ->
    [0] Tidak ada penalti
   *[other] Skor Anda dikurangi { $penalty } poin sebagai penalti
}. Skor Anda kini { $score }, dan Anda masih bisa mengacak { $remaining } kali.
rb-player-reshuffles = { $player } mengacak { $count } bola terdepan. { $penalty ->
    [0] Tidak ada penalti
   *[other] Skor { $player } dikurangi { $penalty } poin sebagai penalti
}. Skornya kini { $score }, dan pemain ini masih bisa mengacak { $remaining } kali.
rb-you-reshuffle-brief = Anda mengacak { $count } bola. Penalti { $penalty }, skor { $score }, tersisa { $remaining } kali.
rb-player-reshuffles-brief = { $player } mengacak { $count } bola. Penalti { $penalty }, skor { $score }, tersisa { $remaining } kali.
rb-view-pipe-header = Menampilkan { $shown } bola berikutnya dari { $total } bola. Anda masih punya { $remaining } kesempatan mengintip.
rb-view-pipe-ball = { $num }: { $description }. Nilai: { $value } poin.
rb-status-pipe = Ronde { $round }. Tersisa { $count } bola di dalam pipa.
rb-status-take-range = Setiap giliran biasa harus mengambil { $min } hingga { $max } bola.
rb-status-turn = Giliran saat ini: { $player }.
rb-status-resources = Anda masih punya { $views } kesempatan mengintip dan { $reshuffles } kesempatan mengacak.
rb-pipe-filled = Pipa telah diisi dengan { $count } bola berbeda dari set: { $packs }.
rb-round-start = Ronde { $round } dimulai. Tersisa { $count } bola di dalam pipa.
rb-round-start-brief = Ronde { $round }, tersisa { $count } bola.
rb-pipe-empty = Pipa sudah kosong.
rb-winner = { $player } menang dengan { $score } poin.
rb-you-win = Anda menang dengan { $score } poin.
rb-you-tie = Anda berbagi kemenangan dengan { $players }. Masing-masing memperoleh { $score } poin.
rb-tie = { $players } berbagi kemenangan dengan { $score } poin.
rb-line-format = { $rank }. { $player }: { $points }
rb-set-min-take = Minimum bola per giliran: { $count }
rb-enter-min-take = Masukkan minimum bola per giliran, dari 1 hingga 5:
rb-option-changed-min-take = Minimum bola per giliran diatur menjadi { $count }.
rollingballs-desc-min-take = Jumlah minimum bola yang harus diambil pemain setiap giliran. Nilai bawaan 1, rentang 1 hingga 5.
rb-set-max-take = Maksimum bola per giliran: { $count }
rb-enter-max-take = Masukkan maksimum bola per giliran, dari 1 hingga 5:
rb-option-changed-max-take = Maksimum bola per giliran diatur menjadi { $count }.
rollingballs-desc-max-take = Jumlah maksimum bola yang boleh diambil pemain setiap giliran. Permainan tidak dapat dimulai jika nilainya lebih rendah daripada minimum. Nilai bawaan 3, rentang 1 hingga 5.
rb-set-view-pipe-limit = Kesempatan mengintip per pemain: { $count }
rb-enter-view-pipe-limit = Masukkan kesempatan mengintip per pemain, dari 0 hingga 100. Nilai 0 menonaktifkan fitur ini:
rb-option-changed-view-pipe-limit = Kesempatan mengintip per pemain diatur menjadi { $count }.
rollingballs-desc-view-pipe-limit = Banyaknya kesempatan setiap pemain untuk mengintip isi pipa. Membuka kembali hasil yang belum berubah tidak mengurangi kesempatan. Nilai 0 menonaktifkan fitur mengintip. Nilai bawaan 5, rentang 0 hingga 100.
rb-set-reshuffle-limit = Kesempatan mengacak per pemain: { $count }
rb-enter-reshuffle-limit = Masukkan kesempatan mengacak per pemain, dari 0 hingga 100. Nilai 0 menonaktifkan fitur mengacak:
rb-option-changed-reshuffle-limit = Kesempatan mengacak per pemain diatur menjadi { $count }.
rollingballs-desc-reshuffle-limit = Banyaknya kesempatan mengacak yang tersedia sebelum pipa kosong. Nilai bawaan 3, rentang 0 hingga 100.
rb-set-reshuffle-penalty = Penalti mengacak: { $points } poin
rb-enter-reshuffle-penalty = Masukkan penalti mengacak, dari 0 hingga 5 poin:
rb-option-changed-reshuffle-penalty = Penalti mengacak diatur menjadi { $points } poin.
rollingballs-desc-reshuffle-penalty = Poin yang dikurangi saat pemain mengacak bola. Opsi ini hanya muncul jika fitur mengacak tersedia. Nilai bawaan 1, rentang 0 hingga 5.
rb-set-ball-packs = Set bola, { $count } dari { $total } dipilih
rb-option-changed-ball-packs = Pilihan set bola diubah.
rollingballs-desc-ball-packs = Pilih set bola bertema yang dimasukkan ke dalam pipa. Setidaknya satu set harus dipilih.
rb-draw-resolving = Tunggu sampai pengambilan bola { $player } selesai sebelum melakukan tindakan lain pada pipa.
rb-take-not-your-turn = Anda tidak bisa mengambil { $count } bola sekarang karena giliran { $player }.
rb-take-outside-range = Anda mencoba mengambil { $count } bola, tetapi permainan ini hanya mengizinkan { $min } hingga { $max } bola per giliran biasa.
rb-not-enough-balls = Anda mencoba mengambil { $count } bola, tetapi hanya tersisa { $remaining } bola di dalam pipa.
rb-reshuffle-not-your-turn = Anda tidak bisa mengacak sekarang karena giliran { $player }.
rb-no-reshuffles-left = Anda sudah memakai seluruh { $limit } kesempatan mengacak dalam permainan ini.
rb-already-reshuffled = Anda sudah mengacak pada giliran ini. Ambil bola untuk menyelesaikan giliran.
rb-not-enough-balls-to-reshuffle = Mengacak memerlukan setidaknya { $required } bola, tetapi hanya tersisa { $remaining }. Silakan ambil bola.
rb-no-views-left = Isi pipa sudah berubah, dan seluruh { $limit } kesempatan mengintip isi baru sudah Anda gunakan. Anda masih dapat membuka kembali hasil intipan yang sama selama isi pipa belum berubah.
rb-error-min-take-invalid = Minimum pengambilan saat ini { $count }. Nilainya harus dari { $min } hingga { $max }.
rb-error-max-take-invalid = Maksimum pengambilan saat ini { $count }. Nilainya harus dari { $min } hingga { $max }.
rb-error-take-range-conflict = Minimum pengambilan { $min } lebih tinggi daripada maksimum { $max }. Turunkan minimum atau naikkan maksimum sebelum memulai.
rb-error-view-limit-invalid = Batas kesempatan mengintip saat ini { $count }. Nilainya harus dari { $min } hingga { $max }.
rb-error-reshuffle-limit-invalid = Batas kesempatan mengacak saat ini { $count }. Nilainya harus dari { $min } hingga { $max }.
rb-error-reshuffle-penalty-invalid = Penalti mengacak saat ini { $points }. Nilainya harus dari { $min } hingga { $max } poin.
rb-error-no-ball-packs = Pilih setidaknya satu set bola sebelum memulai Bola Bergulir.
rb-error-invalid-ball-packs = Pilihan memuat { $count } { $count ->
    [one] set bola
   *[other] set bola
} yang tidak tersedia. Hapus set yang tidak tersedia sebelum memulai.
rb-pack-international = Keliling Dunia
rb-pack-vietnam = Menjelajahi Vietnam
rb-ball-paris-pickpocket = Paspor dan dompet dicuri di luar negeri
rb-ball-lost-luggage-in-london = Harus mencari pertolongan medis darurat di luar negeri
rb-ball-tokyo-train-delay = Ketinggalan penerbangan internasional lanjutan yang terakhir
rb-ball-sahara-sandstorm = Dievakuasi akibat cuaca buruk
rb-ball-passport-lost-before-flight = Paspor hilang sebelum keberangkatan
rb-ball-venice-flood = Penginapan tutup akibat banjir
rb-ball-new-york-traffic = Penerbangan malam dibatalkan
rb-ball-amazon-mosquito-swarm = Bagasi penting terkirim ke negara yang salah
rb-ball-berlin-club-rejected = Reservasi hotel tidak ditemukan saat check-in
rb-ball-hotel-booking-vanished = Rute pegunungan ditutup selama beberapa hari
rb-ball-spilled-coffee-in-rome = Ponsel retak saat berpindah kendaraan
rb-ball-sydney-sunburn = Wisata sehari batal akibat kelelahan karena panas
rb-ball-istanbul-bazaar-scam = Tur yang sudah dibayar gagal terlaksana
rb-ball-moscow-blizzard = Kereta tidak bisa melanjutkan perjalanan akibat badai salju
rb-ball-dubai-heatwave = Kendaraan sewaan mogok
rb-ball-mexico-city-smog = Rencana perjalanan berubah karena kualitas udara buruk
rb-ball-cairo-camel-spit = Mabuk kendaraan dalam perjalanan jauh
rb-ball-athens-ruins-trip = Pergelangan kaki terkilir saat tur jalan kaki
rb-ball-rio-carnival-hangover = Ketiduran dan ketinggalan tur pagi
rb-ball-bali-belly = Sakit perut membuat rencana sore hari batal
rb-ball-swiss-alps-avalanche = Jalur berpemandangan indah ditutup demi keselamatan
rb-ball-amsterdam-bicycle-crash = Ban sepeda kempes
rb-ball-bangkok-tuk-tuk-breakdown = Tuk-tuk mogok di tengah kemacetan
rb-ball-iceland-volcano-ash = Penerbangan tertunda akibat peringatan cuaca
rb-ball-cape-town-wind = Tempat menikmati pemandangan ditutup akibat angin kencang
rb-ball-neutral-passport = Cap baru di paspor
rb-ball-airport-layover = Transit dengan tenang di bandara
rb-ball-hotel-lobby = Menunggu di lobi hotel
rb-ball-tourist-map = Membentangkan peta kota
rb-ball-souvenir-magnet = Memilih magnet suvenir
rb-ball-free-museum-day = Masuk museum gratis
rb-ball-street-food-snack = Jajanan kaki lima yang lezat
rb-ball-post-card-home = Mengirim kartu pos ke rumah
rb-ball-friendly-local = Penduduk setempat membantu menunjukkan arah
rb-ball-sunny-day = Cuaca sempurna untuk menjelajah
rb-ball-eiffel-tower-view = Pemandangan kota Paris dari Menara Eiffel
rb-ball-taj-mahal-sunrise = Matahari terbit di Taj Mahal
rb-ball-great-wall-hike = Menyusuri Tembok Besar Tiongkok
rb-ball-machu-picchu-climb = Pagi hari di Machu Picchu
rb-ball-kyoto-cherry-blossoms = Bunga sakura di Kyoto
rb-ball-colosseum-tour = Mengunjungi Colosseum bersama pemandu
rb-ball-pyramids-exploration = Menjelajahi kompleks piramida Giza
rb-ball-santorini-sunset = Matahari terbenam di Santorini
rb-ball-aurora-borealis = Aurora borealis di langit
rb-ball-safari-lion-sighting = Mengamati satwa liar dalam safari yang bertanggung jawab
rb-ball-bora-bora-villa = Menginap di tepi laguna Bora Bora
rb-ball-maldives-scuba = Menyelam di terumbu karang Maladewa
rb-ball-niagara-falls-boat = Naik perahu di Air Terjun Niagara
rb-ball-grand-canyon-heli = Menikmati pemandangan Grand Canyon dari udara
rb-ball-serengeti-migration = Migrasi Besar di Serengeti
rb-ball-first-class-upgrade = Mendapat kejutan naik ke kelas satu
rb-ball-lottery-in-macau = Memenangkan pas kereta untuk setahun
rb-ball-private-jet = Pelayaran antarpulau yang hanya terjadi sekali seumur hidup
rb-ball-royal-palace-invite = Kunjungan pribadi ke museum setelah jam tutup
rb-ball-world-tour-ticket = Tiket keliling dunia
rb-ball-stolen-motorbike = Paspor dan dompet dicuri saat perjalanan
rb-ball-flooded-street-saigon = Harus pindah tempat segera akibat banjir
rb-ball-food-poisoning-bun-mam = Keadaan darurat medis mengganggu perjalanan
rb-ball-fake-taxi-scam = Kendaraan mogok sehingga ketinggalan pesawat
rb-ball-passport-lost-at-airport = Paspor hilang di bandara
rb-ball-typhoon-in-central-vietnam = Dievakuasi akibat topan di pesisir Vietnam tengah
rb-ball-lost-wallet-ben-thanh = Bagasi penting hilang saat transit
rb-ball-traffic-jam-hanoi = Kereta malam dibatalkan
rb-ball-pickpocketed-in-bui-vien = Ponsel dicuri di kawasan yang ramai
rb-ball-mountain-road-landslide = Jalan pegunungan ditutup akibat longsor
rb-ball-spilled-pho = Kamera rusak akibat hujan mendadak
rb-ball-overcharged-for-coffee = Reservasi hotel tertukar
rb-ball-sunburn-in-mui-ne = Kelelahan akibat panas di Mui Ne
rb-ball-missed-train-to-sapa = Ketinggalan kereta malam ke Lao Cai
rb-ball-loud-karaoke-next-door = Tidak bisa tidur semalaman sebelum berangkat pagi
rb-ball-broken-flip-flop = Tali sandal putus saat tur jalan kaki
rb-ball-sudden-downpour = Hujan tropis deras yang mendadak
rb-ball-dog-chased-you = Salah turun di halte yang jauh dari hotel
rb-ball-bitten-by-mosquitoes = Digigit nyamuk sepanjang sore
rb-ball-out-of-gas = Sepeda motor kehabisan bahan bakar
rb-ball-spicy-chili-bite = Cabai yang ternyata sangat pedas
rb-ball-delayed-flight = Penerbangan domestik tertunda sebentar
rb-ball-wifi-disconnected = Sinyal lemah di pegunungan
rb-ball-forgot-umbrella = Jas hujan tertinggal di hotel
rb-ball-minor-scratch = Salah belok di kawasan Kota Tua
rb-ball-plastic-stool = Duduk di bangku kecil di trotoar
rb-ball-iced-tea-tra-da = Segelas es teh tra da
rb-ball-waiting-for-green-light = Menunggu lama sampai lampu merah berganti
rb-ball-bamboo-hat = Mencoba topi kerucut non la
rb-ball-motorbike-helmet = Mengencangkan tali helm sepeda motor
rb-ball-tasty-banh-mi = Sarapan roti banh mi yang renyah
rb-ball-free-sugar-cane-juice = Sari tebu segar
rb-ball-friendly-street-vendor = Sambutan hangat pedagang pasar
rb-ball-cool-breeze = Angin sejuk setelah hujan
rb-ball-found-10k-vnd = Naik bus lokal dengan tarif murah
rb-ball-delicious-pho-bowl = Semangkuk pho yang harum
rb-ball-egg-coffee-in-hanoi = Kopi telur di Hanoi
rb-ball-boat-ride-in-ninh-binh = Menyusuri Kompleks Lanskap Trang An dengan sampan
rb-ball-lantern-festival-hoian = Malam diterangi lentera di Kota Kuno Hoi An
rb-ball-motorbike-road-trip = Naik perahu menyusuri kebun buah di Delta Mekong
rb-ball-ha-long-bay-cruise = Berlayar melintasi Teluk Ha Long dan Kepulauan Cat Ba
rb-ball-golden-bridge-bana-hills = Jembatan Emas di atas Perbukitan Ba Na
rb-ball-phu-quoc-sunset = Matahari terbenam di Phu Quoc
rb-ball-sapa-terraced-fields = Sawah berundak di sekitar Sa Pa
rb-ball-phong-nha-cave-exploration = Menjelajahi gua di Phong Nha - Ke Bang
rb-ball-tet-holiday-lucky-money = Berkumpul saat Tet dan menerima angpau
rb-ball-vip-ticket-to-concert = Matahari terbit di jalur melingkar Ha Giang
rb-ball-luxury-resort-stay = Mengunjungi kegiatan konservasi masyarakat di Con Dao
rb-ball-business-class-flight = Menikmati pemandangan dari tempat tidur kereta Reunification Express
rb-ball-won-lottery-vietlott = Malam festival di antara monumen Hue
rb-ball-billionaire-inheritance = Ekspedisi Son Doong
rb-ball-found-gold-treasure = Lokakarya budaya pribadi bersama perajin ahli
rb-ball-free-house-in-district-1 = Menjelajahi Vietnam dengan kereta selama sebulan
rb-ball-national-hero-award = Menjadi tamu kehormatan di festival desa
rb-ball-ultimate-happiness = Perjalanan impian dari Ha Giang ke Ca Mau
