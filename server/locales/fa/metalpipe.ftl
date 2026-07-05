# Metal Pipe - پیام‌های بازی

game-name-metalpipe = لوله‌ی فلزی

metalpipe-mode-single = تک‌ضربه
metalpipe-mode-multiple = چندضربه
metalpipe-self-bonk-allowed = خودضربه مجاز است
metalpipe-self-bonk-blocked = خودضربه ممنوع است

metalpipe-game-start = لوله‌ی فلزی در حالت { $mode } آغاز می‌شود. لوله همه چیز را به‌طور خودکار انتخاب می‌کند.
metalpipe-game-start-brief = لوله‌ی فلزی: { $mode }.

metalpipe-you-hit-other = شما لوله‌ی فلزی را می‌چرخانید و به { $bonked } می‌زنید. { $bonked } حذف شد.
metalpipe-player-hits-you = { $bonker } لوله‌ی فلزی را می‌چرخاند و به شما می‌زند. شما حذف شدید.
metalpipe-player-hits-other = { $bonker } لوله‌ی فلزی را می‌چرخاند و به { $bonked } می‌زند. { $bonked } حذف شد.
metalpipe-you-hit-self = شما به نوعی با لوله‌ی فلزی به خودتان می‌زنید و حذف می‌شوید.
metalpipe-player-hits-self = { $bonker } به نوعی با لوله‌ی فلزی به خودش می‌زند و حذف می‌شود.

metalpipe-you-hit-other-brief = شما به { $bonked } زدید. { $bonked } خارج شد.
metalpipe-player-hits-you-brief = { $bonker } به شما زد. شما خارج شدید.
metalpipe-player-hits-other-brief = { $bonker } به { $bonked } زد. { $bonked } خارج شد.
metalpipe-you-hit-self-brief = شما خودضربه زدید. خارج شدید.
metalpipe-player-hits-self-brief = { $bonker } خودضربه زد. خارج شد.

metalpipe-you-win = شما برنده شدید. لوله‌ی فلزی نظر خود را گفت.
metalpipe-you-win-with-others = شما همراه با { $players } برنده شدید. لوله‌ی فلزی نظر خود را گفت.
metalpipe-players-win = { $players } برنده شدند. لوله‌ی فلزی نظر خود را گفت.
metalpipe-you-win-brief = شما برنده شدید.
metalpipe-you-win-with-others-brief = شما و { $players } برنده شدید.
metalpipe-players-win-brief = برندگان: { $players }.
metalpipe-no-winner = لوله‌ی فلزی هیچ برنده‌ای باقی نمی‌گذارد.
metalpipe-no-winner-brief = بدون برنده.

metalpipe-check-status = مشاهده‌ی وضعیت لوله
metalpipe-status-mode = حالت: { $mode }; { $self_bonk }.
metalpipe-status-progress = ضربه‌های انجام‌شده: { $count }. بازیکنان باقی‌مانده: { $alive } از { $total }.
metalpipe-status-awaiting = لوله هنوز فرود نیامده است.
metalpipe-status-last-other = آخرین ضربه: { $bonker } به { $bonked } زد.
metalpipe-status-last-self = آخرین ضربه: { $bonker } به خودش زد.
metalpipe-status-player = { $player}: { $status }.
metalpipe-status-alive = ایستاده
metalpipe-status-eliminated = حذف شد
metalpipe-no-turn-automatic = لوله‌ی فلزی به‌طور خودکار در حال تصمیم‌گیری است. { $alive } بازیکن هنوز ایستاده‌اند و هیچ بازیکنی نوبت دستی ندارد.

metalpipe-final-results = نتایج لوله‌ی فلزی
metalpipe-end-winner = برنده: { $player }.
metalpipe-end-winners = برندگان: { $players }.
metalpipe-line-format = { $player}: { $status }

metalpipe-set-multiple-bonks = چندضربه: { $enabled }
metalpipe-option-changed-multiple-bonks = چندضربه روی { $enabled } تنظیم شد.
metalpipe-desc-multiple-bonks = وقتی فعال باشد، لوله به انتخاب ضربه‌زننده و هدف ادامه می‌دهد تا زمانی که فقط یک بازیکن باقی بماند (پیش‌فرض خاموش).
metalpipe-set-allow-self-bonk = اجازه‌ی خودضربه: { $enabled }
metalpipe-option-changed-allow-self-bonk = اجازه‌ی خودضربه روی { $enabled } تنظیم شد.
metalpipe-desc-allow-self-bonk = وقتی فعال باشد، ضربه‌زننده‌ی انتخاب‌شده به‌طور تصادفی می‌تواند هدف نیز باشد (پیش‌فرض روشن).