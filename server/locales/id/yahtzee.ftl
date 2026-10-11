game-name-yahtzee = Yahtzee
yahtzee-roll = Lempar ulang, tersisa { $count } kali
yahtzee-roll-all = Lempar dadu
yahtzee-score-ones = Angka satu, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-twos = Angka dua, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-threes = Angka tiga, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-fours = Angka empat, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-fives = Angka lima, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-sixes = Angka enam, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-three-kind = Tiga angka sama, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-four-kind = Empat angka sama, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-full-house = Full House, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-small-straight = Urutan pendek, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-large-straight = Urutan panjang, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-yahtzee = Yahtzee, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-score-chance = Bebas, { $points } { $points ->
    [one] poin
   *[other] poin
}
yahtzee-you-rolled = Hasil lemparan Anda: { $dice }. { $remaining ->
    [0] Pilih kategori skor.
   *[other] Tersisa { $remaining } { $remaining ->
        [one] lemparan
       *[other] lemparan
    }.
}
yahtzee-player-rolled = Hasil lemparan { $player }: { $dice }. { $remaining ->
    [0] Pemain harus memilih kategori skor.
   *[other] Tersisa { $remaining } { $remaining ->
        [one] lemparan
       *[other] lemparan
    }.
}
yahtzee-you-rolled-brief = Lemparan Anda: { $dice }.
yahtzee-player-rolled-brief = Lemparan { $player }: { $dice }.
yahtzee-you-scored = Anda mencatat { $points } { $points ->
    [one] poin
   *[other] poin
} pada kategori { $category }.
yahtzee-player-scored = { $player } mencatat { $points } { $points ->
    [one] poin
   *[other] poin
} pada kategori { $category }.
yahtzee-you-scored-brief = { $points } pada kategori { $category }.
yahtzee-player-scored-brief = { $player }: { $points } pada kategori { $category }.
yahtzee-you-bonus = Bonus Yahtzee! Anda mendapat tambahan 100 poin.
yahtzee-player-bonus = { $player } mendapat bonus Yahtzee! Tambahan 100 poin.
yahtzee-you-bonus-brief = Bonus Yahtzee, tambah 100.
yahtzee-player-bonus-brief = { $player }: bonus Yahtzee, tambah 100.
yahtzee-you-upper-bonus = Bonus bagian atas! Tambahan 35 poin. Skor bagian atas Anda { $total }.
yahtzee-player-upper-bonus = { $player } mendapat bonus bagian atas! Tambahan 35 poin. Skor bagian atasnya { $total }.
yahtzee-you-upper-bonus-brief = Bonus bagian atas, tambah 35.
yahtzee-player-upper-bonus-brief = { $player }: bonus bagian atas, tambah 35.
yahtzee-you-upper-bonus-missed = Anda tidak mendapat bonus bagian atas. Skor Anda { $total }, kurang { $needed } poin lagi.
yahtzee-player-upper-bonus-missed = { $player } tidak mendapat bonus bagian atas. Skor bagian atasnya { $total }, kurang { $needed } poin lagi.
yahtzee-you-upper-bonus-missed-brief = Tidak mendapat bonus bagian atas, kurang { $needed }.
yahtzee-player-upper-bonus-missed-brief = { $player }: tidak mendapat bonus bagian atas, kurang { $needed }.
yahtzee-check-scoresheet = Periksa kartu skor
yahtzee-check-all-scorecards = Periksa kartu skor semua pemain
yahtzee-select-scorecard-player = Pilih pemain untuk melihat kartu skornya.
yahtzee-scorecard-no-players = Belum ada pemain aktif yang memiliki kartu skor dalam permainan ini.
yahtzee-scorecard-player-unavailable = Kartu skor pemain tersebut tidak lagi tersedia. Buka kembali daftar kartu skor dan pilih pemain aktif.
yahtzee-view-dice = Periksa dadu
yahtzee-your-dice = Dadu Anda: { $dice }.
yahtzee-your-dice-kept = Dadu Anda: { $dice }. Disimpan: { $kept }.
yahtzee-current-dice = Dadu { $player }: { $dice }.
yahtzee-current-dice-kept = Dadu { $player }: { $dice }. Disimpan: { $kept }.
yahtzee-not-rolled = Pemain yang mendapat giliran belum melempar.
yahtzee-scoresheet-header = Kartu skor { $player }
yahtzee-scoresheet-upper = Bagian atas:
yahtzee-scoresheet-lower = Bagian bawah:
yahtzee-scoresheet-upper-total-bonus = Total bagian atas: { $total }, bonus 35
yahtzee-scoresheet-upper-total-needed = Total bagian atas: { $total }, perlu { $needed } lagi untuk bonus
yahtzee-scoresheet-yahtzee-bonus = Bonus Yahtzee: { $count } kali 100, total { $total }
yahtzee-scoresheet-grand-total = Skor total: { $total }
yahtzee-category-ones = Angka satu
yahtzee-category-twos = Angka dua
yahtzee-category-threes = Angka tiga
yahtzee-category-fours = Angka empat
yahtzee-category-fives = Angka lima
yahtzee-category-sixes = Angka enam
yahtzee-category-three-kind = Tiga angka sama
yahtzee-category-four-kind = Empat angka sama
yahtzee-category-full-house = Full House
yahtzee-category-small-straight = Urutan pendek
yahtzee-category-large-straight = Urutan panjang
yahtzee-category-yahtzee = Yahtzee
yahtzee-category-chance = Bebas
yahtzee-you-win = Anda menang dengan { $score } { $score ->
    [one] poin
   *[other] poin
}!
yahtzee-player-wins = { $player } menang dengan { $score } { $score ->
    [one] poin
   *[other] poin
}!
yahtzee-winners-tie = Seri! { $players } masing-masing mendapat { $score } poin!
yahtzee-set-rounds = Jumlah permainan: { $rounds }
yahtzee-enter-rounds = Masukkan jumlah permainan, dari 1 sampai 10:
yahtzee-option-changed-rounds = Jumlah permainan diatur menjadi { $rounds }.
yahtzee-desc-num-games = Jumlah kartu skor Yahtzee yang diselesaikan sebelum skor total akhir dibandingkan. Nilai bawaan 1, dari 1 sampai 10.
yahtzee-no-rolls-left = Jatah lemparan Anda habis. Pilih kategori skor yang belum terisi untuk mengakhiri giliran.
yahtzee-roll-first = Lempar dadu sebelum memilih kategori skor.
yahtzee-category-filled = Kategori tersebut sudah berisi skor. Pilih kategori yang masih kosong pada kartu skor Anda.
yahtzee-joker-upper-required = Aturan Joker: karena Yahtzee ini menunjukkan angka { $face }, Anda harus mencatat skor pada kotak angka { $face } di bagian atas sebelum memilih kategori lain.
yahtzee-joker-lower-required = Aturan Joker: kotak angka { $face } di bagian atas sudah terisi. Pilih kategori kosong di bagian bawah sebelum menggunakan kotak lain di bagian atas.
