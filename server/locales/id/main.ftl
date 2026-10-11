auth-username-password-required = Nama pengguna dan kata sandi diperlukan.
auth-registration-success = Pendaftaran berhasil! Anda sekarang dapat masuk dengan nama pengguna dan kata sandi Anda.
auth-username-taken = Nama pengguna sudah dipakai. Silakan pilih nama pengguna lain.
auth-username-reserved = Nama ini dikhususkan untuk PlayAural. Silakan pilih nama pengguna lain.
auth-registration-error = Pendaftaran gagal karena kesalahan server. Silakan coba lagi.
auth-error-wrong-password = Kata sandi salah.
auth-error-user-not-found = Pengguna tidak ditemukan.
username-ambiguous = Ada lebih dari satu akun lama yang cocok dengan "{ $username }". Masukkan nama pengguna persis seperti saat didaftarkan.
auth-kicked-logged-in-elsewhere = Koneksi Anda diputus karena akun Anda digunakan untuk masuk dari perangkat lain.
admin-smtp-updated-success = Pengaturan SMTP berhasil diperbarui
admin-smtp-settings = Pengaturan SMTP
email-reset-subject = Kode Pemulihan Kata Sandi PlayAural
email-reset-body =
    Halo { $username },

    Anda meminta pengaturan ulang kata sandi untuk akun PlayAural Anda.
    Kode atur ulang 6 digit Anda adalah: { $code }

    Kode ini akan kedaluwarsa dalam 15 menit.
    Jika Anda tidak memintanya, abaikan email ini.
email-reset-body-html =
    <p>Hai { $username },</p>
    <p>Kami menerima permintaan untuk mengatur ulang kata sandi akun PlayAural Anda.</p>
    <p>Kode pemulihan 6 digit Anda adalah:</p>
    <h2>{ $code }</h2>
    <p>Kode ini akan kedaluwarsa tepat dalam 15 menit.</p>
    <p>Jika Anda tidak memintanya, abaikan email ini. Akun Anda tetap aman.</p>
    <p>Salam,<br>Trung</p>
email-test-subject = Uji SMTP PlayAural
email-test-body = Ini adalah email percobaan dari server PlayAural yang memverifikasi konfigurasi SMTP Anda.
email-test-body-html =
    <p>Halo,</p>
    <p>Ini adalah email percobaan dari server PlayAural.</p>
    <p>Jika Anda membaca ini, konfigurasi SMTP Anda berhasil mengirim email HTML.</p>
smtp-test-sending = Sedang menguji koneksi, harap tunggu...
smtp-test-success = Email percobaan berhasil dikirim ke { $email }!
smtp-test-failed = Gagal mengirim email percobaan: { $error }
smtp-host = Host: { $value }
smtp-port = Port: { $value }
smtp-username = Nama pengguna: { $value }
smtp-password = Kata sandi: { $value }
smtp-from-email = Alamat email pengirim: { $value }
smtp-from-name = Nama pengirim: { $value }
smtp-encryption = Enkripsi: { $value }
smtp-test-connection = Uji Koneksi
smtp-not-set = Tidak disetel
smtp-prompt-host = Masukkan host SMTP, misalnya smtp.gmail.com:
smtp-prompt-port = Masukkan port SMTP, misalnya 587 atau 465:
smtp-prompt-username = Masukkan nama pengguna SMTP:
smtp-prompt-password = Masukkan kata sandi SMTP:
smtp-prompt-from-email = Masukkan alamat email pengirim:
smtp-prompt-from-name = Masukkan nama pengirim, misalnya Dukungan PlayAural:
smtp-prompt-test-email = Masukkan alamat email tujuan untuk pengujian:
smtp-enc-none = Tidak ada enkripsi
smtp-enc-ssl = Gunakan SSL
smtp-enc-tls = Aktifkan enkripsi TLS secara otomatis (STARTTLS)
smtp-current-enc = { $value } (dipilih)
play = Main
view-active-tables = Lihat meja aktif
options = Pengaturan
logout = Keluar
back = Kembali
go-back = Kembali
context-menu = Konteks menu.
no-actions-available = Tidak ada tindakan yang tersedia.
table-new-host-promoted = { $player } sekarang menjadi pemilik meja.
table-new-host-promoted-you = Anda sekarang menjadi pemilik meja.
return-to-table = Kembali ke meja
create-table = Buat meja baru
leave-table = Tinggalkan meja
start-game = Mulai permainan
add-bot = Tambahkan bot
remove-bot = Hapus bot
actions-menu = Menu tindakan
save-table = Simpan meja
whose-turn = Giliran siapa
whos-at-table = Siapa yang ada di meja
check-scores = Periksa skor
check-scores-detailed = Skor terperinci
game-player-skipped = Giliran { $player } dilewati.
game-player-skipped-you = Giliran Anda dilewati.
table-created = { $host } membuat meja { $game } baru.
table-created-broadcast = { $host } membuat meja { $game } baru.
table-joined = { $player } bergabung dengan meja.
table-joined-you = Anda bergabung dengan meja.
table-left = { $player } meninggalkan meja.
new-host = { $player } sekarang menjadi pemilik meja.
new-host-you = Anda sekarang adalah pemilik meja.
waiting-for-players = Menunggu pemain. Minimal { $min }, maksimal { $max }.
game-starting = Permainan dimulai!
table-listing-game-composition-status = { $game } [{ $status }]: meja { $host }. { $composition }.
table-composition-human-players =
    { $count } { $count ->
        [one] pemain
       *[other] pemain
    }: { $names }
table-composition-bots =
    { $count } { $count ->
        [one] bot
       *[other] bot
    }
table-composition-spectators =
    { $count ->
        [one] Penonton
       *[other] Penonton
    }: { $names }
table-composition-spectators-more = Penonton: { $names }, ditambah { $remaining } lagi
table-composition-spectator-host = { $host } (pemilik meja)
table-composition-two = { $first }. { $second }
table-composition-three = { $first }. { $second }. { $third }
table-composition-empty = tidak ada peserta
table-status-waiting = Menunggu
table-status-playing = Bermain
table-status-finished = Selesai
table-not-exists = Meja sudah tidak ada.
table-full = Meja sudah penuh.
table-closed-disconnect-timeout = Meja ditutup karena tidak ada pemain aktif yang kembali dalam { $minutes } menit.
player-replaced-by-bot = { $bot } sekarang bermain atas nama { $player }.
player-reclaimed-from-bot = { $player } kembali dan mengambil alih tempatnya dari { $bot }.
player-reclaimed-from-bot-you = Anda kembali dan mengambil alih tempat Anda dari { $bot }.
spectator-joined = Bergabung dengan meja { $host } sebagai penonton.
spectate = Tonton
now-playing = { $player } sekarang bermain.
now-playing-you = Anda sekarang sedang bermain.
now-spectating = { $player } sekarang sedang menonton.
now-spectating-you = Anda sekarang sedang menonton.
spectator-left = { $player } berhenti menonton.
welcome = Selamat datang di PlayAural!
goodbye = Selamat tinggal!
user-online = { $player } online.
user-offline = { $player } offline.
friend-online = Teman Anda { $player } sekarang online.
friend-offline = Teman Anda { $player } offline.
permission-denied = Anda tidak memiliki izin untuk melakukan tindakan ini pada Pengembang.
kick-user = Keluarkan pengguna
kick-broadcast = { $target } dikeluarkan oleh { $actor }.
kick-broadcast-actor = Anda mengeluarkan { $target }.
user-not-online = Pengguna { $target } tidak online.
kick-confirm = Yakin ingin mengeluarkan { $player }?
no-users-to-kick = Tidak ada pengguna yang dapat dikeluarkan.
usage-kick = Cara penggunaan: /kick <username>
online-users-none = Tidak ada pengguna online.
online-users-summary =
    { $count ->
        [one] { $count } pengguna online. { $groups }
       *[other] { $count } pengguna online. { $groups }
    }
online-users-group =
    { $role ->
        [dev]
            { $count ->
                [one] { $count } pengembang: { $users }.
               *[other] { $count } pengembang: { $users }.
            }
        [admin]
            { $count ->
                [one] { $count } administrator: { $users }.
               *[other] { $count } administrator: { $users }.
            }
       *[user]
            { $staff_count ->
                [0] { $users }.
               *[other]
                    { $count ->
                        [one] { $count } pengguna: { $users }.
                       *[other] { $count } pengguna: { $users }.
                    }
            }
    }
online-users-more = { $count } lagi
online-user-waiting-approval = Menunggu persetujuan
presence-status-main-menu = Menu utama
presence-status-waiting-table = Menunggu di meja { $game }
presence-status-playing = Memainkan { $game }
presence-status-spectating = Menonton { $game }
presence-status-watching-table = Menonton meja { $game }
presence-status-reviewing-results = Meninjau hasil { $game }
presence-status-spectating-results = Menonton hasil { $game }
user-role-dev = Pengembang
user-role-admin = Administrator
user-role-user = Pengguna
client-type-web = Web
client-type-python = Desktop
client-type-mobile = Seluler
client-type-with-platform = { $client } ({ $platform })
online-user-full-entry = { $username } ({ $role }, { $client }, { $language }): { $status }
user-not-online-anymore = Pengguna ini sudah tidak online.
close-menu = Tutup
language = Bahasa
language-option = Bahasa: { $language }
language-changed = Bahasa disetel ke { $language }.
language-menu-entry =
    { $official ->
        [true] { $language }. Bahasa resmi PlayAural. Penerjemah: { $translators }.
       *[false] { $language }. Terjemahan komunitas. Penerjemah: { $translators }.
    }
