game-name-midnight = 1-4-24
midnight-roll = رمي النرد
midnight-keep-die = احتفظ { $value }
midnight-bank = بنك
midnight-check-dice = قراءة النرد الحالي
midnight-check-round-status = عرض حالة الجولة
midnight-round-start = جولة { $round } من { $total }.
midnight-round-start-brief = جولة { $round }/{ $total }.
midnight-you-rolled = لقد تدحرجت: { $dice }.
midnight-player-rolled = { $player } توالت: { $dice }.
midnight-you-rolled-brief = أنت تتدحرج { $dice }.
midnight-player-rolled-brief = { $player }: { $dice }.
midnight-you-keep = ستظل تموت { $index }, يظهر { $die }.
midnight-player-keeps = { $player } يبقى يموت { $index }, يظهر { $die }.
midnight-you-keep-brief = احتفظ { $die }.
midnight-player-keeps-brief = { $player } يبقي { $die }.
midnight-you-unkeep = تعود مت { $index }, يظهر { $die }، إلى تجمع reroll.
midnight-player-unkeeps = { $player } يعود يموت { $index }, يظهر { $die }، إلى تجمع reroll.
midnight-you-unkeep-brief = أنت تعيد { $die }.
midnight-player-unkeeps-brief = { $player } إعادة { $die }.
midnight-you-scored = أنت مؤهل بالرقم 1 و4، وسجل { $score } من { $scoring_dice }.
midnight-scored = { $player } تأهل بالمركزين 1 و4 وسجل { $score } من { $scoring_dice }.
midnight-you-scored-brief = لقد سجلت { $score }.
midnight-scored-brief = { $player }: { $score }.
midnight-you-disqualified = أنت غير مؤهل لأنك مفقود { $missing }.
midnight-player-disqualified = { $player } غير مؤهل لأنهم مفقودون { $missing }.
midnight-you-disqualified-brief = اشتقت { $missing }.
midnight-player-disqualified-brief = { $player } يفتقد { $missing }.
midnight-you-win-round = لقد فزت بالجولة { $round } مع { $score }.
midnight-round-winner = { $player } يفوز بالجولة { $round } مع { $score }.
midnight-you-win-round-brief = تربح R{ $round }: { $score }.
midnight-round-winner-brief = { $player } يفوز ر{ $round }: { $score }.
midnight-round-tie = جولة متعادلة في { $score } بين { $players }. لا يتم منح أي فوز في الجولة.
midnight-all-disqualified = غاب جميع اللاعبين عن الرقمين 1 و4 المطلوبين. لا يتم منح أي فوز في الجولة.
midnight-all-disqualified-brief = لا أحد مؤهل.
midnight-you-win-game =
    تفوز باللعبة مع { $wins } { $wins ->
        [one] فوز الجولة
       *[other] انتصارات الجولة
    }!
midnight-game-winner =
    { $player } يفوز باللعبة مع { $wins } { $wins ->
        [one] فوز الجولة
       *[other] انتصارات الجولة
    }!
midnight-you-win-game-brief = لقد فزت: { $wins }.
midnight-game-winner-brief = { $player } الانتصارات: { $wins }.
midnight-game-tie =
    إنها لعبة التعادل. { $players } انتهى كل منها بـ { $wins } { $wins ->
        [one] فوز الجولة
       *[other] انتصارات الجولة
    }.
midnight-set-rounds = جولات اللعب: { $rounds }
midnight-enter-rounds = أدخل عدد الجولات للعب:
midnight-option-changed-rounds = تم تغيير جولات اللعب إلى { $rounds }
midnight-desc-rounds = عدد جولات منتصف الليل التي سيتم لعبها قبل التسجيل النهائي (الافتراضي 5، النطاق 1-20).
midnight-error-rounds-out-of-range = منتصف الليل يدعم { $min } إلى { $max } جولات. الإعداد الحالي: { $rounds }.
midnight-need-to-roll = قم برمي النرد قبل اختيار النرد للاحتفاظ به.
midnight-no-dice-to-keep = لا يوجد نرد متبقي للتدحرج أو الاحتفاظ به.
midnight-must-keep-one = احتفظ بنرد واحد على الأقل ملفوف حديثًا قبل التدحرج مرة أخرى.
midnight-must-roll-first = قم برمي النرد قبل صرف دورك.
midnight-keep-all-first = تقرر كل يموت قبل المصرفية. احتفظ بجميع النردات المفتوحة أو قم بإعادتها أولاً.
midnight-invalid-die-index = هذا القالب غير متوفر في هذه اللفة.
midnight-die-locked = { $value } (مقفل)
midnight-die-kept = { $value } (محفوظ)
midnight-die-value = { $value }
midnight-die-index = يموت { $index }
midnight-your-dice-not-rolled = أنت لم تدحرج بعد هذا المنعطف.
midnight-player-dice-not-rolled = { $player } لم توالت بعد هذا المنعطف.
midnight-your-dice-status =
    { $qualified ->
        [yes] النرد الخاص بك: { $dice }. مقفل: { $locked }; محفوظ لللفة التالية: { $kept }; النرد لا يزال حيا: { $remaining }. ستكون نتيجة التأهل الحالية { $score } من { $scoring_dice }.
       *[no] النرد الخاص بك: { $dice }. مغلق: { $locked }; محفوظ لللفة التالية: { $kept }; النرد لا يزال حيا: { $remaining }. مازلت بحاجة { $missing } للتأهل.
    }
midnight-player-dice-status =
    { $qualified ->
        [yes] { $player }النرد: { $dice }. مقفل: { $locked }; محفوظ لللفة التالية: { $kept }; النرد لا يزال حيا: { $remaining }. ستكون نتيجة التأهل الحالية { $score } من { $scoring_dice }.
       *[no] { $player }النرد: { $dice }. مقفل: { $locked }; محفوظ لللفة التالية: { $kept }; النرد لا يزال حيا: { $remaining }. ما زالوا بحاجة { $missing } للتأهل.
    }
midnight-status-round = جولة { $round } من { $total }
midnight-status-current-player = المنعطف الحالي: { $player }
midnight-status-current-not-rolled = { $player } لم توالت بعد.
midnight-status-current-dice =
    { $qualified ->
        [yes] النرد الحالي لـ { $player }: { $dice }. النتيجة المحتملة: { $score } من { $scoring_dice }. مغلق { $locked }, أبقى { $kept }مباشر { $remaining }.
       *[no] النرد الحالي لـ { $player }: { $dice }. مفقود { $missing }. مغلق { $locked }, أبقى { $kept }مباشر { $remaining }.
    }
midnight-status-dice-not-rolled = لم تدحرج
midnight-status-last-qualified = المنعطف الأخير: { $player } توالت { $dice } وسجل { $score }.
midnight-status-last-disqualified = المنعطف الأخير: { $player } توالت { $dice } ولم يتأهل.
midnight-status-standing-line =
    { $qualified ->
        [yes] { $rank }. { $player }: { $wins } انتصارات الجولة؛ الجولة الحالية { $current }، مؤهَل.
       *[no] { $rank }. { $player }: { $wins } انتصارات الجولة؛ الجولة الحالية { $current }، غير مؤهل.
    }
midnight-score-unit-round-wins =
    { $count ->
        [one] فوز الجولة
       *[other] انتصارات الجولة
    }
midnight-end-score =
    { $rank }. { $player }: { $wins } { $wins ->
        [one] فوز الجولة
       *[other] انتصارات الجولة
    }
