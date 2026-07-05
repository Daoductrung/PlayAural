game-name-chess = شطرنج

chess-set-time-control = کنترل زمان: { $control }
chess-select-time-control = یک کنترل زمان را انتخاب کنید
chess-option-changed-time-control = کنترل زمان روی { $control } تنظیم شد.
chess-desc-time-control = ساعت شطرنج را انتخاب می‌کند، از بازی بدون زمان تا کنترل‌های بولت، بلیتز، رپید یا کلاسیک.
chess-time-untimed = بدون زمان
chess-time-bullet-1-0 = بولت ۱+۰
chess-time-bullet-2-1 = بولت ۲+۱
chess-time-blitz-3-0 = بلیتز ۳+۰
chess-time-blitz-3-2 = بلیتز ۳+۲
chess-time-blitz-5-0 = بلیتز ۵+۰
chess-time-rapid-10-0 = رپید ۱۰+۰
chess-time-rapid-10-5 = رپید ۱۰+۵
chess-time-classical-30-0 = کلاسیک ۳۰+۰

chess-set-draw-handling = نحوه‌ی تساوی: { $mode }
chess-select-draw-handling = نحوه‌ی تساوی را انتخاب کنید
chess-option-changed-draw-handling = نحوه‌ی تساوی روی { $mode } تنظیم شد.
chess-desc-draw-handling = انتخاب می‌کند که قوانین تساوی خودکار بلافاصله بازی را پایان دهند یا نیاز به درخواست بازیکن داشته باشند.
chess-draw-handling-automatic = خودکار
chess-draw-handling-claim-required = نیاز به درخواست

chess-toggle-draw-offers = اجازه‌ی پیشنهاد تساوی: { $enabled }
chess-option-changed-draw-offers = اجازه‌ی پیشنهاد تساوی روی { $enabled } تنظیم شد.
chess-desc-allow-draw-offers = کنترل می‌کند که آیا بازیکنان می‌توانند تساوی توافقی پیشنهاد داده و به آن پاسخ دهند.
chess-toggle-undo-requests = اجازه‌ی درخواست برگشت: { $enabled }
chess-option-changed-undo-requests = اجازه‌ی درخواست برگشت روی { $enabled } تنظیم شد.
chess-desc-allow-undo-requests = کنترل می‌کند که آیا بازیکنان می‌توانند درخواست برگشت حرکت بدهند که حریف می‌تواند بپذیرد یا رد کند.
chess-error-invalid-time-control = کنترل زمان انتخاب‌شده "{ $control }" برای شطرنج پشتیبانی نمی‌شود.
chess-error-invalid-draw-handling = نحوه‌ی تساوی انتخاب‌شده "{ $mode }" برای شطرنج پشتیبانی نمی‌شود.

chess-read-board = مشاهده‌ی صفحه
chess-check-status = بررسی وضعیت
chess-flip-board = چرخاندن صفحه
chess-check-clock = بررسی ساعت
chess-claim-draw = درخواست تساوی
chess-offer-draw = پیشنهاد تساوی
chess-accept-draw = پذیرش تساوی
chess-decline-draw = رد تساوی
chess-request-undo = درخواست برگشت
chess-accept-undo = پذیرش برگشت
chess-decline-undo = رد برگشت
chess-type-move = تایپ حرکت
chess-enter-move = حرکت خود را تایپ کنید، مانند e2e4، Nf3، O-O، یا e8=Q

chess-promote-queen = ترفیع به وزیر
chess-promote-rook = ترفیع به رخ
chess-promote-bishop = ترفیع به فیل
chess-promote-knight = ترفیع به اسب

chess-color-white = سفید
chess-color-black = سیاه

chess-piece-pawn = سرباز
chess-piece-knight = اسب
chess-piece-bishop = فیل
chess-piece-rook = رخ
chess-piece-queen = وزیر
chess-piece-king = شاه
chess-piece-with-color = { $color } { $piece }

chess-square-empty-label = { $square }، خالی
chess-square-piece-label = { $square }، { $piece }
chess-square-selected-label = انتخاب شد، { $label }
chess-square-move-target = { $square }، حرکت قانونی
chess-square-capture-target = { $square }، گرفتن { $piece }
chess-square-empty = { $square } خالی است.
chess-square-occupied = { $square }: { $piece }.

