# Age of Heroes game messages
# A civilization-building card game for 2-6 players

# Game name
game-name-ageofheroes = عصر الأبطال
# Tribes
ageofheroes-tribe-egyptians = مصريون
ageofheroes-tribe-romans = الرومان
ageofheroes-tribe-greeks = اليونانيون
ageofheroes-tribe-babylonians = البابليون
ageofheroes-tribe-celts = الكلت
ageofheroes-tribe-chinese = صيني
# Special Resources (for monuments)
ageofheroes-special-limestone = حجر جيري
ageofheroes-special-concrete = خرسانة
ageofheroes-special-marble = رخام
ageofheroes-special-bricks = طوب
ageofheroes-special-sandstone = حجر رملي
ageofheroes-special-granite = جرانيت
# Standard Resources
ageofheroes-resource-iron = حديد
ageofheroes-resource-wood = خشب
ageofheroes-resource-grain = حبوب
ageofheroes-resource-stone = حجر
ageofheroes-resource-gold = الذهب
# Events
ageofheroes-event-population-growth = النمو السكاني
ageofheroes-event-earthquake = زلزال
ageofheroes-event-eruption = ثوران
ageofheroes-event-hunger = الجوع
ageofheroes-event-barbarians = البرابرة
ageofheroes-event-olympics = الألعاب الأولمبية
ageofheroes-event-hero = البطل
ageofheroes-event-fortune = ثروة
# Buildings
ageofheroes-building-army = جيش
ageofheroes-building-fortress = حصن
ageofheroes-building-general = عام
ageofheroes-building-road = طريق
ageofheroes-building-city = المدينة
# Actions
ageofheroes-action-tax-collection = تحصيل الضرائب
ageofheroes-action-construction = البناء
ageofheroes-action-war = الحرب
ageofheroes-action-do-nothing = لا تفعل شيئا
ageofheroes-play = لعب
ageofheroes-play-card-label = لعب { $card }
ageofheroes-card-count = { $count } { $card }
ageofheroes-player-tribe = { $player } ({ $tribe })
ageofheroes-player-tribe-direction = { $player } ({ $tribe }) - { $direction }
# War goals
ageofheroes-war-conquest = الفتح
ageofheroes-war-plunder = نهب
ageofheroes-war-destruction = تدمير
# Game options
ageofheroes-set-victory-cities = مدن النصر : { $cities }
ageofheroes-enter-victory-cities = أدخل عدد المدن للفوز (3-7)
ageofheroes-set-victory-monument = اكتمال النصب التذكاري: { $progress }%
ageofheroes-set-max-hand = الحد الأقصى لحجم اليد: { $cards } بطاقات
# Option change announcements
ageofheroes-option-changed-victory-cities = النصر يتطلب { $cities } المدن.
ageofheroes-desc-victory-cities = كم عدد المدن التي يجب على الفريق السيطرة عليها للفوز بعصر الأبطال (الافتراضي 5، النطاق 3-7).
ageofheroes-option-changed-victory-monument = تم تعيين عتبة إكمال النصب التذكاري على { $progress }%.
ageofheroes-option-changed-max-hand = تم ضبط الحد الأقصى لحجم اليد على { $cards } بطاقات.
# Setup phase
ageofheroes-setup-start = أنت قائد { $tribe } قبيلة. مورد النصب التذكاري الخاص بك هو { $special }. قم برمي النرد لتحديد ترتيب الدور.
ageofheroes-setup-viewer = يقوم اللاعبون برمي النرد لتحديد ترتيب الأدوار.
ageofheroes-roll-dice = رمي النرد
ageofheroes-war-roll-dice = رمي النرد
ageofheroes-dice-result = لقد تدحرجت { $total } ({ $die1 } + { $die2 }).
ageofheroes-dice-result-other = { $player } توالت { $total }.
ageofheroes-dice-tie = تعادل العديد من اللاعبين مع { $total }. التدحرج من جديد...
ageofheroes-first-player = { $player } توالت أعلى مع { $total } ويذهب أولا.
ageofheroes-first-player-you = مع { $total } النقاط، تذهب أولا.
ageofheroes-whose-turn-setup = مرحلة الإعداد. في انتظار { $players } للفة بدوره النظام.
ageofheroes-whose-turn-setup-resolving = مرحلة الإعداد. كل النرد موجود؛ يتم حل أمر بدوره.
ageofheroes-whose-turn-prepare = مرحلة التحضير. الأحداث والكوارث تحل.
ageofheroes-whose-turn-fair = مرحلة السوق. { $players } قد لا تزال التجارة.
ageofheroes-whose-turn-fair-resolving = مرحلة السوق. الصفقات تحل.
ageofheroes-whose-turn-road = مرحلة إذن الطريق. { $responder } يجب الإجابة { $requester }طلب الطريق.
ageofheroes-whose-turn-olympics = أعلنت الحرب. { $defender } يجب أن تقرر ما إذا كان سيتم استخدام الألعاب الأولمبية ضد { $attacker }.
ageofheroes-whose-turn-war-attack = التحضير للحرب. { $attacker } هو اختيار القوات ضد { $defender }.
ageofheroes-whose-turn-war-defense = التحضير للحرب. { $defender } هو اختيار قوات الدفاع ضد { $attacker }.
ageofheroes-whose-turn-war-roll = مرحلة المعركة. في انتظار { $players } للفة.
ageofheroes-whose-turn-game-over = انتهت اللعبة.
# Preparation phase
ageofheroes-prepare-start = يجب على اللاعبين لعب بطاقات الأحداث والتخلص من الكوارث.
ageofheroes-prepare-your-turn =
    لديك { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    } للعب أو تجاهل.
