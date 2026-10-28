game-name-lastoutpost = Last Outpost
lo-root-vitals = HP { $hp }/{ $maximum }; AP { $ap }; { $item }.
lo-root-spectator = Menonton Last Outpost.
lo-menu-attack = Serang
lo-menu-move = Bergerak
lo-menu-equipment = Senjata dan isi ulang
lo-menu-support = Bantuan dan kargo
lo-menu-interact = Sasaran dan lingkungan sekitar
lo-menu-supplies = Perbekalan dan peningkatan
lo-menu-back = Kembali ke menu utama
lo-menu-available = { $menu }; Tersedia
lo-menu-equipment-state = { lo-menu-equipment }: { $weapon }; terisi { $loaded }, cadangan { $reserve }.
lo-shop-balance = Kredit: { $credits }.
lo-shop-done = Tutup toko
lo-help-shop-done = Tutup toko tanpa mengakhiri giliran. E atau X juga menutupnya.
lo-key-finish-or-end = Siap, tutup toko, atau akhiri giliran
lo-menu-close-information = Tutup panel informasi terlebih dahulu.
lo-help-menu-attack = Pilih sasaran senjata api, pisau, atau granat.
lo-help-menu-move = Rute terbuka, biaya pergerakan, dan penghuni tujuan.
lo-help-menu-equipment = Isi ulang atau ganti senjata. Mengganti senjata tidak membutuhkan AP.
lo-help-menu-support = { $party_size ->
    [1] Obati diri sendiri atau letakkan kargo.
   *[other] Obati, bangkitkan, atau serahkan kargo.
    }
lo-help-menu-interact = Pulihkan listrik dan radio, buka gerbang, atau perbaiki barikade.
lo-help-menu-supplies = Beli perbekalan dan peningkatan. Toko tetap terbuka setelah pembelian. X untuk kembali.
lo-help-menu-back = Kembali ke tombol kategori Anda di menu utama.
lo-empty-attack = Tidak ada sasaran yang tersedia.
lo-empty-move = Tidak ada rute terbuka.
lo-empty-equipment = Tidak ada tindakan senjata yang tersedia.
lo-empty-preparation = Tidak tersedia selama persiapan.
lo-empty-support = Tidak ada tindakan bantuan atau kargo yang tersedia.
lo-empty-interact = Tidak ada interaksi yang tersedia.
lo-empty-supplies = Tidak ada perbekalan yang tersedia di sini.
lo-move-location = { $zone }. { $description }
lo-destination = { $party_size ->
    [1] { $zone }; { $ap } AP. Musuh: { $inside } di dalam, { $outside } di luar. { $barricade }
   *[other] { $zone }; { $ap } AP. Zombi: { $inside } di dalam, { $outside } di luar. Regu: { $survivors }. { $barricade }
    }
lo-destination-survivor = { $name } ({ $condition })
lo-destination-barricade = Pintu masuk musuh; kekuatan barikade { $strength }.
lo-enemies = Periksa musuh
lo-help-enemies = Sasaran dalam jangkauan ditampilkan lebih dulu, lalu musuh yang lebih jauh dan bala bantuan. Anda tetap harus menunggu giliran serta memiliki AP dan amunisi untuk menyerang.
lo-enemies-context = Sasaran dari { $zone }.
lo-enemies-spectator-context = Gambaran dari { $zone }.
lo-enemies-empty = Tidak ada musuh di peta.
lo-enemy-detail = { $pack }. Kesehatan tiap musuh: { $health }. { $distance } { $access }
lo-enemy-distance = Jarak rute: { $count ->
    [one] { $count } penghubung.
   *[other] { $count } penghubung.
    }
lo-enemy-unreachable = Tidak ada rute terbuka.
lo-enemy-barricade = Di balik barikade berkekuatan { $strength }; serangan terhalang.
lo-enemy-reach = Dalam jangkauan: { $actions }.
lo-enemy-reposition = Di luar jangkauan perlengkapan saat ini.
lo-enemy-observe = Tampilan penonton.
lo-health = Periksa kesehatan
lo-help-health = HP dan status penyelamatan saat ini.
lo-health-report = HP { $hp }/{ $maximum }. { $condition }.
lo-health-upright = Berdiri
lo-health-downed = { $party_size ->
    [1] Tumbang
   *[other] Tumbang; selamatkan dalam { $phases } fase gerombolan
    }
lo-health-awaiting-recovery = Menunggu pemulihan gelombang
lo-slot-primary = Gunakan senjata utama
lo-slot-sidearm = Gunakan pistol
lo-error-slot-empty = Tidak ada senjata utama yang terpasang.
lo-error-preparation = Tindakan tempur tidak tersedia selama persiapan.
lo-option-voices = Dialog karakter: { $enabled }
lo-change-voices = Dialog karakter diatur menjadi { $enabled }.
lo-desc-voices = Dialog karakter berbahasa Inggris, termasuk bahasa kasar. Laporan taktis menggunakan bahasa pilihan Anda.
lo-you = Anda
lo-team = { $party_size ->
    [1] Penyintas
   *[other] Tim
    }
lo-none = Tidak ada
lo-yes = Ya
lo-no = Tidak
lo-inside = di dalam
lo-outside = di luar barikade
lo-message = { $text }
lo-term-none = { lo-none }
lo-term-courtyard = Halaman
lo-term-gatehouse = Pos Gerbang
lo-term-workshop = Bengkel
lo-term-infirmary = Ruang Perawatan
lo-term-loading = Area Bongkar Muat
lo-term-generator = Ruang Generator
lo-term-pump = Aula Pompa
lo-term-roof = Atap Radio
lo-term-walker = { $count ->
    [one] Pejalan
   *[other] Pejalan
    }
