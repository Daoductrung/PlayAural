game-name-yahtzee = یاتزی

yahtzee-roll = پرتاب مجدد ({ $count } باقی‌مانده)
yahtzee-roll-all = پرتاب تاس‌ها

yahtzee-score-ones = یک‌ها برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-twos = دوها برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-threes = سه‌ها برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-fours = چهارها برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-fives = پنج‌ها برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-sixes = شش‌ها برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}

yahtzee-score-three-kind = سه‌تایی برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-four-kind = چهارتایی برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-full-house = فول‌هاوس برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-small-straight = دنباله‌ی کوچک برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-large-straight = دنباله‌ی بزرگ برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-yahtzee = یاتزی برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}
yahtzee-score-chance = شانس برای { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
}

yahtzee-you-rolled = شما پرتاب کردید: { $dice }. { $remaining ->
    [0] یک دسته‌ی امتیازدهی انتخاب کنید.
   *[other] { $remaining } { $remaining ->
        [one] پرتاب
       *[other] پرتاب
    } باقی‌مانده.
}
yahtzee-player-rolled = { $player } پرتاب کرد: { $dice }. { $remaining ->
    [0] او باید یک دسته‌ی امتیازدهی انتخاب کند.
   *[other] { $remaining } { $remaining ->
        [one] پرتاب
       *[other] پرتاب
    } باقی‌مانده.
}
yahtzee-you-rolled-brief = شما پرتاب کردید: { $dice }.
yahtzee-player-rolled-brief = { $player } پرتاب کرد: { $dice }.

yahtzee-you-scored = شما { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
} در { $category } کسب کردید.
yahtzee-player-scored = { $player } { $points } { $points ->
    [one] امتیاز
   *[other] امتیاز
} در { $category } کسب کرد.
yahtzee-you-scored-brief = { $points } در { $category }.
yahtzee-player-scored-brief = { $player }: { $points } در { $category }.

yahtzee-you-bonus = پاداش یاتزی! +۱۰۰ امتیاز
yahtzee-player-bonus = { $player } پاداش یاتزی گرفت! +۱۰۰ امتیاز
yahtzee-you-bonus-brief = پاداش یاتزی، +۱۰۰.
yahtzee-player-bonus-brief = { $player }: پاداش یاتزی، +۱۰۰.

yahtzee-you-upper-bonus = پاداش بخش بالا! +۳۵ امتیاز ({ $total } در بخش بالا)
yahtzee-player-upper-bonus = { $player } پاداش بخش بالا را کسب کرد! +۳۵ امتیاز ({ $total } در بخش بالا)
yahtzee-you-upper-bonus-brief = پاداش بالا، +۳۵.
yahtzee-player-upper-bonus-brief = { $player }: پاداش بالا، +۳۵.
yahtzee-you-upper-bonus-missed = پاداش بخش بالا از دست رفت. شما { $total } امتیاز کسب کردید؛ به { $needed } امتیاز دیگر نیاز داشتید.
yahtzee-player-upper-bonus-missed = { $player } پاداش بخش بالا را با { $total } امتیاز در بخش بالا از دست داد، { $needed } امتیاز کم آورد.
yahtzee-you-upper-bonus-missed-brief = پاداش بالا از دست رفت؛ { $needed } کم آورد.
yahtzee-player-upper-bonus-missed-brief = { $player }: پاداش بالا از دست رفت، { $needed } کم آورد.

