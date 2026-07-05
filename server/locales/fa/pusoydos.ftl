game-name-pusoydos = پوسوی دوس

# =============================================================================
# =============================================================================


# =============================================================================
# برچسب‌ها و راهنماهای گزینه‌ها
# =============================================================================

pusoydos-set-game-mode = حالت بازی: { $choice }
pusoydos-select-game-mode = حالت بازی را انتخاب کنید:
pusoydos-option-changed-game-mode = حالت بازی روی { $choice } تنظیم شد.
pusoydos-desc-game-mode = حذفی: برنده شدن دورها برای خارج شدن، آخرین بازیکن بازنده است. باخت‌ها: بازیکنان آخر جمع‌کننده‌ی خطا هستند، اولی به حد نصاب برسد می‌بازد. امتیازی: برنده‌ی دور امتیازات جریمه را از بازندگان جمع‌آوری می‌کند، اولی به هدف برسد برنده است. حذفی امتیازی: بازندگان امتیازات جریمه‌ی خود را جمع می‌کنند، به حد نصاب برسید حذف می‌شوید، آخرین بازمانده برنده است.

pusoydos-mode-elimination = حذفی
pusoydos-mode-losses = باخت‌ها
pusoydos-mode-points = امتیازی
pusoydos-mode-points-elimination = حذفی امتیازی

pusoydos-set-rounds-to-win = دورهای مورد نیاز برای بردن: { $count }
pusoydos-enter-rounds-to-win = تعداد دورهای مورد نیاز برای حذف شدن را وارد کنید (حداقل: ۱، حداکثر: ۱۰):
pusoydos-option-changed-rounds-to-win = دورهای مورد نیاز برای بردن روی { $count } تنظیم شد.
pusoydos-desc-rounds-to-win = فقط حالت حذفی: چند دور یک بازیکن باید برنده شود تا از بازی به عنوان برنده خارج شود (پیش‌فرض ۲، محدوده ۱-۱۰).

pusoydos-set-losses-to-lose = باخت‌های مورد نیاز برای باخت: { $count }
pusoydos-enter-losses-to-lose = تعداد باخت‌های مورد نیاز برای باخت را وارد کنید (حداقل: ۱، حداکثر: ۱۰):
pusoydos-option-changed-losses-to-lose = باخت‌های مورد نیاز برای باخت روی { $count } تنظیم شد.
pusoydos-desc-losses-to-lose = فقط حالت باخت‌ها: چند بار آخر شدن یک بازیکن می‌تواند قبل از باخت بازی تحمل کند (پیش‌فرض ۳، محدوده ۱-۱۰).

pusoydos-set-target-score = امتیاز هدف: { $score }
pusoydos-enter-target-score = امتیاز هدف را وارد کنید (حداقل: ۱۰، حداکثر: ۱۰۰۰۰):
pusoydos-option-changed-target-score = امتیاز هدف روی { $score } تنظیم شد.
pusoydos-desc-target-score = فقط حالت‌های امتیازی: آستانه‌ی امتیاز برای بردن در حالت امتیازی، یا حذف در حالت حذفی امتیازی (پیش‌فرض ۱۰۰، محدوده ۱۰-۱۰۰۰۰).

pusoydos-set-turn-timer = زمان‌سنج نوبت: { $choice }
pusoydos-select-turn-timer = مدت زمان‌سنج نوبت را انتخاب کنید:
pusoydos-option-changed-turn-timer = زمان‌سنج نوبت روی { $choice } تنظیم شد.
pusoydos-desc-turn-timer = محدودیت زمانی هر نوبت: بدون محدودیت، ۱۰، ۱۵، ۲۰، ۳۰، ۴۵، ۶۰، یا ۹۰ ثانیه (پیش‌فرض بدون محدودیت).

pusoydos-timer-10 = ۱۰ ثانیه
pusoydos-timer-15 = ۱۵ ثانیه
pusoydos-timer-20 = ۲۰ ثانیه
pusoydos-timer-30 = ۳۰ ثانیه
pusoydos-timer-45 = ۴۵ ثانیه
pusoydos-timer-60 = ۶۰ ثانیه
pusoydos-timer-90 = ۹۰ ثانیه
pusoydos-timer-unlimited = بدون محدودیت

pusoydos-set-allow-2-in-straights = اجازه‌ی ۲ در دنباله‌ها: { $enabled }
pusoydos-option-changed-allow-2-in-straights = اجازه‌ی ۲ در دنباله‌ها روی { $enabled } تنظیم شد.
pusoydos-desc-allow-2-in-straights = آیا ۲ می‌تواند در دنباله‌ها استفاده شود (مثلاً A-2-3-4-5).