language-menu-entry-missing-metadata = { $language }. Informasi penerjemah tidak tersedia.
language-menu-current-entry = Saat ini: { $entry }
option-on = Aktif
option-off = Nonaktif
# Multi-select option sub-menu controls
option-back = Kembali
option-select-all = Pilih semua
option-deselect-all = Batalkan semua pilihan
option-selected-count = { $count } dipilih
option-deselected-count = { $count } pilihan dibatalkan
option-multiselect-group = { $group } ({ $count } dari { $total } dipilih)
option-min-selected = Anda harus memilih setidaknya { $count }.
option-max-selected = Anda dapat memilih paling banyak { $count }.
custom-bot-names-option = Nama bot khusus: { $status }
option-notify-table-created = Beritahukan ketika meja dibuat: { $status }
option-notify-user-presence = Notifikasi online/offline pengguna: { $status }
option-notify-friend-presence = Notifikasi online/offline teman: { $status }
dice-keeping-style-option = Cara memilih dadu yang disimpan: { $style }
dice-keeping-style-changed = Cara memilih dadu yang disimpan diubah menjadi { $style }.
dice-keeping-style-indexes = Posisi dadu
dice-keeping-style-values = Nilai dadu
general-options = Pengaturan umum
game-options = Pengaturan permainan
# Game Options (declarative preferences with per-game overrides)
pref-category-display = Tampilan
pref-set-brief-announcements = Pengumuman singkat: { $status }
pref-changed-brief-announcements = Pengumuman singkat { $status }.
pref-desc-brief-announcements = Persingkat pengumuman langkah dan kejadian dalam permainan. Nonaktifkan untuk mendengar penjelasan yang lebih lengkap.
pref-category-sounds = Suara
pref-category-gameplay = Permainan
pref-category-dice = Dadu
pref-default = Bawaan
pref-per-game-for = { $game }: { $value }
pref-reset-all = Atur ulang semua pengaturan permainan
pref-reset-category = Atur ulang pengaturan { $category }
pref-reset-done = Pengaturan permainan telah diatur ulang.
pref-set-play-turn-sound = Suara penanda giliran: { $status }
pref-set-confirm-destructive-actions = Konfirmasikan tindakan berisiko: { $status }
pref-set-allow-custom-bot-names = Nama bot khusus: { $status }
pref-set-clear-kept-on-roll = Lepaskan dadu yang disimpan setelah melempar: { $status }
pref-set-dice-keeping-style = Cara memilih dadu yang disimpan: { $choice }
pref-changed-play-turn-sound = Suara penanda giliran { $status }.
pref-changed-confirm-destructive-actions = Konfirmasikan tindakan berisiko { $status }.
pref-changed-allow-custom-bot-names = Nama bot khusus { $status }.
pref-changed-clear-kept-on-roll = Lepaskan dadu yang disimpan setelah melempar { $status }.
pref-changed-dice-keeping-style = Cara memilih dadu yang disimpan diubah menjadi { $choice }.
pref-desc-play-turn-sound = Mainkan suara saat giliran Anda tiba.
pref-desc-confirm-destructive-actions = Minta konfirmasi sebelum tindakan yang berisiko atau tidak dapat dibatalkan, seperti melewatkan giliran dalam Pusoy Dos.
pref-desc-allow-custom-bot-names = Memungkinkan Anda menetapkan nama khusus untuk bot yang Anda tambahkan ke meja.
pref-desc-clear-kept-on-roll = Dalam permainan dadu yang mendukungnya, seperti Yahtzee, semua dadu yang disimpan akan dilepaskan setelah setiap lemparan. Pada lemparan berikutnya, semua dadu dilempar ulang kecuali Anda menyimpannya lagi. Jika memilih Nilai dadu, gunakan Shift+1 hingga Shift+6 untuk menyimpan dadu dengan nilai yang sesuai.
pref-desc-dice-keeping-style = Posisi dadu: gunakan tombol 1 hingga 5, atau 1 hingga 6 dalam Midnight, untuk menyimpan atau melepaskan dadu berdasarkan posisinya. Nilai dadu: gunakan 1 hingga 6 untuk melepaskan satu dadu tersimpan dengan nilai tersebut, dan Shift+1 hingga Shift+6 untuk menyimpan satu dadu dengan nilai yang sesuai. Dalam tahap pertukaran Tradeoff, tombol 1 hingga 6 menyimpan satu dadu yang sesuai, sedangkan Shift+1 hingga Shift+6 menandainya untuk ditukar. Dalam tahap pengambilan, tombol 1 hingga 6 tanpa Shift mengambil dadu yang sesuai dari kumpulan dadu.
cancel = Batalkan
enter-bot-name = Masukkan nama bot
bot-name-invalid-length = Nama bot harus terdiri dari 3 hingga 30 karakter.
bot-name-invalid-characters = Nama bot hanya boleh berisi huruf, angka, dan spasi.
table-name-already-used = Seorang pemain atau bot dengan nama ini sudah ada di meja.
no-options-available = Tidak ada pilihan yang tersedia.
no-scores-available = Tidak ada skor yang tersedia.
option-desc-generic = { $label }. Bawaan: { $default }.
option-desc-integer = { $label }. Masukkan bilangan bulat dari { $min } hingga { $max }. Bawaan: { $default }.
option-desc-number = { $label }. Masukkan angka dari { $min } hingga { $max }. Bawaan: { $default }.
option-desc-menu = { $label }. Pilih salah satu dari: { $choices }. Bawaan: { $default }.
option-desc-bool = { $label }. Aktifkan item ini untuk mengaktifkan atau menonaktifkan pengaturan. Bawaan: { $default }.
option-desc-multiselect = { $label }. Pilihan saat ini: { $selected }. Minimal: { $min }. Maksimal: { $max }. Pilihan bawaan: { $default }.
option-desc-no-choices = tidak ada pilihan yang tersedia saat ini
option-desc-none-selected = tidak ada
option-desc-no-maximum = tanpa batas maksimal
menu-item-with-hint = { $label }: { $hint }
general-desc-profile = Lihat dan edit detail profil publik Anda.
general-desc-friends = Kelola teman, permintaan pertemanan, pesan pribadi, serta bergabung ke meja teman atau mengundang mereka.
general-desc-my-stats = Tinjau kemenangan, kekalahan, peringkat, dan statistik permainan yang didukung.
general-desc-general-options = Sesuaikan bahasa, obrolan global, audio, aksesibilitas, notifikasi, dan preferensi permainan.
general-desc-game-options = Sesuaikan preferensi permainan yang dapat diterapkan secara global atau pada permainan yang didukung.
general-desc-language = Pilih bahasa yang digunakan oleh menu server, pesan, dan dokumentasi bila tersedia.
general-desc-audio = Atur volume musik, efek suara, suara latar, obrolan suara, bunyi pengetikan, dan perangkat input pada aplikasi desktop.
general-desc-accessibility = Atur pembacaan, masukan, dan perilaku aplikasi yang mendukung aksesibilitas pada perangkat ini.
general-desc-notifications = Pilih notifikasi obrolan, kehadiran, dan pembuatan meja mana yang ingin Anda dengar.
general-desc-music-volume = Ubah volume musik latar. Pilih Nonaktif untuk mematikan musik.
general-desc-sound-volume = Ubah volume efek suara permainan. Volume minimal sepuluh persen agar petunjuk suara penting tetap terdengar.
general-desc-ambience-volume = Ubah volume suara latar. Pilih Nonaktif untuk mematikannya.
general-desc-voice-volume = Ubah volume pemutaran obrolan suara meja.
general-desc-audio-input-device = Pilih mikrofon atau perangkat input yang digunakan oleh klien desktop untuk obrolan suara.
general-desc-play-typing-sounds = Bunyikan suara ketikan saat Anda memasukkan teks ke kolom isian aplikasi.
general-desc-web-speech-settings = Atur pembacaan pada browser, termasuk mode ARIA live atau Web Speech, kecepatan bicara, dan suara.
general-desc-mobile-speech-settings = Atur mesin pembaca teks, suara, dan kecepatan bicara pada aplikasi seluler.
general-desc-invert-multiline-enter = Tukar fungsi tombol untuk mengirim pesan dan membuat baris baru pada kolom teks multibaris di aplikasi desktop.
general-desc-menu-hints = Tampilkan keterangan langsung pada baris menu. Jika dinonaktifkan, arahkan fokus ke pilihan yang memiliki keterangan. Tekan F1 pada desktop atau web dengan keyboard fisik, atau ketuk sekali dengan tiga jari dalam mode pembacaan suara aplikasi seluler untuk mendengarnya.
general-desc-mute-global-chat = Hentikan pesan obrolan global agar tidak diucapkan secara otomatis.
general-desc-global-chat-channel = Pilih saluran bahasa yang digunakan untuk mengirim dan menerima obrolan global. Saluran diperlukan meskipun obrolan global diaktifkan.
general-desc-mute-table-chat = Hentikan pesan obrolan meja agar tidak diucapkan secara otomatis.
general-desc-notify-user-presence = Umumkan saat pengguna online atau offline.
general-desc-notify-friend-presence = Umumkan kapan teman Anda online atau offline.
general-desc-notify-table-created = Umumkan kapan meja publik baru dibuat.
general-desc-speech-mode = Pilih apakah aplikasi web menyampaikan pengumuman melalui pembaca layar dengan ARIA live, atau membacakannya sendiri dengan Web Speech API pada browser.
general-desc-speech-rate = Ubah kecepatan bicara klien web.
general-desc-speech-voice = Pilih suara Web Speech API untuk aplikasi web, atau gunakan suara bawaan browser.
general-desc-mobile-tts-engine = Pilih mesin pembaca teks untuk aplikasi seluler. Saat ini Android menggunakan mesin yang diatur oleh sistem.
general-desc-mobile-tts-voice = Pilih suara pembaca teks untuk aplikasi seluler, atau gunakan suara bawaan sistem.
general-desc-mobile-tts-rate = Ubah kecepatan pembacaan teks pada aplikasi seluler.
saved-tables = Meja Tersimpan
no-saved-tables = Anda tidak memiliki meja yang disimpan.
no-active-tables = Tidak ada meja aktif.
no-active-tables-all = Tidak ada meja aktif yang tersedia.
no-active-tables-waiting = Tidak ada meja yang sedang menunggu pemain.
no-active-tables-playing = Tidak ada meja dengan permainan yang sedang berlangsung.
active-tables-filter = Filter: { $filter }
filter-name-all = Semua
filter-name-waiting = Menunggu
filter-name-playing = Bermain
game-category-filter = Kategori: { $category }
game-category-filter-option = { $category } ({ $count })
game-category-all = Semua
game-category-cards = Permainan Kartu
game-category-poker = Permainan Poker
game-category-dice = Permainan Dadu
game-category-board = Permainan Papan
game-category-arcade = Permainan arkade
game-category-misc = Lain-lain
no-games-in-category = Tidak ada permainan yang tersedia dalam kategori ini.
restore-table = Pulihkan
delete-saved-table = Hapus
saved-table-deleted = Meja tersimpan telah dihapus.
missing-players = Tidak dapat memulihkan: pemain ini tidak tersedia: { $players }
saved-table-blocked-by-you = Meja tersimpan ini mencakup pengguna yang Anda blokir: { $players }. Untuk memulihkannya, buka Pribadi dan Pengaturan, Teman, lalu Pengguna yang Diblokir dan buka blokirnya. Pemulihan hanya dapat dilakukan jika kontak sosial langsung tersedia untuk semua orang. Data simpanan tetap tersedia.
saved-table-social-blocked = Meja yang disimpan ini tidak dapat dipulihkan karena kontak sosial langsung tidak tersedia antara Anda dan: { $players }. Data simpanan tetap tersedia.
saved-table-social-blocked-mixed = Meja tersimpan ini mencakup pengguna yang Anda blokir: { $blocked }. Buka Pribadi dan Pengaturan, Teman, lalu Pengguna yang Diblokir dan buka blokirnya. Kontak sosial langsung juga tidak tersedia dengan: { $unavailable }. Data simpanan tetap tersedia.
saved-table-invalid = Meja yang disimpan ini tidak dapat dipulihkan lagi karena data permainan atau pemain yang disimpan tidak lengkap atau tidak kompatibel. Data simpanan tetap tersedia.
table-restored = Meja dipulihkan!
table-saved-destroying = Meja disimpan! Kembali ke menu utama.
game-type-not-found = Jenis permainan sudah tidak ada lagi.
action-not-your-turn = Ini bukan giliran Anda.
action-not-playing = Permainan belum dimulai.
action-spectator = Penonton tidak bisa melakukan ini.
action-not-host = Hanya pemilik meja yang dapat melakukan hal ini.
action-not-available = Tindakan tersebut tidak tersedia saat ini.
action-game-in-progress = Tidak dapat melakukan ini saat permainan sedang berlangsung.
action-need-more-players = Perlu lebih banyak pemain untuk memulai.
action-table-full = Mejanya penuh.
action-start-needs-more-players = Tidak dapat memulai. Pemain aktif: { $current }. Persyaratan minimum: { $minimum }.
action-start-has-too-many-players = Tidak dapat memulai. Pemain aktif: { $current }. Maksimum yang diperbolehkan: { $maximum }.
action-start-requires-exact-players = Tidak dapat memulai. Pemain aktif: { $current }. Diperlukan: tepatnya { $required }.
action-start-needs-human-player = Tidak dapat memulai hanya dengan bot. Setidaknya satu manusia harus berpartisipasi sebagai pemain. Beralih dari penonton ke pemain, jika meja sudah penuh, hapus bot terlebih dahulu.
action-no-bots = Tidak ada bot yang dapat dikeluarkan.
action-bots-cannot = Bot tidak bisa melakukan ini.
action-role-change-rate-limited =
    Anda beralih antara bermain dan menonton terlalu cepat. Coba lagi dalam { $seconds ->
        [one] 1 detik
       *[other] { $seconds } detik
    }.
options-category-audio = Audio
options-category-accessibility = Aksesibilitas
options-category-notifications = Pemberitahuan
music-volume-option = Volume Musik: { $value }%
sound-volume-option = Volume Efek Suara: { $value }%
ambience-volume-option = Volume Suara latar: { $value }%
voice-volume-option = Volume Obrolan Suara: { $value }%
volume-choice-off = Nonaktif
volume-choice-percent = { $value }%
volume-choice-current = { $label } (saat ini)
audio-input-device-option = Perangkat Masukan Audio: { $device }
audio-input-device-default = Perangkat input bawaan sistem
mute-global-chat-option = Senyapkan obrolan global: { $status }
global-chat-channel-option = Bahasa Obrolan Global: { $channel }
global-chat-channel-none = Tidak ada saluran yang dipilih
global-chat-channel-none-current = Tidak ada saluran yang dipilih (saat ini)
global-chat-channel-name = { $language }
global-chat-channel-recommended = { $language } (direkomendasikan untuk bahasa antarmuka Anda)
global-chat-channel-current = { $language } (saat ini)
global-chat-channel-current-recommended = { $language } (saat ini, direkomendasikan untuk bahasa antarmuka Anda)
global-chat-channel-selected = Bahasa obrolan global disetel ke { $language }. Obrolan global tidak dipantau secara langsung. Jika seseorang menggunakan kata-kata kotor atau menghina Anda, blokir pengguna tersebut. Silakan laporkan penyalahgunaan yang serius atau berulang untuk ditinjau nanti.
global-chat-channel-cleared = Tidak ada bahasa obrolan global yang dipilih. Anda tidak akan mengirim atau menerima pesan global.
mute-table-chat-option = Senyapkan obrolan meja: { $status }
invert-multiline-enter-option = Tukar fungsi tombol Enter: { $status }
menu-hints-option = Petunjuk Menu: { $status }
menu-hints-changed = Petunjuk menu sekarang menjadi { $status }.
play-typing-sounds-option = Mainkan Suara Ketikan: { $status }
invalid-volume = Volume tidak valid.
dice-not-rolled = Anda belum melempar dadu.
dice-no-dice = Tidak ada dadu yang tersedia.
table-no-players = Tidak ada pemain.
table-players-one = { $count } pemain: { $players }.
table-players-many = { $count } pemain: { $players }.
table-spectators = Penonton: { $spectators }.
table-host-suffix = (Pemilik meja)
table-voice-chat-suffix = (dalam obrolan suara)
table-members-summary-compact = Ringkasan meja: { $composition }.
table-summary-human-players =
    { $count } { $count ->
        [one] pemain manusia
       *[other] pemain manusia
    }