lo-term-hound = { $count ->
    [one] Anjing Pemburu
   *[other] Anjing Pemburu
    }
lo-term-brute = { $count ->
    [one] Raksasa
   *[other] Raksasa
    }
lo-term-pistol = Pistol M1911
lo-term-rifle = Senapan AK
lo-term-shotgun = Senapan gentel
lo-term-marksman = Senapan penembak jitu
lo-term-knife = Pisau
lo-term-medkit = Perlengkapan medis
lo-term-grenade = Granat
lo-term-endurance = Daya Tahan
lo-term-medic = Medis Lapangan
lo-term-quickhands = Tangan Cepat
lo-term-combat = Fase penyintas
lo-term-resolving = Tindakan sedang berlangsung
lo-term-reloading = Mengisi ulang
lo-term-prep = Persiapan
lo-term-finished = Selesai
lo-term-dempsey = Dempsey
lo-term-nikolai = Nikolai
lo-term-takeo = Takeo
lo-term-richtofen = Richtofen
lo-term-victory = { $party_size ->
    [1] Berhasil bertahan hidup
   *[other] Regu berhasil bertahan hidup
    }
lo-term-objectives = Radio atau listrik belum selesai dipulihkan
lo-term-overwhelmed = { $party_size ->
    [1] Kewalahan
   *[other] Tim kewalahan
    }
lo-term-overrun = Batas waktu gelombang tercapai
lo-turn-resolving = { lo-error-resolving }
lo-turn-prep = { $survivor_count ->
    [1] Persiapan. Pilih Siap untuk memulai gelombang berikutnya.
   *[other] Persiapan. Gelombang berikutnya dimulai saat semua siap.
    }
lo-map = Peta dan kelompok musuh
lo-forecast = Perkiraan gerombolan berikutnya
lo-inventory = Perlengkapan dan perbekalan
lo-help-map = Rute, barikade, kelompok musuh, dan jadwal kedatangan. Arah hadap audio adalah utara.
lo-help-forecast = Fase gerombolan berikutnya jika tidak ada tindakan lagi.
lo-help-inventory = Kredit, senjata, dan perbekalan Anda, serta suku cadang untuk perbaikan dan sasaran.
lo-header = Gelombang { $wave }; siklus { $cycle }/{ $limit }. { $phase }. { $zone }. HP { $hp }; AP { $ap }; kredit { $credits }; suku cadang { $parts }.
lo-spectator-header = Menonton. Gelombang { $wave }; siklus { $cycle }. { $phase }; suku cadang { $parts }.
lo-objectives = Sasaran
lo-survivor = { $name } ({ $character }): { $zone }; kesehatan { $hp }/{ $maximum }; AP { $ap }. { $condition }; siap { $ready }; bertahan { $guard }.
lo-zone = { $zone }: { $description } Rute terbuka: { $links }. Musuh: { $enemies }. { $barrier } Slot kontak jarak dekat: { $frontage }.
lo-pack = { $count } { $kind }, { $zone }, { $side }; kesehatan gabungan { $hp }
lo-incoming = { $zone }: { $count } bala bantuan setelah fase gerombolan { $cycle }; tindakan pertama pada fase { $first }.
lo-forecast-caveat = Mengasumsikan tidak ada tindakan lagi. Raksasa menggunakan dua slot kontak; musuh lain satu. Musuh yang berdesakan tetap mengganggu sasaran. Membaca tidak menghabiskan waktu.
lo-weapon-status = { $name }, { $weapon }: terisi { $ammo }, cadangan { $reserve }; kerusakan { $damage } per sasaran, hingga { $targets } sasaran; jangkauan { $minimum } hingga { $maximum }; digunakan { $equipped }.
lo-kit-status = { $name }: kredit { $credits }; perlengkapan medis { $medkits }, granat { $grenades }; keunggulan { $perks }.
lo-action-label = { $action }: { $detail } ({ $ap } AP)
lo-action-label-simple = { $action } ({ $ap } AP)
lo-reload-detail = { $weapon }; terisi { $loaded }/{ $capacity }, cadangan { $reserve }
lo-attack-detail = { $weapon }, terisi { $ammo }; { $target }
lo-price = { $item }, { $cost } kredit
lo-ammo-price = { $item }, { $amount } peluru cadangan seharga { $cost } kredit
lo-parts-price = { $item }, { $cost } suku cadang
lo-work-price = { $item }, { $done } dari { $total } pekerjaan, membutuhkan { $cost } suku cadang
lo-verb-fire = Tembak
lo-verb-knife = Tusuk
lo-verb-reload = Isi ulang
lo-verb-grenade = Lempar granat
lo-verb-heal = Gunakan perlengkapan medis
lo-verb-revive = Bangkitkan
lo-verb-open = Buka gerbang
lo-verb-repair = Perbaiki barikade
lo-verb-work = Perbaiki peralatan
lo-verb-ammo = Beli amunisi
lo-verb-buy = Beli perlengkapan
lo-verb-perk = Beli keunggulan
lo-verb-upgrade = Tingkatkan senjata utama
lo-verb-equip = Gunakan
lo-verb-ready = Siap untuk gelombang berikutnya
lo-verb-end = Akhiri giliran
lo-help-fire = Mengenai musuh yang paling terluka dalam kelompok terlebih dahulu. Senapan gentel mengenai hingga dua musuh. Barikade melindungi musuh di luar sampai hancur.
lo-help-knife = Kerusakan 1; 1 AP; zona yang sama. Tanpa amunisi.
lo-help-move = 1 AP per penghubung; 2 saat meninggalkan musuh. Kargo menambah 1 AP.
lo-help-reload = 1 AP; memindahkan amunisi cadangan setelah selesai. Anda tetap dapat berjalan. Tangan Cepat membebaskan biaya AP untuk isi ulang pertama setiap gelombang.
lo-help-grenade = { $party_size ->
    [1] Kerusakan 3 pada hingga empat musuh; 1 AP. Zona Anda atau zona bersebelahan yang terlihat. Hanya mengenai musuh di dalam perimeter.
   *[other] Kerusakan 3 pada hingga empat musuh; 1 AP. Zona Anda atau zona bersebelahan yang terlihat. Hanya mengenai musuh di dalam perimeter; tidak melukai rekan.
    }
