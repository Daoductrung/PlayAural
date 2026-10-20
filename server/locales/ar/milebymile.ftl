game-name-milebymile = ميلاً بعد ميل

milebymile-set-distance = مسافة السباق: { $miles } ميل
milebymile-enter-distance = أدخل مسافة السباق (300-3000)
milebymile-set-winning-score = نتيجة الفوز: { $score } نقطة
milebymile-enter-winning-score = أدخل نتيجة الفوز (1000-10000)
milebymile-desc-team-mode = اللعب فردياً أو ضمن ترتيب فرق يدعمه عدد اللاعبين الحالي.
milebymile-toggle-perfect-crossing = اشتراط الوصول الدقيق: { $enabled }
milebymile-toggle-stacking = السماح بتكديس الهجمات: { $enabled }
milebymile-toggle-reshuffle = إعادة خلط كومة النفايات: { $enabled }
milebymile-toggle-karma = قاعدة الكارما: { $enabled }
milebymile-set-rig = تركيب المجموعة: { $rig }
milebymile-select-rig = اختر خيار تركيب المجموعة
milebymile-rig-none = بلا
milebymile-rig-no-duplicates = بلا تكرار
milebymile-rig-2x-attacks = هجمات مضاعفة
milebymile-rig-2x-defenses = دفاعات مضاعفة

milebymile-option-changed-distance = تم ضبط مسافة السباق على { $miles } ميل.
milebymile-desc-round-distance = المسافة الهدف لكل سباق. إذا فُعّل الوصول الدقيق، فيجب أن تكون هذه المسافة قابلة للقسمة على 25 (الافتراضي 1,000 ميل، المدى 300-3,000).
milebymile-option-changed-winning = تم ضبط نتيجة الفوز على { $score } نقطة.
milebymile-desc-winning-score = إجمالي النتيجة اللازم للفوز بمباراة ميلاً بعد ميل (الافتراضي 5,000، المدى 1,000-10,000).
milebymile-option-changed-crossing = اشتراط الوصول الدقيق { $enabled }.
milebymile-desc-only-allow-perfect-crossing = عند التفعيل، يجب أن يصل اللاعب إلى هدف السباق بالضبط؛ لا يمكن لعب بطاقات المسافة التي تتجاوز خط النهاية.
milebymile-option-changed-stacking = السماح بتكديس الهجمات { $enabled }.
milebymile-desc-allow-stacking-attacks = عند التفعيل، يمكن أن تؤثر عدة عوائق على السيارة نفسها بدلاً من أن يمنعها عائق موجود.
milebymile-option-changed-reshuffle = إعادة خلط كومة النفايات { $enabled }.
milebymile-desc-reshuffle-discard-pile = عند التفعيل، تُخلط كومة النفايات مرة أخرى في مجموعة السحب عند نفاد المجموعة.
milebymile-option-changed-karma = قاعدة الكارما { $enabled }.
milebymile-desc-karma-rule = يتحكم في استخدام بطاقات الكارما والنبذ. الهجوم بينما يملك الطرفان الكارما يُبطل الهجوم؛ المهاجم المنبوذ لا يمكنه استهداف إلا طرفاً منبوذاً آخر. يتطلب 3 سيارات أو فرق على الأقل.
milebymile-option-changed-rig = تم ضبط تركيب المجموعة على { $rig }.
milebymile-desc-rig-game = متغيّر اختياري لتركيب المجموعة: عادي، أو بلا بطاقات مكررة، أو هجمات مضاعفة، أو دفاعات مضاعفة.

milebymile-status = { $score_info }، { $miles } ميل، المشاكل: { $problems }، الوقايات: { $safeties }

