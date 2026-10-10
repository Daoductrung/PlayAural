# Age of Heroes game messages
# A civilization-building card game for 2-6 players

# Game name
game-name-ageofheroes = عصر الأبطال

# Tribes
ageofheroes-tribe-egyptians = المصريون
ageofheroes-tribe-romans = الرومان
ageofheroes-tribe-greeks = الإغريق
ageofheroes-tribe-babylonians = البابليون
ageofheroes-tribe-celts = الكلت
ageofheroes-tribe-chinese = الصينيون

# Special Resources (for monuments)
ageofheroes-special-limestone = الحجر الجيري
ageofheroes-special-concrete = الخرسانة
ageofheroes-special-marble = الرخام
ageofheroes-special-bricks = الطوب
ageofheroes-special-sandstone = الحجر الرملي
ageofheroes-special-granite = الغرانيت

# Standard Resources
ageofheroes-resource-iron = الحديد
ageofheroes-resource-wood = الخشب
ageofheroes-resource-grain = الحبوب
ageofheroes-resource-stone = الحجر
ageofheroes-resource-gold = الذهب

# Events
ageofheroes-event-population-growth = النمو السكاني
ageofheroes-event-earthquake = زلزال
ageofheroes-event-eruption = ثوران بركاني
ageofheroes-event-hunger = مجاعة
ageofheroes-event-barbarians = البرابرة
ageofheroes-event-olympics = الألعاب الأولمبية
ageofheroes-event-hero = بطل
ageofheroes-event-fortune = حظ
# Buildings
ageofheroes-building-army = جيش
ageofheroes-building-fortress = حصن
ageofheroes-building-general = قائد
ageofheroes-building-road = طريق
ageofheroes-building-city = مدينة

# Actions
ageofheroes-action-tax-collection = جمع الضرائب
ageofheroes-action-construction = البناء
ageofheroes-action-war = حرب
ageofheroes-action-do-nothing = عدم فعل شيء
ageofheroes-play = لعب
ageofheroes-play-card-label = لعب { $card }
ageofheroes-card-count = { $count } { $card }
ageofheroes-player-tribe = { $player } ({ $tribe })
ageofheroes-player-tribe-direction = { $player } ({ $tribe }) - { $direction }

# War goals
ageofheroes-war-conquest = الفتح
ageofheroes-war-plunder = النهب
ageofheroes-war-destruction = التدمير

# Game options
ageofheroes-set-victory-cities = مدن النصر: { $cities }
ageofheroes-enter-victory-cities = أدخل عدد المدن اللازمة للفوز (3-7)
ageofheroes-set-victory-monument = اكتمال النصب التذكاري: { $progress }%
ageofheroes-set-max-hand = الحد الأقصى لحجم اليد: { $cards } بطاقة

