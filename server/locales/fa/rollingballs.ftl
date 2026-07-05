# Rolling Balls

game-name-rollingballs = توپ‌های غلتان

# اقدامات
rb-take = برداشتن { $count } { $count ->
    [one] توپ
   *[other] توپ
}
rb-reshuffle-action = به هم زدن جلوی لوله ({ $remaining } استفاده باقی‌مانده)
rb-view-pipe-action = پیش‌نمایش لوله ({ $remaining } استفاده باقی‌مانده)
rb-check-pipe-status = بررسی وضعیت لوله
rb-key-reshuffle-pipe = به هم زدن جلوی لوله
rb-key-view-pipe = پیش‌نمایش لوله

# برداشتن و آشکارسازی توپ‌ها
rb-you-take = شما متعهد به برداشتن { $count } { $count ->
    [one] توپ
   *[other] توپ
} از جلوی لوله‌ی { $remaining } توپی هستید.
rb-player-takes = { $player } متعهد به برداشتن { $count } { $count ->
    [one] توپ
   *[other] توپ
} از جلوی لوله‌ی { $remaining } توپی است.
rb-you-take-brief = شما { $count } { $count ->
    [one] توپ
   *[other] توپ
} برداشتید.
rb-player-takes-brief = { $player } { $count } { $count ->
    [one] توپ
   *[other] توپ
} برداشت.
rb-you-forced-take = فقط { $count } { $count ->
    [one] توپ باقی‌مانده
   *[other] توپ باقی‌مانده
}، کمتر از حداقل برداشت { $minimum }، بنابراین باید بقیه را بردارید.
rb-player-forced-takes = فقط { $count } { $count ->
    [one] توپ باقی‌مانده
   *[other] توپ باقی‌مانده
}، کمتر از حداقل برداشت { $minimum }، بنابراین { $player } باید بقیه را بردارد.
rb-you-forced-take-brief = شما باید { $count } { $count ->
    [one] توپ نهایی
   *[other] توپ نهایی
} را بردارید.
rb-player-forced-takes-brief = { $player } باید { $count } { $count ->
    [one] توپ نهایی
   *[other] توپ نهایی
} را بردارد.

rb-your-ball-plus = توپ { $num } شما: { $description }. به علاوه‌ی { $value } { $value ->
    [one] امتیاز
   *[other] امتیاز
}.
rb-player-ball-plus = توپ { $num } { $player }: { $description }. به علاوه‌ی { $value } { $value ->
    [one] امتیاز
   *[other] امتیاز
}.
rb-your-ball-minus = توپ { $num } شما: { $description }. منهای { $value } { $value ->
    [one] امتیاز
   *[other] امتیاز
}.
rb-player-ball-minus = توپ { $num } { $player }: { $description }. منهای { $value } { $value ->
    [one] امتیاز
   *[other] امتیاز
}.
rb-your-ball-zero = توپ { $num } شما: { $description }. بدون تغییر امتیاز.
rb-player-ball-zero = توپ { $num } { $player }: { $description }. بدون تغییر امتیاز.

rb-your-draw-summary = برداشت { $count } توپی شما دارای ارزش خالص { $delta } امتیاز است. امتیاز شما اکنون { $score } است، با { $remaining } توپ باقی‌مانده در لوله.
rb-player-draw-summary = برداشت { $count } توپی { $player } دارای ارزش خالص { $delta } امتیاز است. امتیاز { $player } اکنون { $score } است، با { $remaining } توپ باقی‌مانده در لوله.
rb-your-draw-summary-brief = خالص { $delta }; امتیاز شما { $score } است. { $remaining } توپ باقی‌مانده.
rb-player-draw-summary-brief = { $player }: خالص { $delta }، امتیاز { $score }. { $remaining } توپ باقی‌مانده.
rb-your-score-legacy = امتیاز شما اکنون { $score } است، با { $remaining } توپ باقی‌مانده در لوله.
rb-player-score-legacy = امتیاز { $player } اکنون { $score } است، با { $remaining } توپ باقی‌مانده در لوله.

