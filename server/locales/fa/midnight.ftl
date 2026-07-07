game-name-midnight = ۱-۴-۲۴

midnight-roll = پرتاب تاس
midnight-keep-die = نگهداشتن { $value }
midnight-bank = ذخیره
midnight-check-dice = مشاهده‌ی تاس‌های فعلی
midnight-check-round-status = مشاهده‌ی وضعیت دور

midnight-round-start = دور { $round } از { $total }.
midnight-round-start-brief = دور { $round }/{ $total }.

midnight-you-rolled = شما پرتاب کردید: { $dice }.
midnight-player-rolled = { $player } پرتاب کرد: { $dice }.
midnight-you-rolled-brief = شما { $dice } پرتاب کردید.
midnight-player-rolled-brief = { $player }: { $dice }.

midnight-you-keep = شما تاس { $index } را نگه می‌دارید که { $die } نشان می‌دهد.
midnight-player-keeps = { $player } تاس { $index } را نگه می‌دارد که { $die } نشان می‌دهد.
midnight-you-keep-brief = شما { $die } را نگه می‌دارید.
midnight-player-keeps-brief = { $player } { $die } را نگه می‌دارد.
midnight-you-unkeep = شما تاس { $index } را که { $die } نشان می‌دهد، به استخر پرتاب مجدد بازمی‌گردانید.
midnight-player-unkeeps = { $player } تاس { $index } را که { $die } نشان می‌دهد، به استخر پرتاب مجدد بازمی‌گرداند.
midnight-you-unkeep-brief = شما { $die } را دوباره می‌اندازید.
midnight-player-unkeeps-brief = { $player } { $die } را دوباره می‌اندازد.

midnight-you-scored = شما با ۱ و ۴ امتیاز می‌گیرید و { $score } از { $scoring_dice } کسب می‌کنید.
midnight-scored = { $player } با ۱ و ۴ امتیاز می‌گیرد و { $score } از { $scoring_dice } کسب می‌کند.
midnight-you-scored-brief = شما { $score } امتیاز گرفتید.
midnight-scored-brief = { $player }: { $score }.
midnight-you-disqualified = شما رد صلاحیت می‌شوید چون { $missing } را ندارید.
midnight-player-disqualified = { $player } رد صلاحیت می‌شود چون { $missing } را ندارد.
midnight-you-disqualified-brief = شما { $missing } را ندارید.
midnight-player-disqualified-brief = { $player } { $missing } را ندارد.

midnight-you-win-round = شما دور { $round } را با { $score } برنده شدید.
midnight-round-winner = { $player } دور { $round } را با { $score } برنده شد.
midnight-you-win-round-brief = شما دور { $round } را بردید: { $score }.
midnight-round-winner-brief = { $player } دور { $round } را برد: { $score }.
midnight-round-tie = دور با { $score } بین { $players } مساوی شد. هیچ برنده‌ای برای دور اعلام نمی‌شود.
midnight-all-disqualified = همه‌ی بازیکنان ۱ و ۴ مورد نیاز را از دست دادند. هیچ برنده‌ای برای دور اعلام نمی‌شود.
midnight-all-disqualified-brief = هیچ‌کس امتیاز نمی‌گیرد.

midnight-you-win-game = شما بازی را با { $wins } { $wins ->
    [one] برد دور
   *[other] برد دور
} برنده شدید!
midnight-game-winner = { $player } بازی را با { $wins } { $wins ->
    [one] برد دور
   *[other] برد دور
} برنده شد!
midnight-you-win-game-brief = شما برنده شدید: { $wins }.
midnight-game-winner-brief = { $player } برنده شد: { $wins }.
midnight-game-tie = بازی مساوی شد. { $players } هر کدام با { $wins } { $wins ->
    [one] برد دور
   *[other] برد دور
} به پایان رسیدند.

midnight-set-rounds = تعداد دورها: { $rounds }
midnight-enter-rounds = تعداد دورها را وارد کنید:
midnight-option-changed-rounds = تعداد دورها به { $rounds } تغییر یافت
midnight-desc-rounds = تعداد دورهای ۱-۴-۲۴ که قبل از امتیازدهی نهایی انجام می‌شود (پیش‌فرض ۵، محدوده ۱-۲۰).
midnight-error-rounds-out-of-range = ۱-۴-۲۴ از { $min } تا { $max } دور را پشتیبانی می‌کند. تنظیم فعلی: { $rounds }.

