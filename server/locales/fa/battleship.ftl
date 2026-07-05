game-name-battleship = نبرد دریایی

# گزینه‌ها
battleship-set-grid-size = منطقه‌ی نبرد: { $size }
battleship-select-grid-size = اندازه‌ی منطقه‌ی نبرد را انتخاب کنید
battleship-option-changed-grid-size = منطقه‌ی نبرد روی { $size } تنظیم شد.
battleship-desc-grid-size = اندازه‌ی شبکه‌ی اقیانوس را برای نبرد دریایی انتخاب می‌کند؛ شبکه‌های بزرگ‌تر جستجوهای طولانی‌تری ایجاد می‌کنند.

battleship-set-placement-mode = استقرار: { $mode }
battleship-select-placement-mode = حالت استقرار را انتخاب کنید
battleship-option-changed-placement-mode = حالت استقرار روی { $mode } تنظیم شد.
battleship-desc-placement-mode = انتخاب می‌کند که کشتی‌ها قبل از شروع نبرد به‌طور خودکار یا دستی قرار داده شوند.

battleship-set-replay-on-hit = شلیک اضافی در صورت اصابت: { $enabled }
battleship-option-changed-replay-on-hit = شلیک اضافی در صورت اصابت روی { $enabled } تنظیم شد.
battleship-desc-replay-on-hit = وقتی فعال باشد، بازیکنی که به هدف اصابت می‌زند، بلافاصله یک شلیک دیگر انجام می‌دهد.

battleship-set-turn-timer = زمان‌سنج نوبت: { $seconds }
battleship-select-turn-timer = زمان‌سنج نوبت را انتخاب کنید
battleship-option-changed-turn-timer = زمان‌سنج نوبت روی { $seconds } تنظیم شد.
battleship-desc-turn-timer = محدودیت زمانی اختیاری برای هر نوبت نبرد دریایی؛ اگر زمان تمام شود، بازی به یک مختصات تصادفی شلیک می‌کند. برای بدون زمان‌سنج، Unlimited را انتخاب کنید.

# برچسب‌های گزینه‌ها
battleship-grid-6x6 = ۶ در ۶
battleship-grid-8x8 = ۸ در ۸
battleship-grid-10x10 = ۱۰ در ۱۰
battleship-grid-12x12 = ۱۲ در ۱۲

battleship-placement-auto = خودکار
battleship-placement-manual = دستی

battleship-timer-off = خاموش
battleship-timer-30 = ۳۰ ثانیه
battleship-timer-45 = ۴۵ ثانیه
battleship-timer-60 = ۶۰ ثانیه

# اعتبارسنجی تنظیمات
battleship-error-invalid-grid-size = اندازه‌ی منطقه‌ی نبرد { $size } پشتیبانی نمی‌شود.
battleship-error-grid-too-small = منطقه‌ی نبرد { $size } در { $size } برای کل ناوگان بسیار کوچک است. حداقل از { $minimum } در { $minimum } استفاده کنید.
battleship-error-invalid-placement-mode = حالت استقرار { $mode } پشتیبانی نمی‌شود.
battleship-error-invalid-turn-timer = زمان‌سنج نوبت { $seconds } پشتیبانی نمی‌شود.

# نام کشتی‌ها
battleship-ship-carrier = ناو هواپیمابر
battleship-ship-battleship = کشتی جنگی
battleship-ship-destroyer = ناوشکن
battleship-ship-submarine = زیردریایی
battleship-ship-patrol = گشت‌زنی
battleship-ship-unknown = شناور

# جهت‌ها
battleship-horizontal = افقی
battleship-vertical = عمودی

# اقدامات
battleship-orient-horizontal = استقرار افقی
battleship-orient-vertical = استقرار عمودی
battleship-orient-horizontal-at = استقرار { $ship } به‌صورت افقی در { $coord }
battleship-orient-vertical-at = استقرار { $ship } به‌صورت عمودی در { $coord }
battleship-toggle-view = تغییر شبکه
battleship-read-fleet = وضعیت ناوگان
battleship-read-enemy-fleet = اطلاعات ناوگان دشمن

