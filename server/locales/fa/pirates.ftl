game-name-pirates = دزدان دریایی دریای گمشده

# راه‌اندازی و جریان دور
pirates-welcome = به دزدان دریایی دریای گمشده خوش آمدید. در مسیر چهل خانه‌ای حرکت کنید، جواهرات پراکنده را جمع‌آوری کنید و از خدمه‌ی رقیب پیشی بگیرید.
pirates-welcome-brief = به دزدان دریایی دریای گمشده خوش آمدید.
pirates-oceans = سفر شما از { $oceans } عبور می‌کند.
pirates-gems-placed = همه‌ی { $total } جواهر در طول مسیر پنهان شده‌اند. پس از بازیابی آخرین جواهر، بالاترین ارزش محموله برنده می‌شود.
pirates-gems-placed-brief = { $total } جواهر در طول مسیر پنهان شده‌اند.
pirates-golden-moon = ماه طلایی در دور { $round } طلوع می‌کند. هر جایزه‌ی تجربه در این دور سه برابر می‌شود.
pirates-golden-moon-brief = ماه طلایی: تجربه‌ی سه‌برابر در دور { $round }.
pirates-turn-you = نوبت شما در دور { $round }. شما در موقعیت { $position } در { $ocean } هستید.
pirates-turn-you-brief = نوبت شما. موقعیت { $position }.
pirates-turn = نوبت { $player } در دور { $round }، در موقعیت { $position } در { $ocean }.
pirates-turn-brief = نوبت { $player }.

# حرکت و اطلاعات نقشه
pirates-move-left = حرکت یک خانه به چپ
pirates-move-right = حرکت یک خانه به راست
pirates-move-2-left = حرکت دو خانه به چپ
pirates-move-2-right = حرکت دو خانه به راست
pirates-move-3-left = حرکت سه خانه به چپ
pirates-move-3-right = حرکت سه خانه به راست
pirates-move-you = شما { $tiles } { $tiles ->
    [one] خانه
   *[other] خانه
} به { $direction } به موقعیت { $position } در { $ocean } حرکت می‌کنید.
pirates-move-you-brief = شما به موقعیت { $position } حرکت می‌کنید.
pirates-move = { $player } { $tiles } { $tiles ->
    [one] خانه
   *[other] خانه
} به { $direction } به موقعیت { $position } در { $ocean } حرکت می‌کند.
pirates-move-brief = { $player } به موقعیت { $position } حرکت می‌کند.
pirates-map-edge = نمی‌توانید بیشتر در آن جهت حرکت کنید؛ موقعیت { $position } لبه‌ی مسیر است. اقدام دیگری انتخاب کنید.
pirates-dir-left = چپ
pirates-dir-right = راست
pirates-your-position = شما در موقعیت { $position }، بخش { $sector }، در { $ocean } هستید.
pirates-check-position = بررسی موقعیت
pirates-check-moon = بررسی ماه طلایی
pirates-moon-active = ماه طلایی در دور { $round } فعال است. تجربه سه برابر می‌شود. خدمه { $collected } از { $total } جواهر را بازیابی کرده‌اند و { $remaining } جواهر باقی‌مانده است.
pirates-moon-inactive = ماه طلایی در دور { $round } فعال نیست. در { $rounds } { $rounds ->
    [one] دور
   *[other] دور
} دیگر بازمی‌گردد. خدمه { $collected } از { $total } جواهر را بازیابی کرده‌اند و { $remaining } جواهر باقی‌مانده است.

# وضعیت و نتایج
pirates-check-status = بررسی وضعیت خدمه
pirates-check-status-detailed = وضعیت دقیق خدمه
pirates-status-line = { $player }: سطح { $level}; { $xp } تجربه‌ی کل، { $progress } از { $needed } تجربه تا سطح بعدی؛ { $points }; { $gem_count } { $gem_count ->
    [one] جواهر
   *[other] جواهر
}{ $detail ->
    [yes] ; موقعیت { $position } در { $ocean }; محموله: { $gems }; اثرات فعال: { $skills }
   *[no] { "" }
}.
pirates-end-score-line = { $rank }. { $player}: { $points }، سطح { $level }
pirates-all-gems-collected = آخرین جواهر بازیابی شد. خدمه محموله‌های خود را مقایسه می‌کنند.
pirates-all-gems-collected-brief = آخرین جواهر بازیابی شد.
pirates-you-win = شما با { $score } امتیاز برنده شدید.
pirates-you-win-brief = شما برنده شدید: { $score } امتیاز.
pirates-winner = { $player } با { $score } امتیاز برنده شد.
pirates-winner-brief = { $player } برنده شد: { $score } امتیاز.
pirates-you-tie = شما با { $players } با { $score } امتیاز در رتبه‌ی اول مساوی می‌شوید.
pirates-you-tie-brief = شما با { $score } امتیاز در رتبه‌ی اول مساوی شدید.
pirates-players-tie = { $players } با { $score } امتیاز در رتبه‌ی اول مساوی می‌شوند.
pirates-players-tie-brief = { $players } با { $score } مساوی شدند.