# Option change announcements
ageofheroes-option-changed-victory-cities = يتطلب الفوز السيطرة على { $cities } مدينة.
ageofheroes-desc-victory-cities = عدد المدن التي يجب أن يسيطر عليها طرف للفوز في عصر الأبطال (الافتراضي 5، النطاق 3-7).
ageofheroes-option-changed-victory-monument = تم تعيين حدّ اكتمال النصب التذكاري إلى { $progress }%.
ageofheroes-option-changed-max-hand = تم تعيين الحد الأقصى لحجم اليد إلى { $cards } بطاقة.
# Setup phase
ageofheroes-setup-start = أنت زعيم قبيلة { $tribe }. مورد نصبك التذكاري الخاص هو { $special }. ارمِ النرد لتحديد ترتيب الأدوار.
ageofheroes-roll-dice = ارمِ النرد
ageofheroes-war-roll-dice = ارمِ النرد
ageofheroes-dice-result = حصلت على { $total } ({ $die1 } + { $die2 }).
ageofheroes-dice-result-other = حصل { $player } على { $total }.
ageofheroes-dice-tie = تعادل عدة لاعبين عند { $total }. إعادة الرمي...
ageofheroes-first-player = حصل { $player } على أعلى نتيجة { $total } ويبدأ أولًا.
ageofheroes-first-player-you = بـ { $total } نقطة، تبدأ أولًا.
ageofheroes-whose-turn-setup = مرحلة الإعداد. في انتظار { $players } لرمي النرد لتحديد ترتيب الأدوار.
ageofheroes-whose-turn-setup-resolving = مرحلة الإعداد. اكتملت جميع عمليات الرمي؛ يجري تحديد ترتيب الأدوار.
ageofheroes-whose-turn-prepare = مرحلة التحضير. يجري حلّ الأحداث والكوارث.
ageofheroes-whose-turn-fair = مرحلة السوق. لا يزال بإمكان { $players } المقايضة.
ageofheroes-whose-turn-fair-resolving = مرحلة السوق. يجري إتمام المقايضات.
ageofheroes-whose-turn-road = مرحلة إذن الطريق. على { $responder } الردّ على طلب الطريق من { $requester }.
ageofheroes-whose-turn-olympics = أُعلنت الحرب. على { $defender } أن يقرر ما إذا كان سيستخدم الألعاب الأولمبية ضد { $attacker }.
ageofheroes-whose-turn-war-attack = التحضير للحرب. يختار { $attacker } قواته ضد { $defender }.
ageofheroes-whose-turn-war-defense = التحضير للحرب. يختار { $defender } قوات الدفاع ضد { $attacker }.
ageofheroes-whose-turn-war-roll = مرحلة المعركة. في انتظار { $players } لرمي النرد.
ageofheroes-whose-turn-game-over = انتهت اللعبة.

# Preparation phase
ageofheroes-prepare-start = على اللاعبين لعب بطاقات الأحداث والتخلص من الكوارث.
ageofheroes-prepare-your-turn = لديك { $count } { $count ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
} للعبها أو للتخلص منها.
# Events played/discarded
ageofheroes-population-growth = يلعب { $player } النمو السكاني ويبني مدينة جديدة.
ageofheroes-population-growth-you = تلعب النمو السكاني وتبني مدينة جديدة.
ageofheroes-discard-card = يتخلّص { $player } من { $card }.
ageofheroes-discard-card-you = تتخلّص من { $card }.
ageofheroes-earthquake = يضرب زلزال قبيلة { $player }؛ تدخل الجيوش { GENDER_TERM($player_gender, "possessive-determiner") } مرحلة التعافي.
ageofheroes-earthquake-you = يضرب زلزال قبيلتك؛ تدخل جيوشك مرحلة التعافي.
ageofheroes-eruption = يدمّر ثوران بركاني إحدى مدن { $player }.
ageofheroes-eruption-you = يدمّر ثوران بركاني إحدى مدنك.
# Disaster effects
ageofheroes-hunger-strikes = تضرب المجاعة.
ageofheroes-lose-card-hunger = تفقد { $card }.
ageofheroes-barbarians-attack = يهاجم البرابرة موارد { $player }.
ageofheroes-barbarians-attack-you = يهاجم البرابرة مواردك.
ageofheroes-lose-card-barbarians = تفقد { $card }.
ageofheroes-block-with-card = يصدّ { $player } الكارثة باستخدام { $card }.
ageofheroes-block-with-card-you = تصدّ الكارثة باستخدام { $card }.

# Targeted disaster cards (Earthquake/Eruption)
ageofheroes-select-disaster-target = اختر هدفًا لـ { $card }.
ageofheroes-no-targets = لا توجد أهداف صالحة متاحة.
ageofheroes-earthquake-strikes-you = يلعب { $attacker } زلزالًا ضدك. جيوشك معطّلة.
ageofheroes-earthquake-strikes = يلعب { $attacker } زلزالًا ضد { $player }.
ageofheroes-armies-disabled = { $count } { $count ->
    [one] جيش معطّل
    [two] جيشان معطّلان
    [few] جيوش معطّلة
    [many] جيشًا معطّلًا
    *[other] جيش معطّل
} لدور واحد.
ageofheroes-eruption-strikes-you = يلعب { $attacker } ثورانًا بركانيًا ضدك. تُدمَّر إحدى مدنك.
ageofheroes-eruption-strikes = يلعب { $attacker } ثورانًا بركانيًا ضد { $player }.
ageofheroes-city-destroyed = دُمّرت مدينة بفعل الثوران البركاني.

