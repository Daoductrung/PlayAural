# Nine - پیام‌های بازی

# نام و توضیحات بازی
game-name-nine = ناین
nine-description = یک بازی کارتی محبوب روسی که در آن بازیکنان دنباله‌های خال می‌سازند.

# اعتبارسنجی تعداد بازیکنان
nine-error-invalid-player-count = ناین از یک دسته‌ی ۳۶ کارتی استفاده می‌کند و دقیقاً ۳، ۴ یا ۶ بازیکن را می‌پذیرد.
nine-error-starting-nine-missing = نه‌ی خشت در هیچ دستی پیدا نشد. بازی نمی‌تواند ادامه یابد.

# پیام‌های پخش کارت
nine-player-nine-deal = پخش { $cards } کارت به هر بازیکن.

# شروع بازی
nine-you-start-player-announcement = شما نه‌ی خشت را دارید و بازی را شروع می‌کنید.
nine-player-start-player-announcement = { $player } نه‌ی خشت را دارد و بازی را شروع می‌کند.
nine-you-start-player-announcement-brief = شما با نه‌ی خشت شروع می‌کنید.
nine-player-start-player-announcement-brief = { $player } با نه‌ی خشت شروع می‌کند.

# اقدامات نوبت
nine-you-plays-starting-nine = شما { $card } را بازی می‌کنید تا میز را باز کنید.
nine-player-plays-starting-nine = { $player } { $card } را بازی می‌کند تا میز را باز کند.
nine-you-plays-starting-nine-brief = شما { $card } بازی کردید.
nine-player-plays-starting-nine-brief = { $player }: { $card }.

nine-you-plays-nine-suit = شما { $card } را بازی می‌کنید تا دنباله‌ی { $suit } را شروع کنید.
nine-player-plays-nine-suit = { $player } { $card } را بازی می‌کند تا دنباله‌ی { $suit } را شروع کند.
nine-you-plays-nine-suit-brief = شما { $suit } را با { $card } شروع کردید.
nine-player-plays-nine-suit-brief = { $player } { $suit } را با { $card } شروع کرد.

nine-you-extend-sequence = شما دنباله‌ی { $suit } را با { $card } ادامه می‌دهید.
nine-player-extend-sequence = { $player } دنباله‌ی { $suit } را با { $card } ادامه می‌دهد.
nine-you-extend-sequence-brief = شما { $card } را روی { $suit } بازی کردید.
nine-player-extend-sequence-brief = { $player }: { $card } روی { $suit }.

nine-you-skips-turn = شما کارت قانونی برای بازی ندارید، بنابراین نوبت شما رد می‌شود.
nine-player-skips-turn = { $player } کارت قانونی برای بازی ندارد و نوبت او رد می‌شود.
nine-you-skips-turn-brief = شما رد شدید؛ کارت قانونی ندارید.
nine-player-skips-turn-brief = { $player } رد شد؛ کارت قانونی ندارد.

# دلایل عدم امکان بازی کارت
nine-reason-not-your-turn = نوبت شما نیست.
nine-reason-card-slot-gone = آن کارت دیگر در دست شما نیست. منوی دست شما به‌روزرسانی شد.
nine-reason-must-play-starting-nine = اولین بازی باید { $starting_card } باشد. { $card } تا زمانی که میز باز نشود قابل بازی نیست.
nine-reason-nine-already-started = { $card } قابل بازی نیست چون دنباله‌ی { $suit } قبلاً باز شده است.
nine-reason-cannot-extend = { $card } نمی‌تواند دنباله‌ی { $suit } را ادامه دهد. کارت بعدی پایین‌تر یا بالاتر را در یکی از انتهای آن دنباله بازی کنید.
nine-reason-unopened-suit = { $card } قابل بازی نیست چون دنباله‌ی { $suit } هنوز باز نشده است. ابتدا آن خال را با ۹ آن شروع کنید.
nine-reason-must-skip = شما کارت قانونی برای بازی ندارید؛ نوبت شما به‌طور خودکار رد می‌شود.
nine-reason-generic = آن کارت در حال حاضر قابل بازی نیست.

# برنده شدن
nine-you-wins-game = شما دیگر کارتی ندارید و بازی را برنده شدید!
nine-player-wins-game = { $player } دیگر کارتی ندارد و بازی را برنده شد!
nine-you-wins-game-brief = شما برنده شدید!
nine-player-wins-game-brief = { $player } برنده شد!
nine-player-game-ended = بازی ناین به پایان رسید.
nine-you-game-ended = بازی ناین به پایان رسید.

nine-you-win = شما برنده شدید!
nine-you-lose = شما باختید!
nine-final-score = کارت‌های باقی‌مانده: { $score }

# وضعیت
nine-status = { $name }: { $cards_left } کارت باقی‌مانده.
nine-status-sequence = دنباله‌ی { $suit }: { $sequence }.
nine-status-no-sequence = هیچ دنباله‌ای برای { $suit } شروع نشده است.
nine-sequence-range = { $low } تا { $high }
nine-none = هیچ
nine-action-check-sequences = بررسی دنباله‌ها
nine-action-check-hand-counts = بررسی تعداد کارت‌های دست
nine-status-player-hand-count = { $player }: { $count } کارت