milebymile-no-matching-safety = ليست لديك بطاقة الوقاية المطابقة!
milebymile-cant-play = لا يمكنك لعب { $card } لأن { $reason }.
milebymile-unplayable-card-menu-title = لا يمكن لعب البطاقة
milebymile-unplayable-discard-question = لا يمكنك لعب { $card } لأن { $reason }. هل تريد التخلص منها؟
milebymile-no-card-selected = لم تُختر بطاقة للتخلص منها.
milebymile-no-valid-targets = لا توجد أهداف صالحة لهذا العائق!
milebymile-you-drew = سحبتَ: { $card }
milebymile-you-discard = تتخلص من { $card }.
milebymile-discards = يتخلص { $player } من { $card }.
milebymile-select-target = اختر هدفاً

milebymile-you-play-distance-individual = تلعب { $distance } ميل، وأصبحت الآن عند { $total } ميل.
milebymile-plays-distance-individual = يلعب { $player } { $distance } ميل، وأصبح الآن عند { $total } ميل.
milebymile-you-play-distance-team = تلعب { $distance } ميل؛ أصبح فريقك الآن عند { $total } ميل.
milebymile-teammate-plays-distance-team = يلعب { $player } { $distance } ميل؛ أصبح فريقك الآن عند { $total } ميل.
milebymile-plays-distance-team = يلعب { $player } { $distance } ميل؛ أصبح الفريق { GENDER_TERM($player_gender, "possessive-determiner") } الآن عند { $total } ميل.

milebymile-you-complete-perfect-individual = أكملت الرحلة بوصول دقيق!
milebymile-journey-complete-perfect-individual = أكمل { $player } الرحلة بوصول دقيق!
milebymile-your-team-completes-perfect = يكمل فريقك الرحلة بوصول دقيق!
milebymile-journey-complete-perfect-team = أكمل الفريق { $team } الرحلة بوصول دقيق!
milebymile-you-complete-individual = أكملت الرحلة!
milebymile-journey-complete-individual = أكمل { $player } الرحلة!
milebymile-your-team-completes = يكمل فريقك الرحلة!
milebymile-journey-complete-team = أكمل الفريق { $team } الرحلة!

milebymile-you-play-hazard-individual = تلعب { $card } على { $target }.
milebymile-hazard-played-on-you = يلعب { $player } { $card } عليك. لديك 7 ثوانٍ للرد.
milebymile-plays-hazard-individual = يلعب { $player } { $card } على { $target }.
milebymile-you-play-hazard-team = تلعب { $card } على الفريق { $team }.
milebymile-hazard-played-on-your-team = يلعب { $player } { $card } على فريقك. لدى فريقك 7 ثوانٍ للرد.
milebymile-plays-hazard-team = يلعب { $player } { $card } على الفريق { $team }.

milebymile-you-play-card = تلعب { $card }.
milebymile-plays-card = يلعب { $player } { $card }.
milebymile-you-play-team-card = تلعب { $card } لفريقك.
milebymile-teammate-plays-team-card = يلعب { $player } { $card } لفريقك.
milebymile-opponent-plays-team-card = يلعب { $player } { $card } للفريق { GENDER_TERM($player_gender, "possessive-determiner") }.
milebymile-you-play-dirty-trick = تلعب { $card } كخدعة قذرة!
milebymile-plays-dirty-trick = يلعب { $player } { $card } كخدعة قذرة!
milebymile-you-play-dirty-trick-team = تلعب { $card } كخدعة قذرة لفريقك!
milebymile-teammate-plays-dirty-trick-team = يلعب { $player } { $card } كخدعة قذرة لفريقك!
milebymile-opponent-plays-dirty-trick-team = يلعب { $player } { $card } كخدعة قذرة للفريق { GENDER_TERM($player_gender, "possessive-determiner") }!

milebymile-deck-reshuffled = أُعيد خلط كومة النفايات في المجموعة.

milebymile-new-race = يبدأ سباق جديد!
milebymile-race-complete = اكتمل السباق! جارٍ حساب النتائج...
milebymile-earned-points = حصل { $name } على { $score } نقطة في هذا السباق: { $breakdown }.
milebymile-total-scores = النتائج الإجمالية:
milebymile-team-score = { $name }: { $score } نقطة

