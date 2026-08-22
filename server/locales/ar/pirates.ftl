game-name-pirates = قراصنة البحار المفقودة
# Setup and round flow
pirates-welcome = مرحبا بكم في قراصنة البحار المفقودة. أبحر في طريق الأربعين فضاء، واسترجع الجواهر المتناثرة، وتغلب على أطقم المنافسين.
pirates-welcome-brief = مرحبا بكم في قراصنة البحار المفقودة.
pirates-oceans = رحلتك تعبر { $oceans }.
pirates-gems-placed = الكل { $total } تم إخفاء الأحجار الكريمة على طول الطريق. تفوز أعلى قيمة للشحنة بعد استرداد الجوهرة النهائية.
pirates-gems-placed-brief = { $total } يتم إخفاء الأحجار الكريمة على طول الطريق.
pirates-golden-moon = القمر الذهبي يرتفع بشكل دائري { $round }. يتم مضاعفة كل جائزة XP في هذه الجولة ثلاث مرات.
pirates-golden-moon-brief = جولدن مون: تريبل إكس بي في الجولة { $round }.
pirates-turn-you = دورك في الجولة { $round }. أنت في الموضع { $position } في { $ocean }.
pirates-turn-you-brief = دورك. الموقف { $position }.
pirates-turn = { $player }دوره في الجولة { $round }، في الموقف { $position } في { $ocean }.
pirates-turn-brief = { $player }دور.
# Movement and map information
pirates-move-left = أبحر مسافة واحدة متبقية
pirates-move-right = أبحر مسافة واحدة لليمين
pirates-move-2-left = أبحر بقي مساحتين
pirates-move-2-right = أبحر مسافتين لليمين
pirates-move-3-left = أبحر ثلاث مسافات متبقية
pirates-move-3-right = أبحر ثلاث مسافات لليمين
pirates-move-you =
    أنت تبحر { $tiles } { $tiles ->
        [one] مساحة
       *[other] مساحات
    } { $direction } إلى الموضع { $position } في { $ocean }.
pirates-move-you-brief = أنت تبحر إلى الموقف { $position }.
pirates-move =
    { $player } أشرعة { $tiles } { $tiles ->
        [one] مساحة
       *[other] المساحات
    } { $direction } إلى الموضع { $position } في { $ocean }.
pirates-move-brief = { $player } أشرعة إلى الموضع { $position }.
pirates-map-edge = لا يمكنك الإبحار أبعد في هذا الاتجاه؛ الموقف { $position } هي حافة الطريق. اختر إجراءً آخر.
pirates-dir-left = اليسار
pirates-dir-right = حق
pirates-your-position = أنت في الموضع { $position }, القطاع { $sector }في { $ocean }.
pirates-check-position = التحقق من الموقف
pirates-check-moon = تحقق من القمر الذهبي
pirates-moon-active = القمر الذهبي ينشط بشكل دائري { $round }. تم مضاعفة XP ثلاث مرات. تم تعافي الطواقم { $collected } من { $total } الأحجار الكريمة مع { $remaining } متبقي.
pirates-moon-inactive =
    القمر الذهبي غير نشط في الجولة { $round }. يعود في { $rounds } { $rounds ->
        [one] جولة
       *[other] جولات
    }. تم تعافي الطواقم { $collected } من { $total } الأحجار الكريمة مع { $remaining } متبقي.
# Status and results
pirates-check-status = التحقق من حالة الطاقم
pirates-check-status-detailed = حالة الطاقم التفصيلية
pirates-status-line =
    { $player }: المستوى { $level }; { $xp } إجمالي XP، { $progress } من { $needed } XP نحو المستوى التالي؛ { $points }; { $gem_count } { $gem_count ->
        [one] جوهرة
       *[other] جواهر
    }{ $detail ->
        [yes] ; الموقف { $position } في { $ocean }; البضائع: { $gems }; التأثيرات النشطة: { $skills }
       *[no] { "" }
    }.