ageofheroes-prepare-done = اكتملت مرحلة التحضير.
# Events played/discarded
ageofheroes-population-growth = { $player } يلعب النمو السكاني ويبني مدينة جديدة.
ageofheroes-population-growth-you = أنت تلعب دور النمو السكاني وتقوم ببناء مدينة جديدة.
ageofheroes-discard-card = { $player } المرتجعات { $card }.
ageofheroes-discard-card-you = أنت تتجاهل { $card }.
ageofheroes-earthquake = زلزال يضرب { $player }قبيلة؛ جيوشهم تذهب إلى التعافي.
ageofheroes-earthquake-you = زلزال يضرب قبيلتك؛ جيوشك تذهب إلى التعافي.
ageofheroes-eruption = ثوران يدمر أحد { $player }مدن.
ageofheroes-eruption-you = ثوران البركان يدمر إحدى مدنك.
# Disaster effects
ageofheroes-hunger-strikes = إضرابات عن الطعام.
ageofheroes-lose-card-hunger = تخسر { $card }.
ageofheroes-barbarians-pillage = هجوم البرابرة { $player }موارد.
ageofheroes-barbarians-attack = هجوم البرابرة { $player }موارد.
ageofheroes-barbarians-attack-you = البرابرة يهاجمون مواردك.
ageofheroes-lose-card-barbarians = تخسر { $card }.
ageofheroes-block-with-card = { $player } يحظر الكارثة باستخدام { $card }.
ageofheroes-block-with-card-you = يمكنك حظر الكارثة باستخدام { $card }.
# Targeted disaster cards (Earthquake/Eruption)
ageofheroes-select-disaster-target = حدد هدفًا لـ { $card }.
ageofheroes-no-targets = لا توجد أهداف صالحة المتاحة.
ageofheroes-earthquake-strikes-you = { $attacker } يلعب الزلزال ضدك. جيوشك معطلة.
ageofheroes-earthquake-strikes = { $attacker } يلعب زلزال ضد { $player }.
ageofheroes-armies-disabled =
    { $count } { $count ->
        [one] الجيش هو
       *[other] الجيوش هي
    } تعطيل لدورة واحدة.