chess-select-own-piece = ابتدا یکی از مهره‌های خود را انتخاب کنید.
chess-piece-no-legal-moves = آن مهره حرکت قانونی ندارد.
chess-piece-selected = { $piece } در { $square } انتخاب شد. { $count } حرکت قانونی در دسترس است.
chess-selection-cleared = انتخاب پاک شد.
chess-illegal-move = حرکت غیرقانونی.
chess-invalid-castle = قلعه رفتن در آنجا قانونی نیست.
chess-promotion-pending = ابتدا یک مهره برای ترفیع انتخاب کنید.
chess-choose-promotion = یک مهره برای ترفیع انتخاب کنید.
chess-typed-move-empty = قبل از ارسال، یک حرکت تایپ کنید.
chess-typed-move-parse-error = نتوانستم "{ $move }" را به عنوان حرکت شطرنج درک کنم. از نماد مختصات مانند e2e4، نماد جبری مانند Nf3، قلعه رفتن مانند O-O، یا ترفیع مانند e8=Q استفاده کنید.
chess-typed-move-ambiguous = "{ $move }" با بیش از یک حرکت قانونی مطابقت دارد. ستون، ردیف یا خانه‌ی کامل شروع را اضافه کنید، مانند Nbd2 یا Rae1.
chess-typed-move-illegal = "{ $move }" در موقعیت فعلی قانونی نیست.
chess-typed-move-bad-promotion = "{ $move }" شامل یک مهره‌ی ترفیع است، اما ترفیع فقط زمانی کار می‌کند که یکی از سربازان شما به ردیف آخر برسد. از وزیر، رخ، فیل یا اسب استفاده کنید.

chess-game-started = شطرنج آغاز شد. { $white } سفید است. { $black } سیاه است.
chess-you-win-checkmate = کیش‌مات. شما برنده شدید.
chess-player-wins-checkmate = کیش‌مات. { $player } برنده شد.
chess-draw = تساوی.
chess-draw-stalemate = تساوی به دلیل پات.
chess-draw-fifty-move = تساوی به دلیل قانون ۵۰ حرکت.
chess-draw-seventy-five-move = تساوی به دلیل قانون اجباری ۷۵ حرکت.
chess-draw-threefold = تساوی به دلیل تکرار سه‌باره.
chess-draw-fivefold = تساوی به دلیل تکرار اجباری پنج‌باره.
chess-draw-insufficient-material = تساوی به دلیل مواد ناکافی.
chess-draw-agreement = تساوی توافقی.
chess-draw-timeout-insufficient = تساوی. وقت حریف تمام شد، اما مواد کافی برای کیش‌مات وجود نداشت.
chess-you-are-in-check = شاه شما در کیش است.
chess-player-is-in-check = شاه { $player } در کیش است.
chess-you-lose-on-time = وقت شما تمام شد. { $winner } به دلیل وقت برنده شد.
chess-player-loses-on-time = وقت { $player } تمام شد. { $winner } به دلیل وقت برنده شد.

