game-name-pirates = قراصنة البحار المفقودة

# Setup and round flow
pirates-welcome = مرحبًا بك في قراصنة البحار المفقودة. أبحر عبر المسار المكوّن من أربعين مربعًا، واستعد الجواهر المتناثرة، وتفوّق على الأطقم المنافسة.
pirates-welcome-brief = مرحبًا بك في قراصنة البحار المفقودة.
pirates-oceans = تعبر رحلتك { $oceans }.
pirates-gems-placed = تم إخفاء كل الجواهر البالغ عددها { $total } على طول المسار. تفوز أعلى قيمة حمولة بعد استعادة الجوهرة الأخيرة.
pirates-gems-placed-brief = { $total } جوهرة مخبأة على طول المسار.
pirates-golden-moon = يبزغ القمر الذهبي في الجولة { $round }. تتضاعف كل مكافأة خبرة ثلاث مرات في هذه الجولة.
pirates-golden-moon-brief = القمر الذهبي: خبرة ثلاثية في الجولة { $round }.
pirates-turn-you = دورك في الجولة { $round }. أنت في الموضع { $position } في { $ocean }.
pirates-turn-you-brief = دورك. الموضع { $position }.
pirates-turn = دور { $player } في الجولة { $round }، في الموضع { $position } في { $ocean }.
pirates-turn-brief = دور { $player }.

# Movement and map information
pirates-move-left = أبحر مربعًا واحدًا إلى اليسار
pirates-move-right = أبحر مربعًا واحدًا إلى اليمين
pirates-move-2-left = أبحر مربعين إلى اليسار
pirates-move-2-right = أبحر مربعين إلى اليمين
pirates-move-3-left = أبحر ثلاثة مربعات إلى اليسار
pirates-move-3-right = أبحر ثلاثة مربعات إلى اليمين
pirates-move-you = تبحر { $tiles } { $tiles ->
    [one] مربعًا
   *[other] مربعات
} إلى { $direction } لتصل إلى الموضع { $position } في { $ocean }.
pirates-move-you-brief = تبحر إلى الموضع { $position }.
pirates-move = يبحر { $player } { $tiles } { $tiles ->
    [one] مربعًا
   *[other] مربعات
} إلى { $direction } ليصل إلى الموضع { $position } في { $ocean }.
pirates-move-brief = يبحر { $player } إلى الموضع { $position }.
pirates-map-edge = لا يمكنك الإبحار أبعد في ذلك الاتجاه؛ الموضع { $position } هو حافة المسار. اختر إجراءً آخر.
pirates-dir-left = اليسار
pirates-dir-right = اليمين
pirates-your-position = أنت في الموضع { $position }، القطاع { $sector }، في { $ocean }.
pirates-check-position = تحقق من الموضع
pirates-check-moon = تحقق من القمر الذهبي
pirates-moon-active = القمر الذهبي نشط في الجولة { $round }. الخبرة مضاعفة ثلاث مرات. استعادت الأطقم { $collected } من أصل { $total } جوهرة، وتبقّى { $remaining }.
pirates-moon-inactive = القمر الذهبي غير نشط في الجولة { $round }. سيعود بعد { $rounds } { $rounds ->
    [one] جولة
   *[other] جولات
}. استعادت الأطقم { $collected } من أصل { $total } جوهرة، وتبقّى { $remaining }.

# Status and results
pirates-check-status = تحقق من حالة الطاقم
pirates-check-status-detailed = حالة الطاقم المفصّلة
pirates-status-line = { $player }: المستوى { $level}؛ { $xp } نقطة خبرة إجمالية، { $progress } من أصل { $needed } نقطة خبرة نحو المستوى التالي؛ { $points }؛ { $gem_count } { $gem_count ->
    [one] جوهرة
   *[other] جواهر
}{ $detail ->
    [yes] ؛ الموضع { $position } في { $ocean }؛ الحمولة: { $gems }؛ التأثيرات النشطة: { $skills }
   *[no] { "" }
}.
pirates-end-score-line = { $rank }. { $player}: { $points }، المستوى { $level }
pirates-all-gems-collected = تمت استعادة الجوهرة الأخيرة. تقارن الأطقم حمولاتها.
pirates-all-gems-collected-brief = تمت استعادة الجوهرة الأخيرة.
pirates-you-win = تفوز بـ { $score } نقطة.
pirates-you-win-brief = تفوز: { $score } نقطة.
pirates-winner = يفوز { $player } بـ { $score } نقطة.
pirates-winner-brief = يفوز { $player }: { $score } نقطة.
pirates-you-tie = تتعادل على المركز الأول مع { $players } عند { $score } نقطة.
pirates-you-tie-brief = تتعادل على المركز الأول عند { $score }.
pirates-players-tie = يتعادل { $players } على المركز الأول عند { $score } نقطة.
pirates-players-tie-brief = يتعادل { $players } عند { $score }.

