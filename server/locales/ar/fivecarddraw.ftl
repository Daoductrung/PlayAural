game-name-fivecarddraw = لعبة البوكر سحب خمس أوراق
draw-set-starting-chips = رقائق البداية: { $count }
draw-enter-starting-chips = أدخل رقائق البداية
draw-option-changed-starting-chips = تم ضبط شرائح البداية على { $count }.
fivecarddraw-desc-starting-chips = مجموعة سحب البطاقات الخمس الافتتاحية لكل لاعب، من 100 إلى 1,000,000 شريحة. الافتراضي: 20000.
draw-set-ante = أنتي : { $count }
draw-enter-ante = أدخل مبلغ الرهان
draw-option-changed-ante = تم ضبط الرهان على { $count }.
fivecarddraw-desc-ante = المساهمة الإجبارية التي ينشرها كل لاعب نشط قبل كل توزيع ورق. يجب أن يكون أقل من مكدس البداية (الافتراضي 100، النطاق من 0 إلى 1,000,000 شريحة).
draw-set-turn-timer = مؤقت الدوران: { $mode }
draw-select-turn-timer = حدد مؤقت الدوران
draw-option-changed-turn-timer = قم بضبط المؤقت على { $mode }.
fivecarddraw-desc-turn-timer = الحد الزمني الاختياري لكل قرار مراهنة أو سحب: 5، 10، 15، 20، 30، 45، 60، أو 90 ثانية، أو غير محدود. الافتراضي: غير محدود.
draw-set-raise-mode = وضع الرفع: { $mode }
draw-select-raise-mode = حدد وضع الرفع
draw-option-changed-raise-mode = تم ضبط وضع الرفع على { $mode }.
fivecarddraw-desc-raise-mode = رفع نمط الحد: لا يوجد حد، حد الرهان، أو حد الرهان المزدوج. تتطلب الأوضاع القائمة على الرهان رهانًا مسبقًا أكبر من 0 حتى يمكن فتح جولة الرهان الأولى بشكل طبيعي (افتراضي بلا حدود).
draw-set-max-raises = الحد الأقصى للزيادة في كل جولة مراهنة: { $count }
draw-enter-max-raises = أدخل الحد الأقصى للزيادة في كل جولة مراهنة (0 لعدد غير محدود)
draw-option-changed-max-raises = تم ضبط الحد الأقصى للزيادات في كل جولة مراهنة على { $count }.
fivecarddraw-desc-max-raises = الحد الأقصى للزيادات المسموح بها في جولة الرهان الواحدة، من 0 إلى 10. قم بتعيين 0 لعدم وجود سقف للزيادة. الافتراضي: 0.
draw-set-draw-limit = رسم القاعدة: { $mode }
draw-select-draw-limit = حدد قاعدة السحب
draw-option-changed-draw-limit = تم ضبط قاعدة الرسم على { $mode }.
fivecarddraw-desc-draw-limit = قاعدة السحب: استبدل ما يصل إلى 3 بطاقات، أو اسمح بـ 4 بطاقات فقط عند الاحتفاظ بالآص. الافتراضي: ما يصل إلى 3 بطاقات.
draw-limit-three-cards = ما يصل إلى 3 بطاقات (قياسية)
draw-limit-four-with-ace = ما يصل إلى 4 بطاقات عند الاحتفاظ بالآص
draw-error-ante-too-high = يجب أن يكون الرهان المسبق ({ $ante } الرقائق) أقل من مجموع رقائق البداية ({ $chips } الرقائق) حتى يتمكن اللاعبون من اتخاذ قرارات الرهان بعد الصفقة.
draw-error-capped-mode-needs-ante =
    { $mode ->
        [pot_limit] حد الوعاء
        [double_pot] حد الرهان المزدوج
       *[other] وضع الرفع هذا
    } يتطلب رهانًا مسبقًا أكبر من 0، لذا يكون لدى اللاعب الأول مبلغًا قائمًا على مجموع الرهان متاحًا للمراهنة.
draw-antes-posted = يتم نشر النمل. الوعاء يحتوي الآن على { $amount } رقائق.
draw-betting-round-1 = جولة الرهان الأولى.
draw-betting-round-2 = جولة الرهان الثانية.
draw-begin-draw = مرحلة الرسم. بدءًا من أول لاعب نشط على يسار الموزع، اختر بطاقات لتبادلها أو الوقوف عليها.
draw-not-draw-phase = بطاقات السحب متاحة فقط بعد جولة الرهان الأولى. استمر في إجراء الرهان الحالي.
draw-not-betting = الرهان غير متاح خلال مرحلة السحب. حدد أي بطاقات تريد استبدالها، ثم اختر سحب البطاقات.
draw-fold-not-available = الطي غير متاح خلال مرحلة السحب. حدد أي بطاقات تريد استبدالها، ثم اختر سحب البطاقات.
draw-toggle-discard = اختر البطاقة { $index } للتبادل
draw-card-keep = { $card }
draw-card-discard = { $card }تم اختياره للتبادل
draw-draw-cards = سحب البطاقات
draw-draw-cards-count =
    { $count ->
        [0] قف بات
        [one] استبدل بطاقة واحدة
       *[other] صرف { $count } بطاقات
    }
