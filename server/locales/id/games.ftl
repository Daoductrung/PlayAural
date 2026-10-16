game-round-start = Ronde { $round }.
game-round-end = Ronde { $round } selesai.
game-turn-start = Giliran { $player }.
game-turn-start-you = Giliran Anda.
game-turn-start-player = Giliran { $player }.
game-no-turn = Saat ini belum ada giliran.

game-score-line = { $player }: { $score } { $unit }
game-score-line-target = { $player }: { $score } dari { $target } { $unit }
game-score-unit-points = { $count ->
    [one] poin
   *[other] poin
}
game-score-unit-chips = { $count ->
    [one] chip
   *[other] chip
}
game-score-unit-coins = { $count ->
    [one] koin
   *[other] koin
}
game-score-unit-health = kesehatan
game-score-unit-ninetynine-tokens = { $count ->
    [one] token
   *[other] token
}
game-score-unit-tokens-home = { $count ->
    [one] bidak sampai di tujuan
   *[other] bidak sampai di tujuan
}
game-score-unit-pawns-home = { $count ->
    [one] bidak sampai di tujuan
   *[other] bidak sampai di tujuan
}
game-score-unit-hand-wins = { $count ->
    [one] ronde dimenangkan
   *[other] ronde dimenangkan
}
game-score-unit-light = cahaya
game-final-scores-header = Skor Akhir:

game-winner = { $player } menang!
game-winner-you = Anda menang!
game-winner-score = { $player } menang dengan { $score } poin!
game-tiebreaker = Hasilnya seri! Lanjut ke ronde penentuan!
game-eliminated = { $player } tersingkir dengan { $score } poin.

game-set-target-score = Target skor: { $score }
game-enter-target-score = Masukkan target skor:
game-option-changed-target = Target skor diatur menjadi { $score }.

game-set-team-mode = Mode tim: { $mode }
game-select-team-mode = Pilih mode tim
game-option-changed-team = Mode tim diatur menjadi { $mode }.
game-team-mode-individual = Perorangan
game-team-mode-x-teams-of-y = { $num_teams } tim, masing-masing { $team_size } pemain
game-team-name = Tim { $index }
team-arrangement-started = Penyusunan tim dimulai. Periksa susunan tim, tukar anggota jika perlu, lalu konfirmasikan untuk memulai permainan.
team-arrangement-confirm = Konfirmasikan tim dan mulai
team-arrangement-read = Bacakan susunan tim
team-arrangement-select-member-action = Pilih anggota tim
team-arrangement-select-member = Pilih anggota tim
team-arrangement-select-swap-target = Pilih pemain yang akan ditukar
team-arrangement-swap-member = Pilih pemain yang akan ditukar
team-arrangement-swap-member-selected = Tukar { $player } dengan...
team-arrangement-cancel = Batalkan penyusunan tim
team-arrangement-line = { $team }: { $members }
team-arrangement-turn-order = Urutan giliran: { $players }
team-arrangement-member-option = { $player }, { $team }, { $selected }
team-arrangement-selected = dipilih
team-arrangement-not-selected = belum dipilih
team-arrangement-member-selected = { $player } dari { $team } dipilih. Pilih pemain dari tim lain untuk bertukar tim.
team-arrangement-swapped-player = { $player } menukar { $first } dan { $second } antartim.
team-arrangement-swapped-you = Anda menukar { $first } dan { $second } antartim.
team-arrangement-cancelled = Penyusunan tim dibatalkan.
team-arrangement-cancelled-roster = Penyusunan tim dibatalkan karena daftar pemain berubah.
team-arrangement-refreshed = Daftar pemain berubah. Susunan tim telah diperbarui.
team-arrangement-in-progress = Selesaikan atau batalkan penyusunan tim terlebih dahulu.
team-arrangement-not-active = Penyusunan tim sedang tidak berlangsung.
team-arrangement-select-first = Pilih anggota tim terlebih dahulu.
team-arrangement-player-missing = Pemain itu sudah tidak tersedia untuk penyusunan tim.
team-arrangement-same-team = Pilih pemain dari tim lain.
team-arrangement-swap-failed = Anggota tim tersebut tidak dapat ditukar.