# Gems and XP
pirates-gem-found-you = تستعيد { $gem }، التي تساوي { $value } { $value ->
    [one] نقطة
   *[other] نقطة
}. تساوي حمولتك الآن { $score } نقطة؛ وتبقّى { $remaining } جوهرة في البحر.
pirates-gem-found-you-brief = تستعيد { $gem }. النتيجة: { $score }.
pirates-gem-found = يستعيد { $player } { $gem }، التي تساوي { $value } { $value ->
    [one] نقطة
   *[other] نقطة
}. تساوي حمولته الآن { $score } نقطة؛ وتبقّى { $remaining } جوهرة في البحر.
pirates-gem-found-brief = يستعيد { $player } { $gem }.
pirates-xp-gained-you = تكسب { $xp } نقطة خبرة مقابل { $reason ->
    [gem] استعادة جوهرة
    [attack] إصابة بالمدفع
    [defense] صد هجوم مدفعي
   *[other] إكمال إجراء
}. لديك الآن { $total } نقطة خبرة إجمالية.
pirates-xp-gained-you-brief = تكسب { $xp } نقطة خبرة. الإجمالي: { $total }.
pirates-xp-gained-player = يكسب { $player } { $xp } نقطة خبرة مقابل { $reason ->
    [gem] استعادة جوهرة
    [attack] إصابة بالمدفع
    [defense] صد هجوم مدفعي
   *[other] إكمال إجراء
}، ليصل إلى { $total } نقطة خبرة إجمالية.
pirates-xp-gained-player-brief = يكسب { $player } { $xp } نقطة خبرة.
pirates-level-up-you = تصل إلى المستوى { $level }.
pirates-level-up-you-brief = تصل إلى المستوى { $level }.
pirates-level-up = يصل { $player } إلى المستوى { $level }.
pirates-level-up-brief = يصل { $player } إلى المستوى { $level }.
pirates-level-up-multiple-you = تكسب { $levels } مستويات وتصل إلى المستوى { $level }.
pirates-level-up-multiple-you-brief = تصل إلى المستوى { $level }.
pirates-level-up-multiple = يكسب { $player } { $levels } مستويات ويصل إلى المستوى { $level }.
pirates-level-up-multiple-brief = يصل { $player } إلى المستوى { $level }.
pirates-skills-unlocked-you = عند المستوى { $level }، تفتح { $skills }.
pirates-skills-unlocked-you-brief = تفتح { $skills }.
pirates-skills-unlocked = عند المستوى { $level }، يفتح { $player } { $skills }.
pirates-skills-unlocked-brief = يفتح { $player } { $skills }.