ageofheroes-eruption-strikes-you = { $attacker } يلعب Eruption ضدك. تم تدمير إحدى مدنك.
ageofheroes-eruption-strikes = { $attacker } يلعب الثوران ضد { $player }.
ageofheroes-city-destroyed = تم تدمير مدينة بسبب الانفجار.
# Fair phase
ageofheroes-fair-start = فجر اليوم في السوق.
ageofheroes-fair-draw-base =
    أنت ترسم { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }.
ageofheroes-fair-draw-roads =
    أنت ترسم { $count } إضافية { $count ->
        [one] بطاقة
       *[other] بطاقات
    } بفضل شبكة الطرق الخاصة بك.
ageofheroes-fair-draw-other =
    { $player } رسم { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }.
# Trading/Auction
ageofheroes-auction-start = يبدأ المزاد.
ageofheroes-offer-trade = عرض للتداول
ageofheroes-offer-made = { $player } عروض { $card } ل { $wanted }.
ageofheroes-offer-made-you = انت تقدم { $card } ل { $wanted }.
ageofheroes-trade-accepted = { $player } يقبل { $other }عرض وتداولات { $give } ل { $receive }.
ageofheroes-trade-accepted-you = أنت تقبل { $other }عرض واستلام { $receive }.
ageofheroes-trade-cancelled = { $player } يسحب عرضه لـ { $card }.
ageofheroes-trade-cancelled-you = قمت بسحب عرضك لـ { $card }.
ageofheroes-stop-trading = إيقاف التداول
ageofheroes-select-request = أنت تقدم { $card }. ماذا تريد في المقابل؟
ageofheroes-cancel = إلغاء
ageofheroes-left-auction = { $player } يغادر.
ageofheroes-left-auction-you = أنت تخرج من السوق.
ageofheroes-already-left-auction = لقد غادرت السوق بالفعل.
ageofheroes-any-card = أي بطاقة
ageofheroes-cannot-trade-own-special = لا يمكنك المتاجرة بمورد النصب التذكاري الخاص بك.
ageofheroes-resource-not-in-game = لا يتم استخدام هذا المورد الخاص في هذه اللعبة.
# Main play phase
ageofheroes-play-start = مرحلة اللعب.
ageofheroes-day = يوم { $day }
ageofheroes-draw-card = { $player } يسحب بطاقة من سطح السفينة.
ageofheroes-draw-card-you = أنت ترسم { $card } من سطح السفينة.
ageofheroes-draw-card-brief = { $player } توجه.
ageofheroes-draw-card-you-brief = رسم: { $card }.
ageofheroes-your-action = ماذا تريد أن تفعل؟
ageofheroes-your-action-brief = فعل؟
# Tax Collection
ageofheroes-tax-collection =
    { $player } يختار تحصيل الضرائب: { $cities } { $cities ->
        [one] المدينة
       *[other] المدن
    } يجمع { $cards } { $cards ->
        [one] بطاقة
       *[other] بطاقات
    }.
ageofheroes-tax-collection-you =
    اخترت تحصيل الضرائب: { $cities } { $cities ->
        [one] المدينة
       *[other] المدن
    } يجمع { $cards } { $cards ->
        [one] بطاقة
       *[other] بطاقات
    }.
ageofheroes-tax-collection-brief = { $player } الضريبة: { $cards } من { $cities }.
ageofheroes-tax-collection-you-brief = الضريبة: { $cards } من { $cities }.
ageofheroes-tax-no-city = تحصيل الضرائب: ليس لديك مدن باقية. تجاهل البطاقة لرسم واحدة جديدة.
ageofheroes-tax-no-city-done = { $player } يختار تحصيل الضرائب ولكن ليس لديه مدن، لذلك يقومون بتبادل البطاقة.
ageofheroes-tax-no-city-done-you = تحصيل الضرائب: قمت بتبادل { $card } للحصول على بطاقة جديدة.
# Construction
ageofheroes-construction-menu = ماذا تريد أن تبني؟
ageofheroes-construction-done = { $player } بني { $building }.
ageofheroes-construction-done-you = لقد بنيت { $building }.
ageofheroes-build-cost-resource =
    { $count ->
        [one] { $resource }
       *[other] { $count }س { $resource }
    }