# جواهرات و تجربه
pirates-gem-found-you = شما { $gem } را بازیابی می‌کنید که { $value } { $value ->
    [one] امتیاز
   *[other] امتیاز
} ارزش دارد. محموله‌ی شما اکنون { $score } امتیاز ارزش دارد؛ { $remaining } جواهر در دریا باقی‌مانده است.
pirates-gem-found-you-brief = شما { $gem } را بازیابی می‌کنید. امتیاز: { $score }.
pirates-gem-found = { $player } { $gem } را بازیابی می‌کند که { $value } { $value ->
    [one] امتیاز
   *[other] امتیاز
} ارزش دارد. محموله‌ی او اکنون { $score } امتیاز ارزش دارد؛ { $remaining } جواهر در دریا باقی‌مانده است.
pirates-gem-found-brief = { $player } { $gem } را بازیابی می‌کند.
pirates-xp-gained-you = شما { $xp } تجربه برای { $reason ->
    [gem] بازیابی جواهر
    [attack] اصابت توپ
    [defense] دفع حمله‌ی توپ
   *[other] تکمیل اقدام
} به دست می‌آورید. اکنون { $total } تجربه‌ی کل دارید.
pirates-xp-gained-you-brief = شما { $xp } تجربه به دست آوردید. کل: { $total }.
pirates-xp-gained-player = { $player } { $xp } تجربه برای { $reason ->
    [gem] بازیابی جواهر
    [attack] اصابت توپ
    [defense] دفع حمله‌ی توپ
   *[other] تکمیل اقدام
} به دست می‌آورد و به { $total } تجربه‌ی کل می‌رسد.
pirates-xp-gained-player-brief = { $player } { $xp } تجربه به دست آورد.
pirates-level-up-you = شما به سطح { $level } رسیدید.
pirates-level-up-you-brief = شما به سطح { $level } رسیدید.
pirates-level-up = { $player } به سطح { $level } رسید.
pirates-level-up-brief = { $player } به سطح { $level } رسید.
pirates-level-up-multiple-you = شما { $levels } سطح ارتقا یافتید و به سطح { $level } رسیدید.
pirates-level-up-multiple-you-brief = شما به سطح { $level } رسیدید.
pirates-level-up-multiple = { $player } { $levels } سطح ارتقا یافت و به سطح { $level } رسید.
pirates-level-up-multiple-brief = { $player } به سطح { $level } رسید.
pirates-skills-unlocked-you = در سطح { $level }، { $skills } را باز می‌کنید.
pirates-skills-unlocked-you-brief = شما { $skills } را باز کردید.
pirates-skills-unlocked = در سطح { $level }، { $player } { $skills } را باز می‌کند.
pirates-skills-unlocked-brief = { $player } { $skills } را باز کرد.

