game-name-tossup = پرتاب و برد

tossup-roll-first =
    پرتاب { $count } { $count ->
        [one] تاس
       *[other] تاس
    }
tossup-roll-remaining =
    پرتاب { $count } { $count ->
        [one] تاس باقی‌مانده
       *[other] تاس باقی‌مانده
    }
tossup-bank =
    ذخیره‌ی { $points } { $points ->
        [one] امتیاز
       *[other] امتیاز
    }
tossup-check-turn-status = بررسی وضعیت نوبت

tossup-game-start = پرتاب و برد با قوانین { $rules }، { $dice } تاس در هر مجموعه و آستانه‌ی هدف { $target } آغاز می‌شود. از آستانه عبور کنید و نوبت‌های باقی‌مانده را برای بردن کامل کنید.
tossup-game-start-brief = پرتاب و برد آغاز شد. از { $target } عبور کنید.
tossup-round-start = دور { $round } آغاز می‌شود.
tossup-round-start-brief = دور { $round }.

tossup-your-turn =
    نوبت شما. امتیاز ذخیره‌شده‌ی شما { $score } است؛ { $dice } { $dice ->
        [one] تاس
       *[other] تاس
    } را برای شروع پرتاب کنید.
tossup-player-turn =
    نوبت { $player } با { $score } امتیاز ذخیره‌شده و { $dice } { $dice ->
        [one] تاس
       *[other] تاس
    }.
tossup-your-turn-brief = نوبت شما: { $score } امتیاز.
tossup-player-turn-brief = نوبت { $player }: { $score } امتیاز.

tossup-you-roll = شما { $results } پرتاب کردید.
tossup-player-rolls = { $player } { $results } پرتاب کرد.
tossup-you-roll-safe-brief =
    { $fresh ->
        [yes] شما: { $results }; مجموع نوبت { $turn_points }; مجموعه‌ی تازه از { $dice_count }.
       *[no] شما: { $results }; مجموع نوبت { $turn_points }; { $dice_count } باقی‌مانده.
    }
tossup-player-rolls-safe-brief =
    { $fresh ->
        [yes] { $player }: { $results }; مجموع نوبت { $turn_points }; مجموعه‌ی تازه از { $dice_count }.
       *[no] { $player }: { $results }; مجموع نوبت { $turn_points }; { $dice_count } باقی‌مانده.
    }

tossup-result-green = { $count } سبز
tossup-result-yellow = { $count } زرد
tossup-result-red = { $count } قرمز

tossup-you-have-points =
    شما { $gained } تاس سبز را کنار می‌گذارید. مجموع نوبت شما { $turn_points } است، با { $dice_count } { $dice_count ->
        [one] تاس
       *[other] تاس
    } باقی‌مانده.
tossup-player-has-points =
    { $player } { $gained } تاس سبز را کنار می‌گذارد و { $turn_points } امتیاز نوبت دارد، با { $dice_count } { $dice_count ->
        [one] تاس
       *[other] تاس
    } باقی‌مانده.

tossup-you-get-fresh = همه‌ی تاس‌ها سبز هستند. شما یک مجموعه‌ی تازه از { $count } تاس دریافت می‌کنید و می‌توانید دوباره پرتاب کنید یا ذخیره کنید.
tossup-player-gets-fresh = همه‌ی تاس‌ها سبز هستند. { $player } یک مجموعه‌ی تازه از { $count } تاس دریافت می‌کند.

tossup-you-bust =
    { $variant ->
        [Standard] چراغ قرمز: شما هیچ سبزی و حداقل یک قرمز پرتاب کردید. نوبت شما پایان می‌یابد و { $points } امتیاز ذخیره‌نشده را از دست می‌دهید.
       *[PlayAural] همه‌ی تاس‌های پرتاب‌شده قرمز هستند. نوبت شما پایان می‌یابد و { $points } امتیاز ذخیره‌نشده را از دست می‌دهید.
    }
tossup-player-busts =
    { $variant ->
        [Standard] چراغ قرمز: { $player } هیچ سبزی و حداقل یک قرمز پرتاب کرد، نوبت پایان می‌یابد و { $points } امتیاز ذخیره‌نشده را از دست می‌دهد.
       *[PlayAural] همه‌ی تاس‌های پرتاب‌شده‌ی { $player } قرمز هستند، نوبت پایان می‌یابد و { $points } امتیاز ذخیره‌نشده را از دست می‌دهد.
    }