pirates-end-score-line = { $rank }. { $player }: { $points }, المستوى { $level }
pirates-all-gems-collected = تم استرداد الجوهرة النهائية. يقوم الطاقم بمقارنة حمولتهم.
pirates-all-gems-collected-brief = تم استرداد الجوهرة النهائية.
pirates-you-win = تربح مع { $score } نقاط.
pirates-you-win-brief = لقد فزت: { $score } نقاط.
pirates-winner = { $player } يفوز مع { $score } نقاط.
pirates-winner-brief = { $player } الانتصارات: { $score } نقاط.
pirates-you-tie = أنت تتعادل لأول مرة مع { $players } في { $score } نقاط.
pirates-you-tie-brief = أنت تتعادل لأول مرة في { $score }.
pirates-players-tie = { $players } التعادل لأول مرة مع { $score } نقاط.
pirates-players-tie-brief = { $players } التعادل في { $score }.
# Gems and XP
pirates-gem-found-you =
    يمكنك استعادة { $gem }, يستحق { $value } { $value ->
        [one] نقطة
       *[other] النقاط
    }. تبلغ قيمة البضائع الخاصة بك الآن { $score } نقاط؛ { $remaining } الأحجار الكريمة تبقى في البحر.
pirates-gem-found-you-brief = يمكنك استعادة { $gem }. النتيجة: { $score }.
pirates-gem-found =
    { $player } يستعيد { $gem }, يستحق { $value } { $value ->
        [one] نقطة
       *[other] النقاط
    }. حمولتهم تستحق الآن { $score } نقاط؛ { $remaining } الأحجار الكريمة تبقى في البحر.
pirates-gem-found-brief = { $player } يستعيد { $gem }.
pirates-xp-gained-you =
    تكسب { $xp } XP لـ { $reason ->
        [gem] استعادة جوهرة
        [attack] هبوط مدفع ضرب
        [defense] صد هجوم مدفعي
       *[other] إكمال الإجراء
    }. لديك الآن { $total } إجمالي XP.
pirates-xp-gained-you-brief = تكسب { $xp } XP. المجموع: { $total }.
pirates-xp-gained-player =
    { $player } مكاسب { $xp } XP لـ { $reason ->
        [gem] استعادة جوهرة
        [attack] هبوط مدفع ضرب
        [defense] صد هجوم مدفعي
       *[other] إكمال الإجراء
    }, وصولا إلى { $total } إجمالي XP.
pirates-xp-gained-player-brief = { $player } مكاسب { $xp } XP.
pirates-level-up-you = وصلت إلى المستوى { $level }.
pirates-level-up-you-brief = وصلت إلى المستوى { $level }.
pirates-level-up = { $player } يصل إلى المستوى { $level }.
pirates-level-up-brief = { $player } يصل إلى المستوى { $level }.
pirates-level-up-multiple-you = تكسب { $levels } المستويات والوصول إلى المستوى { $level }.
pirates-level-up-multiple-you-brief = وصلت إلى المستوى { $level }.
pirates-level-up-multiple = { $player } مكاسب { $levels } المستويات ويصل إلى المستوى { $level }.
pirates-level-up-multiple-brief = { $player } يصل إلى المستوى { $level }.
pirates-skills-unlocked-you = على المستوى { $level }، يمكنك فتح { $skills }.
pirates-skills-unlocked-you-brief = قمت بفتح { $skills }.
pirates-skills-unlocked = على المستوى { $level }, { $player } يفتح { $skills }.
pirates-skills-unlocked-brief = { $player } يفتح { $skills }.
# Cannon combat
pirates-cannonball = قذيفة نارية
pirates-select-cannon-target = اختر سفينة ضمن نطاق المدفع
pirates-target-option =
    { $player }, { $distance } { $distance ->
        [one] مساحة
       *[other] مساحات
    } بعيد، { $score } نقاط تحمل { $gems } { $gems ->
        [one] جوهرة
       *[other] جواهر
    }