yahtzee-check-scoresheet = مشاهده‌ی کارت امتیاز
yahtzee-check-all-scorecards = مشاهده‌ی کارت امتیاز همه‌ی بازیکنان
yahtzee-select-scorecard-player = کارت امتیاز یک بازیکن را انتخاب کنید.
yahtzee-scorecard-no-players = هیچ بازیکن فعالی هنوز کارت امتیاز در این بازی ندارد.
yahtzee-scorecard-player-unavailable = آن بازیکن دیگر برای مشاهده در دسترس نیست. دوباره لیست کارت امتیاز را باز کنید و یک بازیکن فعال انتخاب کنید.
yahtzee-view-dice = مشاهده‌ی دست
yahtzee-your-dice = تاس‌های شما: { $dice }.
yahtzee-your-dice-kept = تاس‌های شما: { $dice }. نگهداری‌شده: { $kept }.
yahtzee-current-dice = تاس‌های { $player }: { $dice }.
yahtzee-current-dice-kept = تاس‌های { $player }: { $dice }. نگهداری‌شده: { $kept }.
yahtzee-not-rolled = بازیکن فعلی هنوز پرتاب نکرده است.

yahtzee-scoresheet-header = کارت امتیاز { $player }
yahtzee-scoresheet-upper = بخش بالا:
yahtzee-scoresheet-lower = بخش پایین:
yahtzee-scoresheet-upper-total-bonus = مجموع بالا: { $total } (پاداش: +۳۵)
yahtzee-scoresheet-upper-total-needed = مجموع بالا: { $total } ({ $needed } امتیاز دیگر برای پاداش)
yahtzee-scoresheet-yahtzee-bonus = پاداش‌های یاتزی: { $count } × ۱۰۰ = { $total }
yahtzee-scoresheet-grand-total = امتیاز کل: { $total }

yahtzee-category-ones = یک‌ها
yahtzee-category-twos = دوها
yahtzee-category-threes = سه‌ها
yahtzee-category-fours = چهارها
yahtzee-category-fives = پنج‌ها
yahtzee-category-sixes = شش‌ها
yahtzee-category-three-kind = سه‌تایی
yahtzee-category-four-kind = چهارتایی
yahtzee-category-full-house = فول‌هاوس
yahtzee-category-small-straight = دنباله‌ی کوچک
yahtzee-category-large-straight = دنباله‌ی بزرگ
yahtzee-category-yahtzee = یاتزی
yahtzee-category-chance = شانس

yahtzee-you-win = شما با { $score } { $score ->
    [one] امتیاز
   *[other] امتیاز
} برنده شدید!
yahtzee-player-wins = { $player } با { $score } { $score ->
    [one] امتیاز
   *[other] امتیاز
} برنده شد!
yahtzee-winners-tie = تساوی! { $players } همه { $score } امتیاز کسب کردند!

yahtzee-set-rounds = تعداد بازی‌ها: { $rounds }
yahtzee-enter-rounds = تعداد بازی‌ها را وارد کنید (۱-۱۰):
yahtzee-option-changed-rounds = تعداد بازی‌ها روی { $rounds } تنظیم شد.
yahtzee-desc-num-games = تعداد کارت‌های امتیاز کامل یاتزی که قبل از مقایسه‌ی مجموع نهایی انجام می‌شود (پیش‌فرض ۱، محدوده ۱-۱۰).

yahtzee-no-rolls-left = شما هیچ پرتابی باقی‌نمانده ندارید؛ یک دسته‌ی امتیازدهی باز انتخاب کنید تا نوبت خود را تمام کنید.
yahtzee-roll-first = قبل از انتخاب دسته‌ی امتیازدهی، تاس‌ها را پرتاب کنید.
yahtzee-category-filled = آن دسته قبلاً امتیاز دارد. دسته‌ای را انتخاب کنید که هنوز در کارت امتیاز شما باز است.
yahtzee-joker-upper-required = قانون جوکر: چون این یاتزی { $face } نشان می‌دهد، قبل از هر دسته‌ی دیگری باید جعبه‌ی بخش بالا را برای { $face } امتیازدهی کنید.
yahtzee-joker-lower-required = قانون جوکر: جعبه‌ی بخش بالا برای { $face } قبلاً پر شده است، بنابراین قبل از استفاده از جعبه‌ی بخش بالا، باید یک دسته‌ی باز از بخش پایین انتخاب کنید.