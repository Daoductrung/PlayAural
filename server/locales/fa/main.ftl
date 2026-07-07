auth-username-password-required = نام کاربری و رمز عبور الزامی هستند.
auth-registration-success = ثبت‌نام موفقیت‌آمیز! اکنون می‌توانید با مشخصات خود وارد شوید.
auth-username-taken = این نام کاربری قبلاً گرفته شده است. لطفاً نام کاربری دیگری انتخاب کنید.
auth-username-reserved-bot = این نام برای ربات‌های PlayAural رزرو شده است. لطفاً نام کاربری دیگری انتخاب کنید.
auth-registration-error = ثبت‌نام به دلیل خطای سرور ناموفق بود. لطفاً دوباره تلاش کنید.
auth-error-wrong-password = رمز عبور اشتباه است.
auth-error-user-not-found = کاربر وجود ندارد.
auth-kicked-logged-in-elsewhere = شما قطع شدید زیرا حساب کاربری شما از دستگاه دیگری وارد شده است.

chat-global = { $player } در کانال عمومی می‌گوید: { $message }
dev-announcement-broadcast = { $dev } یکی از توسعه‌دهندگان PlayAural است.
admin-announcement-broadcast = { $admin } یکی از مدیران PlayAural است.

admin-smtp-updated-success = تنظیمات SMTP با موفقیت به‌روز شد
admin-smtp-settings = تنظیمات SMTP
email-reset-subject = کد بازنشانی رمز عبور PlayAural
email-reset-body = سلام { $username }،\n\nشما درخواست بازنشانی رمز عبور حساب کاربری خود در PlayAural را داده‌اید.\nکد بازنشانی ۶ رقمی شما: { $code }\n\nاین کد تا ۱۵ دقیقه دیگر منقضی می‌شود.\nاگر این درخواست را شما ندادید، لطفاً این ایمیل را نادیده بگیرید.
email-reset-body-html = <p>سلام { $username }،</p>
    <p>درخواستی برای بازنشانی رمز عبور حساب کاربری شما در PlayAural دریافت کردیم.</p>
    <p>کد بازیابی ۶ رقمی شما:</p>
    <h2>{ $code }</h2>
    <p>این کد دقیقاً تا ۱۵ دقیقه دیگر معتبر است.</p>
    <p>اگر این درخواست را شما ندادید، لطفاً این ایمیل را نادیده بگیرید. حساب کاربری شما امن است.</p>
    <p>با احترام،<br>ترانگ</p>
email-test-subject = تست SMTP PlayAural
email-test-body = این یک ایمیل آزمایشی از سرور PlayAural است که تنظیمات SMTP شما را بررسی می‌کند.
email-test-body-html = <p>سلام،</p>
    <p>این یک ایمیل آزمایشی از سرور PlayAural است.</p>
    <p>اگر این پیام را می‌خوانید، تنظیمات SMTP شما با موفقیت ایمیل‌های HTML را ارسال می‌کند.</p>
smtp-test-sending = در حال بررسی اتصال، لطفاً صبر کنید...
smtp-test-success = ایمیل آزمایشی با موفقیت به { $email } ارسال شد!
smtp-test-failed = ارسال ایمیل آزمایشی ناموفق بود: { $error }
smtp-host = میزبان: { $value }
smtp-port = پورت: { $value }
smtp-username = نام کاربری: { $value }
smtp-password = رمز عبور: { $value }
smtp-from-email = ایمیل فرستنده: { $value }
smtp-from-name = نام فرستنده: { $value }
smtp-encryption = رمزنگاری: { $value }
smtp-test-connection = تست اتصال
smtp-not-set = تنظیم نشده
smtp-prompt-host = میزبان SMTP را وارد کنید (مثلاً smtp.gmail.com):
smtp-prompt-port = پورت SMTP را وارد کنید (مثلاً ۵۸۷ یا ۴۶۵):
smtp-prompt-username = نام کاربری SMTP را وارد کنید:
smtp-prompt-password = رمز عبور SMTP را وارد کنید:
smtp-prompt-from-email = آدرس ایمیل فرستنده را وارد کنید:
smtp-prompt-from-name = نام فرستنده را وارد کنید (مثلاً پشتیبانی PlayAural):
smtp-prompt-test-email = آدرس ایمیل مقصد را برای تست وارد کنید:
smtp-enc-none = بدون رمزنگاری
smtp-enc-ssl = استفاده از SSL
smtp-enc-tls = فعال‌سازی خودکار رمزنگاری TLS (STARTTLS)
smtp-current-enc = * { $value }

main-menu-title = منوی اصلی

play = بازی
view-active-tables = مشاهده‌ی میزهای فعال
options = تنظیمات
logout = خروج
back = بازگشت
go-back = بازگشت
context-menu = منوی زمینه.
no-actions-available = هیچ عملی در دسترس نیست.
table-new-host-promoted = { $player } اکنون میزبان میز است.
return-to-lobby = بازگشت به لابی
return-to-table = بازگشت به میز
create-table = ایجاد میز جدید
leave-table = ترک میز
start-game = شروع بازی
add-bot = افزودن ربات
remove-bot = حذف ربات
actions-menu = منوی عملیات
save-table = ذخیره‌ی میز
whose-turn = نوبت کیست
whos-at-table = چه کسانی پشت میز هستند
check-scores = مشاهده‌ی امتیازات
check-scores-detailed = امتیازات دقیق

game-player-skipped = { $player } نوبت او رد شد.

table-created = { $host } یک میز { $game } جدید ایجاد کرد.
table-created-broadcast = { $host } یک میز { $game } جدید ایجاد کرد.
table-joined = { $player } به میز پیوست.
table-left = { $player } میز را ترک کرد.
new-host = { $player } اکنون میزبان است.
waiting-for-players = در انتظار بازیکنان. حداقل { $min }، حداکثر { $max }.
game-starting = بازی شروع می‌شود!
table-listing = میز { $host } ({ $count } کاربر)
table-listing-one = میز { $host } ({ $count } کاربر)
table-listing-with = میز { $host } ({ $count } کاربر) با { $members }
table-listing-game = { $game }: میز { $host } ({ $count } کاربر)
table-listing-game-one = { $game }: میز { $host } ({ $count } کاربر)
table-listing-game-with = { $game }: میز { $host } ({ $count } کاربر) با { $members }
table-listing-game-status = { $game } [{ $status }]: میز { $host } ({ $count } کاربر)
table-listing-game-one-status = { $game } [{ $status }]: میز { $host } ({ $count } کاربر)
table-listing-game-with-status = { $game } [{ $status }]: میز { $host } ({ $count } کاربر) با { $members }
table-status-waiting = در انتظار
table-status-playing = در حال بازی
table-status-finished = تمام شده
table-not-exists = میز دیگر وجود ندارد.
table-full = میز پر است.
player-replaced-by-bot = { $bot } اکنون به جای { $player } بازی می‌کند.
player-reclaimed-from-bot = { $player } بازگشت و جای خود را از { $bot } پس گرفت.
player-took-over = { $player } جای خود را از { $bot } پس گرفت.
spectator-joined = به عنوان تماشاگر به میز { $host } پیوست.

spectate = تماشا
now-playing = { $player } اکنون در حال بازی است.
now-spectating = { $player } اکنون در حال تماشا است.
spectator-left = { $player } تماشا را متوقف کرد.

welcome = به PlayAural خوش آمدید!
goodbye = خداحافظ!