# Fair phase
ageofheroes-fair-start = يبزغ النهار في السوق.
ageofheroes-fair-draw-base = تسحب { $count } { $count ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
}.
ageofheroes-fair-draw-roads = تسحب { $count } { $count ->
    [one] بطاقة إضافية
    [two] بطاقتان إضافيتان
    [few] بطاقات إضافية
    [many] بطاقة إضافية
    *[other] بطاقة إضافية
} بفضل شبكة طرقك.
ageofheroes-fair-draw-other = يسحب { $player } { $count } { $count ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
}.
# Trading/Auction
ageofheroes-auction-start = يبدأ المزاد.
ageofheroes-offer-made = يعرض { $player } { $card } مقابل { $wanted }.
ageofheroes-offer-made-you = تعرض { $card } مقابل { $wanted }.
ageofheroes-trade-accepted = يقبل { $player } عرض { $other } ويقايض { $give } بـ { $receive }.
ageofheroes-trade-accepted-you = تقبل عرض { $other } وتحصل على { $receive }.
ageofheroes-trade-cancelled = يسحب { $player } العرض { GENDER_TERM($player_gender, "possessive-determiner") } لـ { $card }.
ageofheroes-trade-cancelled-you = تسحب عرضك لـ { $card }.
ageofheroes-stop-trading = إيقاف المقايضة
ageofheroes-select-request = أنت تعرض { $card }. ماذا تريد في المقابل؟
ageofheroes-cancel = إلغاء
ageofheroes-left-auction = يغادر { $player }.
ageofheroes-left-auction-you = تغادر السوق.
ageofheroes-already-left-auction = لقد غادرت السوق بالفعل.
ageofheroes-any-card = أي بطاقة
ageofheroes-cannot-trade-own-special = لا يمكنك مقايضة مورد نصبك التذكاري الخاص.
ageofheroes-resource-not-in-game = هذا المورد الخاص غير مستخدم في هذه اللعبة.

# Main play phase
ageofheroes-play-start = مرحلة اللعب.
ageofheroes-day = اليوم { $day }
ageofheroes-draw-card = يسحب { $player } بطاقة من المجموعة.
ageofheroes-draw-card-you = تسحب { $card } من المجموعة.
ageofheroes-draw-card-brief = يسحب { $player }.
ageofheroes-draw-card-you-brief = سحب: { $card }.
ageofheroes-your-action = ماذا تريد أن تفعل؟
ageofheroes-your-action-brief = الإجراء؟

# Tax Collection
ageofheroes-tax-collection = يختار { $player } جمع الضرائب: { $cities } { $cities ->
    [one] مدينة
    [two] مدينتان
    [few] مدن
    [many] مدينة
    *[other] مدينة
} تجمع { $cards } { $cards ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
}.
ageofheroes-tax-collection-you = تختار جمع الضرائب: { $cities } { $cities ->
    [one] مدينة
    [two] مدينتان
    [few] مدن
    [many] مدينة
    *[other] مدينة
} تجمع { $cards } { $cards ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
}.
ageofheroes-tax-collection-brief = ضريبة { $player }: { $cards } من { $cities }.
ageofheroes-tax-collection-you-brief = ضريبة: { $cards } من { $cities }.
ageofheroes-tax-no-city = جمع الضرائب: ليس لديك مدن باقية. تخلّص من بطاقة لسحب بطاقة جديدة.
ageofheroes-tax-no-city-done = يختار { $player } جمع الضرائب لكن لا مدن لديه، مما يدفع { GENDER_TERM($player_gender, "object") } إلى تبديل بطاقة.
ageofheroes-tax-no-city-done-you = جمع الضرائب: بدّلت { $card } ببطاقة جديدة.