milebymile-from-distance = { $miles } من المسافة المقطوعة
milebymile-from-trip = { $points } من إكمال الرحلة
milebymile-from-delayed = { $points } من الإجراء المؤجل
milebymile-from-perfect = { $points } من الوصول الدقيق
milebymile-from-safe = { $points } من رحلة آمنة
milebymile-from-shutout = { $points } من إقصاء كامل
milebymile-from-safeties = { $points } من { $count } { $count ->
    [one] وقاية
    *[other] وقايات
}
milebymile-from-all-safeties = { $points } من كل الوقايات الأربع
milebymile-from-dirty-tricks = { $points } من { $count } { $count ->
    [one] خدعة قذرة
    *[other] خدع قذرة
}

milebymile-you-win-individual = تفوز باللعبة!
milebymile-wins-individual = يفوز { $player } باللعبة!
milebymile-your-team-wins = يفوز فريقك باللعبة!
milebymile-wins-team = يفوز الفريق { $team } باللعبة! ({ $members })
milebymile-final-score = النتيجة النهائية: { $score } نقطة

milebymile-karma-clash-you-target = أنت وهدفك منبوذان كلاكما! الهجوم مُبطَل.
milebymile-karma-clash-you-attacker = أنت و{ $attacker } منبوذان كلاكما! الهجوم مُبطَل.
milebymile-karma-clash-others = { $attacker } و{ $target } منبوذان كلاهما! الهجوم مُبطَل.
milebymile-karma-clash-your-team = فريقك وهدفك منبوذان كلاهما! الهجوم مُبطَل.
milebymile-karma-clash-target-team = فريقك والفريق { $team } منبوذان كلاهما! الهجوم مُبطَل.
milebymile-karma-clash-other-teams = الفريق { $attacker } والفريق { $target } منبوذان كلاهما! الهجوم مُبطَل.

milebymile-karma-shunned-you = نُبذتَ بسبب عدوانيتك! فقدت الكارما.
milebymile-karma-shunned-other = نُبذ { $player } بسبب العدوانية { GENDER_TERM($player_gender, "possessive-determiner") }!
milebymile-karma-shunned-your-team = نُبذ فريقك بسبب عدوانيته! فقد فريقك الكارما.
milebymile-karma-shunned-other-team = نُبذ الفريق { $team } بسبب عدوانيته!

milebymile-false-virtue-you = تلعب الفضيلة الزائفة وتستعيد الكارما!
milebymile-false-virtue-other = يلعب { $player } الفضيلة الزائفة ويستعيد الكارما { GENDER_TERM($player_gender, "possessive-determiner") }!
milebymile-false-virtue-teammate = يلعب { $player } الفضيلة الزائفة؛ يستعيد فريقك الكارما!
milebymile-false-virtue-opponent = يلعب { $player } الفضيلة الزائفة؛ يستعيد الفريق { GENDER_TERM($player_gender, "possessive-determiner") } الكارما!

milebymile-none = بلا

