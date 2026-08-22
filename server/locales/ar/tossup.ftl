game-name-tossup = إرم
tossup-roll-first =
    لفة { $count } { $count ->
        [one] يموت
       *[other] النرد
    }
tossup-roll-remaining =
    لفة { $count } المتبقي { $count ->
        [one] يموت
       *[other] النرد
    }
tossup-bank =
    بنك { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
tossup-check-turn-status = التحقق من حالة الانعطاف
tossup-game-start = يبدأ Toss Up بـ { $rules } القواعد، { $dice } النرد لكل مجموعة، والحد المستهدف هو { $target }. تجاوز العتبة وأكمل الأدوار المتبقية للفوز.
tossup-game-start-brief = يبدأ القذف. تجاوز { $target }.
tossup-round-start = جولة { $round } يبدأ.
tossup-round-start-brief = جولة { $round }.
tossup-your-turn =
    دورك. درجاتك المصرفية هي { $score }; لفة { $dice } { $dice ->
        [one] يموت
       *[other] النرد
    } للبدء.
tossup-player-turn =
    { $player }دور مع { $score } النقاط المصرفية و { $dice } { $dice ->
        [one] يموت
       *[other] النرد
    }.
tossup-your-turn-brief = دورك: { $score } نقاط.
tossup-player-turn-brief = { $player }دور: { $score } نقاط.
tossup-you-roll = لقد تدحرجت { $results }.
tossup-player-rolls = { $player } توالت { $results }.
tossup-you-roll-safe-brief =
    { $fresh ->
        [yes] أنت: { $results }; بدوره الإجمالي { $turn_points }; مجموعة جديدة من { $dice_count }.
       *[no] أنت: { $results }; بدوره الإجمالي { $turn_points }; { $dice_count } غادر.
    }
tossup-player-rolls-safe-brief =
    { $fresh ->
        [yes] { $player }: { $results }; بدوره الإجمالي { $turn_points }; مجموعة جديدة من { $dice_count }.
       *[no] { $player }: { $results }; بدوره الإجمالي { $turn_points }; { $dice_count } غادر.
    }
tossup-result-green = { $count } أخضر
tossup-result-yellow = { $count } أصفر
tossup-result-red = { $count } أحمر
tossup-you-have-points =
    لقد وضعت جانبا { $gained } أخضر { $gained ->
        [one] يموت
       *[other] النرد
    }. إجمالي دورك هو { $turn_points }مع { $dice_count } { $dice_count ->
        [one] يموت
       *[other] النرد
    } متبقي.
tossup-player-has-points =
    { $player } يوضع جانبا { $gained } أخضر { $gained ->
        [one] يموت
       *[other] النرد
    } وله { $turn_points } نقاط الانعطاف مع { $dice_count } { $dice_count ->
        [one] يموت
       *[other] النرد
    } متبقي.
tossup-you-get-fresh = كل قالب أخضر. تتلقى مجموعة جديدة من { $count } النرد وقد يتدحرج مرة أخرى أو البنك.
tossup-player-gets-fresh = كل قالب أخضر. { $player } يتلقى مجموعة جديدة من { $count } النرد.
tossup-you-bust =
    { $variant ->
        [Standard] الضوء الأحمر: لم تقم بتدحرج اللون الأخضر وعلى الأقل لون أحمر واحد. ينتهي دورك وتخسر ​​ { $points } النقاط غير المصرفية.
       *[PlayAural] جميع النرد الملفوفة باللون الأحمر. ينتهي دورك وتخسر ​​ { $points } النقاط غير المصرفية.
    }
tossup-player-busts =
    { $variant ->
        [Standard] الضوء الأحمر: { $player } لم يتدحرج باللون الأخضر وعلى الأقل باللون الأحمر، منهيًا الدور وخسارة { $points } النقاط غير المصرفية.
       *[PlayAural] كل { $player }أحجار النرد الملقاة باللون الأحمر، وتنتهي الدورة وتخسر ​​ { $points } النقاط غير المصرفية.
    }
tossup-you-bust-brief = أنت: { $results }; اعتقال؛ خسارة { $points }.
tossup-player-busts-brief = { $player }: { $results }; اعتقال؛ يخسر { $points }.
tossup-you-bank = أنت البنك { $points } نقطة، ليصل مجموع درجاتك إلى { $total }.
tossup-player-banks = { $player } البنوك { $points } نقطة ليصل مجموع نقاطهم إلى { $total }.
tossup-you-bank-brief = أنت البنك { $points }; المجموع { $total }.
tossup-player-banks-brief = { $player } البنوك { $points }; المجموع { $total }.
tossup-you-trigger-final-turns =
    لقد تجاوزت { $target }-نقطة العتبة مع { $score }. { $count ->
        [one] يتلقى اللاعب المتبقي دورة أخيرة.
       *[other] الباقي { $count } يحصل كل لاعب على دور أخير.
    }
tossup-player-triggers-final-turns =
    { $player } يتجاوز { $target }-نقطة العتبة مع { $score }. { $count ->
        [one] يتلقى اللاعب المتبقي دورة أخيرة.
       *[other] الباقي { $count } يحصل كل لاعب على دور أخير.
    }
tossup-you-trigger-final-turns-brief =
    قمت بتعيين النتيجة للتغلب على { $score }; { $count } { $count ->
        [one] يبقى بدوره.
       *[other] تبقى المنعطفات.
    }
tossup-player-triggers-final-turns-brief =
    { $player } يحدد النتيجة للفوز على { $score }; { $count } { $count ->
        [one] يبقى بدوره.
       *[other] تبقى المنعطفات.
    }
tossup-you-win = لقد فزت في لعبة Toss Up مع { $score } نقاط.
tossup-winner = { $player } يفوز بالإرم مع { $score } نقاط.
tossup-you-win-brief = لقد فزت: { $score }.
tossup-winner-brief = { $player } الانتصارات: { $score }.
tossup-tie-tiebreaker = { $players } مرتبطة بأعلى الدرجات فوق الهدف. هؤلاء اللاعبون فقط هم الذين يستمرون في جولة الشوط الفاصل.
tossup-tie-tiebreaker-brief = الشوط الفاصل: { $players }.
tossup-tiebreaker-round-start = الجولة الفاصلة { $round } يبدأ لـ { $players }.
tossup-tiebreaker-round-start-brief = الجولة الفاصلة { $round }: { $players }.
tossup-your-turn-awaiting-roll =
    دورك لم يبدأ بعد. لديك { $score } النقاط المصرفية و { $dice_count } { $dice_count ->
        [one] يموت
       *[other] النرد
    } مستعد.
tossup-player-turn-awaiting-roll =
    { $player } لم توالت بعد. لديهم { $score } النقاط المصرفية و { $dice_count } { $dice_count ->
        [one] يموت
       *[other] النرد
    } مستعد.
tossup-your-turn-status =
    آخر لفة لك كانت { $results }. لديك { $turn_points } نقاط التحول غير المصرفية, { $score } النقاط المحفوظة و { $dice_count } { $dice_count ->
        [one] يموت
       *[other] النرد
    } على استعداد للفة.
tossup-player-turn-status =
    { $player } آخر توالت { $results }. لديهم { $turn_points } نقاط الانعطاف غير المصرفية، { $score } النقاط المحفوظة و { $dice_count } { $dice_count ->
        [one] يموت
       *[other] النرد
    } على استعداد للفة.
tossup-confirm-risky-roll =
    { $winning ->
        [yes] الخدمات المصرفية الآن ستضعك في المقدمة مع { $total } النقاط فوق { $target }- عتبة النقطة.
       *[no] لديك حاليا { $points } نقاط التحول غير المصرفية.
    } المتداول { $dice } { $dice ->
        [one] يموت
       *[other] النرد
    } لديه حوالي أ { $risk } فرصة في المئة من التمثال النصفي. اضغط على Roll مرة أخرى داخل { $seconds } ثواني للتأكيد، أو البنك لحماية النقاط.
tossup-set-rules-variant = القواعد: { $variant }
tossup-select-rules-variant = حدد قواعد النرد والتمثال النصفي:
tossup-option-changed-rules = تم تغيير القواعد إلى { $variant }.
tossup-desc-rules-variant = يستخدم الطراز الكلاسيكي ثلاثة وجوه خضراء ووجهين أصفر ووجه أحمر لكل قالب؛ اللفة التي لا تحتوي على اللون الأخضر وعلى الأقل لون أحمر واحد هي تمثال نصفي. التسامح يمنح الألوان الثلاثة احتمالات متساوية ويفشل فقط على اللون الأحمر.
tossup-desc-target-score = تدخل اللعبة في استجابتها النهائية بعد أن يحصل اللاعب على أكثر من هذه النتيجة (الافتراضي 100، النطاق 20-500).
tossup-set-starting-dice = النرد لكل مجموعة: { $count }
tossup-enter-starting-dice = أدخل عدد قطع النرد في كل مجموعة جديدة:
tossup-option-changed-dice = تم تغيير النرد لكل مجموعة إلى { $count }.
tossup-desc-starting-dice = اختر عدد النرد الذي يبدأ كل دور ثم يعود بعد أن يصبح كل حجر نرد أخضر (الافتراضي 10، النطاق 5-20).
tossup-rules-standard = كلاسيك
tossup-rules-PlayAural = غفور
tossup-rules-standard-desc = ثلاثة وجوه خضراء ووجهان أصفر ووجه أحمر. تمثال نصفي بدون لون أخضر مع لون أحمر واحد على الأقل.
tossup-rules-PlayAural-desc = احتمالات متساوية لجميع الألوان الثلاثة. تمثال نصفي فقط عندما يكون كل نرد ملفوف باللون الأحمر.
tossup-error-roll-not-playing = لا يمكنك التدحرج لأن Toss Up ليس قيد التقدم حاليًا.
tossup-error-roll-no-turn = لا يمكنك التدحرج لأن Toss Up ليس لديه دور نشط الآن.
tossup-error-roll-not-your-turn = لا يمكنك التدحرج أثناء ذلك { $player }دور. انتظر حتى يصل إليك الدور.
tossup-error-bank-not-playing = لا يمكنك إجراء المعاملات المصرفية لأن Toss Up ليست قيد التقدم حاليًا.
tossup-error-bank-no-turn = لا يمكنك إجراء المعاملات المصرفية لأن Toss Up ليس لها دور نشط في الوقت الحالي.
tossup-error-bank-not-your-turn = لا يمكنك إجراء المعاملات المصرفية خلال { $player }دور. انتظر حتى يصل إليك الدور.
tossup-error-bank-roll-first = لفة مرة واحدة على الأقل قبل المصرفية. قد يتم وضع لفة صفراء بالكامل مقابل صفر نقطة لإنهاء دورك.
tossup-error-spectator-action = يمكن للمشاهدين التحقق من حالة Toss Up العامة، لكن لا يمكنهم رمي النقاط أو جمعها.
tossup-error-status-not-playing = حالة الانعطاف غير متاحة لأن Toss Up ليست قيد التقدم حاليًا.
tossup-error-status-no-turn = حالة الدور غير متاحة لأن Toss Up لا يوجد بها لاعب نشط في الوقت الحالي.
tossup-error-target-out-of-range = العتبة المستهدفة هي { $value }; يجب أن يكون من { $min } من خلال { $max } نقاط.
tossup-error-dice-out-of-range = حجم المجموعة الجديدة هو { $value }; يجب أن يكون من { $min } من خلال { $max } النرد.
tossup-error-rules-variant = قيمة القواعد "{ $variant }" غير مدعومة. اختر الكلاسيكية أو المتسامحة.
tossup-line-format = { $rank }. { $player }: { $points }
