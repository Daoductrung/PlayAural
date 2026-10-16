game-name-chess = الشطرنج

chess-set-time-control = التحكّم بالوقت: { $control }
chess-select-time-control = اختر التحكّم بالوقت
chess-option-changed-time-control = ضُبط التحكّم بالوقت على { $control }.
chess-desc-time-control = يختار ساعة الشطرنج، من اللعب بلا توقيت إلى أنماط البوليت أو البليتز أو السريع أو الكلاسيكي.
chess-time-untimed = بلا توقيت
chess-time-bullet-1-0 = بوليت 1+0
chess-time-bullet-2-1 = بوليت 2+1
chess-time-blitz-3-0 = بليتز 3+0
chess-time-blitz-3-2 = بليتز 3+2
chess-time-blitz-5-0 = بليتز 5+0
chess-time-rapid-10-0 = سريع 10+0
chess-time-rapid-10-5 = سريع 10+5
chess-time-classical-30-0 = كلاسيكي 30+0

chess-set-draw-handling = معالجة التعادل: { $mode }
chess-select-draw-handling = اختر معالجة التعادل
chess-option-changed-draw-handling = ضُبطت معالجة التعادل على { $mode }.
chess-desc-draw-handling = يختار ما إذا كانت قواعد التعادل التلقائية تنهي اللعبة فورًا أم تتطلب من اللاعب المطالبة بالتعادل.
chess-draw-handling-automatic = تلقائي
chess-draw-handling-claim-required = يتطلب مطالبة

chess-toggle-draw-offers = السماح بعروض التعادل: { $enabled }
chess-option-changed-draw-offers = ضُبط السماح بعروض التعادل على { $enabled }.
chess-desc-allow-draw-offers = يتحكّم في ما إذا كان بإمكان اللاعبين تقديم عروض التعادل والردّ عليها.
chess-toggle-undo-requests = السماح بطلبات التراجع: { $enabled }
chess-option-changed-undo-requests = ضُبط السماح بطلبات التراجع على { $enabled }.
chess-desc-allow-undo-requests = يتحكّم في ما إذا كان بإمكان اللاعبين طلب التراجع عن النقلات ليقبله الخصم أو يرفضه.
chess-error-invalid-time-control = التحكّم بالوقت المختار "{ $control }" غير مدعوم في الشطرنج.
chess-error-invalid-draw-handling = نمط معالجة التعادل المختار "{ $mode }" غير مدعوم في الشطرنج.

chess-read-board = اقرأ اللوحة
chess-check-status = حالة الكش
chess-flip-board = اقلب اللوحة
chess-check-clock = تحقّق من الساعة
chess-claim-draw = طالِب بالتعادل
chess-offer-draw = اعرض التعادل
chess-accept-draw = اقبل التعادل
chess-decline-draw = ارفض التعادل
chess-request-undo = اطلب التراجع
chess-accept-undo = اقبل التراجع
chess-decline-undo = ارفض التراجع
chess-type-move = اكتب النقلة
chess-enter-move = اكتب نقلتك، مثل e2e4 أو Nf3 أو O-O أو e8=Q

chess-promote-queen = الترقية إلى وزير
chess-promote-rook = الترقية إلى رخ
chess-promote-bishop = الترقية إلى فيل
chess-promote-knight = الترقية إلى حصان

chess-color-white = أبيض
chess-color-black = أسود

chess-piece-pawn = بيدق
chess-piece-knight = حصان
chess-piece-bishop = فيل
chess-piece-rook = رخ
chess-piece-queen = وزير
chess-piece-king = ملك
chess-piece-with-color = { $piece } { $color }

chess-square-empty-label = { $square }، فارغ
chess-square-piece-label = { $square }، { $piece }
chess-square-selected-label = محدَّد، { $label }
chess-square-move-target = { $square }، نقلة قانونية
chess-square-capture-target = { $square }، أسر { $piece }
chess-square-empty = { $square } فارغ.
chess-square-occupied = { $square }: { $piece }.

