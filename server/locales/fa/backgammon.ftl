# Backgammon - پیام‌های بازی

game-name-backgammon = تخته‌نرد

# رنگ‌ها
backgammon-color-red = قرمز
backgammon-color-white = سفید

# راهنماهای منو
backgammon-unavailable = در دسترس نیست

# شروع بازی
backgammon-game-started = { $red } قرمز بازی می‌کند، { $white } سفید بازی می‌کند.
backgammon-opening-roll = تاس شروع: { $red } { $red_die } انداخت، { $white } { $white_die } انداخت.
backgammon-opening-tie = هر دو { $die } انداختند، دوباره انداختن...
backgammon-opening-winner-you = شما با { $die1 } و { $die2 } اول می‌روید.
backgammon-opening-winner-player = { $player } با { $die1 } و { $die2 } اول می‌رود.

# تاس
backgammon-roll-you = شما { $die1 } و { $die2 } انداختید.
backgammon-roll-player = { $player } { $die1 } و { $die2 } انداخت.

# بدون حرکت
backgammon-no-moves-you = شما حرکت قانونی ندارید، پس نوبت شما تمام می‌شود.
backgammon-no-moves-player = { $player } حرکت قانونی ندارد، پس نوبت او تمام می‌شود.

# شرح حرکت مختصر
backgammon-brief-move-normal = { $is_self ->
    [yes] شما: { $src } به { $dest }.
    *[no] { $player }: { $src } به { $dest }.
}
backgammon-brief-move-hit = { $is_self ->
    [yes] شما: { $src } به { $dest }، خورد { $opponent }.
    [spectator] { $player }: { $src } به { $dest }، خورد { $opponent }.
    *[no] { $player }: { $src } به { $dest }، خورد شما.
}
backgammon-brief-move-bar = { $is_self ->
    [yes] شما: میله به { $dest }.
    *[no] { $player }: میله به { $dest }.
}
backgammon-brief-move-bar-hit = { $is_self ->
    [yes] شما: میله به { $dest }، خورد { $opponent }.
    [spectator] { $player }: میله به { $dest }، خورد { $opponent }.
    *[no] { $player }: میله به { $dest }، خورد شما.
}
backgammon-brief-move-bearoff = { $is_self ->
    [yes] شما: { $src } خارج.
    *[no] { $player }: { $src } خارج.
}

# شرح حرکت مفصل
backgammon-verbose-move-normal = { $is_self ->
    [yes] شما یک مهره را از خانه‌ی { $src } به خانه‌ی { $dest } حرکت می‌دهید.
    *[no] { $player } یک مهره را از خانه‌ی { $src } به خانه‌ی { $dest } حرکت می‌دهد.
} { $src_count ->
    [0] خانه‌ی { $src } اکنون خالی است، { $dest_count } مهره در خانه‌ی { $dest }.
    *[other] { $src_count } مهره در خانه‌ی { $src }، { $dest_count } مهره در خانه‌ی { $dest }.
}
backgammon-verbose-move-hit = { $is_self ->
    [yes] شما یک مهره را از خانه‌ی { $src } حرکت می‌دهید تا مهره‌ی { $opponent } را در خانه‌ی { $dest } بزنید.
    [spectator] { $player } یک مهره را از خانه‌ی { $src } حرکت می‌دهد تا مهره‌ی { $opponent } را در خانه‌ی { $dest } بزند.
    *[no] { $player } یک مهره را از خانه‌ی { $src } حرکت می‌دهد تا مهره‌ی شما را در خانه‌ی { $dest } بزند.
} { $src_count ->
    [0] خانه‌ی { $src } اکنون خالی است.
    *[other] { $src_count } مهره در خانه‌ی { $src } باقی‌مانده.
}
backgammon-verbose-move-bar = { $is_self ->
    [yes] شما از میله به خانه‌ی { $dest } وارد می‌شوید.
    *[no] { $player } از میله به خانه‌ی { $dest } وارد می‌شود.
} { $dest_count } مهره در خانه‌ی { $dest }.
backgammon-verbose-move-bar-hit = { $is_self ->
    [yes] شما از میله وارد می‌شوید تا مهره‌ی { $opponent } را در خانه‌ی { $dest } بزنید.
    [spectator] { $player } از میله وارد می‌شود تا مهره‌ی { $opponent } را در خانه‌ی { $dest } بزند.
    *[no] { $player } از میله وارد می‌شود تا مهره‌ی شما را در خانه‌ی { $dest } بزند.
}
backgammon-verbose-move-bearoff = { $is_self ->
    [yes] شما از خانه‌ی { $src } بیرون می‌آورید.
    *[no] { $player } از خانه‌ی { $src } بیرون می‌آورد.
} { $src_count ->
    [0] خانه‌ی { $src } اکنون خالی است.
    *[other] { $src_count } مهره در خانه‌ی { $src } باقی‌مانده.
}

