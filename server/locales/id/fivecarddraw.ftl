game-name-fivecarddraw = Poker Five Card Draw

draw-set-starting-chips = Chip awal: { $count }
draw-enter-starting-chips = Masukkan jumlah chip awal
draw-option-changed-starting-chips = Jumlah chip awal diatur menjadi { $count }.
fivecarddraw-desc-starting-chips = Jumlah chip setiap pemain saat memulai Five Card Draw, dari 100 hingga 1.000.000 chip. Bawaan: 20.000.

draw-set-ante = Ante: { $count }
draw-enter-ante = Masukkan jumlah ante
draw-option-changed-ante = Ante diatur menjadi { $count }.
fivecarddraw-desc-ante = Taruhan wajib yang dibayar setiap pemain aktif sebelum setiap ronde. Harus lebih kecil daripada chip awal. Bawaan 100, rentang 0 hingga 1.000.000 chip.

draw-set-turn-timer = Batas waktu giliran: { $mode }
draw-select-turn-timer = Pilih batas waktu giliran
draw-option-changed-turn-timer = Batas waktu giliran diatur menjadi { $mode }.
fivecarddraw-desc-turn-timer = Batas waktu untuk setiap keputusan bertaruh atau menukar kartu: 5, 10, 15, 20, 30, 45, 60, atau 90 detik, atau tanpa batas. Bawaan: tanpa batas.

draw-set-raise-mode = Mode raise: { $mode }
draw-select-raise-mode = Pilih mode raise
draw-option-changed-raise-mode = Mode raise diatur menjadi { $mode }.
fivecarddraw-desc-raise-mode = Aturan batas raise: No limit, Pot limit, atau Double pot limit. Mode yang menggunakan batas pot memerlukan ante lebih dari 0 agar putaran taruhan pertama dapat dimulai. Bawaan: No limit.

draw-set-max-raises = Maksimum raise per putaran taruhan: { $count }
draw-enter-max-raises = Masukkan maksimum raise per putaran taruhan. Isi 0 untuk tanpa batas
draw-option-changed-max-raises = Maksimum raise per putaran taruhan diatur menjadi { $count }.
fivecarddraw-desc-max-raises = Jumlah maksimum raise dalam satu putaran taruhan, dari 0 hingga 10. Isi 0 untuk tanpa batas. Bawaan: 0.

draw-set-draw-limit = Aturan penukaran kartu: { $mode }
draw-select-draw-limit = Pilih aturan penukaran kartu
draw-option-changed-draw-limit = Aturan penukaran kartu diatur menjadi { $mode }.
fivecarddraw-desc-draw-limit = Aturan penukaran: tukar hingga 3 kartu, atau izinkan 4 kartu hanya jika tetap menyimpan As. Bawaan: hingga 3 kartu.
draw-limit-three-cards = Hingga 3 kartu, aturan standar
draw-limit-four-with-ace = Hingga 4 kartu jika menyimpan As

draw-error-ante-too-high = Ante sebesar { $ante } chip harus lebih kecil daripada chip awal sebesar { $chips } chip agar pemain masih dapat mengambil keputusan taruhan setelah kartu dibagikan.
draw-error-capped-mode-needs-ante = { $mode ->
    [pot_limit] Pot limit
    [double_pot] Double pot limit
   *[other] Mode raise berbatas ini
} memerlukan ante lebih dari 0 agar pemain pertama dapat bertaruh berdasarkan jumlah pot.

draw-antes-posted = Ante telah dibayar. Pot kini berisi { $amount } chip.
draw-betting-round-1 = Putaran taruhan pertama.
draw-betting-round-2 = Putaran taruhan kedua.
draw-begin-draw = Tahap penukaran kartu. Dimulai dari pemain aktif pertama di sebelah kiri dealer, pilih kartu untuk ditukar atau simpan semua kartu.
draw-not-draw-phase = Kartu hanya dapat ditukar setelah putaran taruhan pertama. Lanjutkan tindakan taruhan saat ini.
draw-not-betting = Taruhan tidak tersedia pada tahap penukaran kartu. Pilih kartu yang ingin ditukar, lalu pilih Tukar kartu.
draw-fold-not-available = Fold tidak tersedia pada tahap penukaran kartu. Pilih kartu yang ingin ditukar, lalu pilih Tukar kartu.

