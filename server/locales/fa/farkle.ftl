game-name-farkle = فارکل

farkle-roll = پرتاب { $count } { $count ->
    [one] تاس
   *[other] تاس
}
farkle-bank = ذخیره‌ی { $points } امتیاز

farkle-take-single-one = تک ۱ برای { $points } امتیاز
farkle-take-single-five = تک ۵ برای { $points } امتیاز
farkle-take-three-kind = سه { $number } برای { $points } امتیاز
farkle-take-four-kind = چهار { $number } برای { $points } امتیاز
farkle-take-five-kind = پنج { $number } برای { $points } امتیاز
farkle-take-six-kind = شش { $number } برای { $points } امتیاز
farkle-take-small-straight = دنباله‌ی کوچک برای { $points } امتیاز
farkle-take-large-straight = دنباله‌ی بزرگ برای { $points } امتیاز
farkle-take-three-pairs = سه جفت برای { $points } امتیاز
farkle-take-double-triplets = دو سه‌تایی برای { $points } امتیاز
farkle-take-full-house = چهارتایی با یک جفت برای { $points } امتیاز

farkle-you-roll = شما { $count } { $count ->
    [one] تاس
   *[other] تاس
} می‌اندازید.
farkle-player-rolls = { $player } { $count } { $count ->
    [one] تاس
   *[other] تاس
} می‌اندازد.
farkle-you-roll-brief = شما { $count } می‌اندازید.
farkle-player-rolls-brief = { $player } { $count } می‌اندازد.
farkle-roll-result = تاس‌ها نشان می‌دهند: { $dice }.
farkle-roll-result-brief = تاس‌ها: { $dice }.

farkle-you-farkle = فارکل! شما { $points } امتیاز نوبت را از دست می‌دهید.
farkle-player-farkles = فارکل! { $player } { $points } امتیاز نوبت را از دست می‌دهد.
farkle-you-farkle-brief = فارکل: شما { $points } را از دست دادید.
farkle-player-farkles-brief = فارکل: { $player } { $points } را از دست داد.

farkle-you-take-combo = شما { $combo } را برای { $points } امتیاز نگه می‌دارید.
farkle-player-takes-combo = { $player } { $combo } را برای { $points } امتیاز نگه می‌دارد.
farkle-you-take-combo-brief = شما: { $combo }، +{ $points }.
farkle-player-takes-combo-brief = { $player }: { $combo }، +{ $points }.

farkle-you-hot-dice = تاس‌های داغ! شما هر شش تاس را امتیاز کردید و می‌توانید هر شش را دوباره بندازید.
farkle-player-hot-dice = تاس‌های داغ! { $player } هر شش تاس را امتیاز کرد و می‌تواند هر شش را دوباره بیندازد.
farkle-you-hot-dice-brief = شما: تاس‌های داغ.
farkle-player-hot-dice-brief = { $player }: تاس‌های داغ.

farkle-you-bank = شما { $points } امتیاز ذخیره می‌کنید. مجموع شما اکنون { $total } است.
farkle-player-banks = { $player } { $points } امتیاز ذخیره می‌کند و مجموع او { $total } می‌شود.
farkle-you-bank-brief = شما { $points} ذخیره کردید؛ مجموع { $total }.
farkle-player-banks-brief = { $player } { $points} ذخیره کرد؛ مجموع { $total }.

farkle-you-win = شما با { $score } امتیاز برنده شدید!
farkle-winner = { $player } با { $score } امتیاز برنده شد!
farkle-you-win-brief = شما برنده شدید: { $score }.
farkle-winner-brief = { $player } برنده شد: { $score }.
farkle-winners-tie = تساوی در هدف! بازیکنان تساوی‌شکن: { $players }.
farkle-tiebreaker-round-start = دور تساوی‌شکن { $round }. هنوز در حال رقابت: { $players }.

farkle-your-turn-score = شما در این نوبت { $points } امتیاز دارید.
farkle-turn-score = { $player } در این نوبت { $points } امتیاز دارد.
farkle-no-turn = در حال حاضر هیچ‌کس نوبت ندارد.