table-summary-bots =
    { $count } { $count ->
        [one] bot
       *[other] bot
    }
table-summary-spectators =
    { $count } { $count ->
        [one] penonton
       *[other] penonton
    }
table-members-empty = Tidak ada anggota meja yang terdaftar saat ini. Gunakan Kembali untuk menyegarkan tampilan meja.
table-member-entry = { $player }: { $status }
table-member-status-host = Pemilik meja
table-member-status-player = Pemain
table-member-status-spectator = Penonton
table-member-status-bot = Bot
table-member-status-online = Online
table-member-status-offline = Offline
table-member-status-voice-chat = dalam obrolan suara
table-member-status-bot-takeover = sedang diwakili bot: { $bot }
table-member-no-actions = Tidak ada tindakan yang tersedia untuk { $player }.
table-member-left = Orang itu sudah tidak ada lagi.
table-member-bot-left = Bot itu sudah tidak ada lagi.
game-over = Permainan Berakhir
game-final-scores = Skor Akhir
game-points =
    { $count } { $count ->
        [one] poin
       *[other] poin
    }
leaderboards = Papan peringkat
leaderboard-no-data = Belum ada data papan peringkat untuk permainan ini.
leaderboard-type-wins = Kemenangan terbanyak
leaderboard-type-rating = Rating keterampilan
leaderboard-type-total-score = Skor Total
leaderboard-type-high-score = Skor tertinggi
leaderboard-type-games-played = Permainan yang Dimainkan
leaderboard-type-avg-points-per-turn = Rata-rata poin per giliran
leaderboard-type-best-single-turn = Giliran terbaik
leaderboard-type-score-per-round = Skor per ronde
leaderboard-type-most-enemies-defeated = Musuh terbanyak yang dikalahkan
leaderboard-type-deepest-wave-reached = Gelombang tertinggi yang dicapai
leaderboard-wins-entry =
    { $rank }: { $player }, { $wins } { $wins ->
        [one] menang
       *[other] menang
    } { $losses } { $losses ->
        [one] kalah
       *[other] kalah
    }, { $percentage }% tingkat kemenangan
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-games-entry = { $rank }. { $player }: { $value } permainan
leaderboard-avg-entry = { $rank }. { $player }: { $value }
leaderboard-no-player-stats = Anda belum memainkan permainan ini.
leaderboard-no-ratings = Belum ada data rating untuk permainan ini.
leaderboard-rating-entry = { $rank }. { $player }: rating { $rating }
leaderboard-no-player-rating = Anda belum memiliki rating untuk permainan ini.
my-stats = Statistik saya
my-stats-select-game = Pilih permainan untuk melihat statistik Anda
my-stats-no-data = Anda belum memainkan permainan ini.
my-stats-no-games = Anda belum memainkan permainan apa pun.
my-stats-header = { $game } - Statistik Anda
my-stats-wins = Menang: { $value }
my-stats-losses = Kalah: { $value }
my-stats-winrate = Tingkat kemenangan: { $value }%
my-stats-games-played = Permainan yang dimainkan: { $value }
my-stats-total-score = Skor total: { $value }
my-stats-high-score = Skor tertinggi: { $value }
my-stats-rating = Rating keterampilan: { $value }
my-stats-no-rating = Belum ada rating keterampilan
my-stats-custom = { $name }: { $value }
my-stats-avg-per-turn = Poin rata-rata per giliran: { $value }
my-stats-best-turn = Giliran terbaik: { $value }
my-stats-score-per-round = Skor per ronde: { $value }
my-stats-most-enemies-defeated = Musuh Terbanyak Dikalahkan: { $value }
my-stats-deepest-wave-reached = Gelombang tertinggi yang dicapai: { $value }
confirm-leave-game = Apakah Anda yakin ingin meninggalkan meja?
confirm-yes = Ya
confirm-no = Tidak
administration = Administrasi
admin-moderation = Moderasi Obrolan
admin-moderation-global-chat-toggle = Obrolan global: { $status }
admin-moderation-global-chat-toggle-description = Mengaktifkan atau menonaktifkan pengiriman pesan untuk setiap saluran bahasa global. Pengaturan ini tetap ada setelah server dimulai ulang.
admin-moderation-global-chat-status-description = Status seluruh server saat ini. Hanya Pengembang yang dapat mengubah pengaturan ini.
admin-moderation-global-chat-update-failed = Pengaturan obrolan global tidak dapat disimpan, jadi tidak ada perubahan yang dilakukan. Silakan coba lagi.
global-chat-availability-enabled = Obrolan global telah diaktifkan oleh pengembang. Pilih saluran bahasa sebelum mengirim atau menerima pesan global.
global-chat-availability-disabled = Obrolan global untuk sementara dinonaktifkan oleh pengembang.
admin-moderation-section-reports = Laporan
admin-moderation-open-reports = Laporan terbuka: { $count }
admin-moderation-closed-reports = Laporan tertutup: { $count }
admin-moderation-all-reports = Semua laporan yang disimpan: { $count }
admin-moderation-section-messages = Riwayat pesan global
admin-moderation-browse-messages = Telusuri dan filter semua pesan global
admin-moderation-find-history = Temukan riwayat obrolan global berdasarkan nama pengguna
admin-moderation-retained-summary = Bukti tersimpan: { $messages } pesan global dan { $closed } laporan tertutup.
admin-moderation-section-retention = Penghapusan permanen
admin-moderation-clear-history = Hapus semua pesan obrolan global yang disimpan ({ $count })
admin-moderation-clear-closed-reports = Hapus semua laporan yang ditutup ({ $count })
admin-moderation-open-report-list = Laporan terbuka, yang terbaru dahulu
admin-moderation-closed-report-list = Laporan tertutup, yang terbaru terlebih dahulu
admin-moderation-all-report-list = Semua laporan yang disimpan, yang terbaru terlebih dahulu
admin-moderation-report-row = Laporan nomor { $id }, dikirim pada { $time }. Pengguna yang dilaporkan: { $target }, ID { $target_id }. Alasan: { $reason }. Pelapor: { $reporter }. Status: { $status }.
admin-moderation-no-reports = Tidak ada laporan yang cocok dengan tampilan ini.
admin-moderation-value-unknown = tidak diketahui
admin-moderation-status-open = terbuka
admin-moderation-status-reviewed = ditinjau
admin-moderation-status-dismissed = ditolak
admin-moderation-status-actioned = tindakan dicatat
admin-moderation-status-unknown = tidak diketahui
admin-moderation-report-unavailable = Laporan ini sudah tidak ada lagi. Pengembang lain mungkin telah menghapusnya.
admin-moderation-report-id = ID Laporan: { $id }
admin-moderation-report-time = Dikirim pada: { $time }
admin-moderation-report-status = Status: { $status }
admin-moderation-report-origin = Asal: { $origin }
admin-moderation-origin-manual = dikirimkan oleh pengguna
admin-moderation-origin-automatic = dihasilkan secara otomatis oleh Sistem
admin-moderation-report-reporter = Pelapor: { $username }. ID Akun: { $uuid }
admin-moderation-report-target = Pengguna yang dilaporkan: { $username }. ID Akun: { $uuid }
admin-moderation-report-reason = Alasan: { $reason }
admin-moderation-report-channel = Saluran konteks obrolan global: { $channel }
admin-moderation-report-scope = Terdeteksi di: { $scope }
admin-moderation-scope-global = obrolan global
admin-moderation-scope-table = obrolan meja
admin-moderation-detection-rate-limited = pesan terkirim terlalu cepat
admin-moderation-detection-repeated-message = pengulangan pesan yang sama
admin-moderation-automatic-evidence = Dibuat otomatis oleh Sistem untuk diperiksa secara manual. Tidak ada sanksi yang diterapkan. Di { $scope }, terdeteksi { $incidents } kejadian spam terpisah dan { $rejected } upaya ditolak selama periode pengamatan { $window }. Ada { $accepted } pesan terbaru yang diterima. Jenis deteksi: { $detection }. Pesan terakhir yang ditolak: { $sample }
admin-moderation-automatic-evidence-unavailable = Laporan ini dibuat secara otomatis oleh Sistem untuk peninjauan manual saja, dan tidak ada sanksi yang diterapkan. Bukti deteksi terstrukturnya tidak tersedia atau berasal dari versi yang tidak didukung.
admin-moderation-report-anchor = ID pesan acuan untuk konteks tersimpan: { $id }
admin-moderation-report-anchor-unavailable = Tidak ada pesan acuan untuk konteks tersimpan. Pengguna yang dilaporkan mungkin belum mengirim pesan yang tersimpan di saluran ini, atau riwayat obrolannya sudah dihapus.
admin-moderation-report-details = Detail tambahan: { $details }
admin-moderation-report-review = Ditinjau oleh { $reviewer }, ID akun { $reviewer_id }, pada { $time }.
admin-moderation-view-context = Lihat percakapan sekitar waktu laporan
admin-moderation-view-target-history = Lihat semua pesan global yang disimpan dari ID akun yang dilaporkan
admin-moderation-mark-reviewed = Tandai sudah ditinjau tanpa sanksi tercatat
admin-moderation-dismiss-report = Tolak laporan
admin-moderation-mark-actioned = Tandai tindakan telah dicatat. Ini tidak menerapkan sanksi.
admin-moderation-context-heading = Konteks untuk laporan nomor { $id }, dikirimkan { $time }. Saluran: { $channel }. Pesan bersifat kronologis, pesan pengguna yang dilaporkan diidentifikasi secara eksplisit.
admin-moderation-context-message = { $username }: { $message } Pesan nomor { $id }, dikirim { $time }. ID Akun: { $uuid }. Bahasa: { $channel }.
admin-moderation-context-target-message = Pengguna yang dilaporkan { $username }: { $message } Pesan nomor { $id }, dikirim { $time }. ID Akun: { $uuid }. Bahasa: { $channel }.
admin-moderation-context-anchor-message = Pesan acuan dari pengguna yang dilaporkan, { $username }: { $message } Pesan nomor { $id }, dikirim pada { $time }. ID akun: { $uuid }. Bahasa: { $channel }.
admin-moderation-context-empty = Tidak ada pesan global yang tersisa pada waktu laporan ini.
admin-moderation-copy-page =
    { $count ->
        [one] Salin pesan di halaman ini (1)
       *[other] Salin pesan di halaman ini ({ $count })
    }
admin-moderation-copy-page-success =
    { $count ->
        [one] Menyalin 1 pesan dari halaman ini ke papan klip.
       *[other] { $count } pesan dari halaman ini disalin ke papan klip.
    }
