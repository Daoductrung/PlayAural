game-name-skipbo = سكيب-بو

skipbo-stock-mode-standard = قياسي (30 أو 20 بطاقة)
skipbo-stock-mode-short = سريع 10 بطاقات
skipbo-stock-mode-short-15 = سريع 15 بطاقة
skipbo-scoring-single = لعبة واحدة
skipbo-scoring-match = مباراة محتسَبة

skipbo-set-stock-mode = أكوام المخزون: { $mode }
skipbo-select-stock-mode = اختر طول كومة المخزون:
skipbo-option-changed-stock-mode = أصبحت أكوام المخزون تستخدم { $mode }.
skipbo-desc-stock-mode = يستخدم الوضع القياسي 30 بطاقة مخزون مع لاعبين من 2 إلى 4، و20 مع 5 أو 6 لاعبين. تستخدم الألعاب السريعة 10 أو 15 بطاقة مخزون لكل لاعب.

skipbo-set-scoring-mode = صيغة المباراة: { $mode }
skipbo-select-scoring-mode = اختر صيغة المباراة:
skipbo-option-changed-scoring-mode = أصبحت صيغة المباراة { $mode }.
skipbo-desc-scoring-mode = تنتهي اللعبة الواحدة عندما يُفرّغ لاعب أو شراكة أكوام مخزونه. تستمر المباراة المحتسَبة عبر الألعاب حتى يبلغ أحدهم النتيجة الهدف.

skipbo-set-winning-score = هدف المباراة: { $score } نقطة
skipbo-enter-winning-score = أدخل هدف المباراة من 25 إلى 5000 نقطة:
skipbo-option-changed-winning-score = أصبح هدف المباراة { $score } نقطة.
skipbo-desc-winning-score = النقاط اللازمة للفوز بمباراة محتسَبة. الهدف الرسمي هو 500 نقطة.
skipbo-desc-team-mode = الوضع الفردي يمنح كل لاعب كومة مخزون ونتيجة منفصلة. الشراكات الرسمية تستخدم فرقًا من اثنين؛ يجوز للشريكين اللعب من أكوام مخزون ورمي أيٍّ منهما، لكن ليس من يد أحدهما الآخر.

skipbo-card-number = { $value }
skipbo-card-wild = سكيب-بو متغيّرة
skipbo-card-wild-as = سكيب-بو بقيمة { $value }

skipbo-source-your-hand = يدك
skipbo-source-player-hand = يد { $owner }
skipbo-source-your-stock = كومة مخزونك
skipbo-source-player-stock = كومة مخزون { $owner }
skipbo-source-your-discard = كومة رميك { $pile }
skipbo-source-player-discard = كومة رمي { $owner } { $pile }

skipbo-action-source-hand = اليد
skipbo-action-source-stock = المخزون
skipbo-action-source-player-stock = مخزون { $owner }
skipbo-action-source-discard = كومة الرمي { $pile }
skipbo-action-source-player-discard = كومة رمي { $owner } { $pile }

skipbo-play-action = { $card } — { $source } إلى الكومة { $pile }
skipbo-card-action = { $card } — { $source }
skipbo-card-desc-play-or-discard = أكوام البناء المتاحة: { $piles }. اختر البطاقة للعبها أو رميها وإنهاء دورك.
skipbo-card-desc-discard-only = اختر البطاقة لرميها وإنهاء دورك.
skipbo-card-desc-choose-building = أكوام البناء المتاحة: { $piles }. اختر البطاقة لتحديد واحدة.
skipbo-end-turn-empty = إنهاء الدور دون رمي
skipbo-end-turn-empty-desc = يدك فارغة ولا يمكن سحب أي بطاقة، لذا لا يمكن الرمي.
skipbo-select-card-move = اختر إلى أين تنقل هذه البطاقة:
skipbo-move-building-empty = كومة البناء { $pile}: فارغة؛ العب { $card }
skipbo-move-building-top = كومة البناء { $pile}: { $current } في الأعلى؛ العب { $card }
skipbo-move-discard-empty = كومة الرمي { $pile}: فارغة؛ ارمِ هنا وأنهِ الدور
skipbo-move-discard-top = كومة الرمي { $pile}: { $top } في الأعلى؛ ارمِ هنا وأنهِ الدور

skipbo-read-building-piles = عرض أكوام البناء
skipbo-read-stock-piles = عرض أكوام المخزون
skipbo-read-own-discard-piles = عرض أكوام رميك
skipbo-read-discard-piles = عرض أكوام رمي لاعب آخر
skipbo-select-discard-owner = اختر أكوام رمي مَن تريد عرضها:

skipbo-game-start = تبدأ اللعبة. كل كومة مخزون تحتوي على { $stock_count } بطاقة.
skipbo-game-start-quick = تبدأ اللعبة السريعة. كل كومة مخزون تحتوي على { $stock_count } بطاقة.
skipbo-match-game-start = تبدأ اللعبة المحتسَبة { $game }. كل كومة مخزون تحتوي على { $stock_count } بطاقة.
skipbo-match-game-start-quick = تبدأ اللعبة المحتسَبة السريعة { $game }. كل كومة مخزون تحتوي على { $stock_count } بطاقة.
skipbo-initial-stock-you = بطاقة مخزونك المكشوفة هي { $card }.
skipbo-initial-stock-player = بطاقة مخزون { $player } المكشوفة هي { $card }.
skipbo-draw-turn-you = تسحب { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} لبدء دورك. يدك هي { $hand }.
skipbo-draw-turn-player = يسحب { $player } { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} لبدء دور { GENDER_TERM($player_gender, "possessive-determiner") }.
skipbo-refill-you = استخدمت كل بطاقة في يدك، لذا تسحب فورًا { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
}. يدك هي { $hand }.
skipbo-refill-player = استخدم { $player } كل بطاقة في يد { GENDER_TERM($player_gender, "possessive-determiner") } ويسحب فورًا { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
}.
skipbo-no-refill-you = يدك فارغة، ولا توجد بطاقات متاحة للسحب.
skipbo-no-refill-player = يد { $player } فارغة، لكن لا توجد بطاقات متاحة للسحب.
skipbo-recycle-completed = كومة السحب فارغة. تُخلط أكوام البناء المكتملة لتكوين كومة سحب جديدة بها { $count } بطاقة.

skipbo-play-you = تلعب { $card } من { $source } إلى كومة البناء { $pile }.
skipbo-play-player = يلعب { $player } { $card } من { $source } إلى كومة البناء { $pile }.
skipbo-complete-building-you = تُكمل كومة البناء { $pile } عند 12. تُوضَع بطاقاتها جانبًا لإعادة الخلط، ويصبح موضع البناء فارغًا من جديد.
skipbo-complete-building-player = يُكمل { $player } كومة البناء { $pile } عند 12. تُوضَع بطاقاتها جانبًا لإعادة الخلط، ويصبح موضع البناء فارغًا من جديد.
skipbo-next-stock-you = بطاقة مخزونك المكشوفة التالية هي { $card }؛ تتبقّى { $count } { $count ->
    [one] بطاقة
   *[other] بطاقات
} في كومة مخزونك.
skipbo-next-stock-player = بطاقة مخزون { $player } المكشوفة التالية هي { $card }؛ تحتوي تلك الكومة على { $count } { $count ->
    [one] بطاقة متبقّية
   *[other] بطاقات متبقّية
}.
skipbo-stock-cleared-you = أصبحت كومة مخزونك فارغة الآن. لا تزال شراكتك بحاجة إلى تفريغ كومة المخزون الأخرى.
skipbo-stock-cleared-player = أصبحت كومة مخزون { $player } فارغة الآن. لا تزال الشراكة بحاجة إلى تفريغ كومة مخزونها الأخرى.
skipbo-discard-you = ترمي { $card } على كومة الرمي { $pile } وتنهي دورك.
skipbo-discard-player = يرمي { $player } { $card } على كومة الرمي { $pile } وينهي دور { GENDER_TERM($player_gender, "possessive-determiner") }.
skipbo-empty-end-you = ليست لديك بطاقة متاحة للرمي، لذا تنهي دورك دون رمي.
skipbo-empty-end-player = ليست لدى { $player } بطاقة متاحة للرمي، وينهي دور { GENDER_TERM($player_gender, "possessive-determiner") } دون رمي.