user-online = { $player } آنلاین شد.
user-offline = { $player } آفلاین شد.
friend-online = دوست شما { $player } اکنون آنلاین است.
friend-offline = دوست شما { $player } آفلاین شد.
permission-denied = شما مجوز انجام این عمل روی یک توسعه‌دهنده را ندارید.
kick-user = اخراج کاربر
kick-broadcast = { $target } توسط { $actor } اخراج شد.
you-were-kicked = شما توسط { $actor } اخراج شدید.
user-not-online = کاربر { $target } آنلاین نیست.
kick-immune = شما نمی‌توانید این کاربر را اخراج کنید.
kick-confirm = آیا مطمئن هستید که می‌خواهید { $player } را اخراج کنید؟
no-users-to-kick = هیچ کاربری برای اخراج در دسترس نیست.
usage-kick = طرز استفاده: /kick <نام‌کاربری>
online-users-none = هیچ کاربری آنلاین نیست.
online-users-one = ۱ کاربر: { $users }
online-users-many = { $count } کاربر: { $users }
online-user-not-in-game = منوی اصلی
online-user-waiting-approval = در انتظار تأیید
presence-status-main-menu = منوی اصلی
presence-status-waiting-table = در انتظار میز { $game }
presence-status-playing = در حال بازی { $game }
presence-status-spectating = در حال تماشای { $game }
presence-status-watching-table = در حال تماشای میز { $game }
presence-status-reviewing-results = در حال بررسی نتایج { $game }
presence-status-spectating-results = در حال تماشای نتایج { $game }
user-role-dev = توسعه‌دهنده
user-role-admin = مدیر
user-role-user = کاربر
client-type-web = وب
client-type-python = دسکتاپ
client-type-mobile = موبایل
client-type-with-platform = { $client } ({ $platform })
online-user-full-entry = { $username } ({ $role }، { $client }، { $language }): { $status }
online-user-actions-title = عملیات برای { $username }
user-not-online-anymore = این کاربر دیگر آنلاین نیست.
close-menu = بستن

language = زبان
language-option = زبان: { $language }
language-changed = زبان به { $language } تغییر یافت.
language-menu-entry =
    { $official ->
        [true] { $language }. زبان رسمی PlayAural. مترجمان: { $translators }.
       *[false] { $language }. ترجمه‌ی جامعه. مترجمان: { $translators }.
    }
language-menu-entry-missing-metadata = { $language }. ابرداده‌ی مترجم در دسترس نیست.
language-menu-current-entry = زبان فعلی: { $entry }

option-on = روشن
option-off = خاموش

# منوی فرعی انتخاب چندگزینه‌ای
option-back = بازگشت
option-select-all = انتخاب همه
option-deselect-all = لغو انتخاب همه
option-selected-count = { $count } انتخاب شده
option-deselected-count = { $count } انتخاب نشده
option-min-selected = حداقل باید { $count } گزینه را انتخاب کنید.
option-max-selected = حداکثر می‌توانید { $count } گزینه را انتخاب کنید.

turn-sound-option = صدای نوبت: { $status }

custom-bot-names-option = نام‌های سفارشی ربات: { $status }
confirm-destructive-option = تأیید اقدامات پرریسک: { $status }
clear-kept-option = پاک کردن تاس‌های نگهداشته‌شده هنگام پرتاب: { $status }
option-notify-table-created = اعلان هنگام ایجاد میز: { $status }
option-notify-user-presence = اعلان آنلاین/آفلاین شدن کاربران: { $status }
option-notify-friend-presence = اعلان آنلاین/آفلاین شدن دوستان: { $status }
dice-keeping-style-option = شیوه‌ی نگهداری تاس: { $style }
dice-keeping-style-changed = شیوه‌ی نگهداری تاس به { $style } تغییر یافت.
dice-keeping-style-indexes = شماره‌ی تاس‌ها
dice-keeping-style-values = مقدار تاس‌ها

# تنظیمات شخصی: دسته‌بندی عمومی و بازی
general-options = تنظیمات عمومی
game-options = تنظیمات بازی

# تنظیمات بازی (ترجیحات اعلامی با قابلیت بازنویسی برای هر بازی)
pref-category-display = نمایش
pref-set-brief-announcements = اعلان‌های مختصر: { $status }
pref-changed-brief-announcements = اعلان‌های مختصر { $status }.
pref-desc-brief-announcements = کوتاه‌سازی اعلان‌های حرکت و رویداد درون‌بازی؛ برای شنیدن توضیحات کامل‌تر، خاموش کنید.
pref-category-sounds = صداها
pref-category-gameplay = گیم‌پلی
pref-category-dice = تاس
pref-default = پیش‌فرض
pref-per-game-for = { $game }: { $value }
pref-reset-all = بازنشانی همه‌ی تنظیمات بازی
pref-reset-category = بازنشانی تنظیمات { $category }
pref-reset-done = تنظیمات بازی بازنشانی شد.
pref-set-play-turn-sound = صدای نوبت: { $status }
pref-set-confirm-destructive-actions = تأیید اقدامات پرریسک: { $status }
pref-set-allow-custom-bot-names = نام‌های سفارشی ربات: { $status }
pref-set-clear-kept-on-roll = پاک کردن تاس‌های نگهداشته‌شده هنگام پرتاب: { $status }
pref-set-dice-keeping-style = شیوه‌ی نگهداری تاس: { $choice }
pref-changed-play-turn-sound = صدای نوبت { $status }.
pref-changed-confirm-destructive-actions = تأیید اقدامات پرریسک { $status }.
pref-changed-allow-custom-bot-names = نام‌های سفارشی ربات { $status }.
pref-changed-clear-kept-on-roll = پاک کردن تاس‌های نگهداشته‌شده هنگام پرتاب { $status }.
pref-changed-dice-keeping-style = شیوه‌ی نگهداری تاس به { $choice } تغییر یافت.
pref-desc-play-turn-sound = وقتی نوبت شما می‌شود، یک صدا پخش کن.
pref-desc-confirm-destructive-actions = قبل از اقدامات پرریسک یا غیرقابل‌بازگشت، مانند پاس دادن در Pusoy Dos، تأیید بگیر.
pref-desc-allow-custom-bot-names = به شما اجازه می‌دهد برای ربات‌هایی که به میز اضافه می‌کنید، نام سفارشی بگذارید.
pref-desc-clear-kept-on-roll = در بازی‌های تاس‌پشتیبانی‌شده مانند یاتزی، بعد از هر پرتاب، همه‌ی تاس‌های نگهداشته‌شده را آزاد کن. پرتاب بعدی همه‌ی تاس‌ها را دوباره می‌اندازد مگر اینکه دوباره تعدادی را نگه دارید؛ با شیوه‌ی مقدار تاس‌ها، از Shift+1-6 برای نگهداشتن تاس‌های هم‌مقدار استفاده کنید.
pref-desc-dice-keeping-style = شماره‌ی تاس‌ها: از ۱-۵ یا در Midnight از ۱-۶ برای انتخاب تاس بر اساس موقعیت استفاده کنید. مقدار تاس‌ها: از ۱-۶ برای آزاد کردن یک تاس نگهداشته‌شده با آن مقدار و Shift+1-6 برای نگهداشتن یک تاس آزاد هم‌مقدار استفاده کنید. در مرحله‌ی مبادله‌ی Tradeoff، ۱-۶ یک تاس هم‌مقدار را نگه می‌دارد و Shift+1-6 یک تاس را برای مبادله علامت‌گذاری می‌کند؛ در مرحله‌ی برداشتن، ۱-۶ ساده یک تاس هم‌مقدار را از استخر برمی‌دارد.