# Cannon combat
pirates-cannonball = أطلق قذيفة مدفع
pirates-select-cannon-target = اختر سفينة ضمن مدى المدفع
pirates-target-option = { $player }، يبعد { $distance } { $distance ->
    [one] مربعًا
   *[other] مربعات
}، { $score } نقطة، يحمل { $gems } { $gems ->
    [one] جوهرة
   *[other] جواهر
}
pirates-target-unavailable = سفينة غير متاحة
pirates-no-targets = لا توجد سفينة منافسة ضمن مدى مدفعك الحالي البالغ { $range } مربعًا. اختر الحركة أو مهارة أخرى متاحة.
pirates-target-out-of-range = لم تعد { $target } ضمن مدى مدفعك البالغ { $range } مربعًا من الموضع { $position }. اختر إجراءً آخر.
pirates-attack-you-fire = تطلق قذيفة مدفع على { $target }.
pirates-attack-you-fire-brief = تطلق النار على { $target }.
pirates-attack-incoming = يطلق { $attacker } قذيفة مدفع عليك.
pirates-attack-incoming-brief = يطلق { $attacker } النار عليك.
pirates-attack-fired = يطلق { $attacker } قذيفة مدفع على { $defender }.
pirates-attack-fired-brief = يطلق { $attacker } النار على { $defender }.
pirates-combat-rolls-you = نرد هجومك هو { $attack_die}، زائد { $attack_bonus}، ليصبح الإجمالي { $attack_total}. نرد دفاع { $defender } هو { $defense_die}، زائد { $defense_bonus}، ليصبح الإجمالي { $defense_total}.
pirates-combat-rolls-you-brief = الهجوم { $attack_total}؛ الدفاع { $defense_total}.
pirates-combat-rolls-defender = يهاجم { $attacker } بنرد { $attack_die}، زائد { $attack_bonus}، ليصبح الإجمالي { $attack_total}. نرد دفاعك هو { $defense_die}، زائد { $defense_bonus}، ليصبح الإجمالي { $defense_total}.
pirates-combat-rolls-defender-brief = الهجوم { $attack_total}؛ دفاعك { $defense_total}.
pirates-combat-rolls-observer = يهاجم { $attacker } بنرد { $attack_die}، زائد { $attack_bonus}، ليصبح الإجمالي { $attack_total}. يدافع { $defender } بنرد { $defense_die}، زائد { $defense_bonus}، ليصبح الإجمالي { $defense_total}.
pirates-combat-rolls-observer-brief = { $attacker } { $attack_total}؛ { $defender } { $defense_total}.
pirates-attack-hit-you = إصابة مباشرة. يتفوق إجماليك { $attack_total } على إجمالي { $target } البالغ { $defense_total}؛ اختر إجراء اقتحام متاحًا.
pirates-attack-hit-you-brief = تصيب { $target }، { $attack_total } مقابل { $defense_total}.
pirates-attack-hit-them = يصيبك { $attacker }، { $attack_total } مقابل { $defense_total}، وقد يقتحم سفينتك الآن.
pirates-attack-hit-them-brief = يصيبك { $attacker }، { $attack_total } مقابل { $defense_total}.
pirates-attack-hit = يصيب { $attacker } { $defender }، { $attack_total } مقابل { $defense_total}، وقد يقتحم.
pirates-attack-hit-brief = يصيب { $attacker } { $defender }.
pirates-attack-hit-no-boarding-you = إصابة مباشرة. يتفوق إجماليك { $attack_total } على إجمالي { $target } البالغ { $defense_total}. تمنح إصابة البارجة هذه خبرة لكن دون إجراء اقتحام.
pirates-attack-hit-no-boarding-you-brief = تصيب { $target }، { $attack_total } مقابل { $defense_total}؛ دون اقتحام.
pirates-attack-hit-no-boarding-them = يصيبك { $attacker }، { $attack_total } مقابل { $defense_total}. لا تمنح إصابات البارجة إجراءات اقتحام.
pirates-attack-hit-no-boarding-them-brief = يصيبك { $attacker }؛ دون اقتحام.
pirates-attack-hit-no-boarding = يصيب { $attacker } { $defender }، { $attack_total } مقابل { $defense_total}. لا تمنح إصابة البارجة هذه إجراء اقتحام.
pirates-attack-hit-no-boarding-brief = يصيب { $attacker } { $defender}؛ دون اقتحام.
pirates-attack-miss-you = إجمالي هجومك { $attack_total } لا يتفوق على إجمالي دفاع { $target } البالغ { $defense_total}. ينتهي دورك.
pirates-attack-miss-you-brief = تخطئ { $target }، { $attack_total } مقابل { $defense_total}.
pirates-attack-miss-them = تصد { $attacker } بإجمالي دفاع { $defense_total } ضد { $attack_total}.
pirates-attack-miss-them-brief = تصد { $attacker }، { $defense_total } مقابل { $attack_total}.
pirates-attack-miss = يصد { $defender } { $attacker }، { $defense_total } مقابل { $attack_total}.
pirates-attack-miss-brief = يخطئ { $attacker } { $defender }.