# نبرد توپ
pirates-cannonball = شلیک توپ
pirates-select-cannon-target = یک کشتی در برد توپ انتخاب کنید
pirates-target-option = { $player }، { $distance } { $distance ->
    [one] خانه
   *[other] خانه
} دورتر، { $score } امتیاز، با { $gems } { $gems ->
    [one] جواهر
   *[other] جواهر
}
pirates-target-unavailable = کشتی در دسترس نیست
pirates-no-targets = هیچ کشتی رقیبی در برد توپ فعلی شما با { $range } خانه نیست. حرکت یا مهارت در دسترس دیگری را انتخاب کنید.
pirates-target-out-of-range = { $target } دیگر در برد { $range } خانه‌ی توپ شما از موقعیت { $position } نیست. اقدام دیگری انتخاب کنید.
pirates-attack-you-fire = شما یک توپ به سمت { $target } شلیک می‌کنید.
pirates-attack-you-fire-brief = شما به سمت { $target } شلیک می‌کنید.
pirates-attack-incoming = { $attacker } یک توپ به سمت شما شلیک می‌کند.
pirates-attack-incoming-brief = { $attacker } به سمت شما شلیک می‌کند.
pirates-attack-fired = { $attacker } یک توپ به سمت { $defender } شلیک می‌کند.
pirates-attack-fired-brief = { $attacker } به سمت { $defender } شلیک می‌کند.
pirates-combat-rolls-you = تاس حمله‌ی شما { $attack_die}، به اضافه‌ی { $attack_bonus}، مجموعاً { $attack_total} است. تاس دفاع { $defender } { $defense_die}، به اضافه‌ی { $defense_bonus}، مجموعاً { $defense_total} است.
pirates-combat-rolls-you-brief = حمله { $attack_total}; دفاع { $defense_total}.
pirates-combat-rolls-defender = { $attacker } با { $attack_die} حمله می‌کند، به اضافه‌ی { $attack_bonus}، مجموعاً { $attack_total}. تاس دفاع شما { $defense_die}، به اضافه‌ی { $defense_bonus}، مجموعاً { $defense_total} است.
pirates-combat-rolls-defender-brief = حمله { $attack_total}; دفاع شما { $defense_total}.
pirates-combat-rolls-observer = { $attacker } با { $attack_die} حمله می‌کند، به اضافه‌ی { $attack_bonus}، مجموعاً { $attack_total}. { $defender } با { $defense_die} دفاع می‌کند، به اضافه‌ی { $defense_bonus}، مجموعاً { $defense_total}.
pirates-combat-rolls-observer-brief = { $attacker } { $attack_total}; { $defender } { $defense_total}.
pirates-attack-hit-you = اصابت مستقیم. { $attack_total } شما از { $defense_total } { $target } بیشتر است؛ یک اقدام یورش موجود را انتخاب کنید.
pirates-attack-hit-you-brief = شما به { $target } اصابت کردید، { $attack_total } به { $defense_total }.
pirates-attack-hit-them = { $attacker } به شما اصابت می‌کند، { $attack_total } به { $defense_total}، و اکنون می‌تواند به کشتی شما یورش ببرد.
pirates-attack-hit-them-brief = { $attacker } به شما اصابت کرد، { $attack_total } به { $defense_total}.
pirates-attack-hit = { $attacker } به { $defender } اصابت می‌کند، { $attack_total } به { $defense_total}، و می‌تواند یورش ببرد.
pirates-attack-hit-brief = { $attacker } به { $defender } اصابت کرد.
pirates-attack-hit-no-boarding-you = اصابت مستقیم. { $attack_total } شما از { $defense_total } { $target } بیشتر است. این اصابت کشتی جنگی تجربه می‌دهد اما اقدام یورشی ندارد.
pirates-attack-hit-no-boarding-you-brief = شما به { $target } اصابت کردید، { $attack_total } به { $defense_total}; بدون یورش.
pirates-attack-hit-no-boarding-them = { $attacker } به شما اصابت می‌کند، { $attack_total } به { $defense_total}. اصابت‌های کشتی جنگی اقدام یورشی نمی‌دهند.
pirates-attack-hit-no-boarding-them-brief = { $attacker } به شما اصابت کرد؛ بدون یورش.
pirates-attack-hit-no-boarding = { $attacker } به { $defender } اصابت می‌کند، { $attack_total } به { $defense_total}. این اصابت کشتی جنگی اقدام یورشی ندارد.
pirates-attack-hit-no-boarding-brief = { $attacker } به { $defender} اصابت کرد؛ بدون یورش.
pirates-attack-miss-you = مجموع حمله‌ی شما { $attack_total } از مجموع دفاع { $target } یعنی { $defense_total } بیشتر نمی‌شود. نوبت شما پایان می‌یابد.
pirates-attack-miss-you-brief = شما به { $target } نخوردید، { $attack_total } به { $defense_total}.
pirates-attack-miss-them = شما { $attacker } را با مجموع دفاع { $defense_total } در برابر { $attack_total } دفع می‌کنید.
pirates-attack-miss-them-brief = شما { $attacker } را دفع کردید، { $defense_total } به { $attack_total}.
pirates-attack-miss = { $defender } { $attacker } را دفع می‌کند، { $defense_total } به { $attack_total}.
pirates-attack-miss-brief = { $attacker } به { $defender } نخورد.