cancel = انصراف
no-bot-names-available = هیچ نام رباتی در دسترس نیست.
enter-bot-name = نام ربات را وارد کنید
bot-name-invalid-length = نام ربات باید بین ۳ تا ۳۰ کاراکتر باشد.
bot-name-invalid-characters = نام ربات فقط می‌تواند شامل حروف، اعداد و فاصله باشد.
bot-name-already-used = یک بازیکن یا ربات با این نام قبلاً در این میز حضور دارد.
bot-name-registered-account = این نام متعلق به یک حساب ثبت‌شده است. لطفاً نام ربات دیگری انتخاب کنید.
table-name-already-used = یک بازیکن یا ربات با این نام قبلاً در این میز حضور دارد.
no-options-available = هیچ گزینه‌ای در دسترس نیست.
no-scores-available = هیچ امتیازی در دسترس نیست.

option-desc-generic = { $label }. پیش‌فرض: { $default }.
option-desc-integer = { $label }. یک عدد صحیح از { $min } تا { $max } وارد کنید. پیش‌فرض: { $default }.
option-desc-number = { $label }. یک عدد از { $min } تا { $max } وارد کنید. پیش‌فرض: { $default }.
option-desc-menu = { $label }. یکی از این گزینه‌ها را انتخاب کنید: { $choices }. پیش‌فرض: { $default }.
option-desc-bool = { $label }. برای روشن یا خاموش کردن، این گزینه را فعال کنید. پیش‌فرض: { $default }.
option-desc-multiselect = { $label }. انتخاب‌شده‌ی فعلی: { $selected }. حداقل انتخاب: { $min }. حداکثر انتخاب: { $max }. انتخاب پیش‌فرض: { $default }.
option-desc-no-choices = در حال حاضر هیچ گزینه‌ای در دسترس نیست
option-desc-none-selected = هیچ‌کدام
option-desc-no-maximum = بدون محدودیت

general-desc-profile = مشاهده و ویرایش جزئیات پروفایل عمومی شما.
general-desc-friends = مدیریت دوستان، درخواست‌های دوستی، پیام‌های خصوصی و اقدامات میز دوستان.
general-desc-my-stats = مشاهده‌ی بردها، باخت‌ها، امتیازات و آمار بازی‌های پشتیبانی‌شده.
general-desc-general-options = تنظیمات سراسری حساب شامل زبان، صدا، دسترسی‌پذیری و اعلان‌ها.
general-desc-game-options = تنظیم ترجیحات گیم‌پلی که می‌تواند به‌صورت سراسری یا برای بازی‌های خاص اعمال شود.
general-desc-language = انتخاب زبانی که برای منوها، پیام‌ها و مستندات سرور در صورت وجود استفاده می‌شود.
general-desc-audio = تنظیم موسیقی، افکت‌های صوتی، صدای محیط، بلندی مکالمه‌ی صوتی، صداهای تایپ و تنظیمات دستگاه ورودی دسکتاپ.
general-desc-accessibility = تنظیمات مربوط به دسترسی‌پذیری شامل خواندن، ورودی و رفتار کلاینت در این دستگاه.
general-desc-notifications = انتخاب اعلان‌های گفتگو، حضور و ایجاد میز که می‌خواهید بشنوید.
general-desc-music-volume = تغییر بلندی موسیقی زمینه. قرار دادن روی خاموش، موسیقی را بی‌صدا می‌کند.
general-desc-sound-volume = تغییر بلندی افکت‌های صوتی بازی. افکت‌ها حداقل ده درصد باقی می‌مانند تا نشانه‌های مهم شنیده شوند.
general-desc-ambience-volume = تغییر بلندی صدای محیط. قرار دادن روی خاموش، صدای محیط را بی‌صدا می‌کند.
general-desc-voice-volume = تغییر بلندی پخش مکالمه‌ی صوتی میز.
general-desc-audio-input-device = انتخاب میکروفون یا دستگاه ورودی که کلاینت دسکتاپ برای مکالمه‌ی صوتی استفاده می‌کند.
general-desc-play-typing-sounds = پخش صداهای کوتاه تایپ هنگام ورود متن در فیلدهای ویرایش کلاینت.
general-desc-web-speech-settings = تنظیم خروجی گفتار مرورگر، شامل حالت ARIA live یا Web Speech، سرعت گفتار و صدا.
general-desc-mobile-speech-settings = تنظیم موتور تبدیل متن به گفتار موبایل، صدا و سرعت گفتار.
general-desc-invert-multiline-enter = جابجایی رفتار دکمه‌ی Enter برای ارسال و خط جدید در فیلدهای چندخطی کلاینت دسکتاپ.
general-desc-mute-global-chat = جلوگیری از پخش خودکار پیام‌های گفتگوی عمومی.
general-desc-mute-table-chat = جلوگیری از پخش خودکار پیام‌های گفتگوی میز.
general-desc-notify-user-presence = اعلام آنلاین یا آفلاین شدن کاربران.
general-desc-notify-friend-presence = اعلام آنلاین یا آفلاین شدن دوستان شما.
general-desc-notify-table-created = اعلام ایجاد یک میز عمومی جدید.
general-desc-speech-mode = انتخاب اینکه کلاینت وب اعلان‌ها را از طریق ARIA live به صفحه‌خوان بفرستد یا با Web Speech API مرورگر بخواند.
general-desc-speech-rate = تغییر سرعت گفتار کلاینت وب.
general-desc-speech-voice = انتخاب صدای مورد استفاده توسط Web Speech API کلاینت وب، یا بازگشت به پیش‌فرض مرورگر.
general-desc-mobile-tts-engine = انتخاب موتور تبدیل متن به گفتار موبایل. اندروید فعلاً از موتور مدیریت‌شده توسط سیستم استفاده می‌کند.
general-desc-mobile-tts-voice = انتخاب صدای تبدیل متن به گفتار موبایل، یا بازگشت به پیش‌فرض سیستم.
general-desc-mobile-tts-rate = تغییر سرعت تبدیل متن به گفتار موبایل.

saved-tables = میزهای ذخیره‌شده
no-saved-tables = هیچ میز ذخیره‌شده‌ای ندارید.
no-active-tables = هیچ میز فعالی وجود ندارد.
no-active-tables-all = هیچ میز فعالی در دسترس نیست.
no-active-tables-waiting = هیچ میز در انتظاری در دسترس نیست.
no-active-tables-playing = هیچ میز در حال بازی در دسترس نیست.
active-tables-filter = فیلتر: { $filter }
filter-name-all = همه
filter-name-waiting = در انتظار
filter-name-playing = در حال بازی
game-category-filter = دسته‌بندی: { $category }
game-category-filter-option = { $category } ({ $count })
game-category-all = همه
game-category-cards = بازی‌های ورق
game-category-poker = بازی‌های پوکر
game-category-dice = بازی‌های تاس
game-category-board = بازی‌های تخته‌ای
game-category-arcade = بازی‌های آرکید
game-category-misc = متفرقه
no-games-in-category = هیچ بازی‌ای در این دسته‌بندی در دسترس نیست.
restore-table = بازیابی
delete-saved-table = حذف
saved-table-deleted = میز ذخیره‌شده حذف شد.
missing-players = قابل بازیابی نیست: این بازیکنان در دسترس نیستند: { $players }
table-restored = میز بازیابی شد! همه‌ی بازیکنان منتقل شدند.
table-saved-destroying = میز ذخیره شد! بازگشت به منوی اصلی.
game-type-not-found = نوع بازی دیگر وجود ندارد.