chess-select-own-piece = اختر إحدى قطعك أولًا.
chess-piece-no-legal-moves = لا توجد نقلات قانونية لهذه القطعة.
chess-piece-selected = حُدّد { $piece } على { $square }. { $count } نقلات قانونية متاحة.
chess-selection-cleared = أُلغي التحديد.
chess-illegal-move = نقلة غير قانونية.
chess-invalid-castle = التبييت غير قانوني هناك.
chess-promotion-pending = اختر قطعة للترقية أولًا.
chess-choose-promotion = اختر قطعة الترقية.
chess-typed-move-empty = اكتب نقلة قبل الإرسال.
chess-typed-move-parse-error = لم أتمكّن من فهم "{ $move }" كنقلة شطرنج. جرّب الترميز الإحداثي مثل e2e4، أو الترميز الجبري مثل Nf3، أو التبييت مثل O-O، أو الترقية مثل e8=Q.
chess-typed-move-ambiguous = "{ $move }" يطابق أكثر من نقلة قانونية. أضف عمود البداية أو صفه أو مربع البداية الكامل، مثل Nbd2 أو Rae1.
chess-typed-move-illegal = "{ $move }" غير قانونية في الوضع الحالي.
chess-typed-move-bad-promotion = "{ $move }" يتضمّن قطعة ترقية، لكن الترقية تعمل فقط عندما يصل أحد بيادقك إلى الصف الأخير. استخدم وزير أو رخ أو فيل أو حصان.

chess-game-started = يبدأ الشطرنج. { $white } يلعب بالأبيض. { $black } يلعب بالأسود.
chess-you-win-checkmate = كش ملك. أنت تفوز.
chess-player-wins-checkmate = كش ملك. يفوز { $player }.
chess-draw = تعادل.
chess-draw-stalemate = تعادل بالحصار.
chess-draw-fifty-move = تعادل بقاعدة الخمسين نقلة.
chess-draw-seventy-five-move = تعادل بقاعدة الخمس والسبعين نقلة الإلزامية.
chess-draw-threefold = تعادل بالتكرار الثلاثي.
chess-draw-fivefold = تعادل بالتكرار الخماسي الإلزامي.
chess-draw-insufficient-material = تعادل لعدم كفاية العتاد.
chess-draw-agreement = تعادل بالاتفاق.
chess-draw-timeout-insufficient = تعادل. نفد وقت الخصم، لكن لم يكن هناك عتاد كافٍ لكش الملك.
chess-you-are-in-check = ملكك في كش.
chess-player-is-in-check = ملك { $player } في كش.
chess-you-lose-on-time = نفد وقتك. يفوز { $winner } بالوقت.
chess-player-loses-on-time = نفد وقت { $player }. يفوز { $winner } بالوقت.