pirates-target-unavailable = سفينة غير متاحة
pirates-no-targets = لا توجد سفينة منافسة ضمن نطاق مدفعك الحالي { $range } المساحات. اختر الحركة أو أي مهارة أخرى متاحة.
pirates-target-out-of-range = { $target } لم يعد ضمن { $range }-مدفع فضائي يتراوح من موضع { $position }. اختر إجراءً آخر.
pirates-attack-you-fire = قمت بإطلاق قذيفة مدفعية على { $target }.
pirates-attack-you-fire-brief = أنت تطلق النار على { $target }.
pirates-attack-incoming = { $attacker } يطلق قذيفة مدفع عليك.
pirates-attack-incoming-brief = { $attacker } الحرائق عليك.
pirates-attack-fired = { $attacker } يطلق قذيفة مدفع على { $defender }.
pirates-attack-fired-brief = { $attacker } حرائق في { $defender }.
pirates-combat-rolls-you = يموت الهجوم الخاص بك { $attack_die }بالإضافة إلى { $attack_bonus }, ل { $attack_total }. { $defender }قالب الدفاع هو { $defense_die }بالإضافة إلى { $defense_bonus }, ل { $defense_total }.
pirates-combat-rolls-you-brief = هجوم { $attack_total }; دفاع { $defense_total }.
pirates-combat-rolls-defender = { $attacker } الهجمات مع { $attack_die }بالإضافة إلى { $attack_bonus }, ل { $attack_total }. يموت دفاعك هو { $defense_die }بالإضافة إلى { $defense_bonus }, ل { $defense_total }.
pirates-combat-rolls-defender-brief = هجوم { $attack_total }; دفاعك { $defense_total }.
pirates-combat-rolls-observer = { $attacker } الهجمات مع { $attack_die }بالإضافة إلى { $attack_bonus }, ل { $attack_total }. { $defender } يدافع بـ { $defense_die }بالإضافة إلى { $defense_bonus }, ل { $defense_total }.
pirates-combat-rolls-observer-brief = { $attacker } { $attack_total }; { $defender } { $defense_total }.
pirates-attack-hit-you = ضربة مباشرة. { $attack_total } الخاص بك  يدق { $target } { $defense_total }; اختر إجراء الصعود المتاح.
pirates-attack-hit-you-brief = لقد ضربت { $target }, { $attack_total } إلى { $defense_total }.
pirates-attack-hit-them = { $attacker } يضربك، { $attack_total } ل { $defense_total }، ويمكنك الآن الصعود إلى سفينتك.
pirates-attack-hit-them-brief = { $attacker } يضربك، { $attack_total } إلى { $defense_total }.
pirates-attack-hit = { $attacker } يضرب { $defender }, { $attack_total } إلى { $defense_total }، ويمكن الصعود.
pirates-attack-hit-brief = { $attacker } يضرب { $defender }.
pirates-attack-hit-no-boarding-you = ضربة مباشرة. { $attack_total } الخاص بك  يدق { $target } { $defense_total }. تمنح ضربة السفينة الحربية نقاط XP ولكن لا توجد عملية صعود.
pirates-attack-hit-no-boarding-you-brief = لقد ضربت { $target }, { $attack_total } إلى { $defense_total }; لا الصعود.
pirates-attack-hit-no-boarding-them = { $attacker } يضربك، { $attack_total } ل { $defense_total }. ضربات السفينة الحربية لا تمنح إجراءات الصعود.
pirates-attack-hit-no-boarding-them-brief = { $attacker } يضربك؛ لا الصعود.
pirates-attack-hit-no-boarding = { $attacker } يضرب { $defender }, { $attack_total } إلى { $defense_total }. لا تمنح ضربة السفينة الحربية هذه أي إجراء للصعود.
pirates-attack-hit-no-boarding-brief = { $attacker } يضرب { $defender }; لا الصعود.
pirates-attack-miss-you = إجمالي هجومك هو { $attack_total } لا يتغلب { $target }إجمالي دفاع { $defense_total }. ينتهي دورك.
pirates-attack-miss-you-brief = اشتقت { $target }, { $attack_total } إلى { $defense_total }.
pirates-attack-miss-them = تصد { $attacker } بإجمالي دفاع { $defense_total } ضد { $attack_total }.
pirates-attack-miss-them-brief = تصد { $attacker }, { $defense_total } إلى { $attack_total }.
pirates-attack-miss = { $defender } يصد { $attacker }, { $defense_total } إلى { $attack_total }.
pirates-attack-miss-brief = { $attacker } يفتقد { $defender }.
# Boarding
pirates-resolve-boarding = حل الصعود
pirates-select-boarding-action = ضرب المدفع. اختر كيفية حل إجراء الصعود إلى الطائرة
pirates-boarding-steal = محاولة سرقة جوهرة
pirates-boarding-push-left = رام المدافع غادر
pirates-boarding-push-right = رام المدافع الأيمن
pirates-boarding-option-unknown = إجراء صعود غير معروف
pirates-must-resolve-boarding = قم بحل إجراء الصعود المعلق الخاص بك قبل اتخاذ إجراء آخر.
pirates-no-pending-boarding = لا توجد أي إجراءات صعود معلقة يتعين عليك حلها.
pirates-boarding-stale = لم يعد إجراء الصعود المعلق يحتوي على مدافع صالح، لذلك تم إلغاؤه. اختر إجراء دوران آخر.
pirates-boarding-option-unavailable = { $action } لم يعد متاحا ضد { $defender }. اختر أحد خيارات الصعود الحالية.
pirates-push-you = أنت رام { $target } { $direction } من الموقف { $old_pos } إلى { $new_pos }, تحريكهم { $distance } المساحات. ساهمت مكافأة الدفع الخاصة بك { $bonus } مساحات اضافية.
pirates-push-you-brief = أنت رام { $target } إلى الموضع { $position }.
pirates-push-them = { $attacker } الكباش لك { $direction } من الموقف { $old_pos } إلى { $new_pos }, يحركك { $distance } المساحات.
pirates-push-them-brief = { $attacker } الكباش لك موقف { $position }.
pirates-push = { $attacker } كباش { $defender } { $direction } من الموقف { $old_pos } ل { $new_pos }مسافة { $distance } المساحات.
pirates-push-brief = { $attacker } كباش { $defender } إلى الموضع { $position }.
pirates-steal-rolls-you = إجمالي سرقتك هو { $steal }; { $target }إجمالي حراسة هو { $defend }.
pirates-steal-rolls-you-brief = سرقة { $steal }; حارس { $defend }.
pirates-steal-rolls-defender = { $attacker }إجمالي سرقة هو { $steal }; إجمالي الحراسة الخاصة بك هو { $defend }.
pirates-steal-rolls-defender-brief = سرقة { $steal }; حارسك { $defend }.
pirates-steal-rolls-observer = { $attacker } محاولات سرقة من { $defender }: سرقة { $steal }, حارس { $defend }.
pirates-steal-rolls-observer-brief = { $attacker } يسرق في { $steal } ضد { $defender } في { $defend }.
pirates-steal-success-you = أنت تسرق { $gem } من { $target }. البضائع الخاصة بك تستحق { $attacker_score } نقاط؛ لهم يستحق { $defender_score }.
pirates-steal-success-you-brief = أنت تسرق { $gem } من { $target }.
pirates-steal-success-them = { $attacker } يسرق { $gem }. حمولتهم تستحق { $attacker_score } نقاط؛ لك يستحق { $defender_score }.
pirates-steal-success-them-brief = { $attacker } يسرق { $gem }.
pirates-steal-success = { $attacker } يسرق { $gem } من { $defender }. قيم البضائع الخاصة بهم هي الآن { $attacker_score } و { $defender_score } النقاط على التوالي.
pirates-steal-success-brief = { $attacker } يسرق { $gem } من { $defender }.
pirates-steal-failed-you = إجمالي سرقتك { $steal } لا يتغلب { $target }إجمالي حراسة { $defend }. أنت لا تسرق شيئا.
pirates-steal-failed-you-brief = سرقتك فاشلة، { $steal } إلى { $defend }.
pirates-steal-failed-defender = توقف { $attacker }سرقة { $defend } إلى { $steal }، واحتفظ ببضائعك.
pirates-steal-failed-defender-brief = توقف { $attacker }سرقة.
pirates-steal-failed = { $defender } توقف { $attacker }سرقة { $defend } إلى { $steal }.
pirates-steal-failed-brief = { $attacker } فشل في السرقة من { $defender }.
pirates-steal-no-gems-you = لا يمكنك السرقة من { $target } لأنهم لم يعودوا يحملون جوهرة. اختر دفعة بدلا من ذلك.
pirates-steal-no-gems-you-brief = { $target } ليس لديه جوهرة للسرقة.
pirates-steal-no-gems-defender = { $attacker } لا يمكن أن يسرق منك لأن بضائعك لا تحتوي على أحجار كريمة.
pirates-steal-no-gems-defender-brief = ليس لديك جوهرة لـ { $attacker } لسرقة.
pirates-steal-no-gems = { $attacker } لا يمكن السرقة من { $defender } لأن المدافع لا يحمل أي جواهر.
pirates-steal-no-gems-brief = { $defender } ليس لديه جوهرة للسرقة.
# Skills and skill state
pirates-use-skill = استخدم مهارة
pirates-select-skill = اختر مهارة غير مقفلة
pirates-unknown-skill = مهارة غير معروفة
pirates-skill-error = { $message }
pirates-skill-selection-stale = لم يعد اختيار المهارات هذا متاحًا في مستواك الحالي أو حالة اللعبة. أعد فتح قائمة المهارات واختر مهارة متاحة.
pirates-req-level = { $skill } يتطلب المستوى { $required }; أنت في المستوى { $current }.
pirates-requires-level =
    { $action ->
        [move_2] الإبحار مسافتين
        [move_3] الإبحار ثلاث مسافات
       *[other] ذلك الفعل
    } يتطلب المستوى { $required }; أنت في المستوى { $current }.