action-not-your-turn = نوبت شما نیست.
action-not-playing = بازی شروع نشده است.
action-spectator = تماشاگران نمی‌توانند این کار را انجام دهند.
action-not-host = فقط میزبان می‌تواند این کار را انجام دهد.
action-not-available = این عمل در حال حاضر در دسترس نیست.
action-game-in-progress = در حین اجرای بازی نمی‌توان این کار را انجام داد.
action-need-more-players = برای شروع به بازیکنان بیشتری نیاز است.
action-table-full = میز پر است.
action-start-needs-more-players = قابل شروع نیست. بازیکنان فعال: { $current }. حداقل نیاز: { $minimum }.
action-start-has-too-many-players = قابل شروع نیست. بازیکنان فعال: { $current }. حداکثر مجاز: { $maximum }.
action-start-requires-exact-players = قابل شروع نیست. بازیکنان فعال: { $current }. نیاز: دقیقاً { $required }.
action-no-bots = هیچ رباتی برای حذف وجود ندارد.
action-bots-cannot = ربات‌ها نمی‌توانند این کار را انجام دهند.
action-no-scores = هنوز هیچ امتیازی در دسترس نیست.

options-category-audio = صدا
options-category-accessibility = دسترسی‌پذیری
options-category-notifications = اعلان‌ها
options-category-game = بازی

music-volume-option = بلندی موسیقی: { $value }%
sound-volume-option = بلندی افکت‌های صوتی: { $value }%
ambience-volume-option = بلندی صدای محیط: { $value }%
voice-volume-option = بلندی مکالمه‌ی صوتی: { $value }%
volume-choice-off = خاموش
volume-choice-percent = { $value }%
volume-choice-current = { $label } (فعلی)
audio-input-device-option = دستگاه ورودی صدا: { $device }
audio-input-device-default = دستگاه ورودی پیش‌فرض سیستم

mute-global-chat-option = بی‌صدا کردن گفتگوی عمومی: { $status }
mute-table-chat-option = بی‌صدا کردن گفتگوی میز: { $status }
invert-multiline-enter-option = معکوس کردن رفتار دکمه‌ی Enter: { $status }
play-typing-sounds-option = پخش صدای تایپ: { $status }
enter-music-volume = بلندی موسیقی را وارد کنید (۰-۱۰۰)
enter-ambience-volume = بلندی صدای محیط را وارد کنید (۰-۱۰۰)
enter-voice-volume = بلندی مکالمه‌ی صوتی را وارد کنید (۱۰-۱۰۰)
invalid-volume = بلندی نامعتبر است.

dice-not-rolled = هنوز تاس نینداخته‌اید.
dice-no-dice = هیچ تاسی در دسترس نیست.
table-no-players = هیچ بازیکنی وجود ندارد.
table-players-one = { $count } بازیکن: { $players }.
table-players-many = { $count } بازیکن: { $players }.
table-spectators = تماشاگران: { $spectators }.
table-host-suffix = (میزبان)
table-voice-chat-suffix = (در مکالمه‌ی صوتی)
table-members-summary = خلاصه‌ی میز: { $total } { $total ->
    [one] صندلی
   *[other] صندلی
}; { $real } { $real ->
    [one] نفر واقعی
   *[other] نفر واقعی
}، { $bots } { $bots ->
    [one] ربات
   *[other] ربات
}; { $active } فعال، { $spectators } در حال تماشا.
table-members-empty = در حال حاضر هیچ عضوی در میز لیست نشده است. برای بازگشت و به‌روزرسانی نمای میز، از دکمه‌ی بازگشت استفاده کنید.
table-member-entry = { $player }: { $status }
table-member-status-host = میزبان
table-member-status-player = بازیکن
table-member-status-spectator = تماشاگر
table-member-status-bot = ربات
table-member-status-online = آنلاین
table-member-status-offline = آفلاین
table-member-status-voice-chat = در مکالمه‌ی صوتی
table-member-status-bot-takeover = ربات به جای او بازی می‌کند: { $bot }
table-member-no-actions = هیچ عملی برای { $player } در دسترس نیست.
table-member-left = آن شخص دیگر در این میز نیست.
table-member-bot-left = آن ربات دیگر در این میز نیست.
game-over = بازی تمام شد
game-final-scores = امتیازات نهایی
game-points = { $count } { $count ->
    [one] امتیاز
   *[other] امتیاز
}

leaderboards = رتبه‌بندی
leaderboard-no-data = هنوز داده‌ای برای این بازی در رتبه‌بندی وجود ندارد.

leaderboard-type-wins = رتبه‌بندی برد
leaderboard-type-rating = رتبه‌بندی امتیاز مهارت
leaderboard-type-total-score = رتبه‌بندی امتیاز کل
leaderboard-type-high-score = رتبه‌بندی بیشترین امتیاز
leaderboard-type-games-played = رتبه‌بندی بازی‌های انجام‌شده
leaderboard-type-avg-points-per-turn = رتبه‌بندی میانگین امتیاز در هر نوبت
leaderboard-type-best-single-turn = رتبه‌بندی بهترین نوبت تکی
leaderboard-type-score-per-round = رتبه‌بندی امتیاز در هر دور
leaderboard-type-most-enemies-defeated = رتبه‌بندی بیشترین دشمن شکست‌خورده
leaderboard-type-deepest-wave-reached = رتبه‌بندی عمیق‌ترین موج رسیده

leaderboard-wins-entry = { $rank }: { $player }، { $wins } { $wins ->
    [one] برد
   *[other] برد
} { $losses } { $losses ->
    [one] باخت
   *[other] باخت
}، { $percentage }% درصد برد
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-games-entry = { $rank }. { $player }: { $value } بازی
leaderboard-avg-entry = { $rank }. { $player }: { $value }

leaderboard-no-player-stats = شما هنوز این بازی را انجام نداده‌اید.

leaderboard-no-ratings = هنوز داده‌ی امتیازی برای این بازی وجود ندارد.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } امتیاز ({ $mu } ± { $sigma })
leaderboard-no-player-rating = شما هنوز برای این بازی امتیازی ندارید.

my-stats = آمار من
my-stats-select-game = برای مشاهده‌ی آمار خود، یک بازی را انتخاب کنید
my-stats-no-data = شما هنوز این بازی را انجام نداده‌اید.
my-stats-no-games = شما هنوز هیچ بازی‌ای انجام نداده‌اید.
my-stats-header = { $game } - آمار شما
my-stats-wins = بردها: { $value }
my-stats-losses = باخت‌ها: { $value }
my-stats-winrate = درصد برد: { $value }%
my-stats-games-played = بازی‌های انجام‌شده: { $value }
my-stats-total-score = امتیاز کل: { $value }
my-stats-high-score = بیشترین امتیاز: { $value }
my-stats-rating = امتیاز مهارت: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = هنوز امتیاز مهارتی ندارید
my-stats-avg-per-turn = میانگین امتیاز در هر نوبت: { $value }
my-stats-best-turn = بهترین نوبت تکی: { $value }
my-stats-score-per-round = امتیاز در هر دور: { $value }
my-stats-most-enemies-defeated = بیشترین دشمن شکست‌خورده: { $value }
my-stats-deepest-wave-reached = عمیق‌ترین موج رسیده: { $value }