# یورش
pirates-resolve-boarding = اجرای یورش
pirates-select-boarding-action = اصابت توپ. نحوه‌ی اجرای اقدام یورش را انتخاب کنید
pirates-boarding-steal = تلاش برای دزدیدن جواهر
pirates-boarding-push-left = کوبیدن مدافع به چپ
pirates-boarding-push-right = کوبیدن مدافع به راست
pirates-boarding-option-unknown = اقدام یورش ناشناس
pirates-must-resolve-boarding = قبل از انجام اقدام نوبتی دیگر، اقدام یورش در انتظار خود را اجرا کنید.
pirates-no-pending-boarding = هیچ اقدام یورش در انتظاری برای شما وجود ندارد.
pirates-boarding-stale = اقدام یورش در انتظار دیگر مدافع معتبری ندارد، بنابراین لغو شد. اقدام نوبتی دیگری انتخاب کنید.
pirates-boarding-option-unavailable = { $action } دیگر در برابر { $defender } در دسترس نیست. یکی از گزینه‌های یورش فعلی را انتخاب کنید.
pirates-push-you = شما { $target } را از موقعیت { $old_pos } به { $new_pos }، { $distance } خانه به { $direction } می‌کوبید. پاداش Push شما { $bonus } خانه‌ی اضافی کمک کرد.
pirates-push-you-brief = شما { $target } را به موقعیت { $position } کوبیدید.
pirates-push-them = { $attacker } شما را از موقعیت { $old_pos } به { $new_pos }، { $distance } خانه به { $direction } می‌کوبد.
pirates-push-them-brief = { $attacker } شما را به موقعیت { $position } کوبید.
pirates-push = { $attacker } { $defender } را از موقعیت { $old_pos } به { $new_pos }، به فاصله‌ی { $distance } خانه به { $direction } می‌کوبد.
pirates-push-brief = { $attacker } { $defender } را به موقعیت { $position } کوبید.
pirates-steal-rolls-you = مجموع دزدی شما { $steal} است؛ مجموع نگهبانی { $target } { $defend} است.
pirates-steal-rolls-you-brief = دزدی { $steal}; نگهبانی { $defend}.
pirates-steal-rolls-defender = مجموع دزدی { $attacker } { $steal} است؛ مجموع نگهبانی شما { $defend} است.
pirates-steal-rolls-defender-brief = دزدی { $steal}; نگهبانی شما { $defend}.
pirates-steal-rolls-observer = { $attacker } تلاش می‌کند از { $defender } بدزدد: دزدی { $steal}، نگهبانی { $defend}.
pirates-steal-rolls-observer-brief = { $attacker } با { $steal } از { $defender } با { $defend } می‌دزدد.
pirates-steal-success-you = شما { $gem } را از { $target } می‌دزدید. محموله‌ی شما { $attacker_score } امتیاز ارزش دارد؛ محموله‌ی آنها { $defender_score } امتیاز ارزش دارد.
pirates-steal-success-you-brief = شما { $gem } را از { $target } دزدیدید.
pirates-steal-success-them = { $attacker } { $gem } شما را می‌دزدد. محموله‌ی آنها { $attacker_score } امتیاز ارزش دارد؛ محموله‌ی شما { $defender_score } امتیاز ارزش دارد.
pirates-steal-success-them-brief = { $attacker } { $gem } شما را دزدید.
pirates-steal-success = { $attacker } { $gem } را از { $defender } می‌دزدد. ارزش محموله‌های آنها اکنون به ترتیب { $attacker_score } و { $defender_score } امتیاز است.
pirates-steal-success-brief = { $attacker } { $gem } را از { $defender } دزدید.
pirates-steal-failed-you = مجموع دزدی شما { $steal } از مجموع نگهبانی { $target } یعنی { $defend} بیشتر نمی‌شود. چیزی نمی‌دزدید.
pirates-steal-failed-you-brief = دزدی شما ناموفق بود، { $steal } به { $defend}.
pirates-steal-failed-defender = شما دزدی { $attacker } را متوقف می‌کنید، { $defend } به { $steal}، و محموله‌ی خود را حفظ می‌کنید.
pirates-steal-failed-defender-brief = شما دزدی { $attacker } را متوقف کردید.
pirates-steal-failed = { $defender } دزدی { $attacker } را متوقف می‌کند، { $defend } به { $steal}.
pirates-steal-failed-brief = { $attacker } نتوانست از { $defender } بدزدد.
pirates-steal-no-gems-you = نمی‌توانید از { $target } بدزدید چون دیگر جواهری حمل نمی‌کند. به جای آن کوبیدن را انتخاب کنید.
pirates-steal-no-gems-you-brief = { $target } جواهری برای دزدیدن ندارد.
pirates-steal-no-gems-defender = { $attacker } نمی‌تواند از شما بدزدد چون محموله‌ی شما جواهری ندارد.
pirates-steal-no-gems-defender-brief = شما جواهری برای دزدیدن { $attacker } ندارید.
pirates-steal-no-gems = { $attacker } نمی‌تواند از { $defender } بدزدد چون مدافع جواهری حمل نمی‌کند.
pirates-steal-no-gems-brief = { $defender } جواهری برای دزدیدن ندارد.

