game-name-leftrightcenter = يسار وسط يمين
lrc-roll =
    لفة { $count } { $count ->
        [one] يموت
       *[other] النرد
    }
lrc-roll-label = لفة النرد
lrc-face-left = اليسار
lrc-face-center = المركز
lrc-face-right = الحق
lrc-face-dot = نقطة
lrc-you-roll = أنت تتدحرج { $results }.
lrc-player-rolls = { $player } لفات { $results }.
lrc-you-roll-brief = أنت: { $results }.
lrc-player-rolls-brief = { $player }: { $results }.
lrc-you-pass-left =
    تمر { $count } { $count ->
        [one] شريحة
       *[other] رقائق
    } اليسار إلى { $target }. لديك { $remaining } غادر؛ { $target } الآن { $target_total }.
lrc-player-passes-left =
    { $player } يمر { $count } { $count ->
        [one] شريحة
       *[other] شيبس
    } اليسار إلى { $target }. { $player } لديه { $remaining } غادر؛ { $target } الآن { $target_total }.
lrc-you-pass-left-brief = أنت، اليسار إلى { $target }: { $count }. المتبقي: { $remaining }.
lrc-player-passes-left-brief = { $player }، من اليسار إلى { $target }: { $count }. المتبقي: { $remaining }.
lrc-you-pass-right =
    تمر { $count } { $count ->
        [one] شريحة
       *[other] شيبس
    } الحق في { $target }. لديك { $remaining } غادر؛ { $target } الآن { $target_total }.
lrc-player-passes-right =
    { $player } يمر { $count } { $count ->
        [one] شريحة
       *[other] شيبس
    } الحق في { $target }. { $player } لديه { $remaining } غادر؛ { $target } الآن { $target_total }.
lrc-you-pass-right-brief = أنت، الحق في ذلك { $target }: { $count }. المتبقي: { $remaining }.
lrc-player-passes-right-brief = { $player }، الحق في { $target }: { $count }. المتبقي: { $remaining }.
lrc-you-pass-center =
    لقد وضعت { $count } { $count ->
        [one] شريحة
       *[other] شيبس
    } في المركز. لديك { $remaining } غادر؛ المركز يحمل الآن { $center }.
lrc-player-passes-center =
    { $player } يضع { $count } { $count ->
        [one] شريحة
       *[other] شيبس
    } في المركز. { $player } لديه { $remaining } غادر؛ المركز يحمل الآن { $center }.
lrc-you-pass-center-brief = أنت، المركز: { $count }. المتبقي: { $remaining }. إجمالي المركز: { $center }.
lrc-player-passes-center-brief = { $player }‎المركز: { $count }. المتبقي: { $remaining }. إجمالي المركز: { $center }.
lrc-you-keep-all =
    كل النرد الخاص بك عبارة عن نقاط، لذا عليك الاحتفاظ بكل { $count } { $count ->
        [one] شريحة
       *[other] شيبس
    }.
lrc-player-keeps-all =
    كل { $player }نرد النقاط عبارة عن نقاط، لذا فهي تحتفظ بكل { $count } { $count ->
        [one] شريحة
       *[other] شيبس
    }.
lrc-you-keep-all-brief =
    أنت: لا تحويلات؛ { $count } { $count ->
        [one] شريحة
       *[other] رقائق
    }.
lrc-player-keeps-all-brief =
    { $player }: لا التحويلات. { $count } { $count ->
        [one] شريحة
       *[other] شيبس
    }.
lrc-you-skip-no-chips = ليس لديك أي رقائق، لذلك تم تخطي دورك. ستبقى في اللعبة ويمكنك الحصول على رقائق من أي من الجيران.
lrc-player-skips-no-chips = { $player } ليس لديه رقائق، لذلك تم تخطي دورهم. يظلون في اللعبة ويمكنهم الحصول على رقائق من أي من الجيران.
lrc-you-skip-no-chips-brief = أنت: لا رقائق. بدوره تخطي.
lrc-player-skips-no-chips-brief = { $player }: لا رقائق. بدوره تخطي.
lrc-you-win =
    أنت آخر لاعب لديه رقائق وتفوز بـ { $count } متبقي. أنت تطالب بـ { $center } { $center ->
        [one] شريحة
       *[other] شيبس
    } في المركز.
lrc-player-wins =
    { $player } هو آخر لاعب لديه رقائق ويفوز بـ { $count } متبقي. يدعون { $center } { $center ->
        [one] شريحة
       *[other] شيبس
    } في المركز.
lrc-you-win-brief = لقد فزت. رقائقك: { $count }. المركز: { $center }.
lrc-player-wins-brief = { $player } يفوز. الرقائق: { $count }. المركز: { $center }.
lrc-roll-already-resolving = لقد تم بالفعل حل القائمة الخاصة بك. انتظر حتى تنتهي عمليات نقل الشريحة.
lrc-no-chips-to-roll = ليس لديك رقائق للفة. سيتم تخطي دورك تلقائيا.
lrc-center-pot =
    وعاء المركز: { $count } { $count ->
        [one] شريحة
       *[other] شيبس
    }.
lrc-check-center = تحقق من الوعاء المركزي
lrc-check-last-roll = التحقق من آخر لفة
lrc-last-roll-none = لم يتم رمي النرد بعد.
lrc-last-roll-you = آخر لفة لك كانت { $results }.
lrc-last-roll-player = { $player } آخر توالت { $results }.
lrc-set-starting-chips = رقائق البداية: { $count }
lrc-enter-starting-chips = أدخل رقائق البداية:
lrc-option-changed-starting-chips = تم ضبط شرائح البداية على { $count }.
leftrightcenter-desc-starting-chips = كم عدد الرقائق التي يبدأ بها كل لاعب من لاعبي الوسط الأيمن والأيسر (الافتراضي 3، النطاق من 1 إلى 10).
lrc-error-starting-chips-invalid = يجب أن تكون رقائق البداية بين { $min } و { $max }; القيمة الحالية هي { $count }.
lrc-line-format =
    { $player }: { $chips } { $chips ->
        [one] شريحة
       *[other] رقائق
    }
