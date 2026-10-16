game-name-pig = Pig
pig-desc-team-mode = Bermain sendiri-sendiri atau dengan susunan tim yang tersedia. Satu tim berbagi skor dan langsung menang saat salah satu anggotanya mengamankan cukup poin.
pig-roll = Lempar dadu
pig-hold = Amankan { $points } poin
pig-check-turn-status = Periksa status giliran
pig-game-start =
    Pig dimulai. { $team ->
        [yes] Tim
       *[no] Pemain
    } pertama yang mengamankan { $target } poin menang. Dadu memiliki { $sides } sisi. Jika muncul angka 1, seluruh poin yang belum diamankan pada giliran itu hangus. { $minimum ->
        [0] Anda boleh mengamankan poin setelah setiap lemparan yang menghasilkan poin.
       *[other] Kumpulkan setidaknya { $minimum } poin giliran sebelum mengamankan poin.
    }
pig-game-start-brief =
    Pig dimulai. Target: { $target }. Dadu: { $sides } sisi. Minimum untuk diamankan: { $minimum }. { $team ->
        [yes] Skor bersama satu tim.
       *[no] Skor per pemain.
    }
pig-round-start = Ronde { $round } dimulai. Setiap pemain aktif mendapat satu giliran.
pig-round-start-brief = Ronde { $round }.
pig-you-roll-result = Hasil lemparan Anda { $roll }. Total giliran Anda kini { $total } poin.
pig-player-roll-result = Hasil lemparan { $player } adalah { $roll }. Total gilirannya kini { $total } poin.
pig-you-roll-result-brief = Anda: { $roll }, total giliran { $total }.
pig-player-roll-result-brief = { $player }: { $roll }, total giliran { $total }.
pig-you-bust = Anda mendapat angka 1. Seluruh { $points } poin yang belum diamankan hangus. Giliran Anda berakhir tanpa poin.
pig-player-busts = { $player } mendapat angka 1. Seluruh { $points } poin yang belum diamankan hangus. Gilirannya berakhir tanpa poin.
pig-you-bust-brief = Anda mendapat angka 1. { $points } poin giliran hangus.
pig-player-busts-brief = { $player } mendapat angka 1. { $points } poin giliran hangus.
pig-you-hold =
    Anda mengamankan { $points } poin. { $team ->
        [yes] Tim Anda kini memiliki { $total } poin.
       *[no] Skor total Anda kini { $total } poin.
    }
pig-player-holds =
    { $player } mengamankan { $points } poin. { $team ->
        [yes] { $team_name } kini memiliki { $total } poin.
       *[no] Skor totalnya kini { $total } poin.
    }
pig-you-hold-brief =
    Anda mengamankan { $points } poin. { $team ->
        [yes] Total { $team_name }: { $total }.
       *[no] Total Anda: { $total }.
    }
pig-player-holds-brief =
    { $player } mengamankan { $points } poin. { $team ->
        [yes] Total { $team_name }: { $total }.
       *[no] Total: { $total }.
    }
pig-you-win =
    { $team ->
        [yes] Tim Anda, { $winner }, memenangi Pig dengan { $score } poin!
       *[no] Anda memenangi Pig dengan { $score } poin!
    }
pig-winner =
    { $team ->
        [yes] Pemenangnya adalah { $winner }, dengan { $score } poin!
       *[no] Pemenangnya adalah { $winner }, dengan { $score } poin!
    }
pig-you-win-brief =
    { $team ->
        [yes] Pemenang: tim Anda, { $winner }, dengan { $score }.
       *[no] Pemenang: Anda, dengan { $score }.
    }
pig-winner-brief = Pemenang: { $winner }, dengan { $score }.
pig-confirm-risky-roll =
    Melempar lagi mempertaruhkan { $points } poin yang belum diamankan, dengan risiko hangus sebesar { $risk } persen. { $winning ->
        [yes] Jika diamankan sekarang, skor Anda menjadi { $total } poin dan Anda menang.
       *[no] Jika diamankan sekarang, skor Anda menjadi { $total } dari target { $target } poin untuk menang.
    } Tekan Lempar lagi dalam { $seconds } detik untuk mengonfirmasi.
pig-action-resolving = Dadu masih bergulir. Tunggu hasilnya.
pig-no-turn-points = Lempar dadu setidaknya sekali sebelum mengamankan poin.
pig-need-more-points = Anda memiliki { $current } poin giliran, tetapi meja ini mensyaratkan setidaknya { $required } sebelum poin dapat diamankan.
pig-desc-target-score = Pemain atau tim pertama yang mengamankan skor total sebanyak ini langsung menang. Nilai bawaan 100, dari 10 sampai 1000.
pig-set-min-bank = Minimum poin untuk diamankan: { $points }
pig-set-dice-sides = Jumlah sisi dadu: { $sides }
pig-enter-min-bank = Masukkan minimum poin giliran sebelum poin dapat diamankan:
pig-enter-dice-sides = Masukkan jumlah sisi dadu:
pig-option-changed-min-bank = Minimum poin untuk diamankan diubah menjadi { $points } poin.
pig-desc-min-bank = Poin giliran minimum sebelum tindakan Amankan tersedia. Pilih 0 untuk aturan Pig standar. Nilainya harus di bawah target skor. Nilai bawaan 0, dari 0 sampai 999.
pig-option-changed-dice = Dadu kini memiliki { $sides } sisi.
pig-desc-dice-sides = Jumlah sisi pada satu dadu yang digunakan. Angka 1 selalu menghanguskan total poin giliran. Nilai bawaan 6, dari 4 sampai 20.
pig-error-target-out-of-range = Target skor { $value } tidak valid. Pilih nilai dari { $min } sampai { $max }.
pig-error-min-bank-out-of-range = Minimum poin untuk diamankan, { $value }, tidak valid. Pilih nilai dari { $min } sampai { $max }.
pig-error-dice-sides-out-of-range = Dadu dengan { $value } sisi tidak didukung. Pilih dari { $min } sampai { $max } sisi.
pig-error-min-bank-too-high = Minimum poin untuk diamankan, { $minimum }, harus lebih rendah dari target skor { $target }.
pig-status-target = Target skor: { $target } poin.
pig-status-round = Ronde saat ini: { $round }.
pig-status-current-turn = { $player } sedang bermain. Poin yang sudah diamankan { $banked }, poin giliran ini { $turn }, total jika diamankan sekarang { $potential }.
pig-status-standing = { $rank }. { $team }: { $score } poin.
pig-line-format = { $rank }. { $player }: { $points }
