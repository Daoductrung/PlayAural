game-name-sorry = Sorry!
sorry-set-rules-profile = Pilihan aturan: { $profile }
sorry-select-rules-profile = Pilih aturan permainan
sorry-option-changed-rules-profile = Pilihan aturan diatur menjadi { $profile }.
sorry-desc-rules-profile = Menentukan aturan Sorry, yaitu kartu Classic 00390 atau aturan inti versi A5065 yang lebih baru.
sorry-rules-profile-classic-00390 = Classic 00390
sorry-rules-profile-a5065-core = A5065 Core
sorry-toggle-auto-apply-single-move = Jalankan otomatis jika hanya ada satu langkah: { $enabled }
sorry-option-changed-auto-apply-single-move = Pengaturan untuk menjalankan satu-satunya langkah secara otomatis kini { $enabled }.
sorry-desc-auto-apply-single-move = Jika diaktifkan, kartu yang hanya memiliki satu langkah yang diperbolehkan akan dijalankan otomatis.
sorry-toggle-faster-setup-one-pawn-out = Mulai lebih cepat, satu bidak sudah keluar: { $enabled }
sorry-option-changed-faster-setup-one-pawn-out = Mulai lebih cepat diatur menjadi { $enabled }.
sorry-desc-faster-setup-one-pawn-out = Setiap pemain mulai dengan satu bidak sudah keluar agar tidak terlalu lama menunggu di awal.
sorry-error-unsupported-rules-profile = Pilihan aturan Sorry "{ $profile }" tidak didukung. Pilih Classic 00390 atau A5065 Core sebelum memulai.
sorry-draw-card = Ambil kartu
sorry-check-board = Baca papan
sorry-check-pawns = Periksa bidak Anda
sorry-check-card = Periksa kartu saat ini
sorry-check-status = Periksa status
sorry-move-slot = Pilihan langkah { $slot }
sorry-move-slot-fallback = Pilih langkah
sorry-move-start = Keluarkan bidak { $pawn } dari { $position } ke lintasan
sorry-move-forward = Majukan bidak { $pawn } dari { $position } sejauh { $steps } petak
sorry-move-backward = Mundurkan bidak { $pawn } dari { $position } sejauh { $steps } petak
sorry-move-swap = Tukar bidak { $pawn } di { $position } dengan bidak { $target_pawn } milik { $target_player } di { $target_position }
sorry-move-sorry = Gunakan Sorry! dengan bidak { $pawn } di { $position } terhadap bidak { $target_pawn } milik { $target_player } di { $target_position }
sorry-move-split7-pick = Bagi 7 langkah antara bidak { $pawn_a } di { $position_a } dan bidak { $pawn_b } di { $position_b }
sorry-move-split7-option = Bidak { $pawn_a } di { $position_a } maju { $steps_a }, bidak { $pawn_b } di { $position_b } maju { $steps_b }
sorry-card-none = belum ada kartu aktif
sorry-card-sorry = Sorry!
sorry-choose-move = Pilih langkah.
sorry-choose-split = Pilih pembagian 7 langkah.
sorry-error-draw-pending-move = Anda sudah mengambil kartu. Pilih salah satu langkah yang tersedia untuk kartu itu sebelum mengambil kartu lagi.
sorry-game-started = Sorry dimulai. Pemain: { $players }.
sorry-draw-announcement = { $player } mengambil kartu { $card }.
sorry-you-draw-announcement = Anda mengambil kartu { $card }.
sorry-no-legal-moves = { $player } tidak memiliki langkah yang diperbolehkan untuk kartu { $card }.
sorry-you-no-legal-moves = Anda tidak memiliki langkah yang diperbolehkan untuk kartu { $card }.
sorry-deck-exhausted = Tumpukan kartu Sorry habis, jadi permainan berakhir.
sorry-you-extra-turn = Anda mengambil kartu 2 dan mendapat giliran tambahan.
sorry-player-extra-turn = { $player } mengambil kartu 2 dan mendapat giliran tambahan.
sorry-play-start = { $brief ->
    [yes] { $player }: bidak { $pawn } keluar ke { $destination }.
   *[no] { $player } mengeluarkan bidak { $pawn } ke { $destination }.
}
sorry-you-play-start = { $brief ->
    [yes] Anda: bidak { $pawn } keluar ke { $destination }.
   *[no] Anda mengeluarkan bidak { $pawn } ke { $destination }.
}
sorry-play-forward = { $brief ->
    [yes] { $player }: bidak { $pawn } maju { $steps } ke { $destination }.
   *[no] { $player } memajukan bidak { $pawn } sejauh { $steps } petak ke { $destination }.
}
sorry-you-play-forward = { $brief ->
    [yes] Anda: bidak { $pawn } maju { $steps } ke { $destination }.
   *[no] Anda memajukan bidak { $pawn } sejauh { $steps } petak ke { $destination }.
}
sorry-play-backward = { $brief ->
    [yes] { $player }: bidak { $pawn } mundur { $steps } ke { $destination }.
   *[no] { $player } memundurkan bidak { $pawn } sejauh { $steps } petak ke { $destination }.
}
sorry-you-play-backward = { $brief ->
    [yes] Anda: bidak { $pawn } mundur { $steps } ke { $destination }.
   *[no] Anda memundurkan bidak { $pawn } sejauh { $steps } petak ke { $destination }.
}
sorry-play-swap = { $brief ->
    [yes] { $player }: bidak { $pawn } bertukar dengan bidak { $target_pawn } milik { $target_player }, berakhir di { $destination }.
   *[no] { $player } menukar bidak { $pawn } dengan bidak { $target_pawn } milik { $target_player }, lalu berhenti di { $destination }.
}
sorry-you-play-swap = { $brief ->
    [yes] Anda: bidak { $pawn } bertukar dengan bidak { $target_pawn } milik { $target_player }, berakhir di { $destination }.
   *[no] Anda menukar bidak { $pawn } dengan bidak { $target_pawn } milik { $target_player }, lalu berhenti di { $destination }.
}
sorry-play-sorry = { $brief ->
    [yes] { $player }: Sorry! Bidak { $pawn } ke { $destination }, bidak { $target_pawn } milik { $target_player } kembali ke area awal.
   *[no] { $player } memainkan Sorry!, menggantikan bidak { $target_pawn } milik { $target_player }, lalu berhenti di { $destination }.
}
sorry-you-play-sorry = { $brief ->
    [yes] Anda: Sorry! Bidak { $pawn } ke { $destination }, bidak { $target_pawn } milik { $target_player } kembali ke area awal.
   *[no] Anda memainkan Sorry!, menggantikan bidak { $target_pawn } milik { $target_player }, lalu berhenti di { $destination }.
}
sorry-play-split7 = { $brief ->
    [yes] { $player }: bidak { $pawn_a } maju { $steps_a } ke { $destination_a }, bidak { $pawn_b } maju { $steps_b } ke { $destination_b }.
   *[no] { $player } membagi 7 langkah. Bidak { $pawn_a } maju { $steps_a } petak ke { $destination_a } dan bidak { $pawn_b } maju { $steps_b } petak ke { $destination_b }.
}
sorry-you-play-split7 = { $brief ->
    [yes] Anda: bidak { $pawn_a } maju { $steps_a } ke { $destination_a }, bidak { $pawn_b } maju { $steps_b } ke { $destination_b }.
   *[no] Anda membagi 7 langkah. Bidak { $pawn_a } maju { $steps_a } petak ke { $destination_a } dan bidak { $pawn_b } maju { $steps_b } petak ke { $destination_b }.
}
sorry-pawn-home = Bidak { $pawn } milik { $player } mencapai rumah.
sorry-you-pawn-home = Bidak { $pawn } Anda mencapai rumah.
sorry-your-pawn-captured = { $brief ->
    [yes] { $by_player }: bidak { $pawn } Anda kembali ke area awal.
   *[no] Bidak { $pawn } Anda dipulangkan ke area awal oleh { $by_player }.
}
sorry-you-captured-pawn = { $brief ->
    [yes] Anda: bidak { $pawn } milik { $target_player } kembali ke area awal.
   *[no] Anda memulangkan bidak { $pawn } milik { $target_player } ke area awal.
}
sorry-pawn-captured = { $brief ->
    [yes] { $player }: bidak { $pawn } milik { $target_player } kembali ke area awal.
   *[no] { $player } memulangkan bidak { $pawn } milik { $target_player } ke area awal.
}
sorry-you-bumped-own-pawn = { $brief ->
    [yes] Anda: bidak { $pawn } sendiri kembali ke area awal.
   *[no] Anda memulangkan bidak { $pawn } milik sendiri ke area awal.
}
sorry-player-bumped-own-pawn = { $brief ->
    [yes] { $player }: bidak { $pawn } sendiri kembali ke area awal.
   *[no] { $player } memulangkan bidak { $pawn } milik sendiri ke area awal.
}
sorry-current-card = Kartu saat ini: { $card }.
sorry-view-your-pawn = Bidak { $pawn } Anda: { $zone }.
sorry-board-your-color = Warna Anda: { $color }.
sorry-board-summary-heading = Ringkasan:
sorry-board-summary-line = { $player } ({ $color }): { $pawns }
sorry-board-summary-item = bidak { $pawn } di { $location }
sorry-board-player-color = { $player } ({ $color })
sorry-board-track-heading = Petak lintasan:
sorry-board-private-areas-heading = Area pribadi:
sorry-board-square-line = Petak { $square }: { $status }
sorry-board-square-empty = kosong
sorry-board-square-slide = jalur luncur { $color }
sorry-board-square-token = bidak { $pawn } milik { $player }
sorry-board-start-line = Area awal { $color } milik { $player }: { $pawns }
sorry-board-safety-line = Petak aman { $color } nomor { $space } milik { $player }: { $pawns }
sorry-board-home-line = Rumah { $color } milik { $player }: { $pawns }
sorry-board-area-empty = kosong
sorry-board-area-pawn = bidak { $pawn }
sorry-color-red = merah
sorry-color-blue = biru
sorry-color-yellow = kuning
sorry-color-green = hijau
sorry-location-start = area awal
sorry-location-track = petak { $position }
sorry-location-home-path = petak aman { $steps }
sorry-location-home = rumah
sorry-zone-start = di area awal
sorry-zone-track = di petak lintasan { $position }
sorry-zone-home-path = di petak { $steps } pada jalur aman
sorry-zone-home = di rumah
sorry-status-turn-number = Giliran { $count }
sorry-status-phase = Tahap: { $phase }
sorry-status-current-card = Kartu: { $card }
sorry-status-current-player = Pemain yang mendapat giliran: { $player }
sorry-phase-draw = mengambil kartu
sorry-phase-choose-move = memilih langkah
sorry-phase-choose-split = membagi tujuh langkah
sorry-phase-resolving = menjalankan langkah
sorry-end-score-line = { $index }. { $player }: { $count ->
    [one] 1 bidak sampai di rumah
   *[other] { $count } bidak sampai di rumah
}