# Boarding
pirates-resolve-boarding = نفّذ الاقتحام
pirates-select-boarding-action = أصاب المدفع. اختر كيفية تنفيذ إجراء الاقتحام
pirates-boarding-steal = حاول سرقة جوهرة
pirates-boarding-push-left = اصدم المدافع إلى اليسار
pirates-boarding-push-right = اصدم المدافع إلى اليمين
pirates-boarding-option-unknown = إجراء اقتحام غير معروف
pirates-must-resolve-boarding = نفّذ إجراء الاقتحام المعلّق قبل اتخاذ إجراء دور آخر.
pirates-no-pending-boarding = لا يوجد إجراء اقتحام معلّق لتنفيذه.
pirates-boarding-stale = لم يعد لإجراء الاقتحام المعلّق مدافع صالح، لذا تم إلغاؤه. اختر إجراء دور آخر.
pirates-boarding-option-unavailable = لم يعد { $action } متاحًا ضد { $defender }. اختر أحد خيارات الاقتحام الحالية.
pirates-push-you = تصدم { $target } إلى { $direction } من الموضع { $old_pos } إلى { $new_pos }، محرّكًا { GENDER_TERM($target_gender, "object") } مسافة { $distance } مربعات. أضافت مكافأة الصدم لديك { $bonus } مربعات إضافية.
pirates-push-you-brief = تصدم { $target } إلى الموضع { $position }.
pirates-push-them = يصدمك { $attacker } إلى { $direction } من الموضع { $old_pos } إلى { $new_pos }، محرّكًا إياك مسافة { $distance } مربعات.
pirates-push-them-brief = يصدمك { $attacker } إلى الموضع { $position }.
pirates-push = يصدم { $attacker } { $defender } إلى { $direction } من الموضع { $old_pos } إلى { $new_pos }، مسافة { $distance } مربعات.
pirates-push-brief = يصدم { $attacker } { $defender } إلى الموضع { $position }.
pirates-steal-rolls-you = إجمالي سرقتك هو { $steal}؛ إجمالي حراسة { $target } هو { $defend}.
pirates-steal-rolls-you-brief = السرقة { $steal}؛ الحراسة { $defend}.
pirates-steal-rolls-defender = إجمالي سرقة { $attacker } هو { $steal}؛ إجمالي حراستك هو { $defend}.
pirates-steal-rolls-defender-brief = السرقة { $steal}؛ حراستك { $defend}.
pirates-steal-rolls-observer = يحاول { $attacker } السرقة من { $defender}: السرقة { $steal}، الحراسة { $defend}.
pirates-steal-rolls-observer-brief = يسرق { $attacker } بـ { $steal } ضد { $defender } بـ { $defend}.
pirates-steal-success-you = تسرق { $gem } من { $target }. تساوي حمولتك { $attacker_score } نقطة؛ بينما تساوي { GENDER_TERM($target_gender, "possessive-pronoun") } { $defender_score}.
pirates-steal-success-you-brief = تسرق { $gem } من { $target }.
pirates-steal-success-them = يسرق { $attacker } { $gem } الخاصة بك. تساوي حمولة { GENDER_TERM($attacker_gender, "possessive-determiner-capitalized") } { $attacker_score } نقطة؛ وتساوي حمولتك { $defender_score}.
pirates-steal-success-them-brief = يسرق { $attacker } { $gem } الخاصة بك.
pirates-steal-success = يسرق { $attacker } { $gem } من { $defender }. أصبحت قيمتا حمولتيهما الآن { $attacker_score } و { $defender_score } نقطة على التوالي.
pirates-steal-success-brief = يسرق { $attacker } { $gem } من { $defender }.
pirates-steal-failed-you = إجمالي سرقتك { $steal } لا يتفوق على إجمالي حراسة { $target } البالغ { $defend}. لا تسرق شيئًا.
pirates-steal-failed-you-brief = تفشل سرقتك، { $steal } مقابل { $defend}.
pirates-steal-failed-defender = توقف سرقة { $attacker }، { $defend } مقابل { $steal}، وتحتفظ بحمولتك.
pirates-steal-failed-defender-brief = توقف سرقة { $attacker }.
pirates-steal-failed = يوقف { $defender } سرقة { $attacker }، { $defend } مقابل { $steal}.
pirates-steal-failed-brief = يفشل { $attacker } في السرقة من { $defender }.
pirates-steal-no-gems-you = لا يمكنك السرقة من { $target } لأن سفينة { GENDER_TERM($target_gender, "possessive-determiner") } لا تحمل أي جواهر. اختر الصدم بدلاً من ذلك.
pirates-steal-no-gems-you-brief = لا تملك { $target } جوهرة لسرقتها.
pirates-steal-no-gems-defender = لا يمكن لـ { $attacker } السرقة منك لأن حمولتك لا تحتوي على أي جواهر.
pirates-steal-no-gems-defender-brief = ليس لديك جوهرة ليسرقها { $attacker }.
pirates-steal-no-gems = لا يمكن لـ { $attacker } السرقة من { $defender } لأن المدافع لا يحمل أي جواهر.
pirates-steal-no-gems-brief = لا يملك { $defender } جوهرة لسرقتها.