admin-moderation-copy-page-failed = Tidak dapat menyalin halaman ini ke papan klip. Periksa izin papan klip dan coba lagi.
admin-moderation-history-prompt = Masukkan nama pengguna secara lengkap untuk mencari riwayat obrolan global yang tersimpan. ID akun lama dengan nama pengguna yang sama akan ditampilkan secara terpisah.
admin-moderation-sender-results-heading = Identitas pengirim tersimpan dengan nama pengguna yang persis cocok dengan "{ $username }".
admin-moderation-sender-result = { $username }, ID akun { $uuid }. { $count } pesan dari { $first } hingga { $last }.
admin-moderation-no-sender-history = Tidak ada riwayat obrolan global yang disimpan yang cocok dengan nama pengguna persis "{ $username }".
admin-moderation-history-heading = Riwayat obrolan global tersimpan untuk { $username }, ID akun { $uuid }: { $count } pesan, yang terbaru dahulu.
admin-moderation-history-message = { $username }: { $message } Pesan nomor { $id }, dikirim { $time }. Bahasa: { $channel }.
admin-moderation-history-empty = Tidak ada pesan global yang disimpan untuk ID akun ini.
admin-moderation-message-list-heading = Riwayat pesan global. Ada { $count } pesan yang cocok. Urutan: { $sort }. Bahasa: { $channel }. Periode: { $period }. Semua waktu menggunakan UTC.
admin-moderation-message-row = { $username }: { $message } Pesan nomor { $id }, dikirim { $time }. ID Akun: { $uuid }. Bahasa: { $channel }.
admin-moderation-message-list-empty = Tidak ada pesan global yang disimpan yang cocok dengan filter ini.
admin-moderation-message-filter-sort = Urutan: { $sort }
admin-moderation-message-filter-language = Bahasa: { $channel }
admin-moderation-message-filter-period = Jangka waktu: { $period }
admin-moderation-message-filter-reset = Setel ulang semua filter pesan
admin-moderation-message-sort-newest = terbaru terlebih dahulu
admin-moderation-message-sort-oldest = terlama terlebih dahulu
admin-moderation-message-language-all = semua bahasa
admin-moderation-message-period-all = sepanjang waktu
admin-moderation-message-period-today = hari ini
admin-moderation-message-period-yesterday = kemarin
admin-moderation-message-period-last-7-days = 7 hari terakhir
admin-moderation-message-period-last-30-days = 30 hari terakhir
admin-moderation-message-period-current-month = bulan kalender saat ini
admin-moderation-message-period-previous-month = bulan kalender sebelumnya
admin-moderation-message-language-menu = Filter pesan berdasarkan bahasa. Filter saat ini adalah { $channel }.
admin-moderation-message-period-menu = Filter pesan berdasarkan periode waktu UTC. Filter saat ini adalah { $period }.
admin-moderation-message-filter-current = { $value } (saat ini)
admin-moderation-clear-history-confirm = Hapus permanen seluruh { $count } pesan obrolan global yang tersimpan? Tindakan ini tidak dapat dibatalkan. Sebanyak { $open } laporan terbuka tetap ada, tetapi pesan acuan dan konteks percakapannya akan dihapus.
admin-moderation-clear-closed-confirm = Hapus permanen seluruh { $count } laporan tertutup? Laporan terbuka dan riwayat obrolan global tetap ada. Tindakan ini tidak dapat dibatalkan.
admin-moderation-report-already-closed = Laporan ini sudah ditutup dalam peninjauan lain. Data terbarunya telah dimuat ulang.
admin-moderation-report-status-updated = Laporan nomor { $id } kini ditandai { $status }. Tidak ada sanksi otomatis yang diterapkan.
admin-new-manual-report = Laporan moderasi baru nomor { $id }: { $reporter } melaporkan { $target }.
admin-new-automatic-report = Laporan spam Sistem baru nomor { $id } memerlukan peninjauan manual: { $target }.
admin-moderation-history-cleared = Sebanyak { $count } pesan obrolan global tersimpan telah dihapus permanen. Laporan tetap ada tanpa pesan acuan. Jika tidak ada pesan yang tersisa, penomoran pesan dimulai lagi dari 1.
admin-moderation-closed-reports-cleared = Sebanyak { $count } laporan tertutup telah dihapus permanen. Laporan terbuka tetap ada. Jika tidak ada laporan yang tersisa, penomoran laporan dimulai lagi dari 1.
admin-database-management = Manajemen Basis Data
admin-database-management-summary = Pemeliharaan basis data khusus pengembang. Analisis bersifat hanya baca. Pencadangan, pembersihan, dan pemadatan menghentikan sementara permainan dan perubahan akun di seluruh server.
admin-database-backup = Cadangkan basis data
admin-database-backup-confirm = Cadangkan basis data sekarang? Perubahan permainan dan akun akan dijeda saat SQLite membuat dan memverifikasi snapshot pemulihan. Cadangan akan disimpan di direktori cadangan server sampai operator menghapusnya.
admin-database-backup-success = Pencadangan basis data selesai: { $filename } ({ $size }).
admin-database-backup-failed = Pencadangan basis data gagal. Tidak ada cadangan parsial yang dipublikasikan. Periksa log server untuk detailnya.
admin-database-size-bytes =
    { $value ->
        [one] 1 byte
       *[other] { NUMBER($value, maximumFractionDigits: 0) } byte
    }
admin-database-size-kib = { NUMBER($value, maximumFractionDigits: 1) } KiB
admin-database-size-mib = { NUMBER($value, maximumFractionDigits: 1) } MiB
admin-database-size-gib = { NUMBER($value, maximumFractionDigits: 1) } GiB
admin-database-storage-analyze = Analisis kandidat pembersihan
admin-database-storage-analysis-summary = Ukuran basis data: { $size }. Ruang SQLite yang dapat digunakan kembali: { $reusable }. Catatan basis data yang memenuhi syarat: { $records }.
admin-database-storage-analysis-failed = Analisis penyimpanan gagal tanpa mengubah data apa pun. Periksa log server untuk detailnya.
admin-database-storage-refresh-analysis = Segarkan analisis penyimpanan
admin-database-storage-cleanup = Jalankan pembersihan penyimpanan
admin-database-storage-cleanup-confirm = Jalankan pembersihan penyimpanan sekarang? Permainan dan perubahan akun akan dijeda saat server membuat dan memverifikasi cadangan pengaman. Server hanya menghapus catatan sementara atau catatan tanpa data terkait yang tercantum dalam daftar, lalu memvalidasi hasilnya. Berkas basis data tidak akan dipadatkan.
admin-database-storage-cleanup-not-needed = Pembersihan penyimpanan tidak diperlukan. Tidak ditemukan catatan basis data yang memenuhi syarat atau file cadangan sementara yang ditinggalkan.
admin-database-storage-cleanup-success = Pembersihan penyimpanan selesai. Catatan basis data dihapus: { $records }. File cadangan sementara yang terbengkalai dihapus: { $files } ({ $file_size }). Ruang SQLite yang dapat digunakan kembali: { $reusable }. Jalankan pemadatan secara terpisah untuk mengurangi ukuran file basis data. Cadangan pengaman: { $filename }.
admin-database-storage-cleanup-failed = Pembersihan penyimpanan gagal. Semua cadangan pengaman yang telah selesai disimpan. Periksa log server sebelum mencoba lagi.
admin-database-storage-no-record-candidates = Saat ini tidak ada catatan basis data yang memenuhi syarat untuk pembersihan aman.
admin-database-storage-temporary-files = File cadangan PlayAural sementara yang ditinggalkan: { $count } ({ $size }).
admin-database-storage-invalid-timestamps = Peringatan keamanan data: { $count } catatan memiliki waktu retensi yang tidak valid. Pembersihan tidak akan menebak usianya untuk menentukan apakah catatan tersebut kedaluwarsa. Periksa secara manual.
admin-database-storage-exclusions = Selalu dikecualikan dari pembersihan otomatis: meja tersimpan, hasil permainan, riwayat obrolan global, laporan moderasi, akun pengguna, blok valid, data aktif, statistik permainan terdaftar, data kompatibilitas, cadangan valid, dan log. Meja yang disimpan dihapus hanya melalui tindakan pemilik atau Pengembang yang eksplisit.
admin-database-storage-category-row = { $category }: { $count }
admin-database-storage-category-expired-table-checkpoints = Cadangan sementara kondisi meja yang telah kedaluwarsa
admin-database-storage-category-expired-password-reset-tokens = Token pengaturan ulang kata sandi sudah habis masa berlakunya
admin-database-storage-category-expired-bans = Catatan pencekalan disimpan selama lebih dari { $days } hari setelah habis masa berlakunya
admin-database-storage-category-stale-pending-friend-requests = Permintaan pertemanan yang tertunda lebih dari { $days } hari
admin-database-storage-category-orphaned-friendships = Catatan pertemanan yang tidak lagi memiliki akun terkait
admin-database-storage-category-orphaned-user-blocks = Catatan pemblokiran pengguna yang tidak lagi memiliki akun terkait
admin-database-storage-category-stale-user-notifications = Notifikasi pengguna lebih lama dari { $days } hari
admin-database-storage-category-orphaned-user-notifications = Catatan pemberitahuan yang tidak lagi memiliki akun terkait
admin-database-storage-category-expired-mutes = Catatan pembisuan yang telah kedaluwarsa
admin-database-storage-category-orphaned-mutes = Catatan pembisuan yang tidak lagi memiliki akun terkait
admin-database-compact = Padatkan basis data untuk mengosongkan ruang yang tidak terpakai
admin-database-compact-confirm = Padatkan basis data sekarang? Permainan dan perubahan akun akan dijeda. Cadangan pengaman akan dibuat dan diverifikasi sebelum SQLite membangun ulang basis data aktif. Proses ini membutuhkan ruang penyimpanan sementara yang besar dan sebaiknya dijalankan saat server tidak sibuk.
admin-database-compact-success = Pemadatan basis data selesai. Ukuran berkas berubah dari { $before } menjadi { $after }. Ruang sebesar { $reclaimed } berhasil dikosongkan. Cadangan pengaman: { $filename }.
admin-database-compact-failed = Pemadatan basis data gagal. Proses ini tidak melakukan perubahan yang disengaja pada basis data aktif. Semua cadangan pengaman yang selesai dibuat tetap disimpan. Periksa log server untuk informasi lebih lanjut.
admin-database-maintenance-busy = Operasi server eksklusif lainnya sudah aktif. Tunggu hingga selesai sebelum memulai pemeliharaan basis data.
database-maintenance-operation-backup = pencadangan basis data
database-maintenance-operation-cleanup = pembersihan penyimpanan
database-maintenance-operation-compaction = pemadatan basis data
database-maintenance-not-active = Pemeliharaan basis data saat ini tidak aktif.
database-maintenance-input-blocked = Proses { $operation } pada server sedang berlangsung. Permainan, proses masuk, pendaftaran, dan perubahan akun dijeda. Menu saat ini tetap tersedia, tetapi tindakan baru dapat dijalankan setelah pemeliharaan selesai.
database-maintenance-auth-blocked = Pemeliharaan basis data server sedang berlangsung. Login, registrasi, dan perubahan kata sandi untuk sementara tidak tersedia. Silakan coba lagi setelah pemeliharaan selesai.
database-maintenance-backup-started = Pengembang sedang membuat cadangan basis data server. Perubahan permainan dan akun dihentikan sementara, menu saat ini tetap terlihat. Anda akan diberi tahu ketika layanan normal dilanjutkan.
database-maintenance-backup-completed = Pencadangan basis data server selesai. Permainan normal dan akses akun dilanjutkan sekarang.
database-maintenance-backup-failed = Pencadangan basis data server tidak dapat diselesaikan. Tidak ada cadangan parsial yang dipublikasikan. Permainan normal dan akses akun dilanjutkan sekarang.
database-maintenance-cleanup-started = Pengembang sedang melakukan pembersihan penyimpanan server. Perubahan permainan dan akun untuk sementara dihentikan, namun menu saat ini tetap terlihat. Cadangan pengaman terverifikasi sedang dibuat terlebih dahulu. Anda akan diberi tahu ketika layanan normal dilanjutkan.
database-maintenance-cleanup-completed = Pembersihan penyimpanan server dan validasi basis data selesai. Permainan normal dan akses akun dilanjutkan sekarang.
database-maintenance-cleanup-failed = Pembersihan penyimpanan server tidak dapat diselesaikan dengan aman. Permainan normal dan akses akun dilanjutkan sekarang.
database-maintenance-compaction-started = Pengembang sedang memadatkan basis data server. Perubahan permainan dan akun dihentikan sementara, menu saat ini tetap terlihat. Anda akan diberi tahu ketika layanan normal dilanjutkan.
database-maintenance-compaction-completed = Pemadatan basis data server selesai. Permainan normal dan akses akun dilanjutkan sekarang.
database-maintenance-compaction-failed = Pemadatan basis data server tidak dapat diselesaikan. Permainan normal dan akses akun dilanjutkan tanpa menerapkan pemadatan.
database-maintenance-reopen-failed = Kesalahan pemeliharaan basis data kritis: basis data aktif tidak dapat dibuka kembali dengan aman, sehingga server tetap dibekukan. Harap tunggu hingga pengembang memulihkan layanan.
account-approval = Persetujuan Akun
no-pending-accounts = Tidak ada akun yang tertunda.
approve-account = Setujui
decline-account = Tolak
account-approved = Akun { $player } telah disetujui.
account-declined = Akun { $player } telah ditolak dan dihapus.
waiting-for-approval = Akun Anda sedang menunggu persetujuan dari administrator. Mohon tunggu...
account-approved-welcome = Akun Anda telah disetujui! Selamat datang di PlayAural!
account-declined-goodbye = Permintaan akun Anda telah ditolak.
account-action = tindakan akun telah dilakukan
promote-admin = Promosikan Admin
demote-admin = Turunkan Admin
ban-user = Cekal pengguna
unban-user = Cabut pencekalan pengguna
no-users-to-promote = Tidak ada pengguna yang tersedia untuk dipromosikan.
no-admins-to-demote = Tidak ada admin yang dapat diturunkan.
admin-search-users = Cari berdasarkan nama pengguna
admin-search-users-current = Cari berdasarkan nama pengguna. Pencarian saat ini: { $query }.
admin-search-prompt = Masukkan seluruh atau sebagian nama pengguna. Kosongkan untuk menelusuri semua hasil per halaman.
menu-page-summary = Menampilkan entri { $start } hingga { $end } dari { $total }. Halaman { $page } dari { $pages }.
menu-page-summary-query = Pencarian "{ $query }": entri { $start } hingga { $end } dari { $total }. Halaman { $page } dari { $pages }.
menu-page-refresh = Segarkan daftar
menu-list-refreshed = Daftar disegarkan.
menu-page-first = Halaman pertama
menu-page-previous = Halaman sebelumnya
menu-page-next = Halaman berikutnya
menu-page-last = Halaman terakhir
admin-search-no-results = Tidak ditemukan pengguna yang cocok. Gunakan Cari berdasarkan nama pengguna untuk mencoba istilah lain.
confirm-promote = Apakah Anda yakin ingin mempromosikan { $player } ke admin?
confirm-demote = Apakah Anda yakin ingin menurunkan { $player } dari admin?
admin-role-target-changed = { $player } tidak lagi memiliki peran yang diharapkan. Segarkan daftar dan coba lagi.
broadcast-to-all = Umumkan kepada semua pengguna
broadcast-to-admins = Umumkan hanya kepada admin
broadcast-to-nobody = Diam (tidak ada pengumuman)
promote-announcement = { $player } telah dipromosikan menjadi admin!
promote-announcement-you = Anda telah dipromosikan menjadi admin!
promote-announcement-actor = Anda mempromosikan { $player } menjadi admin!
demote-announcement = { $player } telah diturunkan dari admin.
demote-announcement-you = Anda telah diturunkan dari admin.
demote-announcement-actor = Anda menurunkan { $player } dari admin.
not-admin-anymore = Anda bukan lagi admin dan tidak dapat melakukan tindakan ini.
dev-only-action = Tindakan ini dibatasi hanya untuk Pengembang.
ban-duration-1h = 1 jam
ban-duration-6h = 6 jam
ban-duration-12h = 12 jam
ban-duration-1d = 1 hari
ban-duration-3d = 3 hari
ban-duration-1w = 1 minggu
ban-duration-1m = 1 bulan
ban-duration-permanent = Permanen
reason-spam = Spam
reason-harassment = Pelecehan
reason-cheating = Kecurangan
reason-inappropriate = Perilaku yang tidak pantas
reason-custom = Alasan lain
no-users-to-ban = Tidak ada pengguna yang dapat dicekal.
no-banned-users = Saat ini tidak ada pengguna yang dicekal.
admin-active-ban-entry = { $username }. Pencekalan berakhir: { $expires }. Alasan: { $reason }. Diterapkan oleh: { $admin }.
admin-active-mute-entry = { $username }. Pembisuan berakhir: { $expires }. Alasan: { $reason }. Diterapkan oleh: { $admin }.
admin-penalty-expiry-permanent = permanen
admin-penalty-expiry-unknown = waktu berakhir tidak diketahui
admin-penalty-expiry-expired = sudah kedaluwarsa
admin-penalty-expiry-timed = { $date } ({ $remaining } tersisa)
admin-penalty-reason-unknown = alasan yang tidak ditentukan
admin-penalty-admin-unknown = administrator yang tidak dikenal
admin-penalty-remaining-days =
    { $count ->
        [one] 1 hari
       *[other] { $count } hari
    }