# Construction
ageofheroes-construction-menu = ماذا تريد أن تبني؟
ageofheroes-construction-done = بنى { $player } { $building }.
ageofheroes-construction-done-you = بنيت { $building }.
ageofheroes-build-cost-resource = { $count ->
    [one] { $resource }
    *[other] { $count }x { $resource }
}
ageofheroes-build-menu-label = { $building } ({ $cost })
ageofheroes-construction-stop = إيقاف البناء
ageofheroes-construction-stopped = قررت إيقاف البناء.
ageofheroes-road-select-neighbor = اختر الجار الذي تريد بناء طريق إليه.
ageofheroes-direction-left = إلى يسارك
ageofheroes-direction-right = إلى يمينك
ageofheroes-road-request-sent = تم إرسال طلب الطريق. في انتظار موافقة الجار.
ageofheroes-road-request-received = يطلب { $requester } الإذن ببناء طريق إلى قبيلتك.
ageofheroes-road-request-denied-you = رفضت طلب الطريق.
ageofheroes-road-request-denied = رفض { $denier } طلب طريقك.
ageofheroes-road-built = ارتبطت { $tribe1 } و{ $tribe2 } الآن بطريق.
ageofheroes-road-built-you = أصبحت أنت و{ $tribe2 } مرتبطين الآن بطريق.
ageofheroes-road-no-target = لا توجد قبائل مجاورة متاحة لبناء الطرق.
ageofheroes-approve = موافقة
ageofheroes-deny = رفض
# Do Nothing
ageofheroes-do-nothing = يمرر { $player }.
ageofheroes-do-nothing-you = تمرر...
ageofheroes-do-nothing-brief = يمرر { $player }.
ageofheroes-do-nothing-you-brief = تمرير.
ageofheroes-confirm-do-nothing = التمرير يتخطّى إجراءك لهذا الدور. اضغط عدم فعل شيء مرة أخرى للتأكيد.

