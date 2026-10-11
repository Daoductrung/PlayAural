game-name-zombiedice = Zombie Dice

zombiedice-set-target-score = Jumlah otak untuk menang: { $score }
zombiedice-enter-target-score = Masukkan target kemenangan antara 5 dan 50 otak:
zombiedice-option-changed-target-score = Target kemenangan sekarang { $score } otak.
zombiedice-desc-target-score = Mencapai jumlah ini memulai ronde terakhir bagi pemain yang belum mendapat giliran. Target resmi adalah 13 otak. Target lebih rendah memperpendek permainan, sedangkan target lebih tinggi memperpanjangnya.
zombiedice-roll-first = Lempar 3 dadu
zombiedice-roll-first-description = Ambil tiga dadu secara acak dari cangkir, lalu lempar.
zombiedice-roll-again = Lempar lagi. { $brains } { $brains ->
    [one] otak dipertaruhkan
   *[other] otak dipertaruhkan
}
zombiedice-roll-again-description = Lempar ulang { $footprints } { $footprints ->
    [one] dadu jejak kaki
   *[other] dadu jejak kaki
} dan ambil { $draw } { $draw ->
    [one] dadu baru
   *[other] dadu baru
} agar jumlahnya tiga. Tembakan ketiga menghilangkan semua { $brains } { $brains ->
    [one] otak yang belum diamankan
   *[other] otak yang belum diamankan
}.
zombiedice-bank = Berhenti dan amankan { $brains } { $brains ->
    [one] otak
   *[other] otak
}
zombiedice-bank-keybind = Berhenti dan amankan otak
zombiedice-bank-description = Akhiri giliran Anda dan amankan { $brains } { $brains ->
    [one] otak
   *[other] otak
}.
zombiedice-check-turn-totals = Periksa perolehan giliran
zombiedice-check-turn-totals-description = Dengarkan jumlah otak, tembakan, dan jejak kaki saat ini.
zombiedice-review-turn = Tinjau giliran saat ini
zombiedice-review-turn-description = Tinjau semua dadu yang terbuka, jumlah dadu dalam cangkir, lemparan terakhir, dan otak yang belum diamankan.
zombiedice-review-table = Tinjau meja
zombiedice-review-table-description = Tinjau target, tahap permainan, urutan giliran, giliran saat ini, dan skor.
zombiedice-game-start = Zombie Dice dimulai. Target: { $target } otak. { $first } mendapat giliran pertama. Urutan: { $order }.
zombiedice-your-turn = Giliran Anda. Sudah diamankan: { $score } { $score ->
    [one] otak
   *[other] otak
}. Lempar tiga dadu.
zombiedice-player-turn = Giliran { $player }. Sudah diamankan: { $score } { $score ->
    [one] otak
   *[other] otak
}.
zombiedice-you-refill-cup = Dadu dalam cangkir tidak cukup. Anda mengembalikan { $count } { $count ->
    [one] dadu otak
   *[other] dadu otak
}. { $brains } { $brains ->
    [one] otak yang Anda peroleh pada giliran ini tetap dihitung
   *[other] otak yang Anda peroleh pada giliran ini tetap dihitung
}.
zombiedice-player-refills-cup = Dadu dalam cangkir tidak cukup. { $player } mengembalikan { $count } { $count ->
    [one] dadu otak
   *[other] dadu otak
}. { $brains } { $brains ->
    [one] otak yang diperolehnya pada giliran ini tetap dihitung
   *[other] otak yang diperolehnya pada giliran ini tetap dihitung
}.
zombiedice-you-roll = Hasil lemparan Anda: { $results }.
zombiedice-player-rolls = Hasil lemparan { $player }: { $results }.
zombiedice-you-bust = Hasil lemparan Anda: { $results }. { $shotguns } tembakan. Anda tertembak dan kehilangan { $brains } { $brains ->
    [one] otak yang belum diamankan
   *[other] otak yang belum diamankan
}.
zombiedice-player-busts = Hasil lemparan { $player }: { $results }. { $shotguns } tembakan. { $player } tertembak dan kehilangan { $brains } { $brains ->
    [one] otak yang belum diamankan
   *[other] otak yang belum diamankan
}.
zombiedice-you-bank = Anda mengamankan { $brains } { $brains ->
    [one] otak
   *[other] otak
}. Total: { $total }.
zombiedice-player-banks = { $player } mengamankan { $brains } { $brains ->
    [one] otak
   *[other] otak
}. Total: { $total }.
zombiedice-you-trigger-final-round = Anda mencapai { $score } otak. Masih ada { $remaining } { $remaining ->
    [one] pemain yang mendapat giliran di ronde terakhir
   *[other] pemain yang mendapat giliran di ronde terakhir
}.
zombiedice-player-triggers-final-round = { $player } mencapai { $score } otak. Masih ada { $remaining } { $remaining ->
    [one] pemain yang mendapat giliran di ronde terakhir
   *[other] pemain yang mendapat giliran di ronde terakhir
}.
zombiedice-tiebreak-start = Babak penentuan { $round }: { $players }, seri dengan { $score } otak. Masing-masing mendapat satu giliran.
zombiedice-you-win = Anda memenangkan Zombie Dice dengan { $score } otak.
zombiedice-player-wins = { $player } memenangkan Zombie Dice dengan { $score } otak.
zombiedice-error-roll-before-stopping = Lempar sekali sebelum berhenti. Setelah lemparan yang aman, Anda boleh berhenti meskipun baru memperoleh 0 otak.
zombiedice-error-roll-resolving = Dadu masih bergulir.
zombiedice-error-target-score-range = Target kemenangan harus antara { $min } dan { $max } otak. Nilai saat ini adalah { $value }.
zombiedice-color-green = hijau
zombiedice-color-yellow = kuning
zombiedice-color-red = merah
zombiedice-face-brain = otak
zombiedice-face-footprint = jejak kaki
zombiedice-face-shotgun = tembakan
zombiedice-roll-result = { $color } { $face }
zombiedice-pool-color = { $count } { $count ->
    [one] dadu
   *[other] dadu
} { $color }
zombiedice-no-dice = tidak ada
zombiedice-status-no-turn = Tidak ada giliran Zombie Dice yang sedang berlangsung.
zombiedice-your-turn-totals = Anda: { $brains } { $brains ->
    [one] otak
   *[other] otak
}, { $shotguns } { $shotguns ->
    [one] tembakan
   *[other] tembakan
}, dan { $footprints } { $footprints ->
    [one] jejak kaki
   *[other] jejak kaki
}.
zombiedice-player-turn-totals = { $player }: { $brains } { $brains ->
    [one] otak
   *[other] otak
}, { $shotguns } { $shotguns ->
    [one] tembakan
   *[other] tembakan
}, dan { $footprints } { $footprints ->
    [one] jejak kaki
   *[other] jejak kaki
}.
zombiedice-status-turn-you = Giliran Anda. Sudah diamankan: { $score } { $score ->
    [one] otak
   *[other] otak
}.
zombiedice-status-turn-player = Giliran { $player }. Sudah diamankan: { $score } { $score ->
    [one] otak
   *[other] otak
}.
zombiedice-status-turn-totals = Giliran ini: { $brains } { $brains ->
    [one] otak
   *[other] otak
}, { $shotguns } { $shotguns ->
    [one] tembakan
   *[other] tembakan
}, dan { $footprints } { $footprints ->
    [one] jejak kaki
   *[other] jejak kaki
}.
zombiedice-status-cup = Cangkir: { $count } { $count ->
    [one] dadu
   *[other] dadu
}.
zombiedice-status-footprints = Dadu jejak kaki yang akan dilempar ulang: { $dice }.
zombiedice-status-brain-dice = Dadu otak yang disisihkan: { $dice }.
zombiedice-status-shotgun-dice = Dadu tembakan yang disisihkan: { $dice }.
zombiedice-status-last-roll = Lemparan terakhir: { $results }.
zombiedice-status-awaiting-roll = Belum ada lemparan pada giliran ini.
zombiedice-status-table-header = Zombie Dice. Ronde { $round }, target: { $target } otak.
zombiedice-status-table-header-tiebreak = Zombie Dice. Target: { $target } otak.
zombiedice-status-main-round = Tahap: permainan utama.
zombiedice-status-final-round = Ronde terakhir. { $player } telah mencapai target.
zombiedice-status-tiebreak = Babak penentuan { $round }: { $players }.
zombiedice-status-current-you = Giliran Anda.
zombiedice-status-current-player = Giliran { $player }.
zombiedice-status-turn-order = Urutan giliran: { $players }.
zombiedice-status-score-you = Anda: { $score } { $score ->
    [one] otak
   *[other] otak
}.
zombiedice-status-score-player = { $player }: { $score } { $score ->
    [one] otak
   *[other] otak
}.
zombiedice-score-unit-brains = { $count ->
    [one] otak
   *[other] otak
}
zombiedice-results-header = Hasil Zombie Dice
zombiedice-results-winner = Pemenang: { $player } dengan { $score } otak.
zombiedice-results-line = { $rank }. { $player }: { $score } { $score ->
    [one] otak
   *[other] otak
}.
