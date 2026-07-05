game-name-holdem = پوکر تگزاس هولدم

holdem-set-starting-chips = تراشه‌های اولیه: { $count }
holdem-enter-starting-chips = تراشه‌های اولیه را وارد کنید
holdem-option-changed-starting-chips = تراشه‌های اولیه روی { $count } تنظیم شد.
holdem-desc-starting-chips = تعداد تراشه‌های اولیه‌ی هر بازیکن در تگزاس هولدم، از ۱۰۰ تا ۱٬۰۰۰٬۰۰۰ تراشه. پیش‌فرض: ۲۰٬۰۰۰.

holdem-set-big-blind = بیگ بلایند: { $count }
holdem-enter-big-blind = بیگ بلایند را وارد کنید
holdem-option-changed-big-blind = بیگ بلایند روی { $count } تنظیم شد.
holdem-desc-big-blind = مبلغ پایه‌ی بیگ بلایند. باید کمتر از تراشه‌های اولیه باشد (پیش‌فرض ۲۰۰، محدوده ۱-۱٬۰۰۰٬۰۰۰ تراشه).

holdem-set-ante = آنته: { $count }
holdem-enter-ante = آنته را وارد کنید
holdem-option-changed-ante = آنته روی { $count } تنظیم شد.
holdem-desc-ante = مبلغ اجباری اختیاری که هر بازیکن فعال پس از فعال شدن آنته‌ها یک بار پرداخت می‌کند، از ۰ تا ۱٬۰۰۰٬۰۰۰ تراشه. پیش‌فرض: ۰.

holdem-set-ante-start = آنته از سطح شروع می‌شود: { $count }
holdem-enter-ante-start = سطح بلایند را برای فعال‌سازی آنته وارد کنید
holdem-option-changed-ante-start = سطح شروع آنته روی { $count } تنظیم شد.
holdem-desc-ante-start-level = سطح بلایندی که آنته‌ها از آن شروع می‌شوند. آنته مثبت از دست اول زمانی که این مقدار ۰ باشد فعال است (پیش‌فرض ۰، محدوده ۰-۲۰).

holdem-set-turn-timer = زمان‌سنج نوبت: { $mode }
holdem-select-turn-timer = زمان‌سنج نوبت را انتخاب کنید
holdem-option-changed-turn-timer = زمان‌سنج نوبت روی { $mode } تنظیم شد.
holdem-desc-turn-timer = محدودیت زمانی اختیاری برای هر تصمیم هولدم: ۵، ۱۰، ۱۵، ۲۰، ۳۰، ۴۵، ۶۰، یا ۹۰ ثانیه، یا بدون محدودیت. پیش‌فرض: بدون محدودیت.

holdem-set-blind-timer = زمان‌سنج بلایند: { $mode }
holdem-select-blind-timer = زمان‌سنج بلایند را انتخاب کنید
holdem-option-changed-blind-timer = زمان‌سنج بلایند روی { $mode } تنظیم شد.
holdem-desc-blind-timer = دقیقه بین افزایش بلایندها: ۵، ۱۰، ۱۵، ۲۰، یا ۳۰. پیش‌فرض: ۲۰ دقیقه.

holdem-set-raise-mode = حالت افزایش: { $mode }
holdem-select-raise-mode = حالت افزایش را انتخاب کنید
holdem-option-changed-raise-mode = حالت افزایش روی { $mode } تنظیم شد.
holdem-desc-raise-mode = سبک محدودیت افزایش: بدون محدودیت، محدودیت پات، یا محدودیت دوبرابر پات. پیش‌فرض: بدون محدودیت.

holdem-set-max-raises = حداکثر افزایش در هر دور شرط‌بندی: { $count }
holdem-enter-max-raises = حداکثر افزایش در هر دور شرط‌بندی را وارد کنید (۰ برای بدون محدودیت)
holdem-option-changed-max-raises = حداکثر افزایش در هر دور شرط‌بندی روی { $count } تنظیم شد.
holdem-desc-max-raises = حداکثر افزایش مجاز در یک دور شرط‌بندی، از ۰ تا ۱۰. برای بدون محدودیت، ۰ را تنظیم کنید. پیش‌فرض: ۰.

holdem-error-big-blind-too-high = بیگ بلایند ({ $blind } تراشه) باید کمتر از تراشه‌های اولیه ({ $chips } تراشه) باشد.
holdem-error-ante-too-high = آنته ({ $ante } تراشه) باید کمتر از تراشه‌های اولیه ({ $chips } تراشه) باشد.
holdem-error-forced-bets-too-high = با آنته‌های فعال از سطح ۰، آنته به اضافه‌ی بیگ بلایند ({ $ante } + { $blind } تراشه) باید کمتر از تراشه‌های اولیه ({ $chips } تراشه) باشد.