# War
ageofheroes-war-declare = يعلن { $attacker } الحرب على { $defender }. الهدف: { $goal }.
ageofheroes-war-prepare = اختر جيوشك لـ { $action }.
ageofheroes-war-no-army = ليس لديك أي جيوش أو بطاقات أبطال متاحة.
ageofheroes-war-no-tribe = ليس لديك قبيلة في هذه المعركة.
ageofheroes-war-no-targets = لا توجد أهداف صالحة للحرب.
ageofheroes-war-no-valid-goal = لا توجد أهداف حرب صالحة ضد هذا الهدف.
ageofheroes-war-invalid-forces = لم تعد تلك القوات صالحة. راجع جيوشك وقادتك وبطاقات الأبطال المتاحة.
ageofheroes-war-select-target = اختر اللاعب الذي تريد مهاجمته.
ageofheroes-war-select-goal = اختر هدف حربك.
ageofheroes-war-prepare-attack = اختر قوات هجومك.
ageofheroes-war-prepare-defense = يهاجمك { $attacker }؛ اختر قوات دفاعك.
ageofheroes-war-force-add-armies = أضف جيشًا واحدًا. الجيوش الملتزمة: { $current } من { $max }.
ageofheroes-war-force-remove-armies = أزل جيشًا واحدًا. الجيوش الملتزمة: { $current } من { $max }.
ageofheroes-war-force-add-generals = أضف قائدًا واحدًا. القادة الملتزمون: { $current } من { $max }.
ageofheroes-war-force-remove-generals = أزل قائدًا واحدًا. القادة الملتزمون: { $current } من { $max }.
ageofheroes-war-force-add-hero-armies = أضف بطلًا كجيش. جيوش الأبطال الملتزمة: { $current } من { $max }.
ageofheroes-war-force-remove-hero-armies = أزل جيش بطل واحدًا. جيوش الأبطال الملتزمة: { $current } من { $max }.
ageofheroes-war-force-add-hero-generals = أضف بطلًا كقائد. قادة الأبطال الملتزمون: { $current } من { $max }.
ageofheroes-war-force-remove-hero-generals = أزل قائد بطل واحدًا. قادة الأبطال الملتزمون: { $current } من { $max }.
ageofheroes-war-force-unit-armies = جيوش
ageofheroes-war-force-unit-generals = قادة
ageofheroes-war-force-unit-hero-armies = جيوش أبطال
ageofheroes-war-force-unit-hero-generals = قادة أبطال
ageofheroes-war-force-max = بلغت الحد الأقصى بالفعل: { $unit } ({ $max }).
ageofheroes-war-force-min = لا شيء ملتزم: { $unit }.
ageofheroes-war-force-updated = القوات الملتزمة: { $armies } جيوش، { $generals } قادة، { $hero_armies } جيوش أبطال، { $hero_generals } قادة أبطال.
ageofheroes-war-attack = هجوم...
ageofheroes-war-defend = دفاع...
ageofheroes-war-clear-forces = مسح القوات
ageofheroes-war-prepared = قواتك: { $armies } { $armies ->
    [one] جيش
    [two] جيشان
    [few] جيوش
    [many] جيشًا
    *[other] جيش
}{ $generals ->
    [0] {""}
    [one] {" وقائد واحد"}
    *[other] { " و" }{ $generals } قادة
}{ $heroes ->
    [0] {""}
    [one] {" وبطل واحد"}
    *[other] { " و" }{ $heroes } أبطال
}.
ageofheroes-war-roll-you = ترمي { $roll }.
ageofheroes-war-roll-other = يرمي { $player } { $roll }.
ageofheroes-war-bonuses-you = { $general ->
    [0] { $fortress ->
        [0] {""}
        [1] +1 من الحصن = { $total } الإجمالي
        *[other] +{ $fortress } من الحصون = { $total } الإجمالي
    }
    *[other] { $fortress ->
        [0] +{ $general } من القائد = { $total } الإجمالي
        [1] +{ $general } من القائد، +1 من الحصن = { $total } الإجمالي
        *[other] +{ $general } من القائد، +{ $fortress } من الحصون = { $total } الإجمالي
    }
}
ageofheroes-war-bonuses-other = { $general ->
    [0] { $fortress ->
        [0] {""}
        [1] { $player }: +1 من الحصن = { $total } الإجمالي
        *[other] { $player }: +{ $fortress } من الحصون = { $total } الإجمالي
    }
    *[other] { $fortress ->
        [0] { $player }: +{ $general } من القائد = { $total } الإجمالي
        [1] { $player }: +{ $general } من القائد، +1 من الحصن = { $total } الإجمالي
        *[other] { $player }: +{ $general } من القائد، +{ $fortress } من الحصون = { $total } الإجمالي
    }
}
ageofheroes-war-bonuses-you-brief = مكافأة +{ $bonus } = { $total }.
ageofheroes-war-bonuses-other-brief = مكافأة { $player } +{ $bonus } = { $total }.
# Battle
ageofheroes-battle-start = تبدأ المعركة. { $att_armies } { $att_armies ->
    [one] جيش
    [two] جيشان
    [few] جيوش
    [many] جيشًا
    *[other] جيش
} لـ { $attacker } ضد { $def_armies } { $def_armies ->
    [one] جيش
    [two] جيشان
    [few] جيوش
    [many] جيشًا
    *[other] جيش
} لـ { $defender }.
ageofheroes-battle-start-brief = معركة: { $attacker } { $att_armies } ضد { $defender } { $def_armies }.
ageofheroes-dice-roll-detailed = يرمي { $name } { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } من القائد" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 من الحصن" }
    *[other] { " + { $fortress } من الحصون" }
} = { $total }.
ageofheroes-dice-roll-detailed-you = ترمي { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } من القائد" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 من الحصن" }
    *[other] { " + { $fortress } من الحصون" }
} = { $total }.
ageofheroes-round-attacker-wins = يفوز { $attacker } بالجولة ({ $att_total } مقابل { $def_total }). يخسر { $defender } جيشًا.
ageofheroes-round-defender-wins = يدافع { $defender } بنجاح ({ $def_total } مقابل { $att_total }). يخسر { $attacker } جيشًا.
ageofheroes-round-draw = يتعادل الطرفان عند { $total }. لم تُخسر أي جيوش.
ageofheroes-round-attacker-wins-brief = { $attacker } { $att_total } يتغلب على { $defender } { $def_total }. { $defender } -1 جيش.
ageofheroes-round-defender-wins-brief = { $defender } { $def_total } يتغلب على { $attacker } { $att_total }. { $attacker } -1 جيش.
ageofheroes-round-draw-brief = تعادل { $total }. لا خسارة.
ageofheroes-you-win-battle-as-attacker = تهزم { $defender }.
ageofheroes-you-lose-battle-as-defender = يهزمك { $attacker }.
ageofheroes-battle-victory-attacker = يهزم { $attacker } { $defender }.
ageofheroes-you-lose-battle-as-attacker = يدافع { $defender } بنجاح ضدك.
ageofheroes-you-win-battle-as-defender = تدافع بنجاح ضد { $attacker }.
ageofheroes-battle-victory-defender = يدافع { $defender } بنجاح ضد { $attacker }.
ageofheroes-you-draw-battle = تخسر أنت و{ $opponent } جميع القوات الملتزمة في المعركة.
ageofheroes-battle-mutual-defeat = يخسر كل من { $attacker } و{ $defender } جميع القوات الملتزمة في المعركة.
ageofheroes-battle-continue = متابعة المعركة.
# War outcomes
ageofheroes-conquest-success = يفتح { $attacker } { $count } { $count ->
    [one] مدينة
    [two] مدينتان
    [few] مدن
    [many] مدينة
    *[other] مدينة
} من { $defender }.
ageofheroes-plunder-success = ينهب { $attacker } { $count } { $count ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
} من { $defender }.
ageofheroes-destruction-success = يدمّر { $attacker } { $count } { $count ->
    [one] مورد
    [two] موردان
    [few] موارد
    [many] موردًا
    *[other] مورد
} من نصب { $defender } التذكاري.
ageofheroes-conquest-success-brief = يأخذ { $attacker } { $count } { $count ->
    [one] مدينة
    [two] مدينتان
    [few] مدن
    [many] مدينة
    *[other] مدينة
} من { $defender }.
ageofheroes-plunder-success-brief = يأخذ { $attacker } { $count } { $count ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
} من { $defender }.
ageofheroes-destruction-success-brief = يدمّر { $attacker } { $count } { $count ->
    [one] مورد نصب
    [two] موردَي نصب
    [few] موارد نصب
    [many] مورد نصب
    *[other] مورد نصب
} من { $defender }.
ageofheroes-army-losses = يخسر { $player } { $count } { $count ->
    [one] جيش
    [two] جيشان
    [few] جيوش
    [many] جيشًا
    *[other] جيش
}.
ageofheroes-army-losses-you = تخسر { $count } { $count ->
    [one] جيش
    [two] جيشان
    [few] جيوش
    [many] جيشًا
    *[other] جيش
}.