pirates-skill-cooldown = { $name } يتعافى ل { $turns } المزيد من المنعطفات الخاصة بك.
pirates-skill-active = { $name } نشط بالفعل لـ { $turns } المزيد من المنعطفات الخاصة بك.
pirates-skill-already-activated-this-turn = لقد قمت بالفعل بتنشيط تعزيز القتال في هذا الدور. قم بحركة أو إجراء مدفعي بعد ذلك.
pirates-skill-no-uses = Gem Seeker ليس له استخدامات متبقية في هذه اللعبة.
pirates-skill-no-gems = لا يستطيع الباحث عن الأحجار الكريمة العثور على هدف لأنه لا توجد جواهر غير مجمعة.
pirates-skill-no-targets = لا توجد سفينة منافسة ضمن { $range }الحالية -النطاق المكاني لهذه المهارة.
pirates-skill-incompatible = { $skill } لا يمكن تفعيلها أثناء { $active } نشط. انتظر حتى انتهاء التأثير الحالي.
pirates-battleship-after-buff = لا يمكن إطلاق السفينة الحربية بعد تفعيل تعزيز القتال في هذا الدور. استخدم التعزيز مع طلقة مدفع عادية، أو انتظر حتى الدور التالي.
pirates-menu-active = { $name } (نشط لـ { $turns } المزيد من المنعطفات)
pirates-menu-cooldown = { $name } (التعافي لـ { $turns } المزيد من المنعطفات)
pirates-menu-activate = تفعيل { $name }
pirates-menu-gem-seeker = { $name } ({ $uses } الاستخدامات المتبقية)
pirates-active-skill-status = { $skill }, { $turns } المنعطفات المتبقية
pirates-no-active-skills = لا شيء
pirates-skill-activated = { $player } ينشط { $skill }. { $effect }
pirates-skill-activated-brief = { $player } ينشط { $skill }.
pirates-buff-expired-you =  { $skill } الخاص بك  ينتهي التأثير قبل أن يبدأ هذا المنعطف.
pirates-buff-expired-you-brief =  { $skill } الخاص بك  تنتهي.
pirates-buff-expired = { $player }'s { $skill } ينتهي التأثير قبل أن يبدأ دورهم.
pirates-buff-expired-brief = { $player } { $skill } تنتهي.
pirates-skill-instinct-name = غريزة البحار
pirates-skill-instinct-desc = قم بمراجعة كل قطاع من خمسة قطاعات فضائية، بما في ذلك الأحجار الكريمة غير المجمعة والسفن المنافسة. إجراء المعلومات هذا لا ينهي الدور.
pirates-instinct-header = مخطط غريزة البحار، مقسم إلى ثمانية قطاعات:
pirates-instinct-sector =
    القطاع { $sector }, المواقف { $start } من خلال { $end }: { $gems } { $gems ->
        [one] جوهرة غير مجمعة
       *[other] جواهر غير محصلة
    }, { $players } منافس { $players ->
        [one] سفينة
       *[other] السفن
    }.