ageofheroes-build-menu-label = { $building } ({ $cost })
ageofheroes-construction-stop = توقف عن البناء
ageofheroes-construction-stopped = لقد قررت التوقف عن البناء.
ageofheroes-road-select-neighbor = حدد أي جار تريد بناء طريق إليه.
ageofheroes-direction-left = عن يسارك
ageofheroes-direction-right = عن يمينك
ageofheroes-road-request-sent = تم إرسال طلب الطريق. في انتظار موافقة الجيران.
ageofheroes-road-request-received = { $requester } يطلب الإذن ببناء طريق إلى قبيلتك.
ageofheroes-road-request-denied-you = لقد رفضت طلب الطريق.
ageofheroes-road-request-denied = { $denier } رفض طلب الطريق الخاص بك.
ageofheroes-road-built = { $tribe1 } و { $tribe2 } متصلة الآن عن طريق البر.
ageofheroes-road-no-target = لا توجد قبائل مجاورة متاحة لبناء الطرق.
ageofheroes-approve = يعتمد
ageofheroes-deny = أنكر
ageofheroes-supply-exhausted = لا أكثر { $building } متاح للبناء.
# Do Nothing
ageofheroes-do-nothing = { $player } يمر.
ageofheroes-do-nothing-you = تمر...
ageofheroes-do-nothing-brief = { $player } يمر.
ageofheroes-do-nothing-you-brief = يمر.
ageofheroes-confirm-do-nothing = التمرير يتخطى الإجراء الخاص بك لهذا المنعطف. اضغط على "لا تفعل شيئًا" مرة أخرى للتأكيد.
# War
ageofheroes-war-declare = { $attacker } تعلن الحرب على { $defender }. الهدف: { $goal }.
ageofheroes-war-prepare = اختر جيوشك لـ { $action }.
ageofheroes-war-no-army = ليس لديك جيوش أو بطاقات أبطال متاحة.
ageofheroes-war-no-tribe = ليس لديك قبيلة في هذه المعركة.
ageofheroes-war-no-targets = لا توجد أهداف صالحة للحرب.
ageofheroes-war-no-valid-goal = لا توجد أهداف حرب صالحة ضد هذا الهدف.
ageofheroes-war-invalid-forces = ولم تعد تلك القوى صالحة. قم بمراجعة الجيوش والجنرالات وبطاقات الأبطال المتوفرة لديك.
ageofheroes-war-select-target = اختر اللاعب الذي تريد مهاجمته.
ageofheroes-war-select-goal = حدد هدف الحرب الخاص بك.
ageofheroes-war-prepare-attack = حدد القوات المهاجمة الخاصة بك.
ageofheroes-war-prepare-defense = { $attacker } يهاجمك؛ حدد قوات الدفاع الخاصة بك.
ageofheroes-war-force-add-armies = إضافة جيش واحد. الجيوش الملتزمة: { $current } من { $max }.
ageofheroes-war-force-remove-armies = إزالة جيش واحد. الجيوش الملتزمة: { $current } من { $max }.
ageofheroes-war-force-add-generals = إضافة عام واحد. الجنرالات الملتزمون: { $current } من { $max }.
ageofheroes-war-force-remove-generals = إزالة عام واحد. الجنرالات الملتزمون: { $current } من { $max }.
ageofheroes-war-force-add-hero-armies = أضف بطلًا واحدًا كجيش. جيوش البطل الملتزمة : { $current } من { $max }.
ageofheroes-war-force-remove-hero-armies = قم بإزالة جيش بطل واحد. جيوش البطل الملتزمة : { $current } من { $max }.
ageofheroes-war-force-add-hero-generals = أضف بطلًا واحدًا كجنرال. الجنرالات البطل ملتزمون : { $current } من { $max }.
ageofheroes-war-force-remove-hero-generals = قم بإزالة جنرال بطل واحد. الجنرالات البطل ملتزمون : { $current } من { $max }.
ageofheroes-war-force-unit-armies = الجيوش
ageofheroes-war-force-unit-generals = جنرالات
ageofheroes-war-force-unit-hero-armies = جيوش الأبطال
ageofheroes-war-force-unit-hero-generals = الجنرالات البطل
ageofheroes-war-force-max = بالفعل عند الحد الأقصى: { $unit } ({ $max }).
ageofheroes-war-force-min = لم يلتزم أحد: { $unit }.
ageofheroes-war-force-updated = القوات المرتكبة: { $armies } الجيوش { $generals } جنرالات، { $hero_armies } جيوش الأبطال، { $hero_generals } الجنرالات الأبطال.
ageofheroes-war-attack = هجوم...
ageofheroes-war-defend = دافع...
ageofheroes-war-clear-forces = قوى واضحة
ageofheroes-war-prepared =
    قواتك: { $armies } { $armies ->
        [one] جيش
       *[other] الجيوش
    }{ $generals ->
        [0] { "" }
        [one] { " و1 عام" }
       *[other] { " و " }{ $generals } جنرالات
    }{ $heroes ->
        [0] { "" }
        [one] { " وبطل واحد" }
       *[other] { " و " }{ $heroes } ابطال
    }.