# مهارت‌ها و وضعیت مهارت
pirates-use-skill = استفاده از مهارت
pirates-select-skill = یک مهارت بازشده انتخاب کنید
pirates-unknown-skill = مهارت ناشناس
pirates-skill-error = { $message }
pirates-skill-selection-stale = آن انتخاب مهارت دیگر در سطح فعلی یا وضعیت بازی شما در دسترس نیست. منوی مهارت را دوباره باز کنید و یک مهارت موجود انتخاب کنید.
pirates-req-level = { $skill } به سطح { $required} نیاز دارد؛ شما سطح { $current} هستید.
pirates-requires-level = { $action ->
    [move_2] حرکت دو خانه
    [move_3] حرکت سه خانه
   *[other] آن اقدام
} به سطح { $required} نیاز دارد؛ شما سطح { $current} هستید.
pirates-skill-cooldown = { $name } برای { $turns } نوبت دیگر از نوبت‌های شما در حال بازیابی است.
pirates-skill-active = { $name } برای { $turns } نوبت دیگر از نوبت‌های شما فعال است.
pirates-skill-already-activated-this-turn = شما قبلاً یک تقویت جنگی در این نوبت فعال کرده‌اید. اقدام حرکت یا توپ بعدی را انجام دهید.
pirates-skill-no-uses = جوینده‌ی جواهر هیچ استفاده‌ی باقی‌مانده‌ای در این بازی ندارد.
pirates-skill-no-gems = جوینده‌ی جواهر نمی‌تواند هدفی پیدا کند چون هیچ جواهر جمع‌آوری‌نشده‌ای باقی نمانده است.
pirates-skill-no-targets = هیچ کشتی رقیبی در برد { $range } خانه‌ی فعلی برای این مهارت نیست.
pirates-skill-incompatible = { $skill } نمی‌تواند در حالی که { $active } فعال است فعال شود. منتظر پایان اثر فعلی باشید.
pirates-battleship-after-buff = کشتی جنگی پس از فعال‌سازی تقویت جنگی در این نوبت قابل پرتاب نیست. از تقویت با شلیک توپ معمولی استفاده کنید، یا تا نوبت بعدی صبر کنید.
pirates-menu-active = { $name } (فعال برای { $turns } نوبت دیگر)
pirates-menu-cooldown = { $name } (در حال بازیابی برای { $turns } نوبت دیگر)
pirates-menu-activate = فعال‌سازی { $name }
pirates-menu-gem-seeker = { $name } ({ $uses } استفاده باقی‌مانده)
pirates-active-skill-status = { $skill }، { $turns } نوبت باقی‌مانده
pirates-no-active-skills = هیچ
pirates-skill-activated = { $player } { $skill} را فعال می‌کند. { $effect }
pirates-skill-activated-brief = { $player } { $skill} را فعال می‌کند.
pirates-buff-expired-you = اثر { $skill } شما قبل از شروع این نوبت منقضی می‌شود.
pirates-buff-expired-you-brief = { $skill } شما منقضی شد.
pirates-buff-expired = اثر { $skill } { $player } قبل از شروع نوبت او منقضی می‌شود.
pirates-buff-expired-brief = { $skill } { $player } منقضی شد.

pirates-skill-instinct-name = غریزه‌ی ملوان
pirates-skill-instinct-desc = هر بخش پنج خانه‌ای را بررسی کنید، از جمله جواهرات جمع‌آوری‌نشده و کشتی‌های رقیب. این اقدام اطلاعاتی نوبت را پایان نمی‌دهد.
pirates-instinct-header = نمودار غریزه‌ی ملوان، تقسیم‌شده به هشت بخش:
pirates-instinct-sector = بخش { $sector}، موقعیت‌های { $start } تا { $end }: { $gems } { $gems ->
    [one] جواهر جمع‌آوری‌نشده
   *[other] جواهر جمع‌آوری‌نشده
}، { $players } کشتی رقیب