lo-help-heal = 1 perlengkapan medis dan 1 AP; memulihkan hingga 3 HP penyintas yang berdiri di zona Anda.
lo-help-revive = Bangkitkan dengan 2 HP; 2 AP, atau 1 dengan Medis Lapangan. Zona yang sama. Tanpa giliran tambahan.
lo-help-revive-preview = { lo-help-revive } Tanpa tindakan selanjutnya, { $target } akan memiliki { $health } HP setelah fase gerombolan berikutnya.
lo-gate-link = { $origin } ke { $destination }
lo-gate-service = Gerbang servis
lo-gate-shortcut = Jalan pintas ruang perawatan
lo-gate-roof = Gerbang akses radio
lo-gate-crossing = Penyeberangan barang
lo-gate-bulkhead = Pintu sekat banjir
lo-gate-status = { $gate }: terbuka { $opened }; { $cost } suku cadang; membutuhkan listrik { $power }. Rute: { $routes }. Slot kontak setelah dibuka: { $frontages }.
lo-help-open-routes = { $cost } suku cadang; 1 AP; zona Anda harus bebas musuh. Membuka { $routes } secara permanen untuk kedua pihak. Membutuhkan listrik: { $power }. Slot kontak sesudahnya: { $frontages }.
lo-frontage-site = { $zone }, { $count } slot kontak
lo-gate-opened-routes = Rute baru untuk kedua pihak: { $routes }.
lo-defense-until-clear = Terus pertahankan { $zone } sampai gelombang berakhir; musuh masih dapat merusak relai.
lo-help-repair = 1 suku cadang dan 1 AP; memulihkan 2 kekuatan barikade, hingga 4. Sekali per siklus; zona bebas musuh.
lo-help-work = 1 AP per unit pekerjaan. Unit pertama membayar biaya suku cadang yang tercantum. Zona harus bebas musuh; radio membutuhkan listrik.
lo-help-ammo = Kapasitas cadangan: tiga magasin. Selama pertempuran, beli di pos amunisi yang bebas musuh. Selama persiapan, beli di mana saja.
lo-help-buy = Hanya saat persiapan. Senjata utama menggantikan senjata utama saat ini. Pembelian pertama termasuk amunisi; pembelian ulang mempertahankan amunisi lama. Tanpa pengembalian dana.
lo-help-perk = Membutuhkan listrik; maksimal dua keunggulan. Daya Tahan: +2 HP. Medis Lapangan: bangkitkan dengan 1 AP. Tangan Cepat: isi ulang pertama setiap gelombang tidak membutuhkan AP.
lo-help-upgrade = Membutuhkan listrik; 500 kredit per jenis senjata. Kerusakan: AK 4, senapan gentel 6, senapan penembak jitu 9.
lo-help-equip = Ganti senjata; tanpa biaya AP.
lo-help-ready = { $survivor_count ->
    [1] Mulai gelombang berikutnya.
   *[other] Ubah status kesiapan. Gelombang berikutnya dimulai saat semua siap. Batalkan kesiapan untuk membeli lagi.
    }
lo-help-end = { $party_size ->
    [1] Buang sisa AP. Musuh bertindak berikutnya.
   *[other] Buang sisa AP. Musuh bertindak setelah regu selesai.
    }
lo-error-unavailable = Tidak tersedia pada fase ini.
lo-error-stale = Pilihan itu tidak lagi tersedia.
lo-error-turn = { action-not-your-turn }
lo-error-down = Anda tumbang.
lo-error-ready = Batalkan kesiapan sebelum membeli.
lo-error-ap = AP tidak cukup.
lo-error-range = Sasaran di luar jangkauan tembak atau garis pandang.
lo-error-ammo = Amunisi yang terisi tidak cukup.
lo-error-grenade = Tidak ada granat.
lo-error-medkit = Tidak ada perlengkapan medis.
lo-error-engaged = Singkirkan musuh dari zona ini terlebih dahulu.
lo-error-complete = Sasaran ini sudah selesai.
lo-error-power = Pulihkan listrik terlebih dahulu.
lo-error-parts = Suku cadang tidak cukup.
lo-error-credits = Kredit tidak cukup.
lo-error-equipped = Senjata ini sudah digunakan.
lo-error-resolving = Tindakan saat ini sedang berlangsung.
lo-event-wave = Gelombang { $amount }; { $count } musuh. { $deployment }.
lo-deployment-now = { $count } di luar sekarang
lo-deployment-later = { $count } tiba setelah fase gerombolan { $cycle }
lo-event-final_warning = Gelombang terakhir. Sisa pekerjaan infrastruktur { $amount }; membutuhkan { $count } suku cadang. Selesaikan infrastruktur dan misi sebelum gelombang berakhir.
lo-event-clear = { $party_size ->
    [1] Gelombang { $amount } selesai. +{ $count } kredit; +3 suku cadang. Pulihkan { $healing } HP, atau bangkit dengan { $recovery } HP jika tumbang. Hingga { $ammo } peluru cadangan pistol. Persiapan.
   *[other] Gelombang { $amount } selesai. Setiap penyintas mendapat { $count } kredit dan hingga { $ammo } peluru cadangan pistol. Penyintas yang berdiri memulihkan { $healing } HP; yang tumbang kembali dengan { $recovery } HP. Tim: +3 suku cadang. Persiapan.
    }