# Army return
ageofheroes-army-return-road = تعود قواتك فورًا عبر الطريق.
ageofheroes-army-return-delayed = { $count } { $count ->
    [one] وحدة تعود
    [two] وحدتان تعودان
    [few] وحدات تعود
    [many] وحدة تعود
    *[other] وحدة تعود
} في نهاية دورك التالي.
ageofheroes-army-returned = عادت قوات { $player } من الحرب.
ageofheroes-army-returned-you = عادت قواتك من الحرب.
ageofheroes-army-recover = تتعافى جيوش { $player } من الزلزال.
ageofheroes-army-recover-you = تتعافى جيوشك من الزلزال.

# Olympics
ageofheroes-you-cancel-war-with-olympics = تلعب الألعاب الأولمبية، ملغيًا الحرب المُعلنة.
ageofheroes-player-cancels-war-with-olympics = يلعب { $player } الألعاب الأولمبية، ملغيًا الحرب المُعلنة.
ageofheroes-olympics-prompt = أعلن { $attacker } الحرب. لديك الألعاب الأولمبية - هل تستخدمها للإلغاء؟
ageofheroes-yes = نعم
ageofheroes-no = لا

# Monument progress
ageofheroes-monument-progress = اكتمل نصب { $player } التذكاري بنسبة { $count }/5.
ageofheroes-monument-progress-you = اكتمل نصبك التذكاري بنسبة { $count }/5.
# Hand management
ageofheroes-discard-excess = لديك أكثر من { $max } بطاقة. تخلّص من { $count } { $count ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
}.
ageofheroes-discard-excess-other = على { $player } التخلص من البطاقات الزائدة.
ageofheroes-discard-more = تخلّص من { $count } { $count ->
    [one] بطاقة أخرى
    [two] بطاقتين أخريين
    [few] بطاقات أخرى
    [many] بطاقة أخرى
    *[other] بطاقة أخرى
}.