skipbo-single-win-you = تُفرّغ كومة مخزونك وتفوز باللعبة.
skipbo-single-win-player = يُفرّغ { $player } كومة مخزون { GENDER_TERM($player_gender, "possessive-determiner") } ويفوز باللعبة.
skipbo-single-win-team-you = تُفرّغ شراكتك كلتا كومتي المخزون وتفوز باللعبة.
skipbo-single-win-team = يُفرّغ الفريق { $team } كلتا كومتي المخزون ويفوز باللعبة.
skipbo-scored-game-win-you = تُفرّغ كومة مخزونك وتفوز باللعبة المحتسَبة { $game }، مكتسبًا { $points } نقطة مع تبقّي { $remaining } عبر أكوام مخزون الخصوم. مجموع مباراتك هو { $total }.
skipbo-scored-game-win-player = يُفرّغ { $player } كومة مخزون { GENDER_TERM($player_gender, "possessive-determiner") } ويفوز باللعبة المحتسَبة { $game }، مكتسبًا { $points } نقطة مع تبقّي { $remaining } عبر أكوام مخزون الخصوم. مجموع المباراة هو { $total }.
skipbo-scored-game-win-team-you = تُفرّغ شراكتك كلتا كومتي المخزون وتفوز باللعبة المحتسَبة { $game }، مكتسبةً { $points } نقطة مع تبقّي { $remaining } عبر أكوام مخزون الخصوم. مجموع مباراتك هو { $total }.
skipbo-scored-game-win-team = يُفرّغ الفريق { $team } كلتا كومتي المخزون ويفوز باللعبة المحتسَبة { $game }، مكتسبًا { $points } نقطة مع تبقّي { $remaining } عبر أكوام مخزون الخصوم. مجموع مباراة الفريق هو { $total }.
skipbo-next-round = ستبدأ اللعبة المحتسَبة التالية قريبًا. يتقدّم موضع البداية مقعدًا واحدًا.
skipbo-match-win-you = تفوز بمباراة سكيب-بو بـ{ $score } نقطة.
skipbo-match-win-player = يفوز { $player } بمباراة سكيب-بو بـ{ $score } نقطة.
skipbo-match-win-team-you = تفوز شراكتك بمباراة سكيب-بو بـ{ $score } نقطة.
skipbo-match-win-team = يفوز الفريق { $team } بمباراة سكيب-بو بـ{ $score } نقطة.

skipbo-building-empty = كومة البناء { $pile }: فارغة؛ تحتاج 1.
skipbo-building-top = كومة البناء { $pile }: { $value } في الأعلى؛ تحتاج { $needed }.
skipbo-draw-count = كومة السحب: { $draw_count } بطاقة. بطاقات البناء المكتملة بانتظار إعادة الخلط: { $recycle_count }.
skipbo-stock-empty = كومة مخزون { $player }: فارغة.
skipbo-stock-status = كومة مخزون { $player }: { $card } مكشوفة، { $count } { $count ->
    [one] بطاقة إجمالًا
   *[other] بطاقات إجمالًا
}.
skipbo-discard-your-header = أكوام رميك:
skipbo-discard-player-header = أكوام رمي { $player }:
skipbo-discard-empty = كومة الرمي { $pile }: فارغة.
skipbo-discard-top = كومة الرمي { $pile }: { $card } في الأعلى، { $count } { $count ->
    [one] بطاقة إجمالًا
   *[other] بطاقات إجمالًا
}.
skipbo-hand-empty = ليست لديك أي بطاقات في اليد بعد.
skipbo-hand-menu-card = اليد: { $card }

skipbo-error-invalid-stock-mode = طول كومة المخزون المحدَّد غير مدعوم. اختر قياسي أو سريع 10 أو سريع 15.
skipbo-error-invalid-scoring-mode = صيغة المباراة المحدَّدة غير مدعومة. اختر لعبة واحدة أو مباراة محتسَبة.
skipbo-error-winning-score-range = يجب أن يكون هدف المباراة من { $min } إلى { $max } نقطة؛ وهو حاليًا { $value }.
skipbo-error-partnership-player-count = تتطلّب الشراكات 4 لاعبين بالضبط لشراكتين، أو 6 لاعبين لثلاث شراكات.
skipbo-error-game-not-active = لعبة سكيب-بو هذه ليست نشطة حاليًا.
skipbo-error-round-transition = انتهت اللعبة الحالية. انتظر بدء اللعبة التالية.
skipbo-error-card-move-selection-you = اختر أولًا إلى أين تنقل البطاقة المحدَّدة.
skipbo-error-play-changed = لم تعد تلك اللعبة متاحة لأن البطاقة أو كومة البناء تغيّرت. اختر إجراءً حاليًا من قائمة الدور.
skipbo-error-card-changed = لم تعد تلك البطاقة متاحة. اختر إجراءً حاليًا من قائمة الدور.
skipbo-error-cards-available = لا تزال لديك بطاقة متاحة للرمي. أنهِ دورك باختيار تلك البطاقة وإحدى أكوام رميك الأربع.
skipbo-error-no-discard-targets = لا تتوفّر أكوام رمي أي لاعب آخر.
skipbo-error-discard-target-changed = لم تعد أكوام رمي ذلك اللاعب متاحة. اختر لاعبًا حاليًا.
skipbo-discard-owner-unavailable = اللاعب لم يعد متاحًا

skipbo-result-line = { $rank }. { $player }: { $points }
