game-name-bunko = بونكو
bunko-roll = رمي النرد
bunko-check-status = التحقق من الحالة
bunko-check-last-roll = تحقق من أحدث لفة
bunko-game-start = يبدأ بونكو. اللاعبين: { $players }.
bunko-round-start = جولة { $round } من { $total_rounds }. الرقم المستهدف لهذه الجولة هو { $target }.
bunko-round-start-brief = جولة { $round }/{ $total_rounds }. الهدف { $target }.
bunko-you-win-round = لقد فزت بالجولة { $round } مع { $score } نقاط ضد الهدف { $target }.
bunko-player-wins-round = { $player } يفوز بالجولة { $round } مع { $score } نقاط ضد الهدف { $target }.
bunko-you-win-round-brief = تربح R{ $round }: { $score }.
bunko-player-wins-round-brief = { $player } يفوز ر{ $round }: { $score }.
bunko-you-roll-match =
    أنت تتدحرج { $dice } والنتيجة { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    } نحو الهدف { $target }. مجموع الجولة: { $round_total }. النتيجة الإجمالية: { $total }.
bunko-player-rolls-match =
    { $player } لفات { $dice } والنتائج { $points } { $points ->
        [one] نقطة
       *[other] نقاط
    } نحو الهدف { $target }. مجموع الجولة: { $round_total }. النتيجة الإجمالية: { $total }.
bunko-you-roll-match-brief = أنت: { $dice }, +{ $points }. جولة { $round_total }; المجموع { $total }.
bunko-player-rolls-match-brief = { $player }: { $dice }, +{ $points }. جولة { $round_total }; المجموع { $total }.
bunko-you-roll-mini_bunko = أنت تتدحرج { $dice }، سجل بونكو صغيرًا لأن جميع أحجار النرد تتطابق مع بعضها البعض ولكنها لا تستهدف { $target }، واكسب { $points } نقاط. مجموع الجولة: { $round_total }. النتيجة الإجمالية: { $total }.
bunko-player-rolls-mini_bunko = { $player } لفات { $dice }، يسجل Bunko صغيرًا لأن جميع أحجار النرد تتطابق مع بعضها البعض ولكنها لا تستهدف { $target }، والمكاسب { $points } نقاط. مجموع الجولة: { $round_total }. النتيجة الإجمالية: { $total }.
bunko-you-roll-mini_bunko-brief = أنت: ميني بونكو { $dice }, +{ $points }. جولة { $round_total }; المجموع { $total }.
bunko-player-rolls-mini_bunko-brief = { $player }: ميني بونكو { $dice }, +{ $points }. جولة { $round_total }; المجموع { $total }.
bunko-you-roll-bunko = أنت تتدحرج { $dice } وسجل بونكو: ثلاثة أهداف { $target }لـ { $points } نقاط. إجمالي الجولة: { $round_total }. النتيجة الإجمالية: { $total }.
bunko-player-rolls-bunko = { $player } لفات { $dice } ويسجل بونكو: ثلاثة أهداف { $target }لـ { $points } نقاط. مجموع الجولة: { $round_total }. النتيجة الإجمالية: { $total }.
bunko-you-roll-bunko-brief = أنت: بونكو { $dice }, +{ $points }. جولة { $round_total }; المجموع { $total }.
bunko-player-rolls-bunko-brief = { $player }: بونكو { $dice }, +{ $points }. جولة { $round_total }; المجموع { $total }.
bunko-you-roll-no_score = أنت تتدحرج { $dice } ولم يسجل أي شيء لأنه لم يتطابق أي من النرد مع الهدف { $target } وليس هناك بونكو صغير. دورك يمر.
bunko-player-rolls-no_score = { $player } لفات { $dice } ولم يسجل شيئًا لأنه لم يتطابق أي من أحجار النرد مع الهدف { $target } وليس هناك بونكو صغير. يمر الدور.
bunko-you-roll-no_score-brief = أنت: { $dice }, 0. تمرير.
bunko-player-rolls-no_score-brief = { $player }: { $dice }, 0. تمرير.
bunko-last-roll-none = لم يتم إجراء أي لفة حتى الآن في هذه الجولة.
bunko-last-roll-match =
    { $player } آخر توالت { $dice } وسجل { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    } نحو الهدف { $target }.