predict-outcomes = پیش‌بینی نتایج
predict-header = نتایج پیش‌بینی‌شده (بر اساس امتیاز مهارت)
predict-note-multiplayer = درصد برد فقط برای مسابقات ۲ نفره نشان داده می‌شود. با ۳ بازیکن واقعی یا بیشتر، فقط امتیازات مهارت نشان داده می‌شوند.
predict-entry = { $rank }. { $player } (امتیاز: { $rating })
predict-entry-2p = { $rank }. { $player } (امتیاز: { $rating }، { $probability }% شانس برد)
predict-unavailable = پیش‌بینی امتیازی در دسترس نیست.
predict-need-players = برای پیش‌بینی به حداقل ۲ بازیکن واقعی نیاز است.
action-need-more-humans = به بازیکنان واقعی بیشتری نیاز است.
confirm-leave-game = آیا مطمئن هستید که می‌خواهید میز را ترک کنید؟
confirm-yes = بله
confirm-no = خیر

administration = مدیریت

account-approval = تأیید حساب
no-pending-accounts = هیچ حسابی در انتظار تأیید نیست.
approve-account = تأیید
decline-account = رد
account-approved = حساب { $player } تأیید شد.
account-declined = حساب { $player } رد و حذف شد.

waiting-for-approval = حساب کاربری شما در انتظار تأیید توسط مدیر است. لطفاً صبر کنید...
account-approved-welcome = حساب شما تأیید شد! به PlayAural خوش آمدید!
account-declined-goodbye = درخواست حساب شما رد شد.

account-request = درخواست حساب
account-action = اقدام روی حساب انجام شد

promote-admin = ارتقا به مدیر
demote-admin = تنزل از مدیریت
ban-user = مسدود کردن کاربر
unban-user = لغو مسدودیت کاربر
no-users-to-promote = هیچ کاربری برای ارتقا در دسترس نیست.
no-admins-to-demote = هیچ مدیری برای تنزل در دسترس نیست.
admin-search-users = جستجو بر اساس نام کاربری
admin-search-users-current = جستجو بر اساس نام کاربری. جستجوی فعلی: { $query }.
admin-search-prompt = برای جستجو، تمام یا بخشی از نام کاربری را وارد کنید. برای مرور همه‌ی نتایج به صورت صفحه‌بندی‌شده، خالی بگذارید.
menu-page-summary = نمایش { $start }-{ $end } از { $total } ورودی. صفحه‌ی { $page } از { $pages }.
menu-page-summary-query = جستجوی "{ $query }": نمایش { $start }-{ $end } از { $total } ورودی. صفحه‌ی { $page } از { $pages }.
menu-page-refresh = به‌روزرسانی لیست
menu-list-refreshed = لیست به‌روزرسانی شد.
menu-page-first = صفحه‌ی اول
menu-page-previous = صفحه‌ی قبل
menu-page-next = صفحه‌ی بعد
menu-page-last = صفحه‌ی آخر
admin-search-no-results = هیچ کاربری یافت نشد. برای جستجوی عبارت دیگر از گزینه‌ی جستجو بر اساس نام کاربری استفاده کنید.
confirm-promote = آیا مطمئن هستید که می‌خواهید { $player } را به مدیر ارتقا دهید؟
confirm-demote = آیا مطمئن هستید که می‌خواهید { $player } را از مدیریت تنزل دهید؟
broadcast-to-all = اعلام به همه‌ی کاربران
broadcast-to-admins = فقط به مدیران اعلام کن
broadcast-to-nobody = بی‌صدا (بدون اعلام)
promote-announcement = { $player } به مدیر ارتقا یافت!
promote-announcement-you = شما به مدیر ارتقا یافتید!
demote-announcement = { $player } از مدیریت تنزل یافت.
demote-announcement-you = شما از مدیریت تنزل یافتید.
not-admin-anymore = شما دیگر مدیر نیستید و نمی‌توانید این اقدام را انجام دهید.
dev-only-action = این اقدام فقط برای توسعه‌دهندگان مجاز است.

ban-duration-1h = ۱ ساعت
ban-duration-6h = ۶ ساعت
ban-duration-12h = ۱۲ ساعت
ban-duration-1d = ۱ روز
ban-duration-3d = ۳ روز
ban-duration-1w = ۱ هفته
ban-duration-1m = ۱ ماه
ban-duration-permanent = دائمی

reason-spam = هرزنامه
reason-harassment = آزار و اذیت
reason-cheating = تقلب
reason-inappropriate = رفتار نامناسب
reason-custom = سایر / سفارشی

no-users-to-ban = هیچ کاربری برای مسدود کردن در دسترس نیست.
no-banned-users = در حال حاضر هیچ کاربری مسدود نشده است.
admin-active-ban-entry = { $username }. انقضای مسدودیت: { $expires }. دلیل: { $reason }. صادرکننده: { $admin }.
admin-active-mute-entry = { $username }. انقضای بی‌صدا کردن: { $expires }. دلیل: { $reason }. صادرکننده: { $admin }.
admin-penalty-expiry-permanent = دائمی
admin-penalty-expiry-unknown = تاریخ انقضای نامشخص
admin-penalty-expiry-expired = قبلاً منقضی شده
admin-penalty-expiry-timed = { $date } ({ $remaining } باقی‌مانده)
admin-penalty-reason-unknown = دلیل نامشخص
admin-penalty-admin-unknown = مدیر نامشخص
admin-penalty-remaining-days = { $count ->
    [one] ۱ روز
   *[other] { $count } روز
}
admin-penalty-remaining-hours = { $count ->
    [one] ۱ ساعت
   *[other] { $count } ساعت
}
admin-penalty-remaining-minutes = { $count ->
    [one] ۱ دقیقه
   *[other] { $count } دقیقه
}
admin-penalty-remaining-less-minute = کمتر از ۱ دقیقه

ban-broadcast = { $target } توسط { $actor } به دلیل { $reason } مسدود شد. مدت: { $duration }.
unban-broadcast = مسدودیت { $target } توسط { $actor } لغو شد.

banned-menu-title = حساب مسدود شده
banned-reason = دلیل: { $reason }
banned-expires = انقضا: { $expires }
banned-permanent = انقضا: دائمی
disconnect = قطع اتصال

enter-custom-ban-reason = دلیل سفارشی مسدودیت را وارد کنید:

mute-user = بی‌صدا کردن کاربر
unmute-user = لغو بی‌صدا کردن کاربر
no-users-to-mute = هیچ کاربری برای بی‌صدا کردن در دسترس نیست.
no-muted-users = در حال حاضر هیچ کاربری بی‌صدا نشده است.
mute-duration-5m = ۵ دقیقه
mute-duration-15m = ۱۵ دقیقه
mute-duration-30m = ۳۰ دقیقه
mute-duration-1h = ۱ ساعت
mute-duration-6h = ۶ ساعت
mute-duration-1d = ۱ روز
mute-duration-permanent = دائمی
enter-custom-mute-reason = دلیل سفارشی بی‌صدا کردن را وارد کنید:
mute-broadcast = { $target } توسط { $actor } به دلیل { $reason } بی‌صدا شد. مدت: { $duration }.
unmute-broadcast = بی‌صدایی { $target } توسط { $actor } لغو شد.
you-have-been-muted = شما بی‌صدا شده‌اید. دلیل: { $reason }. مدت: { $duration }.
you-have-been-unmuted = بی‌صدایی شما لغو شد. می‌توانید دوباره گفتگو کنید.
muted-remaining-seconds = شما بی‌صدا هستید. { $seconds } ثانیه باقی‌مانده.
muted-remaining-minutes = شما بی‌صدا هستید. { $minutes } دقیقه باقی‌مانده.
muted-permanent = شما به‌طور دائمی بی‌صدا شده‌اید. برای اطلاعات بیشتر با مدیر تماس بگیرید.
auto-muted-seconds = به دلیل ارسال هرزنامه به‌طور موقت بی‌صدا شده‌اید. { $seconds } ثانیه باقی‌مانده.
auto-muted-minutes = به دلیل ارسال هرزنامه به‌طور موقت بی‌صدا شده‌اید. { $minutes } دقیقه باقی‌مانده.
auto-muted-applied-seconds = به دلیل ارسال بیش از حد هرزنامه در گفتگو، به مدت { $seconds } ثانیه به‌طور خودکار بی‌صدا شدید.
auto-muted-applied-minutes = به دلیل ارسال بیش از حد هرزنامه در گفتگو، به مدت { $minutes } دقیقه به‌طور خودکار بی‌صدا شدید.
chat-rate-limited = آرام‌تر! پیام‌ها را خیلی سریع ارسال می‌کنید.
chat-global-disabled-send = گفتگوی عمومی در تنظیمات شما غیرفعال است. قبل از ارسال پیام عمومی، گفتگوی عمومی را روشن کنید.
chat-table-disabled-send = گفتگوی میز در تنظیمات شما غیرفعال است. قبل از ارسال پیام میز، گفتگوی میز را روشن کنید.
admin-spam-alert = هشدار: { $username } در حال ارسال بیش از حد هرزنامه در گفتگو است و به‌طور خودکار بی‌صدا شد.

broadcast-announcement = اعلامیه‌ی همگانی
admin-broadcast-prompt = پیام خود را برای پخش به همه‌ی کاربران آنلاین وارد کنید. (این پیام برای همه ارسال خواهد شد!)
admin-broadcast-sent = اعلامیه برای { $count } کاربر ارسال شد.

manage-motd = مدیریت پیام روز
create-update-motd = ایجاد/به‌روزرسانی پیام روز
view-motd = مشاهده‌ی پیام روز فعال
delete-motd = حذف پیام روز
motd-version-prompt = شماره‌ی نسخه‌ی جدید پیام روز را وارد کنید (باید > ۰ باشد):
invalid-motd-version = نسخه‌ی پیام روز نامعتبر است. باید یک عدد مثبت باشد.
motd-prompt = پیام روز را برای { $language } وارد کنید (برای خط جدید از Enter استفاده کنید، در صورت معکوس بودن چندخطی از Shift+Enter برای ارسال استفاده کنید):
motd-created = پیام روز نسخه‌ی { $version } با موفقیت ایجاد شد.
motd-cancelled = ایجاد پیام روز لغو شد.
motd-deleted = پیام روز حذف شد.
motd-delete-empty = هیچ پیام روز فعالی برای حذف وجود ندارد.
motd-not-exists = هیچ پیام روز فعالی وجود ندارد.
motd-announcement = پیام روز
motd-broadcast = پیام روز جدید: { $message }
error-no-languages = خطا: هیچ زبانی یافت نشد.
ok = تأیید

unknown-player = بازیکن ناشناس

logout-confirm-title = آیا مطمئن هستید که می‌خواهید خارج شوید و بازی را ترک کنید؟
logout-confirm-yes = بله، خارج شو
logout-confirm-no = نه، بمان

system-name = سیستم
server-restarting = سرور در { $seconds } ثانیه دیگر راه‌اندازی مجدد می‌شود...
server-restarting-now = سرور در حال راه‌اندازی مجدد است. لطفاً به‌زودی دوباره وصل شوید.
server-shutting-down = سرور در { $seconds } ثانیه دیگر خاموش می‌شود...
server-shutting-down-now = سرور در حال خاموش شدن است. خداحافظ!
server-power-management = مدیریت برق سرور
server-power-reboot = راه‌اندازی مجدد سرور
server-power-shutdown = خاموش کردن سرور
server-power-cancel = لغو اقدام برق برنامه‌ریزی‌شده
server-power-active-status = { $action } برنامه‌ریزی شده. دلیل: { $reason }.
server-power-action-reboot = راه‌اندازی مجدد
server-power-action-shutdown = خاموش‌سازی
server-power-delay-30s = در ۳۰ ثانیه
server-power-delay-1m = در ۱ دقیقه
server-power-delay-5m = در ۵ دقیقه
server-power-delay-10m = در ۱۰ دقیقه
server-power-delay-30m = در ۳۰ دقیقه
server-power-delay-1h = در ۱ ساعت
server-power-delay-2h = در ۲ ساعت
server-power-delay-custom = تأخیر سفارشی به دقیقه
server-power-custom-delay-prompt = تأخیر را به دقیقه وارد کنید، از ۱ تا { $max }:
server-power-invalid-custom-delay = تأخیر نامعتبر است. یک عدد صحیح از ۱ تا { $max } دقیقه وارد کنید.
server-power-reason-update = به‌روزرسانی
server-power-reason-maintenance = نگهداری
server-power-reason-security = امنیت
server-power-reason-technical = مشکل فنی
server-power-reason-custom = دلیل سفارشی
server-power-reason-unspecified = دلیل نامشخص
server-power-custom-reason-prompt = دلیل اقدام برق سرور را برای { $language } وارد کنید:
server-power-confirm-summary = تأیید { $action } سرور در { $duration }. دلیل: { $reason }.
server-power-scheduled = { $action } سرور در { $duration } برنامه‌ریزی شد.
server-power-already-scheduled = یک اقدام برق سرور قبلاً برنامه‌ریزی شده است. قبل از برنامه‌ریزی مجدد، آن را لغو کنید.
server-power-cancel-none = در حال حاضر هیچ اقدام برق سروری برنامه‌ریزی نشده است.
server-power-cancelled = اقدام برق برنامه‌ریزی‌شده‌ی سرور لغو شد.
server-power-cancelled-broadcast = { $admin } اقدام برق برنامه‌ریزی‌شده‌ی { $action } سرور را لغو کرد.
server-power-command-removed = دستورات /reboot و /stop از گفتگو حذف شدند. به جای آن از مدیریت، مدیریت برق سرور استفاده کنید.
server-power-finalizing-input-blocked = سرور در حال نهایی‌سازی راه‌اندازی مجدد یا خاموش‌سازی است. لطفاً منتظر بمانید تا کلاینت قطع شود.
server-power-finalize-failed = { $action } برنامه‌ریزی‌شده‌ی سرور نتوانست با ایمنی کامل شود. سرور آنلاین باقی می‌ماند؛ لطفاً با مدیر تماس بگیرید.
server-power-reboot-warning = راه‌اندازی مجدد سرور در { $duration }. دلیل: { $reason }. به‌صورت دستی قطع نکنید؛ کلاینت شما به‌طور خودکار دوباره وصل می‌شود و میزهای فعال حفظ می‌شوند.
server-power-shutdown-warning = خاموش‌سازی سرور در { $duration }. دلیل: { $reason }. سرور در حال آفلاین شدن است؛ قبل از خاموش‌سازی، هر بازی که می‌خواهید نگه دارید را ذخیره کنید.
server-power-reboot-now = سرور در حال راه‌اندازی مجدد است. دلیل: { $reason }. به‌صورت دستی قطع نکنید؛ کلاینت شما به‌طور خودکار دوباره وصل می‌شود و میزهای فعال حفظ می‌شوند.
server-power-shutdown-now = سرور در حال خاموش شدن است. دلیل: { $reason }. سرور در حال آفلاین شدن است.
server-power-restore-waiting = این میز پس از یک راه‌اندازی مجدد برنامه‌ریزی‌شده بازیابی شد. تا { $seconds } ثانیه برای اتصال مجدد سایر بازیکنان صبر می‌شود قبل از اینکه جای خالی با ربات‌ها پر شود.
server-power-restore-input-blocked = این میز هنوز در حال بازیابی از راه‌اندازی مجدد برنامه‌ریزی‌شده است. گیم‌پلی به مدت { $seconds } ثانیه دیگر در حال انتظار برای { $players } متوقف شده است؛ لطفاً پس از پایان دوره‌ی مهلت دوباره تلاش کنید.
server-power-restore-missing-players-fallback = سایر بازیکنان
server-power-restore-complete = همه‌ی بازیکنان فعال پس از راه‌اندازی مجدد برنامه‌ریزی‌شده دوباره متصل شدند. بازی از سر گرفته شد.
server-power-restore-complete-with-bots = مهلت اتصال مجدد پس از راه‌اندازی مجدد برنامه‌ریزی‌شده به پایان رسید. صندلی‌های خالی با ربات‌ها پر شدند و بازی از سر گرفته می‌شود.
duration-seconds = { $count ->
    [one] ۱ ثانیه
   *[other] { $count } ثانیه
}
duration-minutes = { $count ->
    [one] ۱ دقیقه
   *[other] { $count } دقیقه
}
duration-hours = { $count ->
    [one] ۱ ساعت
   *[other] { $count } ساعت
}
duration-minutes-seconds = { $minutes } دقیقه و { $seconds } ثانیه
duration-hours-minutes = { $hours } ساعت و { $minutes } دقیقه
server-error-changing-language = خطا در تغییر زبان: { $error }
default-save-name = { $game } - { $date }