pirates-skill-portal-name = پورتال
pirates-skill-portal-desc = یک اقیانوس متفاوت با حضور رقیب را انتخاب کنید، یا Random را برای تله‌پورت به هر نقطه‌ای از نقشه انتخاب کنید. زمان بازیابی: ۳ نوبت از نوبت‌های شما.
pirates-resolve-portal = انتخاب مقصد پورتال
pirates-select-portal-ocean = یک اقیانوس متفاوت با حضور رقیب را انتخاب کنید، یا Random را برای هر نقطه‌ای از نقشه انتخاب کنید
pirates-portal-option = { $ocean }; کشتی‌ها: { $ships}; { $gems } { $gems ->
    [one] جواهر جمع‌آوری‌نشده
   *[other] جواهر جمع‌آوری‌نشده
}
pirates-portal-option-random = نقطه‌ی تصادفی نقشه
pirates-portal-option-unavailable = آن اقیانوس مقصد پورتال معتبری نیست چون اقیانوس فعلی شماست یا هیچ کشتی رقیبی در آن حضور ندارد. مقصد دیگری انتخاب کنید.
pirates-must-resolve-portal = چون از پورتال استفاده کردید، نوبت شما به آن مهارت قفل شده است. برای تکمیل پورتال و پایان نوبت، یک مقصد انتخاب کنید یا Random را انتخاب کنید.
pirates-no-pending-portal = هیچ مقصد پورتال در انتظاری برای شما وجود ندارد.
pirates-portal-no-ships = هیچ مقصد پورتال اقیانوس رقیب خاصی در دسترس نیست، اما Random همچنان می‌تواند شما را به هر نقطه‌ای از نقشه بفرستد.
pirates-portal-fizzle-you = مقصد پورتال شما دیگر معتبر نیست. Random را انتخاب کنید تا به هر نقطه‌ای از نقشه تله‌پورت کنید، یا مقصد معتبر دیگری انتخاب کنید.
pirates-portal-fizzle-you-brief = Random یا مقصد پورتال معتبر دیگری انتخاب کنید.
pirates-portal-fizzle = مقصد پورتال { $player } دیگر معتبر نیست.
pirates-portal-fizzle-brief = { $player } باید مقصد پورتال دیگری انتخاب کند.
pirates-portal-success-you = شما از طریق پورتال به { $ocean} سفر می‌کنید و به موقعیت { $position} می‌رسید. پورتال برای ۳ نوبت از نوبت‌های شما وارد زمان بازیابی می‌شود.
pirates-portal-success-you-brief = شما به موقعیت { $position } در { $ocean} پورتال می‌زنید.
pirates-portal-success = { $player } از طریق یک پورتال به { $ocean} سفر می‌کند و به موقعیت { $position} می‌رسد.
pirates-portal-success-brief = { $player } به موقعیت { $position} پورتال می‌زند.

pirates-skill-seeker-name = جوینده‌ی جواهر
pirates-skill-seeker-desc = موقعیت دقیق یک جواهر جمع‌آوری‌نشده را آشکار می‌کند. سه بار استفاده در هر بازی؛ استفاده از آن نوبت را پایان نمی‌دهد.
pirates-gem-seeker-reveal = جوینده‌ی جواهر { $gem } را در موقعیت { $position} پیدا می‌کند. { $uses } استفاده‌ی باقی‌مانده در این بازی دارید.

pirates-skill-sword-name = شمشیرزن
pirates-skill-sword-desc = به مدت ۳ نوبت از نوبت‌های خود، +۲ حمله به دست آورید. زمان بازیابی: ۶ نوبت. نمی‌تواند با کاپیتان ماهر همپوشانی داشته باشد.
pirates-sword-fighter-activated = شما شمشیرزن را فعال می‌کنید: +{ $bonus } حمله برای { $turns } نوبت از نوبت‌های شما. زمان بازیابی: { $cooldown } نوبت. همچنان می‌توانید در این نوبت حرکت یا شلیک کنید.
pirates-sword-fighter-activated-brief = شمشیرزن فعال: +{ $bonus } حمله.

