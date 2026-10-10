game-name-battleship = معركة بحرية

# Options
battleship-set-grid-size = منطقة القتال: { $size }
battleship-select-grid-size = اختر حجم منطقة القتال
battleship-option-changed-grid-size = تم ضبط منطقة القتال على { $size }.
battleship-desc-grid-size = يحدد حجم شبكة المحيط في المعركة البحرية؛ الشبكات الأكبر تجعل البحث أطول.

battleship-set-placement-mode = النشر: { $mode }
battleship-select-placement-mode = اختر وضع النشر
battleship-option-changed-placement-mode = تم ضبط وضع النشر على { $mode }.
battleship-desc-placement-mode = يحدد ما إذا كانت السفن توضع تلقائيًا أو يدويًا قبل بدء المعركة.

battleship-set-replay-on-hit = طلقة إضافية عند الإصابة: { $enabled }
battleship-option-changed-replay-on-hit = تم ضبط الطلقة الإضافية عند الإصابة على { $enabled }.
battleship-desc-replay-on-hit = عند التفعيل، يحصل اللاعب الذي يسجّل إصابة على طلقة أخرى فورًا.

battleship-set-turn-timer = مؤقّت الدور: { $seconds }
battleship-select-turn-timer = اختر مؤقّت الدور
battleship-option-changed-turn-timer = تم ضبط مؤقّت الدور على { $seconds }.
battleship-desc-turn-timer = حد زمني اختياري لكل دور في المعركة البحرية؛ إذا نفد الوقت، تطلق اللعبة النار على إحداثي عشوائي. اختر "غير محدود" لإلغاء المؤقّت.

# Option choice labels
battleship-grid-6x6 = 6 في 6
battleship-grid-8x8 = 8 في 8
battleship-grid-10x10 = 10 في 10
battleship-grid-12x12 = 12 في 12

battleship-placement-auto = تلقائي
battleship-placement-manual = يدوي

battleship-timer-off = معطّل
battleship-timer-30 = 30 ثانية
battleship-timer-45 = 45 ثانية
battleship-timer-60 = 60 ثانية

# Setup validation
battleship-error-invalid-grid-size = حجم منطقة القتال { $size } غير مدعوم.
battleship-error-grid-too-small = منطقة القتال { $size } في { $size } صغيرة جدًا على الأسطول الكامل. استخدم { $minimum } في { $minimum } على الأقل.
battleship-error-invalid-placement-mode = وضع النشر { $mode } غير مدعوم.
battleship-error-invalid-turn-timer = مؤقّت الدور { $seconds } غير مدعوم.

# Ship names
battleship-ship-carrier = حاملة طائرات
battleship-ship-battleship = بارجة
battleship-ship-destroyer = مدمّرة
battleship-ship-submarine = غوّاصة
battleship-ship-patrol = زورق دورية
battleship-ship-unknown = سفينة

# Orientations
battleship-horizontal = أفقي
battleship-vertical = عمودي

# Actions
battleship-orient-horizontal = نشر أفقي
battleship-orient-vertical = نشر عمودي
battleship-orient-horizontal-at = انشر { $ship } أفقيًا عند { $coord }
battleship-orient-vertical-at = انشر { $ship } عموديًا عند { $coord }
battleship-select-orientation = اختر اتجاه النشر
battleship-toggle-view = تبديل الشبكة
battleship-read-fleet = حالة الأسطول
battleship-read-enemy-fleet = معلومات أسطول العدو

# Deployment phase
battleship-deploy-start = مرحلة النشر. ضع { $ship } خاصتك، بطول { $size } قطاعات. اختر إحداثيًا، ثم اختر الاتجاه.
battleship-choose-orientation = نشر { $ship } عند { $coord }، { $size } قطاعات. اختر الاتجاه.
battleship-ship-placed = تم نشر { $ship } عند { $coord }، باتجاه { $orientation }.
battleship-cannot-place = لا يمكن نشر { $ship } عند { $coord } { $orientation }. السفينة لا تتسع أو تتداخل مع سفينة أخرى.
battleship-place-next-ship = السفينة التالية: { $ship }، { $size } قطاعات.
battleship-deploy-done = تم نشر الأسطول. بانتظار العدو.
battleship-deploy-complete = اكتمل النشر.
battleship-select-cell-first = اختر إحداثيًا على الشبكة أولًا.
battleship-deploy-in-progress = النشر لا يزال جاريًا.
battleship-deploy-status-header = مرحلة وضع السفن.
battleship-deploy-status-ready-self = أنت جاهز.
battleship-deploy-status-ready-other = { $player } جاهز.
battleship-deploy-status-not-ready-self = لست جاهزًا بعد.
battleship-deploy-status-not-ready-other = { $player } ليس جاهزًا بعد.