# Skills and skill state
pirates-use-skill = استخدم مهارة
pirates-select-skill = اختر مهارة مفتوحة
pirates-unknown-skill = مهارة غير معروفة
pirates-skill-error = { $message }
pirates-skill-selection-stale = لم يعد اختيار المهارة هذا متاحًا في مستواك الحالي أو حالة اللعبة الحالية. أعد فتح قائمة المهارات واختر مهارة متاحة.
pirates-req-level = تتطلب { $skill } المستوى { $required}؛ أنت في المستوى { $current}.
pirates-requires-level = يتطلب { $action ->
    [move_2] الإبحار مربعين
    [move_3] الإبحار ثلاثة مربعات
   *[other] هذا الإجراء
} المستوى { $required}؛ أنت في المستوى { $current}.
pirates-skill-cooldown = { $name } في فترة استعادة لمدة { $turns } من أدوارك القادمة.
pirates-skill-active = { $name } نشطة بالفعل لمدة { $turns } من أدوارك القادمة.
pirates-skill-already-activated-this-turn = لقد فعّلت تعزيزًا قتاليًا بالفعل في هذا الدور. اتخذ إجراء حركة أو مدفع تاليًا.
pirates-skill-no-uses = لم يتبقَّ لـ "باحث الجواهر" أي استخدامات في هذه اللعبة.
pirates-skill-no-gems = لا يستطيع "باحث الجواهر" إيجاد هدف لعدم تبقّي أي جواهر غير مجمّعة.
pirates-skill-no-targets = لا توجد سفينة منافسة ضمن المدى الحالي البالغ { $range } مربعًا لهذه المهارة.
pirates-skill-incompatible = لا يمكن تفعيل { $skill } أثناء نشاط { $active }. انتظر انتهاء التأثير الحالي.
pirates-battleship-after-buff = لا يمكن إطلاق البارجة بعد تفعيل تعزيز قتالي في هذا الدور. استخدم التعزيز مع طلقة مدفع عادية، أو انتظر حتى دورك التالي.
pirates-menu-active = { $name } (نشطة لمدة { $turns } أدوار إضافية)
pirates-menu-cooldown = { $name } (في فترة استعادة لمدة { $turns } أدوار إضافية)
pirates-menu-activate = فعّل { $name }
pirates-menu-gem-seeker = { $name } ({ $uses } استخدامات متبقية)
pirates-active-skill-status = { $skill }، { $turns } أدوار متبقية
pirates-no-active-skills = لا شيء
pirates-skill-activated = يفعّل { $player } { $skill}. { $effect }
pirates-skill-activated-brief = يفعّل { $player } { $skill}.
pirates-buff-expired-you = ينتهي تأثير { $skill } لديك قبل بدء هذا الدور.
pirates-buff-expired-you-brief = ينتهي { $skill } لديك.
pirates-buff-expired = ينتهي تأثير { $skill } الخاص بـ { $player } قبل بدء دور { GENDER_TERM($player_gender, "possessive-determiner") }.
pirates-buff-expired-brief = ينتهي { $skill } الخاص بـ { $player }.