farkle-set-target-score = امتیاز هدف: { $score }
farkle-enter-target-score = امتیاز هدف را وارد کنید (۵۰۰-۵۰۰۰):
farkle-option-changed-target = امتیاز هدف روی { $score } تنظیم شد.
farkle-desc-target-score = امتیاز مورد نیاز برای شروع نوبت‌های نهایی فارکل و احتمال برنده شدن (پیش‌فرض ۱۰۰۰، محدوده ۵۰۰-۵۰۰۰).

farkle-set-entrance-score = حداقل امتیاز ورود: { $score }
farkle-enter-entrance-score = حداقل امتیاز ورود را وارد کنید (۰-۵۰۰۰):
farkle-option-changed-entrance = حداقل امتیاز ورود روی { $score } تنظیم شد.
farkle-desc-min-entrance-score = حداقل امتیاز نوبت مورد نیاز برای ذخیره‌ی اولین امتیاز بازیکن. نمی‌تواند از امتیاز هدف بیشتر باشد (پیش‌فرض ۵۰، محدوده ۰-۵۰۰۰).

farkle-set-bank-score = حداقل امتیاز ذخیره: { $score }
farkle-enter-bank-score = حداقل امتیاز ذخیره را وارد کنید (۰-۵۰۰۰):
farkle-option-changed-bank = حداقل امتیاز ذخیره روی { $score } تنظیم شد.
farkle-desc-min-bank-score = حداقل امتیاز نوبت مورد نیاز قبل از در دسترس بودن ذخیره، پس از اینکه بازیکن در تابلو ثبت شد. نمی‌تواند از امتیاز هدف بیشتر باشد (پیش‌فرض ۳۰، محدوده ۰-۵۰۰۰).

farkle-error-entrance-above-target = حداقل امتیاز ورود ({ $entrance }) نمی‌تواند از امتیاز هدف ({ $target }) بیشتر باشد.
farkle-error-bank-above-target = حداقل امتیاز ذخیره ({ $bank }) نمی‌تواند از امتیاز هدف ({ $target }) بیشتر باشد.

farkle-must-take-combo = قبل از پرتاب مجدد باید حداقل یک تاس یا ترکیب امتیازدهنده را نگه دارید.
farkle-cannot-bank = فقط پس از نگه داشتن یک تاس یا ترکیب امتیازدهنده در این نوبت می‌توانید ذخیره کنید.
farkle-must-reach-entrance-score = قبل از ذخیره‌ی اولین امتیاز خود به حداقل { $points } امتیاز نوبت نیاز دارید.
farkle-must-reach-bank-score = قبل از ذخیره به حداقل { $points } امتیاز نوبت نیاز دارید.
farkle-confirm-risky-roll = اکنون می‌توانید { $points } امتیاز را ذخیره کنید. پرتاب مجدد ریسک از دست دادن آنها را دارد؛ برای تأیید، پرتاب را ظرف { $seconds } ثانیه تکرار کنید.
farkle-invalid-combo-action = آن انتخاب امتیازدهی شناسایی نشد. لطفاً یکی از ترکیب‌های لیست‌شده‌ی فعلی را انتخاب کنید.
farkle-combo-no-longer-available = آن ترکیب امتیازدهی دیگر در دسترس نیست. انتخاب‌های امتیازدهی فعلی به‌روزرسانی شدند.

farkle-combo-single-1 = تک ۱
farkle-combo-single-5 = تک ۵
farkle-combo-three-kind = سه { $number }
farkle-combo-four-kind = چهار { $number }
farkle-combo-five-kind = پنج { $number }
farkle-combo-six-kind = شش { $number }
farkle-combo-small-straight = دنباله‌ی کوچک
farkle-combo-large-straight = دنباله‌ی بزرگ
farkle-combo-three-pairs = سه جفت
farkle-combo-double-triplets = دو سه‌تایی
farkle-combo-full-house = چهارتایی با یک جفت

farkle-line-format = { $rank }. { $player }: { $points }
farkle-combo-fallback = { $combo } برای { $points } امتیاز

farkle-check-turn-score = بررسی امتیاز نوبت
farkle-roll-label = پرتاب تاس
farkle-bank-label = ذخیره‌ی امتیاز