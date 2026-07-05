# Humanity Cards - ترجمه‌ی فارسی

game-name-humanitycards = کارت‌ها علیه بشریت

# گزینه‌ها
hc-set-winning-score = امتیاز برنده: { $score }
hc-enter-winning-score = امتیاز برنده را وارد کنید:
hc-option-changed-winning-score = امتیاز برنده روی { $score } تنظیم شد.
hc-desc-winning-score = تعداد کارت‌های برنده‌ای که یک بازیکن برای بردن مسابقه باید جمع‌آوری کند (پیش‌فرض ۷، محدوده ۳-۲۰).

hc-set-hand-size = تعداد کارت در دست: { $count }
hc-enter-hand-size = تعداد کارت در دست را وارد کنید:
hc-option-changed-hand-size = تعداد کارت در دست روی { $count } تنظیم شد.
hc-desc-hand-size = تعداد کارت‌های پاسخ که هر بازیکن پس از هر پر کردن مجدد در دست دارد. دست‌های بزرگ‌تر انتخاب‌های بیشتری می‌دهند اما دورها را طولانی‌تر می‌کنند (پیش‌فرض ۱۰، محدوده ۵-۱۵).

hc-set-card-packs = بسته‌های کارت ({ $count } از { $total } انتخاب شده)
hc-option-changed-card-packs = انتخاب بسته‌های کارت تغییر کرد.
hc-desc-card-packs = انتخاب کنید که کدام بسته‌های پاسخ و سوال در بازی با هم مخلوط شوند. حداقل یک بسته باید انتخاب شده بماند.

hc-set-czar-selection = انتخاب کارت تزار: { $mode }
hc-select-czar-selection = حالت انتخاب کارت تزار را انتخاب کنید
hc-option-changed-czar-selection = انتخاب کارت تزار روی { $mode } تنظیم شد.
hc-desc-czar-selection = تعیین می‌کند که چه کسی هر دور را داوری می‌کند: چرخشی در ترتیب نشستن، انتخاب تصادفی، یا برنده‌ی آخرین دور.

hc-set-num-judges = تعداد داوران: { $count }
hc-enter-num-judges = تعداد داوران را وارد کنید:
hc-option-changed-num-judges = تعداد داوران روی { $count } تنظیم شد.
hc-desc-num-judges = تعداد کارت تزارهایی که هر دور داوری می‌کنند. تعداد باید کمتر از تعداد بازیکنان باشد تا حداقل یک غیرداور بتواند ارسال کند؛ با چند داور، هر داوری می‌تواند برنده را انتخاب کند (پیش‌فرض ۱، محدوده ۱-۳).

hc-czar-rotating = چرخشی
hc-czar-random = تصادفی
hc-czar-winner = برنده‌ی آخرین دور

# جریان بازی
hc-game-starting = در حال به هم زدن دسته‌ها...
hc-dealing-cards = پخش { $count } کارت به هر بازیکن.
hc-round-start = دور { $round }.

# اعلام داور
hc-judge-is = { $judges } { $count ->
    [1] کارت تزار است
   *[other] کارت تزار هستند
}.
hc-you-are-judge = شما در این دور کارت تزار هستید.
hc-you-and-others-are-judges = شما و { $judges } در این دور کارت تزار هستید.
hc-you-are-not-judge = شما در این دور کارت تزار نیستید.

# کارت سیاه
hc-black-card = سوال این است: { $text }
hc-black-card-pick = { $count } کارت انتخاب کنید.
hc-view-black-card = مشاهده‌ی کارت سوال

# مرحله‌ی ارسال
hc-select-cards = { $count } { $count ->
    [one] کارت
   *[other] کارت
} از دست خود انتخاب کنید.
hc-card-selected = { $text }، انتخاب شد
hc-card-not-selected = { $text }
hc-submit-cards = ارسال ({ $selected } از { $required } انتخاب شد)
hc-submission-progress = { $submitted } از { $total } بازیکن ارسال کردند.
hc-waiting-for-submissions = در انتظار ارسال‌ها...
hc-already-submitted = شما قبلاً کارت‌های خود را ارسال کرده‌اید.
hc-you-submitted = شما کارت‌های خود را ارسال کردید.
hc-player-submitted = { $player } کارت‌های خود را ارسال کرد.
hc-judge-cannot-submit = شما در این دور کارت تزار هستید، بنابراین نمی‌توانید پاسخ ارسال کنید.
hc-not-submission-phase = فقط در مرحله‌ی ارسال می‌توانید کارت‌های سفید را انتخاب و ارسال کنید.
hc-card-not-in-hand = آن شکاف کارت در دست شما نیست.
hc-judge-has-no-submission = کارت تزار در این دور ارسالی برای پیش‌نمایش ندارد.
hc-no-submission-active = در حال حاضر هیچ ارسال فعالی برای پیش‌نمایش وجود ندارد.
hc-wrong-card-count = باید دقیقاً { $count } { $count ->
    [one] کارت
   *[other] کارت
} انتخاب کنید.