# Victory
ageofheroes-victory-cities = بنى { $player } { $cities } مدينة! إمبراطورية المدن.
ageofheroes-victory-cities-you = بنيت { $cities } مدينة! إمبراطورية المدن.
ageofheroes-victory-monument = أكمل { $player } النصب التذكاري { GENDER_TERM($player_gender, "possessive-determiner") }! حاملو الثقافة العظيمة.
ageofheroes-victory-monument-you = أكملت نصبك التذكاري! حاملو الثقافة العظيمة.
ageofheroes-victory-last-standing = { $player } هو القبيلة الأخيرة الصامدة! الأكثر مثابرة.
ageofheroes-victory-last-standing-you = أنت القبيلة الأخيرة الصامدة! الأكثر مثابرة.
ageofheroes-game-over = انتهت اللعبة.
ageofheroes-final-winner = الفائز: { $player }
ageofheroes-final-days = الأيام الملعوبة: { $days }

# Elimination
ageofheroes-eliminated = تم إقصاء { $player }.
ageofheroes-eliminated-you = تم إقصاؤك.

# Hand
ageofheroes-check-hand = فحص اليد
ageofheroes-hand-empty = ليس لديك بطاقات.
ageofheroes-initial-hand = يدك الابتدائية ({ $count } { $count ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
}): { $cards }
ageofheroes-hand-contents = يدك ({ $count } { $count ->
    [one] بطاقة
    [two] بطاقتان
    [few] بطاقات
    [many] بطاقة
    *[other] بطاقة
}): { $cards }
# Status
ageofheroes-check-status = فحص الحالة
ageofheroes-check-status-detailed = الحالة التفصيلية
ageofheroes-status = { $player } ({ $tribe }): { $cities } { $cities ->
    [one] مدينة
    [two] مدينتان
    [few] مدن
    [many] مدينة
    *[other] مدينة
}، { $armies } { $armies ->
    [one] جيش
    [two] جيشان
    [few] جيوش
    [many] جيشًا
    *[other] جيش
}، النصب التذكاري { $monument }/5
ageofheroes-status-detailed-header = { $player } ({ $tribe })
ageofheroes-status-road-left = يسار
ageofheroes-status-road-right = يمين
ageofheroes-status-none = لا شيء
ageofheroes-status-earthquake-armies = الجيوش المتعافية: { $count }
ageofheroes-status-returning-armies = الجيوش العائدة: { $count }
ageofheroes-status-returning-generals = القادة العائدون: { $count }
ageofheroes-status-detailed-line = { $player } ({ $tribe }): { $cities } { $cities ->
    [one] مدينة
    [two] مدينتان
    [few] مدن
    [many] مدينة
    *[other] مدينة
}، { $armies } { $armies ->
    [one] جيش
    [two] جيشان
    [few] جيوش
    [many] جيشًا
    *[other] جيش
}، { $generals } { $generals ->
    [one] قائد
    [two] قائدان
    [few] قادة
    [many] قائدًا
    *[other] قائد
}، { $fortresses } { $fortresses ->
    [one] حصن
    [two] حصنان
    [few] حصون
    [many] حصنًا
    *[other] حصن
}، النصب التذكاري { $monument }/5، الطرق: { $roads }{ $details }
ageofheroes-status-detail-recovering-armies = { $count } { $count ->
    [one] جيش متعافٍ
    [two] جيشان متعافيان
    [few] جيوش متعافية
    [many] جيشًا متعافيًا
    *[other] جيش متعافٍ
}
ageofheroes-status-detail-returning-armies = { $count } { $count ->
    [one] جيش عائد
    [two] جيشان عائدان
    [few] جيوش عائدة
    [many] جيشًا عائدًا
    *[other] جيش عائد
}
ageofheroes-status-detail-returning-generals = { $count } { $count ->
    [one] قائد عائد
    [two] قائدان عائدان
    [few] قادة عائدون
    [many] قائدًا عائدًا
    *[other] قائد عائد
}