draw-dealt-cards = بطاقاتك الخمس هي { $cards }.
draw-you-drew-cards =
     { $count } الخاص بك  استبدال { $count ->
        [one] البطاقة هي
       *[other] البطاقات هي
    } { $cards }.
draw-you-draw =
    تقوم بالتبادل { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }.
draw-player-draws =
    { $player } التبادلات { $count } { $count ->
        [one] بطاقة
       *[other] بطاقات
    }.
draw-you-stand-pat = أنت تقف وتحتفظ بجميع البطاقات الخمس.
draw-player-stands-pat = { $player } يقف باتًا ويحتفظ بجميع البطاقات الخمس.
draw-you-discard-limit = لا يجوز لك تبادل أكثر من { $count } البطاقات ضمن قاعدة السحب المحددة.
draw-four-requires-kept-ace = يتطلب تبادل 4 بطاقات الاحتفاظ بآس واحد على الأقل. قم بإلغاء تحديد الآس أو تبادل ما لا يزيد عن 3 بطاقات.
draw-raise-invalid = أدخل رقمًا صحيحًا أكبر من 0 للمبلغ المراد رفعه.
draw-raise-cap-reached = الحد { $count } لقد تم بالفعل الوصول إلى الزيادات في جولة الرهان هذه. يمكنك الاتصال أو الطي.
draw-raise-over-stack = لقد حاولت رفع من قبل { $requested } رقائق، ولكن لديك فقط { $chips } الرقائق المتبقية. أدخل زيادة أقل أو اختر الكل في.
draw-raise-too-small = لقد حاولت رفع بواسطة { $requested } رقائق. الحد الأدنى للزيادة هو { $minimum } رقائق.
draw-raise-over-limit =
    لقد حاولت رفع بواسطة { $requested } رقائق. تحت { $mode ->
        [pot_limit] حد الوعاء
        [double_pot] حد الوعاء المزدوج
       *[other] وضع الرفع المحدد
    }، أكبر زيادة متاحة بعد الاتصال هي { $maximum } رقائق.
draw-all-in-over-limit =
    لا يمكنك المشاركة بكل ما تبقى لديك من { $stack } رقائق لأن { $mode ->
        [pot_limit] حد الوعاء
        [double_pot] حد الوعاء المزدوج
       *[other] وضع الرفع المحدد
    } يسمح حاليا برفع الحد الأقصى { $maximum } رقائق بعد الاتصال. استخدم رفع لإدخال المبلغ المسموح به.
draw-all-in-raise-cap-reached = لا يمكنك الدخول في كل شيء كزيادة كاملة لأن الحد الأقصى { $count } لقد تم بالفعل الوصول إلى الزيادات. يمكنك الاتصال أو الطي.
draw-all-in-unavailable-raise-cap = كل ما في الأمر غير متاح لأنه سيكون بمثابة زيادة كاملة بعد الوصول إلى حد الزيادة. يمكنك الاتصال أو الطي.
draw-all-in-unavailable-limit = الكل غير متاح لأن مجموعتك تتجاوز حد الرهان الحالي. استخدم رفع لإدخال المبلغ المسموح به.
draw-raise-unavailable-cap = الزيادة غير متاحة لأن جولة الرهان هذه قد وصلت إلى حد الزيادة.
draw-raise-unavailable-limit = الزيادة الكاملة غير متاحة مع مجموعتك وحد الرهان الحالي. يمكنك الاتصال أو طي أو استخدام الكل عندما يكون ذلك قانونيًا.
draw-current-bet = رهان الجدول الحالي هو { $amount } رقائق.
draw-raise-range = الحد الأدنى للزيادة هو { $minimum } رقائق. يمكنك زيادة ما يصل إلى { $maximum } رقائق بعد الاتصال.
draw-no-full-raise-available = تحتاج { $to_call } رقائق للاتصال والحصول على { $chips } الرقائق المتبقية، لذلك لا يمكنك الحصول على زيادة كاملة. يمكنك استدعاء الكل أو طيه.
draw-dealer-unavailable = لا يوجد منصب تاجر لليد الحالية حتى الآن.
draw-position-unavailable = أنت غير نشط في توزيع الورق الحالي، لذا ليس لديك مركز مراهنة.
draw-card-key = مفتاح البطاقة { $index }
draw-winner-chips =
    { $rank }. { $player }: { $chips } { $chips ->
        [one] شريحة
       *[other] رقائق
    }