tossup-you-bust-brief = شما: { $results }; شکست؛ از دست دادن { $points }.
tossup-player-busts-brief = { $player }: { $results }; شکست؛ از دست دادن { $points }.

tossup-you-bank = شما { $points } امتیاز ذخیره می‌کنید و مجموع امتیاز شما به { $total } می‌رسد.
tossup-player-banks = { $player } { $points } امتیاز ذخیره می‌کند و مجموع امتیاز او به { $total } می‌رسد.
tossup-you-bank-brief = شما { $points } ذخیره کردید؛ مجموع { $total }.
tossup-player-banks-brief = { $player } { $points } ذخیره کرد؛ مجموع { $total }.

tossup-you-trigger-final-turns =
    شما با { $score } از آستانه‌ی { $target } امتیاز عبور کردید.
    { $count ->
        [one] بازیکن باقی‌مانده یک نوبت نهایی دریافت می‌کند.
       *[other] { $count } بازیکن باقی‌مانده هر کدام یک نوبت نهایی دریافت می‌کنند.
    }
tossup-player-triggers-final-turns =
    { $player } با { $score } از آستانه‌ی { $target } امتیاز عبور کرد.
    { $count ->
        [one] بازیکن باقی‌مانده یک نوبت نهایی دریافت می‌کند.
       *[other] { $count } بازیکن باقی‌مانده هر کدام یک نوبت نهایی دریافت می‌کنند.
    }
tossup-you-trigger-final-turns-brief =
    شما امتیاز شکست‌ناپذیر را روی { $score } تنظیم کردید؛ { $count } { $count ->
        [one] نوبت باقی‌مانده.
       *[other] نوبت باقی‌مانده.
    }
tossup-player-triggers-final-turns-brief =
    { $player } امتیاز شکست‌ناپذیر را روی { $score } تنظیم کرد؛ { $count } { $count ->
        [one] نوبت باقی‌مانده.
       *[other] نوبت باقی‌مانده.
    }

tossup-you-win = شما پرتاب و برد را با { $score } امتیاز برنده شدید.
tossup-winner = { $player } پرتاب و برد را با { $score } امتیاز برنده شد.
tossup-you-win-brief = شما برنده شدید: { $score }.
tossup-winner-brief = { $player } برنده شد: { $score }.
tossup-tie-tiebreaker = { $players } برای بالاترین امتیاز بالای هدف مساوی هستند. فقط آن بازیکنان به دور تساوی‌شکن ادامه می‌دهند.
tossup-tie-tiebreaker-brief = تساوی‌شکن: { $players }.
tossup-tiebreaker-round-start = دور تساوی‌شکن { $round } برای { $players } آغاز می‌شود.
tossup-tiebreaker-round-start-brief = دور تساوی‌شکن { $round }: { $players }.

tossup-your-turn-awaiting-roll =
    نوبت شما هنوز شروع به پرتاب نکرده است. شما { $score } امتیاز ذخیره‌شده و { $dice_count } { $dice_count ->
        [one] تاس
       *[other] تاس
    } آماده دارید.
tossup-player-turn-awaiting-roll =
    { $player } هنوز پرتاب نکرده است. او { $score } امتیاز ذخیره‌شده و { $dice_count } { $dice_count ->
        [one] تاس
       *[other] تاس
    } آماده دارد.
tossup-your-turn-status =
    آخرین پرتاب شما { $results } بود. شما { $turn_points } امتیاز ذخیره‌نشده‌ی نوبت، { $score } امتیاز ذخیره‌شده، و { $dice_count } { $dice_count ->
        [one] تاس
       *[other] تاس
    } آماده برای پرتاب دارید.
tossup-player-turn-status =
    آخرین پرتاب { $player } { $results } بود. او { $turn_points } امتیاز ذخیره‌نشده‌ی نوبت، { $score } امتیاز ذخیره‌شده، و { $dice_count } { $dice_count ->
        [one] تاس
       *[other] تاس
    } آماده برای پرتاب دارد.

tossup-confirm-risky-roll =
    { $winning ->
        [yes] ذخیره‌ی اکنون شما را با { $total } امتیاز، بالای آستانه‌ی { $target } امتیاز، جلو می‌اندازد.
       *[no] شما در حال حاضر { $points } امتیاز ذخیره‌نشده‌ی نوبت دارید.
    }
    پرتاب { $dice } { $dice ->
        [one] تاس
       *[other] تاس
    } حدود { $risk } درصد شانس شکست دارد. برای تأیید، ظرف { $seconds } ثانیه دوباره پرتاب را فشار دهید، یا برای محافظت از امتیازات، ذخیره کنید.