pusoydos-set-instant-wins = بردهای فوری: { $enabled }
pusoydos-option-changed-instant-wins = بردهای فوری روی { $enabled } تنظیم شد.
pusoydos-desc-instant-wins = آیا دست‌های ویژه‌ی داده‌شده (اژدها، چهار ۲، شش جفت) دور را فوری می‌برند. این نمی‌تواند با پاس دادن کارت ترکیب شود.

pusoydos-set-card-passing = پاس دادن کارت: { $choice }
pusoydos-select-card-passing = حالت پاس دادن کارت را انتخاب کنید:
pusoydos-option-changed-card-passing = پاس دادن کارت روی { $choice } تنظیم شد.
pusoydos-desc-card-passing = تبادل کارت بین برندگان و بازندگان پس از پخش: خاموش، ساده، یا کامل. پاس کامل دقیقاً به ۲ یا ۴ بازیکن نیاز دارد، و پاس دادن نمی‌تواند با بردهای فوری ترکیب شود.

pusoydos-passing-off = خاموش
pusoydos-passing-simple = ساده (اول و آخر ۱ کارت مبادله می‌کنند)
pusoydos-passing-full = کامل (اول/آخر ۲ کارت، دوم/سوم ۱ کارت مبادله می‌کنند)

pusoydos-set-penalty-tier = سطح جریمه: { $choice }
pusoydos-select-penalty-tier = سطح جریمه را انتخاب کنید:
pusoydos-option-changed-penalty-tier = سطح جریمه روی { $choice } تنظیم شد.
pusoydos-desc-penalty-tier = فقط حالت‌های امتیازی: میزان جریمه‌ی کارت‌های باقی‌مانده در پایان دور.

pusoydos-penalty-standard = استاندارد (۱۰+ کارت: x۲، ۱۳ کارت: x۳)
pusoydos-penalty-aggressive = تهاجمی (۸-۹: x۲، ۱۰-۱۲: x۳، ۱۳: x۴)
pusoydos-penalty-flat = مسطح (۱ امتیاز برای هر کارت، بدون ضریب)

pusoydos-set-penalty-per-two = جریمه به ازای هر ۲ نگهداشته‌شده: { $enabled }
pusoydos-option-changed-penalty-per-two = جریمه به ازای هر ۲ نگهداشته‌شده روی { $enabled } تنظیم شد.
pusoydos-desc-penalty-per-two = فقط حالت‌های امتیازی: هر ۲ باقی‌مانده در دست بازنده، جریمه‌ی آن دست را دو برابر می‌کند.

# =============================================================================
# اعلان‌های جریان بازی
# =============================================================================


pusoydos-new-hand = دور { $round }.
pusoydos-dealt = { $count } کارت داده شد: { $cards }.

pusoydos-you-first-player = شما ۳ خشت را دارید و اول می‌روید.
pusoydos-first-player = { $player } ۳ خشت را دارد و اول می‌رود.
pusoydos-you-first-player-lowest = شما پایین‌ترین کارت را دارید و اول می‌روید.
pusoydos-first-player-lowest = { $player } پایین‌ترین کارت را دارد و اول می‌رود.

# حالت حذفی
pusoydos-you-eliminated = شما { $count } دور برنده شدید و خارج شدید! بازی خوبی بود.
pusoydos-player-eliminated = { $player } { $count } دور برنده شد و خارج شد! بازی خوبی بود.
pusoydos-you-last-player = شما آخرین بازیکن باقی‌مانده هستید. بازی تمام شد!
pusoydos-last-player = { $player } آخرین بازیکن باقی‌مانده است. بازی تمام شد!
pusoydos-players-remaining = { $count } { $count ->
    [one] بازیکن
   *[other] بازیکن
} باقی‌مانده.

# حالت باخت‌ها
pusoydos-you-round-loser = شما آخر شدید و یک باخت می‌گیرید! ({ $count } { $count ->
    [one] باخت
   *[other] باخت
} مجموع.)
pusoydos-round-loser = { $player } آخر شد و یک باخت می‌گیرد! ({ $count } { $count ->
    [one] باخت
   *[other] باخت
} مجموع.)
pusoydos-you-losses-game-over = شما به { $count } باخت رسیدید و بازی را باختید!
pusoydos-losses-game-over = { $player } به { $count } باخت رسید و بازی را باخت!