pirates-skill-portal-name = البوابة
pirates-skill-portal-desc = اختر محيطًا مختلفًا يشغله المنافس، أو اختر Random للانتقال فوريًا إلى أي مساحة على الخريطة. التهدئة: 3 من دوراتك.
pirates-resolve-portal = اختر وجهة البوابة
pirates-select-portal-ocean = اختر محيطًا مختلفًا يشغله المنافس، أو اختر عشوائيًا لأي مساحة خريطة
pirates-portal-option =
    { $ocean }; السفن: { $ships }; { $gems } غير مجمعة { $gems ->
        [one] جوهرة
       *[other] جواهر
    }
pirates-portal-option-random = مساحة الخريطة العشوائية
pirates-portal-option-unavailable = هذا المحيط ليس وجهة بوابة صالحة لأنه محيطك الحالي أو لا تشغله أي سفينة منافسة. اختر وجهة أخرى.
pirates-must-resolve-portal = نظرًا لأنك استخدمت Portal، فإن دورك مقيد بهذه المهارة. اختر وجهة، أو اختر عشوائيًا، لإكمال البوابة وإنهاء دورك.
pirates-no-pending-portal = لا توجد وجهة مدخل معلقة يمكنك حلها.
pirates-portal-no-ships = لا تتوفر وجهة محددة لبوابة المحيط المنافس، ولكن لا يزال بإمكان Random إرسالك إلى أي مساحة خريطة.
pirates-portal-fizzle-you = وجهة البوابة الإلكترونية الخاصة بك لم تعد صالحة. اختر Random للانتقال فوريًا إلى أي مكان على الخريطة، أو اختر وجهة صالحة أخرى.
pirates-portal-fizzle-you-brief = اختر عشوائيًا أو وجهة بوابة صالحة أخرى.
pirates-portal-fizzle = { $player }وجهة البوابة الإلكترونية لم تعد صالحة.
pirates-portal-fizzle-brief = { $player } يجب أن تختار وجهة بوابة أخرى.
pirates-portal-success-you = تسافر عبر البوابة إلى { $ocean }، الوصول إلى الموضع { $position }. تدخل البوابة في فترة التهدئة لمدة 3 من دوراتك.
pirates-portal-success-you-brief = أنت بوابة إلى الموضع { $position } في { $ocean }.
pirates-portal-success = { $player } يسافر عبر بوابة إلى { $ocean }، الوصول إلى الموضع { $position }.
pirates-portal-success-brief = { $player } بوابات لوضع { $position }.
pirates-skill-seeker-name = الباحث عن الجوهرة
pirates-skill-seeker-desc = اكشف عن الموقع الدقيق لجوهرة واحدة لم يتم جمعها. ثلاثة استخدامات لكل لعبة؛ استخدامه لا ينتهي بدوره.
pirates-gem-seeker-reveal = يقوم Gem Seeker بتحديد موقع { $gem } في الموضع { $position }. لديك { $uses } يستخدم ما تبقى من هذه اللعبة.
pirates-skill-sword-name = مقاتل بالسيف
pirates-skill-sword-desc = احصل على هجوم +2 لمدة 3 من دوراتك. التهدئة: 6 دورات. لا يمكن أن يتداخل مع الكابتن الماهر.
pirates-sword-fighter-activated = تقوم بتفعيل Sword Fighter: +{ $bonus } الهجوم على { $turns } من دوراتك. فترة التهدئة: { $cooldown } المنعطفات. لا يزال بإمكانك التحرك أو إطلاق هذا المنعطف.
pirates-sword-fighter-activated-brief = مقاتل السيف نشط: +{ $bonus } هجوم.
pirates-skill-push-name = سرعة الصدم
pirates-skill-push-desc = أضف مسافتين إلى دفعات الصعود لمدة 3 من دوراتك. التهدئة: 6 دورات.
pirates-push-activated = قمت بتنشيط سرعة الصدم: +{ $bonus } مساحات لدفعات الصعود لـ { $turns } من دوراتك. فترة التهدئة: { $cooldown } المنعطفات. لا يزال بإمكانك التحرك أو إطلاق هذا المنعطف.
pirates-push-activated-brief = سرعة الصدم النشطة: +{ $bonus } مسافة الدفع.
pirates-skill-captain-name = الكابتن الماهر
pirates-skill-captain-desc = احصل على هجوم +1 ودفاع +1 لمدة 4 من دوراتك. التهدئة: 7 دورات. لا يمكن أن يتداخل مع Sword Fighter.
pirates-skilled-captain-activated = قمت بتفعيل الكابتن الماهر: +{ $attack } هجوم و +{ $defense } دفاع عن { $turns } من دوراتك. فترة التهدئة: { $cooldown } المنعطفات. لا يزال بإمكانك التحرك أو إطلاق هذا المنعطف.
pirates-skilled-captain-activated-brief = الكابتن الماهر النشط: +{ $attack } هجوم +{ $defense } دفاع.
pirates-skill-battleship-name = سفينة حربية
pirates-skill-battleship-desc = أطلق طلقتين مدفعيتين مستهدفتين للطاقم، دون الحصول على مكافآت الصعود. هذا ينهي الدور. التهدئة: 4 دورات.
pirates-battleship-activated = قمت بإطلاق سفينة حربية لـ { $shots } طلقات مدفع. يختار طاقمك الهدف الأكثر قيمة في النطاق لكل طلقة؛ الزيارات لا تمنح الصعود. فترة التهدئة: { $cooldown } المنعطفات.
pirates-battleship-activated-brief = قمت بإطلاق سفينة حربية لـ { $shots } لقطات.
pirates-battleship-activated-player = { $player } تطلق سفينة حربية لـ { $shots } طلقات مدفع. الضربات من هذه الطلقات لا تمنح الصعود.
pirates-battleship-activated-player-brief = { $player } تطلق سفينة حربية.
pirates-battleship-shot = يطلق طاقمك النار على سفينة حربية { $shot } في { $target }.
pirates-battleship-shot-brief = لقطة { $shot } في { $target }.
pirates-battleship-shot-player = { $player }أطلق طاقم السفينة الحربية النار { $shot } في { $target }.
pirates-battleship-shot-player-brief = { $player } حرائق في { $target }.
pirates-battleship-no-targets = لا يمكن لطاقمك إطلاق النار { $shot } لأنه لم يبق منافس في { $range } المساحات. تنتهي السفينة الحربية.
pirates-battleship-no-targets-brief = لا يوجد هدف للتسديد { $shot }.
pirates-battleship-no-targets-player = { $player } لا يمكن إطلاق رصاصة سفينة حربية { $shot } لأنه لم يبق منافس في { $range } المساحات.
pirates-battleship-no-targets-player-brief = { $player } لا يوجد هدف للتصويب { $shot }.
pirates-skill-devastation-name = دمار مزدوج
pirates-skill-devastation-desc = قم بزيادة نطاق المدفع العادي من 5 إلى 10 مسافات لمدة 3 من دوراتك. التهدئة: 10 دورات. غير متوافق مع سفينة حربية.
pirates-double-devastation-activated = تقوم بتنشيط Double Devastation: يصبح نطاق المدفع { $range } مساحات لـ { $turns } من دوراتك. فترة التهدئة: { $cooldown } المنعطفات. لا يزال بإمكانك التحرك أو إطلاق هذا المنعطف.
pirates-double-devastation-activated-brief = الدمار المزدوج نشط: النطاق { $range }.
# Options and validation
pirates-set-combat-xp-multiplier = مضاعف مكافحة XP: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = أدخل مضاعف XP القتالي من 0.1 إلى 3.0
pirates-option-changed-combat-xp = تم ضبط مضاعف Combat XP على { $combat_multiplier }.
pirates-desc-combat-xp-multiplier = يقيس XP من ضربات المدفع والدفاعات الناجحة. يتم تطبيق مضاعف Golden Moon بشكل منفصل (الافتراضي 1.0، النطاق 0.1-3.0).
pirates-set-find-gem-xp-multiplier = مضاعف XP لاسترداد الأحجار الكريمة: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = أدخل مضاعف XP لاسترداد الأحجار الكريمة من 0.1 إلى 3.0
pirates-option-changed-find-gem-xp = تم ضبط مضاعف XP لاسترداد الأحجار الكريمة على { $find_gem_multiplier }.
pirates-desc-find-gem-xp-multiplier = تُمنح نقاط الخبرة عندما تستعيد سفينة جوهرة، بما في ذلك بعد الحركة القسرية (الافتراضي 1.0، النطاق 0.1-3.0).
pirates-set-gem-stealing = سرقة الجوهرة : { $mode }
pirates-select-gem-stealing = اختر كيفية استخدام قوائم سرقة الصعود للمكافآت القتالية
pirates-option-changed-stealing = تم تعيين سرقة الأحجار الكريمة على { $mode }.
pirates-desc-gem-stealing = يتحكم في ما إذا كانت سرقة الأحجار الكريمة متاحة بعد الإصابة المباشرة وما إذا كانت مكافآت الهجوم والدفاع النشطة تعمل على تعديل قائمة السرقة.
pirates-stealing-with-bonus = ممكّنة بمكافآت قتالية
pirates-stealing-no-bonus = ممكّن بدون مكافآت قتالية
pirates-stealing-disabled = عاجز؛ الصعود يمكن أن يدفع فقط
pirates-error-combat-xp-range = مضاعف XP القتالي هو { $value }، خارج النطاق المدعوم لـ { $min } إلى { $max }. اضبطه ضمن هذا النطاق قبل البدء.
pirates-error-gem-xp-range = مضاعف XP لاسترداد الأحجار الكريمة هو { $value }، خارج النطاق المدعوم لـ { $min } إلى { $max }. اضبطه ضمن هذا النطاق قبل البدء.
pirates-error-stealing-mode = وضع سرقة الجوهرة المخزنة، { $mode }، غير مدعوم. اختر أحد أوضاع سرقة الأحجار الكريمة المدرجة قبل البدء.
# Ocean names
pirates-ocean-rory = محيط روري
pirates-ocean-dev = المطور العميق
pirates-ocean-par = بحر الجنة للمبرمجين
pirates-ocean-pal = مياه القصر
pirates-ocean-sil = مضيق سيلفا
pirates-ocean-kai = تيار كاي
pirates-ocean-gam = خليج اللاعبين
pirates-ocean-ser = غرفة خادم البحر
pirates-ocean-bat = باتل باي
pirates-ocean-cod = قناة تجميع الأكواد
pirates-ocean-unknown = محيط غير معروف
# Gem names
pirates-gem-0 = أوبال
pirates-gem-1 = روبي
pirates-gem-2 = العقيق
pirates-gem-3 = الماس
pirates-gem-4 = ياقوت
pirates-gem-5 = زمرد
pirates-gem-6 = جوهرة القصر
pirates-gem-7 = جوهرة بلاستيكية كبيرة
pirates-gem-8 = حجر اللقيط الأزرق الرائع
pirates-gem-9 = جمشت
pirates-gem-10 = خاتم ذهبي
pirates-gem-11 = حجر اللب الأحمر الرائع
pirates-gem-12 = حجر جيري أحمر رائع
pirates-gem-13 = حجر القمر
pirates-gem-14 = اللازورد
pirates-gem-15 = العنبر
pirates-gem-16 = السترين
pirates-gem-17 = بالتأكيد ليست اللؤلؤة السوداء الملعونة (tm)
pirates-gem-unknown = جوهرة مجهولة
pirates-gem-none = لا الأحجار الكريمة