draw-toggle-discard = Pilih kartu ke-{ $index } untuk ditukar
draw-card-keep = { $card }
draw-card-discard = { $card }, dipilih untuk ditukar
draw-draw-cards = Tukar kartu
draw-draw-cards-count = { $count ->
    [0] Simpan semua kartu
    [one] Tukar 1 kartu
   *[other] Tukar { $count } kartu
}
draw-dealt-cards = Kelima kartu Anda: { $cards }.
draw-you-drew-cards = { $count } { $count ->
    [one] kartu pengganti Anda adalah
   *[other] kartu pengganti Anda adalah
} { $cards }.
draw-you-draw = Anda menukar { $count } { $count ->
    [one] kartu
   *[other] kartu
}.
draw-player-draws = { $player } menukar { $count } { $count ->
    [one] kartu
   *[other] kartu
}.
draw-you-stand-pat = Anda tidak menukar kartu dan menyimpan kelima kartu.
draw-player-stands-pat = { $player } tidak menukar kartu dan menyimpan kelima kartu.
draw-you-discard-limit = Aturan penukaran yang dipilih hanya mengizinkan Anda menukar hingga { $count } kartu.
draw-four-requires-kept-ace = Untuk menukar 4 kartu, Anda harus menyimpan setidaknya satu As. Batalkan pilihan pada As atau tukar paling banyak 3 kartu.

draw-raise-invalid = Masukkan bilangan bulat lebih dari 0 sebagai jumlah kenaikan taruhan.
draw-raise-cap-reached = Batas { $count } kali raise pada putaran taruhan ini telah tercapai. Anda dapat melakukan call atau fold.
draw-raise-over-stack = Anda mencoba menaikkan taruhan sebesar { $requested } chip, tetapi hanya memiliki { $chips } chip. Masukkan kenaikan yang lebih kecil atau pilih All-in.
draw-raise-too-small = Anda mencoba menaikkan taruhan sebesar { $requested } chip. Raise minimum adalah { $minimum } chip.
draw-raise-over-limit = Anda mencoba menaikkan taruhan sebesar { $requested } chip. Dalam { $mode ->
    [pot_limit] mode Pot limit
    [double_pot] mode Double pot limit
   *[other] mode raise yang dipilih
}, kenaikan maksimum setelah call adalah { $maximum } chip.
draw-all-in-over-limit = Anda tidak dapat melakukan all-in dengan sisa { $stack } chip karena { $mode ->
    [pot_limit] mode Pot limit
    [double_pot] mode Double pot limit
   *[other] mode raise yang dipilih
} saat ini hanya mengizinkan kenaikan hingga { $maximum } chip setelah call. Pilih Raise untuk memasukkan jumlah yang diizinkan.
draw-all-in-raise-cap-reached = Anda tidak dapat melakukan all-in sebagai raise penuh karena batas { $count } kali raise telah tercapai. Anda dapat melakukan call atau fold.
draw-all-in-unavailable-raise-cap = All-in tidak tersedia karena akan menjadi raise penuh setelah batas jumlah raise tercapai. Anda dapat melakukan call atau fold.
draw-all-in-unavailable-limit = All-in tidak tersedia karena jumlah chip Anda melebihi batas taruhan saat ini. Pilih Raise untuk memasukkan jumlah yang diizinkan.
draw-raise-unavailable-cap = Raise tidak tersedia karena batas jumlah raise pada putaran taruhan ini telah tercapai.
draw-raise-unavailable-limit = Chip Anda dan batas taruhan saat ini tidak memungkinkan raise penuh. Anda dapat melakukan call, fold, atau All-in jika diizinkan.

draw-current-bet = Taruhan di meja saat ini adalah { $amount } chip.
draw-raise-range = Raise minimum adalah { $minimum } chip. Anda dapat menaikkan taruhan hingga { $maximum } chip setelah call.
draw-no-full-raise-available = Anda memerlukan { $to_call } chip untuk call dan hanya memiliki { $chips } chip, sehingga tidak dapat melakukan raise penuh. Anda dapat melakukan call dengan all-in atau fold.
draw-dealer-unavailable = Posisi dealer untuk ronde ini belum ditentukan.
draw-position-unavailable = Anda tidak aktif dalam ronde ini, sehingga tidak memiliki posisi taruhan.

draw-card-key = Tombol kartu ke-{ $index }

draw-winner-chips = { $rank }. { $player }: { $chips } { $chips ->
    [one] chip
   *[other] chip
}