# حالت امتیازی
pusoydos-penalty-entry = { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
} از { $player }
pusoydos-you-penalty-summary = شما دور را برنده شدید: { $breakdown }. ({ $gained } در این دور، { $total } مجموع.)
pusoydos-penalty-summary = { $player } دور را برنده شد: { $breakdown }. ({ $gained } در این دور، { $total } مجموع.)
pusoydos-you-win-round = شما دور را برنده شدید!
pusoydos-round-winner = { $player } دور را برنده شد!
pusoydos-you-go-out = شما خارج شدید!
pusoydos-player-goes-out = { $player } خارج شد!
pusoydos-you-points-winner = شما به { $score } امتیاز رسیدید و بازی را برنده شدید!
pusoydos-points-winner = { $player } به { $score } امتیاز رسید و بازی را برنده شد!

# حالت حذفی امتیازی
pusoydos-you-points-elim-penalty = شما { $points } امتیاز می‌گیرید. ({ $total } مجموع.)
pusoydos-points-elim-penalty = { $player } { $points } امتیاز می‌گیرد. ({ $total } مجموع.)
pusoydos-you-points-elim-eliminated = شما به { $score } امتیاز رسیدید و حذف شدید!
pusoydos-points-elim-eliminated = { $player } به { $score } امتیاز رسید و حذف شد!
pusoydos-you-points-elim-winner = شما آخرین بازیکن باقی‌مانده هستید. شما برنده شدید!
pusoydos-points-elim-winner = { $player } آخرین بازیکن باقی‌مانده است. { $player } برنده شد!

# بردهای فوری
pusoydos-you-instant-win-dragon = شما اژدها دارید (دنباله‌ی ۱۳ کارتی)! برد فوری!
pusoydos-instant-win-dragon = { $player } اژدها دارد (دنباله‌ی ۱۳ کارتی)! برد فوری!
pusoydos-you-instant-win-four-twos = شما هر چهار ۲ را دارید! برد فوری!
pusoydos-instant-win-four-twos = { $player } هر چهار ۲ را دارد! برد فوری!
pusoydos-you-instant-win-six-pairs = شما شش جفت دارید! برد فوری!
pusoydos-instant-win-six-pairs = { $player } شش جفت دارد! برد فوری!
pusoydos-checking-instant-wins = بررسی دست‌های برد فوری...
pusoydos-no-instant-wins = هیچ برد فوری در این دور وجود ندارد.

# پاس دادن کارت
pusoydos-passing-phase = مرحله‌ی پاس دادن کارت.
pusoydos-loser-gives = { $loser } { $count ->
    [one] بالاترین کارت خود
   *[other] { $count } کارت بالای خود
} را به { $winner } می‌دهد.
pusoydos-winner-gives-back = { $winner } { $count ->
    [one] یک کارت
   *[other] { $count } کارت
} را به { $loser } بازمی‌گرداند.
pusoydos-select-cards-to-give = { $count ->
    [one] ۱ کارت
   *[other] { $count } کارت
} را برای بازگرداندن به { $recipient } انتخاب کنید:
pusoydos-cards-exchanged = کارت‌ها مبادله شدند.
pusoydos-passed-cards = شما { $cards } را به { $recipient } دادید.
pusoydos-received-cards = شما { $cards } را از { $sender } دریافت کردید.

# =============================================================================
# تعامل با کارت و اقدامات
# =============================================================================

pusoydos-card-unselected = { $card }
pusoydos-card-selected = { $card } (انتخاب شد)

pusoydos-play-none = کارت‌هایی برای بازی انتخاب کنید.
pusoydos-play-invalid = ترکیب نامعتبر.
pusoydos-play-combo = بازی { $combo }

pusoydos-pass = گذشتن
pusoydos-check-trick = بررسی دسته
pusoydos-read-hand = مشاهده‌ی دست
pusoydos-check-turn-timer = بررسی زمان‌سنج نوبت
pusoydos-read-card-counts = تعداد کارت‌ها
pusoydos-card-count-line = { $player }: { $count } { $count ->
    [one] کارت
   *[other] کارت
}
pusoydos-card-counts-empty = هیچ بازیکن فعالی کارت برای شمارش ندارد.
pusoydos-timer-disabled = زمان‌سنج نوبت غیرفعال است.
pusoydos-timer-remaining = { $seconds } ثانیه باقی‌مانده.

# برچسب‌های کلیدهای میانبر
pusoydos-key-play = بازی کارت‌های انتخاب‌شده
pusoydos-key-pass = گذشتن
pusoydos-key-trick = بررسی دسته‌ی فعلی
pusoydos-key-hand = مشاهده‌ی دست خود
pusoydos-key-counts = تعداد کارت‌ها
pusoydos-key-timer = زمان‌سنج نوبت

