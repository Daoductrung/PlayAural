game-round-start = دور { $round }.
game-round-end = دور { $round } کامل شد.
game-turn-start = نوبت { $player } است.
game-turn-start-you = نوبت شماست.
game-turn-start-player = نوبت { $player } است.
game-no-turn = در حال حاضر نوبت هیچ‌کس نیست.

game-score-line = { $player }: { $score } { $unit }
game-score-line-target = { $player }: { $score }/{ $target } { $unit }
game-score-unit-points = { $count ->
    [one] امتیاز
   *[other] امتیاز
}
game-score-unit-chips = { $count ->
    [one] تراشه
   *[other] تراشه
}
game-score-unit-coins = { $count ->
    [one] سکه
   *[other] سکه
}
game-score-unit-health = سلامتی
game-score-unit-ninetynine-tokens = { $count ->
    [one] نشان
   *[other] نشان
}
game-score-unit-tokens-home = { $count ->
    [one] نشان در خانه
   *[other] نشان در خانه
}
game-score-unit-pawns-home = { $count ->
    [one] مهره در خانه
   *[other] مهره در خانه
}
game-score-unit-hand-wins = { $count ->
    [one] برد دست
   *[other] برد دست
}
game-score-unit-light = نور
game-final-scores-header = امتیازات نهایی:

game-winner = { $player } برنده شد!
game-winner-you = شما برنده شدید!
game-winner-score = { $player } با { $score } امتیاز برنده شد!
game-tiebreaker = تساوی! دور تساوی‌شکن!
game-tiebreaker-players = تساوی بین { $players }! دور تساوی‌شکن!
game-eliminated = { $player } با { $score } امتیاز حذف شد.

game-set-target-score = امتیاز هدف: { $score }
game-enter-target-score = امتیاز هدف را وارد کنید:
game-option-changed-target = امتیاز هدف روی { $score } تنظیم شد.

game-set-team-mode = حالت تیمی: { $mode }
game-select-team-mode = حالت تیمی را انتخاب کنید
game-option-changed-team = حالت تیمی روی { $mode } تنظیم شد.
game-team-mode-individual = انفرادی
game-team-mode-x-teams-of-y = { $num_teams } تیم { $team_size } نفره
game-team-name = تیم { $index }
team-arrangement-started = چینش تیم‌ها آغاز شد. تیم‌ها را بررسی کنید، در صورت نیاز اعضا را جابه‌جا کنید، سپس برای شروع تأیید کنید.
team-arrangement-confirm = تأیید تیم‌ها و شروع
team-arrangement-read = مشاهده‌ی تیم‌ها
team-arrangement-select-member-action = انتخاب عضو تیم
team-arrangement-select-member = یک عضو تیم انتخاب کنید
team-arrangement-select-swap-target = یک بازیکن را برای جابه‌جایی انتخاب کنید
team-arrangement-swap-member = انتخاب هدف جابه‌جایی
team-arrangement-swap-member-selected = جابه‌جایی { $player } با...
team-arrangement-cancel = لغو چینش تیم‌ها
team-arrangement-line = { $team }: { $members }
team-arrangement-turn-order = ترتیب نوبت: { $players }
team-arrangement-member-option = { $player }، { $team }، { $selected }
team-arrangement-selected = انتخاب شد
team-arrangement-not-selected = انتخاب نشد
team-arrangement-member-selected = { $player } از { $team } انتخاب شد. یک بازیکن از تیم دیگر را برای جابه‌جایی انتخاب کنید.
team-arrangement-swapped = { $first } و { $second } تیم‌های خود را عوض کردند.
team-arrangement-cancelled = چینش تیم‌ها لغو شد.
team-arrangement-cancelled-roster = چینش تیم‌ها به دلیل تغییر لیست بازیکنان لغو شد.
team-arrangement-refreshed = لیست بازیکنان تغییر کرد. چینش تیم‌ها به‌روزرسانی شد.
team-arrangement-in-progress = ابتدا چینش تیم‌ها را تمام یا لغو کنید.
team-arrangement-not-active = چینش تیم‌ها فعال نیست.
team-arrangement-select-first = ابتدا یک عضو تیم انتخاب کنید.
team-arrangement-player-missing = آن بازیکن دیگر برای چینش تیم‌ها در دسترس نیست.
team-arrangement-same-team = از یک تیم دیگر انتخاب کنید.
team-arrangement-swap-failed = جابه‌جایی آن اعضای تیم امکان‌پذیر نبود.