status-box-closed = Informasi status ditutup.

game-leave = Keluar dari permainan

round-timer-paused = { $player } menjeda permainan. Tekan p untuk memulai ronde berikutnya.
round-timer-paused-you = Anda menjeda permainan. Tekan p untuk memulai ronde berikutnya.
dice-keeping = Dadu { $value } dipertahankan.
dice-rerolling = Dadu { $value } akan dilempar ulang.
dice-locked = Dadu itu terkunci dan tidak dapat diubah.
dice-status-label-locked = { $value } (terkunci)
dice-status-label-kept = { $value } (dipertahankan)

game-deal-counter = Pembagian kartu { $current } dari { $total }.
game-you-deal = Anda membagikan kartu.
game-player-deals = { $player } membagikan kartu.

card-name = { $rank } { $suit }
no-cards = Tidak ada kartu

suit-diamonds = wajik
suit-clubs = keriting
suit-hearts = hati
suit-spades = sekop

rank-ace = As
rank-two = 2
rank-three = 3
rank-four = 4
rank-five = 5
rank-six = 6
rank-seven = 7
rank-eight = 8
rank-nine = 9
rank-ten = 10
rank-jack = Jack
rank-queen = Queen
rank-king = King

rank-ace-plural = As
rank-two-plural = 2
rank-three-plural = 3
rank-four-plural = 4
rank-five-plural = 5
rank-six-plural = 6
rank-seven-plural = 7
rank-eight-plural = 8
rank-nine-plural = 9
rank-ten-plural = 10
rank-jack-plural = Jack
rank-queen-plural = Queen
rank-king-plural = King

poker-high-card-with = Kartu tertinggi { $high }, dengan { $rest }
poker-high-card = Kartu tertinggi { $high }
poker-pair-with = Pair { $pair }, dengan { $rest }
poker-pair = Pair { $pair }
poker-two-pair-with = Two Pair, { $high } dan { $low }, dengan { $kicker }
poker-two-pair = Two Pair, { $high } dan { $low }
poker-trips-with = Three of a Kind, { $trips }, dengan { $rest }
poker-trips = Three of a Kind, { $trips }
poker-straight-high = Straight dengan kartu tertinggi { $high }
poker-flush-high-with = Flush dengan kartu tertinggi { $high }, dengan { $rest }
poker-full-house = Full House, tiga { $trips } dan sepasang { $pair }
poker-quads-with = Four of a Kind, { $quads }, dengan { $kicker }
poker-quads = Four of a Kind, { $quads }
poker-royal-flush = Royal Flush
poker-straight-flush-high = Straight Flush dengan kartu tertinggi { $high }
poker-unknown-hand = Kombinasi kartu tidak diketahui

game-error-invalid-team-mode = Mode tim yang dipilih tidak sesuai dengan jumlah pemain saat ini.

documentation-menu = Dokumentasi
introduction = Pengantar
community-rules = Aturan Komunitas
global-keys = Kontrol Umum
game-rules = Aturan Permainan
changelog = Riwayat Perubahan
donation = Donasi
contact = Kontak
document-not-found = Dokumen tidak ditemukan.
help = Bantuan

# Game Info (Ctrl+I)
game-info = Informasi Permainan
game-info-header = Informasi Permainan Saat Ini
game-info-name = Permainan: { $game }
game-info-players = Pemain: { $count }
game-info-host = Pemilik meja: { $host }
game-info-status = Status: { $status }
game-info-status-waiting = Menunggu di lobi
game-info-status-playing = Sedang berlangsung
game-info-options-header = Pengaturan:
game-info-no-options = Permainan ini tidak memiliki pengaturan khusus.

# How to Play (Ctrl+F1)
how-to-play = Cara Bermain
game-rules-not-available = Aturan untuk { $game } belum tersedia.

# Compatibility strings retained until the public runtime adopts the newer message ids.
team-arrangement-swapped = { $first } dan { $second } telah bertukar tim.