# به هم زدن
rb-you-reshuffle = شما { $count } توپ اول را به هم می‌زنید. { $penalty ->
    [0] هیچ جریمه‌ای وجود ندارد
   *[other] شما یک جریمه‌ی { $penalty } امتیازی پرداخت می‌کنید
}; امتیاز شما اکنون { $score } است و { $remaining } به هم زدن باقی‌مانده دارید.
rb-player-reshuffles = { $player } { $count } توپ اول را به هم می‌زند. { $penalty ->
    [0] هیچ جریمه‌ای وجود ندارد
   *[other] { $player } یک جریمه‌ی { $penalty } امتیازی پرداخت می‌کند
}; امتیاز او اکنون { $score } است و { $remaining } به هم زدن باقی‌مانده دارد.
rb-you-reshuffle-brief = شما { $count } توپ را به هم زدید؛ جریمه { $penalty }، امتیاز { $score }، { $remaining } استفاده باقی‌مانده.
rb-player-reshuffles-brief = { $player } { $count } توپ را به هم زد؛ جریمه { $penalty }، امتیاز { $score }، { $remaining } استفاده باقی‌مانده.

# پیش‌نمایش و وضعیت لوله
rb-view-pipe-header = نمایش { $shown } توپ بعدی از { $total }. شما { $remaining } پیش‌نمایش جدید باقی‌مانده دارید.
rb-view-pipe-ball = { $num }: { $description }. ارزش: { $value } امتیاز.
rb-status-pipe = دور { $round }. { $count } توپ در لوله باقی‌مانده.
rb-status-take-range = هر نوبت معمولی بین { $min } و { $max } توپ نیاز دارد.
rb-status-turn = نوبت فعلی: { $player }.
rb-status-resources = شما { $views } پیش‌نمایش جدید لوله و { $reshuffles } به هم زدن باقی‌مانده دارید.

# شروع و جریان دور
rb-pipe-filled = لوله با { $count } توپ منحصربه‌فرد از: { $packs } پر شده است.
rb-round-start = دور { $round } با { $count } توپ باقی‌مانده در لوله آغاز می‌شود.
rb-round-start-brief = دور { $round }; { $count } توپ باقی‌مانده.

# پایان بازی
rb-pipe-empty = لوله خالی است.
rb-winner = { $player } با { $score } امتیاز برنده شد.
rb-you-win = شما با { $score } امتیاز برنده شدید.
rb-you-tie = شما برد را با { $players } تقسیم می‌کنید؛ هر کدام از شما با { $score } امتیاز به پایان رسیدید.
rb-tie = { $players } برد را با { $score } امتیاز تقسیم می‌کنند.
rb-line-format = { $rank }. { $player }: { $points }

