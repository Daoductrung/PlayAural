game-name-bunko = بونكو

bunko-roll = ارمِ النرد
bunko-check-status = التحقق من الحالة
bunko-check-last-roll = التحقق من آخر رمية

bunko-game-start = تبدأ بونكو. اللاعبون: { $players }.
bunko-round-start = الجولة { $round } من { $total_rounds }. الرقم المستهدف لهذه الجولة هو { $target }.
bunko-round-start-brief = الجولة { $round }/{ $total_rounds }. الهدف { $target }.
bunko-you-win-round = تفوز بالجولة { $round } بـ { $score } نقطة مقابل الهدف { $target }.
bunko-player-wins-round = { $player } يفوز بالجولة { $round } بـ { $score } نقطة مقابل الهدف { $target }.
bunko-you-win-round-brief = تفوز بالجولة { $round }: { $score }.
bunko-player-wins-round-brief = { $player } يفوز بالجولة { $round }: { $score }.

bunko-you-roll-match = ترمي { $dice } وتسجّل { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} نحو الهدف { $target }. إجمالي الجولة: { $round_total }. النتيجة الكلية: { $total }.
bunko-player-rolls-match = { $player } يرمي { $dice } ويسجّل { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} نحو الهدف { $target }. إجمالي الجولة: { $round_total }. النتيجة الكلية: { $total }.
bunko-you-roll-match-brief = أنت: { $dice }، +{ $points }. الجولة { $round_total }؛ الإجمالي { $total }.
bunko-player-rolls-match-brief = { $player }: { $dice }، +{ $points }. الجولة { $round_total }؛ الإجمالي { $total }.

bunko-you-roll-mini_bunko = ترمي { $dice }، وتسجّل بونكو مصغّرًا لأن كل النرد متطابق مع بعضه لكن ليس مع الهدف { $target }، وتكسب { $points } نقطة. إجمالي الجولة: { $round_total }. النتيجة الكلية: { $total }.
bunko-player-rolls-mini_bunko = { $player } يرمي { $dice }، ويسجّل بونكو مصغّرًا لأن كل النرد متطابق مع بعضه لكن ليس مع الهدف { $target }، ويكسب { $points } نقطة. إجمالي الجولة: { $round_total }. النتيجة الكلية: { $total }.
bunko-you-roll-mini_bunko-brief = أنت: بونكو مصغّر { $dice }، +{ $points }. الجولة { $round_total }؛ الإجمالي { $total }.
bunko-player-rolls-mini_bunko-brief = { $player }: بونكو مصغّر { $dice }، +{ $points }. الجولة { $round_total }؛ الإجمالي { $total }.

bunko-you-roll-bunko = ترمي { $dice } وتسجّل بونكو: ثلاثة من الهدف { $target } مقابل { $points } نقطة. إجمالي الجولة: { $round_total }. النتيجة الكلية: { $total }.
bunko-player-rolls-bunko = { $player } يرمي { $dice } ويسجّل بونكو: ثلاثة من الهدف { $target } مقابل { $points } نقطة. إجمالي الجولة: { $round_total }. النتيجة الكلية: { $total }.
bunko-you-roll-bunko-brief = أنت: بونكو { $dice }، +{ $points }. الجولة { $round_total }؛ الإجمالي { $total }.
bunko-player-rolls-bunko-brief = { $player }: بونكو { $dice }، +{ $points }. الجولة { $round_total }؛ الإجمالي { $total }.

bunko-you-roll-no_score = ترمي { $dice } ولا تسجّل شيئًا لأن أيًّا من النرد لا يطابق الهدف { $target } ولا يوجد بونكو مصغّر. ينتقل دورك.
bunko-player-rolls-no_score = { $player } يرمي { $dice } ولا يسجّل شيئًا لأن أيًّا من النرد لا يطابق الهدف { $target } ولا يوجد بونكو مصغّر. ينتقل الدور.
bunko-you-roll-no_score-brief = أنت: { $dice }، 0. تمرير.
bunko-player-rolls-no_score-brief = { $player }: { $dice }، 0. تمرير.