# Deck info
ageofheroes-deck-reshuffled = أُعيد خلط كومة المهملات في المجموعة.

# Give up
ageofheroes-give-up-confirm = هل أنت متأكد أنك تريد الاستسلام؟
ageofheroes-gave-up = استسلم { $player }!
ageofheroes-gave-up-you = لقد استسلمت!

# Fortune card
ageofheroes-you-use-fortune = تستخدم الحظ لإعادة رمي نرد المعركة.
ageofheroes-player-uses-fortune = يستخدم { $player } الحظ لإعادة رمي نرد المعركة.
# Disabled action reasons
ageofheroes-not-your-turn = ليس دورك.
ageofheroes-game-not-started = لم تبدأ اللعبة بعد.
ageofheroes-wrong-phase = هذا الإجراء غير متاح في المرحلة الحالية.
ageofheroes-invalid-player = هذا الإجراء غير متاح لك.
ageofheroes-not-in-game = أنت لست في هذه اللعبة.
ageofheroes-not-in-war = أنت لست طرفًا في هذه الحرب.
ageofheroes-already-rolled = لقد رميت النرد بالفعل.
ageofheroes-invalid-card-index = لم تعد تلك البطاقة متاحة.
ageofheroes-no-card-selected = اختر بطاقة أولًا.
ageofheroes-no-cards-to-discard = ليس لديك بطاقات للتخلص منها.
ageofheroes-disaster-too-early = لا يمكن لعب بطاقات الكوارث إلا بدءًا من اليوم الثاني.
ageofheroes-no-resources = ليس لديك الموارد المطلوبة.
ageofheroes-cannot-accept-own-offer = لا يمكنك قبول عرض المقايضة الخاص بك.
ageofheroes-offerer-unavailable = لم يعد عرض المقايضة ذلك متاحًا.
ageofheroes-offered-card-unavailable = لم تعد البطاقة المعروضة متاحة.
ageofheroes-trade-card-type-mismatch = لا تطابق بطاقتك المختارة نوع البطاقة المطلوب.
ageofheroes-trade-card-subtype-mismatch = لا تطابق بطاقتك المختارة البطاقة المطلوبة.
ageofheroes-trade-offer-label = { $player }: { $offered } مقابل { $wanted }
