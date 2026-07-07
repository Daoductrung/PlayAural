game-name-leftrightcenter = چپ مرکز راست

lrc-roll = پرتاب { $count } { $count ->
    [one] تاس
   *[other] تاس
}
lrc-roll-label = پرتاب تاس

lrc-face-left = چپ
lrc-face-center = مرکز
lrc-face-right = راست
lrc-face-dot = نقطه

lrc-you-roll = شما { $results } می‌اندازید.
lrc-player-rolls = { $player } { $results } می‌اندازد.
lrc-you-roll-brief = شما: { $results }.
lrc-player-rolls-brief = { $player }: { $results }.

lrc-you-pass-left = شما { $count } { $count ->
    [one] تراشه
   *[other] تراشه
} را به چپ به { $target } می‌دهید. { $remaining } برای شما باقی‌مانده؛ { $target } اکنون { $target_total } دارد.
lrc-player-passes-left = { $player } { $count } { $count ->
    [one] تراشه
   *[other] تراشه
} را به چپ به { $target } می‌دهد. { $player } { $remaining } دارد؛ { $target } اکنون { $target_total } دارد.
lrc-you-pass-left-brief = شما، چپ به { $target }: { $count }. باقی‌مانده: { $remaining }.
lrc-player-passes-left-brief = { $player }، چپ به { $target }: { $count }. باقی‌مانده: { $remaining }.

lrc-you-pass-right = شما { $count } { $count ->
    [one] تراشه
   *[other] تراشه
} را به راست به { $target } می‌دهید. { $remaining } برای شما باقی‌مانده؛ { $target } اکنون { $target_total } دارد.
lrc-player-passes-right = { $player } { $count } { $count ->
    [one] تراشه
   *[other] تراشه
} را به راست به { $target } می‌دهد. { $player } { $remaining } دارد؛ { $target } اکنون { $target_total } دارد.
lrc-you-pass-right-brief = شما، راست به { $target }: { $count }. باقی‌مانده: { $remaining }.
lrc-player-passes-right-brief = { $player }، راست به { $target }: { $count }. باقی‌مانده: { $remaining }.

lrc-you-pass-center = شما { $count } { $count ->
    [one] تراشه
   *[other] تراشه
} را در مرکز قرار می‌دهید. { $remaining } برای شما باقی‌مانده؛ مرکز اکنون { $center } دارد.
lrc-player-passes-center = { $player } { $count } { $count ->
    [one] تراشه
   *[other] تراشه
} را در مرکز قرار می‌دهد. { $player } { $remaining } دارد؛ مرکز اکنون { $center } دارد.
lrc-you-pass-center-brief = شما، مرکز: { $count }. باقی‌مانده: { $remaining }. مجموع مرکز: { $center }.
lrc-player-passes-center-brief = { $player }، مرکز: { $count }. باقی‌مانده: { $remaining }. مجموع مرکز: { $center }.

lrc-you-keep-all = همه‌ی تاس‌های شما نقطه هستند، بنابراین همه‌ی { $count } { $count ->
    [one] تراشه
   *[other] تراشه
} را نگه می‌دارید.
lrc-player-keeps-all = همه‌ی تاس‌های { $player } نقطه هستند، بنابراین همه‌ی { $count } { $count ->
    [one] تراشه
   *[other] تراشه
} را نگه می‌دارند.
lrc-you-keep-all-brief = شما: بدون انتقال؛ { $count } { $count ->
    [one] تراشه
   *[other] تراشه
}.
lrc-player-keeps-all-brief = { $player }: بدون انتقال؛ { $count } { $count ->
    [one] تراشه
   *[other] تراشه
}.

lrc-you-skip-no-chips = شما تراشه ندارید، بنابراین نوبت شما رد می‌شود. شما در بازی باقی می‌مانید و می‌توانید از هر دو همسایه تراشه دریافت کنید.
lrc-player-skips-no-chips = { $player } تراشه ندارد، بنابراین نوبت او رد می‌شود. او در بازی باقی می‌ماند و می‌تواند از هر دو همسایه تراشه دریافت کند.
lrc-you-skip-no-chips-brief = شما: بدون تراشه؛ نوبت رد شد.
lrc-player-skips-no-chips-brief = { $player }: بدون تراشه؛ نوبت رد شد.

lrc-you-win = شما آخرین بازیکن با تراشه هستید و با { $count } تراشه‌ی باقی‌مانده برنده می‌شوید. شما { $center } { $center ->
    [one] تراشه
   *[other] تراشه
} موجود در مرکز را برمی‌دارید.
lrc-player-wins = { $player } آخرین بازیکن با تراشه است و با { $count } تراشه‌ی باقی‌مانده برنده می‌شود. او { $center } { $center ->
    [one] تراشه
   *[other] تراشه
} موجود در مرکز را برمی‌دارد.
lrc-you-win-brief = شما برنده شدید. تراشه‌های شما: { $count }. مرکز: { $center }.
lrc-player-wins-brief = { $player } برنده شد. تراشه‌ها: { $count }. مرکز: { $center }.

lrc-roll-already-resolving = پرتاب شما در حال بررسی است. منتظر پایان انتقال تراشه‌ها باشید.
lrc-no-chips-to-roll = شما تراشه‌ای برای پرتاب ندارید. نوبت شما به‌طور خودکار رد می‌شود.

lrc-center-pot = جایزه‌ی مرکز: { $count } { $count ->
    [one] تراشه
   *[other] تراشه
}.
lrc-check-center = بررسی جایزه‌ی مرکز
lrc-check-last-roll = بررسی آخرین پرتاب
lrc-last-roll-none = هنوز تاسی پرتاب نشده است.
lrc-last-roll-you = آخرین پرتاب شما { $results } بود.
lrc-last-roll-player = آخرین پرتاب { $player } { $results } بود.

lrc-set-starting-chips = تراشه‌های اولیه: { $count }
lrc-enter-starting-chips = تراشه‌های اولیه را وارد کنید:
lrc-option-changed-starting-chips = تراشه‌های اولیه روی { $count } تنظیم شد.
leftrightcenter-desc-starting-chips = تعداد تراشه‌هایی که هر بازیکن در چپ مرکز راست با آن شروع می‌کند (پیش‌فرض ۳، محدوده ۱-۱۰).
lrc-error-starting-chips-invalid = تراشه‌های اولیه باید بین { $min } و { $max } باشند؛ مقدار فعلی { $count } است.

lrc-line-format = { $player }: { $chips } { $chips ->
    [one] تراشه
   *[other] تراشه
}