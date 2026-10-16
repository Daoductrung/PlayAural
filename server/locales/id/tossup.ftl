game-name-tossup = Toss Up

tossup-roll-first =
    Lempar { $count } { $count ->
        [one] dadu
       *[other] dadu
    }
tossup-roll-remaining =
    Lempar { $count } { $count ->
        [one] dadu yang tersisa
       *[other] dadu yang tersisa
    }
tossup-bank =
    Amankan { $points } { $points ->
        [one] poin
       *[other] poin
    }
tossup-check-turn-status = Periksa status giliran
tossup-game-start = Toss Up dimulai dengan aturan { $rules }, { $dice } dadu per set, dan batas target { $target }. Lampaui batas tersebut dan selesaikan giliran yang tersisa untuk menang.
tossup-game-start-brief = Toss Up dimulai. Lampaui { $target } poin.
tossup-round-start = Ronde { $round } dimulai.
tossup-round-start-brief = Ronde { $round }.
tossup-your-turn =
    Giliran Anda. Skor yang sudah diamankan adalah { $score }. Lempar { $dice } { $dice ->
        [one] dadu
       *[other] dadu
    } untuk memulai.
tossup-player-turn =
    Giliran { $player } dengan { $score } poin yang sudah diamankan dan { $dice } { $dice ->
        [one] dadu
       *[other] dadu
    }.
tossup-your-turn-brief = Giliran Anda: { $score } poin.
tossup-player-turn-brief = Giliran { $player }: { $score } poin.
tossup-you-roll = Hasil lemparan Anda: { $results }.
tossup-player-rolls = Hasil lemparan { $player }: { $results }.
tossup-you-roll-safe-brief =
    { $fresh ->
        [yes] Anda: { $results }. Total giliran { $turn_points }. Set baru berisi { $dice_count } dadu.
       *[no] Anda: { $results }. Total giliran { $turn_points }. Tersisa { $dice_count } dadu.
    }
tossup-player-rolls-safe-brief =
    { $fresh ->
        [yes] { $player }: { $results }. Total giliran { $turn_points }. Set baru berisi { $dice_count } dadu.
       *[no] { $player }: { $results }. Total giliran { $turn_points }. Tersisa { $dice_count } dadu.
    }
tossup-result-green = { $count } hijau
tossup-result-yellow = { $count } kuning
tossup-result-red = { $count } merah
tossup-you-have-points =
    Anda menyisihkan { $gained } { $gained ->
        [one] dadu hijau
       *[other] dadu hijau
    }. Total giliran Anda { $turn_points }, dengan sisa { $dice_count } { $dice_count ->
        [one] dadu
       *[other] dadu
    }.
tossup-player-has-points =
    { $player } menyisihkan { $gained } { $gained ->
        [one] dadu hijau
       *[other] dadu hijau
    } dan memperoleh total { $turn_points } poin pada giliran ini, dengan sisa { $dice_count } { $dice_count ->
        [one] dadu
       *[other] dadu
    }.
tossup-you-get-fresh = Semua dadu berwarna hijau. Anda mendapat set baru berisi { $count } dadu dan boleh melempar lagi atau mengamankan poin.
tossup-player-gets-fresh = Semua dadu berwarna hijau. { $player } mendapat set baru berisi { $count } dadu.
tossup-you-bust =
    { $variant ->
        [Standard] Lampu merah. Lemparan Anda tidak menghasilkan hijau dan mengandung setidaknya satu merah. Giliran Anda berakhir dan Anda kehilangan { $points } poin yang belum diamankan.
       *[PlayAural] Semua dadu yang Anda lempar berwarna merah. Giliran Anda berakhir dan Anda kehilangan { $points } poin yang belum diamankan.
    }