admin-penalty-remaining-hours =
    { $count ->
        [one] 1 jam
       *[other] { $count } jam
    }
admin-penalty-remaining-minutes =
    { $count ->
        [one] 1 menit
       *[other] { $count } menit
    }
admin-penalty-remaining-less-minute = kurang dari 1 menit
ban-broadcast = { $target } dicekal oleh { $actor } karena { $reason }. Durasi: { $duration }.
ban-broadcast-actor = Anda mencekal { $target } karena { $reason }. Durasi: { $duration }.
unban-broadcast = Pencekalan { $target } dicabut oleh { $actor }.
unban-broadcast-actor = Anda mencabut pencekalan { $target }.
unban-broadcast-target = Pencekalan Anda dicabut oleh { $actor }.
banned-menu-title = Akun dicekal
banned-reason = Alasan: { $reason }
banned-expires = Kedaluwarsa: { $expires }
banned-permanent = Kedaluwarsa: Permanen
disconnect = Putuskan sambungan
mute-user = Bisukan Pengguna
unmute-user = Cabut pembisuan pengguna
no-users-to-mute = Tidak ada pengguna yang dapat dibisukan.
no-muted-users = Tidak ada pengguna yang dibisukan saat ini.
mute-duration-5m = 5 menit
mute-duration-15m = 15 menit
mute-duration-30m = 30 menit
mute-duration-1h = 1 jam
mute-duration-6h = 6 jam
mute-duration-1d = 1 hari
mute-duration-permanent = Permanen
mute-broadcast = { $target } dibisukan oleh { $actor } karena { $reason }. Durasi: { $duration }.
mute-broadcast-actor = Anda membisukan { $target } karena { $reason }. Durasi: { $duration }.
unmute-broadcast = Pembisuan { $target } dicabut oleh { $actor }.
unmute-broadcast-actor = Anda mencabut pembisuan { $target }.
you-have-been-muted = Anda dibisukan. Alasan: { $reason }. Durasi: { $duration }.
you-have-been-unmuted = Pembisuan Anda dicabut. Anda dapat mengobrol lagi.
muted-remaining-seconds = Anda dibisukan. Tersisa { $seconds } detik.
muted-remaining-minutes = Anda dibisukan. Tersisa { $minutes } menit.
muted-permanent = Anda dibisukan tanpa batas waktu. Hubungi administrator untuk informasi lebih lanjut.
chat-rate-limited = Pelan-pelan! Anda mengirim pesan terlalu cepat.
chat-repeated-message = Tolong jangan ulangi pesan yang sama.
chat-global-disabled-send = Obrolan global dinonaktifkan di pengaturan Anda. Aktifkan kembali obrolan global sebelum mengirim pesan global.
chat-global-channel-required-send = Pilih bahasa untuk obrolan global sebelum mengirim pesan. Obrolan global tidak dipantau secara langsung. Jika seseorang menggunakan kata-kata kotor atau menghina Anda, blokir pengguna tersebut. Silakan laporkan penyalahgunaan yang serius atau berulang untuk ditinjau nanti.
chat-global-log-unavailable = Obrolan global untuk sementara tidak tersedia karena pesan ini tidak dapat disimpan dengan aman. Silakan coba lagi nanti.
chat-table-disabled-send = Obrolan meja dinonaktifkan di pengaturan Anda. Aktifkan kembali obrolan meja sebelum mengirim pesan meja.
chat-global-temporarily-disabled-send = Obrolan global untuk sementara dinonaktifkan oleh pengembang.
chat-invalid-channel = Saluran obrolan itu tidak tersedia.
communication-channel-table = Obrolan Meja
communication-channel-global = Obrolan Global
communication-channel-team = Obrolan Tim
communication-channel-selected = { $channel } dipilih.
communication-channel-stale = Saluran komunikasi itu tidak lagi tersedia. Pilihan saluran Anda telah disegarkan.
communication-text-restricted = Anda tidak dapat mengirim pesan di saluran ini sekarang.
communication-chat-message = { $player } di { $channel }: { $message }
communication-chat-message-you = Anda di { $channel }: { $message }
communication-voice-room-label = Suara { $channel }
communication-voice-restricted = Saat ini mikrofon Anda tidak dapat digunakan di saluran ini.
communication-voice-not-connected = Obrolan Suara harus terhubung sebelum Anda dapat menggunakan mikrofon.
chat-invalid-message = Pesan tersebut tidak dapat dikirim karena formatnya tidak valid.
chat-message-too-long = Pesan terlalu panjang. Maksimal { $limit } karakter.
report-user = Laporkan pengguna
enter-report-username = Masukkan nama pengguna yang akan dilaporkan.
report-error-self = Anda tidak dapat melaporkan akun Anda sendiri.
report-select-reason = Laporkan { $username }: pilih alasan yang paling menggambarkan perilaku tersebut.
report-reason-spam = Spam atau gangguan berulang
report-reason-harassment = Pelecehan atau penghinaan pribadi
report-reason-hateful-content = Konten yang penuh kebencian
report-reason-sexual-content = Konten seksual
report-reason-threats = Ancaman untuk menyakiti
report-reason-personal-information = Berbagi informasi pribadi
report-reason-other = Pelanggaran berat lainnya
report-channel-unspecified = tidak ada saluran obrolan global yang dipilih
report-confirm-summary = Laporkan { $username } untuk { $reason }. Saluran konteks: { $channel }. Laporan akan disimpan untuk ditinjau secara manual. Pengguna tidak akan diberi tahu atau secara otomatis dikenakan sanksi.
report-submit = Kirim laporan
report-change-reason = Ubah alasan
report-submitted = Laporan Anda tentang { $username } beserta waktu pengirimannya telah disimpan untuk ditinjau secara manual. Pengguna tersebut tidak diberi tahu. Anda juga dapat memblokirnya untuk menghentikan kontak langsung dan menyembunyikan pesan globalnya.
report-target-cooldown = Anda baru saja melaporkan { $username }. Tunggu { $duration } sebelum mengirim laporan lagi. Gunakan Blokir sekarang jika Anda tidak ingin menerima pesannya.
report-rate-limited = Anda telah mengirimkan beberapa laporan baru-baru ini. Coba lagi setelah { $duration }.
report-failed = Laporan tersebut tidak dapat disimpan dengan aman. Silakan coba lagi nanti.
broadcast-announcement = Siarkan pengumuman
admin-broadcast-prompt = Masukkan pengumuman untuk semua pengguna yang online. Pesan ini akan dikirim kepada mereka semua.
admin-broadcast-sent = Pengumuman dikirim ke { $count } pengguna.
manage-motd = Kelola Pesan Hari Ini
create-update-motd = Buat/Perbarui Pesan Hari Ini
view-motd = Lihat Pesan Hari Ini
delete-motd = Hapus Pesan Hari Ini
motd-version-prompt = Masukkan nomor versi Pesan Hari Ini yang baru. Angka harus lebih besar dari nol:
invalid-motd-version = Versi Pesan Hari Ini tidak valid. Itu harus berupa angka positif.
motd-created = Versi Pesan Hari Ini { $version } telah berhasil dibuat.
motd-deleted = Pesan Hari Ini telah dihapus.
motd-delete-empty = Tidak ada Pesan Hari Ini untuk dihapus.
motd-not-exists = Tidak ada Pesan Hari Ini yang aktif.
motd-announcement = Pesan Hari Ini
motd-broadcast = Pesan Hari Ini yang baru: { $message }
error-no-languages = Kesalahan: Tidak ditemukan bahasa.
ok = Oke
admin-localized-text-subject-motd = Pesan Hari Ini
admin-localized-text-subject-power = alasan pengelolaan daya server
admin-localized-text-subject-ban = alasan khusus pencekalan
admin-localized-text-subject-mute = alasan khusus pembisuan
admin-localized-text-instructions = Edit terjemahan { $subject }. Bahasa resmi diperlukan. Bahasa komunitas bersifat opsional dan gunakan { $fallback } jika kosong.
admin-localized-text-motd-version = Versi Pesan Hari Ini: { $version }
admin-localized-text-official-heading = Bahasa resmi, wajib diisi
admin-localized-text-community-heading = Bahasa komunitas, opsional
admin-localized-text-field = { $language }: { $status }
admin-localized-text-required-set = sudah diisi, wajib
admin-localized-text-required-missing = belum diisi, wajib
admin-localized-text-optional-set = sudah diisi, opsional
admin-localized-text-optional-fallback = belum diisi, opsional, menggunakan bahasa pengganti
admin-localized-text-prompt = Masukkan { $subject } dalam bahasa { $language }. Maksimal { $max } karakter.
admin-localized-text-too-long = Terjemahan terlalu panjang. Maksimal { $max } karakter.
admin-localized-text-missing-required = Isi semua terjemahan yang wajib terlebih dahulu. Belum diisi: { $languages }.
admin-localized-text-publish-motd = Publikasikan Pesan Hari Ini
admin-localized-text-continue = Lanjutkan
admin-localized-text-apply-ban = Terapkan pencekalan
admin-localized-text-apply-mute = Terapkan pembisuan
unknown-player = Pemain tidak dikenal
unknown-user = Pengguna tidak dikenal
user-account-unavailable = Akun pengguna ini tidak lagi tersedia.
logout-confirm-title = Yakin ingin keluar dari akun dan menutup permainan?
logout-confirm-yes = Ya, keluar
logout-confirm-no = Tidak, tetap di sini
system-name = Sistem
server-restarting = Server dimulai ulang dalam { $seconds } detik...
server-shutting-down = Server dimatikan dalam { $seconds } detik...
server-shutting-down-now = Server sedang dimatikan sekarang. Selamat tinggal!
server-power-management = Manajemen Daya Server
server-power-reboot = Mulai ulang server
server-power-shutdown = Matikan Server
server-power-cancel = Batalkan jadwal pengelolaan daya
server-power-active-status = { $action } terjadwal. Alasan: { $reason }.
server-power-action-reboot = mulai ulang
server-power-action-shutdown = pematian
server-power-delay-30s = Dalam 30 detik
server-power-delay-1m = Dalam 1 menit
server-power-delay-5m = Dalam 5 menit
server-power-delay-10m = Dalam 10 menit
server-power-delay-30m = Dalam 30 menit
server-power-delay-1h = Dalam 1 jam
server-power-delay-2h = Dalam 2 jam
server-power-delay-custom = Penundaan khusus dalam hitungan menit
server-power-custom-delay-prompt = Masukkan waktu tunggu dalam menit, dari 1 hingga { $max }:
server-power-invalid-custom-delay = Waktu tunggu tidak valid. Masukkan bilangan bulat dari 1 hingga { $max } menit.
server-power-reason-update = Pembaruan
server-power-reason-maintenance = Pemeliharaan
server-power-reason-security = Keamanan
server-power-reason-technical = Masalah teknis
server-power-reason-custom = Alasan khusus
server-power-reason-unspecified = alasan yang tidak ditentukan
server-power-confirm-summary = Konfirmasi { $action } server dalam { $duration }. Alasan: { $reason }.
server-power-scheduled = Proses { $action } server dijadwalkan dalam { $duration }.
server-power-already-scheduled = Tindakan daya server sudah dijadwalkan. Batalkan sebelum menjadwalkan yang lain.
server-power-cancel-none = Tidak ada tindakan daya server yang dijadwalkan saat ini.
server-power-cancelled = Tindakan daya server terjadwal dibatalkan.
server-power-cancelled-broadcast = { $admin } membatalkan jadwal { $action } server.
server-power-cancelled-broadcast-you = Anda membatalkan jadwal { $action } server.
server-power-command-removed = Perintah obrolan /reboot dan /stop telah dihapus. Gunakan Administrasi, Manajemen Daya Server sebagai gantinya.
server-power-finalizing-input-blocked = Server sedang menyelesaikan proses mulai ulang atau pematian. Tunggu hingga aplikasi memutuskan koneksi.
server-power-maintenance-active = Operasi daya server tidak dapat dijadwalkan saat pemeliharaan basis data aktif. Tunggu hingga pemeliharaan selesai dan coba lagi.
server-power-finalize-failed = Proses { $action } server yang dijadwalkan tidak dapat diselesaikan dengan aman. Server tetap online. Hubungi administrator.
server-power-reboot-warning = Server akan dimulai ulang dalam { $duration }. Alasan: { $reason }. Jangan putuskan koneksi secara manual. Aplikasi Anda akan terhubung kembali secara otomatis dan meja aktif akan dipertahankan.
server-power-shutdown-warning = Server akan dimatikan dalam { $duration }. Alasan: { $reason }. Server akan offline. Simpan permainan yang ingin Anda lanjutkan sebelum server dimatikan.
server-power-reboot-now = Server sedang dimulai ulang. Alasan: { $reason }. Jangan putuskan koneksi secara manual. Aplikasi Anda akan terhubung kembali secara otomatis dan meja aktif akan dipertahankan.
server-power-shutdown-now = Server sedang dimatikan sekarang. Alasan: { $reason }. Server sedang offline.
server-power-restore-waiting = Meja ini dipulihkan setelah server dimulai ulang sesuai jadwal. Menunggu hingga { $seconds } detik agar pemain lain terhubung kembali sebelum pemain yang belum kembali digantikan bot.
server-power-restore-input-blocked = Meja ini masih dipulihkan setelah server dimulai ulang sesuai jadwal. Permainan dijeda hingga { $seconds } detik lagi sambil menunggu { $players }. Coba lagi setelah waktu tunggu berakhir.
server-power-restore-missing-players-fallback = pemain yang tersisa
server-power-restore-complete = Semua pemain aktif telah terhubung kembali setelah server dimulai ulang sesuai jadwal. Permainan dilanjutkan.
server-power-restore-complete-with-bots = Waktu tunggu untuk terhubung kembali setelah server dimulai ulang telah habis. Pemain yang belum kembali digantikan bot dan permainan dilanjutkan.
duration-seconds =
    { $count ->
        [one] 1 detik
       *[other] { $count } detik
    }