# Battle phase
battleship-battle-start = كل السفن في مواقعها. ابدأ إطلاق النار!

# Hit — first-person (shooter), second-person (target), third-person (spectator)
battleship-hit-self = تطلق النار على { $coord }. إصابة مباشرة!
battleship-hit-target = { $player } يطلق النار على { $coord } خاصتك. إصابة مباشرة!
battleship-hit-spectator = { $player } يطلق النار على { $coord } الخاص بـ { $target }. إصابة مباشرة!

# Miss — first/second/third
battleship-miss-self = تطلق النار على { $coord }. إخفاق.
battleship-miss-target = { $player } يطلق النار على { $coord } خاصتك. إخفاق.
battleship-miss-spectator = { $player } يطلق النار على { $coord } الخاص بـ { $target }. إخفاق.

# Sunk — first/second/third
battleship-sunk-self = أغرقت { $ship } العدو!
battleship-sunk-target = { $player } أغرق { $ship } خاصتك!
battleship-sunk-spectator = { $player } أغرق { $ship } الخاص بـ { $target }!

# Victory — first/second/third
battleship-victory-self = لقد فزت! أُغرقت كل سفن العدو.
battleship-victory-target = { $player } يفوز! أُغرقت كل سفنك.
battleship-victory-spectator = { $player } يفوز! أُغرقت كل سفن { $target }.

battleship-shot-in-flight = لا تزال قذيفة في الجو. انتظر النتيجة قبل إطلاق النار مجددًا.
battleship-not-your-turn = ليس دورك لإطلاق النار. انتظر حتى يختار { $player } إحداثيًا.
battleship-wait-for-turn = انتظر أمر الإطلاق التالي قبل اختيار إحداثي.
battleship-already-shot = لقد أطلقت النار على { $coord } من قبل. اختر إحداثيًا لم يُستكشف بعد.
battleship-switch-to-shots = أنت تعرض مياهك، لذا إطلاق النار محظور. اضغط V للتبديل إلى شبكة الهدف.
battleship-timeout-fire = انتهى الوقت! إطلاق تلقائي على { $coord }.

# View toggle
battleship-view-own = عرض مياهك.
battleship-view-shots = عرض شبكة الهدف.

# Cell labels
battleship-cell-empty = { $coord }، مياه مفتوحة.
battleship-cell-ship-placed = { $coord }، { $ship }.
battleship-cell-unknown = { $coord }، غير مستكشف.
battleship-cell-hit = { $coord }، إصابة.
battleship-cell-sunk = { $coord }، { $ship }، أُغرقت.
battleship-cell-miss = { $coord }، إخفاق.
battleship-cell-own-ship = { $coord }، { $ship } خاصتك.
battleship-cell-own-hit = { $coord }، { $ship } خاصتك، مصابة.
battleship-cell-own-sunk = { $coord }، { $ship } خاصتك، أُغرقت.
battleship-cell-own-miss = { $coord }، طلقة واردة أخفقت.

# Fleet status
battleship-fleet-header = أسطولك
battleship-status-intact = جاهزة للقتال
battleship-status-damaged = متضررة ({ $hits } من { $size } إصابة)
battleship-status-sunk = أُغرقت

battleship-enemy-fleet-header = أسطول العدو
battleship-enemy-fleet-summary = أُغرقت { $sunk } من { $total } سفينة للعدو.
battleship-enemy-ship-sunk = { $ship } (الحجم { $size }): أُغرقت

# End screen
battleship-winner-line = { $player } يفوز!
battleship-stats-line = { $player }: { $shots } طلقة، { $hits } إصابة، دقة { $accuracy }%