pirates-skill-instinct-name = غريزة البحّار
pirates-skill-instinct-desc = راجع كل قطاع مكوّن من خمسة مربعات، بما في ذلك الجواهر غير المجمّعة والسفن المنافسة. لا ينهي إجراء المعلومات هذا الدور.
pirates-instinct-header = مخطط غريزة البحّار، مقسّم إلى ثمانية قطاعات:
pirates-instinct-sector = القطاع { $sector}، المواضع من { $start } إلى { $end}: { $gems } { $gems ->
    [one] جوهرة غير مجمّعة
   *[other] جواهر غير مجمّعة
}، { $players } { $players ->
    [one] سفينة منافسة
   *[other] سفن منافسة
}.

pirates-skill-portal-name = البوابة
pirates-skill-portal-desc = اختر محيطًا مختلفًا يشغله منافس، أو اختر عشوائي للانتقال الفوري إلى أي مربع على الخريطة. فترة الاستعادة: 3 من أدوارك.
pirates-resolve-portal = اختر وجهة البوابة
pirates-select-portal-ocean = اختر محيطًا مختلفًا يشغله منافس، أو اختر عشوائي لأي مربع على الخريطة
pirates-portal-option = { $ocean }؛ السفن: { $ships}؛ { $gems } { $gems ->
    [one] جوهرة غير مجمّعة
   *[other] جواهر غير مجمّعة
}
pirates-portal-option-random = مربع عشوائي على الخريطة
pirates-portal-option-unavailable = ذلك المحيط ليس وجهة بوابة صالحة لأنه محيطك الحالي أو لا تشغله أي سفينة منافسة. اختر وجهة أخرى.
pirates-must-resolve-portal = لأنك استخدمت البوابة، أصبح دورك مقفلاً على تلك المهارة. اختر وجهة، أو اختر عشوائي، لإكمال البوابة وإنهاء دورك.
pirates-no-pending-portal = لا توجد وجهة بوابة معلّقة لتنفيذها.
pirates-portal-no-ships = لا توجد وجهة بوابة محددة في محيط منافس، لكن يمكن لعشوائي أن ينقلك إلى أي مربع على الخريطة.
pirates-portal-fizzle-you = لم تعد وجهة بوابتك صالحة. اختر عشوائي للانتقال إلى أي مكان على الخريطة، أو اختر وجهة صالحة أخرى.
pirates-portal-fizzle-you-brief = اختر عشوائي أو وجهة بوابة صالحة أخرى.
pirates-portal-fizzle = لم تعد وجهة بوابة { $player } صالحة.
pirates-portal-fizzle-brief = يجب على { $player } اختيار وجهة بوابة أخرى.
pirates-portal-success-you = تسافر عبر البوابة إلى { $ocean}، وتصل إلى الموضع { $position}. تدخل البوابة فترة استعادة لمدة 3 من أدوارك.
pirates-portal-success-you-brief = تنتقل عبر البوابة إلى الموضع { $position } في { $ocean}.
pirates-portal-success = يسافر { $player } عبر بوابة إلى { $ocean}، ويصل إلى الموضع { $position}.
pirates-portal-success-brief = ينتقل { $player } عبر البوابة إلى الموضع { $position}.

pirates-skill-seeker-name = باحث الجواهر
pirates-skill-seeker-desc = اكشف الموضع الدقيق لجوهرة واحدة غير مجمّعة. ثلاثة استخدامات لكل لعبة؛ استخدامها لا ينهي الدور.
pirates-gem-seeker-reveal = يحدد باحث الجواهر موقع { $gem } في الموضع { $position}. لديك { $uses } استخدامات متبقية في هذه اللعبة.

pirates-skill-sword-name = مبارز السيف
pirates-skill-sword-desc = احصل على +2 هجوم لمدة 3 من أدوارك. فترة الاستعادة: 6 أدوار. لا يمكن أن يتداخل مع القبطان الماهر.
pirates-sword-fighter-activated = تفعّل مبارز السيف: +{ $bonus } هجوم لمدة { $turns } من أدوارك. فترة الاستعادة: { $cooldown } أدوار. لا يزال بإمكانك التحرك أو إطلاق النار في هذا الدور.
pirates-sword-fighter-activated-brief = مبارز السيف نشط: +{ $bonus } هجوم.