milebymile-reason-not-on-team = لستَ في فريق
milebymile-reason-stopped = تحتاج إلى ضوء انطلاق قبل أن تتمكن من القيادة
milebymile-reason-has-problem = مشكلة طريق توقف سيارتك
milebymile-reason-out-of-gas = لا يمكنك التحرك لأن وقودك نفد؛ العب الوقود أو الخزان الإضافي أولاً
milebymile-reason-flat-tire = لا يمكنك التحرك لأن لديك إطاراً مثقوباً؛ العب الإطار الاحتياطي أو المقاوم للثقب أولاً
milebymile-reason-accident = لا يمكنك التحرك لأنك تعرضت لحادث؛ العب الإصلاحات أو بارع القيادة أولاً
milebymile-reason-speed-limit = أنت تحت حد السرعة، لذا يُسمح فقط ببطاقات 25 أو 50 ميلاً
milebymile-reason-exceeds-distance = أنت عند { $current } ميل، وبطاقة { $distance } ميل ستضعك عند { $total } ميل، بعد خط النهاية البالغ { $target } ميل؛ الوصول الدقيق مُفعّل، لذا تحتاج إلى { $miles } ميل إضافي بالضبط
milebymile-reason-too-many-200s = لقد لعبت بالفعل بطاقتي 200 ميل في هذا السباق
milebymile-reason-no-targets = لا يمكن لأي خصم أن يتلقى هذا العائق بشكل قانوني الآن
milebymile-reason-no-opponents = لا توجد فرق منافسة لاستهدافها
milebymile-reason-hazard-protected = كل هدف محتمل محمي من { $card } بواسطة { $safety }
milebymile-reason-hazard-karma = لقد فقدت الكارما ولا يمكنك مهاجمة إلا هدف فقد الكارما أيضاً
milebymile-reason-hazard-duplicate-speed-limit = كل هدف محتمل تحت حد السرعة بالفعل
milebymile-reason-hazard-duplicate = كل هدف محتمل لديه { $card } بالفعل
milebymile-reason-hazard-blocked = كل هدف محتمل متوقف بالفعل بسبب عائق آخر
milebymile-reason-no-speed-limit = لستَ تحت حد سرعة
milebymile-reason-has-right-of-way = حق الأولوية يتيح لك الانطلاق دون أضواء انطلاق
milebymile-reason-already-moving = أنت تتحرك بالفعل
milebymile-reason-must-fix-first = يجب أن تصلح { $problem } أولاً بواسطة { $remedy }
milebymile-reason-has-gas = سيارتك لديها وقود
milebymile-reason-tires-fine = إطاراتك سليمة
milebymile-reason-no-accident = لم تتعرض سيارتك لحادث
milebymile-reason-has-safety = لديك تلك الوقاية بالفعل
milebymile-reason-has-karma = ما زلت تملك الكارما
milebymile-reason-generic = لا يمكن لعبها الآن

milebymile-card-out-of-gas = نفاد الوقود
milebymile-card-flat-tire = إطار مثقوب
milebymile-card-accident = حادث
milebymile-card-speed-limit = حد السرعة
milebymile-card-stop = توقّف
milebymile-card-gasoline = وقود
milebymile-card-spare-tire = إطار احتياطي
milebymile-card-repairs = إصلاحات
milebymile-card-end-of-limit = نهاية الحد
milebymile-card-green-light = ضوء الانطلاق
milebymile-card-extra-tank = خزان إضافي
milebymile-card-puncture-proof = مقاوم للثقب
milebymile-card-driving-ace = بارع القيادة
milebymile-card-right-of-way = حق الأولوية
milebymile-card-false-virtue = الفضيلة الزائفة
milebymile-card-miles = { $miles } ميل

milebymile-no-dirty-trick-window = لا توجد نافذة خدعة قذرة نشطة.
milebymile-not-your-dirty-trick = ليست نافذة الخدعة القذرة لفريقك.
milebymile-between-races = انتظر بدء السباق التالي.

milebymile-error-karma-needs-three-teams = تتطلب قاعدة الكارما 3 سيارات/فرق متمايزة على الأقل.
milebymile-error-perfect-distance-step = يتطلب الوصول الدقيق مسافة سباق قابلة للقسمة على 25، لأن كل بطاقات المسافة من مضاعفات 25.

milebymile-line-format = { $rank }. { $name }: { $points }

milebymile-target-individual = { $name } ({ $miles } ميل)
milebymile-target-team = الفريق { $team }: { $members } ({ $miles } ميل)

milebymile-discard-card = التخلص من بطاقة
milebymile-detailed-status = الحالة التفصيلية
milebymile-check-status = عرض الحالة
milebymile-dirty-trick = لعب خدعة قذرة
milebymile-info-button = معلومات
milebymile-info-msg-individual = { $player }: العوائق: { $hazards }. الوقايات: { $safeties }. المسافة: { $miles } ميل.
milebymile-info-msg-team = { $team } ({ $members }): العوائق: { $hazards }. الوقايات: { $safeties }. المسافة: { $miles } ميل.