duration-minutes =
    { $count ->
        [one] 1 menit
       *[other] { $count } menit
    }
duration-hours =
    { $count ->
        [one] 1 jam
       *[other] { $count } jam
    }
duration-minutes-seconds = { $minutes } menit dan { $seconds } detik
duration-hours-minutes = { $hours } jam dan { $minutes } menit
server-error-changing-language = Bahasa tidak dapat diubah. Antarmuka tetap menggunakan bahasa sebelumnya.
default-save-name = { $game } - { $date }
speech-settings = Pengaturan suara pembaca
speech-mode-option = Mode Ucapan: { $status }
speech-rate-option = Kecepatan Bicara: { $value }%
speech-voice-option = Suara: { $voice }
select-voice = Pilih Suara
invalid-rate = Kecepatan bicara tidak valid. Gunakan nilai antara 50 dan 300.
mode-aria = ARIA live
mode-web-speech = Web Speech API
default-voice = Suara Bawaan
mobile-speech-settings = Pengaturan suara pembaca seluler
mobile-tts-engine-option = Mesin TTS: { $engine }
mobile-tts-engine-system = Bawaan sistem
mobile-tts-engine-system-selected = Mesin TTS bawaan sistem
mobile-tts-engine-api-note = Pada versi aplikasi ini, mesin pembaca teks Android dipilih melalui pengaturan sistem.
mobile-tts-voice-option = Suara Seluler: { $voice }
mobile-tts-rate-option = Kecepatan Bicara Seluler: { $value }%
mobile-tts-enter-rate = Masukkan kecepatan bicara seluler, dari 50 hingga 200
mobile-tts-invalid-rate = Kecepatan bicara seluler tidak valid. Gunakan nilai antara 50 dan 200.
player-kicked-offline = Pemain { $player } dikeluarkan karena offline.
game-paused-host-disconnect = Permainan dijeda. Menunggu { $player } terhubung kembali...
game-resumed = { $player } terhubung kembali. Permainan dilanjutkan!
game-resumed-you = Anda terhubung kembali. Permainan dilanjutkan!
auth-error-username-length = Nama pengguna harus antara 3 dan 30 karakter.
auth-error-username-invalid-chars = Nama pengguna hanya boleh berisi huruf, angka, dan spasi (tidak ada spasi berurutan, dan tidak ada karakter khusus).
auth-error-password-weak = Kata sandi harus terdiri dari minimal 8 karakter dan mengandung huruf dan angka.
personal-and-options = Pribadi dan Pengaturan
profile = Profil
friends = Teman
profile-registration-date = Tanggal Pendaftaran: { $date }
profile-date-unknown = Tidak diketahui
profile-username = Nama pengguna: { $username }
profile-email = Email: { $email }
admin-view-email = Tampilan Admin - Email: { $email }
profile-gender = Gender: { $gender }
profile-bio = Tentang diri: { $bio }
profile-bio-empty = Tidak disetel
profile-email-empty = Tidak disetel
gender-male = Laki-laki
gender-female = Perempuan
gender-non-binary = Non-biner
gender-not-set = Tidak disetel
# Shared grammatical forms for account gender. Games may override any form by
# defining <context>-gender-term-<form> and passing that context to GENDER_TERM.
gender-term-subject =
    { $gender ->
        [male] dia
        [female] dia
       *[other] dia
    }
gender-term-subject-capitalized =
    { $gender ->
        [male] Dia
        [female] Dia
       *[other] Dia
    }
gender-term-subject-be =
    { $gender ->
        [male] dia
        [female] dia
       *[other] dia
    }
gender-term-subject-be-capitalized =
    { $gender ->
        [male] Dia
        [female] Dia
       *[other] Dia
    }
gender-term-subject-have =
    { $gender ->
        [male] dia memiliki
        [female] dia memiliki
       *[other] dia memiliki
    }
gender-term-subject-have-capitalized =
    { $gender ->
        [male] Dia memiliki
        [female] Dia memiliki
       *[other] Dia memiliki
    }
gender-term-object =
    { $gender ->
        [male] dia
        [female] dia
       *[other] dia
    }
gender-term-possessive-determiner =
    { $gender ->
        [male] miliknya
        [female] miliknya
       *[other] miliknya
    }
gender-term-possessive-determiner-capitalized =
    { $gender ->
        [male] Miliknya
        [female] Miliknya
       *[other] Miliknya
    }
gender-term-possessive-pronoun =
    { $gender ->
        [male] miliknya
        [female] miliknya
       *[other] miliknya
    }
gender-term-reflexive =
    { $gender ->
        [male] dirinya sendiri
        [female] dirinya sendiri
       *[other] dirinya sendiri
    }
action-set-edit = Atur / Sunting
action-delete = Hapus
bio-already-empty = Keterangan tentang diri Anda sudah kosong.
bio-deleted = Keterangan tentang diri Anda dihapus.
bio-updated = Keterangan tentang diri Anda diperbarui.
enter-email = Masukkan alamat email baru:
email-updated = Alamat email diperbarui.
enter-bio = Ceritakan tentang diri Anda:
gender-updated = Gender diperbarui.
no-changes-made = Tidak ada perubahan yang dilakukan.
confirm-email-change = Apakah Anda yakin ingin mengubah email Anda menjadi { $email }?
mandatory-email-notice = Anda harus mengatur email untuk terus berpartisipasi. Email Anda bersifat pribadi dan hanya Anda yang mengetahuinya.
error-email-empty = Email wajib diisi dan tidak boleh kosong.
error-email-invalid = Format email tidak valid. Harap berikan alamat email yang valid.
reg-error-email = Email diperlukan untuk mendaftar.
error-email-taken = Email ini sudah digunakan oleh akun lain.
error-bio-length = Keterangan tentang diri Anda maksimal 250 karakter.
error-captcha-failed = Verifikasi gagal. Silakan coba lagi.
error-rate-limit-login = Terlalu banyak upaya login yang gagal. Silakan coba lagi dalam 15 menit.
error-rate-limit-register = Anda telah mencapai jumlah maksimum pendaftaran akun untuk hari ini.
auth-error-rate-limit = { error-rate-limit-login }
friends-my-friends = Daftar teman saya
friends-pending-requests = Permintaan yang Tertunda ({ $count })
friends-no-pending-requests = Permintaan yang Tertunda
friends-sent-requests =
    { $count ->
        [0] Permintaan Terkirim
       *[other] Permintaan Terkirim ({ $count })
    }
friends-send-request = Kirim Permintaan Pertemanan
friends-block-user = Blokir Pengguna
enter-block-username = Masukkan nama pengguna yang ingin Anda blokir:
friends-blocked-users =
    { $count ->
        [0] Pengguna yang Diblokir
       *[other] Pengguna yang Diblokir ({ $count })
    }