pirates-skill-push-name = سرعة الصدم
pirates-skill-push-desc = أضف مربعين إلى صدمات الاقتحام لمدة 3 من أدوارك. فترة الاستعادة: 6 أدوار.
pirates-push-activated = تفعّل سرعة الصدم: +{ $bonus } مربعات لصدمات الاقتحام لمدة { $turns } من أدوارك. فترة الاستعادة: { $cooldown } أدوار. لا يزال بإمكانك التحرك أو إطلاق النار في هذا الدور.
pirates-push-activated-brief = سرعة الصدم نشطة: +{ $bonus } مسافة صدم.

pirates-skill-captain-name = القبطان الماهر
pirates-skill-captain-desc = احصل على +1 هجوم و+1 دفاع لمدة 4 من أدوارك. فترة الاستعادة: 7 أدوار. لا يمكن أن يتداخل مع مبارز السيف.
pirates-skilled-captain-activated = تفعّل القبطان الماهر: +{ $attack } هجوم و+{ $defense } دفاع لمدة { $turns } من أدوارك. فترة الاستعادة: { $cooldown } أدوار. لا يزال بإمكانك التحرك أو إطلاق النار في هذا الدور.
pirates-skilled-captain-activated-brief = القبطان الماهر نشط: +{ $attack } هجوم، +{ $defense } دفاع.

pirates-skill-battleship-name = البارجة
pirates-skill-battleship-desc = أطلق طلقتي مدفع يستهدفهما الطاقم، دون مكافآت اقتحام. ينهي هذا الدور. فترة الاستعادة: 4 أدوار.
pirates-battleship-activated = تطلق البارجة لـ { $shots } طلقات مدفع. يختار طاقمك الهدف الأكثر قيمة ضمن المدى لكل طلقة؛ الإصابات لا تمنح اقتحامًا. فترة الاستعادة: { $cooldown } أدوار.
pirates-battleship-activated-brief = تطلق البارجة لـ { $shots } طلقات.
pirates-battleship-activated-player = يطلق { $player } البارجة لـ { $shots } طلقات مدفع. الإصابات من هذه الطلقات لا تمنح اقتحامًا.
pirates-battleship-activated-player-brief = يطلق { $player } البارجة.
pirates-battleship-shot = يطلق طاقمك طلقة البارجة { $shot } على { $target}.
pirates-battleship-shot-brief = الطلقة { $shot } على { $target}.
pirates-battleship-shot-player = يطلق طاقم { $player } طلقة البارجة { $shot } على { $target}.
pirates-battleship-shot-player-brief = يطلق { $player } النار على { $target}.
pirates-battleship-no-targets = لا يستطيع طاقمك إطلاق الطلقة { $shot } لعدم بقاء أي منافس ضمن { $range } مربعًا. تنتهي البارجة.
pirates-battleship-no-targets-brief = لا هدف للطلقة { $shot}.
pirates-battleship-no-targets-player = لا يستطيع { $player } إطلاق طلقة البارجة { $shot } لعدم بقاء أي منافس ضمن { $range } مربعًا.
pirates-battleship-no-targets-player-brief = لا هدف لـ { $player } في الطلقة { $shot}.

pirates-skill-devastation-name = الدمار المزدوج
pirates-skill-devastation-desc = زِد مدى المدفع العادي من 5 إلى 10 مربعات لمدة 3 من أدوارك. فترة الاستعادة: 10 أدوار. غير متوافق مع البارجة.
pirates-double-devastation-activated = تفعّل الدمار المزدوج: يصبح مدى المدفع { $range } مربعات لمدة { $turns } من أدوارك. فترة الاستعادة: { $cooldown } أدوار. لا يزال بإمكانك التحرك أو إطلاق النار في هذا الدور.
pirates-double-devastation-activated-brief = الدمار المزدوج نشط: المدى { $range}.

