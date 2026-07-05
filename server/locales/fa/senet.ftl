# Senet - ترجمه‌ی فارسی

game-name-senet = سنت

# شروع بازی
senet-game-started = { $p1 } بازیکن ۱ است، { $p2 } بازیکن ۲ است. { $first } اول می‌رود.

# پرتاب چوب‌ها
senet-throw-you = شما { $result } پرتاب کردید.{ $bonus ->
    [yes] {" "}پرتاب پاداش!
   *[no] {""}
}
senet-throw-other = { $player } { $result } پرتاب کرد.{ $bonus ->
    [yes] {" "}پرتاب پاداش!
   *[no] {""}
}

# حرکت
senet-move-you = شما از خانه‌ی { $from } به خانه‌ی { $to } حرکت می‌کنید.
senet-move-other = { $player } از خانه‌ی { $from } به خانه‌ی { $to } حرکت می‌کند.
senet-swap-you = شما با { $opponent } در خانه‌ی { $to } جابه‌جا می‌شوید. { $opponent } به خانه‌ی { $from } بازمی‌گردد.
senet-swap-other = { $player } با { $opponent } در خانه‌ی { $to } جابه‌جا می‌شود. { $opponent } به خانه‌ی { $from } بازمی‌گردد.
senet-bearoff-you = شما از خانه‌ی { $from } خارج می‌شوید. { $remaining } مهره باقی‌مانده.
senet-bearoff-other = { $player } از خانه‌ی { $from } خارج می‌شود. { $remaining } مهره باقی‌مانده.
senet-water-you = شما در خانه‌ی آب فرود آمدید! مهره به خانه‌ی { $dest } فرستاده شد.
senet-water-other = { $player } در خانه‌ی آب فرود آمد! مهره به خانه‌ی { $dest } فرستاده شد.
senet-happiness-you = شما به خانه‌ی خوشبختی رسیدید.
senet-happiness-other = { $player } به خانه‌ی خوشبختی رسید.
senet-horus-auto-you = مهره‌ی شما از خانه‌ی هوروس خارج می‌شود چون ردیف اول شما خالی است. { $remaining } مهره باقی‌مانده.
senet-horus-auto-other = مهره‌ی { $player } از خانه‌ی هوروس خارج می‌شود چون ردیف اول او خالی است. { $remaining } مهره باقی‌مانده.

# بدون حرکت
senet-no-moves-you = شما هیچ حرکت قانونی ندارید.
senet-no-moves-other = { $player } هیچ حرکت قانونی ندارد.

# برچسب‌های خانه‌ها
senet-sq-empty = { $sq }
senet-sq-own = { $sq }، متعلق به شما
senet-sq-opponent = { $sq }، { $owner }
senet-sq-empty-special = { $sq }، { $name }
senet-sq-own-special = { $sq }، { $name }، متعلق به شما
senet-sq-opponent-special = { $sq }، { $name }، { $owner }

# نام خانه‌های ویژه
senet-house-rebirth = تولد دوباره
senet-house-happiness = خوشبختی
senet-house-water = آب
senet-house-three-truths = سه حقیقت
senet-house-re-atum = ره-آتوم
senet-house-horus = هوروس

# وضعیت
senet-status = { $p1 }: { $off1 } خارج شده. { $p2 }: { $off2 } خارج شده.{ $phase ->
    [throwing] {" "}در انتظار پرتاب.
   *[moving] {" "}پرتاب: { $roll }.
}
senet-sticks = { $result }
senet-sticks-none = هنوز پرتابی انجام نشده است.

# برد
senet-wins-you = شما برنده شدید! همه‌ی مهره‌های شما از آخرین خانه عبور کردند.
senet-wins-other = { $player } برنده شد! همه‌ی مهره‌های او از آخرین خانه عبور کردند.

# برچسب‌های اقدامات
senet-check-status = وضعیت
senet-check-sticks = چوب‌ها
senet-next-piece = مهره‌ی بعدی
senet-previous-piece = مهره‌ی قبلی
senet-score-line = { $player }: { $off } مهره خارج شده.

# خطاها
senet-not-your-piece = این مهره‌ی شما نیست.
senet-no-piece-there = هیچ مهره‌ای آنجا نیست.
senet-no-moves-from-here = هیچ حرکت قانونی از این خانه وجود ندارد.
senet-need-throw-first = قبل از انتخاب مهره برای حرکت، باید چوب‌ها را پرتاب کنید.
senet-no-movable-pieces = هیچ‌کدام از مهره‌های شما با پرتاب فعلی نمی‌توانند حرکت کنند.
senet-error-exactly-two-players = سنت دقیقاً به ۲ بازیکن فعال نیاز دارد. بازیکنان فعال فعلی: { $count }.

# گزینه‌ها
senet-option-bot-difficulty = دشواری ربات: { $bot_difficulty }
senet-option-select-bot-difficulty = دشواری ربات را انتخاب کنید
senet-option-changed-bot-difficulty = دشواری ربات روی { $bot_difficulty } تنظیم شد.
senet-desc-bot-difficulty = نحوه‌ی حرکت ربات‌های سنت را انتخاب می‌کند: تصادفی به‌طور ساده حرکت می‌کند، در حالی که ساده حرکت‌های تاکتیکی ایمن‌تر را ترجیح می‌دهد.
senet-difficulty-random = تصادفی
senet-difficulty-simple = ساده