# گزینه‌ها
rb-set-min-take = حداقل توپ در هر نوبت: { $count }
rb-enter-min-take = حداقل توپ در هر نوبت را از ۱ تا ۵ وارد کنید:
rb-option-changed-min-take = حداقل توپ در هر نوبت روی { $count } تنظیم شد.
rollingballs-desc-min-take = حداقل تعداد توپ‌هایی که یک بازیکن باید در یک نوبت بردارد (پیش‌فرض ۱، محدوده ۱-۵).
rb-set-max-take = حداکثر توپ در هر نوبت: { $count }
rb-enter-max-take = حداکثر توپ در هر نوبت را از ۱ تا ۵ وارد کنید:
rb-option-changed-max-take = حداکثر توپ در هر نوبت روی { $count } تنظیم شد.
rollingballs-desc-max-take = حداکثر تعداد توپ‌هایی که یک بازیکن می‌تواند در یک نوبت بردارد. اگر این مقدار از حداقل کمتر باشد، بازی نمی‌تواند شروع شود (پیش‌فرض ۳، محدوده ۱-۵).
rb-set-view-pipe-limit = پیش‌نمایش‌های جدید لوله برای هر بازیکن: { $count }
rb-enter-view-pipe-limit = پیش‌نمایش‌های جدید لوله برای هر بازیکن را از ۰ تا ۱۰۰ وارد کنید؛ ۰ پیش‌نمایش را غیرفعال می‌کند:
rb-option-changed-view-pipe-limit = پیش‌نمایش‌های جدید لوله برای هر بازیکن روی { $count } تنظیم شد.
rollingballs-desc-view-pipe-limit = تعداد توپ‌های آینده‌ای که می‌توان از لوله پیش‌نمایش کرد. برای غیرفعال کردن پیش‌نمایش، ۰ را تنظیم کنید (پیش‌فرض ۵، محدوده ۰-۱۰۰).
rb-set-reshuffle-limit = به هم زدن برای هر بازیکن: { $count }
rb-enter-reshuffle-limit = به هم زدن برای هر بازیکن را از ۰ تا ۱۰۰ وارد کنید؛ ۰ به هم زدن را غیرفعال می‌کند:
rb-option-changed-reshuffle-limit = به هم زدن برای هر بازیکن روی { $count } تنظیم شد.
rollingballs-desc-reshuffle-limit = تعداد به هم زدن‌های موجود قبل از تمام شدن لوله (پیش‌فرض ۳، محدوده ۰-۱۰۰).
rb-set-reshuffle-penalty = جریمه‌ی به هم زدن: { $points } امتیاز
rb-enter-reshuffle-penalty = جریمه‌ی به هم زدن را از ۰ تا ۵ امتیاز وارد کنید:
rb-option-changed-reshuffle-penalty = جریمه‌ی به هم زدن روی { $points } امتیاز تنظیم شد.
rollingballs-desc-reshuffle-penalty = جریمه‌ی امتیازی اعمال‌شده هنگام استفاده از به هم زدن. این گزینه فقط زمانی ظاهر می‌شود که به هم زدن در دسترس باشد (پیش‌فرض ۱، محدوده ۰-۵).
rb-set-ball-packs = مجموعه‌های توپ ({ $count } از { $total } انتخاب شده)
rb-option-changed-ball-packs = انتخاب مجموعه‌های توپ تغییر کرد.
rollingballs-desc-ball-packs = انتخاب کنید که کدام مجموعه‌های توپ موضوعی در لوله گنجانده شوند. حداقل یک مجموعه باید انتخاب شده بماند.

# دلایل غیرفعال و اعتبارسنجی تنظیمات
rb-draw-resolving = منتظر بمانید تا برداشت توپ فعلی { $player } تمام شود، سپس اقدام لوله‌ی دیگری را شروع کنید.
rb-take-not-your-turn = نمی‌توانید { $count } توپ را بردارید زیرا نوبت { $player } است.
rb-take-outside-range = شما سعی کردید { $count } توپ بردارید، اما این بازی { $min } تا { $max } در هر نوبت معمولی را مجاز می‌کند.
rb-not-enough-balls = شما سعی کردید { $count } توپ بردارید، اما فقط { $remaining } توپ در لوله باقی‌مانده است.
rb-reshuffle-not-your-turn = نمی‌توانید اکنون به هم بزنید زیرا نوبت { $player } است.
rb-no-reshuffles-left = شما از همه‌ی { $limit } به هم زدن خود برای این بازی استفاده کرده‌اید.
rb-already-reshuffled = شما قبلاً در این نوبت به هم زدید. برای پایان نوبت، توپ بردارید.
rb-not-enough-balls-to-reshuffle = به هم زدن حداقل به { $required } توپ نیاز دارد، اما فقط { $remaining } توپ باقی‌مانده است. به جای آن توپ بردارید.
rb-no-views-left = لوله تغییر کرده است و شما از همه‌ی { $limit } پیش‌نمایش جدید خود استفاده کرده‌اید. همچنان می‌توانید قبل از حرکت لوله، یک پیش‌نمایش بدون تغییر را دوباره باز کنید.
rb-error-min-take-invalid = حداقل برداشت { $count } است؛ باید از { $min } تا { $max } باشد.
rb-error-max-take-invalid = حداکثر برداشت { $count } است؛ باید از { $min } تا { $max } باشد.
rb-error-take-range-conflict = حداقل برداشت { $min } است که بالاتر از حداکثر { $max } است. قبل از شروع، حداقل را کاهش دهید یا حداکثر را افزایش دهید.
rb-error-view-limit-invalid = محدودیت پیش‌نمایش { $count } است؛ باید از { $min } تا { $max } باشد.
rb-error-reshuffle-limit-invalid = محدودیت به هم زدن { $count } است؛ باید از { $min } تا { $max } باشد.
rb-error-reshuffle-penalty-invalid = جریمه‌ی به هم زدن { $points } است؛ باید از { $min } تا { $max } امتیاز باشد.
rb-error-no-ball-packs = قبل از شروع توپ‌های غلتان، حداقل یک مجموعه‌ی توپ را انتخاب کنید.
rb-error-invalid-ball-packs = انتخاب شامل { $count } { $count ->
    [one] مجموعه‌ی توپ غیرقابل‌دسترس
   *[other] مجموعه‌ی توپ غیرقابل‌دسترس
} است. قبل از شروع، مجموعه‌های غیرقابل‌دسترس را حذف کنید.