chess-you-en-passant = تنقل { $piece } الخاص بك من { $from_square } إلى { $to_square } وتأسر بالأخذ بالتجاوز.
chess-player-en-passant = ينقل { $player } { $piece } { GENDER_TERM($player_gender, "possessive-determiner") } من { $from_square } إلى { $to_square } ويأسر بالأخذ بالتجاوز.
chess-you-en-passant-brief = أنت { $from_square } x { $to_square } تجاوز
chess-player-en-passant-brief = { $player } { $from_square } x { $to_square } تجاوز
chess-you-capture = تنقل { $piece } الخاص بك من { $from_square } إلى { $to_square }، آسرًا { $captured_piece }.
chess-player-captures = ينقل { $player } { $piece } { GENDER_TERM($player_gender, "possessive-determiner") } من { $from_square } إلى { $to_square }، آسرًا { $captured_piece }.
chess-you-capture-brief = أنت { $from_square } x { $to_square }.
chess-player-captures-brief = { $player } { $from_square } x { $to_square }.
chess-you-castle-kingside = تُبيّت على جهة الملك.
chess-player-castles-kingside = يُبيّت { $player } على جهة الملك.
chess-you-castle-kingside-brief = أنت O-O.
chess-player-castles-kingside-brief = { $player } O-O.
chess-you-castle-queenside = تُبيّت على جهة الوزير.
chess-player-castles-queenside = يُبيّت { $player } على جهة الوزير.
chess-you-castle-queenside-brief = أنت O-O-O.
chess-player-castles-queenside-brief = { $player } O-O-O.
chess-you-move = تنقل { $piece } الخاص بك من { $from_square } إلى { $to_square }.
chess-player-moves = ينقل { $player } { $piece } { GENDER_TERM($player_gender, "possessive-determiner") } من { $from_square } إلى { $to_square }.
chess-you-move-brief = أنت { $from_square } { $to_square }.
chess-player-moves-brief = { $player } { $from_square } { $to_square }.
chess-you-promote = تُرقّي على { $square }.
chess-player-promotes = يُرقّي { $player } على { $square }.
chess-you-promote-to = تُرقّي البيدق على { $square } إلى { $piece }.
chess-player-promotes-to = يُرقّي { $player } البيدق على { $square } إلى { $piece }.
chess-you-promote-to-brief = تُرقّي { $square } إلى { $piece }.
chess-player-promotes-to-brief = يُرقّي { $player } { $square } إلى { $piece }.
chess-you-offer-draw = تعرض التعادل.
chess-player-offers-draw = يعرض { $player } التعادل.
chess-you-accept-draw = تقبل التعادل.
chess-player-accepts-draw = يقبل { $player } التعادل.
chess-you-decline-draw = ترفض التعادل.
chess-player-declines-draw = يرفض { $player } التعادل.
chess-you-request-undo = تطلب التراجع.
chess-player-requests-undo = يطلب { $player } التراجع.
chess-you-accept-undo = تقبل طلب التراجع.
chess-player-accepts-undo = يقبل { $player } طلب التراجع.
chess-you-decline-undo = ترفض طلب التراجع.
chess-player-declines-undo = يرفض { $player } طلب التراجع.
chess-draw-offer-too-early = عروض التعادل متاحة فقط بعد أن يؤدّي كلا اللاعبين نقلة واحدة على الأقل.
chess-claim-available-fifty-move = يمكن المطالبة بتعادل الخمسين نقلة الآن.
chess-claim-available-threefold = يمكن المطالبة بالتعادل بالتكرار الثلاثي الآن.
chess-you-claim-draw-fifty-move = تطالب بتعادل بقاعدة الخمسين نقلة.
chess-draw-claimed-fifty-move = يطالب { $player } بتعادل بقاعدة الخمسين نقلة.
chess-you-claim-draw-threefold = تطالب بتعادل بالتكرار الثلاثي.
chess-draw-claimed-threefold = يطالب { $player } بتعادل بالتكرار الثلاثي.

chess-status-white = الأبيض: { $player }
chess-status-black = الأسود: { $player }
chess-status-turn = الدور: { $color } ({ $player })
chess-status-move-count = النقلات الكاملة المنجزة: { $count }. أنصاف النقلات الملعوبة: { $plies }.
chess-status-promotion-pending = هناك اختيار ترقية معلّق.
chess-status-check = الجهة صاحبة الدور في كش.
chess-status-time-control = التحكّم بالوقت: { $control }
chess-status-draw-offer = عرض تعادل بانتظار الردّ من { $player }.
chess-status-undo-request = طلب تراجع بانتظار الردّ من { $player }.
chess-clock-line = ساعة { $color }: { $time }
chess-clock-untimed = غير محدود
chess-clock-announcement = الأبيض { $white }. الأسود { $black }.
chess-clock-announcement-untimed = هذه اللعبة بلا توقيت.

chess-board-flipped = قُلبت اللوحة إلى جهة { $color }.
chess-empty = فارغ
chess-board-rank-line = الصف { $rank }: { $pieces }

chess-end-winner = يفوز { $player } بالـ { $color }.
chess-end-move-count = النقلات الكاملة المنجزة: { $count }. أنصاف النقلات الملعوبة: { $plies }.