holdem-antes-posted = آنته‌ها پرداخت شدند. پات اکنون شامل { $amount } تراشه است.
holdem-you-post-small-blind = شما اسمال بلایند ({ $sb } تراشه) را پرداخت می‌کنید. { $bb_player } بیگ بلایند ({ $bb } تراشه) را پرداخت می‌کند.
holdem-you-post-big-blind = { $sb_player } اسمال بلایند ({ $sb } تراشه) را پرداخت می‌کند. شما بیگ بلایند ({ $bb } تراشه) را پرداخت می‌کنید.
holdem-players-post-blinds = { $sb_player } اسمال بلایند ({ $sb } تراشه) را پرداخت می‌کند. { $bb_player } بیگ بلایند ({ $bb } تراشه) را پرداخت می‌کند.

holdem-raise-invalid = برای مبلغ افزایش، یک عدد صحیح بزرگتر از ۰ وارد کنید.
holdem-raise-cap-reached = محدودیت { $count } افزایش در این دور شرط‌بندی قبلاً به‌دست آمده است. می‌توانید همراهی کنید یا کناره‌گیری کنید.
holdem-raise-over-stack = شما سعی کردید { $requested } تراشه افزایش دهید، اما فقط { $chips } تراشه باقی‌مانده دارید. افزایش کمتری وارد کنید یا همه‌چیز را انتخاب کنید.
holdem-raise-too-small = شما سعی کردید { $requested } تراشه افزایش دهید. حداقل افزایش { $minimum } تراشه است.
holdem-raise-over-limit = شما سعی کردید { $requested } تراشه افزایش دهید. تحت { $mode ->
    [pot_limit] محدودیت پات
    [double_pot] محدودیت دوبرابر پات
   *[other] حالت افزایش انتخاب‌شده
}، بزرگ‌ترین افزایش موجود پس از همراهی { $maximum } تراشه است.
holdem-all-in-over-limit = نمی‌توانید با { $stack } تراشه‌ی باقی‌مانده‌ی خود همه‌چیز بروید زیرا { $mode ->
    [pot_limit] محدودیت پات
    [double_pot] محدودیت دوبرابر پات
   *[other] حالت افزایش انتخاب‌شده
} در حال حاضر حداکثر { $maximum } تراشه افزایش را پس از همراهی مجاز می‌کند. برای وارد کردن مبلغ مجاز، از افزایش استفاده کنید.
holdem-all-in-raise-cap-reached = نمی‌توانید به عنوان یک افزایش کامل همه‌چیز بروید زیرا محدودیت { $count } افزایش قبلاً به‌دست آمده است. می‌توانید همراهی کنید یا کناره‌گیری کنید.
holdem-all-in-unavailable-raise-cap = همه‌چیز در دسترس نیست زیرا پس از رسیدن به محدودیت افزایش، یک افزایش کامل محسوب می‌شود. می‌توانید همراهی کنید یا کناره‌گیری کنید.
holdem-all-in-unavailable-limit = همه‌چیز در دسترس نیست زیرا تراشه‌های شما از محدودیت شرط‌بندی فعلی بیشتر است. برای وارد کردن مبلغ مجاز، از افزایش استفاده کنید.
holdem-raise-unavailable-cap = افزایش در دسترس نیست زیرا این دور شرط‌بندی به محدودیت افزایش خود رسیده است.
holdem-raise-unavailable-limit = افزایش کامل با تراشه‌های شما و محدودیت شرط‌بندی فعلی در دسترس نیست. می‌توانید همراهی کنید، کناره‌گیری کنید، یا در صورت قانونی بودن از همه‌چیز استفاده کنید.

holdem-current-bet = شرط فعلی میز { $amount } تراشه است.
holdem-raise-range = حداقل افزایش { $minimum } تراشه است. پس از همراهی می‌توانید تا { $maximum } تراشه افزایش دهید.
holdem-no-full-raise-available = برای همراهی به { $to_call } تراشه نیاز دارید و { $chips } تراشه باقی‌مانده دارید، بنابراین نمی‌توانید افزایش کامل انجام دهید. می‌توانید همه‌چیز را همراهی کنید یا کناره‌گیری کنید.
holdem-button-unavailable = هنوز موقعیت دکمه‌ای برای دست فعلی وجود ندارد.
holdem-position-unavailable = شما در دست فعلی فعال نیستید، بنابراین موقعیت شرط‌بندی ندارید.
holdem-reveal-no-live-hand = فقط زمانی می‌توانید کارت‌های مخفی را آشکار کنید که با یک دست زنده به نمایش رسیده باشید.
holdem-private-hand-unavailable = تراشه‌های شما تمام شده است و دیگر دست زنده‌ای برای مشاهده ندارید.

holdem-winner-chips = { $rank }. { $player }: { $chips } { $chips ->
    [one] تراشه
   *[other] تراشه
}