tossup-set-rules-variant = قوانین: { $variant }
tossup-select-rules-variant = قوانین تاس و شکست را انتخاب کنید:
tossup-option-changed-rules = قوانین به { $variant } تغییر یافت.
tossup-desc-rules-variant = کلاسیک از سه وجه سبز، دو وجه زرد و یک وجه قرمز در هر تاس استفاده می‌کند؛ پرتاب بدون سبز و با حداقل یک قرمز، شکست محسوب می‌شود. بخشنده شانس برابر برای هر سه رنگ می‌دهد و فقط در صورت تمام قرمز بودن شکست می‌خورد.

tossup-desc-target-score = بازی پس از ذخیره‌ی امتیاز بیشتر از این مقدار توسط یک بازیکن، وارد نوبت‌های نهایی پاسخ می‌شود (پیش‌فرض ۱۰۰، محدوده ۲۰-۵۰۰).
tossup-set-starting-dice = تاس در هر مجموعه: { $count }
tossup-enter-starting-dice = تعداد تاس در هر مجموعه‌ی تازه را وارد کنید:
tossup-option-changed-dice = تاس در هر مجموعه به { $count } تغییر یافت.
tossup-desc-starting-dice = انتخاب می‌کند که هر نوبت با چند تاس شروع شود و پس از سبز شدن همه‌ی تاس‌ها، چند تاس برگردد (پیش‌فرض ۱۰، محدوده ۵-۲۰).


tossup-rules-standard = کلاسیک
tossup-rules-PlayAural = بخشنده
tossup-rules-standard-desc = سه وجه سبز، دو وجه زرد و یک وجه قرمز. شکست در صورت بدون سبز با حداقل یک قرمز.
tossup-rules-PlayAural-desc = شانس برابر برای هر سه رنگ. شکست فقط زمانی که همه‌ی تاس‌های پرتاب‌شده قرمز باشند.

tossup-error-roll-not-playing = نمی‌توانید پرتاب کنید چون پرتاب و برد در حال حاضر در جریان نیست.
tossup-error-roll-no-turn = نمی‌توانید پرتاب کنید چون پرتاب و برد در حال حاضر نوبت فعالی ندارد.
tossup-error-roll-not-your-turn = نمی‌توانید در طول نوبت { $player } پرتاب کنید. منتظر بمانید تا نوبت به شما برسد.
tossup-error-bank-not-playing = نمی‌توانید ذخیره کنید چون پرتاب و برد در حال حاضر در جریان نیست.
tossup-error-bank-no-turn = نمی‌توانید ذخیره کنید چون پرتاب و برد در حال حاضر نوبت فعالی ندارد.
tossup-error-bank-not-your-turn = نمی‌توانید در طول نوبت { $player } ذخیره کنید. منتظر بمانید تا نوبت به شما برسد.
tossup-error-bank-roll-first = قبل از ذخیره، حداقل یک بار پرتاب کنید. یک پرتاب تمام زرد ممکن است برای صفر امتیاز ذخیره شود تا نوبت شما پایان یابد.
tossup-error-spectator-action = تماشاگران می‌توانند وضعیت عمومی پرتاب و برد را بررسی کنند، اما نمی‌توانند پرتاب یا ذخیره کنند.
tossup-error-status-not-playing = وضعیت نوبت در دسترس نیست چون پرتاب و برد در حال حاضر در جریان نیست.
tossup-error-status-no-turn = وضعیت نوبت در دسترس نیست چون پرتاب و برد در حال حاضر بازیکن فعالی ندارد.
tossup-error-target-out-of-range = آستانه‌ی هدف { $value } است؛ باید از { $min } تا { $max } امتیاز باشد.
tossup-error-dice-out-of-range = اندازه‌ی مجموعه‌ی تازه { $value } است؛ باید از { $min } تا { $max } تاس باشد.
tossup-error-rules-variant = مقدار قوانین "{ $variant }" پشتیبانی نمی‌شود. کلاسیک یا بخشنده را انتخاب کنید.

tossup-line-format = { $rank }. { $player }: { $points }