status-box-closed = اطلاعات وضعیت بسته شد.

game-leave = ترک بازی

round-timer-paused = { $player } بازی را متوقف کرد (برای شروع دور بعدی p را فشار دهید).
round-timer-resumed = زمان‌سنج دور از سر گرفته شد.
round-timer-countdown = دور بعدی در { $seconds }...

dice-keeping = نگهداشتن { $value }.
dice-rerolling = پرتاب مجدد { $value }.
dice-locked = آن تاس قفل است و قابل تغییر نیست.
dice-status-label-locked = { $value } (قفل)
dice-status-label-kept = { $value } (نگهداشته‌شده)

game-deal-counter = پخش { $current }/{ $total }.
game-you-deal = شما کارت‌ها را پخش می‌کنید.
game-player-deals = { $player } کارت‌ها را پخش می‌کند.

card-name = { $rank } { $suit }
no-cards = بدون کارت

suit-diamonds = خشت
suit-clubs = پیک
suit-hearts = دل
suit-spades = خشت‌های سیاه

rank-ace = آس
rank-two = ۲
rank-three = ۳
rank-four = ۴
rank-five = ۵
rank-six = ۶
rank-seven = ۷
rank-eight = ۸
rank-nine = ۹
rank-ten = ۱۰
rank-jack = سرباز
rank-queen = بی‌بی
rank-king = شاه

rank-ace-plural = آس‌ها
rank-two-plural = دوها
rank-three-plural = سه‌ها
rank-four-plural = چهارها
rank-five-plural = پنج‌ها
rank-six-plural = شش‌ها
rank-seven-plural = هفت‌ها
rank-eight-plural = هشت‌ها
rank-nine-plural = نه‌ها
rank-ten-plural = ده‌ها
rank-jack-plural = سربازها
rank-queen-plural = بی‌بی‌ها
rank-king-plural = شاه‌ها


poker-high-card-with = { $high } بالا، با { $rest }
poker-high-card = { $high } بالا
poker-pair-with = جفت { $pair }، با { $rest }
poker-pair = جفت { $pair }
poker-two-pair-with = دو جفت، { $high } و { $low }، با { $kicker }
poker-two-pair = دو جفت، { $high } و { $low }
poker-trips-with = سه‌تایی، { $trips }، با { $rest }
poker-trips = سه‌تایی، { $trips }
poker-straight-high = دنباله‌ی { $high } بالا
poker-flush-high-with = پنج‌برگ { $high } بالا، با { $rest }
poker-full-house = فول‌هاوس، { $trips } روی { $pair }
poker-quads-with = چهارتایی، { $quads }، با { $kicker }
poker-quads = چهارتایی، { $quads }
poker-royal-flush = رویال فلاش
poker-straight-flush-high = دنباله‌ی پنج‌برگ { $high } بالا
poker-unknown-hand = دست ناشناس

game-error-invalid-team-mode = حالت تیمی انتخاب‌شده برای تعداد فعلی بازیکنان معتبر نیست.

documentation-menu = مستندات
introduction = مقدمه
community-rules = قوانین جامعه
global-keys = کنترل‌های عمومی
game-rules = قوانین بازی
changelog = تغییرات
donation = کمک مالی
contact = تماس
document-not-found = سند یافت نشد.
help = راهنما

# اطلاعات بازی (Ctrl+I)
game-info = اطلاعات بازی
game-info-header = اطلاعات بازی فعلی
game-info-name = بازی: {$game}
game-info-players = بازیکنان: {$count}
game-info-host = میزبان: {$host}
game-info-status = وضعیت: {$status}
game-info-status-waiting = در انتظار در لابی
game-info-status-playing = در حال اجرا
game-info-options-header = تنظیمات:
game-info-no-options = این بازی گزینه‌های پیکربندی سفارشی ندارد.

# نحوه‌ی بازی (Ctrl+F1)
how-to-play = نحوه‌ی بازی
game-rules-not-available = قوانین {$game} هنوز در دسترس نیست.