bunko-last-roll-none = لم تُجرَ أي رمية بعد في هذه الجولة.
bunko-last-roll-match = { $player } رمى آخر مرة { $dice } وسجّل { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} نحو الهدف { $target }.
bunko-last-roll-match-you = رميت آخر مرة { $dice } وسجّلت { $points } { $points ->
    [one] نقطة
   *[other] نقاط
} نحو الهدف { $target }.
bunko-last-roll-mini_bunko = { $player } رمى آخر مرة { $dice } محققًا بونكو مصغّرًا، مسجّلًا { $points } نقطة لأن النرد تطابق مع بعضه لكن ليس مع الهدف { $target }.
bunko-last-roll-mini_bunko-you = رميت آخر مرة { $dice } محققًا بونكو مصغّرًا، مسجّلًا { $points } نقطة لأن النرد تطابق مع بعضه لكن ليس مع الهدف { $target }.
bunko-last-roll-bunko = { $player } رمى آخر مرة { $dice } محققًا بونكو: ثلاثة من الهدف { $target }، بقيمة { $points } نقطة.
bunko-last-roll-bunko-you = رميت آخر مرة { $dice } محققًا بونكو: ثلاثة من الهدف { $target }، بقيمة { $points } نقطة.
bunko-last-roll-no_score = { $player } رمى آخر مرة { $dice } ولم يسجّل شيئًا مقابل الهدف { $target }.
bunko-last-roll-no_score-you = رميت آخر مرة { $dice } ولم تسجّل شيئًا مقابل الهدف { $target }.

bunko-status-round = الجولة { $round } من { $total_rounds }. الرقم المستهدف: { $target }.
bunko-status-turn = اللاعب الحالي: { $player }.
bunko-status-leader = المتصدّر: { $player } بـ { $rounds } { $rounds ->
    [one] جولة رابحة
   *[other] جولات رابحة
} و { $total } نقطة كلية.

bunko-standings-header = الترتيب. يُحدَّد الفائز حسب { $mode }.
bunko-score-line = { $rank }. { $player }: { $rounds } { $rounds ->
    [one] جولة رابحة
   *[other] جولات رابحة
}، { $total } نقطة كلية، { $current } هذه الجولة، { $bunkos } { $bunkos ->
    [one] بونكو
   *[other] بونكو
}، { $mini_bunkos } { $mini_bunkos ->
    [one] بونكو مصغّر
   *[other] بونكو مصغّر
}

bunko-roll-already-resolving = لا يزال نردك يدور. انتظر النتيجة قبل الرمي مجددًا.
bunko-error-round-count-invalid = تتطلب بونكو بين { $min } و { $max } جولة. الإعداد الحالي { $count }.
bunko-error-winning-mode-invalid = لا تدعم بونكو وضع الفوز "{ $mode }". اختر الفوز بالجولات أو النتيجة الكلية.

bunko-set-round-count = الجولات: { $count }
bunko-enter-round-count = أدخل عدد الجولات:
bunko-option-changed-round-count = تم تغيير عدد الجولات إلى { $count }.
bunko-desc-round-count = عدد جولات بونكو التي تُلعب قبل تحديد الفائز (الافتراضي 6، النطاق 1-12).

bunko-set-winning-mode = وضع الفوز: { $mode }
bunko-select-winning-mode = اختر وضع الفوز:
bunko-option-changed-winning-mode = تم تغيير وضع الفوز إلى { $mode }.
bunko-desc-winning-mode = يحدد ما إذا كان ترتيب فائزي بونكو حسب الجولات المكسوبة أم حسب النتيجة الكلية.
bunko-winning-mode-round-wins = الفوز بالجولات
bunko-winning-mode-total-score = النتيجة الكلية
