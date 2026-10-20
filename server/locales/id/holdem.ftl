game-name-holdem = Poker Texas Hold'em

holdem-set-starting-chips = Chip awal: { $count }
holdem-enter-starting-chips = Masukkan jumlah chip awal
holdem-option-changed-starting-chips = Jumlah chip awal diatur menjadi { $count }.
holdem-desc-starting-chips = Jumlah chip setiap pemain saat memulai Texas Hold'em, dari 100 hingga 1.000.000 chip. Bawaan: 20.000.

holdem-set-big-blind = Big blind: { $count }
holdem-enter-big-blind = Masukkan jumlah big blind
holdem-option-changed-big-blind = Big blind diatur menjadi { $count }.
holdem-desc-big-blind = Jumlah dasar big blind. Harus lebih kecil daripada chip awal. Bawaan 200, rentang 1 hingga 1.000.000 chip.

holdem-set-ante = Ante: { $count }
holdem-enter-ante = Masukkan jumlah ante
holdem-option-changed-ante = Ante diatur menjadi { $count }.
holdem-desc-ante = Taruhan wajib yang dibayar setiap pemain aktif setelah ante mulai berlaku, dari 0 hingga 1.000.000 chip. Bawaan: 0.

holdem-set-ante-start = Ante mulai pada level: { $count }
holdem-enter-ante-start = Masukkan level blind saat ante mulai berlaku
holdem-option-changed-ante-start = Level awal ante diatur menjadi { $count }.
holdem-desc-ante-start-level = Level blind saat ante mulai berlaku. Jika diatur ke 0 dan ante lebih dari 0, ante berlaku sejak ronde pertama. Bawaan 0, rentang 0 hingga 20.

holdem-set-turn-timer = Batas waktu giliran: { $mode }
holdem-select-turn-timer = Pilih batas waktu giliran
holdem-option-changed-turn-timer = Batas waktu giliran diatur menjadi { $mode }.
holdem-desc-turn-timer = Batas waktu untuk setiap keputusan dalam Hold'em: 5, 10, 15, 20, 30, 45, 60, atau 90 detik, atau tanpa batas. Bawaan: tanpa batas.

holdem-set-blind-timer = Waktu kenaikan blind: { $mode }
holdem-select-blind-timer = Pilih waktu kenaikan blind
holdem-option-changed-blind-timer = Waktu kenaikan blind diatur menjadi { $mode }.
holdem-desc-blind-timer = Jeda antara kenaikan blind: 5, 10, 15, 20, atau 30 menit. Bawaan: 20 menit.

holdem-set-raise-mode = Mode raise: { $mode }
holdem-select-raise-mode = Pilih mode raise
holdem-option-changed-raise-mode = Mode raise diatur menjadi { $mode }.
holdem-desc-raise-mode = Aturan batas raise: No limit, Pot limit, atau Double pot limit. Bawaan: No limit.

holdem-set-max-raises = Maksimum raise per putaran taruhan: { $count }
holdem-enter-max-raises = Masukkan maksimum raise per putaran taruhan. Isi 0 untuk tanpa batas
holdem-option-changed-max-raises = Maksimum raise per putaran taruhan diatur menjadi { $count }.
holdem-desc-max-raises = Jumlah maksimum raise dalam satu putaran taruhan, dari 0 hingga 10. Isi 0 untuk tanpa batas. Bawaan: 0.

holdem-error-big-blind-too-high = Big blind sebesar { $blind } chip harus lebih kecil daripada chip awal sebesar { $chips } chip.
holdem-error-ante-too-high = Ante sebesar { $ante } chip harus lebih kecil daripada chip awal sebesar { $chips } chip.
holdem-error-forced-bets-too-high = Jika ante berlaku sejak level 0, jumlah ante dan big blind, yaitu { $ante } ditambah { $blind } chip, harus lebih kecil daripada chip awal sebesar { $chips } chip.