# مجموعه‌های توپ
rb-pack-all = همه‌ی مجموعه‌های توپ مخلوط
rb-pack-international = دور دنیا
rb-pack-vietnam = سفر در ویتنام

# دور دنیا: ۵-
rb-ball-paris-pickpocket = گذرنامه و کیف پول در خارج از کشور دزدیده شد
rb-ball-lost-luggage-in-london = ویزیت پزشکی اضطراری در خارج از کشور
rb-ball-tokyo-train-delay = آخرین اتصال بین‌المللی از دست رفت
rb-ball-sahara-sandstorm = تخلیه‌ی اضطراری در آب و هوای شدید
rb-ball-passport-lost-before-flight = گذرنامه قبل از پرواز گم شد
# دور دنیا: ۴-
rb-ball-venice-flood = سیل محل اقامت شما را می‌بندد
rb-ball-new-york-traffic = لغو پرواز شبانه
rb-ball-amazon-mosquito-swarm = چمدان ضروری به کشور اشتباه فرستاده شد
rb-ball-berlin-club-rejected = رزرو هتل در هنگام ورود وجود ندارد
rb-ball-hotel-booking-vanished = مسیر کوهستانی برای چند روز بسته شد
# دور دنیا: ۳-
rb-ball-spilled-coffee-in-rome = گوشی در حین ترانسفر ترک خورد
rb-ball-sydney-sunburn = گرمازدگی یک سفر یک روزه را لغو می‌کند
rb-ball-istanbul-bazaar-scam = رزرو تور پیش‌پرداخت‌شده لغو می‌شود
rb-ball-moscow-blizzard = کولاک قطار شما را سرگردان می‌کند
rb-ball-dubai-heatwave = وسیله‌ی نقلیه‌ی کرایه‌ای خراب می‌شود
# دور دنیا: ۲-
rb-ball-mexico-city-smog = کیفیت پایین هوا برنامه‌ی سفر را تغییر می‌دهد
rb-ball-cairo-camel-spit = بیماری حرکت در یک سفر طولانی
rb-ball-athens-ruins-trip = پیچ خوردگی مچ پا در تور پیاده‌روی
rb-ball-rio-carnival-hangover = خواب ماند و تور صبحگاهی را از دست داد
rb-ball-bali-belly = ناراحتی معده یک بعدازظهر را از دست می‌دهد
# دور دنیا: ۱-
rb-ball-swiss-alps-avalanche = مسیر دیدنی برای ایمنی بسته شد
rb-ball-amsterdam-bicycle-crash = پنچری لاستیک دوچرخه
rb-ball-bangkok-tuk-tuk-breakdown = توک‌توک در ترافیک متوقف می‌شود
rb-ball-iceland-volcano-ash = هشدار آب و هوایی پرواز را به تأخیر می‌اندازد
rb-ball-cape-town-wind = باد شدید نقطه‌ی دید را می‌بندد
# دور دنیا: ۰
rb-ball-neutral-passport = یک مهر گذرنامه‌ی تازه
rb-ball-airport-layover = یک توقف آرام در فرودگاه
rb-ball-hotel-lobby = انتظار در لابی هتل
rb-ball-tourist-map = باز کردن نقشه‌ی شهر
rb-ball-souvenir-magnet = انتخاب یک آهنربای سوغاتی
# دور دنیا: ۱+
rb-ball-free-museum-day = ورودی رایگان موزه
rb-ball-street-food-snack = میان‌وعده‌ی عالی خیابانی
rb-ball-post-card-home = کارت پستال به خانه فرستاده شد
rb-ball-friendly-local = راهنمایی مفید از یک محلی
rb-ball-sunny-day = آب و هوای عالی برای گشت‌وگذار
# دور دنیا: ۲+
rb-ball-eiffel-tower-view = نمای پاریس از برج ایفل
rb-ball-taj-mahal-sunrise = طلوع خورشید در تاج محل
rb-ball-great-wall-hike = پیاده‌روی روی دیوار بزرگ چین
rb-ball-machu-picchu-climb = صبح در ماچو پیچو
rb-ball-kyoto-cherry-blossoms = شکوفه‌های گیلاس در کیوتو
# دور دنیا: ۳+
rb-ball-colosseum-tour = بازدید راهنما از کولوسئوم
rb-ball-pyramids-exploration = کاوش در مجموعه‌ی اهرام جیزه
rb-ball-santorini-sunset = غروب خورشید در سانتورینی
rb-ball-aurora-borealis = شفق شمالی در آسمان
rb-ball-safari-lion-sighting = مشاهده‌ی حیات وحش در سافاری مسئولانه
# دور دنیا: ۴+
rb-ball-bora-bora-villa = اقامت در تالاب بورا بورا
rb-ball-maldives-scuba = غواصی در صخره‌های مالدیو
rb-ball-niagara-falls-boat = سفر با قایق در آبشار نیاگارا
rb-ball-grand-canyon-heli = تور هوایی گرند کنیون
rb-ball-serengeti-migration = مهاجرت بزرگ در سرنگتی
# دور دنیا: ۵+
rb-ball-first-class-upgrade = ارتقاء غیرمنتظره به درجه‌ی یک
rb-ball-lottery-in-macau = برنده‌ی یک بلیط قطار یک ساله
rb-ball-private-jet = سفر جزیره‌ای یک بار در طول عمر
rb-ball-royal-palace-invite = بازدید خصوصی از موزه پس از ساعات کاری
rb-ball-world-tour-ticket = بلیط دور دنیا