pirates-skill-push-name = سرعت کوبیدن
pirates-skill-push-desc = به مدت ۳ نوبت از نوبت‌های خود، ۲ خانه به کوبیدن‌های یورش اضافه کنید. زمان بازیابی: ۶ نوبت.
pirates-push-activated = شما سرعت کوبیدن را فعال می‌کنید: +{ $bonus } خانه به کوبیدن‌های یورش برای { $turns } نوبت از نوبت‌های شما. زمان بازیابی: { $cooldown } نوبت. همچنان می‌توانید در این نوبت حرکت یا شلیک کنید.
pirates-push-activated-brief = سرعت کوبیدن فعال: +{ $bonus } فاصله‌ی کوبیدن.

pirates-skill-captain-name = کاپیتان ماهر
pirates-skill-captain-desc = به مدت ۴ نوبت از نوبت‌های خود، +۱ حمله و +۱ دفاع به دست آورید. زمان بازیابی: ۷ نوبت. نمی‌تواند با شمشیرزن همپوشانی داشته باشد.
pirates-skilled-captain-activated = شما کاپیتان ماهر را فعال می‌کنید: +{ $attack } حمله و +{ $defense } دفاع برای { $turns } نوبت از نوبت‌های شما. زمان بازیابی: { $cooldown } نوبت. همچنان می‌توانید در این نوبت حرکت یا شلیک کنید.
pirates-skilled-captain-activated-brief = کاپیتان ماهر فعال: +{ $attack } حمله، +{ $defense } دفاع.

pirates-skill-battleship-name = کشتی جنگی
pirates-skill-battleship-desc = دو شلیک توپ هدف‌گیرنده‌ی خدمه، بدون پاداش یورش شلیک کنید. این نوبت را پایان می‌دهد. زمان بازیابی: ۴ نوبت.
pirates-battleship-activated = شما کشتی جنگی را برای { $shots } شلیک توپ پرتاب می‌کنید. خدمه‌ی شما با ارزش‌ترین هدف در برد را برای هر شلیک انتخاب می‌کند؛ اصابت‌ها یورش نمی‌دهند. زمان بازیابی: { $cooldown } نوبت.
pirates-battleship-activated-brief = شما کشتی جنگی را برای { $shots } شلیک پرتاب کردید.
pirates-battleship-activated-player = { $player } کشتی جنگی را برای { $shots } شلیک توپ پرتاب می‌کند. اصابت‌های این شلیک‌ها یورش نمی‌دهند.
pirates-battleship-activated-player-brief = { $player } کشتی جنگی را پرتاب کرد.
pirates-battleship-shot = خدمه‌ی شما شلیک کشتی جنگی { $shot } را به سمت { $target} شلیک می‌کند.
pirates-battleship-shot-brief = شلیک { $shot } به سمت { $target}.
pirates-battleship-shot-player = خدمه‌ی { $player } شلیک کشتی جنگی { $shot } را به سمت { $target} شلیک می‌کند.
pirates-battleship-shot-player-brief = { $player } به سمت { $target} شلیک می‌کند.
pirates-battleship-no-targets = خدمه‌ی شما نمی‌تواند شلیک { $shot } را شلیک کند چون هیچ رقیبی در { $range } خانه باقی نمانده است. کشتی جنگی پایان می‌یابد.
pirates-battleship-no-targets-brief = هدفی برای شلیک { $shot} وجود ندارد.
pirates-battleship-no-targets-player = { $player } نمی‌تواند شلیک کشتی جنگی { $shot } را شلیک کند چون هیچ رقیبی در { $range } خانه باقی نمانده است.
pirates-battleship-no-targets-player-brief = { $player } هدفی برای شلیک { $shot} ندارد.

pirates-skill-devastation-name = ویرانی دوگانه
pirates-skill-devastation-desc = به مدت ۳ نوبت از نوبت‌های خود، برد توپ معمولی را از ۵ به ۱۰ خانه افزایش دهید. زمان بازیابی: ۱۰ نوبت. با کشتی جنگی ناسازگار است.
pirates-double-devastation-activated = شما ویرانی دوگانه را فعال می‌کنید: برد توپ برای { $turns } نوبت از نوبت‌های شما به { $range } خانه تبدیل می‌شود. زمان بازیابی: { $cooldown } نوبت. همچنان می‌توانید در این نوبت حرکت یا شلیک کنید.
pirates-double-devastation-activated-brief = ویرانی دوگانه فعال: برد { $range}.