chess-you-en-passant = شما { $piece } خود را از { $from_square } به { $to_square } حرکت می‌دهید و به‌صورت آن‌پاسان می‌گیرید.
chess-player-en-passant = { $player } { $piece } خود را از { $from_square } به { $to_square } حرکت می‌دهد و به‌صورت آن‌پاسان می‌گیرد.
chess-you-en-passant-brief = شما { $from_square } x { $to_square } آن‌پاسان.
chess-player-en-passant-brief = { $player } { $from_square } x { $to_square } آن‌پاسان.
chess-you-capture = شما { $piece } خود را از { $from_square } به { $to_square } حرکت می‌دهید و { $captured_piece } را می‌گیرید.
chess-player-captures = { $player } { $piece } خود را از { $from_square } به { $to_square } حرکت می‌دهد و { $captured_piece } را می‌گیرد.
chess-you-capture-brief = شما { $from_square } x { $to_square }.
chess-player-captures-brief = { $player } { $from_square } x { $to_square }.
chess-you-castle-kingside = شما در سمت شاه قلعه می‌روید.
chess-player-castles-kingside = { $player } در سمت شاه قلعه می‌رود.
chess-you-castle-kingside-brief = شما O-O.
chess-player-castles-kingside-brief = { $player } O-O.
chess-you-castle-queenside = شما در سمت وزیر قلعه می‌روید.
chess-player-castles-queenside = { $player } در سمت وزیر قلعه می‌رود.
chess-you-castle-queenside-brief = شما O-O-O.
chess-player-castles-queenside-brief = { $player } O-O-O.
chess-you-move = شما { $piece } خود را از { $from_square } به { $to_square } حرکت می‌دهید.
chess-player-moves = { $player } { $piece } خود را از { $from_square } به { $to_square } حرکت می‌دهد.
chess-you-move-brief = شما { $from_square } { $to_square }.
chess-player-moves-brief = { $player } { $from_square } { $to_square }.
chess-you-promote = شما در { $square } ترفیع می‌کنید.
chess-player-promotes = { $player } در { $square } ترفیع می‌کند.
chess-you-promote-to = شما سرباز را در { $square } به { $piece } ترفیع می‌دهید.
chess-player-promotes-to = { $player } سرباز را در { $square } به { $piece } ترفیع می‌دهد.
chess-you-promote-to-brief = شما در { $square } به { $piece } ترفیع می‌کنید.
chess-player-promotes-to-brief = { $player } در { $square } به { $piece } ترفیع می‌کند.
chess-you-offer-draw = شما تساوی پیشنهاد می‌دهید.
chess-player-offers-draw = { $player } تساوی پیشنهاد می‌دهد.
chess-you-accept-draw = شما تساوی را می‌پذیرید.
chess-player-accepts-draw = { $player } تساوی را می‌پذیرد.
chess-you-decline-draw = شما تساوی را رد می‌کنید.
chess-player-declines-draw = { $player } تساوی را رد می‌کند.
chess-you-request-undo = شما درخواست برگشت می‌دهید.
chess-player-requests-undo = { $player } درخواست برگشت می‌دهد.
chess-you-accept-undo = شما درخواست برگشت را می‌پذیرید.
chess-player-accepts-undo = { $player } درخواست برگشت را می‌پذیرد.
chess-you-decline-undo = شما درخواست برگشت را رد می‌کنید.
chess-player-declines-undo = { $player } درخواست برگشت را رد می‌کند.
chess-draw-offer-too-early = پیشنهاد تساوی فقط پس از اینکه هر دو بازیکن حداقل یک حرکت انجام داده‌اند در دسترس است.
chess-claim-available-fifty-move = تساوی ۵۰ حرکت قابل درخواست است.
chess-claim-available-threefold = تساوی تکرار سه‌باره قابل درخواست است.
chess-you-claim-draw-fifty-move = شما تساوی به دلیل قانون ۵۰ حرکت را درخواست می‌کنید.
chess-draw-claimed-fifty-move = { $player } تساوی به دلیل قانون ۵۰ حرکت را درخواست می‌کند.
chess-you-claim-draw-threefold = شما تساوی به دلیل تکرار سه‌باره را درخواست می‌کنید.
chess-draw-claimed-threefold = { $player } تساوی به دلیل تکرار سه‌باره را درخواست می‌کند.

chess-status-white = سفید: { $player }
chess-status-black = سیاه: { $player }
chess-status-turn = نوبت: { $color } ({ $player })
chess-status-move-count = تعداد حرکت‌های کامل: { $count }. نیم‌حرکت‌های انجام‌شده: { $plies }.
chess-status-promotion-pending = انتخاب ترفیع در انتظار است.
chess-status-check = طرفی که نوبت دارد در کیش است.
chess-status-time-control = کنترل زمان: { $control }
chess-status-draw-offer = پیشنهاد تساوی از { $player } در انتظار است.
chess-status-undo-request = درخواست برگشت از { $player } در انتظار است.
chess-clock-line = ساعت { $color }: { $time }
chess-clock-untimed = نامحدود
chess-clock-announcement = سفید { $white }. سیاه { $black }.
chess-clock-announcement-untimed = این بازی بدون زمان است.

chess-board-flipped = صفحه به سمت { $color } چرخانده شد.
chess-empty = خالی
chess-board-rank-line = ردیف { $rank }: { $pieces }

chess-end-winner = { $player } به عنوان { $color } برنده شد.
chess-end-move-count = تعداد حرکت‌های کامل: { $count }. نیم‌حرکت‌های انجام‌شده: { $plies }.