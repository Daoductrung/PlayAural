game-name-backgammon = Backgammon
backgammon-color-red = merah
backgammon-color-white = putih
backgammon-game-started = { $red } memegang Merah, { $white } memegang Putih.
backgammon-game-started-you-red = Anda memegang Merah. { $opponent } memegang Putih.
backgammon-game-started-you-white = Anda memegang Putih. { $opponent } memegang Merah.
backgammon-opening-roll = Lemparan pembuka: { $red } mendapat { $red_die }, { $white } mendapat { $white_die }.
backgammon-opening-roll-you = Lemparan pembuka: Anda mendapat { $your_die }, { $opponent } mendapat { $opponent_die }.
backgammon-opening-tie = Keduanya mendapat { $die }. Dadu dilempar ulang.
backgammon-opening-winner-you = Anda mendapat giliran pertama dengan dadu { $die1 } dan { $die2 }.
backgammon-opening-winner-player = { $player } mendapat giliran pertama dengan dadu { $die1 } dan { $die2 }.
backgammon-roll-you = Anda melempar dadu dan mendapat { $die1 } dan { $die2 }.
backgammon-roll-player = { $player } melempar dadu dan mendapat { $die1 } dan { $die2 }.
backgammon-no-moves-you = Anda tidak memiliki langkah yang sah. Giliran Anda berakhir.
backgammon-no-moves-player = { $player } tidak memiliki langkah yang sah. Gilirannya berakhir.
backgammon-brief-move-normal = { $is_self ->
    [yes] Anda: { $src } ke { $dest }.
    *[no] { $player }: { $src } ke { $dest }.
}
backgammon-brief-move-hit = { $is_self ->
    [yes] Anda: { $src } ke { $dest }, menangkap bidak { $opponent }.
    [spectator] { $player }: { $src } ke { $dest }, menangkap bidak { $opponent }.
    *[no] { $player }: { $src } ke { $dest }, menangkap bidak Anda.
}
backgammon-brief-move-bar = { $is_self ->
    [yes] Anda: bar ke { $dest }.
    *[no] { $player }: bar ke { $dest }.
}
backgammon-brief-move-bar-hit = { $is_self ->
    [yes] Anda: bar ke { $dest }, menangkap bidak { $opponent }.
    [spectator] { $player }: bar ke { $dest }, menangkap bidak { $opponent }.
    *[no] { $player }: bar ke { $dest }, menangkap bidak Anda.
}
backgammon-brief-move-bearoff = { $is_self ->
    [yes] Anda: keluar dari { $src }.
    *[no] { $player }: keluar dari { $src }.
}
backgammon-verbose-move-normal = { $is_self ->
    [yes] Anda memindahkan bidak dari petak { $src } ke petak { $dest }.
    *[no] { $player } memindahkan bidak dari petak { $src } ke petak { $dest }.
} { $src_count ->
    [0] Petak { $src } kini kosong. Ada { $dest_count } bidak di petak { $dest }.
    *[other] Kini ada { $src_count } bidak di petak { $src } dan { $dest_count } di petak { $dest }.
}
backgammon-verbose-move-hit = { $is_self ->
    [yes] Anda memindahkan bidak dari petak { $src } untuk menangkap bidak { $opponent } di petak { $dest }.
    [spectator] { $player } memindahkan bidak dari petak { $src } untuk menangkap bidak { $opponent } di petak { $dest }.
    *[no] { $player } memindahkan bidak dari petak { $src } untuk menangkap bidak Anda di petak { $dest }.
} { $src_count ->
    [0] Petak { $src } kini kosong.
    *[other] Tersisa { $src_count } bidak di petak { $src }.
}
backgammon-verbose-move-bar = { $is_self ->
    [yes] Anda memasukkan bidak dari bar ke petak { $dest }.
    *[no] { $player } memasukkan bidak dari bar ke petak { $dest }.
} Kini ada { $dest_count } bidak di petak { $dest }.
backgammon-verbose-move-bar-hit = { $is_self ->
    [yes] Anda memasukkan bidak dari bar untuk menangkap bidak { $opponent } di petak { $dest }.
    [spectator] { $player } memasukkan bidak dari bar untuk menangkap bidak { $opponent } di petak { $dest }.
    *[no] { $player } memasukkan bidak dari bar untuk menangkap bidak Anda di petak { $dest }.
}
backgammon-verbose-move-bearoff = { $is_self ->
    [yes] Anda mengeluarkan bidak dari petak { $src }.
    *[no] { $player } mengeluarkan bidak dari petak { $src }.
} { $src_count ->
    [0] Petak { $src } kini kosong.
    *[other] Tersisa { $src_count } bidak di petak { $src }.
}
backgammon-doubles-you = Anda menawarkan penggandaan nilai kubus menjadi { $value }.
backgammon-doubles-player = { $player } menawarkan penggandaan nilai kubus menjadi { $value }.
backgammon-accepts-you = Anda menerima penggandaan dan menjadi pemilik kubus.
backgammon-accepts-player = { $player } menerima penggandaan dan menjadi pemilik kubus.
backgammon-drops-you = Anda menolak penggandaan dan menyerah dengan nilai kubus saat ini.
backgammon-drops-player = { $player } menolak penggandaan dan menyerah dengan nilai kubus saat ini.
backgammon-accept = Terima
backgammon-drop = Tolak dan menyerah
backgammon-point-empty = { $point }
backgammon-point-occupied = { $point } { $color }, { $count }
backgammon-point-occupied-selected = { $point } { $color }, { $count }, dipilih
backgammon-point-occupied-selected-bearoff = { $point } { $color }, { $count }, dipilih. Aktifkan lagi untuk mengeluarkan bidak
backgammon-label-double = Gandakan
backgammon-label-roll = Lempar dadu
backgammon-label-undo = Batalkan langkah
backgammon-label-deselect = Batalkan pilihan
backgammon-label-next-destination = Tujuan berikutnya
backgammon-label-previous-destination = Tujuan sebelumnya
backgammon-no-checkers-there = Tidak ada bidak di sana.
backgammon-not-your-checkers = Itu bukan bidak Anda.
backgammon-no-moves-from-here = Tidak ada langkah yang sah dari sini.
backgammon-must-enter-from-bar = Masukkan bidak dari bar terlebih dahulu.
backgammon-illegal-move = Langkah tidak sah.
backgammon-no-dice-remaining = Tidak ada dadu yang tersisa untuk digunakan pada giliran ini.
backgammon-no-checkers-on-bar = Tidak ada bidak Anda di bar yang perlu dimasukkan.
backgammon-invalid-destination = Tujuan itu bukan petak Backgammon yang dapat dimainkan.
backgammon-source-empty = Tidak ada bidak di petak { $point } yang dapat dipindahkan.
backgammon-source-opponent = Petak { $point } berisi bidak lawan.
backgammon-destination-blocked = Petak { $point } terhalang oleh { $count } bidak lawan.
backgammon-bar-entry-blocked = Anda tidak dapat masuk ke petak { $point } karena terhalang oleh { $count } bidak lawan.
backgammon-no-die-for-bar-entry = Tidak ada dadu tersisa ({ $dice }) yang dapat digunakan untuk masuk ke petak { $point }.
backgammon-no-die-for-destination = Tidak ada dadu tersisa ({ $dice }) yang dapat digunakan untuk berpindah dari petak { $src } ke petak { $dest }.
backgammon-must-use-forced-die = Anda harus menggunakan { $dice } sekarang. Aturan Backgammon mewajibkan penggunaan kedua dadu jika memungkinkan, atau dadu yang lebih besar jika hanya satu yang dapat dimainkan.
backgammon-move-would-waste-die = Langkah itu akan menghalangi penggunaan dadu sebanyak yang diwajibkan aturan. Pilih langkah sah lainnya.
backgammon-bearoff-not-home = Anda belum dapat mengeluarkan bidak. Bidak di luar area rumah: { $outside }. Bidak di bar: { $bar }. Bawa semua bidak ke petak 1 hingga 6 dan kosongkan bar terlebih dahulu.
backgammon-bearoff-outside-home-point = Petak { $point } berada di luar area rumah Anda. Hanya bidak di petak 1 hingga 6 yang dapat dikeluarkan.
backgammon-bearoff-blocked = Anda tidak dapat mengeluarkan bidak dari petak { $point } dengan dadu { $die } karena masih ada bidak di petak { $blocking_point }.
backgammon-bearoff-no-die = Anda tidak dapat mengeluarkan bidak dari petak { $point } dengan dadu yang tersisa ({ $die }).
backgammon-nothing-to-undo = Tidak ada langkah yang dapat dibatalkan.
backgammon-undo-move = { $listener ->
    [actor] Anda membatalkan langkah dari { $source } ke { $destination }.
    *[observer] { $player } membatalkan langkah dari { $source } ke { $destination }.
}
backgammon-undo-hit = { $listener ->
    [actor] Anda membatalkan langkah dari { $source } ke { $destination } dan mengembalikan bidak { $opponent }.
    [target] { $player } membatalkan langkah dari { $source } ke { $destination } dan mengembalikan bidak Anda.
    *[observer] { $player } membatalkan langkah dari { $source } ke { $destination } dan mengembalikan bidak { $opponent }.
}
backgammon-selection-cleared = Pilihan bidak dibatalkan.
backgammon-no-selection = Belum ada bidak yang dipilih.
backgammon-cannot-double = Anda tidak dapat menggandakan nilai kubus sekarang.
backgammon-double-single-game = Kubus pengganda tidak digunakan dalam permainan tunggal.
backgammon-double-crawford = Ini adalah permainan Crawford. Kubus pengganda tidak tersedia.
backgammon-double-dead-cube = Kemenangan dengan nilai kubus saat ini sudah cukup untuk memenangkan pertandingan. Kubus tidak lagi berguna bagi Anda dan tidak boleh digandakan.
backgammon-double-cube-owned = Kubus dimiliki { $opponent }. Hanya pemiliknya yang boleh menawarkan penggandaan berikutnya.
backgammon-double-cube-owned-unknown = Kubus dimiliki lawan. Anda tidak dapat menawarkan penggandaan berikutnya.
backgammon-double-before-roll-only = Anda hanya boleh menawarkan penggandaan pada awal giliran, sebelum melempar dadu.
backgammon-cannot-undo = Tidak ada langkah yang dapat dibatalkan.
backgammon-not-doubling-phase = Tidak ada tawaran penggandaan untuk dijawab.
backgammon-need-roll-first = Lempar dadu sebelum memindahkan bidak.
backgammon-roll-before-moving-only = Anda hanya boleh melempar dadu pada awal giliran, sebelum memindahkan bidak.
backgammon-confirm-drop-double = Menolak berarti menyerah dalam permainan ini dengan nilai kubus saat ini. Tekan Tolak dan menyerah sekali lagi dalam { $seconds } detik untuk mengonfirmasi.
backgammon-check-status = Status
backgammon-check-cube = Kubus
backgammon-check-pip = Sisa jarak
backgammon-check-dice = Dadu
backgammon-check-legal-moves = Langkah yang sah
backgammon-status = { $red_self ->
    [yes] Anda, Merah
    *[no] { $red }, Merah
}. Di bar: { $bar_red }, di luar area rumah: { $outside_red }, sudah keluar: { $off_red }. { $white_self ->
    [yes] Anda, Putih
    *[no] { $white }, Putih
}. Di bar: { $bar_white }, di luar area rumah: { $outside_white }, sudah keluar: { $off_white }.
backgammon-dice = { $is_self ->
    [yes] Dadu Anda yang tersisa: { $dice }.
    *[no] Dadu { $player } yang tersisa: { $dice }.
}
backgammon-dice-none = Tidak ada dadu.
backgammon-no-dice-list = tidak ada
backgammon-cube-status = Nilai kubus { $value }. { $owner ->
    [center] Kubus di tengah. Kedua pemain boleh menawarkan penggandaan.
    [self] Anda memiliki kubus.
    *[other] Kubus dimiliki { $owner }.
} { $can_double ->
    [yes] Penggandaan dapat ditawarkan sekarang.
    [crawford] Ini adalah permainan Crawford. Penggandaan tidak diperbolehkan.
    [dead] Kubus tidak lagi berguna bagi pemain yang mendapat giliran karena nilainya sudah cukup untuk memenangkan pertandingan.
    *[no] Penggandaan belum dapat ditawarkan.
}
backgammon-cube-no-match = Tidak ada kubus pengganda dalam permainan tunggal.
backgammon-pip-count = { $red_self ->
    [yes] Anda, Merah
    *[no] { $red }, Merah
}: { $red_pip } langkah. { $white_self ->
    [yes] Anda, Putih
    *[no] { $white }, Putih
}: { $white_pip } langkah.
backgammon-match-score-line = { $is_self ->
    [yes] Anda: { $score } dari { $match_length }.
    *[no] { $player }: { $score } dari { $match_length }.
}
backgammon-match-score-cube-line = Kubus: { $cube }.
backgammon-legal-moves-awaiting-roll = { $is_self ->
    [yes] Anda harus melempar dadu sebelum dapat memindahkan bidak.
    *[no] { $player } harus melempar dadu sebelum dapat memindahkan bidak.
}
backgammon-legal-moves-awaiting-double-response = { $is_self ->
    [yes] Anda harus menerima atau menolak penggandaan sebelum permainan dilanjutkan.
    *[no] { $player } harus menerima atau menolak penggandaan sebelum permainan dilanjutkan.
}
backgammon-legal-moves-none = { $is_self ->
    [yes] Anda tidak memiliki langkah bidak yang sah.
    *[no] { $player } tidak memiliki langkah bidak yang sah.
}
backgammon-move-source-bar = bar
backgammon-move-destination-off = keluar papan
backgammon-legal-move-line = { $is_self ->
    [yes] Anda: { $source } ke { $destination } dengan dadu { $die }
    *[no] { $player }: { $source } ke { $destination } dengan dadu { $die }
}{ $hit ->
    [yes] , menangkap bidak yang sendirian.
    *[no] .
}
backgammon-wins-game-you = Anda mendapat { $points } poin{ $points ->
    [one] {""}
    *[other] {""}
}. { $result ->
    [single] Kemenangan biasa dengan nilai kubus { $cube }.
    [gammon] Gammon dengan nilai kubus { $cube }.
    [backgammon] Backgammon dengan nilai kubus { $cube }.
    *[drop] Lawan Anda menolak penggandaan saat nilai kubus { $cube }.
}
backgammon-wins-game-player = { $player } mendapat { $points } poin{ $points ->
    [one] {""}
    *[other] {""}
}. { $result ->
    [single] Kemenangan biasa dengan nilai kubus { $cube }.
    [gammon] Gammon dengan nilai kubus { $cube }.
    [backgammon] Backgammon dengan nilai kubus { $cube }.
    *[drop] Lawannya menolak penggandaan saat nilai kubus { $cube }.
}
backgammon-new-game = Memulai permainan ke-{ $number }.
backgammon-match-winner-you = Anda memenangkan pertandingan!
backgammon-match-winner-player = { $player } memenangkan pertandingan!
backgammon-end-score = { $red } { $red_score }, { $white } { $white_score }. Target pertandingan { $match_length } poin.
backgammon-crawford = Permainan Crawford. Penggandaan tidak diperbolehkan pada permainan ini.
backgammon-difficulty-random = Acak
backgammon-difficulty-simple = Sederhana
backgammon-option-match-length = Target pertandingan: { $match_length }
backgammon-option-select-match-length = Atur target pertandingan (1 hingga 25)
backgammon-option-changed-match-length = Target pertandingan diatur menjadi { $match_length }.
backgammon-desc-match-length = Jumlah poin untuk memenangkan pertandingan Backgammon. Nilai 1 berarti satu permainan tanpa kubus pengganda. Bawaan 1, rentang 1 hingga 25.
backgammon-option-bot-difficulty = Tingkat kesulitan bot: { $bot_difficulty }
backgammon-option-select-bot-difficulty = Pilih tingkat kesulitan bot
backgammon-option-changed-bot-difficulty = Tingkat kesulitan bot diatur menjadi { $bot_difficulty }.
backgammon-desc-bot-difficulty = Tentukan cara bot memilih langkah. Acak memilih langkah sah secara acak, sedangkan Sederhana mengutamakan langkah yang lebih menguntungkan secara taktis.
