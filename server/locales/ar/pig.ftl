game-name-pig = خنزير
pig-desc-team-mode = العب بشكل فردي أو ضمن ترتيب فريق مدعوم. يشارك الفريق درجة واحدة ويفوز فورًا عندما يحمل أحد الأعضاء نقاطًا كافية.
pig-roll = رمي النرد
pig-hold = عقد { $points } النقاط
pig-check-turn-status = التحقق من حالة الانعطاف
pig-game-start =
    يبدأ الخنزير. الأول { $team ->
        [yes] فريق
       *[no] لاعب
    } لعقد { $target } نقاط يفوز. النرد لديه { $sides } الجانبين، ورمي 1 يخسر كل نقطة غير مصرفية من هذا المنعطف. { $minimum ->
        [0] يمكنك الاستمرار بعد أي لفة تسجيل.
       *[other] يجب عليك جمع ما لا يقل عن { $minimum } نقاط الدوران قبل الضغط.
    }
pig-game-start-brief =
    يبدأ الخنزير. الهدف: { $target }. يموت: { $sides } الجانبين. الحد الأدنى للاحتفاظ: { $minimum }.{ $team ->
        [yes] تتقاسم الفرق النتائج.
       *[no] النتائج الفردية.
    }
pig-round-start = جولة { $round } يبدأ. سيأخذ كل لاعب نشط دورًا واحدًا.
pig-round-start-brief = جولة { $round }.
pig-you-roll-result = لقد تدحرجت { $roll }. إجمالي دورك الآن { $total } نقاط.
pig-player-roll-result = { $player } توالت { $roll }. إجمالي دورهم الآن { $total } نقاط.
pig-you-roll-result-brief = أنت: { $roll }; بدوره الإجمالي { $total }.
pig-player-roll-result-brief = { $player }: { $roll }; بدوره الإجمالي { $total }.
pig-you-bust = لقد حصلت على 1 وخسرت الكل { $points } النقاط غير المصرفية. ينتهي دورك بدون أي نتيجة.
pig-player-busts = { $player } تدحرجت 1 وخسرت كل شيء { $points } النقاط غير المصرفية. وينتهي دورهم بلا نتيجة.
pig-you-bust-brief = لقد رميت 1 وخسرت { $points } نقاط الانعطاف.
pig-player-busts-brief = { $player } توالت 1 وخسرت { $points } نقاط الانعطاف.
pig-you-hold =
    أنت تحمل { $points } نقاط. { $team ->
        [yes] فريقك الآن لديه { $total } نقاط.
       *[no] مجموع درجاتك الآن { $total } نقاط.
    }
pig-player-holds =
    { $player } يحمل { $points } نقاط. { $team ->
        [yes] { $team_name } الآن { $total } نقاط.
       *[no] مجموع نقاطهم الآن { $total } نقاط.
    }
pig-you-hold-brief =
    أنت تحمل { $points };{ $team ->
        [yes] { $team_name } المجموع { $total }.
       *[no] مجموعك { $total }.
    }
pig-player-holds-brief =
    { $player } يحمل { $points };{ $team ->
        [yes] { $team_name } المجموع { $total }.
       *[no] المجموع { $total }.
    }
pig-you-win =
    { $team ->
        [yes] فريقك { $winner }، هو الفائز بالخنزير مع { $score } نقاط!
       *[no] أنت الفائز بالخنزير مع { $score } نقاط!
    }
pig-winner =
    { $team ->
        [yes] الفائز هو { $winner }مع { $score } نقاط!
       *[no] الفائز هو { $winner }مع { $score } نقاط!
    }
pig-you-win-brief =
    { $team ->
        [yes] الفائز: فريقك، { $winner }مع { $score }.
       *[no] الفائز: أنت، مع { $score }.
    }
pig-winner-brief = الفائز: { $winner }مع { $score }.
pig-confirm-risky-roll =
    المتداول مرة أخرى يضع { $points } النقاط غير المصرفية المعرضة للخطر، مع { $risk } فرصة في المئة لفقدانهم. { $winning ->
        [yes] عقد الآن سيعطيك { $total } النقاط والفوز باللعبة.
       *[no] عقد الآن سيعطيك { $total } من { $target } النقاط اللازمة للفوز.
    } اضغط على Roll مرة أخرى داخل { $seconds } ثواني للتأكيد.
pig-action-resolving = وما زال الموت يتدحرج. انتظر النتيجة.
pig-no-turn-points = قم برمي النرد مرة واحدة على الأقل قبل الإمساك به.
pig-need-more-points = لديك { $current } نقاط الدوران، ولكن هذا الجدول يتطلب على الأقل { $required } قبل عقد.
pig-desc-target-score = أول لاعب أو فريق يحمل هذا العدد الإجمالي من النقاط يفوز على الفور (الافتراضي 100، النطاق 10-1000).
pig-set-min-bank = الحد الأدنى للاحتفاظ: { $points }
pig-set-dice-sides = جوانب القالب: { $sides }
pig-enter-min-bank = أدخل الحد الأدنى من نقاط الانعطاف المطلوبة للاحتفاظ بها:
pig-enter-dice-sides = أدخل عدد جوانب القالب:
pig-option-changed-min-bank = تم تغيير الحد الأدنى للاحتفاظ إلى { $points } نقاط.
pig-desc-min-bank = عدد نقاط الانعطاف المطلوبة قبل أن يصبح التعليق متاحًا. اضبط هذا على 0 للخنزير القياسي؛ يجب أن تظل أقل من النتيجة المستهدفة (الافتراضي 0، النطاق 0-999).
pig-option-changed-dice = النرد الآن لديه { $sides } الجانبين.
pig-desc-dice-sides = عدد جوانب القالب الواحد. التدحرج 1 يفقد دائمًا إجمالي عدد الأدوار (الافتراضي 6، النطاق 4-20).
pig-error-target-out-of-range = النتيجة المستهدفة { $value } غير صالح. اختر قيمة من { $min } إلى { $max }.
pig-error-min-bank-out-of-range = الحد الأدنى للعقد { $value } غير صالح. اختر قيمة من { $min } إلى { $max }.
pig-error-dice-sides-out-of-range = أ { $value }القالب ذو الجوانب غير مدعوم. اختر من { $min } إلى { $max } الجانبين.
pig-error-min-bank-too-high = الحد الأدنى للعقد { $minimum } يجب أن تكون أقل من النتيجة المستهدفة { $target }.
pig-status-target = النتيجة المستهدفة: { $target } نقاط.
pig-status-round = الجولة الحالية: { $round }.
pig-status-current-turn = { $player } يلعب: { $banked } بنك، { $turn } في هذا المنعطف، { $potential } إذا عقدت الآن.
pig-status-standing = { $rank }. { $team }: { $score } نقاط.
pig-line-format = { $rank }. { $player }: { $points }