# سفر در ویتنام: ۵-
rb-ball-stolen-motorbike = گذرنامه و کیف پول در طول سفر دزدیده شد
rb-ball-flooded-street-saigon = سیل باعث جابجایی اضطراری می‌شود
rb-ball-food-poisoning-bun-mam = اورژانس پزشکی سفر را قطع می‌کند
rb-ball-fake-taxi-scam = خرابی حمل‌ونقل باعث از دست دادن پرواز می‌شود
rb-ball-passport-lost-at-airport = گذرنامه در فرودگاه گم شد
# سفر در ویتنام: ۴-
rb-ball-typhoon-in-central-vietnam = تخلیه‌ی طوفان در ساحل مرکزی
rb-ball-lost-wallet-ben-thanh = چمدان ضروری در حین حمل‌ونقل گم شد
rb-ball-traffic-jam-hanoi = لغو قطار شبانه
rb-ball-pickpocketed-in-bui-vien = گوشی در یک منطقه‌ی شلوغ دزدیده شد
rb-ball-mountain-road-landslide = گذرگاه کوهستانی بر اثر رانش زمین بسته شد
# سفر در ویتنام: ۳-
rb-ball-spilled-pho = دوربین در باران ناگهانی آسیب دید
rb-ball-overcharged-for-coffee = اشتباه در رزرو هتل
rb-ball-sunburn-in-mui-ne = گرمازدگی در موی نه
rb-ball-missed-train-to-sapa = قطار شبانه به لائو کای از دست رفت
rb-ball-loud-karaoke-next-door = شب بی‌خوابی قبل از حرکت زودهنگام
# سفر در ویتنام: ۲-
rb-ball-broken-flip-flop = بند صندل در تور پیاده‌روی پاره شد
rb-ball-sudden-downpour = باران ناگهانی استوایی
rb-ball-dog-chased-you = ایستگاه اتوبوس اشتباه دور از هتل
rb-ball-bitten-by-mosquitoes = یک عصر پر از نیش پشه
rb-ball-out-of-gas = موتورسیکلت بنزین تمام می‌کند
# سفر در ویتنام: ۱-
rb-ball-spicy-chili-bite = یک فلفل تند غیرمنتظره
rb-ball-delayed-flight = تأخیر کوتاه پرواز داخلی
rb-ball-wifi-disconnected = سیگنال ضعیف در کوهستان
rb-ball-forgot-umbrella = بارانی در هتل جا ماند
rb-ball-minor-scratch = پیچ اشتباه در محله‌ی قدیمی
# سفر در ویتنام: ۰
rb-ball-plastic-stool = نشستن روی چهارپایه‌ی پلاستیکی کنار پیاده‌رو
rb-ball-iced-tea-tra-da = یک لیوان ترا دا
rb-ball-waiting-for-green-light = انتظار برای چراغ سبز طولانی
rb-ball-bamboo-hat = امتحان کردن نون لا
rb-ball-motorbike-helmet = بستن کلاه موتورسیکلت
# سفر در ویتنام: ۱+
rb-ball-tasty-banh-mi = بام می‌تازه برای صبحانه
rb-ball-free-sugar-cane-juice = آب نیشکر تازه
rb-ball-friendly-street-vendor = استقبال گرم از فروشنده‌ی بازار
rb-ball-cool-breeze = نسیم خنک پس از باران
rb-ball-found-10k-vnd = یک سواری ارزان با اتوبوس محلی
# سفر در ویتنام: ۲+
rb-ball-delicious-pho-bowl = یک کاسه‌ی خوش‌عطر فو
rb-ball-egg-coffee-in-hanoi = قهوه‌ی تخم‌مرغ در هانوی
rb-ball-boat-ride-in-ninh-binh = قایق‌رانی در مجموعه‌ی منظر ترانگ آن
rb-ball-lantern-festival-hoian = شبی با فانوس در شهر باستانی هوی آن
rb-ball-motorbike-road-trip = قایق‌رانی در باغ‌های دلتای مکونگ
# سفر در ویتنام: ۳+
rb-ball-ha-long-bay-cruise = سفر دریایی در خلیج هالانگ - مجمع‌الجزایر کات با
rb-ball-golden-bridge-bana-hills = پل طلایی در بالای تپه‌های با نا
rb-ball-phu-quoc-sunset = غروب خورشید در فو کوک
rb-ball-sapa-terraced-fields = مزارع پله‌ای در اطراف ساپا
rb-ball-phong-nha-cave-exploration = سفر به غارها در فونگ نها - که بانگ
# سفر در ویتنام: ۴+
rb-ball-tet-holiday-lucky-money = دیدار تت و پول خوش‌یمنی
rb-ball-vip-ticket-to-concert = طلوع خورشید در حلقه‌ی ها گیانگ
rb-ball-luxury-resort-stay = بازدید از حفاظت جامعه در کن دائو
rb-ball-business-class-flight = کابین دیدنی در قطار اتحاد مجدد
rb-ball-won-lottery-vietlott = شب جشن در میان بناهای تاریخی هوئه
# سفر در ویتنام: ۵+
rb-ball-billionaire-inheritance = اکسپدیشن سون دونگ
rb-ball-found-gold-treasure = کارگاه فرهنگی خصوصی با صنعتگران ماهر
rb-ball-free-house-in-district-1 = سفر یک ماهه با قطار در سراسر ویتنام
rb-ball-national-hero-award = مهمان ویژه در جشنواره‌ی روستا
rb-ball-ultimate-happiness = سفر رؤیایی از ها گیانگ تا کا مائو