ageofheroes-war-roll-you = أنت تتدحرج { $roll }.
ageofheroes-war-roll-other = { $player } لفات { $roll }.
ageofheroes-war-bonuses-you =
    { $general ->
        [0]
            { $fortress ->
                [0] { "" }
                [1] +1 من القلعة = { $total } المجموع
               *[other] +{ $fortress } من الحصون = { $total } المجموع
            }
       *[other]
            { $fortress ->
                [0] +{ $general } من العام = { $total } المجموع
                [1] +{ $general } من العام، +1 من القلعة = { $total } المجموع
               *[other] +{ $general } من العام +{ $fortress } من الحصون = { $total } المجموع
            }
    }
ageofheroes-war-bonuses-other =
    { $general ->
        [0]
            { $fortress ->
                [0] { "" }
                [1] { $player }: +1 من القلعة = { $total } المجموع
               *[other] { $player }: +{ $fortress } من الحصون = { $total } المجموع
            }
       *[other]
            { $fortress ->
                [0] { $player }: +{ $general } من العام = { $total } المجموع
                [1] { $player }: +{ $general } من العام، +1 من القلعة = { $total } المجموع
               *[other] { $player }: +{ $general } من العام +{ $fortress } من الحصون = { $total } المجموع
            }
    }
ageofheroes-war-bonuses-you-brief = مكافأة +{ $bonus } = { $total }.
ageofheroes-war-bonuses-other-brief = { $player } مكافأة +{ $bonus } = { $total }.
# Battle
ageofheroes-battle-start =
    تبدأ المعركة. { $attacker } { $att_armies } { $att_armies ->
        [one] جيش
       *[other] الجيوش
    } مقابل { $defender } { $def_armies } { $def_armies ->
        [one] جيش
       *[other] الجيوش
    }.
ageofheroes-battle-start-brief = المعركة: { $attacker } { $att_armies } مقابل { $defender } { $def_armies }.
ageofheroes-dice-roll-detailed =
    { $name } لفات { $dice }{ $general ->
        [0] { "" }
       *[other] { " + { $general } من العام" }
    }{ $fortress ->
        [0] { "" }
        [one] { " +1 من الحصن" }
       *[other] { " + { $الحصن } من الحصون" }
    } = { $total }.