tossup-player-busts =
    { $variant ->
        [Standard] Lampu merah. Lemparan { $player } tidak menghasilkan hijau dan mengandung setidaknya satu merah. Gilirannya berakhir dan ia kehilangan { $points } poin yang belum diamankan.
       *[PlayAural] Semua dadu yang dilempar { $player } berwarna merah. Gilirannya berakhir dan ia kehilangan { $points } poin yang belum diamankan.
    }
tossup-you-bust-brief = Anda: { $results }. Gagal, kehilangan { $points } poin.
tossup-player-busts-brief = { $player }: { $results }. Gagal, kehilangan { $points } poin.
tossup-you-bank = Anda mengamankan { $points } poin. Total skor Anda menjadi { $total }.
tossup-player-banks = { $player } mengamankan { $points } poin. Total skornya menjadi { $total }.
tossup-you-bank-brief = Anda mengamankan { $points } poin. Total { $total }.
tossup-player-banks-brief = { $player } mengamankan { $points } poin. Total { $total }.
tossup-you-trigger-final-turns =
    Anda melampaui batas { $target } poin dengan skor { $score }.
    { $count ->
        [one] Satu pemain yang tersisa mendapat satu giliran terakhir.
       *[other] { $count } pemain yang tersisa masing-masing mendapat satu giliran terakhir.
    }
tossup-player-triggers-final-turns =
    { $player } melampaui batas { $target } poin dengan skor { $score }.
    { $count ->
        [one] Satu pemain yang tersisa mendapat satu giliran terakhir.
       *[other] { $count } pemain yang tersisa masing-masing mendapat satu giliran terakhir.
    }
tossup-you-trigger-final-turns-brief =
    Skor Anda, { $score }, kini harus dilampaui. Tersisa { $count } { $count ->
        [one] giliran.
       *[other] giliran.
    }
tossup-player-triggers-final-turns-brief =
    Skor { $player }, { $score }, kini harus dilampaui. Tersisa { $count } { $count ->
        [one] giliran.
       *[other] giliran.
    }
tossup-you-win = Anda memenangkan Toss Up dengan { $score } poin.
tossup-winner = { $player } memenangkan Toss Up dengan { $score } poin.
tossup-you-win-brief = Anda menang: { $score } poin.
tossup-winner-brief = { $player } menang: { $score } poin.
tossup-tie-tiebreaker = { $players } memiliki skor tertinggi yang sama di atas target. Hanya para pemain tersebut yang melanjutkan ke babak penentuan.
tossup-tie-tiebreaker-brief = Babak penentuan: { $players }.
tossup-tiebreaker-round-start = Babak penentuan { $round } dimulai untuk { $players }.
tossup-tiebreaker-round-start-brief = Babak penentuan { $round }: { $players }.
tossup-your-turn-awaiting-roll =
    Anda belum melempar pada giliran ini. Anda memiliki { $score } poin yang sudah diamankan dan { $dice_count } { $dice_count ->
        [one] dadu siap dilempar
       *[other] dadu siap dilempar
    }.
tossup-player-turn-awaiting-roll =
    { $player } belum melempar. Ia memiliki { $score } poin yang sudah diamankan dan { $dice_count } { $dice_count ->
        [one] dadu siap dilempar
       *[other] dadu siap dilempar
    }.
tossup-your-turn-status =
    Hasil lemparan terakhir Anda: { $results }. Anda memiliki { $turn_points } poin giliran yang belum diamankan, { $score } poin yang sudah diamankan, dan { $dice_count } { $dice_count ->
        [one] dadu siap dilempar
       *[other] dadu siap dilempar
    }.
tossup-player-turn-status =
    Hasil lemparan terakhir { $player }: { $results }. Ia memiliki { $turn_points } poin giliran yang belum diamankan, { $score } poin yang sudah diamankan, dan { $dice_count } { $dice_count ->
        [one] dadu siap dilempar
       *[other] dadu siap dilempar
    }.