# مرحله‌ی داوری
hc-judging-start = همه‌ی کارت‌ها رسیدند! زمان داوری است.
hc-choose-best-card = بهترین کارت را انتخاب کنید
hc-choose-best-card-for = بهترین کارت را انتخاب کنید که با این سوال مطابقت دارد: { $prompt }
hc-select-winner-prompt = ارسال برنده را انتخاب کنید
hc-card-number = کارت { $number }
hc-submission-number = ارسال { $number }
hc-submission-option = { $text }
hc-only-judges-pick = فقط کارت تزار می‌تواند ارسال برنده را انتخاب کند.
hc-not-judging-phase = فقط در مرحله‌ی داوری می‌توانید ارسال برنده را انتخاب کنید.
hc-submission-not-available = آن ارسال دیگر در دسترس نیست.

# نتایج
hc-you-win-round = شما دور را برنده شدید! امتیاز شما اکنون { $score } است.
hc-player-wins-round = { $player } دور را برنده شد! امتیاز: { $score }.
hc-round-scores = امتیازات پس از دور { $round }:
hc-score-line = { $player }: { $score } { $score ->
    [one] امتیاز
   *[other] امتیاز
}
hc-final-score-line = { $rank }. { $player }: { $score } { $score ->
    [one] امتیاز
   *[other] امتیاز
}
hc-all-submissions = سایر ارسال‌ها:
hc-your-winning-answer = پاسخ برنده‌ی شما: { $text }
hc-winning-answer-player = پاسخ برنده‌ی { $player }: { $text }
hc-your-other-submission = سایر ارسال‌های شما: { $text }
hc-other-submission-player = { $player }: { $text }

# مشاهده
hc-preview-submission = پیش‌نمایش ارسال خود
hc-view-submission = مشاهده‌ی ارسال خود
hc-preview-submission-text = پیش‌نمایش: { $text }
hc-your-submission = ارسال شما: { $text }
hc-select-cards-first = ابتدا حداقل ۱ کارت انتخاب کنید.

# برد
hc-game-winner = { $player } با { $score } امتیاز برنده شد!
hc-you-win = شما با { $score } امتیاز برنده شدید!
hc-english-content-note = توجه: متن کارت‌های سوال و پاسخ در حال حاضر فقط از انگلیسی پشتیبانی می‌کند.

# مدیریت دسته
hc-deck-reshuffled = توده‌ی دور ریخته‌ی کارت‌های سفید دوباره به دسته برگردانده شد.
hc-black-deck-reshuffled = توده‌ی دور ریخته‌ی کارت‌های سیاه دوباره به دسته برگردانده شد.
hc-not-enough-cards = کارت‌های کافی وجود ندارد. سعی کنید بسته‌های بیشتری را فعال کنید.
hc-error-too-many-judges = { $judges } داور حداقل به { $required } بازیکن نیاز دارد، اما این میز { $players } بازیکن دارد. تعداد داوران را کاهش دهید یا بازیکنان بیشتری اضافه کنید.
hc-error-no-valid-packs = هیچ بسته‌ی کارت معتبری انتخاب نشده است. قبل از شروع حداقل یک بسته را انتخاب کنید.
hc-error-no-black-cards = بسته‌های کارت انتخاب‌شده هیچ کارت سوال سیاهی ندارند. قبل از شروع بسته‌ی دیگری را انتخاب کنید.
hc-error-not-enough-white-cards = { $players } بازیکن با اندازه‌ی دست { $hand_size } حداقل به { $needed } کارت سفید نیاز دارند، اما بسته‌های انتخاب‌شده فقط { $available } کارت ارائه می‌دهند. بسته‌های بیشتری را فعال کنید یا اندازه‌ی دست را کاهش دهید.
hc-error-pick-exceeds-hand-size = بسته‌های انتخاب‌شده شامل سوالی است که به { $pick } پاسخ نیاز دارد، اما اندازه‌ی دست فقط { $hand_size } است. اندازه‌ی دست را افزایش دهید یا بسته‌های دیگری را انتخاب کنید.

# مدیریت دست
hc-view-hand = مشاهده‌ی دست
hc-toggle-card-keybind = تغییر وضعیت کارت { $number }
hc-submit-cards-keybind = ارسال کارت‌ها

# امتیازات
hc-view-scores = مشاهده‌ی امتیازات
hc-no-scores = هنوز امتیازی وجود ندارد.

# نوبت کیست / داور کیست
hc-whose-judge = چه کسی داوری می‌کند
hc-waiting-for = در انتظار ارسال { $names }.
hc-all-submitted-waiting-judge = همه‌ی بازیکنان ارسال کردند. در انتظار داوری { $judge }.