holdem-antes-posted = Ante telah dibayar. Pot kini berisi { $amount } chip.
holdem-you-post-small-blind = Anda membayar small blind sebesar { $sb } chip. { $bb_player } membayar big blind sebesar { $bb } chip.
holdem-you-post-big-blind = { $sb_player } membayar small blind sebesar { $sb } chip. Anda membayar big blind sebesar { $bb } chip.
holdem-players-post-blinds = { $sb_player } membayar small blind sebesar { $sb } chip. { $bb_player } membayar big blind sebesar { $bb } chip.

holdem-raise-invalid = Masukkan bilangan bulat lebih dari 0 sebagai jumlah kenaikan taruhan.
holdem-raise-cap-reached = Batas { $count } kali raise pada putaran taruhan ini telah tercapai. Anda dapat melakukan call atau fold.
holdem-raise-over-stack = Anda mencoba menaikkan taruhan sebesar { $requested } chip, tetapi hanya memiliki { $chips } chip. Masukkan kenaikan yang lebih kecil atau pilih All-in.
holdem-raise-too-small = Anda mencoba menaikkan taruhan sebesar { $requested } chip. Raise minimum adalah { $minimum } chip.
holdem-raise-over-limit = Anda mencoba menaikkan taruhan sebesar { $requested } chip. Dalam { $mode ->
    [pot_limit] mode Pot limit
    [double_pot] mode Double pot limit
   *[other] mode raise yang dipilih
}, kenaikan maksimum setelah call adalah { $maximum } chip.
holdem-all-in-over-limit = Anda tidak dapat melakukan all-in dengan sisa { $stack } chip karena { $mode ->
    [pot_limit] mode Pot limit
    [double_pot] mode Double pot limit
   *[other] mode raise yang dipilih
} saat ini hanya mengizinkan kenaikan hingga { $maximum } chip setelah call. Pilih Raise untuk memasukkan jumlah yang diizinkan.
holdem-all-in-raise-cap-reached = Anda tidak dapat melakukan all-in sebagai raise penuh karena batas { $count } kali raise telah tercapai. Anda dapat melakukan call atau fold.
holdem-all-in-unavailable-raise-cap = All-in tidak tersedia karena akan menjadi raise penuh setelah batas jumlah raise tercapai. Anda dapat melakukan call atau fold.
holdem-all-in-unavailable-limit = All-in tidak tersedia karena jumlah chip Anda melebihi batas taruhan saat ini. Pilih Raise untuk memasukkan jumlah yang diizinkan.
holdem-raise-unavailable-cap = Raise tidak tersedia karena batas jumlah raise pada putaran taruhan ini telah tercapai.
holdem-raise-unavailable-limit = Chip Anda dan batas taruhan saat ini tidak memungkinkan raise penuh. Anda dapat melakukan call, fold, atau All-in jika diizinkan.

holdem-current-bet = Taruhan di meja saat ini adalah { $amount } chip.
holdem-raise-range = Raise minimum adalah { $minimum } chip. Anda dapat menaikkan taruhan hingga { $maximum } chip setelah call.
holdem-no-full-raise-available = Anda memerlukan { $to_call } chip untuk call dan hanya memiliki { $chips } chip, sehingga tidak dapat melakukan raise penuh. Anda dapat melakukan call dengan all-in atau fold.
holdem-button-unavailable = Posisi button untuk ronde ini belum ditentukan.
holdem-position-unavailable = Anda tidak aktif dalam ronde ini, sehingga tidak memiliki posisi taruhan.
holdem-reveal-no-live-hand = Anda hanya dapat membuka kartu pribadi jika masih bertahan hingga showdown.
holdem-private-hand-unavailable = Anda kehabisan chip dan tidak lagi memiliki kartu dalam ronde ini untuk dibaca.

holdem-winner-chips = { $rank }. { $player }: { $chips } { $chips ->
    [one] chip
   *[other] chip
}