# دابل کردن
backgammon-doubles-you = شما پیشنهاد دابل کردن تاس به { $value } را می‌دهید.
backgammon-doubles-player = { $player } پیشنهاد دابل کردن تاس به { $value } را می‌دهد.
backgammon-accepts-you = شما دابل را می‌پذیرید و مالکیت تاس را به دست می‌گیرید.
backgammon-accepts-player = { $player } دابل را می‌پذیرد و مالکیت تاس را به دست می‌گیرد.
backgammon-drops-you = شما دابل را رها می‌کنید و مقدار فعلی تاس را می‌پذیرید.
backgammon-drops-player = { $player } دابل را رها می‌کند و مقدار فعلی تاس را می‌پذیرد.
backgammon-accept = پذیرش
backgammon-drop = رها کردن

# برچسب‌های خانه‌ها
backgammon-point-empty = { $point }
backgammon-point-empty-selected = { $point } انتخاب شد
backgammon-point-occupied = { $point } { $color }، { $count }
backgammon-point-occupied-selected = { $point } { $color }، { $count } انتخاب شد

# برچسب‌های اقدامات
backgammon-label-double = دابل
backgammon-label-undo = برگرداندن
backgammon-label-next = بعدی
backgammon-label-previous = قبلی
backgammon-label-deselect = لغو انتخاب
backgammon-label-next-destination = مقصد بعدی
backgammon-label-previous-destination = مقصد قبلی

# بازخورد انتخاب
backgammon-selected-point = خانه‌ی { $point } انتخاب شد، { $count } مهره.
backgammon-selected-bar = میله انتخاب شد.
backgammon-deselected = انتخاب لغو شد.
backgammon-no-checkers-there = هیچ مهره‌ای آنجا نیست.
backgammon-not-your-checkers = این مهره‌ها متعلق به شما نیستند.
backgammon-no-moves-from-here = هیچ حرکت قانونی از اینجا وجود ندارد.
backgammon-must-enter-from-bar = ابتدا باید از میله وارد شوید.
backgammon-illegal-move = حرکت غیرقانونی.
backgammon-no-dice-remaining = شما تاسی برای استفاده در این نوبت ندارید.
backgammon-no-checkers-on-bar = شما هیچ مهره‌ای روی میله برای وارد کردن ندارید.
backgammon-invalid-destination = آن مقصد یک خانه‌ی قابل بازی در تخته‌نرد نیست.
backgammon-source-empty = خانه‌ی { $point } هیچ مهره‌ای برای حرکت ندارد.
backgammon-source-opponent = خانه‌ی { $point } شامل مهره‌های حریف شماست.
backgammon-destination-blocked = خانه‌ی { $point } توسط { $count } مهره‌ی حریف مسدود شده است.
backgammon-bar-entry-blocked = نمی‌توانید در خانه‌ی { $point } وارد شوید؛ توسط { $count } مهره‌ی حریف مسدود شده است.
backgammon-no-die-for-bar-entry = هیچ‌کدام از تاس‌های باقی‌مانده‌ی شما ({ $dice }) در خانه‌ی { $point } وارد نمی‌شود.
backgammon-no-die-for-destination = هیچ‌کدام از تاس‌های باقی‌مانده‌ی شما ({ $dice }) از خانه‌ی { $src } به خانه‌ی { $dest } حرکت نمی‌کند.
backgammon-must-use-forced-die = باید از { $dice } استفاده کنید زیرا تخته‌نرد در صورت امکان به استفاده از هر دو تاس نیاز دارد، یا زمانی که فقط یک تاس قابل بازی است، تاس بزرگ‌تر را الزامی می‌کند.
backgammon-bearoff-not-home = هنوز نمی‌توانید بیرون بیاورید زیرا همه‌ی مهره‌های شما در خانه‌ی خودی نیستند.
backgammon-bearoff-blocked = نمی‌توانید از خانه‌ی { $point } با تاس { $die } بیرون بیاورید، زیرا مهره‌هایی در خانه‌ی { $blocking_point } شما وجود دارد.
backgammon-bearoff-no-die = نمی‌توانید از خانه‌ی { $point } با تاس‌های باقی‌مانده‌ی خود ({ $die }) بیرون بیاورید.
backgammon-nothing-to-undo = چیزی برای برگرداندن وجود ندارد.
backgammon-undone = حرکت برگردانده شد.
backgammon-cannot-double = در حال حاضر نمی‌توانید دابل کنید.
backgammon-cannot-undo = چیزی برای برگرداندن وجود ندارد.
backgammon-not-doubling-phase = دابلی برای پاسخ دادن وجود ندارد.
backgammon-need-roll-first = قبل از حرکت مهره باید تاس بیندازید.
backgammon-confirm-drop-double = رها کردن دابل به معنای واگذاری این بازی با مقدار فعلی تاس است. برای تأیید، ظرف ۱۰ ثانیه دوباره رها کردن را فشار دهید.