bunko-last-roll-match-you =
    لقد تدحرجت آخر مرة { $dice } وسجل { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    } نحو الهدف { $target }.
bunko-last-roll-mini_bunko = { $player } آخر توالت { $dice } لميني بونكو سجل { $points } نقاط لأن النرد تطابق مع بعضها البعض ولكن ليس الهدف { $target }.
bunko-last-roll-mini_bunko-you = لقد تدحرجت آخر مرة { $dice } لميني بونكو سجل { $points } نقاط لأن النرد تطابق مع بعضها البعض ولكن ليس الهدف { $target }.
bunko-last-roll-bunko = { $player } آخر توالت { $dice } لبونكو: ثلاثة أهداف { $target }ق، بقيمة { $points } نقاط.
bunko-last-roll-bunko-you = لقد تدحرجت آخر مرة { $dice } لبونكو: ثلاثة أهداف { $target }ق، بقيمة { $points } نقاط.
bunko-last-roll-no_score = { $player } آخر توالت { $dice } ولم يسجل أي شيء في مرمى الهدف { $target }.
bunko-last-roll-no_score-you = لقد تدحرجت آخر مرة { $dice } ولم يسجل أي شيء في مرمى الهدف { $target }.
bunko-status-round = جولة { $round } من { $total_rounds }. الرقم المستهدف: { $target }.
bunko-status-turn = اللاعب الحالي: { $player }.
bunko-status-leader =
    القائد : { $player } مع { $rounds } { $rounds ->
        [one] فوز الجولة
       *[other] انتصارات الجولة
    } و { $total } النقاط الشاملة.
bunko-standings-header = الترتيب. تم تحديد الفائز بواسطة { $mode }.
bunko-score-line =
    { $rank }. { $player }: { $rounds } { $rounds ->
        [one] فوز الجولة
       *[other] انتصارات الجولة
    }, { $total } النقاط الإجمالية، { $current } هذه الجولة { $bunkos } { $bunkos ->
        [one] بونكو
       *[other] بنكوس
    }, { $mini_bunkos } { $mini_bunkos ->
        [one] ميني بونكو
       *[other] ميني بونكوس
    }
bunko-roll-already-resolving = النرد الخاص بك لا يزال المتداول. انتظر النتيجة قبل التدحرج مرة أخرى.
bunko-error-round-count-invalid = يتطلب بونكو بين { $min } و { $max } جولات. الإعداد الحالي هو { $count }.
bunko-error-winning-mode-invalid = بونكو لا يدعم وضع الفوز "{ $mode }". اختر انتصارات الجولة أو النتيجة الإجمالية.
bunko-set-round-count = الجولات: { $count }
bunko-enter-round-count = أدخل عدد الجولات:
bunko-option-changed-round-count = تم تغيير عدد الجولات إلى { $count }.
bunko-desc-round-count = كم عدد جولات Bunko التي تم لعبها قبل تحديد الفائز (الافتراضي 6، النطاق 1-12).
bunko-set-winning-mode = وضع الفوز: { $mode }
bunko-select-winning-mode = حدد الوضع الفائز:
bunko-option-changed-winning-mode = تم تغيير وضع الفوز إلى { $mode }.
bunko-desc-winning-mode = يختار ما إذا كان سيتم تصنيف الفائزين في Bunko حسب الجولات التي تم الفوز بها أو حسب النتيجة الإجمالية.
bunko-winning-mode-round-wins = انتصارات الجولة
bunko-winning-mode-total-score = مجموع النقاط
