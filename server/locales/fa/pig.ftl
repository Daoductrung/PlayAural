game-name-pig = خوک
pig-desc-team-mode = به‌صورت انفرادی یا در یک آرایش تیمی پشتیبانی‌شده بازی کنید. یک تیم یک امتیاز مشترک دارد و زمانی که یک عضو امتیاز کافی داشته باشد، بلافاصله برنده می‌شود.

pig-roll = پرتاب تاس
pig-hold = ذخیره‌ی { $points } امتیاز
pig-check-turn-status = بررسی وضعیت نوبت

pig-game-start =
    خوک آغاز شد. اولین { $team ->
        [yes] تیمی
       *[no] بازیکنی
    } که { $target } امتیاز را ذخیره کند برنده می‌شود. تاس { $sides } وجه دارد و پرتاب ۱ تمام امتیازات ذخیره‌نشده‌ی آن نوبت را از بین می‌برد. { $minimum ->
        [0] می‌توانید پس از هر پرتاب امتیازدهنده ذخیره کنید.
       *[other] قبل از ذخیره باید حداقل { $minimum } امتیاز نوبت جمع‌آوری کنید.
    }
pig-game-start-brief =
    خوک آغاز شد. هدف: { $target }. تاس: { $sides } وجه. حداقل ذخیره: { $minimum }.{ $team ->
        [yes] تیم‌ها امتیازات را به اشتراک می‌گذارند.
       *[no] امتیازات انفرادی.
    }
pig-round-start = دور { $round } آغاز می‌شود. هر بازیکن فعال یک نوبت خواهد داشت.
pig-round-start-brief = دور { $round }.

pig-you-roll-result = شما { $roll } انداختید. مجموع نوبت شما اکنون { $total } امتیاز است.
pig-player-roll-result = { $player } { $roll } انداخت. مجموع نوبت او اکنون { $total } امتیاز است.
pig-you-roll-result-brief = شما: { $roll }; مجموع نوبت { $total }.
pig-player-roll-result-brief = { $player }: { $roll }; مجموع نوبت { $total }.

pig-you-bust = شما ۱ انداختید و همه‌ی { $points } امتیاز ذخیره‌نشده را از دست دادید. نوبت شما بدون امتیاز به پایان می‌رسد.
pig-player-busts = { $player } ۱ انداخت و همه‌ی { $points } امتیاز ذخیره‌نشده را از دست داد. نوبت او بدون امتیاز به پایان می‌رسد.
pig-you-bust-brief = شما ۱ انداختید و { $points } امتیاز نوبت را از دست دادید.
pig-player-busts-brief = { $player } ۱ انداخت و { $points } امتیاز نوبت را از دست داد.

pig-you-hold =
    شما { $points } امتیاز ذخیره می‌کنید. { $team ->
        [yes] تیم شما اکنون { $total } امتیاز دارد.
       *[no] امتیاز کل شما اکنون { $total } است.
    }
pig-player-holds =
    { $player } { $points } امتیاز ذخیره می‌کند. { $team ->
        [yes] { $team_name } اکنون { $total } امتیاز دارد.
       *[no] امتیاز کل او اکنون { $total } است.
    }
pig-you-hold-brief =
    شما { $points } ذخیره کردید؛{ $team ->
        [yes] مجموع { $team_name } { $total }.
       *[no] مجموع شما { $total }.
    }
pig-player-holds-brief =
    { $player } { $points } ذخیره کرد؛{ $team ->
        [yes] مجموع { $team_name } { $total }.
       *[no] مجموع { $total }.
    }

pig-you-win =
    { $team ->
        [yes] تیم شما، { $winner }، با { $score } امتیاز برنده‌ی خوک شد!
       *[no] شما با { $score } امتیاز برنده‌ی خوک شدید!
    }
pig-winner =
    { $team ->
        [yes] برنده { $winner } با { $score } امتیاز است!
       *[no] برنده { $winner } با { $score } امتیاز است!
    }
pig-you-win-brief =
    { $team ->
        [yes] برنده: تیم شما، { $winner }، با { $score }.
       *[no] برنده: شما، با { $score }.
    }
pig-winner-brief = برنده: { $winner }، با { $score }.

pig-confirm-risky-roll =
    پرتاب مجدد { $points } امتیاز ذخیره‌نشده را به خطر می‌اندازد، با { $risk } درصد احتمال از دست دادن آنها. { $winning ->
        [yes] ذخیره‌ی اکنون به شما { $total } امتیاز می‌دهد و بازی را می‌برید.
       *[no] ذخیره‌ی اکنون به شما { $total } از { $target } امتیاز مورد نیاز برای بردن را می‌دهد.
    } برای تأیید، پرتاب را ظرف { $seconds } ثانیه تکرار کنید.

pig-action-resolving = تاس هنوز در حال چرخش است. منتظر نتیجه باشید.
pig-no-turn-points = قبل از ذخیره، حداقل یک بار تاس بیندازید.
pig-need-more-points = شما { $current } امتیاز نوبت دارید، اما این میز حداقل به { $required } امتیاز قبل از ذخیره نیاز دارد.

pig-desc-target-score = اولین بازیکن یا تیمی که این تعداد امتیاز کل را ذخیره کند، بلافاصله برنده می‌شود (پیش‌فرض ۱۰۰، محدوده ۱۰-۱۰۰۰).
pig-set-min-bank = حداقل ذخیره: { $points }
pig-set-dice-sides = وجه‌های تاس: { $sides }
pig-enter-min-bank = حداقل امتیاز نوبت مورد نیاز برای ذخیره را وارد کنید:
pig-enter-dice-sides = تعداد وجه‌های تاس را وارد کنید:
pig-option-changed-min-bank = حداقل ذخیره به { $points } امتیاز تغییر یافت.
pig-desc-min-bank = تعداد امتیازات نوبت مورد نیاز قبل از در دسترس شدن ذخیره. برای خوک استاندارد این را ۰ تنظیم کنید؛ باید کمتر از امتیاز هدف باشد (پیش‌فرض ۰، محدوده ۰-۹۹۹).
pig-option-changed-dice = تاس اکنون { $sides } وجه دارد.
pig-desc-dice-sides = تعداد وجه‌های تاس تکی. پرتاب ۱ همیشه مجموع نوبت را از بین می‌برد (پیش‌فرض ۶، محدوده ۴-۲۰).

pig-error-target-out-of-range = امتیاز هدف { $value } نامعتبر است. مقداری از { $min } تا { $max } انتخاب کنید.
pig-error-min-bank-out-of-range = حداقل ذخیره‌ی { $value } نامعتبر است. مقداری از { $min } تا { $max } انتخاب کنید.
pig-error-dice-sides-out-of-range = تاس { $value } وجهی پشتیبانی نمی‌شود. از { $min } تا { $max } وجه انتخاب کنید.
pig-error-min-bank-too-high = حداقل ذخیره‌ی { $minimum } باید کمتر از امتیاز هدف { $target } باشد.

pig-status-target = امتیاز هدف: { $target } امتیاز.
pig-status-round = دور فعلی: { $round }.
pig-status-current-turn = { $player } در حال بازی است: { $banked } ذخیره‌شده، { $turn } در این نوبت، { $potential } اگر اکنون ذخیره شود.
pig-status-standing = { $rank }. { $team }: { $score } امتیاز.

pig-line-format = { $rank }. { $player }: { $points }