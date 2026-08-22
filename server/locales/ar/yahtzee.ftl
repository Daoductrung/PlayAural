game-name-yahtzee = يهتزي
yahtzee-roll = إعادة التدوير ({ $count } لليسار)
yahtzee-roll-all = لفة النرد
yahtzee-score-ones =
    منها لـ { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-twos =
    اثنان لـ { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-threes =
    الثلاثات ل { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-fours =
    أربعات لـ { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-fives =
    الخمسات ل { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-sixes =
    الستات ل { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-three-kind =
    ثلاثة من نفس النوع لـ { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-four-kind =
    أربعة من نفس النوع لـ { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-full-house =
    منزل كامل لـ { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-small-straight =
    صغير مستقيم لـ { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-large-straight =
    كبير مستقيم ل { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-score-yahtzee =
    ياهتزي لـ { $points } { $points ->
        [one] نقطة
       *[other] نقاط
    }
yahtzee-score-chance =
    فرصة ل { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    }
yahtzee-you-rolled =
    لقد تدحرجت: { $dice }. { $remaining ->
        [0] اختر فئة التسجيل.
       *[other]
            { $remaining } { $remaining ->
                [one] لفة
               *[other] لفات
            } غادر.
    }
yahtzee-player-rolled =
    { $player } توالت: { $dice }. { $remaining ->
        [0] يجب عليهم اختيار فئة التسجيل.
       *[other]
            { $remaining } { $remaining ->
                [one] لفة
               *[other] لفات
            } غادر.
    }
yahtzee-you-rolled-brief = لقد تدحرجت: { $dice }.
yahtzee-player-rolled-brief = { $player } توالت: { $dice }.
yahtzee-you-scored =
    لقد سجلت { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    } في { $category }.
yahtzee-player-scored =
    { $player } سجل { $points } { $points ->
        [one] نقطة
       *[other] النقاط
    } في { $category }.
yahtzee-you-scored-brief = { $points } في { $category }.
yahtzee-player-scored-brief = { $player }: { $points } في { $category }.
yahtzee-you-bonus = مكافأة ياهتزي! +100 نقطة
yahtzee-player-bonus = { $player } حصلت على مكافأة Yahtzee! +100 نقطة
yahtzee-you-bonus-brief = مكافأة ياهتزي +100.
yahtzee-player-bonus-brief = { $player }: مكافأة ياهتزي +100.
yahtzee-you-upper-bonus = مكافأة القسم العلوي! +35 نقطة ({ $total } في القسم العلوي)
yahtzee-player-upper-bonus = { $player } حصلت على مكافأة القسم العلوي! +35 نقطة ({ $total } في القسم العلوي)
yahtzee-you-upper-bonus-brief = المكافأة العليا +35.
yahtzee-player-upper-bonus-brief = { $player }: المكافأة العليا، +35.
yahtzee-you-upper-bonus-missed = غاب عن مكافأة القسم العلوي. لقد سجلت { $total }; كنت في حاجة { $needed } أكثر.
yahtzee-player-upper-bonus-missed = { $player } غاب عن مكافأة القسم العلوي مع { $total } في القسم العلوي { $needed } قصير.
yahtzee-you-upper-bonus-missed-brief = المكافأة العليا مفقودة؛ { $needed } قصير.
yahtzee-player-upper-bonus-missed-brief = { $player }: المكافأة العليا غاب، { $needed } قصير.
yahtzee-check-scoresheet = التحقق من بطاقة النتائج
yahtzee-check-all-scorecards = التحقق من بطاقة النتائج لجميع اللاعبين
yahtzee-select-scorecard-player = اختر بطاقة أداء اللاعب.
yahtzee-scorecard-no-players = لا يوجد لدى أي لاعب نشط بطاقات أداء في هذه اللعبة حتى الآن.
yahtzee-scorecard-player-unavailable = هذا اللاعب لم يعد متاحًا للعرض. افتح قائمة بطاقة الأداء مرة أخرى واختر لاعبًا نشطًا.
yahtzee-view-dice = تحقق من اليد
yahtzee-your-dice = النرد الخاص بك: { $dice }.
yahtzee-your-dice-kept = النرد الخاص بك: { $dice }. حفظ: { $kept }.
yahtzee-current-dice = { $player }النرد: { $dice }.
yahtzee-current-dice-kept = { $player }النرد: { $dice }. حفظ: { $kept }.
yahtzee-not-rolled = اللاعب الحالي لم يتدحرج بعد.
yahtzee-scoresheet-header = { $player }بطاقة الأداء
yahtzee-scoresheet-upper = القسم العلوي:
yahtzee-scoresheet-lower = القسم السفلي:
yahtzee-scoresheet-upper-total-bonus = المجموع العلوي: { $total } (مكافأة: +35)
yahtzee-scoresheet-upper-total-needed = المجموع العلوي: { $total } ({ $needed } المزيد للحصول على المكافأة)
yahtzee-scoresheet-yahtzee-bonus = مكافآت ياهتزي: { $count } × 100 = { $total }
yahtzee-scoresheet-grand-total = مجموع الدرجات: { $total }
yahtzee-category-ones =
yahtzee-category-twos = ثنائي
yahtzee-category-threes = الثلاثات
yahtzee-category-fours = اربعة
yahtzee-category-fives = خمسات
yahtzee-category-sixes = الستات
yahtzee-category-three-kind = ثلاثة من نفس النوع
yahtzee-category-four-kind = أربعة من نفس النوع
yahtzee-category-full-house = فول هاوس
yahtzee-category-small-straight = صغير مستقيم
yahtzee-category-large-straight = مستقيم كبير
yahtzee-category-yahtzee = يهتزي
yahtzee-category-chance = فرصة
yahtzee-you-win =
    تربح مع { $score } { $score ->
        [one] نقطة
       *[other] النقاط
    }!
yahtzee-player-wins =
    { $player } يفوز مع { $score } { $score ->
        [one] نقطة
       *[other] النقاط
    }!
yahtzee-winners-tie = إنها ربطة عنق! { $players } كل شيء سجل { $score } نقاط!
yahtzee-set-rounds = عدد الألعاب: { $rounds }
yahtzee-enter-rounds = أدخل عدد الألعاب (1-10):
yahtzee-option-changed-rounds = تم ضبط عدد الألعاب على { $rounds }.
yahtzee-desc-num-games = كم عدد بطاقات أداء Yahtzee الكاملة التي تم لعبها قبل مقارنة المجاميع النهائية (الافتراضي 1، النطاق 1-10).
yahtzee-no-rolls-left = لم يبق لديك أي لفات. اختر فئة تسجيل مفتوحة لإنهاء دورك.
yahtzee-roll-first = قم برمي النرد قبل اختيار فئة التسجيل.
yahtzee-category-filled = هذه الفئة لديها بالفعل النتيجة. اختر فئة لا تزال مفتوحة في بطاقة الأداء الخاصة بك.
yahtzee-joker-upper-required = قاعدة الجوكر: لأن هذا ياهتزي يظهر { $face }، يجب عليك تسجيل مربع القسم العلوي لـ { $face } قبل أي فئة أخرى.
yahtzee-joker-lower-required = قاعدة الجوكر: مربع القسم العلوي لـ { $face } تم ملؤه بالفعل، لذلك يجب عليك اختيار فئة القسم السفلي المفتوحة قبل استخدام مربع القسم العلوي الآخر.