friends-blocked-empty = Anda belum memblokir siapa pun.
friends-list-empty = Anda belum punya teman.
friend-status-offline = Offline
friend-status-offline-last-online = Offline, terakhir online { $relative_time }
friend-list-entry = { $username } ({ $status })
view-profile = Lihat Profil
block-user = Blokir Pengguna
unblock-user = Buka blokir Pengguna
join-table = Bergabung ke meja
remove-friend = Hapus Teman
friend-remove-confirm = Hapus { $username } dari daftar teman Anda?
friend-remove-not-friends = { $username } tidak lagi ada dalam daftar teman Anda.
already-in-table = Anda sudah berada di meja.
friend-removed-success = { $username } telah dihapus dari daftar teman Anda.
friend-removed-notify = { $username } menghapus Anda dari daftar temannya.
no-pending-requests = Tidak ada permintaan yang tertunda.
no-sent-requests = Anda tidak memiliki permintaan terkirim yang tertunda.
friend-request-to = Permintaan pertemanan dikirim ke { $username }
accept = Terima
decline = Tolak
friend-accepted-success = Anda sekarang berteman dengan { $username }.
friend-accepted-notify = { $username } telah menerima permintaan pertemanan Anda!
request-not-found = Permintaan pertemanan sudah tidak ada lagi.
friend-declined-success = Permintaan pertemanan ditolak.
friend-declined-notify = { $username } menolak permintaan pertemanan Anda.
friend-request-manage-sent = Kelola Permintaan Pertemanan Terkirim
friend-request-accept-action = Terima Permintaan Pertemanan
friend-request-cancel-action = Batalkan Permintaan Pertemanan
friend-request-cancel-confirm = Batalkan permintaan pertemanan Anda yang tertunda ke { $username }?
friend-request-cancelled = Permintaan pertemanan Anda ke { $username } dibatalkan.
friend-request-cancel-unavailable = Permintaan pertemanan ini tidak lagi tertunda, jadi tidak dibatalkan.
relative-time-just-now = baru saja
relative-time-minutes-ago =
    { $count ->
        [one] 1 menit yang lalu
       *[other] { $count } menit yang lalu
    }
relative-time-hours-ago =
    { $count ->
        [one] 1 jam yang lalu
       *[other] { $count } jam yang lalu
    }
relative-time-days-ago =
    { $count ->
        [one] 1 hari yang lalu
       *[other] { $count } hari yang lalu
    }
relative-time-weeks-ago =
    { $count ->
        [one] 1 minggu yang lalu
       *[other] { $count } minggu yang lalu
    }
relative-time-months-ago =
    { $count ->
        [one] 1 bulan yang lalu
       *[other] { $count } bulan yang lalu
    }
relative-time-years-ago =
    { $count ->
        [one] 1 tahun yang lalu
       *[other] { $count } tahun yang lalu
    }
enter-friend-username = Masukkan nama pengguna yang ingin Anda tambahkan sebagai teman:
friend-error-self = Anda tidak dapat mengirim permintaan pertemanan kepada diri Anda sendiri.
friend-error-already-friends = Anda sudah berteman dengan pengguna ini.
friend-error-duplicate = Anda sudah memiliki permintaan pertemanan yang tertunda untuk pengguna ini.
friend-error-blocked-by-you = Anda memblokir { $username }. Buka blokirnya sebelum mengirim permintaan pertemanan.
friend-error-blocked = Permintaan pertemanan tidak tersedia antara Anda dan { $username }.
friend-request-sent = Permintaan pertemanan dikirim ke { $username }.
friend-request-received = Anda telah menerima permintaan pertemanan baru dari { $username }.
block-confirm = Blokir { $username }? Pertemanan dan permintaan pertemanan yang tertunda di antara Anda akan dihapus. Anda berdua tidak dapat saling mengirim permintaan pertemanan, pesan pribadi, atau undangan meja. Pesan obrolan biasa akan disembunyikan dari satu sama lain. Selama blokir berlaku, Anda berdua tidak dapat memasuki meja milik satu sama lain atau memulihkan meja tersimpan yang berisi Anda berdua. Pemblokiran tidak mengeluarkan Anda dari meja yang sama, menghalangi pengambilan kembali tempat yang telah dicadangkan, atau membisukan obrolan suara.
block-success = Anda memblokir { $username }. Kontak langsung di antara Anda kini dibatasi dan pesan obrolan biasa disembunyikan dari satu sama lain. Anda berdua tidak dapat memasuki meja milik satu sama lain atau memulihkan meja tersimpan yang berisi Anda berdua.
block-error-self = Anda tidak dapat memblokir diri Anda sendiri.
block-already-active = Anda telah memblokir { $username }.
block-no-longer-active = Pemblokiran ini sudah tidak aktif.
unblock-success = Anda membuka blokir { $username }. Pertemanan dan permintaan sebelumnya tidak dipulihkan.
friends-grouped-requests = Anda memiliki permintaan pertemanan yang tertunda dari: { $usernames }
friends-grouped-accepted = Permintaan pertemanan Anda diterima oleh: { $usernames }
friends-grouped-declined = Permintaan pertemanan Anda ditolak oleh: { $usernames }
friends-grouped-removed = Anda dihapus dari daftar teman oleh: { $usernames }
friends-and-others =
    { $names } dan { $count } { $count ->
        [one] lainnya
       *[other] lainnya
    }
send-private-message = Kirim Pesan Pribadi
enter-pm-message = Masukkan pesan untuk { $username }:
pm-error-not-friends = Anda hanya dapat mengirim pesan pribadi ke teman.
pm-error-blocked = Pesan pribadi tidak tersedia antara Anda dan pengguna ini.
pm-error-offline = { $username } saat ini tidak online.
pm-error-self = Anda tidak dapat mengirim pesan pribadi ke diri Anda sendiri.
pm-error-message-required = Masukkan pesan pribadi. Jika melalui obrolan, sertakan nama pengguna, misalnya @NamaPengguna halo.
pm-sent-content = Anda ke { $username }: { $message }
pm-received = Pesan pribadi dari { $username }: { $message }
host-management = Pengelolaan meja
table-spectator-suffix = (Penonton)
host-management-set-private = Jadikan meja privat
host-management-set-public = Jadikan meja publik
host-management-invite = Undang Teman
host-management-voice = Kelola Obrolan Suara
host-management-switch-game = Beralih ke Permainan Lain
host-management-pass-host = Alihkan kepemilikan meja ke pemain lain
host-management-kick = Keluarkan pemain
host-management-kick-ban = Keluarkan dan cekal pemain
host-management-player-substitution = Pergantian Pemain
host-management-restart-game = Mulai ulang Permainan
host-management-table-now-private = Meja ini sekarang privat. Hanya pengguna yang diundang yang dapat bergabung.
host-management-table-now-public = Meja ini sekarang bersifat publik.
host-game-switch-current =
    Permainan saat ini: { $game }. Meja ini memiliki { $seats } { $seats ->
        [one] tempat pemain aktif
       *[other] tempat pemain aktif
    }. Hanya permainan yang dapat menampung semuanya yang ditampilkan.
host-game-switch-no-compatible-games =
    Tidak ada permainan lain yang dapat menampung seluruh { $seats } { $seats ->
        [one] tempat pemain aktif
       *[other] tempat pemain aktif
    }.
host-game-switch-confirm = Ganti permainan di meja ini dari { $old_game } ke { $new_game }? Semua peserta yang masih hadir akan pindah ke ruang tunggu baru dengan peran pemain atau penonton yang sama. Bot tetap ikut. Kondisi pertandingan atau ruang tunggu saat ini, pengaturan, tim, dan status siap akan dihapus. Kepemilikan meja, privasi, pencekalan, dan koneksi obrolan suara tetap dipertahankan. Undangan permainan lama yang belum ditanggapi akan dibatalkan.
host-game-switch-target-unavailable = Permainan tersebut tidak lagi tersedia sebagai target peralihan. Tidak ada status meja yang diubah.
host-game-switch-roster-invalid = Daftar peserta yang hadir di meja ini tidak lagi cocok dengan daftar peserta permainan. Pergantian permainan dibatalkan agar tidak ada peserta yang tersisih. Kembali ke meja dan coba lagi setelah daftar diperbarui.
host-game-switch-too-many-seats =
    Tidak dapat beralih ke { $game }. Permainan ini mendukung maksimal { $max } { $max ->
        [one] tempat pemain aktif
       *[other] tempat pemain aktif
    }, sedangkan meja ini membutuhkan { $seats }.
