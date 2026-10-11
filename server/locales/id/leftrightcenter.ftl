game-name-leftrightcenter = Kiri Tengah Kanan

lrc-roll = Lempar { $count } { $count ->
    [one] dadu
   *[other] dadu
}
lrc-roll-label = Lempar dadu
lrc-face-left = Kiri
lrc-face-center = Tengah
lrc-face-right = Kanan
lrc-face-dot = Titik
lrc-you-roll = Hasil lemparan Anda: { $results }.
lrc-player-rolls = Hasil lemparan { $player }: { $results }.
lrc-you-roll-brief = Anda: { $results }.
lrc-player-rolls-brief = { $player }: { $results }.
lrc-you-pass-left = Anda memberikan { $count } { $count ->
    [one] chip
   *[other] chip
} ke kiri kepada { $target }. Anda memiliki sisa { $remaining }. { $target } sekarang memiliki { $target_total }.
lrc-player-passes-left = { $player } memberikan { $count } { $count ->
    [one] chip
   *[other] chip
} ke kiri kepada { $target }. { $player } memiliki sisa { $remaining }. { $target } sekarang memiliki { $target_total }.
lrc-you-pass-left-brief = Anda memberikan { $count } chip ke kiri kepada { $target }. Sisa: { $remaining }.
lrc-player-passes-left-brief = { $player } memberikan { $count } chip ke kiri kepada { $target }. Sisa: { $remaining }.
lrc-you-pass-right = Anda memberikan { $count } { $count ->
    [one] chip
   *[other] chip
} ke kanan kepada { $target }. Anda memiliki sisa { $remaining }. { $target } sekarang memiliki { $target_total }.
lrc-player-passes-right = { $player } memberikan { $count } { $count ->
    [one] chip
   *[other] chip
} ke kanan kepada { $target }. { $player } memiliki sisa { $remaining }. { $target } sekarang memiliki { $target_total }.
lrc-you-pass-right-brief = Anda memberikan { $count } chip ke kanan kepada { $target }. Sisa: { $remaining }.
lrc-player-passes-right-brief = { $player } memberikan { $count } chip ke kanan kepada { $target }. Sisa: { $remaining }.
lrc-you-pass-center = Anda meletakkan { $count } { $count ->
    [one] chip
   *[other] chip
} di tengah. Anda memiliki sisa { $remaining }. Jumlah di tengah sekarang { $center }.
lrc-player-passes-center = { $player } meletakkan { $count } { $count ->
    [one] chip
   *[other] chip
} di tengah. { $player } memiliki sisa { $remaining }. Jumlah di tengah sekarang { $center }.
lrc-you-pass-center-brief = Anda meletakkan { $count } chip di tengah. Sisa: { $remaining }. Total di tengah: { $center }.
lrc-player-passes-center-brief = { $player } meletakkan { $count } chip di tengah. Sisa: { $remaining }. Total di tengah: { $center }.
lrc-you-keep-all = Semua dadu Anda menunjukkan titik, jadi Anda tetap memiliki seluruh { $count } { $count ->
    [one] chip
   *[other] chip
}.
lrc-player-keeps-all = Semua dadu { $player } menunjukkan titik, jadi ia tetap memiliki seluruh { $count } { $count ->
    [one] chip
   *[other] chip
}.
lrc-you-keep-all-brief = Anda: tidak ada chip yang berpindah. { $count } { $count ->
    [one] chip
   *[other] chip
}.
lrc-player-keeps-all-brief = { $player }: tidak ada chip yang berpindah. { $count } { $count ->
    [one] chip
   *[other] chip
}.
lrc-you-skip-no-chips = Anda tidak memiliki chip, jadi giliran Anda dilewati. Anda tetap ikut bermain dan dapat menerima chip dari pemain di kiri atau kanan Anda.
lrc-player-skips-no-chips = { $player } tidak memiliki chip, jadi gilirannya dilewati. Ia tetap ikut bermain dan dapat menerima chip dari pemain di kiri atau kanannya.
lrc-you-skip-no-chips-brief = Anda: tidak ada chip. Giliran dilewati.
lrc-player-skips-no-chips-brief = { $player }: tidak ada chip. Giliran dilewati.
lrc-you-win = Anda satu-satunya pemain yang masih memiliki chip dan menang dengan sisa { $count }. Anda mengambil { $center } { $center ->
    [one] chip
   *[other] chip
} di tengah.
lrc-player-wins = { $player } satu-satunya pemain yang masih memiliki chip dan menang dengan sisa { $count }. { $center } { $center ->
    [one] chip
   *[other] chip
} di tengah menjadi miliknya.
lrc-you-win-brief = Anda menang. Chip Anda: { $count }. Di tengah: { $center }.
lrc-player-wins-brief = { $player } menang. Chip: { $count }. Di tengah: { $center }.
lrc-roll-already-resolving = Hasil lemparan Anda sedang diselesaikan. Tunggu hingga pemindahan chip selesai.
lrc-no-chips-to-roll = Anda tidak memiliki chip untuk melempar dadu. Giliran Anda akan dilewati secara otomatis.
lrc-center-pot = Kumpulan di tengah: { $count } { $count ->
    [one] chip
   *[other] chip
}.
lrc-check-center = Periksa chip di tengah
lrc-check-last-roll = Periksa lemparan terakhir
lrc-last-roll-none = Belum ada dadu yang dilempar.
lrc-last-roll-you = Hasil lemparan terakhir Anda adalah { $results }.
lrc-last-roll-player = Hasil lemparan terakhir { $player } adalah { $results }.
lrc-set-starting-chips = Chip awal: { $count }
lrc-enter-starting-chips = Masukkan jumlah chip awal:
lrc-option-changed-starting-chips = Jumlah chip awal diatur menjadi { $count }.
leftrightcenter-desc-starting-chips = Jumlah chip yang dimiliki setiap pemain Kiri Tengah Kanan saat permainan dimulai. Nilai bawaan 3, rentang 1 hingga 10.
lrc-error-starting-chips-invalid = Jumlah chip awal harus antara { $min } dan { $max }. Nilai saat ini adalah { $count }.
lrc-line-format = { $player }: { $chips } { $chips ->
    [one] chip
   *[other] chip
}