ageofheroes-dice-roll-detailed-you =
    أنت تتدحرج { $dice }{ $general ->
        [0] { "" }
       *[other] { " + { $general } من العام" }
    }{ $fortress ->
        [0] { "" }
        [one] { " +1 من الحصن" }
       *[other] { " + { $الحصن } من الحصون" }
    } = { $total }.
ageofheroes-round-attacker-wins = { $attacker } يفوز بالجولة ({ $att_total } vs { $def_total }). { $defender } يفقد جيشا.
ageofheroes-round-defender-wins = { $defender } يدافع بنجاح ({ $def_total } vs { $att_total }). { $attacker } يفقد جيشا.
ageofheroes-round-draw = كلا الجانبين يتعادلان عند { $total }. ولم تخسر أي جيوش.
ageofheroes-round-attacker-wins-brief = { $attacker } { $att_total } يدق { $defender } { $def_total }. { $defender } -1 جيش.
ageofheroes-round-defender-wins-brief = { $defender } { $def_total } يدق { $attacker } { $att_total }. { $attacker } -1 جيش.
ageofheroes-round-draw-brief = ربطة عنق { $total }. لا خسارة.
ageofheroes-you-win-battle-as-attacker = تهزم { $defender }.
ageofheroes-you-lose-battle-as-defender = { $attacker } يهزمك.
ageofheroes-battle-victory-attacker = { $attacker } هزائم { $defender }.
ageofheroes-you-lose-battle-as-attacker = { $defender } يدافع بنجاح ضدك.
ageofheroes-you-win-battle-as-defender = لقد نجحت في الدفاع ضد { $attacker }.
ageofheroes-battle-victory-defender = { $defender } يدافع بنجاح ضد { $attacker }.
ageofheroes-you-draw-battle = أنت و { $opponent } كلاهما يفقد كل القوات الملتزمة بالمعركة.
ageofheroes-battle-mutual-defeat = كلاهما { $attacker } و { $defender } تفقد جميع القوات الملتزمة بالمعركة.
ageofheroes-general-bonus =
    +{ $count } من { $count ->
        [one] عام
       *[other] جنرالات
    }
ageofheroes-fortress-bonus = +{ $count } من الدفاع عن القلعة
ageofheroes-battle-winner = { $winner } يفوز في المعركة.
ageofheroes-battle-draw = وتنتهي المعركة بالتعادل...
ageofheroes-battle-continue = مواصلة المعركة.
ageofheroes-battle-end = انتهت المعركة.
# War outcomes
ageofheroes-conquest-success =
    { $attacker } ينتصر { $count } { $count ->
        [one] المدينة
       *[other] المدن
    } من { $defender }.
ageofheroes-plunder-success =
    { $attacker } نهب { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    } من { $defender }.
ageofheroes-destruction-success =
    { $attacker } يدمر { $count } من { $defender }نصب تذكاري { $count ->
        [one] المصدر
       *[other] الموارد
    }.
ageofheroes-conquest-success-brief =
    { $attacker } يأخذ { $count } { $count ->
        [one] المدينة
       *[other] المدن
    } من { $defender }.
ageofheroes-plunder-success-brief =
    { $attacker } يأخذ { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    } من { $defender }.
ageofheroes-destruction-success-brief =
    { $attacker } يدمر { $count } نصب تذكاري { $count ->
        [one] المصدر
       *[other] الموارد
    } من { $defender }.
ageofheroes-army-losses =
    { $player } يخسر { $count } { $count ->
        [one] جيش
       *[other] الجيوش
    }.
ageofheroes-army-losses-you =
    تخسر { $count } { $count ->
        [one] جيش
       *[other] الجيوش
    }.
# Army return
ageofheroes-army-return-road = تعود قواتك على الفور عبر الطريق.
ageofheroes-army-return-delayed =
    { $count } { $count ->
        [one] إرجاع الوحدة
       *[other] عودة الوحدات
    } في نهاية المنعطف التالي.