midnight-need-to-roll = قبل از انتخاب تاس برای نگهداشتن، تاس را پرتاب کنید.
midnight-no-dice-to-keep = هیچ تاسی برای پرتاب یا نگهداشتن باقی نمانده است.
midnight-must-keep-one = قبل از پرتاب مجدد، حداقل یک تاس تازه پرتاب‌شده را نگه دارید.
midnight-must-roll-first = قبل از ذخیره‌ی نوبت خود، تاس را پرتاب کنید.
midnight-keep-all-first = قبل از ذخیره، درباره‌ی هر تاس تصمیم بگیرید. ابتدا همه‌ی تاس‌های باز را نگه دارید یا بازگردانید.
midnight-invalid-die-index = آن تاس در این پرتاب در دسترس نیست.

midnight-die-locked = { $value } (قفل)
midnight-die-kept = { $value } (نگهداشته‌شده)
midnight-die-value = { $value }
midnight-die-index = تاس { $index }

midnight-your-dice-not-rolled = شما هنوز در این نوبت تاس نینداخته‌اید.
midnight-player-dice-not-rolled = { $player } هنوز در این نوبت تاس نینداخته است.
midnight-your-dice-status =
    { $qualified ->
        [yes] تاس‌های شما: { $dice }. قفل‌شده: { $locked }; نگهداشته‌شده برای پرتاب بعدی: { $kept }; تاس‌های زنده: { $remaining }. امتیاز فعلی واجد شرایط { $score } از { $scoring_dice } خواهد بود.
       *[no] تاس‌های شما: { $dice }. قفل‌شده: { $locked }; نگهداشته‌شده برای پرتاب بعدی: { $kept }; تاس‌های زنده: { $remaining }. هنوز به { $missing } برای واجد شرایط شدن نیاز دارید.
    }
midnight-player-dice-status =
    { $qualified ->
        [yes] تاس‌های { $player }: { $dice }. قفل‌شده: { $locked }; نگهداشته‌شده برای پرتاب بعدی: { $kept }; تاس‌های زنده: { $remaining }. امتیاز فعلی واجد شرایط { $score } از { $scoring_dice } خواهد بود.
       *[no] تاس‌های { $player }: { $dice }. قفل‌شده: { $locked }; نگهداشته‌شده برای پرتاب بعدی: { $kept }; تاس‌های زنده: { $remaining }. او هنوز به { $missing } برای واجد شرایط شدن نیاز دارد.
    }

midnight-status-round = دور { $round } از { $total }
midnight-status-current-player = نوبت فعلی: { $player }
midnight-status-current-not-rolled = { $player } هنوز تاس نینداخته است.
midnight-status-current-dice =
    { $qualified ->
        [yes] تاس‌های فعلی برای { $player }: { $dice }. امتیاز احتمالی: { $score } از { $scoring_dice }. قفل‌شده { $locked }، نگهداشته‌شده { $kept}، زنده { $remaining}.
       *[no] تاس‌های فعلی برای { $player }: { $dice }. { $missing} از دست رفته. قفل‌شده { $locked }، نگهداشته‌شده { $kept}، زنده { $remaining}.
    }
midnight-status-dice-not-rolled = پرتاب نشده
midnight-status-last-qualified = آخرین نوبت: { $player } { $dice } پرتاب کرد و { $score } امتیاز گرفت.
midnight-status-last-disqualified = آخرین نوبت: { $player } { $dice } پرتاب کرد و واجد شرایط نشد.
midnight-status-standing-line =
    { $qualified ->
        [yes] { $rank }. { $player }: { $wins } برد دور؛ دور فعلی { $current}، واجد شرایط.
       *[no] { $rank }. { $player }: { $wins } برد دور؛ دور فعلی { $current}، واجد شرایط نیست.
    }

midnight-score-unit-round-wins = { $count ->
    [one] برد دور
   *[other] برد دور
}
midnight-end-score = { $rank }. { $player }: { $wins } { $wins ->
    [one] برد دور
   *[other] برد دور
}