# گزینه‌ها و اعتبارسنجی
pirates-set-combat-xp-multiplier = ضریب تجربه‌ی جنگی: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = ضریب تجربه‌ی جنگی را از ۰.۱ تا ۳.۰ وارد کنید
pirates-option-changed-combat-xp = ضریب تجربه‌ی جنگی روی { $combat_multiplier} تنظیم شد.
pirates-desc-combat-xp-multiplier = تجربه‌ی حاصل از اصابت توپ و دفاع‌های موفق را مقیاس‌بندی می‌کند. ضریب ماه طلایی به‌طور جداگانه اعمال می‌شود (پیش‌فرض ۱.۰، محدوده ۰.۱-۳.۰).
pirates-set-find-gem-xp-multiplier = ضریب تجربه‌ی بازیابی جواهر: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = ضریب تجربه‌ی بازیابی جواهر را از ۰.۱ تا ۳.۰ وارد کنید
pirates-option-changed-find-gem-xp = ضریب تجربه‌ی بازیابی جواهر روی { $find_gem_multiplier} تنظیم شد.
pirates-desc-find-gem-xp-multiplier = تجربه‌ی اعطاشده زمانی که کشتی جواهری را بازیابی می‌کند، از جمله پس از حرکت اجباری، را مقیاس‌بندی می‌کند (پیش‌فرض ۱.۰، محدوده ۰.۱-۳.۰).
pirates-set-gem-stealing = دزدی جواهر: { $mode }
pirates-select-gem-stealing = نحوه‌ی استفاده‌ی پرتاب‌های یورش از پاداش‌های جنگی را انتخاب کنید
pirates-option-changed-stealing = دزدی جواهر روی { $mode} تنظیم شد.
pirates-desc-gem-stealing = کنترل می‌کند که آیا دزدی جواهر پس از اصابت مستقیم در دسترس است و آیا پاداش‌های حمله و دفاع فعال پرتاب دزدی را اصلاح می‌کنند یا نه.
pirates-stealing-with-bonus = فعال با پاداش‌های جنگی
pirates-stealing-no-bonus = فعال بدون پاداش‌های جنگی
pirates-stealing-disabled = غیرفعال؛ یورش فقط می‌تواند کوبیدن کند
pirates-error-combat-xp-range = ضریب تجربه‌ی جنگی { $value} است که خارج از محدوده‌ی پشتیبانی‌شده‌ی { $min } تا { $max} است. قبل از شروع آن را در آن محدوده تنظیم کنید.
pirates-error-gem-xp-range = ضریب تجربه‌ی بازیابی جواهر { $value} است که خارج از محدوده‌ی پشتیبانی‌شده‌ی { $min } تا { $max} است. قبل از شروع آن را در آن محدوده تنظیم کنید.
pirates-error-stealing-mode = حالت دزدی جواهر ذخیره‌شده، { $mode}، پشتیبانی نمی‌شود. قبل از شروع یکی از حالت‌های دزدی جواهر لیست‌شده را انتخاب کنید.

# نام اقیانوس‌ها
pirates-ocean-rory = اقیانوس روری
pirates-ocean-dev = ژرفای توسعه‌دهنده
pirates-ocean-par = دریای بهشت برنامه‌نویسان
pirates-ocean-pal = آب‌های کاخ
pirates-ocean-sil = تنگه‌ی سیلوا
pirates-ocean-kai = جریان کای
pirates-ocean-gam = خلیج گیمرها
pirates-ocean-ser = دریای اتاق سرور
pirates-ocean-bat = خلیج نبرد
pirates-ocean-cod = کانال کامپایل کد
pirates-ocean-unknown = اقیانوس ناشناس

# نام جواهرات
pirates-gem-0 = عقیق
pirates-gem-1 = یاقوت
pirates-gem-2 = گارنت
pirates-gem-3 = الماس
pirates-gem-4 = یاقوت کبود
pirates-gem-5 = زمرد
pirates-gem-6 = جواهر کاخ
pirates-gem-7 = جواهر پلاستیکی بزرگ
pirates-gem-8 = سنگ لعنتی آبی عالی
pirates-gem-9 = آمیتیست
pirates-gem-10 = حلقه‌ی طلایی
pirates-gem-11 = سنگ پالپ قرمز عالی
pirates-gem-12 = سنگ گور قرمز عالی
pirates-gem-13 = سنگ ماه
pirates-gem-14 = لاجورد
pirates-gem-15 = کهربا
pirates-gem-16 = سیترین
pirates-gem-17 = مروارید سیاه قطعاً نفرین‌شده (ثبت‌شده)
pirates-gem-unknown = جواهر ناشناس
pirates-gem-none = بدون جواهر