# Options and validation
pirates-set-combat-xp-multiplier = مضاعف خبرة القتال: { $combat_multiplier }
pirates-enter-combat-xp-multiplier = أدخل مضاعف خبرة القتال من 0.1 إلى 3.0
pirates-option-changed-combat-xp = تم ضبط مضاعف خبرة القتال على { $combat_multiplier}.
pirates-desc-combat-xp-multiplier = يضبط حجم الخبرة المكتسبة من إصابات المدفع والدفاعات الناجحة. يُطبّق مضاعف القمر الذهبي بشكل منفصل (الافتراضي 1.0، المدى 0.1-3.0).
pirates-set-find-gem-xp-multiplier = مضاعف خبرة استعادة الجواهر: { $find_gem_multiplier }
pirates-enter-find-gem-xp-multiplier = أدخل مضاعف خبرة استعادة الجواهر من 0.1 إلى 3.0
pirates-option-changed-find-gem-xp = تم ضبط مضاعف خبرة استعادة الجواهر على { $find_gem_multiplier}.
pirates-desc-find-gem-xp-multiplier = يضبط حجم الخبرة الممنوحة عندما تستعيد سفينة جوهرة، بما في ذلك بعد الحركة القسرية (الافتراضي 1.0، المدى 0.1-3.0).
pirates-set-gem-stealing = سرقة الجواهر: { $mode }
pirates-select-gem-stealing = اختر كيفية استخدام رميات سرقة الاقتحام لمكافآت القتال
pirates-option-changed-stealing = تم ضبط سرقة الجواهر على { $mode}.
pirates-desc-gem-stealing = يتحكم في ما إذا كانت سرقة الجواهر متاحة بعد إصابة مباشرة وما إذا كانت مكافآت الهجوم والدفاع النشطة تعدّل رمية السرقة.
pirates-stealing-with-bonus = مُفعّلة مع مكافآت القتال
pirates-stealing-no-bonus = مُفعّلة بدون مكافآت القتال
pirates-stealing-disabled = معطّلة؛ الاقتحام يمكنه الصدم فقط
pirates-error-combat-xp-range = مضاعف خبرة القتال هو { $value}، خارج المدى المدعوم من { $min } إلى { $max}. اضبطه ضمن ذلك المدى قبل البدء.
pirates-error-gem-xp-range = مضاعف خبرة استعادة الجواهر هو { $value}، خارج المدى المدعوم من { $min } إلى { $max}. اضبطه ضمن ذلك المدى قبل البدء.
pirates-error-stealing-mode = وضع سرقة الجواهر المخزّن، { $mode}، غير مدعوم. اختر أحد أوضاع سرقة الجواهر المدرجة قبل البدء.

# Ocean names
pirates-ocean-rory = محيط روري
pirates-ocean-dev = أعماق المطوّر
pirates-ocean-par = بحر جنة المبرمج
pirates-ocean-pal = مياه القصر
pirates-ocean-sil = مضيق سيلفا
pirates-ocean-kai = تيار كاي
pirates-ocean-gam = خليج اللاعب
pirates-ocean-ser = بحر غرفة الخادم
pirates-ocean-bat = خليج المعركة
pirates-ocean-cod = قناة تجميع الشيفرة
pirates-ocean-unknown = محيط غير معروف

# Gem names
pirates-gem-0 = الأوبال
pirates-gem-1 = الياقوت
pirates-gem-2 = العقيق الأحمر
pirates-gem-3 = الماس
pirates-gem-4 = الياقوت الأزرق
pirates-gem-5 = الزمرد
pirates-gem-6 = جوهرة القصر
pirates-gem-7 = جوهرة بلاستيكية كبيرة
pirates-gem-8 = الحجر الأزرق اللعين الرائع
pirates-gem-9 = الجمشت
pirates-gem-10 = الخاتم الذهبي
pirates-gem-11 = حجر اللب الأحمر الرائع
pirates-gem-12 = حجر الدماء الأحمر الرائع
pirates-gem-13 = حجر القمر
pirates-gem-14 = اللازورد
pirates-gem-15 = الكهرمان
pirates-gem-16 = السيترين
pirates-gem-17 = اللؤلؤة السوداء غير الملعونة قطعًا (علامة تجارية)
pirates-gem-unknown = جوهرة غير معروفة
pirates-gem-none = لا جواهر