# میانبرهای اطلاعاتی
backgammon-check-status = وضعیت
backgammon-check-cube = تاس
backgammon-check-pip = تعداد پیپ
backgammon-check-score = امتیاز
backgammon-check-score-detailed = امتیاز دقیق
backgammon-check-dice = تاس‌ها
backgammon-status = میله‌ی قرمز: { $bar_red }. میله‌ی سفید: { $bar_white }. خارج‌شده‌ی قرمز: { $off_red }. خارج‌شده‌ی سفید: { $off_white }.
backgammon-dice = { $dice }
backgammon-dice-none = تاسی وجود ندارد.
backgammon-cube-status = تاس روی { $value }. { $owner ->
    [center] در مرکز، هر بازیکنی می‌تواند دابل کند.
    *[other] متعلق به { $owner }.
} { $can_double ->
    [yes] دابل کردن در حال حاضر امکان‌پذیر است.
    [crawford] این بازی کرافورد است، دابل کردن مجاز نیست.
    *[no] دابل کردن در حال حاضر امکان‌پذیر نیست.
}
backgammon-cube-no-match = در بازی‌های تکی تاس دابل وجود ندارد.
backgammon-pip-count = تعداد پیپ قرمز: { $red_pip }. تعداد پیپ سفید: { $white_pip }.
backgammon-match-score-line = { $player }: { $score } از { $match_length }.
backgammon-match-score-cube-line = تاس: { $cube }.

# امتیازدهی
backgammon-wins-game-you = شما { $points } { $points ->
    [one] امتیاز
    *[other] امتیاز
} برنده می‌شوید.
backgammon-wins-game-player = { $player } { $points } { $points ->
    [one] امتیاز
    *[other] امتیاز
} برنده می‌شود.
backgammon-new-game = شروع بازی شماره‌ی { $number }.
backgammon-match-winner-you = شما مسابقه را برنده شدید!
backgammon-match-winner-player = { $player } مسابقه را برد!
backgammon-end-score = { $red } { $red_score } - { $white } { $white_score }. مسابقه تا { $match_length }.
backgammon-crawford = بازی کرافورد: در این بازی دابل کردن مجاز نیست.

# سطح دشواری
backgammon-difficulty-random = تصادفی
backgammon-difficulty-simple = ساده

# گزینه‌ها
backgammon-option-match-length = طول مسابقه: { $match_length }
backgammon-option-select-match-length = تنظیم طول مسابقه (۱-۲۵)
backgammon-option-changed-match-length = طول مسابقه روی { $match_length } تنظیم شد.
backgammon-desc-match-length = امتیاز مورد نیاز برای بردن مسابقه‌ی تخته‌نرد. مقدار ۱ به معنای یک بازی تکی بدون تاس دابل است (پیش‌فرض ۱، محدوده ۱-۲۵).
backgammon-option-bot-difficulty = دشواری ربات: { $bot_difficulty }
backgammon-option-select-bot-difficulty = انتخاب دشواری ربات
backgammon-option-changed-bot-difficulty = دشواری ربات روی { $bot_difficulty } تنظیم شد.
backgammon-desc-bot-difficulty = نحوه‌ی حرکت ربات‌ها را انتخاب می‌کند: تصادفی حرکت‌های قانونی را به‌طور ساده انجام می‌دهد، در حالی که ساده حرکت‌های تاکتیکی قوی‌تر را ترجیح می‌دهد.