ageofheroes-army-returned = { $player }لقد عادت قواتنا من الحرب.
ageofheroes-army-returned-you = لقد عادت قواتك من الحرب.
ageofheroes-army-recover = { $player }جيوش الصين تتعافى من الزلزال.
ageofheroes-army-recover-you = جيوشك تتعافى من الزلزال.
# Olympics
ageofheroes-you-cancel-war-with-olympics = تلعب الألعاب الأولمبية، وإلغاء الحرب المعلنة.
ageofheroes-player-cancels-war-with-olympics = { $player } تلعب الألعاب الأولمبية، وإلغاء الحرب المعلنة.
ageofheroes-olympics-prompt = { $attacker } أعلنت الحرب. لديك دورة ألعاب أولمبية - هل تستخدمها للإلغاء؟
ageofheroes-yes = نعم
ageofheroes-no = لا
# Monument progress
ageofheroes-monument-progress = { $player }نصب تذكاري هو { $count }/5 كاملة.
ageofheroes-monument-progress-you = نصبك هو { $count }/5 كاملة.
# Hand management
ageofheroes-discard-excess =
    لديك أكثر من { $max } بطاقات. تجاهل { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }.
ageofheroes-discard-excess-other = { $player } يجب التخلص من البطاقات الزائدة.
ageofheroes-discard-more =
    تجاهل { $count } المزيد { $count ->
        [one] بطاقة
       *[other] بطاقات
    }.
# Victory
ageofheroes-victory-cities = { $player } قد بني { $cities } المدن! إمبراطورية المدن.
ageofheroes-victory-cities-you = لقد بنيت { $cities } المدن! إمبراطورية المدن.
ageofheroes-victory-monument = { $player } أكمل نصبهم! حاملي الثقافة العظيمة.
ageofheroes-victory-monument-you = لقد أكملت النصب التذكاري الخاص بك! حاملي الثقافة العظيمة.
ageofheroes-victory-last-standing = { $player } هي آخر قبيلة واقفة! الأكثر ثباتا.
ageofheroes-victory-last-standing-you = أنت آخر قبيلة واقفة! الأكثر ثباتا.
ageofheroes-game-over = انتهت اللعبة.
ageofheroes-final-winner = الفائز: { $player }
ageofheroes-final-days = أيام اللعب: { $days }
# Elimination
ageofheroes-eliminated = { $player } تم القضاء عليه.
ageofheroes-eliminated-you = لقد تم القضاء عليك.
# Hand
ageofheroes-check-hand = فحص اليد
ageofheroes-hand-empty = ليس لديك بطاقات.
ageofheroes-initial-hand =
    يد البداية الخاصة بك ({ $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }): { $cards }
ageofheroes-hand-contents =
    يدك ({ $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }): { $cards }
# Status
ageofheroes-check-status = التحقق من الحالة
ageofheroes-check-status-detailed = الحالة التفصيلية
ageofheroes-status =
    { $player } ({ $tribe }): { $cities } { $cities ->
        [one] المدينة
       *[other] المدن
    }, { $armies } { $armies ->
        [one] جيش
       *[other] الجيوش
    }, { $monument }/5 نصب
ageofheroes-status-detailed-header = { $player } ({ $tribe })
ageofheroes-status-cities = المدن: { $count }
ageofheroes-status-armies = الجيوش: { $count }
ageofheroes-status-generals = الجنرالات: { $count }
ageofheroes-status-fortresses = الحصون: { $count }
ageofheroes-status-monument = نصب تذكاري: { $count }/5
ageofheroes-status-roads = الطرق: { $left }{ $right }
ageofheroes-status-road-left = اليسار
ageofheroes-status-road-right = حق
ageofheroes-status-none = لا شيء
ageofheroes-status-earthquake-armies = الجيوش المستردة: { $count }
ageofheroes-status-returning-armies = الجيوش العائدة: { $count }
ageofheroes-status-returning-generals = الجنرالات العائدين: { $count }
ageofheroes-status-detailed-line =
    { $player } ({ $tribe }): { $cities } { $cities ->
        [one] مدينة
       *[other] المدن
    }, { $armies } { $armies ->
        [one] جيش
       *[other] الجيوش
    }, { $generals } { $generals ->
        [one] عام
       *[other] جنرالات
    }, { $fortresses } { $fortresses ->
        [one] حصن
       *[other] حصون
    }, نصب { $monument }/5 الطرق: { $roads }{ $details }