lo-event-fire = { $actor } menembakkan { $item } di { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife = { $actor } menyerang dengan pisau di { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade = { $actor } meledakkan granat di { $zone }. { $hits }. { lo-combat-kills }
lo-event-move = { $actor } bergerak dari { $origin } ke { $zone }.
lo-event-reload = { $actor } mengisi { $amount } peluru ke { $item }.
lo-reload-start = { $actor } sedang mengisi ulang.
lo-reload-start-personal = Sedang mengisi ulang.
lo-error-reloading = { lo-reload-start-personal }
lo-event-heal = { $actor } mengobati { $target }; kesehatan kini { $amount }.
lo-event-revive = { $actor } membangkitkan { $target } dengan { $amount } HP.
lo-event-open = { $actor } membuka { $item }; tersisa { $amount } suku cadang. { $routes }
lo-event-repair = { $actor } memperbaiki barikade di { $zone } hingga berkekuatan { $amount }.
lo-event-work = { $count ->
    [1] { $actor } memulihkan { $item } di { $zone }.
   *[0] { $actor } mengerjakan { $item } di { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo = { $actor } membeli { $amount } peluru untuk { $item }, membayar { $count } kredit.
lo-event-buy = { $actor } membeli { $item }; tersisa { $amount } kredit.
lo-event-perk = { $actor } memperoleh { $item }.
lo-event-upgrade = { $actor } meningkatkan { $item }.
lo-event-equip = { $actor } menggunakan { $item }.
lo-event-ready = { $actor } { $amount ->
    [1] siap untuk gelombang berikutnya.
   *[0] belum siap.
    }
lo-event-end = { $actor } mengakhiri gilirannya.
lo-event-barrier = { $zone }: { $count } serangan barikade oleh { $item }; kekuatan kini { $amount }.
lo-event-enter = { $count } { $item } memasuki { $zone }.
lo-event-approach = { $count } { $item } bergerak dari { $origin } ke { $zone }.
lo-event-hurt = { $target }: { $count } serangan oleh { $item }, total kerusakan { $amount } di { $zone }.
lo-event-down = { $target } tumbang di { $zone }. Bangkitkan dalam dua fase gerombolan berikutnya.
lo-event-incapacitated = { $target } tidak dapat bertindak sampai gelombang berikutnya.
lo-event-recovery = { $target }: pemulihan darurat terakhir. HP { $amount }; giliran berikutnya { $count } AP. Kargo tetap di tempatnya tumbang.
lo-event-arrivals = { $count } bala bantuan di luar. Mereka bertindak pada fase gerombolan berikutnya.
lo-event-finish = { $item }. Gelombang selesai: { $amount } dari { $waves }.
lo-result-cycles = Fase gerombolan: { $count }.
lo-error-magazine-full = Magasin senjata yang digunakan sudah penuh.
lo-error-reserve-empty = Tidak ada amunisi cadangan.
lo-error-barrier-full = Barikade ini sudah berkekuatan penuh.
lo-error-already-repaired = Barikade ini sudah diperbaiki pada siklus ini.
lo-error-weapon-owned = Anda sudah membawa senjata utama ini.
lo-error-kit-capacity = Kapasitas perlengkapan medis tercapai.
lo-error-grenade-capacity = Kapasitas granat tercapai.
lo-error-ammo-capacity = Kapasitas amunisi cadangan tercapai.
lo-error-perk-owned = Anda sudah memiliki keunggulan ini.
lo-error-perk-capacity = Batas keunggulan tercapai.
lo-error-no-primary = Beli senjata utama terlebih dahulu.
lo-error-upgraded = Senjata ini sudah ditingkatkan.
lo-event-heal-self = { $actor } menggunakan perlengkapan medis; kesehatan kini { $amount }.
lo-event-heal-self-personal = Anda mengobati diri sendiri; kesehatan kini { $amount }.
lo-event-heal-target = { $actor } mengobati Anda; kesehatan kini { $amount }.
lo-event-revive-target = { $actor } membangkitkan Anda dengan { $amount } HP. Anda bertindak pada siklus berikutnya.
lo-event-hurt-personal = Anda menerima { $count } serangan dari { $item }, total kerusakan { $amount } di { $zone }.
lo-event-down-personal = Anda tumbang di { $zone }. Tim Anda memiliki dua fase gerombolan berikutnya untuk membangkitkan Anda.
lo-event-down-solo-recovery = { $target } tumbang di { $zone }. Pemulihan darurat: { $recovery_seconds } detik setelah fase gerombolan ini.
lo-event-down-solo-recovery-personal = Anda tumbang di { $zone }. Pemulihan darurat: { $recovery_seconds } detik setelah fase gerombolan ini.
lo-event-down-solo-final = { $target } tumbang di { $zone }. Tidak ada penyintas atau pemulihan yang tersisa.
lo-event-down-solo-final-personal = Anda tumbang di { $zone }. Tidak ada penyintas atau pemulihan yang tersisa.
lo-event-incapacitated-personal = Anda tidak dapat bertindak sampai gelombang berikutnya.
lo-event-recovery-personal = Anda menggunakan pemulihan darurat terakhir. HP { $amount }; giliran berikutnya { $count } AP. Kargo tetap di tempat Anda tumbang.
lo-event-fire-personal = Anda menembakkan { $item } di { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife-personal = Anda menyerang dengan pisau di { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade-personal = Anda melempar granat di { $zone }. { $hits }. { lo-combat-kills }
lo-event-move-personal = Anda bergerak dari { $origin } ke { $zone }.
lo-event-reload-personal = Anda mengisi { $amount } peluru ke { $item }.
lo-event-heal-personal = Anda mengobati { $target }; kesehatan kini { $amount }.
lo-event-revive-personal = Anda membangkitkan { $target } dengan { $amount } HP.
lo-event-open-personal = Anda membuka { $item }; tersisa { $amount } suku cadang. { $routes }
lo-event-repair-personal = Anda memperbaiki barikade { $zone } hingga berkekuatan { $amount }.
lo-event-work-personal = { $count ->
    [1] Anda memulihkan { $item } di { $zone }.
   *[0] Anda mengerjakan { $item } di { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo-personal = Anda membeli { $amount } peluru untuk { $item }, membayar { $count } kredit.
lo-event-buy-personal = Anda membeli { $item }; kredit tersisa { $amount }.
lo-event-perk-personal = Anda memperoleh { $item }.
lo-event-upgrade-personal = Anda meningkatkan { $item }.
lo-event-equip-personal = Anda menggunakan { $item }.
lo-event-ready-personal = Anda { $amount ->
    [1] siap untuk gelombang berikutnya.
   *[0] belum siap.
    }
lo-event-end-personal = Anda mengakhiri giliran.
lo-term-horde = musuh
lo-help-move-destination = { $description } { lo-help-move }
lo-zone-description-courtyard = Beton retak mengelilingi tiang bendera kosong di bawah langit terbuka. Bengkel berada di barat, Ruang Perawatan di timur; di selatan, Pos Gerbang menghadap kegelapan di luar perimeter.
lo-zone-description-gatehouse = Di selatan Halaman, atap pos gerbang telah runtuh, menyisakan papan lantai pecah yang terbuka ke langit malam. Kursi penjaga yang kosong menghadap pintu masuk luar, tempat pagar perimeter bertemu jalan.
lo-zone-description-workshop = Noda minyak menyebar di bawah meja kerja terbengkalai, dan karat mengotori dinding pelat logam. Lemari amunisi berdiri di dinding belakang; gerbang servis mengarah ke generator.
lo-zone-description-infirmary = Ranjang sempit berjajar di ruang kayu di timur Halaman. Perban berdebu menggantung dari troli yang terguling, dan cahaya pucat memantul di kaca jendela. Lorong samping mengarah ke Aula Pompa.
lo-zone-description-loading = Lantai baja berkarat membentang melewati tumpukan palet kosong di bawah langit terbuka. Bengkel berada di selatan; di timur, sebuah lorong menuju kelembapan Aula Pompa.
lo-zone-description-generator = Generator pendek dan lebar memenuhi ruang beton di balik gerbang servis Bengkel. Kabel tebal melintasi lantai logam menuju panel listrik yang penuh goresan. Di sinilah listrik pos harus dipulihkan.
lo-zone-description-pump = Air dangkal menutupi lantai di bawah pipa tebal dan katup berkarat. Bekas ketinggian air menodai dinding beton. Lorong Ruang Perawatan bertemu rute dari Area Bongkar Muat di sini.
lo-zone-description-roof = Antena miring menjulang di atas atap beton kosong, dengan kawat penahannya membentang di langit. Radio tersimpan dalam lemari tahan cuaca yang penyok. Gerbang akses bertenaga listrik menjaga jalan masuk dari bawah.
lo-option-map = Peta: { $value }
lo-prompt-map = Pilih peta
lo-change-map = Peta diatur menjadi { $value }.
lo-desc-map = Pos Terbengkalai: garnisun rusak di sekeliling halaman terbuka. Emplasemen: rel sepi di bawah jembatan sempit. Instalasi Banjir: aula mesin yang tergenang dan dipisahkan gerbang berat.
lo-option-mode = Mode: { $value }
lo-prompt-mode = Pilih mode
lo-change-mode = Mode diatur menjadi { $value }.
lo-desc-mode = Operasi: misi dan infrastruktur. Pengepungan: pertahankan keutuhan relai. Penyelamatan Kargo: ambil kembali kargo. Evakuasi Klasik: delapan gelombang, listrik, radio, dan pengiriman perbekalan terakhir.
lo-extraction-route = Gelombang { $wave }: pindahkan perbekalan dari { $pickup } ke { $destination } dalam { $deadline } fase gerombolan. Bersihkan zona pengambilan dan pengiriman. Kargo: +1 AP per gerakan, hanya pistol.
lo-option-difficulty = Kesulitan: { $value }
lo-prompt-difficulty = Pilih kesulitan
lo-change-difficulty = Kesulitan diatur menjadi { $value }.
lo-desc-difficulty = Rekrut: lebih banyak pemulihan dan perbekalan. Standar: gerombolan lebih kuat dan kondisi berubah-ubah. Veteran: tekanan maksimal, pendapatan terbatas, tanpa pemulihan kesehatan atau amunisi pistol gratis setiap gelombang.
lo-error-scenario = Peta, mode, atau kesulitan tidak didukung. Periksa opsi lobi.
lo-event-start = { $map }. { $mode }, { $difficulty }. { $waves } gelombang. Mulai di { $spawn }.
lo-scenario-status = { $map }; { $mode }; { $difficulty }. { $condition }.
lo-mission-status-retrieve = Ambil kargo di { $cargo }; pembawa { $carrier }; kirim ke { $destination }. Tersisa { $remaining } fase gerombolan.
lo-mission-status-relay = Terminal relai: { $zone } dan { $destination }. Tersisa { $remaining } fase gerombolan.
lo-mission-status-hold = Pertahankan { $zone }: { $progress } dari { $total } fase pertahanan. Tersisa { $remaining } fase gerombolan.
lo-mission-help-retrieve = 1 AP untuk mengambil, mengirim, menyerahkan, atau meletakkan. Zona harus bebas musuh kecuali saat meletakkan. Kargo: +1 AP per gerakan, hanya pistol. Kargo jatuh saat Anda tumbang; batas waktunya terus berjalan.
lo-mission-help-relay = { $survivor_count ->
    [1] 1 AP per terminal di zona bebas musuh. Aktifkan kedua lokasi; aktivasi bertahan antarsiklus. Kedua lokasi harus bebas musuh setelah gerombolan bertindak.
   *[other] 1 AP per terminal di zona bebas musuh. Dua penyintas mengaktifkan lokasi berbeda pada siklus yang sama, lalu tetap berdiri di sana selama gerombolan bertindak. Kedua lokasi harus berakhir bebas musuh.
    }
lo-mission-help-hold = Pastikan ada penyintas yang berdiri di lokasi, tanpa musuh di dalam, pada akhir dua fase gerombolan. Lokasi kosong atau yang masih berisi musuh kehilangan satu kemajuan. Dalam Pengepungan, lindungi relai sampai gelombang berakhir; melewati batas waktu mengurangi keutuhannya.
lo-terminal-status = { $zone }: diaktifkan oleh { $actor }.
lo-verb-mission = Interaksi misi
lo-verb-handoff = Serahkan kargo
lo-verb-drop = Letakkan kargo
lo-verb-guard = Bersiap bertahan
lo-help-mission = 1 AP; lakukan tugas yang ditandai di zona bebas musuh.
lo-help-handoff = 1 AP; serahkan kargo kepada rekan yang berdiri di zona bebas musuh yang sama.
lo-help-drop = 1 AP; letakkan kargo di sini. Memulihkan pergerakan normal dan penggunaan senjata utama.
lo-help-guard = 1 AP; cegat serangan berikutnya di zona ini dan kurangi kerusakannya sebanyak satu. Berakhir pada siklus berikutnya; tidak dapat ditumpuk dan tidak menarik musuh jauh.
lo-error-guarded = Anda sudah bersiap bertahan.
lo-error-carrying = Kargo menghalangi penggunaan senjata utama. Gunakan pistol atau letakkan kargo.
lo-error-terminal = Terminal ini sudah aktif.
lo-error-relay-partner = Penyintas lain harus mengaktifkan terminal satunya.
lo-task-activate = Aktifkan terminal relai ini; lokasi pasangan: { $zone }
lo-task-pickup = Ambil kargo untuk { $zone }
lo-task-deliver = Kirim kargo di { $zone }
lo-event-mission_complete = { $party_size ->
    [1] { $item } selesai: { $sites }. +{ $count } kredit; +1 suku cadang. { $defense }
   *[other] { $item } selesai: { $sites }. Setiap penyintas +{ $count } kredit; tim +1 suku cadang. { $defense }
    }
lo-event-mission_failed = { $item } gagal. Misi gagal: { $amount }.
lo-event-mission_clock = { $item }: tersisa { $amount } fase gerombolan.
lo-event-mission_pressure = Kebisingan misi menarik { $count } pejalan ke luar { $zone }. Aktif pada fase gerombolan berikutnya.
lo-event-hold_progress = Pertahanan di { $zone }: { $amount } dari { $count } fase diamankan.
lo-event-core_damage = Relai di { $zone } kehilangan { $amount } keutuhan; tersisa { $count }.
lo-event-relay_reset = Relai: { $item }.
lo-event-cargo_lost = Kargo jatuh di { $zone }.
lo-event-condition = { $item }. Bala bantuan pertama setelah fase gerombolan { $amount }.
lo-term-outpost = Pos Terbengkalai
lo-term-switchyard = Emplasemen
lo-term-floodworks = Instalasi Banjir
lo-term-operations = Operasi
lo-term-siege = Pengepungan
lo-term-salvage = Penyelamatan Kargo
lo-term-classic = Evakuasi Klasik
lo-term-recruit = Rekrut
lo-term-standard = Standar
lo-term-veteran = Veteran
lo-term-retrieve = Pengambilan kargo
lo-term-relay = Relai terkoordinasi
lo-term-hold = Pertahanan sektor
lo-term-mission_quota = Persyaratan misi tidak terpenuhi
lo-term-core_lost = Relai hancur
lo-term-latched = terminal yang sudah diaktifkan tetap siap
lo-term-reset = aktifkan kembali kedua terminal pada siklus yang sama
lo-term-condition-normal = Kondisi cerah
lo-term-condition-rush = Bala bantuan lebih awal
lo-term-condition-fog = Kabut: senjata api dibatasi satu penghubung
lo-term-condition-battering = Gerombolan pendobrak: satu kerusakan tambahan pada barikade
lo-term-condition-shortage = Kekurangan perbekalan: magasin cadangan seharga 90 kredit
lo-term-depot = Depo Penumpang
lo-term-west_tracks = Rel Barat
lo-term-east_tracks = Rel Timur
lo-term-signal_box = Pos Sinyal
lo-term-freight = Lapangan Barang
lo-term-maintenance = Gudang Perawatan
lo-term-switchgear = Ruang Panel Listrik
lo-term-overpass = Jembatan Layang
lo-term-tower = Menara Radio
lo-term-tunnel = Terowongan Rel
lo-term-quay = Dermaga
lo-term-foyer = Lobi Masuk
lo-term-canal = Kanal Drainase
lo-term-filter = Bak Filter
lo-term-control = Ruang Kendali
lo-term-laboratory = Laboratorium
lo-term-archive = Gudang Perbekalan
lo-term-turbine = Aula Turbin
lo-term-skybridge = Jembatan Radio
lo-term-clinic = Klinik
lo-event-guard = { $actor } bersiap bertahan: serangan berikutnya menimbulkan satu kerusakan lebih sedikit.
lo-event-guard-personal = Anda bersiap bertahan: serangan berikutnya menimbulkan satu kerusakan lebih sedikit.
lo-event-cargo_pickup = { $actor } mengambil kargo di { $zone } untuk { $origin }.
lo-event-cargo_pickup-personal = Anda mengambil kargo di { $zone } untuk { $origin }.
lo-event-cargo_deliver = { $actor } mengirim kargo di { $zone }.
lo-event-cargo_deliver-personal = Anda mengirim kargo di { $zone }.
lo-event-cargo_drop = { $actor } meletakkan kargo di { $zone }.
lo-event-cargo_drop-personal = Anda meletakkan kargo di { $zone }.
lo-event-cargo_handoff = { $actor } menyerahkan kargo kepada { $target } di { $zone }.
lo-event-cargo_handoff-personal = Anda menyerahkan kargo kepada { $target } di { $zone }.
lo-event-relay_armed = { $actor } mengaktifkan terminal di { $zone }; { $amount } terminal siap.
lo-event-relay_armed-personal = Anda mengaktifkan terminal di { $zone }; { $amount } terminal siap.
lo-event-cargo_handoff-target = { $actor } menyerahkan kargo kepada Anda di { $zone }.
lo-zone-description-depot = Deretan bangku kosong menghadap papan keberangkatan yang membeku pada daftar kereta dibatalkan. Debu menyelimuti lantai beton. Pintu di kedua ujung aula menuju rel barat dan timur.
lo-zone-description-west_tracks = Jalur baja mengikuti rel berkarat di bawah lampu sinyal mati. Tiang pagar menandai tepi emplasemen; di seberang depo, Pos Sinyal menjulang di sisi utara.
lo-zone-description-east_tracks = Gerbong kosong berdiri di samping lantai baja yang melengkung. Rel membentang menuju kegelapan di luar perimeter; Lapangan Barang terbuka di utara.
lo-zone-description-signal_box = Tuas memenuhi kabin kayu di atas diagram rel yang memudar. Jendela menghadap rel barat. Lorong mengarah ke Gudang Perawatan dan tangga menuju Jembatan Layang.
lo-zone-description-freight = Kontainer barang menjulang di atas lapangan berlapis baja penyok. Rantai longgar menggantung dari rangka pemuat. Gerbang penyeberangan menjaga jalan ke Jembatan Layang; rute lain memasuki Terowongan Rel.
lo-zone-description-maintenance = Roda yang dibongkar dan perkakas berminyak memenuhi gudang berdinding logam bergelombang. Lemari amunisi berdiri di lantai beton bernoda, di samping gerbang servis menuju Ruang Panel Listrik.
lo-zone-description-switchgear = Deretan sakelar besar memenuhi ruang beton di balik gerbang servis. Kabel tebal menghilang di bawah pelat lantai logam, dan label peringatan terkelupas dari lemari. Pulihkan listrik emplasemen di sini.
lo-zone-description-overpass = Lantai kisi baja terbuka membentang di atas rel, dengan hanya pegangan sempit di tepi jurang. Pos Sinyal dan Lapangan Barang berada di bawah; Menara Radio menjulang di depan, ke utara.
lo-zone-description-tower = Meja radio dan kursi kayu usang memenuhi kabin di atas rel. Jendela menghadap emplasemen di segala sisi. Listrik diperlukan untuk membuka gerbang akses di bawah.
lo-zone-description-tunnel = Rel menghilang ke dalam terowongan beton bergaris jelaga dan rembesan air. Lapangan Barang berada di belakang Anda; lorong samping menanjak menuju gerbang akses Menara Radio.
lo-zone-description-quay = Papan dermaga melengkung menjorok di atas air hitam, dengan tali tambat menjuntai longgar. Perimeter selatan berakhir di sini. Di depan, pintu masuk beton instalasi membuka jalan ke Lobi Masuk.
lo-zone-description-foyer = Noda air merambat di dinding beton di bawah denah evakuasi yang memudar. Pintu masuk sempit ini bercabang ke Kanal Drainase di barat dan Gudang Perbekalan di timur.
lo-zone-description-canal = Air dangkal mengalir di antara tepian beton tinggi, membawa potongan rumput dari luar perimeter. Kanal berbelok ke utara menuju Bak Filter; lobi berada di timur.
lo-zone-description-filter = Air banjir menggenang di sekeliling deretan bak filter tersumbat di bawah dinding logam berkarat. Gerbang servis menuju turbin; pintu sekat berat memisahkan aula ini dari Ruang Kendali.
lo-zone-description-control = Deretan panjang alat ukur dan layar retak menghadap lantai logam. Laboratorium terbuka di timur, pintu sekat filter di barat; jalan utara menanjak ke Jembatan Radio.
lo-zone-description-laboratory = Stoples sampel keruh memenuhi meja, dan pecahan kaca berkilau di atas beton. Pintu menghubungkan Gudang Perbekalan, Ruang Kendali, dan Klinik; semua rute melintasi ruang kerja terbengkalai ini.
lo-zone-description-archive = Buku catatan yang menggembung terkena air terkulai di rak kayu di samping peti perbekalan tersegel. Lemari amunisi menempati sudut paling kering. Lobi berada di barat, Laboratorium di utara.
lo-zone-description-turbine = Rumah turbin raksasa memenuhi aula logam luas di balik gerbang servis. Pelat perawatan membentuk lantai di antaranya. Kontrol listrik berada di bawah rute naik ke Jembatan Radio.
lo-zone-description-skybridge = Jembatan baja sempit menggantung di atas aula utara instalasi, terbuka terhadap angin. Lemari radio berdiri di bawah antena; jalan dari Ruang Kendali, Klinik, dan turbin bertemu di sini.
lo-zone-description-clinic = Tirai privasi pudar membagi ruang beton yang dipenuhi ranjang pemeriksaan. Kelembapan merambat di bawah lemari obat. Laboratorium berada di selatan; jalan lain menanjak ke Jembatan Radio.
lo-event-mission_start-retrieve = Kargo: { $zone } ke { $origin }. Batas waktu: { $amount } fase gerombolan.
lo-event-mission_start-relay = Relai: { $zone } dan { $origin }. Batas waktu: { $amount } fase gerombolan.
lo-event-mission_start-hold = Pertahankan { $zone }. Batas waktu: { $amount } fase gerombolan.
lo-error-visibility = Kabut menghalangi tembakan melewati satu penghubung.
lo-help-weapon = Kerusakan { $damage }; setelah ditingkatkan { $upgraded }; sasaran { $targets }; jangkauan { $minimum }–{ $maximum }; magasin { $magazine }; { $rounds } peluru per tembakan; { $price } kredit. Menggantikan senjata utama; tanpa pengembalian dana.
lo-error-barricade = Barikade menghalangi serangan ini.
lo-combat-hit = { $enemy }: kerusakan { $damage }
lo-combat-outside = { $zone }, { lo-outside }
lo-objective-generator = Listrik
lo-objective-radio = Radio
lo-combat-kills = { $count ->
    [0] { "" }
    [one] 1 musuh terbunuh.
   *[other] { $count } musuh terbunuh.
    }
lo-shop-ready = Selesai berbelanja dan Siap
lo-help-shop-ready = E menutup toko dan menandai Anda siap. X kembali tanpa menandai siap.
lo-already-ready = { $party_size ->
    [1] Siap.
   *[other] Anda siap. Menunggu regu.
    }
lo-help-teammates = { $party_size ->
    [1] Posisi, kesehatan, dan karakter Anda.
   *[other] Posisi, kesehatan, batas waktu penyelamatan, dan karakter regu.
    }
lo-help-objectives = Syarat kemenangan, kemajuan infrastruktur, dan misi aktif.
lo-teammates = { $party_size ->
    [1] Karakter
   *[other] Rekan satu tim
    }
lo-required = Wajib
lo-optional = Opsional
lo-complete = Selesai
lo-incomplete = Belum selesai
lo-objective-waves = Wajib: selesaikan semua gelombang. { $completed }/{ $total } selesai.
lo-objective-missions = Wajib: selesaikan { $total } misi. { $completed } selesai; { $failed } gagal.
lo-objective-bonus-missions = Misi: { $completed } selesai; { $failed } gagal.
lo-objective-integrity = Wajib: jaga keutuhan relai. Keutuhan { $current }/{ $total }.
lo-objective-project = { $project }, { $zone }: { $requirement }. { $state }; pekerjaan { $progress }/{ $total }. Tersisa: { $remaining } pekerjaan, { $cost } suku cadang, ditambah gerbang akses yang belum dibuka.
lo-mission-idle = Tidak ada misi aktif.
lo-verb-unready = Batalkan kesiapan

lo-health-recovering = Tumbang; pemulihan darurat { $recovery_seconds } detik setelah gerombolan bertindak
lo-inventory-parts = { $party_size ->
    [1] Suku cadang: { $parts }.
   *[other] Suku cadang bersama: { $parts }.
    }
lo-board-lineup = { $count ->
    [1] Satu penyintas
   *[other] Penyintas { $count }: manusia { $humans }, bot { $bots }
    }
lo-board-original = Tanpa pengambilalihan oleh bot
lo-board-takeover = Dengan pengambilalihan oleh bot
leaderboard-lo-clear-entry = { $rank }. { $player }: { $value } fase gerombolan.
lo-personal-record = { $name }: { $value } fase gerombolan.
lo-record-unranked = Tidak masuk peringkat: susunan pemain awal berubah.