host-game-switch-failed = Permainan tidak dapat dialihkan dengan aman. Meja dan permainan saat ini tidak diubah.
host-game-switch-you = Anda mengalihkan meja ini dari { $old_game } ke { $new_game }. Semua orang sekarang berada di ruang tunggu yang baru, obrolan suara meja tetap terhubung.
host-game-switch-player = { $player } mengalihkan meja ini dari { $old_game } ke { $new_game }. Semua orang sekarang berada di ruang tunggu yang baru, obrolan suara meja tetap terhubung.
host-restart-confirm = Mulai ulang permainan saat ini dan kembalikan meja ini ke ruang tunggu? Pemain saat ini dan obrolan suara akan tetap terhubung, namun pertandingan saat ini akan dibatalkan.
host-restart-broadcast = { $player } memulai kembali permainan. Meja dikembalikan ke ruang tunggu.
host-restart-you = Anda memulai kembali permainan. Meja dikembalikan ke ruang tunggu.
host-restart-not-playing = Tidak ada permainan aktif untuk dimulai ulang.
player-substitution-offer-action = Tawarkan tempat ini kepada penonton
player-substitution-seat-bot = Tempat bot: { $bot }
player-substitution-seat-replacement = { $bot }, bermain di tempat yang dicadangkan untuk { $player }
player-substitution-seat-self = Tempat duduk Anda: { $player }
player-substitution-seat-player = Tempat pemain: { $player }
player-substitution-no-seats = (Tidak ada tempat pemain aktif yang tersedia)
player-substitution-seat-unavailable = Tempat pemain itu tidak lagi tersedia untuk pergantian pemain. Tidak ada peran yang diubah.
player-substitution-no-spectators = (Tidak ada penonton yang memenuhi syarat tersedia)
player-substitution-spectator-unavailable = Penonton itu tidak lagi tersedia untuk pengganti. Tidak ada peran yang diubah.
player-substitution-user-busy = { $player } sedang mengisi kolom isian atau membuka tampilan status lain. Coba lagi setelah selesai.
player-substitution-game-busy = Permainan sedang menyelesaikan pilihan tersinkronisasi atau pemulihan meja yang mengunci sementara pergantian pemain. Coba lagi setelah selesai.
player-substitution-offer-sent = Tempat { $seat } ditawarkan kepada { $player }. Kendali baru berpindah setelah tawaran diterima.
player-substitution-self-offer-sent = Tempat Anda ditawarkan kepada { $player }. Jika diterima, Anda menjadi penonton dan tetap menjadi pemilik meja. Hasil akhir tempat tersebut akan dicatat untuk pemain pengganti.
player-substitution-self-incoming-consent-sent = Anda meminta { $player } menyerahkan tempatnya kepada Anda. Jika diterima, Anda langsung mengambil alih karena pilihan Anda tadi sudah dianggap sebagai persetujuan.
player-substitution-outgoing-consent-sent = Anda meminta { $player } menyerahkan tempatnya kepada { $substitute }. Jika disetujui, pemain pengganti juga harus menerima sebelum kendali berpindah.
player-substitution-offer-pending = { $player } sudah memiliki permintaan pergantian pemain yang menunggu tanggapan.
player-substitution-seat-offer-pending = Tempat { $seat } sudah memiliki permintaan pergantian pemain yang menunggu tanggapan.
player-substitution-self-seat-offer-pending = Tempat Anda sudah memiliki permintaan pergantian pemain yang menunggu tanggapan.
player-substitution-request-outgoing = { $host } ingin { $player } menggantikan Anda. Jika diterima, Anda menjadi penonton. Pemain pengganti mewarisi kondisi permainan, informasi pribadi dalam permainan, dan sisa waktu giliran Anda. Hasil akhir akan dicatat untuk pemain pengganti. Penghitung waktu tidak diatur ulang.
player-substitution-request-outgoing-host-incoming = { $host } ingin menggantikan Anda. Jika diterima, Anda menjadi penonton. Pemain pengganti mewarisi kondisi permainan, informasi pribadi dalam permainan, dan sisa waktu giliran Anda. Hasil akhir akan dicatat untuk pemain pengganti. Penghitung waktu tidak diatur ulang.
player-substitution-request-player = { $host } menawarkan tempat { $player } kepada Anda. Jika diterima, Anda mewarisi kondisi permainan, informasi pribadi dalam permainan, dan sisa waktu giliran di tempat tersebut. Hasil akhir akan dicatat untuk Anda. Penghitung waktu tidak diatur ulang dan pemain sebelumnya menjadi penonton.
player-substitution-request-host-seat = { $host } menawarkan tempatnya kepada Anda. Jika diterima, Anda mewarisi kondisi permainan, informasi pribadi dalam permainan, dan sisa waktu giliran di tempat tersebut. Hasil akhir akan dicatat untuk Anda. Penghitung waktu tidak diatur ulang. Pemain sebelumnya menjadi penonton dan tetap menjadi pemilik meja.
player-substitution-request-bot = { $host } menawarkan tempat yang saat ini dikendalikan { $bot } kepada Anda. Jika diterima, Anda mewarisi kondisi permainan, informasi pribadi dalam permainan, dan sisa waktu giliran di tempat tersebut. Hasil akhir akan dicatat untuk Anda. Penghitung waktu tidak diatur ulang.
player-substitution-request-replacement = { $host } menawarkan tempat yang dicadangkan untuk { $player } dan saat ini dikendalikan { $bot } kepada Anda. Jika diterima, Anda mewarisi kondisi permainan, informasi pribadi dalam permainan, dan sisa waktu giliran di tempat tersebut. Hasil akhir akan dicatat untuk Anda. Penghitung waktu tidak diatur ulang dan pemain sebelumnya tidak dapat mengambil kembali tempat ini.
player-substitution-decline = Tolak Pergantian
player-substitution-accept = Terima Pergantian
player-substitution-offer-expired = Permintaan pergantian pemain sudah habis masa berlakunya.
player-substitution-offer-expired-host = { $player } tidak merespons sebelum permintaan pergantian pemain berakhir. Tidak ada peran yang diubah.
player-substitution-offer-declined = { $player } menolak permintaan pergantian pemain. Tidak ada peran yang diubah.
player-substitution-no-longer-available = Permintaan pergantian pemain itu tidak lagi tersedia. Tidak ada peran yang diubah.
player-substitution-awaiting-incoming = { $player } sekarang dapat menerima atau menolak pergantian pemain. Belum ada peran yang berubah.
player-substitution-complete-player-you = Anda mengambil alih tempat { $player }. Pemain tersebut sekarang menjadi penonton.
player-substitution-complete-outgoing-you = { $player } mengambil alih tempat Anda sebelumnya. Anda sekarang adalah penonton.
player-substitution-complete-player = { $player } mengambil alih tempat { $outgoing }. Pemain sebelumnya kini menjadi penonton.
player-substitution-complete-host-player-you = Anda mengambil alih tempat { $player }. Pemain tersebut kini menjadi penonton dan tetap menjadi pemilik meja.
player-substitution-complete-outgoing-host-you = { $player } mengambil alih tempat Anda sebelumnya. Anda sekarang menjadi penonton dan tetap menjadi pemilik meja.
player-substitution-complete-host = { $player } mengambil alih tempat { $outgoing }. Pemain sebelumnya kini menjadi penonton dan tetap menjadi pemilik meja.
player-substitution-complete-bot-you = Anda mengambil kendali tempat { $bot }.
player-substitution-complete-bot = { $player } mengambil alih tempat { $bot }.
player-substitution-complete-replacement-you = Anda mengambil kendali tempat yang dicadangkan untuk { $replaced_player } dari { $bot }. Reservasi sebelumnya telah berakhir.
player-substitution-complete-replacement = { $player } mengambil alih tempat yang dicadangkan untuk { $replaced_player } dari { $bot }. Reservasi sebelumnya telah berakhir.
host-invite-no-friends = (Tidak ada teman yang bisa diundang)
host-invite-sent = Undangan dikirim ke { $player }.
host-invite-friend-unavailable = Teman itu tidak lagi dapat diundang.
host-invite-already-pending = Undangan untuk teman tersebut sudah menunggu keputusan.
host-invite-friend-busy = Teman itu sudah ada dalam permainan.
host-invite-pair-cooldown =
    Harap tunggu { $seconds ->
        [one] 1 detik
       *[other] { $seconds } detik
    } sebelum mengundang teman itu lagi.
host-invite-rate-limited =
    Anda mengirimkan undangan meja terlalu cepat. Coba lagi dalam { $seconds ->
        [one] 1 detik
       *[other] { $seconds } detik
    }.
host-invite-declined = { $player } menolak undangan meja Anda.
table-invite-received = { $host } mengundang Anda ke meja { $game } miliknya.
table-invite-queued = { $host } mengundang Anda ke meja { $game } miliknya. Selesaikan isian Anda saat ini untuk menanggapi undangan.
table-invite-expired = Undangan meja telah kedaluwarsa.
table-invite-no-longer-available = Undangan meja itu tidak lagi tersedia.
invite-accept = Terima Undangan
invite-decline = Tolak Undangan
host-management-no-longer-host = Anda bukan lagi pemilik meja ini.
host-pass-no-candidates = (Tidak ada pemain yang tersedia untuk dijadikan pemilik meja)
host-pass-no-longer-host = Anda telah mengalihkan kepemilikan meja ke pemain lain. Anda bukan lagi pemilik meja ini.
host-passed = { $player } sekarang menjadi pemilik meja.
host-passed-you = Anda sekarang adalah pemilik meja.
host-pass-failed = Kepemilikan meja gagal dialihkan. Pemain tersebut mungkin sudah pergi.
host-kick-no-candidates = Tidak ada pemain yang dapat dikeluarkan.
host-kick-invalid-target = Pemain yang akan dikeluarkan tidak valid.
host-kick-broadcast = { $player } telah dikeluarkan dari meja.
host-kick-ban-broadcast = { $player } dikeluarkan dan dicekal dari meja.
host-kick-confirm = Anda mengeluarkan { $player } dari meja.
host-kick-ban-confirm = Anda mengeluarkan dan mencekal { $player } dari meja.
host-kick-you = Anda dikeluarkan dari meja oleh { $host }.
host-kick-ban-you = Anda dikeluarkan dan dicekal dari meja oleh { $host }.
table-you-are-banned = Anda dicekal dari meja ini.
table-private-invite-only = Meja ini bersifat pribadi. Anda harus menerima undangan dari pemilik meja untuk bergabung.
table-join-social-blocked = Anda tidak dapat memasuki meja ini karena kontak sosial langsung tidak tersedia antara Anda dan pemilik meja. Anda masih dapat memperoleh kembali tempat yang telah dipesan untuk Anda.
voice-room-table-label = Obrolan suara meja { $game }
voice-unavailable = Obrolan Suara tidak tersedia saat ini.
voice-invalid-context = Permintaan ruang suara tersebut tidak valid.
voice-not-at-table = Anda belum bergabung dengan meja. Bergabunglah dengan meja sebelum memulai Obrolan Suara.
voice-not-in-context = Anda harus berada di meja sebelum bergabung dengan Obrolan Suara.
voice-rate-limited = Permintaan perubahan obrolan suara terlalu sering. Tunggu sebentar.
voice-muted-seconds = Anda dibisukan dan tidak dapat bergabung dengan Obrolan Suara. { $seconds } detik tersisa.
voice-muted-minutes = Anda dibisukan dan tidak dapat bergabung dengan Obrolan Suara. { $minutes } menit tersisa.
voice-muted-permanent = Anda dibisukan dan tidak dapat bergabung dengan Obrolan Suara.
voice-status-connected = { $player } terhubung ke Obrolan Suara.
voice-status-connected-you = Anda terhubung ke Obrolan Suara.
voice-status-disconnected = { $player } terputus dari Obrolan Suara.
voice-status-disconnected-you = Anda terputus dari Obrolan Suara.
voice-status-connection-lost = { $player } kehilangan koneksi dan dikeluarkan dari obrolan suara.
voice-status-connection-lost-you = Anda kehilangan koneksi dan dikeluarkan dari Obrolan Suara.
voice-status-left-table = { $player } meninggalkan meja dan meninggalkan Obrolan Suara.
voice-status-left-table-you = Anda meninggalkan meja dan meninggalkan Obrolan Suara.
voice-member-status-connected = terhubung ke Obrolan Suara
voice-member-status-not-connected = tidak terhubung ke Obrolan Suara
voice-member-status-host-muted = mikrofon dinonaktifkan oleh pemilik meja
voice-member-status-host-unmuted = diperbolehkan menggunakan mikrofon
voice-member-entry = { $player }: { $status }
voice-host-management-no-members = Tidak ada anggota meja lain yang dapat dimoderasi.
voice-host-target-summary = Status suara untuk { $player }: { $voice_status }, { $moderation_status }.
voice-host-mute-action = Nonaktifkan Mikrofon { $player }
voice-host-unmute-action = Izinkan { $player } Menggunakan Mikrofon
voice-host-cannot-mute-self = Anda tidak dapat membatasi mikrofon sendiri melalui kontrol pemilik meja.
voice-host-moderation-rate-limited = Anda terlalu sering mengubah pembatasan mikrofon. Coba lagi dalam { $seconds } detik.
voice-host-muted-actor = Anda menonaktifkan mikrofon { $player }. Pengguna tersebut masih dapat mendengarkan, tetapi tidak dapat berbicara melalui mikrofon.
voice-host-muted-target = { $host } menonaktifkan mikrofon Anda. Anda masih dapat mendengarkan, namun tidak dapat mengaktifkan mikrofon.
voice-host-muted-observer = { $host } menonaktifkan mikrofon { $player } untuk meja ini.
voice-host-unmuted-actor = Anda mengizinkan { $player } menggunakan mikrofon lagi. Mikrofon tetap nonaktif sampai dinyalakan sendiri oleh pengguna tersebut.
voice-host-unmuted-target = { $host } mengizinkan Anda menggunakan mikrofon lagi. Mikrofon tetap nonaktif sampai Anda menyalakannya sendiri.
voice-host-unmuted-observer = { $host } mengizinkan { $player } menggunakan mikrofon.
voice-host-unmuted-self = Anda kembali mengizinkan penggunaan mikrofon. Mikrofon tetap nonaktif sampai Anda menyalakannya.
voice-personal-settings-action = Pengaturan Suara Pribadi
voice-personal-settings-summary = Pengaturan suara pribadi untuk { $player }: volume { $volume } persen, { $mute_status }, { $connection_status }.
voice-personal-status-muted = disenyapkan untuk Anda
voice-personal-status-unmuted = tidak disenyapkan untuk Anda
voice-personal-mute-action = Senyapkan { $player } untuk saya
voice-personal-unmute-action = Dengarkan kembali { $player }
voice-personal-volume-action = Ubah Volume Pribadi, Saat Ini { $volume } Persen
voice-personal-volume-choice = { $volume } Persen
voice-personal-reset-action = Atur Ulang Pengaturan Suara Pribadi
voice-personal-muted = Anda menyenyapkan suara { $player } hanya untuk Anda. Pengguna lain tetap dapat mendengarnya.
voice-personal-unmuted = Anda kembali dapat mendengar suara { $player }.
voice-personal-volume-set = Anda mengatur volume suara pribadi { $player } ke { $volume } persen.
voice-personal-reset = Anda mengatur ulang pengaturan suara pribadi Anda untuk { $player }.
voice-member-left = Anggota meja itu sudah tidak ada lagi. Pengaturan suara meja yang dipertahankan tidak diubah.
voice-settings-limit-reached = Meja ini telah mencapai batas keamanan pengaturan suara. Tidak ada pengaturan yang diubah.
voice-settings-invalid = Pengaturan suara itu tidak valid. Tidak ada pengaturan yang diubah.
voice-invalid-participant = Peserta suara itu tidak valid.
voice-moderation-provider-failed = Moderasi suara tidak dapat diterapkan saat ini. Tidak ada pengaturan yang diubah, silakan coba lagi.
error-smtp-not-configured = Pemulihan kata sandi saat ini dinonaktifkan oleh administrator.
error-email-not-found = Tidak ada akun dengan alamat email tersebut.
success-reset-email-sent = Kode atur ulang telah dikirimkan ke alamat email Anda.
error-smtp-send-failed = Gagal mengirim email atur ulang. Silakan coba lagi nanti.
error-invalid-reset-code = Kode atur ulang tidak valid atau kedaluwarsa.
success-password-reset = Kata sandi Anda telah berhasil diatur ulang. Anda sekarang dapat masuk.
chat-global = { $player } di obrolan global: { $message }