# =============================================================================
# خطاها
# =============================================================================

pusoydos-error-full-passing-players = پاس کامل کارت دقیقاً به ۲ یا ۴ بازیکن نیاز دارد.
pusoydos-error-instant-wins-card-passing = بردهای فوری و پاس دادن کارت با هم تداخل دارند. قبل از شروع بازی یکی از آنها را غیرفعال کنید.
pusoydos-error-no-cards = شما هیچ کارتی انتخاب نکرده‌اید.
pusoydos-error-invalid-combo = کارت‌های انتخاب‌شده ترکیب معتبری تشکیل نمی‌دهند.
pusoydos-error-first-turn-3c = باید ۳ خشت را در اولین بازی شامل کنید.
pusoydos-error-wrong-length = باید دقیقاً { $count } { $count ->
    [one] کارت
   *[other] کارت
} بازی کنید تا دسته‌ی فعلی را ببرید.
pusoydos-error-lower-combo = ترکیب شما از دسته‌ی فعلی پایین‌تر است.
pusoydos-error-must-play = هنگام شروع یک دسته‌ی جدید نمی‌توانید بگذرید.
pusoydos-error-select-cards-to-give = دقیقاً { $count } { $count ->
    [one] کارت
   *[other] کارت
} را برای بازگرداندن به { $recipient } انتخاب کنید.
pusoydos-error-select-required-give-cards = تعداد کارت‌های مورد نیاز را قبل از تأیید مبادله انتخاب کنید.
pusoydos-error-eliminated = شما قبلاً از این بازی خارج شده‌اید.
pusoydos-confirm-pass = برای تأیید، دوباره از اقدام گذشتن استفاده کنید.

# =============================================================================
# پخش‌ها
# =============================================================================

pusoydos-you-play-single = شما { $card } را بازی می‌کنید.
pusoydos-player-plays-single = { $player } { $card } را بازی می‌کند.
pusoydos-you-play-combo = شما یک { $combo } از { $cards } بازی می‌کنید.
pusoydos-player-plays-combo = { $player } یک { $combo } از { $cards } بازی می‌کند.
pusoydos-you-pass = شما می‌گذرید.
pusoydos-player-passes = { $player } می‌گذرد.
pusoydos-you-win-trick = شما دسته را می‌برید.
pusoydos-trick-won = { $player } دسته را می‌برد.

pusoydos-trick-empty = دسته خالی است.
pusoydos-trick-status = { $player } یک { $combo } از { $cards } بازی کرد.
pusoydos-your-hand = دست شما: { $cards }.

pusoydos-score-no-scores = هنوز امتیازی وجود ندارد.
pusoydos-score-wins = { $player }: { $count } { $count ->
    [one] برد
   *[other] برد
}
pusoydos-score-losses = { $player }: { $count } { $count ->
    [one] باخت
   *[other] باخت
}
pusoydos-score-points = { $player }: { $score } امتیاز

pusoydos-you-one-card = شما یک کارت باقی‌مانده دارید!
pusoydos-one-card = { $player } یک کارت باقی‌مانده دارد!

# =============================================================================
# نام ترکیب‌ها
# =============================================================================

pusoydos-combo-single = تکی
pusoydos-combo-pair = جفت
pusoydos-combo-three_of_a_kind = سه‌تایی
pusoydos-combo-straight = دنباله
pusoydos-combo-flush = پنج‌برگ
pusoydos-combo-full_house = فول‌هاوس
pusoydos-combo-four_of_a_kind = چهارتایی
pusoydos-combo-straight_flush = دنباله‌ی پنج‌برگ

# نام دست‌های برد فوری
pusoydos-combo-dragon = اژدها
pusoydos-combo-four_twos = چهار ۲
pusoydos-combo-six_pairs = شش جفت

# =============================================================================
# صفحه‌ی پایان
# =============================================================================

pusoydos-game-over = بازی تمام شد! { $player } باخت!
pusoydos-game-over-points = بازی تمام شد! { $player } با { $score } امتیاز برنده شد!
pusoydos-game-over-losses = بازی تمام شد! { $player } با { $count } باخت باخت!
pusoydos-line-format = { $rank }. { $player }: { $score } امتیاز
pusoydos-line-format-wins = { $rank }. { $player }: { $wins } { $wins ->
    [one] برد
   *[other] برد
}
pusoydos-line-format-losses = { $rank }. { $player }: { $losses } { $losses ->
    [one] باخت
   *[other] باخت
}