tossup-confirm-risky-roll =
    { $winning ->
        [yes] Mengamankan poin sekarang akan membuat Anda memimpin dengan { $total } poin, di atas batas { $target } poin.
       *[no] Saat ini Anda memiliki { $points } poin giliran yang belum diamankan.
    }
    Melempar { $dice } { $dice ->
        [one] dadu
       *[other] dadu
    } memiliki peluang gagal sekitar { $risk } persen. Tekan Lempar sekali lagi dalam { $seconds } detik untuk mengonfirmasi, atau amankan poin agar tidak hilang.
tossup-set-rules-variant = Aturan: { $variant }
tossup-select-rules-variant = Pilih aturan dadu dan kegagalan:
tossup-option-changed-rules = Aturan diubah menjadi { $variant }.
tossup-desc-rules-variant = Klasik memakai tiga sisi hijau, dua kuning, dan satu merah pada setiap dadu. Lemparan gagal jika tidak ada hijau dan ada setidaknya satu merah. Santai memberi peluang yang sama untuk ketiga warna dan hanya gagal jika semuanya merah.
tossup-desc-target-score = Giliran terakhir dimulai setelah seorang pemain mengamankan skor yang lebih tinggi dari batas ini. Nilai bawaan 100, rentang 20 hingga 500.
tossup-set-starting-dice = Dadu per set: { $count }
tossup-enter-starting-dice = Masukkan jumlah dadu dalam setiap set baru:
tossup-option-changed-dice = Jumlah dadu per set diubah menjadi { $count }.
tossup-desc-starting-dice = Pilih jumlah dadu di awal setiap giliran dan yang diberikan kembali setelah semua dadu menjadi hijau. Nilai bawaan 10, rentang 5 hingga 20.
tossup-rules-standard = Klasik
tossup-rules-PlayAural = Santai
tossup-rules-standard-desc = Tiga sisi hijau, dua kuning, dan satu merah. Gagal jika tidak ada hijau dan ada setidaknya satu merah.
tossup-rules-PlayAural-desc = Ketiga warna memiliki peluang yang sama. Gagal hanya jika semua dadu yang dilempar berwarna merah.
tossup-error-roll-not-playing = Anda tidak dapat melempar karena Toss Up sedang tidak berlangsung.
tossup-error-roll-no-turn = Anda tidak dapat melempar karena saat ini tidak ada giliran yang aktif di Toss Up.
tossup-error-roll-not-your-turn = Anda tidak dapat melempar pada giliran { $player }. Tunggu giliran Anda.
tossup-error-bank-not-playing = Anda tidak dapat mengamankan poin karena Toss Up sedang tidak berlangsung.
tossup-error-bank-no-turn = Anda tidak dapat mengamankan poin karena saat ini tidak ada giliran yang aktif di Toss Up.
tossup-error-bank-not-your-turn = Anda tidak dapat mengamankan poin pada giliran { $player }. Tunggu giliran Anda.
tossup-error-bank-roll-first = Lempar setidaknya sekali sebelum mengamankan poin. Anda boleh mengamankan hasil lemparan yang seluruhnya kuning dengan 0 poin untuk mengakhiri giliran.
tossup-error-spectator-action = Penonton dapat memeriksa status umum Toss Up, tetapi tidak dapat melempar atau mengamankan poin.
tossup-error-status-not-playing = Status giliran tidak tersedia karena Toss Up sedang tidak berlangsung.
tossup-error-status-no-turn = Status giliran tidak tersedia karena saat ini tidak ada pemain aktif di Toss Up.
tossup-error-target-out-of-range = Batas target saat ini { $value }. Nilainya harus antara { $min } dan { $max } poin.
tossup-error-dice-out-of-range = Jumlah dadu dalam set baru saat ini { $value }. Jumlahnya harus antara { $min } dan { $max } dadu.
tossup-error-rules-variant = Aturan "{ $variant }" tidak didukung. Pilih Klasik atau Santai.
tossup-line-format = { $rank }. { $player }: { $points }