speech-settings = تنظیمات گفتار
speech-mode-option = حالت گفتار: { $status }
speech-rate-option = سرعت گفتار: { $value }%
speech-voice-option = صدا: { $voice }
select-voice = انتخاب صدا
enter-speech-rate = سرعت گفتار را وارد کنید (۵۰-۳۰۰)
invalid-rate = سرعت گفتار نامعتبر است. مقداری بین ۵۰ و ۳۰۰ استفاده کنید.
mode-aria = Aria-live
mode-web-speech = Web Speech API
default-voice = صدای پیش‌فرض
mobile-speech-settings = تنظیمات گفتار موبایل
mobile-tts-engine-option = موتور TTS: { $engine }
mobile-tts-engine-system = پیش‌فرض سیستم
mobile-tts-engine-system-selected = موتور TTS پیش‌فرض سیستم
mobile-tts-engine-api-note = انتخاب موتور اندروید در این نسخه توسط تنظیمات سیستم مدیریت می‌شود.
mobile-tts-voice-option = صدای موبایل: { $voice }
mobile-tts-rate-option = سرعت گفتار موبایل: { $value }%
mobile-tts-enter-rate = سرعت گفتار موبایل را وارد کنید (۵۰-۲۰۰)
mobile-tts-invalid-rate = سرعت گفتار موبایل نامعتبر است. مقداری بین ۵۰ و ۲۰۰ استفاده کنید.

player-kicked-offline = بازیکن { $player } اخراج شد (آفلاین).
game-paused-host-disconnect = بازی متوقف شد. در انتظار اتصال مجدد { $player }...
game-resumed = { $player } دوباره متصل شد. بازی از سر گرفته شد!

auth-error-username-length = نام کاربری باید بین ۳ تا ۳۰ کاراکتر باشد.
auth-error-username-invalid-chars = نام کاربری فقط می‌تواند شامل حروف، اعداد و فاصله باشد (بدون فاصله‌ی پشت‌سرهم و بدون کاراکترهای خاص).
auth-error-password-weak = رمز عبور باید حداقل ۸ کاراکتر باشد و شامل حروف و اعداد باشد.

personal-and-options = شخصی و تنظیمات
profile = پروفایل
friends = دوستان
profile-registration-date = تاریخ ثبت‌نام: { $date }
profile-username = نام کاربری: { $username }
profile-email = ایمیل: { $email }
admin-view-email = نمای مدیر - ایمیل: { $email }
profile-gender = جنسیت: { $gender }
profile-bio = بیوگرافی: { $bio }
profile-bio-empty = تنظیم نشده
profile-email-empty = تنظیم نشده

gender-male = مرد
gender-female = زن
gender-non-binary = غیردودویی
gender-not-set = تنظیم نشده

action-set-edit = تنظیم / ویرایش
action-delete = حذف
bio-already-empty = بیوگرافی در حال حاضر خالی است.
bio-deleted = بیوگرافی حذف شد.
bio-updated = بیوگرافی به‌روز شد.

enter-email = آدرس ایمیل جدید را وارد کنید:
email-updated = آدرس ایمیل به‌روز شد.
enter-bio = بیوگرافی خود را وارد کنید:

gender-updated = جنسیت به‌روز شد.
no-changes-made = هیچ تغییری اعمال نشد.
confirm-email-change = آیا مطمئن هستید که می‌خواهید ایمیل خود را به { $email } تغییر دهید؟

mandatory-email-notice = برای ادامه‌ی مشارکت باید ایمیل خود را تنظیم کنید. ایمیل شما خصوصی است و فقط برای شما قابل مشاهده است.
error-email-empty = ایمیل الزامی است و نمی‌تواند خالی باشد.
error-email-invalid = فرمت ایمیل نامعتبر است. لطفاً یک آدرس ایمیل معتبر وارد کنید.
reg-error-email = ایمیل برای ثبت‌نام الزامی است.

error-email-taken = این ایمیل قبلاً توسط حساب دیگری استفاده می‌شود.

error-bio-length = بیوگرافی نباید بیشتر از ۲۵۰ کاراکتر باشد.
error-captcha-failed = تأییدیه ناموفق بود. لطفاً دوباره تلاش کنید.
error-rate-limit-login = تعداد تلاش‌های ناموفق برای ورود زیاد است. لطفاً ۱۵ دقیقه دیگر دوباره تلاش کنید.
error-rate-limit-register = امروز به حداکثر تعداد ثبت‌نام حساب رسیده‌اید.
auth-error-rate-limit = { error-rate-limit-login }

friends-my-friends = دوستان من
friends-pending-requests = درخواست‌های در انتظار ({ $count })
friends-no-pending-requests = درخواست‌های در انتظار
friends-send-request = ارسال درخواست دوستی
friends-list-empty = شما هنوز دوستی ندارید.
friend-status-offline = آفلاین
friend-status-playing = در حال بازی { $game }
friend-status-spectating = در حال تماشای { $game }
friend-status-lobby = منوی اصلی
friend-list-entry = { $username } ({ $status })

friend-actions-title = عملیات برای { $username }
view-profile = مشاهده‌ی پروفایل
join-table = پیوستن به میز
remove-friend = حذف دوست
friend-remove-confirm = آیا { $username } را از لیست دوستان خود حذف می‌کنید؟
friend-remove-not-friends = { $username } دیگر در لیست دوستان شما نیست.
already-in-table = شما قبلاً در این میز هستید.
friend-removed-success = { $username } از لیست دوستان شما حذف شد.
friend-removed-notify = { $username } شما را از لیست دوستان خود حذف کرد.