# مرحله‌ی استقرار
battleship-deploy-start = مرحله‌ی استقرار. { $ship } خود را که { $size } بخش طول دارد، قرار دهید. یک مختصات انتخاب کنید، سپس جهت را انتخاب کنید.
battleship-choose-orientation = استقرار { $ship } در { $coord }، { $size } بخش. جهت را انتخاب کنید.
battleship-ship-placed = { $ship } در { $coord } با جهت { $orientation } مستقر شد.
battleship-cannot-place = نمی‌توان { $ship } را در { $coord } { $orientation } مستقر کرد. شناور جا نمی‌شود یا با کشتی دیگری همپوشانی دارد.
battleship-place-next-ship = شناور بعدی: { $ship }، { $size } بخش.
battleship-deploy-done = ناوگان مستقر شد. در انتظار دشمن.
battleship-deploy-complete = استقرار کامل شد.
battleship-select-cell-first = ابتدا یک مختصات در شبکه انتخاب کنید.
battleship-deploy-in-progress = استقرار هنوز در حال انجام است.
battleship-deploy-status-header = مرحله‌ی قرار دادن کشتی‌ها.
battleship-deploy-status-ready-self = شما آماده هستید.
battleship-deploy-status-ready-other = { $player } آماده است.
battleship-deploy-status-not-ready-self = شما هنوز آماده نیستید.
battleship-deploy-status-not-ready-other = { $player } هنوز آماده نیست.

# مرحله‌ی نبرد
battleship-battle-start = همه‌ی کشتی‌ها در موقعیت خود. آتش!

# اصابت - اول شخص (شلیک‌کننده)، دوم شخص (هدف)، سوم شخص (تماشاگر)
battleship-hit-self = شما به { $coord } شلیک می‌کنید. اصابت مستقیم!
battleship-hit-target = { $player } به { $coord } شما شلیک می‌کند. اصابت مستقیم!
battleship-hit-spectator = { $player } به { $coord } { $target } شلیک می‌کند. اصابت مستقیم!

# خطا - اول/دوم/سوم شخص
battleship-miss-self = شما به { $coord } شلیک می‌کنید. خطا رفت.
battleship-miss-target = { $player } به { $coord } شما شلیک می‌کند. خطا رفت.
battleship-miss-spectator = { $player } به { $coord } { $target } شلیک می‌کند. خطا رفت.

# غرق - اول/دوم/سوم شخص
battleship-sunk-self = شما { $ship } دشمن را غرق کردید!
battleship-sunk-target = { $player } { $ship } شما را غرق کرد!
battleship-sunk-spectator = { $player } { $ship } { $target } را غرق کرد!

# پیروزی - اول/دوم/سوم شخص
battleship-victory-self = شما برنده شدید! همه‌ی کشتی‌های دشمن غرق شدند.
battleship-victory-target = { $player } برنده شد! همه‌ی کشتی‌های شما غرق شدند.
battleship-victory-spectator = { $player } برنده شد! همه‌ی کشتی‌های { $target } غرق شدند.

battleship-shot-in-flight = یک گلوله هنوز در حال پرواز است. قبل از شلیک مجدد منتظر نتیجه باشید.
battleship-not-your-turn = نوبت شلیک شما نیست. منتظر { $player } برای انتخاب مختصات باشید.
battleship-wait-for-turn = قبل از انتخاب مختصات، منتظر دستور شلیک بعدی باشید.
battleship-already-shot = شما قبلاً به { $coord } شلیک کرده‌اید. یک مختصات ناشناخته انتخاب کنید.
battleship-switch-to-shots = شما در حال مشاهده‌ی آب‌های خود هستید، بنابراین شلیک مسدود است. برای تغییر به شبکه‌ی هدف، V را فشار دهید.
battleship-timeout-fire = زمان تمام شد! شلیک خودکار به { $coord }.

# تغییر نمای
battleship-view-own = مشاهده‌ی آب‌های خود.
battleship-view-shots = مشاهده‌ی شبکه‌ی هدف.

# برچسب‌های سلول‌ها
battleship-cell-empty = { $coord }، آب باز.
battleship-cell-ship-placed = { $coord }، { $ship }.
battleship-cell-unknown = { $coord }، ناشناخته.
battleship-cell-hit = { $coord }، اصابت.
battleship-cell-sunk = { $coord }، { $ship }، غرق‌شده.
battleship-cell-miss = { $coord }، خطا.
battleship-cell-own-ship = { $coord }، { $ship } شما.
battleship-cell-own-hit = { $coord }، { $ship } شما، اصابت.
battleship-cell-own-sunk = { $coord }، { $ship } شما، غرق‌شده.
battleship-cell-own-miss = { $coord }، خطای ورودی.

# وضعیت ناوگان
battleship-fleet-header = ناوگان شما
battleship-status-intact = آماده‌ی نبرد
battleship-status-damaged = آسیب‌دیده ({ $hits } از { $size } اصابت)
battleship-status-sunk = غرق‌شده

battleship-enemy-fleet-header = ناوگان دشمن
battleship-enemy-fleet-summary = { $sunk } از { $total } شناور دشمن غرق شد.
battleship-enemy-ship-sunk = { $ship } (اندازه { $size }): غرق‌شده

# صفحه‌ی پایان
battleship-winner-line = { $player } برنده شد!
battleship-stats-line = { $player }: { $shots } شلیک، { $hits } اصابت، { $accuracy }% دقت