ageofheroes-status-detail-recovering-armies =
    { $count } يتعافى { $count ->
        [one] جيش
       *[other] الجيوش
    }
ageofheroes-status-detail-returning-armies =
    { $count } العودة { $count ->
        [one] جيش
       *[other] الجيوش
    }
ageofheroes-status-detail-returning-generals =
    { $count } العودة { $count ->
        [one] عام
       *[other] جنرالات
    }
# Deck info
ageofheroes-deck-empty = لا أكثر { $card } بطاقات في سطح السفينة.
ageofheroes-deck-count = البطاقات المتبقية: { $count }
ageofheroes-deck-reshuffled = تم تعديل الكومة المهملة إلى سطح السفينة.
# Give up
ageofheroes-give-up-confirm = هل أنت متأكد أنك تريد الاستسلام؟
ageofheroes-gave-up = { $player } استسلم!
ageofheroes-gave-up-you = لقد استسلمت!
# Hero card
ageofheroes-hero-use = استخدام كجيش أو جنرال؟
ageofheroes-hero-army = جيش
ageofheroes-hero-general = عام
# Fortune card
ageofheroes-you-use-fortune = يمكنك استخدام Fortune لإعادة دحرجة نرد المعركة.
ageofheroes-player-uses-fortune = { $player } يستخدم Fortune لإعادة نرد المعركة.
ageofheroes-fortune-prompt = لقد فقدت لفة. استخدام الحظ لإعادة التدوير؟
# Disabled action reasons
ageofheroes-not-your-turn = إنه ليس دورك.
ageofheroes-game-not-started = اللعبة لم تبدأ بعد
ageofheroes-wrong-phase = هذا الإجراء غير متوفر في المرحلة الحالية.
ageofheroes-invalid-player = هذا الإجراء غير متاح لك.
ageofheroes-not-in-game = أنت لست في هذه اللعبة.
ageofheroes-not-in-war = أنت لست مشاركا في هذه الحرب.
ageofheroes-already-rolled = لقد توالت بالفعل.
ageofheroes-invalid-card-index = هذه البطاقة لم تعد متوفرة.
ageofheroes-no-card-selected = حدد البطاقة أولاً.
ageofheroes-no-cards-to-discard = ليس لديك أي بطاقات للتخلص منها.
ageofheroes-disaster-too-early = لا يمكن لعب بطاقات الكوارث إلا اعتبارًا من اليوم الثاني فصاعدًا.
ageofheroes-no-resources = ليس لديك الموارد المطلوبة.
ageofheroes-cannot-accept-own-offer = لا يمكنك قبول العرض التجاري الخاص بك.
ageofheroes-offerer-unavailable = هذا العرض التجاري لم يعد متاحا.
ageofheroes-offered-card-unavailable = البطاقة المقدمة لم تعد متوفرة.
ageofheroes-trade-card-type-mismatch = بطاقتك المحددة لا تتطابق مع نوع البطاقة المطلوبة.
ageofheroes-trade-card-subtype-mismatch = البطاقة التي اخترتها لا تتطابق مع البطاقة المطلوبة.
ageofheroes-trade-offer-label = { $player }: { $offered } ل { $wanted }
# Building costs (for display)
ageofheroes-cost-army = 2 الحبوب والحديد
ageofheroes-cost-fortress = حديد، خشب، حجر
ageofheroes-cost-general = حديد ذهب
ageofheroes-cost-road = 2 حجر
ageofheroes-cost-city = 2 الخشب والحجر