no-pending-requests = هیچ درخواستی در انتظار نیست.
friend-request-from = درخواست دوستی از { $username }
accept = پذیرش
decline = رد
friend-accepted-success = شما اکنون با { $username } دوست هستید.
friend-accepted-notify = { $username } درخواست دوستی شما را پذیرفت!
request-not-found = درخواست دوستی دیگر وجود ندارد.
friend-declined-success = درخواست دوستی رد شد.
friend-declined-notify = { $username } درخواست دوستی شما را رد کرد.

public-profile-title = پروفایل { $username }
enter-friend-username = نام کاربری شخصی که می‌خواهید با او دوست شوید را وارد کنید:
friend-error-self = نمی‌توانید برای خودتان درخواست دوستی بفرستید.
friend-error-already-friends = شما قبلاً با این کاربر دوست هستید.
friend-error-duplicate = شما قبلاً یک درخواست دوستی در انتظار برای این کاربر دارید.
friend-request-sent = درخواست دوستی برای { $username } ارسال شد.
friend-request-received = شما یک درخواست دوستی جدید از { $username } دریافت کردید.

friends-grouped-requests = شما درخواست‌های دوستی در انتظار از: { $usernames } دارید.
friends-grouped-accepted = درخواست‌های دوستی شما توسط: { $usernames } پذیرفته شد.
friends-grouped-declined = درخواست‌های دوستی شما توسط: { $usernames } رد شد.
friends-grouped-removed = شما توسط: { $usernames } از لیست دوستان حذف شدید.
friends-and-others = { $names } و { $count } { $count ->
    [one] نفر دیگر
   *[other] نفر دیگر
}

send-private-message = ارسال پیام خصوصی
enter-pm-message = پیام خود را برای { $username } وارد کنید:
pm-error-not-friends = شما فقط می‌توانید برای دوستان خود پیام خصوصی بفرستید.
pm-error-offline = { $username } در حال حاضر آنلاین نیست.
pm-sent-success = پیام به { $username } ارسال شد.
pm-sent-content = شما به { $username }: { $message }
pm-received = پیام خصوصی از { $username }: { $message }

host-management = مدیریت میزبان
table-spectator-suffix = (تماشاگر)
host-management-set-private = خصوصی کردن میز
host-management-set-public = عمومی کردن میز
host-management-invite = دعوت از یک دوست
host-management-pass-host = انتقال میزبانی به بازیکن دیگر
host-management-kick = اخراج یک بازیکن
host-management-kick-ban = اخراج و مسدود کردن یک بازیکن
host-management-restart-game = راه‌اندازی مجدد بازی
host-management-table-now-private = این میز اکنون خصوصی است. فقط بازیکنان دعوت‌شده می‌توانند بپیوندند.
host-management-table-now-public = این میز اکنون عمومی است.
host-restart-confirm = آیا بازی فعلی را راه‌اندازی مجدد کرده و این میز را به اتاق انتظار بازمی‌گردانید؟ بازیکنان فعلی و مکالمه‌ی صوتی متصل می‌مانند، اما مسابقه‌ی فعلی لغو می‌شود.
host-restart-broadcast = { $player } بازی را راه‌اندازی مجدد کرد. میز به اتاق انتظار بازگشت.
host-restart-not-playing = هیچ بازی فعالی برای راه‌اندازی مجدد وجود ندارد.
host-invite-no-friends = (هیچ دوستی برای دعوت در دسترس نیست)
host-invite-sent = دعوتنامه برای { $player } ارسال شد.
host-invite-friend-unavailable = آن دوست در حال حاضر آنلاین نیست.
host-invite-already-pending = یک دعوتنامه قبلاً برای آن دوست در انتظار است.
host-invite-friend-busy = آن دوست قبلاً در یک بازی است.
host-invite-declined = { $player } دعوتنامه‌ی میز شما را رد کرد.
table-invite-received = { $host } شما را به میز { $game } خود دعوت کرده است.
table-invite-queued = { $host } شما را به میز { $game } خود دعوت کرد. برای پاسخ، ورودی فعلی خود را تمام کنید.
table-invite-expired = دعوتنامه‌ی میز منقضی شد.
invite-accept = پذیرش دعوتنامه
invite-decline = رد دعوتنامه
host-management-no-longer-host = شما دیگر میزبان این میز نیستید.
host-pass-no-candidates = (هیچ بازیکنی برای انتقال میزبانی در دسترس نیست)
host-pass-no-longer-host = شما میزبانی را به بازیکن دیگری منتقل کردید. دیگر میزبان این میز نیستید.
host-passed = { $player } اکنون میزبان است.
host-pass-failed = انتقال میزبانی ناموفق بود. ممکن است بازیکن میز را ترک کرده باشد.
host-kick-no-candidates = (هیچ بازیکنی برای اخراج در دسترس نیست)
host-kick-invalid-target = هدف اخراج نامعتبر است.
host-kick-broadcast = { $player } از میز اخراج شد.
host-kick-ban-broadcast = { $player } از میز اخراج و مسدود شد.
host-kick-you = شما توسط { $host } از میز اخراج شدید.
host-kick-ban-you = شما توسط { $host } از میز اخراج و مسدود شدید.
table-you-are-banned = شما از این میز مسدود هستید.
table-private-invite-only = این میز خصوصی است. برای پیوستن باید از میزبان دعوتنامه دریافت کنید.

voice-room-table-label = مکالمه‌ی صوتی میز { $game }
voice-unavailable = مکالمه‌ی صوتی در حال حاضر در دسترس نیست.
voice-invalid-context = درخواست اتاق صوتی نامعتبر است.
voice-not-at-table = شما هنوز به میزی نپیوسته‌اید. قبل از شروع مکالمه‌ی صوتی، به یک میز بپیوندید.
voice-not-in-context = قبل از پیوستن به مکالمه‌ی صوتی آن، باید در آن میز حضور داشته باشید.
voice-rate-limited = آرام‌تر. مکالمه‌ی صوتی در حال حاضر خیلی سریع در حال تغییر است.
voice-muted-seconds = شما بی‌صدا هستید و نمی‌توانید به مکالمه‌ی صوتی بپیوندید. { $seconds } ثانیه باقی‌مانده.
voice-muted-minutes = شما بی‌صدا هستید و نمی‌توانید به مکالمه‌ی صوتی بپیوندید. { $minutes } دقیقه باقی‌مانده.
voice-muted-permanent = شما بی‌صدا هستید و نمی‌توانید به مکالمه‌ی صوتی بپیوندید.
voice-status-connected = { $player } به مکالمه‌ی صوتی میز متصل شد.
voice-status-disconnected = { $player } از مکالمه‌ی صوتی قطع شد.
voice-status-connection-lost = اتصال { $player } قطع شد و از مکالمه‌ی صوتی حذف شد.
voice-status-left-table = { $player } میز را ترک کرد و مکالمه‌ی صوتی را ترک کرد.

error-smtp-not-configured = بازیابی رمز عبور در حال حاضر توسط مدیر غیرفعال شده است.
error-email-not-found = هیچ حسابی با این آدرس ایمیل یافت نشد.
success-reset-email-sent = یک کد بازنشانی به آدرس ایمیل شما ارسال شد.
error-smtp-send-failed = ارسال ایمیل بازنشانی ناموفق بود. لطفاً بعداً دوباره تلاش کنید.
error-invalid-reset-code = کد بازنشانی نامعتبر یا منقضی شده است.
success-password-reset = رمز عبور شما با موفقیت بازنشانی شد. اکنون می‌توانید وارد شوید.