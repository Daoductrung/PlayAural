game-name-battleship = سفينة حربية
# Options
battleship-set-grid-size = منطقة القتال: { $size }
battleship-select-grid-size = حدد حجم منطقة القتال
battleship-option-changed-grid-size = تم ضبط منطقة القتال على { $size }.
battleship-desc-grid-size = يختار حجم شبكة المحيط للسفينة الحربية؛ تعمل الشبكات الأكبر حجمًا على إنشاء عمليات بحث أطول.
battleship-set-placement-mode = النشر: { $mode }
battleship-select-placement-mode = حدد وضع النشر
battleship-option-changed-placement-mode = تم ضبط وضع النشر على { $mode }.
battleship-desc-placement-mode = يختار ما إذا كان سيتم وضع السفن تلقائيًا أو يدويًا قبل بدء المعركة.
battleship-set-replay-on-hit = طلقة إضافية عند الضربة: { $enabled }
battleship-option-changed-replay-on-hit = تم ضبط الضربة الإضافية على { $enabled }.
battleship-desc-replay-on-hit = عند التمكين، يقوم اللاعب الذي يسجل ضربة بتسديد ضربة أخرى على الفور.
battleship-set-turn-timer = مؤقت الدوران: { $seconds }
battleship-select-turn-timer = حدد مؤقت الدوران
battleship-option-changed-turn-timer = قم بضبط المؤقت على { $seconds }.
battleship-desc-turn-timer = حد زمني اختياري لكل دور سفينة حربية؛ إذا نفاد الوقت، تنطلق اللعبة بإحداثيات عشوائية. اختر غير محدود بدون توقيت.
# Option choice labels
battleship-grid-6x6 = 6 في 6
battleship-grid-8x8 = 8 في 8
battleship-grid-10x10 = 10 في 10
battleship-grid-12x12 = 12 في 12
battleship-placement-auto = آلي
battleship-placement-manual = دليل
battleship-timer-off = معطلة
battleship-timer-30 = 30 ثانية
battleship-timer-45 = 45 ثانية
battleship-timer-60 = 60 ثانية
# Setup validation
battleship-error-invalid-grid-size = حجم منطقة القتال { $size } غير معتمد.
battleship-error-grid-too-small =  { $size } بواسطة { $size } منطقة القتال صغيرة جدًا بالنسبة للأسطول الكامل. استخدم على الأقل { $minimum } بواسطة { $minimum }.
battleship-error-invalid-placement-mode = وضع النشر { $mode } غير معتمد.
battleship-error-invalid-turn-timer = بدوره الموقت { $seconds } غير معتمد.
# Ship names
battleship-ship-carrier = الناقل
battleship-ship-battleship = سفينة حربية
battleship-ship-destroyer = المدمرة
battleship-ship-submarine = غواصة
battleship-ship-patrol = زورق دورية
battleship-ship-unknown = سفينة
# Orientations
battleship-horizontal = أفقي
battleship-vertical = عمودي
# Actions
battleship-orient-horizontal = نشر أفقي
battleship-orient-vertical = نشر عمودي
battleship-orient-horizontal-at = نشر { $ship } أفقياً عند { $coord }
battleship-orient-vertical-at = نشر { $ship } عموديا في { $coord }
battleship-select-orientation = حدد محمل النشر
battleship-toggle-view = تبديل الشبكة
battleship-read-fleet = حالة الأسطول
battleship-read-enemy-fleet = إنتل أسطول العدو
# Deployment phase
battleship-deploy-start = مرحلة النشر. ضع موقعك { $ship }, { $size } القطاعات طويلة. حدد الإحداثيات، ثم اختر الاتجاه.
battleship-choose-orientation = نشر { $ship } في { $coord }, { $size } القطاعات. حدد تحمل.
battleship-ship-placed = { $ship } منتشرة في { $coord }, تحمل { $orientation }.
battleship-cannot-place = لا يمكن النشر { $ship } في { $coord } { $orientation }. السفينة لا تتناسب مع سفينة أخرى أو تتداخل معها.
battleship-place-next-ship = السفينة التالية: { $ship }, { $size } القطاعات.
battleship-deploy-done = تم نشر الأسطول. الوقوف بجانب العدو.
battleship-deploy-complete = اكتمل النشر.
battleship-select-cell-first = حدد الإحداثيات على الشبكة أولاً.
battleship-deploy-in-progress = النشر لا يزال قيد التقدم.
battleship-deploy-status-header = مرحلة وضع السفينة.
battleship-deploy-status-ready-self = أنت جاهز.
battleship-deploy-status-ready-other = { $player } جاهز.
battleship-deploy-status-not-ready-self = أنت لست مستعدا بعد.
battleship-deploy-status-not-ready-other = { $player } ليست جاهزة بعد.
# Battle phase
battleship-battle-start = جميع السفن في موقفها. البدء بإطلاق النار!
# Hit — first-person (shooter), second-person (target), third-person (spectator)
battleship-hit-self = أنت تطلق النار على { $coord }. ضربة مباشرة!
battleship-hit-target = { $player } حرائق على { $coord }. ضربة مباشرة!
battleship-hit-spectator = { $player } حرائق على { $target } { $coord }. ضربة مباشرة!
# Miss — first/second/third
battleship-miss-self = أنت تطلق النار على { $coord }. مٌفتَقد.
battleship-miss-target = { $player } حرائق على { $coord }. مٌفتَقد.
battleship-miss-spectator = { $player } حرائق على { $target } { $coord }. مٌفتَقد.
# Sunk — first/second/third
battleship-sunk-self = لقد أغرقت العدو { $ship }!
battleship-sunk-target = { $player } غرق { $ship }!
battleship-sunk-spectator = { $player } غرقت { $target } { $ship }!
# Victory — first/second/third
battleship-victory-self = فزت! وقد غرقت جميع سفن العدو.
battleship-victory-target = { $player } يفوز! لقد غرقت جميع السفن الخاصة بك.
battleship-victory-spectator = { $player } يفوز! كل { $target }لقد غرقت سفن.
battleship-shot-in-flight = قذيفة لا تزال في الرحلة. انتظر النتيجة قبل إطلاق النار مرة أخرى.
battleship-not-your-turn = ليس دورك لاطلاق النار. انتظر { $player } لاختيار الإحداثيات.
battleship-wait-for-turn = انتظر أمر الإطلاق التالي قبل اختيار الإحداثيات.
battleship-already-shot = لقد أطلقت النار بالفعل على { $coord }. اختر إحداثيات مجهولة.
battleship-switch-to-shots = أنت تشاهد مياهك الخاصة، لذا فإن إطلاق النار محظور. اضغط على V للتبديل إلى الشبكة المستهدفة.
battleship-timeout-fire = انتهى الوقت! إطلاق النار التلقائي على { $coord }.
# View toggle
battleship-view-own = عرض المياه الخاصة بك.
battleship-view-shots = عرض الشبكة المستهدفة.
# Cell labels
battleship-cell-empty = { $coord }المياه المفتوحة.
battleship-cell-ship-placed = { $coord }, { $ship }.
battleship-cell-unknown = { $coord }، مجهولة.
battleship-cell-hit = { $coord }، يضرب.
battleship-cell-sunk = { $coord }, { $ship }، غرقت.
battleship-cell-miss = { $coord }، يفتقد.
battleship-cell-own-ship = { $coord }، { $ship }.
battleship-cell-own-hit = { $coord }، { $ship }، يضرب.
battleship-cell-own-sunk = { $coord }، { $ship }، غرقت.
battleship-cell-own-miss = { $coord }، ملكة جمال واردة.
# Fleet status
battleship-fleet-header = أسطولك
battleship-status-intact = جاهز للمعركة
battleship-status-damaged = تالف ({ $hits } من { $size } ضرب)
battleship-status-sunk = غرقت
battleship-enemy-fleet-header = أسطول العدو
battleship-enemy-fleet-summary = { $sunk } من { $total } غرقت سفن العدو.
battleship-enemy-ship-sunk = { $ship } (الحجم { $size }): غرقت
# End screen
battleship-winner-line = { $player } يفوز!
battleship-stats-line = { $player }: { $shots } إطلاق نار { $hits } يضرب، { $accuracy }٪ دقة
